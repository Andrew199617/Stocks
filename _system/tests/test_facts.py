#!/usr/bin/env python3
"""facts.json in make_score.py (engine 5.7; Andrew's ruling R3 of 2026-10-19 — strict quoting; design 02 §3-§5,
§7-§8, §10 tests 9-22; L2 rebase A1, A3, A5, A6, A10, A13-A18; 10 §(l)).
Run: python _system/tests/test_facts.py (or python -m pytest _system/tests). Offline: make_score.py runs as a
subprocess on synthetic folders in a temp STOCKS_BASE (test_make_score_55's Run harness, fail-loud engine / ttm
stand-ins, the registry redirected); the folder files come from the trimmed APP copies in fixtures/facts/APP/.
The judgments are written verbatim (Run(judgment_text=...)) so the G16 helper (rulings57) never touches them.

Each test fails on the code before the lane (e22e814 ignores facts.json, renders none of the new key_numbers lines,
traces no reason and has no facts.check / resolve):
 9 schema refusals (02 §8.2 texts) — make_score refuses and writes nothing;
10 the folder path grammar on real structures (the eleven 02 §4.1 examples; integer index, ttm without @end, unknown
   period, null value) and the worked examples in _system/examples/facts/;
11 a folder fact that does not equal its file refuses with both values, one that does is "verified";
12 drift on a rebuild is recorded, not refused; an edited declaration is authoring again;
13 a non-folder fact repeating a folder figure refuses; a 2-digit one is a warning; an adjusted figure is shown beside
   the folder's;
14 calc facts reproduce (growth, ratio, mid, cagr); a wrong value or a kind stronger than an operand refuses;
15 the influence rules on 5.7 runs (third-party only, unknown id, untraced, no number, missing used_for tag, a plain
   pin), never on a 5.5 record; the registry tier_override event carries the cited facts;
16 STALE guidance is marked, never blocking (older than the filing the engine used; superseded by actuals);
17 "Declared facts (not engine output)" is the last section and formats every unit;
18 the hashes: key_numbers_sha256 is the written file's, facts_sha256 survives reformatting, dcf_content_hash is #47's;
19 the declared_facts registry event keeps its first date; a cited-nothing tier_override keeps its date (A6);
20 a legacy rebuild without facts is unchanged except for additive key_numbers lines (A1: Filed history after Growth);
21 saved method runs are rendered and hash-checked (refused on 5.7, warned on older runs);
22 the previous-score block;
A17 a citation added after the engine run needs no engine re-run (IPR&D record: no IPRD_JUDGMENT_CHANGED), keeps
    dcf_content_hash and the live-figure bindings, and re-dates the tier_override event;
A18 a registry holding declared_facts / cited tier_override events and another ticker's deferred-payment event loads
    and survives; a declared_facts event with a stray `periods` key is refused (the name collision rule);
plus check_influence's trace_only / require_anchor (10 §(l)) and misfit_notch_reason, and the engine lines.
"""
import contextlib
import copy
import csv
import difflib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import make_score as M  # noqa: E402
import facts as F  # noqa: E402
import check_quotes as CQ  # noqa: E402
from test_make_score_55 import Run, _numbers, _judgment, _stamp, T, CUR  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "facts", "APP")
EXAMPLES = os.path.join(SYS, "examples", "facts")
FIL = {"form": "10-K", "accession": "0000999001-26-000010", "section": "Item 7 MD&A — Key metrics", "filed": "2026-02-19"}
REL = {"form": "8-K", "accession": "0000999001-26-000057", "exhibit": "99.1", "filed": "2026-08-05"}
TP = {"url": "https://example.com/consensus", "publisher": "Example Wire", "published": "2026-09-28"}


def F1(**kw):   # release, adjusted revenue (differs from the folder's GAAP 1,923,686,000)
    return dict({"id": "F1", "label": "Q2 2026 adjusted revenue", "value": 1.95e9, "unit": "USD", "scale": "B",
                 "precision": 2, "period": "Q2 FY2026", "kind": "release", "type": "actual", "metric": "revenue",
                 "source": dict(REL), "snippet": "Adjusted revenue of $1.95 billion, up 55% year over year",
                 "used_for": ["context", "tier_override"]}, **kw)


def F2(**kw):   # folder, verified against fundamentals.json
    return dict({"id": "F2", "label": "FY2025 share repurchases", "value": 2191944000, "unit": "USD", "scale": "",
                 "precision": 0, "period": "FY2025", "kind": "folder", "type": "actual", "metric": "buybacks",
                 "source": {"path": "fundamentals.json:annual[FY2025].buybacks"}, "used_for": ["flag_resolution"]}, **kw)


def F3(**kw):   # release guidance range
    return dict({"id": "F3", "label": "FY2026 revenue guidance", "value": [3.18e9, 3.22e9], "unit": "USD",
                 "scale": "B", "precision": 2, "period": "FY2026", "kind": "release", "type": "guidance",
                 "source": dict(REL), "snippet": "raises full-year revenue outlook to $3.18 billion to $3.22 billion",
                 "used_for": ["guidance_check"]}, **kw)


def F4(**kw):   # filing metric
    return dict({"id": "F4", "label": "net revenue retention", "value": 1.26, "unit": "pct", "precision": 0,
                 "period": "FY2025", "kind": "filing", "type": "metric", "metric": "net_revenue_retention",
                 "source": dict(FIL), "snippet": "our dollar-based net revenue retention rate was 126%",
                 "used_for": ["moat:retention"]}, **kw)


def F5(**kw):   # third-party estimate
    return dict({"id": "F5", "label": "analyst consensus FY2027 EPS", "value": 4.1, "unit": "USD/share",
                 "precision": 2, "period": "FY2027", "kind": "third_party", "type": "estimate", "source": dict(TP),
                 "snippet": "consensus calls for $4.10 a share in fiscal 2027", "used_for": ["scenarios"]}, **kw)


def F6(**kw):   # calc: the synthetic record's price $20 against IV@15 $25
    return dict({"id": "F6", "label": "price discount to weighted IV@15%", "value": -0.2, "unit": "pct",
                 "precision": 1, "period": "2026-10-18", "kind": "folder", "type": "actual",
                 "calc": {"op": "growth", "of": ["dcf_numbers.json:price", "dcf_numbers.json:iv_at_15"]},
                 "used_for": ["context"]}, **kw)


def _doc(*facts, **extra):
    d = {"schema": 1, "ticker": T, "facts": [copy.deepcopy(f) for f in facts]}
    d.update(extra)
    return d


