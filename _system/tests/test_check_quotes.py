#!/usr/bin/env python3
"""check_quotes.py and the quote_tokens tokenizer (engine 5.7; Andrew's ruling R3 of 2026-10-19 — strict quoting;
design 02 §6 / §10 tests 1-8, L2 rebase A5, A7, A11, A12, A16, A19).
Run: python _system/tests/test_check_quotes.py (or python -m pytest _system/tests). Offline; the committed folders
(APP, GMED, VOD, RNR, MICC, HALO) are read only; every write goes to a temp STOCKS_BASE.

Each test fails on the code before the lane (e22e814: no check_quotes module, a quote_tokens skeleton without a
tokenizer):
1. the tokenizer: units, scales, ranges, slash lists, arithmetic chains, signs, currencies;
2. the ignore rules: dates, years, references, versions, forms, identifiers, accounting-standard references (A12:
   HALO's "ASC 805-50"), index names, small counts; method constants only in their context and only when unmatched;
3. the tolerance at the quoted precision (approximate tokens twice it; signs ignored);
4. worker text is never a source (the curly-quoted echo, the pre-5.7 echo patterns, facts.json labels / snippets);
5. every engine figure printed in a committed key_numbers.md re-quoted the way analysts write it traces (A16: HALO
   too — the IPR&D section's figures);
6. the CLI's exit codes (gated pass / fail, legacy, --strict, unreadable folder, I2 hand-edited key_numbers.md);
7. --all gates only 5.7 runs;
8. --save-run copies verified engine output only.
Review fixes (2026-10-21), each failing on the lane's first build (cc121e2):
r01 judgment.json probs_used / moat_score are never a source (judgment.json is not bound to the score);
r01 / r02 worker text the engine copies into its record and echoes into flag strings (ads_ratio.source) is blanked
   by the record's own copy, at any length, whatever judgment.json says after make_score;
r03 a convention or reference word ("first", "next", "past", "notes", "Tier 1") never swallows a research number;
r07 I4 binds a saved run to score.json method_runs by content_hash, not by label alone;
r08 the refusal says "1 number traces".
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
for _p in (HERE, SYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import quote_tokens as Q  # noqa: E402
import check_quotes as CQ  # noqa: E402
from test_make_score_55 import Run, _numbers, _judgment, _stamp, T  # noqa: E402

CHECK = os.path.join(SYS, "check_quotes.py")


def _toks(text):
    return [(k.kind, round(k.val if k.kind in ("money", "plain", "mult") else k.v, 6)) for k in Q.numbers(text)]


def _cli(base, *args):
    env = dict(os.environ, STOCKS_BASE=base, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, CHECK, *args], capture_output=True, text=True, encoding="utf-8", env=env,
                       timeout=120)
    return r.returncode, r.stdout + r.stderr


# ---------------------------------------------------------------- 1. tokenizer
def test_tokenizer_units_scales_ranges():
    """02 §6.3: kinds and values as written; ranges inherit right to left; slash lists; arithmetic chains."""
    assert _toks("$1.52B") == [("money", 1.52e9)]
    assert Q.tolerance(Q.numbers("$1.52B")[0]) == 5e6
    assert _toks("1,520") == [("plain", 1520.0)] and _toks("11.70%") == [("pct", 11.7)]
    assert _toks("2.5x and 6.05×") == [("mult", 2.5), ("mult", 6.05)]
    assert _toks("$3.18–3.22B") == [("money", 3.18e9), ("money", 3.22e9)]
    assert _toks("−$518,826,000") == [("money", 518826000.0)]
    assert _toks("$5.09/share") == [("money", 5.09)]
    assert _toks("40–60bps") == [("bps", 40.0), ("bps", 60.0)]
    assert _toks("−0.29 / −0.05pp") == [("pp", 0.29), ("pp", 0.05)]
    assert _toks("EUR 2,799M") == [("money", 2.799e9)] and _toks("R$1,746,480,000") == [("money", 1746480000.0)]
    assert _toks("$1,075.6 − $282.6 = $801.9M") == [("money", 1.0756e9), ("money", 2.826e8), ("money", 8.019e8)]
    assert _toks("probs 15/30/30/17/8") == [("pct", 15.0), ("pct", 30.0), ("pct", 30.0), ("pct", 17.0), ("pct", 8.0)]
    assert _toks("0.1 / 4.1 / **8.1** / 11.1 / 14.1%") == [("pct", 0.1), ("pct", 4.1), ("pct", 8.1), ("pct", 11.1),
                                                          ("pct", 14.1)]
    assert [k for k, _ in _toks("−12/−5/+5/+12pp offsets")] == ["pp"] * 4
    assert _toks("10-15% growth") == [("pct", 10.0), ("pct", 15.0)]
    assert _toks("2024 — $103.6M") == [("money", 103.6e6)]                # a year never lends a range its scale
    assert _toks("$19.77 and 25%") == [("money", 19.77), ("pct", 25.0)]    # never through "and"
    # columns are those of the original text (markdown removed, columns kept)
    t = "IRR **18.43%** here"
    k = Q.numbers(t)[0]
    assert t[k.start:k.end] == "18.43%" and k.raw == "18.43%" and Q.line_col("a\nb 5.5%", 4) == (2, 3)


# ---------------------------------------------------------------- 2. ignore rules
IGNORED = ["FY2025", "FY2024–25", "FY23–25", "2023/24", "2026-10-19", "2026-10", "31 May 2025", "May 31, 2025",
           "Nov 1, 2023", "10-K", "20-F", "6-K/A", "0001751008-26-000010", "SIC 6324", "SIC codes 6311/6321",
           "CIK 1751008", "step 8 (c)", "Item 7", "Note 34", "§8.6", "PR #31", "#2", "v5.1", "5.5.0",
           "## DCF — 5.4 final run", "new in 5.5", "pre-5.5", "What 5.5 changed", "engine 5.7", "Q2 2026", "H1 2026",
           "Q2 FY2026", "9M FY2026", "FY 2025", "FY26", "3-yr", "15-year", "90 days", "4 quarters",
           "5 of the last 5", "moat 6/10", "top 10", "CFM56-7B", "MV-75", "COVID-19", "200mm", "S&P 500",
           "Russell 2000", "Nasdaq-100", "Phillips 66", "ASC 805-50", "ASC 805-10", "ASU 2016-13", "IFRS 15", "IAS 36",
           "Topic 842", "R4.htm", "p. F-8", "pp. 51–52", "IV@15", "@12%", "21st", "latest FY OE/share / 1000",
           "sha256 1a2b3c4d5e6f", "<!-- 99.9% -->", "https://example.com/a/12345/7.5%"]


def test_ignore_rules():
    """02 §6.4 (+ A12, A19): each span is not a quantity; method constants are ignored only in their context and
    only when unmatched; "21.6 months" is a number (an engine figure)."""
    for s in IGNORED:
        assert Q.numbers(s) == [], (s, Q.numbers(s))
    for s in ("clears 15%", "2.5% terminal growth", "in scope (under $40B)", "the 0.1x band", "the 1.3 CAP slope",
              "default multiples 0.75 / 0.90 / 1.00 / 1.10 / 1.25", "a >60% revenue jump", "below the 5% flag threshold",
              "the super-bull case (OE ×1.25)", "probs 10/25/30/25/10"):
        toks = Q.numbers(s)
        assert toks and all(Q.is_method_constant(k, s) for k in toks), s
        assert not Q.carries_number(s), s
    for s in ("revenue +15% YoY", "margin 2.5% higher", "$40B of backlog"):
        assert not all(Q.is_method_constant(k, s) for k in Q.numbers(s)), s
    assert _toks("21.6 months") == [("plain", 21.6)]
    assert Q.numbers("What 5.5 is")[0].release_like and not Q.numbers("5.85 per share")[0].release_like
    # a constant that matches a source is a match (the caller decides): trace_text counts it as matched
    vs = Q.ValueSet()
    vs.add(0.15)
    un, ig, checked, matched = CQ.trace_text("clears 15% and 15% again", CQ.Sources(vs))
    assert not un and matched == 2 and ig["const"] == 0, (un, ig)
    un, ig, *_ = CQ.trace_text("clears 15%", CQ.Sources(Q.ValueSet()))
    assert not un and ig["const"] == 1
    un, *_ = CQ.trace_text("revenue +15% YoY", CQ.Sources(Q.ValueSet()))
    assert [u.raw for u in un] == ["+15%"]
    # A12: HALO's "ASC 805-50" / "ASC 805-10" no longer read as 805 in its committed analysis
    rep = CQ.check_folder(os.path.join(ROOT, "HALO"))
    assert rep["status"] == "legacy" and not any(u["raw"].strip("$") == "805" for u in rep["untraced"]), rep["untraced"]
    # not_quantities texts are blanked
    assert Q.numbers("Paragon 28 beat", not_quantities=["Paragon 28"]) == []
    # review r03 (2026-10-21): a convention word (top / first / last / next / past) or a reference word (note, tier,
    # level ...) blanks only a complete small integer — never the leading digits of a research number, which then
    # produced no token at all (neither checked nor ignored)
    for s, raw in (("The company signed its first 100,000 subscribers in Brazil.", "100,000"),
                   ("Management plans the next 1,250 store openings.", "1,250"),
                   ("Over the past 2.5 billion in buybacks the share count fell.", "2.5 billion"),
                   ("It repaid its notes 1,250 million early.", "1,250 million"),
                   ("The bank's Tier 1 13.2% ratio cleared the floor.", "13.2%"),
                   ("Its senior notes 5.25% due 2030 were refinanced.", "5.25%"),
                   ("It reached its first 250 million users.", "250 million"),
                   ("The last 12.5% of the float is locked up.", "12.5%")):
        un, ig, checked, _ = CQ.trace_text(s, CQ.Sources(Q.ValueSet()))
        assert [u.raw for u in un] == [raw] and checked == 1, (s, [u.raw for u in un], ig)
    for s in ("its top 10 customers", "the last 3 years", "the first 100 days", "Tier 1 capital", "Level 3 assets",
              "Item 1A", "Item 7A", "Notes 4-5", "Note 12.3", "tier 2 suppliers", "past 52 weeks"):
        assert Q.numbers(s) == [], (s, Q.numbers(s))


# ---------------------------------------------------------------- 3. tolerance
def test_tolerance_at_quoted_precision():
    """02 §6.5: half a unit of the last written digit, twice that for an approximate token; signs ignored. ("$1,521M"
    is 1,520,504,000 correctly rounded, so it traces — design 02 test 3 listed it as a miss; "$1,522M" is one.)"""
    vs = Q.ValueSet()
    vs.add(0.184321)
    vs.add(1520504000)
    for s, ok in (("18.43%", True), ("18.4%", True), ("18%", True), ("~18.5%", True), ("18.5%", False),
                  ("18.45%", False), ("$1.52B", True), ("$1.5B", True), ("$1,520.5M", True), ("$1.53B", False),
                  ("$1,521M", True), ("$1,522M", False), ("-$1.52B", True), ("about $1.5 billion", True)):
        k = Q.numbers(s)[0]
        assert vs.match(k) is ok, (s, ok)
    vs2 = Q.ValueSet()
    vs2.add(0.0042)
    assert vs2.match(Q.numbers("42 bps")[0]) and not vs2.match(Q.numbers("43 bps")[0])
    vs3 = Q.ValueSet()
    vs3.add(3.25, key="weighted_irr_impact_pp")     # a field already in points
    assert vs3.match(Q.numbers("+3.25pp")[0])


# ---------------------------------------------------------------- 4. worker text
def _folder(base, t, n, j, key_numbers, analysis, facts=None, score=None):
    d = os.path.join(base, t)
    os.makedirs(d, exist_ok=True)
    for name, obj in (("dcf_numbers.json", n), ("judgment.json", j), ("facts.json", facts), ("score.json", score)):
        if obj is not None:
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=1, ensure_ascii=False)
    for name, text in (("key_numbers.md", key_numbers), ("analysis.md", analysis)):
        if text is not None:
            with open(os.path.join(d, name), "w", encoding="utf-8", newline="") as f:
                f.write(text)
    return d


def test_worker_text_is_never_a_source():
    """02 §6.6: a number echoed from worker text — the 5.7 “…” echo, the pre-5.7 "(agent override of X: …)" tier
    line, an Overrides table Source cell, a "- capex reason:" line, an OVERRIDE_APPLIED "(estimate: …)" echo, a
    facts.json label or snippet — never traces; the same figure as an engine number does."""
    base = tempfile.mkdtemp(prefix="cq_worker_")
    try:
        n = {"ticker": T, "engine_version": 5, "engine_release": "5.5.0", "price": 20.0, "iv_at_15": 25.0,
             "fragility_flags": ["OVERRIDE_APPLIED: capex filled (estimate: about 7.75% of revenue per the deck)"]}
        j = {"tier_override_reason": "we trim it: 7.25% haircut on the base", "moat_score": 6.5,
             "probs_used": [0.1, 0.25, 0.3, 0.25, 0.1]}
        kn = ("# TST — key numbers\n- Tier: C (agent override of B: we trim it: 7.25% haircut on the base) · confidence medium\n"
              "- Misfit notch: “a typed 6.25% figure”\n| capex | $1.0M | estimate | 8.25% of sales (the deck) | FY2025 |\n"
              "- capex reason: 9.25% of revenue is the run rate\n- Weighted IRR: 17.00%\n")
        facts = {"schema": 1, "ticker": T, "facts": [{"id": "F1", "label": "share of 5.75% users", "snippet": "a 4.75% move"}]}
        # review r01: judgment.json probs_used / moat_score are judgment text, not a source (25%, 6.5)
        d = _folder(base, T, n, j, kn, "7.25% 6.25% 8.25% 9.25% 7.75% 5.75% 4.75% but 17.00% and 25%, moat 6.5\n",
                    facts=facts)
        rep = CQ.check_folder(d)
        assert rep["status"] == "legacy"
        assert sorted(u["raw"] for u in rep["untraced"]) == ["25%", "4.75%", "5.75%", "6.25%", "6.5", "7.25%", "7.75%",
                                                              "8.25%", "9.25%"], rep["untraced"]
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_worker_text_the_engine_echoes_is_never_a_source():
    """Review r01 / r02 (2026-10-21): the engine copies worker text into its own record (ads_ratio.source here; an
    override's source, a share-class source) and echoes it into flag strings — in dcf_numbers.json and in
    key_numbers.md's Fragility flags. That text is blanked through the record's own copy (hash-bound by I1), at any
    length, so a number inside it never traces analysis.md — and editing judgment.json after make_score (the 12+
    character judgment strings are blanked too) changes nothing."""
    from test_make_score_55 import _ads, CUR
    for src in ("NRR 131%", "20-F cover page; NRR 131% per investor deck"):
        n = _ads(2.0, 20.0, release=CUR)
        n["ads_ratio"] = dict(n["ads_ratio"], source=src)
        n["fragility_flags"] = [f"ADS_RATIO_APPLIED: 20-F filer — per-share figures scaled x2.0 ordinary shares per "
                                f"ADS ({src}) so they are comparable to the ADS price; TTM pins are taken as per-ADS "
                                "already"]
        r = Run(n, _judgment(n)).run()
        try:
            assert r.rc == 0, r.err[-800:]
            assert f"({src})" in r.key()
            with open(os.path.join(r.folder, "analysis.md"), "w", encoding="utf-8") as f:
                f.write(GOOD + "Net revenue retention reached 131%.\n")
            rep = CQ.check_folder(r.folder)
            assert rep["status"] == "fail" and [u["raw"] for u in rep["untraced"]] == ["131%"], (src, rep)
            with open(r.jpath, encoding="utf-8") as f:
                j = json.load(f)
            j["ads_ratio"]["source"] = "Form 20-F cover page"
            with open(r.jpath, "w", encoding="utf-8") as f:
                json.dump(j, f, indent=1)
            rep = CQ.check_folder(r.folder)
            assert rep["status"] == "fail" and [u["raw"] for u in rep["untraced"]] == ["131%"], (src, rep)
        finally:
            r.close()


# ---------------------------------------------------------------- 5. committed figures re-quoted
COMMITTED = ("APP", "GMED", "VOD", "RNR", "MICC", "HALO")


def _variants(k):
    v, out = abs(k.val if k.kind in ("money", "plain", "mult") else k.v), [k.raw]
    if k.kind == "money":
        if v >= 1e9:
            out += [f"${v / 1e9:.3f}B", f"${v / 1e9:.2f}B", f"${v / 1e9:.1f}B", f"${v / 1e6:,.0f}M",
                    f"${v / 1e9:.1f} billion", f"~${v / 1e9:.0f}B"]
        elif v >= 1e6:
            out += [f"${v / 1e6:.1f}M", f"${v / 1e6:,.0f}M", f"${v / 1e6:.2f} million", f"${v:,.0f}"]
        elif v >= 1:
            out += [f"${v:.2f}", f"${v:.1f}", f"~${v:.0f}"]
    elif k.kind == "pct":
        out += [f"{v:.1f}%", f"~{v:.0f}%", f"{v:.2f}%"]
    elif k.kind == "mult":
        out += [f"{v:.1f}x", f"{v:.2f}×"]
    return out


def test_committed_engine_figures_requoted_match():
    """02 test 5 (+ A16): every engine figure printed in a committed folder's key_numbers.md (worker text removed),
    re-quoted at analyst precision ($3.742B -> $3.74B, $3.7B, $3,742M, ~$4B; 18.43% -> 18.4%, ~18%; 6.05x -> 6.1x),
    traces. Guards the tokenizer and the tolerance against a regression on real files (HALO: the IPR&D lines)."""
    fails, total = [], 0
    for t in COMMITTED:
        d = os.path.join(ROOT, t)
        with open(os.path.join(d, "key_numbers.md"), encoding="utf-8", newline="") as f:
            raw = f.read()      # CRLF on a Windows checkout (core.autocrlf), LF in git and on the VM
        j = CQ._try_load(os.path.join(d, "judgment.json")) or {}
        n = CQ._try_load(os.path.join(d, "dcf_numbers.json")) or {}
        src = CQ.Sources.for_folder(d)
        text = CQ.key_numbers_source_text(raw.replace("\r\n", "\n"), CQ.worker_blank(j, None, n))
        for k in Q.numbers(text):
            if (k.val if k.kind in ("money", "plain", "mult") else k.v) == 0:
                continue
            for q in _variants(k):
                qt = Q.numbers(q)
                if not qt:
                    continue
                total += 1
                if not all(src.match(x) for x in qt):
                    fails.append((t, k.raw, q))
    assert total > 1500 and not fails, (total, fails[:20])


# ---------------------------------------------------------------- 6. CLI
def _built(release=None, j=None):
    """A make_score-built folder (a 5.7 run unless release says otherwise) in its own temp base."""
    n = _numbers() if release is None else _numbers(release=release)
    r = Run(n, j).run()
    assert r.rc == 0, r.err[-800:]
    return r


GOOD = "Tier B: weighted IRR 17.00% (base case 17.00%), weighted IV $25.00 at 15% against a $20.00 price.\n"


def test_cli_exit_codes():
    """02 §6.1: gated pass -> 0; gated fail -> 1 listing analysis.md:<line>; legacy -> 0 "legacy"; legacy --strict
    -> 1; no analysis.md -> 2; a hand-edited key_numbers.md (I2) -> 1 naming it; --json is the report."""
    r = _built()
    try:
        with open(os.path.join(r.folder, "analysis.md"), "w", encoding="utf-8") as f:
            f.write(GOOD)
        rc, out = _cli(r.base, T)
        assert rc == 0 and "PASS" in out, out
        rc, out = _cli(r.base, T, "--json")
        rep = json.loads(out)
        assert rc == 0 and rep["status"] == "pass" and rep["gated"] and rep["checked"] >= 4 and not rep["untraced"], rep
        with open(os.path.join(r.folder, "analysis.md"), "a", encoding="utf-8") as f:
            f.write("\nBuybacks were $2.19B last year (a preliminary run said 14.35%).\n")
        rc, out = _cli(r.base, T)
        assert rc == 1 and "FAIL" in out and "analysis.md:3:" in out and "\"$2.19B\"" in out, out
        assert "--save-run TST prelim" in out, out
        rep = CQ.check_folder(r.folder)
        assert "2 numbers trace to no generated file" in CQ.refusal_text(rep), CQ.refusal_text(rep)
        rep1 = dict(rep, untraced=rep["untraced"][:1])
        assert "1 number traces to no generated file" in CQ.refusal_text(rep1), CQ.refusal_text(rep1)   # review r08
        # I2: a number added to key_numbers.md by hand
        with open(os.path.join(r.folder, "analysis.md"), "w", encoding="utf-8") as f:
            f.write(GOOD)
        with open(os.path.join(r.folder, "key_numbers.md"), "a", encoding="utf-8") as f:
            f.write("- Buybacks: $2.19B\n")
        rc, out = _cli(r.base, T)
        assert rc == 1 and "I2: key_numbers.md differs from what make_score.py wrote" in out, out
        os.remove(os.path.join(r.folder, "analysis.md"))
        rc, out = _cli(r.base, T)
        assert rc == 2 and "no analysis.md" in out, out
    finally:
        r.close()
    r = _built(release="5.5.0")
    try:
        with open(os.path.join(r.folder, "analysis.md"), "w", encoding="utf-8") as f:
            f.write(GOOD + "Buybacks were $2.19B.\n")
        rc, out = _cli(r.base, T)
        assert rc == 0 and "legacy" in out and "\"$2.19B\"" in out, out
        rc, out = _cli(r.base, T, "--strict")
        assert rc == 1, out
    finally:
        r.close()
    assert _cli(tempfile.gettempdir(), "--save-run")[0] == 2


def test_integrity_checks_on_gated_runs():
    """02 §6.2 I1, I3, I4, I5 (+ A7: I1 is reprice.run_hash_problem's rule): another run's score.json, a facts.json
    edited after make_score, a tampered saved run, an empty analysis.md — each fails a gated run; a key_numbers.md
    whose only change is CRLF line endings (a Windows checkout) passes I2 (A5)."""
    r = _built()
    try:
        p = os.path.join(r.folder, "analysis.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(GOOD)
        assert CQ.check_folder(r.folder)["status"] == "pass"
        # A5: the same key_numbers.md with CRLF line endings (a Windows checkout, core.autocrlf) still passes I2
        kp = os.path.join(r.folder, "key_numbers.md")
        lf = open(kp, encoding="utf-8").read()
        with open(kp, "w", encoding="utf-8", newline="") as f:
            f.write(lf.replace("\n", "\r\n"))
        assert CQ.check_folder(r.folder)["status"] == "pass", CQ.check_folder(r.folder)["integrity"]
        with open(kp, "w", encoding="utf-8", newline="") as f:
            f.write(lf)
        assert CQ.check_folder(r.folder)["status"] == "pass"
        sp = os.path.join(r.folder, "score.json")
        s = json.load(open(sp, encoding="utf-8"))
        json.dump(dict(s, dcf_content_hash="0" * 64), open(sp, "w", encoding="utf-8"))
        assert any(m.startswith("I1:") for m in CQ.check_folder(r.folder)["integrity"])
        json.dump(s, open(sp, "w", encoding="utf-8"))
        # [Integrate L3] the run's facts.json (the minimal moat scorecard's facts, rulings57) is put back afterwards,
        # not deleted: the scorecard make_score re-reads below cites them
        fp = os.path.join(r.folder, "facts.json")
        facts_before = open(fp, "rb").read() if os.path.exists(fp) else None
        with open(fp, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "ticker": T, "facts": []}, f)
        assert any(m.startswith("I3:") for m in CQ.check_folder(r.folder)["integrity"])
        if facts_before is None:
            os.remove(fp)
        else:
            with open(fp, "wb") as f:
                f.write(facts_before)
        n = json.load(open(os.path.join(r.folder, "dcf_numbers.json"), encoding="utf-8"))
        with open(os.path.join(r.folder, "dcf_numbers_prelim.json"), "w", encoding="utf-8") as f:
            json.dump(dict(n, price=99.0), f)
        integ = CQ.check_folder(r.folder)["integrity"]
        assert any(m.startswith("I4:") and "MISMATCH" in m for m in integ), integ
        with open(os.path.join(r.folder, "dcf_numbers_prelim.json"), "w", encoding="utf-8") as f:
            json.dump(n, f)
        integ = CQ.check_folder(r.folder)["integrity"]
        assert any("not listed in score.json method_runs" in m for m in integ), integ
        # review r07: I4 binds a saved run by content_hash, not by label — one replaced after make_score fails, and
        # its figures are no source until make_score re-runs and renders it
        with open(p, "w", encoding="utf-8") as f:
            f.write(GOOD + "The preliminary run gave a weighted IRR of 14.37%.\n")
        r.run()
        assert r.rc == 0, r.err[-800:]
        rep = CQ.check_folder(r.folder)
        assert not rep["integrity"] and [u["raw"] for u in rep["untraced"]] == ["14.37%"], rep
        with open(os.path.join(r.folder, "dcf_numbers_prelim.json"), "w", encoding="utf-8") as f:
            json.dump(_stamp(dict(n, implied_irr_weighted=0.1437)), f)
        rep = CQ.check_folder(r.folder)
        assert rep["integrity"] == ["I4: dcf_numbers_prelim.json changed after make_score.py — re-run make_score.py"], rep
        assert [u["raw"] for u in rep["untraced"]] == ["14.37%"] and rep["sources"]["method_runs"] == [], rep
        r.run()
        assert r.rc == 0, r.err[-800:]
        rep = CQ.check_folder(r.folder)
        assert rep["status"] == "pass" and rep["sources"]["method_runs"] == ["prelim"], rep
        with open(p, "w", encoding="utf-8") as f:
            f.write(GOOD)
        os.remove(os.path.join(r.folder, "dcf_numbers_prelim.json"))
        open(p, "w").close()
        assert any(m.startswith("I5:") for m in CQ.check_folder(r.folder)["integrity"])
    finally:
        r.close()


# ---------------------------------------------------------------- 7. --all
def test_all_mode_gates_only_57_runs():
    """02 §6.1: --all exits 1 only when a gated (5.7) run fails; a failing legacy run is reported, never failing; the
    summary counts statuses; --release-min filters; --json writes every report."""
    base = tempfile.mkdtemp(prefix="cq_all_")
    built = []
    try:
        for name, release, text in (("LEG", "5.5.0", GOOD + "Buybacks $2.19B.\n"), ("GOOD", None, GOOD)):
            r = _built(release)
            built.append(r)
            with open(os.path.join(r.folder, "analysis.md"), "w", encoding="utf-8") as f:
                f.write(text)
            shutil.copytree(r.folder, os.path.join(base, name))
        rc, out = _cli(base, "--all")
        assert rc == 0 and "LEG legacy" in out and "GOOD pass" in out and "2 folders" in out, out
        assert "gated 1" in out, out
        shutil.copytree(os.path.join(base, "GOOD"), os.path.join(base, "BAD"))
        with open(os.path.join(base, "BAD", "analysis.md"), "a", encoding="utf-8") as f:
            f.write("Margins hit 31.4%.\n")
        jp = os.path.join(base, "all.json")
        rc, out = _cli(base, "--all", "--json", jp)
        assert rc == 1 and "BAD fail" in out and "fail 1" in out, out
        reps = json.load(open(jp, encoding="utf-8"))
        assert sorted(x["ticker"] for x in reps) == ["BAD", "GOOD", "LEG"], reps
        rc, out = _cli(base, "--all", "--release-min", "5.7.0", "--quiet")
        assert rc == 1 and "2 folders" in out and "LEG" not in out, out
    finally:
        for r in built:
            r.close()
        shutil.rmtree(base, ignore_errors=True)


# ---------------------------------------------------------------- 8. --save-run
def test_save_run_copies_verified_output_only():
    """02 §6.1 (+ A7): a valid run is copied byte for byte; a tampered dcf_numbers.json is refused (exit 1, nothing
    written); an existing label needs --replace; a bad label is a usage error (exit 2)."""
    r = _built()
    try:
        src = os.path.join(r.folder, "dcf_numbers.json")
        rc, out = _cli(r.base, "--save-run", T, "prelim")
        dst = os.path.join(r.folder, "dcf_numbers_prelim.json")
        assert rc == 0 and open(dst, "rb").read() == open(src, "rb").read(), out
        rc, out = _cli(r.base, "--save-run", T, "prelim")
        assert rc == 1 and "--replace" in out, out
        rc, out = _cli(r.base, "--save-run", T, "prelim", "--replace")
        assert rc == 0, out
        assert _cli(r.base, "--save-run", T, "Bad-Label")[0] == 2
        n = json.load(open(src, encoding="utf-8"))
        json.dump(dict(n, price=1.0), open(src, "w", encoding="utf-8"))
        rc, out = _cli(r.base, "--save-run", T, "other")
        assert rc == 1 and "MISMATCH" in out and not os.path.exists(os.path.join(r.folder, "dcf_numbers_other.json")), out
    finally:
        r.close()


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL {name}: {str(e)[:1500]}")
            except Exception as e:
                fails += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
