#!/usr/bin/env python3
"""One currency per fundamentals.json (ruling-sheet Q8 bug 3, Andrew 2026-10-19).
Run: python _system/tests/test_fundamentals_currency.py (or python -m pytest _system/tests).
No network, no company folders: inline companyfacts-shaped fixtures shaped like
RDY (PR #30) and fundamentals.main() run against a temporary folder with
get_json stubbed.

RDY files every fiscal year in INR (three years per 20-F) and, in each 20-F,
the latest year's USD convenience translation too. The readers preferred USD
per period, so FY2017 revenue was Rs140.809B and FY2018 the $2.181B
translation (statements.json: Rs142.028B) — revenue growth -98.45% — and the
INR dividend per share (Rs40) was divided by the USD price ($12.87): a
310.80% dividend yield (SKM: KRW 3,540 over $31.96, 11,076%).

1. money_unit: the ONE money unit of the file — the currency the newest
   annual filing files most of its core FY facts (revenue, net income, OCF,
   assets) in, the all-filing count then USD breaking a tie (RTO moved from
   GBP to USD) — the rule statements.money_unit applies to statements.json.
2. build_annual / build_quarterly / the DPS and flow readers read money facts
   in that unit only (per-share facts in <unit>/shares); a convenience
   translation never enters a series.
3. The price is USD: a yield is a price-based ratio, so a block whose
   numerators are in another currency carries no yields (null, with the
   reason in yields_display), at build time and when build_site.py reprices
   it (price_dividends(currency=...)); the market cap (USD price x shares) stays.
"""
import contextlib, datetime, io, json, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import fundamentals as F  # noqa: E402

IF = "ifrs-full"


def _facts(entries):
    out = {"facts": {}}
    for tax, tag, unit, e in entries:
        out["facts"].setdefault(tax, {}).setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    return out


def _fy(tag, end, val, unit, filed, tax=IF):
    """An FY-duration fact (fiscal year ending March 31, RDY's) on a 20-F."""
    start = f"{int(end[:4]) - 1}-04-01"
    return (tax, tag, unit, {"start": start, "end": end, "val": val, "form": "20-F", "fp": "FY", "filed": filed, "accn": "F" + filed})


def _inst(tag, end, val, unit, filed, tax=IF):
    return (tax, tag, unit, {"end": end, "val": val, "form": "20-F", "fp": "FY", "filed": filed, "accn": "F" + filed})


def rdy_facts():
    """FY2017 (filed in the 2017 20-F, INR only) and FY2018 (the 2018 20-F: INR + the latest year's USD translation)."""
    e = []
    for tag, v17, v18, usd18 in (("Revenue", 140_809e6, 142_028e6, 2_181e6), ("ProfitLoss", 12_900e6, 9_500e6, 146e6),
                                 ("CashFlowsFromUsedInOperatingActivities", 20_000e6, 21_000e6, 322e6)):
        e += [_fy(tag, "2017-03-31", v17, "INR", "2017-07-01"), _fy(tag, "2017-03-31", v17, "INR", "2018-07-01"),
              _fy(tag, "2018-03-31", v18, "INR", "2018-07-01"), _fy(tag, "2018-03-31", usd18, "USD", "2018-07-01")]
    e += [_inst("Assets", "2017-03-31", 180_000e6, "INR", "2017-07-01"), _inst("Assets", "2018-03-31", 190_000e6, "INR", "2018-07-01"),
          _inst("Assets", "2018-03-31", 2_917e6, "USD", "2018-07-01")]
    # DPS: INR per share on every year, the USD translation on the latest
    e += [_fy("DividendsRecognisedAsDistributionsToOwnersPerShare", "2017-03-31", 20.0, "INR/shares", "2017-07-01"),
          _fy("DividendsRecognisedAsDistributionsToOwnersPerShare", "2018-03-31", 20.0, "INR/shares", "2018-07-01"),
          _fy("DividendsRecognisedAsDistributionsToOwnersPerShare", "2018-03-31", 0.31, "USD/shares", "2018-07-01")]
    return _facts(e)


