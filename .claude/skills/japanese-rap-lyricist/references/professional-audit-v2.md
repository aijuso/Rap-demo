# Professional Audit v2

生成後の歌詞を、韻密度や見た目の整い方に引きずられず、意味、声、具体性、韻、flow、ユーモア、構造、独創性、実演可能性に分けて厳しく監査する。点数より hard gate を先に適用する。

## 目次

- 監査の独立性
- 入出力
- 監査順序
- Hard gates
- 行・小節・セクション分析
- 韻監査
- ユーモア監査
- 語彙監査
- Flow監査
- 構造監査
- AI臭監査
- 固有名詞監査
- 100点rubric
- 証拠の書き方
- 修復優先順位
- 再監査
- 監査出力schema

## 監査の独立性

- Draft Integrator と別のエージェントが監査する。
- 監査者へ作者の期待スコア、自己弁護、採用理由を渡さない。
- 参照アーティスト名を評価基準にしない。
- 「難しい韻」「語彙が多い」「長い行」を自動的に高評価しない。
- まず欠陥を探し、次に機能している証拠を探す。
- 録音がなければ performance と pocket を満点にしない。
- 一度付けた点数に合わせて観察を後付けしない。

同一エージェントしか使えない場合は、初稿の生成理由を閉じ、rubricとbriefだけを読み直す。その場合 `audit_independence: partial` とする。

## 入出力

### 入力

- 凍結した `brief.yaml`
- ID付きの対象draft
- `narrative_plan.yaml`
- `vocabulary_bank.json`
- `rhyme_graph.json`
- `flow_map.yaml`
- 必要時のみユーザー提供原文

監査に不要なreference artistの名前、別候補の優劣、生成ログは渡さない。

### 出力

- `audit_report.yaml`
- 問題ID付きの所見
- hard gate結果
- category score
- 修復優先順位
- 残存する未検証項目

## 監査順序

1. brief、話者、事実境界を確認する。`checkpoint_log` とユーザー返答の引用を照合し、
   G8（プロセス証拠）を先に判定する。
2. originality、意味、自然な日本語、安全のhard gateを適用する。
3. 1行ごとに意味を平易に言い換える。
4. 2小節または4小節ごとの新情報、感情、flow変化を記録する。
5. 韻、ユーモア、語彙、flowを別々に監査する。
6. 音読または録音で発話を検証する。
7. category scoreを付ける。
8. 最も影響の大きい問題を最大5件へ絞る。
9. Repair Ownerへ、修正条件と壊してはいけない部分を渡す。
10. 改訂後は別コンテキストで同じ順序を再実行する。

## Hard gates

### G1 著作権・模倣

失敗条件:

- 公開曲の特徴的な語句、希少比喩、場面順、韻語、オチがまとまって残る。
- 特定人物の決め台詞、アドリブ、経歴を移植する。
- 名前だけ置換して構文と展開を残す。
- 本人作、未発表曲、本人の発言と誤認させる。

`FAIL` は0点。疑わしいが確認できない場合は `HOLD` とし、49点を上限にする。

### G2 意味の完全性

失敗条件:

- 中心となる2行以上を、作者の説明なしに平易に言い換えられない。
- 韻のために主語、目的語、時制、因果、指示対象が変わる。
- 比喩の対応関係が途中で崩れる。
- パンチラインのturnとsetupの共通項がない。

失敗時は39点を上限にする。

### G3 自然な日本語

失敗条件:

- 不自然な倒置、助詞抜け、助詞誤用が反復する。
- 韻のためだけに語域や敬語が飛ぶ。
- 書字上だけ成立し、想定読みでは意味が失われる。
- 長い名詞列が係り受け不明になる。

失敗時は49点を上限にする。

### G4 Brief・話者・事実

失敗条件:

- 指定テーマ、形式、禁止語、話者を外す。
- ユーザー未提供の経歴、貧困、犯罪、病気、方言を実話として足す。
- 話者が知り得ない情報を説明なく断定する。
- 視点または呼びかけ相手が偶発的に変わる。

失敗時は39点を上限にする。

