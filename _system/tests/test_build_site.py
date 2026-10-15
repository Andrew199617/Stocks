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
"""
import datetime
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
            "shareholder_yield": (float, type(None)), "has": dict, "watchlist": bool}
HAS_KEYS = ("prices", "fundamentals", "dividends", "segments", "live", "analysis", "second_pass", "statements", "profile")
RECORD_KEYS = ("ticker", "name", "sector", "folder", "built_at", "built_from_mtime", "row", "score", "numbers", "forecast", "live", "profile",
               "history", "fundamentals", "prices", "segments", "ttm", "judgment", "registry", "analysis_md", "second_pass_md", "files")
FORECAST_KEYS = ("paths", "growth_paths", "sensitivity", "hurdle_prices", "inputs", "g_base", "g_blend", "g_terminal", "cap_years",
                 "growth_components", "growth_components_adjusted", "share_cagr", "share_count_adj", "share_adj_basis", "replayed")


class TempBase:
    """A temporary STOCKS_BASE holding copies of the test folders."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix="build_site_test_")
        os.makedirs(os.path.join(self.dir, "_system"))
        for t in TICKERS:
            shutil.copytree(os.path.join(BASE, t), os.path.join(self.dir, t))
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
        with open(os.path.join(self.dir, *parts), "w", encoding="utf-8") as f:
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
                assert isinstance(row["irr_live"], float)  # all three carry live.json
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
