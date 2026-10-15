#!/usr/bin/env python3
"""reprice.py tests (v5.4). Run: python3 _system/tests/test_reprice.py
(or python3 -m pytest _system/tests). No network, no writes inside the repo:
everything comes from reprice.reprice() (a pure function), the APP files
already in the repo, in-memory variants of them, and a throwaway temp dir
used as STOCKS_BASE for the file-level (reprice_folder) cases.

1. Repricing APP at its SCORED price reproduces the scored weighted IRR and
   every scenario IRR to 1e-9 — the live path is the scored path. The same
   holds for a 5.4-style record (stored `paths` / `growth_paths` rounded to
   6 dp): replay_paths prefers the exact replay from the inputs.
2. Repricing at a lower price gives a higher IRR (and a higher upside), at a
   higher price a lower one; the price-independent IVs do not move.
3. replay_paths: the weighted path is the probability-weighted sum of the
   scenario paths; stored paths are the fallback (no inputs, or a replay that
   disagrees with the record beyond rounding), never the first choice.
4. Ineligible runs (Tier F, data gap, no inputs) raise Skip, never write.
5. An agent tier override (score.json tier_final != tier_by_numbers) is
   preserved in `tier` while the live numbers tier equals the scored numbers
   tier, and superseded (flagged) only when the numbers tier moved.
6. live_price refuses a prices.json without last_date, for another ticker,
   or stale against the scored run (fetched_at before as_of; without
   fetched_at, last_date more than STALE_DAYS before as_of); a weekend gap
   is accepted.
7. reprice_folder: unreadable dcf_numbers.json / prices.json -> Skip and the
   stale live.json is removed; unreadable score.json degrades to a written
   live.json with score_note; a foreign prices.json -> Skip.
"""
import os, sys, json, math, copy, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
BASE = os.path.dirname(SYS)
sys.path.insert(0, SYS)
import dcf_engine as E  # noqa: E402
import reprice as R  # noqa: E402

LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]


def _app():
    n = json.load(open(os.path.join(BASE, "APP", "dcf_numbers.json"), encoding="utf-8"))
    s = json.load(open(os.path.join(BASE, "APP", "score.json"), encoding="utf-8"))
    return n, s


def _app54():
    """APP as engine 5.4 would store it: paths / growth_paths rounded to 6 dp
    (dcf_engine main: `[round(f, 6) for f in flows]`) and the release stamp."""
    n, s = _app()
    paths, gpaths = E.replay_paths({k: v for k, v in n.items() if k not in ("paths", "growth_paths")})
    assert paths and gpaths
    m = copy.deepcopy(n)
    m["paths"] = {k: [round(f, 6) for f in v] for k, v in paths.items()}
    m["growth_paths"] = {k: [round(g, 6) for g in v] for k, v in gpaths.items()}
    m["engine_release"] = "5.4.0"
    return m, s


