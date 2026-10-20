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
   stale live.json is removed; so is an unreadable score.json, or one from
   another engine run (Codex review round 11 of PR #47: it cannot vouch for
   the run, so no live figures); a foreign prices.json -> Skip.
8. Per-share basis (Codex review of PR #2): a split between the scored run
   and the last close is divided out of every per-share value — the
   reviewer's synthetic APP 2:1 ($272.28 -> $136.14) keeps 18.4268% / B
   instead of 28.7236% / S; an ordinary quote difference changes nothing;
   a ratio that is neither ordinary nor exactly one clean split, or no
   close near the scored date, is refused (no live.json).
   Second round: on scoring night Nasdaq has not posted the scored
   session's row yet, so no split can be in the closes and the quote's gap
   to the prior close (a -32% day, a -15% earnings day) is neither fitted
   to a split nor refused; a one-session move after the scored date with a
   split's exact size is held while fresh (an unadjusted split would hide
   behind it), and repriced once it has stood HOLD_SESSIONS sessions.
9. Score identity (Codex review of PR #2): an override is read only from a
   score.json built from THIS run — the reviewer's stale B/B score against
   a rerun at $217.824 (21.2495% / A) no longer shows the stale B; since
   Codex review round 11 of PR #47 it writes no live.json at all (Skip),
   any one identity field off included.
10. ADS market cap (engine 5.5, decision 1): the live market cap divides by
   numbers.ads_ratio.ratio (synthetic ratios 100 / 2 / 0.5, also after a
   split since scoring) and in_scope_under_40b follows it; a run without an
   ADS ratio is bit-identical to price × shares_diluted_latest when its
   market_cap_basis.shares_source is diluted_latest (or it has no basis
   record); otherwise market_cap_basis.shares_used (a scale- or
   split-corrected count, or the dei_latest cover-page count) is the count
   used, and the module docstring says so (FIX_DECISIONS_R1 M6).
prices.json is a gitignored cache (a fresh clone has none), so every case
builds its own synthetic prices.json; only the committed APP / EXPE judgment
records are read from the repo.
"""
import os, sys, io, json, math, copy, tempfile, shutil, contextlib

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
    # make_score.py (v5.4) copies the run's release into score.json: a score
    # built from this run carries it, one from the pre-5.4 run does not
    return m, dict(s, engine_release="5.4.0")


# APP's real closes around its scored run (scored 2026-10-14 at $272.28, which
# is the 2026-10-13 close). prices.json is a gitignored cache, so the tests
# never read the repo's copy.
APP_DAILY = [["2026-10-12", 270.87], ["2026-10-13", 272.28], ["2026-10-14", 262.19]]


def _prices(ticker="APP", daily=None, last=None, last_date=None, weekly=None,
            fetched_at="2026-10-15T19:29:39-04:00"):
    """A minimal prices.json as prices.py writes it (split-adjusted closes)."""
    daily = APP_DAILY if daily is None else daily
    if last is None and daily:
        last_date, last = daily[-1]
    return {"ticker": ticker, "source": "Nasdaq historical quotes API (api.nasdaq.com)", "currency": "USD",
            "as_of": last_date, "fetched_at": fetched_at, "daily_1y": [list(r) for r in daily],
            "weekly": [list(r) for r in (weekly or [])], "monthly": [],
            "stats": {"last": last, "last_date": last_date}}


def _ref(close):
    """prices.json whose daily series reaches the scored session (2026-10-14)
    with `close` on it and on the session before: the ratio test runs (a
    series that stops before the scored session never fits a split)."""
    return _prices(daily=[["2026-10-13", close], ["2026-10-14", close]])


def _split_prices(k, last=None, last_date="2026-10-20"):
    """APP's closes after a k-for-1 split on 2026-10-19, as Nasdaq serves them
    (history divided by k); the last close is the split-day close unless given."""
    daily = [[d, round(c / k, 2)] for d, c in APP_DAILY]
    lc = round(272.28 / k, 2) if last is None else last
    daily += [["2026-10-19", lc], [last_date, lc]]
    return _prices(daily=daily, fetched_at=f"{last_date}T19:30:00-04:00")


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
              "upside_at_12", "market_cap_est", "in_scope_under_40b", "scored", "delta", "engine_release_of_run", "basis",
              "split_factor", "basis_check", "score_json_fresh", "score_mismatch"):
        assert k in live, f"live.json missing {k}"
    # no prices.json passed: basis unchecked, factor 1; the score is this run's own
    assert live["split_factor"] == 1.0 and live["basis_check"]["status"] == "unchecked"
    assert live["score_json_fresh"] is True and live["score_mismatch"] is None and "score_note" not in live
    # ...and with APP's real closes passed the basis is "ok" and nothing else changes
    checked = R.reprice(n, n["price"], "scored-day", s, today="2026-10-14", prices=_prices())
    assert checked["basis_check"]["status"] == "ok" and checked["split_factor"] == 1.0
    assert {k: v for k, v in checked.items() if k != "basis_check"} == {k: v for k, v in live.items() if k != "basis_check"}
    for k in ("irr_weighted", "tier_by_numbers", "tier_final", "tier_override_reason", "upside_at_15"):
        assert k in live["scored"], f"live.json scored block missing {k}"
    for k in ("irr_pp", "tier_changed", "tier_changed_vs_final"):
        assert k in live["delta"], f"live.json delta missing {k}"
    return live


def test_reprice_at_scored_price_reproduces_run():
    n, s = _app()
    _check_reproduces(n, s)


def test_ads_ratio_divides_live_market_cap():
    """ADS runs: the live cap is on the scored basis — price x ordinary
    shares / ads_ratio (2026-10-18 engine fix) — and the scope flag follows
    it. APP's numbers with a ratio-10 ads_ratio recorded: $93.11B / 10 =
    $9.31B, in scope; without the division the live cap (and the flag)
    would contradict the scored run's market_cap_est."""
    n, s = _app54()
    n["ads_ratio"] = {"ratio": 10.0, "source": "test fixture", "reason": "ADS shape"}
    n["market_cap_est"] = n["price"] * n["shares_diluted_latest"] / 10.0
    live = R.reprice(n, n["price"], "scored-day", s, today="2026-10-14")
    assert close(live["market_cap_est"], n["market_cap_est"]), \
        f"live cap {live['market_cap_est']} vs scored {n['market_cap_est']}"
    assert live["in_scope_under_40b"] is True


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
    # APP's real 2026-10-14 close ($262.19) is below the scored $272.28 -> a higher live IRR,
    # the same with the prices.json basis check on (an ordinary day, factor 1)
    p = _prices()
    px, pd = R.live_price(p, "APP", n["as_of"])
    live = R.reprice(n, px, pd, s, today="2026-10-14", prices=p)
    assert px == 262.19 and live["irr_weighted"] > n["implied_irr_weighted"]
    assert live["split_factor"] == 1.0 and live["basis_check"]["status"] == "ok"
    assert live["basis_check"]["ref_close_date"] == "2026-10-13" and live["basis_check"]["log_residual"] == 0.0


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


def _write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f)