def _fixture_files():
    out = {}
    for name in sorted(os.listdir(FIX)):
        with open(os.path.join(FIX, name), encoding="utf-8", newline="") as f:
            out[f"{T}/{name}"] = f.read()
    return out


class S:
    """One make_score run on a synthetic 5.7 (or older) folder with the APP fixture files and a facts.json."""

    def __init__(self, n=None, j=None, facts=None, files=True, prior_score=None, registry=None, extra=None):
        fl = _fixture_files() if files else {}
        if facts is not None:
            fl[f"{T}/facts.json"] = facts
        fl.update(extra or {})
        n = n if n is not None else _numbers()
        j = j if j is not None else _judgment(n)
        self.r = Run(n, judgment_text=json.dumps(j, indent=1, ensure_ascii=False) + "\n", files=fl,
                     prior_score=prior_score)
        if registry is not None:
            with open(self.r.registry, "w", encoding="utf-8") as f:
                json.dump({"entries": registry}, f, indent=1)

    def run(self):
        self.before = {name: self._bytes(name) for name in ("score.json", "key_numbers.md", "judgment.json")}
        self.r.run()
        return self

    def _bytes(self, name):
        p = os.path.join(self.r.folder, name)
        return open(p, "rb").read() if os.path.exists(p) else None

    @property
    def rc(self):
        return self.r.rc

    @property
    def err(self):
        return self.r.err

    def score(self):
        return self.r.score()

    def key(self):
        return self.r.key()

    def write(self, name, obj):
        with open(os.path.join(self.r.folder, name), "w", encoding="utf-8", newline="" if isinstance(obj, str) else None) as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj, indent=1, ensure_ascii=False))

    def close(self):
        self.r.close()


@contextlib.contextmanager
def scored(**kw):
    s = S(**kw).run()
    try:
        yield s
    finally:
        s.close()


def _refuses(s, needle):
    """Refused with needle, and nothing written: score.json, key_numbers.md and judgment.json are as they were."""
    assert s.rc == 1 and "REFUSED" in s.err and needle in s.err, (s.rc, s.err[-1500:], needle)
    after = {name: s._bytes(name) for name in s.before}
    assert after == s.before, ("a refusal wrote a file", [k for k in after if after[k] != s.before[k]])


def _check(doc, folder=FIX, n=None, prior_sha=None):
    """facts.check -> (FactsCheck, None) or (None, refusal text)."""
    try:
        return F.check(doc, folder, T, n=n if n is not None else _numbers(), prior_sha=prior_sha), None
    except F.FactsRefusal as e:
        return None, str(e)


# ---------------------------------------------------------------- 9. schema
def test_schema_refusals():
    """02 §8.2: one case per schema rule, the exact text; make_score refuses a malformed facts.json and writes
    nothing (before the lane it ignored facts.json and scored)."""
    cases = [
        (_doc(dict(F1(), id="X1")), "facts.json: id X1 is not of the form F<n>"),
        (_doc(F1(), F1()), "facts.json: duplicate fact id F1"),
        (_doc({k: v for k, v in F1().items() if k != "id"}), "facts.json: fact #1 has no id"),
        (dict(_doc(F1()), schema=2), "facts.json: schema must be 1"),
        (dict(_doc(F1()), ticker="APP"), "facts.json: ticker APP is not this folder's TST"),
        (dict(_doc(), facts={"F1": F1()}), 'facts.json: "facts" must be a list of objects'),
        (_doc(F1(kind="news")), "facts.json F1: kind must be one of folder, filing, release, third_party (got 'news')"),
        (_doc(F1(type="rumour")), "facts.json F1: type must be one of actual, guidance, estimate, metric, event"),
        (_doc(F3(value=[3.22e9, 3.18e9])), "facts.json F3: value must be a number or a [low, high] pair of numbers (low ≤ high)"),
        (_doc(F1(unit="dollars")), "facts.json F1: unit must be an ISO currency code, '<CCY>/share', 'pct', 'pp', 'bps', 'x' or 'count' (got 'dollars')"),
        (_doc(F1(scale="bn")), 'facts.json F1: scale must be one of "", K, M, B, T'),
        (_doc(F1(precision=7)), "facts.json F1: precision must be an integer 0–6"),
        (_doc(F1(period="Q2 2026")), "facts.json F1: period 'Q2 2026' is not recognised — use FY2025, Q2 FY2026, H1 FY2026, 9M FY2026, TTM 2026-06-30, CY2026 or a YYYY-MM-DD instant"),
        (_doc(F4(source=dict(FIL, accession="12345"))), "facts.json F4 (filing): source needs form, accession (##########-##-######), section and filed (YYYY-MM-DD)"),
        (_doc(F1(source=dict(REL, form="10-Q"))), "facts.json F1 (release): source needs form 8-K or 6-K, accession, exhibit and filed"),
        (_doc(F5(source=dict(TP, url="http://example.com"))), "facts.json F5 (third_party): source needs url (https://…), publisher and published (YYYY-MM-DD)"),
        (_doc({k: v for k, v in F4().items() if k != "snippet"}), "facts.json F4: a filing fact needs a snippet — the source's own words, under 25 words, containing the number"),
        (_doc(F4(snippet="our " + "very " * 21 + "rate was 126%")), "facts.json F4: snippet has 25 words — keep it under 25 (R3)"),
        (_doc(F4(snippet="our dollar-based net revenue retention rate was 125%")), "facts.json F4: snippet does not contain the declared value 126% at the snippet's own precision"),
        (_doc(F5(used_for=["tier_override"])), "facts.json F5: used_for tier_override is not allowed for a third_party fact — third-party facts calibrate scenarios and give context only (R3)"),
        (_doc(F4(used_for=["moat:market_position"])), "market_position is not a moat pillar since the M1b amendment"),
        (_doc(F1(), not_quantities=[{"text": "rounded to $0.1M", "reason": "a rounding note"}]), "facts.json: not_quantities entry 'rounded to $0.1M' is a quantity (money) — declare it as a fact or reword it"),
        (_doc(F2(value=[1.0, 2.0])), "facts.json F2 (folder): a [low, high] range cannot be a folder fact"),
    ]
    for doc, want in cases:
        fc, why = _check(doc)
        assert fc is None and why is not None and want in why, (want, why)
    assert _check(_doc(F1(), not_quantities=[{"text": "Paragon 28", "reason": "a company name"}]))[0] is not None
    # end to end: a malformed declaration refuses before any write (and the old make_score scored it)
    for doc, want in (cases[0], cases[6], cases[18]):
        with scored(facts=doc) as s:
            _refuses(s, want)
    with scored(facts="{not json") as s:
        _refuses(s, "facts.json: not valid JSON (")


