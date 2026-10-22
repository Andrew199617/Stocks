#!/usr/bin/env python3
"""The hand-written documents stay in step with the code (docs group, 2026-10-16).
Run: python _system/tests/test_docs_contract.py (or python -m pytest _system/tests).
No network, no writes; reads only committed files (works on a fresh clone).

Documents: _system/SITE_CONTRACT.md, _system/README.md, automation/README.md.
A "named" key or option is one that appears inside code formatting in the
document (a `backtick` span or a fenced block), so prose that happens to use
the same word does not count.

1. Every key build_site.py puts on an index row (has.* included), on a
   data/<T>.json record and in meta.counts, and every history CSV column
   (HISTORY_COLUMNS), is named in SITE_CONTRACT.md — read from the code's own
   dict literals, so a new key fails here until the contract names it.
2. The keys and options the 2026-10-16 round added are still in the code AND
   named in the documents that describe them (a rename on either side fails):
   live.json's basis-check keys, record.live_withheld's reason, the
   restricted-cash arrays and line, last_minute, price_note / PRICE_LEAVES,
   --street-only, the app test's APP_TEST_BUILT / APP_TEST_BASE, score.json's
   entry and exit alert gates, queue.py pass2-check; and engine 5.5's
   score.json market_cap_basis / ads_corrected_by_make_score /
   in_scope_corrected_by_make_score, reprice.live_market_cap (the live ADS
   market cap), build_site.TRIM_NUMBERS_KEYS and app.js isOverrideTag / runCapText,
   plus the engine 5.5 CSV columns, dcf_numbers.json records and the
   scope_correction registry event that README's per-folder list names,
   and the verifier round's keys (score.json
   net_debt_to_normalized_oe_ads_basis, ttm.json
   capex_override_superseded_legs, the new share_scale / share_basis
   entries, the parts_of_total and no_ppe_leg capex records; after round 4
   median_latest_scale_breaks, ttm.json sbc_reconciliation_withdrawn_legs and
   the remainder_unknown intangible record).
3. automation/README.md's day table matches every cron file present: the
   "When" cell carries the front matter's cadence (every N min / HH:MM daily)
   and the row says "Disabled" exactly when `enabled: false`. Every cron file
   is present in every checkout (the daily files were renamed without colons).
4. The passages this round corrected stay corrected (the stale wording is
   absent) — also engine 5.5's verifier-round corrections in README,
   SITE_CONTRACT, WORKER_SPEC and AGENTS.md.
5. Engine 5.7 (Andrew's 2026-10-19/20 rulings R1-R9; lane L7 writes every
   lane's doc tests): the new keys, flags, files and switches are in the code
   and named in the documents that describe them (PAIRS also binds AGENTS.md,
   WORKER_SPEC and SECOND_PASS now); the notch, quote-gate, moat-rubric,
   moat-trend, share-class, capex and ops passages say what the code does;
   and the wording the rulings retired is absent.
"""
import ast
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
CONTRACT = "_system/SITE_CONTRACT.md"
SYS_README = "_system/README.md"
AUTO_README = "automation/README.md"
WORKER_SPEC = "_system/WORKER_SPEC.md"
AGENTS_MD = "AGENTS.md"
SECOND_PASS = "_system/SECOND_PASS.md"


def _read(rel):
    with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


def code_text(doc):
    """Everything a markdown document shows in code formatting: fenced blocks
    (line-anchored ``` fences) and inline `spans`, joined by newlines. An
    inline ``` (prose about fences) and ``double-backtick`` spans are dropped
    first so they cannot shift the pairing of single backticks."""
    fences = re.findall(r"^```[^\n]*\n(.*?)^```[ \t]*$", doc, flags=re.S | re.M)
    rest = re.sub(r"^```[^\n]*\n.*?^```[ \t]*$", "", doc, flags=re.S | re.M)
    rest = rest.replace("```", "")
    rest = re.sub(r"``.+?``", "", rest)
    assert rest.count("`") % 2 == 0, "unbalanced backticks: a span would swallow prose"
    spans = re.findall(r"`([^`]+)`", rest)
    return "\n".join(fences + spans)


def named(token, code):
    """token appears in code as a whole word (hyphens count as word characters,
    so `pass2-check` and `--street-only` match only whole)."""
    return re.search(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])", code) is not None


def _module(rel):
    return ast.parse(_read(rel), filename=rel)


def _function(tree, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name}() not found")


def _str_keys(d):
    return [k.value for k in d.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)]


def _assigned_dict(fn, target):
    """The dict literal assigned to `target` inside fn (the first one)."""
    for node in ast.walk(fn):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                and any(isinstance(t, ast.Name) and t.id == target for t in node.targets)):
            return node.value
    raise AssertionError(f"no `{target} = {{...}}` in {fn.name}()")


def _updated_keys(fn, target):
    """Keys of dict literals passed to `target.update({...})` inside fn."""
    out = []
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "update"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == target
                and node.args and isinstance(node.args[0], ast.Dict)):
            out += _str_keys(node.args[0])
    return out


def _value_of(d, key):
    for k, v in zip(d.keys, d.values):
        if isinstance(k, ast.Constant) and k.value == key:
            return v
    return None


def _missing(keys, code):
    return sorted({k for k in keys if not named(k, code)})


# ---------------------------------------------------------------- 1
def test_index_row_keys_are_named_in_the_contract():
    fn = _function(_module("_system/build_site.py"), "index_row")
    row = _assigned_dict(fn, "row")
    keys = _str_keys(row) + _updated_keys(fn, "row")
    has = _value_of(row, "has")
    assert isinstance(has, ast.Dict), "index_row() has no has={...}"
    keys += _str_keys(has)
    assert {"live_withheld", "split_restated", "statements", "profile", "shareholder_yield_label"} <= set(keys), keys
    code = code_text(_read(CONTRACT))
    assert not _missing(keys, code), f"index row keys not named in SITE_CONTRACT.md: {_missing(keys, code)}"


def test_record_keys_are_named_in_the_contract():
    fn = _function(_module("_system/build_site.py"), "build_record")
    keys = _str_keys(_assigned_dict(fn, "rec"))
    assert {"live_withheld", "split_restated", "profile", "prices"} <= set(keys), keys
    pr = _value_of(_assigned_dict(fn, "rec"), "prices")
    assert pr is not None
    code = code_text(_read(CONTRACT))
    assert not _missing(keys, code), f"record keys not named in SITE_CONTRACT.md: {_missing(keys, code)}"
    # record.prices: the keys build_record passes through from prices.json
    prices_keys = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Dict) and "sessions_5d" in _str_keys(node):
            prices_keys = _str_keys(node)
    assert "intraday" in prices_keys and "warnings" in prices_keys, prices_keys
    assert not _missing(prices_keys, code), f"record.prices keys not named: {_missing(prices_keys, code)}"


def test_meta_counts_and_history_columns_are_named_in_the_contract():
    tree = _module("_system/build_site.py")
    counts = None
    for node in ast.walk(_function(tree, "build")):
        if isinstance(node, ast.Dict):
            v = _value_of(node, "counts")
            if isinstance(v, ast.Dict):
                counts = _str_keys(v)
    assert counts and {"live_withheld", "split_restated", "with_live"} <= set(counts), counts
    cols = None
    for node in tree.body:
        if (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "HISTORY_COLUMNS" for t in node.targets)
                and isinstance(node.value, ast.Tuple)):
            cols = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
    assert cols and cols[0] == "rank", cols
    code = code_text(_read(CONTRACT))
    assert not _missing(counts, code), f"meta.counts keys not named: {_missing(counts, code)}"
    assert not _missing(cols, code), f"history CSV columns not named: {_missing(cols, code)}"


