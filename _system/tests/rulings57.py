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
import re


# ---------------------------------------------------------------------------
# One function per 5.7 obligation (each lane fills its own; no-ops in L0)
# ---------------------------------------------------------------------------
NOTCH_REASON = "test: payable-earnings measure implies 9.25%"   # one number, colliding with no synthetic leaf


def add_notch_reason(n, j, folder=None):
    """L1 (R1): a current-release sector misfit (S-C, not on the payable base) gets a misfit_notch_reason carrying a
    number (make_score's R-3 / R-4 on a 5.7 run); tier_override is left alone. A judgment that already sets the field
    (a test of the reason itself) is untouched, and so is everything else. [Integrate L3] Given the test's folder, a
    misfit is also what make_score's misfit_detection reads there (dcf_engine.misfit_status: the re-read sector_model,
    the folder's own SIC files) — so a 5.7 test record at a bank / insurer / utility folder (L3's minimal-scorecard
    SIC-lock test) is notched with a reason, not refused before the test's own assertion. A reason on a modeled name
    is harmless (make_score reads it only on a misfit), so the two readings are OR-ed."""
    if not (isinstance(n, dict) and isinstance(j, dict)) or "misfit_notch_reason" in j:
        return None
    rel = n.get("engine_release")
    if not (isinstance(rel, str) and _release_at_least_57(rel)):
        return None
    sm = n.get("sector_model") if isinstance(n.get("sector_model"), dict) else {}
    misfit = bool(sm.get("misfit")) or any(str(f).startswith("SECTOR_MODEL_MISMATCH")
                                           for f in n.get("fragility_flags") or [])
    if not misfit and folder is not None:
        misfit = _folder_misfit(n, folder)
    if misfit and n.get("tier_by_numbers") in ("S", "A", "B", "C") and not n.get("payable_base"):
        j["misfit_notch_reason"] = NOTCH_REASON
    return None


def _folder_misfit(n, folder):
    """make_score.misfit_detection's answer for record n in the test's folder (dcf_engine imported lazily, as
    minimal_business_type does): True when dcf_engine.misfit_status says misfit."""
    import sys
    sysdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sysdir not in sys.path:
        sys.path.insert(0, sysdir)
    import dcf_engine
    fold = os.path.normpath(folder)
    return dcf_engine.misfit_status(n, os.path.dirname(fold), os.path.basename(fold))[0] == "misfit"


def _release_at_least_57(rel):
    try:
        return tuple(int(x) for x in rel.split(".")[:3]) >= (5, 7, 0)
    except ValueError:
        return False


