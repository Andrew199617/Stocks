#!/usr/bin/env python3
"""The moat scorecard make_score checks — engine 5.7 (Andrew, 2026-10-19, R4 REVISED: "It should be a combination" of
Pat Dorsey's moat framework and the evidence scorecard; amendments M1b and M1c the same day; design 03b with the main
agent's decisions 03c, 2026-10-20, and the lane defaults of 2026-10-21). Policy-bearing. Pure: reads the folder's own
files, never the network, never writes.

The moat stays ONE 0-10 judgment that sets the fade only (CAP = clamp(2 + 1.3 x moat, 2, 15); M0: one lever per
question — risk in the probabilities, growth in the growth start, return on capital in the capex inside owner's
earnings, the moat in the fade). judgment.json `moat_scorecard` backs it in two layers and make_score checks it
(score.json `moat_evidence`, key_numbers.md "## Moat scorecard"):

Layer 1 — SOURCES (WHY the moat exists; M1, M1c): a closed enum of eight types — intangible_assets, switching_costs,
network_effects, cost_advantage, size_advantage (Dorsey), efficient_scale (Morningstar), counter_positioning (Helmer),
customer_captivity (Greenwald) — with closed subtypes, a strength (narrow | wide) and facts (facts.json ids, used_for
moat:sources) or measured metrics. Great products, market share, execution, management and M1c's non-sources (first
mover, technology lead, high growth, a big market, partnerships, culture) are never a source. Rules S1-S9 / W1-W8;
source caps: no source -> moat <= 3, one narrow source -> <= 6, 7+ needs a wide source or two fact-backed sources, 9+
two wide sources and returns_on_capital +2 sustained. No reason field relaxes a cap.

Layer 2 — EVIDENCE (DOES it compound; M2, M1b): 11 core pillars (total weight 16) — four MECHANICAL ones make_score
derives (returns_on_capital on the governing measure: ROIC, tangible ROIC when goodwill + intangibles exceed 30% of
invested capital, ROE at a balance-sheet financial incl. a SIC-6798 mortgage REIT; industry_structure from
same-ladder SIC peers in _system/industry_returns.json; capital_intensity; scale_economics) and seven DECLARED ones
citing facts.json series — and four SUPPORTING factors (product_quality, market_share, execution, management) whose
sum / 4, capped at +-1, is added to the core evidence (03c decision 11: a lone factor moves it by at most 0.25,
management -2 by 0.50). core = 5 + 5 x weighted mean of each score over its own range end; evidence = clamp(core +
supporting adjustment, 0, 10).

Gates on a 5.7 run (G1-G6): the moat within +-2 of the evidence score or a moat_divergence_reason carrying a number;
the core weight floor 8; the source caps; 7+ on a governing return below 10% (ROE 15%) or unmeasured needs
low_roic_reason; 4 or below on a governing return of 20%+ with every year >= 15% needs high_return_low_moat_reason
(under tangible governance only when the plain ROIC median is >= 10%, 03c decision 2); MOAT_EROSION (governing return
AND margin both down over the last 5 FY; operating margin where gross margin is not filed, fundamentals.json rows
only — 10b COVERAGE, lane default Q4) with erosion_risks +1 needs erosion_rebuttal carrying a number. Every reason is
an influence field (make_score.check_influence). GATE_DRIFT_ON_REBUILD (03c decision 6, True): on a rebuild — the
same engine run, the same declaration, the same facts.json — a newly failing DATA-driven gate is recorded in
`gate_drift`, never refused; caps and rules that depend only on the declaration refuse everywhere.

Acquired IPR&D (engine 5.6's one-time value deduction; lane default Q3 (b), main agent 2026-10-21): the charge the
engine deducted once from value is added back to EBIT in returns_on_capital and scale_economics for those fiscal
years (never when the engine judged it recurrent), so the moat — and through it the fade — does not take it twice;
the IPRD_CHARGE_IN_WINDOW flag and the per-year add-back stay on record. ADDBACK_IPRD is the one switch.

Output from an engine release before 5.7.0 (every folder on file until its next engine run) is evaluated
report_only: mechanical pillars, flags and lint, nothing refused. A scorecard that is present is shape-checked on
any release.

CLI: python3 _system/moat_scorecard.py <T>  — read-only dry run with the 5.7 rules on (prints the evidence, the
governing measure, sources and caps, every gate, lint; exit 0, or 1 on a refusal). Workers run it before the final
engine run (WORKER_SPEC step 5).
"""
import csv
import datetime
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facts as _facts  # noqa: E402  (the rulings-release predicate, period helpers; stdlib only)
from fundamentals import capital_returns_from_row, row_ebit  # noqa: E402  (the ONE returns function)
import dcf_engine as _engine  # noqa: E402  (sic_misfit_class, IPRD_TREATMENT_ONE_TIME; no I/O at import)

# ---------------------------------------------------------------------------
# Constants (03b §10.1 with 03c's decisions folded in)
# ---------------------------------------------------------------------------
SCORECARD_VERSION = 1
BUSINESS_TYPES = ("consumer_users", "enterprise_recurring", "consumer_brands_retail", "industrial", "healthcare",
                  "commodity_producer", "financial_balance_sheet", "financial_fee", "real_assets")
MECHANICAL = ("returns_on_capital", "industry_structure", "capital_intensity", "scale_economics")
DECLARED = ("pricing_power", "retention", "reach_and_growth", "switching_costs", "concentration", "erosion_risks",
            "customer_regard")
CORE = MECHANICAL + DECLARED
SUPPORTING = ("product_quality", "market_share", "execution", "management")
RETIRED_PILLARS = {"market_position": "supporting.market_share", "reinvestment_discipline": "supporting.management",
                   "capital_allocation": "supporting.management", "durability_risks": "pillars.erosion_risks"}
WEIGHTS = {"returns_on_capital": 3.0, "industry_structure": 1.5, "capital_intensity": 1.0, "scale_economics": 1.0,
           "retention": 2.0, "pricing_power": 2.0, "switching_costs": 1.5, "erosion_risks": 1.5,
           "reach_and_growth": 1.0, "concentration": 1.0, "customer_regard": 0.5}
RANGES = {k: (-2, 2) for k in CORE}
RANGES["erosion_risks"] = (-2, 1)
SUPPORTING_RANGES = {"product_quality": (-1, 1), "market_share": (-1, 1), "execution": (-1, 1), "management": (-2, 1)}
SUPPORTING_DIVISOR = 4.0   # 03c decision 11 (main agent's calibration of M1b, 2026-10-20): sum of the four slots / 4
SUPPORTING_CAP = 1.0       # M1b: together they move the evidence score by at most one point
NA_ALLOWED = {"consumer_users": set(), "enterprise_recurring": {"customer_regard"},
              "consumer_brands_retail": {"switching_costs"}, "industrial": {"customer_regard"},
              "healthcare": {"customer_regard", "retention"},
              "commodity_producer": {"retention", "switching_costs", "customer_regard"},
              "financial_balance_sheet": {"customer_regard"}, "financial_fee": {"customer_regard"},
              "real_assets": {"customer_regard", "switching_costs"}}
MECH_NA = {
    ("financial_balance_sheet", "capital_intensity"): "balance-sheet financial: operating cash flow carries deposit / "
        "loan / policyholder flows and capex is immaterial, so capex / OCF measures nothing",
    ("financial_balance_sheet", "scale_economics"): "balance-sheet financial: no operating-income line comparable to "
        "revenue (interest expense is cost of goods), so an operating margin trend is not measured",
    ("real_assets", "capital_intensity"): "real assets: growth capital (rate base, acquisitions, development) earns an "
        "allowed or contracted return and is funded outside OCF; capex / OCF measures the build-out rate, not the "
        "franchise",
}
LADDERS = {"default": (0.20, 0.15, 0.10, 0.05), "real_assets": (0.08, 0.06, 0.04, 0.025), "roe": (0.15, 0.12, 0.09, 0.06)}
LADDER_FAMILY = {"financial_balance_sheet": "roe", "real_assets": "real_assets"}   # else "default"
INTANGIBLE_SHARE_GOVERNS = 0.30          # goodwill + intangibles > 30% of invested capital -> tangible ROIC governs
TANGIBLE_PLUS2_PLAIN_LINE = 0.10         # 03c decision 2: tangible-governed +2 also needs the plain ROIC median >= 10%
ROA_LINE = 0.07                          # Dorsey: ROA >= 7% likely has a competitive advantage (cross-check, not scored)
LOW_RETURN = (7, 0.10, 0.15)             # G4: moat >= 7 on governing < 10% (ROE < 15%) or unmeasured
REVERSE = (4, 0.20, 0.15)                # G5: moat <= 4 on governing >= 20% with every valid year >= 15%
EROSION_T = (0.03, 0.20, 0.02)           # 03c decision 3: returns -3pp and -20% of the start, margin -2pp, OLS slopes < 0
TOLERANCE = 2.0
MIN_EVIDENCE_WEIGHT = 8.0
SERIES_MIN_PERIODS = 3
SERIES_MIN_SPAN_DAYS = 360
INFLATION_HURDLE = 0.03
FLAT = 0.01
POINT_OK_PILLARS = {"switching_costs", "erosion_risks", "execution", "management"}
POINT_FACT_TYPES = {"event"}
PILLAR_FACT_TYPES = {"actual", "metric", "event"}   # 07 §1.6: no guidance / estimate, no range values
THIRD_PARTY_CAP = 1
SOURCE_TYPES = {
    "intangible_assets": ("brand", "patent", "license_regulatory", "content_ip", "trade_secret", "proprietary_data"),
    "switching_costs": ("workflow_training", "data_integration", "contractual", "risk_of_change", "embedded_component",
                        "installed_base_aftermarket"),
    "network_effects": ("two_sided_marketplace", "user_network", "data_network", "ecosystem_complements"),
    "cost_advantage": ("process", "location", "unique_asset", "cornered_resource", "shared_scale"),
    "size_advantage": ("distribution_density", "manufacturing_scale", "purchasing_scale", "capital_barrier"),
    "efficient_scale": ("niche", "infrastructure"),
    "counter_positioning": ("business_model",),
    "customer_captivity": ("habit", "search_cost_trust"),
}
SOURCE_ORIGIN = {"intangible_assets": "Dorsey", "switching_costs": "Dorsey", "network_effects": "Dorsey",
                 "cost_advantage": "Dorsey + Helmer", "size_advantage": "Dorsey + M1c", "efficient_scale": "Morningstar",
                 "counter_positioning": "Helmer", "customer_captivity": "Greenwald"}
SUBTYPE_ALIASES = {("switching_costs", "training"): ("switching_costs", "workflow_training"),
                   ("switching_costs", "data"): ("switching_costs", "data_integration"),
                   ("switching_costs", "integration"): ("switching_costs", "data_integration"),
                   ("switching_costs", "contract"): ("switching_costs", "contractual"),
                   ("switching_costs", "risk-of-change"): ("switching_costs", "risk_of_change"),
                   ("network_effects", "marketplace"): ("network_effects", "two_sided_marketplace"),
                   ("network_effects", "exchange"): ("network_effects", "two_sided_marketplace"),
                   ("network_effects", "communication"): ("network_effects", "user_network"),
                   ("network_effects", "payments"): ("network_effects", "user_network"),
                   ("size_advantage", "niche"): ("efficient_scale", "niche")}
SOURCE_METRICS = ("returns_on_capital", "capital_intensity", "scale_economics")
SOURCE_KEYS = ("type", "subtype", "strength", "facts", "metrics", "rationale")
SOURCE_EXTRA_KEYS = {"expiry_years": ("intangible_assets", "patent"), "incumbents": ("counter_positioning", None),
                     "competitors": ("efficient_scale", None)}
AFTERMARKET_METRICS = {"aftermarket_revenue_share", "recurring_revenue_share", "service_revenue_share",
                       "consumables_revenue_share"}
PROCESS_LEAD_METRICS = {"unit_cost_lead", "yield_lead"}
CAPTIVITY_METRICS = {"retention_rate", "gross_retention", "net_revenue_retention", "renewal_rate", "churn_rate",
                     "repeat_purchase_rate", "repeat_customer_share"}
EFFICIENT_SCALE_MAX_COMPETITORS = 5      # 03c decision 7
COST_OF_CAPITAL_LINE = {"default": 0.10, "real_assets": 0.06, "roe": 0.12}   # 03c decision 15 (ROE moved to 12%)
PATENT_NARROW_YEARS = 5
PROCESS_LEAD_MIN_FY = 5
PROCESS_LEAD_MIN_SPAN_DAYS = 1440
NO_SOURCE_CAP = 3
ONE_NARROW_CAP = 6
WIDE_OR_TWO_MIN = 7
TWO_WIDE_MIN = 9
GATE_DRIFT_ON_REBUILD = True             # 03c decision 6 (main agent, 2026-10-20)
ADDBACK_IPRD = True                      # lane default Q3 (b) (main agent, 2026-10-21): the one switch
REIT_LOCK = {"financial_assets_share": 0.50, "liabilities_share": 0.75,
             "bank_revenue_bases": ("InterestIncomeExpenseNet + NoninterestIncome", "Revenues (bank total)")}
EROSION_THREATS = ("technology_substitution", "reinvestment_away_from_moat", "subsidized_competitor",
                   "patent_licence_expiry", "regulation")
# the top-level keys a moat_scorecard may carry — one constant so the fade lane (L3b) adds widening_declined here
SCORECARD_KEYS = ("version", "business_type", "business_type_reason", "sources", "pillars", "supporting",
                  "volume_price", "moat_divergence_reason", "low_roic_reason", "high_return_low_moat_reason",
                  "erosion_rebuttal")
REASON_FIELDS = ("moat_divergence_reason", "low_roic_reason", "high_return_low_moat_reason", "erosion_rebuttal")
REASON_GATE = {"moat_divergence_reason": "divergence", "low_roic_reason": "low_return",
               "high_return_low_moat_reason": "reverse", "erosion_rebuttal": "erosion"}
DECLARED_PILLAR_KEYS = ("score", "rationale", "facts", "applicable", "not_applicable_reason")
INDUSTRY_MIN_PEERS = 5
INDUSTRY_LEVELS = (4, 3, 2)
INDUSTRY_FILE = "industry_returns.json"
NOTE_INF = "unbounded_high"
NOTES_NEG_INF = ("loss_on_nonpositive_capital", "loss_on_unstable_capital")
# M1b / M1c bad-moat wording (03b §2.5, round 3: SRC is anchored source PHRASES)
BAD = re.compile(r"(?<!\w)(?:leader|leading|leadership|market[- ]share|share leader|best[- ]in[- ]class|execution|"
                 r"execut(?:e|es|ed|ing)|management|manag(?:ement|er)s? team|great products?|best products?|#1|no\. ?1|"
                 r"number[- ]one|dominan\w*|top[- ]tier|first[- ]mover|technology lead|tech(?:nology)? leader|"
                 r"fast[- ]growing|high growth|(?:large|huge) (?:TAM|addressable market)|partnerships?|culture)(?!\w)", re.I)