def test_reprice_folder_unreadable_and_foreign_files():
    n, s = _app()
    prices = _prices()
    tmp = tempfile.mkdtemp(prefix="reprice_test_")
    old_base = R.BASE
    try:
        R.BASE = tmp

        def folder(name, numbers="ok", prices_="ok", score="ok", stale_live=True, fund=None):
            d = os.path.join(tmp, name); os.makedirs(d, exist_ok=True)
            for fn, what, good in (("dcf_numbers.json", numbers, n), ("prices.json", prices_, dict(prices, ticker=name)), ("score.json", score, s)):
                if isinstance(what, dict):
                    _write(os.path.join(d, fn), dict(what, ticker=name) if fn == "prices.json" else what)
                elif what == "ok":
                    _write(os.path.join(d, fn), good)
                elif what == "bad":
                    _write(os.path.join(d, fn), "{not json")
                elif what == "foreign":
                    _write(os.path.join(d, fn), prices)  # ticker APP in another folder
            if fund is not None:
                _write(os.path.join(d, "fundamentals.json"), fund)
            if stale_live:
                _write(os.path.join(d, "live.json"), "{}")
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
        # [Codex review r11 of PR #47] an unreadable score.json cannot vouch for this run: no live figures
        folder("BADS", score="bad"); expect_skip("BADS", "score.json unreadable")
        d = folder("GOOD")
        live = R.reprice_folder("GOOD")
        assert "score_note" not in live and live["scored"]["tier_final"] == s["tier_final"]
        assert json.load(open(os.path.join(d, "live.json"), encoding="utf-8"))["price"] == prices["stats"]["last"]
        assert live["basis_check"]["status"] == "ok" and live["basis_check"]["filed_splits_after_scoring"] is None
        # a 2:1 split since scoring: written, restated, the SEC record carried as evidence
        fund = {"dividends": {"split_adjustments": [{"effective": "2026-10-19", "ratio": 2, "source": "ratio_fact"},
                                                     {"effective": "2021-01-04", "ratio": 3, "source": "ratio_fact"}]}}
        d = folder("SPLIT", prices_=_split_prices(2), fund=fund)
        live = R.reprice_folder("SPLIT")
        on_disk = json.load(open(os.path.join(d, "live.json"), encoding="utf-8"))
        assert on_disk["split_factor"] == 2.0 and on_disk["basis_check"]["split"] == "2:1"
        assert on_disk["irr_weighted"] == n["implied_irr_weighted"] and on_disk["tier"] == "B"
        assert live["basis_check"]["filed_splits_after_scoring"] == [{"effective": "2026-10-19", "ratio": 2.0}]
        # an unreadable fundamentals.json is evidence lost, never a failed name
        folder("SPLITNOFUND", prices_=_split_prices(2), fund="{not json")
        assert R.reprice_folder("SPLITNOFUND")["basis_check"]["filed_splits_after_scoring"] is None
        # an unexplained basis gap: refused, the stale live.json removed
        mismatch = _prices(daily=[[dt, round(c / 1.37, 2)] for dt, c in APP_DAILY])
        folder("MISMATCH", prices_=mismatch); expect_skip("MISMATCH", "per-share basis mismatch")
        # a score.json from an earlier run of the day: [Codex review r11 of PR #47] no live figures, the reason given
        folder("OLDSCORE", score=dict(s, tier_final="C", implied_irr=0.2125, tier_override_reason="stale"))
        expect_skip("OLDSCORE", "score.json is not from this engine run (implied_irr 0.2125")
        # no score.json yet (the engine has run, make_score not): repriced, tier_final unknown
        d = folder("NOSCORE", score="missing")
        live = R.reprice_folder("NOSCORE")
        assert os.path.isfile(os.path.join(d, "live.json")) and live["score_json_fresh"] is None
        assert live["scored"]["tier_final"] is None and live["override_active"] is False
        # --all never lets one bad folder stop the sweep and reports every reason
        names = R.company_folders()
        assert set(names) == {"BADN", "BADP", "BADS", "FOREIGN", "GOOD", "NOP", "SPLIT", "SPLITNOFUND", "MISMATCH", "OLDSCORE",
                              "NOSCORE"}
        buf, old_argv = io.StringIO(), sys.argv
        try:
            sys.argv = ["reprice.py", "--all", "--quiet"]
            with contextlib.redirect_stdout(buf):
                try:
                    R.main()
                except SystemExit as e:
                    assert e.code == 0
        finally:
            sys.argv = old_argv
        out = buf.getvalue()
        assert "4 live.json written, 7 skipped" in out, out
        assert "split since scoring, per-share values restated: SPLIT 2:1, SPLITNOFUND 2:1" in out, out
        assert "skipped OLDSCORE: score.json is not from this engine run" in out, out
        assert "skipped MISMATCH: per-share basis mismatch" in out, out
    finally:
        R.BASE = old_base
        shutil.rmtree(tmp, ignore_errors=True)


