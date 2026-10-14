#!/usr/bin/env python3
"""Aggregate every ~/workspace/stocks/<TICKER>/score.json into one self-contained,
filterable HTML ranking. Run daily by cron; also runnable by hand.
Output: ~/workspace/stocks/_daily/ranking-YYYY-MM-DD.html  (+ latest.html)
"""
import json, os, glob, datetime, html, csv, re
from zoneinfo import ZoneInfo

BASE = "/home/hatch/workspace/stocks"
OUT = f"{BASE}/_daily"

def is_current(numbers):
    """A score presents as current only when its engine output is v5+: the
    DATA GATE exists. Pre-v5 dcf_numbers.json (engine_version < 5 or no
    data_gap field) means the score predates the gate — round-2 audit found
    the ranking mixing engines, with v4 Tier B names (HIG/PRU/PCG) sitting
    unmarked next to v5 rows."""
    ev = (numbers or {}).get("engine_version")
    return isinstance(ev, (int, float)) and not isinstance(ev, bool) and ev >= 5 and "data_gap" in numbers

def load_scores():
    scores, stale = [], []
    for p in glob.glob(f"{BASE}/*/score.json"):
        try:
            s = json.load(open(p))
            folder = os.path.dirname(p)
            s["_folder"] = os.path.basename(folder)
            try:
                s["_numbers"] = json.load(open(f"{folder}/dcf_numbers.json"))
            except Exception:
                s["_numbers"] = {}
            # A score superseded by a v5 DATA_GAP block (its engine rerun found
            # uncovered gaps after the score was written) must not render as live.
            if s["_numbers"].get("data_gap_uncovered"):
                continue
            if not is_current(s["_numbers"]):
                stale.append(s)
                continue
            try:
                with open(f"{folder}/financials_history.csv") as f:
                    s["_history"] = list(csv.DictReader(f))
            except Exception:
                s["_history"] = []
            s["_has_second_pass_md"] = os.path.exists(f"{folder}/second_pass.md")
            scores.append(s)
        except Exception:
            pass
    key = lambda s: (s.get("implied_irr") if s.get("implied_irr") is not None else -9)
    scores.sort(key=key, reverse=True)
    stale.sort(key=key, reverse=True)
    return scores, stale

def fmt_pct(x, dec=1):
    return f"{x*100:.{dec}f}%" if isinstance(x, (int, float)) else "—"

def fmt_big(v):
    try:
        v = float(v)
    except Exception:
        return "—"
    if abs(v) >= 1e9:
        return f"${v/1e9:,.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:,.0f}M"
    return f"${v:,.0f}"

def safe_id(ticker):
    return re.sub(r"[^A-Za-z0-9_-]", "-", str(ticker))