SRC = re.compile(
    r"(?<!\w)(?:switching[- ]costs?|lock[- ]?in|network[- ]effects?|network economics|two[- ]sided|marketplaces?|"
    r"brands?|brand[- ]name|patents?|patented|licen[cs](?:e|es|ed|ing)|(?<!un)(?<!un-)regulated|regulatory|"
    r"franchises?|exclusive|exclusivity|cost advantages?|low[- ]cost|lowest[- ]cost|"
    r"economies of scale|scale (?:advantages?|economies)|route density|density|unique assets?|"
    r"reserves?|installed[- ]base|embedded|integrated into|deeply integrated|contractual|multi[- ]year contracts?|"
    r"long[- ]term contracts?|take[- ]or[- ]pay|recurring revenue|(?:customer|client|subscriber|user) retention|"
    r"retention rates?|renewal rates?|renewals?|pricing power|price increases?|spec(?:ced)?[- ]in|certifi(?:ed|cation|cations)|"
    r"efficient scale|few competitors|duopoly|oligopoly|habit(?:ual|-forming| forming)|search[- ]costs?|"
    r"trusted (?:provider|advisor|brand)|cornered resource|aftermarket|ecosystem|counter[- ]position(?:ing|ed)?|"
    r"captive|captivity|proprietary data|trade secrets?)(?!\w)", re.I)
SUPPORT_CITE = re.compile(r"\(supporting: ?(?:product_quality|market_share|execution|management)\)")
DIGIT = re.compile(r"\d")
# The 83 SEC / OSHA two-digit SIC major groups (industry labels)
MAJOR_GROUPS = {
    "01": "Agricultural Production - Crops", "02": "Agricultural Production - Livestock", "07": "Agricultural Services",
    "08": "Forestry", "09": "Fishing, Hunting and Trapping", "10": "Metal Mining", "12": "Coal Mining",
    "13": "Oil and Gas Extraction", "14": "Mining and Quarrying of Nonmetallic Minerals",
    "15": "Building Construction - General Contractors", "16": "Heavy Construction other than Building",
    "17": "Construction - Special Trade Contractors", "20": "Food and Kindred Products", "21": "Tobacco Products",
    "22": "Textile Mill Products", "23": "Apparel and Other Finished Products", "24": "Lumber and Wood Products",
    "25": "Furniture and Fixtures", "26": "Paper and Allied Products", "27": "Printing, Publishing and Allied Industries",
    "28": "Chemicals and Allied Products", "29": "Petroleum Refining and Related Industries",
    "30": "Rubber and Miscellaneous Plastics Products", "31": "Leather and Leather Products",
    "32": "Stone, Clay, Glass and Concrete Products", "33": "Primary Metal Industries", "34": "Fabricated Metal Products",
    "35": "Industrial and Commercial Machinery and Computer Equipment",
    "36": "Electronic and Other Electrical Equipment and Components", "37": "Transportation Equipment",
    "38": "Measuring, Analyzing and Controlling Instruments", "39": "Miscellaneous Manufacturing Industries",
    "40": "Railroad Transportation", "41": "Local and Suburban Transit", "42": "Motor Freight Transportation",
    "43": "United States Postal Service", "44": "Water Transportation", "45": "Transportation by Air",
    "46": "Pipelines, Except Natural Gas", "47": "Transportation Services", "48": "Communications",
    "49": "Electric, Gas and Sanitary Services", "50": "Wholesale Trade - Durable Goods",
    "51": "Wholesale Trade - Nondurable Goods", "52": "Building Materials, Hardware, Garden Supply",
    "53": "General Merchandise Stores", "54": "Food Stores", "55": "Automotive Dealers and Gasoline Service Stations",
    "56": "Apparel and Accessory Stores", "57": "Home Furniture, Furnishings and Equipment Stores",
    "58": "Eating and Drinking Places", "59": "Miscellaneous Retail", "60": "Depository Institutions",
    "61": "Non-depository Credit Institutions", "62": "Security and Commodity Brokers, Dealers, Exchanges and Services",
    "63": "Insurance Carriers", "64": "Insurance Agents, Brokers and Service", "65": "Real Estate",
    "67": "Holding and Other Investment Offices", "70": "Hotels, Rooming Houses, Camps, and Other Lodging Places",
    "72": "Personal Services", "73": "Business Services", "75": "Automotive Repair, Services and Parking",
    "76": "Miscellaneous Repair Services", "78": "Motion Pictures", "79": "Amusement and Recreation Services",
    "80": "Health Services", "81": "Legal Services", "82": "Educational Services", "83": "Social Services",
    "84": "Museums, Art Galleries and Botanical and Zoological Gardens", "86": "Membership Organizations",
    "87": "Engineering, Accounting, Research, Management and Related Services", "88": "Private Households",
    "89": "Services, Not Elsewhere Classified", "91": "Executive, Legislative and General Government",
    "92": "Justice, Public Order and Safety", "93": "Public Finance, Taxation and Monetary Policy",
    "94": "Administration of Human Resource Programs", "95": "Administration of Environmental Quality and Housing Programs",
    "96": "Administration of Economic Programs", "97": "National Security and International Affairs",
    "99": "Nonclassifiable Establishments"}


class MoatRefusal(Exception):
    """A moat_scorecard / gate violation: make_score refuses the score (nothing written)."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _fnum(x):
    """A finite number from a number or a CSV string, else None (bool refused)."""
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x) if math.isfinite(x) else None
    try:
        v = float(str(x).strip())
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _r(x, d=4):
    return None if x is None or not math.isfinite(x) else round(x, d)


def _median(vals):
    """Median of numbers that may be +-inf. Even count: the mean of the two middle values, except a -inf / +inf pair
    (undefined) gives the lower one."""
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return None
    if n % 2:
        return s[n // 2]
    a, b = s[n // 2 - 1], s[n // 2]
    if a == b:
        return a
    m = (a + b) / 2
    return a if math.isnan(m) else m


def _pct(x, d=2):
    if x is None:
        return "n/m"
    if x == math.inf:
        return "unbounded"
    if x == -math.inf:
        return "loss on non-positive capital"
    return f"{x * 100:.{d}f}%"


def _sgn(s):
    return "n/a" if s is None else f"{s:+d}"


def _ladder(x, t):
    return 2 if x >= t[0] else 1 if x >= t[1] else 0 if x >= t[2] else -1 if x >= t[3] else -2


def _slope(ys):
    n = len(ys)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0


def _value(v, note):
    """A year's measure as a number for medians: the ratio, +inf for unbounded_high, -inf for a loss on non-positive or
    unstable capital, None when the year is not measured."""
    if v is not None:
        return v
    if note == NOTE_INF:
        return math.inf
    if note in NOTES_NEG_INF:
        return -math.inf
    return None


def _med_record(vals, neg_note="loss_on_nonpositive_capital"):
    """(median for JSON or None, median_note) of a list of measured values (+-inf allowed)."""
    m = _median(vals)
    if m is None:
        return None, None
    if m == math.inf:
        return None, NOTE_INF
    if m == -math.inf:
        return None, neg_note
    return _r(m), None


def _canon_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                     default=str).encode("utf-8")).hexdigest()


def declaration_sha256(j):
    """sha256 of the canonical JSON of {moat_score, moat_scorecard} — the declaration half of authoring vs rebuild."""
    return _canon_sha({"moat_score": j.get("moat_score"), "moat_scorecard": j.get("moat_scorecard")})


def facts_sha256(folder):
    """sha256 of facts.json's canonical JSON (None when absent / unreadable) — the facts half of authoring vs rebuild
    (rebase L3 amendment 3.2 (d): an edited facts.json with an unchanged judgment is an authoring run)."""
    try:
        with open(os.path.join(folder, "facts.json"), encoding="utf-8") as f:
            return _canon_sha(json.load(f))
    except (OSError, ValueError):
        return None


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Rows: fundamentals.json annual rows (>= 3) else financials_history.csv — every year through the ONE returns function
# ---------------------------------------------------------------------------
def csv_row(r):
    """financials_history.csv row (strings) -> the canonical raw keys capital_returns_from_row reads (csv=True). Engine
    5.5+ CSVs: total_debt = the engine's assembled `debt_total`, `assets` / `liabilities` from their columns, `cash` is
    the engine's available cash; earlier CSVs: debt_current + debt_lt when either is filed. The CSV has no pre-tax income, interest,
    goodwill or intangibles column."""
    g = lambda k: _fnum(r.get(k))  # noqa: E731
    if g("debt_total") is not None:
        td = g("debt_total")
    elif g("debt_current") is not None or g("debt_lt") is not None:
        td = (g("debt_current") or 0.0) + (g("debt_lt") or 0.0)
    else:
        td = None
    pe = str(r.get("period_end") or "")
    return {"period_end": pe, "fy": str(r.get("fy_label") or pe[:4]), "revenue": g("revenue"),
            "operating_income": g("operating_income"), "pretax_income": None, "interest_expense": None,
            "tax": g("tax"), "net_income": g("net_income"), "equity": g("equity"), "total_debt": td, "cash": g("cash"),
            "goodwill": None, "intangibles": None, "assets": g("assets"), "liabilities": g("liabilities"),
            "gross_margin": None, "revenue_basis": None, "financial_assets_pct_assets": None,
            "ocf": g("ocf"), "capex": g("capex"),
            "capex_assumed_zero": str(r.get("capex_assumed_zero") or "").strip().lower() == "true"}


def _csv_raw(folder):
    try:
        with open(os.path.join(folder, "financials_history.csv"), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r.get("period_end")]
    except (OSError, csv.Error, UnicodeDecodeError):
        return []
    rows.sort(key=lambda r: r["period_end"])
    return [csv_row(r) for r in rows]


def raw_rows(folder):
    """(source, rows, is_csv): the last 5 fiscal years — fundamentals.json annual rows when it has >= 3, else the CSV."""
    doc = _read_json(os.path.join(folder, "fundamentals.json"))
    ann = doc.get("annual") if isinstance(doc, dict) else None
    a = sorted((r for r in (ann if isinstance(ann, list) else []) if isinstance(r, dict) and isinstance(r.get("period_end"), str)),
               key=lambda r: r["period_end"])
    if len(a) >= 3:
        return "fundamentals.json", [dict(r, fy=str(r.get("fy") or r["period_end"][:4])) for r in a[-5:]], False
    return "financials_history.csv", _csv_raw(folder)[-5:], True


def year_record(r, is_csv, addback=None):
    """One fiscal year: capital_returns_from_row (with the IPR&D add-back when given) + ROE / ROA (equity > 0 only)."""
    cr = capital_returns_from_row(r, csv=is_csv, ebit_addback=addback)
    ni, eq, assets = _fnum(r.get("net_income")), _fnum(r.get("equity")), _fnum(r.get("assets"))
    roe = (ni / eq) if (ni is not None and eq is not None and eq > 0) else None
    roa = (ni / assets) if (ni is not None and assets) else None
    ebit, _, _ = row_ebit(r, csv=is_csv)
    if ebit is not None and addback:
        ebit += addback
    return dict(cr, fy=r.get("fy"), period_end=r.get("period_end"), roe=roe, roa=roa, ebit=ebit,
                revenue=_fnum(r.get("revenue")), gross_margin=_fnum(r.get("gross_margin")),
                iprd_addback=addback or None)


def annual_rows(folder, addbacks=None):
    """(source, rows): raw_rows through year_record — each year recomputed from its raw fields with
    fundamentals.capital_returns_from_row, so a fundamentals.json written before engine 5.7 scores exactly like a
    refreshed one. addbacks: {period_end: one-time EBIT add-back} (acquired IPR&D)."""
    src, raw, is_csv = raw_rows(folder)
    ab = addbacks or {}
    return src, [year_record(r, is_csv, ab.get(r.get("period_end"))) for r in raw]


# ---------------------------------------------------------------------------
# Acquired IPR&D inside the window (engine 5.6's iprd_adjustment; lane default Q3 (b))
# ---------------------------------------------------------------------------
def iprd_in_window(n, rows):
    """[{period, amount, pct_of_operating_income, treatment, addback}] for each fiscal year of the window whose
    engine-recorded acquired-IPR&D charge is positive (treatment not none), and the {period_end: amount} add-backs
    (treatment one_time_value_deduction and not recurrent, ADDBACK_IPRD on)."""
    blk = n.get("iprd_adjustment") if isinstance(n, dict) else None
    if not isinstance(blk, dict) or blk.get("treatment") in (None, "none"):
        return [], {}
    one_time = blk.get("treatment") == getattr(_engine, "IPRD_TREATMENT_ONE_TIME", "one_time_value_deduction")
    recurrent = bool(blk.get("recurrent"))
    ends = {r.get("period_end"): r for r in rows}
    out, add = [], {}
    for p in blk.get("periods") or []:
        if not isinstance(p, dict) or p.get("window") not in (None, "fy") or p.get("excluded"):
            continue
        end = p.get("period")
        amt = _fnum(p.get("deducted"))
        if amt is None:
            amt = _fnum(p.get("amount"))
        if amt is None:
            amt = _fnum(p.get("expense"))
        if not amt or amt <= 0 or end not in ends:
            continue
        if p.get("fx_rate") is not None:   # the block is in USD; a converted charge does not meet the filed-unit rows
            amt_native = _fnum(p.get("expense"))
            if amt_native is None:
                continue
            amt = amt_native
        oi = ends[end].get("ebit")
        do_add = bool(ADDBACK_IPRD and one_time and not recurrent)
        out.append({"period": end, "amount": round(amt, 2),
                    "pct_of_operating_income": _r(amt / oi) if (oi and oi > 0) else None,
                    "treatment": blk.get("treatment"), "recurrent": recurrent, "addback": do_add})
        if do_add:
            add[end] = amt
    return out, add


# ---------------------------------------------------------------------------
# Business type: the SIC lock (07 §1.4 + the SIC-6798 mortgage-REIT rule) and the legacy hint
# ---------------------------------------------------------------------------
def type_lock(sic, last_row):
    """(allowed set or None, rule text or None, sic_class) — 07 §1.4 from dcf_engine.sic_misfit_class: bank / credit /
    insurance_carrier -> {financial_balance_sheet}; utility / real_estate_lessor -> {real_assets}; reit -> locked to
    {financial_balance_sheet} on a mortgage-REIT balance sheet (03b §3.1: loans + debt securities > 50% of assets, the
    bank revenue basis, or liabilities >= 75% of assets with no operating-income tag), else {real_assets,
    financial_balance_sheet}; broker_dealer / None -> unlocked."""
    cls = _engine.sic_misfit_class(sic) if sic not in (None, "") else None
    if cls in ("bank", "credit", "insurance_carrier"):
        return {"financial_balance_sheet"}, None, cls
    if cls in ("utility", "real_estate_lessor"):
        return {"real_assets"}, None, cls
    if cls == "reit":
        lr = last_row or {}
        fy = str(lr.get("fy") or (lr.get("period_end") or "")[:4])
        fa = _fnum(lr.get("financial_assets_pct_assets"))
        if fa is not None and fa > REIT_LOCK["financial_assets_share"]:
            return {"financial_balance_sheet"}, f"loans and debt securities {_pct(fa)} of assets (FY{fy})", cls
        if lr.get("revenue_basis") in REIT_LOCK["bank_revenue_bases"]:
            return {"financial_balance_sheet"}, f"bank revenue basis {lr.get('revenue_basis')} (FY{fy})", cls
        liab, assets = _fnum(lr.get("liabilities")), _fnum(lr.get("assets"))
        if liab is not None and assets and assets > 0 and liab / assets >= REIT_LOCK["liabilities_share"] \
                and _fnum(lr.get("operating_income")) is None:
            return ({"financial_balance_sheet"},
                    f"liabilities {_pct(liab / assets)} of assets and no operating-income tag (FY{fy})", cls)
        return {"real_assets", "financial_balance_sheet"}, None, cls
    return None, None, cls


def sic_hint(sic, flags, allowed, cls):
    """(hint type or None, basis) for output with no declared type: a single locked type -> sic_lock; an unlocked REIT
    -> real_assets (sic_hint); SIC 6200-6299 except 6211, and 6411 -> financial_fee (sic_hint); with no SIC the
    SECTOR_MODEL_MISMATCH flag (Finance -> financial_balance_sheet; Real Estate / Utilities -> real_assets); else None."""
    if allowed and len(allowed) == 1:
        return next(iter(allowed)), "sic_lock"
    if cls == "reit":
        return "real_assets", "sic_hint"
    try:
        s = int(str(sic).strip())
    except (TypeError, ValueError):
        s = None
    if s is not None and ((6200 <= s <= 6299 and s != 6211) or s == 6411):
        return "financial_fee", "sic_hint"
    if s is None:
        for f in flags or ():
            f = str(f)
            if f.startswith("SECTOR_MODEL_MISMATCH"):
                if "Finance" in f:
                    return "financial_balance_sheet", "sector_flag"
                if "Real Estate" in f or "Utilities" in f:
                    return "real_assets", "sector_flag"
    return None, "default"


def ladder_family(btype):
    return LADDER_FAMILY.get(btype, "default")


# ---------------------------------------------------------------------------
# Mechanical pillars
# ---------------------------------------------------------------------------
def governing(btype, rows):
    """(measure, ladder, reason): ROE at a financial_balance_sheet; tangible ROIC when the median of (goodwill +
    intangibles) / invested capital over the window's years with positive invested capital exceeds 30%; else ROIC."""
    if btype == "financial_balance_sheet":
        return "roe", "roe", "balance-sheet financial: ROE governs (ladder 15 / 12 / 9 / 6%)"
    lad = ladder_family(btype)
    shares = [r["intangibles_share_ic"] for r in rows if r.get("intangibles_share_ic") is not None]
    if not shares:
        return "roic", lad, "invested capital not positive in any year of the window: ROIC governs"
    m = _median(shares)
    if m > INTANGIBLE_SHARE_GOVERNS:
        return "roic_tangible", lad, f"goodwill + intangibles median {_pct(m)} of invested capital (> 30%): tangible ROIC governs"
    return "roic", lad, f"goodwill + intangibles median {_pct(m)} of invested capital (<= 30%): ROIC governs"


