#!/usr/bin/env python3
"""fundamentals.py's ONE returns function (engine 5.7, Andrew 2026-10-19, R4 revised M2: "fix the measure at the
source"; design 03b §4.1-4.3). Run: python _system/tests/test_fundamentals_returns.py (or python -m pytest
_system/tests). No network, no company folders: inline companyfacts-shaped fixtures in the style of
test_fundamentals_debt.py, and fundamentals.main() run against a temporary folder with get_json stubbed.

F-1 roic equals the (kept) roic_proxy bit for bit on a stable invested capital; basis operating_income, no flags.
F-2 VRSN shape (negative equity, no debt tag): roic None with note unbounded_high, the flags, roe_note
    negative_equity while roe and roic_proxy keep their old (sign-meaningless) values.
F-3 the 5%-of-revenue stable-denominator rule: 3% -> unbounded_high / loss_on_unstable_capital; exactly 5% -> a ratio.
F-4 tangible ROIC: share of goodwill + intangibles, goodwill above IC -> unbounded_high, nothing filed -> equals roic.
F-5 the EBIT ladder: pretax + interest (EBIT_FALLBACK); no_ebit on a fundamentals row; the CSV rung (csv=True).
F-5b row_tax_rate is build_annual's 0-50%-else-21% rule, and roic_proxy is computed with it.
F-6 key order: every pre-existing key keeps its relative order; the thirteen new keys sit, contiguous, between
    share_issuance_tags and revenue_growth; roe / roa / roic_proxy unchanged.
F-7 the stable write: an old-shape fundamentals.json is rewritten once, then left alone.
F-9 the financial-assets share (NLY shape) the moat scorecard's SIC-6798 lock reads; neither group filed -> None.
(F-8, the scorecard reading the same numbers, is in test_moat_scorecard.py.)
Each test fails on the code before engine 5.7 (no capital_returns_from_row / row_tax_rate / new keys).
"""
import contextlib, copy, datetime, io, json, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import fundamentals as F  # noqa: E402

G = "us-gaap"
NEW_KEYS = ["nopat", "invested_capital", "invested_capital_tangible", "intangibles_share_ic", "roic", "roic_note",
            "roic_tangible", "roic_tangible_note", "roic_basis", "roic_flags", "roe_note",
            "financial_assets", "financial_assets_pct_assets"]
# the annual row's keys before engine 5.7 (07cb4af through e22e814: identical), in order
OLD_KEYS = ['period_end', 'fy', 'revenue', 'revenue_basis', 'cogs', 'gross_profit', 'gross_margin', 'rnd', 'sga',
            'rnd_pct_rev', 'sga_pct_rev', 'operating_income', 'operating_margin', 'interest_expense', 'pretax_income',
            'tax', 'net_income', 'net_margin', 'disc_ops', 'nonop', 'eps_diluted', 'eps_basic', 'shares_diluted',
            'shares_tag', 'shares_outstanding', 'ocf', 'icf', 'fincf', 'capex', 'capex_intangibles', 'sbc', 'da', 'fcf',
            'oe_conservative', 'ocf_margin', 'oe_margin', 'fcf_margin', 'capex_pct_rev', 'sbc_pct_rev', 'sbc_pct_ocf',
            'dividends_paid', 'buybacks', 'acquisitions', 'shareholder_yield_paid', 'cash', 'cash_basis',
            'restricted_cash', 'short_term_investments', 'receivables', 'inventory', 'prepaids', 'assets_current',
            'ppe_net', 'goodwill', 'intangibles', 'assets', 'liab_current', 'deferred_revenue', 'debt_current', 'debt_lt',
            'total_debt', 'debt_basis', 'net_debt', 'lease_liabilities', 'liabilities', 'equity', 'retained_earnings',
            'oe_per_share', 'fcf_per_share', 'ocf_per_share', 'revenue_per_share', 'book_value_per_share', 'roe', 'roa',
            'roic_proxy', 'net_debt_to_oe', 'goodwill_pct_assets', 'prepaids_pct_assets', 'current_ratio',
            'dps_declared', 'dps_paid', 'share_issuance', 'share_issuance_tags', 'revenue_growth',
            'gross_profit_growth', 'operating_income_growth', 'net_income_growth', 'eps_diluted_growth', 'ocf_growth',
            'oe_conservative_growth', 'fcf_growth', 'shares_diluted_growth', 'oe_per_share_growth']

DUR_TAG = {"revenue": "Revenues", "operating_income": "OperatingIncomeLoss", "net_income": "NetIncomeLoss",
           "pretax_income": "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
           "tax": "IncomeTaxExpenseBenefit", "interest_expense": "InterestExpense",
           "ocf": "NetCashProvidedByUsedInOperatingActivities", "capex": "PaymentsToAcquirePropertyPlantAndEquipment"}
