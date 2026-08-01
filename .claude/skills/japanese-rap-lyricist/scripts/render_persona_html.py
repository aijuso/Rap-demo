#!/usr/bin/env python3
"""Render verse persona/story artifacts into one self-contained review page.

Unlike ``render_research_html.py``, which lists the whole keyword bank as a flat
sortable table, this renderer puts the persona and the story first and hangs the
selected words under the beat that uses them. That is the shape a writer needs
at CP2: the question is not "which of 233 words are nice" but "does this person,
this story, and these words belong together".

Usage:
    python3 render_persona_html.py run/persona_A1.json run/persona_A2.json ... \
        [-o run/verse_personas.html]
"""

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from html_common import BASE_CSS, BASE_JS, select_bar  # noqa: E402

EXTRA_CSS = """
.verse { border: 1px solid #ddd; border-radius: 10px; padding: 1rem 1.1rem; margin: 1.4rem 0; background: #fff; }
@media (prefers-color-scheme: dark) { .verse { background: #1c1f26; border-color: #333; } .card { background: #23262e !important; } .beat { background: #1f232b !important; } .beat.low { background: #1a1d24 !important; } }
.verse > h2 { margin-top: 0; display: flex; flex-wrap: wrap; gap: .5rem; align-items: baseline; }
.gadget { font-size: .82rem; font-weight: normal; color: #777; }
.card { background: #f7f8fa; border-radius: 8px; padding: .7rem .9rem; margin: .6rem 0; }
.card h3 { font-size: .9rem; margin: 0 0 .4rem; letter-spacing: .04em; color: #666; }
.kv { display: grid; grid-template-columns: 8.5rem 1fr; gap: .25rem .8rem; }
.kv dt { color: #777; font-size: .84rem; }
.kv dd { margin: 0; }
.arc { display: grid; grid-template-columns: repeat(4, 1fr); gap: .5rem; margin: .5rem 0 0; }
.arc div { background: #eef1f6; border-radius: 6px; padding: .4rem .55rem; font-size: .84rem; }
@media (prefers-color-scheme: dark) { .arc div { background: #262a33; } }
@media (max-width: 720px) { .arc { grid-template-columns: 1fr 1fr; } .kv { grid-template-columns: 1fr; } }
.beat { border-left: 3px solid #9aa4b8; background: #f4f6fa; border-radius: 0 8px 8px 0; padding: .6rem .9rem; margin: .55rem 0; }
.beat.low { border-left-color: #cfd5e0; background: #fafbfd; }
.beat h4 { margin: 0 0 .3rem; font-size: .92rem; }
.beat .bars { font-family: ui-monospace, Menlo, monospace; font-size: .8rem; color: #777; margin-right: .5rem; }
.pred { color: #777; font-size: .84rem; margin: .25rem 0 .45rem; }
.words { display: flex; flex-wrap: wrap; gap: .4rem; }
.w { display: flex; align-items: baseline; gap: .35rem; background: #fff; border: 1px solid #dde1e8; border-radius: 999px; padding: .18rem .6rem; font-size: .86rem; }
@media (prefers-color-scheme: dark) { .w { background: #2a2e38; border-color: #3a3f4a; } }
.w .rd { color: #888; font-size: .76rem; }
.w .role { font-size: .7rem; padding: 0 .35rem; border-radius: 999px; background: #e5e9f0; color: #4a5162; }
@media (prefers-color-scheme: dark) { .w .role { background: #383d49; color: #b9c0cd; } }
.role-オチ, .role-両義語 { background: #ffe9c7 !important; color: #7a4a00 !important; }
.role-回収 { background: #d9f2df !important; color: #14602a !important; }
.why { font-size: .8rem; color: #666; margin: .35rem 0 0; }
details.why-list { margin: .4rem 0 0; }
details.why-list summary { cursor: pointer; font-size: .84rem; color: #666; }
details.why-list li { font-size: .82rem; margin: .2rem 0; }
.rejected li { font-size: .82rem; color: #777; }
"""


def _kv(pairs) -> str:
    rows = "".join(
        f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in pairs if v
    )
    return f"<dl class='kv'>{rows}</dl>"


def _word_chip(w: dict) -> str:
    role = w.get("role", "")
    wid = escape(str(w.get("id", "")))
    return (
        f"<label class='w' title='{escape(w.get('why', ''))}'>"
        f"<input type='checkbox' class='rowsel' value='{wid}' checked>"
        f"<span>{escape(w.get('surface', ''))}</span>"
        f"<span class='rd'>{escape(w.get('reading', ''))}</span>"
        f"<span class='role role-{escape(role)}'>{escape(role)}</span>"
        "</label>"
    )


