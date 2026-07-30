---
name: japanese-rap-lyricist
description: Orchestrate research-grounded creation, analysis, revision, and adversarial evaluation of original Japanese rap lyrics. Use for Japanese rap lyrics, hooks, verses, rhyme graphs, every-word semantic annotation, mora-based rhyme analysis, humor and punchline design, beat-aware flow maps, artist-reference abstraction, professional audits, or Suno-ready production handoffs.
---

# Japanese Rap Lyricist

Create performed Japanese rap through separate evidence-bearing specialist stages. Never infer
quality from rhyme density, vocabulary rarity, named references, or a self-awarded score.

## Non-negotiable rules

- No black-box runs: a substantive `create` or `rewrite` must pass the user checkpoints
  (CP1 intake loop, CP2 keywords, CP3 rhyme bank, CP4 draft) unless the user explicitly
  delegated the whole run. A finished lyric the user never steered is a failed run, not a
  convenience.
- Preserve meaning, natural Japanese, speaker truth, and performability before technique density.
- Treat text, reading, mora, accent, beat placement, and recorded delivery as different evidence.
- Label every important claim `observed`, `inferred`, `proposed`, or `unknown`.
- Never call flow, pocket, accent, or breath verified without relevant audio.
- Never fabricate hardship, crime, illness, dialect, biography, or cultural identity.
- Convert named-artist requests into anonymous techniques before drafting.
- Do not store, reconstruct, or imitate commercial lyrics. Analyze them through derived functions,
  interviews, scholarship, and brief lawful identification spans.
- Apply hard gates before scores. A failed gate cannot be compensated by dense rhyme.

## Host execution: Claude Code first

Claude Code is the primary host. Map the workflow onto Claude Code capabilities directly:

- **Subagents**: run each specialist role as a Task-tool subagent. Spawn independent roles
  (Narrative, Vocabulary, Humor, Rhyme, Flow) in parallel in a single turn. Give each subagent
  the frozen brief, only its permitted references, and exactly one writable output path.
- **Blind audit**: spawn the Professional Auditor as a fresh subagent that receives only the
  brief, the artifacts, and the audit rubric — never the Integrator's conversation, self-score,
  or justification. This is what makes audit independence `full` instead of `partial`.
- **Scripts**: run every `scripts/*.py` command through the Bash tool with `python3`. Core
  scripts use only the Python 3.10+ standard library; `pyopenjtalk` and `fugashi`/UniDic are
  optional pronunciation backends — degrade to manual readings with warnings when absent.
- **Stage tracking**: mirror the orchestration stages (reference → parallel specialists →
  integration → audit → repair → reaudit) in the TodoList so no gate is skipped.
- **Working files**: keep all run artifacts under a local `run/` directory in the project
  workspace; resolve skill paths relative to this `SKILL.md`.
- **HTML deliverables**: generate `run/research_keywords.html` and `run/rhyme_bank.html` with
  the `scripts/render_*_html.py` renderers and attach them in chat with SendUserFile
  (`display: render`). In-loop direction choices during CP1 use AskUserQuestion.
- Keep host tool names, session ids, absolute run paths, and model names out of artifacts.

Ready-to-install Claude Code subagent definitions are in [agents/claude-code/](agents/claude-code/)
— copy them into the project's `.claude/agents/` to make the blind-audit roles first-class.

If subagents are unavailable (plain claude.ai chat, single-context hosts), fall back to the
sequential pseudo-separation protocol and mark audit independence `partial`.

Read [subagent-contracts.md](references/subagent-contracts.md) for the portable artifact protocol,
role contracts, concurrency, conflict resolution, the Claude Code adapter, the legacy
Codex/ChatGPT adapter, and the single-agent fallback.

## Route the request

Select one or more modes:

- `create`: original hook, verse, or full song;
- `analyze`: semantic, grammatical, narrative, sound, humor, and flow analysis;
- `rewrite`: preserve declared content while repairing selected layers;
- `rhyme-bank`: context-filtered rhyme graph, not a flat ending list;
- `flow-map`: density, subdivision, accents, rests, duration, breath, voice, and switches;
- `audit`: independent hard gates, evidence, diagnostics, repair instructions, and score caps;
- `teach`: original demonstrations and exercises without commercial lyric reproduction;
- `production`: recording or Suno handoff after lyric reaudit.

Intake questions and all further user interaction follow the checkpoint protocol below. Use
restrained defaults only for gaps the user has explicitly delegated; mark missing performance
data unknown.

