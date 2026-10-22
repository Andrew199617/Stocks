#!/usr/bin/env python3
"""make_score.py under engine 5.7 — the declared 6-K interim bridge and the annual-instance check (Andrew's ruling R2,
2026-10-19; design 04 A.5 / B.3, tests 29-36; rebase L4 amendments 6, 12-20; defaults Q7, Q8). Run:
python _system/tests/test_make_score_57_interim.py (or python -m pytest). Offline: the records come from REAL offline
engine and ttm.py runs on a synthetic 20-F filer (MICC's FY2025 and H1 legs, EUR; engine55_harness), make_score runs
on them through test_make_score_55's Run with real-engine stand-ins (the BRIDGE pattern of test_make_score_iprd) that
log every spawn's argv and environment; ttm.py is a fail-loud stand-in. Each test fails on the L0 scaffold (e22e814:
no bridge block, no measurement, no obligation, no refusals).

29. a --ttm pin on a declared bridge scores: score.json interim_bridge (descriptors) and base_alternatives (the
    declared_interim published entry beside the annual_median alternative, measured by one --measure replay with no
    pin), TTM_DECLARED_INTERIM in score.json's flags (not in dcf_numbers.json), the registry interim_bridge event,
    key_numbers.md's "Interim bridge" section last; the median replay takes no DCF_IPRD_HOLD (T-e) and no override
    toggle.
30. refusals: the declaration edited after ttm.py (hash), ttm.json edited before the engine run (arithmetic), the FY
    leg not this run's, a --base-oe-ps copy of the bridged figure, a declared bridge the run is not pinned to.
31. a release mismatch never spawns: the prior score's measurement is carried on the same declaration and base, else
    "not measured".
32. the override impact on a bridged base: base_used declared_interim, the pin zero-filled from ttm.json
    override_counterfactual, DCF_IPRD_HOLD on the replay (T-d), ttm.py never spawned.
33. the 5.7 obligation: a STALE_FY 20-F median run with neither interim_bridge nor interim_bridge_declined refuses;
    with a numeric interim_bridge_declined it scores and prints the line (registry event); a reason without a number
    refuses; the same record stamped 5.5.0 scores (D1); default Q7: a plain --base-oe-ps pin owes it too, and the
    switch INTERIM_OBLIGATION_RULE = "median_only" exempts it; both declarations at once refuse.
34. the interim_bridge event keeps its first date on an unchanged declaration.
35. annual_from_instance applied without <T>/annual_instance.json refuses; with it, the key_numbers.md line; with its
    facts edited (T-b) refuses.
36. no repo folder enters the new paths (the compatibility proof for the rebuild of every scored folder).
T-f a registry holding both events loads, and their fields avoid the deferred-payment names; T-g a bridge rejected
by R7's plan is not refused, without the plan it is; T-h an iprd_amortized / basis_window "ttm" base_override beside a
bridge gets its named refusal.
Review fix (2026-10-21; fails on the pre-fix L4 head 6fc70cd): make_score re-runs interim_bridge.py's pure rules on
the declaration, so a rule-breaking judgment edit with a patched ttm.json declaration_hash is refused.
[Integrate L4] (07 §1.12 step 7; fails on the L4 merge 83988ca): a 5.7 reason quoting the annual-median IRR the bridge
was measured against traces through the measurement's numeric leaves; the "Interim bridge" section sits between the
Moat scorecard and the Declared facts (07 §1.9).
"""
import copy
import glob
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import engine55_harness as H  # noqa: E402
from test_make_score_55 import Run, _numbers, _judgment, FAIL_LOUD  # noqa: E402
import make_score as M  # noqa: E402
import rulings57  # noqa: E402  ([Integrate L4] L3's obligation alone for a judgment written as is)

E = H._shared_engine()
IF = "ifrs-full"
CIK, FX_T = 999003, "SYF"
ACC = "0001104659-26-088404"
EXAMPLE = os.path.join(SYS, "examples", "interim_bridge.example.json")
SIX_K = os.path.join(HERE, "fixtures", "instance", "tiny_6k.xml")
PROBS = [0.1, 0.25, 0.3, 0.25, 0.1]
ARGS = ["--moat", "5.0", "--probs", "0.1,0.25,0.3,0.25,0.1", "--offsets", "-0.12,-0.05,0.0,0.05,0.12",
        "--mults", "0.75,0.9,1.0,1.1,1.25", "--gterm", "0.025"]
ADS = {"ratio": 1.0, "source": "test 20-F cover: ordinary shares trade directly", "reason": "no ADS program"}
YEARS = (2019, 2020, 2021, 2022, 2023, 2024, 2025)
RATES = {f"{y}-12-31": r for y, r in zip(YEARS, (1.1234, 1.2271, 1.1326, 1.0666, 1.105, 1.0389, 1.175))}
FLOWS = {"Revenue": 9000e6, "ProfitLoss": 360e6, "CashFlowsFromUsedInOperatingActivities": 483e6,
         "AdjustmentsForDepreciationAndAmortisationExpense": 300e6, "AdjustmentsForSharebasedPayments": 35e6,
         "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities": 357e6,
         "PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities": 3e6}
SBC_OVERRIDE = {"value": 35e6, "kind": "estimate", "source": "test: the FY2025 20-F notes give share-based payments "
                "EUR 35M (the cash-flow line is not tagged)", "reason": "test: FY2025 SBC is untagged",
                "ack_reason": "test"}


# ---------------------------------------------------------------------------
# the synthetic filer: a real engine run, ttm.py --interim, the final --ttm run
# ---------------------------------------------------------------------------
def _put(f, tax, tag, unit, e):
    f["facts"].setdefault(tax, {}).setdefault(tag, {"units": {}})["units"].setdefault(unit, []).append(e)


