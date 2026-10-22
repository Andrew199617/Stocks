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
same engine run, the same declaration, the same facts.json (run_kind) — a newly failing DATA-driven gate is recorded
in `gate_drift`, never refused: G1, G4-G6, the measured halves of the source rules and caps, the weight floor G2 when
the declared pillars plus the measurable mechanical ones could clear it, and the volume x price bounds on the annual
rows' revenue; caps and rules that depend only on the declaration refuse everywhere. moat_evidence never records the
run kind itself: an identical rerun writes an identical moat_evidence (it is a SCORE_DECISION_KEYS field).

Acquired IPR&D (engine 5.6's one-time value deduction; lane default Q3 (b), main agent 2026-10-21): the charge the
engine deducted once from value is added back to EBIT in returns_on_capital and scale_economics for those fiscal
years (never when the engine judged it recurrent), in the rows' own money unit (fundamentals.json's currency; USD on
financials_history.csv), so the moat — and through it the fade — does not take it twice; the IPRD_CHARGE_IN_WINDOW
flag and the per-year add-back stay on record. ADDBACK_IPRD is the one switch.

M6, the moat's DIRECTION sets the growth hold (L3b; Andrew 2026-10-20: "eroding moat should fade faster and vice
versa"; design 10_moat_fade, decisions 10b, lane defaults Q4-Q6). trend_test runs MOAT_EROSION and its exact mirror
MOAT_WIDENING (governing return AND margin both up by 3pp and 20% of the start, margin 2pp; gross margin, operating
margin where gross margin is not filed; fundamentals.json rows only — TREND_ROW_SOURCES). fade_trend gives the hold
a 5.7 run must run (dcf_engine.HOLD_BY_TREND, via --moat-trend): eroding 0 unless erosion_rebuttal is declared;
widening 3 only when every guard passes — a fact-backed source, returns_on_capital >= +1, plain ROIC up too when
tangible ROIC governs (acquisition goodwill shrinks the tangible base), ROA up too when ROE governs (buybacks shrink
equity), and not a commodity producer on the committed SIC (COMMODITY_SIC, the SIC-6199 contract-revenue lock; an
unknown SIC fails closed) unless business_type_reason quotes a cited cost-position fact (COST_POSITION_METRICS, 10b
OQ10) — and widening_declined is not declared; else 2. WIDENING_FROM_TROUGH (non-blocking) marks a widening from a
first-two-year return below the cost-of-capital line. moat_evidence.fade records it all with the counterfactual at
the holds that matter; on a 5.7 record with scenarios fade_sync checks the engine ran it (authoring: refused;
rebuild: gate drift, FADE_DRIFT_ON_REBUILD). An erosion_rebuttal restoring hold 2 must be anchored outside the trend
test (fade_trace_leaves trace, never anchor — every figure the hold moves included, in the record and in its saved
runs; fade_anchor_leaves are the plain-ROIC / ROA figures of the tangible-only / ROE-only erosion case); on a rebuild
it restores the hold only when the prior score already ran it as the hold-restoring field (rebuttal_unchecked).

Output from an engine release before 5.7.0 (every folder on file until its next engine run) is evaluated
report_only: mechanical pillars, flags and lint, nothing refused. A scorecard that is present is shape-checked on
any release.

CLI: python3 _system/moat_scorecard.py <T>  — read-only dry run with the 5.7 rules on, always as an AUTHORING run
(prints the evidence, the governing measure, sources and caps, every gate, lint; exit 0, or 1 on a refusal). Workers
run it before the final engine run (WORKER_SPEC step 5): what it refuses, that run refuses.
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
import quote_tokens as _qt  # noqa: E402  (L3b: the one tokenizer — a cost-position reason quotes its fact's value)
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
                  "erosion_rebuttal",
                  "widening_declined")                                   # L3b (M6): declining a measured widening
# ---- M6, the moat's direction sets the growth hold (L3b; Andrew 2026-10-20; design 10_moat_fade, decisions 10b) ----
FADE_VERSION = 1
TREND_FLAGS = {"eroding": "MOAT_EROSION", "widening": "MOAT_WIDENING"}
TROUGH_FLAG = "WIDENING_FROM_TROUGH"
TREND_EPS = 1e-12            # the trend thresholds are inclusive (a change of exactly 3.00pp passes) despite float sums
# lane default Q4 (main agent, 2026-10-21): the trend (gross margin, else operating margin) is measured on these rows
# only — fundamentals.json, the SEC enrichment; a CSV-only folder is never measured. Reading B adds
# "financials_history.csv" here (the one switch).
TREND_ROW_SOURCES = ("fundamentals.json",)
# lane default Q5 (main agent, 2026-10-21): a fade mismatch on a 5.7 REBUILD records gate drift (03c decision 6) and
# never refuses; False refuses it on rebuilds too (M6's letter), leaving the other gates on GATE_DRIFT_ON_REBUILD
FADE_DRIFT_ON_REBUILD = True
# guard 4 (10 §1.3): the committed-SIC commodity proxy (inclusive ranges) and the SIC-6199 operating lock
COMMODITY_SIC = ((1000, 1499), (2040, 2079), (2400, 2499), (2611, 2631), (2810, 2829), (2860, 2879), (2911, 2911),
                 (3310, 3369), (4412, 4424))
CRYPTO_LOCK_SIC = 6199
CONTRACT_REVENUE_PREFIX = "RevenueFromContractWithCustomer"
# 10b OQ10 (main agent, 2026-10-20): a numeric business_type_reason lifts the commodity guard only when its anchor is a
# COST-POSITION fact (a cited, non-third-party facts.json fact tagged business_type_reason whose metric is one of these
# and whose value the reason quotes); a commodity price move never counts as widening
COST_POSITION_METRICS = ("cost_curve_position", "cost_curve_percentile", "cash_cost_per_unit", "cash_cost_vs_peers",
                         "all_in_sustaining_cost", "unit_cost_lead")
# make_score's anchor rule (10 §1.4): the dcf_numbers.json paths whose figures the hold moves (the hold keys and the
# valuation outputs) leave the engine-source set of an erosion_rebuttal / commodity-exemption reason — they trace, never
# anchor
FADE_TRACE_PATHS = (("hold_years", "inputs.hold_years", "implied_irr_weighted", "implied_irr_base", "irr_bear",
                     "irr_bull", "irr_low", "irr_high", "iv_at_12", "iv_at_15", "iv_at_20", "iv_at_25", "upside_at_15",
                     "upside_at_12", "weighted", "hurdle_prices", "paths", "growth_paths", "iprd_adjustment.before",
                     "iprd_adjustment.after", "diagnostics.tv_share_at_15", "diagnostics.scenario_spread_iv15")
                    + tuple(f"scenarios.{k}.{f}" for k in ("super_bear", "bear", "base", "bull", "super_bull")
                            for f in ("iv_at_10", "iv_at_12", "iv_at_15", "iv_at_20", "iv_at_25", "irr", "hold_years")))
# [L3b review, 2026-10-21] of those, the per-year series: never an engine source (check_quotes.SKIP_KEYS), they trace
# through the path, but their values are not trace-only VALUES (an independent engine figure equal to one still
# anchors) — five scenarios x the projection years are so dense that, as values, they would refuse 32% of the 0-dp and
# 9% of the 1-dp filed-history percentages on the 34 eroding folders (r57/L3b/fix3/series_collateral.out); every other
# FADE_TRACE_PATHS figure is a trace-only value
FADE_SERIES_PATHS = ("paths", "growth_paths")
# the engine flags whose numbers the hold moves (dcf_engine main: the bear / bull IRR, the scenario IV spread, the
# terminal share of IV@15, the hold): their numbers reach the engine set through the flag string, outside any path
FADE_TRACE_FLAGS = ("TIER_BAND", "WIDE_SCENARIO_SPREAD", "HIGH_TV_SHARE", "MOAT_TREND_HOLD")
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
def rows_money_unit(folder, is_csv):
    """The money unit of the scorecard's rows: USD on financials_history.csv (the engine's rows, converted to USD by its
    FX pass); fundamentals.json's own `currency` (its one money unit, figures as filed — fundamentals.money_unit),
    USD when the file names none."""
    if is_csv:
        return "USD"
    doc = _read_json(os.path.join(folder, "fundamentals.json"))
    cur = doc.get("currency") if isinstance(doc, dict) else None
    return cur.strip().upper() if isinstance(cur, str) and cur.strip() else "USD"