### G5 最低限の曲機能

失敗条件:

- 大半の行が交換可能な自己肯定、勝利、努力、批判である。
- 韻候補一覧を文に並べただけである。
- セクションの役割、反復の意味、またはenergy contourがない。
- 韻を外すと文章として何も残らない。

失敗時は29点を上限にする。

### G6 実演可能性

失敗条件:

- 目標BPMで2回試しても、重要語を潰さず発話できない。
- 呼吸位置が意味単位を繰り返し切る。
- 長音、促音、撥音、英語部が想定gridと矛盾する。
- punchline前の空白が実演上存在しない。

録音で失敗した場合は49点を上限にする。録音またはbeatがなければ `UNVERIFIED` とし、総合84点を上限にする。

### G7 安全・名誉

失敗条件:

- 実在人物の犯罪、私生活、能力を根拠なく断定する。
- 差別、脅迫、嫌がらせをbriefの範囲を超えて追加する。
- 架空表現を実在の事実として見せる。

削除または明確なfiction化まで0点とする。

### G8 プロセス証拠（checkpoint evidence）

チェックポイントはユーザーの舵取りの権利であり、仮定の丁寧な記録では代替できない。

失敗条件:

- `interaction_mode` が `collaborative`（または未記録）なのに、CP1〜CP4 のそれぞれについて
  ユーザーの実際の返答の逐語引用が `checkpoint_log` にない。
- `autonomous` を主張しているが、ユーザー自身の明示的な委任発言の逐語引用がない。
  環境が自律実行前提であることは委任の根拠にならない。
- 最初のユーザー回答と同一ターンで完成稿が納品されている。
- CP1 が1ラウンドの一括質問（3問まとめ等）だけで凍結されており、ユーザーの依頼が
  最初から全必須項目を満たしていたわけでもない。

`FAIL` は49点を上限にする。`create` / `rewrite` の監査では audit-evidence の
`interaction` ブロックを必須とし、欠落は unknowns に記録して conditional_pass 止まりにする。

## 行・小節・セクション分析

### 1行ごとの分解

各行へ次を記録する。

```yaml
bar_id: B01
plain_paraphrase: ""
speaker_action: ""
referents:
  pronouns: {}
  proper_nouns: {}
new_information: ""
emotion: ""
observable_detail: ""
syntax:
  subject: ""
  predicate: ""
  objects: []
  omitted_elements: []
  naturalness: 0
sound:
  rhyme_events: []
  alliteration: []
  prominence_words: []
flow:
  estimated_morae: 0
  entry: unknown
  rests: []
craft:
  setup_ids: []
  payoff_ids: []
  humor_ids: []
  narrative_function: ""
indispensability: 0
problems: []
```

`plain_paraphrase` が原行より長くなり続ける場合、圧縮ではなく曖昧化の可能性がある。

### 2小節・4小節単位

各unitで次を比較する。

- 新しい情報
- 感情の変化
- 画角または時間の変化
- flowの変化
- 韻familyの変化
- setup、payoff、callback
- 次unitへ残す問い

4小節ごとに `情報、感情、flow` の全てが不変なら停滞候補にする。ただしgroove-firstの意図的反復は、音価、声色、語の置換、蓄積効果の証拠があれば許容する。

## 韻監査

### 全rhyme eventを分類する

最低限、次を分ける。

- 行末韻
- 内部韻
- 行頭・頭韻
- 句中の母音韻
- 子音韻
- 複数モーラ韻
- phrase/mosaic rhyme
- split rhyme
- cross-bar rhyme
- delayed rhyme
- overlapping rhyme
- chain/monorhyme
- exact rhyme
- slant/half rhyme
- performative variant
- 同一語反復
- 文法語尾だけの一致

### 各eventの採点

```text
audibility       0-2
meaning          0-2
naturalness      0-2
placement        0-2
freshness        0-2
```

意味または自然さが0なら、合計が高くても修復対象にする。

### 必須診断

