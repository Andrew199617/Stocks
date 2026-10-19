#!/usr/bin/env python3
"""
Standardized owner's-earnings DCF engine v2 (screening grade, consistent across all companies).

Key correctness rules learned from the APP pilot:
- EDGAR companyfacts 'fy' is the FILING's fiscal year — comparative columns share it.
  All series are keyed by PERIOD END DATE, never by fy. Latest filing wins per period
  (so history is on the latest restated / continuing-operations basis).
- Price comes from the Nasdaq quote API (Stooq hangs from this VM); fallback = universe.csv price.
- Capex: if no PPE-capex line exists for a period but the company files a full cash-flow
  statement, capex is treated as 0 and flagged (asset-light filers like APP do this).

Outputs: <TICKER>/financials_history.csv, <TICKER>/dcf_numbers.json
Usage: python3 dcf_engine.py TICKER [--price 123.45] [--moat 0-10] [--probs sb,b,base,bull,sbull] [--offsets pp,pp,pp,pp,pp] [--mults x,x,x,x,x]

v3 (2026-10-12, Andrew's edit): FIVE scenarios (super_bear, bear, base, bull, super_bull), each with
an agent-assigned probability (must sum to 1.0). Headline value = probability-weighted expected
cash-flow path -> weighted IV at 10/12/15% and a probability-weighted implied IRR; the hurdle
tier comes from the WEIGHTED IRR (base-case IRR kept for reference).

v4 (2026-10-12, brittleness audit — full list in DCF_AUDIT.md):
- Base OE is the MEDIAN of the last 3 fiscal years' OE/share (normalized), not the single
  latest year. --base-oe-ps overrides with an agent-supplied TTM figure when the FY is stale.
- Growth is a BLEND: median of rev CAGR 5y, rev CAGR 3y, latest rev YoY, and OE/share CAGR,
  then adjusted for share-count trend (buybacks add, dilution subtracts, clamped ±5pp).
- Fade holds g0 for 2 years, then converges to terminal over the CAP in either direction.
- Candidate EDGAR tags are merged per period (tag switches no longer truncate history).
- Terminal growth is a parameter (--gterm, default 2.5%).
- Every run emits diagnostics + fragility_flags (stale FY, base divergence, low OE yield,
  TV share, scenario spread, leverage, dilution, basis breaks, volatility, thin history,
  sector mismatch). The analyzing agent must address every flag in analysis.md.
MOAT-DRIVEN FADE: revenue/OE growth does not fade on a fixed schedule. It fades linearly from
g0 to the 2.5% terminal rate over the Competitive Advantage Period CAP = clamp(2 + 1.3*moat, 2, 15)
years (moat 0 -> ~2y, moat 5 -> ~8.5y, moat 10 -> 15y), with a 15-year explicit projection.
The moat score (0-10) is the analyzing agent's judgment, justified in analysis.md — the engine
only turns it into fade math. Defaults if unflagged: moat 5, probs 10/25/30/25/10,
growth offsets -12/-5/0/+5/+12pp vs the capped historical base growth,
OE level multipliers 0.75/0.90/1.00/1.10/1.25.

v5 (2026-10-13, external audit — see README Fixes & lessons): DATA GATE. Missing data used
to become zero silently (capex assumed $0, SBC dropped from OE) and fake tiers shipped.
Now: SBC tries AllocatedShareBasedCompensationExpense as a fallback tag; capex tries
construction-in-process / other-productive-assets tags; the tag actually used is recorded
per period in the CSV. If SBC, capex or diluted shares are missing for ANY of the last 3
fiscal years, the price is unavailable, or the filer reports in a non-USD currency
(non-USD unit present on revenue/NI/OCF facts), the engine writes dcf_numbers.json with a
data_gap list + DATA_GAP:<field> fragility flags, tier_by_numbers = null, prints a
DATA_GAP line and exits 4 (price-only gap exits 3, like NO_DATA) — it NEVER emits a tier
on a data gap. Fragility flags are computed BEFORE the Tier F branch so F names carry
theirs too. Dates use America/New_York, not the VM's UTC clock.

v5.1 (2026-10-13, Andrew's override rule — code flags gaps, the agent decides, and
every decision lands in a field): judgment.json may carry structured overrides
(capex_override / sbc_override / shares_override, each {value, source, reason,
kind: "filing"|"estimate"}). An override fills ONLY periods where the filing tag is
absent (the CSV tag column records OVERRIDE for those periods) — it never replaces
a filed value. Gaps fully covered by overrides proceed with a tier; partially
covered gaps still exit 4 listing only the uncovered ones. dcf_numbers.json records
data_gap (the original gaps found), data_gap_uncovered, overrides_applied, and
override_impact — the DCF run both ways (zero-fill baseline vs with-override) on
the engine-native base. `--measure` runs the math with no file writes and no gate
exit (used for the impact runs); DCF_NO_OVERRIDES=1 disables override loading.

v5.2 (2026-10-14, round-2 re-audit — the gate's perimeter was narrower than
"incomplete data"): (1) OCF joins the gate — missing operating cash flow for
ANY of the last 3 FY is DATA_GAP:ocf, with
NetCashProvidedByUsedInOperatingActivitiesContinuingOperations as a fallback
tag (a continuing-ops-only filer previously got a fake Tier F); the tag used
is recorded as ocf_tag. (2) Override sanity bounds — a negative override is
refused outright; a value outside 0.1x-10x of the last FILED value for that
field (or with no filed value at all) is out of band, flagged
OVERRIDE_OUT_OF_BAND, and make_score refuses it without an ack_reason in
judgment.json. (3) TTM pin provenance — `--ttm` reads the base from
<TICKER>/ttm.json (written by ttm.py); make_score refuses a pinned base
that differs from ttm.json by >0.1% unless judgment.json declares a
base_override. (4) Currency check scoped to the last 3 FY (a stray 2016 EUR
fact blocked a whole company); foreign-form filers (20-F/40-F, from EDGAR
submissions) need an ads_ratio judgment field — the engine applies it to
per-share figures and records it, make_score refuses without one. (5) IRR
solver: value still above price at a 200% discount rate now returns a
capped 2.0 with an IRR_CAPPED flag instead of a blank that tiered D.
(6) Diluted shares missing with only BASIC shares filed is DATA_GAP:shares
(diluted) — no silent swap. (7) Provenance: dcf_numbers.json carries a
content_hash (sha256 over the canonical payload); make_score recomputes
and refuses on mismatch or absence.

v5.3 (2026-10-14, Andrew's IFRS go decision): period_series merges across
TAXONOMIES (us-gaap candidates first, then ifrs-full) the same way v4 merged
across tags, with an ifrs-full concept map for every field (Revenue,
ProfitLoss, CashFlowsFromUsedInOperatingActivities,
PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities,
AdjustmentsForSharebasedPayments, AdjustedWeightedAverageShares = the
diluted denominator, etc.). Currency: values keep their filed unit per
period. A filer whose monetary facts are filed in USD — including the
issuer's own USD convenience translations (JD files CNY + USD) — is no
longer a currency gap. A single non-USD reporting currency is converted to
USD at period-end ECB reference rates (frankfurter.app); the rates used
are recorded in dcf_numbers.json (fx_conversion) and flagged FX_CONVERTED.
Flow facts use the period-end rate too — a screening simplification the
agent must note. Mixed reporting currencies, or a currency with no ECB
rate, remain DATA_GAP:currency. ADS handling is unchanged (v5.2).
v5.3.1 (same day, Codex review of Stocks PR #1 — four fixes): units merge
per period within a tag (v5.3 picked one unit per tag and dropped
local-currency-only years); conversion eligibility is judged on the
last-3-FY core facts, not all history (one stray historical currency
disabled conversion entirely); monetary judgment overrides are declared
in the reporting currency and are FX-converted at the period-end rate
before being applied (v5.3 inserted them verbatim into USD series); the
override sanity band anchors on the last filed value in its filed unit.

2026-10-19 (insurer payable-earnings base, Andrew's decision; engine_release
stays 5.4.0 — no existing run changes): `--base-judgment` pins the base to the
judgment.json base_override of basis "payable_earnings_5y" (five filed annual
operating-income-to-common figures / latest diluted shares, scaled by the ADS
ratio), recomputed and checked here (`load_payable_base`,
`payable_base_per_share`), recorded as dcf_numbers.json `payable_base` with
base_source "judgment_base_override"; a declaration that does not reproduce,
a share count that is not this run's latest, or an FX-converted filer is
refused (BAD_BASE_OVERRIDE, exit 3). make_score.py verifies and measures it.

v5.4 (2026-10-14, formula audit of the whole engine — every item below is a
behaviour change and is recorded as engine_release "5.4.0"; engine_version
stays 5 for the data-gate check):
(1) Share-count adjustment was DOUBLE-COUNTED (audit round-1 "Model design",
    never fixed): the ±5pp buyback/dilution adjustment was added on top of a
    blend that already contains OE/share CAGR, which embeds the share-count
    trend. Now the adjustment is applied to the three REVENUE components only;
    the OE/share CAGR enters the median unadjusted.
(2) The v5.2 "basic-only shares = DATA_GAP" rule was DEAD CODE for almost every
    filer: a basic-only period fell through to CommonStockSharesOutstanding /
    dei cover-page counts and shipped a tier with no flag. Now any non-diluted
    share source in the last 3 FY is DATA_GAP:shares (the fallback count is
    named in the flag so a filing override is one lookup away); older periods
    may use a fallback for history, with the source recorded per period in a
    new shares_tag CSV column and a SHARES_FALLBACK flag. dei counts match a
    period only within 90 days after its end (they are cover-page dates).
(3) Debt: LongTermDebt (a TOTAL including current maturities) sat in the
    noncurrent candidate list and stacked on DebtCurrent. Total-debt tags are
    now a separate debt_total series used only when no noncurrent tag exists;
    short-term borrowings / commercial paper / lease-inclusive tags added;
    the basis is recorded per period (debt_tag column) and a period with no
    debt tag at all raises DEBT_TAGS_BLANK instead of a silent net-cash read.
(4) IRR floor: the terminal value used max(r - g, 0.005), so no IRR could be
    solved below terminal growth + 0.5% and names at that floor ranked on a
    fake ~3.0%. The Gordon value does not converge at r <= g; present_value
    now returns +inf there, the solver converges onto g, and the run is
    flagged IRR_AT_FLOOR (diagnostics.irr_at_floor) — the true IRR is at or
    below terminal growth.
(5) IRR band + hurdle prices: irr_bear / irr_bull / tier_bear / tier_bull are
    emitted next to the weighted headline (audit P2: rank on a band, not a
    point), plus weighted iv_at_20 / iv_at_25 — the prices at which the A and
    S hurdles clear — and the full 15-year per-share paths (paths) and growth
    schedules (growth_paths) for every scenario and the weighted case.
(6) Tier F is split: f_subtype "sbc_exceeds_cash" (OCF - capex > 0 but SBC
    eats it) vs "no_cash_generation" (OCF - capex <= 0) — different stories.
(7) Portability: BASE comes from $STOCKS_BASE or the script's parent folder,
    so the engine runs anywhere; the math is in module-level functions
    (project_path / present_value / solve_irr / tier_for_irr) that the HTML
    builder and the test-suite import — one implementation, no drift.
"""
import json, sys, os, csv, urllib.request, datetime, re, time, subprocess, hashlib, statistics
from zoneinfo import ZoneInfo

UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS = f"{BASE}/_system"
ENGINE_RELEASE = "5.4.0"
ET_TODAY = datetime.datetime.now(ZoneInfo("America/New_York")).date()
MEASURE = "--measure" in sys.argv   # compute + print JSON only: no file writes, no gate exit
HOLD_YEARS = 2          # v4: growth holds at g0 for 2 years before the fade starts
PROJECTION_YEARS = 15
DEFAULT_GTERM = 0.025
GROWTH_CAP_BASE = 0.35  # g_base cap (20% until 2026-10-12 — see README Fixes & lessons)
GROWTH_CAP_START = 0.50 # scenario start cap
GROWTH_FLOOR_BASE, GROWTH_FLOOR_START = -0.05, -0.10


# ---------------------------------------------------------------------------
# Valuation math (module-level so make_score / build_daily_html / tests import
# the SAME functions the engine runs — v5.4).
# ---------------------------------------------------------------------------
def growth_path(g0, cap_years, gterm=DEFAULT_GTERM, n=PROJECTION_YEARS, hold=HOLD_YEARS):
    """Per-year growth rate: holds at g0 for `hold` years, then converges
    linearly to gterm over cap_years — in either direction, never overshooting."""
    step = (g0 - gterm) / cap_years if cap_years > 0 else (g0 - gterm)
    out = []
    for t in range(1, n + 1):
        g = g0 - step * max(0, t - hold)
        g = min(g, g0) if g0 > gterm else max(g, g0)      # never overshoot past g0
        g = max(g, gterm) if g0 > gterm else min(g, gterm)  # never cross past terminal
        out.append(g)
    return out


def project_path(oe0, g0, cap_years, gterm=DEFAULT_GTERM, n=PROJECTION_YEARS, hold=HOLD_YEARS):
    """15 per-share owner's-earnings flows from base oe0 along growth_path()."""
    flows, cur = [], oe0
    for g in growth_path(g0, cap_years, gterm, n, hold):
        cur *= (1 + g); flows.append(cur)
    return flows


def present_value(flows, r, gterm=DEFAULT_GTERM):
    """PV of the explicit flows plus a Gordon terminal value on the last flow.
    v5.4: the terminal value does not converge at r <= gterm — the old
    max(r - g, 0.005) floor manufactured a finite value there and no IRR
    could be solved below g + 0.5%. +inf is the honest answer."""
    if r <= gterm:
        return float("inf")
    v = sum(f / (1 + r) ** (t + 1) for t, f in enumerate(flows))
    tv = flows[-1] * (1 + gterm) / (r - gterm)
    return v + tv / (1 + r) ** len(flows)


def terminal_share(flows, r, gterm=DEFAULT_GTERM):
    total = present_value(flows, r, gterm)
    if not total or total == float("inf"):
        return None
    tv = flows[-1] * (1 + gterm) / (r - gterm) / (1 + r) ** len(flows)
    return tv / total


def solve_irr(flows, px, gterm=DEFAULT_GTERM):
    """(irr, capped, at_floor). capped: value at a 200% rate still exceeds
    the price (round-2 fix — recorded as 2.0, not blank). at_floor (v5.4):
    the bisection converged onto the Gordon boundary, i.e. the true IRR is at
    or below terminal growth; the returned value is the floor, not a solution."""
    if present_value(flows, 2.0, gterm) > px:
        return 2.0, True, False
    lo, hi = -0.5, 2.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if present_value(flows, mid, gterm) > px: lo = mid
        else: hi = mid
    irr = (lo + hi) / 2
    # A perpetuity growing at g has an IRR above g at ANY finite price, so the
    # model cannot express a return below g_terminal: anything within 0.5pp of
    # it (the region the old 0.005 denominator floor distorted) is "at floor".
    return irr, False, (irr - gterm) <= 0.005 + 1e-12


def tier_for_irr(irr):
    if irr is None:
        return None
    return "S" if irr >= 0.25 else "A" if irr >= 0.20 else "B" if irr >= 0.15 else "C" if irr >= 0.10 else "D"


def cap_years_for_moat(moat):
    """Competitive advantage period: clamp(2 + 1.3 * moat, 2, 15) years."""
    moat = max(0.0, min(10.0, float(moat)))
    return max(2.0, min(15.0, 2 + 1.3 * moat))


def replay_paths(numbers):
    """(paths, growth_paths) for a recorded dcf_numbers.json payload — the
    flows the scored run discounted, replayed from its recorded inputs
    exactly as the engine computed them (g0 = clamp(g_base + offset),
    project_path(base * mult, g0, CAP(moat), g_terminal), weighted =
    probability-weighted sum). Mirrors build_daily_html.forecast_paths; used
    by reprice.py so the live IRR is solved on the SAME flows as the scored
    IRR (bit-for-bit at the scored price).

    Engine 5.4 also stores `paths` / `growth_paths`, rounded to 6 decimals
    for the file. Those are the fallback, not the first choice: the replay
    is exact, the stored copy is not. The stored copy is returned only when
    the inputs are missing (a hand-built or foreign record) or when the
    replay disagrees with it beyond rounding (the record is the engine's
    own output and wins over a drifted replay). (None, None) when neither
    is available. Additive (v5.4 reprice)."""
    if not isinstance(numbers, dict):
        return None, None
    stored = None
    if numbers.get("paths") and numbers.get("growth_paths"):
        stored = (numbers["paths"], numbers["growth_paths"])
    inp, scn = numbers.get("inputs") or {}, numbers.get("scenarios") or {}
    try:
        base = float(numbers.get("base_oe_per_share"))
        gb = float(numbers.get("g_base"))
    except (TypeError, ValueError):
        return stored or (None, None)
    if not inp or not scn:
        return stored or (None, None)
    labels = ["super_bear", "bear", "base", "bull", "super_bull"]
    gterm = inp.get("g_terminal", DEFAULT_GTERM)
    cap = cap_years_for_moat(inp.get("moat", 5))
    paths, gpaths = {}, {}
    try:
        for i, k in enumerate(labels):
            g0 = max(GROWTH_FLOOR_START, min(GROWTH_CAP_START, gb + inp["offsets"][i]))
            paths[k] = project_path(base * inp["mults"][i], g0, cap, gterm)
            gpaths[k] = growth_path(g0, cap, gterm)
        probs = inp["probs"]
        paths["weighted"] = [sum(probs[i] * paths[labels[i]][t] for i in range(5)) for t in range(len(paths["base"]))]
    except Exception:
        return stored or (None, None)
    if stored is not None and not _paths_agree(paths, stored[0]):
        return stored
    return paths, gpaths


def _paths_agree(replayed, stored, tol=1e-5):
    """True when every stored path (rounded to 6 dp by the engine) matches the
    replayed one within `tol` per flow — i.e. they differ only by rounding."""
    try:
        for k, flows in stored.items():
            rep = replayed.get(k)
            if rep is None or len(rep) != len(flows):
                return False
            if any(abs(float(a) - float(b)) > tol * max(1.0, abs(float(b))) for a, b in zip(rep, flows)):
                return False
        return True
    except (TypeError, ValueError, AttributeError):
        return False

def load_overrides(ticker):
    """Structured judgment overrides from {ticker}/judgment.json. A malformed or
    incomplete override (non-numeric value, kind outside filing|estimate, blank
    source/reason) is ignored here; make_score.py validates strictly and refuses
    on any disagreement between judgment.json and what the engine applied."""
    if os.environ.get("DCF_NO_OVERRIDES"):
        return {}
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for field, key in (("capex", "capex_override"), ("sbc", "sbc_override"), ("shares", "shares_override")):
        o = j.get(key) if isinstance(j, dict) else None
        if (isinstance(o, dict) and isinstance(o.get("value"), (int, float))
                and not isinstance(o.get("value"), bool)
                and o.get("kind") in ("filing", "estimate")
                and str(o.get("source") or "").strip() and str(o.get("reason") or "").strip()):
            out[field] = {"value": float(o["value"]), "kind": o["kind"],
                          "source": o["source"], "reason": o["reason"],
                          "ack_reason": str(o["ack_reason"]).strip() if isinstance(o.get("ack_reason"), str) and o["ack_reason"].strip() else None}
    return out

PAYABLE_BASIS = "payable_earnings_5y"
# SIC codes the payable-earnings rule is scoped to (P&C insurers and reinsurers):
# 6331 Fire, Marine & Casualty Insurance; 6351 Surety Insurance. Life (6311),
# accident & health (6321), banks and REITs keep the OCF base + notch rule.
PAYABLE_SIC = frozenset({"6331", "6351"})

def payable_base_per_share(figures, shares, ads_ratio=None):
    """Insurer payable-earnings base (Andrew, 2026-10-19): the average of the
    last five fiscal years' operating income available to common shareholders
    (filing USD, dollars) over the latest diluted share count, scaled by the
    ADS ratio so the pin is comparable to the traded price (per-share pins are
    not scaled anywhere else — see the ADS flag text)."""
    figs = [float(x) for x in figures]
    if len(figs) != 5 or not shares or float(shares) <= 0:
        raise ValueError("payable base needs exactly five annual figures and a positive share count")
    ratio = float(ads_ratio["ratio"]) if ads_ratio else 1.0
    return sum(figs) / 5.0 / float(shares) * ratio

def load_payable_base(ticker):
    """judgment.json base_override with basis payable_earnings_5y:
    {value (per ORDINARY share, filing USD), kind "filing", basis, figures [5],
    shares, source, reason}. Returns the dict, or raises ValueError naming the
    defect — the engine refuses the run rather than guessing."""
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"judgment.json unreadable ({e})")
    o = j.get("base_override") if isinstance(j, dict) else None
    if not isinstance(o, dict):
        raise ValueError("judgment.json carries no base_override object")
    if o.get("basis") != PAYABLE_BASIS:
        raise ValueError(f"base_override.basis must be {PAYABLE_BASIS!r}")
    if o.get("kind") != "filing":
        raise ValueError("base_override.kind must be 'filing' (the figures come from the filer's releases / 10-K)")
    figs = o.get("figures")
    if not (isinstance(figs, list) and len(figs) == 5
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in figs)):
        raise ValueError("base_override.figures must list exactly five annual operating-income-to-common figures (dollars)")
    if not isinstance(o.get("shares"), (int, float)) or isinstance(o.get("shares"), bool) or o["shares"] <= 0:
        raise ValueError("base_override.shares must be the latest diluted share count (a positive number)")
    if not isinstance(o.get("value"), (int, float)) or isinstance(o.get("value"), bool):
        raise ValueError("base_override.value must be a number (per ordinary share)")
    if not str(o.get("source") or "").strip() or not str(o.get("reason") or "").strip():
        raise ValueError("base_override.source and .reason must be non-empty")
    per_ord = sum(float(x) for x in figs) / 5.0 / float(o["shares"])
    if abs(per_ord - float(o["value"])) > 0.005:  # cent-level: the construction must reproduce to the cent
        raise ValueError(f"base_override.value {o['value']} does not reproduce from figures/shares ({per_ord:.6f}) to the cent")
    o = dict(o); o["value"] = per_ord  # the recomputed figure is the one recorded and pinned
    return o