def iprd_in_window(n, rows, unit="USD"):
    """[{period, amount, unit, amount_usd, filed_unit, fx_rate, pct_of_operating_income, treatment, recurrent,
    addback}] for each fiscal year of the window whose engine-recorded acquired-IPR&D charge is positive (treatment not
    none), and the {period_end: amount} add-backs (treatment one_time_value_deduction and not recurrent, ADDBACK_IPRD
    on). `unit` is the rows' money unit (rows_money_unit).
    [L3 review R4, 2026-10-21] The engine's period record is USD (dcf_engine._iprd_pick converts a non-USD fact at the
    period-end rate: expense / amount / deducted = native x fx_rate; expense_unit / cash_unit name the filed unit), but
    a 20-F filer's fundamentals.json rows are in its own currency, as filed. The add-back is therefore expressed in the
    rows' unit: the USD figure on USD rows (incl. every financials_history.csv row), the native figure (USD / fx_rate)
    on rows in the unit the charge was filed in; rows in any other unit get no add-back (amount None, unit_note) —
    the charge is still listed and flagged. It had added the USD figure to EUR rows."""
    blk = n.get("iprd_adjustment") if isinstance(n, dict) else None
    if not isinstance(blk, dict) or blk.get("treatment") in (None, "none"):
        return [], {}
    one_time = blk.get("treatment") == getattr(_engine, "IPRD_TREATMENT_ONE_TIME", "one_time_value_deduction")
    recurrent = bool(blk.get("recurrent"))
    ends = {r.get("period_end"): r for r in rows}
    unit = (unit or "USD").upper()
    out, add = [], {}
    for p in blk.get("periods") or []:
        if not isinstance(p, dict) or p.get("window") not in (None, "fy") or p.get("excluded"):
            continue
        end = p.get("period")
        usd = _fnum(p.get("deducted"))
        if usd is None:
            usd = _fnum(p.get("amount"))
        if usd is None:
            usd = _fnum(p.get("expense"))
        if not usd or usd <= 0 or end not in ends:
            continue
        rate = _fnum(p.get("fx_rate"))
        if rate is not None and rate > 0:   # converted: the figure is USD, filed in the leg's own unit
            filed = p.get("cash_unit") if p.get("amount_basis") == "cash_outflow" else p.get("expense_unit")
            filed = str(filed or "").upper() or None
        else:
            rate, filed = None, "USD"
        if unit == "USD":
            amt = usd
        elif filed == unit and rate is not None:
            amt = usd / rate
        else:
            amt = None
        oi = ends[end].get("ebit")
        do_add = bool(ADDBACK_IPRD and one_time and not recurrent and amt is not None)
        rec = {"period": end, "amount": round(amt, 2) if amt is not None else None, "unit": unit,
               "amount_usd": round(usd, 2), "filed_unit": filed, "fx_rate": rate,
               "pct_of_operating_income": _r(amt / oi) if (amt is not None and oi and oi > 0) else None,
               "treatment": blk.get("treatment"), "recurrent": recurrent, "addback": do_add}
        if amt is None:
            rec["unit_note"] = (f"the charge is recorded in USD (filed in {filed or 'an unnamed unit'}) and the rows are "
                                f"{unit}: not converted, not added back")
        out.append(rec)
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
    iprd, add = iprd_in_window(n or {}, rows, rows_money_unit(folder, is_csv)) if raw else ([], {})
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


def _trend_leg(pairs):
    """One returns leg of the trend test over [(fy, value)] in row order (03b §3.5; 03c decision 3): None when it is
    not measurable (fewer than 4 finite years, or one of the last two not finite); else the finite years' first-2 and
    last-2 averages, the change, the OLS slope over the year index and both directions at EROSION_T — down: slope < 0
    AND change <= -3pp AND <= -20% of the first-2 average; up: the exact mirror (slope > 0, >= +3pp, >= +20%). The
    bounds are inclusive (TREND_EPS)."""
    g = [v for _, v in pairs]
    fin = [(fy, v) for fy, v in pairs if v is not None and math.isfinite(v)]
    if len(fin) < 4 or any(v is None or not math.isfinite(v) for v in g[-2:]):
        return None
    gf = [v for _, v in fin]
    d = (gf[-1] + gf[-2]) / 2 - (gf[0] + gf[1]) / 2
    start = abs((gf[0] + gf[1]) / 2)
    s = _slope(gf)
    return {"values": gf, "years": [str(fy) for fy, _ in fin], "first2": (gf[0] + gf[1]) / 2,
            "last2": (gf[-1] + gf[-2]) / 2, "change": d, "slope": s,
            "down": bool(s < 0 and d <= -EROSION_T[0] + TREND_EPS and d <= -EROSION_T[1] * start + TREND_EPS),
            "up": bool(s > 0 and d >= EROSION_T[0] - TREND_EPS and d >= EROSION_T[1] * start - TREND_EPS)}


def _leg_record(leg):
    """A cross-check leg (plain ROIC, ROA) for moat_evidence.fade: {status, first2, last2, change_pp, slope, up, down,
    years} (fractions 4 dp, pp 2 dp, slope 6 dp)."""
    if leg is None:
        return {"status": "not_measured", "first2": None, "last2": None, "change_pp": None, "slope": None, "up": False,
                "down": False, "years": None}
    return {"status": "measured", "first2": _r(leg["first2"]), "last2": _r(leg["last2"]),
            "change_pp": round(leg["change"] * 100, 2), "slope": _r(leg["slope"], 6), "up": leg["up"], "down": leg["down"],
            "years": leg["years"]}


def trend_test(roc, rows, src=None):
    """The moat's DIRECTION (10 §1.1; replaces 03b's erosion test, which erosion_test() still returns): the governing
    measure's leg (_trend_leg) and a margin series (>= 4 years) — gross margin, else the filed operating margin
    (operating income / revenue, the IPR&D add-back included; 10b COVERAGE) — on fundamentals.json rows only
    (TREND_ROW_SOURCES, lane default Q4). Margin down: slope < 0 AND change <= -2pp; up: the mirror. direction =
    eroding (returns AND margin down: MOAT_EROSION), widening (both up: MOAT_WIDENING), contradicting (one up, the other
    down), flat (otherwise); None when not measured (reason csv_only | governing_not_finite | no_margin). When tangible
    ROIC governs the returns leg is also run on plain ROIC (plain_roic), when ROE governs on ROA (roa): recorded, they
    never change the direction (widening reads them as guards 3 / 3b)."""
    measure = roc.get("metric")
    out = {"status": "not_measured", "reason": None, "reason_text": None, "direction": None, "measure": measure,
           "years": None, "governing_first2": None, "governing_last2": None, "governing_change_pp": None,
           "slope_governing": None, "margin_change_pp": None, "slope_margin": None, "margin_basis": None,
           "returns_up": False, "returns_down": False, "margin_up": False, "margin_down": False,
           "plain_roic": None, "roa": None}
    if src not in TREND_ROW_SOURCES:
        return dict(out, reason="csv_only",
                    reason_text="no fundamentals.json annual rows (a CSV-only folder has no gross-margin line)")
    leg = _trend_leg([(r.get("fy"), year_value(r, measure)) for r in rows])
    if leg is None:
        return dict(out, reason="governing_not_finite",
                    reason_text="fewer than 4 finite years of the governing return, or one of the last two not finite")
    gm = [r.get("gross_margin") for r in rows if r.get("gross_margin") is not None]
    basis = "gross"
    if len(gm) < 4:
        # the filed operating margin (operating income / revenue; the IPR&D add-back included) — not the pretax EBIT
        # fallback: a filer with no operating-income line has no operating margin to trend
        gm = [r["ebit"] / r["revenue"] for r in rows if r.get("roic_basis") == "operating_income" and r.get("ebit") is not None
              and r.get("revenue") and r["revenue"] > 0]
        basis = "operating"
    if len(gm) < 4:
        return dict(out, reason="no_margin", reason_text="fewer than 4 years of gross or operating margin")
    dm = (gm[-1] + gm[-2]) / 2 - (gm[0] + gm[1]) / 2
    sm = _slope(gm)
    m_down = bool(sm < 0 and dm <= -EROSION_T[2] + TREND_EPS)
    m_up = bool(sm > 0 and dm >= EROSION_T[2] - TREND_EPS)
    r_down, r_up = leg["down"], leg["up"]
    direction = ("eroding" if r_down and m_down else "widening" if r_up and m_up else
                 "contradicting" if (r_down and m_up) or (r_up and m_down) else "flat")
    plain = roa = None
    if measure == "roic_tangible":
        plain = _leg_record(_trend_leg([(r.get("fy"), year_value(r, "roic")) for r in rows]))
    if measure == "roe":
        roa = _leg_record(_trend_leg([(r.get("fy"), r.get("roa")) for r in rows]))
    return dict(out, status="measured", direction=direction, years=leg["years"],
                governing_first2=_r(leg["first2"]), governing_last2=_r(leg["last2"]),
                governing_change_pp=round(leg["change"] * 100, 2), slope_governing=_r(leg["slope"], 6),
                margin_change_pp=round(dm * 100, 2), slope_margin=_r(sm, 6), margin_basis=basis,
                returns_up=r_up, returns_down=r_down, margin_up=m_up, margin_down=m_down, plain_roic=plain, roa=roa)