```text
end-rhyme bias =
  end-position rhyme events
  / all rhyme events

family reuse =
  events in most-used vowel family
  / all rhyme events

grammar-only ratio =
  grammatical ending-only events
  / all rhyme events

meaningful rhyme ratio =
  events with meaning >= 1 and naturalness >= 1
  / all rhyme events
```

診断値に普遍的な合格線は置かない。ただし次を警告する。

- end-rhyme biasが高く、内部またはcross-bar設計がない。
- 同一母音列を4回以上連続使用し、意味も配置も変わらない。
- 行末が `〜してる、〜になる、〜じゃない` の反復で支えられる。
- 同一語反復を別韻として水増しする。
- 漢字表記は似るが、実演読みが一致しない。
- 読みを不自然に歪めないと成立しない。
- 韻語を外すと文の意図が消える。

### 音読検証

- 実際の発音で母音長を確認する。
- 無声化して聞こえにくい母音を紙面通りに数えない。
- 長音、促音、撥音、拗音をモーラとして扱う。
- 英単語、略語、固有名詞は話者の実演読みを優先する。
- 重要韻が子音の衝突や早口で聞こえない場合、存在していてもaudibilityを下げる。

## ユーモア監査

### 種類

- 自虐
- 誇張
- デッドパン
- 社会風刺
- 下品な題材の知的表現
- 固有名詞の意外な接続
- 前振りと回収
- キャラクター同士の認識のズレ
- シリアスな文脈への異物混入
- callback
- rule of three
- bathos
- 語域衝突
- anti-joke
- misdirection
- double meaning

### 各humor eventの監査

```yaml
humor_id: H01
type: ""
setup_present: true
predicted_frame: ""
violated_expectation: ""
shared_bridge: ""
landing_word: ""
timing_support: ""
character_revelation: ""
meaning_without_joke: ""
risk:
  cruelty: 0
  obscurity: 0
  randomness: 0
  tonal_damage: 0
score:
  legibility: 0
  surprise: 0
  economy: 0
  voice_fit: 0
  structural_value: 0
```

### 失敗パターン

- setupがないため、単に変な単語が出ただけ。
- 固有名詞の知名度だけに依存する。
- 下品な語を置いただけで、二重意味、語域差、構造がない。
- 自虐が話者の同じ欠点を繰り返すだけ。
- 比喩の接続が遠すぎて説明が必要。
- punchlineを解説する次の行がある。
- 笑いが物語上の損失や真剣な感情を無効化する。
- すべて同じ声色で、pauseまたはlandingの設計がない。
- 前振りと回収の間に、覚えておくべき目印がない。

笑いがなくてもbrief上不要なら減点しない。ユーモア指定がある場合も、イベント数より種類、配置、キャラクター機能を評価する。

## 語彙監査

### 必須質問

- 抽象語が続いていないか。
- 具体物は場面を見せるか、単なる名詞羅列か。
- 動詞が実際の行動を示すか。
- 形容詞が証拠を説明し直しているだけではないか。
- 同じ意味を別語で繰り返していないか。
- 語のliteral senseとcontextual senseがつながるか。
- 話者がその専門語、ブランド、制度語を使う理由があるか。
- 固有名詞を外しても行の意味が残るか。
- 珍語が韻のためだけに選ばれていないか。
- 4小節ごとに少なくとも1つ、観察可能な情報があるか。

### 診断

- longest abstract run
- concrete scene coverage
- content-word repetition
- semantic-domain diversity
- unsupported-specificity count
- cliché cluster count

AIが好む抽象クラスターの例として `未来、運命、覚悟、証明、世界、光、闇、壁、自分` が近接する場合、語そのものを禁止せず、具体的な根拠と固有の関係があるか確認する。

## Flow監査

### テキスト監査

- 各barの概算モーラ数
- 2/4小節単位の密度contour
- pickup、強拍、休符、引き伸ばし
- 文節境界とbar境界
- 早口区間の子音衝突
- breath候補
- 同型リズムの反復回数
- flow switchの物語上の理由
- punchline直前の空白
- 声色または人物の切り替え

### 実演監査

