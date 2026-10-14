#!/usr/bin/env python3
"""score.json builder (v5, 2026-10-13 — zero hand transcription of numbers).

Usage: python3 make_score.py <TICKER>

Builds score.json purely from dcf_numbers.json plus judgment.json in the
company folder. Judgment fields (written by the analyzing agent):
  name, sector, moat_score, moat_justification, moat_for, moat_against
  (optional lists of short pillar strings), probs_used (5 numbers, the
  probabilities passed to the engine), one_liner, confidence,
  tier_override + tier_override_reason, in_scope_under_40b.
Every numeric field in score.json is copied from dcf_numbers.json.

Refuses (exit 1, nothing written) when: dcf_numbers.json has a data gap NOT
covered by an applied override, or no tier; judgment.json is missing/invalid;
probs_used does not sum to 1 or does not match the engine run; moat_score
does not match the engine run; a tier override lacks a written reason.

Round-2 additions (2026-10-14): refuses pre-v5 dcf_numbers.json (engine_version
< 5 or no data_gap field — the v4 bypass); refuses on content_hash mismatch or
absence (hand-edited engine output); refuses a negative override outright and
an out-of-band override (outside 0.1x-10x of the last filed value, or no
filed value) without an ack_reason; refuses a pinned base that differs from
ttm.json's ttm_oe_per_share by >0.1% unless judgment.json declares a matching
base_override; refuses a 20-F/40-F filer with no applied ads_ratio
(DATA_GAP:ads_ratio); refuses an in_scope_under_40b claim that contradicts
the engine's market cap (scope is computed here). Confidence is clamped to
medium (confidence_capped: true) when WIDE_SCENARIO_SPREAD is present. The
registry is rewritten wholesale for the ticker on every run and also records
judgment-call events: tier_override, manual_price, base_override, gterm,
cik, ads_ratio.

Overrides (v5.1): judgment.json may carry capex_override / sbc_override /
shares_override ({value, source, reason, kind: "filing"|"estimate"}). They
are validated for shape, cross-checked against dcf_numbers.json's
overrides_applied (value/kind must agree; an override declared for a field
the engine still shows as an uncovered gap refuses), summarized into
score.json, and upserted into the central registry
_system/overrides_registry.json (single writer: this script, fcntl-locked;
the path can be redirected with the MAKE_SCORE_REGISTRY env var, for tests).

Override impact (Andrew's basis, 2026-10-13): measured by THIS script, on
the base the final run actually used — "ttm" when the score's base was a
TTM pin via --base-oe-ps, else "median_3y" — never on the engine-native
base when a TTM pin is in force (that made APP read 0.0%/0.0pp while the
override moved the TTM base actually used by -0.45% and was the only
reason APP had a tier at all). The without-override side reruns the final
run's exact configuration (same moat/probs/offsets/mults/gterm and the
same base pin) with overrides toggled off: for a TTM base the base comes
from ttm.py with DCF_NO_OVERRIDES=1 (zero-fill; reconstructed from the
with-override ttm.py run when the disabled run cannot compute — the gap
is exactly why), for a median base from the engine's side-effect-free
--measure mode with overrides disabled. The block is written to score.json
as override_impact (the HTML and the registry read THIS block) and into
each registry entry, together with unblocks_tier: true when the final
dcf_numbers.json recorded data_gap entries the overrides fully covered —
without them the engine would have exited 4 and there would be no tier.
When the overridden field is shares (a denominator, not a subtractive
leg) no zero-fill counterfactual exists at all: the impact fields are
recorded as null with unblocks_tier: true rather than refusing the score
(first hit: STZ, 2026-10-14, whose FY24-26 diluted shares live only in
the 10-K — both the median and TTM counterfactuals have no denominator).

Also generates <TICKER>/key_numbers.md — every headline figure from the
final dcf_numbers.json in one formatted file. It is the single source
workers quote in analysis.md; no figure should ever be recomputed in prose.

If judgment.json is absent but score.json exists, judgment.json is seeded
from the existing score.json first (the v5 re-run path), then score.json is
rebuilt from the current dcf_numbers.json.
"""
import json, sys, os, datetime, fcntl, subprocess, hashlib
from zoneinfo import ZoneInfo

BASE = "/home/hatch/workspace/stocks"
SYS_DIR = f"{BASE}/_system"
ENGINE = f"{SYS_DIR}/dcf_engine.py"
TTM_PY = f"{SYS_DIR}/ttm.py"
LABELS = ["super_bear", "bear", "base", "bull", "super_bull"]
TIERS = ("S", "A", "B", "C", "D", "F")
CONFIDENCE = ("low", "medium", "high")
OVERRIDE_KEYS = {"capex": "capex_override", "sbc": "sbc_override", "shares": "shares_override"}
REGISTRY = os.environ.get("MAKE_SCORE_REGISTRY") or f"{SYS_DIR}/overrides_registry.json"


def fail(msg):
    print(f"make_score.py: REFUSED — {msg}", file=sys.stderr)
    sys.exit(1)