def erosion_view(tt):
    """moat_evidence.erosion_test — 03b's shape (unchanged since L3, the fields G6 and its tests read) plus the trend's
    `direction`; fired = direction eroding."""
    out = {"status": "not_measured", "fired": False, "governing_change_pp": None, "margin_change_pp": None,
           "margin_basis": None, "slope_governing": None, "slope_margin": None, "reason": None}
    if tt["status"] != "measured":
        return dict(out, reason=tt["reason_text"], direction=None)
    return dict(out, status="measured", fired=tt["direction"] == "eroding", governing_change_pp=tt["governing_change_pp"],
                margin_change_pp=tt["margin_change_pp"], margin_basis=tt["margin_basis"],
                slope_governing=tt["slope_governing"], slope_margin=tt["slope_margin"],
                governing_first2=tt["governing_first2"], governing_last2=tt["governing_last2"], direction=tt["direction"])


def erosion_test(roc, rows, src=None):
    """MOAT_EROSION (03b §3.5; 03c decision 3): the governing measure's finite yearly values (>= 4, both of the last two
    finite) and a margin series (>= 4): gross margin, else operating margin (EBIT / revenue, the IPR&D add-back
    included) — the operating fallback on fundamentals.json rows only (10b COVERAGE, lane default Q4: a CSV-only folder
    is never measured). Returns down: OLS slope < 0 AND the last-2 minus first-2 average <= -3pp AND <= -20% of the
    first-2 average; margin down: slope < 0 AND change <= -2pp. Fired = both. Since L3b the wrapper of trend_test:
    03b's shape plus `direction`."""
    return erosion_view(trend_test(roc, rows, src))


# ---------------------------------------------------------------------------
# M6: the moat's direction sets the growth hold (L3b; Andrew 2026-10-20 "eroding moat should fade faster and vice
# versa"; design 10_moat_fade, decisions 10b; lane defaults Q4-Q6). The engine owns the trend -> hold map
# (dcf_engine.HOLD_BY_TREND); this module owns the trend (fade_trend), make_score checks the engine ran it.
# ---------------------------------------------------------------------------
def _sic_int(sic):
    try:
        return int(str(sic).strip())
    except (TypeError, ValueError):
        return None


def _span(years, a, b):
    """'FY2021-22' for two fiscal-year labels."""
    return f"FY{years[a]}-{str(years[b])[-2:]}" if years and len(years) >= 2 else "FY?"


def _leg_text(name, rec, why_governs, gov_pp, tail):
    if not rec or rec.get("status") != "measured":
        return (f"{name} not measured (fewer than 4 finite years, or one of the last two not finite) while {why_governs} "
                f"governs — {tail}")
    y = rec.get("years") or []
    return (f"{name} {rec['change_pp']:+.2f}pp ({_span(y, 0, 1)} avg {_pct(rec['first2'])} -> {_span(y, -2, -1)} avg "
            f"{_pct(rec['last2'])}) does not pass the widening thresholds while {why_governs} governs ({gov_pp:+.2f}pp) — "
            f"{tail}")


def cost_position_anchor(reason, facts):
    """10b OQ10: the id of the cited cost-position fact that anchors a commodity-guard exemption — kind not
    third_party (a calc fact carries its weakest operand's kind), used_for lists business_type_reason, metric in
    COST_POSITION_METRICS, and a number in the reason equals its value at the quoted precision — else None."""
    if not isinstance(reason, str) or not DIGIT.search(reason) or not facts:
        return None
    toks = _qt.numbers(reason)
    for fid in _facts.parse_refs(reason):
        f = facts.get(fid)
        if (not isinstance(f, dict) or f.get("kind") == "third_party" or f.get("metric") not in COST_POSITION_METRICS
                or "business_type_reason" not in (f.get("used_for") or [])):
            continue
        vs = _qt.ValueSet()
        for v in (f.get("value") if isinstance(f.get("value"), list) else [f.get("value")]):
            if _fnum(v) is not None:
                vs.add(_fnum(v))
        if any(vs.match(t) for t in toks):
            return fid
    return None


def commodity_guard(btype, sic, last_row, reason, facts=None):
    """Guard 4 (10 §1.3, mechanical on committed SEC data; no universe.csv): fails when (a) the declared business type
    is commodity_producer, (b) the filer's SIC is in COMMODITY_SIC, (c) the SIC-6199 operating lock fires (SIC 6199 and
    the latest fundamentals.json annual row's revenue_basis an ASC 606 contract-revenue tag), or (d) no SIC is known
    (fails closed). (b)-(d) are lifted only by a business_type_reason anchored on a cited cost-position fact
    (cost_position_anchor; 10b OQ10). Returns the guards.commodity_sic block (detail: the failure text, else None)."""
    s = _sic_int(sic)
    rb = last_row.get("revenue_basis") if isinstance(last_row, dict) else None
    out = {"sic": str(s) if s is not None else None, "basis": None, "revenue_basis": None, "exempted_by_reason": False,
           "exempt_fact": None, "passes": True, "detail": None}
    lift = ("business_type_reason must carry a cost-position number (cost-curve position or cash cost per unit vs peers) "
            "from a cited non-third-party fact tagged business_type_reason to lift this guard")
    if btype == "commodity_producer":
        return dict(out, basis="declared", passes=False,
                    detail="business type commodity_producer declared — a commodity price upcycle is not a widening moat")
    if s is None:
        basis, why = "sic_unknown", ("SIC unknown (no sector_model.sic and no profile SIC): the commodity guard fails "
                                     f"closed; {lift.replace('this guard', 'it')}")
    elif any(lo <= s <= hi for lo, hi in COMMODITY_SIC):
        basis, why = "sic", (f"commodity SIC {s}, declared {btype or 'no business type'} — a commodity price upcycle is not "
                             f"a widening moat; {lift}")
    elif s == CRYPTO_LOCK_SIC and isinstance(rb, str) and rb.startswith(CONTRACT_REVENUE_PREFIX):
        fy = str((last_row or {}).get("fy") or str((last_row or {}).get("period_end") or "")[:4])
        out["revenue_basis"] = rb
        basis, why = "sic_6199_operating", (f"SIC 6199 with contract revenue ({rb}, FY{fy}): an operating business filed "
                                            "under finance services whose revenue is priced off a token or commodity — a "
                                            f"price upcycle is not a widening moat; {lift}")
    else:
        return out
    fid = cost_position_anchor(reason, facts)
    if fid:
        return dict(out, basis=basis, exempted_by_reason=True, exempt_fact=fid)
    return dict(out, basis=basis, passes=False, detail=why)


def _widening_guards(tt, roc, sources, btype, tbasis, sic, last_row, sc, facts, strict):
    """The ruled widening guards (10 §1.3), each mechanical: 1 a fact-backed source (facts / facts_and_metrics, not
    third-party only; None — unknown — on output older than 5.7, which declares no sources), 2 returns_on_capital >= +1
    measured, 3 plain ROIC up when tangible ROIC governs, 3b ROA up when ROE governs, 4 the commodity guard. `failed`
    names each failing guard."""
    failed = []
    fbs = src_name = None
    if strict:
        fb = [s for s in sources or [] if s.get("support") in ("facts", "facts_and_metrics") and not s.get("third_party_only")]
        fbs = bool(fb)
        src_name = f"{fb[0]['type']}/{fb[0]['subtype']}" if fb else None
        if not fbs:
            failed.append("no fact-backed source (a moat source citing facts.json ids that are not third-party only; a "
                          "metric-only source does not count)")
    rs = roc.get("score") if roc.get("status") == "measured" else None
    if rs is None or rs < 1:
        failed.append(f"returns_on_capital {_sgn(rs) if rs is not None else 'not measured'} < +1")
    pra = roa_ok = None
    if tt["measure"] == "roic_tangible":
        p = tt.get("plain_roic")
        pra = bool(p and p.get("status") == "measured" and p.get("up"))
        if not pra:
            failed.append(_leg_text("plain roic", p, "tangible roic", tt["governing_change_pp"],
                                    "widening on tangible returns alone can be acquisition goodwill shrinking the "
                                    "tangible base (03c decision 2)"))
    if tt["measure"] == "roe":
        p = tt.get("roa")
        roa_ok = bool(p and p.get("status") == "measured" and p.get("up"))
        if not roa_ok:
            failed.append(_leg_text("roa", p, "roe", tt["governing_change_pp"],
                                    "ROE rising on a shrinking equity base can be buybacks, not a widening moat"))
    cg = commodity_guard(btype, sic, last_row, (sc or {}).get("business_type_reason"), facts)
    if not cg["passes"]:
        failed.append(cg["detail"])
    return {"applies": True, "fact_backed_source": fbs, "source": src_name, "returns_on_capital": rs,
            "plain_roic_agrees": pra, "roa_agrees": roa_ok, "commodity_sic": cg, "business_type": btype,
            "business_type_basis": tbasis, "failed": failed}


