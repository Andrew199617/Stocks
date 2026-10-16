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

The Nasdaq caches (prices.json, live.json, street.json) are gitignored, so
a fresh clone has none: TempBase removes whatever the copies carried and
installs the frozen copies in test_build_site_fixtures.json (or nothing,
with caches=False), so no assertion depends on the machine or the market.
"""
import datetime
import glob
import json
import os
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
            "live_withheld": bool, "split_restated": (dict, type(None))}
HAS_KEYS = ("prices", "fundamentals", "dividends", "segments", "live", "analysis", "second_pass", "statements", "profile")
RECORD_KEYS = ("ticker", "name", "sector", "folder", "built_at", "built_from_mtime", "row", "score", "numbers", "forecast", "live", "profile",
               "history", "fundamentals", "prices", "segments", "ttm", "judgment", "registry", "analysis_md", "second_pass_md", "files",
               "live_withheld", "split_restated")
FORECAST_KEYS = ("paths", "growth_paths", "sensitivity", "hurdle_prices", "inputs", "g_base", "g_blend", "g_terminal", "cap_years",
                 "growth_components", "growth_components_adjusted", "share_cagr", "share_count_adj", "share_adj_basis", "replayed")


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
                      "profile": isinstance(B.jload(os.path.join(folder, "profile.json")), dict)}
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
        assert {r[1]: r[-1] for r in _read_csv(path)[1][1:]} == {"APP": "false", "KR": "true", "ZS": "false", "AEE": "false"}
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
            written = F.price_dividends(core, p, d, "prices.json stats.last")
            assert _json(served) == _json(written), (path, p)
            assert served["price"] == p and served["price_date"] == d and served["price_source"] == "prices.json stats.last"
            if div["price"] is not None:  # a price present on both sides: only the volatile leaves differ
                assert S.canonical({"dividends": served}, F.PRICE_LEAVES) == S.canonical({"dividends": own}, F.PRICE_LEAVES), (path, p)
        assert fund == B.jload(path), "nothing is modified in place"
    assert n >= 80, n


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
            "iv_at_20": 30.0, "iv_at_25": 20.0, "split_factor": 2.0, "basis_check": {"factor": 2.0, "split": "2:1"}}
    c = {"folder": "T", "path": "", "ticker": "T", "score": {"ticker": "T", "price": 100.0, "iv_at_15": 80.0, "implied_irr": 0.12,
                                                            "analysis_date": "2026-10-14"},
         "numbers": {"engine_version": 5, "data_gap": [], "price": 100.0}, "live": live, "history": [], "files": []}
    rec = B.build_record(c, {}, "2026-10-20T19:00:00-04:00", 0.0)
    assert rec["row"]["iv20"] == 30.0 and rec["row"]["iv25"] == 20.0 and rec["row"]["iv15"] == 40.0 and rec["row"]["price"] == 50.0
    assert rec["score"]["price"] == 50.0 and rec["numbers"]["price"] == 50.0 and rec["split_restated"]["split"] == "2:1"
    assert c["score"]["price"] == 100.0 and c["live"]["iv_at_20"] == 30.0, "the loaded files are never modified"
    assert B.live_split({"split_factor": 1.0}) == (None, None) and B.live_split({"basis_check": {"factor": 3.0}}) == (3.0, "3x")
    assert B.live_split(None) == (None, None) and B.live_split({"split_factor": -2}) == (None, None)


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
        assert "older than the scored analysis" in w["note"]
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
    assert "2026-10-01 run" in w["note"] and "reprice.py" in w["note"], w["note"]
    old_run["live"]["scored_date"] = "2026-10-16"
    assert B.live_shown(old_run) == (old_run["live"], None), "same run, close after scoring: shown"


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
