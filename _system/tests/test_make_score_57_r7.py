#!/usr/bin/env python3
"""make_score.py under engine 5.7 — R7, STALE_FY discretion made checkable (Andrew's ruling R7, 2026-10-19,
ruling-sheet Q5 option A: "a worker MAY reject the TTM base, but only when the rejection reason names the distorting
cash-flow line WITH A NUMBER"; design 11 §9 T1-T20; the main agent's defaults Q13-Q18 of 2026-10-21). Run:
python _system/tests/test_make_score_57_r7.py (or python -m pytest). Offline: make_score runs as a subprocess on
synthetic folders through test_make_score_55's Run (registry redirected, no repo folder written); its engine replays
go to a stand-in that answers DCF_REPLAY_PURPOSE=base_alternatives spawns from base_replays.json and logs every spawn
(argv, DCF_REPLAY_PURPOSE, DCF_NO_OVERRIDES, DCF_IPRD_HOLD); T14 / T19 / T20 run the REAL engine offline
(engine55_harness, test_make_score_57_interim's and test_make_score_iprd's BRIDGE stand-ins). HII is the ruling's
standard: median $16.1404 Tier C vs TTM -$3.4772 (ttm.json to 2026-06-30, a literal copy of HII's legs, stamped
with the current release — never read from HII/).

T1 validator · T2 the closed cash-flow vocabulary · T3 published base kinds (base_used_label is
compute_override_impact's expression) · T4 ttm_for_run states · T5 HII's rejected TTM recorded beside the median
(score.json, key_numbers.md, registry, one --ttm replay) · T6 a STALE_FY median without a qualifying reason refuses ·
T7 no obligation without STALE_FY or a TTM for the run · T8 the reason beside a TTM pin / with nothing to reject ·
T9 a TTM-published STALE_FY run measures the annual median (Q15) · T10 release mismatch carries or records "not
measured" · T11 replay outcomes · T12 a ttm.json off the share-class declaration is never priced (L8's hook) · T13
a pre-5.7 / out-of-sync ttm.json refuses only under the obligation (L9) · T14 the declared 6-K bridge is one record
(L4) · T15 older output rebuilds unchanged (compat; passes on the old code by design) · T16 the registry event's
identity and reserved keys · T17 the reason traces (L2) · T18 declared pins need the reason (Q18), the payable pin
does not · T19 the rejected TTM takes its own acquired-IPR&D window (real engine) · T20 the engine's amortized-median
refusal names R7 · Q14 ttm_unavailable_reason quotes ttm.py's real exit-3 messages · Q16 the entry alert when a
rejection lifts the tier into S / A · the capex_unlisted_ack reasons (L9) trace like every 5.7 reason · the
switches Q13 / Q15 / Q18. Each fails on the R7 lane's base 4f7d6f1 except T15. Review fixes (the adversarial review
of 626b157, 2026-10-21; each fails on 626b157): a fixable ttm.json ttm.py cannot rebuild scores on the exit-3 quote ·
Q14 keyed on STALE_FY, not on Q13's switch · the exit-3 quote is the whole line, bound to the run · the bridge's
release-mismatch carry is R7's one carry rule (a not-computed median keeps its note) · a 20-F's declined reason is
quoted in the declared_interim entry's note.
"""
import contextlib
import copy
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from test_make_score_55 import Run, _numbers, _judgment, _stamp, CUR, T  # noqa: E402
import make_score as M  # noqa: E402
import rulings57  # noqa: E402

E = M._engine
STALE = "STALE_FY: latest fiscal year ended 10 months ago — check TTM/quarterly OE and consider --base-oe-ps override"
HII_BASE = 16.140350877192983
HII_TTM = -3.4771573604060912
HII_REASON = "median +$16.14/sh Tier C vs TTM −$3.48/sh on a half-year working-capital trough"


def hii_ttm(**over):
    """HII's ttm.json legs (FY2025 OCF $1,196M − H1'25 $428M + H1'26 −$421M; capex; SBC; 39.4M shares), stamped."""
    def leg(fy, prior, cur, tag):
        return {"fy": fy, "fy_period": ["2025-01-01", "2025-12-31"], "fy_tag": tag, "ytd_prior": prior,
                "ytd_prior_period": ["2025-01-01", "2025-06-30"], "ytd_prior_tag": tag, "ytd_current": cur,
                "ytd_current_period": ["2026-01-01", "2026-06-30"], "ytd_current_tag": tag, "ttm": fy - prior + cur}
    sh = leg(39300000, 39300000, 39400000, "WeightedAverageNumberOfDilutedSharesOutstanding")
    sh.pop("ttm")
    t = {"ticker": T, "cik": 1, "entity": "TEST CO", "fy_end": "2025-12-31", "ytd_end": "2026-06-30",
         "inputs": {"ocf": leg(1196000000, 428000000, -421000000, "NetCashProvidedByUsedInOperatingActivities"),
                    "capex": leg(402000000, 163000000, 193000000, "PaymentsToAcquirePropertyPlantAndEquipment"),
                    "sbc": leg(54000000, 33000000, 31000000, "ShareBasedCompensation"), "shares_diluted": sh},
         "ttm_ocf": 347000000, "ttm_capex": 432000000, "ttm_sbc": 52000000, "ttm_shares_diluted": 39400000,
         "ttm_oe_total": -137000000, "ttm_oe_per_share": HII_TTM, "warnings": [], "overrides_used": [],
         "engine_release": CUR}
    t.update(over)
    return t


def hii(release=CUR, **kw):
    """HII's 5.4.0 record re-stamped as a current-release (5.7) STALE_FY median run (ttm_inputs null: a median run)."""
    f = dict(base_oe_per_share=HII_BASE, base_oe_normalized_per_share=HII_BASE, tier_by_numbers="C",
             implied_irr_weighted=0.1033, implied_irr_base=0.1033, fragility_flags=[STALE], ttm_inputs=None)
    f.update(kw)
    return _numbers(release=release, **f)


def ttm_reply(tt, irr=None, tier="F", f_subtype="no_cash_generation", **kw):
    r = {"base_oe_per_share": tt["ttm_oe_per_share"], "implied_irr_weighted": irr, "tier_by_numbers": tier,
         "f_subtype": f_subtype, "data_gap": [], "ttm_inputs": E.ttm_inputs_record(tt)}
    r.update(kw)
    return r


def median_reply(base=HII_BASE, irr=0.1033, tier="C", **kw):
    r = {"base_oe_per_share": base, "implied_irr_weighted": irr, "tier_by_numbers": tier, "f_subtype": None,
         "data_gap": []}
    r.update(kw)
    return r


# The replay stand-in: logs every spawn; answers DCF_REPLAY_PURPOSE=base_alternatives engine spawns with the canned
# "ttm" (argv has --ttm) or "median" reply — JSON, {"exit": n, "stdout": ...} or {"raw": text} — and any other engine
# spawn with "other" when given; exits 97 otherwise (ttm.py always).
STANDIN = r'''import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "SPAWNED_" + os.path.basename(__file__) + ".txt"), "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "purpose": os.environ.get("DCF_REPLAY_PURPOSE"),
                        "no_overrides": os.environ.get("DCF_NO_OVERRIDES"),
                        "hold": os.environ.get("DCF_IPRD_HOLD")}) + "\n")
cfg = json.load(open(os.path.join(here, "base_replays.json"), encoding="utf-8"))
if os.path.basename(__file__) != "dcf_engine.py":
    sys.exit(97)
if os.environ.get("DCF_REPLAY_PURPOSE") == "base_alternatives":
    rep = cfg.get("ttm" if "--ttm" in sys.argv else "median")
else:
    rep = cfg.get("other")
if rep is None:
    sys.stderr.write("fail-loud stand-in: an unexpected engine spawn\n")
    sys.exit(97)
if "exit" in rep:
    sys.stdout.write(str(rep.get("stdout") or "") + "\n")
    sys.exit(int(rep["exit"]))
if "raw" in rep:
    sys.stdout.write(rep["raw"])
    sys.exit(0)
sys.stdout.write(json.dumps(rep))
'''


def run(n, j=None, ttm=None, replies=None, prior_score=None, registry=None, judgment_text=None, files=None,
        csv_rows=None):
    """make_score on a fresh folder with the replay stand-in; the closed Run with its outputs and logged spawns."""
    r = Run(n, j if judgment_text is None else None, judgment_text=judgment_text, prior_score=prior_score, files=files,
            csv_rows=csv_rows)
    try:
        for name in ("dcf_engine.py", "ttm.py"):
            with open(os.path.join(r.sysdir, name), "w", encoding="utf-8") as f:
                f.write(STANDIN)
        with open(os.path.join(r.sysdir, "base_replays.json"), "w", encoding="utf-8") as f:
            json.dump(replies or {}, f)
        if ttm is not None:
            with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
                json.dump(ttm, f, indent=1)
        if registry is not None:
            with open(r.registry, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=1)
        r.run()
        spawns = []
        for name in r.spawned():
            with open(os.path.join(r.sysdir, name), encoding="utf-8") as f:
                spawns += [dict(json.loads(line), script=name) for line in f if line.strip()]
        r.result = dict(r.state(), score=r.score() if r.rc == 0 else None, key=r.key() if r.rc == 0 else None,
                        entries=r.entries(), spawns=spawns)
        if r.rc == 0:
            with open(r.registry, encoding="utf-8") as f:
                r.result["registry"] = json.load(f)
    finally:
        r.close()
    return r


def ok(r):
    assert r.rc == 0, f"make_score refused: {r.err[-2500:]}"
    return r


def section(key, head="## Base alternatives"):
    """The lines of key_numbers.md's section starting with `head` (to the next ## or the end)."""
    lines = key.splitlines()
    i = next(k for k, ln in enumerate(lines) if ln.startswith(head))
    out = [lines[i]]
    for ln in lines[i + 1:]:
        if ln.startswith("## ") or not ln.strip():
            break
        out.append(ln)
    return out


def refusal(fn, *a, **k):
    """The refusal text fn writes before exiting (make_score.fail), or None when it returns."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        try:
            fn(*a, **k)
        except SystemExit:
            return err.getvalue()
    return None


@contextlib.contextmanager
def folder(files):
    """A temp STOCKS_BASE with <base>/TST holding `files` ({name: object or text}); make_score's BASE points at it."""
    d = tempfile.mkdtemp(prefix="r7_unit_")
    fo = os.path.join(d, T)
    os.makedirs(fo)
    for name, obj in (files or {}).items():
        with open(os.path.join(fo, name), "w", encoding="utf-8") as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj, indent=1))
    saved = M.BASE
    M.BASE = d
    try:
        yield fo
    finally:
        M.BASE = saved
        shutil.rmtree(d, ignore_errors=True)


@contextlib.contextmanager
def switch(name, value):
    saved = getattr(M, name)
    setattr(M, name, value)
    try:
        yield
    finally:
        setattr(M, name, saved)


def unavailable(t=T, cik=1, fy="2025-12-31", leg="sbc"):
    """ttm.py's exit-3 message for a filer with no 10-Q since the FY (the line main() prints)."""
    return (f"ttm.py: cannot compute TTM for {t} (CIK {cik}): {leg}: no post-FY YTD fact (no 10-Q since the {fy} "
            "fiscal year end)")


# ===========================================================================
# T1 / T2 — the validator and the closed vocabulary
# ===========================================================================
def test_rejection_reason_validator_accepts_and_refuses():
    """§2: the ruling's HII standard and the design's examples pass; a reason with no figure is [TTM-REJ2], one with no
    cash-flow line [TTM-REJ1], both when both; anything but a non-empty string [TTM-REJ0]. (A figure no source holds, or
    resting on a third-party fact, passes this rule and is refused by the trace, T17.)"""
    for text in (HII_REASON,
                 "Working capital: H1 2026 operating cash flow was −$421M (ttm.json current-YTD leg) against +$428M in "
                 "H1 2025, so the TTM base is −$3.48/sh against the $16.14/sh median",
                 "Receivables: contract assets rose $640M in Q1 2026 [F4]",
                 "OCF: H1 2026 includes a $2.1B risk-adjustment receipt [F2] that lands once a year",
                 "Capex: the H1 2026 leg carries the $1.2B Q2 fab payment",
                 "TTM −$3.48/sh vs median $16.14/sh; working-capital trough",
                 "Working capital fell $999M"):
        assert M.ttm_rejection_problem(text) is None, (text, M.ttm_rejection_problem(text))
    for text, has, hasnt in (("working-capital timing", ["[TTM-REJ2]"], ["[TTM-REJ1]"]),
                             ("TTM −$3.48/sh vs median $16.14/sh", ["[TTM-REJ1]"], ["[TTM-REJ2]"]),
                             ("The TTM is distorted by a one-off; the median is more representative",
                              ["[TTM-REJ1]", "[TTM-REJ2]"], []),
                             ("Working capital swung in H1 2026 (10-Q filed 2026-08-05)", ["[TTM-REJ2]"], ["[TTM-REJ1]"]),
                             ("Working capital: a 5 of 6 quarter pattern", ["[TTM-REJ2]"], ["[TTM-REJ1]"])):
        p = M.ttm_rejection_problem(text)
        assert p and p.startswith("judgment.json ttm_rejection_reason does not qualify: "), (text, p)
        assert all(c in p for c in has) and not any(c in p for c in hasnt), (text, p)
        assert "'working-capital timing' with no figure does not qualify (R7)" in p
    for bad in ({"line": "ocf", "value": -421e6}, "", "   ", None, 3.48, ["working capital $1M"]):
        p = M.ttm_rejection_problem(bad)
        assert p and p.startswith("[TTM-REJ0] judgment.json ttm_rejection_reason must be a non-empty string (got "), p