def render_verse(p: dict) -> str:
    per = p.get("persona", {})
    st = p.get("story", {})
    words = p.get("words", [])
    by_beat: dict[str, list] = {}
    for w in words:
        by_beat.setdefault(w.get("beat", "?"), []).append(w)

    out = [
        f"<section class='verse'><h2>{escape(p.get('verse_id', ''))}"
        f" — {escape(per.get('label', ''))}"
        f"<span class='gadget'>× {escape(p.get('gadget', ''))}</span></h2>"
    ]

    out.append("<div class='card'><h3>ペルソナ</h3>")
    out.append(
        _kv(
            [
                ("年齢・仕事", per.get("age_and_job", "")),
                ("人前での顔", per.get("public_face", "")),
                ("本当の望み", per.get("private_want", "")),
                ("本人の盲点", per.get("blind_spot", "")),
                ("声", per.get("voice", "")),
                ("一日", per.get("day_in_life", "")),
            ]
        )
    )
    sig = per.get("signals", [])
    if sig:
        chips = "".join(f"<span class='pill'>{escape(s)}</span>" for s in sig)
        out.append(f"<div style='margin-top:.5rem'>名前を出さずに伝わる記号: {chips}</div>")
    out.append("</div>")

    out.append("<div class='card'><h3>物語</h3><div class='arc'>")
    for label, key in (
        ("主張", "proposition"),
        ("圧力", "pressure"),
        ("転回", "turn"),
        ("residue", "residue"),
    ):
        out.append(f"<div><b>{escape(label)}</b><br>{escape(st.get(key, ''))}</div>")
    out.append("</div></div>")

    gl = p.get("gadget_link")
    if gl:
        out.append(f"<div class='card'><h3>道具の制約が刺さる一点</h3>{escape(gl)}</div>")

    for b in st.get("beats", []):
        density = b.get("density", "")
        cls = "beat low" if density.startswith("低") else "beat"
        out.append(f"<div class='{cls}'>")
        out.append(
            f"<h4><span class='bars'>{escape(b.get('bars', ''))}</span>"
            f"{escape(b.get('job', ''))}"
            + (f" <span class='gadget'>密度 {escape(density)}</span>" if density else "")
            + "</h4>"
        )
        out.append(f"<div>{escape(b.get('content', ''))}</div>")
        if b.get("listener_prediction"):
            out.append(
                f"<div class='pred'>聞き手の予測: {escape(b['listener_prediction'])}</div>"
            )
        chips = by_beat.get(b.get("bars", ""), [])
        if chips:
            out.append("<div class='words'>" + "".join(_word_chip(w) for w in chips) + "</div>")
            out.append(
                "<details class='why-list'><summary>各語の仕事</summary><ul>"
                + "".join(
                    f"<li><b>{escape(w.get('surface', ''))}</b> — {escape(w.get('why', ''))}</li>"
                    for w in chips
                )
                + "</ul></details>"
            )
        out.append("</div>")

    pd = p.get("punch_design")
    if pd:
        out.append("<div class='card'><h3>パンチの設計</h3>")
        out.append(
            _kv(
                [
                    ("予測", pd.get("prediction", "")),
                    ("違反", pd.get("violation", "")),
                    ("第二の読み", pd.get("reframe", "")),
                    ("安全弁", pd.get("benignizer", "")),
                    ("タイミング", pd.get("timing", "")),
                ]
            )
        )
        out.append("</div>")

    cb = p.get("callback_design")
    if cb:
        out.append("<div class='card'><h3>前振りと回収</h3>")
        out.append(
            _kv(
                [
                    ("前振り", cb.get("setup", "")),
                    ("回収", cb.get("payoff", "")),
                    ("意味の変化", cb.get("meaning_change", "")),
                ]
            )
        )
        out.append("</div>")

    ba = p.get("bathos_design")
    if ba:
        out.append("<div class='card'><h3>バソスの落差</h3>")
        out.append(
            _kv(
                [
                    ("峰", ba.get("peak", "")),
                    ("谷", ba.get("drop", "")),
                    ("落とし先の物", ba.get("single_object", "")),
                ]
            )
        )
        out.append("</div>")

    tp = p.get("target_policy")
    if tp:
        allowed = "、".join(tp.get("allowed", []))
        avoided = "、".join(tp.get("avoided", []))
        out.append(
            "<div class='card'><h3>笑い・怒りの標的</h3>"
            + _kv([("向ける先", allowed), ("向けない先", avoided)])
            + "</div>"
        )

    ho = p.get("handoff_to_prehook")
    if ho:
        out.append(f"<div class='card'><h3>プリフックへの渡し</h3>{escape(ho)}</div>")

    rej = p.get("rejected_words", [])
    if rej:
        out.append(
            "<details class='why-list'><summary>落とした語と理由（"
            f"{len(rej)}件）</summary><ul class='rejected'>"
            + "".join(
                f"<li><b>{escape(r.get('surface', ''))}</b> — {escape(r.get('why_rejected', ''))}</li>"
                for r in rej
            )
            + "</ul></details>"
        )

    out.append("</section>")
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--title", default="バース別ペルソナと物語")
    args = ap.parse_args()

    personas = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.paths]
    total = sum(len(p.get("words", [])) for p in personas)

    body = [
        f"<h1>{escape(args.title)}</h1>",
        f"<div class='meta'>{len(personas)}バース / 採用語 {total}語。"
        "各語のチェックを外して『選択IDをコピー』すると、残した語のIDが返信用に取れます。"
        "語にカーソルを合わせると、その語がその場面で果たす仕事が出ます。</div>",
    ]
    body += [render_verse(p) for p in personas]
    body.append(select_bar())

    html = (
        "<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        f"<title>{escape(args.title)}</title>\n"
        f"<style>{BASE_CSS}{EXTRA_CSS}</style>\n"
        + "\n".join(body)
        + f"\n<script>{BASE_JS}</script>\n"
    )

    out = Path(args.out) if args.out else Path("run/verse_personas.html")
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html)} bytes, {len(personas)} verses, {total} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
