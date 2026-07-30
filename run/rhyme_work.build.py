#!/usr/bin/env python3
"""Work file: assemble rhyme-graph/v2 payload from tool outputs.
Inputs: rhyme_work.candidates.json, rhyme_work.graph.json,
        rhyme_work.scores.json, rhyme_work.g2p.json
Output: rhyme_graph.payload.json
Sound scores come from rhyme_score.py / rhyme_graph.py. semantic_fit,
syntactic_fit, novelty, transition_cost are model-curated annotations.
"""
import json
from pathlib import Path

D = Path(__file__).parent
cand = {n["id"]: n for n in json.load(open(D / "rhyme_work.candidates.json"))["nodes"]}
graph = json.load(open(D / "rhyme_work.graph.json"))
g2p = json.load(open(D / "rhyme_work.g2p.json"))
cli = json.load(open(D / "rhyme_work.scores.json"))
gnode = {n["id"]: n for n in graph["nodes"]}
gedge = {}
for e in graph["edges"]:
    gedge[frozenset((e["source"], e["target"]))] = e

surf2id = {}
for i, n in cand.items():
    surf2id.setdefault(n["surface"], i)
surf2id["ゾンビに"] = "zonbi"

cli_by_pair = {}
for d in cli:
    a = surf2id.get(d["surface_a"]); b = surf2id.get(d["surface_b"])
    if a and b:
        cli_by_pair[frozenset((a, b))] = d

# ---------------- nodes ----------------
CONF = {1.0: "high", 0.85: "medium"}
nodes_out = []
LONGVOWEL = {"tensei", "jinsei", "settei", "keikenchi", "teihen", "hiseiki", "keiyaku"}
for nid, n in cand.items():
    g = g2p[nid]
    notes = []
    if n.get("meta_note"):
        notes.append(n["meta_note"])
    if nid in LONGVOWEL:
        notes.append("エイ→エーの長音演奏読みを採用(long_vowel_performance_variant)")
    conf = "high" if n["reading_confidence"] >= 1.0 else "medium"
    nodes_out.append({
        "node_id": nid,
        "surface": n["surface"],
        "reading": n["reading"],
        "morae": g["moras"],
        "mora_count": g["mora_count"],
        "vowel_sequence": g["signature"],
        "consonant_sequence": g["onsets"],
        "special_morae": g["specials"],
        "accent": "unknown",
        "pos": n["part_of_speech"],
        "semantic_domain": [d for d in n["semantic_domains"] if not d.startswith("side:")],
        "side": [d for d in n["semantic_domains"] if d.startswith("side:")][0].split(":")[1],
        "register": n["register"],
        "proper_noun": False,
        "frequency_band": n["frequency"],
        "freshness": n["freshness"],
        "particles_before": n["particles_before"],
        "particles_after": n["particles_after"],
        "articulation_cost": n["articulation_cost"],
        "reading_confidence": conf,
        "reading_source": "manual+g2p.py mora解析(辞書バックエンド無しのため未照合)" if conf == "medium" else "surface-kana+g2p.py",
        "notes": notes,
    })

side = {n["node_id"]: n["side"] for n in nodes_out}
reg = {n["node_id"]: n["register"] for n in nodes_out}
mora_ct = {n["node_id"]: n["mora_count"] for n in nodes_out}
posmap = {n["node_id"]: n["pos"] for n in nodes_out}

# shared-morpheme pairs -> low value, never promote
SHARED = {
    frozenset(p): tag for p, tag in [
        (("gacha", "oyagacha"), "同語幹(ガチャ)派生ペア"),
        (("kakin", "mukakin"), "同語幹(課金)派生ペア"),
        (("kakin", "shogakukin"), "形態素「金」共有"),
        (("mukakin", "shogakukin"), "形態素「金」共有"),
        (("tenshoku_calling", "tenshoku_change"), "同音異義+形態素「職」共有"),
        (("muso", "musho"), "接頭辞「無」共有"),
        (("muso", "mukakin"), "接頭辞「無」共有"),
        (("musho", "mukakin"), "接頭辞「無」共有"),
        (("shuden", "shushinkoyo"), "形態素「終」共有"),
    ]
}

