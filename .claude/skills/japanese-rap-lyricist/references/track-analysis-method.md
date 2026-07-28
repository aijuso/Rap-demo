# Track and word analysis method

## Contents

1. Purpose and evidence policy
2. Three analysis levels
3. Token-by-token procedure
4. Bar and section procedure
5. Rhyme and humor tracing
6. Commercial-work boundary
7. Worked original example
8. Quality controls

## Purpose and evidence policy

Analyze what each word does, not merely what a line appears to say. Keep three columns mentally
separate:

- **observed**: spelling, supplied reading, repetition, position, grammar, visible reference;
- **inferred**: contextual sense, connotation, comic mechanism, narrative intention;
- **unknown**: performed pronunciation, accent prominence, pocket, audience recognition, authorial
  intention.

Every interpretive claim needs a short reason. A label without evidence is not analysis. Do not
turn an interpretation into a fact merely because it sounds plausible.

Use `assets/word-analysis.schema.json` as the exchange format. Run:

```bash
python3 scripts/analyze_words.py analysis.json
```

The script validates coverage and summarizes annotations. It cannot decide the correct dictionary
sense, joke, referent, or artistic value.

## Three analysis levels

### Token level

Segment particles, auxiliaries, compounds, contractions, English insertions, names, and
onomatopoeia according to their performed function. A dictionary tokenizer is a starting point;
it is not authoritative for split rhymes or deliberately shifted word boundaries.

For every token record:

| Field | Question |
|---|---|
| `surface` | What exact form appears in the permitted source text? |
| `normalized` | What comparison form removes harmless orthographic variation? |
| `reading` | How is it actually performed? |
| `morae` | What mora sequence is heard, including ン, ッ, and long vowels? |
| `literal_sense` | What is the narrow dictionary-level sense here? |
| `contextual_sense` | What does it mean in this sentence and persona? |
| `connotation` | What social, emotional, comic, or cultural associations are activated? |
| `referent` | Which person, object, event, text, or brand is meant? |
| `part_of_speech` | What grammatical category is functioning here? |
| `syntax_role` | Topic, subject, object, modifier, predicate, connective, aside, and so on? |
| `register` | Formal, colloquial, dialectal, bureaucratic, childish, technical, vulgar? |
| `semantic_domain` | Money, food, labor, body, media, bureaucracy, family, status, and so on? |
| `concreteness` | Can the audience picture or sense it, from 0 to 1? |
| `sound_role` | Alliteration, consonance, vowel color, percussive onset, held vowel, filler? |
| `rhyme_role` | Family, domain boundary, anchor, bridge, echo, decoy, or none? |
| `humor_role` | Setup, expectation cue, incongruous intruder, reveal, callback, or none? |
| `narrative_role` | Fact, motive, obstacle, turn, consequence, character detail, or none? |
| `prominence` | Background, normal, accented, held, or adjacent to a meaningful rest? |
| `confidence` | How secure is the annotation? |
| `evidence` | Which grammar, context, audio cue, dictionary, or source supports it? |

Do not force a token to have a rhyme or humor role. `none` is useful information.

### Bar level

For each bar record:

- a fresh paraphrase rather than synonym replacement;
- the bar's structural function;
- the new information introduced;
- dominant emotion and sensory image;
- ambiguity and possible alternative parses;
- rhyme-domain boundaries and their placement;
- relationship to setup, payoff, callback, or transition;
- flow observations, inferences, and audio-dependent unknowns.

Test the bar without its rhyme words. If its proposition becomes empty, the rhyme is concealing a
writing problem.

### Section level

Map:

- proposition, pressure, turn, and residue;
- what the listener knows at each bar;
- escalation and release;
- changes in persona, time, location, addressee, emotional temperature, rhyme family, and flow;
- hook promise versus verse evidence;
- local punchlines versus the lasting whole-section meaning.

At every four-bar boundary, require a change in information, emotion, or flow unless deliberate
stasis has a documented purpose.

## Token-by-token procedure