def test_split_since_scoring_is_divided_out():
    """Codex finding 4289642852: the reviewer's synthetic APP 2:1 split
    ($272.28 scored -> $136.14 last close, no real move)."""
    n, s = _app()
    # the bug: the unsplit paths at the split price read 28.7236% / S
    raw = R.reprice(n, 136.14, "2026-10-20", s, today="2026-10-20")
    assert round(raw["irr_weighted"] * 100, 4) == 28.7236 and raw["tier"] == "S"
    p = _split_prices(2)
    px, pd = R.live_price(p, "APP", n["as_of"])
    assert (px, pd) == (136.14, "2026-10-20")
    live = R.reprice(n, px, pd, s, today="2026-10-20", prices=p)
    assert live["irr_weighted"] == n["implied_irr_weighted"]  # bit-for-bit: halving a float is exact
    assert round(live["irr_weighted"] * 100, 4) == 18.4268 and live["tier"] == live["tier_by_numbers"] == "B"
    for k in LABELS:
        assert close(live["scenarios"][k]["irr"], n["scenarios"][k]["irr"]), k
    b = live["basis_check"]
    assert live["split_factor"] == 2.0 and b["status"] == "split_adjusted" and b["split"] == "2:1" and b["factor"] == 2.0
    assert b["scored_price_raw"] == 272.28 and b["scored_price_adjusted"] == 136.14 and b["scored_date"] == "2026-10-14"
    assert b["ref_close"] == 136.14 and b["ref_close_date"] == "2026-10-13" and b["observed_ratio"] == 2.0
    assert b["log_residual"] == 0.0 and b["filed_splits_after_scoring"] is None
    # per-share values restated in today's units; unit-free ones unchanged
    unsplit = R.reprice(n, n["price"], None, s, today="2026-10-20")
    for k in ("iv_at_15", "iv_at_12", "iv_at_20", "iv_at_25"):
        assert close(live[k], unsplit[k] / 2), k
    assert live["scored_price"] == 136.14 and close(live["price_change_pct"], 0.0)
    assert close(live["upside_at_15"], n["upside_at_15"]) and close(live["market_cap_est"], n["market_cap_est"])
    assert close(live["delta"]["irr_pp"], 0.0) and not live["delta"]["tier_changed"] and not live["delta"]["tier_changed_vs_final"]
    assert "SPLIT 2:1 since scoring" in R.one_line(live)
    # a real move after the split is priced exactly like the same move on the scored basis
    moved = R.reprice(n, 120.0, "2026-10-20", s, today="2026-10-20", prices=_split_prices(2, last=120.0))
    same = R.reprice(n, 240.0, None, s, today="2026-10-20")
    assert close(moved["irr_weighted"], same["irr_weighted"], 1e-12) and moved["tier"] == same["tier"]
    assert close(moved["price_change_pct"], same["price_change_pct"]) and close(moved["upside_at_15"], same["upside_at_15"])
    # other clean ratios, forward and reverse: the split close prices like the scored-basis close
    for k, label in ((3.0, "3:1"), (1.5, "3:2"), (10.0, "10:1"), (50.0, "50:1"), (0.5, "1:2"), (0.1, "1:10")):
        p = _split_prices(k)
        px, pd = R.live_price(p, "APP", n["as_of"])
        live = R.reprice(n, px, pd, s, today="2026-10-20", prices=p)
        assert live["basis_check"]["split"] == label and live["split_factor"] == k, (label, live["basis_check"])
        same = R.reprice(n, px * k, None, s, today="2026-10-20")
        assert close(live["irr_weighted"], same["irr_weighted"], 1e-9) and live["tier"] == "B", label
        assert close(live["irr_weighted"], n["implied_irr_weighted"], 1e-3), label  # the split close, rounded to cents
    # a split with a quote a few % off the close (HIG-sized intraday gap) is still that split
    p = _ref(round(272.28 / 2.08, 2))
    assert R.check_basis(n, p)["split"] == "2:1"