def _record_g0s(n):
    """The five scenario start rates of record n (the engine's clamp of g_base + offset; else the recorded g_start),
    or None."""
    inp = n.get("inputs") if isinstance(n.get("inputs"), dict) else {}
    try:
        gb = float(n["g_base"])
        return [max(_engine.GROWTH_FLOOR_START, min(_engine.GROWTH_CAP_START, gb + float(inp["offsets"][i])))
                for i in range(len(_engine.SCENARIO_LABELS))]
    except (KeyError, TypeError, ValueError, IndexError):
        pass
    scn = n.get("scenarios") if isinstance(n.get("scenarios"), dict) else {}
    try:
        return [float(scn[k]["g_start"]) for k in _engine.SCENARIO_LABELS]
    except (KeyError, TypeError, ValueError):
        return None


def engine_trend(n):
    """moat_evidence.fade.engine: the trend and hold the engine RECORDED — {moat_trend (None when the record names none,
    i.e. every pre-5.7 record: the default stable), hold_years (dcf_engine.recorded_hold_years: 2 absent, None
    malformed), source inputs | default}."""
    inp = n.get("inputs") if isinstance(n.get("inputs"), dict) else {}
    if "moat_trend" in inp:
        return {"moat_trend": inp["moat_trend"], "hold_years": _engine.recorded_hold_years(n), "source": "inputs"}
    return {"moat_trend": n.get("moat_trend"), "hold_years": _engine.recorded_hold_years(n),
            "source": "record" if n.get("moat_trend") is not None else "default"}


def fade_counterfactual(n, holds, report_only=False):
    """moat_evidence.fade.counterfactual (10 §5.5, no engine spawn): the record replayed at each hold in `holds` with the
    engine's own functions — dcf_engine.replay_paths(n, hold=h) (the record's hold_rule), adjusted_irr / adjusted_value
    with its acquired-IPR&D charge, tier_for_irr — [{hold_years, irr_weighted (4 dp), iv_at_15 (2 dp),
    tier_by_numbers, report_only}]; a record that cannot replay gets nulls and a note. Never feeds a tier, a gate or an
    alert."""
    out = []
    for h in holds:
        e = {"hold_years": h, "irr_weighted": None, "iv_at_15": None, "tier_by_numbers": None, "report_only": bool(report_only)}
        try:
            paths, _ = _engine.replay_paths(n, hold=h)
            price = float(n.get("price"))
            inp = n.get("inputs") if isinstance(n.get("inputs"), dict) else {}
            gterm = inp.get("g_terminal", n.get("g_terminal", _engine.DEFAULT_GTERM))
            if paths and paths.get("weighted"):
                c = _engine.iprd_charge_per_share(n)
                irr = _engine.adjusted_irr(paths["weighted"], price, gterm, c)[0]
                iv = _engine.adjusted_value(paths["weighted"], 0.15, gterm, c)
                e.update(irr_weighted=_r(irr), iv_at_15=round(iv, 2) if math.isfinite(iv) else None,
                         tier_by_numbers=_engine.tier_for_irr(irr))
            else:
                e["note"] = "not replayable from the record's inputs"
        except (TypeError, ValueError):
            e["note"] = "not replayable from the record's inputs"
        out.append(e)
    return out


def fade_trend(tt, roc, sources, btype, tbasis, sic, last_row, sc, facts, n, is_57, assume_projection=False,
               rebuttal_checked=True):
    """moat_evidence.fade (10 §6.3): the direction, the guards and the hold a 5.7 run must run, computed from the trend
    test (tt), the governing pillar, the counted sources, the business type, the committed SIC and latest annual row,
    the two declarations (erosion_rebuttal, widening_declined) and the engine record n. Pure, never refuses (the sync
    is fade_sync's). Rules (10 §1.2): eroding -> hold 0 unless erosion_rebuttal is declared (stable, 2); widening -> 3
    only when every guard passes and widening_declined is not declared; contradicting / flat / not measured -> 2. On
    output older than 5.7 the direction and the would-be hold are reported (rule report_only); on a record without
    scenarios (Tier F) the hold changes nothing (rule no_projection). assume_projection: the dry run, before the final
    engine run, always names the trend the final run must pass.
    rebuttal_checked=False [L3b review, 2026-10-21]: a REBUILD whose prior score did not already run the rebuttal as
    the hold-restoring influence field (its fade rule was not eroding_rebutted — the rebuttal was unused when it was
    authored, and a rebuild skips the influence checks): a declared rebuttal restores no hold — rule
    eroding_not_rebutted with rebuttal_declared true (rebuttal_unchecked(fade)), so the sync records the drift."""
    n = n if isinstance(n, dict) else {}
    sc = sc if isinstance(sc, dict) else {}
    has_proj = bool(n.get("scenarios")) or bool(assume_projection)
    reb, dec = sc.get("erosion_rebuttal"), sc.get("widening_declined")
    reb_on = isinstance(reb, str) and bool(reb.strip())
    dec_on = isinstance(dec, str) and bool(dec.strip())
    d = tt.get("direction")
    if d == "widening":
        guards = _widening_guards(tt, roc, sources, btype, tbasis, sic, last_row, sc, facts, is_57)
    else:
        guards = {"applies": False, "fact_backed_source": None, "source": None, "returns_on_capital": None,
                  "plain_roic_agrees": None, "roa_agrees": None, "commodity_sic": None, "business_type": btype,
                  "business_type_basis": tbasis, "failed": []}
    if not is_57:
        rule = "report_only"
    elif not has_proj:
        rule = "no_projection"
    elif tt.get("status") != "measured":
        rule = "not_measured"
    elif d == "eroding":
        rule = "eroding_rebutted" if reb_on and rebuttal_checked else "eroding_not_rebutted"
    elif d == "widening":
        rule = "widening_guard_failed" if guards["failed"] else "widening_declined" if dec_on else "widening_confirmed"
    elif d == "contradicting":
        rule = "contradicting"
    else:
        rule = "no_trend"
    if rule in ("report_only", "no_projection"):
        trend = hold = None
    else:
        trend = {"eroding_not_rebutted": "eroding", "widening_confirmed": "widening"}.get(rule, "stable")
        hold = _engine.HOLD_BY_TREND[trend]
    eng = engine_trend(n)
    flags, trough = [], None
    line = COST_OF_CAPITAL_LINE.get(roc.get("ladder") or "default", COST_OF_CAPITAL_LINE["default"])
    if d == "widening" and tt.get("governing_first2") is not None and tt["governing_first2"] < line:
        flags.append(TROUGH_FLAG)
        trough = {"governing_first2": tt["governing_first2"], "line": line}
    holds = set()
    if has_proj:
        if rule == "report_only":
            holds |= {0} if d == "eroding" else {3} if d == "widening" else set()
        elif rule != "no_projection":
            if eng["hold_years"] != _engine.HOLD_YEARS:
                holds.add(_engine.HOLD_YEARS)
            if rule == "eroding_rebutted":
                holds.add(_engine.HOLD_BY_TREND["eroding"])
            if rule in ("widening_declined", "widening_guard_failed"):
                holds.add(_engine.HOLD_BY_TREND["widening"])
            if hold is not None:
                holds.add(hold)
        holds.discard(eng["hold_years"])
    cf = fade_counterfactual(n, sorted(holds), report_only=rule == "report_only") if holds else []
    return {"version": FADE_VERSION, "status": tt.get("status"), "reason": tt.get("reason"), "direction": d,
            "measure": tt.get("measure"), "years": tt.get("years"),
            "governing_first2": tt.get("governing_first2"), "governing_last2": tt.get("governing_last2"),
            "governing_change_pp": tt.get("governing_change_pp"), "slope_governing": tt.get("slope_governing"),
            "margin_change_pp": tt.get("margin_change_pp"), "slope_margin": tt.get("slope_margin"),
            "margin_basis": tt.get("margin_basis"),
            "trend": trend, "hold_years": hold, "rule": rule,
            "plain_roic": tt.get("plain_roic"), "roa": tt.get("roa"), "guards": guards,
            "rebuttal_declared": reb_on, "rebuttal_unused": bool(reb_on and d != "eroding"),
            "decline_declared": dec_on, "decline_unused": bool(dec_on and d != "widening"),
            "flags": flags, "trough": trough, "engine": eng, "in_sync": None, "counterfactual": cf}


