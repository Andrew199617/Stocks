#!/usr/bin/env python3
"""build_site.py tests (v6 data layer). Run: python3 _system/tests/test_build_site.py
(or python3 -m pytest _system/tests). No network. Nothing in the repo is
written: the four test folders (APP, KR, AEE, ZS) plus _system/queue.json and
_system/overrides_registry.json are COPIED into a temporary STOCKS_BASE and
the site is built there with --only APP,KR,AEE,ZS, so the "touch a folder
file" and "folder no longer qualifies" cases run on the copies.

1. Contract shapes: required keys and types on meta / index rows / records,
   ranking by irr_live-else-irr with nulls last, AEE (Tier F) has no paths and
   null IRR fields, ZS carries irr_at_floor (bear cases at the floor in
   live.json), sensitivity has 10/12/15/20/25 + irr for all five scenarios
   and weighted, hurdle prices 15/20/25, has{} flags match the files present.
2. Attachment: top-N records are trimmed (no judgment / ttm / prices.daily_1y /
   numbers.used_tags), the full index is carried, the JSON is script-safe.
   Engine 5.5's numbers.capex_provenance / sbc_provenance / share_basis are
   dropped from the attachment copy like used_tags (trim_record), and kept
   in the site record.
3. Incremental: a second run skips every unchanged record; touching one
   folder file rebuilds only that record; removing score.json removes the
   record and lists it.
4. CLI: the script runs from the command line and prints one summary line.
5. Watchlist: _system/watchlist.json -> meta.watchlist + row.watchlist on
   every row (and meta.stale entries), re-derived on every run without
   rebuilding records.
6. Keys: a folder whose score.json ticker differs from the folder name is
   served as data/<ticker>.json (row, record, attachment agree); a second
   folder claiming an already-served ticker is ignored and reported.
7. Robustness: non-object score/numbers, lists where objects belong, NaN in a
   verbatim file, 1e400 in the CSV -> the run completes, every output is
   strict JSON; a record that still fails to build is logged, keeps its
   previous row and is listed in meta.failed, the others are written.
8. Deleted folder files: removing live.json (or segments.json) rebuilds the
   record on the next run even though no surviving file is newer.
9. Scored floor flags (review 4289642893): every sensitivity row carries
   irr_at_floor for the SCORED IRR — the run's own flag when recorded, else
   solve_irr's flag on the replayed flows (ZS bear / super-bear at floor),
   never replacing the recorded IRR.
10. Zero terminal growth (review 4289642918): g_terminal = 0.0 is kept, and
   the replayed hurdle prices / sensitivity IVs use it.
11. street.json (2026-10-16 data policy): merged onto record.profile.street /
   .market / .street_fetched_at, legacy profile.json fallback, a changed
   street.json rebuilds only that record.
12. Missing outputs: a fresh clone (no caches, no _daily/) builds everything;
   a deleted data/<T>.json is rebuilt whatever state.json says, even outside
   --only; meta.json / index.json are always written.
13. History CSV: --attachment writes _daily/history/ranking-<date>.csv.
14. Dividends at the latest close (2026-10-16 data policy): a newer
   prices.json close reprices the committed dividends block with
   fundamentals.price_dividends (row yields follow); an older close, no
   prices.json, a pre-5.4.4 block or a split since scoring leave it as
   written. On EVERY committed folder with a dividends block (offline) the
   function reproduces the committed block at its own price, and the block
   build_site serves at a price P equals price_dividends(price-free core, P)
   — what fundamentals.py writes at P (build_dividends ends with that call).
15. Split since scoring: a live.json with split_factor 2.0 halves every
   per-share run figure the app shows (SPLIT_DIVIDE), doubles the run's share
   counts, leaves IRRs / tiers / upside / market caps alone, and sets
   record.split_restated and row.split_restated.
16. Live older than the score: a live.json whose close predates the scored
   analysis is withheld (record.live null, record.live_withheld, row flag),
   and the ranking / history CSV use the scored figures.
17. record.profile carries street_fetched_at (null) without street.json.
18. Pre-render (2026-10-16): with the real app shell in the site dir and Node
    available, --attachment inlines the static layer prerender.js renders
    with the app's own code (ranking rows + company pages as plain HTML that
    reads with JavaScript off, CSS-radio tier filter, JS-on cleanup script),
    SITE_DATA stays inlined, and prerender=False keeps the old JS-only file.
    Skipped when Node or the shell is unavailable.
19. Prices staleness guard (2026-10-20): a scored name whose last close on
    file is more than one session behind the newest close the sweep holds
    is flagged on its row (row.prices_stale {last_date, sessions_behind,
    latest_close}) and counted / named in meta — one session behind is
    the normal posting lag. The flag is re-derived on every build, like
    row.watchlist. (The refresh that never ran left HALO two sessions
    behind for two days in October 2026, silent.)
20. Engine 5.7 rulings (Andrew, 2026-10-19; lane L6, design 06 + rebase
    amendments B1-B20): facts.json served and rebuilt (T-PY-1), the misfit
    notch row fields and the new tier_override meaning (T-PY-2), the live
    notch on a bound live.json (T-PY-3), the attachment keeping facts and a
    declared-interim ttm.json (T-PY-4), the quote check and its failure
    isolation (T-PY-5), the builder mtime following the checker (T-PY-6),
    the moat / interim row summaries (T-PY-7), split restatement of the new
    per-share figures (T-PY-8) and of declared share classes (08 §10),
    base_alternatives passed through (R7), record.score_from_run (B5), the
    history CSV's moat / hold columns (T-PY-10, T-PY-11), the moat summary
    keys (T-PY-12), meta.counts.moat_eroding / moat_widening (T-PY-13), the
    forecast hold fields (T24) and every committed folder building with the
    new fields (T-PY-9, ~1 min).

The Nasdaq caches (prices.json, live.json, street.json) are gitignored, so
a fresh clone has none: TempBase removes whatever the copies carried and
installs the frozen copies in test_build_site_fixtures.json (or nothing,
with caches=False), so no assertion depends on the machine or the market.
"""
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
BASE = os.path.dirname(SYS)
sys.path.insert(0, SYS)
import build_site as B  # noqa: E402
import fundamentals as F  # noqa: E402
import _stable as S  # noqa: E402

TICKERS = ["APP", "KR", "AEE", "ZS"]
ONLY = ",".join(TICKERS)
RATES = ("10", "12", "15", "20", "25")
SCN = ["super_bear", "bear", "base", "bull", "super_bull", "weighted"]
ROW_KEYS = {"ticker": str, "name": str, "sector": (str, type(None)), "fit": str, "tier": str, "tier_by_numbers": (str, type(None)),
            "tier_override": bool, "tier_live": (str, type(None)), "tier_bear": (str, type(None)), "tier_bull": (str, type(None)),
            "irr": (float, type(None)), "irr_live": (float, type(None)), "irr_bear": (float, type(None)), "irr_bull": (float, type(None)),
            "irr_at_floor": bool, "irr_capped": bool, "f_subtype": (str, type(None)), "price": (float, type(None)),
            "price_live": (float, type(None)), "price_date": (str, type(None)), "ret_1y_pct": (float, type(None)),
            "iv15": (float, type(None)), "iv12": (float, type(None)), "iv20": (float, type(None)), "iv25": (float, type(None)),
            "upside15": (float, type(None)), "upside15_live": (float, type(None)), "market_cap_b": (float, type(None)),
            "market_cap_b_live": (float, type(None)), "moat": (float, type(None)), "cap_years": (float, type(None)),
            "confidence": (str, type(None)), "confidence_capped": bool, "one_liner": (str, type(None)), "analysis_date": (str, type(None)),
            "engine_release": (str, type(None)), "flags": list, "overrides": list, "override_unblocks_tier": bool,
            "second_pass": (dict, type(None)), "alert_eligible": bool, "dividend_yield": (float, type(None)),
            "shareholder_yield": (float, type(None)), "has": dict, "watchlist": bool,
            "live_withheld": bool, "split_restated": (dict, type(None)), "prices_stale": (dict, type(None)),
            # engine 5.7 rulings (lane L6; design 06 §3, rebase B17): the misfit notch (R1), the moat and 6-K bridge
            # summaries (R4 / R2a), the share basis (R6)
            "tier_notched": bool, "misfit_notch": (dict, type(None)), "tier_by_numbers_live": (str, type(None)),
            "misfit_notch_live": (dict, type(None)), "moat_evidence": (dict, type(None)), "interim_bridge": (dict, type(None)),
            "share_basis": (str, type(None))}
HAS_KEYS = ("prices", "fundamentals", "dividends", "segments", "live", "analysis", "second_pass", "statements", "profile", "facts")
RECORD_KEYS = ("ticker", "name", "sector", "folder", "built_at", "built_from_mtime", "row", "score", "numbers", "forecast", "live", "profile",
               "history", "fundamentals", "prices", "segments", "ttm", "judgment", "registry", "analysis_md", "second_pass_md", "files",
               "live_withheld", "split_restated", "facts", "quote_check", "score_from_run")
FORECAST_KEYS = ("paths", "growth_paths", "sensitivity", "hurdle_prices", "inputs", "g_base", "g_blend", "g_terminal", "cap_years",
                 "growth_components", "growth_components_adjusted", "share_cagr", "share_count_adj", "share_adj_basis", "replayed",
                 "hold_years", "moat_trend", "hold_by_scenario")


CACHE_FILES = ("prices.json", "live.json", "street.json")  # gitignored: never assumed present in the repo
FIXTURES = os.path.join(HERE, "test_build_site_fixtures.json")


class TempBase:
    """A temporary STOCKS_BASE holding copies of the test folders. The
    gitignored caches are replaced by the frozen fixtures (caches=True) or
    left absent like a fresh clone (caches=False)."""

    def __init__(self, caches=True):
        self.caches = caches

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix="build_site_test_")
        os.makedirs(os.path.join(self.dir, "_system"))
        fixtures = B.jload(FIXTURES)["folders"] if self.caches else {}
        for t in TICKERS:
            shutil.copytree(os.path.join(BASE, t), os.path.join(self.dir, t))
            for f in CACHE_FILES:
                p = os.path.join(self.dir, t, f)
                if os.path.exists(p):
                    os.remove(p)
            for f, obj in fixtures.get(t, {}).items():
                self.write_json(t, f, obj=obj)
        for f in ("queue.json", "overrides_registry.json", "watchlist.json"):
            shutil.copy(os.path.join(SYS, f), os.path.join(self.dir, "_system", f))
        self.site = os.path.join(self.dir, "_daily", "site")
        return self

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)

    def build(self, **kw):
        kw.setdefault("only", TICKERS)
        kw.setdefault("quiet", True)
        return B.build(base=self.dir, site_dir=self.site, **kw)

    def read(self, name):
        with open(os.path.join(self.site, name), encoding="utf-8") as f:
            return json.load(f)

    def record(self, t):
        return self.read(os.path.join("data", f"{t}.json"))

    def write_json(self, *parts, obj):
        path = os.path.join(self.dir, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)

    def clone(self, src, folder, ticker=None, **edits):
        """Copy test folder `src` to `folder`, set score.ticker (default: the
        folder name) and apply {filename: callable(obj) -> obj | text} edits."""
        dst = os.path.join(self.dir, folder)
        shutil.copytree(os.path.join(self.dir, src), dst)
        sc = B.jload(os.path.join(dst, "score.json"))
        sc["ticker"] = ticker or folder
        self.write_json(folder, "score.json", obj=sc)
        # make_score copies the run's ticker into score.json: the clone's run says the same, so its score.json is
        # still the run's own (build_site.score_from_run — Codex review r11 of PR #47)
        nb = B.jload(os.path.join(dst, "dcf_numbers.json"))
        if isinstance(nb, dict):
            self.write_json(folder, "dcf_numbers.json", obj=dict(nb, ticker=sc["ticker"]))
        for fname, fn in edits.items():
            path = os.path.join(dst, fname)
            cur = B.jload(path) if fname.endswith(".json") else B.tread(path)
            new = fn(cur)
            if isinstance(new, str):
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
            else:
                self.write_json(folder, fname, obj=new)
        return dst