1. Establish the performed reading. Mark names, numbers, slang, elision, and code-switching as
   uncertain until checked.
2. Segment by grammatical and performed function. Preserve cross-token rhyme domains separately.
3. Choose the contextual sense. List a second sense only when the line genuinely activates it.
4. Explain connotation without assuming the whole audience shares specialist knowledge.
5. Assign syntax role. This exposes inverted or AI-like word order selected only for rhyme.
6. Assign semantic and concreteness values. Count an abstract noun grounded by a visible action
   differently from an unsupported slogan.
7. Mark sound role using the performed span, not merely the token boundary.
8. Mark humor and narrative roles, including `expectation cue` and `withheld fact`.
9. Add evidence and confidence. Lower confidence for unsourced wordplay or uncertain references.
10. Reconstruct the bar from the annotations. If they do not explain why the bar is there, revise
    the analysis.

## Bar and section procedure

Build two timelines:

1. **information timeline** — facts and implications newly available to the listener;
2. **sound timeline** — rhyme families, repeated consonants, density, rests, and voice changes.

Then connect them. A meaningful rhyme often joins two concepts, characters, or times; it does not
only match sound. A flow switch should coincide with a semantic or emotional reason often enough
to be legible, but not so mechanically that every turn sounds announced.

## Rhyme and humor tracing

Give every planned rhyme family and joke an id:

```yaml
rhyme:
  id: R2
  spans: [B2:T3-T4, B4:T1-T2]
  relation: phrase_slant
  placement: [internal, cross_bar]
  semantic_link: status-display versus account-display
humor:
  id: H1
  setup_bar: 1
  expectation: a sponsor signals success
  payoff_bar: 2
  violation: the sponsor is a supermarket discount sticker
  target: the speaker's own performance of status
  timing: short pause before the reveal
```

Use ids to detect orphan setups, unsupported payoffs, rhyme-family overuse, and decorative proper
nouns.

## Commercial-work boundary

For user-supplied lyrics or original generated text, token-level `surface` may be retained for the
task. For a commercial work that the user has not supplied:

- do not build or store a substitute lyric transcript;
- omit `surface` and store a paraphrased function map;
- store only short identification spans when legally and analytically necessary;
- record readings and rhyme relations as derived observations without reconstructing adjacent
  lines;
- cite interviews, official descriptions, or scholarship for claims about method;
- separate a listener's analysis from an artist's stated intention.

The purpose is to learn transferable technique, not to create a recoverable lyric corpus.

## Worked original example

Original training line:

> レジ脇、値引きシールが今日だけ俺のスポンサー

Selected token annotations:

| Token | Literal/contextual sense | Grammar | Sound | Humor/narrative |
|---|---|---|---|---|
| レジ脇 | beside the checkout; an ordinary low-status stage | location noun | clipped consonants make a quick scene cut | concrete setting |
| 値引きシール | discount label; evidence of economizing | subject modifier | long-vowel tail can bridge to a later family | expectation cue |
| 今日だけ | only today; limits the fantasy | adverbial | compact rhythmic hinge | weakens the boast before reveal |
| 俺の | belonging to the speaker | possessive | neutral | makes self-deprecation explicit |
| スポンサー | patron/brand sponsor, reinterpreted as the sticker | predicate noun | held final vowel supports deadpan landing | incongruous reveal and status metaphor |

The joke is not “poverty is funny.” The setup borrows the prestige register of sponsorship; the
payoff assigns that role to a mundane object, while the speaker remains the target. A delivery map
should leave a short space before `スポンサー`. A second bar must develop the situation rather than
merely find another word with the same ending.

## Quality controls

Reject an analysis when:

- it paraphrases a line but never explains individual word choices;
- every noun is labeled a punchline or rhyme anchor;
- pronunciation and accent claims lack audio or a reading source;
- a proper noun is treated as self-evidently funny;
- the interpretation depends on biography or intent that was not sourced;
- commercial text is copied into the dataset;
- technical labels do not lead to a reproducible drafting or revision decision.
