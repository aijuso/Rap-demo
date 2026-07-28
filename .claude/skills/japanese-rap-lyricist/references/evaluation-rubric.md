# Evaluation rubric for Japanese rap lyrics

Use this after a complete draft and, whenever possible, a provisional recording.
The rubric prevents dense rhyme or polished formatting from hiding weak
language, incoherence, plagiarism risk, or unperformable delivery.

## Table of contents

- Evaluation order
- Hard gates and score caps
- Declare the intended mode
- Weighted score: 100 points
- Category tests
- Low-quality examples that must not score high
- Strict audit procedure
- Revision decision

## Evaluation order

Run evaluation in this order:

1. hard gates;
2. mode and brief compliance;
3. page audit;
4. audio/performance audit;
5. weighted scoring;
6. adversarial review;
7. revision decision.

Never calculate a high numerical score first and then excuse a failed gate.

## Hard gates and score caps

### Gate A: Originality and non-imitation

Fail if the lyric:

- reproduces or closely paraphrases a published line;
- uses a living artist's signature phrase, biography, tag, or clustered
  mannerisms to simulate that artist;
- substitutes names while retaining a recognizable source structure;
- contains a distinctive aphorism that a basic similarity search reveals as
  prior wording.

**Cap:** 0/100 until copied material is removed. For suspicious but unconfirmed
similarity, cap at 49 and require review.

Bonbero describes checking a suspected line online and finding a similar prior
expression:
<https://fnmnl.tv/2022/12/13/149988>

### Gate B: Semantic integrity

Fail if two or more central lines are unintelligible without post-hoc
explanation, or if rhyme changes facts, speaker, tense, or causal relations
accidentally.

**Cap:** 39/100. Sound density cannot compensate.

### Gate C: Performability

Fail if the declared cadence cannot be spoken at the target tempo after two
reasonable takes, or if required breaths repeatedly destroy words and meaning.
If no beat or BPM is available, mark this gate `UNVERIFIED`; do not award full
performance points.

**Cap:** 49/100 for a verified failure; 84/100 while unverified.

Mummy-D emphasizes performance and recording as part of composition:
<https://fika.cinra.net/article/201910-mummyd_kngsh>

### Gate D: Natural Japanese

Fail if forced inversion, particle misuse, unexplained register shifts, or
pronunciation distortion occurs repeatedly and primarily exists to preserve a
rhyme.

**Cap:** 49/100.

### Gate E: Brief and point-of-view integrity

Fail if the output ignores the requested format, changes the intended speaker,
fabricates user biography, or violates explicit content constraints.

**Cap:** 39/100.

### Gate F: Minimum song function

Fail if most lines are interchangeable claims, rhyme lists, or filler and the
draft has no discernible progression, groove design, or formal purpose.

**Cap:** 29/100. A correct number of bars does not pass this gate.

### Gate G: Safety and unsupported accusation

Fail if fictional boasts are presented as real criminal facts about an
identifiable person, or if the draft introduces defamatory specifics not
provided by the user.

**Cap:** 0/100 until removed or clearly fictionalized.

## Declare the intended mode

Score against the chosen goal:

```yaml
composition_mode: meaning-first | rhyme-first | flow-first | hook-first |
  experience-first | story-first | collage
payoff_mode: payoff-dense | groove-first | whole-arc
format: full-song | hook-plus-verse | standalone-verse | 64-bars | exercise
```

Do not penalize a whole-arc verse for lacking constant one-liners, or a
hookless-format exercise for lacking a hook. Evidence for these distinct modes:

- $MOKE OG on whole-track flow:
  <https://www.redbull.com/jp-ja/rasen-12-smokeog>
- FARMHOUSE on whole-verse meaning:
  <https://www.redbull.com/jp-ja/rasen-21-farmhouse>
- Red Bull on the hookless 64 Bars format:
  <https://www.redbull.com/jp-ja/projects/64barsjp-s2/64bars-s2-introduction>

## Weighted score: 100 points

Apply only after gates. Use integers and cite at least one concrete observation
for every category.

| Category | Points | Full-credit evidence |
|---|---:|---|
| Brief, voice, and point of view | 10 | Speaker, listener, setting, register, and constraints remain controlled |
| Semantic progression | 15 | Each section adds scene, evidence, complication, or turn; ending changes the reading |
| Concrete language and imagery | 10 | Specific nouns, verbs, sensory details, and earned recurring images |
| Rhyme and sound architecture | 15 | Audible sound links with semantic value; varied placement and density; no filler |
| Flow and beat relationship | 15 | Intentional entries, subdivisions, pauses, and density contour; beat changes are answered |
| Natural Japanese and clarity | 10 | Syntax and particles remain intelligible by ear; pronunciation is credible |
| Hook or structural payoff | 10 | Hook performs its declared job, or hookless form has an equivalent organizing return |
| Surprise, compression, and punch | 5 | Turns or memorable phrases are earned and concise, not random |
| Performance and breath | 5 | Recorded delivery preserves key words, energy, and breath plan |
| Originality and revision evidence | 5 | No suspicious imitation; weak lines were tested and revised |