# curated flagship annotations: (pair): dict overrides
CUR = {
    ("tensei", "jinsei"): dict(sf=0.85, nov=0.55, rel="assonance", note="中核対: 転生への夢/一度きりの人生。既出例も多く novelty は中"),
    ("tensei", "settei"): dict(sf=0.85, nov=0.7, rel="slant", note="N/Q置換(テン/セッ)。「最初からハードモードの設定」文脈で機能"),
    ("tensei", "mensetsu"): dict(sf=0.8, nov=0.75, rel="slant", note="転生願望と面接落ちの対置。末尾ツ処理は内部置き推奨"),
    ("tenshoku_calling", "tenshoku_change"): dict(sf=0.75, nov=0.6, rel="exact", note="同音異義パン(天職/転職)。identity扱いで1回限りの掛詞に限定"),
    ("zangyo", "tenjo"): dict(sf=0.9, nov=0.85, rel="assonance", note="残業とガチャ天井=どちらも上限の見えない搾取。多義語天井が軸"),
    ("zangyo", "danjon"): dict(sf=0.85, nov=0.8, rel="slant", note="残業=ダンジョン周回。末尾ン/ーのNQR不一致、演奏で伸ばして寄せる"),
    ("kakin", "yachin"): dict(sf=0.9, nov=0.8, rel="assonance", note="課金と家賃=可処分所得の奪い合い。a-i-N完全一致"),
    ("shukai", "shukatsu"): dict(sf=0.85, nov=0.75, rel="slant", note="周回プレイと就活=同じ画面の繰り返し。末尾イ/ツのみ差"),
    ("chiito", "niito"): dict(sf=0.9, nov=0.85, rel="exact", note="チート/ニート=能力の過剰と欠如。1子音差の対義的ミニマルペア"),
    ("muso", "musho"): dict(sf=0.85, nov=0.7, rel="assonance", note="無双する主人公/無償で働く俺。接頭辞「無」共有につき使用は1回"),
    ("rodo", "shomo"): dict(sf=0.85, nov=0.7, rel="assonance", note="労働=消耗。o-R-o-R完全一致、同一領域なので意味距離は近め"),
    ("mao", "kacho"): dict(sf=0.9, nov=0.9, rel="assonance", note="魔王討伐/課長の説教。権力者の格落とし対比が主眼"),
    ("shujinko", "kyujinhyo"): dict(sf=0.9, nov=0.85, rel="assonance", note="主人公になれる求人は無い。5モーラ対応の主力ペア"),
    ("shujinko", "shushinkoyo"): dict(sf=0.85, nov=0.8, rel="slant", note="主人公補正/終身雇用=どちらも幻想。モーラ数差2は分割配置で吸収"),
    ("torakku", "burakku"): dict(sf=0.9, nov=0.85, rel="assonance", note="トラック転生/ブラック労働=入口の対比。Q含む4モーラ"),
    ("girudo", "shifuto"): dict(sf=0.85, nov=0.8, rel="assonance", note="ギルドの受付/シフト表。i-u-o一致、子音は遠い"),
    ("konbini", "zonbi"): dict(sf=0.9, nov=0.85, rel="mosaic", note="コンビニ/ゾンビ+に(助詞込みモザイク)。深夜レジの死んだ目"),
    ("isekai", "misekake"): dict(sf=0.85, nov=0.8, rel="assonance", note="異世界/見せかけ=誇大広告としての転生譚"),
    ("kuesuto", "kuezuni"): dict(sf=0.85, nov=0.8, rel="phrase", note="クエスト/食えずに=タスクは湧くのに飯が食えない。句モザイク"),
    ("reberuage", "nererumae"): dict(sf=0.85, nov=0.85, rel="phrase", note="レベル上げ/寝れる前=5モーラ完全母音一致の句対。ら抜き口語注意"),
    ("keikenchi", "teihen"): dict(sf=0.85, nov=0.8, rel="split", note="経験値/底辺=頭アンカーの分割韻(ケーケン/テーヘン)。余りチは次拍へ送る。suffix採点ツールでは0.272と過小評価"),
    ("genjitsu", "tenbiki"): dict(sf=0.85, nov=0.8, rel="slant", note="現実/天引き=手取りから引かれる現実。e-N-i-x対応"),
    ("jikyu", "chikyu"): dict(sf=0.9, nov=0.9, rel="exact", note="時給/地球=この惑星こそ低時給の異世界。1子音差(j/ch調音近接)"),
    ("rirekisho", "hiseiki"): dict(sf=0.85, nov=0.75, rel="slant", note="履歴書/非正規=書類と身分。母音のみ弱対応、内部置き推奨"),
    ("daihon", "daison"): dict(sf=0.85, nov=0.8, rel="assonance", note="他人の台本/十連で大損。a-i-o-N一致"),
    ("haiyaku", "keiyaku"): dict(sf=0.9, nov=0.85, rel="consonance", note="配役/契約=配られた役と有期契約。ヤク2モーラ完全+子音一致"),
    ("akuyaku", "koryaku"): dict(sf=0.8, nov=0.7, rel="consonance", note="悪役/攻略。ヤク着地の連鎖用リンク"),
    ("akuyaku", "haiyaku"): dict(sf=0.85, nov=0.75, rel="consonance", note="悪役/配役=配役への抗議の軸。形態素「役」共有につき連発禁止"),
    ("isekai", "risemara"): dict(sf=0.8, nov=0.7, rel="slant", note="異世界/リセマラ=やり直し願望。i-e-a対応"),
    ("mobu", "tenshoku_change"): dict(sf=0.75, nov=0.6, rel="assonance", note="モブ/転職(ショク)。2モーラ内部テクスチャ限定"),
    ("tenjo", "kyujinhyo"): dict(sf=0.85, nov=0.8, rel="assonance", note="天井/求人票=見上げる紙とスクロールする画面"),
    ("gacha", "risemara"): dict(sf=0.8, nov=0.6, rel="assonance", note="ガチャ/リセマラ。同領域2モーラ、内部テクスチャ"),
    ("gacha", "inkya"): dict(sf=0.7, nov=0.65, rel="slant", note="ガチャ運/陰キャ。拗音チャ/キャの口蓋近接"),
    ("mensetsu", "genjitsu"): dict(sf=0.85, nov=0.75, rel="slant", note="面接/現実=e-N-x-u対応。落選通知の現実"),
    ("shinya", "inkya"): dict(sf=0.8, nov=0.7, rel="assonance", note="深夜/陰キャ=i-N-a一致。深夜帯の自画像"),
    ("tenbiki", "konbini"): dict(sf=0.8, nov=0.75, rel="slant", note="天引き/コンビニ=給与明細と深夜バイト"),
    ("keikenchi", "zonbi"): dict(sf=0.75, nov=0.7, rel="slant", note="経験値ゼロ/ゾンビ=鼻音コーダの近接(ンチ/ンビ)"),
    ("suteetasu", "keiyaku"): dict(sf=0.75, nov=0.7, rel="slant", note="ステータス画面/契約(更新)。タス/ヤク弱対応+アク?要文脈"),
    ("shuden", "shogakukin"): dict(sf=0.75, nov=0.7, rel="slant", note="終電/奨学金=夜と借金。対応列は弱く内部置き"),
    ("kakin", "mukakin"): dict(sf=0.5, nov=0.1, rel="performance_variant", note="派生ペア。韻としては低価値、対句(課金圧/無課金の意地)専用"),
    ("gacha", "oyagacha"): dict(sf=0.5, nov=0.1, rel="performance_variant", note="派生ペア。韻でなくフックの反復素材"),
}