def test_money_unit_is_the_unit_of_most_core_facts():
    assert F.money_unit(rdy_facts()) == "INR"
    assert F.money_unit({"facts": {}}) == "USD"
    usd = _facts([_fy("Revenue", "2018-03-31", 5e9, "USD", "2018-07-01"), _fy("Revenue", "2017-03-31", 4e9, "USD", "2018-07-01"),
                  _fy("Revenue", "2018-03-31", 35e9, "CNY", "2018-07-01")])
    assert F.money_unit(usd) == "USD"
    tie = _facts([_fy("Revenue", "2018-03-31", 5e9, "USD", "2018-07-01"), _fy("Revenue", "2018-03-31", 35e9, "CNY", "2018-07-01")])
    assert F.money_unit(tie) == "USD", "USD on a tie"


def _fyc(tag, end, val, unit, filed):
    """An FY-duration fact on a calendar fiscal year (RTO's) on a 20-F."""
    return (IF, tag, unit, {"start": f"{end[:4]}-01-01", "end": end, "val": val, "form": "20-F", "fp": "FY", "filed": filed, "accn": "F" + filed})


def rto_facts():
    """RTO's shape (verifier round 1): GBP presentation through the 20-F filed 2025-03-26, every GBP year re-filed in three
    20-Fs (so GBP holds most core FY facts); the 20-F filed 2026-03-25 moves to USD and files FY2023-FY2025 in USD only
    (restated), no GBP figure for FY2025."""
    e = []
    gbp = {"Revenue": {2020: 2_840e6, 2021: 2_953e6, 2022: 3_714e6, 2023: 5_375e6, 2024: 5_436e6},
           "ProfitLoss": {2020: 43e6, 2021: 263e6, 2022: 284e6, 2023: 314e6, 2024: 299e6},
           "CashFlowsFromUsedInOperatingActivities": {2020: 650e6, 2021: 600e6, 2022: 640e6, 2023: 900e6, 2024: 830e6}}
    for tag, by in gbp.items():
        for y, v in by.items():
            for filed_y in (y + 1, y + 2, y + 3):
                if filed_y <= 2025:
                    e.append(_fyc(tag, f"{y}-12-31", v, "GBP", f"{filed_y}-03-26"))
    usd = {"Revenue": {2023: 6_714e6, 2024: 6_964e6, 2025: 6_908e6}, "ProfitLoss": {2023: 474e6, 2024: 392e6, 2025: 470e6},
           "CashFlowsFromUsedInOperatingActivities": {2023: 1_120e6, 2024: 1_060e6, 2025: 1_164e6}}
    for tag, by in usd.items():
        for y, v in by.items():
            e.append(_fyc(tag, f"{y}-12-31", v, "USD", "2026-03-25"))
    return _facts(e)