def close(a, b, tol=1e-9):
    return a is not None and b is not None and math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def _check_reproduces(n, s):
    live = R.reprice(n, n["price"], "scored-day", s, today="2026-10-14")
    assert close(live["irr_weighted"], n["implied_irr_weighted"]), f"weighted {live['irr_weighted']} vs {n['implied_irr_weighted']}"
    for k in LABELS:
        assert close(live["scenarios"][k]["irr"], n["scenarios"][k]["irr"]), f"{k}: {live['scenarios'][k]['irr']} vs {n['scenarios'][k]['irr']}"
    assert live["tier"] == live["tier_display"] == live["tier_by_numbers"] == n["tier_by_numbers"]
    assert not live["delta"]["tier_changed"] and not live["delta"]["tier_changed_vs_final"]
    assert close(live["delta"]["irr_pp"], 0.0)
    assert close(live["price_change_pct"], 0.0)
    assert close(live["iv_at_15"], n["weighted"]["iv_at_15"]) and close(live["iv_at_12"], n["weighted"]["iv_at_12"])
    assert close(live["upside_at_15"], n["upside_at_15"])
    assert close(live["irr_base"], n["implied_irr_base"])
    assert close(live["irr_low"], min(n["scenarios"][k]["irr"] for k in LABELS))
    assert close(live["irr_high"], max(n["scenarios"][k]["irr"] for k in LABELS))
    assert close(live["market_cap_est"], n["price"] * n["shares_diluted_latest"])
    assert live["in_scope_under_40b"] is False  # APP is the >$40B pilot exception
    assert live["scored"]["tier_final"] == s["tier_final"] and live["scored"]["tier_by_numbers"] == n["tier_by_numbers"]
    assert live["override_active"] is (s["tier_final"] != n["tier_by_numbers"]) and live["override_superseded"] is False
    assert live["price_source"] == "prices.json (Nasdaq last close)" and live["basis"] == R.BASIS
    assert live["as_of"] == "2026-10-14" and live["scored_date"] == n["as_of"]
    # iv_at_20 / 25 are replayed for a pre-5.4 run: a lower rate means a higher value
    assert live["iv_at_25"] < live["iv_at_20"] < live["iv_at_15"] < live["iv_at_12"]
    # the hurdle prices are the prices at which the A / S tiers clear
    at20 = R.reprice(n, live["iv_at_20"], None, s, today="2026-10-14")
    at25 = R.reprice(n, live["iv_at_25"], None, s, today="2026-10-14")
    assert close(at20["irr_weighted"], 0.20, 1e-6) and close(at25["irr_weighted"], 0.25, 1e-6)
    for k in ("ticker", "as_of", "price", "price_date", "price_source", "scored_price", "scored_date", "price_change_pct",
              "irr_weighted", "tier", "tier_display", "tier_by_numbers", "override_active", "override_superseded",
              "irr_base", "irr_bear", "irr_bull", "tier_bear", "tier_bull", "irr_low", "irr_high",
              "irr_capped", "irr_at_floor", "scenarios", "iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25", "upside_at_15",
              "upside_at_12", "market_cap_est", "in_scope_under_40b", "scored", "delta", "engine_release_of_run", "basis"):
        assert k in live, f"live.json missing {k}"
    for k in ("irr_weighted", "tier_by_numbers", "tier_final", "tier_override_reason", "upside_at_15"):
        assert k in live["scored"], f"live.json scored block missing {k}"
    for k in ("irr_pp", "tier_changed", "tier_changed_vs_final"):
        assert k in live["delta"], f"live.json delta missing {k}"
    return live


def test_reprice_at_scored_price_reproduces_run():
    n, s = _app()
    _check_reproduces(n, s)


def test_reprice_reproduces_run_with_stored_rounded_paths():
    """Engine 5.4 stores the paths rounded to 6 dp; the live IRR must still
    equal the scored one bit-for-bit, because the replay from the recorded
    inputs is preferred over the rounded copy."""
    m, s = _app54()
    live = _check_reproduces(m, s)
    assert live["engine_release_of_run"] == "5.4.0"
    paths, gpaths = E.replay_paths(m)
    for k in LABELS + ["weighted"]:
        assert all(abs(a - b) <= 5e-7 for a, b in zip(paths[k], m["paths"][k])), f"{k}: replay differs from the stored copy by more than rounding"
        assert any(a != b for a, b in zip(paths[k], m["paths"][k])), f"{k}: expected the exact replay, got the rounded copy"
    probs = m["inputs"]["probs"]
    for t in range(15):
        assert close(paths["weighted"][t], sum(probs[i] * paths[LABELS[i]][t] for i in range(5)))