def test_basis_ordinary_unexplained_and_unverifiable():
    n, s = _app()

    def skip(prices, why, numbers=None):
        try:
            R.check_basis(numbers or n, prices)
            raise AssertionError(f"expected Skip: {why}")
        except R.Skip as e:
            assert why in str(e), f"{why!r} not in {e}"

    # ordinary quote differences (HIG's intraday quote was 4.3% off on 2026-10-14) change nothing
    for r in (1.0, 1.043, 1 / 1.043, 1.10, 1 / 1.10):
        b = R.check_basis(n, _ref(round(272.28 / r, 2)))
        assert b["status"] == "ok" and b["factor"] == 1.0 and b["split"] is None and b["method"] == "ratio", r
    # beyond ordinary and no clean split -> refused: no repriced IRR in mixed units
    for r in (1.12, 1 / 1.12, 1.37, 1.7, 2.3, 0.6, 2.12):
        skip(_ref(round(272.28 / r, 2)), "per-share basis mismatch")
    try:
        R.reprice(n, 198.0, "2026-10-14", s, today="2026-10-14",
                  prices=_ref(round(272.28 / 1.37, 2)))
        raise AssertionError("expected Skip")
    except R.Skip as e:
        assert "ratio 1.3700" in str(e) and "re-score" in str(e), e
    # only closes on / before the scored date are the reference; later ones (the repriced close) are not
    b = R.check_basis(n, _prices(daily=[["2026-10-13", 272.28], ["2026-10-14", 262.19], ["2026-10-20", 200.0]]))
    assert b["status"] == "ok" and b["ref_close_date"] == "2026-10-13"
    # unverifiable: no close within a week of the scored date, no series, no scored date
    skip(_prices(daily=[["2026-10-01", 290.0]]), "no close within 7 days")
    skip(_prices(daily=[]), "no close within 7 days")
    skip({"stats": {}}, "no close within 7 days")
    skip("nope", "not an object")
    skip(_prices(), "no price or as_of", numbers={k: v for k, v in n.items() if k != "as_of"})
    # a run older than daily_1y: the weekly closes either side of the scored date
    b = R.check_basis(n, _prices(daily=[], weekly=[["2026-10-09", 138.52], ["2026-10-16", 131.1]]))
    assert b["split"] == "2:1" and b["ref_close_date"] == "2026-10-09"
    assert R.check_basis(n, _prices(daily=[], weekly=[["2026-10-09", 277.04]]))["status"] == "ok"


def test_split_windows_are_disjoint():
    """At most one clean ratio can explain a quote, and none overlaps the
    ordinary band — so no split is ever chosen by list order."""
    logs = sorted(math.log(k) for k, _ in R.SPLIT_RATIOS)
    assert all(b - a > 2 * R.SPLIT_LOG_TOL for a, b in zip(logs, logs[1:]))
    assert min(abs(x) for x in logs) - R.SPLIT_LOG_TOL > R.ORDINARY_LOG_TOL
    # the guard behind it: were overlapping ratios ever added, a fit to two is refused, never guessed
    n, _ = _app()
    old = R.SPLIT_RATIOS
    try:
        R.SPLIT_RATIOS = old + ((4 / 3, "4:3"), (5 / 4, "5:4"))
        R.check_basis(n, _ref(round(272.28 / 1.29, 2)))
        raise AssertionError("expected Skip: ambiguous")
    except R.Skip as e:
        assert "ambiguous" in str(e) and "4:3, 5:4" in str(e), e
    finally:
        R.SPLIT_RATIOS = old


def _app_rerun(price):
    """APP's recorded run re-solved at another price, as the engine writes it."""
    n, _ = _app()
    paths, _ = E.replay_paths(n)
    g = n["inputs"]["g_terminal"]
    m = copy.deepcopy(n)
    m["price"] = price
    for k in LABELS:
        m["scenarios"][k]["irr"] = E.solve_irr(paths[k], price, g)[0]
    m["implied_irr_weighted"] = E.solve_irr(paths["weighted"], price, g)[0]
    m["implied_irr_base"] = m["scenarios"]["base"]["irr"]
    m["tier_by_numbers"] = E.tier_for_irr(m["implied_irr_weighted"])
    m["market_cap_est"] = price * n["shares_diluted_latest"]
    m["upside_at_15"] = n["iv_at_15"] / price - 1
    return m


