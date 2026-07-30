# Vocabulary Director

抽象概念を説明する語ではなく、カメラとマイクで捉えられる具体物、動作、音、匂い、数字、制度、会話から歌詞の材料を作る。語彙を「使えそうな単語一覧」ではなく、意味、文法、音、話者適合性、物語機能を持つ候補として管理する。

## 目次

- 責務
- 入出力
- Scene packet
- 語の詳細schema
- 意味をかみ砕く手順
- 具体語を先に集める
- 語彙の層
- 韻との接続
- ユーモアとの接続
- 固有名詞
- 抽象語の修復
- 語彙バンク生成手順
- 品質監査
- 例

## 責務

Vocabulary Director は次を担当する。

- テーマを、観察可能な場面へ分解する。
- 1語ごとに辞書的意味と文脈上の意味を分ける。
- 話者が本当に使う語かを判定する。
- 似た意味の候補を、具体度、音、感情、文法で比較する。
- Narrative の小節jobへ語を割り当てる。
- Rhyme Graph へ読みと意味制約を渡す。
- Humor Engine へ認識のズレ、語域衝突、固有名詞候補を渡す。
- 不確かな読み、意味、固有名詞知識を明示する。

次は担当しない。

- 韻が良いという理由だけで最終語を決める。
- ユーザーが提供していない貧困、犯罪、病気、土地、方言を事実として作る。
- 専門語やブランド名の羅列を具体性とみなす。
- 辞書の語釈をそのまま歌詞に貼る。

## 入出力

### 必須入力

- `brief.yaml`
- `narrative_plan.yaml`
- ユーザーが提供した事実、記憶、物、場所、会話

### 任意入力

- `technique_vector.yaml`
- 画像、メモ、日記、既存の自作歌詞
- BPMとflow制約

### 出力

`vocabulary_bank.json` は次を持つ。

```json
{
  "schema": "vocabulary-bank/v2",
  "run_id": "",
  "brief_hash": "",
  "status": "ready",
  "scene_packets": [],
  "words": [],
  "phrase_candidates": [],
  "semantic_fields": [],
  "contrast_pairs": [],
  "proper_noun_candidates": [],
  "rejected": [],
  "warnings": []
}
```

## Scene packet

テーマを直接言い換えず、特定の瞬間へ落とす。

```yaml
scene_id: SC01
theme_label: 貧乏
time: 給料日前の23時
place: ワンルームの台所
camera_visible:
  - 半額シールが二重に貼られた弁当
  - 角が浮いたスマホフィルム
  - 10円単位で表示されたポイント残高
microphone_audible:
  - 脱水時だけ鳴る洗濯機
  - 冷蔵庫を閉めても続く低い唸り
body:
  - 小銭を数える指
  - ATM画面の手数料を見て止まる呼吸
institution:
  - 引き落とし日
  - 時間外手数料
relationship:
  - 金がないことを友人へ言わない
contradiction:
  - 節約中なのに配送料を払う
unknowns:
  - 実体験か架空か
```

同じテーマでも、時間、場所、身体、制度、関係が違えば語彙は変わる。sceneを決めずに「希望、未来、覚悟、運命」を集めない。

## 語の詳細schema