def strict_json(path):
    """json.load that refuses NaN / Infinity (what browsers' JSON.parse refuses)."""
    def bad(c):
        raise ValueError(f"non-finite constant {c} in {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f, parse_constant=bad)


def _check_types(obj, spec, where):
    for k, typ in spec.items():
        assert k in obj, f"{where}: missing {k}"
        assert isinstance(obj[k], typ), f"{where}.{k}: {type(obj[k]).__name__} not {typ}"


def test_contract_shapes():
    with TempBase() as tb:
        res = tb.build()
        assert sorted(res["written"]) == sorted(TICKERS) and not res["skipped"] and not res["removed"]
        meta, index = tb.read("meta.json"), tb.read("index.json")
        # ---- meta
        _check_types(meta, {"built_at": str, "date": str, "data_version": int, "engine_release_latest": (str, type(None)), "sweep": dict,
                            "counts": dict, "hurdles": dict, "stale": list, "notes": list, "watchlist": list, "failed": list, "tabs": list}, "meta")
        assert meta["failed"] == [] and meta["counts"]["failed"] == 0
        for k in ("done", "total", "pending", "blocked_data_gap", "blocked_no_data", "in_progress"):
            assert isinstance(meta["sweep"][k], int), k
        assert meta["sweep"]["total"] == 2617 and meta["sweep"]["done"] >= 1
        assert meta["counts"]["current"] == 4 and meta["counts"]["stale"] == 0 and meta["counts"]["with_live"] == 3
        assert meta["counts"]["tiers"] == {"S": 0, "A": 0, "B": 1, "C": 0, "D": 2, "F": 1}
        assert meta["hurdles"] == {"S": 0.25, "A": 0.20, "B": 0.15, "C": 0.10}
        assert len(meta["date"]) == 10 and meta["built_at"].startswith(meta["date"])
        # ---- index rows
        assert [r["ticker"] for r in index] == ["APP", "KR", "ZS", "AEE"], [r["ticker"] for r in index]  # irr_live else irr, nulls last
        keys = [r["irr_live"] if r["irr_live"] is not None else r["irr"] for r in index]
        non_null = [k for k in keys if k is not None]
        assert non_null == sorted(non_null, reverse=True) and keys[-1] is None
        for r in index:
            _check_types(r, ROW_KEYS, r["ticker"])
            assert set(r["has"]) == set(HAS_KEYS) and all(isinstance(v, bool) for v in r["has"].values())
            assert r["fit"] in ("modeled", "misfit") and r["tier"] in "SABCDF"
            for o in r["overrides"]:
                assert set(o) == {"field", "kind"}
            folder = os.path.join(tb.dir, r["ticker"])
            fund = B.jload(os.path.join(folder, "fundamentals.json"))
            expect = {"prices": os.path.exists(os.path.join(folder, "prices.json")), "fundamentals": isinstance(fund, dict),
                      "dividends": isinstance(fund, dict) and isinstance(fund.get("dividends"), dict),
                      "segments": os.path.exists(os.path.join(folder, "segments.json")), "live": os.path.exists(os.path.join(folder, "live.json")),
                      "analysis": os.path.exists(os.path.join(folder, "analysis.md")), "second_pass": os.path.exists(os.path.join(folder, "second_pass.md")),
                      "statements": isinstance(B.jload(os.path.join(folder, "statements.json")), dict),
                      "profile": isinstance(B.jload(os.path.join(folder, "profile.json")), dict),
                      "facts": isinstance(B.jload(os.path.join(folder, "facts.json")), dict)}
            assert r["has"] == expect, (r["ticker"], r["has"], expect)
            if r["has"]["live"]:
                assert r["irr_live"] is not None and r["price_live"] is not None and r["tier_live"] in "SABCDF"
            else:
                assert r["irr_live"] is None and r["price_live"] is None and r["tier_live"] is None
        app = next(r for r in index if r["ticker"] == "APP")
        assert app["tier"] == "B" and app["fit"] == "modeled" and app["overrides"] == [{"field": "capex", "kind": "estimate"}]
        assert app["iv20"] is not None and app["iv25"] is not None and app["iv25"] < app["iv20"] < app["iv15"] < app["iv12"]
        assert app["upside15_live"] is not None and app["market_cap_b_live"] is not None and app["ret_1y_pct"] is not None
        # ---- records
        for t in TICKERS:
            rec = tb.record(t)
            for k in RECORD_KEYS:
                assert k in rec, f"{t}: record missing {k}"
            assert rec["row"] == next(r for r in index if r["ticker"] == t)
            assert rec["folder"] == t and isinstance(rec["built_from_mtime"], float)
            assert "paths" not in rec["numbers"] and "growth_paths" not in rec["numbers"]
            for k in FORECAST_KEYS:
                assert k in rec["forecast"], f"{t}: forecast missing {k}"
            assert isinstance(rec["history"], list) and rec["history"], t
            h0 = rec["history"][0]
            assert isinstance(h0["revenue"], (int, float)) and isinstance(h0["period_end"], str)  # CSV coercion
            assert all(v is None or isinstance(v, (int, float, bool, str)) for v in h0.values())
            assert set(rec["prices"]) >= {"source", "as_of", "stats", "weekly", "daily_1y"}
            assert rec["files"] == sorted(f for f in os.listdir(os.path.join(tb.dir, t)) if not f.startswith("."))
            assert isinstance(rec["registry"], list) and (rec["analysis_md"] is None or isinstance(rec["analysis_md"], str))
        # ---- AEE: Tier F, no scenarios
        aee = tb.record("AEE")
        assert aee["row"]["tier"] == "F"
        for k in ("irr", "irr_live", "irr_bear", "irr_bull", "iv15", "iv20", "iv25", "upside15"):
            assert aee["row"][k] is None, (k, aee["row"][k])
        assert aee["forecast"]["paths"] is None and aee["forecast"]["growth_paths"] is None
        assert aee["forecast"]["sensitivity"] is None and aee["forecast"]["hurdle_prices"] is None and aee["forecast"]["replayed"] is False
        assert aee["live"] is None and aee["row"]["tier_live"] is None
        # ---- ZS: IRR at the model floor
        zs = tb.record("ZS")
        assert isinstance(zs["row"]["irr_at_floor"], bool)
        sens = zs["forecast"]["sensitivity"]
        assert any(sens[k].get("irr_live_at_floor") for k in SCN), "ZS bear cases sit at the floor in live.json"
        assert zs["row"]["irr"] is not None and zs["row"]["irr"] < 0.05
        # ---- sensitivity / hurdle prices on the modeled names
        for t in ("APP", "KR", "ZS"):
            rec = tb.record(t)
            fc = rec["forecast"]
            assert set(fc["paths"]) == set(SCN) and all(len(fc["paths"][k]) == 15 for k in SCN)
            assert set(fc["growth_paths"]) == set(SCN) - {"weighted"} and all(len(fc["growth_paths"][k]) == 15 for k in fc["growth_paths"])
            assert set(fc["sensitivity"]) == set(SCN)
            for k in SCN:
                row = fc["sensitivity"][k]
                for rate in RATES:
                    assert isinstance(row[rate], float), (t, k, rate, row)
                assert row["10"] > row["12"] > row["15"] > row["20"] > row["25"] > 0, (t, k)
                assert isinstance(row["irr"], float) and "irr_live" in row
                assert isinstance(row["irr_at_floor"], bool), (t, k, row)  # the scored flag: recorded or replayed, never missing here
                assert isinstance(row["irr_live"], float)  # all three carry live.json
            assert fc["sensitivity"]["weighted"]["irr_at_floor"] is rec["row"]["irr_at_floor"], t
            assert set(fc["hurdle_prices"]) == {"15", "20", "25"}
            hp = fc["hurdle_prices"]
            assert hp["15"] > hp["20"] > hp["25"] > 0
            w15 = rec["numbers"]["weighted"]["iv_at_15"]  # the engine's own figure, bit-for-bit through the replay
            assert hp["15"] == w15 and fc["sensitivity"]["weighted"]["15"] == w15, (t, hp, w15)
            assert abs(hp["15"] - rec["score"]["iv_at_15"]) < 0.01, (t, hp, rec["score"]["iv_at_15"])  # score.json rounds to cents
            assert rec["row"]["iv20"] == hp["20"] and rec["row"]["iv25"] == hp["25"]
            assert fc["replayed"] is (not bool(rec["numbers"].get("hurdle_prices")))
            live = rec["live"]
            assert abs(fc["sensitivity"]["weighted"]["irr_live"] - live["irr_weighted"]) < 1e-12
            for k in SCN[:-1]:
                assert abs(fc["sensitivity"][k]["irr_live"] - live["scenarios"][k]["irr"]) < 1e-12
                assert abs(fc["sensitivity"][k]["irr"] - rec["numbers"]["scenarios"][k]["irr"]) < 1e-12


def test_attachment_trimmed():
    with TempBase() as tb:
        res = tb.build(attachment=True, top=2)
        path, size, n = res["attachment"]
        assert n == 2 and os.path.exists(path) and size > 0
        assert os.path.basename(path) == f"ranking-{res['meta']['date']}.html"
        latest = os.path.join(tb.dir, "_daily", "latest.html")
        assert os.path.exists(latest) and os.path.getsize(latest) == os.path.getsize(path)
        with open(path, encoding="utf-8") as f:
            doc = f.read()
        start = doc.index("<script>window.SITE_DATA=") + len("<script>window.SITE_DATA=")
        end = doc.index(";</script>", start)
        payload_text = doc[start:end]
        assert "</" not in payload_text and "<!--" not in payload_text, "payload must be safe inside a script tag"
        data = json.loads(payload_text)
        assert set(data) >= {"meta", "index", "records"}
        assert [r["ticker"] for r in data["index"]] == ["APP", "KR", "ZS", "AEE"]  # the full index travels
        assert sorted(data["records"]) == ["APP", "KR"]  # only the top 2
        for t, rec in data["records"].items():
            assert "judgment" not in rec and "ttm" not in rec, t
            assert "daily_1y" not in rec["prices"] and "weekly" in rec["prices"], t
            assert "used_tags" not in rec["numbers"], t
            for k in ("row", "score", "forecast", "history", "fundamentals", "analysis_md", "files"):
                assert k in rec, (t, k)
        full = tb.record("APP")
        assert "judgment" in full and "ttm" in full and "daily_1y" in full["prices"]  # the site record is untrimmed
        assert "<title>" in doc and "<!doctype html>" in doc.lower()


def test_trim_record_drops_engine_provenance():
    """Engine 5.5 adds per-period provenance records to dcf_numbers.json; the
    attachment copy drops them (with used_tags) so its size stays flat, and
    leaves every other numbers key and the site record itself untouched."""
    numbers = {"base_oe_per_share": 3.0, "market_cap_basis": {"shares_used": 1e9, "shares_source": "diluted_latest"},
               "share_scale": {"defect": False}, "used_tags": {"capex": "PaymentsToAcquirePropertyPlantAndEquipment"},
               "capex_provenance": {"2025-12-31": {"ppe_source": "rollup"}},
               "sbc_provenance": {"2025-12-31": {"reconciled": False}},
               "share_basis": {"split": None, "divergence": None, "unconfirmed_split_facts": []}}
    rec = {"ticker": "TST", "numbers": numbers, "judgment": {}, "ttm": {}, "prices": {"daily_1y": [], "weekly": []}}
    out = B.trim_record(rec)
    assert set(out["numbers"]) == {"base_oe_per_share", "market_cap_basis", "share_scale"}, sorted(out["numbers"])
    assert set(B.TRIM_NUMBERS_KEYS) == {"used_tags", "capex_provenance", "sbc_provenance", "share_basis"}
    assert "judgment" not in out and "ttm" not in out and "daily_1y" not in out["prices"]
    assert rec["numbers"] is numbers and len(numbers) == 7  # the site record is not modified


def test_attachment_prerendered():
    node = shutil.which("node") or ("/usr/bin/node" if os.path.isfile("/usr/bin/node") else None)
    shell = os.path.join(BASE, "_daily", "site")
    if not node or not os.path.isfile(os.path.join(shell, "app.js")):
        print("  (skipped: needs node and the app shell)")
        return
    with TempBase() as tb:
        os.makedirs(tb.site, exist_ok=True)
        for f in ("index.html", "app.css", "app.js"):
            shutil.copy(os.path.join(shell, f), os.path.join(tb.site, f))
        # engine 5.7 (R3; rebase B14): a record with declared facts renders them in the static layer too
        tb.write_json("APP", "facts.json", obj=dict(_example(os.path.join("facts", "TST", "facts.json")), ticker="APP"))
        res = tb.build(attachment=True, top=2)
        assert res["prerender"] and "sections" in res["prerender"], res["prerender"]
        with open(res["attachment"][0], encoding="utf-8") as f:
            doc = f.read()
        assert 'id="static"' in doc and "getElementById('static')" in doc  # the layer + its JS-on cleanup script
        assert "window.SITE_DATA=" in doc  # the interactive app still boots from the same payload
        static_only = re.sub(r"<script>.*?</script>", "", doc, flags=re.S)  # what a no-JS viewer is left with
        assert 'data-ticker="APP"' in static_only and "$376.12" in static_only  # ranking row + IV@15 as plain text
        assert 'id="c-APP"' in static_only and 'data-pane="forecast"' in static_only  # company page, every tab pane
        assert 'name="prtf"' in static_only and "Loading the ranking" not in static_only  # CSS tier filter, no dead card
        # static nav is radios + labels with no fragment anchors (2026-10-20:
        # the iOS chat viewer ignores fragment navigation — taps were dead)
        assert 'href="#c-' not in static_only and ":target" not in static_only
        assert 'name="conav"' in static_only and 'id="co-list"' in static_only and 'id="co-APP"' in static_only  # the nav radio group
        assert '<label for="co-APP"' in static_only and '<label class="back" for="co-list"' in static_only  # row link + back control
        assert "#static #co-APP:checked ~ .page#c-APP{display:block}" in static_only  # generated per-company show rule
        # engine 5.7 (B14): the kind / form chips are JS-only (dead taps in the iOS viewer) — hidden; every row stays
        assert "#static .fchips{display:none}" in static_only
        assert "Declared facts" in static_only and 'id="fact-F1"' in static_only, "a record with facts renders them statically"
        res2 = tb.build(attachment=True, top=2, prerender=False)
        assert res2["prerender"] is None
        with open(res2["attachment"][0], encoding="utf-8") as f:
            assert 'id="static"' not in f.read()


def test_incremental_skip_touch_remove():
    with TempBase() as tb:
        first = tb.build()
        assert sorted(first["written"]) == sorted(TICKERS)
        second = tb.build()
        assert second["written"] == [] and sorted(second["skipped"]) == sorted(TICKERS) and second["removed"] == []
        assert [r["ticker"] for r in tb.read("index.json")] == ["APP", "KR", "ZS", "AEE"]
        # touch one folder file -> only that record rebuilds
        target = os.path.join(tb.dir, "KR", "analysis.md")
        rec_mtime = os.path.getmtime(os.path.join(tb.site, "data", "KR.json"))
        os.utime(target, (time.time() + 5, max(rec_mtime, time.time()) + 5))
        third = tb.build()
        assert third["written"] == ["KR"], third["written"]
        assert sorted(third["skipped"]) == ["AEE", "APP", "ZS"]
        assert tb.record("KR")["built_from_mtime"] >= os.path.getmtime(target)
        # --force rebuilds everything
        forced = tb.build(force=True)
        assert sorted(forced["written"]) == sorted(TICKERS)
        # a folder that no longer qualifies: its record is removed and listed
        os.remove(os.path.join(tb.dir, "AEE", "score.json"))
        fourth = tb.build()
        assert fourth["removed"] == ["AEE"] and "AEE" not in fourth["written"]
        assert not os.path.exists(os.path.join(tb.site, "data", "AEE.json"))
        assert [r["ticker"] for r in tb.read("index.json")] == ["APP", "KR", "ZS"]
        assert tb.read("meta.json")["counts"]["current"] == 3
        # a pre-v5 run lands in meta.stale, never in the index
        n_path = os.path.join(tb.dir, "ZS", "dcf_numbers.json")
        with open(n_path, encoding="utf-8") as f:
            n = json.load(f)
        n["engine_version"] = 4
        with open(n_path, "w", encoding="utf-8") as f:
            json.dump(n, f)
        fifth = tb.build()
        assert fifth["removed"] == ["ZS"]
        meta = tb.read("meta.json")
        assert [s["ticker"] for s in meta["stale"]] == ["ZS"] and meta["counts"]["stale"] == 1
        assert set(meta["stale"][0]) == {"ticker", "name", "tier", "irr", "analysis_date", "watchlist"}
        assert [r["ticker"] for r in tb.read("index.json")] == ["APP", "KR"]


def test_cli():
    with TempBase() as tb:
        env = dict(os.environ, STOCKS_BASE=tb.dir, PYTHONIOENCODING="utf-8")
        cmd = [sys.executable, os.path.join(SYS, "build_site.py"), "--only", ONLY, "--site-dir", tb.site]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        assert p.returncode == 0, p.stderr
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        assert len(lines) == 1 and lines[0].startswith("build_site: 4 written / 0 skipped / 0 removed"), p.stdout
        assert "largest record" in lines[0]
        q = subprocess.run(cmd + ["--quiet", "--attachment", "--top", "1"], capture_output=True, text=True, env=env)
        assert q.returncode == 0 and q.stdout.strip() == "", q.stdout
        assert os.path.exists(os.path.join(tb.dir, "_daily", "latest.html"))
        hist = os.listdir(os.path.join(tb.dir, "_daily", "history"))
        assert len(hist) == 1 and hist[0].startswith("ranking-") and hist[0].endswith(".csv"), hist


def test_watchlist_flag():
    with TempBase() as tb:
        res = tb.build()
        meta, index = tb.read("meta.json"), tb.read("index.json")
        wl = meta["watchlist"]
        # file order (2026-10-15: meta.watchlist keeps _system/watchlist.json's order; meta.watchlist_outside = not in the universe)
        file_order = [e["ticker"].upper() for e in B.jload(os.path.join(tb.dir, "_system", "watchlist.json"))["tickers"]]
        assert wl == list(dict.fromkeys(file_order)) and all(t == t.upper() for t in wl) and "APP" in wl, wl  # APP is in watchlist.json
        assert res["watchlist"] == wl
        assert isinstance(meta["watchlist_outside"], list) and all(t in wl for t in meta["watchlist_outside"])
        assert [e["ticker"] for e in meta["watchlist_entries"]] == wl
        flags = {r["ticker"]: r["watchlist"] for r in index}
        assert flags["APP"] is True and flags["KR"] is False, flags
        assert meta["counts"]["watchlist"] == sum(flags.values()) >= 1
        assert tb.record("APP")["row"]["watchlist"] is True and tb.record("KR")["row"]["watchlist"] is False
        assert any("watchlist" in n for n in meta["notes"])
        # a changed list re-flags every row on the next run WITHOUT rebuilding any record
        tb.write_json("_system", "watchlist.json", obj={"tickers": [{"ticker": "kr "}, "ZS", {"ticker": None}, 7]})
        res2 = tb.build()
        assert res2["written"] == [] and sorted(res2["skipped"]) == sorted(TICKERS)
        meta2, index2 = tb.read("meta.json"), tb.read("index.json")
        assert meta2["watchlist"] == ["KR", "ZS"] and meta2["counts"]["watchlist"] == 2
        assert {r["ticker"]: r["watchlist"] for r in index2} == {"APP": False, "KR": True, "ZS": True, "AEE": False}
        # the attachment carries the index row (authoritative) inside each embedded record
        att = tb.build(attachment=True, top=4)
        with open(att["attachment"][0], encoding="utf-8") as f:
            doc = f.read()
        start = doc.index("<script>window.SITE_DATA=") + len("<script>window.SITE_DATA=")
        data = json.loads(doc[start:doc.index(";</script>", start)])
        assert data["meta"]["watchlist"] == ["KR", "ZS"]
        assert data["records"]["KR"]["row"]["watchlist"] is True and data["records"]["APP"]["row"]["watchlist"] is False
        # a pre-v5 (stale) entry is flagged too; a missing / malformed watchlist file means an empty list
        n_path = os.path.join(tb.dir, "ZS", "dcf_numbers.json")
        n = B.jload(n_path)
        n["engine_version"] = 4
        tb.write_json("ZS", "dcf_numbers.json", obj=n)
        tb.build()
        assert [(s["ticker"], s["watchlist"]) for s in tb.read("meta.json")["stale"]] == [("ZS", True)]
        os.remove(os.path.join(tb.dir, "_system", "watchlist.json"))
        tb.build()
        meta4 = tb.read("meta.json")
        assert meta4["watchlist"] == [] and not any(r["watchlist"] for r in tb.read("index.json")) and meta4["stale"][0]["watchlist"] is False


def test_folder_ticker_mismatch_and_duplicate():
    with TempBase() as tb:
        tb.clone("APP", "APPX", ticker="xyz")  # served as XYZ: data/XYZ.json, row.ticker XYZ, record.folder APPX
        tb.clone("APP", "AAPP", ticker="APP")  # sorts BEFORE "APP" yet APP (the folder named after the ticker) must be served
        tb.clone("APP", "APP2", ticker="APP")  # a second folder claiming APP: ignored, reported
        only = TICKERS + ["XYZ"]
        res = tb.build(only=only, attachment=True, top=200)
        assert sorted(res["written"]) == sorted(only), res["written"]
        assert len(res["duplicates"]) == 2 and all("served from APP)" in d for d in res["duplicates"]), res["duplicates"]
        assert {d.split(" ")[0] for d in res["duplicates"]} == {"AAPP", "APP2"}
        assert os.path.exists(os.path.join(tb.site, "data", "XYZ.json"))
        for f in ("APPX", "APP2", "AAPP"):
            assert not os.path.exists(os.path.join(tb.site, "data", f"{f}.json")), f
        xyz = tb.record("XYZ")
        assert xyz["ticker"] == "XYZ" and xyz["folder"] == "APPX" and xyz["row"]["ticker"] == "XYZ"
        index = tb.read("index.json")
        assert sum(1 for r in index if r["ticker"] == "APP") == 1 and any(r["ticker"] == "XYZ" for r in index)
        assert next(r for r in index if r["ticker"] == "APP") == tb.record("APP")["row"]
        assert tb.record("APP")["folder"] == "APP"
        meta = tb.read("meta.json")
        assert any("duplicate" in n and "APP2" in n for n in meta["notes"])
        assert meta["counts"]["current"] == 5
        # the attachment embeds XYZ (looked up by the served key, not the folder)
        path, size, n = res["attachment"]
        assert n == 5
        with open(path, encoding="utf-8") as f:
            doc = f.read()
        start = doc.index("<script>window.SITE_DATA=") + len("<script>window.SITE_DATA=")
        data = json.loads(doc[start:doc.index(";</script>", start)])
        assert "XYZ" in data["records"] and data["records"]["XYZ"]["folder"] == "APPX" and sorted(data["embedded"]) == sorted(only)
        # incremental: XYZ is keyed consistently in state.json and skipped unchanged
        res2 = tb.build(only=only)
        assert res2["written"] == [] and sorted(res2["skipped"]) == sorted(only)
        assert "XYZ" in tb.read("state.json")["records"] and "APPX" not in tb.read("state.json")["records"]
        # --only accepts the folder name as well as the served ticker
        res3 = tb.build(only=["APPX"], force=True)
        assert res3["written"] == ["XYZ"], res3["written"]
        # a duplicate folder disappearing changes nothing; once the served folder goes, the
        # remaining claimant (first by name) takes over the key and APP is rebuilt from it
        shutil.rmtree(os.path.join(tb.dir, "APP2"))
        assert tb.build(only=only)["written"] == []
        shutil.rmtree(os.path.join(tb.dir, "APP"))
        res4 = tb.build(only=only)
        assert res4["written"] == ["APP"] and res4["removed"] == [] and tb.record("APP")["folder"] == "AAPP", res4["summary"]


def test_malformed_folders_never_abort():
    """Every shape the reviewers crashed the builder with, in one base."""
    with TempBase() as tb:
        inf_csv = lambda txt: txt.replace("\n", "\n", 1).split("\n")  # noqa: E731 — placeholder, replaced below
        bad = {}
        bad["BADNUM"] = tb.clone("APP", "BADNUM", **{"dcf_numbers.json": lambda n: [1, 2]})          # numbers not an object
        bad["BADSCN"] = tb.clone("APP", "BADSCN", **{"dcf_numbers.json": lambda n: {**n, "scenarios": [1], "hurdle_prices": [1], "inputs": "x",
                                                                                    "diagnostics": 3, "weighted": [], "growth_components": None}})
        bad["BADLIVE"] = tb.clone("APP", "BADLIVE", **{"live.json": lambda lv: {**lv, "scenarios": [1, 2], "tier": 9}})
        nan_score = lambda s: {**s, "price": float("nan"), "market_cap_b": float("inf"), "tier_bear": ["x"], "overrides": "capex",  # noqa: E731
                               "fragility_flags": "STALE_FY", "second_pass": [1], "override_impact": [1]}
        bad["BADNAN"] = tb.clone("APP", "BADNAN", **{"score.json": nan_score})
        def csv_inf(txt):
            lines = txt.split("\n")
            cols = lines[0].split(",")
            cells = lines[1].split(",")
            cells[cols.index("revenue")] = "1e400"
            lines[1] = ",".join(cells)
            return "\n".join(lines)
        bad["BADCSV"] = tb.clone("APP", "BADCSV", **{"financials_history.csv": csv_inf})
        bad["BADFUND"] = tb.clone("APP", "BADFUND", **{"fundamentals.json": lambda f: {**f, "dividends": [1]}, "prices.json": lambda p: {**p, "stats": [], "weekly": {}}})
        # score.json not an object: not scored at all (neither current nor stale)
        os.makedirs(os.path.join(tb.dir, "BADSTR"))
        tb.write_json("BADSTR", "score.json", obj="hello")
        shutil.copy(os.path.join(tb.dir, "APP", "dcf_numbers.json"), os.path.join(tb.dir, "BADSTR", "dcf_numbers.json"))
        only = TICKERS + sorted(bad)
        res = tb.build(only=only + ["BADSTR"])
        assert res["failed"] == [], res["failed"]
        built = sorted(res["written"])
        assert built == sorted(TICKERS + ["BADSCN", "BADLIVE", "BADNAN", "BADCSV", "BADFUND"]), built
        index, meta = strict_json(os.path.join(tb.site, "index.json")), strict_json(os.path.join(tb.site, "meta.json"))
        assert [s["ticker"] for s in meta["stale"]] == ["BADNUM"]  # numbers unreadable -> treated like a pre-v5 run
        assert not any(r["ticker"] == "BADSTR" for r in index) and "BADSTR" not in [s["ticker"] for s in meta["stale"]]
        for t in built:
            rec = strict_json(os.path.join(tb.site, "data", f"{t}.json"))  # strict: no NaN / Infinity anywhere
            _check_types(rec["row"], ROW_KEYS, t)
            assert rec["row"] == next(r for r in index if r["ticker"] == t)
        scn = tb.record("BADSCN")
        assert scn["forecast"]["paths"] is None and scn["forecast"]["growth_paths"] is None and scn["forecast"]["hurdle_prices"] is None
        assert scn["forecast"]["sensitivity"] is None or isinstance(scn["forecast"]["sensitivity"]["bear"]["irr"], float)  # score.scenarios may still carry IRRs
        assert scn["forecast"]["inputs"] is None and scn["forecast"]["growth_components"] == {} and scn["row"]["tier"] == "B"
        assert scn["row"]["iv20"] == B.num(scn["live"]["iv_at_20"]) and scn["row"]["irr_bear"] is not None  # live fallback; score.irr_bear still read
        lv = tb.record("BADLIVE")
        assert lv["row"]["has"]["live"] and lv["row"]["irr_live"] is not None and lv["row"]["tier_live"] == lv["row"]["tier"]
        assert lv["forecast"]["sensitivity"]["weighted"]["irr_live"] is not None and lv["forecast"]["sensitivity"]["bear"]["irr_live"] is None
        nan = tb.record("BADNAN")
        assert nan["row"]["price"] is None and nan["row"]["market_cap_b"] is None and nan["score"]["price"] is None and nan["score"]["market_cap_b"] is None
        assert nan["row"]["overrides"] == [] and nan["row"]["second_pass"] is None and nan["row"]["tier_bear"] in "SABCDF"
        assert nan["row"]["flags"] == [str(f) for f in nan["numbers"]["fragility_flags"]]  # score's string -> numbers' list
        csvr = tb.record("BADCSV")
        assert csvr["history"][0]["revenue"] is None and csvr["history"][1]["revenue"] is not None
        fr = tb.record("BADFUND")
        assert fr["row"]["has"]["dividends"] is False and fr["row"]["dividend_yield"] is None and fr["row"]["ret_1y_pct"] is None
        assert fr["prices"]["stats"] == {} and fr["prices"]["weekly"] == []


def test_build_failure_is_isolated():
    with TempBase() as tb:
        first = tb.build()
        assert sorted(first["written"]) == sorted(TICKERS)
        kr_before = tb.record("KR")
        os.utime(os.path.join(tb.dir, "KR", "analysis.md"), (time.time() + 5, time.time() + 5))  # KR must rebuild
        os.utime(os.path.join(tb.dir, "ZS", "analysis.md"), (time.time() + 5, time.time() + 5))  # so must ZS
        real = B.build_record

        def boom(c, *a, **kw):
            if c.get("ticker") == "KR":
                raise RuntimeError("synthetic")
            return real(c, *a, **kw)

        B.build_record = boom
        try:
            second = tb.build()
        finally:
            B.build_record = real
        assert second["failed"] == ["KR"] and second["written"] == ["ZS"] and sorted(second["skipped"]) == ["AEE", "APP"]
        index, meta = tb.read("index.json"), tb.read("meta.json")
        assert [r["ticker"] for r in index] == ["APP", "KR", "ZS", "AEE"]  # KR kept its previous row
        assert next(r for r in index if r["ticker"] == "KR") == kr_before["row"]
        assert tb.record("KR") == kr_before  # and its previous record
        assert meta["failed"] == ["KR"] and meta["counts"]["failed"] == 1 and any("FAILED" in n and "KR" in n for n in meta["notes"])
        assert "FAILED [KR]" in second["summary"]
        # the failure is not remembered as a successful build: KR rebuilds on the next run
        third = tb.build(now=datetime.datetime.now(B.NY) + datetime.timedelta(minutes=1))
        assert third["written"] == ["KR"] and third["failed"] == [], third
        assert tb.record("KR")["built_at"] != kr_before["built_at"]
        # a folder with no previous record simply has no row this run
        tb.clone("APP", "NEWCO")
        B.build_record = lambda c, *a, **kw: (_ for _ in ()).throw(RuntimeError("x")) if c.get("ticker") == "NEWCO" else real(c, *a, **kw)
        try:
            fourth = tb.build(only=TICKERS + ["NEWCO"])
        finally:
            B.build_record = real
        assert fourth["failed"] == ["NEWCO"] and not any(r["ticker"] == "NEWCO" for r in tb.read("index.json"))
        assert not os.path.exists(os.path.join(tb.site, "data", "NEWCO.json"))


def test_deleted_file_rebuilds():
    with TempBase() as tb:
        tb.build()
        app = tb.record("APP")
        assert app["row"]["has"]["live"] and app["live"] is not None
        os.remove(os.path.join(tb.dir, "APP", "live.json"))
        res = tb.build()
        assert res["written"] == ["APP"], res["written"]
        app2 = tb.record("APP")
        assert app2["live"] is None and app2["row"]["has"]["live"] is False and app2["row"]["irr_live"] is None and app2["row"]["price_live"] is None
        assert "live.json" not in app2["files"] and tb.read("state.json")["records"]["APP"]["files"] == app2["files"]
        index = tb.read("index.json")
        assert next(r for r in index if r["ticker"] == "APP")["irr_live"] is None
        assert B.rank_key(next(r for r in index if r["ticker"] == "APP"))[1] == -app2["row"]["irr"]  # ranked by the scored IRR now
        # unchanged again -> skipped; removing another optional file rebuilds again
        assert tb.build()["written"] == []
        os.remove(os.path.join(tb.dir, "APP", "segments.json"))
        res3 = tb.build()
        assert res3["written"] == ["APP"] and tb.record("APP")["segments"] is None and tb.record("APP")["row"]["has"]["segments"] is False
        # a state.json without file lists (older builder) rebuilds once, then settles
        st = tb.read("state.json")
        for e in st["records"].values():
            e.pop("files", None)
        tb.write_json("_daily", "site", "state.json", obj=st)
        assert sorted(tb.build()["written"]) == sorted(TICKERS)
        assert tb.build()["written"] == []


def test_scored_floor_flags_in_sensitivity():
    """Review 4289642893: the sensitivity block kept the scored IRR but dropped its
    floor flag while carrying the live one (ZS: live Bear '3.0% at floor' beside an
    unmarked scored 2.7%)."""
    E = B.ENGINE
    with TempBase() as tb:
        tb.build()
        zs = tb.record("ZS")
        sens, n = zs["forecast"]["sensitivity"], zs["numbers"]
        # ZS is a pre-5.4 run: no recorded scenario flags, so the replay decides
        assert all("irr_at_floor" not in n["scenarios"][k] for k in SCN[:-1])
        paths, _ = E.replay_paths(n)
        for k in SCN[:-1]:
            assert sens[k]["irr_at_floor"] is E.solve_irr(paths[k], n["price"], n["inputs"]["g_terminal"])[2], k
        assert sens["bear"]["irr_at_floor"] is True and sens["super_bear"]["irr_at_floor"] is True
        assert sens["base"]["irr_at_floor"] is False and sens["bull"]["irr_at_floor"] is False and sens["super_bull"]["irr_at_floor"] is False
        assert sens["weighted"]["irr_at_floor"] is False and zs["row"]["irr_at_floor"] is False
        # the historical scored IRR is kept, never replaced by the replay's 2.98%
        assert sens["bear"]["irr"] == n["scenarios"]["bear"]["irr"] == 0.027458705313011644
        assert sens["super_bear"]["irr"] == n["scenarios"]["super_bear"]["irr"]
        assert sens["bear"]["irr_live_at_floor"] is True  # its live counterpart, unchanged
        # recorded flags (engine 5.4) win over the replay, in both directions
        def flagged(nn):
            nn["scenarios"]["bear"]["irr_at_floor"] = False   # replay says True
            nn["scenarios"]["base"]["irr_at_floor"] = True    # replay says False
            nn["weighted"]["irr_at_floor"] = True
            return nn
        tb.clone("ZS", "ZSF", **{"dcf_numbers.json": flagged})
        tb.build(only=TICKERS + ["ZSF"])
        f = tb.record("ZSF")["forecast"]["sensitivity"]
        assert f["bear"]["irr_at_floor"] is False and f["base"]["irr_at_floor"] is True and f["super_bear"]["irr_at_floor"] is True
        assert f["weighted"]["irr_at_floor"] is True and tb.record("ZSF")["row"]["irr_at_floor"] is True
        # nothing recorded and nothing to replay (no inputs): unknown, not a guess
        def no_inputs(nn):
            nn.pop("inputs")
            return nn
        tb.clone("ZS", "ZSN", **{"dcf_numbers.json": no_inputs})
        tb.build(only=TICKERS + ["ZSN"])
        nrec = tb.record("ZSN")
        assert nrec["forecast"]["paths"] is None
        assert all(nrec["forecast"]["sensitivity"][k]["irr_at_floor"] is None for k in SCN), nrec["forecast"]["sensitivity"]
        assert nrec["row"]["irr_at_floor"] is False
    # unit: the helper itself
    flows = [1.0] * 15
    assert B.scored_floor((None, True), flows, 100.0, 0.025) is True
    assert B.scored_floor(("yes", None), [], 100.0, 0.025) is None
    assert B.scored_floor((), flows, 10_000.0, 0.025) is True and B.scored_floor((), flows, 1.0, 0.025) is False


def test_zero_terminal_growth_is_kept():
    """Review 4289642918: `or` treated g_terminal = 0.0 as missing and replayed with 2.5%."""
    assert B._gterm({"inputs": {"g_terminal": 0.0}, "g_terminal": 0.03}) == 0.0
    assert B._gterm({"inputs": {}, "g_terminal": 0.0}) == 0.0
    assert B._gterm({"inputs": {"g_terminal": None}, "g_terminal": 0.01}) == 0.01
    assert B._gterm({}) == 0.025 and B._gterm({"inputs": "x", "g_terminal": "nan"}) == 0.025
    E = B.ENGINE

    def zero_g(nn):
        nn["inputs"]["g_terminal"] = 0.0
        nn["g_terminal"] = 0.0
        return nn
    with TempBase() as tb:
        tb.clone("ZS", "ZSG", **{"dcf_numbers.json": zero_g})
        tb.build(only=TICKERS + ["ZSG"])
        rec = tb.record("ZSG")
        fc, n = rec["forecast"], rec["numbers"]
        assert fc["g_terminal"] == 0.0 and fc["replayed"] is True
        paths, _ = E.replay_paths(n)
        assert fc["paths"]["weighted"] == paths["weighted"]
        for rate in (0.20, 0.25):  # not stored by a pre-5.4 run: replayed with the run's own 0.0
            want = E.present_value(paths["weighted"], rate, 0.0)
            assert fc["hurdle_prices"][str(int(rate * 100))] == want, (rate, fc["hurdle_prices"])
            assert want != E.present_value(paths["weighted"], rate, 0.025)  # the old fallback gave a different price
            for k in SCN:
                assert fc["sensitivity"][k][str(int(rate * 100))] == E.present_value(paths[k], rate, 0.0), (k, rate)
        for k in SCN[:-1]:  # the floor replay uses 0.0 too
            assert fc["sensitivity"][k]["irr_at_floor"] is E.solve_irr(paths[k], n["price"], 0.0)[2], k
        assert rec["row"]["iv20"] == fc["hurdle_prices"]["20"]


STREET = {"source": "Nasdaq analyst endpoints", "as_of": "2026-10-16", "consensus": "Buy", "analysts": 9, "buy": 7, "hold": 2, "sell": 0,
          "target_mean": 300.0, "target_low": 250.0, "target_high": 350.0, "history": [{"date": "2026-10", "mean_target": 300.0, "buy": 7, "hold": 2, "sell": 0}]}
MARKET = {"exchange": "NASDAQ-GS", "average_volume": 1000, "volume": 900, "market_cap_nasdaq": 35000000000, "high_52w": 336.99, "low_52w": 114.6}


def street_file(**over):
    d = {"ticker": "ZS", "cik": 1713683, "as_of": "2026-10-16", "fetched_at": "2026-10-16T18:01:02-04:00",
         "source": "Nasdaq analyst and quote endpoints", "street": STREET, "market": MARKET,
         "sources": {"nasdaq_ratings": "https://api.nasdaq.com/api/analyst/ZS/ratings"}, "warnings": []}
    d.update(over)
    return d


def test_street_json_merged_into_profile():
    with TempBase() as tb:
        prof_path = os.path.join(tb.dir, "ZS", "profile.json")
        legacy = B.jload(prof_path)
        legacy.update({"street": {**STREET, "consensus": "Hold", "as_of": "2026-10-01"}, "market": {**MARKET, "volume": 1},
                       "fetched_at": "2026-10-01T06:00:00-04:00"})
        tb.write_json("ZS", "profile.json", obj=legacy)
        # (1) legacy profile.json, no street.json: its own street / market, its fetched_at
        tb.build()
        p = tb.record("ZS")["profile"]
        assert p["street"]["consensus"] == "Hold" and p["market"]["volume"] == 1 and p["street_fetched_at"] == "2026-10-01T06:00:00-04:00"
        assert p.get("about") == legacy.get("about") and p.get("filings") == legacy.get("filings") and p["ticker"] == "ZS"
        # (2) street.json wins over the legacy keys; only ZS rebuilds (an ordinary folder file)
        tb.write_json("ZS", "street.json", obj=street_file())
        rec_mtime = os.path.getmtime(os.path.join(tb.site, "data", "ZS.json"))
        st_path = os.path.join(tb.dir, "ZS", "street.json")
        os.utime(st_path, (rec_mtime + 5, rec_mtime + 5))
        res = tb.build()
        assert res["written"] == ["ZS"] and sorted(res["skipped"]) == ["AEE", "APP", "KR"], res["summary"]
        rec = tb.record("ZS")
        p = rec["profile"]
        assert p["street"] == STREET and p["market"] == MARKET and p["street_fetched_at"] == "2026-10-16T18:01:02-04:00"
        assert p.get("about") == legacy.get("about") and p["fetched_at"] == legacy["fetched_at"] and rec["row"]["has"]["profile"] is True
        assert "street.json" in rec["files"]
        # unchanged -> skipped; a re-pulled street.json (newer mtime) rebuilds ZS again
        assert tb.build()["written"] == []
        tb.write_json("ZS", "street.json", obj=street_file(street={**STREET, "analysts": 10}, fetched_at="2026-10-17T18:00:00-04:00"))
        os.utime(st_path, (rec_mtime + 10, rec_mtime + 10))
        assert tb.build()["written"] == ["ZS"] and tb.record("ZS")["profile"]["street"]["analysts"] == 10
        # (3) a new pull with no coverage (street: null) is not overridden by the older profile.json block
        tb.write_json("ZS", "street.json", obj=street_file(street=None))
        os.utime(st_path, (rec_mtime + 15, rec_mtime + 15))
        tb.build()
        p = tb.record("ZS")["profile"]
        assert p["street"] is None and p["market"] == MARKET and p["street_fetched_at"] == "2026-10-16T18:01:02-04:00"
        # (4) the new profile.json shape (no street / market keys) without street.json -> null, about kept
        new_prof = {k: v for k, v in legacy.items() if k not in ("street", "market")}
        tb.write_json("ZS", "profile.json", obj=new_prof)
        os.remove(st_path)
        assert tb.build()["written"] == ["ZS"]  # the deleted street.json rebuilds the record
        p = tb.record("ZS")["profile"]
        assert p["street"] is None and p["market"] is None and p["street_fetched_at"] is None and p.get("about") == legacy.get("about")
        # (5) a malformed street.json counts as absent; street.json without profile.json still serves the Street
        tb.write_json("ZS", "street.json", obj=[1, 2])
        os.utime(st_path, (rec_mtime + 20, rec_mtime + 20))
        tb.build()
        assert tb.record("ZS")["profile"]["street"] is None
        os.remove(prof_path)
        tb.write_json("ZS", "street.json", obj=street_file())
        os.utime(st_path, (rec_mtime + 25, rec_mtime + 25))
        tb.build()
        rec = tb.record("ZS")
        assert rec["profile"] == {"street": STREET, "market": MARKET, "street_fetched_at": "2026-10-16T18:01:02-04:00"}
        assert rec["row"]["has"]["profile"] is False
        # the attachment keeps record.profile (with the merged Street)
        att = tb.build(attachment=True, top=4)
        with open(att["attachment"][0], encoding="utf-8") as f:
            doc = f.read()
        start = doc.index("<script>window.SITE_DATA=") + len("<script>window.SITE_DATA=")
        data = json.loads(doc[start:doc.index(";</script>", start)])
        assert data["records"]["ZS"]["profile"]["street"] == STREET
    # unit: neither file -> None
    assert B.profile_with_street(None, None) is None and B.profile_with_street("x", [1]) is None


def test_missing_outputs_fresh_clone():
    """A fresh clone has no caches and no _daily/; a machine may lose data/ while state.json
    and index.json still claim the records exist."""
    with TempBase(caches=False) as tb:
        assert not os.path.exists(os.path.join(tb.dir, "_daily"))
        for t in TICKERS:
            assert not any(os.path.exists(os.path.join(tb.dir, t, f)) for f in CACHE_FILES)
        res = tb.build(attachment=True)
        assert sorted(res["written"]) == sorted(TICKERS) and res["failed"] == []
        meta, index = tb.read("meta.json"), tb.read("index.json")
        assert meta["counts"]["current"] == 4 and meta["counts"]["with_live"] == 0 and len(index) == 4
        for r in index:
            assert r["has"]["prices"] is False and r["has"]["live"] is False and r["irr_live"] is None and r["price_live"] is None
            rec = tb.record(r["ticker"])
            assert rec["prices"] is None and rec["live"] is None
            if rec["forecast"]["sensitivity"]:
                assert all(v["irr_live"] is None and v["irr_live_at_floor"] is None for v in rec["forecast"]["sensitivity"].values())
        assert [r["ticker"] for r in index] == ["APP", "KR", "ZS", "AEE"]  # scored IRR order without live data
        assert tb.record("ZS")["forecast"]["sensitivity"]["bear"]["irr_at_floor"] is True  # needs no cache
        assert os.path.exists(res["history"][0]) and os.path.exists(res["attachment"][0])
        # data/ deleted while state.json and index.json survive: everything is rebuilt
        shutil.rmtree(os.path.join(tb.site, "data"))
        assert os.path.exists(os.path.join(tb.site, "state.json")) and os.path.exists(os.path.join(tb.site, "index.json"))
        res2 = tb.build()
        assert sorted(res2["written"]) == sorted(TICKERS), res2["summary"]
        # one record deleted -> only that one is rebuilt
        os.remove(os.path.join(tb.site, "data", "ZS.json"))
        res3 = tb.build()
        assert res3["written"] == ["ZS"] and sorted(res3["skipped"]) == ["AEE", "APP", "KR"]
        # outside --only too: a missing record is built so the index keeps every company
        os.remove(os.path.join(tb.site, "data", "KR.json"))
        res4 = tb.build(only=["APP"])
        assert res4["written"] == ["KR"] and res4["missing_outside_only"] == ["KR"] and sorted(res4["skipped"]) == ["AEE", "APP", "ZS"]
        assert sorted(r["ticker"] for r in tb.read("index.json")) == sorted(TICKERS)
        assert any("outside --only" in n and "KR" in n for n in tb.read("meta.json")["notes"])
        assert tb.build(only=["APP"])["written"] == []  # settled
        # meta.json / index.json are always written: removed, they come back on a run that builds nothing
        os.remove(os.path.join(tb.site, "meta.json"))
        os.remove(os.path.join(tb.site, "index.json"))
        res5 = tb.build()
        assert sorted(res5["written"]) == sorted(TICKERS)  # no index rows to reuse -> rebuilt, never served empty
        assert len(tb.read("index.json")) == 4 and tb.read("meta.json")["counts"]["current"] == 4
        assert tb.build()["written"] == []
        os.remove(os.path.join(tb.site, "meta.json"))
        assert tb.build()["written"] == [] and tb.read("meta.json")["counts"]["current"] == 4
        # unreadable / foreign-shaped state.json, index.json, queue.json, registry: treated as absent
        tb.write_json("_daily", "site", "state.json", obj=[1, 2])
        tb.write_json("_daily", "site", "index.json", obj=7)
        tb.write_json("_system", "queue.json", obj=[1])
        tb.write_json("_system", "overrides_registry.json", obj=["x"])
        res6 = tb.build()
        assert res6["written"] == [] and res6["failed"] == []  # rows and mtimes recovered from the records themselves
        meta = tb.read("meta.json")
        assert meta["sweep"]["total"] == 0 and [r["ticker"] for r in tb.read("index.json")] == ["APP", "KR", "ZS", "AEE"]
        # state.json entries for tickers that are no longer current are dropped
        st = tb.read("state.json")
        st["records"]["GONE"] = {"built_from_mtime": 1.0, "builder_mtime": 1.0, "files": []}
        tb.write_json("_daily", "site", "state.json", obj=st)
        tb.build()
        assert "GONE" not in tb.read("state.json")["records"] and sorted(tb.read("state.json")["records"]) == sorted(TICKERS)


def _read_csv(path):
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    import csv as _csv
    return raw, list(_csv.reader(text.splitlines()))


def test_history_csv():
    now = datetime.datetime(2026, 10, 16, 19, 7, tzinfo=B.NY)
    with TempBase() as tb:
        res = tb.build(attachment=True, now=now)
        path, n = res["history"]
        assert path == os.path.join(tb.dir, "_daily", "history", "ranking-2026-10-16.csv") and n == 4
        assert os.path.basename(res["attachment"][0]) == "ranking-2026-10-16.html"  # the same date as the attachment
        raw, rows = _read_csv(path)
        assert b"\r" not in raw and raw.endswith(b"\n") and not raw.startswith(b"\xef\xbb\xbf")
        header, body = rows[0], rows[1:]
        assert tuple(header) == B.HISTORY_COLUMNS
        assert [r[1] for r in body] == ["APP", "KR", "ZS", "AEE"] and [r[0] for r in body] == ["1", "2", "3", "4"]
        by = {r[1]: dict(zip(header, r)) for r in body}
        idx = {r["ticker"]: r for r in tb.read("index.json")}
        zs, z = by["ZS"], idx["ZS"]
        assert zs["name"] == "Zscaler Inc" and zs["sector_misfit"] == "false" and zs["tier_scored"] == "D" and zs["tier_live"] == "D"
        assert zs["irr_scored"] == "0.032600" and zs["irr_live"] == f"{z['irr_live']:.6f}" == "0.032836"
        assert zs["band_low_tier"] == z["tier_bear_live"] == "D" and zs["band_high_tier"] == z["tier_bull_live"] == "D"
        assert zs["price"] == "220.79" and zs["price_date"] == "2026-10-14" and zs["iv15"] == "11.14"
        assert zs["upside15_pct"] == f"{z['upside15_live']:.2f}" == "-94.95"
        assert zs["analysis_date"] == "2026-10-14" and zs["engine_release"] == "" and zs["alert_eligible"] == "false"
        assert by["APP"]["watchlist"] == "true" and by["KR"]["watchlist"] == "false"
        aee = by["AEE"]  # Tier F: no IRRs -> last, blanks (never "None" / "nan")
        assert aee["tier_scored"] == "F" and aee["irr_scored"] == "" and aee["irr_live"] == "" and aee["tier_live"] == ""
        assert aee["price"] == f"{idx['AEE']['price']:.2f}" and aee["price_date"] == idx["AEE"]["analysis_date"]
        for r in body:
            assert len(r) == len(header)
            assert not any(v in ("None", "null", "nan", "inf", "-0.000000") for v in r), r
        # deterministic: an identical run writes identical bytes; the same day's file is overwritten
        tb.build(attachment=True, now=now)
        assert _read_csv(path)[0] == raw
        tb.write_json("_system", "watchlist.json", obj={"tickers": ["KR"]})
        tb.build(attachment=True, now=now)
        assert os.listdir(os.path.dirname(path)) == ["ranking-2026-10-16.csv"]
        wcol = B.HISTORY_COLUMNS.index("watchlist")  # engine 5.7 appended columns after watchlist (no longer the last)
        assert {r[1]: r[wcol] for r in _read_csv(path)[1][1:]} == {"APP": "false", "KR": "true", "ZS": "false", "AEE": "false"}
        # a --site-dir build writes next to that directory, never into the real _daily/history
        other = os.path.join(tb.dir, "scratch", "site")
        res2 = B.build(base=tb.dir, site_dir=other, only=TICKERS, attachment=True, quiet=True, now=now)
        assert res2["history"][0] == os.path.join(tb.dir, "scratch", "history", "ranking-2026-10-16.csv")
    # ordering: live IRR desc, then scored IRR desc, then ticker; nulls after values; no "-0.000000"
    rows = [{"ticker": "B", "irr_live": 0.10, "irr": 0.05, "price_live": 1.0}, {"ticker": "A", "irr_live": 0.10, "irr": 0.05, "price_live": 1.0},
            {"ticker": "C", "irr_live": 0.10, "irr": 0.09, "price_live": 1.0}, {"ticker": "D", "irr_live": None, "irr": 0.50},
            {"ticker": "E", "irr_live": None, "irr": None}, {"ticker": "F", "irr_live": 0.20, "irr": None, "price_live": 1.0},
            {"ticker": "G", "irr_live": None, "irr": -1e-9, "name": "Comma, Inc", "fit": "misfit", "price": 1234.5}]
    out = B.history_rows(rows)
    assert [r[1] for r in out] == ["F", "C", "A", "B", "D", "G", "E"], [r[1] for r in out]
    g = dict(zip(B.HISTORY_COLUMNS, out[5]))
    assert g["irr_scored"] == "0.000000" and g["sector_misfit"] == "true" and g["price"] == "1234.50" and g["name"] == "Comma, Inc"


# ---------------- 14. dividends at the latest close
def _json(o):
    return json.loads(json.dumps(o))


def _isclose(a, b, rel=1e-12):
    return a is not None and b is not None and abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def _set_close(tb, t, last, last_date):
    p = B.jload(os.path.join(tb.dir, t, "prices.json"))
    p["stats"] = dict(p.get("stats") or {}, last=last, last_date=last_date)
    tb.write_json(t, "prices.json", obj=p)


def test_dividends_block_repriced_at_a_newer_close():
    with TempBase() as tb:
        fpath = os.path.join(tb.dir, "KR", "fundamentals.json")
        fund = B.jload(fpath)
        # the committed block, on a known close (whatever close the file was last written at) that prices.json also has
        committed = _json(F.price_dividends(fund["dividends"], 63.09, "2026-10-14", "prices.json stats.last"))
        tb.write_json("KR", "fundamentals.json", obj=dict(fund, dividends=committed))
        _set_close(tb, "KR", 63.09, "2026-10-14")
        assert committed["dps_ttm"] and committed["shares_outstanding"]
        tb.build()
        assert tb.record("KR")["fundamentals"]["dividends"] == committed, "the close the block already has: shown as written"
        # a newer close: the block fundamentals.py would write at that close
        _set_close(tb, "KR", 70.0, "2026-10-16")
        assert tb.build()["written"] == ["KR"]
        rec = tb.record("KR")
        d, row = rec["fundamentals"]["dividends"], rec["row"]
        assert d == _json(F.price_dividends(committed, 70.0, "2026-10-16", "prices.json stats.last"))
        assert (d["price"], d["price_date"], d["price_source"], d["price_note"]) == (70.0, "2026-10-16", "prices.json stats.last", None)
        assert _isclose(d["dividend_yield"], committed["dps_ttm"] / 70.0)
        assert _isclose(d["market_cap"], 70.0 * committed["shares_outstanding"])
        assert _isclose(d["shareholder_yield"], committed["yield_basis"]["shareholder_yield"]["numerator"] / d["market_cap"])
        assert d["yield_basis"]["dividend_yield"]["denominator"] == "price 70.0 (prices.json stats.last)"
        assert d["yields_display"]["dividend_yield"]["label"] == f"{d['dividend_yield'] * 100:.2f}%"
        assert S.canonical({"dividends": d}, F.PRICE_LEAVES) == S.canonical({"dividends": committed}, F.PRICE_LEAVES), \
            "only the price leaves moved"
        assert (row["dividend_yield"], row["shareholder_yield"]) == (d["dividend_yield"], d["shareholder_yield"])
        assert row["shareholder_yield_label"] == d["yields_display"]["shareholder_yield"]["label"]
        assert row["shareholder_yield_bound"] == d["yields_display"]["shareholder_yield"]["bound"]
        assert B.jload(fpath)["dividends"] == committed, "the committed file is never touched"
        # an older close than the block's own: as written
        _set_close(tb, "KR", 50.0, "2026-10-01")
        tb.build()
        assert tb.record("KR")["fundamentals"]["dividends"] == committed
        # the same date: a different figure (the block came from score.json's analysis-time quote) reprices, the same one does not
        sc = dict(committed, price=63.5, price_source="score.json price")
        tb.write_json("KR", "fundamentals.json", obj=dict(B.jload(fpath), dividends=sc))
        _set_close(tb, "KR", 63.09, "2026-10-14")
        tb.build()
        d = tb.record("KR")["fundamentals"]["dividends"]
        assert d["price"] == 63.09 and d["price_source"] == "prices.json stats.last" and d["price_note"] is None
        tb.write_json("KR", "fundamentals.json", obj=dict(B.jload(fpath), dividends=committed))
        tb.build()
        assert tb.record("KR")["fundamentals"]["dividends"] == committed
        # a block written before 5.4.4 (no yields_display) is shown as written whatever the close
        old = {k: v for k, v in committed.items() if k != "yields_display"}
        tb.write_json("KR", "fundamentals.json", obj=dict(B.jload(fpath), dividends=old))
        _set_close(tb, "KR", 70.0, "2026-10-16")
        tb.build()
        assert tb.record("KR")["fundamentals"]["dividends"] == old
    # a fresh clone (no prices.json): as written
    with TempBase(caches=False) as tb:
        tb.build()
        assert tb.record("KR")["fundamentals"]["dividends"] == B.jload(os.path.join(tb.dir, "KR", "fundamentals.json"))["dividends"]
    assert B.priced_fundamentals(None, {"stats": {"last": 1.0, "last_date": "2026-10-16"}}) is None
    assert B.priced_fundamentals({"annual": []}, {"stats": {"last": 1.0, "last_date": "2026-10-16"}}) == {"annual": []}
    # the close as filed: a JSON number only (fundamentals._read_price reads the same value), else as written
    fund = B.jload(os.path.join(BASE, "KR", "fundamentals.json"))
    for bad in ("70.0", True, None, 0, -1.0, float("nan")):
        assert B.priced_fundamentals(fund, {"stats": {"last": bad, "last_date": "2099-01-01"}}) is fund, bad
    assert B.priced_fundamentals(fund, {"stats": {"last": 70.0, "last_date": "2099"}}) is fund, "no usable date"
    d = B.priced_fundamentals(fund, {"stats": {"last": 70, "last_date": "2099-01-01"}})["dividends"]
    assert d["market_cap_basis"].startswith("70 × ") and d["yield_basis"]["dividend_yield"]["denominator"] == "price 70 (prices.json stats.last)"


def test_priced_fundamentals_backfills_ads_ratio_into_legacy_blocks():
    """A dividends block written before blocks carried ads_ratio reprices on
    the traded-cap basis when the caller passes the run's recorded ratio
    (2026-10-18 ADS fix): KR's block with a passed ratio of 0.5 serves a
    market cap of price x shares / 0.5; without the pass it is the legacy
    price x shares, and a block that already carries a ratio keeps its own."""
    fund = B.jload(os.path.join(BASE, "KR", "fundamentals.json"))
    div = fund["dividends"]
    assert "ads_ratio" not in div, "the committed KR block is a legacy block for this test"
    legacy = B.priced_fundamentals(fund, {"stats": {"last": 70, "last_date": "2099-01-01"}})["dividends"]
    served = B.priced_fundamentals(fund, {"stats": {"last": 70, "last_date": "2099-01-01"}}, ads_ratio=0.5)["dividends"]
    assert served["market_cap"] == legacy["market_cap"] * 2, "ratio 0.5 doubles the traded cap"
    assert "ADS ratio 0.5" in served["market_cap_basis"]
    assert "ads_ratio" not in fund["dividends"], "the input is not modified"
    own = dict(fund, dividends=dict(div, ads_ratio=4.0))
    kept = B.priced_fundamentals(own, {"stats": {"last": 70, "last_date": "2099-01-01"}}, ads_ratio=0.5)["dividends"]
    assert kept["ads_ratio"] == 4.0 and kept["market_cap"] == legacy["market_cap"] / 4, "the block's own ratio wins"


def test_repriced_block_equals_what_fundamentals_writes_on_every_committed_folder():
    """Offline, on the committed SEC files themselves (no caches needed): for every folder whose
    fundamentals.json carries a dividends block, (1) price_dividends reproduces the committed block at
    its own price — it is the function the file was written with; (2) the block build_site serves at a
    newer close P equals price_dividends(core, P), core = the block without its price leaves — exactly
    what fundamentals.py writes at P, since build_dividends returns price_dividends(core, price); and
    (3) the two differ only in the volatile price leaves, so that close alone never rewrites the file."""
    n = 0
    for path in sorted(glob.glob(os.path.join(BASE, "*", "fundamentals.json"))):
        fund = B.jload(path)
        div = fund.get("dividends") if isinstance(fund, dict) else None
        if not isinstance(div, dict):
            continue
        assert F.repriceable(div), f"{path}: a committed block price_dividends cannot read"
        n += 1
        legacy = [x for x in div["notes"] if x.startswith("price: ")]  # written before 2026-10-16: the note is price_note now
        own = _json(F.price_dividends(div, div["price"], div["price_date"], div["price_source"]))
        if "price_note" in div:  # written from 2026-10-16 on
            assert not legacy and own == div, path
        else:
            assert own.pop("price_note") == (legacy[0] if legacy else None), path
            assert own == dict(div, notes=[x for x in div["notes"] if x not in legacy]), path
        core = S._strip({"dividends": div}, F.PRICE_LEAVES)["dividends"]
        assert not any(k in core for k in ("price", "price_date", "market_cap", "dividend_yield")), path
        for p, d in ((123.45, "2099-01-02"), ((div["price"] or 20.0) * 0.5, "2099-01-03")):
            served = B.priced_fundamentals(fund, {"stats": {"last": p, "last_date": d}})["dividends"]
            # ruling-sheet Q8 bug 3: priced in the block's own unit (a non-USD file carries no yields; a pre-rule block's unit is unrecorded)
            unit = B.dividends_unit(fund)
            cur = fund.get("currency") if fund.get("currency") not in (None, "USD") else None
            written = F.price_dividends(core, p, d, "prices.json stats.last", **unit)
            assert _json(served) == _json(written), (path, p)
            assert served["price"] == p and served["price_date"] == d and served["price_source"] == "prices.json stats.last"
            if cur is not None:
                assert all(served[k] is None for k in F.YIELD_KEYS), (path, "no cross-currency yield is served")
            if div["price"] is not None:  # a price present on both sides: only the volatile leaves differ
                ref = own if cur is None else _json(F.price_dividends(div, div["price"], div["price_date"], div["price_source"], **unit))
                assert S.canonical({"dividends": served}, F.PRICE_LEAVES) == S.canonical({"dividends": ref}, F.PRICE_LEAVES), (path, p)
        assert fund == B.jload(path), "nothing is modified in place"
    assert n >= 80, n


def test_priced_fundamentals_serves_no_cross_currency_yield():
    """Ruling-sheet Q8 bug 3 (Andrew, 2026-10-19): RDY's committed block printed a 310.80% dividend yield (Rs40 DPS
    over the $12.87 close). build_site prices the block in the file's own currency, so a non-USD file serves null
    yields at a newer close AND, for a block written before the rule, without one (re-priced at its own close);
    the market cap and the USD file are untouched."""
    fund = B.jload(os.path.join(BASE, "RDY", "fundamentals.json"))
    assert fund["currency"] == "INR"
    newer = B.priced_fundamentals(fund, {"stats": {"last": 13.0, "last_date": "2099-01-01"}})["dividends"]
    assert all(newer[k] is None for k in F.YIELD_KEYS) and newer["market_cap"] is not None
    note = newer["yields_display"]["dividend_yield"]["note"]
    assert ("not record the currency" in note and "INR" in note) if "currency" not in fund["dividends"] else "filed in INR" in note, note
    usd = B.jload(os.path.join(BASE, "KR", "fundamentals.json"))
    assert B.priced_fundamentals(usd, {}) is usd, "a USD file without a newer close is served as written"
    assert B.priced_fundamentals(usd, {"stats": {"last": 70, "last_date": "2099-01-01"}})["dividends"]["dividend_yield"] is not None

def _pre_rule_inr_fund():
    """An INR fundamentals.json whose dividends block was written BEFORE the Q8 currency rule (verifier round 1): its
    yields were computed across currencies (RDY's shape — Rs40 DPS over a $12.87 close, a 310.80% dividend yield). An
    inline fixture, so the test never depends on a committed file still being pre-rule."""
    annual = [{"fy": "2025", "period_end": "2025-03-31", "eps_diluted": 57.0, "dividends_paid": 3_400e6, "buybacks": None, "share_issuance": None,
               "oe_conservative": 15_000e6, "fcf": 16_000e6, "shares_diluted": 834e6}]
    ctx = {"filed_any": {"dividends_paid": True, "buybacks": False, "share_issuance": False},
           "shares_instant": (834_656_970, "2026-03-31", "ifrs-full:NumberOfSharesOutstanding"),
           "latest_filed_period": {}, "split_notes": [], "splits": [], "warnings": []}  # no ctx currency: the pre-rule block
    div = F.build_dividends(annual, [], {"declared": {}, "paid": {}}, {"declared": {}, "paid": {"2024-03-31": 40.0, "2025-03-31": 40.0}},
                            12.87, "2026-10-14", "prices.json stats.last", ctx)
    assert div["dividend_yield"] is not None and round(div["dividend_yield"] * 100, 2) == 310.80, div["dividend_yield"]
    return {"currency": "INR", "dividends": div}


def test_pre_rule_non_usd_block_loses_its_yields_on_every_serving_path():
    """Verifier round 1: the re-price of a pre-rule non-USD block at its own close was only tested behind
    `if RDY's committed file still carries a yield` (silently skipped after RDY's refresh), and build_record's
    split-since-scoring branch served the block as written — SKM's 11,076% dividend yield and TLK's 123.36%
    shareholder yield would reach the Dividends tab and the ranking row. Both paths now null the yields at the
    block's own price; the market cap, shares and price are the block's own."""
    fund = _pre_rule_inr_fund()
    div0 = fund["dividends"]
    for prices in ({}, {"stats": {"last": 13.0, "last_date": "2000-01-01"}}, {"stats": {"last": 12.87, "last_date": "2026-10-14"}}):
        served = B.priced_fundamentals(fund, prices)["dividends"]
        assert all(served[k] is None for k in F.YIELD_KEYS), (prices, {k: served[k] for k in F.YIELD_KEYS})
        assert served["price"] == div0["price"] and served["price_date"] == div0["price_date"] and served["market_cap"] == div0["market_cap"], prices
    assert fund["dividends"] is div0 and div0["dividend_yield"] is not None, "the loaded block is not modified"
    # the split-since-scoring branch (build_record serves the block as written, never repriced): no cross-currency yield either
    live = {"price": 6.5, "price_date": "2026-10-20", "scored_date": "2026-10-14", "irr_weighted": 0.12, "iv_at_15": 10.0,
            "iv_at_20": 8.0, "iv_at_25": 6.0, "split_factor": 2.0, "basis_check": {"factor": 2.0, "split": "2:1"}}
    c = {"folder": "T", "path": "", "ticker": "T", "score": {"ticker": "T", "price": 13.0, "iv_at_15": 20.0, "implied_irr": 0.12,
                                                            "analysis_date": "2026-10-14"},
         "numbers": {"engine_version": 5, "data_gap": [], "price": 13.0}, "live": live, "history": [], "files": [], "fund": fund}
    rec = B.build_record(c, {}, "2026-10-20T19:00:00-04:00", 0.0)
    d = rec["fundamentals"]["dividends"]
    assert all(d[k] is None for k in F.YIELD_KEYS), {k: d[k] for k in F.YIELD_KEYS}
    assert d["price"] == div0["price"] and d["market_cap"] == div0["market_cap"], "not repriced across the split: its own close"
    assert rec["row"]["dividend_yield"] is None and rec["row"]["shareholder_yield"] is None and rec["row"]["shareholder_yield_label"] == "—"
    # a USD block across a split is still served exactly as written
    usd = {"currency": "USD", "dividends": dict(div0)}
    assert B.cross_currency_safe(usd) is usd and B.build_record(dict(c, fund=usd), {}, "2026-10-20T19:00:00-04:00", 0.0)["fundamentals"]["dividends"] == div0


def test_pre_rule_non_usd_block_note_does_not_call_the_file_currency_the_legs_unit():
    """Verifier round 2 (TLK, CX, RDY, WIT, ZTO): a non-USD file's top-level `currency` written before the one-currency
    rule meant "some core fact was filed in another currency" — its dividend legs were read USD-first (CX's $90M is a USD
    fact, TLK's dividends paid the USD 1,099,000,000 one). build_site priced such a block with currency=<file currency>,
    so the yield note said "the numerator is filed in MXN". Only a block's own `currency` key names the legs' unit; a
    pre-rule block's note says the unit is not recorded (the yields stay null until the file's next refresh)."""
    div = dict(_pre_rule_inr_fund()["dividends"])
    cx = {"currency": "MXN", "dividends": div}
    assert B.dividends_unit(cx) == {"unit_unrecorded": "MXN"}
    for prices in ({}, {"stats": {"last": 13.0, "last_date": "2099-01-01"}}):
        served = B.priced_fundamentals(cx, prices)["dividends"]
        assert all(served[k] is None for k in F.YIELD_KEYS), prices
        notes = [v["note"] for v in served["yields_display"].values()]
        assert all("does not record the currency" in n and "MXN" in n for n in notes), notes
        assert not any("filed in MXN" in n for n in notes), notes
    # a block that records its unit (the new rule) keeps the plain cross-currency note; a USD file prices as before
    idr = {"currency": "IDR", "dividends": dict(div, currency="IDR")}
    assert B.dividends_unit(idr) == {"currency": "IDR"}
    n2 = B.priced_fundamentals(idr, {"stats": {"last": 13.0, "last_date": "2099-01-01"}})["dividends"]["yields_display"]["dividend_yield"]["note"]
    assert "the numerator is filed in IDR" in n2, n2
    assert B.dividends_unit({"currency": "USD", "dividends": div}) == {}


# ---------------- 15. split since scoring
def _split_live(live, factor=2.0, label="2:1"):
    """live.json as reprice.py writes it after a split since the scored run: every per-share value in
    today's units (÷ factor), the IRRs, upside and market cap unchanged."""
    lv = _json(live)
    for k in ("price", "scored_price", "iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25"):
        lv[k] = lv[k] / factor
    lv["split_factor"] = factor
    lv["basis_check"] = {"status": "split_adjusted", "factor": factor, "split": label, "method": "ratio",
                         "scored_price_raw": live["scored_price"], "scored_price_adjusted": live["scored_price"] / factor,
                         "scored_date": live["scored_date"]}
    return lv


def _at(rec, path):
    """{concrete path: number} for a dotted path with `*` (as SPLIT_DIVIDE spells them)."""
    out = {}

    def walk(o, parts, where):
        if not parts:
            if B.num(o) is not None:
                out[where] = B.num(o)
            return
        k, rest = parts[0], parts[1:]
        if isinstance(o, dict):
            for kk in (list(o) if k == "*" else [k] if k in o else []):
                walk(o[kk], rest, f"{where}.{kk}")
        elif isinstance(o, list) and k == "*":
            for i, v in enumerate(o):
                walk(v, rest, f"{where}[{i}]")
    walk(rec, path.split("."), "")
    return out


# every per-share run figure app.js displays (renderHeader / renderOverview / renderForecast / renderData,
# priceSpec's IV line, band and hurdle lines, the scored-price marker, the ranking row): restated
SHOWN_PER_SHARE = ("score.price", "score.iv_at_15", "score.iv_at_12", "score.base_oe_per_share", "score.scenarios.*.iv_at_15",
                   "numbers.price", "numbers.base_oe_per_share", "numbers.base_oe_latest_per_share", "numbers.base_oe_normalized_per_share",
                   "numbers.weighted.iv_at_15", "numbers.scenarios.*.iv_at_15", "forecast.paths.*.*", "forecast.hurdle_prices.*",
                   "forecast.sensitivity.*.15", "forecast.sensitivity.*.25", "row.price", "row.iv15", "row.iv12", "row.iv20", "row.iv25",
                   "ttm.ttm_oe_per_share")
UNCHANGED = ("row.irr", "row.irr_live", "row.irr_bear", "row.irr_bull", "row.irr_bear_live", "row.irr_bull_live", "row.upside15",
             "row.upside15_live", "row.market_cap_b", "row.market_cap_b_live", "score.implied_irr", "score.scenarios.*.irr",
             "score.upside_at_15_pct", "score.market_cap_b", "numbers.implied_irr_weighted", "numbers.scenarios.*.irr",
             "numbers.market_cap_est", "numbers.upside_at_15", "forecast.sensitivity.*.irr", "forecast.sensitivity.*.irr_live",
             "forecast.growth_paths.*.*", "forecast.g_base", "history.*.oe_conservative")


def test_split_since_scoring_restates_every_per_share_run_figure():
    with TempBase() as tb:
        now = datetime.datetime(2026, 10, 16, 19, 7, tzinfo=B.NY)
        tb.build(attachment=True, now=now)
        a = tb.record("APP")
        assert a["split_restated"] is None and a["row"]["split_restated"] is None
        live = B.jload(os.path.join(tb.dir, "APP", "live.json"))
        div0 = a["fundamentals"]["dividends"]
        tb.write_json("APP", "live.json", obj=_split_live(live))
        _set_close(tb, "APP", live["price"] / 2, "2099-01-02")  # Nasdaq's history is split-adjusted; newer than any block
        res = tb.build(attachment=True, now=now)
        assert res["written"] == ["APP"]
        b = tb.record("APP")
        for path in SHOWN_PER_SHARE:
            va, vb = _at(a, path), _at(b, path)
            assert va and set(va) == set(vb), (path, va, vb)
            for k in va:
                assert _isclose(vb[k], va[k] / 2), (k, va[k], vb[k])
        for path in B.SPLIT_DIVIDE:
            va, vb = _at(a, path), _at(b, path)
            assert set(va) == set(vb) and all(_isclose(vb[k], va[k] / 2) for k in va), path
        for path in B.SPLIT_MULTIPLY:
            va, vb = _at(a, path), _at(b, path)
            assert set(va) == set(vb) and all(_isclose(vb[k], va[k] * 2) for k in va), path
        assert _at(a, "history.*.shares_diluted") and _at(a, "numbers.shares_diluted_latest")
        for path in UNCHANGED:
            va, vb = _at(a, path), _at(b, path)
            assert va == vb, (path, va, vb)
        assert (a["row"]["tier"], a["row"]["tier_live"]) == (b["row"]["tier"], b["row"]["tier_live"])
        # the record agrees with reprice.py's own restated live figures, and live.json itself is not restated twice
        assert b["live"] == _split_live(live)
        assert _isclose(b["forecast"]["hurdle_prices"]["15"], b["live"]["iv_at_15"]) and _isclose(b["row"]["iv20"], b["live"]["iv_at_20"])
        assert _isclose(b["score"]["price"], b["live"]["scored_price"]), "the scored-price marker in today's units"
        sr = b["split_restated"]
        assert sr["factor"] == 2.0 and sr["split"] == "2:1" and sr["scored_date"] == "2026-10-14" and sr["price_date"] == "2026-10-14"
        assert sr["as_scored"] == {"price": a["score"]["price"], "iv_at_15": a["score"]["iv_at_15"], "base_oe_per_share": a["score"]["base_oe_per_share"]}
        assert "score.price" in sr["fields"] and "forecast.paths.*.*" in sr["fields"] and "history.*.shares_diluted" in sr["fields"]
        assert "2:1 split" in sr["note"] and b["row"]["split_restated"] == {"factor": 2.0, "split": "2:1"}
        meta = tb.read("meta.json")
        assert meta["counts"]["split_restated"] == 1 and any("split" in x and "APP 2:1" in x for x in meta["notes"])
        # the dividends block is not repriced across the split (filed DPS / shares vs a post-split close)
        assert b["fundamentals"]["dividends"] == div0
        # the attachment record and the history CSV carry the restated figures
        att = res["attachment"][0]
        assert os.path.exists(att)
        hist = {r[1]: dict(zip(B.HISTORY_COLUMNS, r)) for r in _read_csv(res["history"][0])[1][1:]}
        assert hist["APP"]["iv15"] == f"{b['row']['iv15']:.2f}" and _isclose(b["row"]["iv15"], a["row"]["iv15"] / 2)
        # a reverse split (1:10): × 10
        tb.write_json("APP", "live.json", obj=_split_live(live, 0.1, "1:10"))
        tb.build()
        c = tb.record("APP")
        assert _isclose(c["score"]["iv_at_15"], a["score"]["iv_at_15"] * 10) and c["row"]["split_restated"] == {"factor": 0.1, "split": "1:10"}
        # factor 1.0 (reprice's normal output): nothing restated
        lv1 = dict(live, split_factor=1.0, basis_check={"status": "ok", "factor": 1.0, "split": None, "method": "ratio"})
        tb.write_json("APP", "live.json", obj=lv1)
        _set_close(tb, "APP", live["price"], "2026-10-14")
        tb.build()
        d = tb.record("APP")
        assert d["split_restated"] is None and d["score"] == a["score"] and d["forecast"] == a["forecast"] and d["row"]["iv15"] == a["row"]["iv15"]


def test_split_live_iv_fallback_is_restated_once():
    """A run whose hurdle prices are unknown takes iv20 / iv25 from live.json, already in today's units:
    the row must show them once restated, not divided again."""
    live = {"price": 50.0, "price_date": "2026-10-20", "scored_date": "2026-10-14", "irr_weighted": 0.12, "iv_at_15": 40.0,
            "iv_at_20": 30.0, "iv_at_25": 20.0, "split_factor": 2.0, "basis_check": {"factor": 2.0, "split": "2:1"},
            # computed against the score below (reprice records which one: Codex review r29 of PR #47)
            "score_json_fresh": True, "scored": {"tier_final": None, "tier_override_reason": None}}
    c = {"folder": "T", "path": "", "ticker": "T", "score": {"ticker": "T", "price": 100.0, "iv_at_15": 80.0, "implied_irr": 0.12,
                                                            "analysis_date": "2026-10-14", "tier_by_numbers": "C",
                                                            "engine_version": 5},
         # the run the score was built from (build_site.score_from_run — Codex review r11 of PR #47)
         "numbers": {"engine_version": 5, "data_gap": [], "price": 100.0, "as_of": "2026-10-14", "tier_by_numbers": "C",
                     "implied_irr_weighted": 0.12, "iv_at_15": 80.0}, "live": live, "history": [], "files": []}
    rec = B.build_record(c, {}, "2026-10-20T19:00:00-04:00", 0.0)
    assert rec["row"]["iv20"] == 30.0 and rec["row"]["iv25"] == 20.0 and rec["row"]["iv15"] == 40.0 and rec["row"]["price"] == 50.0
    assert rec["score"]["price"] == 50.0 and rec["numbers"]["price"] == 50.0 and rec["split_restated"]["split"] == "2:1"
    assert c["score"]["price"] == 100.0 and c["live"]["iv_at_20"] == 30.0, "the loaded files are never modified"
    assert B.live_split({"split_factor": 1.0}) == (None, None) and B.live_split({"basis_check": {"factor": 3.0}}) == (3.0, "3x")
    assert B.live_split(None) == (None, None) and B.live_split({"split_factor": -2}) == (None, None)


# ---------------- 16b. [Codex review r11 of PR #47] live beside a score.json from another engine run
def test_live_beside_a_score_from_another_run_is_withheld():
    """The main agent's general rule: make_score refused the latest engine run (or has not run on it), so the
    score.json on disk is another run's — the live.json on file is not shown as current, whatever make_score's reason:
    record.live_withheld reason score_not_from_this_run, the row ranked on its scored IRR; the score's own run shows."""
    with TempBase() as tb:
        tb.build()
        a = tb.record("APP")
        assert a["live"] is not None and a["live_withheld"] is None
        live = B.jload(os.path.join(tb.dir, "APP", "live.json"))
        n = B.jload(os.path.join(tb.dir, "APP", "dcf_numbers.json"))
        tb.write_json("APP", "dcf_numbers.json", obj=dict(n, implied_irr_weighted=n["implied_irr_weighted"] + 0.01,
                                                         tier_by_numbers=B.tier_for_irr(n["implied_irr_weighted"] + 0.01)))
        tb.build()
        b = tb.record("APP")
        w = b["live_withheld"]
        assert b["live"] is None and w["reason"] == "score_not_from_this_run" and w["price"] == live["price"], w
        assert "make_score" in w["note"] and b["row"]["live_withheld"] is True and b["row"]["irr_live"] is None
        tb.write_json("APP", "dcf_numbers.json", obj=n)
        tb.build()
        assert tb.record("APP")["live"] is not None and tb.record("APP")["live_withheld"] is None


# ---------------- 16c. [Codex review r29 of PR #47] live figures bound to the score they were computed against
def test_live_not_computed_against_the_current_score_is_withheld():
    """[Codex review r29 of PR #47, #4335127671] reprice.py wrote live.json for a folder with no score.json yet (the
    numbers tier, tier_final unknown); make_score then scored the SAME run with a tier_override, and live_shown
    accepted the old live.json (same run, same dates), so the page and the ranking showed the numbers tier at the
    last close and the agent's override was silently dropped — and a live.json computed against an earlier score of
    the same run (an override since removed by a make_score re-run) survived the same way. live.json now records the
    score it was computed against (score_json_fresh, scored.tier_final / tier_override_reason / dcf_content_hash) and
    a live.json not computed against the score on file is withheld: record.live null, reason
    live_not_from_this_score, the row ranked on its scored figures — the latest available, never "pending" (Andrew,
    2026-10-20). A live.json computed against the score on file is shown, the override kept."""
    import reprice as R
    with TempBase() as tb:
        n = B.jload(os.path.join(tb.dir, "APP", "dcf_numbers.json"))
        s = B.jload(os.path.join(tb.dir, "APP", "score.json"))
        over = dict(s, tier_final="D", tier_override_reason="test: the agent's override (analysis.md)")
        price, day = 262.19, "2026-10-14"
        pre = R.reprice(n, price, day, None, today="2026-10-15")      # written before make_score scored the run
        assert pre["score_json_fresh"] is None and pre["tier"] == "B", pre
        on_over = R.reprice(n, price, day, over, today="2026-10-15")  # computed against the override score
        assert on_over["tier"] == "D" and on_over["override_active"] is True, on_over
        for live, score, why in ((pre, over, "no score.json"), (on_over, s, "earlier score")):
            tb.write_json("APP", "score.json", obj=score)
            tb.write_json("APP", "live.json", obj=live)
            tb.build()
            r = tb.record("APP")
            w = r["live_withheld"]
            assert r["live"] is None and w and w["reason"] == "live_not_from_this_score", (why, w)
            assert w["price"] == price and w["price_date"] == day and w["scored_date"] == day, (why, w)
            assert "latest available" in w["note"] and "pending" not in w["note"].lower(), (why, w["note"])
            assert r["row"]["live_withheld"] is True and r["row"]["tier_live"] is None and r["row"]["irr_live"] is None, why
            assert r["row"]["tier"] == score["tier_final"], (why, r["row"]["tier"])
        # computed against the score on file: shown, the override kept
        tb.write_json("APP", "score.json", obj=over)
        tb.write_json("APP", "live.json", obj=on_over)
        tb.build()
        r = tb.record("APP")
        assert r["live"] is not None and r["live_withheld"] is None and r["row"]["tier_live"] == "D", r["live_withheld"]
    # the score's run identity is part of what live.json was computed against (a same-day score of another run)
    hashed = dict(s, dcf_content_hash=n.get("content_hash"))
    assert B.score_from_run(hashed, n) == (True, [])
    lv = R.reprice(n, price, day, hashed, today="2026-10-15")
    assert lv["scored"]["dcf_content_hash"] == n["content_hash"], lv["scored"]
    assert B.live_shown({"score": hashed, "numbers": n, "live": lv}) == (lv, None)
    other = dict(lv, scored=dict(lv["scored"], dcf_content_hash="0" * 64))
    shown, w = B.live_shown({"score": hashed, "numbers": n, "live": other})
    assert shown is None and w["reason"] == "live_not_from_this_score", w
    # a hand-made live.json beside no run record is judged on its dates alone, as before
    assert B.live_shown({"score": {}, "live": {"price": 1.0, "irr_weighted": 0.1}})[1] is None


def test_a_live_json_with_no_score_identity_is_not_from_a_score_that_carries_one():
    """[Codex review r29 of PR #47, review note] live_score_problem compared scored.dcf_content_hash only when the
    live.json recorded it, so a live.json written before round 29 (no such key) beside a same-day score.json of
    ANOTHER engine run — one that carries dcf_content_hash — was shown as current: the earlier run's live IRR beside
    the new run's score (live_not_from_this_score never fired). A live.json that records no score identity was not
    computed against a score that has one: withheld until the next reprice rewrites it — since the round's polish
    review with its own reason, live_without_score_identity (it records no identity, so it is never said to have been
    computed before the score). Beside a score.json with no dcf_content_hash (a run from before release 5.6.0) there
    is no identity to bind, and such a live.json is shown as before."""
    import copy
    import hashlib
    import json
    import reprice as R
    with TempBase() as tb:
        n = B.jload(os.path.join(tb.dir, "APP", "dcf_numbers.json"))
        s = B.jload(os.path.join(tb.dir, "APP", "score.json"))
    assert "dcf_content_hash" not in s and B.score_from_run(s, n) == (True, []), s.get("dcf_content_hash")
    price, day = 262.19, n["as_of"]
    legacy = copy.deepcopy(R.reprice(n, price, day, s, today=day))
    assert legacy["scored"].pop("dcf_content_hash", "absent") is None, legacy["scored"]
    # beside its own (unhashed) score: nothing to bind, shown
    assert B.live_shown({"score": s, "numbers": n, "live": legacy}) == (legacy, None)
    # run B, the same day: another engine run record (a new content_hash), the same headline figures, scored with
    # its hash (make_score writes dcf_content_hash since round 12)
    nb = copy.deepcopy(n)
    nb["diagnostics"] = dict(nb.get("diagnostics") or {}, test_run="B: another engine run of the same day")
    nb.pop("content_hash", None)
    nb["content_hash"] = hashlib.sha256(json.dumps(nb, sort_keys=True, separators=(",", ":"),
                                                   default=str).encode()).hexdigest()
    assert nb["content_hash"] != n.get("content_hash")
    sb = dict(s, dcf_content_hash=nb["content_hash"])
    assert B.score_from_run(sb, nb) == (True, [])
    shown, w = B.live_shown({"score": sb, "numbers": nb, "live": legacy})
    assert shown is None and w and w["reason"] == "live_without_score_identity", w
    assert w["price"] == price and "latest available" in w["note"], w
    assert B.live_score_problem(legacy, sb, nb) is None
    assert "records no score identity" in B.live_score_identity_missing(legacy, sb)
    # the same score.json hashed for run A (its own run): a legacy live.json still records no identity — withheld
    sa = dict(s, dcf_content_hash=n.get("content_hash"))
    assert B.score_from_run(sa, n) == (True, [])
    assert B.live_shown({"score": sa, "numbers": n, "live": legacy})[1]["reason"] == "live_without_score_identity"
    # the next reprice records the identity and is shown
    fresh = R.reprice(nb, price, day, sb, today=day)
    assert fresh["scored"]["dcf_content_hash"] == nb["content_hash"]
    assert B.live_shown({"score": sb, "numbers": nb, "live": fresh}) == (fresh, None)


def test_a_live_json_with_no_score_identity_never_claims_it_was_computed_before_the_score():
    """[Codex review r29 of PR #47, polish review] A live.json written by the pre-round-29 reprice records no
    scored.dcf_content_hash. Beside a score.json that carries one it was withheld as live_not_from_this_score, whose
    note says it "was computed before the current score of this run (make_score has scored it since)" — false for the
    common case right after the merge: reprice ran AFTER make_score scored its own run, against that same score, and
    only the identity is missing (every published name's live.json on the VM until the next reprice). It now has its
    own reason, live_without_score_identity, checked right after live_not_from_this_score: the note says the
    repricing records no score identity and is refreshed by the next repricing (never "pending", Andrew 2026-10-20).
    A legacy live.json that also disagrees on what it did record (score_json_fresh, tier_final, the override reason)
    was computed against another score: live_not_from_this_score, as before. A live.json carrying the identity, or
    beside a score.json with none, is unchanged."""
    import copy
    import reprice as R
    with TempBase() as tb:
        n = B.jload(os.path.join(tb.dir, "APP", "dcf_numbers.json"))
        s = B.jload(os.path.join(tb.dir, "APP", "score.json"))
    sa = dict(s, dcf_content_hash=n.get("content_hash"))      # make_score writes the run's hash (since round 12)
    assert B.score_from_run(sa, n) == (True, [])
    day = n["as_of"]
    lv = R.reprice(n, 262.19, day, sa, today=day)               # computed against THIS score
    assert B.live_shown({"score": sa, "numbers": n, "live": lv}) == (lv, None)
    legacy = copy.deepcopy(lv)
    legacy["scored"].pop("dcf_content_hash")                   # what the pre-round-29 reprice wrote
    assert B.live_score_problem(legacy, sa, n) is None, B.live_score_problem(legacy, sa, n)
    why = B.live_score_identity_missing(legacy, sa)
    assert why and "records no score identity" in why and sa["dcf_content_hash"] in why, why
    shown, w = B.live_shown({"score": sa, "numbers": n, "live": legacy})
    assert shown is None and w["reason"] == "live_without_score_identity", w
    assert w["price"] == 262.19 and w["price_date"] == day and w["scored_date"] == day and w["method"] is None, w
    assert w["note"] == B.LIVE_NO_SCORE_IDENTITY_NOTE, w
    note = w["note"].lower()
    assert "records no score identity" in note and "next repricing" in note and "latest available" in note, note
    assert "computed before" not in note and "scored it since" not in note and "pending" not in note, note
    # a legacy live.json that also disagrees on what it recorded was computed against another score: the known
    # mismatch is named first, as before
    over = dict(sa, tier_final="D", tier_override_reason="test: the agent's override (analysis.md)")
    assert B.live_shown({"score": over, "numbers": n, "live": legacy})[1]["reason"] == "live_not_from_this_score"
    pre = copy.deepcopy(legacy)
    pre["score_json_fresh"] = None
    assert B.live_shown({"score": sa, "numbers": n, "live": pre})[1]["reason"] == "live_not_from_this_score"
    # a recorded identity that is null (computed against a score with no hash) beside a hashed score: another score
    nulled = copy.deepcopy(legacy)
    nulled["scored"]["dcf_content_hash"] = None
    assert B.live_shown({"score": sa, "numbers": n, "live": nulled})[1]["reason"] == "live_not_from_this_score"
    assert B.live_score_identity_missing(nulled, sa) is None
    # beside a score.json with no hash there is no identity to bind: shown, as before
    assert B.live_score_identity_missing(legacy, s) is None
    assert B.live_shown({"score": s, "numbers": n, "live": legacy}) == (legacy, None)


# ---------------- 16. live older than the score
def test_live_older_than_the_score_is_withheld():
    now = datetime.datetime(2026, 10, 16, 19, 7, tzinfo=B.NY)
    with TempBase() as tb:
        tb.build()
        a = tb.record("APP")
        live = B.jload(os.path.join(tb.dir, "APP", "live.json"))
        # scoring day: Nasdaq has not posted the scored session; reprice used the session before it
        stale = dict(live, price_date="2026-10-13", irr_weighted=-0.5, split_factor=1.0,
                     basis_check={"status": "ok", "factor": 1.0, "split": None, "method": "no_close_since_scoring"})
        tb.write_json("APP", "live.json", obj=stale)
        res = tb.build(attachment=True, now=now)
        b, row = tb.record("APP"), tb.record("APP")["row"]
        assert b["live"] is None and b["live_withheld"]["reason"] == "live_older_than_score"
        w = b["live_withheld"]
        assert (w["price_date"], w["scored_date"], w["method"], w["price"]) == ("2026-10-13", "2026-10-14", "no_close_since_scoring", live["price"])
        assert "predates the scored analysis" in w["note"] and "latest available" in w["note"] and "pending" not in w["note"].lower(), w["note"]
        # merge of main #83 into PR #47: the note's tail is an f-string too (it printed a literal "{pd}"), and it
        # matches fixtures/assemble.js liveShown word for word
        assert w["note"].endswith("as of the 2026-10-13 close.") and "{" not in w["note"], w["note"]
        assert row["live_withheld"] is True and row["has"]["live"] is False
        for k in ("irr_live", "price_live", "tier_live", "upside15_live", "market_cap_b_live", "price_date"):
            assert row[k] is None, k
        assert all(v["irr_live"] is None for v in b["forecast"]["sensitivity"].values())
        assert row["irr"] == a["row"]["irr"] and b["score"] == a["score"] and b["forecast"]["hurdle_prices"] == a["forecast"]["hurdle_prices"]
        index = tb.read("index.json")
        assert [r["ticker"] for r in index][0] == "APP" and B.rank_key(index[0])[1] == -row["irr"], "ranked on the scored IRR, not -50%"
        meta = tb.read("meta.json")
        assert meta["counts"]["live_withheld"] == 1 and meta["counts"]["with_live"] == 2 and any("withheld" in x and "APP" in x for x in meta["notes"])
        hist = {r[1]: dict(zip(B.HISTORY_COLUMNS, r)) for r in _read_csv(res["history"][0])[1][1:]}
        assert hist["APP"]["irr_live"] == "" and hist["APP"]["tier_live"] == "" and hist["APP"]["price_date"] == "2026-10-14"
        assert hist["APP"]["price"] == f"{a['score']['price']:.2f}"
        # a split factor on a withheld live.json is not applied
        tb.write_json("APP", "live.json", obj=dict(_split_live(live), price_date="2026-10-13"))
        tb.build()
        assert tb.record("APP")["split_restated"] is None and tb.record("APP")["score"] == a["score"]
        # the scored session's own close (same date) is current: shown
        tb.write_json("APP", "live.json", obj=dict(stale, price_date="2026-10-14"))
        tb.build()
        assert tb.record("APP")["live"] is not None and tb.record("APP")["live_withheld"] is None and tb.record("APP")["row"]["irr_live"] == -0.5
    # the later of score.json analysis_date and the run's as_of (live.scored_date) counts
    c = {"score": {"analysis_date": "2026-10-16"}, "live": {"price": 1.0, "irr_weighted": 0.1, "price_date": "2026-10-15", "scored_date": "2026-10-14"}}
    assert B.live_shown(c)[0] is None and B.live_shown(c)[1]["scored_date"] == "2026-10-16"
    c["score"]["analysis_date"] = "2026-10-14"
    assert B.live_shown(c) == (c["live"], None)
    assert B.live_shown({"score": {}, "live": {"price": 1.0, "irr_weighted": 0.1}}) == ({"price": 1.0, "irr_weighted": 0.1}, None), "undatable: shown as before"
    assert B.live_shown({"score": {}, "live": {"price": 1.0}}) == (None, None)
    # a live.json left over from an earlier run of a re-scored name: withheld even when its close is newer
    old_run = {"score": {"analysis_date": "2026-10-16"},
               "live": {"price": 50.0, "irr_weighted": 0.2, "price_date": "2026-10-17", "scored_date": "2026-10-01"}}
    lv, w = B.live_shown(old_run)
    assert lv is None and w["reason"] == "live_from_earlier_run" and w["scored_date"] == "2026-10-16", w
    assert "2026-10-01 run" in w["note"] and "latest available" in w["note"] and "pending" not in w["note"].lower(), w["note"]
    old_run["live"]["scored_date"] = "2026-10-16"
    assert B.live_shown(old_run) == (old_run["live"], None), "same run, close after scoring: shown"


# ---------------- 19. prices staleness guard
def test_prices_staleness_guard_flags_rows_and_meta():
    with TempBase() as tb:
        # controlled closes: APP two sessions behind the sweep's newest close,
        # KR one behind (the normal posting lag), AEE / ZS at the newest
        dates = {"APP": "2026-10-12", "KR": "2026-10-13", "AEE": "2026-10-14", "ZS": "2026-10-14"}
        for t, d in dates.items():
            p = B.jload(os.path.join(tb.dir, t, "prices.json"))
            p["as_of"] = d
            p["stats"]["last_date"] = d
            tb.write_json(t, "prices.json", obj=p)
        res = tb.build()
        rows = {r["ticker"]: r for r in res["rows"]}
        assert rows["APP"]["prices_stale"] == {"last_date": "2026-10-12", "sessions_behind": 2, "latest_close": "2026-10-14"}, rows["APP"].get("prices_stale")
        assert rows["KR"]["prices_stale"] is None, "one session behind is the normal posting lag, not staleness"
        assert rows["AEE"]["prices_stale"] is None and rows["ZS"]["prices_stale"] is None
        meta = tb.read("meta.json")
        assert meta["counts"]["prices_stale"] == 1, meta["counts"]
        assert any("more than one session behind" in x and "APP" in x for x in meta["notes"]), meta["notes"]
        # re-derived on every build (like row.watchlist): a second run that skips
        # every record unchanged keeps the flag and the count
        res2 = tb.build()
        rows2 = {r["ticker"]: r for r in res2["rows"]}
        assert rows2["APP"]["prices_stale"] == rows["APP"]["prices_stale"] and res2["meta"]["counts"]["prices_stale"] == 1
    # a stale company whose record FAILS to build has no row: it is not a
    # candidate, so it cannot enter the count / note or shift the baseline
    with TempBase() as tb:
        dates = {"APP": "2026-10-12", "KR": "2026-10-13", "AEE": "2026-10-14", "ZS": "2026-10-14"}
        for t, d in dates.items():
            p = B.jload(os.path.join(tb.dir, t, "prices.json"))
            p["as_of"] = d
            p["stats"]["last_date"] = d
            tb.write_json(t, "prices.json", obj=p)
        real = B.build_record
        B.build_record = lambda c, *a, **kw: (_ for _ in ()).throw(RuntimeError("x")) if c.get("ticker") == "APP" else real(c, *a, **kw)
        try:
            res = tb.build()
        finally:
            B.build_record = real
        assert res["failed"] == ["APP"] and not any(r["ticker"] == "APP" for r in res["rows"])
        assert res["meta"]["counts"]["prices_stale"] == 0, res["meta"]["counts"]
        assert not any("more than one session behind" in x for x in res["meta"]["notes"])
        assert all(r["prices_stale"] is None for r in res["rows"])
    # sessions are counted from the names' daily_1y series, not from the set of
    # terminal dates: no cache here ends on 2026-10-12 / 2026-10-13, but the
    # series contain them, so a name last closed 2026-10-09 is three behind
    with TempBase() as tb:
        p = B.jload(os.path.join(tb.dir, "APP", "prices.json"))
        p["as_of"] = "2026-10-09"
        p["stats"]["last_date"] = "2026-10-09"
        tb.write_json("APP", "prices.json", obj=p)
        res = tb.build()
        rows = {r["ticker"]: r for r in res["rows"]}
        assert rows["APP"]["prices_stale"] == {"last_date": "2026-10-09", "sessions_behind": 3, "latest_close": "2026-10-14"}, rows["APP"].get("prices_stale")
        assert res["meta"]["counts"]["prices_stale"] == 1


# ---------------- 17. street_fetched_at without street.json
def test_profile_carries_street_fetched_at_without_street_json():
    new = {"ticker": "T", "as_of": "2026-09-01", "fetched_at": "2026-09-01T06:00:00-04:00", "about": {"x": 1}, "filings": []}
    for prof in (new, dict(new, street=None, market={}), dict(new, street={}, market=None)):
        p = B.profile_with_street(prof, None)
        assert "street_fetched_at" in p and p["street_fetched_at"] is None and p["street"] is None and p["market"] is None, prof
        assert p["about"] == {"x": 1} and p["as_of"] == "2026-09-01"
    assert B.profile_with_street(dict(new, street={"a": 1}), None)["street_fetched_at"] == new["fetched_at"], "a legacy block was pulled"
    with TempBase(caches=False) as tb:
        for t in TICKERS:
            prof = B.jload(os.path.join(tb.dir, t, "profile.json"))
            tb.write_json(t, "profile.json", obj={k: v for k, v in prof.items() if k not in ("street", "market")})
        res = tb.build(attachment=True)
        for t in TICKERS:
            p = tb.record(t)["profile"]
            assert "street_fetched_at" in p and p["street_fetched_at"] is None and p["street"] is None, t
        with open(res["attachment"][0], encoding="utf-8") as f:
            html = f.read()
        data = json.loads(html.split("window.SITE_DATA=", 1)[1].split(";</script>", 1)[0].replace("<\\/", "</"))
        assert all("street_fetched_at" in r["profile"] and r["profile"]["street_fetched_at"] is None for r in data["records"].values())


# ---------------- 20. engine 5.7 rulings (Andrew, 2026-10-19 — R1 misfit notch, R2a declared 6-K bridge, R3 declared
# facts + quote check, R4 moat scorecard, R6 share classes, R7 base alternatives, M6 growth hold; lane L6, design 06
# with rebase amendments B1-B20). Each fails on the code before the lane (4f7d6f1).
EXAMPLES = os.path.join(SYS, "examples")


def _example(name):
    return B.jload(os.path.join(EXAMPLES, name))


def _notch(tbn, after, applies=True, src="auto", na=None, reason=None):
    """A score.json misfit_notch block as make_score.misfit_notch writes it (L1)."""
    return {"applies": applies, "tier_by_numbers": tbn, "tier_after_notch": after,
            "reason": reason or f"Sector misfit (universe sector Finance): numbers tier {tbn} at a weighted IRR of 18.43% "
                                f"publishes one notch lower as {after} — the mechanical sector-misfit notch",
            "reason_source": src, "not_applied": na,
            "basis": {"source": "engine_flag", "sector": "Finance", "sic": "6211", "sic_description": "Security Brokers",
                      "sic_class": "broker_dealer", "sic_source": "edgar_submissions"}}


def _misfit(**fields):
    return lambda s: dict(s, model_fit="misfit", **fields)


def test_facts_json_is_served_and_rebuilds_only_its_record():
    """T-PY-1 (R3): facts.json is an ordinary folder file — adding, touching or deleting it rebuilds that record alone,
    and the record carries it verbatim (record.facts, row.has.facts, meta.counts.facts)."""
    doc = dict(_example(os.path.join("facts", "TST", "facts.json")), ticker="APP")
    with TempBase() as tb:
        tb.build()
        tb.write_json("APP", "facts.json", obj=doc)
        res = tb.build()
        assert res["written"] == ["APP"] and sorted(res["skipped"]) == ["AEE", "KR", "ZS"], (res["written"], res["skipped"])
        rec = tb.record("APP")
        assert rec["facts"] == doc and rec["row"]["has"]["facts"] is True
        assert tb.read("meta.json")["counts"]["facts"] == 1
        assert all(tb.record(t)["facts"] is None and tb.record(t)["row"]["has"]["facts"] is False for t in ("KR", "AEE", "ZS"))
        p = os.path.join(tb.dir, "APP", "facts.json")
        os.utime(p, (time.time() + 10, max(time.time(), os.path.getmtime(os.path.join(tb.site, "data", "APP.json"))) + 10))
        assert tb.build()["written"] == ["APP"]
        os.remove(p)
        res = tb.build()
        assert res["written"] == ["APP"] and tb.record("APP")["facts"] is None and tb.record("APP")["row"]["has"]["facts"] is False
        assert tb.read("meta.json")["counts"]["facts"] == 0
        # a malformed facts.json renders as absent (make_score refuses it on a 5.7 run)
        with open(p, "w", encoding="utf-8") as f:
            f.write("[1, 2]")
        tb.build()
        assert tb.record("APP")["facts"] is None and tb.record("APP")["row"]["has"]["facts"] is False


def test_misfit_notch_row_fields_and_the_new_tier_override_meaning():
    """T-PY-2 (R1; design 01 §5 / 06 §1.5, rebase B3): tier_override is a judgment override BEYOND the notch; a notched
    misfit is tier_notched with tier_override false; a misfit scored before the notch (no block) reads as before; the
    history CSV appends tier_by_numbers / tier_notched. Only tier_final / misfit_notch / tier_override_reason are
    edited, so each score is still its run's."""
    with TempBase() as tb:
        tb.clone("APP", "MFA", **{"score.json": _misfit(tier_final="C", misfit_notch=_notch("B", "C"))})
        tb.clone("APP", "MFB", **{"score.json": _misfit(tier_final="D", misfit_notch=_notch("B", "C"),
                                                        tier_override_reason="a judgment below the notch: 9.8% payable IRR")})
        tb.clone("KR", "MFC", **{"score.json": _misfit(misfit_notch=_notch("D", "D", applies=False, na="tier_floor_D"))})
        tb.clone("AEE", "MFF", **{"score.json": _misfit(misfit_notch=_notch("F", "F", applies=False, na="tier_F"))})
        tb.clone("APP", "MFL", **{"score.json": _misfit(tier_final="C", tier_override_reason="legacy one-notch insurer override")})
        only = TICKERS + ["MFA", "MFB", "MFC", "MFF", "MFL"]
        res = tb.build(only=only, attachment=True, now=datetime.datetime(2026, 10, 21, 19, 7, tzinfo=B.NY))
        rows = {r["ticker"]: r for r in tb.read("index.json")}
        a, b, c, f, leg = rows["MFA"], rows["MFB"], rows["MFC"], rows["MFF"], rows["MFL"]
        assert a["tier"] == "C" and a["tier_override"] is False and a["tier_notched"] is True, a
        assert a["misfit_notch"] == {"applies": True, "tier_by_numbers": "B", "tier_after_notch": "C", "reason_source": "auto",
                                     "not_applied": None}, a["misfit_notch"]
        assert b["tier"] == "D" and b["tier_override"] is True and b["tier_notched"] is True, b
        assert c["tier_override"] is False and c["tier_notched"] is False and c["misfit_notch"]["applies"] is False
        assert c["misfit_notch"]["not_applied"] == "tier_floor_D" and f["misfit_notch"]["not_applied"] == "tier_F"
        assert leg["tier_override"] is True and leg["misfit_notch"] is None and leg["tier_notched"] is False, "legacy unchanged"
        for t in TICKERS:
            assert rows[t]["misfit_notch"] is None and rows[t]["tier_notched"] is False
            assert rows[t]["tier_override"] is bool(rows[t]["tier_by_numbers"] and rows[t]["tier"] != rows[t]["tier_by_numbers"])
        meta = tb.read("meta.json")
        assert meta["counts"]["notched"] == 2 and meta["counts"]["misfits"] == 6, meta["counts"]  # + AEE (a legacy utility misfit)
        assert any("2 published one tier below their numbers tier" in x for x in meta["notes"]), meta["notes"]
        # the record keeps the whole block (reason, basis) for the page
        assert tb.record("MFA")["score"]["misfit_notch"]["basis"]["sic"] == "6211"
        hdr, body = _read_csv(res["history"][0])[1][0], _read_csv(res["history"][0])[1][1:]
        assert tuple(hdr) == B.HISTORY_COLUMNS and len(hdr) == 28 and hdr[:18] == list(B.HISTORY_COLUMNS[:18])
        assert hdr[18:20] == ["tier_by_numbers", "tier_notched"], hdr
        by = {r[1]: dict(zip(hdr, r)) for r in body}
        assert (by["MFA"]["tier_scored"], by["MFA"]["tier_by_numbers"], by["MFA"]["tier_notched"]) == ("C", "B", "true")
        assert (by["MFL"]["tier_scored"], by["MFL"]["tier_by_numbers"], by["MFL"]["tier_notched"]) == ("C", "B", "false")
        assert by["MFC"]["tier_notched"] == "false" and by["APP"]["tier_notched"] == "false"


def _bound_live(live, score):
    """live.json as reprice.py writes it AGAINST `score` (Codex review r29 of PR #47: score_json_fresh, scored.tier_final,
    scored.tier_override_reason while the override is active — tier_final other than the run's numbers tier)."""
    sc = dict(live.get("scored") or {}, tier_final=score.get("tier_final"),
              tier_override_reason=score.get("tier_override_reason") if score.get("tier_final") != score.get("tier_by_numbers") else None)
    if "dcf_content_hash" in score:
        sc["dcf_content_hash"] = score["dcf_content_hash"]
    return dict(live, score_json_fresh=True, scored=sc)


def test_live_notch_fields_on_the_row():
    """T-PY-3 (R1; rebase B3, I5): a live.json bound to the notched score carries reprice's live notch — the row's
    tier_live is the notched LIVE tier, tier_by_numbers_live the live numbers tier, misfit_notch_live the block. The same
    live.json computed against the un-notched score is withheld (live_not_from_this_score): an un-notched live tier is
    never shown beside a notched score (06 open question 4, resolved by PR #47)."""
    with TempBase() as tb:
        tb.clone("APP", "MFA", **{"score.json": _misfit(tier_final="C", misfit_notch=_notch("B", "C"))})
        s = B.jload(os.path.join(tb.dir, "MFA", "score.json"))
        live = B.jload(os.path.join(tb.dir, "MFA", "live.json"))
        lv = _bound_live(dict(live, ticker="MFA", tier="C", tier_display="C", tier_by_numbers="B",
                              misfit_notch={"tier_by_numbers": "B", "tier_after_notch": "C", "applies": True, "basis": "score_json"}), s)
        tb.write_json("MFA", "live.json", obj=lv)
        tb.build(only=TICKERS + ["MFA"])
        r = tb.record("MFA")
        assert r["live_withheld"] is None, r["live_withheld"]
        row = r["row"]
        assert row["tier_live"] == "C" and row["tier_by_numbers_live"] == "B", row
        assert row["misfit_notch_live"] == {"applies": True, "tier_by_numbers": "B", "tier_after_notch": "C",
                                            "reason_source": None, "not_applied": None, "basis": "score_json"}, row["misfit_notch_live"]
        app = tb.record("APP")["row"]
        assert app["tier_by_numbers_live"] == "B" and app["misfit_notch_live"] is None  # modeled: live numbers tier, no block
        assert tb.record("AEE")["row"]["tier_by_numbers_live"] is None and tb.record("AEE")["row"]["misfit_notch_live"] is None
        # the same live.json computed against the un-notched score (scored.tier_final B): withheld, never shown
        tb.write_json("MFA", "live.json", obj=dict(lv, scored=dict(lv["scored"], tier_final="B")))
        tb.build(only=TICKERS + ["MFA"])
        r = tb.record("MFA")
        assert r["live"] is None and r["live_withheld"]["reason"] == "live_not_from_this_score", r["live_withheld"]
        assert r["row"]["tier_live"] is None and r["row"]["tier_by_numbers_live"] is None and r["row"]["misfit_notch_live"] is None


def _declared_interim_ttm(ttm):
    """KR's ttm.json reshaped as ttm.py --interim writes a declared 6-K bridge (L4: basis, legs, fx, shares, provenance)."""
    leg = lambda fy, p, c: {"fy": {"local": fy, "usd": fy * 1.17, "tag": "ENGINE_FY"}, "prior_interim": {"local": p, "usd": p * 1.10, "kind": "filing", "verified": "xbrl_instance"},  # noqa: E731
                            "current_interim": {"local": c, "usd": c * 1.14, "kind": "filing", "verified": "snippet"},
                            "ttm_local": fy - p + c, "ttm_usd": fy * 1.17 - p * 1.10 + c * 1.14}
    return dict(ttm, basis="declared_interim", currency="EUR", fy_end="2025-12-31", ytd_end="2026-06-30",
                periods={"fy": ["2025-01-01", "2025-12-31"], "prior_interim": ["2025-01-01", "2025-06-30"],
                         "current_interim": ["2026-01-01", "2026-06-30"]},
                report={"form": "6-K", "accession": "0001104659-26-088404", "document": "micc-20260630x6k.htm", "filed": "2026-07-30"},
                fx={"basis": "ecb_period_end", "rates_used": {"fy": 1.17, "prior_interim": 1.10, "current_interim": 1.14}},
                legs={"ocf": leg(483e6, 276e6, 539e6), "capex_ppe": leg(357e6, 150e6, 182e6),
                      "capex_intangibles": dict(leg(3e6, 1.49e6, 1.49e6), prior_interim={"local": 1.49e6, "usd": 1.64e6, "kind": "estimate", "method": "fy_prorated", "verified": "estimate"}),
                      "sbc": leg(35e6, 19e6, 18e6)},
                shares={"current_interim": {"value": 617e6, "kind": "filing", "verified": "xbrl_instance"}, "fy_diluted": 615e6, "ratio_to_fy": 1.003},
                ads_ratio=1.0, ttm_oe_per_ordinary_share=0.59,
                provenance=[{"field": "ocf", "leg": "current_interim", "accession": "0001104659-26-088404", "document": "micc-20260630x6k.htm",
                             "page": 12, "section": "Condensed consolidated statement of cash flows", "snippet": "Net cash flow from operating activities 539 276",
                             "verified": "xbrl_instance", "xbrl_tag": "ifrs-full:CashFlowsFromUsedInOperatingActivities"}])


def test_attachment_keeps_facts_and_a_declared_interim_ttm():
    """T-PY-4 (R2a / R3; 06 §1.7): the attachment copy keeps record.facts and a declared-interim ttm.json (its legs and
    provenance are the Data tab's Interim bridge section), drops every other ttm.json and judgment.json, and keeps a
    legacy (not gated) quote_check's counts with an empty untraced list; the site record keeps the list. The facts
    payload of the 24-fact worked example stays under 16 KB per record (the size bound)."""
    ex = _example("moat_scorecard_consumer_subscription.json")
    doc = dict(ex["inputs"]["facts"], ticker="APP")
    with TempBase() as tb:
        tb.write_json("APP", "facts.json", obj=doc)
        tb.write_json("KR", "ttm.json", obj=_declared_interim_ttm(B.jload(os.path.join(tb.dir, "KR", "ttm.json"))))
        res = tb.build(attachment=True, top=4, prerender=False)
        with open(res["attachment"][0], encoding="utf-8") as f:
            html = f.read()
        data = json.loads(html.split("window.SITE_DATA=", 1)[1].split(";</script>", 1)[0].replace("<\\/", "</"))
        recs = data["records"]
        assert recs["APP"]["facts"] == doc, "facts kept in the attachment"
        assert recs["KR"]["ttm"]["basis"] == "declared_interim" and recs["KR"]["ttm"]["provenance"], "a declared bridge's ttm kept"
        assert "ttm" not in recs["APP"] and "ttm" not in recs["AEE"], "every other ttm.json is trimmed"
        assert all("judgment" not in r for r in recs.values())
        site = tb.record("APP")
        assert site["quote_check"]["status"] == "legacy" and site["quote_check"]["untraced"], site["quote_check"]["untraced_count"]
        aq = recs["APP"]["quote_check"]
        assert aq["untraced"] == [] and aq["untraced_count"] == site["quote_check"]["untraced_count"] and aq["checked"] == site["quote_check"]["checked"]
        size = len(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        assert len(doc["facts"]) >= 24 and size <= 16 * 1024, size


def test_quote_check_summary_and_failure_isolation():
    """T-PY-5 (R3; 06 §1.4): record.quote_check is check_quotes.check_folder's report compacted to the §3 keys; without
    the checker it is null and meta says so; a checker exception is status 'error', the record is still written."""
    keys = {"status", "gated", "engine_release", "checked", "matched", "ignored", "untraced_count", "untraced", "integrity",
            "warnings", "error"}
    real = B.QUOTES
    assert real is not None, "check_quotes imports"
    with TempBase() as tb:
        tb.build()
        q = tb.record("APP")["quote_check"]
        assert set(q) == keys and q["status"] == "legacy" and q["gated"] is False, q
        assert len(q["untraced"]) <= B.QUOTE_UNTRACED_MAX and q["untraced_count"] >= len(q["untraced"])
        assert all(set(u) == {"line", "col", "raw", "kind"} and len(u["raw"]) <= 40 for u in q["untraced"])
        full = real.check_folder(os.path.join(tb.dir, "APP"))
        assert q["untraced_count"] == len(full["untraced"]) and q["checked"] == full["checked"] and q["matched"] == full["matched"]
        assert tb.record("ZS")["quote_check"]["status"] in ("pass", "fail", "legacy", "error")
        try:
            B.QUOTES = None
            res = tb.build(force=True)
            assert res["failed"] == [] and tb.record("APP")["quote_check"] is None
            assert any("quote checker unavailable" in x for x in tb.read("meta.json")["notes"])

            def boom(folder):
                raise RuntimeError("checker bug")
            import types
            B.QUOTES = types.SimpleNamespace(__file__=real.__file__, check_folder=boom)
            res = tb.build(force=True)
            assert res["failed"] == [] and sorted(res["written"]) == sorted(TICKERS)
            q = tb.record("APP")["quote_check"]
            assert q["status"] == "error" and "RuntimeError" in q["error"] and "checker bug" in q["error"] and set(q) == keys
        finally:
            B.QUOTES = real
        # no analysis.md -> null
        os.remove(os.path.join(tb.dir, "KR", "analysis.md"))
        tb.build()
        assert tb.record("KR")["quote_check"] is None


def test_builder_mtime_follows_the_quote_checker():
    """T-PY-6 (06 §1.8, rebase B11): record.quote_check depends on check_quotes.py / facts.py / quote_tokens.py, so a
    newer checker rebuilds every record (before, check_quotes was not in the builder mtime: all four were skipped)."""
    import types
    real = B.QUOTES
    with TempBase() as tb:
        assert sorted(tb.build()["written"]) == sorted(TICKERS)
        assert tb.build()["written"] == []
        newer = os.path.join(tb.dir, "check_quotes_stub.py")
        with open(newer, "w", encoding="utf-8") as f:
            f.write("# stub\n")
        t = time.time() + 60
        os.utime(newer, (t, t))
        try:
            B.QUOTES = types.SimpleNamespace(__file__=newer, check_folder=real.check_folder)
            assert B.builder_code_mtime() >= t - 1
            assert sorted(tb.build()["written"]) == sorted(TICKERS)
        finally:
            B.QUOTES = real
    names = {os.path.basename(m.__file__) for m in (B.QUOTES, sys.modules.get("facts"), sys.modules.get("quote_tokens")) if m}
    assert names == {"check_quotes.py", "facts.py", "quote_tokens.py"}, names


def _base_alts_bridge(pub_tier="D", med_tier="D"):
    """score.json base_alternatives of a published declared 6-K bridge (make_score.interim_base_alternatives, L4 / R7)."""
    return {"schema": 1, "published": "declared_interim", "stale_fy": True, "ttm_rejection_reason": None,
            "bases": [{"kind": "declared_interim", "role": "published", "computed": True, "measured": True, "base_oe_per_share": 0.5904,
                       "weighted_irr": 0.061, "tier_by_numbers": pub_tier, "f_subtype": None, "iprd_charge_per_share": 0.0,
                       "iprd_treatment": None, "fy_end": "2025-12-31", "ytd_end": "2026-06-30", "source": "ttm.json (ttm.py --interim)",
                       "why": "declared_interim", "why_text": "published — the declared 6-K interim bridge", "note": None},
                      {"kind": "annual_median", "role": "alternative", "computed": True, "measured": True, "base_oe_per_share": 1.11,
                       "weighted_irr": 0.0914, "tier_by_numbers": med_tier, "f_subtype": None, "iprd_charge_per_share": 0.0,
                       "iprd_treatment": None, "data_gap": [], "source": "median_of_last_3_fy_oe_per_share",
                       "base_change_pct": 88.01, "weighted_irr_change_pp": 3.04, "tier_changed": False,
                       "why": "not_chosen", "why_text": "not chosen: the declared 6-K interim bridge is the published base", "note": None}],
            "replays": 1, "measured": True, "note": None, "impact_carried_from_prior_score": False, "counterfactual_engine_release": None}


def _interim_block():
    """score.json interim_bridge (make_score.score_interim_fields, L4)."""
    return {"basis": "declared_interim", "currency": "EUR", "declaration_hash": "ab" * 32, "fy_period": ["2025-01-01", "2025-12-31"],
            "prior_interim_period": ["2025-01-01", "2025-06-30"], "current_interim_period": ["2026-01-01", "2026-06-30"],
            "report_form": "6-K", "report_accession": "0001104659-26-088404",
            "fx": {"basis": "ecb_period_end", "fy": 1.175, "prior_interim": 1.172, "current_interim": 1.1394},
            "estimate_legs": ["capex_intangibles.prior_interim", "capex_intangibles.current_interim"], "unverified_legs": [],
            "xbrl_verified_legs": ["ocf.current_interim"], "comparative_restated": False, "perimeter_changes": [],
            "iprd_interim_scan": "xbrl_instance: none", "measured_in": "base_alternatives"}


def test_moat_and_interim_row_summaries():
    """T-PY-7 (R4 revised / R2a; 06 §1.5, 03b §7.2): the row's moat_evidence summary from the worked example's
    expected_moat_evidence and the interim_bridge summary from L4's blocks; meta.counts moat_checked / interim_bridged."""
    me = _example("moat_scorecard_consumer_subscription.json")["expected_moat_evidence"]
    with TempBase() as tb:
        tb.clone("APP", "MOA", **{"score.json": lambda s: dict(s, moat_evidence=me, interim_bridge=_interim_block(),
                                                                base_alternatives=_base_alts_bridge("D", "C"))})
        tb.build(only=TICKERS + ["MOA"])
        row = tb.record("MOA")["row"]
        assert row["moat_evidence"] == {
            "score": 8.23, "status": "checked", "within_tolerance": True, "divergence": -1.23, "core_score": 7.73,
            "supporting_adjustment": 0.5, "measure": "roic", "return_median": 0.3609, "return_note": None, "sources": 2,
            "widest": "narrow", "flags": [], "industry": {"code": "4:7372", "level": 4, "label": "Services-Prepackaged Software (fictional peers)",
                                                         "ladder": "default", "peers": 6, "rank": 2, "of": 7},
            "fade_trend": None, "fade_in_sync": None, "fade_direction": None, "hold_years": 2}, row["moat_evidence"]
        assert row["interim_bridge"] == {"tier_bridged": "D", "tier_annual_median": "C", "estimate_legs": 2, "measured": True,
                                         "published_base": "declared_interim"}, row["interim_bridge"]
        meta = tb.read("meta.json")
        assert meta["counts"]["moat_checked"] == 1 and meta["counts"]["interim_bridged"] == 1, meta["counts"]
        assert all(tb.record(t)["row"]["moat_evidence"] is None and tb.record(t)["row"]["interim_bridge"] is None for t in TICKERS)
    # a STALE_FY rejection that published the median beside a declared bridge (R7) is not a bridged base
    s = {"interim_bridge": _interim_block(), "base_alternatives": dict(_base_alts_bridge(), published="annual_median")}
    assert B.interim_summary(s)["published_base"] == "annual_median"
    # a pre-R7 06-shape block (bridged / annual_median inside interim_bridge) still reads
    old = {"interim_bridge": {"bridged": {"tier_by_numbers": "D"}, "annual_median": {"tier_by_numbers": "C"}, "estimate_legs": ["x"], "measured": True}}
    assert B.interim_summary(old) == {"tier_bridged": "D", "tier_annual_median": "C", "estimate_legs": 1, "measured": True, "published_base": None}


def test_split_restates_the_new_per_share_fields():
    """T-PY-8 (06 §1.2, rebase B9): across a split since scoring the rulings' per-share figures of the run are divided by
    the factor — every base_alternatives base, the saved method runs, the previous score, a declared bridge's
    per-ordinary-share figure, the fade counterfactual's IV — and the bridge's share counts multiplied; facts.json values
    (source quotes) and the moat's volume x price figures are not restated."""
    me = _example("moat_scorecard_consumer_subscription.json")["expected_moat_evidence"]
    me = dict(me, fade={"version": 1, "status": "measured", "trend": "stable", "hold_years": 2, "in_sync": True,
                        "counterfactual": [{"hold_years": 0, "irr_weighted": 0.12, "iv_at_15": 150.0, "tier_by_numbers": "C", "report_only": False}]})
    doc = dict(_example(os.path.join("facts", "TST", "facts.json")), ticker="APP")
    extra = {"base_alternatives": _base_alts_bridge(), "moat_evidence": me,
             "method_runs": [{"label": "prelim", "file": "dcf_numbers_prelim.json", "content_hash": "c" * 64, "as_of": "2026-10-13",
                              "engine_release": "5.7.0", "base_oe_per_share": 9.0, "base_source": "ttm_json", "implied_irr": 0.15,
                              "iv_at_15": 300.0, "tier_by_numbers": "B"}],
             "previous_score": {"analysis_date": "2026-10-01", "engine_release": "5.4.0", "tier_final": "B", "tier_by_numbers": "B",
                                "implied_irr": 0.17, "iv_at_15": 280.0, "base_oe_per_share": 8.5, "dcf_content_hash": None}}
    new_div = ("score.base_alternatives.bases.*.base_oe_per_share", "score.method_runs.*.base_oe_per_share", "score.method_runs.*.iv_at_15",
               "score.previous_score.base_oe_per_share", "score.previous_score.iv_at_15", "ttm.ttm_oe_per_ordinary_share",
               "score.moat_evidence.fade.counterfactual.*.iv_at_15")
    new_mul = ("ttm.shares.current_interim.value", "ttm.shares.fy_diluted")
    with TempBase() as tb:
        tb.write_json("APP", "score.json", obj=dict(B.jload(os.path.join(tb.dir, "APP", "score.json")), **extra))
        tb.write_json("APP", "facts.json", obj=doc)
        tb.write_json("APP", "ttm.json", obj=_declared_interim_ttm(B.jload(os.path.join(tb.dir, "APP", "ttm.json"))))
        tb.build()
        a = tb.record("APP")
        live = B.jload(os.path.join(tb.dir, "APP", "live.json"))
        tb.write_json("APP", "live.json", obj=_split_live(live))
        tb.build()
        b = tb.record("APP")
        assert b["split_restated"]["factor"] == 2.0
        for path in new_div:
            assert path in B.SPLIT_DIVIDE, path
            va, vb = _at(a, path), _at(b, path)
            assert va and set(va) == set(vb) and all(_isclose(vb[k], va[k] / 2) for k in va), (path, va, vb)
            assert path in b["split_restated"]["fields"], path
        for path in new_mul:
            assert path in B.SPLIT_MULTIPLY, path
            va, vb = _at(a, path), _at(b, path)
            assert va and all(_isclose(vb[k], va[k] * 2) for k in va), (path, va, vb)
        assert b["facts"] == a["facts"] == doc, "declared facts are source quotes: never restated"
        assert b["score"]["moat_evidence"]["volume_price"] == a["score"]["moat_evidence"]["volume_price"]
        for k in ("weighted_irr", "tier_by_numbers", "base_change_pct"):
            assert [x.get(k) for x in b["score"]["base_alternatives"]["bases"]] == [x.get(k) for x in a["score"]["base_alternatives"]["bases"]], k


def _declared_share_classes():
    """dcf_numbers.json / ttm.json / score.json share_classes records of a declared Up-C (design 08 §7.1, §8.5; VNOM-shaped)."""
    applied = [{"period_end": "2025-12-31", "filed_traded": 142530000, "declared_units": 197117368, "units_split_factor": 1.0,
                "units_split_basis": "no_split", "units_equivalent": 197117368.0, "total_units": 339647368.0, "included_units": 0.0,
                "diluted_minus_basic": 0.0, "exchange_test": {"test": "passed"}, "classes": [{"name": "Class B", "value": 197117368, "exchange_ratio": 1.0}]}]
    numbers = {"declared": True, "basis": "up_c_exchangeable_units", "declaration_sha256": "d" * 64, "traded_class": "Class A",
               "classes": [{"name": "Class B", "holder": "Parent", "exchange_ratio": 1.0}], "applied": applied,
               "ttm": {"period_end": "2026-06-30", "filed_traded": 187553000, "units_equivalent": 171536228.0, "total_units": 359089228.0,
                       "ttm_oe_per_share": 4.143816867711776, "ttm_oe_per_share_filed_basis": 7.933757391244075},
               "latest": {"period_end": "2025-12-31", "filed_traded": 142530000, "units_equivalent": 197117368.0, "total_units": 339647368.0,
                          "declared_share_of_total": 0.5804},
               "nci_check": {"nci_share_of_equity": 0.5708, "declared_share_of_total": 0.5804, "agrees": True},
               "cap_check": {"cap_ratio": 2.5201, "universe_price": 42.99, "declared_uplift": 1.383, "band": 0.05, "gap": False},
               "included_periods": [], "counterfactual": False}
    ttm = {"filed_traded": 187553000, "units_equivalent": 171536228.0, "total_units": 359089228.0, "included_units": 0.0,
           "classes": [{"name": "Class B", "value": 171536228}], "declaration_sha256": "d" * 64}
    score = {"basis": "up_c_exchangeable_units", "base_used": "ttm", "replay_pin": 7.933757391244075, "base_oe_filed_basis": 7.9338,
             "base_oe_total_units": 4.1438, "base_oe_impact_pct": -47.77, "weighted_irr_filed_basis": 0.2505, "weighted_irr_total_units": 0.1502,
             "tier_filed_basis": "S", "tier_total_units": "B", "market_cap_filed_basis": 6416700600.0, "market_cap_total_units": 15290924507.36,
             "latest": {"filed_traded": 142530000, "units_equivalent": 197117368, "total_units": 339647368, "declared_share_of_total": 0.5804},
             "ttm": {"filed_traded": 187553000, "units_equivalent": 171536228, "total_units": 359089228}, "measured": True}
    return numbers, ttm, score


def test_split_restates_declared_share_class_figures():
    """Design 08 §10 T-PY (R6): a declared share-class record after a 2:1 split — every listed count doubled, every listed
    per-share figure halved (the filed-basis TTM, the universe price, the replay pin, both measured bases), the ratios,
    caps, IRRs and tiers unchanged; the row's share_basis is total_units."""
    nsc, tsc, ssc = _declared_share_classes()
    with TempBase() as tb:
        n = B.jload(os.path.join(tb.dir, "APP", "dcf_numbers.json"))
        tb.write_json("APP", "dcf_numbers.json", obj=dict(n, share_classes=nsc, up_c_check={"suspect": True, "universe_price": 42.99, "suppressed_by": "share_classes"},
                                                          market_cap_basis=dict(n.get("market_cap_basis") or {}, traded_shares=142530000, declared_units=197117368)))
        tb.write_json("APP", "ttm.json", obj=dict(B.jload(os.path.join(tb.dir, "APP", "ttm.json")), share_classes=tsc, ttm_shares_diluted_filed=187553000,
                                                  ttm_oe_per_share_filed_basis=7.933757391244075))
        tb.write_json("APP", "score.json", obj=dict(B.jload(os.path.join(tb.dir, "APP", "score.json")), share_classes=ssc))
        tb.build()
        a = tb.record("APP")
        assert a["row"]["share_basis"] == "total_units" and tb.record("KR")["row"]["share_basis"] is None
        tb.write_json("APP", "live.json", obj=_split_live(B.jload(os.path.join(tb.dir, "APP", "live.json"))))
        tb.build()
        b = tb.record("APP")
        mul = [p for p in B.SPLIT_MULTIPLY if "share_classes" in p or p.startswith("numbers.market_cap_basis") or p == "ttm.ttm_shares_diluted_filed"]
        div = [p for p in B.SPLIT_DIVIDE if "share_classes" in p or "up_c_check" in p or "filed_basis" in p]
        assert len(mul) >= 25 and len(div) >= 8, (len(mul), len(div))
        hit_m = hit_d = 0
        for p in mul:
            va, vb = _at(a, p), _at(b, p)
            assert set(va) == set(vb) and all(_isclose(vb[k], va[k] * 2) for k in va), (p, va, vb)
            hit_m += bool(va)
        for p in div:
            va, vb = _at(a, p), _at(b, p)
            assert set(va) == set(vb) and all(_isclose(vb[k], va[k] / 2) for k in va), (p, va, vb)
            hit_d += bool(va)
        assert hit_m >= 15 and hit_d >= 6, (hit_m, hit_d)
        assert _at(b, "numbers.share_classes.applied.*.classes.*.value") == {k: v * 2 for k, v in _at(a, "numbers.share_classes.applied.*.classes.*.value").items()}
        for p in ("numbers.share_classes.latest.declared_share_of_total", "numbers.share_classes.classes.*.exchange_ratio",
                  "numbers.share_classes.cap_check.cap_ratio", "numbers.share_classes.nci_check.nci_share_of_equity",
                  "score.share_classes.market_cap_total_units", "score.share_classes.weighted_irr_total_units",
                  "score.share_classes.latest.declared_share_of_total", "numbers.share_classes.applied.*.units_split_factor"):
            assert _at(a, p) and _at(a, p) == _at(b, p), p
        assert b["score"]["share_classes"]["tier_total_units"] == "B"


def test_base_alternatives_pass_through():
    """T-PY-R7 (design 11 §7.4): score.json base_alternatives reaches data/<T>.json verbatim (build_record passes the score
    through); a pre-5.7 score has none and the record carries none."""
    rejected = {"schema": 1, "published": "annual_median", "stale_fy": True,
                "ttm_rejection_reason": "median +$16.14/sh Tier C vs TTM −$3.48/sh on a half-year working-capital trough",
                "bases": [{"kind": "annual_median", "role": "published", "computed": True, "measured": True, "base_oe_per_share": 16.1404,
                           "weighted_irr": 0.1033, "tier_by_numbers": "C", "source": "median_of_last_3_fy_oe_per_share", "why": "ttm_rejected"},
                          {"kind": "ttm", "role": "rejected", "computed": True, "measured": True, "base_oe_per_share": -3.4772,
                           "weighted_irr": None, "tier_by_numbers": "F", "f_subtype": "no_cash_generation", "base_change_pct": -121.54,
                           "tier_changed": True, "why": "rejection_reason"}],
                "replays": 1, "measured": True, "note": None, "impact_carried_from_prior_score": False, "counterfactual_engine_release": None}
    with TempBase() as tb:
        tb.write_json("KR", "score.json", obj=dict(B.jload(os.path.join(tb.dir, "KR", "score.json")), base_alternatives=rejected))
        tb.build()
        assert tb.record("KR")["score"]["base_alternatives"] == rejected
        assert "base_alternatives" not in tb.record("APP")["score"]


def test_score_from_run_record():
    """Rebase B5: record.score_from_run is build_site.score_from_run's answer ({matches, mismatches} — at most five, each at
    most 200 characters), the Data tab's "Content hash" line reads it instead of comparing the hashes itself."""
    with TempBase() as tb:
        tb.build()
        assert tb.record("APP")["score_from_run"] == {"matches": True, "mismatches": []}
        n = B.jload(os.path.join(tb.dir, "APP", "dcf_numbers.json"))
        tb.write_json("APP", "dcf_numbers.json", obj=dict(n, implied_irr_weighted=n["implied_irr_weighted"] + 0.01, engine_release="9.9.9",
                                                          as_of="2026-10-20", price=n["price"] + 1))
        tb.build()
        sfr = tb.record("APP")["score_from_run"]
        assert sfr["matches"] is False and 1 <= len(sfr["mismatches"]) <= 5 and all(len(m) <= 200 for m in sfr["mismatches"]), sfr
        assert any("implied_irr" in m for m in sfr["mismatches"]) or any("analysis_date" in m for m in sfr["mismatches"])
    rec = B.score_run_record({"dcf_content_hash": "x" * 300}, {"content_hash": "y"})
    assert rec["matches"] is False and all(len(m) <= 200 for m in rec["mismatches"]) and len(rec["mismatches"]) <= 5


def test_history_csv_moat_columns():
    """T-PY-10 (03b §7.1, 10 §4): the moat record columns sit after tier_notched in that order; an unbounded median is
    `inf`, a loss on non-positive capital `-inf`, an unmeasured one blank; float() parses inf / -inf; moat_trend and
    hold_years close the row (blank trend / 2 before 5.7)."""
    cols = list(B.HISTORY_COLUMNS)
    assert cols[cols.index("tier_notched") + 1:] == ["moat_score", "moat_evidence_score", "moat_return_measure", "moat_return_median",
                                                       "moat_sources", "moat_widest_source", "moat_trend", "hold_years"], cols
    base = {"irr": 0.1, "moat": 6.0}
    rows = [dict(base, ticker="U", moat_evidence={"score": 7.123, "measure": "roic", "return_median": None, "return_note": "unbounded_high",
                                                 "sources": 2, "widest": "wide", "fade_trend": "eroding", "hold_years": 0}),
            dict(base, ticker="L", moat_evidence={"score": 3.0, "measure": "roic_tangible", "return_median": None,
                                                 "return_note": "loss_on_nonpositive_capital", "sources": None, "widest": None, "hold_years": 2}),
            dict(base, ticker="N", moat_evidence={"score": None, "measure": None, "return_median": None, "return_note": None,
                                                 "sources": None, "widest": None, "fade_trend": None, "hold_years": 2}),
            dict(base, ticker="M", moat_evidence={"score": 5.5, "measure": "roe", "return_median": 0.1234567, "return_note": None,
                                                 "sources": 1, "widest": "narrow", "fade_trend": "widening", "hold_years": 3}),
            dict(base, ticker="Z")]
    out = {r[1]: dict(zip(cols, r)) for r in B.history_rows(rows)}
    assert all(len(r) == len(cols) for r in B.history_rows(rows))
    u, l, nn, m, z = out["U"], out["L"], out["N"], out["M"], out["Z"]
    assert (u["moat_score"], u["moat_evidence_score"], u["moat_return_measure"], u["moat_return_median"]) == ("6", "7.12", "roic", "inf")
    assert l["moat_return_median"] == "-inf" and nn["moat_return_median"] == "" and m["moat_return_median"] == "0.123457"
    assert float(u["moat_return_median"]) == float("inf") and float(l["moat_return_median"]) == float("-inf")
    assert (u["moat_trend"], u["hold_years"], m["moat_trend"], m["hold_years"], nn["moat_trend"], nn["hold_years"]) == ("eroding", "0", "widening", "3", "", "2")
    assert (z["moat_score"], z["moat_evidence_score"], z["moat_return_median"], z["moat_trend"], z["hold_years"]) == ("6", "", "", "", "2"), "no moat evidence"
    # [L6 review r4] 03b §7.1: measure "blank (insufficient)" — a returns_on_capital pillar with insufficient_data (AMH,
    # VTRS, NVR, … on the 5.7 rebuild: "0 valid year(s) of roic") writes no measure, though moat_scorecard keeps
    # governing.measure "roic" there; the row summary's measure is null, so the CSV copies a blank
    me = _example("moat_scorecard_consumer_subscription.json")["expected_moat_evidence"]
    assert me["pillars"]["returns_on_capital"]["status"] == "measured" and B.moat_summary({"moat_evidence": me}, {})["measure"] == "roic"
    ins = json.loads(json.dumps(me))
    ins["pillars"]["returns_on_capital"] = dict(ins["pillars"]["returns_on_capital"], status="insufficient_data", score=None, median=None,
                                                median_note=None, reason="0 valid year(s) of roic in the last 5 fiscal year(s); at least 3 needed")
    ins["governing"] = dict(ins["governing"], measure="roic", median=None, median_note=None)
    summ = B.moat_summary({"moat_evidence": ins}, {})
    assert summ["measure"] is None and summ["return_median"] is None and summ["return_note"] is None, summ
    ir = {r[1]: dict(zip(cols, r)) for r in B.history_rows([dict(base, ticker="I", moat_evidence=summ)])}["I"]
    assert (ir["moat_return_measure"], ir["moat_return_median"], ir["moat_evidence_score"]) == ("", "", f"{summ['score']:.2f}"), ir
    # a record without the pillar keeps the median / note reading: unmeasured → blank, a note → the measure
    nop = {"governing": {"measure": "roe", "median": None, "median_note": None}}
    assert B.moat_summary({"moat_evidence": nop})["measure"] is None
    assert B.moat_summary({"moat_evidence": dict(nop, governing={"measure": "roe", "median": None, "median_note": "unbounded_high"})})["measure"] == "roe"


def test_history_csv_moat_sources_blank_vs_zero():
    """T-PY-11 (03b §7.1): a record with no declared scorecard leaves moat_sources / moat_widest_source BLANK (not declared
    is not "no source"); a declared scorecard with zero sources writes 0 / none; two sources, one wide, 2 / wide."""
    cols = list(B.HISTORY_COLUMNS)
    rows = [{"ticker": "LEG", "irr": 0.1, "moat_evidence": {"sources": None, "widest": None}},
            {"ticker": "ZERO", "irr": 0.1, "moat_evidence": {"sources": 0, "widest": "none"}},
            {"ticker": "TWO", "irr": 0.1, "moat_evidence": {"sources": 2, "widest": "wide"}}]
    out = {r[1]: dict(zip(cols, r)) for r in B.history_rows(rows)}
    assert (out["LEG"]["moat_sources"], out["LEG"]["moat_widest_source"]) == ("", "")
    assert (out["ZERO"]["moat_sources"], out["ZERO"]["moat_widest_source"]) == ("0", "none")
    assert (out["TWO"]["moat_sources"], out["TWO"]["moat_widest_source"]) == ("2", "wide")
    # the summary itself: a report-only record (no scorecard) has sources null; a declared one its count
    leg = B.moat_summary({"moat_evidence": {"status": "report_only", "sources": {"declared": False, "count": None, "widest": None}}})
    dec = B.moat_summary({"moat_evidence": {"status": "checked", "sources": {"declared": True, "count": 0, "widest": "none"}}})
    assert (leg["sources"], leg["widest"], dec["sources"], dec["widest"]) == (None, None, 0, "none")


def test_moat_summary_keys():
    """T-PY-12 (03b §7.2 + 10 §4): the row summary carries every key with the right types; industry is null when the
    industry pillar is insufficient_data; the JSON has no Infinity."""
    me = _example("moat_scorecard_consumer_subscription.json")["expected_moat_evidence"]
    types_ = {"score": (float, type(None)), "status": (str, type(None)), "within_tolerance": (bool, type(None)), "divergence": (float, type(None)),
              "core_score": (float, type(None)), "supporting_adjustment": (float, type(None)), "measure": (str, type(None)),
              "return_median": (float, type(None)), "return_note": (str, type(None)), "sources": (int, type(None)),
              "widest": (str, type(None)), "flags": list, "industry": (dict, type(None)), "fade_trend": (str, type(None)),
              "fade_in_sync": (bool, type(None)), "fade_direction": (str, type(None)), "hold_years": (int, type(None))}
    s = B.moat_summary({"moat_evidence": me}, {})
    assert set(s) == set(types_), sorted(set(s) ^ set(types_))
    _check_types(s, types_, "moat_summary")
    assert set(s["industry"]) == {"code", "level", "label", "ladder", "peers", "rank", "of"}
    me2 = json.loads(json.dumps(me))
    me2["pillars"]["industry_structure"] = {"source": "mechanical", "status": "insufficient_data", "reason": "4 peers (< 5)"}
    me2["governing"] = {"measure": "roic", "median": None, "median_note": "unbounded_high"}
    s2 = B.moat_summary({"moat_evidence": me2}, {"inputs": {"moat_trend": "eroding", "hold_years": 0}})
    assert s2["industry"] is None and s2["return_median"] is None and s2["return_note"] == "unbounded_high"
    assert (s2["fade_trend"], s2["hold_years"]) == ("eroding", 0)
    json.dumps(s2, allow_nan=False)
    assert B.moat_summary({}) is None and B.moat_summary({"moat_evidence": []}) is None


def test_meta_counts_moat_eroding():
    """T-PY-13 (03b §7.2, 10 §4): meta.counts.moat_eroding / moat_widening count the rows whose moat_evidence flags carry
    MOAT_EROSION / MOAT_WIDENING."""
    me = _example("moat_scorecard_consumer_subscription.json")["expected_moat_evidence"]
    with TempBase() as tb:
        tb.clone("APP", "ER1", **{"score.json": lambda s: dict(s, moat_evidence=dict(me, flags=["MOAT_EROSION"]))})
        tb.clone("APP", "ER2", **{"score.json": lambda s: dict(s, moat_evidence=dict(me, flags=["MOAT_EROSION", "IPRD_CHARGE_IN_WINDOW"]))})
        tb.clone("APP", "WID", **{"score.json": lambda s: dict(s, moat_evidence=dict(me, flags=["MOAT_WIDENING"]))})
        tb.build(only=TICKERS + ["ER1", "ER2", "WID"])
        c = tb.read("meta.json")["counts"]
        assert c["moat_eroding"] == 2 and c["moat_widening"] == 1 and c["moat_checked"] == 3, c


def _hold0(n):
    """dcf_numbers.json of a 5.7 run whose moat trend is eroding (M6): hold 0 on the scenarios above terminal growth."""
    scn = {k: dict(v, hold_years=(0 if k in ("base", "bull", "super_bull") else 2)) for k, v in (n.get("scenarios") or {}).items()}
    return dict(n, moat_trend="eroding", hold_years=0, scenarios=scn,
                inputs=dict(n.get("inputs") or {}, moat_trend="eroding", hold_years=0, hold_rule="above_terminal"))


def test_forecast_hold_fields():
    """T24 (design 10 §4, §7): forecast.hold_years / moat_trend / hold_by_scenario from the engine record (legacy: 2 / null /
    null); the row's moat_evidence.fade_trend is the ENGINE's trend (never moat_evidence.fade.trend, which make_score
    re-measures) beside fade_in_sync / fade_direction / hold_years — the drift fixture keeps "eroding" beside a fade that
    now reads stable; the history CSV's moat_trend / hold_years."""
    me = _example("moat_scorecard_consumer_subscription.json")["expected_moat_evidence"]
    drift = dict(me, fade={"version": 1, "status": "measured", "direction": "flat", "trend": "stable", "hold_years": 2,
                           "in_sync": False, "engine": {"moat_trend": "eroding", "hold_years": 0, "source": "inputs"}},
                 gate_drift=[{"gate": "fade_sync", "was": "eroding", "now": "stable"}])
    # [rebase L3b A14, L6 review r3] a score.json from ANOTHER run (the newer run on disk is not scored yet): make_score's
    # trend test there checked the run IT scored, so the row's fade_in_sync / fade_direction are null; fade_trend and
    # hold_years stay the engine record's
    insync = dict(me, flags=["MOAT_EROSION"], fade={"version": 1, "status": "measured", "direction": "eroding", "trend": "eroding", "hold_years": 0,
                                                     "in_sync": True, "engine": {"moat_trend": "eroding", "hold_years": 0, "source": "inputs"}})
    with TempBase() as tb:
        tb.clone("APP", "HZ", **{"dcf_numbers.json": _hold0, "score.json": lambda s: dict(s, moat_evidence=drift)})
        tb.clone("APP", "HM", **{"dcf_numbers.json": lambda n: dict(_hold0(n), as_of="2026-10-20"),   # a newer engine run
                                 "score.json": lambda s: dict(s, moat_evidence=insync)})
        res = tb.build(only=TICKERS + ["HZ", "HM"], attachment=True, prerender=False, now=datetime.datetime(2026, 10, 21, 19, 7, tzinfo=B.NY))
        hm = tb.record("HM")
        assert hm["score_from_run"]["matches"] is False and (hm["live_withheld"] or {}).get("reason") == "score_not_from_this_run", (hm["score_from_run"], hm["live_withheld"])
        m2 = hm["row"]["moat_evidence"]
        assert (m2["fade_trend"], m2["fade_in_sync"], m2["fade_direction"], m2["hold_years"]) == ("eroding", None, None, 0), m2
        assert tb.record("HZ")["score_from_run"]["matches"] is True, "A14: the hold-0 / drift fixture must stay this run's score"
        fc = tb.record("HZ")["forecast"]
        assert fc["hold_years"] == 0 and fc["moat_trend"] == "eroding", (fc["hold_years"], fc["moat_trend"])
        assert fc["hold_by_scenario"] == {"super_bear": 2, "bear": 2, "base": 0, "bull": 0, "super_bull": 0}, fc["hold_by_scenario"]
        for t in TICKERS:
            f = tb.record(t)["forecast"]
            assert f["hold_years"] == 2 and f["moat_trend"] is None and f["hold_by_scenario"] is None, t
        m = tb.record("HZ")["row"]["moat_evidence"]
        assert (m["fade_trend"], m["fade_in_sync"], m["fade_direction"], m["hold_years"]) == ("eroding", False, "flat", 0), m
        hist = {r[1]: dict(zip(B.HISTORY_COLUMNS, r)) for r in _read_csv(res["history"][0])[1][1:]}
        assert (hist["HZ"]["moat_trend"], hist["HZ"]["hold_years"]) == ("eroding", "0")
        assert (hist["APP"]["moat_trend"], hist["APP"]["hold_years"]) == ("", "2")
    # the local fallback when the engine lacks the reader (lane L3b not merged): the same reads
    assert B.recorded_hold_years({}) == 2 and B.recorded_hold_years({"inputs": {"hold_years": 3}}) == 3
    assert B.recorded_hold_years({"hold_years": "x"}) is None and B.engine_moat_trend({"moat_trend": "widening"}) == "widening"
    assert B.engine_moat_trend({"inputs": {"moat_trend": "bogus"}}) is None
    # A14 at the function: from_run decides; without it moat_summary asks score_from_run itself (no run → not this run's)
    on, off = (B.moat_summary({"moat_evidence": insync}, {}, from_run=f) for f in (True, False))
    assert (on["fade_in_sync"], on["fade_direction"], off["fade_in_sync"], off["fade_direction"]) == (True, "eroding", None, None)
    assert B.moat_summary({"moat_evidence": insync})["fade_in_sync"] is None


def test_every_committed_folder_builds_with_the_new_fields():
    """T-PY-9 (compatibility, rebase B15): every folder of the real base builds into a temp --site-dir with the rulings'
    fields: no failure, every qualifying folder written (the count is computed, never pinned), every row's tier_override
    == (tier != the published numbers tier) and tier_notched == misfit_notch.applies, every record strict JSON with a
    quote_check status of the four. While no committed score.json carries misfit_notch (before the R5 rebuild data PR)
    every row's tier_override equals the old value and no row is notched."""
    t0 = time.time()
    qualifying, seen = 0, set()
    for p in sorted(glob.glob(os.path.join(BASE, "*", "score.json"))):
        fname = os.path.basename(os.path.dirname(p))
        if fname.startswith(("_", ".")):
            continue
        c = B.load_light(os.path.dirname(p))
        if not c["score"]:
            continue
        t = B.ticker_key(c)
        if t in seen:
            continue
        seen.add(t)
        qualifying += bool(B.qualifies(c))
    any_block = any(isinstance(B.jload(p), dict) and "misfit_notch" in B.jload(p) for p in glob.glob(os.path.join(BASE, "*", "score.json")))
    site = tempfile.mkdtemp(prefix="build_site_all_")
    try:
        res = B.build(base=BASE, site_dir=os.path.join(site, "site"), quiet=True, prerender=False)
        assert res["failed"] == [], res["failed"]
        assert len(res["written"]) == qualifying and qualifying > 400, (len(res["written"]), qualifying)
        statuses = set()
        for r in res["rows"]:
            pub = B.published_numbers_tier(r["tier_by_numbers"], r["misfit_notch"])
            assert r["tier_override"] == bool(r["tier_by_numbers"] and r["tier"] != pub), r["ticker"]
            assert r["tier_notched"] == bool(r["misfit_notch"] and r["misfit_notch"]["applies"]), r["ticker"]
            if not any_block:
                assert r["misfit_notch"] is None and r["tier_override"] == bool(r["tier_by_numbers"] and r["tier"] != r["tier_by_numbers"])
        for f in glob.glob(os.path.join(site, "site", "data", "*.json")):
            if f.endswith(B.STATEMENTS_SUFFIX):
                continue
            rec = strict_json(f)
            q = rec["quote_check"]
            assert q is None or q["status"] in ("pass", "fail", "legacy", "error"), (f, q)
            statuses.add(q["status"] if q else None)
            assert rec["score_from_run"]["matches"] in (True, False)
        assert "legacy" in statuses, statuses
        print(f"  (T-PY-9: {qualifying} folders built in {time.time() - t0:.0f} s; quote_check statuses {sorted(map(str, statuses))})")
    finally:
        shutil.rmtree(site, ignore_errors=True)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            import traceback
            traceback.print_exc()
            print(f"FAIL {name}: {e}")
    sys.exit(1 if failed else 0)
