# Site Measurement Readiness

Load this when the operator mentions paid traffic, Google Ads, Google
Analytics/GA4, GTM, Meta pixel, conversion tracking, booking links, HubSpot or
CRM forms, form-submit testing, retargeting, instrumentation, or launch
readiness.

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

## Instrumentation Facts

Use `facts.instrumentation` from `mb site check` when the operator asks "what
about analytics?" or "is tracking set up?"

- `declared` means repo-safe metadata records a planned ID or conversion.
- `detected` means static markup contains a tag, widget, form, or platform
  signal.
- `conversion_surface.state == "planned"` means `.mainbranch/conversion.json`
  owns the conversion path.
- `conversion_surface.state == "detectable_unplanned"` means a form, booking
  widget, or CRM widget exists but Main Branch has not recorded the conversion
  plan yet.

Detected is not the same as ready. A Calendly, HubSpot, Shopify, or form widget
can be detectable while delivery, attribution, and conversion-event mapping are
still unproven.

## Submit And Traffic Quality Smokes

Before paid launch, name the manual smoke that remains:

- submit a test form or booking and confirm the operator receives the lead;
- verify the expected `mb_*` dataLayer events fire in GTM Preview/Tag Assistant;
- reconcile provider-reported human clicks with site telemetry when live traffic
  looks crawler-heavy or inflated.

## Secrets Boundary

Never ask the operator to paste Google Ads, GTM, OAuth, or API tokens into chat.

Use `mb connect plan` or `mb connect doctor --json` for provider readiness and quote the CLI's `next_command` or `repair_command`.
