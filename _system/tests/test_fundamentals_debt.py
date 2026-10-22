#!/usr/bin/env python3
"""Total-debt basis and the stable fundamentals.json write (Codex review of PR #2).
Run: python _system/tests/test_fundamentals_debt.py (or python -m pytest _system/tests).
No network, no company folders: inline companyfacts-shaped fixtures shaped like
the filers the reviewer and the survey used (HBAN, CPNG, JD, KVUE, SMCI), and
fundamentals.main() run against a temporary folder with get_json stubbed.

1. A LONG-TERM total tag (LongTermDebt, LongTermDebtAndCapitalLeaseObligations-
   IncludingCurrentMaturities) carries current maturities but not short-term
   borrowings filed on their own line: those are added (HBAN FY2025 17.221B ->
   18.482B, the statements pipeline's figure), the current maturities never are.
2. An aggregate of long- and short-term debt (DebtLongtermAndShorttermCombinedAmount,
   IFRS Borrowings) stands alone.
3. Never across currencies: a short-term line filed in another unit is read in
   the total's unit, else left out and named.
4. dcf_engine.debt_from_total_tag applies the same rule (diagnostics only).
5. fundamentals.json is rewritten only when its content apart from `as_of` changed.
6. (repair round) ... and not when the only other change is an old 8-K ageing out
   of the 12-month window (the count is compared as of the file's own as_of), nor
   on a fresh clone without the gitignored prices.json (the committed close is
   carried instead of falling back to score.json's older analysis price).
7. (2026-10-16) Price-free file: _stable's `*` paths (every key of an object,
   every item of a list); a new close alone — or a price that moves from
   prices.json to score.json and back — never rewrites the file (the price
   leaves are volatile), a filing change writes it at the run's close; every
   text-mode open() in fundamentals.py names utf-8.
"""
import ast, contextlib, io, json, os, shutil, sys, tempfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import fundamentals as F  # noqa: E402
import dcf_engine as E  # noqa: E402
import _stable as S  # noqa: E402

G = "us-gaap"
IF = "ifrs-full"


def _facts(entries):
    """companyfacts-shaped dict from [(taxonomy, tag, unit, fact)]."""
    out = {"facts": {}}
    for tax, tag, unit, e in entries:
        out["facts"].setdefault(tax, {}).setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)
    return out


def _inst(tag, end, val, unit="USD", filed=None, tax=G):
    """An instant balance-sheet fact from a 10-K."""
    return (tax, tag, unit, {"end": end, "val": val, "form": "10-K", "fp": "FY", "filed": filed or f"{int(end[:4]) + 1}-02-15", "accn": "K" + end})


def _ni(end, val, unit="USD"):
    start = f"{end[:4]}-01-01"
    return (G, "NetIncomeLoss", unit, {"start": start, "end": end, "val": val, "form": "10-K", "fp": "FY", "filed": f"{int(end[:4]) + 1}-02-15", "accn": "K" + end})


def _row(facts, end):
    rows, _, _ = F.build_annual(facts)
    return next(r for r in rows if r["period_end"] == end)


# ---------------- 1. long-term total + short-term borrowings ----------------
def test_hban_long_term_debt_plus_short_term_borrowings():
    # HBAN FY2025 (unclassified bank balance sheet): LongTermDebt 17,221M, ShortTermBorrowings 1,261M, cash 13,495M
    facts = _facts([_ni("2025-12-31", 2.2e9), _inst("LongTermDebt", "2025-12-31", 17221e6), _inst("ShortTermBorrowings", "2025-12-31", 1261e6),
                    _inst("CashAndCashEquivalentsAtCarryingValue", "2025-12-31", 13495e6)])
    r = _row(facts, "2025-12-31")
    assert r["total_debt"] == 18482e6, f"17.221B + 1.261B = 18.482B (statements.json total_debt), got {r['total_debt']}"
    assert r["net_debt"] == 18482e6 - 13495e6 and r["debt_current"] == 1261e6 and r["debt_lt"] is None
    assert r["debt_basis"] == "total tag (LongTermDebt, long-term incl. current maturities) + short-term borrowings (ShortTermBorrowings)"


def test_current_maturities_are_never_added_to_a_long_term_total():
    # CPNG FY2024: LongTermDebt 988M (current maturities 66M inside it) + ShortTermBorrowings 479M = 1,467M, not 1,533M
    facts = _facts([_ni("2024-12-31", 1.4e8), _inst("LongTermDebt", "2024-12-31", 988e6), _inst("LongTermDebtCurrent", "2024-12-31", 66e6),
                    _inst("ShortTermBorrowings", "2024-12-31", 479e6)])
    r = _row(facts, "2024-12-31")
    assert r["total_debt"] == 1467e6 and r["debt_current"] == 545e6, "debt_current still reports both current lines; the total adds the short-term part only"
    # commercial paper is short-term borrowing too (KVUE FY2023: LongTermDebt 7,687M + CommercialPaper 600M)
    facts = _facts([_ni("2023-12-31", 1.6e9), _inst("LongTermDebt", "2023-12-31", 7687e6), _inst("CommercialPaper", "2023-12-31", 600e6)])
    assert _row(facts, "2023-12-31")["total_debt"] == 8287e6


def test_long_term_total_without_short_term_borrowings_is_unchanged():
    facts = _facts([_ni("2025-12-31", 1e8), _inst("LongTermDebt", "2025-12-31", 9794e6)])
    r = _row(facts, "2025-12-31")
    assert r["total_debt"] == 9794e6 and "no short-term borrowings filed" in r["debt_basis"]
    # an aggregate DebtCurrent with no separately filed short-term part cannot be split: nothing is guessed, the basis says so
    facts = _facts([_ni("2025-12-31", 1e8), _inst("LongTermDebt", "2025-12-31", 9794e6), _inst("DebtCurrent", "2025-12-31", 500e6)])
    r = _row(facts, "2025-12-31")
    assert r["total_debt"] == 9794e6 and "DebtCurrent has no separately filed short-term part" in r["debt_basis"]


def test_noncurrent_path_is_untouched():
    facts = _facts([_ni("2025-12-31", 1e8), _inst("LongTermDebtNoncurrent", "2025-12-31", 900e6), _inst("LongTermDebtCurrent", "2025-12-31", 100e6),
                    _inst("ShortTermBorrowings", "2025-12-31", 50e6), _inst("LongTermDebt", "2025-12-31", 1000e6)])
    r = _row(facts, "2025-12-31")
    assert r["total_debt"] == 1050e6 and r["debt_basis"] == "noncurrent+current"