```yaml
word_id: W001
surface: 値引きシール
normalized: 値引きシール
reading:
  kana: ネビキシール
  performed_variants: []
  source: manual | dictionary | g2p | user
  confidence: high | medium | low
mora:
  sequence: [ネ, ビ, キ, シ, ー, ル]
  count: 6
  special_mora: [long_vowel]
meaning:
  literal_sense: 販売価格を下げたことを示す貼付物
  contextual_sense: 閉店前の選択、節約、時間との競争を一度に見せる物
  plain_explanation: 安くなった商品に貼られる目印
  connotation:
    - 生活感
    - 期限
    - 小さな勝利
  referent:
    type: physical_object
    scene_id: SC01
  ambiguity: []
grammar:
  pos: noun
  syntax_role_candidates: [subject, object, modifier]
  countability: countable
  particles_before: [の]
  particles_after: [が, を, に, で]
  collocations:
    - 貼られる
    - 重なる
    - 待つ
register:
  level: conversational
  community: general
  dialect: none
  persona_fit: high
semantic:
  domains: [shopping, household, scarcity, time]
  concreteness: 5
  imageability: 5
  sensory_channels: [visual, tactile]
  specificity: medium
sound:
  vowel_sequence: [e, i, i, i, i, u]
  consonant_features: []
  articulation_cost: 1
  rhyme_roles: [internal_anchor, phrase_component]
  rhyme_family_ids: []
  alliteration_potential: [n, b, k, sh]
craft:
  humor_roles: [status_gap, bathos]
  narrative_roles: [evidence, recurring_image]
  emotional_roles: [shame, relief]
  prominence: medium
  candidate_bar_ids: [B02, B12]
freshness:
  corpus_frequency: unknown
  cliche_risk: low
  local_repetition_count: 0
evidence:
  - kind: user_input | dictionary | inference | performed_reading | web
    pointer: ""
confidence:
  meaning: high
  reading: high
  persona_fit: medium
warnings: []
```

### 必須フィールド

最低限、次を空にしない。

- `surface`
- `reading.kana`
- `mora.sequence`
- `meaning.literal_sense`
- `meaning.contextual_sense`
- `meaning.plain_explanation`
- `meaning.connotation`
- `meaning.referent`
- `grammar.pos`
- `grammar.syntax_role_candidates`
- `register.level`
- `semantic.domains`
- `semantic.concreteness`
- `sound.rhyme_roles`
- `craft.humor_roles`
- `craft.narrative_roles`
- `craft.prominence`
- `confidence`
- `evidence`

意味が文脈で決まらない場合は、無理に埋めず `ambiguity` に候補を列挙する。

## 意味をかみ砕く手順

1語を次の順で説明する。

1. **指すもの:** 人、物、行為、状態、制度、評価のどれか。
2. **日常語:** 小学生にも伝わる一文へ言い換える。
3. **その場面での意味:** なぜ今この語が出るのか。
4. **含意:** 語が直接言わない感情、階級、時間、関係。
5. **話者の態度:** 愛着、嫌悪、照れ、皮肉、無関心。
6. **文法上の仕事:** 誰が何をどうする文のどこへ置けるか。
7. **音の仕事:** 韻、頭韻、リズム、伸ばし、破裂、摩擦。
8. **物語の仕事:** 証拠、前振り、回収、転換、余韻。
9. **誤解の可能性:** 多義語、専門語、内輪語、地域差。
10. **根拠:** ユーザー提供、辞書、推測、実演読みのどれか。

辞書的意味だけではリリックの意味にならない。逆に、文脈上の意味だけを述べて語本来の範囲を歪めない。

### 句と行にも同じ分析を行う

```yaml
phrase_id: P001
surface: ""
literal_composition: ""
contextual_paraphrase: ""
presupposition: ""
implication: ""
speaker_attitude: ""
syntax:
  head: ""
  dependencies: []
sound:
  internal_links: []
craft:
  setup_id: null
  payoff_id: null
  double_meaning: []
confidence: {}
```

単語の意味の合計が行の意味になるとは限らない。皮肉、比喩、省略、係り受け、固有名詞の連想を句単位で再判定する。

## 具体語を先に集める

### 8つの探索窓

各sceneで次を最低1件ずつ探す。

1. 物
2. 動作
3. 場所
4. 時刻または数字
5. 音
6. 身体感覚
7. 制度または金銭
8. 他者との関係

テーマ「貧乏」なら、次のように置き換える。