def seed_judgment(folder, score):
    probs = []
    sc = score.get("scenarios") or {}
    for lbl in LABELS:
        p = (sc.get(lbl) or {}).get("prob")
        if p is None:
            fail("cannot seed judgment.json: existing score.json lacks scenario probabilities")
        probs.append(p)
    override = None
    reason = None
    if score.get("tier_final") and score.get("tier_by_numbers") and score["tier_final"] != score["tier_by_numbers"]:
        override = score["tier_final"]
        reason = "Seeded from the pre-v5 score.json — the original override reason is in analysis.md"
    j = {"name": score.get("name"), "sector": score.get("sector"),
         "moat_score": score.get("moat_score"), "moat_justification": score.get("moat_justification"),
         "probs_used": probs, "one_liner": score.get("one_liner"),
         "confidence": score.get("confidence"), "tier_override": override,
         "tier_override_reason": reason, "in_scope_under_40b": score.get("in_scope_under_40b")}
    if isinstance(score.get("moat_for"), list):
        j["moat_for"] = score["moat_for"]
    if isinstance(score.get("moat_against"), list):
        j["moat_against"] = score["moat_against"]
    with open(f"{folder}/judgment.json", "w") as f:
        json.dump(j, f, indent=1)
    print(f"make_score.py: seeded judgment.json from existing score.json in {folder}")


def check_str_list(j, key):
    if key in j and j[key] is not None:
        if not isinstance(j[key], list) or not all(isinstance(x, str) for x in j[key]):
            fail(f"judgment.json: {key} must be a list of strings")


def validate_overrides(j):
    """Shape-check judgment.json's override objects; returns {field: override}."""
    out = {}
    for field, key in OVERRIDE_KEYS.items():
        o = j.get(key)
        if o is None:
            continue
        if not isinstance(o, dict):
            fail(f"judgment.json: {key} must be an object {{value, source, reason, kind}}")
        if not isinstance(o.get("value"), (int, float)) or isinstance(o.get("value"), bool):
            fail(f"judgment.json: {key}.value must be a number")
        if o["value"] < 0:
            # Round-2: a negative override is impossible, not a judgment call
            # (a negative capex override manufactured a Tier S in the harness).
            fail(f"judgment.json: {key}.value {o['value']} is negative — an override can never be "
                 "negative (capex / SBC / share counts are >= 0); refused outright")
        if o.get("kind") not in ("filing", "estimate"):
            fail(f"judgment.json: {key}.kind must be \"filing\" or \"estimate\"")
        if not str(o.get("source") or "").strip():
            fail(f"judgment.json: {key}.source must be a non-empty string")
        if not str(o.get("reason") or "").strip():
            fail(f"judgment.json: {key}.reason must be a non-empty string")
        out[field] = o
    return out


def validate_base_override(j):
    """judgment.json base_override {value, source, reason} — the declared
    provenance for a base pin that did NOT come from ttm.json. None if absent."""
    o = j.get("base_override")
    if o is None:
        return None
    if not isinstance(o, dict):
        fail("judgment.json: base_override must be an object {value, source, reason}")
    if not isinstance(o.get("value"), (int, float)) or isinstance(o.get("value"), bool):
        fail("judgment.json: base_override.value must be a number")
    if not str(o.get("source") or "").strip():
        fail("judgment.json: base_override.source must be a non-empty string")
    if not str(o.get("reason") or "").strip():
        fail("judgment.json: base_override.reason must be a non-empty string")
    return o


def validate_ads_ratio(j):
    """judgment.json ads_ratio {ratio, source, reason} for 20-F/40-F filers.
    None if absent; shape-checked if present."""
    a = j.get("ads_ratio")
    if a is None:
        return None
    if not isinstance(a, dict):
        fail("judgment.json: ads_ratio must be an object {ratio, source, reason}")
    if not isinstance(a.get("ratio"), (int, float)) or isinstance(a.get("ratio"), bool) or a["ratio"] <= 0:
        fail("judgment.json: ads_ratio.ratio must be a positive number (ordinary shares per ADS)")
    if not str(a.get("source") or "").strip():
        fail("judgment.json: ads_ratio.source must be a non-empty string")
    if not str(a.get("reason") or "").strip():
        fail("judgment.json: ads_ratio.reason must be a non-empty string")
    return a