## User checkpoints — no black-box runs

Substantive `create` and `rewrite` runs are collaborative by default. Never jump from a thin
request straight to a finished, audited lyric: the user must see and steer the direction while
it can still be changed cheaply. Pause at each checkpoint, present a compact human-readable
summary in the conversation (never raw JSON), and wait for the user's reply before continuing.

Interaction modes:

- `collaborative` (default): every mandatory checkpoint stops and waits for the user.
- `autonomous`: only when the user explicitly delegates the whole run ("お任せ", "全部任せる",
  "確認不要で最後まで"). Record `interaction_mode: autonomous` in the brief assumptions, still
  announce each stage transition in one line, and still deliver the CP1 summary (without
  blocking) so the user can interrupt early.
- A reply like "続けて" or "OK" at a checkpoint approves the current proposal only. It is not a
  standing delegation for the remaining checkpoints.

### CP1 — Intake as a conversation ⇄ scout-research loop (mandatory)

CP1 is not a single summary-and-approve exchange. It is a loop in which every user choice
triggers a light research pass that makes the next round of options more concrete:

1. Take the user's input (theme, wish, fragment — e.g. "ドラえもんをテーマにしたい").
2. Spawn `rap-theme-researcher` in **scout mode** with the brief fields filled so far. It runs a
   handful of web searches and returns 3–5 concrete angles for "what could this theme × this
   direction become", each with a one-line premise, 2–3 usable motifs, and sources
   (artifact: `run/scout_research_<round>.json`, validated by `scripts/validate_bank.py`).
3. Present the angles as options with AskUserQuestion (e.g. ドラえもん → 社会風刺／ノスタルジー／
   キャラ視点…).
4. Record the choice in the brief, deepen the focus, and loop: the next scout round searches the
   narrowed intersection (e.g. ドラえもん×社会風刺 → propose "ひみつ道具で社会を直す" style
   concepts).

Every round, show the required-field checklist with filled/open state:
`テーマ / コンセプト / 物語・場面 / 話者 / トーン / 構成・尺 / 用途` — each marked ✓ or □.
Concept selection happens inside this loop (there is no separate concept checkpoint). When the
concept is chosen and every required field is filled, present the complete brief in one bullet
list and freeze it on approval. If the brief changes later, return here, re-freeze, and mark
downstream artifacts stale.

### Stage R — Deep theme research (after freeze)

Spawn `rap-theme-researcher` in **deep mode**: it sweeps the web across the eight vocabulary
windows (物・動作・場所・時刻/数字・音・身体・制度/金銭・関係) seeded with the motifs the user
chose during scouting, attaches readings and vowel/consonant skeletons via `scripts/skeleton.py`,
writes `run/research_bank.json` (schema `assets/research-bank.schema.json`), and renders
`run/research_keywords.html` with `scripts/render_research_html.py`.

### CP2 — Keyword selection (mandatory)

Attach `run/research_keywords.html` in chat with SendUserFile (`display: render`). The user
checks rows and replies with the copied ID list (or free text) to pick ~20 important words and
add any of their own. Record the result as `selected_keywords` in the brief.

### Stage K — Rhyme bank

Spawn `rap-rhyme-banker`: for every selected keyword it generates 20+ candidates covering all
rhyme types without omission — assonance, consonance (matched via consonant skeletons like
カタカタ→`ktkt`), alliteration, multimora, phrase/mosaic, and internal/initial/cross-bar
placement proposals — scores each with `scripts/rhyme_score.py` in all three modes
(`--mode vowel|consonant|balanced`), writes `run/rhyme_bank.json` (validated with type minimums
by `scripts/validate_bank.py`), and renders `run/rhyme_bank.html`.

### CP3 — Rhyme bank review (mandatory)

Attach `run/rhyme_bank.html` the same way. The user marks favourite pairs, rejects weak ones, or
asks for more of a type. Record the result as `selected_rhyme_pairs` in the brief.

### Stage D — Draft integration

The orchestrator (parent context) runs the remaining specialist roles (Narrative, Humor, Flow)
and integrates the selected keywords and rhyme pairs into a draft.

### CP4 — Draft proposal (mandatory)

Present the draft as a proposal — "こんなドラフトはどうか" — noting which selected keywords and
rhyme pairs each section uses, plus any bars you are unsure about. Invite section- or line-level
feedback (keep / rewrite / drop). Run the blind audit only after the user has reacted or
explicitly skipped review. When both `conservative` and `experimental` drafts exist, show both.

