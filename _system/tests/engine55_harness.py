#!/usr/bin/env python3
"""Offline harness for driving dcf_engine.main() / ttm.main() against the gzip fixtures in
fixtures/engine55/ (built by fixtures/engine55/build_fixtures.py — the only piece that touches the network).

    from engine55_harness import run_engine, load_fixture
    out = run_engine("AR", args=["--moat", "5"])            # -> dict: dcf_numbers payload + csv rows + exit code
    out["numbers"]["base_oe_per_share"], out["rows"][-1]["capex_tag"], out["exit"]

What it does: builds a throwaway STOCKS_BASE (universe.csv with the fixture's row, a two-entry
sec_tickers_exchange.json, the ticker folder with the judgment.json / ttm.json you pass or the repo's own
copies), monkeypatches every network call the engine makes (get_json for companyfacts, nasdaq_price, fx_rate,
filer_annual_form, the --measure subprocess replay _override_impact) and runs main() in-process with sys.argv
set. Nothing is written outside the temp base. Importing this module never imports the engine with a live
sys.argv (dcf_engine reads MEASURE from sys.argv at import), so MEASURE is forced per run.
"""
import csv, gzip, importlib, importlib.util, io, json, os, shutil, sys, tempfile, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
ROOT = os.path.dirname(SYS)
FIXTURES = os.path.join(HERE, "fixtures", "engine55")


def load_fixture(ticker):
    with gzip.open(os.path.join(FIXTURES, f"{ticker}.json.gz"), "rt", encoding="utf-8") as f:
        return json.load(f)


_PRIVATE = 0