VOCABULARY = (
    "operating cash flow", "operating cash flows", "cash flow from operations", "cash flows from operating activities",
    "cash from operations", "operating activities", "OCF", "working capital", "working-capital", "net working capital",
    "trade working capital", "NWC", "receivables", "accounts receivable", "trade receivables", "receivable",
    "contract assets", "contract liabilities", "contract liability", "unbilled", "inventory", "inventories",
    "payables", "accounts payable", "trade payables", "accrued", "accruals", "deferred revenue",
    "deferred income taxes", "deferred taxes", "customer advances", "customer deposits", "customer prepayments",
    "unearned revenue", "prepayments", "billings", "income taxes paid", "taxes paid", "cash taxes", "tax payments",
    "tax refunds", "pension", "pensions", "retiree benefits", "postretirement", "post-retirement", "interest paid",
    "restructuring payments", "restructuring cash", "litigation settlement", "legal settlements", "settlement payments",
    "insurance proceeds", "insurance recoveries", "collateral", "margin deposits", "factoring", "securitization",
    "securitisations", "capex", "Capex", "capital expenditures", "capital spending", "PP&E",
    "property, plant and equipment", "property, plant & equipment", "property and equipment", "capitalized software",
    "capitalised software", "intangible purchases", "intangible asset purchases", "purchases of intangibles", "SBC",
    "stock-based compensation", "share-based compensation", "equity based compensation", "stock compensation")
NOT_LINES = ("revenue", "gross margin", "EPS", "net income", "guidance", "crack spread", "bookings", "margin", "taxes",
             "settlement", "restructuring charges", "EBITDA", "operating income", "backlog", "the H1 2026 trough",
             "ocfs", "SBCs", "capexes")


def test_cash_flow_line_vocabulary_is_closed():
    """§2: every documented line (owner's earnings' own: operating cash flow and its statement sub-lines, capex — PP&E,
    capitalized software (R9), intangibles — and SBC) matches CASH_FLOW_LINE_RE, inside a sentence and in any case;
    P&L words and word fragments never do."""
    for line in VOCABULARY:
        for text in (line, f"the {line} leg moved $5M", line.upper()):
            assert M.CASH_FLOW_LINE_RE.search(text), (line, text)
    for word in NOT_LINES:
        assert not M.CASH_FLOW_LINE_RE.search(word), word
        assert not M.CASH_FLOW_LINE_RE.search(f"a {word} spike of $25.95"), word


# ===========================================================================
# T3 / T4 — published base kinds, ttm_for_run
# ===========================================================================
def _old_base_used(ticker, n):
    """compute_override_impact's base_used expression at the lane's base (4f7d6f1), verbatim."""
    base_src = (n.get("base_source") or "").lower()
    pin_src = (n.get("inputs") or {}).get("base_pin_source")
    pinned = (n.get("inputs") or {}).get("base_oe_ps_arg") is not None or "ttm" in base_src
    return "payable_5y" if (pin_src == "judgment_base_override" or n.get("payable_base")) \
        else "declared_interim" if M._interim_pinned(ticker, n) \
        else "declared_pin" if M._declared_pin_not_ttm(ticker, n) \
        else "ttm" if pinned else "median_3y"


def _pinned(n, pin, src="base_oe_ps_arg", window=None, base_source="agent_supplied_ttm_override"):
    inp = dict(n["inputs"], base_oe_ps_arg=pin, base_pin_source=src)
    if window:
        inp["base_basis_window"] = window
    return dict(n, base_oe_per_share=pin, base_source=base_source, inputs=inp)


def test_published_kind_follows_the_override_impact_labels():
    """§3.2: published_base_kind is compute_override_impact's label (base_used_label, the expression extracted
    unchanged — identical to the old one on every case) with median_3y read as annual_median; ttm_published for the
    TTM kinds and a basis_window "ttm" pin; an iprd_amortized pin is ttm (native ttm_json) or declared_pin (median)."""
    tt = hii_ttm()
    n = hii()
    amort_m = {"treatment": "amortized_in_base", "amortized": {"native_base": "median_of_last_3_fy_oe_per_share",
                                                               "native_base_per_share": 16.5, "pinned_per_share": 15.9}}
    amort_t = {"treatment": "amortized_in_base", "amortized": {"native_base": "ttm_json", "native_base_per_share": HII_TTM,
                                                               "pinned_per_share": -3.6}}
    bo = {"value": 15.0, "source": "s", "reason": "r", "basis_window": {"window": "fy"}}
    bo_t = {"value": 15.0, "source": "s", "reason": "r",
            "basis_window": {"window": "ttm", "ytd_current_period": ["2026-01-01", "2026-06-30"]}}
    am_m = {"value": 15.9, "source": "s", "reason": "r", "basis": "iprd_amortized",
            "native_base": "median_of_last_3_fy_oe_per_share"}
    am_t = {"value": -3.6, "source": "s", "reason": "r", "basis": "iprd_amortized", "native_base": "ttm_json"}
    pay_n, pay_j = __import__("test_make_score_55")._payable(CUR)
    bridge = dict(tt, basis="declared_interim")
    cases = [  # (record, judgment, ttm.json, kind, ttm_published, variant)
        (n, {}, tt, "annual_median", False, None),
        (_pinned(n, HII_TTM, "ttm_json", base_source="ttm_json"), {}, tt, "ttm", True, None),
        (_pinned(n, HII_TTM), {}, tt, "ttm", True, None),                                   # via-TTM --base-oe-ps
        (_pinned(n, 15.0, window={"window": "fy"}), {"base_override": bo}, tt, "declared_pin", False, None),
        (_pinned(n, 15.0, window=bo_t["basis_window"]), {"base_override": bo_t}, tt, "declared_pin", True, None),
        (pay_n, pay_j, None, "payable_5y", False, None),
        (dict(_pinned(n, 15.9), iprd_adjustment=amort_m), {"base_override": am_m}, tt, "declared_pin", False,
         "iprd_amortized"),
        (dict(_pinned(n, -3.6), iprd_adjustment=amort_t), {"base_override": am_t}, tt, "ttm", True, "iprd_amortized"),
        (_pinned(n, HII_TTM, "ttm_json", base_source="ttm_json"), {}, bridge, "declared_interim", True, None),
    ]
    for rec, jj, doc, kind, pub, variant in cases:
        files = {"judgment.json": jj}
        if doc is not None:
            files["ttm.json"] = doc
        with folder(files):
            got = M.published_base_kind(T, rec)
            assert got[:2] == (kind, pub), (kind, got)
            assert got[2]["variant"] == variant, got
            old = _old_base_used(T, rec)
            assert M.base_used_label(T, rec) == old, (kind, old)
            assert (old if old != "median_3y" else "annual_median") == kind


def test_ttm_for_run_states():
    """§3.3: no file / unreadable / not an object / no finite numeric ttm_oe_per_share -> None; another FY -> other_fy;
    an unstamped or 5.6.0-stamped file -> fixable (L9's note); an override ttm.json used that judgment.json withdrew or
    changed -> fixable; a declared bridge judgment.json no longer declares -> orphan_bridge, one whose record checks
    fail -> fixable (L4); otherwise eligible, with its input hash and stamp."""
    n = hii()
    for files in ({}, {"ttm.json": "not json"}, {"ttm.json": "[1, 2]"}, {"ttm.json": hii_ttm(ttm_oe_per_share="x")},
                  {"ttm.json": hii_ttm(ttm_oe_per_share=None)}, {"ttm.json": '{"ttm_oe_per_share": NaN}'}):
        with folder(files) as fo:
            assert M.ttm_for_run(fo, n, {}) is None, files
    with folder({"ttm.json": hii_ttm()}) as fo:
        t = M.ttm_for_run(fo, n, {})
        assert (t["kind"], t["status"], t["note"]) == ("ttm", "eligible", None), t
        assert t["base_oe_per_share"] == HII_TTM and t["ttm_input_hash"] == E.ttm_inputs_record(hii_ttm())["ttm_input_hash"]
        assert (t["fy_end"], t["ytd_end"], t["ttm_engine_release"], t["share_basis"]) == ("2025-12-31", "2026-06-30",
                                                                                        CUR, None)
    with folder({"ttm.json": hii_ttm(fy_end="2024-12-31")}) as fo:
        t = M.ttm_for_run(fo, n, {})
        assert t["status"] == "other_fy" and t["note"] == ("ttm.json is built on FY 2024-12-31; this run's latest FY "
                                                           "ends 2025-12-31 — not this run's TTM (rerun ttm.py)"), t
    unstamped = hii_ttm()
    del unstamped["engine_release"]
    for doc, rel in ((unstamped, "none"), (hii_ttm(engine_release="5.6.0"), "5.6.0")):
        with folder({"ttm.json": doc}) as fo:
            t = M.ttm_for_run(fo, n, {})
            assert t["status"] == "fixable" and t["note"] == (f"ttm.json predates engine 5.7 (engine_release {rel}): its "
                                                              "legs were built without the 5.7 capex rules — rerun "
                                                              "ttm.py TST"), t
    used = hii_ttm(overrides_used=[{"field": "sbc", "value": 30e6, "kind": "estimate", "source": "s", "legs_filled": {}}])
    with folder({"ttm.json": used}) as fo:
        t = M.ttm_for_run(fo, n, {}, j_over={})
        assert t["status"] == "fixable" and t["note"] == ("ttm.json used a sbc_override that judgment.json no longer "
                                                          "declares — rerun ttm.py TST with the current judgment.json"), t
        t = M.ttm_for_run(fo, n, {}, j_over={"sbc": {"value": 31e6, "kind": "estimate"}})
        assert t["status"] == "fixable" and "declares as value 31000000.0, kind estimate" in t["note"], t
        assert M.ttm_for_run(fo, n, {}, j_over={"sbc": {"value": 30e6, "kind": "estimate"}})["status"] == "eligible"
    bridge = hii_ttm(basis="declared_interim")
    with folder({"ttm.json": bridge}) as fo:
        t = M.ttm_for_run(fo, n, {})
        assert (t["kind"], t["status"]) == ("declared_interim", "orphan_bridge"), t
        assert t["note"] == ("ttm.json is a declared 6-K interim bridge but judgment.json declares no interim_bridge "
                             "(withdrawn) — not a TTM for this run")
        t = M.ttm_for_run(fo, n, {"interim_bridge": {"not": "valid"}})
        assert t["status"] == "fixable" and "judgment.json declares no (valid) interim_bridge" in t["note"], t


# ===========================================================================
# T5 — HII, the ruling's standard
# ===========================================================================
def _hii_expected(tt):
    h, rel = E.ttm_inputs_record(tt)["ttm_input_hash"], tt.get("engine_release")
    return {"schema": 1, "published": "annual_median", "stale_fy": True, "ttm_rejection_reason": HII_REASON,
            "ttm_unavailable_reason": None,
            "bases": [{"kind": "annual_median", "role": "published", "computed": True, "measured": True,
                       "base_oe_per_share": 16.1404, "weighted_irr": 0.1033, "tier_by_numbers": "C", "f_subtype": None,
                       "iprd_charge_per_share": 0.0, "iprd_treatment": None,
                       "source": "median_of_last_3_fy_oe_per_share", "why": "ttm_rejected",
                       "why_text": "published — the TTM was rejected (judgment.json ttm_rejection_reason; WORKER_SPEC "
                                   "step 4)", "note": None},
                      {"kind": "ttm", "role": "rejected", "computed": True, "measured": True,
                       "base_oe_per_share": -3.4772, "weighted_irr": None, "tier_by_numbers": "F",
                       "f_subtype": "no_cash_generation", "iprd_charge_per_share": 0.0, "iprd_treatment": None,
                       "fy_end": "2025-12-31", "ytd_end": "2026-06-30", "ttm_input_hash": h, "ttm_engine_release": rel,
                       "share_basis": None, "source": "ttm.json (ttm.py: FY − prior YTD + current YTD, 10-Q)",
                       "replay": "--measure --ttm (final configuration, field overrides on)",
                       "base_change_pct": -121.54, "weighted_irr_change_pp": None, "tier_changed": True,
                       "why": "rejection_reason", "why_text": None, "note": None}],
            "replays": 1, "measured": True, "note": None, "impact_carried_from_prior_score": False,
            "counterfactual_engine_release": None}


HII_KEY = [
    "## Base alternatives (R7 — the published base beside every other base computed for this run)",
    "- Published: annual median of the last 3 FY OE/share $16.14 — weighted IRR 10.33% · Tier C (by numbers)",
    "- Rejected: TTM to 2026-06-30 (ttm.py, 10-Q YTD; FY 2025-12-31) $-3.48/share — weighted IRR — (Tier F, "
    "no_cash_generation) · base -121.54% vs published · tier C → F",
    "- Rejection reason: “median +$16.14/sh Tier C vs TTM −$3.48/sh on a half-year working-capital trough”",
    "- Measured: the final configuration replayed with --ttm (field overrides on; the TTM's own acquired-IPR&D window "
    "and share count; 1 replay)",
    "- STALE_FY fires: the TTM is the scored base unless rejected with a reason that names the distorting cash-flow "
    "line and a number (WORKER_SPEC step 4)"]


