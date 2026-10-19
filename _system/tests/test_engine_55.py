#!/usr/bin/env python3
"""Engine release 5.5 tests (DESIGN_5.5 §11). Run: python _system/tests/test_engine_55.py
(or python -m pytest _system/tests). No network.

Written FROM THE DESIGN (DESIGN_5.5 v2 + Andrew's rulings of 2026-10-18), independently of the
implementation, as the specification check for engine release 5.5.0:

1. Unit tests of every new dcf_engine helper with the design's exact names and signatures
   (market_cap_est, normalized_oe_total, latest_dei_count, share_scale_check,
   scale_factor_for_cap, snap_split_ratio, split_events_post_fy, confirm_split, capex_for_period,
   reconcile_sbc, override_currency_basis, capex_coverage_low, period_series(with_filed=True)),
   fed tiny synthetic inputs built from real cached EDGAR values (copied into this file — the tests
   never read the scratchpad caches).
2. End-to-end offline runs of dcf_engine.main() / ttm.main() through engine55_harness on the gzip
   fixtures in fixtures/engine55/ (companyfacts trimmed to the tags the engine reads; every fetch
   monkeypatched). Inputs (CLI args, judgment.json, ttm.json pins) are written into each test, so the
   re-scores of the named folders on this branch do not move the expectations. Only CCJ / APP / STZ
   (not re-scored) are compared against their recorded dcf_numbers.json, guarded by the fixture's
   recorded_as_of stamp.
3. make_score.py on synthetic folders in a temp STOCKS_BASE (the style of test_queue_alert_gates).

Every test names the decision it covers in its docstring:
  Decision 1  ADS market cap (price x shares / ads_ratio) and the normalized-OE total behind
              net_debt_to_normalized_oe / HIGH_NET_DEBT / BIG_NET_CASH; make_score's pre-5.5 correction
  Decision 2  share basis: §1 share-scale guard, §2-3 split basis / dei fallback, §5 share_class_mismatch
  Decision 3  PaymentsForCapitalImprovements + the zero-guard
  Decision 4  additive capex components (roll-up authoritative)
  Decision 5  intangible capex leg (narrow piece) + CAPEX_COVERAGE_LOW
  Decision 6  SBC tag reconciliation (Allocated > Share, same unit)
  Decision 7  USD-declared overrides used verbatim
  Release     ENGINE_RELEASE 5.5.0, bit-identity of untouched folders, make_score release handling
  [ADDITION — ECHO] (after the retro-scan; not in the rulings) an intangible capex fact whose value the
              same tag also files on a >380-day context is a cumulative figure, dropped from the intangible
              leg ('cumulative_duplicate') in dcf_engine.py and ttm.py alike — synthetic ECHO-shaped fixture
              built in the test
  Verifier rounds (section 8b: round 1, rulings E1-E11; section 8c: round 2 — R2-E3 a dei the latest count
              fails leaves the leverage unverifiable, R2-CAP (withdrawn in round 3), R2-PIN test
              (a) on the pin actually used + ttm.py's denominator warning, R2-E2 the OE/share CAGR stays unless
              a break lies between its endpoints, R2-E4 a skipped cover-page zero is recorded; round 3 — R3-CAP
              the pin's cap factor needs the median year's count and the latest count on one scale, R3-SPLIT a
              split is confirmed against the latest filed count): each test fails on the code before its fix
"""
import contextlib
import copy
import hashlib
import importlib
import io
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402

E = H._engine()  # a private dcf_engine copy (neutral argv, MEASURE False) for the unit tests; each run_engine executes its own fresh copy and never touches sys.modules["dcf_engine"]
MAKE_SCORE = os.path.join(SYS, "make_score.py")

# ---------------------------------------------------------------------------
# Tag names (DESIGN §3-5) and shared texts
# ---------------------------------------------------------------------------
IF = "ifrs-full"
PRIMARY = "PaymentsToAcquirePropertyPlantAndEquipment"
EXPLORE = "PaymentsToExploreAndDevelopOilAndGasProperties"
ACQ_OG = "PaymentsToAcquireOilAndGasProperty"
OTHER_PPE = "PaymentsToAcquireOtherPropertyPlantAndEquipment"
CIP = "PaymentsForConstructionInProcess"
PRODUCTIVE = "PaymentsToAcquireProductiveAssets"
OTHER_PRODUCTIVE = "PaymentsToAcquireOtherProductiveAssets"
CAP_IMPROVEMENTS = "PaymentsForCapitalImprovements"
INTANG = "PaymentsToAcquireIntangibleAssets"
OTHER_INTANG = "PaymentsToAcquireOtherIntangibleAssets"
IFRS_PPE = "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"
IFRS_PPE2 = "PurchaseOfPropertyPlantAndEquipment"
IFRS_COMBINED = "PurchaseOfPropertyPlantAndEquipmentIntangibleAssetsOtherThanGoodwillInvestmentPropertyAndOtherNoncurrentAssets"
IFRS_INTANG = "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities"
SBC_SHARE = "ShareBasedCompensation"
SBC_ALLOC = "AllocatedShareBasedCompensationExpense"
AR_COMPONENTS = f"{EXPLORE}+{ACQ_OG}+{OTHER_PPE}"
EM = "—"  # the em dash the engine's flag texts use
FORMULA_ADS = "price × shares ÷ ads_ratio"
FORMULA_PLAIN = "price × shares"
SCALE_GAP = f"DATA_GAP:shares {EM} SHARE_SCALE"
CLASS_GAP = f"DATA_GAP:shares {EM} SHARE_CLASS_MISMATCH"

# ---------------------------------------------------------------------------
# Recorded run inputs, frozen here (from each folder's dcf_numbers.json "inputs" at fixture time)
# ---------------------------------------------------------------------------
P_DEFAULT = "0.1,0.25,0.3,0.25,0.1"
P_CONS = "0.15,0.3,0.3,0.15,0.1"
O_DEFAULT = "-0.12,-0.05,0.0,0.05,0.12"
M_DEFAULT = "0.75,0.9,1.0,1.1,1.25"


def args_for(moat, probs=P_DEFAULT, offsets=O_DEFAULT, mults=M_DEFAULT, extra=()):
    return ["--moat", str(float(moat)), "--probs", probs, "--offsets", offsets, "--mults", mults,
            "--gterm", "0.025", *extra]


AR_ARGS = args_for(5)
APA_ARGS = args_for(3, P_CONS, "-0.5,-0.42,-0.35,-0.29,-0.23", "0.5,0.75,1.0,1.1,1.25", ["--ttm"])
JLL_ARGS = args_for(5, P_CONS)
DD_ARGS = args_for(5, P_CONS, "0.0,0.05,0.1,0.14,0.19", extra=["--ttm"])
NTNX_PIN = 1.355341859271022
TEM_PIN = -3.9324392632609864
VIV_PIN = 1.2803686126106435
NTNX_ARGS = args_for(5)
TEM_ARGS = args_for(5)
VIV_ARGS = args_for(5, "0.15,0.25,0.3,0.2,0.1", "0.03,0.06,0.1,0.14,0.19")
TLK_ARGS = args_for(6)
VOD_ARGS = args_for(4, "0.15,0.3,0.3,0.18,0.07")
ATO_ARGS = args_for(6)
RBC_ARGS = args_for(6, P_DEFAULT, "-0.14,-0.08,-0.02,0.03,0.1", extra=["--ttm"])
FER_ARGS = args_for(6)
PR_ARGS = args_for(5)
WF_ARGS = args_for(3, P_CONS)
IESC_ARGS = args_for(5)
CX_ARGS = args_for(5)
ELS_ARGS = args_for(5)


def _o(value, kind="filing", **extra):
    o = {"value": value, "kind": kind, "source": "test fixture (copied from the folder's filing citation)",
         "reason": "test fixture"}
    o.update(extra)
    return o


def _ads(ratio):
    return {"ratio": ratio, "source": "test fixture (20-F/40-F cover)", "reason": "test fixture"}


JLL_J = {"capex_override": _o(215600000)}
TLK_J = {"ads_ratio": _ads(100), "sbc_override": _o(0, ack_reason="test: no filed SBC to band against"),
         "shares_override": _o(99062216600)}
PUK_J = {"ads_ratio": _ads(2.0), "sbc_override": _o(85000000)}
CX_J = {"ads_ratio": _ads(30.0), "sbc_override": _o(55000000)}
VOD_J = {"ads_ratio": _ads(10)}
CCJ_J = {"ads_ratio": _ads(1.0)}
WF_J = {"ads_ratio": _ads(3)}
APP_J = {"capex_override": _o(19000000, kind="estimate")}
STZ_J = {"shares_override": _o(175568000, ack_reason="test: no filed diluted count")}
VIV_SHARES = _o(3195606352, source="FY2025 20-F EPS note (test)", reason="test", ack_reason="test")


def fer_j(sbc_value, kind="filing", currency=None):
    sbc = _o(sbc_value, kind=kind, ack_reason="test: no filed SBC to band against")
    if currency is not None:
        sbc["currency"] = currency
    return {"ads_ratio": _ads(1.0), "capex_override": _o(187000000, ack_reason="test: no filed capex"),
            "sbc_override": sbc}


def _bo(value, **extra):
    """A declared base_override {value, source, reason} (the NTNX / TEM / VIV folders declare their pins this way;
    ruling E1: only a --base-oe-ps pin that judgment.json declares like this carries a share-scale defect)."""
    o = {"value": value, "source": "test fixture (this run's dcf_numbers.json figures, as the folder cites)",
         "reason": "test fixture"}
    o.update(extra)
    return o


NTNX_J = {"base_override": _bo(NTNX_PIN)}
TEM_J = {"base_override": _bo(TEM_PIN, kind="estimate")}


def viv_j(with_shares=True, with_base_override=True):
    j = {"ads_ratio": _ads(2)}
    if with_shares:
        j["shares_override"] = dict(VIV_SHARES)
    if with_base_override:
        j["base_override"] = _bo(VIV_PIN)
    return j


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def close(a, b, rel=1e-9, abs_=1e-6):
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=abs_)


def f(x):
    """A CSV cell as float (None when blank)."""
    if x in (None, ""):
        return None
    return float(x)


def row(rows, period):
    for r in rows:
        if r["period_end"] == period:
            return r
    raise AssertionError(f"no CSV row for {period}: {[r['period_end'] for r in rows]}")


def flags(n, prefix):
    return [x for x in (n.get("fragility_flags") or []) if str(x).startswith(prefix)]


def tagname(t):
    return t[1] if isinstance(t, (tuple, list)) else t


def dropped(res):
    """{(tag, reason)} from capex_for_period's dropped list ((tag, value, reason) tuples, tolerant of dicts)."""
    out = set()
    for d in res.get("dropped") or []:
        if isinstance(d, dict):
            out.add((d.get("tag"), d.get("reason")))
        else:
            d = tuple(d)
            out.add((d[0], d[-1]))
    return out


def fact(tag, value, filed, unit="USD"):
    """One capex_for_period input fact: (tag, value, unit, filed)."""
    return (tag, value, unit, filed)


_CACHE = {}


def _cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def run(ticker, args=(), judgment=None, ttm=None, fixture=None, patch=None):
    """dcf_engine.main() offline on the fixture, in a temp base holding ONLY the judgment.json / ttm.json
    passed here (never the repo folder's files, which this branch re-scores)."""
    fx = fixture or H.load_fixture(ticker)
    base = H.make_base(fx, judgment, ttm, copy_repo_files=False)
    return H.run_engine(ticker, args=list(args), base=base, fixture=fx, patch=patch)


def run_ttm(ticker, judgment=None, fixture=None, patch=None):
    fx = fixture or H.load_fixture(ticker)
    base = H.make_base(fx, judgment, None, copy_repo_files=False)
    return H.run_ttm(ticker, base=base, fixture=fx, patch=patch)


def recorded_matching_fixture(ticker):
    """The folder's recorded dcf_numbers.json, refusing when the folder was re-scored after the fixture
    was built (the comparison would then be against a different run)."""
    rec = H.recorded(ticker)
    fx = H.load_fixture(ticker)
    assert rec is not None, f"{ticker}: no recorded dcf_numbers.json"
    assert rec.get("as_of") == fx.get("recorded_as_of"), (
        f"{ticker} was re-scored after its fixture was built ({rec.get('as_of')} vs fixture {fx.get('recorded_as_of')}) "
        "— rebuild fixtures/engine55 with build_fixtures.py before comparing")
    return rec


LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]


def assert_same_math(n, rec, who):
    """Numerical identity on the valuation outputs (DESIGN §0: base, g_base, every scenario IV/IRR,
    weighted, tier; new keys and the content_hash differ by design)."""
    assert n.get("base_oe_per_share") == rec["base_oe_per_share"], f"{who}: base {n.get('base_oe_per_share')} vs {rec['base_oe_per_share']}"
    assert n.get("g_base") == rec["g_base"], f"{who}: g_base {n.get('g_base')} vs {rec['g_base']}"
    for lbl in LABELS:
        for k in ("iv_at_10", "iv_at_12", "iv_at_15", "irr"):
            a, b = n["scenarios"][lbl][k], rec["scenarios"][lbl][k]
            assert a == b, f"{who}: {lbl}.{k} {a} vs {b}"
    for k in ("iv_at_10", "iv_at_12", "iv_at_15", "irr"):
        assert n["weighted"][k] == rec["weighted"][k], f"{who}: weighted.{k} {n['weighted'][k]} vs {rec['weighted'][k]}"
    assert n.get("implied_irr_weighted") == rec["implied_irr_weighted"], who
    assert n.get("tier_by_numbers") == rec["tier_by_numbers"], f"{who}: tier {n.get('tier_by_numbers')} vs {rec['tier_by_numbers']}"


