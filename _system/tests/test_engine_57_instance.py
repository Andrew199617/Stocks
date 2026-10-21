#!/usr/bin/env python3
"""Engine 5.7 — annual facts from the filing's own XBRL instance (Andrew's ruling R2b, 2026-10-19; design 04 Part B,
tests 6-13, rebase L4 amendments 6-8). Run: python _system/tests/test_engine_57_instance.py (or python -m pytest).
Offline: engine55_harness (EDGAR submissions, the instance fetch and FX are patched); nothing is written outside the
harness's temp bases. Every test fails on the L0 scaffold (e22e814: load_annual_instance is the identity stub, the
tag lists are not hoisted).

The equivalence tests drop a fixture's latest fiscal year from companyfacts (every annual entry ending at its FY
end), hand the engine an XBRL 2.1 instance built from exactly the dropped entries and an EDGAR submissions record
listing that annual report, and require the run to equal the unmodified fixture's: the merged facts must reach every
reader in the engine (CSV rows, base, tier, scenarios, FX, the acquired-IPR&D detection).

6. drop-and-restore on CCJ (40-F, IFRS, CAD): identical record and CSV, plus annual_from_instance.applied and the
   ANNUAL_FROM_INSTANCE flag; without the fallback (the L0 stub) the latest FY is missing and the base differs.
7. RDY's shape: companyfacts keeps the dei cover fact of the very accession whose annual facts it lacks — the
   fallback still merges (the trigger is the missing period, not the accession) and never duplicates that fact.
8. no candidate (the period is in companyfacts / isXBRL 0 / only an /A amendment is newer): no new key, identical run.
9. a dei mismatch (DocumentType 10-Q, another CIK, another period end) records applied false with the reason, no
   flag, CSV unchanged; an inline-only folder records "inline document only".
10. a failed EDGAR submissions fetch degrades: the run completes, annual_from_instance {applied false, checked false}.
11. --measure never writes <T>/annual_instance.json; a written one is reused without a fetch; one whose facts were
   edited no longer hashes to its facts_sha256: refetched, or "edited" when the refetch fails (amendment 6).
12. every engine fixture (23) runs with no annual_from_instance key and no ANNUAL_FROM_INSTANCE flag, and three of
   them equal the DCF_NO_INSTANCE=1 run byte for byte.
13. the hoisted tag lists are the engine's own: the same lists main() reads (used_tags of the recorded CCJ / VOD /
   PUK runs), DILUTED_ONLY_TAGS without the basic tags.
Amendment 7: merged entries carry companyfacts' full shape, so a merged 10-K FY's acquired-IPR&D charge reaches the
one-time deduction (HALO drop-and-restore: the same iprd_adjustment).
"""
import copy
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402
from test_engine_55 import args_for, CCJ_J, recorded_matching_fixture  # noqa: E402

E = H._engine()
ANNUAL = ("10-K", "20-F", "40-F")
VOLATILE = ("content_hash", "annual_from_instance")
NS = {"us-gaap": "http://fasb.org/us-gaap/2025", "ifrs-full": "https://xbrl.ifrs.org/taxonomy/2025-03-27/ifrs-full",
      "dei": "http://xbrl.sec.gov/dei/2025"}
HALO_J = {"iprd_cash_flow_check": [
    {"period": "2025-12-31", "window": "fy", "amount": 284887000, "presentation": "added_back_paid_in_investing",
     "source": "test: HALO 10-K FY2025 cash-flow statement (the acquired IPR&D added back, paid in investing)"}]}


