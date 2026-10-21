#!/usr/bin/env python3
"""Moat evidence: operating-basis ROIC and the measured moat anchor (moat rubric 2, 2026-10-21).

Usage: python3 moat_evidence.py <TICKER> [--moat M] [--json]

Pure functions over one company's fundamentals.json — no network, no writes.
fundamentals.py and statements.py take their displayed ROIC from roic_row();
make_score.py records evidence() + assess() in score.json `moat_evidence` and
prints key_numbers_lines() under key_numbers.md "## Growth & moat"; WORKER_SPEC
step 5 runs this file's CLI, which prints the same lines, before the moat is set.

Why (Andrew's request in the "Tighten moat scoring" thread, 2026-10-20): moats
across the 521 scored folders sat 82% at 4-6 (mean 5.17, sd 1.13; the engine
default is 5) and tracked measured returns only at Spearman 0.30, partly
because the old `roic_proxy` = NOPAT / (equity + debt − cash) was wrong exactly
where moats are widest: buyback-driven negative equity turned VRSN's 70%-margin
business into −46%, cash ≈ equity swung MANH between +9315% and −1540%, a
loss over negative capital read positive (IBRX +43%), unfiled operating
income left MTD and ZTS with no ROIC at all, and an unread debt tag tripled
DKS. Pat Dorsey's order — a history of returns above the cost of capital,
then a structural source, then durability — is the method; Morningstar's
wide / narrow lines (excess returns for 20 / 10 years) set the knots.

ROIC (one formula; every caller imports roic_row):
  t      = tax / pretax when pretax > 0 and 0 <= tax/pretax <= 0.5, else 0.21
  NOPAT  = operating_income × (1 − t). Operating income unfiled AND the SIC known
           and not financial: (pretax + |interest|) × (1 − t); pretax × (1 − t)
           when interest is unfiled; net income + |interest| × (1 − t) when pretax
           is unfiled. A blank or financial SIC gets no fallback (NLY would add
           back $4.8B of repo interest; ARCC files no SIC). Financial = SIC
           6000-6799 less the real-estate operators 6500-6599 outside the
           6510-6519 lessors (CBRE, JLL are services firms, measured on ROIC).
  IC     = operating basis: assets − cash − short-term investments − (current
           liabilities − current debt, never below 0); current debt =
           debt_current, else max(0, total_debt − debt_lt), else 0. Goodwill
           and acquired intangibles stay IN: owner's earnings never deduct acquisitions, so
           the goodwill-inclusive return is the return on the growth the CAP
           credits. Current liabilities unfiled (an unclassified balance sheet):
           financing basis equity + total_debt − cash when total_debt is filed
           and covers the balance sheet (liabilities − total_debt <= 50% of
           assets), else assets basis assets − cash − STI (ROIC a lower bound).
           Same-period rule: cash or current liabilities filed in another
           period but missing in this one → no figure; a missing short-term
           investment cell counts as 0 (most filers file it in some years only).
  shown  `roic_proxy` = NOPAT / IC only when IC >= 10% of revenue (IC > 0 when
           revenue is unknown); otherwise null and `roic_class` says why
           (`capital_light`, `customer_funded`, `loss`; `financial` at a
           financial SIC, where ROIC is not the measure). `roic_basis` names the IC
           basis; `roic_tangible` = NOPAT / (IC − goodwill − intangibles), context.
  evidence = NOPAT / max(IC, 10% × revenue), clipped to ±100%: equal to the shown
           figure wherever one is shown; capital <= 0 never flips a profit's sign
           (VRSN > +100%, customer-funded), a loss stays negative, and a thin
           margin on negative capital stays thin (NTNX FY2024 2.8%, not +100%).

Anchor (0-9; a 10 is never mechanical). Paths: `roic` (hurdle 10%; real-estate
operators included); `roe_fin` for the other financial SICs — banks 6020-6099
on tangible equity — mortgage REITs and a blank SIC with no operating income
(ROE on average equity, hurdle 12%); `roe_util` for regulated utilities (ROE,
hurdle 9%, anchor <= 6); `reit_prior` for equity REITs and lessors (SIC 6798 /
6510-6519 with operating income filed, or D&A >= 10% of revenue — 2% of assets
when revenue is unread: AMH): fixed 4, book returns not scored. Level = the
5-year median interpolated on the path's knots (roic: −20%→0, 0→2, 5%→3, 8%→4,
11%→5, 15%→6, 20%→7, 30%→8; the 11% and 20% knots are where, out of sample, an
earlier median went on to clear 10% in half / 85% of later years). Terms only
at a median at or above the hurdle: persistence −0.5 below 80% of the last 10
years at the hurdle (Dorsey's four years in five), −1 below 60%; trough −0.5
for any year below 0 — and level + these never below the level at the hurdle
itself (`hurdle_floor`: a median just under the hurdle takes no terms, so a
better record never scores lower). At any median: record +1 (roic, the only
route to 9) for >= 8 usable years all at 15%+, a median >= 20% and a 5-year
EBIT margin >= 10%; leverage −1 (roe_fin) above 1.5× the sector's
assets/equity norm. Caps: EBIT margin < 10% → 7 (turnover or supplier
float: HPQ, EME); 3+ of 5 years off the operating basis
→ 7 (NVR); financial net margin < 5% → 4 (float ROE: MOH); financial median
ROE > 40% → 6 with `data_check` (IBKR's NCI-inclusive income); fewer than 5
usable years → 6. Fewer than 3 usable years in the last 5: no anchor, band 0-5.

Judgment (assess): band = anchor_r ± 2 (audit-round-1's "let judgment adjust by
±2"), 9-10 only on anchor_r >= 8. `moat_sources` names Dorsey's five sources;
an explicitly empty list caps the band at 4. Outside the band a
`moat_evidence_reason` {code, text, ...} from REASONS widens it; the four
mechanical codes are tested here (BUSINESS_CHANGED by the main rules on the
years since a change inside the 5-year window), the text-only ones are accepted
but never reopen the entry alert; no reach passes 8 below anchor 8. An
unexplained moat above the band closes the entry alert gate in make_score
(MOAT_ABOVE_EVIDENCE); a moat below it is recorded
(MOAT_BELOW_EVIDENCE) and touches no gate. Nothing here refuses except a
malformed reason or source, or a moat that is not a finite number (ValueError).
A non-USD fundamentals.json whose dividends block records no currency (the
marker of a file written before the one-money-unit rule, 2026-10-19, whatever
its as_of) is not measured.
"""
import argparse
import json
import math
import os
import statistics
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)

