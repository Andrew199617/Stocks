#!/usr/bin/env python3
"""Daily ranking + company pages — v2 (2026-10-14, engine 5.4 era).

Usage: python3 build_daily_html.py [--no-split] [--max-embed N] [--only T[,T...]]

Reads every <TICKER>/score.json — plus dcf_numbers.json, financials_history.csv
and, when present, fundamentals.json (fundamentals.py), prices.json (prices.py),
ttm.json, judgment.json, analysis.md and second_pass.md — and writes:

  _daily/ranking-YYYY-MM-DD.html and _daily/latest.html
      the ranking with every company page embedded: one self-contained file
      (the chat attachment), client-side tabs and detail switching
  _daily/companies/<TICKER>.html
      one standalone page per company (same renderer) for browsing the folder
      or publishing it; --no-split skips these

Company page = header (price, tier, expected return) → price-vs-value chart
(price history with the weighted IV@15 line, the bear–bull band and the 20% /
25% hurdle prices) → tabs: Overview · Financials · Forecast · Analysis · Data.

Every figure is read from the files. The only computation here is the
15-year projection replay for the Forecast tab, done with the engine's own
functions (imported from dcf_engine.py, never re-implemented), and the
display arithmetic a reader expects (growth %, margins) when fundamentals.json
has not been pulled yet. Charts are drawn in the browser from embedded JSON
so they stay sharp and readable at phone widths.

--max-embed N (default 250): full pages are embedded only for the top N
ranked rows; rows beyond link to their companies/ page, so the single file
cannot grow without bound as the sweep approaches 2,617 names.
"""
import json, os, glob, datetime, html, csv, re, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
OUT = f"{BASE}/_daily"
try:
    import dcf_engine as ENGINE
except Exception:  # the page still builds without the forecast replay
    ENGINE = None

TIER_ACCENT = {"S": "#B79CFF", "A": "#4ADE80", "B": "#5BD69C", "C": "#F2B84B", "D": "#F08A4B", "F": "#9AA3B2"}
TIER_MEANING = {"S": "≥25% expected return", "A": "20–25%", "B": "15–20% · clears the hurdle", "C": "10–15% · below hurdle", "D": "below 10%", "F": "no positive owner's earnings"}
LABELS = [("super_bear", "Super bear"), ("bear", "Bear"), ("base", "Base"), ("bull", "Bull"), ("super_bull", "Super bull")]
SCN_COLORS = {"super_bear": "#8A93A6", "bear": "#A7B1C7", "base": "#C9D4FF", "bull": "#9AD6B4", "super_bull": "#5BD69C", "weighted": "#FFFFFF"}
C_PRICE, C_IV, C_BAND, C_POS, C_NEG = "#FF8A8A", "#C9D4FF", "rgba(122,162,255,.18)", "#5BD69C", "#FF8A8A"
C_REV, C_NI, C_OE, C_OCF, C_CAPEX, C_SBC, C_CASH, C_DEBT, C_FCF = "#7AA2FF", "#5BD69C", "#C9D4FF", "#7484A0", "#F2B84B", "#F08A4B", "#7AA2FF", "#F08A4B", "#9AD6B4"


# ---------------------------------------------------------------- helpers
def esc(x):
    return html.escape("" if x is None else str(x), quote=True)


def num(v):
    try:
        if v is None or v == "":
            return None
        f = float(v)
        return f if f == f else None
    except Exception:
        return None


def fmt_money(v, d=2):
    v = num(v)
    return f"${v:,.{d}f}" if v is not None else "—"


def fmt_big(v):
    v = num(v)
    if v is None:
        return "—"
    s = "-" if v < 0 else ""
    a = abs(v)
    if a >= 1e12: return f"{s}${a/1e12:,.2f}T"
    if a >= 1e9: return f"{s}${a/1e9:,.2f}B"
    if a >= 1e6: return f"{s}${a/1e6:,.0f}M"
    if a >= 1e3: return f"{s}${a/1e3:,.0f}K"
    return f"{s}${a:,.2f}"


def fmt_cnt(v):
    v = num(v)
    if v is None:
        return "—"
    a = abs(v)
    if a >= 1e9: return f"{v/1e9:,.2f}B"
    if a >= 1e6: return f"{v/1e6:,.1f}M"
    return f"{v:,.0f}"


def fmt_pct(x, d=1, signed=False):
    x = num(x)
    if x is None:
        return "—"
    return f"{x*100:+.{d}f}%" if signed else f"{x*100:.{d}f}%"


def fmt_x(v, d=1):
    v = num(v)
    return f"{v:.{d}f}×" if v is not None else "—"


def sign_cls(v):
    v = num(v)
    return "" if v is None else ("pos" if v > 0 else "neg" if v < 0 else "")


def safe_id(ticker):
    return re.sub(r"[^A-Za-z0-9_-]", "-", str(ticker))


def jload(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def tread(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def attr_json(obj):
    """JSON for a single-quoted HTML attribute: only &, < and ' are escaped,
    so the quote-heavy JSON stays compact (html.escape would turn every "
    into &quot; — 5x the bytes on a 300-point price series)."""
    return json.dumps(obj, separators=(",", ":")).replace("&", "&amp;").replace("<", "&lt;").replace("'", "&#39;")


def chart(spec, cls=""):
    """A chart placeholder the browser renders from its JSON spec."""
    return f"<div class=\"chart {cls}\" data-chart='{attr_json(spec)}'></div>"


def is_current(numbers):
    ev = (numbers or {}).get("engine_version")
    return isinstance(ev, (int, float)) and not isinstance(ev, bool) and ev >= 5 and "data_gap" in numbers


# ---------------------------------------------------------------- markdown (analysis.md)
_INLINE = [(re.compile(r"\*\*(.+?)\*\*"), r"<b>\1</b>"), (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
           (re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)"), r'<a href="\2" target="_blank" rel="noopener">\1</a>')]


def _inline(s):
    s = esc(s)
    for rx, rep in _INLINE:
        s = rx.sub(rep, s)
    return s


def md_to_html(md):
    out, para, lst, tbl = [], [], None, None

    def flush_para():
        if para:
            out.append("<p>" + " ".join(_inline(x) for x in para) + "</p>"); para.clear()

    def flush_list():
        nonlocal lst
        if lst:
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in lst) + "</ul>"); lst = None

    def flush_tbl():
        nonlocal tbl
        if tbl:
            head, rows = tbl[0], tbl[1:]
            h = "".join(f"<th>{_inline(c)}</th>" for c in head)
            b = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="twrap"><table class="mdt"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'); tbl = None

    for line in (md or "").splitlines():
        s = line.rstrip()
        if s.startswith("|"):
            flush_para(); flush_list()
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c or "--") for c in cells):
                continue
            tbl = (tbl or []); tbl.append(cells); continue
        flush_tbl()
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            flush_para(); flush_list()
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>"); continue
        m = re.match(r"^\s*[-*]\s+(.*)", s)
        if m:
            flush_para(); lst = (lst or []); lst.append(m.group(1)); continue
        if s.strip() in ("---", "***"):
            flush_para(); flush_list(); out.append("<hr>"); continue
        if not s.strip():
            flush_para(); flush_list(); continue
        if lst is not None and s.startswith("  "):
            lst[-1] += " " + s.strip(); continue
        flush_list(); para.append(s.strip())
    flush_para(); flush_list(); flush_tbl()
    return "".join(out)


# ---------------------------------------------------------------- loading
def load_company(folder):
    c = {"_folder": os.path.basename(folder)}
    c["score"] = jload(f"{folder}/score.json") or {}
    c["numbers"] = jload(f"{folder}/dcf_numbers.json") or {}
    try:
        with open(f"{folder}/financials_history.csv", encoding="utf-8") as f:
            c["history"] = list(csv.DictReader(f))
    except Exception:
        c["history"] = []
    c["fund"] = jload(f"{folder}/fundamentals.json")
    c["prices"] = jload(f"{folder}/prices.json")
    c["ttm"] = jload(f"{folder}/ttm.json")
    c["judgment"] = jload(f"{folder}/judgment.json")
    c["analysis_md"] = tread(f"{folder}/analysis.md")
    c["second_pass_md"] = tread(f"{folder}/second_pass.md")
    return c


def load_all(only=None):
    current, stale = [], []
    for p in sorted(glob.glob(f"{BASE}/*/score.json")):
        folder = os.path.dirname(p)
        t = os.path.basename(folder)
        if only and t not in only:
            continue
        c = load_company(folder)
        if not c["score"]:
            continue
        if c["numbers"].get("data_gap_uncovered"):
            continue  # superseded by a DATA_GAP block
        (current if is_current(c["numbers"]) else stale).append(c)
    key = lambda c: (c["score"].get("implied_irr") if c["score"].get("implied_irr") is not None else -9)
    current.sort(key=key, reverse=True)
    stale.sort(key=key, reverse=True)
    for i, c in enumerate(current, 1):
        c["_rank"] = i
    return current, stale


def model_fit(c):
    s = c["score"]
    if s.get("model_fit"):
        return s["model_fit"]
    return "misfit" if any(str(f).startswith("SECTOR_MODEL_MISMATCH") for f in s.get("fragility_flags") or []) else "modeled"


# ---------------------------------------------------------------- forecast replay (engine functions)
def forecast_paths(n):
    """Per-share OE paths + growth schedules per scenario and weighted, from the
    recorded run inputs via the engine's own functions. Uses the engine's
    stored paths when present (5.4+), else replays bit-for-bit."""
    if n.get("paths") and n.get("growth_paths"):
        return n["paths"], n["growth_paths"]
    if ENGINE is None:
        return None, None
    inp, scn = n.get("inputs") or {}, n.get("scenarios") or {}
    base, gb = num(n.get("base_oe_per_share")), num(n.get("g_base"))
    if not inp or base is None or gb is None or not scn:
        return None, None
    gterm = inp.get("g_terminal", 0.025)
    cap = ENGINE.cap_years_for_moat(inp.get("moat", 5))
    paths, gpaths = {}, {}
    try:
        for i, (k, _) in enumerate(LABELS):
            g0 = max(ENGINE.GROWTH_FLOOR_START, min(ENGINE.GROWTH_CAP_START, gb + inp["offsets"][i]))
            paths[k] = ENGINE.project_path(base * inp["mults"][i], g0, cap, gterm)
            gpaths[k] = ENGINE.growth_path(g0, cap, gterm)
        probs = inp["probs"]
        paths["weighted"] = [sum(probs[i] * paths[LABELS[i][0]][t] for i in range(5)) for t in range(len(paths["base"]))]
    except Exception:
        return None, None
    return paths, gpaths


def hurdle_prices(n):
    """Weighted IV at 15 / 20 / 25% — stored by engine 5.4; replayed otherwise."""
    if n.get("hurdle_prices"):
        return {k: num(v) for k, v in n["hurdle_prices"].items()}
    paths, _ = forecast_paths(n)
    if not paths or ENGINE is None:
        return {"15": num(n.get("iv_at_15"))}
    gterm = (n.get("inputs") or {}).get("g_terminal", 0.025)
    w = paths["weighted"]
    return {"15": ENGINE.present_value(w, 0.15, gterm), "20": ENGINE.present_value(w, 0.20, gterm), "25": ENGINE.present_value(w, 0.25, gterm)}


def scenario_sensitivity(n):
    """{label: {10,12,15,20,25: iv}} from stored values (5.4) or replay."""
    scn = n.get("scenarios") or {}
    paths, _ = forecast_paths(n)
    gterm = (n.get("inputs") or {}).get("g_terminal", 0.025)
    out = {}
    for k, _ in LABELS + [("weighted", "Weighted")]:
        r = scn.get(k) if k != "weighted" else (n.get("weighted") or {})
        row = {}
        for rate in (10, 12, 15, 20, 25):
            v = (r or {}).get(f"iv_at_{rate}")
            if v is None and paths and ENGINE is not None and k in paths:
                v = ENGINE.present_value(paths[k], rate / 100, gterm)
            row[rate] = num(v)
        row["irr"] = num((r or {}).get("irr"))
        out[k] = row
    return out


# ---------------------------------------------------------------- page sections
def tile(k, v, cls="", sub=""):
    sub_h = f'<span class="tsub">{sub}</span>' if sub else ""
    return f'<div class="tile"><span class="k">{k}</span><span class="v {cls}">{v}</span>{sub_h}</div>'


def section(title, body, note="", extra_cls=""):
    n = f'<p class="note">{note}</p>' if note else ""
    return f'<section class="sec {extra_cls}"><h2>{title}</h2>{n}{body}</section>'