# ---------------------------------------------------------------------------
# helpers: drop a fiscal year, write its instance, list its filing
# ---------------------------------------------------------------------------
def drop_fy(fx, fy_end, keep=()):
    """(fixture without the annual entries ending at fy_end, [(taxonomy, tag, unit, entry)] removed). `keep`:
    (taxonomy, tag) pairs left in companyfacts (RDY's dei cover fact)."""
    fx = copy.deepcopy(fx)
    removed = []
    for tax, tags in fx["facts"]["facts"].items():
        for tag, d in tags.items():
            for unit, arr in d["units"].items():
                kept = []
                for e in arr:
                    if (e.get("end") == fy_end and e.get("form") in ANNUAL and e.get("fp") == "FY"
                            and (tax, tag) not in keep):
                        removed.append((tax, tag, unit, e))
                    else:
                        kept.append(e)
                d["units"][unit] = kept
    return fx, removed


def _unit_xml(uid, unit):
    def m(u):
        return f"iso4217:{u}" if len(u) == 3 and u.isupper() else f"xbrli:{u}"
    if "/" in unit:
        a, b = unit.split("/", 1)
        return (f'<xbrli:unit id="{uid}"><xbrli:divide><xbrli:unitNumerator><xbrli:measure>{m(a)}</xbrli:measure>'
                f'</xbrli:unitNumerator><xbrli:unitDenominator><xbrli:measure>{m(b)}</xbrli:measure>'
                f'</xbrli:unitDenominator></xbrli:divide></xbrli:unit>')
    return f'<xbrli:unit id="{uid}"><xbrli:measure>{m(unit)}</xbrli:measure></xbrli:unit>'


def instance_xml(removed, cik, doc_type, period_end, fy_focus, fp="FY"):
    """An XBRL 2.1 instance holding exactly the removed companyfacts entries, undimensioned, plus the dei block."""
    ctx, units, facts = {}, {}, []
    for tax, tag, unit, e in removed:
        key = (e.get("start"), e["end"])
        cid = ctx.setdefault(key, f"c{len(ctx)}")
        uid = units.setdefault(unit, f"u{len(units)}")
        v = e["val"]
        txt = repr(float(v)) if isinstance(v, float) and not float(v).is_integer() else str(int(v))
        facts.append(f'<{tax}:{tag} contextRef="{cid}" unitRef="{uid}" decimals="0">{txt}</{tax}:{tag}>')
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             '<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:iso4217="http://www.xbrl.org/2003/iso4217" '
             + " ".join(f'xmlns:{p}="{u}"' for p, u in NS.items()) + ">"]
    dur = "c_dei"
    for (s, en), cid in ctx.items():
        per = (f"<xbrli:startDate>{s}</xbrli:startDate><xbrli:endDate>{en}</xbrli:endDate>" if s
               else f"<xbrli:instant>{en}</xbrli:instant>")
        lines.append(f'<xbrli:context id="{cid}"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">'
                     f'{cik:010d}</xbrli:identifier></xbrli:entity><xbrli:period>{per}</xbrli:period></xbrli:context>')
    lines.append(f'<xbrli:context id="{dur}"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">{cik:010d}'
                 f'</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:instant>{period_end}</xbrli:instant>'
                 '</xbrli:period></xbrli:context>')
    lines += [_unit_xml(uid, u) for u, uid in units.items()]
    for k, v in (("DocumentType", doc_type), ("DocumentPeriodEndDate", period_end), ("DocumentFiscalPeriodFocus", fp),
                 ("DocumentFiscalYearFocus", fy_focus), ("EntityCentralIndexKey", f"{cik:010d}")):
        lines.append(f'<dei:{k} contextRef="{dur}">{v}</dei:{k}>')
    lines += facts + ["</xbrli:xbrl>"]
    return "\n".join(lines).encode("utf-8")


def submissions(*filings):
    """An EDGAR submissions record: filings (form, accession, filed, reportDate, primary, isXBRL), newest first."""
    cols = ("form", "accessionNumber", "filingDate", "reportDate", "primaryDocument", "isXBRL")
    return {"filings": {"recent": {c: [f[i] for f in filings] for i, c in enumerate(cols)}}}