def recorded_rows(ticker):
    import csv
    with open(os.path.join(ROOT, ticker, "financials_history.csv"), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def nd_identity(n, ratio=None):
    """net_debt_to_normalized_oe on the decision-1 basis: net debt / (base x market-cap shares [/ ratio]);
    None when net debt is unknown (DEBT_TAGS_BLANK — NTNX), which is what the engine must record then."""
    if n.get("net_debt_latest") is None:
        return None
    shares = (n.get("market_cap_basis") or {}).get("shares_used", n.get("shares_diluted_latest"))
    tot = n["base_oe_per_share"] * shares
    if ratio:
        tot = tot / ratio
    return n["net_debt_latest"] / tot


# ===========================================================================
# 1. Release constants and shared plumbing
# ===========================================================================
def test_release_constant():
    """Release: ENGINE_RELEASE is bumped to 5.5.0 (engine_version stays 5 — checked on the CCJ run)."""
    assert E.ENGINE_RELEASE == "5.5.0", E.ENGINE_RELEASE


def test_capex_tag_lists_match_the_design():
    """Decisions 3, 4, 5: the roll-up, component, intangible and combined-tag lists exactly as DESIGN §3-5
    (PaymentsForCapitalImprovements appended; the generalized E&P components; the narrow intangible leg —
    us-gaap PaymentsToAcquire(Other)IntangibleAssets + IFRS PurchaseOfIntangibleAssets…; the IFRS combined
    PP&E+intangibles tag is the one that never takes intangibles on top)."""
    assert [tagname(t) for t in E.CAPEX_ROLLUP_TAGS] == [PRIMARY, IFRS_PPE, IFRS_PPE2, IFRS_COMBINED]
    assert E.CAPEX_ROLLUP_TAGS[0] == PRIMARY == E.PRIMARY_ROLLUP
    assert all(isinstance(t, tuple) and t[0] == IF for t in E.CAPEX_ROLLUP_TAGS[1:])
    assert list(E.CAPEX_COMPONENT_TAGS) == [EXPLORE, ACQ_OG, OTHER_PPE, CIP, PRODUCTIVE, OTHER_PRODUCTIVE, CAP_IMPROVEMENTS]
    assert [tagname(t) for t in E.CAPEX_INTANGIBLE_TAGS] == [INTANG, OTHER_INTANG, IFRS_INTANG]
    assert isinstance(E.CAPEX_INTANGIBLE_TAGS[2], tuple) and E.CAPEX_INTANGIBLE_TAGS[2][0] == IF
    assert set(E.CAPEX_COMBINED_TAGS) == {IFRS_COMBINED}


def test_period_series_keeps_its_4_tuple_and_adds_filed_dates():
    """Release (DESIGN §0): period_series keeps its 4-tuple return; with_filed=True adds a 5th dict
    {period: filed date of the fact used} (latest filing wins). AR's PaymentsToAcquireOilAndGasProperty
    FY2023 was last filed 2025-02-12 (the FY2025 10-K dropped the comparative)."""
    def e(start, end, val, fy, fp, form, filed):
        return {"start": start, "end": end, "val": val, "fy": fy, "fp": fp, "form": form, "filed": filed,
                "accn": f"0000000000-{filed}"}
    facts = {"facts": {"us-gaap": {ACQ_OG: {"units": {"USD": [
        e("2023-01-01", "2023-12-31", 151135000, 2023, "FY", "10-K", "2024-02-14"),
        e("2023-01-01", "2023-12-31", 151135000, 2024, "FY", "10-K", "2025-02-12"),
        e("2024-01-01", "2024-12-31", 90995000, 2024, "FY", "10-K", "2025-02-12"),
        e("2025-01-01", "2025-06-30", 56640000, 2025, "Q2", "10-Q", "2025-07-30")]}}}}}
    out4 = E.period_series(facts, [ACQ_OG], True)
    assert isinstance(out4, tuple) and len(out4) == 4
    assert out4[0] == {"2023-12-31": 151135000, "2024-12-31": 90995000}
    out5 = E.period_series(facts, [ACQ_OG], True, with_filed=True)
    assert len(out5) == 5 and tuple(out5[:4]) == tuple(out4)
    assert out5[4] == {"2023-12-31": "2025-02-12", "2024-12-31": "2025-02-12"}, out5[4]


# ===========================================================================
# 2. Decision 1 — ADS market cap and the normalized-OE total
# ===========================================================================
def test_market_cap_est_divides_by_the_ads_ratio():
    """Decision 1: market_cap_est(price, shares, ads_ratio) = (price x shares) / ratio — ratio 100
    (TLK: $1,092.66B -> ~$10.93B), 30 (CX ~$15.06B), 10 (VOD $405.57B -> $40.56B), 2 (VIV), and a
    fractional ratio 0.5 (one ADS = half a share: the cap doubles)."""
    M = E.market_cap_est
    assert M(11.03, 99062216600.0, 100.0) == (11.03 * 99062216600.0) / 100.0
    assert abs(M(11.03, 99062216600.0, 100.0) - 10.93e9) < 0.005e9
    assert M(10.25, 44065652000, 30.0) == (10.25 * 44065652000) / 30.0
    assert abs(M(10.25, 44065652000, 30.0) - 15.06e9) < 0.005e9
    assert M(15.51, 26149000000, 10.0) == 40557099000.0
    assert M(12.26, 3195606352, 2.0) == (12.26 * 3195606352) / 2.0
    assert M(10.0, 1000.0, 0.5) == 20000.0


def test_market_cap_est_is_bit_identical_without_a_ratio():
    """Decision 1 (ruling: 'non-ADS bit-identical'): ratio None and ratio 1.0 give exactly price x shares
    (IEEE division by 1.0 is exact) — CCJ's recorded $35,456,212,000.0 at ads_ratio 1.0; None when price
    or shares is falsy (the engine then keeps its universe-cap fallback)."""
    M = E.market_cap_est
    for price, shares in ((81.4, 435580000), (132.7, 419200000), (69.98, 292183), (0.1 + 0.2, 3), (305.51, 48312000)):
        assert M(price, shares, None) == price * shares
        assert M(price, shares, 1.0) == price * shares
    assert M(81.4, 435580000, 1.0) == 35456212000.0
    for falsy in (None, 0, 0.0):
        assert M(falsy, 1e6, None) is None
        assert M(falsy, 1e6, 2.0) is None
        assert M(10.0, falsy, None) is None
        assert M(10.0, falsy, 2.0) is None


def test_normalized_oe_total_uses_the_ads_basis():
    """Decision 1 (the second bug: base_oe_total_norm = per-ADS OE x ORDINARY shares): normalized_oe_total
    = (oe_ps x shares) / ratio when a ratio applies, oe_ps x shares otherwise (same operation order, so
    ratio 1.0 / None are bit-identical — CCJ 1.095035000734019 x 435,580,000 = 476,975,345.61972404);
    None when shares is falsy or oe_ps is None; a zero or negative base is a number, not None."""
    N = E.normalized_oe_total
    assert N(2.2319306753731576, 99062216600.0, 100.0) == (2.2319306753731576 * 99062216600.0) / 100.0
    assert N(4.868951714485654, 26149000000, 10.0) == (4.868951714485654 * 26149000000) / 10.0
    assert N(1.095035000734019, 435580000, 1.0) == 1.095035000734019 * 435580000 == 476975345.61972404
    assert N(1.095035000734019, 435580000, None) == 1.095035000734019 * 435580000
    assert N(TEM_PIN, 174264000, None) == TEM_PIN * 174264000
    assert N(0.0, 1e6, None) == 0.0
    assert N(None, 1e6, None) is None
    assert N(None, 1e6, 2.0) is None
    for falsy in (None, 0):
        assert N(1.0, falsy, None) is None
        assert N(1.0, falsy, 2.0) is None


# ===========================================================================
# 3. Decision 2 — dei hygiene, share-scale guard
# ===========================================================================
def _dei(end, val, filed, form="10-Q", fp="Q2"):
    return {"end": end, "val": val, "filed": filed, "form": form, "fp": fp, "fy": int(filed[:4]),
            "accn": f"0000000000-{filed.replace('-', '')}"}


DD_DEI = [_dei("2025-11-04", 418975324, "2025-11-06", fp="Q3"),
          _dei("2026-02-12", 408923857, "2026-02-17", form="10-K", fp="FY"),
          _dei("2026-05-01", 409921306, "2026-05-05", fp="Q1"),
          _dei("2026-07-31", 135042975, "2026-08-04")]


def test_latest_dei_count_takes_the_latest_cover_page_count():
    """Decision 2: latest_dei_count(dei_entries, latest_fy_end) -> (value, date) of the latest usable
    EntityCommonStockSharesOutstanding — DD's post-split 10-Q cover (135,042,975 on 2026-07-31) wins over
    the earlier pre-split covers, regardless of list order."""
    assert E.latest_dei_count(DD_DEI, "2025-12-31") == (135042975, "2026-07-31")
    assert E.latest_dei_count(list(reversed(DD_DEI)), "2025-12-31") == (135042975, "2026-07-31")
    assert E.latest_dei_count([], "2025-12-31") == (None, None)


def test_latest_dei_count_drops_placeholder_covers():
    """Decision 2 (DESIGN §2.0, review finding): values below 10,000 are placeholders and absent — FOX/FOXA
    file a single dei of 1 (2019-03-18), WMG 1,060/1,069 (2019-2020), VOD a 0 (2019-04-30, beside stale
    real covers). Each comes back (None, None), so test (b) cannot fire on them."""
    fox = [_dei("2019-03-18", 1, "2019-03-18")]
    wmg = [_dei("2019-05-07", 1060, "2019-05-07"), _dei("2019-08-06", 1060, "2019-08-06", fp="Q3"),
           _dei("2019-11-27", 1060, "2019-11-27", form="10-K", fp="FY"), _dei("2020-01-31", 1069, "2020-01-31", fp="Q1")]
    vod = [_dei("2019-03-31", 27230375568, "2019-06-07", form="20-F", fp="FY"),
           _dei("2019-04-30", 0, "2019-06-07", form="20-F", fp="FY"),
           _dei("2020-03-31", 27230375568, "2020-07-02", form="20-F", fp="FY"),
           _dei("2021-03-31", 28816835778, "2021-06-23", form="20-F", fp="FY")]
    assert E.latest_dei_count(fox, "2026-06-30") == (None, None)
    assert E.latest_dei_count(wmg, "2025-09-30") == (None, None)
    assert E.latest_dei_count(vod, "2025-03-31") == (None, None)
    # a placeholder never shadows a usable count: the usable one is returned even though it is older
    assert E.latest_dei_count([_dei("2026-01-31", 435000000, "2026-02-05"), _dei("2026-04-30", 1, "2026-05-01")],
                              "2025-12-31") == (435000000, "2026-01-31")


def test_latest_dei_count_ignores_stale_covers():
    """Decision 2 (DESIGN §2.0): a cover dated earlier than latest_fy_end - 548 days (18 months) is absent
    (COKE's 2016 dei beside a 2025 FY; IBKR's 2011 dei). The boundary is inclusive: for a 2025-12-31 FY
    end, 2024-07-01 (548 days earlier) qualifies, 2024-06-30 does not."""
    assert E.latest_dei_count([_dei("2016-03-04", 7141447, "2016-03-18", form="10-K", fp="FY")], "2025-12-31") == (None, None)
    assert E.latest_dei_count([_dei("2020-01-31", 520000000, "2020-02-05")], "2025-09-30") == (None, None)
    assert E.latest_dei_count([_dei("2024-07-01", 300000000, "2024-07-05")], "2025-12-31") == (300000000, "2024-07-01")
    assert E.latest_dei_count([_dei("2024-06-30", 300000000, "2024-07-05")], "2025-12-31") == (None, None)


def test_latest_dei_count_sums_class_facts_of_one_cover():
    """Decision 2 (DESIGN §2.0): several facts sharing the latest (end, filed) are class counts and are
    summed (dual-class covers); a later filing for the same end date wins over the earlier pair."""
    two_class = [_dei("2025-10-31", 430000000, "2025-11-05"),
                 _dei("2026-01-31", 235000000, "2026-02-10"),
                 _dei("2026-01-31", 200000000, "2026-02-10")]
    assert E.latest_dei_count(two_class, "2025-12-31") == (435000000, "2026-01-31")
    amended = two_class + [_dei("2026-01-31", 436000000, "2026-03-01")]
    assert E.latest_dei_count(amended, "2025-12-31") == (436000000, "2026-01-31")


def test_share_scale_check_fires_on_the_known_defects():
    """Decision 2 §1: (a) |base OE/share| > 20 x price — VIV 2,068.56 vs $12.26 (168x), TEM -3,932.44 vs
    $64.72 (61x, absolute value); (b) latest diluted count / dei outside [1/100, 100] — NTNX 292,183 vs
    270,570,179 (0.00108) and NVMI 32,800 vs 29,278,401 (0.00112), both of which sit UNDER 20x price
    (19.37x, 18.19x), so (b) is the test that catches them."""
    S = E.share_scale_check
    viv = S(2068.560818461329, 12.26, 3195606352, 3195606352)
    assert viv["defect"] is True and viv["tests"]["a"] is True and viv["tests"]["b"] is False, viv
    assert viv["dei_ratio"] == 1.0 and viv["reasons"] and all(isinstance(x, str) for x in viv["reasons"])
    tem = S(-3932.4392632609865, 64.72, 174264, None)
    assert tem["defect"] is True and tem["tests"]["a"] is True and tem["tests"]["b"] is False, tem
    assert tem["dei_ratio"] is None and tem["reasons"]
    ntnx = S(1355.341859271022, 69.98, 292183, 270570179)
    assert ntnx["defect"] is True and ntnx["tests"]["a"] is False and ntnx["tests"]["b"] is True, ntnx
    assert close(ntnx["dei_ratio"], 292183 / 270570179, rel=1e-12) and ntnx["reasons"]
    nvmi = S(5842.195121951219, 321.2, 32800, 29278401)
    assert nvmi["defect"] is True and nvmi["tests"]["a"] is False and nvmi["tests"]["b"] is True, nvmi


def test_share_scale_check_is_quiet_on_clean_names():
    """Decision 2 §1: no false positives — STLA's legitimate maximum (|-3.34| vs $4.37 = 0.76x price,
    dei 2,897,483,196 vs 2,886,684,000), CCJ, FOX once its placeholder dei is dropped. Only the latest
    count is an input: v1's history-jump test (c) is gone (EMBJ/WRB/QXO/FRHC were 4/4 false positives),
    so 'tests' carries exactly (a) and (b)."""
    S = E.share_scale_check
    for args in ((-3.341019618122064, 4.37, 2886684000, 2897483196),
                 (1.095035000734019, 81.4, 435580000, 435457978),
                 (3.0432801822323463, 56.8529, 439000000, None),
                 (3.623, 22.5, 734632806, 725000000)):          # EMBJ-shaped last-3 window (clean)
        r = S(*args)
        assert r["defect"] is False and not r["tests"]["a"] and not r["tests"]["b"], (args, r)
        assert not r["reasons"], r
        assert set(r["tests"]) == {"a", "b"}, r["tests"]


def test_share_scale_check_boundaries_and_missing_inputs():
    """Decision 2 §1: (a) is strict (> 20x), (b) is inclusive ([1/100, 100] passes); a missing price, base
    or dei switches the corresponding test off instead of raising (dei 0 included)."""
    S = E.share_scale_check
    assert S(250.0, 12.5, 1e8, None)["tests"]["a"] is False            # exactly 20x
    assert S(250.0 * 1.0001, 12.5, 1e8, None)["tests"]["a"] is True
    assert S(-250.0 * 1.0001, 12.5, 1e8, None)["tests"]["a"] is True   # absolute value
    assert S(1.0, 50.0, 100000000, 1000000)["tests"]["b"] is False     # ratio exactly 100
    assert S(1.0, 50.0, 1000000, 100000000)["tests"]["b"] is False     # ratio exactly 1/100
    assert S(1.0, 50.0, 100000001, 1000000)["tests"]["b"] is True
    assert S(1.0, 50.0, 999999, 100000000)["tests"]["b"] is True
    r = S(5000.0, None, 1e8, None)
    assert r["defect"] is False and r["tests"]["a"] is False and r["dei_ratio"] is None
    assert S(None, 10.0, 1e8, None)["tests"]["a"] is False
    r = S(1.0, 10.0, 1e8, 0)
    assert r["tests"]["b"] is False and r["dei_ratio"] is None


TEM_WINDOW = [("2023-12-31", 63306), ("2024-12-31", 119849), ("2025-12-31", 174264)]   # median year FY2023 -> latest


def test_scale_factor_for_cap():
    """Decision 2 §1 (market-cap shares for a defect): basis 'dei' when shares x 10^k (k != 0) lands within
    25% of dei — NTNX 292,183 x 1,000 vs 270,570,179 -> 1,000, NVMI 32,800 x 1,000 vs 29,278,401 -> 1,000,
    and a thousand-times-too-large count -> 0.001; else basis 'pin' when native / pinned base is within 2%
    of 10^k — TEM (no dei) -3,932.44 / -3.9324 -> 1,000; VIV (dei ratio 1, pin ratio 1,615.6) -> (None,
    None). [Round 3, R3-CAP] the pin path takes the counts from the median's year to the latest year
    (`window_counts`, TEM's FY2023 63,306 -> FY2025 174,264: one scale) and is not consulted without them."""
    F = E.scale_factor_for_cap
    fac, basis = F(292183, 270570179, 1355.341859271022, NTNX_PIN)
    assert fac == 1000 and basis == "dei", (fac, basis)
    fac, basis = F(32800, 29278401, 5842.195121951219, 5.842195121951219)
    assert fac == 1000 and basis == "dei", (fac, basis)
    fac, basis = F(174264, None, -3932.4392632609865, TEM_PIN, window_counts=TEM_WINDOW)
    assert fac == 1000 and basis == "pin", (fac, basis)
    assert F(174264, None, -3932.4392632609865, TEM_PIN) == (None, None)            # no window: pin not consulted
    assert F(3195606352, 3195606352, 2068.560818461329, VIV_PIN) == (None, None)
    fac, basis = F(270570179000, 270570179, None, None)
    assert basis == "dei" and fac is not None and abs(fac - 0.001) < 1e-12, (fac, basis)
    fac, basis = F(174264, 50000000, -3932.4392632609865, TEM_PIN, window_counts=TEM_WINDOW)   # dei unrelated
    assert fac == 1000 and basis == "pin", (fac, basis)
    assert F(292183, None, 1355.341859271022, None) == (None, None)


# ===========================================================================
# 4. Decision 2 — split basis (Option B: the engine handles it)
# ===========================================================================
def test_snap_split_ratio():
    """Decision 2 §2: snap_split_ratio returns p/q (integers 1..10) within 1% of x, else x — DD's filed
    0.333 is the 1-for-3 (1/3), 0.6667 is 2/3 (WRB's rounded filing), whole ratios stay whole; BMNR's
    0.005 has no such fraction and stays; 1.183 has none within 1% and stays."""
    S = E.snap_split_ratio
    assert abs(S(0.333) - 1 / 3) < 1e-12
    assert abs(S(0.6667) - 2 / 3) < 1e-12
    assert S(2) == 2.0 and S(10) == 10.0 and S(4) == 4.0
    assert S(1.5) == 1.5 and S(0.25) == 0.25 and abs(S(0.3) - 0.3) < 1e-12
    assert S(0.005) == 0.005
    assert S(1.183) == 1.183


def test_snap_split_ratio_1_13_follows_the_design_rule():
    """Decision 2 §2: BWA's filed 1.13 is NOT a split (the dei confirmation rejects it — see
    confirm_split), but the snap rule itself is literal: 9/8 = 1.125 lies 0.44% from 1.13, inside 1%, so
    the design's rule returns 9/8 (fundamentals.snap_ratio, the repo's existing helper, does the same).
    The task brief's '1.13 stays 1.13' contradicts DESIGN §2b's stated rule; this test follows the design
    (reported as an open point)."""
    assert abs(E.snap_split_ratio(1.13) - 9 / 8) < 1e-12


def _split(end, val, filed, start=None, form="10-Q", fp="Q2"):
    e = {"end": end, "val": val, "filed": filed, "form": form, "fp": fp, "fy": int(filed[:4]),
         "accn": f"0000000000-{filed.replace('-', '')}"}
    if start:
        e["start"] = start
    return e


MLI_SPLITS = [  # MLI: the 2023 2-for-1 re-disclosed in every FY context, then the real 2026 2-for-1
    _split("2023-09-26", 2, "2023-10-25", fp="Q3"),
    _split("2023-09-26", 2, "2024-02-28", form="10-K", fp="FY"),
    _split("2023-10-20", 2, "2024-07-24"),
    _split("2023-12-30", 2, "2024-02-28", start="2023-01-01", form="10-K", fp="FY"),
    _split("2024-12-28", 2, "2025-02-26", start="2023-12-31", form="10-K", fp="FY"),
    _split("2025-12-27", 2, "2026-02-25", start="2024-12-29", form="10-K", fp="FY"),
    _split("2026-05-29", 2, "2026-07-22"),
    _split("2026-06-27", 2, "2026-07-22", start="2025-12-28"),
]


def _events(out):
    return [(e[0], e[1]) for e in out]


def test_split_events_post_fy_keeps_only_post_fy_events():
    """Decision 2 §2 (review P1): only ratio facts whose context END is after the latest FY end are
    events. MLI's three FY-context re-disclosures of its 2023 split (the last ends exactly ON the 2025-12-27
    FY end) are not events; its 2026 split, tagged at 2026-05-29 and 2026-06-27, is ONE event at its first
    date (180-day collapse). DD's 0.333 at 2026-06-30 is kept with the ratio as filed."""
    assert _events(E.split_events_post_fy(MLI_SPLITS, "2025-12-27")) == [("2026-05-29", 2)]
    dd = [_split("2026-06-30", 0.333, "2026-08-04", start="2026-01-01")]
    assert _events(E.split_events_post_fy(dd, "2025-12-31")) == [("2026-06-30", 0.333)]


def test_split_events_post_fy_ignores_in_history_re_disclosures():
    """Decision 2 §2: facts dated on or before the latest FY end describe splits the annual filing already
    reflects — CSGP's 10-for-1 (2021 dates plus a 2025-01-01..2025-06-30 re-tag), DXCM's 4-for-1 (a 2021 FY
    context for a 2022 split), CFG (165,582 and a 6 in a FY2021 context), COKE's 10-for-1 of 2025-03-04,
    BWA's 1.13 at every FY end: none is an event, so no history is ever rewritten for them."""
    csgp = [_split("2021-06-07", 10, "2023-02-22", form="10-K", fp="FY"), _split("2021-06-30", 10, "2021-07-28", start="2021-01-01"),
            _split("2021-09-30", 10, "2021-10-27", start="2021-01-01", fp="Q3"), _split("2022-03-31", 10, "2022-04-28", start="2022-01-01", fp="Q1"),
            _split("2025-06-30", 10, "2025-07-23", start="2025-01-01")]
    dxcm = [_split("2021-12-31", 4, "2023-02-09", start="2021-01-01", form="10-K", fp="FY"), _split("2022-06-10", 4, "2022-07-28"),
            _split("2022-06-10", 4, "2023-10-26", fp="Q3")]
    cfg = [_split("2014-08-22", 165582, "2016-02-26", form="10-K", fp="FY"), _split("2021-12-31", 6, "2022-02-23", start="2021-01-01", form="10-K", fp="FY")]
    coke = [_split("2025-03-04", 10, "2025-04-30", fp="Q1"), _split("2025-03-04", 10, "2026-02-18", form="10-K", fp="FY")]
    bwa = [_split("2023-12-31", 1.13, "2024-02-08", start="2023-01-01", form="10-K", fp="FY"),
           _split("2024-12-31", 1.13, "2025-02-06", start="2024-01-01", form="10-K", fp="FY"),
           _split("2025-12-31", 1.13, "2026-02-11", start="2025-01-01", form="10-K", fp="FY")]
    for name, ents in (("CSGP", csgp), ("DXCM", dxcm), ("CFG", cfg), ("COKE", coke), ("BWA", bwa)):
        assert E.split_events_post_fy(ents, "2025-12-31") == [], name


def test_split_events_post_fy_drops_ratio_one_and_out_of_range():
    """Decision 2 §2: ratio 1 (TW tags 1 every quarter) and ratios outside [0.01, 100] (BMNR's 0.005, ELAN's
    2,932,900 IPO recapitalisation, a 150) are dropped even after the FY end; 100 and 0.01 are inside."""
    post = "2025-12-31"
    tw = [_split("2026-03-31", 1, "2026-04-29", start="2026-01-01", fp="Q1"), _split("2026-06-30", 1, "2026-07-30", start="2026-01-01")]
    assert E.split_events_post_fy(tw, post) == []
    assert E.split_events_post_fy([_split("2026-05-31", 0.005, "2026-07-14", start="2025-09-01", fp="Q3")], "2025-08-31") == []
    assert E.split_events_post_fy([_split("2026-03-15", 2932900, "2026-05-01")], post) == []
    assert E.split_events_post_fy([_split("2026-03-15", 150, "2026-05-01")], post) == []
    assert _events(E.split_events_post_fy([_split("2026-03-15", 100, "2026-05-01")], post)) == [("2026-03-15", 100)]
    assert _events(E.split_events_post_fy([_split("2026-03-15", 0.01, "2026-05-01")], post)) == [("2026-03-15", 0.01)]


def test_split_events_post_fy_collapses_within_180_days():
    """Decision 2 §2: the same ratio within 180 days is one event at its first date (Qnity's 0.5 tagged at
    2026-03-31 and 2026-06-30); 212 days apart they are two events; different ratios are never merged."""
    q = [_split("2026-03-31", 0.5, "2026-05-12", start="2026-01-01", fp="Q1"), _split("2026-06-30", 0.5, "2026-08-04", start="2026-01-01")]
    assert _events(E.split_events_post_fy(q, "2025-12-31")) == [("2026-03-31", 0.5)]
    two = [_split("2026-02-01", 2, "2026-03-01"), _split("2026-09-01", 2, "2026-10-01")]
    assert sorted(_events(E.split_events_post_fy(two, "2025-12-31"))) == [("2026-02-01", 2), ("2026-09-01", 2)]
    mixed = [_split("2026-02-01", 2, "2026-03-01"), _split("2026-03-01", 3, "2026-04-01")]
    assert sorted(_events(E.split_events_post_fy(mixed, "2025-12-31"))) == [("2026-02-01", 2), ("2026-03-01", 3)]


def test_confirm_split_accepts_only_dei_confirmed_events():
    """Decision 2 §2 (review P1: a failed confirmation never adjusts): the latest event a post-event dei
    confirms within ±15% of r or 1/r. DD: 135,042,975 / 419,200,000 = 0.322 vs 0.333 -> confirmed, ratio
    used = snap(0.333) = 1/3. MLI: 221,181,388 / 111,492,000 = 1.984 vs 2 -> 2. Qnity's 0.5 (a spin-off
    distribution ratio: dei 209,208,543 vs 209,800,000) and BMNR's 0.005 (dei 25x UP) are NOT confirmed."""
    C = E.confirm_split
    r = C([("2026-06-30", 0.333)], 419200000, 135042975, "2026-07-31")
    assert r is not None and r[0] == "2026-06-30" and abs(r[1] - 1 / 3) < 1e-12 and r[2], r
    r = C([("2026-05-29", 2)], 111492000, 221181388, "2026-07-17")
    assert r is not None and r[0] == "2026-05-29" and r[1] == 2.0, r
    assert C([("2026-03-31", 0.5)], 209800000, 209208543, "2026-07-31") is None
    assert C([("2026-05-31", 0.005)], 24515226, 603226394, "2026-07-09") is None
    # BWA's 1.13 is deliberately NOT asserted here: under the literal ±15% rule its inverse (0.885) matches
    # BWA's ordinary buyback drift (dei / shares 0.941), so only split_events_post_fy's "after the latest FY
    # end" filter keeps it out (test_split_events_post_fy_ignores_in_history_re_disclosures).


def test_confirm_split_handles_inverse_ratio_filers():
    """Decision 2 §2: filers write the ratio either way round — a 1-for-10 reverse split filed as 10 is
    confirmed by dei / shares ~ 1/10 (ratio used 0.1), a 2-for-1 filed as 0.5 by dei / shares ~ 2 (ratio
    used 2)."""
    C = E.confirm_split
    r = C([("2026-03-15", 10)], 50000000, 5100000, "2026-04-30")
    assert r is not None and r[0] == "2026-03-15" and abs(r[1] - 0.1) < 1e-12, r
    r = C([("2026-05-29", 0.5)], 111492000, 221181388, "2026-07-17")
    assert r is not None and r[1] == 2.0, r


def test_confirm_split_needs_a_post_event_dei():
    """Decision 2 §2: the dei must be dated AFTER the event (DD's pre-split 2026-05-01 cover, or a cover on
    the event date, confirms nothing); no dei or no events -> None; with several events the latest one the
    dei confirms is returned (an unconfirmed later ratio does not hide a confirmed earlier one)."""
    C = E.confirm_split
    assert C([("2026-06-30", 0.333)], 419200000, 409921306, "2026-05-01") is None
    assert C([("2026-06-30", 0.333)], 419200000, 135042975, "2026-06-30") is None
    assert C([("2026-06-30", 0.333)], 419200000, None, None) is None
    assert C([], 419200000, 135042975, "2026-07-31") is None
    r = C([("2026-02-01", 2.0), ("2026-06-30", 3.0)], 100000000, 201000000, "2026-07-31")
    assert r is not None and r[0] == "2026-02-01" and r[1] == 2.0, r


def test_confirm_split_needs_a_basis_change_in_the_dei():
    """Decision 2 §2 [READING of "split-basis check against the latest dei"; resolves the spec-test open point on
    near-1 ratios]: a cover-page count within ±15% of the latest diluted count shows no basis change, so it
    confirms nothing — otherwise any ratio near 1 is 'confirmed' by ordinary buyback / issuance drift. BWA's 1.13
    (a spin-off conversion ratio) filed AFTER an FY end with dei / shares 0.941 (its real drift) -> None (its
    inverse 0.885 is within 15% of 0.941 — the literal band alone would rescale the history by 1/1.13); a real
    1.1 stock split with dei / shares 1.10 is indistinguishable from issuance -> None; a 10-K whose counts are
    already restated (dei / shares 1.0) never confirms; a 5-for-4 split with dei / shares 1.25 IS confirmed
    (5/4); DD (0.322) and MLI (1.984) as before."""
    C = E.confirm_split
    assert C([("2026-03-31", 1.13)], 216400000, 203700000, "2026-04-24") is None
    assert C([("2026-03-31", 1.1)], 100000000, 110000000, "2026-04-30") is None
    assert C([("2026-02-15", 1.1)], 110000000, 110200000, "2026-03-01") is None
    r = C([("2026-03-31", 1.25)], 100000000, 125000000, "2026-04-30")
    assert r is not None and r[1] == 1.25 and r[2]["matched"] == "ratio", r
    r = C([("2026-06-30", 0.333)], 419200000, 135042975, "2026-07-31")
    assert r is not None and abs(r[1] - 1 / 3) < 1e-12, r
    r = C([("2026-05-29", 2)], 111492000, 221181388, "2026-07-17")
    assert r is not None and r[1] == 2.0, r


# ===========================================================================
# 5. Decisions 3, 4, 5 — capex assembly
# ===========================================================================
def test_capex_rollup_is_authoritative():
    """Decision 4: when the PP&E roll-up is filed it is the PP&E leg and no component is stacked on it —
    AR FY2022 943,971,000 (its three components sum to the same figure and are NOT added)."""
    res = E.capex_for_period([fact(PRIMARY, 943971000, "2023-02-15")],
                             [fact(EXPLORE, 780649000, "2025-02-12"), fact(ACQ_OG, 149009000, "2025-02-12"),
                              fact(OTHER_PPE, 14313000, "2025-02-12")], [])
    assert res["ppe"] == 943971000 and res["ppe_source"] == "rollup", res
    assert list(res["ppe_tags"]) == [PRIMARY] and res["provenance"] == PRIMARY, res
    assert res["ppe_unit"] == "USD" and res["intangibles"] == 0.0 and list(res["intangible_tags"]) == []


def test_capex_components_summed_across_filings_ar():
    """Decision 4 (AR, ruling: FY2023-25 print the summed totals): with no roll-up the components are the
    per-tag latest filings, summed — FY2023 964,346,000 + 151,135,000 (last filed 2025-02-12; the FY2025
    10-K dropped the comparative) + 16,382,000 = 1,131,863,000 ('components_mixed_filings'); FY2024
    716,779,000; FY2025 944,003,000 from one filing ('components'). Provenance lists the tags in list order."""
    C = E.capex_for_period
    fy23 = C([], [fact(EXPLORE, 964346000, "2026-02-11"), fact(ACQ_OG, 151135000, "2025-02-12"),
                  fact(OTHER_PPE, 16382000, "2026-02-11")], [])
    assert fy23["ppe"] == 1131863000 and fy23["ppe_source"] == "components_mixed_filings", fy23
    assert list(fy23["ppe_tags"]) == [EXPLORE, ACQ_OG, OTHER_PPE] and fy23["provenance"] == AR_COMPONENTS, fy23
    assert not dropped(fy23), fy23["dropped"]
    fy24 = C([], [fact(EXPLORE, 614855000, "2026-02-11"), fact(ACQ_OG, 90995000, "2025-02-12"),
                  fact(OTHER_PPE, 10929000, "2026-02-11")], [])
    assert fy24["ppe"] == 716779000 and fy24["ppe_source"] == "components_mixed_filings", fy24
    fy25 = C([], [fact(EXPLORE, 685468000, "2026-02-11"), fact(ACQ_OG, 253128000, "2026-02-11"),
                  fact(OTHER_PPE, 5407000, "2026-02-11")], [])
    assert fy25["ppe"] == 944003000 and fy25["ppe_source"] == "components", fy25
    assert fy25["provenance"] == AR_COMPONENTS


def test_capex_retag_duplicate_counted_once_ip():
    """Decision 4 (review P1, IP): an older-filed component equal (within 0.5%) to a newer-filed component of
    a DIFFERENT tag is the same cash-flow line re-tagged — IP's OtherPPE 1,141M (filed 2025-02-21) =
    ProductiveAssets 1,141M (filed 2026-02-27): 1,141M once, the older one dropped as 'retag_duplicate'.
    Same for FY2024 921M. 0.35% apart still dedupes; 0.8% apart are two lines and both count."""
    C = E.capex_for_period
    for v in (1141000000, 921000000):
        res = C([], [fact(OTHER_PPE, v, "2025-02-21"), fact(PRODUCTIVE, v, "2026-02-27")], [])
        assert res["ppe"] == v, res
        assert (OTHER_PPE, "retag_duplicate") in dropped(res), res["dropped"]
        assert list(res["ppe_tags"]) == [PRODUCTIVE] and res["provenance"] == PRODUCTIVE, res
    near = C([], [fact(OTHER_PPE, 1141000000, "2025-02-21"), fact(PRODUCTIVE, 1145000000, "2026-02-27")], [])
    assert near["ppe"] == 1145000000 and (OTHER_PPE, "retag_duplicate") in dropped(near), near
    apart = C([], [fact(OTHER_PPE, 1141000000, "2025-02-21"), fact(PRODUCTIVE, 1150000000, "2026-02-27")], [])
    assert apart["ppe"] == 2291000000 and not dropped(apart), apart


def test_capex_same_filing_identical_value_counted_once_ip():
    """Decision 4 [READING — design silent; ruling 5's 'never double-counted'; resolves the spec-test open
    point on IP FY2022]: two DIFFERENT component tags carrying the IDENTICAL value in the SAME filing are one
    cash-flow line tagged twice — IP FY2022 PaymentsToAcquireOtherPropertyPlantAndEquipment and
    PaymentsToAcquireProductiveAssets are both 931,000,000 in the 2025-02-21 10-K: 931M once (the first in list
    order kept, the other dropped 'same_filing_duplicate'), not 1,862M. Within one filing only identity counts:
    GLPI FY2022 OtherPPE 23,865,000 and construction in process 23,864,000 (same 10-K) are two disclosures and
    both are summed (47,729,000 + capital improvements 159,000). The intangible leg follows the same rule."""
    C = E.capex_for_period
    ip = C([], [fact(OTHER_PPE, 931000000, "2025-02-21"), fact(PRODUCTIVE, 931000000, "2025-02-21")], [])
    assert ip["ppe"] == 931000000 and list(ip["ppe_tags"]) == [OTHER_PPE] and ip["provenance"] == OTHER_PPE, ip
    assert (PRODUCTIVE, "same_filing_duplicate") in dropped(ip), ip["dropped"]
    glpi = C([], [fact(OTHER_PPE, 23865000, "2025-02-20"), fact(CIP, 23864000, "2025-02-20"),
                  fact(CAP_IMPROVEMENTS, 159000, "2025-02-20")], [])
    assert glpi["ppe"] == 23865000 + 23864000 + 159000 and not dropped(glpi), glpi
    intang = C([fact(PRIMARY, 500000000, "2026-02-20")], [],
               [fact(INTANG, 40000000, "2026-02-20"), fact(OTHER_INTANG, 40000000, "2026-02-20")])
    assert intang["intangibles"] == 40000000 and list(intang["intangible_tags"]) == [INTANG], intang
    assert (OTHER_INTANG, "same_filing_duplicate") in dropped(intang), intang["dropped"]
    # two distinct intangible lines (different values) are both added
    two = C([fact(PRIMARY, 500000000, "2026-02-20")], [],
            [fact(INTANG, 40000000, "2026-02-20"), fact(OTHER_INTANG, 3000000, "2026-02-20")])
    assert two["intangibles"] == 43000000 and not dropped(two), two


def test_capex_glpi_fy2023_union_keeps_the_separately_filed_line():
    """Decisions 3 + 4 (resolves the stale design figure 'GLPI FY2023 0 -> 47,437,000'): under v2's per-tag-latest
    union, GLPI FY2023 is construction in process $0 (zero-guard: contributes 0, blocks nothing) + other PP&E
    47,437,000 (2026-02-19) + capital improvements 67,000 (last filed 2025-02-20; the FY2025 10-K dropped the
    comparative) = 47,504,000, 'components_mixed_filings'. 47,437,000 was the v1 same-filing rule's answer, which
    v2 replaced because it drops separately filed lines (AR's 151.1M acquisitions line)."""
    res = E.capex_for_period([], [fact(OTHER_PPE, 47437000, "2026-02-19"), fact(CIP, 0, "2026-02-19"),
                                  fact(CAP_IMPROVEMENTS, 67000, "2025-02-20")], [])
    assert res["ppe"] == 47504000 and res["ppe_source"] == "components_mixed_filings", res
    assert not [d for d in dropped(res) if d[1] != "zero_guard"], res["dropped"]


def test_capex_zero_component_never_blocks_els():
    """Decision 3 (zero-guard): ELS FY2023 — a $0 PaymentsToAcquireOtherProductiveAssets (filed 2024-02-22)
    contributes 0 and never blocks PaymentsForCapitalImprovements 317,086,000. ELS FY2022 (history):
    ProductiveAssets 132.8M + CapitalImprovements 249.277M — two filed lines -> 382,077,000."""
    C = E.capex_for_period
    fy23 = C([], [fact(OTHER_PRODUCTIVE, 0, "2024-02-22"), fact(CAP_IMPROVEMENTS, 317086000, "2026-02-18")], [])
    assert fy23["ppe"] == 317086000, fy23
    assert CAP_IMPROVEMENTS in fy23["ppe_tags"] and CAP_IMPROVEMENTS in fy23["provenance"], fy23
    assert fy23["ppe_source"] in ("components", "components_mixed_filings"), fy23
    fy22 = C([], [fact(PRODUCTIVE, 132800000, "2024-01-22"), fact(OTHER_PRODUCTIVE, 0, "2024-02-22"),
                  fact(CAP_IMPROVEMENTS, 249277000, "2025-02-25")], [])
    assert fy22["ppe"] == 382077000 and fy22["ppe_source"] == "components_mixed_filings", fy22


def test_capex_rollup_wins_over_a_re_tagged_component_rbc():
    """Decisions 3 + 4: RBC FY2023 files the roll-up 42.0M (2023-05-19) and, in later 10-Ks, the same 42.0M
    re-tagged as PaymentsForCapitalImprovements — the roll-up wins and nothing is added (not 84M)."""
    res = E.capex_for_period([fact(PRIMARY, 42000000, "2023-05-19")], [fact(CAP_IMPROVEMENTS, 42000000, "2025-05-16")], [])
    assert res["ppe"] == 42000000 and res["ppe_source"] == "rollup" and res["provenance"] == PRIMARY, res


def test_capex_intangibles_added_on_top_of_any_ppe_leg():
    """Decision 5 [READING: intangibles additive on roll-up years]: APP FY2023 roll-up 4,246,000 +
    PaymentsToAcquireIntangibleAssets 63,899,000; VOD FY2023 IFRS roll-up EUR 4,957M + IFRS intangibles EUR
    2,799M (each leg keeps its unit); on a component leg too. Provenance = PP&E tags + intangible tags."""
    C = E.capex_for_period
    app = C([fact(PRIMARY, 4246000, "2025-02-27")], [], [fact(INTANG, 63899000, "2026-02-19")])
    assert app["ppe"] == 4246000 and app["intangibles"] == 63899000, app
    assert list(app["intangible_tags"]) == [INTANG] and app["provenance"] == f"{PRIMARY}+{INTANG}", app
    vod = C([fact(IFRS_PPE, 4957000000, "2025-06-06", "EUR")], [], [fact(IFRS_INTANG, 2799000000, "2025-06-06", "EUR")])
    assert vod["ppe"] == 4957000000 and vod["ppe_unit"] == "EUR" and vod["ppe_source"] == "rollup", vod
    assert vod["intangibles"] == 2799000000 and vod["intangibles_unit"] == "EUR", vod
    assert vod["provenance"] == f"{IFRS_PPE}+{IFRS_INTANG}", vod
    comp = C([], [fact(EXPLORE, 100000000, "2026-02-11")],
             [fact(INTANG, 5000000, "2026-02-11"), fact(OTHER_INTANG, 2000000, "2026-02-11")])
    assert comp["ppe"] == 100000000 and comp["intangibles"] == 7000000, comp
    assert list(comp["intangible_tags"]) == [INTANG, OTHER_INTANG], comp


def test_capex_combined_ifrs_tag_takes_no_intangibles():
    """Decision 5 ('never double-counted against the IFRS combined PP&E+intangibles tag'): when the PP&E leg
    is the combined tag, the intangible leg adds nothing and is dropped with reason 'combined_tag'."""
    res = E.capex_for_period([fact(IFRS_COMBINED, 1000000000, "2026-04-24", "EUR")], [],
                             [fact(IFRS_INTANG, 100000000, "2026-04-24", "EUR")])
    assert res["ppe"] == 1000000000 and res["intangibles"] == 0.0, res
    assert list(res["intangible_tags"]) == [] and res["provenance"] == IFRS_COMBINED, res
    assert (IFRS_INTANG, "combined_tag") in dropped(res), res["dropped"]


def test_capex_mixed_units_keep_the_majority_unit():
    """Decision 4 (review P2: one unit per leg): components are summed in the unit most of them carry (USD on
    a tie); the minority-unit facts are dropped with reason 'unit'. The intangible leg follows the same rule
    and keeps its own unit beside the PP&E leg's (JD FY2023: USD-translated roll-up 567M + a CNY-only 3M
    intangible fact — the engine converts each leg at its own rate)."""
    C = E.capex_for_period
    res = C([], [fact(EXPLORE, 100000000, "2026-02-11", "CNY"), fact(ACQ_OG, 50000000, "2026-02-11", "CNY"),
                 fact(OTHER_PPE, 7000000, "2026-02-11", "USD")], [])
    assert res["ppe"] == 150000000 and res["ppe_unit"] == "CNY", res
    assert (OTHER_PPE, "unit") in dropped(res), res["dropped"]
    tie = C([], [fact(EXPLORE, 100000000, "2026-02-11", "CNY"), fact(OTHER_PPE, 7000000, "2026-02-11", "USD")], [])
    assert tie["ppe"] == 7000000 and tie["ppe_unit"] == "USD" and (EXPLORE, "unit") in dropped(tie), tie
    jd = C([fact(PRIMARY, 567000000, "2024-04-18", "USD")], [], [fact(INTANG, 3000000, "2024-04-18", "CNY")])
    assert jd["ppe"] == 567000000 and jd["ppe_unit"] == "USD", jd
    assert jd["intangibles"] == 3000000 and jd["intangibles_unit"] == "CNY", jd
    ints = C([fact(PRIMARY, 1, "2026-01-01")], [],
             [fact(INTANG, 3000000, "2026-01-01", "CNY"), fact(OTHER_INTANG, 2000000, "2026-01-01", "CNY"),
              fact(IFRS_INTANG, 1000000, "2026-01-01", "USD")])
    assert ints["intangibles"] == 5000000 and ints["intangibles_unit"] == "CNY", ints
    assert (IFRS_INTANG, "unit") in dropped(ints), ints["dropped"]


def test_capex_zero_guard_non_primary_candidates():
    """Decision 3 (zero-guard, ruling 3(a)): a $0 from a NON-primary candidate never blocks a non-zero value
    from a later candidate for the same period — GLPI FY2023's $0 construction-in-process beside OtherPPE
    47,437,000; a $0 IFRS roll-up yields to a later non-zero roll-up or to the components; with nothing
    non-zero behind it the $0 stands."""
    C = E.capex_for_period
    glpi = C([], [fact(CIP, 0, "2026-02-19"), fact(OTHER_PPE, 47437000, "2026-02-19")], [])
    assert glpi["ppe"] == 47437000 and glpi["ppe_source"] == "components", glpi
    r = C([fact(IFRS_PPE, 0, "2026-04-24", "EUR"), fact(IFRS_PPE2, 33000000, "2026-04-24", "EUR")], [], [])
    assert r["ppe"] == 33000000 and r["ppe_source"] == "rollup" and list(r["ppe_tags"]) == [IFRS_PPE2], r
    r = C([fact(IFRS_PPE, 0, "2026-04-24", "EUR")], [fact(OTHER_PPE, 47000000, "2026-04-24", "EUR")], [])
    assert r["ppe"] == 47000000 and r["ppe_source"] == "components", r
    r = C([fact(IFRS_PPE, 0, "2026-04-24", "EUR")], [], [])
    assert r["ppe"] == 0 and r["ppe"] is not None and r["ppe_source"] == "rollup", r


def test_capex_zero_primary_rollup_stays_authoritative():
    """Decision 3 (ruling 3(a) covers non-primary candidates only): a $0 under
    PaymentsToAcquirePropertyPlantAndEquipment is the filer's own capex line and stays — the later
    PaymentsForCapitalImprovements is not used."""
    r = E.capex_for_period([fact(PRIMARY, 0, "2026-02-20")], [fact(CAP_IMPROVEMENTS, 42000000, "2026-02-20")], [])
    assert r["ppe"] == 0 and r["ppe_source"] == "rollup" and list(r["ppe_tags"]) == [PRIMARY], r


def test_capex_nothing_filed_is_none():
    """Decisions 3/4: no PP&E fact at all -> ppe None (the 5.4 missing-capex path: gate, override fill),
    intangibles 0.0; an intangible-only period still has no PP&E leg."""
    r = E.capex_for_period([], [], [])
    assert r["ppe"] is None and r["ppe_source"] is None and r["intangibles"] == 0.0, r
    r = E.capex_for_period([], [], [fact(INTANG, 5000000, "2026-02-19")])
    assert r["ppe"] is None and r["ppe_source"] is None, r


ECHO_CUM = 30000000000  # EchoStar's PaymentsToAcquireIntangibleAssets on FY2024 AND on two multi-year contexts


def _ctx(start, end, val, form="10-K", fp="FY", fy=None, filed=None):
    """One companyfacts entry (an instant when start is None)."""
    e = {"end": end, "val": val, "form": form, "fp": fp, "fy": fy or int(end[:4]), "filed": filed or f"{int(end[:4]) + 1}-02-27"}
    if start:
        e["start"] = start
    return e


def test_cumulative_context_values_reads_multi_year_contexts_only():
    """[ADDITION — ECHO] cumulative_context_values: every non-zero (tag, unit, value) filed on a context LONGER than
    380 days (end - start), any form, every unit unless `units` limits them, us-gaap and (taxonomy, tag) entries;
    annual (<= 380 days) contexts, instants and zeros never count."""
    facts = {"facts": {
        "us-gaap": {INTANG: {"units": {
            "USD": [_ctx("2024-01-01", "2024-12-31", ECHO_CUM),                                 # annual: not cumulative
                    _ctx("2008-01-01", "2023-12-31", ECHO_CUM, fy=2023, filed="2024-02-29"),     # ECHO's two contexts
                    _ctx("2018-01-01", "2025-12-31", ECHO_CUM, fy=2025, filed="2026-03-02"),
                    _ctx("2010-01-01", "2015-12-31", 0),                                        # zero: ignored
                    _ctx("2020-01-01", "2021-01-16", 5000000),                                  # 381 days: counts
                    _ctx("2022-01-01", "2023-01-16", 7000000),                                  # 380 days: annual
                    _ctx(None, "2024-12-31", 9000000)],                                         # instant: ignored
            "CNY": [_ctx("2016-01-01", "2019-12-31", 1000000, form="10-Q", fp="Q2")]}},
            OTHER_INTANG: {"units": {"USD": [_ctx("2025-01-01", "2025-12-31", 4000000)]}}},
        IF: {IFRS_INTANG: {"units": {"EUR": [_ctx("2019-01-01", "2025-12-31", 2000000, form="20-F")]}}}}}
    got = E.cumulative_context_values(facts, E.CAPEX_INTANGIBLE_TAGS)
    assert got == {(INTANG, "USD", ECHO_CUM), (INTANG, "USD", 5000000), (INTANG, "CNY", 1000000),
                   (IFRS_INTANG, "EUR", 2000000)}, got
    usd = E.cumulative_context_values(facts, [t for t in E.CAPEX_INTANGIBLE_TAGS if isinstance(t, str)], units=("USD",))
    assert usd == {(INTANG, "USD", ECHO_CUM), (INTANG, "USD", 5000000)}, usd
    assert E.cumulative_context_values({"facts": {}}, E.CAPEX_INTANGIBLE_TAGS) == set()


def test_capex_cumulative_duplicate_dropped_from_intangible_leg_echo():
    """[ADDITION — ECHO] capex_for_period(cumulative=...): ECHO FY2024 roll-up 1,544,877,000 + intangible 30,000,000,000
    whose value the tag also files on multi-year contexts -> the intangible fact is dropped ('cumulative_duplicate'),
    capex = the roll-up. Without the set the 5.5 leg is unchanged (31,544,877,000); a genuine second intangible is
    kept; the same value in another unit is not a duplicate; the PP&E legs are never checked."""
    C = E.capex_for_period
    cum = {(INTANG, "USD", ECHO_CUM)}
    res = C([fact(PRIMARY, 1544877000, "2026-03-02")], [], [fact(INTANG, ECHO_CUM, "2025-02-27")], cumulative=cum)
    assert res["ppe"] == 1544877000 and res["intangibles"] == 0.0 and res["intangibles_unit"] is None, res
    assert list(res["intangible_tags"]) == [] and res["provenance"] == PRIMARY, res
    assert [list(d) for d in res["dropped"]] == [[INTANG, ECHO_CUM, "cumulative_duplicate"]], res["dropped"]
    old = C([fact(PRIMARY, 1544877000, "2026-03-02")], [], [fact(INTANG, ECHO_CUM, "2025-02-27")])
    assert old["ppe"] + old["intangibles"] == 31544877000 and old["dropped"] == [], old
    two = C([fact(PRIMARY, 1544877000, "2026-03-02")], [],
            [fact(INTANG, ECHO_CUM, "2025-02-27"), fact(OTHER_INTANG, 4000000, "2025-02-27")], cumulative=cum)
    assert two["intangibles"] == 4000000 and list(two["intangible_tags"]) == [OTHER_INTANG], two
    assert (INTANG, "cumulative_duplicate") in dropped(two), two["dropped"]
    cny = C([fact(PRIMARY, 1544877000, "2026-03-02")], [], [fact(INTANG, ECHO_CUM, "2025-02-27", "CNY")], cumulative=cum)
    assert cny["intangibles"] == ECHO_CUM and cny["intangibles_unit"] == "CNY", cny
    ppe = C([fact(PRIMARY, ECHO_CUM, "2026-03-02")], [fact(CAP_IMPROVEMENTS, 5, "2026-03-02")], [],
            cumulative={(PRIMARY, "USD", ECHO_CUM), (CAP_IMPROVEMENTS, "USD", 5)})
    assert ppe["ppe"] == ECHO_CUM and ppe["dropped"] == [], ppe


def _cov_rows(pairs, years=(2023, 2024, 2025)):
    return [{"period_end": f"{y}-12-31", "fy_label": str(y), "capex": c, "da": d} for y, (c, d) in zip(years, pairs)]


WY_ROWS = _cov_rows([(57000000.0, 518000000.0), (52000000.0, 520000000.0), (51000000.0, 510000000.0)])  # 0.11/0.10/0.10


def test_capex_coverage_low_fires_three_of_three():
    """Decision 5 (CAPEX_COVERAGE_LOW): capex below 50% of D&A in EACH of the last 3 FY at a filer with
    positive PP&E -> (True, detail naming every year) — WY's 0.11/0.10/0.10."""
    fired, detail = E.capex_coverage_low(WY_ROWS, True)
    assert fired is True, detail
    for y in ("2023", "2024", "2025"):
        assert y in detail, detail


def test_capex_coverage_low_needs_positive_ppe_and_all_three_years():
    """Decision 5: unknown PP&E (None) or non-positive PP&E -> no flag; one year at or above 0.5 -> no flag
    (0.5 exactly is not below 50%); a year without capex or D&A, or with D&A 0, cannot be judged -> no flag."""
    L = E.capex_coverage_low
    assert L(WY_ROWS, None)[0] is False
    assert L(WY_ROWS, False)[0] is False
    assert L(_cov_rows([(57e6, 518e6), (260e6, 520e6), (51e6, 510e6)]), True)[0] is False
    assert L(_cov_rows([(57e6, 518e6), (259e6, 518e6), (51e6, 510e6)]), True)[0] is False   # exactly 0.5
    assert L(_cov_rows([(57e6, 518e6), (52e6, None), (51e6, 510e6)]), True)[0] is False
    assert L(_cov_rows([(57e6, 518e6), (None, 520e6), (51e6, 510e6)]), True)[0] is False
    assert L(_cov_rows([(57e6, 518e6), (52e6, 0.0), (51e6, 510e6)]), True)[0] is False


# ===========================================================================
# 6. Decisions 6, 7 — SBC reconciliation, USD overrides
# ===========================================================================
def _inst(tag, val, end, form="10-K", fp="FY", taxonomy="us-gaap", unit="USD"):
    return {"facts": {taxonomy: {tag: {"units": {unit: [{"end": end, "val": val, "form": form, "fp": fp,
                                                         "filed": end[:4] + "-12-31"}]}}}}}


def _merge_facts(*fs):
    out = {"facts": {}}
    for fct in fs:
        for tax, tags in fct["facts"].items():
            out["facts"].setdefault(tax, {}).update(tags)
    return out


def test_ppe_positive_reads_annual_instants_of_the_four_tags():
    """Decision 5 CAPEX_COVERAGE_LOW gate [READING, resolves the spec-test open point on 10-Q facts]: PP&E
    positivity is read like every other balance-sheet fact the engine uses — the latest ANNUAL (10-K / 20-F /
    40-F, fp FY) instant per tag — from PropertyPlantAndEquipmentNet, RealEstateInvestmentPropertyNet (REITs),
    ifrs-full PropertyPlantAndEquipment and ifrs-full InvestmentProperty; positive if any is > 0, False when all
    are <= 0, None (unknown -> no flag) when none is filed annually. A PP&E fact filed only in a 10-Q (APP's
    2022 quarters) does not establish it."""
    P = E._ppe_positive
    assert P(_inst("RealEstateInvestmentPropertyNet", 9.1e9, "2025-12-31")) is True
    assert P(_inst("InvestmentProperty", 2.0e9, "2025-12-31", form="20-F", taxonomy=IF, unit="EUR")) is True
    assert P(_inst("PropertyPlantAndEquipment", 1.0e9, "2025-03-31", form="20-F", taxonomy=IF, unit="EUR")) is True
    assert P(_inst("PropertyPlantAndEquipmentNet", 1.2e8, "2022-09-30", form="10-Q", fp="Q3")) is None
    assert P(_inst("PropertyPlantAndEquipmentNet", 0, "2025-12-31")) is False
    both = _merge_facts(_inst("PropertyPlantAndEquipmentNet", 0, "2025-12-31"),
                        _inst("RealEstateInvestmentPropertyNet", 5.0e9, "2025-12-31"))
    assert P(both) is True
    assert P({"facts": {}}) is None


def test_reconcile_sbc_same_unit_allocated_larger():
    """Decision 6 (option 1): both tags for the period, same unit, Allocated > Share -> Allocated is used,
    tag recorded, reconciled True — JLL FY2025 2.7M vs 112.0M, FY2023 3.4M vs 74.9M; STZ FY2026 67.7M vs
    69.2M and APP FY2025 210.421M vs 211.621M (no tolerance, as ruled)."""
    R = E.reconcile_sbc
    for share, alloc in ((2700000, 112000000), (3400000, 74900000), (67700000, 69200000), (210421000, 211621000)):
        v, unit, tag, rec, _note = R((share, "USD"), (alloc, "USD"))
        assert (v, unit, tag, rec) == (alloc, "USD", SBC_ALLOC, True), (share, alloc, v, unit, tag, rec)


def test_reconcile_sbc_never_across_units():
    """Decision 6 (review P1): JD files ShareBasedCompensation as the issuer's USD translation (677M) and
    Allocated only in CNY (4,804M = the same figure at ~7.1 CNY/USD) — different units are never reconciled:
    Share is kept and the note says 'unit_mismatch' (also BEKE/LI/HTHT)."""
    v, unit, tag, rec, note = E.reconcile_sbc((677000000, "USD"), (4804000000, "CNY"))
    assert (v, unit, tag) == (677000000, "USD", SBC_SHARE) and not rec, (v, unit, tag, rec)
    assert "unit_mismatch" in str(note), note


def test_reconcile_sbc_keeps_share_otherwise():
    """Decision 6: equal values (DD FY2025 38M / 38M), Allocated smaller (ELS FY2023 17.833M vs 14.711M;
    RBC FY2026's 8.6 'dollars' scale error) -> Share kept, not reconciled; Share absent -> Allocated as
    today's fallback (APA FY2025 107M), which is not a reconciliation; nothing -> no value."""
    R = E.reconcile_sbc
    for share, alloc in ((38000000, 38000000), (17833000, 14711000), (34500000, 8.6)):
        v, unit, tag, rec, _ = R((share, "USD"), (alloc, "USD"))
        assert (v, unit, tag) == (share, "USD", SBC_SHARE) and not rec, (share, alloc, v, tag, rec)
    v, unit, tag, rec, _ = R(None, (107000000, "USD"))
    assert (v, unit, tag) == (107000000, "USD", SBC_ALLOC) and not rec, (v, unit, tag, rec)
    v, unit, tag, rec, _ = R((5000000, "USD"), None)
    assert (v, unit, tag) == (5000000, "USD", SBC_SHARE) and not rec
    v, _unit, _tag, rec, _ = R(None, None)
    assert v is None and not rec


FX_EUR = {"from_currency": "EUR", "to_currency": "USD", "converted_fields": ["revenue"],
          "rates": {"2025-12-31": 1.175}, "rates_by_currency": {"EUR": {"2025-12-31": 1.175}}}


def test_override_currency_basis_each_branch():
    """Decision 7: override_currency_basis(o, fx_info, last_filed_unit) — 'no_fx' with no conversion at all
    (verbatim as today); 'declared_usd' for currency 'USD' on a kind-'filing' override (it wins over the
    fallback); 'last_filed_unit_usd' when the last filed value of the field was USD (PUK, CX — any kind);
    otherwise 'converted' (FER: EUR, or no filed value at all); a USD declaration on an estimate is not
    honoured."""
    B = E.override_currency_basis
    o = {"value": 50000000.0, "kind": "filing", "source": "s", "reason": "r", "ack_reason": None, "field": "sbc"}
    assert B(o, None, "EUR") == "no_fx"
    assert B(o, None, None) == "no_fx"
    assert B(dict(o, currency="USD"), FX_EUR, "EUR") == "declared_usd"
    assert B(dict(o, currency="USD"), FX_EUR, "USD") == "declared_usd"
    assert B(dict(o, currency="USD"), FX_EUR, None) == "declared_usd"
    assert B(o, FX_EUR, "USD") == "last_filed_unit_usd"
    assert B(dict(o, kind="estimate"), FX_EUR, "USD") == "last_filed_unit_usd"
    assert B(o, FX_EUR, "EUR") == "converted"
    assert B(o, FX_EUR, None) == "converted"
    assert B(dict(o, kind="estimate", currency="USD"), FX_EUR, "EUR") == "converted"


def test_override_currency_basis_shares():
    """Decision 7: a share-count override is never a currency question — basis 'shares' (TLK's
    99,062,216,600 shares_override at an IDR filer). Without fx_info either 'shares' or 'no_fx' reads
    correctly (both mean verbatim)."""
    B = E.override_currency_basis
    o = {"value": 99062216600.0, "kind": "filing", "source": "s", "reason": "r", "ack_reason": None, "field": "shares"}
    fx_idr = {"from_currency": "IDR", "to_currency": "USD", "rates": {"2024-12-31": 6.2e-05},
              "rates_by_currency": {"IDR": {"2024-12-31": 6.2e-05}}}
    assert B(o, fx_idr, "shares") == "shares"
    assert B(o, None, "shares") in ("shares", "no_fx")


def test_load_overrides_passes_currency_through():
    """Decision 7: load_overrides (engine AND ttm.py) passes an override's `currency` through, upper-cased;
    an override without one carries none."""
    base = tempfile.mkdtemp(prefix="e55_lo_")
    try:
        os.makedirs(os.path.join(base, "TST"))
        with open(os.path.join(base, "TST", "judgment.json"), "w", encoding="utf-8") as fh:
            json.dump({"sbc_override": _o(5000000, currency="usd"), "capex_override": _o(1000000)}, fh)
        saved = E.BASE
        E.BASE = base
        try:
            out = E.load_overrides("TST")
        finally:
            E.BASE = saved
        assert out["sbc"].get("currency") == "USD", out
        assert out["capex"].get("currency") is None, out
        T = importlib.import_module("ttm")
        saved_t = T.BASE
        T.BASE = base
        try:
            out_t = T.load_overrides("TST")
        finally:
            T.BASE = saved_t
        assert out_t["sbc"].get("currency") == "USD", out_t
        assert out_t["capex"].get("currency") is None, out_t
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ===========================================================================
# 7. End-to-end engine runs (engine55_harness, offline)
# ===========================================================================
def _ar():
    return _cached("AR", lambda: run("AR", AR_ARGS))


def test_ar_capex_components_e2e():
    """Decision 4 (AR, unblocked): the CSV prints the summed series — FY2022 943,971,000 (roll-up), FY2023
    1,131,863,000 and FY2024 716,779,000 (mixed filings), FY2025 944,003,000 — with '+'-joined capex_tag
    provenance, the new trailing columns (capex_ppe, capex_intangibles, capex_source, shares_split_factor),
    used_tags.capex / capex_components and capex_provenance with the filing date of every summed fact.
    AR's fake 5.4 Tier B rested on OtherPPE alone (16.4M); CAPEX_COVERAGE_LOW no longer applies."""
    out = _ar()
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    assert list(rows[0].keys())[-4:] == ["capex_ppe", "capex_intangibles", "capex_source", "shares_split_factor"], list(rows[0].keys())
    exp = {"2022-12-31": (943971000, PRIMARY, "rollup"),
           "2023-12-31": (1131863000, AR_COMPONENTS, "components_mixed_filings"),
           "2024-12-31": (716779000, AR_COMPONENTS, "components_mixed_filings"),
           "2025-12-31": (944003000, AR_COMPONENTS, "components")}
    for p, (v, tag, src) in exp.items():
        r = row(rows, p)
        assert f(r["capex"]) == v, (p, r["capex"])
        assert r["capex_tag"] == tag, (p, r["capex_tag"])
        assert f(r["capex_ppe"]) == v and (f(r["capex_intangibles"]) or 0.0) == 0.0, (p, r["capex_ppe"], r["capex_intangibles"])
        assert r["capex_source"] == src, (p, r["capex_source"])
        assert r["shares_split_factor"] == "", (p, r["shares_split_factor"])
    assert n["used_tags"]["capex"] == AR_COMPONENTS, n["used_tags"]
    comps = n["used_tags"]["capex_components"].split("+")
    assert comps == sorted(comps) and {PRIMARY, EXPLORE, ACQ_OG, OTHER_PPE} <= set(comps), comps
    prov = n["capex_provenance"]["2023-12-31"]
    assert prov["ppe_source"] == "components_mixed_filings", prov
    assert prov["ppe"] == {EXPLORE: 964346000, ACQ_OG: 151135000, OTHER_PPE: 16382000}, prov["ppe"]
    assert prov["filed"][ACQ_OG] == "2025-02-12" and prov["filed"][EXPLORE] == "2026-02-11", prov["filed"]
    assert set(n["capex_provenance"]) >= set(exp), sorted(n["capex_provenance"])
    assert "capex" not in (n.get("data_gap") or [])
    assert not flags(n, "CAPEX_COVERAGE_LOW"), flags(n, "CAPEX_COVERAGE_LOW")
    last3 = rows[-3:]
    med = statistics.median(f(r["oe_conservative"]) / f(r["shares_diluted"]) for r in last3)
    assert close(n["base_oe_per_share"], med, rel=1e-12), (n["base_oe_per_share"], med)
    mb = n["market_cap_basis"]
    assert mb["shares_source"] == "diluted_latest" and mb["ads_ratio"] is None and mb["formula"] == FORMULA_PLAIN, mb
    assert n["market_cap_est"] == n["price"] * n["shares_diluted_latest"]


def test_apa_reproduces_its_series_without_the_capex_override_e2e():
    """Decision 4 (APA re-scored override-free): with judgment.json's capex_override removed (sbc_override
    kept), the Explore leg alone gives FY2023-25 2,313M / 2,851M / 2,740M, the capex gap is gone and no
    capex override is applied."""
    j = H.repo_judgment("APA", drop=("capex_override",))
    assert "capex_override" not in j
    out = run("APA", APA_ARGS, judgment=j, ttm={"ttm_oe_per_share": 4.748587570621469})
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    for p, v in {"2023-12-31": 2313000000, "2024-12-31": 2851000000, "2025-12-31": 2740000000}.items():
        r = row(rows, p)
        assert f(r["capex"]) == v and r["capex_tag"] == EXPLORE, (p, r["capex"], r["capex_tag"])
    assert "capex" not in (n.get("data_gap") or []), n.get("data_gap")
    assert not [o for o in n.get("overrides_applied") or [] if o.get("field") == "capex"], n.get("overrides_applied")
    assert not flags(n, "OVERRIDE_APPLIED:capex")
    assert n["base_oe_per_share"] == 4.748587570621469 and n["base_source"] == "ttm_json"


def test_els_capital_improvements_unblocked_e2e():
    """Decision 3 (ELS unblocked): PaymentsForCapitalImprovements fills FY2023-25 — 317,086,000 (beside a $0
    OtherProductiveAssets: zero-guard), 241,279,000, 237,091,000; FY2022 382,077,000 (two filed lines,
    history). DATA_GAP:capex is gone. Decision 6 also reconciles ELS's history FY2022 SBC (8.76M Share vs
    10.5M Allocated) while FY2023's larger Share (17.833M vs 14.711M) is kept."""
    out = run("ELS", ELS_ARGS)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    assert "capex" not in (n.get("data_gap") or []), n.get("data_gap")
    for p, v in (("2023-12-31", 317086000), ("2024-12-31", 241279000), ("2025-12-31", 237091000), ("2022-12-31", 382077000)):
        assert f(row(rows, p)["capex"]) == v, (p, row(rows, p)["capex"])
    assert CAP_IMPROVEMENTS in row(rows, "2023-12-31")["capex_tag"]
    assert row(rows, "2024-12-31")["capex_tag"] == CAP_IMPROVEMENTS and row(rows, "2025-12-31")["capex_tag"] == CAP_IMPROVEMENTS
    assert row(rows, "2024-12-31")["capex_source"] == "components"
    r22, r23 = row(rows, "2022-12-31"), row(rows, "2023-12-31")
    assert f(r22["sbc"]) == 10500000 and r22["sbc_tag"] == SBC_ALLOC, (r22["sbc"], r22["sbc_tag"])
    assert f(r23["sbc"]) == 17833000 and r23["sbc_tag"] == SBC_SHARE, (r23["sbc"], r23["sbc_tag"])
    fl = flags(n, "SBC_TAG_RECONCILED")
    assert len(fl) == 1 and "2022" in fl[0], fl


def test_rbc_rollup_then_capital_improvements_without_override_e2e():
    """Decisions 3 + 4 (RBC re-run without its capex override): FY2023 42.0M from the roll-up (the re-tagged
    PaymentsForCapitalImprovements copy is not added), FY2024-26 33.2M / 49.8M / 73.1M from
    PaymentsForCapitalImprovements; no capex gap."""
    out = run("RBC", RBC_ARGS, judgment={}, ttm={"ttm_oe_per_share": 11.351216719364736})
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    exp = {"2023-04-01": (42000000, PRIMARY), "2024-03-30": (33200000, CAP_IMPROVEMENTS),
           "2025-03-29": (49800000, CAP_IMPROVEMENTS), "2026-03-28": (73100000, CAP_IMPROVEMENTS)}
    for p, (v, tag) in exp.items():
        r = row(rows, p)
        assert f(r["capex"]) == v and r["capex_tag"] == tag, (p, r["capex"], r["capex_tag"])
    assert "capex" not in (n.get("data_gap") or [])
    assert not flags(n, "OVERRIDE_SUPERSEDED_BY_FILED_TAG")


def test_rbc_override_superseded_by_filed_tag_e2e():
    """Decision 3 [ADDITION — the WY shape] on RBC's real override: the 73.1M capex_override now fills
    nothing (an override never replaces a filed value) and FY2024's filed 33.2M is 0.45x of it (outside
    [0.5, 2]) -> OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex naming FY2024, recorded in
    override_checks.capex.superseded_periods; FY2025 (1.47x) and FY2026 (1.0x) are not superseded."""
    out = run("RBC", RBC_ARGS, judgment={"capex_override": _o(73100000)}, ttm={"ttm_oe_per_share": 11.351216719364736})
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    for p, v in (("2024-03-30", 33200000), ("2025-03-29", 49800000), ("2026-03-28", 73100000)):
        r = row(rows, p)
        assert f(r["capex"]) == v and r["capex_tag"] == CAP_IMPROVEMENTS, (p, r["capex"], r["capex_tag"])
    assert not [o for o in n.get("overrides_applied") or [] if o.get("field") == "capex"]
    fl = flags(n, "OVERRIDE_SUPERSEDED_BY_FILED_TAG:capex")
    assert len(fl) == 1 and "2024" in fl[0], fl
    sp = json.dumps(n["override_checks"]["capex"]["superseded_periods"])
    assert "2024" in sp and "2025-03-29" not in sp and "2026-03-28" not in sp, sp


def test_pr_component_capex_e2e():
    """Decision 4 (PR, first on the retro-check list): FY2023-25 capex = Explore + AcquireOG + OtherPPE =
    1,793,670,000 / 3,120,640,000 / 3,050,155,000 (5.4 read OtherPPE alone: 34.5M / 12.8M / 13.7M and
    printed a fake Tier S 32.7%). The base becomes the FY2025 OE/share 0.6663 — no Tier S."""
    out = run("PR", PR_ARGS)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    for p, v in (("2023-12-31", 1793670000), ("2024-12-31", 3120640000), ("2025-12-31", 3050155000)):
        r = row(rows, p)
        assert f(r["capex"]) == v and r["capex_tag"] == AR_COMPONENTS, (p, r["capex"], r["capex_tag"])
    assert close(n["base_oe_per_share"], 0.6662539758541673, rel=1e-9), n["base_oe_per_share"]
    assert n["tier_by_numbers"] != "S", n["tier_by_numbers"]


def test_jll_sbc_reconciled_e2e():
    """Decision 6 (JLL re-run; capex_override kept): SBC FY2023-25 74.9M / 95.1M / 112.0M from
    AllocatedShareBasedCompensationExpense (Share tagged 3.4M / 2.3M / 2.7M), history years too (FY2021
    80.1M, FY2022 75.3M), one SBC_TAG_RECONCILED flag listing every reconciled year, sbc_provenance per
    period; the base falls to the FY2024 OE/share 9.8115 (from 11.7299)."""
    out = run("JLL", JLL_ARGS, judgment=JLL_J)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    for p, v in (("2021-12-31", 80100000), ("2022-12-31", 75300000), ("2023-12-31", 74900000),
                 ("2024-12-31", 95100000), ("2025-12-31", 112000000)):
        r = row(rows, p)
        assert f(r["sbc"]) == v and r["sbc_tag"] == SBC_ALLOC, (p, r["sbc"], r["sbc_tag"])
    for p in ("2023-12-31", "2024-12-31", "2025-12-31"):
        assert row(rows, p)["capex_tag"] == "OVERRIDE" and f(row(rows, p)["capex"]) == 215600000
    fl = flags(n, "SBC_TAG_RECONCILED")
    assert len(fl) == 1, fl
    for y in ("2021", "2022", "2023", "2024", "2025"):
        assert y in fl[0], fl[0]
    prov = n["sbc_provenance"]["2025-12-31"]
    assert prov["reconciled"] is True and prov["used"] == SBC_ALLOC, prov
    assert list(prov["share"]) == [2700000, "USD"] and list(prov["allocated"]) == [112000000, "USD"], prov
    assert close(n["base_oe_per_share"], 9.811461175886876, rel=1e-9), n["base_oe_per_share"]


def test_ato_sbc_reconciled_stays_tier_f_e2e():
    """Decision 6 (ATO re-check): Allocated 23.7M / 25.4M / 33.2M replaces Share 10.2M / 10.7M / 12.7M for
    FY2023-25; the median OE/share stays negative (-8.0488) -> Tier F."""
    out = run("ATO", ATO_ARGS)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    for p, v in (("2023-09-30", 23700000), ("2024-09-30", 25400000), ("2025-09-30", 33200000)):
        r = row(rows, p)
        assert f(r["sbc"]) == v and r["sbc_tag"] == SBC_ALLOC, (p, r["sbc"], r["sbc_tag"])
    assert flags(n, "SBC_TAG_RECONCILED")
    assert n["tier_by_numbers"] == "F", n["tier_by_numbers"]
    assert close(n["base_oe_per_share"], -8.048799339735108, rel=1e-9), n["base_oe_per_share"]


def _dd():
    return _cached("DD", lambda: run("DD", DD_ARGS, judgment={},
                                     ttm={"ttm_oe_per_share": 4.803206997084548, "ttm_ocf": 1041000000,
                                          "ttm_capex": 339000000, "ttm_sbc": 43000000}))


def test_dd_split_basis_adjusted_e2e():
    """Decision 2 §2 (DD, unblocked with no override): the 0.333 ratio filed for 2026-06-30 post-dates every
    filing behind the history and the 2026-07-31 dei (135,042,975 / 419,200,000 = 0.322) confirms it ->
    every history count x 1/3 (shares_split_factor), SHARE_BASIS_ADJUSTED '1-for-3', shares_diluted_latest
    139,733,333.33, market_cap_basis.shares_source diluted_latest_split_adjusted, cap ~$18.5B (was $55.6B);
    the TTM pin 4.8032 (already post-split) and the Tier D result are unchanged; no divergence fallback."""
    out = _dd()
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-2000:]
    assert n["base_oe_per_share"] == 4.803206997084548 and n["base_source"] == "ttm_json"
    assert close(n["shares_diluted_latest"], 419200000 / 3, rel=1e-12), n["shares_diluted_latest"]
    mb = n["market_cap_basis"]
    assert mb["shares_source"] == "diluted_latest_split_adjusted", mb
    assert close(mb["shares_used"], 419200000 / 3, rel=1e-12) and mb["ads_ratio"] is None, mb
    assert close(n["market_cap_est"], 132.7 * 419200000 / 3, rel=1e-12), n["market_cap_est"]
    assert abs(n["market_cap_est"] - 18.5e9) < 0.1e9
    fl = flags(n, "SHARE_BASIS_ADJUSTED")
    assert len(fl) == 1 and "1-for-3" in fl[0] and "2026-06-30" in fl[0], fl
    assert not flags(n, "SHARE_BASIS_DIVERGENCE")
    assert n["share_basis"]["split"], n["share_basis"]
    assert n["share_scale"]["defect"] is False, n["share_scale"]
    for p, filed_count in (("2023-12-31", 449900000), ("2024-12-31", 419200000), ("2025-12-31", 419200000)):
        r = row(rows, p)
        assert close(f(r["shares_split_factor"]), 1 / 3, rel=1e-12), (p, r["shares_split_factor"])
        assert close(f(r["shares_diluted"]), filed_count / 3, rel=1e-12), (p, r["shares_diluted"])
        assert close(f(r["oe_per_share"]), f(r["oe_conservative"]) / f(r["shares_diluted"]), rel=1e-12), p
    assert n["tier_by_numbers"] == "D"
    assert close(n["implied_irr_weighted"], 0.0658898036251695, rel=1e-12), n["implied_irr_weighted"]
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n), rel=1e-12)


