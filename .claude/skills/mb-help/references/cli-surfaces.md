# Newer CLI surfaces — the business question each one answers

Operators never browse the CLI; they ask business questions and the agent
runs the right command. This map keys each newer surface to its question
and to the *moment* it should be offered. If an operator's question matches
a row, answer with the row — do not make them learn the command catalog.

| Business question | Surface | Offer it when |
| --- | --- | --- |
| "Where do my customers/leads actually live? Can my agent see them?" | `mb spine declare --store <provider>` records the position as a repo fact; `mb spine show` reads it back; `mb doctor` grades it (queryability, declared gaps, revisit trigger). | Any whose-data question, or when status/doctor shows no spine declaration. |
| "We deliberately keep no customer list — is that okay?" | `mb spine declare --store none --intentional` — a declared stance, not a gap. | Local-first / privacy-stance products. |
| "My platform can't answer X about my people." | `mb spine init --owned` scaffolds the owned contact+event schema (the *triggered* build path — declare first; see decisions/2026-06-12-spine-levels.md). | Only when a real unanswerable question exists — never as a default migration. |
| "How do I know my checkout/forms still work while I sleep?" | `mb canary init` scaffolds the golden-path smoke harness + alert doctrine (FAIL pages, WARN never). | The moment real money or real leads flow unattended. |
| "Give me a daily read on the business — what happened, what do I do today?" | `mb pulse init` scaffolds deterministic per-source collectors plus a repo-local pulse skill: scorecard, anomalies, exactly ONE recommended action, sub-60-line daily log. Read-only; it consumes `mb status` facts rather than re-ranking them. | When the operator wants a recurring morning picture — typically once real traffic, leads, or sends exist to report on. |
| "How do my scheduled tasks read credentials safely?" | `mb connect token <provider>` — token to stdout only, for scripts and agents; never for chat. | Any cron/automation wiring. Never echo the value. |
| "Are any of my API keys sitting in plaintext where an agent could leak them?" | `mb connect hygiene` — read-only scan of `~/.claude.json` + project MCP/settings for plaintext credentials; reports surface, location, length-only mask, and a keychain/env remediation. Never prints the value. | After wiring MCP servers, before sharing a machine, or any credential-hygiene worry. |
| "My tool isn't in the provider list." | `mb connect <id> --custom` — operator-named provider on the same secure rails. | When `mb connect` says unknown provider. |
| "Did my key rotation actually take everywhere?" | Rotation sweeps sibling refs automatically and warns loudly about any it could not update. | After any credential rotation. |
| "Validate just what I changed, not the whole repo's history." | `mb validate --paths <file-or-dir>` (repeatable). | Agents validating their own work in repos with legacy debt. |
| "Show me the business visually." | `mb dashboard build` / `mb dashboard open` — local, read-only, never committed. | "What's the state of things" moments. |
| "I changed my offer — did the ads/pages catch up?" | `core_propagation` drift in `mb status` flags identity files newer than active push records. | Automatic; explain it when it appears. |
| "We decided that weeks ago — did anything actually change?" | `uncodified_decisions` drift flags accepted decisions never codified; repair with `/mb-think codify`. | Automatic; explain it when it appears. |
| "What can my agents actually access?" | `core/operations/agent-access-dossier.md` (scaffolded at setup); `mb doctor` runs the safe rows of its verify column. | Access/capability questions; after connecting providers. |

Two rules when using this map:

- **Lead with the business answer, command second.** "Your customers live
  in your commerce platform; let's record that so every agent knows" — then
  the command.
- **Triggered surfaces stay triggered.** Never push `spine init --owned` or
  a canary on a business whose trigger hasn't fired; the doctrine pages say
  when (decisions/2026-06-12-spine-levels.md, the canary README it
  scaffolds, docs/delivery-truth.md, docs/traffic-reconciliation.md).
