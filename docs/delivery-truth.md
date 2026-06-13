# Delivery truth: acceptance is not delivery

Email and message providers return success when they *accept* a send, not
when the recipient *receives* it. Resend (and most providers) return a 200
and a message id even when the recipient is suppressed, the domain bounces,
or the message dies downstream. A business that trusts the 200 believes it
contacted a lead it never reached.

This page is the engine-side doctrine for any surface that sends on a
business's behalf — email, SMS, webhooks, or future channels. It was proven
three times on a live business (a verified-webhook delivery log, per-lead
`delivery_state` columns, and spine `*_sent` events) before graduating here.

## The pattern

1. **Record the provider message id at send.** The send call's response id
   is the join key for everything that follows. Store it with the record
   that triggered the send (the lead, the order, the nurture step).
2. **Keep `delivery_state` separate from "sent".** `sent` means the
   provider accepted the request. `delivery_state` starts at `accepted` and
   only becomes `delivered` on provider evidence. They are different facts;
   never collapse them into one boolean.
3. **Reconcile with a webhook fast-path.** Subscribe to the provider's
   delivery events (delivered, bounced, complained, suppressed), verify the
   webhook signature, and flip `delivery_state` from the event. This is the
   cheap, near-real-time path.
4. **Back it with a GET ceiling.** Webhooks drop. A periodic reconcile
   fetches the message status by id for anything still `accepted` past a
   ceiling (for example 30 minutes) and flips the state from the fetch.
5. **Page on `delivery_failed`.** A bounce or suppression on a money-path
   send (a paid report, a lead response, a receipt) is an operator-facing
   alert with the contact and the repair, not a log line.
6. **Never trust the 200.** Agents reporting "email sent" must read
   `delivery_state`, not the send response. "Accepted by the provider,
   delivery pending" is the honest report until evidence lands.

## Why the suppression case is the keystone

Suppression is the silent killer: a marketing unsubscribe can suppress
*transactional* sends on the same provider, and the send API still returns
200 with an id. The recipient gets nothing; every system that trusted the
200 says they did. On a live business this surfaced as paying customers not
receiving the product they paid for. Treat suppression events as
first-class delivery failures and check suppression lists before money-path
sends where the provider exposes them.

## Send-function shape

Channel-agnostic template; adapt names to the stack:

```js
async function sendWithTruth(record, message, provider) {
  const response = await provider.send(message);   // throws on transport error
  await store.recordSend({
    record_id: record.id,
    provider_message_id: response.id,              // join key — never skip
    delivery_state: "accepted",                    // NOT "delivered"
    sent_at: now(),
  });
  return response.id;
}

// Webhook fast-path (verify the signature before trusting anything):
async function onDeliveryEvent(event) {
  verifySignature(event);                          // e.g. Svix for Resend
  await store.updateDeliveryState(event.message_id, {
    delivery_state: mapEvent(event.type),          // delivered | bounced | suppressed
    delivery_evidence: event.type,
    delivered_at: event.created_at,
  });
  if (isMoneyPath(event) && isFailure(event.type)) {
    await alertOperator(event);                    // page, don't log
  }
}

// GET ceiling (cron): anything accepted past the ceiling gets reconciled.
async function reconcileStale(ceilingMinutes = 30) {
  for (const row of await store.staleAccepted(ceilingMinutes)) {
    const status = await provider.getMessage(row.provider_message_id);
    await store.updateDeliveryState(row.provider_message_id, {
      delivery_state: mapStatus(status),
      delivery_evidence: "reconcile_fetch",
    });
  }
}
```

## What this means for Main Branch surfaces

- Any engine surface or playbook that sends (or generates code that sends)
  follows this pattern; "send succeeded" in operator-facing output means
  `delivery_state`, not the API response.
- The contact/event spine schema carries send and delivery events so "did
  we reach this lead?" is answerable from the system of record
  (issue #814).
- Provider mutation gates treat sends as mutations that require verify
  receipts (issue #656); the delivery state is the receipt.

Related: [checks-and-review-model.md](checks-and-review-model.md) for the
verify-before-done discipline this belongs to, and
[provider-mutation-contract.md](provider-mutation-contract.md) for the
preview → approve → apply → verify gate every external-account write runs
(a send is one such mutation; its delivery receipt is the verify step).
