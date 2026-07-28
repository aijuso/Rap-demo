#!/usr/bin/env python3
"""Build an explainable graph of candidate Japanese rhyme relationships.

Input is a JSON object with a ``nodes`` array. Readings must be supplied; this
tool never invents kanji or name readings. Sound edges are evidence for review,
not a lyric-quality score.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from kana_to_mora import parse_morae
from rhyme_score import score_pair


def enrich_node(raw: dict, index: int) -> dict:
    if not raw.get("surface") or not raw.get("reading"):
        raise ValueError(f"node {index} requires surface and reading")
    moras, warnings = parse_morae(raw["reading"])
    if warnings:
        raise ValueError(f"node {index} has unresolved reading: {'; '.join(warnings)}")
    return {
        "id": str(raw.get("id", f"n{index}")),
        "surface": raw["surface"],
        "reading": raw["reading"],
        "vowel_sequence": [m.signature for m in moras],
        "consonant_sequence": [m.onset or None for m in moras],
        "mora_count": len(moras),
        "accent": raw.get("accent"),
        "part_of_speech": raw.get("part_of_speech"),
        "register": raw.get("register"),
        "semantic_domains": raw.get("semantic_domains", []),
        "frequency": raw.get("frequency"),
        "freshness": raw.get("freshness"),
        "cliche_risk": raw.get("cliche_risk"),
        "articulation_cost": raw.get("articulation_cost"),
        "proper_noun": bool(raw.get("proper_noun", False)),
        "particle_affordances": raw.get("particle_affordances", []),
        "particles_before": raw.get("particles_before", []),
        "particles_after": raw.get("particles_after", []),
        "bar": raw.get("bar"),
        "position": raw.get("position", "unplaced"),
        "source": raw.get("source", "manual"),
        "reading_confidence": float(raw.get("reading_confidence", 1.0)),
    }


def relation_types(pair: dict, left: dict, right: dict) -> list[str]:
    domain = pair["best_domain"]
    types: list[str] = []
    if domain["vowel_or_coda"] >= 0.98:
        types.append("assonance")
    elif domain["vowel_or_coda"] >= 0.72:
        types.append("near_assonance")
    if domain["onset"] >= 0.72:
        types.append("consonance")
    if domain["special_mora"] >= 0.95:
        types.append("special_mora_match")
    if (
        domain["vowel_or_coda"] >= 0.98
        and domain["onset"] >= 0.90
        and domain["special_mora"] >= 0.95
    ):
        types.append("exact_or_near_exact_sound")
    else:
        types.append("slant_or_half_rhyme")
    if domain["domain_length"] >= 4:
        types.append("multi_mora")
    if " " in left["surface"] or " " in right["surface"]:
        types.append("phrase_or_mosaic_candidate")
    positions = {left["position"], right["position"]}
    if positions == {"end"}:
        types.append("end_rhyme")
    if "internal" in positions or "caesura" in positions:
        types.append("internal_rhyme")
    if left.get("bar") and right.get("bar") and abs(left["bar"] - right["bar"]) > 1:
        types.append("delayed_or_callback_candidate")
    return sorted(set(types))


def build_graph(raw_nodes: list[dict], threshold: float = 0.48) -> dict:
    nodes = [enrich_node(item, index) for index, item in enumerate(raw_nodes, 1)]
    if len({item["id"] for item in nodes}) != len(nodes):
        raise ValueError("node ids must be unique")
    edges: list[dict] = []
    for left, right in combinations(nodes, 2):
        pair = score_pair(
            left["surface"], right["surface"], left["reading"], right["reading"]
        )
        score = pair["sound_score_after_penalty"]
        if score < threshold:
            continue
        shared_domains = set(left["semantic_domains"]) & set(right["semantic_domains"])
        edges.append(
            {
                "source": left["id"],
                "target": right["id"],
                "sound_score": score,
                "label": pair["label"],
                "rhyme_types": relation_types(pair, left, right),
                "domain_morae": pair["best_domain"]["domain_length"],
                "semantic_fit": None,
                "transition_cost": None,
                "shared_semantic_domains": sorted(shared_domains),
                "alignment": pair["best_domain"]["alignment"],
                "warnings": pair["warnings"],
            }
        )
    parent = {node["id"]: node["id"] for node in nodes}

    def find(node_id: str) -> str:
        while parent[node_id] != node_id:
            parent[node_id] = parent[parent[node_id]]
            node_id = parent[node_id]
        return node_id

    def union(left_id: str, right_id: str) -> None:
        left_root, right_root = find(left_id), find(right_id)
        if left_root != right_root:
            parent[right_root] = left_root

    for edge in edges:
        union(edge["source"], edge["target"])
    components: dict[str, list[str]] = {}
    for node in nodes:
        components.setdefault(find(node["id"]), []).append(node["id"])
    node_by_id = {node["id"]: node for node in nodes}
    families = []
    for index, members in enumerate(
        sorted(components.values(), key=lambda item: (-len(item), item)), 1
    ):
        if len(members) < 2:
            continue
        prototype = max(members, key=lambda item: node_by_id[item]["mora_count"])
        families.append(
            {
                "id": f"fam-{index}",
                "member_node_ids": sorted(members),
                "prototype_vowels": node_by_id[prototype]["vowel_sequence"],
            }
        )
    spans = [
        {
            "id": f"span-{node['id']}",
            "node_id": node["id"],
            "performed_reading": node["reading"],
            "mora_count": node["mora_count"],
            "token_boundary_signature": [node["mora_count"]],
        }
        for node in nodes
    ]
    occurrences = [
        {
            "id": f"occ-{node['id']}",
            "span_id": f"span-{node['id']}",
            "bar": node["bar"],
            "position": node["position"],
            "audio_verified": False,
        }
        for node in nodes
    ]
    return {
        "nodes": nodes,
        "spans": spans,
        "occurrences": occurrences,
        "families": families,
        "edges": sorted(edges, key=lambda item: item["sound_score"], reverse=True),
        "limitations": [
            "Accent, frequency, freshness, meaning, syntax, and beat salience are not inferred.",
            "Semantic fit and transition cost require a specific line context.",
            "A dense graph is a search aid, not evidence of a strong lyric.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--threshold", type=float, default=0.48)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    nodes = payload["nodes"] if isinstance(payload, dict) else payload
    print(json.dumps(build_graph(nodes, args.threshold), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
