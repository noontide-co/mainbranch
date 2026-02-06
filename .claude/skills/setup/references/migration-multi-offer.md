# Migration: Single-Offer to Multi-Offer

When an existing user with `core/offer.md` wants to add another offer (detected when user says "I want to add another offer", "I have a second product", or similar).

## Detection

Check for existing single-offer structure:
```bash
ls reference/core/offer.md 2>/dev/null && ! ls reference/offers/*/offer.md 2>/dev/null
```

If `core/offer.md` exists and no `offers/` folder: this is a migration.

## Steps

1. **Confirm the restructure:**
   > "Right now your offer details are in `core/offer.md`. To add another offer, we restructure: `core/offer.md` becomes your brand-level thesis, and each specific offer gets its own file."

2. **Name the existing offer:**
   > "What should we call the offer currently in `core/offer.md`?" (e.g., "community", "course", "coaching")

3. **Name the new offer:**
   > "And what's the new offer called?"

4. **Execute atomically:**
   ```bash
   # Move existing offer to its own folder
   mkdir -p "reference/offers/[existing-name]"
   git mv reference/core/offer.md "reference/offers/[existing-name]/offer.md"

   # Create new offer folder
   mkdir -p "reference/offers/[new-name]"
   # (new offer.md will be written in the guide-writing step below)

   # Create product-ladder.md
   mkdir -p reference/domain
   # (product-ladder.md will be written below)

   # Create session state
   mkdir -p .vip
   echo "current_offer: [existing-name]" > .vip/local.yaml

   # Ensure .vip/local.yaml is git-ignored
   grep -q ".vip/local.yaml" .gitignore 2>/dev/null || echo ".vip/local.yaml" >> .gitignore
   ```

5. **Write new brand-level `core/offer.md`:**
   Guide the user to write a high-level brand thesis. This covers what the brand stands for across all offers -- not the specifics of any single one.
   > "Now we need a brand-level offer.md. This isn't about one product -- it's the umbrella. What does your brand offer the world? What transformation do all your products share?"

6. **Write the new offer's `offer.md`:**
   Guide them through the standard offer template for the new offer.

7. **Write `reference/domain/product-ladder.md`:**
   > "How do these offers relate? Is there a natural progression?"

8. **Commit atomically:**
   ```bash
   git add -A
   git commit -m "[refactor] Migrate to multi-offer structure

   - Moved existing offer to offers/[existing-name]/
   - Created brand-level core/offer.md
   - Added offers/[new-name]/
   - Created product-ladder.md
   - Added .vip/local.yaml for session offer tracking

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

9. **Confirm:**
   > "Migration complete. You now have [N] offers. `/start` will ask which offer to work on each session. Run `/start [offer-name]` to jump straight to one."
