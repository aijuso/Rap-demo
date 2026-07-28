# サブエージェント・オーケストレーション契約

この資料は、作詞を一人の生成器による一発出力にせず、独立した専門工程へ分解するための実行契約である。ファイルまたは構造化テキストで受け渡せる `portable core` を正本とし、**Claude Code を第一ホスト**として設計する。Claude Code の Task サブエージェント、並列起動、TodoList、Bash 実行に契約を直接マッピングし、Codex/ChatGPT は互換用の legacy アダプターとして扱う。

## 目次

- 設計原則
- Portable core
- 実行状態
- 依存関係と並列化
- 共通artifact契約
- 役割別契約
- 統合と競合解決
- 独立監査と修復ループ
- 著作権・模倣防止
- 失敗時のfallback
- Claude Code adapter(第一ホスト)
- Codex/ChatGPT adapter(legacy)
- 単一エージェント環境
- 完了条件

## 設計原則

1. `共有brief` を凍結してから専門工程を始める。
2. 事実、推測、提案、未検証を別フィールドで渡す。
3. 各専門家は自分の担当外の最終判断をしない。
4. Draft Integrator は各artifactを読むが、専門家同士の口調を混ぜない。
5. Auditor は初稿の意図や自己採点を見ず、brief、成果物、証拠だけで独立採点する。
6. Repair Owner は問題を隠す全面書き換えを避け、修正理由と影響範囲を記録する。
7. 韻密度、ユーモア量、固有名詞量を品質の代理変数にしない。
8. 実演していないフローは `unverified` とする。
9. 特定アーティスト名は生成条件へ直接渡さず、一般技法へ抽象化する。
10. 商業曲の本文を永続artifactへ保存しない。

## Portable core

### 入力ディレクトリ

ホストを問わず、次の論理artifactを使用する。人間向け表示は JSON または YAML を
使えるが、同梱Pythonスクリプトへ直接渡す入力は標準ライブラリだけで読める JSON
を正本とする。YAMLを使うadapterは、schemaを保ったJSONへ変換してから実行する。

```text
run/
  brief.yaml
  source_policy.yaml
  technique_vector.yaml
  narrative_plan.yaml
  vocabulary_bank.json
  humor_plan.yaml
  rhyme_graph.json
  flow_map.yaml
  draft_candidates.md
  integration_report.yaml
  audit_report.yaml
  repair_report.yaml
  final.md
```

ファイルを使えないホストでは、同名の見出しを持つ fenced block で代用する。artifact名、schema version、producer、status を省略しない。

### 共有brief

```yaml
schema: japanese-rap-brief/v2
run_id: unique-local-id
mode: create | analyze | rewrite | audit | teach
deliverable: hook | verse | full-song | analysis | rhyme-bank
language: ja
theme: ""
core_message: ""
facts_and_images: []
speaker:
  identity: ""
  fictional: true
  point_of_view: first
  knowledge_boundary: []
listener: ""
setting:
  time: ""
  place: ""
tone: []
register: conversational
dialect:
  name: none
  confidence: high
bpm: null
meter: 4/4
bars: null
structure: []
required_words: []
forbidden_words: []
explicitness: clean | moderate | explicit
reference_requests: []
reference_traits: []
copyright_input_class: original_prompt | user_supplied_text | commercial_work
assumptions: []
unknowns: []
```

`reference_requests` は Reference/Technique Analyst だけが読む。以後の役割へは、固有名を除いた `reference_traits` だけを渡す。

### 不変条件

- `run_id` と `brief hash` を全artifactに含める。
- brief変更時は downstream artifactを `stale` にする。
- `status` は `ready | partial | blocked | unverified | stale` のいずれかにする。
- 推測した読み、アクセント、事実は `confidence` と `evidence` を伴わせる。
- セクション、小節、単語のIDは統合後も変えず、修正は revision を上げる。

## 実行状態