# ---------------------------------------------------------------- 10. path grammar
PATHS = {   # 02 §4.1's examples on APP (the fixture is a trimmed copy of APP's committed files)
    "financials_history.csv:ocf[FY2025]": 3971094000,
    "statements.json:cashflow.ocf.annual[FY2025]": 3971094000,
    "statements.json:income.revenue.quarterly[Q2 FY2026]": 1923686000,
    "statements.json:income.revenue.ttm@2026-06-30": 6829124000,
    "fundamentals.json:annual[FY2025].buybacks": 2191944000,
    "fundamentals.json:quarterly[Q2 FY2026].revenue_yoy": 0.5282461863080474,
    "fundamentals.json:ttm.sbc@2026-06-30": 283176000,
    "segments.json:tables[geography/Revenues/annual].rows[country:US].values[FY2025]": 2827248000,
    "profile.json:about.employees.count": 898,
    "ttm.json:ttm_ocf": 4527589000,
    "ttm.json:inputs.sbc.ytd_current": 168981000,
}


def test_folder_paths_resolve_on_real_structures():
    """02 §4.1 (rebase A9, D1): the eleven example paths resolve to APP's values with their units; an integer index,
    a ttm selector without @end, an unknown period, a null value, a TTM that moved, an unknown file and a
    dcf_numbers.json path outside a calc are refused with their reason; the worked examples verify."""
    fol = F.Folder(FIX)
    units = {"fundamentals.json:quarterly[Q2 FY2026].revenue_yoy": "pct", "profile.json:about.employees.count": "count"}
    for p, v in PATHS.items():
        r = F.resolve(p, fol)
        assert abs(r.value - v) <= 1e-6 * max(1, abs(v)) and r.unit == units.get(p, "USD"), (p, r.value, r.unit)
    assert F.resolve("financials_history.csv:ocf[2025-12-31]", fol).value == 3971094000
    assert F.resolve("statements.json:income.revenue.annual[FY2025]", fol).filed == "2026-02-19"
    for p, why, status in (("statements.json:income.revenue.annual[0]", "integer indexes are not accepted", "unresolved"),
                           ("statements.json:income.revenue.ttm", "must carry @<end>", "unresolved"),
                           ("statements.json:income.revenue.annual[FY1999]", "period FY1999 is not in statements.json", "unresolved"),
                           ("financials_history.csv:debt_current[FY2025]", "value is null", "unresolved"),
                           ("statements.json:income.revenue.ttm@2026-03-31", "TTM in statements.json now ends 2026-06-30", "period_moved"),
                           ("fundamentals.json:ttm.sbc", "must carry @<end>", "unresolved"),
                           ("annual.json:x", "unknown file annual.json", "unresolved"),
                           ("dcf_numbers.json:iv_at_15", "allowed only as a calc operand", "unresolved"),
                           ("segments.json:tables[geography/Revenues/annual].rows[country:XX].values[FY2025]", "row country:XX", "unresolved")):
        try:
            F.resolve(p, fol)
            raise AssertionError(f"{p} resolved")
        except F.PathError as e:
            assert why in e.why and e.status == status, (p, e.why, e.status)
    try:
        F.resolve("statements.json:income.revenue.annual[FY2025]", F.Folder(os.path.join(FIX, "nowhere")))
    except F.PathError as e:
        assert e.status == "file_missing", e.status
    # the worked examples (_system/examples/facts/): TST's schema is valid; APP's folder facts verify against APP
    with open(os.path.join(EXAMPLES, "TST", "facts.json"), encoding="utf-8") as f:
        tst = json.load(f)
    assert F.validate(tst, "TST") is None, F.validate(tst, "TST")
    assert {f["kind"] for f in tst["facts"]} == set(F.KINDS) and any("calc" in f for f in tst["facts"])
    with open(os.path.join(EXAMPLES, "APP_folder_facts.json"), encoding="utf-8") as f:
        app = json.load(f)
    fc = F.check(dict(app, ticker="APP"), FIX, "APP", n={"latest_period_end": "2025-12-31"})
    assert fc.summary()["verified"] == [x["id"] for x in app["facts"]], fc.summary()


# ---------------------------------------------------------------- 11. verification
def test_folder_fact_mismatch_refuses_and_match_verifies():
    """02 §4.2-§4.3: off by more than half a unit of the declared precision -> refused with both values; within ->
    "— verified" in key_numbers.md and declared_facts.verified; a unit that is not the file's -> refused."""
    with scored(facts=_doc(F2(value=2191945000))) as s:
        _refuses(s, "facts.json F2 (folder): value $2,191,945,000 does not equal fundamentals.json:annual[FY2025].buybacks "
                    "= $2,191,944,000 at the declared precision (± 2.69")   # 0.5 at precision 0, plus 1e-9 relative
    with scored(facts=_doc(F2(value=2.19e9, scale="B", precision=2))) as s:
        assert s.rc == 0, s.err[-1500:]
        assert s.score()["declared_facts"]["verified"] == ["F2"], s.score()["declared_facts"]
        assert ("- F2 · $2.19B — “FY2025 share repurchases” · FY2025 · actual (series buybacks) · folder "
                "fundamentals.json:annual[FY2025].buybacks — verified (as filed 2026-02-19)") in s.key(), s.key()[-1500:]
    with scored(facts=_doc(F2(unit="EUR"))) as s:
        _refuses(s, "facts.json F2 (folder): unit EUR does not match fundamentals.json's USD")
    with scored(facts=_doc(F2(source={"path": "fundamentals.json:annual[FY2031].buybacks"}))) as s:
        _refuses(s, "facts.json F2 (folder): path fundamentals.json:annual[FY2031].buybacks does not resolve — period "
                    "FY2031 is not in fundamentals.json annual")