def cite_facts_for_reasons(j, n, folder=None):
    """L2 (R3, Andrew 2026-10-19; 07 G16, rebase A14): on a 5.7 record, the reasons make_score now traces
    (tier_override_reason when a tier_override is set, misfit_notch_reason) are given what R3 asks for, so every
    pre-existing assertion holds:
    - a reason that already cites ids ([F1, F2], test_make_score_iprd's unverified-share-count override) gets them
      declared in facts.json for its untraced figures, in order — a count as a filing fact, a per-share charge that
      is the record's acquired-IPR&D total over the declared count as a calc fact (ratio, kind filing) — and its
      quoted percent(s) (the adjusted weighted IRR) from a saved method run dcf_numbers_test_reasons.json (a copy
      of the record with that IRR, hash-stamped), A14's shape;
    - a reason that cites nothing gets a filing fact per untraced figure and the [F#] citations appended, and a
      reason with no number at all ("test reason", "one notch") gains the figure 8.75% [F89].
    Facts go through merge_facts (no other lane's are lost). The identity on older records, without a folder, or when
    nothing needs declaring."""
    if not (isinstance(j, dict) and isinstance(n, dict) and folder and os.path.isdir(folder)):
        return None
    import check_quotes as CQ
    import facts as F
    import quote_tokens as Q
    if not F.is_rulings_run(n):
        return None
    engine = CQ.influence_sources(folder, n, judgment=j)   # check_influence's own engine set
    period = f"FY{str(n.get('latest_period_end') or '2025')[:4]}"
    new_facts, run_values, next_id = [], [], 80
    for field, tag in REASON_FIELDS:
        if field == "tier_override_reason" and not j.get("tier_override"):
            continue
        text = j.get(field)
        if not isinstance(text, str) or not text.strip():
            continue
        refs = F.parse_refs(text)
        toks = [t for t in Q.numbers(text) if not engine.match(t) and not (t.release_like or Q.is_method_constant(t, text))]
        added = []
        if refs:
            plain = [t for t in toks if t.kind not in ("pct", "pp", "bps")]
            iprd = n.get("iprd_adjustment") if isinstance(n.get("iprd_adjustment"), dict) else {}
            total = iprd.get("total") if iprd.get("treatment") == "not_applied_share_count_unverified" else None
            # (the count may coincide with a share figure of the synthetic record: picked from every number)
            count = next((t for t in Q.numbers(text) if t.kind == "plain"), None) if total else None
            charge = next((t for t in Q.numbers(text) if t.kind == "money" and count is not None and t is not count
                           and isinstance(total, (int, float)) and count.val
                           and abs(total / count.val - t.val) <= 0.5 * 10 ** (-t.dec)), None)
            if count is not None and charge is not None and len(refs) >= 2:
                # A14: the unverified-share-count hand deduction — the count a filing fact, the charge a calc fact
                new_facts.append(dict(_reason_fact(refs[0], count, tag, text, period), label="verified diluted shares"))
                new_facts.append({"id": refs[1], "label": "acquired-IPR&D charge per verified share", "value": charge.val,
                                  "unit": "USD/share", "precision": charge.dec, "period": period, "kind": "filing",
                                  "type": "actual", "calc": {"op": "ratio", "of": [
                                      "dcf_numbers.json:iprd_adjustment.total", refs[0]]}, "used_for": [tag]})
                plain = [t for t in plain if t.start not in (count.start, charge.start)]
                refs_left = refs[2:]
            else:
                refs_left = refs
            for fid, t in zip(refs_left, plain):
                new_facts.append(_reason_fact(fid, t, tag, text, period))
            run_values += [t.v / 100.0 for t in toks if t.kind in ("pct", "pp")]
            toks = plain[len(refs_left):]
        for t in toks:                    # untraced figures nothing cites yet: declared and cited
            fid = f"F{next_id}"
            next_id += 1
            new_facts.append(_reason_fact(fid, t, tag, text, period))
            added.append(fid)
        if not Q.carries_number(text):
            fid = NO_NUMBER_FACT_ID[field]
            new_facts.append({"id": fid, "label": "test reason figure", "value": TEST_FIGURE[0], "unit": "pct",
                              "precision": 2, "period": period, "kind": "filing", "type": "actual",
                              "source": dict(TEST_FILING), "snippet": f"{TEST_FIGURE[1]} per the test filing",
                              "used_for": [tag]})
            j[field] = f"{text} (test figure {TEST_FIGURE[1]} [{fid}])"
        elif added:
            j[field] = f"{text} [{', '.join(added)}]"
    if run_values:
        rec = copy.deepcopy(n)
        rec["implied_irr_weighted"] = run_values[0]
        if len(run_values) > 1:
            rec["test_reason_figures"] = run_values[1:]
        rec["content_hash"] = content_hash(rec)
        with open(os.path.join(folder, f"dcf_numbers_{SAVED_RUN_LABEL}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
    if new_facts:
        merge_facts(folder, new_facts, ticker=n.get("ticker"))
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


def add_minimal_scorecard_as_written(folder):
    """[Integrate L3] L3's obligation ALONE, for a test that writes its judgment verbatim (Run(judgment_text=...)) so
    that the reason obligations (L1's notch reason, L2's citations) leave the worker text exactly as written — L2's
    test_facts.S, L1's _as_written. On a 5.7 record (<folder>/dcf_numbers.json) whose judgment.json declares no
    moat_scorecard, add_minimal_scorecard's scorecard is added (judgment.json rewritten as JSON, indent 1, UTF-8,
    one trailing newline: the tests' own judgment_text format) and its facts merged into facts.json; when the judgment
    already carries the minimal scorecard (a test rewrote facts.json since), its facts are merged back. Every other
    key of the judgment, and every fact the test declared, is kept. A facts.json that is not a well-formed facts
    document (a schema-refusal test's) is left exactly as written and nothing is added: make_score refuses it at step
    2, before the moat scorecard is read. Returns True when the folder carries the minimal scorecard."""
    bad = object()

    def rd(name):
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            return None
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except ValueError:
            return bad
    n, j, fdoc = rd("dcf_numbers.json"), rd("judgment.json"), rd("facts.json")
    if not isinstance(j, dict) or not isinstance(n, dict) or not _is_57(n):
        return False
    if fdoc is not None:
        import sys
        sysdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if sysdir not in sys.path:
            sys.path.insert(0, sysdir)
        import facts as F
        if fdoc is bad or F.validate(fdoc, os.path.basename(os.path.normpath(folder))) is not None:
            return False
    if "moat_scorecard" not in j:
        add_minimal_scorecard(j, n=n, folder=folder)
        with open(os.path.join(folder, "judgment.json"), "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(j, indent=1, ensure_ascii=False) + "\n")
        return True
    if j["moat_scorecard"] != minimal_scorecard(*minimal_business_type(n, folder)):
        return False                       # the test's own scorecard: its facts are the test's business
    have = {f.get("id") for f in (fdoc or {}).get("facts") or [] if isinstance(f, dict)}
    missing = [copy.deepcopy(f) for f in MINIMAL_SCORECARD_FACTS if f["id"] not in have]
    if missing:
        merge_facts(folder, missing, ticker=(n or {}).get("ticker"))
    return True


INTERIM_DECLINED_FIXTURE = {"reason": "test fixture: the latest 6-K interim report (181 days to 2026-06-30) prints no "
                                      "condensed cash-flow statement, so no leg can be declared",
                            "report": None}


def add_interim_declined(n, j):
    """L4 (R2a): interim_bridge_declined with a numeric reason on a 5.7 STALE_FY 20-F / 40-F record that declares
    neither interim_bridge nor interim_bridge_declined and is not on the payable base — the obligation make_score's
    check_interim_obligation enforces (default Q7: a --base-oe-ps pin owes it too). Mutates j (apply() passes a copy);
    no record any pre-existing test builds carries STALE_FY, so this changes none of them."""
    if not isinstance(n, dict) or not isinstance(j, dict):
        return None
    import facts as _f
    if not _f.is_rulings_run(n) or n.get("filer_annual_form") not in ("20-F", "40-F"):
        return None
    if not any(str(fl).startswith("STALE_FY") for fl in n.get("fragility_flags") or []):
        return None
    if j.get("interim_bridge") is not None or j.get("interim_bridge_declined") is not None:
        return None
    if (n.get("inputs") or {}).get("base_pin_source") == "judgment_base_override":
        return None
    j["interim_bridge_declined"] = dict(INTERIM_DECLINED_FIXTURE)
    return None


UP_C_REASON_FIXTURE = ("test fixture: the noncontrolling interest is an ordinary subsidiary minority — the filed "
                       "diluted count covers every class (diluted ÷ basic 1.000)")


def add_up_c_reason(j, n):
    """L8 (R6): up_c_suspect_reason (carrying a number) on a 5.7 record flagged UP_C_SUSPECT that declares no
    share_classes and no reason of its own — the obligation make_score's check_up_c_obligation (R-8) enforces. No
    synthetic record a pre-existing test builds carries the flag, so this changes none of them; it exists so a later
    fixture cannot trip R-8 silently. Mutates j (apply() passes a copy)."""
    if not isinstance(n, dict) or not isinstance(j, dict):
        return None
    import facts as _f
    if not _f.is_rulings_run(n):
        return None
    if not any(str(fl).startswith("UP_C_SUSPECT") for fl in n.get("fragility_flags") or []):
        return None
    if j.get("share_classes") is not None or j.get("up_c_suspect_reason") is not None:
        return None
    j["up_c_suspect_reason"] = UP_C_REASON_FIXTURE
    return None


def _stale_fy(n):
    return any(str(f).startswith("STALE_FY") for f in (n or {}).get("fragility_flags") or [])


def _r7_published_not_ttm(n, j, ttm):
    """make_score.published_base_kind's answer, approximated for the fixtures (R7): True when the record's base is the
    annual median or a declared base_override pin not built on the TTM (the bases ttm_rejection_reason /
    ttm_unavailable_reason bind); False for the payable pin, a --ttm / via-TTM pin, a basis_window "ttm" pin and an
    iprd_amortized pin on the ttm_json native base."""
    inp = n.get("inputs") if isinstance(n.get("inputs"), dict) else {}
    src = inp.get("base_pin_source")
    if n.get("payable_base") or src == "judgment_base_override":
        return False
    if src is None and inp.get("base_oe_ps_arg") is None and "ttm" not in str(n.get("base_source") or "").lower():
        return True
    bo = (j or {}).get("base_override") if isinstance(j, dict) else None
    if src != "base_oe_ps_arg" or not isinstance(bo, dict):
        return False
    if bo.get("basis") == "iprd_amortized":
        return bo.get("native_base") != "ttm_json"
    if bo.get("basis") is not None:
        return False
    bw = inp.get("base_basis_window") if isinstance(inp.get("base_basis_window"), dict) else {}
    if bw.get("window") == "ttm":
        return False
    tv, pin = (ttm or {}).get("ttm_oe_per_share") if isinstance(ttm, dict) else None, inp.get("base_oe_ps_arg")
    near = (isinstance(tv, (int, float)) and isinstance(pin, (int, float)) and not isinstance(tv, bool)
            and abs(pin - tv) <= 1e-3 * abs(tv))
    return bw.get("window") == "fy" or not near


def _dollars(x):
    return f"{'-' if x < 0 else ''}${abs(x):,.2f}"


def _ttm_for_latest_fy(n, ttm):
    v = ttm.get("ttm_oe_per_share") if isinstance(ttm, dict) else None
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and ttm.get("fy_end") == (n or {}).get("latest_period_end"))


R7_REASON_MARK = "test (R7 G16):"   # the fixture reason add_ttm_rejection writes (r7_current re-derives it)
R7_UNAVAILABLE_RE = re.compile(r"ttm\.py: cannot compute TTM for \S+ \(CIK \d+\): sbc: no post-FY YTD fact \(no 10-Q "
                               r"since the [0-9-]+ fiscal year end\)$")   # the one add_ttm_unavailable writes


def add_ttm_rejection(j, n, ttm=None):
    """R7 (Andrew, 2026-10-19): on a 5.7 STALE_FY record whose published base is the annual median or a declared pin
    (not the TTM) beside a 10-Q ttm.json `ttm` for its latest FY, a qualifying ttm_rejection_reason — a cash-flow line
    and the record's and ttm.json's own figures (so every number traces). Untouched: a judgment that already carries
    the field (a test of it), an older record, a declared 6-K bridge ttm.json (L4's binding refusal is that test's
    subject), no ttm. Mutates j (apply() passes a copy)."""
    if not (isinstance(j, dict) and isinstance(n, dict) and isinstance(ttm, dict)) or "ttm_rejection_reason" in j:
        return None
    if not _is_57(n) or not _stale_fy(n) or ttm.get("basis") == "declared_interim" or not _ttm_for_latest_fy(n, ttm):
        return None
    b = n.get("base_oe_per_share")
    if not isinstance(b, (int, float)) or not _r7_published_not_ttm(n, j, ttm):
        return None
    j["ttm_rejection_reason"] = (f"{R7_REASON_MARK} the TTM base {_dollars(ttm['ttm_oe_per_share'])}/share against the "
                                 f"published {_dollars(b)}/share rests on a half-year working-capital swing")
    return None


def add_ttm_unavailable(j, n, ttm=None, ticker=None):
    """R7 default Q14: on a 5.7 STALE_FY 10-K record whose published base is the annual median or a declared pin and
    which has no TTM for its latest FY (`ttm` None, or a ttm.json on another FY), ttm.py's exit-3 message for it in
    ttm_unavailable_reason (what ttm.py prints when the 10-Q YTD facts are missing). Untouched otherwise, and when the
    judgment already carries the field. Mutates j."""
    if not (isinstance(j, dict) and isinstance(n, dict)) or "ttm_unavailable_reason" in j:
        return None
    if not _is_57(n) or not _stale_fy(n) or n.get("filer_annual_form") in ("20-F", "40-F"):
        return None
    if isinstance(ttm, dict) and (ttm.get("fy_end") == n.get("latest_period_end")
                                  and isinstance(ttm.get("ttm_oe_per_share"), (int, float))):
        return None
    if not _r7_published_not_ttm(n, j, ttm):
        return None
    try:
        cik = int(n.get("cik") or 0)
    except (TypeError, ValueError):
        cik = 0
    t = str(ticker or n.get("ticker") or "TST").upper()
    j["ttm_unavailable_reason"] = (f"ttm.py: cannot compute TTM for {t} (CIK {cik}): sbc: no post-FY YTD fact (no 10-Q "
                                   f"since the {n.get('latest_period_end')} fiscal year end)")
    return None


def r7_current(folder, sysdir=None, replies=None):
    """R7's obligations for a Run folder already written, called by a pre-existing test right before make_score runs
    (after it wrote ttm.json and installed its engine stand-in): judgment.json gains add_ttm_rejection /
    add_ttm_unavailable from the folder's own dcf_numbers.json / ttm.json (rewritten only when changed: JSON indent 1,
    UTF-8, one trailing newline — the tests' own format), and, given sysdir, the R7 base replays are answered beside
    the test's stand-in (answer_base_replays), so no pre-existing assertion about spawns changes. Returns folder."""
    def rd(name):
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            return None
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except ValueError:
            return None
    n, j, tt = rd("dcf_numbers.json"), rd("judgment.json"), rd("ttm.json")
    if isinstance(n, dict) and isinstance(j, dict):
        j2 = copy.deepcopy(j)
        # the fields an earlier call added are re-derived from the folder as it is now (a test that writes ttm.json
        # after building the folder turns "no TTM" into a TTM to reject); a field the test wrote itself is kept
        if str(j2.get("ttm_rejection_reason") or "").startswith(R7_REASON_MARK):
            del j2["ttm_rejection_reason"]
        if R7_UNAVAILABLE_RE.match(str(j2.get("ttm_unavailable_reason") or "")):
            del j2["ttm_unavailable_reason"]
        add_ttm_rejection(j2, n, ttm=tt)
        add_ttm_unavailable(j2, n, ttm=tt, ticker=os.path.basename(os.path.normpath(folder)))
        if j2 != j:
            with open(os.path.join(folder, "judgment.json"), "w", encoding="utf-8", newline="") as f:
                f.write(json.dumps(j2, indent=1, ensure_ascii=False) + "\n")
    if sysdir is not None and isinstance(n, dict):
        answer_base_replays(sysdir, n, ttm_doc=tt, replies=replies)
    return folder


def _dcf_engine():
    """The shared dcf_engine module (imported once with a neutral argv: the engine reads --measure from sys.argv)."""
    import importlib
    import sys
    if "dcf_engine" in sys.modules:
        return sys.modules["dcf_engine"]
    sysdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sysdir not in sys.path:
        sys.path.insert(0, sysdir)
    saved = sys.argv
    sys.argv = ["dcf_engine.py"]
    try:
        return importlib.import_module("dcf_engine")
    finally:
        sys.argv = saved


def add_ttm_engine_release(tt, n=None):
    """L9 (R8 / R9 TTM provenance; 09 rebase A8): a 5.7 run whose basis read ttm.json needs a ttm.json stamped by a
    5.7 ttm.py (make_score refuse_pre57_ttm_json), so a test that hand-writes a ttm.json for a current-release record
    stamps it here: tt["engine_release"] = dcf_engine.ENGINE_RELEASE (what ttm.py writes) and, given the record n
    whose ttm_inputs is a dict (the run read ttm.json), n["ttm_inputs"] = dcf_engine.ttm_inputs_record(tt) — the
    engine's own record of the stamped file — and n's content_hash re-stamped when it carries one. A record with
    ttm_inputs null (a median run) or absent (an older record) is left as it is. Modifies tt (and n) in place;
    returns tt."""
    if not isinstance(tt, dict):
        return tt
    E = _dcf_engine()
    tt["engine_release"] = E.ENGINE_RELEASE
    if isinstance(n, dict) and isinstance(n.get("ttm_inputs"), dict):
        n["ttm_inputs"] = E.ttm_inputs_record(tt)
        if "content_hash" in n:
            n["content_hash"] = content_hash(n)
    return tt


R7_WRAPPER_MARK = "# rulings57.answer_base_replays (R7)"
R7_INNER = "dcf_engine_standin_before_r7.py"
R7_WRAPPER = R7_WRAPPER_MARK + r'''
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
if os.environ.get("DCF_REPLAY_PURPOSE") == "base_alternatives":
    cfg = json.load(open(os.path.join(here, "base_replays.json"), encoding="utf-8"))
    with open(os.path.join(here, "BASE_REPLAY_" + os.path.basename(__file__) + ".txt"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"argv": sys.argv[1:], "no_overrides": os.environ.get("DCF_NO_OVERRIDES"),
                            "hold": os.environ.get("DCF_IPRD_HOLD")}) + "\n")
    rep = cfg.get("ttm" if "--ttm" in sys.argv else "median")
    if not isinstance(rep, dict):
        sys.exit(97)
    if "exit" in rep:
        sys.stdout.write(str(rep.get("stdout") or "") + "\n")
        sys.exit(int(rep["exit"]))
    sys.stdout.write(json.dumps(rep))
    sys.exit(0)
src = open(os.path.join(here, "''' + R7_INNER + r'''"), encoding="utf-8").read()
exec(compile(src, __file__, "exec"), {"__file__": __file__, "__name__": "__main__"})
'''


def answer_base_replays(sysdir, n, ttm_doc=None, replies=None):
    """R7 (07 G16): answer the DCF_REPLAY_PURPOSE=base_alternatives engine spawns beside whatever stand-in the test
    installed as <sysdir>/dcf_engine.py — the stand-in moves to R7_INNER and a wrapper answers R7's replays from
    `replies` ({"median": reply, "ttm": reply}; a reply is the engine's JSON or {"exit": 3, "stdout": "..."}), else
    from the record itself (the median reply: n's base_oe_normalized_per_share with n's IRR and tier; the TTM reply:
    ttm_doc's ttm_oe_per_share with dcf_engine.ttm_inputs_record(ttm_doc)), logging them to
    BASE_REPLAY_dcf_engine.py.txt; every other spawn runs the test's own stand-in unchanged (its SPAWNED_* log, its
    __file__). Idempotent; nothing when sysdir does not exist. Returns None."""
    if not os.path.isdir(sysdir):
        return None
    eng = os.path.join(sysdir, "dcf_engine.py")
    src = None
    if os.path.exists(eng):
        with open(eng, encoding="utf-8") as f:
            src = f.read()
    if src is None or R7_WRAPPER_MARK not in src:
        with open(os.path.join(sysdir, R7_INNER), "w", encoding="utf-8") as f:
            f.write(src if src is not None else "import sys\nsys.exit(97)\n")
        with open(eng, "w", encoding="utf-8") as f:
            f.write(R7_WRAPPER)
    rep = dict(replies or {})
    if "median" not in rep and isinstance(n, dict):
        b = n.get("base_oe_normalized_per_share", n.get("base_oe_per_share"))
        rep["median"] = {"base_oe_per_share": b, "implied_irr_weighted": n.get("implied_irr_weighted"),
                         "tier_by_numbers": n.get("tier_by_numbers"), "f_subtype": n.get("f_subtype"), "data_gap": []}
    if "ttm" not in rep and isinstance(n, dict) and isinstance(ttm_doc, dict):
        rep["ttm"] = {"base_oe_per_share": ttm_doc.get("ttm_oe_per_share"),
                      "implied_irr_weighted": n.get("implied_irr_weighted"), "tier_by_numbers": n.get("tier_by_numbers"),
                      "f_subtype": n.get("f_subtype"), "data_gap": [],
                      "ttm_inputs": _dcf_engine().ttm_inputs_record(ttm_doc)}
    with open(os.path.join(sysdir, "base_replays.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
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


_NO_TTM_GIVEN = object()   # R7: "the caller did not say whether a ttm.json exists" (Run.__init__ writes it later)


def apply(n, j, folder=None, ttm=_NO_TTM_GIVEN):
    """Every judgment-side obligation above, in lane merge order, on COPIES of engine record n and judgment j (either
    may be None); returns (n, j). The inputs are never modified. A record that carried a content_hash is re-stamped
    when an obligation changed it. The identity in L0. R7's two obligations read ttm.json, so they run only when the
    caller passes `ttm` (the folder's ttm.json object, or None for "no ttm.json" — make_current does); a caller that
    writes ttm.json later (test_make_score_55.Run) applies them right before the run with r7_current."""
    n2 = copy.deepcopy(n) if n is not None else None
    j2 = copy.deepcopy(j) if j is not None else None
    before = _canon(n2) if isinstance(n2, dict) else None
    add_notch_reason(n2, j2, folder=folder)               # L1
    cite_facts_for_reasons(j2, n2, folder=folder)         # L2
    add_minimal_scorecard(j2, n=n2, folder=folder)        # L3
    add_interim_declined(n2, j2)                          # L4
    add_up_c_reason(j2, n2)                               # L8
    if ttm is not _NO_TTM_GIVEN:                          # R7
        add_ttm_rejection(j2, n2, ttm=ttm)
        add_ttm_unavailable(j2, n2, ttm=ttm, ticker=os.path.basename(os.path.normpath(folder)) if folder else None)
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


# ---------------------------------------------------------------------------
# L2's fixtures for cite_facts_for_reasons (at the end of the file, which no lane edits, so each lane's hunk
# stays apart in the sequential merge)
# ---------------------------------------------------------------------------
REASON_FIELDS = (("tier_override_reason", "tier_override"), ("misfit_notch_reason", "misfit_notch"))
TEST_FILING = {"form": "10-K", "accession": "0000999001-26-000090", "section": "test fixture (07 G16)",
               "filed": "2026-02-20"}
TEST_FIGURE = (0.0875, "8.75%")          # the figure a reason with no number gains (collides with no synthetic leaf)
NO_NUMBER_FACT_ID = {"tier_override_reason": "F89", "misfit_notch_reason": "F88"}
SAVED_RUN_LABEL = "test_reasons"         # the saved method run that carries a reason's quoted IRR (rebase A14)
_SCALE_LETTER = {"trillion": "T", "tn": "T", "T": "T", "billion": "B", "bn": "B", "B": "B", "b": "B",
                 "million": "M", "mn": "M", "mm": "M", "M": "M", "m": "M", "thousand": "K", "K": "K", "k": "K"}


def _reason_fact(fid, tok, tag, text, period):
    """A filing fact declaring exactly the figure token tok shows (its snippet is the token itself)."""
    after = text[tok.end:tok.end + 6]
    unit = {"pct": "pct", "pp": "pp", "bps": "bps", "mult": "x", "plain": "count"}.get(tok.kind) or (
        "USD/share" if after.startswith("/share") else "USD")
    value = tok.v / 100.0 if tok.kind in ("pct", "pp") else tok.v / 1e4 if tok.kind == "bps" else tok.val
    return {"id": fid, "label": f"test reason figure {tok.raw}"[:80], "value": value, "unit": unit,
            "scale": _SCALE_LETTER.get(tok.scale, "") if tok.kind == "money" else "", "precision": tok.dec,
            "period": period, "kind": "filing", "type": "actual", "source": dict(TEST_FILING),
            "snippet": f"{tok.raw} per the test filing", "used_for": [tag]}
