#!/usr/bin/env python3
"""UTF-8 file I/O in dcf_engine.py, ttm.py and forensic_pull.py on a Windows PC.
Run: python _system/tests/test_encoding_utf8.py (or python -m pytest _system/tests).
No network: fixtures go to a temporary folder, SEC fetches are stubbed, and the
two subprocess smoke runs stop at NO_CIK before any fetch.

On Windows a text-mode open() without encoding= decodes with the locale code
page (cp1252), not UTF-8. Most judgment.json files (82 of 90 on 2026-10-15)
carry UTF-8 text (em dashes, minus signs, accented names), and 8 put it in an override's
source / reason (APP, CFG, DFTX, EME, ESLT, MTB, STZ, WRB), which the engine
copies into dcf_numbers.json: run from Andrew's PC those strings came out as
mojibake ("â€”" for "—") and moved content_hash, and a character whose UTF-8
bytes include one cp1252 leaves undefined (0x81 0x8D 0x8F 0x90 0x9D, e.g. "Ł")
raised inside a bare `except Exception`, so the override was silently dropped.

1. Static: every text-mode open() in the three scripts names encoding="utf-8";
   binary opens stay binary.
2. Static: no json.dump / json.dumps there turns ensure_ascii off, so what they
   write is pure ASCII and safe in any code page.
3. Behaviour under a simulated cp1252 default (an `open` placed in the module's
   namespace that decodes with cp1252 when no encoding is given, the way
   Windows does): dcf_engine.load_overrides / load_ads_ratio, ttm.load_overrides
   and forensic_pull.main read judgment.json / score.json / dcf_numbers.json intact.
4. A control proves that simulation bites, so (3) would fail on the old code.
5. dcf_engine.py and ttm.py still start and read universe.csv and
   sec_tickers_exchange.json with every text open naming its encoding.
"""
import ast, builtins, contextlib, io, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
BASE = os.path.dirname(SYS)
sys.path.insert(0, SYS)
import dcf_engine as E  # noqa: E402
import ttm as T  # noqa: E402
import forensic_pull as FP  # noqa: E402

SCRIPTS = ("dcf_engine.py", "ttm.py", "forensic_pull.py")
# text-mode open() calls per script after the fix (reads and writes)
EXPECTED_TEXT_OPENS = {"dcf_engine.py": 10, "ttm.py": 4, "forensic_pull.py": 2}

# "Ł" is C5 81 in UTF-8; 0x81 is undefined in cp1252, so a cp1252 read raises.
DROP = "10-K FY2025 note 7 — Łódź plant capex"
# "—" (E2 80 94) and "−" (E2 88 92) decode in cp1252, as mojibake.
MOJI = "Growth capex — excluded (−$1.2B) per Nestlé guidance"


class Cp1252Default:
    """Stand-in for builtins.open that behaves like Windows: a text-mode open
    without encoding= decodes / encodes with cp1252. Records each such call."""

    def __init__(self):
        self.unencoded = []

    def __call__(self, file, mode="r", buffering=-1, encoding=None, errors=None,
                 newline=None, closefd=True, opener=None):
        if "b" not in mode and encoding is None:
            self.unencoded.append((os.path.basename(str(file)), mode))
            encoding = "cp1252"
        return builtins.open(file, mode, buffering, encoding, errors, newline, closefd, opener)


@contextlib.contextmanager
def windows_open(module, base):
    """Shadow `open` in module's globals with Cp1252Default and point its BASE at base."""
    fake, old_base = Cp1252Default(), module.BASE
    had_open = "open" in vars(module)
    module.open, module.BASE = fake, base
    saved_env = os.environ.pop("DCF_NO_OVERRIDES", None)
    try:
        yield fake
    finally:
        module.BASE = old_base
        if not had_open:
            del module.open
        if saved_env is not None:
            os.environ["DCF_NO_OVERRIDES"] = saved_env