RULE_TEXT = {"eroding_not_rebutted": "eroding, erosion_rebuttal not declared",
             "eroding_rebutted": "eroding, erosion_rebuttal declared",
             "widening_confirmed": "widening, all guards pass",
             "widening_declined": "widening, widening declined in judgment.json",
             "contradicting": "contradicting: returns and margin move in opposite directions",
             "no_trend": "no trend", "not_measured": "not measured"}
UNCHECKED_TEXT = ("eroding, erosion_rebuttal declared but never checked (it was declared while no erosion was measured, "
                  "and a rebuild skips the influence checks)")


def rebuttal_unchecked(f):
    """[L3b review, 2026-10-21] True when a declared erosion_rebuttal restores no hold because no run has checked it
    (fade_trend's rebuttal_checked=False on a rebuild): rule eroding_not_rebutted with rebuttal_declared — the one
    case where a declared rebuttal leaves the erosion unrebutted."""
    f = f if isinstance(f, dict) else {}
    return f.get("rule") == "eroding_not_rebutted" and bool(f.get("rebuttal_declared"))


def _measured_clause(f):
    """'governing roic -6.40pp FY2021-22 -> FY2024-25, gross margin -3.10pp' (generated numbers only)."""
    if f.get("status") != "measured":
        return f"not measured: {f.get('reason')}"
    y = f.get("years") or []
    return (f"governing {f.get('measure')} {f['governing_change_pp']:+.2f}pp {_span(y, 0, 1)} -> {_span(y, -2, -1)}, "
            f"{f.get('margin_basis')} margin {f['margin_change_pp']:+.2f}pp")


def fade_sync(fade, n):
    """(in_sync, detail, malformed) — make_score's check that the engine ran the trend the trend test gives, called only
    on a record WITH scenarios (10 §5.2). The record's own consistency first (malformed: refused on every run): its
    moat_trend (absent = stable) is a trend, inputs.hold_years a valid hold paired with it (HOLD_BY_TREND), every
    per-scenario hold the run's hold or 2 (dcf_engine.recorded_scenario_holds). It never re-derives the per-scenario
    holds from today's fade_hold: the record is the source of truth. Then the recorded trend / hold against fade.trend
    / fade.hold_years (detail: the authoring refusal text)."""
    eng = engine_trend(n)
    et = eng["moat_trend"] if eng["moat_trend"] is not None else "stable"
    if et not in _engine.MOAT_TRENDS:
        return False, (f"dcf_numbers.json records moat_trend {et!r}, not one of {', '.join(_engine.MOAT_TRENDS)} — rerun "
                       "the engine"), True
    h = eng["hold_years"]
    if h is None:
        return False, (f"dcf_numbers.json inputs.hold_years {(n.get('inputs') or {}).get('hold_years')!r} is not a whole "
                       f"number of years 0-{_engine.PROJECTION_YEARS} — rerun the engine"), True
    if h != _engine.HOLD_BY_TREND[et]:
        return False, (f"dcf_numbers.json records moat_trend {et} with hold_years {h} — the engine pairs {et} with "
                       f"{_engine.HOLD_BY_TREND[et]}; rerun the engine"), True
    inp = n.get("inputs") if isinstance(n.get("inputs"), dict) else {}
    gterm = inp.get("g_terminal", n.get("g_terminal", _engine.DEFAULT_GTERM))
    if _engine.recorded_scenario_holds(n, _record_g0s(n) or [], gterm) is None:
        scn = n.get("scenarios") or {}
        for k in _engine.SCENARIO_LABELS:
            v = (scn.get(k) if isinstance(scn.get(k), dict) else {}).get("hold_years", _engine._MISSING)
            if v is _engine._MISSING:
                return False, (f"dcf_numbers.json scenarios.{k} records no hold_years while other scenarios do — rerun "
                               "the engine"), True
            if not _engine._valid_hold(v) or v not in (h, _engine.HOLD_YEARS):
                return False, (f"dcf_numbers.json scenarios.{k}.hold_years {v!r} is neither the run's hold {h} nor the "
                               f"default {_engine.HOLD_YEARS} — rerun the engine"), True
        return False, "dcf_numbers.json per-scenario holds do not replay — rerun the engine", True
    if et == fade.get("trend") and h == fade.get("hold_years"):
        return True, None, False
    want, rule = fade.get("trend"), fade.get("rule")
    head = f"moat fade: make_score's trend test says {want} ("
    if rebuttal_unchecked(fade):
        head += (f"{_measured_clause(fade)}; the erosion_rebuttal was declared while no erosion was measured and no run "
                 "has checked it")
        tail = (" — rerun the final pass: an authoring run checks moat_scorecard.erosion_rebuttal (a traced number "
                "anchored outside the trend test), or remove it and run --moat-trend eroding")
    elif rule == "eroding_not_rebutted":
        head += f"{_measured_clause(fade)}; no erosion_rebuttal"
        tail = (" — rerun the final pass with --moat-trend eroding, or declare moat_scorecard.erosion_rebuttal carrying a "
                "traced number")
    elif rule == "widening_confirmed":
        head += f"{_measured_clause(fade)}; all guards pass"
        tail = " — rerun the final pass with --moat-trend widening, or declare moat_scorecard.widening_declined"
    else:
        why = RULE_TEXT.get(rule, rule)
        if rule == "widening_guard_failed":
            why = "widening guard failed: " + "; ".join((fade.get("guards") or {}).get("failed") or [])
        elif rule in ("no_trend", "not_measured", "contradicting"):
            why = f"{why}: {_measured_clause(fade)}" if rule != "not_measured" else _measured_clause(fade)
        head += why
        tail = f" — rerun the final pass with --moat-trend {want}"
    return False, (f"{head}) -> --moat-trend {want} (growth hold {fade.get('hold_years')} years), but the engine ran "
                   f"--moat-trend {et} (hold {h}){tail}"), False


def fade_drift_detail(fade, n):
    """The gate_drift entry's text when a REBUILD finds the engine's trend out of date (data moved since the run)."""
    eng = engine_trend(n)
    et = eng["moat_trend"] if eng["moat_trend"] is not None else "stable"
    head = (f"engine ran {et} (hold {eng['hold_years']}); the trend computed now is {fade.get('trend')} "
            f"({fade.get('rule')}: {_measured_clause(fade)}) — data moved since the engine run")
    if rebuttal_unchecked(fade):   # [L3b review, 2026-10-21]
        return (head + "; the erosion_rebuttal, declared while no erosion was measured, has never been checked (a rebuild "
                "skips the influence checks), so it restores no hold here — the next authoring run checks it (a traced "
                "number anchored outside the trend test keeps --moat-trend stable) or passes --moat-trend eroding")
    return head + f"; the next engine run passes --moat-trend {fade.get('trend')}"


def _pp_forms(x):
    """A pp figure as a reason may quote it: the number and the fraction (a '-6.40pp' / '6.40%' token matches 100 x v)."""
    return [] if x is None else [x, x / 100.0]


def fade_anchor_leaves(ev):
    """10 §1.4 anchor (c): the plain-ROIC figures (first2, last2, change) in the TANGIBLE-ONLY erosion case (tangible
    ROIC governs, the direction is eroding, plain ROIC measured and not down — DD / HSY) and the ROA figures in the
    matching ROE-only case; [] otherwise."""
    f = (ev or {}).get("fade") or {}
    if f.get("direction") != "eroding":
        return []
    leg = f.get("plain_roic") if f.get("measure") == "roic_tangible" else f.get("roa") if f.get("measure") == "roe" else None
    if not leg or leg.get("status") != "measured" or leg.get("down"):
        return []
    return [v for v in [leg.get("first2"), leg.get("last2")] + _pp_forms(leg.get("change_pp")) if v is not None]