def load_ads_ratio(ticker):
    """ads_ratio from judgment.json ({ratio, source, reason}) for foreign-form
    filers: ratio = ordinary shares per ADS. Per-share EDGAR figures for a
    20-F/40-F filer are per ordinary share while the traded price is per ADS."""
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json", encoding="utf-8"))
    except Exception:
        return None
    a = j.get("ads_ratio") if isinstance(j, dict) else None
    if (isinstance(a, dict) and isinstance(a.get("ratio"), (int, float))
            and not isinstance(a.get("ratio"), bool) and float(a["ratio"]) > 0
            and str(a.get("source") or "").strip() and str(a.get("reason") or "").strip()):
        return {"ratio": float(a["ratio"]), "source": a["source"], "reason": a["reason"]}
    return None


def market_cap_est(price, shares, ads_ratio=None, fallback=None):
    """Traded market cap. `price` is per traded unit — per ADS for a
    foreign-form filer — while `shares` is the ordinary share count from
    EDGAR, so when an ads_ratio applies the ordinary count is divided by
    it (ordinary shares / shares-per-ADS = ADS count; x per-ADS price =
    traded cap). No ratio (or ratio 1) is the identity — bit-identical to
    the pre-fix price * shares. Missing price/shares returns `fallback`
    (the universe screener cap, already a traded cap, never rescaled)."""
    if price and shares:
        ratio = ads_ratio["ratio"] if ads_ratio else 1.0
        return price * shares / ratio
    return fallback

def _content_hash(payload):
    """sha256 over the canonical dcf_numbers payload (everything except the
    hash itself). make_score.py recomputes it and refuses on mismatch or
    absence — hand-edited numbers cannot pass as engine output."""
    canon = json.dumps({k: v for k, v in payload.items() if k != "content_hash"},
                       sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canon.encode()).hexdigest()

def _measure_run(ticker, price, no_overrides):
    """Re-run this engine in --measure mode (no writes, no gate exit) and return
    (base_oe_per_share, implied_irr_weighted). --base-oe-ps is dropped: the impact
    measurement compares the engine-native bases of the two worlds."""
    args = [sys.executable, os.path.abspath(__file__)]
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--base-oe-ps":
            i += 2
            continue
        if argv[i] in ("--measure", "--ttm", "--base-judgment"):  # pin sources like --base-oe-ps: dropped
            i += 1
            continue
        args.append(argv[i])
        i += 1
    if "--price" not in argv and price is not None:
        args += ["--price", repr(price)]
    args.append("--measure")
    env = dict(os.environ)
    if no_overrides:
        env["DCF_NO_OVERRIDES"] = "1"
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=600, env=env)
        txt = out.stdout or ""
        j = json.loads(txt[txt.index("{"):])
        return j.get("base_oe_per_share"), j.get("implied_irr_weighted")
    except Exception:
        return None, None

def _override_impact(ticker, price, headline_base, headline_irr):
    zb, zi = _measure_run(ticker, price, True)
    if "--base-oe-ps" in sys.argv or "--base-judgment" in sys.argv:
        # Any pin: replay the with-override world on the engine-native base too,
        # so both sides of this block are on the same (native) basis.
        fb, fi = _measure_run(ticker, price, False)
    else:
        fb, fi = headline_base, headline_irr
    return {"base_oe_per_share_zero_fill": zb, "base_oe_per_share_final": fb,
            "weighted_irr_zero_fill": zi, "weighted_irr_final": fi,
            "basis": "engine-native normalized base (median of last 3 FY) and weighted IRR, DCF run both ways (zero-fill baseline vs with-override); a --base-oe-ps TTM base or a --base-judgment payable base is excluded from both sides — its override effect shows in ttm.py output / make_score's payable_5y impact"}

def filer_sic(cik):
    """(sic, sicDescription) from EDGAR submissions — the authoritative industry
    code the payable-earnings rule is gated on (PAYABLE_SIC)."""
    try:
        sub = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
        return (str(sub.get("sic") or "") or None), (sub.get("sicDescription") or None)
    except Exception:
        return None, None

def filer_annual_form(cik):
    """The filer's most recent annual form (10-K / 20-F / 40-F) from EDGAR
    submissions — foreign-form filers need ADS-ratio handling (see ads_ratio)."""
    try:
        sub = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
        for f in sub.get("filings", {}).get("recent", {}).get("form", []):
            if f in ("10-K", "10-K/A", "20-F", "40-F"):
                return f.replace("/A", "")
    except Exception:
        pass
    return None

def get_json(url, headers=UA, timeout=90):
    last = None
    for attempt in range(3):  # simple retry with backoff on transient EDGAR/Nasdaq failures
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            if attempt < 2: time.sleep(2 ** attempt)
    raise last

_fx_cache = {}
def fx_rate(ccy, date_str):
    """ccy->USD rate on date_str from frankfurter.app (ECB reference rates;
    returns the closest available business day). None when the currency is
    not ECB-covered or the fetch fails — the caller keeps the currency gap."""
    key = (ccy, date_str)
    if key in _fx_cache: return _fx_cache[key]
    rate = None
    try:
        d = get_json(f"https://api.frankfurter.app/{date_str}?from={ccy}&to=USD", timeout=30)
        rate = float(d["rates"]["USD"])
    except Exception:
        rate = None
    _fx_cache[key] = rate
    return rate