### CP5 — Repair alignment

After the audit, translate the issues (max 5) into plain language with the proposed repair for
each, and let the user decide per issue: apply, accept as-is, or override with their own fix.
Reaudit after repairs as usual. Score changes are reported with their evidence.

### Between checkpoints

- Announce each stage transition in one line with a concrete result
  ("韻バンク完成: 18語×平均23候補、子音韻は全語3件以上").
- Keep artifacts under `run/` and reference them by path; do not dump JSON into chat. HTML
  deliverables are attached with SendUserFile (`display: render`); in-loop options use
  AskUserQuestion.
- Mirror checkpoint status in the TodoList together with the orchestration stages so no
  checkpoint is silently skipped.

`analyze`, `rhyme-bank`, `flow-map`, `audit`, and `teach` need CP1 only when the request is
ambiguous; a small, clearly scoped request may proceed directly. `production` requires a CP4-style
confirmation of the final lyric before the handoff is generated.

## Load the minimum complete reference set

Read every selected file fully.

| Need | Required references |
|---|---|
| orchestration or substantive creation | [subagent-contracts.md](references/subagent-contracts.md), [lyric-writing-workflows.md](references/lyric-writing-workflows.md), [technique-mixer.md](references/technique-mixer.md) |
| every-word or track analysis | [track-analysis-method.md](references/track-analysis-method.md), [japanese-phonology.md](references/japanese-phonology.md), [copyright-and-originality.md](references/copyright-and-originality.md) |
| vocabulary | [vocabulary-director.md](references/vocabulary-director.md) |
| rhyme, rhyme bank, or rhyme graph | [rhyme-taxonomy-extended.md](references/rhyme-taxonomy-extended.md), [rhyme-scoring.md](references/rhyme-scoring.md), [japanese-phonology.md](references/japanese-phonology.md) |
| humor or punchlines | [humor-engine.md](references/humor-engine.md), [story-punchline-engine.md](references/story-punchline-engine.md) |
| flow or performance | [flow-mapper-v2.md](references/flow-mapper-v2.md), [flow-and-cadence.md](references/flow-and-cadence.md) |
| audit or any final creation pass | [professional-audit-v2.md](references/professional-audit-v2.md), [evaluation-rubric.md](references/evaluation-rubric.md) |
| named references or research report | [artist-techniques-rhyme.md](references/artist-techniques-rhyme.md), [artist-techniques-humor.md](references/artist-techniques-humor.md), [source-ledger.yaml](references/source-ledger.yaml) |
| English/global technique transfer | [japanese-vs-global.md](references/japanese-vs-global.md) |
| reading uncertainty or G2P | [g2p-and-dictionaries.md](references/g2p-and-dictionaries.md) |
| Suno or production deliverable | [suno-production-handoff.md](references/suno-production-handoff.md) |

When a referenced optional research file is unavailable, continue with the remaining technique
modules and mark source analysis partial. Never invent its contents.

## Classify the source before analysis

Choose one:

- `original_prompt`: no pre-existing lyric text;
- `user_supplied_text`: the user supplied the text for this task;
- `original_generated_text`: text produced in this run;
- `commercial_work`: a published work not supplied in full by the user.

For `user_supplied_text`, detailed token and bar analysis may cover the supplied text. Do not add
it to reusable fixtures or references. For `commercial_work`, store only paraphrased bar
functions, derived sound relationships, work metadata, sources, and confidence. Do not assemble a
recoverable transcript through token annotations. Use
`assets/commercial-derived-analysis.schema.json` and route to Derived Technique Analyst plus
Copyright Analysis Auditor rather than Token Semantic Analyst.

## Freeze the shared brief

Create a brief with:

```yaml
schema: japanese-rap-brief/v2
run_id: ""
mode: create
interaction_mode: collaborative
checkpoint_log: []   # e.g. "CP1 round 2: user chose 社会風刺", "CP2: K01,K05,K09 selected"
concept: ""          # the angle fixed during the CP1 loop, e.g. "ひみつ道具で社会を直す"
scout_rounds: []     # per round: focus, angles offered, user choice
selected_keywords: []     # filled at CP2 from research_keywords.html
selected_rhyme_pairs: []  # filled at CP3 from rhyme_bank.html
deliverable: verse
theme: ""
core_message: ""
facts_and_images: []
fiction_or_lived: fictional | lived | mixed
speaker:
  identity: ""
  point_of_view: first
  knowledge_boundary: []
listener: ""
setting: {time: "", place: ""}
tone: []
register: conversational
dialect: {name: none, confidence: high}
bpm: null
meter: 4/4
bars: null
structure: []
rhyme_density: medium
rhyme_methods: []
humor_intensity: none | light | medium | high
explicitness: clean | moderate | explicit
required_words: []
forbidden_words: []
reference_requests: []
reference_traits: []
generation_target: none | suno | other
copyright_input_class: original_prompt
assumptions: []
unknowns: []
```