```yaml
schema: japanese-rap-orchestration/v1
run_id: ""
brief_hash: ""
revision: 1
stages:
  reference_analysis: pending
  narrative: pending
  vocabulary: pending
  humor: pending
  rhyme: pending
  flow: pending
  integration: pending
  audit: pending
  repair: pending
  reaudit: pending
artifacts: {}
decisions: []
open_risks: []
```

状態遷移は `pending -> running -> ready` を基本とし、証拠不足は `unverified`、続行不能は `blocked` とする。失敗を空のartifactで上書きしない。

## 依存関係と並列化

```text
brief
  |
  +--> Reference/Technique Analyst --+
  |                                  |
  +--> Narrative Architect ----------+----> Draft Integrator
  |                                  |
  +--> Vocabulary Director ----------+
  |                                  |
  +--> Humor Engineer ---------------+
  |                                  |
  +--> Rhyme Graph Engineer ----------+
  |                                  |
  +--> Flow Mapper -------------------+
                                         |
                                         v
                              Adversarial Professional Auditor
                                         |
                                         v
                                    Repair Owner
                                         |
                                         v
                                  independent reaudit
                                         |
                                         v
                              Production Director (必要時)
```

### 並列実行してよい工程

- Narrative、Vocabulary、Humor、Rhyme、Flow は共有brief確定後に並列実行できる。
- Reference Analyst は名前付き参照がある場合のみ先行させ、一般技法ベクトル確定後に他工程を開始する。
- Vocabulary と Rhyme は第一便を並列に作り、必要なら第二便で相互参照する。
- Humor は Narrative の暫定beat sheetなしでも候補を作れるが、最終配置は Narrative IDへ結び直す。
- Flow は歌詞前の制約mapを先に作り、初稿後に実語のモーラ負荷を再計算する。

第一便では循環参照を禁止する。第二便に
`vocabulary_rhyme_reconciliation`、`narrative_humor_reconciliation`、
`rhyme_flow_reconciliation`を置き、採用候補、棄却理由、共有ID、読み、bar範囲を
確定する。Draft後は実語で`flow_remap`を作り、旧い暫定mapを監査へ渡さない。

### 直列にする工程

- Draft Integrator は必要artifactが揃うまで開始しない。
- Auditor は統合済みの候補を受け取ってから開始する。
- Repair Owner は監査の gate、優先順位、禁止事項を受けてから修正する。
- 再監査は修復者とは別のエージェントが行う。別エージェントを使えない場合は、修復ログを閉じて新しい評価コンテキストで実行する。

## 共通artifact契約

すべての専門artifactは次の envelope を持つ。

```yaml
schema: artifact-type/version
run_id: ""
brief_hash: ""
producer:
  role: ""
  instance_id: ""
created_at: ISO-8601-or-null
status: ready | partial | blocked | unverified | stale
inputs:
  - artifact: brief.yaml
    revision: 1
assumptions: []
confidence: high | medium | low
evidence:
  - kind: user_input | performed_reading | dictionary | interview | paper | inference
    pointer: ""
warnings: []
payload: {}
```

### 出力品質

- 結論だけでなく、選択理由、棄却案、未解決リスクを残す。
- proseだけで渡さず、ID付き要素に分解する。
- `must_use` と `candidate` を分ける。
- 数値は絶対品質ではなく、比較または監査用の診断値として扱う。
- 他の役割へ命令せず、自分の提案と制約を分ける。

## 役割別契約

### Reference/Technique Analyst

**目的:** 名前付き参照、公開インタビュー、研究資料から移植可能な一般技法だけを抽出する。

**入力:** `brief.yaml`, `source_policy.yaml`

**禁止:** 商業歌詞の収録、特徴的な文句の転記、単一人物の完全再現、未確認の逸話。

**出力:** `technique_vector.yaml`

```yaml
schema: technique-vector/v1
source_profiles:
  - source_id: ""
    source_type: artist_interview | research | user_note
    confidence: high
transferable:
  sound: []
  rhythm: []
  narrative: []
  humor: []
  vocabulary: []
  structure: []
anti_transfer:
  signature_phrases: true
  rare_metaphor_clusters: true
  biography: true
  recognizable_story_sequence: true
distance_requirements:
  change_at_least: 3
  dimensions: [theme, speaker, setting, metaphor_domain, rhyme_family, structure]
```