def _run_json(cmd, env_extra=None, timeout=600):
    """Run a helper script and parse the JSON object from its stdout.
    Returns None on non-zero exit or unparseable output."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    txt = out.stdout or ""
    i = txt.find("{")
    if i < 0:
        return None
    try:
        return json.loads(txt[i:])
    except Exception:
        return None


def _final_run_args(n):
    """Engine CLI args replicating the final run recorded in dcf_numbers.json.
    Prefers the engine-recorded inputs block; falls back to deriving offsets
    from the recorded scenario g_starts minus the recorded g_base (verified
    to reproduce APP's final run bit-for-bit)."""
    scn = n.get("scenarios") or {}
    inp = n.get("inputs") or {}
    moat = inp.get("moat", n.get("moat_score"))
    probs = inp.get("probs") or [(scn.get(l) or {}).get("prob") for l in LABELS]
    mults = inp.get("mults") or [(scn.get(l) or {}).get("oe_mult") for l in LABELS]
    offsets = inp.get("offsets")
    if offsets is None:
        gb = n.get("g_base")
        offsets = [((scn.get(l) or {}).get("g_start") - gb)
                   if gb is not None and (scn.get(l) or {}).get("g_start") is not None else None
                   for l in LABELS]
    gterm = inp.get("g_terminal", n.get("g_terminal"))
    vals = [moat, gterm] + list(probs or []) + list(mults or []) + list(offsets or [])
    if any(v is None for v in vals):
        fail("dcf_numbers.json does not record the final run's inputs (moat/probs/offsets/mults/gterm) — "
             "cannot measure override impact; rerun the engine so it records them")
    args = ["--moat", repr(float(moat)),
            "--probs", ",".join(repr(float(p)) for p in probs),
            "--offsets", ",".join(repr(float(o)) for o in offsets),
            "--mults", ",".join(repr(float(m)) for m in mults),
            "--gterm", repr(float(gterm))]
    if n.get("price") is not None:
        args += ["--price", repr(float(n["price"]))]
    if n.get("cik"):
        args += ["--cik", str(n["cik"])]
    return args


def _ttm_base_without_overrides(ticker, n):
    """Zero-fill TTM OE/share. Primary: ttm.py with overrides disabled. When
    that cannot compute — the usual case, since the filing gap the override
    covers is exactly what breaks it — reconstruct zero-fill from the
    with-override run: remove each filled leg's contribution with TTM signs
    (FY - prior YTD + current YTD) from the OE total."""
    cik_args = ["--cik", str(n["cik"])] if n.get("cik") else []
    # DCF_TTM_NO_WRITE: these measurement runs must never clobber the worker's
    # ttm.json — the pin-provenance check compares the score's base against it.
    d = _run_json([sys.executable, TTM_PY, ticker] + cik_args, {"DCF_NO_OVERRIDES": "1", "DCF_TTM_NO_WRITE": "1"})
    if d is not None and d.get("ttm_oe_per_share") is not None:
        return d["ttm_oe_per_share"]
    d = _run_json([sys.executable, TTM_PY, ticker] + cik_args, {"DCF_TTM_NO_WRITE": "1"})
    if d is None or d.get("ttm_oe_per_share") is None or d.get("ttm_oe_total") is None:
        fail("cannot compute the no-override TTM base for the override impact (ttm.py failed with and without overrides)")
    used = {u.get("field"): u for u in d.get("overrides_used") or []}
    if "shares" in used:
        # No zero-fill denominator exists for shares: without the override
        # there is no TTM base at all. Signal "no counterfactual" (None);
        # the caller records a null impact with unblocks_tier set.
        return None
    oe_total = d["ttm_oe_total"]
    for field in ("capex", "sbc"):
        legs = (used.get(field) or {}).get("legs_filled") or {}
        oe_total += (legs.get("fy") or {}).get("amount", 0.0) \
                  - (legs.get("ytd_prior") or {}).get("amount", 0.0) \
                  + (legs.get("ytd_current") or {}).get("amount", 0.0)
    shares = d.get("ttm_shares_diluted")
    if not shares:
        fail("ttm.py returned no TTM share count — cannot measure override impact")
    return oe_total / shares


def compute_override_impact(ticker, n):
    """The impact block, on Andrew's basis: the base the final run actually
    used, the final run's exact configuration, toggling only the overrides.
    Returns the block stored in score.json (override_impact) and the registry."""
    base_with = n.get("base_oe_per_share")
    irr_with = n.get("implied_irr_weighted")
    gaps = list(n.get("data_gap") or [])
    unblocks = bool(gaps) and not (n.get("data_gap_uncovered") or [])
    base_src = (n.get("base_source") or "").lower()
    pinned = (n.get("inputs") or {}).get("base_oe_ps_arg") is not None or "ttm" in base_src
    base_used = "ttm" if pinned else "median_3y"
    args = _final_run_args(n)
    if base_used == "ttm":
        base_without = _ttm_base_without_overrides(ticker, n)
        if base_without is None:
            if not unblocks:
                fail("no no-override TTM base exists but the override covers no data gap — cannot measure override impact")
            irr_without = None
        else:
            m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args
                          + ["--base-oe-ps", repr(float(base_without))], {"DCF_NO_OVERRIDES": "1"})
            if m is None:
                fail("counterfactual engine --measure run failed — cannot measure override impact on the TTM base")
            irr_without = m.get("implied_irr_weighted")
    else:
        m = _run_json([sys.executable, ENGINE, ticker, "--measure"] + args, {"DCF_NO_OVERRIDES": "1"})
        if m is None or m.get("base_oe_per_share") is None:
            if not unblocks:
                fail("counterfactual engine --measure run failed — cannot measure override impact on the median base")
            # The override covers a data gap: without it the gate emits no
            # base at all, so the impact is honestly unmeasurable — record
            # nulls; unblocks_tier carries the information.
            base_without = None
            irr_without = None
        else:
            base_without = m["base_oe_per_share"]
            irr_without = m.get("implied_irr_weighted")
    base_pct = round((base_with - base_without) / base_without * 100, 3) \
        if isinstance(base_with, (int, float)) and base_without else None
    irr_pp = round((irr_with - irr_without) * 100, 3) \
        if isinstance(irr_with, (int, float)) and isinstance(irr_without, (int, float)) else None
    return {"base_used": base_used,
            "base_oe_without_override": round(base_without, 4) if isinstance(base_without, (int, float)) else None,
            "base_oe_with_override": round(base_with, 4) if isinstance(base_with, (int, float)) else None,
            "base_oe_impact_pct": base_pct,
            "weighted_irr_without_override": round(irr_without, 4) if isinstance(irr_without, (int, float)) else None,
            "weighted_irr_with_override": round(irr_with, 4) if isinstance(irr_with, (int, float)) else None,
            "weighted_irr_impact_pp": irr_pp,
            "unblocks_tier": unblocks}