# ---------------- 2. aggregates stand alone ----------------
def test_aggregate_of_long_and_short_term_debt_stands_alone():
    # KVUE FY2024: DebtLongtermAndShorttermCombinedAmount 8,607M already holds the 800M of commercial paper
    facts = _facts([_ni("2024-12-31", 1e9), _inst("DebtLongtermAndShorttermCombinedAmount", "2024-12-31", 8607e6), _inst("CommercialPaper", "2024-12-31", 800e6)])
    r = _row(facts, "2024-12-31")
    assert r["total_debt"] == 8607e6 and r["debt_basis"] == "total tag (DebtLongtermAndShorttermCombinedAmount, includes short-term debt)"
    # IFRS Borrowings = current + non-current borrowings
    facts = _facts([_ni("2024-12-31", 1e9), _inst("Borrowings", "2024-12-31", 5e9, tax="ifrs-full"), _inst("ShorttermBorrowings", "2024-12-31", 1e9, tax="ifrs-full")])
    assert _row(facts, "2024-12-31")["total_debt"] == 5e9


# ---------------- 3. never across currencies ----------------
def test_short_term_borrowings_are_read_in_the_totals_unit():
    # JD FY2025: LongTermDebt in RMB only; ShortTermBorrowings filed in RMB AND as a USD convenience translation (USD wins the
    # unit preference) — the RMB figure is the one added (49,689M RMB, statements.json's total)
    facts = _facts([_ni("2025-12-31", 4e10, "CNY"), _inst("LongTermDebt", "2025-12-31", 41675e6, "CNY"),
                    _inst("ShortTermBorrowings", "2025-12-31", 1146e6, "USD"), _inst("ShortTermBorrowings", "2025-12-31", 8014e6, "CNY")])
    r = _row(facts, "2025-12-31")
    assert r["total_debt"] == 49689e6, r["total_debt"]
    # filed only in USD: left out, never added to an RMB total, and named
    facts = _facts([_ni("2025-12-31", 4e10, "CNY"), _inst("LongTermDebt", "2025-12-31", 41675e6, "CNY"), _inst("ShortTermBorrowings", "2025-12-31", 1146e6, "USD")])
    r = _row(facts, "2025-12-31")
    assert r["total_debt"] == 41675e6 and "short-term borrowings filed only in USD — not added" in r["debt_basis"]


def test_annual_series_unit_filter():
    facts = _facts([_inst("ShortTermBorrowings", "2025-12-31", 1146e6, "USD"), _inst("ShortTermBorrowings", "2025-12-31", 8014e6, "CNY")])
    assert F.annual_series(facts, ["ShortTermBorrowings"], False)[0] == {"2025-12-31": 1146e6}, "USD preferred by default"
    v, t, u = F.annual_series(facts, ["ShortTermBorrowings"], False, unit="CNY")
    assert v == {"2025-12-31": 8014e6} and u == {"2025-12-31": "CNY"}
    assert F.annual_series(facts, ["ShortTermBorrowings"], False, unit="EUR")[0] == {}


# ---------------- 4. the engine applies the same rule ----------------
def test_engine_debt_from_total_tag_matches_fundamentals():
    cases = [  # (tot, tot_tag, st, st_tag, expected total)
        (17221e6, "LongTermDebt", 1261e6, "ShortTermBorrowings", 18482e6),                      # HBAN FY2025
        (648e6, "LongTermDebt", 960e6, "ShortTermBorrowings", 1608e6),                          # CPNG FY2025
        (7687e6, "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", 600e6, "CommercialPaper", 8287e6),
        (8607e6, "DebtLongtermAndShorttermCombinedAmount", 800e6, "CommercialPaper", 8607e6),   # KVUE FY2024: aggregate
        (5e9, "Borrowings", 1e9, "ShorttermBorrowings", 5e9),                                  # IFRS aggregate
        (9794e6, "LongTermDebt", None, None, 9794e6),                                           # nothing short-term filed
    ]
    for tot, tag, st, st_tag, want in cases:
        assert E.debt_from_total_tag(tot, tag, st, st_tag)[0] == want, (tag, st)
        assert F.debt_from_total_tag(tot, tag, st, st_tag)[0] == want, (tag, st)
    assert E.debt_from_total_tag(17221e6, "LongTermDebt", 1261e6, "ShortTermBorrowings") == (18482e6, "TOTAL:LongTermDebt+ShortTermBorrowings")
    assert E.debt_from_total_tag(9794e6, "LongTermDebt") == (9794e6, "TOTAL:LongTermDebt"), "the pre-fix tag string when nothing is added"
    assert E.debt_from_total_tag(8607e6, "DebtLongtermAndShorttermCombinedAmount", 800e6, "CommercialPaper") == (8607e6, "TOTAL:DebtLongtermAndShorttermCombinedAmount")
    v, tag = E.debt_from_total_tag(41675e6, "LongTermDebt", 1146e6, "ShortTermBorrowings", same_unit=False)
    assert v == 41675e6 and "another unit, not added" in tag, "an unconverted currency is never added"
    assert E.LT_DEBT_TOTAL_TAGS == F.LT_DEBT_TOTAL_TAGS