CCJ_ACC = "0001193125-26-116229"
CCJ_FILING = ("40-F", CCJ_ACC, "2026-03-19", "2025-12-31", "ccj-20251231.htm", 1)
CCJ_PRIOR = ("40-F", "0001193125-25-060350", "2025-03-21", "2024-12-31", "ccj-20241231.htm", 1)


def ccj_restored(doc_type="40-F", cik=None, period="2025-12-31", fp="FY", filing=CCJ_FILING, keep=(), extra=None):
    """CCJ with its FY2025 dropped from companyfacts, its instance and submissions attached."""
    fx, removed = drop_fy(H.load_fixture("CCJ"), "2025-12-31", keep=keep)
    if keep:   # the instance still carries the kept facts (the filing has them; companyfacts happens to as well)
        _, removed = drop_fy(H.load_fixture("CCJ"), "2025-12-31")
    fx["instance_bytes"] = instance_xml(removed, cik or fx["cik"], doc_type, period, "2025", fp=fp)
    fx["instance_url"] = "https://www.sec.gov/Archives/edgar/data/1009001/000119312526116229/ccj-20251231_htm.xml"
    fx["submissions"] = submissions(("6-K", "0001193125-26-200000", "2026-08-01", "2026-06-30", "x.htm", 0),
                                    filing, CCJ_PRIOR)
    fx.update(extra or {})
    return fx, removed


def run(ticker, args, judgment=None, fixture=None, patch=None, measure=False, env=None, keep_base=False, base=None):
    fx = fixture or H.load_fixture(ticker)
    base = base or H.make_base(fx, judgment, None, copy_repo_files=False)
    return H.run_engine(ticker, args=list(args), base=base, fixture=fx, patch=patch, measure=measure, env=env,
                        keep_base=keep_base)


def strip(n):
    n = {k: v for k, v in n.items() if k not in VOLATILE}
    n["fragility_flags"] = [f for f in n.get("fragility_flags") or [] if not f.startswith("ANNUAL_FROM_INSTANCE")]
    return n


_CACHE = {}


def plain_ccj():
    if "ccj" not in _CACHE:
        out = run("CCJ", args_for(5), judgment=CCJ_J)
        assert out["exit"] == 0, out["stdout"][-1500:]
        _CACHE["ccj"] = out
    return _CACHE["ccj"]


def dropped_ccj():
    """CCJ with FY2025 dropped and no instance (what the L0 / 5.6 engine reads)."""
    if "dropped" not in _CACHE:
        fx, _ = drop_fy(H.load_fixture("CCJ"), "2025-12-31")
        _CACHE["dropped"] = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
    return _CACHE["dropped"]


# ---------------------------------------------------------------------------
# 6-7. drop and restore
# ---------------------------------------------------------------------------
def test_drop_and_restore_equivalence():
    plain = plain_ccj()
    fx, removed = ccj_restored()
    out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
    assert out["exit"] == 0, out["stdout"][-1500:]
    n, p = out["numbers"], plain["numbers"]
    rec = n.get("annual_from_instance")
    assert rec and rec["applied"] is True and rec["checked"] is True, rec
    assert rec["form"] == "40-F" and rec["accession"] == CCJ_ACC and rec["report_date"] == "2025-12-31", rec
    assert rec["periods_added"] == ["2025-12-31"] and rec["companyfacts_latest_annual_end"] == "2024-12-31", rec
    assert rec["facts_merged"] == len(removed) == 22 and rec["conflicts"] == [] and rec["reason"] is None, rec
    assert rec["cache"] == "CCJ/annual_instance.json" and rec["instance_url"].endswith("_htm.xml"), rec
    assert len(rec["instance_sha256"]) == 64 and len(rec["facts_sha256"]) == 64, rec
    flags = [f for f in n["fragility_flags"] if f.startswith("ANNUAL_FROM_INSTANCE")]
    assert flags == ["ANNUAL_FROM_INSTANCE: fiscal year(s) 2025-12-31 read from the 40-F's own XBRL instance (accession "
                     f"{CCJ_ACC}, filed 2026-03-19) — EDGAR companyfacts had not ingested them (its latest annual period "
                     "ends 2024-12-31); 22 undimensioned facts merged, no companyfacts value replaced; see dcf_numbers.json "
                     "annual_from_instance"], flags
    assert strip(n) == strip(p), sorted(k for k in set(n) | set(p) if strip(n).get(k) != strip(p).get(k))
    assert out["rows"] == plain["rows"]
    assert n["latest_period_end"] == "2025-12-31" and n["base_oe_per_share"] == p["base_oe_per_share"]
    # the content hash covers the record (make_score recomputes it)
    assert n["content_hash"] == E._content_hash(n)
    # the L0 / 5.6 engine: the fiscal year is simply missing
    old = dropped_ccj()["numbers"]
    assert old["latest_period_end"] == "2024-12-31" and old["base_oe_per_share"] != p["base_oe_per_share"]
    assert "annual_from_instance" not in old