def base_edge(a, b):
    key = frozenset((a, b))
    ge = gedge.get(key)
    cd = cli_by_pair.get(key)
    if cd:
        bd = cd["best_domain"]
        return dict(score=cd["sound_score_after_penalty"], label=cd["label"],
                    matched=bd["domain_length"], vow=bd["vowel_or_coda"], ons=bd["onset"],
                    pen=cd["trivial_repetition_penalty"], src="rhyme_score.py(CLI)")
    if ge:
        al = ge["alignment"]
        vow = sum(x["vowel_or_coda_similarity"] for x in al) / len(al)
        ons = sum(x["onset_similarity"] for x in al) / len(al)
        return dict(score=ge["sound_score"], label=ge["label"], matched=ge["domain_morae"],
                    vow=round(vow, 3), ons=round(ons, 3), pen=0.0, src="rhyme_graph.py(score_pair)")
    return None

# ---- select edges ----
selected = []
seen = set()

def add(a, b):
    key = frozenset((a, b))
    if key in seen:
        return
    be = base_edge(a, b)
    if be is None:
        return
    seen.add(key)
    cur = CUR.get((a, b)) or CUR.get((b, a)) or {}
    cross = side[a] != side[b]
    same_dom = bool(set(cand[a]["semantic_domains"]) & set(cand[b]["semantic_domains"]) - {f"side:{side[a]}"})
    sf = cur.get("sf", 0.75 if cross else (0.55 if same_dom else 0.6))
    nov = cur.get("nov", 0.65 if cross else 0.4)
    cautions = []
    if frozenset((a, b)) in SHARED:
        cautions.append(SHARED[frozenset((a, b))] + "。低価値ラベル、高価値韻へ昇格禁止")
        nov = min(nov, 0.35)
    delta = abs(mora_ct[a] - mora_ct[b])
    if delta >= 2:
        cautions.append("モーラ数差が大きい(分割/延伸で吸収)")
    if be["matched"] <= 2:
        cautions.append("短スパン(2モーラ)。単独では弱テクスチャ")
    if be["label"] in ("weak-or-contextual", "not-established"):
        cautions.append("ツール判定weak。文脈・演奏補助が前提")
    if be["pen"] > 0:
        cautions.append("表層反復ペナルティあり(同音/同語幹)")
    regs = {reg[a], reg[b]}
    tc = 0.25 + (0.15 if ("formal" in regs and ("slang" in regs or "colloquial" in regs)) else 0.0) \
         + (0.1 if delta >= 2 else 0.0) + (0.1 if "phrase" in (posmap[a], posmap[b]) else 0.0)
    if be["matched"] >= 4:
        place = ["internal", "end", "cross_bar"]
    elif be["matched"] == 3:
        place = ["internal", "end"]
    else:
        place = ["internal"]
    rel = cur.get("rel")
    if rel is None:
        if be["vow"] >= 0.98 and be["ons"] >= 0.9:
            rel = "exact"
        elif be["vow"] >= 0.98:
            rel = "assonance"
        elif be["ons"] >= 0.75:
            rel = "consonance"
        else:
            rel = "slant"
        if "phrase" in (posmap[a], posmap[b]):
            rel = "phrase"
    syn = 0.6 if "phrase" in (posmap[a], posmap[b]) else (0.85 if posmap[a].endswith("suru") and posmap[b].endswith("suru") else 0.8)
    note = cur.get("note")
    selected.append({
        "edge_id": f"E{len(selected)+1:03d}",
        "from": a, "to": b,
        "relation": rel,
        "matched_morae": be["matched"],
        "vowel_similarity": round(be["vow"], 3),
        "consonant_similarity": round(be["ons"], 3),
        "mora_length_delta": delta,
        "accent_compatibility": "unknown",
        "sound_score": round(be["score"], 3),
        "sound_score_source": be["src"],
        "tool_label": be["label"],
        "semantic_fit": sf,
        "syntactic_fit": syn,
        "novelty": nov,
        "transition_cost": round(tc, 2),
        "placement_options": place,
        "cautions": cautions,
        "notes": note,
    })