def year_value(r, measure):
    if measure == "roe":
        return r.get("roe")
    return _value(r.get(measure), r.get(measure + "_note"))


def _neg_note(rows, measure):
    notes = [r.get(measure + "_note") for r in rows]
    return "loss_on_unstable_capital" if ("loss_on_unstable_capital" in notes and "loss_on_nonpositive_capital" not in notes) \
        else "loss_on_nonpositive_capital"


def pillar_returns_on_capital(btype, src, rows):
    measure, lad, reason = governing(btype, rows)
    t = LADDERS[lad]
    series = []
    for r in rows:
        e = {"fy": r.get("fy"), "roic": _r(r.get("roic")), "roic_note": r.get("roic_note"),
             "roic_tangible": _r(r.get("roic_tangible")), "roic_tangible_note": r.get("roic_tangible_note"),
             "roe": _r(r.get("roe")), "roe_note": r.get("roe_note"), "roa": _r(r.get("roa")),
             "intangibles_share_ic": _r(r.get("intangibles_share_ic")), "roic_basis": r.get("roic_basis"),
             "flags": list(r.get("roic_flags") or [])}
        if r.get("iprd_addback"):
            e["iprd_addback"] = round(r["iprd_addback"], 2)
        series.append(e)
    medians = {}
    for k in ("roic", "roic_tangible", "roe", "roa"):
        vv = [v for v in (year_value(r, k) if k != "roa" else r.get("roa") for r in rows) if v is not None]
        if len(vv) >= 3:
            m, note = _med_record(vv, _neg_note(rows, k) if k.startswith("roic") else "loss_on_nonpositive_capital")
        else:
            m, note = None, None
        medians[k] = m
        if k in ("roic", "roic_tangible", "roe"):
            medians[k + "_note"] = note
    roa_m = medians["roa"]
    base = {"source": "mechanical", "weight": WEIGHTS["returns_on_capital"], "range": list(RANGES["returns_on_capital"]),
            "metric": measure, "ladder": lad, "governing_reason": reason,
            "basis": f"{src} annual rows (fundamentals.capital_returns_from_row)", "series": series, "medians": medians,
            "roa_cross_check": {"median": roa_m, "line": ROA_LINE, "applies": btype != "financial_balance_sheet"},
            "thresholds": list(t)}
    vals = [v for v in (year_value(r, measure) for r in rows) if v is not None]
    if len(vals) < 3:
        return dict(base, status="insufficient_data", score=None, median=None, median_note=None, min=None,
                    sustained_plus2=False, plain_roic_check=None,
                    reason=f"{len(vals)} valid year(s) of {measure} in the last {len(rows)} fiscal year(s); at least 3 needed")
    med = _median(vals)
    s = _ladder(med, t)
    if s == 2 and min(vals) < t[2]:
        s = 1                                   # cycle floor: +2 needs every valid year at or above the 0-band floor
    plain = None
    if measure == "roic_tangible":
        pv = [v for v in (year_value(r, "roic") for r in rows) if v is not None]
        pm = _median(pv) if len(pv) >= 3 else None
        capped = s == 2 and not (pm is not None and pm >= TANGIBLE_PLUS2_PLAIN_LINE)
        pmj, pmn = _med_record(pv, _neg_note(rows, "roic")) if len(pv) >= 3 else (None, None)
        plain = {"median": pmj, "median_note": pmn, "line": TANGIBLE_PLUS2_PLAIN_LINE, "applies": True, "capped": capped}
        if capped:
            s = 1                               # 03c decision 2: an overpaying acquirer does not max the pillar
    sustained = s == 2 and all(v >= t[1] for v in vals)
    mj, mn = _med_record(vals, _neg_note(rows, measure) if measure != "roe" else "loss_on_nonpositive_capital")
    mn_v = min(vals)
    pv = [v for v in (year_value(r, "roic") for r in rows) if v is not None]
    # (the underscore keys are working values for the gates and the industry rank; evaluate strips them)
    return dict(base, status="measured", score=s, median=mj, median_note=mn,
                min=_r(mn_v) if math.isfinite(mn_v) else None, sustained_plus2=sustained, plain_roic_check=plain,
                _median_value=med, _values=vals, _plain_median=_median(pv) if len(pv) >= 3 else None)


def window_rows(folder, n=None):
    """(source, rows, iprd_in_window list): the scorecard's last-5-FY rows with the acquired-IPR&D add-backs applied."""
    src, raw, is_csv = raw_rows(folder)
    rows = [year_record(r, is_csv) for r in raw]
    iprd, add = iprd_in_window(n or {}, rows)
    if add:
        rows = [year_record(r, is_csv, add.get(r.get("period_end"))) for r in raw]
    return src, rows, iprd


def governing_return(folder, btype, n=None):
    """{measure, ladder, median, median_note, years, value} — the folder's governing 5-FY median (industry_returns.py
    reads the same function make_score scores with; `value` is the float incl. +-inf, or None when unmeasured)."""
    src, rows, _ = window_rows(folder, n)
    roc = pillar_returns_on_capital(btype, src, rows)
    return {"measure": roc["metric"], "ladder": roc["ladder"], "median": roc["median"], "median_note": roc["median_note"],
            "years": len([1 for r in rows if year_value(r, roc["metric"]) is not None]),
            "value": roc.get("_median_value") if roc["status"] == "measured" else None}


def pillar_capital_intensity(btype, folder):
    """capex / OCF median over the last 5 CSV years (the engine's capex, overrides included); a year with capex
    assumed zero is excluded, OCF <= 0 counts +inf; <= 15% +2, <= 30% +1, <= 50% 0, <= 80% -1, else -2."""
    w = {"source": "mechanical", "weight": WEIGHTS["capital_intensity"], "range": list(RANGES["capital_intensity"])}
    if (btype, "capital_intensity") in MECH_NA:
        return dict(w, status="not_applicable", score=None, reason=MECH_NA[(btype, "capital_intensity")])
    rows = _csv_raw(folder)[-5:]
    series, vals, revr = [], [], []
    for r in rows:
        if r["ocf"] is None or r["capex"] is None or r["capex_assumed_zero"]:
            series.append({"fy": r["fy"], "value": None,
                           "note": "capex not filed (assumed zero)" if r["capex_assumed_zero"] else "ocf or capex missing"})
            continue
        if r["ocf"] <= 0:
            vals.append(math.inf)
            series.append({"fy": r["fy"], "value": None, "note": "ocf <= 0"})
        else:
            v = r["capex"] / r["ocf"]
            vals.append(v)
            series.append({"fy": r["fy"], "value": _r(v), "note": None})
        if r["revenue"] and r["revenue"] > 0:
            revr.append(r["capex"] / r["revenue"])
    base = dict(w, metric="capex_to_ocf", basis="financials_history.csv: capex / ocf (engine capex, overrides included)",
                series=series)
    if len(vals) < 3:
        return dict(base, status="insufficient_data", score=None, median=None, median_note=None,
                    reason=f"{len(vals)} valid year(s); at least 3 needed")
    med = _median(vals)
    s = 2 if med <= 0.15 else 1 if med <= 0.30 else 0 if med <= 0.50 else -1 if med <= 0.80 else -2
    return dict(base, status="measured", score=s, median=_r(med), median_note=("ocf_nonpositive" if med == math.inf else None),
                capex_to_revenue_median=_r(_median(revr)) if revr else None)


def pillar_scale_economics(btype, src, rows):
    """Operating margin (EBIT / revenue, the IPR&D add-back included) first-2 vs last-2 years against the revenue CAGR;
    a year with margin > 100% is excluded (bad revenue tag), margins clamped at -100%; >= 4 valid years."""
    w = {"source": "mechanical", "weight": WEIGHTS["scale_economics"], "range": list(RANGES["scale_economics"])}
    if (btype, "scale_economics") in MECH_NA:
        return dict(w, status="not_applicable", score=None, reason=MECH_NA[(btype, "scale_economics")])
    v, series = [], []
    for r in rows:
        rev, ebit = r.get("revenue"), r.get("ebit")
        if not (rev and rev > 0) or ebit is None:
            series.append({"fy": r.get("fy"), "margin": None, "note": "no revenue or operating income"})
            continue
        m = ebit / rev
        if m > 1.0:
            series.append({"fy": r.get("fy"), "margin": None, "note": "operating income above revenue (bad revenue tag)"})
            continue
        m = max(-1.0, m)
        v.append((r.get("fy") or "", rev, m))
        e = {"fy": r.get("fy"), "margin": _r(m), "revenue": rev,
             "note": None if r.get("roic_basis") == "operating_income" else r.get("roic_basis")}
        if r.get("iprd_addback"):
            e["iprd_addback"] = round(r["iprd_addback"], 2)
        series.append(e)
    base = dict(w, metric="operating_margin_vs_revenue_growth", basis=f"{src}: operating income / revenue", series=series)
    if len(v) < 4:
        return dict(base, status="insufficient_data", score=None, reason=f"{len(v)} valid year(s); at least 4 needed")
    first, last = (v[0][2] + v[1][2]) / 2, (v[-1][2] + v[-2][2]) / 2
    dm = last - first
    y0, y1 = str(v[0][0])[:4], str(v[-1][0])[:4]
    yrs = int(y1) - int(y0) if (y0.isdigit() and y1.isdigit()) else len(v) - 1
    cagr = (v[-1][1] / v[0][1]) ** (1 / max(1, yrs)) - 1
    if cagr >= 0.03:
        s = 2 if dm >= 0.03 else 1 if dm >= 0.01 else 0 if dm > -0.01 else -1 if dm > -0.05 else -2
    else:
        s = 1 if dm >= 0.03 else 0 if dm > -0.01 else -1 if dm > -0.05 else -2
    return dict(base, status="measured", score=s, revenue_cagr=_r(cagr), margin_first2=_r(first), margin_last2=_r(last),
                margin_change_pp=round(dm * 100, 2))


def load_industry(sys_dir):
    """<sys_dir>/industry_returns.json with its build date and sha256 (make_score passes SYS_DIR = $STOCKS_BASE/_system,
    the DATA base), or None when absent / unreadable."""
    path = os.path.join(sys_dir, INDUSTRY_FILE)
    try:
        with open(path, "rb") as f:
            raw = f.read()
        doc = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(doc, dict):
        return None
    return dict(doc, _sha256=hashlib.sha256(raw).hexdigest())


def _peer_value(m):
    if not isinstance(m, dict):
        return None
    v = _fnum(m.get("median"))
    if v is not None:
        return v
    return _value(None, m.get("median_note"))


def pillar_industry_structure(btype, ticker, sic, roc, industry, cik=None):
    """Same-ladder SIC peers' governing medians (leave-one-out by CIK; 03c decision 13 option (b): peers whose median is
    -inf are dropped and counted) -> median -> the company's ladder (no cycle floor). The group is the first level
    4 -> 3 -> 2 with >= 5 peers; else insufficient_data (weight 0)."""
    lad = ladder_family(btype)
    t = LADDERS[lad]
    w = {"source": "mechanical", "weight": WEIGHTS["industry_structure"], "range": list(RANGES["industry_structure"]),
         "ladder": lad, "thresholds": list(t)}
    sic_s = str(sic).strip() if sic not in (None, "") else ""
    if industry is None:
        return dict(w, status="insufficient_data", score=None, sic=sic_s or None,
                    reason=f"_system/{INDUSTRY_FILE} missing or unreadable")
    fb = {"file_built": industry.get("built"), "file_sha256": industry.get("_sha256")}
    if not sic_s.isdigit():
        return dict(w, **fb, status="insufficient_data", score=None, sic=None, reason="no SIC on record")
    members = industry.get("members") if isinstance(industry.get("members"), dict) else {}
    groups = industry.get("groups") if isinstance(industry.get("groups"), dict) else {}
    own_cik = str(cik) if cik not in (None, "") else None
    own_val = roc.get("_median_value") if roc.get("status") == "measured" else None
    for lvl in INDUSTRY_LEVELS:
        code = sic_s[:lvl]
        g = groups.get(f"{lad}|{lvl}:{code}")
        if not isinstance(g, dict):
            continue
        peers, dropped, mix = [], 0, {}
        for tk in g.get("members") or []:
            m = members.get(tk)
            if not isinstance(m, dict) or tk == ticker or (own_cik and str(m.get("cik") or "") == own_cik):
                continue
            v = _peer_value(m)
            if v is None:
                continue
            if v == -math.inf:
                dropped += 1
                continue
            peers.append((tk, v))
            mix[m.get("measure")] = mix.get(m.get("measure"), 0) + 1
        if len(peers) < INDUSTRY_MIN_PEERS:
            continue
        med = _median([v for _, v in peers])
        rank = (1 + sum(1 for _, v in peers if v > own_val)) if own_val is not None else None
        mj, mn = (None, NOTE_INF) if med == math.inf else (_r(med), None)
        return dict(w, **fb, status="measured", sic=sic_s, group=f"{lvl}:{code}", level=lvl, label=g.get("label"),
                    peers=len(peers), peers_dropped=dropped, median=mj, median_note=mn,
                    metric_mix={k: mix[k] for k in sorted(mix, key=str)}, rank=rank, of=len(peers) + 1,
                    score=_ladder(med, t))
    return dict(w, **fb, status="insufficient_data", score=None, sic=sic_s,
                reason=f"fewer than {INDUSTRY_MIN_PEERS} same-ladder peers ({lad}) at SIC 2-digit {sic_s[:2]}")