def test_accession_in_companyfacts_does_not_block_a_missing_period():
    plain = plain_ccj()
    fx, removed = ccj_restored(keep={("dei", "EntityCommonStockSharesOutstanding")})
    dei = fx["facts"]["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"]
    assert any(e.get("accn") == CCJ_ACC for e in dei)          # companyfacts lists the accession (RDY's shape)
    out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
    n = out["numbers"]
    assert n["annual_from_instance"]["applied"] is True
    assert n["annual_from_instance"]["facts_merged"] == len(removed) - 1 == 21   # the dei fact is never duplicated
    assert strip(n) == strip(plain["numbers"]) and out["rows"] == plain["rows"]


# ---------------------------------------------------------------------------
# 8-10. no candidate, dei mismatch, submissions failure
# ---------------------------------------------------------------------------
def test_no_candidate_adds_no_key():
    plain = plain_ccj()
    # (a) companyfacts already has the reported fiscal year: reportDate - cf_latest = 0 days
    fx = copy.deepcopy(H.load_fixture("CCJ"))
    fx["submissions"] = submissions(CCJ_FILING, CCJ_PRIOR)
    fx["instance_bytes"] = b"<never read/>"
    out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
    assert "annual_from_instance" not in out["numbers"] and out["numbers"] == plain["numbers"]
    dropped = dropped_ccj()
    # (b) the newest annual report is not XBRL; (c) only an amendment is newer than companyfacts
    for filings in ((CCJ_FILING[:5] + (0,), CCJ_PRIOR), (("40-F/A",) + CCJ_FILING[1:], CCJ_PRIOR)):
        fx, _ = ccj_restored()
        fx["submissions"] = submissions(*filings)
        out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
        assert "annual_from_instance" not in out["numbers"], filings
        assert out["numbers"] == dropped["numbers"] and out["rows"] == dropped["rows"], filings
    # the 300-day rule is pure
    sub = submissions(("10-K", "a", "2026-02-01", "2025-12-31", "a.htm", 1))
    assert E.annual_instance_candidate(sub, "2025-03-31") is None              # 275 days: not a new fiscal year
    assert E.annual_instance_candidate(sub, "2024-12-28")["accession"] == "a"   # 368 days
    assert E.annual_instance_candidate(sub, None) is None
    assert E.annual_instance_candidate({"filings": {"recent": {}}}, "2024-12-31") is None


