#!/usr/bin/env python3
"""Shared self-contained HTML scaffolding for research/rhyme bank tables.

Everything is inlined (CSS + vanilla JS, no external requests) so the file can
be attached in chat or opened from disk. Tables support column sort, text
filter, per-column select filters, and row checkboxes whose ids can be copied
as a comma-separated list for checkpoint replies.
"""

from __future__ import annotations

from html import escape

BASE_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 1.2rem;
  font-family: "Hiragino Sans", "Noto Sans JP", system-ui, sans-serif;
  font-size: 14px; line-height: 1.55;
  background: #fafafa; color: #1a1a1a;
}
@media (prefers-color-scheme: dark) {
  body { background: #16181d; color: #e8e8e8; }
  table { border-color: #333 !important; }
  th { background: #23262e !important; }
  tr:nth-child(even) td { background: #1c1f26; }
  input, select, button { background: #23262e; color: #e8e8e8; border: 1px solid #444; }
  .badge-ok { background: #1d4028 !important; color: #9be3af !important; }
  .badge-ng { background: #4a1f1f !important; color: #f3a6a6 !important; }
  .pill { background: #2a2e38 !important; }
}
h1 { font-size: 1.3rem; margin: 0 0 .3rem; }
h2 { font-size: 1.05rem; margin: 1.6rem 0 .4rem; }
.meta { color: #777; font-size: .85rem; margin-bottom: 1rem; }
.controls { display: flex; flex-wrap: wrap; gap: .5rem; margin: .8rem 0; align-items: center; }
input[type=search], select { padding: .35rem .5rem; border: 1px solid #ccc; border-radius: 6px; }
button { padding: .4rem .8rem; border: 1px solid #bbb; border-radius: 6px; cursor: pointer; }
.tablewrap { overflow-x: auto; border: 1px solid #ddd; border-radius: 8px; }
table { border-collapse: collapse; width: 100%; min-width: 720px; }
th, td { padding: .4rem .6rem; text-align: left; border-bottom: 1px solid #e2e2e2; vertical-align: top; }
th { background: #f0f1f4; position: sticky; top: 0; cursor: pointer; user-select: none; white-space: nowrap; }
th .dir { opacity: .5; font-size: .75rem; }
tr:nth-child(even) td { background: #f6f7f9; }
.skel { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: .85rem; white-space: nowrap; }
.pill { display: inline-block; padding: .05rem .5rem; border-radius: 999px; background: #e8eaf0; font-size: .78rem; margin: 0 .15rem .15rem 0; white-space: nowrap; }
.badge-ok { background: #d9f2df; color: #14602a; padding: .1rem .5rem; border-radius: 6px; font-size: .78rem; }
.badge-ng { background: #f8dcdc; color: #8c1d1d; padding: .1rem .5rem; border-radius: 6px; font-size: .78rem; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.selectbar { position: sticky; bottom: 0; background: inherit; padding: .6rem 0; display: flex; gap: .6rem; align-items: center; }
#selcount { font-weight: 600; }
a { color: inherit; }
td.src { max-width: 16rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
"""

BASE_JS = """
function tableOf(el) { return el.closest('table'); }
function sortTable(th) {
  const table = tableOf(th);
  const tbody = table.querySelector('tbody');
  const index = Array.from(th.parentNode.children).indexOf(th);
  const dir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
  table.querySelectorAll('th').forEach(h => { h.dataset.dir = ''; const d = h.querySelector('.dir'); if (d) d.textContent = ''; });
  th.dataset.dir = dir;
  const mark = th.querySelector('.dir'); if (mark) mark.textContent = dir === 'asc' ? '▲' : '▼';
  const numeric = th.dataset.type === 'num';
  Array.from(tbody.rows)
    .sort((a, b) => {
      const av = a.cells[index].dataset.v ?? a.cells[index].textContent.trim();
      const bv = b.cells[index].dataset.v ?? b.cells[index].textContent.trim();
      const cmp = numeric ? (parseFloat(av) || 0) - (parseFloat(bv) || 0) : av.localeCompare(bv, 'ja');
      return dir === 'asc' ? cmp : -cmp;
    })
    .forEach(row => tbody.appendChild(row));
}
function applyFilters(scope) {
  const root = scope ? document.getElementById(scope) : document;
  const q = (root.querySelector('input[type=search]')?.value || '').toLowerCase();
  const selects = Array.from(root.querySelectorAll('select[data-col]'));
  root.querySelectorAll('tbody tr').forEach(row => {
    let show = !q || row.textContent.toLowerCase().includes(q);
    for (const sel of selects) {
      if (!show) break;
      if (sel.value && row.dataset[sel.dataset.col] !== sel.value) show = false;
    }
    row.style.display = show ? '' : 'none';
  });
  updateCount();
}
function updateCount() {
  const n = document.querySelectorAll('input.rowsel:checked').length;
  const el = document.getElementById('selcount');
  if (el) el.textContent = n + '件選択中';
}
function copySelected() {
  const ids = Array.from(document.querySelectorAll('input.rowsel:checked')).map(cb => cb.value);
  const text = ids.join(',');
  const out = document.getElementById('selout');
  if (out) out.value = text;
  if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
}
document.addEventListener('change', e => { if (e.target.classList.contains('rowsel')) updateCount(); });
"""


def page(title: str, body: str) -> str:
    return (
        "<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        f"<title>{escape(title)}</title>\n"
        f"<style>{BASE_CSS}</style>\n"
        f"{body}\n"
        f"<script>{BASE_JS}</script>\n"
    )


def select_bar() -> str:
    return (
        "<div class='selectbar'>"
        "<span id='selcount'>0件選択中</span>"
        "<button type='button' onclick='copySelected()'>選択IDをコピー</button>"
        "<input id='selout' type='text' readonly size='48' "
        "placeholder='ここに選択IDが入ります（返信に貼り付け）'>"
        "</div>"
    )


def th(label: str, numeric: bool = False) -> str:
    kind = " data-type='num'" if numeric else ""
    return f"<th onclick='sortTable(this)'{kind}>{escape(label)} <span class='dir'></span></th>"