def _at(obj, path):
    """The value at dotted path `path` of a JSON object, or None (check_quotes.path_value's rule)."""
    cur = obj
    for k in str(path).split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _nums(x):
    """Every finite number in x (a number, a list or a dict, at any depth; bools excluded)."""
    if isinstance(x, bool) or x is None:
        return []
    if isinstance(x, (int, float)):
        return [float(x)] if math.isfinite(x) else []
    if isinstance(x, dict):
        return [v for y in x.values() for v in _nums(y)]
    if isinstance(x, list):
        return [v for y in x for v in _nums(y)]
    return []


def hold_moved_values(rec):
    """[L3b review, 2026-10-21] The figures of engine record `rec` that the growth hold moves and that reach a reason's
    engine set (check_quotes.engine_sources) OUTSIDE FADE_TRACE_PATHS: check_quotes.derived_values' price / IV@15 and
    its premium / discount, and the numbers inside the FADE_TRACE_FLAGS flag strings (TIER_BAND's bear / bull IRR,
    WIDE_SCENARIO_SPREAD's IV ratio, HIGH_TV_SHARE's terminal share), as plain values (a percent as its fraction)."""
    rec = rec if isinstance(rec, dict) else {}
    out = []
    p, iv = rec.get("price"), rec.get("iv_at_15")
    if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (p, iv)) and iv:
        out += [p / iv, p / iv - 1.0]
    for fl in rec.get("fragility_flags") or []:
        if isinstance(fl, str) and fl.split(":", 1)[0].strip() in FADE_TRACE_FLAGS:
            for t in _qt.numbers(fl):
                out.append(t.v / 100.0 if t.kind in ("pct", "pp") else t.v / 1e4 if t.kind == "bps" else t.val)
    return [float(v) for v in out if isinstance(v, (int, float)) and math.isfinite(v)]


def fade_trace_leaves(ev, n=None, saved=()):
    """make_score.check_influence's trace_only for an erosion_rebuttal / commodity-exemption reason (10 §1.4, §(l)):
    {"values": the trend block's own figures (the governing first-2 / last-2 averages and change, the margin change,
    both slopes, in moat_evidence.fade and .erosion_test), the EROSION_T thresholds, the three holds, the plain-ROIC /
    ROA figures outside the anchor case and every counterfactual figure; "paths": FADE_TRACE_PATHS — the record's hold
    keys and valuation outputs}. A number matching them traces (quoting the measurement beside the evidence is not
    refused as untraced) but never anchors.
    [L3b review, 2026-10-21] Every figure the hold moves is a trace-only VALUE too (10 §1.4: the implied IRRs, the
    weighted and per-scenario IV / IRR and the tier figures trace but never anchor), so an engine leaf with the same
    value no longer anchors it: n, the scored record — its figures at FADE_TRACE_PATHS (not the per-year
    FADE_SERIES_PATHS, which only trace) and hold_moved_values(n); saved, the verified saved runs
    (dcf_numbers_<label>.json) the reason's engine set reads — every such figure where the saved run differs from n
    (a preliminary run at another hold: its IRR and IVs stay in the engine set, check_quotes.engine_sources dropping a
    saved run's path only where it repeats n's) and hold_moved_values(saved run)."""
    ev = ev or {}
    f, e = ev.get("fade") or {}, ev.get("erosion_test") or {}
    vals = []
    for blk in (f, e):
        vals += [blk.get(k) for k in ("governing_first2", "governing_last2", "slope_governing", "slope_margin")]
        vals += _pp_forms(blk.get("governing_change_pp")) + _pp_forms(blk.get("margin_change_pp"))
    vals += list(EROSION_T) + [x * 100 for x in EROSION_T] + sorted(set(_engine.HOLD_BY_TREND.values()))
    anchors = fade_anchor_leaves(ev)
    for k in ("plain_roic", "roa"):
        leg = f.get(k) or {}
        if leg.get("status") == "measured" and not anchors:
            vals += [leg.get("first2"), leg.get("last2"), leg.get("slope")] + _pp_forms(leg.get("change_pp"))
    for c in f.get("counterfactual") or []:
        vals += [c.get("irr_weighted"), c.get("iv_at_15"), c.get("hold_years")]
    if isinstance(n, dict):
        for p in FADE_TRACE_PATHS:
            if p not in FADE_SERIES_PATHS:
                vals += _nums(_at(n, p))
        vals += hold_moved_values(n)
    for rec in saved or ():
        if isinstance(rec, dict):
            for p in FADE_TRACE_PATHS:
                v = _at(rec, p)
                if p not in FADE_SERIES_PATHS and v is not None and v != _at(n, p):
                    vals += _nums(v)
            vals += hold_moved_values(rec)
    vals = [float(v) for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]
    return {"values": vals, "paths": list(FADE_TRACE_PATHS)}


def fade_extra_leaves(ev, trace=None):
    """check_influence's `extra` (the anchors moat_evidence supplies) for an erosion_rebuttal / commodity-exemption
    reason: every number of moat_evidence OUTSIDE the trend block (numeric_leaves without fade and erosion_test), minus
    any value equal to a trace-only figure (a value the trend block shares never anchors), plus fade_anchor_leaves.
    trace: the trace-only values to filter against (default fade_trace_leaves(ev)'s; make_score passes the full set,
    the record's hold-moved figures included)."""
    trace = [abs(w) for w in (fade_trace_leaves(ev)["values"] if trace is None else trace)]
    # signs are ignored the way quote matching ignores them (quote_tokens.ValueSet)
    out = [v for v in numeric_leaves(ev, exclude=("fade", "erosion_test"))
           if not any(abs(abs(v) - w) <= 1e-9 * max(1.0, w) for w in trace)]
    return out + fade_anchor_leaves(ev)


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


ROW_REVENUE = "total revenue (annual rows)"


def volume_price(vp, rows, ctx, gate=None):
    """The users x revenue-per-user decomposition (03 §3.4). gate(name, msg, data_driven): [L3 review R5] in levels
    mode on the annual rows' revenue (no revenue_facts) the alignment depends on measured data, so too few aligned
    periods goes through the gate (drift on a rebuild: returns None, no bounds checked); every other refusal here is
    the declaration's and refuses everywhere."""
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
            rsrc = ROW_REVENUE
            rv = [(datetime.date.fromisoformat(r["period_end"]), r["revenue"]) for r in rows
                  if r.get("period_end") and r.get("revenue")]
            aligned = []
            for p, v in pts:
                d = datetime.date.fromisoformat(p)
                m = [rr for dd, rr in rv if abs((dd - d).days) <= 10]
                if m:
                    aligned.append((p, v, m[0]))
        if len(aligned) < SERIES_MIN_PERIODS or any(v <= 0 or r <= 0 for _, v, r in aligned):
            msg = (f"{where}: {len(aligned)} volume period(s) align with a fiscal-year revenue (period end within "
                   f"10 days); at least {SERIES_MIN_PERIODS} positive values needed")
            if gate is None or rsrc != ROW_REVENUE:
                raise MoatRefusal(msg)
            gate("volume_price", msg, True)
            return None
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


def check_bounds(vpres, pillars, gate=None):
    """The decomposition's class bounds pricing_power and reach_and_growth. A declared-N/A pillar beside it refuses
    everywhere. [L3 review R5] A score outside the bounds refuses through gate(name, msg, data_driven) — data-driven
    when the revenue is the annual rows' (no revenue_facts: a restated revenue moves the class, so a rebuild records
    drift), the declaration's own otherwise (declared revenue facts or growth rates: refused everywhere)."""
    b, errs, vals, decl_errs = vpres["bounds"], [], {}, 0
    for k in ("pricing_power", "reach_and_growth"):
        pe = pillars.get(k) or {}
        if pe.get("status") == "not_applicable":
            errs.append(f"{k} cannot be not applicable when a volume x price decomposition is declared")
            decl_errs += 1
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
        msg = (f"moat_scorecard: the volume x price decomposition ({vpres['volume_metric']}: volume CAGR "
               f"{vpres['volume_cagr'] * 100:+.2f}%, revenue per unit CAGR {vpres['price_cagr'] * 100:+.2f}% vs "
               f"hurdle {vpres['inflation_hurdle'] * 100:.2f}% -> {vpres['class']}) bounds the scores: " + "; ".join(errs))
        if decl_errs or gate is None:
            raise MoatRefusal(msg)
        gate("volume_price", msg, vpres.get("revenue_source") == ROW_REVENUE)


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


