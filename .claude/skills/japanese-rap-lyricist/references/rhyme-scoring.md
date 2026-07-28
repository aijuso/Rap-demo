# 日本語ラップの韻類似度・候補探索仕様

## 目次

1. [目的](#目的)
2. [証拠格付け](#証拠格付け)
3. [韻ドメイン](#韻ドメイン)
4. [音韻アラインメント](#音韻アラインメント)
5. [スコア構成](#スコア構成)
6. [完全韻・近似韻・特殊モーラ](#完全韻近似韻特殊モーラ)
7. [位置・内部韻・連鎖韻](#位置内部韻連鎖韻)
8. [意味・自然さ・創造性](#意味自然さ創造性)
9. [候補探索](#候補探索)
10. [説明可能な出力](#説明可能な出力)
11. [誤検出と過剰最適化](#誤検出と過剰最適化)
12. [評価仕様](#評価仕様)
13. [出典](#出典)

## 目的

韻の「音の近さ」と、リリックとしての「良さ」を分離して測る。音韻的に完全でも
同じ語尾の反復なら創造性は低い。意味が面白くても音が対応しなければ韻ではない。
一つの不透明な総合点だけを返さず、下位スコアと成立条件を返す。

## 証拠格付け

| 等級 | 根拠 | 用途 |
|---|---|---|
| A | 査読研究、一次コーパス分析 | 韻構造と子音類似度の主要根拠 |
| B | 公式実装・API・再現可能な公開コード | 実装契約 |
| C | 未査読予稿、研究会論文、学位論文 | スコア初期値、探索手法の候補 |
| D | 個人解説、出典不明の韻検索サービス | 仕様の根拠にしない |

## 韻ドメイン

日本語ラップの行末韻は、行末側から複数のモーラ的要素が対応する。川原の初期分析
では最低2要素、母音とcodaのN/Qが対応し、周辺部の非対応モーラを最大1つ
extrametricalとして許す分析が提案されている
（[C1](https://user.keio.ac.jp/~kawahara/pdf/hiphop_prose.pdf)）。
後の概説では、行末から複数母音、しばしば最低2つで、上限は固定されない
（[C2](https://user.keio.ac.jp/~kawahara/pdf/rap2017.pdf)）。

実装規則:

- 末尾から2〜8モーラの可変長windowを比較する。
- 8は検索量を抑える既定値であり、ユーザーが長い多音節韻を求める場合は広げる。
- 1モーラ一致は`weak`または偶然一致とし、通常の成立判定には使わない。
- 周辺の非対応要素は最大1つを減点付きで許す。
- 内部の任意gapは高コストにする。
- 句読点を末尾とみなすか、小節末を末尾とみなすかを入力メタデータで切り替える。

例:

```text
未来    mi-ra-i  → i-a-i
芝居    shi-ba-i → i-a-i
```

表面の子音が異なっても、3母音が行末から対応する。子音類似度は完全性を上げる
加点要素であり、母音一致を置き換える唯一の条件ではない。

## 音韻アラインメント

### 基本方式

suffix-anchored semi-global alignmentを使う。行末側の位置ほど重くする。

```text
position_weight(p, L, alpha) = ((p + 1) / L) ** alpha
```

`p=0`を比較window先頭、`p=L-1`を行末とし、既定`alpha=3`を初期値にできる。
これは2026年の大会予稿
（[C3](https://www.anlp.jp/proceedings/annual_meeting/2026/pdf_dir/P9-3.pdf)）
に基づく実装候補であり、査読済みの普遍値ではない。

### 母音置換の初期コスト

同予稿の初期値:

|  | a | i | u | e | o |
|---|---:|---:|---:|---:|---:|
| a | 0 | 3 | 5 | 2 | 4 |
| i | 3 | 0 | 2 | 1 | 3 |
| u | 5 | 2 | 0 | 3 | 1 |
| e | 2 | 1 | 3 | 0 | 2 |
| o | 4 | 3 | 1 | 2 | 0 |

- Nと通常母音の置換コストは4を初期値にする。
- 挿入・削除の基礎コストは周辺1、内部3を初期値にする。
- 値は`vowel_costs.json`等へ外出しし、評価セットで調整する。
- コスト表だけで韻の可否を決めない。

距離を0〜1へ変換する例:

```text
r_rhyme = clamp(1 - d_suffix / d_max, 0, 1)
```

ただし、`d_max`は比較window、挿入削除、置換表から一貫して計算する。
発音候補が複数あるときは全組み合わせを採点し、最良値と採用候補を返す。
低信頼の発音候補でのみ高得点になる場合は`needs_review=true`とする。

## スコア構成

既定の説明用構成:

```text
sound_score =
    0.40 * nucleus_match
  + 0.10 * special_mora_match
  + 0.10 * onset_similarity
  + 0.10 * matched_span_length
  + 0.05 * position_salience

lyric_score =
    0.10 * flow_prosody
  + 0.10 * semantic_relevance_and_naturalness
  + 0.05 * novelty_after_duplicate_penalty
```

重みは初期値であり、スタイル別に変更可能にする。必ず次を個別に返す。

- `nucleus_match`
- `special_mora_match`
- `onset_similarity`
- `matched_span_length`
- `position_salience`
- `flow_prosody`
- `semantic_relevance`
- `naturalness`
- `novelty`
- `duplicate_penalty`
- `pronunciation_confidence`

`final_score`を返す場合も、soundとlyricを別々に残す。ユーザーが「硬い韻」を
求める場合は子音・長さ・特殊モーラを強め、「ゆるい韻」を求める場合は
近似母音の許容幅を広げる。ただし、意味と自然さの下限を外さない。

## 完全韻・近似韻・特殊モーラ

### 母音

優先順位:

```text
同じ基底母音
> 通常の実発音候補で一致
> 長母音化・縮約候補で一致
> 無声化を仮定した場合のみ一致
> 音響的に近い母音
```

変形を多く仮定するほど減点する。一つのpairで複数の低信頼変形を積み重ねて
「完全韻」に昇格させない。

### 特殊モーラ

N/Q/Rを比較するモードを二つ用意する。

- `strict_mora`: N/Q/Rの有無と位置を強く評価する。
- `nucleus_only`: 母音音質を中心にし、N/Q/R不一致を小さく減点する。

例:

```text
感動 ka-N-do-R
反応 ha-N-no-R
```

母音とN/Rの位置が揃い、strictでも強い。一方、短母音語との比較は
nucleus-onlyでは近くてもstrictでは下がる。

### 子音

川原2007は98曲、20,224の子音対応を調べ、音声的に類似する子音ほど韻で
対応しやすいことを示した
（[A1](https://user.keio.ac.jp/~kawahara/pdf/JEAL16_kawahara.pdf)）。
共有弁別素性数とrhymabilityには有意な正相関がある。

最低限の特徴:

- place
- manner
- voice
- palatal
- nasal
- continuant
- sonorant

同研究に示された歴史コーパスの回帰例:

```text
ln(O/E) =
  -0.94
  + 0.62[pal]
  + 0.25[voi]
  + 0.23[nas]
  + 0.21[cont]
  + 0.11[son]
  - 0.008[cons]
  - 0.12[place]
```

これを固定の美的法則にしない。説明可能な弱いpriorとしてのみ使う。
論文自身も弁別素性だけでは詳細な音響類似性を捉えきれないとする。

## 位置・内部韻・連鎖韻

### 位置

次を独立したsalience特徴にする。

- 行末
- 小節末
- 強拍
- 句末
- 反復される同一拍位置

拍情報がなければ推測せず`unknown`とする。テキスト上の改行を必ず小節末と
仮定しない。

### 内部韻

各行の2〜6モーラwindowを列挙し、同一行または隣接行のwindow同士を比較する。
行末韻と同じ閾値にせず、次を返す。

- span
- token境界
- bar/beat位置
- 重なりの有無
- 偶然一致の推定

同じ語の内部で機械的に生じた部分一致を多数の内部韻として重複計上しない。

### 連鎖韻

行・句をnode、pairwise rhymeをedgeとするグラフで表現する。全行を一つの
anchorだけに比較すると、A〜B、B〜Cは強いがA〜Cは弱い循環的な連鎖を落とす。
connected component、edge強度、音形の推移を返す。

## 意味・自然さ・創造性

音響スコアとは独立して評価する。

- `semantic_relevance`: 曲のテーマ、直前行、話者設定への適合
- `naturalness`: 日本語としての語順、係り受け、用法、発話可能性
- `semantic_distance_of_pair`: 韻語同士の意味の距離
- `novelty`: 予測しにくさ、表層重複の少なさ
- `persona_fit`: 語彙が演者設定や視点と整合するか

「韻の飛距離」は、テーマ適合を保ったまま、韻語同士の意味領域が離れていて
意外な接続を生むこととして扱う。意味距離だけを最大化すると文脈が壊れるため、
`semantic_relevance`に下限を置き、Pareto選択する。

同一語、同じlemma、同じ活用語尾、同じ助詞列、同じ接尾フィラーには
段階的なduplicate penaltyを付ける。文字列Jaccardだけではなく形態素単位でも
測る。

## 候補探索

### 索引

辞書・候補句を次のキーで索引する。

```text
reversed_vowel_N_signature
final_moras
mora_length
lemma
POS sequence
semantic tags or embedding
register
OOV/confidence
```

探索順:

1. 完全suffix bucketを取得する。
2. 長さ±1、近似母音、特殊モーラ差へ広げる。
3. BK-tree、VP-tree、または特徴vector ANNで近傍を得る。
4. suffix alignmentで再順位付けする。
5. テーマ、品詞、自然さ、personaで絞る。
6. 音、意味、自然さ、創造性のPareto候補を残す。

単語だけで不足するときは1〜3形態素のphraseを品詞制約下で組み立てる。
助詞や`だぜ/だね/だけ`等を追加して点を稼ぐ候補にはフィラーpenaltyを付ける。

## 説明可能な出力

推奨JSON:

```json
{
  "pair": ["未来", "芝居"],
  "pronunciations": ["mi-ra-i", "shi-ba-i"],
  "domains": ["i-a-i", "i-a-i"],
  "alignment": [
    {"left":"i","right":"i","type":"exact"},
    {"left":"a","right":"a","type":"exact"},
    {"left":"i","right":"i","type":"exact"}
  ],
  "sound_score": 0.86,
  "lyric_score": 0.71,
  "components": {},
  "pronunciation_sources": [],
  "warnings": [],
  "needs_review": false
}
```

説明文では「何モーラ」「どの位置」「完全か近似か」「どの発音候補を採用したか」
「同一語尾減点があるか」を示す。

## 誤検出と過剰最適化

### 誤検出

- 同じ文法語尾の反復を高品質韻と判定する。
- 同じ単語や同音語を創造的な韻と判定する。
- 母音無声化を一律削除し、異なる基底列を同一視する。
- 近似母音の置換を安くしすぎ、無関係な語を結ぶ。
- 自由なlocal alignmentが内部gapを大量に作る。
- 子音を重視しすぎ、日本語の母音韻を落とす。
- 子音を完全に無視し、硬さの差を説明できない。
- 文字数をモーラ数として拗音・長音を誤る。
- 拍位置がないのに偶然反復を強い韻とする。
- 低信頼OOV読みでのみ成立する韻を確定する。

### 過剰最適化

- 接尾語、助詞、フィラーを水増しする。
- 倒置と省略を重ね、日本語が不自然になる。
- 希少な固有名詞や未知語を詰め込む。
- 音列を反復してメッセージを失う。
- embeddingに近い一般的テーマ語へcollapseする。
- reward最大化で同型句を反復する。
- 過去98曲等の限定コーパスを全時代・全スタイルの絶対則にする。
- 実在歌詞を記憶・再生成し、既存作品へ過度に近づく。

生成物には既存歌詞との長いn-gram一致、固有表現の連続一致、極端な意味類似を
監査する。学習・例示には辞書、音韻規則、許諾済み素材、自作例を優先する。

## 評価仕様

### Golden set

日本語母語話者かつラップの韻に通じた注釈者2名以上で、次を注釈する。

- 実際の読み
- モーラ列
- 韻ドメイン
- 韻の有無
- 音の強さ
- 自然さ
- 創造性
- 小節・強拍位置

主観的不一致を消さず、注釈者別ラベルと合意値を保存する。

### 必須カテゴリ

- 完全韻
- 近似韻
- 非韻
- 同一語の自明一致
- 同じ接尾辞の自明一致
- 周辺1モーラ不一致
- 無声化を仮定した一致
- 長母音候補による一致
- N/Q/R一致・不一致
- 英語コードスイッチ
- 内部韻
- 循環的連鎖韻

### 指標

- 韻有無: precision、recall、F1
- 人間の品質順位との一致: Spearman、Kendall
- スコアcalibration
- 発音候補のtop-1/top-k精度
- OOV、方言、コードスイッチ別error

ablation:

- 基底発音のみ vs 実現候補あり
- 母音のみ vs 子音特徴あり
- duplicate penaltyなし/あり
- 位置情報なし/あり
- strict mora vs nucleus-only

最終評価にはテキストだけでなく、同一ビート上での音声A/Bを含める。

## 出典

- **A1** Shigeto Kawahara, “Half Rhymes in Japanese Rap Lyrics and
  Knowledge of Similarity”:
  https://user.keio.ac.jp/~kawahara/pdf/JEAL16_kawahara.pdf
- **C1** Shigeto Kawahara, “A Faithfulness Ranking Projective from a
  Perceptibility Scale: Correspondence in Japanese Hip-Hop Rhymes”:
  https://user.keio.ac.jp/~kawahara/pdf/hiphop_prose.pdf
- **C2** 川原繁人、日本語ラップの韻に関する概説:
  https://user.keio.ac.jp/~kawahara/pdf/rap2017.pdf
- **C3** 小川・川原、2026年言語処理学会予稿、語末重み付き編集距離と
  rhyme reward:
  https://www.anlp.jp/proceedings/annual_meeting/2026/pdf_dir/P9-3.pdf
- **C4** DEIM 2019、音韻条件緩和・品詞・意味関連を組み合わせた韻候補生成:
  https://db-event.jpn.org/deim2019/post/papers/236.pdf
- **C5** “Japanese Rhyme Generation Based on Mora Similarity”
  （2025年Springer章、アクセス制限の可能性あり）:
  https://dl.acm.org/doi/10.1007/978-3-032-11976-6_7