def test_hii_rejected_ttm_is_recorded_beside_the_median():
    """§3.9-§3.11: HII's next 5.7 run with the ruling's own reason scores on the median; score.json base_alternatives
    is §3.9's record (the rejected TTM replayed: base -$3.4772, Tier F, no_cash_generation; -121.54% against the
    published base); key_numbers.md's section is §3.11's, right after the IPR&D place and before Growth & moat; one
    base_alternatives registry event (§3.10); exactly ONE engine spawn: the final configuration with --measure --ttm,
    labelled DCF_REPLAY_PURPOSE=base_alternatives, field overrides on, no IPR&D hold; tier_final stays C."""
    tt, n = hii_ttm(), hii()
    r = ok(run(n, _judgment(n, ttm_rejection_reason=HII_REASON), ttm=tt, replies={"ttm": ttm_reply(tt)}))
    s, key = r.result["score"], r.result["key"]
    assert s["base_alternatives"] == _hii_expected(tt), json.dumps(s["base_alternatives"], indent=1)
    assert s["tier_final"] == "C" and s["tier_by_numbers"] == "C" and s["base_oe_per_share"] == HII_BASE
    assert section(key) == HII_KEY, section(key)
    heads = [h for h in key.splitlines() if h.startswith("## ")]
    assert heads.index("## Base alternatives (R7 — the published base beside every other base computed for this run)") \
        == heads.index("## Growth & moat") - 1, heads
    assert [(x["script"], x["argv"], x["purpose"], x["no_overrides"], x["hold"]) for x in r.result["spawns"]] == [
        ("SPAWNED_dcf_engine.py.txt", [T, "--measure"] + M._final_run_args(n) + ["--ttm"], "base_alternatives", None,
         None)], r.result["spawns"]
    ev = [e for e in r.result["entries"] if e.get("event") == "base_alternatives"]
    assert len(ev) == 1, r.result["entries"]
    e = dict(ev[0])
    assert isinstance(e.pop("date"), str)
    assert e == {"ticker": T, "event": "base_alternatives", "chosen": "annual_median", "stale_fy": True,
                 "reason": HII_REASON, "ttm_kind": "ttm", "ttm_fy_end": "2025-12-31", "ttm_ytd_end": "2026-06-30",
                 "bases": [{"kind": "annual_median", "role": "published", "computed": True, "base_oe_per_share": 16.1404,
                            "weighted_irr": 0.1033, "tier_by_numbers": "C", "note": None},
                           {"kind": "ttm", "role": "rejected", "computed": True, "base_oe_per_share": -3.4772,
                            "weighted_irr": None, "tier_by_numbers": "F", "note": None}],
                 "measured": True, "note": None, "impact_carried_from_prior_score": False,
                 "counterfactual_engine_release": None}, e
    assert M.registry_entry_problem(ev[0]) is None
    assert "base_alternatives" in M.SCORE_DECISION_KEYS
    # the reason traced (L2): two engine figures, no fact
    assert s["declared_facts"]["influence"]["ttm_rejection_reason"] == {"facts": [], "engine_numbers": 2,
                                                                         "third_party_only": False}


# ===========================================================================
# T6 / T7 / T8 — the obligation and its refusals
# ===========================================================================
R7_1 = ("[TTM-REJ0] STALE_FY fires and ttm.json holds a TTM for this run (to 2026-06-30: $-3.48/share) but the "
        "published base is the annual median ($16.14/share) — pass --ttm in the final run, or reject the TTM in "
        "judgment.json ttm_rejection_reason: name the distorting cash-flow line with a number (WORKER_SPEC step 4; "
        "Andrew's ruling R7)")


def test_stale_fy_median_without_a_qualifying_reason_is_refused():
    """§4 R7-1 .. R7-4: a STALE_FY median beside an eligible TTM for its FY, with no reason, an empty / non-string one,
    one with no figure or one with no cash-flow line, is refused before any replay and any write."""
    tt, n = hii_ttm(), hii()
    for jj, needles in ((_judgment(n), [R7_1]),
                        (_judgment(n, ttm_rejection_reason=None), [R7_1]),
                        (_judgment(n, ttm_rejection_reason=""), ["[TTM-REJ0] judgment.json ttm_rejection_reason must "
                                                                 "be a non-empty string (got '')"]),
                        (_judgment(n, ttm_rejection_reason={}), ["[TTM-REJ0]", "(got {})"]),
                        (_judgment(n, ttm_rejection_reason="working-capital timing"), ["[TTM-REJ2]"]),
                        (_judgment(n, ttm_rejection_reason="TTM −$3.48/sh vs median $16.14/sh"), ["[TTM-REJ1]"])):
        r = run(n, jj, ttm=tt, replies={"ttm": ttm_reply(tt)})
        r.refused(*needles)
        assert r.result["spawns"] == [] and r.result["entries"] == [], (needles, r.result["spawns"])


def test_no_obligation_without_stale_fy_or_a_ttm_for_this_run():
    """§3.6 rows 2-4: without STALE_FY a TTM for the run is an `alternative` taken from ttm.json, not replayed, no
    reason needed; with STALE_FY and no TTM for this run (no ttm.json; one on another FY) the TTM entry is computed:
    false with why — a 10-K quoting ttm.py's exit-3 message (default Q14, recorded on the block), a 20-F with
    interim_bridge_declined; no refusal, no spawn, no registry event."""
    tt = hii_ttm()
    fresh = hii(fragility_flags=[])
    r = ok(run(fresh, _judgment(fresh), ttm=tt))
    ba = r.result["score"]["base_alternatives"]
    assert ba["published"] == "annual_median" and ba["stale_fy"] is False and ba["replays"] == 0, ba
    pub, alt = ba["bases"]
    assert pub["why"] == "default_median" and alt["kind"] == "ttm" and alt["role"] == "alternative", ba
    assert alt["computed"] is True and alt["measured"] is False and alt["base_oe_per_share"] == -3.4772, alt
    assert alt["note"] == "not replayed: STALE_FY does not fire — the median is the default base", alt
    assert r.result["spawns"] == [] and not [e for e in r.result["entries"] if e.get("event") == "base_alternatives"]
    assert ("- Alternative: TTM to 2026-06-30 (ttm.py, 10-Q YTD; FY 2025-12-31) $-3.48/share — weighted IRR / tier: "
            "not replayed: STALE_FY does not fire — the median is the default base") in r.result["key"]
    # no STALE_FY, no ttm.json: no alternative, no block
    r = ok(run(fresh, _judgment(fresh)))
    assert "base_alternatives" not in r.result["score"] and "## Base alternatives" not in r.result["key"]
    # STALE_FY, no ttm.json (a 10-K: ttm.py's exit-3 message quoted)
    n = hii()
    msg = unavailable()
    r = ok(run(n, _judgment(n, ttm_unavailable_reason=msg)))
    ba = r.result["score"]["base_alternatives"]
    assert ba["ttm_unavailable_reason"] == msg and ba["replays"] == 0 and ba["measured"] is True, ba
    pub, alt = ba["bases"]
    assert pub["why"] == "no_ttm_for_run" and (alt["kind"], alt["computed"], alt["measured"]) == ("ttm", False, False)
    assert alt["note"] == ("no ttm.json for this run — ttm.py cannot build one (judgment.json ttm_unavailable_reason "
                           "quotes its exit-3 message)"), alt
    assert f"- TTM unavailable (ttm.py's exit-3 message, judgment.json ttm_unavailable_reason): “{msg}”" in r.result["key"]
    assert "- Alternative: TTM not computed — no ttm.json for this run" in r.result["key"]
    assert r.result["spawns"] == [] and not [e for e in r.result["entries"] if e.get("event") == "base_alternatives"]
    # STALE_FY, a ttm.json on another FY: not this run's TTM (the 10-K quotes ttm.py)
    r = ok(run(n, _judgment(n, ttm_unavailable_reason=msg), ttm=hii_ttm(fy_end="2024-12-31")))
    alt = r.result["score"]["base_alternatives"]["bases"][1]
    assert alt["computed"] is False and alt["note"].startswith("ttm.json is built on FY 2024-12-31; this run's latest FY "
                                                               "ends 2025-12-31"), alt
    assert r.result["spawns"] == []
    # a 20-F STALE_FY median with interim_bridge_declined: the declared_interim entry is not computed, no Q14 field
    ads = {"ratio": 1.0, "source": "cover", "reason": "no ADS"}
    nf = hii(filer_annual_form="20-F", ads_ratio=ads)
    jf = _judgment(nf, interim_bridge_declined={"reason": "the H1 6-K (181 days) prints no cash-flow statement",
                                                "report": None})
    r = ok(run(nf, jf))
    alt = r.result["score"]["base_alternatives"]["bases"][1]
    assert (alt["kind"], alt["computed"]) == ("declared_interim", False), alt
    assert alt["note"] == ("no ttm.json for this run — no declared 6-K interim bridge (judgment.json "
                           "interim_bridge_declined, R2): “the H1 6-K (181 days) prints no cash-flow statement”"), alt


def test_reason_beside_a_ttm_pin_or_with_nothing_to_reject_is_refused():
    """§4 R7-5 / R7-6: the field beside a TTM pin, without STALE_FY, beside the payable pin or with no TTM for this run
    is a stale or misplaced declaration — refused, nothing written."""
    tt = hii_ttm(ttm_oe_per_share=20.5, ttm_oe_total=20.5 * 39.4e6)
    pinned = _pinned(hii(), 20.5, "ttm_json", base_source="ttm_json")
    pinned["ttm_inputs"] = E.ttm_inputs_record(tt)
    run(pinned, _judgment(pinned, ttm_rejection_reason=HII_REASON), ttm=tt).refused(
        "judgment.json ttm_rejection_reason rejects the TTM but the final run's base is ttm.json's (base_source ttm_json) "
        "— drop the field, or rerun the final pass without --ttm")
    fresh = hii(fragility_flags=[])
    run(fresh, _judgment(fresh, ttm_rejection_reason=HII_REASON), ttm=hii_ttm()).refused(
        "judgment.json ttm_rejection_reason is declared but STALE_FY does not fire (the median is the default base) — "
        "remove it")
    import test_make_score_55 as T55
    pn, pj = T55._payable(CUR)
    pn = dict(pn, fragility_flags=[STALE])
    run(pn, dict(pj, ttm_rejection_reason=HII_REASON), ttm=hii_ttm(), replies={"other": median_reply()}).refused(
        "judgment.json ttm_rejection_reason is declared but the payable-earnings base replaces the OCF base — remove it")
    n = hii()
    run(n, _judgment(n, ttm_rejection_reason=HII_REASON), ttm=hii_ttm(fy_end="2024-12-31")).refused(
        "judgment.json ttm_rejection_reason is declared but ttm.json holds no TTM for this run (ttm.json is built on FY "
        "2024-12-31;")
    run(n, _judgment(n, ttm_rejection_reason=HII_REASON)).refused(
        "judgment.json ttm_rejection_reason is declared but ttm.json holds no TTM for this run (no ttm.json) — remove it")


# ===========================================================================
# T9 — a TTM-published STALE_FY run measures the annual median (default Q15)
# ===========================================================================
def _ttm_published(tier="B", irr=0.16):
    tt = hii_ttm(ttm_oe_per_share=20.5, ttm_oe_total=20.5 * 39.4e6)
    n = _pinned(hii(tier_by_numbers=tier, implied_irr_weighted=irr), 20.5, "ttm_json", base_source="ttm_json")
    n["ttm_inputs"] = E.ttm_inputs_record(tt)
    return n, tt


def test_ttm_published_stale_run_measures_the_annual_median():
    """§3.6 / default Q15 (R7_MEDIAN_BESIDE_TTM): a --ttm STALE_FY run spawns ONE --measure replay with no pin (no
    --ttm, no --base-oe-ps); its annual-median entry is the record's base_oe_normalized_per_share with the replay's
    IRR and tier, why not_chosen; no registry event (a mandated TTM base is no judgment call); a replay base other
    than the record's median refuses (R7-10)."""
    n, tt = _ttm_published()
    r = ok(run(n, _judgment(n), ttm=tt, replies={"median": median_reply()}))
    ba = r.result["score"]["base_alternatives"]
    pub, med = ba["bases"]
    assert ba["published"] == "ttm" and ba["replays"] == 1 and ba["measured"] is True, ba
    assert pub["why"] == "stale_fy_ttm" and pub["ttm_input_hash"] == n["ttm_inputs"]["ttm_input_hash"], pub
    assert pub["ytd_end"] == "2026-06-30" and pub["ttm_engine_release"] == CUR, pub
    assert (med["kind"], med["role"], med["computed"], med["measured"]) == ("annual_median", "alternative", True, True)
    assert (med["base_oe_per_share"], med["weighted_irr"], med["tier_by_numbers"]) == (16.1404, 0.1033, "C"), med
    assert med["why"] == "not_chosen" and med["replay"] == "--measure (final configuration, field overrides on, no pin)"
    assert med["base_change_pct"] == -21.27 and med["weighted_irr_change_pp"] == -5.67 and med["tier_changed"] is True
    sp = r.result["spawns"]
    assert len(sp) == 1 and sp[0]["purpose"] == "base_alternatives" and sp[0]["hold"] is None, sp
    assert "--measure" in sp[0]["argv"] and "--ttm" not in sp[0]["argv"] and "--base-oe-ps" not in sp[0]["argv"], sp
    assert not [e for e in r.result["entries"] if e.get("event") == "base_alternatives"]
    assert ("- Alternative: annual median of the last 3 FY OE/share $16.14 — weighted IRR 10.33% (-5.67pp) (Tier C) · "
            "base -21.27% vs published · tier B → C (not chosen: STALE_FY fires and the TTM was not rejected "
            "(WORKER_SPEC step 4))") in r.result["key"], section(r.result["key"])
    assert ("- Measured: the final configuration replayed without a base pin (field overrides on; the median's own "
            "acquired-IPR&D window and share count; 1 replay)") in r.result["key"]
    run(n, _judgment(n), ttm=tt, replies={"median": median_reply(base=17.0)}).refused(
        "the annual_median replay scored base 17.0, not 16.140350877192983 — re-run the engine")
    # without STALE_FY the median is recorded from the run, not replayed
    nf, _ = _ttm_published()
    nf["fragility_flags"] = []
    r = ok(run(nf, _judgment(nf), ttm=tt))
    med = r.result["score"]["base_alternatives"]["bases"][1]
    assert med["measured"] is False and med["note"] == "not replayed: STALE_FY does not fire" and med["weighted_irr"] is None
    assert r.result["score"]["base_alternatives"]["bases"][0]["why"] == "ttm_pinned" and r.result["spawns"] == []


