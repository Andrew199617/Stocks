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
