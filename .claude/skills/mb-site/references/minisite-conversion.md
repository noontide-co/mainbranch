# Minisite Conversion Endpoint

Load this for step 6 of the minisite flow: choosing and recording the CTA target.

## Operator Pick

Operator picks the kind, per the [Conversion endpoint](minisite.md#conversion-endpoint) section of the engine spec:

- Stripe payment page.
- Lead form.
- Appointment booking.
- Custom webhook.

## Stripe Payment Page

Run after the operator approves the offer, price, and success URL:

```bash
python3 .claude/skills/mb-site/scripts/stripe.py create-payment-link <offer-slug> --amount <cents> --success-url https://<domain>/start/thanks/
```

Capture `payment_link.url` from the envelope.

## Lead Form

Ask:

> "Where does form data go?"

Capture provider and URL, such as Tally, Typeform, Google Form, native + Formspree, or custom backend.

## Appointment Booking

Ask for the booking-link URL, such as Cal.com, Calendly, or SavvyCal.

## Custom Webhook

Ask for the URL and confirm the operator owns the endpoint.

## Write Conversion JSON

Write the picked endpoint to `<site_repo>/.mainbranch/conversion.json`. The shape is the same for all kinds; the `metadata` block varies.

Stripe payment page:

```json
{
  "kind": "stripe_payment_page",
  "url": "https://buy.stripe.com/abc123",
  "render": "link_out",
  "metadata": {
    "amount_usd": 100,
    "currency": "usd",
    "stripe_product_id": "prod_xyz",
    "stripe_payment_link_id": "plink_abc",
    "payment_kind": "deposit"
  }
}
```

Lead form:

```json
{
  "kind": "lead_form",
  "url": "https://tally.so/r/abc123",
  "render": "link_out",
  "metadata": { "provider": "tally" }
}
```

Appointment booking:

```json
{
  "kind": "appointment_booking",
  "url": "https://cal.com/devon/intro",
  "render": "link_out",
  "metadata": { "provider": "cal.com" }
}
```

Custom webhook:

```json
{
  "kind": "custom_webhook",
  "url": "https://operator-domain.com/leads",
  "render": "form_post",
  "metadata": {}
}
```

## Click-ID capture invariant (lead-capturing surfaces)

Operating-principles §6 — own the form, capture the attribution — is enforced
by scaffold, not by a later audit. Any surface that captures a lead
(`lead_form`, `custom_webhook`, or any form that posts) MUST snapshot the
click IDs and campaign params from the landing URL by default, and forward
them on submit. A real business we built captured `fbclid` + 5 UTMs but ZERO
Google click IDs, so its first Google clicks were permanently unattributable —
caught only by a readiness audit, which is exactly the failure this default
prevents.

Required capture set (snapshot from the querystring on first load, persist
across navigation, forward on submit):

- **Google click IDs:** `gclid`, `gbraid`, `wbraid`
- **Meta click ID:** `fbclid`
- **UTMs (all five):** `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`

Add `msclkid` (Microsoft) and `ttclid` (TikTok) when those channels are live.
Capture the params even when no campaign is running yet — the cost of a missing
column is permanent, unrecoverable attribution loss the day paid traffic starts.

## Generation Contract

The generation subagent reads `kind`, `render`, and `url`, then renders the home CTA accordingly:

- link-out button;
- embedded form;
- embedded booking iframe;
- form-POST handler.

For every lead-capturing render, the generated form/handler carries the
click-ID capture invariant above by default (hidden fields hydrated from the
landing querystring, forwarded on submit) — never an audit-time retrofit.
Flagging an existing lead-capturing site that is missing the set is a
follow-up `/mb-status` check (#887).

After conversion is recorded, move to [`concept-variations.md`](concept-variations.md).