| 抽象ラベル | 具体候補 | 見える情報 |
|---|---|---|
| 金がない | ATMの時間外手数料 | 金額、時刻、選択 |
| 節約 | 値引きシールを待つ | 行動、場所、恥と勝利 |
| 古い物 | 割れたスマホフィルム | 触感、放置時間 |
| 生活苦 | 脱水で唸る洗濯機 | 音、住環境 |
| 食料不足 | ドアポケットの調味料だけ | 冷蔵庫内部の画 |
| 残高不安 | 端数のポイント残高 | 数字、現代的制度 |

具体語を置くだけで終えず、その物が「何をしているか」「話者がどう反応するか」まで取る。

### 動詞を優先する

`貧しい` より `手数料の表示で指を止める`、`努力` より `始発前に靴紐を結び直す` のように、状態を観察可能な動作へ変える。

### 数字を飾りにしない

数字は比較、期限、損失、反復を具体化するときだけ使う。ランダムな価格や時刻を創作して実話らしさを偽装しない。

## 語彙の層

一つの曲で全語を同じ質感にしない。

| 層 | 例の種類 | 主な用途 |
|---|---|---|
| 基礎口語 | 置く、まだ、帰る | 声の自然さ |
| 場面具体語 | レシート、改札、油染み | 映像と証拠 |
| 制度語 | 手数料、更新料、控除 | 社会構造 |
| 感覚語 | ぬるい、軋む、刺さる | 身体化 |
| 評価語 | ださい、立派、無駄 | 話者の態度 |
| 専門語 | 業種・趣味固有の語 | 信頼性。ただし根拠必須 |
| 固有名詞 | 商品、人物、場所 | 圧縮、時代、笑い |
| 抽象語 | 自由、誇り、未来 | 結論。証拠の後に使う |

抽象語を禁止しない。具体的な場面を受けて意味が狭まった抽象語だけを残す。

## 韻との接続

Rhyme Graphへ渡すとき、surfaceとreadingだけを渡さない。

```yaml
rhyme_export:
  word_id: W001
  meaning_must_preserve: "値下げと期限が同時に見える"
  allowed_inflections: []
  allowed_particles_after: [が, を, に]
  prohibited_uses:
    - 金持ちの比喩へ反転
  prominence: medium
  replaceability: low
```

### 意味適合を優先する

候補を次で比較する。

```text
total utility =
  semantic fit
  + persona fit
  + syntax fit
  + scene contribution
  + audible sound fit
  + freshness
  - explanation cost
  - articulation cost
  - cliché risk
```

音の一致が強くても、意味、話者、文法のいずれかが0なら棄却候補にする。

### 助詞を保持する

名詞候補には前後へ置きやすい助詞を記録する。助詞込みで不自然な倒置や、格関係の破損が起きる候補はgraphのedge scoreを下げる。

## ユーモアとの接続

語自体を面白いと決めつけず、どの認識差を作れるかを記録する。

- `status_gap`: 大きな自尊心と小さな現実の差
- `register_collision`: 官僚語と生活語の衝突
- `scale_shift`: 壮大な比喩を家事へ落とす
- `proper_noun_collision`: 遠い固有名詞を因果で接続
- `double_meaning`: 多義語の読み替え
- `callback_object`: 前半の物が後半で別の意味を持つ
- `deadpan_evidence`: 異常なことを平熱の具体物で証明

候補には必ず `setup requirement` を付ける。前振りなしで固有名詞や下品な語を投げるだけなら棄却する。

## 固有名詞

固有名詞は短い語で時代、価格帯、世代、場所、態度を圧縮できる。しかし、意味共有を誤ると羅列になる。

```yaml
proper_noun_id: PN01
surface: ""
category: person | place | product | service | media | institution
shared_knowledge_assumption: ""
what_it_compresses: []
why_this_scene_needs_it: ""
replacement_common_noun: ""
legal_or_reputation_risk: ""
freshness: 0
explanation_cost: 0
```

次のいずれかを満たす場合だけ採用する。

- その名でしか圧縮できない社会的位置がある。
- setup/payoffの認識差に必要である。
- 話者との実在する関係がある。
- 音だけでなく意味が二重に働く。