INST_TAG = {"equity": "StockholdersEquity", "debt_lt": "LongTermDebtNoncurrent", "cash": "CashAndCashEquivalentsAtCarryingValue",
            "goodwill": "Goodwill", "intangibles": "IntangibleAssetsNetExcludingGoodwill", "assets": "Assets",
            "liabilities": "Liabilities", "loans": "LoansAndLeasesReceivableNetReportedAmount",
            "afs_debt": "AvailableForSaleSecuritiesDebtSecurities"}


def facts_for(years):
    """companyfacts-shaped dict from {year: {field: value}} (FY = calendar year, 10-K filed the next February)."""
    out = {"facts": {G: {}}}
    for y, vals in years.items():
        end, start, filed = f"{y}-12-31", f"{y}-01-01", f"{y + 1}-02-15"
        for k, v in vals.items():
            if v is None:
                continue
            if k in DUR_TAG:
                e = {"start": start, "end": end, "val": v, "form": "10-K", "fp": "FY", "fy": y, "filed": filed, "accn": f"K{y}"}
                tag = DUR_TAG[k]
            else:
                e = {"end": end, "val": v, "form": "10-K", "fp": "FY", "fy": y, "filed": filed, "accn": f"K{y}"}
                tag = INST_TAG[k]
            out["facts"][G].setdefault(tag, {"units": {"USD": []}})["units"]["USD"].append(e)
    return out


def row_of(facts, year):
    rows, _, _ = F.build_annual(facts)
    return next(r for r in rows if r["period_end"] == f"{year}-12-31")


BASE_YEAR = {"revenue": 1000e6, "operating_income": 200e6, "net_income": 152e6, "pretax_income": 190e6, "tax": 38e6,
             "equity": 300e6, "debt_lt": 150e6, "cash": 50e6, "assets": 900e6}


def test_roic_matches_proxy_on_stable_capital():
    r = row_of(facts_for({2025: BASE_YEAR}), 2025)
    assert r["invested_capital"] == 400e6 and r["invested_capital"] == 0.40 * r["revenue"]
    assert r["roic"] == r["roic_proxy"], (r["roic"], r["roic_proxy"])   # bit for bit
    assert r["roic"] == 200e6 * (1 - 38 / 190) / 400e6
    assert r["roic_basis"] == "operating_income" and r["roic_flags"] == [] and r["roe_note"] is None and r["roic_note"] is None
    assert r["nopat"] == 200e6 * (1 - 38 / 190)
    # neither goodwill nor intangibles filed: tangible == roic, with the note
    assert r["roic_tangible"] == r["roic"] and r["roic_tangible_note"] == "goodwill_intangibles_not_filed"
    assert r["intangibles_share_ic"] == 0.0


def test_vrsn_shape_unbounded_high():
    y = {"revenue": 1.6e9, "operating_income": 1.121e9, "net_income": 0.8e9, "pretax_income": 1.04e9, "tax": 0.24e9,
         "equity": -2.154e9, "cash": 0.308e9, "assets": 1.7e9}
    r = row_of(facts_for({2025: y}), 2025)
    assert r["roic"] is None and r["roic_note"] == "unbounded_high", (r["roic"], r["roic_note"])
    assert {"NONPOSITIVE_INVESTED_CAPITAL", "DEBT_NOT_TAGGED", "NEGATIVE_EQUITY"} <= set(r["roic_flags"]), r["roic_flags"]
    assert r["roe_note"] == "negative_equity"
    assert r["roe"] == 0.8e9 / -2.154e9, "roe keeps its old (sign-meaningless) value for compatibility"
    t = 0.24e9 / 1.04e9
    assert r["roic_proxy"] == 1.121e9 * (1 - t) / (-2.154e9 - 0.308e9) and r["roic_proxy"] < 0, "roic_proxy is kept"
    assert r["invested_capital"] == -2.154e9 - 0.308e9 and r["intangibles_share_ic"] is None


def test_unstable_denominator():
    # revenue 1,000M; invested capital 30M = 3% of revenue
    y = dict(BASE_YEAR, equity=30e6, debt_lt=None, cash=None)
    r = row_of(facts_for({2025: y}), 2025)
    assert r["roic"] is None and r["roic_note"] == "unbounded_high" and "ROIC_DENOMINATOR_UNSTABLE" in r["roic_flags"], r
    r = row_of(facts_for({2025: dict(y, operating_income=-50e6)}), 2025)
    assert r["roic"] is None and r["roic_note"] == "loss_on_unstable_capital" and "ROIC_DENOMINATOR_UNSTABLE" in r["roic_flags"]
    # exactly 5% of revenue is a stable denominator: a ratio
    r = row_of(facts_for({2025: dict(y, equity=50e6)}), 2025)
    assert r["roic"] == 200e6 * (1 - 38 / 190) / 50e6 and r["roic_note"] is None
    assert "ROIC_DENOMINATOR_UNSTABLE" not in r["roic_flags"]
    # non-positive capital with a loss
    r = row_of(facts_for({2025: dict(y, equity=-10e6, operating_income=-50e6)}), 2025)
    assert r["roic"] is None and r["roic_note"] == "loss_on_nonpositive_capital" and "NONPOSITIVE_INVESTED_CAPITAL" in r["roic_flags"]


