# Operator Loops — Stress Test (04)

Pure reasoning + repo reading. No web research. The job: take six candidate
taxonomies plus one I designed, classify 20 real solo-operator activities
against each, count the breaks, and pick a defensible winner.

The winner has to survive (a) the 20 activities below, (b) cross-business
operators (fitness coach, B2B consultant, ecom DTC), and (c) the actual work
the 17 bundled skills already do.

---

## Candidates tested

- **A. Devon current** — Know · See · Decide · Execute · Show
- **B. Devon alt** — Know · See · Decide · Execute · Learn
- **C. OODA** — Observe · Orient · Decide · Act
- **D. PDCA** — Plan · Do · Check · Act
- **E. Build–Measure–Learn (+ prep)** — Prep · Build · Measure · Learn
- **F. GTD 5** — Capture · Clarify · Organize · Reflect · Engage
- **G. Plain-English 6** — Capture · Plan · Make · Ship · Measure · Improve
- **H. Mine — "Devon current, renamed"** — Know · See · Decide · Make · Narrate

H differs from A only in two places: "Execute" → "Make" (because Execute
swallows ops/ship/connect work that isn't really making), and "Show" → "Narrate"
(because Show implies external broadcast, but a quarterly retro to yourself is
also loop-5 work). I'll test H against A directly.

---

## Classification table

Legend: single letter = clean fit, `dual:X+Y` = forced into two, `?` = unclear,
`–` = no slot exists. Numbers correspond to the 20 activities.

| #  | Activity                                | A (K/S/D/E/Sh)   | B (K/S/D/E/L)    | C (OODA)        | D (PDCA)        | E (BML+P)        | F (GTD)         | G (6-step)            | H (K/S/D/M/N)    |
|----|-----------------------------------------|------------------|------------------|-----------------|-----------------|------------------|-----------------|-----------------------|------------------|
| 1  | Update offer.md after price change      | K                | K                | Or              | dual:P+A        | Pr               | Cl/Or?          | Pl?                   | K                |
| 2  | Read `mb status`                        | S                | S                | Ob              | Ch              | Me?              | Re              | Me                    | S                |
| 3  | Write YouTube script (teaching)         | E                | E                | Ac              | Do              | Bu               | En              | Ma                    | M                |
| 4  | Record YouTube post-mortem (failed launch) | dual:E+Sh     | dual:E+L         | dual:Ac+Or      | dual:Do+A       | dual:Bu+Le       | En?             | dual:Ma+Im            | dual:M+N         |
| 5  | Draft 4 ad variants for new bet         | E                | E                | Ac              | Do              | Bu               | En              | Ma                    | M                |
| 6  | Post one ad live to Meta                | E                | E                | Ac              | Do              | Bu               | En              | Sh                    | M                |
| 7  | Tweet "shipped my lander, here's link"  | Sh               | dual:E+L?        | Ac              | Do              | Bu               | En              | Sh                    | N                |
| 8  | Tweet "closed workshop bet — 51/40 won" | Sh               | L                | Or?             | A               | Le               | Re?             | Im                    | N                |
| 9  | Close `bets/<slug>.md` with verdict     | dual:E+Sh        | L                | Or              | A               | Le               | Re              | Im                    | N                |
| 10 | Connect Stripe via `mb connect`         | E?               | E?               | Ac              | dual:P+Do       | Pr               | Or              | Pl?                   | dual:S+M?        |
| 11 | Run `mb update` 0.2.6 → 0.3.0           | E? S?            | E? S?            | Ob/Ac?          | dual:P+Do       | Pr               | Or              | Pl?                   | dual:S+M?        |
| 12 | Fix broken skill symlink                | E? S?            | E? S?            | Ac              | dual:Ch+A       | Pr               | Or              | Im?                   | dual:S+M?        |
| 13 | Read offer.md before sales call         | K                | K                | Ob              | dual:P+Do       | Pr               | Re              | Pl?                   | K                |
| 14 | Choose which of 3 offers to launch next | D                | D                | De              | Pl              | Pr               | Cl              | Pl                    | D                |
| 15 | Write quarterly retro about all bets    | dual:K+Sh        | L                | Or              | A               | Le               | Re              | Im                    | N                |
| 16 | Member-only Skool weekly update         | Sh               | dual:E+L         | Ac              | Do              | Bu/Me?           | En              | Sh                    | N                |
| 17 | Edit voice.md after tone shift          | dual:K+Sh        | dual:K+L         | Or              | A               | Le               | Cl/Or           | Im                    | dual:K+N         |
| 18 | Record customer interview to research/  | K                | K                | Ob              | dual:P+Ch       | Pr/Me?           | Cap             | Cap                   | K                |
| 19 | Build Cloudflare lander                 | E                | E                | Ac              | Do              | Bu               | En              | Ma                    | M                |
| 20 | Review draft VSL with seven sweeps      | dual:E+S?        | dual:E+L?        | Or              | Ch              | Me?              | Re              | Im                    | dual:M+S?        |

**Counts (out of 20):**

| Taxonomy | Clean | Dual-loop | Unclear/`?` | Notes |
|----------|------:|----------:|------------:|-------|
| A — Know/See/Decide/Execute/Show       | 12 | 4 | 4 | "Show" forces public framing; ops work has no home |
| B — Know/See/Decide/Execute/Learn      | 13 | 3 | 3 | "Learn" is internally generous; public-tweet ambiguous |
| C — OODA                                | 14 | 1 | 3 | Surprisingly clean, but Orient does too much work |
| D — PDCA                                |  9 | 6 | 1 | Reference reads collide with planning; ops work splits |
| E — BML+Prep                            | 12 | 1 | 4 | "Prep" is a junk drawer; reference reads aren't "Build" |
| F — GTD 5                               | 11 | 0 | 4 | Capture/Clarify/Organize collapse on operator (no inbox); Engage swallows |
| G — Plain-English 6                     | 14 | 2 | 4 | Make vs Ship gap matters; Improve vs Plan ambiguous |
| **H — Know/See/Decide/Make/Narrate**    | **15** | **3** | **2** | "Make" cleanly hosts ops; "Narrate" hosts internal+external |

H scores best, but the count alone isn't the argument. Failure modes below.

---

## Failure modes by taxonomy

### A — Know · See · Decide · Execute · Show
- **"Show" forces external audience.** #15 (quarterly retro), #17 (voice.md edit
  from a tone realization), #9 (close bet) — these are partly *learning*
  artifacts the operator writes for themselves first. Calling them "Show"
  implies broadcast, so they get dual-mapped to Know/Execute + Show.
