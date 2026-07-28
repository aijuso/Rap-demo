# Suno production handoff for Japanese rap

Use this reference after the lyric has passed the writing and audit workflow. It converts the
finished text into a copy-ready production brief without pretending that text metatags provide
deterministic arrangement control.

## Table of contents

- Evidence levels
- Output contract
- Derive tempo and flow
- Design the global sound
- Write Styles
- Write Exclude
- Build metatagged Lyrics
- Protect Japanese pronunciation
- Recommend generation settings
- Test adherence
- Output template

## Evidence levels

Keep three kinds of control separate:

1. **Official field behavior:** Custom Mode accepts user Lyrics, Styles, and Advanced options.
   Exclude is an official negative-control field. V4.5 documentation explicitly supports adding
   more song context in Lyrics while keeping genre information in Styles.
   [src:suno-custom-mode] [src:suno-better-lyrics-prompts] [src:suno-exclude]
2. **Community-observed convention:** tags such as `[Intro]`, `[Verse]`, `[Hook]`, `[Break]`,
   `[Outro]`, `[End]`, and `[pause for a beat]` are widely used as local structure hints.
   [src:suno-jp-metatags]
3. **Inference for this lyric:** exact BPM, key, subdivision, vocal register, and arrangement are
   design recommendations derived from the text. They remain provisional until audio exists.

Never describe a community tag as a guaranteed command. Generation is stochastic and a tag may be
ignored, blended with another section, or interpreted musically rather than literally.

## Output contract

For a complete Suno-targeted song, return:

1. `Production specification`;
2. `Rhyme and flow map`;
3. `Styles`;
4. `Exclude`;
5. `Lyrics with metatags`;
6. `Generation settings`;
7. `Adherence test and repair path`.

Make each of the three input fields independently copyable. Do not mix explanatory prose into the
copy blocks.

## Derive tempo and flow

Count performed morae per bar when readings are reliable. For each section, report:

```yaml
bars:
role:
mora_range:
entry: downbeat | pickup | delayed
subdivision: eighth | sixteenth | triplet | mixed
density: low | medium | high
pocket: ahead | on-beat | behind
rests:
breath:
important_landings:
rhyme_domains:
```

Choose BPM by balancing:

- intelligibility of the densest bar;
- intended emotional pressure;
- space needed for consonants and particles;
- contrast between hook and verse;
- live feasibility versus a comped studio take.

If the original target makes the densest bar rush, lower BPM or redesign the line. Do not fix an
overloaded lyric only by labeling it `rapid rap`. Report both the artistic target and the practical
generation BPM when they differ.

## Design the global sound

Specify:

- meter;
- key or key feel;
- genre and era;
- drum character and snare location;
- swing or straight feel;
- bass;
- harmonic instrument;
- texture or environmental sound;
- vocal gender only when relevant;
- register, mic distance, dryness, articulation, timing, and emotional restraint;
- verse melodic treatment;
- hook melodic treatment;
- arrangement and density contour;
- transition before the final hook;
- ending behavior.

Every choice must support the lyric. A nocturnal reflective verse may justify a minor key, dry
close vocal, and sparse harmony; those are not universal rap defaults.

## Write Styles

Use Styles for global behavior. Prefer one coherent paragraph in compact English because model
interfaces often respond well to dense attribute phrases. Include only compatible instructions.

Recommended order:

```text
genre and era, BPM, meter, key feel, mood.
drums, bass, harmony, texture.
vocal identity, register, articulation, timing, melodic restraint.
section density contour, transition, ending.
```

When the interface character limit is known, count characters with a deterministic tool. Keep a
margin for later edits. Do not claim the text fits merely by visual inspection.

Avoid:

- artist-name imitation;
- mutually exclusive genres without a structural reason;
- repeated synonyms that consume the limit;
- negative instructions that belong in Exclude;
- exact section-by-section lyric directions better placed in Lyrics.

## Write Exclude