def erosion_test(roc, rows, src=None):
    """MOAT_EROSION (03b §3.5; 03c decision 3): the governing measure's finite yearly values (>= 4, both of the last two
    finite) and a margin series (>= 4): gross margin, else operating margin (EBIT / revenue, the IPR&D add-back
    included) — the operating fallback on fundamentals.json rows only (10b COVERAGE, lane default Q4: a CSV-only folder
    is never measured). Returns down: OLS slope < 0 AND the last-2 minus first-2 average <= -3pp AND <= -20% of the
    first-2 average; margin down: slope < 0 AND change <= -2pp. Fired = both. The return shape is kept stable for the
    fade lane (L3b) to wrap."""
    out = {"status": "not_measured", "fired": False, "governing_change_pp": None, "margin_change_pp": None,
           "margin_basis": None, "slope_governing": None, "slope_margin": None, "reason": None}
    if src != "fundamentals.json":
        return dict(out, reason="no fundamentals.json annual rows (a CSV-only folder has no gross-margin line)")
    measure = roc.get("metric")
    g = [year_value(r, measure) for r in rows]
    gf = [v for v in g if v is not None and math.isfinite(v)]
    if len(gf) < 4 or any(v is None or not math.isfinite(v) for v in g[-2:]):
        return dict(out, reason="fewer than 4 finite years of the governing return, or one of the last two not finite")
    gm = [r.get("gross_margin") for r in rows if r.get("gross_margin") is not None]
    basis = "gross"
    if len(gm) < 4:
        # the filed operating margin (operating income / revenue; the IPR&D add-back included) — not the pretax EBIT
        # fallback: a filer with no operating-income line has no operating margin to trend
        gm = [r["ebit"] / r["revenue"] for r in rows if r.get("roic_basis") == "operating_income" and r.get("ebit") is not None
              and r.get("revenue") and r["revenue"] > 0]
        basis = "operating"
    if len(gm) < 4:
        return dict(out, reason="fewer than 4 years of gross or operating margin")
    dg = (gf[-1] + gf[-2]) / 2 - (gf[0] + gf[1]) / 2
    dm = (gm[-1] + gm[-2]) / 2 - (gm[0] + gm[1]) / 2
    start = abs((gf[0] + gf[1]) / 2)
    sg, sm = _slope(gf), _slope(gm)
    ret_down = sg < 0 and dg <= -EROSION_T[0] and dg <= -EROSION_T[1] * start
    mar_down = sm < 0 and dm <= -EROSION_T[2]
    return dict(out, status="measured", fired=bool(ret_down and mar_down), governing_change_pp=round(dg * 100, 2),
                margin_change_pp=round(dm * 100, 2), margin_basis=basis, slope_governing=_r(sg, 6), slope_margin=_r(sm, 6),
                governing_first2=_r((gf[0] + gf[1]) / 2), governing_last2=_r((gf[-1] + gf[-2]) / 2))


# ---------------------------------------------------------------------------
# Facts (facts.json, 02's schema; validated by the facts lane, re-read here for what the moat rules need)
# ---------------------------------------------------------------------------
def _ctx(folder, n, facts):
    return {"facts": facts or {}, "calendar": _facts.fiscal_calendar(folder), "lpe": (n or {}).get("latest_period_end")}


def _fact_end(f, ctx):
    return _facts.period_end(f, ctx["calendar"], ctx["lpe"])


def check_fact_ids(where, fids, ctx, tag, types=PILLAR_FACT_TYPES):
    """The cited ids: distinct strings, declared in facts.json, each listing `tag` in used_for; a pillar or factor cites
    only actual / metric / event facts with a point value (07 §1.6)."""
    if not isinstance(fids, list) or not all(isinstance(x, str) for x in fids) or len(set(fids)) != len(fids):
        raise MoatRefusal(f"{where}.facts must be a list of distinct facts.json ids")
    missing = [x for x in fids if x not in ctx["facts"]]
    if missing:
        raise MoatRefusal(f"{where} cites {', '.join(missing)}, which facts.json does not declare")
    for x in fids:
        f = ctx["facts"][x]
        uf = f.get("used_for") if isinstance(f.get("used_for"), list) else []
        if tag not in uf:
            raise MoatRefusal(f"{where} cites {x}, but {x} does not list used_for {tag}")
        if types is not None and f.get("type") not in types:
            raise MoatRefusal(f"{where} cites {x} of type {f.get('type')!r}: a moat pillar cites only actual, metric or "
                              "event facts (guidance and estimates calibrate scenarios, not the moat)")
        if types is not None and isinstance(f.get("value"), list):
            raise MoatRefusal(f"{where} cites {x}, a range value: a moat pillar cites point values only")
    return fids


def _series_ends(fids, ctx, metric_filter=None):
    """metric -> sorted distinct period ends among the cited non-event facts (metric_filter: a set of metric names)."""
    out = {}
    for x in fids:
        f = ctx["facts"][x]
        if f.get("type") in POINT_FACT_TYPES:
            continue
        m = f.get("metric")
        if metric_filter is not None and m not in metric_filter:
            continue
        pe = _fact_end(f, ctx)
        if m and pe:
            out.setdefault(m, set()).add(pe)
    return {m: sorted(p) for m, p in out.items()}


def _is_series(ends, min_periods=SERIES_MIN_PERIODS, min_days=SERIES_MIN_SPAN_DAYS):
    if len(ends) < min_periods:
        return False
    return (datetime.date.fromisoformat(ends[-1]) - datetime.date.fromisoformat(ends[0])).days >= min_days


def check_series(where, fids, ctx):
    """R4: every cited metric is a SERIES (>= 3 distinct period ends spanning >= 360 days among the cited facts of the
    same metric); event facts are points. Returns (number of series, point fact ids, third-party only)."""
    sm = _series_ends(fids, ctx)
    not_series, points = [], []
    for x in fids:
        f = ctx["facts"][x]
        if f.get("type") in POINT_FACT_TYPES:
            points.append(x)
            continue
        per = sm.get(f.get("metric")) or []
        if not _is_series(per):
            not_series.append(f"{x} ({f.get('metric') or 'no metric'}: {len(per)} period(s))")
    if not_series:
        raise MoatRefusal(f"{where}: every cited metric must be a series of >= {SERIES_MIN_PERIODS} distinct periods spanning "
                          f">= 12 months among the cited facts — not a series: {', '.join(not_series)}")
    tp = bool(fids) and all(ctx["facts"][x].get("kind") == "third_party" for x in fids)
    return sum(1 for per in sm.values() if _is_series(per)), points, tp


def _is_growth_rate(f):
    calc = f.get("calc") if isinstance(f.get("calc"), dict) else {}
    return str(f.get("metric") or "").endswith("_growth") or calc.get("op") in ("growth", "cagr")


def _score_of(p, lo, hi, where, extra=""):
    s = p.get("score")
    if isinstance(s, bool) or not isinstance(s, int):
        raise MoatRefusal(f"{where}.score must be an integer {lo:+d}..{hi:+d} (got {s!r})")
    if not lo <= s <= hi:
        raise MoatRefusal(f"{where} score {s} is outside {lo:+d}..{hi:+d}{extra}")
    return s


# ---------------------------------------------------------------------------
# Declared core pillars and the supporting factors
# ---------------------------------------------------------------------------
def check_declared(name, p, btype, ctx, strict=True):
    where = f"moat_scorecard.pillars.{name}"
    lo, hi = RANGES[name]
    base = {"source": "declared", "weight": WEIGHTS[name], "range": [lo, hi]}
    if not isinstance(p, dict):
        raise MoatRefusal(f"{where} must be an object")
    allowed = DECLARED_PILLAR_KEYS + (("threats",) if name == "erosion_risks" else ())
    unknown = sorted(set(p) - set(allowed))
    if unknown:
        raise MoatRefusal(f"{where} has unknown key(s) {unknown} (allowed: {', '.join(allowed)})")
    if p.get("applicable", True) is False:
        na = NA_ALLOWED.get(btype, set())
        if name not in na:
            raise MoatRefusal(f"{where} cannot be not applicable for business type {btype} "
                              f"(allowed: {sorted(na) or 'none'}) — score it from the type's equivalent metric")
        if not str(p.get("not_applicable_reason") or "").strip():
            raise MoatRefusal(f"{where}: applicable false needs a not_applicable_reason")
        return dict(base, status="not_applicable", score=None, reason=str(p["not_applicable_reason"]).strip())
    if "applicable" in p and p["applicable"] is not True:
        raise MoatRefusal(f"{where}.applicable must be true or false")
    s = _score_of(p, lo, hi, where)
    if not str(p.get("rationale") or "").strip():
        raise MoatRefusal(f"{where}: a scored pillar needs a rationale")
    fids = check_fact_ids(where, p.get("facts", []), ctx, f"moat:{name}")
    threats = p.get("threats")
    if threats is not None and not isinstance(threats, list):
        raise MoatRefusal(f"{where}.threats must be a list of {{type, facts}}")
    th_out = []
    if name == "erosion_risks":
        seen = set()
        for i, t in enumerate(threats or []):
            if not isinstance(t, dict) or set(t) - {"type", "facts"}:
                raise MoatRefusal(f"{where}.threats[{i}] must be {{type, facts}}")
            if t.get("type") not in EROSION_THREATS:
                raise MoatRefusal(f"{where}.threats[{i}]: type {t.get('type')!r} is not one of {', '.join(EROSION_THREATS)}")
            if t["type"] in seen:
                raise MoatRefusal(f"{where}.threats: {t['type']} is listed twice")
            seen.add(t["type"])
            tf = t.get("facts")
            if not isinstance(tf, list) or not tf or not all(isinstance(x, str) for x in tf):
                raise MoatRefusal(f"{where}.threats[{i}] ({t['type']}) needs at least one fact")
            outside = [x for x in tf if x not in fids]
            if outside:
                raise MoatRefusal(f"{where}.threats[{i}] ({t['type']}) cites {', '.join(outside)}, which the pillar's facts do not list")
            th_out.append({"type": t["type"], "facts": list(tf)})
        if s < 0 and not th_out:
            raise MoatRefusal(f"{where} scores {s:+d} with no threats — a negative erosion score names its threats "
                              f"({', '.join(EROSION_THREATS)})")
    if not fids:
        if s != 0:
            raise MoatRefusal(f"{where} scores {s:+d} with no facts — a non-zero pillar cites facts.json ids")
        return dict(base, status="unsupported_neutral", score=0, facts=[], weight_counted=False,
                    rationale=str(p["rationale"]).strip(), **({"threats": th_out} if name == "erosion_risks" else {}))
    n_series, points, tp = check_series(where, fids, ctx)
    if s != 0 and n_series == 0 and name not in POINT_OK_PILLARS:
        raise MoatRefusal(f"{where} scores {s:+d} on point facts only ({', '.join(points)}) — cite at least one metric "
                          f"series (point facts may stand alone only on {', '.join(sorted(POINT_OK_PILLARS))})")
    if tp and abs(s) > THIRD_PARTY_CAP:
        raise MoatRefusal(f"{where} scores {s:+d} on third-party facts only ({', '.join(fids)}) — third-party-only pillars "
                          f"are capped at |score| <= {THIRD_PARTY_CAP}")
    out = dict(base, status="scored", score=s, facts=list(fids), third_party_only=tp, rationale=str(p["rationale"]).strip(),
               weight_counted=True)
    if name == "erosion_risks":
        out["threats"] = th_out
    if name == "reach_and_growth":
        gro = all(_is_growth_rate(ctx["facts"][x]) for x in fids)
        out["growth_rate_facts_only"] = gro
        if strict and s == 2 and gro:
            raise MoatRefusal(f"{where} +2 cites growth rates only ({', '.join(fids)}): a growth rate belongs in the growth "
                              "start (one lever per question); +2 needs a scale or retention fact (users, customers, share "
                              "of the served market, cohort retention)")
    return out


def check_supporting(sup, ctx):
    """M1b: the four supporting factors, each scored with facts or declared not applicable; their sum / 4 (a scored 0
    counts, N/A is 0 too), clamped to +-1, is the supporting adjustment (03c decision 11)."""
    where = "moat_scorecard.supporting"
    if not isinstance(sup, dict):
        raise MoatRefusal(f"{where} must be an object with {', '.join(SUPPORTING)}")
    unknown = sorted(set(sup) - set(SUPPORTING))
    if unknown:
        raise MoatRefusal(f"{where} has unknown key(s) {unknown} (the factors are {', '.join(SUPPORTING)}; there is no "
                          "`supports` field)")
    out, total, applicable = {}, 0, 0
    for k in SUPPORTING:
        w = f"{where}.{k}"
        p = sup.get(k)
        lo, hi = SUPPORTING_RANGES[k]
        base = {"source": "declared", "range": [lo, hi]}
        if p is None:
            raise MoatRefusal(f"{w} is missing — score it with facts or declare applicable: false with not_applicable_reason")
        if not isinstance(p, dict):
            raise MoatRefusal(f"{w} must be an object")
        unk = sorted(set(p) - set(DECLARED_PILLAR_KEYS))
        if unk:
            raise MoatRefusal(f"{w} has unknown key(s) {unk} (allowed: {', '.join(DECLARED_PILLAR_KEYS)})")
        if p.get("applicable", True) is False:
            if not str(p.get("not_applicable_reason") or "").strip():
                raise MoatRefusal(f"{w}: applicable false needs a not_applicable_reason")
            out[k] = dict(base, status="not_applicable", score=None, reason=str(p["not_applicable_reason"]).strip())
            continue
        if "applicable" in p and p["applicable"] is not True:
            raise MoatRefusal(f"{w}.applicable must be true or false")
        s = _score_of(p, lo, hi, w, " (-2 is reserved for value-destroying reinvestment outside the moat)" if k == "management" else "")
        if not str(p.get("rationale") or "").strip():
            raise MoatRefusal(f"{w}: a scored factor needs a rationale")
        fids = check_fact_ids(w, p.get("facts", []), ctx, f"moat:{k}")
        applicable += 1
        total += s
        if not fids:
            if s != 0:
                raise MoatRefusal(f"{w} scores {s:+d} with no facts — a non-zero factor cites facts.json ids")
            out[k] = dict(base, status="unsupported_neutral", score=0, facts=[], third_party_only=False,
                          rationale=str(p["rationale"]).strip())
            continue
        n_series, points, tp = check_series(w, fids, ctx)
        if s != 0 and n_series == 0 and k not in POINT_OK_PILLARS:
            raise MoatRefusal(f"{w} scores {s:+d} on point facts only ({', '.join(points)}) — event facts may stand alone "
                              "only on execution and management")
        if tp and abs(s) > THIRD_PARTY_CAP:
            raise MoatRefusal(f"{w} {s:+d} rests on third-party facts only ({', '.join(fids)}): third-party-only support caps "
                              f"a score at +-{THIRD_PARTY_CAP}")
        out[k] = dict(base, status="scored", score=s, facts=list(fids), third_party_only=tp, rationale=str(p["rationale"]).strip())
    adj = round(max(-SUPPORTING_CAP, min(SUPPORTING_CAP, total / SUPPORTING_DIVISOR)), 2)
    out.update({"sum": total, "divisor": SUPPORTING_DIVISOR, "cap": SUPPORTING_CAP, "adjustment": adj})
    return out, ("scored" if applicable else "none_applicable")