RUBRIC = 2                  # the moat rubric this module implements (WORKER_SPEC step 5)
VERSION = 1                 # score.json moat_evidence block version
CLIP = 1.0                  # evidence ratios clipped to ±100%
FLOOR_REV = 0.10            # capital floor for the evidence ratio: turnover capped at 10×
PARTIAL_DEBT = 0.50         # unclassified balance sheet: liabilities − total_debt > 50% of assets → assets basis
WINDOW, HIST = 5, 10        # level window / persistence window (fiscal years)
MIN_USABLE = 3              # usable years in the last 5 for an anchor
PROVEN_YEARS = 5            # Dorsey: five years is the minimum → fewer usable years caps the anchor at 6
BAND = 2
NO_ANCHOR_BAND = (0, 5)     # unproven returns: weak-to-narrow at most
WIDE_MIN_ANCHOR = 8         # 9-10 needs anchor_r >= 8; no reason lifts a moat past 8 otherwise
NO_SOURCE_CAP = 4           # an explicitly empty moat_sources: weak at most
UTIL_SIC = (4911, 4922, 4923, 4924, 4931, 4932, 4939, 4941)
BANK_SIC = (6020, 6099)     # return on TANGIBLE equity (Morningstar's bank test)
# path → hurdle, cap, knots (5y median → level; linear between knots, flat outside)
PATHS = {
    "roic": {"hurdle": 0.10, "cap": 9.0,
             "knots": ((-0.20, 0), (0.0, 2), (0.05, 3), (0.08, 4), (0.11, 5), (0.15, 6), (0.20, 7), (0.30, 8))},
    "roe_fin": {"hurdle": 0.12, "cap": 8.0,
                "knots": ((-0.20, 0), (0.0, 2), (0.06, 3), (0.09, 4), (0.12, 5), (0.15, 6), (0.20, 7), (0.25, 8))},
    "roe_util": {"hurdle": 0.09, "cap": 6.0,
                 "knots": ((-0.20, 0), (0.0, 2), (0.06, 3), (0.08, 4), (0.10, 5), (0.12, 6))},
}
REIT_PRIOR = 4
REIT_DA = (0.10, 0.02)          # SIC 6798 / 6510-6519: D&A >= 10% of revenue (or 2% of assets, revenue unread) → equity REIT
LOW_MARGIN = (0.10, 7.0)        # roic path: 5y median EBIT margin < 10% → anchor <= 7
NON_OP_CAP = 7.0                # roic path: >= 3 of 5 usable years on the financing / assets basis → anchor <= 7
THIN_NET_MARGIN = (0.05, 4.0)   # roe_fin: 5y median net margin < 5% → anchor <= 4
DATA_CHECK_ROE = (0.40, 6.0)    # roe_fin: 5y median ROE > 40% → anchor <= 6, a probable data defect
SHORT_CAP = 6.0
RECORD = {"years": 8, "floor": 0.15, "median": 0.20}
# assets / equity norms for the roe_fin leverage term (5y median above 1.5× the norm → −1)
LEV_NORMS = (((6000, 6199), 12.0), ((6200, 6299), 6.0), ((6311, 6311), 12.0), ((6300, 6499), 4.5),
             ((6798, 6798), 8.0), ((6500, 6799), 4.0))
SERIAL_ACQUIRER = 0.25          # acquisitions (or goodwill + intangibles growth) >= 25% of 5y OCF

SOURCES = ("intangible_assets", "switching_costs", "network_effect", "cost_advantage", "efficient_scale")
# code → (direction it explains, tested here?)
REASONS = {
    "ACQUIRED_GOODWILL": ("up", True),
    "EXPENSED_INVESTMENT": ("up", True),
    "BUSINESS_CHANGED": ("both", True),
    "CYCLE_ADJUSTED": ("both", True),
    "SHORT_HISTORY": ("up", False),
    "MEASUREMENT_DEFECT": ("both", False),
    "NO_DURABLE_SOURCE": ("down", False),
}
DEFECT_FIELDS = ("operating_income", "pretax_income", "tax", "interest_expense", "net_income", "revenue",
                 "assets", "liab_current", "cash", "short_term_investments", "debt_current", "debt_lt",
                 "total_debt", "equity", "goodwill", "intangibles")
MIN_TEXT = 40
ROIC_KEYS = ("roic_proxy", "roic_class", "roic_basis", "roic_tangible")
GAP_KEYS = ("cash", "liab_current")   # filed in other periods but missing in this one → no figure (same-period rule)


# ------------------------------------------------------------------ helpers
def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _z(x):
    return x if num(x) else 0.0


def sic_int(fu_or_sic):
    """The SIC as an int from a fundamentals.json dict (profile.sic) or a raw value; None when blank."""
    s = ((fu_or_sic.get("profile") or {}).get("sic")) if isinstance(fu_or_sic, dict) else fu_or_sic
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