# ---------------------------------------------------------------- 12. drift
def test_drift_on_rebuild_is_recorded_not_refused():
    """02 §4.7 (D1 rebuild safety): scored once; the folder file then changes (the SEC enrichment, a restatement) and
    a rebuild with the same facts.json scores, recording the drift and printing DRIFTED; editing facts.json makes it
    authoring again, and the stale figure refuses."""
    s = S(facts=_doc(F2())).run()
    try:
        assert s.rc == 0, s.err[-1500:]
        fu = json.load(open(os.path.join(s.r.folder, "fundamentals.json"), encoding="utf-8"))
        for r in fu["annual"]:
            if r["fy"] == "2025":
                r["buybacks"] = 2200000000
        s.write("fundamentals.json", fu)
        s.run()
        assert s.rc == 0, s.err[-1500:]
        dfs = s.score()["declared_facts"]
        assert dfs["drift"] == [{"id": "F2", "status": "mismatch", "path": "fundamentals.json:annual[FY2025].buybacks",
                                 "declared": 2191944000, "file_value": 2200000000.0}], dfs["drift"]
        assert "— DRIFTED: fundamentals.json:annual[FY2025].buybacks now reads $2,200,000,000" in s.key()
        assert [f["status"] for f in dfs["facts"]] == ["drifted"]
        s.write("facts.json", _doc(F2(label="FY2025 buybacks")))
        s.run()
        _refuses(s, "facts.json F2 (folder): value $2,191,944,000 does not equal")
    finally:
        s.close()


# ---------------------------------------------------------------- 13. folder duplicates
def test_non_folder_duplicate_of_folder_value():
    """02 §4.5: a release fact equal to a folder figure for the same period refuses (metric-keyed, and metric-blind at
    >= 4 significant digits); a 2-digit equality is a warning; a metric-keyed adjusted figure that differs is recorded
    and printed beside the folder's."""
    dup = F1(value=1923686000, scale="", precision=0, snippet="Revenue of $1,923,686,000 for the quarter")
    with scored(facts=_doc(dup)) as s:
        _refuses(s, "facts.json F1 (release): the value equals statements.json:income.revenue.quarterly[Q2 FY2026] = "
                    "$1,923,686,000 for the same period — a number available in a folder file must be declared kind "
                    "\"folder\" with that path (R3)")
    blind = dict(dup)
    blind.pop("metric")
    fc, why = _check(_doc(blind))
    assert fc is None and "the value equals" in why and "quarterly[Q2 FY2026]" in why, why
    small = F1(value=1.9e9, precision=1, snippet="Revenue of $1.9 billion")
    small.pop("metric")
    with scored(facts=_doc(small)) as s:
        assert s.rc == 0, s.err[-1500:]
        pd = s.score()["declared_facts"]["possible_folder_duplicates"]
        assert {"id": "F1", "path": "statements.json:income.revenue.quarterly[Q2 FY2026]",
                "file_value": 1923686000.0} in pd, pd
        assert "  - possible folder duplicate: statements.json:income.revenue.quarterly[Q2 FY2026] = $1,923,686,000" in s.key()
    with scored(facts=_doc(F1())) as s:
        assert s.rc == 0, s.err[-1500:]
        fcp = s.score()["declared_facts"]["folder_counterparts"]
        assert fcp == [{"id": "F1", "path": "statements.json:income.revenue.quarterly[Q2 FY2026]",
                        "file_value": 1923686000.0}], fcp
        assert ("  - folder figure for the same period: statements.json:income.revenue.quarterly[Q2 FY2026] = "
                "$1,923,686,000") in s.key()


# ---------------------------------------------------------------- 14. calc
def test_calc_facts():
    """02 §4.6: growth / ratio / mid / cagr reproduce from fact ids and paths (dcf_numbers.json and folder files);
    a wrong value refuses; a calc fact's kind is its weakest operand's."""
    rev25, rev22 = 5480717000, 2817058000
    cagr = (rev25 / rev22) ** (1 / 3) - 1
    good = [F6(),
            {"id": "F7", "label": "guidance midpoint", "value": 3.2e9, "unit": "USD", "scale": "B", "precision": 2,
             "period": "FY2026", "kind": "release", "type": "guidance", "calc": {"op": "mid", "of": ["F3"]},
             "used_for": ["guidance_check"]},
            {"id": "F8", "label": "FY2022-25 revenue CAGR", "value": round(cagr, 4), "unit": "pct", "precision": 2,
             "period": "FY2025", "kind": "folder", "type": "actual",
             "calc": {"op": "cagr", "of": ["financials_history.csv:revenue[FY2025]", "financials_history.csv:revenue[FY2022]"],
                      "years": 3}, "used_for": ["context"]},
            {"id": "F9", "label": "buybacks over FY2025 OCF", "value": 0.552, "unit": "pct", "precision": 1,
             "period": "FY2025", "kind": "folder", "type": "actual",
             "calc": {"op": "ratio", "of": ["F2", "statements.json:cashflow.ocf.annual[FY2025]"]}, "used_for": ["context"]}]
    fc, why = _check(_doc(F2(), F3(), *good))
    assert fc is not None, why
    assert [fc.status[x["id"]] for x in good] == ["verified"] * 4, fc.status
    with scored(facts=_doc(F2(), F3(), *good)) as s:
        assert s.rc == 0, s.err[-1500:]
        assert "- F6 · -20.0% — “price discount to weighted IV@15%” · 2026-10-18 · actual · calc growth(dcf_numbers.json:price, dcf_numbers.json:iv_at_15) — verified" in s.key()
    fc, why = _check(_doc(F6(value=-0.25)))
    assert fc is None and why == "facts.json F6: calc growth does not reproduce: computed -20.0%, declared -25.0% (± 0.050 points)", why
    weak = {"id": "F10", "label": "consensus over price", "value": 0.205, "unit": "x", "precision": 3, "period": "FY2027",
            "kind": "filing", "type": "estimate", "calc": {"op": "ratio", "of": ["F5", "dcf_numbers.json:price"]},
            "used_for": ["scenarios"]}
    fc, why = _check(_doc(F5(), weak))
    assert fc is None and why == "facts.json F10: calc kind must be third_party (its weakest operand)", why
    fc, why = _check(_doc(F5(), dict(weak, kind="third_party")))
    assert fc is not None and fc.status["F10"] == "verified", why
    cyc = [dict(F6(), calc={"op": "ratio", "of": ["F11", "dcf_numbers.json:price"]}),
           {"id": "F11", "label": "a circular figure", "value": 1.0, "unit": "x", "precision": 0, "period": "FY2025", "kind": "folder",
            "type": "actual", "calc": {"op": "ratio", "of": ["F6", "dcf_numbers.json:price"]}, "used_for": ["context"]}]
    fc, why = _check(_doc(*cyc))
    assert fc is None and "cycle" in why, why


# ---------------------------------------------------------------- 15. influence
def _over(reason, release=None, **jkw):
    n = _numbers() if release is None else _numbers(release=release)
    return n, _judgment(n, tier_override="C", tier_override_reason=reason, **jkw)


