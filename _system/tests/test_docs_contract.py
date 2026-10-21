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
   and the row says "Disabled" exactly when `enabled: false`. (The daily cron
   files have colons in their names and are absent from a Windows checkout;
   the rows of the files that are present are checked.)
4. The passages this round corrected stay corrected (the stale wording is
   absent) — also engine 5.5's verifier-round corrections in README,
   SITE_CONTRACT, WORKER_SPEC and AGENTS.md.
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
]


def test_round_keys_are_in_the_code_and_the_documents():
    codes = {d: code_text(_read(d)) for d in (CONTRACT, SYS_README, AUTO_README)}
    gone, unnamed = [], []
    for src, literal, token, docs in PAIRS:
        if literal not in _read(src):
            gone.append(f"{src}: {literal}")
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