def test_score_from_another_run_is_not_an_override():
    """Codex finding 4289642862: APP's original B/B score left in place
    after a same-day rerun at $217.824 (21.2495% / A). [Codex review r11 of
    PR #47, the main agent's general rule] Such a score is not this run's
    verdict, so no live figures are written at all (Skip): before, live.json
    carried the rerun's figures with score_json_fresh false."""
    n, s = _app()
    m = _app_rerun(217.824)
    assert round(m["implied_irr_weighted"] * 100, 4) == 21.2495 and m["tier_by_numbers"] == "A"
    assert m["as_of"] == s["analysis_date"] and (s["tier_by_numbers"], s["tier_final"]) == ("B", "B")

    def skipped(numbers, scored, *needles):
        try:
            R.reprice(numbers, numbers["price"], None, scored, today="2026-10-14")
        except R.Skip as e:
            msg = str(e)
            assert "score.json is not from this engine run" in msg and "make_score" in msg, msg
            assert all(x in msg for x in needles), (needles, msg)
            return msg
        raise AssertionError("repriced against a score.json from another run")

    skipped(m, s, "tier_by_numbers 'B' vs run 'A'", "implied_irr 0.1843", "price 272.28 vs run 217.824")
    # a score built from the rerun, with a deliberate override, keeps it
    fresh = dict(s, price=217.824, implied_irr=round(m["implied_irr_weighted"], 4), tier_by_numbers="A",
                 tier_final="B", tier_override_reason="test: size it like a B")
    live = R.reprice(m, 217.824, None, fresh, today="2026-10-14")
    assert live["score_json_fresh"] is True and live["score_mismatch"] is None and "score_note" not in live
    assert live["tier"] == "B" and live["tier_by_numbers"] == "A" and live["override_active"] and not live["override_superseded"]
    # each identity field on its own: the matching score keeps its override, any one field off writes nothing
    over = dict(s, tier_final="C", tier_override_reason="test")
    assert R.reprice(n, n["price"], None, over, today="2026-10-14")["tier"] == "C"
    for key, val in (("analysis_date", "2026-10-13"), ("analysis_date", None), ("tier_by_numbers", "C"),
                     ("implied_irr", 0.1849), ("implied_irr", None), ("price", 272.29), ("base_oe_per_share", 12.5644),
                     ("iv_at_15", 376.13), ("engine_version", 4), ("engine_release", "5.4.0"), ("ticker", "ZS")):
        skipped(n, dict(over, **{key: val}), key)
    # no score.json (scored=None): repriced, tier_final unknown
    live = R.reprice(n, n["price"], None, None, today="2026-10-14")
    assert live["score_json_fresh"] is None and live["scored"]["tier_final"] is None and not live["override_active"]
    # make_score's own rounding (implied_irr 4 dp, iv_at_15 2 dp) is not a mismatch
    assert R.score_matches_run(dict(s, implied_irr=round(n["implied_irr_weighted"], 4), iv_at_15=round(n["iv_at_15"], 2)), n) == (True, [])
    # a run record whose tier is not the tier of its own weighted IRR cannot vouch for any score
    bad = dict(n, tier_by_numbers="A")
    ok, mm = R.score_matches_run(dict(s, tier_by_numbers="A"), bad)
    assert not ok and any("is not the tier of its weighted IRR" in x for x in mm), mm


def _lag_prices(fetched_at="2026-10-14T19:30:00-04:00"):
    """prices.json pulled the evening of the scored day (2026-10-14) while
    Nasdaq has not posted that session's row yet: the series ends 10-13."""
    return _prices(daily=APP_DAILY[:2], fetched_at=fetched_at)