def numeric_leaves(ev, exclude=("fade",)):
    """Every number in moat_evidence (bools excluded) — the engine-source set a moat reason's numbers may trace to
    (make_score.check_influence extra=...): a low-ROIC reason quoting the tangible ROIC, the industry median or the
    supporting adjustment traces. L3b (10 §1.4): never the `fade` block (its trend figures and counterfactual IRRs are
    trace-only, fade_trace_leaves); `exclude` names the top-level keys left out."""
    out = []
    if isinstance(ev, dict) and exclude:
        ev = {k: v for k, v in ev.items() if k not in exclude}

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


def run_kind(folder, n, j, is_57, prior):
    """"authoring" | "rebuild" on a 5.7 run (None on older output) — the run's bookkeeping, never part of
    moat_evidence. [L3 review R1, 2026-10-21] It had been persisted as moat_evidence.run_kind, so an identical rerun
    (always a rebuild of the run before it) wrote a different moat_evidence, which is a SCORE_DECISION_KEYS field: L5's
    pr_worktree prepare reruns make_score on the sweep's committed score.json and refuses any mismatch. evaluate()
    decides drift with it; make_score skips the reasons' influence checks on a rebuild with it."""
    if not is_57:
        return None
    sc = (j or {}).get("moat_scorecard")
    decl_sha = declaration_sha256(j) if sc is not None else None
    return "rebuild" if is_rebuild(prior, n, decl_sha, facts_sha256(folder)) else "authoring"


def _declared_weight(pillars):
    """The weight of the DECLARED core pillars that count (scored with support) — the part of G2's weight a rebuild
    cannot move."""
    return round(sum(WEIGHTS[k] for k in DECLARED if (pillars.get(k) or {}).get("status") == "scored"
                     and (pillars.get(k) or {}).get("score") is not None), 2)


def _mechanical_weight_possible(btype):
    """The weight the four mechanical pillars carry when all are measured for this business type (MECH_NA excluded)."""
    return round(sum(WEIGHTS[k] for k in MECHANICAL if (btype, k) not in MECH_NA), 2)


def evaluate(folder, n, j, facts=None, is_57=False, sic=None, industry=None, prior=None, sync=True, dry_run=False):
    """score.json moat_evidence for one folder, or MoatRefusal (03b §5 order: core pillars -> core evidence ->
    supporting factors -> adjustment -> evidence -> G2 -> G1 -> sources -> G3 caps -> G4, G5, G6). facts: {id: fact}
    from facts.json; is_57: an engine-5.7 run (the gates refuse); sic: the filer's SIC; industry: load_industry();
    prior: the score.json being replaced (authoring vs rebuild: run_kind). The result depends only on the inputs (the
    declaration, facts.json, the folder's rows, the engine record, the industry file) and, through gate_drift, on
    whether a newly failing data-driven gate drifted on a rebuild (an authoring run refuses it instead) — so an
    identical rerun writes an identical moat_evidence (L3 review R1).
    L3b (M6): after the gates, `fade` (fade_trend) — and on a 5.7 run of a record WITH scenarios the fade sync
    (fade_sync): a record inconsistent with itself refuses everywhere; a recorded trend / hold other than the trend
    test's refuses an authoring run and records gate drift on a rebuild (GATE_DRIFT_ON_REBUILD and
    FADE_DRIFT_ON_REBUILD). sync=False computes the fade and skips the sync; dry_run=True (the CLI, which runs BEFORE
    the final engine run) also skips it and names the trend the final run must pass even on a record without
    scenarios."""
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
        wd = sc.get("widening_declined")   # L3b (M6, 10 §6.2): not an influence field, shape-checked on any release
        if wd is not None and not (isinstance(wd, str) and wd.strip()):
            raise MoatRefusal("moat_scorecard.widening_declined must be a non-empty string (why the measured widening is a "
                              "cycle or a recovery, not a moat widening) or null")
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
    rebuild = run_kind(folder, n, j, strict, prior) == "rebuild"
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
            vpres = volume_price(sc["volume_price"], rows, ctx, gate)
            if vpres:
                check_bounds(vpres, pillars, gate)
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
    tt = trend_test(gm, rows, src)                 # L3b (M6): the direction; erosion_test is its 03b view
    ero = erosion_view(tt)
    if ero["fired"]:
        flags.insert(0, "MOAT_EROSION")
    if tt["direction"] == "widening":
        flags.insert(0, TREND_FLAGS["widening"])
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
            # [L3 review R5] the weight counts the MECHANICAL pillars, so the floor is data-driven when the declared
            # pillars plus every mechanical pillar this type can measure would clear it (the shortfall is unmeasured
            # data: drift on a rebuild, 03c decision 6); a declaration that cannot reach 8 even then refuses everywhere
            gate("weight_floor", f"moat evidence weight {weight:g} < {MIN_EVIDENCE_WEIGHT:g}: too little of the scorecard "
                 "is measured or fact-supported to check the moat (cite facts for more pillars)",
                 _declared_weight(pillars) + _mechanical_weight_possible(bt) >= MIN_EVIDENCE_WEIGHT)
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
    # ---- L3b (M6): the moat's direction -> the growth hold, and the check that the engine ran it ----
    # [L3b review, 2026-10-21] a rebuild skips the influence checks, so a rebuttal restores the hold on a rebuild only
    # when the prior score already ran it as the hold-restoring field (rule eroding_rebutted, set only by an authoring
    # run that checked it, then carried by rebuilds); one that was unused when authored and meets a newly measured
    # erosion on a rebuild restores nothing until an authoring run checks it (fade sync drift; no registry event)
    pme = prior.get("moat_evidence") if isinstance(prior, dict) else None
    prior_fade = pme.get("fade") if isinstance(pme, dict) else None
    reb_checked = not (rebuild and not dry_run) or (isinstance(prior_fade, dict)
                                                    and prior_fade.get("rule") == "eroding_rebutted")
    fade = fade_trend(tt, gm, sources_rec.get("items") or [], bt, tbasis, sic, last_raw, sc, ctx["facts"], n, strict,
                      assume_projection=dry_run, rebuttal_checked=reb_checked)
    if TROUGH_FLAG in fade["flags"]:
        flags.insert(flags.index(TREND_FLAGS["widening"]) + 1 if TREND_FLAGS["widening"] in flags else 0, TROUGH_FLAG)
    if strict and sync and not dry_run and n.get("scenarios"):
        in_sync, detail, malformed = fade_sync(fade, n)
        fade["in_sync"] = in_sync
        if not in_sync:
            if malformed:
                raise MoatRefusal(detail)
            if rebuild and GATE_DRIFT_ON_REBUILD and FADE_DRIFT_ON_REBUILD:
                drift.append({"gate": "fade_sync", "detail": fade_drift_detail(fade, n)})
            else:
                raise MoatRefusal(detail)
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
           "erosion_test": ero, "fade": fade, "flags": flags, "gates": gates,
           "moat_divergence_reason": reasons["moat_divergence_reason"],
           "moat_lint": lint_bad_moats(j, strict),
           "industry_file": ({"built": industry.get("built"), "sha256": industry.get("_sha256")} if industry else None),
           "declaration_sha256": decl_sha, "facts_sha256": f_sha,
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


TREND_REASON_TEXT = {"csv_only": "no fundamentals.json annual rows: a CSV-only folder is not measured",
                     "governing_not_finite": "fewer than 4 finite years of the governing return, or one of the last two "
                                             "not finite",
                     "no_margin": "no gross-margin or operating-margin line in 4 of the last 5 FY"}


def _cf_text(c):
    if c.get("irr_weighted") is None:
        return f"at hold {c.get('hold_years')} the record does not replay"
    iv = f", IV@15 ${c['iv_at_15']:,.2f}" if c.get("iv_at_15") is not None else ""
    return f"at hold {c['hold_years']} the weighted IRR would be {_pct(c['irr_weighted'])} (tier {c.get('tier_by_numbers')}){iv}"