# ===========================================================================
# T10 — release mismatch
# ===========================================================================
def test_release_mismatch_carries_or_records_not_measured_without_a_spawn():
    """§3.7: a 5.7 record of another release (5.7.99) never replays: the prior score.json base_alternatives is carried
    when it was measured on this published base and IRR, the same kind and the same ttm_input_hash
    (impact_carried_from_prior_score, counterfactual_engine_release); another ttm.json or no prior record -> the
    rejected entry keeps ttm.json's base, IRR / tier null, measured false, the block's not-measured note. The
    obligation still binds: no reason -> R7-1."""
    tt, n = hii_ttm(), hii()
    good = ok(run(n, _judgment(n, ttm_rejection_reason=HII_REASON), ttm=tt, replies={"ttm": ttm_reply(tt)}))
    n2 = hii(release="5.7.99")
    j2 = _judgment(n2, ttm_rejection_reason=HII_REASON)
    c = ok(run(n2, j2, ttm=tt, prior_score=good.result["score"]))
    ba = c.result["score"]["base_alternatives"]
    assert c.result["spawns"] == [] and ba["impact_carried_from_prior_score"] is True, ba
    assert ba["counterfactual_engine_release"] == "5.7.99" and ba["note"] is None and ba["measured"] is True, ba
    assert ba["bases"][1] == good.result["score"]["base_alternatives"]["bases"][1], ba["bases"][1]
    assert "- Measured: carried from the prior score.json, not re-measured (engine output release 5.7.99 vs current " \
           f"{CUR})" in c.result["key"]
    note = M._not_measured_note("5.7.99")
    for prior, doc in ((None, tt), (good.result["score"], hii_ttm(ttm_sbc=52000001))):
        r = ok(run(n2, j2, ttm=doc, prior_score=prior))
        ba = r.result["score"]["base_alternatives"]
        rej = ba["bases"][1]
        assert r.result["spawns"] == [] and ba["impact_carried_from_prior_score"] is False and ba["note"] == note, ba
        assert rej["measured"] is False and rej["weighted_irr"] is None and rej["tier_by_numbers"] is None, rej
        assert rej["base_oe_per_share"] == -3.4772 and ba["measured"] is False, rej
        assert f"- Measured: {note}" in r.result["key"]
    run(n2, _judgment(n2), ttm=tt).refused("[TTM-REJ0] STALE_FY fires and ttm.json holds a TTM for this run")


# ===========================================================================
# T11 — replay outcomes
# ===========================================================================
def test_replay_outcomes():
    """§3.5: the rejected TTM's replay exits 3 -> R7-8 naming the engine's line; it answers a data gap and no base ->
    the entry computed: false "the TTM replay gaps: ..." and the score writes; the median of a TTM-published run
    refused by the engine -> computed: false with the line; exit 1, or exit 0 with unparseable output -> R7-9; a run
    that cannot start -> rc None; ttm.json changed during the replay (another ttm_input_hash) -> R7-10."""
    tt, n = hii_ttm(), hii()
    jj = _judgment(n, ttm_rejection_reason=HII_REASON)
    run(n, jj, ttm=tt, replies={"ttm": {"exit": 3, "stdout": "BAD_TTM_SHARES for TST: ttm.json ttm_shares_diluted is "
                                                             "missing"}}).refused(
        "the rejected TTM does not score through the engine: BAD_TTM_SHARES for TST: ttm.json ttm_shares_diluted is "
        "missing — fix ttm.json (rerun ttm.py TST), then make_score")
    r = ok(run(n, jj, ttm=tt, replies={"ttm": {"base_oe_per_share": None, "data_gap": ["shares"]}}))
    rej = r.result["score"]["base_alternatives"]["bases"][1]
    assert (rej["computed"], rej["measured"], rej["note"]) == (False, True, "the TTM replay gaps: shares"), rej
    assert rej["base_oe_per_share"] is None and rej["tier_by_numbers"] is None
    assert ("- Rejected: TTM to 2026-06-30 (ttm.py, 10-Q YTD; FY 2025-12-31) not computed — the TTM replay gaps: "
            "shares") in r.result["key"]
    pn, ptt = _ttm_published()
    r = ok(run(pn, _judgment(pn), ttm=ptt, replies={"median": {"exit": 3, "stdout": "BAD_BASE_OVERRIDE for TST: x"}}))
    med = r.result["score"]["base_alternatives"]["bases"][1]
    assert (med["computed"], med["note"]) == (False, "the annual-median replay refused: BAD_BASE_OVERRIDE for TST: x"), med
    for rep, needle in (({"exit": 1, "stdout": "Traceback"}, "TTM replay failed (exit 1) — cannot measure the base "
                                                             "alternatives; retry make_score"),
                        ({"raw": "not json"}, "TTM replay failed (exit 0) — cannot measure the base alternatives"),
                        ({"base_oe_per_share": None, "data_gap": []}, "TTM replay produced no base and no data gap"),
                        (ttm_reply(hii_ttm(ttm_sbc=1)), "ttm.json changed while make_score measured it"),
                        (ttm_reply(tt, base_oe_per_share=-3.9), "the ttm replay scored base -3.9, not "
                                                                "-3.4771573604060912")):
        r = run(n, jj, ttm=tt, replies={"ttm": rep})
        r.refused(needle)
        assert len(r.result["spawns"]) == 1, r.result["spawns"]
    d = tempfile.mkdtemp(prefix="r7_rc_")
    try:
        assert M._run_replay([os.path.join(d, "no_such_interpreter.exe"), "x"]) == (None, None, None)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ===========================================================================
# T12 / T13 — L8's share-class gate, L9's release stamp and the override sync
# ===========================================================================
OFF_BASIS = "ttm.json is not on this share_classes declaration — rerun ttm.py"


def test_share_classes_ttm_off_declaration_is_never_priced():
    """08 §8.9 / M-12 (the contract R7 meets; L8 fills _alt_ttm_ok with share_classes.ttm_on_declaration): a ttm.json
    the gate refuses is recorded computed: false with 08's exact note — never priced, no replay, no obligation (a
    STALE_FY median scores without a reason); one on the declaration is priced, share_basis total_units, and
    key_numbers names it per economic unit."""
    tt, n = hii_ttm(), hii()
    with folder({"ttm.json": tt, "judgment.json": {}}) as fo, switch("_alt_ttm_ok", lambda doc, j_sc: False):
        t = M.ttm_for_run(fo, n, {})
        assert (t["status"], t["note"]) == ("off_basis", OFF_BASIS), t
        plan = M.ttm_rejection_state(fo, n, {}, j_sc={"declared": True})
        assert plan["required"] is False and plan["ttm"]["status"] == "off_basis", plan
        ba = M.build_base_alternatives(T, fo, n, {}, plan)      # no replay is spawned (none can be: off the basis)
        alt = ba["bases"][1]
        assert (alt["kind"], alt["computed"], alt["note"], ba["replays"]) == ("ttm", False, OFF_BASIS, 0), ba
        assert alt["base_oe_per_share"] is None and alt["weighted_irr"] is None
        assert refusal(M.ttm_rejection_state, fo, n, {"ttm_rejection_reason": HII_REASON}, j_sc={"declared": True}) \
            .count("ttm.json holds no TTM for this run (ttm.json is not on this share_classes declaration")
    with folder({"ttm.json": tt, "judgment.json": {}}) as fo:
        t = M.ttm_for_run(fo, n, {}, j_sc={"declared": True})
        assert t["status"] == "eligible" and t["share_basis"] == "total_units", t
        e = M._alt_entry("ttm", "rejected", {"base_oe_per_share": 16.1404, "weighted_irr": 0.1033,
                                             "tier_by_numbers": "C"}, True, True, vals=dict(ttm_reply(tt),
                                                                                           base_oe_per_share=-3.4772),
                         ttm=t)
        assert e["share_basis"] == "total_units"
        lines = M._kn_base_alternatives({"base_alternatives": {"bases": [
            {"kind": "annual_median", "role": "published", "computed": True, "measured": True,
             "base_oe_per_share": 16.1404, "weighted_irr": 0.1033, "tier_by_numbers": "C"}, e], "replays": 1}})
        assert any(ln.startswith("- Rejected: TTM to 2026-06-30 (ttm.py, 10-Q YTD; FY 2025-12-31) $-3.48 per economic "
                                 "unit") for ln in lines), lines


def test_pre57_or_out_of_sync_ttm_json_refuses_only_under_the_obligation():
    """§3.3 rows 5-6 (L9's stamp; the override sync): under the obligation an unstamped ttm.json, or one that used a
    sbc_override judgment.json no longer declares, cannot be priced — R7-7, before any replay; without STALE_FY the
    same file is an unreplayed alternative with the note and the run scores."""
    n = hii()
    unstamped = hii_ttm()
    del unstamped["engine_release"]
    used = hii_ttm(overrides_used=[{"field": "sbc", "value": 30e6, "kind": "estimate", "source": "s",
                                    "legs_filled": {"ytd_current": {"period": ["2026-01-01", "2026-06-30"],
                                                                    "amount": 15e6}}}])
    for doc, needle in ((unstamped, "ttm.json predates engine 5.7 (engine_release none)"),
                        (used, "ttm.json used a sbc_override that judgment.json no longer declares")):
        r = run(n, _judgment(n, ttm_rejection_reason=HII_REASON), ttm=doc, replies={"ttm": ttm_reply(doc)})
        r.refused("the TTM this run rejects cannot be priced: " + needle, "R7 records the rejected TTM's base, weighted "
                  "IRR and tier beside the published base")
        assert r.result["spawns"] == []
    fresh = hii(fragility_flags=[])
    r = ok(run(fresh, _judgment(fresh), ttm=unstamped))
    alt = r.result["score"]["base_alternatives"]["bases"][1]
    assert alt["measured"] is False and alt["note"].startswith("not replayed: ttm.json predates engine 5.7"), alt


# ===========================================================================
# T14 — the declared 6-K bridge is one record (L4)
# ===========================================================================
def test_declared_interim_bridge_is_one_record():
    """§7.2 (real engine offline, test_make_score_57_interim's synthetic 20-F filer): (a) a published bridge —
    base_alternatives (declared_interim published, the annual median replayed once), score.json interim_bridge
    without the both-bases figures, the registry interim_bridge event without them and one base_alternatives event,
    key_numbers' pointer line; (b) declared and REJECTED with a qualifying reason on the median run — scores (L4 alone
    refused it), the declared_interim entry `rejected`, priced by one --ttm replay of the bridge; (c) declared,
    unpinned, no reason — L4's binding refusal (R7-11), no spawn; (d) an orphan bridge ttm.json — computed: false,
    no obligation."""
    import test_make_score_57_interim as TB
    n, rows, tt, fx, j = TB.pipeline()
    a = TB.score(n, j, rows, tt, fx)
    assert a.rc == 0, a.err[-2000:]
    s = a.result["score"]
    assert s["base_alternatives"]["published"] == "declared_interim" and s["base_alternatives"]["replays"] == 1
    assert s["interim_bridge"]["measured_in"] == "base_alternatives"
    assert not {"bridged", "annual_median", "base_change_pct", "measured"} & set(s["interim_bridge"]), s["interim_bridge"]
    ev = [e for e in a.result["entries"] if e.get("event") == "interim_bridge"][0]
    assert not {"base_oe_bridged", "base_oe_annual_median", "weighted_irr_bridged", "tier_bridged", "measured", "note"} \
        & set(ev), ev
    assert len([e for e in a.result["entries"] if e.get("event") == "base_alternatives"]) == 1
    assert '- Bases compared: see "Base alternatives"' in a.result["key"]
    # (b) the median run beside the declared bridge, rejected
    med_n, med_rows = TB.median_record()
    base = med_n["base_oe_per_share"]
    why = (f"the bridged TTM ${tt['ttm_oe_per_share']:.2f}/sh against the median ${base:.2f}/sh rests on a half-year "
           "working-capital swing")
    b = TB.score(med_n, dict(j, ttm_rejection_reason=why), med_rows, tt, fx)
    assert b.rc == 0, b.err[-2500:]
    ba = b.result["score"]["base_alternatives"]
    pub, rej = ba["bases"]
    assert ba["published"] == "annual_median" and pub["why"] == "bridge_rejected" and ba["ttm_rejection_reason"] == why
    assert (rej["kind"], rej["role"], rej["computed"], rej["measured"]) == ("declared_interim", "rejected", True, True)
    assert rej["base_oe_per_share"] == round(tt["ttm_oe_per_share"], 4) and rej["tier_by_numbers"] == n["tier_by_numbers"]
    assert rej["ttm_input_hash"] == E.ttm_inputs_record(tt)["ttm_input_hash"], rej
    sp = b.result["spawns"]
    assert len(sp) == 1 and "--ttm" in sp[0]["argv"] and sp[0]["purpose"] == "base_alternatives", sp
    assert "interim_bridge" not in b.result["score"]   # declared, not the published base
    ev = [e for e in b.result["entries"] if e.get("event") == "base_alternatives"]
    assert len(ev) == 1 and ev[0]["chosen"] == "annual_median" and ev[0]["ttm_kind"] == "declared_interim", ev
    # (c) declared, unpinned, no reason
    c = TB.score(med_n, j, med_rows, tt, live=False)
    c.refused("judgment.json declares interim_bridge but the final run is not pinned through --ttm",
              "or keep it declared and reject it with ttm_rejection_reason")
    assert c.result["spawns"] == []
    # (d) an orphan bridge: judgment.json declines instead
    jd = {k: v for k, v in j.items() if k != "interim_bridge"}
    jd["interim_bridge_declined"] = {"reason": "the H1 6-K (181 days) restates the comparative", "report": None}
    d = TB.score(med_n, jd, med_rows, tt, live=False)
    assert d.rc == 0, d.err[-2000:]
    alt = d.result["score"]["base_alternatives"]["bases"][1]
    assert (alt["kind"], alt["computed"]) == ("declared_interim", False) and alt["note"].startswith(
        "ttm.json is a declared 6-K interim bridge but judgment.json declares no interim_bridge"), alt
    assert d.result["spawns"] == []