def test_scored_session_close_not_posted_yet():
    """Codex finding 4289642852, second round: Nasdaq posts a session's
    daily row hours after the close, so on scoring night the series stops at
    the session before the scored one. The scored quote's gap to that close
    is the day's move, never a split: -32% used to read as a 2:3 reverse
    split (IV@15 $564.19 instead of $376.12), +48% as 3:2, and -15% was
    refused with "re-score the run"."""
    n, _ = _app()
    for q in (185.15, 402.97, 231.44, 272.28 / 1.4998):
        m = _app_rerun(q)
        p = _lag_prices()
        px, pd = R.live_price(p, "APP", m["as_of"])
        assert (px, pd) == (272.28, "2026-10-13")
        live = R.reprice(m, px, pd, None, today="2026-10-14", prices=p)
        b = live["basis_check"]
        assert live["split_factor"] == 1.0 and b["status"] == "ok" and b["split"] is None, (q, b)
        assert b["method"] == "no_close_since_scoring" and b["ref_close_date"] == "2026-10-13" and close(b["observed_ratio"], q / 272.28)
        # the scored paths at the 10-13 close: APP's own scored figures, consistent units
        assert close(live["irr_weighted"], n["implied_irr_weighted"], 1e-12) and live["tier"] == "B", (q, live["irr_weighted"])
        assert close(live["iv_at_15"], n["iv_at_15"]) and close(live["scored_price"], q)
        assert "SPLIT" not in R.one_line(live) and "scored session close not posted yet" in R.one_line(live)
    # the next morning the 10-14 row is there and the ratio test runs on it:
    # a real -33% day is an ordinary quote (it closed there), not a split
    m = _app_rerun(181.54)
    p = _prices(daily=[["2026-10-12", 270.87], ["2026-10-13", 272.28], ["2026-10-14", 181.54]])
    live = R.reprice(m, 181.54, "2026-10-14", None, today="2026-10-15", prices=p)
    assert live["basis_check"]["method"] == "ratio" and live["basis_check"]["status"] == "ok" and live["split_factor"] == 1.0
    assert "not posted yet" not in R.one_line(live)
    assert close(live["irr_weighted"], m["implied_irr_weighted"], 1e-12) and live["basis_check"]["ref_close_date"] == "2026-10-14"
    # a series that stops more than a week before the scored date is a stale pull, not that lag: refused
    try:
        R.check_basis(n, _prices(daily=[["2026-10-06", 280.0]]))
        raise AssertionError("expected Skip")
    except R.Skip as e:
        assert "no close within 7 days" in str(e), e
    # a weekend run: scored Saturday at Friday's close, no session since -> factor 1;
    # Monday's row arrives with the history halved (a 2:1 split that Monday) -> divided out
    sat = dict(n, as_of="2026-10-17")
    b = R.check_basis(sat, _prices(daily=[["2026-10-15", 270.0], ["2026-10-16", 272.28]]))
    assert b["status"] == "ok" and b["method"] == "no_close_since_scoring", b
    b = R.check_basis(sat, _prices(daily=[["2026-10-15", 135.0], ["2026-10-16", 136.14], ["2026-10-19", 136.14]]))
    assert b["status"] == "split_adjusted" and b["split"] == "2:1" and b["ref_close_date"] == "2026-10-16", b
    # file level: the -15% scoring-day quote is written (it used to be refused and live.json deleted)
    tmp = tempfile.mkdtemp(prefix="reprice_test_")
    old_base = R.BASE
    try:
        R.BASE = tmp
        d = os.path.join(tmp, "APP"); os.makedirs(d)
        _write(os.path.join(d, "dcf_numbers.json"), _app_rerun(231.44))
        _write(os.path.join(d, "prices.json"), _lag_prices())
        live = R.reprice_folder("APP")
        assert os.path.isfile(os.path.join(d, "live.json")) and live["basis_check"]["method"] == "no_close_since_scoring"
    finally:
        R.BASE = old_base
        shutil.rmtree(tmp, ignore_errors=True)


def test_unadjusted_split_step_is_held():
    """Codex finding 4289642852, second round: were Nasdaq to post a
    post-split close before adjusting the history, the reference close
    would still read in the scored units (ratio 1) and the reviewer's 2:1
    example would read 28.7236% / S again. A one-session move after the
    scored date with a split's exact size is held while it is fresh."""
    n, s = _app()
    unadjusted = [["2026-10-12", 270.87], ["2026-10-13", 272.28], ["2026-10-14", 262.19], ["2026-10-19", 136.14]]
    p = _prices(daily=unadjusted, fetched_at="2026-10-19T19:30:00-04:00")
    raw = R.reprice(n, 136.14, "2026-10-19", s, today="2026-10-19")
    assert round(raw["irr_weighted"] * 100, 4) == 28.7236 and raw["tier"] == "S"  # what the unchecked basis publishes
    try:
        R.reprice(n, 136.14, "2026-10-19", s, today="2026-10-19", prices=p)
        raise AssertionError("expected Skip: held")
    except R.Skip as e:
        assert str(e).startswith("held:") and "2:1 split" in str(e) and "2026-10-14 -> 2026-10-19" in str(e), e
        assert "-48.1%" in str(e), e
    moves = R.split_like_moves(p, R._date("2026-10-14"))
    assert [(m["to_date"], m["split"]) for m in moves] == [("2026-10-19", "2:1")]
    # once Nasdaq adjusts the history the step is gone and the split is divided out
    live = R.reprice(n, 136.14, "2026-10-20", s, today="2026-10-20", prices=_split_prices(2))
    assert live["basis_check"]["split"] == "2:1" and round(live["irr_weighted"] * 100, 4) == 18.4268 and live["tier"] == "B"
    # a real -33% day after scoring (SMCI 2026-03-20 was 1.4998): held while it is among the
    # newest HOLD_SESSIONS closes, repriced once it has stood that long
    crash = [["2026-10-13", 272.28], ["2026-10-14", 262.19], ["2026-10-15", 174.82]]
    later = [["2026-10-16", 176.0], ["2026-10-19", 177.5], ["2026-10-20", 178.0]]
    assert R.HOLD_SESSIONS == 3
    for extra in range(R.HOLD_SESSIONS):
        try:
            R.check_basis(n, _prices(daily=crash + later[:extra]))
            raise AssertionError(f"expected Skip: held ({extra} sessions since the move)")
        except R.Skip as e:
            assert str(e).startswith("held:") and "3:2 split" in str(e) and "-33.3%" in str(e), e
    p = _prices(daily=crash + later)
    px, pd = R.live_price(p, "APP", n["as_of"])
    live = R.reprice(n, px, pd, s, today="2026-10-20", prices=p)
    assert live["split_factor"] == 1.0 and live["basis_check"]["status"] == "ok" and px == 178.0
    assert close(live["irr_weighted"], R.reprice(n, 178.0, None, s, today="2026-10-20")["irr_weighted"], 1e-12)
    # an up-move of a reverse split's size (DFTX 2026-06-22 was 1/1.498) is held the same way
    try:
        R.check_basis(n, _prices(daily=[["2026-10-13", 272.28], ["2026-10-14", 262.19], ["2026-10-15", 393.0]]))
        raise AssertionError("expected Skip: held")
    except R.Skip as e:
        assert "2:3 split" in str(e), e
    # a move INTO the scored session is already in the scored quote: never held
    m = _app_rerun(181.54)
    p = _prices(daily=[["2026-10-12", 270.87], ["2026-10-13", 272.28], ["2026-10-14", 181.54]])
    assert R.split_like_moves(p, R._date("2026-10-14")) == [] and R.check_basis(m, p)["status"] == "ok"
    # ordinary moves after scoring are never held
    assert R.split_like_moves(_prices(), R._date("2026-10-12")) == []
    # file level: held -> no live.json (a stale one is removed), the reason in the --all summary
    tmp = tempfile.mkdtemp(prefix="reprice_test_")
    old_base, old_argv = R.BASE, sys.argv
    try:
        R.BASE = tmp
        d = os.path.join(tmp, "HELD"); os.makedirs(d)
        _write(os.path.join(d, "dcf_numbers.json"), n)
        _write(os.path.join(d, "prices.json"), _prices(ticker="HELD", daily=unadjusted, fetched_at="2026-10-19T19:30:00-04:00"))
        _write(os.path.join(d, "live.json"), "{}")
        buf = io.StringIO()
        sys.argv = ["reprice.py", "--all", "--quiet"]
        with contextlib.redirect_stdout(buf):
            try:
                R.main()
            except SystemExit as e:
                assert e.code == 0
        out = buf.getvalue()
        assert "0 live.json written, 1 skipped" in out and "skipped HELD: held: the 2026-10-14 -> 2026-10-19 close" in out, out
        assert not os.path.exists(os.path.join(d, "live.json"))
    finally:
        R.BASE, sys.argv = old_base, old_argv
        shutil.rmtree(tmp, ignore_errors=True)