Hash or otherwise identify the frozen brief. Mark downstream artifacts stale if it changes.
Do not freeze before CP1 approval unless `interaction_mode: autonomous` was explicitly granted.

## Compile the orchestration

For a substantive `create`, `rewrite`, or named-reference request, use separate subagents when the
host provides them — in Claude Code, spawn each role as a Task subagent and launch independent
roles in parallel within a single turn. Compile a deterministic task graph when useful:

```bash
python3 scripts/orchestrate_plan.py brief.json
```

Use these roles:

1. `Reference/Technique Analyst`, only when names or sources are present;
2. `Theme Research Analyst` (`rap-theme-researcher`): scout mode inside the CP1 loop, deep mode
   once after freeze;
3. `Narrative Architect`;
4. `Vocabulary Director`;
5. `Humor Engineer`;
6. `Rhyme Bank Engineer` (`rap-rhyme-banker`), after CP2 keyword selection;
7. `Rhyme Graph Engineer`, consuming the selected rhyme pairs;
8. `Flow Mapper`;
9. `Draft Integrator`;
10. `Adversarial Professional Auditor`;
11. `Repair Owner`;
12. a fresh `Professional Auditor` for reaudit;
13. `Production Director`, only when needed.

Never let parallel agents edit the same file or artifact. Give each role the frozen brief, only
the references it needs, one output path or named fenced block, and the exact contract in
[subagent-contracts.md](references/subagent-contracts.md).

Wrap specialist payloads in the common envelope and validate the final set:

```bash
python3 scripts/artifact_envelope.py wrap payload.json --brief brief.json \
  --schema vocabulary-bank/v2 --run-id RUN --role vocabulary_director \
  --instance-id AGENT --status ready --input brief.json
python3 scripts/artifact_envelope.py validate artifact-1.json artifact-2.json \
  --brief brief.json
```

Validate the raw Reference artifact separately against `reference_brief`. Then run Reference
Sanitizer, remove all names and signatures, and rewrap the anonymous technique vector against
`generation_brief`. Validate downstream artifacts only with `generation_brief`; never mix the two
hash domains in one validation set.

### Parallel phase

After optional reference normalization, run Narrative, Vocabulary, Humor, Rhyme, and Flow in
parallel as first-pass constraints. They propose artifacts, not competing finished verses. Before
Draft Integration, run second-pass reconciliation for Vocabulary↔Rhyme, Narrative↔Humor, and
Rhyme↔Flow. Validate shared ids, readings, bar ranges, setup/payoff links, accepted candidates,
and rejected conflicts. After the draft, remap Flow using the actual words before audit.

If subagents are unavailable, execute the same roles sequentially. Close each role's free
reasoning and pass only its structured artifact forward. Mark audit independence `partial`.

### Reference firewall

Only Reference/Technique Analyst sees artist names. It must:

1. use at least two sources or creators for a transferable technique;
2. distinguish artist statements, third-party interpretation, and listener observation;
3. output operations, conditions, effects, risks, and confidence;
4. remove signature phrases, rare metaphor clusters, biography, ad-libs, and recognizable scene
   order;
5. change at least three of theme, speaker, setting, metaphor domain, rhyme family, and structure;
6. pass only anonymous `reference_traits` to generation roles.

Reference Sanitizer is the sole bridge. All other tasks receive `generation_brief` with
`reference_requests` removed and may depend only on the rewrapped anonymous technique vector.

Use [technique-mixer.md](references/technique-mixer.md). Do not write “R-指定風” or “GADORO風”
into a drafting prompt.

## Build the specialist artifacts

### Narrative Architect

Return proposition, pressure, turn, residue, listener knowledge by bar, section jobs, setup ids,
payoff ids, withheld facts, and a reason for every four-bar change. Read
[story-punchline-engine.md](references/story-punchline-engine.md).

### Vocabulary Director

