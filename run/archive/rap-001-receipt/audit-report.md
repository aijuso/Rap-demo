# Professional Audit — `rap-001-receipt` / 「領収書」

```yaml
schema: professional-audit/v2
run_id: rap-001-receipt
draft_revision: 1
auditor:
  independence: partial      # 別エージェントによるブラインド監査は未実施
verification:
  text_read: true
  spoken_read: false
  recorded_on_beat: false
```

## 監査の独立性について

このセッションでは Draft Integrator と監査者が同一コンテキストである。
`professional-audit-v2.md` の規定により `audit_independence: partial` とし、
総合点に上限を適用する。ブラインド監査（`rap-professional-auditor` サブエージェント）は未実施。

## Hard gates

| Gate | 内容 | 結果 | 根拠 |
|---|---|---|---|
| G1 | 著作権・模倣 | **pass** | 参照指定なし。既存曲の語句・場面順・オチの流用なし。固有名詞ゼロ |
| G2 | 意味の完全性 | **pass** | 全24小節に平易な言い換えを付与し、`interesting_without_rhyme_review` が全 pass |
| G3 | 自然な日本語 | **pass** | 全24小節に naturalness 証拠あり。韻のための倒置・助詞抜けなし |
| G4 | Brief・話者・事実 | **pass** | 一人称固定、知識境界内。捏造された経歴・困窮・方言なし |
| G5 | 最低限の曲機能 | **pass** | setup/payoff 6組が解決。抽象語トークン比率 0.112 |
| G6 | 実演可能性 | **UNVERIFIED** | ビート・録音なし。**総合84点上限** |
| G7 | 安全・名誉 | **pass** | 実在人物への言及・断定なし |

`professional_audit.py` の判定: `eligible-for-human-release-review` / hard_gate_failures 0件。

## 診断値（実測）

```
bar_count                 24
rhyme_hit_count           25
end_rhyme_bias            0.68     （行末以外 8件）
dominant_family_ratio     0.08
grammar_tail_ratio        0.00
low_confidence_rhymes     0
abstract_token_ratio      0.112
four_bar_windows          6/6 pass （全窓で information / emotion / flow が変化）
unresolved_setups         []
orphan_payoffs            []
```

## 100点 rubric

| Category | 配点 | 評点 | 証拠 |
|---|---:|---:|---|
| Brief・話者・事実境界 | 8 | 7 | 話者の視点・呼びかけ相手が全編一貫。捏造なし。−1 は brief がユーザー確認を経ていない既定値である点 |
| 意味・因果・行ごとの明瞭さ | 14 | 12 | 全24小節を平易に言い換え済み。−2 は B01「差はゼロコンマ」と B08「取り分」の圧縮が初聴で解けにくい点 |
| セクション進行 | 10 | 8 | 6窓すべてで情報・感情・flow が変化。−2 は B17–B20 が観察の連続で、感情の階段が最も浅い点 |
| 具体語・映像・語彙 | 10 | 9 | 抽象トークン比率 0.112。抽象語は「後悔・限界・感情」の3語のみで、いずれも直前の具体物に接地 |
| 韻と音の architecture | 15 | 11 | 行末バイアス 0.68、ファミリー占有 0.08、文法語尾一致 0.00 と分布は良好。−4 は B15/B16 が同一形態素「桁」依存、B17/B18 が 0.74 と弱いこと、B05/B06 の「精算」が韻ではなく同語反復であること |
| Flow・休符・呼吸 | 13 | 7 | 密度 13–21モーラの contour を設計し、B07 を sparse、B14 を burst に配置。ただし **すべて proposal**。録音がないため上限を超えられない |
| ユーモア・surprise・punch | 8 | 6 | B07「足が出る／足が出た」は setup・違反軸・共有項・着地語が揃う。B16 の桁落ちは bathos として機能。−2 は B17「湯たんぽ」が笑いとしては弱く画像止まりな点 |
| Hook または return 設計 | 7 | 5 | Hook が選択肢を提示し「領収書」を無韻で置く。反復時に Verse の「割り勘」が「取り分」を再意味づけする。−2 はメロディック・セルがなく反復の力がテキストだけに依存している点 |
| 自然な日本語と声 | 8 | 7 | 全小節 naturalness pass。−1 は B24「レシートと感情」の並列助詞が意図的な語域衝突で、聴者によっては引っかかる点 |
| 独創性と revision evidence | 7 | 4 | 模倣なし・参照なし。−3 は **独立監査と再監査が未実施**である点 |
| **raw_total** | **100** | **76** | |

```
applied_cap : 84   （G6 UNVERIFIED — 録音なし）
final_score : 76
decision    : conditional_pass
```

`conditional_pass` = テキストとしては公開検討可能。ただし録音検証と独立監査を経るまで
「完成」とは呼ばない。

## 残存 issue（優先順）

| ID | 深刻度 | 小節 | 層 | 内容 | 受入テスト |
|---|---|---|---|---|---|
| A-001 | major | 全体 | process | 独立したブラインド監査と再監査が未実施。独創性・韻・ユーモアの評価に自己確証バイアスが残る | 別コンテキストの監査者が hard gate から再実行し、critical が0件 |
| A-002 | major | 全体 | flow | 88BPM 実ビート上での録音が未実施。B14(21モーラ)・B18(20モーラ)・B21(20モーラ) が潰れずに発音できるか不明 | 3テイク（neutral / exaggerated / underplayed）で重要語が全て聞き取れる |
| A-003 | minor | B15,B16 | rhyme | 「四桁／三桁」が同一形態素「桁」に依存。freshness が低い | 桁の対比を保ったまま、片側を別語尾に置換しても bathos が残る |
| A-004 | minor | B17,B18 | rhyme | 「湯たんぽ／ポケット」は 0.74 と本作で最も弱い韻 | 同じ2つの映像を保ったまま 0.85 以上のペアが見つかる、または非韻区間として確定させる |
| A-005 | minor | B13–B17 | syntax | 体言止めが5小節連続。全体でも 15/24（62%）と高め | 映像を落とさずに1小節を述語終止へ変えられる |

## 保持すべき強み

- B07 の慣用句字義化。setup と payoff が同一小節に収まり、直前に1拍の空白がある。
- B23/B24 の「勘定／感情」。同音異義で意味が完全に切り替わり、曲全体の主張を1語で担う。
- B11/B12「一円は割れても 一秒は間に合わん」。金銭の精度と時間の非可逆を同じ「一」で対比。
- 抽象語比率 0.112。AI が収束しがちな抽象クラスタ（未来・運命・光・闇・翼・王冠 等）が皆無。
- 固有名詞ゼロ。知名度依存の見せかけの具体性がない。

## 未検証のまま残る主張

- pocket、microtiming、呼吸位置、スタミナ
- アクセントの自然さ（ピッチアクセント）
- B22 の「足の声」と B23 の地の声が聴覚的に区別できるか
- 休符が緊張として機能するか、単なる空白に聞こえるか
- 全読みは手動指定（本環境では pyopenjtalk / fugashi が利用不可）