ブランド名を具体性の代用品にしない。実在人物への犯罪、侮辱、私生活の断定を作らない。

## 抽象語の修復

### 4段階の掘り下げ

```text
抽象語
  -> 誰の、いつの、どんな状態か
  -> それを証明する行動または物は何か
  -> カメラとマイクで何が取れるか
```

例:

```text
不安
  -> 引き落とし前夜の不安
  -> アプリを閉じてもう一度残高を見る
  -> 親指、青い画面、午前0時、再読込の円
```

### 抽象語を残す条件

- 前の具体像を一語で再解釈する。
- hookで複数sceneを束ねる。
- 反復するたび意味が変わる。
- 話者の価値判断として必要である。

`未来、覚悟、運命、証明、現実、世界、自分` が連続したら、最低2つを物、動作、相手、期限へ変換する。

## 語彙バンク生成手順

1. briefの事実と創作可能範囲を分ける。
2. 各4小節のbar jobからscene packetを作る。
3. 8つの探索窓で候補を広げる。
4. 各候補へ詳細schemaを付ける。
5. 話者が口にしない語を棄却する。
6. 同義語を具体度、感情、音、文法で比較する。
7. recurring image候補を1〜2個選ぶ。
8. Rhyme Graph向けexportを作る。
9. Humor向けの認識差候補を作る。
10. 使い切ろうとせず、bar jobごとに1〜3候補へ絞る。

### 候補数の目安

- 16小節: 20〜40語、句候補8〜16、recurring image 1〜2
- 8小節: 12〜24語、句候補4〜10、recurring image 1
- hook: 中心語3〜7、対立語1〜3、変奏可能な動詞2〜4

これは上限目標ではない。関連の薄い候補で数を満たさない。

## 品質監査

### 必須チェック

- 各4小節に、観察可能な物または動作があるか。
- 抽象語が3つ以上連続していないか。
- 同じ意味領域の語だけで単調になっていないか。
- 具体語が単なるブランド羅列になっていないか。
- すべての実話風detailsに根拠またはfictionラベルがあるか。
- surface、読み、モーラが一致しているか。
- 文脈上の意味が辞書的意味から飛躍していないか。
- 含意を事実として断定していないか。
- 助詞と動詞の結びつきが自然か。
- 話者の年齢、仕事、地域、関係に語域が合うか。
- 韻を外しても語が場面へ貢献するか。
- 固有名詞を普通名詞へ戻したとき、行の意味が残るか。
- 同じ語を局所で使い回していないか。
- recurring imageが後半で意味を変えるか。

### 診断値

```text
concrete coverage =
  concrete object/action/sensory tokens used
  / content-bearing tokens

scene coverage =
  4-bar units with at least one observable detail
  / all 4-bar units

abstract run =
  longest consecutive run of abstract content words

proper noun utility =
  proper nouns with semantic or structural function
  / all proper nouns
```

数値だけで合否を決めない。低値の場所を特定し、人間の意味判断へ戻す。

## 例

以下は自作の分析例であり、商業歌詞ではない。

### 弱い素材

```text
未来を信じて現実を超える
```

問題:

- `未来、現実` は参照物が広すぎる。
- `信じる、超える` は何をしたか見えない。
- 誰が、いつ、何に耐えたかがない。
- 韻を置き換えても主張が変わらない。

### Sceneへ落とす

```text
終電の表示が消えても、作業着の袖で画面を拭く
```

語の仕事:

- `終電`: 時刻と帰れなさを圧縮する制度語。
- `表示が消える`: 状況の変化を見せる動作。
- `作業着`: 話者の労働を示す具体物。実話なら根拠が必要。
- `袖`: 身体と物を接続する。
- `画面を拭く`: 諦め、誤読、再確認のいずれにも解釈できる動作。

この段階でも「希望」とは言っていない。後のbarで画面が何だったかを回収すれば、抽象語を使わずに期待と失望を設計できる。
