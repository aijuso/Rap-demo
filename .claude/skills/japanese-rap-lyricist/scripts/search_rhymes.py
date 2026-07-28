#!/usr/bin/env python3
"""Search a user-built lexicon and return explainable rhyme candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rhyme_score import score_pair


def load_jsonl(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def search(
    lexicon: Path,
    surface: str,
    reading: str,
    *,
    tags: set[str],
    pos: str | None,
    top_k: int,
) -> list[dict]:
    results = []
    for item in load_jsonl(lexicon):
        if pos and item.get("pos") != pos:
            continue
        item_tags = set(item.get("tags", []))
        tag_overlap = len(tags & item_tags)
        pair = score_pair(surface, item["surface"], reading, item["reading"])
        results.append(
            {
                "surface": item["surface"],
                "reading": item["reading"],
                "pos": item.get("pos", ""),
                "tags": item.get("tags", []),
                "sound_score": pair["sound_score_after_penalty"],
                "domain_length": pair["best_domain"]["domain_length"],
                "matched_spans": [
                    pair["best_domain"]["span_a"],
                    pair["best_domain"]["span_b"],
                ],
                "tag_overlap": tag_overlap,
                "rank_score": round(pair["sound_score_after_penalty"] + 0.04 * tag_overlap, 3),
                "warning": "Semantic relevance and naturalness require contextual review.",
            }
        )
    results.sort(key=lambda x: (x["rank_score"], x["domain_length"]), reverse=True)
    return results[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lexicon", type=Path)
    parser.add_argument("surface")
    parser.add_argument("--reading", required=True)
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--pos")
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()
    payload = {
        "query": {"surface": args.surface, "reading": args.reading},
        "candidates": search(
            args.lexicon,
            args.surface,
            args.reading,
            tags=set(args.tag),
            pos=args.pos,
            top_k=args.top_k,
        ),
        "limitations": [
            "This is a reranker over a user-supplied lexicon, not a lyric generator.",
            "Do not select a candidate on sound score alone.",
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