def test_tangible_roic():
    # goodwill + intangibles 240M = 60% of IC 400M
    r = row_of(facts_for({2025: dict(BASE_YEAR, goodwill=200e6, intangibles=40e6)}), 2025)
    nopat = 200e6 * (1 - 38 / 190)
    assert r["intangibles_share_ic"] == 0.60 and r["invested_capital_tangible"] == 160e6
    assert r["roic_tangible"] == nopat / 160e6 and r["roic_tangible_note"] is None and r["roic"] == nopat / 400e6
    # goodwill above invested capital: profit on non-positive tangible capital
    r = row_of(facts_for({2025: dict(BASE_YEAR, goodwill=500e6)}), 2025)
    assert r["roic_tangible"] is None and r["roic_tangible_note"] == "unbounded_high"
    assert "NONPOSITIVE_TANGIBLE_CAPITAL" in r["roic_flags"] and r["intangibles_share_ic"] == 1.25
    # tangible capital positive but under 5% of revenue
    r = row_of(facts_for({2025: dict(BASE_YEAR, goodwill=370e6)}), 2025)
    assert r["roic_tangible"] is None and "TANGIBLE_DENOMINATOR_UNSTABLE" in r["roic_flags"]
    # goodwill and intangibles both filed as zero: tangible == roic, no note
    r = row_of(facts_for({2025: dict(BASE_YEAR, goodwill=0, intangibles=0)}), 2025)
    assert r["roic_tangible"] == r["roic"] and r["roic_tangible_note"] is None


def test_ebit_fallback():
    y = dict(BASE_YEAR, operating_income=None, interest_expense=12e6)
    r = row_of(facts_for({2025: y}), 2025)
    assert r["roic_basis"] == "pretax_income_plus_interest" and "EBIT_FALLBACK" in r["roic_flags"]
    assert r["roic"] == (190e6 + 12e6) * (1 - 38 / 190) / 400e6
    assert r["roic_proxy"] is None, "the proxy needs operating income, as before"
    # neither operating income nor pretax income, net income and tax filed: no_ebit on a fundamentals row ...
    y2 = dict(BASE_YEAR, operating_income=None, pretax_income=None)
    r = row_of(facts_for({2025: y2}), 2025)
    assert r["roic"] is None and r["roic_note"] == "no_ebit" and r["roic_basis"] is None and r["nopat"] is None
    # ... and the CSV rung on the same raw fields (financials_history.csv has no pretax line)
    raw = {k: r[k] for k in ("revenue", "operating_income", "pretax_income", "interest_expense", "tax", "net_income",
                             "equity", "total_debt", "cash", "goodwill", "intangibles")}
    c = F.capital_returns_from_row(raw, csv=True)
    t = 38e6 / (152e6 + 38e6)
    assert c["roic_basis"] == "net_income_plus_tax" and "EBIT_FALLBACK" in c["roic_flags"]
    assert c["roic"] == (152e6 + 38e6) * (1 - t) / 400e6
    # no equity: no_equity, but EBIT and NOPAT are still computed
    c = F.capital_returns_from_row(dict(raw, operating_income=200e6, equity=None))
    assert c["roic_note"] == "no_equity" and c["roe_note"] == "no_equity" and c["nopat"] is not None and c["invested_capital"] is None
    # the scorecard's add-back keyword (acquired IPR&D, Q3 default) moves EBIT only; the tax rate stays the row's
    base = F.capital_returns_from_row(dict(raw, operating_income=200e6, pretax_income=190e6))
    plus = F.capital_returns_from_row(dict(raw, operating_income=200e6, pretax_income=190e6), ebit_addback=50e6)
    assert plus["nopat"] == (200e6 + 50e6) * (1 - 38 / 190) and base["nopat"] == 200e6 * (1 - 38 / 190)