# 1) curated flagship pairs first
for (a, b) in CUR:
    add(a, b)
# 2) all strong graph edges (>=0.80, >=3 morae)
for e in graph["edges"]:
    if e["sound_score"] >= 0.80 and e["domain_morae"] >= 3:
        add(e["source"], e["target"])

# ---------------- families ----------------
FAM = [
    ("fam-01", "エンセー族 (e-N-e-R)", ["e", "N", "e", "e"], ["tensei", "jinsei", "settei"], "転生/人生/設定。設定はQ置換のslantメンバー"),
    ("fam-02", "エン〜ウ族 (e-N-x-u)", ["e", "N", "o", "u"], ["tenshoku_calling", "tenshoku_change", "mensetsu", "genjitsu", "tenbiki", "mobu"], "転職・天職・面接・現実・天引き。モブは末尾o-uのみの弱メンバー"),
    ("fam-03", "アンヨー族 (a-N-o-R)", ["a", "N", "o", "o"], ["zangyo", "tenjo", "danjon", "mao", "kacho"], "残業/天井/ダンジョン+短形の魔王/課長"),
    ("fam-04", "シュー族 (u-R頭)", ["u", "u", "i", "N", "o", "o"], ["shukai", "shukatsu", "shuden", "kyujinhyo", "shushinkoyo", "shujinko"], "周回/就活/終電/求人票/終身雇用/主人公"),
    ("fam-05", "キン族 (a-i-N)", ["a", "i", "N"], ["kakin", "mukakin", "yachin", "shogakukin"], "課金/家賃が主力。無課金・奨学金は形態素共有注意"),
    ("fam-06", "ヤク族 (a-u+ヤク)", ["a", "i", "a", "u"], ["akuyaku", "haiyaku", "keiyaku", "koryaku"], "悪役/配役/契約/攻略。ヤク着地の連鎖用"),
    ("fam-07", "オー重音族 (o-R-o-R)", ["o", "o", "o", "o"], ["rodo", "shomo", "muso", "musho"], "労働/消耗+無双/無償(u-o-R)"),
    ("fam-08", "イー音族 (i-R-o / i-u-R)", ["i", "i", "o"], ["chiito", "niito", "jikyu", "chikyu"], "チート/ニート、時給/地球の2対"),
    ("fam-09", "イセ族 (i-e-a)", ["i", "e", "a", "i"], ["isekai", "risemara", "misekake"], "異世界/リセマラ/見せかけ"),
    ("fam-10", "クエ族 (u-e-u-o)", ["u", "e", "u", "o"], ["kuesuto", "kuezuni", "suteetasu"], "クエスト/食えずに。ステータスは頭u-eのみのslantメンバー"),
    ("fam-11", "イウオ族 (i-u-o)", ["i", "u", "o"], ["girudo", "shifuto"], "ギルド/シフト"),
    ("fam-12", "レベル句族 (e-e-u-a-e)", ["e", "e", "u", "a", "e"], ["reberuage", "nererumae"], "レベル上げ/寝れる前。5モーラ句対"),
    ("fam-13", "オンビ族 (o-N-i)", ["o", "N", "i", "i"], ["konbini", "zonbi"], "コンビニ/ゾンビ(+に)"),
    ("fam-14", "インヤ族 (i-N-a)", ["i", "N", "a"], ["shinya", "inkya"], "深夜/陰キャ"),
    ("fam-15", "ガチャ族 (a-a)", ["a", "a"], ["gacha", "oyagacha"], "同語幹。フック反復素材でありファミリー内は韻加点なし"),
    ("fam-16", "ラック族 (a-Q-u)", ["o", "a", "Q", "u"], ["torakku", "burakku"], "トラック/ブラック"),
    ("fam-17", "ダイオン族 (a-i-o-N)", ["a", "i", "o", "N"], ["daihon", "daison"], "台本/大損"),
    ("fam-18", "エーエン族 (e-R-e-N)", ["e", "e", "e", "N"], ["keikenchi", "teihen"], "経験値/底辺。頭アンカー分割韻"),
    ("fam-19", "イセキ族 (i-e-i)", ["i", "e", "i"], ["rirekisho", "hiseiki"], "履歴書/非正規。弱対応"),
]
assigned = [m for f in FAM for m in f[3]]
assert len(assigned) == len(set(assigned)) == 60, (len(assigned), len(set(assigned)))
families = [
    {"family_id": fid, "label": lab, "prototype_vowels": proto,
     "member_node_ids": mem, "notes": note}
    for fid, lab, proto, mem, note in FAM
]