# ---------------------------------------------------------------------------
# Volume x price (users x revenue per user and its equivalents; 03 §6 with 02's pct fractions)
# ---------------------------------------------------------------------------
VOLUME_PRICE_KEYS = ("mode", "volume_facts", "volume_basis", "revenue", "revenue_facts", "price_facts", "inflation_hurdle_fact")


def classify(u, a, h=INFLATION_HURDLE):
    if a >= h and u >= -FLAT:
        return "pricing_power"
    if a > 0 and u < -FLAT:
        return "harvesting"
    if a < 0 and u > FLAT:
        return "buying_growth"
    if a <= 0 and u <= FLAT:
        return "declining"
    return "mixed"


def bounds(cls, u, a, h=INFLATION_HURDLE):
    pp_max = 2 if a >= h else 1 if a > 0 else 0
    pp_min = 1 if cls == "pricing_power" else -2
    rg_max = 2 if u >= 0.08 else 1 if u >= 0.02 else 0 if u >= -FLAT else -1
    pair_max = {"harvesting": -1, "buying_growth": 0, "declining": -2}.get(cls)
    return {"pricing_power": [pp_min, pp_max], "reach_and_growth": [-2, rg_max], "pair_max": pair_max}


def volume_price(vp, rows, ctx):
    where = "moat_scorecard.volume_price"
    if not isinstance(vp, dict):
        raise MoatRefusal(f"{where} must be an object")
    unknown = sorted(set(vp) - set(VOLUME_PRICE_KEYS))
    if unknown:
        raise MoatRefusal(f"{where} has unknown key(s) {unknown}")
    mode = vp.get("mode", "levels")
    if mode not in ("levels", "growth_rates"):
        raise MoatRefusal(f"{where}.mode must be levels or growth_rates")
    facts = ctx["facts"]
    vf = vp.get("volume_facts") or []
    ids = list(vf) + list(vp.get("revenue_facts") or []) + list(vp.get("price_facts") or [])
    for x in ids:
        if x not in facts:
            raise MoatRefusal(f"{where} cites {x}, which facts.json does not declare")
    if len({facts[x].get("metric") for x in vf}) != 1:
        raise MoatRefusal(f"{where}.volume_facts must share one metric")
    pts = sorted((_fact_end(facts[x], ctx), _fnum(facts[x].get("value"))) for x in vf)
    if any(p is None or v is None for p, v in pts) or len({p for p, _ in pts}) != len(pts):
        raise MoatRefusal(f"{where}.volume_facts need distinct periods and numeric values")
    hurdle, hbasis = INFLATION_HURDLE, "default 3.00%/yr"
    if vp.get("inflation_hurdle_fact"):
        hf = facts.get(vp["inflation_hurdle_fact"])
        if not hf or _fnum(hf.get("value")) is None or hf.get("unit") != "pct":
            raise MoatRefusal(f"{where}.inflation_hurdle_fact must be a pct fact id")
        hurdle, hbasis = _fnum(hf["value"]), f"fact {vp['inflation_hurdle_fact']}"
    if mode == "levels":
        if vp.get("revenue_facts"):
            revs = {_fact_end(facts[x], ctx): _fnum(facts[x].get("value")) for x in vp["revenue_facts"]}
            rsrc = "declared revenue facts"
            aligned = [(p, v, revs.get(p)) for p, v in pts if revs.get(p)]
        else:
            rsrc = "total revenue (annual rows)"
            rv = [(datetime.date.fromisoformat(r["period_end"]), r["revenue"]) for r in rows
                  if r.get("period_end") and r.get("revenue")]
            aligned = []
            for p, v in pts:
                d = datetime.date.fromisoformat(p)
                m = [rr for dd, rr in rv if abs((dd - d).days) <= 10]
                if m:
                    aligned.append((p, v, m[0]))
        if len(aligned) < SERIES_MIN_PERIODS or any(v <= 0 or r <= 0 for _, v, r in aligned):
            raise MoatRefusal(f"{where}: {len(aligned)} volume period(s) align with a fiscal-year revenue (period end within "
                              f"10 days); at least {SERIES_MIN_PERIODS} positive values needed")
        p0, pn = aligned[0][0], aligned[-1][0]
        yrs = max(1, round((datetime.date.fromisoformat(pn) - datetime.date.fromisoformat(p0)).days / 365.25))
        u = (aligned[-1][1] / aligned[0][1]) ** (1 / yrs) - 1
        rg = (aligned[-1][2] / aligned[0][2]) ** (1 / yrs) - 1
        a = (1 + rg) / (1 + u) - 1
        detail = [{"period_end": p, "volume": v, "revenue": r, "revenue_per_unit": round(r / v, 4)} for p, v, r in aligned]
    else:
        pf = sorted((_fact_end(facts[x], ctx), _fnum(facts[x].get("value"))) for x in (vp.get("price_facts") or []))
        vols = {_fact_end(facts[x], ctx): _fnum(facts[x].get("value")) for x in vf}
        aligned = [(p, vols[p], g) for p, g in pf if p in vols and vols[p] is not None and g is not None]
        if len(aligned) < SERIES_MIN_PERIODS:
            raise MoatRefusal(f"{where} (growth_rates): {len(aligned)} aligned period(s); at least {SERIES_MIN_PERIODS}")
        u = math.prod(1 + v for _, v, _ in aligned) ** (1 / len(aligned)) - 1
        a = math.prod(1 + g for _, _, g in aligned) ** (1 / len(aligned)) - 1
        rg = (1 + u) * (1 + a) - 1
        rsrc = "declared growth rates"
        detail = [{"period_end": p, "volume_growth": round(v, 4), "price_growth": round(g, 4)} for p, v, g in aligned]
    cls = classify(u, a, hurdle)
    return {"mode": mode, "volume_metric": facts[vf[0]].get("metric"), "volume_basis": vp.get("volume_basis"),
            "revenue_source": rsrc, "periods": detail, "volume_cagr": _r(u), "revenue_cagr": _r(rg), "price_cagr": _r(a),
            "inflation_hurdle": hurdle, "hurdle_basis": hbasis, "class": cls, "bounds": bounds(cls, u, a, hurdle)}


def check_bounds(vpres, pillars):
    b, errs, vals = vpres["bounds"], [], {}
    for k in ("pricing_power", "reach_and_growth"):
        pe = pillars.get(k) or {}
        if pe.get("status") == "not_applicable":
            errs.append(f"{k} cannot be not applicable when a volume x price decomposition is declared")
            continue
        s = pe.get("score")
        vals[k] = s
        lo, hi = b[k]
        if s is not None and not lo <= s <= hi:
            errs.append(f"{k} {s:+d} outside [{lo:+d}, {hi:+d}]")
    if b["pair_max"] is not None and all(vals.get(k) is not None for k in ("pricing_power", "reach_and_growth")):
        if vals["pricing_power"] + vals["reach_and_growth"] > b["pair_max"]:
            errs.append(f"pricing_power + reach_and_growth = {vals['pricing_power'] + vals['reach_and_growth']:+d} above "
                        f"{b['pair_max']:+d}")
    if errs:
        raise MoatRefusal(f"moat_scorecard: the volume x price decomposition ({vpres['volume_metric']}: volume CAGR "
                          f"{vpres['volume_cagr'] * 100:+.2f}%, revenue per unit CAGR {vpres['price_cagr'] * 100:+.2f}% vs "
                          f"hurdle {vpres['inflation_hurdle'] * 100:.2f}% -> {vpres['class']}) bounds the scores: "
                          + "; ".join(errs))


# ---------------------------------------------------------------------------
# Sources (Layer 1): S1-S9, W1-W8, then the caps
# ---------------------------------------------------------------------------
def _pillar_score(pillars, name):
    p = pillars.get(name) or {}
    return p.get("score") if p.get("status") in ("scored", "unsupported_neutral", "measured") else None


def _ge(v, x):
    return v is not None and v >= x