def test_ntnx_scale_guard_blocks_without_the_pin_e2e():
    """Decision 2 §1 (guard fires pre-override): NTNX's thousands-filed diluted counts (292,183 vs dei
    270,570,179) with no declared pin -> exit 4, gap key 'share_scale' (uncovered — no override can cover
    it), flag 'DATA_GAP:shares — SHARE_SCALE …', no tier; share_scale records the defect and the dei-based
    factor 1,000, and the market cap already uses the corrected count (~$20.4B, not $20.4M)."""
    out = run("NTNX", NTNX_ARGS, judgment={})
    n = out["numbers"]
    assert out["exit"] == 4, (out["exit"], out["stdout"][-1500:])
    assert "share_scale" in n["data_gap"] and "share_scale" in n["data_gap_uncovered"], (n["data_gap"], n["data_gap_uncovered"])
    assert flags(n, SCALE_GAP), n["fragility_flags"]
    assert n["tier_by_numbers"] is None
    ss = n["share_scale"]
    assert ss["defect"] is True and ss["tests"]["b"] is True and ss["rescued_by_pin"] is False, ss
    assert ss["scale_factor"] == 1000 and ss["factor_basis"] == "dei", ss
    assert ss["dei_count"] == 270570179 and ss["dei_date"] == "2026-08-31", ss
    assert close(n["market_cap_est"], 69.98 * 292183 * 1000, rel=1e-12), n["market_cap_est"]


