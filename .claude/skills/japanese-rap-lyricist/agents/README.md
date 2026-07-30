# Host adapters

The portable contract lives in `../references/subagent-contracts.md`. Files here are thin
host-specific adapters.

## claude-code/ (primary)

Ready-to-install Claude Code subagent definitions. Copy them into your project to make the
firewall roles first-class subagents:

```bash
mkdir -p .claude/agents
cp agents/claude-code/*.md .claude/agents/
```

- `rap-professional-auditor.md` — blind adversarial auditor. Spawning this as a separate
  subagent (instead of self-auditing in the writer's context) is what upgrades audit
  independence from `partial` to `full`.
- `rap-reference-analyst.md` — the only role allowed to see artist names; returns an
  anonymous technique vector.
- `rap-theme-researcher.md` — theme web researcher with two modes: `scout` (repeated inside
  the CP1 intake loop, returns 3-5 concrete angles per round) and `deep` (one exhaustive
  keyword sweep after the brief freezes, producing `run/research_bank.json` and the
  `run/research_keywords.html` table).
- `rap-rhyme-banker.md` — generates 20+ scored rhyme candidates per selected keyword across
  all rhyme types (assonance, consonance/"ktkt" skeletons, multimora, phrase/mosaic,
  placement proposals), producing `run/rhyme_bank.json` and `run/rhyme_bank.html`.

The remaining roles (Narrative, Vocabulary, Humor, Rhyme, Flow, Integrator, Repair Owner,
Production Director) do not need standing definitions: spawn them as ad-hoc Task subagents
using the role contracts in `subagent-contracts.md`. Installing the two above is optional —
the skill works without them by spawning ad-hoc Tasks with the same contracts.

## openai.yaml (legacy)

ChatGPT/Codex skill manifest kept for backwards compatibility. Claude Code ignores it.
