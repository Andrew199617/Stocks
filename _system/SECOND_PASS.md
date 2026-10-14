# Second pass — what it is and why it exists

The first pass is a standardized, filing-driven DCF (see README.md, DCF_AUDIT.md). It is
deliberately uniform, which means it structurally misses company-specific context that
doesn't show up in consolidated EDGAR facts. The second pass exists to catch exactly
that, in BOTH directions (hidden strength and hidden rot).

## What it hunts for
- **Segment growth masked by consolidated numbers** — a core segment compounding while a
  sunset / discontinued / legacy line drags consolidated growth (the Unity case: ads
  growing fast while a sunset legacy stack ate reported growth). Reverse case: a dying
  one-off segment flattering the consolidated total.
- **One-offs that aren't** — charges or gains pass 1 normalized away that actually recur;
  and "one-offs" that are really structural costs of the business.
- **Post-filing reality** — guidance changes, earnings-call disclosures, M&A, major
  customer wins/losses, product sunsets announced after the last filing pass 1 used.
- **SBC / dilution trajectory** vs the share-count adjustment pass 1 baked in.
- **Thin flag resolutions** — fragility flags pass 1 resolved on weak evidence get
  re-examined with targeted searches.

## Filing freshness — step 0, before the hunts (added 2026-10-13, Andrew)
Pass 1's numbers are only as fresh as its analysis date, and the sweep takes ~2 weeks
while earnings land. Run `python3 ~/workspace/stocks/_system/forensic_pull.py <TICKER>`
first — its Filing freshness section lists any 10-K/10-Q filed after pass 1's analysis
date with a newer period than pass 1 used, plus material 8-Ks (mergers, officer changes,
results, material agreements).
- **Newer periodic filing exists** → pass 1's base is stale by definition. Recompute the
  TTM owner's-earnings base filing-direct from the new filing (same YTD math as the v4
  TTM override: FY − prior-year YTD + current YTD for OCF, capex, SBC, shares) and treat
  any material base change as a finding: re-run the engine and log it like any other
  change. A base that barely moves still gets the recompute noted in second_pass.md.
- **Material 8-K only** → fold its content into the post-filing hunt; quantify or say
  why it doesn't move the numbers.

## Forensic battery — every run (added 2026-10-13, Andrew)
Andrew's fundamental-analysis checklist, baked in. `forensic_pull.py` computes the
filing-direct half automatically (paste its output into second_pass.md); the worker
resolves every tripped flag in writing and runs the judgment checks. The battery feeds
three things only: moat evidence, base-OE reconstruction, and confidence.
- **Margin structure** — gross margin level + trend (≥40% is the durable-advantage rule
  of thumb, judged sector-relative: a grocer and a software firm are not the same test);
  COGS % of revenue stability (swings in non-compounders = weak cost control = moat
  evidence AGAINST).
- **SG&A-vs-COGS split test (IBM pattern)** — if costs migrate between COGS and SG&A
  while combined (COGS+SG&A)/revenue is flat, it's presentation, not improvement; the
  combined series is the honest one.
- **NI vs operating income gap** — a persistent gap means noncore items (interest,
  investment gains/losses, one-offs) are carrying or dragging reported earnings.
  Interpret with care when operating income is near zero (the % explodes).
- **Prepaid battery** — prepaids % of assets, prepaids/SG&A, YoY and QoQ jumps. The
  deferral pattern is: prepaids spiking while earnings improve and OCF weakens, then
  reversing into expense later. Any leg of that pattern gets resolved in writing.
- **Divestiture / discontinued-ops optics (judgment)** — when a divestiture, held-for-
  sale line, or discontinued ops appears, compare pre / during / post on operating
  income, SG&A, CFO, and FCF, including stranded costs the parent still carries. State
  plainly: real improvement or accounting optics.
- **Noncore income reconstruction (judgment)** — build core revenue and core operating
  profit excluding interest, investment, financing, and one-time gains; track the
  noncore share over time. If noncore is material to the base, rebuild base OE on core
  numbers and log the change like any other.
- **Capitalized-cost shifting (judgment, WorldCom pattern)** — capex or capitalized
  balances (e.g. capitalized software) growing faster than revenue while SG&A/R&D fall
  and earnings outrun OCF. Any two legs together = hard look, in writing.
- **Standing cautions** — adding back S&M/R&D "growth spend" to owner's earnings is a
  sensitivity only; the headline base stays conservative unless evidence is unusually
  concrete. State which of pass 1's two OE definitions (total-capex vs maintenance) is
  the honest one for this business, and why. A hard forensic hit (deferral pattern,
  capitalized-cost shifting, noncore carrying the base) can force a downgrade on its
  own, logged like any other change.

## Authority (Andrew, 2026-10-13)
The second pass MAY change score.json directly when it finds something material.
Every change must be logged: old vs new inputs and outputs, the evidence, and sources,
in `~/workspace/stocks/<TICKER>/second_pass.md`, plus a `second_pass` object inside
score.json (date, prior/new tier, prior/new weighted IRR, summary). analysis.md gets a
dated addendum pointing to second_pass.md; pass-1 content is never rewritten silently.

## Rules
- Same v4 engine and sanity checks as pass 1 (scenario starts vs actual prints; a start
  below the latest print needs a written reason).
- No change without quantified evidence from filings or a cited source. Vibes don't move
  scores; a "no material finding" verdict with the checks listed is a valid outcome.
- Alerts: only when a change moves a company INTO Tier S/A (weighted IRR ≥20%) or OUT
  of Tier S/A. Everything else is silent; the daily ranking reflects the new numbers.
