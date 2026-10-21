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
    engine = CQ.engine_sources(folder, n, judgment=j)
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


def add_minimal_scorecard(j, n=None, folder=None):
    """L3 (R4): the minimal moat_scorecard (and its facts, merge_facts) a 5.7 run needs. No-op in L0."""
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