def test_big_scoring_day_move_is_never_read_as_a_split():
    """Codex finding 4289642852, verifier round: once the scored session's
    row is posted, a quote that is split-sized against the PRIOR close but
    more than ~10% from the scored close used to fit 2:3 through the min()
    over both reference closes. On a session that itself moved more than
    ORDINARY_LOG_TOL the quote is tied to neither close: between them it is
    that day's trading (factor 1), a split-sized gap is refused."""
    n, _ = _app()
    def basis(q, daily):
        return R.check_basis(dict(n, price=q, as_of="2026-10-14"), _prices(daily=daily))
    # -33% open recovering to -20%: 67 vs 100 fits 2:3, 67 vs 80 is 17.7% off -> refused, never "2:3"
    try:
        basis(67.0, [["2026-10-13", 100.0], ["2026-10-14", 80.0]])
        raise AssertionError("expected Skip")
    except R.Skip as e:
        assert "ambiguous" in str(e) and "2:3" in str(e) and "-20.0%" in str(e), e
    # an earnings swing: quoted at 85 between the 100 and 75 closes -> ordinary, factor 1
    b = basis(85.0, [["2026-10-13", 100.0], ["2026-10-14", 75.0]])
    assert b["status"] == "ok" and b["factor"] == 1.0 and b["method"] == "within_scored_day_range", b
    # a pre-market quote at the prior close before a -33% session stays ordinary (not 3:2 against the scored close)
    b = basis(100.0, [["2026-10-13", 100.0], ["2026-10-14", 66.7]])
    assert b["status"] == "ok" and b["factor"] == 1.0 and b["ref_close_date"] == "2026-10-13", b
    # far outside both closes on a big day, no split fit -> refused
    try:
        basis(130.0, [["2026-10-13", 100.0], ["2026-10-14", 80.0]])
        raise AssertionError("expected Skip")
    except R.Skip as e:
        assert "mismatch" in str(e) and "outside" in str(e), e
    # an ordinary session still divides a real split out (the reviewer's 2:1)
    b = basis(272.28, [["2026-10-13", 136.14], ["2026-10-14", 136.0], ["2026-10-19", 137.0]])
    assert b["status"] == "split_adjusted" and b["split"] == "2:1" and b["factor"] == 2.0, b