# ---------------------------------------------------------------- 2
# (code file, a literal that must still be in it, the token the documents name, the documents)
PAIRS = [
    ("_system/reprice.py", '"split_factor"', "split_factor", [CONTRACT, SYS_README]),
    ("_system/reprice.py", '"basis_check"', "basis_check", [CONTRACT, SYS_README]),
    ("_system/reprice.py", '"score_mismatch"', "score_mismatch", [CONTRACT]),
    ("_system/reprice.py", '"score_json_fresh"', "score_json_fresh", [CONTRACT]),
    ("_system/reprice.py", '"no_close_since_scoring"', "no_close_since_scoring", [CONTRACT]),
    ("_system/reprice.py", '"within_scored_day_range"', "within_scored_day_range", [CONTRACT]),
    ("_system/build_site.py", '"live_older_than_score"', "live_older_than_score", [CONTRACT]),
    ("_system/build_site.py", '"street_fetched_at"', "street_fetched_at", [CONTRACT]),
    ("_system/statements.py", '"incl_restricted_annual"', "incl_restricted_annual", [CONTRACT]),
    ("_system/statements.py", '"incl_restricted_quarterly"', "incl_restricted_quarterly", [CONTRACT]),
    ("_system/statements.py", '"incl_restricted_ttm"', "incl_restricted_ttm", [CONTRACT]),
    ("_system/statements.py", 'L("restricted_cash"', "restricted_cash", [CONTRACT]),
    ("_system/statements.py", "def restricted_cash_pending(", "restricted_cash_pending", [CONTRACT]),
    ("_system/prices.py", '"last_minute"', "last_minute", [CONTRACT]),
    ("_system/fundamentals.py", '"price_note"', "price_note", [CONTRACT]),
    ("_system/fundamentals.py", "PRICE_LEAVES = (", "PRICE_LEAVES", [CONTRACT]),
    ("_system/profile.py", '"--street-only"', "--street-only", [CONTRACT, SYS_README, AUTO_README]),
    ("_daily/site/tests/app.test.js", "process.env.APP_TEST_BUILT", "APP_TEST_BUILT", [CONTRACT]),
    ("_daily/site/tests/app.test.js", "process.env.APP_TEST_BASE", "APP_TEST_BASE", [CONTRACT]),
    ("_system/make_score.py", 'score["alert_eligible"]', "alert_eligible", [SYS_README, AUTO_README]),
    ("_system/make_score.py", 'score["exit_alert_eligible"]', "exit_alert_eligible", [SYS_README, AUTO_README]),
    ("_system/make_score.py", 'score["exit_alert_suppressed_reason"]', "exit_alert_suppressed_reason", [SYS_README]),
    # engine 5.5 (2026-10-19): score.json's market-cap basis / scope correction and the live ADS market-cap rule
    ("_system/make_score.py", '"market_cap_basis": mcap_basis', "market_cap_basis", [CONTRACT]),
    ("_system/make_score.py", '"ads_corrected_by_make_score"', "ads_corrected_by_make_score", [CONTRACT]),
    ("_system/make_score.py", 'score["in_scope_corrected_by_make_score"]', "in_scope_corrected_by_make_score", [CONTRACT]),
    ("_system/reprice.py", "def live_market_cap(", "live_market_cap", [CONTRACT]),
    ("_system/build_site.py", "TRIM_NUMBERS_KEYS = (", "TRIM_NUMBERS_KEYS", [CONTRACT]),
    ("_daily/site/app.js", "function isOverrideTag(", "isOverrideTag", [CONTRACT]),
    ("_daily/site/app.js", "function runCapText(", "runCapText", [CONTRACT]),
    # engine 5.5: the CSV columns and dcf_numbers.json records README's per-folder list names
    ("_system/dcf_engine.py", '"capex_ppe": capex_ppe', "capex_ppe", [SYS_README]),
    ("_system/dcf_engine.py", '"capex_intangibles": capex_intang_added', "capex_intangibles", [SYS_README]),
    ("_system/dcf_engine.py", '"capex_source": capex_source_p', "capex_source", [SYS_README]),
    ("_system/dcf_engine.py", '"shares_split_factor": None', "shares_split_factor", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"market_cap_basis": market_cap_basis', "market_cap_basis", [SYS_README]),
    ("_system/dcf_engine.py", '"share_scale": share_scale', "share_scale", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"share_basis": share_basis', "share_basis", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"share_class_mismatch": share_class', "share_class_mismatch", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"capex_provenance": capex_provenance', "capex_provenance", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"sbc_provenance": {', "sbc_provenance", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'used["capex_components"]', "capex_components", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"currency_basis": _ov_basis(field)', "currency_basis", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'fx_info["overrides_usd_verbatim"]', "overrides_usd_verbatim", [SYS_README, CONTRACT]),
    ("_system/make_score.py", '"event": "scope_correction"', "scope_correction", [SYS_README, CONTRACT]),
    # engine 5.5 verifier round (2026-10-19): the records its fixes added
    ("_system/make_score.py", 'score["net_debt_to_normalized_oe_ads_basis"]', "net_debt_to_normalized_oe_ads_basis",
     [SYS_README, CONTRACT]),
    ("_system/ttm.py", '"capex_override_superseded_legs": capex_superseded', "capex_override_superseded_legs",
     [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"pin_rejected": None', "pin_rejected", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"leverage_unverifiable": False', "leverage_unverifiable", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'growth_inputs_dropped=list(_gone)', "growth_inputs_dropped", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"in_history_split_facts": [', "in_history_split_facts", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"nonpositive_counts": [', "nonpositive_counts", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"periods_override_not_rescaled": [', "periods_override_not_rescaled", [SYS_README]),
    ("_system/dcf_engine.py", '"parts_of_total"', "parts_of_total", [SYS_README]),
    ("_system/dcf_engine.py", 'rec["intangibles_not_added"] = "no_ppe_leg"', "no_ppe_leg", [SYS_README]),
    ("_system/queue.py", '"pass2-check"', "pass2-check", [SYS_README, AUTO_README]),
    # engine 5.5 verifier round 2 (2026-10-19): the records its fixes added
    ("_system/dcf_engine.py", '"pin_over_price": False', "pin_over_price", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'growth_inputs_kept=', "growth_inputs_kept", [SYS_README, CONTRACT]),
    ("_system/ttm.py", "def share_scale_warnings(", "share_scale_warnings", [SYS_README]),
    # engine 5.5 verifier round 3 (2026-10-19): the records its fixes added
    ("_system/dcf_engine.py", '"pin_factor_withheld": None', "pin_factor_withheld", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def median_window_counts(", "median_window_counts", [SYS_README]),
    ("_system/dcf_engine.py", '"confirmed_against_period": split_confirm_row', "confirmed_against_period",
     [SYS_README, CONTRACT]),
    # engine 5.5 verifier round 4 (2026-10-19): the records its fixes added
    ("_system/dcf_engine.py", "def median_latest_scale_breaks(", "median_latest_scale_breaks", [SYS_README]),
    ("_system/ttm.py", '"sbc_reconciliation_withdrawn_legs": sbc_withdrawn', "sbc_reconciliation_withdrawn_legs",
     [SYS_README, CONTRACT]),
    ("_system/ttm.py", '"remainder_unknown"', "remainder_unknown", [SYS_README, CONTRACT]),
    # engine 5.6 (2026-10-19, acquired IPR&D one-time value adjustment — Andrew): the records, helpers and the site line
    ("_system/dcf_engine.py", '"iprd_adjustment": iprd', "iprd_adjustment", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def adjusted_value(", "adjusted_value", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def adjusted_irr(", "adjusted_irr", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def iprd_charge_per_share(", "iprd_charge_per_share", [SYS_README]),
    # [Codex review r8 of PR #47] already_in_capex only through the declared presentation; the size is a note
    ("_system/dcf_engine.py", '"paid_in_intangible_capex": "already_in_capex"', "paid_in_intangible_capex", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'rec["capex_overlap_note"] = ', "capex_overlap_note", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def iprd_date_ok(", "iprd_date_ok", [SYS_README]),
    ("_system/dcf_engine.py", 'rec["expense_tags_conflict"] = conflict', "expense_tags_conflict", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "unconverted_remainder_of=list(unknown_rest)", "unconverted_remainder_of", [SYS_README, CONTRACT]),
    ("_system/make_score.py", 'IPRD_DEFERRED_EVENT = "iprd_deferred_payment"', "paid_to_date", [SYS_README, CONTRACT]),
    ("_system/make_score.py", 'score["iprd_adjustment"] = _iprd', "iprd_adjustment", [SYS_README, CONTRACT]),
    ("_system/reprice.py", '"iprd_charge_per_share": charge', "iprd_charge_per_share", [SYS_README, CONTRACT]),
    ("_system/build_site.py", "def iprd_charge(", "iprd_charge", [CONTRACT]),
    ("_daily/site/app.js", "function iprdNote(", "iprdNote", [CONTRACT, SYS_README]),
    # engine 5.6 review round: the counterfactual's held IPR&D charge and its record
    ("_system/make_score.py", '"DCF_IPRD_HOLD": _iprd_hold(n)', "DCF_IPRD_HOLD", [SYS_README]),
    ("_system/dcf_engine.py", 'iprd["held_from_final_run"] = held', "held_from_final_run", [SYS_README]),
    # engine 5.6 fixer review round: the cash-flow check for an expense-basis period, deferred payments
    ("_system/dcf_engine.py", 'IPRD_CF_CHECK_KEY = "iprd_cash_flow_check"', "iprd_cash_flow_check", [SYS_README]),
    ("_system/dcf_engine.py", 'IPRD_AWAITING = "awaiting_cash_flow_check"', "awaiting_cash_flow_check", [SYS_README]),
    ("_system/dcf_engine.py", '"ACQUIRED_IPRD_UNCONFIRMED: ', "ACQUIRED_IPRD_UNCONFIRMED", [SYS_README]),
    ("_system/dcf_engine.py", "deferred_payment=(", "deferred_payment", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'rec["cash_flow_check"] = ', "cash_flow_check", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'rec["cash_sign_note"] = ', "cash_sign_note", [SYS_README]),
    ("_system/make_score.py", '"unconfirmed_total": b.get("unconfirmed_total")', "unconfirmed_total", [SYS_README, CONTRACT]),
    # deferred payments of an earlier deal (Andrew's 2026-10-20 ruling, delegated to the main agent)
    ("_system/dcf_engine.py", 'IPRD_DEFERRED_KEY = "iprd_deferred_payment"', "iprd_deferred_payment", [SYS_README]),
    ("_system/dcf_engine.py", 'rec["deferred_payment_of"] = ', "deferred_payment_of", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'rec["recurrence_excluded"] = ', "recurrence_excluded", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'iprd["deferred_payments_refused"] = ', "deferred_payments_refused", [SYS_README]),
    ("_system/dcf_engine.py", '"BAD_IPRD_DEFERRED_PAYMENT for ', "BAD_IPRD_DEFERRED_PAYMENT", [SYS_README]),
    ("_system/make_score.py", 'out["recurrence_excluded"] = ', "recurrence_excluded", [SYS_README, CONTRACT]),
    # Codex review round of the same ruling
    ("_system/dcf_engine.py", 'iprd["deferred_payments_rolled_out"] = ', "deferred_payments_rolled_out", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"first_charge_evidence": c[3]', "first_charge_evidence", [SYS_README]),
    ("_system/dcf_engine.py", 'IPRD_DEFERRED_WINDOWS = ("fy",)', "fy", [SYS_README]),
    # the per-deal cap (the main agent's decision on the review's open item, delegated by Andrew 2026-10-20)
    ("_system/dcf_engine.py", '"contingent_total": {"value": float(', "contingent_total", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def iprd_deferred_cap_problems(", "iprd_deferred_cap_problems", [SYS_README]),
    # Codex review round 9 of PR #47: a rolled-out period is a fiscal-year end; a recorded deal's evidence is fixed
    ("_system/dcf_engine.py", 'iprd["fy_period_ends"] = _fy_ends', "fy_period_ends", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def iprd_fy_end_problem(", "iprd_fy_end_problem", [SYS_README]),
    ("_system/dcf_engine.py", "def iprd_fy_period_ends(", "iprd_fy_period_ends", [SYS_README]),
    # engine 5.6 Codex review round 1 of PR #47
    ("_system/make_score.py", "def check_iprd_share_count_unverified(", "not_applied_share_count_unverified", [SYS_README]),
    ("_system/dcf_engine.py", "expense_fx_note=(", "expense_fx_note", [SYS_README]),
    # engine 5.6 Codex review round 2 of PR #47
    ("_system/dcf_engine.py", "def iprd_accession_year(", "iprd_accession_year", [SYS_README]),
    # engine 5.6 Codex review round 4 of PR #47
    ("_system/dcf_engine.py", "cash_native=float(cnative)", "cash_native", [SYS_README]),
    ("_system/make_score.py", "def _ads_factor(", "ADS ratio", [SYS_README]),
    ("_system/build_site.py", 'else "iprd_share_count_unverified"', "iprd_share_count_unverified", [SYS_README, CONTRACT]),
    ("_system/make_score.py", "def iprd_amortized_impact(", "iprd_amortized_impact", [SYS_README]),
    ("_system/make_score.py", '"iprd_charge_per_share_without_override"', "iprd_charge_per_share_without_override", [SYS_README]),
    # engine 5.6 Codex review round 3 of PR #47
    ("_system/dcf_engine.py", 'IPRD_UNCONVERTED = "non_usd_no_rate"', "non_usd_no_rate", [SYS_README]),
    ("_system/dcf_engine.py", '"ACQUIRED_IPRD_UNCONVERTED: ', "ACQUIRED_IPRD_UNCONVERTED", [SYS_README]),
    ("_system/dcf_engine.py", '"ACQUIRED_IPRD_UNMATCHED_PAYMENT: ', "ACQUIRED_IPRD_UNMATCHED_PAYMENT",
     [SYS_README]),
    ("_system/dcf_engine.py", 'x["pre_window_charges"] = ', "pre_window_charges", [SYS_README]),
    ("_system/dcf_engine.py", "def iprd_pre_window_charges(", "iprd_pre_window_charges", [SYS_README]),
    ("_system/make_score.py", "def check_iprd_unconverted(", "expense_native", [SYS_README]),
    # engine 5.6 Codex review round 6 of PR #47
    ("_system/dcf_engine.py", "cash_native=float(cnat)", "cash_fx_note", [SYS_README]),
    ("_system/dcf_engine.py", "def iprd_unresolved(", "iprd_unresolved", [SYS_README, CONTRACT]),
    ("_system/build_site.py", '"iprd_unresolved" if unresolved', "iprd_unresolved", [SYS_README, CONTRACT]),
    # Codex review round 11 of PR #47: tiled window legs, partial coverage, and the general live-figure rule
    ("_system/dcf_engine.py", 'IPRD_AGGREGATED = "aggregated_quarters"', "aggregated_quarters", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'x["aggregated_contexts"] = ', "aggregated_contexts", [SYS_README, CONTRACT]),
    # Codex review round 18 of PR #47: the tiled unit the figure was read from; the other tiled units beside it
    ("_system/dcf_engine.py", 'x["aggregated_contexts_other_units"] = ', "aggregated_contexts_other_units",
     [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'out["partial_coverage"] = partial', "partial_coverage", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '"ACQUIRED_IPRD_PARTIAL_PERIOD: ', "ACQUIRED_IPRD_PARTIAL_PERIOD", [SYS_README]),
    ("_system/dcf_engine.py", "def iprd_tile(", "iprd_tile", [SYS_README]),
    ("_system/reprice.py", "def check_score(", "check_score", [SYS_README, CONTRACT]),
    ("_system/build_site.py", '"reason": "score_not_from_this_run"', "score_not_from_this_run", [SYS_README, CONTRACT]),
    ("_system/build_site.py", "def score_from_run(", "score_from_run", [SYS_README, CONTRACT]),
    # Codex review round 12 of PR #47: the score bound to its run's content hash; share-paid residuals
    ("_system/make_score.py", '"dcf_content_hash": ch', "dcf_content_hash", [SYS_README, CONTRACT]),
    ("_system/reprice.py", "def run_hash_problem(", "run_hash_problem", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'rec["residual_paid_in_shares"] = ', "residual_paid_in_shares", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'rec["deferred_payment_assumption"] = (', "deferred_payment_assumption",
     [SYS_README, CONTRACT]),
    # Codex review round 13 of PR #47: the hash required for current-release scores; the notice without live.json
    ("_system/reprice.py", 'HASH_REQUIRED_FROM_RELEASE = "5.6.0"', "HASH_REQUIRED_FROM_RELEASE", [SYS_README, CONTRACT]),
    ("_system/reprice.py", "def requires_content_hash(", "requires_content_hash", [SYS_README, CONTRACT]),
    # Codex review round 19 of PR #47: the window's start; the registry transaction; the notice for every published run
    ("_system/build_site.py", "def run_published(", "run_published", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def iprd_window_start(", "iprd_window_start", [SYS_README]),
    ("_system/dcf_engine.py", "def iprd_before_window(", "iprd_before_window", [SYS_README]),
    ("_system/make_score.py", "def registry_transaction(", "registry_transaction", [SYS_README]),
    ("_system/dcf_engine.py", "def _iprd_is_zero(", "_iprd_pick", [SYS_README]),
    # Codex review round 14 of PR #47: a mismatched check refused on any basis; a negative detector fact is no charge
    ("_system/make_score.py", 'mm = [p for p in periods if p.get("cash_flow_check_mismatch")', "cash_flow_check_mismatch",
     [SYS_README]),
    ("_system/dcf_engine.py", 'rec["expense_reversal_note"] = (', "expense_reversal_note", [SYS_README, CONTRACT]),
    # Codex review round 15 of PR #47: unit conflicts, a cash-basis check the cash path cannot honor, the minimal
    # deferred_payments_only score block, a plain pin's basis_window
    ("_system/dcf_engine.py", 'x["unit_conflict"] = units_conflict', "unit_conflict", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", 'IPRD_UNIT_TOLERANCE = 0.01', "IPRD_UNIT_TOLERANCE", [SYS_README]),
    ("_system/dcf_engine.py", 'rec["cash_flow_check_inapplicable"] = dict(', "cash_flow_check_inapplicable",
     [SYS_README, CONTRACT]),
    ("_system/make_score.py", 'ia = [p for p in periods if isinstance(p.get("cash_flow_check_inapplicable"), dict)]',
     "cash_flow_check_inapplicable", [SYS_README]),
    ("_system/make_score.py", '"deferred_payments_only": True, "periods": []', "deferred_payments_only",
     [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", '**({"base_basis_window": base_basis_window}', "base_basis_window", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def base_basis_window_problem(", "base_basis_window_problem", [SYS_README]),
    ("_system/make_score.py", "def check_base_basis_window(", "basis_window", [SYS_README, CONTRACT]),
    # Codex review round 16 of PR #47: units tiled beside an exact fact; the site note binds to the score's own run
    ("_system/dcf_engine.py", "def iprd_tile(facts, tag, start, end, only_units=None):", "only_units", [SYS_README]),
    ("_daily/site/app.js", "var nb = obj(obj(record.numbers).iprd_adjustment), r = num(nb.ads_ratio);",
     "numbers.iprd_adjustment.ads_ratio", [SYS_README, CONTRACT]),
    # Codex review round 17 of PR #47: a declared rest beside an automatic settlement
    ("_system/dcf_engine.py", "automatic_settlement=auto, declared_residual=amt", "declared_residual",
     [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "automatic_settlement=auto, declared_residual=amt", "automatic_settlement",
     [SYS_README, CONTRACT]),
    # Codex review round 22 of PR #47: the run's hash of its IPR&D judgment inputs, checked by make_score
    ("_system/dcf_engine.py", '"iprd_judgment_hash": iprd_judgment', "iprd_judgment_hash", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def iprd_judgment_inputs(", "iprd_judgment_inputs", [SYS_README]),
    ("_system/make_score.py", "def check_iprd_judgment_current(", "check_iprd_judgment_current", [SYS_README]),
    # Codex review round 23 of PR #47: what a pinned run read from ttm.json, checked by make_score
    ("_system/dcf_engine.py", '"ttm_inputs": ttm_inputs', "ttm_inputs", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "def ttm_input_legs(", "ttm_input_legs", [SYS_README]),
    ("_system/dcf_engine.py", "def ttm_inputs_record(", "ttm_inputs_record", [SYS_README, CONTRACT]),
    ("_system/make_score.py", "def check_ttm_inputs_current(", "check_ttm_inputs_current", [SYS_README]),
    # Codex review round 24 of PR #47: a declared FY-built pin is never a TTM pin; an unconvertible parallel tag gates
    ("_system/make_score.py", "def declared_fy_built_pin(", "declared_fy_built_pin", [SYS_README]),
    ("_system/dcf_engine.py", "expense_tag_unconverted=tags_unconv", "expense_tag_unconverted", [SYS_README, CONTRACT]),
    ("_system/dcf_engine.py", "rec[\"cash_flow_check_not_applied\"]", "cash_flow_check_not_applied", [SYS_README, CONTRACT]),
    # Codex review round 25 of PR #47: declared-pin and ttm.json-figure matches at half a cent when either is zero
    ("_system/dcf_engine.py", "def pin_matches(", "pin_matches", [SYS_README]),
    ("_system/dcf_engine.py", "PIN_MATCH_ZERO_ABS = 0.005", "PIN_MATCH_ZERO_ABS", [SYS_README]),
    # Codex review round 26 of PR #47: the half cent is declaration arithmetic only; a malformed registry is refused
    ("_system/dcf_engine.py", "def figure_matches(", "figure_matches", [SYS_README]),
    ("_system/dcf_engine.py", "def declared_value_matches(", "declared_value_matches", [SYS_README]),
    ("_system/dcf_engine.py", "IPRD_AMORTIZED_ZERO_EPS = 1e-9", "IPRD_AMORTIZED_ZERO_EPS", [SYS_README]),
    ("_system/make_score.py", "def load_registry(", "load_registry", [SYS_README]),
    # Codex review round 29 of PR #47: a first charge carries its own expense; a whole charge unknown in USD is never
    # declared whole; live figures need the run's current score and are bound to it
    ("_system/dcf_engine.py", "def iprd_has_own_expense(", "iprd_has_own_expense", [SYS_README]),
    ("_system/dcf_engine.py", "def iprd_whole_charge_unknown(", "iprd_whole_charge_unknown", [SYS_README]),
    ("_system/build_site.py", '"reason": "live_not_from_this_score"', "live_not_from_this_score", [SYS_README, CONTRACT]),
    ("_system/build_site.py", "def live_score_problem(", "live_score_problem", [SYS_README, CONTRACT]),
    ("_system/reprice.py", '"dcf_content_hash": scored.get("dcf_content_hash")', "dcf_content_hash", [CONTRACT]),
    # the round-29 review notes: ACQUIRED_IPRD_CHARGE names a cash settlement as one
    ("_system/dcf_engine.py", "def _iprd_settles_earlier_charge(", "_iprd_settles_earlier_charge", [SYS_README]),
    # the round-29 polish review: one rule for a year's own charge in USD; a live.json with no score identity has its
    # own reason
    ("_system/dcf_engine.py", "def iprd_own_charge_usd(", "iprd_own_charge_usd", [SYS_README]),
    ("_system/build_site.py", '"reason": "live_without_score_identity"', "live_without_score_identity", [SYS_README, CONTRACT]),
    ("_system/build_site.py", "def live_score_identity_missing(", "live_score_identity_missing", [SYS_README, CONTRACT]),
    # the round-29 second polish review: a year's own expense reads every expense tag in every unit; unknown only there
    ("_system/dcf_engine.py", "def iprd_own_expense_unknown(", "iprd_own_expense_unknown", [SYS_README]),
    # Codex review round 30 of PR #47: a TTM base's IPR&D share count is ttm.json's, validated, or the run is refused
    ("_system/dcf_engine.py", "def iprd_ttm_share_count(", "iprd_ttm_share_count", [SYS_README]),
    ("_system/dcf_engine.py", 'print(f"BAD_TTM_SHARES for {ticker}: ', "BAD_TTM_SHARES", [SYS_README]),
    # ruling-sheet Q8 bugs 2-3 (Andrew, 2026-10-19): the enrichment rules the fixes added
    ("_system/fundamentals.py", "def money_unit(", "money_unit", [SYS_README, CONTRACT]),
    ("_system/fundamentals.py", "def class_count_check(", "class_count_check", [SYS_README, CONTRACT]),
    ("_system/fundamentals.py", "ENGINE_INTANGIBLE_TAGS = _engine.CAPEX_INTANGIBLE_TAGS", "ENGINE_INTANGIBLE_TAGS", [SYS_README, CONTRACT]),
    ("_system/fundamentals.py", 'PRICE_CURRENCY = "USD"', "PRICE_CURRENCY", [SYS_README, CONTRACT]),
    ("_system/fundamentals.py", "_engine.DEI_MAX_AGE_DAYS", "DEI_MAX_AGE_DAYS", [SYS_README, CONTRACT]),
    # verifier round 1 on the Q8 branch
    ("_system/fundamentals.py", "def pick_money_unit(", "pick_money_unit", [SYS_README, CONTRACT]),
    ("_system/fundamentals.py", "def intangible_capex_ttm(", "intangible_capex_ttm", [SYS_README, CONTRACT]),
    ("_system/build_site.py", "def cross_currency_safe(", "cross_currency_safe", [SYS_README, CONTRACT]),
    ("_system/statements.py", "DEBT_LIKE_TAGS = [", "DEBT_LIKE_TAGS", [SYS_README, CONTRACT]),
    # Codex review round 2 on PR #53
    ("_system/fundamentals.py", "ENGINE_CAPEX_GROUPS = (_engine.CAPEX_ROLLUP_TAGS", "ENGINE_CAPEX_GROUPS", [SYS_README, CONTRACT]),
    ("_system/fundamentals.py", "def annual_row_periods(", "annual_row_periods", [SYS_README, CONTRACT]),
    # ---- engine 5.7 (Andrew's rulings R1-R9, 2026-10-19/20; the lanes' doc notes, written by L7) ----
    # L1 (R1): the mechanical sector-misfit notch; misfits by universe sector OR EDGAR SIC (01 T-16)
    ("_system/make_score.py", 'score["misfit_notch"] = notch', "misfit_notch",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", 'score["misfit_sector_set_aside"] = set_aside', "misfit_sector_set_aside",
     [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/facts.py", '"misfit_notch_reason": "misfit_notch"', "misfit_notch_reason", [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", "def sector_model_record(", "sector_model", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", "def misfit_status(", "misfit_status", [SYS_README]),
    ("_system/dcf_engine.py", "def notch_tier(", "notch_tier", [SYS_README]),
    ("_system/dcf_engine.py", "MISFIT_SIC_RANGES = (", "MISFIT_SIC_RANGES", [SYS_README, AGENTS_MD]),
    ("_system/dcf_engine.py", "SIC_SETS_ASIDE_SECTOR = ", "dcf_engine.SIC_SETS_ASIDE_SECTOR", [SYS_README, AGENTS_MD]),
    # L2 (R3): declared facts, saved runs and the quote gate (02 §10)
    ("_system/facts.py", 'os.path.join(folder, "facts.json")', "facts.json", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/queue.py", "import check_quotes as _quotes", "check_quotes.py",
     [SYS_README, AUTO_README, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/check_quotes.py", "python3 _system/check_quotes.py --save-run <T> <label> [--replace]", "--save-run",
     [SYS_README, AUTO_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/check_quotes.py", "<T>/dcf_numbers_<label>.json", "dcf_numbers_<label>.json",
     [SYS_README, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/make_score.py", 'score["key_numbers_sha256"] = hashlib', "key_numbers_sha256",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", 'score["declared_facts"] = fc.summary()', "declared_facts", [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/make_score.py", 'score["method_runs"] = ', "method_runs", [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/make_score.py", 'score["previous_score"] = previous', "previous_score", [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/quote_tokens.py", "SNIPPET_MAX_WORDS = ", "SNIPPET_MAX_WORDS", [SYS_README]),
    # L3 (R4 revised): the combined moat scorecard (03 §14.19: moat_evidence named)
    ("_system/make_score.py", 'score["moat_evidence"] = moat_ev', "moat_evidence", [CONTRACT, SYS_README, AGENTS_MD, SECOND_PASS]),
    ("_system/moat_scorecard.py", "SCORECARD_VERSION = 1", "moat_scorecard", [SYS_README, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/moat_scorecard.py", "def evaluate(", "moat_scorecard.py", [SYS_README, AUTO_README, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/fundamentals.py", "def capital_returns_from_row(", "capital_returns_from_row", [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/industry_returns.py", 'ap.add_argument("--write", action="store_true")', "industry_returns.json",
     [SYS_README, AUTO_README]),
    ("_system/moat_scorecard.py", "ADDBACK_IPRD = ", "moat_scorecard.ADDBACK_IPRD", [SYS_README]),
    # L3b (M6): the moat's direction sets the growth hold (10 T26)
    ("_system/dcf_engine.py", "HOLD_BY_TREND = {", "--moat-trend", [SYS_README, AUTO_README, WORKER_SPEC, SECOND_PASS]),
    ("_system/dcf_engine.py", "EXIT_BAD_MOAT_TREND = ", "BAD_MOAT_TREND", [WORKER_SPEC]),
    ("_system/dcf_engine.py", 'f"MOAT_TREND_HOLD: moat eroding', "MOAT_TREND_HOLD", [AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'HOLD_RULE = "', "dcf_engine.HOLD_RULE", [SYS_README]),
    ("_system/dcf_engine.py", '"moat_trend": moat_trend, "hold_years": hold_years,', "hold_years",
     [CONTRACT, SYS_README, AGENTS_MD]),
    ("_system/dcf_engine.py", '"moat_trend": moat_trend, "hold_years": hold_years,', "moat_trend",
     [CONTRACT, SYS_README, AGENTS_MD]),
    ("_system/moat_scorecard.py", "TREND_ROW_SOURCES = (", "TREND_ROW_SOURCES", [SYS_README]),
    ("_system/moat_scorecard.py", "FADE_DRIFT_ON_REBUILD = ", "FADE_DRIFT_ON_REBUILD", [SYS_README]),
    ("_system/moat_scorecard.py", "COST_POSITION_METRICS = (", "moat_scorecard.COST_POSITION_METRICS", [WORKER_SPEC]),
    # L4 (R2): the declared 6-K interim bridge and the annual-from-instance fallback
    ("_system/dcf_engine.py", "def load_annual_instance(", "annual_instance.json", [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'result["annual_from_instance"] = annual_instance', "annual_from_instance",
     [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/dcf_engine.py", '"ANNUAL_FROM_INSTANCE: fiscal year(s)', "ANNUAL_FROM_INSTANCE",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", "def interim_pin_state(", "interim_bridge", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", "def check_interim_obligation(", "interim_bridge_declined",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", 'INTERIM_OBLIGATION_RULE = "re_declare"', "INTERIM_OBLIGATION_RULE", [SYS_README]),
    ("_system/make_score.py", "def interim_bridge_measurement(", "base_alternatives", [SYS_README, CONTRACT]),
    ("_system/make_score.py", 'INTERIM_FLAG = "TTM_DECLARED_INTERIM"', "TTM_DECLARED_INTERIM",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", "def _interim_rule_problems(", "declaration_rule_problems", [SYS_README, AGENTS_MD]),
    ("_system/interim_bridge.py", "def declaration_rule_problems(", "declaration_rule_problems", [SYS_README, AGENTS_MD]),
    ("_system/interim_bridge.py", "PERIOD_SOURCE_DEI = ", "interim_bridge.py", [SYS_README, AGENTS_MD]),
    ("_system/xbrl_instance.py", "def parse_undimensioned(", "xbrl_instance.py", [SYS_README, AGENTS_MD]),
    ("_system/ttm.py", "def interim_main(", "--interim", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/ttm.py", "Usage: python3 ttm.py <TICKER> [--cik N] [--interim | --interim-draft <6-K accession>]",
     "--interim-draft", [SYS_README, WORKER_SPEC]),
    # L6 (site, 06 §4.3)
    ("_system/build_site.py", "def quote_check(", "quote_check", [CONTRACT]),
    ("_system/build_site.py", '"declared_interim"', "declared_interim", [CONTRACT, AGENTS_MD]),
    ("_system/build_site.py", "def score_run_record(", "score_from_run", [CONTRACT]),
    ("_daily/site/app.js", "function notchView(", "notchView", [CONTRACT]),
    ("_daily/site/app.js", "function edgarFilingUrl(", "edgarFilingUrl", [CONTRACT]),
    ("_daily/site/app.js", "function httpsUrl(", "httpsUrl", [CONTRACT]),
    ("_daily/site/app.js", "function fmtFactValue(", "fmtFactValue", [CONTRACT]),
    # R7 (STALE_FY discretion made checkable; design 11)
    ("_system/make_score.py", "def ttm_rejection_problem(", "ttm_rejection_reason",
     [SYS_README, CONTRACT, AUTO_README, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/make_score.py", "def ttm_unavailable_problem(", "ttm_unavailable_reason",
     [SYS_README, CONTRACT, AUTO_README, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/make_score.py", "def build_base_alternatives(", "base_alternatives",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC, SECOND_PASS]),
    ("_system/make_score.py", '"base_alternatives": ("chosen"', "base_alternatives", [SYS_README]),
    ("_system/make_score.py", "R7_OBLIGATION_SCOPE = ", "R7_OBLIGATION_SCOPE", [SYS_README]),
    ("_system/make_score.py", "R7_TTM_UNAVAILABLE_RULE = ", "R7_TTM_UNAVAILABLE_RULE", [SYS_README]),
    ("_system/make_score.py", "R7_MEDIAN_BESIDE_TTM = ", "R7_MEDIAN_BESIDE_TTM", [SYS_README]),
    ("_system/make_score.py", "R7_ALERT_RULE = ", "R7_ALERT_RULE", [SYS_README]),
    ("_system/make_score.py", "R7_DECLARED_PIN_RULE = ", "R7_DECLARED_PIN_RULE", [SYS_README]),
    # L8 (R6): declared share classes and the Up-C detector (08 docs tests)
    ("_system/dcf_engine.py", 'result["share_classes"] = sc_record', "share_classes",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'result["up_c_check"] = up_c', "up_c_check", [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/dcf_engine.py", 'SHARE_CLASSES_TAG = "+SHARE_CLASSES"', "+SHARE_CLASSES", [SYS_README, CONTRACT, AGENTS_MD]),
    ("_system/dcf_engine.py", 'f"SHARE_CLASSES_DECLARED: ', "SHARE_CLASSES_DECLARED", [CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'f"SHARE_CLASSES_NCI_GAP: ', "SHARE_CLASSES_NCI_GAP", [AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'f"SHARE_CLASSES_CAP_GAP: ', "SHARE_CLASSES_CAP_GAP", [AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'f"UP_C_SUSPECT: ', "UP_C_SUSPECT", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", '"(judgment.json up_c_suspect_reason)"', "up_c_suspect_reason",
     [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'print(f"BAD_SHARE_CLASSES for {ticker}: ', "BAD_SHARE_CLASSES", [WORKER_SPEC]),
    ("_system/dcf_engine.py", 'print(f"BAD_TTM_SHARE_BASIS for {ticker}: ', "BAD_TTM_SHARE_BASIS", [WORKER_SPEC]),
    ("_system/make_score.py", 'if o["share_basis"] not in SHARE_BASIS_VALUES', "share_basis",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/share_classes.py", '"in_filed_count": ifc is True', "in_filed_count", [AGENTS_MD, WORKER_SPEC]),
    ("_system/share_classes.py", "def ttm_on_declaration(", "ttm_on_declaration", [SYS_README]),
    ("_system/make_score.py", "SC_REFUSE_FILED_BASIS_PIN = ", "make_score.SC_REFUSE_FILED_BASIS_PIN", [SYS_README]),
    # L9 (R8 / R9): every filed PP&E component, capitalized software as capex, ttm.json's release stamp (L9 §6)
    ("_system/dcf_engine.py", '"PaymentsToAcquireMachineryAndEquipment", "PaymentsToAcquireMiningAssets",',
     "PaymentsToAcquireMachineryAndEquipment", [AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", "CAPEX_SUBCLASS_COMPONENTS = ", "PaymentsToAcquireMiningAssets", [AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'CAPEX_SOFTWARE_TAGS = ["PaymentsToDevelopSoftware"', "PaymentsToDevelopSoftware",
     [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", "CapitalizedComputerSoftwareAdditions is NOT read", "CapitalizedComputerSoftwareAdditions",
     [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", "def unlisted_capex_components(", "CAPEX_UNLISTED_COMPONENT",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'UNLISTED_CAPEX_OVERRIDDEN_FLAG = "CAPEX_UNLISTED_COMPONENT_OVERRIDDEN"',
     "CAPEX_UNLISTED_COMPONENT_OVERRIDDEN", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", '(f[0], f[1], "subclass_alone")', "subclass_alone", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", '"in_ppe_total")', "in_ppe_total", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/dcf_engine.py", 'return [f], [], "ppe_duplicate"', "ppe_duplicate", [SYS_README, WORKER_SPEC]),
    ("_system/make_score.py", "def refuse_capex_override_software(", "software_included", [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", "def refuse_unlisted_capex_component(", "capex_unlisted_ack", [SYS_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/make_score.py", "def refuse_pre57_ttm_json(", "ttm_engine_release", [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    ("_system/ttm.py", '"engine_release": _engine.ENGINE_RELEASE', "ttm_inputs.ttm_engine_release",
     [SYS_README, CONTRACT, AGENTS_MD, WORKER_SPEC]),
    # L5 (R5): sweep reliability — preflight, run health, PR protocol and the engine backlog
    ("_system/preflight.py", "def main(", "preflight.py", [SYS_README, AUTO_README, WORKER_SPEC, SECOND_PASS]),
    ("_system/run_health.py", "def main(", "run_health.py", [SYS_README, AUTO_README, WORKER_SPEC, SECOND_PASS]),
    ("_system/pr_worktree.py", "def main(", "pr_worktree.py", [SYS_README, AUTO_README, AGENTS_MD, WORKER_SPEC]),
    ("_system/pr_audit.py", "def main(", "pr_audit.py", [SYS_README, AUTO_README, WORKER_SPEC]),
]


def test_round_keys_are_in_the_code_and_the_documents():
    codes = {}
    gone, unnamed = [], []
    for src, literal, token, docs in PAIRS:
        if literal not in _read(src):
            gone.append(f"{src}: {literal}")
        for d in docs:
            if d not in codes:
                codes[d] = code_text(_read(d))
        unnamed += [f"{d}: {token}" for d in docs if not named(token, codes[d])]
    assert not gone, f"no longer in the code (update the documents and this list): {gone}"
    assert not unnamed, f"not named in the documents: {unnamed}"


def test_code_text_and_named():
    doc = "a `x.y_z` b\n```json\n{\"k\": 1}\n```\nprose ``` fences and `` `code` `` and `--street-only` / `pass2-check`"
    code = code_text(doc)
    assert named("y_z", code) and named("k", code) and named("--street-only", code) and named("pass2-check", code)
    assert not named("prose", code) and not named("street", code) and not named("pass2", code) and not named("y", code)


# ---------------------------------------------------------------- 3
def _front_matter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"---\n(.*?)\n---\n", text, flags=re.S)
    assert m, f"{path}: no front matter"

    def get(key):
        mm = re.search(r"^\s*" + key + r":\s*'?([^'\n]*?)'?\s*$", m.group(1), flags=re.M)
        return mm.group(1) if mm else None
    return {k: get(k) for k in ("id", "enabled", "kind", "every", "time")}


def _expected_when(fm):
    if fm["kind"] == "interval":
        mm = re.fullmatch(r"(\d+)m", fm["every"] or "")
        assert mm, f"{fm['id']}: interval {fm['every']!r} is not in minutes — extend this test"
        return f"every {int(mm.group(1))} min"
    if fm["kind"] == "daily":
        return f"{fm['time'][:5]} daily"
    raise AssertionError(f"{fm['id']}: schedule kind {fm['kind']!r} — extend this test")


def test_automation_day_table_matches_the_cron_files():
    rows = {}
    for line in _read(AUTO_README).splitlines():
        if line.startswith("| ") and "`dcf-" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            job = re.search(r"`(dcf-[\w-]+)`", cells[1])
            if job:
                rows[job.group(1)] = cells
    files = sorted(glob.glob(os.path.join(ROOT, "automation", "crons", "*", "*.md")))
    assert files, "no cron files found"
    for path in files:
        fm = _front_matter(path)
        assert fm["id"] in rows, f"{fm['id']} ({os.path.basename(path)}) has no row in the day table"
        when, what = rows[fm["id"]][0], rows[fm["id"]][2]
        exp = _expected_when(fm)
        assert when.startswith(exp), f"{fm['id']}: table says {when!r}, front matter says {exp!r}"
        disabled = fm["enabled"] == "false"
        assert ("Disabled" in what) == disabled, f"{fm['id']}: enabled {fm['enabled']} but the row reads {what!r}"


# ---------------------------------------------------------------- 4
STALE = [
    # Codex review round 29 of PR #47: a folder with no score.json is no longer repriced; an expense with no USD figure
    # beside usable cash is not gated, so the claim that its run is was wrong
    (CONTRACT, "A folder with no score.json yet is\n  repriced"),
    ("_system/reprice.py", "a folder with no score.json yet is still repriced"),
    ("_system/reprice.py", "A folder with no score.json yet is repriced as before"),
    ("_system/dcf_engine.py", "claimed (its run is gated ACQUIRED_IPRD_UNCONVERTED)"),
    # Codex review round 29 of PR #47, review notes: live_shown checks live_from_earlier_run, live_not_from_this_score
    # and live_older_than_score after the PR #47 reasons, and all three read "Scored figures are the latest — …"; a
    # live.json with no scored.dcf_content_hash is not computed against a score.json that carries one
    (CONTRACT, "Precedence: the three PR #47 reasons are checked first and win over the two date reasons"),
    (CONTRACT, 'only the date reasons are worded "Scored figures are the latest'),
    (CONTRACT, "`scored.dcf_content_hash`, when the live.json records it, not the score's"),
    ("_system/build_site.py", "are checked first and win over main's two date reasons"),
    ("_system/build_site.py", 'only those two carry the "scored figures are the'),
    ("_system/build_site.py", "a live.json written before carries no such"),
    ("_daily/site/app.js", "Those three PR #47 reasons take precedence"),
    # the round-29 polish review: a live.json with no score identity has its own reason (live_without_score_identity),
    # never live_not_from_this_score's "computed before the current score"; four reasons read "Scored figures ..."
    (CONTRACT, "was not computed against it and is withheld the same way"),
    (CONTRACT, "`live_not_from_this_score` and `live_older_than_score` (the score on file is the run's: all"),
    ("_system/build_site.py", "or — written before round 29 — with no"),
    ("_system/build_site.py", "no score identity recorded beside a score.json that carries one)"),
    ("_system/build_site.py", "the app words all three"),
    ("_daily/site/app.js", "or one from before round 29 that records no score identity beside a score that has one) is"),
    ("_daily/site/app.js", "live_not_from_this_score and live_older_than_score, all three worded"),
    ("AGENTS.md", "is not computed against it either"),
    # the round-29 second polish review: the recurrence figure reads the expense side (unknown only when the own
    # expense is), the whole charge adds the cash side, and a parallel expense tag's figure always counts
    (WORKER_SPEC, "the recurrence figure reads the same way"),
    (WORKER_SPEC, "a counted period with no USD figure reads as material"),
    (AGENTS_MD, "a counted period with no USD figure reads as material"),
    (AGENTS_MD, "and any such figure with no USD value makes the materiality unknown"),
    (SYS_README, "(`expense_tags_conflict`, no unit conflict: the current tag is used) is not read"),
    (SYS_README, "now for a USD expense beside cash with no FX rate as well"),
    ("_system/dcf_engine.py", "(expense_tags_conflict, no unit conflict: the current tag is used) is not read here"),
    ("_system/dcf_engine.py", "with no USD figure: its share of the base OE total is unknown"),
    ("_system/make_score.py", "with no USD figure: unknown, read as material"),
    ("_daily/site/app.js", 'only the two date reasons read "Scored figures are the latest"'),
    (SYS_README, "has no `dcf_content_hash` key and is compared on the rest"),
    # engine 5.6 Codex review round 3 of PR #47: the IPR&D charge is ADDED to the price each IRR is solved at
    (CONTRACT, "and from the price each IRR is solved at"),
    ("_daily/site/app.js", "and from the price each IRR is solved at"),
    (SYS_README, "weighted IRR 22.64% → 22.39%, Tier A survives"),
    (AGENTS_MD, "deducted once from every IV and the IRR price"),
    ("README.md", "intrinsic value and the IRR price — never from the base"),
    # engine 5.6 fixer review round: provenance (no scratch-brief labels, no "settled" credit for main-agent fills)
    # and the iprd_amortized shape / declared_pin definitions
    (SYS_README, "**No cliff (F4):**"),
    (SYS_README, "**Treatment (settled):**"),
    (SYS_README, "`figures` = this run's three FY charges"),
    (SYS_README, "equal to a declared `base_override` (no `basis`) and not ttm.json's figure"),
    (SYS_README, "a base_override's `kind` and payable shape (`basis`, `figures`, `shares`)"),
    ("_system/make_score.py", "base_override without `basis` (within 0.1%)"),
    (AGENTS_MD, "- Engine 5.6 (Andrew, 2026-10-19): an impairment"),
    (WORKER_SPEC, "**Acquired IPR&D (engine 5.6, Andrew 2026-10-19).**"),
    (WORKER_SPEC, "**Amortized acquired IPR&D (engine 5.6, Andrew 2026-10-19).**"),
    # engine 5.6 (2026-10-19): the stale-release gate text names the current release, not a pinned 5.5.0
    (SYS_README, '"engine output predates release 5.5.0 — re-run the engine before an entry / exit alert"'),
    (WORKER_SPEC, "predates release 5.5.0 — re-run the engine"),
    (AGENTS_MD, "(\"engine output predates release 5.5.0 —"),
    (CONTRACT, "still reads `stats.last` / `stats.last_date` only"),
    (CONTRACT, "GitHub Pages at\n   `_daily/site/`"),
    (CONTRACT, "is still not emitted"),
    (CONTRACT, "In a fresh site dir that means the index holds only the"),
    (CONTRACT, "upper-cased, sorted, whether or not it is in the universe"),
    (CONTRACT, "`profile.json` `as_of` is younger than `--max-age-days`"),
    (CONTRACT, "reaches further than this capture"),
    (CONTRACT, "Until that lands the site shows"),
    (SYS_README, "ranges 1Y–MAX"),
    (SYS_README, "fcntl-locked"),
    (SYS_README, "every company page opens on a price-vs-value chart"),
    # engine 5.5 verifier round (2026-10-19): the last-filed-unit refusal is not narrowed by the reporting
    # currency (every use of the fallback by a filing override needs currency "USD"), a share_class_mismatch is
    # not "any truthy value", and the live cap is not bit-identical for every run without an ADS ratio
    (SYS_README, "`fx_conversion.from_currency` is not USD"),
    (WORKER_SPEC, "`fx_conversion.from_currency` is not USD"),
    (AGENTS_MD, "`fx_conversion.from_currency` is not USD"),
    (SYS_README, "in judgment.json — any truthy value —"),
    (WORKER_SPEC, "truthy value counts"),
    (CONTRACT, "A run without an ADS ratio gives exactly"),
    (SYS_README, "key_numbers.md prints the net-debt ratio corrected beside the engine's"),
    # engine 5.5 verifier round 2 (2026-10-19): a malformed share_class_mismatch raises no gap (M5), the in-history
    # split count is over all 490 scored folders, M4's estimate exemption is a premise nothing enforces (not a
    # guarantee), and a dei that the latest count fails also makes the leverage diagnostics unverifiable
    ("_system/dcf_engine.py", "a truthy judgment.json share_class_mismatch is DATA_GAP:shares"),
    (SYS_README, "(85 folders record one)"),
    (SYS_README, "it is anchored on the last filed value in that value's own unit, so its unit is the anchor's"),
    (WORKER_SPEC, "is anchored on the last filed value, in that value's own unit"),
    (AGENTS_MD, "anchored on the last filed value, in that value's unit)"),
    ("_system/make_score.py", "anchor's — no ambiguity"),
    (AGENTS_MD, "scale factor and no dei sets"),
    (WORKER_SPEC, "with no cover-page count either, `share_scale.leverage_unverifiable`"),
    # engine 5.5 verifier round 3 (2026-10-19): a dei within 25% of the latest count no longer blocks the pin factor
    # (R3-CAP's window test replaced round 2's early return)
    (WORKER_SPEC, "confirms that count, so no\n   factor is applied"),
    (AGENTS_MD, "within 25% of the latest count means no scale factor at all"),
    (SYS_README, "`scale_factor_for_cap` returns no factor and never consults the pin"),
    ("_system/dcf_engine.py", "the cover-page count confirms it within 25%, so no power-of-ten"),
    ("_system/tests/test_engine_55.py", "R2-CAP a dei within 25% takes no cap factor"),
    # engine 5.5 verifier round 4 (2026-10-19): the cap factor's and the OE/share CAGR's scale tests compare the two
    # counts their rules name (R4-CAP / R4-E2), not every adjacent pair between them
    (SYS_README, "no adjacent pair more than 100× apart"),
    (SYS_README, "leaves the blend only when a break lies between its own two endpoints"),
    ("_system/dcf_engine.py", "share_series_scale_breaks: no adjacent pair"),
    ("_system/dcf_engine.py", "the OE/share CAGR does not span the break"),
    (AGENTS_MD, "when the break lies between its two endpoints"),
    (WORKER_SPEC, "OE/share CAGR when the break"),
    # enrichment fixes verifier round 2 (ruling-sheet Q8 bugs 2-3, 2026-10-19): statements.py's module docstring states
    # pick_money_unit's rule; the Dividends tab reads the legs' unit from the block's own key, never the file's currency;
    # the Forecast tab's OE-history note names the intangible leg when one is deducted
    ("_system/statements.py", "USD preferred on ties"),
    ("_daily/site/app.js", "(typeof fund.currency === 'string' && fund.currency) || 'USD'"),
    ("_daily/site/app.js", "Filed owner\\'s earnings (operating cash flow − capex − stock-based compensation) per diluted share"),
    (CONTRACT, "The block is priced in the file's own `currency`"),
    # engine 5.6 Codex review round 21 of PR #47: the overlap guard is the declared paid_in_intangible_capex
    # presentation (round 8) — the intangible leg's size alone is only a capex_overlap_note; and the registry is
    # written before score.json inside the registry transaction
    ("_system/dcf_engine.py", "an expense-basis amount the period's capex intangible leg already covers"),
    (SYS_README, "the deduction with no cliff, the ≥ 98% overlap guard,"),
    (SYS_README, "the score.json write, the registry replacement and key_numbers.md now run inside"),
    ("_system/make_score.py", "the score.json write, the registry replacement\n    (update_registry, lock_held=True) and key_numbers.md"),
    # ---- engine 5.7 (Andrew's rulings R1-R9, 2026-10-19/20): the wording the rulings retired ----
    # L5 (R5): the daily cron files were renamed without colons, so no checkout misses them
    ("README.md", "names, which NTFS cannot hold"),
    ("README.md", "core.protectNTFS false"),
    (AGENTS_MD, "a filename artifact, not a change"),
    (AGENTS_MD, "under `automation/crons/daily/` showing as deleted in"),
    ("_system/tests/test_docs_contract.py", "files have colons in their names and are absent" + " from a Windows checkout"),
    # L1 (R1): the notch is make_score's mechanical step, so misfit tiers are no longer "soft" judgment calls
    ("automation/crons/daily/dcf-daily-ranking__daily@19-07-00_user_current.md", "their tiers are soft"),
    ("_daily/site/app.js", "their tiers are soft"),
    (WORKER_SPEC, "The one-notch softening (2026-10-15) cannot bridge that gap."),
    (AGENTS_MD, "- Standing policy (Andrew, 2026-10-15): the final tier is sized one notch"),
    (AGENTS_MD, "- A `tier_override` with a quantified written reason (see Sector misfits)."),
    (AGENTS_MD, "REITs keep the 2026-10-15 rule."),
    (WORKER_SPEC, "and any filer without that printed line, keep the 2026-10-15 rule."),
    # L0 / every lane: the 5.7 events are written now
    (SYS_README, "No run writes them yet."),
    # R7 (+ L4): a STALE_FY run takes the TTM unless the worker rejects it with a number (or ttm.py's exit-3 line)
    (WORKER_SPEC, "use the median base and say so"),
    (WORKER_SPEC, "ttm.json TTM base — step 4; the engine refuses the median there), else the median."),
    (AGENTS_MD, "figure when the last FY is stale. Five"),
    ("README.md", "10-Qs when the fiscal year is stale\n- Five"),
    # L2 (R3): every number in analysis.md traces to a generated file or a declared fact
    (WORKER_SPEC, "If a figure you need is not in the computed outputs, say so in words."),
    (WORKER_SPEC, "After it runs, check analysis.md against `key_numbers.md` and fix any figure that"),
    # L3 (R4 revised): the moat is the combined sources + evidence rule, under Andrew's 2026-10-19 rubric
    (AGENTS_MD, "- The moat score needs FOR and AGAINST pillars in `analysis.md` and the"),
    (WORKER_SPEC, "Rubric: 9–10 wide and durable"),
    (SYS_README, "Rubric: 9-10 wide/durable, 7-8 strong"),
    # L3b (M6): the growth hold is the moat's direction (0 / 2 / 3), not a fixed 2 years
    (WORKER_SPEC, "The moat sets the fade: growth holds 2 years, then converges"),
]


def test_depreciation_anchor_clause_present():
    """Andrew's 2026-10-18 clause: a capex estimate may anchor on filed
    depreciation only when no capex was ever filed, the override carries an
    ack_reason, and analysis.md states the anchor. The clause must stand in
    WORKER_SPEC step 8 and in README's bounded-authority summary (the
    2026-10-14 entry, amended in place). Fails on the pre-clause documents —
    the regression test for a prose policy change."""
    spec = _read("_system/WORKER_SPEC.md")
    for phrase in ("Depreciation-anchor exception", "no capex value was ever filed",
                   "must state the anchor explicitly", "ack_reason"):
        assert phrase in spec, f"WORKER_SPEC.md lost the clause phrase: {phrase!r}"
    readme = _read(SYS_README)
    assert "Depreciation anchor for capex estimates (Andrew's decision)" in readme, \
        "README Fixes & lessons lost the depreciation-anchor entry"
    assert "amended 2026-10-18" in readme and "filed depreciation" in readme, \
        "README's bounded-authority summary lost the amendment"


def _flat(rel):
    return " ".join(_read(rel).split())


def test_iprd_amortized_is_rebuilt_on_every_rescore():
    """[engine 5.6 fixer review round] The re-score and second-pass specs say to carry overrides through unchanged,
    but an iprd_amortized base_override is recomputed from the run's own native base, window and share count, so a
    carried one can never reproduce on a new filing: WORKER_SPEC step 2 (re-score after a new filing), step 8 (the
    bounded authority) and SECOND_PASS step 7 must say to rebuild it (or drop it when no longer recurrent). Fails on
    the documents before the round."""
    spec = _flat(WORKER_SPEC)
    for phrase in ("An `iprd_amortized` `base_override` is not carried either: rebuild it from this re-score's "
                   "preliminary run", "or drop it when that run no longer raises `ACQUIRED_IPRD_RECURRENT`",
                   "It is the one override NOT carried through unchanged on a re-score: rebuild it from every "
                   "re-score's preliminary run", "`iprd_cash_flow_check` entries carry over"):
        assert phrase in spec, f"WORKER_SPEC.md lost: {phrase!r}"
    sp = _flat("_system/SECOND_PASS.md")
    for phrase in ("an `iprd_amortized` `base_override` (engine 5.6) is rebuilt from that rerun's dcf_numbers.json",
                   "passes `--base-oe-ps <the new value>` instead of `--ttm`"):
        assert phrase in sp, f"SECOND_PASS.md lost: {phrase!r}"


def test_halo_iprd_example_names_the_price_of_each_irr():
    """[Codex review r3 of PR #47, #4322176055] README's engine 5.6 HALO example quoted the weighted IRR 22.64% →
    22.39% "at its scored price", but the committed re-score is at $122.50 (HALO/dcf_numbers.json: 22.57% → 22.32%);
    the 22.64 / 22.39 pair is the 5.5.0 record's $121.84. The example states both pairs with their prices, and the
    committed pair is read from HALO/dcf_numbers.json so a later re-score that moves it fails here."""
    import json
    with open(os.path.join(ROOT, "HALO", "dcf_numbers.json"), encoding="utf-8") as f:
        n = json.load(f)
    before = n["iprd_adjustment"]["before"]["weighted"]["irr"] * 100
    after = n["implied_irr_weighted"] * 100
    readme = _read(SYS_README)
    committed = f"weighted IRR {before:.2f}% → {after:.2f}% at the re-score's ${n['price']:.2f}"
    assert committed in readme, f"README's HALO example lost the committed pair: {committed!r}"
    assert "weighted IRR 22.64% → 22.39% at the 5.5.0 record's $121.84" in readme, "README lost the $121.84 pair's price"


def _live_shown_reasons():
    """record.live_withheld's reasons in the order build_site.live_shown checks them, read from its code (a dict's
    "reason" value: a string, or `a if cond else b`)."""
    src = _read("_system/build_site.py")
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "live_shown")
    found = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Dict):
            continue
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and k.value == "reason":
                vals = [v.body, v.orelse] if isinstance(v, ast.IfExp) else [v]
                found.extend((x.lineno, x.col_offset, x.value) for x in vals
                             if isinstance(x, ast.Constant) and isinstance(x.value, str))
    return [r for _, _, r in sorted(found)], ast.get_docstring(tree) or "", ast.get_docstring(fn) or ""


def _names_in_order(text, anchor, names, span=1600):
    """The first occurrence of each of `names` after `anchor` in `text` (within `span` characters), in that order."""
    i = text.find(anchor)
    assert i >= 0, f"anchor {anchor!r} is gone"
    win = text[i:i + span]
    pos = [win.find(n) for n in names]
    return [n for n, p in zip(names, pos) if p < 0], pos == sorted(pos)


def test_live_withheld_reasons_are_documented_in_the_order_live_shown_checks_them():
    """[Codex review r29 of PR #47, review notes] Round 29 checked live_not_from_this_score after
    live_from_earlier_run and before live_older_than_score, and worded it like the date reasons ("Scored figures are
    the latest — …"), but SITE_CONTRACT.md, live_shown's docstring and app.js's header comment still said the three
    PR #47 reasons are checked first and only the two date reasons carry that wording, and build_site's module
    docstring did not list the new reason. Every reason live_shown sets is named in build_site's module docstring
    and in live_shown's own, and the three precedence passages name all of them in the order the code checks them —
    since the round's polish review live_without_score_identity too, right after live_not_from_this_score."""
    reasons, module_doc, fn_doc = _live_shown_reasons()
    assert reasons == ["iprd_unresolved", "iprd_share_count_unverified", "score_not_from_this_run",
                       "live_from_earlier_run", "live_not_from_this_score", "live_without_score_identity",
                       "live_older_than_score"], reasons
    for where, doc in (("build_site module docstring", module_doc), ("live_shown docstring", fn_doc)):
        missing = [r for r in reasons if r not in doc]
        assert not missing, f"{where} does not name {missing}"
    for rel, text, anchor in ((CONTRACT, _flat(CONTRACT), "[Merge of main #83 into PR #47] Precedence:"),
                              ("_system/build_site.py", " ".join(fn_doc.split()), "[merge of main #83 into PR #47] Precedence:"),
                              ("_daily/site/app.js", _flat("_daily/site/app.js"), "[merge of main #83] Precedence:")):
        missing, ordered = _names_in_order(text, anchor, reasons)
        assert not missing and ordered, f"{rel}'s precedence passage: missing {missing}, in order {ordered}"
        # ...and the two wordings: score_not_from_this_run's last, then the three that read "Scored figures ..."
        missing, ordered = _names_in_order(text, anchor, ["score_not_from_this_run", "Live figures withheld",
                                                          "live_from_earlier_run", "Scored figures are the latest"])
        assert not missing and ordered, f"{rel}'s precedence passage wording: missing {missing}, in order {ordered}"


def test_the_recurrence_figure_is_documented_on_the_expense_side():
    """[Codex review r29 of PR #47, second polish review] WORKER_SPEC said a year's whole charge is the largest of its
    expense and cash figures in every unit filed and "the recurrence figure reads the same way", but the recurrence
    figure reads the expense side (EUR 100M at 1.08 on the cash tag beside the USD 40M expensed and paid: $40M, the
    whole charge $108M) and is unknown only when the own expense is; and a parallel expense tag's figure counts
    whether or not that tag carries a unit conflict. WORKER_SPEC, AGENTS.md and README's round-29 entry say so."""
    spec = _flat(WORKER_SPEC)
    for phrase in ("The recurrence figure reads the expense side only", "the whole charge adds the cash side",
                   "on any of its acquired-IPR&D expense tags (the detector tag and the parallel one)",
                   "is unknown (read as material) only when the own expense has no USD figure",
                   "a USD expense beside cash with no FX rate reads that expense"):
        assert phrase in spec, f"WORKER_SPEC.md lost: {phrase!r}"
    agents = _flat(AGENTS_MD)
    for phrase in ("the recurrence figure reads the expense side", "the whole charge adds the cash side",
                   "whose acquired-IPR&D expense has no USD figure reads as material"):
        assert phrase in agents, f"AGENTS.md lost: {phrase!r}"
    readme = _flat(SYS_README)
    for phrase in ("**Round-29 second polish review", "the recurrence figure reads the expense side",
                   "the whole charge adds the cash side", "`expense_tags_conflict` figures too"):
        assert phrase in readme, f"README.md lost: {phrase!r}"


R30_TOLERANCE_PHRASES = ("unit-agreement tolerance", "`IPRD_UNIT_TOLERANCE`", "max($1, 1% of the larger)",
                         "a unit within it is the figure used")


def test_every_unit_filed_reads_the_units_that_disagree_beyond_the_unit_agreement_tolerance():
    """[Codex review r30 of PR #47, #4336863087 — behaviour unchanged] The round-29 rule says a year's own expense and
    whole charge are its largest figures "in every unit filed", but a unit that agrees with the figure used within the
    engine's unit-agreement tolerance (IPRD_UNIT_TOLERANCE, 0.01: units disagree only when, after conversion, they
    differ by more than max($1, 1% of the larger)) records no unit_conflict and is that same figure — so USD 100M beside
    EUR converting to $100.7M is a $100M charge. WORKER_SPEC, AGENTS.md, README (its round-29 entry and the round-30
    entry) and the three helpers' docstrings name the tolerance and its value and say a unit within it is the figure
    used."""
    for rel in (WORKER_SPEC, AGENTS_MD, SYS_README):
        text = _flat(rel)
        missing = [p for p in R30_TOLERANCE_PHRASES if p not in text]
        assert not missing, f"{rel} does not say which units 'every unit filed' reads: missing {missing}"
    readme = _flat(SYS_README)
    r29 = readme.find("**Round-29 second polish review")
    r30 = readme.find("**Codex review round 30 of PR #47")
    assert 0 <= r29 < r30, "README's round-30 entry must follow the round-29 second polish review"
    assert "a unit within it is the figure used" in readme[r29:r30], "README's round-29 entry does not name the tolerance"
    assert "a unit within it is the figure used" in readme[r30:], "README's round-30 entry does not name the tolerance"
    tree = _module("_system/dcf_engine.py")
    for fn in ("iprd_own_charge_usd", "iprd_own_expense_unknown", "iprd_whole_charge_unknown"):
        doc = " ".join((ast.get_docstring(_function(tree, fn)) or "").split())
        missing = [p for p in ("IPRD_UNIT_TOLERANCE", "max($1, 1% of the larger)", "a unit within it is the figure used")
                   if p not in doc]
        assert not missing, f"dcf_engine.{fn}'s docstring: missing {missing}"


R30_SPREAD_PHRASE = "the tolerance applies to their spread"


def test_the_unit_agreement_tolerance_is_documented_as_a_spread_across_every_unit():
    """[Codex review r30 of PR #47, review of the round's doc fix] The round-30 wording ("a unit within it is the figure
    used") read pairwise; the engine tests the spread across every unit filed (_iprd_pick). WORKER_SPEC, AGENTS.md,
    README and the three helpers' docstrings say so."""
    for rel in (WORKER_SPEC, AGENTS_MD, SYS_README):
        assert R30_SPREAD_PHRASE in _flat(rel), f"{rel} does not say the tolerance applies to the units' spread"
    tree = _module("_system/dcf_engine.py")
    for fn in ("iprd_own_charge_usd", "iprd_own_expense_unknown", "iprd_whole_charge_unknown"):
        doc = " ".join((ast.get_docstring(_function(tree, fn)) or "").split())
        assert R30_SPREAD_PHRASE in doc, f"dcf_engine.{fn}'s docstring does not say the tolerance applies to the spread"


def test_a_ttm_base_without_ttm_shares_is_documented_as_refused():
    """[Codex review r30 of PR #47, #4336863102] A TTM base's acquired-IPR&D figures are per share on ttm.json's
    ttm_shares_diluted; without a positive one the run is refused (BAD_TTM_SHARES), never put on the latest-FY count.
    WORKER_SPEC, AGENTS.md and README say so."""
    for rel in (WORKER_SPEC, AGENTS_MD, SYS_README):
        text = _flat(rel)
        missing = [p for p in ("`BAD_TTM_SHARES`", "never the latest-FY count") if p not in text]
        assert not missing, f"{rel}: missing {missing}"


# ---------------------------------------------------------------- 5 (engine 5.7)
def _between(text, start, end):
    """text from `start` up to (not including) the next `end` after it."""
    i = text.find(start)
    assert i >= 0, f"anchor {start!r} is gone"
    j = text.find(end, i + len(start))
    return text[i:j if j >= 0 else len(text)]


def _md_section(rel, heading):
    """One '## <heading>' section of a markdown document, up to the next '## ' heading (raw text)."""
    text = _read(rel)
    i = text.find("\n## " + heading)
    assert i >= 0, f"{rel}: section {heading!r} is gone"
    j = text.find("\n## ", i + 1)
    return text[i:j if j >= 0 else len(text)]


def _consts(rel):
    """A code file's module-level `NAME = <literal>` constants, read with ast (never imported). A dict value that is a
    module constant's name is resolved against the constants read before it."""
    out = {}
    for node in _module(rel).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        v = node.value
        try:
            out[node.targets[0].id] = ast.literal_eval(v)
        except ValueError:
            if isinstance(v, ast.Dict) and all(isinstance(k, ast.Constant) for k in v.keys):
                vals = [x.value if isinstance(x, ast.Constant) else out.get(x.id) if isinstance(x, ast.Name) else None
                        for x in v.values]
                out[node.targets[0].id] = {k.value: x for k, x in zip(v.keys, vals)}
    return out


# (code file, a literal that must still be in it, a phrase the documents say in prose, the documents) — for rules the
# documents state in words rather than by a code name
PHRASES_57 = [
    ("_system/make_score.py", '"## Interim bridge (declared 6-K TTM — the scored base)"', '"Interim bridge"',
     [AGENTS_MD, WORKER_SPEC]),
    ("_system/interim_bridge.py", "PERIOD_SOURCE_DEI = \"the 6-K's XBRL dei DocumentPeriodEndDate\"",
     "XBRL 6-K's dei DocumentPeriodEndDate", [SYS_README]),
    ("_system/interim_bridge.py", "def report_period_end(", "a non-XBRL 6-K's reportDate is its cover date", [WORKER_SPEC]),
    ("_system/dcf_engine.py", "def _own_module(", "imports its siblings through its own folder", [SYS_README]),
    ("_system/check_quotes.py", 'f"analysis.md fails the quote check', "analysis.md fails the quote check",
     [WORKER_SPEC, SECOND_PASS]),
    ("_system/queue.py", "restore it from git and run the command again", "restore it from git", [SYS_README, SECOND_PASS]),
    ("_system/queue.py", "is malformed ({why})", "is malformed", [SYS_README, SECOND_PASS]),
]


def test_engine_57_rules_stated_in_prose_match_the_code():
    gone, missing = [], []
    for src, literal, phrase, docs in PHRASES_57:
        if literal not in _read(src):
            gone.append(f"{src}: {literal}")
        missing += [f"{d}: {phrase!r}" for d in docs if phrase not in _flat(d)]
    assert not gone, f"no longer in the code (update the documents and this list): {gone}"
    assert not missing, f"not stated in the documents: {missing}"


def test_docs_name_the_notch():
    """[engine 5.7, L1 / R1 — 01 T-16] AGENTS.md "Sector misfits" says make_score applies the notch (it is
    mechanical, never graded) and names misfit_notch_reason; WORKER_SPEC names the SIC rule ("universe sector OR the
    EDGAR SIC") and misfit_notch_reason; _system/README.md names misfit_notch and misfit_sector_set_aside."""
    sec = _md_section(AGENTS_MD, "Sector misfits")
    flat, code = " ".join(sec.split()), code_text(sec)
    for phrase in ("**The notch is mechanical**", "make_score publishes every sector misfit one tier below its numbers tier",
                   "Never grade the notch"):
        assert phrase in flat, f"AGENTS.md Sector misfits lost: {phrase!r}"
    for tok in ("misfit_notch_reason", "misfit_notch", "dcf_engine.SIC_SETS_ASIDE_SECTOR", "misfit_sector_set_aside"):
        assert named(tok, code), f"AGENTS.md Sector misfits does not name `{tok}`"
    spec = _flat(WORKER_SPEC)
    assert "the universe sector OR the EDGAR SIC" in spec, "WORKER_SPEC lost the SIC rule"
    assert named("misfit_notch_reason", code_text(_read(WORKER_SPEC))), "WORKER_SPEC does not name misfit_notch_reason"
    readme = code_text(_read(SYS_README))
    assert named("misfit_notch", readme) and named("misfit_sector_set_aside", readme)


def test_the_quote_gate_is_documented():
    """[engine 5.7, L2 / R3 — 02 §10] _system/README.md names the declared-facts file, the checker, its --save-run
    copy and the score keys that prove key_numbers.md was not hand-edited; WORKER_SPEC says queue.py done runs the
    checker; SECOND_PASS says pass2-done does (and pass2-reset never). The retired "say so in words" sentence is in
    STALE."""
    readme = code_text(_read(SYS_README))
    for tok in ("facts.json", "check_quotes.py", "--save-run", "declared_facts", "key_numbers_sha256",
                "dcf_numbers_<label>.json"):
        assert named(tok, readme), f"_system/README.md does not name `{tok}`"
    spec = _flat(WORKER_SPEC)
    for phrase in ("Since engine 5.7 `queue.py done` runs `check_quotes.py`",
                   "`queue.py done` refuses an engine 5.7 run whose analysis.md fails check_quotes.py",
                   "never edit key_numbers.md", "judgment.json is never a source"):
        assert phrase in spec, f"WORKER_SPEC lost: {phrase!r}"
    sp = _flat(SECOND_PASS)
    for phrase in ("**`pass2-done` refused by the quote check**", "`pass2-reset` is never gated"):
        assert phrase in sp, f"SECOND_PASS lost: {phrase!r}"


def test_the_snippet_limit_is_the_codes_one_constant():
    """[engine 5.7, L2 / L4 — 07 §1.7] A declared fact's snippet (and a 6-K bridge leg's) is at most
    quote_tokens.SNIPPET_MAX_WORDS words — one constant everywhere. The lane notes said "under 25 words" and the code
    says 24: every word limit the documents state is the constant."""
    n = _consts("_system/quote_tokens.py")["SNIPPET_MAX_WORDS"]
    for rel in (AGENTS_MD, WORKER_SPEC, SYS_README):
        text = _flat(rel)
        stated = re.findall(r"\bat most (\d+) words\b", text)
        assert stated, f"{rel} does not state the snippet limit"
        assert all(int(s) == n for s in stated), f"{rel} states {stated}, the code {n}"
        assert not re.search(r"\bunder \d+ words\b", text), f"{rel} states an 'under N words' limit"


def _rubric_bands(text, sep):
    """[(lo, hi, band text)] of a 'lo–hi words' / 'n words' rubric, the bands separated by `sep`."""
    out = []
    for band in re.split(sep, text.strip()):
        m = re.match(r"(\d+)(?:–(\d+))?\s", band.strip())
        assert m, f"rubric band without a range: {band!r}"
        out.append((int(m.group(1)), int(m.group(2) or m.group(1)), band))
    return out


def _check_rubric(rel, bands, caps):
    no_src, one_narrow, wide_two, two_wide = caps
    his = [hi for lo, hi, b in bands if "no source" in b]
    assert his and max(his) == no_src, f"{rel}: the 'no source' bands end at {his}, the cap is {no_src}"
    assert all(hi <= one_narrow for lo, hi, b in bands if "one narrow source" in b), \
        f"{rel}: 'one narrow source' above ONE_NARROW_CAP {one_narrow}"
    by_lo = {lo: b for lo, hi, b in bands}
    assert "a wide source or two fact-backed sources" in by_lo.get(wide_two, ""), f"{rel}: the {wide_two}+ band"
    assert "two wide sources" in by_lo.get(two_wide, ""), f"{rel}: the {two_wide}+ band"
    assert [lo for lo, hi, b in bands] == sorted(lo for lo, hi, b in bands) and bands[-1][1] == 10, f"{rel}: bands"


def test_moat_rubric_matches_the_caps():
    """[engine 5.7, L3 — 03b test 31] WORKER_SPEC step 5's rubric and README §Moat's copy put "no source" only in
    bands ending at moat_scorecard.NO_SOURCE_CAP (3), "one narrow source" only at or below ONE_NARROW_CAP (6), "a wide
    source or two fact-backed sources" at WIDE_OR_TWO_MIN (7) and "two wide sources" at TWO_WIDE_MIN (9); both caps
    sentences carry the constants; and the rubric medians WORKER_SPEC quotes are README's measured ones."""
    c = _consts("_system/moat_scorecard.py")
    caps = (c["NO_SOURCE_CAP"], c["ONE_NARROW_CAP"], c["WIDE_OR_TWO_MIN"], c["TWO_WIDE_MIN"])
    spec = _flat(WORKER_SPEC)
    rub = _between(spec, "**Rubric (Andrew, 2026-10-19 — use the whole range).**", " Today's scores")
    _check_rubric(WORKER_SPEC, _rubric_bands(rub.split("**", 2)[2], r"(?<=\.)\s+(?=\d)"), caps)
    assert (f"The caps: none ≤ {caps[0]}; one narrow ≤ {caps[1]}; {caps[2]}+ a wide or two fact-backed sources; "
            f"{caps[3]}+ two wide") in spec, "WORKER_SPEC step 5's caps sentence"
    readme = _flat(SYS_README)
    rub = _between(readme, "Rubric (WORKER_SPEC step 5 — use the whole range): ", " - Sources (type")
    _check_rubric(SYS_README, _rubric_bands(rub.split(": ", 1)[1].rstrip("."), r";\s+"), caps)
    assert (f"Caps: none → {caps[0]}, one narrow → {caps[1]}, {caps[2]}+ a wide source or two fact-backed sources, "
            f"{caps[3]}+ two wide") in readme, "README §Moat's caps sentence"
    m = re.search(r"Rubric medians \(governing return\) at moat ([\d/]+): ([\d. /]+)%", readme)
    assert m, "README lost the measured rubric medians"
    med = dict(zip((int(x) for x in m.group(1).split("/")), (x.strip() for x in m.group(2).split("/"))))
    q = re.search(r"median governing return at moat 6 is ([\d.]+)% and at moat 7 is ([\d.]+)% .*?\(moat 4 / 5: ([\d.]+)% / "
                  r"([\d.]+)%", spec)
    assert q, "WORKER_SPEC lost the rubric medians"
    assert (med[6], med[7], med[4], med[5]) == q.groups(), f"README medians {med} vs WORKER_SPEC {q.groups()}"


def test_moat_scorecard_enums_are_documented():
    """[engine 5.7, L3] WORKER_SPEC step 5 gives the scorecard version and lists every business type
    moat_scorecard.evaluate accepts; README §Moat names the pillars an event fact may stand alone on
    (POINT_OK_PILLARS)."""
    c = _consts("_system/moat_scorecard.py")
    step5 = _between(_flat(WORKER_SPEC), "5. **Moat 0–10", "6. **Five scenarios**")
    assert f"`{{version: {c['SCORECARD_VERSION']}, business_type," in step5, "WORKER_SPEC step 5: the scorecard version"
    missing = [t for t in c["BUSINESS_TYPES"] if t not in step5]
    assert not missing, f"WORKER_SPEC step 5 does not list the business types {missing}"
    readme = _flat(SYS_README)
    point = _between(readme, "`event` facts (points, not series) may stand alone only on", ".")
    missing = sorted(p for p in c["POINT_OK_PILLARS"] if p not in point)
    assert not missing, f"README §Moat's event-fact sentence does not name {missing}"
    w = c["WEIGHTS"]
    head = f"Core pillars ({len(w)}, weight {sum(w.values()):g}): "
    stated = dict(re.findall(r"\b([a-z_]+) (\d+(?:\.\d+)?)\b", _between(readme, head, ". Supporting factors")[len(head):]))
    assert {k: float(v) for k, v in stated.items()} == w, f"README §Moat's pillar weights {stated} vs the code's {w}"


def test_the_moat_trend_holds_and_exit_are_documented():
    """[engine 5.7, L3b / M6 — 10 T26] WORKER_SPEC step 5 gives the three holds of dcf_engine.HOLD_BY_TREND and the
    --moat-trend flag; step 2 names BAD_MOAT_TREND with EXIT_BAD_MOAT_TREND; README says the same; every documented
    final-run command, README's "Workflow per company" line and the engine's Usage line pass --moat-trend."""
    c = _consts("_system/dcf_engine.py")
    hold, code = c["HOLD_BY_TREND"], c["EXIT_BAD_MOAT_TREND"]
    assert set(hold) == set(c["MOAT_TRENDS"]), hold
    spec = _flat(WORKER_SPEC)
    step5 = _between(spec, "5. **Moat 0–10", "6. **Five scenarios**")
    for phrase in (f"eroding → hold {hold['eroding']}", f"widening → hold {hold['widening']}",
                   f"anything else → hold {hold['stable']}", "`--moat-trend`"):
        assert phrase in step5, f"WORKER_SPEC step 5 lost: {phrase!r}"
    assert f"**Exit {code} `BAD_MOAT_TREND`" in spec, "WORKER_SPEC step 2: the BAD_MOAT_TREND exit"
    readme = _flat(SYS_README)
    assert (f"`--moat-trend eroding` {hold['eroding']} years, `stable` {hold['stable']} (the v4 hold), "
            f"`widening` {hold['widening']}") in readme, "README: the three holds"
    assert f"exits {code} (BAD_MOAT_TREND)" in readme, "README: the BAD_MOAT_TREND exit"
    assert "--moat-trend" in _between(readme, "- Workflow per company:", " ## "), "README's workflow line"
    for rel in (WORKER_SPEC, SECOND_PASS):
        cmds = [s for s in code_text(_read(rel)).split("\n") if "dcf_engine.py <T> --moat " in s]
        assert cmds and all("--moat-trend" in s for s in cmds), f"{rel}: a final-run command without --moat-trend"
    assert "[--moat-trend eroding|stable|widening]" in (ast.get_docstring(_module("_system/dcf_engine.py")) or "")


def test_share_classes_are_documented():
    """[engine 5.7, L8 / R6 — 08 docs tests] AGENTS.md's arithmetic check 1 recomputes a declared run on total units
    (`+SHARE_CLASSES` rows); WORKER_SPEC step 4 / 8 carry the declaration's shape; README's Fixes & lessons has the
    dated R6 entry."""
    arith = _md_section(AGENTS_MD, "Arithmetic you can redo from the diff")
    assert named("+SHARE_CLASSES", code_text(arith)) and named("share_classes", code_text(arith)), \
        "AGENTS.md check 1 does not recompute a share_classes run on total units"
    spec = code_text(_read(WORKER_SPEC))
    missing = [t for t in ("share_classes", "SHARE_CLASSES_DECLARED", "UP_C_SUSPECT", "SHARE_CLASSES_CAP_GAP",
                           "SHARE_CLASSES_NCI_GAP", "up_c_suspect_reason", "BAD_SHARE_CLASSES", "BAD_TTM_SHARE_BASIS",
                           "share_basis", "in_filed_count") if not named(t, spec)]
    assert not missing, f"WORKER_SPEC does not name {missing}"
    assert re.search(r"^- \*\*2026-10-21 — Engine 5\.7: declared share classes .*\bR6\b", _read(SYS_README), flags=re.M), \
        "README Fixes & lessons lost the dated R6 entry"


def test_the_capex_rules_are_documented():
    """[engine 5.7, L9 / R8-R9 — L9 §6] WORKER_SPEC's STALE_FY paragraph says ttm.json records the engine_release
    that built it and the run copies it to ttm_inputs.ttm_engine_release; AGENTS.md's capex check names the R8 / R9
    tags and records (the code pairs are in PAIRS)."""
    stale = _between(_read(WORKER_SPEC), "Recurring ones — `STALE_FY`", "**Rejecting the TTM (R7).**")
    code = code_text(stale)
    assert named("engine_release", code) and named("ttm_inputs.ttm_engine_release", code), \
        "WORKER_SPEC's STALE_FY paragraph lost ttm.json's engine_release stamp"
    agents = code_text(_read(AGENTS_MD))
    missing = [t for t in ("PaymentsToAcquireMachineryAndEquipment", "PaymentsToAcquireMiningAssets",
                           "PaymentsToDevelopSoftware", "CapitalizedComputerSoftwareAdditions",
                           "CAPEX_UNLISTED_COMPONENT_OVERRIDDEN", "subclass_alone") if not named(t, agents)]
    assert not missing, f"AGENTS.md does not name {missing}"


def test_specs_run_preflight_before_claiming():
    """[engine 5.7, L5 / R5 — 05 §9] WORKER_SPEC step 1 runs preflight.py before `queue.py claim`; SECOND_PASS step 1
    runs it before pass2-claim."""
    for rel, claim in ((WORKER_SPEC, "queue.py claim"), (SECOND_PASS, "pass2-claim")):
        step1 = _between(_read(rel), "1. **Preflight, then claim.**", "\n2. **")
        p, q = step1.find("preflight.py"), step1.find(claim)
        assert 0 <= p < q, f"{rel} step 1: preflight.py at {p}, {claim} at {q}"


def test_every_cron_body_records_run_health():
    """[engine 5.7, L5 / R5 — 05 §9] Every cron body starts and records its run in run_health.py under its own id."""
    files = sorted(glob.glob(os.path.join(ROOT, "automation", "crons", "*", "*.md")))
    assert files, "no cron files found"
    for path in files:
        fm = _front_matter(path)
        with open(path, encoding="utf-8") as f:
            body = re.sub(r"\A---\n.*?\n---\n", "", f.read(), flags=re.S)
        for verb in ("start", "record"):
            assert f"run_health.py {verb} {fm['id']}" in body, f"{os.path.basename(path)}: no `run_health.py {verb} {fm['id']}`"


def test_lane_default_switches_exist_in_the_code():
    """[engine 5.7] README's lane-defaults table (Q1-Q18, the main agent's defaults pending Andrew's ratification)
    names the one switch that flips each default. Every `module.NAME` switch it names is a module-level assignment
    in _system/<module>.py, so a renamed or removed switch fails here before the table misleads a ratification."""
    rows = {}
    for line in _read(SYS_README).splitlines():
        m = re.match(r"\s*\| (Q\d+) \|(.*)\|\s*$", line)
        if m:
            rows[m.group(1)] = m.group(2).split("|")[-1]
    assert list(rows) == [f"Q{i}" for i in range(1, 19)], f"README's lane-defaults table rows: {list(rows)}"
    named_switches = 0
    for q, cell in rows.items():
        for mod, name in re.findall(r"`(\w+)\.([A-Z][A-Z0-9_]+)`", cell):
            src = _read(f"_system/{mod}.py")
            assert re.search(rf"^{name}\s*=", src, flags=re.M), f"{q}: `{mod}.{name}` is not assigned in _system/{mod}.py"
            named_switches += 1
    assert named_switches >= 12, named_switches


def test_agents_md_has_the_backlog_exception():
    """[engine 5.7, L5 / R5 — 05 §9] AGENTS.md "What is in a PR" lets a company data PR append to
    _system/ENGINE_BACKLOG.md (and only append)."""
    sec = _md_section(AGENTS_MD, "What is in a PR")
    assert named("_system/ENGINE_BACKLOG.md", code_text(sec)), "AGENTS.md What is in a PR does not name the backlog"
    flat = " ".join(sec.split())
    assert "**The backlog exception (Andrew, 2026-10-19, R5).**" in flat and "may only append" in flat, \
        "AGENTS.md lost the backlog exception"


def test_corrected_passages_stay_corrected():
    found = [f"{doc}: {phrase!r}" for doc, phrase in STALE if phrase in _read(doc)]
    assert not found, f"stale wording is back: {found}"


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:
                fails += 1; print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
