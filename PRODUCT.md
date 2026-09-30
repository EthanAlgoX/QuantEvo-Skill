# QuantEvo Skill

<!-- impeccable:product-schema 1 -->

## Platform
web

## Users and purpose
Users install a skill into their existing AI tool, evaluate strategies, and
monitor independently running local paper accounts. The requested website
shows each strategy's state; Codex can inspect the same state through JSON.

## Operating context and constraints
Local single-user deployment. No real orders or extra LLM configuration.
CSV producers append completed bars; history is immutable. Accounts pin a
strategy and execution version, preserve state across restart, and expose stale
feeds and failed workers. Research candidates never replace active accounts
implicitly. Demonstration data is synthetic and must be visibly labeled.

## Existing identity
Name: QuantEvo Skill. README workflow asset provides an existing restrained
visual identity. English-first bilingual documentation is an established choice.

## Open decisions
Homepage emphasis is pending the optional user question. Until answered,
inferred default: compact account list with health and a selected-account
ledger, equity chart and fill history. This is a working assumption.