# ---------------- 5. fundamentals.json is rewritten only when its content changes ----------------
def _run_main(base, facts, today, sub_recent=None):
    """fundamentals.main() for ticker ZZDEBT under `base`, network stubbed; returns the printed summary.
    sub_recent = the submissions feed's filings.recent (default: empty)."""
    saved = (F.BASE, F.get_json, F.ET_TODAY, list(sys.argv))

    def fake_get_json(url, timeout=90):
        if "companyfacts" in url:
            return facts
        if "submissions" in url:
            return {"sic": "6022", "sicDescription": "State commercial banks", "fiscalYearEnd": "1231", "filings": {"recent": sub_recent or {}}}
        raise AssertionError(f"unexpected fetch {url}")
    try:
        F.BASE, F.get_json, F.ET_TODAY = base, fake_get_json, today
        sys.argv = ["fundamentals.py", "ZZDEBT", "--cik", "1"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            F.main()
        return json.loads(buf.getvalue())
    finally:
        F.BASE, F.get_json, F.ET_TODAY = saved[0], saved[1], saved[2]
        sys.argv[:] = saved[3]


def test_fundamentals_json_is_rewritten_only_when_its_content_changes():
    base = tempfile.mkdtemp(prefix="fund_stable_")
    try:
        facts = _facts([_ni("2025-12-31", 2.2e9), _inst("LongTermDebt", "2025-12-31", 17221e6), _inst("ShortTermBorrowings", "2025-12-31", 1261e6)])
        path = os.path.join(base, "ZZDEBT", "fundamentals.json")
        s1 = _run_main(base, facts, datetime.date(2026, 10, 15))
        assert s1["fundamentals_json"] == "written" and os.path.exists(path)
        text = open(path, encoding="utf-8").read()
        assert text.startswith('{\n "ticker": "ZZDEBT"'), "json.dump(indent=1) formatting kept"
        assert json.loads(text)["annual"][0]["total_debt"] == 18482e6
        os.utime(path, ns=(1_000_000_000_000_000_000, 1_000_000_000_000_000_000))  # an old mtime the second run must not touch
        s2 = _run_main(base, facts, datetime.date(2026, 10, 16))  # next day, same filings: only as_of differs
        assert s2["fundamentals_json"] == "unchanged"
        assert os.stat(path).st_mtime_ns == 1_000_000_000_000_000_000, "file left untouched"
        assert json.load(open(path, encoding="utf-8"))["as_of"] == "2026-10-15", "as_of = the day this content was produced"
        facts2 = _facts([_ni("2025-12-31", 2.2e9), _inst("LongTermDebt", "2025-12-31", 17221e6), _inst("ShortTermBorrowings", "2025-12-31", 1300e6)])
        s3 = _run_main(base, facts2, datetime.date(2026, 10, 17))  # a filing changed a figure
        d = json.load(open(path, encoding="utf-8"))
        assert s3["fundamentals_json"] == "written" and d["as_of"] == "2026-10-17" and d["annual"][0]["total_debt"] == 18521e6
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---------------- 6. no rewrite for a rolling 8-K window or a missing price cache ----------------
def _recent(rows):
    """submissions filings.recent from [(form, filingDate, reportDate)] (newest first, as EDGAR lists them)."""
    return {"form": [r[0] for r in rows], "filingDate": [r[1] for r in rows], "reportDate": [r[2] for r in rows],
            "accessionNumber": [f"{r[0]}-{r[1]}" for r in rows], "primaryDocument": ["d.htm"] * len(rows)}


# Q's shape: 8-Ks spread over the year, one of them filed 2025-10-17 (ages out of the window after 2026-10-17)
SUB_8K = _recent([("8-K", "2026-08-05", ""), ("10-Q", "2026-08-05", "2026-06-30"), ("8-K", "2026-05-06", ""),
                  ("8-K", "2026-02-11", ""), ("10-K", "2026-02-20", "2025-12-31"), ("8-K", "2025-11-05", ""),
                  ("8-K", "2025-10-17", ""), ("8-K", "2025-09-01", "")])


def test_eight_k_count_is_the_365_days_to_a_date():
    dates = [d for f, d in zip(SUB_8K["form"], SUB_8K["filingDate"]) if f == "8-K"]
    assert F.eight_k_count(dates, datetime.date(2026, 10, 15)) == 5, "2025-10-15..2026-10-15: the 2025-09-01 8-K is out"
    assert F.eight_k_count(dates, datetime.date(2026, 10, 17)) == 5, "both ends included"
    assert F.eight_k_count(dates, datetime.date(2026, 10, 20)) == 4, "2025-10-17 has aged out"
    assert F.eight_k_count(dates, datetime.date(2026, 3, 1)) == 4, "a window ending before later 8-Ks does not count them"
    assert F.eight_k_count([None, "", "2026-01-01"], datetime.date(2026, 6, 1)) == 1


def test_an_8k_ageing_out_of_the_window_does_not_rewrite_the_file():
    # verifier, PR #2 repair round: on the same companyfacts and submissions Q went 13 -> 12 8-Ks (HBAN 31 -> 29) between
    # 2026-10-15 and 2026-10-20 and both committed files were rewritten with nothing filed
    base = tempfile.mkdtemp(prefix="fund_8k_")
    try:
        facts = _facts([_ni("2025-12-31", 2.2e9), _inst("LongTermDebt", "2025-12-31", 17221e6)])
        path = os.path.join(base, "ZZDEBT", "fundamentals.json")
        s1 = _run_main(base, facts, datetime.date(2026, 10, 15), SUB_8K)
        d1 = json.load(open(path, encoding="utf-8"))
        assert s1["fundamentals_json"] == "written" and d1["profile"]["eight_k_count_12m"] == 5
        os.utime(path, ns=(1_000_000_000_000_000_000, 1_000_000_000_000_000_000))
        s2 = _run_main(base, facts, datetime.date(2026, 10, 20), SUB_8K)  # 2025-10-17 aged out: 4 to the run date
        d2 = json.load(open(path, encoding="utf-8"))
        assert s2["fundamentals_json"] == "unchanged", s2["fundamentals_json"]
        assert os.stat(path).st_mtime_ns == 1_000_000_000_000_000_000, "file left untouched"
        assert d2["as_of"] == "2026-10-15" and d2["profile"]["eight_k_count_12m"] == 5, "as_of and its 8-K count still agree"
        # an 8-K filed after the file's as_of, with nothing else new, waits for the next content change
        sub_new = _recent([("8-K", "2026-10-19", "")] + list(zip(SUB_8K["form"], SUB_8K["filingDate"], SUB_8K["reportDate"])))
        assert _run_main(base, facts, datetime.date(2026, 10, 20), sub_new)["fundamentals_json"] == "unchanged"
        # a filing that changes a figure rewrites it, with the count carried to the run date
        facts2 = _facts([_ni("2025-12-31", 2.3e9), _inst("LongTermDebt", "2025-12-31", 17221e6)])
        s3 = _run_main(base, facts2, datetime.date(2026, 10, 20), sub_new)
        d3 = json.load(open(path, encoding="utf-8"))
        assert s3["fundamentals_json"] == "written" and d3["as_of"] == "2026-10-20" and d3["profile"]["eight_k_count_12m"] == 5, \
            "2026-10-19 in, 2025-10-17 out: 5 to 2026-10-20"
        # the pre-fix rule (the window to the run date, compared as is) would have rewritten the file on the second run
        stale = dict(d1, profile=dict(d1["profile"], eight_k_count_12m=F.eight_k_count(
            [d for f, d in zip(SUB_8K["form"], SUB_8K["filingDate"]) if f == "8-K"], datetime.date(2026, 10, 20))))
        assert stale["profile"]["eight_k_count_12m"] == 4 and stale["profile"] != d1["profile"]
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def test_read_price_carries_the_committed_close_without_prices_json():
    base = tempfile.mkdtemp(prefix="fund_price_")
    try:
        folder = os.path.join(base, "Q")
        _write(os.path.join(folder, "score.json"), {"price": 121.8685, "analysis_date": "2026-10-14"})
        prev = {"price": 121.62, "price_date": "2026-10-14", "price_source": "prices.json stats.last"}
        # the reviewer's Q: committed 121.62 (prices.json close, 2026-10-14) vs score.json 121.8685 (analysis price, same day)
        assert F._read_price(folder, prev) == (121.62, "2026-10-14", "prices.json stats.last"), "the committed close, not the older analysis price"
        assert F._read_price(folder) == (121.8685, "2026-10-14", "score.json price"), "no committed file: score.json as before"
        _write(os.path.join(folder, "prices.json"), {"stats": {"last": 123.0, "last_date": "2026-10-15"}})
        assert F._read_price(folder, prev) == (123.0, "2026-10-15", "prices.json stats.last"), "prices.json always wins"
        os.remove(os.path.join(folder, "prices.json"))
        _write(os.path.join(folder, "score.json"), {"price": 130.0, "analysis_date": "2026-10-19"})
        assert F._read_price(folder, prev) == (130.0, "2026-10-19", "score.json price"), "a newer analysis price beats an older carried close"
        from_score = {"price": 121.8685, "price_date": "2026-10-19", "price_source": "score.json price"}
        _write(os.path.join(folder, "score.json"), {"price": 125.0, "analysis_date": "2026-10-19"})
        assert F._read_price(folder, from_score) == (125.0, "2026-10-19", "score.json price"), "a score.json price is re-read, never carried"
        assert F._read_price(folder, {"price": None, "price_date": "2026-10-14", "price_source": "prices.json stats.last"})[2] == "score.json price"
        os.remove(os.path.join(folder, "score.json"))
        assert F._read_price(folder, prev) == (121.62, "2026-10-14", "prices.json stats.last")
        assert F._read_price(folder, None) == (None, None, None)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_fresh_clone_without_prices_json_leaves_the_file_alone():
    # verifier, PR #2 repair round: Q with prices.json moved away was rewritten at score.json's price (121.62 -> 121.8685)
    base = tempfile.mkdtemp(prefix="fund_fresh_")
    try:
        folder = os.path.join(base, "ZZDEBT")
        path = os.path.join(folder, "fundamentals.json")
        _write(os.path.join(folder, "score.json"), {"price": 15.01, "analysis_date": "2026-10-14"})
        _write(os.path.join(folder, "prices.json"), {"stats": {"last": 15.1, "last_date": "2026-10-14"}})
        facts = _facts([_ni("2025-12-31", 2.2e9), _inst("LongTermDebt", "2025-12-31", 17221e6)])
        assert _run_main(base, facts, datetime.date(2026, 10, 15), SUB_8K)["fundamentals_json"] == "written"
        assert json.load(open(path, encoding="utf-8"))["dividends"]["price"] == 15.1
        os.remove(os.path.join(folder, "prices.json"))   # the gitignored cache a clone does not have
        s2 = _run_main(base, facts, datetime.date(2026, 10, 20), SUB_8K)
        d2 = json.load(open(path, encoding="utf-8"))["dividends"]
        assert s2["fundamentals_json"] == "unchanged", s2["fundamentals_json"]
        assert (d2["price"], d2["price_date"], d2["price_source"]) == (15.1, "2026-10-14", "prices.json stats.last")
        assert s2["dividends"]["price"] == 15.1 and not any(n.startswith("price:") for n in s2["dividends"]["notes"])
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---------------- 7. price-free fundamentals.json (2026-10-16) ----------------
def test_stable_wildcard_paths():
    doc = {"as_of": "2026-10-16", "a": {"x": 1, "y": {"v": 2, "w": 3}, "z": {"v": 4, "w": 5}},
           "rows": [{"p": 1, "q": 2}, {"p": 3, "q": 4}, 7], "tags": ["t1", "t2"], "n": 5}
    snap = json.dumps(doc, sort_keys=True)
    assert S._strip(doc, ("a.*.v",)) == dict(doc, a={"x": 1, "y": {"w": 3}, "z": {"w": 5}}), "every key's v (a non-dict value is skipped)"
    assert S._strip(doc, ("rows.*.p",)) == dict(doc, rows=[{"q": 2}, {"q": 4}, 7]), "every list item's p"
    assert S._strip(doc, ("tags.*",)) == dict(doc, tags=[]) and S._strip(doc, ("a.*",)) == dict(doc, a={})
    assert S._strip(doc, ("missing.*.v", "a.y.missing", "n.x", "rows.0.p")) == doc, "paths that do not exist change nothing"
    assert S._strip(doc, ("as_of", "a.y")) == {k: v for k, v in dict(doc, a={"x": 1, "z": {"v": 4, "w": 5}}).items() if k != "as_of"}
    assert json.dumps(doc, sort_keys=True) == snap, "the caller's object is never modified"
    assert S._strip([1], ("a",)) == [1] and S._strip(doc, ()) == doc and S._strip(doc, ()) is not doc
    # the public API is unchanged and takes the wildcard paths
    assert S.canonical(dict(doc, a=dict(doc["a"], y={"v": 99, "w": 3})), ("a.*.v",)) == S.canonical(doc, ("a.*.v",))
    assert S.canonical(dict(doc, a=dict(doc["a"], y={"v": 2, "w": 99})), ("a.*.v",)) != S.canonical(doc, ("a.*.v",))
    base = tempfile.mkdtemp(prefix="stable_wild_")
    try:
        path = os.path.join(base, "f.json")
        assert S.write_json_if_changed(path, doc, volatile=("as_of", "rows.*.p"), indent=1) is True
        assert S.write_json_if_changed(path, dict(doc, as_of="x", rows=[{"p": 9, "q": 2}, {"p": 9, "q": 4}, 7]), volatile=("as_of", "rows.*.p")) is False
        assert S.write_json_if_changed(path, dict(doc, rows=[{"p": 1, "q": 9}, {"p": 3, "q": 4}, 7]), volatile=("as_of", "rows.*.p")) is True
        assert S.same_content(path, dict(doc, rows=[{"p": 0, "q": 9}, {"p": 0, "q": 4}, 7]), volatile=("rows.*.p",))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_price_leaves_strip_every_price_dependent_field():
    """FUNDAMENTALS_VOLATILE strips exactly the price leaves: the 10 top-level price / price note / market
    cap / yield leaves and the denominator, value and label under each of the four yields (10 + 3 × 4 = 22)."""
    shapes = {k: {"value": 1.0, "label": "1%", "bound": "exact", "prefix": "", "note": None} for k in F.YIELD_KEYS}
    div = {"price": 1.0, "price_date": "d", "price_source": "s", "price_note": None, "market_cap": 2.0, "market_cap_basis": "b",
           "dividend_yield": 0.1, "buyback_yield": 0.1, "net_buyback_yield": 0.1, "shareholder_yield": 0.1, "dps_ttm": 3.0,
           "yield_basis": {k: {"numerator": 5.0, "denominator": "x", "bound": "exact"} for k in F.YIELD_KEYS}, "yields_display": shapes}
    left = S._strip({"as_of": "x", "dividends": div}, F.FUNDAMENTALS_VOLATILE)
    assert left == {"dividends": {"dps_ttm": 3.0, "yield_basis": {k: {"numerator": 5.0, "bound": "exact"} for k in F.YIELD_KEYS},
                                  "yields_display": {k: {"bound": "exact", "prefix": "", "note": None} for k in F.YIELD_KEYS}}}
    n_leaves = sum(1 for p in F.PRICE_LEAVES if "*" not in p) + sum(len(F.YIELD_KEYS) for p in F.PRICE_LEAVES if "*" in p)
    assert n_leaves == 22, n_leaves


def test_a_new_close_alone_never_rewrites_the_file():
    base = tempfile.mkdtemp(prefix="fund_close_")
    try:
        folder = os.path.join(base, "ZZDEBT")
        path = os.path.join(folder, "fundamentals.json")
        facts = _facts([_ni("2025-12-31", 2.2e9), _inst("LongTermDebt", "2025-12-31", 17221e6),
                        _inst("EntityCommonStockSharesOutstanding", "2026-02-01", 1.45e9, unit="shares", tax="dei")])
        _write(os.path.join(folder, "prices.json"), {"stats": {"last": 15.1, "last_date": "2026-10-14"}})
        assert _run_main(base, facts, datetime.date(2026, 10, 15), SUB_8K)["fundamentals_json"] == "written"
        d1 = json.load(open(path, encoding="utf-8"))["dividends"]
        assert d1["price"] == 15.1 and d1["market_cap"] == 15.1 * 1.45e9 and d1["price_note"] is None
        assert d1["yield_basis"]["dividend_yield"]["denominator"] == "price 15.1 (prices.json stats.last)"
        os.utime(path, ns=(1_000_000_000_000_000_000, 1_000_000_000_000_000_000))
        # the next sessions' closes, same filings: the file stays, at the close it was written with
        for day, px in ((16, 15.6), (19, 14.2)):
            _write(os.path.join(folder, "prices.json"), {"stats": {"last": px, "last_date": f"2026-10-{day - 1}"}})
            s = _run_main(base, facts, datetime.date(2026, 10, day), SUB_8K)
            assert s["fundamentals_json"] == "unchanged", (day, s["fundamentals_json"])
            assert s["dividends"]["price"] == px, "the run itself priced at the new close"
        assert os.stat(path).st_mtime_ns == 1_000_000_000_000_000_000, "file left untouched"
        assert json.load(open(path, encoding="utf-8"))["dividends"] == d1
        # no prices.json and a newer score.json analysis price: score.json's quote, price_note says so — still volatile
        os.remove(os.path.join(folder, "prices.json"))
        _write(os.path.join(folder, "score.json"), {"price": 16.0, "analysis_date": "2026-10-20"})
        s = _run_main(base, facts, datetime.date(2026, 10, 20), SUB_8K)
        assert s["fundamentals_json"] == "unchanged" and s["dividends"]["price"] == 16.0
        assert os.stat(path).st_mtime_ns == 1_000_000_000_000_000_000
        # a filing that changes a figure writes the file, at the run's own price
        facts2 = _facts([_ni("2025-12-31", 2.3e9), _inst("LongTermDebt", "2025-12-31", 17221e6),
                         _inst("EntityCommonStockSharesOutstanding", "2026-02-01", 1.45e9, unit="shares", tax="dei")])
        _write(os.path.join(folder, "prices.json"), {"stats": {"last": 17.0, "last_date": "2026-10-20"}})
        s3 = _run_main(base, facts2, datetime.date(2026, 10, 21), SUB_8K)
        d3 = json.load(open(path, encoding="utf-8"))["dividends"]
        assert s3["fundamentals_json"] == "written" and d3["price"] == 17.0 and d3["market_cap"] == 17.0 * 1.45e9
        # a new share count is content (it moves the market cap at any price): written
        facts3 = _facts([_ni("2025-12-31", 2.3e9), _inst("LongTermDebt", "2025-12-31", 17221e6),
                         _inst("EntityCommonStockSharesOutstanding", "2026-05-01", 1.40e9, unit="shares", tax="dei")])
        assert _run_main(base, facts3, datetime.date(2026, 10, 22), SUB_8K)["fundamentals_json"] == "written"
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_every_text_mode_open_names_utf8():
    src = open(F.__file__, encoding="utf-8").read()
    bad = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            mode = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else next(
                (k.value.value for k in node.keywords if k.arg == "mode" and isinstance(k.value, ast.Constant)), "r")
            if "b" not in mode and not any(k.arg == "encoding" for k in node.keywords):
                bad.append(node.lineno)
    assert not bad, f"fundamentals.py open() without encoding at lines {bad}"


# ---------------- 8. ruling-sheet Q8 (Andrew, 2026-10-19): derived FCF / OE on the engine's total capex ----------------
def _fyd(tag, end, val, unit="USD", tax=G, start=None, form="10-K", filed=None):
    start = start or f"{end[:4]}-01-01"
    return (tax, tag, unit, {"start": start, "end": end, "val": val, "form": form, "fp": "FY", "filed": filed or f"{int(end[:4]) + 1}-02-15", "accn": "K" + end})


def test_fcf_and_owner_earnings_deduct_the_engine_intangible_leg():
    """GGB / GMED (PRs #43 / #44): the enrichment's fcf and oe_conservative subtracted the PP&E leg only, while
    engine 5.5 (dcf_engine.capex_for_period, the scored CSV) adds intangible purchases on top. GGB FY2025 (BRL):
    OCF 7,987,454,000 − PP&E 6,681,620,000 − intangibles 171,221,000 = FCF 1,134,613,000 (was 1,305,834,000),
    OE 985,403,000 (was 1,156,624,000). GMED FY2025: 579,022,000 / 529,243,000 (was 588,768,000 / 538,989,000)."""
    ggb = _facts([_fyd("CashFlowsFromUsedInOperatingActivities", "2025-12-31", 7_987_454_000, "BRL", IF, form="20-F"),
                  _fyd("PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities", "2025-12-31", 6_681_620_000, "BRL", IF, form="20-F"),
                  _fyd("PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities", "2025-12-31", 171_221_000, "BRL", IF, form="20-F"),
                  _fyd("AdjustmentsForSharebasedPayments", "2025-12-31", 149_210_000, "BRL", IF, form="20-F"),
                  _fyd("ProfitLoss", "2025-12-31", 1_000_000_000, "BRL", IF, form="20-F")])
    r = _row(ggb, "2025-12-31")
    assert r["capex"] == 6_681_620_000 and r["capex_intangibles"] == 171_221_000, "the PP&E and intangible display fields are unchanged"
    assert r["fcf"] == 1_134_613_000 and r["oe_conservative"] == 985_403_000, (r["fcf"], r["oe_conservative"])
    gmed = _facts([_fyd("NetCashProvidedByUsedInOperatingActivities", "2025-12-31", 753_447_000), _fyd("PaymentsToAcquirePropertyPlantAndEquipment", "2025-12-31", 164_679_000),
                   _fyd("PaymentsToAcquireIntangibleAssets", "2025-12-31", 9_746_000), _fyd("ShareBasedCompensation", "2025-12-31", 49_779_000),
                   _fyd("NetIncomeLoss", "2025-12-31", 300_000_000)])
    r = _row(gmed, "2025-12-31")
    assert r["fcf"] == 579_022_000 and r["oe_conservative"] == 529_243_000, (r["fcf"], r["oe_conservative"])


def test_intangible_leg_follows_the_engine_rules():
    """The leg is dcf_engine's: its tag set (CAPEX_INTANGIBLE_TAGS — capitalized software, PaymentsToDevelopSoftware,
    is capex since engine 5.7 (R9, Andrew 2026-10-19), so it is shown in capex_intangibles AND deducted), a
    negative fact dropped, and ECHO's cumulative duplicate (30,000,000,000 also filed on a multi-year context) dropped.
    [07 G16b] Before engine 5.7 this asserted fcf 900 / oe_conservative 890 (software not deducted)."""
    base = [_fyd("NetCashProvidedByUsedInOperatingActivities", "2025-12-31", 1_000), _fyd("PaymentsToAcquirePropertyPlantAndEquipment", "2025-12-31", 100),
            _fyd("ShareBasedCompensation", "2025-12-31", 10), _fyd("NetIncomeLoss", "2025-12-31", 500)]
    soft = _row(_facts(base + [_fyd("PaymentsToDevelopSoftware", "2025-12-31", 40)]), "2025-12-31")
    assert soft["capex_intangibles"] == 40 and soft["fcf"] == 860 and soft["oe_conservative"] == 850, soft["fcf"]
    neg = _row(_facts(base + [_fyd("PaymentsToAcquireIntangibleAssets", "2025-12-31", -6)]), "2025-12-31")
    assert neg["fcf"] == 900
    echo = _row(_facts(base + [_fyd("PaymentsToAcquireIntangibleAssets", "2025-12-31", 30_000_000_000),
                               _fyd("PaymentsToAcquireIntangibleAssets", "2025-12-31", 30_000_000_000, start="2018-01-01")]), "2025-12-31")
    assert echo["fcf"] == 900, echo["fcf"]
    both = _row(_facts(base + [_fyd("PaymentsToAcquireIntangibleAssets", "2025-12-31", 30), _fyd("PaymentsToAcquireOtherIntangibleAssets", "2025-12-31", 5)]), "2025-12-31")
    assert both["fcf"] == 865 and both["oe_conservative"] == 855, "two engine intangible lines are summed, as capex_for_period does"
    assert F.ENGINE_INTANGIBLE_TAGS is E.CAPEX_INTANGIBLE_TAGS, "one tag list, the engine's"


def _ytd_facts(tag, vals, fy_start="2025-01-01", ends=("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31")):
    """Year-to-date facts (cash-flow lines are filed YTD): vals[i] is the YTD value at ends[i]; None = not tagged then."""
    out = []
    for i, v in enumerate(vals):
        if v is None:
            continue
        form, fp = ("10-K", "FY") if i == 3 else ("10-Q", f"Q{i + 1}")
        out.append((G, tag, "USD", {"start": fy_start, "end": ends[i], "val": v, "form": form, "fp": fp, "filed": f"{ends[i][:4]}-{ends[i][5:7]}-28", "accn": f"Q{fy_start}{i}"}))
    return out


def _intang_case(intang_ytd, fy_start="2025-01-01", ends=("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31")):
    """OCF 100/quarter, PP&E capex 10/quarter, SBC 5/quarter, net income 50/quarter — and the intangible line's YTD values."""
    cum = lambda per: [per * (i + 1) for i in range(4)]
    facts = _facts(_ytd_facts("NetCashProvidedByUsedInOperatingActivities", cum(100), fy_start, ends) + _ytd_facts("NetIncomeLoss", cum(50), fy_start, ends)
                   + _ytd_facts("PaymentsToAcquirePropertyPlantAndEquipment", cum(10), fy_start, ends) + _ytd_facts("ShareBasedCompensation", cum(5), fy_start, ends)
                   + _ytd_facts("PaymentsToAcquireIntangibleAssets", intang_ytd, fy_start, ends))
    annual, _, _ = F.build_annual(facts)
    q = F.build_quarterly(facts, annual=annual)
    ttm = F.build_ttm(q, intang_ttm=F.intangible_capex_ttm(facts, "USD", q, fy_starts=F.core_fy_starts(facts, money="USD")))
    return annual, q, ttm


def test_quarterly_and_ttm_fcf_deduct_the_intangible_leg():
    """GMED's TTM OE was 706,634,000 in the enrichment vs the DCF's 701,888,000 — the 4,746,000 TTM intangible leg.
    Quarters derive the leg year-to-date less the previous year-to-date, so a year's quarters sum to its FY figure; a
    derived quarter may be negative (a YTD restated down) — only the TTM total is floored, as the engine's is."""
    annual, q, ttm = _intang_case([1, 3, 6, 5])  # Q4 derived 5 - 6 = -1
    assert [r["fcf"] for r in q] == [89, 88, 87, 91], [r["fcf"] for r in q]
    assert [r["oe_conservative"] for r in q] == [84, 83, 82, 86]
    assert annual[-1]["fcf"] == 400 - 40 - 5, "the FY leg is the filed FY fact (5)"
    assert ttm["fcf"] == annual[-1]["fcf"] and ttm["oe_conservative"] == annual[-1]["oe_conservative"], (ttm["fcf"], annual[-1]["fcf"])


def test_intangible_leg_first_tagged_mid_year_reaches_the_quarters_and_ttm():
    """Verifier round 1 (IREN): PaymentsToAcquireIntangibleAssets 107,573,000 is first tagged on the six-month 10-Q, then
    the nine-month and FY contexts, Q1 untagged. The old derivation needed the leg one rank shorter, so no quarter of the
    year deducted anything: TTM fcf -897,588,000 against an FY2026 fcf of -1,005,161,000 for the same four quarters (PFGC
    is the nine-month shape). An untagged earlier YTD is 0, as the engine counts an untagged leg."""
    ends = ("2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30")
    annual, q, ttm = _intang_case([None, 107_573_000, 107_573_000, 107_573_000], fy_start="2025-07-01", ends=ends)
    assert [r["fcf"] for r in q] == [90, 90 - 107_573_000, 90, 90], [r["fcf"] for r in q]
    assert annual[-1]["fcf"] == 360 - 107_573_000
    assert ttm["fcf"] == annual[-1]["fcf"], (ttm["fcf"], annual[-1]["fcf"])
    _, q9, ttm9 = _intang_case([None, None, 9_600_000, 9_600_000])  # PFGC: first tagged on the nine-month 10-Q
    assert q9[2]["fcf"] == 90 - 9_600_000 and ttm9["fcf"] == 360 - 9_600_000, (q9[2]["fcf"], ttm9["fcf"])


def test_intangible_ytd_restated_down_is_not_floored_per_quarter():
    """Verifier round 1 (RMD): YTD 2,814,000 / 1,479,000 / 1,479,000 / FY 2,218,000 — the derived Q2 is -1,335,000. The
    old code dropped it (each quarter floored at zero), so the TTM deducted 3,553,000 while FY2026, the same window,
    deducts 2,218,000. The quarters now sum to the FY figure and the TTM equals it."""
    annual, q, ttm = _intang_case([2_814_000, 1_479_000, 1_479_000, 2_218_000])
    assert [r["fcf"] for r in q] == [90 - 2_814_000, 90 + 1_335_000, 90, 90 - 739_000], [r["fcf"] for r in q]
    assert sum(r["fcf"] for r in q) == annual[-1]["fcf"] == 360 - 2_218_000
    assert ttm["fcf"] == annual[-1]["fcf"] and ttm["oe_conservative"] == annual[-1]["oe_conservative"]


def test_completed_year_without_an_fy_intangible_figure_deducts_nothing_in_its_quarters():
    """Verifier round 2 (RMD FY2024): the 10-Qs tag YTD 10,831,000 / 12,036,000 / 13,954,000 and the latest 10-K
    re-files FY2024 as 0, which the engine ignores, so the annual row deducts 0. The old quarters still deducted the
    10-Q legs with no Q4 to offset them (13,954,000 across the year vs 0 on the annual row - BAX FY2025, NXT FY2026
    the same: no FY fact at all). A filed year's quarters now sum to its annual figure: nothing."""
    for fy in (0, None):
        annual, q, _ = _intang_case([10_831_000, 12_036_000, 13_954_000, fy])
        assert annual[-1]["fcf"] == 360, annual[-1]["fcf"]
        assert [r["fcf"] for r in q] == [90, 90, 90, 90], (fy, [r["fcf"] for r in q])
        assert sum(r["fcf"] for r in q) == annual[-1]["fcf"]
    # the year still in progress (no annual row yet) keeps its YTD legs
    ends = ("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31")
    cum = lambda per: [per * (i + 1) for i in range(3)] + [None]
    facts = _facts(_ytd_facts("NetCashProvidedByUsedInOperatingActivities", cum(100), "2025-01-01", ends) + _ytd_facts("NetIncomeLoss", cum(50), "2025-01-01", ends)
                   + _ytd_facts("PaymentsToAcquirePropertyPlantAndEquipment", cum(10), "2025-01-01", ends)
                   + _ytd_facts("PaymentsToAcquireIntangibleAssets", [10_831_000, 12_036_000, 13_954_000, None], "2025-01-01", ends))
    assert F.intangible_capex_quarterly(facts, "USD", fy_starts={"2025-01-01"}) == {"2025-03-31": 10_831_000, "2025-06-30": 1_205_000, "2025-09-30": 1_918_000}


def test_ttm_intangible_leg_is_the_engine_formula():
    """A TTM ending mid-year: FY - the prior year's same-length YTD + the current YTD (ttm.py add_intangibles), floored
    at zero; a prior-YTD amount with no FY amount leaves the remainder unknown and neither leg counts (R4-INTANG, BAX)."""
    ends = ("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31")
    ends2 = ("2026-03-31", "2026-06-30", "2026-09-30", "2026-12-31")
    base = []
    cum = lambda per: [per * (i + 1) for i in range(4)]
    for fs, en in (("2025-01-01", ends), ("2026-01-01", ends2)):
        base += (_ytd_facts("NetCashProvidedByUsedInOperatingActivities", cum(100), fs, en) + _ytd_facts("NetIncomeLoss", cum(50), fs, en)
                 + _ytd_facts("PaymentsToAcquirePropertyPlantAndEquipment", cum(10), fs, en) + _ytd_facts("ShareBasedCompensation", cum(5), fs, en))
    def run(i25, i26):
        facts = _facts(base + _ytd_facts("PaymentsToAcquireIntangibleAssets", i25, "2025-01-01", ends)
                       + _ytd_facts("PaymentsToAcquireIntangibleAssets", i26, "2026-01-01", ends2))
        q = [r for r in F.build_quarterly(facts, annual=F.build_annual(facts)[0]) if r["period_end"] <= "2026-06-30"]
        return F.intangible_capex_ttm(facts, "USD", q, fy_starts=F.core_fy_starts(facts, money="USD"))
    assert run([4, 6, 9, 12], [1, 2, None, None]) == 12 - 6 + 2
    assert run([None, 9, None, None], [3, 3, None, None]) == 3, "BAX: prior YTD 9 with no FY fact - only the current YTD counts"
    assert run([4, 30, 31, 12], [1, 2, None, None]) == 2, "a prior YTD above the FY figure: the remainder is unknown"
    assert run([4, 6, 9, 12], [None, None, None, None]) == 6 and run([0, 0, 0, 0], [None, None, None, None]) == 0


def test_direct_three_month_intangible_facts_keep_their_quarters():
    """Codex review round 1 on PR #53 (4322240083): the FY context alone (and a Q1 fact, which starts on the fiscal-year
    start) made the year a year-to-date year, so the direct three-month Q2 / Q3 facts were dropped and Q4 took the
    whole remainder: Q1 10, Q2 20, Q3 30 and FY 100 gave Q1 10, no Q2 / Q3, Q4 90. A quarter with a filed three-month
    fact and no year-to-date leg ending with it keeps that fact; only the quarters with no figure of their own are
    derived (Q4 = FY less the quarters before it), so the year still sums to its FY figure."""
    T = "PaymentsToAcquireIntangibleAssets"
    def d(start, end, val, form="10-Q", fp="Q1"):
        return (G, T, "USD", {"start": start, "end": end, "val": val, "form": form, "fp": fp, "filed": f"{end[:4]}-{end[5:7]}-28", "accn": "A" + end})
    fy = d("2025-01-01", "2025-12-31", 100, "10-K", "FY")
    direct = _facts([d("2025-01-01", "2025-03-31", 10), d("2025-04-01", "2025-06-30", 20, fp="Q2"), d("2025-07-01", "2025-09-30", 30, fp="Q3"), fy])
    got = F.intangible_capex_quarterly(direct, "USD", fy_starts={"2025-01-01"})
    assert got == {"2025-03-31": 10, "2025-06-30": 20, "2025-09-30": 30, "2025-12-31": 40}, got
    # a discrete Q2 between year-to-date legs: Q1 10, Q2 (three months) 20, nine months 60, FY 100
    mixed = _facts([d("2025-01-01", "2025-03-31", 10), d("2025-04-01", "2025-06-30", 20, fp="Q2"), d("2025-01-01", "2025-09-30", 60, fp="Q3"), fy])
    got = F.intangible_capex_quarterly(mixed, "USD", fy_starts={"2025-01-01"})
    assert got == {"2025-03-31": 10, "2025-06-30": 20, "2025-09-30": 30, "2025-12-31": 40}, got


# ---------------- Codex review round 2 on PR #53 ----------------
def _fact6k(tag, start, end, val, form, fp, filed, accn):
    return (G, tag, "USD", {"start": start, "end": end, "val": val, "form": form, "fp": fp, "filed": filed, "accn": accn})


def test_a_full_year_on_a_6k_is_not_a_completed_annual_year():
    """Codex review round 2 on PR #53 (4322452072): core_fy_periods reads every duration form, so a full-year revenue /
    profit / OCF context furnished on a 6-K before the 20-F (AGI's 2016 6-K with fp FY; TU's Q2 6-Ks carry trailing
    twelve-month contexts) counted as a completed year with an annual row. annual_series makes no annual row from a
    6-K, so the year had no FY intangible figure, landed in `unreconciled`, and every filed quarterly intangible fact of
    the year was discarded: Q1's filed purchase of 10 deducted nothing (fcf 43, not 55 - 12 - 10 = 33). Only the
    annual-report periods annual_series turns into an annual row (fp FY on MONEY_UNIT_FORMS) are completed years."""
    T = {"rev": "RevenueFromContractWithCustomerExcludingAssessedTax", "ni": "NetIncomeLoss", "ocf": "NetCashProvidedByUsedInOperatingActivities",
         "ppe": "PaymentsToAcquirePropertyPlantAndEquipment", "int": "PaymentsToAcquireIntangibleAssets"}
    base = [_fact6k(T[k], "2024-01-01", "2024-12-31", v, "20-F", "FY", "2025-03-20", "A20F24") for k, v in (("rev", 1000), ("ni", 100), ("ocf", 200), ("ppe", 50), ("int", 40))]
    base += [_fact6k(T[k], "2025-01-01", "2025-03-31", v, "6-K", "Q1", "2025-05-10", "A6KQ1") for k, v in (("rev", 260), ("ni", 26), ("ocf", 55), ("ppe", 12), ("int", 10))]
    full_year_6k = [_fact6k(T[k], "2025-01-01", "2025-12-31", v, "6-K", "FY", "2026-02-10", "A6KFY") for k, v in (("rev", 1100), ("ni", 110), ("ocf", 220))]
    ttm_6k = [_fact6k(T[k], "2024-04-01", "2025-03-31", v, "6-K", "Q1", "2025-05-10", "A6KQ1") for k, v in (("rev", 1050), ("ni", 105), ("ocf", 210))]
    for extra in ([], full_year_6k, ttm_6k):
        facts = _facts(base + extra)
        assert F.intangible_capex_quarterly(facts, "USD", fy_starts=F.core_fy_starts(facts, money="USD")) == {"2024-12-31": 40, "2025-03-31": 10}, extra[:1]
        q1 = next(r for r in F.build_quarterly(facts) if r["period_end"] == "2025-03-31")
        assert q1["fcf"] == 55 - 12 - 10, (q1["fcf"], extra[:1])
    assert F.annual_row_periods(_facts(base + full_year_6k), money="USD") == {("2024-01-01", "2024-12-31")}


def _engine_annual_capex(facts, end):
    """The engine's own annual capex assembly for one FY (dcf_engine.py v5.5: per tag the FY fact, then capex_for_period)."""
    def legs(tags):
        out = []
        for t in tags:
            vals, _, units, filed = F.annual_series(facts, [t], True, with_filed=True, money="USD")
            if end in vals:
                out.append((t[1] if isinstance(t, tuple) else t, vals[end], units[end], filed.get(end)))
        return out
    return E.capex_for_period(legs(E.CAPEX_ROLLUP_TAGS), legs(E.CAPEX_COMPONENT_TAGS), legs(E.CAPEX_INTANGIBLE_TAGS),
                              cumulative=E.cumulative_context_values(facts, E.CAPEX_INTANGIBLE_TAGS, units=("USD",)))


def test_the_ppe_leg_is_the_engine_assembly_not_the_first_tag():
    """Codex review round 2 on PR #53 (4322452077): with no PP&E roll-up and several additive components, the
    enrichment's capex was the first tag in its list (construction in process 10) while engine 5.5's PP&E leg sums the
    components (capex_for_period: 10 + 20), so OCF 100, CIP 10, other PP&E 20, intangibles 5 gave fcf 85, not the
    engine's 65 (GLPI FY2025 191.3M vs 495.7M, GSAT, LNT, IP). Components outside the old list count too (HST's
    PaymentsForCapitalImprovements, AR's oil-and-gas lines). `capex` is now the engine's PP&E leg (a roll-up when filed,
    else the components summed under its unit / duplicate / parts-of-total rules); fcf / oe_conservative = OCF - that
    leg - the intangible leg [- SBC], on the annual rows, the quarters and the TTM alike."""
    end = "2025-12-31"
    base = [_fyd("NetCashProvidedByUsedInOperatingActivities", end, 100), _fyd("PaymentsToAcquireIntangibleAssets", end, 5),
            _fyd("ShareBasedCompensation", end, 3), _fyd("NetIncomeLoss", end, 50), _fyd("Revenues", end, 500)]
    comps = _facts(base + [_fyd("PaymentsForConstructionInProcess", end, 10), _fyd("PaymentsToAcquireOtherPropertyPlantAndEquipment", end, 20)])
    rows, tags, _ = F.build_annual(comps)
    r = next(x for x in rows if x["period_end"] == end)
    eng = _engine_annual_capex(comps, end)
    assert (eng["ppe"], eng["intangibles"]) == (30, 5)
    assert r["capex"] == 30 and r["fcf"] == 65 and r["oe_conservative"] == 62, (r["capex"], r["fcf"], r["oe_conservative"])
    assert tags["capex"] == ["+".join(eng["ppe_tags"])] == ["PaymentsToAcquireOtherPropertyPlantAndEquipment+PaymentsForConstructionInProcess"], tags["capex"]
    hst = _facts(base + [_fyd("PaymentsForCapitalImprovements", end, 40), _fyd("PaymentsToAcquireOtherPropertyPlantAndEquipment", end, 20)])
    r = _row(hst, end)
    assert r["capex"] == 60 and r["fcf"] == 35, (r["capex"], r["fcf"])
    rolled = _facts(base + [_fyd("PaymentsToAcquirePropertyPlantAndEquipment", end, 50), _fyd("PaymentsForConstructionInProcess", end, 10)])
    r = _row(rolled, end)
    assert r["capex"] == 50 and r["fcf"] == 45, "a filed roll-up is authoritative; components are never added to it"
    # quarters and the TTM: each year-to-date context is assembled the engine's way, then differenced
    cum = lambda per: [per * (i + 1) for i in range(4)]
    q_facts = _facts(_ytd_facts("NetCashProvidedByUsedInOperatingActivities", cum(100)) + _ytd_facts("NetIncomeLoss", cum(50))
                     + _ytd_facts("PaymentsForConstructionInProcess", cum(3)) + _ytd_facts("PaymentsToAcquireOtherPropertyPlantAndEquipment", cum(5))
                     + _ytd_facts("ShareBasedCompensation", cum(1)))
    annual, _, _ = F.build_annual(q_facts)
    q = F.build_quarterly(q_facts, annual=annual)
    assert [x["capex"] for x in q] == [8, 8, 8, 8], [x["capex"] for x in q]
    assert [x["fcf"] for x in q] == [92, 92, 92, 92] and [x["oe_conservative"] for x in q] == [91, 91, 91, 91]
    assert annual[-1]["capex"] == 32 and annual[-1]["fcf"] == 368
    ttm = F.build_ttm(q, intang_ttm=F.intangible_capex_ttm(q_facts, "USD", q, fy_starts=F.core_fy_starts(q_facts, money="USD")))
    assert ttm["capex"] == 32 and ttm["fcf"] == annual[-1]["fcf"], (ttm["capex"], ttm["fcf"])


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