def test_ntnx_scale_guard_ttm_pin_does_not_rescue_e2e():
    """Decision 2 §1: a --ttm pin does not rescue the guard (ttm.py divides by the same mis-scaled counts);
    only a declared --base-oe-ps pin does."""
    out = run("NTNX", NTNX_ARGS + ["--ttm"], judgment={}, ttm={"ttm_oe_per_share": NTNX_PIN})
    assert out["exit"] == 4, out["exit"]
    assert "share_scale" in out["numbers"]["data_gap"]


def test_ntnx_scale_guard_rescued_by_its_declared_pin_e2e():
    """Decision 2 §1 (existing overrides reproduce): with its declared base pin 1.3553 NTNX scores Tier D as
    recorded (weighted IRR 5.71%) — no gap, SHARE_SCALE_SUSPECT [ADDITION] keeps the defect visible,
    share_scale.scale_factor 1,000 (dei), market cap ~$20.45B on diluted_latest_scale_corrected, and
    net_debt_to_normalized_oe on the same corrected count (None here: NTNX's net debt is unknown —
    DEBT_TAGS_BLANK — so the identity checks that no ratio is invented)."""
    out = run("NTNX", NTNX_ARGS + ["--base-oe-ps", repr(NTNX_PIN)], judgment=NTNX_J)
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert n["base_oe_per_share"] == NTNX_PIN
    assert "share_scale" not in (n.get("data_gap") or [])
    assert flags(n, "SHARE_SCALE_SUSPECT") and not flags(n, SCALE_GAP), n["fragility_flags"]
    ss = n["share_scale"]
    assert ss["defect"] is True and ss["rescued_by_pin"] is True, ss
    assert ss["scale_factor"] == 1000 and ss["factor_basis"] == "dei", ss
    mb = n["market_cap_basis"]
    assert mb["shares_source"] == "diluted_latest_scale_corrected" and close(mb["shares_used"], 292183000, rel=1e-12), mb
    assert close(n["market_cap_est"], 20446966340.0, rel=1e-12), n["market_cap_est"]
    assert n["tier_by_numbers"] == "D"
    assert close(n["implied_irr_weighted"], 0.057127403486683326, rel=1e-9), n["implied_irr_weighted"]
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n), rel=1e-12)


def test_tem_scale_guard_e2e():
    """Decision 2 §1 (TEM): with no dei at all, test (a) fires (61x price) — exit 4 / 'share_scale' without
    the pin; with its declared pin -3.9324 the run emits Tier F, SHARE_SCALE_SUSPECT, and the pin-derived
    factor 1,000 puts the cap at ~$11.28B (diluted_latest_scale_corrected)."""
    blocked = run("TEM", TEM_ARGS, judgment={})
    assert blocked["exit"] == 4 and "share_scale" in blocked["numbers"]["data_gap"], blocked["exit"]
    assert flags(blocked["numbers"], SCALE_GAP)
    out = run("TEM", TEM_ARGS + ["--base-oe-ps", repr(TEM_PIN)], judgment=TEM_J)
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert n["base_oe_per_share"] == TEM_PIN and n["tier_by_numbers"] == "F", (n["base_oe_per_share"], n["tier_by_numbers"])
    assert flags(n, "SHARE_SCALE_SUSPECT")
    ss = n["share_scale"]
    assert ss["defect"] and ss["tests"]["a"] and ss["rescued_by_pin"] is True, ss
    assert ss["scale_factor"] == 1000 and ss["factor_basis"] == "pin", ss
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest_scale_corrected", n["market_cap_basis"]
    assert close(n["market_cap_est"], 11278366080.0, rel=1e-12), n["market_cap_est"]


def test_viv_scale_guard_e2e():
    """Decision 2 §1 (VIV). FY2025 has only a basic count, so the 5.4 basic-share rule still gaps it; the
    test declares the FY2025 shares_override the re-score plan expects (3,195,606,352 from the 20-F EPS note)
    — the choice the task brief left open — and the base_override the folder declares for its pin (ruling E1).
    Without the pin: exit 4 / 'share_scale' (the 5.4 engine printed a fake Tier S at IRR 200% here). Without the
    shares_override but with the pin: the only gap is 'shares'. With both: SHARE_SCALE_SUSPECT, no scale factor
    (dei ratio 1, pin ratio 1,615.6), cap = price x shares / 2, and [ruling E2] the share series breaks scale
    inside the growth window (FY2022 3,195,606,352 -> FY2023 1,658,604 ... FY2024 1,643,132 -> FY2025
    3,195,606,352), so the share-count CAGR and the -97.7%/yr OE/share CAGR leave the blend: with no revenue
    component either, g_blend is the engine's 3% default and the weighted IRR is 18.73% (Tier B) where the
    artefact pinned g_base at the -5% floor (14.57%, Tier C). [ruling E3] the dei exists and test (b) passed,
    so net_debt_to_normalized_oe stands."""
    blocked = run("VIV", VIV_ARGS, judgment=viv_j(True))
    assert blocked["exit"] == 4 and "share_scale" in blocked["numbers"]["data_gap"], (blocked["exit"], blocked["numbers"].get("data_gap"))
    assert flags(blocked["numbers"], SCALE_GAP)
    pinned_args = VIV_ARGS + ["--base-oe-ps", repr(VIV_PIN)]
    gap = run("VIV", pinned_args, judgment=viv_j(False))
    assert gap["exit"] == 4, gap["exit"]
    assert "shares" in gap["numbers"]["data_gap_uncovered"] and "share_scale" not in gap["numbers"]["data_gap"], gap["numbers"]["data_gap"]
    out = run("VIV", pinned_args, judgment=viv_j(True))
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert n["base_oe_per_share"] == VIV_PIN and n["tier_by_numbers"] == "B", (n["base_oe_per_share"], n["tier_by_numbers"])
    assert close(n["implied_irr_weighted"], 0.187316425136128, rel=1e-9), n["implied_irr_weighted"]
    assert n["g_base"] == 0.03 and n["share_cagr"] is None and n["share_count_adj"] == 0.0, (n["g_base"], n["share_cagr"])
    assert n["growth_components_adjusted"]["oe_ps_cagr_2y"] is None, n["growth_components_adjusted"]
    fl = flags(n, "SHARE_SCALE_SUSPECT")
    assert len(fl) == 1 and "breaks scale inside the growth window" in fl[0] and "-97.7%/yr" in fl[0], fl
    assert not flags(n, "DILUTION") and not flags(n, "BUYBACK_TAILWIND"), n["fragility_flags"]
    ss = n["share_scale"]
    assert ss["defect"] and ss["tests"]["a"] and not ss["tests"]["b"], ss
    assert ss["scale_factor"] is None and ss["rescued_by_pin"] is True and ss["pin_rejected"] is None, ss
    assert ss["growth_inputs_dropped"] == ["share_cagr", "oe_ps_cagr_2y"], ss
    assert [(b["from_period"], b["to_period"]) for b in ss["scale_breaks"]] == [("2022-12-31", "2023-12-31"), ("2024-12-31", "2025-12-31")], ss
    assert ss["leverage_unverifiable"] is False, ss
    assert n["shares_diluted_latest"] == 3195606352
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest", n["market_cap_basis"]
    assert n["market_cap_est"] == E.market_cap_est(12.26, 3195606352, 2.0) == (12.26 * 3195606352) / 2.0
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n, 2.0), rel=1e-12)


def test_share_class_declaration_blocks_bnt_e2e():
    """Decision 2 §5 (flag route): a share_class_mismatch declaration in judgment.json — the bare `true` the
    ruling spells and the object {value, source, reason} — adds the uncovered gap key 'share_class', flag
    'DATA_GAP:shares — SHARE_CLASS_MISMATCH: … (<source or no source given>) …', exit 4, no tier, and the
    record share_class_mismatch {declared, source, reason}."""
    src = "FY2025 20-F Notes 23/25 (test)"
    why = "test: the filed count is the ordinary class, not the traded ADS"
    for decl, text in ((True, "no source given"), ({"value": True, "source": src, "reason": why}, src)):
        out = run("BNT", (), judgment={"share_class_mismatch": decl})
        n = out["numbers"]
        assert out["exit"] == 4, (decl, out["exit"])
        assert "share_class" in n["data_gap"] and "share_class" in n["data_gap_uncovered"], n["data_gap"]
        fl = flags(n, CLASS_GAP)
        assert len(fl) == 1 and text in fl[0], fl
        assert n["tier_by_numbers"] is None
        rec = n["share_class_mismatch"]
        assert rec["declared"] is True, rec
        if isinstance(decl, dict):
            assert rec["source"] == src and rec["reason"] == why, rec


def test_share_class_declaration_blocks_a_clean_name_and_nothing_rescues_it():
    """Decision 2 §5: on a clean name (CCJ, no other gap) the declaration alone blocks — data_gap is exactly
    ['share_class'] — and a declared base pin does not rescue it; a falsy value is no declaration."""
    j = dict(CCJ_J, share_class_mismatch=True)
    out = run("CCJ", H.recorded_args(recorded_matching_fixture("CCJ")), judgment=j)
    assert out["exit"] == 4 and set(out["numbers"]["data_gap"]) == {"share_class"}, (out["exit"], out["numbers"].get("data_gap"))
    pinned = run("CCJ", H.recorded_args(H.recorded("CCJ")) + ["--base-oe-ps", "1.095035000734019"], judgment=j)
    assert pinned["exit"] == 4 and "share_class" in pinned["numbers"]["data_gap"]
    ok = run("CCJ", H.recorded_args(H.recorded("CCJ")), judgment=dict(CCJ_J, share_class_mismatch=False))
    assert ok["exit"] == 0 and "share_class" not in (ok["numbers"].get("data_gap") or [])


def test_tlk_ads_market_cap_e2e():
    """Decision 1 (TLK unblocked): market_cap_est = $11.03 x 99,062,216,600 / 100 ~ $10.93B (5.4 printed
    $1,092.66B), market_cap_basis {shares_used, shares_source diluted_latest, ads_ratio 100, formula price x
    shares / ads_ratio}; net_debt_to_normalized_oe on the per-ADS basis (normalized_oe_total / 100). Decision
    7: the shares override's basis is 'shares', the $0 SBC override (no filed value) is 'converted'."""
    out = run("TLK", TLK_ARGS, judgment=TLK_J)
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert n["price"] == 11.03 and n["shares_diluted_latest"] == 99062216600
    assert n["market_cap_est"] == (11.03 * 99062216600) / 100.0
    assert abs(n["market_cap_est"] - 10.93e9) < 0.005e9, n["market_cap_est"]
    mb = n["market_cap_basis"]
    assert mb["ads_ratio"] == 100.0 and mb["shares_source"] == "diluted_latest" and mb["formula"] == FORMULA_ADS, mb
    assert mb["shares_used"] == 99062216600, mb
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n, 100.0), rel=1e-12)
    assert n["override_checks"]["shares"]["currency_basis"] == "shares", n["override_checks"]
    assert n["override_checks"]["sbc"]["currency_basis"] == "converted", n["override_checks"]


def test_wf_ads_market_cap_in_scope():
    """Decision 1 (WF 'in scope'): the cap is price x shares / 3 (~$17.3B, under $40B; 5.4 printed $52.0B),
    recorded with ads_ratio 3 — also on a run that still gaps on the 5.4 basic-share rule."""
    n = run("WF", WF_ARGS, judgment=WF_J)["numbers"]
    assert n["market_cap_est"] == (n["price"] * n["shares_diluted_latest"]) / 3.0, (n["market_cap_est"], n["price"], n["shares_diluted_latest"])
    assert n["market_cap_est"] < 40e9
    assert n["market_cap_basis"]["ads_ratio"] == 3.0, n["market_cap_basis"]


def test_vod_intangible_leg_e2e():
    """Decision 5 (VOD re-run; its S->D override stands): IFRS PurchaseOfIntangibleAssets EUR 2,799M /
    2,641M / 2,375M (FY2023-25) is added on the IFRS PP&E roll-up and converted at the period rates; base
    $4.869 -> $3.8174/ADS; weighted IRR 32.57% -> 26.04% at $15.51 (IV@25 $16.22) — still Tier S by numbers,
    as DESIGN §3-5 [READING] reports to Andrew. Decision 1: cap $40.56B (out of scope) and HIGH_NET_DEBT
    (net debt ~4.6x normalized OE on the per-ADS basis). Capex/D&A 76%/66%/62%: no CAPEX_COVERAGE_LOW."""
    out = run("VOD", VOD_ARGS, judgment=VOD_J)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    rates = H.load_fixture("VOD")["fx_rates"]["EUR"]
    for p, eur in (("2023-03-31", 2799e6), ("2024-03-31", 2641e6), ("2025-03-31", 2375e6)):
        r = row(rows, p)
        assert close(f(r["capex_intangibles"]), eur * rates[p], rel=1e-9), (p, r["capex_intangibles"])
        assert close(f(r["capex"]), f(r["capex_ppe"]) + f(r["capex_intangibles"]), rel=1e-12), p
        assert r["capex_tag"] == f"{IFRS_PPE}+{IFRS_INTANG}", (p, r["capex_tag"])
    assert n["market_cap_est"] == (15.51 * 26149000000) / 10.0 and n["market_cap_est"] >= 40e9
    assert close(n["base_oe_per_share"], 3.8173568929321204, rel=1e-9), n["base_oe_per_share"]
    assert close(n["implied_irr_weighted"], 0.26039012954471363, abs_=1e-6), n["implied_irr_weighted"]
    assert n["implied_irr_weighted"] < 0.32569825322923396 and n["tier_by_numbers"] == "S"
    assert close(n["weighted"]["iv_at_25"], 16.221873230136197, abs_=1e-4), n["weighted"]["iv_at_25"]
    assert flags(n, "HIGH_NET_DEBT"), n["fragility_flags"]
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n, 10.0), rel=1e-12)
    assert not flags(n, "CAPEX_COVERAGE_LOW")


def test_iesc_stays_on_the_filed_basis():
    """Decision 2 (unexecutable acceptance item): IESC has no split-ratio fact and its latest dei (19,924,356
    on 2026-07-27) is pre-split, within 25% of the FY2025 diluted 20,182,797 — no split adjustment, no
    divergence fallback, the cap stays price x filed shares. It stays blocked in the queue."""
    n = run("IESC", IESC_ARGS)["numbers"]
    assert not n["share_basis"]["split"] and not n["share_basis"]["divergence"], n["share_basis"]
    assert not flags(n, "SHARE_BASIS_ADJUSTED") and not flags(n, "SHARE_BASIS_DIVERGENCE")
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest"
    assert n["shares_diluted_latest"] == 20182797
    assert n["market_cap_est"] == n["price"] * 20182797


def test_market_cap_basis_names_the_universe_fallback_e2e():
    """Decision 1 record (resolves the make_score open point on the fallback basis): with no price the engine
    keeps 5.4's universe.csv market-cap fallback, and market_cap_basis says so — shares_source
    'universe_market_cap', shares_used null (no share count was used), the universe formula — instead of
    naming a diluted count it never multiplied. The run is a DATA_GAP:price (no tier; a price-only gap exits 3)."""
    fx = copy.deepcopy(H.load_fixture("CCJ"))
    fx["price"] = None
    fx["universe_row"] = dict(fx.get("universe_row") or {"ticker": "CCJ", "name": "Cameco", "sector": "", "cik": str(fx["cik"])},
                              price="", market_cap="35000000000")
    out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
    n = out["numbers"]
    assert out["exit"] == 3 and n.get("data_gap_uncovered") == ["price"], (out["exit"], n.get("data_gap_uncovered"))
    assert n["market_cap_est"] == 35000000000.0, n["market_cap_est"]
    mb = n["market_cap_basis"]
    assert mb["shares_used"] is None and mb["shares_source"] == "universe_market_cap", mb
    assert str(mb["formula"]).startswith("universe.csv market_cap"), mb
    # the pin-rescued share-scale flag names that basis too (NTNX with no price: no count was multiplied)
    fx = copy.deepcopy(H.load_fixture("NTNX"))
    fx["price"] = None
    fx["universe_row"] = dict(fx.get("universe_row") or {"ticker": "NTNX", "name": "Nutanix", "sector": "", "cik": str(fx["cik"])},
                              price="", market_cap="20000000000")
    out = run("NTNX", NTNX_ARGS + ["--base-oe-ps", repr(NTNX_PIN)], judgment=NTNX_J, fixture=fx)
    n = out["numbers"]
    assert out["exit"] == 3 and n["market_cap_basis"]["shares_source"] == "universe_market_cap", (out["exit"], out["stdout"][-800:])
    fl = flags(n, "SHARE_SCALE_SUSPECT")
    assert len(fl) == 1 and "universe.csv's market cap" in fl[0], fl


def test_fx_record_names_the_intangible_leg_and_the_verbatim_set_e2e():
    """Decisions 5 + 7 records (resolves the engine open points): when the intangible leg is FX-converted
    (VOD: EUR intangibles), fx_conversion.converted_fields names 'capex_intang' like every other converted
    series; fx_conversion.overrides_usd_verbatim is written whenever fx_info exists — {} when no override was
    used verbatim (VOD declares none; FER's EUR override converts), {field: basis} otherwise."""
    fx = run("VOD", VOD_ARGS, judgment=VOD_J)["numbers"]["fx_conversion"]
    assert "capex_intang" in fx["converted_fields"], fx["converted_fields"]
    assert fx.get("overrides_usd_verbatim") == {}, fx
    fer = run("FER", FER_ARGS, judgment=fer_j(50000000))["numbers"]["fx_conversion"]
    assert fer.get("overrides_usd_verbatim") == {}, fer
    fer = run("FER", FER_ARGS, judgment=fer_j(50000000, currency="USD"))["numbers"]["fx_conversion"]
    assert fer.get("overrides_usd_verbatim") == {"sbc": "declared_usd"}, fer


def test_puk_usd_sbc_override_used_verbatim_e2e():
    """Decision 7 (PUK re-run): the engine's SBC series are the issuer's USD translations (last filed unit
    USD), so the $85M sbc_override is used verbatim — not multiplied by a GBP rate — fills FY2023-25 and
    clears DATA_GAP:sbc; override_checks.sbc.currency_basis and fx_conversion.overrides_usd_verbatim record
    'last_filed_unit_usd'. Decision 1: cap = $23.81 x 2,592,000,000 / 2."""
    out = run("PUK", (), judgment=PUK_J)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert "sbc" not in (n.get("data_gap_uncovered") or [])
    for r in rows[-3:]:
        assert f(r["sbc"]) == 85000000 and r["sbc_tag"] == "OVERRIDE", (r["period_end"], r["sbc"], r["sbc_tag"])
    assert n["override_checks"]["sbc"]["currency_basis"] == "last_filed_unit_usd", n["override_checks"]
    fx = n["fx_conversion"]
    assert (fx.get("overrides_usd_verbatim") or {}).get("sbc") == "last_filed_unit_usd", fx
    assert "sbc" not in (fx.get("overrides_converted") or []), fx
    assert n["market_cap_est"] == (23.81 * 2592000000) / 2.0


def test_cx_usd_sbc_override_and_cpo_dei_e2e():
    """Decision 7 (CX re-run): the $55M sbc_override is used verbatim (last filed unit USD) and fills
    FY2022-24. Decision 2: CX's dei 14,507,429,244 counts CPOs (3 shares each) — at a 20-F filer the
    divergence is recorded in share_basis.divergence with no flag and no switch, so the cap stays $10.25 x
    44,065,652,000 / 30 ~ $15.06B (the dei route would print $4.96B); test (b) does not fire (ratio 3.04)."""
    out = run("CX", CX_ARGS, judgment=CX_J)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    for r in rows[-3:]:
        assert f(r["sbc"]) == 55000000 and r["sbc_tag"] == "OVERRIDE", (r["period_end"], r["sbc"], r["sbc_tag"])
    assert n["override_checks"]["sbc"]["currency_basis"] == "last_filed_unit_usd", n["override_checks"]
    assert (n["fx_conversion"].get("overrides_usd_verbatim") or {}).get("sbc") == "last_filed_unit_usd", n["fx_conversion"]
    assert not flags(n, "SHARE_BASIS_DIVERGENCE"), flags(n, "SHARE_BASIS_DIVERGENCE")
    assert n["share_basis"]["divergence"], n["share_basis"]
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest", n["market_cap_basis"]
    assert n["market_cap_est"] == (10.25 * 44065652000) / 30.0
    assert abs(n["market_cap_est"] - 15.06e9) < 0.005e9 and n["market_cap_est"] < 40e9
    assert n["share_scale"]["defect"] is False, n["share_scale"]


def test_fer_eur_override_still_converted_e2e():
    """Decision 7 (FER-style regression): a EUR sbc_override (synthetic EUR 50M, no currency key, no filed SBC
    to read a unit from) is still FX-converted at each period's rate — $53.33M / $55.25M / $51.945M /
    $58.75M for FY2022-25; overrides_converted lists sbc; currency_basis 'converted'; the capex override
    converts as before. Decision 5: FER's capex (the converted override) is 47%/42%/38% of D&A with IFRS PP&E
    EUR 1,012M positive -> CAPEX_COVERAGE_LOW."""
    out = run("FER", FER_ARGS, judgment=fer_j(50000000))
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    rates = H.load_fixture("FER")["fx_rates"]["EUR"]
    for p, literal in (("2022-12-31", 53.33e6), ("2023-12-31", 55.25e6), ("2024-12-31", 51.945e6), ("2025-12-31", 58.75e6)):
        r = row(rows, p)
        assert r["sbc_tag"] == "OVERRIDE", (p, r["sbc_tag"])
        assert close(f(r["sbc"]), 50000000 * rates[p], rel=1e-12) and abs(f(r["sbc"]) - literal) < 1.0, (p, r["sbc"])
        assert close(f(r["capex"]), 187000000 * rates[p], rel=1e-12), (p, r["capex"])
    fx = n["fx_conversion"]
    assert "sbc" in fx["overrides_converted"] and "capex" in fx["overrides_converted"], fx
    assert n["override_checks"]["sbc"]["currency_basis"] == "converted", n["override_checks"]
    assert (fx.get("overrides_usd_verbatim") or {}).get("sbc") not in ("declared_usd", "last_filed_unit_usd"), fx
    fl = flags(n, "CAPEX_COVERAGE_LOW")
    assert len(fl) == 1 and all(y in fl[0] for y in ("2023", "2024", "2025")), fl


def test_fer_declared_usd_override_used_verbatim_e2e():
    """Decision 7: the same override declared currency 'USD' (kind filing) is used verbatim — 50,000,000 in
    every filled period — with basis 'declared_usd' recorded in override_checks and overrides_usd_verbatim,
    and it leaves overrides_converted (the undeclared capex override still converts)."""
    out = run("FER", FER_ARGS, judgment=fer_j(50000000, currency="USD"))
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    for p in ("2022-12-31", "2023-12-31", "2024-12-31", "2025-12-31"):
        assert f(row(rows, p)["sbc"]) == 50000000, (p, row(rows, p)["sbc"])
    fx = n["fx_conversion"]
    assert n["override_checks"]["sbc"]["currency_basis"] == "declared_usd", n["override_checks"]
    assert (fx.get("overrides_usd_verbatim") or {}).get("sbc") == "declared_usd", fx
    assert "sbc" not in (fx.get("overrides_converted") or []) and "capex" in fx["overrides_converted"], fx


def test_fer_usd_declaration_on_an_estimate_is_not_honoured_e2e():
    """Decision 7 ('kind filing only'): currency 'USD' on an estimate is not a USD filing figure — the engine
    converts it (make_score refuses the declaration outright)."""
    out = run("FER", FER_ARGS, judgment=fer_j(50000000, kind="estimate", currency="USD"))
    n, rows = out["numbers"], out["rows"]
    rates = H.load_fixture("FER")["fx_rates"]["EUR"]
    assert close(f(row(rows, "2025-12-31")["sbc"]), 50000000 * rates["2025-12-31"], rel=1e-12)
    assert n["override_checks"]["sbc"]["currency_basis"] == "converted", n["override_checks"]


def _no_reconcile(share, allocated):
    """Test stand-in for E.reconcile_sbc that never reconciles (the 5.4 priority merge)."""
    if share is not None:
        return share[0], share[1], SBC_SHARE, False, "test: reconciliation disabled"
    if allocated is not None:
        return allocated[0], allocated[1], SBC_ALLOC, False, "test: reconciliation disabled"
    return None, None, None, False, "test: reconciliation disabled"


def _patch_55_off(mod):
    mod.CAPEX_INTANGIBLE_TAGS = []
    mod.reconcile_sbc = _no_reconcile


def _same_rows(rows, rec_rows, who, cols=("capex", "sbc", "ocf", "shares_diluted", "oe_conservative"), skip=()):
    rec = {r["period_end"]: r for r in rec_rows}
    assert sorted(r["period_end"] for r in rows) == sorted(rec), (who, [r["period_end"] for r in rows], sorted(rec))
    for r in rows:
        if r["period_end"] in skip:
            continue
        for c in cols:
            assert f(r[c]) == f(rec[r["period_end"]][c]), (who, r["period_end"], c, r[c], rec[r["period_end"]][c])


def test_ccj_numerically_identical_to_its_recorded_run():
    """Release (non-trigger folders reproduce): CCJ has an IFRS PP&E roll-up every year, no intangible tag, IFRS
    SBC only, no split fact, dei / diluted ~ 1 and ads_ratio 1.0 (exact division) — base, g_base, every
    scenario's IV@10/12/15 and IRR, the weighted case, tier D, the market cap and net debt / normalized OE are
    bit-identical to the recorded (pre-5.4) run. engine_release 5.5.0, engine_version 5, new keys and the
    content_hash differ by design."""
    rec = recorded_matching_fixture("CCJ")
    out = run("CCJ", H.recorded_args(rec), judgment=CCJ_J)
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert_same_math(n, rec, "CCJ")
    assert n["market_cap_est"] == rec["market_cap_est"] == 35456212000.0
    assert n["diagnostics"]["net_debt_to_normalized_oe"] == rec["diagnostics"]["net_debt_to_normalized_oe"]
    assert n["engine_release"] == "5.5.0" and n["engine_version"] == 5
    for prefix in ("CAPEX_COVERAGE_LOW", "SBC_TAG_RECONCILED", "SHARE_", "OVERRIDE_SUPERSEDED"):
        assert not flags(n, prefix), (prefix, flags(n, prefix))
    assert n["share_scale"]["defect"] is False and not n["share_basis"]["split"], (n["share_scale"], n["share_basis"])
    _same_rows(out["rows"], recorded_rows("CCJ"), "CCJ")


def test_app_identical_with_the_55_legs_disabled():
    """Release (APP bit-identity, run 1 of 2): with CAPEX_INTANGIBLE_TAGS emptied and reconcile_sbc disabled
    (run_engine's patch hook) APP reproduces its recorded run — this proves the decision 1/2/3/4/7 paths are
    inert for it (roll-up every year until the FY2025 override, no ratio, no split, no dei defect)."""
    rec = recorded_matching_fixture("APP")
    out = run("APP", H.recorded_args(rec), judgment=APP_J, ttm={"ttm_oe_per_share": rec["base_oe_per_share"]},
              patch=_patch_55_off)
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert_same_math(out["numbers"], rec, "APP (5.5 legs off)")
    _same_rows(out["rows"], recorded_rows("APP"), "APP (5.5 legs off)")


def test_app_full_55_differs_only_by_the_documented_legs():
    """Decisions 5 + 6 on APP (run 2 of 2): capex FY2023 4,246,000 + 63,899,000 = 68,145,000 and FY2024
    4,776,000 + 25,553,000 = 30,329,000 (intangibles); FY2025 stays the $19M OVERRIDE with the 28,318,000
    intangible fact NOT added (override_present, and the OVERRIDE_APPLIED:capex text says so); SBC FY2024
    369,367,000 -> 376,455,000 and FY2025 210,421,000 -> 211,621,000. Every other row is unchanged and the
    valuation is identical (TTM-pinned base; g_base capped at 35% both ways)."""
    rec = recorded_matching_fixture("APP")
    out = run("APP", H.recorded_args(rec), judgment=APP_J, ttm={"ttm_oe_per_share": rec["base_oe_per_share"]})
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert_same_math(n, rec, "APP (full 5.5)")
    changed = {"2023-12-31", "2024-12-31", "2025-12-31"}
    _same_rows(rows, recorded_rows("APP"), "APP (full 5.5)", skip=changed)
    assert f(row(rows, "2023-12-31")["capex"]) == 68145000 and f(row(rows, "2024-12-31")["capex"]) == 30329000
    assert row(rows, "2023-12-31")["capex_tag"] == f"{PRIMARY}+{INTANG}"
    r25 = row(rows, "2025-12-31")
    assert f(r25["capex"]) == 19000000 and r25["capex_tag"] == "OVERRIDE" and f(r25["capex_ppe"]) == 19000000, (r25["capex"], r25["capex_tag"])
    assert n["capex_provenance"]["2025-12-31"].get("intangibles_not_added") == "override_present", n["capex_provenance"]["2025-12-31"]
    ov = flags(n, "OVERRIDE_APPLIED:capex")
    assert len(ov) == 1 and "were not added on top of the override" in ov[0], ov
    assert f(row(rows, "2023-12-31")["sbc"]) == 363107000
    assert f(row(rows, "2024-12-31")["sbc"]) == 376455000 and f(r25["sbc"]) == 211621000
    fl = flags(n, "SBC_TAG_RECONCILED")
    assert len(fl) == 1 and "2024" in fl[0] and "2025" in fl[0], fl