def test_influence_rules_on_57_runs():
    """02 §5 on 5.7 runs: a tier_override_reason resting only on a third-party fact, citing an undeclared id, quoting
    an untraced number, carrying no number, or citing a fact without used_for tier_override refuses; one citing a
    release fact tagged tier_override scores and the registry event carries the cited facts; a plain pin's reason /
    source traces too but needs no number; the same judgments on a 5.5.0 record score (D1)."""
    docs = _doc(F1(), F4(), F5())
    for reason, needle in (("consensus EPS $4.10 a share [F5]", "judgment.json tier_override_reason rests only on third-party facts (F5) — it needs an engine figure or a filing / release / folder fact (R3)"),
                           ("adjusted revenue $1.95B [F9]", "judgment.json tier_override_reason cites F9, which facts.json does not declare"),
                           ("margins near 31.4% [F1]", "judgment.json tier_override_reason quotes 31.4% that is neither an engine figure nor a fact it cites — declare it in facts.json and cite it as [F#]"),
                           ("the risk is high", "judgment.json tier_override_reason carries no number — the reason must name the figure it rests on"),
                           ("retention at 126% [F4]", "judgment.json tier_override_reason cites F4, but F4 does not list used_for tier_override")):
        n, j = _over(reason)
        with scored(n=n, j=j, facts=docs) as s:
            _refuses(s, needle)
        n, j = _over(reason, release="5.5.0")
        with scored(n=n, j=j, facts=docs) as s:
            assert s.rc == 0, (reason, s.err[-1500:])
    n, j = _over("adjusted revenue $1.95B [F1] against a weighted IRR of 17.00%")
    with scored(n=n, j=j, facts=docs) as s:
        assert s.rc == 0, s.err[-1500:]
        ev = [e for e in s.r.entries() if e.get("event") == "tier_override"]
        assert ev and ev[0]["facts"] == [{"id": "F1", "kind": "release", "value": 1.95e9, "unit": "USD",
                                          "period": "Q2 FY2026", "source": REL}], ev
        assert s.score()["declared_facts"]["influence"] == {
            "tier_override_reason": {"facts": ["F1"], "engine_numbers": 1, "third_party_only": False}}
        dfe = [e for e in s.r.entries() if e.get("event") == "declared_facts"]
        assert dfe and dfe[0]["influencing"] == ["F1"] and dfe[0]["by_kind"] == {"release": 1, "filing": 1, "third_party": 1}
    # a plain base_override pin (rebase I13): its numbers trace, but it needs none
    n = _numbers(base_oe_per_share=3.25, base_source="agent_supplied_ttm_override")
    n["inputs"] = dict(n["inputs"], base_oe_ps_arg=3.25, base_pin_source="base_oe_ps_arg", base_basis_window={"window": "fy"})
    for bo, ok in (({"value": 3.25, "kind": "estimate", "source": "the FY2025 10-K", "reason": "normalized base",
                     "basis_window": {"window": "fy"}}, True),
                   ({"value": 3.25, "kind": "estimate", "source": "FY2025 OCF $7.31B less capex", "reason": "normalized",
                     "basis_window": {"window": "fy"}}, False)):
        with scored(n=n, j=_judgment(n, base_override=bo), facts=docs) as s:
            if ok:
                assert s.rc == 0, s.err[-1500:]
            else:
                _refuses(s, "judgment.json base_override quotes $7.31B that is neither an engine figure nor a fact it cites")