def foreign_fixture(sbc_2025=True, price=5.0):
    f = {"cik": CIK, "entityName": "SYNTH FOREIGN (test)", "facts": {IF: {}, "dei": {}}}
    for i, y in enumerate(YEARS):
        g = 1.04 ** (i - 6)
        meta = {"accn": f"0009990030-{(y + 1) % 100:02d}-000010", "fy": y, "fp": "FY", "form": "20-F",
                "filed": f"{y + 1}-03-18"}
        for tag, v in FLOWS.items():
            if tag == "AdjustmentsForSharebasedPayments" and y == 2025 and not sbc_2025:
                continue
            _put(f, IF, tag, "EUR", dict(meta, start=f"{y}-01-01", end=f"{y}-12-31", val=round(v * g)))
        _put(f, IF, "AdjustedWeightedAverageShares", "shares", dict(meta, start=f"{y}-01-01", end=f"{y}-12-31",
                                                                     val=615600000))
        for tag, v in (("CashAndCashEquivalents", 500e6), ("LongtermBorrowings", 2000e6),
                       ("PropertyPlantAndEquipment", 2500e6)):
            _put(f, IF, tag, "EUR", dict(meta, end=f"{y}-12-31", val=v))
    _put(f, "dei", "EntityCommonStockSharesOutstanding", "shares",
         {"end": "2025-12-31", "val": 615600000, "accn": "0009990030-26-000010", "fy": 2025, "fp": "FY",
          "form": "20-F", "filed": "2026-03-18"})
    return {"ticker": FX_T, "cik": CIK, "entityName": f["entityName"], "price": price, "filer_annual_form": "20-F",
            "fx_rates": {"EUR": dict(RATES)},
            "universe_row": {"ticker": FX_T, "name": "Synth Foreign", "sector": "", "price": str(price),
                             "market_cap": "", "cik": str(CIK)},
            "facts": f}


def decl():
    with open(EXAMPLE, encoding="utf-8") as fh:
        return json.load(fh)["interim_bridge"]


def judgment(**kw):
    j = _judgment(None, moat_score=5, probs_used=PROBS, name="Synth Foreign", sector="Consumer Staples",
                  ads_ratio=dict(ADS), interim_bridge=decl())
    j.update(kw)
    return {k: v for k, v in j.items() if v is not None}


def _submissions(acc=ACC):
    return {"filings": {"recent": {"form": ["6-K"], "accessionNumber": [acc], "filingDate": ["2026-07-30"],
                                   "reportDate": ["2026-06-30"], "primaryDocument": ["micc-20260630x6k.htm"],
                                   "isXBRL": [1]}}}


def _ttm_patch(T):
    sys.argv.append("--interim")
    T.fetch_submissions = lambda cik: _submissions()
    T.fetch_report_instance = lambda cik, filing: (open(SIX_K, "rb").read(), "https://www.sec.gov/x/micc_htm.xml")
    T.fx_rate = lambda ccy, date: {"2025-06-30": 1.172, "2026-06-30": 1.1394}.get(date) if ccy == "EUR" else None


_CACHE = {}


def pipeline(sbc_override=False):
    """(n, csv rows, ttm.json, fixture, judgment): preliminary median run -> ttm.py --interim -> final --ttm run, all
    real code offline. Cached per configuration."""
    key = ("pipe", sbc_override)
    if key in _CACHE:
        return copy.deepcopy(_CACHE[key])
    fx = foreign_fixture(sbc_2025=not sbc_override)
    j = judgment(**({"sbc_override": dict(SBC_OVERRIDE)} if sbc_override else {}))
    base = H.make_base(fx, j, None, copy_repo_files=False)
    try:
        pre = H.run_engine(FX_T, args=ARGS, base=base, fixture=fx, keep_base=True)
        assert pre["exit"] == 0, pre["stdout"][-2000:]
        t = H.run_ttm(FX_T, base=base, fixture=fx, patch=_ttm_patch, keep_base=True)
        assert t["exit"] == 0, t["stderr"][-2000:]
        fin = H.run_engine(FX_T, args=ARGS + ["--ttm"], base=base, fixture=fx, keep_base=True)
        assert fin["exit"] == 0, fin["stdout"][-2000:]
        n, rows, tt = fin["numbers"], fin["rows"], t["ttm"]
    finally:
        shutil.rmtree(base, ignore_errors=True)
    _CACHE[key] = (n, rows, tt, fx, j)
    return copy.deepcopy(_CACHE[key])


def median_record():
    """The synthetic filer's preliminary (median) run — no pin."""
    if "median" not in _CACHE:
        fx = foreign_fixture()
        out = H.run_engine(FX_T, args=ARGS, judgment={"ads_ratio": dict(ADS)}, fixture=fx)
        assert out["exit"] == 0, out["stdout"][-2000:]
        _CACHE["median"] = (out["numbers"], out["rows"])
    return copy.deepcopy(_CACHE["median"])


BRIDGE57 = r'''import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, "bridge57.json"), encoding="utf-8"))
with open(os.path.join(here, "SPAWNED_" + os.path.basename(__file__) + ".txt"), "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "no_overrides": os.environ.get("DCF_NO_OVERRIDES"),
                        "hold": os.environ.get("DCF_IPRD_HOLD"),
                        "purpose": os.environ.get("DCF_REPLAY_PURPOSE")}) + "\n")
if os.path.basename(__file__) == "ttm.py":
    sys.stderr.write("fail-loud stand-in: ttm.py was spawned\n")
    sys.exit(97)
sys.path[:0] = cfg["paths"]
import engine55_harness as H
folder = os.path.join(os.path.dirname(here), "TST")
def _load(name):
    try:
        return json.load(open(os.path.join(folder, name), encoding="utf-8"))
    except Exception:
        return None
fx = cfg["fixture"]
base = H.make_base(fx, _load("judgment.json") or {}, _load("ttm.json"), copy_repo_files=False)
out = H.run_engine(fx["ticker"], args=[a for a in sys.argv[2:] if a != "--measure"], base=base, fixture=fx,
                   measure="--measure" in sys.argv)
sys.stdout.write(out["stdout"])
sys.exit(out["exit"] or 0)
'''


