#!/usr/bin/env python3
"""Engine 5.7 worker obligations for the PRE-EXISTING tests (07 §2 G16) — imported by tests, never run on its own.

Since engine release 5.7.0 every test that stamps a record with the current release (E.ENGINE_RELEASE) builds a "5.7
run", which inherits each new 5.7 obligation (a misfit's misfit_notch_reason, facts.json and cited reasons, the moat
scorecard, a 20-F STALE_FY run's interim declaration, an Up-C reason, a STALE_FY TTM rejection reason, a 5.7-stamped
ttm.json, the R7 base replays). One function per obligation, so every pre-existing test keeps its assertions
unchanged: the lane that adds an obligation fills its own function here (the scaffold, L0, left each a no-op) and the
call sites already apply it — test_make_score_55.Run (also test_make_score_iprd, which builds through Run),
test_payable_base._score_files, test_queue_alert_gates._folder and test_engine_55._ms_run, all through apply().
add_ttm_engine_release and answer_base_replays are wired by their lanes (L9, R7) where a test writes a ttm.json or
installs an engine stand-in.

Files: an obligation that needs a folder file writes it itself into `folder` (the test's temp folder) — facts go
through merge_facts, so the lanes that cite facts (L2 reasons, L3 scorecard, L8 / R7 reasons) never overwrite each
other's. (The other half of the L0 decision for L2 / L3: test_make_score_55.Run(files=...) writes any extra file a
lane's OWN new tests need — facts.json, fundamentals.json, _system/industry_returns.json.)
"""
import copy
import hashlib
import json
import os


# ---------------------------------------------------------------------------
# One function per 5.7 obligation (each lane fills its own; no-ops in L0)
# ---------------------------------------------------------------------------
def add_notch_reason(n, j):
    """L1 (R1): a current-release sector misfit (S-C, not on the payable base) gets a misfit_notch_reason carrying a
    number. No-op in L0."""
    return None


def cite_facts_for_reasons(j, n, folder=None):
    """L2 (R3): facts.json facts (merge_facts) and [F#] citations for the reasons a 5.7 run traces
    (tier_override_reason, base_override, ...), so every number in them traces. No-op in L0."""
    return None


MINIMAL_SCORECARD_FACTS = (   # L3: a kind-filing, type-metric series (instant periods: no fiscal calendar needed)
    [{"id": f"F9{i}", "label": "seat renewal rate (fixture)", "value": v, "unit": "pct", "scale": "", "precision": 2,
      "period": p, "kind": "filing", "type": "metric", "metric": "seat_renewal_rate",
      "source": {"form": "10-K", "accession": "0000000000-26-000090", "section": "Item 7 (fixture)", "filed": "2026-02-20"},
      "snippet": f"seat renewal rate was {v * 100:.2f}%",
      "used_for": ["moat:sources", "moat:switching_costs", "moat:retention", "moat:pricing_power", "moat:concentration",
                   "moat:reach_and_growth", "moat:erosion_risks"]}
     for i, (p, v) in enumerate((("2023-12-31", 0.9137), ("2024-12-31", 0.9241), ("2025-12-31", 0.9358)), start=1)]
    + [{"id": "F90", "label": "moat backstop figure (fixture)", "value": 7.25, "unit": "x", "scale": "", "precision": 2,
        "period": "2025-12-31", "kind": "filing", "type": "actual", "metric": "moat_backstop",
        "source": {"form": "10-K", "accession": "0000000000-26-000090", "section": "Item 7 (fixture)", "filed": "2026-02-20"},
        "snippet": "the backstop figure was 7.25x", "used_for": ["moat_divergence", "low_roic"]}])