複数参照に共通する技法と、一人だけに強く結びつく特徴を分離する。後者は原則として生成条件から外す。

### Narrative Architect

**目的:** 音より先に、曲の命題、圧力、変化、余韻を設計する。

**入力:** `brief.yaml`, 必要時 `technique_vector.yaml`

**出力:** `narrative_plan.yaml`

```yaml
schema: narrative-plan/v2
proposition: ""
pressure: ""
turn: ""
residue: ""
speaker_knowledge_boundary: []
sections:
  - section_id: S1
    bars: "1-4"
    function: setup
    new_information: ""
    scene: ""
    emotion: ""
    recurring_image_state: ""
    setup_ids: []
    payoff_ids: []
bar_jobs:
  - bar_id: B01
    job: ""
    must_communicate: ""
    withheld_information: ""
continuity_risks: []
```

4小節ごとに `情報、感情、フロー` の少なくとも一つが変化するよう設計する。非物語形式でも、主張、証拠、反証、再定義のような進行を与える。

### Vocabulary Director

**目的:** 抽象語を説明する前に、場面を見せる具体語、動作、感覚、社会関係を集める。

**入力:** `brief.yaml`, `narrative_plan.yaml`

**出力:** `vocabulary_bank.json`

詳細契約は `vocabulary-director.md` を読む。各語は surface だけでなく、読み、意味、含意、文法、音、物語上の用途、証拠を持つ。実体験を捏造しない。

### Humor Engineer

**目的:** 笑いの機構、前振り、予測、破り方、声色、間を設計する。

**入力:** `brief.yaml`, `narrative_plan.yaml`, `vocabulary_bank.json`

**出力:** `humor_plan.yaml`

```yaml
schema: humor-plan/v2
target_intensity: none | light | medium | high
persona_rule: ""
devices:
  - humor_id: H01
    type: self_deprecation | exaggeration | deadpan | satire | intelligent_vulgarity |
      proper_noun_collision | setup_payoff | knowledge_gap | foreign_object |
      callback | rule_of_three | bathos | register_collision | anti_joke |
      misdirection | double_meaning
    section_id: S1
    setup:
      stated_fact: ""
      predicted_frame: ""
    turn:
      violated_expectation: ""
      bridge_for_legibility: ""
    landing:
      semantic_target: ""
      timing: before_rest | on_strong_beat | after_pause
    character_cost: ""
    risk: cruelty | obscurity | random_reference | tonal_break | none
callbacks:
  - setup_id: H01
    payoff_section: S3
```

パンチラインそのものを書き切るより、期待の設計と壊す軸を渡す。固有名詞は知名度ではなく、文脈との距離と意味的必然性で選ぶ。

### Rhyme Graph Engineer

**目的:** 韻候補の羅列ではなく、音、文法、意味、配置の移動可能性を持つグラフを作る。

**入力:** `brief.yaml`, `vocabulary_bank.json`, `flow_map.yaml` の暫定版

**出力:** `rhyme_graph.json`

```yaml
schema: rhyme-graph/v2
nodes:
  - node_id: W001
    surface: ""
    reading: ""
    morae: []
    vowel_sequence: []
    consonant_sequence: []
    accent: unknown
    pos: ""
    semantic_domain: ""
    register: ""
    proper_noun: false
    frequency_band: common | marked | rare | unknown
    freshness: 0
    particles_before: []
    particles_after: []
    articulation_cost: 0
    reading_confidence: high
edges:
  - edge_id: E001
    from: W001
    to: W002
    relation: exact | slant | assonance | consonance | alliteration |
      phrase | mosaic | split | performance_variant
    matched_morae: 0
    vowel_similarity: 0.0
    consonant_similarity: 0.0
    mora_length_delta: 0
    accent_compatibility: unknown
    semantic_fit: 0
    syntactic_fit: 0
    novelty: 0
    transition_cost: 0
    placement_options: [internal, end, cross_bar]
    cautions: []
families: []
```

