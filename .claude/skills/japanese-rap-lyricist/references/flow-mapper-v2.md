# Flow Mapper

## Contents

1. Scope
2. Inputs and output contract
3. Mapping procedure
4. Density, accents, rests, and duration
5. Repetition and switching
6. Punchline timing
7. Voice and character
8. Verification and audit

## Scope

Design an intentional performance hypothesis for each bar. Do not treat a count of written
characters or morae as flow. Flow emerges from duration, subdivision, grouping, accent, rest,
breath, rhyme landing, voice, and microtiming against a beat.

Use `assets/flow-map.schema.json`. Compile and check a proposal with:

```bash
python3 scripts/flow_map.py flow-input.json
```

The result remains a proposal unless beat and audio performance were reviewed.

## Inputs and output contract

Require or mark unknown:

- BPM, meter, beat or beat description;
- performed reading for every bar;
- bar boundaries and pickups;
- persona and intended emotional temperature;
- bar function and planned punchline locations.

Return for every bar:

- subdivision: eighth, sixteenth, triplet, or mixed;
- performed mora count and density label;
- accent locations and rhyme landings;
- rests and their duration;
- held vowels or consonant closures;
- breath before or after;
- repeated rhythmic cell and repetition count;
- flow-change instruction;
- pre-punch silence;
- voice, character, volume, and articulation;
- confidence and unknowns.

## Mapping procedure

1. Mark strong beat positions and plausible pickups.
2. Write the performed reading, including contractions and stretched vowels.
3. Group morae into spoken chunks. Do not distribute one mora per slot mechanically.
4. Place meaning-bearing words before decorative sounds.
5. Mark the primary accent or landing of each chunk.
6. Insert rests for syntax, contrast, breath, or expectation; never as random emptiness.
7. Identify the densest burst and ensure adjacent recovery space.
8. Choose a repeated rhythmic cell and state why repetition helps recall or character.
9. Switch only when information, emotion, perspective, or comic timing gives it a job.
10. Record what must be tested aloud.

## Density, accents, rests, and duration

Use density relatively within the section:

- `sparse`: space and held duration carry authority, tension, or deadpan;
- `medium`: conversational intelligibility;
- `dense`: compressed information with controlled articulation;
- `burst`: a short contrast, not the default condition.

Mora count is diagnostic, not a capacity law. Long vowels, ン, ッ, devoiced vowels, English
clusters, swing, and deliberate compression change perceived load.

Mark accents with both position and reason:

```yaml
accents:
  - location: beat_2_and
    span: "値引き"
    reason: "concrete clue"
```

A rest must name its function: breath, syntactic boundary, suspense, embarrassment, character
switch, beat exposure, or hook participation.

## Repetition and switching

Repeat a rhythmic cell long enough to establish a prediction. Common choices:

- two repetitions followed by variation;
- three repetitions followed by a shortened or silent fourth;
- stable verse cell broken at the narrative turn;
- one character with clipped cells and another with legato cells.

Record both `repeat_pattern` and `switch`. “Change the flow here” is not sufficient. Specify what
changes: subdivision, onset, density, grouping, landing, breath, pitch range, timbre, or persona.

## Punchline timing

For each payoff, map:

1. last expectation-building word;
2. silence or held sound before reveal;
3. reveal span;
4. beat position of the reveal;
5. post-reveal space, tag, or immediate continuation;
6. voice and facial/attitudinal equivalent.

Do not place every punchline at the bar end. Test internal reveal, delayed cross-bar reveal,
underplayed downbeat, offbeat interruption, and callback in a later section.

## Voice and character

Voice is part of the map:

- narrator versus quoted character;
- confident surface versus anxious aside;
- deadpan, mock-serious, bureaucratic, childish, overheard, or muttered register;
- call-and-response and deliberate misunderstanding;
- ad-lib as a second perspective, not generic decoration.

When multiple characters speak, label who knows which information. A recognition gap can create
both narrative tension and humor.

## Verification and audit

Text-only checks can verify:

- all bars have readings and explicit directives;
- density contrast exists;
- breath points are not missing;
- a punchline has planned timing;
- repeated cells and switch points are documented.

Only recorded-on-beat audio can support claims about:

- pocket and microtiming;
- natural accent realization;
- articulation at the chosen BPM;
- whether rests feel tense or empty;
- whether a voice change is legible;
- live breath and stamina.

The deterministic `flow_map.py` never self-promotes to `audio_verified`. A host must actually open
the beat and recorded take, write `assets/audio-review.schema.json`, and run
`scripts/validate_audio_review.py` so the bar findings are bound to exact flow-map, beat, and audio
hashes. Hash integrity does not prove the reviewer's artistic judgment; preserve reviewer,
evidence, and unresolved bars.

Run at least three takes: neutral, exaggerated, and underplayed. Preserve the version whose
meaning and character remain clear, then revise text and map together.