def _guard_summary(f):
    g = f.get("guards") or {}
    cg = g.get("commodity_sic") or {}
    rs = g.get("returns_on_capital")
    parts = []
    if g.get("fact_backed_source") is not None:
        parts.append("fact-backed source " + (f"yes ({g.get('source')})" if g.get("fact_backed_source") else "no"))
    parts.append(f"returns_on_capital {_sgn(rs) if rs is not None else 'not measured'}")
    for key, name, gov in (("plain_roic", "plain roic", "tangible roic"), ("roa", "roa", "roe")):
        leg = f.get(key)
        if leg is not None:
            ok = g.get("plain_roic_agrees" if key == "plain_roic" else "roa_agrees")
            parts.append((f"{name} {leg['change_pp']:+.2f}pp" if leg.get("status") == "measured" else f"{name} not measured")
                         + f" {'agrees' if ok else 'does not agree'} ({gov} governs)")
    if cg:
        parts.append(f"commodity SIC {'no' if cg.get('passes') and not cg.get('exempted_by_reason') else 'yes'}"
                     + (f" (SIC {cg.get('sic')})" if cg.get("sic") else " (SIC unknown)")
                     + (f", lifted by the cost-position fact {cg.get('exempt_fact')}" if cg.get("exempted_by_reason") else ""))
    if g.get("business_type"):
        parts.append(f"business type {g.get('business_type')}")
    return " · ".join(parts)


def fade_lines(f):
    """key_numbers.md's two M6 lines (10 §5.7): '- Trend test …' (it replaces 03b's '- Erosion test' line) and
    '- Fade direction …'. Every number is generated (quotable); no worker free text (the rebuttal and decline texts
    stay out, 07 §1.10)."""
    L = []
    d, y = f.get("direction"), f.get("years") or []
    if f.get("status") == "measured":
        res = {"eroding": "eroding (MOAT_EROSION)", "widening": "widening (MOAT_WIDENING)", "flat": "no trend"}.get(d, d)
        if d == "contradicting":
            up = (f.get("governing_change_pp") or 0) > 0
            res = (f"contradicting (returns {'up' if up else 'down'}, {f.get('margin_basis')} margin "
                   f"{'down' if up else 'up'}): stable")
        L.append(f"- Trend test (last 5 FY, governing {f.get('measure')}): {_span(y, 0, 1)} avg {_pct(f['governing_first2'])} "
                 f"-> {_span(y, -2, -1)} avg {_pct(f['governing_last2'])} ({f['governing_change_pp']:+.2f}pp, slope "
                 f"{f['slope_governing']:+.4f}/yr) · {f.get('margin_basis')} margin {f['margin_change_pp']:+.2f}pp (slope "
                 f"{f['slope_margin']:+.4f}/yr) -> {res}")
    else:
        L.append(f"- Trend test: not measured ({TREND_REASON_TEXT.get(f.get('reason'), f.get('reason'))})")
    rule = f.get("rule")
    eng = f.get("engine") or {}
    et = eng.get("moat_trend") or "stable"
    cf = "; ".join(_cf_text(c) for c in f.get("counterfactual") or [])
    if rule == "report_only":
        if d == "eroding":
            body = "eroding -> a 5.7 run holds growth 0 yrs unless rebutted; this record ran the 2-year hold"
        elif d == "widening":
            body = ("widening -> a 5.7 run holds 3 yrs only with a fact-backed source, returns_on_capital >= +1, plain roic "
                    "agreeing when tangible roic governs, roa agreeing when roe governs and no commodity SIC ("
                    + _guard_summary(f) + " today)")
        else:
            body = {"contradicting": "contradicting", "flat": "no trend"}.get(d, "not measured") + " -> a 5.7 run holds growth 2 yrs"
        L.append(f"- Fade direction (report only, pre-5.7 record): {body}" + (f" ({cf})" if cf else ""))
    elif rule == "no_projection":
        L.append(f"- Fade direction: {d or 'not measured'} (no projection: Tier F record, the hold changes nothing) · engine "
                 f"recorded --moat-trend {et}")
    else:
        head = {"widening_confirmed": "widening, guards: " + _guard_summary(f),
                "widening_guard_failed": "widening, guard failed: " + "; ".join((f.get("guards") or {}).get("failed") or []),
                "contradicting": "contradicting (stable)"}.get(rule, RULE_TEXT.get(rule, rule))
        if rebuttal_unchecked(f):
            head = UNCHECKED_TEXT
        if f.get("rebuttal_unused"):
            head += " · erosion_rebuttal declared but unused (no measured erosion)"
        if f.get("decline_unused"):
            head += " · widening_declined declared but unused (no measured widening)"
        s = f.get("in_sync")
        sync = ("in sync" if s is True else
                "OUT OF SYNC — gate drift on this rebuild (resolved at the next engine run)" if s is False else "not checked")
        L.append(f"- Fade direction: {head} -> growth hold {f.get('hold_years')} yrs · engine ran --moat-trend {et} "
                 f"(hold {eng.get('hold_years')}): {sync}" + (f" · {cf}" if cf else ""))
    return L


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
        unit = x.get("unit") or "USD"
        fy = f"FY{str(x['period'])[:4]}"
        if x.get("amount") is None:   # rows in a unit the charge was not filed in (L3 review R4): listed, not added back
            L.append(f"- Acquired IPR&D inside the window: {fy} ${x['amount_usd']:,.0f} (USD; the {unit} rows are not "
                     f"converted) — not added back (filed in {x.get('filed_unit') or 'an unnamed unit'}): returns_on_capital "
                     "and scale_economics read operating income as filed")
            continue
        how = ("added back to operating income in returns_on_capital and scale_economics (the engine deducted it once from "
               "value)" if x.get("addback") else
               "read as filed in returns_on_capital and scale_economics" + (" (judged recurrent)" if x.get("recurrent") else ""))
        amt_s = f"${x['amount']:,.0f}" if unit == "USD" else f"{x['amount']:,.0f} {unit}"
        L.append(f"- Acquired IPR&D inside the window: {fy} {amt_s}"
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
    f = me.get("fade")
    if isinstance(f, dict):   # L3b (M6): the trend test (both directions) and what the hold must be
        L += fade_lines(f)
    else:
        e = me.get("erosion_test") or {}
        if e.get("status") == "measured":
            L.append(f"- Erosion test: {'FIRED' if e.get('fired') else 'not fired'} (governing {e.get('governing_change_pp'):+.2f}pp, "
                     f"{e.get('margin_basis')} margin {e.get('margin_change_pp'):+.2f}pp over the last 5 FY)")
        else:
            L.append(f"- Erosion test: not measured ({e.get('reason')})")
    if me.get("flags"):
        tr = (f or {}).get("trough") if isinstance(f, dict) else None
        L.append("- Flags: " + ", ".join(
            (f"{x} (first-two-year governing average {_pct(tr['governing_first2'])} < {_pct(tr['line'])})"
             if x == TROUGH_FLAG and tr else x) for x in me["flags"]))
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
        # [L3 review R3, 2026-10-21] always an AUTHORING check (prior=None): the worker runs this before the final engine
        # run, which is an authoring run, so every gate that would refuse it refuses here. Passing the folder's
        # score.json had made an unchanged folder a rebuild — a failing data-driven gate was recorded as drift and the
        # dry run printed "passes the 5.7 rules"
        # [L3b, M6] sync=False: this runs BEFORE the final engine run, so the preliminary record's trend is not checked —
        # the dry run prints the --moat-trend value the final run must pass instead
        ev = evaluate(folder, n, j, facts=_facts.by_id(fdoc) if fdoc else {}, is_57=True, sic=sic,
                      industry=load_industry(os.path.join(base, "_system")), prior=None, dry_run=True)
    except MoatRefusal as e:
        print(f"moat_scorecard.py: REFUSED — {e}")
        return 1
    for line in key_numbers_lines(ev):
        print(line)
    f = ev.get("fade") or {}
    print(f"fade: {f.get('direction') or 'not measured'} ({f.get('rule')}) -> pass --moat-trend {f.get('trend')} "
          f"(growth hold {f.get('hold_years')} years)")
    if f.get("rule") == "eroding_rebutted":
        # [whole-PR review fix, 2026-10-21] the dry run applies the gates, not make_score's reason trace
        print("fade: that trend assumes make_score's trace accepts the erosion_rebuttal (a number anchored on a cited "
              "fact or an engine figure, not a restatement of the trend test) — this dry run does not trace reasons; "
              "if make_score refuses it, fix the rebuttal or drop it and pass --moat-trend eroding")
    cf = "; ".join(_cf_text(c) for c in f.get("counterfactual") or [])
    if cf:
        print(f"fade, on the preliminary run in dcf_numbers.json as it stands (engine --moat-trend "
              f"{(f.get('engine') or {}).get('moat_trend') or 'stable'}): {cf}")
    print(f"moat_scorecard.py: {t} evidence {ev.get('evidence_score')} (core {ev.get('core_evidence_score')}, supporting "
          f"{ev.get('supporting_adjustment'):+.2f}) vs moat {ev.get('moat_score'):g} — passes the 5.7 rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