def is_financial(sic):
    """SIC 6000-6799, less the real-estate operators 6500-6599 outside the 6510-6519 lessors (CBRE, JLL: services
    firms, measured on ROIC like any operating business)."""
    if sic is None or not 6000 <= sic <= 6799:
        return False
    return not (6500 <= sic <= 6599 and not 6510 <= sic <= 6519)


def _clip(v):
    return None if v is None else max(-CLIP, min(CLIP, v))


def _median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def _adjacent(prev, cur):
    """True when prev's fiscal year ends 300-430 days before cur's (one fiscal year earlier)."""
    try:
        d = (date.fromisoformat(str(cur["period_end"])) - date.fromisoformat(str(prev["period_end"]))).days
    except (KeyError, TypeError, ValueError):
        return False
    return 300 <= d <= 430


# ------------------------------------------------------------------ ROIC
def tax_rate(r):
    pt, tx = r.get("pretax_income"), r.get("tax")
    if num(pt) and pt > 0 and num(tx) and 0 <= tx / pt <= 0.5:
        return tx / pt
    return 0.21


def nopat(r, sic, t=None):
    """(NOPAT, basis) for one row; basis 'oi' | 'pretax+interest' | 'pretax' | 'ni+interest'; (None, None)
    when no figure exists. t overrides the row's tax rate (statements.py's trailing-four-quarter rate)."""
    t = tax_rate(r) if t is None else t
    oi = r.get("operating_income")
    if num(oi):
        return oi * (1 - t), "oi"
    if sic is None or is_financial(sic):
        return None, None
    pt, ie, ni = r.get("pretax_income"), r.get("interest_expense"), r.get("net_income")
    if num(pt):
        return ((pt + abs(ie)) * (1 - t), "pretax+interest") if num(ie) else (pt * (1 - t), "pretax")
    if num(ni):
        return ni + (abs(ie) * (1 - t) if num(ie) else 0.0), "ni+interest"
    return None, None


def current_debt(r):
    dc, td, dl = r.get("debt_current"), r.get("total_debt"), r.get("debt_lt")
    if num(dc):
        return dc
    if num(td) and num(dl):
        return max(0.0, td - dl)
    return 0.0


def invested_capital(r):
    """(IC, basis) for one row: basis 'operating' | 'financing' | 'assets'; (None, None) with no assets or equity."""
    a, lc = r.get("assets"), r.get("liab_current")
    cash, sti = _z(r.get("cash")), _z(r.get("short_term_investments"))
    if num(a) and num(lc):
        # current debt above current liabilities is an inconsistent row (a stale mixed-currency file): no add-back
        return a - cash - sti - max(0.0, lc - current_debt(r)), "operating"
    eq, td, li = r.get("equity"), r.get("total_debt"), r.get("liabilities")
    partial = num(td) and num(li) and num(a) and a > 0 and (li - td) > PARTIAL_DEBT * a
    if num(eq) and num(td) and not partial:
        return eq + td - cash, "financing"
    if num(a):
        return a - cash - sti, "assets"
    return None, None


def filed_keys(rows):
    """The GAP_KEYS filed in any of `rows` (the same-period rule's 'filed in other periods')."""
    return {k for k in GAP_KEYS if any(num(x.get(k)) for x in rows or [])}


def gap(r, filed):
    """True when a GAP_KEYS line filed in another period is missing from this one: no figure (same-period rule)."""
    return any(k in filed and not num(r.get(k)) for k in GAP_KEYS)


def roic_row(r, sic, t=None, filed=()):
    """The displayed ROIC fields for one period (ROIC_KEYS): fundamentals.json annual rows and statements.py
    cells. Year-end capital; no other period is read. t: see nopat(). filed: the GAP_KEYS the file carries in
    any period — one of them missing from this row gives no figure (a short-term-investment cell missing in
    one period counts as 0: most filers file it in some years only)."""
    out = dict.fromkeys(ROIC_KEYS)
    if is_financial(sic):
        out["roic_class"] = "financial"
        return out
    if gap(r, filed):
        return out
    n, _ = nopat(r, sic, t)
    ic, basis = invested_capital(r)
    out["roic_basis"] = basis
    if n is None or ic is None:
        return out
    rev = r.get("revenue")
    floor = FLOOR_REV * rev if num(rev) and rev > 0 else 0.0
    if ic > 0 and ic >= floor:
        out["roic_proxy"] = n / ic
        out["roic_class"] = "ok"
        tan = ic - _z(r.get("goodwill")) - _z(r.get("intangibles"))
        if tan > 0 and tan >= floor:
            out["roic_tangible"] = n / tan
    elif n > 0:
        out["roic_class"] = "capital_light" if ic > 0 else "customer_funded"
    else:
        out["roic_class"] = "loss"
    return out


def apply_roic(annual, sic):
    """Rewrite the ROIC_KEYS of every fundamentals.json annual row in place (fundamentals.py, after the
    submissions profile gives the SIC)."""
    filed = filed_keys(annual)
    for r in annual or []:
        r.update(roic_row(r, sic, filed=filed))
    return annual


