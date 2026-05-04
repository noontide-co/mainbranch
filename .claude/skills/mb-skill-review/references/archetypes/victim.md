# Victim

Pure suffering, no agency yet. The audience may currently feel like a Victim — but **never position the buyer as a Victim on a sales page.** This archetype's role is to describe the trap the offer breaks, not to label the buyer.

The Victim archetype is the audience's *current state*, not the offer's identity. It belongs in the brief schema's `audience_current_archetype` field, never in `archetype` (the offer's narrative shape).

## When to invoke

- As `audience_current_archetype` to name the trap the offer reframes.
- In the brief draft step, to anchor the "before" half of paired imagery.
- As the source state the hero section moves the reader *out of*, not into.

Do **not** invoke as the offer's archetype. Sales pages that position the buyer as a Victim trigger immediate rejection — the buyer's brain reads "you're helpless" and resists, even if circumstantially true. The Victim is the trap; the offer is the door.

## Audience-current trap → reframe

The Victim believes the system, the past, or other people have done this *to* them. There is no agency yet. The reframe target is whichever offer archetype gives them an artifact to act with: **Savior** (we'll do it for you, you don't have to fight) or **Wounded Healer** (I was where you are, I found a way out, here's the path).

The conversion event is the moment the buyer stops reading themselves as a Victim and starts reading themselves as a Broken Hero — someone who has fallen but can rise. That's the transition the page engineers.

## Do-not-state list

These conclusions belong to the reader. The skill does NOT write them as headlines or body copy.

- "You're a victim of [system / circumstance]." (Even if true, the buyer rejects the label.)
- "It's not your fault." (Will be heard as condescension.)
- "You deserve better." (Pep-talk; reads as sales-page emptiness.)
- "The system is broken." (Without specifics, this is empty rhetoric.)
- "You've been let down." (Triggers either agreement-then-numbness or defensiveness.)

## Paired-imagery template

Per the Hughes paired-imagery rule: every visual block is two adjacent inputs the reader's brain magnetizes into a conclusion. For the Victim slot:

- **The trap made tangible:** the system / pattern / scenario keeping them stuck (the form they fill out every quarter, the calendar full of the same week, the queue, the gatekeeper) **paired with** a specific moment of friction (a phone screen at 11pm, a stack of unpaid invoices, a closed door). Same composition, two states of the same trap. No operator visible — this is the world the reader inhabits, not the offer.

The next block (the offer's archetype slot) introduces the operator + the artifact. The reader's eye snaps from one to the other and assembles the path on their own.

## Reframe target (mandatory)

Victim is never standalone. The brief must pair it with one of:

- **`archetype: savior`** — the chore goes away, the reader doesn't have to fight. Best when the buyer's job is to *not* think about the work (B2B SaaS, done-for-you services).
- **`archetype: wounded-healer`** — the operator was in the same trap and found a way out. Best when the buyer needs to do the work themselves but with a guide.

Picking neither leaves the audience inside the Victim frame, which kills conversion.

## Example brand applications

- **A bookkeeping service** for small business owners: their `audience_current_archetype: victim` (drowning in receipts, IRS letters, late-night QuickBooks sessions); offer's `archetype: savior` (we do it for you).
- **A trauma-recovery coach**: `audience_current_archetype: victim` (events that happened *to* them); `archetype: wounded-healer` (I was there, here's the path back).
- **A consumer-protection class-action firm**: `audience_current_archetype: victim` (the bank, the insurer, the carrier); `archetype: david-goliath` (here's the slingshot).

## Voice anchor

- Names the trap in the audience's own words. Specific objects, specific times of day, specific phrases the buyer recognises from their own life.
- No labels (`victim`, `helpless`, `stuck`). The image carries the state; the copy describes the scene.
- No pep talk. No reassurance. The Victim slot is camera-on-the-trap, not narrator-comforting-the-reader.

## Anti-patterns

- Stock photography of a person with their head in their hands.
- Sales-page headlines that begin with "Tired of..."
- "We see you." (Soft-skill marketing copy that names the state instead of showing it.)
- Sympathy-bait. The Victim slot earns its conversion by being honest about the trap, not by performing empathy.

## Pairing prompts (for image + text generation)

When briefing the visual generator, pass paired prompts that hold the trap on one side and an absence-of-friction on the other:

- *"A desk at 11pm covered in receipts and an unopened envelope. Single overhead lamp."* + *"The same desk in morning light, completely cleared, a single open laptop showing a clean dashboard."*
- *"A long queue at a beige government counter, fluorescent lighting."* + *"A phone screen showing the same form auto-completed, a 'submitted' confirmation."*
- *"A bathroom mirror in the dark, the operator out of frame, the room visible."* + *"The same mirror in daylight, the operator visible from the back, walking out of frame."*

The text block that accompanies the pair names the scene, never the conclusion.