同音異義語、同一語反復、助動詞・語尾だけの一致は別ラベルにして、高価値韻へ自動昇格させない。無声化、長音、促音、撥音、演技上の伸縮は表記一致から独立して評価する。

### Flow Mapper

**目的:** 2小節または4小節単位で、密度、入口、アクセント、休符、呼吸、声色、変更点を設計する。

**入力:** `brief.yaml`, `narrative_plan.yaml`, `rhyme_graph.json` の候補

**出力:** `flow_map.yaml`

```yaml
schema: flow-map/v2
verification: text_only | spoken | recorded_on_beat
units:
  - unit_id: F01
    bars: "1-2"
    subdivision: eighth | sixteenth | triplet | mixed
    target_mora_range_per_bar: [10, 18]
    entry: beat_1 | pickup | after_rest
    strong_positions: []
    rests: []
    fast_zone: null
    held_vowels: []
    repeated_pattern_count: 2
    switch_at: null
    pre_punch_silence: null
    voice_color: ""
    character_voice: ""
    breath_after: B02
    narrative_reason: ""
risks: []
```

BPMまたはビートがなければ具体的な pocket を断定しない。テキスト上の提案と録音検証を分ける。

### Draft Integrator

**目的:** 専門artifactの候補を取捨選択し、意味が通り、口で言え、音が設計された複数初稿を作る。

**入力:** `brief`, `technique_vector`, `narrative_plan`, `vocabulary_bank`, `humor_plan`, `rhyme_graph`, `flow_map`

**出力:** `draft_candidates.md`, `integration_report.yaml`

最低2案を作る。

- `conservative`: 意味、声、自然な日本語を優先する。
- `experimental`: 音、構造、間、ユーモアの一要素を強くする。

各小節へ `bar_id` を残し、どの語彙、韻edge、humor ID、flow unitを採用したか記録する。すべてを入れようとしない。衝突時は `意味 > 話者の自然さ > 演奏可能性 > 構造 > 韻密度` を標準優先順位とする。

### Adversarial Professional Auditor

**目的:** 良い点を説明するのではなく、公開品質を妨げる最小の失敗を発見する。

**入力:** `brief.yaml`, 対象draft, 必要な分析artifact

**出力:** `audit_report.yaml`

`professional-audit-v2.md` の gate を先に適用し、その後だけ点数を付ける。Draft Integrator の自己説明や期待スコアは入力しない。

### Repair Owner

**目的:** 監査で確認された欠陥を、別の層を壊さず優先順に修復する。

**入力:** 対象draft, `audit_report.yaml`, 元の専門artifact

**出力:** `repair_report.yaml`, 改訂draft

```yaml
schema: repair-report/v1
source_revision: 1
target_revision: 2
changes:
  - issue_id: A-001
    bar_ids: [B03]
    layer: semantics | voice | image | rhyme | flow | humor | structure | originality
    before_summary: ""
    change_intent: ""
    after_summary: ""
    collateral_checks: []
unresolved: []
```

高密度化を万能修正にしない。末尾だけの語置換で構文や意味の欠陥を隠さない。

### Production Director

**目的:** 完成した意味と発話を、録音またはSuno向けの音楽仕様へ変換する。

**入力:** 再監査を通過したfinal、最終 `flow_map`

**出力:** production handoff

詞を制作仕様に合わせて変更する場合は Draft Integrator へ戻し、無監査で final を上書きしない。

## 統合と競合解決

### 競合台帳

```yaml
conflicts:
  - conflict_id: C01
    artifacts: [vocabulary_bank, rhyme_graph]
    description: "最良の韻候補が話者の語彙域から外れる"
    options:
      - id: O1
        effect: "韻を弱めて自然語を維持"
      - id: O2
        effect: "場面を追加して専門語を正当化"
    decision: O1
    rule: voice_over_density
    owner: Draft Integrator
```

### 標準優先順位