Build scene packets before rhyme. Search objects, actions, place, time/number, sound, body,
institution/money, and relationships. For every selected word explain:

- literal and contextual sense;
- plain-language meaning, connotation, referent, and ambiguity;
- part of speech, syntax roles, register, and persona fit;
- reading, morae, sound role, particle affordances, and articulation cost;
- semantic domain, concreteness, humor role, narrative role, prominence, evidence, and confidence.

Use [vocabulary-director.md](references/vocabulary-director.md) and
`assets/word-analysis.schema.json`. Do not treat brand names as concrete detail by themselves.
Use `source_policy` values `user_supplied_text`, `original_generated_text`, or `commercial_work`
consistently. In `commercial_work`, do not emit an ordered token list.

### Humor Engineer

Choose a mechanism, target, setup, predicted frame, violated expectation, shared bridge, landing,
timing, character cost, and risk. Support self-deprecation, exaggeration, deadpan, satire,
intelligent treatment of vulgar material, proper-noun collision, setup/payoff, knowledge gap,
foreign-object intrusion, callback, rule of three, bathos, register collision, anti-joke,
misdirection, double meaning, and other documented variants.

A weird word is not a joke. A payoff must transform a recoverable setup. Leave a planned pause,
voice, or rhythmic landing when performance carries the surprise.
Validate character and callback plans against `assets/humor-plan.schema.json`; require original
character provenance when character-driven references are used.

```bash
python3 scripts/validate_humor_plan.py humor-plan.json
```

### Rhyme Graph Engineer

Build nodes with surface, performed reading, morae, vowels, consonant features, accent status,
part of speech, meaning field, frequency band, freshness, proper-noun flag, particles, placement,
articulation cost, source, and confidence.

Build edges with sound relation, matched domain, mora-length difference, accent compatibility,
semantic fit, syntax fit, novelty, transition cost, placement options, and cautions. Classify
sound relation, span, placement, network pattern, and performance transformation independently.

Use:

```bash
python3 scripts/g2p.py --text "対象" --json
python3 scripts/rhyme_score.py "候補A" "候補B" \
  --reading-a "コウホエー" --reading-b "コウホビー" --explain
python3 scripts/rhyme_graph.py candidates.json --threshold 0.48
```

Manual performed readings override automatic readings. Penalize identical words, grammar endings,
invented readings, predictable pairs, semantic forcing, and one-family overuse.

### Flow Mapper

Return subdivision, mora load, density, entry, accents, rests, fast zones, held vowels, breath,
repeated-cell count, switch point, pre-punch silence, voice, character, and narrative reason for
every two or four bars. After drafting, remap actual words bar by bar:

```bash
python3 scripts/flow_map.py flow-input.json
```

Never distribute one mora per slot and call it flow. `flow_map.py` always returns `proposal`
because it cannot listen. To upgrade the artistic audit, the host must open the beat and take,
write `assets/audio-review.schema.json`, bind the review to exact file hashes, and run:

```bash
python3 scripts/validate_audio_review.py audio-review.json \
  --flow-map flow-map.json --beat beat.wav --audio take.wav
```

Hash validation proves file identity, not the correctness of the listening judgment. Keep
unresolved bars unknown.

## Integrate drafts

Wait for all required artifacts. Record conflicts and apply this priority:

1. safety, facts, copyright, and explicit constraints;
2. meaning and causality;
3. speaker voice and natural Japanese;
4. performability and audibility of important words;
5. setup/payoff and section structure;
6. concrete imagery;
7. rhyme, humor, and technique density.

Write at least:

- `conservative`: meaning, voice, and naturalness first;
- `experimental`: strengthen one chosen sound, structure, timing, or humor control.

Trace every bar to vocabulary ids, rhyme edges, humor ids, flow units, and narrative jobs. Do not
use every candidate. Give each bar one primary job. Read aloud during drafting.

Revise in separate passes:

1. meaning and referents;
2. speaker voice and grammar;
3. observable detail;
4. setup, payoff, and section movement;
5. rhyme architecture and sound texture;
6. flow, duration, rest, and breath;
7. hook and recall;
8. originality and reference distance.

Rebuild upstream when local word replacement cannot fix the proposition or flow.

## Analyze every word

For user-supplied or original text, follow [track-analysis-method.md](references/track-analysis-method.md):