def header_html(c):
    s, n, pr = c["score"], c["numbers"], c["prices"] or {}
    tier = s.get("tier_final") or s.get("tier_by_numbers") or "?"
    acc = TIER_ACCENT.get(tier, "#9AA3B2")
    price = num(s.get("price"))
    st = pr.get("stats") or {}
    chg = num(st.get("change_1d_pct"))
    live = num(st.get("last"))
    live_html = ""
    if live is not None and st.get("last_date"):
        chg_s = f'<span class="{ "pos" if (chg or 0) >= 0 else "neg"}">{chg:+.2f}%</span>' if chg is not None else ""
        live_html = (f'<div class="hstat live"><span class="k">Last close</span>'
                     f'<span class="v mono">{fmt_money(live)} <small>{chg_s}</small></span>'
                     f'<span class="tsub">{esc(st["last_date"])} · 52-wk {fmt_money(st.get("low_52w"))}–{fmt_money(st.get("high_52w"))}'
                     + (f' · 1y {fmt_pct(num(st.get("ret_1y_pct")) / 100, 0, True)}' if st.get("ret_1y_pct") is not None else "") + "</span></div>")
    irr = num(s.get("implied_irr"))
    irr_s = fmt_pct(irr) if irr is not None else "—"
    floor = s.get("irr_at_floor") or (n.get("diagnostics") or {}).get("irr_at_floor")
    band = ""
    if s.get("tier_bear") and s.get("tier_bull"):
        band = f'<span class="tsub">Bear {fmt_pct(s.get("irr_bear"))} ({esc(s["tier_bear"])}) → Bull {fmt_pct(s.get("irr_bull"))} ({esc(s["tier_bull"])})</span>'
    elif (s.get("scenarios") or {}).get("bear") and ENGINE is not None:
        sb, su = num(s["scenarios"]["bear"].get("irr")), num((s["scenarios"].get("bull") or {}).get("irr"))
        if sb is not None and su is not None:
            band = f'<span class="tsub">Bear {fmt_pct(sb)} ({ENGINE.tier_for_irr(sb)}) → Bull {fmt_pct(su)} ({ENGINE.tier_for_irr(su)})</span>'
    up = num(s.get("upside_at_15_pct"))
    prof = (c["fund"] or {}).get("profile") or {}
    meta = " · ".join(x for x in [esc(s.get("sector")), fmt_cap(s.get("market_cap_b")),
                                  esc((prof.get("exchanges") or [None])[0]) if prof.get("exchanges") else "",
                                  esc(prof.get("filer_category")) if prof.get("filer_category") else ""] if x)
    fsub = ""
    if tier == "F":
        fs = s.get("f_subtype") or n.get("f_subtype")
        fsub = {"sbc_exceeds_cash": "F · SBC exceeds cash generation", "no_cash_generation": "F · no cash generation"}.get(fs, "F · no positive owner's earnings")
    return f"""<header class="hero" style="--acc:{acc}">
<div class="hrow">
<span class="ttile" style="background:{acc}">{esc(tier)}</span>
<div class="hname"><div class="hline"><span class="htick">{esc(s.get("ticker"))}</span><span class="hco">{esc(s.get("name"))}</span></div><span class="note">{meta}</span></div>
</div>
<div class="hstats">
<div class="hstat big"><span class="k">Expected return / yr</span><span class="v mono" style="color:{acc}">{irr_s}</span><span class="tsub">Probability-weighted IRR at {fmt_money(price)}{' · at the model floor' if floor else ''}{(' · ' + esc(fsub)) if fsub else ''}</span>{band}</div>
<div class="hstat"><span class="k">Price used</span><span class="v mono">{fmt_money(price)}</span><span class="tsub">{esc(n.get("price_source") or "")} · {esc(s.get("analysis_date") or "")}</span></div>
<div class="hstat"><span class="k">Value @15%</span><span class="v mono">{fmt_money(s.get("iv_at_15"))}</span><span class="tsub {sign_cls(up)}">{(f"{up:+.0f}% vs price") if up is not None else "—"}</span></div>
{live_html}
</div>
<p class="take">{esc(s.get("one_liner"))}</p>
</header>"""


def fmt_cap(v):
    v = num(v)
    return f"${v:,.2f}B" if v is not None else "—"


def price_chart_html(c):
    s, n, pr = c["score"], c["numbers"], c["prices"]
    price = num(s.get("price"))
    scn = n.get("scenarios") or s.get("scenarios") or {}
    ivs = [num((scn.get(k) or {}).get("iv_at_15")) for k, _ in LABELS]
    ivs = [v for v in ivs if v is not None]
    hp = hurdle_prices(n) if n else {}
    spec = {"iv15": num(s.get("iv_at_15")), "iv12": num(s.get("iv_at_12")),
            "lo": min(ivs) if ivs else None, "hi": max(ivs) if ivs else None,
            "bear": num((scn.get("bear") or {}).get("iv_at_15")), "bull": num((scn.get("bull") or {}).get("iv_at_15")),
            "h20": num(hp.get("20")), "h25": num(hp.get("25")), "price": price, "pdate": s.get("analysis_date")}
    if pr and pr.get("weekly"):
        spec["w"] = pr["weekly"]; spec["d"] = pr.get("daily_1y") or []
        spec["src"] = pr.get("source"); spec["asof"] = pr.get("as_of")
        ranges = "".join(f'<button data-r="{r}" class="{"on" if r == "5Y" else ""}">{r}</button>' for r in ("1Y", "3Y", "5Y", "10Y", "MAX"))
        toggles = ('<label><input type="checkbox" class="tg-iv" checked> Weighted value</label>'
                   '<label><input type="checkbox" class="tg-band" checked> Bear–bull range</label>'
                   '<label><input type="checkbox" class="tg-h"> 20% / 25% hurdle prices</label>')
        body = (f'<div class="pcbar"><div class="ranges">{ranges}</div><div class="toggles">{toggles}</div></div>'
                f"<div class=\"pchart\" data-px='{attr_json(spec)}'></div>"
                f'<div class="pcfoot"><span class="legend"><i style="background:{C_PRICE}"></i>Price</span><span class="legend"><i class="dash" style="border-color:{C_IV}"></i>Weighted IV @15%</span>'
                f'<span class="legend"><i style="background:{C_BAND};border:1px solid rgba(122,162,255,.6)"></i>Scenario range (super bear → super bull)</span><span class="pcret"></span></div>'
                f'<p class="note">Prices: {esc(pr.get("source") or "")}, through {esc(pr.get("as_of") or "")}. The valuation lines are the engine\'s values at a 15% discount rate — the price at which the expected return equals the hurdle. Where the price sits against them is the whole screen.</p>')
    else:
        body = price_vs_value_line(c) + '<p class="note">No price history pulled for this name yet (prices.py) — the number line shows today\'s price against every scenario\'s value.</p>'
    return f'<section class="sec pcsec"><div class="card pc">{body}</div></section>'


def price_vs_value_line(c):
    s, n = c["score"], c["numbers"]
    price, w_iv = num(s.get("price")), num(s.get("iv_at_15"))
    scn = n.get("scenarios") or s.get("scenarios") or {}
    ivs = [num(r.get("iv_at_15")) for r in scn.values() if num(r.get("iv_at_15")) is not None]
    if not (ivs and price and w_iv and w_iv > 0):
        return ""
    lo, hi = min(ivs), max(ivs)
    top = max(price, hi)
    axis_max = next((x for x in (10, 20, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000) if x > top * 1.04), top * 1.1)
    X = lambda v: v / axis_max * 100
    ticks = "".join(f"<span>${int(axis_max * i / 5):,}</span>" for i in range(6))
    return f"""<div class="pvplot">
<span class="pv-range-lbl" style="left:{X(lo):.2f}%">Scenario range</span>
<span class="pv-range-val" style="left:{X(lo):.2f}%">{fmt_money(lo)} – {fmt_money(hi)}</span>
<div class="pv-track"></div><div class="pv-band" style="left:{X(lo):.2f}%;width:{max(0.5, X(hi) - X(lo)):.2f}%"></div>
<div class="pv-ivmark" style="left:{X(w_iv):.2f}%"></div><div class="pv-pricedot" style="left:{X(price):.2f}%"></div>
<div class="pv-ivlbl" style="left:{X(w_iv):.2f}%"><span>Weighted IV</span><b>{fmt_money(w_iv)}</b></div>
<div class="pv-pricelbl"><span>Price</span><b>{fmt_money(price)}</b></div></div><div class="pv-axis">{ticks}</div>"""


