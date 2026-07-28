# 日本語ラップ用G2P・辞書・語彙資源

## 目次

1. [目的](#目的)
2. [推奨構成](#推奨構成)
3. [UniDic](#unidic)
4. [Sudachi](#sudachi)
5. [Open JTalkとpyopenjtalk](#open-jtalkとpyopenjtalk)
6. [JMdictと意味資源](#jmdictと意味資源)
7. [フォールバックと信頼度](#フォールバックと信頼度)
8. [ユーザー発音辞書](#ユーザー発音辞書)
9. [英語・外来語・コードスイッチ](#英語外来語コードスイッチ)
10. [失敗例と防御策](#失敗例と防御策)
11. [API契約](#api契約)
12. [ライセンスと再配布](#ライセンスと再配布)
13. [出典](#出典)

## 目的

表記から一つの「正解発音」を決め打ちするのではなく、複数の発音候補を
出典・信頼度・警告付きで返す。ラップでは辞書発音とdeliveryが異なるため、
G2Pは韻判定の入力候補であり最終真値ではない。

証拠等級:

- **A**: 公式辞書仕様、公式プロジェクト文書、査読論文
- **B**: 公式OSS/API、再現可能な実装
- **C**: 技術ブログ、issue、予稿

## 推奨構成

```text
manual line override
  ↓
user pronunciation dictionary
  ↓
UniDic Contemporary Spoken Japanese
  ↓
UniDic Contemporary Written Japanese
  ↓
Sudachi Full
  ↓
pyopenjtalk G2P
  ↓
rule-only kana parser
```

バックエンドを一つに絞らない。第一候補を返しつつ、異なる候補と不一致理由も
保持する。

## UniDic

### 選択

UniDicを主辞書にする。公式配布には現代書き言葉UniDicと現代話し言葉UniDic
3.1.0があり、ラップでは現代話し言葉版を第一候補にする
（[A1](https://clrd.ninjal.ac.jp/unidic/en/)）。

UniDicは短単位のMeCab辞書で、階層的な語彙素構造を持つ
（[A2](https://clrd.ninjal.ac.jp/unidic/about_unidic.html)）。
表層形だけでなく、語彙素、読み、発音形、品詞、語種、アクセント関連情報を
利用できる。

### 使うフィールド

最低限:

```text
surface
lemma
pos1..pos4
lForm
orth / orthBase
pron / pronBase
kana / kanaBase
goshu
cType / cForm
accent-related fields when available
```

公式マニュアルは`pron`を発音形出現形、`pronBase`を発音形基本形として区別し、
「データ/データー」「ニュース/ニューズ」のような発音変異を扱う
（[A3](https://clrd.ninjal.ac.jp/unidic/UNIDIC_manual.pdf)）。
韻判定には読みだけでなく`pron`を優先し、`pronBase`も候補として保存する。

Pythonではfugashiで構造化フィールドを取得できる
（[B1](https://github.com/polm/fugashi)）。
`UnidicFeatures26`の定義は実装で確認できる
（[B2](https://github.com/polm/fugashi/blob/main/fugashi/fugashi.pyx)）。

### 避ける構成

`unidic-lite`は軽量な開発用には便利だが、公開説明上、古いUniDic 2.1.2由来で
あるため、現行語彙、スラング、固有名詞を扱う本番の唯一の辞書にしない
（[B3](https://pypi.org/project/unidic-lite/)）。

## Sudachi

SudachiはUniDicで未知語または低信頼になった表記のフォールバックに使う。
Morpheme APIから次を得る。

- `reading_form()`
- `normalized_form()`
- `is_oov()`

公式API:
[B4](https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.morpheme.html)

SudachiDictにはSmall/Core/Fullがあり、Fullは雑多な固有名詞を含む
（[B5](https://github.com/WorksApplications/SudachiDict)）。
芸名、地名、新語候補の探索ではFullを選ぶ。ただし辞書にあることは
「演者がその読みで発音する」保証ではない。

推奨:

- UniDicとSudachiが一致: 通常語なら信頼度を上げる。
- 不一致: 両方の候補を返し、文脈選択または確認へ回す。
- Sudachiのみで既知: 固有名詞なら中信頼以下に留める。
- 両方OOV: pyopenjtalkへ進むが、要確認を外さない。

## Open JTalkとpyopenjtalk

Open JTalkは日本語TTSシステムで、公式プロジェクトはBSDライセンス
（[B6](https://open-jtalk.sourceforge.net/)）。
pyopenjtalkはPython wrapperであり、次のG2Pを提供する
（[B7](https://github.com/r9y9/pyopenjtalk)、
[B8](https://github.com/r9y9/pyopenjtalk/blob/master/pyopenjtalk/__init__.py)）。

```python
pyopenjtalk.g2p(text, kana=False, join=True)
pyopenjtalk.g2p(text, kana=True, join=True)
pyopenjtalk.g2p(text, kana=False, join=False)
```

音素出力の読み方:

| 記号 | 意味 | 内部変換 |
|---|---|---|
| `N` | 撥音 | 特殊モーラN |
| `cl` | 促音の閉鎖 | 特殊モーラQ |
| `I` | 無声化した/i/ | nucleus i、`devoiced=true` |
| `U` | 無声化した/u/ | nucleus u、`devoiced=true` |
| `pau` | 休止 | 境界。モーラに数えない |
| `sil` | 無音境界 | 境界。モーラに数えない |

実例を含む解説:
[C1](https://www.ai-shift.co.jp/techblog/2312)

ESPnetも`pyopenjtalk.g2p(text, kana=False)`を利用し、
`drop_unvoiced_vowels`をオプションとして扱う。また、珍しい外来語かなの補正を
実装している
（[B9](https://github.com/espnet/espnet/blob/master/espnet2/text/phoneme_tokenizer.py)）。
したがって大文字I/Uを常に削除せず、基底とsurface候補を分ける。

pyopenjtalkは次に使う。

- UniDicの発音形との照合
- 音素特徴への変換
- 辞書にないかな列の暫定候補
- 無声化候補の生成

次には使わない。

- 人名・当て字の唯一の読み
- 数字・小数の無検証変換
- 英語コードスイッチの唯一の発音
- ラップdeliveryの最終真値

公開issueには数字・未知語・環境依存の問題が記録されている
（[C2](https://github.com/r9y9/pyopenjtalk/issues)）。失敗時だけでなく、
もっともらしい誤読にも備える。

## JMdictと意味資源

JMdictを候補語の見出し、読み、品詞、語義付与に使う。

- 公式プロジェクト:
  [A4](https://www.edrdg.org/jmdict/j_jmdict.html)
- JSON簡略配布:
  [B10](https://github.com/scriptin/jmdict-simplified)

JMdictは次に向く。

- 韻候補の語義表示
- 品詞制約
- 同音異義語の分離
- 英語glossを介したテーマ検索

文脈中の実発音や日本語ラップ固有の縮約をJMdictだけで決めない。
JSON簡略配布のCC-BY-SA 4.0等、利用する配布物ごとのライセンスを確認する。

意味類似候補にはSudachi関連のchiVe等を補助的に利用できる。
配布情報:
[B11](https://registry.opendata.aws/sudachi/)

embeddingは韻の音響判定に混ぜず、テーマ適合と候補の意味距離に使う。

## フォールバックと信頼度

推奨する候補型:

```json
{
  "reading": "エーガ",
  "phonemes": ["e", "e", "g", "a"],
  "moras": ["e", "R", "ga"],
  "source": "unidic-spoken:pron",
  "transformations": ["ei_to_e_long"],
  "confidence": 0.88,
  "warnings": []
}
```

信頼度は根拠の数だけで機械的に決めない。初期ヒューリスティクス:

| 状況 | 初期範囲 |
|---|---:|
| 演者の行単位指定 | 0.98〜1.00 |
| ユーザー辞書完全一致 | 0.95〜0.99 |
| UniDic話し言葉の通常語 | 0.85〜0.95 |
| 複数辞書一致の通常語 | 0.85〜0.95 |
| 長母音等の一般的変異 | 0.70〜0.90 |
| Sudachiのみの固有名 | 0.50〜0.75 |
| pyopenjtalkのみのOOV | 0.35〜0.65 |
| 文字規則のみ | 0.20〜0.50 |

これらは確率校正済みの値ではない。評価セットでcalibrationし、範囲を設定ファイル
へ外出しする。人名、数字、コードスイッチは通常語より上限を低くする。

複数候補が近い場合は、一つへ丸めずtop-kを返す。最終韻スコアは候補組み合わせを
探索し、採用した読みを必ず表示する。

## ユーザー発音辞書

TSV例:

```text
surface	context_regex	reading	phonemes	priority	note
般若	.*	ハンニャ	h a N ny a	100	芸名としての指定
AI	日本語.*	エーアイ	e e a i	90	アルファベット読み
AI	英語.*	ey ay	EY AY	90	英語span
```

要件:

- 完全表記だけでなくcontext条件を持てる。
- かな読みと音素列を別々に上書きできる。
- 適用したrule IDを結果へ残す。
- 全体辞書より行単位overrideを優先する。
- 重複ruleはpriorityと具体性で決め、黙って上書きしない。
- 不正なモーラ列を登録時に検証する。

## 英語・外来語・コードスイッチ

まず言語spanを推定し、曖昧なら複数候補を返す。

```json
{
  "surface": "flow",
  "language_candidates": ["ja-loan", "en"],
  "pronunciation_candidates": [
    {"moras":["fu","ro","R"],"type":"ja-loan"},
    {"phonemes":["F","L","OW"],"type":"en"}
  ]
}
```

原語英語音素を無理に日本語5母音へ潰すと、英語のstress、diphthong、codaを失う。
逆に、常に英語発音とすると、日本語化された「フロー」を誤る。言語別に採点し、
最後に拍位置、末尾音、演者指定を統合する。

英字大文字列は、単語読み、頭字語読み、文字読みを候補にする。`AI`、`MC`、
`DJ`のような高頻度語はユーザー辞書へ登録する。

## 失敗例と防御策

| 失敗 | 防御 |
|---|---|
| 「生」の読みを常に一つにする | 文脈形態素解析＋複数候補 |
| 「は」を/ha/のまま韻比較する | 品詞・辞書発音を使う |
| 「映画」を常に/eiga/または/eːga/にする | 両候補を保持 |
| 大文字I/Uを削除する | 無声化フラグ付き母音として保持 |
| `cl`をノイズとして捨てる | Qモーラへ変換 |
| 小数や年号を無検証で読む | 数値parser＋候補＋警告 |
| 芸名の辞書ヒットを確定読みとする | 固有名上限＋override |
| 英単語を全てカタカナ化する | language spanと原語候補 |
| OOVで例外を投げて候補を失う | rule-only fallback |
| OOVでも警告なしに生成を続ける | `needs_review`を伝播 |
| 複数辞書の不一致を先着順で隠す | 全候補とsourceを保存 |

## API契約

### 入力

```json
{
  "text": "映画みたいな未来",
  "locale": "ja-JP",
  "boundaries": [{"type":"bar_end","char_offset":8}],
  "overrides": [],
  "return_candidates": 5
}
```

### 出力

```json
{
  "surface": "映画みたいな未来",
  "normalized": "映画みたいな未来",
  "tokens": [
    {
      "surface": "映画",
      "lemma": "映画",
      "pos": ["名詞"],
      "pron": "エーガ",
      "pron_base": "エーガ",
      "source": "unidic-spoken",
      "is_oov": false,
      "confidence": 0.9
    }
  ],
  "pronunciation_candidates": [],
  "warnings": [],
  "needs_review": false
}
```

エラーは「解析不能」と「低信頼だが候補あり」を分ける。後者は候補を捨てず、
警告を韻検索結果まで伝播する。

## ライセンスと再配布

- UniDic公式ページはGPL v2、LGPL v2.1、BSDの三重ライセンスを案内する。
  実際に同梱する版のLICENSEを保存・確認する。
- Sudachi/SudachiDictは各公式リポジトリのライセンスを確認する。
- Open JTalkは公式案内上BSD。辞書や音声モデル等、別配布物の条件も個別確認する。
- JMdict派生配布は配布形式により条件が異なる。`jmdict-simplified`は
  CC-BY-SA 4.0の表示を確認する。
- skillへ巨大辞書本体を無断同梱しない。取得手順と版を固定し、帰属を残す。
- 学習用の実在歌詞は辞書とは別問題である。歌詞本文をデータセットへ収録・
  再配布する前に権利処理を確認する。

## 出典

- **A1** UniDic公式ダウンロード・ライセンス:
  https://clrd.ninjal.ac.jp/unidic/en/
- **A2** UniDic概要:
  https://clrd.ninjal.ac.jp/unidic/about_unidic.html
- **A3** UniDic公式マニュアル:
  https://clrd.ninjal.ac.jp/unidic/UNIDIC_manual.pdf
- **A4** JMdict公式:
  https://www.edrdg.org/jmdict/j_jmdict.html
- **B1** fugashi:
  https://github.com/polm/fugashi
- **B2** fugashi UniDic feature定義:
  https://github.com/polm/fugashi/blob/main/fugashi/fugashi.pyx
- **B3** unidic-lite:
  https://pypi.org/project/unidic-lite/
- **B4** SudachiPy Morpheme API:
  https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.morpheme.html
- **B5** SudachiDict:
  https://github.com/WorksApplications/SudachiDict
- **B6** Open JTalk:
  https://open-jtalk.sourceforge.net/
- **B7** pyopenjtalk:
  https://github.com/r9y9/pyopenjtalk
- **B8** pyopenjtalk G2P API実装:
  https://github.com/r9y9/pyopenjtalk/blob/master/pyopenjtalk/__init__.py
- **B9** ESPnet phoneme tokenizer:
  https://github.com/espnet/espnet/blob/master/espnet2/text/phoneme_tokenizer.py
- **B10** jmdict-simplified:
  https://github.com/scriptin/jmdict-simplified
- **B11** Sudachi Open Data:
  https://registry.opendata.aws/sudachi/
- **C1** pyopenjtalk音素出力例:
  https://www.ai-shift.co.jp/techblog/2312
- **C2** pyopenjtalk issue一覧:
  https://github.com/r9y9/pyopenjtalk/issues