def test_lower_price_means_higher_irr():
    n, s = _app()
    at = R.reprice(n, n["price"], None, s, today="2026-10-14")
    lower = R.reprice(n, n["price"] * 0.9, None, s, today="2026-10-14")
    higher = R.reprice(n, n["price"] * 1.1, None, s, today="2026-10-14")
    assert lower["irr_weighted"] > at["irr_weighted"] > higher["irr_weighted"]
    assert lower["delta"]["irr_pp"] > 0 > higher["delta"]["irr_pp"]
    for k in LABELS:
        assert lower["scenarios"][k]["irr"] > at["scenarios"][k]["irr"] > higher["scenarios"][k]["irr"], k
    assert lower["upside_at_15"] > at["upside_at_15"] > higher["upside_at_15"]
    for k in ("iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25"):
        assert close(lower[k], at[k]) and close(higher[k], at[k]), f"{k} must not move with the price"
    assert close(lower["price_change_pct"], -10.0) and close(higher["price_change_pct"], 10.0)
    assert close(lower["market_cap_est"], at["market_cap_est"] * 0.9)
    # the repo's actual last close is below the scored price -> a higher live IRR
    p = json.load(open(os.path.join(BASE, "APP", "prices.json"), encoding="utf-8"))
    px = p["stats"]["last"]
    if px < n["price"]:
        live = R.reprice(n, px, p["stats"]["last_date"], s, today="2026-10-14")
        assert live["irr_weighted"] > n["implied_irr_weighted"]


def test_replay_paths_weighted_is_probability_weighted_sum():
    n, _ = _app()
    paths, gpaths = E.replay_paths(n)
    assert paths and gpaths and set(paths) == set(LABELS + ["weighted"]) and set(gpaths) == set(LABELS)
    probs = n["inputs"]["probs"]
    for t in range(15):
        assert close(paths["weighted"][t], sum(probs[i] * paths[LABELS[i]][t] for i in range(5)))
    for k in LABELS:
        assert len(paths[k]) == 15 and close(paths[k][0], n["base_oe_per_share"] * n["inputs"]["mults"][LABELS.index(k)] * (1 + gpaths[k][0]))
        assert close(round(gpaths[k][0], 4), n["scenarios"][k]["g_start"], 1e-12)
    # stored paths are the fallback when there are no inputs to replay from
    stored = {"paths": {"x": [1]}, "growth_paths": {"x": [0.1]}}
    assert E.replay_paths(stored) == ({"x": [1]}, {"x": [0.1]})
    assert E.replay_paths({}) == (None, None)
    assert E.replay_paths({"inputs": {}, "scenarios": {}, "base_oe_per_share": 1, "g_base": 0.1}) == (None, None)
    bad = copy.deepcopy(n); bad["inputs"] = dict(bad["inputs"], offsets=[0.0])
    assert E.replay_paths(bad) == (None, None)
    # malformed inputs but a stored copy -> the stored copy
    bad["paths"], bad["growth_paths"] = {"x": [1]}, {"x": [0.1]}
    assert E.replay_paths(bad) == ({"x": [1]}, {"x": [0.1]})
    # a stored copy that disagrees with the replay beyond rounding is the engine's
    # own record and wins over a drifted replay
    m, _ = _app54()
    m["paths"] = {k: [f * 2 for f in v] for k, v in m["paths"].items()}
    p2, g2 = E.replay_paths(m)
    assert p2 is m["paths"] and g2 is m["growth_paths"]


def test_ineligible_runs_are_skipped():
    n, s = _app()
    for mutate, why in ((lambda m: m.update(tier_by_numbers="F"), "Tier F"),
                        (lambda m: m.update(tier_by_numbers=None, data_gap_uncovered=["capex"]), "data gap"),
                        (lambda m: m.pop("inputs"), "no recorded inputs"),
                        (lambda m: m.update(engine_version=4), "pre-v5"),
                        (lambda m: m.update(base_oe_per_share=-1.0), "not positive"),
                        (lambda m: m.pop("scenarios"), "no scenarios")):
        m = copy.deepcopy(n); mutate(m)
        try:
            R.reprice(m, 100.0, None, s, today="2026-10-14")
            raise AssertionError(f"expected Skip for {why}")
        except R.Skip as e:
            assert why in str(e), f"{why}: {e}"


