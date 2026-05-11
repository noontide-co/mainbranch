# Agent Writing Style

A short rubric for agent-facing docs, PR descriptions, review comments,
issue bodies, and generated repo guidance. The goal is more signal per
token, not terseness for its own sake. Plain business language stays;
filler goes.

Surfaced from MAIN-323 / #490 alongside the post-release alignment
playbook.

## Audience

Apply this rubric when writing for:

- agent-facing docs in this repo (`AGENTS.md`, `CLAUDE.md`, generated repo
  guidance, bundled skill prose);
- PR titles, bodies, and review comments;
- GitHub issue bodies and comments synced from Linear;
- local agent preferences (which should be especially short — see
  `docs/post-release-alignment.md` -> Local Preferences Alignment).

User-facing product copy (`README.md`, `docs/beginner-setup.md`, the
`/mb-start` greeting, error messages an operator reads) keeps a warmer,
business-readable tone — it does not adopt this rubric verbatim. The
rubric's compression discipline still helps there, but lead with
plain-English clarity.

## Style Boundary

Main Branch keeps full sentences, clear tense, and a business-casual voice.
The compression pattern is action-first writing: drop filler, keep one-line
bullets tight, replace repeated background with links, and scale detail to
the risk of the decision. User-facing copy stays warm and plain-spoken.

A local compression-style writing reference was reviewed while drafting this
rubric. The useful pattern was brevity with structure; the public rule is the
rubric below.

## Rubric

1. Lead with the action or decision.
2. State only the context this reader needs for this task.
3. Link or point to source docs instead of restating them.
4. Use plain business language; reserve schema and infrastructure terms
   for contributor docs and code comments.
5. Prefer short sections and concrete bullets over long paragraphs.
6. Remove duplicate warnings unless the warning is load-bearing for this
   specific moment.
7. Separate facts, decisions, and open questions visually.
8. Do not sound clever or overly technical when business language is
   clearer.
9. Do not hide risk to save words. If a step is destructive or
   public-visible, say so plainly.
10. End with the next action.

## Token-saving rules

For cold starts and PR reviews:

- Do not paste the whole product stance when `AGENTS.md`, decisions, or
  docs already cover it. Link.
- Tell the agent which docs to read and what question to answer; do not
  pre-answer the question.
- Use one-line bullets for known facts.
- Use `Out of scope:` instead of long warning paragraphs.
- Use `Follow-ups:` instead of explaining every future branch.
- In review comments, quote only the changed behavior or the risky line.
  Do not restate background.
- Do not narrate your own thought process. State the conclusion.

## Guardrails

- Keep enough reasoning for non-obvious or load-bearing recommendations.
- Keep validation evidence and release evidence. See
  `docs/release-agent-contract.md`.
- Keep user-facing product copy warm and plain-spoken.
- Keep safety language when the risk is real. Public/private boundary
  warnings, destructive-action callouts, and release-truth statements stay.

## Where it applies

- `AGENTS.md` and `CLAUDE.md`: contributor protocol, already aligned.
- Bundled skill `SKILL.md` files: prefer linking `references/` over
  inlining long prose.
- Generated `CLAUDE.md.tmpl` / `AGENTS.md.tmpl`: keep the generated
  business-repo instructions short and link back to engine docs for
  detail.
- Local agent preferences: especially short. Protocol + read order, not a
  parallel product spec.
- PR bodies and review comments: see the validation-line evidence template
  in `docs/release-agent-contract.md`.

If a passage you are writing fails the rubric, the usual remedy is to
delete words, not rewrite. If after deletion the passage no longer makes
sense without the missing context, link to the doc that carries the
context.
