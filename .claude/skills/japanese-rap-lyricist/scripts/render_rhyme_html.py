#!/usr/bin/env python3
"""Render a rhyme-bank/v1 JSON into a self-contained per-keyword rhyme-table HTML.

Usage: python3 scripts/render_rhyme_html.py run/rhyme_bank.json \
           [-o run/rhyme_bank.html]
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from html import escape
from pathlib import Path

from html_common import page, select_bar, th
from validate_bank import DEFAULT_TYPE_MINIMUMS, TYPE_BUCKETS

BUCKET_LABELS = {
    "assonance": "母音韻",
    "consonance": "子音韻・頭韻",
    "multimora": "4モーラ以上",
    "phrase_or_mosaic": "フレーズ・モザイク",
    "placement_proposal": "内部・頭・跨ぎ配置",
}


def bucket_counts(candidates: list[dict]) -> dict[str, int]:
    counts = {bucket: 0 for bucket in TYPE_BUCKETS}
    for candidate in candidates:
        types = set(candidate.get("rhyme_types", []))
        for bucket, members in TYPE_BUCKETS.items():
            if members & types:
                counts[bucket] += 1
    return counts


def keyword_section(keyword: dict, candidates: list[dict], minimums: dict[str, int]) -> str:
    kid = escape(str(keyword.get("id", "")))
    counts = bucket_counts(candidates)
    badges = []
    for bucket, minimum in minimums.items():
        have = counts.get(bucket, 0)
        cls = "badge-ok" if have >= minimum else "badge-ng"
        badges.append(
            f"<span class='{cls}'>{escape(BUCKET_LABELS.get(bucket, bucket))} {have}/{minimum}</span>"
        )
    rows = []
    for index, candidate in enumerate(candidates):
        cid = f"{kid}-{index + 1:02d}"
        types = "".join(
            f"<span class='pill'>{escape(t)}</span>" for t in candidate.get("rhyme_types", [])
        )
        warn = "; ".join(candidate.get("warnings", []))
        rows.append(
            "<tr>"
            f"<td><input class='rowsel' type='checkbox' value='{cid}'></td>"
            f"<td>{cid}</td>"
            f"<td>{escape(str(candidate.get('surface', '')))}</td>"
            f"<td>{escape(str(candidate.get('reading', '')))}</td>"
            f"<td class='skel'>{escape(str(candidate.get('vowel_skeleton', '')))}</td>"
            f"<td class='skel'>{escape(str(candidate.get('consonant_skeleton', '')))}</td>"
            f"<td>{types}</td>"
            f"<td class='num' data-v='{candidate.get('domain_length', 0)}'>{candidate.get('domain_length', 0)}</td>"
            f"<td class='num' data-v='{candidate.get('score_vowel', 0)}'>{candidate.get('score_vowel', 0):.2f}</td>"
            f"<td class='num' data-v='{candidate.get('score_consonant', 0)}'>{candidate.get('score_consonant', 0):.2f}</td>"
            f"<td class='num' data-v='{candidate.get('score_balanced', 0)}'>{candidate.get('score_balanced', 0):.2f}</td>"
            f"<td>{escape(str(candidate.get('example_phrase', '')))}</td>"
            f"<td>{escape(warn) if warn else '—'}</td>"
            "</tr>"
        )
    return f"""
<h2 id='{kid}'>{kid} {escape(str(keyword.get('surface', '')))}
 <small class='skel'>（{escape(str(keyword.get('reading', '')))} ｜ 母音 {escape(str(keyword.get('vowel_skeleton', '')))} ｜ 子音 {escape(str(keyword.get('consonant_skeleton', '')))}）</small></h2>
<div class='meta'>{' '.join(badges)} ｜ 候補 {len(candidates)}件</div>
<div class='tablewrap'>
<table>
<thead><tr>
  <th>✓</th>{th('ID')}{th('候補')}{th('読み')}{th('母音骨格')}{th('子音骨格')}
  {th('韻タイプ')}{th('一致長', True)}{th('vowel', True)}{th('consonant', True)}
  {th('総合', True)}{th('用例')}{th('備考')}
</tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>
"""


def render(payload: dict) -> str:
    keywords = payload.get("keywords", [])
    grouped: dict[str, list[dict]] = defaultdict(list)
    for candidate in payload.get("candidates", []):
        grouped[str(candidate.get("keyword_id", ""))].append(candidate)
    minimums = {**DEFAULT_TYPE_MINIMUMS, **payload.get("type_minimums", {})}
    toc = " ｜ ".join(
        f"<a href='#{escape(str(k.get('id', '')))}'>{escape(str(k.get('surface', '')))}"
        f"({len(grouped.get(str(k.get('id', '')), []))})</a>"
        for k in keywords
    )
    sections = "".join(
        keyword_section(k, grouped.get(str(k.get("id", "")), []), minimums) for k in keywords
    )
    total = sum(len(v) for v in grouped.values())
    body = f"""
<h1>韻バンク</h1>
<div class='meta'>キーワード {len(keywords)}語 ｜ 候補 合計{total}件 ｜
 気に入った候補にチェックして「選択IDをコピー」→ 返信に貼り付けてください。<br>{toc}</div>
<div class='controls'>
  <input type='search' placeholder='全体を絞り込み…' oninput='applyFilters()'>
</div>
{sections}
{select_bar()}
"""
    return page("韻バンク", body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    output = args.output or args.input.with_name("rhyme_bank.html")
    output.write_text(render(payload), encoding="utf-8")
    print(json.dumps({
        "written": str(output),
        "keywords": len(payload.get("keywords", [])),
        "candidates": len(payload.get("candidates", [])),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