1. 普通の速度で意味を保って読む。
2. metronomeまたはbeatで2回録る。
3. 重要語が聞こえるか確認する。
4. breathで助詞と述語が切れないか確認する。
5. 休符が空白ではなく期待を作るか確認する。
6. fast zone前後で密度差が聞こえるか確認する。
7. 同一patternが意図した回数だけ認識できるか確認する。

録音なしに「耳が気持ちいい」「完全にハマる」と断定しない。

## 構造監査

- hookの約束をverseが証明、反証、複雑化しているか。
- 前半で置いた物、会話、傷が後半で別の意味を持つか。
- 4小節ごとに情報、感情、flowのいずれかが変わるか。
- すべてのbarが結論を叫び、setupが不足していないか。
- 逆にsetupだけが続き、payoffがないか。
- 最終行が単に最大の韻ではなく、全体の読みを変えるか。
- collage形式なら、並び順にenergy、意味領域、音色の原理があるか。
- hookless形式なら、return motifまたはenergy contourが代替しているか。

## AI臭監査

### 構文

- すべてが「名詞A、名詞B、俺は〜」の同型ではないか。
- 行末が同じ助動詞または断定形へ収束していないか。
- 不自然な体言止めが連続していないか。
- 接続詞が論理を説明しすぎていないか。
- 対句が均整しすぎ、話者の癖が消えていないか。

### 意味

- 具体的な失敗、代償、矛盾がなく、成功だけを一般化していないか。
- 「他人は偽物、自分は本物」を証拠なく繰り返していないか。
- 比喩が `炎、翼、王冠、戦場、光と闇` へ自動収束していないか。
- 各行が同じ強度で、平熱や観察がないか。
- 説明できない造語を高度さと誤認していないか。

### 音

- 末尾韻しかないか。
- 同じ母音familyを過剰再利用していないか。
- 韻候補を列挙するために名詞が孤立していないか。
- 発音ではなく文字面で合わせていないか。
- 韻をマークしただけで声に出すと聞こえないか。

AI臭は一つの語で判定しない。同型反復、意味の薄さ、音の均質化が複数重なったときに問題とする。

## 固有名詞監査

各固有名詞へ次を問う。

1. 何を圧縮しているか。
2. 話者とどう関係するか。
3. setup/payoffまたは二重意味に必要か。
4. 一般名詞へ置換したら何が失われるか。
5. 聞き手に要求する知識量は適切か。
6. 実在人物への事実断定や侮辱になっていないか。
7. 同じ行に複数並べる必要があるか。

`音が合う` しか理由がなければ棄却候補にする。

## 100点rubric

hard gate通過後だけ採点する。

| Category | 点 | 満点の証拠 |
|---|---:|---|
| Brief、話者、事実境界 | 8 | 指定と知識境界が一貫し、捏造がない |
| 意味、因果、行ごとの明瞭さ | 14 | 各行を平易に言い換えられ、因果と指示対象が明確 |
| セクション進行 | 10 | 4小節ごとに情報、感情、flowが意図的に進む |
| 具体語、映像、語彙 | 10 | 物、動作、感覚、制度が場面と感情を同時に運ぶ |
| 韻と音のarchitecture | 15 | 種類、位置、距離が多様で、意味と自然さを壊さない |
| Flow、休符、呼吸 | 13 | 密度contour、強調、休符、breathが実演で機能する |
| ユーモア、surprise、punch | 8 | setup、違反軸、着地が明瞭で、声と構造に貢献 |
| Hookまたはreturn設計 | 7 | 反復が意味を増し、verseとの役割が異なる |
| 自然な日本語と声 | 8 | 語順、助詞、語域、口調が耳で自然 |
| 独創性とrevision evidence | 7 | 模倣を避け、監査と修復の履歴がある |

### anchor

- 90–100: 録音検証済みで、公開前の味調整だけが残る。
- 80–89: 強いdraft。局所修正と録音確認が残る。
- 70–79: 明確な個性と機能があるが、複数層の修復が必要。
- 60–69: demoとして成立するが、filler、停滞、forced rhymeが目立つ。
- 40–59: 局所的な音や行はあるが、意味または構造が未完成。
- 0–39: gate失敗、模倣、意味破綻、brief逸脱、または大半がfiller。