def nasdaq_price(ticker):
    try:
        d = get_json(f"https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks", headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
        p = d.get("data", {}).get("primaryData", {}).get("lastSalePrice", "")
        return float(p.replace("$", "").replace(",", ""))
    except Exception:
        return None

# Codex review of PR #2 (HBAN FY2025: net debt read on 17.221B of debt while the
# statements pipeline shows 18.482B): the debt_total tags are of two kinds. A
# LONG-TERM total (LongTermDebt, LongTermDebtAndCapitalLeaseObligationsIncluding-
# CurrentMaturities) carries the current maturities of long-term debt but not
# the short-term borrowings a filer reports on their own line (debt_cur_st:
# ShortTermBorrowings / CommercialPaper / NotesPayableCurrent / IFRS
# ShorttermBorrowings), so those are added — never the current maturities,
# which are inside it. An aggregate of long- AND short-term debt
# (DebtLongtermAndShorttermCombinedAmount, IFRS Borrowings) stands alone.
# Debt feeds diagnostics only (net_debt_latest, HIGH_NET_DEBT / BIG_NET_CASH):
# no valuation input moves, so engine_release stays 5.4.0.
LT_DEBT_TOTAL_TAGS = frozenset({"LongTermDebt", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"})


def debt_from_total_tag(tot, tot_tag, st=None, st_tag=None, same_unit=True):
    """(total debt, debt_tag) for a period whose only long-term figure is a
    debt_total tag; st = the short-term-borrowings component (debt_cur_st) and
    same_unit = whether it is in tot's unit after the FX pass (never added
    across currencies)."""
    if tot_tag in LT_DEBT_TOTAL_TAGS and st is not None:
        if same_unit:
            return tot + st, f"TOTAL:{tot_tag}+{st_tag}"
        return tot, f"TOTAL:{tot_tag} (short-term {st_tag} filed in another unit, not added)"
    return tot, f"TOTAL:{tot_tag}"

def period_series(facts, tags, duration=True):
    """({period_end: value}, first_used_tag, {period_end: tag}, {period_end: unit}) —
    annual periods only, latest filing wins. v4: MERGES across candidate tags per
    period (in priority order). v3 returned only the first tag that had any data,
    silently truncating history when a filer switched tags. v5: also returns which
    tag supplied each period (provenance — the audit found used_tags hiding years
    that were silently zero-filled). v5.3: `tags` items are either "Tag" (us-gaap)
    or ("taxonomy", "Tag") pairs, merged across taxonomies in priority order;
    values stay in their filed unit and the unit used per period is returned so
    the caller can FX-convert non-USD periods."""
    merged, used, tag_by_period, unit_by_period = {}, None, {}, {}
    pairs = [(t if isinstance(t, tuple) else ("us-gaap", t)) for t in tags]
    for taxonomy, tag in pairs:
        tax_facts = facts.get("facts", {}).get(taxonomy, {})
        if tag not in tax_facts: continue
        units = tax_facts[tag].get("units", {})
        # v5.3.1 (Codex review of Stocks PR #1): units merge PER PERIOD, in
        # preference order — v5.3 picked ONE unit per tag, so a tag with USD
        # facts for some years and local-currency facts for others silently
        # dropped the local-only years. USD wins a period when it has one;
        # other units fill the periods USD lacks, with the unit recorded.
        pref = [u for u in ("USD", "shares", "USD/shares") if u in units]
        pref += [u for u in units if u not in pref]
        for unit_key in pref:
            best = {}
            for e in units[unit_key]:
                if e.get("fp") != "FY": continue
                if e.get("form", "") not in ("10-K", "10-K/A", "20-F", "40-F"): continue
                end = e.get("end"); start = e.get("start")
                if not end: continue
                if duration:
                    if not start: continue
                    days = (datetime.date.fromisoformat(end) - datetime.date.fromisoformat(start)).days
                    if not (330 <= days <= 380): continue
                else:
                    if start and start != end: continue
                prev = best.get(end)
                if prev is None or e.get("filed", "") > prev.get("filed", ""):
                    best[end] = e
            for k, v in best.items():
                if k not in merged:
                    merged[k] = v["val"]
                    tag_by_period[k] = tag
                    unit_by_period[k] = unit_key
                    if used is None: used = tag
    return merged, used, tag_by_period, unit_by_period

def main():
    ticker = sys.argv[1].upper()
    price_arg = float(sys.argv[sys.argv.index("--price") + 1]) if "--price" in sys.argv else None

    uni = {}
    with open(f"{SYS}/universe.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f): uni[row["ticker"]] = row
    sec = json.load(open(f"{SYS}/sec_tickers_exchange.json", encoding="utf-8"))
    cik_by_ticker = {}
    for rec in sec["data"]: cik_by_ticker.setdefault(rec[2].upper(), rec[0])
    cik = None
    if "--cik" in sys.argv:  # agent-supplied override for entity/CIK-change cases (see NO_DATA)
        cik = int(sys.argv[sys.argv.index("--cik") + 1])
    else:
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in cik_by_ticker: cik = cik_by_ticker[cand]; break
    if cik is None and ticker in uni and uni[ticker].get("cik"): cik = int(uni[ticker]["cik"])
    if cik is None: print(f"NO_CIK for {ticker}"); sys.exit(2)

    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    name = facts.get("entityName", (uni.get(ticker) or {}).get("name", ticker))
    cik_fallback_note = None
    # v4.1: CIK/entity trap (found on XOM): the tickers file can map a ticker to a NEW holding-
    # company CIK with no filing history (2026: XOM -> ExxonMobil Holdings Corp, CIK 2115436,
    # while all history sits under CIK 34088). If the primary CIK yields <3 years of net income,
    # probe the older company_tickers.json mapping and use whichever CIK has more history.
    def _ni_periods(f):
        s, _, _, _ = period_series(f, ["NetIncomeLoss", "ProfitLoss", ("ifrs-full", "ProfitLoss")], True)
        return len(s)
    if _ni_periods(facts) < 3:
        try:
            alt_list = get_json("https://www.sec.gov/files/company_tickers.json")
            alt_cik = None
            for rec in alt_list.values():
                if rec.get("ticker", "").upper() == ticker: alt_cik = int(rec["cik_str"]); break
            if alt_cik and alt_cik != cik:
                alt_facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{alt_cik:010d}.json")
                if _ni_periods(alt_facts) > _ni_periods(facts):
                    cik_fallback_note = f"CIK_FALLBACK: tickers_exchange CIK {cik} ({name}) has thin history; used CIK {alt_cik} ({alt_facts.get('entityName')}) instead — verify this is the right operating parent"
                    facts, cik = alt_facts, alt_cik
                    name = facts.get("entityName", name)
        except Exception:
            pass

    # v5.3: each field's candidates are us-gaap tags first, then ("ifrs-full", tag)
    # pairs — period_series merges across both in this priority order. IFRS picks
    # verified against real companyfacts pulls (CCJ / TECK / GFI) 2026-10-14:
    # AdjustedWeightedAverageShares is the DILUTED denominator (one value per
    # period, consistently just above basic WeightedAverageShares);
    # AdjustmentsFor* are the cash-flow-statement addbacks, the same role the
    # us-gaap ShareBasedCompensation / DDA tags play.
    IF = "ifrs-full"
    dur_defs = {
        "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax",
                    (IF, "Revenue"), (IF, "RevenueFromContractsWithCustomers")],
        "net_income": ["NetIncomeLoss", "ProfitLoss", (IF, "ProfitLoss")],
        "operating_income": ["OperatingIncomeLoss", (IF, "ProfitLossFromOperatingActivities")],
        # v5.2: continuing-operations OCF as fallback — a filer tagging OCF only
        # there previously produced oe_cons = None and a fake Tier F (round-2).
        "ocf": ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                (IF, "CashFlowsFromUsedInOperatingActivities"), (IF, "CashFlowsFromUsedInOperatingActivitiesContinuingOperations")],
        # v5: construction-in-process (ED files capex there FY23+) and other-productive-assets
        # (ROP) added as fallbacks — both verified against real companyfacts pulls 2026-10-13.
        "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForConstructionInProcess", "PaymentsToAcquireOtherPropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsToAcquireOtherProductiveAssets",
                  (IF, "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"), (IF, "PurchaseOfPropertyPlantAndEquipment"),
                  (IF, "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets")],
        "da": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization", "Depreciation",
               (IF, "AdjustmentsForDepreciationAndAmortisationExpense"), (IF, "DepreciationAndAmortisationExpense")],
        # v5: DFTX and many others file SBC only under the allocated tag.
        "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense",
                (IF, "AdjustmentsForSharebasedPayments"), (IF, "ExpenseFromSharebasedPaymentTransactionsWithEmployees")],
        "tax": ["IncomeTaxExpenseBenefit", (IF, "IncomeTaxExpenseContinuingOperations"), (IF, "IncomeTaxExpense")],
        "shares_diluted": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingDiluted", "WeightedAverageNumberOfSharesOutstandingBasic",
                           (IF, "AdjustedWeightedAverageShares"), (IF, "WeightedAverageShares")],
    }
    inst_defs = {
        "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", (IF, "CashAndCashEquivalents")],
        # Codex review of PR #2: the combined cash+restricted fallback must not be
        # netted against debt as if it were free — restricted cash is tracked and
        # subtracted when tagged, flagged when not (see the per-period loop).
        "restricted_cash": ["RestrictedCashAndCashEquivalents", "RestrictedCash", "RestrictedCashAndCashEquivalentsAtCarryingValue",
                            "RestrictedCashCurrent", (IF, "RestrictedCashAndCashEquivalents")],
        "assets_current": ["AssetsCurrent", (IF, "CurrentAssets")],
        "liab_current": ["LiabilitiesCurrent", (IF, "CurrentLiabilities")],
        # v5.4 debt: CURRENT and NONCURRENT candidate lists hold only tags of
        # that classification; TOTAL tags (LongTermDebt includes current
        # maturities; the audit found it stacking on DebtCurrent) live in
        # debt_total and are used only when no noncurrent tag reports.
        # Codex review of PR #2: current debt is an AGGREGATE tag when filed; when
        # it is not, the components are ADDITIVE (current maturities of long-term
        # debt + short-term borrowings) and must be summed, not treated as
        # fallbacks that keep only the first one present. Within each component
        # group the tags are alternatives (one of them per period).
        "debt_current": ["DebtCurrent", (IF, "CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings")],
        "debt_cur_ltd": ["LongTermDebtAndCapitalLeaseObligationsCurrent", "LongTermDebtCurrent", (IF, "CurrentPortionOfLongtermBorrowings")],
        "debt_cur_st": ["ShortTermBorrowings", "CommercialPaper", "NotesPayableCurrent", (IF, "ShorttermBorrowings")],
        "debt_lt": ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations", "LongTermNotesPayable",
                    (IF, "LongtermBorrowings"), (IF, "NoncurrentPortionOfNoncurrentBorrowings")],
        "debt_total": ["LongTermDebt", "DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
                       (IF, "Borrowings")],
        "lease_liab_current": ["OperatingLeaseLiabilityCurrent", (IF, "CurrentLeaseLiabilities")],
        "lease_liab_lt": ["OperatingLeaseLiabilityNoncurrent", (IF, "NoncurrentLeaseLiabilities")],
        "assets": ["Assets", (IF, "Assets")],
        "liabilities": ["Liabilities", (IF, "Liabilities")],
        "ppe_net": ["PropertyPlantAndEquipmentNet", (IF, "PropertyPlantAndEquipment")],
        "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", (IF, "Equity")],
        "shares_out_inst": ["CommonStockSharesOutstanding", (IF, "NumberOfSharesOutstanding")],
    }
    DILUTED_SHARE_TAGS = {"WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingDiluted",
                          "AdjustedWeightedAverageShares", "OVERRIDE"}
    # Tags that carry only a BASIC share count — a period sourced from one is a
    # shares (diluted) gap, never a silent swap (v5.2 rule, extended to IFRS).
    BASIC_SHARE_TAGS = {"WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageShares"}
    series, used, series_tags, series_units = {}, {}, {}, {}
    for k, tags in dur_defs.items(): series[k], used[k], series_tags[k], series_units[k] = period_series(facts, tags, True)
    for k, tags in inst_defs.items(): series[k], used[k], series_tags[k], series_units[k] = period_series(facts, tags, False)
    annual_form = filer_annual_form(cik)
    ads_ratio = load_ads_ratio(ticker)
    # Currency handling is v5.3 (see the FX conversion pass below and the gate):
    # filed units are tracked per period in series_units; the issuer's own USD
    # translations are used as filed, and a single foreign reporting currency
    # is converted at period-end ECB rates. The pre-v5.3 rule (any non-USD unit
    # on core facts in the last 3 FY = gap) is gone.
    # v4.2 share-count fallback: some filers (XOM) stopped tagging weighted diluted shares in
    # XBRL years ago. Fill missing years from dei EntityCommonStockSharesOutstanding (instant).
    dei_shares = {}
    try:
        dei = facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
        for unit_vals in dei.get("units", {}).values():
            for e in unit_vals:
                end = e.get("end")
                if end and (end not in dei_shares or e.get("filed", "") > dei_shares[end][0]):
                    dei_shares[end] = (e.get("filed", ""), e["val"])
        dei_shares = {k: v[1] for k, v in dei_shares.items()}
    except Exception:
        dei_shares = {}

    def dei_for_period(p):
        """v5.4: dei EntityCommonStockSharesOutstanding is dated by the COVER
        PAGE, not the period end (audit: it rarely matched a period). Accept
        the earliest cover-page count within 90 days AFTER the period end."""
        try:
            pe = datetime.date.fromisoformat(p)
        except Exception:
            return None, None
        best = None
        for d, v in dei_shares.items():
            try:
                dd = datetime.date.fromisoformat(d)
            except Exception:
                continue
            lag = (dd - pe).days
            if 0 <= lag <= 90 and (best is None or lag < best[0]):
                best = (lag, v, d)
        return (best[1], best[2]) if best else (None, None)
    latest_dei = max(dei_shares.items(), key=lambda kv: kv[0]) if dei_shares else None

    # v5.3.1 (Codex review of Stocks PR #1): the override sanity band anchors
    # on the last FILED value in its FILED unit, captured here before the FX
    # pass converts the series — override values are declared in the filer's
    # reporting currency, so a post-conversion (USD) anchor compares unlike
    # units and misjudges the band on every converted name.
    last_filed_raw, last_filed_unit = {}, {}
    for _k in ("capex", "sbc", "shares_diluted"):
        _ps = [p for p in sorted(series[_k]) if series[_k][p] is not None]
        if _ps:
            last_filed_raw[_k] = series[_k][_ps[-1]]
            last_filed_unit[_k] = series_units.get(_k, {}).get(_ps[-1])

    # ---- v5.3 FX conversion: monetary series are in filed units (series_units).
    # A single non-USD reporting currency is converted to USD at period-end ECB
    # rates; flow facts use the period-end rate too (screening simplification,
    # flagged FX_CONVERTED). Dates with no available rate stay unconverted and
    # the currency gate below decides whether they matter (last-3-FY core facts).
    monetary_keys = [k for k in list(dur_defs) + list(inst_defs) if k not in ("shares_diluted", "shares_out_inst")]
    filed_currencies = set()
    for k in monetary_keys:
        for u in series_units.get(k, {}).values():
            if u not in ("USD", "shares", "USD/shares"): filed_currencies.add(u)
    # v5.3.1 (Codex review of Stocks PR #1): conversion eligibility is decided
    # by the last-3-FY CORE facts (revenue / net income / OCF), not by every
    # currency anywhere in history — one stray historical second-currency fact
    # used to disable conversion for a filer that is single-currency today.
    # Exactly one recent core currency: convert it, plus any stray-currency
    # periods elsewhere, each at its own period-end rate. Two or more: a
    # genuinely mixed filer — convert nothing and let the gate fire. No recent
    # core currency (core filed as USD translations): fall back to the
    # all-history set (the JD shape — USD core, one CNY-only debt series).
    _core_periods = sorted({p for k in ("revenue", "net_income", "ocf") for p in series.get(k, {})})[-3:]
    recent_core_ccys = {series_units[k][p] for k in ("revenue", "net_income", "ocf")
                        for p in _core_periods
                        if series_units.get(k, {}).get(p) not in (None, "USD", "shares", "USD/shares")}
    if len(recent_core_ccys) == 1:
        conv_ccys = set(filed_currencies)
    elif len(recent_core_ccys) == 0 and len(filed_currencies) == 1:
        conv_ccys = set(filed_currencies)
    else:
        conv_ccys = set()
    fx_info, fx_unconverted_dates, fx_converted_periods = None, set(), set()
    if conv_ccys:
        rates_by_ccy = {}
        for ccy in sorted(conv_ccys):
            need_dates = sorted({p for k in monetary_keys for p, u in series_units.get(k, {}).items() if u == ccy})
            rates = {}
            for d in need_dates:
                r = fx_rate(ccy, d)
                if r is None: fx_unconverted_dates.add(d)
                else: rates[d] = r
            if rates: rates_by_ccy[ccy] = rates
        if rates_by_ccy:
            converted_fields = []
            for k in monetary_keys:
                for p, u in list(series_units.get(k, {}).items()):
                    r = (rates_by_ccy.get(u) or {}).get(p)
                    if r is not None and series[k].get(p) is not None:
                        series[k][p] = series[k][p] * r
                        fx_converted_periods.add((k, p))
                        if k not in converted_fields: converted_fields.append(k)
            primary = next(iter(recent_core_ccys)) if recent_core_ccys else next(iter(conv_ccys))
            fx_info = {"from_currency": primary, "to_currency": "USD",
                       "source": "frankfurter.app — ECB reference rates (closest business day to each period end)",
                       "converted_fields": converted_fields,
                       "rates": rates_by_ccy.get(primary, {}),
                       "rates_by_currency": rates_by_ccy}
    # Did the engine rely on the issuer's own USD convenience translations?
    # (A core tag whose filed units include both USD and a foreign currency,
    # with USD the unit actually used — e.g. JD's CNY + USD.)
    usd_translation_used = False
    for k in ("revenue", "net_income", "ocf"):
        for t in dur_defs[k]:
            tax, tag = t if isinstance(t, tuple) else ("us-gaap", t)
            unit_keys = list((facts.get("facts", {}).get(tax, {}).get(tag) or {}).get("units", {}).keys())
            if "USD" in unit_keys and any(u not in ("USD", "shares", "USD/shares") for u in unit_keys):
                usd_translation_used = True

    periods = sorted(set(series["revenue"]) | set(series["net_income"]) | set(series["ocf"]))[-10:]
    overrides = load_overrides(ticker)
    # v5.2 override sanity bounds (round-2 audit: a capex override typed as 19
    # instead of 19,000,000 lifted a test company B -> A; a negative one made
    # Tier S). Negative values are impossible — refuse outright, here and in
    # make_score. A value outside 0.1x-10x of the last FILED value for that
    # field (or with no filed value at all) is out of band: flagged
    # OVERRIDE_OUT_OF_BAND below, and make_score refuses it unless
    # judgment.json carries an ack_reason acknowledging the out-of-band value.
    for field, o in overrides.items():
        if o["value"] < 0:
            print(f"dcf_engine.py: REFUSED — judgment.json {field}_override value {o['value']} is negative; "
                  "an override can never be negative (capex / SBC / share counts are >= 0). Fix judgment.json.", file=sys.stderr)
            sys.exit(1)
    ov_fx_fields = set()
    def _override_usd(field, p):
        """The judgment override for `field` expressed in USD for period p.
        v5.3.1 (Codex review of Stocks PR #1): override values are declared
        in the filer's reporting currency (they are read from the filing),
        but v5.3 inserted them verbatim into the USD-converted series —
        silently corrupting owner's earnings on every FX-converted name.
        Monetary overrides convert at the same period-end rate as the filed
        series; share counts are never converted. None when there is no
        override, or when that period's rate is unavailable (the fill does
        not happen and the gap stands)."""
        o = overrides.get(field)
        if o is None: return None
        if field == "shares" or not fx_info: return o["value"]
        r = (fx_info.get("rates_by_currency", {}).get(fx_info["from_currency"]) or {}).get(p)
        if r is None: return None
        ov_fx_fields.add(field)
        return o["value"] * r

    override_checks = {}
    for field, key in (("capex", "capex"), ("sbc", "sbc"), ("shares", "shares_diluted")):
        _lf = last_filed_raw.get(key)
        _o = overrides.get(field)
        if _o is None:
            continue
        if _lf is None:
            _oob = True
        elif _lf == 0:
            _oob = _o["value"] != 0
        else:
            _oob = not (0.1 <= abs(_o["value"] / _lf) <= 10)
        override_checks[field] = {"value": _o["value"], "last_filed_value": _lf,
                                  "last_filed_unit": last_filed_unit.get(key),
                                  "out_of_band": bool(_oob),
                                  "ack_reason_present": bool(_o.get("ack_reason"))}
    filled = {"capex": [], "sbc": [], "shares": []}        # period ends an override filled
    raw_missing = {"capex": set(), "sbc": set(), "shares": set(), "ocf": set()}  # periods with NO filed value
    basic_only = set()  # periods where only BASIC shares are filed (no diluted figure)
    share_fallback = {}  # v5.4: period -> (fallback count, source tag) when no diluted figure is filed
    debt_blank = []      # v5.4: periods with no debt tag at all (net debt unknown, not zero)
    cash_restricted_periods = []  # periods whose only cash tag includes restricted cash (Codex review of PR #2)
    hist, prev_nwc = [], None
    for p in periods:
        g = lambda k: series[k].get(p)
        capex_raw = g("capex")
        if capex_raw is None:
            raw_missing["capex"].add(p)
        capex_tag_p = series_tags["capex"].get(p)
        capex_ov = _override_usd("capex", p)
        if capex_raw is None and capex_ov is not None:
            capex = capex_ov; capex_tag_p = "OVERRIDE"
            capex_assumed_zero = False; filled["capex"].append(p)
        else:
            capex_assumed_zero = capex_raw is None and g("ocf") is not None
            capex = 0 if capex_assumed_zero else capex_raw
        sbc_raw = g("sbc")
        if sbc_raw is None:
            raw_missing["sbc"].add(p)
        sbc_tag_p = series_tags["sbc"].get(p)
        sbc_ov = _override_usd("sbc", p)
        if sbc_raw is None and sbc_ov is not None:
            sbc = sbc_ov; sbc_tag_p = "OVERRIDE"; filled["sbc"].append(p)
        else:
            sbc = sbc_raw
        sh_tag_p = series_tags["shares_diluted"].get(p)
        sh_merged = g("shares_diluted")
        # v5.2: BASIC shares are not a silent substitute for diluted (round-2:
        # the basic tag sat in the diluted candidate list and tiers shipped on
        # it unflagged). v5.4: that rule was dead code — a basic-only period
        # fell straight through to CommonStockSharesOutstanding / dei counts
        # and shipped unflagged. Now ANY non-diluted source is a shares gap
        # for the gated years; the fallback count is kept (and named in the
        # flag) so the worker can declare a filing override in one step, and
        # older periods use it for history with the source recorded.
        sh_diluted = sh_merged if sh_tag_p in DILUTED_SHARE_TAGS else None
        shares_src = None
        if sh_diluted is not None:
            shares_val, shares_src = sh_diluted, sh_tag_p
        else:
            raw_missing["shares"].add(p)
            fb = None
            if sh_merged is not None:
                basic_only.add(p); fb = (sh_merged, sh_tag_p)
            elif g("shares_out_inst") is not None:
                fb = (g("shares_out_inst"), series_tags["shares_out_inst"].get(p))
            else:
                dv, dd = dei_for_period(p)
                if dv is not None: fb = (dv, f"dei:EntityCommonStockSharesOutstanding@{dd}")
            if fb: share_fallback[p] = fb
            if "shares" in overrides:
                shares_val = overrides["shares"]["value"]; shares_src = "OVERRIDE"; filled["shares"].append(p)
            elif fb:
                shares_val, shares_src = fb[0], f"FALLBACK:{fb[1]}"
            else:
                shares_val = None
        if g("ocf") is None:
            raw_missing["ocf"].add(p)
        # v5.4 debt basis per period: noncurrent + current when a noncurrent
        # tag reports; else a TOTAL tag alone (never stacked on current); else
        # unknown — recorded, flagged, never read as zero debt.
        if g("debt_current") is not None:
            d_cur, d_cur_tag = g("debt_current"), series_tags["debt_current"].get(p)
        else:
            _parts = [(k, g(k)) for k in ("debt_cur_ltd", "debt_cur_st") if g(k) is not None]
            d_cur = sum(v for _, v in _parts) if _parts else None
            d_cur_tag = "+".join(str(series_tags[k].get(p)) for k, _ in _parts) if _parts else None
        d_lt, d_tot = g("debt_lt"), g("debt_total")
        if d_lt is not None:
            total_debt = d_lt + (d_cur or 0)
            debt_tag_p = f"{series_tags['debt_lt'].get(p)}+{d_cur_tag or 'none'}"
        elif d_tot is not None:
            _eff_unit = lambda k: "USD" if (k, p) in fx_converted_periods else series_units.get(k, {}).get(p)
            total_debt, debt_tag_p = debt_from_total_tag(d_tot, series_tags["debt_total"].get(p), g("debt_cur_st"), series_tags["debt_cur_st"].get(p),
                                                         same_unit=_eff_unit("debt_total") == _eff_unit("debt_cur_st"))
        elif d_cur is not None:
            total_debt = d_cur
            debt_tag_p = f"CURRENT_ONLY:{d_cur_tag}"
        else:
            total_debt, debt_tag_p = None, None
            debt_blank.append(p)
        # Codex review of PR #2: when the only cash tag is the combined
        # cash + restricted-cash total, subtract the restricted part if it is
        # tagged; otherwise the period is flagged and net debt is understated
        # in a known direction rather than silently.
        cash_avail, cash_tag_p = g("cash"), series_tags["cash"].get(p)
        if cash_avail is not None and cash_tag_p == "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents":
            if g("restricted_cash") is not None:
                cash_avail = cash_avail - g("restricted_cash"); cash_tag_p = f"{cash_tag_p} minus {series_tags['restricted_cash'].get(p)}"
            else:
                cash_restricted_periods.append(p)
        net_debt_p = (total_debt - (cash_avail or 0)) if total_debt is not None else None
        lease_liab = None
        if g("lease_liab_lt") is not None or g("lease_liab_current") is not None:
            lease_liab = (g("lease_liab_lt") or 0) + (g("lease_liab_current") or 0)
        rev, ni, ocf, da = g("revenue"), g("net_income"), g("ocf"), g("da")
        fcf = (ocf - capex) if (ocf is not None and capex is not None) else None
        oe_cons = (fcf - sbc) if (fcf is not None and sbc is not None) else fcf
        nwc = None
        if g("assets_current") is not None and g("liab_current") is not None:
            nwc = (g("assets_current") - (g("cash") or 0)) - (g("liab_current") - (g("debt_current") or 0))
        d_nwc = (nwc - prev_nwc) if (nwc is not None and prev_nwc is not None) else None
        if nwc is not None: prev_nwc = nwc
        oe_maint = None
        if ni is not None and da is not None and capex is not None:
            oe_maint = ni + da - min(capex, da) - (d_nwc or 0)
        hist.append({"period_end": p, "fy_label": p[:4], "revenue": rev, "net_income": ni,
                     "operating_income": g("operating_income"), "ocf": ocf,
                     "ocf_tag": series_tags["ocf"].get(p), "capex": capex,
                     "capex_assumed_zero": capex_assumed_zero,
                     "capex_tag": capex_tag_p, "sbc_tag": sbc_tag_p,
                     "da": da, "sbc": sbc, "fcf": fcf,
                     "oe_conservative": oe_cons, "oe_maintenance": oe_maint, "delta_nwc": d_nwc,
                     "shares_diluted": shares_val, "shares_tag": shares_src, "cash": cash_avail,
                     "cash_tag": cash_tag_p, "restricted_cash": g("restricted_cash"),
                     "debt_current": d_cur, "debt_lt": d_lt, "debt_total": total_debt, "debt_tag": debt_tag_p,
                     "net_debt": net_debt_p, "lease_liabilities": lease_liab,
                     "assets": g("assets"), "liabilities": g("liabilities"),
                     "ppe_net": g("ppe_net"), "equity": g("equity"), "tax": g("tax"),
                     "oe_per_share": (oe_cons / shares_val) if (oe_cons is not None and shares_val) else None,
                     "fcf_per_share": (fcf / shares_val) if (fcf is not None and shares_val) else None})

    if fx_info and ov_fx_fields:
        # v5.3.1: monetary override values were converted from the reporting
        # currency at period-end rates before being applied (see _override_usd).
        fx_info["overrides_converted"] = sorted(ov_fx_fields)
    overrides_applied = []
    for field in ("capex", "sbc", "shares"):
        if filled[field]:
            o = overrides[field]
            overrides_applied.append({"field": field, "value": o["value"], "kind": o["kind"],
                                      "source": o["source"], "reason": o["reason"],
                                      "periods_filled": filled[field],
                                      "out_of_band": override_checks.get(field, {}).get("out_of_band", False),
                                      "last_filed_value": override_checks.get(field, {}).get("last_filed_value")})
    if len(hist) < 2:
        # No usable history is a DATA failure, not a Tier F verdict. Exit distinctly so the
        # sweep marks blocked_no_data instead of publishing a fake F (the XOM trap).
        print(f"NO_DATA for {ticker}: only {len(hist)} usable fiscal years under CIK {cik} ({name}) — possible entity/CIK change (e.g. a 2026 holding-company reorganization). The analyzing agent should find the operating parent's CIK (web search the company + 'CIK 10-K') and rerun with --cik <CIK>; if none exists, mark blocked_no_data.")
        sys.exit(3)
    latest = hist[-1] if hist else {}
    shares = latest.get("shares_diluted")
    net_debt = latest.get("net_debt")  # v5.4: per-period basis (see debt_tag); None = unknown, never zero

    price = price_arg or nasdaq_price(ticker)
    if price_arg is not None: price_source = "manual"  # v5: a hand-passed price was labelled nasdaq_quote_api (audit)
    elif price: price_source = "nasdaq_quote_api"
    else: price_source = None
    if price is None and ticker in uni:
        try: price = float(uni[ticker]["price"]); price_source = "universe_screener"
        except Exception: price = None
    mktcap = market_cap_est(price, shares, ads_ratio,
                            float(uni[ticker]["market_cap"]) if ticker in uni and uni[ticker].get("market_cap") else None)

    def cagr(key, periods_n):
        vals = [(h["period_end"], h[key]) for h in hist if h.get(key)]
        if len(vals) < 2: return None
        (d0, v0), (d1, v1) = vals[-min(periods_n, len(vals))], vals[-1]
        yrs = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days / 365.25
        if v0 and v0 > 0 and v1 > 0 and yrs > 0.5: return (v1 / v0) ** (1 / yrs) - 1
        return None
    rev_cagr5, rev_cagr3 = cagr("revenue", 6), cagr("revenue", 4)
    oe_vals = [h["oe_conservative"] for h in hist if h.get("oe_conservative") is not None]

    # ---- v4: per-share OE history + NORMALIZED base (median of last 3 years) ----
    # v3 used the single latest fiscal year as the DCF base — the most fragile choice in the
    # model: one cyclical peak/trough, one-off, or SBC/WC spike year became the foundation.
    # (statistics is imported at module level — v5.4)
    oe_ps_hist = [(h["period_end"], h["oe_conservative"] / h["shares_diluted"])
                  for h in hist if h.get("oe_conservative") is not None and h.get("shares_diluted")]
    if ads_ratio:
        # Per-share figures become per-ADS (x ordinary shares per ADS) so they
        # are comparable to the ADS price. Ratio is a constant scale: growth
        # rates are unaffected. A TTM pin (--base-oe-ps / --ttm) is NOT scaled —
        # pins are taken as per-ADS already (see the ADS flag text).
        oe_ps_hist = [(d, v * ads_ratio["ratio"]) for d, v in oe_ps_hist]
    oe_ps_latest = oe_ps_hist[-1][1] if oe_ps_hist else None
    last3 = [v for _, v in oe_ps_hist[-3:]]
    oe_ps_norm = statistics.median(last3) if len(last3) >= 2 else oe_ps_latest
    # Base pin: --base-oe-ps wins for compatibility; --ttm reads the pin from
    # <TICKER>/ttm.json (ttm.py's saved output) so the base is never a free
    # number typed at a shell — make_score verifies it against ttm.json.
    pin_source = None
    payable_base = None
    if "--base-oe-ps" in sys.argv:
        base_override = float(sys.argv[sys.argv.index("--base-oe-ps") + 1]); pin_source = "base_oe_ps_arg"
    elif "--ttm" in sys.argv:
        try:
            with open(f"{BASE}/{ticker}/ttm.json", encoding="utf-8") as _f:
                base_override = float(json.load(_f)["ttm_oe_per_share"])
            pin_source = "ttm_json"
        except Exception as e:
            print(f"NO_TTM for {ticker}: --ttm given but {BASE}/{ticker}/ttm.json is missing or unreadable ({e}) — run ttm.py {ticker} first so the pin has provenance")
            sys.exit(3)
    elif "--base-judgment" in sys.argv:
        # Insurer payable-earnings base (2026-10-19): the pin is the declared
        # 5-yr average operating income to common / latest diluted shares, in
        # judgment.json, recomputed here and scaled by the ADS ratio. Refused
        # (exit 3) when the declaration is malformed, does not reproduce, the
        # share count is not this run's latest diluted count, or the filer's
        # series were FX-converted (the figures must already be USD).
        try:
            pb = load_payable_base(ticker)
            if not shares or abs(float(pb["shares"]) - float(shares)) >= 1.0:  # exact: the denominator IS the latest count
                raise ValueError(f"base_override.shares {pb['shares']:,.0f} is not this run's latest diluted count {shares if shares else 'n/a'}")
            sic, sic_desc = filer_sic(cik)
            if sic not in PAYABLE_SIC:
                raise ValueError(f"the payable-earnings rule is scoped to P&C insurers/reinsurers (SIC {sorted(PAYABLE_SIC)}); "
                                 f"EDGAR lists SIC {sic or 'unknown'} ({sic_desc or 'n/a'}) — keep the OCF base and the 2026-10-15 notch")
            if fx_info and fx_info.get("from_currency") and fx_info.get("from_currency") != "USD":
                raise ValueError("payable base is only defined for USD filers (series were FX-converted) — escalate NEEDS_MAIN_AGENT")
            base_override = payable_base_per_share(pb["figures"], pb["shares"], ads_ratio)
        except ValueError as e:
            print(f"BAD_BASE_OVERRIDE for {ticker}: --base-judgment given but {e}")
            sys.exit(3)
        pin_source = "judgment_base_override"
        payable_base = {"basis": PAYABLE_BASIS, "figures": [float(x) for x in pb["figures"]],
                        "average": sum(float(x) for x in pb["figures"]) / 5.0,
                        "shares": float(pb["shares"]), "per_ordinary_share": float(pb["value"]),
                        "ads_ratio": float(ads_ratio["ratio"]) if ads_ratio else 1.0,
                        "pinned_per_share": base_override, "sic": sic, "sic_description": sic_desc}
    else:
        base_override = None
    if base_override is not None:
        oe_ps, base_source = base_override, ("ttm_json" if pin_source == "ttm_json"
                                             else "judgment_base_override" if pin_source == "judgment_base_override"
                                             else "agent_supplied_ttm_override")
    elif oe_ps_norm is not None:
        oe_ps, base_source = oe_ps_norm, "median_of_last_3_fy_oe_per_share"
    else:
        oe_ps, base_source = None, "none"
    base_oe = latest.get("oe_conservative")

    # ---- v4: blended growth (median of independent signals) + share-count adjustment ----
    rev_yoy_latest = None
    revs = [(h["period_end"], h["revenue"]) for h in hist if h.get("revenue")]
    if len(revs) >= 2 and revs[-2][1]:
        rev_yoy_latest = revs[-1][1] / revs[-2][1] - 1
    oe_ps_cagr = None
    if len(oe_ps_hist) >= 3 and oe_ps_hist[-3][1] and oe_ps_hist[-3][1] > 0 and oe_ps_hist[-1][1] > 0:
        yrs = (datetime.date.fromisoformat(oe_ps_hist[-1][0]) - datetime.date.fromisoformat(oe_ps_hist[-3][0])).days / 365.25
        if yrs > 0.5: oe_ps_cagr = (oe_ps_hist[-1][1] / oe_ps_hist[-3][1]) ** (1 / yrs) - 1
    share_cagr = None
    sh = [(h["period_end"], h["shares_diluted"]) for h in hist if h.get("shares_diluted")]
    if len(sh) >= 2:
        (d0, s0), (d1, s1) = sh[-min(4, len(sh))], sh[-1]
        yrs = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days / 365.25
        if s0 and s0 > 0 and s1 > 0 and yrs > 0.5: share_cagr = (s1 / s0) ** (1 / yrs) - 1
    growth_components = {"rev_cagr_5y": rev_cagr5, "rev_cagr_3y": rev_cagr3,
                         "rev_yoy_latest": rev_yoy_latest, "oe_ps_cagr_2y": oe_ps_cagr}  # v5: was mislabelled oe_ps_cagr_3y — the span from t-3 to t-1 endpoints is 2 years
    share_adj = max(-0.05, min(0.05, -(share_cagr or 0.0)))  # buybacks lift OE/share growth; dilution drags it
    # v5.4: the share-count adjustment is applied to the REVENUE components
    # only. v4 added it to the median of all four signals, but the OE/share
    # CAGR already embeds the share-count trend — the audit's "double-counted
    # dilution" finding. The per-share CAGR enters the median unadjusted.
    growth_components_adjusted = {"rev_cagr_5y": None if rev_cagr5 is None else rev_cagr5 + share_adj,
                                  "rev_cagr_3y": None if rev_cagr3 is None else rev_cagr3 + share_adj,
                                  "rev_yoy_latest": None if rev_yoy_latest is None else rev_yoy_latest + share_adj,
                                  "oe_ps_cagr_2y": oe_ps_cagr}
    comp_vals = [v for v in growth_components_adjusted.values() if v is not None]
    g_blend = statistics.median(comp_vals) if comp_vals else 0.03

    result = {"ticker": ticker, "name": name, "cik": cik, "engine_version": 5, "engine_release": ENGINE_RELEASE,
              "as_of": ET_TODAY.isoformat(),
              "price": price, "price_source": price_source, "shares_diluted_latest": shares,
              "shares_outstanding_dei_latest": (latest_dei[1] if latest_dei else None),
              "shares_outstanding_dei_asof": (latest_dei[0] if latest_dei else None),
              "market_cap_est": mktcap, "net_debt_latest": net_debt, "net_debt_basis": latest.get("debt_tag"),
              "lease_liabilities_latest": latest.get("lease_liabilities"),
              "latest_period_end": latest.get("period_end"),
              "rev_cagr_5y": rev_cagr5, "rev_cagr_3y": rev_cagr3,
              "oe_positive_years_of_last_5": f"{sum(1 for v in oe_vals[-5:] if v>0)}/{len(oe_vals[-5:])}",
              "base_oe_total_latest_fy": base_oe, "base_oe_per_share": oe_ps,
              "base_oe_latest_per_share": oe_ps_latest, "base_oe_normalized_per_share": oe_ps_norm,
              "base_source": base_source, "growth_components": growth_components,
              "growth_components_adjusted": growth_components_adjusted,
              "g_blend": g_blend, "share_cagr": share_cagr, "share_count_adj": share_adj,
              "share_adj_basis": "applied to revenue components only (v5.4); OE/share CAGR enters unadjusted",
              "used_tags": used,
              "filer_annual_form": annual_form, "ads_ratio": ads_ratio, "fx_conversion": fx_info,
              "payable_base": payable_base,
              "override_checks": override_checks}

    # ---- v3 scenario / moat inputs ----
    def arglist(flag, default):
        if flag in sys.argv:
            return [float(x) for x in sys.argv[sys.argv.index(flag) + 1].split(",")]
        return default
    moat = float(sys.argv[sys.argv.index("--moat") + 1]) if "--moat" in sys.argv else 5.0
    moat = max(0.0, min(10.0, moat))
    cap_years = cap_years_for_moat(moat)
    probs = arglist("--probs", [0.10, 0.25, 0.30, 0.25, 0.10])
    offsets = arglist("--offsets", [-0.12, -0.05, 0.0, 0.05, 0.12])
    mults = arglist("--mults", [0.75, 0.90, 1.00, 1.10, 1.25])
    psum = sum(probs)
    probs = [p / psum for p in probs] if psum > 0 else [0.2] * 5

    gterm = float(sys.argv[sys.argv.index("--gterm") + 1]) if "--gterm" in sys.argv else DEFAULT_GTERM

    # ---- v5: fragility flags that do NOT depend on the scenario math are computed HERE,
    # before the Tier F branch — v4 computed flags only inside the positive-OE branch, so
    # every F name shipped with an empty flag list (audit finding). ----
    flags_pre, months_stale = [], None
    if latest.get("period_end"):
        months_stale = (ET_TODAY - datetime.date.fromisoformat(latest["period_end"])).days / 30.44
        if months_stale > 7: flags_pre.append(f"STALE_FY: latest fiscal year ended {months_stale:.0f} months ago — check TTM/quarterly OE and consider --base-oe-ps override")
    if share_cagr is not None and share_cagr > 0.03: flags_pre.append(f"DILUTION: share count growing {share_cagr*100:.1f}%/yr — already deducted via the growth adjustment; check SBC trend")
    if share_cagr is not None and share_cagr < -0.02: flags_pre.append(f"BUYBACK_TAILWIND: share count shrinking {-share_cagr*100:.1f}%/yr — already credited via the growth adjustment")
    rev_yoys = [revs[i][1] / revs[i - 1][1] - 1 for i in range(1, len(revs)) if revs[i - 1][1]][-5:]
    if any(abs(y) > 0.60 for y in rev_yoys): flags_pre.append("BASIS_BREAK_SUSPECT: a >60% revenue jump/drop in the last 5 yrs — check for divestitures, big M&A, or restatements before trusting any CAGR")
    pos_oe = [v for _, v in oe_ps_hist[-5:] if v > 0]
    if len(pos_oe) >= 3 and max(pos_oe) / min(pos_oe) > 3: flags_pre.append("OE_VOLATILE: OE/share range over the last 5 yrs spans >3x — normalized base helps but the business is cyclical; widen bear weight")
    ni_ocf_gap_years = [h["period_end"][:4] for h in hist[-3:]
                        if h.get("net_income") is not None and h.get("ocf") not in (None, 0)
                        and abs(h["net_income"] - h["ocf"]) / abs(h["ocf"]) > 0.40
                        and abs(h["net_income"] - h["ocf"]) > (h.get("da") or 0)]
    if ni_ocf_gap_years: flags_pre.append(f"NI_OCF_DIVERGENCE: net income and operating cash flow differ by >40% in {', '.join(ni_ocf_gap_years)} — find the one-off (tax deposits, impairments, WC swings) before trusting the OE base")
    if cik_fallback_note: flags_pre.append(cik_fallback_note)
    if fx_info:
        flags_pre.append(f"FX_CONVERTED: reporting currency {fx_info['from_currency']} converted to USD at period-end ECB reference rates (frankfurter.app) — flow facts use the period-end rate, not a period average; the rates used are recorded in dcf_numbers.json fx_conversion")
    if usd_translation_used:
        flags_pre.append("USD_TRANSLATIONS_USED: the issuer files its own USD convenience translations alongside its reporting currency; the engine used the filed USD figures")
    if annual_form in ("20-F", "40-F"):
        if ads_ratio:
            flags_pre.append(f"ADS_RATIO_APPLIED: {annual_form} filer — per-share figures scaled x{ads_ratio['ratio']} ordinary shares per ADS "
                             f"({ads_ratio['source']}) so they are comparable to the ADS price; TTM pins are taken as per-ADS already")
        else:
            flags_pre.append(f"ADS_RATIO_MISSING: {annual_form} filer — per-share figures are per ordinary share but the traded price is per ADS; "
                             "make_score refuses (DATA_GAP:ads_ratio) until judgment.json carries an ads_ratio {ratio, source, reason}")
    for field, chk in override_checks.items():
        if chk["out_of_band"] and not chk["ack_reason_present"]:
            lf = chk["last_filed_value"]
            lf_s = f"${lf:,.0f}" if isinstance(lf, (int, float)) else "no filed value at all"
            flags_pre.append(f"OVERRIDE_OUT_OF_BAND:{field} — override value {chk['value']:,.0f} is outside 0.1x-10x of the last filed value "
                             f"({lf_s}) and judgment.json carries no ack_reason — make_score will refuse until the out-of-band value is explicitly acknowledged")
    if len(hist) < 4: flags_pre.append(f"THIN_HISTORY: only {len(hist)} fiscal years of data")
    _fb_hist = sorted(p[:4] for p in share_fallback if p not in [h["period_end"] for h in hist[-3:]] and p in [h["period_end"] for h in hist])
    if _fb_hist:
        flags_pre.append(f"SHARES_FALLBACK: no diluted share count filed for {', '.join(_fb_hist)} — those history years use the basic / outstanding / dei count recorded in the shares_tag column; per-share history there is approximate")
    if debt_blank and latest.get("period_end") in debt_blank:
        flags_pre.append("DEBT_TAGS_BLANK: no debt tag reports for the latest fiscal year — net debt is UNKNOWN (not zero); no leverage verdict is possible from the engine, state the balance sheet from the filing in analysis.md")
    if cash_restricted_periods and latest.get("period_end") in cash_restricted_periods:
        flags_pre.append("CASH_INCLUDES_RESTRICTED: the only cash tag filed for the latest fiscal year is the combined cash + restricted-cash total and no restricted-cash tag separates it — net debt is UNDERSTATED by the restricted amount (escrow / collateral / regulatory); check the balance sheet before trusting HIGH_NET_DEBT's absence")
    sector_u = (uni.get(ticker) or {}).get("sector", "")
    if sector_u in ("Finance", "Real Estate", "Utilities"):  # v5: was Finance only — IRM (REIT) and ED/PCG/PEG (utilities) slipped through unflagged
        flags_pre.append(f"SECTOR_MODEL_MISMATCH: {sector_u} sector — OE/capex DCF fits {sector_u.lower()} names poorly; grade confidence low")

    # ---- v5 DATA GATE: missing data must never silently become zero again. ----
    # Gaps are judged on the FILED values (raw_missing), before any override fill.
    last3_periods = [h["period_end"] for h in hist[-3:]]
    # v5.3: the currency gap is judged on the periods actually used. Not a gap:
    # facts filed in USD (including the issuer's own USD convenience
    # translations) or FX-converted above. Still a gap: mixed reporting
    # currencies in the last 3 FY, or a last-3-FY core fact whose period-end
    # rate was unavailable and so stayed unconverted.
    # v5.3.1: a last-3-FY core period is a currency gap iff it was filed in a
    # non-USD unit and the FX pass did not convert it (mixed filer, or no ECB
    # rate for its currency) — one rule for every filer shape.
    currency_gap = any(series_units.get(k, {}).get(p) not in (None, "USD", "shares", "USD/shares")
                       and (k, p) not in fx_converted_periods
                       for k in ("revenue", "net_income", "ocf") for p in last3_periods)
    gap_fields, gap_years = [], {}
    for field in ("sbc", "capex", "shares", "ocf"):
        missing = [p[:4] for p in last3_periods if p in raw_missing[field]]
        if missing: gap_fields.append(field); gap_years[field] = missing
    if currency_gap: gap_fields.append("currency")
    if price is None: gap_fields.append("price")
    # A gap is covered only if a judgment override actually filled that field.
    covered = [f for f in gap_fields if f in ("capex", "sbc", "shares") and filled[f]]
    uncovered = [f for f in gap_fields if f not in covered]
    for f in covered:
        flags_pre.append(f"OVERRIDE_APPLIED:{f} — filing gap in the last 3 FY filled by a judgment override "
                         f"({overrides[f]['kind']}: {overrides[f]['source']}); an override never replaces a filed "
                         f"value — see overrides_applied and override_impact")
    if uncovered and not MEASURE:
        gap_flags = []
        for f in uncovered:
            if f == "currency": gap_flags.append("DATA_GAP:currency — last-3-FY core facts are filed in a non-USD currency that could not be converted to USD (mixed reporting currencies, or no ECB reference rate for the currency) — no tier emitted")
            elif f == "price": gap_flags.append("DATA_GAP:price — no price available from Nasdaq, --price, or the universe file — no tier emitted")
            elif f == "shares" and any(p in share_fallback for p in last3_periods if p[:4] in gap_years[f]):
                _fbs = "; ".join(f"{p[:4]}: {share_fallback[p][0]:,.0f} ({share_fallback[p][1]})" for p in last3_periods if p in share_fallback)
                gap_flags.append(f"DATA_GAP:shares — DILUTED shares missing for fiscal year(s) {', '.join(gap_years[f])} of the last 3; only a non-diluted count is filed ({_fbs}) — no silent swap (v5.4). Declare shares_override kind \"filing\" from the 10-K EPS note — no tier emitted")
            else: gap_flags.append(f"DATA_GAP:{f} — {f} missing for fiscal year(s) {', '.join(gap_years[f])} of the last 3 — no tier emitted")
        result.update({"tier_by_numbers": None, "implied_irr_weighted": None, "implied_irr_base": None,
                       "moat_score": moat, "cap_years": round(cap_years, 1), "g_terminal": gterm,
                       "data_gap": gap_fields, "data_gap_uncovered": uncovered,
                       "overrides_applied": overrides_applied,
                       "fragility_flags": gap_flags + flags_pre,
                       "note": "DATA_GAP: required filing data is missing (see data_gap / data_gap_uncovered). v5 never emits a tier on an uncovered data gap — a missing value is not a zero."})
        result["content_hash"] = _content_hash(result)
        folder = f"{BASE}/{ticker}"; os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/financials_history.csv", "w", newline="", encoding="utf-8") as f:
            if hist:
                w = csv.DictWriter(f, fieldnames=list(hist[0].keys())); w.writeheader(); w.writerows(hist)
        json.dump(result, open(f"{folder}/dcf_numbers.json", "w", encoding="utf-8"), indent=1)
        print(f"DATA_GAP for {ticker}: {', '.join(uncovered)} — no tier emitted (dcf_numbers.json written with data_gap + flags)")
        print(json.dumps(result, indent=1))
        sys.exit(3 if uncovered == ["price"] else 4)  # price-only failure exits like NO_DATA, never Tier F

    # v5.4: the valuation math lives in module-level functions (project_path /
    # present_value / solve_irr / tier_for_irr) shared with the HTML builder
    # and the test-suite. The fade: growth HOLDS at g0 for 2 years (near-term
    # prints have visibility; v3 faded from year 1), then converges LINEARLY
    # to the terminal rate over cap_years — in EITHER direction.
    labels = ["super_bear", "bear", "base", "bull", "super_bull"]
    if oe_ps and oe_ps > 0 and price:
        # Blended growth (median of share-adjusted rev CAGRs / latest YoY and the raw OE/ps CAGR),
        # capped [-5%, 35%] (cap history: 20% until 2026-10-12 — see README Fixes & lessons).
        g_base = max(GROWTH_FLOOR_BASE, min(GROWTH_CAP_BASE, g_blend))
        scenarios, all_flows, capped_labels, floor_labels = {}, [], [], []
        paths, gpaths = {}, {}
        for i, label in enumerate(labels):
            g0 = max(GROWTH_FLOOR_START, min(GROWTH_CAP_START, g_base + offsets[i]))
            flows = project_path(oe_ps * mults[i], g0, cap_years, gterm)
            all_flows.append(flows)
            paths[label] = [round(f, 6) for f in flows]
            gpaths[label] = [round(g, 6) for g in growth_path(g0, cap_years, gterm)]
            _irr, _capped, _floor = solve_irr(flows, price, gterm)
            if _capped: capped_labels.append(label)
            if _floor: floor_labels.append(label)
            scenarios[label] = {"prob": round(probs[i], 4), "g_start": round(g0, 4), "oe_mult": mults[i],
                                "iv_at_10": present_value(flows, 0.10, gterm), "iv_at_12": present_value(flows, 0.12, gterm),
                                "iv_at_15": present_value(flows, 0.15, gterm), "iv_at_20": present_value(flows, 0.20, gterm),
                                "iv_at_25": present_value(flows, 0.25, gterm), "irr": _irr, "irr_at_floor": _floor}
        wflows = [sum(probs[i] * all_flows[i][t] for i in range(5)) for t in range(PROJECTION_YEARS)]
        paths["weighted"] = [round(f, 6) for f in wflows]
        _wirr, _wcapped, _wfloor = solve_irr(wflows, price, gterm)
        if _wcapped: capped_labels.append("weighted")
        if _wfloor: floor_labels.append("weighted")
        weighted = {"iv_at_10": present_value(wflows, 0.10, gterm), "iv_at_12": present_value(wflows, 0.12, gterm),
                    "iv_at_15": present_value(wflows, 0.15, gterm), "iv_at_20": present_value(wflows, 0.20, gterm),
                    "iv_at_25": present_value(wflows, 0.25, gterm), "irr": _wirr, "irr_at_floor": _wfloor}
        irr = weighted["irr"]
        tier = tier_for_irr(irr)
        irr_bear, irr_bull = scenarios["bear"]["irr"], scenarios["bull"]["irr"]

        # ---- diagnostics & scenario-dependent fragility flags (flags_pre, computed before
        # this branch, carries the rest — the agent MUST address every flag in analysis.md) ----
        flags = list(flags_pre)
        if capped_labels:
            flags.append(f"IRR_CAPPED: implied IRR exceeds the 200% solver cap at the current price ({', '.join(capped_labels)}) — recorded as 2.0 (capped); the stock is cheaper than the solver's range, not a D")
        if floor_labels:
            flags.append(f"IRR_AT_FLOOR: implied IRR sits within 0.5pp of terminal growth {gterm*100:.1f}% ({', '.join(floor_labels)}) — a perpetuity growing at g has an IRR above g at any price, so the model cannot express a return below ~{gterm*100:.1f}%; this price is beyond the model's range and the expected return is 'at most ~{(gterm+0.005)*100:.1f}%', not the recorded figure")
        if oe_ps_latest and oe_ps_norm and oe_ps_norm > 0 and abs(oe_ps_latest / oe_ps_norm - 1) > 0.35:
            flags.append(f"BASE_DIVERGENCE: latest FY OE/share {oe_ps_latest:.2f} vs 3-yr median {oe_ps_norm:.2f} — one of them is distorted; find out which and why")
        oe_yield = oe_ps / price
        if oe_yield < 0.02: flags.append(f"LOW_OE_YIELD: base OE yield {oe_yield*100:.1f}% — valuation rests almost entirely on growth; tier is fragile")
        tvs = terminal_share(wflows, 0.15, gterm)
        if tvs and tvs > 0.70: flags.append(f"HIGH_TV_SHARE: terminal value is {tvs*100:.0f}% of IV@15% — result is mostly a terminal assumption")
        ivsb, ivsbu = scenarios["super_bear"]["iv_at_15"], scenarios["super_bull"]["iv_at_15"]
        spread = (ivsbu / ivsb) if ivsb and ivsb > 0 else None
        if spread and spread > 4: flags.append(f"WIDE_SCENARIO_SPREAD: super-bull IV is {spread:.1f}x super-bear IV — uncertainty is huge; confidence should not be high")
        base_oe_total_norm = oe_ps * shares if shares else None
        nd_ratio = (net_debt / base_oe_total_norm) if (net_debt is not None and base_oe_total_norm) else None
        if nd_ratio is not None and nd_ratio > 3: flags.append(f"HIGH_NET_DEBT: net debt is {nd_ratio:.1f}x normalized OE — levered OE can vanish fast; stress the bear cases")
        if nd_ratio is not None and nd_ratio < -2: flags.append(f"BIG_NET_CASH: net cash is {-nd_ratio:.1f}x normalized OE — part of the price is a cash pile, not the operating business; note it in the verdict")
        tier_bear, tier_bull = tier_for_irr(irr_bear), tier_for_irr(irr_bull)
        if tier_bear != tier_bull:
            flags.append(f"TIER_BAND: bear-case tier {tier_bear} ({irr_bear*100:.1f}%) vs bull-case tier {tier_bull} ({irr_bull*100:.1f}%) — the verdict spans tiers; size any position to the bear end")
        result.update({"g_base": g_base, "moat_score": moat, "cap_years": round(cap_years, 1), "g_terminal": gterm,
                       "inputs": {"moat": moat, "probs": probs, "offsets": offsets, "mults": mults,
                                  "g_terminal": gterm, "base_oe_ps_arg": base_override, "base_pin_source": pin_source},
                       "data_gap": gap_fields, "data_gap_uncovered": uncovered,
                       "overrides_applied": overrides_applied,
                       "scenarios": scenarios, "weighted": weighted,
                       "paths": paths, "growth_paths": gpaths,
                       "implied_irr_weighted": irr, "implied_irr_base": scenarios["base"]["irr"],
                       "irr_bear": irr_bear, "irr_bull": irr_bull,
                       "irr_low": min(s["irr"] for s in scenarios.values()), "irr_high": max(s["irr"] for s in scenarios.values()),
                       "tier_by_numbers": tier, "tier_bear": tier_bear, "tier_bull": tier_bull,
                       "hurdle_prices": {"15": weighted["iv_at_15"], "20": weighted["iv_at_20"], "25": weighted["iv_at_25"]},
                       "upside_at_15": weighted["iv_at_15"] / price - 1, "upside_at_12": weighted["iv_at_12"] / price - 1,
                       "iv_at_15": weighted["iv_at_15"], "iv_at_12": weighted["iv_at_12"],
                       "iv_at_20": weighted["iv_at_20"], "iv_at_25": weighted["iv_at_25"],
                       "diagnostics": {"oe_yield": oe_yield, "tv_share_at_15": tvs, "scenario_spread_iv15": spread,
                                       "net_debt_to_normalized_oe": nd_ratio, "months_since_fy_end": months_stale,
                                       "irr_capped": bool(capped_labels), "irr_at_floor": bool(_wfloor)},
                       "fragility_flags": flags})
    else:
        # v5.4: Tier F is split — "SBC exceeds cash generation" and "no cash
        # generation" are different stories (audit round-1, Model design).
        # Codex review of PR #2: classify on the SAME basis that produced the
        # non-positive base — the ttm.json legs for a TTM pin, else the last
        # three fiscal years (the median window) summed — and actually test
        # SBC against FCF, never the latest year alone.
        f_fcf = f_sbc = None
        f_basis = None
        if pin_source == "ttm_json":
            try:
                with open(f"{BASE}/{ticker}/ttm.json", encoding="utf-8") as _f:
                    _t = json.load(_f)
                f_fcf = float(_t["ttm_ocf"]) - float(_t["ttm_capex"]); f_sbc = float(_t["ttm_sbc"]); f_basis = "ttm.json legs (TTM pin)"
            except Exception:
                f_fcf = f_sbc = None
        if pin_source == "judgment_base_override" and payable_base:
            # The non-positive base is the five-year payable average: classify
            # on that, not on OCF/capex/SBC, which may well be positive here.
            f_basis = "five-year average of operating income available to common (payable pin)"
            f_fcf, f_sbc = None, None
        elif f_fcf is None:
            _w = [h for h in hist[-3:] if h.get("fcf") is not None]
            if _w:
                f_fcf = sum(h["fcf"] for h in _w); f_sbc = sum((h.get("sbc") or 0) for h in _w)
                f_basis = f"sum of the last {len(_w)} fiscal years (the median window)"
        if oe_ps is None:
            f_subtype = "no_base"
        elif pin_source == "judgment_base_override" and payable_base:
            f_subtype = "payable_earnings_nonpositive"
        elif f_fcf is None:
            f_subtype = "indeterminate"
        elif f_fcf <= 0:
            f_subtype = "no_cash_generation"
        elif f_sbc is not None and f_sbc >= f_fcf:
            f_subtype = "sbc_exceeds_cash"
        else:
            f_subtype = "indeterminate"  # FCF > SBC on this basis yet the base is non-positive (an agent-supplied pin without legs)
        result.update({"tier_by_numbers": "F", "f_subtype": f_subtype, "f_subtype_basis": f_basis,
                       "implied_irr_weighted": None, "implied_irr_base": None, "moat_score": moat,
                       "cap_years": round(cap_years, 1), "g_terminal": gterm,
                       "inputs": {"moat": moat, "probs": probs, "offsets": offsets, "mults": mults,
                                  "g_terminal": gterm, "base_oe_ps_arg": base_override, "base_pin_source": pin_source},
                       "data_gap": gap_fields, "data_gap_uncovered": uncovered,
                       "overrides_applied": overrides_applied,
                       "fragility_flags": flags_pre,  # v5: F names carry their flags too
                       "note": "No positive NORMALIZED (3-yr median) conservative owner's earnings — OE DCF not supportable on numbers alone. If the latest year alone is positive, that is a flag to investigate, not a pass."
                               + (f" F sub-type: payable earnings non-positive (five-year average operating income available to common {payable_base['average']:,.0f} on the --base-judgment pin; OCF-based OE is not the basis here)." if f_subtype == "payable_earnings_nonpositive"
                                  else " F sub-type: SBC exceeds cash generation (OCF - capex is positive; SBC consumes it)." if f_subtype == "sbc_exceeds_cash"
                                  else " F sub-type: no cash generation (OCF - capex is not positive)." if f_subtype == "no_cash_generation" else "")})

    if overrides_applied and not MEASURE:
        result["override_impact"] = _override_impact(ticker, price,
                                                     result.get("base_oe_per_share"),
                                                     result.get("implied_irr_weighted"))
    result["content_hash"] = _content_hash(result)
    folder = f"{BASE}/{ticker}"; os.makedirs(folder, exist_ok=True)
    if not MEASURE:
        with open(f"{folder}/financials_history.csv", "w", newline="", encoding="utf-8") as f:
            if hist:
                w = csv.DictWriter(f, fieldnames=list(hist[0].keys())); w.writeheader(); w.writerows(hist)
        json.dump(result, open(f"{folder}/dcf_numbers.json", "w", encoding="utf-8"), indent=1)
    print(json.dumps(result, indent=1))

if __name__ == "__main__":
    main()