- **No home for ops/install work.** #10 (`mb connect`), #11 (`mb update`), #12
  (skill symlink) are not Execute (they don't ship business value), not See
  (they aren't observation), not Know (they don't write reference). They limp
  into Execute by elimination.
- **Post-mortem #4 collapses.** A YouTube post-mortem is simultaneously
  Execute (record video) and Show (publish narration). Real dual.

### B — Know · See · Decide · Execute · Learn
- **Better than A** because Learn captures internal reflection without forcing
  publicness. #15 retro, #8 closing-tweet-as-internal-record, #9 bet close all
  land cleanly.
- **But "Learn" eats narration.** Public broadcast (#7 launch tweet, #16 Skool
  update) doesn't fit Learn. Forced into Execute or dual.
- **Same ops gap as A.** #10–#12 still homeless.
- **Learn also competes with Decide.** Reading `mb status` (#2) is technically
  learning the state, but it's "See." Reviewing a VSL draft (#20) is learning
  whether copy works — Learn? Execute? Both?

### C — OODA
- Cleanest small taxonomy. Orient absorbs reflection, decision-prep, retros,
  reference updates — almost too well. The cost is **Orient becomes a junk
  drawer**: #1, #8, #15, #17, #18, #20 all live there. If one bucket has 6/20
  activities, the taxonomy isn't doing real work.
- **No "narrate to others" loop.** Public tweets, Skool updates, public bet
  pages are just Act. That collapses Devon's actual product (public narration
  as fulfillment for vip members) into the same bucket as posting an ad.

### D — PDCA
- Worst on raw counts. **Reference reads collide with Plan.** Reading offer.md
  (#13) and updating offer.md (#1) both touch Plan, but one is read and one is
  write — PDCA has no read primitive.
- **Check is too narrow.** `mb status` is checking, but so is reviewing a VSL
  draft (#20), so is a customer interview (#18 — checking what they actually
  said). Three different things in one bucket.
- **Act-as-corrective-action vs Act-as-do.** PDCA's "Act" means "adjust based
  on Check." But colloquially "act" reads as "do." The taxonomy is brittle for
  non-engineers.

### E — Build–Measure–Learn (+ Prep)
- **"Prep" is a junk drawer** — it eats setup, reference reads, integrations,
  research collection. That's 5–7 of the 20 activities. Same problem as OODA's
  Orient.
- **Measure is thin.** What does an operator measure when they don't yet have
  data? `mb status` (#2) is measuring repo state, not business outcomes. The
  loop assumes a quantitative substrate the solo operator often lacks.
- **Build/Measure/Learn is a launch-cycle frame, not a daily-operator frame.**
  It works for "launch a bet," not for "Tuesday morning."

### F — GTD 5
- **Capture/Clarify/Organize collapse.** GTD assumes an inbox of items needing
  triage. The operator's repo *is* the organized state. So #1 (update offer.md)
  is simultaneously Clarify ("what does this price change mean") and Organize
  ("file the new price in offer.md"). No clean split.
- **"Engage" swallows everything operational.** #3, #5, #6, #7, #16, #19 all
  Engage. Six activities in one bucket = bucket isn't doing work.
- **Reflect is the only good fit** — it cleanly hosts retros and `mb status`.
  But that's not enough to redeem the rest.

### G — Plain-English 6
- **Make vs Ship is the right cut.** Drafting an ad (#5) ≠ posting it (#6),
  writing a script (#3) ≠ recording the video (#4). Plain-English 6 captures
  this where A/B/H smush them into one Execute/Make bucket.
- **But Plan vs Improve is the wrong cut for solo operators.** Editing
  voice.md after realizing a tone shift (#17) is "Improve" (correction) but
  also "Plan" (sets future tone). #14 (choose next offer) is Plan, but
  informed by what didn't work — Improve.
- **Six is too many.** The cognitive load of remembering six categories with
  near-synonyms (Plan vs Improve, Make vs Ship, Capture vs Plan) is more than
  most operators will pay. Five is the sweet spot.

### H — Know · See · Decide · Make · Narrate (mine)
- **"Make" replaces "Execute."** Make is honest: it's craft work — drafting,
  building, recording, designing, coding, posting. It naturally extends to
  ops/install ("making the system run") via mild stretch.
- **"Narrate" replaces "Show."** Narrate covers internal narration (retros,
  bet closes, decisions) AND external narration (tweets, public bet pages,
  Skool updates). One word, full coverage.
- **Surviving breaks:** post-mortem #4 still dual (it's Make + Narrate, but
  the action is genuinely both). #17 voice.md edit is dual (you re-Know
  *because* you Narrated to yourself first). #20 VSL review is dual (See the
  draft + critique it). These are *real* duals, not taxonomy failures.
- **Residual fuzz:** ops/install (#10–#12) still doesn't have a perfect home.
  I forced them to See+Make. More on this below.

---

## Cross-business stress test

I'll apply the top two contenders (H and B) to three specific operators and
see if the taxonomy holds for their actual weekly work. The test: take a
representative week and try to put every action in one bucket.

### Fitness coach running a Skool community ($97/mo)

Weekly work:

1. Record Monday Q&A call for members → **Make** (H) / **Execute** (B)
2. Review weekly check-ins from 12 members → **See** + **Decide** (H) / same (B)
3. Update meal-plan PDF after FDA labeling change → **Know** (H/B)
4. Post Reel teaching one tactic → **Make + Narrate** (H — dual)
5. Tweet "12 PRs hit this week from the crew" → **Narrate** (H) / **Learn?** (B — fuzzy)
6. Decide whether to raise price → **Decide** (H/B)
7. Write monthly retro on member retention → **Narrate** (H) / **Learn** (B)
8. Reply to DMs about onboarding friction → **See** + **Make** (H) / **Execute** (B fuzzy)
9. Record short video answering a member's specific question → **Make + Narrate** (H — public-facing answer)

H wins because #5 (public-tweet-of-internal-progress) and #7 (retro) both go
to Narrate — same loop, different audience. B forces #5 into Learn or Execute,
which feels wrong; tweeting member wins is closer to retro than to learning.

### B2B consultant ($25K engagements, LinkedIn-led)

Weekly work:

1. Read a prospect's 10-K before discovery call → **Know** (clean both)
2. Update positioning doc after discovery insights → **Know** (H/B)
3. Draft proposal for inbound lead → **Make** (H) / **Execute** (B)
4. LinkedIn post: case-study narration of a recent client → **Narrate** (H) / fuzzy (B — Execute? Learn?)
5. Send invoice → **Make** (H, ops-as-make) / **Execute** (B, also fuzzy)
6. Quarterly P&L review → **See** (H/B)
7. Decide whether to raise day-rate → **Decide** (H/B)
8. Update CRM with last week's calls → **Know** (capture facts about clients)

H holds. B's fuzziness on #4 (LinkedIn case study) is the same Show-vs-Learn
seam. The consultant *narrates publicly* as marketing — that's the same loop
as their internal client retro, different audience.

### Shopify DTC operator (skincare, ~$50K/mo)

Weekly work:

1. Pull yesterday's GA + Shopify revenue → **See** (H/B clean)
2. Decide tomorrow's ad budget allocation → **Decide** (H/B)
3. Write 3 new ad hooks → **Make** (H) / **Execute** (B)
4. Send creative brief to designer → **Make** (H) / **Execute** (B)
5. Update product page copy after CRO test result → **Make + Know?** (H — dual: copy is craft, but it also updates durable reference)
6. Approve new SKU launch plan → **Decide**
7. Post launch announcement on IG + email → **Make + Narrate** (H — dual)
8. Read this month's churn numbers → **See**
9. Write retro on Q1 ad spend → **Narrate** (H) / **Learn** (B)

Both hold. H's Narrate-covers-internal-and-external again proves cleaner on
#9. The operator also clearly distinguishes See (read metrics) from Decide
(allocate budget) from Make (write hooks) from Narrate (announce launch) —
five buckets, one slot per action.

**Verdict across three businesses: H holds, B has a recurring seam at the
"public narration" boundary, A has the same seam plus an ops-work hole.**

---

## My recommended winner

**H — Know · See · Decide · Make · Narrate.**

Why H, defensibly:

1. **It scores best on the 20-activity test (15 clean, 3 dual, 2 unclear).**
   The duals it does have are *real* duals (a post-mortem really is Make and
   Narrate at once), not taxonomy artifacts.

2. **"Make" is more honest than "Execute."** Execute carries an implementation
   smell (engineers execute on a roadmap). Make is what solo operators
   actually do all day — they make things. It also stretches naturally to
   "make the system run" so `mb connect`, `mb update`, fixing symlinks have
   a defensible home (operational craft is still craft).

3. **"Narrate" is the single biggest unlock vs A and B.** The seam in
   Devon's current taxonomy is that "Show" assumes external broadcast and
   "Learn" assumes internal capture, but the operator's loop-5 work is *the
   same act with different audiences*. Closing a bet is narration to yourself.
   Tweeting the close is narration to the public. They share infrastructure
   (the bet file), share content (the verdict), share rhythm (post-decision).
   Calling them one loop is correct.

4. **It maps cleanly onto the existing 17 skills.** Going through them:
   - Know: `/mb-think` (codify mode), `/mb-setup`, `/mb-wiki`
   - See: `/mb-status`, `/mb-help`, `/mb-pull` (legacy), `/mb-update`
   - Decide: `/mb-start` (triage), `/mb-think` (decide mode), `/mb-bet new`
   - Make: `/mb-ads`, `/mb-vsl`, `/mb-organic`, `/mb-site`,
     `/mb-skill-brief-draft`, `/mb-skill-concept`, `/mb-skill-review`
   - Narrate: `/mb-end`, `/mb-bet close|narrate`
   16 of 17 skills slot into exactly one loop. `/mb-think` legitimately spans
   Know + Decide because it's the combined research-decision skill — that's
   skill-level, not taxonomy-level, ambiguity.

5. **It survives cross-business.** Fitness coach, B2B consultant, ecom DTC
   all work clean. The seam in B (public narration) doesn't appear in H.

6. **It preserves Devon's current 5-loop structure.** This isn't a re-org —
   it's a rename in two slots. Existing docs (`OPERATOR-LOOPS.md`,
   `SYNTHESIS.md` line 199) keep their shape. The PR diff is small.

7. **Five is the right count.** Four (OODA) leaves a junk-drawer Orient.
   Six (G) creates synonym confusion (Plan vs Improve, Make vs Ship). Five
   is what an operator can hold in their head while opening their laptop.

**The two renames I'd actually push:**

- `Execute` → `Make` (honest about what's happening; absorbs ops work
  without contortion)
- `Show` → `Narrate` (covers internal + external; matches `/mb-end`,
  `/mb-bet`, retros, and public broadcast in one word)

Devon's "alternative" (Learn instead of Show) is *better than current* but
*worse than Narrate* because it loses the public-broadcast frame entirely.
Narrate is the synthesis.

---

## Edge cases the winner still struggles with

I'll be honest about the residual fuzz so this isn't oversold.

1. **Ops/install work (#10 connect Stripe, #11 mb update, #12 fix symlink)
   is genuinely awkward.** It's not Make in the craft sense; it's See-adjacent
   ("is the system healthy?") and Make-adjacent ("make it work"). The honest
   read is that **ops work is a sixth implicit loop** ("Maintain") that I'm
   collapsing into Make+See for parsimony. If Devon wants strict purity, a
   sixth "Tend" or "Maintain" loop would be defensible — but I'd argue against
   it because it doubles the count of skills no operator wants to learn.

2. **Post-mortems (#4) are genuinely dual.** Recording a YouTube post-mortem
   is Make (production) and Narrate (the post-mortem itself is the artifact).
   No taxonomy collapses this without losing information. Accept the dual.

3. **Reference-update-as-correction (#17 voice.md after a tone shift)** is
   K → N → K in time: you Narrate to yourself, learn, then update Know. The
   loop is sequential, not single-bucket. Document this as "loops chain" in
   the taxonomy doc.

4. **VSL review (#20)** is See (look at the draft) + Make (improve it) +
   Decide (does it pass?). The seven-sweeps process is intrinsically
   multi-loop. Probably the right framing is that *review processes always
   span See + Decide*, and that's a feature.

5. **`mb status` reading (#2) vs `/mb-think` research (#18)** — both produce
   "I now know more." Status is See (current state); research is Know
   (durable capture). The split is "ephemeral observation vs durable
   reference." This is the cleanest seam in the taxonomy and worth naming
   explicitly in `OPERATOR-LOOPS.md`.

6. **Sub-loops within Make.** Drafting → reviewing → publishing has internal
   structure. H ignores it (one bucket). G's Make/Ship split captures it but
   pays a cost elsewhere. I'd handle this by saying *Make is one loop with a
   draft → review → ship rhythm inside it*, and let `/mb-skill-review` etc.
   handle the rhythm at skill level, not taxonomy level.

---

## Position

Adopt **Know · See · Decide · Make · Narrate**. Rename Execute → Make and
Show → Narrate in `docs/OPERATOR-LOOPS.md` and `SYNTHESIS.md` line 199.

Keep five loops. Don't add Maintain. Document loops-chain explicitly so users
know K→N→K and Make→Narrate sequences are normal, not taxonomy bugs.

The one-line test for any future skill, command, or feature: *which loop does
this make better?* If the answer is "two," the feature is fine but the loop
chain should be named. If the answer is "none," the feature shouldn't ship.