def test_row_tax_rate_is_build_annuals_rule():
    assert F.row_tax_rate(0, 10) == 0.21 and F.row_tax_rate(-5, 1) == 0.21 and F.row_tax_rate(None, 1) == 0.21
    assert F.row_tax_rate(100, -3) == 0.21 and F.row_tax_rate(100, 51) == 0.21 and F.row_tax_rate(100, None) == 0.21
    assert F.row_tax_rate(100, 30) == 0.30 and F.row_tax_rate(100, 50) == 0.50 and F.row_tax_rate(100, 0) == 0.0
    years = {2023: dict(BASE_YEAR, tax=60e6), 2024: dict(BASE_YEAR, pretax_income=-5e6), 2025: BASE_YEAR}
    rows, _, _ = F.build_annual(facts_for(years))
    for r in rows:
        inv = r["equity"] + (r["total_debt"] or 0) - (r["cash"] or 0)
        assert r["roic_proxy"] == r["operating_income"] * (1 - F.row_tax_rate(r["pretax_income"], r["tax"])) / inv, r["period_end"]


def test_key_order_and_unchanged_fields():
    years = {2023: dict(BASE_YEAR, goodwill=100e6), 2024: dict(BASE_YEAR, revenue=1100e6), 2025: BASE_YEAR}
    rows, _, _ = F.build_annual(facts_for(years))
    for r in rows:
        keys = list(r)
        it = iter(keys)
        assert all(k in it for k in OLD_KEYS), "the pre-5.7 keys keep their relative order"
        i = keys.index("share_issuance_tags")
        assert keys[i + 1:i + 1 + len(NEW_KEYS)] == NEW_KEYS, keys[i + 1:i + 1 + len(NEW_KEYS)]
        assert keys[i + 1 + len(NEW_KEYS)] == "revenue_growth"
        assert set(keys) == set(OLD_KEYS) | set(NEW_KEYS)
        inv = r["equity"] + (r["total_debt"] or 0) - (r["cash"] or 0)
        assert r["roe"] == r["net_income"] / r["equity"] and r["roa"] == r["net_income"] / r["assets"]
        assert r["roic_proxy"] == r["operating_income"] * (1 - 38 / 190) / inv


def _run_main(base, facts, today):
    saved = (F.BASE, F.get_json, F.ET_TODAY, list(sys.argv))

    def fake_get_json(url, timeout=90):
        if "companyfacts" in url:
            return facts
        if "submissions" in url:
            return {"sic": "3490", "sicDescription": "Misc fabricated metal", "fiscalYearEnd": "1231", "filings": {"recent": {}}}
        raise AssertionError(f"unexpected fetch {url}")
    try:
        F.BASE, F.get_json, F.ET_TODAY = base, fake_get_json, today
        sys.argv = ["fundamentals.py", "ZZRET", "--cik", "1"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            F.main()
        return json.loads(buf.getvalue())
    finally:
        F.BASE, F.get_json, F.ET_TODAY = saved[0], saved[1], saved[2]
        sys.argv[:] = saved[3]


def test_stable_rewrite_once():
    base = tempfile.mkdtemp(prefix="fund_returns_")
    try:
        facts = facts_for({2024: BASE_YEAR, 2025: dict(BASE_YEAR, revenue=1100e6)})
        path = os.path.join(base, "ZZRET", "fundamentals.json")
        os.makedirs(os.path.dirname(path))
        assert _run_main(base, facts, datetime.date(2026, 10, 20))["fundamentals_json"] == "written"
        # an old-shape file (written before engine 5.7): the same content without the thirteen keys
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        old = copy.deepcopy(doc)
        for r in old["annual"]:
            for k in NEW_KEYS:
                r.pop(k, None)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(old, f, indent=1)
        assert _run_main(base, facts, datetime.date(2026, 10, 21))["fundamentals_json"] == "written", "rewritten once"
        with open(path, encoding="utf-8") as f:
            new = json.load(f)
        assert all(all(k in r for k in NEW_KEYS) for r in new["annual"])
        assert _run_main(base, facts, datetime.date(2026, 10, 22))["fundamentals_json"] == "unchanged", "and never again"
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_financial_assets_share():
    nly = dict(BASE_YEAR, assets=135.6e9, afs_debt=70e9, loans=2e9, liabilities=119.5e9)
    r = row_of(facts_for({2025: nly}), 2025)
    assert r["financial_assets"] == 72e9 and round(r["financial_assets_pct_assets"], 3) == 0.531
    # an equity REIT that files neither group
    r = row_of(facts_for({2025: dict(BASE_YEAR, assets=10e9)}), 2025)
    assert r["financial_assets"] is None and r["financial_assets_pct_assets"] is None
    # one group alone counts; no assets -> no share
    assert F.financial_assets_from_row(None, 5.0, None) == (5.0, None)
    assert F.financial_assets_from_row(3.0, None, 6.0) == (3.0, 0.5)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                import traceback
                traceback.print_exc()
                print("FAIL", name, e)
    sys.exit(1 if fails else 0)