def minimal_scorecard(business_type="industrial", sic=None):
    """03b §17 (f): one narrow source (switching_costs/workflow_training on the F91-F93 series), the seven core declared
    pillars at core weight 9.0 (retention +1, pricing_power +1, switching_costs +1, concentration 0, reach_and_growth 0,
    erosion_risks 0 — each with the series — customer_regard N/A), every supporting factor N/A (adjustment 0.00), and
    the 07 G16 backstop reasons citing [F90] (value 7.25). With no mechanical pillar measured the evidence is 6.53
    (5.88-6.88 when a CSV measures capital_intensity): within +-2 of the fixtures' moats 5 and 6; one narrow source
    caps the moat at 6. business_type: minimal_business_type's choice (the SIC lock, else industrial); the declared
    weight is 9.0 for every type, so a type whose capital_intensity / scale_economics are N/A still clears the floor."""
    fs = ["F91", "F92", "F93"]
    na = {"applicable": False, "not_applicable_reason": "fixture"}
    pill = lambda s: {"score": s, "rationale": "fixture", "facts": list(fs)}  # noqa: E731
    return {"version": 1, "business_type": business_type,
            "business_type_reason": ("fixture: 100% of revenue is one manufactured product line"
                                     if business_type == "industrial" else f"fixture: the SIC lock (SIC {sic})"),
            "sources": [{"type": "switching_costs", "subtype": "workflow_training", "strength": "narrow", "facts": list(fs),
                         "metrics": [], "rationale": "fixture"}],
            "pillars": {"retention": pill(1), "pricing_power": pill(1), "switching_costs": pill(1), "concentration": pill(0),
                        "reach_and_growth": pill(0), "erosion_risks": pill(0), "customer_regard": dict(na)},
            "supporting": {k: dict(na) for k in ("product_quality", "market_share", "execution", "management")},
            "volume_price": None,
            "moat_divergence_reason": "fixture backstop: 7.25 [F90]", "low_roic_reason": "fixture backstop: 7.25 [F90]",
            "high_return_low_moat_reason": None, "erosion_rebuttal": None}


def minimal_business_type(n, folder):
    """(business_type, sic) for the minimal scorecard — 03b §17 (f) / rebase L3 §3.10: "from the SIC lock, else
    industrial". The SIC is resolved the way make_score resolves it (dcf_numbers.json sector_model.sic, else
    dcf_engine.folder_sic on the folder's files: fundamentals.json profile.sic, then profile.json) and locked by
    moat_scorecard.type_lock on the folder's latest annual row (the SIC-6798 mortgage-REIT rule included). A single
    locked type is used; an unlocked REIT (real_assets or financial_balance_sheet) gets financial_balance_sheet, which
    needs no numeric business_type_reason; no SIC or an unlocked SIC gives industrial. [L3 review R6, 2026-10-21] The
    helper had always declared industrial, so a 5.7 test record at a bank, insurer or utility folder was refused before
    the test's own assertion. _system modules are imported lazily (this helper stays import-light)."""
    import sys
    sm = (n or {}).get("sector_model") if isinstance(n, dict) else None
    sic = str(sm.get("sic")).strip() if isinstance(sm, dict) and sm.get("sic") not in (None, "") else None
    sysdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sysdir not in sys.path:
        sys.path.insert(0, sysdir)
    import dcf_engine
    import moat_scorecard
    fold = os.path.normpath(folder)
    if not sic:
        sic = dcf_engine.folder_sic(os.path.dirname(fold), os.path.basename(fold))[0]
    if not sic:
        return "industrial", None
    raw = moat_scorecard.raw_rows(fold)[1]
    allowed, _, _ = moat_scorecard.type_lock(sic, raw[-1] if raw else None)
    if not allowed:
        return "industrial", sic
    if len(allowed) == 1:
        return next(iter(allowed)), sic
    return ("financial_balance_sheet" if "financial_balance_sheet" in allowed else sorted(allowed)[0]), sic


def _is_57(n):
    """facts.is_rulings_run without importing _system (the helper stays import-light): engine_release >= 5.7.0.
    (Placed above add_minimal_scorecard, inside L3's lines, so lane L4's insertion before add_interim_declined merges
    cleanly — L3 review R7.)"""
    rel = (n or {}).get("engine_release") if isinstance(n, dict) else None
    try:
        parts = tuple(int(x) for x in str(rel).split(".")[:3])
    except (TypeError, ValueError):
        return False
    return len(parts) >= 2 and (parts + (0,) * (3 - len(parts))) >= (5, 7, 0)


def add_minimal_scorecard(j, n=None, folder=None):
    """L3 (R4 revised): on a 5.7 run (engine release >= 5.7.0) whose judgment declares no moat_scorecard, the minimal
    scorecard above with minimal_business_type's type, and its facts written into <folder>/facts.json (merge_facts, so
    the other lanes' facts stay). Without a folder nothing is added (a scorecard whose facts cannot be written would
    refuse). Idempotent."""
    if not isinstance(j, dict) or folder is None or "moat_scorecard" in j or not _is_57(n):
        return None
    j["moat_scorecard"] = minimal_scorecard(*minimal_business_type(n, folder))
    merge_facts(folder, copy.deepcopy(MINIMAL_SCORECARD_FACTS), ticker=(n or {}).get("ticker"))
    return None


