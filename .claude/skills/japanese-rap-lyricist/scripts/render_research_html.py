#!/usr/bin/env python3
"""Render a research-bank/v1 JSON into a self-contained keyword-table HTML.

Usage: python3 scripts/render_research_html.py run/research_bank.json \
           [-o run/research_keywords.html]
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from html_common import page, select_bar, th

KIND_LABELS = {"vocabulary": "語彙", "episode": "エピソード", "association": "連想"}
DOMAIN_LABELS = {
    "object": "物", "action": "動作", "place": "場所",
    "time_or_number": "時刻・数字", "sound": "音", "body": "身体",
    "institution_or_money": "制度・金銭", "relationship": "関係", "other": "その他",
}


def option_html(values: dict[str, str]) -> str:
    return "".join(f"<option value='{escape(k)}'>{escape(v)}</option>" for k, v in values.items())


def render(payload: dict) -> str:
    theme = payload.get("theme", "")
    concept = payload.get("concept") or ""
    keywords = payload.get("keywords", [])
    rows = []
    for keyword in keywords:
        kid = escape(str(keyword.get("id", "")))
        kind = str(keyword.get("kind", ""))
        domain = str(keyword.get("domain", ""))
        sources = [
            e for e in keyword.get("evidence", []) if str(e.get("pointer", "")).startswith("http")
        ]
        src_html = " ".join(
            f"<a href='{escape(e['pointer'])}' target='_blank' rel='noopener'>"
            f"{escape(e['pointer'].split('/')[2] if len(e['pointer'].split('/')) > 2 else e['pointer'])}</a>"
            for e in sources
        ) or "—"
        rows.append(
            f"<tr data-kind='{escape(kind)}' data-domain='{escape(domain)}'>"
            f"<td><input class='rowsel' type='checkbox' value='{kid}'></td>"
            f"<td>{kid}</td>"
            f"<td>{escape(str(keyword.get('surface', '')))}</td>"
            f"<td>{escape(str(keyword.get('reading', '')))}</td>"
            f"<td class='num' data-v='{keyword.get('mora_count', 0)}'>{keyword.get('mora_count', 0)}</td>"
            f"<td class='skel'>{escape(str(keyword.get('vowel_skeleton', '')))}</td>"
            f"<td class='skel'>{escape(str(keyword.get('consonant_skeleton', '')))}</td>"
            f"<td>{escape(KIND_LABELS.get(kind, kind))}</td>"
            f"<td>{escape(DOMAIN_LABELS.get(domain, domain))}</td>"
            f"<td>{escape(str(keyword.get('plain_meaning', '')))}"
            f"{('<br><small>' + escape(str(keyword.get('usage_note'))) + '</small>') if keyword.get('usage_note') else ''}</td>"
            f"<td class='src'>{src_html}</td>"
            f"<td>{escape(str(keyword.get('confidence', '')))}</td>"
            "</tr>"
        )
    body = f"""
<h1>リサーチ・キーワード表</h1>
<div class='meta'>テーマ: {escape(theme)}{(' ｜ コンセプト: ' + escape(concept)) if concept else ''}
 ｜ キーワード {len(keywords)}件 ｜ 使いたい語にチェックして「選択IDをコピー」→ 返信に貼り付けてください。</div>
<div class='controls'>
  <input type='search' placeholder='絞り込み…' oninput='applyFilters()'>
  <select data-col='kind' onchange='applyFilters()'>
    <option value=''>種別: すべて</option>{option_html(KIND_LABELS)}
  </select>
  <select data-col='domain' onchange='applyFilters()'>
    <option value=''>探索窓: すべて</option>{option_html(DOMAIN_LABELS)}
  </select>
</div>
<div class='tablewrap'>
<table>
<thead><tr>
  <th>✓</th>{th('ID')}{th('表記')}{th('読み')}{th('モーラ', True)}
  {th('母音骨格')}{th('子音骨格')}{th('種別')}{th('探索窓')}
  {th('意味・使いどころ')}{th('出典')}{th('信頼度')}
</tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>
{select_bar()}
"""
    return page(f"リサーチ・キーワード表 — {theme}", body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=None)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    output = args.output or args.input.with_name("research_keywords.html")
    output.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"written": str(output), "keywords": len(payload.get('keywords', []))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
