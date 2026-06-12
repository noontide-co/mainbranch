"""Golden-path canary scaffold (`mb canary init`).

Graduates the canary harness shape proven on a live business: checks return
``{name, state, surface, detail}``, a cheap tier runs often at near-zero
cost, an expensive tier runs rarely behind a flag, optional-secret checks
WARN instead of failing, and every alert is actionable. Check CONTENTS stay
business-side — the engine ships the harness and the doctrine, never the
business's invariants.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SMOKE_TEMPLATE = """#!/usr/bin/env node
/**
 * smoke.mjs — golden-path smoke test for this business's money path.
 *
 * ONE command. Exits non-zero on ANY hard failure. Prints a PASS/WARN/FAIL
 * line per check.
 *
 * USAGE
 *   node canary/smoke.mjs              # CHEAP tier only (near $0, run often)
 *   node canary/smoke.mjs --expensive  # CHEAP + EXPENSIVE tier (run rarely)
 *   node canary/smoke.mjs --json       # machine-readable summary on stdout
 *
 * DOCTRINE (see canary/README.md)
 *   - Every check guards ONE business invariant no platform synthetic can
 *     know, with a self-documenting comment: what breaks if it fails.
 *   - FAIL pages the operator. WARN never pages. Optional-secret checks
 *     WARN when the secret is absent so the cheap tier stays secret-free.
 *   - The cheap tier must stay safe to run every few minutes: no sends, no
 *     spend, no customer-visible side effects.
 */

const SITE = process.env.CANARY_SITE || "https://example.com"; // TODO: your site

const args = new Set(process.argv.slice(2));
const EXPENSIVE = args.has("--expensive");
const JSON_OUT = args.has("--json");

const results = [];

function record(name, state, surface, detail) {
  results.push({ name, state, surface, detail });
  if (!JSON_OUT) console.log(`${state.padEnd(4)} ${name} — ${detail}`);
}

async function fetchWithTimeout(url, opts = {}, ms = 30000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    return await fetch(url, { ...opts, signal: ctrl.signal });
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// CHEAP TIER — each check: guards <invariant>; breaks => <business impact>.
// ---------------------------------------------------------------------------

// Guards: the site is up. Breaks => every funnel is dark.
async function checkSiteRoot() {
  try {
    const res = await fetchWithTimeout(SITE + "/");
    record(
      "site_root",
      res.ok ? "PASS" : "FAIL",
      SITE + "/",
      res.ok ? `HTTP ${res.status}` : `HTTP ${res.status} — site down or erroring`,
    );
  } catch (err) {
    record("site_root", "FAIL", SITE + "/", `unreachable: ${err.name}`);
  }
}

// Guards: unknown paths return a REAL 404, not the homepage with 200.
// Breaks => ad QA, crawler hygiene, and uptime checks can't trust statuses.
async function checkSite404() {
  try {
    const res = await fetchWithTimeout(SITE + "/canary-known-missing-path");
    record(
      "site_404",
      res.status === 404 ? "PASS" : "FAIL",
      SITE,
      res.status === 404 ? "real 404 served" : `soft 404: HTTP ${res.status}`,
    );
  } catch (err) {
    record("site_404", "FAIL", SITE, `unreachable: ${err.name}`);
  }
}

// TODO: add YOUR money-path checks here. Patterns from a real business:
//   - a checkout/spend gate rejects requests missing its bot-wall token
//   - a config endpoint still serves the LIVE tracking/payment ids (a
//     silent revert to test mode screams instead of quietly failing)
//   - the lead/contact door validates input and supports a dryRun that
//     never sends (the canary must stay email-free)
//   - optional-secret check: read the secret from env; if unset, WARN and
//     return (soft pass) so the cheap tier needs no secrets.

const CHEAP = [checkSiteRoot, checkSite404];

// ---------------------------------------------------------------------------
// EXPENSIVE TIER — costs real money or quota; runs only with --expensive.
// ---------------------------------------------------------------------------

const COSTLY = [
  // TODO: e.g. one full generation/build against a stable canary slug.
];

const tiers = EXPENSIVE ? [...CHEAP, ...COSTLY] : CHEAP;
for (const check of tiers) await check();

const fails = results.filter((r) => r.state === "FAIL");
const warns = results.filter((r) => r.state === "WARN");
if (JSON_OUT) {
  console.log(
    JSON.stringify(
      { ok: fails.length === 0, fails: fails.length, warns: warns.length, results },
      null,
      2,
    ),
  );
} else {
  console.log(
    `\\n${fails.length === 0 ? "PASS" : "FAIL"} — ${results.length} checks, ` +
      `${fails.length} fail, ${warns.length} warn`,
  );
}
process.exit(fails.length === 0 ? 0 : 1);
"""

README_TEMPLATE = """# Canary — the golden-path guard

One command proves the money path is alive: `node canary/smoke.mjs`.

## The alert doctrine

- **Every alert is actionable.** A check exists only if its failure names a
  specific break and a specific fix. No vibes-based monitoring.
- **FAIL pages the operator. WARN never pages.** WARN is for soft
  conditions (an optional secret unset, a rate-limit hit) that must be
  visible without crying wolf.
- **Checks guard business invariants no platform synthetic can know** —
  "the checkout gate rejects an untrusted request", "the config endpoint
  still serves the LIVE payment mode" — not generic uptime, which your
  platform already watches.
- **The cheap tier is side-effect-free**: no sends, no spend, no
  customer-visible writes; safe on a tight schedule. Expensive checks run
  rarely, behind `--expensive`.
- **Optional secrets soft-pass.** A check that needs a secret WARNs when
  the secret is absent, so the cheap tier runs secret-free anywhere.

## Growing up: the scheduled Worker

When the business takes real money, promote this harness to a scheduled
worker (cron every ~15 min) with:

- an alert throttle (KV-backed) so a sustained break pages once, not every
  tick;
- a `/test-alert` route that proves the paging path end to end on demand;
- a `/simulate-break` route that forces one check to FAIL so you can watch
  the whole loop (check → throttle → page) before you need it for real.

Keep the checks in one runtime-agnostic module shared by this CLI smoke
test and the worker, so the two can never drift.

## Adding a check

Copy an existing check. The comment above it must answer: what invariant
does this guard, and what business impact appears when it breaks? If you
cannot answer, the check does not belong here.
"""


def init(repo: str | Path = ".", *, force: bool = False) -> dict[str, Any]:
    """Scaffold canary/smoke.mjs + canary/README.md in a business repo."""
    root = Path(repo).resolve()
    canary_dir = root / "canary"
    smoke_path = canary_dir / "smoke.mjs"
    readme_path = canary_dir / "README.md"
    existing = [str(p.relative_to(root)) for p in (smoke_path, readme_path) if p.exists()]
    if existing and not force:
        return {
            "ok": False,
            "repo": str(root),
            "written": [],
            "skipped": existing,
            "summary": (
                "canary files already exist; rerun with --force to overwrite "
                "(your checks live in smoke.mjs — overwriting loses them)"
            ),
        }
    canary_dir.mkdir(parents=True, exist_ok=True)
    smoke_path.write_text(SMOKE_TEMPLATE, encoding="utf-8")
    readme_path.write_text(README_TEMPLATE, encoding="utf-8")
    return {
        "ok": True,
        "repo": str(root),
        "written": [str(smoke_path.relative_to(root)), str(readme_path.relative_to(root))],
        "skipped": [],
        "summary": (
            "canary scaffold written — add your money-path checks to "
            "canary/smoke.mjs (see canary/README.md for the doctrine), then "
            "run `node canary/smoke.mjs`"
        ),
    }