# ------------------------------------------------------------------ evidence series
def roic_series(ann, sic, filed=None):
    """Per row: v = NOPAT / max(IC, 10% × revenue) clipped to ±100% (equal to roic_row's figure before clipping
    where that is shown), v_tan on IC − goodwill − intangibles, the label and the EBIT margin. filed: see
    roic_row (default: the GAP_KEYS filed in `ann`)."""
    filed = filed_keys(ann) if filed is None else filed
    out = []
    for r in ann:
        n, nb = nopat(r, sic)
        ic, basis = invested_capital(r)
        if gap(r, filed):
            n = nb = ic = basis = None
        gwi = _z(r.get("goodwill")) + _z(r.get("intangibles"))
        d = {"fy": r.get("fy"), "nopat": n, "nopat_basis": nb, "ic": ic, "basis": basis,
             "v": None, "v_tan": None, "label": None, "ebit_margin": None}
        rev = r.get("revenue")
        if n is not None and num(rev) and rev > 0:
            d["ebit_margin"] = n / (1 - tax_rate(r)) / rev
        if n is None or ic is None:
            d["label"] = "no_data"
        elif num(rev) and rev > 0:
            fl = FLOOR_REV * rev
            d["v"], d["v_tan"] = _clip(n / max(ic, fl)), _clip(n / max(ic - gwi, fl))
            d["label"] = "ok" if ic >= fl else "loss" if n <= 0 else "capital_light" if ic > 0 else "customer_funded"
        elif ic > 0:
            d["v"] = _clip(n / ic)
            d["v_tan"] = _clip(n / (ic - gwi)) if ic - gwi > 0 else (CLIP if n > 0 else -CLIP)
            d["label"] = "ok"
        elif n <= 0:
            d["v"], d["v_tan"], d["label"] = -CLIP, -CLIP, "loss"
        else:
            d["label"] = "no_revenue"   # a profit over capital <= 0 with no revenue: unusable
        out.append(d)
    return out


def roe_series(ann, sic):
    """Per row: v = net income / average equity (prior row 300-430 days earlier), tangible at banks (total
    equity when tangible <= 0), clipped to ±100%; equity <= 0 is unusable."""
    tangible = sic is not None and BANK_SIC[0] <= sic <= BANK_SIC[1]
    out = []
    for i, r in enumerate(ann):
        ni, eq, rev = r.get("net_income"), r.get("equity"), r.get("revenue")
        d = {"fy": r.get("fy"), "v": None, "label": None, "leverage": None, "net_margin": None}
        if num(ni) and num(rev) and rev > 0:
            d["net_margin"] = ni / rev
        if num(r.get("assets")) and num(eq) and eq > 0:
            d["leverage"] = r["assets"] / eq
        if not (num(ni) and num(eq)):
            d["label"] = "no_data"
            out.append(d)
            continue
        prev = ann[i - 1] if i > 0 and _adjacent(ann[i - 1], r) and num(ann[i - 1].get("equity")) else None

        def base(tan):
            e = eq - ((_z(r.get("goodwill")) + _z(r.get("intangibles"))) if tan else 0.0)
            if prev is not None:
                e = (e + prev["equity"] - ((_z(prev.get("goodwill")) + _z(prev.get("intangibles"))) if tan else 0.0)) / 2
            return e
        e = base(tangible)
        if tangible and e <= 0:
            e = base(False)
        if e <= 0:
            d["label"] = "equity<=0"
        else:
            d["v"], d["label"] = _clip(ni / e), ("rote" if tangible else "roe")
        out.append(d)
    return out


def path_for(fu):
    """The evidence path for a fundamentals.json dict: 'roic' | 'roe_fin' | 'roe_util' | 'reit_prior'."""
    sic = sic_int(fu)
    last5 = (fu.get("annual") or [])[-WINDOW:]
    oi_years = sum(1 for r in last5 if num(r.get("operating_income")))
    if sic is None:
        return "roic" if oi_years >= 3 else "roe_fin"      # ARCC (a BDC with no SIC) → ROE
    if sic in UTIL_SIC:
        return "roe_util"
    if sic == 6798 or 6510 <= sic <= 6519:
        da = _median([r["da"] / r["revenue"] for r in last5
                      if num(r.get("da")) and num(r.get("revenue")) and r["revenue"] > 0])
        # revenue unread (AMH files no revenue tag the reader takes): depreciation against assets instead
        da_a = _median([r["da"] / r["assets"] for r in last5
                        if num(r.get("da")) and num(r.get("assets")) and r["assets"] > 0]) if da is None else None
        if oi_years >= 3 or (da is not None and da >= REIT_DA[0]) or (da_a is not None and da_a >= REIT_DA[1]):
            return "reit_prior"                              # equity REIT / lessor: efficient-scale prior
        return "roe_fin"                                     # mortgage REIT (NLY, AGNC): a spread lender
    if is_financial(sic):
        return "roe_fin"
    return "roic"                                            # real-estate operators (CBRE, JLL) included


def _interp(knots, x):
    if x <= knots[0][0]:
        return float(knots[0][1])
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return float(knots[-1][1])


def _lev_norm(sic):
    for (lo, hi), n in LEV_NORMS:
        if sic is not None and lo <= sic <= hi:
            return n
    return 4.0