def test_dei_mismatch_records_and_skips():
    dropped = dropped_ccj()
    for kw, field in (({"doc_type": "10-Q"}, "DocumentType"), ({"cik": 1234567}, "EntityCentralIndexKey"),
                      ({"period": "2025-06-30"}, "DocumentPeriodEndDate"), ({"fp": "Q4"}, "DocumentFiscalPeriodFocus")):
        fx, _ = ccj_restored(**kw)
        out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)
        n = out["numbers"]
        rec = n["annual_from_instance"]
        assert rec["applied"] is False and rec["checked"] is True, rec
        assert rec["reason"].startswith(f"instance dei {field} ") and "does not match the submissions record" in rec["reason"], rec
        assert not any(f.startswith("ANNUAL_FROM_INSTANCE") for f in n["fragility_flags"])
        assert out["rows"] == dropped["rows"] and strip(n) == strip(dropped["numbers"]), field
    # an inline-only folder (the fetch finds no instance) and an inline document handed back as the instance
    for extra, why in (({"instance_bytes": None}, "no XBRL 2.1 instance in the filing folder (inline document only)"),
                       ({"instance_bytes": open(os.path.join(HERE, "fixtures", "instance", "tiny_inline.htm"), "rb").read()},
                        "not an XBRL 2.1 instance")):
        fx, _ = ccj_restored(extra=extra)
        rec = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)["numbers"]["annual_from_instance"]
        assert rec["applied"] is False and rec["reason"].startswith(why), rec
    # an instance with no annual operating cash flow at the report date
    fx, removed = ccj_restored()
    fx["instance_bytes"] = instance_xml([r for r in removed if r[1] != "CashFlowsFromUsedInOperatingActivities"],
                                        fx["cik"], "40-F", "2025-12-31", "2025")
    rec = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)["numbers"]["annual_from_instance"]
    assert rec["applied"] is False and rec["reason"] == ("the instance carries no undimensioned annual operating cash "
                                                         "flow for 2025-12-31"), rec


def test_submissions_failure_degrades():
    plain = plain_ccj()

    def boom(_cik):
        raise RuntimeError("EDGAR 503")
    out = run("CCJ", args_for(5), judgment=CCJ_J, patch=lambda E_: setattr(E_, "edgar_submissions", boom))
    assert out["exit"] == 0, out["stdout"][-1000:]
    n = out["numbers"]
    assert n["annual_from_instance"] == {"applied": False, "checked": False,
                                         "reason": "EDGAR submissions unavailable: EDGAR 503"}, n["annual_from_instance"]
    assert strip(n) == strip(plain["numbers"]) and out["rows"] == plain["rows"]
    # the kill switch
    off = run("CCJ", args_for(5), judgment=CCJ_J, patch=lambda E_: setattr(E_, "edgar_submissions", boom),
              env={"DCF_NO_INSTANCE": "1"})
    assert "annual_from_instance" not in off["numbers"] and off["numbers"] == plain["numbers"]


# ---------------------------------------------------------------------------
# 11. the cache: never written under --measure, reused without a fetch, bound to its facts (amendment 6)
# ---------------------------------------------------------------------------
def test_measure_mode_never_writes_the_cache():
    fx, _ = ccj_restored()
    out = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, measure=True, keep_base=True)
    try:
        assert out["numbers"]["annual_from_instance"]["applied"] is True
        assert not os.path.exists(os.path.join(out["base"], "CCJ", "annual_instance.json"))
    finally:
        shutil.rmtree(out["base"], ignore_errors=True)


def _no_fetch(E_):
    def boom(_cik, _filing):
        raise AssertionError("fetch_instance must not run: the cache is current")
    E_.fetch_instance = boom