def add_interim_declined(n, j):
    """L4 (R2a): interim_bridge_declined with a numeric reason on a 5.7 STALE_FY 20-F / 40-F record. No-op in L0."""
    return None


def add_up_c_reason(j, n):
    """L8 (R6): up_c_suspect_reason (carrying a number) on a 5.7 record flagged UP_C_SUSPECT. No-op in L0."""
    return None


def add_ttm_rejection(j, n, ttm=None):
    """R7: a qualifying ttm_rejection_reason (a cash-flow line and a traced figure) on a 5.7 STALE_FY record whose
    published base is not ttm.json's TTM. No-op in L0."""
    return None


def add_ttm_engine_release(tt, n=None):
    """L9 (R8 / R9 TTM provenance): stamp ttm.json object tt with the current engine release (and, given the record
    n, its ttm_inputs and content hash). Returns tt. No-op in L0."""
    return tt


def answer_base_replays(sysdir, n, ttm_doc=None, replies=None):
    """R7: answer the DCF_REPLAY_PURPOSE=base_alternatives engine spawns beside the test's own stand-in in sysdir.
    No-op in L0."""
    return None


# ---------------------------------------------------------------------------
# The entry points the call sites use
# ---------------------------------------------------------------------------
def _canon(n):
    return json.dumps({k: v for k, v in n.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":"),
                      default=str)


def content_hash(n):
    """The engine's content hash of record n (dcf_engine._content_hash's canonicalization)."""
    return hashlib.sha256(_canon(n).encode()).hexdigest()


def apply(n, j, folder=None, ttm=None):
    """Every judgment-side obligation above, in lane merge order, on COPIES of engine record n and judgment j (either
    may be None); returns (n, j). The inputs are never modified. A record that carried a content_hash is re-stamped
    when an obligation changed it. The identity in L0."""
    n2 = copy.deepcopy(n) if n is not None else None
    j2 = copy.deepcopy(j) if j is not None else None
    before = _canon(n2) if isinstance(n2, dict) else None
    add_notch_reason(n2, j2)                              # L1
    cite_facts_for_reasons(j2, n2, folder=folder)         # L2
    add_minimal_scorecard(j2, n=n2, folder=folder)        # L3
    add_interim_declined(n2, j2)                          # L4
    add_up_c_reason(j2, n2)                               # L8
    add_ttm_rejection(j2, n2, ttm=ttm)                    # R7
    if isinstance(n2, dict) and "content_hash" in n2 and _canon(n2) != before:
        n2["content_hash"] = content_hash(n2)
    return n2, j2


def make_current(base, ticker):
    """The obligations for a folder already written under base (lane L5's pr_worktree / rebuild_scores fixtures):
    applies apply() to <base>/<ticker>/dcf_numbers.json and judgment.json (ttm.json read when present) and rewrites a
    file only when it changed. Returns the folder path. The identity in L0."""
    folder = os.path.join(base, ticker)

    def rd(name):
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    n, j, tt = rd("dcf_numbers.json"), rd("judgment.json"), rd("ttm.json")
    n2, j2 = apply(n, j, folder=folder, ttm=tt)
    for name, old, new in (("dcf_numbers.json", n, n2), ("judgment.json", j, j2)):
        if new is not None and new != old:
            with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                json.dump(new, f, indent=1, ensure_ascii=False)
    return folder


def merge_facts(folder, facts, ticker=None):
    """Add (or replace, by id) fact objects in <folder>/facts.json, creating it as {schema: 1, ticker, facts: []}
    when absent — so two lanes' obligations never overwrite each other's facts. Returns the written document."""
    path = os.path.join(folder, "facts.json")
    doc = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    if not isinstance(doc, dict):
        doc = {"schema": 1, "ticker": (ticker or os.path.basename(os.path.normpath(folder))).upper(), "facts": []}
    have = {f.get("id"): i for i, f in enumerate(doc.get("facts") or []) if isinstance(f, dict)}
    doc.setdefault("facts", [])
    for fact in facts:
        if fact.get("id") in have:
            doc["facts"][have[fact["id"]]] = fact
        else:
            have[fact.get("id")] = len(doc["facts"])
            doc["facts"].append(fact)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    return doc