def overview_html(c, registry):
    s, n = c["score"], c["numbers"]
    diag = n.get("diagnostics") or {}
    tier = s.get("tier_final") or s.get("tier_by_numbers") or "?"
    acc = TIER_ACCENT.get(tier, "#9AA3B2")
    irr = num(s.get("implied_irr"))
    scale = 30.0
    if irr is not None and irr * 100 > 30:
        scale = float(int(irr * 100 // 10 + 1) * 10)
    fill = max(0.0, min(100.0, irr * 100 / scale * 100)) if irr is not None else 0.0
    hurdle_left = 15 / scale * 100
    if irr is not None:
        diff = irr * 100 - 15
        glabel = f"{abs(diff):.1f} pts {'above' if diff >= 0 else 'below'} the 15% hurdle"
    else:
        glabel = "No positive owner's earnings — no return can be computed"
    chips = [f"Tier {esc(tier)} · {TIER_MEANING.get(tier, '')}"]
    if s.get("moat_score") is not None: chips.append(f"Moat {esc(s['moat_score'])}/10")
    if s.get("cap_years") is not None: chips.append(f"Advantage period {esc(s['cap_years'])} yrs")
    if s.get("confidence"): chips.append(f"Confidence {esc(s['confidence'])}" + (" (capped)" if s.get("confidence_capped") else ""))
    if model_fit(c) == "misfit": chips.append("Sector model misfit — tier is soft")
    for o in s.get("overrides") or []:
        if isinstance(o, dict) and o.get("field"):
            chips.append(f"{esc(o['field'])}: {'AI estimate' if o.get('kind') == 'estimate' else 'filing override'}")
    if s.get("tier_by_numbers") and tier != s.get("tier_by_numbers"):
        chips.append(f"Tier overridden {esc(s['tier_by_numbers'])}→{esc(tier)} by agent judgment")
    if s.get("engine_release"): chips.append(f"Engine {esc(s['engine_release'])}")
    elif n.get("engine_version"): chips.append("Engine 5.3.x (pre-5.4 numbers)")
    chips_html = "".join(f'<span class="chip">{x}</span>' for x in chips)
    gauge = f"""<div class="card verdict">
<div class="vmain"><div class="vgauge"><span class="vgl" style="color:{acc}">{glabel}</span>
<div class="gauge"><div class="gfill" style="width:{fill:.1f}%;background:{acc}"></div><div class="gtick" style="left:{hurdle_left:.1f}%"></div></div>
<div class="gscale"><span style="left:0">0%</span><span class="gmid" style="left:{hurdle_left:.1f}%">15% hurdle</span><span style="right:0">{scale:.0f}%</span></div></div></div>
<div class="chips">{chips_html}</div></div>"""
    # pass 2
    sp = s.get("second_pass") or {}
    p2 = ""
    if sp.get("verdict") == "changed":
        p2 = (f'<div class="p2box"><b>↺ Revised by pass 2 · {esc(sp.get("date"))}</b><p>Tier {esc(sp.get("prior_tier"))} → {esc(tier)} · Wtd IRR {fmt_pct(sp.get("prior_weighted_irr"))} → {fmt_pct(irr)} · IV@15% {fmt_money(sp.get("prior_iv_at_15"))} → {fmt_money(s.get("iv_at_15"))}</p><p>{esc(sp.get("summary"))}</p></div>')
    elif sp:
        p2 = f'<div class="p2box"><b>✓ Pass 2 checked {esc(sp.get("date"))} — no material change</b><p>{esc(sp.get("summary"))}</p></div>'
    # key numbers
    up = num(s.get("upside_at_15_pct"))
    hp = hurdle_prices(n) if n else {}
    tiles = "".join([
        tile("Price", fmt_money(s.get("price"))),
        tile("IV @15%", fmt_money(s.get("iv_at_15")), sub="clears 15%"),
        tile("Price for 20%", fmt_money(hp.get("20")), sub="Tier A hurdle"),
        tile("Price for 25%", fmt_money(hp.get("25")), sub="Tier S hurdle"),
        tile("Upside @15%", f"{up:+.0f}%" if up is not None else "—", sign_cls(up)),
        tile("Base-case IRR", fmt_pct(s.get("implied_irr_base_case"))),
        tile("OE yield", fmt_pct(diag.get("oe_yield")), sub="base OE / price"),
        tile("Terminal value share", fmt_pct(diag.get("tv_share_at_15")), sub="of IV @15%"),
        tile("Scenario spread", fmt_x(diag.get("scenario_spread_iv15")), sub="super bull / super bear"),
        tile("Net debt / OE", fmt_x(diag.get("net_debt_to_normalized_oe")), sub=fmt_big(s.get("net_debt_latest") if s.get("net_debt_latest") is not None else n.get("net_debt_latest"))),
    ])
    base_src = {"ttm_json": "TTM from ttm.py (10-Q YTD math)", "agent_supplied_ttm_override": "TTM pin (agent-supplied)",
                "median_of_last_3_fy_oe_per_share": "median of the last 3 fiscal years"}.get(s.get("base_source"), esc(s.get("base_source")))
    bps = num(s.get("base_oe_per_share"))
    kn = f"""<div class="tiles">{tiles}</div>
<div class="card baseoe"><span class="k">Base owner's earnings</span><span class="bv mono">{fmt_money(bps)}<span class="bu"> / share</span></span>
<p class="note">Basis: {base_src}. Latest FY {fmt_money(n.get("base_oe_latest_per_share"))}/sh · 3-yr median {fmt_money(n.get("base_oe_normalized_per_share"))}/sh · growth blend {fmt_pct(n.get("g_blend"))} → start {fmt_pct(n.get("g_base"))} · terminal {fmt_pct(n.get("g_terminal"))}.</p></div>"""
    # scenarios
    scn = n.get("scenarios") or s.get("scenarios") or {}
    rows = ""
    for k, lbl in LABELS:
        r = scn.get(k) or {}
        r_irr = num(r.get("irr"))
        w = max(0.0, min(100.0, r_irr * 100 / scale * 100)) if r_irr is not None else 0
        prob = f"{round(num(r.get('prob')) * 100)}%" if num(r.get("prob")) is not None else "—"
        rows += f"""<div class="scn"><div class="scnh"><span class="scnn"><i style="background:{SCN_COLORS[k]}"></i>{lbl}<span class="prob">{prob}</span></span><span class="mono scni">{fmt_pct(r_irr)}</span></div>
<div class="scnbar"><div class="scnfill" style="width:{w:.1f}%;background:{acc}"></div><div class="scntick" style="left:{hurdle_left:.1f}%"></div></div>
<div class="scnsub"><span>Growth start <b>{fmt_pct(r.get("g_start"))}</b></span><span>OE multiple <b>{fmt_x(r.get("oe_mult"), 2)}</b></span><span>IV @15% <b>{fmt_money(r.get("iv_at_15"))}</b></span></div></div>"""
    sc = f'<div class="card scncard">{rows}<div class="scnfoot"><span>Probability-weighted</span><span class="mono">IV {fmt_money(s.get("iv_at_15"))} · IRR {fmt_pct(irr)}</span></div></div>'
    # moat
    moat = num(s.get("moat_score"))
    dots = ('<span class="mdots">' + "".join(f'<i class="{"on" if i < round(moat) else ""}"></i>' for i in range(10)) + "</span>") if moat is not None else ""
    mfor, mag = s.get("moat_for"), s.get("moat_against")
    if isinstance(mfor, list) and mfor:
        cols = ('<div class="mcols"><div class="mcol"><span class="mk pos">Strengths</span><ul>' + "".join(f'<li><span class="sign pos">+</span><span>{esc(x)}</span></li>' for x in mfor) + '</ul></div>'
                '<div class="mcol"><span class="mk neg">Pressures</span><ul>' + "".join(f'<li><span class="sign neg">−</span><span>{esc(x)}</span></li>' for x in (mag or [])) + '</ul></div></div>')
    else:
        cols = f'<p class="dimp">{esc(s.get("moat_justification"))}</p>'
    moat_h = f'<div class="card"><div class="moathead"><span class="moattitle"><h2>Moat</h2><span class="mono moatscore">{esc(s.get("moat_score", "—"))}/10</span>{dots}</span><span class="note">Advantage period <b class="mono">{esc(s.get("cap_years", "—"))} yrs</b> · the moat sets how fast growth fades to {fmt_pct(n.get("g_terminal"))}</span></div>{cols}<p class="note">{esc(s.get("moat_justification")) if isinstance(mfor, list) and mfor else ""}</p></div>'
    # flags
    flags = s.get("fragility_flags") or []
    fl = ""
    if flags:
        items = "".join(f'<li><code>{esc(str(f).split(":")[0].split(" ")[0])}</code><span>{esc(str(f).split(":", 1)[1].strip() if ":" in str(f) else "")}</span></li>' for f in flags)
        fl = f'<div class="card"><ul class="flags">{items}</ul><p class="note">Each flag is resolved in the write-up — see the Analysis tab.</p></div>'
    # overrides
    ov = overrides_html(c, registry)
    return (gauge + p2 + section("Key numbers", kn) + (section("Overrides", ov, "Filing gaps filled by a judgment override — an override never replaces a filed value.") if ov else "")
            + section("Scenarios", sc, "IRR at today's price for each case, against the 15% hurdle.")
            + section("", moat_h) + (section(f"Fragility flags <span class='fcount mono'>{len(flags)}</span>", fl) if flags else ""))


def overrides_html(c, registry):
    s, n = c["score"], c["numbers"]
    ov_applied = n.get("overrides_applied") or []
    if not ov_applied and s.get("overrides"):
        ov_applied = [{"field": o.get("field"), "value": o.get("value"), "kind": o.get("kind"), "source": o.get("source"), "reason": "", "periods_filled": []} for o in s["overrides"] if isinstance(o, dict)]
    if not ov_applied:
        return ""
    rows = ""
    for o in ov_applied:
        v = o.get("value")
        fv = fmt_big(v) if o.get("field") in ("capex", "sbc") else fmt_cnt(v)
        rows += f"<tr><td>{esc(o.get('field'))}</td><td class='num mono'>{fv}</td><td>{esc(o.get('kind'))}</td><td>{esc(o.get('source'))}</td><td>{esc(', '.join(str(x)[:4] for x in (o.get('periods_filled') or [])))}</td></tr>"
    imp = s.get("override_impact") or {}
    imp_h = ""
    if imp:
        basis = "TTM base" if imp.get("base_used") == "ttm" else "3-year median base"
        pct, pp = num(imp.get("base_oe_impact_pct")), num(imp.get("weighted_irr_impact_pp"))
        imp_h = (f'<p class="note">Measured impact on the {basis} actually used (no override → with override): base OE/share {fmt_money(imp.get("base_oe_without_override"))} → {fmt_money(imp.get("base_oe_with_override"))}'
                 + (f" ({pct:+.2f}%)" if pct is not None else "") + f' · weighted IRR {fmt_pct(imp.get("weighted_irr_without_override"))} → {fmt_pct(imp.get("weighted_irr_with_override"))}' + (f" ({pp:+.2f}pp)" if pp is not None else "") + "</p>")
        if imp.get("unblocks_tier"):
            imp_h += '<p class="note"><b>This override is the only reason this company has a tier.</b> Without it the filing gap blocks scoring entirely — the judgment call is the whole verdict.</p>'
    reasons = "".join(f'<p class="note"><b>{esc(o.get("field"))}:</b> {esc(o.get("reason"))}</p>' for o in ov_applied if o.get("reason"))
    return f'<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Field</th><th class="num">Value</th><th>Kind</th><th>Source</th><th>Years filled</th></tr></thead><tbody>{rows}</tbody></table></div>{imp_h}{reasons}</div>'


def financials_html(c):
    s, n, fund = c["score"], c["numbers"], c["fund"]
    hist = c["history"] or []
    parts = []
    if fund:
        ann, q, ttm = fund.get("annual") or [], fund.get("quarterly") or [], fund.get("ttm")
        cur = fund.get("currency") or "USD"
        unit_note = f"Figures as filed with the SEC, in {esc(cur)}." + (" <b>Not USD</b> — the engine converts for the valuation; this tab shows the filings as filed." if cur != "USD" else "")
        warn = "".join(f'<li>{esc(w)}</li>' for w in fund.get("warnings") or [])
        if warn:
            unit_note += f'<ul class="warnlist">{warn}</ul>'
        # ---- quarterly
        if q:
            labels = [r.get("label") or r["period_end"] for r in q]
            spec = {"labels": labels, "yfmt": "big", "height": 240,
                    "series": [{"name": "Revenue", "color": C_REV, "kind": "bar", "values": [r.get("revenue") for r in q]},
                               {"name": "Net income", "color": C_NI, "kind": "line", "values": [r.get("net_income") for r in q]},
                               {"name": "Owner's earnings", "color": C_OE, "kind": "line", "values": [r.get("oe_conservative") for r in q]}]}
            head = "".join(f"<th class='num'>{esc(l)}</th>" for l in labels)
            def qrow(name, key, f=fmt_big, mark=None):
                cells = ""
                for r in q:
                    v = r.get(key)
                    d = r.get(f"{key}_derived")
                    cells += f"<td>{f(v)}{'<sup title=\"derived: year-to-date minus prior year-to-date\">†</sup>' if d else ''}</td>"
                return f"<tr><th>{name}</th>{cells}</tr>"
            def qpct(name, key):
                return f"<tr class='sub'><th>{name}</th>" + "".join(f"<td{(' class=' + sign_cls(r.get(key))) if sign_cls(r.get(key)) else ''}>{fmt_pct(r.get(key), 1, True)}</td>" for r in q) + "</tr>"
            qt = f"""<div class="twrap"><table class="fin"><thead><tr><th>Quarter</th>{head}</tr><tr class="sub"><th>Period end</th>{"".join(f"<td>{esc(r['period_end'])}</td>" for r in q)}</tr></thead><tbody>
{qrow("Revenue", "revenue")}{qpct("Revenue growth (YoY)", "revenue_yoy")}{qrow("Gross margin", "gross_margin", fmt_pct)}{qrow("Operating income", "operating_income")}{qrow("Net income", "net_income")}{qpct("Net income growth (YoY)", "net_income_yoy")}{qrow("EPS (diluted)", "eps_diluted", fmt_money)}
{qrow("Operating cash flow", "ocf")}{qrow("Capex", "capex")}{qrow("Stock-based comp", "sbc")}{qrow("Owner's earnings (cons.)", "oe_conservative")}{qpct("Owner's earnings growth (YoY)", "oe_conservative_yoy")}{qrow("Diluted shares", "shares_diluted", fmt_cnt)}</tbody></table></div>"""
            ttm_h = ""
            if ttm:
                ttm_h = ('<div class="tiles">' + tile("TTM revenue", fmt_big(ttm.get("revenue")), sub=fmt_pct(ttm.get("revenue_yoy"), 1, True) + " YoY" if ttm.get("revenue_yoy") is not None else "")
                         + tile("TTM net income", fmt_big(ttm.get("net_income")), sub=fmt_pct(ttm.get("net_income_yoy"), 1, True) + " YoY" if ttm.get("net_income_yoy") is not None else "")
                         + tile("TTM operating CF", fmt_big(ttm.get("ocf")), sub=fmt_pct(ttm.get("ocf_yoy"), 1, True) + " YoY" if ttm.get("ocf_yoy") is not None else "")
                         + tile("TTM owner's earnings", fmt_big(ttm.get("oe_conservative")), sub=(fmt_money(ttm.get("oe_per_share")) + " / share") if ttm.get("oe_per_share") is not None else "")
                         + tile("TTM OE margin", fmt_pct(ttm.get("oe_margin")), sub=f"through {esc(ttm.get('period_end'))}")
                         + tile("TTM SBC", fmt_big(ttm.get("sbc")), sub=(fmt_pct(num(ttm.get("sbc")) / num(ttm.get("ocf"))) + " of OCF") if num(ttm.get("sbc")) is not None and num(ttm.get("ocf")) else "")
                         + "</div>")
            parts.append(section("Quarterly", ttm_h + f'<div class="card">{chart(spec)}{qt}<p class="note">† derived as year-to-date minus the prior year-to-date in the same fiscal year (cash-flow lines are filed year-to-date only); Q4 = fiscal year minus nine months.</p></div>',
                                 "The last twelve fiscal quarters, filing-direct. This is the trend the annual history hides."))
        # ---- annual
        if ann:
            labels = [r["fy"] for r in ann]
            spec = {"labels": labels, "yfmt": "big", "height": 240,
                    "series": [{"name": "Revenue", "color": C_REV, "kind": "bar", "values": [r.get("revenue") for r in ann]},
                               {"name": "Net income", "color": C_NI, "kind": "line", "values": [r.get("net_income") for r in ann]},
                               {"name": "Owner's earnings", "color": C_OE, "kind": "line", "values": [r.get("oe_conservative") for r in ann]}]}
            head = "".join(f"<th class='num'>FY{esc(l)}</th>" for l in labels)
            def arow(name, key, f=fmt_big, cls=""):
                return f"<tr{(' class=' + cls) if cls else ''}><th>{name}</th>" + "".join(f"<td>{f(r.get(key))}</td>" for r in ann) + "</tr>"
            def apct(name, key):
                return f"<tr class='sub'><th>{name}</th>" + "".join(f"<td{(' class=' + sign_cls(r.get(key))) if sign_cls(r.get(key)) else ''}>{fmt_pct(r.get(key), 1, True)}</td>" for r in ann) + "</tr>"
            inc = f"""<div class="twrap"><table class="fin"><thead><tr><th>Income statement</th>{head}</tr><tr class="sub"><th>Period end</th>{"".join(f"<td>{esc(r['period_end'])}</td>" for r in ann)}</tr></thead><tbody>
{arow("Revenue", "revenue", cls="strong")}{apct("Revenue growth", "revenue_growth")}{arow("Cost of revenue", "cogs")}{arow("Gross profit", "gross_profit")}{apct("Gross margin", "gross_margin")}{arow("R&amp;D", "rnd")}{arow("SG&amp;A", "sga")}{arow("Operating income", "operating_income", cls="strong")}{apct("Operating margin", "operating_margin")}{arow("Interest expense", "interest_expense")}{arow("Pretax income", "pretax_income")}{arow("Income tax", "tax")}{arow("Net income", "net_income", cls="strong")}{apct("Net margin", "net_margin")}{apct("Net income growth", "net_income_growth")}{arow("EPS (diluted)", "eps_diluted", fmt_money)}{apct("EPS growth", "eps_diluted_growth")}{arow("Diluted shares", "shares_diluted", fmt_cnt)}{apct("Share count change", "shares_diluted_growth")}</tbody></table></div>"""
            cf = f"""<div class="twrap"><table class="fin"><thead><tr><th>Cash flow</th>{head}</tr></thead><tbody>
{arow("Operating cash flow", "ocf", cls="strong")}{apct("OCF growth", "ocf_growth")}{arow("Capex", "capex")}{apct("Capex % revenue", "capex_pct_rev")}{arow("Depreciation &amp; amortization", "da")}{arow("Stock-based compensation", "sbc")}{apct("SBC % revenue", "sbc_pct_rev")}{apct("SBC % OCF", "sbc_pct_ocf")}{arow("Free cash flow (OCF − capex)", "fcf")}{arow("Owner's earnings (OCF − capex − SBC)", "oe_conservative", cls="strong")}{apct("Owner's earnings margin", "oe_margin")}{apct("Owner's earnings growth", "oe_conservative_growth")}{arow("OE per share", "oe_per_share", fmt_money)}{apct("OE/share growth", "oe_per_share_growth")}{arow("Dividends paid", "dividends_paid")}{arow("Buybacks", "buybacks")}{arow("Acquisitions", "acquisitions")}{arow("Investing cash flow", "icf")}{arow("Financing cash flow", "fincf")}</tbody></table></div>"""
            bs = f"""<div class="twrap"><table class="fin"><thead><tr><th>Balance sheet</th>{head}</tr></thead><tbody>
{arow("Cash &amp; equivalents", "cash")}{arow("Short-term investments", "short_term_investments")}{arow("Receivables", "receivables")}{arow("Inventory", "inventory")}{arow("Prepaids", "prepaids")}{apct("Prepaids % assets", "prepaids_pct_assets")}{arow("Current assets", "assets_current")}{arow("PP&amp;E (net)", "ppe_net")}{arow("Goodwill", "goodwill")}{apct("Goodwill % assets", "goodwill_pct_assets")}{arow("Intangibles", "intangibles")}{arow("Total assets", "assets", cls="strong")}{arow("Current liabilities", "liab_current")}{arow("Deferred revenue", "deferred_revenue")}{arow("Total debt", "total_debt", cls="strong")}{arow("Net debt (debt − cash)", "net_debt")}{arow("Operating lease liabilities", "lease_liabilities")}{arow("Total liabilities", "liabilities")}{arow("Shareholders' equity", "equity", cls="strong")}{arow("Book value / share", "book_value_per_share", fmt_money)}{arow("Current ratio", "current_ratio", fmt_x)}{apct("Return on equity", "roe")}{apct("ROIC (proxy)", "roic_proxy")}{arow("Net debt / owner's earnings", "net_debt_to_oe", fmt_x)}</tbody></table></div>"""
            cash_debt = {"labels": labels, "yfmt": "big", "height": 220,
                         "series": [{"name": "Cash", "color": C_CASH, "kind": "bar", "values": [r.get("cash") for r in ann]},
                                    {"name": "Total debt", "color": C_DEBT, "kind": "bar", "values": [-(num(r.get("total_debt")) or 0) if r.get("total_debt") is not None else None for r in ann]},
                                    {"name": "Net debt", "color": "#ECEEF2", "kind": "line", "values": [r.get("net_debt") for r in ann]}]}
            margins = {"labels": labels, "yfmt": "pct", "height": 200, "zero": True,
                       "series": [{"name": "Gross margin", "color": C_REV, "kind": "line", "values": [r.get("gross_margin") for r in ann]},
                                  {"name": "Operating margin", "color": C_NI, "kind": "line", "values": [r.get("operating_margin") for r in ann]},
                                  {"name": "Owner's-earnings margin", "color": C_OE, "kind": "line", "values": [r.get("oe_margin") for r in ann]}]}
            cfchart = {"labels": labels, "yfmt": "big", "height": 220,
                       "series": [{"name": "Operating CF", "color": C_OCF, "kind": "bar", "values": [r.get("ocf") for r in ann]},
                                  {"name": "Capex", "color": C_CAPEX, "kind": "bar", "values": [-(num(r.get("capex")) or 0) if r.get("capex") is not None else None for r in ann]},
                                  {"name": "SBC", "color": C_SBC, "kind": "bar", "values": [-(num(r.get("sbc")) or 0) if r.get("sbc") is not None else None for r in ann]},
                                  {"name": "Owner's earnings", "color": C_OE, "kind": "line", "values": [r.get("oe_conservative") for r in ann]}]}
            capret = {"labels": labels, "yfmt": "big", "height": 180,
                      "series": [{"name": "Buybacks", "color": C_IV, "kind": "bar", "values": [r.get("buybacks") for r in ann]},
                                 {"name": "Dividends", "color": C_FCF, "kind": "bar", "values": [r.get("dividends_paid") for r in ann]},
                                 {"name": "Acquisitions", "color": C_CAPEX, "kind": "bar", "values": [r.get("acquisitions") for r in ann]}]}
            parts.append(section("Revenue &amp; profits", f'<div class="card">{chart(spec)}{inc}</div>', unit_note))
            parts.append(section("Cash flow &amp; owner's earnings", f'<div class="card">{chart(cfchart)}{cf}</div>', "Owner's earnings = operating cash flow − capex − stock-based compensation (SBC always treated as a real cost)."))
            parts.append(section("Margins", f'<div class="card">{chart(margins)}</div>'))
            parts.append(section("Cash &amp; debt", f'<div class="card">{chart(cash_debt)}{bs}</div>', "Debt is shown below the axis; the line is net debt. Operating leases are listed separately and are not in net debt (comparability across the universe)."))
            parts.append(section("Capital returned", f'<div class="card">{chart(capret)}</div>', "Cash actually paid out: buybacks, dividends, and acquisitions, per the cash-flow statement."))
    if not parts:
        # fall back to the engine's own history CSV
        if hist:
            labels = [r.get("fy_label") for r in hist]
            spec = {"labels": labels, "yfmt": "big", "height": 230,
                    "series": [{"name": "Revenue", "color": C_REV, "kind": "bar", "values": [num(r.get("revenue")) for r in hist]},
                               {"name": "OE (cons.)", "color": C_OE, "kind": "line", "values": [num(r.get("oe_conservative")) for r in hist]},
                               {"name": "OE (maint.)", "color": C_FCF, "kind": "line", "values": [num(r.get("oe_maintenance")) for r in hist]}]}
            rows = "".join(f"<tr><td>{esc(r.get('fy_label'))}</td><td class='num mono'>{fmt_big(r.get('revenue'))}</td><td class='num mono'>{fmt_big(r.get('net_income'))}</td><td class='num mono'>{fmt_big(r.get('ocf'))}</td><td class='num mono'>{fmt_big(r.get('capex'))}</td><td class='num mono'>{fmt_big(r.get('sbc'))}</td><td class='num mono'>{fmt_big(r.get('oe_conservative'))}</td><td class='num mono'>{fmt_big(r.get('oe_maintenance'))}</td><td class='num mono'>{fmt_cnt(r.get('shares_diluted'))}</td></tr>" for r in hist[-10:])
            parts.append(section("Financial history (engine)", f'<div class="card">{chart(spec)}<div class="twrap"><table class="mini"><thead><tr><th>FY</th><th class="num">Revenue</th><th class="num">Net income</th><th class="num">Op CF</th><th class="num">Capex</th><th class="num">SBC</th><th class="num">OE (cons)</th><th class="num">OE (maint)</th><th class="num">Shares</th></tr></thead><tbody>{rows}</tbody></table></div><p class="note">The extended statements appear once fundamentals.py has been run for this name.</p></div>'))
        else:
            parts.append('<p class="note">No financial history available.</p>')
    return "".join(parts)


def forecast_html(c):
    s, n = c["score"], c["numbers"]
    if not n.get("scenarios"):
        return '<div class="card"><p class="note">No projection: the engine found no positive normalized owner\'s earnings (Tier F), so there is no cash-flow path to discount.</p></div>'
    paths, gpaths = forecast_paths(n)
    parts = []
    inp = n.get("inputs") or {}
    gterm = inp.get("g_terminal", n.get("g_terminal"))
    years = [str(i) for i in range(1, 16)]
    base = num(n.get("base_oe_per_share"))
    if paths:
        series = [{"name": lbl, "color": SCN_COLORS[k], "kind": "line", "values": [round(v, 4) for v in paths[k]]} for k, lbl in LABELS]
        series.append({"name": "Probability-weighted", "color": SCN_COLORS["weighted"], "kind": "line", "width": 3, "values": [round(v, 4) for v in paths["weighted"]]})
        spec = {"labels": years, "yfmt": "money", "height": 260, "series": series, "zero": True, "xlabel": "Projection year"}
        gs = [{"name": lbl, "color": SCN_COLORS[k], "kind": "line", "values": [round(v, 5) for v in gpaths[k]]} for k, lbl in LABELS]
        gspec = {"labels": years, "yfmt": "pct", "height": 200, "series": gs, "zero": True, "xlabel": "Projection year"}
        parts.append(section("Owner's earnings per share — the five paths",
                             f'<div class="card">{chart(spec)}<p class="note">Base {fmt_money(base)}/share × each scenario\'s OE multiple, grown along its growth path. The weighted line is the probability-weighted path whose IRR is the headline. Year-15 flow carries a Gordon terminal value at {fmt_pct(gterm)} growth.</p></div>',
                             "What the DCF actually discounts."))
        parts.append(section("Growth fade", f'<div class="card">{chart(gspec)}<p class="note">Growth holds for 2 years, then converges linearly to the {fmt_pct(gterm)} terminal rate over the competitive advantage period of {esc(s.get("cap_years"))} years (moat {esc(s.get("moat_score"))}/10 → CAP = 2 + 1.3 × moat).</p></div>'))
    sens = scenario_sensitivity(n)
    price = num(s.get("price"))
    head = "".join(f"<th class='num'>IV @{r}%</th>" for r in (10, 12, 15, 20, 25))
    rows = ""
    for k, lbl in LABELS + [("weighted", "Probability-weighted")]:
        r = sens.get(k) or {}
        cells = ""
        for rate in (10, 12, 15, 20, 25):
            v = r.get(rate)
            cls = "pos" if (v is not None and price and v >= price) else ("neg" if v is not None else "")
            cells += f"<td class='num mono {cls}'>{fmt_money(v)}</td>"
        prob = (n.get("scenarios") or {}).get(k, {}).get("prob") if k != "weighted" else None
        rows += f"<tr class='{'strong' if k == 'weighted' else ''}'><th>{lbl}{(' <span class=prob>' + str(round(prob * 100)) + '%</span>') if prob is not None else ''}</th>{cells}<td class='num mono'>{fmt_pct(r.get('irr'))}</td></tr>"
    sens_h = f"""<div class="card"><div class="twrap"><table class="fin"><thead><tr><th>Scenario</th>{head}<th class="num">IRR at {fmt_money(price)}</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Each cell is the price at which that scenario returns that rate. Green = at or above today's price. The 15% column is the hurdle; 20% and 25% are the Tier A and Tier S prices.</p></div>"""
    parts.append(section("Value at every discount rate", sens_h, "Sensitivity of value to the return you demand."))
    hp = hurdle_prices(n)
    tiles = "".join([tile("Price for 15% (Tier B)", fmt_money(hp.get("15")), sign_cls((hp.get("15") or 0) - (price or 0)) if hp.get("15") else ""),
                     tile("Price for 20% (Tier A)", fmt_money(hp.get("20")), sign_cls((hp.get("20") or 0) - (price or 0)) if hp.get("20") else ""),
                     tile("Price for 25% (Tier S)", fmt_money(hp.get("25")), sign_cls((hp.get("25") or 0) - (price or 0)) if hp.get("25") else ""),
                     tile("Today's price", fmt_money(price))])
    band = ""
    if ENGINE is not None:
        scn = n.get("scenarios") or {}
        sb, su = num((scn.get("bear") or {}).get("irr")), num((scn.get("bull") or {}).get("irr"))
        if sb is not None and su is not None:
            band = f'<p class="note">Tier band: bear case <b>{ENGINE.tier_for_irr(sb)}</b> ({fmt_pct(sb)}) to bull case <b>{ENGINE.tier_for_irr(su)}</b> ({fmt_pct(su)}); headline tier {esc(s.get("tier_by_numbers"))} on the weighted path{(" → " + esc(s.get("tier_final")) + " after agent override") if s.get("tier_final") != s.get("tier_by_numbers") else ""}. Size any position to the bear end.</p>'
    parts.append(section("Hurdle prices", f'<div class="tiles">{tiles}</div>{band}', "The price at which the probability-weighted path returns each hurdle. Green = today's price is below it (the hurdle clears)."))
    gc = n.get("growth_components") or {}
    gca = n.get("growth_components_adjusted") or {}
    comp_rows = "".join(f"<tr><th>{lbl}</th><td class='num mono'>{fmt_pct(gc.get(k))}</td><td class='num mono'>{fmt_pct(gca.get(k)) if gca else '—'}</td></tr>"
                        for k, lbl in (("rev_cagr_5y", "Revenue CAGR 5y"), ("rev_cagr_3y", "Revenue CAGR 3y"), ("rev_yoy_latest", "Latest revenue YoY"), ("oe_ps_cagr_2y", "OE/share CAGR 2y")))
    method = f"""<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Growth signal</th><th class="num">Raw</th><th class="num">Share-adjusted</th></tr></thead><tbody>{comp_rows}
<tr class="strong"><th>Blend (median)</th><td class="num mono">{fmt_pct(n.get("g_blend"))}</td><td class="num mono">→ start {fmt_pct(n.get("g_base"))}</td></tr></tbody></table></div>
<p class="note">Share-count CAGR {fmt_pct(n.get("share_cagr"))} → adjustment {fmt_pct(n.get("share_count_adj"), 1, True)} ({esc(n.get("share_adj_basis") or "applied to the blend (pre-5.4 engine)")}). Scenario offsets {esc(inp.get("offsets"))} pp and OE multiples {esc(inp.get("mults"))} with probabilities {esc(inp.get("probs"))}. Start growth is capped at 35% (base) / 50% (scenario) — see README Fixes &amp; lessons.</p></div>"""
    parts.append(section("How growth was set", method))
    return "".join(parts)


def analysis_html(c):
    out = []
    if c["analysis_md"]:
        out.append(f'<div class="card md">{md_to_html(c["analysis_md"])}</div>')
    else:
        out.append('<div class="card"><p class="note">No analysis.md in this folder.</p></div>')
    if c["second_pass_md"]:
        out.append(section("Second pass", f'<div class="card md">{md_to_html(c["second_pass_md"])}</div>'))
    return "".join(out)


def data_html(c, registry):
    s, n, fund, ttm, j = c["score"], c["numbers"], c["fund"], c["ttm"], c["judgment"]
    prof = (fund or {}).get("profile") or {}
    rows = []
    def kv(k, v):
        rows.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
    kv("Entity", f"{esc(n.get('name') or s.get('name'))} · CIK {esc(n.get('cik'))} · <a href='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={esc(n.get('cik'))}&type=10-K' target='_blank' rel='noopener'>EDGAR</a>")
    if prof:
        kv("Industry (SIC)", f"{esc(prof.get('sic_description'))} ({esc(prof.get('sic'))})")
        fye = prof.get("fiscal_year_end_mmdd") or ""
        kv("Fiscal year end", f"{esc(fye[:2])}/{esc(fye[2:])} · {esc(prof.get('filer_category'))} · incorporated {esc(prof.get('state_of_incorporation'))}")
        lf = prof.get("latest_filings") or {}
        for form, d in lf.items():
            link = f" · <a href='{esc(d.get('url'))}' target='_blank' rel='noopener'>open</a>" if d.get("url") else ""
            kv(f"Latest {esc(form)}", f"filed {esc(d.get('filed'))} for the period ending {esc(d.get('period'))}{link}")
        kv("8-K filings, last 12 months", esc(prof.get("eight_k_count_12m")))
    kv("Engine", f"v{esc(n.get('engine_version'))} · release {esc(n.get('engine_release') or '5.3.x (pre-5.4)')} · run {esc(n.get('as_of'))} · annual form {esc(n.get('filer_annual_form'))}")
    kv("Price", f"{fmt_money(n.get('price'))} ({esc(n.get('price_source'))}) · market cap est. {fmt_big(n.get('market_cap_est'))} · diluted shares {fmt_cnt(n.get('shares_diluted_latest'))}")
    kv("Base", f"{fmt_money(n.get('base_oe_per_share'))}/share · {esc(n.get('base_source'))} · pin source {esc((n.get('inputs') or {}).get('base_pin_source'))}")
    inp = n.get("inputs") or {}
    kv("Run inputs", f"moat {esc(inp.get('moat'))} · probs {esc(inp.get('probs'))} · offsets {esc(inp.get('offsets'))} · mults {esc(inp.get('mults'))} · g_terminal {esc(inp.get('g_terminal'))}")
    kv("Net debt basis", f"{fmt_big(n.get('net_debt_latest'))} · {esc(n.get('net_debt_basis') or 'current + noncurrent tags (pre-5.4)')}" + (f" · operating leases {fmt_big(n.get('lease_liabilities_latest'))}" if n.get("lease_liabilities_latest") is not None else ""))
    if n.get("fx_conversion"):
        fx = n["fx_conversion"]
        kv("FX conversion", f"{esc(fx.get('from_currency'))} → USD at period-end ECB rates ({esc(fx.get('source'))}); rates {esc(json.dumps(fx.get('rates')))}")
    if n.get("ads_ratio"):
        kv("ADS ratio", f"{esc(n['ads_ratio'].get('ratio'))} ordinary per ADS · {esc(n['ads_ratio'].get('source'))}")
    kv("Data gaps", f"{esc(n.get('data_gap') or [])} (uncovered: {esc(n.get('data_gap_uncovered') or [])})")
    kv("Content hash", f"<span class='mono'>{esc((n.get('content_hash') or '')[:16])}…</span>" if n.get("content_hash") else "none (pre-stamping run)")
    ut = n.get("used_tags") or {}
    kv("EDGAR tags (engine)", "<br>".join(f"<span class='mono small'>{esc(k)}: {esc(v)}</span>" for k, v in ut.items() if v))
    if (fund or {}).get("tags_used"):
        kv("EDGAR tags (fundamentals)", "<br>".join(f"<span class='mono small'>{esc(k)}: {esc(', '.join(v))}</span>" for k, v in fund["tags_used"].items() if v))
    kv("Files", " · ".join(f"<span class='mono'>{esc(f)}</span>" for f in sorted(os.listdir(f"{BASE}/{c['_folder']}")) if not f.startswith(".")))
    prov = f'<div class="card"><div class="twrap"><table class="kv"><tbody>{"".join(rows)}</tbody></table></div></div>'
    parts = [section("Provenance", prov)]
    if ttm and ttm.get("inputs"):
        trs = ""
        for k, lbl in (("ocf", "Operating cash flow"), ("capex", "Capex"), ("sbc", "Stock-based comp"), ("shares_diluted", "Diluted shares")):
            d = ttm["inputs"].get(k) or {}
            f = fmt_cnt if k == "shares_diluted" else fmt_big
            trs += (f"<tr><th>{lbl}</th><td class='num mono'>{f(d.get('fy'))}</td><td class='num mono'>{f(d.get('ytd_prior'))}</td><td class='num mono'>{f(d.get('ytd_current'))}</td>"
                    f"<td class='num mono strong'>{f(d.get('ttm')) if k != 'shares_diluted' else f(d.get('ytd_current'))}</td><td class='small'>{esc(d.get('fy_tag'))}</td></tr>")
        t = f"""<div class="card"><div class="twrap"><table class="fin"><thead><tr><th>TTM leg</th><th class="num">FY {esc((ttm['inputs'].get('ocf') or {}).get('fy_period', ['', ''])[1])}</th><th class="num">− prior YTD</th><th class="num">+ current YTD</th><th class="num">= TTM</th><th>Tag</th></tr></thead><tbody>{trs}</tbody></table></div>
<p class="note">TTM owner's earnings {fmt_big(ttm.get('ttm_oe_total'))} ÷ {fmt_cnt(ttm.get('ttm_shares_diluted'))} shares = <b class="mono">{fmt_money(ttm.get('ttm_oe_per_share'))}</b> / share, computed by ttm.py from EDGAR 10-Q year-to-date facts (FY − prior YTD + current YTD). {("Overrides used: " + esc(", ".join(o.get("field") for o in ttm.get("overrides_used") or []))) if ttm.get("overrides_used") else ""}</p></div>"""
        parts.append(section("TTM construction", t))
    ov = overrides_html(c, registry)
    if ov:
        parts.append(section("Overrides", ov))
    ev = [e for e in registry.get(s.get("ticker"), []) if e.get("event")]
    if ev:
        li = "".join(f"<li><code>{esc(e.get('event'))}</code> {esc(e.get('date'))}: " + esc(", ".join(f"{k}={v}" for k, v in e.items() if k not in ("ticker", "event", "date"))) + "</li>" for e in ev)
        parts.append(section("Judgment calls on record", f'<div class="card"><ul class="flags">{li}</ul><p class="note">From _system/overrides_registry.json — every judgment call the run embodies.</p></div>'))
    if j:
        parts.append(section("judgment.json", f'<div class="card"><pre class="json">{esc(json.dumps(j, indent=1))}</pre></div>', "The agent's judgment inputs exactly as make_score.py consumed them."))
    return "".join(parts)


def company_page(c, registry, standalone=False, prev_next=None):
    s = c["score"]
    sid = safe_id(s.get("ticker"))
    back = "../latest.html" if standalone else "#"
    back_attr = "" if standalone else ' onclick="return backToList()"'
    nav_right = f"Pass 1 · {esc(s.get('analysis_date'))}"
    if (s.get("second_pass") or {}).get("verdict") == "changed":
        nav_right = f"Pass 2 revised · {esc(s['second_pass'].get('date'))}"
    pn = ""
    if prev_next:
        p, nx = prev_next
        pl = f'<a href="{("" if standalone else "#") + (p + ".html" if standalone else p)}" {"" if standalone else "onclick=\"return showDetail(\'" + p + "\')\""} class="pn">← {esc(p)}</a>' if p else "<span></span>"
        nl = f'<a href="{("" if standalone else "#") + (nx + ".html" if standalone else nx)}" {"" if standalone else "onclick=\"return showDetail(\'" + nx + "\')\""} class="pn">{esc(nx)} →</a>' if nx else "<span></span>"
        pn = f'<div class="pnav">{pl}<span class="note">rank {esc(c.get("_rank", "—"))}</span>{nl}</div>'
    tabs = [("overview", "Overview"), ("financials", "Financials"), ("forecast", "Forecast"), ("analysis", "Analysis"), ("data", "Data")]
    tab_btns = "".join(f'<button class="tab{" on" if i == 0 else ""}" data-tab="{k}">{lbl}</button>' for i, (k, lbl) in enumerate(tabs))
    panes = (f'<div class="pane on" data-pane="overview">{overview_html(c, registry)}</div>'
             f'<div class="pane" data-pane="financials">{financials_html(c)}</div>'
             f'<div class="pane" data-pane="forecast">{forecast_html(c)}</div>'
             f'<div class="pane" data-pane="analysis">{analysis_html(c)}</div>'
             f'<div class="pane" data-pane="data">{data_html(c, registry)}</div>')
    return f"""<article class="page" id="d-{sid}" data-ticker="{esc(s.get('ticker'))}">
<nav class="dnav"><a class="back" href="{back}"{back_attr}>← Ranking</a><span class="navr mono">{nav_right}</span></nav>
{header_html(c)}
{price_chart_html(c)}
<div class="tabs" role="tablist">{tab_btns}</div>
{panes}
{pn}
<footer class="dfoot"><span>Screening-grade standardized DCF — not a buy or sell call.</span><span class="mono">stocks/{esc(c['_folder'])}/</span></footer>
</article>"""


# ---------------------------------------------------------------- ranking list
def row_html(c, embedded):
    s = c["score"]
    t = s.get("ticker", "")
    sid = safe_id(t)
    tier = s.get("tier_final") or s.get("tier_by_numbers") or "?"
    irr, up, moat = num(s.get("implied_irr")), num(s.get("upside_at_15_pct")), num(s.get("moat_score"))
    fit = model_fit(c)
    sp = s.get("second_pass") or {}
    badges = []
    if sp.get("verdict") == "changed":
        badges.append(f'<span class="bdg p2">↺ pass 2: {esc(sp.get("prior_tier"))} → {esc(tier)}</span>')
    elif sp:
        badges.append('<span class="bdg p2">✓ pass 2</span>')
    for o in s.get("overrides") or []:
        if isinstance(o, dict) and o.get("field"):
            badges.append(f'<span class="bdg ov">{esc(o["field"])}: {"AI estimate" if o.get("kind") == "estimate" else "filing override"}</span>')
    if s.get("tier_by_numbers") and tier != s.get("tier_by_numbers"):
        badges.append(f'<span class="bdg to">tier {esc(s["tier_by_numbers"])}→{esc(tier)} by judgment</span>')
    if fit == "misfit":
        badges.append('<span class="bdg mf">sector misfit</span>')
    if s.get("irr_at_floor"):
        badges.append('<span class="bdg mf">IRR at floor</span>')
    fl = s.get("fragility_flags") or []
    tb, tu = s.get("tier_bear"), s.get("tier_bull")
    if not (tb and tu) and ENGINE is not None:
        sb, su = num(((s.get("scenarios") or {}).get("bear") or {}).get("irr")), num(((s.get("scenarios") or {}).get("bull") or {}).get("irr"))
        tb, tu = (ENGINE.tier_for_irr(sb) if sb is not None else None), (ENGINE.tier_for_irr(su) if su is not None else None)
    band = f'<span class="band"><i style="background:{TIER_ACCENT.get(tb, "#333")}">{esc(tb)}</i>→<i style="background:{TIER_ACCENT.get(tu, "#333")}">{esc(tu)}</i></span>' if tb and tu else "—"
    href = f"companies/{sid}.html"
    onclick = f' onclick="return showDetail(\'{sid}\')"' if embedded else ""
    st = ((c.get("prices") or {}).get("stats") or {})
    r1 = num(st.get("ret_1y_pct"))
    return f"""<tr data-tier="{esc(tier)}" data-fit="{fit}" data-conf="{esc(s.get('confidence'))}" data-irr="{irr if irr is not None else -9}" data-up="{up if up is not None else -999}" data-moat="{moat if moat is not None else -1}" data-cap="{num(s.get('market_cap_b')) or 0}" data-bear="{num(s.get('irr_bear')) if s.get('irr_bear') is not None else (num(((s.get('scenarios') or {}).get('bear') or {}).get('irr')) or -9)}" data-search="{esc((t + ' ' + str(s.get('name', '')) + ' ' + str(s.get('sector', ''))).lower())}">
<td class="co"><a href="{href}"{onclick}><b class="mono">{esc(t)}</b><span class="nm">{esc(s.get('name'))}</span></a><span class="sub">{esc(s.get('sector'))}</span></td>
<td><span class="tbadge" style="background:{TIER_ACCENT.get(tier, '#333')}">{esc(tier)}</span></td>
<td class="num">{band}</td>
<td class="num mono strong">{fmt_pct(irr)}</td>
<td class="num mono">{fmt_money(s.get('price'))}</td>
<td class="num mono">{fmt_money(s.get('iv_at_15'))}</td>
<td class="num mono {sign_cls(up)}">{(f'{up:+.0f}%') if up is not None else '—'}</td>
<td class="num mono">{(f'{moat:.0f}/10') if moat is not None else '—'}</td>
<td>{esc(s.get('confidence'))}</td>
<td class="num mono">{fmt_cap(s.get('market_cap_b'))}</td>
<td class="num mono {sign_cls(r1)}">{(f'{r1:+.0f}%') if r1 is not None else '—'}</td>
<td class="take">{''.join(badges)}<span>{esc(s.get('one_liner'))}</span><span class="sub">{('⚠ ' + str(len(fl)) + ' flags · ') if fl else ''}{esc(s.get('analysis_date'))} · <a href="{href}"{onclick} class="more">details ›</a></span></td></tr>
"""


def list_page(current, stale, embedded_ids, today, progress):
    done, total = progress
    counts = {}
    for c in current:
        counts[c["score"].get("tier_final") or "?"] = counts.get(c["score"].get("tier_final") or "?", 0) + 1
    misfits = sum(1 for c in current if model_fit(c) == "misfit")
    rows = "".join(row_html(c, safe_id(c["score"].get("ticker")) in embedded_ids) for c in current)
    stale_rows = "".join(f"<tr><td><b class='mono'>{esc(c['score'].get('ticker'))}</b> {esc(c['score'].get('name'))}</td><td><span class='tbadge stale'>{esc(c['score'].get('tier_final') or c['score'].get('tier_by_numbers'))}</span></td><td class='num mono'>{fmt_pct(c['score'].get('implied_irr'))}</td><td>{esc(c['score'].get('analysis_date'))}</td></tr>" for c in stale)
    stale_h = (f'<details class="stalebox"><summary>Pre-v5 results — re-run pending ({len(stale)})</summary><p class="note">Produced before the data gate existed; shown for reference only, every one is queued for a v5 re-run.</p><div class="twrap"><table class="mini"><thead><tr><th>Company</th><th>Old tier</th><th class="num">Old Wtd IRR</th><th>Scored</th></tr></thead><tbody>{stale_rows}</tbody></table></div></details>' if stale else "")
    tier_chips = "".join(f'<span class="tchip" style="--c:{TIER_ACCENT[t]}"><i>{t}</i>{counts.get(t, 0)}</span>' for t in "SABCDF")
    pct = (done / total * 100) if total else 0
    return f"""<div id="listView">
<header class="lhead">
<div><h1>Owner's-Earnings DCF Ranking</h1><div class="note">{esc(today)} · {done:,} of {total:,} companies under $40B analyzed ({pct:.1f}%) · ranked by probability-weighted expected return at today's price · tap a company for its page</div>
<div class="prog"><div style="width:{pct:.2f}%"></div></div></div>
<div class="tchips">{tier_chips}<span class="tchip"><i style="background:#3A4252">MF</i>{misfits} sector misfits</span></div>
</header>
<details class="howto"><summary>How to read this</summary><p>Each company gets a five-scenario owner's-earnings DCF (super bear / bear / base / bull / super bull, each with an assigned likelihood); growth fades over a moat-driven competitive advantage period. <b>Wtd IRR</b> is the probability-weighted expected annual return at the current price; the <b>band</b> is the bear-case → bull-case tier. <b>IV</b> is the probability-weighted intrinsic value per share at a 15% discount rate; <b>Upside</b> is IV vs price. Tiers: S ≥25% · A 20–25% · B 15–20% (clears the 15% hurdle) · C 10–15% · D &lt;10% · F no positive owner's earnings. Banks, insurers, REITs and utilities fit the owner's-earnings model poorly and are marked <b>sector misfit</b> — their tiers are soft. Screening-grade standardized DCF — read the Analysis tab before acting.</p></details>
<div class="controls">
<div class="seg" id="tierseg"><button data-f="all" class="on">All</button><button data-f="S">S</button><button data-f="A">A</button><button data-f="B">B</button><button data-f="C">C</button><button data-f="D">D</button><button data-f="F">F</button></div>
<div class="seg" id="fitseg"><button data-fit="modeled" class="on">Modeled</button><button data-fit="misfit">Sector misfits</button><button data-fit="all">All</button></div>
<select id="sort"><option value="irr">Sort: Wtd IRR</option><option value="bear">Sort: Bear-case IRR</option><option value="up">Sort: Upside @15%</option><option value="moat">Sort: Moat</option><option value="cap">Sort: Market cap</option></select>
<input id="q" placeholder="Search ticker / name / sector…"><span class="note" id="count"></span>
</div>
<div class="twrap"><table id="t"><thead><tr><th>Company</th><th>Tier</th><th class="num">Band</th><th class="num">Wtd IRR</th><th class="num">Price</th><th class="num">IV @15%</th><th class="num">Upside</th><th class="num">Moat</th><th>Conf.</th><th class="num">Mkt cap</th><th class="num">1y price</th><th>Take</th></tr></thead>
<tbody>{rows if rows else '<tr><td colspan="12">No companies analyzed yet.</td></tr>'}</tbody></table></div>
{stale_h}
</div>"""


# ---------------------------------------------------------------- CSS / JS
CSS = r"""
:root{color-scheme:dark;--bg:#0C0E12;--card:#14171D;--card2:#1B1F27;--line:#272C36;--line2:#2C323D;--txt:#ECEEF2;--txt2:#D9DDE4;--mut:#A0A8B6;--acc:#C9D4FF;--pos:#5BD69C;--neg:#FF8A8A;--sans:'IBM Plex Sans',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;--mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--txt);font-family:var(--sans);-webkit-font-smoothing:antialiased;padding:16px 16px 72px}
a{color:var(--acc)} a:hover{color:#fff}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.mono{font-family:var(--mono)} .small{font-size:12px} .pos{color:var(--pos)} .neg{color:var(--neg)}
.note{font-size:13.5px;color:var(--mut);line-height:1.5;margin:6px 0} .note b{color:var(--txt);font-weight:500}
.k{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;margin:12px 0}
.sec{margin:26px 0} .sec>h2{font-size:19px;font-weight:600;margin:0 0 4px} .sec>h2:empty{display:none}
h1{font-size:22px;margin:0 0 4px}
.twrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:13.5px} th,td{padding:8px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top} td.num,th.num{text-align:right;white-space:nowrap}
table.mini{font-size:13px} table.mini th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);font-weight:500}
table.fin{font-size:13px;min-width:640px} table.fin td{text-align:right;white-space:nowrap;font-family:var(--mono)} table.fin th{font-weight:500;color:var(--txt2);white-space:nowrap;position:sticky;left:0;background:var(--card);z-index:1} table.fin thead th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)} table.fin thead th.num{text-align:right} table.fin thead tr.sub th,table.fin thead tr.sub td{font-size:11px;color:var(--mut);text-transform:none;letter-spacing:0;padding-top:0;font-family:var(--mono)}
table.fin tr.sub th{color:var(--mut);font-size:12.5px;padding-left:22px} table.fin tr.sub td{font-size:12.5px}
table.fin tr.strong th,table.fin tr.strong td{color:#fff;font-weight:600;background:rgba(255,255,255,.02)}
table.kv th{width:190px;color:var(--mut);font-weight:500;font-size:12.5px} table.kv td{word-break:break-word}
table.mdt th{font-weight:600} .md h2{font-size:17px;margin:18px 0 6px} .md h3{font-size:15px;margin:16px 0 4px} .md h4{font-size:14px;margin:14px 0 4px} .md p{line-height:1.6;margin:8px 0;color:var(--txt2)} .md ul{padding-left:20px;line-height:1.55;color:var(--txt2)} .md li{margin:4px 0} .md code{font-family:var(--mono);font-size:12.5px;background:var(--card2);padding:1px 5px;border-radius:4px}
pre.json{font-family:var(--mono);font-size:12px;white-space:pre-wrap;word-break:break-word;color:var(--txt2);margin:0}
sup{font-size:9px;color:var(--mut)}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:10px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:5px;min-width:0}
.tile .v{font-family:var(--mono);font-size:20px;font-weight:500} .tsub{font-size:12px;color:var(--mut)}
.chip{display:inline-flex;align-items:center;padding:6px 10px;border-radius:999px;background:var(--card2);border:1px solid var(--line2);font-size:13px;color:#D4D8E0} .chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.prob{font-family:var(--mono);font-size:12px;padding:2px 7px;border-radius:999px;background:var(--card2);border:1px solid var(--line2);color:#C3C9D4;font-weight:400;margin-left:8px}
/* ---- list ---- */
.lhead{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px 24px;align-items:flex-start}
.prog{height:6px;border-radius:3px;background:var(--line);margin-top:10px;max-width:520px} .prog div{height:6px;border-radius:3px;background:var(--acc)}
.tchips{display:flex;flex-wrap:wrap;gap:8px} .tchip{display:inline-flex;align-items:center;gap:7px;font-family:var(--mono);font-size:13px;padding:5px 10px 5px 5px;border-radius:999px;background:var(--card2);border:1px solid var(--line2)} .tchip i{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:6px;background:var(--c);color:#0C0E12;font-style:normal;font-weight:600;font-size:12px}
details.howto{margin:14px 0 6px} details.howto summary{color:var(--mut);font-size:13px;cursor:pointer} details.howto p{color:var(--mut);font-size:13px;line-height:1.55;margin:6px 0 0}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0;align-items:center}
.seg{display:inline-flex;border:1px solid var(--line2);border-radius:10px;overflow:hidden;background:var(--card2)} .seg button{background:transparent;border:0;color:var(--txt2);padding:8px 12px;font-size:13.5px;cursor:pointer;min-height:38px} .seg button.on{background:#2C3648;color:#fff}
select,input{background:var(--card2);color:var(--txt);border:1px solid var(--line2);border-radius:10px;padding:8px 10px;font-size:14px;min-height:38px}
#t{min-width:1180px;table-layout:fixed} #t th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);font-weight:500;cursor:pointer;user-select:none}
#t col.c1{width:15%} #t td.co a{color:var(--txt);text-decoration:none;display:flex;flex-direction:column;gap:2px} #t td.co a b{font-size:15px} #t td.co .nm{font-size:13px;color:var(--txt2)} #t td.co .sub{display:block;font-size:11.5px;color:var(--mut);margin-top:3px}
#t td.take{line-height:1.45;font-size:13px} #t td.take .sub{display:block;font-size:11.5px;color:var(--mut);margin-top:4px} #t td.take>span{display:block}
.sub{color:var(--mut);font-size:12px}
.tbadge{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:8px;color:#0C0E12;font-family:var(--mono);font-size:15px;font-weight:600} .tbadge.stale{background:#4b5563;opacity:.75;color:#fff}
.band{display:inline-flex;align-items:center;gap:3px;font-family:var(--mono);font-size:11px;color:var(--mut)} .band i{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:5px;color:#0C0E12;font-style:normal;font-weight:600}
.bdg{display:inline-block;border-radius:6px;padding:1px 7px;font-size:12px;margin:0 4px 4px 0;border:1px solid} .bdg.p2{background:#0b3b52;color:#7dd3fc;border-color:#155e75} .bdg.ov{background:#3a2b0b;color:#fbbf24;border-color:#8a6d1f} .bdg.to{background:#2e1065;color:#c4b5fd;border-color:#6d28d9} .bdg.mf{background:#2a2f3a;color:#c3c9d4;border-color:#3a4252}
.more{color:var(--acc);text-decoration:none}
details.stalebox{margin:18px 0 6px;border:1px dashed #4b5563;border-radius:10px;padding:10px 12px;background:var(--card)} details.stalebox summary{color:#fbbf24;font-size:14px;font-weight:600;cursor:pointer}
/* ---- company page ---- */
.page{display:none;max-width:860px;margin:0 auto} .page.open{display:block} body.standalone .page{display:block}
.dnav{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px} .back{color:var(--acc);text-decoration:none;font-size:14px;font-weight:500;min-height:44px;display:inline-flex;align-items:center} .navr{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.hero{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:22px 20px;display:flex;flex-direction:column;gap:18px}
.hrow{display:flex;align-items:center;gap:14px} .ttile{display:inline-flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:13px;color:#0C0E12;font-family:var(--mono);font-size:24px;font-weight:600;flex:0 0 auto}
.hname{min-width:0} .hline{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap} .htick{font-family:var(--mono);font-size:28px;font-weight:600;line-height:1.1} .hco{font-size:18px;font-weight:500}
.hstats{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:14px 22px} .hstat{display:flex;flex-direction:column;gap:5px;min-width:0} .hstat .v{font-size:24px;font-weight:500;white-space:nowrap} .hstat.big .v{font-size:50px;line-height:1;letter-spacing:-.02em} .hstat .v small{font-size:14px;font-weight:500} .hstat .tsub{white-space:normal}
@media (max-width:900px){.hstats{grid-template-columns:1fr 1fr}.hstat.big{grid-column:1/-1}}
.take{margin:0;padding-top:18px;border-top:1px solid var(--line);font-size:16px;line-height:1.6;color:var(--txt2)}
.pcsec{margin:14px 0} .pc{padding:14px 12px 12px}
.pcbar{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:6px} .ranges{display:inline-flex;gap:4px} .ranges button{background:transparent;border:1px solid transparent;color:var(--mut);padding:6px 9px;border-radius:8px;font-family:var(--mono);font-size:12.5px;cursor:pointer;min-height:34px} .ranges button.on{background:var(--card2);border-color:var(--line2);color:#fff}
.toggles{display:flex;flex-wrap:wrap;gap:10px;font-size:12.5px;color:var(--mut)} .toggles label{display:inline-flex;align-items:center;gap:5px;cursor:pointer} .toggles input{accent-color:#7AA2FF;min-height:0}
.pchart{position:relative;width:100%;height:280px} .pchart svg{width:100%;height:100%;display:block}
.pcfoot{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--mut);margin-top:8px;align-items:center} .legend{display:inline-flex;align-items:center;gap:6px} .legend i{display:inline-block;width:12px;height:12px;border-radius:3px} .legend i.dash{width:14px;height:0;border-top:2px dashed;border-radius:0} .pcret{margin-left:auto;font-family:var(--mono)}
.chart{position:relative;width:100%;min-height:160px;margin:4px 0 8px} .chart svg{width:100%;display:block} .chart .leg{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--mut);margin-top:6px} .chart .leg span{display:inline-flex;align-items:center;gap:6px} .chart .leg i{display:inline-block;width:11px;height:11px;border-radius:3px}
.chart text{font-family:var(--mono);font-size:11px;fill:var(--mut)} .chart .grid{stroke:#232832} .chart .zero{stroke:#3A4252} .pchart text{font-family:var(--mono);font-size:11px;fill:var(--mut)} .pchart .grid{stroke:#232832}
.tabs{display:flex;gap:0;border-bottom:2px solid var(--line);margin:22px 0 6px;overflow-x:auto} .tab{background:transparent;border:0;color:#7FA3FF;font-size:16px;font-weight:500;padding:12px 16px;cursor:pointer;white-space:nowrap;border-bottom:2px solid transparent;margin-bottom:-2px;min-height:44px} .tab.on{color:#fff;background:var(--card2);border-radius:10px 10px 0 0;border-bottom-color:#fff}
.pane{display:none} .pane.on{display:block}
.verdict{border-radius:20px;padding:20px} .vmain{display:flex;flex-wrap:wrap;align-items:flex-end;gap:18px 36px} .vgauge{flex:1 1 240px;display:flex;flex-direction:column;gap:8px} .vgl{font-size:14px;font-weight:500}
.gauge{position:relative;height:10px;border-radius:5px;background:var(--line)} .gfill{position:absolute;left:0;top:0;bottom:0;border-radius:5px} .gtick{position:absolute;top:-5px;width:2px;height:20px;margin-left:-1px;border-radius:1px;background:var(--txt)}
.gscale{position:relative;height:16px;font-family:var(--mono);font-size:12px;color:var(--mut)} .gscale span{position:absolute;top:0} .gmid{transform:translateX(-50%);color:var(--txt);white-space:nowrap}
.p2box{background:#0E1B2E;border:1px solid #274b73;border-radius:16px;padding:14px 18px;margin:14px 0} .p2box p{margin:6px 0 0;line-height:1.55;font-size:14px;color:var(--txt2)}
.baseoe{display:flex;flex-direction:column;gap:8px} .bv{font-size:26px;font-weight:500;line-height:1.1} .bu{font-size:15px;color:var(--mut)}
.scncard{padding:6px 0 0;overflow:hidden} .scn{padding:14px 16px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:10px} .scnh{display:flex;justify-content:space-between;align-items:center;gap:12px} .scnn{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:600} .scnn i{width:10px;height:10px;border-radius:3px;display:inline-block} .scni{font-size:18px;font-weight:500}
.scnbar{position:relative;height:6px;border-radius:3px;background:var(--line)} .scnfill{position:absolute;left:0;top:0;bottom:0;border-radius:3px} .scntick{position:absolute;top:-4px;width:2px;height:14px;margin-left:-1px;border-radius:1px;background:var(--txt)}
.scnsub{display:flex;flex-wrap:wrap;gap:4px 18px;font-size:13px;color:var(--mut)} .scnsub b{font-family:var(--mono);color:var(--txt);font-weight:500}
.scnfoot{padding:14px 16px;background:var(--card2);display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 16px;font-size:14px;font-weight:600} .scnfoot .mono{font-weight:500;color:#D4D8E0}
.moathead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px 16px} .moattitle{display:flex;align-items:center;gap:12px} .moattitle h2{margin:0;font-size:19px} .moatscore{font-size:17px;font-weight:500}
.mdots{display:inline-flex;gap:3px} .mdots i{width:7px;height:7px;border-radius:50%;background:#333A46;display:inline-block} .mdots i.on{background:var(--txt)}
.mcols{display:flex;flex-wrap:wrap;gap:16px 28px;margin-top:16px} .mcol{flex:1 1 260px;display:flex;flex-direction:column;gap:10px} .mk{font-size:11px;letter-spacing:.08em;text-transform:uppercase} .mk.pos{color:var(--pos)} .mk.neg{color:var(--neg)}
.mcol ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px;font-size:14px;line-height:1.5;color:var(--txt2)} .mcol li{display:flex;gap:10px} .sign{font-family:var(--mono)} .sign.pos{color:var(--pos)} .sign.neg{color:var(--neg)}
.dimp{color:var(--txt2);font-size:14.5px;line-height:1.6;margin:14px 0 0}
ul.flags{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px;font-size:13.5px;line-height:1.5;color:var(--txt2)} ul.flags li{display:flex;gap:10px;align-items:flex-start} ul.flags code{font-family:var(--mono);font-size:12px;padding:3px 7px;border-radius:6px;background:var(--card2);border:1px solid var(--line2);color:#D4D8E0;white-space:nowrap;flex:0 0 auto}
.fcount{font-size:15px;font-weight:500;color:var(--mut)} ul.warnlist{margin:6px 0 0;padding-left:18px;color:#fbbf24}
.pnav{display:flex;justify-content:space-between;align-items:center;margin:18px 0;gap:10px} .pn{font-family:var(--mono);text-decoration:none;font-size:14px;color:var(--acc);min-height:44px;display:inline-flex;align-items:center}
.dfoot{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 16px;padding-top:16px;border-top:1px solid var(--line);font-size:13px;color:var(--mut);margin-top:8px}
.pvplot{position:relative;height:128px} .pv-range-lbl{position:absolute;top:0;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);white-space:nowrap} .pv-range-val{position:absolute;top:17px;font-family:var(--mono);font-size:13px;color:var(--acc);white-space:nowrap}
.pv-track{position:absolute;left:0;right:0;top:58px;height:4px;border-radius:2px;background:var(--line)} .pv-band{position:absolute;top:50px;height:20px;border-radius:5px;background:rgba(122,162,255,.18);border:1px solid rgba(122,162,255,.6)} .pv-ivmark{position:absolute;top:44px;width:2px;height:32px;margin-left:-1px;border-radius:1px;background:var(--txt)} .pv-pricedot{position:absolute;top:53px;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:#FF8A8A;box-shadow:0 0 0 4px rgba(255,138,138,.18)}
.pv-ivlbl{position:absolute;top:86px;margin-left:-1px;display:flex;flex-direction:column;gap:2px;white-space:nowrap} .pv-ivlbl span,.pv-pricelbl span{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)} .pv-ivlbl b{font-family:var(--mono);font-size:15px;font-weight:500} .pv-pricelbl{position:absolute;right:0;top:86px;display:flex;flex-direction:column;align-items:flex-end;gap:2px;white-space:nowrap} .pv-pricelbl b{font-family:var(--mono);font-size:15px;font-weight:500;color:#FF8A8A} .pv-axis{display:flex;justify-content:space-between;padding-top:8px;border-top:1px solid var(--line);font-family:var(--mono);font-size:11px;color:var(--mut)}
@media (max-width:760px){
 body{padding:12px 12px 64px}
 #t{min-width:0;table-layout:auto} #t thead{display:none} #t,#t tbody{display:block}
 #t tr{display:grid;grid-template-columns:1fr 1fr 1fr;column-gap:10px;align-items:start;border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:10px;background:var(--card)}
 #t td{display:block;border-bottom:none;padding:3px 0;text-align:left!important;white-space:normal!important}
 #t td.co,#t td.take{grid-column:1/-1}
 #t td::before{display:block;font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin-bottom:1px}
 #t td:nth-child(2)::before{content:"Tier"} #t td:nth-child(3)::before{content:"Band"} #t td:nth-child(4)::before{content:"Wtd IRR"} #t td:nth-child(5)::before{content:"Price"} #t td:nth-child(6)::before{content:"IV @15%"} #t td:nth-child(7)::before{content:"Upside"} #t td:nth-child(8)::before{content:"Moat"} #t td:nth-child(9)::before{content:"Conf."} #t td:nth-child(10)::before{content:"Mkt cap"} #t td:nth-child(11)::before{content:"1y price"}
 .hstat.big .v{font-size:40px} .htick{font-size:24px} .tab{font-size:15px;padding:12px 12px}
 .pchart{height:240px}
}
"""

JS = r"""
(function(){
const $=(s,r)=>(r||document).querySelector(s), $$=(s,r)=>Array.from((r||document).querySelectorAll(s));
const setHash=h=>{try{if(history.replaceState)history.replaceState(null,'',h)}catch(e){}};
function fmtBig(v){const a=Math.abs(v),s=v<0?'-':'';if(a>=1e12)return s+'$'+(a/1e12).toFixed(2)+'T';if(a>=1e9)return s+'$'+(a/1e9).toFixed(a>=1e10?0:1)+'B';if(a>=1e6)return s+'$'+(a/1e6).toFixed(0)+'M';if(a>=1e3)return s+'$'+(a/1e3).toFixed(0)+'K';return s+'$'+a.toFixed(2)}
const FMT={big:fmtBig,pct:v=>(v*100).toFixed(Math.abs(v)>=0.995?0:1)+'%',money:v=>'$'+(Math.abs(v)>=100?v.toFixed(0):Math.abs(v)>=10?v.toFixed(1):v.toFixed(2)),num:v=>v.toLocaleString()};
const axisFmt=(fmt,step)=>fmt===FMT.money?(v=>'$'+(step>=1?v.toFixed(0):step>=0.1?v.toFixed(1):v.toFixed(2))):fmt;
function nice(lo,hi,n){if(hi===lo){hi=lo+1}const raw=(hi-lo)/n,mag=Math.pow(10,Math.floor(Math.log10(raw))),norm=raw/mag,step=(norm<1.5?1:norm<3?2:norm<7?5:10)*mag;return{lo:Math.floor(lo/step)*step,hi:Math.ceil(hi/step)*step,step}}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
/* ---- generic category chart (bars / lines / areas) ---- */
function drawChart(el){
 let spec;try{spec=JSON.parse(el.dataset.chart)}catch(e){return}
 const W=Math.max(el.clientWidth||600,280),H=spec.height||230,L=W<480?46:60,R=12,T=12,B=28,fmt=FMT[spec.yfmt||'big'];
 const vals=[];spec.series.forEach(s=>s.values.forEach(v=>{if(typeof v==='number')vals.push(v)}));
 if(!vals.length){el.innerHTML='<p class="note">No data.</p>';return}
 let lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals);if(spec.zero!==false){lo=Math.min(lo,0);hi=Math.max(hi,0)}
 const ax=nice(lo,hi,4),Y=v=>T+(H-T-B)*(1-(v-ax.lo)/(ax.hi-ax.lo)),n=spec.labels.length,slot=(W-L-R)/Math.max(n,1),X=i=>L+slot*(i+0.5),afmt=axisFmt(fmt,ax.step);
 let s='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'">';
 for(let v=ax.lo;v<=ax.hi+ax.step/1e6;v+=ax.step){const y=Y(v);s+='<line class="'+(Math.abs(v)<ax.step/1e6?'zero':'grid')+'" x1="'+L+'" x2="'+(W-R)+'" y1="'+y.toFixed(1)+'" y2="'+y.toFixed(1)+'"/><text x="'+(L-6)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end">'+afmt(v)+'</text>'}
 const bars=spec.series.filter(x=>x.kind==='bar'),nb=bars.length,bw=slot*0.72/Math.max(nb,1);
 bars.forEach((sr,bi)=>sr.values.forEach((v,i)=>{if(typeof v!=='number')return;const x=X(i)-slot*0.36+bi*bw,y0=Y(0),y1=Y(v);s+='<rect x="'+x.toFixed(1)+'" y="'+Math.min(y0,y1).toFixed(1)+'" width="'+(bw*0.88).toFixed(1)+'" height="'+Math.max(1,Math.abs(y0-y1)).toFixed(1)+'" rx="2" fill="'+sr.color+'" opacity=".9"><title>'+esc(spec.labels[i])+' · '+esc(sr.name)+': '+fmt(v)+'</title></rect>'}));
 spec.series.filter(x=>x.kind!=='bar').forEach(sr=>{let d='',seg=[];const pts=[];sr.values.forEach((v,i)=>{if(typeof v!=='number'){if(seg.length){d+=seg;seg=[]}return}const x=X(i),y=Y(v);pts.push([x,y,v,i]);seg+=(seg?' L':'M')+x.toFixed(1)+','+y.toFixed(1)});if(seg)d+=seg;
  if(sr.kind==='area'&&pts.length){s+='<path d="'+d+' L'+pts[pts.length-1][0].toFixed(1)+','+Y(Math.max(ax.lo,0)).toFixed(1)+' L'+pts[0][0].toFixed(1)+','+Y(Math.max(ax.lo,0)).toFixed(1)+'Z" fill="'+sr.color+'" opacity=".15"/>'}
  s+='<path d="'+d+'" fill="none" stroke="'+sr.color+'" stroke-width="'+(sr.width||2)+'" stroke-linejoin="round" stroke-linecap="round"'+(sr.dash?' stroke-dasharray="5 4"':'')+'/>';
  pts.forEach(p=>{s+='<circle cx="'+p[0].toFixed(1)+'" cy="'+p[1].toFixed(1)+'" r="'+(n>20?2:3)+'" fill="'+sr.color+'"><title>'+esc(spec.labels[p[3]])+' · '+esc(sr.name)+': '+fmt(p[2])+'</title></circle>'})});
 const every=Math.ceil(n/Math.max(3,Math.floor((W-L-R)/58)));spec.labels.forEach((lb,i)=>{if(i%every!==0&&i!==n-1)return;s+='<text x="'+X(i).toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle">'+esc(lb)+'</text>'});
 s+='</svg>';
 el.innerHTML=s+'<div class="leg">'+spec.series.map(x=>'<span><i style="background:'+x.color+'"></i>'+esc(x.name)+'</span>').join('')+(spec.xlabel?'<span style="margin-left:auto">'+esc(spec.xlabel)+'</span>':'')+'</div>';
}
/* ---- price vs value chart ---- */
function drawPrice(el){
 let d;try{d=JSON.parse(el.dataset.px)}catch(e){return}
 const card=el.closest('.pc'),range=(card.dataset.range||'5Y'),showIv=!$('.tg-iv',card)||$('.tg-iv',card).checked,showBand=!$('.tg-band',card)||$('.tg-band',card).checked,showH=$('.tg-h',card)&&$('.tg-h',card).checked;
 let pts=range==='1Y'&&d.d&&d.d.length>30?d.d:d.w;if(!pts||pts.length<2){el.innerHTML='<p class="note">No price history.</p>';return}
 const last=new Date(pts[pts.length-1][0]);const yrs={'1Y':1,'3Y':3,'5Y':5,'10Y':10,'MAX':200}[range]||5;const cut=new Date(last);cut.setFullYear(cut.getFullYear()-yrs);
 pts=pts.filter(p=>new Date(p[0])>=cut);if(pts.length<2){pts=d.w.slice(-2)}
 const W=Math.max(el.clientWidth||600,280),H=el.clientHeight||260,L=W<480?44:56,R=58,T=14,B=26;
 const closes=pts.map(p=>p[1]);let lo=Math.min.apply(null,closes),hi=Math.max.apply(null,closes);
 const over=[];if(showIv&&d.iv15)over.push(d.iv15);if(showBand&&d.lo&&d.hi){over.push(d.lo,d.hi)}if(showH){if(d.h20)over.push(d.h20);if(d.h25)over.push(d.h25)}
 const cap=hi*3;over.forEach(v=>{if(v<=cap){lo=Math.min(lo,v);hi=Math.max(hi,v)}});lo=Math.max(0,lo-(hi-lo)*0.06);hi=hi+(hi-lo)*0.06;
 const ax=nice(lo,hi,4),Y=v=>T+(H-T-B)*(1-(v-ax.lo)/(ax.hi-ax.lo)),t0=new Date(pts[0][0]).getTime(),t1=last.getTime(),X=t=>L+(W-L-R)*((t-t0)/Math.max(1,(t1-t0)));
 let s='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'">';
 const afmt=axisFmt(FMT.money,ax.step);
 for(let v=ax.lo;v<=ax.hi+ax.step/1e6;v+=ax.step){const y=Y(v);if(y<T-1||y>H-B+1)continue;s+='<line class="grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+y.toFixed(1)+'" y2="'+y.toFixed(1)+'"/><text x="'+(L-6)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end">'+afmt(v)+'</text>'}
 if(showBand&&d.lo&&d.hi){const y1=Y(Math.min(d.hi,ax.hi)),y2=Y(Math.max(d.lo,ax.lo));s+='<rect x="'+L+'" y="'+Math.min(y1,y2).toFixed(1)+'" width="'+(W-L-R)+'" height="'+Math.abs(y2-y1).toFixed(1)+'" fill="rgba(122,162,255,.14)" stroke="rgba(122,162,255,.45)"><title>Scenario range at 15%: '+FMT.money(d.lo)+' – '+FMT.money(d.hi)+'</title></rect>'}
 let path='',area='';pts.forEach((p,i)=>{const x=X(new Date(p[0]).getTime()),y=Y(p[1]);path+=(i?' L':'M')+x.toFixed(1)+','+y.toFixed(1)});
 area=path+' L'+X(t1).toFixed(1)+','+Y(ax.lo).toFixed(1)+' L'+X(t0).toFixed(1)+','+Y(ax.lo).toFixed(1)+'Z';
 const up=closes[closes.length-1]>=closes[0],col=up?'#5BD69C':'#FF8A8A';
 s+='<path d="'+area+'" fill="'+col+'" opacity=".12"/><path d="'+path+'" fill="none" stroke="'+col+'" stroke-width="1.8" stroke-linejoin="round"/>';
 const line=(v,label,color,dash)=>{if(!v||v>ax.hi||v<ax.lo)return;const y=Y(v);s+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y.toFixed(1)+'" y2="'+y.toFixed(1)+'" stroke="'+color+'" stroke-width="1.5" stroke-dasharray="'+dash+'"/><rect x="'+(W-R+3)+'" y="'+(y-9).toFixed(1)+'" width="'+(R-5)+'" height="18" rx="4" fill="'+color+'"/><text x="'+(W-R+(R-5)/2+3)+'" y="'+(y+4).toFixed(1)+'" text-anchor="middle" style="fill:#0C0E12;font-weight:600">'+label+'</text>'};
 if(showH){line(d.h20,'20%','#B79CFF','2 3');line(d.h25,'25%','#B79CFF','2 3')}
 if(showIv&&d.iv15)line(d.iv15,'IV','#C9D4FF','6 4');
 const lastC=closes[closes.length-1],yl=Y(lastC);s+='<circle cx="'+X(t1).toFixed(1)+'" cy="'+yl.toFixed(1)+'" r="4" fill="'+col+'"/><rect x="'+(W-R+3)+'" y="'+(yl-9).toFixed(1)+'" width="'+(R-5)+'" height="18" rx="4" fill="'+col+'"/><text x="'+(W-R+(R-5)/2+3)+'" y="'+(yl+4).toFixed(1)+'" text-anchor="middle" style="fill:#0C0E12;font-weight:600">'+(lastC>=1000?lastC.toFixed(0):lastC.toFixed(lastC>=100?1:2))+'</text>';
 if(d.iv15&&(d.iv15>ax.hi)){s+='<text x="'+(L+6)+'" y="'+(T+12)+'" style="fill:#C9D4FF">▲ IV@15% '+FMT.money(d.iv15)+' above chart</text>'}
 const years=new Set();pts.forEach(p=>years.add(p[0].slice(0,4)));const ys=Array.from(years),everyY=Math.ceil(ys.length/Math.max(2,Math.floor((W-L-R)/70)));
 ys.forEach((y,i)=>{if(i%everyY)return;const first=pts.find(p=>p[0].slice(0,4)===y);if(!first)return;const x=X(new Date(first[0]).getTime());if(x<L+10)return;s+='<text x="'+x.toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle">'+(range==='1Y'?first[0].slice(0,7):y)+'</text>'});
 if(range==='1Y'){const ms=new Set();pts.forEach(p=>ms.add(p[0].slice(0,7)));const arr=Array.from(ms);const ev=Math.ceil(arr.length/Math.max(3,Math.floor((W-L-R)/60)));s=s.replace(/<text x="[^"]+" y="\d+" text-anchor="middle">\d{4}-\d{2}<\/text>/g,'');arr.forEach((m,i)=>{if(i%ev)return;const first=pts.find(p=>p[0].slice(0,7)===m);const x=X(new Date(first[0]).getTime());s+='<text x="'+x.toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle">'+m.slice(2)+'</text>'})}
 s+='</svg>';el.innerHTML=s;
 const ret=$('.pcret',card);if(ret){const r=(lastC/closes[0]-1)*100;ret.textContent=range+': '+(r>=0?'+':'')+r.toFixed(0)+'% ('+pts[0][0]+' → '+pts[pts.length-1][0]+')';ret.className='pcret '+(r>=0?'pos':'neg')}
}
function drawVisible(root){$$('.chart',root).forEach(el=>{if(el.offsetParent!==null)drawChart(el)});$$('.pchart',root).forEach(el=>{if(el.offsetParent!==null)drawPrice(el)})}
/* ---- tabs ---- */
document.addEventListener('click',e=>{
 const tb=e.target.closest('.tab');if(tb){const page=tb.closest('.page');$$('.tab',page).forEach(x=>x.classList.toggle('on',x===tb));$$('.pane',page).forEach(p=>p.classList.toggle('on',p.dataset.pane===tb.dataset.tab));drawVisible(page);{const t=page.dataset.ticker;setHash(document.body.classList.contains('standalone')?'#'+tb.dataset.tab:'#'+t+'/'+tb.dataset.tab)}return}
 const rb=e.target.closest('.ranges button');if(rb){const card=rb.closest('.pc');$$('.ranges button',card).forEach(x=>x.classList.toggle('on',x===rb));card.dataset.range=rb.dataset.r;drawPrice($('.pchart',card));return}
});
document.addEventListener('change',e=>{if(e.target.matches('.toggles input')){const card=e.target.closest('.pc');drawPrice($('.pchart',card))}});
/* ---- list: filter / sort / detail ---- */
let tier='all',fit='modeled';const q=$('#q');
window.apply=function(){const tb=$('#t tbody');if(!tb)return;let n=0;const key=($('#sort')||{}).value||'irr';const rows=$$('tr',tb);rows.sort((a,b)=>parseFloat(b.dataset[key]||-9)-parseFloat(a.dataset[key]||-9));rows.forEach(tr=>{tb.appendChild(tr);const okT=tier==='all'||tr.dataset.tier===tier,okF=fit==='all'||tr.dataset.fit===fit,okQ=!q||!q.value||tr.dataset.search.includes(q.value.toLowerCase());tr.style.display=(okT&&okF&&okQ)?'':'none';if(okT&&okF&&okQ)n++});const c=$('#count');if(c)c.textContent=n+' shown'};
$$('#tierseg button').forEach(b=>b.onclick=()=>{tier=b.dataset.f;$$('#tierseg button').forEach(x=>x.classList.toggle('on',x===b));apply()});
$$('#fitseg button').forEach(b=>b.onclick=()=>{fit=b.dataset.fit;$$('#fitseg button').forEach(x=>x.classList.toggle('on',x===b));apply()});
if(q)q.oninput=apply;const so=$('#sort');if(so)so.onchange=apply;
window.showDetail=function(id,tab){const lv=$('#listView');const el=document.getElementById('d-'+id);if(!el)return true;if(lv)lv.style.display='none';$$('.page').forEach(p=>p.classList.remove('open'));el.classList.add('open');if(tab){const b=$('.tab[data-tab="'+tab+'"]',el);if(b)b.click()}window.scrollTo(0,0);drawVisible(el);setHash('#'+id+(tab?'/'+tab:''));return false};
window.backToList=function(){$$('.page').forEach(p=>p.classList.remove('open'));const lv=$('#listView');if(lv)lv.style.display='';window.scrollTo(0,0);setHash('#');return false};
function route(){const h=location.hash.replace(/^#/,'');if(document.body.classList.contains('standalone')){const b=h&&$('.tab[data-tab="'+h+'"]');if(b)b.click();drawVisible(document);return}if(!h){backToList();return}const [id,tab]=h.split('/');if(document.getElementById('d-'+id))showDetail(id,tab)}
window.addEventListener('hashchange',route);
let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>drawVisible(document),150)});
apply();route();
})();
"""

FONTS = '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">'


def document(title, body, standalone=False):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title, quote=False)}</title>'
            f'{FONTS}<style>{CSS}</style></head><body class="{"standalone" if standalone else ""}">{body}<script>{JS}</script></body></html>')