def _anchor(ser, path, sic, level_window=WINDOW, min_usable=MIN_USABLE):
    """The anchor from an oldest-first evidence series (dicts with 'v')."""
    P = PATHS[path]
    h = P["hurdle"]
    vals = [x["v"] for x in ser]
    u5 = [v for v in vals[-level_window:] if v is not None]
    u10 = [v for v in vals[-HIST:] if v is not None]
    res = {"path": path, "hurdle": h, "usable_5": len(u5), "usable_10": len(u10)}
    if len(u5) < min_usable:
        res["status"] = "insufficient_history"
        return res
    m5 = statistics.median(u5)
    level = _interp(P["knots"], m5)
    terms, caps = {}, {}
    hits = sum(1 for v in u10 if v >= h)
    if m5 >= h:
        p = hits / len(u10)
        if p < 0.6:
            terms["persistence"] = -1.0
        elif p < 0.8:
            terms["persistence"] = -0.5
        if min(u10) < 0:
            terms["trough"] = -0.5
    tail = ser[-WINDOW:]
    if path == "roic":
        em = _median([x.get("ebit_margin") for x in tail if x["v"] is not None])
        res["ebit_margin_5y"] = em
        if (len(u10) >= RECORD["years"] and min(u10) >= RECORD["floor"] and m5 >= RECORD["median"]
                and em is not None and em >= LOW_MARGIN[0]):
            terms["record"] = 1.0
        if em is not None and em < LOW_MARGIN[0]:
            caps["low_margin"] = LOW_MARGIN[1]
        if sum(1 for x in tail if x["v"] is not None and x.get("basis") in ("financing", "assets")) >= 3:
            caps["non_operating_basis"] = NON_OP_CAP
    if path == "roe_fin":
        lv = _median([x.get("leverage") for x in tail])
        nm = _median([x.get("net_margin") for x in tail])
        res.update(leverage_5y=lv, leverage_norm=_lev_norm(sic), net_margin_5y=nm)
        if lv is not None and lv > 1.5 * _lev_norm(sic):
            terms["leverage"] = -1.0
        if nm is not None and nm < THIN_NET_MARGIN[0]:
            caps["thin_margin"] = THIN_NET_MARGIN[1]
        if m5 > DATA_CHECK_ROE[0]:
            caps["data_check"] = DATA_CHECK_ROE[1]
    if len(u10) < PROVEN_YEARS:
        caps["short_history"] = SHORT_CAP
    cap = min([P["cap"]] + list(caps.values()))
    base = level + terms.get("persistence", 0.0) + terms.get("trough", 0.0)
    if m5 >= h and base < _interp(P["knots"], h):
        # continuity at the hurdle: a median at or above it never scores below the untermed level at the hurdle,
        # where a median just under it (no terms) would land
        base = _interp(P["knots"], h)
        res["hurdle_floor"] = round(base, 2)
    a = max(0.0, min(cap, base + terms.get("record", 0.0) + terms.get("leverage", 0.0)))
    res.update(status="measured", median_5y=m5, level=round(level, 2), terms=terms, caps=caps,
               hits=hits, hits_of=len(u10), trough=min(u10), anchor=round(a, 2), anchor_r=int(math.floor(a + 0.5)))
    return res


def band_for(anchor_r):
    lo, hi = max(0, anchor_r - BAND), min(10, anchor_r + BAND)
    if anchor_r < WIDE_MIN_ANCHOR:
        hi = min(hi, 8)
    return [lo, hi]


def _context(fu, ser):
    """roic path context: tangible ROIC, goodwill share of IC, acquisition intensity (serial acquirer), and the
    growth / spend ratios EXPENSED_INVESTMENT tests."""
    ann = fu["annual"]
    last5, tail = ann[-WINDOW:], ser[-WINDOW:]
    tan = [x["v_tan"] for x in tail if x.get("v_tan") is not None]
    gw_share = _median([(_z(r.get("goodwill")) + _z(r.get("intangibles"))) / x["ic"]
                        for r, x in zip(last5, tail) if num(x.get("ic")) and x["ic"] > 0])
    ocf = sum(_z(r.get("ocf")) for r in last5)
    acq = sum(abs(_z(r.get("acquisitions"))) for r in last5)
    gwi = [_z(r.get("goodwill")) + _z(r.get("intangibles")) for r in ann]
    base_i = len(ann) - WINDOW - 1 if len(ann) > WINDOW else 0
    d_gwi = max(0.0, gwi[-1] - gwi[base_i])   # the fallback when `acquisitions` is unfiled (TRU, RVTY, ALLE, TKO)
    intensity = (max(acq, d_gwi) / ocf) if ocf > 0 else None
    revs = [r.get("revenue") for r in ann[-4:]]
    cagr = ((revs[-1] / revs[0]) ** (1 / 3) - 1) if len(revs) == 4 and all(num(v) and v > 0 for v in revs) else None
    last = ann[-1]
    rv = last.get("revenue")
    rnd = (last["rnd"] / rv) if num(last.get("rnd")) and num(rv) and rv > 0 else None
    sbc = (last["sbc"] / rv) if num(last.get("sbc")) and num(rv) and rv > 0 else None
    return {"tangible_median_5y": _median(tan) if len(tan) >= MIN_USABLE else None,
            "tangible_years_ge_20": sum(1 for v in tan if v >= 0.20),
            "goodwill_share_of_ic": gw_share,
            "acquisition_intensity_5y": intensity,
            # OCF <= 0 or unfiled: any acquisition spend or goodwill growth counts (ALNY: none → not one)
            "serial_acquirer": (intensity >= SERIAL_ACQUIRER) if intensity is not None else max(acq, d_gwi) > 0,
            "rev_cagr_3y": cagr,
            "gross_margin_5y": _median([r.get("gross_margin") for r in last5 if num(r.get("gross_margin"))]),
            "rnd_pct_rev": rnd, "sbc_pct_rev": sbc}