def test_stz_identical_with_the_55_legs_disabled():
    """Release (STZ bit-identity, run 1 of 2): reconciliation disabled and intangibles emptied -> STZ
    reproduces its recorded run exactly."""
    rec = recorded_matching_fixture("STZ")
    out = run("STZ", H.recorded_args(rec), judgment=STZ_J, patch=_patch_55_off)
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert_same_math(out["numbers"], rec, "STZ (5.5 legs off)")
    _same_rows(out["rows"], recorded_rows("STZ"), "STZ (5.5 legs off)")


def test_stz_full_55_differs_only_by_fy2026_sbc():
    """Decision 6 on STZ (run 2 of 2): only FY2026 SBC moves (67.7M -> 69.2M Allocated), so the median base —
    the FY2026 OE/share — falls from 9.8327 to 9.8241; tier D; the weighted IRR edges down."""
    rec = recorded_matching_fixture("STZ")
    out = run("STZ", H.recorded_args(rec), judgment=STZ_J)
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    _same_rows(rows, recorded_rows("STZ"), "STZ (full 5.5)", cols=("capex", "sbc", "ocf", "shares_diluted"), skip={"2026-02-28"})
    r = row(rows, "2026-02-28")
    assert f(r["sbc"]) == 69200000 and r["sbc_tag"] == SBC_ALLOC and f(r["capex"]) == 875000000, (r["sbc"], r["sbc_tag"], r["capex"])
    assert close(n["base_oe_per_share"], 9.824113733710016, rel=1e-9), n["base_oe_per_share"]
    assert n["tier_by_numbers"] == "D" and n["implied_irr_weighted"] < rec["implied_irr_weighted"]


# ===========================================================================
# 8. ttm.py end to end
# ===========================================================================
def test_ttm_ar_sums_the_capex_components():
    """Decisions 4 (ttm.py identical): AR's TTM capex legs are the summed components per exact period — FY2025
    944,003,000, H1-2025 414,554,000, H1-2026 508,897,000 -> TTM 1,038,346,000 (5.4: 12,721,000 from OtherPPE
    alone); the leg *_tag fields carry the '+'-joined provenance; ttm.json gains capex_components per leg."""
    out = run_ttm("AR")
    assert out["exit"] == 0, out["stderr"]
    t = out["ttm"]
    cap = t["inputs"]["capex"]
    assert (cap["fy"], cap["ytd_prior"], cap["ytd_current"]) == (944003000, 414554000, 508897000), cap
    for leg in ("fy_tag", "ytd_prior_tag", "ytd_current_tag"):
        assert cap[leg] == AR_COMPONENTS, (leg, cap[leg])
    assert t["ttm_capex"] == 1038346000
    comps = t["capex_components"]
    for leg, v in (("fy", 944003000), ("ytd_prior", 414554000), ("ytd_current", 508897000)):
        assert comps[leg]["ppe"] == v, (leg, comps[leg])
    assert t["ttm_sbc"] == 54811000
    assert close(t["ttm_oe_per_share"], (1978740000 - 1038346000 - 54811000) / 310931000, rel=1e-12), t["ttm_oe_per_share"]


def test_ttm_els_capital_improvements_legs():
    """Decision 3 (ttm.py identical): ELS's TTM capex comes from PaymentsForCapitalImprovements — FY2025
    237,091,000, Q1-2025 45,202,000, Q1-2026 45,285,000 -> 237,174,000 (5.4 could not compute it); the
    Q1-2025 SBC keeps Share 2.334M over Allocated 1.771M."""
    out = run_ttm("ELS")
    assert out["exit"] == 0, out["stderr"]
    t = out["ttm"]
    cap = t["inputs"]["capex"]
    assert (cap["fy"], cap["ytd_prior"], cap["ytd_current"]) == (237091000, 45202000, 45285000), cap
    assert cap["fy_tag"] == CAP_IMPROVEMENTS, cap
    assert t["ttm_capex"] == 237174000 and t["ttm_sbc"] == 7066000, (t["ttm_capex"], t["ttm_sbc"])
    assert close(t["ttm_oe_per_share"], 1.6373091679322196, rel=1e-12), t["ttm_oe_per_share"]


def test_ttm_jll_reconciles_sbc_per_leg():
    """Decision 6 (ttm.py, same rule per exact leg period): JLL's FY2025 leg uses Allocated 112.0M (Share
    2.7M); the H1 legs have no Allocated fact and keep Share 1.4M / 0.2M -> TTM SBC 110,800,000;
    sbc_reconciled_legs names the FY leg only. The capex legs are still the override fill (215.6M)."""
    out = run_ttm("JLL", judgment=JLL_J)
    assert out["exit"] == 0, out["stderr"]
    t = out["ttm"]
    sbc = t["inputs"]["sbc"]
    assert sbc["fy"] == 112000000 and sbc["fy_tag"] == SBC_ALLOC, sbc
    assert sbc["ytd_prior"] == 1400000 and sbc["ytd_current"] == 200000, sbc
    assert t["ttm_sbc"] == 110800000
    assert "fy" in t["sbc_reconciled_legs"] and "ytd_prior" not in t["sbc_reconciled_legs"], t["sbc_reconciled_legs"]
    assert t["ttm_capex"] == 215600000
    assert close(t["ttm_oe_per_share"], (1362000000 - 215600000 - 110800000) / 47368000, rel=1e-12), t["ttm_oe_per_share"]


def test_ttm_dd_post_split_leg_is_not_adjusted():
    """Decision 2 §2 (ttm.py): DD's H1-2026 diluted count 137.2M is already post-split (137.2M / dei
    135.0M ~ 1, not ~3), so no split adjustment applies and the saved ttm.json stands: TTM OE/share
    4.803206997084548."""
    out = run_ttm("DD")
    assert out["exit"] == 0, out["stderr"]
    t = out["ttm"]
    assert t["ttm_shares_diluted"] == 137200000, t["ttm_shares_diluted"]
    assert t["ttm_oe_per_share"] == 4.803206997084548, t["ttm_oe_per_share"]


def test_ttm_split_adjusts_a_pre_split_ytd_denominator():
    """Decision 2 §2 (ttm.py, synthetic leg): DD's fixture with the H1-2026 diluted count put back on the
    pre-split basis (411.6M — 3.05x the 2026-07-31 dei) -> the confirmed 1-for-3 applies to the TTM
    denominator (411.6M x 1/3 = 137.2M), recorded as split_adjustment; the TTM base is unchanged."""
    fx = copy.deepcopy(H.load_fixture("DD"))
    es = fx["facts"]["facts"]["us-gaap"]["WeightedAverageNumberOfDilutedSharesOutstanding"]["units"]["shares"]
    hit = 0
    for e in es:
        if e.get("start") == "2026-01-01" and e.get("end") == "2026-06-30":
            e["val"] = 411600000
            hit += 1
    assert hit, "fixture lost DD's H1-2026 diluted count"
    out = run_ttm("DD", fixture=fx)
    assert out["exit"] == 0, out["stderr"]
    t = out["ttm"]
    assert close(t["ttm_shares_diluted"], 411600000 / 3, rel=1e-9), t["ttm_shares_diluted"]
    assert t.get("split_adjustment"), t.get("split_adjustment")
    assert close(t["ttm_oe_per_share"], 4.803206997084548, rel=1e-9), t["ttm_oe_per_share"]


# ---------------------------------------------------------------------------
# [ADDITION — ECHO] a cumulative intangible figure on an annual context (engine + ttm.py, e2e)
# ---------------------------------------------------------------------------
# EchoStar's real FY / H1 values (cached companyfacts, copied here) on a synthetic fixture built in the test; the
# FY2023 intangible purchase (12,000,000) is synthetic — the control that an ordinary purchase is still added.
ECHO_FY = {  # year: (revenue, net income, OCF, PP&E capex, SBC, diluted shares, D&A, cash)
    2021: (19818678000, 62700000, 4655373000, 1619312000, 59379000, 313122000, 1213946000, 535894000),
    2022: (18634246000, 166500000, 3621190000, 3050472000, 82994000, 307733000, 1174895000, 2497536000),
    2023: (17015598000, -496100000, 2432647000, 3100921000, 51514000, 270842000, 1597923000, 1821376000),
    2024: (15825516000, -124500000, 1252697000, 1544877000, 36383000, 274079000, 1930193000, 4305393000),
    2025: (15004989000, -51900000, -99374000, 965730000, 36272000, 287589000, 1585549000, 1883074000)}
ECHO_H1 = {2025: (7594717000, 214267000, 551600000, 16123000, 287012000),   # revenue, OCF, PP&E capex, SBC, shares
           2026: (7243653000, 228324000, 225734000, 23363000, 351432000)}


def _echo_fixture():
    us = {}

    def put(tag, unit, e):
        us.setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    for y, (rev, ni, ocf, capex, sbc, sh, da, cash) in ECHO_FY.items():
        for tag, unit, v in (("RevenueFromContractWithCustomerExcludingAssessedTax", "USD", rev), ("NetIncomeLoss", "USD", ni),
                             ("NetCashProvidedByUsedInOperatingActivities", "USD", ocf), (PRIMARY, "USD", capex),
                             (SBC_SHARE, "USD", sbc), ("WeightedAverageNumberOfDilutedSharesOutstanding", "shares", sh),
                             ("DepreciationDepletionAndAmortization", "USD", da)):
            put(tag, unit, _ctx(f"{y}-01-01", f"{y}-12-31", v))
        put("CashAndCashEquivalentsAtCarryingValue", "USD", _ctx(None, f"{y}-12-31", cash))
    for y, (rev, ocf, capex, sbc, sh) in ECHO_H1.items():
        for tag, unit, v in (("RevenueFromContractWithCustomerExcludingAssessedTax", "USD", rev),
                             ("NetCashProvidedByUsedInOperatingActivities", "USD", ocf), (PRIMARY, "USD", capex),
                             (SBC_SHARE, "USD", sbc), ("WeightedAverageNumberOfDilutedSharesOutstanding", "shares", sh)):
            put(tag, unit, _ctx(f"{y}-01-01", f"{y}-06-30", v, form="10-Q", fp="Q2", fy=y, filed=f"{y}-08-03"))
    for e in (_ctx("2023-01-01", "2023-12-31", 12000000),                                   # synthetic control
              _ctx("2024-01-01", "2024-12-31", ECHO_CUM, filed="2025-02-27"),                # the annual duplicate
              _ctx("2008-01-01", "2023-12-31", ECHO_CUM, fy=2023, filed="2024-02-29"),       # cumulative contexts
              _ctx("2018-01-01", "2025-12-31", ECHO_CUM, fy=2025, filed="2026-03-02"),
              _ctx("2025-01-01", "2025-06-30", ECHO_CUM, form="10-Q", fp="Q2", fy=2025, filed="2025-08-01"),
              _ctx("2018-01-01", "2026-06-30", ECHO_CUM, form="10-Q", fp="Q2", fy=2026, filed="2026-08-03")):
        put(INTANG, "USD", e)
    return {"ticker": "ECHO", "cik": 1415404, "entityName": "EchoStar Corporation (synthetic test fixture)", "price": 25.0,
            "filer_annual_form": "10-K", "fx_rates": {},
            "universe_row": {"ticker": "ECHO", "name": "EchoStar", "sector": "", "price": "", "market_cap": "", "cik": "1415404"},
            "facts": {"cik": 1415404, "entityName": "EchoStar Corporation", "facts": {"us-gaap": us}}}


def test_echo_cumulative_intangible_dropped_e2e():
    """[ADDITION — ECHO] dcf_engine.main(): FY2024's 30,000,000,000 intangible fact repeats the value the tag files on
    2008-01-01..2023-12-31 and 2018-01-01..2025-12-31 -> dropped, capex 1,544,877,000 (was 31,544,877,000 — 24x OCF),
    capex_provenance FY2024 dropped [[PaymentsToAcquireIntangibleAssets, 30000000000, 'cumulative_duplicate']]; the
    FY2023 purchase (12,000,000, on no multi-year context) is still added; base = median of the three OE/share."""
    out = run("ECHO", args_for(5), fixture=_echo_fixture())
    n, rows = out["numbers"], out["rows"]
    assert out["exit"] == 0 and n.get("data_gap_uncovered") in (None, []), out["stdout"][-1500:]
    r24 = row(rows, "2024-12-31")
    assert f(r24["capex"]) == 1544877000 and f(r24["capex_intangibles"]) is None and r24["capex_tag"] == PRIMARY, r24
    assert f(r24["oe_conservative"]) == 1252697000 - 1544877000 - 36383000, r24["oe_conservative"]
    r23 = row(rows, "2023-12-31")
    assert f(r23["capex"]) == 3112921000 and f(r23["capex_intangibles"]) == 12000000, r23
    assert r23["capex_tag"] == f"{PRIMARY}+{INTANG}", r23["capex_tag"]
    prov = n["capex_provenance"]["2024-12-31"]
    assert prov["dropped"] == [[INTANG, ECHO_CUM, "cumulative_duplicate"]] and prov["intangibles"] == {}, prov
    assert n["capex_provenance"]["2023-12-31"]["dropped"] == [], n["capex_provenance"]["2023-12-31"]
    oe_ps = [(2432647000 - 3112921000 - 51514000) / 270842000, (1252697000 - 1544877000 - 36383000) / 274079000,
             (-99374000 - 965730000 - 36272000) / 287589000]
    assert close(n["base_oe_per_share"], statistics.median(oe_ps), rel=1e-12), n["base_oe_per_share"]
    assert n["tier_by_numbers"] == "F", n["tier_by_numbers"]


def test_ttm_echo_cumulative_intangible_dropped():
    """[ADDITION — ECHO] ttm.py, the same helper per leg: the H1-2025 intangible fact (30,000,000,000 — the value of the
    2018-01-01..2025-12-31 context) is dropped from the prior-YTD leg -> TTM capex 965,730,000 - 551,600,000 +
    225,734,000 = 639,864,000 and TTM OE/share -2.1873 (was capex -29,360,136,000 and a fake +83.18/share);
    capex_components.ytd_prior.dropped names it."""
    out = run_ttm("ECHO", fixture=_echo_fixture())
    assert out["exit"] == 0, out["stderr"]
    t = out["ttm"]
    cap = t["inputs"]["capex"]
    assert (cap["fy"], cap["ytd_prior"], cap["ytd_current"]) == (965730000, 551600000, 225734000), cap
    assert cap["ytd_prior_tag"] == PRIMARY and t["ttm_capex"] == 639864000, (cap, t["ttm_capex"])
    assert [INTANG, ECHO_CUM, "cumulative_duplicate"] in t["capex_components"]["ytd_prior"]["dropped"], t["capex_components"]
    oe = (-99374000 - 214267000 + 228324000) - 639864000 - (36272000 - 16123000 + 23363000)
    assert close(t["ttm_oe_per_share"], oe / 351432000, rel=1e-12), t["ttm_oe_per_share"]


# ===========================================================================
# 8b. Verifier round 1 — the main agent's rulings E1-E11 (FIX_DECISIONS_R1); each test fails on the pre-fix engine
# ===========================================================================
# Synthetic filer (offline, built here): revenue / NI / OCF grow 5%/yr from 1,000M / 100M / 200M, capex 50M, SBC 10M,
# D&A 60M, diluted shares 100M, cash 100M, long-term debt 200M, PP&E 500M, FY2019-FY2025; a dei cover count of 100M
# on 2026-01-31. Every series is overridable per year (None = not filed that year).
SYN_YEARS = (2019, 2020, 2021, 2022, 2023, 2024, 2025)
SYN_SHARE_TAG = "WeightedAverageNumberOfDilutedSharesOutstanding"


def _syn_put(facts, tag, unit, entry, taxonomy="us-gaap"):
    facts["facts"].setdefault(taxonomy, {}).setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(entry)


def _syn_facts(shares=None, capex=None, intangibles=None, dei=(100e6, "2026-01-31", "2026-02-20")):
    """shares / capex / intangibles: {year: value} overrides of the defaults (value None = not filed that year);
    intangibles default to none filed. dei: (count, date, filed) or None."""
    facts = {"cik": 999001, "entityName": "SYNTH CO (test fixture)", "facts": {"us-gaap": {}}}
    sh = dict.fromkeys(SYN_YEARS, 100e6)
    sh.update(shares or {})
    cx = dict.fromkeys(SYN_YEARS, 50e6)
    cx.update(capex or {})
    for i, y in enumerate(SYN_YEARS):
        g = 1.05 ** i
        for tag, unit, v in (("Revenues", "USD", 1000e6 * g), ("NetIncomeLoss", "USD", 100e6 * g),
                             ("NetCashProvidedByUsedInOperatingActivities", "USD", 200e6 * g),
                             ("DepreciationDepletionAndAmortization", "USD", 60e6), (SBC_SHARE, "USD", 10e6),
                             (PRIMARY, "USD", cx[y]), (SYN_SHARE_TAG, "shares", sh[y]),
                             (INTANG, "USD", (intangibles or {}).get(y))):
            if v is not None:
                _syn_put(facts, tag, unit, _ctx(f"{y}-01-01", f"{y}-12-31", v, filed=f"{y + 1}-02-20"))
        for tag, v in (("CashAndCashEquivalentsAtCarryingValue", 100e6), ("LongTermDebtNoncurrent", 200e6),
                       ("DebtCurrent", 0), ("PropertyPlantAndEquipmentNet", 500e6)):
            _syn_put(facts, tag, "USD", _ctx(None, f"{y}-12-31", v, filed=f"{y + 1}-02-20"))
    if dei:
        _syn_put(facts, "EntityCommonStockSharesOutstanding", "shares",
                 {"end": dei[1], "val": dei[0], "fy": 2025, "fp": "FY", "form": "10-K", "filed": dei[2],
                  "accn": "0000999001-26-000001"}, taxonomy="dei")
    return facts


def _syn_fixture(facts, price=30.0, ticker="SYN"):
    return {"ticker": ticker, "cik": facts["cik"], "entityName": facts["entityName"], "price": price,
            "filer_annual_form": "10-K", "fx_rates": {},
            "universe_row": {"ticker": ticker, "name": "Synth", "sector": "", "price": str(price), "market_cap": "",
                             "cik": str(facts["cik"])},
            "facts": facts}


def _syn_run(facts, extra=(), judgment=None, price=30.0, ticker="SYN"):
    return run(ticker, args_for(5, extra=list(extra)), judgment=judgment if judgment is not None else {},
               fixture=_syn_fixture(facts, price, ticker))


def _split_fact(facts, end, ratio, filed, start=None):
    e = {"end": end, "val": ratio, "fy": int(filed[:4]), "fp": "Q1", "form": "10-Q", "filed": filed,
         "accn": f"0000999001-split-{end}"}
    if start:
        e["start"] = start
    _syn_put(facts, "StockholdersEquityNoteStockSplitConversionRatio1", "pure", e)


# ---- E1: the share-scale rescue needs a declared, non-payable base_override equal to a sane --base-oe-ps pin ----
TEM_TTM_MISSCALED = -2504.7657800272013   # TEM's ttm.json ttm_oe_per_share: thousands-scaled share legs read as units


def test_e1_share_scale_pin_rescue_conditions():
    """Ruling E1 (unit): share_scale_pin_rescue rescues only (1) a --base-oe-ps pin (2) that judgment.json declares as a
    base_override WITHOUT `basis` equal to the pin within 0.1% (3) whose own magnitude is within 20x the price."""
    R = E.share_scale_pin_rescue
    assert R("base_oe_ps_arg", 1.3553, 70.0, _bo(1.3553)) == (True, [])
    assert R("base_oe_ps_arg", 1.3553, 70.0, _bo(1.3553 * 1.0009))[0] is True          # inside 0.1%
    ok, why = R("base_oe_ps_arg", 1.3553, 70.0, _bo(1.3553 * 1.002))                    # outside 0.1%
    assert not ok and "within 0.1%" in why[0], why
    ok, why = R("base_oe_ps_arg", 1.3553, 70.0, None)
    assert not ok and why == ["judgment.json declares no base_override"], why
    ok, why = R("base_oe_ps_arg", 1.3553, 70.0, _bo(1.3553, basis="payable_earnings_5y"))
    assert not ok and "basis" in why[0], why
    ok, why = R("base_oe_ps_arg", TEM_TTM_MISSCALED, 64.72, _bo(TEM_TTM_MISSCALED))      # declared, but itself mis-scaled
    assert not ok and len(why) == 1 and "x the price" in why[0], why
    assert R("ttm_json", 1.3553, 70.0, _bo(1.3553))[0] is False                           # a --ttm pin never rescues
    assert R("judgment_base_override", 1.3553, 70.0, _bo(1.3553))[0] is False
    assert R("base_oe_ps_arg", 1.3553, None, _bo(1.3553))[0] is True                      # no price: test (a) not evaluable
    assert R("base_oe_ps_arg", 1.0, 70.0, {"value": True, "source": "s", "reason": "r"})[0] is False   # a bool is no value


def test_e1_tem_undeclared_ttm_value_pin_does_not_rescue_e2e():
    """Ruling E1 (P1, fidelity): TEM's own mis-scaled ttm.json figure (-2,504.77 on thousands-scaled shares) passed as
    --base-oe-ps with no declared base_override -> exit 4, gap 'share_scale', share_scale.pin_rejected naming both the
    missing declaration and the pin's own 39x-price scale, and the DATA_GAP text says the pin does not carry it (5.5:
    exit 0, rescued_by_pin, a Tier F at -$2,504.77 and a $0.01B cap; positive, a Tier S). The positive twin, the
    declared-but-mis-scaled pin and a declaration 1% off the pin all gap too, and the cap takes no factor from a
    rejected pin; the declared TEM pin (-3.9324) still rescues (test_tem_scale_guard_e2e)."""
    out = run("TEM", TEM_ARGS + ["--base-oe-ps", repr(TEM_TTM_MISSCALED)], judgment={})
    n = out["numbers"]
    assert out["exit"] == 4 and "share_scale" in n["data_gap_uncovered"], (out["exit"], n.get("data_gap"))
    assert n["tier_by_numbers"] is None
    ss = n["share_scale"]
    assert ss["defect"] is True and ss["rescued_by_pin"] is False, ss
    assert ss["pin_rejected"][0] == "judgment.json declares no base_override" and "x the price" in ss["pin_rejected"][1], ss
    assert ss["scale_factor"] is None and ss["factor_basis"] is None, ss                  # a rejected pin sets no factor
    fl = flags(n, SCALE_GAP)
    assert len(fl) == 1 and "does not carry it" in fl[0], fl
    assert not flags(n, "SHARE_SCALE_SUSPECT")
    for pin, j in ((-TEM_TTM_MISSCALED, {}),                                               # the positive twin (fake Tier S)
                   (TEM_TTM_MISSCALED, {"base_override": _bo(TEM_TTM_MISSCALED, kind="estimate")}),  # declared, mis-scaled
                   (TEM_PIN, {"base_override": _bo(TEM_PIN * 1.01, kind="estimate")})):    # declared value 1% off
        o = run("TEM", TEM_ARGS + ["--base-oe-ps", repr(pin)], judgment=j)
        assert o["exit"] == 4 and "share_scale" in o["numbers"]["data_gap"], (pin, j, o["exit"])
        assert o["numbers"]["share_scale"]["rescued_by_pin"] is False


def test_e1_ttm_pin_with_a_declaration_still_does_not_rescue_e2e():
    """Ruling E1 (1): a --ttm pin never rescues, even when judgment.json declares a base_override equal to it (ttm.py
    divides by the same mis-scaled counts); the NTNX declared --base-oe-ps pin rescues (test_ntnx_scale_guard_rescued…)."""
    out = run("NTNX", NTNX_ARGS + ["--ttm"], judgment=NTNX_J, ttm={"ttm_oe_per_share": NTNX_PIN})
    assert out["exit"] == 4 and "share_scale" in out["numbers"]["data_gap"], out["exit"]
    assert out["numbers"]["share_scale"]["pin_rejected"] is None   # no --base-oe-ps pin was offered


# ---- E2: a scale break inside the growth window drops the share-derived growth inputs ----
def test_e2_share_series_scale_breaks_unit():
    """Ruling E2 (unit): adjacent counts more than 100x apart break the series (VIV-shaped); a consistently scaled
    series (NTNX: every count in thousands) and ordinary drift do not."""
    B = E.share_series_scale_breaks
    viv = [("2022-12-31", 1663556731000), ("2023-12-31", 1658604), ("2024-12-31", 1643132), ("2025-12-31", 3195606352)]
    assert B(viv) == [("2022-12-31", 1663556731000, "2023-12-31", 1658604), ("2024-12-31", 1643132, "2025-12-31", 3195606352)]
    ntnx = [("2023-07-31", 245000), ("2024-07-31", 270000), ("2025-07-31", 282000), ("2026-07-31", 292183)]
    assert B(ntnx) == []
    assert B([("2024", 100e6), ("2025", 100e6 / 99)]) == [] and B([("2024", 100e6), ("2025", 100e6 / 101)]) != []
    assert B([("2024", 0), ("2025", 1e9)]) == [] and B([]) == []


def test_e2_rescued_defect_with_a_break_drops_share_growth_e2e():
    """Ruling E2 (P1, adversarial tier crossing): a filer whose FY2023-25 diluted counts are filed in thousands (dei
    100M) with a declared pin 2.6 used to score Tier B on g_base 10% — share_cagr -90%/yr added +5pp to the revenue
    components. Now the share-count CAGR leaves the blend (share adjustment 0) and — verifier round 2 (R2-E2) — the
    OE/share CAGR stays, because the only break (FY2022 -> FY2023) precedes its FY2023 -> FY2025 window: the growth
    is within 0.001pp of the clean filer's and the tier is the clean filer's (Tier C, 13.13%); share_scale records
    the break and the dropped input, and SHARE_SCALE_SUSPECT says so; no DILUTION / BUYBACK flag reads the broken
    series."""
    pin_args = ["--base-oe-ps", "2.6"]
    clean = _syn_run(_syn_facts(), pin_args)["numbers"]
    out = _syn_run(_syn_facts(shares={2023: 100e3, 2024: 100e3, 2025: 100e3}), pin_args,
                   judgment={"base_override": _bo(2.6)})
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    ss = n["share_scale"]
    assert ss["defect"] and ss["tests"]["b"] and ss["rescued_by_pin"], ss
    assert [(b["from_period"], b["to_period"]) for b in ss["scale_breaks"]] == [("2022-12-31", "2023-12-31")], ss
    # [verifier round 2, R2-E2] the only break (FY2022 -> FY2023) precedes the OE/share CAGR's window (FY2023 ->
    # FY2025, both in thousands): that CAGR is valid and stays; only the share-count CAGR leaves the blend
    assert ss["growth_inputs_dropped"] == ["share_cagr"] and ss["growth_inputs_kept"] == ["oe_ps_cagr_2y"], ss
    assert close(ss["growth_inputs_dropped_values"]["share_cagr"], (100e3 / 100e6) ** (1 / ((E.datetime.date(2025, 12, 31) - E.datetime.date(2022, 12, 31)).days / 365.25)) - 1, rel=1e-12)
    assert n["share_cagr"] is None and n["share_count_adj"] == 0.0, (n["share_cagr"], n["share_count_adj"])
    assert n["growth_components_adjusted"]["oe_ps_cagr_2y"] == n["growth_components"]["oe_ps_cagr_2y"] is not None
    gc = n["growth_components"]
    assert n["g_base"] == statistics.median([gc["rev_cagr_5y"], gc["rev_cagr_3y"], gc["rev_yoy_latest"], gc["oe_ps_cagr_2y"]]), n["g_base"]
    assert abs(n["g_base"] - clean["g_base"]) < 1e-5 and n["tier_by_numbers"] == clean["tier_by_numbers"] == "C", \
        (n["g_base"], clean["g_base"], n["tier_by_numbers"], clean["tier_by_numbers"])   # 5.5: g_base 10%, Tier B
    assert abs(n["implied_irr_weighted"] - clean["implied_irr_weighted"]) < 1e-5, (n["implied_irr_weighted"], clean["implied_irr_weighted"])
    fl = flags(n, "SHARE_SCALE_SUSPECT")
    assert len(fl) == 1 and "breaks scale inside the growth window (FY2022 100,000,000 -> FY2023 100,000)" in fl[0], fl
    assert not flags(n, "DILUTION") and not flags(n, "BUYBACK_TAILWIND"), n["fragility_flags"]
    # without the pin the run gaps, and the gap text names the dropped inputs too
    gap = _syn_run(_syn_facts(shares={2023: 100e3, 2024: 100e3, 2025: 100e3}))
    fl = flags(gap["numbers"], SCALE_GAP)
    assert gap["exit"] == 4 and len(fl) == 1 and "dropped from the growth blend" in fl[0], (gap["exit"], fl)


def test_e2_consistently_scaled_ntnx_keeps_its_growth_inputs_e2e():
    """Ruling E2: NTNX's counts are in thousands in every year of the growth window — the share CAGR is valid, so the
    rescued run keeps share_cagr and the OE/share CAGR (no scale_breaks, nothing dropped)."""
    n = run("NTNX", NTNX_ARGS + ["--base-oe-ps", repr(NTNX_PIN)], judgment=NTNX_J)["numbers"]
    ss = n["share_scale"]
    assert ss["rescued_by_pin"] and ss["scale_breaks"] == [] and ss["growth_inputs_dropped"] == [], ss
    assert n["share_cagr"] is not None and n["growth_components_adjusted"]["oe_ps_cagr_2y"] == n["growth_components"]["oe_ps_cagr_2y"]
    assert "breaks scale" not in flags(n, "SHARE_SCALE_SUSPECT")[0]