# ---------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    only = None
    if "--only" in args:
        only = set(x.strip().upper() for x in args[args.index("--only") + 1].split(","))
    max_embed = int(args[args.index("--max-embed") + 1]) if "--max-embed" in args else 250
    split = "--no-split" not in args
    os.makedirs(OUT, exist_ok=True)
    current, stale = load_all(only)
    registry = {}
    for e in (jload(f"{BASE}/_system/overrides_registry.json") or {}).get("entries", []):
        registry.setdefault(e.get("ticker"), []).append(e)
    try:
        qd = jload(f"{BASE}/_system/queue.json") or {}
        total, done = qd.get("universe_size", 0), sum(1 for e in qd.get("queue", []) if e.get("status") == "done")
    except Exception:
        total, done = 0, 0
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    order = [safe_id(c["score"].get("ticker")) for c in current]
    embedded, pages = [], []
    for i, c in enumerate(current):
        prev_t = order[i - 1] if i > 0 else None
        next_t = order[i + 1] if i + 1 < len(order) else None
        page_embedded = company_page(c, registry, standalone=False, prev_next=(prev_t, next_t))
        if i < max_embed:
            pages.append(page_embedded); embedded.append(order[i])
        if split:
            os.makedirs(f"{OUT}/companies", exist_ok=True)
            st = company_page(c, registry, standalone=True, prev_next=(prev_t, next_t))
            with open(f"{OUT}/companies/{order[i]}.html", "w", encoding="utf-8") as f:
                f.write(document(f"{c['score'].get('ticker')} — {c['score'].get('name')} · DCF", st, standalone=True))
    body = list_page(current, stale, set(embedded), today, (done, total)) + "".join(pages)
    doc = document("Owner's-Earnings DCF Ranking", body)
    if not only:
        with open(f"{OUT}/ranking-{today}.html", "w", encoding="utf-8") as f:
            f.write(doc)
        with open(f"{OUT}/latest.html", "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"wrote {OUT}/ranking-{today}.html ({len(doc)/1e6:.1f} MB) with {len(current)} companies ({len(embedded)} embedded, {len(stale)} stale); progress {done}/{total}"
              + (f"; {len(current)} standalone pages in {OUT}/companies/" if split else ""))
    else:
        with open(f"{OUT}/preview-{'-'.join(sorted(only))}.html", "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"wrote {OUT}/preview-{'-'.join(sorted(only))}.html")


if __name__ == "__main__":
    main()