### Scoring anchors

- **90–100:** Release-ready in writing and convincing in recorded performance;
  only taste-level edits remain.
- **80–89:** Strong draft; limited repairs to one or two sections.
- **70–79:** Clear identity and several strong passages, but structural or
  performance revision remains.
- **60–69:** Functional demo with visible craft and equally visible filler,
  flatness, or forced lines.
- **40–59:** Partial draft; isolated good sounds or ideas do not cohere.
- **0–39:** Failed brief, copied/imitation-heavy, semantically broken, or mostly
  filler.

Do not use 80 as a default. A draft with no provisional audio cannot exceed 84.
A first draft with no documented revision cannot receive the final 5 points.

## Category tests

### Brief, voice, and point of view

- Underline every pronoun and addressee. Can each referent be recovered?
- Does the speaker know only what the chosen point of view permits?
- Are autobiographical details supplied by the user, or clearly fictional?
- Does word choice belong to one voice rather than a generic "rapper" costume?

宇多丸 discusses grounding a lyric in the affected person's viewpoint and
rewriting explanation as emotional expression:
<https://ikinobirubooks.jp/series/sasaki-tomoko/1998/>

### Semantic progression

Label every two or four bars with its new function. If three consecutive units
all mean "I am good and others are bad," progression fails even if the rhymes
differ.

Acceptable functions include:

- introduce scene;
- provide evidence;
- complicate claim;
- reveal motive;
- change time or scale;
- answer the hook;
- reverse an earlier image;
- land consequence.

### Concrete language and imagery

Calculate:

```text
specificity ratio =
  lines containing an observable action, object, location, sensory detail,
  or verifiable personal fact
  / total lines
```

The ratio is diagnostic, not a universal threshold. If below 0.35, investigate
generic abstraction. Do not reward fake brand names or arbitrary proper nouns
as specificity.

### Rhyme and sound architecture

For every marked rhyme, score:

```text
audibility 0-2
semantic contribution 0-2
naturalness 0-2
placement/payoff 0-2
```

Any rhyme scoring `semantic contribution = 0` or `naturalness = 0` is a repair
candidate, regardless of total rhyme count.

R-指定's discussion of meaning-, rhyme-, and flow-first methods and deliberate
non-rhyme supports evaluating function rather than density:
<https://miyearnzzlabo.com/archives/66634>

Kawahara's phonetic research is the basis for auditing performed sound rather
than orthography:
<https://user.keio.ac.jp/~kawahara/pdf/rap2017.pdf>

### Flow and beat relationship

Check:

- at least one stable pocket is established before variation;
- variation corresponds to meaning, beat development, or section role;
- important words land audibly;
- pauses are composed, not accidental gaps;
- subdivision labels match the heard event rate;
- syntax remains recoverable across bar lines.

Use the practical rhythm vocabulary in:

- <https://plugplus.rittor-music.co.jp/training/series/rap_lesson/lesson01/>
- <https://plugplus.rittor-music.co.jp/training/series/rap_lesson/lesson02/>

### Natural Japanese and clarity

Read once as prose, then listen without text. Deduct when:

- particle relations are ambiguous;
- a predicate arrives too late to recover the clause;
- kanji suggests a rhyme that pronunciation does not;
- a vowel is distorted only to imitate another artist or force a match;
- ornamental English obscures the intended meaning;
- register changes have no character or dramatic reason.

### Hook or structural payoff

For a hook:

- recall after one or two readings;
- clear rhythmic contrast from verse;
- repeatability without semantic exhaustion;
- connection to the song's tension;
- an audible final landing.

For hookless work:

- recurring motif, pocket, image, or argument;
- clear escalation;
- decisive ending or intentional open form.

R-指定 and PUNPEE provide first-person evidence for hook-first discovery:

- <https://www.billboard-japan.com/special/detail/4723>
- <https://eyescream.jp/music/125820/>

### Surprise, compression, and punch

Do not award points for obscurity alone. A successful turn preserves a bridge
between setup and payoff. Ask whether the listener can explain what changed
without being given the author's private reasoning.