最初のdraftに80点を既定値として与えない。録音なしは84点、revision evidenceなしは93点を上限とする。

## 証拠の書き方

悪い:

```text
韻が多くて気持ちいい。意味も深い。
```

良い:

```text
B03中間の3モーラ近似韻とB04末尾のphrase rhymeが別位置で呼応する。
ただしB04は目的語が欠け、意味の自然さは0/2。B03を保持しB04を再設計する。
```

各categoryに最低1件、bar IDまたはsection ID付きの証拠を置く。高評価と低評価の両方に証拠を要求する。

## 修復優先順位

1. 安全、著作権、捏造、brief違反
2. 意味、主語、因果、話者
3. 自然な日本語
4. 実演不能、breath、重要語の不可聴
5. setup/payoff、セクション進行
6. 抽象語、filler、具体性
7. 韻family、配置、freshness
8. humorのタイミングと種類
9. 表記、注釈、体裁

最大5問題だけRepair Ownerへ渡す。複数の小さな症状が一つの上流原因から生じる場合、上流原因を1件として扱う。

### 修復指示

```yaml
issue_id: A-003
severity: critical | major | minor
bar_ids: [B05, B06]
failed_layer: semantics
evidence: ""
root_cause: "韻語から意味を逆算した"
must_preserve:
  - B05の具体物
must_change:
  - B06の主語と因果
acceptance_test:
  - "B05-B06を一文で自然に言い換えられる"
collateral_checks:
  - rhyme
  - flow
```

修正語を直接指定しすぎず、合格条件を渡す。

## 再監査

- 修復者と異なる監査者を使う。
- 旧スコアを見ず、hard gateから再実行する。
- 修正対象だけでなく、前後2小節の副作用を見る。
- 直した韻で意味が壊れていないか確認する。
- 具体語を足した結果、事実捏造が起きていないか確認する。
- ユーモアを足した結果、感情の重みが消えていないか確認する。
- flow修正でsetup/payoffの距離が変わっていないか確認する。
- `resolved`, `partially_resolved`, `regressed`, `new_issue` を区別する。

同じcritical issueが2周続いた場合、局所修正を止め、Narrative、Vocabulary、Flowの上流artifactを作り直す。3周後もgateを通らなければ、完成扱いせず残存リスクを報告する。

## 監査出力schema

```yaml
schema: professional-audit/v2
run_id: ""
brief_hash: ""
draft_revision: 1
auditor:
  instance_id: ""
  independence: full | partial
verification:
  text_read: true
  spoken_read: false
  recorded_on_beat: false
hard_gates:
  - gate_id: G1   # G1〜G8。G8はプロセス証拠（checkpoint evidence）
    result: pass | fail | hold | unverified
    evidence: []
    score_cap: null
line_analysis: []
unit_analysis: []
diagnostics:
  end_rhyme_bias: null
  dominant_family_reuse: null
  grammar_only_ratio: null
  meaningful_rhyme_ratio: null
  longest_abstract_run: null
  concrete_scene_coverage: null
  unsupported_specificity_count: null
  four_bar_change_coverage: null
scores:
  brief_voice_facts: 0
  semantic_clarity: 0
  section_progression: 0
  concrete_vocabulary: 0
  rhyme_architecture: 0
  flow_breath: 0
  humor_surprise: 0
  hook_return: 0
  natural_japanese: 0
  originality_revision: 0
raw_total: 0
applied_cap: null
final_score: 0
issues:
  - issue_id: A-001
    severity: critical
    bar_ids: []
    failed_layer: ""
    evidence: ""
    root_cause: ""
    must_preserve: []
    must_change: []
    acceptance_test: []
    collateral_checks: []
strengths_to_preserve: []
unverified_claims: []
decision: fail | revise | conditional_pass | pass
```

`pass` はhard gateを全て通過し、重大問題がなく、必要な実演検証が済んだ場合だけ使う。テキストのみなら、優れたdraftでも `conditional_pass` とする。