def evidence(fu):
    """The measured half of the moat for one fundamentals.json dict (None → not measured)."""
    if not isinstance(fu, dict) or not (fu.get("annual") or []):
        return {"version": VERSION, "status": "not_measured", "why": "no fundamentals.json", "anchor": None, "band": None}
    dv = fu.get("dividends")
    if fu.get("currency") not in (None, "USD") and not (isinstance(dv, dict) and dv.get("currency")):
        # a non-USD file written before the one-money-unit rule records no currency on its dividends block (the
        # marker fundamentals.price_dividends reads): its lines may mix currencies (HTHT: USD assets, CNY revenue)
        return {"version": VERSION, "status": "not_measured", "anchor": None, "band": None, "fundamentals_as_of": fu.get("as_of"),
                "why": ("non-USD fundamentals.json with no currency on its dividends block, written by a fundamentals.py "
                        "from before the one-money-unit rule (2026-10-19) whatever its as_of — re-run fundamentals.py")}
    filed = filed_keys(fu["annual"])
    ann = fu["annual"][-HIST:]
    fu = dict(fu, annual=ann)
    sic = sic_int(fu)
    path = path_for(fu)
    ev = {"version": VERSION, "path": path, "sic": sic, "as_of_fy": ann[-1].get("fy"), "fundamentals_as_of": fu.get("as_of")}
    if path == "reit_prior":
        ev.update(status="prior", anchor=float(REIT_PRIOR), anchor_r=REIT_PRIOR, band=band_for(REIT_PRIOR),
                  why="equity REIT: efficient-scale prior, book returns not scored")
        return ev
    ser = roic_series(ann, sic, filed) if path == "roic" else roe_series(ann, sic)
    ev["series"] = ser
    ev.update(_anchor(ser, path, sic))
    if ev["status"] == "insufficient_history":
        ev.update(anchor=None, anchor_r=None, band=list(NO_ANCHOR_BAND),
                  why=f"{ev['usable_5']} usable years in the last {WINDOW} (needs {MIN_USABLE})")
        return ev
    ev["band"] = band_for(ev["anchor_r"])
    if path == "roic":
        ev.update(_context(fu, ser))
    if len(ann) >= 8:
        ev["anchor_10y_r"] = _anchor(ser, path, sic, level_window=HIST).get("anchor_r")
    return ev


# ------------------------------------------------------------------ judgment checks
def _sentence(v):
    """The stripped text of a string field; "" for anything else, so a list or dict never passes a length check."""
    return v.strip() if isinstance(v, str) else ""


def check_sources(sources):
    """None (undeclared, a pre-rubric-2 judgment) or a list of {source, evidence}; ValueError when malformed."""
    if sources is None:
        return None
    if not isinstance(sources, list):
        raise ValueError(f"moat_sources must be a list of {{source, evidence}} objects (source one of {', '.join(SOURCES)})")
    for s in sources:
        if not isinstance(s, dict) or s.get("source") not in SOURCES or len(_sentence(s.get("evidence"))) < 20:
            raise ValueError(f"moat_sources entry {s!r}: source must be one of {', '.join(SOURCES)} and evidence "
                             "a company-specific sentence (a string >= 20 characters)")
    return sources


def check_reason_shape(reason):
    """None or a well-formed {code, text, since_fy | field + fy}; ValueError when malformed."""
    if reason is None:
        return None
    if not isinstance(reason, dict):
        raise ValueError("moat_evidence_reason must be an object {code, text, ...}")
    code = reason.get("code")
    if not isinstance(code, str) or code not in REASONS:
        raise ValueError(f"moat_evidence_reason.code {code!r} must be one of {', '.join(REASONS)}")
    if len(_sentence(reason.get("text"))) < MIN_TEXT:
        raise ValueError(f"moat_evidence_reason.text must state the evidence (a string >= {MIN_TEXT} characters)")
    if code == "BUSINESS_CHANGED" and not str(reason.get("since_fy") or "").strip().isdigit():
        raise ValueError("moat_evidence_reason BUSINESS_CHANGED needs since_fy (the first fiscal year of the changed business)")
    if code == "MEASUREMENT_DEFECT" and (reason.get("field") not in DEFECT_FIELDS
                                         or not str(reason.get("fy") or "").strip().isdigit()):
        raise ValueError(f"moat_evidence_reason MEASUREMENT_DEFECT needs field (one of {', '.join(DEFECT_FIELDS)}) and fy")
    return reason


def check_reason(ev, reason):
    """(accepted, reach_lo, reach_hi, mechanical, why) for a well-formed reason against measured evidence. No
    reach passes 8 unless anchor_r >= 8 (WIDE_MIN_ANCHOR)."""
    check_reason_shape(reason)
    ar = ev.get("anchor_r")
    top = 10 if ar is not None and ar >= WIDE_MIN_ANCHOR else 8
    ok, rlo, rhi, mech, why = _check_reason(ev, reason, ar, top)
    return ok, rlo, min(rhi, top), mech, why


