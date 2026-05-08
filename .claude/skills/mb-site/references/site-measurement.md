# Site Measurement Readiness

Load this when the operator mentions paid traffic, Google Ads, GTM, conversion tracking, retargeting, or launch readiness.

## Source Of Truth

Load `docs/google-ads-gtm-conversion-rubric.md` before generating or approving a paid-traffic site. Use the rubric's `mb_*` event vocabulary and do not recommend launch from prose alone.

After the site repo has `.mainbranch/conversion.json` and built HTML, run:

```bash
mb site check "$SITE_REPO" --business-repo "$BUSINESS_REPO" --json
```

If running from a site repo with `.mainbranch/repo.json` or legacy
`.mainbranch/source.json`, `mb site check . --json` can infer the linked
business repo when a local checkout hint exists. If the descriptor only stores
safe GitHub handles, pass `--business-repo "$BUSINESS_REPO"`.

## Readiness States

Use the JSON as the readiness source of truth:

- `blocked`: stop and give the exact failed checks plus the next command or manual step.
- `ready_for_preview`: static instrumentation can be previewed, but provider metadata or approvals are still missing.
- `ready_for_operator_review`: the operator must review GTM Preview/Tag Assistant, conversion actions, consent posture, and publication before launch.
- `ready`: local checks and recorded approvals passed. It still does not launch anything.

The readiness states are exactly `missing`, `blocked`, `ready_for_preview`, `ready_for_operator_review`, and `ready`.

Do not invent `ready_for_launch` or say Main Branch can launch a campaign.

## Secrets Boundary

Never ask the operator to paste Google Ads, GTM, OAuth, or API tokens into chat.

Use `mb connect plan` or `mb connect doctor --json` for provider readiness and quote the CLI's `next_command` or `repair_command`.