1. 安全、事実、著作権、briefの明示制約
2. 意味と因果
3. 話者の声、自然な日本語
4. 実演可能性、重要語の可聴性
5. 構造上の前振りと回収
6. イメージの具体性
7. 韻、ユーモア、技巧の密度

ただし、課題が韻練習など特定技法のexerciseである場合は、その技法を3位まで上げてよい。上げたことを `decision` に記録する。

### 棄却規則

- artifact間で読みが違う場合、ユーザー指定の実演読みを優先する。
- 辞書と想定発音が違う場合、両方を保持し、録音時の採用を明示する。
- 韻候補が語順を壊す場合、候補を棄却する。
- ユーモアが話者の損失や感情を無効化する場合、強度を落とすか別セクションへ移す。
- 固有名詞が説明なしでは伝わらない場合、落差の中心にしない。
- 同一行に複数専門家の見せ場が集中した場合、主機能を一つ決めて他を弱める。

## 独立監査と修復ループ

```text
integrated draft
  -> blind audit
  -> gates failed? --yes--> repair only failed layers
  -> scored audit
  -> top 3 issues
  -> repair
  -> fresh reaudit
  -> pass or explicit residual risk
```

監査者へ渡すのは、brief、draft、必要な読みとflow情報だけにする。Draft Integrator の意図、候補比較、自己評価は渡さない。再監査者は修復ログを参照してよいが、改善したという主張を信用せず、同じgateを再実行する。

修復は最大3周を既定とする。同じgateが2周連続で失敗した場合、局所修正を止め、Narrative または Flow の上流artifactへ戻る。

## 著作権・模倣防止

### ユーザー提供歌詞

- 依頼の範囲で全文を一時的に分析してよい。
- token、bar、section単位の詳細注釈を返してよい。
- 永続reference、fixture、語彙バンクへ自動追加しない。
- 書き換えでは保持する意味と変更する層を先に合意する。

### 商業曲・公開曲

- 歌詞全文または長い連続抜粋を取得、保存、再構成しない。
- 公開された本人インタビュー、公式解説、研究、短い適法な引用から一般技法を抽出する。
- bar機能は「場面提示」「自己卑下から反転」のように要約し、原文を保存しない。
- 単語単位の網羅復元を目的にしない。
- 曲名、アーティスト名、出典URL、抽象技法、確信度だけをsource profileへ残す。

### 名前付き模倣の変換

1. Reference Analyst だけが名前を見る。
2. 最低2人、可能なら3人以上から共通技法を抽出する。
3. `signature` と判定した特徴を削除する。
4. 題材、話者、場所、比喩領域、韻系列、構造のうち最低3軸を変える。
5. Integrator へは匿名化した technique vectorだけを渡す。
6. final は「オリジナル」として提示し、本人作を示唆しない。

## 失敗時のfallback

| 失敗 | fallback | status |
|---|---|---|
| サブエージェントが使えない | 役割ごとに独立コンテキスト/見出しで順番に実行 | partial |
| 辞書/G2Pが使えない | 手作業読みを併記し、曖昧語を警告 | unverified |
| BPM/beatがない | 相対密度、休符、強調だけを設計 | unverified |
| Referenceの一次資料がない | 参照名を生成条件から外し、一般技法だけで続行 | partial |
| Vocabularyが抽象語ばかり | scene packetを再取得し、具体物を最低8件集め直す | stale |
| Rhyme graphが疎 | 近似韻、phrase rhyme、内部配置へ探索範囲を広げる | partial |
| Humorが説明的 | punchline文を削り、予測と違反軸だけ再設計 | stale |
| Integratorが全候補を詰め込む | 主機能を1 bar 1つに戻す | stale |
| 監査者が甘い | 点数を破棄し、hard gateだけ別監査者で再実行 | stale |
| 修復で別層が悪化 | 直前revisionへ戻し、collateral checkを追加 | stale |

fallbackを使った事実を final の検証注記から隠さない。

## Claude Code adapter(第一ホスト)

Claude Code ではこの契約を次のように実行する。

### 役割 → Task サブエージェント