def test_money_unit_follows_a_presentation_currency_change():
    """Verifier round 1 (RTO): the money unit is the newest annual filing's currency, not the all-time majority — GBP holds
    more core FY facts (each year re-filed three times) but the newest 20-F is USD-only, so the file is USD and keeps FY2025.
    The old majority rule picked GBP, ended the table at FY2024 on the superseded GBP figures and called USD a
    'convenience translation'. statements.money_unit applies the same rule, so the two files agree."""
    facts = rto_facts()
    assert F.money_counts(facts)["GBP"] > F.money_counts(facts)["USD"], "the fixture's GBP history outnumbers its USD facts"
    assert F.money_unit(facts) == "USD", F.money_unit(facts)
    rows, _, currency = F.build_annual(facts)
    assert currency == [] and rows[-1]["period_end"] == "2025-12-31" and rows[-1]["revenue"] == 6_908e6, (currency, rows[-1])
    by = {r["period_end"]: r for r in rows}
    assert by["2024-12-31"]["revenue"] == 6_964e6, "FY2024 is the restated USD figure, not the superseded GBP one"
    assert "2022-12-31" not in by, "a former presentation currency's years are not read beside the USD ones"
    w = F.money_unit_warning(F.pick_money_unit(F.money_entries(facts)))
    assert w and "GBP" in w and "former presentation currency" in w and "convenience" not in w, w
    import statements as S
    warnings = []
    assert S.money_unit(facts, warnings) == "USD", warnings
    assert warnings and "former presentation currency" in warnings[0] and "convenience" not in warnings[0], warnings
    # a convenience translation in the newest filing still loses to the reporting currency (RDY), and a tie is still USD
    pick = F.pick_money_unit(F.money_entries(rdy_facts()))
    assert pick["unit"] == "INR" and pick["translations"] == ["USD"] and pick["earlier"] == [], pick
    assert F.pick_money_unit(F.money_entries(facts))["former"] == ["GBP"]
    # a currency that is a minority in EVERY filing, and only in older ones, is an old convenience translation, not a former
    # presentation currency (VOD: EUR filings whose older 20-Fs also carried USD translations)
    vod = rdy_facts()
    vod["facts"][IF]["Revenue"]["units"]["INR"].append({"start": "2018-04-01", "end": "2019-03-31", "val": 153_000e6, "form": "20-F", "fp": "FY",
                                                         "filed": "2019-07-01", "accn": "F2019-07-01"})
    p2 = F.pick_money_unit(F.money_entries(vod))
    assert p2["unit"] == "INR" and p2["earlier_translations"] == ["USD"] and p2["former"] == [], p2
    w2 = F.money_unit_warning(p2)
    assert "convenience translations of earlier filings" in w2 and "former presentation currency" not in w2, w2
    warnings = []
    assert S.money_unit(rdy_facts(), warnings) == "INR" and "convenience translations" in warnings[0], warnings


def test_annual_series_never_mixes_a_convenience_translation_into_the_reporting_currency():
    rows, _, currency = F.build_annual(rdy_facts())
    by = {r["period_end"]: r for r in rows}
    assert currency == ["INR"], currency
    assert by["2018-03-31"]["revenue"] == 142_028e6, by["2018-03-31"]["revenue"]
    g = by["2018-03-31"]["revenue_growth"]
    assert g is not None and round(g * 100, 2) == 0.87, g  # Rs140.809B -> Rs142.028B, not -98.45%
    assert by["2018-03-31"]["ocf"] == 21_000e6 and by["2018-03-31"]["net_income"] == 9_500e6
    # the explicit unit= reader is unchanged (JD's short-term borrowings read in the total's unit)
    assert F.annual_series(rdy_facts(), [(IF, "Revenue")], True, unit="USD")[0] == {"2018-03-31": 2_181e6}


def test_dps_series_is_read_in_the_reporting_currency():
    dps_q, dps_fy, _ = F.dividends_inputs(rdy_facts(), money="INR")
    paid = dps_fy["paid"] or dps_fy["declared"]
    assert paid.get("2018-03-31") == 20.0, (dps_fy, "the USD/shares translation 0.31 is not the FY2018 DPS")
    assert F.duration_facts(rdy_facts(), [(IF, "Revenue")], money="INR")[("2017-04-01", "2018-03-31")][2] == "INR"


def _block(currency, price=12.87):
    annual = [{"fy": "2018", "period_end": "2018-03-31", "eps_diluted": 57.0, "dividends_paid": 3_400e6, "buybacks": None, "share_issuance": None,
               "oe_conservative": 15_000e6, "fcf": 16_000e6, "shares_diluted": 166e6}]
    ctx = {"filed_any": {"dividends_paid": True, "buybacks": False, "share_issuance": False}, "shares_instant": (166e6, "2018-03-31", "ifrs-full:NumberOfSharesOutstanding"),
           "latest_filed_period": {}, "split_notes": [], "splits": [], "warnings": [], "currency": currency}
    return F.build_dividends(annual, [], {"declared": {}, "paid": {}}, {"declared": {}, "paid": {"2017-03-31": 20.0, "2018-03-31": 40.0}},
                             price, "2026-10-19", "prices.json stats.last", ctx)