def test_cache_reused_without_fetch():
    fx, _ = ccj_restored()
    first = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, keep_base=True)
    base = first["base"]
    try:
        path = os.path.join(base, "CCJ", "annual_instance.json")
        doc = json.load(open(path, encoding="utf-8"))
        assert doc["accession"] == CCJ_ACC and doc["cik"] == fx["cik"] and doc["form"] == "40-F", doc
        assert doc["companyfacts_latest_annual_end"] == "2024-12-31" and len(doc["facts"]) == 22, doc
        assert doc["facts_sha256"] == first["numbers"]["annual_from_instance"]["facts_sha256"]
        assert doc["extracted_by"].startswith(f"dcf_engine {E.ENGINE_RELEASE} ")
        mtime = os.path.getmtime(path)
        second = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, patch=_no_fetch, base=base, keep_base=True)
        assert second["numbers"]["annual_from_instance"] == first["numbers"]["annual_from_instance"]
        assert strip(second["numbers"]) == strip(first["numbers"]) and second["rows"] == first["rows"]
        assert os.path.getmtime(path) == mtime, "an unchanged cache must not be rewritten"
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_annual_instance_facts_tamper_refetched_or_refused():
    """Amendment 6 (engine half of T-b): an annual_instance.json whose facts were edited (one value) no longer hashes
    to its facts_sha256 — the engine refetches the instance (the run is the instance's again, and the file is
    rewritten), and records 'edited' when the refetch fails, never reading the edited figure."""
    fx, _ = ccj_restored()
    first = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, keep_base=True)
    base = first["base"]
    try:
        path = os.path.join(base, "CCJ", "annual_instance.json")
        doc = json.load(open(path, encoding="utf-8"))
        ocf = [f for f in doc["facts"] if f["tag"] == "CashFlowsFromUsedInOperatingActivities"][0]
        ocf["val"] = ocf["val"] * 2
        json.dump(doc, open(path, "w", encoding="utf-8"), indent=1)
        failed = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, patch=_no_fetch, base=base, keep_base=True)
        rec = failed["numbers"]["annual_from_instance"]
        assert rec["applied"] is False and rec["reason"].startswith("annual_instance.json does not hash to its facts — edited"), rec
        assert failed["numbers"]["latest_period_end"] == "2024-12-31"            # the edited figure was never read
        again = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, base=base, keep_base=True)
        assert again["numbers"]["annual_from_instance"] == first["numbers"]["annual_from_instance"]
        assert strip(again["numbers"]) == strip(first["numbers"])
        rewritten = json.load(open(path, encoding="utf-8"))
        assert [f["val"] for f in rewritten["facts"] if f["tag"] == "CashFlowsFromUsedInOperatingActivities"] == [ocf["val"] // 2]
        assert rewritten["facts_sha256"] == first["numbers"]["annual_from_instance"]["facts_sha256"]
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---------------------------------------------------------------------------
# 12-13. every fixture unchanged; the hoisted tag lists
# ---------------------------------------------------------------------------
FIXTURES = sorted(f[:-len(".json.gz")] for f in os.listdir(H.FIXTURES) if f.endswith(".json.gz"))


def test_existing_fixtures_unchanged():
    assert len(FIXTURES) == 23, FIXTURES
    for t in FIXTURES:
        out = run(t, args_for(5))
        n = out["numbers"]
        assert n is not None, (t, out["stdout"][-500:])
        assert "annual_from_instance" not in n, t
        assert not any(str(f).startswith("ANNUAL_FROM_INSTANCE") for f in n.get("fragility_flags") or []), t
    for t in ("CCJ", "VOD", "HALO"):
        a = run(t, args_for(5))
        b = run(t, args_for(5), env={"DCF_NO_INSTANCE": "1"})
        assert a["numbers"] == b["numbers"] and a["rows"] == b["rows"], t
    # ...while the gate is open on the trigger shape (the same fixture with its FY missing and a candidate listed),
    # and the kill switch closes it there
    fx, _ = ccj_restored()
    assert run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx)["numbers"]["annual_from_instance"]["applied"] is True
    off = run("CCJ", args_for(5), judgment=CCJ_J, fixture=fx, env={"DCF_NO_INSTANCE": "1"})
    assert "annual_from_instance" not in off["numbers"] and off["numbers"] == dropped_ccj()["numbers"]