def _check_reason(ev, reason, ar, top):
    code = reason["code"]
    lo, hi = ev["band"]
    mech = REASONS[code][1]
    if code == "NO_DURABLE_SOURCE":
        return True, (max(0, ar - 5) if ar is not None else 0), hi, False, "accepted (text: pass 2 checks the erosion force)"
    if code == "MEASUREMENT_DEFECT":
        return True, 0, top, False, "accepted (text: pass 2 confirms the figure in the filing)"
    if code == "SHORT_HISTORY":
        if ev.get("status") == "prior":
            return False, lo, hi, False, "SHORT_HISTORY does not apply to the equity-REIT prior (no history is scored)"
        if ev.get("usable_10", 0) >= PROVEN_YEARS:
            return False, lo, hi, False, f"SHORT_HISTORY needs fewer than {PROVEN_YEARS} usable years"
        return True, lo, max(hi, 7), False, "accepted (text: the predecessor's or parent's history)"
    if ar is None or ev.get("status") != "measured":
        return False, lo, hi, mech, f"{code} needs a measured anchor"
    if code == "ACQUIRED_GOODWILL":
        ty, gs = ev.get("tangible_years_ge_20") or 0, ev.get("goodwill_share_of_ic") or 0.0
        if ty < 3 or gs < 0.30:
            miss = ([f"tangible ROIC >= 20% in {ty}/5 years (needs 3)"] if ty < 3 else []) + \
                   ([f"goodwill + intangibles {gs:.0%} of capital (needs 30%)"] if gs < 0.30 else [])
            return False, lo, hi, True, "; ".join(miss)
        return True, lo, hi + (1 if ev.get("serial_acquirer") else 2), True, "accepted"
    if code == "EXPENSED_INVESTMENT":
        if not ((ev.get("rev_cagr_3y") or 0) >= 0.15 and (ev.get("gross_margin_5y") or 0) >= 0.50
                and ((ev.get("rnd_pct_rev") or 0) >= 0.15 or (ev.get("sbc_pct_rev") or 0) >= 0.10)):
            return False, lo, hi, True, ("needs 3y revenue CAGR >= 15%, 5y gross margin >= 50%, and R&D >= 15% "
                                         "or SBC >= 10% of revenue")
        return True, lo, max(hi, min(8, max(ar + 3, 5))), True, "accepted"
    if code == "CYCLE_ADJUSTED":
        a10 = ev.get("anchor_10y_r")
        vals = [x["v"] for x in (ev.get("series") or [])[-HIST:] if x["v"] is not None]
        if a10 is None or len(vals) < 8:
            return False, lo, hi, True, "needs >= 8 usable years"
        side = [v >= ev["hurdle"] for v in vals]
        crossings = sum(1 for u, w in zip(side, side[1:]) if u != w)
        if crossings < 2:
            return False, lo, hi, True, f"no cycle: returns crossed the hurdle {crossings} time(s) in {len(vals)} years"
        b10 = band_for(a10)
        up = hi if ev.get("serial_acquirer") else b10[1]   # acquisitions, not the cycle, explain a serial acquirer
        return True, min(lo, b10[0]), max(hi, up), True, f"10-year anchor {a10}"
    if code == "BUSINESS_CHANGED":
        # the changed business is measured by the main rules: MIN_USABLE usable years since the change, and a
        # change inside the level window (an earlier since_fy would only drop old years from persistence)
        ser = ev.get("series") or []
        since = str(reason["since_fy"]).strip()
        first = str(ser[-WINDOW:][0].get("fy")) if ser else ""
        if since < first:
            return False, lo, hi, True, f"since_fy {since} is before the {WINDOW}-year window (FY{first} on)"
        a2 = _anchor([x for x in ser if str(x.get("fy")) >= since], ev["path"], ev.get("sic"))
        if a2.get("status") != "measured":
            return False, lo, hi, True, f"{a2['usable_5']} usable years since FY{since} (needs {MIN_USABLE})"
        b2 = band_for(a2["anchor_r"])
        return True, min(lo, b2[0]), max(hi, b2[1]), True, f"post-change anchor {a2['anchor_r']}"
    return False, lo, hi, mech, "unknown code"


def assess(ev, moat, reason=None, sources=None):
    """Where a judgment moat sits against the evidence. sources None = undeclared; [] = declared none.
    ValueError on a malformed reason or source."""
    check_sources(sources)
    check_reason_shape(reason)
    if not num(moat):
        raise ValueError(f"moat_score must be a finite number, got {moat!r}")
    out = {"moat": float(moat), "sources_declared": sources is not None, "entry_gate_closed": False}
    if ev.get("band") is None:
        out["status"] = "not_measured"
        return out
    lo, hi = ev["band"]
    if isinstance(sources, list) and not sources:
        lo, hi = min(lo, NO_SOURCE_CAP), min(hi, NO_SOURCE_CAP)
    out["band"] = [lo, hi]
    m = float(moat)
    if lo <= m <= hi:
        out["status"] = "in_band"
        return out
    direction = "above" if m > hi else "below"
    out["direction"] = direction
    if reason is not None:
        ok, rlo, rhi, mech, why = check_reason(ev, reason)
        out["reason_code"] = reason["code"]
        d = REASONS[reason["code"]][0]
        if ok and d != "both" and d != ("up" if direction == "above" else "down"):
            ok, why = False, f"{reason['code']} explains a moat {'above' if d == 'up' else 'below'} the band only"
        if ok and isinstance(sources, list) and not sources:
            rhi = min(rhi, NO_SOURCE_CAP)
        if ok and rlo <= m <= rhi:
            out.update(status="outside_band_explained", reach=[rlo, rhi], reason_tested=mech)
            out["entry_gate_closed"] = direction == "above" and not mech   # text never reopens the entry gate
            return out
        out["reason_rejected"] = why if not ok else f"moat {m:g} beyond the reason's reach {rlo}–{rhi}"
    out["status"] = "outside_band_unexplained"
    out["flag"] = "MOAT_ABOVE_EVIDENCE" if direction == "above" else "MOAT_BELOW_EVIDENCE"
    out["entry_gate_closed"] = direction == "above"
    return out


# ------------------------------------------------------------------ records and printouts
def _r4(v):
    return round(v, 4) if num(v) else v


def record(ev, a):
    """The score.json `moat_evidence` block: evidence (compact) + the assessment."""
    keep = ("version", "status", "path", "sic", "as_of_fy", "fundamentals_as_of", "why", "hurdle", "median_5y", "hits", "hits_of",
            "level", "terms", "hurdle_floor", "caps", "anchor", "anchor_r", "band", "anchor_10y_r", "tangible_median_5y",
            "goodwill_share_of_ic", "acquisition_intensity_5y", "serial_acquirer")
    out = {"rubric": RUBRIC}
    out.update({k: _r4(ev[k]) for k in keep if k in ev})
    out["evidence_band"] = out.pop("band", None)
    out["evidence_status"] = out.pop("status", None)
    if ev.get("series"):
        out["series"] = [[x.get("fy"), _r4(x.get("v")), x.get("label")] for x in ev["series"][-WINDOW:]]
    out.update({k: v for k, v in a.items() if k != "moat"})
    return out


def _fmt(v):
    if v is None:
        return "—"
    if v >= CLIP:
        return ">100%"
    if v <= -CLIP:
        return "<-100%"
    return f"{v * 100:.1f}%"


PATH_NAMES = {"roic": "ROIC (after-tax operating income ÷ operating capital incl. goodwill; floor 10% of revenue)",
              "roe_fin": "ROE on average equity (tangible at banks)", "roe_util": "ROE on average equity (regulated utility)"}