def check_sources(sources, pillars, btype, ctx, roc, strict, gate):
    """Validate moat_scorecard.sources in order. Shape (S1, S1a, field types, the extra keys only where they belong)
    always; the evidence rules S2-S9 / W1-W8 on a 5.7 run (strict). gate(name, msg, data_driven) refuses, or records
    drift on a rebuild for the data-driven halves (S3, S7, S9 (b), W4). Returns the items for moat_evidence."""
    where0 = "moat_scorecard.sources"
    if not isinstance(sources, list):
        raise MoatRefusal(f"{where0} must be a list (an empty list only at moat 3 or below)")
    items, seen = [], set()
    lad = ladder_family(btype)
    for i, s in enumerate(sources):
        where = f"{where0}[{i}]"
        if not isinstance(s, dict):
            raise MoatRefusal(f"{where} must be an object")
        typ, sub = s.get("type"), s.get("subtype")
        if (typ, sub) in SUBTYPE_ALIASES:
            nt, ns = SUBTYPE_ALIASES[(typ, sub)]
            raise MoatRefusal(f"{where}: {typ}/{sub} is a retired name — use {nt}/{ns}")
        if typ not in SOURCE_TYPES:
            raise MoatRefusal(f"{where}: type {typ!r} is not a moat source (allowed: {', '.join(SOURCE_TYPES)}; great "
                              "products, market share, execution and management are supporting factors, never a source)")
        if sub not in SOURCE_TYPES[typ]:
            raise MoatRefusal(f"{where}: subtype {sub!r} is not a subtype of {typ} (allowed: {', '.join(SOURCE_TYPES[typ])})")
        if (typ, sub) in seen:
            raise MoatRefusal(f"{where}: {typ}/{sub} is declared twice")
        seen.add((typ, sub))
        allowed = set(SOURCE_KEYS)
        for k, (t2, s2) in SOURCE_EXTRA_KEYS.items():
            if typ == t2 and (s2 is None or sub == s2):
                allowed.add(k)
        unknown = sorted(set(s) - allowed)
        if unknown:
            raise MoatRefusal(f"{where} ({typ}/{sub}) has unknown key(s) {unknown}")
        strength = s.get("strength")
        if strength not in ("narrow", "wide"):
            raise MoatRefusal(f"{where} ({typ}/{sub}): strength must be narrow or wide")
        if not str(s.get("rationale") or "").strip():
            raise MoatRefusal(f"{where} ({typ}/{sub}) needs a rationale")
        fids = check_fact_ids(where, s.get("facts", []), ctx, "moat:sources", types=None)
        mets = s.get("metrics", [])
        if not isinstance(mets, list) or any(m not in SOURCE_METRICS for m in mets) or len(set(mets)) != len(mets):
            raise MoatRefusal(f"{where}.metrics must be distinct names from {', '.join(SOURCE_METRICS)}")
        name = f"{typ}/{sub}"
        tp_only = bool(fids) and not mets and all(ctx["facts"][x].get("kind") == "third_party" for x in fids)
        item = {"type": typ, "subtype": sub, "strength": strength, "facts": list(fids), "metrics": list(mets),
                "third_party_only": tp_only,
                "support": "facts_and_metrics" if (fids and mets) else ("facts" if fids else "metrics_only"),
                "expiry_years": None, "incumbents_count": None, "competitors_count": None}
        if "incumbents" in s:
            inc = s["incumbents"]
            if not isinstance(inc, list) or not 1 <= len(inc) <= 5 or not all(isinstance(x, str) and 2 <= len(x.strip()) <= 60 for x in inc):
                raise MoatRefusal(f"{where}.incumbents must be 1-5 names of 2-60 characters")
            item["incumbents_count"] = len(inc)
        if "competitors" in s:
            comp = s["competitors"]
            if (not isinstance(comp, list) or not 1 <= len(comp) <= 5
                    or not all(isinstance(x, str) and 2 <= len(x.strip()) <= 60 for x in comp) or len(set(comp)) != len(comp)):
                raise MoatRefusal(f"{where}.competitors must be 1-5 distinct names of 2-60 characters")
            item["competitors_count"] = len(comp)
        if "expiry_years" in s:
            ey = s["expiry_years"]
            fid = ey.get("fact") if isinstance(ey, dict) else None
            if not isinstance(ey, dict) or set(ey) != {"fact"} or fid not in fids:
                raise MoatRefusal(f"{where}.expiry_years must be {{\"fact\": \"<id>\"}} naming an event fact among the source's facts")
            f = ctx["facts"][fid]
            if f.get("type") != "event" or f.get("unit") != "count" or f.get("unit_label") != "years" or _fnum(f.get("value")) is None:
                raise MoatRefusal(f"{where}.expiry_years: {fid} must be an event fact with unit count and unit_label years "
                                  "(years of protection left on the core patents)")
            item["expiry_years"] = {"fact": fid, "years": _fnum(f["value"])}
        items.append(item)
        if not strict:
            continue
        # ---- evidence rules (5.7 runs) ----
        if not fids and not mets:   # S2
            raise MoatRefusal(f"{where} ({name}) has no support — cite facts.json ids (used_for moat:sources) or a measured "
                              "metric at +1 or better")
        for m in mets:              # S3 (data-driven)
            sc = _pillar_score(pillars, m)
            if not _ge(sc, 1):
                gate("source_metric", f"{where} cites metric {m}, which scored {_sgn(sc) if sc is not None else 'not measured'} — "
                     "a metric supports a source only at +1 or better", True)
        if "returns_on_capital" in mets and not fids:   # W8 (a)
            raise MoatRefusal(f"{where} ({name}) cites returns_on_capital with no fact: returns on capital may support a "
                              "source only together with a fact")
        pp, ret = _pillar_score(pillars, "pricing_power"), _pillar_score(pillars, "retention")
        if typ == "intangible_assets" and sub == "brand" and not (_ge(pp, 1) or _ge(ret, 1)):   # S4
            raise MoatRefusal(f"{where} intangible_assets/brand needs pricing_power or retention at +1 or better (a brand "
                              "counts only when it lets the company charge more or keeps repeat purchase): pricing_power "
                              f"{_sgn(pp)}, retention {_sgn(ret)}")
        if typ == "switching_costs" and not _ge(_pillar_score(pillars, "switching_costs"), 1):   # S5
            raise MoatRefusal(f"{where} {name} is declared but the switching_costs pillar scores "
                              f"{_sgn(_pillar_score(pillars, 'switching_costs'))}")
        if typ == "network_effects" and not (_ge(_pillar_score(pillars, "reach_and_growth"), 1) or _ge(ret, 1)):   # S6
            raise MoatRefusal(f"{where} {name} needs reach_and_growth or retention at +1 or better (value that rises with "
                              "users shows up as users or as retention)")
        se = pillars.get("scale_economics") or {}
        if typ == "size_advantage" and se.get("status") == "measured" and se.get("score", 0) < 0:   # S7 (data-driven)
            gate("source_scale", f"{where} {name} with scale_economics {se['score']:+d} (margins fell as revenue grew: "
                 f"first-2-yr avg {_pct(se.get('margin_first2'))} -> last-2-yr avg {_pct(se.get('margin_last2'))}) — size is "
                 "not giving a cost edge", True)
        if typ == "switching_costs" and sub == "installed_base_aftermarket":   # S8
            sm = _series_ends([x for x in fids if ctx["facts"][x].get("unit") == "pct"], ctx, AFTERMARKET_METRICS)
            if not any(_is_series(p) for p in sm.values()):
                raise MoatRefusal(f"{where} switching_costs/installed_base_aftermarket needs an aftermarket or recurring "
                                  f"revenue share series (metric one of {', '.join(sorted(AFTERMARKET_METRICS))}; 3 periods "
                                  "over 360 days): none cited")
        if typ == "efficient_scale":   # S9
            cc = [x for x in fids if ctx["facts"][x].get("metric") == "competitor_count"
                  and ctx["facts"][x].get("unit") == "count" and ctx["facts"][x].get("kind") != "third_party"]
            vals = [_fnum(ctx["facts"][x].get("value")) for x in cc]
            if not cc or any(v is None or v > EFFICIENT_SCALE_MAX_COMPETITORS for v in vals):
                got = f" (got {', '.join(f'{x} = {v:g}' for x, v in zip(cc, vals) if v is not None)})" if cc else ""
                raise MoatRefusal(f"{where} {name} needs a competitor_count fact (served-market competitors, "
                                  f"{EFFICIENT_SCALE_MAX_COMPETITORS} or fewer; not third-party){got}: none cited" if not cc else
                                  f"{where} {name} needs a competitor_count fact of {EFFICIENT_SCALE_MAX_COMPETITORS} or fewer "
                                  f"served-market competitors{got}")
            if item["competitors_count"] is None:
                raise MoatRefusal(f"{where} {name} needs competitors: the served-market competitors by name")
            if any(item["competitors_count"] != v for v in vals):
                raise MoatRefusal(f"{where} {name} names {item['competitors_count']} competitors but its competitor_count fact "
                                  f"({cc[0]}) says {vals[0]:g}: name every served-market competitor")
            line = COST_OF_CAPITAL_LINE[lad]
            gm = roc.get("_median_value") if roc.get("status") == "measured" else None
            if gm is None or gm < line:   # (b) data-driven
                gate("source_efficient_scale_return",
                     f"{where} {name} with governing {roc.get('metric')} median {_pct(gm) if gm is not None else 'unmeasured'} "
                     f"(< {_pct(line, 0)}{' on the real-asset ladder' if lad == 'real_assets' else ''}): a market that supports "
                     "only a few profitable players shows returns above the cost of capital", True)
            threats = [t.get("type") for t in (pillars.get("erosion_risks") or {}).get("threats") or []]
            if not _ge(pp, 0) or "subsidized_competitor" in threats:   # (c)
                raise MoatRefusal(f"{where} {name} with pricing_power {_sgn(pp)}"
                                  f"{' and a subsidized_competitor threat' if 'subsidized_competitor' in threats else ''}: returns "
                                  "above the cost of capital must come without a price war")
        if strength == "wide" and tp_only:   # W1
            raise MoatRefusal(f"{where} {name} is wide on third-party facts only ({', '.join(fids)}) — third-party-only support "
                              "makes a source narrow at most")
        if typ == "cost_advantage" and sub == "process" and strength == "wide":   # W2 (03c decision 14: the series alone)
            ok = False
            for m in PROCESS_LEAD_METRICS:
                fx = [x for x in fids if ctx["facts"][x].get("metric") == m and ctx["facts"][x].get("type") != "event"]
                ends = sorted({_fact_end(ctx["facts"][x], ctx) for x in fx
                               if str(ctx["facts"][x].get("period") or "").startswith("FY") and _fact_end(ctx["facts"][x], ctx)})
                vals_m = [_fnum(ctx["facts"][x].get("value")) for x in fx]
                if (len(ends) >= PROCESS_LEAD_MIN_FY and _is_series(ends, PROCESS_LEAD_MIN_FY, PROCESS_LEAD_MIN_SPAN_DAYS)
                        and all(v is not None and v > 0 for v in vals_m)):
                    ok = True
            if not ok:
                nfy = max([len({ctx["facts"][x].get("period") for x in fids if ctx["facts"][x].get("metric") == m})
                           for m in PROCESS_LEAD_METRICS] + [0])
                raise MoatRefusal(f"{where} cost_advantage/process is wide: a process advantage is narrow unless a "
                                  f"unit_cost_lead or yield_lead series covers {PROCESS_LEAD_MIN_FY} fiscal years with a lead "
                                  f"every year ({nfy} FY cited)")
        if typ == "switching_costs" and strength == "wide":   # W3
            if btype == "consumer_brands_retail":
                raise MoatRefusal(f"{where} {name} is wide at a consumer_brands_retail company: consumer retail / staples "
                                  "switching costs are narrow at most")
            if not _ge(pp, 1):
                raise MoatRefusal(f"{where} {name} is wide with pricing_power {_sgn(pp)}: a wide switching cost also lets the "
                                  "company charge more (pricing_power +1 or better)")
        if typ == "size_advantage" and strength == "wide" and not _ge(_pillar_score(pillars, "scale_economics"), 1):   # W4
            gate("source_scale_wide", f"{where} {name} is wide with scale_economics "
                 f"{_sgn(_pillar_score(pillars, 'scale_economics'))}", True)
        if typ == "intangible_assets" and sub == "patent":   # W5
            if item["expiry_years"] is None:
                raise MoatRefusal(f"{where} intangible_assets/patent needs expiry_years {{\"fact\": \"<id>\"}} (an event fact: "
                                  "years of protection left on the core patents)")
            yrs = item["expiry_years"]["years"]
            if strength == "wide" and yrs < PATENT_NARROW_YEARS:
                raise MoatRefusal(f"{where} intangible_assets/patent is wide with {yrs:g} years of protection left "
                                  f"({item['expiry_years']['fact']}): under {PATENT_NARROW_YEARS} years makes a patent source narrow")
        if typ == "counter_positioning":   # W6
            if strength == "wide":
                raise MoatRefusal(f"{where} counter_positioning/business_model is wide: counter-positioning is narrow and "
                                  "time-limited (it erodes once incumbents accept the damage)")
            if not item["incumbents_count"] or not fids:
                raise MoatRefusal(f"{where} counter_positioning needs incumbents (who cannot copy the model) and at least one fact")
        if typ == "customer_captivity" and strength == "wide":   # W7
            sm = _series_ends(fids, ctx, CAPTIVITY_METRICS)
            if not (_ge(ret, 1) and any(_is_series(p) for p in sm.values())):
                raise MoatRefusal(f"{where} {name} is wide without retention at +1 or better and a retention or repeat-purchase "
                                  f"series among its facts (metric one of {', '.join(sorted(CAPTIVITY_METRICS))}): retention "
                                  f"{_sgn(ret)}")
        if strength == "wide" and not fids:   # W8 (b)
            raise MoatRefusal(f"{where} {name} is wide on metrics only ({', '.join(mets)}): a source with no fact is narrow at most")
    return items


def source_caps(moat, items, roc, gate):
    """G3 (M1): no source -> <= 3; one narrow source -> <= 6; 7+ needs a wide source or two fact-backed sources (W8 (c):
    a metric-only source is not the second); 9+ needs two wide sources AND returns_on_capital +2 sustained. Checked
    after the evidence score; nothing in the evidence relaxes them."""
    n = len(items)
    w = sum(1 for s in items if s["strength"] == "wide")
    nf = sum(1 for s in items if s["facts"])
    sustained = bool(roc.get("sustained_plus2"))
    if n == 0:
        mx, why = NO_SOURCE_CAP, "no source: the moat is capped at 3"
    elif w == 0 and nf < 2:
        mx, why = ONE_NARROW_CAP, ("one narrow source caps the moat at 6" if n == 1 else
                                   f"{n} narrow sources of which {nf} cites a fact: 7+ needs a wide source or two fact-backed sources")
    elif w >= 2 and sustained:
        mx, why = 10, "two wide sources and returns_on_capital +2 sustained: 9-10 possible"
    else:
        mx, why = 8, (f"{n} source(s) ({w} wide): 9-10 needs two wide sources" if w < 2 else
                      "two wide sources, returns_on_capital not +2 sustained: 9-10 needs it")
    cap = {"max_moat": mx, "moat_9_ok": w >= 2 and sustained, "reason": why}
    names = ", ".join(f"{s['type']}/{s['subtype']}" for s in items)
    if n == 0 and moat > NO_SOURCE_CAP:
        raise MoatRefusal(f"moat_score {moat:g} with no source in moat_scorecard.sources: a moat with no moat source (see "
                          "SOURCE_TYPES) is capped at 3")
    if n == 1 and w == 0 and moat > ONE_NARROW_CAP:
        raise MoatRefusal(f"moat_score {moat:g} rests on one narrow source ({names}): one narrow source caps the moat at 6")
    if moat >= WIDE_OR_TWO_MIN and not (w >= 1 or nf >= 2):
        mo = ", ".join(f"{s['type']}/{s['subtype']}" for s in items if not s["facts"])
        raise MoatRefusal(f"moat_score {moat:g} rests on {n} sources of which only {nf} cites a fact"
                          f"{f' ({mo} is metric-only)' if mo else ''}: 7+ needs a wide source or two fact-backed sources")
    if moat >= TWO_WIDE_MIN:
        if w < 2:
            raise MoatRefusal(f"moat_score {moat:g} needs two wide sources and returns_on_capital +2 sustained (every year at "
                              f"or above 15%): {w} wide source(s)")
        if not sustained:
            low = [f"FY{s['fy']} {_pct(s.get(roc.get('metric')))}" for s in roc.get("series") or []
                   if s.get(roc.get("metric")) is not None and s.get(roc.get("metric")) < (roc.get("thresholds") or [0, 0.15])[1]]
            gate("cap_moat_9_sustained", f"moat_score {moat:g} needs two wide sources and returns_on_capital +2 sustained "
                 f"(every year at or above the +1 line): returns_on_capital {_sgn(roc.get('score'))}, not sustained"
                 f"{' (' + ', '.join(low) + ')' if low else ''}", True)
    return {"declared": True, "count": n, "wide": w, "widest": ("wide" if w else "narrow") if n else "none",
            "fact_backed": nf, "items": items, "cap": cap}


# ---------------------------------------------------------------------------
# Evidence, lint, gates
# ---------------------------------------------------------------------------
def core_evidence(pillars):
    """(core evidence 0-10 or None, weight): 5 + 5 x the weighted mean of each scored pillar's score over its own range
    end (s / max when s > 0, s / |min| when s < 0) — for a +-2 pillar exactly 5 + 2.5 x the mean."""
    num = den = 0.0
    for k in CORE:
        p = pillars.get(k) or {}
        if p.get("score") is None or p.get("status") not in ("measured", "scored"):
            continue
        lo, hi = RANGES[k]
        s = p["score"]
        sh = s / hi if s > 0 else (s / abs(lo) if s < 0 else 0.0)
        num += WEIGHTS[k] * sh
        den += WEIGHTS[k]
    if den == 0:
        return None, 0.0
    return round(5 + 5 * num / den, 2), round(den, 2)


def evidence(core, adjustment):
    return None if core is None else round(max(0.0, min(10.0, core + adjustment)), 2)


def lint_bad_moats(j, is_57):
    """M1b: bad-moat wording (leader, share, execution, management, great products, ...) presented as the SOURCE — an
    item of moat_for / moat_justification / a source rationale that matches BAD and names no source phrase (SRC); on a
    5.7 run an item that marks itself `(supporting: <factor>)` is support, not source. Non-blocking; no worker text in
    the output (the matched word is from the fixed vocabulary)."""
    items = [(f"moat_for[{i}]", s) for i, s in enumerate(j.get("moat_for") or [])]
    items.append(("moat_justification", j.get("moat_justification")))
    sc = j.get("moat_scorecard") if isinstance(j.get("moat_scorecard"), dict) else {}
    for k, s in enumerate(sc.get("sources") or [] if isinstance(sc.get("sources"), list) else []):
        if isinstance(s, dict):
            items.append((f"moat_scorecard.sources[{k}].rationale", s.get("rationale")))
    out = []
    for field, s in items:
        if not isinstance(s, str):
            continue
        m = BAD.search(s)
        if not m or SRC.search(s):
            continue
        if is_57 and SUPPORT_CITE.search(s):
            continue
        out.append({"field": field, "matched": m.group(0).lower()})
    return out


def numeric_leaves(ev):
    """Every number in moat_evidence (bools excluded) — the engine-source set a moat reason's numbers may trace to
    (make_score.check_influence extra=...): a low-ROIC reason quoting the tangible ROIC, the industry median or the
    supporting adjustment traces."""
    out = []

    def walk(x):
        if isinstance(x, bool) or x is None:
            return
        if isinstance(x, (int, float)):
            if math.isfinite(x):
                out.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(ev)
    return out


def industry_file_line(ev):
    f = (ev or {}).get("industry_file")
    if not f:
        return f"{INDUSTRY_FILE} not found — industry_structure not measured"
    return f"{INDUSTRY_FILE} built {f.get('built')} (sha256 {str(f.get('sha256'))[:8]}…)"