# ===========================================================================
# T15 — older output rebuilds unchanged (compat; passes on the old code by design)
# ===========================================================================
def test_pre57_output_rebuilds_unchanged():
    """§5 / D1: on 5.6.0, 5.5.0 and pre-5.4 (no release) records with STALE_FY, a ttm.json for the FY and a median base,
    nothing of R7 runs: no base_alternatives, no section, no event, no spawn, and a malformed ttm_rejection_reason /
    ttm_unavailable_reason is never read — score.json, key_numbers.md and the registry are byte-identical with and
    without them."""
    for rel in ("5.6.0", "5.5.0", None):
        n = hii(release=rel)
        outs = []
        for extra in ({}, {"ttm_rejection_reason": {"bad": 1}, "ttm_unavailable_reason": ""}):
            r = ok(run(n, _judgment(n, **extra), ttm=hii_ttm()))
            outs.append(r)
            assert "base_alternatives" not in r.result["score"] and "Base alternatives" not in r.result["key"]
            assert not [e for e in r.result["entries"] if e.get("event") == "base_alternatives"] and not r.result["spawns"]
        a, b = outs
        assert a.result["score"] == b.result["score"] and a.result["key"] == b.result["key"], rel
        strip = lambda es: [{k: v for k, v in e.items() if k != "date"} for e in es]  # noqa: E731
        assert strip(a.result["entries"]) == strip(b.result["entries"]), rel


# ===========================================================================
# T16 — the registry event
# ===========================================================================
def test_registry_event_identity_and_reserved_keys():
    """§3.10: an unchanged reason against the same TTM window keeps its first date across runs; a new 10-Q window
    (ttm_ytd_end), a new FY or a rewritten reason is a new judgment (re-dated); the event carries no deferred-payment
    field name and passes registry_entry_problem; another ticker's base_alternatives event survives a run."""
    tt, n = hii_ttm(), hii()
    jj = _judgment(n, ttm_rejection_reason=HII_REASON)
    first = ok(run(n, jj, ttm=tt, replies={"ttm": ttm_reply(tt)}))
    reg = first.result["registry"]
    for e in reg["entries"]:
        if e.get("event") == "base_alternatives":
            e["date"] = "2026-08-01"
            assert not set(e) & set(M.IPRD_DEFERRED_EVENT_KEYS) and M.registry_entry_problem(e) is None, e
    other = dict(next(e for e in reg["entries"] if e.get("event") == "base_alternatives"), ticker="OTHR")
    reg["entries"].append(other)
    again = ok(run(n, jj, ttm=tt, replies={"ttm": ttm_reply(tt)}, registry=copy.deepcopy(reg)))
    ev = [e for e in again.result["entries"] if e.get("event") == "base_alternatives" and e["ticker"] == T]
    assert len(ev) == 1 and ev[0]["date"] == "2026-08-01", ev
    assert other in again.result["entries"]
    rew = ok(run(n, dict(jj, ttm_rejection_reason=HII_REASON + " (H1 2026 OCF −$421M)"), ttm=tt,
                 replies={"ttm": ttm_reply(tt)}, registry=copy.deepcopy(reg)))
    ev = [e for e in rew.result["entries"] if e.get("event") == "base_alternatives" and e["ticker"] == T]
    assert ev[0]["date"] > "2026-08-01", ev
    base_ev = {"event": "base_alternatives", "chosen": "annual_median", "reason": "r", "ttm_kind": "ttm",
               "ttm_fy_end": "2025-12-31", "ttm_ytd_end": "2026-06-30"}
    k = M._declaration(base_ev)
    assert k == M._declaration(dict(base_ev, bases=[{"x": 1}], measured=False, stale_fy=True))
    for change in ({"ttm_ytd_end": "2026-09-30"}, {"ttm_fy_end": "2026-12-31"}, {"reason": "r2"},
                   {"chosen": "declared_pin"}, {"ttm_kind": "declared_interim"}):
        assert M._declaration(dict(base_ev, **change)) != k, change
    assert M._EVENT_DECLARATION["base_alternatives"] == ("chosen", "reason", "ttm_kind", "ttm_fy_end", "ttm_ytd_end")


# ===========================================================================
# T17 — the reason traces (L2)
# ===========================================================================
FIL = {"form": "10-Q", "accession": "0000999001-26-000020", "section": "Item 2 MD&A — Liquidity", "filed": "2026-08-05"}
TP = {"url": "https://example.com/h2", "publisher": "Example Wire", "published": "2026-09-28"}


def _fact(fid, used_for, kind="filing", **kw):
    f = {"id": fid, "label": "H1 2026 contract asset build", "value": 640e6, "unit": "USD", "scale": "M", "precision": 0,
         "period": "FY2025", "kind": kind, "type": "actual", "source": dict(FIL if kind == "filing" else TP),
         "snippet": "contract assets rose $640 million in the half", "used_for": used_for}
    f.update(kw)
    return f


def test_rejection_reason_must_trace():
    """§3.8 (L2's check_influence, field ttm_rejection_reason, used_for ttm_rejection): a figure no engine source
    holds and no fact declares is refused; one resting only on a third-party fact is refused (R3); a cited fact that
    does not list used_for ttm_rejection is refused; ttm.json's legs (−$421M, +$428M), the bases and a cited filing fact
    tagged ttm_rejection pass — every refusal before any replay and any write."""
    tt, n = hii_ttm(), hii()
    rep = {"ttm": ttm_reply(tt)}
    r = run(n, _judgment(n, ttm_rejection_reason="Working capital fell $999M in H1 2026"), ttm=tt, replies=rep)
    r.refused("judgment.json ttm_rejection_reason quotes $999M that is neither an engine figure nor a fact it cites")
    tp = {"T/facts.json".replace("T/", f"{T}/"): {"schema": 1, "ticker": T, "facts": [
        _fact("F7", ["context"], kind="third_party", type="estimate", label="analyst H2 inflow estimate", value=500e6,
              snippet="analysts expect $500 million of second-half inflow")]}}
    r = run(n, _judgment(n, ttm_rejection_reason="Working capital: analysts expect $500M of H2 inflow [F7]"), ttm=tt,
            replies=rep, files=tp)
    r.refused("judgment.json ttm_rejection_reason rests only on third-party facts (F7)")
    untagged = {f"{T}/facts.json": {"schema": 1, "ticker": T, "facts": [_fact("F4", ["context"])]}}
    r = run(n, _judgment(n, ttm_rejection_reason="Receivables: contract assets rose $640M in H1 2026 [F4]"), ttm=tt,
            replies=rep, files=untagged)
    r.refused("judgment.json ttm_rejection_reason cites F4, but F4 does not list used_for ttm_rejection")
    legs = ("Working capital: H1 2026 operating cash flow was −$421M (ttm.json current-YTD leg) against +$428M in H1 "
            "2025, so the TTM base is −$3.48/sh against the $16.14/sh median")
    r = ok(run(n, _judgment(n, ttm_rejection_reason=legs), ttm=tt, replies=rep))
    assert r.result["score"]["declared_facts"]["influence"]["ttm_rejection_reason"]["engine_numbers"] == 4
    tagged = {f"{T}/facts.json": {"schema": 1, "ticker": T, "facts": [_fact("F4", ["ttm_rejection"])]}}
    r = ok(run(n, _judgment(n, ttm_rejection_reason="Receivables: contract assets rose $640M in H1 2026 [F4]"), ttm=tt,
               replies=rep, files=tagged))
    assert r.result["score"]["declared_facts"]["influence"]["ttm_rejection_reason"]["facts"] == ["F4"]
    # the rejected TTM's replayed figures trace too (the base_alternatives leaves): a 6.50% replayed IRR
    rep2 = {"ttm": ttm_reply(tt, irr=0.065, tier="D", f_subtype=None)}
    r = ok(run(n, _judgment(n, ttm_rejection_reason="Working capital: the TTM replays at 6.50% against the median's "
                                                    "10.33%"), ttm=tt, replies=rep2))
    assert r.result["score"]["base_alternatives"]["bases"][1]["weighted_irr"] == 0.065


# ===========================================================================
# T18 — declared pins (default Q18) and the payable pin
# ===========================================================================
def _declared_pin(stale=True):
    n = _pinned(hii(fragility_flags=[STALE] if stale else []), 15.0, window={"window": "fy"})
    bo = {"value": 15.0, "kind": "filing", "source": "test: the median $16.14 less a one-off FY2025 receipt",
          "reason": "test: the 3-yr median carries a one-off", "basis_window": {"window": "fy"}}
    return n, bo


def test_declared_pin_needs_the_reason_payable_does_not():
    """Default Q18 (R7_DECLARED_PIN_RULE = "require"): a STALE_FY declared base_override pin (basis_window fy) beside an
    eligible TTM is refused without the reason; with one the TTM is `rejected` (one --ttm replay) and the annual median
    an alternative from the record, "not replayed" (its own impact is the base_override event's). A STALE_FY payable
    pin beside a ttm.json needs nothing: no TTM entry, the annual median from payable_impact, no R7 spawn."""
    tt = hii_ttm()
    n, bo = _declared_pin()
    run(n, _judgment(n, base_override=bo), ttm=tt).refused(
        "[TTM-REJ0] STALE_FY fires and ttm.json holds a TTM for this run (to 2026-06-30: $-3.48/share) but the "
        "published base is the declared base_override pin ($15.00/share)")
    r = ok(run(n, _judgment(n, base_override=bo, ttm_rejection_reason=HII_REASON), ttm=tt,
               replies={"ttm": ttm_reply(tt)}))
    ba = r.result["score"]["base_alternatives"]
    pub, rej, med = ba["bases"]
    assert ba["published"] == "declared_pin" and pub["why"] == "ttm_rejected" and ba["replays"] == 1, ba
    assert (rej["kind"], rej["role"], rej["measured"]) == ("ttm", "rejected", True), rej
    assert (med["kind"], med["measured"], med["base_oe_per_share"]) == ("annual_median", False, 16.1404), med
    assert med["note"] == ("not replayed: the published base is a declared base_override pin — its own impact is in "
                           "the base_override event"), med
    assert [x["purpose"] for x in r.result["spawns"]] == ["base_alternatives"], r.result["spawns"]
    with switch("R7_DECLARED_PIN_RULE", "exempt"):
        with folder({"ttm.json": tt, "judgment.json": {"base_override": bo}}) as fo:
            plan = M.ttm_rejection_state(fo, n, {"base_override": bo})
            assert plan["required"] is False, plan
            msg = refusal(M.ttm_rejection_state, fo, n, {"base_override": bo, "ttm_rejection_reason": HII_REASON})
            assert "declared base_override pins are exempt (default Q18, R7_DECLARED_PIN_RULE)" in msg, msg
    import test_make_score_55 as T55
    pn, pj = T55._payable(CUR)
    pn = dict(pn, fragility_flags=[STALE])
    r = ok(run(pn, pj, ttm=tt, replies={"other": median_reply(base=77.78, irr=0.2731, tier="S")}))
    ba = r.result["score"]["base_alternatives"]
    assert ba["published"] == "payable_5y" and [b["kind"] for b in ba["bases"]] == ["payable_5y", "annual_median"], ba
    med = ba["bases"][1]
    assert (med["base_oe_per_share"], med["weighted_irr"], med["tier_by_numbers"], med["measured"]) == (
        77.78, 0.2731, "S", True), med
    assert [x["purpose"] for x in r.result["spawns"]] == [None], r.result["spawns"]   # payable_pin_impact's own replay
    assert not [e for e in r.result["entries"] if e.get("event") == "base_alternatives"]