# ---- E3: a rescued defect with no factor and no dei leaves the leverage diagnostics unverifiable ----
def test_e3_rescued_defect_without_factor_or_dei_suppresses_leverage_e2e():
    """Ruling E3 (P2): every count in thousands (consistent: no break), no dei, a declared pin 2.5 whose ratio to the
    native base (~781x) is no power of ten -> no cap factor; 5.5 printed net debt / normalized OE 400x and
    HIGH_NET_DEBT on the 1,000x-small total. Now net_debt_to_normalized_oe is None, neither leverage flag fires,
    share_scale.leverage_unverifiable is true and SHARE_SCALE_SUSPECT says the leverage diagnostics are unverifiable;
    the growth inputs stay (E2 needs a break)."""
    facts = _syn_facts(shares=dict.fromkeys(SYN_YEARS, 100e3), dei=None)
    out = _syn_run(facts, ["--base-oe-ps", "2.5"], judgment={"base_override": _bo(2.5)})
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    ss = n["share_scale"]
    assert ss["defect"] and ss["tests"]["a"] and not ss["tests"]["b"] and ss["dei_ratio"] is None, ss
    assert ss["rescued_by_pin"] and ss["scale_factor"] is None and ss["leverage_unverifiable"] is True, ss
    assert n["diagnostics"]["net_debt_to_normalized_oe"] is None, n["diagnostics"]
    assert not flags(n, "HIGH_NET_DEBT") and not flags(n, "BIG_NET_CASH"), n["fragility_flags"]
    fl = flags(n, "SHARE_SCALE_SUSPECT")
    assert len(fl) == 1 and "leverage diagnostics are unverifiable" in fl[0], fl
    assert ss["scale_breaks"] == [] and n["share_cagr"] is not None
    # with a dei that agrees with the latest count (test (b) evaluated and passed) the diagnostics stand: VIV
    # (test_viv_scale_guard_e2e asserts its net_debt_to_normalized_oe identity)


# ---- E4: a filed share count <= 0 is not filed ----
def test_e4_zero_diluted_count_in_the_last_3_fy_is_a_shares_gap_e2e():
    """Ruling E4 (P1, TLN shape): WeightedAverageNumberOfDilutedSharesOutstanding 0 for FY2024 (in the last 3 FY, no
    other share tag, no dei within 90 days) -> raw_missing shares -> DATA_GAP:shares, exit 4, the gap text names the
    zero count; share_basis.nonpositive_counts records it. 5.5 dropped the row from the median window (FY2022,
    FY2023, FY2025) and emitted a tier."""
    out = _syn_run(_syn_facts(shares={2024: 0}))
    n = out["numbers"]
    assert out["exit"] == 4 and n["data_gap_uncovered"] == ["shares"], (out["exit"], n.get("data_gap_uncovered"))
    fl = flags(n, "DATA_GAP:shares")
    assert len(fl) == 1 and "2024" in fl[0] and "is not a share count" in fl[0] and SYN_SHARE_TAG in fl[0], fl
    assert n["share_basis"]["nonpositive_counts"] == [{"period": "2024-12-31", "series": "shares_diluted", "tag": SYN_SHARE_TAG,
                                                       "value": 0, "replaced_by": None}], n["share_basis"]
    assert row(out["rows"], "2024-12-31")["shares_diluted"] == "", row(out["rows"], "2024-12-31")


def test_e4_zero_count_takes_the_next_positive_tag_or_the_fallback_e2e():
    """Ruling E4: the zero fact is treated as not filed, so the next candidate tag with a positive count fills the
    period (another diluted tag: no gap, no fallback), and in a history year the fallback chain runs on (a basic /
    CommonStockSharesOutstanding count with SHARES_FALLBACK) — never a 0 that silently drops the row."""
    facts = _syn_facts(shares={2024: 0})
    _syn_put(facts, "WeightedAverageNumberOfSharesOutstandingDiluted", "shares", _ctx("2024-01-01", "2024-12-31", 101e6, filed="2025-02-20"))
    out = _syn_run(facts)
    assert out["exit"] == 0, out["stdout"][-1500:]
    r = row(out["rows"], "2024-12-31")
    assert f(r["shares_diluted"]) == 101e6 and r["shares_tag"] == "WeightedAverageNumberOfSharesOutstandingDiluted", r
    assert out["numbers"]["share_basis"]["nonpositive_counts"][0]["replaced_by"] == "WeightedAverageNumberOfSharesOutstandingDiluted"
    hist = _syn_facts(shares={2020: 0})
    _syn_put(hist, "CommonStockSharesOutstanding", "shares", _ctx(None, "2020-12-31", 99e6, filed="2021-02-20"))
    out = _syn_run(hist)
    assert out["exit"] == 0, out["stdout"][-1500:]
    r = row(out["rows"], "2020-12-31")
    assert f(r["shares_diluted"]) == 99e6 and r["shares_tag"] == "FALLBACK:CommonStockSharesOutstanding", r
    assert f(r["oe_per_share"]) == f(r["oe_conservative"]) / 99e6
    assert flags(out["numbers"], "SHARES_FALLBACK") and "2020" in flags(out["numbers"], "SHARES_FALLBACK")[0]


# ---- E5: a component that is the sum of other components is the total ----
def test_e5_capex_component_equal_to_the_sum_of_others_is_the_total_glpi():
    """Ruling E5 (P2, GLPI FY2024): other PP&E 39,688,000 (2026-02-19) = construction in process 39,542,000
    (2026-02-19) + capital improvements 134,000 (2025-02-20) + an untagged 12,000 (0.03% off) -> the total is kept
    and the parts dropped ('parts_of_total'): 39,688,000, not 79,364,000. Two components with no third (GLPI FY2025
    304,443,000 + 191,289,000) and a single other part (FY2023 47,437,000 + 67,000) stay summed — no other
    near-equal rule."""
    res = E.capex_for_period([], [fact(OTHER_PPE, 39688000, "2026-02-19"), fact(CIP, 39542000, "2026-02-19"),
                                  fact(CAP_IMPROVEMENTS, 134000, "2025-02-20")], [])
    assert res["ppe"] == 39688000 and res["ppe_tags"] == [OTHER_PPE] and res["provenance"] == OTHER_PPE, res
    assert dropped(res) == {(CIP, "parts_of_total"), (CAP_IMPROVEMENTS, "parts_of_total")}, res["dropped"]
    fy25 = E.capex_for_period([], [fact(OTHER_PPE, 304443000, "2026-02-19"), fact(CIP, 191289000, "2026-02-19")], [])
    assert fy25["ppe"] == 495732000 and not fy25["dropped"], fy25
    fy23 = E.capex_for_period([], [fact(OTHER_PPE, 47437000, "2026-02-19"), fact(CIP, 0, "2026-02-19"),
                                   fact(CAP_IMPROVEMENTS, 67000, "2025-02-20")], [])
    assert fy23["ppe"] == 47504000, fy23
    # a sum outside 0.5% is no total; the closest matching subset wins (the exact one over a 0.3% one)
    far = E.capex_for_period([], [fact(OTHER_PPE, 100e6, "2026-02-19"), fact(CIP, 60e6, "2026-02-19"),
                                  fact(CAP_IMPROVEMENTS, 39.4e6, "2026-02-19")], [])
    assert far["ppe"] == 199.4e6 and not far["dropped"], far
    exact = E.capex_for_period([], [fact(OTHER_PPE, 100e6, "2026-02-19"), fact(CIP, 99.7e6, "2026-02-19"),
                                    fact(CAP_IMPROVEMENTS, 0.2e6, "2026-02-19"), fact(PRODUCTIVE, 0.1e6, "2026-02-19")], [])
    assert exact["ppe"] == 100e6 and len(exact["dropped"]) == 3, exact


# ---- E6: negative and $0 intangible facts ----
def test_e6_negative_intangible_dropped_and_zero_joins_nothing():
    """Ruling E6 (P3 x2, unit): a negative intangible fact is dropped (reason 'negative' — FTAI FY2019 -606,000 lowered
    capex); a $0 fact contributes nothing and joins nothing (DECK FY2017 carried '+PaymentsToAcquireIntangibleAssets'
    on a $0 fact). PP&E legs keep their 5.4 semantics."""
    res = E.capex_for_period([fact(PRIMARY, 331777000, "2021-02-26")], [], [fact(INTANG, -606000, "2021-02-26")])
    assert res["ppe"] + res["intangibles"] == 331777000 and res["intangible_tags"] == [], res
    assert (INTANG, "negative") in dropped(res) and res["provenance"] == PRIMARY, res
    z = E.capex_for_period([fact(PRIMARY, 50e6, "2018-05-25")], [], [fact(INTANG, 0, "2018-05-25")])
    assert z["intangible_tags"] == [] and z["provenance"] == PRIMARY and z["intangibles"] == 0.0 and not z["dropped"], z
    mixed = E.capex_for_period([fact(PRIMARY, 50e6, "2026-02-20")], [],
                               [fact(INTANG, 0, "2026-02-20"), fact(OTHER_INTANG, 4e6, "2026-02-20")])
    assert mixed["intangible_tags"] == [OTHER_INTANG] and mixed["intangibles"] == 4e6, mixed


def test_e6_zero_intangible_e2e_and_the_override_note():
    """Ruling E6 (e2e): a $0 intangible fact every year leaves capex_tag = the PP&E tag and capex_intangibles blank; on
    an OVERRIDE-filled year a $0 intangible fact is not listed in the OVERRIDE_APPLIED 'not added' note (TPL listed
    'FY2024 (0), FY2025 (0)')."""
    out = _syn_run(_syn_facts(intangibles=dict.fromkeys(SYN_YEARS, 0)))
    assert out["exit"] == 0, out["stdout"][-1500:]
    for r in out["rows"]:
        assert r["capex_tag"] == PRIMARY and r["capex_intangibles"] == "", r
    facts = _syn_facts(capex={2025: None}, intangibles={2024: 3e6, 2025: 0})
    out = _syn_run(facts, judgment={"capex_override": _o(50e6)})
    fl = flags(out["numbers"], "OVERRIDE_APPLIED:capex")
    assert out["exit"] == 0 and len(fl) == 1 and "intangible purchases" not in fl[0], (out["exit"], fl)
    assert row(out["rows"], "2025-12-31")["capex_tag"] == "OVERRIDE"


# ---- E7: an assumed-zero row does not add the intangible leg ----
def test_e7_assumed_zero_row_does_not_add_intangibles_e2e():
    """Ruling E7 (P3): FY2021 files no PP&E capex line (history year: assumed zero) but files 5,000,000 of intangible
    purchases -> capex stays 0, capex_tag blank, capex_assumed_zero true, capex_source assumed_zero,
    capex_intangibles records 5,000,000 and capex_provenance notes intangibles_not_added 'no_ppe_leg' (5.5 wrote capex
    5,000,000 under the intangible tag on an assumed-zero row). Other years add the leg as before."""
    out = _syn_run(_syn_facts(capex={2021: None}, intangibles=dict.fromkeys(SYN_YEARS, 5e6)))
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    r = row(out["rows"], "2021-12-31")
    assert f(r["capex"]) == 0 and r["capex_tag"] == "" and r["capex_assumed_zero"] == "True", r
    assert r["capex_source"] == "assumed_zero" and f(r["capex_intangibles"]) == 5e6 and f(r["capex_ppe"]) == 0, r
    prov = n["capex_provenance"]["2021-12-31"]
    assert prov["intangibles_not_added"] == "no_ppe_leg" and prov["intangibles_filed"] == {INTANG: 5e6} and prov["intangibles"] == {}, prov
    r22 = row(out["rows"], "2022-12-31")
    assert f(r22["capex"]) == 55e6 and r22["capex_tag"] == f"{PRIMARY}+{INTANG}", r22


# ---- E8: used_tags.sbc follows the reconciliation ----
def test_e8_used_tags_sbc_names_the_reconciled_tag_jll_e2e():
    """Ruling E8 (P3): JLL uses AllocatedShareBasedCompensationExpense in every CSV year after the reconciliation, so
    used_tags.sbc names it (5.5 kept ShareBasedCompensation, period_series' first-used tag)."""
    out = run("JLL", JLL_ARGS, judgment=JLL_J)
    n = out["numbers"]
    assert out["exit"] == 0 and out["rows"][-1]["sbc_tag"] == SBC_ALLOC
    assert n["used_tags"]["sbc"] == SBC_ALLOC, n["used_tags"]


# ---- E9: SHARE_BASIS_ADJUSTED names the split and the years ----
def test_e9_split_label():
    """Ruling E9 (unit): the split named from its multiplier — 1-for-20 / 1-for-15 (limit_denominator(10) printed
    1-for-10 for both), 1-for-3, 2-for-1, 3-for-2, 2-for-3, 15-for-1."""
    L = E.split_label
    assert (L(0.05), L(1 / 15), L(1 / 3), L(0.333), L(2.0), L(1.5), L(2 / 3), L(15), L(0.1)) == \
        ("1-for-20", "1-for-15", "1-for-3", "1-for-3", "2-for-1", "3-for-2", "2-for-3", "15-for-1", "1-for-10")


def test_e9_share_basis_adjusted_text_reverse_split_and_override_year_e2e():
    """Ruling E9 (P3 x2, e2e): a confirmed 1-for-20 (ratio 0.05 at 2026-03-15, dei 5,000,000 on 2026-04-30) prints
    '1-for-20', lists the adjusted years one by one and adds 'except FY2021 (OVERRIDE count, not rescaled)' for the
    year a shares_override filled (recorded in share_basis.split.periods_override_not_rescaled)."""
    facts = _syn_facts(shares={2021: None}, dei=(5e6, "2026-04-30", "2026-05-05"))
    _split_fact(facts, "2026-03-15", 0.05, "2026-05-05")
    j = {"shares_override": _o(5e6, ack_reason="test: post-split basis")}
    out = _syn_run(facts, judgment=j, price=600.0)
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    fl = flags(n, "SHARE_BASIS_ADJUSTED")
    assert len(fl) == 1 and fl[0].startswith("SHARE_BASIS_ADJUSTED: 1-for-20 split"), fl
    assert "FY2019, FY2020, FY2022, FY2023, FY2024, FY2025 except FY2021 (OVERRIDE count, not rescaled)" in fl[0], fl
    sp = n["share_basis"]["split"]
    assert sp["periods_override_not_rescaled"] == ["2021-12-31"] and "2021-12-31" not in sp["periods_adjusted"], sp
    assert f(row(out["rows"], "2021-12-31")["shares_diluted"]) == 5e6 and f(row(out["rows"], "2025-12-31")["shares_diluted"]) == 5e6


# ---- E10: ttm.py warns when a 5.5-new filed tag displaces a capex override leg ----
def _ttm_fixture(capex_tag, fy_capex, h1_prior, h1_cur):
    us = {}

    def put(tag, unit, e):
        us.setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    for tag, unit, fy, h1p, h1c in (("NetCashProvidedByUsedInOperatingActivities", "USD", 1000e6, 450e6, 500e6),
                                    (SBC_SHARE, "USD", 40e6, 20e6, 22e6), (SYN_SHARE_TAG, "shares", 700e6, 700e6, 705e6),
                                    (capex_tag, "USD", fy_capex, h1_prior, h1_cur)):
        put(tag, unit, _ctx("2025-01-01", "2025-12-31", fy, filed="2026-02-20"))
        put(tag, unit, _ctx("2025-01-01", "2025-06-30", h1p, form="10-Q", fp="Q2", fy=2025, filed="2025-08-01"))
        put(tag, unit, _ctx("2026-01-01", "2026-06-30", h1c, form="10-Q", fp="Q2", fy=2026, filed="2026-08-03"))
    return {"ticker": "SYNT", "cik": 999002, "entityName": "SYNTH TTM (test fixture)", "price": 30.0,
            "filer_annual_form": "10-K", "fx_rates": {},
            "universe_row": {"ticker": "SYNT", "name": "Synth", "sector": "", "price": "", "market_cap": "", "cik": "999002"},
            "facts": {"cik": 999002, "entityName": "SYNTH TTM", "facts": {"us-gaap": us}}}


def test_e10_ttm_warns_when_a_new_tag_displaces_the_capex_override():
    """Ruling E10 (P3, WY shape): a 447,000,000 capex_override whose legs are now filled by PaymentsForCapitalImprovements
    (52M FY / 25M / 27M, a tag 5.4 did not read) -> each leg is filed (the override fills nothing), one warning per
    leg and ttm.json capex_override_superseded_legs {leg: period, override, override_prorated, filed_ppe, filed_tags}.
    Within 0.5x-2x of the prorated override, or filled by a 5.4 tag, nothing is recorded."""
    t = run_ttm("SYNT", judgment={"capex_override": _o(447e6)}, fixture=_ttm_fixture(CAP_IMPROVEMENTS, 52e6, 25e6, 27e6))
    assert t["exit"] == 0, t["stderr"]
    out = t["ttm"]
    assert out["ttm_capex"] == 52e6 - 25e6 + 27e6 and out["overrides_used"] == [], (out["ttm_capex"], out["overrides_used"])
    sup = out["capex_override_superseded_legs"]
    assert set(sup) == {"fy", "ytd_prior", "ytd_current"}, sup
    assert sup["fy"]["filed_ppe"] == 52e6 and sup["fy"]["filed_tags"] == CAP_IMPROVEMENTS and close(sup["fy"]["override_prorated"], 447e6), sup
    assert close(sup["ytd_prior"]["override_prorated"], 447e6 * 181 / 365.0, rel=1e-12), sup["ytd_prior"]
    warn = [w for w in out["warnings"] if "now FILED" in w]
    assert len(warn) == 3 and all(CAP_IMPROVEMENTS in w for w in warn), out["warnings"]
    inband = run_ttm("SYNT", judgment={"capex_override": _o(60e6)}, fixture=_ttm_fixture(CAP_IMPROVEMENTS, 52e6, 25e6, 27e6))["ttm"]
    assert inband["capex_override_superseded_legs"] == {} and not [w for w in inband["warnings"] if "now FILED" in w]
    old_tag = run_ttm("SYNT", judgment={"capex_override": _o(447e6)}, fixture=_ttm_fixture(PRIMARY, 52e6, 25e6, 27e6))["ttm"]
    assert old_tag["capex_override_superseded_legs"] == {}, old_tag["capex_override_superseded_legs"]


def test_e6_ttm_zero_intangible_on_an_override_leg_warns_nothing():
    """Ruling E6 (ttm.py's equivalent): a $0 intangible fact on an OVERRIDE-filled leg is not reported as 'not added'
    (only a non-zero purchase is)."""
    fx = _ttm_fixture(CAP_IMPROVEMENTS, 52e6, 25e6, 27e6)
    us = fx["facts"]["facts"]["us-gaap"]
    us.pop(CAP_IMPROVEMENTS)   # no PP&E leg filed: the override fills every leg
    us[INTANG] = {"units": {"USD": [_ctx("2025-01-01", "2025-12-31", 0, filed="2026-02-20"),
                                    _ctx("2026-01-01", "2026-06-30", 3e6, form="10-Q", fp="Q2", fy=2026, filed="2026-08-03")]}}
    t = run_ttm("SYNT", judgment={"capex_override": _o(447e6)}, fixture=fx)
    assert t["exit"] == 0, t["stderr"]
    notes = [w for w in t["ttm"]["warnings"] if "intangible purchases" in w]
    assert len(notes) == 1 and "capex ytd_current" in notes[0], t["ttm"]["warnings"]


# ---- E11: in-history split facts are recorded ----
def test_e11_split_facts_in_history_unit():
    """Ruling E11 (unit): the split facts split_events_post_fy ignores — dated on or before the latest FY end — with the
    same filters and 180-day collapse: MLI's 2023 2-for-1 re-disclosures collapse to 2023-09-26 and the two later FY
    contexts stay; the post-FY 2026 split is not in-history."""
    assert E.split_facts_in_history(MLI_SPLITS, "2025-12-27") == [("2023-09-26", 2.0), ("2024-12-28", 2.0), ("2025-12-27", 2.0)]
    assert E.split_facts_in_history([_split("2024-06-15", 1, "2024-07-30"), _split("2024-06-15", 500, "2024-07-30")], "2025-12-31") == []


def test_e11_in_history_split_facts_recorded_e2e():
    """Ruling E11 (P2, TPL shape; informational): a 3-for-1 fact dated 2024-03-26 (before the FY2025 end) is listed in
    share_basis.in_history_split_facts; nothing is rescaled and nothing else changes (no split, no unconfirmed fact)."""
    facts = _syn_facts()
    _split_fact(facts, "2024-03-26", 3.0, "2024-05-08")
    out = _syn_run(facts)
    sb = out["numbers"]["share_basis"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    assert sb["in_history_split_facts"] == [{"date": "2024-03-26", "ratio_filed": 3.0}], sb
    assert sb["split"] is None and sb["unconfirmed_split_facts"] == [], sb
    assert all(r["shares_split_factor"] == "" for r in out["rows"])
    assert out["numbers"]["base_oe_per_share"] == _syn_run(_syn_facts())["numbers"]["base_oe_per_share"]


# ===========================================================================
# 8c. Verifier round 2 — each test fails on the round-1 engine / ttm.py
# ===========================================================================
def _syn_set(facts, tag, values, unit="USD"):
    """Replace the FY values of a synthetic series: {year: value} on the {year}-01-01..{year}-12-31 contexts."""
    for e in facts["facts"]["us-gaap"][tag]["units"][unit]:
        y = int(e["end"][:4])
        if e.get("start") == f"{y}-01-01" and y in values:
            e["val"] = values[y]


def _syn_dei(facts, end, val, filed):
    _syn_put(facts, "EntityCommonStockSharesOutstanding", "shares",
             {"end": end, "val": val, "fy": int(filed[:4]), "fp": "FY", "form": "10-K", "filed": filed,
              "accn": f"0000999001-dei-{end}"}, taxonomy="dei")


# ---- R2-E3: a dei that the latest count FAILS (test (b)) with no factor leaves the leverage unverifiable too ----
def test_r2_e3_dei_failing_test_b_without_a_factor_suppresses_leverage_e2e():
    """Verifier round 2 (P2 x2, fidelity + adversarial): every count in thousands (100,000) against a dei of 250M —
    test (b) fails (ratio 0.0004) and 100,000 x 10^k never lands within 25% of 250M; the declared pin 2.5 is no power
    of ten off the native base either, so no cap factor. The round-1 engine kept the leverage diagnostics here
    (leverage_unverifiable False: the dei EXISTED) and printed net debt / normalized OE 400x and HIGH_NET_DEBT on the
    1,000x-small total — the very number E3 suppresses when there is no dei at all. Now leverage_unverifiable is
    true, the ratio is None, neither leverage flag fires and SHARE_SCALE_SUSPECT names the failing cover-page count.
    The 50M-dei twin (e3b: FY2023-25 in thousands, pin 1.5; 666.7x) behaves the same."""
    for shares, dei, pin in ((dict.fromkeys(SYN_YEARS, 100e3), 250e6, 2.5),
                             ({2023: 100e3, 2024: 100e3, 2025: 100e3}, 50e6, 1.5)):
        facts = _syn_facts(shares=shares, dei=(dei, "2026-01-31", "2026-02-20"))
        out = _syn_run(facts, ["--base-oe-ps", repr(pin)], judgment={"base_override": _bo(pin)})
        n = out["numbers"]
        assert out["exit"] == 0, out["stdout"][-1500:]
        ss = n["share_scale"]
        assert ss["defect"] and ss["tests"]["b"] and ss["dei_ratio"] is not None, ss
        assert ss["rescued_by_pin"] and ss["scale_factor"] is None, ss
        assert ss["leverage_unverifiable"] is True, ss            # round 1: False
        assert n["diagnostics"]["net_debt_to_normalized_oe"] is None, n["diagnostics"]   # round 1: 400.0 / 666.7
        assert not flags(n, "HIGH_NET_DEBT") and not flags(n, "BIG_NET_CASH"), n["fragility_flags"]
        fl = flags(n, "SHARE_SCALE_SUSPECT")
        assert len(fl) == 1 and "test (b) failed" in fl[0] and f"{dei:,.0f}" in fl[0], fl
        assert "leverage diagnostics are unverifiable" in fl[0], fl


# ---- R2-CAP (round 2), replaced by R3-CAP (round 3): the pin factor needs the median year and the latest count on
# one scale; a dei that agrees with the latest count no longer decides it ----
BREAK_WINDOW = [("2023-12-31", 100e3), ("2024-12-31", 100e3), ("2025-12-31", 100e6)]   # median year FY2023, latest right
THOUSANDS_WINDOW = [("2024-12-31", 100e3), ("2025-12-31", 100e3)]                       # one scale throughout


def test_r2_cap_dei_confirming_the_latest_count_takes_no_pin_factor():
    """Verifier round 2 (P1, adversarial; VIV fixture reproduction): FY2023-24 counts in thousands, FY2025 and the dei
    both 100M, declared pin = the FY2023 OE/share on the right scale, so native median / pin is exactly 1,000. The
    round-1 scale_factor_for_cap fell through to the pin path and multiplied the CONFIRMED latest count by 1,000 —
    a $3.0T cap (VIV: $19.76T), in_scope_under_40b flipped and net debt / OE 1,000x too small. Round 3 (R3-CAP)
    keeps the result — (None, None), cap price x 100M, leverage on the same count — for the reason that applies
    whether or not a dei exists: the FY2023 median year (100,000) and the latest count (100,000,000) are on
    different scales, so the pin's power of ten says nothing about the latest count (share_scale.pin_factor_withheld).
    Unit cases: a break in the window withholds the factor at any dei — the round-2 0.71 case had taken (1000, 'pin')."""
    F = E.scale_factor_for_cap
    assert F(100e6, 100e6, 1830.1, 1.8301, window_counts=BREAK_WINDOW) == (None, None)   # round 1: (1000, 'pin')
    assert F(100e6, 130e6, 1830.1, 1.8301, window_counts=BREAK_WINDOW) == (None, None)
    assert F(100e6, 140e6, 1830.1, 1.8301, window_counts=BREAK_WINDOW) == (None, None)   # round 2: (1000, 'pin')
    assert F(100e6, None, 1830.1, 1.8301, window_counts=BREAK_WINDOW) == (None, None)    # round 2: (1000, 'pin')
    oe23 = (200e6 * 1.05 ** 4 - 60e6) / 100e6
    facts = _syn_facts(shares={2023: 100e3, 2024: 100e3})
    out = _syn_run(facts, ["--base-oe-ps", repr(oe23)], judgment={"base_override": _bo(oe23)})
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    ss = n["share_scale"]
    assert ss["defect"] and ss["tests"]["a"] and not ss["tests"]["b"] and ss["rescued_by_pin"], ss
    assert close(ss["dei_ratio"], 1.0) and ss["scale_factor"] is None and ss["factor_basis"] is None, ss
    assert ss["leverage_unverifiable"] is False, ss
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest", n["market_cap_basis"]
    assert n["market_cap_est"] == 30.0 * 100e6, n["market_cap_est"]  # round 1: 3.0e12
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n), rel=1e-12)
    wh = ss["pin_factor_withheld"]
    assert wh["factor"] == 1000 and wh["window"][0]["period"] == "2023-12-31", wh
    fl = flags(n, "SHARE_SCALE_SUSPECT")[0]
    assert ("the latest diluted count as filed (the cover-page count agrees with it within 25%; the pin's x1000 ratio "
            "to the native base measures the count behind the FY2023 median") in fl, fl
    # [verifier round 4, R4-CAP] the endpoint pair the rule tests (median year FY2023 vs latest FY2025), not the
    # adjacent FY2024 -> FY2025 pair round 3 printed
    assert "(FY2023 100,000 -> FY2025 100,000,000), so it does not apply)" in fl, fl


# ---- R3-CAP: the pin factor is withheld when the median year and the latest count are on different scales, and
# applied when every count — the dei included — shares one scale ----
def test_r3_cap_median_window_counts():
    """Verifier round 3 (R3-CAP, unit): the window runs from the earliest year whose OE/share defines the native median
    to the latest year — the middle value's year of three (every tied year), both years of two, the one year of one."""
    W = E.median_window_counts
    sh = [("2021", 1), ("2022", 2), ("2023", 3), ("2024", 4), ("2025", 5)]
    assert W([("2023", 1831.0), ("2024", 1952.6), ("2025", 2.08)], sh, "2025") == [("2023", 3), ("2024", 4), ("2025", 5)]
    assert W([("2023", 2.0), ("2024", 1.0), ("2025", 3.0)], sh, "2025") == [("2023", 3), ("2024", 4), ("2025", 5)]
    assert W([("2023", 1.0), ("2024", 2.0), ("2025", 3.0)], sh, "2025") == [("2024", 4), ("2025", 5)]
    assert W([("2023", 1.0), ("2024", 3.0), ("2025", 2.0)], sh, "2025") == [("2025", 5)]
    assert W([("2023", 2.0), ("2024", 2.0), ("2025", 5.0)], sh, "2025") == [("2023", 3), ("2024", 4), ("2025", 5)]
    assert W([("2024", 1.0), ("2025", 3.0)], sh, "2025") == [("2024", 4), ("2025", 5)]
    assert W([("2025", 1.0)], sh, "2025") == [("2025", 5)]
    assert W([], sh, "2025") == [] and W([("2025", 1.0)], sh, None) == []
    assert E.pin_power_of_ten(1830.1, 1.8301) == 1000 and E.pin_power_of_ten(1.8301, 1830.1) == 0.001
    assert E.pin_power_of_ten(2068.56, VIV_PIN) is None and E.pin_power_of_ten(None, 1.0) is None


def test_r3_cap_unit_thousands_dei_takes_the_pin_factor():
    """Verifier round 3 (P1, adversarial case (c), unit): every count AND the dei in thousands (100,000) — the dei
    agrees with the latest count, the window has one scale, and native / pin is 1,000 -> (1000, 'pin'). Round 2's
    early return had answered (None, None) because the dei 'confirmed' the mis-scaled latest count."""
    F = E.scale_factor_for_cap
    assert F(100e3, 100e3, 1952.6, 1.9526, window_counts=THOUSANDS_WINDOW) == (1000, "pin")   # round 2: (None, None)
    assert F(100e3, None, 1952.6, 1.9526, window_counts=THOUSANDS_WINDOW) == (1000, "pin")


