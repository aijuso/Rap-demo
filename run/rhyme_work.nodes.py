#!/usr/bin/env python3
"""Work file: node seed definitions for isekai-satire-001 rhyme graph.
Writes rhyme_work.candidates.json (input for rhyme_graph.py).
Readings are performed readings (katakana). No dictionary backend is
available in this environment, so kanji readings are manual and flagged.
"""
import json
from pathlib import Path

# id, surface, reading(performed), pos, domains, register, freq_band,
# freshness, articulation_cost, reading_confidence, particles_before,
# particles_after, side(isekai/reality/bridge), notes
N = [
    # --- isekai / game trope side ---
    ("tensei", "転生", "テンセー", "noun_suru", ["isekai_trope", "rebirth"], "neutral", "common", 0.35, 0.2, "high", ["異世界に"], ["する", "したい", "先"], "isekai", "辞書形テンセイ/演奏読みで長音化"),
    ("isekai", "異世界", "イセカイ", "noun", ["isekai_trope", "world"], "neutral", "common", 0.3, 0.2, "high", ["この"], ["へ", "行き"], "isekai", ""),
    ("gacha", "ガチャ", "ガチャ", "noun", ["gacha", "game_mechanics", "money"], "colloquial", "common", 0.3, 0.1, "high", ["十連"], ["回す", "運"], "isekai", ""),
    ("oyagacha", "親ガチャ", "オヤガチャ", "noun", ["gacha", "inequality"], "slang", "common", 0.4, 0.2, "high", [], ["外れ", "のせい"], "bridge", "ガチャと語幹共有"),
    ("tenjo", "天井", "テンジョー", "noun", ["gacha", "money", "room_interior"], "neutral", "common", 0.55, 0.2, "high", ["課金の"], ["まで", "を見る"], "bridge", "多義: ガチャ天井/部屋の天井"),
    ("mobu", "モブ", "モブ", "noun", ["isekai_trope", "character_role"], "slang", "common", 0.35, 0.1, "high", ["ただの"], ["キャラ", "扱い"], "isekai", ""),
    ("shukai", "周回", "シューカイ", "noun_suru", ["game_mechanics", "repetition"], "neutral", "marked", 0.5, 0.2, "high", ["デイリー"], ["プレイ", "する"], "isekai", ""),
    ("chiito", "チート", "チート", "noun", ["game_mechanics", "privilege"], "colloquial", "common", 0.3, 0.1, "high", [], ["能力", "級"], "isekai", ""),
    ("reberuage", "レベル上げ", "レベルアゲ", "phrase_noun", ["game_mechanics", "growth"], "colloquial", "common", 0.4, 0.3, "high", ["深夜の"], ["に飽きた"], "isekai", "句ノード"),
    ("suteetasu", "ステータス", "ステータス", "noun", ["game_mechanics", "status"], "neutral", "common", 0.3, 0.3, "high", [], ["画面", "隠す"], "isekai", ""),
    ("kuesuto", "クエスト", "クエスト", "noun", ["game_mechanics", "task"], "neutral", "common", 0.3, 0.2, "high", ["強制"], ["受注", "消化"], "isekai", ""),
    ("girudo", "ギルド", "ギルド", "noun", ["isekai_trope", "organization"], "neutral", "marked", 0.4, 0.2, "high", [], ["の受付", "審査"], "isekai", ""),
    ("shujinko", "主人公", "シュジンコー", "noun", ["character_role", "protagonism"], "neutral", "common", 0.3, 0.3, "high", ["物語の"], ["補正", "面"], "isekai", ""),
    ("akuyaku", "悪役", "アクヤク", "noun", ["character_role"], "neutral", "common", 0.35, 0.2, "high", [], ["令嬢", "顔"], "isekai", ""),
    ("koryaku", "攻略", "コーリャク", "noun_suru", ["game_mechanics", "strategy"], "neutral", "common", 0.35, 0.3, "high", [], ["本", "する"], "isekai", ""),
    ("mao", "魔王", "マオー", "noun", ["character_role", "authority"], "neutral", "common", 0.3, 0.1, "high", [], ["討伐", "城"], "isekai", ""),
    ("muso", "無双", "ムソー", "noun_suru", ["isekai_trope", "dominance"], "colloquial", "common", 0.35, 0.1, "high", ["俺だけ"], ["する", "状態"], "isekai", ""),
    ("risemara", "リセマラ", "リセマラ", "noun_suru", ["gacha", "retry"], "slang", "marked", 0.5, 0.3, "high", ["人生を"], ["する", "不可"], "bridge", "リセットマラソンの略"),
    ("kakin", "課金", "カキン", "noun_suru", ["gacha", "money"], "neutral", "common", 0.3, 0.1, "high", ["月末に"], ["する", "圧"], "bridge", ""),
    ("mukakin", "無課金", "ムカキン", "noun", ["gacha", "money", "poverty"], "colloquial", "common", 0.4, 0.2, "high", [], ["勢", "の意地"], "bridge", "課金と語幹共有"),
    ("torakku", "トラック", "トラック", "noun", ["isekai_trope", "death_trigger", "vehicle"], "neutral", "common", 0.3, 0.2, "high", ["異世界行きの"], ["に轢かれ", "待ち"], "isekai", "転生の定番トリガー"),
    ("danjon", "ダンジョン", "ダンジョン", "noun", ["isekai_trope", "place"], "neutral", "common", 0.3, 0.2, "high", ["自動生成の"], ["攻略", "の奥"], "isekai", ""),
    ("settei", "設定", "セッテー", "noun_suru", ["narrative_device"], "neutral", "common", 0.3, 0.2, "high", ["初期"], ["ミス", "資料"], "bridge", "辞書形セッテイ"),
    ("keikenchi", "経験値", "ケーケンチ", "noun", ["game_mechanics", "growth"], "neutral", "common", 0.35, 0.3, "high", [], ["ゼロ", "稼ぎ"], "isekai", "辞書形ケイケンチ"),
    ("zonbi", "ゾンビ", "ゾンビ", "noun", ["monster", "exhaustion_metaphor"], "neutral", "common", 0.35, 0.2, "high", ["歩く"], ["みたい", "の列"], "bridge", ""),
    ("tenshoku_calling", "天職", "テンショク", "noun", ["work", "aspiration"], "neutral", "marked", 0.5, 0.2, "high", ["これが"], ["だと", "探し"], "reality", ""),
    # --- reality / labor side ---
    ("zangyo", "残業", "ザンギョー", "noun_suru", ["labor", "overtime"], "neutral", "common", 0.3, 0.2, "high", ["サービス"], ["代", "続き"], "reality", ""),
    ("shuden", "終電", "シューデン", "noun", ["commute", "night"], "neutral", "common", 0.3, 0.2, "high", [], ["逃し", "間際"], "reality", ""),
    ("shukatsu", "就活", "シューカツ", "noun_suru", ["job_hunting"], "colloquial", "common", 0.3, 0.2, "high", [], ["生", "戦線"], "reality", ""),
    ("kyujinhyo", "求人票", "キュージンヒョー", "noun", ["job_hunting", "document"], "neutral", "marked", 0.55, 0.4, "high", [], ["の嘘", "眺め"], "reality", ""),
    ("shushinkoyo", "終身雇用", "シューシンコヨー", "noun", ["labor_system"], "formal", "marked", 0.5, 0.4, "high", [], ["の幻", "は伝説"], "reality", ""),
    ("mensetsu", "面接", "メンセツ", "noun_suru", ["job_hunting"], "neutral", "common", 0.3, 0.2, "high", ["最終"], ["官", "で落ち"], "reality", ""),
    ("tenshoku_change", "転職", "テンショク", "noun_suru", ["labor", "retry"], "neutral", "common", 0.3, 0.2, "high", [], ["サイト", "を繰り返す"], "reality", "天職と同音"),
    ("rirekisho", "履歴書", "リレキショ", "noun", ["job_hunting", "document"], "neutral", "common", 0.35, 0.4, "high", [], ["を盛る", "の空欄"], "reality", ""),
    ("hiseiki", "非正規", "ヒセーキ", "noun", ["labor_status", "precarity"], "neutral", "common", 0.45, 0.3, "high", [], ["雇用", "のまま"], "reality", "辞書形ヒセイキ"),
    ("shogakukin", "奨学金", "ショーガクキン", "noun", ["debt", "education"], "neutral", "common", 0.4, 0.4, "high", [], ["の残高", "返済"], "reality", ""),
    ("yachin", "家賃", "ヤチン", "noun", ["money", "housing"], "neutral", "common", 0.3, 0.1, "high", ["今月の"], ["の督促", "を払う"], "reality", ""),
    ("tenbiki", "天引き", "テンビキ", "noun_suru", ["money", "wage"], "neutral", "marked", 0.55, 0.2, "high", ["給料から"], ["される", "の明細"], "reality", ""),
    ("jikyu", "時給", "ジキュー", "noun", ["money", "wage"], "neutral", "common", 0.3, 0.1, "high", ["深夜の"], ["換算", "で売る"], "reality", ""),
    ("chikyu", "地球", "チキュー", "noun", ["world", "reality"], "neutral", "common", 0.35, 0.1, "high", ["この"], ["という現場", "産"], "bridge", "現実側の「異世界」"),
    ("shinya", "深夜", "シンヤ", "noun", ["night", "time"], "neutral", "common", 0.3, 0.1, "high", [], ["勤務", "のレジ"], "reality", ""),
    ("inkya", "陰キャ", "インキャ", "noun", ["character_role", "self_image"], "slang", "common", 0.4, 0.2, "high", [], ["扱い", "の隅"], "reality", ""),
    ("konbini", "コンビニ", "コンビニ", "noun", ["place", "night_work"], "neutral", "common", 0.3, 0.2, "high", ["深夜の"], ["の灯り", "のレジ"], "reality", ""),
    ("shifuto", "シフト", "シフト", "noun", ["labor", "schedule"], "neutral", "common", 0.3, 0.1, "high", ["穴埋め"], ["を組まれ", "表"], "reality", ""),
    ("niito", "ニート", "ニート", "noun", ["labor_status", "self_image"], "colloquial", "common", 0.3, 0.1, "high", [], ["寸前", "呼ばわり"], "reality", ""),
    ("kacho", "課長", "カチョー", "noun", ["authority", "office"], "neutral", "common", 0.3, 0.1, "high", ["うちの"], ["の説教", "の椅子"], "reality", "役職の一般名詞"),
    ("rodo", "労働", "ロードー", "noun_suru", ["labor"], "formal", "common", 0.3, 0.2, "high", ["単純"], ["力", "時間"], "reality", ""),
    ("shomo", "消耗", "ショーモー", "noun_suru", ["exhaustion"], "neutral", "common", 0.35, 0.2, "high", [], ["戦", "品"], "reality", ""),
    ("musho", "無償", "ムショー", "noun", ["labor", "money"], "formal", "marked", 0.5, 0.1, "high", [], ["労働", "の愛"], "reality", ""),
    ("teihen", "底辺", "テーヘン", "noun", ["hierarchy", "self_image"], "colloquial", "common", 0.35, 0.2, "high", [], ["職", "からの視界"], "reality", "辞書形テイヘン"),
    ("genjitsu", "現実", "ゲンジツ", "noun", ["reality"], "neutral", "common", 0.25, 0.2, "high", ["この"], ["逃避", "に戻る"], "reality", ""),
    ("jinsei", "人生", "ジンセー", "noun", ["life"], "neutral", "common", 0.25, 0.1, "high", ["一度きりの"], ["設計", "の主役"], "reality", "辞書形ジンセイ"),
    ("burakku", "ブラック", "ブラック", "noun", ["labor", "exploitation"], "slang", "common", 0.35, 0.2, "high", [], ["な現場", "認定"], "reality", "劣悪労働の一般語"),
    ("haiyaku", "配役", "ハイヤク", "noun", ["narrative_device", "role_assignment"], "neutral", "marked", 0.55, 0.2, "high", ["勝手な"], ["ミス", "を拒む"], "bridge", ""),
    ("keiyaku", "契約", "ケーヤク", "noun_suru", ["labor", "document"], "neutral", "common", 0.3, 0.2, "high", ["有期"], ["更新", "書"], "reality", "辞書形ケイヤク"),
    ("daison", "大損", "ダイソン", "noun_suru", ["money", "loss"], "colloquial", "marked", 0.5, 0.2, "high", ["十連で"], ["こいた"], "reality", ""),
    ("nererumae", "寝れる前", "ネレルマエ", "phrase", ["night", "exhaustion"], "colloquial", "marked", 0.55, 0.3, "high", [], ["に朝"], "reality", "ら抜き口語。句ノード"),
    ("kuezuni", "食えずに", "クエズニ", "phrase", ["poverty"], "colloquial", "marked", 0.55, 0.2, "high", ["夢じゃ"], ["並ぶ"], "reality", "句ノード"),
    ("misekake", "見せかけ", "ミセカケ", "noun", ["deception"], "neutral", "common", 0.4, 0.2, "high", [], ["の自由", "の福利"], "reality", ""),
    ("daihon", "台本", "ダイホン", "noun", ["narrative_device", "script"], "neutral", "common", 0.35, 0.2, "high", ["他人の"], ["を破る", "通り"], "bridge", ""),
]

nodes = []
for (nid, surface, reading, pos, domains, register, freq, fresh, art, conf, pb, pa, side, note) in N:
    nodes.append({
        "id": nid,
        "surface": surface,
        "reading": reading,
        "part_of_speech": pos,
        "semantic_domains": domains + [f"side:{side}"],
        "register": register,
        "frequency": freq,
        "freshness": fresh,
        "articulation_cost": art,
        "reading_confidence": 1.0 if all("ぁ" <= c <= "ヿ" or c == "ー" for c in surface) else 0.85,
        "particles_before": pb,
        "particles_after": pa,
        "proper_noun": False,
        "source": "manual",
        "position": "unplaced",
        "meta_note": note,
    })

out = Path(__file__).parent / "rhyme_work.candidates.json"
out.write_text(json.dumps({"nodes": nodes}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(nodes)} nodes")
