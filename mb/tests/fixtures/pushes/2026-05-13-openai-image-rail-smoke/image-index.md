# Image Index - OpenAI Image Rail Smoke

This fixture-safe record proves the first narrow OpenAI image rail without
committing generated binaries, secrets, private paths, or provider request
credentials.

```yaml
schema: mainbranch.image_index.v0
push_slug: 2026-05-13-openai-image-rail-smoke
docs_checked: '2026-05-13'
output_record_written: true
binary_committed: false
assets:
- asset_id: fake-openai-image-001
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt: Create a fixture-safe static ad concept for a fictional business called
    Northstar Ledger. Show an abstract desk scene with a clean notebook, simple
    charts, and warm natural light. Do not include real brands, real people, customer
    data, logos, screenshots, account details, or private information. Leave open
    space near the upper center for a later deterministic text overlay.
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-smoke/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    aspect_ratio: '2:3'
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-smoke/images/fake-openai-image-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: unreviewed
  safe_to_share: true
  generated_at: '2026-05-13T17:20:50+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only;
    keep any generated binary in configured private media storage.
```
