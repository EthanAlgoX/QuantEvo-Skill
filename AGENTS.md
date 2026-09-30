# QuantEvo Skill

Build an independent, open-source-ready strategy research skill for Codex and
Claude Code. The current project name is provisional.

- Canonical skill: `skills/quantevo/SKILL.md`. Both clients install this folder.
- Bundle runtime helpers under `skills/quantevo/scripts/` so installed skills
  work outside the repository. No dependency on the private QuantEvo checkout.
- Read `docs/architecture.md` for implemented versus planned capabilities.
- Models propose strategy changes; deterministic tools calculate and evaluate.
- Keep data, costs, evaluation rules and engine versions fixed within a study.
- Do not describe repeatedly inspected periods as blind holdouts.
- Preserve baseline and candidate versions; never replace an active simulation
  with a research candidate implicitly.
- Keep personal strategies, credentials, accounts and server configuration out
  of distributable files. Synthetic fixtures must be labeled.
- Run `python3 -m unittest discover -s tests -v` after runtime changes.
- This foundation has no order placement, unattended research or live feed.
  Do not advertise a planned command as executable.