AKLO discusses unexpected phrase breaks and last-line revelation:
<https://music.fanplus.co.jp/special/20160607660229aeb>

### Performance and breath

Require a complete take at target tempo. Mark:

- swallowed particles;
- involuntary rushing;
- late landings;
- exhausted phrase endings;
- unclear consonant transitions;
- energy that contradicts section meaning.

Long passages also require a stamina and ad-lib plan. MFS discusses both:
<https://www.redbull.com/jp-ja/rasen-06-mfs>

### Originality and revision evidence

Evidence may include:

- before/after weak-line changes;
- recording notes;
- a revised neighboring line after a cadence change;
- a similarity search for distinctive lines;
- deletion of a rhyme that damaged meaning;
- a four-bar rewrite or full reset.

VIGORMAN describes revising weak recorded sections and their neighboring lines:
<https://www.redbull.com/jp-ja/64bars-vigorman>

CHICO CARLITO describes discarding and rebuilding a 64-bar draft:
<https://www.redbull.com/jp-ja/podcast-episodes/behind-the-bars-japan-red-bull-64-bars-s1-e8>

## Low-quality examples that must not score high

The examples below are invented for evaluation and are not model lyrics.

### Dense end rhyme with no content

```text
未来へ期待　時代を支配
でかい舞台　俺だけ偉大
```

Why it fails:

- each line is a generic claim;
- rhyme supplies nearly all apparent craft;
- no scene, evidence, conflict, or turn;
- the voice could belong to anyone.

Expected result: Gate F fails; maximum 29 even if rhyme audibility is high.

### Forced syntax for rhyme

```text
駅へと向かうを　描くこの夜
```

Why it fails: the particle construction is unnatural and exists to preserve
sound. Expected result: repair immediately; repeated instances fail Gate D and
cap the score at 49.

### Incoherent image pile

```text
冷たい太陽　透明な火山
昨日の未来が宇宙で破産
```

Contradiction or surrealism can work, but unexplained incompatible images are
not automatically deep. If no scene, emotional logic, or later payoff connects
them, Gate B or F applies.

### Formatted but unperformable

A 16-bar page with equal line lengths, many multi-mora rhymes, and no marked
breaths may look complete. If it cannot be delivered at the declared BPM after
reasonable takes, Gate C caps it at 49. Typography is not cadence.

### Generic hook

```text
俺は上へ　まだ上へ
止まらないぜ　ただ上へ
```

Repetition alone does not create a hook. Without a specific tension, image,
rhythmic identity, or consequence, hook points should be low and Gate F may
apply to the full song.

### Unexplained imitation

A technically original lyric that combines a named artist's signature ad-lib,
known biography, favorite repeated phrase, and characteristic self-reference
still fails Gate A. Avoiding verbatim copying is necessary but not sufficient.

## Strict audit procedure

Run four independent passes. Do not let a strong result in one pass erase
another pass's defect.

### Pass 1: Red-team meaning

Paraphrase every two or four bars in plain Japanese. Mark:

- `NEW`: adds information;
- `DEEPEN`: complicates existing information;
- `RETURN`: meaningfully recalls earlier material;
- `FILLER`: restates without new function;
- `BROKEN`: cannot be paraphrased coherently.

Two consecutive `BROKEN` units fail Gate B. Three consecutive `FILLER` units
fail Gate F unless the repetition is the declared hook and works musically.

### Pass 2: Sound-only

Listen without text. Note only what can actually be heard:

- rhyme;
- landing;
- phrasing;
- breath;
- clarity;
- section contrast.

Do not award page-only wordplay.

### Pass 3: Text-only

Read without beat. Check syntax, point of view, scene logic, originality, and
progression. Do not excuse broken language with an imagined delivery.

### Pass 4: Similarity and cliché

Search the most distinctive lines and flag generic rap formulas. Also compare
against any artist named in the prompt at the level of devices and mannerisms,
not just exact strings.

## Revision decision

Choose the smallest adequate intervention:

| Finding | Action |
|---|---|
| One weak word or landing | Replace word and re-record with neighbors |
| One weak line | Rewrite line, then verify adjacent syntax and rhyme |
| Repeated pocket fatigue | Redesign a four-bar unit |
| Weak hook but strong verses | Rewrite hook from the song's strongest image or cadence |
| Strong hook, redundant verses | Assign a distinct scene or argumentative job to each verse |
| Broken POV or concept | Rewrite the section outline before editing lines |
| Multiple gate failures | Full reset from the song contract |

After revision, rerun all gates. A repaired score is not valid if it inherits
the previous pass without fresh evaluation.