vowel_heads = sorted({f["prototype_vowels"][0] for f in families})

payload = {
    "schema": "rhyme-graph/v2",
    "graph_scope": "テーマ中核語(異世界転生トロープ×現実労働)からの独立構築。vocabulary_bank/flow_map未参照(並列フェーズ第一便)",
    "seed_terms": ["転生", "ガチャ", "モブ", "周回", "残業", "課金", "異世界", "労働"],
    "nodes": nodes_out,
    "edges": selected,
    "families": families,
    "metrics": {
        "node_count": len(nodes_out),
        "edge_count": len(selected),
        "family_count": len(families),
        "vowel_family_heads": vowel_heads,
        "cross_side_edge_ratio": round(sum(1 for e in selected if side[e["from"]] != side[e["to"]]) / len(selected), 2),
        "cli_scored_pairs": len(cli),
        "proper_noun_nodes": 0,
    },
    "usage_guidance": [
        "同語幹・同形態素ペア(cautions記載)はフック反復・対句素材に限定し、韻の実績としてカウントしない",
        "matched_morae<=2のエッジは内部テクスチャ専用。行末アンカーには4モーラ以上のエッジを使う",
        "semantic_fit/noveltyはモデル注釈。ライン文脈確定後にflow_map側で再評価すること",
        "経験値/底辺は頭アンカー分割韻。suffix採点ツールの数値(0.272)をそのまま使わない",
    ],
    "warnings": [
        "g2p辞書バックエンド(pyopenjtalk/UniDic)が本環境に無く、漢字表記の読みは手動付与。g2p.pyのモーラ解析のみ通過(unverified)のためreading_confidence=medium",
        "エイ→エー等の長音演奏読みを採用(転生・人生・設定・経験値・底辺・非正規・契約)。辞書形は各ノードnotesに記載",
        "アクセント・無声化・拍位置は全ノードunknown(音源なし)。placement_optionsは提案であり確定ではない",
        "semantic_fit / syntactic_fit / novelty / transition_cost はモデルによるヒューリスティック+手動キュレーション値",
        "sound_scoreはrhyme_score.py(suffixアンカー)による。頭アンカー分割韻は過小評価される(該当エッジのcautions参照)",
    ],
}
out = D / "rhyme_graph.payload.json"
out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
print("edges:", len(selected), "cross-side ratio:", payload["metrics"]["cross_side_edge_ratio"])
rels = {}
for e in selected:
    rels[e["relation"]] = rels.get(e["relation"], 0) + 1
print("relations:", rels)
iso = set(cand) - {e["from"] for e in selected} - {e["to"] for e in selected}
print("isolated nodes:", iso or "none")