def test_tag_hoist_is_identity():
    IF = "ifrs-full"
    assert E.ENGINE_OCF_TAGS == ["NetCashProvidedByUsedInOperatingActivities",
                                 "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                                 (IF, "CashFlowsFromUsedInOperatingActivities"),
                                 (IF, "CashFlowsFromUsedInOperatingActivitiesContinuingOperations")]
    assert E.ENGINE_SBC_TAGS == ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense",
                                 (IF, "AdjustmentsForSharebasedPayments"),
                                 (IF, "ExpenseFromSharebasedPaymentTransactionsWithEmployees")]
    assert E.ENGINE_SHARES_DILUTED_TAGS == ["WeightedAverageNumberOfDilutedSharesOutstanding",
                                            "WeightedAverageNumberOfSharesOutstandingDiluted",
                                            "WeightedAverageNumberOfSharesOutstandingBasic",
                                            (IF, "AdjustedWeightedAverageShares"), (IF, "WeightedAverageShares")]
    assert E.BASIC_SHARE_TAGS == {"WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageShares"}
    assert E.DILUTED_SHARE_TAGS == {"WeightedAverageNumberOfDilutedSharesOutstanding",
                                    "WeightedAverageNumberOfSharesOutstandingDiluted", "AdjustedWeightedAverageShares",
                                    "OVERRIDE"}
    assert E.DILUTED_ONLY_TAGS == ["WeightedAverageNumberOfDilutedSharesOutstanding",
                                   "WeightedAverageNumberOfSharesOutstandingDiluted", (IF, "AdjustedWeightedAverageShares")]
    # main() reads these very lists: the recorded runs' used_tags come out the same (the fixtures that still match
    # their folder's recorded run: CCJ IFRS 40-F, APP and STZ us-gaap 10-K)
    # (APP's sbc used tag moved with 5.5's SBC reconciliation, so its sbc entry is not compared)
    for t, j, keys in (("CCJ", CCJ_J, ("ocf", "sbc", "shares_diluted")), ("APP", {}, ("ocf", "shares_diluted")),
                       ("STZ", {}, ("ocf", "shares_diluted"))):
        rec = recorded_matching_fixture(t)
        out = run(t, args_for(5), judgment=j)
        for k in keys:
            assert out["numbers"]["used_tags"][k] == rec["used_tags"][k], (t, k, out["numbers"]["used_tags"][k])
    src = open(os.path.join(SYS, "dcf_engine.py"), encoding="utf-8").read()
    for line in ('"ocf": ENGINE_OCF_TAGS,', '"sbc": ENGINE_SBC_TAGS,', '"shares_diluted": ENGINE_SHARES_DILUTED_TAGS,'):
        assert line in src, line


# ---------------------------------------------------------------------------
# Amendment 7: the merged entries reach the acquired-IPR&D detection
# ---------------------------------------------------------------------------
def test_merged_fy_reaches_the_iprd_detection():
    args = args_for(7)
    plain = run("HALO", args, judgment=HALO_J)
    assert plain["exit"] == 0, plain["stdout"][-1500:]
    p = plain["numbers"]
    assert p["iprd_adjustment"] and p["iprd_adjustment"]["total"] == 284887000, p["iprd_adjustment"]
    fx, removed = drop_fy(H.load_fixture("HALO"), "2025-12-31")
    assert any(r[1] == "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff" for r in removed)
    fx["instance_bytes"] = instance_xml(removed, fx["cik"], "10-K", "2025-12-31", "2025")
    fx["instance_url"] = "https://www.sec.gov/Archives/edgar/data/1159036/000115903626000024/halo-20251231_htm.xml"
    fx["submissions"] = submissions(("10-K", "0001159036-26-000024", "2026-02-17", "2025-12-31", "halo-20251231.htm", 1))
    out = run("HALO", args, judgment=HALO_J, fixture=fx)
    assert out["exit"] == 0, out["stdout"][-1500:]
    n = out["numbers"]
    assert n["annual_from_instance"]["applied"] is True and n["annual_from_instance"]["form"] == "10-K"
    assert n["iprd_adjustment"] == p["iprd_adjustment"], (n["iprd_adjustment"], p["iprd_adjustment"])
    assert strip(n) == strip(p) and out["rows"] == plain["rows"]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and fn.__module__ == __name__:
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