1. establish performed reading and confidence;
2. segment by grammatical and performed function;
3. explain literal sense in plain language;
4. explain contextual sense, implication, connotation, referent, and ambiguity;
5. assign part of speech, syntax role, register, and semantic domain;
6. mark concreteness, sound role, rhyme role, humor role, narrative role, and prominence;
7. cite evidence and distinguish observation from inference;
8. reconstruct the bar and section information timeline.

Validate the annotation:

```bash
python3 scripts/analyze_words.py analysis.json
```

Do not force every token to be technical. Particles and neutral words may have `none` roles.

## Run an adversarial audit

The first audit must be separate from drafting. Do not pass the Integrator's self-score or
justification. Read [professional-audit-v2.md](references/professional-audit-v2.md).

Apply hard gates before scoring:

- copyright, imitation, safety, and unsupported biography;
- missing proposition or broken causality;
- unnatural Japanese or rhyme-driven word order;
- brief, speaker, fact, form, or bar-count violation;
- abstract/filler dominance or no song function;
- no meaningful setup/payoff when one is claimed;
- end-rhyme-only architecture on a technical brief;
- invented or unresolved central readings;
- unperformable density when audio establishes failure.

Audit every requested concern:

- rhyme still serves meaning;
- syntax is not mechanically AI-like;
- placements are not limited to line endings;
- one vowel family is not recycled without change;
- abstract runs are grounded;
- every payoff has a recoverable setup;
- proper nouns have semantic or structural utility;
- the text remains interesting when rhyme is removed;
- accent claims have audio evidence;
- every four bars change information, emotion, or flow.

Prepare `assets/audit-evidence.schema.json` and run:

```bash
python3 scripts/professional_audit.py audit-evidence.json
```

The script checks measurable structure and evidence coverage. It does not judge whether a joke is
funny or a line is artistically excellent. Treat its output as deterministic preflight, then use
the evidence-based 100-point rubric in `professional-audit-v2.md`; do not convert the preflight
cap into an artistic score.

### Repair and reaudit

Return no more than five prioritized issues with bar ids, root cause, evidence, required change,
must-preserve elements, acceptance test, and collateral checks. Repair only failed layers. Then
use a fresh auditor or fresh evaluation context and repeat all gates.

Stop local repair and rebuild Narrative, Vocabulary, or Flow when the same critical gate fails
twice. After three rounds, report residual risk rather than calling the result complete.

## Production handoff

For a completed song intended for generation or recording, read
[suno-production-handoff.md](references/suno-production-handoff.md). Derive BPM, meter, key feel,
groove, vocal profile, section density, arrangement, `Styles`, `Exclude`, and metatagged `Lyrics`
from the audited lyric. If production changes wording, return it to integration and reaudit.
When `production` is requested directly, first validate the final input, remap its actual words,
audit, repair if needed, remap the repaired flow, and reaudit before Production Director runs.

## Output

For creation, return:

1. frozen brief and assumptions;
2. clean performance draft;
3. concise word/rhyme/flow annotations requested by the user;
4. conservative audit with hard gates, evidence, score caps, and unknowns;
5. a checkpoint log: what was proposed, what the user chose or changed at each CP;
6. production handoff only when relevant.

For analysis, return:

1. source-policy boundary;
2. plain-language section and bar map;
3. word table with meaning, grammar, sound, rhyme, humor, narrative, evidence, and confidence;
4. rhyme graph and placement map;
5. flow observations versus audio-dependent unknowns;
6. highest-impact revisions when requested.

Do not bury a requested lyric under process notes. Do not present a numerical score without its
evidence and cap.

## Definition of done

- Every mandatory checkpoint (CP1–CP4, CP5 when an audit found issues) was either approved by
  the user or explicitly delegated via `interaction_mode: autonomous`; the choices are recorded
  in `checkpoint_log`, and `selected_keywords` / `selected_rhyme_pairs` trace the user's picks.
- The brief and artifact revisions agree.
- Required specialist artifacts are ready or explicitly unverified.
- Named references were converted to anonymous multi-source techniques.
- Concrete material precedes abstraction.
- Rhyme uses plausible performed readings and varied placement appropriate to the brief.
- Humor has mechanism, setup, violated expectation, target, and timing.
- Every bar has a job; every four bars change information, emotion, or flow unless justified.
- Natural Japanese survives removal of rhyme words.
- A blind audit, repair log, and fresh reaudit exist for substantive creation.
- No commercial lyric corpus or close imitation entered references, fixtures, or final output.
- Performance uncertainty remains visible until audio is reviewed.