def key_numbers_lines(ev, a=None):
    """The key_numbers.md lines (and this file's CLI printout)."""
    dated = f" · fundamentals.json as of {ev['fundamentals_as_of']}" if ev.get("fundamentals_as_of") else ""
    if ev.get("band") is None:
        L = [f"- Moat evidence: not measured ({ev.get('why')}) — run fundamentals.py, then judge from the rubric"]
    elif ev.get("status") == "prior":
        L = [f"- Moat evidence: equity REIT, efficient-scale prior {REIT_PRIOR} · band {ev['band'][0]}–{ev['band'][1]}{dated}"]
    else:
        ser = " / ".join(f"FY{x['fy']} {_fmt(x['v'])}" + ("" if x.get("label") in ("ok", "roe", "rote") else f" ({x['label']})")
                         for x in ev["series"][-WINDOW:])
        head = f"- Moat evidence ({ev['path']}, hurdle {ev['hurdle']:.0%}): {PATH_NAMES[ev['path']]}: {ser}"
        if ev.get("anchor") is None:
            L = [f"{head} · insufficient history ({ev.get('why')}) · band {ev['band'][0]}–{ev['band'][1]}{dated}"]
        else:
            t = ", ".join(f"{k} {v:+g}" for k, v in ev["terms"].items())
            c = ", ".join(f"{k} ≤{v:g}" for k, v in ev["caps"].items())
            L = [f"{head} · 5y median {_fmt(ev['median_5y'])} · years ≥ {ev['hurdle']:.0%}: {ev['hits']}/{ev['hits_of']}"
                 f" · level {ev['level']:g}" + (f" · {t}" if t else "")
                 + (f" · hurdle floor {ev['hurdle_floor']:g}" if ev.get("hurdle_floor") is not None else "")
                 + (f" · caps {c}" if c else "")
                 + f" → anchor {ev['anchor']:g} ({ev['anchor_r']}) · band {ev['band'][0]}–{ev['band'][1]}{dated}"]
        if ev.get("path") == "roic" and ev.get("anchor") is not None:
            ai = ev.get("acquisition_intensity_5y")
            gs = ev.get("goodwill_share_of_ic")
            L.append(f"- ROIC ex-goodwill (context only): 5y median {_fmt(ev.get('tangible_median_5y'))} · goodwill + "
                     f"intangibles {_fmt(gs) + ' of capital' if gs is not None else 'n/a (capital <= 0)'} · acquisitions "
                     + (f"{ai * 100:.0f}% of 5y OCF" if ai is not None else "n/a (OCF <= 0)")
                     + (" — serial acquirer: the OE never deducts acquisitions, judge on the goodwill-inclusive return"
                        if ev.get("serial_acquirer") else ""))
    if a is not None:
        st = a.get("status")
        m = f"{a['moat']:g}"
        if st == "not_measured":
            L.append(f"- Moat vs evidence: {m} → not measured")
        elif st == "in_band":
            L.append(f"- Moat vs evidence: {m} → in band {a['band'][0]}–{a['band'][1]}")
        elif st == "outside_band_explained":
            L.append(f"- Moat vs evidence: {m} → {a['direction']} band {a['band'][0]}–{a['band'][1]}, explained by "
                     f"{a['reason_code']} (reach {a['reach'][0]}–{a['reach'][1]}"
                     + ("; text-only reason — entry alert closed)" if a.get("entry_gate_closed") else ")"))
        else:
            L.append(f"- Moat vs evidence: {m} → {a['direction']} band {a['band'][0]}–{a['band'][1]}, unexplained ({a['flag']}"
                     + (" — entry alert closed" if a.get("entry_gate_closed") else "")
                     + (f"; reason rejected: {a['reason_rejected']}" if a.get("reason_rejected") else "") + ")")
        if not a.get("sources_declared"):
            L.append("- Moat sources: not declared (judgment.json moat_sources, rubric 2)")
    return L


def load_fundamentals(folder):
    """A folder's fundamentals.json as a dict, None when absent or unreadable."""
    try:
        with open(os.path.join(folder, "fundamentals.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")   # a cp1252 console never crashes on '≥' / '→'
        except (AttributeError, ValueError, OSError):
            pass
    ap = argparse.ArgumentParser(prog="moat_evidence.py", description="Moat evidence for one folder (moat rubric 2).")
    ap.add_argument("ticker")
    ap.add_argument("--moat", type=float, help="the moat to assess (default: judgment.json moat_score)")
    ap.add_argument("--json", action="store_true", help="print the score.json moat_evidence block")
    opt = ap.parse_args()
    if opt.moat is not None and not (num(opt.moat) and 0 <= opt.moat <= 10):
        ap.error("--moat must be a number 0-10")
    folder = os.path.join(BASE, opt.ticker.upper())
    ev = evidence(load_fundamentals(folder))
    j = {}
    try:
        with open(os.path.join(folder, "judgment.json"), encoding="utf-8") as f:
            j = json.load(f)
    except (OSError, ValueError):
        j = {}
    j = j if isinstance(j, dict) else {}
    moat = opt.moat
    if moat is None and num(j.get("moat_score")):
        moat = float(j["moat_score"])
    a = None
    if moat is not None:
        try:
            a = assess(ev, moat, j.get("moat_evidence_reason"), j.get("moat_sources"))
        except ValueError as e:
            print(f"moat_evidence.py: judgment.json is malformed — {e}", file=sys.stderr)
            sys.exit(1)
    if opt.json:
        print(json.dumps(record(ev, a or {"moat": None}), indent=1, default=str))
    else:
        print("\n".join(key_numbers_lines(ev, a)))


if __name__ == "__main__":
    main()