def _influence(field, text, fc, n=None, folder=FIX, **kw):
    """check_influence in-process -> the refusal text, or None (and fc's influence record)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            M.check_influence(field, text, F.parse_refs(text), fc, folder, n if n is not None else _stamp(_numbers()), **kw)
    except SystemExit:
        return buf.getvalue()
    return None


def test_trace_only_require_anchor_and_the_notch_reason():
    """10 §(l): a number matching trace_only is accepted but never counts as an engine match, the values at
    trace_only's dcf_numbers.json paths leave the engine set; require_anchor refuses a reason anchored only there,
    and accepts one anchored by `extra` or by a cited non-third-party fact tagged for the field. misfit_notch_reason
    (L1's field) follows the same rules with its own used_for tag; a pre-5.7 record is never checked."""
    fc, why = _check(_doc(F1(), F4(used_for=["misfit_notch", "erosion_rebuttal"]), F5()))
    assert fc is not None, why
    fld = "moat_scorecard.erosion_rebuttal"
    assert _influence(fld, "trend -6.40pp", fc, trace_only=[0.064]) is None
    why = _influence(fld, "trend -6.40pp", fc, trace_only=[0.064], require_anchor=True)
    assert why and "traces only through figures that restate the measurement" in why, why
    assert _influence(fld, "trend -6.40pp; retention 126% [F4]", fc, trace_only=[0.064], require_anchor=True) is None
    assert _influence(fld, "trend -6.40pp; volumes -3.10pp", fc, trace_only=[0.064], extra=[0.031],
                      require_anchor=True) is None
    # dcf_numbers.json paths in trace_only remove those figures from the engine set (17.00% is the record's weighted,
    # base-case and every scenario IRR)
    paths = ["implied_irr_weighted", "implied_irr_base", "scenarios"]
    why = _influence(fld, "IRR 17.00% at hold 2", fc, trace_only=paths, require_anchor=True)
    assert why and "traces only through figures" in why, why
    assert _influence(fld, "IRR 17.00% at hold 2", fc, trace_only=paths) is None
    assert _influence(fld, "IRR 17.00% at hold 2", fc, require_anchor=True) is None
    why = _influence("misfit_notch_reason", "payable-earnings measure 126% [F4]", fc)
    assert why is None, why
    assert fc.influence["misfit_notch_reason"] == {"facts": ["F4"], "engine_numbers": 0, "third_party_only": False}
    why = _influence("misfit_notch_reason", "adjusted revenue $1.95B [F1]", fc)
    assert why and "cites F1, but F1 does not list used_for misfit_notch" in why, why
    assert _influence("misfit_notch_reason", "x 99.9%", fc, n=_stamp(_numbers(release="5.6.0"))) is None


# ---------------------------------------------------------------- 16. staleness
def test_stale_guidance_is_marked_not_blocking():
    """02 §8.4 (rebase A8): guidance dated before the filing the engine used (the run's TTM reaches the Q2 FY2026
    10-Q filed 2026-08-05) is STALE — recorded, printed, a check_quotes warning — and scores; guidance for a period
    that has already reported is "superseded"."""
    import dcf_engine as E
    with open(os.path.join(FIX, "ttm.json"), encoding="utf-8") as f:
        tt = json.load(f)
    n = _numbers(ttm_inputs=E.ttm_inputs_record(tt))   # the run read the fixture's ttm.json (YTD to 2026-06-30)
    assert n["ttm_inputs"]["ytd_current_period"] == ["2026-01-01", "2026-06-30"], n["ttm_inputs"]
    old = F3(source=dict(REL, filed="2026-05-01"))
    past = F3(id="F7", period="FY2025", label="FY2025 revenue guidance", source=dict(REL, filed="2025-11-04"))
    with scored(n=n, facts=_doc(old, past)) as s:
        assert s.rc == 0, s.err[-1500:]
        dfs = s.score()["declared_facts"]
        assert dfs["latest_filing_used"] == {"period_end": "2026-06-30", "filed": "2026-08-05", "form": "10-Q",
                                             "basis": "statements.json"}, dfs["latest_filing_used"]
        st = {x["id"]: x["why"] for x in dfs["stale"]}
        assert st["F3"] == "older than the 10-Q filed 2026-08-05 the engine used", st
        assert st["F7"].startswith("superseded by reported actuals"), st
        assert "· STALE: older than the 10-Q filed 2026-08-05 the engine used" in s.key()
        with open(os.path.join(s.r.folder, "analysis.md"), "w", encoding="utf-8") as f:
            f.write("Weighted IRR 17.00%.\n")
        rep = CQ.check_folder(s.r.folder)
        assert any("F3 is STALE" in w for w in rep["warnings"]), rep["warnings"]


# ---------------------------------------------------------------- 17. rendering
def test_declared_section_is_last_and_formatted():
    """02 §7.4 / D7: the heading text, last of all; every unit's format; worker text in “…”."""
    x = {"id": "F7", "label": "net debt to EBITDA covenant", "value": 2.5, "unit": "x", "precision": 1,
         "period": "2026-06-30", "kind": "filing", "type": "event", "source": dict(FIL),
         "snippet": "maximum leverage ratio of 2.5x under the credit agreement", "used_for": ["context"]}
    emp = {"id": "F8", "label": "employees at year end", "value": 898, "unit": "count", "unit_label": "employees",
           "precision": 0, "period": "2025-12-31", "kind": "folder", "type": "actual",
           "source": {"path": "profile.json:about.employees.count"}, "used_for": ["context"]}
    with scored(facts=_doc(F1(), F2(), F3(), F4(), F5(), F6(), x, emp)) as s:
        assert s.rc == 0, s.err[-1500:]
        key = s.key()
        heads = [line for line in key.split("\n") if line.startswith("## ")]
        assert heads[-1] == "## Declared facts (not engine output)", heads
        sec = key[key.index("## Declared facts (not engine output)"):]
        assert "Declared by the worker in facts.json (8 facts: 3 folder · 2 filing · 2 release · 1 third-party; sha256 " in sec
        for frag in ("- F1 · $1.95B — “Q2 2026 adjusted revenue” · Q2 FY2026 · actual (series revenue) · release 8-K "
                     "0000999001-26-000057 Ex. 99.1, filed 2026-08-05 · used for: context, tier_override",
                     "  - source words: “Adjusted revenue of $1.95 billion, up 55% year over year”",
                     "- F2 · $2,191,944,000 — “FY2025 share repurchases”", "- F3 · $3.18B–$3.22B — ",
                     "- F4 · 126% — “net revenue retention” · FY2025 · metric (series net_revenue_retention) · filing 10-K "
                     "0000999001-26-000010 “Item 7 MD&A — Key metrics”, filed 2026-02-19 · used for: moat:retention",
                     "- F5 · $4.10/share — “analyst consensus FY2027 EPS” · FY2027 · estimate · third-party “Example Wire”, 2026-09-28",
                     "- F7 · 2.5x — ", "- F8 · 898 employees — “employees at year end”"):
            assert frag in sec, (frag, sec)


# ---------------------------------------------------------------- 18. hashes
def test_score_hashes():
    """02 §8.3 (rebase A3, A5): key_numbers_sha256 is the sha256 of key_numbers.md as written (LF); reformatting
    facts.json keeps facts_sha256; dcf_content_hash (#47's) is the engine hash."""
    s = S(facts=_doc(F1(), F2())).run()
    try:
        assert s.rc == 0, s.err[-1500:]
        sc = s.score()
        with open(os.path.join(s.r.folder, "key_numbers.md"), encoding="utf-8", newline="") as f:
            on_disk = f.read()
        assert sc["key_numbers_sha256"] == hashlib.sha256(on_disk.replace("\r\n", "\n").encode("utf-8")).hexdigest()
        n = json.load(open(os.path.join(s.r.folder, "dcf_numbers.json"), encoding="utf-8"))
        assert sc["dcf_content_hash"] == n["content_hash"]
        sha = sc["declared_facts"]["facts_sha256"]
        assert sha == F.canonical_sha256(_doc(F1(), F2()))
        with open(os.path.join(s.r.folder, "facts.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(_doc(F1(), F2()), indent=4, sort_keys=True))
        s.run()
        assert s.rc == 0 and s.score()["declared_facts"]["facts_sha256"] == sha, s.err[-800:]
    finally:
        s.close()


# ---------------------------------------------------------------- 19. registry dates
def test_registry_declared_facts_event_keeps_first_date():
    """02 §5 (rebase A6): the first run dates the declared_facts event; an unchanged declaration keeps that date;
    a changed one is re-dated. A 5.7 tier_override whose reason cites nothing gets no `facts` key, so an event
    recorded before 5.7 keeps its first date."""
    reason = "trimmed: weighted IRR 17.00% sits at the bear end"
    n = _numbers()
    j = _judgment(n, tier_override="C", tier_override_reason=reason)
    sha = F.canonical_sha256(_doc(F1(), F2()))
    prior = [{"ticker": T, "event": "declared_facts", "date": "2026-10-01", "facts_sha256": sha, "count": 2,
              "by_kind": {"release": 1, "folder": 1}, "influencing": []},
             {"ticker": T, "event": "tier_override", "date": "2026-10-02", "tier_by_numbers": "B", "tier_final": "C",
              "reason": reason}]
    s = S(n=n, j=j, facts=_doc(F1(), F2()), registry=prior).run()
    try:
        assert s.rc == 0, s.err[-1500:]
        mine = {e["event"]: e for e in s.r.entries()}
        assert mine["declared_facts"]["date"] == "2026-10-01", mine
        assert mine["tier_override"]["date"] == "2026-10-02" and "facts" not in mine["tier_override"], mine
        s.write("facts.json", _doc(F1(), F2(label="FY2025 buybacks")))
        s.run()
        assert s.rc == 0, s.err[-1500:]
        de = [e for e in s.r.entries() if e.get("event") == "declared_facts"][0]
        assert de["date"] > "2026-10-01" and de["facts_sha256"] != sha, de
    finally:
        s.close()


# ---------------------------------------------------------------- 20. legacy rebuild
def _without_l2_lines(folder, n, j, score):
    keep = {k: getattr(M, k) for k in ("_kn_price_vs_iv", "_kn_base_extras", "_kn_growth_extras", "_kn_filed_history",
                                       "_kn_scenario_extras", "_kn_method_runs", "_kn_declared_facts")}
    try:
        for k in keep:
            setattr(M, k, lambda *a, **kw: [])
        return M.build_key_numbers(folder, n, j, score, {})
    finally:
        for k, v in keep.items():
            setattr(M, k, v)


def test_legacy_rebuild_without_facts_is_unchanged():
    """02 test 20 (rebase A1, A10): a 5.5.0 and a release-less (v5) record with no facts.json rebuild with the same
    tier, IRR, gates and no declared_facts / method_runs / previous_score; key_numbers.md only GAINS lines — the
    engine lines, and the Filed history table after "## Growth & moat" (never between the capex basis lines and it)."""
    for release in ("5.5.0", None):
        n = _numbers(release=release)
        with scored(n=n) as s:
            assert s.rc == 0, s.err[-1500:]
            sc = s.score()
            assert sc["tier_final"] == "B" and sc["implied_irr"] == 0.17 and sc["alert_eligible"] is False
            assert not {"declared_facts", "method_runs", "previous_score"} & set(sc), sorted(sc)
            key = s.key()
            base = _without_l2_lines(s.r.folder, _stamp(n), _judgment(n), sc)
            removed = [line for line in difflib.ndiff(base.split("\n"), key.split("\n")) if line.startswith("- ")]
            assert not removed, removed
            assert "## Filed history" in key and key.index("## Growth & moat") < key.index("## Filed history") < key.index("## Scenarios")
            assert "- Price vs weighted IV@15%: price $20.00 is 20.0% below it (price ÷ IV@15% = 0.80x)" in key, key
            assert "- Price ÷ base OE/share: 6.67x" in key
            assert "- Probability weight: bear-or-worse 35% · base 30% · bull-or-better 35%" in key
            assert "- Gross margin (fundamentals.json): " in key and "ROIC" not in key.split("## Growth & moat")[1].split("##")[0]
            assert "| FY2025 | 2025-12-31 | $5,480,717,000 |" in key, key
            assert "OE/share column withheld" in key and "Share basis" not in key and "Capex basis" not in key
            rows = list(csv.DictReader(open(os.path.join(FIX, "financials_history.csv"), encoding="utf-8")))
            yoy = float(rows[-1]["revenue"]) / float(rows[-2]["revenue"]) - 1
            assert f"- Revenue YoY: {yoy * 100:+.2f}% (FY2025)" in key, key


# ---------------------------------------------------------------- 21. method runs
def _saved(n, **kw):
    return _stamp(dict(_stamp(n), **kw))


def test_method_runs_rendered_and_hash_checked():
    """02 §7.3 (rebase A15, D3): a valid dcf_numbers_prelim.json renders under "Method runs" and lands in score.json
    method_runs; a tampered one refuses a 5.7 run and is only warned about on a 5.5.0 run; a saved IPR&D run is
    marked as after its own deduction (and the IPR&D tests' forbidden phrases never appear)."""
    n = _numbers()
    pre = _saved(n, implied_irr_weighted=0.1435, iv_at_15=70.74, g_base=0.3112, moat_score=5,
                 iprd_adjustment={"treatment": "one_time_value_deduction", "charge_per_share": 2.3334, "total": 2.8e8})
    with scored(n=n, extra={f"{T}/dcf_numbers_prelim.json": pre}) as s:
        assert s.rc == 0, s.err[-1500:]
        mr = s.score()["method_runs"]
        assert mr == [{"label": "prelim", "file": "dcf_numbers_prelim.json", "content_hash": pre["content_hash"],
                       "as_of": "2026-10-18", "engine_release": CUR, "base_oe_per_share": 3.0,
                       "base_source": "median_of_last_3_fy_oe_per_share", "implied_irr": 0.1435, "iv_at_15": 70.74,
                       "tier_by_numbers": "B", "iprd_treatment": "one_time_value_deduction",
                       "iprd_charge_per_share": 2.3334}], mr
        key = s.key()
        line = [x for x in key.split("\n") if x.startswith("- prelim (")][0]
        assert line.startswith(f"- prelim (dcf_numbers_prelim.json, 2026-10-18, release {CUR}): base $3.00/share "
                               "(median_of_last_3_fy_oe_per_share), moat 5, probs 10/25/30/25/10, g_base 31.12% → "
                               "weighted IRR 14.35%, IV@15% $25.00"), line
        assert "acquired IPR&D: one_time_value_deduction, $2.33/share off every IV" in line
        for bad in ("deducted $", "(deducted, no flag)", "Total charge", "Treatment:"):
            assert bad not in key, bad
    tampered = dict(pre, price=99.0)
    with scored(n=n, extra={f"{T}/dcf_numbers_prelim.json": tampered}) as s:
        _refuses(s, "dcf_numbers_prelim.json: content_hash missing or MISMATCH — a saved method run must be verbatim engine output")
    old = _numbers(release="5.5.0")
    with scored(n=old, extra={f"{T}/dcf_numbers_prelim.json": dict(_saved(old), price=99.0)}) as s:
        assert s.rc == 0 and "warning — dcf_numbers_prelim.json: content_hash missing or MISMATCH" in s.err, s.err[-800:]
        assert "method_runs" not in s.score()


# ---------------------------------------------------------------- 22. previous score
def test_previous_score_block():
    """02 §7.3: a score from another engine run is recorded as previous_score and printed; a rebuild of the same run
    carries it forward; a first-ever score has none."""
    n = _numbers()
    other = {"analysis_date": "2026-10-16", "engine_release": "5.4.0", "tier_final": "D", "tier_by_numbers": "D",
             "implied_irr": 0.0712, "iv_at_15": 23.08, "base_oe_per_share": 1.95, "dcf_content_hash": "f" * 64}
    s = S(n=n, prior_score=dict(other, ticker=T)).run()
    try:
        assert s.rc == 0, s.err[-1500:]
        assert s.score()["previous_score"] == other, s.score().get("previous_score")
        assert ("- Previous score (replaced by this run): 2026-10-16, release 5.4.0, tier D (numbers D), weighted IRR "
                "7.12%, IV@15% $23.08, base $1.95/share") in s.key()
        s.run()                       # a rebuild of the same run: carried
        assert s.rc == 0 and s.score()["previous_score"] == other, s.score().get("previous_score")
    finally:
        s.close()
    with scored(n=n) as s:
        assert s.rc == 0 and "previous_score" not in s.score() and "Previous score" not in s.key()
    # a legacy prior without dcf_content_hash, from the same run (same as_of / IRR / base / release): no block
    with scored(n=n, prior_score={"ticker": T, "analysis_date": "2026-10-18", "engine_release": CUR,
                                  "implied_irr": 0.17, "base_oe_per_share": 3.0, "tier_final": "B"}) as s:
        assert s.rc == 0 and "previous_score" not in s.score()


# ---------------------------------------------------------------- A17
def test_a_citation_added_after_the_run_needs_no_engine_rerun():
    """Rebase A17 (I1-I2): on an IPR&D record (engine 5.7, one-time deduction), scored with a reason quoting an engine
    figure, then given a [F1] citation and a facts.json: make_score scores again with no engine re-run (no
    IPRD_JUDGMENT_CHANGED), the same dcf_content_hash, build_site.score_from_run / reprice.score_matches_run still
    bound to the run, a new facts_sha256, and the tier_override event re-dated (it now carries facts)."""
    import test_make_score_iprd as TMI
    import build_site
    import reprice
    n = copy.deepcopy(TMI._one_time())
    n["ticker"] = T
    irr = n["implied_irr_weighted"] * 100
    reason = f"trimmed one tier: weighted IRR {irr:.2f}% after the deduction"
    j = TMI._with_applied(n, TMI._j(tier_override="C" if n["tier_by_numbers"] != "C" else "D", tier_override_reason=reason))
    s = S(n=n, j=j, files=False).run()
    try:
        assert s.rc == 0, s.err[-1500:]
        first = s.score()
        with open(s.r.registry, encoding="utf-8") as f:
            reg = json.load(f)
        for e in reg["entries"]:
            if e.get("event") == "tier_override":
                e["date"] = "2026-10-01"
        with open(s.r.registry, "w", encoding="utf-8") as f:
            json.dump(reg, f)
        fact = F4(id="F1", used_for=["tier_override"], snippet="the rate was 126%")
        s.write("facts.json", _doc(fact))
        s.write("judgment.json", dict(j, tier_override_reason=reason + "; retention 126% [F1]"))
        s.run()
        assert s.rc == 0 and "IPRD_JUDGMENT_CHANGED" not in s.err, s.err[-1500:]
        second = s.score()
        rec = json.load(open(os.path.join(s.r.folder, "dcf_numbers.json"), encoding="utf-8"))
        assert second["dcf_content_hash"] == first["dcf_content_hash"] == rec["content_hash"]
        assert reprice.score_matches_run(second, rec)[0], reprice.score_matches_run(second, rec)
        assert build_site.score_from_run(second, rec)[0], build_site.score_from_run(second, rec)
        assert second["declared_facts"]["facts_sha256"] == F.canonical_sha256(_doc(fact))
        ev = [e for e in s.r.entries() if e.get("event") == "tier_override"][0]
        assert ev["date"] > "2026-10-01" and [x["id"] for x in ev["facts"]] == ["F1"], ev
    finally:
        s.close()


# ---------------------------------------------------------------- A18
DEFERRED_OTHER = {"ticker": "OTHR", "event": "iprd_deferred_payment", "date": "2026-10-20", "deal": "Test Bio",
                  "first_charged_period": "2023-12-31",
                  "contingent_total": {"value": 1e8, "source": "SYN 10-K FY2024 (0000999001-25-000003) Note 6, p. 77"},
                  "paid_to_date": 2e7, "periods": [{"period": "2025-12-31", "amount": 2e7}]}


def test_registry_with_declared_facts_loads_and_names_never_collide():
    """Rebase A18 (I5): a registry holding a declared_facts event, a tier_override event with `facts` and another
    ticker's iprd_deferred_payment event loads, and a run keeps the other ticker's entries byte for byte; a
    declared_facts event carrying a stray `periods` key is refused as a malformed deferred-payment event (the
    name-collision rule pinned)."""
    assert M.registry_entry_problem(DEFERRED_OTHER) is None, M.registry_entry_problem(DEFERRED_OTHER)
    others = [DEFERRED_OTHER,
              {"ticker": "OTHR", "event": "declared_facts", "date": "2026-10-20", "facts_sha256": "a" * 64, "count": 1,
               "by_kind": {"filing": 1}, "influencing": ["F1"]},
              {"ticker": "OTHR", "event": "tier_override", "date": "2026-10-20", "tier_by_numbers": "B",
               "tier_final": "C", "reason": "r 9.25% [F1]",
               "facts": [{"id": "F1", "kind": "filing", "value": 0.0925, "unit": "pct", "period": "FY2025",
                          "source": dict(FIL)}]}]
    n, j = _over("adjusted revenue $1.95B [F1] against a weighted IRR of 17.00%")
    with scored(n=n, j=j, facts=_doc(F1()), registry=others) as s:
        assert s.rc == 0, s.err[-1500:]
        assert [e for e in s.r.entries() if e.get("ticker") == "OTHR"] == others
        mine = [e for e in s.r.entries() if e.get("ticker") == T]
        for e in mine:
            assert M.registry_entry_problem(e) is None and not set(e) & set(M.IPRD_DEFERRED_EVENT_KEYS), e
        # this run's own L2 events sit beside them: the declared_facts event and the cited facts on tier_override
        assert {e.get("event") for e in mine} >= {"declared_facts", "tier_override"}, mine
        assert [x["id"] for x in next(e for e in mine if e.get("event") == "tier_override")["facts"]] == ["F1"], mine
    bad = dict(others[1], periods=[{"period": "2025-12-31", "amount": 1.0}])
    assert M.registry_entry_problem(bad)[0] == "event", M.registry_entry_problem(bad)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {str(e)[:2500]}")
            except Exception as e:
                import traceback
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}")
    sys.exit(1 if fails else 0)