def _write_utf8(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with builtins.open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def _override(text):
    return {"value": 1.5e9, "kind": "filing", "source": text, "reason": text}


def _judgment(text):
    return {"capex_override": _override(text), "sbc_override": _override(text),
            "shares_override": {"value": 250e6, "kind": "estimate", "source": text, "reason": text},
            "ads_ratio": {"ratio": 2.0, "source": text, "reason": text}}


@contextlib.contextmanager
def fixture_base():
    d = tempfile.mkdtemp(prefix="test_encoding_")
    try:
        _write_utf8(f"{d}/TDROP/judgment.json", _judgment(DROP))
        _write_utf8(f"{d}/TMOJI/judgment.json", _judgment(MOJI))
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _open_calls(path):
    """[(lineno, mode, encoding)] for every call to builtin open() in path."""
    with builtins.open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            mode = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else "r"
            enc = None
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = kw.value.value
                if kw.arg == "encoding":
                    enc = kw.value.value if isinstance(kw.value, ast.Constant) else "<expr>"
            out.append((node.lineno, mode, enc))
    return out


# ---------------- 1-2. static ----------------
def test_every_text_open_names_utf8():
    for name in SCRIPTS:
        calls = _open_calls(os.path.join(SYS, name))
        text = [c for c in calls if "b" not in c[1]]
        bad = [c for c in text if c[2] != "utf-8"]
        assert not bad, f"{name}: text-mode open() without encoding='utf-8' at {bad}"
        assert len(text) >= EXPECTED_TEXT_OPENS[name], f"{name}: expected {EXPECTED_TEXT_OPENS[name]} text opens, found {len(text)}"
        for ln, mode, enc in calls:
            if "b" in mode:
                assert enc is None, f"{name}:{ln}: a binary open() takes no encoding"


def test_no_other_text_io_without_encoding():
    """Path.read_text / write_text / .open() and io / codecs opens would bypass
    the open() check above; none may appear without an encoding."""
    for name in SCRIPTS:
        with builtins.open(os.path.join(SYS, name), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("read_text", "write_text", "open")
                    and not (isinstance(node.func.value, ast.Name) and node.func.value.id in ("urllib", "webbrowser"))):
                kws = {k.arg for k in node.keywords}
                assert "encoding" in kws, f"{name}:{node.lineno}: .{node.func.attr}() without encoding"


def test_json_writes_stay_ascii():
    for name in SCRIPTS:
        with builtins.open(os.path.join(SYS, name), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("dump", "dumps")
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "json"):
                for kw in node.keywords:
                    assert kw.arg != "ensure_ascii", f"{name}:{node.lineno}: json.{node.func.attr} must keep ensure_ascii's default"
    # default ensure_ascii: the engine's em-dash note and a non-ASCII override
    # reason serialise to ASCII, so the file is the same bytes in any code page
    s = json.dumps({"note": "v5 never emits a tier on an uncovered data gap — a missing value is not a zero.",
                    "overrides_applied": [{"reason": DROP + MOJI}]}, indent=1)
    assert s.encode("cp1252") == s.encode("ascii") == s.encode("utf-8")
    assert json.loads(s)["overrides_applied"][0]["reason"] == DROP + MOJI


# ---------------- 3-4. behaviour under a cp1252 default ----------------
def test_control_cp1252_default_breaks_utf8_reads():
    """Without encoding=, the simulated Windows open drops one fixture and mangles the other."""
    with fixture_base() as d:
        fake = Cp1252Default()
        try:
            with fake(f"{d}/TDROP/judgment.json") as f:
                json.load(f)
            raise AssertionError("cp1252 read of a 'Ł' fixture should raise UnicodeDecodeError")
        except UnicodeDecodeError:
            pass
        with fake(f"{d}/TMOJI/judgment.json") as f:
            got = json.load(f)["capex_override"]["source"]
        assert got != MOJI and "â€”" in got, got
        assert len(fake.unencoded) == 2


def test_dcf_engine_reads_judgment_as_utf8():
    with fixture_base() as d, windows_open(E, d) as fake:
        for tk, text in (("TDROP", DROP), ("TMOJI", MOJI)):
            ov = E.load_overrides(tk)
            assert set(ov) == {"capex", "sbc", "shares"}, f"{tk}: overrides dropped: {ov}"
            for field in ov:
                assert ov[field]["source"] == text and ov[field]["reason"] == text, f"{tk}/{field}: {ov[field]}"
            ads = E.load_ads_ratio(tk)
            assert ads == {"ratio": 2.0, "source": text, "reason": text}, f"{tk}: {ads}"
        assert not fake.unencoded, fake.unencoded


def test_ttm_reads_judgment_as_utf8():
    with fixture_base() as d, windows_open(T, d) as fake:
        for tk, text in (("TDROP", DROP), ("TMOJI", MOJI)):
            ov = T.load_overrides(tk)
            assert set(ov) == {"capex", "sbc", "shares"}, f"{tk}: overrides dropped: {ov}"
            for field in ov:
                assert ov[field]["source"] == text and ov[field]["reason"] == text, f"{tk}/{field}: {ov[field]}"
        assert not fake.unencoded, fake.unencoded


def test_forensic_pull_reads_score_and_numbers_as_utf8():
    """score.json with UTF-8 prose: under cp1252 it raised inside a bare except,
    so the freshness check ran against analysis_date 0000-00-00."""
    calls = []

    def fake_get_json(url, timeout=90):
        calls.append(url)
        if "companyfacts" in url:
            return {"facts": {}}
        if "submissions" in url:
            return {"filings": {"recent": {"filingDate": ["2026-08-01", "2026-10-01"], "form": ["10-Q", "10-Q"],
                                           "reportDate": ["2026-06-30", "2026-09-30"], "items": ["", ""]}}}
        raise AssertionError(f"unexpected fetch {url}")

    with fixture_base() as d, windows_open(FP, d) as fake:
        _write_utf8(f"{d}/TFOR/dcf_numbers.json", {"cik": 1234567, "latest_period_end": "2026-06-30",
                                                  "note": "engine note — " + MOJI})
        _write_utf8(f"{d}/TFOR/score.json", {"analysis_date": "2026-09-15", "thesis": DROP})
        old_get, old_argv = FP.get_json, sys.argv
        FP.get_json, sys.argv = fake_get_json, ["forensic_pull.py", "TFOR"]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                FP.main()
        finally:
            FP.get_json, sys.argv = old_get, old_argv
        out = buf.getvalue()
    assert all("CIK0001234567" in u for u in calls) and len(calls) == 2, calls  # cik came from dcf_numbers.json
    assert "Pass 1 analysis date: 2026-09-15; latest period pass 1 used: 2026-06-30" in out, out
    assert "10-Q filed 2026-10-01, period 2026-09-30" in out and "2026-08-01" not in out, out
    assert "STALE_PASS1" in out
    assert not fake.unencoded, fake.unencoded


# ---------------- 5. the scripts still start ----------------
STRICT_RUNNER = r"""
import builtins, runpy, sys
_open = builtins.open
def _strict(file, mode="r", *a, **k):
    if "b" not in mode and k.get("encoding") is None and len(a) < 2:
        sys.stderr.write(f"UNENCODED_OPEN {file} {mode}\n")
        k["encoding"] = "cp1252"
    return _open(file, mode, *a, **k)
builtins.open = _strict
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
"""


def _run_strict(script, *args):
    env = dict(os.environ, STOCKS_BASE=BASE, PYTHONIOENCODING="utf-8")
    env.pop("DCF_NO_OVERRIDES", None)
    return subprocess.run([sys.executable, "-c", STRICT_RUNNER, os.path.join(SYS, script), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)


def test_dcf_engine_starts_offline():
    p = _run_strict("dcf_engine.py", "ZZZZNOCIK")
    assert p.returncode == 2, (p.returncode, p.stdout[-500:], p.stderr[-2000:])
    assert "NO_CIK for ZZZZNOCIK" in p.stdout, p.stdout[-500:]
    assert "UNENCODED_OPEN" not in p.stderr, p.stderr[-2000:]


def test_ttm_starts_offline():
    p = _run_strict("ttm.py", "ZZZZNOCIK")
    assert p.returncode == 2, (p.returncode, p.stdout[-500:], p.stderr[-2000:])
    assert "ttm.py: NO_CIK for ZZZZNOCIK" in p.stderr, p.stderr[-2000:]
    assert "UNENCODED_OPEN" not in p.stderr, p.stderr[-2000:]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if fails else 0)