def score(n, j, rows, tt=None, fx=None, prior_score=None, live=True, judgment_text=None, files=None, as_written=False):
    """make_score on record n (ticker rewritten to TST) with the real-engine stand-ins (live) or fail-loud ones.
    [Integrate L4] as_written (with judgment_text): L3's moat-scorecard obligation alone is added before the run
    (rulings57.add_minimal_scorecard_as_written), so the worker's reasons stay exactly as written."""
    m = copy.deepcopy(n)
    m["ticker"] = "TST"
    run = Run(m, j if judgment_text is None else None, judgment_text=judgment_text, prior_score=prior_score,
              csv_rows=rows, files=files)
    if live:
        for name in ("dcf_engine.py", "ttm.py"):
            with open(os.path.join(run.sysdir, name), "w", encoding="utf-8") as f:
                f.write(BRIDGE57)
        with open(os.path.join(run.sysdir, "bridge57.json"), "w", encoding="utf-8") as f:
            json.dump({"paths": [HERE, SYS], "fixture": fx or foreign_fixture()}, f)
    if tt is not None:
        with open(os.path.join(run.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(tt, f, indent=1)
    if as_written:
        rulings57.add_minimal_scorecard_as_written(run.folder)
    try:
        run.run()
        spawns = []
        for name in run.spawned():
            with open(os.path.join(run.sysdir, name), encoding="utf-8") as f:
                spawns += [dict(json.loads(line), script=name) if line.strip().startswith("{")
                           else {"script": name, "argv": line.split()} for line in f if line.strip()]
        run.result = dict(run.state(), score=run.score() if run.rc == 0 else None, key=run.key() if run.rc == 0 else None,
                          entries=run.entries(), spawns=spawns, registry_path=run.registry)
        if run.rc == 0:
            with open(run.registry, encoding="utf-8") as f:
                run.result["registry"] = json.load(f)
    finally:
        run.close()
    return run


def _stamp(n):
    n = {k: v for k, v in n.items() if k != "content_hash"}
    n["content_hash"] = E._content_hash(n)
    return n


# ---------------------------------------------------------------------------
# 29. the bridged score
# ---------------------------------------------------------------------------
def test_bridge_pin_scores_and_measures_both_bases():
    n, rows, tt, fx, j = pipeline()
    assert n["inputs"]["base_pin_source"] == "ttm_json" and n["base_oe_per_share"] == tt["ttm_oe_per_share"]
    assert any(f.startswith("STALE_FY") for f in n["fragility_flags"])
    assert not any(f.startswith("TTM_DECLARED_INTERIM") for f in n["fragility_flags"])   # never in engine output
    med_n, _ = median_record()
    r = score(n, j, rows, tt, fx)
    assert r.rc == 0, r.err[-2000:]
    s, key = r.result["score"], r.result["key"]
    ib = s["interim_bridge"]
    assert ib["basis"] == "declared_interim" and ib["currency"] == "EUR" and ib["declaration_hash"] == tt["declaration_hash"]
    assert ib["prior_interim_period"] == ["2025-01-01", "2025-06-30"] and ib["report_accession"] == ACC
    assert ib["fx"] == {"basis": "ecb_period_end", "fy": 1.175, "prior_interim": 1.172, "current_interim": 1.1394}
    assert ib["estimate_legs"] == ["capex_intangibles.prior_interim", "capex_intangibles.current_interim"]
    assert ib["perimeter_changes"] == [
        {"kind": "demerger", "effective_date": "2025-12-06", "material": True, "resolution": "same_business_perimeter"},
        {"kind": "acquisition", "effective_date": "2026-03-30", "material": False, "resolution": "immaterial"}]
    assert ib["measured_in"] == "base_alternatives" and ib["iprd_interim_scan"] == "xbrl_instance: none"
    alts = s["base_alternatives"]
    assert alts["schema"] == 1 and alts["published"] == "declared_interim" and alts["replays"] == 1 and alts["measured"]
    pub, med = alts["bases"]
    assert pub["kind"] == "declared_interim" and pub["role"] == "published" and pub["computed"] and pub["measured"]
    assert pub["base_oe_per_share"] == round(n["base_oe_per_share"], 4) == round(tt["ttm_oe_per_share"], 4)
    assert pub["weighted_irr"] == round(n["implied_irr_weighted"], 4) and pub["tier_by_numbers"] == n["tier_by_numbers"]
    assert pub["ttm_input_hash"] == n["ttm_inputs"]["ttm_input_hash"] and pub["ytd_end"] == "2026-06-30"
    assert med["kind"] == "annual_median" and med["role"] == "alternative" and med["measured"] and med["computed"]
    assert med["base_oe_per_share"] == round(med_n["base_oe_per_share"], 4), (med, med_n["base_oe_per_share"])
    assert med["weighted_irr"] == round(med_n["implied_irr_weighted"], 4) and med["tier_by_numbers"] == med_n["tier_by_numbers"]
    assert med["base_change_pct"] == round((med["base_oe_per_share"] - pub["base_oe_per_share"])
                                           / abs(pub["base_oe_per_share"]) * 100, 2)
    assert med["tier_changed"] == (med["tier_by_numbers"] != pub["tier_by_numbers"])
    # the flag: score.json's list only
    flags = [f for f in s["fragility_flags"] if f.startswith("TTM_DECLARED_INTERIM")]
    assert len(flags) == 1 and s["fragility_flags"][:-1] == n["fragility_flags"], s["fragility_flags"]
    assert flags[0].startswith("TTM_DECLARED_INTERIM: base is the declared 6-K interim bridge (FY 2025-12-31 − prior "
                               "interim to 2025-06-30 + current interim to 2026-06-30, EUR at per-period ECB rates; 2 "
                               "estimate legs) — bridged $0.59/share"), flags[0]
    # one replay: the median, field overrides on, no pin, no IPR&D hold (T-e), labelled for R7
    spawns = r.result["spawns"]
    assert [x["script"] for x in spawns] == ["SPAWNED_dcf_engine.py.txt"], spawns
    sp = spawns[0]
    assert "--measure" in sp["argv"] and "--ttm" not in sp["argv"] and "--base-oe-ps" not in sp["argv"], sp
    assert sp["hold"] is None and sp["no_overrides"] is None and sp["purpose"] == "base_alternatives", sp
    # the registry event
    ev = [e for e in r.result["entries"] if e.get("event") == "interim_bridge"]
    assert len(ev) == 1, r.result["entries"]
    e = ev[0]
    assert e["declaration_hash"] == tt["declaration_hash"] and e["currency"] == "EUR" and e["report_accession"] == ACC
    assert e["perimeter_changes"][0] == {"kind": "demerger", "effective_date": "2025-12-06",
                                         "resolution": "same_business_perimeter"}
    assert not set(e) & set(M.IPRD_DEFERRED_EVENT_KEYS)
    # [R7, 11 §7.2] both bases, their IRRs and tiers are the base_alternatives event's (one record, not two shapes);
    # the interim_bridge event keeps the declaration's descriptors
    assert not {"base_oe_bridged", "base_oe_annual_median", "tier_bridged", "tier_annual_median", "measured"} & set(e), e
    ba = [x for x in r.result["entries"] if x.get("event") == "base_alternatives"]
    assert len(ba) == 1 and ba[0]["chosen"] == "declared_interim" and ba[0]["ttm_kind"] == "declared_interim", ba
    assert ba[0]["ttm_ytd_end"] == "2026-06-30" and ba[0]["measured"] is True and ba[0]["reason"] is None, ba
    assert [(b["kind"], b["role"], b["base_oe_per_share"], b["tier_by_numbers"]) for b in ba[0]["bases"]] == [
        ("declared_interim", "published", pub["base_oe_per_share"], pub["tier_by_numbers"]),
        ("annual_median", "alternative", med["base_oe_per_share"], med["tier_by_numbers"])], ba
    assert not set(ba[0]) & set(M.IPRD_DEFERRED_EVENT_KEYS)
    # key_numbers.md
    assert '- Base source: ttm_json — the declared 6-K interim bridge (see "Interim bridge")' in key
    assert "## Interim bridge (declared 6-K TTM — the scored base)" in key
    assert key.index("## Fragility flags") < key.index("## Interim bridge")
    # [Integrate L4] 07 §1.9's order: ... Moat scorecard (L3) -> Interim bridge -> Declared facts (L2), last. On a 5.7
    # run the moat scorecard (the obligation, rulings57) writes facts.json, so L2's section now follows this one.
    heads = [h for h in key.splitlines() if h.startswith("## ")]
    ib_head = "## Interim bridge (declared 6-K TTM — the scored base)"
    assert heads[-3:] == ["## Moat scorecard", ib_head, "## Declared facts (not engine output)"], heads
    ib_sec = key.split("\n" + ib_head + "\n")[1].split("\n## ")[0]
    assert ib_sec.rstrip().splitlines()[-1].startswith("- Source — shares_diluted current: 6-K"), ib_sec[-400:]
    assert ("- Basis: FY 2025-01-01..2025-12-31 − prior interim 2025-01-01..2025-06-30 + current interim "
            f"2026-01-01..2026-06-30 (6-K {ACC}, filed 2026-07-30); legs in EUR, each converted at its own period-end ECB "
            "rate: FY 1.1750 (engine) · prior 1.1720 · current 1.1394") in key, key
    assert "| Operating cash flow | 483,000,000 | 276,000,000 | 539,000,000 | 746,000,000 | $858,189,600 |" in key, key
    assert "| Capex — intangibles | 3,000,000 | 1,487,671 (est.) | 1,487,671 (est.) | 3,000,000 | $3,476,502 |" in key
    assert "| Owner's earnings | | | | 320,000,000 | $364,301,098 |" in key
    assert ("- Shares (current-interim weighted average diluted): 617,000,000 × ADS ratio 1.0 → bridged base OE/share "
            "$0.5904 (scored)") in key
    # [R7, 11 §3.11] the both-bases comparison is the one "Base alternatives" section; "Interim bridge" points to it
    assert '- Bases compared: see "Base alternatives"' in key and "Annual-median base (same configuration" not in key
    assert (f"- Alternative: annual median of the last 3 FY OE/share ${med['base_oe_per_share']:,.2f} — weighted IRR "
            f"{med['weighted_irr'] * 100:.2f}%") in key, key
    assert "estimates: capex_intangibles prior (fy_prorated: FY 3,000,000 × 181/365)" in key, key
    assert "demerger 2025-12-06 (material; same_business_perimeter: “" in key and "acquisition 2026-03-30 (immaterial; 2.3% of revenue)" in key
    assert "TTM_DECLARED_INTERIM" in key.split("## Fragility flags")[1].split("##")[0]


# ---------------------------------------------------------------------------
# 30. refusals
# ---------------------------------------------------------------------------
def test_declaration_hash_mismatch_refuses():
    n, rows, tt, fx, j = pipeline()
    j["interim_bridge"]["reason"] += " (edited after ttm.py)"
    r = score(n, j, rows, tt, live=False)
    r.refused("judgment.json interim_bridge changed after ttm.py --interim ran (declaration hash")
    assert r.result["spawns"] == []
    gone = dict(j)
    del gone["interim_bridge"]
    score(n, gone, rows, tt, live=False).refused("ttm.json is a declared interim bridge but judgment.json declares no "
                                                 "(valid) interim_bridge — rerun ttm.py TST --interim")


def test_edited_ttm_json_refuses():
    n, rows, tt, fx, j = pipeline()
    # edited AFTER the engine run: the run's ttm_inputs no longer match (#47's TTM_CHANGED comes first, I14)
    after = copy.deepcopy(tt)
    after["ttm_sbc"] += 1
    score(n, j, rows, after, live=False).refused("ttm.json changed after the engine run")
    # edited BEFORE the engine run (the run read the edited file): a leg no longer the declaration's
    before = copy.deepcopy(tt)
    before["legs"]["ocf"]["current_interim"]["local"] = 540000000
    n2 = _stamp(dict(n, ttm_inputs=E.ttm_inputs_record(before)))
    score(n2, j, rows, before, live=False).refused("ttm.json's interim arithmetic does not reproduce from its own legs")
    # ... or a figure the legs no longer give
    fig = copy.deepcopy(tt)
    fig["ttm_ocf"] += 1000.0
    fig["inputs"]["ocf"]["ttm"] = fig["ttm_ocf"]
    n3 = _stamp(dict(n, ttm_inputs=E.ttm_inputs_record(fig)))
    score(n3, j, rows, fig, live=False).refused("ttm.json's interim arithmetic does not reproduce from its own legs")


def test_fy_leg_not_this_run_refuses():
    n, rows, tt, fx, j = pipeline()
    rows[-1]["ocf"] = str(float(rows[-1]["ocf"]) + 1e6)
    score(n, j, rows, tt, live=False).refused("the bridge's FY leg is not this run's latest FY (ocf: ttm.json")
    other = copy.deepcopy(tt)
    other["ads_ratio"] = 2.0
    other["ttm_oe_per_share"] *= 2   # consistent arithmetic on another ADS ratio
    n4 = _stamp(dict(n, base_oe_per_share=other["ttm_oe_per_share"], ttm_inputs=E.ttm_inputs_record(other)))
    _, rows4, _, _, _ = pipeline()
    score(n4, j, rows4, other, live=False).refused("ttm.json applied ADS ratio 2.0, the engine 1.0")


def test_forged_hash_rule_breaking_declaration_refused():
    """Review fix (2026-10-21; fails on the pre-fix L4 head 6fc70cd, where make_score scored every case): make_score
    re-runs interim_bridge.py's pure rules on the declaration (declaration_rule_problems: periods, sources, snippets,
    estimates, definitions, like-for-like, the share band) and checks the declared report is the one ttm.py verified.
    A judgment edit that breaks a rule, with ttm.json's declaration_hash patched to it (ttm.py never re-run;
    declaration_hash is outside TTM_INPUT_TOP_FIELDS, so check_ttm_inputs_current passes), is refused before any
    replay."""
    import interim_bridge as IB
    n, rows, tt, fx, j = pipeline()
    src = {"accession": ACC, "document": "micc-20260630x6k.htm", "page": 3, "section": "Basis of preparation"}

    def lfl2(d):
        d["like_for_like"]["perimeter_changes"][1].update(material=True, resolution="same_business_perimeter")

    def snip(d):
        d["legs"]["ocf"]["current_interim"]["snippet"] = "Net cash flow from operating activities 123 456"

    def lfl1(d):
        d["like_for_like"].update(comparative_restated=True, comparative_note="H1 2025 restated for the demerger",
                                  comparative_source=dict(src), comparative_snippet="restated",
                                  restatement={"description": "re-presented", "fy_leg_consistent": False,
                                               "source": dict(src), "snippet": "restated"})

    def src2(d):
        d["legs"]["sbc"]["prior_interim"]["source"]["accession"] = "0001104659-25-070000"

    def other_report(d):
        d["report"]["accession"] = "0001104659-26-099999"
        for f in ("ocf", "capex_ppe", "capex_intangibles", "sbc", "shares_diluted"):
            for leg in d["legs"][f].values():
                if leg.get("kind") == "filing":
                    leg["source"]["accession"] = "0001104659-26-099999"
    for edit, needle in ((lfl2, "[IB-LFL2] perimeter change acquisition on 2026-03-30"),
                         (snip, "[IB-SNIP] ocf.current_interim snippet does not show 539,000,000"),
                         (lfl1, "[IB-LFL1] the comparative was restated"),
                         (src2, "[IB-SRC2] sbc.prior_interim cites accession 0001104659-25-070000"),
                         (other_report, "[IB-SRC1] judgment.json interim_bridge.report.accession 0001104659-26-099999 "
                                        f"is not the 6-K ttm.py --interim verified ({ACC})")):
        jj = copy.deepcopy(j)
        edit(jj["interim_bridge"])
        t2 = copy.deepcopy(tt)
        t2["declaration_hash"] = IB.declaration_hash(jj["interim_bridge"])   # the only edit to the generated file
        r = score(n, jj, rows, t2, live=False)
        r.refused("judgment.json interim_bridge breaks the rules ttm.py --interim enforces", needle)
        assert r.result["spawns"] == [], (edit.__name__, r.result["spawns"])


def test_base_oe_ps_copy_refuses():
    n, rows, tt, fx, j = pipeline()
    inp = dict(n["inputs"], base_pin_source="base_oe_ps_arg", base_oe_ps_arg=tt["ttm_oe_per_share"])
    n2 = _stamp(dict(n, inputs=inp))
    r = score(n2, j, rows, tt, live=False)
    r.refused("a declared interim bridge pins the base only through --ttm (base_pin_source 'base_oe_ps_arg') — a "
              "--base-oe-ps copy of the figure is not accepted")


def test_declared_but_not_pinned_refuses():
    n_med, rows = median_record()
    _, _, tt, fx, j = pipeline()
    r = score(n_med, j, rows, tt, live=False)
    r.refused("judgment.json declares interim_bridge but the final run is not pinned through --ttm to a declared-interim "
              "ttm.json (base_source median_of_last_3_fy_oe_per_share)",
              "or keep it declared and reject it with ttm_rejection_reason")
    assert r.result["spawns"] == []


# ---------------------------------------------------------------------------
# 31. release mismatch
# ---------------------------------------------------------------------------
def _other_release(n, tt, rel="5.6.0"):
    t2 = copy.deepcopy(tt)
    t2["engine_record"]["engine_release"] = rel
    n2 = _stamp(dict(n, engine_release=rel, ttm_inputs=E.ttm_inputs_record(t2)))
    return n2, t2


def test_release_mismatch_carries_or_not_measured_without_spawn():
    n, rows, tt, fx, j = pipeline()
    good = score(n, j, rows, tt, fx)
    assert good.rc == 0, good.err[-1500:]
    n2, t2 = _other_release(n, tt)
    # no prior score: not measured, nothing spawned
    r = score(n2, j, rows, t2, live=False)
    assert r.rc == 0, r.err[-1500:]
    assert r.result["spawns"] == []
    alts = r.result["score"]["base_alternatives"]
    med = alts["bases"][1]
    assert alts["measured"] is False and med["measured"] is False and med["weighted_irr"] is None
    assert alts["note"] == f"not measured: engine output predates release {E.ENGINE_RELEASE}; re-run the engine to measure"
    assert med["base_oe_per_share"] == round(n["base_oe_normalized_per_share"], 4)
    # [R7, 11 §7.2] the measurement's state is the base_alternatives event's
    ev = [e for e in r.result["entries"] if e["event"] == "base_alternatives"][0]
    assert ev["measured"] is False and ev["note"].startswith("not measured")
    # a prior score measured on this declaration and base: carried
    c = score(n2, j, rows, t2, live=False, prior_score=good.result["score"])
    assert c.rc == 0 and c.result["spawns"] == [], c.err[-1500:]
    ca = c.result["score"]["base_alternatives"]
    assert ca["impact_carried_from_prior_score"] is True and ca["counterfactual_engine_release"] == "5.6.0"
    assert ca["bases"][1]["weighted_irr"] == good.result["score"]["base_alternatives"]["bases"][1]["weighted_irr"]
    assert "carried from the prior score.json, not re-measured" in c.result["key"]


# ---------------------------------------------------------------------------
# 32. override impact on a bridged base (T-d)
# ---------------------------------------------------------------------------
def test_override_impact_on_declared_interim_never_runs_ttm():
    n, rows, tt, fx, j = pipeline(sbc_override=True)
    assert [o["field"] for o in n["overrides_applied"]] == ["sbc"]
    cf = tt["override_counterfactual"]
    assert cf and set(cf["fy_fields_override_filled"]) == {"sbc"}, tt["override_counterfactual"]
    r = score(n, j, rows, tt, fx)
    assert r.rc == 0, r.err[-2000:]
    imp = r.result["score"]["override_impact"]
    assert imp["base_used"] == "declared_interim", imp
    scripts = [x["script"] for x in r.result["spawns"]]
    assert scripts == ["SPAWNED_dcf_engine.py.txt", "SPAWNED_dcf_engine.py.txt"], r.result["spawns"]   # never ttm.py
    ov, medr = r.result["spawns"]
    assert ov["no_overrides"] == "1" and ov["hold"] is not None, ov                 # T-d: the IPR&D hold
    assert "--base-oe-ps" in ov["argv"] and abs(float(ov["argv"][ov["argv"].index("--base-oe-ps") + 1])
                                                - cf["base_oe_per_share_zero_fill"]) < 1e-9, ov
    assert medr["hold"] is None and medr["no_overrides"] is None and medr["purpose"] == "base_alternatives"
    key = r.result["key"]
    assert "declared 6-K interim bridge (field overrides toggled off; FY override fields zero-filled)" in key


# ---------------------------------------------------------------------------
# 33. the 5.7 obligation (defaults Q7)
# ---------------------------------------------------------------------------
STALE = "STALE_FY: latest fiscal year ended 10 months ago — check TTM/quarterly OE and consider --base-oe-ps override"


def _foreign(release=None, **kw):
    a = dict(ADS)
    return _numbers(release=release or E.ENGINE_RELEASE, filer_annual_form="20-F", ads_ratio=a,
                    fragility_flags=[STALE], **kw)


def _fj(**kw):
    return dict(_judgment(None), ads_ratio=dict(ADS), **kw)


def test_57_stale_foreign_needs_bridge_or_declined():
    from test_make_score_55 import _with
    n = _foreign()
    r = _with(n, judgment_text=json.dumps(_fj()))
    r.refused("STALE_FY at a 20-F / 40-F filer on a 5.7 run: declare interim_bridge (python3 _system/ttm.py TST "
              "--interim-draft <6-K accession>, then --interim and --ttm) or interim_bridge_declined {reason, report}")
    reason = "the H1 2026 6-K (181 days) prints no condensed cash-flow statement"
    ok = _with(n, _fj(interim_bridge_declined={"reason": reason, "report": {"form": "6-K", "accession": ACC,
                                                                             "document": "x.htm"}}))
    assert ok.rc == 0, ok.err
    assert ok.result["score"]["interim_bridge_declined"] == {"reason": reason, "report": {"form": "6-K", "accession": ACC,
                                                                                          "document": "x.htm"}}
    assert f"- Interim bridge declined: “{reason}” (report {ACC})" in ok.result["key"]
    ev = [e for e in ok.result["entries"] if e.get("event") == "interim_bridge_declined"]
    assert ev and ev[0]["reason"] == reason and ev[0]["report_accession"] == ACC
    _with(n, judgment_text=json.dumps(_fj(interim_bridge_declined={"reason": "no cash-flow statement", "report": None}))
          ).refused("interim_bridge_declined.reason carries no number")
    _with(n, judgment_text=json.dumps(_fj(interim_bridge_declined={"reason": " "}))).refused(
        "judgment.json interim_bridge_declined must be {reason, report}")
    # D1: the same record from release 5.5.0 rebuilds as before
    assert _with(_foreign(release="5.5.0"), judgment_text=json.dumps(_fj())).rc == 0
    # a 10-K filer, or no STALE_FY: no obligation. [Integrate L4] The judgment goes through Run's rulings57 obligations
    # (as `ok` above), so these 5.7 runs carry L3's moat scorecard; add_interim_declined adds nothing to them (neither
    # is a STALE_FY 20-F / 40-F record), so they still prove the interim obligation does not apply.
    # [R7] a STALE_FY 10-K median with no ttm.json quotes ttm.py's exit-3 message (default Q14; rulings57)
    n10k = dict(_foreign(), filer_annual_form="10-K", ads_ratio=None)
    j10k = dict(_judgment(None))
    rulings57.add_ttm_unavailable(j10k, n10k, ttm=None, ticker="TST")
    r10k = _with(n10k, j10k)
    assert r10k.rc == 0, r10k.err
    assert "interim_bridge_declined" not in r10k.result["score"], r10k.result["score"].get("interim_bridge_declined")
    rfresh = _with(dict(_foreign(), fragility_flags=[]), _fj())
    assert rfresh.rc == 0, rfresh.err
    assert "interim_bridge_declined" not in rfresh.result["score"]
    # default Q7: a plain --base-oe-ps pin (a hand-built 6-K bridge) owes it too
    bo = {"value": 3.0, "source": "hand bridge from the H1 6-K", "reason": "STALE_FY"}
    pinned = _foreign(base_source="base_oe_ps_arg", inputs=dict(_numbers()["inputs"], base_oe_ps_arg=3.0,
                                                                 base_pin_source="base_oe_ps_arg"))
    r = _with(pinned, judgment_text=json.dumps(_fj(base_override=bo)))
    r.refused("STALE_FY at a 20-F / 40-F filer on a 5.7 run", "a hand-built 6-K pin is re-declared as interim_bridge "
                                                              "(default Q7)")
    assert M.INTERIM_OBLIGATION_RULE == "re_declare"
    assert M._interim_obligation_applies({"inputs": {"base_pin_source": "base_oe_ps_arg"}}) is True
    assert M._interim_obligation_applies({"inputs": {"base_pin_source": "judgment_base_override"}}) is False
    saved = M.INTERIM_OBLIGATION_RULE
    try:
        M.INTERIM_OBLIGATION_RULE = "median_only"
        assert M._interim_obligation_applies({"inputs": {"base_pin_source": "base_oe_ps_arg"}}) is False
        assert M._interim_obligation_applies({"inputs": {"base_pin_source": None}}) is True
    finally:
        M.INTERIM_OBLIGATION_RULE = saved
    # both declarations at once
    both = _fj(interim_bridge=decl(), interim_bridge_declined={"reason": "6-K of 181 days", "report": None})
    _with(n, judgment_text=json.dumps(both)).refused("judgment.json declares both interim_bridge and "
                                                     "interim_bridge_declined")


# ---------------------------------------------------------------------------
# 34. the registry keeps the first date
# ---------------------------------------------------------------------------
def test_registry_interim_event_keeps_first_date():
    n, rows, tt, fx, j = pipeline()
    first = score(n, j, rows, tt, fx)
    assert first.rc == 0, first.err[-1500:]
    reg = first.result["registry"]
    for e in reg["entries"]:
        if e.get("event") == "interim_bridge":
            e["date"] = "2026-08-01"
    m = copy.deepcopy(n)
    m["ticker"] = "TST"
    run = Run(m, j, csv_rows=rows)
    try:
        for name in ("dcf_engine.py", "ttm.py"):
            with open(os.path.join(run.sysdir, name), "w", encoding="utf-8") as f:
                f.write(BRIDGE57)
        with open(os.path.join(run.sysdir, "bridge57.json"), "w", encoding="utf-8") as f:
            json.dump({"paths": [HERE, SYS], "fixture": fx}, f)
        with open(os.path.join(run.folder, "ttm.json"), "w", encoding="utf-8") as f:
            json.dump(tt, f)
        with open(run.registry, "w", encoding="utf-8") as f:
            json.dump(reg, f)
        run.run()
        assert run.rc == 0, run.err[-1500:]
        ev = run.entries("interim_bridge")
        assert len(ev) == 1 and ev[0]["date"] == "2026-08-01", ev
    finally:
        run.close()
    # a changed declaration is a new judgment: re-dated
    keyed = M._declaration({"event": "interim_bridge", "declaration_hash": "a"})
    assert keyed != M._declaration({"event": "interim_bridge", "declaration_hash": "b"})
    assert keyed == M._declaration({"event": "interim_bridge", "declaration_hash": "a", "base_oe_bridged": 9.9})


# ---------------------------------------------------------------------------
# 35. the annual-instance file (T-b)
# ---------------------------------------------------------------------------
def _instance_doc():
    import xbrl_instance as X
    facts = [{"taxonomy": IF, "tag": "CashFlowsFromUsedInOperatingActivities", "unit": "EUR", "start": "2025-04-01",
              "end": "2026-03-31", "val": 607000000, "decimals": -6}]
    return {"ticker": "TST", "cik": 1, "form": "20-F", "accession": "0009990020-26-000381", "filed": "2026-05-29",
            "report_date": "2026-03-31", "fiscal_year_focus": 2026, "instance_url": "u", "instance_sha256": "s" * 64,
            "instance_bytes": 10, "companyfacts_latest_annual_end": "2025-03-31", "extracted_by": "dcf_engine",
            "extracted_at": "2026-10-21", "facts": facts, "conflicts": [], "facts_sha256": X.facts_sha256(facts, [])}


def test_annual_instance_file_required():
    from test_make_score_55 import _with
    doc = _instance_doc()
    rec = {"applied": True, "checked": True, "form": "20-F", "accession": doc["accession"], "filed": "2026-05-29",
           "report_date": "2026-03-31", "periods_added": ["2026-03-31"], "companyfacts_latest_annual_end": "2025-03-31",
           "instance_url": "u", "instance_sha256": doc["instance_sha256"], "facts_merged": 1, "conflicts": [],
           "facts_sha256": doc["facts_sha256"], "cache": "TST/annual_instance.json", "reason": None}
    n = _numbers(release=E.ENGINE_RELEASE, annual_from_instance=rec, latest_period_end="2026-03-31")
    _with(n).refused("dcf_numbers.json says annual facts were read from the XBRL instance of 0009990020-26-000381 but "
                     "TST/annual_instance.json is missing or differs — commit the file the engine wrote, or rerun the engine")
    ok = _with(n, files={"TST/annual_instance.json": doc})
    assert ok.rc == 0, ok.err
    assert ("- Annual facts for FY 2026-03-31: read from the 20-F's own XBRL instance (accession 0009990020-26-000381, "
            "filed 2026-05-29) — EDGAR companyfacts had not ingested them (its latest annual period ended 2025-03-31); "
            "1 facts merged (TST/annual_instance.json)") in ok.result["key"], ok.result["key"]
    tampered = copy.deepcopy(doc)
    tampered["facts"][0]["val"] = 707000000
    _with(n, files={"TST/annual_instance.json": tampered}).refused(
        "annual_instance.json changed after the engine run (its facts no longer hash to dcf_numbers.json "
        "annual_from_instance.facts_sha256) — rerun dcf_engine.py; it is the run's input")
    other = dict(doc, accession="0009990020-26-000999")
    _with(n, files={"TST/annual_instance.json": other}).refused("TST/annual_instance.json is missing or differs")
    # an applied:false record needs no file and prints nothing
    off = _numbers(release=E.ENGINE_RELEASE, annual_from_instance={"applied": False, "checked": False, "reason": "x"})
    r = _with(off)
    assert r.rc == 0 and "Annual facts for FY" not in r.result["key"]


# ---------------------------------------------------------------------------
# 36. no repo folder enters the new paths
# ---------------------------------------------------------------------------
def test_no_repo_folder_enters_the_new_paths():
    folders = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(ROOT, "*", "score.json")))
    assert len(folders) > 400, len(folders)
    for folder in folders:
        def rd(name):
            try:
                with open(os.path.join(folder, name), encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError):
                return None
        n, j, tt = rd("dcf_numbers.json"), rd("judgment.json") or {}, rd("ttm.json")
        assert not M._is_declared_interim(tt), folder
        assert "interim_bridge" not in j and "interim_bridge_declined" not in j, folder
        if isinstance(n, dict):
            assert "annual_from_instance" not in n, folder
            assert not M.is_57_run(n), folder
            assert M.interim_pin_state(folder, n, j, tt) is None, folder
            assert M._interim_pinned(os.path.basename(folder), n) is False, folder