def _engine():
    """A private, freshly executed copy of dcf_engine for one harness run (neutral argv, MEASURE False).

    It is never registered as sys.modules["dcf_engine"] and never reloads that module: make_score and reprice
    keep references to the shared module's functions (market_cap_estimate = dcf_engine.market_cap_est), and a
    reload replaced them under the other test modules when the whole suite ran in one process (Codex, PR #31:
    test_release_helpers and test_live_market_cap_divides_by_the_ads_ratio failed under pytest). Each run's
    monkeypatches (network stand-ins, _patch_55_off) land on this copy only, so no reset is needed."""
    global _PRIVATE
    saved = sys.argv
    sys.argv = ["dcf_engine.py"]
    try:
        if SYS not in sys.path:
            sys.path.insert(0, SYS)
        _PRIVATE += 1
        spec = importlib.util.spec_from_file_location(f"_dcf_engine_harness_{_PRIVATE}", os.path.join(SYS, "dcf_engine.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.argv = saved


def _shared_engine():
    """The shared sys.modules["dcf_engine"], imported once with a neutral argv (MEASURE False) and the caller's
    environment — never with a harness temp base as STOCKS_BASE. Not used for engine runs (those get _engine())."""
    if "dcf_engine" in sys.modules:
        return sys.modules["dcf_engine"]
    saved = sys.argv
    sys.argv = ["dcf_engine.py"]
    try:
        if SYS not in sys.path:
            sys.path.insert(0, SYS)
        return importlib.import_module("dcf_engine")
    finally:
        sys.argv = saved


def make_base(fixture, judgment=None, ttm=None, copy_repo_files=True):
    """A temp STOCKS_BASE for the fixture's ticker. judgment / ttm: dicts written as judgment.json / ttm.json;
    when None and copy_repo_files, the repo folder's own files are copied (so acceptance runs use the worker's
    saved judgment). Returns the base path."""
    t = fixture["ticker"]
    base = tempfile.mkdtemp(prefix=f"e55_{t}_")
    os.makedirs(f"{base}/_system", exist_ok=True)
    os.makedirs(f"{base}/{t}", exist_ok=True)
    row = fixture.get("universe_row") or {"ticker": t, "name": fixture.get("entityName") or t, "sector": "", "price": "", "market_cap": "", "cik": str(fixture["cik"])}
    with open(f"{base}/_system/universe.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        w.writeheader()
        w.writerow(row)
    with open(f"{base}/_system/sec_tickers_exchange.json", "w", encoding="utf-8") as f:
        json.dump({"fields": ["cik", "name", "ticker", "exchange"],
                   "data": [[fixture["cik"], fixture.get("entityName") or t, t, "NYSE"]]}, f)
    if judgment is not None:
        json.dump(judgment, open(f"{base}/{t}/judgment.json", "w", encoding="utf-8"), indent=1)
    elif copy_repo_files and os.path.exists(f"{ROOT}/{t}/judgment.json"):
        shutil.copy(f"{ROOT}/{t}/judgment.json", f"{base}/{t}/judgment.json")
    if ttm is not None:
        json.dump(ttm, open(f"{base}/{t}/ttm.json", "w", encoding="utf-8"), indent=1)
    elif copy_repo_files and os.path.exists(f"{ROOT}/{t}/ttm.json"):
        shutil.copy(f"{ROOT}/{t}/ttm.json", f"{base}/{t}/ttm.json")
    return base


def run_engine(ticker, args=(), judgment=None, ttm=None, base=None, price=None, measure=False,
               fixture=None, patch=None, keep_base=False, env=None):
    """Run dcf_engine.main() offline. Returns {"exit": int|None, "numbers": dict|None, "rows": [csv rows]|None,
    "stdout": str, "base": path}. `args` are the extra CLI args (--moat, --probs, --ttm, --base-oe-ps ...).
    `patch` is an optional callable(engine_module) for extra monkeypatching. `env` extra environment
    (e.g. {"DCF_NO_OVERRIDES": "1"})."""
    fx = fixture or load_fixture(ticker)
    base = base or make_base(fx, judgment, ttm)
    E = _engine()
    E.BASE, E.SYS = base, f"{base}/_system"
    E.MEASURE = bool(measure)
    facts = fx["facts"]
    cik = int(fx["cik"])

    def fake_get_json(url, headers=None, timeout=90):
        if "companyfacts" in url:
            if f"CIK{cik:010d}" in url:
                return json.loads(json.dumps(facts))
            raise RuntimeError(f"offline harness: no fixture for {url}")
        if "company_tickers.json" in url:
            return {}
        if "frankfurter" in url:
            raise RuntimeError("offline harness: fx_rate must be patched, not fetched")
        raise RuntimeError(f"offline harness: unexpected fetch {url}")

    rates = fx.get("fx_rates") or {}

    def fake_fx_rate(ccy, date_str):
        return (rates.get(ccy) or {}).get(date_str)

    E.get_json = fake_get_json
    E.fx_rate = fake_fx_rate
    E.filer_annual_form = lambda _cik: fx.get("filer_annual_form")
    px = fx.get("price") if price is None else price
    E.nasdaq_price = lambda _t: px
    E._override_impact = lambda *a, **k: {"base_oe_per_share_zero_fill": None, "base_oe_per_share_final": None,
                                          "weighted_irr_zero_fill": None, "weighted_irr_final": None,
                                          "basis": "offline harness: impact replay not run"}
    if patch:
        patch(E)
    saved_argv, saved_env = sys.argv, dict(os.environ)
    sys.argv = ["dcf_engine.py", ticker] + list(args) + (["--measure"] if measure else [])
    os.environ["STOCKS_BASE"] = base
    for k, v in (env or {}).items():
        os.environ[k] = v
    out = io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out):
            try:
                E.main()
                code = 0
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
    finally:
        sys.argv = saved_argv
        os.environ.clear()
        os.environ.update(saved_env)
    text = out.getvalue()
    numbers, rows = None, None
    npath = f"{base}/{ticker}/dcf_numbers.json"
    if os.path.exists(npath) and not measure:
        numbers = json.load(open(npath, encoding="utf-8"))
    else:
        i = text.find("{")
        if i >= 0:
            try:
                numbers = json.loads(text[i:])
            except Exception:
                numbers = None
    cpath = f"{base}/{ticker}/financials_history.csv"
    if os.path.exists(cpath):
        rows = list(csv.DictReader(open(cpath, encoding="utf-8")))
    result = {"exit": code, "numbers": numbers, "rows": rows, "stdout": text, "base": base}
    if not keep_base:
        shutil.rmtree(base, ignore_errors=True)
    return result


def run_ttm(ticker, judgment=None, base=None, fixture=None, patch=None, keep_base=False, env=None):
    """Run ttm.main() offline against the fixture. Returns {"exit", "ttm": dict|None, "stdout", "stderr", "base"}."""
    fx = fixture or load_fixture(ticker)
    base = base or make_base(fx, judgment)
    _shared_engine()   # import the shared dcf_engine (ttm.py's helper module) before STOCKS_BASE points at a temp base
    saved_argv, saved_env = sys.argv, dict(os.environ)
    sys.argv = ["ttm.py", ticker]
    os.environ["STOCKS_BASE"] = base
    for k, v in (env or {}).items():
        os.environ[k] = v
    try:
        if SYS not in sys.path:
            sys.path.insert(0, SYS)
        # A private copy of ttm.py per run (never a reload of sys.modules["ttm"]): its BASE / get_json patches stay
        # on this copy. Its `import dcf_engine as _engine` binds the shared engine, whose helpers ttm calls are pure.
        global _PRIVATE
        _PRIVATE += 1
        spec = importlib.util.spec_from_file_location(f"_ttm_harness_{_PRIVATE}", os.path.join(SYS, "ttm.py"))
        T = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(T)
        T.BASE, T.SYS = base, f"{base}/_system"
        facts = fx["facts"]
        T.get_json = lambda url, headers=None, timeout=90: json.loads(json.dumps(facts))
        if patch:
            patch(T)
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                T.main()
                code = 0
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
    finally:
        sys.argv = saved_argv
        os.environ.clear()
        os.environ.update(saved_env)
    text = out.getvalue()
    data = None
    i = text.find("{")
    if i >= 0:
        try:
            data = json.loads(text[i:])
        except Exception:
            data = None
    result = {"exit": code, "ttm": data, "stdout": text, "stderr": err.getvalue(), "base": base}
    if not keep_base:
        shutil.rmtree(base, ignore_errors=True)
    return result


def recorded(ticker):
    """The repo folder's recorded dcf_numbers.json (None when absent)."""
    p = f"{ROOT}/{ticker}/dcf_numbers.json"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def repo_judgment(ticker, drop=(), **updates):
    """A copy of the repo folder's judgment.json ({} when the folder has none) with the keys in `drop`
    removed and `updates` merged on top — for runs such as "APA's judgment minus its capex_override".
    The repo file is never modified."""
    p = f"{ROOT}/{ticker}/judgment.json"
    j = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    j = json.loads(json.dumps(j))
    for k in drop:
        j.pop(k, None)
    j.update(updates)
    return j


def recorded_args(n):
    """CLI args replaying a recorded run's inputs (moat / probs / offsets / mults / gterm and the base pin)."""
    inp = n.get("inputs") or {}
    args = ["--moat", repr(float(inp["moat"])),
            "--probs", ",".join(repr(float(p)) for p in inp["probs"]),
            "--offsets", ",".join(repr(float(o)) for o in inp["offsets"]),
            "--mults", ",".join(repr(float(m)) for m in inp["mults"]),
            "--gterm", repr(float(inp.get("g_terminal", 0.025)))]
    if inp.get("base_pin_source") == "ttm_json":
        args.append("--ttm")
    elif inp.get("base_oe_ps_arg") is not None:
        args += ["--base-oe-ps", repr(float(inp["base_oe_ps_arg"]))]
    return args