def test_live_market_cap_divides_by_the_ads_ratio():
    """Engine 5.5, decision 1: the price is per ADS, shares_diluted_latest per
    ordinary share, so the live cap is price × shares ÷ ratio (TLK's live cap
    read $1.09T beside its $10.93B score); everything else is unchanged."""
    n, s = _app()
    shares = n["shares_diluted_latest"]
    plain = R.reprice(n, 262.19, "2026-10-14", s, today="2026-10-14")
    # non-ADS: bit-identical to the 5.4 formula, at the scored and a moved price
    assert plain["market_cap_est"] == 262.19 * shares * 1.0
    at_scored = R.reprice(n, n["price"], None, s, today="2026-10-14")
    assert at_scored["market_cap_est"] == n["price"] * shares and at_scored["market_cap_est"] == n["market_cap_est"]
    for ratio in (100, 2.0, 0.5):
        m = copy.deepcopy(n)
        m["ads_ratio"] = {"ratio": ratio, "source": "synthetic 20-F cover page", "reason": "test"}
        live = R.reprice(m, 262.19, "2026-10-14", s, today="2026-10-14")
        assert live["market_cap_est"] == (262.19 * shares) / ratio, (ratio, live["market_cap_est"])
        assert live["in_scope_under_40b"] is (live["market_cap_est"] < 40e9), ratio
        # the ratio touches the cap only: IRRs, tiers and IVs are the plain run's
        for k in ("irr_weighted", "tier", "iv_at_15", "iv_at_25", "upside_at_15", "scenarios"):
            assert live[k] == plain[k], (ratio, k)
        assert R.live_market_cap(m, 10.0) == (10.0 * shares) / ratio
    m = copy.deepcopy(n)
    m["ads_ratio"] = {"ratio": 100, "source": "s", "reason": "r"}
    assert R.reprice(m, 262.19, None, s, today="2026-10-14")["in_scope_under_40b"] is True  # $0.88B, not $88B
    assert plain["in_scope_under_40b"] is False
    # a split since scoring multiplies after the division (2:1: half the price, twice the shares)
    p = _split_prices(2)
    px, pd = R.live_price(p, "APP", n["as_of"])
    m = copy.deepcopy(n)
    m["ads_ratio"] = {"ratio": 2.0, "source": "s", "reason": "r"}
    split = R.reprice(m, px, pd, s, today="2026-10-20", prices=p)
    assert split["split_factor"] == 2.0 and split["market_cap_est"] == (px * shares) / 2.0 * 2.0
    assert close(split["market_cap_est"], n["market_cap_est"] / 2.0)
    # an ads_ratio that does not apply (null / zero / not a number) is no ratio
    for bad in (None, {"ratio": None}, {"ratio": 0}, {"ratio": "2"}, "2"):
        m = dict(n, ads_ratio=bad)
        assert R.live_market_cap(m, 262.19) == 262.19 * shares, bad
    # a 5.5 run records the count its market cap used: a scale-corrected count wins over the mis-scaled diluted one
    m = dict(n, shares_diluted_latest=shares / 1000,
             market_cap_basis={"shares_used": shares, "shares_source": "diluted_latest_scale_corrected",
                               "ads_ratio": None, "formula": "price × shares"})
    assert R.live_market_cap(m, 262.19) == 262.19 * shares
    m["market_cap_basis"] = {"shares_used": None, "shares_source": "diluted_latest"}
    assert R.live_market_cap(m, 262.19) == 262.19 * (shares / 1000)
    # the engine's helper is the one formula (dcf_engine 5.5): reprice uses it, never a local copy
    assert R._market_cap_estimate is E.market_cap_est
    assert E.market_cap_est(262.19, shares, 2.0) == R._market_cap_estimate(262.19, shares, 2.0)
    assert E.market_cap_est(262.19, shares, None) == 262.19 * shares


def test_live_market_cap_share_count_rule_m6():
    """FIX_DECISIONS_R1 M6 (round-1 verification; a wording fix): without an ADS ratio the live cap is bit-identical
    to close × shares_diluted_latest only for a run whose market_cap_basis.shares_source is diluted_latest, or with
    no basis record; any other shares_source prices on market_cap_basis.shares_used (an HBAN-shaped dei_latest run).
    The module docstring says so — it claimed every run without an ADS ratio was unchanged bit for bit."""
    n = {"shares_diluted_latest": 1504836000}
    assert R.live_market_cap(n, 15.0) == 15.0 * 1504836000
    n["market_cap_basis"] = {"shares_used": 1504836000, "shares_source": "diluted_latest", "ads_ratio": None,
                             "formula": "price × shares"}
    assert R.live_market_cap(n, 15.0) == 15.0 * 1504836000
    n["market_cap_basis"] = {"shares_used": 2027130587, "shares_source": "dei_latest", "ads_ratio": None,
                             "formula": "price × shares"}
    assert R.live_market_cap(n, 15.0) == 15.0 * 2027130587 == 30406958805.0
    doc = " ".join(R.__doc__.split())
    assert "A run without an ADS ratio is unchanged bit for bit." not in doc
    assert ("for a run whose market_cap_basis.shares_source is diluted_latest, or with no basis record; otherwise the "
            "count is market_cap_basis.shares_used") in doc, doc[-900:]
    assert "a non-ADS run is bit-identical)" not in " ".join(R.live_market_cap.__doc__.split())


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
            except Exception as e:  # an unexpected Skip / error fails the test, never the runner
                fails += 1; print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
