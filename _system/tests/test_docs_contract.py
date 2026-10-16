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
   entry and exit alert gates, queue.py pass2-check.
3. automation/README.md's day table matches every cron file present: the
   "When" cell carries the front matter's cadence (every N min / HH:MM daily)
   and the row says "Disabled" exactly when `enabled: false`. (The daily cron
   files have colons in their names and are absent from a Windows checkout;
   the rows of the files that are present are checked.)
4. The passages this round corrected stay corrected (the stale wording is
   absent).
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
    ("_system/reprice.py", '"score_note"', "score_note", [CONTRACT]),
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
    ("_system/queue.py", '"pass2-check"', "pass2-check", [SYS_README, AUTO_README]),
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
]


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