def _default_cik(ticker):
    """The CIK the tickers-exchange mapping assigns (what the engine uses
    unless a --cik override or the CIK-fallback probe intervened)."""
    try:
        sec = json.load(open(f"{SYS_DIR}/sec_tickers_exchange.json"))
        m = {}
        for rec in sec["data"]:
            m.setdefault(rec[2].upper(), rec[0])
        for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
            if cand in m:
                return m[cand]
    except Exception:
        pass
    return None


def update_registry(ticker, applied, j_over, impact, j, n):
    """Replace this ticker's registry entries wholesale on every score
    (round-2: the old upsert only replaced fields still applied, so a
    removed override's entry went stale and stayed forever). Records the
    applied field overrides (schema unchanged: value/kind/source/reason +
    final-base impact + unblocks_tier) AND every other judgment call the
    run embodies, each as its own entry with "event": tier_override (with
    reason), manual_price, base_override, gterm (non-default), cik
    (non-default / fallback), ads_ratio. make_score.py is the single
    writer; the write is atomic under an fcntl lock."""
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    lock_fd = os.open(REGISTRY + ".lock", os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            reg = json.load(open(REGISTRY))
        except Exception:
            reg = {"entries": []}
        entries = [e for e in reg.get("entries", []) if e.get("ticker") != ticker]
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                a = applied[field]
                entries.append({"ticker": ticker, "field": field, "value": a["value"],
                                "kind": a["kind"], "source": a["source"],
                                "reason": j_over[field]["reason"], "date": today,
                                "base_used": impact["base_used"],
                                "base_oe_without_override": impact["base_oe_without_override"],
                                "base_oe_with_override": impact["base_oe_with_override"],
                                "base_oe_impact_pct": impact["base_oe_impact_pct"],
                                "weighted_irr_without_override": impact["weighted_irr_without_override"],
                                "weighted_irr_with_override": impact["weighted_irr_with_override"],
                                "weighted_irr_impact_pp": impact["weighted_irr_impact_pp"],
                                "unblocks_tier": impact["unblocks_tier"]})
        if j.get("tier_override"):
            entries.append({"ticker": ticker, "event": "tier_override", "date": today,
                            "tier_by_numbers": n.get("tier_by_numbers"),
                            "tier_final": j["tier_override"],
                            "reason": j.get("tier_override_reason")})
        if n.get("price_source") == "manual":
            entries.append({"ticker": ticker, "event": "manual_price", "date": today,
                            "value": n.get("price")})
        bo = j.get("base_override")
        if bo and ((n.get("inputs") or {}).get("base_oe_ps_arg") is not None
                   or "ttm" in (n.get("base_source") or "").lower()):
            entries.append({"ticker": ticker, "event": "base_override", "date": today,
                            "value": bo["value"], "source": bo["source"], "reason": bo["reason"]})
        gterm = (n.get("inputs") or {}).get("g_terminal", n.get("g_terminal"))
        if isinstance(gterm, (int, float)) and abs(gterm - 0.025) > 1e-9:
            entries.append({"ticker": ticker, "event": "gterm", "date": today, "value": gterm})
        cik_used = n.get("cik")
        cik_default = _default_cik(ticker)
        cik_fallback = any(str(f).startswith("CIK_FALLBACK") for f in n.get("fragility_flags") or [])
        if cik_used is not None and (cik_fallback or (cik_default is not None and int(cik_used) != int(cik_default))):
            entries.append({"ticker": ticker, "event": "cik", "date": today, "value": cik_used,
                            "note": "engine ran under a non-default CIK (--cik override or CIK-fallback probe)"})
        if n.get("ads_ratio"):
            a = n["ads_ratio"]
            entries.append({"ticker": ticker, "event": "ads_ratio", "date": today,
                            "ratio": a["ratio"], "source": a["source"], "reason": a["reason"]})
        reg["entries"] = entries
        tmp = REGISTRY + ".tmp"
        with open(tmp, "w") as f:
            json.dump(reg, f, indent=1)
        os.rename(tmp, REGISTRY)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def _usd(v):
    if v is None:
        return "—"
    a = abs(v)
    if a >= 1e9:
        return f"${v / 1e9:,.3f}B"
    if a >= 1e6:
        return f"${v / 1e6:,.1f}M"
    if a >= 1e3:
        return f"${v:,.0f}"
    return f"${v:,.2f}"


def _pct(x, digits=2):
    return "—" if x is None else f"{x * 100:.{digits}f}%"


def _money(v):
    return "—" if v is None else f"${v:,.2f}"


def write_key_numbers(folder, n, j, score, applied, impact=None):
    """key_numbers.md — every headline figure from the final dcf_numbers.json.
    The single source workers quote in analysis.md."""
    L = [f"# {n['ticker']} — key numbers",
         f"Generated by make_score.py from dcf_numbers.json (engine v{n.get('engine_version')}, as of {n.get('as_of')}).",
         "Quote these figures verbatim in analysis.md — never recompute or retype a derived figure.",
         "",
         "## Headline"]
    if n.get("price") is not None:
        L.append(f"- Price: ${n['price']:,.2f} (source: {n.get('price_source')})")
    tier_note = score["tier_final"]
    if score.get("tier_override_reason"):
        tier_note += f" (agent override of {n['tier_by_numbers']}: {score['tier_override_reason']})"
    conf_note = score["confidence"]
    if score.get("confidence_capped"):
        conf_note += " (capped from high by make_score: WIDE_SCENARIO_SPREAD present)"
    L.append(f"- Tier: {tier_note} · confidence {conf_note}")
    if n.get("implied_irr_weighted") is not None:
        w = n.get("weighted") or {}
        L.append(f"- Weighted IRR: {_pct(n['implied_irr_weighted'])} · base-case IRR: {_pct(n.get('implied_irr_base'))}")
        L.append(f"- Weighted IV: @15% {_money(w.get('iv_at_15'))} · @12% {_money(w.get('iv_at_12'))} · @10% {_money(w.get('iv_at_10'))}")
        L.append(f"- Upside vs price: @15% {_pct(n.get('upside_at_15'), 1)} · @12% {_pct(n.get('upside_at_12'), 1)}")
    if n.get("note"):
        L.append(f"- Note: {n['note']}")
    L += ["", "## Base owner's earnings",
          f"- Base OE/share: {_money(n.get('base_oe_per_share'))} (source: {n.get('base_source')})",
          f"- Latest FY OE/share: {_money(n.get('base_oe_latest_per_share'))} · normalized (3-yr median) OE/share: {_money(n.get('base_oe_normalized_per_share'))}",
          f"- Latest FY OE total: {_usd(n.get('base_oe_total_latest_fy'))}",
          f"- Shares diluted (latest): {n.get('shares_diluted_latest'):,.0f}" if n.get("shares_diluted_latest") else "- Shares diluted (latest): —",
          f"- Market cap (est): {_usd(n.get('market_cap_est'))} · net debt (latest): {_usd(n.get('net_debt_latest'))}",
          f"- OE-positive years (last 5): {n.get('oe_positive_years_of_last_5')}"]
    gc = n.get("growth_components") or {}
    L += ["", "## Growth & moat",
          f"- Growth blend: {_pct(n.get('g_blend'))}" + (f" → g_base {_pct(n.get('g_base'))}" if n.get("g_base") is not None else ""),
          f"- Components: rev CAGR 5y {_pct(gc.get('rev_cagr_5y'))} · rev CAGR 3y {_pct(gc.get('rev_cagr_3y'))} · latest rev YoY {_pct(gc.get('rev_yoy_latest'))} · OE/share CAGR 2y {_pct(gc.get('oe_ps_cagr_2y'))}",
          f"- Share count CAGR: {_pct(n.get('share_cagr'))} (growth adj {_pct(n.get('share_count_adj'))})",
          f"- Moat: {j['moat_score']}/10 · CAP {n.get('cap_years')} yrs · terminal growth {_pct(n.get('g_terminal'))}"]
    scn = n.get("scenarios") or {}
    if scn:
        L += ["", "## Scenarios",
              "| Scenario | Prob | Growth start | OE mult | IV@15 | IV@12 | IRR |",
              "|---|---|---|---|---|---|---|"]
        names = {"super_bear": "Super bear", "bear": "Bear", "base": "Base", "bull": "Bull", "super_bull": "Super bull"}
        for lbl in LABELS:
            r = scn.get(lbl) or {}
            L.append(f"| {names[lbl]} | {_pct(r.get('prob'), 0)} | {_pct(r.get('g_start'), 1)} | {r.get('oe_mult')} | "
                     f"{_money(r.get('iv_at_15'))} | {_money(r.get('iv_at_12'))} | {_pct(r.get('irr'))} |")
    d = n.get("diagnostics") or {}
    if d:
        # Round-2 fix: the old line was ONE conditional expression over a
        # concatenated f-string, so a blank scenario spread dropped the OE
        # yield and TV share lines with it. Each figure gets its own line.
        L += ["", "## Diagnostics",
              f"- OE yield: {_pct(d.get('oe_yield'))}",
              f"- TV share @15%: {_pct(d.get('tv_share_at_15'), 1)}",
              f"- Scenario spread (IV@15 super-bull / super-bear): {d['scenario_spread_iv15']:.2f}x" if d.get("scenario_spread_iv15") is not None else "- Scenario spread: —",
              f"- Net debt / normalized OE: {d.get('net_debt_to_normalized_oe'):.2f}x" if d.get("net_debt_to_normalized_oe") is not None else "- Net debt / normalized OE: —",
              f"- Months since FY end: {d.get('months_since_fy_end'):.1f}" if d.get("months_since_fy_end") is not None else "- Months since FY end: —"]
    flags = n.get("fragility_flags") or []
    L += ["", "## Fragility flags"]
    L += [f"- {f}" for f in flags] or ["- (none)"]
    if applied:
        L += ["", "## Overrides applied",
              f"Filing gaps found and covered by judgment overrides: {', '.join(n.get('data_gap') or []) or '—'}",
              "",
              "| Field | Value | Kind | Source | Periods filled |",
              "|---|---|---|---|---|"]
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                a = applied[field]
                val = _usd(a["value"]) if field in ("capex", "sbc") else f"{a['value']:,.0f}"
                L.append(f"| {field} | {val} | {a['kind']} | {a['source']} | {', '.join(a.get('periods_filled') or [])} |")
        for field in ("capex", "sbc", "shares"):
            if field in applied:
                L.append(f"- {field} reason: {applied[field]['reason']}")
        if impact:
            basis_lbl = "TTM base" if impact.get("base_used") == "ttm" else "3-yr median base"
            pct = impact.get("base_oe_impact_pct")
            pp = impact.get("weighted_irr_impact_pp")
            L += ["",
                  f"- Measured impact (on the {basis_lbl} actually used; same final configuration, overrides toggled off): "
                  f"base OE/share {_money(impact.get('base_oe_without_override'))} (no override) → "
                  f"{_money(impact.get('base_oe_with_override'))} (with override)"
                  + (f", {pct:+.2f}%" if isinstance(pct, (int, float)) else "")
                  + f" · weighted IRR {_pct(impact.get('weighted_irr_without_override'))} → {_pct(impact.get('weighted_irr_with_override'))}"
                  + (f" ({pp:+.2f}pp)" if isinstance(pp, (int, float)) else "")]
            if impact.get("unblocks_tier"):
                L.append("- Unblocks tier: YES — this override is the only reason this company has a tier; "
                         "without it the filing gap blocks scoring entirely.")
    with open(f"{folder}/key_numbers.md", "w") as f:
        f.write("\n".join(L) + "\n")


def main():
    ticker = sys.argv[1].upper()
    folder = f"{BASE}/{ticker}"
    npath, jpath, spath = f"{folder}/dcf_numbers.json", f"{folder}/judgment.json", f"{folder}/score.json"
    if not os.path.exists(npath):
        fail(f"no dcf_numbers.json in {folder} — run dcf_engine.py first")
    n = json.load(open(npath))
    # Round-2 audit (NOW item): never build a score from pre-v5, gate-less
    # engine output. Before this check, make_score happily rebuilt HIG's v4
    # Tier B score.json from a v4 dcf_numbers.json (SBC missing in every
    # year) — a complete bypass of the v5 data gate, live mid-re-run.
    ev = n.get("engine_version")
    if not isinstance(ev, (int, float)) or isinstance(ev, bool) or ev < 5 or "data_gap" not in n:
        fail(f"dcf_numbers.json is pre-v5 output (engine_version={ev!r}, "
             f"data_gap field {'present' if 'data_gap' in n else 'MISSING'}) — this folder holds "
             "pre-v5 output and the engine must be re-run under v5 before scoring; "
             "make_score.py never builds a score from gate-less engine output")
    # Provenance (round-2): the engine stamps dcf_numbers.json with a sha256
    # content hash over its canonical payload. A mismatch — or no hash at
    # all — means the numbers were touched after the engine run (the audit
    # hand-edited one to Tier S, 31% IRR, and it scored). Refuse both.
    ch = n.get("content_hash")
    if not ch:
        fail("dcf_numbers.json has no content_hash — it predates engine provenance stamping or was "
             "stripped; re-run dcf_engine.py so the engine stamps its own output before scoring")
    canon = json.dumps({k: v for k, v in n.items() if k != "content_hash"},
                       sort_keys=True, separators=(",", ":"), default=str)
    if hashlib.sha256(canon.encode()).hexdigest() != ch:
        fail("dcf_numbers.json content_hash MISMATCH — the engine output was modified after the run "
             "(hand-edited numbers); re-run dcf_engine.py and score only what the engine produces")
    applied = {}
    for o in n.get("overrides_applied") or []:
        if isinstance(o, dict) and o.get("field"):
            applied[o["field"]] = o
    gaps = list(n.get("data_gap") or [])
    uncovered = [f for f in gaps if f not in applied]
    for f in n.get("data_gap_uncovered") or []:
        if f not in applied and f not in uncovered:
            uncovered.append(f)
    if uncovered:
        fail(f"dcf_numbers.json has uncovered data_gap {uncovered} — no score may be written on an uncovered data gap (gaps fully covered by judgment overrides appear in overrides_applied)")
    if not n.get("tier_by_numbers"):
        fail("dcf_numbers.json has no tier_by_numbers — engine run did not produce a tier")

    if not os.path.exists(jpath):
        if os.path.exists(spath):
            seed_judgment(folder, json.load(open(spath)))
        else:
            fail(f"no judgment.json in {folder} and no score.json to seed from")
    j = json.load(open(jpath))

    for field in ("name", "sector", "moat_score", "moat_justification", "probs_used",
                  "one_liner", "confidence", "in_scope_under_40b"):
        if j.get(field) is None:
            fail(f"judgment.json: missing required field '{field}'")
    check_str_list(j, "moat_for")
    check_str_list(j, "moat_against")
    probs = j["probs_used"]
    if not (isinstance(probs, list) and len(probs) == 5 and all(isinstance(p, (int, float)) for p in probs)):
        fail("judgment.json: probs_used must be a list of 5 numbers")
    if abs(sum(probs) - 1.0) > 0.01:
        fail(f"judgment.json: probs_used sums to {sum(probs):.3f}, not 1.0")
    scn = n.get("scenarios") or {}
    if scn:
        for i, lbl in enumerate(LABELS):
            ep = (scn.get(lbl) or {}).get("prob")
            if ep is None or abs(ep - probs[i]) > 0.005:
                fail(f"judgment.json probs_used[{i}]={probs[i]} does not match engine scenario '{lbl}' prob {ep} — judgment.json is not the input set for this engine run")
    if n.get("moat_score") is not None and abs(float(j["moat_score"]) - float(n["moat_score"])) > 0.01:
        fail(f"judgment.json moat_score {j['moat_score']} does not match engine moat_score {n['moat_score']} — rerun the engine with this judgment or fix judgment.json")
    if j["confidence"] not in CONFIDENCE:
        fail(f"judgment.json: confidence must be one of {CONFIDENCE}")
    override = j.get("tier_override")
    if override is not None:
        if override not in TIERS:
            fail(f"judgment.json: tier_override must be one of {TIERS} or null")
        if not (j.get("tier_override_reason") or "").strip():
            fail("judgment.json: tier_override requires a tier_override_reason")
    j_over = validate_overrides(j)
    for field, o in j_over.items():
        if field in applied:
            a = applied[field]
            if a.get("kind") != o["kind"] or abs(float(a["value"]) - float(o["value"])) > max(1.0, abs(float(o["value"])) * 0.001):
                fail(f"judgment.json {field}_override (value {o['value']}, kind {o['kind']}) disagrees with dcf_numbers.json overrides_applied (value {a.get('value')}, kind {a.get('kind')}) — the judgment file and the engine run are out of sync; rerun the engine")
        elif field in gaps:
            fail(f"judgment.json declares {field}_override but dcf_numbers.json shows an uncovered {field} gap — rerun the engine so the override is applied before scoring")
    for field in applied:
        if field not in j_over:
            fail(f"dcf_numbers.json overrides_applied includes {field} but judgment.json declares no {field}_override")

    # Override sanity band (round-2): the engine measured each declared
    # override against the company's last FILED value for that field. A value
    # outside 0.1x-10x of it (or with no filed value at all) needs an explicit
    # ack_reason in judgment.json acknowledging the out-of-band value — the
    # harness typo (19 for 19,000,000) and the never-filed case both land here.
    checks = n.get("override_checks") or {}
    for field, o in j_over.items():
        chk = checks.get(field)
        if chk and chk.get("out_of_band") and not str(o.get("ack_reason") or "").strip():
            lf = chk.get("last_filed_value")
            lf_s = f"${lf:,.0f}" if isinstance(lf, (int, float)) else "no filed value at all"
            fail(f"judgment.json {field}_override value {o['value']:,.0f} is OUT OF BAND — outside 0.1x-10x of the "
                 f"last filed value ({lf_s}) — and judgment.json carries no ack_reason acknowledging it. "
                 "Correct the value, or add ack_reason explaining why an out-of-band figure is right")

    j_base_override = validate_base_override(j)
    j_ads = validate_ads_ratio(j)

    # ADS gate (round-2): a 20-F/40-F filer's per-share figures are per
    # ordinary share; the traded price is per ADS. Without an applied
    # ads_ratio the tier is meaningless — refuse with DATA_GAP:ads_ratio so
    # the worker blocks it like any other data gap.
    form = n.get("filer_annual_form")
    if form in ("20-F", "40-F"):
        n_ads = n.get("ads_ratio")
        if not n_ads:
            fail(f"DATA_GAP:ads_ratio — {ticker} files on {form} and no ads_ratio was applied by the engine, so its "
                 "per-share figures are per ordinary share while the price is per ADS. Block via queue.py with this "
                 "reason, or add ads_ratio {ratio, source, reason} to judgment.json (a main-agent decision) and rerun the engine")
        if not j_ads or abs(float(j_ads["ratio"]) - float(n_ads["ratio"])) > max(0.001, abs(float(n_ads["ratio"])) * 0.001):
            fail("judgment.json ads_ratio disagrees with the ratio the engine applied in dcf_numbers.json — "
                 "rerun the engine with the current judgment.json")

    # TTM pin provenance (round-2): a pinned base (--base-oe-ps / --ttm) must
    # trace to ttm.py's saved output (ttm.json) within 0.1%. Any other pin is
    # a free number (the harness's --base-oe-ps 9.99 made a Tier S) unless
    # judgment.json declares it as a base_override {value, source, reason}.
    inp = n.get("inputs") or {}
    pinned = inp.get("base_oe_ps_arg") is not None or "ttm" in (n.get("base_source") or "").lower()
    if pinned:
        score_base = n.get("base_oe_per_share")
        ttm_val = None
        try:
            with open(f"{folder}/ttm.json") as f:
                ttm_val = json.load(f).get("ttm_oe_per_share")
        except Exception:
            ttm_val = None
        via_ttm = (isinstance(ttm_val, (int, float)) and isinstance(score_base, (int, float))
                   and ttm_val != 0 and abs(score_base - ttm_val) <= 0.001 * abs(ttm_val))
        if not via_ttm:
            declared = (j_base_override and isinstance(score_base, (int, float)) and score_base != 0
                        and abs(float(j_base_override["value"]) - score_base) <= 0.001 * abs(score_base))
            if not declared:
                fail(f"base pin provenance: the score's base OE/share {score_base} differs from ttm.json's "
                     f"ttm_oe_per_share {ttm_val} by >0.1% (or ttm.json is missing) and judgment.json declares no "
                     "matching base_override {value, source, reason} — a pinned base must come from ttm.py "
                     "(ttm.json, via --ttm) or be declared as a base_override; an arbitrary pin is not scoreable")

    # Impact on the base the final run actually used — computed before any
    # write, so a measurement failure refuses cleanly like any other refusal.
    impact = compute_override_impact(ticker, n) if applied else None

    scenarios = {}
    for lbl in LABELS:
        r = scn.get(lbl)
        if r:
            scenarios[lbl] = {"prob": r.get("prob"),
                              "iv_at_15": round(r["iv_at_15"], 2) if r.get("iv_at_15") is not None else None,
                              "irr": round(r["irr"], 4) if r.get("irr") is not None else None}
    # Scope and confidence are COMPUTED here, never trusted from judgment
    # (round-2: in_scope_under_40b: true at a $93B market cap and confidence:
    # high under WIDE_SCENARIO_SPREAD were both accepted verbatim).
    mktcap = n.get("market_cap_est")
    computed_scope = (mktcap < 40e9) if isinstance(mktcap, (int, float)) else None
    if computed_scope is not None and bool(j["in_scope_under_40b"]) != computed_scope:
        fail(f"judgment.json in_scope_under_40b={j['in_scope_under_40b']} contradicts the engine's market cap "
             f"({_usd(mktcap)}) — scope is computed from market cap by make_score.py; fix judgment.json to match")
    scope_val = computed_scope if computed_scope is not None else j["in_scope_under_40b"]
    conf = j["confidence"]
    conf_capped = False
    if conf == "high" and any(str(f).startswith("WIDE_SCENARIO_SPREAD") for f in n.get("fragility_flags") or []):
        conf, conf_capped = "medium", True
    mktcap_b = round(n["market_cap_est"] / 1e9, 2) if n.get("market_cap_est") else None
    score = {"ticker": n["ticker"], "name": j["name"], "sector": j["sector"],
             "price": n.get("price"), "market_cap_b": mktcap_b,
             "engine_version": n.get("engine_version"),
             "base_oe_per_share": n.get("base_oe_per_share"),
             "base_year": (n.get("latest_period_end") or "")[:4] or None,
             "base_source": n.get("base_source"),
             "moat_score": j["moat_score"], "moat_justification": j["moat_justification"],
             "cap_years": n.get("cap_years"), "fragility_flags": n.get("fragility_flags", []),
             "scenarios": scenarios,
             "iv_at_15": round(n["iv_at_15"], 2) if n.get("iv_at_15") is not None else None,
             "iv_at_12": round(n["iv_at_12"], 2) if n.get("iv_at_12") is not None else None,
             "implied_irr": round(n["implied_irr_weighted"], 4) if n.get("implied_irr_weighted") is not None else None,
             "implied_irr_base_case": round(n["implied_irr_base"], 4) if n.get("implied_irr_base") is not None else None,
             "upside_at_15_pct": round(n["upside_at_15"] * 100, 1) if n.get("upside_at_15") is not None else None,
             "tier_by_numbers": n["tier_by_numbers"],
             "tier_final": override or n["tier_by_numbers"],
             "confidence": conf, "one_liner": j["one_liner"],
             "analysis_date": n.get("as_of"), "in_scope_under_40b": scope_val}
    if conf_capped:
        score["confidence_capped"] = True
    if override:
        score["tier_override_reason"] = j["tier_override_reason"]
    if j.get("moat_for"):
        score["moat_for"] = j["moat_for"]
    if j.get("moat_against"):
        score["moat_against"] = j["moat_against"]
    if applied:
        score["overrides"] = [{"field": f, "value": applied[f]["value"], "kind": applied[f]["kind"],
                               "source": applied[f]["source"]}
                              for f in ("capex", "sbc", "shares") if f in applied]
        score["override_impact"] = impact
    with open(spath, "w") as f:
        json.dump(score, f, indent=1)
    # Every run: the ticker's registry entries are replaced wholesale and
    # re-derived from THIS run (applied overrides + judgment-call events).
    update_registry(ticker, applied, j_over, impact, j, n)
    write_key_numbers(folder, n, j, score, applied, impact)
    print(f"make_score.py: wrote {spath} — tier {score['tier_final']}, weighted IRR {score['implied_irr']}, IV@15 {score['iv_at_15']}")


if __name__ == "__main__":
    main()
