# 日本語ラップ押韻分類・ライムグラフ拡張仕様

## 目次

1. [目的](#目的)
2. [分類の原則](#分類の原則)
3. [押韻を記述する七つの軸](#押韻を記述する七つの軸)
4. [音素材による分類](#音素材による分類)
5. [長さと語境界による分類](#長さと語境界による分類)
6. [位置による分類](#位置による分類)
7. [反復配置とライムスキーム](#反復配置とライムスキーム)
8. [日本語固有の音韻処理](#日本語固有の音韻処理)
9. [文法・語彙・意味の評価](#文法語彙意味の評価)
10. [押韻と区別して保持する技法](#押韻と区別して保持する技法)
11. [ライムグラフのデータモデル](#ライムグラフのデータモデル)
12. [エッジとスコア](#エッジとスコア)
13. [グラフ指標](#グラフ指標)
14. [語単位・句単位分析スキーマ](#語単位句単位分析スキーマ)
15. [生成時の検索仕様](#生成時の検索仕様)
16. [監査手順](#監査手順)
17. [最小テストセット](#最小テストセット)
18. [根拠と限界](#根拠と限界)

## 目的

「母音が同じ」「行末が同じ」だけで韻を判定しない。日本語ラップの押韻を、
次の三層へ分け、再現可能なデータとして保存する。

1. **音韻層**: 何の音が、どれだけ、どの発音条件で対応するか。
2. **配置層**: 小節、拍、句、語境界をまたいで、どのような網を作るか。
3. **言語・機能層**: 韻が意味、語順、人物像、笑い、フロウに何をしているか。

一つの韻対に一つだけ分類名を付けない。たとえば同じ対が
`internal + multimora + mosaic + delayed + slant`を同時に満たし得る。

## 分類の原則

- 表記でなく、実際に発話される読みを比較する。
- 文字数でなく、モーラ、音節、音素、実演時間を別々に持つ。
- 「完全／不完全」を二値化せず、母音、子音、特殊モーラ、長さを分解する。
- 改行を小節末と決めつけない。bar/beat情報がなければ位置は`unknown`にする。
- 意味類似、反復、ダジャレ、リズム一致は韻に関係し得るが、韻そのものと混同しない。
- 同一語、同一lemma、助詞、助動詞、活用語尾の一致には独立した減点を付ける。
- 発音変形を仮定するたび、変形の種類、根拠、信頼度を残す。
- 音声がない分析では、アクセント、無声化、伸長、着地拍を確定しない。
- 高密度を高品質の同義語にしない。意味と発話可能性に下限を置く。

## 押韻を記述する七つの軸

| 軸 | 問い | 主要フィールド |
|---|---|---|
| 音素材 | どの音が対応するか | `nucleus`, `onset`, `coda`, `NQR`, `phonetic_distance` |
| 長さ | 何モーラ・何語に及ぶか | `mora_count`, `syllable_count`, `token_count` |
| 位置 | 行・小節・拍のどこか | `bar`, `beat`, `subdivision`, `phrase_position` |
| 配置 | 反復がどんな網を作るか | `scheme`, `family_id`, `edge_sequence` |
| 文法 | 内容語か語尾か | `POS`, `lemma`, `inflection`, `suffix_load` |
| 実演 | どう聞こえるようにしたか | `duration`, `prominence`, `pitch`, `devoicing`, `microtiming` |
| 意味・機能 | なぜその韻が必要か | `semantic_fit`, `rhetorical_job`, `humor_role`, `narrative_job` |

分類ラベルは上記の観測値から導出する。ラベルだけを人手入力して観測値を捨てない。

## 音素材による分類

### 完全韻 `exact_rhyme`

対象spanの母音核、子音、特殊モーラ、順序、モーラ数が、採用した実演発音上で
高い精度で一致する。完全一致でも同一語反復なら創造性は別に低く評価する。

必須条件:

- 採用読みが確定または高信頼。
- 内部の要素脱落を仮定しない。
- 語尾の一部だけでなく、宣言したspan全体を比較する。

### 母音韻・類音 `assonance`

複数の母音核が同順序で対応する。日本語ラップの中核的な探索手段だが、
母音だけを見て全候補を同強度にしない。

記録する差:

- 子音が同じ、類似、遠い。
- N/Q/Rが一致、欠落、置換。
- 音数と着地位置が一致するか。
- 一致母音が連続か、内部gapを含むか。

### 子音韻・類音 `consonance`

語頭に限らず、語中・語末で同一または音声的に近い子音を反復する。川原の
日本語ラップ・コーパス分析は、半韻における子音対応が段階的で、類似した子音ほど
対応しやすいことを示す。したがって子音を完全一致／不一致の二値にしない。

推奨特徴:

- 調音位置 `place`
- 調音方法 `manner`
- 有声性 `voice`
- 鼻音性 `nasal`
- 連続性 `continuant`
- 共鳴性 `sonorant`
- 口蓋性 `palatal`

### 頭韻 `alliteration`

複数の強調語、句、拍頭で語頭子音または語頭モーラを反復する。単に同じ助詞が
連続した場合は数えない。破裂音の連打、摩擦音の持続など、音色機能も記録する。

### 脚韻 `end_rhyme`

行末、小節末、意味句末の一つ以上で対応する。テキストの右端ではなく、実演上の
着地点を使う。行末助動詞だけが一致する場合は`grammar_tail_only=true`にする。

### 近似韻・半韻 `slant_rhyme`

一部の母音、子音、特殊モーラ、長さが近いが完全ではない対応。近似の理由を
次のサブラベルで明示する。

- `vowel_near`: 母音音質が近い。
- `consonant_near`: 子音特徴が近い。
- `length_near`: モーラ数が±1。
- `NQR_mismatch`: 撥音、促音、長音の差。
- `delivery_assisted`: 伸長、縮約、無声化等の実演で近づく。
- `boundary_assisted`: 前後語を含めると近づく。

### 同音韻 `homophonic_rhyme`

異なる語・意味が同音またはほぼ同音になる。掛詞や意味反転と併用しやすい。
同音異義語の対応と、同じ語の反復を分離する。

### 押韻的反復 `identity_rhyme`

同じsurfaceまたはlemmaを再使用する。フック、意味更新、人物切替に有効だが、
韻語彙の新規性としては加点しない。反復ごとの意味・声色・音価が変わる場合のみ、
別の修辞価値を付ける。

### 逆向き・部分反転 `reordered_sound_play`

音の部分列を入れ替える、逆順に近づける、子音と母音の役割を交換するなどの
語音遊戯。通常の韻エッジとは別の`phonological_wordplay`エッジにする。
厳密な回文でないものを回文と呼ばない。

### 多言語韻 `cross_language_rhyme`

日本語化した外来語、アルファベット読み、原語寄り発音、方言発音の間を接続する。
言語spanごとに発音系を保持し、日本語カナ読みへ一律変換しない。

## 長さと語境界による分類

### 一モーラ韻 `single_mora_match`

偶然一致率が高いため、通常は弱いテクスチャとして扱う。強拍反復、密集配置、
子音一致等が重なる場合のみ知覚的価値を上げる。

### 多モーラ韻 `multimora_rhyme`

2モーラ以上の順序対応。長いほど自動的に良いとはしない。5モーラ一致でも
同じ定型句なら新規性は低い。

### 多音節韻 `multisyllabic_rhyme`

音節構造をまたぐ対応。日本語の「多文字韻」と同義にしない。
モーラ数と音節数を別々に保存する。

### 句韻・フレーズ韻 `phrase_rhyme`

一つ以上の文節または意味句が対応する。自然な構文のまま長い音列を作れるかを
評価する。単に助詞を大量に含めて長さを稼がない。

### モザイク韻 `mosaic_rhyme`

一語対複数語、複数語対一語、異なる語境界どうしで音列が対応する。
`token_boundary_signature`を比較して、境界が異なることを明示する。

### 分割韻 `split_rhyme`

一つの韻spanが休符、句切れ、小節線で分割される。実演で連結して聞こえる場合と、
意図的に断片化して回収する場合を区別する。

### 全句同音型 `holorhyme_like`

句全体が別の語列とほぼ同音になる稀な型。完全性を誇張せず、内部の不一致と
発音操作量を表示する。

## 位置による分類

| ラベル | 定義 | 監査上の注意 |
|---|---|---|
| `initial_rhyme` | 句・小節・行の開始付近 | 頭韻と同時成立し得る |
| `internal_rhyme` | 同一行・小節内の複数位置 | 行末韻と別familyでもよい |
| `medial_rhyme` | 意味句の中央着地 | 句読点だけで確定しない |
| `end_rhyme` | 行・小節・意味句末 | 文法語尾依存を検査 |
| `cross_bar_rhyme` | 前小節末と次小節内／末が対応 | 改行跨ぎだけを指さない |
| `bridge_rhyme` | 小節線をまたぐ一つのspan | split/phraseとの併記可 |
| `enjambed_rhyme` | 文の完結を次行へ送り、対応を作る | 統語と呼吸を別に保存 |
| `delayed_rhyme` | 期待した直後でなく、後の拍・行で回収 | delay量を拍・小節で持つ |
| `echo_rhyme` | 前の語尾・句を短く反響させる | ad-lib反復と区別 |
| `hook_anchor` | フックの同一位置へ繰り返し着地 | 同語反復でも機能価値あり |
| `offbeat_landing` | 弱拍・裏拍に韻の知覚中心が来る | 音声・グリッドなしでは未確定 |
| `strong_beat_landing` | 強拍に知覚中心が来る | 強調の実演も必要 |

## 反復配置とライムスキーム

### 基本スキーム

- `couplet`: A A
- `alternate`: A B A B
- `enclosed`: A B B A
- `monorhyme`: A A A A
- `paired`: A A B B
- `return`: A B C A
- `unrhymed_break`: A A X A

`X`は失敗でなく、意味転換やパンチライン前の音響的空白として機能し得る。

### 連鎖韻 `chain_rhyme`

AとB、BとCが接続し、AとCは弱い場合も含む。全候補を一つの固定anchorへだけ
比較しない。音形の漸進変化を`rhyme_drift`として記録する。

### 重層韻 `layered_rhyme`

同じ小節群で、行末family A、内部family B、頭韻family Cが同時進行する。
一つのscheme文字列に潰さず、layerごとの系列を保存する。

### 交差韻 `crossed_rhyme`

二つ以上のfamilyが、位置を入れ替えながら交差する。例:
`A(internal)-B(end) / B(internal)-A(end)`。

### 入れ子韻 `nested_rhyme`

長い韻spanの内部に、別の短い韻familyが埋め込まれる。重複カウントを避けるため、
親子関係`contains`を張る。

### リレー韻 `relay_rhyme`

マイクリレーで前話者の音列、語、意味を次話者が引き継ぐ。音の継承と意味の継承を
別エッジにする。梅田サイファー型の多人数曲を分析する際に重要。

### 変形回収 `transformed_callback`

以前のfamilyを、長さ、母音、アクセント、語境界の一つ以上を変えて再登場させる。
単なる反復でなく、変化量と回収距離を記録する。

### 韻スイッチ `family_switch`

支配的familyを切り替える地点。切替前後の理由を
`section_change | emotion_change | flow_change | punch_setup | speaker_change`
から選ぶ。

### 多重韻

用語が「長い韻」「複数family」「複数回踏む」のいずれにも使われるため、
内部ラベルとして使わない。必ず次へ言い換える。

- spanが長い → `multimora` / `multisyllabic`
- familyが並行 → `layered`
- 反復回数が多い → `dense_chain`
- 一語内に複数対応 → `nested`

## 日本語固有の音韻処理

### 特殊モーラ

- 撥音`N`、促音`Q`、長音`R`を独立タイミング単位として保持する。
- `strict_mora`では位置と有無を強く評価する。
- `nucleus_only`では母音核を中心にするが、N/Q/R差を表示する。
- `Q`を無音、`R`を単純重複文字として消去しない。

### 拗音・外来語音

キャ、ティ、ファ等は最長一致で一つの自立モーラとして解析する。小書き文字を
独立モーラにしない。ヴァ行等の実現揺れは複数候補にする。

### 長母音・連母音

`えい→えー`、`おう→おー`を常時変換しない。辞書形、通常発音、テイク固有発音を
併存させる。長音化でのみ一致する韻は`delivery_assisted`とする。

### 母音無声化

/i, u/を基底列から削除せず、無声化候補を追加する。無声化を仮定したときのみ
成立する場合、`devoicing_dependency`を上げる。地域、速度、強調、語境界で
実現が変わるため、音声なしで確定しない。

### 縮約・口語化

「している→してる」等は、元形、縮約規則、実演指定を保存する。韻のためだけに
不自然な縮約を作らない。

### ピッチアクセントと知覚的強調

語彙アクセント型、句の音高、声量、音価、拍位置を分離する。アクセント一致は
韻の知覚を助け得るが、音素対応なしに韻成立とはしない。

## 文法・語彙・意味の評価

### 文法接尾辞ペナルティ

次の一致率を計算する。

```text
suffix_load =
  matched_morae_from_particles_auxiliaries_inflections
  / all_matched_morae
```

推奨警告:

- `suffix_load >= 0.75`: `grammar_tail_dominant`
- 内容語の一致が0モーラ: `grammar_tail_only`
- 4回以上同一助動詞で着地: `repetitive_inflection`

日本語として必要な助詞を罰するのではない。「韻の発明」を語尾が代行している
場合に、創造性スコアだけを下げる。

### 語彙新鮮度

次を別々に評価する。

- corpus頻度
- 同一曲内の出現回数
- 同じlemma・語幹・接辞の再利用
- 同じ意味領域の過密
- 固有名詞の一般性と文脈必然性
- 既成句、広告句、ネット定型句への近さ

珍しい語ほど良いとはしない。`freshness`と`comprehensibility`を両立させる。

### 意味適合

- `local_coherence`: 直前・直後との意味接続
- `theme_fit`: 曲の主題への寄与
- `persona_fit`: 話者が言いそうか
- `image_specificity`: 観察可能な像を作るか
- `semantic_distance`: 韻語同士の意味距離
- `surprise`: 予測からのずれ

「韻の飛距離」は`semantic_distance`を高くしながら、`local_coherence`と
`theme_fit`を下げないPareto条件として扱う。

### 意味を壊す兆候

- 係り受けが韻のためだけにねじれる。
- 不自然な体言止めが連続する。
- 抽象漢語を名詞列として積む。
- 固有名詞が文脈なしに並ぶ。
- 比喩のsource/targetが途中で入れ替わる。
- 因果関係より韻候補が先に進行を決めている。

## 押韻と区別して保持する技法

| 技法 | 韻との関係 | 別フィールド |
|---|---|---|
| 掛詞・同音異義 | 同音韻と共存 | `wordplay.polysemy` |
| ダジャレ | 音近似を利用 | `humor.pun` |
| 畳語・反復 | 音を反復 | `repetition.function` |
| 擬音・擬態語 | 音色とリズム | `sound_symbolism` |
| 頭字語・綴り遊び | 表記依存もある | `orthographic_wordplay` |
| 意味並行 | 音一致なしでも成立 | `semantic_parallelism` |
| 構文反復 | 同じ文型の反復 | `syntactic_parallelism` |
| アナフォラ | 句頭反復 | `repetition.anaphora` |
| エピフォラ | 句末反復 | `repetition.epiphora` |
| パンチライン | setup/payoff機能 | `rhetoric.punchline` |
| コールバック | 遠隔回収 | `narrative.callback` |

## ライムグラフのデータモデル

### グラフ単位

単一グラフへ全情報を押し込まず、次の多層グラフを使う。

1. `token_layer`: 表層語・形態素。
2. `span_layer`: 実際に比較する音列。
3. `occurrence_layer`: 曲中の位置・実演。
4. `family_layer`: 韻familyとscheme。
5. `semantic_layer`: 意味領域、イメージ、修辞機能。

### Token node

```json
{
  "id": "tok-b03-07",
  "surface": "値引きシール",
  "normalized": "値引きシール",
  "reading": "ネビキシール",
  "reading_source": "manual",
  "reading_confidence": 1.0,
  "mora": ["ne", "bi", "ki", "shi", "R", "ru"],
  "vowels": ["e", "i", "i", "i", "i", "u"],
  "onsets": ["n", "b", "k", "sh", null, "r"],
  "pos": "NOUN",
  "lemma": "値引きシール",
  "sense": "値下げを示す店舗の貼付物",
  "semantic_domain": ["shopping", "poverty_detail", "daily_object"],
  "register": "colloquial_neutral",
  "named_entity": false,
  "frequency_band": "medium",
  "freshness": 0.68
}
```

### Span node

```json
{
  "id": "span-b03-a",
  "token_ids": ["tok-b03-07"],
  "source_char_span": [12, 18],
  "performed_reading": "ネビキシール",
  "mora_start": 0,
  "mora_end": 6,
  "mora_count": 6,
  "syllable_count": 5,
  "token_boundary_signature": [6],
  "phonology_variant": "base",
  "variant_cost": 0.0
}
```

### Occurrence node

```json
{
  "id": "occ-v1-b03-a",
  "span_id": "span-b03-a",
  "section": "verse_1",
  "bar": 3,
  "beat_start": 2.5,
  "beat_end": 4.0,
  "subdivision": "sixteenth",
  "phrase_position": "internal",
  "prominence": "high",
  "duration_beats": 1.5,
  "microtiming": "unknown",
  "breath_group": "bg-04",
  "speaker": "narrator",
  "audio_verified": false
}
```

### Family node

```json
{
  "id": "fam-A",
  "prototype_vowels": ["e", "i", "i", "i", "u"],
  "prototype_special": ["R"],
  "member_occurrences": ["occ-v1-b03-a", "occ-v1-b04-b"],
  "family_type": ["multimora", "internal", "slant"],
  "section_role": "momentum",
  "confidence": 0.81
}
```

### Provenance

全node/edgeに、必要に応じて次を付ける。

```yaml
provenance:
  source_type: user_supplied_lyrics | licensed_transcript | manual_audio_annotation | g2p
  source_uri: null
  annotator: human | model | script
  timestamp:
  confidence:
  copyright_scope: private_analysis | redistributable
```

## エッジとスコア

### エッジ種別

- `RHYMES_WITH`: 総合的な韻対応。
- `ASSONATES_WITH`: 母音対応。
- `CONSONATES_WITH`: 子音対応。
- `ALLITERATES_WITH`: 語頭対応。
- `REPEATS`: surface/lemma反復。
- `MORPH_VARIANT_OF`: 活用・派生関係。
- `PERFORMED_VARIANT_OF`: 縮約、伸長、無声化等。
- `CONTAINS`: nested span。
- `BRIDGES`: 小節線をまたぐ。
- `CALLS_BACK_TO`: 遠隔回収。
- `SEMANTICALLY_RELATES`: 同一／近接意味領域。
- `SEMANTICALLY_CONTRASTS`: 反義・意外な距離。
- `SETS_UP` / `PAYS_OFF`: パンチライン構造。
- `SPEAKER_HANDOFF`: マイクリレー。

### Rhyme edge

```json
{
  "source": "occ-v1-b03-a",
  "target": "occ-v1-b04-b",
  "type": "RHYMES_WITH",
  "labels": ["internal", "multimora", "mosaic", "slant"],
  "alignment": [
    {"a":"e","b":"e","kind":"exact"},
    {"a":"i","b":"i","kind":"exact"},
    {"a":"R","b":"i","kind":"NQR_mismatch"},
    {"a":"u","b":"u","kind":"exact"}
  ],
  "nucleus_match": 0.91,
  "onset_similarity": 0.58,
  "special_mora_match": 0.50,
  "span_length_score": 0.82,
  "position_salience": 0.74,
  "prosody_fit": null,
  "semantic_fit": 0.86,
  "naturalness": 0.92,
  "novelty": 0.71,
  "grammar_tail_penalty": 0.0,
  "duplicate_penalty": 0.0,
  "pronunciation_confidence": 1.0,
  "audio_verified": false
}
```

### スコア方針

```text
sound = f(nucleus, onset, NQR, span_length, alignment_cost)
placement = f(position_salience, repetition_distance, scheme_role)
language = f(naturalness, semantic_fit, persona_fit)
invention = f(novelty, semantic_distance, boundary_difference)
penalty = grammar_tail + duplicate + forced_syntax + pronunciation_risk
```

単一`final_score`で候補を並べる前に、多目的のPareto frontを返す。
音が最も近い候補、意味が最も適切な候補、意外性が高い候補を分ける。

## グラフ指標

### 網羅性

- `rhyme_coverage`: 内容語モーラのうち韻edgeに含まれる割合。
- `salient_coverage`: 強調位置のうち韻edgeを持つ割合。
- `bar_coverage`: 少なくとも一つの韻役割を持つ小節割合。

### 偏り

- `end_bias`: 全韻occurrenceのうち行末・小節末のみの割合。
- `suffix_dependency`: 一致モーラに占める助詞・助動詞・活用語尾割合。
- `family_dominance`: 最大familyが全韻occurrenceを占める割合。
- `vowel_sequence_reuse`: 同一母音列の過剰再利用。
- `named_entity_load`: 韻候補に占める固有名詞割合。

### 多様性

- `position_entropy`: internal/end/initial/cross-bar等の分布エントロピー。
- `family_entropy`: family利用の分散。
- `span_length_variance`: 韻span長の変化。
- `boundary_diversity`: 一語、句、mosaicの分布。
- `technique_diversity`: 音・位置・配置ラベルの種類。

### 構造

- connected components数
- familyごとの密度
- hub occurrence
- average回収距離
- chainの最長長
- family switch地点
- speaker間edge数
- setup/payoff edgeの閉路未完了数

### 品質リスク

- `forced_syntax_rate`
- `low_confidence_reading_rate`
- `devoicing_dependency_rate`
- `one_mora_edge_rate`
- `duplicate_edge_rate`
- `semantic_orphan_rate`
- `audio_unknown_rate`

## 語単位・句単位分析スキーマ

ユーザーが権利を持つ歌詞、本人提供テキスト、ライセンス済みコーパスを分析する場合の
最小スキーマ:

```yaml
surface: ""
normalized: ""
reading: ""
reading_variants: []
mora: []
mora_count: 0
syllable_count: 0
POS: ""
lemma: ""
inflection: ""
sense: ""
sense_confidence: 0.0
semantic_domain: []
concreteness: 0.0
imageability: 0.0
register: ""
dialect: ""
named_entity:
frequency_band:
freshness:
syntax_role:
dependency_head:
phrase_id:
bar:
beat_start:
beat_end:
prominence:
rhyme_role: []
rhyme_family_ids: []
humor_role: []
rhetorical_role: []
narrative_role:
speaker:
pronunciation_source:
audio_verified:
notes:
```

### `rhyme_role`の許容値

```text
anchor | response | bridge | internal_texture | end_landing |
chain_link | delayed_payoff | family_switch | hook_anchor |
alliterative_texture | consonant_texture | identity_refrain
```

### `humor_role`の許容値

```text
setup | misdirection | incongruity | escalation | deadpan_marker |
self_deprecation_target | status_reversal | callback | punch |
proper_noun_collision | taboo_reframing | character_mismatch
```

## 生成時の検索仕様

候補nodeには最低限、次を持たせる。

- 母音列
- 子音特徴
- N/Q/R列
- モーラ数
- 通常アクセント候補
- POSと活用
- lemma
- sense
- 意味領域
- 使用頻度
- 新鮮度
- 固有名詞判定
- 前後に置きやすい助詞
- registerとdialect
- 完全韻／近似韻の条件
- 発音信頼度

検索は次の順で広げる。

1. 同じ意味役割・自然なPOSで、完全な母音/NQR suffixを探す。
2. 子音類似、長さ±1、語境界変更へ広げる。
3. フレーズ組立でmosaic候補を作る。
4. 近似母音、実演依存候補へ広げる。
5. 最後にのみ固有名詞・低頻度語へ広げる。

候補を採用する前に、韻を外した文として読んでも意味が通るか確認する。

## 監査手順

1. 原文、読み、モーラ、語境界を保存する。
2. bar/beatが不明なら、テキスト位置と実演位置を分離する。
3. 2〜8モーラwindowを列挙し、重複spanを統合する。
4. 母音、子音、N/Q/Rを別採点する。
5. positionとschemeを付ける。
6. 同一語、lemma、語尾、助詞列を検出する。
7. 意味、自然さ、人物像への適合を別採点する。
8. family graphを作り、末尾偏重、family偏重、孤立を測る。
9. 音声があれば着地、伸長、無声化、アクセントを更新する。
10. 最後に、人間が「意味を壊していないか」「口に乗るか」を確認する。

### 強制修正ゲート

- 主要韻の75%以上が文法語尾のみ。
- 全ての主要韻が末尾だけで、技術密度指定が中以上。
- 読み不明語が主要familyのanchor。
- 同一語反復を別韻として水増し。
- 韻を外すと文の意味が崩れる。
- 固有名詞が意味上の役割なしに3つ以上連続。
- 音声なしで無声化・アクセント・ポケットを断定。

## 最小テストセット

| テスト | 期待 |
|---|---|
| 3母音一致、子音不一致 | assonance、slant、子音低得点 |
| 母音と子音とN/R一致 | exact候補 |
| 同一助動詞のみ4回 | grammar_tail_dominant |
| 一語対二語 | mosaic |
| 前小節末対次小節内部 | cross_bar |
| A-B、B-C強、A-C弱 | chainとして同component |
| 同じ語を意味更新なしで反復 | identity、novelty低 |
| 同じ語を人物別の意味で反復 | identity + rhetorical value |
| 無声化時のみ成立 | delivery_assisted + warning |
| えい→えー時のみ成立 | long_vowel_variant + warning |
| 小書きャを独立カウント | parser failure |
| 英語原音とカナ読みが混在 | language-span分離 |
| 行末韻0、内部韻多数 | end_bias低、coverage高 |
| 音一致なしの反義語 | semantic contrastのみ、rhymeなし |

## 根拠と限界

### 音韻・日本語ラップ

- Shigeto Kawahara, “Half Rhymes in Japanese Rap Lyrics and Knowledge of Similarity”
  は、日本語ラップの子音対応を98曲・20,224対応から分析し、子音類似度を
  段階評価する根拠を与える。
  <https://user.keio.ac.jp/~kawahara/pdf/JEAL16_kawahara.pdf>
- Kawaharaの概説は、日本語ラップの韻、母音対応、ピッチの知覚的役割を整理する。
  <https://user.keio.ac.jp/~kawahara/pdf/rap2017.pdf>
- Natsuko Tsujimura and Stuart Davis, “Dragon Ash and the Reconsideration of
  Japanese Rhyme” は、日本語ラップの韻単位を英語の綴りや単純な音節観へ
  還元しないための比較資料である。
  <https://cl.indiana.edu/davis/TsujimuraDavisDragonAsh2009.pdf>
- Haruo Kubozono, “Moras and Syllables” はモーラと音節を分ける基礎資料。
  <https://www.cambridge.org/core/books/cambridge-handbook-of-japanese-linguistics/moras-and-syllables/F9213E649E5536ACE32E209AE7E11185>

### フロウと配置

- Kyle Adamsは、ラップのアクセント、句の配置、拍節との関係を分析する。日本語へ
  移植するときは語彙強勢をそのまま使わず、モーラonset、音価、音高、声量へ分解する。
  <https://www.mtosmt.org/issues/mto.09.15.5/mto.09.15.5.adams.html>
- Mitchell Ohrinerは、16分音符グリッドと拍節曖昧性を使ったフロウ分析例を示す。
  <https://mtosmt.org/issues/mto.19.25.1/mto.19.25.1.ohriner.html>
- Ben Duinkerは、ラップの表情的タイミングを単なるグリッド誤差でなく、
  機能を持つ実演として扱う。
  <https://online.ucpress.edu/jpms/article-abstract/34/1/90/120447/Functions-of-Expressive-Timing-in-Hip-Hop-Flow>

### 限界

- 上記研究は、全時代、全地域、全ラッパーの美的基準を決めるものではない。
- 歌詞テキストだけでは、ポケット、伸長、アクセント、無声化を確定できない。
- 分類数を増やしても、面白さ、説得力、声の魅力は自動的に保証されない。
- スコアの重みは初期値にすぎず、ユーザー評価と録音比較で校正する。