# ===========================================================================
# T19 / T20 — the real engine (acquired IPR&D, PR #47)
# ===========================================================================
def test_ttm_alternative_takes_its_own_iprd_window():
    """§7.1 (real engine offline, test_make_score_iprd's BRIDGE): a STALE_FY median run at the synthetic filer with a
    $20M FY2025 and a $30M H1 2026 acquired-IPR&D charge, beside ttm.json (2.1/share on 98M shares): the rejected TTM
    replays with --ttm and takes the TTM window and ttm.json's count — $50M / 98M = $0.5102/share off every IV — while
    the published median keeps its FY window ($20M / 100M = $0.20); the replay carried no DCF_IPRD_HOLD and no
    override toggle."""
    import test_make_score_iprd as TMI
    TI = TMI.TI
    facts = TI._ttm_ytd_facts()
    ttm = TI._ttm_doc(2.1, 98e6)
    n = TI._ok(TI._run(facts, ttm=ttm))
    assert any(f.startswith("STALE_FY") for f in n["fragility_flags"]) and n["ttm_inputs"] is None
    assert E.iprd_charge_per_share(n) == 0.2, E.iprd_charge_per_share(n)
    why = (f"the TTM base $2.10/sh against the median ${n['base_oe_per_share']:.2f}/sh rests on a half-year "
           "working-capital swing")
    m = copy.deepcopy(n)
    m["ticker"] = T
    r = Run(m, TMI._with_applied(n, TMI._j(ttm_rejection_reason=why)))
    try:
        for name in ("dcf_engine.py", "ttm.py"):
            with open(os.path.join(r.sysdir, name), "w", encoding="utf-8") as f:
                f.write(TMI.BRIDGE)
        with open(os.path.join(r.sysdir, "bridge.json"), "w", encoding="utf-8") as f:
            json.dump({"paths": [HERE, SYS], "fixture": TI._syn_fixture(facts, 30.0), "ttm_no_override": None}, f)
        with open(os.path.join(r.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(ttm, f)
        r.run()
        assert r.rc == 0, r.err[-2500:]
        ba = r.score()["base_alternatives"]
        with open(os.path.join(r.sysdir, "SPAWNED_dcf_engine.py.txt"), encoding="utf-8") as f:
            spawns = [json.loads(line) for line in f if line.strip()]
    finally:
        r.close()
    pub, rej = ba["bases"]
    assert pub["iprd_charge_per_share"] == 0.2 and pub["iprd_treatment"] == "one_time_value_deduction", pub
    assert rej["iprd_charge_per_share"] == round(50e6 / 98e6, 4) and rej["iprd_treatment"] == "one_time_value_deduction"
    assert rej["base_oe_per_share"] == 2.1 and rej["measured"] is True, rej
    assert len(spawns) == 1 and "--ttm" in spawns[0]["argv"] and spawns[0]["hold"] is None, spawns
    assert spawns[0]["no_overrides"] is None


def test_engine_amortized_median_refusal_names_r7():
    """§8 (engine text only, no logic change; default Q17): under STALE_FY beside a ttm.json TTM base a median-native
    iprd_amortized pin is still refused (BAD_BASE_OVERRIDE, exit 3) — the message keeps "native_base must be
    'ttm_json'" and now names ttm_rejection_reason (a rejected TTM leaves the median with the one-time deduction)."""
    import test_engine_iprd as TI
    facts = TI._facts(expense={2023: 15e6, 2025: 20e6})
    ttm = TI._ttm_doc(2.1, 100e6)
    med = TI.amortized_decl(TI._recurrent())
    out = TI._run(facts, extra=["--base-oe-ps", repr(med["value"])], judgment={"base_override": med}, ttm=ttm)
    assert out["exit"] == 3 and "native_base must be 'ttm_json'" in out["stdout"], out["stdout"][-800:]
    assert ("unless judgment.json ttm_rejection_reason rejects it (engine 5.7, R7)" in out["stdout"]
            and "a rejected TTM leaves the median with the one-time deduction" in out["stdout"]), out["stdout"][-800:]


# ===========================================================================
# Default Q14 — ttm_unavailable_reason quotes ttm.py's exit-3 message
# ===========================================================================
def _ttm_py_exit3(facts):
    import engine55_harness as H
    import test_engine_55 as T55
    out = H.run_ttm("SYN", fixture=T55._syn_fixture(facts))
    assert out["exit"] == 3, (out["exit"], out["stderr"][-800:])
    return out["stderr"].strip().splitlines()[-1]


def test_ttm_unavailable_reason_quotes_ttm_py():
    """Default Q14 (R7_TTM_UNAVAILABLE_RULE = "require"): ttm.py's REAL exit-3 messages (offline, the synthetic filer
    with no 10-Q; with no capex filed; with a current but no prior-year YTD) pass ttm_unavailable_problem for their
    own run and match TTM_PY_EXIT3_RES problem by problem; a STALE_FY 10-K median with no ttm.json refuses without
    the quote [TTM-UNAV0], refuses free text [TTM-UNAV1] and another ticker's / CIK's / FY's message [TTM-UNAV2]; the
    field beside a TTM for this run, without STALE_FY or at a 20-F filer is refused; the switch "off" records it
    without requiring it."""
    import test_engine_55 as T55
    syn = {"ticker": "SYN", "cik": 999001, "latest_period_end": "2025-12-31"}
    no_q = _ttm_py_exit3(T55._syn_facts())
    no_capex = _ttm_py_exit3(T55._syn_facts(capex={y: None for y in T55.SYN_YEARS}))
    part = T55._syn_facts()
    T55._syn_put(part, "NetCashProvidedByUsedInOperatingActivities", "USD",
                 {"start": "2026-01-01", "end": "2026-06-30", "val": 90e6, "form": "10-Q", "fp": "Q2", "fy": 2026,
                  "filed": "2026-08-05", "accn": "0000999001-26-000030"})
    no_prior = _ttm_py_exit3(part)
    for msg in (no_q, no_capex, no_prior):
        assert msg.startswith("ttm.py: cannot compute TTM for SYN (CIK 999001): "), msg
        assert M.ttm_unavailable_problem(msg, syn, "SYN") is None, (msg, M.ttm_unavailable_problem(msg, syn, "SYN"))
        # the whole line, problem by problem, is ttm.py's own words (review fix 3: a verbatim quote)
        parsed = M.parse_ttm_py_exit3(msg)
        assert parsed is not None and len(parsed[1]) == len(msg.split(": ", 2)[2].split("; ")), (msg, parsed)
    assert "ocf: no post-FY YTD fact (no 10-Q since the 2025-12-31 fiscal year end)" in no_q
    assert "capex: no capex facts in companyfacts under any candidate tag" in no_capex
    assert "ocf: no prior-year YTD fact matching 2025-06-30 (FY start 2025-01-01)" in no_prior
    assert "UNAV2" in M.ttm_unavailable_problem(no_q, dict(syn, latest_period_end="2026-12-31"), "SYN")
    assert "UNAV2" in M.ttm_unavailable_problem(no_q, syn, "OTHR") and "UNAV2" in M.ttm_unavailable_problem(
        no_q, dict(syn, cik=5), "SYN")
    assert M.ttm_unavailable_problem("ttm.py failed on the 10-Q", syn, "SYN").startswith("[TTM-UNAV1]")
    assert M.ttm_unavailable_problem("", syn, "SYN").startswith("[TTM-UNAV0]")
    # end to end: a STALE_FY 10-K median, no ttm.json
    n = hii()
    run(n, _judgment(n)).refused("[TTM-UNAV0] STALE_FY fires at a 10-K filer and ttm.json holds no TTM for this run's "
                                 "latest FY (no ttm.json) — run python3 _system/ttm.py TST and pass --ttm in the final "
                                 "run (or reject the TTM with ttm_rejection_reason); when ttm.py exits 3, quote the "
                                 "message it prints in judgment.json ttm_unavailable_reason (default Q14)")
    run(n, _judgment(n, ttm_unavailable_reason="ttm.py could not build it")).refused("[TTM-UNAV1]")
    run(n, _judgment(n, ttm_unavailable_reason=unavailable(fy="2024-12-31"))).refused(
        "[TTM-UNAV2] judgment.json ttm_unavailable_reason quotes another run's ttm.py message ('sbc: no post-FY YTD "
        "fact' is about the fiscal year ending 2024-12-31, not this run's latest FY (2025-12-31))")
    run(n, _judgment(n, ttm_unavailable_reason=unavailable(t="HII"))).refused("[TTM-UNAV2]", "it names HII, not TST")
    run(n, _judgment(n, ttm_unavailable_reason=unavailable()), ttm=hii_ttm()).refused(
        "[TTM-UNAV] judgment.json ttm_unavailable_reason is declared but ttm.json holds a TTM for this run (to "
        "2026-06-30) — pin it with --ttm or reject it with ttm_rejection_reason — remove it")
    fresh = hii(fragility_flags=[])
    run(fresh, _judgment(fresh, ttm_unavailable_reason=unavailable())).refused(
        "[TTM-UNAV] judgment.json ttm_unavailable_reason is declared but STALE_FY does not fire")
    ads = {"ratio": 1.0, "source": "cover", "reason": "no ADS"}
    nf = hii(filer_annual_form="20-F", ads_ratio=ads)
    run(nf, _judgment(nf, ttm_unavailable_reason=unavailable(),
                      interim_bridge_declined={"reason": "the H1 6-K (181 days) has no cash-flow statement",
                                               "report": None})).refused(
        "20-F filers record why no TTM exists in interim_bridge_declined (R2)")
    with switch("R7_TTM_UNAVAILABLE_RULE", "off"), folder({"judgment.json": {}}) as fo:
        plan = M.ttm_rejection_state(fo, n, {})
        assert plan["unavailable_required"] is False and plan["unavailable_reason"] is None, plan
        plan = M.ttm_rejection_state(fo, n, {"ttm_unavailable_reason": unavailable()})
        assert plan["unavailable_reason"] == unavailable(), plan
        assert "[TTM-UNAV1]" in refusal(M.ttm_rejection_state, fo, n, {"ttm_unavailable_reason": "x"})


# ===========================================================================
# Default Q16 — the entry alert
# ===========================================================================
def test_rejection_lifting_the_tier_into_s_a_suppresses_the_entry_alert():
    """Default Q16 (R7_ALERT_RULE = "suppress_raise"): a STALE_FY median published at Tier A whose rejected TTM scores
    Tier F closes the entry gate (alert_eligible false, the reason names the rejection); a rejected TTM scoring at or
    above the published tier does not; the switch "off" restores today's gates."""
    tt = hii_ttm()
    n = hii(tier_by_numbers="A", implied_irr_weighted=0.2233)
    jj = _judgment(n, ttm_rejection_reason=HII_REASON)
    r = ok(run(n, jj, ttm=tt, replies={"ttm": ttm_reply(tt)}))
    s = r.result["score"]
    assert s["tier_final"] == "A" and s["alert_eligible"] is False, s
    assert s["alert_suppressed_reason"] == ("tier rests on a TTM rejection (ttm_rejection_reason): the rejected TTM "
                                            "scores Tier F, the published annual median Tier A"), s
    r = ok(run(n, jj, ttm=tt, replies={"ttm": ttm_reply(tt, irr=0.31, tier="S", f_subtype=None)}))
    assert r.result["score"]["alert_eligible"] is True and "alert_suppressed_reason" not in r.result["score"]
    ba = {"published": "annual_median", "bases": [{"role": "rejected", "kind": "ttm", "measured": True,
                                                    "tier_by_numbers": "C"}]}
    assert M.ttm_rejection_alert_reasons(ba, "A") and not M.ttm_rejection_alert_reasons(ba, "B")
    assert M.ttm_rejection_alert_reasons({"published": "annual_median", "bases": [
        {"role": "rejected", "kind": "ttm", "measured": True, "computed": False, "tier_by_numbers": None}]}, "S")
    assert not M.ttm_rejection_alert_reasons({"published": "annual_median", "bases": [
        {"role": "rejected", "kind": "ttm", "measured": False, "tier_by_numbers": "F"}]}, "A")   # unmeasured
    with switch("R7_ALERT_RULE", "off"):
        assert M.ttm_rejection_alert_reasons(ba, "A") == []


# ===========================================================================
# The main agent's decision: capex_unlisted_ack reasons trace like every 5.7 reason
# ===========================================================================
ME = "PaymentsToAcquireMachineryAndEquipment"
UNLISTED = (f"CAPEX_UNLISTED_COMPONENT:{ME} — FY2025 795,392,000 (accession 0001492691-26-000010) vs the whole "
            "component capex leg 1,066,000 (PaymentsToAcquireOtherProductiveAssets): a capex-like cash-flow tag on no "
            "engine capex list exceeds the component leg in the same filing")


def test_capex_unlisted_ack_reasons_trace():
    """R7 lane (the main agent's decision, 2026-10-21): L9's capex_unlisted_ack reasons go through L2's check on a 5.7
    run — the flag's own figure traces; a figure no source holds is refused naming the tag; one resting only on a
    third-party fact is refused; a cited filing fact must list used_for capex_unlisted_ack (influence_tag reads the
    map's prefix); output older than 5.7 is never traced."""
    n = _numbers(fragility_flags=[UNLISTED])
    ok(run(n, _judgment(n, capex_unlisted_ack={ME: "lease buy-outs of $795.4M in FY2025, not capex (test)"})))
    run(n, _judgment(n, capex_unlisted_ack={ME: "lease buy-outs of $812.0M in FY2025, not capex"})).refused(
        f"judgment.json capex_unlisted_ack.{ME} quotes $812.0M that is neither an engine figure nor a fact it cites")
    fact = _fact("F5", ["capex_unlisted_ack"], label="FY2025 tractor lease buy-outs", value=812e6, period="FY2025",
                 snippet="we bought out tractor leases for $812 million")
    ok(run(n, _judgment(n, capex_unlisted_ack={ME: "tractor lease buy-outs of $812M in FY2025 [F5], not capex"}),
           files={f"{T}/facts.json": {"schema": 1, "ticker": T, "facts": [fact]}}))
    run(n, _judgment(n, capex_unlisted_ack={ME: "tractor lease buy-outs of $812M in FY2025 [F5], not capex"}),
        files={f"{T}/facts.json": {"schema": 1, "ticker": T, "facts": [dict(fact, used_for=["context"])]}}).refused(
        f"judgment.json capex_unlisted_ack.{ME} cites F5, but F5 does not list used_for capex_unlisted_ack")
    tp = _fact("F6", ["context"], kind="third_party", type="estimate", label="analyst lease estimate", value=812e6,
               snippet="analysts put lease buy-outs at $812 million")
    run(n, _judgment(n, capex_unlisted_ack={ME: "lease buy-outs of $812M [F6], not capex"}),
        files={f"{T}/facts.json": {"schema": 1, "ticker": T, "facts": [tp]}}).refused(
        f"judgment.json capex_unlisted_ack.{ME} rests only on third-party facts (F6)")
    import facts as F
    assert F.influence_tag(f"capex_unlisted_ack.{ME}") == "capex_unlisted_ack" and "capex_unlisted_ack" in F.USED_FOR
    assert "capex_unlisted_ack" in F.THIRD_PARTY_NOT_SOLE_SUPPORT
    assert F.influence_tag("ttm_rejection_reason") == "ttm_rejection" and F.influence_tag("moat_scorecard.x") == \
        "moat_scorecard.x"
    old = _numbers(release="5.6.0", fragility_flags=[UNLISTED])
    ok(run(old, _judgment(old, capex_unlisted_ack={ME: "lease buy-outs of $812.0M in FY2025, not capex"})))


# ===========================================================================
# The switches (defaults Q13 / Q15) and the worked example
# ===========================================================================
def test_switches_scope_and_median_beside_ttm():
    """Default Q13 (R7_OBLIGATION_SCOPE = "stale_fy"): "ttm_present" binds a fresh-FY median beside a TTM for its FY
    too (the refusal then says nothing of STALE_FY). Default Q15 (R7_MEDIAN_BESIDE_TTM = True): off, a TTM-published
    STALE_FY run records the median from the run, not replayed, and says why."""
    tt = hii_ttm()
    fresh = hii(fragility_flags=[])
    with folder({"ttm.json": tt, "judgment.json": {}}) as fo:
        assert M.ttm_rejection_state(fo, fresh, {})["required"] is False
        with switch("R7_OBLIGATION_SCOPE", "ttm_present"):
            msg = refusal(M.ttm_rejection_state, fo, fresh, {})
            assert msg and "[TTM-REJ0] ttm.json holds a TTM for this run (to 2026-06-30" in msg, msg
    n, ptt = _ttm_published()
    with folder({"ttm.json": ptt, "judgment.json": {}}) as fo, switch("R7_MEDIAN_BESIDE_TTM", False):
        plan = M.ttm_rejection_state(fo, n, {})
        ba = M.build_base_alternatives(T, fo, n, {}, plan)
        med = ba["bases"][1]
        assert ba["replays"] == 0 and med["measured"] is False, ba
        assert med["note"] == "not replayed: R7_MEDIAN_BESIDE_TTM is off (default Q15 switch)", med
    assert (M.R7_OBLIGATION_SCOPE, M.R7_TTM_UNAVAILABLE_RULE, M.R7_MEDIAN_BESIDE_TTM, M.R7_ALERT_RULE,
            M.R7_DECLARED_PIN_RULE) == ("stale_fy", "require", True, "suppress_raise", "require")


def test_worked_example_is_the_hii_record():
    """_system/examples/ttm_rejection_hii.json (WORKER_SPEC step 4 points at it): its judgment field qualifies and its
    base_alternatives block is the record T5 builds from HII's figures (the input hash of the example's ttm.json)."""
    with open(os.path.join(SYS, "examples", "ttm_rejection_hii.json"), encoding="utf-8") as f:
        ex = json.load(f)
    assert ex["judgment"]["ttm_rejection_reason"] == HII_REASON and M.ttm_rejection_problem(HII_REASON) is None
    tt = dict(hii_ttm(), **{k: ex["ttm_json"][k] for k in ("ticker", "cik", "entity", "engine_release")})
    assert ex["ttm_json"] == tt, "the example's ttm.json is HII's legs"
    exp = _hii_expected(tt)
    assert ex["score_base_alternatives"] == exp, json.dumps(ex["score_base_alternatives"], indent=1)
    assert ex["key_numbers"] == HII_KEY


# ===========================================================================
# Review fixes (adversarial review of 626b157, 2026-10-21) — each fails on 626b157
# ===========================================================================
SBC_WITHDRAWN = ("ttm.json used a sbc_override that judgment.json no longer declares — rerun ttm.py TST with the "
                 "current judgment.json")
PRE57 = ("ttm.json predates engine 5.7 (engine_release none): its legs were built without the 5.7 capex rules — rerun "
         "ttm.py TST")
UNBUILDABLE = " — ttm.py cannot rebuild it (judgment.json ttm_unavailable_reason quotes its exit-3 message)"
EXIT3_HEAD = "ttm.py: cannot compute TTM for TST (CIK 1): "
NO_CAPEX = ("capex: no capex facts in companyfacts under any candidate tag and no capex_override in judgment.json — "
            "refusing to zero-fill (same DATA_GAP standard as the engine)")


def _withdrawn_ttm():
    """HII's ttm.json as ttm.py built it with a sbc_override judgment.json has since withdrawn (APA: the 10-Qs print no
    SBC line, so the override filled the current-YTD leg)."""
    return hii_ttm(overrides_used=[{"field": "sbc", "value": 30e6, "kind": "estimate", "source": "s",
                                    "legs_filled": {"ytd_current": {"period": ["2026-01-01", "2026-06-30"],
                                                                    "amount": 15e6}}}])


def _unstamped_ttm():
    doc = hii_ttm()
    del doc["engine_release"]
    return doc


def hii_csv(**over):
    """HII's FY2025 financials_history.csv row as a 5.7 engine writes it (a literal; never read from HII/)."""
    row = {"period_end": "2025-12-31", "fy_label": "2025", "revenue": 12484000000, "net_income": 605000000,
           "ocf": 1196000000, "ocf_tag": "NetCashProvidedByUsedInOperatingActivities", "capex": 402000000,
           "capex_assumed_zero": False, "capex_tag": "PaymentsToAcquirePropertyPlantAndEquipment",
           "sbc_tag": "ShareBasedCompensation", "sbc": 54000000, "shares_diluted": 39300000,
           "shares_tag": "WeightedAverageNumberOfDilutedSharesOutstanding", "oe_per_share": 18.829516539440203,
           "capex_ppe": 402000000, "capex_intangibles": "", "capex_source": "rollup", "shares_split_factor": ""}
    row.update(over)
    return [row]


def test_unbuildable_stale_ttm_json_scores_on_the_exit3_quote():
    """Review fix 1 (design 11 §3.3 / §14 item 6: a TTM the worker can rebuild refuses under the obligation, one the
    worker cannot is recorded, never refused). A STALE_FY 10-K median beside a 'fixable' ttm.json for its FY (an
    override judgment.json withdrew; a pre-5.7 stamp) whose ttm.py rerun exits 3 — ttm.py writes nothing on exit 3, so
    the stale file stays: judgment.json ttm_unavailable_reason quoting the exit-3 line stands for it — no obligation,
    no replay, no registry event; the TTM entry computed: false with the file's note + "ttm.py cannot rebuild it".
    R7-1 and R7-7 name that path. The quote is still checked; with ttm_rejection_reason too, beside an eligible TTM,
    or without STALE_FY it is refused."""
    n = hii()
    msg = unavailable()
    for doc, note in ((_withdrawn_ttm(), SBC_WITHDRAWN), (_unstamped_ttm(), PRE57)):
        with folder({"ttm.json": doc, "judgment.json": {}}) as fo:
            plan = M.ttm_rejection_state(fo, n, {TTM_UNAVAILABLE: msg})
            assert (plan["required"], plan["ttm_unbuildable"], plan["unavailable_reason"]) == (False, True, msg), plan
        r = ok(run(n, _judgment(n, ttm_unavailable_reason=msg), ttm=doc))
        ba = r.result["score"]["base_alternatives"]
        assert ba["ttm_unavailable_reason"] == msg and ba["ttm_rejection_reason"] is None and ba["replays"] == 0, ba
        pub, alt = ba["bases"]
        assert pub["why"] == "no_ttm_for_run", pub
        assert (alt["kind"], alt["role"], alt["computed"], alt["measured"]) == ("ttm", "alternative", False, False), alt
        assert alt["base_oe_per_share"] is None and alt["ytd_end"] == "2026-06-30", alt
        assert alt["note"] == note + UNBUILDABLE, alt
        assert r.result["spawns"] == [] and not [e for e in r.result["entries"] if e.get("event") == "base_alternatives"]
        assert (f"- Alternative: TTM to 2026-06-30 (ttm.py, 10-Q YTD; FY 2025-12-31) not computed — {note}{UNBUILDABLE}"
                in r.result["key"]), section(r.result["key"])
        # the refusals a worker meets first name the way out
        run(n, _judgment(n), ttm=doc).refused(
            R7_1, f" — ttm.json cannot be priced as it stands: {note}; when ttm.py exits 3 instead (it cannot rebuild "
                  "this TTM), quote the line it prints in judgment.json ttm_unavailable_reason")
        run(n, _judgment(n, ttm_rejection_reason=HII_REASON), ttm=doc).refused(
            "the TTM this run rejects cannot be priced: " + note, "when ttm.py exits 3 instead (it cannot rebuild this "
            "TTM), drop ttm_rejection_reason and quote the line it prints in judgment.json ttm_unavailable_reason")
    doc = _withdrawn_ttm()
    run(n, _judgment(n, ttm_unavailable_reason=msg, ttm_rejection_reason=HII_REASON), ttm=doc).refused(
        "judgment.json ttm_rejection_reason is declared but ttm.py cannot rebuild ttm.json's TTM (judgment.json "
        "ttm_unavailable_reason quotes its exit-3 message) — nothing priceable to reject — remove it")
    run(n, _judgment(n, ttm_unavailable_reason="ttm.py could not rebuild it"), ttm=doc).refused("[TTM-UNAV1]")
    run(n, _judgment(n, ttm_unavailable_reason=unavailable(fy="2024-12-31")), ttm=doc).refused("[TTM-UNAV2]")
    run(n, _judgment(n, ttm_unavailable_reason=msg), ttm=hii_ttm()).refused(
        "[TTM-UNAV] judgment.json ttm_unavailable_reason is declared but ttm.json holds a TTM for this run (to "
        "2026-06-30) — pin it with --ttm or reject it with ttm_rejection_reason — remove it")
    fresh = hii(fragility_flags=[])
    run(fresh, _judgment(fresh, ttm_unavailable_reason=msg), ttm=doc).refused(
        "[TTM-UNAV] judgment.json ttm_unavailable_reason is declared but STALE_FY does not fire")


TTM_UNAVAILABLE = "ttm_unavailable_reason"


def test_q13_switch_alone_leaves_q14_on_stale_fy():
    """Review fix 2 (12_lane_defaults: each default flips by one constant): Q14 is defined on STALE_FY 10-K folders,
    so flipping Q13 alone (R7_OBLIGATION_SCOPE "ttm_present") leaves a fresh-FY 10-K median with no ttm.json owing
    nothing — it scores — and a ttm_unavailable_reason there is still misplaced; a STALE_FY one still owes the quote.
    (Q13 flipped beside a TTM for the run binds the fresh-FY median: test_switches_scope_and_median_beside_ttm.)"""
    fresh = hii(fragility_flags=[])
    with folder({"judgment.json": {}}) as fo, switch("R7_OBLIGATION_SCOPE", "ttm_present"):
        msg = refusal(M.ttm_rejection_state, fo, fresh, {})
        assert msg is None, msg
        plan = M.ttm_rejection_state(fo, fresh, {})
        assert (plan["scope"], plan["required"], plan["unavailable_required"]) == (True, False, False), plan
        assert M.build_base_alternatives(T, fo, fresh, {}, plan) is None
        msg = refusal(M.ttm_rejection_state, fo, fresh, {TTM_UNAVAILABLE: unavailable()})
        assert msg and "[TTM-UNAV] judgment.json ttm_unavailable_reason is declared but STALE_FY does not fire" in msg, msg
        msg = refusal(M.ttm_rejection_state, fo, hii(), {})
        assert msg and "[TTM-UNAV0] STALE_FY fires at a 10-K filer" in msg, msg
    # Q13 flipped beside a stale ttm.json ttm.py cannot rebuild: the reason binds the fresh FY, so the exit-3 quote
    # stands for the file there too
    with folder({"ttm.json": _withdrawn_ttm(), "judgment.json": {}}) as fo, switch("R7_OBLIGATION_SCOPE", "ttm_present"):
        plan = M.ttm_rejection_state(fo, fresh, {TTM_UNAVAILABLE: unavailable()})
        assert (plan["required"], plan["ttm_unbuildable"]) == (False, True), plan


def _real_exit3(facts, judgment=None):
    import engine55_harness as H
    import test_engine_55 as T55
    out = H.run_ttm("SYN", judgment=judgment if judgment is not None else {}, fixture=T55._syn_fixture(facts))
    assert out["exit"] == 3, (out["exit"], out["stderr"][-800:])
    return out["stderr"].strip().splitlines()[-1]


def _syn_ytd(facts, legs):
    """10-Q YTD facts (H1 2025, H1 2026) on the synthetic filer: [(tag, unit, prior, current)]."""
    import test_engine_55 as T55
    for tag, unit, prior, cur in legs:
        for start, end, v in (("2025-01-01", "2025-06-30", prior), ("2026-01-01", "2026-06-30", cur)):
            T55._syn_put(facts, tag, unit, {"start": start, "end": end, "val": v, "form": "10-Q", "fp": "Q2",
                                            "fy": int(end[:4]), "filed": f"{end[:4]}-08-05",
                                            "accn": f"0000999001-{end[2:4]}-000020"})


def test_ttm_unavailable_quote_is_the_whole_line_and_this_runs():
    """Review fix 3: ttm_unavailable_reason is ttm.py's exit-3 line verbatim — the head, then problems in ttm.py's own
    words, each whole, joined by "; ", nothing else (prose around it, a fragment of a problem: [TTM-UNAV1]). Every
    dated problem names this run's latest FY (the intangible-currency legs too); an undated one the record contradicts
    is [TTM-UNAV2]: "no annual (FY) fact" / "no capex facts" while this run's latest-FY row of financials_history.csv
    carries that leg from a USD us-gaap fact ttm.py reads, an override-currency problem when judgment.json declares no
    such override or declares it in USD. Without that evidence (an FX-converted run, the filing's own instance, an
    override or assumed-zero row, no CSV row) an undated problem stands. ttm.py's real override-currency and
    intangible-currency lines pass for their own run."""
    import test_engine_55 as T55
    import ttm as TTMPY
    n, rows = hii(), hii_csv()

    def prob(text, rec=n, rr=rows, jj=None):
        return M.ttm_unavailable_problem(text, rec, T, rows=rr, j=jj or {})

    # the review's three accepted strings, refused
    assert (prob(EXIT3_HEAD + "sbc: no annual (FY) fact") or "").startswith("[TTM-UNAV2]")
    assert (prob(EXIT3_HEAD + NO_CAPEX.split(" —")[0]) or "").startswith("[TTM-UNAV1]")   # a fragment of the problem
    assert (prob(EXIT3_HEAD + NO_CAPEX) or "").startswith("[TTM-UNAV2]")
    assert (prob("We did not run ttm.py this quarter. " + EXIT3_HEAD + "ocf: no annual (FY) fact") or "").startswith(
        "[TTM-UNAV1]")
    for bad in (unavailable() + " (checked 2026-10-20)", "“" + unavailable() + "”", unavailable() + ";",
                unavailable() + "; sbc: it is late"):
        assert (prob(bad) or "").startswith("[TTM-UNAV1]"), bad
    p = prob(EXIT3_HEAD + "ocf: no annual (FY) fact")
    assert p and "'ocf: no annual (FY) fact'" in p and "NetCashProvidedByUsedInOperatingActivities" in p, p
    assert (prob(EXIT3_HEAD + "shares_diluted: no annual (FY) fact") or "").startswith("[TTM-UNAV2]")
    # whole problems joined by "; " pass; leading / trailing whitespace is not text
    two = unavailable() + "; " + unavailable(leg="capex").split(": ", 2)[2]
    assert prob(two) is None and prob("  " + unavailable() + "\n") is None
    # no evidence against an undated problem: it stands
    assert prob(EXIT3_HEAD + "sbc: no annual (FY) fact", rr=hii_csv(sbc_tag="OVERRIDE")) is None
    assert prob(EXIT3_HEAD + "sbc: no annual (FY) fact", rr=[]) is None
    assert prob(EXIT3_HEAD + "sbc: no annual (FY) fact", rr=hii_csv(period_end="2024-12-31")) is None
    assert prob(EXIT3_HEAD + "ocf: no annual (FY) fact", rec=dict(n, fx_conversion={"from_currency": "CAD"})) is None
    assert prob(EXIT3_HEAD + "ocf: no annual (FY) fact",
                rec=dict(n, annual_from_instance={"applied": True, "periods_added": ["2025-12-31"]})) is None
    assert prob(EXIT3_HEAD + NO_CAPEX, rr=hii_csv(capex_source="assumed_zero", capex_tag="", capex=0, capex_ppe=0)) is None
    assert prob(EXIT3_HEAD + "shares_diluted: no annual (FY) fact",
                rr=hii_csv(shares_tag="FALLBACK:dei:EntityCommonStockSharesOutstanding@2026-01-31")) is None
    # the tags make_score holds ttm.py to are ttm.py's own
    assert M.TTM_PY_LEG_TAGS == {"ocf": tuple(TTMPY.OCF_TAGS), "capex": tuple(TTMPY.CAPEX_TAGS),
                                 "sbc": tuple(TTMPY.SBC_TAGS), "shares_diluted": tuple(TTMPY.SHARE_TAGS)}
    # ttm.py's REAL override-currency line (a sbc_override with no currency, a CAD core fact, no SBC 10-Q legs) and
    # intangible-currency line (H1 2026 intangible purchases filed only in CNY)
    syn = {"ticker": "SYN", "cik": 999001, "latest_period_end": "2025-12-31"}
    ov = {"value": 10e6, "kind": "estimate", "source": "s", "reason": "r"}
    f = T55._syn_facts()
    _syn_ytd(f, [("NetCashProvidedByUsedInOperatingActivities", "USD", 100e6, 110e6), (T55.PRIMARY, "USD", 25e6, 26e6),
                 (T55.SYN_SHARE_TAG, "shares", 100e6, 100e6)])
    T55._syn_put(f, "Revenues", "CAD", T55._ctx("2025-01-01", "2025-12-31", 1400e6))
    occy = _real_exit3(f, {"sbc_override": ov})
    assert "sbc: the sbc_override is not declared currency \"USD\" at a filer whose core facts are filed in CAD" in occy
    assert M.ttm_unavailable_problem(occy, syn, "SYN", rows=[], j={"sbc_override": ov}) is None, occy
    for jj in ({}, {"sbc_override": dict(ov, currency="usd")}, {"sbc_override": dict(ov, kind="guess")}):
        p = M.ttm_unavailable_problem(occy, syn, "SYN", rows=[], j=jj)
        assert p and p.startswith("[TTM-UNAV2]") and "sbc_override" in p, (jj, p)
    f = T55._syn_facts()
    _syn_ytd(f, [("NetCashProvidedByUsedInOperatingActivities", "USD", 100e6, 110e6), (T55.PRIMARY, "USD", 25e6, 26e6),
                 (T55.SBC_SHARE, "USD", 5e6, 5e6), (T55.SYN_SHARE_TAG, "shares", 100e6, 100e6)])
    _syn_ytd(f, [(T55.INTANG, "CNY", 0, 7e6)])
    intang = _real_exit3(f)
    assert "capex ytd_current: intangible purchases for 2026-01-01..2026-06-30 are filed only in CNY" in intang, intang
    assert M.ttm_unavailable_problem(intang, syn, "SYN", rows=[], j={}) is None, intang
    p = M.ttm_unavailable_problem(intang, dict(syn, latest_period_end="2024-12-31"), "SYN", rows=[], j={})
    assert p and p.startswith("[TTM-UNAV2]") and "2026-01-01..2026-06-30" in p, p
    for leg, start, end, ok_ in (("fy", "2025-01-01", "2025-12-31", True), ("ytd_prior", "2025-01-01", "2025-06-30", True),
                                 ("fy", "2024-01-01", "2024-12-31", False),
                                 ("ytd_prior", "2024-01-01", "2024-06-30", False),
                                 ("ytd_current", "2025-01-01", "2025-06-30", False)):
        text = intang.replace("capex ytd_current: intangible purchases for 2026-01-01..2026-06-30",
                              f"capex {leg}: intangible purchases for {start}..{end}")
        p = M.ttm_unavailable_problem(text, syn, "SYN", rows=[], j={})
        assert (p is None) == ok_, (leg, start, p)
    # end to end: the record's own CSV contradicts the undated quote
    run(n, _judgment(n, ttm_unavailable_reason=EXIT3_HEAD + "sbc: no annual (FY) fact"), csv_rows=hii_csv()).refused(
        "[TTM-UNAV2]", "'sbc: no annual (FY) fact'")
    ok(run(n, _judgment(n, ttm_unavailable_reason=unavailable()), csv_rows=hii_csv()))


def test_bridge_carry_is_the_one_carry_rule():
    """Review fix 4 (design 11 §7.2: the bridge's release mismatch is §3.7, not 04's own carry): a release-mismatch
    record pinned to a declared bridge carries the prior score's annual-median entry through carried_base_alternatives
    — its note too, so a prior median replay the engine refused stays "not computed — <the engine's line>" (never "no
    base") in score.json, key_numbers.md and the TTM_DECLARED_INTERIM flag; the prior declaration hash, published kind,
    base and weighted IRR must match, else "not measured". carried_base_alternatives carries a not-computed median the
    same way on a TTM-published run."""
    tt = {"basis": "declared_interim", "fy_end": "2025-12-31", "ytd_end": "2026-06-30", "ttm_oe_per_share": 2.5,
          "engine_release": CUR, "declaration_hash": "h1"}
    nb = hii(base_oe_per_share=2.5, release="5.7.99")
    pub = {"kind": "declared_interim", "role": "published", "computed": True, "measured": True, "base_oe_per_share": 2.5,
           "weighted_irr": 0.1033, "tier_by_numbers": "C"}
    refused_note = "the annual-median replay refused: BAD_BASE_OVERRIDE for TST: x"
    med = {"kind": "annual_median", "role": "alternative", "computed": False, "measured": True, "base_oe_per_share": None,
           "weighted_irr": None, "tier_by_numbers": None, "note": refused_note}

    def prior(med_entry, decl="h1", irr=0.1033):
        return {"interim_bridge": {"declaration_hash": decl},
                "base_alternatives": {"published": "declared_interim", "note": None,
                                      "bases": [dict(pub, weighted_irr=irr), med_entry]}}
    interim = {"ttm": tt, "decl": {}, "hash": "h1", "estimate_legs": []}
    meas = M.interim_bridge_measurement(T, nb, interim, True, prior(med))
    ba = M.interim_base_alternatives(nb, interim, meas)
    e = ba["bases"][1]
    assert ba["impact_carried_from_prior_score"] is True and ba["note"] is None, ba
    assert (e["computed"], e["measured"], e["note"], e["base_oe_per_share"]) == (False, True, refused_note, None), e
    assert (f"- Alternative: annual median of the last 3 FY OE/share not computed — {refused_note}"
            in M._kn_base_alternatives({"base_alternatives": ba})), M._kn_base_alternatives({"base_alternatives": ba})
    assert f"({refused_note})" in M.interim_flag(interim, meas)
    # a measured prior median: its figures
    meas = M.interim_bridge_measurement(T, nb, dict(interim), True, prior(dict(
        med, computed=True, base_oe_per_share=16.1404, weighted_irr=0.1033, tier_by_numbers="C", note=None)))
    assert meas["impact_carried_from_prior_score"] and meas["annual_median"]["weighted_irr"] == 0.1033, meas
    # another declaration, another weighted IRR: not measured
    for p in (prior(med, decl="h2"), prior(med, irr=0.2)):
        meas = M.interim_bridge_measurement(T, nb, dict(interim), True, p)
        assert meas["impact_carried_from_prior_score"] is False and meas["measured"] is False, meas
        assert meas["note"] == M._not_measured_note("5.7.99") and meas["annual_median"]["base_oe_per_share"] == 16.1404
    # R7's own carry (a TTM-published STALE_FY run whose median replay the engine refused)
    n, ptt = _ttm_published()
    n = dict(n, engine_release="5.7.99")
    with folder({"ttm.json": ptt, "judgment.json": {}}) as fo:
        plan = M.ttm_rejection_state(fo, n, {})
        prior_ba = {"published": "ttm", "note": None,
                    "bases": [{"kind": "ttm", "role": "published", "base_oe_per_share": 20.5, "weighted_irr": 0.16},
                              med]}
        ba = M.build_base_alternatives(T, fo, n, {}, plan, release_mismatch=True,
                                       prior_score={"base_alternatives": prior_ba})
        assert ba["impact_carried_from_prior_score"] is True and ba["bases"][1]["note"] == refused_note, ba
        assert ba["bases"][1]["computed"] is False and ba["bases"][1]["measured"] is True, ba


def test_declined_bridge_reason_is_quoted_in_the_entry_note():
    """Review fix 5 (design 11 §3.6 row 2: a 20-F / 40-F with interim_bridge_declined — the declared_interim entry's
    note quotes it): the validated reason in curly quotes (07 §1.10: worker text echoed by make_score), in score.json
    and key_numbers.md — and check_quotes never reads its figures as an engine source."""
    import check_quotes as CQ
    ads = {"ratio": 1.0, "source": "cover", "reason": "no ADS"}
    nf = hii(filer_annual_form="20-F", ads_ratio=ads)
    why = "the H1 2026 6-K (accession 0001-26-000001) prints no cash-flow statement; 0 of 3 legs, $412M of revenue"
    r = ok(run(nf, _judgment(nf, interim_bridge_declined={"reason": why, "report": None})))
    alt = r.result["score"]["base_alternatives"]["bases"][1]
    assert (alt["kind"], alt["computed"]) == ("declared_interim", False), alt
    assert alt["note"] == ("no ttm.json for this run — no declared 6-K interim bridge (judgment.json "
                           f"interim_bridge_declined, R2): “{why}”"), alt
    line = [ln for ln in section(r.result["key"]) if ln.startswith("- Alternative: declared 6-K interim bridge")]
    assert line == [f"- Alternative: declared 6-K interim bridge TTM not computed — {alt['note']}"], line
    assert "412" not in CQ.key_numbers_source_text(line[0], ())
    # an orphan bridge ttm.json beside the declined reason: the note quotes it too
    with folder({"ttm.json": hii_ttm(basis="declared_interim"), "judgment.json": {}}) as fo:
        jj = {"interim_bridge_declined": {"reason": why, "report": None}}
        plan = M.ttm_rejection_state(fo, nf, jj)
        e = M.build_base_alternatives(T, fo, nf, jj, plan)["bases"][1]
        assert e["note"].startswith("ttm.json is a declared 6-K interim bridge but judgment.json declares no "
                                    "interim_bridge") and e["note"].endswith(f"interim_bridge_declined (R2): “{why}”"), e


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn) and fn.__module__ == __name__:
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {str(e)[:3000]}")
            except Exception as e:
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {str(e)[:3000]}")
    sys.exit(1 if fails else 0)