def test_yields_need_the_numerator_in_the_price_currency():
    d = _block("INR")
    assert d["dps_ttm"] == 40.0, d["dps_ttm"]
    assert d["dividend_yield"] is None and d["shareholder_yield"] is None and d["buyback_yield"] is None and d["net_buyback_yield"] is None, d
    assert d["market_cap"] is not None and round(d["market_cap"]) == round(12.87 * 166e6), "the USD market cap is still shown"
    assert all(v["label"] == "—" for v in d["yields_display"].values())
    note = d["yields_display"]["dividend_yield"]["note"]
    assert note and "INR" in note and "USD" in note, note
    assert any("INR" in n and "yield" in n for n in d["notes"]), d["notes"]
    # USD numerators: unchanged
    u = _block("USD", price=1300.0)
    assert u["dividend_yield"] is not None and round(u["dividend_yield"] * 100, 4) == round(40 / 1300 * 100, 4)
    # build_site.py reprices a committed block with the file's currency: a pre-fix INR block loses its yields too
    old = dict(_block("USD"), dividend_yield=3.108)
    rp = F.price_dividends(old, 13.10, "2026-10-20", F.PRICES_JSON_SOURCE, currency="INR")
    assert rp["dividend_yield"] is None and rp["shareholder_yield"] is None and rp["market_cap"] is not None
    assert F.price_dividends(old, 13.10, "2026-10-20", F.PRICES_JSON_SOURCE)["dividend_yield"] is not None, "no currency given: USD (every pre-existing caller)"
    # repricing is still idempotent with the build: build at P == reprice(build at Q, P)
    assert F.price_dividends(_block("INR", price=9.0), 12.87, "2026-10-19", "prices.json stats.last", currency="INR") == d


def test_main_writes_one_currency_and_no_cross_currency_yield():
    base = tempfile.mkdtemp(prefix="fund_ccy_")
    saved = (F.BASE, F.get_json, F.ET_TODAY, list(sys.argv))
    try:
        os.makedirs(os.path.join(base, "ZZINR"))
        with open(os.path.join(base, "ZZINR", "score.json"), "w", encoding="utf-8") as f:
            json.dump({"price": 12.87, "as_of": "2026-10-19"}, f)
        facts = rdy_facts()

        def fake_get_json(url, timeout=90):
            if "companyfacts" in url:
                return facts
            return {"fiscalYearEnd": "0331", "filings": {"recent": {}}}
        F.BASE, F.get_json, F.ET_TODAY = base, fake_get_json, datetime.date(2026, 10, 19)
        sys.argv = ["fundamentals.py", "ZZINR", "--cik", "1"]
        with contextlib.redirect_stdout(io.StringIO()):
            F.main()
        with open(os.path.join(base, "ZZINR", "fundamentals.json"), encoding="utf-8") as f:
            doc = json.load(f)
        assert doc["currency"] == "INR"
        r18 = next(r for r in doc["annual"] if r["period_end"] == "2018-03-31")
        assert r18["revenue"] == 142_028e6 and round(r18["revenue_growth"] * 100, 2) == 0.87
        assert doc["dividends"]["dividend_yield"] is None, doc["dividends"]["dividend_yield"]
        assert any("INR" in w and "convenience" in w for w in doc["warnings"]), doc["warnings"]
    finally:
        F.BASE, F.get_json, F.ET_TODAY = saved[0], saved[1], saved[2]
        sys.argv[:] = saved[3]
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:  # a crash is a failure too
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