R3_OE23 = (200e6 * 1.05 ** 4 - 60e6) / 100e6   # the FY2023 OE/share on the right scale = native median / 1,000


def _r3_cap_run(dei, form="10-K", judgment_extra=None, shares=None, pin=R3_OE23):
    facts = _syn_facts(shares=shares if shares is not None else {2023: 100e3, 2024: 100e3}, dei=dei)
    j = {"base_override": _bo(pin)}
    j.update(judgment_extra or {})
    fx = _syn_fixture(facts, 30.0, "SYN")
    fx["filer_annual_form"] = form
    out = run("SYN", args_for(5, extra=["--base-oe-ps", repr(pin)]), judgment=j, fixture=fx)
    assert out["exit"] == 0, out["stdout"][-1500:]
    return out["numbers"]


def test_r3_cap_correct_latest_count_beside_thousands_median_years_takes_no_pin_factor_e2e():
    """Verifier round 3 (P1 x2, fidelity + adversarial): FY2023-24 diluted counts filed in thousands (100,000), the
    FY2025 count right (100,000,000), price $30, the declared pin = the FY2023 OE/share (native median / 1,000). With
    (a) no dei, (b) a dei of 150M (latest / dei 0.667: test (b) passes, outside 25%) or (d) a 20-F filer (ads_ratio 1)
    whose 300M cover count is in other units, the round-2 engine took the pin's x1,000 on the CORRECT latest count:
    market_cap_est 3.0e12 (true 3.0e9), net debt / normalized OE 0.000546 (true 0.546). Now no factor: the cap is
    price x 100M; with no dei E3 makes the leverage diagnostics unverifiable, with a dei that passed test (b) they
    stand on the right count; share_scale.pin_factor_withheld records the x1,000 and the FY2024 -> FY2025 break."""
    for label, dei, form, extra in (
            ("a: no dei", None, "10-K", None),
            ("b: dei 150M", (150e6, "2026-01-31", "2026-02-20"), "10-K", None),
            ("d: 20-F, dei 300M", (300e6, "2026-01-31", "2026-02-20"), "20-F", {"ads_ratio": _ads(1.0)})):
        n = _r3_cap_run(dei, form, extra)
        ss = n["share_scale"]
        assert ss["defect"] and ss["tests"]["a"] and not ss["tests"]["b"] and ss["rescued_by_pin"], (label, ss)
        assert ss["scale_factor"] is None and ss["factor_basis"] is None, (label, ss)          # round 2: 1000 / 'pin'
        assert n["market_cap_basis"]["shares_used"] == 100e6, (label, n["market_cap_basis"])   # round 2: 1.0e11
        assert n["market_cap_est"] == 30.0 * 100e6, (label, n["market_cap_est"])               # round 2: 3.0e12
        wh = ss["pin_factor_withheld"]   # [verifier round 4, R4-CAP] breaks = the median-year / latest endpoint pair
        assert wh and wh["factor"] == 1000 and wh["breaks"] == [{"from_period": "2023-12-31", "from_count": 100e3,
                                                                  "to_period": "2025-12-31", "to_count": 100e6}], (label, wh)
        fl = flags(n, "SHARE_SCALE_SUSPECT")
        assert len(fl) == 1 and "so it does not apply" in fl[0] and "x 1000" not in fl[0], (label, fl)
        if dei is None:
            assert ss["leverage_unverifiable"] is True, (label, ss)
            assert n["diagnostics"]["net_debt_to_normalized_oe"] is None, (label, n["diagnostics"])
        else:
            assert ss["leverage_unverifiable"] is False, (label, ss)
            assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n), rel=1e-12), (label, n["diagnostics"])
            assert close(n["diagnostics"]["net_debt_to_normalized_oe"], 100e6 / (R3_OE23 * 100e6), rel=1e-9), label
        assert not flags(n, "HIGH_NET_DEBT") and not flags(n, "BIG_NET_CASH"), (label, n["fragility_flags"])


def test_r3_cap_every_count_and_the_dei_in_thousands_take_the_pin_factor_e2e():
    """Verifier round 3 (P1, adversarial case (c)): every diluted count AND the cover-page count filed in thousands
    (100,000), the declared pin 1.95. Round 2's early return let the dei 'confirm' the mis-scaled latest count: no
    factor, market_cap_est 3,000,000 and a false HIGH_NET_DEBT 512.8x (the pre-round-2 engine had it right). Now the
    window has one scale, so the pin's x1,000 applies: cap 3.0e9, net debt / OE 0.51 on 100M shares, no leverage
    flag, nothing withheld."""
    n = _r3_cap_run((100e3, "2026-01-31", "2026-02-20"), shares=dict.fromkeys(SYN_YEARS, 100e3), pin=1.95)
    ss = n["share_scale"]
    assert ss["defect"] and ss["tests"]["a"] and not ss["tests"]["b"] and close(ss["dei_ratio"], 1.0), ss
    assert ss["scale_factor"] == 1000 and ss["factor_basis"] == "pin", ss                      # round 2: None
    assert ss["pin_factor_withheld"] is None and ss["leverage_unverifiable"] is False, ss
    assert n["market_cap_basis"]["shares_used"] == 100e6, n["market_cap_basis"]
    assert n["market_cap_est"] == 30.0 * 100e6, n["market_cap_est"]                             # round 2: 3.0e6
    assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n), rel=1e-12), n["diagnostics"]
    assert not flags(n, "HIGH_NET_DEBT"), n["fragility_flags"]                                 # round 2: 512.8x
    assert "x 1000 (pin basis: 100,000,000 shares)" in flags(n, "SHARE_SCALE_SUSPECT")[0]


# ---- R3-SPLIT: the split is confirmed against the latest FILED count, not a latest-FY override ----
def _r3_split_run(override_value):
    facts = _syn_facts(shares={**dict.fromkeys(SYN_YEARS, 300e6), 2025: None}, dei=(100e6, "2026-07-31", "2026-08-05"))
    _split_fact(facts, "2026-06-30", 0.333, "2026-08-05", start="2026-06-30")
    j = {"shares_override": _o(override_value, source="10-K FY2025 EPS note, diluted weighted average shares (test)",
                               ack_reason="test: diluted count not tagged for FY2025")}
    out = _syn_run(facts, judgment=j)
    assert out["exit"] == 0, out["stdout"][-1500:]
    return out


def test_r3_split_latest_fy_post_split_override_confirms_the_split_e2e():
    """Verifier round 3 (P1, fidelity): a 1-for-3 split (ratio 0.333 at 2026-06-30, 10-Q) after the FY2025 10-K, a
    post-split dei of 100,000,000 (2026-07-31), FY2019-24 diluted counts 300,000,000, FY2025 diluted count not
    filed, so judgment.json fills it with a shares_override on the POST-split basis (100,000,000 — what WORKER_SPEC
    step 8 and ruling D7 require). The round-2 engine confirmed the split against hist[-1] — the override itself,
    equal to the dei — so nothing was confirmed: FY2023/24 stayed at 300,000,000, base 0.6509, Tier D 6.03%, no
    flag. Now the split is confirmed against the latest FILED count (FY2024): FY2019-24 are rescaled to 100,000,000,
    the override is untouched, and base, IRR, tier and cap equal the all-post-split reference (base 1.9526, Tier C,
    cap $3.0B). A pre-split override (300,000,000) confirms the split too and stays unrescaled; the flag names it."""
    ref = _syn_run(_syn_facts())["numbers"]                     # every count on the post-split basis, no split
    out = _r3_split_run(100e6)
    n, rows = out["numbers"], out["rows"]
    sp = n["share_basis"]["split"]
    assert sp is not None, n["share_basis"]                                        # round 2: None (unconfirmed)
    assert sp["confirmed_against_period"] == "2024-12-31" and close(sp["dei_to_shares"], 1 / 3), sp
    assert sp["periods_adjusted"] == [f"{y}-12-31" for y in SYN_YEARS if y != 2025], sp
    assert sp["periods_override_not_rescaled"] == ["2025-12-31"] and n["share_basis"]["unconfirmed_split_facts"] == [], sp
    assert close(f(row(rows, "2024-12-31")["shares_diluted"]), 100e6) and f(row(rows, "2025-12-31")["shares_diluted"]) == 100e6
    for k in ("base_oe_per_share", "implied_irr_weighted", "market_cap_est"):
        assert close(n[k], ref[k], rel=1e-9), (k, n[k], ref[k])                   # round 2: base 0.6509, IRR 6.03%
    assert n["tier_by_numbers"] == ref["tier_by_numbers"] == "C", (n["tier_by_numbers"], ref["tier_by_numbers"])
    fl = flags(n, "SHARE_BASIS_ADJUSTED")
    assert len(fl) == 1 and "except FY2025 (OVERRIDE count, not rescaled)" in fl[0], fl
    assert fl[0].endswith("(dei 100,000,000 on 2026-07-31 confirms against the FY2024 filed count)"), fl
    # the pre-split override: the split is still confirmed against FY2024; the override stays at 300,000,000 and the
    # flag names it as not rescaled (WORKER_SPEC step 8: restate it on the post-split basis -> the case above)
    n2 = _r3_split_run(300e6)["numbers"]
    sp2 = n2["share_basis"]["split"]
    assert sp2 and sp2["confirmed_against_period"] == "2024-12-31" and sp2["periods_override_not_rescaled"] == ["2025-12-31"]
    assert n2["shares_diluted_latest"] == 300e6 and "except FY2025 (OVERRIDE count, not rescaled)" in flags(n2, "SHARE_BASIS_ADJUSTED")[0]


def test_r3_split_latest_fy_filed_keeps_the_round_2_text():
    """Verifier round 3 (R3-SPLIT, no-change guard): with the latest FY's count filed, the split is confirmed against
    that same year, as before — confirmed_against_period is the latest FY and the flag text carries no 'against'
    clause (DD's and MLI's records are unchanged but for the new key)."""
    facts = _syn_facts(shares=dict.fromkeys(SYN_YEARS, 300e6), dei=(100e6, "2026-07-31", "2026-08-05"))
    _split_fact(facts, "2026-06-30", 0.333, "2026-08-05", start="2026-06-30")
    n = _syn_run(facts)["numbers"]
    sp = n["share_basis"]["split"]
    assert sp and sp["confirmed_against_period"] == "2025-12-31" and "2025-12-31" in sp["periods_adjusted"], sp
    fl = flags(n, "SHARE_BASIS_ADJUSTED")
    assert len(fl) == 1 and fl[0].endswith("(dei 100,000,000 on 2026-07-31 confirms)"), fl


# ---- R2-PIN: test (a) on the base actually used ----
TTM_PIN_MISSCALED = 2180.19   # ttm.py's pin when the current-YTD diluted count is filed in thousands (73x a $30 price)


def test_r2_pin_share_scale_check_tests_the_pin_unit():
    """Verifier round 2 (P1, adversarial): share_scale_check tests the pin actually used — |pin| > 20x price is a
    defect (pin_over_price) whatever the native median says; exactly 20x passes; no pin is the 5.5 result."""
    S = E.share_scale_check
    r = S(1.95, 30.0, 100e6, 100e6, pin=TTM_PIN_MISSCALED, pin_source="ttm_json")   # round 1: TypeError
    assert r["defect"] is True and r["pin_over_price"] is True and r["tests"] == {"a": False, "b": False}, r
    assert len(r["reasons"]) == 1 and "the --ttm pin" in r["reasons"][0] and "73x the price" in r["reasons"][0], r
    assert S(1.95, 30.0, 100e6, 100e6, pin=600.0, pin_source="base_oe_ps_arg")["defect"] is False       # exactly 20x
    assert S(1.95, 30.0, 100e6, 100e6, pin=-600.01, pin_source="base_oe_ps_arg")["pin_over_price"] is True  # |pin|
    assert S(1.95, None, 100e6, 100e6, pin=5000.0, pin_source="ttm_json")["defect"] is False            # no price
    clean = S(1.95, 30.0, 100e6, 100e6)
    assert clean["defect"] is False and clean["pin_over_price"] is False and clean["reasons"] == [], clean


def test_r2_pin_over_20x_price_gaps_on_clean_annual_counts_e2e():
    """Verifier round 2 (P1, adversarial, fake Tier S): clean FY counts, dei 100M, price $30 — a --ttm pin of 2,180.19
    (ttm.py on a current-YTD diluted count filed in thousands) used to score Tier S at IRR 200% with no gap and no
    SHARE flag, because test (a) ran on the native median only. Now: exit 4, gap 'share_scale', pin_over_price, the
    gap text names the --ttm pin. The same through --base-oe-ps with a matching declaration gaps too (the pin fails
    E1 (3), named in pin_rejected); a sane pin on the same filer still scores."""
    out = run("SYN", args_for(5, extra=["--ttm"]), judgment={}, ttm={"ttm_oe_per_share": TTM_PIN_MISSCALED},
              fixture=_syn_fixture(_syn_facts()))
    n = out["numbers"]
    assert out["exit"] == 4 and "share_scale" in n["data_gap_uncovered"], (out["exit"], n.get("data_gap"), n.get("tier_by_numbers"))
    ss = n["share_scale"]
    assert ss["defect"] and ss["pin_over_price"] and not ss["tests"]["a"] and not ss["tests"]["b"], ss
    assert ss["rescued_by_pin"] is False and ss["pin_rejected"] is None and ss["scale_factor"] is None, ss
    fl = flags(n, SCALE_GAP)
    assert len(fl) == 1 and "the --ttm pin (ttm.json ttm_oe_per_share) 2,180.19 is 73x the price" in fl[0], fl
    o = _syn_run(_syn_facts(), ["--base-oe-ps", "700"], judgment={"base_override": _bo(700.0)})
    assert o["exit"] == 4 and "share_scale" in o["numbers"]["data_gap"], o["exit"]
    assert any("x the price" in w for w in o["numbers"]["share_scale"]["pin_rejected"]), o["numbers"]["share_scale"]
    ok = _syn_run(_syn_facts(), ["--base-oe-ps", "2.0"], judgment={"base_override": _bo(2.0)})
    assert ok["exit"] == 0 and ok["numbers"]["share_scale"]["defect"] is False, ok["stdout"][-800:]
    assert ok["numbers"]["share_scale"]["pin_over_price"] is False


def test_r2_ttm_warns_when_its_denominator_is_off_scale():
    """Verifier round 2 (P1, adversarial; ttm.py half): the current-YTD diluted count filed in thousands (705,000
    against a 700,000,000 FY leg and a 702M cover page) gives a TTM pin ~1,356/share with no warning in round 1. Now
    ttm.json warns twice (FY leg, cover page); values are unchanged. The normal fixture warns nothing about shares."""
    fx = _ttm_fixture(PRIMARY, 52e6, 25e6, 27e6)
    us = fx["facts"]["facts"]["us-gaap"]
    for e in us[SYN_SHARE_TAG]["units"]["shares"]:
        if e["end"] == "2026-06-30":
            e["val"] = 705e3
    fx["facts"]["facts"]["dei"] = {"EntityCommonStockSharesOutstanding": {"units": {"shares": [
        {"end": "2026-07-31", "val": 702e6, "fy": 2026, "fp": "Q2", "form": "10-Q", "filed": "2026-08-03", "accn": "x-1"}]}}}
    t = run_ttm("SYNT", fixture=fx)
    assert t["exit"] == 0, t["stderr"]
    out = t["ttm"]
    assert out["ttm_shares_diluted"] == 705e3 and out["ttm_oe_per_share"] > 20 * 30.0, out["ttm_oe_per_share"]
    w = [x for x in out["warnings"] if x.startswith("shares: the TTM denominator")]
    assert len(w) == 2, out["warnings"]
    assert "x the FY diluted count 700,000,000" in w[0] and "x the cover-page count 702,000,000 (2026-07-31" in w[1], w
    clean = run_ttm("SYNT", fixture=_ttm_fixture(PRIMARY, 52e6, 25e6, 27e6))["ttm"]
    assert not [x for x in clean["warnings"] if x.startswith("shares:")], clean["warnings"]


# ---- R2-E2: the OE/share CAGR stays when no break lies between its endpoints ----
def test_r2_e2_oe_ps_cagr_kept_when_the_break_precedes_its_window_e2e():
    """Verifier round 2 (P2, adversarial, C -> D crossing): revenue CAGR ~2% (5y) / ~4% (3y) / 8% (yoy) and an
    OE/share CAGR of ~15%; the defect twin files FY2023-25 counts in thousands (FY2022 100M, dei 100M) and declares
    pin 1.75. The only break (FY2022 -> FY2023) lies BEFORE the OE/share CAGR's window (FY2023 -> FY2025, both in
    thousands), so that CAGR is valid. Round 1 dropped it anyway (growth median 4% instead of 6%) and the twin
    scored Tier D where the clean filer scores C. Now the twin keeps it (growth_inputs_kept), drops only the share
    CAGR, and matches the clean filer's g_base, IRR and tier; the flag says the OE/share CAGR stays (round 4: it
    reads only its two endpoints, whose counts share one scale)."""
    rev = {2019: 970e6, 2020: 978.2e6, 2021: 970e6, 2022: 960.1e6, 2023: 980e6, 2024: 1000e6, 2025: 1080e6}
    ocf = {2019: 180e6, 2020: 185e6, 2021: 190e6, 2022: 195e6, 2023: 200e6, 2024: 221e6, 2025: 245.15e6}

    def facts(shares=None):
        fs = _syn_facts(shares=shares)
        _syn_set(fs, "Revenues", rev)
        _syn_set(fs, "NetCashProvidedByUsedInOperatingActivities", ocf)
        return fs
    pin = ["--base-oe-ps", "1.75"]
    clean = _syn_run(facts(), pin, judgment={"base_override": _bo(1.75)})["numbers"]
    out = _syn_run(facts({2023: 100e3, 2024: 100e3, 2025: 100e3}), pin, judgment={"base_override": _bo(1.75)})
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    ss = n["share_scale"]
    assert ss["rescued_by_pin"] and [(b["from_period"], b["to_period"]) for b in ss["scale_breaks"]] == [("2022-12-31", "2023-12-31")], ss
    assert ss["growth_inputs_dropped"] == ["share_cagr"] and ss["growth_inputs_kept"] == ["oe_ps_cagr_2y"], ss
    assert close(n["growth_components_adjusted"]["oe_ps_cagr_2y"], clean["growth_components"]["oe_ps_cagr_2y"], rel=1e-12)
    assert abs(n["growth_components_adjusted"]["oe_ps_cagr_2y"] - 0.15) < 0.002, n["growth_components_adjusted"]
    assert close(n["g_base"], clean["g_base"], rel=1e-9) and abs(n["g_base"] - 0.06) < 0.002, (n["g_base"], clean["g_base"])
    assert close(n["implied_irr_weighted"], clean["implied_irr_weighted"], rel=1e-9), (n["implied_irr_weighted"], clean["implied_irr_weighted"])
    assert clean["tier_by_numbers"] == n["tier_by_numbers"] == "C", (clean["tier_by_numbers"], n["tier_by_numbers"])  # round 1: D
    fl = flags(n, "SHARE_SCALE_SUSPECT")
    # [verifier round 4, R4-E2] the note says what the rule tests: the CAGR's two endpoints share one scale
    assert len(fl) == 1 and "the OE/share CAGR reads only its two endpoints" in fl[0] and "the share-count CAGR (" in fl[0], fl
    # a break INSIDE the OE/share window (FY2024 -> FY2025) still drops it (VIV: test_viv_scale_guard_e2e)
    inside = _syn_run(facts({2023: 100e3, 2024: 100e3}), ["--base-oe-ps", "1.75"], judgment={"base_override": _bo(1.75)})["numbers"]
    assert inside["share_scale"]["growth_inputs_dropped"] == ["share_cagr", "oe_ps_cagr_2y"], inside["share_scale"]
    assert inside["share_scale"]["growth_inputs_kept"] == [] and inside["growth_components_adjusted"]["oe_ps_cagr_2y"] is None


# ---- R2-E4: a skipped cover-page zero is recorded ----
def test_r2_e4_skipped_cover_page_zero_is_recorded_e2e():
    """Verifier round 2 (P3, differential; LTM 2017): FY2020 files no diluted count and no outstanding count, and the
    only cover page within 90 days after it carries 0 — round 1 skipped it (E4) with no record, so the year silently
    left SHARES_FALLBACK. Now share_basis.nonpositive_counts lists it (series 'dei', its cover date, replaced_by null);
    with a positive cover count in the same window the year falls back to it and the record names it."""
    fs = _syn_facts(shares={2020: None})
    _syn_dei(fs, "2021-01-31", 0, "2021-02-20")
    out = _syn_run(fs)
    assert out["exit"] == 0, out["stdout"][-1500:]
    npc = out["numbers"]["share_basis"]["nonpositive_counts"]
    assert npc == [{"period": "2020-12-31", "series": "dei", "tag": "EntityCommonStockSharesOutstanding", "value": 0,
                    "date": "2021-01-31", "replaced_by": None}], npc               # round 1: []
    assert row(out["rows"], "2020-12-31")["shares_diluted"] == ""
    assert not flags(out["numbers"], "SHARES_FALLBACK")
    fs2 = _syn_facts(shares={2020: None})
    _syn_dei(fs2, "2021-01-31", 0, "2021-02-20")
    _syn_dei(fs2, "2021-02-15", 98e6, "2021-02-25")
    out2 = _syn_run(fs2)
    npc2 = out2["numbers"]["share_basis"]["nonpositive_counts"]
    assert npc2 == [dict(npc[0], replaced_by="dei:EntityCommonStockSharesOutstanding@2021-02-15")], npc2
    r = row(out2["rows"], "2020-12-31")
    assert f(r["shares_diluted"]) == 98e6 and r["shares_tag"] == "FALLBACK:dei:EntityCommonStockSharesOutstanding@2021-02-15", r
    assert "2020" in flags(out2["numbers"], "SHARES_FALLBACK")[0]


# ---- Verifier round 4: R4-CAP / R4-E2 (endpoint tests), R4-E3 (an agreeing dei on the median year's scale), and
# ttm.py's prior-YTD leg (R4-SBC, R4-INTANG) ----
ALT_WINDOW = [("2023-12-31", 100e3), ("2024-12-31", 100e6), ("2025-12-31", 100e3)]   # endpoints in thousands


def test_r4_cap_median_latest_scale_breaks_unit():
    """Verifier round 4 (P1 fidelity + P2 adversarial, unit): R3-CAP's rule is "the median year's count and the latest
    count on one scale", so median_latest_scale_breaks compares those two counts — the endpoints of the window — and
    ignores the years between. An alternating window (FY2023 and FY2025 in thousands, FY2024 on the true scale) has
    no endpoint break, so scale_factor_for_cap takes the pin's x1,000 (round 3: (None, None) — its adjacent-pair test
    saw two breaks); BREAK_WINDOW (median year in thousands, latest right) still withholds it and names the endpoint
    pair FY2023 -> FY2025."""
    M = E.median_latest_scale_breaks
    assert M(ALT_WINDOW) == [], M(ALT_WINDOW)
    assert M(BREAK_WINDOW) == [("2023-12-31", 100e3, "2025-12-31", 100e6)], M(BREAK_WINDOW)
    assert M(THOUSANDS_WINDOW) == [] and M(TEM_WINDOW) == [] and M([("2025-12-31", 5)]) == [] and M([]) == []
    F = E.scale_factor_for_cap
    assert F(100e3, None, 1830.1, 1.8301, window_counts=ALT_WINDOW) == (1000, "pin")      # round 3: (None, None)
    assert F(100e3, 100e3, 1830.1, 1.8301, window_counts=ALT_WINDOW) == (1000, "pin")     # dei in thousands too
    assert F(100e6, None, 1830.1, 1.8301, window_counts=BREAK_WINDOW) == (None, None)
    viv = [("2023-12-31", 1658604), ("2024-12-31", 1643132), ("2025-12-31", 3195606352)]
    assert M(viv) == [("2023-12-31", 1658604, "2025-12-31", 3195606352)]                 # VIV keeps no pin factor


def _r4_alt_facts(dei=None, fy2024=100e6):
    return _syn_facts(shares={**dict.fromkeys(SYN_YEARS, 100e3), 2024: fy2024}, dei=dei)


def test_r4_cap_alternating_series_takes_the_pin_factor_e2e():
    """Verifier round 4 (P1, fidelity): every diluted count filed in thousands (100,000) except FY2024 on the true
    scale (100,000,000), price $30, the declared pin = the FY2023 OE/share on the true count (native median / 1,000).
    The median year FY2023 and the latest year FY2025 are both in thousands, so the pin's x1,000 is right for the
    latest count — the round-3 adjacent-pair test withheld it: cap 3,000,000 (true 3.0e9), leverage suppressed, and
    SHARE_SCALE_SUSPECT said the two equal counts were 'on another scale'. Now: factor 1000 (pin), cap 3.0e9, net
    debt / OE on 100M shares, nothing withheld. The same holds (a) when FY2024 is untagged and filled by a true-scale
    kind 'filing' shares_override, and (b) with a cover-page count filed in thousands too (finding 6: round 3 printed
    HIGH_NET_DEBT 546x there)."""
    cases = (("alternating, no dei", _r4_alt_facts(), {}),
             ("FY2024 from a shares_override", _r4_alt_facts(fy2024=None),
              {"shares_override": _o(100e6, source="10-K FY2024 EPS note (test)", reason="FY2024 diluted count untagged",
                                     ack_reason="test")}),
             ("dei in thousands", _r4_alt_facts(dei=(100e3, "2026-01-31", "2026-02-20")), {}))
    for label, facts, extra in cases:
        j = {"base_override": _bo(R3_OE23)}
        j.update(extra)
        out = _syn_run(facts, ["--base-oe-ps", repr(R3_OE23)], judgment=j)
        n = out["numbers"]
        assert out["exit"] == 0, (label, out["stdout"][-1500:])
        ss = n["share_scale"]
        assert ss["defect"] and ss["tests"]["a"] and ss["rescued_by_pin"], (label, ss)
        assert ss["scale_factor"] == 1000 and ss["factor_basis"] == "pin", (label, ss)          # round 3: None
        assert ss["pin_factor_withheld"] is None and ss["leverage_unverifiable"] is False, (label, ss)
        assert n["market_cap_basis"]["shares_used"] == 100e6, (label, n["market_cap_basis"])
        assert n["market_cap_basis"]["shares_source"] == "diluted_latest_scale_corrected", (label, n["market_cap_basis"])
        assert n["market_cap_est"] == 30.0 * 100e6, (label, n["market_cap_est"])                # round 3: 3.0e6
        assert close(n["diagnostics"]["net_debt_to_normalized_oe"], nd_identity(n), rel=1e-12), (label, n["diagnostics"])
        assert not flags(n, "HIGH_NET_DEBT") and not flags(n, "BIG_NET_CASH"), (label, n["fragility_flags"])
        fl = flags(n, "SHARE_SCALE_SUSPECT")
        assert len(fl) == 1 and "x 1000 (pin basis: 100,000,000 shares)" in fl[0], (label, fl)
        assert "on another scale than the latest count" not in fl[0], (label, fl)
        if label == "FY2024 from a shares_override":
            assert row(out["rows"], "2024-12-31")["shares_tag"] == "OVERRIDE", label


def test_r4_cap_withheld_factor_names_the_endpoint_pair_e2e():
    """Verifier round 4 (R4-CAP record): when the factor IS withheld (FY2023-24 in thousands, FY2025 right),
    pin_factor_withheld.breaks and the SHARE_SCALE_SUSPECT text name the endpoint pair the rule tests — the median
    year FY2023 against the latest year FY2025 — not the adjacent FY2024 -> FY2025 pair round 3 printed."""
    n = _r3_cap_run(None)
    wh = n["share_scale"]["pin_factor_withheld"]
    assert wh and wh["factor"] == 1000 and wh["breaks"] == [{"from_period": "2023-12-31", "from_count": 100e3,
                                                              "to_period": "2025-12-31", "to_count": 100e6}], wh
    fl = flags(n, "SHARE_SCALE_SUSPECT")[0]
    assert "(FY2023 100,000 -> FY2025 100,000,000), so it does not apply" in fl, fl


def test_r4_e2_alternating_series_keeps_the_oe_ps_cagr_e2e():
    """Verifier round 4 (P1, fidelity — R2-E2 incomplete): the OE/share CAGR reads only oe_ps_hist[-3] (FY2023) and
    oe_ps_hist[-1] (FY2025), whose counts are both in thousands; FY2024 between them is on the true scale. Round 3's
    _oe_break tested every adjacent pair from FY2023 to FY2025 and dropped the valid CAGR. Now it stays: the same
    value as the all-thousands reference, growth_inputs_kept names it, and the flag says it reads only its endpoints.
    The share-count CAGR still leaves the blend (ruling E2: any break among the last four counts)."""
    pin = ["--base-oe-ps", repr(R3_OE23)]
    j = {"base_override": _bo(R3_OE23)}
    ref = _syn_run(_syn_facts(shares=dict.fromkeys(SYN_YEARS, 100e3), dei=None), pin, judgment=j)["numbers"]
    out = _syn_run(_r4_alt_facts(), pin, judgment=j)
    n = out["numbers"]
    assert out["exit"] == 0, out["stdout"][-1500:]
    ss = n["share_scale"]
    assert ss["growth_inputs_kept"] == ["oe_ps_cagr_2y"] and ss["growth_inputs_dropped"] == ["share_cagr"], ss
    cagr = n["growth_components_adjusted"]["oe_ps_cagr_2y"]                                    # round 3: None
    assert cagr is not None and close(cagr, ref["growth_components_adjusted"]["oe_ps_cagr_2y"], rel=1e-12), (cagr, ref["growth_components_adjusted"])
    assert close(n["g_base"], ref["g_base"], rel=1e-12), (n["g_base"], ref["g_base"])
    fl = flags(n, "SHARE_SCALE_SUSPECT")[0]
    assert "the OE/share CAGR reads only its two endpoints, whose counts are on one scale, so it stays in the blend" in fl, fl