def build_detail(s, tier_color):
    t = html.escape(str(s.get("ticker", "")))
    sid = safe_id(s.get("ticker", ""))
    tier = s.get("tier_final") or s.get("tier_by_numbers") or "?"
    n = s.get("_numbers") or {}
    diag = n.get("diagnostics") or {}
    sp = s.get("second_pass") or {}
    accent = {"S": "#B79CFF", "A": "#4ADE80", "B": "#5BD69C", "C": "#F2B84B", "D": "#F08A4B", "F": "#9AA3B2"}.get(tier, "#9AA3B2")
    irr = s.get("implied_irr")
    price = s.get("price")
    w_iv = s.get("iv_at_15")
    # ---- hurdle gauge (0..scale, hurdle tick at 15) ----
    scale = 30.0
    if isinstance(irr, (int, float)) and irr * 100 > 30:
        scale = float(int(irr * 100 // 10 + 1) * 10)
    if isinstance(irr, (int, float)):
        fill = max(0.0, min(100.0, irr * 100 / scale * 100))
        diff = irr * 100 - 15
        gauge_lbl = f"{abs(diff):.1f} pts {'above' if diff >= 0 else 'below'} the hurdle"
        irr_big = f"{irr*100:.1f}%"
    else:
        fill, gauge_lbl, irr_big = 0.0, "No positive owner's earnings", "—"
    hurdle_left = 15 / scale * 100
    chips = [f"Tier {tier}" + (f" · {html.escape(str(s.get('tier_meaning','')))}" if s.get("tier_meaning") else "")]
    if s.get("moat_score") is not None:
        chips.append(f"Moat {s.get('moat_score')}/10")
    if s.get("cap_years") is not None:
        chips.append(f"Advantage period {s.get('cap_years')} yrs")
    if s.get("confidence"):
        chips.append(f"Confidence {html.escape(str(s['confidence']))}")
    for o in s.get("overrides") or []:
        if isinstance(o, dict) and o.get("field"):
            kind_lbl = "AI estimate" if o.get("kind") == "estimate" else "filing override"
            chips.append(f"{html.escape(str(o['field']))}: {kind_lbl}")
    if s.get("tier_by_numbers") and tier != s.get("tier_by_numbers"):
        chips.append(f"Tier overridden {html.escape(str(s['tier_by_numbers']))}→{html.escape(str(tier))} (agent judgment — see registry)")
    chips_html = "".join(f'<span class="dchip">{c}</span>' for c in chips)
    # ---- pass 2 banner ----
    p2_html = ""
    if sp.get("verdict") == "changed":
        prior_irr = sp.get("prior_weighted_irr")
        p2_html = (f'<div class="p2box"><span class="p2chg">↺ Revised by pass 2 · {html.escape(str(sp.get("date", "")))}</span>'
                   f'<p>Tier {html.escape(str(sp.get("prior_tier", "?")))} → {html.escape(str(tier))} · Wtd IRR {fmt_pct(prior_irr)} → {fmt_pct(irr)} · IV@15% {fmt_money(sp.get("prior_iv_at_15"))} → {fmt_money(w_iv)}</p>'
                   f'<p>{html.escape(str(sp.get("summary", "")))}</p></div>')
    nav_right = (f"Pass 2 revised · {html.escape(str(sp.get('date','')))}" if sp.get("verdict") == "changed"
                 else f"Pass 1 · {html.escape(str(s.get('analysis_date', '')))}")
    # ---- price vs value number line ----
    scn = (n.get("scenarios") or {})
    pv_html = ""
    ivs = [r.get("iv_at_15") for r in scn.values() if isinstance(r.get("iv_at_15"), (int, float))]
    if ivs and isinstance(price, (int, float)) and isinstance(w_iv, (int, float)) and w_iv > 0:
        lo, hi = min(ivs), max(ivs)
        top = max(price, hi)
        axis_max = next((c for c in (10, 20, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000) if c > top * 1.04), top * 1.1)
        X = lambda v: v / axis_max * 100
        ticks = "".join(f"<span>${int(axis_max * i / 5):,}</span>" for i in range(6))
        mult_w = f"{price / w_iv:.1f}×" if w_iv else "—"
        mult_hi = f"{price / hi:.1f}×" if hi else "—"
        pv_html = f"""<section class="dsec"><h2 class="dh2">Price vs. value</h2>
<p class="dnote">Every scenario's value at a 15% discount rate, against today's price.</p>
<div class="dcard pv">
<div class="pvplot">
<span class="pv-range-lbl" style="left:{X(lo):.2f}%">Scenario range</span>
<span class="pv-range-val" style="left:{X(lo):.2f}%">{fmt_money(lo)} – {fmt_money(hi)}</span>
<div class="pv-track"></div>
<div class="pv-band" style="left:{X(lo):.2f}%;width:{max(0.5, X(hi) - X(lo)):.2f}%"></div>
<div class="pv-ivmark" style="left:{X(w_iv):.2f}%"></div>
<div class="pv-pricedot" style="left:{X(price):.2f}%"></div>
<div class="pv-ivlbl" style="left:{X(w_iv):.2f}%"><span>Weighted IV</span><b>{fmt_money(w_iv)}</b></div>
<div class="pv-pricelbl"><span>Price</span><b>{fmt_money(price)}</b></div>
</div>
<div class="pv-axis">{ticks}</div>
</div>
<p class="dnote">Today's price is {mult_w} the weighted value and {mult_hi} the super-bull case. At a 12% discount rate, value is {fmt_money(s.get('iv_at_12'))}.</p></section>"""
    # ---- key numbers ----
    def tile(k, v, cls=""):
        return f'<div class="dtile"><span class="dk">{k}</span><span class="dv {cls}">{v}</span></div>'
    up = s.get("upside_at_15_pct")
    tiles = "".join([
        tile("Price", fmt_money(price)),
        tile("IV @15%", fmt_money(w_iv)),
        tile("IV @12%", fmt_money(s.get("iv_at_12"))),
        tile("Upside @15%", f"{up:+.0f}%" if isinstance(up, (int, float)) else "—", "neg" if isinstance(up, (int, float)) and up < 0 else "pos"),
        tile("Base-case IRR", fmt_pct(s.get("implied_irr_base_case"))),
        tile("OE yield", fmt_pct(diag.get("oe_yield")) if diag.get("oe_yield") is not None else "—"),
        tile("Terminal value share", fmt_pct(diag.get("tv_share_at_15")) if diag.get("tv_share_at_15") is not None else "—"),
        tile("Scenario spread", f"{diag['scenario_spread_iv15']:.1f}×" if isinstance(diag.get("scenario_spread_iv15"), (int, float)) else "—"),
    ])
    base_note = html.escape(str(s.get("base_source", "")))
    kn_html = f"""<section class="dsec"><h2 class="dh2">Key numbers</h2>
<div class="dtiles">{tiles}</div>
<div class="dcard baseoe"><span class="dk">Base owner's earnings</span>
<span class="baseoe-v">{("$" + format(s["base_oe_per_share"], ",.2f")) if isinstance(s.get("base_oe_per_share"), (int, float)) else "—"}<span class="baseoe-u"> / share</span></span>
<p class="dnote">Source: {base_note}. Market cap {fmt_cap(s.get("market_cap_b"))}.</p></div></section>"""
    # ---- overrides (judgment.json decisions applied by the engine) ----
    ov_applied = n.get("overrides_applied") or []
    if not ov_applied and s.get("overrides"):
        ov_applied = [{"field": o.get("field"), "value": o.get("value"), "kind": o.get("kind"),
                       "source": o.get("source"), "reason": "", "periods_filled": []}
                      for o in s["overrides"] if isinstance(o, dict)]
    ov_html = ""
    if ov_applied:
        ov_rows = ""
        for o in ov_applied:
            v = o.get("value")
            fv = fmt_big(v) if o.get("field") in ("capex", "sbc") else (f"{v:,.0f}" if isinstance(v, (int, float)) else "—")
            ov_rows += (f"<tr><td>{html.escape(str(o.get('field', '')))}</td><td class='num'>{fv}</td>"
                        f"<td>{html.escape(str(o.get('kind', '')))}</td><td>{html.escape(str(o.get('source', '')))}</td>"
                        f"<td>{html.escape(', '.join(o.get('periods_filled') or []))}</td></tr>")
        imp = s.get("override_impact") or {}
        imp_html = ""
        if imp:
            basis_lbl = "TTM base" if imp.get("base_used") == "ttm" else "3-year median base"
            pct = imp.get("base_oe_impact_pct")
            pp = imp.get("weighted_irr_impact_pp")
            imp_html = (f"<p class=\"dnote\">Measured impact on the {basis_lbl} actually used (no override → with override): base OE/share "
                        f"{fmt_money(imp.get('base_oe_without_override'))} → {fmt_money(imp.get('base_oe_with_override'))}"
                        + (f" ({pct:+.2f}%)" if isinstance(pct, (int, float)) else "")
                        + f" · weighted IRR {fmt_pct(imp.get('weighted_irr_without_override'))} → {fmt_pct(imp.get('weighted_irr_with_override'))}"
                        + (f" ({pp:+.2f}pp)" if isinstance(pp, (int, float)) else "")
                        + "</p>")
            if imp.get("unblocks_tier"):
                imp_html += ("<p class=\"dnote\"><b>This override is the only reason this company has a tier.</b> "
                             "Without it, the filing gap blocks scoring entirely — the judgment call is the whole verdict.</p>")
        reasons = "".join(f"<p class=\"dnote\"><b>{html.escape(str(o.get('field', '')))}:</b> {html.escape(str(o.get('reason', '')))}</p>"
                          for o in ov_applied if o.get("reason"))
        ov_html = f"""<section class="dsec"><h2 class="dh2">Overrides</h2>
<p class="dnote">Filing gaps filled by a main-agent judgment override — an override never replaces a filed value.</p>
<div class="dcard ovcard"><div class="twrap"><table class="mini"><thead><tr><th>Field</th><th class="num">Value</th><th>Kind</th><th>Source</th><th>Periods filled</th></tr></thead><tbody>{ov_rows}</tbody></table></div>
{imp_html}{reasons}</div></section>"""
    # ---- scenarios ----
    order = [("super_bear", "Super bear"), ("bear", "Bear"), ("base", "Base"), ("bull", "Bull"), ("super_bull", "Super bull")]
    dot_colors = ["#3A4252", "#55617A", "#7484A0", "#97A6C2", "#BFCBE0"]
    sc_rows = ""
    sc_src = scn if scn else (s.get("scenarios") or {})
    for i, (k, lbl) in enumerate(order):
        r = sc_src.get(k) or {}
        r_irr = r.get("irr")
        w = max(0.0, min(100.0, r_irr * 100 / scale * 100)) if isinstance(r_irr, (int, float)) else 0
        prob = f"{round(r['prob']*100)}%" if isinstance(r.get("prob"), (int, float)) else "—"
        g = fmt_pct(r.get("g_start")) if r.get("g_start") is not None else "—"
        mult = f"{r['oe_mult']}×" if r.get("oe_mult") is not None else "—"
        sc_rows += f"""<div class="scnrow">
<div class="scnhead"><span class="scnname"><span class="scndot" style="background:{dot_colors[i]}"></span>{lbl}<span class="prob">{prob}</span></span><span class="scnirr">{fmt_pct(r_irr)}</span></div>
<div class="scnbar"><div class="scnfill" style="width:{w:.1f}%;background:{accent}"></div><div class="scntick" style="left:{hurdle_left:.1f}%"></div></div>
<div class="scnsub"><span>Growth start <b>{g}</b></span><span>OE multiple <b>{mult}</b></span><span>IV @15% <b>{fmt_money(r.get('iv_at_15'))}</b></span></div>
</div>"""
    sc_html = f"""<section class="dsec"><h2 class="dh2">Scenarios</h2>
<p class="dnote">IRR at today's price for each case, against the 15% hurdle.</p>
<div class="dcard scncard">{sc_rows}
<div class="scnfoot"><span>Probability-weighted</span><span>IV {fmt_money(w_iv)} · IRR {irr_big}</span></div></div></section>"""
    # ---- moat ----
    moat = s.get("moat_score")
    dots = ""
    if isinstance(moat, (int, float)):
        dots = '<span class="mdots">' + "".join(f'<span class="mdot {"on" if i < round(moat) else ""}"></span>' for i in range(10)) + "</span>"
    mfor, magainst = s.get("moat_for"), s.get("moat_against")
    if isinstance(mfor, list) and isinstance(magainst, list) and mfor:
        cols = ('<div class="mcols"><div class="mcol"><span class="mk pos">Strengths</span><ul>'
                + "".join(f'<li><span class="sign pos">+</span><span>{html.escape(str(x))}</span></li>' for x in mfor)
                + '</ul></div><div class="mcol"><span class="mk neg">Pressures</span><ul>'
                + "".join(f'<li><span class="sign neg">−</span><span>{html.escape(str(x))}</span></li>' for x in magainst)
                + "</ul></div></div>")
    else:
        cols = f'<p class="dimp">{html.escape(str(s.get("moat_justification", "")))}</p>'
    moat_html = f"""<section class="dsec"><div class="dcard moatcard">
<div class="moathead"><span class="moattitle"><h2 class="dh2">Moat</h2><span class="moatscore">{moat if moat is not None else "—"}/10</span>{dots}</span>
<span class="dnote">Competitive advantage period <b class="mono">{s.get("cap_years", "—")} yrs</b></span></div>
{cols}</div></section>"""
    # ---- history chart + table ----
    hist = (s.get("_history") or [])
    def fnum(v):
        try:
            return float(v)
        except Exception:
            return None
    chart_html, hist_rows = "", ""
    if hist:
        last6 = hist[-6:]
        vals = [abs(fnum(r.get("oe_conservative")) or 0) for r in last6] + [abs(fnum(r.get("oe_maintenance")) or 0) for r in last6]
        mx = max(vals) if vals and max(vals) > 0 else 1
        bars = ""
        for r in last6:
            pair = ""
            for key, cls in (("oe_conservative", "cons"), ("oe_maintenance", "maint")):
                v = fnum(r.get(key))
                if v is None:
                    pair += f'<div class="hbar {cls} pos" style="top:79px;height:2px"></div>'
                    continue
                h = max(2.0, abs(v) / mx * 72)
                if v >= 0:
                    pair += f'<div class="hbar {cls}" style="top:{80 - h:.0f}px;height:{h:.0f}px"></div>'
                else:
                    pair += f'<div class="hbar {cls}" style="top:80px;height:{h:.0f}px"></div>'
            lbl = ""
            lv = fnum(last6[-1].get("oe_maintenance")) if r is last6[-1] else None
            if r is last6[-1] and lv is not None:
                lbl = f'<span class="hlbl">{lv/1e9:+.2f}</span>'
            bars += f'<div class="hcol">{pair}{lbl}</div>'
        years = "".join(f"<span>{html.escape(str(r.get('fy_label', '')))}</span>" for r in last6)
        chart_html = f"""<div class="hlegend"><span><i class="sw cons"></i>OE (cons)</span><span><i class="sw maint"></i>OE (maint)</span><span class="hunit">$B, FY</span></div>
<div class="hchart"><div class="hzero"></div>{bars}</div>
<div class="hyears">{years}</div>"""
        for row in hist[-10:]:
            hist_rows += (f"<tr><td>{html.escape(str(row.get('fy_label', '')))}</td><td class='num'>{fmt_big(row.get('revenue'))}</td>"
                          f"<td class='num'>{fmt_big(row.get('ocf'))}</td><td class='num'>{fmt_big(row.get('capex'))}</td>"
                          f"<td class='num'>{fmt_big(row.get('sbc'))}</td><td class='num'>{fmt_big(row.get('oe_conservative'))}</td>"
                          f"<td class='num'>{fmt_big(row.get('oe_maintenance'))}</td></tr>")
    hist_html = f"""<section class="dsec"><h2 class="dh2">Financial history</h2>
<div class="dcard histcard">{chart_html}
<div class="twrap"><table class="mini"><thead><tr><th>FY</th><th class="num">Revenue</th><th class="num">Op CF</th><th class="num">Capex</th><th class="num">SBC</th><th class="num">OE (cons)</th><th class="num">OE (maint)</th></tr></thead><tbody>{hist_rows if hist_rows else '<tr><td colspan="7">No history available.</td></tr>'}</tbody></table></div></div></section>"""
    # ---- flags ----
    flags = s.get("fragility_flags") or []
    flags_html = ""
    if flags:
        codes = [html.escape(str(f).split(":")[0].strip()) for f in flags]
        chips_f = "".join(f'<span class="fchip">{c}</span>' for c in codes)
        flags_html = f"""<section class="dsec"><h2 class="dh2">⚠ Fragility flags <span class="fcount">{len(flags)}</span></h2>
<div class="fchips">{chips_f}</div>
<p class="dnote">Each flag is resolved in the write-up (stocks/{html.escape(s.get('_folder', ''))}/analysis.md).</p></section>"""
    files_note = f"stocks/{html.escape(s.get('_folder', ''))}/analysis.md" + (" · second_pass.md" if s.get("_has_second_pass_md") else "")
    return f"""<div class="detail" id="d-{sid}">
<nav class="dnav"><a class="dback" href="#" onclick="return backToList()">← Ranking</a><span class="dnavr">{nav_right}</span></nav>
<section class="dcard verdict">
<div class="vhead"><span class="vtile" style="background:{accent}">{html.escape(str(tier))}</span>
<div class="vtitle"><div class="vname"><span class="vtick">{t}</span><span class="vco">{html.escape(str(s.get('name', '')))}</span></div>
<span class="dnote">{html.escape(str(s.get('sector', '')))} · {fmt_cap(s.get('market_cap_b'))}</span></div></div>
<div class="vmain">
<div class="virr"><span class="dk">Expected return / yr</span><span class="virr-v">{irr_big}</span><span class="dnote">Probability-weighted IRR at {fmt_money(price)}</span></div>
<div class="vgauge"><span class="vgauge-lbl" style="color:{accent}">{gauge_lbl}</span>
<div class="gauge"><div class="gaugefill" style="width:{fill:.1f}%;background:{accent}"></div><div class="gaugetick" style="left:{hurdle_left:.1f}%"></div></div>
<div class="gaugescale"><span style="left:0">0%</span><span class="gs-mid" style="left:{hurdle_left:.1f}%">15% hurdle</span><span style="right:0">{scale:.0f}%</span></div></div>
</div>
<div class="vchips">{chips_html}</div>
<p class="vtake">{html.escape(str(s.get('one_liner', '')))}</p>
</section>
{p2_html}
{pv_html}
{kn_html}
{ov_html}
{sc_html}
{moat_html}
{hist_html}
{flags_html}
<footer class="dfoot"><span>Screening-grade standardized DCF — not a buy or sell call.</span><span class="mono">{files_note}</span></footer>
</div>"""

def fmt_money(v):
    return f"${v:,.2f}" if isinstance(v, (int, float)) else "—"

def fmt_cap(v):
    return f"${v:,.2f}B" if isinstance(v, (int, float)) else "—"

def main():
    os.makedirs(OUT, exist_ok=True)
    scores, stale = load_scores()
    try:
        q = json.load(open(f"{BASE}/_system/queue.json"))
        total, done = q["universe_size"], sum(1 for e in q["queue"] if e["status"] == "done")
    except Exception:
        total, done = 0, 0
    changed_count = sum(1 for s in scores if (s.get("second_pass") or {}).get("verdict") == "changed")
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()  # v5: ET, not the VM's UTC date (audit: ranking-2026-10-14 was written on Oct 13 ET)
    tier_color = {"S": "#7c3aed", "A": "#15803d", "B": "#16a34a", "C": "#d97706", "D": "#b45309", "F": "#6b7280"}
    rows = ""
    details = ""
    for s in scores:
        irr = s.get("implied_irr")
        irr_s = f"{irr*100:.1f}%" if isinstance(irr, (int, float)) else "—"
        up = s.get("upside_at_15_pct")
        up_s = f"{up:+.0f}%" if isinstance(up, (int, float)) else "—"
        up_cls = "pos" if isinstance(up, (int, float)) and up >= 0 else "neg"
        tier = s.get("tier_final") or s.get("tier_by_numbers") or "?"
        moat = s.get("moat_score")
        moat_s = f"{moat}/10" if isinstance(moat, (int, float)) else "—"
        sc = s.get("scenarios") or {}
        fl = s.get("fragility_flags") or []
        fl_s = f"<br><span class=\"sub\">⚠ {len(fl)} fragility flag(s) — see analysis.md</span>" if fl else ""
        sc_s = ""
        if sc:
            order = [("super_bear", "SB"), ("bear", "B"), ("base", "Base"), ("bull", "Bull"), ("super_bull", "SBu")]
            sc_s = "<br><span class=\"sub\">Scenarios: " + " · ".join(f"{lbl} {round(sc[k]['prob']*100)}%" for k, lbl in order if k in sc) + "</span>"
        sp = s.get("second_pass") or {}
        p2_s, p2_attr = "", ""
        if sp.get("verdict") == "changed":
            p2_attr = ' data-p2="changed"'
            prior_irr = sp.get("prior_weighted_irr")
            prior_irr_s = f"{prior_irr*100:.1f}%" if isinstance(prior_irr, (int, float)) else "—"
            p2_s = (f"<span class=\"p2chg\">↺ Pass 2 {html.escape(str(sp.get('date','')))}: Tier {html.escape(str(sp.get('prior_tier','?')))} → {html.escape(str(tier))} · Wtd IRR {prior_irr_s} → {irr_s}</span>"
                    f"<br><span class=\"sub\">{html.escape(str(sp.get('summary','')))}</span><br>")
        elif sp:
            # Pass-2 badge integrity (round-2 audit): the badge may render ONLY
            # when the CURRENT score.json itself carries a second_pass object.
            # A second_pass_queue.json status or a second_pass.md on disk
            # describes an older score (pass 2 reviewed v4 numbers); a v5
            # re-score built by make_score.py drops the object naturally.
            p2_s = f"<br><span class=\"sub\">✓ Pass 2 checked {html.escape(str(sp.get('date','')))} — no change</span>"
        ov_s = ""
        ov_badges = []
        for o in s.get("overrides") or []:
            if isinstance(o, dict) and o.get("field"):
                kind_lbl = "AI estimate" if o.get("kind") == "estimate" else "filing override"
                ov_badges.append(f"<span class=\"ovbadge\">{html.escape(str(o['field']))}: {kind_lbl}</span>")
        if s.get("tier_by_numbers") and tier != s.get("tier_by_numbers"):
            ov_badges.append(f"<span class=\"tobadge\">tier overridden {html.escape(str(s['tier_by_numbers']))}→{html.escape(str(tier))}</span>")
        if ov_badges:
            ov_s = "".join(ov_badges) + "<br>"
        rows += f"""<tr{p2_attr} data-tier="{html.escape(str(tier))}" data-sector="{html.escape(str(s.get('sector','')))}" data-conf="{html.escape(str(s.get('confidence','')))}" data-search="{html.escape((s.get('ticker','')+' '+s.get('name','')).lower())}">
<td><a class="co" href="#d-{safe_id(s.get('ticker',''))}" onclick="return showDetail('{safe_id(s.get('ticker',''))}')"><b>{html.escape(str(s.get('ticker','')))}</b></a><br><span class="sub">{html.escape(str(s.get('name','')))} · <span class="more">details ›</span></span></td>
<td><span class="badge" style="background:{tier_color.get(tier,'#333')}">{html.escape(str(tier))}</span></td>
<td class="num">{moat_s}</td>
<td class="num">{irr_s}</td>
<td class="num">{fmt_money(s.get('price'))}</td>
<td class="num">{fmt_money(s.get('iv_at_15'))}</td>
<td class="num {up_cls}">{up_s}</td>
<td class="num">{fmt_cap(s.get('market_cap_b'))}</td>
<td>{html.escape(str(s.get('sector','')))}</td>
<td>{html.escape(str(s.get('confidence','')))}</td>
<td>{p2_s}{ov_s}{html.escape(str(s.get('one_liner','')))}{sc_s}{fl_s}<br><span class="sub">{html.escape(str(s.get('analysis_date','')))} · folder: stocks/{html.escape(s.get('_folder',''))}/</span></td></tr>
"""
        details += build_detail(s, tier_color)
    stale_html = ""
    if stale:
        stale_rows = ""
        for s in stale:
            tier = s.get("tier_final") or s.get("tier_by_numbers") or "?"
            irr = s.get("implied_irr")
            irr_s = f"{irr*100:.1f}%" if isinstance(irr, (int, float)) else "—"
            stale_rows += (f"<tr><td><b>{html.escape(str(s.get('ticker','')))}</b></td>"
                           f"<td>{html.escape(str(s.get('name','')))}</td>"
                           f"<td><span class=\"badge stalebadge\">{html.escape(str(tier))}</span></td>"
                           f"<td class=\"num\">{irr_s}</td>"
                           f"<td>{html.escape(str(s.get('analysis_date','')))}</td></tr>\n")
        stale_html = f"""<details class="stalebox"><summary>Pre-v5 results — re-run pending ({len(stale)})</summary>
<p class="sub">These scores were produced by the pre-v5 engine, before the data gate existed. They are shown for reference only and are <b>not current results</b> — every one is queued for a v5 re-run and leaves this list when its v5 score lands.</p>
<div class="twrap"><table class="stalet"><thead><tr><th>Ticker</th><th>Company</th><th>Old tier</th><th class="num">Old Wtd IRR</th><th>Scored</th></tr></thead><tbody>{stale_rows}</tbody></table></div>
</details>"""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DCF Ranking — {today}</title><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet"><style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0f1115;color:#e6e6e6;margin:16px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#9aa;font-size:12px}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}}
button,select,input{{background:#1c1f26;color:#e6e6e6;border:1px solid #333;border-radius:8px;padding:7px 10px;font-size:14px}}
button.on{{background:#2563eb;border-color:#2563eb}}
.twrap{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;min-width:1120px;table-layout:fixed;font-size:14px}} th,td{{padding:8px;border-bottom:1px solid #262a33;text-align:left;vertical-align:top;overflow-wrap:normal}}
td:last-child{{overflow-wrap:break-word}}
td.num{{text-align:right;white-space:nowrap}} th.num{{text-align:right}}
a.co{{color:#e6e6e6;text-decoration:none}} a.co:hover{{color:#7dd3fc}} .more{{color:#7dd3fc}}
.mono{{font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace}}
.detail{{display:none;max-width:760px;margin:0 auto;font-family:'IBM Plex Sans',-apple-system,Segoe UI,Roboto,sans-serif;color:#ECEEF2}}
.detail.open{{display:block}}
.dnav{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}}
.dback{{color:#C9D4FF;text-decoration:none;font-size:14px;font-weight:500}}
.dnavr{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#A0A8B6}}
.dcard{{background:#14171D;border:1px solid #272C36;border-radius:16px;padding:18px;margin:14px 0}}
.dsec{{margin:26px 0}} .dh2{{font-size:19px;font-weight:600;margin:0 0 6px}}
.dnote{{font-size:13.5px;color:#A0A8B6;line-height:1.5;margin:4px 0}} .dnote b{{color:#ECEEF2;font-weight:500}}
.dk{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#A0A8B6}}
.verdict{{border-radius:20px;padding:22px 20px;margin-top:0}}
.vhead{{display:flex;align-items:center;gap:14px}}
.vtile{{display:inline-flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:13px;color:#0C0E12;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:24px;font-weight:600;flex:0 0 auto}}
.vname{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}}
.vtick{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:28px;font-weight:600}}
.vco{{font-size:18px;font-weight:500}}
.vmain{{display:flex;flex-wrap:wrap;align-items:flex-end;gap:18px 36px;margin-top:20px}}
.virr{{display:flex;flex-direction:column;gap:6px}}
.virr-v{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:56px;font-weight:500;line-height:1;letter-spacing:-.02em}}
.vgauge{{flex:1 1 240px;display:flex;flex-direction:column;gap:8px;padding-bottom:4px}}
.vgauge-lbl{{font-size:14px;font-weight:500}}
.gauge{{position:relative;height:10px;border-radius:5px;background:#272C36}}
.gaugefill{{position:absolute;left:0;top:0;bottom:0;border-radius:5px}}
.gaugetick{{position:absolute;top:-5px;width:2px;height:20px;margin-left:-1px;border-radius:1px;background:#ECEEF2}}
.gaugescale{{position:relative;height:16px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;color:#A0A8B6}}
.gaugescale span{{position:absolute;top:0}} .gs-mid{{transform:translateX(-50%);color:#ECEEF2;white-space:nowrap}}
.vchips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}}
.dchip{{display:inline-flex;align-items:center;padding:6px 10px;border-radius:999px;background:#1B1F27;border:1px solid #2C323D;font-size:13px;color:#D4D8E0}}
.vtake{{margin:20px 0 0;padding-top:20px;border-top:1px solid #272C36;font-size:16px;line-height:1.6;color:#D9DDE4}}
.p2box{{background:#0E1B2E;border:1px solid #274b73;border-radius:16px;padding:14px 18px;margin:14px 0}} .p2box p{{margin:6px 0 0;line-height:1.55;font-size:14px;color:#D9DDE4}}
.pv{{padding:18px 16px 14px}}
.pvplot{{position:relative;height:128px}}
.pv-range-lbl{{position:absolute;top:0;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#A0A8B6;white-space:nowrap}}
.pv-range-val{{position:absolute;top:17px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px;color:#C9D4FF;white-space:nowrap}}
.pv-track{{position:absolute;left:0;right:0;top:58px;height:4px;border-radius:2px;background:#272C36}}
.pv-band{{position:absolute;top:50px;height:20px;box-sizing:border-box;border-radius:5px;background:rgba(122,162,255,.18);border:1px solid rgba(122,162,255,.6)}}
.pv-ivmark{{position:absolute;top:44px;width:2px;height:32px;margin-left:-1px;border-radius:1px;background:#ECEEF2}}
.pv-pricedot{{position:absolute;top:53px;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:#FF8A8A;box-shadow:0 0 0 4px rgba(255,138,138,.18)}}
.pv-ivlbl{{position:absolute;top:86px;margin-left:-1px;display:flex;flex-direction:column;gap:2px;white-space:nowrap}}
.pv-ivlbl span,.pv-pricelbl span{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#A0A8B6}}
.pv-ivlbl b{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:15px;font-weight:500}}
.pv-pricelbl{{position:absolute;right:0;top:86px;display:flex;flex-direction:column;align-items:flex-end;gap:2px;white-space:nowrap}}
.pv-pricelbl b{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:15px;font-weight:500;color:#FF8A8A}}
.pv-axis{{display:flex;justify-content:space-between;padding-top:8px;border-top:1px solid #272C36;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:11px;color:#A0A8B6}}
.dtiles{{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}}
.dtile{{flex:1 1 160px;box-sizing:border-box;background:#14171D;border:1px solid #272C36;border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:6px}}
.dv{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:20px;font-weight:500}} .dv.pos{{color:#4ade80}} .dv.neg{{color:#FF8A8A}}
.baseoe{{display:flex;flex-direction:column;gap:8px}}
.baseoe-v{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:26px;font-weight:500;line-height:1.1}}
.baseoe-u{{font-size:15px;color:#A0A8B6}}
.scncard{{padding:6px 0 0;overflow:hidden}}
.scnrow{{padding:14px 16px;border-bottom:1px solid #272C36;display:flex;flex-direction:column;gap:10px}}
.scnhead{{display:flex;justify-content:space-between;align-items:center;gap:12px}}
.scnname{{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:600}}
.scndot{{width:10px;height:10px;border-radius:3px}}
.prob{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;padding:2px 7px;border-radius:999px;background:#1B1F27;border:1px solid #2C323D;color:#C3C9D4;font-weight:400}}
.scnirr{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:18px;font-weight:500}}
.scnbar{{position:relative;height:6px;border-radius:3px;background:#272C36}}
.scnfill{{position:absolute;left:0;top:0;bottom:0;border-radius:3px}}
.scntick{{position:absolute;top:-4px;width:2px;height:14px;margin-left:-1px;border-radius:1px;background:#ECEEF2}}
.scnsub{{display:flex;flex-wrap:wrap;gap:4px 18px;font-size:13px;color:#A0A8B6}}
.scnsub b{{font-family:'IBM Plex Mono',ui-monospace,monospace;color:#ECEEF2;font-weight:500}}
.scnfoot{{padding:14px 16px;background:#1B1F27;display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 16px;font-size:14px;font-weight:600}}
.scnfoot span:last-child{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:500;color:#D4D8E0}}
.moathead{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px 16px}}
.moattitle{{display:flex;align-items:center;gap:12px}} .moattitle .dh2{{margin:0}}
.moatscore{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:17px;font-weight:500}}
.mdots{{display:inline-flex;gap:3px}} .mdot{{width:7px;height:7px;border-radius:50%;background:#333A46}} .mdot.on{{background:#ECEEF2}}
.mcols{{display:flex;flex-wrap:wrap;gap:16px 28px;margin-top:16px}}
.mcol{{flex:1 1 260px;display:flex;flex-direction:column;gap:10px}}
.mk{{font-size:11px;letter-spacing:.08em;text-transform:uppercase}} .mk.pos{{color:#5BD69C}} .mk.neg{{color:#FF8A8A}}
.mcol ul{{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px;font-size:14px;line-height:1.5;color:#D9DDE4}}
.mcol li{{display:flex;gap:10px}} .sign{{font-family:'IBM Plex Mono',ui-monospace,monospace}} .sign.pos{{color:#5BD69C}} .sign.neg{{color:#FF8A8A}}
.dimp{{color:#D9DDE4;font-size:14.5px;line-height:1.6;margin:14px 0 0}}
.histcard{{padding:16px}}
.hlegend{{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:#A0A8B6;margin-bottom:12px}}
.hlegend .sw{{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px}} .sw.cons{{background:#7484A0}} .sw.maint{{background:#C9D4FF}}
.hunit{{margin-left:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px}}
.hchart{{position:relative;height:160px;display:flex;gap:8px}}
.hzero{{position:absolute;left:0;right:0;top:80px;height:1px;background:#3A4252}}
.hcol{{flex:1 1 0;position:relative;min-width:0}}
.hbar{{position:absolute;width:32%;border-radius:3px}} .hbar.cons{{left:16%;background:#7484A0}} .hbar.maint{{left:52%;background:#C9D4FF}}
.hlbl{{position:absolute;left:50%;top:0;transform:translateX(-30%);font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:11px;color:#ECEEF2;white-space:nowrap}}
.hyears{{display:flex;gap:8px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;color:#A0A8B6;margin-top:6px}}
.hyears span{{flex:1 1 0;text-align:center}}
table.mini{{min-width:560px;table-layout:auto;font-size:13px}} table.mini th,table.mini td{{padding:6px 8px}} table.mini td.num{{font-family:'IBM Plex Mono',ui-monospace,monospace}}
.histcard .twrap{{overflow-x:auto;margin-top:12px}}
.fchips{{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}}
.fchip{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;padding:5px 9px;border-radius:6px;background:#1B1F27;border:1px solid #2C323D;color:#D4D8E0}}
.fcount{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:15px;font-weight:500;color:#A0A8B6}}
.dfoot{{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 16px;padding-top:16px;border-top:1px solid #272C36;font-size:13px;color:#A0A8B6;margin-top:8px}}
@media (max-width:760px){{
#t{{min-width:0;table-layout:auto}}
#t thead{{display:none}}
#t,#t tbody{{display:block}}
#t tr{{display:grid;grid-template-columns:1fr 1fr;column-gap:14px;align-items:start;border:1px solid #262a33;border-radius:12px;padding:10px 12px;margin-bottom:10px;background:#14161c}}
#t tr[data-p2="changed"]{{background:#0d1f2c;border-color:#155e75}}
#t td{{display:block;border-bottom:none;padding:2px 0;text-align:left!important;white-space:normal!important}}
#t td:nth-child(1),#t td:nth-child(9),#t td:nth-child(11){{grid-column:1/-1}}
#t td::before{{display:block;font-size:11px;color:#9aa;text-transform:uppercase;letter-spacing:.04em;margin-bottom:1px}}
#t td:nth-child(2)::before{{content:"Tier"}} #t td:nth-child(3)::before{{content:"Moat"}} #t td:nth-child(4)::before{{content:"Wtd IRR"}} #t td:nth-child(5)::before{{content:"Price"}} #t td:nth-child(6)::before{{content:"IV @15%"}} #t td:nth-child(7)::before{{content:"Upside @15%"}} #t td:nth-child(8)::before{{content:"Mkt Cap"}} #t td:nth-child(9)::before{{content:"Sector"}} #t td:nth-child(10)::before{{content:"Conf."}} #t td:nth-child(11)::before{{content:"Take"}}
.detail .twrap{{overflow-x:auto}}
}} .pos{{color:#4ade80}} .neg{{color:#f87171}}
.badge{{color:#fff;border-radius:6px;padding:2px 9px;font-weight:700}}
.p2chg{{display:inline-block;background:#0b3b52;color:#7dd3fc;border:1px solid #155e75;border-radius:6px;padding:1px 7px;font-size:12.5px;margin:0 0 2px}}
.ovbadge{{display:inline-block;background:#3a2b0b;color:#fbbf24;border:1px solid #8a6d1f;border-radius:6px;padding:1px 7px;font-size:12.5px;margin:0 4px 2px 0}}
.tobadge{{display:inline-block;background:#2e1065;color:#c4b5fd;border:1px solid #6d28d9;border-radius:6px;padding:1px 7px;font-size:12.5px;margin:0 4px 2px 0}}
.ovcard{{padding:16px 18px}} .ovcard .mini{{min-width:0}} .ovcard td{{white-space:normal}}
tr[data-p2="changed"] td:first-child{{box-shadow:inset 3px 0 0 #38bdf8}}
details.howto{{margin:2px 0 6px}} details.howto summary{{color:#9aa;font-size:12.5px;cursor:pointer}} details.howto p{{color:#9aa;font-size:12.5px;line-height:1.5;margin:6px 0 0}}
details.stalebox{{margin:18px 0 6px;border:1px dashed #4b5563;border-radius:10px;padding:10px 12px;background:#14161c}}
details.stalebox summary{{color:#fbbf24;font-size:14px;font-weight:600;cursor:pointer}}
details.stalebox p{{margin:8px 0}}
table.stalet{{min-width:0;table-layout:auto;font-size:13px}} table.stalet th,table.stalet td{{padding:5px 8px}}
.stalebadge{{background:#4b5563!important;opacity:.75}}
td:last-child{{line-height:1.45}}
</style></head><body>
<h1>Owner's-Earnings DCF Ranking — {today}</h1>
<div class="sub">Sweep progress: {done} analyzed of {total} companies under $40B + pilot exceptions.{f" {changed_count} revised by the second pass (↺ badge in Take)." if changed_count else ""} Ranked by probability-weighted implied IRR at current price. Tap a company name for its detail page.</div>
<details class="howto"><summary>How to read this</summary><p>Each company gets a five-scenario owner's-earnings DCF (super bear / bear / base / bull / super bull, each with an assigned likelihood); growth fades over a moat-driven competitive advantage period. <b>Wtd IRR</b> = probability-weighted expected annual return at the current price. <b>IV</b> = probability-weighted intrinsic value per share at a 15% discount rate; <b>Upside</b> = IV vs price. Tiers: S ≥25% · A 20-25% · B 15-20% (clears the 15% hurdle) · C 10-15% · D &lt;10% · F no positive owner's earnings. Screening-grade standardized DCF — read the company folder's analysis.md before acting.</p></details>
<div id="listView">
<div class="controls">
<button data-f="all" class="on">All</button><button data-f="S">S ≥25%</button><button data-f="A">A 20%+</button><button data-f="B">B 15%+</button><button data-f="C">C</button><button data-f="D">D</button><button data-f="F">F</button>
<input id="q" placeholder="Search ticker / name…" size="24"><span class="sub" id="count"></span>
</div>
<div class="twrap"><table id="t"><colgroup><col style="width:11%"><col style="width:4.5%"><col style="width:5%"><col style="width:6%"><col style="width:7%"><col style="width:8%"><col style="width:7%"><col style="width:7%"><col style="width:9%"><col style="width:5.5%"><col style="width:30%"></colgroup><thead><tr><th>Company</th><th>Tier</th><th class="num">Moat</th><th class="num">Wtd IRR</th><th class="num">Price</th><th class="num">Wtd IV @15%</th><th class="num">Upside @15%</th><th class="num">Mkt Cap</th><th>Sector</th><th>Conf.</th><th>Take</th></tr></thead>
<tbody>{rows if rows else '<tr><td colspan="11">No companies analyzed yet.</td></tr>'}</tbody></table></div>
</div>
{stale_html}
{details}
<script>
let tier='all';const q=document.getElementById('q');
function apply(){{let n=0;document.querySelectorAll('#t tbody tr').forEach(tr=>{{const okT=tier==='all'||tr.dataset.tier===tier;const okQ=!q.value||tr.dataset.search.includes(q.value.toLowerCase());tr.style.display=(okT&&okQ)?'':'none';if(okT&&okQ)n++}});document.getElementById('count').textContent=n+' shown'}}
document.querySelectorAll('button[data-f]').forEach(b=>b.onclick=()=>{{tier=b.dataset.f;document.querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');apply()}});
q.oninput=apply;apply();
function showDetail(id){{document.getElementById('listView').style.display='none';document.querySelectorAll('.detail').forEach(d=>d.classList.remove('open'));const el=document.getElementById('d-'+id);if(el){{el.classList.add('open')}}window.scrollTo(0,0);return false}}
function backToList(){{document.querySelectorAll('.detail').forEach(d=>d.classList.remove('open'));document.getElementById('listView').style.display='';window.scrollTo(0,0);return false}}
if(location.hash&&location.hash.startsWith('#d-')){{showDetail(location.hash.slice(3))}}
</script></body></html>"""
    path = f"{OUT}/ranking-{today}.html"
    open(path, "w").write(doc)
    open(f"{OUT}/latest.html", "w").write(doc)
    print(f"wrote {path} with {len(scores)} companies; progress {done}/{total}")

if __name__ == "__main__":
    main()