def test_agent_tier_override_is_preserved_until_numbers_move():
    n, s = _app()
    assert n["tier_by_numbers"] == "B"
    over = dict(s, tier_final="C", tier_by_numbers="B", tier_override_reason="test: sized to the conservative end")
    # price barely moved -> numbers tier still B -> the override (C) stays on screen
    live = R.reprice(n, n["price"] * 0.99, None, over, today="2026-10-14")
    assert live["tier_by_numbers"] == "B" and live["tier"] == live["tier_display"] == "C"
    assert live["override_active"] is True and live["override_superseded"] is False
    assert live["delta"]["tier_changed"] is False and live["delta"]["tier_changed_vs_final"] is False
    assert live["scored"]["tier_final"] == "C" and live["scored"]["tier_override_reason"].startswith("test:")
    # price collapsed -> numbers tier S -> the live numbers tier shows, flagged
    live = R.reprice(n, live["iv_at_25"] * 0.9, None, over, today="2026-10-14")
    assert live["tier_by_numbers"] == "S" and live["tier"] == "S"
    assert live["override_active"] is True and live["override_superseded"] is True
    assert live["delta"]["tier_changed"] is True and live["delta"]["tier_changed_vs_final"] is True
    # no override: tier == numbers tier, nothing flagged, no reason carried
    live = R.reprice(n, n["price"], None, s, today="2026-10-14")
    assert live["override_active"] is False and live["scored"]["tier_override_reason"] is None
    # no score.json at all: numbers tier, tier_final unknown
    live = R.reprice(n, n["price"], None, None, today="2026-10-14")
    assert live["tier"] == "B" and live["scored"]["tier_final"] is None and live["override_active"] is False
    assert live["delta"]["tier_changed_vs_final"] is False
    # the repo's own override case when one is present (EXPE: numbers A, final B on 2026-10-14)
    ep = os.path.join(BASE, "EXPE")
    if os.path.isfile(os.path.join(ep, "dcf_numbers.json")) and os.path.isfile(os.path.join(ep, "score.json")):
        en = json.load(open(os.path.join(ep, "dcf_numbers.json"), encoding="utf-8"))
        es = json.load(open(os.path.join(ep, "score.json"), encoding="utf-8"))
        if en.get("inputs") and es.get("tier_final") and es["tier_final"] != en.get("tier_by_numbers") and en.get("tier_by_numbers") not in (None, "F"):
            live = R.reprice(en, en["price"], None, es, today="2026-10-14")
            assert live["tier"] == es["tier_final"] and live["tier_by_numbers"] == en["tier_by_numbers"]
            assert live["override_active"] and not live["override_superseded"] and not live["delta"]["tier_changed_vs_final"]


def test_live_price_refuses_missing_foreign_and_stale():
    def skip(prices, *a, why=""):
        try:
            R.live_price(prices, *a)
            raise AssertionError(f"expected Skip: {why}")
        except R.Skip as e:
            assert why in str(e), f"{why!r} not in {e}"
    skip({"stats": {}}, why="no stats.last")
    skip({"stats": {"last": 262.19}}, why="no stats.last_date")
    skip("nope", why="not an object")
    ok = {"ticker": "APP", "stats": {"last": 262.19, "last_date": "2026-10-14"}}
    assert R.live_price(ok) == (262.19, "2026-10-14")
    assert R.live_price(ok, "APP", "2026-10-14") == (262.19, "2026-10-14")
    assert R.live_price(ok, "app", "2026-10-14") == (262.19, "2026-10-14")
    skip(dict(ok, ticker="ZS"), "APP", "2026-10-14", why="belongs to ZS, not APP")
    # no fetched_at: last_date more than STALE_DAYS before as_of is a failed refresh
    skip({"ticker": "APP", "stats": {"last": 400.0, "last_date": "2026-09-01"}}, "APP", "2026-10-14", why="predates the scored run 2026-10-14")
    # ...but a weekend / holiday gap is not (Friday close, scored the Tuesday after a Monday holiday)
    assert R.live_price({"ticker": "APP", "stats": {"last": 1.0, "last_date": "2026-10-09"}}, "APP", "2026-10-13") == (1.0, "2026-10-09")
    skip({"ticker": "APP", "stats": {"last": 1.0, "last_date": "2026-10-08"}}, "APP", "2026-10-13", why="predates")
    # fetched_at decides when present: refreshed on / after the scored day is fresh whatever last_date is
    fresh = {"ticker": "APP", "fetched_at": "2026-10-14T19:05:00-04:00", "stats": {"last": 1.0, "last_date": "2026-10-01"}}
    assert R.live_price(fresh, "APP", "2026-10-14") == (1.0, "2026-10-01")
    skip(dict(fresh, fetched_at="2026-10-13T19:05:00-04:00"), "APP", "2026-10-14", why="fetched 2026-10-13 predates the scored run")
    # a later close than the scored day is always fine
    assert R.live_price({"ticker": "APP", "stats": {"last": 1.0, "last_date": "2026-10-20"}}, "APP", "2026-10-14") == (1.0, "2026-10-20")