def test_r4_e3_dei_agreeing_with_a_latest_count_on_the_median_scale_suppresses_leverage_e2e():
    """Verifier round 4 (P1, adversarial — the round-3 case (c) fix incomplete): every diluted count AND the cover page
    filed in thousands (100,000), a declared TTM-style pin 2.0 or 2.3 — 2.4% / 15% off native / 1,000, so
    pin_power_of_ten finds no factor. Round 3 kept the leverage diagnostics because the dei 'passed' test (b), and
    printed net debt / normalized OE 500x / 434.8x with HIGH_NET_DEBT on the 1,000x-small total, reassuring the reader
    that 'the cover-page count agrees with it within 25%'. The latest count is on the median year's scale, which test
    (a) found wrong, so the agreement verifies nothing: leverage_unverifiable, no ratio, no leverage flag, and the flag
    says why. The cap stays price x the filed count (no factor is invented — README follow-up). With the pin exactly
    native / 1,000 (1.95) the factor applies as before (test_r3_cap_every_count_and_the_dei_in_thousands...)."""
    for pin in (2.0, 2.3):
        n = _r3_cap_run((100e3, "2026-01-31", "2026-02-20"), shares=dict.fromkeys(SYN_YEARS, 100e3), pin=pin)
        ss = n["share_scale"]
        assert ss["defect"] and ss["tests"]["a"] and not ss["tests"]["b"] and close(ss["dei_ratio"], 1.0), (pin, ss)
        assert ss["rescued_by_pin"] and ss["scale_factor"] is None and ss["pin_factor_withheld"] is None, (pin, ss)
        assert ss["leverage_unverifiable"] is True, (pin, ss)                                    # round 3: False
        assert n["diagnostics"]["net_debt_to_normalized_oe"] is None, (pin, n["diagnostics"])    # round 3: 500.0 / 434.8
        assert not flags(n, "HIGH_NET_DEBT") and not flags(n, "BIG_NET_CASH"), (pin, n["fragility_flags"])
        assert n["market_cap_est"] == 30.0 * 100e3, (pin, n["market_cap_est"])
        fl = flags(n, "SHARE_SCALE_SUSPECT")
        assert len(fl) == 1 and "agrees with it within 25%" not in fl[0], (pin, fl)
        assert "verifies nothing" in fl[0] and "leverage diagnostics are unverifiable" in fl[0], (pin, fl)
    # a dei that agrees with a latest count on ANOTHER scale than the median year keeps the diagnostics (VIV shape:
    # test_r2_cap_dei_confirming_the_latest_count_takes_no_pin_factor asserts leverage_unverifiable False there)


def test_r4_e3_tem_with_its_ttm_derived_pin_is_unverifiable_e2e():
    """Verifier round 4 (finding 5, TEM): TEM's x1,000 cap holds only because its declared pin equals the FY2023
    native / 1,000. With a TTM-derived pin (its ttm.json value / 1,000, -2.50477 — no power of ten off the native
    base) no factor is found: the cap is price x the filed 174,264 (diluted_latest) and, with no cover-page count, the
    leverage diagnostics are unverifiable and the flag says so (E3). Guard test: the cap residual is a README
    follow-up."""
    pin = TEM_TTM_MISSCALED / 1000
    n = run("TEM", TEM_ARGS + ["--base-oe-ps", repr(pin)], judgment={"base_override": _bo(pin, kind="estimate")})["numbers"]
    ss = n["share_scale"]
    assert ss["rescued_by_pin"] and ss["scale_factor"] is None and ss["leverage_unverifiable"] is True, ss
    assert n["market_cap_basis"]["shares_source"] == "diluted_latest" and n["market_cap_basis"]["shares_used"] == 174264, n["market_cap_basis"]
    assert n["tier_by_numbers"] == "F" and not flags(n, "HIGH_NET_DEBT") and not flags(n, "BIG_NET_CASH"), n["fragility_flags"]
    assert "leverage diagnostics are unverifiable" in flags(n, "SHARE_SCALE_SUSPECT")[0]


_TTM_LEGS = (("2025-01-01", "2025-12-31", "10-K", "FY", None, "2026-02-20"),
             ("2025-01-01", "2025-06-30", "10-Q", "Q2", 2025, "2025-08-01"),
             ("2026-01-01", "2026-06-30", "10-Q", "Q2", 2026, "2026-08-03"))


def _ttm_leg_facts(vals):
    """(FY, H1 prior, H1 current) values -> the _ttm_fixture contexts; None = not filed on that leg."""
    return [_ctx(s, e, v, form=form, fp=fp, fy=fy, filed=filed)
            for (s, e, form, fp, fy, filed), v in zip(_TTM_LEGS, vals) if v is not None]


def _ttm_sbc_fixture(share, alloc):
    """_ttm_fixture's filer (PP&E capex 52M / 25M / 27M) with its SBC facts replaced: share / alloc are (FY, H1 prior,
    H1 current) tuples, None = not filed on that leg."""
    fx = _ttm_fixture(PRIMARY, 52e6, 25e6, 27e6)
    us = fx["facts"]["facts"]["us-gaap"]
    us.pop(SBC_SHARE, None)
    for tag, vals in ((SBC_SHARE, share), (SBC_ALLOC, alloc)):
        es = _ttm_leg_facts(vals)
        if es:
            us[tag] = {"units": {"USD": es}}
    return fx


def test_r4_sbc_ttm_never_below_the_unreconciled_ttm():
    """Verifier round 4 (P2, differential; SYM shape): FY Share 183,936,000 > Allocated 174,402,000 (Share kept),
    prior-YTD Allocated 97,956,000 > Share 92,322,000 (reconciled), current-YTD Share 142,919,000 > Allocated
    142,902,000 (Share kept). Reconciliation per leg raised the SUBTRACTED leg, so TTM SBC fell to 228,899,000 —
    below Share's 234,533,000, although decision 6 can only raise SBC. Now the prior-YTD leg keeps its Share figure:
    TTM SBC 234,533,000, sbc_reconciled_legs {}, sbc_reconciliation_withdrawn_legs names the leg with both TTMs, and
    a warning says why."""
    t = run_ttm("SYNT", judgment={}, fixture=_ttm_sbc_fixture((183936000, 92322000, 142919000),
                                                              (174402000, 97956000, 142902000)))
    assert t["exit"] == 0, t["stderr"]
    out = t["ttm"]
    assert out["ttm_sbc"] == 183936000 - 92322000 + 142919000, out["ttm_sbc"]                 # round 3: 228,899,000
    assert out["inputs"]["sbc"]["ytd_prior_tag"] == SBC_SHARE and out["sbc_reconciled_legs"] == {}, out["inputs"]["sbc"]
    wd = out["sbc_reconciliation_withdrawn_legs"]
    assert set(wd) == {"ytd_prior"} and wd["ytd_prior"]["ttm_reconciled"] == 228899000, wd
    assert wd["ytd_prior"]["ttm_unreconciled"] == wd["ytd_prior"]["ttm_used"] == 234533000, wd
    assert [w for w in out["warnings"] if w.startswith("sbc ytd_prior:") and "SUBTRACTED" in w], out["warnings"]


def test_r4_sbc_added_legs_still_reconcile_and_mixed_tags_warn():
    """Verifier round 4 (R4-SBC): the floor touches only the prior-YTD leg. JHX shape — FY files only Share 38.0M, both
    YTD legs file both tags with Allocated larger (10.9M / 15.2M over 6.9M / 12.0M): the prior-YTD leg keeps Share
    (round 3: TTM 42.3M, below Share's 43.1M), the current-YTD leg stays reconciled -> 38.0 - 6.9 + 15.2 = 46.3M, and
    the mixed-tag warning names each leg's tag. JLL shape — Allocated 112.0M on the FY leg only, the 10-Qs file just
    the Share slice (1.4M / 0.2M): TTM 110.8M is unchanged (one tag on all three legs would give 1.5M), nothing is
    withdrawn, and the mixed-tag warning fires. All three legs reconciled: no warning, nothing withdrawn."""
    jhx = run_ttm("SYNT", judgment={}, fixture=_ttm_sbc_fixture((38e6, 6.9e6, 12e6), (None, 10.9e6, 15.2e6)))["ttm"]
    assert close(jhx["ttm_sbc"], 38e6 - 6.9e6 + 15.2e6), jhx["ttm_sbc"]                       # round 3: 42.3M
    assert set(jhx["sbc_reconciled_legs"]) == {"ytd_current"}, jhx["sbc_reconciled_legs"]
    assert set(jhx["sbc_reconciliation_withdrawn_legs"]) == {"ytd_prior"}, jhx["sbc_reconciliation_withdrawn_legs"]
    mixed = [w for w in jhx["warnings"] if w.startswith("sbc: ") and "mixes tags" in w]
    assert len(mixed) == 1 and f"ytd_current {SBC_ALLOC}" in mixed[0] and f"fy {SBC_SHARE}" in mixed[0], jhx["warnings"]
    jll = run_ttm("SYNT", judgment={}, fixture=_ttm_sbc_fixture((2.7e6, 1.4e6, 0.2e6), (112e6, None, None)))["ttm"]
    assert close(jll["ttm_sbc"], 112e6 - 1.4e6 + 0.2e6), jll["ttm_sbc"]
    assert set(jll["sbc_reconciled_legs"]) == {"fy"} and jll["sbc_reconciliation_withdrawn_legs"] == {}, jll
    assert len([w for w in jll["warnings"] if "mixes tags" in w]) == 1, jll["warnings"]
    uni = run_ttm("SYNT", judgment={}, fixture=_ttm_sbc_fixture((40e6, 20e6, 22e6), (41e6, 21e6, 23e6)))["ttm"]
    assert uni["ttm_sbc"] == 41e6 - 21e6 + 23e6, uni["ttm_sbc"]
    assert set(uni["sbc_reconciled_legs"]) == {"fy", "ytd_prior", "ytd_current"}, uni["sbc_reconciled_legs"]
    assert uni["sbc_reconciliation_withdrawn_legs"] == {} and not [w for w in uni["warnings"] if w.startswith("sbc")]


def _ttm_intang_fixture(fy, h1p, h1c):
    fx = _ttm_fixture(PRIMARY, 52e6, 25e6, 27e6)
    fx["facts"]["facts"]["us-gaap"][INTANG] = {"units": {"USD": _ttm_leg_facts((fy, h1p, h1c))}}
    return fx


def test_r4_intang_ttm_remainder_must_be_measurable():
    """Verifier round 4 (P2, differential; BAX shape): PaymentsToAcquireIntangibleAssets filed only in the 10-Qs
    (prior YTD 9,000,000, current YTD 3,000,000), none in the 10-K. Added per leg, the TTM contribution was
    0 - 9,000,000 + 3,000,000 = -6,000,000, cutting TTM capex below 5.4's PP&E-only figure. Now the FY - prior-YTD
    remainder is unknown, so neither of those legs adds intangibles ('remainder_unknown', warning) and the current
    YTD adds its own: PP&E TTM 54M + 3M = 57M (the BAX lower bound). An FY figure below the prior YTD is unknown too;
    a measurable remainder (FY 12M >= 9M) and a current-YTD-only filer (TPL shape) are unchanged."""
    ppe_ttm = 52e6 - 25e6 + 27e6
    for fy, expect, warned in ((None, ppe_ttm + 3e6, True), (5e6, ppe_ttm + 3e6, True),
                               (12e6, ppe_ttm + 12e6 - 9e6 + 3e6, False)):
        t = run_ttm("SYNT", judgment={}, fixture=_ttm_intang_fixture(fy, 9e6, 3e6))
        assert t["exit"] == 0, t["stderr"]
        out = t["ttm"]
        assert close(out["ttm_capex"], expect), (fy, out["ttm_capex"])                         # round 3: 48M (fy None)
        comps = out["capex_components"]
        notes = [w for w in out["warnings"] if "remainder is unknown" in w]
        if warned:
            assert comps["ytd_prior"]["intangibles_not_added"] == "remainder_unknown", (fy, comps["ytd_prior"])
            assert len(notes) == 1 and "9,000,000" in notes[0], (fy, out["warnings"])
            assert out["inputs"]["capex"]["ytd_prior_tag"] == PRIMARY, out["inputs"]["capex"]
            assert out["inputs"]["capex"]["ytd_current_tag"] == f"{PRIMARY}+{INTANG}", out["inputs"]["capex"]
        else:
            assert not notes and "intangibles_not_added" not in comps["ytd_prior"], (fy, out["warnings"])
    tpl = run_ttm("SYNT", judgment={}, fixture=_ttm_intang_fixture(None, None, 21.4e6))["ttm"]
    assert close(tpl["ttm_capex"], ppe_ttm + 21.4e6) and not [w for w in tpl["warnings"] if "remainder" in w], tpl["warnings"]


# ===========================================================================
# 9. make_score.py (synthetic folders, DESIGN §8)
# ===========================================================================
PROBS = [0.1, 0.25, 0.3, 0.25, 0.1]
_BASIS_55 = {"shares_used": 1.0e8, "shares_source": "diluted_latest", "ads_ratio": None, "formula": FORMULA_PLAIN}


def _content_hash(n):
    canon = json.dumps({k: v for k, v in n.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canon.encode()).hexdigest()


def _ms_numbers(basis=True, **over):
    """An engine-stamped dcf_numbers.json for ticker TST (valid content_hash). basis=False leaves out
    market_cap_basis (pre-5.5 output never has one)."""
    n = {"ticker": "TST", "name": "Test Co", "cik": 1, "engine_version": 5, "engine_release": "5.5.0",
         "as_of": "2026-10-18", "price": 50.0, "price_source": "nasdaq_quote_api",
         "shares_diluted_latest": 1.0e8, "market_cap_est": 5.0e9, "net_debt_latest": 0.0,
         "latest_period_end": "2025-12-31", "filer_annual_form": "10-K", "ads_ratio": None,
         "base_oe_per_share": 3.0, "base_source": "median_of_last_3_fy_oe_per_share",
         "tier_by_numbers": "B", "moat_score": 6.0, "cap_years": 9.8, "g_terminal": 0.025, "g_base": 0.07,
         "inputs": {"moat": 6.0, "probs": PROBS, "offsets": [-0.12, -0.05, 0.0, 0.05, 0.12],
                    "mults": [0.75, 0.9, 1.0, 1.1, 1.25], "g_terminal": 0.025, "base_oe_ps_arg": None,
                    "base_pin_source": None},
         "data_gap": [], "data_gap_uncovered": [], "overrides_applied": [], "override_checks": {},
         "scenarios": {lbl: {"prob": p, "g_start": 0.07, "oe_mult": 1.0, "iv_at_10": 70.0, "iv_at_12": 60.0,
                             "iv_at_15": 50.0, "iv_at_20": 40.0, "iv_at_25": 30.0, "irr": 0.13, "irr_at_floor": False}
                       for lbl, p in zip(LABELS, PROBS)},
         "weighted": {"iv_at_10": 70.0, "iv_at_12": 60.0, "iv_at_15": 50.0, "iv_at_20": 40.0, "iv_at_25": 30.0,
                      "irr": 0.13, "irr_at_floor": False},
         "implied_irr_weighted": 0.13, "implied_irr_base": 0.13, "irr_bear": 0.12, "irr_bull": 0.14,
         "tier_bear": "C", "tier_bull": "C", "iv_at_15": 50.0, "iv_at_12": 60.0, "iv_at_20": 40.0, "iv_at_25": 30.0,
         "upside_at_15": 0.0, "upside_at_12": 0.2, "fragility_flags": [], "diagnostics": {"irr_at_floor": False}}
    if basis:
        n["market_cap_basis"] = dict(_BASIS_55)
    n.update(over)
    n["content_hash"] = _content_hash(n)
    return n


def _ms_judgment(**over):
    j = {"name": "Test Co", "sector": "Industrials", "moat_score": 6, "moat_justification": "test",
         "probs_used": PROBS, "one_liner": "test", "confidence": "medium", "tier_override": None,
         "tier_override_reason": None, "in_scope_under_40b": True}
    j.update(over)
    return j


def _ms_run(n, j, prior_score=None):
    """make_score.py TST in a temp STOCKS_BASE; returns code / score / judgment after / registry / key / stderr."""
    base = tempfile.mkdtemp(prefix="e55_ms_")
    try:
        os.makedirs(os.path.join(base, "TST"))
        os.makedirs(os.path.join(base, "_system"))
        for name, obj in (("dcf_numbers.json", n), ("judgment.json", j), ("score.json", prior_score)):
            if obj is not None:
                with open(os.path.join(base, "TST", name), "w", encoding="utf-8") as fh:
                    json.dump(obj, fh, indent=1, ensure_ascii=False)
        reg = os.path.join(base, "_system", "overrides_registry.json")
        env = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8", MAKE_SCORE_REGISTRY=reg)
        for k in ("DCF_NO_OVERRIDES", "DCF_TTM_NO_WRITE"):
            env.pop(k, None)
        r = subprocess.run([sys.executable, MAKE_SCORE, "TST"], capture_output=True, text=True, encoding="utf-8",
                           env=env, timeout=180)
        out = {"code": r.returncode, "stderr": r.stderr, "stdout": r.stdout, "score": None, "key": None, "registry": []}
        if r.returncode == 0:
            with open(os.path.join(base, "TST", "score.json"), encoding="utf-8") as fh:
                out["score"] = json.load(fh)
            kp = os.path.join(base, "TST", "key_numbers.md")
            if os.path.exists(kp):
                with open(kp, encoding="utf-8") as fh:
                    out["key"] = fh.read()
        with open(os.path.join(base, "TST", "judgment.json"), encoding="utf-8") as fh:
            out["judgment"] = json.load(fh)
        if os.path.exists(reg):
            with open(reg, encoding="utf-8") as fh:
                out["registry"] = json.load(fh).get("entries", [])
        return out
    finally:
        shutil.rmtree(base, ignore_errors=True)


ADS2 = {"ratio": 2.0, "source": "test 20-F cover", "reason": "test"}


def test_make_score_pre55_ads_correction_rewrites_scope():
    """Decision 1 (make_score, not the engine; [READING] scope rewrite): pre-5.5 output with an applied ads_ratio
    printed price x ORDINARY shares ($50 x 1.2B = $60B, out of scope); make_score uses price x shares / ratio =
    $30B for market_cap_b, scope and key_numbers.md ('ADS-corrected by make_score'), rewrites judgment.json's
    in_scope_under_40b (it held the scope the old cap implied), records market_cap_basis
    'ads_corrected_by_make_score', in_scope_corrected_by_make_score and a registry scope_correction event."""
    n = _ms_numbers(basis=False, engine_release="5.4.0", filer_annual_form="20-F", ads_ratio=ADS2,
                    shares_diluted_latest=1.2e9, market_cap_est=60.0e9)
    j = _ms_judgment(in_scope_under_40b=False, ads_ratio=ADS2)
    res = _ms_run(n, j)
    assert res["code"] == 0, res["stderr"]
    s = res["score"]
    assert s["market_cap_b"] == 30.0 and s["in_scope_under_40b"] is True, s
    assert s["market_cap_basis"] == "ads_corrected_by_make_score", s.get("market_cap_basis")
    assert s.get("in_scope_corrected_by_make_score") is True, s
    assert res["judgment"]["in_scope_under_40b"] is True, res["judgment"]
    assert {k: v for k, v in res["judgment"].items() if k != "in_scope_under_40b"} == \
        {k: v for k, v in j.items() if k != "in_scope_under_40b"}, "only in_scope_under_40b may change"
    ev = [e for e in res["registry"] if e.get("event") == "scope_correction"]
    assert len(ev) == 1 and ev[0]["old_cap"] == 60.0e9 and ev[0]["new_cap"] == 30.0e9 and ev[0]["in_scope"] is True, ev
    assert "ADS-corrected by make_score" in (res["key"] or ""), (res["key"] or "")[:1500]


def test_make_score_pre55_ads_correction_with_judgment_already_on_the_corrected_scope():
    """Decision 1: the same pre-5.5 ADS run with judgment.json already saying in scope (the corrected cap's
    side) scores without a rewrite and without refusing."""
    n = _ms_numbers(basis=False, engine_release="5.4.0", filer_annual_form="20-F", ads_ratio=ADS2,
                    shares_diluted_latest=1.2e9, market_cap_est=60.0e9)
    j = _ms_judgment(in_scope_under_40b=True, ads_ratio=ADS2)
    res = _ms_run(n, j)
    assert res["code"] == 0, res["stderr"]
    assert res["score"]["market_cap_b"] == 30.0 and res["score"]["in_scope_under_40b"] is True
    assert res["score"]["market_cap_basis"] == "ads_corrected_by_make_score"
    assert res["judgment"] == j


def test_make_score_other_scope_disagreements_still_refuse():
    """Decision 1: 'any other disagreement still refuses' — a non-ADS pre-5.5 cap of $60B with in_scope true;
    an ADS run whose corrected cap ($100B) is still above the line; a 5.5 run contradicting its own cap."""
    n = _ms_numbers(basis=False, engine_release="5.4.0", shares_diluted_latest=1.2e9, market_cap_est=60.0e9)
    assert _ms_run(n, _ms_judgment(in_scope_under_40b=True))["code"] != 0
    n = _ms_numbers(basis=False, engine_release="5.4.0", filer_annual_form="20-F", ads_ratio=ADS2,
                    shares_diluted_latest=4.0e9, market_cap_est=200.0e9)
    assert _ms_run(n, _ms_judgment(in_scope_under_40b=True, ads_ratio=ADS2))["code"] != 0
    n = _ms_numbers(shares_diluted_latest=1.2e9, market_cap_est=60.0e9,
                    market_cap_basis=dict(_BASIS_55, shares_used=1.2e9))
    assert _ms_run(n, _ms_judgment(in_scope_under_40b=True))["code"] != 0


def test_make_score_55_output_carries_the_engine_basis_and_is_never_divided_twice():
    """Decision 1 (DESIGN §1/§8.7): for 5.5 output score.json market_cap_basis = the engine's
    market_cap_basis.shares_source (e.g. dei_latest), and an ADS cap the engine already divided ($30B) is
    taken as is — never divided by the ratio again."""
    n = _ms_numbers(market_cap_basis=dict(_BASIS_55, shares_source="dei_latest"))
    res = _ms_run(n, _ms_judgment())
    assert res["code"] == 0, res["stderr"]
    assert res["score"]["market_cap_basis"] == "dei_latest" and res["score"]["market_cap_b"] == 5.0, res["score"]
    n = _ms_numbers(filer_annual_form="20-F", ads_ratio=ADS2, shares_diluted_latest=1.2e9, market_cap_est=30.0e9,
                    market_cap_basis={"shares_used": 1.2e9, "shares_source": "diluted_latest", "ads_ratio": 2.0,
                                      "formula": FORMULA_ADS})
    res = _ms_run(n, _ms_judgment(ads_ratio=ADS2))
    assert res["code"] == 0, res["stderr"]
    s = res["score"]
    assert s["market_cap_b"] == 30.0 and s["market_cap_basis"] == "diluted_latest", s
    assert not s.get("in_scope_corrected_by_make_score"), s


def _with_capex_override(release="5.4.0"):
    n = _ms_numbers(basis=False, engine_release=release, data_gap=["capex"], data_gap_uncovered=[],
                    overrides_applied=[{"field": "capex", "value": 100000000.0, "kind": "filing", "source": "s",
                                        "reason": "r", "periods_filled": ["2023-12-31", "2024-12-31", "2025-12-31"],
                                        "out_of_band": False, "last_filed_value": 90000000}],
                    override_checks={"capex": {"value": 100000000.0, "last_filed_value": 90000000,
                                               "last_filed_unit": "USD", "out_of_band": False,
                                               "ack_reason_present": False}})
    j = _ms_judgment(capex_override={"value": 100000000, "kind": "filing", "source": "s", "reason": "r"})
    return n, j


PRIOR_IMPACT = {"base_used": "median_3y", "base_oe_without_override": 2.9, "base_oe_with_override": 3.0,
                "base_oe_impact_pct": 3.448, "weighted_irr_without_override": 0.12, "weighted_irr_with_override": 0.13,
                "weighted_irr_impact_pp": 1.0, "unblocks_tier": True}


def test_make_score_release_mismatch_carries_the_prior_impact():
    """Release (DESIGN §8.2): engine output from another release is never replayed against the current engine
    (EMBJ's 5.5 base is 43% lower from intangibles alone) — the existing score.json override_impact is carried
    with impact_carried_from_prior_score: true and counterfactual_engine_release. (Success proves no replay ran:
    the synthetic ticker has no CIK to replay.)"""
    n, j = _with_capex_override()
    res = _ms_run(n, j, prior_score={"ticker": "TST", "override_impact": dict(PRIOR_IMPACT)})
    assert res["code"] == 0, res["stderr"]
    oi = res["score"]["override_impact"]
    assert oi.get("impact_carried_from_prior_score") is True and oi.get("counterfactual_engine_release") == "5.4.0", oi
    for k in ("base_oe_without_override", "base_oe_impact_pct", "weighted_irr_without_override", "weighted_irr_impact_pp"):
        assert oi[k] == PRIOR_IMPACT[k], (k, oi[k])
    assert oi["unblocks_tier"] is True
    reg = [e for e in res["registry"] if e.get("field") == "capex"]
    assert len(reg) == 1 and reg[0]["base_oe_without_override"] == 2.9, reg


def test_make_score_release_mismatch_without_a_prior_score_records_nulls():
    """Release (DESIGN §8.2): with no prior block the impact fields are null with the note 'not measured: engine
    output predates release 5.5.0; re-run the engine to measure'; unblocks_tier is computed as today."""
    n, j = _with_capex_override()
    res = _ms_run(n, j)
    assert res["code"] == 0, res["stderr"]
    oi = res["score"]["override_impact"]
    for k in ("base_oe_without_override", "base_oe_impact_pct", "weighted_irr_without_override", "weighted_irr_impact_pp"):
        assert oi.get(k) is None, (k, oi.get(k))
    assert oi["unblocks_tier"] is True
    assert "not measured" in oi.get("note", "") and "5.5.0" in oi.get("note", ""), oi


def test_make_score_stale_release_closes_both_alert_gates():
    """Release (DESIGN §8.3 [ADDITION, policy-bearing]): output from an engine before 5.5.0 (5.4.0, or no
    engine_release at all) never alerts — alert_eligible false on a Tier A, exit_alert_eligible false on a
    Tier B, both with the reason 'engine output predates release 5.5.0 …'; current-release output alerts as
    in 5.4."""
    res = _ms_run(_ms_numbers(basis=False, engine_release="5.4.0", tier_by_numbers="A"), _ms_judgment())
    assert res["code"] == 0, res["stderr"]
    s = res["score"]
    assert s["alert_eligible"] is False and "predates release 5.5.0" in s.get("alert_suppressed_reason", ""), s
    res = _ms_run(_ms_numbers(basis=False, engine_release="5.4.0", tier_by_numbers="B"), _ms_judgment())
    s = res["score"]
    assert s["exit_alert_eligible"] is False and "predates release 5.5.0" in s.get("exit_alert_suppressed_reason", ""), s
    res = _ms_run(_ms_numbers(basis=False, engine_release=None, tier_by_numbers="A"), _ms_judgment())
    assert res["code"] == 0, res["stderr"]
    assert res["score"]["alert_eligible"] is False, res["score"]
    res = _ms_run(_ms_numbers(tier_by_numbers="A"), _ms_judgment())
    assert res["code"] == 0, res["stderr"]
    assert res["score"]["alert_eligible"] is True and "alert_suppressed_reason" not in res["score"], res["score"]
    res = _ms_run(_ms_numbers(tier_by_numbers="B"), _ms_judgment())
    assert res["score"]["exit_alert_eligible"] is True, res["score"]


def test_make_score_validate_overrides_currency():
    """Decision 7 (make_score validate_overrides): `currency`, when present, must be 'USD' and the kind
    'filing' — EUR refuses, USD on an estimate refuses, USD on a filing override is accepted (and kept),
    no currency is accepted as before."""
    M = importlib.import_module("make_score")

    def refused(j):
        with contextlib.redirect_stderr(io.StringIO()):
            try:
                M.validate_overrides(j)
            except SystemExit:
                return True
        return False
    assert refused({"sbc_override": _o(5000000, currency="EUR")})
    assert refused({"sbc_override": _o(5000000, kind="estimate", currency="USD")})
    out = M.validate_overrides({"sbc_override": _o(5000000, currency="USD")})
    assert out["sbc"]["currency"] == "USD", out
    assert "sbc" in M.validate_overrides({"sbc_override": _o(5000000)})


def test_make_score_currency_refusal_end_to_end():
    """Decision 7: make_score.py refuses a judgment.json whose override declares a currency other than USD."""
    n, j = _with_capex_override()
    j["capex_override"]["currency"] = "EUR"
    res = _ms_run(n, j)
    assert res["code"] != 0 and res["score"] is None, res["stdout"]


def test_make_score_refuses_share_class_mismatch():
    """Decision 2 §5: make_score refuses any truthy share_class_mismatch — the bare true, an object without
    source / reason, a complete object — and says SHARE_CLASS_MISMATCH, even on engine output that carries
    no share_class gap (an engine predating the rule)."""
    for decl in (True, {"value": True}, {"value": True, "source": "FY2025 20-F (test)", "reason": "test"}):
        res = _ms_run(_ms_numbers(), _ms_judgment(share_class_mismatch=decl))
        assert res["code"] != 0 and res["score"] is None, (decl, res["stdout"])
        assert "SHARE_CLASS_MISMATCH" in res["stderr"], (decl, res["stderr"])


def test_harness_never_replaces_the_shared_engine_module():
    """[Codex, PR #31] engine55_harness runs each engine pass on a private copy of dcf_engine: after an offline run
    the module registered as sys.modules["dcf_engine"] and its functions are the very objects make_score and reprice
    imported (make_score.market_cap_estimate is dcf_engine.market_cap_est). The old harness reloaded the shared
    module, so with the whole suite in one process (pytest) test_make_score_55::test_release_helpers and
    test_reprice::test_live_market_cap_divides_by_the_ads_ratio failed (461 passed, 2 failed)."""
    import dcf_engine as shared
    import make_score as MS
    before_mod, before_fn = sys.modules["dcf_engine"], shared.market_cap_est
    assert MS.market_cap_estimate is before_fn
    out = run("CCJ", H.recorded_args(recorded_matching_fixture("CCJ")), judgment=CCJ_J)
    assert out["exit"] == 0, out["stdout"][-800:]
    assert sys.modules["dcf_engine"] is before_mod, "the harness replaced sys.modules['dcf_engine']"
    assert sys.modules["dcf_engine"].market_cap_est is before_fn, "the harness reloaded dcf_engine in place"
    assert MS.market_cap_estimate is sys.modules["dcf_engine"].market_cap_est
    priv = H._engine()
    assert priv is not sys.modules["dcf_engine"] and priv.__name__ != "dcf_engine", priv.__name__


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
