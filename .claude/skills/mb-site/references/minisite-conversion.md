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

## Generation Contract

The generation subagent reads `kind`, `render`, and `url`, then renders the home CTA accordingly:

- link-out button;
- embedded form;
- embedded booking iframe;
- form-POST handler.

After conversion is recorded, move to [`concept-variations.md`](concept-variations.md).