def test_reprice_folder_unreadable_and_foreign_files():
    n, s = _app()
    prices = json.load(open(os.path.join(BASE, "APP", "prices.json"), encoding="utf-8"))
    tmp = tempfile.mkdtemp(prefix="reprice_test_")
    old_base = R.BASE
    try:
        R.BASE = tmp

        def folder(name, numbers="ok", prices_="ok", score="ok", stale_live=True):
            d = os.path.join(tmp, name); os.makedirs(d, exist_ok=True)
            for fn, what, good in (("dcf_numbers.json", numbers, n), ("prices.json", prices_, dict(prices, ticker=name)), ("score.json", score, s)):
                if what == "ok":
                    json.dump(good, open(os.path.join(d, fn), "w", encoding="utf-8"))
                elif what == "bad":
                    open(os.path.join(d, fn), "w", encoding="utf-8").write("{not json")
                elif what == "foreign":
                    json.dump(prices, open(os.path.join(d, fn), "w", encoding="utf-8"))  # ticker APP in another folder
            if stale_live:
                open(os.path.join(d, "live.json"), "w", encoding="utf-8").write("{}")
            return d

        def expect_skip(name, why):
            d = os.path.join(tmp, name)
            try:
                R.reprice_folder(name)
                raise AssertionError(f"{name}: expected Skip ({why})")
            except R.Skip as e:
                assert why in str(e), f"{name}: {why!r} not in {e}"
            assert not os.path.exists(os.path.join(d, "live.json")), f"{name}: stale live.json left in place"

        folder("BADN", numbers="bad"); expect_skip("BADN", "dcf_numbers.json unreadable")
        folder("BADP", prices_="bad"); expect_skip("BADP", "prices.json unreadable")
        folder("FOREIGN", prices_="foreign"); expect_skip("FOREIGN", "belongs to APP, not FOREIGN")
        folder("NOP", prices_="missing"); expect_skip("NOP", "no prices.json")
        folder("NON", numbers="missing"); expect_skip("NON", "no dcf_numbers.json")
        d = folder("BADS", score="bad")
        live = R.reprice_folder("BADS")
        assert os.path.isfile(os.path.join(d, "live.json")) and "score.json unreadable" in live["score_note"]
        assert live["scored"]["tier_final"] is None and live["override_active"] is False
        d = folder("GOOD")
        live = R.reprice_folder("GOOD")
        assert "score_note" not in live and live["scored"]["tier_final"] == s["tier_final"]
        assert json.load(open(os.path.join(d, "live.json"), encoding="utf-8"))["price"] == prices["stats"]["last"]
        # --all never lets one bad folder stop the sweep and reports every reason
        names = R.company_folders()
        assert set(names) == {"BADN", "BADP", "BADS", "FOREIGN", "GOOD", "NOP"}
    finally:
        R.BASE = old_base
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if fails else 0)
