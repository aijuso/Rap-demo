#!/usr/bin/env python3
"""Compile a portable role/dependency plan for the lyric workflow."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


ROLE_CONTRACTS = {
    "source_policy_classifier": [
        "classify input as original, user-supplied, generated, or commercial",
        "commercial analysis must not emit reconstructable token sequences",
    ],
    "derived_technique_analyst": [
        "return section functions, non-reconstructive sound events, technique claims, sources, and confidence",
        "never emit ordered lyric tokens or recoverable adjacent spans",
    ],
    "copyright_analysis_auditor": [
        "audit source accuracy, claim status, confidence, and non-reconstructability",
        "reject commercial text, ordered token sequences, and unsupported artist-intent claims",
    ],
    "reference_analyst": [
        "return abstract techniques with evidence; never imitate a named artist",
        "do not reproduce commercial lyrics",
    ],
    "reference_sanitizer": [
        "remove artist names, signature phrases, biography, ad-libs, and recognizable scene order",
        "rewrap only anonymous technique operations against the generation brief hash",
    ],
    "narrative_architect": [
        "return proposition, pressure, turn, residue, bar functions, and setup/payoff ids",
    ],
    "vocabulary_director": [
        "return concrete objects/actions before abstractions",
        "annotate meaning, register, semantic domain, and likely syntax affordances",
    ],
    "humor_engineer": [
        "return mechanism, setup, violated expectation, target, payoff, and timing",
        "reject punch-down and reference-only jokes",
    ],
    "rhyme_graph_engineer": [
        "return readings, morae, rhyme relations, placements, confidence, and penalties",
        "do not equate sound similarity with lyric quality",
    ],
    "flow_mapper": [
        "return density, subdivision, accents, rests, held vowels, breath, voice, and switches",
        "mark pocket unverified without audio",
    ],
    "rhyme_flow_reconciler": [
        "resolve first-pass rhyme and flow conflicts without changing the brief",
        "return accepted placements, rejected candidates, and draft-time remap requirements",
    ],
    "specialist_reconciler": [
        "resolve cross-artifact ids, readings, bar ranges, setup/payoff links, and rejected options",
        "do not write finished lyrics",
    ],
    "token_semantic_analyst": [
        "annotate each permitted token with meaning, grammar, sound, role, evidence, and confidence",
        "for commercial work return paraphrased functions and non-reconstructive events only",
    ],
    "narrative_humor_analyst": [
        "map bar functions, information changes, setup/payoff, humor mechanisms, and uncertainty",
    ],
    "analysis_integrator": [
        "merge semantic, rhyme, narrative, humor, and flow findings without upgrading uncertainty",
    ],
    "draft_integrator": [
        "use accepted artifacts; preserve meaning before maximizing rhyme density",
        "return clean draft plus traceability to artifact ids",
    ],
    "professional_auditor": [
        "audit independently and cite bar-level evidence",
        "apply hard gates and label audio-dependent claims unknown",
    ],
    "repair_owner": [
        "repair only prioritized failures; record changed and intentionally unchanged bars",
    ],
    "production_director": [
        "derive production choices from lyric function; mark generation behavior provisional",
    ],
}


def task(task_id: str, role: str, depends: list[str], artifact: str) -> dict:
    reference_role = role == "reference_analyst"
    return {
        "id": task_id,
        "role": role,
        "depends_on": depends,
        "artifact": artifact,
        "input_brief": "reference_brief" if reference_role else "generation_brief",
        "allowed_references": ["named_sources"] if reference_role else [],
        "write_scope": [artifact],
        "status": "pending",
        "contract": ROLE_CONTRACTS[role],
    }


def compile_plan(brief: dict) -> dict:
    mode = brief.get("mode", "create")
    request_seed = json.dumps(brief, ensure_ascii=False, sort_keys=True).encode("utf-8")
    request_id = hashlib.sha256(request_seed).hexdigest()[:12]
    tasks: list[dict] = []
    reference_brief = copy.deepcopy(brief)
    generation_brief = copy.deepcopy(brief)
    generation_brief.pop("reference_requests", None)
    if brief.get("reference_requests"):
        tasks.append(task("reference", "reference_analyst", [], "technique_profile.json"))
        tasks.append(
            task(
                "reference_sanitize",
                "reference_sanitizer",
                ["reference"],
                "anonymous_technique_vector.json",
            )
        )
    common_dependencies = ["reference_sanitize"] if tasks else []
    if mode in {"create", "rewrite", "teach"}:
        tasks.extend(
            [
                task("narrative", "narrative_architect", common_dependencies, "narrative_map.json"),
                task("vocabulary", "vocabulary_director", common_dependencies, "vocabulary_bank.json"),
                task("humor", "humor_engineer", common_dependencies, "humor_plan.json"),
                task("rhyme", "rhyme_graph_engineer", common_dependencies, "rhyme_graph.json"),
                task("flow", "flow_mapper", common_dependencies, "flow_map.json"),
            ]
        )
        tasks.append(
            task(
                "vocabulary_rhyme_reconcile",
                "specialist_reconciler",
                ["vocabulary", "rhyme"],
                "vocabulary_rhyme_reconciliation.json",
            )
        )
        tasks.append(
            task(
                "narrative_humor_reconcile",
                "specialist_reconciler",
                ["narrative", "vocabulary", "humor"],
                "narrative_humor_reconciliation.json",
            )
        )
        tasks.append(
            task(
                "rhyme_flow_reconcile",
                "rhyme_flow_reconciler",
                ["narrative", "vocabulary", "rhyme", "flow"],
                "rhyme_flow_reconciliation.json",
            )
        )
        tasks.append(
            task(
                "draft",
                "draft_integrator",
                [
                    "narrative", "vocabulary", "humor",
                    "rhyme", "flow", "vocabulary_rhyme_reconcile",
                    "narrative_humor_reconcile", "rhyme_flow_reconcile",
                ],
                "draft.json",
            )
        )
        tasks.append(
            task("flow_remap", "flow_mapper", ["draft"], "final_flow_map.json")
        )
        tasks.append(
            task("audit", "professional_auditor", ["draft", "flow_remap"], "audit.json")
        )
        tasks.append(
            task(
                "repair",
                "repair_owner",
                [
                    "audit", "draft", "narrative", "vocabulary", "humor",
                    "rhyme", "flow_remap",
                ],
                "revised_draft.json",
            )
        )
        tasks.append(
            task(
                "post_repair_flow_remap",
                "flow_mapper",
                ["repair"],
                "repaired_flow_map.json",
            )
        )
        tasks.append(
            task(
                "reaudit",
                "professional_auditor",
                ["repair", "post_repair_flow_remap"],
                "reaudit.json",
            )
        )
        if brief.get("generation_target") not in {None, "none"}:
            tasks.append(
                task(
                    "production",
                    "production_director",
                    ["reaudit", "repair", "post_repair_flow_remap"],
                    "production_handoff.json",
                )
            )
    elif mode == "rhyme-bank":
        tasks.append(task("vocabulary", "vocabulary_director", common_dependencies, "vocabulary_bank.json"))
        tasks.append(task("rhyme", "rhyme_graph_engineer", ["vocabulary"], "rhyme_graph.json"))
    elif mode == "flow-map":
        tasks.append(task("flow", "flow_mapper", common_dependencies, "flow_map.json"))
    elif mode == "analyze":
        source_dependencies = list(common_dependencies)
        tasks.append(
            task("source_policy", "source_policy_classifier", [], "source_policy.json")
        )
        if brief.get("copyright_input_class") == "commercial_work":
            tasks.extend(
                [
                    task(
                        "derived_techniques",
                        "derived_technique_analyst",
                        ["source_policy"] + source_dependencies,
                        "commercial_derived_analysis.json",
                    ),
                    task(
                        "flow_observation",
                        "flow_mapper",
                        ["source_policy"],
                        "flow_observation.json",
                    ),
                    task(
                        "commercial_analysis_integration",
                        "analysis_integrator",
                        ["derived_techniques", "flow_observation"],
                        "commercial_analysis_report.json",
                    ),
                    task(
                        "copyright_analysis_audit",
                        "copyright_analysis_auditor",
                        ["commercial_analysis_integration"],
                        "copyright_analysis_audit.json",
                    ),
                ]
            )
        else:
            tasks.extend(
                [
                task(
                    "token_semantics",
                    "token_semantic_analyst",
                    ["source_policy"],
                    "word_analysis.json",
                ),
                task(
                    "rhyme_analysis",
                    "rhyme_graph_engineer",
                    ["source_policy", "token_semantics"],
                    "rhyme_graph.json",
                ),
                task(
                    "narrative_humor_analysis",
                    "narrative_humor_analyst",
                    ["source_policy"],
                    "narrative_humor_analysis.json",
                ),
                task(
                    "flow_analysis",
                    "flow_mapper",
                    ["source_policy"],
                    "flow_map.json",
                ),
                task(
                    "analysis_integration",
                    "analysis_integrator",
                    [
                        "token_semantics",
                        "rhyme_analysis",
                        "narrative_humor_analysis",
                        "flow_analysis",
                    ] + source_dependencies,
                    "analysis_report.json",
                ),
                task(
                    "analysis_audit",
                    "professional_auditor",
                    ["analysis_integration"],
                    "analysis_audit.json",
                ),
                ]
            )
    elif mode == "audit":
        tasks.append(task("audit", "professional_auditor", common_dependencies, "audit.json"))
    elif mode == "production":
        tasks.append(
            task(
                "final_input_validation",
                "professional_auditor",
                common_dependencies,
                "final_input_validation.json",
            )
        )
        tasks.append(
            task(
                "flow_remap",
                "flow_mapper",
                ["final_input_validation"],
                "final_flow_map.json",
            )
        )
        tasks.append(
            task(
                "audit",
                "professional_auditor",
                ["final_input_validation", "flow_remap"],
                "audit.json",
            )
        )
        tasks.append(
            task(
                "repair",
                "repair_owner",
                ["audit", "final_input_validation", "flow_remap"],
                "revised_draft.json",
            )
        )
        tasks.append(
            task(
                "post_repair_flow_remap",
                "flow_mapper",
                ["repair"],
                "repaired_flow_map.json",
            )
        )
        tasks.append(
            task(
                "reaudit",
                "professional_auditor",
                ["repair", "post_repair_flow_remap"],
                "reaudit.json",
            )
        )
        tasks.append(
            task(
                "production",
                "production_director",
                ["reaudit", "repair", "post_repair_flow_remap"],
                "production_handoff.json",
            )
        )
    else:
        raise ValueError(f"unsupported mode: {mode}")
    task_ids = {item["id"] for item in tasks}
    gates = []
    if {"narrative", "vocabulary", "humor", "rhyme", "flow"} <= task_ids:
        gates.append(
            {
                "id": "integration_ready",
                "after": [
                    "narrative", "vocabulary", "humor", "rhyme", "flow",
                    "vocabulary_rhyme_reconcile",
                    "narrative_humor_reconcile",
                    "rhyme_flow_reconcile",
                ],
                "requirements": [
                    "all required artifacts present",
                    "all readings carry source and confidence",
                    "no named-artist imitation instructions",
                ],
            }
        )
    final_review = (
        "reaudit"
        if "reaudit" in task_ids
        else "copyright_analysis_audit"
        if "copyright_analysis_audit" in task_ids
        else "analysis_audit"
        if "analysis_audit" in task_ids
        else "audit"
        if "audit" in task_ids
        else None
    )
    if final_review:
        evidence_requirement = (
            "non-reconstructive section/event evidence with sources attached"
            if (
                mode == "analyze"
                and brief.get("copyright_input_class") == "commercial_work"
            )
            else "bar-level evidence attached"
        )
        gates.append(
            {
                "id": "release_ready",
                "after": [final_review],
                "requirements": [
                    "no hard-gate failures",
                    evidence_requirement,
                    "audio-dependent claims marked unknown unless audio was reviewed",
                ],
            }
        )
    return {
        "request_id": request_id,
        "brief": generation_brief,
        "generation_brief": generation_brief,
        "reference_brief": reference_brief if brief.get("reference_requests") else None,
        "tasks": tasks,
        "gates": gates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("brief", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.brief.read_text(encoding="utf-8"))
    print(json.dumps(compile_plan(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