Use Exclude for global unwanted elements, especially accidental genre drift or vocal behavior.
[src:suno-exclude]

Group only relevant risks:

```text
unwanted vocal gender or ensemble, pop singing behavior, unwanted genres,
unwanted instruments, melisma or vibrato, shouting, excessive tuning,
excessive reverb, dense ad-libs, unwanted emotional framing
```

Do not negate required elements. Do not stuff Exclude with every imaginable genre.

## Build metatagged Lyrics

Use basic structural tags as the stable layer:

```text
[Intro]
[Verse 1]
[Hook]
[Break]
[Bridge]
[Final Hook]
[Outro]
[End]
```

Add at most one concise local instruction to a section header when it materially differs:

```text
[Verse 1 - restrained spoken rap, medium-density sixteenths, behind the beat]
[Verse 1B - brief triplet burst, tight diction, same voice]
[Hook - half-spoken, wider phrasing, sparse drums]
[pause for a beat]
```

Use English inside tags and keep the lyric itself in Japanese. Prefer descriptors over commands.
Do not add a unique compound tag to every line. Too many local instructions can fragment the song
or compete with the global style.

Place:

- tempo, meter, key, main genre, instrument palette, and global voice in Styles;
- unwanted global behavior in Exclude;
- section identity, local density, one-off pause, breakdown, and ending in Lyrics.

Treat exact `[BPM...]`, chord, instrument-solo, capitalization, and obscure tag chains as
low-confidence community controls. Use them only for a deliberate A/B test, never as the sole
control. The community reference itself notes that tags can be ignored.
[src:suno-jp-metatags] [src:suno-jp-prompts]

## Protect Japanese pronunciation

Inspect:

- Latin initialisms;
- product names;
- uncommon compounds;
- names and place names;
- numerals;
- words whose intended performed reading differs from the default.

For a risky word, prefer replacing the surface form directly with kana in the generation copy,
while preserving the clean literary version separately. Avoid isolated parenthetical readings:
parentheses are commonly interpreted as backing vocals or ad-libs. [src:suno-jp-metatags]

Do not convert all kanji to kana by default. Preserve readability and change only high-risk spans.

## Recommend generation settings

If creative sliders are available:

- explain that Weirdness `50%` is documented as the normal expected result;
- recommend lower Weirdness when structure, pronunciation, and restraint matter;
- recommend stronger Style Influence when adherence matters;
- label numerical starting points as heuristics, not official optimums.

[src:suno-creative-sliders]

Do not hardcode a current model name without checking the current official interface or
documentation. Product models and limits change.

## Test adherence

Suno output cannot be validated without generating audio. Propose an A/B test:

- `A`: detailed section headers;
- `B`: basic structural tags only;
- hold Styles, Exclude, lyric wording, and generation settings constant;
- generate at least two takes per condition.

Score:

1. section boundaries;
2. verse non-melodic restraint;
3. requested subdivision switch;
4. pause or breakdown;
5. hook contrast;
6. pronunciation;
7. ending without unwanted continuation.

If one section fails, repair only that section with the available editor or replacement workflow.
If the same failure appears across all sections, revise Styles or Exclude. If only condition A
fails, simplify the local tags.

## Output template

````markdown
## Production specification

| Field | Design | Reason |
|---|---|---|
| BPM | | |
| Meter | | |
| Key / key feel | | |
| Groove | | |
| Snare | | |
| Vocal | | |
| Verse | | |
| Hook | | |
| Density contour | | |
| Instrumentation | | |

## Rhyme and flow map

| Bars | Mora load | Entry / subdivision | Pocket / breath | Rhyme evidence |
|---|---:|---|---|---|

## Styles

```text
...
```

## Exclude

```text
...
```

## Lyrics

```text
[Intro - ...]
...
[End]
```

## Generation settings and verification

- model: verify current availability
- Weirdness:
- Style Influence:
- unverified:
- A/B test:
- smallest repair:
```
````