- 各専門役割を Task ツールのサブエージェントとして起動する。依存のない役割
  (Narrative、Vocabulary、Humor、Rhyme、Flow)は **1ターン内で並列に spawn** する。
- 各 Task へ渡すのは (1) 凍結した brief、(2) その役割に許可された reference ファイル、
  (3) 書き込み可能な出力パス1つ、(4) この資料の該当役割契約、だけにする。
- 同じファイルを複数の Task に編集させない。出力先は `run/<artifact名>` で役割ごとに固定する。
- 親コンテキストは Integrator として、Task 完了後に
  `python3 scripts/artifact_envelope.py validate` で artifact を検証してから統合する。

### 監査の独立性

- Professional Auditor は**新しい Task** として起動し、brief・成果物・監査rubricだけを渡す。
  Integrator の会話履歴、自己採点、意図説明は渡さない。これにより監査独立性を `full` にできる。
- 再監査(reaudit)も修復担当とは別の fresh Task で行い、元スコアを渡さない。
- 常設化したい場合は `agents/claude-code/` のサブエージェント定義をプロジェクトの
  `.claude/agents/` へコピーする。定義ファイルは adapter であり、正本の契約はこの reference に置く。

### 進行管理と検証

- orchestration の stage(reference → 並列specialist → integration → audit → repair → reaudit)
  を TodoList に写し、gate の飛ばしを防ぐ。
- `python3 scripts/orchestrate_plan.py brief.json` で決定的な task graph を作れる場合は先に作る。
- hook や slash command で検証を自動化する場合も、合否は `audit_report.yaml` へ移し、
  CLI 出力だけに残さない。
- Bash ツールから実行する script は Python 3.10+ 標準ライブラリのみで動く。
  `pyopenjtalk` / `fugashi` が無い環境では読みを手動併記し `unverified` とする。

### fallback

- Task が使えない環境(claude.ai の単一チャット等)では、役割promptを順番に実行し、
  前工程の自由記述ではなく artifact だけを次へ渡す。監査独立性は `partial` と表示する。

Claude固有のtool名、model名、権限設定を portable artifact の必須フィールドにしない。

## Codex/ChatGPT adapter(legacy)

ChatGPT/Codex で実行する場合の互換手順。正本は上記の portable core と Claude Code adapter。

- 並列エージェント機能がある場合、Narrative、Vocabulary、Humor、Rhyme、Flow を個別taskとして起動する。
- 各taskへ共有brief、許可されたreference、書き込み可能な出力ファイルだけを渡す。
- 同じファイルを複数エージェントに編集させない。
- 親エージェントは Integrator として、完了通知後にartifactを検証して統合する。
- Auditor は新しいtaskとして起動し、Integrator の会話履歴を必要最小限にする。
- filesystemがない対話では、artifact envelopeをMarkdown内のYAML/JSONとして返させる。

Codex固有のtool名、セッションID、絶対パスを portable artifact 内へ保存しない。

## 単一エージェント環境

以下の順番で「擬似分離」する。

1. briefを凍結する。
2. 各役割のartifactだけを書き、歌詞はまだ作らない。
3. 役割を切り替えるたびに前の自由推論を閉じ、artifactだけを入力として読む。
4. Integratorで最低2案を書く。
5. 自己弁護を閉じ、監査rubricだけを読み直して blind auditを行う。
6. repair reportを作り、修復する。
7. 元スコアを見ずに再採点する。

単一コンテキストで同時に「作者」「採点者」を演じた場合、監査独立性は `partial` と表示する。

## 完了条件

- briefと全final artifactの `brief_hash` が一致する。
- 必須roleのartifactが `ready` または理由付き `unverified` である。
- Reference名が匿名 technique vectorへ変換されている。
- 具体語、物語、ユーモア、韻、flowの提案がIDで追跡できる。
- 統合時の採用、棄却、競合理由が残る。
- hard gateを通過し、修復後の独立再監査がある。
- 未録音のperformance claimを断定していない。
- 商業歌詞がreferenceやfixtureへ保存されていない。
- finalだけでなく、残存リスクと検証状態を提示できる。