# ---------------------------------------------------------------------------
# T-f, T-g, T-h
# ---------------------------------------------------------------------------
def test_registry_with_interim_events_loads():
    n, rows, tt, fx, j = pipeline()
    state = {"ttm": tt, "decl": j["interim_bridge"], "hash": tt["declaration_hash"], "estimate_legs": [],
             "measurement": {"bridged": {"base_oe_per_share": 0.59}, "annual_median": {"base_oe_per_share": 0.2},
                             "measured": True, "note": None}}
    evs = M._interim_events("TST", state, {"reason": "6-K of 181 days", "report": None}, "2026-10-21")
    assert [e["event"] for e in evs] == ["interim_bridge", "interim_bridge_declined"]
    for e in evs:
        assert not set(e) & set(M.IPRD_DEFERRED_EVENT_KEYS), e
        assert M.registry_entry_problem(e) is None, e
    import tempfile
    d = tempfile.mkdtemp(prefix="reg57_")
    try:
        path = os.path.join(d, "overrides_registry.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"entries": evs}, f)
        saved = M.REGISTRY
        M.REGISTRY = path
        try:
            assert M.load_registry()["entries"] == evs
        finally:
            M.REGISTRY = saved
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_rejected_bridge_with_reason_is_an_alternative():
    """T-g (amendment 16): R7's plan rejecting a declared bridge (a qualifying ttm_rejection_reason) lifts L4's binding
    refusal; R7's builder then records the bridge as the rejected alternative (R7's own tests)."""
    n = dict(_foreign(), ticker="TST", base_source="median_of_last_3_fy_oe_per_share")
    j = _fj(interim_bridge=decl())
    assert _refusal_text(M.check_interim_obligation, n, j, None, plan={"bridge_rejected": True}) is None
    # the rejected bridge also meets the 5.7 obligation, which the same STALE_FY 20-F run without it owes
    msg = _refusal_text(M.check_interim_obligation, n, _fj(), None, plan={"bridge_rejected": False})
    assert msg and "STALE_FY at a 20-F / 40-F filer on a 5.7 run" in msg, msg


def test_rejected_bridge_without_reason_refused():
    n = dict(_foreign(), ticker="TST")
    j = _fj(interim_bridge=decl())
    for plan in (None, {"bridge_rejected": False}):
        msg = _refusal_text(M.check_interim_obligation, n, j, None, plan=plan)
        assert msg and "judgment.json declares interim_bridge but the final run is not pinned through --ttm" in msg, \
            f"a declared, unpinned bridge must refuse without R7's rejection (plan {plan}): {msg}"


def _refusal_text(fn, *a, **k):
    import io
    import contextlib
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        try:
            fn(*a, **k)
        except SystemExit:
            return err.getvalue()
    return None


def test_iprd_amortized_beside_bridge_refused():
    n = dict(_foreign(), ticker="TST")
    am = _fj(interim_bridge=decl(), base_override={"value": 1.0, "source": "s", "reason": "r", "basis": "iprd_amortized"})
    msg = _refusal_text(M.check_interim_obligation, n, am, None)
    assert msg and "an acquired-IPR&D amortized pin cannot sit on a declared interim bridge" in msg, msg
    bw = _fj(interim_bridge=decl(), base_override={"value": 1.0, "source": "s", "reason": "r",
                                                   "basis_window": {"window": "ttm"}})
    msg = _refusal_text(M.check_interim_obligation, n, bw, None)
    assert msg and "a declared interim bridge pins only through --ttm; a per-unit pin on its figures needs " \
                   "share_classes (R6)" in msg, msg


# ---------------------------------------------------------------------------
# [Integrate L4] the interim measurement is an engine source of every 5.7 influence trace (07 §1.12 step 7)
# ---------------------------------------------------------------------------
def test_57_reasons_trace_to_the_interim_measurement():
    """R2a x R3 (Andrew, 2026-10-19; 07 §1.12 step 7): on a 5.7 run the influence trace's engine sources are L2's set
    plus the numeric leaves of the moat evidence and of the declared bridge's measurement — a tier_override_reason
    quoting the annual-median weighted IRR the bridged base was measured against traces with nothing declared or
    cited (the judgment is scored exactly as written). A figure in no generated file still refuses, writing nothing.
    Fails on the L4 merge before Integrate L4 (83988ca: the median IRR was in no source of the trace)."""
    n, rows, tt, fx, j = pipeline()
    med_n, _ = median_record()
    assert (n["tier_by_numbers"], med_n["tier_by_numbers"]) == ("B", "D"), (n["tier_by_numbers"], med_n["tier_by_numbers"])
    med_pct = f"{med_n['implied_irr_weighted'] * 100:.2f}%"
    br_pct = f"{n['implied_irr_weighted'] * 100:.2f}%"

    def why(median_figure):
        return (f"the annual-median base gives only {median_figure} weighted against the bridged {br_pct}: one tier "
                "down until the next annual report confirms the half-year")

    def as_written(reason):
        jt = dict(j, tier_override="C", tier_override_reason=reason)
        return score(n, None, rows, tt, fx, judgment_text=json.dumps(jt, indent=1, ensure_ascii=False) + "\n",
                     as_written=True)

    r = as_written(why(med_pct))
    assert r.rc == 0, r.err[-2000:]
    s = r.result["score"]
    assert s["tier_final"] == "C" and s["tier_override_reason"] == why(med_pct), s.get("tier_override_reason")
    med_entry = s["base_alternatives"]["bases"][1]
    assert med_entry["kind"] == "annual_median" and f"{med_entry['weighted_irr'] * 100:.2f}%" == med_pct, med_entry
    inf = s["declared_facts"]["influence"]["tier_override_reason"]
    assert inf["facts"] == [] and inf["engine_numbers"] == 2 and inf["third_party_only"] is False, inf
    # a figure the measurement does not hold (nor any generated file): refused before any write
    off = f"{med_n['implied_irr_weighted'] * 100 + 0.37:.2f}%"
    bad = as_written(why(off))
    bad.refused(f"judgment.json tier_override_reason quotes {off} that is neither an engine figure nor a fact it cites")
    assert not bad.result["entries"], bad.result["entries"]
    # the helper itself: both measurements' leaves, nothing without them
    assert M.influence_extra(None, None) == []
    leaves = M.influence_extra({"pillars": {"returns_on_capital": {"value": 0.1388, "applies": True}}},
                               {"bridged": {"base_oe_per_share": 0.5904}, "annual_median": {"weighted_irr": 0.0664},
                                "replays": 1, "measured": True})
    assert leaves == [0.1388, 0.5904, 0.0664], leaves


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
