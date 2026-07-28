# 参照ラッパーから抽出する押韻技術

## 目次

1. [この資料の使い方](#この資料の使い方)
2. [著作権と分析境界](#著作権と分析境界)
3. [証拠レベル](#証拠レベル)
4. [共通の分析プロトコル](#共通の分析プロトコル)
5. [R-指定から抽出する技術](#r-指定から抽出する技術)
6. [GADOROから抽出する技術](#gadoroから抽出する技術)
7. [KREVAから抽出する技術](#krevaから抽出する技術)
8. [梅田サイファーから抽出する技術](#梅田サイファーから抽出する技術)
9. [KOPERU・KennyDoes・テークエム・KBDの分析カード](#koperukennydoesテークエムkbdの分析カード)
10. [横断的に抽出できる独立モジュール](#横断的に抽出できる独立モジュール)
11. [三曲ずつの分析キュー](#三曲ずつの分析キュー)
12. [語単位分析の実行契約](#語単位分析の実行契約)
13. [禁止する学習方法](#禁止する学習方法)
14. [ソース記録](#ソース記録)

## この資料の使い方

この資料は「R-指定風」「GADORO風」等の模倣プロンプトを作るためのものではない。
本人発言、公式作品情報、正規配信音源から、再利用可能な工程だけを抽出する。

抽出単位は次の通り。

- `composition_method`: どこから書き始めるか。
- `rhyme_architecture`: 韻をどこへ、何層、どの距離で置くか。
- `semantic_method`: 韻と意味をどう両立するか。
- `flow_method`: 韻をどう聞かせるか。
- `revision_method`: どこを削り、何を書き直すか。
- `ensemble_method`: 複数MC間で何を受け渡すか。

出力時にはアーティスト名を外し、これらの技術IDだけを組み合わせる。

## 著作権と分析境界

- 市販曲の歌詞全文、長い連続箇所、復元可能な語順を保存しない。
- 正規配信の音源を聞いて作る注釈は、bar番号、音韻型、位置、機能、短い要約にする。
- 一語ずつの完全分析は、ユーザー提供歌詞、権利保有テキスト、ライセンス済み歌詞に限る。
- 一般公開用の参照ファイルには、商業歌詞のtoken列を入れない。
- 代表曲名を示すことは、分析対象の識別であり、歌詞の転載ではない。
- 本人の希少な口癖、固有ad-lib、個人史、方言表面を生成voiceへ移植しない。

このため以下の「三曲分析」は、歌詞を記録するものではなく、何を聴き、どの
技術仮説を検証するかを定義する研究キューである。

## 証拠レベル

| 等級 | 根拠 | 記述の仕方 |
|---|---|---|
| A | 本人の制作発言、公式クレジット、公式音源 | 技術の直接根拠 |
| B | 査読研究、信頼できる一次コーパス分析 | 音韻・フロウの一般化 |
| C | 音楽媒体の本人インタビュー、正規配信メタデータ | 制作意図と作品同定 |
| D | 研究者による音源聴取メモ | 仮説として明記 |
| E | 歌詞サイト、まとめ、人気順位 | 根拠にしない |

観察と推論を混ぜない。

```yaml
claim:
  statement: ""
  status: observed | artist_stated | inferred | unknown
  source_url:
  audio_verified:
  transcript_authorized:
```

## 共通の分析プロトコル

### Pass 1: 作品単位

1. 正規配信または公式MVで曲名、版、参加者を確定する。
2. BPM、拍子、bar境界は音源から取り、外部BPMサイトを唯一の根拠にしない。
3. セクション、話者、フロウ変更点、フック回帰を記録する。
4. 歌詞を保存せず、barごとの意味機能を要約する。

### Pass 2: 音韻単位

1. 主要な韻spanだけ、認識に必要な最小限の短い部分を私的注釈する。
2. 読み、モーラ、母音、子音、N/Q/R、語境界を付ける。
3. exact/slant、internal/end/cross-bar、multi-mora/mosaic等を複数付与する。
4. 助詞・助動詞・活用語尾を除いても対応が残るか調べる。

### Pass 3: 聴感単位

1. 韻の着地が強拍、裏拍、休符前、伸長上のどこにあるか記録する。
2. 直前の密度、音価、声量、音高が韻を目立たせているか調べる。
3. テキスト上で強くても、実演で埋もれる韻を分ける。
4. アカペラ版・ライブ版がある場合、同じ韻の聞こえ方を比較する。

### Pass 4: 意味単位

1. 韻語を外しても、文として面白いか。
2. 韻語が場面、人物、主張を前へ進めるか。
3. 意味領域の距離が意外性を作りつつ、文脈内に留まるか。
4. 固有名詞や外来語が、音合わせだけでなく意味上の仕事をするか。

### Pass 5: 抽象化

固有語を削除し、次のような技術カードへ変換する。

```yaml
technique_id: RHY-LAYER-03
input_condition:
  bpm_range:
  section_job:
  semantic_material:
operations:
  - "同一cadence内に内部韻familyを増やす"
  - "4小節目だけfamilyを切り替える"
constraints:
  - "文法語尾をanchorにしない"
  - "主要韻に内容語を一つ以上含める"
validation:
  - "end_bias < 0.65"
  - "naturalness >= 0.8"
source_basis: []
```

## R-指定から抽出する技術

### 本人発言から確定できる工程

1. **少ないフロウ手数に韻を増やす。**
   『アンサンブル・プレイ』期の本人発言では、フロウの手数を絞り、同じフロウの中で
   グルーヴさせるため韻の数を増やしたと説明されている。これは
   `flow_complexity`と`rhyme_density`を同時に上げない設計として抽象化できる。
   <https://natalie.mu/music/pp/creepynuts05>

2. **タイトル級の一語・パンチラインを制作の照明にする。**
   本人は、決めのフレーズやタイトルになる語が出ると曲全体が進みやすいと説明する。
   先に全行を韻で埋めるのでなく、核フレーズから逆算する工程にできる。
   <https://www.oricon.co.jp/news/2224563/full/>

3. **既出テーマを、視点変更で再設計する。**
   「堕天」では、すでに扱った「夜」を直接繰り返さず、一人称中心から第三者・
   フィクショナルな視点へ移したと本人が説明している。
   <https://www.musicman.co.jp/artist/480417>

4. **音符でなく言葉固有のリズムを聴く。**
   R-指定は他ジャンルの歌詞についても「音符じゃない言葉としてのリズム」と
   ライムの運びを聴き取っている。語義、文節、発話リズムを譜割り前から扱う
   分析姿勢として抽出できる。
   <https://natalie.mu/music/pp/teto>

### 独立技術カード

#### `RHY-STABLE-CADENCE-DENSITY`

- cadence patternは1〜2種類に限定する。
- 同一cadence内で、末尾だけでなく拍2、拍3裏、拍4へ別familyを置く。
- 4小節単位で一度だけfamilyまたは着地位置を変える。
- 評価は韻数でなく、同じcadenceを飽きさせない機能で行う。

#### `COMPOSE-ANCHOR-BACKWARD`

- 曲の命題を含むタイトル級フレーズを一つ作る。
- そのフレーズの意味前提を2〜4小節前へ配置する。
- anchorの音列から2 familyを派生させる。
- anchor自体は最も長い韻でなくてもよい。

#### `POV-REFRACTION`

- 既出・凡庸な主題に対し、話者、観察距離、時間、相手の一つを変える。
- 視点変更後の語彙場を先に作り、元テーマ語を禁止語にして1稿を書く。
- 最終稿でテーマ語を戻すか判断する。

### 三曲の研究キュー

| 曲 | 公式・正規ソース | 検証する仮説 |
|---|---|---|
| 生業 | 公式アルバム／ライブ収録情報 <https://creepynuts.com/1manTour2021release/> | 自己定義を進めながら内部・多モーラ韻がどの位置に積層するか |
| 堕天 | 公式作品情報 <https://creepynuts.com/ensembleplay2022/> | 第三者視点、メロディ、韻密度の分担 |
| ビリケン | 公式アルバム情報 <https://creepynuts.com/legion/> | 一つのcadence内で反復、語感、内部韻が推進力を作るか |

上表は「技術の候補」であり、音源と権利ある歌詞をbar単位で照合するまで
具体的な韻familyを確定しない。

## GADOROから抽出する技術

### 本人発言から確定できる工程

1. **高密度押韻とメロディを対立させない。**
   GADOROは『TAKANABE』以降について「韻をめちゃくちゃ踏みながら歌ったり
   メロディを付けたりする」方向へ変化し、今後研ぎ澄ませたいと説明している。
   `rhyme_density`と`melodic_delivery`を別スライダーにして両立させる根拠になる。
   <https://natalie.mu/music/pp/gadoro03>

2. **生活の変化を抽象的成功談でなく、空間の尺度で示す。**
   『四畳半』から『1LDK』へのタイトル設計を、実際の住居と制作上の原点回帰の
   両方として本人が説明している。生活物・間取り・価格・傷等を語彙の先行材料に
   する工程へ抽象化できる。
   <https://natalie.mu/music/pp/gadoro>

3. **強い共演相手に対して全面改稿する。**
   般若との共作では、競争心から自分のverseを何度も書き直し、録り直したと
   本人が説明する。初稿の韻密度を正当化せず、隣接verseとの比較で再設計する
   `competitive_revision`にできる。
   <https://natalie.mu/music/pp/gadoro>

4. **弱さや失敗を、主張でなく具体的出来事へ変換する。**
   本人の作品・インタビューを横断すると、居住空間、地元、失敗、緊張等を隠さず
   主題化する姿勢が一貫する。ただし、生成時に本人の貧困・地元・家族史を借用せず、
   ユーザー本人の事実または架空設定から具体物を集める。

### 独立技術カード

#### `RHYME-MELODY-DUAL`

- hookまたは半hookで母音の伸ばしやすいanchorを選ぶ。
- verse内部では子音・多モーラ対応を増やす。
- 同一語を歌う箇所と、密に踏む箇所を分ける。
- 伸長を韻成立の言い訳にせず、基底形でも近さを残す。

#### `CONCRETE-STATUS-METER`

- 抽象テーマを、部屋、靴、レシート、移動距離、故障音等の測れる物へ落とす。
- 4小節ごとに「物→行動→代償→現在の判断」の順で進める。
- 成功をブランド羅列だけで示さない。

#### `COMPETITIVE-REVISION`

- 比較対象verseの最強点を`meaning / rhyme / flow / image / punch`に分解する。
- 自分の初稿を同じ軸で採点する。
- 一軸だけ上回る修正ではなく、意味を保ったまま弱い二軸を直す。
- 相手の語彙、固有名詞、口癖を借りない。

### 三曲の研究キュー

| 曲 | 公式・正規ソース | 検証する仮説 |
|---|---|---|
| ラッパーなのに | 公式ライブ収録情報 <https://gadoro.jp/blogs/%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9/20250530> | 自虐が地位低下だけで終わらず、技術誇示へ反転する位置 |
| 自遊空間 | 公式アルバム情報 <https://gadoro.jp/products/gadoro-newalbum-takanabe> | 高密度押韻とキャッチーなdeliveryの両立 |
| クズ | 公式ライブ収録情報 <https://gadoro.jp/blogs/%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9/20250530> | 自己否定語を反復しながら、各回の意味と感情を更新する方法 |

## KREVAから抽出する技術

### 本人発言・公式情報から確定できる工程

1. **紙とペンを含む反復可能な制作習慣。**
   KREVAは、リリック制作で必ず手書きし、頭の中の「リリックの棚」を半開きに
   しておく練習について語る。日常で候補語、句、音列を継続採取する
   `always-open-capture`へ抽象化できる。
   <https://abc-magazine.asahi.co.jp/post-45561/>

2. **作詞、作曲、トラック、ラップを統合して判断する。**
   公式プロフィールは、作詞、作曲、トラックメイク、ラップ、プロデュースを
   自身で行うことを明記する。韻だけを文章上で最適化せず、トラック余白、旋律、
   音価まで一体で判断する研究対象となる。
   <https://hibiyamusicfes.jp/2025/lineup/profile/kreva/>

3. **技術密度と初見理解を両立する。**
   Apple Musicの編集プロフィールは、ラップ固有の面白さを押し出しながら、
   初めて聴いても意味が理解できる言葉遣いとウィットを特徴として説明する。
   これは本人発言ではないためC/D級だが、監査仮説として有用。
   <https://music.apple.com/jp/artist/kreva/74494472>

4. **異なる時期・形式で同じ曲を再演し、技術を検証する。**
   「音色」には後年版があり、『Project K』にはライブ、MV、制作映像がある。
   同じ言葉を別アレンジで比較し、韻の強さと伴奏依存を分けられる。
   <https://www.jvcmusic.co.jp/-/Discography/A025671/VIZL-2409.html>

### 独立技術カード

#### `ALWAYS-OPEN-CAPTURE`

- 日常採取を`phrase / sound / image / contradiction / proper_noun`へ分類する。
- その場で曲にしない。使用候補に日付、場面、感情、読みを付ける。
- 制作時にテーマ一致と音一致の二段階で検索する。
- 使用後も原文を削除せず、派生と採用理由を記録する。

#### `TRACK-LYRIC-CO-DESIGN`

- トラックの空白、低域、主旋律、snare位置を先に記述する。
- 音数の多い語を、伴奏が密な箇所へ置かない。
- 韻着地と楽器のaccentが常時重ならないよう、強調と抜きを設計する。
- hookでは理解速度、verseでは再聴取価値を優先する。

#### `CLEAR-WIT`

- 一聴目で命題が分かるplain lineを一本置く。
- 周辺に多義語、軽い意味反転、音の対応を積む。
- 解説しなければ成立しない固有名詞ネタを避ける。
- 韻を外しても、発話として機知が残るか確認する。

### 三曲の研究キュー

| 曲 | 公式・正規ソース | 検証する仮説 |
|---|---|---|
| 音色 | 公式プロフィール／正規配信 <https://hibiyamusicfes.jp/2025/lineup/profile/kreva/> | メロディックなhookとラップの韻設計がどう役割分担するか |
| 基準 | 正規配信情報 <https://music.apple.com/jp/song/1199462194> | 明快な中心語を反復しつつ、verse側で定義を更新する方法 |
| No Limit | 公式作品情報 <https://www.jvcmusic.co.jp/-/Discography/A025671/VIZL-2409.html> | 短時間・高密度の中で意味理解と技術提示を両立する方法 |

## 梅田サイファーから抽出する技術

### 公式情報から確定できる条件

Sony Music公式プロフィールは、梅田サイファーを上下関係やリーダーのない
「個人の集まり」と説明する。したがって分析単位を「統一された一人の作風」に
せず、各MCの独立性とマイクリレーの接続技術に置く。
<https://www.sonymusic.co.jp/artist/UMEDACYPHER/profile/>

公式アルバム情報は各曲の参加MCを列挙しており、話者別比較の信頼できる
クレジットになる。
<https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/549766>
<https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/566336>

### 独立技術カード

#### `MIC-RELAY-HANDOFF`

- 前話者の最後の韻family、意味、声色、リズムのうち一つだけを引き継ぐ。
- 残り二つ以上を変え、人物差を出す。
- 完全断絶を選ぶ場合は、休符、効果音、hookで境界を可聴化する。
- `SPEAKER_HANDOFF` edgeで引継ぎ対象を記録する。

#### `CONSTRAINT-PUNCHLINE`

- 外部題材、紹介対象、固有名詞を必須語として受け取る。
- 固有名詞を説明するのでなく、別意味領域の動詞・比喩へ接続する。
- 一つの対象につき、情報、音、笑いの三機能から最低二つを満たす。
- PlayStation公式コラボのような制約付き書き下ろしを研究対象にできる。
  <https://www.famitsu.com/news/202303/09295406.html>

#### `ENSEMBLE-CONTRAST`

- 同一トラック上で各MCに`density`, `register`, `rhyme_family`,
  `humor_temperature`, `entry_position`を割り当てる。
- 隣接MCが全項目同じにならないよう制約する。
- 曲全体のhook anchorだけ共有し、verseの語彙を均質化しない。

### 三曲の研究キュー

| 曲 | 公式・正規ソース | 検証する仮説 |
|---|---|---|
| KING | 公式曲目・参加者 <https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/549766> | 短いverseで固有題材、パンチ、話者差をどう立てるか |
| Odd Numbers | 公式アルバム情報 <https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/566336> | 異質な個を、共有テーマとhandoffで束ねる方法 |
| CONTINUE | 正規配信クレジット <https://music.apple.com/jp/album/continue-feat-koperu-peko-kbd-kennydoes-single/1740696154> | 4MCの少人数リレーでfamilyと意味をどう継続するか |

## KOPERU・KennyDoes・テークエム・KBDの分析カード

以下は作風を断定する人物ラベルではなく、複数曲から検証する観測テンプレート。
各MCを最低3曲・3verseで分析し、単一曲の印象を一般化しない。

### KOPERU

研究曲:

1. `KING`
2. `CONTINUE`
3. `Odd Numbers`

観測項目:

- 語頭・内部・末尾のどこへ韻anchorを置くか。
- 句の長さと休符が反復時にどう変わるか。
- 前話者の意味または音を受けるか、断つか。
- 口語registerと多モーラ韻の自然さ。

### KennyDoes

研究曲:

1. `KING`
2. `CONTINUE`
3. `Odd Numbers`

観測項目:

- 拍頭・裏拍の着地比率。
- 韻family変更がトラックやsection設計と一致するか。
- 話者としてのverseと、曲全体の構成上の役割。
- 内容語と文法語尾の比率。

KennyDoesは公式クレジットで制作参加が確認できる曲もあるため、MCとしての
観察とプロデューサー／作曲上の判断を混ぜない。たとえば『RAPNAVIO』の
「アマタノオロチ」はprod. KennyDoesと公式記載される。

### テークエム

研究曲:

1. `KING`
2. `Odd Numbers`
3. `Rodeo13`

観測項目:

- 声色・人物切替と韻familyの同期。
- 誇張、固有名詞、比喩の着地が音のためだけになっていないか。
- 高密度区間前後の休符。
- 句跨ぎ・小節跨ぎのspan。

「Rodeo13」は公式に参加者と一発撮り映像が確認でき、スタジオ版と実演の
比較に使える。
<https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/566597>

### KBD

研究曲:

1. `KING`
2. `CONTINUE`
3. `Odd Numbers`

観測項目:

- setupからpunchまでの距離。
- punch語と韻anchorが同じか、ずらされているか。
- 一義的説明と多義的語遊びの比率。
- 笑いがなくても韻と主張が残るか。

### 比較表

| 変数 | KOPERU | KennyDoes | テークエム | KBD |
|---|---|---|---|---|
| 主要韻位置 | 要測定 | 要測定 | 要測定 | 要測定 |
| 平均span長 | 要測定 | 要測定 | 要測定 | 要測定 |
| end bias | 要測定 | 要測定 | 要測定 | 要測定 |
| family entropy | 要測定 | 要測定 | 要測定 | 要測定 |
| 文法語尾依存 | 要測定 | 要測定 | 要測定 | 要測定 |
| punch前休符 | 要音声 | 要音声 | 要音声 | 要音声 |
| handoff方式 | 要比較 | 要比較 | 要比較 | 要比較 |

値を事前に埋めないことが重要である。聴感的な評判を測定値に見せかけない。

## 横断的に抽出できる独立モジュール

### `DENSE-BUT-CLEAR`

根拠候補: R-指定、GADORO、KREVA。

1. 4小節のplain-language命題を書く。
2. 内容語を残し、内部韻を2箇所増やす。
3. 末尾韻を一つ外して休符へ変える。
4. 音読し、一聴理解を損なう語順を戻す。

### `MELODY-RHYME-SEPARATION`

根拠候補: GADORO、KREVA、R-指定。

- 伸ばす母音をhook anchorにする。
- verseでは別familyを内部へ置く。
- hookの反復は意味更新または声色更新を伴わせる。
- メロディが韻の不一致を隠していないかアカペラで確認する。

### `CONCRETE-BEFORE-RHYME`

根拠候補: GADORO、R-指定の一人称／人物描写。

- テーマ語を一時禁止する。
- 具体物8、行動6、数値3、音3、会話2を集める。
- そこから自然な句を作り、最後に韻familyを探す。
- 先に作った韻辞書から場面を捏造しない。

### `ANCHOR-AND-REFRACTION`

根拠候補: R-指定、KREVA。

- タイトル級anchorを決める。
- 同じ意味を正面から3回説明しない。
- 視点、時間、人物、比喩領域を変えてanchorを3回照らす。
- 各回の韻familyも同一に固定しない。

### `COLLECTIVE-DIFFERENCE`

根拠候補: 梅田サイファー。

- 共通の命題とhookだけ共有する。
- 各MCへ異なる具体語彙、韻位置、密度、ユーモア役割を割り当てる。
- handoffは一要素を継承し、二要素を変更する。
- 最終verseが情報・感情・フロウの少なくとも一つを更新する。

## 三曲ずつの分析キュー

### 必須成果物

各アーティスト／MCごとに三曲を分析した後、以下を出す。

```yaml
artist_or_mc:
tracks:
  - title:
    version:
    official_source:
    participants:
    transcript_authorized:
observed_techniques: []
inferred_techniques: []
cross_track_constants: []
cross_track_variants: []
not_enough_evidence: []
portable_modules: []
do_not_copy: []
```

### 三曲ルール

- 同一アルバム三曲だけに偏らせない。ただし現在技法の比較目的なら理由を記す。
- battle映像だけ、pop songだけ、客演だけに偏らせない。
- 少なくとも一曲は音源とライブ／一発撮りの比較可能なものを選ぶ。
- 三曲で共通しない特徴を「本人の本質」と呼ばない。
- 複数人曲では、話者境界を確定できない箇所を保留する。

## 語単位分析の実行契約

完全な語単位分析は、ユーザー提供またはライセンス済みテキストに対して行う。
各tokenは最低限、次を説明する。

| フィールド | 平易な説明 |
|---|---|
| `surface` | 実際に書かれた形 |
| `reading` | その箇所での読み |
| `mora` | リズム上の音の単位 |
| `POS` | 名詞・動詞・助詞等 |
| `sense` | 文脈内で何を意味するか |
| `semantic-domain` | 生活、金、身体、学校等の領域 |
| `syntax-role` | 主語、目的語、修飾、述語等 |
| `register` | 口語、文語、俗語、専門語等 |
| `rhyme-role` | anchor、response、bridge等 |
| `humor-role` | setup、misdirection、punch等 |

さらに句・bar単位で次を説明する。

- 文字通りの意味。
- 含意、比喩、固有名詞の背景。
- 前barから増えた情報。
- 韻familyと実演上の着地。
- 語順を変えると何が失われるか。
- 笑いやパンチの前振りと回収。
- 韻を外した場合にも残る面白さ。

商業歌詞がユーザーから提供されていない場合は、語列を再現せず、次へ縮退する。

```text
bar 5–8:
- 場面要約
- 主要な意味領域
- 韻位置と音列の抽象パターン
- フロウ変化
- 技術仮説
- 音声／歌詞の未確認事項
```

## 禁止する学習方法

- 曲名とラッパー名だけから作風を自動補完する。
- 歌詞サイトをscrapeし、商業歌詞全文をskillへ同梱する。
- 一つの有名曲の特徴を全キャリアへ一般化する。
- 「韻が多い」「言葉遊びがすごい」で分析を終える。
- 母音列だけを抽出し、子音、特殊モーラ、語境界、実演を捨てる。
- 末尾一致数だけでプロらしさを採点する。
- ラッパー本人の貧困、地元、家族、受賞歴を架空の話者へ移す。
- 固有の口癖、ad-lib、希少比喩をfew-shot例として再利用する。
- 複数MCのverseを一人の「梅田サイファー風」へ平均化する。
- 音声未確認のpitch、無声化、pocketを確定値として保存する。

## ソース記録

### R-指定／Creepy Nuts

- 『アンサンブル・プレイ』制作インタビュー。フロウの手数を絞り、同一フロウ内で
  韻数を増やしたという本人発言。
  <https://natalie.mu/music/pp/creepynuts05>
- R-指定の作詞開始点に関する本人発言。タイトル級のフレーズが制作を進める。
  <https://www.oricon.co.jp/news/2224563/full/>
- 「堕天」の視点変更と既出テーマ回避に関する本人発言。
  <https://www.musicman.co.jp/artist/480417>
- 公式作品情報: 『Case』『アンサンブル・プレイ』『LEGION』。
  <https://creepynuts.com/1manTour2021release/>
  <https://creepynuts.com/ensembleplay2022/>
  <https://creepynuts.com/legion/>

### GADORO

- 2025年本人インタビュー。『TAKANABE』以降の高密度押韻とメロディの両立を説明。
  <https://natalie.mu/music/pp/gadoro03>
- 2020年本人インタビュー。『四畳半』から『1LDK』、原点回帰、共演時の全面改稿を説明。
  <https://natalie.mu/music/pp/gadoro>
- 公式『TAKANABE』曲目。
  <https://gadoro.jp/products/gadoro-newalbum-takanabe>
- 公式『HOME』および武道館映像曲目。
  <https://gadoro.jp/blogs/%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9/20250530>

### KREVA

- 2025年本人インタビュー。手書きと日常的なリリック準備。
  <https://abc-magazine.asahi.co.jp/post-45561/>
- 公式プロフィール。作詞・作曲・トラックメイク・ラップ・プロデュースの統合。
  <https://hibiyamusicfes.jp/2025/lineup/profile/kreva/>
- 公式『Project K』作品情報。
  <https://www.jvcmusic.co.jp/-/Discography/A025671/VIZL-2409.html>
- 正規配信プロフィールと作品ページ。本人発言ではない説明はC/D級として扱う。
  <https://music.apple.com/jp/artist/kreva/74494472>
  <https://music.apple.com/jp/song/1199462194>

### 梅田サイファー

- Sony Music公式プロフィール。集団の成り立ちと非階層的な個人集合。
  <https://www.sonymusic.co.jp/artist/UMEDACYPHER/profile/>
- 公式『RAPNAVIO』参加者・producer表。
  <https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/549766>
- 公式『Unfold Collective』曲目と参加者。
  <https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/566336>
- 公式「Rodeo13」一発撮り情報。
  <https://www.sonymusic.co.jp/artist/UMEDACYPHER/info/566597>
- PlayStation制約付き書き下ろしの公式発表転載。
  <https://www.famitsu.com/news/202303/09295406.html>
- KOPERU、peko、KennyDoes本人インタビュー。個の集合、参加経緯、サイファー文化。
  <https://www.jprime.jp/articles/-/27304>

### 一般化の音韻根拠

- Shigeto Kawahara, “Half Rhymes in Japanese Rap Lyrics and Knowledge of Similarity.”
  <https://user.keio.ac.jp/~kawahara/pdf/JEAL16_kawahara.pdf>
- Shigeto Kawahara, “The phonetics of Japanese rap rhymes.”
  <https://user.keio.ac.jp/~kawahara/pdf/rap2017.pdf>
- Noriko Manabe, “Globalization and Japanese Creativity: Adaptations of Japanese
  Language to Rap.” 表面コピーでなく日本語への創造的適応を見る根拠。
  <https://www.norikomanabe.com/publications/globalization-and-japanese-creativity>

最終確認日: 2026-07-27