def _strip_private(x):
    if isinstance(x, dict):
        return {k: _strip_private(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, list):
        return [_strip_private(v) for v in x]
    return x


def _reason_ok(text):
    return isinstance(text, str) and bool(text.strip()) and bool(DIGIT.search(text))


def is_rebuild(prior, n, decl_sha, f_sha):
    """Authoring vs rebuild (03b §5, rebase L3 amendment 3.2): a rebuild is the same engine run (the prior score's
    dcf_content_hash), the same declaration and the same facts.json as a prior CHECKED 5.7 moat_evidence."""
    pe = (prior or {}).get("moat_evidence") if isinstance(prior, dict) else None
    if not isinstance(pe, dict) or pe.get("status") != "checked":
        return False
    return (prior.get("dcf_content_hash") == (n or {}).get("content_hash") and pe.get("declaration_sha256") == decl_sha
            and pe.get("facts_sha256") == f_sha)


def evaluate(folder, n, j, facts=None, is_57=False, sic=None, industry=None, prior=None):
    """score.json moat_evidence for one folder, or MoatRefusal (03b §5 order: core pillars -> core evidence ->
    supporting factors -> adjustment -> evidence -> G2 -> G1 -> sources -> G3 caps -> G4, G5, G6). facts: {id: fact}
    from facts.json; is_57: an engine-5.7 run (the gates refuse); sic: the filer's SIC; industry: load_industry();
    prior: the score.json being replaced (authoring vs rebuild)."""
    n = n or {}
    ticker = str(n.get("ticker") or os.path.basename(os.path.normpath(folder))).upper()
    sc = j.get("moat_scorecard")
    if is_57 and sc is None:
        raise MoatRefusal("an engine 5.7 run needs judgment.json moat_scorecard (WORKER_SPEC step 5) — none declared")
    if sc is not None:
        if not isinstance(sc, dict):
            raise MoatRefusal("moat_scorecard must be an object")
        unknown = sorted(set(sc) - set(SCORECARD_KEYS))
        if unknown:
            raise MoatRefusal(f"moat_scorecard has unknown key(s) {unknown} (allowed: {', '.join(SCORECARD_KEYS)})")
        if sc.get("version") != SCORECARD_VERSION or isinstance(sc.get("version"), bool):
            raise MoatRefusal(f"moat_scorecard.version must be {SCORECARD_VERSION}")
        for k in REASON_FIELDS:
            if sc.get(k) is not None and not isinstance(sc.get(k), str):
                raise MoatRefusal(f"moat_scorecard.{k} must be a string or null")
    strict = bool(is_57)
    # the fiscal calendar (CSV + statements.json) is read only when a declared scorecard cites facts
    ctx = _ctx(folder, n, facts) if sc is not None else {"facts": {}, "calendar": {}, "lpe": n.get("latest_period_end")}
    moat = float(j["moat_score"])
    src, rows, iprd = window_rows(folder, n)
    raw = raw_rows(folder)[1]
    last_raw = raw[-1] if raw else None
    allowed, lock_rule, cls = type_lock(sic, last_raw)
    hint, hint_basis = sic_hint(sic, n.get("fragility_flags"), allowed, cls)
    reason_required = False
    if sc is not None:
        btype = sc.get("business_type")
        if btype not in BUSINESS_TYPES:
            raise MoatRefusal(f"moat_scorecard.business_type must be one of {', '.join(BUSINESS_TYPES)} (got {btype!r})")
        if allowed and btype not in allowed:
            if cls == "reit" and lock_rule:
                raise MoatRefusal(f"moat_scorecard.business_type {btype} at SIC {sic} with {lock_rule}: a mortgage-REIT "
                                  "balance sheet is locked to financial_balance_sheet (ROE governs)")
            raise MoatRefusal(f"moat_scorecard.business_type {btype} contradicts SIC {sic}: a filer in this SIC range is "
                              f"scored as {' or '.join(sorted(allowed))} (its mechanical pillars depend on it)")
        btr = sc.get("business_type_reason")
        if not isinstance(btr, str) or not btr.strip():
            raise MoatRefusal("moat_scorecard.business_type_reason must say why this type (a revenue share or segment)")
        if cls == "reit" and not lock_rule and btype == "real_assets":
            reason_required = True
            if not DIGIT.search(btr):
                raise MoatRefusal(f"moat_scorecard.business_type real_assets at SIC {sic} needs business_type_reason carrying "
                                  "a number (what share of revenue or assets is owned real estate)")
        tbasis = "declared"
    else:
        btype, tbasis = None, hint_basis
    bt = btype or hint
    decl_sha = declaration_sha256(j) if sc is not None else None
    f_sha = facts_sha256(folder)
    rebuild = strict and is_rebuild(prior, n, decl_sha, f_sha)
    drift = []

    def gate(name, msg, data_driven):
        if data_driven and rebuild and GATE_DRIFT_ON_REBUILD:
            drift.append({"gate": name, "detail": msg})
            return
        raise MoatRefusal(msg)

    # ---- mechanical pillars ----
    roc = pillar_returns_on_capital(bt, src, rows)
    pillars = {"returns_on_capital": roc,
               "industry_structure": pillar_industry_structure(bt, ticker, sic, roc, industry, cik=n.get("cik")),
               "capital_intensity": pillar_capital_intensity(bt, folder),
               "scale_economics": pillar_scale_economics(bt, src, rows)}
    vpres, sup, sup_status, items = None, None, "absent", None
    if sc is not None:
        decl = sc.get("pillars")
        if not isinstance(decl, dict):
            raise MoatRefusal("moat_scorecard.pillars must be an object keyed by pillar name")
        for k in decl:
            if k in RETIRED_PILLARS:
                raise MoatRefusal(f"moat_scorecard.pillars.{k} is not a pillar since the M1b amendment — score it under "
                                  f"{RETIRED_PILLARS[k]}")
        unknown = sorted(set(decl) - set(CORE))
        if unknown:
            raise MoatRefusal(f"moat_scorecard.pillars has unknown key(s) {unknown}; pillars are {', '.join(CORE)}")
        missing = [k for k in DECLARED if k not in decl]
        if missing:
            raise MoatRefusal(f"moat_scorecard.pillars is missing {missing} — every declared pillar is mandatory (score it, or "
                              "mark applicable false with a not_applicable_reason where the business type allows)")
        for k in MECHANICAL:
            m = decl.get(k)
            if m is None:
                continue
            if not isinstance(m, dict) or set(m) - {"comment"}:
                raise MoatRefusal(f"moat_scorecard.pillars.{k} is mechanical (make_score derives it); it may carry only a "
                                  "'comment' — put a disagreement in moat_divergence_reason / low_roic_reason")
            if str(m.get("comment") or "").strip():
                pillars[k]["comment"] = str(m["comment"]).strip()
        for k in DECLARED:
            pillars[k] = check_declared(k, decl[k], bt, ctx, strict=strict)
        if sc.get("volume_price") is not None:
            vpres = volume_price(sc["volume_price"], rows, ctx)
            check_bounds(vpres, pillars)
        elif bt == "consumer_users" and strict:
            raise MoatRefusal("moat_scorecard.volume_price (users x revenue per user) is required for business type consumer_users")
        if sc.get("supporting") is not None:
            sup, sup_status = check_supporting(sc["supporting"], ctx)
        elif strict:
            raise MoatRefusal("moat_scorecard.supporting is required on a 5.7 run: product_quality, market_share, execution "
                              "and management, each scored with facts or declared applicable: false with not_applicable_reason")
        if strict and "sources" not in sc:
            raise MoatRefusal("moat_scorecard.sources is required on a 5.7 run (a list of moat sources; [] only at moat 3 or below)")
    core, weight = core_evidence(pillars)
    adj = sup["adjustment"] if sup else 0.0
    ev_score = evidence(core, adj)
    div = round(moat - ev_score, 2) if ev_score is not None else None
    within = (abs(moat - ev_score) <= TOLERANCE) if ev_score is not None else None
    flags = []
    gm = pillars["returns_on_capital"]
    unstable_flag = "TANGIBLE_DENOMINATOR_UNSTABLE" if gm["metric"] == "roic_tangible" else "ROIC_DENOMINATOR_UNSTABLE"
    if gm["metric"] != "roe" and any(unstable_flag in (r.get("roic_flags") or []) for r in rows):
        flags.append("ROIC_DENOMINATOR_UNSTABLE")
    if iprd:
        flags.append("IPRD_CHARGE_IN_WINDOW")
    ero = erosion_test(gm, rows, src)
    if ero["fired"]:
        flags.insert(0, "MOAT_EROSION")
    # ---- gates (computed on every run; refused on a 5.7 run) ----
    gmed = gm.get("_median_value") if gm.get("status") == "measured" else None
    low_line = LOW_RETURN[2] if gm["metric"] == "roe" else LOW_RETURN[1]
    low_applies = moat >= LOW_RETURN[0] and (gmed is None or gmed < low_line)
    vals = gm.get("_values") or []
    plain_ok = gm["metric"] != "roic_tangible" or (gm.get("_plain_median") is not None and gm["_plain_median"] >= TANGIBLE_PLUS2_PLAIN_LINE)
    rev_applies = (moat <= REVERSE[0] and gmed is not None and gmed >= REVERSE[1] and bool(vals)
                   and all(v >= REVERSE[2] for v in vals) and plain_ok)
    er = pillars.get("erosion_risks") or {}
    ero_applies = bool(ero["fired"] and er.get("status") == "scored" and er.get("score") == 1)
    reasons = {k: (sc or {}).get(k) for k in REASON_FIELDS}
    gates = {"divergence": {"applies": bool(within is False), "reason": reasons["moat_divergence_reason"]},
             "low_return": {"applies": low_applies, "measure": gm["metric"], "median": gm.get("median"),
                            "median_note": gm.get("median_note"), "threshold": low_line, "reason": reasons["low_roic_reason"]},
             "reverse": {"applies": rev_applies, "median": gm.get("median"), "median_note": gm.get("median_note"),
                         "min": gm.get("min"), "threshold": REVERSE[1], "every_year": REVERSE[2],
                         "reason": reasons["high_return_low_moat_reason"]},
             "erosion": {"applies": ero_applies, "reason": reasons["erosion_rebuttal"]}}
    sources_rec = {"declared": False, "count": None, "wide": None, "widest": None, "fact_backed": None, "items": [],
                   "cap": None}
    if strict:
        if weight < MIN_EVIDENCE_WEIGHT:   # G2
            raise MoatRefusal(f"moat evidence weight {weight:g} < {MIN_EVIDENCE_WEIGHT:g}: too little of the scorecard is "
                              "measured or fact-supported to check the moat (cite facts for more pillars)")
        if within is False and not _reason_ok(reasons["moat_divergence_reason"]):   # G1
            gate("divergence", f"moat_score {moat:g} is {abs(moat - ev_score):.2f} from the evidence score {ev_score:.2f} "
                 f"(tolerance +/-{TOLERANCE:g}) — add moat_scorecard.moat_divergence_reason carrying a number, or revisit "
                 "the moat or the pillars", True)
    if sc is not None and "sources" in sc:
        items = check_sources(sc.get("sources"), pillars, bt, ctx, gm, strict, gate)
        sources_rec = {"declared": True, "count": len(items), "wide": sum(1 for s in items if s["strength"] == "wide"),
                       "widest": ("wide" if any(s["strength"] == "wide" for s in items) else "narrow") if items else "none",
                       "fact_backed": sum(1 for s in items if s["facts"]), "items": items, "cap": None}
        if strict:
            sources_rec = source_caps(moat, items, gm, gate)   # G3
    if strict:
        if low_applies and not _reason_ok(reasons["low_roic_reason"]):   # G4
            med_s = "unmeasured" if gmed is None else _pct(gmed)
            gate("low_return", f"moat_score {moat:g} >= 7 on median {gm['metric']} {med_s} (< {_pct(low_line, 0)}) — add "
                 "moat_scorecard.low_roic_reason carrying a number (why the measured history understates the franchise)", True)
        if rev_applies and not _reason_ok(reasons["high_return_low_moat_reason"]):   # G5
            fys = [s.get("fy") for s in gm.get("series") or []] or ["?"]
            gate("reverse", f"moat_score {moat:g} <= 4 on governing {gm['metric']} median {_pct(gmed)} with every year >= 15% "
                 f"(FY{fys[0]}-FY{fys[-1]}) — add moat_scorecard.high_return_low_moat_reason carrying a number (e.g. returns "
                 "from a cycle peak or from leverage, not a source), or revisit the moat", True)
        if ero_applies and not _reason_ok(reasons["erosion_rebuttal"]):   # G6
            gate("erosion", f"MOAT_EROSION: governing {gm['metric']} fell {ero['governing_change_pp']:+.2f}pp "
                 f"(first-2 avg {_pct(ero.get('governing_first2'))} -> last-2 avg {_pct(ero.get('governing_last2'))}) and "
                 f"{ero['margin_basis']} margin {ero['margin_change_pp']:+.2f}pp over the last 5 FY — erosion_risks +1 needs "
                 "moat_scorecard.erosion_rebuttal carrying a number (why this is a cycle, not a moat eroding), or score "
                 "erosion_risks <= 0", True)
    drifted = {d["gate"] for d in drift}
    for g, rec in gates.items():
        rec["drifted"] = g in drifted
    out = {"scorecard": "declared" if sc is not None else "absent", "version": SCORECARD_VERSION,
           "status": "checked" if strict else "report_only",
           "business_type": btype, "business_type_basis": tbasis, "business_type_hint": hint,
           "sic": str(sic) if sic not in (None, "") else None,
           "type_lock": {"sic_class": cls, "locked": sorted(allowed) if allowed and len(allowed) == 1 else None,
                         "allowed": sorted(allowed) if allowed else None, "rule": lock_rule,
                         "reason_required": reason_required},
           "core_evidence_score": core, "supporting_adjustment": adj, "supporting_status": sup_status,
           "evidence_score": ev_score, "evidence_weight": weight, "weight_total": round(sum(WEIGHTS.values()), 2),
           "moat_score": moat, "divergence": div, "tolerance": TOLERANCE, "within_tolerance": within,
           "governing": {"measure": gm["metric"], "ladder": gm["ladder"], "median": gm.get("median"),
                         "median_note": gm.get("median_note"), "reason": gm.get("governing_reason")},
           "sources": sources_rec,
           "pillars": {k: pillars[k] for k in CORE if k in pillars},
           "supporting": sup if sup is not None else None,
           "erosion_test": ero, "flags": flags, "gates": gates,
           "moat_divergence_reason": reasons["moat_divergence_reason"],
           "moat_lint": lint_bad_moats(j, strict),
           "industry_file": ({"built": industry.get("built"), "sha256": industry.get("_sha256")} if industry else None),
           "declaration_sha256": decl_sha, "facts_sha256": f_sha,
           "run_kind": ("rebuild" if rebuild else "authoring") if strict else None,
           "gate_drift": drift}
    if vpres:
        out["volume_price"] = vpres
    if iprd:
        out["iprd_in_window"] = iprd
    return _strip_private(out)


# ---------------------------------------------------------------------------
# key_numbers.md "## Moat scorecard" (every number generated; no worker free text — 07 §1.10)
# ---------------------------------------------------------------------------
def _yr(entry, key):
    v = entry.get(key)
    if v is not None:
        return f"FY{entry.get('fy')} {_pct(v)}"
    note = entry.get(key + "_note")
    if note == NOTE_INF:
        return f"FY{entry.get('fy')} unbounded"
    return f"FY{entry.get('fy')} n/m ({note or 'not measured'})"


def _med_s(v, note):
    if v is not None:
        return _pct(v)
    if note == NOTE_INF:
        return "unbounded"
    if note == "negative_equity":
        return "n/m (negative equity)"
    return f"n/m ({note})" if note else "n/m"


def key_numbers_lines(me):
    if not me:
        return []
    p = me.get("pillars") or {}
    L = ["", "## Moat scorecard"]
    declared = me.get("scorecard") == "declared"
    hint = me.get("business_type_hint")
    if not declared:
        L.append(f"- Scorecard: none declared (engine output predates release 5.7.0) — mechanical pillars, flags and lint only; "
                 f"reported, not checked; thresholds for type {hint or 'default'} ({me.get('business_type_basis')})")
    else:
        tl = me.get("type_lock") or {}
        lock = ""
        if tl.get("locked"):
            lock = f" (locked at SIC {me.get('sic')}" + (f": {tl['rule']}" if tl.get("rule") else "") + ")"
        elif me.get("sic"):
            lock = f" (SIC {me.get('sic')})"
        L.append(f"- Business type: {me.get('business_type')}{lock}" + ("" if me.get("status") == "checked" else " — reported, not checked"))
    ev, core = me.get("evidence_score"), me.get("core_evidence_score")
    gap = me.get("divergence")
    if not declared:
        L.append(f"- Evidence score (mechanical only): {'n/m' if ev is None else f'{ev:.2f}'}/10 from core pillars weighing "
                 f"{me.get('evidence_weight'):g} of {me.get('weight_total'):g} · supporting factors not declared (adjustment 0.00) "
                 f"· moat (judgment) {me.get('moat_score'):g}/10" + ("" if gap is None else f" · gap {gap:+.2f} (not checked)"))
    else:
        sup = me.get("supporting") or {}
        parts = []
        for k in SUPPORTING:
            f = sup.get(k) or {}
            parts.append(f"{k} n/a" if f.get("status") == "not_applicable" else f"{k} {f.get('score', 0):+d}")
        within = me.get("within_tolerance")
        L.append(f"- Evidence score: core {'n/m' if core is None else f'{core:.2f}'}/10 from pillars weighing "
                 f"{me.get('evidence_weight'):g} of {me.get('weight_total'):g} · supporting adjustment "
                 f"{me.get('supporting_adjustment', 0):+.2f} (sum of 4 slots / 4: {', '.join(parts)}; capped at ±1.00) → "
                 f"{'n/m' if ev is None else f'{ev:.2f}'}/10 · moat (judgment) {me.get('moat_score'):g}/10"
                 + ("" if gap is None else f" · gap {gap:+.2f} ({'within' if within else 'OUTSIDE'} ±{me.get('tolerance'):g})"))
    r = p.get("returns_on_capital") or {}
    m = r.get("metric")
    if r.get("status") == "measured":
        sus = " (sustained)" if r.get("sustained_plus2") else ""
        cap = ""
        pc = r.get("plain_roic_check") or {}
        if pc.get("capped"):
            cap = f" (capped from +2: plain ROIC median {_med_s(pc.get('median'), pc.get('median_note'))} < 10%)"
        L.append(f"- Returns on capital — governing {m} ({r.get('governing_reason')}): "
                 + " · ".join(_yr(s, m) for s in r.get("series") or [])
                 + f" → median {_med_s(r.get('median'), r.get('median_note'))} → score {r.get('score'):+d}{sus}{cap}")
    else:
        L.append(f"- Returns on capital — governing {m}: insufficient data — {r.get('reason')}")
    md = r.get("medians") or {}
    rc = r.get("roa_cross_check") or {}
    roa_s = _pct(md.get("roa")) if md.get("roa") is not None else "n/m"
    roa_x = ""
    if rc.get("applies") and md.get("roa") is not None:
        roa_x = f" (cross-check: ROA >= 7% suggests an advantage — {'above' if md['roa'] >= ROA_LINE else 'below'})"
    L.append(f"- Side by side, 5-FY medians: ROIC {_med_s(md.get('roic'), md.get('roic_note'))} · tangible ROIC "
             f"{_med_s(md.get('roic_tangible'), md.get('roic_tangible_note'))} · ROE {_med_s(md.get('roe'), md.get('roe_note'))} · "
             f"ROA {roa_s}{roa_x}")
    neg = [s.get("fy") for s in r.get("series") or [] if s.get("roe_note") == "negative_equity"]
    if neg:
        L.append(f"- ROE n/m (negative equity): FY{', FY'.join(str(x) for x in neg)}")
    ind = p.get("industry_structure") or {}
    if ind.get("status") == "measured":
        L.append(f"- Industry structure: {ind.get('label')} ({ind.get('level')}-digit, {ind.get('ladder')} ladder) — "
                 f"{ind.get('peers')} same-ladder peers ({ind.get('peers_dropped', 0)} dropped: loss on non-positive capital), "
                 f"median governing return {_med_s(ind.get('median'), ind.get('median_note'))}; "
                 + (f"rank {ind.get('rank')} of {ind.get('of')}" if ind.get("rank") is not None else f"rank n/m of {ind.get('of')}")
                 + f" → score {ind.get('score'):+d}")
    else:
        L.append(f"- Industry structure: insufficient data — {ind.get('reason')}")
    L.append(f"- {industry_file_line(me)}")
    c = p.get("capital_intensity") or {}
    if c.get("status") == "measured":
        ser = " · ".join((f"FY{s['fy']} {_pct(s['value'])}" if s.get("value") is not None else f"FY{s['fy']} n/m ({s.get('note')})")
                         for s in c.get("series") or [])
        L.append(f"- capital_intensity (mechanical, capex / OCF, financials_history.csv): {ser} → median "
                 f"{_pct(c.get('median')) if c.get('median') is not None else 'n/m (OCF <= 0)'}"
                 + (f" (capex / revenue median {_pct(c['capex_to_revenue_median'])})" if c.get("capex_to_revenue_median") is not None else "")
                 + f" → score {c.get('score'):+d}")
    else:
        L.append(f"- capital_intensity (mechanical): {str(c.get('status')).replace('_', ' ')} — {c.get('reason')}")
    s = p.get("scale_economics") or {}
    if s.get("status") == "measured":
        L.append(f"- scale_economics (mechanical, operating margin vs revenue growth): revenue CAGR {_pct(s.get('revenue_cagr'))} · "
                 f"operating margin first-2-yr avg {_pct(s.get('margin_first2'))} → last-2-yr avg {_pct(s.get('margin_last2'))} "
                 f"({s.get('margin_change_pp'):+.2f}pp) → score {s.get('score'):+d}")
    else:
        L.append(f"- scale_economics (mechanical): {str(s.get('status')).replace('_', ' ')} — {s.get('reason')}")
    for x in me.get("iprd_in_window") or []:
        how = ("added back to operating income in returns_on_capital and scale_economics (the engine deducted it once from "
               "value)" if x.get("addback") else
               "read as filed in returns_on_capital and scale_economics" + (" (judged recurrent)" if x.get("recurrent") else ""))
        L.append(f"- Acquired IPR&D inside the window: FY{str(x['period'])[:4]} ${x['amount']:,.0f}"
                 + (f" ({_pct(x['pct_of_operating_income'])} of operating income)" if x.get("pct_of_operating_income") is not None else "")
                 + f" — {how}")
    if declared:
        src_rec = me.get("sources") or {}
        items = src_rec.get("items") or []
        if items:
            L += ["", "| Source | Strength | Support | Counts |", "|---|---|---|---|"]
            for it in items:
                sup_s = ", ".join(it.get("facts") or []) or "—"
                if it.get("metrics"):
                    sup_s += ("; " if it.get("facts") else "") + "metrics " + ", ".join(it["metrics"])
                extra = ""
                if it.get("expiry_years"):
                    extra = f"; expiry {it['expiry_years']['years']:g} years ({it['expiry_years']['fact']})"
                if it.get("incumbents_count"):
                    extra += f"; incumbents named: {it['incumbents_count']}"
                if it.get("competitors_count"):
                    extra += f"; competitors named: {it['competitors_count']}"
                L.append(f"| {it['type']}/{it['subtype']} | {it['strength']} | {sup_s}{extra} | yes |")
        cap = src_rec.get("cap") or {}
        if cap:
            L.append(f"- Source caps: {src_rec.get('count')} source(s) ({src_rec.get('wide')} wide) → moat up to {cap.get('max_moat')}; "
                     + ("9-10 possible" if cap.get("moat_9_ok") else "9-10 needs two wide sources and returns_on_capital +2 sustained"))
        elif src_rec.get("declared"):
            L.append(f"- Sources: {src_rec.get('count')} declared (caps not checked on this run)")
        L += ["", "| Pillar | Weight | Range | Score | Facts cited |", "|---|---|---|---|---|"]
        for k in DECLARED:
            q = p.get(k) or {}
            rng = f"{q.get('range', [-2, 2])[0]:+d}..{q.get('range', [-2, 2])[1]:+d}"
            if q.get("status") == "not_applicable":
                L.append(f"| {k} | {WEIGHTS[k]:g} | {rng} | n/a | not applicable (declared) |")
                continue
            cited = ", ".join(q.get("facts") or []) or "none (neutral, not counted)"
            tag = " (third-party only, cap ±1)" if q.get("third_party_only") else ""
            th = ""
            if q.get("threats"):
                th = "; threats: " + ", ".join(t["type"] for t in q["threats"])
            L.append(f"| {k} | {WEIGHTS[k]:g} | {rng} | {q.get('score'):+d} | {cited}{tag}{th} |")
        sup = me.get("supporting") or {}
        if sup:
            L += ["", "| Factor | Range | Score | Facts |", "|---|---|---|---|"]
            for k in SUPPORTING:
                q = sup.get(k) or {}
                rng = f"{q.get('range', [-1, 1])[0]:+d}..{q.get('range', [-1, 1])[1]:+d}"
                if q.get("status") == "not_applicable":
                    L.append(f"| {k} | {rng} | n/a (declared not applicable) | — |")
                else:
                    L.append(f"| {k} | {rng} | {q.get('score'):+d} | {', '.join(q.get('facts') or []) or 'none (neutral)'} |")
        vp = me.get("volume_price")
        if vp:
            if vp["mode"] == "levels":
                per = " · ".join(f"{x['period_end'][:4]}: {x['volume']:,.0f} → {x['revenue_per_unit']:,.2f}/unit" for x in vp["periods"])
            else:
                per = " · ".join(f"{x['period_end'][:4]}: volume {_pct(x['volume_growth'], 1)}, price {_pct(x['price_growth'], 1)}"
                                 for x in vp["periods"])
            b = vp["bounds"]
            L.append(f"- Volume × price ({vp['mode']}, {vp['volume_metric']}): {per}; volume CAGR {_pct(vp['volume_cagr'])} · "
                     f"revenue per unit CAGR {_pct(vp['price_cagr'])} vs inflation hurdle {_pct(vp['inflation_hurdle'])} → "
                     f"{vp['class']}; bounds pricing_power [{b['pricing_power'][0]:+d}, {b['pricing_power'][1]:+d}], "
                     f"reach_and_growth ≤ {b['reach_and_growth'][1]:+d}" + (f", pair ≤ {b['pair_max']:+d}" if b.get("pair_max") is not None else ""))
    e = me.get("erosion_test") or {}
    if e.get("status") == "measured":
        L.append(f"- Erosion test: {'FIRED' if e.get('fired') else 'not fired'} (governing {e.get('governing_change_pp'):+.2f}pp, "
                 f"{e.get('margin_basis')} margin {e.get('margin_change_pp'):+.2f}pp over the last 5 FY)")
    else:
        L.append(f"- Erosion test: not measured ({e.get('reason')})")
    if me.get("flags"):
        L.append(f"- Flags: {', '.join(me['flags'])}")
    g = me.get("gates") or {}
    checked = me.get("status") == "checked"
    lr, rv, er, dv = g.get("low_return") or {}, g.get("reverse") or {}, g.get("erosion") or {}, g.get("divergence") or {}
    lines = []
    if lr.get("applies"):
        lines.append(f"low-return applies (moat {me.get('moat_score'):g} >= 7 on median {lr.get('measure')} "
                     f"{_med_s(lr.get('median'), lr.get('median_note')) if lr.get('median') is not None or lr.get('median_note') else 'unmeasured'})"
                     + (" — reason declared in judgment.json" if lr.get("reason") else ""))
    else:
        lines.append("low-return clear" if me.get("moat_score", 0) >= LOW_RETURN[0] else f"low-return n/a (moat {me.get('moat_score'):g})")
    if rv.get("applies"):
        lines.append(f"reverse applies (moat {me.get('moat_score'):g} <= 4 on median {_med_s(rv.get('median'), rv.get('median_note'))})"
                     + (" — reason declared in judgment.json" if rv.get("reason") else ""))
    else:
        lines.append("reverse clear" if me.get("moat_score", 10) <= REVERSE[0] else f"reverse n/a (moat {me.get('moat_score'):g})")
    if er.get("applies"):
        lines.append("erosion applies (MOAT_EROSION with erosion_risks +1)" + (" — rebuttal declared in judgment.json" if er.get("reason") else ""))
    if dv.get("applies") and declared:
        lines.append("divergence applies" + (" — reason declared in judgment.json" if dv.get("reason") else ""))
    if not declared:
        lines.append("sources not declared")
    L.append(f"- Gates {'(checked)' if checked else 'on a 5.7 run'}: " + " · ".join(lines))
    if me.get("gate_drift"):
        L.append(f"- Gate drift on this rebuild (recorded, not refused; the next authoring run resolves it): "
                 + ", ".join(d["gate"] for d in me["gate_drift"]))
    if me.get("moat_lint"):
        L.append("- Bad-moat wording presented as a source (lint): "
                 + " · ".join(f"{x['field']} \"{x['matched']}\"" for x in me["moat_lint"]))
    return L


# ---------------------------------------------------------------------------
# CLI: the dry run (5.7 rules on; writes nothing)
# ---------------------------------------------------------------------------
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1 or argv[0].startswith("-"):
        print("usage: python3 _system/moat_scorecard.py <TICKER>   (read-only dry run with the 5.7 rules on)", file=sys.stderr)
        return 2
    base = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
    t = argv[0].upper()
    folder = os.path.join(base, t)
    n = _read_json(os.path.join(folder, "dcf_numbers.json")) or {"ticker": t}
    j = _read_json(os.path.join(folder, "judgment.json"))
    if not isinstance(j, dict) or j.get("moat_score") is None:
        print(f"moat_scorecard.py: {folder}/judgment.json with a moat_score is needed", file=sys.stderr)
        return 2
    fdoc = _read_json(os.path.join(folder, "facts.json"))
    sic = (n.get("sector_model") or {}).get("sic") if isinstance(n.get("sector_model"), dict) else None
    sic = sic or _engine.folder_sic(base, t)[0]
    try:
        ev = evaluate(folder, n, j, facts=_facts.by_id(fdoc) if fdoc else {}, is_57=True, sic=sic,
                      industry=load_industry(os.path.join(base, "_system")),
                      prior=_read_json(os.path.join(folder, "score.json")))
    except MoatRefusal as e:
        print(f"moat_scorecard.py: REFUSED — {e}")
        return 1
    for line in key_numbers_lines(ev):
        print(line)
    print(f"moat_scorecard.py: {t} evidence {ev.get('evidence_score')} (core {ev.get('core_evidence_score')}, supporting "
          f"{ev.get('supporting_adjustment'):+.2f}) vs moat {ev.get('moat_score'):g} — passes the 5.7 rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
