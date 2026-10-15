/* Owner's-Earnings DCF Ranking — static app (v6 presentation, 2026-10-14).
 *
 * One file, vanilla ES2018, no modules, no libraries. Renders the ranking and
 * every company page from the JSON the data layer writes next to this file
 * (_system/build_site.py → meta.json, index.json, data/<TICKER>.json), or
 * from window.SITE_DATA when inlined into the chat attachment. Contract:
 * _system/SITE_CONTRACT.md. The app never computes a valuation figure —
 * every number is read from a record; the only arithmetic is display
 * arithmetic the v2 Python renderer also did (ratios on filed values).
 *
 * Layout of this file:
 *   1. constants (design tokens for charts, labels)
 *   2. pure helpers: esc, num, fmt*, md
 *   3. pure derivations: liveView, hurdlePrices, sensitivity
 *   4. pure renderers: renderListHTML, renderCompanyHTML, render<Tab>
 *   5. pure chart specs: chartSpecs*(record) → {id: spec}
 *   6. DOM: drawChart / drawPrice, mount, route, data loading, events
 *   7. exports (module.exports for node tests, window.App in the browser)
 */
(function (root) {
'use strict';

/* ------------------------------------------------------------ 1. constants */
var TABS = [['overview', 'Overview'], ['financials', 'Financials'], ['dividends', 'Dividends'], ['segments', 'Segments'],
            ['forecast', 'Forecast'], ['analysis', 'Analysis'], ['data', 'Data']];
var TAB_KEYS = TABS.map(function (t) { return t[0]; });
var TIER_ACCENT = { S: '#B79CFF', A: '#4ADE80', B: '#5BD69C', C: '#F2B84B', D: '#F08A4B', F: '#9AA3B2' };
var TIER_MEANING = { S: '≥25% expected return', A: '20–25%', B: '15–20% · clears the hurdle', C: '10–15% · below hurdle', D: 'below 10%', F: "no positive owner's earnings" };
var LABELS = [['super_bear', 'Super bear'], ['bear', 'Bear'], ['base', 'Base'], ['bull', 'Bull'], ['super_bull', 'Super bull']];
var SCN_COLORS = { super_bear: '#8A93A6', bear: '#A7B1C7', base: '#C9D4FF', bull: '#9AD6B4', super_bull: '#5BD69C', weighted: '#FFFFFF' };
var C_PRICE = '#FF8A8A', C_IV = '#C9D4FF', C_BAND = 'rgba(122,162,255,.18)', C_FCBAR = '#7AA2FF'; // forecast bars next to filed (C_OE) bars
var C_REV = '#7AA2FF', C_NI = '#5BD69C', C_OE = '#C9D4FF', C_OCF = '#7484A0', C_CAPEX = '#F2B84B', C_SBC = '#F08A4B', C_CASH = '#7AA2FF', C_DEBT = '#F08A4B', C_FCF = '#9AD6B4';
var SEG_COLORS = ['#7AA2FF', '#5BD69C', '#F2B84B', '#F08A4B', '#B79CFF', '#C9D4FF', '#9AD6B4', '#FF8A8A', '#7484A0', '#D4A5FF', '#8FD3F4', '#E6C98C'];
var DIV_FREQ = { quarterly: 'Quarterly', semiannual: 'Semiannual', annual: 'Annual', irregular: 'Irregular', none: 'None' };
var HURDLES_DEFAULT = { S: 0.25, A: 0.20, B: 0.15, C: 0.10 };
var ELIM_RX = /elimin|corporate|intersegment|unallocated|reconcil|\bother\b/i;
var SORTS = [['irr_live', 'Live IRR'], ['irr', 'Scored IRR'], ['irr_bear', 'Bear-case IRR'], ['upside', 'Upside @15%'], ['moat', 'Moat'], ['cap', 'Market cap'], ['ret_1y', '1y price']];
var STORAGE_KEY = 'oe-dcf.list.v1';

/* ------------------------------------------------------------ 2. helpers */
function esc(x) {
  if (x === null || x === undefined) return '';
  return String(x).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function num(v) {
  if (v === null || v === undefined || v === '' || typeof v === 'boolean') return null;
  var f = Number(v);
  return isFinite(f) ? f : null;
}
function commas(s) { // "1234567.89" → "1,234,567.89"
  var parts = String(s).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}
function fixed(v, d) { return commas(Math.abs(v).toFixed(d === undefined ? 2 : d)); }
function fmtMoney(v, d) {
  v = num(v); if (v === null) return '—';
  return (v < 0 ? '-' : '') + '$' + fixed(v, d === undefined ? 2 : d);
}
function fmtBig(v) {
  v = num(v); if (v === null) return '—';
  var s = v < 0 ? '-' : '', a = Math.abs(v);
  if (a >= 1e12) return s + '$' + fixed(a / 1e12, 2) + 'T';
  if (a >= 1e9) return s + '$' + fixed(a / 1e9, 2) + 'B';
  if (a >= 1e6) return s + '$' + fixed(a / 1e6, 0) + 'M';
  if (a >= 1e3) return s + '$' + fixed(a / 1e3, 0) + 'K';
  return s + '$' + fixed(a, 2);
}
function fmtCnt(v) {
  v = num(v); if (v === null) return '—';
  var s = v < 0 ? '-' : '', a = Math.abs(v);
  if (a >= 1e9) return s + fixed(a / 1e9, 2) + 'B';
  if (a >= 1e6) return s + fixed(a / 1e6, 1) + 'M';
  return s + fixed(a, 0);
}
function fmtPct(x, d, signed) {
  x = num(x); if (x === null) return '—';
  d = d === undefined ? 1 : d;
  var p = x * 100, s = fixed(p, d);
  return (p < 0 ? '-' : (signed ? '+' : '')) + s + '%';
}
function fmtPts(p, d) { // a value already in percent units, signed: "+38%"
  p = num(p); if (p === null) return '—';
  d = d === undefined ? 0 : d;
  return (p < 0 ? '-' : '+') + fixed(p, d) + '%';
}
function fmtX(v, d) {
  v = num(v); if (v === null) return '—';
  return (v < 0 ? '-' : '') + fixed(v, d === undefined ? 1 : d) + '×';
}
function fmtCap(v) { v = num(v); return v === null ? '—' : (v < 0 ? '-' : '') + '$' + fixed(v, 2) + 'B'; }
function signCls(v) { v = num(v); return v === null ? '' : v > 0 ? 'pos' : v < 0 ? 'neg' : ''; }
function safeId(t) { return String(t === null || t === undefined ? '' : t).replace(/[^A-Za-z0-9_.-]/g, '-'); }
function get(a, i) { return Array.isArray(a) && i < a.length ? a[i] : null; }
function obj(x) { return x && typeof x === 'object' && !Array.isArray(x) ? x : {}; }
function arr(x) { return Array.isArray(x) ? x : []; }
function first(x) { return Array.isArray(x) && x.length ? x[0] : null; }
function joinNonEmpty(parts, sep) { return parts.filter(function (p) { return p; }).join(sep); }

/* ---- markdown (analysis.md / second_pass.md): headings, lists, tables, bold, code, links, hr, fences */
function mdInline(s) {
  s = esc(s);
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return s;
}
function md(text) {
  var out = [], para = [], list = null, listTag = 'ul', tbl = null, fence = null;
  function flushPara() { if (para.length) { out.push('<p>' + para.map(mdInline).join(' ') + '</p>'); para = []; } }
  function flushList() { if (list) { out.push('<' + listTag + '>' + list.map(function (x) { return '<li>' + mdInline(x) + '</li>'; }).join('') + '</' + listTag + '>'); list = null; } }
  function flushTbl() {
    if (tbl) {
      var head = tbl[0], rows = tbl.slice(1);
      var h = head.map(function (c) { return '<th>' + mdInline(c) + '</th>'; }).join('');
      var b = rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + mdInline(c) + '</td>'; }).join('') + '</tr>'; }).join('');
      out.push('<div class="twrap"><table class="mdt"><thead><tr>' + h + '</tr></thead><tbody>' + b + '</tbody></table></div>');
      tbl = null;
    }
  }
  var lines = String(text === null || text === undefined ? '' : text).split(/\r?\n/);
  for (var i = 0; i < lines.length; i++) {
    var s = lines[i].replace(/\s+$/, ''), m;
    if (fence !== null) {
      if (/^\s*```/.test(s)) { out.push('<pre class="json">' + esc(fence.join('\n')) + '</pre>'); fence = null; }
      else fence.push(lines[i]);
      continue;
    }
    if (/^\s*```/.test(s)) { flushPara(); flushList(); flushTbl(); fence = []; continue; }
    if (s.charAt(0) === '|') {
      flushPara(); flushList();
      var cells = s.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(function (c) { return c.trim(); });
      var sep = cells.every(function (c) { return /^:?-{2,}:?$/.test(c || '--'); });
      if (sep) continue;
      tbl = tbl || []; tbl.push(cells); continue;
    }
    flushTbl();
    m = /^(#{1,6})\s+(.*)/.exec(s);
    if (m) { flushPara(); flushList(); var lvl = Math.min(m[1].length + 1, 4); out.push('<h' + lvl + '>' + mdInline(m[2]) + '</h' + lvl + '>'); continue; }
    m = /^\s*[-*]\s+(.*)/.exec(s);
    if (m) { flushPara(); if (list && listTag !== 'ul') flushList(); listTag = 'ul'; list = list || []; list.push(m[1]); continue; }
    m = /^\s*\d+[.)]\s+(.*)/.exec(s);
    if (m) { flushPara(); if (list && listTag !== 'ol') flushList(); listTag = 'ol'; list = list || []; list.push(m[1]); continue; }
    if (s.trim() === '---' || s.trim() === '***') { flushPara(); flushList(); out.push('<hr>'); continue; }
    if (!s.trim()) { flushPara(); flushList(); continue; }
    if (list !== null && /^\s{2,}/.test(s)) { list[list.length - 1] += ' ' + s.trim(); continue; }
    flushList(); para.push(s.trim());
  }
  if (fence !== null) out.push('<pre class="json">' + esc(fence.join('\n')) + '</pre>');
  flushPara(); flushList(); flushTbl();
  return out.join('');
}

/* ------------------------------------------------------------ 3. derivations (read-only views over a record) */
function tierForIrr(irr, hurdles) {
  irr = num(irr); if (irr === null) return null;
  var h = obj(hurdles);
  var S = num(h.S) !== null ? num(h.S) : HURDLES_DEFAULT.S, A = num(h.A) !== null ? num(h.A) : HURDLES_DEFAULT.A;
  var B = num(h.B) !== null ? num(h.B) : HURDLES_DEFAULT.B, C = num(h.C) !== null ? num(h.C) : HURDLES_DEFAULT.C;
  return irr >= S ? 'S' : irr >= A ? 'A' : irr >= B ? 'B' : irr >= C ? 'C' : 'D';
}
function scnMap(src) {
  var o = {}, s = obj(src);
  Object.keys(s).forEach(function (k) { var r = s[k]; if (r && typeof r === 'object') o[k] = { irr: num(r.irr), tier: r.tier || null }; });
  return o;
}
/* The figures the page shows: live.json (the scored paths repriced at the last close) when it
   carries a price and a weighted IRR, else the scored values. Every key is present either way;
   scored_* keeps the verdict-date figure. Upside is IV@15 ÷ price − 1 on the file's own values. */
function liveView(record) {
  var s = obj(record.score), lv = obj(record.live), row = obj(record.row);
  var scoredTier = s.tier_final || s.tier_by_numbers || row.tier || '?';
  var scn = scnMap(s.scenarios);
  var v = {
    is_live: false, price: num(s.price), price_date: s.analysis_date || null, price_source: null,
    irr: num(s.implied_irr), tier: scoredTier, irr_base: num(s.implied_irr_base_case),
    irr_bear: num(s.irr_bear !== undefined ? s.irr_bear : row.irr_bear), irr_bull: num(s.irr_bull !== undefined ? s.irr_bull : row.irr_bull),
    tier_bear: s.tier_bear || row.tier_bear || null, tier_bull: s.tier_bull || row.tier_bull || null,
    upside: num(s.upside_at_15_pct), cap_b: num(s.market_cap_b), irr_at_floor: !!(s.irr_at_floor || row.irr_at_floor),
    scenarios: scn, scored_scenarios: scn,
    scored_price: num(s.price), scored_date: s.analysis_date || null, scored_irr: num(s.implied_irr), scored_tier: scoredTier,
    scored_upside: num(s.upside_at_15_pct), scored_cap_b: num(s.market_cap_b),
    tier_changed: false, irr_pp: null, price_change_pct: null
  };
  var price = num(lv.price), irr = num(lv.irr_weighted);
  if (record.live && price !== null && irr !== null) {
    var iv15 = num(lv.iv_at_15), up = null;
    if (iv15 !== null && price > 0) up = (iv15 / price - 1) * 100;
    else if (num(lv.upside_at_15) !== null) up = num(lv.upside_at_15) * 100;
    var cap = num(lv.market_cap_est), d = obj(lv.delta), sc = obj(lv.scored), liveScn = scnMap(lv.scenarios);
    var liveTier = lv.tier || scoredTier;
    v.is_live = true; v.price = price; v.price_date = lv.price_date || lv.as_of || null; v.price_source = lv.price_source || null;
    v.irr = irr; v.tier = liveTier;
    v.irr_base = num(lv.irr_base) !== null ? num(lv.irr_base) : v.irr_base;
    v.irr_bear = num(lv.irr_bear) !== null ? num(lv.irr_bear) : v.irr_bear;
    v.irr_bull = num(lv.irr_bull) !== null ? num(lv.irr_bull) : v.irr_bull;
    v.tier_bear = lv.tier_bear || v.tier_bear; v.tier_bull = lv.tier_bull || v.tier_bull;
    v.upside = up !== null ? up : v.upside; v.cap_b = cap !== null ? cap / 1e9 : v.cap_b;
    v.irr_at_floor = !!(lv.irr_at_floor || row.irr_at_floor_live); v.scenarios = Object.keys(liveScn).length ? liveScn : scn;
    v.scored_price = num(lv.scored_price) !== null ? num(lv.scored_price) : v.scored_price;
    v.scored_date = lv.scored_date || v.scored_date;
    v.scored_irr = num(sc.irr_weighted) !== null ? num(sc.irr_weighted) : v.scored_irr;
    v.scored_tier = sc.tier_final || scoredTier;
    v.tier_changed = ('tier_changed' in d) ? !!d.tier_changed : liveTier !== scoredTier;
    v.irr_pp = num(d.irr_pp); v.price_change_pct = num(lv.price_change_pct);
  }
  return v;
}
function tierShiftChip(v) {
  if (v.is_live && v.tier_changed && v.tier !== v.scored_tier) return '<span class="chip lvchip">Tier ' + esc(v.scored_tier) + ' → ' + esc(v.tier) + ' at last close</span>';
  return '';
}
function modelFit(record) {
  var row = obj(record.row), s = obj(record.score);
  if (row.fit) return row.fit;
  if (s.model_fit) return s.model_fit;
  return arr(s.fragility_flags).some(function (f) { return String(f).indexOf('SECTOR_MODEL_MISMATCH') === 0; }) ? 'misfit' : 'modeled';
}
/* Weighted IV at 15 / 20 / 25% — the hurdle prices. forecast.hurdle_prices (stored by the data
   layer from engine 5.4 or its replay), else the scored IV@15 and the index row's iv20 / iv25. */
function hurdlePrices(record) {
  var fc = obj(record.forecast), s = obj(record.score), row = obj(record.row);
  var hp = obj(fc.hurdle_prices);
  if (Object.keys(hp).length) return { 15: num(hp['15']), 20: num(hp['20']), 25: num(hp['25']) };
  return { 15: num(s.iv_at_15 !== undefined ? s.iv_at_15 : row.iv15), 20: num(s.iv_at_20 !== undefined ? s.iv_at_20 : row.iv20), 25: num(s.iv_at_25 !== undefined ? s.iv_at_25 : row.iv25) };
}
/* {label: {10,12,15,20,25, irr, irr_live, irr_at_floor, irr_live_at_floor}} from forecast.sensitivity, else the
   stored scenario IVs. The floor flags say the solver clamped that IRR at its floor — the figure is a bound,
   not an improvement, and every renderer that prints it marks it. */
function sensitivity(record) {
  var fc = obj(record.forecast), n = obj(record.numbers), s = obj(record.score), lv = obj(record.live), out = {};
  var sens = obj(fc.sensitivity), keys = LABELS.map(function (l) { return l[0]; }).concat(['weighted']);
  keys.forEach(function (k) {
    var src = sens[k] ? obj(sens[k]) : (k === 'weighted' ? obj(n.weighted) : obj(obj(n.scenarios)[k] || obj(s.scenarios)[k]));
    var row = {};
    [10, 12, 15, 20, 25].forEach(function (r) { row[r] = num(src[String(r)] !== undefined ? src[String(r)] : src['iv_at_' + r]); });
    row.irr = num(src.irr); row.irr_live = num(src.irr_live);
    row.irr_at_floor = !!src.irr_at_floor;
    row.irr_live_at_floor = !!(src.irr_live_at_floor || (k === 'weighted' && (lv.irr_at_floor || obj(record.row).irr_at_floor_live)));
    out[k] = row;
  });
  return out;
}
/* Which of the shown scenario IRRs sit at the solver's floor: {bear, bull, weighted, any} for the view in use
   (live when the page shows live figures, else scored). */
function floorFlags(record, isLive) {
  var sens = sensitivity(record), key = isLive ? 'irr_live_at_floor' : 'irr_at_floor', out = { any: false };
  LABELS.map(function (l) { return l[0]; }).concat(['weighted']).forEach(function (k) { out[k] = !!obj(sens[k])[key]; if (out[k]) out.any = true; });
  return out;
}
function floorSup(title) { return '<sup class="floor" title="' + esc(title || 'the IRR solver stopped at its floor: this figure is a bound, not a solved return') + '">at floor</sup>'; }

/* ------------------------------------------------------------ 4. renderers (pure: record → HTML string) */
function tile(k, v, cls, sub) {
  return '<div class="tile"><span class="k">' + k + '</span><span class="v ' + (cls || '') + '">' + v + '</span>' + (sub ? '<span class="tsub">' + sub + '</span>' : '') + '</div>';
}
function section(title, body, note, cls) {
  return '<section class="sec ' + (cls || '') + '"><h2>' + (title || '') + '</h2>' + (note ? '<p class="note">' + note + '</p>' : '') + body + '</section>';
}
function chartDiv(id, cls) { return '<div class="chart ' + (cls || '') + '" data-cid="' + esc(id) + '"></div>'; }
function gaugeScale(irr) {
  var scale = 30;
  if (irr !== null && irr * 100 > 30) scale = Math.floor(irr * 100 / 10 + 1) * 10;
  return scale;
}

function renderHeader(record) {
  var s = obj(record.score), n = obj(record.numbers), pr = obj(record.prices), row = obj(record.row);
  var v = liveView(record), tier = v.tier, acc = TIER_ACCENT[tier] || '#9AA3B2', price = v.price;
  var st = obj(pr.stats), chg = num(st.change_1d_pct), last = num(st.last);
  var ret1y = num(st.ret_1y_pct) !== null ? num(st.ret_1y_pct) : num(row.ret_1y_pct);
  var irr = v.irr, irrS = irr !== null ? fmtPct(irr) : '—';
  var ff = floorFlags(record, v.is_live), floor = v.irr_at_floor || ff.weighted || (!v.is_live && !!obj(n.diagnostics).irr_at_floor);
  var band = '', fbear = ff.bear ? ' ' + floorSup() : '', fbull = ff.bull ? ' ' + floorSup() : '';
  if (v.tier_bear && v.tier_bull) band = '<span class="tsub">Bear ' + fmtPct(v.irr_bear) + ' (' + esc(v.tier_bear) + ')' + fbear + ' → Bull ' + fmtPct(v.irr_bull) + ' (' + esc(v.tier_bull) + ')' + fbull + (v.is_live ? ' at last close' : '') + '</span>';
  else if (obj(v.scenarios.bear).irr !== null && obj(v.scenarios.bear).irr !== undefined && obj(v.scenarios.bull).irr !== null && obj(v.scenarios.bull).irr !== undefined) {
    var sb = v.scenarios.bear.irr, su = v.scenarios.bull.irr;
    band = '<span class="tsub">Bear ' + fmtPct(sb) + ' (' + esc(tierForIrr(sb)) + ')' + fbear + ' → Bull ' + fmtPct(su) + ' (' + esc(tierForIrr(su)) + ')' + fbull + (v.is_live ? ' at last close' : '') + '</span>';
  }
  var up = v.upside, prof = obj(obj(record.fundamentals).profile);
  var meta = joinNonEmpty([esc(s.sector || record.sector || row.sector), fmtCap(v.cap_b) + (v.is_live ? ' at last close' : ''),
    first(prof.exchanges) ? esc(first(prof.exchanges)) : '', prof.filer_category ? esc(prof.filer_category) : ''], ' · ');
  var fsub = '';
  if (tier === 'F') {
    var fs = s.f_subtype || n.f_subtype || row.f_subtype;
    fsub = { sbc_exceeds_cash: 'F · SBC exceeds cash generation', no_cash_generation: 'F · no cash generation' }[fs] || "F · no positive owner's earnings";
  }
  // compact header (owner decision, 2026-10-14): tier tile · ticker · name · sector line; the live expected
  // return with the scored figure beside it; the last close with its 1-day change; value @15% with upside.
  var sub, priceTile, ttile, chgS = chg !== null ? ' <small class="' + ((chg || 0) >= 0 ? 'pos' : 'neg') + '">' + fmtPts(chg, 2) + '</small>' : '';
  var rangeSub = joinNonEmpty([st.last_date && last !== null ? '52-wk ' + fmtMoney(st.low_52w) + '–' + fmtMoney(st.high_52w) : '', ret1y !== null ? '1y ' + fmtPts(ret1y, 0) : ''], ' · ');
  if (v.is_live) {
    sub = 'Scored <b>' + fmtPct(v.scored_irr) + '</b> at ' + fmtMoney(v.scored_price) + ' on ' + esc(v.scored_date) + (v.irr_pp !== null ? ' · ' + fmtPts(v.irr_pp, 1).replace('%', '') + ' pp at the last close' : '');
    priceTile = '<div class="hstat"><span class="k">Last close</span><span class="v mono">' + fmtMoney(price) + chgS + '</span><span class="tsub">' + joinNonEmpty([esc(v.price_date), v.price_change_pct !== null ? fmtPts(v.price_change_pct, 1) + ' vs scored ' + fmtMoney(v.scored_price) : 'scored at ' + fmtMoney(v.scored_price), rangeSub], ' · ') + '</span></div>';
    ttile = '<span class="ttile" style="background:' + acc + '" title="Live tier at the last close">' + esc(tier) + '</span>';
  } else {
    sub = 'Probability-weighted IRR at ' + fmtMoney(price);
    priceTile = '<div class="hstat"><span class="k">' + (last !== null && st.last_date ? 'Last close' : 'Price used') + '</span><span class="v mono">' + fmtMoney(last !== null && st.last_date ? last : price) + (last !== null && st.last_date ? chgS : '') + '</span><span class="tsub">' + joinNonEmpty([last !== null && st.last_date ? esc(st.last_date) + ' · scored at ' + fmtMoney(price) + ' (' + esc(s.analysis_date || '') + ')' : esc(n.price_source || '') + ' · ' + esc(s.analysis_date || ''), rangeSub], ' · ') + '</span></div>';
    ttile = '<span class="ttile" style="background:' + acc + '">' + esc(tier) + '</span>';
  }
  var chip = tierShiftChip(v);
  var scoredChip = v.is_live ? '<span class="chip lvchip muted" title="Scored on ' + esc(v.scored_date) + '">Scored ' + esc(v.scored_tier) + ' · live ' + esc(tier) + '</span>' : '';
  var wchip = row.watchlist === true ? '<span class="chip lvchip wchip" title="On the watchlist (_system/watchlist.json)">★ Watchlist</span>' : '';
  return '<header class="hero" style="--acc:' + acc + '"><div class="hrow">' + ttile
    + '<div class="hname"><div class="hline"><span class="htick">' + esc(s.ticker || record.ticker) + '</span><span class="hco">' + esc(s.name || record.name) + '</span>' + (chip || scoredChip) + wchip + '</div><span class="note">' + meta + '</span></div></div>'
    + '<div class="hstats"><div class="hstat big"><span class="k">Expected return / yr' + (v.is_live ? ' · live' : '') + '</span><span class="v mono" style="color:' + acc + '">' + irrS + '</span><span class="tsub">' + sub + (floor ? ' · at the model floor' : '') + (fsub ? ' · ' + esc(fsub) : '') + '</span>' + band + '</div>'
    + priceTile
    + '<div class="hstat"><span class="k">Value @15%</span><span class="v mono">' + fmtMoney(s.iv_at_15 !== undefined ? s.iv_at_15 : row.iv15) + '</span><span class="tsub ' + signCls(up) + '">' + (up !== null ? fmtPts(up, 0) + ' vs ' + (v.is_live ? 'last close' : 'price') : '—') + '</span></div>'
    + '</div></header>';
}
/* The condensed line the sticky tab bar shows once the header has scrolled away: ticker · last close ·
   1-day change · expected return. Same price rule as the header: the live price (with the 1-day change)
   on a live page; otherwise prices.stats.last with its change when a last close exists, else the scored
   price with no change figure — a change belongs to the close it was measured on, never to the scored price. */
function renderTabSummary(record) {
  var s = obj(record.score), row = obj(record.row), v = liveView(record), st = obj(obj(record.prices).stats), acc = TIER_ACCENT[v.tier] || '#9AA3B2';
  var last = num(st.last), hasLast = last !== null && !!st.last_date, chg = num(st.change_1d_pct);
  var price = v.is_live ? v.price : (hasLast ? last : v.price), showChg = chg !== null && (v.is_live || hasLast);
  return '<div class="tabsum" aria-hidden="true"><span class="ttile sm" style="background:' + acc + '">' + esc(v.tier) + '</span><b class="mono">' + esc(s.ticker || record.ticker || row.ticker) + '</b>'
    + '<span class="mono" title="' + (v.is_live || hasLast ? 'Last close' : 'Scored price') + '">' + fmtMoney(price) + '</span>' + (showChg ? '<span class="mono ' + ((chg || 0) >= 0 ? 'pos' : 'neg') + '">' + fmtPts(chg, 2) + '</span>' : '')
    + '<span class="mono" style="color:' + acc + '">' + (v.irr !== null ? fmtPct(v.irr) : '—') + (v.is_live ? ' live' : '') + '</span></div>';
}

function priceVsValueLine(record) {
  var s = obj(record.score), n = obj(record.numbers), v = liveView(record);
  var price = v.price, wIv = num(s.iv_at_15);
  var scn = Object.keys(obj(n.scenarios)).length ? obj(n.scenarios) : obj(s.scenarios);
  var ivs = Object.keys(scn).map(function (k) { return num(obj(scn[k]).iv_at_15); }).filter(function (x) { return x !== null; });
  if (!(ivs.length && price && wIv && wIv > 0)) return '';
  var lo = Math.min.apply(null, ivs), hi = Math.max.apply(null, ivs), top = Math.max(price, hi);
  var cands = [10, 20, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000], axisMax = top * 1.1;
  for (var i = 0; i < cands.length; i++) if (cands[i] > top * 1.04) { axisMax = cands[i]; break; }
  var X = function (x) { return (x / axisMax * 100).toFixed(2); };
  var ticks = '';
  for (var j = 0; j < 6; j++) ticks += '<span>$' + commas(Math.round(axisMax * j / 5)) + '</span>';
  return '<div class="pvplot"><span class="pv-range-lbl" style="left:' + X(lo) + '%">Scenario range</span><span class="pv-range-val" style="left:' + X(lo) + '%">' + fmtMoney(lo) + ' – ' + fmtMoney(hi) + '</span>'
    + '<div class="pv-track"></div><div class="pv-band" style="left:' + X(lo) + '%;width:' + Math.max(0.5, X(hi) - X(lo)).toFixed(2) + '%"></div>'
    + '<div class="pv-ivmark" style="left:' + X(wIv) + '%"></div><div class="pv-pricedot" style="left:' + X(price) + '%"></div>'
    + '<div class="pv-ivlbl" style="left:' + X(wIv) + '%"><span>Weighted IV</span><b>' + fmtMoney(wIv) + '</b></div><div class="pv-pricelbl"><span>Price</span><b>' + fmtMoney(price) + '</b></div></div><div class="pv-axis">' + ticks + '</div>';
}
function renderPriceChart(record) {
  var pr = obj(record.prices), body;
  if (arr(pr.weekly).length) {
    var ranges = ['1Y', '3Y', '5Y', '10Y', 'MAX'].map(function (r) { return '<button type="button" data-r="' + r + '" class="' + (r === '5Y' ? 'on' : '') + '" aria-pressed="' + (r === '5Y') + '">' + r + '</button>'; }).join('');
    var toggles = '<label><input type="checkbox" class="tg-iv" checked> Weighted value</label><label><input type="checkbox" class="tg-band" checked> Bear–bull range</label><label><input type="checkbox" class="tg-h"> 20% / 25% hurdle prices</label>';
    body = '<div class="pcbar"><div class="ranges" role="group" aria-label="Price range">' + ranges + '</div><div class="toggles">' + toggles + '</div></div><div class="pchart" data-cid="price"></div>'
      + '<div class="pcfoot"><span class="legend"><i style="background:' + C_PRICE + '"></i>Price</span><span class="legend"><i class="dash" style="border-color:' + C_IV + '"></i>Weighted IV @15%</span><span class="legend"><i style="background:' + C_BAND + ';border:1px solid rgba(122,162,255,.6)"></i>Scenario range (super bear → super bull)</span><span class="pcret"></span></div>'
      + '<p class="note">Prices: ' + esc(pr.source || '') + ', through ' + esc(pr.as_of || '') + ". The valuation lines are the engine's values at a 15% discount rate — the price at which the expected return equals the hurdle. Where the price sits against them is the whole screen.</p>";
  } else {
    body = priceVsValueLine(record) + "<p class=\"note\">No price history pulled for this name yet (prices.py) — the number line shows today's price against every scenario's value.</p>";
  }
  return '<section class="sec pcsec"><div class="card pc" data-range="5Y">' + body + '</div></section>';
}

function renderOverrides(record) {
  var s = obj(record.score), n = obj(record.numbers);
  var ov = arr(n.overrides_applied);
  if (!ov.length && arr(s.overrides).length) ov = arr(s.overrides).filter(function (o) { return o && typeof o === 'object'; }).map(function (o) { return { field: o.field, value: o.value, kind: o.kind, source: o.source, reason: '', periods_filled: [] }; });
  if (!ov.length) return '';
  var rows = ov.map(function (o) {
    var fv = (o.field === 'capex' || o.field === 'sbc') ? fmtBig(o.value) : fmtCnt(o.value);
    return '<tr><td>' + esc(o.field) + '</td><td class="num mono">' + fv + '</td><td>' + esc(o.kind) + '</td><td>' + esc(o.source) + '</td><td>' + esc(arr(o.periods_filled).map(function (x) { return String(x).slice(0, 4); }).join(', ')) + '</td></tr>';
  }).join('');
  var imp = obj(s.override_impact), impH = '';
  if (Object.keys(imp).length) {
    var basis = imp.base_used === 'ttm' ? 'TTM base' : '3-year median base', pct = num(imp.base_oe_impact_pct), pp = num(imp.weighted_irr_impact_pp);
    impH = '<p class="note">Measured impact on the ' + basis + ' actually used (no override → with override): base OE/share ' + fmtMoney(imp.base_oe_without_override) + ' → ' + fmtMoney(imp.base_oe_with_override)
      + (pct !== null ? ' (' + fmtPts(pct, 2) + ')' : '') + ' · weighted IRR ' + fmtPct(imp.weighted_irr_without_override) + ' → ' + fmtPct(imp.weighted_irr_with_override) + (pp !== null ? ' (' + fmtPts(pp, 2).replace('%', 'pp') + ')' : '') + '</p>';
    if (imp.unblocks_tier) impH += '<p class="note"><b>This override is the only reason this company has a tier.</b> Without it the filing gap blocks scoring entirely — the judgment call is the whole verdict.</p>';
  }
  var reasons = ov.filter(function (o) { return o.reason; }).map(function (o) { return '<p class="note"><b>' + esc(o.field) + ':</b> ' + esc(o.reason) + '</p>'; }).join('');
  return '<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Field</th><th class="num">Value</th><th>Kind</th><th>Source</th><th>Years filled</th></tr></thead><tbody>' + rows + '</tbody></table></div>' + impH + reasons + '</div>';
}

/* ---- profile cards (record.profile from profile.py; every card renders gracefully without it) */
function safeUrl(u) { u = String(u || ''); return /^https?:\/\//i.test(u) ? u : ''; }
function extLink(url, text) { var u = safeUrl(url); return u ? '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + text + '</a>' : text; }
function renderAbout(record) {
  var p = obj(record.profile), about = obj(p.about), fp = obj(obj(record.fundamentals).profile), n = obj(record.numbers), s = obj(record.score);
  var facts = [];
  var push = function (k, v) { if (v !== null && v !== undefined && v !== '') facts.push('<div class="fact"><span class="k">' + k + '</span><span>' + v + '</span></div>'); };
  var industry = about.industry || fp.sic_description, sector = about.sector || s.sector || record.sector;
  push('Industry', industry ? esc(industry) + (about.sic || fp.sic ? ' <span class="sub">SIC ' + esc(about.sic || fp.sic) + '</span>' : '') : null);
  push('Sector', sector ? esc(sector) : null);
  push('Headquarters', about.headquarters ? esc(about.headquarters) : null);
  push('Incorporated', about.state_of_incorporation || fp.state_of_incorporation ? esc(about.state_of_incorporation || fp.state_of_incorporation) : null);
  push('Exchange', about.exchange || first(fp.exchanges) ? esc(about.exchange || first(fp.exchanges)) : null);
  push('Filer category', about.filer_category || fp.filer_category ? esc(about.filer_category || fp.filer_category) : null);
  var fye = String(about.fiscal_year_end_mmdd || fp.fiscal_year_end_mmdd || '');
  push('Fiscal year end', fye.length === 4 ? esc(fye.slice(0, 2)) + '/' + esc(fye.slice(2)) : null);
  var emp = about.employees && typeof about.employees === 'object' ? about.employees : (num(about.employees) !== null ? { count: about.employees } : null);
  if (emp) push('Employees', (num(emp.count) !== null ? fmtCnt(emp.count) : esc(emp.count)) + (emp.as_of ? ' <span class="sub">' + esc(emp.as_of) + '</span>' : '') + (emp.evidence ? '<span class="sub quote">“' + esc(emp.evidence) + '”</span>' : ''));
  push('First SEC filing', about.first_sec_filing ? esc(about.first_sec_filing) + ' <span class="sub">(IPO-date proxy)</span>' : null);
  push('Website', safeUrl(about.website) ? extLink(about.website, esc(String(about.website).replace(/^https?:\/\//i, '').replace(/\/$/, ''))) : null);
  push('EDGAR', safeUrl(about.edgar_url || fp.edgar_url) ? extLink(about.edgar_url || fp.edgar_url, 'company filings') + (n.cik ? ' <span class="sub">CIK ' + esc(n.cik) + '</span>' : '') : null);
  var desc = '';
  if (about.description) {
    var d = typeof about.description === 'object' ? obj(about.description) : { text: about.description };
    var src = d.accession || d.url ? '<span class="sub">From the 10-K, Item 1 ' + (d.url ? extLink(d.url, esc(d.accession || 'filing')) : esc(d.accession || '')) + '</span>' : '';
    desc = '<p class="dimp">' + esc(d.text || '') + '</p>' + src;
  } else if (about.description_short) desc = '<p class="dimp">' + esc(about.description_short) + '</p><span class="sub">Nasdaq company profile</span>';
  if (about.description && about.description_short && (typeof about.description !== 'object' || about.description.text !== about.description_short)) desc += '<p class="note">' + esc(about.description_short) + '</p>';
  var missing = Object.keys(p).length ? '' : '<p class="note">Profile enrichment has not run for this name yet (profile.py) — the facts shown come from fundamentals.json and the engine run.</p>';
  if (!facts.length && !desc) return section('About', '<div class="card empty">' + (missing || '<p class="note">No profile facts on record.</p>') + '</div>');
  return section('About', '<div class="card about">' + desc + (facts.length ? '<div class="facts">' + facts.join('') + '</div>' : '') + missing + (p.as_of ? '<p class="note">Profile as of ' + esc(p.as_of) + '.</p>' : '') + '</div>');
}
/* Generated prose from the filed numbers: fiscal year named, numbers only, no adjectives. Pure; '' without annual rows. */
function financialPerformance(record) {
  var fund = obj(record.fundamentals), ann = arr(fund.annual).filter(function (r) { return r && typeof r === 'object'; }), ttm = obj(fund.ttm), cur = fund.currency || 'USD';
  if (!ann.length) return '';
  var a = ann[ann.length - 1], prev = ann.length > 1 ? ann[ann.length - 2] : null, fy = 'fiscal ' + esc(a.fy), out = [];
  var unit = cur !== 'USD' ? ' (figures in ' + esc(cur) + ' as filed)' : '';
  if (num(a.revenue) !== null) out.push('In ' + fy + (a.period_end ? ' (ended ' + esc(a.period_end) + ')' : '') + ' revenue was ' + fmtBig(a.revenue) + (num(a.revenue_growth) !== null && prev ? ', ' + fmtPct(a.revenue_growth, 1, true) + ' on fiscal ' + esc(prev.fy) : '') + unit + '.');
  else out.push('In ' + fy + ' no revenue figure was filed' + unit + '.');
  var p = [];
  if (num(a.gross_margin) !== null) p.push('gross margin ' + fmtPct(a.gross_margin));
  if (num(a.operating_income) !== null) p.push('operating income ' + fmtBig(a.operating_income) + (num(a.operating_margin) !== null ? ' (' + fmtPct(a.operating_margin) + ' margin)' : ''));
  if (num(a.net_income) !== null) p.push('net income ' + fmtBig(a.net_income) + (num(a.net_margin) !== null ? ' (' + fmtPct(a.net_margin) + ' margin)' : '') + (num(a.net_income_growth) !== null && prev ? ', ' + fmtPct(a.net_income_growth, 1, true) + ' year over year' : ''));
  if (p.length) out.push(p.join('; ').replace(/^./, function (c) { return c.toUpperCase(); }) + '.');
  var c = [];
  if (num(a.ocf) !== null) c.push('operating cash flow ' + fmtBig(a.ocf) + (num(a.ocf_growth) !== null && prev ? ' (' + fmtPct(a.ocf_growth, 1, true) + ')' : ''));
  if (num(a.capex) !== null) c.push('capex ' + fmtBig(a.capex) + (num(a.capex_pct_rev) !== null ? ' (' + fmtPct(a.capex_pct_rev) + ' of revenue)' : ''));
  if (num(a.sbc) !== null) c.push('stock-based compensation ' + fmtBig(a.sbc) + (num(a.sbc_pct_ocf) !== null ? ' (' + fmtPct(a.sbc_pct_ocf) + ' of operating cash flow)' : ''));
  if (c.length) out.push(c.join('; ').replace(/^./, function (x) { return x.toUpperCase(); }) + '.');
  if (num(a.oe_conservative) !== null) out.push("Owner's earnings (operating cash flow − capex − stock-based compensation) were " + fmtBig(a.oe_conservative) + (num(a.oe_margin) !== null ? ', a ' + fmtPct(a.oe_margin) + ' margin' : '') + (num(a.oe_per_share) !== null ? ', ' + fmtMoney(a.oe_per_share) + ' per diluted share' : '') + (num(a.oe_per_share_growth) !== null && prev ? ' (' + fmtPct(a.oe_per_share_growth, 1, true) + ' on fiscal ' + esc(prev.fy) + ')' : '') + '.');
  if (num(ttm.revenue) !== null || num(ttm.oe_conservative) !== null) {
    var t = [];
    if (num(ttm.revenue) !== null) t.push('revenue ' + fmtBig(ttm.revenue) + (num(ttm.revenue_yoy) !== null ? ' (' + fmtPct(ttm.revenue_yoy, 1, true) + ' year over year)' : ''));
    if (num(ttm.net_income) !== null) t.push('net income ' + fmtBig(ttm.net_income) + (num(ttm.net_income_yoy) !== null ? ' (' + fmtPct(ttm.net_income_yoy, 1, true) + ')' : ''));
    if (num(ttm.ocf) !== null) t.push('operating cash flow ' + fmtBig(ttm.ocf) + (num(ttm.ocf_yoy) !== null ? ' (' + fmtPct(ttm.ocf_yoy, 1, true) + ')' : ''));
    if (num(ttm.oe_conservative) !== null) t.push("owner's earnings " + fmtBig(ttm.oe_conservative) + (num(ttm.oe_margin) !== null ? ' (' + fmtPct(ttm.oe_margin) + ' margin)' : '') + (num(ttm.oe_per_share) !== null ? ', ' + fmtMoney(ttm.oe_per_share) + ' per share' : ''));
    out.push('Over the twelve months to ' + esc(ttm.period_end || 'the latest quarter') + ': ' + t.join('; ') + '.');
  }
  if (num(a.shares_diluted) !== null) {
    var five = ann.length > 5 ? ann[ann.length - 6] : (ann.length > 1 ? ann[0] : null), span = five ? Number(a.fy) - Number(five.fy) : 0;
    var chg5 = five && num(five.shares_diluted) ? (num(a.shares_diluted) / num(five.shares_diluted) - 1) : null;
    out.push('Diluted shares were ' + fmtCnt(a.shares_diluted) + (num(a.shares_diluted_growth) !== null && prev ? ', ' + fmtPct(a.shares_diluted_growth, 1, true) + ' on fiscal ' + esc(prev.fy) : '') + (chg5 !== null && span > 0 ? ' and ' + fmtPct(chg5, 1, true) + ' over ' + span + ' years (fiscal ' + esc(five.fy) + ' → ' + esc(a.fy) + ')' : '') + '.');
  }
  var bs = [];
  if (num(a.cash) !== null) bs.push('cash ' + fmtBig(a.cash));
  if (num(a.total_debt) !== null) bs.push('total debt ' + fmtBig(a.total_debt));
  if (num(a.net_debt) !== null) bs.push('net debt ' + fmtBig(a.net_debt) + (num(a.net_debt_to_oe) !== null ? ' (' + fmtX(a.net_debt_to_oe) + " owner's earnings)" : ''));
  if (bs.length) out.push('At fiscal year end: ' + bs.join(', ') + '.');
  var cr = [];
  if (num(a.dividends_paid) !== null) cr.push('dividends ' + fmtBig(a.dividends_paid));
  if (num(a.buybacks) !== null) cr.push('buybacks ' + fmtBig(a.buybacks));
  if (num(a.acquisitions) !== null) cr.push('acquisitions ' + fmtBig(a.acquisitions));
  if (cr.length) out.push('Cash returned or deployed in ' + fy + ': ' + cr.join(', ') + '.');
  return out.join(' ');
}
function renderPerformance(record) {
  var text = financialPerformance(record);
  if (!text) return '';
  return section('Financial performance', '<div class="card"><p class="dimp">' + text + '</p><p class="note">Generated from the filed figures in fundamentals.json (EDGAR companyfacts) — see the Financials tab for the statements.</p></div>');
}
/* ---- Street (Nasdaq analyst data from profile.street): third-party, clearly labelled, never an input to the valuation.
   The Overview keeps a compact summary; the full section lives in the Forecast tab's Street sub-tab. */
function streetOf(record) { var p = obj(record.profile); return p.street && typeof p.street === 'object' && !Array.isArray(p.street) ? p.street : null; }
function streetCounts(st) {
  var b = num(st.buy), h = num(st.hold), s = num(st.sell), tot = (b || 0) + (h || 0) + (s || 0);
  return { buy: b, hold: h, sell: s, total: tot, analysts: num(st.analysts) !== null ? num(st.analysts) : (tot || null) };
}
function streetEmpty(record, title) {
  var p = obj(record.profile);
  return section(title || 'Street summary', '<div class="card empty"><p class="note">' + (Object.keys(p).length ? 'No analyst data on record for this name.' : 'Street consensus appears once profile.py has pulled the Nasdaq analyst data for this name.') + ' The Street\'s targets are shown only beside our hurdle prices and never enter the valuation.</p></div>');
}
/* The one paragraph both the summary card and the Street sub-tab open with. */
function streetParagraph(record, st) {
  var v = liveView(record), c = streetCounts(st), px = v.price, tm = num(st.target_mean), lo = num(st.target_low), hi = num(st.target_high), t = esc(obj(record.score).ticker || record.ticker || obj(record.row).ticker);
  var parts = [];
  parts.push((c.analysts !== null ? c.analysts + ' analyst' + (c.analysts === 1 ? '' : 's') + ' cover ' + t : 'Nasdaq lists analyst coverage for ' + t) + (st.consensus ? '; the consensus rating is <b>' + esc(st.consensus) + '</b>' : '') + '.');
  if (tm !== null) parts.push('The mean 12-month price target is <b class="mono">' + fmtMoney(tm) + '</b>' + (px ? ', <b class="' + signCls(tm - px) + '">' + fmtPts((tm / px - 1) * 100, 0) + '</b> vs ' + (v.is_live ? 'the last close ' : 'the price used ') + fmtMoney(px) : '') + (lo !== null || hi !== null ? ' (range ' + fmtMoney(lo) + ' – ' + fmtMoney(hi) + ')' : '') + '.');
  return parts.join(' ');
}
function bhsBar(c) {
  if (!c.total) return '';
  var w = function (x) { return ((x || 0) / c.total * 100).toFixed(1) + '%'; };
  return '<div class="bhs" role="img" aria-label="' + esc((c.buy || 0) + ' buy, ' + (c.hold || 0) + ' hold, ' + (c.sell || 0) + ' sell') + '"><i class="buy" style="width:' + w(c.buy) + '"></i><i class="hold" style="width:' + w(c.hold) + '"></i><i class="sell" style="width:' + w(c.sell) + '"></i></div>'
    + '<div class="bhsl"><span><i class="buy"></i>Buy ' + esc(c.buy !== null ? c.buy : '—') + '</span><span><i class="hold"></i>Hold ' + esc(c.hold !== null ? c.hold : '—') + '</span><span><i class="sell"></i>Sell ' + esc(c.sell !== null ? c.sell : '—') + '</span></div>';
}
function streetSourceNote(st) {
  return '<b>The Street\'s view, not ours.</b> Source: ' + esc(st.source || 'Nasdaq analyst endpoints') + (st.as_of ? ', pulled ' + esc(st.as_of) : '') + '. Third-party data shown for context beside our hurdle prices; nothing here enters the owner\'s-earnings valuation.';
}
function renderStreet(record) {
  var st = streetOf(record);
  if (!st) return streetEmpty(record, 'Street summary');
  var t = obj(record.score).ticker || record.ticker || obj(record.row).ticker, hp = hurdlePrices(record), c = streetCounts(st);
  var ours = hp[15] !== null || hp[20] !== null ? ' Our hurdle prices: ' + fmtMoney(hp[15]) + ' for 15% (Tier B), ' + fmtMoney(hp[20]) + ' for 20% (Tier A).' : '';
  return section('Street summary', '<div class="card street"><p class="dimp">' + streetParagraph(record, st) + ours + '</p>' + bhsBar(c)
    + '<p class="note"><a class="seefc" href="#' + esc(t) + '.forecast.street">See forecast ›</a> · ' + streetSourceNote(st) + '</p></div>');
}
function renderFilings(record) {
  var p = obj(record.profile), fp = obj(obj(record.fundamentals).profile);
  var filings = arr(p.filings).filter(function (f) { return f && typeof f === 'object'; });
  if (!filings.length) {
    var lf = obj(fp.latest_filings), keys = Object.keys(lf);
    if (!keys.length) return section('Filings', '<div class="card empty"><p class="note">' + (Object.keys(p).length ? 'No filings on record.' : 'The EDGAR filing feed appears once profile.py has run for this name.') + '</p></div>');
    filings = keys.map(function (form) { var d = obj(lf[form]); return { form: form, filed: d.filed, period: d.period, url: d.url, description: 'latest ' + form }; });
  }
  var rows = filings.slice(0, 20).map(function (f) {
    var items = arr(f.items).map(function (x) { return esc(x); }).join(', ');
    return '<tr><td class="mono">' + esc(f.filed) + '</td><td><b>' + esc(f.form) + '</b>' + (items ? ' <span class="sub">' + items + '</span>' : '') + '</td><td>' + esc(f.description || '') + (f.period ? ' <span class="sub">period ' + esc(f.period) + '</span>' : '') + '</td><td>' + (safeUrl(f.url) ? extLink(f.url, 'open') : '') + '</td></tr>';
  }).join('');
  return section('Filings', '<div class="card"><div class="twrap"><table class="mini filings"><thead><tr><th>Filed</th><th>Form</th><th>What</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div><p class="note">From EDGAR submissions' + (p.as_of ? ', as of ' + esc(p.as_of) : '') + (fp.eight_k_count_12m !== undefined && fp.eight_k_count_12m !== null ? ' · ' + esc(fp.eight_k_count_12m) + ' 8-Ks in the last 12 months' : '') + '.</p></div>');
}

function renderOverview(record) {
  var s = obj(record.score), n = obj(record.numbers), row = obj(record.row), diag = obj(n.diagnostics);
  var v = liveView(record), tier = v.tier, acc = TIER_ACCENT[tier] || '#9AA3B2', irr = v.irr;
  var atPx = (v.is_live ? 'at last close ' : 'at ') + fmtMoney(v.price);
  var scale = gaugeScale(irr), fill = irr !== null ? Math.max(0, Math.min(100, irr * 100 / scale * 100)) : 0, hurdleLeft = 15 / scale * 100;
  var glabel = irr !== null ? (Math.abs(irr * 100 - 15).toFixed(1) + ' pts ' + (irr * 100 - 15 >= 0 ? 'above' : 'below') + ' the 15% hurdle ' + atPx) : "No positive owner's earnings — no return can be computed";
  var chips = ['Tier ' + esc(tier) + ' · ' + (TIER_MEANING[tier] || '') + (v.is_live && v.tier !== v.scored_tier ? ' · live (scored ' + esc(v.scored_tier) + ')' : (v.is_live ? ' · live' : ''))];
  if (tierShiftChip(v)) chips.push('Tier ' + esc(v.scored_tier) + ' → ' + esc(v.tier) + ' at last close');
  if (s.moat_score !== null && s.moat_score !== undefined) chips.push('Moat ' + esc(s.moat_score) + '/10');
  if (s.cap_years !== null && s.cap_years !== undefined) chips.push('Advantage period ' + esc(s.cap_years) + ' yrs');
  if (s.confidence) chips.push('Confidence ' + esc(s.confidence) + (s.confidence_capped ? ' (capped)' : ''));
  if (modelFit(record) === 'misfit') chips.push('Sector model misfit — tier is soft');
  arr(s.overrides).forEach(function (o) { if (o && typeof o === 'object' && o.field) chips.push(esc(o.field) + ': ' + (o.kind === 'estimate' ? 'AI estimate' : 'filing override')); });
  if (s.tier_by_numbers && v.scored_tier !== s.tier_by_numbers) chips.push('Tier overridden ' + esc(s.tier_by_numbers) + '→' + esc(v.scored_tier) + ' by agent judgment');
  if (s.engine_release) chips.push('Engine ' + esc(s.engine_release));
  else if (n.engine_version) chips.push('Engine 5.3.x (pre-5.4 numbers)');
  var gauge = '<div class="card verdict"><div class="vmain"><div class="vgauge"><span class="vgl" style="color:' + acc + '">' + glabel + '</span>'
    + '<div class="gauge"><div class="gfill" style="width:' + fill.toFixed(1) + '%;background:' + acc + '"></div><div class="gtick" style="left:' + hurdleLeft.toFixed(1) + '%"></div></div>'
    + '<div class="gscale"><span style="left:0">0%</span><span class="gmid" style="left:' + hurdleLeft.toFixed(1) + '%">15% hurdle</span><span style="right:0">' + scale.toFixed(0) + '%</span></div></div></div>'
    + '<div class="chips">' + chips.map(function (c) { return '<span class="chip">' + c + '</span>'; }).join('') + '</div>'
    + '<p class="take">' + esc(s.one_liner || row.one_liner) + '</p></div>';
  var sp = obj(s.second_pass), p2 = '';
  if (sp.verdict === 'changed') p2 = '<div class="p2box"><b>↺ Revised by pass 2 · ' + esc(sp.date) + '</b><p>Tier ' + esc(sp.prior_tier) + ' → ' + esc(tier) + ' · Wtd IRR ' + fmtPct(sp.prior_weighted_irr) + ' → ' + fmtPct(irr) + ' · IV@15% ' + fmtMoney(sp.prior_iv_at_15) + ' → ' + fmtMoney(s.iv_at_15) + '</p><p>' + esc(sp.summary) + '</p></div>';
  else if (Object.keys(sp).length) p2 = '<div class="p2box"><b>✓ Pass 2 checked ' + esc(sp.date) + ' — no material change</b><p>' + esc(sp.summary) + '</p></div>';
  var up = v.upside, hp = hurdlePrices(record), px = v.price, iv15 = num(s.iv_at_15 !== undefined ? s.iv_at_15 : row.iv15);
  var tiles = [
    tile(v.is_live ? 'Last close' : 'Price', fmtMoney(px), '', v.is_live ? esc(v.price_date) + ' · scored at ' + fmtMoney(v.scored_price) : ''),
    tile('IV @15%', fmtMoney(iv15), px && iv15 !== null ? signCls(iv15 - px) : '', 'clears 15%' + (v.is_live ? ' at last close' : '')),
    tile('Price for 20%', fmtMoney(hp[20]), px && hp[20] !== null ? signCls(hp[20] - px) : '', 'Tier A hurdle'),
    tile('Price for 25%', fmtMoney(hp[25]), px && hp[25] !== null ? signCls(hp[25] - px) : '', 'Tier S hurdle'),
    tile('Upside @15%', up !== null ? fmtPts(up, 0) : '—', signCls(up), v.is_live && v.scored_upside !== null ? 'scored ' + fmtPts(v.scored_upside, 0) : ''),
    tile('Base-case IRR', fmtPct(v.irr_base), '', v.is_live && num(s.implied_irr_base_case) !== null ? 'scored ' + fmtPct(s.implied_irr_base_case) : ''),
    tile('OE yield', fmtPct(diag.oe_yield), '', 'base OE / price'),
    tile('Terminal value share', fmtPct(diag.tv_share_at_15), '', 'of IV @15%'),
    tile('Scenario spread', fmtX(diag.scenario_spread_iv15), '', 'super bull / super bear'),
    tile('Net debt / OE', fmtX(diag.net_debt_to_normalized_oe), '', fmtBig(s.net_debt_latest !== undefined && s.net_debt_latest !== null ? s.net_debt_latest : n.net_debt_latest))
  ].join('');
  var baseSrc = { ttm_json: 'TTM from ttm.py (10-Q YTD math)', agent_supplied_ttm_override: 'TTM pin (agent-supplied)', median_of_last_3_fy_oe_per_share: 'median of the last 3 fiscal years' }[s.base_source] || esc(s.base_source);
  var kn = '<div class="tiles">' + tiles + '</div><div class="card baseoe"><span class="k">Base owner\'s earnings</span><span class="bv mono">' + fmtMoney(s.base_oe_per_share) + '<span class="bu"> / share</span></span>'
    + '<p class="note">Basis: ' + baseSrc + '. Latest FY ' + fmtMoney(n.base_oe_latest_per_share) + '/sh · 3-yr median ' + fmtMoney(n.base_oe_normalized_per_share) + '/sh · growth blend ' + fmtPct(n.g_blend) + ' → start ' + fmtPct(n.g_base) + ' · terminal ' + fmtPct(n.g_terminal) + '.</p></div>';
  // scenarios
  var scn = Object.keys(obj(n.scenarios)).length ? obj(n.scenarios) : obj(s.scenarios), rows = '';
  LABELS.forEach(function (l) {
    var k = l[0], r = obj(scn[k]), scoredIrr = num(r.irr);
    var rIrr = v.is_live ? obj(v.scenarios[k]).irr : scoredIrr;
    if (rIrr === null || rIrr === undefined) rIrr = scoredIrr;
    var w = rIrr !== null ? Math.max(0, Math.min(100, rIrr * 100 / scale * 100)) : 0;
    var prob = num(r.prob) !== null ? Math.round(num(r.prob) * 100) + '%' : '—';
    var scoredH = v.is_live && scoredIrr !== null ? '<span>Scored IRR <b>' + fmtPct(scoredIrr) + '</b></span>' : '';
    rows += '<div class="scn"><div class="scnh"><span class="scnn"><i style="background:' + SCN_COLORS[k] + '"></i>' + l[1] + '<span class="prob">' + prob + '</span></span><span class="mono scni">' + fmtPct(rIrr) + '</span></div>'
      + '<div class="scnbar"><div class="scnfill" style="width:' + w.toFixed(1) + '%;background:' + acc + '"></div><div class="scntick" style="left:' + hurdleLeft.toFixed(1) + '%"></div></div>'
      + '<div class="scnsub"><span>Growth start <b>' + fmtPct(r.g_start) + '</b></span><span>OE multiple <b>' + fmtX(r.oe_mult, 2) + '</b></span><span>IV @15% <b>' + fmtMoney(r.iv_at_15) + '</b></span>' + scoredH + '</div></div>';
  });
  var sc = '<div class="card scncard">' + rows + '<div class="scnfoot"><span>Probability-weighted' + (v.is_live ? ' · at last close' : '') + '</span><span class="mono">IV ' + fmtMoney(iv15) + ' · IRR ' + fmtPct(irr) + (v.is_live ? ' <span class="scored">scored ' + fmtPct(v.scored_irr) + '</span>' : '') + '</span></div></div>';
  // moat
  var moat = num(s.moat_score), dots = '';
  if (moat !== null) { dots = '<span class="mdots">'; for (var i = 0; i < 10; i++) dots += '<i class="' + (i < Math.round(moat) ? 'on' : '') + '"></i>'; dots += '</span>'; }
  var mfor = s.moat_for, mag = arr(s.moat_against), cols;
  if (Array.isArray(mfor) && mfor.length) {
    cols = '<div class="mcols"><div class="mcol"><span class="mk pos">Strengths</span><ul>' + mfor.map(function (x) { return '<li><span class="sign pos">+</span><span>' + esc(x) + '</span></li>'; }).join('') + '</ul></div>'
      + '<div class="mcol"><span class="mk neg">Pressures</span><ul>' + mag.map(function (x) { return '<li><span class="sign neg">−</span><span>' + esc(x) + '</span></li>'; }).join('') + '</ul></div></div>';
  } else cols = '<p class="dimp">' + esc(s.moat_justification) + '</p>';
  var moatH = '<div class="card"><div class="moathead"><span class="moattitle"><h2>Moat</h2><span class="mono moatscore">' + esc(s.moat_score !== undefined && s.moat_score !== null ? s.moat_score : '—') + '/10</span>' + dots + '</span><span class="note">Advantage period <b class="mono">' + esc(s.cap_years !== undefined && s.cap_years !== null ? s.cap_years : '—') + ' yrs</b> · the moat sets how fast growth fades to ' + fmtPct(n.g_terminal) + '</span></div>' + cols + '<p class="note">' + (Array.isArray(mfor) && mfor.length ? esc(s.moat_justification) : '') + '</p></div>';
  // flags
  var flags = arr(s.fragility_flags), fl = '';
  if (flags.length) {
    var items = flags.map(function (f) { f = String(f); var code = f.split(':')[0].split(' ')[0], rest = f.indexOf(':') >= 0 ? f.slice(f.indexOf(':') + 1).trim() : ''; return '<li><code>' + esc(code) + '</code><span>' + esc(rest) + '</span></li>'; }).join('');
    fl = '<div class="card"><ul class="flags">' + items + '</ul><p class="note">Each flag is resolved in the write-up — see the Analysis tab.</p></div>';
  }
  var ov = renderOverrides(record);
  return gauge + p2 + renderAbout(record) + renderPerformance(record) + renderStreet(record) + renderFilings(record)
    + section('Key numbers', kn) + (ov ? section('Overrides', ov, 'Filing gaps filled by a judgment override — an override never replaces a filed value.') : '')
    + section('Scenarios', sc, 'IRR ' + atPx + ' for each case, against the 15% hurdle.' + (v.is_live ? " Live figures reprice the scored cash-flow paths at the last close; the scored IRR is the agent's verdict-date figure." : ''))
    + section('', moatH) + (flags.length ? section('Fragility flags <span class="fcount mono">' + flags.length + '</span>', fl) : '');
}

/* ---- Financials */
function derivedSup() { return '<sup title="derived: year-to-date minus prior year-to-date">†</sup>'; }
function renderFinancials(record) {
  var fund = record.fundamentals && typeof record.fundamentals === 'object' ? record.fundamentals : null, hist = arr(record.history), parts = [];
  if (fund) {
    var ann = arr(fund.annual), q = arr(fund.quarterly), ttm = obj(fund.ttm), cur = fund.currency || 'USD';
    var unitNote = 'Figures as filed with the SEC, in ' + esc(cur) + '.' + (cur !== 'USD' ? ' <b>Not USD</b> — the engine converts for the valuation; this tab shows the filings as filed.' : '');
    var warn = arr(fund.warnings).map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('');
    if (warn) unitNote += '<ul class="warnlist">' + warn + '</ul>';
    if (q.length) {
      var qlabels = q.map(function (r) { return r.label || r.period_end; });
      var qhead = qlabels.map(function (l) { return '<th class="num">' + esc(l) + '</th>'; }).join('');
      var qrow = function (name, key, f, skipBlank) {
        f = f || fmtBig;
        if (skipBlank && q.every(function (r) { return r[key] === null || r[key] === undefined; })) return '';
        return '<tr><th>' + name + '</th>' + q.map(function (r) { return '<td>' + f(r[key]) + (r[key + '_derived'] ? derivedSup() : '') + '</td>'; }).join('') + '</tr>';
      };
      var qpct = function (name, key) { return '<tr class="sub"><th>' + name + '</th>' + q.map(function (r) { var c = signCls(r[key]); return '<td' + (c ? ' class="' + c + '"' : '') + '>' + fmtPct(r[key], 1, true) + '</td>'; }).join('') + '</tr>'; };
      var qt = '<div class="twrap"><table class="fin"><thead><tr><th>Quarter</th>' + qhead + '</tr><tr class="sub"><th>Period end</th>' + q.map(function (r) { return '<td>' + esc(r.period_end) + '</td>'; }).join('') + '</tr></thead><tbody>'
        + qrow('Revenue', 'revenue') + qpct('Revenue growth (YoY)', 'revenue_yoy') + qrow('Gross margin', 'gross_margin', fmtPct) + qrow('Operating income', 'operating_income') + qrow('Net income', 'net_income') + qpct('Net income growth (YoY)', 'net_income_yoy') + qrow('EPS (diluted)', 'eps_diluted', fmtMoney)
        + qrow('Operating cash flow', 'ocf') + qrow('Capex', 'capex') + qrow('Stock-based comp', 'sbc') + qrow("Owner's earnings (cons.)", 'oe_conservative') + qpct("Owner's earnings growth (YoY)", 'oe_conservative_yoy') + qrow('Diluted shares', 'shares_diluted', fmtCnt)
        + qrow('Dividends paid', 'dividends_paid', fmtBig, true) + qrow('Buybacks', 'buybacks', fmtBig, true) + qrow('DPS declared', 'dps_declared', fmtMoney, true) + qrow('DPS paid', 'dps_paid', fmtMoney, true) + '</tbody></table></div>';
      var ttmH = '';
      if (Object.keys(ttm).length) {
        var sbcOcf = num(ttm.sbc) !== null && num(ttm.ocf) ? fmtPct(num(ttm.sbc) / num(ttm.ocf)) + ' of OCF' : '';
        ttmH = '<div class="tiles">' + tile('TTM revenue', fmtBig(ttm.revenue), '', num(ttm.revenue_yoy) !== null ? fmtPct(ttm.revenue_yoy, 1, true) + ' YoY' : '')
          + tile('TTM net income', fmtBig(ttm.net_income), '', num(ttm.net_income_yoy) !== null ? fmtPct(ttm.net_income_yoy, 1, true) + ' YoY' : '')
          + tile('TTM operating CF', fmtBig(ttm.ocf), '', num(ttm.ocf_yoy) !== null ? fmtPct(ttm.ocf_yoy, 1, true) + ' YoY' : '')
          + tile("TTM owner's earnings", fmtBig(ttm.oe_conservative), '', num(ttm.oe_per_share) !== null ? fmtMoney(ttm.oe_per_share) + ' / share' : '')
          + tile('TTM OE margin', fmtPct(ttm.oe_margin), '', 'through ' + esc(ttm.period_end))
          + tile('TTM SBC', fmtBig(ttm.sbc), '', sbcOcf) + '</div>';
      }
      parts.push(section('Quarterly', ttmH + '<div class="card">' + chartDiv('fin-q') + qt + '<p class="note">† derived as year-to-date minus the prior year-to-date in the same fiscal year (cash-flow lines are filed year-to-date only); Q4 = fiscal year minus nine months.</p></div>',
        'The last twelve fiscal quarters, filing-direct. This is the trend the annual history hides.'));
    }
    if (ann.length) {
      var head = ann.map(function (r) { return '<th class="num">FY' + esc(r.fy) + '</th>'; }).join('');
      var arow = function (name, key, f, cls) { f = f || fmtBig; return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th>' + name + '</th>' + ann.map(function (r) { return '<td>' + f(r[key]) + '</td>'; }).join('') + '</tr>'; };
      var apct = function (name, key) { return '<tr class="sub"><th>' + name + '</th>' + ann.map(function (r) { var c = signCls(r[key]); return '<td' + (c ? ' class="' + c + '"' : '') + '>' + fmtPct(r[key], 1, true) + '</td>'; }).join('') + '</tr>'; };
      var pend = '<tr class="sub"><th>Period end</th>' + ann.map(function (r) { return '<td>' + esc(r.period_end) + '</td>'; }).join('') + '</tr>';
      var inc = '<div class="twrap"><table class="fin"><thead><tr><th>Income statement</th>' + head + '</tr>' + pend + '</thead><tbody>'
        + arow('Revenue', 'revenue', null, 'strong') + apct('Revenue growth', 'revenue_growth') + arow('Cost of revenue', 'cogs') + arow('Gross profit', 'gross_profit') + apct('Gross margin', 'gross_margin') + arow('R&amp;D', 'rnd') + arow('SG&amp;A', 'sga') + arow('Operating income', 'operating_income', null, 'strong') + apct('Operating margin', 'operating_margin') + arow('Interest expense', 'interest_expense') + arow('Pretax income', 'pretax_income') + arow('Income tax', 'tax') + arow('Net income', 'net_income', null, 'strong') + apct('Net margin', 'net_margin') + apct('Net income growth', 'net_income_growth') + arow('EPS (diluted)', 'eps_diluted', fmtMoney) + apct('EPS growth', 'eps_diluted_growth') + arow('Diluted shares', 'shares_diluted', fmtCnt) + apct('Share count change', 'shares_diluted_growth') + '</tbody></table></div>';
      var cf = '<div class="twrap"><table class="fin"><thead><tr><th>Cash flow</th>' + head + '</tr></thead><tbody>'
        + arow('Operating cash flow', 'ocf', null, 'strong') + apct('OCF growth', 'ocf_growth') + arow('Capex', 'capex') + apct('Capex % revenue', 'capex_pct_rev') + arow('Depreciation &amp; amortization', 'da') + arow('Stock-based compensation', 'sbc') + apct('SBC % revenue', 'sbc_pct_rev') + apct('SBC % OCF', 'sbc_pct_ocf') + arow('Free cash flow (OCF − capex)', 'fcf') + arow("Owner's earnings (OCF − capex − SBC)", 'oe_conservative', null, 'strong') + apct("Owner's earnings margin", 'oe_margin') + apct("Owner's earnings growth", 'oe_conservative_growth') + arow('OE per share', 'oe_per_share', fmtMoney) + apct('OE/share growth', 'oe_per_share_growth') + arow('Dividends paid', 'dividends_paid') + arow('Buybacks', 'buybacks') + arow('Acquisitions', 'acquisitions') + arow('Investing cash flow', 'icf') + arow('Financing cash flow', 'fincf') + '</tbody></table></div>';
      var bs = '<div class="twrap"><table class="fin"><thead><tr><th>Balance sheet</th>' + head + '</tr></thead><tbody>'
        + arow('Cash &amp; equivalents', 'cash') + arow('Short-term investments', 'short_term_investments') + arow('Receivables', 'receivables') + arow('Inventory', 'inventory') + arow('Prepaids', 'prepaids') + apct('Prepaids % assets', 'prepaids_pct_assets') + arow('Current assets', 'assets_current') + arow('PP&amp;E (net)', 'ppe_net') + arow('Goodwill', 'goodwill') + apct('Goodwill % assets', 'goodwill_pct_assets') + arow('Intangibles', 'intangibles') + arow('Total assets', 'assets', null, 'strong') + arow('Current liabilities', 'liab_current') + arow('Deferred revenue', 'deferred_revenue') + arow('Total debt', 'total_debt', null, 'strong') + arow('Net debt (debt − cash)', 'net_debt') + arow('Operating lease liabilities', 'lease_liabilities') + arow('Total liabilities', 'liabilities') + arow("Shareholders' equity", 'equity', null, 'strong') + arow('Book value / share', 'book_value_per_share', fmtMoney) + arow('Current ratio', 'current_ratio', fmtX) + apct('Return on equity', 'roe') + apct('ROIC (proxy)', 'roic_proxy') + arow("Net debt / owner's earnings", 'net_debt_to_oe', fmtX) + '</tbody></table></div>';
      parts.push(section('Revenue &amp; profits', '<div class="card">' + chartDiv('fin-ann') + inc + '</div>', unitNote));
      parts.push(section("Cash flow &amp; owner's earnings", '<div class="card">' + chartDiv('fin-cf') + cf + '</div>', "Owner's earnings = operating cash flow − capex − stock-based compensation (SBC always treated as a real cost)."));
      parts.push(section('Margins', '<div class="card">' + chartDiv('fin-margins') + '</div>'));
      parts.push(section('Cash &amp; debt', '<div class="card">' + chartDiv('fin-cashdebt') + bs + '</div>', 'Debt is shown below the axis; the line is net debt. Operating leases are listed separately and are not in net debt (comparability across the universe).'));
      parts.push(section('Capital returned', '<div class="card">' + chartDiv('fin-capret') + '</div>', 'Cash actually paid out: buybacks, dividends, and acquisitions, per the cash-flow statement.'));
    }
  }
  if (!parts.length) {
    if (hist.length) {
      var rows = hist.slice(-10).map(function (r) {
        return '<tr><td>' + esc(r.fy_label) + '</td><td class="num mono">' + fmtBig(r.revenue) + '</td><td class="num mono">' + fmtBig(r.net_income) + '</td><td class="num mono">' + fmtBig(r.ocf) + '</td><td class="num mono">' + fmtBig(r.capex) + '</td><td class="num mono">' + fmtBig(r.sbc) + '</td><td class="num mono">' + fmtBig(r.oe_conservative) + '</td><td class="num mono">' + fmtBig(r.oe_maintenance) + '</td><td class="num mono">' + fmtCnt(r.shares_diluted) + '</td></tr>';
      }).join('');
      parts.push(section('Financial history (engine)', '<div class="card">' + chartDiv('fin-hist') + '<div class="twrap"><table class="mini"><thead><tr><th>FY</th><th class="num">Revenue</th><th class="num">Net income</th><th class="num">Op CF</th><th class="num">Capex</th><th class="num">SBC</th><th class="num">OE (cons)</th><th class="num">OE (maint)</th><th class="num">Shares</th></tr></thead><tbody>' + rows + '</tbody></table></div><p class="note">The extended statements appear once fundamentals.py has been run for this name.</p></div>'));
    } else parts.push('<div class="card"><p class="note">No financial history available.</p></div>');
  }
  return parts.join('');
}

/* ---- Dividends (fundamentals.json "dividends" block) */
function renderDividends(record) {
  var fund = obj(record.fundamentals), d = fund.dividends;
  if (!d || typeof d !== 'object' || Array.isArray(d)) return '<div class="card empty"><p class="note">Dividend enrichment has not run for this name yet — fundamentals.py adds a <code>dividends</code> block (declared / paid per-share facts, dividends paid, buybacks, issuance) once it is re-run.</p></div>';
  var price = num(d.price), pdate = d.price_date, dps = num(d.dps_ttm), freq = d.frequency || 'none', basis = d.dps_basis;
  var payer = freq !== 'none' && dps !== null && dps > 0;
  var priceNote = price !== null ? 'the last close ' + fmtMoney(price) + ' (' + esc(pdate) + ')' : 'the last close';
  var cashTiles = [
    tile('Buyback yield', fmtPct(d.buyback_yield), '', num(d.buybacks_ttm) !== null ? fmtBig(d.buybacks_ttm) + ' TTM' : 'no buyback filed'),
    tile('Net buyback yield', fmtPct(d.net_buyback_yield), signCls(d.net_buyback_yield), num(d.issuance_ttm) !== null ? 'buybacks − issuance ' + fmtBig(d.issuance_ttm) : 'buybacks − issuance'),
    tile('Shareholder yield', fmtPct(d.shareholder_yield), signCls(d.shareholder_yield), 'dividend + net buyback')
  ];
  var parts = [];
  if (!payer) {
    var paid = num(d.dividends_paid_ttm);
    var why = (paid === null || paid === 0) ? 'no dividend per-share fact or dividend payment in the filings' : 'no per-share dividend fact filed; cash dividends paid TTM ' + fmtBig(paid);
    parts.push('<div class="card nodiv"><span class="k">Dividend</span><span class="bv">No dividend</span><p class="note">' + why + '. Capital returned to shareholders comes through buybacks, if any — the yields below use ' + priceNote + '.</p></div>');
    parts.push('<div class="tiles">' + cashTiles.join('') + '</div>');
  } else {
    var g5 = num(d.dps_cagr_5y), g3 = num(d.dps_cagr_3y);
    var gsub = joinNonEmpty([g5 !== null ? '5-yr CAGR ' + fmtPct(g5, 1, true) : '', g3 !== null ? '3-yr CAGR ' + fmtPct(g3, 1, true) : ''], ' · ');
    var gy = num(d.growth_years), cut = d.last_cut_fy;
    var tiles = [
      tile('Dividend yield', fmtPct(d.dividend_yield), '', price !== null ? 'TTM DPS ÷ ' + fmtMoney(price) : 'TTM DPS ÷ last close'),
      tile('Annual dividend', fmtMoney(dps), '', basis ? 'TTM DPS · ' + esc(basis) : 'TTM DPS'),
      tile('Payout frequency', DIV_FREQ[freq] || esc(freq)),
      tile('Payout ratio (vs EPS)', fmtPct(d.payout_ratio_eps), '', 'TTM DPS ÷ diluted EPS'),
      tile("Payout vs owner's earnings", fmtPct(d.payout_ratio_oe), '', 'dividends paid ÷ OE (TTM)'),
      tile('Payout vs free cash flow', fmtPct(d.payout_ratio_fcf), '', 'dividends paid ÷ FCF (TTM)'),
      tile('Dividend growth (YoY)', fmtPct(d.dps_growth_yoy, 1, true), signCls(d.dps_growth_yoy), gsub),
      tile('Growth years', gy !== null ? String(Math.trunc(gy)) : '—', '', gy !== null ? (cut ? 'last cut FY' + esc(cut) : 'no cut in the filed history') : '')
    ].concat(cashTiles);
    parts.push('<div class="tiles">' + tiles.join('') + '</div>');
  }
  var ann = arr(d.annual_dps).filter(function (r) { return r && typeof r === 'object' && num(r.dps) !== null; });
  if (ann.length) parts.push(section('Dividend per share by fiscal year', '<div class="card">' + chartDiv('div-dps') + '<p class="note">Annual DPS summed from the filed per-share facts (' + esc(basis || 'declared') + '); hover a bar for the year-over-year change.</p></div>'));
  var hist = arr(d.history).filter(function (r) { return r && typeof r === 'object'; }).slice(0, 20);
  if (hist.length) {
    var rows = hist.map(function (r) { var x = num(r.dps); return '<tr><td class="mono">' + esc(r.period_end) + '</td><td class="num mono">' + ((x || 0) < 0.1 ? fmtMoney(x, 4) : fmtMoney(x)) + '</td><td>' + esc(r.kind) + '</td></tr>'; }).join('');
    parts.push(section('Dividend history', '<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Period end</th><th class="num">DPS</th><th>Basis</th></tr></thead><tbody>' + rows + '</tbody></table></div><p class="note">The last ' + hist.length + ' per-share facts, newest first.</p></div>'));
  }
  var notes = arr(d.notes).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
  var meta = num(d.shares_diluted) !== null ? 'Diluted shares ' + fmtCnt(d.shares_diluted) + ' · market cap ' + fmtBig(d.market_cap) : '';
  parts.push("<p class=\"note\">Filing-direct EDGAR figures: per-share dividend facts (declared or paid, as filed) and the cash-flow statement's dividends paid, buybacks and issuance; TTM is the last four filed quarters. Yields use " + priceNote + '. ' + meta + '</p>' + (notes ? '<ul class="warnlist">' + notes + '</ul>' : ''));
  return parts.join('');
}

/* ---- Segments (segments.json) */
function segTables(record) {
  var sg = obj(record.segments);
  var tables = arr(sg.tables).filter(function (t) { return t && typeof t === 'object' && arr(t.rows).length; });
  tables.sort(function (a, b) { return (a.periodicity === 'annual' ? 0 : 1) - (b.periodicity === 'annual' ? 0 : 1); });
  return tables.map(function (t) {
    var rows = arr(t.rows).filter(function (r) { return r && typeof r === 'object'; }).slice(0, 12);
    var name = function (r) { return String(r.label || r.member || ''); };
    rows = rows.filter(function (r) { return !ELIM_RX.test(name(r)); }).concat(rows.filter(function (r) { return ELIM_RX.test(name(r)); }));
    var periods = arr(t.periods), plabels = arr(t.period_labels).length ? arr(t.period_labels) : periods;
    return { t: t, rows: rows, periods: periods, plabels: plabels, tot: obj(t.total) };
  });
}
function renderSegments(record) {
  var sg = obj(record.segments), tables = segTables(record);
  if (!tables.length) return '<div class="card empty"><p class="note">No segment tables for this name (segments.json absent or empty — the filer may report a single segment or no XBRL segment axis).</p></div>';
  var cur = sg.currency || 'USD', parts = [];
  tables.forEach(function (T, ti) {
    var t = T.t, rows = T.rows, plabels = T.plabels, periods = T.periods, tot = T.tot, np = plabels.length, tvals = arr(tot.values);
    var head = plabels.map(function (l) { return '<th class="num">' + esc(l) + '</th>'; }).join('');
    var pend = periods.length && periods.join('\u0001') !== plabels.join('\u0001') ? periods.map(function (p) { return '<td>' + esc(p) + '</td>'; }).join('') : '';
    var body = '';
    rows.forEach(function (r) {
      var cells = '', gro = '', shr = '';
      for (var j = 0; j < np; j++) {
        cells += '<td>' + fmtBig(get(r.values, j)) + (get(r.derived, j) ? '<sup title="derived: year-to-date minus prior year-to-date, or total minus the other segments">†</sup>' : '') + '</td>';
        var c = signCls(get(r.growth_yoy, j));
        gro += '<td' + (c ? ' class="' + c + '"' : '') + '>' + fmtPct(get(r.growth_yoy, j), 1, true) + '</td>';
        shr += '<td>' + fmtPct(get(r.share_of_total, j), 0) + '</td>';
      }
      body += '<tr><th>' + esc(r.label || r.member) + '</th>' + cells + '</tr><tr class="sub"><th>YoY growth</th>' + gro + '</tr><tr class="sub share"><th>Share of total</th>' + shr + '</tr>';
    });
    var hasTot = tvals.some(function (x) { return num(x) !== null; });
    if (hasTot) { body += '<tr class="strong"><th>Total <span class="sub">(' + esc(tot.basis || '') + ')</span></th>'; for (var j = 0; j < np; j++) body += '<td>' + fmtBig(get(tvals, j)) + '</td>'; body += '</tr>'; }
    var tbl = '<div class="twrap"><table class="fin segt"><thead><tr><th>' + esc(t.concept || 'Segment') + '</th>' + head + '</tr>' + (pend ? '<tr class="sub"><th>Period end</th>' + pend + '</tr>' : '') + '</thead><tbody>' + body + '</tbody></table></div>';
    var span = np > 1 ? esc(plabels[0]) + ' – ' + esc(plabels[np - 1]) : esc(np ? plabels[0] : '');
    var title = esc(t.label || 'Revenue by segment') + ' <span class="note">· ' + esc(t.periodicity || '') + ' · ' + span + '</span>';
    parts.push(section(title, '<div class="card">' + chartDiv('seg-' + ti) + tbl + '<p class="note">Stacked bars are the segments; the thin outline is the ' + esc(tot.basis || 'total') + '. Share of total and YoY growth are plain ratios of the filed values; † marks a derived cell. Figures in ' + esc(cur) + ' as filed.</p></div>'));
  });
  var fl = arr(sg.filings).filter(function (f) { return f && typeof f === 'object'; }).map(function (f) { return esc(f.form) + ' ' + esc(f.period); }).join(', ');
  var warn = arr(sg.warnings).map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('');
  parts.push('<p class="note">Source: ' + esc(sg.source || '') + (fl ? ' — ' + fl : '') + '. As of ' + esc(sg.as_of || '') + '.</p>' + (warn ? '<ul class="warnlist">' + warn + '</ul>' : ''));
  return parts.join('');
}

/* ---- Forecast: three sub-tabs (owner decision, 2026-10-14 night) — DCF (ours), Street (Nasdaq analyst data,
   third-party, never an input), Analysts (coverage and rating history). Hash form: #T.forecast (DCF),
   #T.forecast.street, #T.forecast.analysts. */
var SUBTABS = [['dcf', 'DCF'], ['street', 'Street'], ['analysts', 'Analysts']];
var SUB_KEYS = SUBTABS.map(function (t) { return t[0]; });
var FC_YEARS = [1, 2, 3, 5, 10, 15];

/* Filed OE/share history, oldest first, last 10 fiscal years: fundamentals.annual.oe_per_share; a null cell is
   filled by the ratio of the filed OE and diluted shares (display arithmetic on two filed values), from the
   annual row or, failing that, the engine CSV row for the same fiscal year; without fundamentals the engine
   CSV alone. Leading empty years are dropped. */
function oeHistory(record) {
  var fund = obj(record.fundamentals), ann = arr(fund.annual).filter(function (r) { return r && typeof r === 'object'; }), out = [];
  var ps = function (r) { var v = num(r.oe_per_share); if (v === null && num(r.oe_conservative) !== null && num(r.shares_diluted)) v = num(r.oe_conservative) / num(r.shares_diluted); return v; };
  var hist = arr(record.history).filter(function (r) { return r && typeof r === 'object'; });
  if (ann.length) ann.forEach(function (r) {
    var fy = String(r.fy || r.period_end || ''), v = ps(r);
    if (v === null) hist.forEach(function (h) { if (v === null && String(h.fy_label) === fy) v = ps(h); }); // the engine CSV for a year the enrichment left blank
    out.push({ fy: fy, v: v });
  });
  else hist.forEach(function (r) { out.push({ fy: String(r.fy_label || r.period_end || ''), v: ps(r) }); });
  while (out.length && out[0].v === null) out.shift();
  return out.slice(-10);
}
function yoy(vals) { // growth when the prior value is positive; null otherwise (a ratio on a negative base has no sign)
  return vals.map(function (v, i) { var p = i ? vals[i - 1] : null; return v !== null && p !== null && p > 0 ? v / p - 1 : null; });
}
/* The joined series behind the two DCF charts: history labels then the 15 projection years. Forecast series carry
   the engine's base OE/share at the last history position so the dashed lines start from the base year. The
   weighted growth is the year-over-year change of the stored weighted path (no weighted growth path is stored);
   bear / bull growth are the stored growth paths. Null without forecast.paths. */
function oeForecastSeries(record) {
  var fc = obj(record.forecast), paths = obj(fc.paths), gp = obj(fc.growth_paths), s = obj(record.score), n = obj(record.numbers);
  var w = arr(paths.weighted).map(num); if (!w.length) return null;
  var base = num(s.base_oe_per_share !== undefined ? s.base_oe_per_share : n.base_oe_per_share);
  var hist = oeHistory(record); if (!hist.length) hist = [{ fy: 'Base', v: base }];
  var H = hist.length, N = w.length, lastFy = hist[H - 1].fy, fyNum = /^\d{4}$/.test(lastFy) ? Number(lastFy) : null;
  var labels = hist.map(function (h) { return h.fy; }), fcLabels = [];
  for (var i = 1; i <= N; i++) fcLabels.push(fyNum !== null ? String(fyNum + i) : '+' + i);
  var pad = function (vals, withBase) { var o = []; for (var k = 0; k < H - 1; k++) o.push(null); o.push(withBase ? base : null); arr(vals).forEach(function (v) { o.push(num(v)); }); while (o.length < H + N) o.push(null); return o.slice(0, H + N); };
  var histVals = hist.map(function (h) { return h.v; }); while (histVals.length < H + N) histVals.push(null);
  var wg = w.map(function (v, i) { var p = i ? w[i - 1] : base; return v !== null && p !== null && p > 0 ? v / p - 1 : null; });
  var g = function (k) { return arr(gp[k]).map(num); };
  return { labels: labels.concat(fcLabels), fcLabels: fcLabels, hist: hist, histVals: histVals, base: base, baseIndex: H - 1, H: H, N: N,
    weighted: pad(w, true), bear: pad(paths.bear, true), bull: pad(paths.bull, true), super_bear: pad(paths.super_bear, true), super_bull: pad(paths.super_bull, true),
    raw: { weighted: w, bear: arr(paths.bear).map(num), bull: arr(paths.bull).map(num), super_bear: arr(paths.super_bear).map(num), super_bull: arr(paths.super_bull).map(num) },
    histGrowth: yoy(hist.map(function (h) { return h.v; })), wGrowth: wg, bearGrowth: g('bear'), bullGrowth: g('bull') };
}
function hal(title, cols, rows, note) { // High / Avg / Low table
  var head = cols.map(function (c) { return '<th class="num">' + c + '</th>'; }).join('');
  var body = rows.map(function (r) { return '<tr' + (r.strong ? ' class="strong"' : '') + '><th>' + r.name + '</th>' + r.cells.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('');
  return '<div class="twrap"><table class="fin hal"><thead><tr><th>' + title + '</th>' + head + '</tr></thead><tbody>' + body + '</tbody></table></div>' + (note ? '<p class="note">' + note + '</p>' : '');
}
function renderForecastDCF(record) {
  var s = obj(record.score), n = obj(record.numbers), fc = obj(record.forecast), row = obj(record.row);
  var hasScn = Object.keys(obj(n.scenarios)).length || Object.keys(obj(s.scenarios)).length || Object.keys(obj(fc.sensitivity)).length;
  if (!hasScn) return "<div class=\"card empty\"><p class=\"note\">No projection: the engine found no positive normalized owner's earnings (Tier F), so there is no cash-flow path to discount.</p></div>";
  var parts = [], inp = Object.keys(obj(fc.inputs)).length ? obj(fc.inputs) : obj(n.inputs);
  var gterm = inp.g_terminal !== undefined ? inp.g_terminal : (fc.g_terminal !== undefined ? fc.g_terminal : n.g_terminal);
  var paths = obj(fc.paths), gpaths = obj(fc.growth_paths), base = num(s.base_oe_per_share !== undefined ? s.base_oe_per_share : n.base_oe_per_share);
  var capYears = s.cap_years !== undefined ? s.cap_years : fc.cap_years, moat = s.moat_score !== undefined ? s.moat_score : row.moat;
  var J = oeForecastSeries(record);
  if (J) {
    var yl = function (y) { return 'Year ' + y + (J.fcLabels[y - 1] && J.fcLabels[y - 1].charAt(0) !== '+' ? ' <span class="sub">FY' + esc(J.fcLabels[y - 1]) + '</span>' : ''); };
    var cell = function (vals, y) { return '<span class="mono">' + fmtMoney(get(vals, y - 1)) + '</span>'; };
    var t1 = hal("OE / share", FC_YEARS.map(yl), [
      { name: 'High <span class="sub">super bull</span>', cells: FC_YEARS.map(function (y) { return cell(J.raw.super_bull, y); }) },
      { name: 'Avg <span class="sub">probability-weighted</span>', strong: true, cells: FC_YEARS.map(function (y) { return cell(J.raw.weighted, y); }) },
      { name: 'Low <span class="sub">super bear</span>', cells: FC_YEARS.map(function (y) { return cell(J.raw.super_bear, y); }) }]);
    parts.push(section("Owner's earnings per share — history and forecast", '<div class="card">' + chartDiv('fc-oe') + t1
      + '<p class="note">Solid line: filed owner\'s earnings per diluted share by fiscal year' + (arr(obj(record.fundamentals).annual).length ? ' (fundamentals.json)' : ' (engine history CSV)') + '. Dashed lines from the base year: the engine\'s projection — base ' + fmtMoney(base) + '/share (' + esc({ ttm_json: 'TTM', agent_supplied_ttm_override: 'TTM pin', median_of_last_3_fy_oe_per_share: '3-year median' }[s.base_source] || s.base_source || 'engine base') + ') grown along each scenario\'s path; the bold dashed line is the probability-weighted path whose IRR is the headline, the shaded band runs from super bear to super bull. Year-15 flow carries a Gordon terminal value at ' + fmtPct(gterm) + ' growth.' + (fc.replayed ? ' Paths replayed from the recorded run inputs through the engine (pre-5.4 run).' : '') + '</p></div>', 'What the DCF actually discounts, against what was filed.'));
    var gy = [1, 2, 3], gcell = function (vals, y) { var v = get(vals, y - 1); return '<span class="mono ' + signCls(v) + '">' + fmtPct(v, 1, true) + '</span>'; };
    var hasG = J.bearGrowth.length && J.bullGrowth.length;
    var t2 = hal('OE / share growth', gy.map(yl), [
      { name: 'High <span class="sub">bull growth path</span>', cells: gy.map(function (y) { return hasG ? gcell(J.bullGrowth, y) : '—'; }) },
      { name: 'Avg <span class="sub">weighted path, YoY</span>', strong: true, cells: gy.map(function (y) { return gcell(J.wGrowth, y); }) },
      { name: 'Low <span class="sub">bear growth path</span>', cells: gy.map(function (y) { return hasG ? gcell(J.bearGrowth, y) : '—'; }) }]);
    parts.push(section("Owner's earnings growth", '<div class="card">' + chartDiv('fc-oegrowth') + t2
      + '<p class="note">Historical bars: year-over-year change in the filed OE/share (blank where the prior year was not positive). Forecast bars: the year-over-year change of the probability-weighted path (year 1 is measured from the base, so it also carries the scenarios\' OE level multiples); the error bar runs from the bear to the bull growth path for the same year' + (hasG ? '' : ' (no growth paths stored for this run)') + '.</p></div>'));
  }
  if (arr(paths.weighted).length) {
    parts.push(section("Owner's earnings per share — the five paths", '<div class="card">' + chartDiv('fc-paths') + '<p class="note">Base ' + fmtMoney(base) + "/share × each scenario's OE multiple, grown along its growth path. The weighted line is the probability-weighted path whose IRR is the headline. Year-15 flow carries a Gordon terminal value at " + fmtPct(gterm) + ' growth.' + (fc.replayed ? ' Paths replayed from the recorded run inputs through the engine (pre-5.4 run).' : '') + '</p></div>'));
    if (arr(gpaths.base).length) parts.push(section('Growth fade', '<div class="card">' + chartDiv('fc-growth') + '<p class="note">Growth holds for 2 years, then converges linearly to the ' + fmtPct(gterm) + ' terminal rate over the competitive advantage period of ' + esc(capYears) + ' years (moat ' + esc(moat) + '/10 → CAP = 2 + 1.3 × moat).</p></div>'));
  } else parts.push('<div class="card"><p class="note">No stored projection paths for this run — the 15-year paths appear after the next engine run (5.4+) or when the data layer replays them.</p></div>');
  var sens = sensitivity(record), lv = liveView(record), price = lv.price, pxWord = lv.is_live ? 'the last close' : "today's price";
  var head = [10, 12, 15, 20, 25].map(function (r) { return '<th class="num">IV @' + r + '%</th>'; }).join(''), rows = '', anyFloor = false;
  LABELS.concat([['weighted', 'Probability-weighted']]).forEach(function (l) {
    var k = l[0], r = obj(sens[k]), cells = '';
    [10, 12, 15, 20, 25].forEach(function (rate) { var x = r[rate]; var cls = x !== null && x !== undefined && price && x >= price ? 'pos' : (x !== null && x !== undefined ? 'neg' : ''); cells += '<td class="num mono ' + cls + '">' + fmtMoney(x) + '</td>'; });
    var prob = k !== 'weighted' ? num(obj(obj(n.scenarios)[k] || obj(s.scenarios)[k]).prob) : null;
    var scoredIrr = num(r.irr), irrCell, sf = r.irr_at_floor ? ' ' + floorSup('the scored IRR solver stopped at its floor') : '';
    if (r.irr_at_floor) anyFloor = true;
    if (lv.is_live) {
      var liveIrr = k === 'weighted' ? lv.irr : (num(r.irr_live) !== null ? num(r.irr_live) : obj(lv.scenarios[k]).irr);
      var lf = r.irr_live_at_floor ? ' ' + floorSup('the live IRR solver stopped at its floor — the last close did not improve this case; the figure is a bound') : '';
      if (r.irr_live_at_floor) anyFloor = true;
      irrCell = '<td class="num mono' + (r.irr_live_at_floor ? ' atfloor' : '') + '">' + (liveIrr !== null && liveIrr !== undefined ? fmtPct(liveIrr) : fmtPct(scoredIrr)) + lf + '<span class="scored">scored ' + fmtPct(scoredIrr) + sf + '</span></td>';
    } else irrCell = '<td class="num mono' + (r.irr_at_floor ? ' atfloor' : '') + '">' + fmtPct(scoredIrr) + sf + '</td>';
    rows += '<tr class="' + (k === 'weighted' ? 'strong' : '') + '"><th>' + l[1] + (prob !== null ? ' <span class="prob">' + Math.round(prob * 100) + '%</span>' : '') + '</th>' + cells + irrCell + '</tr>';
  });
  var irrHead = (lv.is_live ? 'IRR at last close ' : 'IRR at ') + fmtMoney(price);
  parts.push(section('Value at every discount rate', '<div class="card"><div class="twrap"><table class="fin"><thead><tr><th>Scenario</th>' + head + '<th class="num">' + irrHead + '</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
    + '<p class="note">Each cell is the price at which that scenario returns that rate. Green = at or above ' + pxWord + '. The 15% column is the hurdle; 20% and 25% are the Tier A and Tier S prices.' + (lv.is_live ? ' The IRR column reprices each scored path at the last close (' + esc(lv.price_date) + '); the muted figure is the scored IRR at ' + fmtMoney(lv.scored_price) + ' on ' + esc(lv.scored_date) + '.' : '') + (anyFloor ? ' <b>At floor</b> marks an IRR the solver clamped at its floor: that figure is a bound, not a solved return, so a floored live figure above the scored one is not an improvement at the last close.' : '') + '</p></div>', 'Sensitivity of value to the return you demand.'));
  var hp = hurdlePrices(record);
  var hpTile = function (k, label) { return tile(label, fmtMoney(hp[k]), hp[k] !== null && price ? signCls(hp[k] - price) : ''); };
  var tiles = hpTile(15, 'Price for 15% (Tier B)') + hpTile(20, 'Price for 20% (Tier A)') + hpTile(25, 'Price for 25% (Tier S)')
    + tile(lv.is_live ? 'Last close' : "Today's price", fmtMoney(price), '', lv.is_live ? esc(lv.price_date) + ' · scored at ' + fmtMoney(lv.scored_price) : '');
  var band = '', sb = obj(lv.scenarios.bear).irr, su = obj(lv.scenarios.bull).irr, ff = floorFlags(record, lv.is_live);
  if (sb === undefined) sb = lv.irr_bear; if (su === undefined) su = lv.irr_bull;
  if (sb !== null && sb !== undefined && su !== null && su !== undefined) {
    var tb = lv.tier_bear || tierForIrr(sb), tu = lv.tier_bull || tierForIrr(su), ovr = s.tier_final && s.tier_by_numbers && s.tier_final !== s.tier_by_numbers ? ' → ' + esc(s.tier_final) + ' after agent override' : '';
    var headline = lv.is_live ? 'headline tier <b>' + esc(lv.tier) + '</b> at the last close (scored ' + esc(s.tier_by_numbers) + ' on the weighted path' + ovr + ')' : 'headline tier ' + esc(s.tier_by_numbers) + ' on the weighted path' + ovr;
    band = '<p class="note">Tier band' + (lv.is_live ? ' at the last close' : '') + ': bear case <b>' + esc(tb) + '</b> (' + fmtPct(sb) + (ff.bear ? ', ' + floorSup() : '') + ') to bull case <b>' + esc(tu) + '</b> (' + fmtPct(su) + (ff.bull ? ', ' + floorSup() : '') + '); ' + headline + (ff.weighted ? ' — the weighted IRR sits at the solver\'s floor' : '') + '. Size any position to the bear end.</p>';
  }
  parts.push(section('Hurdle prices', '<div class="tiles">' + tiles + '</div>' + band, 'The price at which the probability-weighted path returns each hurdle. Green = ' + pxWord + ' is below it (the hurdle clears).'));
  var gc = Object.keys(obj(fc.growth_components)).length ? obj(fc.growth_components) : obj(n.growth_components);
  var gca = fc.growth_components_adjusted ? obj(fc.growth_components_adjusted) : obj(n.growth_components_adjusted), hasAdj = Object.keys(gca).length > 0;
  var comp = [['rev_cagr_5y', 'Revenue CAGR 5y'], ['rev_cagr_3y', 'Revenue CAGR 3y'], ['rev_yoy_latest', 'Latest revenue YoY'], ['oe_ps_cagr_2y', 'OE/share CAGR 2y']].map(function (c) { return '<tr><th>' + c[1] + '</th><td class="num mono">' + fmtPct(gc[c[0]]) + '</td><td class="num mono">' + (hasAdj ? fmtPct(gca[c[0]]) : '—') + '</td></tr>'; }).join('');
  var pick = function (k) { return fc[k] !== undefined && fc[k] !== null ? fc[k] : n[k]; };
  var method = '<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Growth signal</th><th class="num">Raw</th><th class="num">Share-adjusted</th></tr></thead><tbody>' + comp
    + '<tr class="strong"><th>Blend (median)</th><td class="num mono">' + fmtPct(pick('g_blend')) + '</td><td class="num mono">→ start ' + fmtPct(pick('g_base')) + '</td></tr></tbody></table></div>'
    + '<p class="note">Share-count CAGR ' + fmtPct(pick('share_cagr')) + ' → adjustment ' + fmtPct(pick('share_count_adj'), 1, true) + ' (' + esc(pick('share_adj_basis') || 'applied to the blend (pre-5.4 engine)') + '). Scenario offsets ' + esc(JSON.stringify(inp.offsets || null)) + ' pp and OE multiples ' + esc(JSON.stringify(inp.mults || null)) + ' with probabilities ' + esc(JSON.stringify(inp.probs || null)) + '. Start growth is capped at 35% (base) / 50% (scenario) — see README Fixes &amp; lessons.</p></div>';
  parts.push(section('How growth was set', method));
  return parts.join('');
}

/* ---- Street sub-tab helpers (pure) */
function gaugeSvg(c) { // semicircle Sell → Hold → Buy; needle at (buy + ½ hold) / total
  if (!c.total) return '';
  var p = ((c.buy || 0) + 0.5 * (c.hold || 0)) / c.total, cx = 100, cy = 100, r = 80;
  var arc = function (a0, a1, color) { var x0 = cx + r * Math.cos(Math.PI - a0 * Math.PI), y0 = cy - r * Math.sin(Math.PI - a0 * Math.PI), x1 = cx + r * Math.cos(Math.PI - a1 * Math.PI), y1 = cy - r * Math.sin(Math.PI - a1 * Math.PI); return '<path d="M' + x0.toFixed(1) + ',' + y0.toFixed(1) + ' A' + r + ',' + r + ' 0 0 1 ' + x1.toFixed(1) + ',' + y1.toFixed(1) + '" fill="none" stroke="' + color + '" stroke-width="14" stroke-linecap="butt"/>'; };
  var nx = cx + (r - 6) * Math.cos(Math.PI - p * Math.PI), ny = cy - (r - 6) * Math.sin(Math.PI - p * Math.PI);
  return '<svg class="sgauge" viewBox="0 0 200 118" role="img" aria-label="' + esc('Consensus needle at ' + Math.round(p * 100) + '% of the way from Sell to Buy') + '">' + arc(0, 1 / 3, '#FF8A8A') + arc(1 / 3, 2 / 3, '#fbbf24') + arc(2 / 3, 1, '#5BD69C')
    + '<line x1="' + cx + '" y1="' + cy + '" x2="' + nx.toFixed(1) + '" y2="' + ny.toFixed(1) + '" stroke="#ECEEF2" stroke-width="3" stroke-linecap="round"/><circle cx="' + cx + '" cy="' + cy + '" r="5" fill="#ECEEF2"/>'
    + '<text x="14" y="112" text-anchor="start">Sell</text><text x="100" y="12" text-anchor="middle">Hold</text><text x="186" y="112" text-anchor="end">Buy</text></svg>';
}
function qParse(period) { // "Q1 2026" / "Q1 FY2025" / "2026-Q1" → {q, y}
  var s = String(period || ''), m = /Q([1-4])/i.exec(s), y = /(\d{4})/.exec(s);
  return m && y ? { q: Number(m[1]), y: Number(y[1]) } : null;
}
function fyParse(period) { var m = /(\d{4})/.exec(String(period || '')); return m ? Number(m[1]) : null; }
function epsAnnualHist(record) { return arr(obj(record.fundamentals).annual).filter(function (r) { return r && typeof r === 'object' && num(r.eps_diluted) !== null; }).map(function (r) { return { fy: String(r.fy || ''), v: num(r.eps_diluted), g: num(r.eps_diluted_growth), r: r }; }); }
function growthCell(v) { return '<span class="' + signCls(v) + '">' + fmtPct(v, 1, true) + '</span>'; }
function epsTile(label, f, from, fromLabel) {
  var c = f ? num(f.consensus) : null, g = c !== null && from !== null && from > 0 ? c / from - 1 : null;
  return tile(label + (f && f.period ? ' <span class="sub">' + esc(f.period) + '</span>' : ''), fmtMoney(c), g !== null ? signCls(g) : '', c === null ? 'no consensus' : joinNonEmpty([from !== null ? 'from ' + fmtMoney(from) + (fromLabel ? ' (' + fromLabel + ')' : '') : '', g !== null ? '<b class="' + signCls(g) + '">' + fmtPct(g, 1, true) + '</b>' : ''], ' · '));
}
function renderForecastStreet(record) {
  var st = streetOf(record);
  if (!st) return streetEmpty(record, 'Stock price forecast');
  var v = liveView(record), c = streetCounts(st), px = v.price, parts = [], pxWord = v.is_live ? 'last close' : 'price used';
  var fund = obj(record.fundamentals), annH = epsAnnualHist(record), qH = arr(fund.quarterly).filter(function (r) { return r && typeof r === 'object'; });
  // (1) stock price forecast
  var hasPx = arr(obj(record.prices).weekly).length > 1 || arr(obj(record.prices).daily_1y).length > 1;
  parts.push(section('Stock price forecast', '<div class="card street"><p class="dimp">' + streetParagraph(record, st) + '</p><div class="sgrow"><div>' + gaugeSvg(c) + '<p class="note">Needle at (buy + ½ hold) ÷ (buy + hold + sell). Nasdaq publishes buy / hold / sell counts only — there is no strong-buy / strong-sell split.</p></div>'
    + '<div class="sgfan">' + (hasPx ? '<div class="fanchart" data-cid="street-fan"></div><p class="note">Past year of closes, then the Street\'s low / mean / high 12-month targets fanned out from the ' + pxWord + '.</p>' : '<p class="note">No price history pulled for this name yet (prices.py) — the fan chart appears once it exists.</p>') + '</div></div></div>'));
  // (2) price target table
  var pt = function (name, x) { x = num(x); return '<tr><th>' + name + '</th><td class="num mono">' + fmtMoney(x) + '</td><td class="num mono ' + (px && x !== null ? signCls(x - px) : '') + '">' + (px && x !== null ? fmtPts((x / px - 1) * 100, 1) : '—') + '</td></tr>'; };
  parts.push(section('Price target', '<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>12-month target</th><th class="num">Price</th><th class="num">vs ' + pxWord + ' ' + fmtMoney(px) + '</th></tr></thead><tbody>' + pt('Low', st.target_low) + pt('Average', st.target_mean) + pt('High', st.target_high) + '</tbody></table></div><p class="note">Nasdaq publishes no median target, so none is shown. Our hurdle prices for comparison: ' + fmtMoney(hurdlePrices(record)[15]) + ' for a 15% return, ' + fmtMoney(hurdlePrices(record)[20]) + ' for 20%.' + (st.target_1y_nasdaq_summary ? ' ' + esc(st.target_1y_nasdaq_summary) : '') + '</p></div>'));
  // (3) analyst ratings
  var hist = arr(st.history).filter(function (r) { return r && typeof r === 'object'; }).slice().sort(function (a, b) { return String(a.date) < String(b.date) ? -1 : String(a.date) > String(b.date) ? 1 : 0; });
  var ratingP = '<p class="dimp">' + (c.total ? 'Of the ' + c.total + ' ratings Nasdaq lists, ' + (c.buy || 0) + ' are buy, ' + (c.hold || 0) + ' hold and ' + (c.sell || 0) + ' sell' + (st.consensus ? ' — consensus <b>' + esc(st.consensus) + '</b>' : '') + '.' : 'No rating counts on record.') + '</p>';
  var trendT = hist.length ? '<div class="twrap"><table class="mini"><thead><tr><th>Month</th><th class="num">Buy</th><th class="num">Hold</th><th class="num">Sell</th><th class="num">Total</th><th class="num">Mean target</th></tr></thead><tbody>'
    + hist.slice(-12).reverse().map(function (r) { var cc = streetCounts(r); return '<tr><td class="mono">' + esc(r.date) + (r.consensus ? ' <span class="sub">' + esc(r.consensus) + '</span>' : '') + '</td><td class="num mono">' + esc(cc.buy !== null ? cc.buy : '—') + '</td><td class="num mono">' + esc(cc.hold !== null ? cc.hold : '—') + '</td><td class="num mono">' + esc(cc.sell !== null ? cc.sell : '—') + '</td><td class="num mono">' + (cc.total || '—') + '</td><td class="num mono">' + fmtMoney(r.mean_target) + '</td></tr>'; }).join('') + '</tbody></table></div>' : '<p class="note">No rating history on record.</p>';
  parts.push(section('Analyst ratings', '<div class="card">' + ratingP + bhsBar(c) + (hist.length ? '<h3 class="sub3">Recommendation trends</h3>' + chartDiv('street-trend') : '') + trendT + '</div>'));
  // (4) financial forecast — annual · quarterly
  var ef = obj(st.eps_forecast), fa = arr(ef.annual).filter(function (r) { return r && typeof r === 'object'; }), fq = arr(ef.quarterly).filter(function (r) { return r && typeof r === 'object'; });
  var lastFy = annH.length ? annH[annH.length - 1] : null;
  var aTiles = '<div class="tiles">' + epsTile('EPS this year', fa[0] || null, lastFy ? lastFy.v : null, lastFy ? 'FY' + esc(lastFy.fy) + ' filed' : '') + epsTile('EPS next year', fa[1] || null, fa[0] ? num(fa[0].consensus) : null, fa[0] ? esc(fa[0].period) + ' consensus' : '') + '</div>';
  var qFrom = function (f) { var p = f ? qParse(f.period) : null; if (!p) return null; for (var i = 0; i < qH.length; i++) { var h = qParse(qH[i].label || qH[i].period_end); if (h && h.q === p.q && h.y === p.y - 1 && num(qH[i].eps_diluted) !== null) return { v: num(qH[i].eps_diluted), label: esc(qH[i].label || qH[i].period_end) + ' filed' }; } return null; };
  var q0 = qFrom(fq[0]), q1 = qFrom(fq[1]);
  var qTiles = '<div class="tiles">' + epsTile('EPS this quarter', fq[0] || null, q0 ? q0.v : null, q0 ? q0.label : '') + epsTile('EPS next quarter', fq[1] || null, q1 ? q1.v : null, q1 ? q1.label : '') + '</div>';
  var ffTable = function (histRows, histLabel, fcRows, isQ) {
    var cols = histRows.map(function (r) { return '<th class="num">' + histLabel(r) + ' <span class="sub">filed</span></th>'; }).join('') + fcRows.map(function (f) { return '<th class="num">' + esc(f.period) + ' <span class="sub">consensus</span></th>'; }).join('');
    var line = function (name, hf, ff, cls) { return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th>' + name + '</th>' + histRows.map(function (r) { return '<td>' + hf(r) + '</td>'; }).join('') + fcRows.map(function (f, i) { return '<td>' + ff(f, i) + '</td>'; }).join('') + '</tr>'; };
    var dash = function () { return '—'; };
    var prevEps = function (i) { if (i > 0) return num(fcRows[i - 1].consensus); var h = histRows.length ? histRows[histRows.length - 1] : null; if (!h) return null; if (isQ) { var qf = qFrom(fcRows[0]); return qf ? qf.v : null; } return num(h.eps_diluted); };
    return '<div class="twrap"><table class="fin fft"><thead><tr><th>' + (isQ ? 'Quarter' : 'Fiscal year') + '</th>' + cols + '</tr></thead><tbody>'
      + line('Revenue', function (r) { return fmtBig(r.revenue); }, dash)
      + line('Revenue growth', function (r) { return growthCell(isQ ? r.revenue_yoy : r.revenue_growth); }, dash, 'sub')
      + line('Gross profit', function (r) { return fmtBig(r.gross_profit !== undefined ? r.gross_profit : (num(r.revenue) !== null && num(r.gross_margin) !== null ? num(r.revenue) * num(r.gross_margin) : null)); }, dash)
      + line('Gross margin', function (r) { return fmtPct(r.gross_margin); }, dash, 'sub')
      + line('Operating income', function (r) { return fmtBig(r.operating_income); }, dash)
      + line('Net income', function (r) { return fmtBig(r.net_income); }, dash)
      + line('EPS (diluted)', function (r) { return fmtMoney(r.eps_diluted); }, function (f) { return fmtMoney(f.consensus); }, 'strong')
      + line('EPS growth', function (r) { return growthCell(isQ ? r.eps_diluted_yoy : r.eps_diluted_growth); }, function (f, i) { var p = prevEps(i), cnum = num(f.consensus); return p !== null && p > 0 && cnum !== null ? growthCell(cnum / p - 1) : '—'; }, 'sub')
      + line('No. of estimates', dash, function (f) { return esc(num(f.estimates) !== null ? f.estimates : '—'); }, 'sub')
      + line('Revisions ↑ / ↓', dash, function (f) { return esc(num(f.revisions_up) !== null ? f.revisions_up : '—') + ' / ' + esc(num(f.revisions_down) !== null ? f.revisions_down : '—'); }, 'sub')
      + '</tbody></table></div>';
  };
  var annRows = arr(fund.annual).filter(function (r) { return r && typeof r === 'object'; }).slice(-2), qRows = qH.slice(-4);
  var ffA = aTiles + ffTable(annRows, function (r) { return 'FY' + esc(r.fy); }, fa.slice(0, 4), false);
  var ffQ = qTiles + ffTable(qRows, function (r) { return esc(r.label || r.period_end); }, fq.slice(0, 4), true);
  parts.push(section('Financial forecast', '<div class="card ffcard"><div class="ffbar"><div class="seg ffseg" role="group" aria-label="Forecast basis"><button type="button" data-ff="annual" class="on" aria-pressed="true">Annual</button><button type="button" data-ff="quarterly" aria-pressed="false">Quarterly</button></div><span class="note">Filed columns from fundamentals.json; consensus columns from Nasdaq.</span></div>'
    + '<div class="ffpane on" data-ff="annual">' + ffA + '</div><div class="ffpane" data-ff="quarterly">' + ffQ + '</div>'
    + '<p class="note">Revenue, profit and margin rows show "—" in the consensus columns because Nasdaq publishes EPS consensus only. EPS growth in a consensus column is measured against the prior filed figure (or the prior consensus); the "from" figure on a quarterly tile is the same quarter a year earlier as filed.</p></div>'));
  // (5) EPS forecast chart + table
  var epsHal = function (rows, labelOf) { return hal('EPS', rows.map(function (f) { return esc(labelOf(f)); }), [
    { name: 'High', cells: rows.map(function (f) { return '<span class="mono">' + fmtMoney(f.high) + '</span>'; }) },
    { name: 'Avg <span class="sub">consensus</span>', strong: true, cells: rows.map(function (f) { return '<span class="mono">' + fmtMoney(f.consensus) + '</span>'; }) },
    { name: 'Low', cells: rows.map(function (f) { return '<span class="mono">' + fmtMoney(f.low) + '</span>'; }) }]); };
  if (fa.length || annH.length) parts.push(section('EPS forecast', '<div class="card">' + (fa.length ? chartDiv('street-eps') : '') + (fa.length ? epsHal(fa, function (f) { return f.period; }) : '<p class="note">No annual EPS consensus on record.</p>') + '<p class="note">Solid line: filed diluted EPS by fiscal year. Dashed: the Nasdaq consensus, with the low–high range of estimates shaded. Consensus EPS is on the analysts\' adjusted basis, not GAAP, so the two lines are not strictly comparable.</p></div>'));
  // (6) EPS growth
  if (fa.length || annH.length) {
    var prevC = lastFy ? lastFy.v : null, gRows = fa.map(function (f, i) { var p = i ? num(fa[i - 1].consensus) : prevC, ok = p !== null && p > 0; var r = { period: f.period, hi: ok && num(f.high) !== null ? num(f.high) / p - 1 : null, avg: ok && num(f.consensus) !== null ? num(f.consensus) / p - 1 : null, lo: ok && num(f.low) !== null ? num(f.low) / p - 1 : null }; return r; });
    parts.push(section('EPS growth', '<div class="card">' + (fa.length ? chartDiv('street-epsg') : '') + (gRows.length ? hal('EPS growth', gRows.map(function (r) { return esc(r.period); }), [
      { name: 'High', cells: gRows.map(function (r) { return growthCell(r.hi); }) }, { name: 'Avg <span class="sub">consensus</span>', strong: true, cells: gRows.map(function (r) { return growthCell(r.avg); }) }, { name: 'Low', cells: gRows.map(function (r) { return growthCell(r.lo); }) }]) : '<p class="note">No annual EPS consensus on record.</p>')
      + '<p class="note">Historical bars: year-over-year change in filed diluted EPS. Forecast bars: the consensus against the prior year (filed for the first forecast year, consensus after), with the error bar spanning the low and high estimates. Blank where the prior figure was not positive.</p></div>'));
  }
  // (7) earnings track record
  var eh = arr(st.eps_history).filter(function (r) { return r && typeof r === 'object'; }), up = arr(st.eps_upcoming).filter(function (r) { return r && typeof r === 'object'; }), ne = obj(st.next_earnings);
  var trackT = eh.length ? '<div class="twrap"><table class="mini"><thead><tr><th>Quarter</th><th class="num">Consensus</th><th class="num">Actual</th><th class="num">Surprise</th></tr></thead><tbody>' + eh.slice(-4).map(function (r) { var sp = num(r.surprise_pct); if (sp === null && num(r.consensus) && num(r.actual) !== null) sp = (num(r.actual) / num(r.consensus) - 1) * 100; return '<tr><td class="mono">' + esc(r.period) + '</td><td class="num mono">' + fmtMoney(r.consensus) + '</td><td class="num mono">' + fmtMoney(r.actual) + '</td><td class="num mono ' + signCls(sp) + '">' + (sp !== null ? fmtPts(sp, 1) : '—') + '</td></tr>'; }).join('') + '</tbody></table></div>' : '<p class="note">No actual-vs-consensus history on record for this name.</p>';
  var nextLine = joinNonEmpty([ne.date || ne.text ? 'Next report: <b>' + esc(ne.date || '') + '</b>' + (ne.text ? ' <span class="sub">' + esc(ne.text) + '</span>' : '') : '', up.length ? 'upcoming consensus ' + up.slice(0, 2).map(function (r) { return esc(r.period) + ' ' + fmtMoney(r.consensus); }).join(', ') : ''], ' · ');
  parts.push(section('Earnings track record', '<div class="card">' + (eh.length ? chartDiv('street-track') : '') + trackT + (nextLine ? '<p class="note">' + nextLine + '</p>' : '') + '</div>'));
  // (8) data sources
  parts.push('<div class="srcbox"><b>Data sources.</b> ' + esc(st.source || 'Nasdaq analyst endpoints') + ' (Zacks consensus)' + (st.as_of ? ' — pulled ' + esc(st.as_of) : '') + '; EPS consensus is on the analysts\' adjusted basis, not GAAP; not an input to the DCF. ' + streetSourceNote(st) + '</div>');
  return parts.join('');
}
function renderForecastAnalysts(record) {
  var st = streetOf(record), p = obj(record.profile), parts = [];
  var honest = '<p class="note">Individual analyst names, track records and per-analyst price targets are paid (TipRanks) data and are not included here.</p>';
  if (!st) return '<div class="card empty"><p class="note">' + (Object.keys(p).length ? 'No analyst coverage data on record for this name.' : 'Analyst coverage appears once profile.py has pulled the Nasdaq analyst data for this name.') + '</p>' + honest + '</div>';
  var brokers = arr(st.brokers).map(function (b) { return typeof b === 'string' ? b : obj(b).name || obj(b).broker || ''; }).filter(Boolean);
  parts.push(section('Covering brokers', '<div class="card">' + (brokers.length ? '<div class="chips">' + brokers.map(function (b) { return '<span class="chip">' + esc(b) + '</span>'; }).join('') + '</div>' : '<p class="note">Nasdaq returned no broker list for this name.</p>') + (num(st.analysts) !== null ? '<p class="note">' + esc(st.analysts) + ' analysts in the consensus.</p>' : '') + '</div>'));
  var hist = arr(st.history).filter(function (r) { return r && typeof r === 'object'; }).slice().sort(function (a, b) { return String(a.date) < String(b.date) ? 1 : String(a.date) > String(b.date) ? -1 : 0; });
  parts.push(section('Ratings history', '<div class="card">' + (hist.length ? '<div class="twrap"><table class="mini"><thead><tr><th>Month</th><th>Consensus</th><th class="num">Buy</th><th class="num">Hold</th><th class="num">Sell</th><th class="num">Total</th><th class="num">Mean target</th></tr></thead><tbody>'
    + hist.map(function (r) { var cc = streetCounts(r); return '<tr><td class="mono">' + esc(r.date) + '</td><td>' + esc(r.consensus || '—') + '</td><td class="num mono">' + esc(cc.buy !== null ? cc.buy : '—') + '</td><td class="num mono">' + esc(cc.hold !== null ? cc.hold : '—') + '</td><td class="num mono">' + esc(cc.sell !== null ? cc.sell : '—') + '</td><td class="num mono">' + (cc.total || '—') + '</td><td class="num mono">' + fmtMoney(r.mean_target) + '</td></tr>'; }).join('') + '</tbody></table></div>' : '<p class="note">No rating history on record.</p>') + '</div>'));
  var mo = obj(st.momentum), mrow = function (k, name) { var m = obj(mo[k]); if (!Object.keys(m).length) return ''; var cur = num(m.current), wk = num(m.week_ago), mn = num(m.month_ago); var d = function (x) { return cur !== null && x !== null && x !== 0 ? growthCell(cur / x - 1) : '—'; }; return '<tr><th>' + name + (m.period ? ' <span class="sub">' + esc(m.period) + '</span>' : '') + '</th><td class="num mono">' + fmtMoney(cur) + '</td><td class="num mono">' + fmtMoney(wk) + ' <span class="sub">' + d(wk) + '</span></td><td class="num mono">' + fmtMoney(mn) + ' <span class="sub">' + d(mn) + '</span></td></tr>'; };
  var mT = mrow('quarter', 'Current quarter') + mrow('year', 'Current year');
  var peg = num(st.peg_forward);
  parts.push(section('Estimate momentum', '<div class="card">' + (mT ? '<div class="twrap"><table class="mini"><thead><tr><th>Consensus EPS</th><th class="num">Now</th><th class="num">1 week ago</th><th class="num">1 month ago</th></tr></thead><tbody>' + mT + '</tbody></table></div>' : '<p class="note">No estimate-revision momentum on record.</p>') + (peg !== null ? '<div class="tiles">' + tile('Forward PEG', fmtX(peg, 2), '', 'price / EPS ÷ expected growth (Nasdaq)') + '</div>' : '') + '</div>'));
  var ud = arr(st.upgrades_downgrades).filter(function (x) { return x !== null && x !== undefined; });
  parts.push(section('Upgrades / downgrades', '<div class="card">' + (ud.length ? '<ul class="flags">' + ud.map(function (u) { if (typeof u !== 'object') return '<li><span>' + esc(u) + '</span></li>'; var o = obj(u); return '<li><code>' + esc(o.date || '') + '</code><span>' + esc(joinNonEmpty([o.firm || o.broker, o.action, o.from && o.to ? o.from + ' → ' + o.to : (o.rating || ''), o.target !== undefined && o.target !== null ? 'target ' + fmtMoney(o.target) : ''], ' · ')) + '</span></li>'; }).join('') + '</ul>' : '<p class="note">Nasdaq returned no upgrades or downgrades for this name (it rarely does).</p>') + honest + '</div>'));
  parts.push('<div class="srcbox">' + streetSourceNote(st) + '</div>');
  return parts.join('');
}
function renderForecast(record, sub) {
  sub = SUB_KEYS.indexOf(sub) >= 0 ? sub : 'dcf';
  var btns = SUBTABS.map(function (t) { return '<button type="button" role="tab" class="subtab' + (t[0] === sub ? ' on' : '') + '" data-sub="' + t[0] + '" aria-selected="' + (t[0] === sub) + '">' + t[1] + (t[0] !== 'dcf' ? '<span class="sub">Nasdaq</span>' : '') + '</button>'; }).join('');
  var bodies = { dcf: renderForecastDCF, street: renderForecastStreet, analysts: renderForecastAnalysts };
  var panes = SUBTABS.map(function (t) {
    var body;
    try { body = bodies[t[0]](record); } catch (e) { body = '<div class="card err">This section could not be rendered: ' + esc(e && e.message) + '</div>'; }
    return '<div class="subpane' + (t[0] === sub ? ' on' : '') + '" data-sub="' + t[0] + '" role="tabpanel">' + body + '</div>';
  }).join('');
  return '<div class="subtabs" role="tablist" aria-label="Forecast view">' + btns + '</div>' + panes;
}

function renderAnalysis(record) {
  var out = [];
  if (record.analysis_md) out.push('<div class="card md">' + md(record.analysis_md) + '</div>');
  else out.push('<div class="card empty"><p class="note">No analysis.md in this folder.</p></div>');
  if (record.second_pass_md) out.push(section('Second pass', '<div class="card md">' + md(record.second_pass_md) + '</div>'));
  return out.join('');
}

function renderData(record) {
  var s = obj(record.score), n = obj(record.numbers), fund = obj(record.fundamentals), ttm = obj(record.ttm), j = record.judgment, prof = obj(fund.profile), rows = [];
  var kv = function (k, v) { rows.push('<tr><th>' + k + '</th><td>' + v + '</td></tr>'); };
  var cik = n.cik !== undefined && n.cik !== null ? String(n.cik) : '';
  kv('Entity', esc(n.name || s.name || record.name) + ' · CIK ' + esc(cik) + (cik ? ' · <a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&amp;CIK=' + esc(encodeURIComponent(cik)) + '&amp;type=10-K" target="_blank" rel="noopener">EDGAR</a>' : ''));
  if (Object.keys(prof).length) {
    kv('Industry (SIC)', esc(prof.sic_description) + ' (' + esc(prof.sic) + ')');
    var fye = String(prof.fiscal_year_end_mmdd || '');
    kv('Fiscal year end', esc(fye.slice(0, 2)) + '/' + esc(fye.slice(2)) + ' · ' + esc(prof.filer_category) + ' · incorporated ' + esc(prof.state_of_incorporation));
    var lf = obj(prof.latest_filings);
    Object.keys(lf).forEach(function (form) {
      var d = obj(lf[form]), url = String(d.url || '');
      var link = /^https?:\/\//i.test(url) ? ' · <a href="' + esc(url) + '" target="_blank" rel="noopener">open</a>' : '';
      kv('Latest ' + esc(form), 'filed ' + esc(d.filed) + ' for the period ending ' + esc(d.period) + link);
    });
    kv('8-K filings, last 12 months', esc(prof.eight_k_count_12m));
  }
  kv('Engine', 'v' + esc(n.engine_version) + ' · release ' + esc(n.engine_release || s.engine_release || '5.3.x (pre-5.4)') + ' · run ' + esc(n.as_of) + ' · annual form ' + esc(n.filer_annual_form));
  kv('Price', fmtMoney(n.price) + ' (' + esc(n.price_source) + ') · market cap est. ' + fmtBig(n.market_cap_est) + ' · diluted shares ' + fmtCnt(n.shares_diluted_latest));
  var inp = obj(n.inputs);
  kv('Base', fmtMoney(n.base_oe_per_share) + '/share · ' + esc(n.base_source) + ' · pin source ' + esc(inp.base_pin_source));
  kv('Run inputs', 'moat ' + esc(inp.moat) + ' · probs ' + esc(JSON.stringify(inp.probs || null)) + ' · offsets ' + esc(JSON.stringify(inp.offsets || null)) + ' · mults ' + esc(JSON.stringify(inp.mults || null)) + ' · g_terminal ' + esc(inp.g_terminal));
  kv('Net debt basis', fmtBig(n.net_debt_latest) + ' · ' + esc(n.net_debt_basis || 'current + noncurrent tags (pre-5.4)') + (n.lease_liabilities_latest !== undefined && n.lease_liabilities_latest !== null ? ' · operating leases ' + fmtBig(n.lease_liabilities_latest) : ''));
  if (n.fx_conversion) { var fx = obj(n.fx_conversion); kv('FX conversion', esc(fx.from_currency) + ' → USD at period-end ECB rates (' + esc(fx.source) + '); rates ' + esc(JSON.stringify(fx.rates || null))); }
  if (n.ads_ratio) kv('ADS ratio', esc(obj(n.ads_ratio).ratio) + ' ordinary per ADS · ' + esc(obj(n.ads_ratio).source));
  kv('Data gaps', esc(JSON.stringify(n.data_gap || [])) + ' (uncovered: ' + esc(JSON.stringify(n.data_gap_uncovered || [])) + ')');
  kv('Content hash', n.content_hash ? '<span class="mono">' + esc(String(n.content_hash).slice(0, 16)) + '…</span>' : 'none (pre-stamping run)');
  var ut = obj(n.used_tags), utKeys = Object.keys(ut).filter(function (k) { return ut[k]; });
  kv('EDGAR tags (engine)', utKeys.length ? utKeys.map(function (k) { return '<span class="mono small">' + esc(k) + ': ' + esc(ut[k]) + '</span>'; }).join('<br>') : '<span class="note">not kept in this record (attachment trims used_tags)</span>');
  var tu = obj(fund.tags_used), tuKeys = Object.keys(tu).filter(function (k) { return arr(tu[k]).length; });
  if (tuKeys.length) kv('EDGAR tags (fundamentals)', tuKeys.map(function (k) { return '<span class="mono small">' + esc(k) + ': ' + esc(arr(tu[k]).join(', ')) + '</span>'; }).join('<br>'));
  kv('Files', arr(record.files).map(function (f) { return '<span class="mono">' + esc(f) + '</span>'; }).join(' · ') || '—');
  var parts = [section('Provenance', '<div class="card"><div class="twrap"><table class="kv"><tbody>' + rows.join('') + '</tbody></table></div></div>')];
  if (Object.keys(obj(ttm.inputs)).length) {
    var ti = obj(ttm.inputs), trs = '';
    [['ocf', 'Operating cash flow'], ['capex', 'Capex'], ['sbc', 'Stock-based comp'], ['shares_diluted', 'Diluted shares']].forEach(function (c) {
      var k = c[0], d = obj(ti[k]), f = k === 'shares_diluted' ? fmtCnt : fmtBig;
      trs += '<tr><th>' + c[1] + '</th><td class="num mono">' + f(d.fy) + '</td><td class="num mono">' + f(d.ytd_prior) + '</td><td class="num mono">' + f(d.ytd_current) + '</td><td class="num mono strong">' + (k !== 'shares_diluted' ? f(d.ttm) : f(d.ytd_current)) + '</td><td class="small">' + esc(d.fy_tag) + '</td></tr>';
    });
    var fyEnd = get(obj(ti.ocf).fy_period, 1) || '';
    var ovUsed = arr(ttm.overrides_used).map(function (o) { return obj(o).field; }).filter(Boolean);
    parts.push(section('TTM construction', '<div class="card"><div class="twrap"><table class="fin"><thead><tr><th>TTM leg</th><th class="num">FY ' + esc(fyEnd) + '</th><th class="num">− prior YTD</th><th class="num">+ current YTD</th><th class="num">= TTM</th><th>Tag</th></tr></thead><tbody>' + trs + '</tbody></table></div>'
      + "<p class=\"note\">TTM owner's earnings " + fmtBig(ttm.ttm_oe_total) + ' ÷ ' + fmtCnt(ttm.ttm_shares_diluted) + ' shares = <b class="mono">' + fmtMoney(ttm.ttm_oe_per_share) + '</b> / share, computed by ttm.py from EDGAR 10-Q year-to-date facts (FY − prior YTD + current YTD). ' + (ovUsed.length ? 'Overrides used: ' + esc(ovUsed.join(', ')) : '') + '</p></div>'));
  } else if (record.ttm === undefined && record.live) {
    parts.push('<p class="note">TTM construction and judgment.json are trimmed from the attachment — open the site for the full record.</p>');
  }
  var ov = renderOverrides(record);
  if (ov) parts.push(section('Overrides', ov));
  var ev = arr(record.registry).filter(function (e) { return e && typeof e === 'object' && e.event; });
  if (ev.length) {
    var li = ev.map(function (e) { return '<li><code>' + esc(e.event) + '</code> ' + esc(e.date) + ': ' + esc(Object.keys(e).filter(function (k) { return k !== 'ticker' && k !== 'event' && k !== 'date'; }).map(function (k) { return k + '=' + (typeof e[k] === 'object' ? JSON.stringify(e[k]) : e[k]); }).join(', ')) + '</li>'; }).join('');
    parts.push(section('Judgment calls on record', '<div class="card"><ul class="flags">' + li + '</ul><p class="note">From _system/overrides_registry.json — every judgment call the run embodies.</p></div>'));
  }
  if (j && typeof j === 'object') parts.push(section('judgment.json', '<div class="card"><pre class="json">' + esc(JSON.stringify(j, null, 1)) + '</pre></div>', "The agent's judgment inputs exactly as make_score.py consumed them."));
  return parts.join('');
}

var TAB_RENDERERS = { overview: renderOverview, financials: renderFinancials, dividends: renderDividends, segments: renderSegments, forecast: renderForecast, analysis: renderAnalysis, data: renderData };

/* The company page. nav = {prev, next, rank} (tickers by rank) is optional; sub is the Forecast sub-tab. */
function renderCompanyHTML(record, tab, nav, sub) {
  record = obj(record); nav = obj(nav);
  tab = TAB_KEYS.indexOf(tab) >= 0 ? tab : 'overview';
  sub = SUB_KEYS.indexOf(sub) >= 0 ? sub : 'dcf';
  var s = obj(record.score), row = obj(record.row), ticker = s.ticker || record.ticker || row.ticker || '';
  var navRight = 'Pass 1 · ' + esc(s.analysis_date || row.analysis_date);
  if (obj(s.second_pass).verdict === 'changed') navRight = 'Pass 2 revised · ' + esc(s.second_pass.date);
  var tabBtns = TABS.map(function (t) { return '<button type="button" role="tab" class="tab' + (t[0] === tab ? ' on' : '') + '" data-tab="' + t[0] + '" aria-selected="' + (t[0] === tab) + '">' + t[1] + '</button>'; }).join('');
  // header → sticky tab bar → tab content; the price-vs-value chart is the Overview tab's first card (owner decision, 2026-10-14)
  var panes = TABS.map(function (t) {
    var body;
    try { body = (t[0] === 'overview' ? renderPriceChart(record) : '') + (t[0] === 'forecast' ? renderForecast(record, sub) : TAB_RENDERERS[t[0]](record)); }
    catch (e) { body = '<div class="card err">This tab could not be rendered: ' + esc(e && e.message) + '</div>'; }
    return '<div class="pane' + (t[0] === tab ? ' on' : '') + '" data-pane="' + t[0] + '" role="tabpanel">' + body + '</div>';
  }).join('');
  var pn = '<div class="pnav">' + (nav.prev ? '<a href="#' + esc(nav.prev) + '" class="pn">← ' + esc(nav.prev) + '</a>' : '<span></span>')
    + '<span class="note">' + (nav.rank ? 'rank ' + esc(nav.rank) : '') + '</span>' + (nav.next ? '<a href="#' + esc(nav.next) + '" class="pn">' + esc(nav.next) + ' →</a>' : '<span></span>') + '</div>';
  return '<article class="page open" id="d-' + esc(safeId(ticker)) + '" data-ticker="' + esc(ticker) + '">'
    + '<nav class="dnav"><a class="back" href="#">← Ranking</a><span class="navr mono">' + navRight + '</span></nav>'
    + renderHeader(record)
    + '<div class="tabbar">' + renderTabSummary(record) + '<div class="tabs" role="tablist">' + tabBtns + '</div></div>' + panes + pn
    + '<footer class="dfoot"><span>Screening-grade standardized DCF — not a buy or sell call.</span><span class="mono">stocks/' + esc(record.folder || ticker) + '/</span></footer></article>';
}
function renderMissingHTML(row, meta) {
  row = obj(row); meta = obj(meta);
  var site = meta.site_url ? '<a href="' + esc(meta.site_url) + '#' + esc(row.ticker) + '" target="_blank" rel="noopener">open the site</a>' : 'open the site';
  return '<article class="page open"><nav class="dnav"><a class="back" href="#">← Ranking</a><span class="navr mono">' + esc(row.analysis_date || '') + '</span></nav>'
    + '<div class="card notice"><h2 class="mono">' + esc(row.ticker) + ' <span class="hco">' + esc(row.name) + '</span></h2><p class="note">' + esc(row.ticker) + ' is not embedded in this file — ' + site + ' for its page. '
    + (row.tier ? 'Scored Tier ' + esc(row.tier) + ' · IRR ' + fmtPct(row.irr) + (num(row.irr_live) !== null ? ' · live ' + fmtPct(row.irr_live) : '') + ' · ' + esc(row.one_liner) : '') + '</p></div></article>';
}
function renderErrorHTML(msg, detail) {
  return '<div class="card err" role="alert"><b>Could not load the ranking data.</b><p class="note">' + esc(msg) + (detail ? ' — ' + esc(detail) : '') + '</p><p class="note">Serve this folder over HTTP (for example <code>python -m http.server</code> inside <code>_daily/site/</code>) and rebuild with <code>python _system/build_site.py</code> if the JSON files are missing.</p></div>';
}

/* ---- Ranking list. state = {tier, fit, sort, q, watch}; stars = per-device extra watchlist tickers (localStorage,
   README: "the app's star buttons add per-device extras"), passed alongside the state so the renderers stay pure. */
function defaultState() { return { tier: 'all', fit: 'modeled', sort: 'irr_live', q: '', watch: false }; }
function normState(state) {
  var d = defaultState(), s = obj(state);
  return { tier: /^(all|S|A|B|C|D|F)$/.test(String(s.tier)) ? s.tier : d.tier, fit: /^(all|modeled|misfit)$/.test(String(s.fit)) ? s.fit : d.fit,
    sort: SORTS.some(function (x) { return x[0] === s.sort; }) ? s.sort : d.sort, q: typeof s.q === 'string' ? s.q : '', watch: s.watch === true };
}
function normStars(stars) { // array of tickers (or an object keyed by ticker) → upper-cased unique array
  var src = Array.isArray(stars) ? stars : (stars && typeof stars === 'object' ? Object.keys(stars).filter(function (k) { return stars[k]; }) : []), out = [];
  src.forEach(function (t) { if (typeof t === 'string' && /^[A-Za-z0-9._-]{1,12}$/.test(t)) { t = t.toUpperCase(); if (out.indexOf(t) < 0) out.push(t); } });
  return out;
}
function isStarred(row, stars) { return normStars(stars).indexOf(String(obj(row).ticker || '').toUpperCase()) >= 0; }
function isWatched(row, stars) { return obj(row).watchlist === true || isStarred(row, stars); }
function rowTier(row) { return row.tier_live || row.tier || '?'; }
function sortKey(row, key) {
  switch (key) {
    case 'irr_live': return num(row.irr_live) !== null ? num(row.irr_live) : num(row.irr);
    case 'irr': return num(row.irr);
    case 'irr_bear': return num(row.irr_bear_live) !== null ? num(row.irr_bear_live) : num(row.irr_bear);
    case 'upside': return num(row.upside15_live) !== null ? num(row.upside15_live) : num(row.upside15);
    case 'moat': return num(row.moat);
    case 'cap': return num(row.market_cap_b_live) !== null ? num(row.market_cap_b_live) : num(row.market_cap_b);
    case 'ret_1y': return num(row.ret_1y_pct);
    default: return null;
  }
}
function filterSortIndex(index, state, stars) {
  state = normState(state); stars = normStars(stars);
  var q = state.q.trim().toLowerCase();
  var rows = arr(index).map(function (r, i) { return { r: obj(r), i: i }; }).filter(function (x) {
    var r = x.r, okT = state.tier === 'all' || rowTier(r) === state.tier, okF = state.fit === 'all' || (r.fit || 'modeled') === state.fit;
    var okW = !state.watch || isWatched(r, stars);
    var hay = (String(r.ticker || '') + ' ' + String(r.name || '') + ' ' + String(r.sector || '')).toLowerCase();
    return okT && okF && okW && (!q || hay.indexOf(q) >= 0);
  });
  rows.sort(function (a, b) {
    var ka = sortKey(a.r, state.sort), kb = sortKey(b.r, state.sort);
    if (ka === null && kb === null) return a.i - b.i;
    if (ka === null) return 1; if (kb === null) return -1;
    return kb - ka || a.i - b.i;
  });
  return rows.map(function (x) { return x.r; });
}
function starHTML(row, stars) { // canonical watchlist rows get a fixed star; every other row a per-device toggle
  var t = String(obj(row).ticker || '');
  if (obj(row).watchlist === true) return '<span class="star fixed" title="On the watchlist (_system/watchlist.json)">★</span>';
  var on = isStarred(row, stars);
  return '<button type="button" class="star' + (on ? ' on' : '') + '" data-star="' + esc(t) + '" aria-pressed="' + on + '" title="' + (on ? 'Remove from this device\'s watchlist extras' : 'Star on this device (local extras, not synced)') + '" aria-label="' + (on ? 'Unstar ' : 'Star ') + esc(t) + '">' + (on ? '★' : '☆') + '</button>';
}
function renderRowHTML(row, stars) {
  row = obj(row);
  var t = row.ticker || '', tier = rowTier(row), scoredTier = row.tier || '?', sp = obj(row.second_pass), badges = [];
  if (sp.verdict === 'changed') badges.push('<span class="bdg p2">↺ pass 2: ' + esc(sp.prior_tier) + ' → ' + esc(scoredTier) + '</span>');
  else if (Object.keys(sp).length) badges.push('<span class="bdg p2">✓ pass 2</span>');
  arr(row.overrides).forEach(function (o) { if (o && typeof o === 'object' && o.field) badges.push('<span class="bdg ov">' + esc(o.field) + ': ' + (o.kind === 'estimate' ? 'AI estimate' : 'filing override') + '</span>'); });
  if (row.tier_override || (row.tier_by_numbers && row.tier && row.tier !== row.tier_by_numbers)) badges.push('<span class="bdg to">tier ' + esc(row.tier_by_numbers) + '→' + esc(row.tier) + ' by judgment</span>');
  if (row.fit === 'misfit') badges.push('<span class="bdg mf">sector misfit</span>');
  if (row.irr_at_floor) badges.push('<span class="bdg mf">IRR at floor</span>');
  if (row.irr_capped) badges.push('<span class="bdg mf">IRR capped</span>');
  var fl = arr(row.flags), live = num(row.irr_live) !== null;
  var tb = (live && row.tier_bear_live) || row.tier_bear, tu = (live && row.tier_bull_live) || row.tier_bull;
  var band = tb && tu ? '<span class="band" title="' + (live ? 'bear → bull tier at the last close' : 'bear → bull tier as scored') + '"><i style="background:' + (TIER_ACCENT[tb] || '#333') + '">' + esc(tb) + '</i>→<i style="background:' + (TIER_ACCENT[tu] || '#333') + '">' + esc(tu) + '</i></span>' : '—';
  var up = live ? num(row.upside15_live) : num(row.upside15), price = live && num(row.price_live) !== null ? row.price_live : row.price;
  var cap = live && num(row.market_cap_b_live) !== null ? row.market_cap_b_live : row.market_cap_b, r1 = num(row.ret_1y_pct), moat = num(row.moat);
  var tierCell = '<span class="tbadge" style="background:' + (TIER_ACCENT[tier] || '#333') + '" title="' + (live ? 'Live tier at the last close' : 'Scored tier') + '">' + esc(tier) + '</span>' + (live && tier !== scoredTier ? '<span class="was">was ' + esc(scoredTier) + '</span>' : '');
  return '<tr data-ticker="' + esc(t) + '" data-tier="' + esc(tier) + '" data-fit="' + esc(row.fit || 'modeled') + '"' + (isWatched(row, stars) ? ' data-watch="1"' : '') + '>'
    + '<td class="co"><div class="corow">' + starHTML(row, stars) + '<a href="#' + esc(t) + '"><b class="mono">' + esc(t) + '</b><span class="nm">' + esc(row.name) + '</span></a></div><span class="sub">' + esc(row.sector) + '</span></td>'
    + '<td>' + tierCell + '</td><td class="num">' + band + '</td>'
    + '<td class="num mono strong">' + (live ? fmtPct(row.irr_live) : '<span class="sub">—</span>') + '</td>'
    + '<td class="num mono' + (live ? ' muted' : ' strong') + '">' + fmtPct(row.irr) + '</td>'
    + '<td class="num mono"' + (row.price_date ? ' title="' + esc(row.price_date) + '"' : '') + '>' + fmtMoney(price) + '</td>'
    + '<td class="num mono">' + fmtMoney(row.iv15) + '</td>'
    + '<td class="num mono ' + signCls(up) + '">' + (up !== null ? fmtPts(up, 0) : '—') + '</td>'
    + '<td class="num mono">' + (moat !== null ? moat.toFixed(0) + '/10' : '—') + '</td>'
    + '<td>' + esc(row.confidence) + (row.confidence_capped ? '<span class="sub"> capped</span>' : '') + '</td>'
    + '<td class="num mono">' + fmtCap(cap) + '</td>'
    + '<td class="num mono ' + signCls(r1) + '">' + (r1 !== null ? fmtPts(r1, 0) : '—') + '</td>'
    + '<td class="take">' + badges.join('') + '<span>' + esc(row.one_liner) + '</span><span class="sub">' + (fl.length ? '⚠ ' + fl.length + ' flags · ' : '') + esc(row.analysis_date) + ' · <a href="#' + esc(t) + '" class="more">details ›</a></span></td></tr>';
}
function renderListRowsHTML(index, state, stars) {
  var rows = filterSortIndex(index, state, stars);
  if (!arr(index).length) return '<tr><td colspan="13">No companies analyzed yet.</td></tr>';
  if (!rows.length) return '<tr><td colspan="13" class="note">' + (normState(state).watch ? 'Nothing on the watchlist matches these filters.' : 'Nothing matches these filters.') + '</td></tr>';
  return rows.map(function (r) { return renderRowHTML(r, stars); }).join('');
}
function watchCount(index, stars) { return arr(index).filter(function (r) { return isWatched(r, stars); }).length; }
function watchButtonHTML(index, state, stars) {
  var n = watchCount(index, stars), on = normState(state).watch;
  return '<button type="button" id="watchbtn" class="wbtn' + (on ? ' on' : '') + '" aria-pressed="' + on + '" title="Only the names on _system/watchlist.json plus the ones starred on this device">★ Watchlist <span class="mono">' + n + '</span></button>';
}
function renderStaleHTML(meta) {
  var stale = arr(obj(meta).stale);
  if (!stale.length) return '';
  var rows = stale.map(function (c) { c = obj(c); return '<tr><td><b class="mono">' + esc(c.ticker) + '</b> ' + esc(c.name) + '</td><td><span class="tbadge stale">' + esc(c.tier) + '</span></td><td class="num mono">' + fmtPct(c.irr) + '</td><td>' + esc(c.analysis_date) + '</td></tr>'; }).join('');
  return '<details class="stalebox"><summary>Pre-v5 results — re-run pending (' + stale.length + ')</summary><p class="note">Produced before the data gate existed; shown for reference only, every one is queued for a v5 re-run.</p><div class="twrap"><table class="mini"><thead><tr><th>Company</th><th>Old tier</th><th class="num">Old Wtd IRR</th><th>Scored</th></tr></thead><tbody>' + rows + '</tbody></table></div></details>';
}
/* [header, cell class, sort key or title, column width %] — widths feed the <colgroup> (table-layout: fixed
   otherwise splits 13 columns evenly and wraps Company / Take into tall rows). */
var COLS = [['Company', '', '', 14], ['Tier', '', 'live tier at the last close; "was X" when it moved from the scored tier', 4.5], ['Band', 'num', 'bear-case → bull-case tier', 5.5], ['Live IRR', 'num', 'irr_live', 6], ['Scored IRR', 'num', 'irr', 6], ['Price', 'num', '', 6], ['IV @15%', 'num', '', 6], ['Upside', 'num', 'upside', 5], ['Moat', 'num', 'moat', 4.5], ['Conf.', '', '', 5], ['Mkt cap', 'num', 'cap', 6], ['1y price', 'num', 'ret_1y', 5], ['Take', '', '', 26.5]];
function renderListHTML(meta, index, state, stars) {
  meta = obj(meta); index = arr(index); state = normState(state);
  var sweep = obj(meta.sweep), counts = obj(meta.counts), tiers = obj(counts.tiers);
  var done = num(sweep.done) || 0, total = num(sweep.total) || 0, pct = total ? done / total * 100 : 0;
  var misfits = num(counts.misfits) !== null ? num(counts.misfits) : index.filter(function (r) { return obj(r).fit === 'misfit'; }).length;
  var withLive = num(counts.with_live) !== null ? num(counts.with_live) : index.filter(function (r) { return num(obj(r).irr_live) !== null; }).length;
  var tierChips = 'SABCDF'.split('').map(function (t) { return '<span class="tchip" style="--c:' + TIER_ACCENT[t] + '"><i>' + t + '</i>' + (num(tiers[t]) !== null ? num(tiers[t]) : index.filter(function (r) { return obj(r).tier === t; }).length) + '</span>'; }).join('');
  var notes = arr(meta.notes).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
  var seg = function (id, items, cur, attr) { return '<div class="seg" id="' + id + '" role="group">' + items.map(function (it) { return '<button type="button" data-' + attr + '="' + esc(it[0]) + '" class="' + (it[0] === cur ? 'on' : '') + '" aria-pressed="' + (it[0] === cur) + '">' + it[1] + '</button>'; }).join('') + '</div>'; };
  var sortSel = '<select id="sort" aria-label="Sort">' + SORTS.map(function (s) { return '<option value="' + s[0] + '"' + (s[0] === state.sort ? ' selected' : '') + '>Sort: ' + s[1] + '</option>'; }).join('') + '</select>';
  var ths = COLS.map(function (c) { var sortable = SORTS.some(function (s) { return s[0] === c[2]; }); return '<th class="' + c[1] + (sortable ? ' sortable' : '') + (sortable && state.sort === c[2] ? ' sorted' : '') + '"' + (sortable ? ' data-sort="' + c[2] + '" title="Sort by ' + esc(c[0]) + '"' : (c[2] ? ' title="' + esc(c[2]) + '"' : '')) + '>' + c[0] + '</th>'; }).join('');
  var shown = filterSortIndex(index, state, stars).length;
  var colgroup = '<colgroup>' + COLS.map(function (c, i) { return '<col class="c' + (i + 1) + '" style="width:' + c[3] + '%">'; }).join('') + '</colgroup>';
  return '<div id="listView">'
    + '<header class="lhead"><div><h1>Owner\'s-Earnings DCF Ranking</h1><div class="note">' + esc(meta.date) + ' · ' + commas(done) + ' of ' + commas(total) + ' companies under $40B analyzed (' + pct.toFixed(1) + '%) · ranked by probability-weighted expected return at the last close (' + withLive + ' of ' + index.length + ' repriced live; the rest at their scored price) · tap a company for its page</div>'
    + '<div class="prog" role="progressbar" aria-valuenow="' + pct.toFixed(1) + '" aria-valuemin="0" aria-valuemax="100"><div style="width:' + pct.toFixed(2) + '%"></div></div></div>'
    + '<div class="tchips">' + tierChips + '<span class="tchip"><i style="background:#3A4252">MF</i>' + misfits + ' sector misfits</span></div></header>'
    + '<div id="notice" class="notice" role="status" aria-live="polite"></div>'
    + '<details class="howto"><summary>How to read this</summary><p>Each company gets a five-scenario owner\'s-earnings DCF (super bear / bear / base / bull / super bull, each with an assigned likelihood); growth fades over a moat-driven competitive advantage period. <b>Live IRR</b> is the probability-weighted expected annual return with the scored cash-flow paths repriced at the last close; <b>Scored IRR</b> is the agent\'s verdict-date figure at the price it used. The <b>band</b> is the bear-case → bull-case tier. <b>IV</b> is the probability-weighted intrinsic value per share at a 15% discount rate; <b>Upside</b> is IV vs price. Tiers: S ≥25% · A 20–25% · B 15–20% (clears the 15% hurdle) · C 10–15% · D &lt;10% · F no positive owner\'s earnings. Banks, insurers, REITs and utilities fit the owner\'s-earnings model poorly and are marked <b>sector misfit</b> — their tiers are soft. Screening-grade standardized DCF — read the Analysis tab before acting.</p>' + (notes ? '<ul class="warnlist">' + notes + '</ul>' : '') + '</details>'
    + '<div class="controls">' + seg('tierseg', [['all', 'All'], ['S', 'S'], ['A', 'A'], ['B', 'B'], ['C', 'C'], ['D', 'D'], ['F', 'F']], state.tier, 'f') + watchButtonHTML(index, state, stars) + seg('fitseg', [['modeled', 'Modeled'], ['misfit', 'Sector misfits'], ['all', 'All']], state.fit, 'fit') + sortSel
    + '<input id="q" type="search" placeholder="Search ticker / name / sector…" aria-label="Search" value="' + esc(state.q) + '"><span class="note" id="count">' + shown + ' shown</span></div>'
    + '<div class="twrap"><table id="t">' + colgroup + '<thead><tr>' + ths + '</tr></thead><tbody>' + renderListRowsHTML(index, state, stars) + '</tbody></table></div>'
    + renderStaleHTML(meta) + '<footer class="dfoot"><span>Screening-grade standardized DCF — not a buy or sell call.</span><span class="mono">built ' + esc(meta.built_at || '') + ' · engine ' + esc(meta.engine_release_latest || '') + '</span></footer></div>';
}

/* ------------------------------------------------------------ 5. chart specs (pure: record → {id: spec}) */
function priceSpec(record) {
  var s = obj(record.score), n = obj(record.numbers), pr = obj(record.prices), row = obj(record.row), v = liveView(record);
  var scn = Object.keys(obj(n.scenarios)).length ? obj(n.scenarios) : obj(s.scenarios), hp = hurdlePrices(record);
  var ivs = LABELS.map(function (l) { return num(obj(scn[l[0]]).iv_at_15); }).filter(function (x) { return x !== null; });
  return { iv15: num(s.iv_at_15 !== undefined ? s.iv_at_15 : row.iv15), iv12: num(s.iv_at_12 !== undefined ? s.iv_at_12 : row.iv12),
    lo: ivs.length ? Math.min.apply(null, ivs) : null, hi: ivs.length ? Math.max.apply(null, ivs) : null,
    bear: num(obj(scn.bear).iv_at_15), bull: num(obj(scn.bull).iv_at_15), h20: hp[20], h25: hp[25], price: v.price, pdate: v.price_date,
    w: arr(pr.weekly), d: arr(pr.daily_1y), src: pr.source || null, asof: pr.as_of || null };
}
function chartSpecsFinancials(record) {
  var fund = obj(record.fundamentals), ann = arr(fund.annual), q = arr(fund.quarterly), hist = arr(record.history), out = {};
  var neg = function (x) { x = num(x); return x === null ? null : -x; };
  var col = function (rows, key, f) { return rows.map(function (r) { var x = num(obj(r)[key]); return x === null ? null : (f ? f(x) : x); }); };
  if (q.length) out['fin-q'] = { labels: q.map(function (r) { return r.label || r.period_end; }), yfmt: 'big', height: 240,
    series: [{ name: 'Revenue', color: C_REV, kind: 'bar', values: col(q, 'revenue') }, { name: 'Net income', color: C_NI, kind: 'line', values: col(q, 'net_income') }, { name: "Owner's earnings", color: C_OE, kind: 'line', values: col(q, 'oe_conservative') }] };
  if (ann.length) {
    var labels = ann.map(function (r) { return String(r.fy); });
    out['fin-ann'] = { labels: labels, yfmt: 'big', height: 240, series: [{ name: 'Revenue', color: C_REV, kind: 'bar', values: col(ann, 'revenue') }, { name: 'Net income', color: C_NI, kind: 'line', values: col(ann, 'net_income') }, { name: "Owner's earnings", color: C_OE, kind: 'line', values: col(ann, 'oe_conservative') }] };
    out['fin-cf'] = { labels: labels, yfmt: 'big', height: 220, series: [{ name: 'Operating CF', color: C_OCF, kind: 'bar', values: col(ann, 'ocf') }, { name: 'Capex', color: C_CAPEX, kind: 'bar', values: col(ann, 'capex', neg) }, { name: 'SBC', color: C_SBC, kind: 'bar', values: col(ann, 'sbc', neg) }, { name: "Owner's earnings", color: C_OE, kind: 'line', values: col(ann, 'oe_conservative') }] };
    out['fin-margins'] = { labels: labels, yfmt: 'pct', height: 200, zero: true, series: [{ name: 'Gross margin', color: C_REV, kind: 'line', values: col(ann, 'gross_margin') }, { name: 'Operating margin', color: C_NI, kind: 'line', values: col(ann, 'operating_margin') }, { name: "Owner's-earnings margin", color: C_OE, kind: 'line', values: col(ann, 'oe_margin') }] };
    out['fin-cashdebt'] = { labels: labels, yfmt: 'big', height: 220, series: [{ name: 'Cash', color: C_CASH, kind: 'bar', values: col(ann, 'cash') }, { name: 'Total debt', color: C_DEBT, kind: 'bar', values: col(ann, 'total_debt', neg) }, { name: 'Net debt', color: '#ECEEF2', kind: 'line', values: col(ann, 'net_debt') }] };
    out['fin-capret'] = { labels: labels, yfmt: 'big', height: 180, series: [{ name: 'Buybacks', color: C_IV, kind: 'bar', values: col(ann, 'buybacks') }, { name: 'Dividends', color: C_FCF, kind: 'bar', values: col(ann, 'dividends_paid') }, { name: 'Acquisitions', color: C_CAPEX, kind: 'bar', values: col(ann, 'acquisitions') }] };
  }
  if (!q.length && !ann.length && hist.length) {
    var h = hist.slice(-10);
    out['fin-hist'] = { labels: h.map(function (r) { return String(obj(r).fy_label || ''); }), yfmt: 'big', height: 230, series: [{ name: 'Revenue', color: C_REV, kind: 'bar', values: col(h, 'revenue') }, { name: 'OE (cons.)', color: C_OE, kind: 'line', values: col(h, 'oe_conservative') }, { name: 'OE (maint.)', color: C_FCF, kind: 'line', values: col(h, 'oe_maintenance') }] };
  }
  return out;
}
function chartSpecsDividends(record) {
  var d = obj(obj(record.fundamentals).dividends), out = {};
  var ann = arr(d.annual_dps).filter(function (r) { return r && typeof r === 'object' && num(r.dps) !== null; });
  if (!ann.length) return out;
  var tips = [], prev = null;
  ann.forEach(function (r) { var cur = num(r.dps); tips.push(prev !== null && prev !== 0 && cur !== null ? 'YoY ' + fmtPct(cur / prev - 1, 1, true) : ''); prev = cur; });
  out['div-dps'] = { labels: ann.map(function (r) { return 'FY' + r.fy; }), yfmt: 'money', height: 220, series: [{ name: 'Dividend per share', color: C_FCF, kind: 'bar', values: ann.map(function (r) { return num(r.dps); }), tips: tips }] };
  return out;
}
function chartSpecsSegments(record) {
  var out = {};
  segTables(record).forEach(function (T, ti) {
    var np = T.plabels.length, series = T.rows.map(function (r, i) {
      var tips = [];
      for (var j = 0; j < np; j++) { var sh = num(get(r.share_of_total, j)); tips.push(sh !== null ? Math.round(sh * 100) + '% of total' : ''); }
      var vals = []; for (var k = 0; k < np; k++) vals.push(num(get(r.values, k)));
      return { name: String(r.label || r.member || ''), color: SEG_COLORS[i % SEG_COLORS.length], kind: 'bar', values: vals, tips: tips };
    });
    var spec = { labels: T.plabels.map(String), yfmt: 'big', height: 260, stacked: true, series: series };
    var tvals = arr(T.tot.values);
    if (tvals.some(function (x) { return num(x) !== null; })) { spec.totals = []; for (var j = 0; j < np; j++) spec.totals.push(num(get(tvals, j))); spec.totalName = String(T.tot.basis || 'Total'); }
    out['seg-' + ti] = spec;
  });
  return out;
}
function chartSpecsForecast(record) {
  var fc = obj(record.forecast), paths = obj(fc.paths), gpaths = obj(fc.growth_paths), out = {};
  if (!arr(paths.weighted).length) return out;
  var years = []; for (var i = 1; i <= arr(paths.weighted).length; i++) years.push(String(i));
  var r4 = function (v) { v = num(v); return v === null ? null : Math.round(v * 1e4) / 1e4; }, r5 = function (v) { v = num(v); return v === null ? null : Math.round(v * 1e5) / 1e5; };
  var series = LABELS.map(function (l) { return { name: l[1], color: SCN_COLORS[l[0]], kind: 'line', values: arr(paths[l[0]]).map(r4) }; });
  series.push({ name: 'Probability-weighted', color: SCN_COLORS.weighted, kind: 'line', width: 3, values: arr(paths.weighted).map(r4) });
  out['fc-paths'] = { labels: years, yfmt: 'money', height: 260, series: series, zero: true, xlabel: 'Projection year' };
  if (arr(gpaths.base).length) out['fc-growth'] = { labels: years, yfmt: 'pct', height: 200, zero: true, xlabel: 'Projection year', series: LABELS.map(function (l) { return { name: l[1], color: SCN_COLORS[l[0]], kind: 'line', values: arr(gpaths[l[0]]).map(r5) }; }) };
  // history + forecast (owner decision, Forecast tab): filed OE/share solid, forecast dashed from the base year, super-bear → super-bull band
  var J = oeForecastSeries(record);
  if (J) {
    var tipsW = []; for (var k = 0; k < J.labels.length; k++) tipsW.push(k === J.baseIndex ? 'base OE/share the engine grew from' : (k > J.baseIndex ? 'projection year ' + (k - J.baseIndex) : ''));
    out['fc-oe'] = { labels: J.labels, yfmt: 'money', height: 280, zero: true, xlabel: 'Fiscal year → projection', dividerAt: J.baseIndex, series: [
      { name: 'Super bear → super bull', color: '#7AA2FF', kind: 'band', values: J.super_bull.map(r4), lows: J.super_bear.map(r4) },
      { name: 'Filed OE / share', color: C_OE, kind: 'line', width: 2.5, values: J.histVals.map(r4) },
      { name: 'Bear', color: SCN_COLORS.bear, kind: 'line', dash: true, width: 1.5, nodots: true, values: J.bear.map(r4) },
      { name: 'Bull', color: SCN_COLORS.bull, kind: 'line', dash: true, width: 1.5, nodots: true, values: J.bull.map(r4) },
      { name: 'Probability-weighted', color: SCN_COLORS.weighted, kind: 'line', dash: true, width: 3, values: J.weighted.map(r4), tips: tipsW }] };
    var gVals = [], gErr = [], gCol = [], gTips = [];
    for (var m = 0; m < J.labels.length; m++) {
      if (m <= J.baseIndex) { gVals.push(r5(J.histGrowth[m])); gErr.push(null); gCol.push(C_OE); gTips.push('filed, year over year'); }
      else { var y = m - J.baseIndex, lo = r5(get(J.bearGrowth, y - 1)), hi = r5(get(J.bullGrowth, y - 1)); gVals.push(r5(J.wGrowth[y - 1])); gErr.push(lo !== null && hi !== null ? [Math.min(lo, hi), Math.max(lo, hi)] : null); gCol.push(C_FCBAR); gTips.push('weighted path, year ' + y + (lo !== null && hi !== null ? ' · bear ' + FMT.pct(lo) + ' → bull ' + FMT.pct(hi) : '')); }
    }
    out['fc-oegrowth'] = { labels: J.labels, yfmt: 'pct', height: 220, zero: true, xlabel: 'Fiscal year → projection', dividerAt: J.baseIndex, legendExtra: [{ name: 'Forecast (weighted path)', color: C_FCBAR }, { name: 'Bear → bull growth', color: '#ECEEF2', kind: 'err' }],
      series: [{ name: 'Filed YoY', color: C_OE, kind: 'bar', values: gVals, colors: gCol, errors: gErr, tips: gTips }] };
  }
  return out;
}
/* Street sub-tab charts (profile.street): recommendation trends, EPS forecast with the low–high band, EPS growth
   with error bars, actual vs consensus track record; the price-target fan is a time chart drawn by drawFan. */
function chartSpecsStreet(record) {
  var st = streetOf(record), out = {};
  if (!st) return out;
  var r4 = function (v) { v = num(v); return v === null ? null : Math.round(v * 1e4) / 1e4; };
  var hist = arr(st.history).filter(function (r) { return r && typeof r === 'object'; }).slice().sort(function (a, b) { return String(a.date) < String(b.date) ? -1 : String(a.date) > String(b.date) ? 1 : 0; }).slice(-12);
  if (hist.length) out['street-trend'] = { labels: hist.map(function (r) { return String(r.date || '').slice(0, 7); }), yfmt: 'num', height: 200, stacked: true, series: [
    { name: 'Buy', color: '#5BD69C', kind: 'bar', values: hist.map(function (r) { return num(r.buy); }) }, { name: 'Hold', color: '#fbbf24', kind: 'bar', values: hist.map(function (r) { return num(r.hold); }) }, { name: 'Sell', color: '#FF8A8A', kind: 'bar', values: hist.map(function (r) { return num(r.sell); }) }] };
  var annH = epsAnnualHist(record).slice(-10), fa = arr(obj(st.eps_forecast).annual).filter(function (r) { return r && typeof r === 'object'; }).slice(0, 4);
  if (fa.length) {
    var H = annH.length, labels = annH.map(function (h) { return 'FY' + h.fy; }).concat(fa.map(function (f) { return String(f.period); }));
    var joinAt = H ? annH[H - 1].v : null;
    var pad = function (f) { var o = []; for (var i = 0; i < H - 1; i++) o.push(null); if (H) o.push(joinAt); fa.forEach(function (x) { o.push(r4(f(x))); }); return o; };
    var filed = annH.map(function (h) { return r4(h.v); }); while (filed.length < labels.length) filed.push(null);
    out['street-eps'] = { labels: labels, yfmt: 'money', height: 240, zero: true, dividerAt: H - 1, series: [
      { name: 'Low → high estimate', color: '#7AA2FF', kind: 'band', values: pad(function (x) { return x.high; }), lows: pad(function (x) { return x.low; }) },
      { name: 'Filed diluted EPS', color: C_OE, kind: 'line', width: 2.5, values: filed },
      { name: 'Consensus', color: SCN_COLORS.weighted, kind: 'line', dash: true, width: 2.5, values: pad(function (x) { return x.consensus; }) }] };
    var gv = [], ge = [], gc = [], gt = [];
    annH.forEach(function (h, i) { var g = h.g !== null ? h.g : (i && annH[i - 1].v > 0 ? h.v / annH[i - 1].v - 1 : null); gv.push(r4(g)); ge.push(null); gc.push(C_OE); gt.push('filed, year over year'); });
    fa.forEach(function (f, i) { var p = i ? num(fa[i - 1].consensus) : joinAt, ok = p !== null && p > 0; var lo = ok && num(f.low) !== null ? r4(num(f.low) / p - 1) : null, hi = ok && num(f.high) !== null ? r4(num(f.high) / p - 1) : null; gv.push(ok && num(f.consensus) !== null ? r4(num(f.consensus) / p - 1) : null); ge.push(lo !== null && hi !== null ? [Math.min(lo, hi), Math.max(lo, hi)] : null); gc.push(C_FCBAR); gt.push('consensus vs ' + (i ? 'prior consensus' : 'last filed FY')); });
    out['street-epsg'] = { labels: labels, yfmt: 'pct', height: 200, zero: true, dividerAt: H - 1, legendExtra: [{ name: 'Consensus', color: C_FCBAR }, { name: 'Low → high', color: '#ECEEF2', kind: 'err' }], series: [{ name: 'Filed YoY', color: C_OE, kind: 'bar', values: gv, colors: gc, errors: ge, tips: gt }] };
  }
  var eh = arr(st.eps_history).filter(function (r) { return r && typeof r === 'object'; }).slice(-4);
  if (eh.length) out['street-track'] = { labels: eh.map(function (r) { return String(r.period); }), yfmt: 'money', height: 200, zero: true, series: [
    { name: 'Consensus', color: C_OCF, kind: 'bar', values: eh.map(function (r) { return r4(r.consensus); }) },
    { name: 'Actual', color: C_NI, kind: 'bar', values: eh.map(function (r) { return r4(r.actual); }), tips: eh.map(function (r) { var sp = num(r.surprise_pct); if (sp === null && num(r.consensus) && num(r.actual) !== null) sp = (num(r.actual) / num(r.consensus) - 1) * 100; return sp !== null ? 'surprise ' + fmtPts(sp, 1) : ''; }) }] };
  var pr = obj(record.prices), v = liveView(record), all = arr(pr.daily_1y).length > 30 ? arr(pr.daily_1y) : arr(pr.weekly);
  if (all.length > 1 && (num(st.target_mean) !== null || num(st.target_low) !== null || num(st.target_high) !== null)) {
    var lastD = new Date(all[all.length - 1][0]), cut = new Date(lastD); cut.setFullYear(cut.getFullYear() - 1);
    out['street-fan'] = { pts: all.filter(function (p) { return new Date(p[0]) >= cut && typeof p[1] === 'number'; }), from: v.price, fromDate: v.price_date, low: num(st.target_low), mean: num(st.target_mean), high: num(st.target_high) };
  }
  return out;
}
function chartSpecs(record) {
  record = obj(record);
  var out = { price: priceSpec(record) }, groups = [chartSpecsFinancials(record), chartSpecsDividends(record), chartSpecsSegments(record), chartSpecsForecast(record), chartSpecsStreet(record)];
  groups.forEach(function (g) { Object.keys(g).forEach(function (k) { out[k] = g[k]; }); });
  return out;
}

/* ------------------------------------------------------------ 6. DOM: charts, mount, route, data */
function fmtBigJs(v) { var a = Math.abs(v), s = v < 0 ? '-' : ''; if (a >= 1e12) return s + '$' + (a / 1e12).toFixed(2) + 'T'; if (a >= 1e9) return s + '$' + (a / 1e9).toFixed(a >= 1e10 ? 0 : 1) + 'B'; if (a >= 1e6) return s + '$' + (a / 1e6).toFixed(0) + 'M'; if (a >= 1e3) return s + '$' + (a / 1e3).toFixed(0) + 'K'; return s + '$' + a.toFixed(2); }
var FMT = { big: fmtBigJs, pct: function (v) { return (v * 100).toFixed(Math.abs(v) >= 0.995 ? 0 : 1) + '%'; }, money: function (v) { return (v < 0 ? '-' : '') + '$' + (Math.abs(v) >= 100 ? Math.abs(v).toFixed(0) : Math.abs(v) >= 10 ? Math.abs(v).toFixed(1) : Math.abs(v).toFixed(2)); }, num: function (v) { return v.toLocaleString(); } };
function axisFmt(fmt, step) { return fmt === FMT.money ? function (v) { return (v < 0 ? '-' : '') + '$' + (step >= 1 ? Math.abs(v).toFixed(0) : step >= 0.1 ? Math.abs(v).toFixed(1) : Math.abs(v).toFixed(2)); } : fmt; }
function nice(lo, hi, n) {
  if (hi === lo) hi = lo + 1;
  var raw = (hi - lo) / n, mag = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)), norm = raw / mag, step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag;
  return { lo: Math.floor(lo / step) * step, hi: Math.ceil(hi / step) * step, step: step };
}
function isNum(v) { return typeof v === 'number' && isFinite(v); }

/* Category chart: bar / line / area series; stacked:true stacks positives per label upward and
   negatives downward with a thin outline on spec.totals; tooltips via <title>. */
function drawChart(el, spec) {
  if (!spec || !arr(spec.series).length) { el.innerHTML = '<p class="note">No data.</p>'; return; }
  var W = Math.max(el.clientWidth || 600, 280), H = spec.height || 230, L = W < 480 ? 46 : 60, R = 12, T = 12, B = 28, fmt = FMT[spec.yfmt || 'big'] || FMT.big;
  var labels = arr(spec.labels), n = labels.length, series = spec.series, bars = series.filter(function (x) { return x.kind === 'bar'; }), vals = [];
  var posSum = [], negSum = [];
  for (var i = 0; i < n; i++) { posSum.push(0); negSum.push(0); }
  var extraVals = function (sr) { arr(sr.lows).forEach(function (v) { if (isNum(v)) vals.push(v); }); arr(sr.errors).forEach(function (e) { if (Array.isArray(e)) e.forEach(function (v) { if (isNum(v)) vals.push(v); }); }); };
  if (spec.stacked) {
    bars.forEach(function (sr) { arr(sr.values).forEach(function (v, i) { if (!isNum(v) || i >= n) return; if (v >= 0) posSum[i] += v; else negSum[i] += v; }); });
    posSum.forEach(function (v) { vals.push(v); }); negSum.forEach(function (v) { vals.push(v); });
    arr(spec.totals).forEach(function (v) { if (isNum(v)) vals.push(v); });
    series.filter(function (x) { return x.kind !== 'bar'; }).forEach(function (sr) { arr(sr.values).forEach(function (v) { if (isNum(v)) vals.push(v); }); extraVals(sr); });
  } else series.forEach(function (sr) { arr(sr.values).forEach(function (v) { if (isNum(v)) vals.push(v); }); extraVals(sr); });
  if (!vals.length) { el.innerHTML = '<p class="note">No data.</p>'; return; }
  var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
  if (spec.zero !== false) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
  var ax = nice(lo, hi, 4), Y = function (v) { return T + (H - T - B) * (1 - (v - ax.lo) / (ax.hi - ax.lo)); };
  var slot = (W - L - R) / Math.max(n, 1), X = function (i) { return L + slot * (i + 0.5); }, afmt = axisFmt(fmt, ax.step);
  var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + esc(series.map(function (x) { return x.name; }).join(', ')) + '">';
  for (var v = ax.lo; v <= ax.hi + ax.step / 1e6; v += ax.step) { var y = Y(v); s += '<line class="' + (Math.abs(v) < ax.step / 1e6 ? 'zero' : 'grid') + '" x1="' + L + '" x2="' + (W - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '"/><text x="' + (L - 6) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + esc(afmt(v)) + '</text>'; }
  var tip = function (sr, i, v) { var t = esc(labels[i]) + ' · ' + esc(sr.name) + ': ' + esc(fmt(v)); var extra = arr(sr.tips)[i]; return t + (extra ? ' · ' + esc(extra) : ''); };
  if (spec.stacked) {
    var bw = slot * 0.72, posBase = [], negBase = [];
    for (var k = 0; k < n; k++) { posBase.push(0); negBase.push(0); }
    bars.forEach(function (sr) {
      arr(sr.values).forEach(function (v, i) {
        if (!isNum(v) || i >= n || v === 0) return;
        var from = v >= 0 ? posBase[i] : negBase[i], to = from + v, y0 = Y(from), y1 = Y(to);
        if (v >= 0) posBase[i] = to; else negBase[i] = to;
        s += '<rect x="' + (X(i) - bw / 2).toFixed(1) + '" y="' + Math.min(y0, y1).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(1, Math.abs(y0 - y1)).toFixed(1) + '" fill="' + sr.color + '" opacity=".9" stroke="#0C0E12" stroke-width=".6"><title>' + tip(sr, i, v) + '</title></rect>';
      });
    });
    arr(spec.totals).forEach(function (v, i) {
      if (!isNum(v) || i >= n) return;
      var y0 = Y(0), y1 = Y(v);
      s += '<rect x="' + (X(i) - bw / 2 - 1.5).toFixed(1) + '" y="' + (Math.min(y0, y1) - 1.5).toFixed(1) + '" width="' + (bw + 3).toFixed(1) + '" height="' + (Math.max(1, Math.abs(y0 - y1)) + 3).toFixed(1) + '" rx="2" fill="none" stroke="#ECEEF2" stroke-width="1" opacity=".8"><title>' + esc(labels[i]) + ' · ' + esc(spec.totalName || 'Total') + ': ' + esc(fmt(v)) + '</title></rect>';
    });
  } else {
    var nb = bars.length, gbw = slot * 0.72 / Math.max(nb, 1);
    bars.forEach(function (sr, bi) {
      arr(sr.values).forEach(function (v, i) {
        if (!isNum(v) || i >= n) return;
        var x = X(i) - slot * 0.36 + bi * gbw, y0 = Y(0), y1 = Y(v), col = arr(sr.colors)[i] || sr.color;
        s += '<rect x="' + x.toFixed(1) + '" y="' + Math.min(y0, y1).toFixed(1) + '" width="' + (gbw * 0.88).toFixed(1) + '" height="' + Math.max(1, Math.abs(y0 - y1)).toFixed(1) + '" rx="2" fill="' + col + '" opacity=".9"><title>' + tip(sr, i, v) + '</title></rect>';
      });
      arr(sr.errors).forEach(function (e, i) { // error bar [lo, hi] centred on the bar: a stem with caps
        if (!Array.isArray(e) || i >= n || !isNum(e[0]) || !isNum(e[1])) return;
        var cx = X(i) - slot * 0.36 + bi * gbw + gbw * 0.44, yl = Y(e[0]), yh = Y(e[1]), cw = Math.max(3, Math.min(6, gbw * 0.3));
        s += '<g class="err" stroke="#ECEEF2" stroke-width="1.2" opacity=".85"><line x1="' + cx.toFixed(1) + '" x2="' + cx.toFixed(1) + '" y1="' + yh.toFixed(1) + '" y2="' + yl.toFixed(1) + '"/><line x1="' + (cx - cw).toFixed(1) + '" x2="' + (cx + cw).toFixed(1) + '" y1="' + yh.toFixed(1) + '" y2="' + yh.toFixed(1) + '"/><line x1="' + (cx - cw).toFixed(1) + '" x2="' + (cx + cw).toFixed(1) + '" y1="' + yl.toFixed(1) + '" y2="' + yl.toFixed(1) + '"/><title>' + esc(labels[i]) + ' · range: ' + esc(fmt(e[0])) + ' → ' + esc(fmt(e[1])) + '</title></g>';
      });
    });
  }
  series.filter(function (x) { return x.kind === 'band'; }).forEach(function (sr) { // shaded area between lows and values, per contiguous run
    var hi = arr(sr.values), lo = arr(sr.lows), run = [];
    var flush = function () { if (run.length < 2) { run = []; return; } var d = ''; run.forEach(function (p, j) { d += (j ? ' L' : 'M') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }); for (var j = run.length - 1; j >= 0; j--) d += ' L' + run[j][0].toFixed(1) + ',' + run[j][2].toFixed(1); s += '<path d="' + d + 'Z" fill="' + sr.color + '" opacity=".16" stroke="' + sr.color + '" stroke-opacity=".35" stroke-width="1"><title>' + esc(sr.name) + '</title></path>'; run = []; };
    for (var i = 0; i < n; i++) { if (isNum(hi[i]) && isNum(lo[i])) run.push([X(i), Y(hi[i]), Y(lo[i])]); else flush(); }
    flush();
  });
  if (isNum(spec.dividerAt) && spec.dividerAt >= 0 && spec.dividerAt < n - 1) { var dx = (X(spec.dividerAt) + X(spec.dividerAt + 1)) / 2; s += '<line class="divider" x1="' + dx.toFixed(1) + '" x2="' + dx.toFixed(1) + '" y1="' + T + '" y2="' + (H - B) + '" stroke="#3A4252" stroke-dasharray="3 3"/><text x="' + (dx + 4).toFixed(1) + '" y="' + (T + 10) + '" text-anchor="start">forecast →</text>'; }
  series.filter(function (x) { return x.kind !== 'bar' && x.kind !== 'band'; }).forEach(function (sr) {
    var d = '', seg = '', pts = [];
    arr(sr.values).forEach(function (v, i) {
      if (!isNum(v) || i >= n) { if (seg) { d += seg; seg = ''; } return; }
      var x = X(i), y = Y(v); pts.push([x, y, v, i]); seg += (seg ? ' L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1);
    });
    if (seg) d += seg;
    if (sr.kind === 'area' && pts.length) s += '<path d="' + d + ' L' + pts[pts.length - 1][0].toFixed(1) + ',' + Y(Math.max(ax.lo, 0)).toFixed(1) + ' L' + pts[0][0].toFixed(1) + ',' + Y(Math.max(ax.lo, 0)).toFixed(1) + 'Z" fill="' + sr.color + '" opacity=".15"/>';
    if (d) s += '<path d="' + d + '" fill="none" stroke="' + sr.color + '" stroke-width="' + (sr.width || 2) + '" stroke-linejoin="round" stroke-linecap="round"' + (sr.dash ? ' stroke-dasharray="5 4"' : '') + '/>';
    if (!sr.nodots) pts.forEach(function (p) { s += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="' + (n > 20 ? 2 : 3) + '" fill="' + sr.color + '"><title>' + tip(sr, p[3], p[2]) + '</title></circle>'; });
  });
  var every = Math.ceil(n / Math.max(3, Math.floor((W - L - R) / 58)));
  labels.forEach(function (lb, i) { if (i % every !== 0 && i !== n - 1) return; s += '<text x="' + X(i).toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(lb) + '</text>'; });
  s += '</svg>';
  var legItem = function (x) { return '<span>' + (x.kind === 'err' ? '<i class="lerr" style="border-color:' + x.color + '"></i>' : x.kind === 'band' ? '<i style="background:' + x.color + ';opacity:.35"></i>' : x.dash ? '<i class="ldash" style="border-color:' + x.color + '"></i>' : '<i style="background:' + x.color + '"></i>') + esc(x.name) + '</span>'; };
  var leg = series.map(legItem).concat(arr(spec.legendExtra).map(legItem)).join('');
  if (spec.stacked && arr(spec.totals).length) leg += '<span><i style="background:transparent;border:1px solid #ECEEF2"></i>' + esc(spec.totalName || 'Total') + '</span>';
  el.innerHTML = s + '<div class="leg">' + leg + (spec.xlabel ? '<span style="margin-left:auto">' + esc(spec.xlabel) + '</span>' : '') + '</div>';
}

/* Price vs value: closes with the weighted IV@15 line, the scenario band and the hurdle prices.
   opts = {range, showIv, showBand, showH}; returns the range return text for the footer. */
function drawPrice(el, d, opts) {
  opts = obj(opts); var range = opts.range || '5Y';
  var showIv = opts.showIv !== false, showBand = opts.showBand !== false, showH = !!opts.showH;
  if (!d) { el.innerHTML = '<p class="note">No price history.</p>'; return null; }
  var all = range === '1Y' && arr(d.d).length > 30 ? d.d : arr(d.w);
  if (!all || all.length < 2) { el.innerHTML = '<p class="note">No price history.</p>'; return null; }
  var last = new Date(all[all.length - 1][0]), yrs = { '1Y': 1, '3Y': 3, '5Y': 5, '10Y': 10, 'MAX': 200 }[range] || 5, cut = new Date(last); cut.setFullYear(cut.getFullYear() - yrs);
  var pts = all.filter(function (p) { return new Date(p[0]) >= cut && isNum(p[1]); });
  if (pts.length < 2) pts = all.slice(-2);
  var W = Math.max(el.clientWidth || 600, 280), H = el.clientHeight || 260, L = W < 480 ? 44 : 56, R = 58, T = 14, B = 26;
  var closes = pts.map(function (p) { return p[1]; }), lo = Math.min.apply(null, closes), hi = Math.max.apply(null, closes);
  var over = []; if (showIv && d.iv15) over.push(d.iv15); if (showBand && d.lo && d.hi) over.push(d.lo, d.hi); if (showH) { if (d.h20) over.push(d.h20); if (d.h25) over.push(d.h25); }
  var cap = hi * 3; over.forEach(function (v) { if (v <= cap) { lo = Math.min(lo, v); hi = Math.max(hi, v); } });
  lo = Math.max(0, lo - (hi - lo) * 0.06); hi = hi + (hi - lo) * 0.06;
  var ax = nice(lo, hi, 4), Y = function (v) { return T + (H - T - B) * (1 - (v - ax.lo) / (ax.hi - ax.lo)); };
  var t0 = new Date(pts[0][0]).getTime(), t1 = last.getTime(), X = function (t) { return L + (W - L - R) * ((t - t0) / Math.max(1, (t1 - t0))); };
  var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="Price history against the engine\'s values">', afmt = axisFmt(FMT.money, ax.step);
  for (var v = ax.lo; v <= ax.hi + ax.step / 1e6; v += ax.step) { var y = Y(v); if (y < T - 1 || y > H - B + 1) continue; s += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '"/><text x="' + (L - 6) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + esc(afmt(v)) + '</text>'; }
  if (showBand && d.lo && d.hi) { var y1 = Y(Math.min(d.hi, ax.hi)), y2 = Y(Math.max(d.lo, ax.lo)); s += '<rect x="' + L + '" y="' + Math.min(y1, y2).toFixed(1) + '" width="' + (W - L - R) + '" height="' + Math.abs(y2 - y1).toFixed(1) + '" fill="rgba(122,162,255,.14)" stroke="rgba(122,162,255,.45)"><title>Scenario range at 15%: ' + esc(FMT.money(d.lo)) + ' – ' + esc(FMT.money(d.hi)) + '</title></rect>'; }
  var path = '';
  pts.forEach(function (p, i) { path += (i ? ' L' : 'M') + X(new Date(p[0]).getTime()).toFixed(1) + ',' + Y(p[1]).toFixed(1); });
  var area = path + ' L' + X(t1).toFixed(1) + ',' + Y(ax.lo).toFixed(1) + ' L' + X(t0).toFixed(1) + ',' + Y(ax.lo).toFixed(1) + 'Z';
  var up = closes[closes.length - 1] >= closes[0], col = up ? '#5BD69C' : '#FF8A8A';
  s += '<path d="' + area + '" fill="' + col + '" opacity=".12"/><path d="' + path + '" fill="none" stroke="' + col + '" stroke-width="1.8" stroke-linejoin="round"/>';
  var tag = function (y, label, color) { return '<rect x="' + (W - R + 3) + '" y="' + (y - 9).toFixed(1) + '" width="' + (R - 5) + '" height="18" rx="4" fill="' + color + '"/><text x="' + (W - R + (R - 5) / 2 + 3) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="middle" style="fill:#0C0E12;font-weight:600">' + esc(label) + '</text>'; };
  var line = function (v, label, color, dash, title) { if (!v || v > ax.hi || v < ax.lo) return; var y = Y(v); s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" stroke="' + color + '" stroke-width="1.5" stroke-dasharray="' + dash + '"><title>' + esc(title) + ': ' + esc(FMT.money(v)) + '</title></line>' + tag(y, label, color); };
  if (showH) { line(d.h20, '20%', '#B79CFF', '2 3', 'Price for a 20% return (Tier A)'); line(d.h25, '25%', '#B79CFF', '2 3', 'Price for a 25% return (Tier S)'); }
  if (showIv && d.iv15) line(d.iv15, 'IV', '#C9D4FF', '6 4', 'Weighted IV @15%');
  var lastC = closes[closes.length - 1], yl = Y(lastC);
  s += '<circle cx="' + X(t1).toFixed(1) + '" cy="' + yl.toFixed(1) + '" r="4" fill="' + col + '"><title>' + esc(pts[pts.length - 1][0]) + ': ' + esc(FMT.money(lastC)) + '</title></circle>' + tag(yl, lastC >= 1000 ? lastC.toFixed(0) : lastC.toFixed(lastC >= 100 ? 1 : 2), col);
  if (d.iv15 && d.iv15 > ax.hi) s += '<text x="' + (L + 6) + '" y="' + (T + 12) + '" style="fill:#C9D4FF">▲ IV@15% ' + esc(FMT.money(d.iv15)) + ' above chart</text>';
  var xl = [];
  if (range === '1Y') {
    var ms = []; pts.forEach(function (p) { var m = String(p[0]).slice(0, 7); if (ms.indexOf(m) < 0) ms.push(m); });
    var ev = Math.ceil(ms.length / Math.max(3, Math.floor((W - L - R) / 60)));
    ms.forEach(function (m, i) { if (i % ev) return; var f = pts.filter(function (p) { return String(p[0]).slice(0, 7) === m; })[0]; if (f) xl.push([X(new Date(f[0]).getTime()), m.slice(2)]); });
  } else {
    var ys = []; pts.forEach(function (p) { var y = String(p[0]).slice(0, 4); if (ys.indexOf(y) < 0) ys.push(y); });
    var evY = Math.ceil(ys.length / Math.max(2, Math.floor((W - L - R) / 70)));
    ys.forEach(function (y, i) { if (i % evY) return; var f = pts.filter(function (p) { return String(p[0]).slice(0, 4) === y; })[0]; if (f) { var x = X(new Date(f[0]).getTime()); if (x >= L + 10) xl.push([x, y]); } });
  }
  xl.forEach(function (t) { s += '<text x="' + t[0].toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(t[1]) + '</text>'; });
  s += '</svg>'; el.innerHTML = s;
  var r = (lastC / closes[0] - 1) * 100;
  return { text: range + ': ' + (r >= 0 ? '+' : '') + r.toFixed(0) + '% (' + pts[0][0] + ' → ' + pts[pts.length - 1][0] + ')', cls: r >= 0 ? 'pos' : 'neg' };
}

/* Price-target fan (Street sub-tab): the past year of closes, then dashed lines from the last close to the
   Street's low / mean / high 12-month targets, with a shaded fan and right-edge tags. spec = {pts, from, low, mean, high}. */
function drawFan(el, d) {
  if (!d || !arr(d.pts).length || arr(d.pts).length < 2) { el.innerHTML = '<p class="note">No price history.</p>'; return null; }
  var pts = d.pts.filter(function (p) { return isNum(p[1]); }), W = Math.max(el.clientWidth || 600, 280), H = el.clientHeight || 260, L = W < 480 ? 44 : 56, R = 62, T = 14, B = 26;
  var closes = pts.map(function (p) { return p[1]; }), lastC = isNum(d.from) ? d.from : closes[closes.length - 1], t0 = new Date(pts[0][0]).getTime(), tl = new Date(pts[pts.length - 1][0]).getTime(), t1 = tl + 365 * 864e5;
  var targets = [['low', d.low, '#FF8A8A', 'Low target'], ['mean', d.mean, '#C9D4FF', 'Mean target'], ['high', d.high, '#5BD69C', 'High target']].filter(function (t) { return isNum(t[1]); });
  var lo = Math.min.apply(null, closes.concat(targets.map(function (t) { return t[1]; }), [lastC])), hi = Math.max.apply(null, closes.concat(targets.map(function (t) { return t[1]; }), [lastC]));
  lo = Math.max(0, lo - (hi - lo) * 0.06); hi = hi + (hi - lo) * 0.06;
  var ax = nice(lo, hi, 4), Y = function (v) { return T + (H - T - B) * (1 - (v - ax.lo) / (ax.hi - ax.lo)); }, X = function (t) { return L + (W - L - R) * ((t - t0) / Math.max(1, t1 - t0)); };
  var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="Past year of closes and the Street\'s 12-month price targets">', afmt = axisFmt(FMT.money, ax.step);
  for (var v = ax.lo; v <= ax.hi + ax.step / 1e6; v += ax.step) { var y = Y(v); if (y < T - 1 || y > H - B + 1) continue; s += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '"/><text x="' + (L - 6) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + esc(afmt(v)) + '</text>'; }
  var path = ''; pts.forEach(function (p, i) { path += (i ? ' L' : 'M') + X(new Date(p[0]).getTime()).toFixed(1) + ',' + Y(p[1]).toFixed(1); });
  s += '<path d="' + path + '" fill="none" stroke="#ECEEF2" stroke-width="1.6" stroke-linejoin="round"/>';
  var xl = X(tl), xr = X(t1), yl = Y(lastC), loT = isNum(d.low) ? d.low : null, hiT = isNum(d.high) ? d.high : null;
  if (loT !== null && hiT !== null) s += '<path d="M' + xl.toFixed(1) + ',' + yl.toFixed(1) + ' L' + xr.toFixed(1) + ',' + Y(hiT).toFixed(1) + ' L' + xr.toFixed(1) + ',' + Y(loT).toFixed(1) + 'Z" fill="rgba(122,162,255,.14)" stroke="rgba(122,162,255,.4)"><title>Street target range: ' + esc(FMT.money(loT)) + ' – ' + esc(FMT.money(hiT)) + '</title></path>';
  var tag = function (y, label, color) { return '<rect x="' + (W - R + 3) + '" y="' + (y - 9).toFixed(1) + '" width="' + (R - 5) + '" height="18" rx="4" fill="' + color + '"/><text x="' + (W - R + (R - 5) / 2 + 3) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="middle" style="fill:#0C0E12;font-weight:600">' + esc(label) + '</text>'; };
  targets.forEach(function (t) { var yt = Y(t[1]); s += '<line x1="' + xl.toFixed(1) + '" y1="' + yl.toFixed(1) + '" x2="' + xr.toFixed(1) + '" y2="' + yt.toFixed(1) + '" stroke="' + t[2] + '" stroke-width="1.5" stroke-dasharray="5 4"><title>' + esc(t[3]) + ': ' + esc(FMT.money(t[1])) + '</title></line>' + tag(yt, FMT.money(t[1]), t[2]); });
  s += '<circle cx="' + xl.toFixed(1) + '" cy="' + yl.toFixed(1) + '" r="4" fill="#ECEEF2"><title>' + esc(d.fromDate || pts[pts.length - 1][0]) + ': ' + esc(FMT.money(lastC)) + '</title></circle>';
  s += '<line x1="' + xl.toFixed(1) + '" x2="' + xl.toFixed(1) + '" y1="' + T + '" y2="' + (H - B) + '" stroke="#3A4252" stroke-dasharray="3 3"/>';
  var ms = []; pts.forEach(function (p) { var m = String(p[0]).slice(0, 7); if (ms.indexOf(m) < 0) ms.push(m); });
  for (var k = 1; k <= 12; k++) { var dt = new Date(tl); dt.setMonth(dt.getMonth() + k); ms.push(dt.toISOString().slice(0, 7)); }
  var ev = Math.ceil(ms.length / Math.max(3, Math.floor((W - L - R) / 60)));
  ms.forEach(function (m, i) { if (i % ev) return; var tm = new Date(m + '-01').getTime(); if (tm < t0 || tm > t1) return; s += '<text x="' + X(tm).toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(m.slice(2)) + '</text>'; });
  s += '</svg>'; el.innerHTML = s;
  return { from: lastC, targets: targets.length };
}

/* ---- DOM state and wiring (browser only) */
var D = { app: null, meta: null, index: null, records: {}, pending: {}, charts: {}, state: defaultState(), stars: [], current: null, notice: '', embedded: false };
var STARS_KEY = 'oe-dcf.stars.v1';
function $(sel, r) { return (r || document).querySelector(sel); }
function $$(sel, r) { return Array.prototype.slice.call((r || document).querySelectorAll(sel)); }
function setHash(h) { try { if (history.replaceState) history.replaceState(null, '', h); else location.hash = h; } catch (e) { /* sandboxed / file: */ } }
function loadState() {
  try { var raw = localStorage.getItem(STORAGE_KEY); if (raw) D.state = normState(JSON.parse(raw)); } catch (e) { D.state = defaultState(); }
  try { var st = localStorage.getItem(STARS_KEY); D.stars = st ? normStars(JSON.parse(st)) : []; } catch (e2) { D.stars = []; }
}
function saveState() { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(D.state)); } catch (e) { /* private mode */ } }
function saveStars() { try { localStorage.setItem(STARS_KEY, JSON.stringify(D.stars)); } catch (e) { /* private mode */ } }

function drawPriceCard(card) {
  var el = $('.pchart', card); if (!el) return;
  var spec = D.charts.price, cb = function (sel) { var c = $(sel, card); return c ? c.checked : undefined; };
  var res = drawPrice(el, spec, { range: card.dataset.range || '5Y', showIv: cb('.tg-iv') !== false, showBand: cb('.tg-band') !== false, showH: cb('.tg-h') === true });
  var ret = $('.pcret', card); if (ret) { ret.textContent = res ? res.text : ''; ret.className = 'pcret ' + (res ? res.cls : ''); }
}
function drawVisible(rootEl) {
  rootEl = rootEl || D.app;
  $$('.chart[data-cid]', rootEl).forEach(function (el) { if (el.offsetParent !== null) drawChart(el, D.charts[el.dataset.cid]); });
  $$('.fanchart[data-cid]', rootEl).forEach(function (el) { if (el.offsetParent !== null) drawFan(el, D.charts[el.dataset.cid]); });
  $$('.pc', rootEl).forEach(function (card) { if (card.offsetParent !== null) drawPriceCard(card); });
}
function mount(html, charts) {
  D.charts = charts || {};
  D.app.innerHTML = html;
  window.scrollTo(0, 0);
  drawVisible(D.app);
}
function showNotice(text) { var n = $('#notice'); if (n) { n.textContent = text || ''; n.style.display = text ? 'block' : 'none'; } D.notice = ''; } // shown once, on the next list mount

function mountList() {
  D.current = null;
  document.title = "Owner's-Earnings DCF Ranking";
  mount(renderListHTML(D.meta, D.index, D.state, D.stars), {});
  showNotice(D.notice);
  var q = $('#q'); if (q && D.state.q) { try { q.focus(); q.setSelectionRange(q.value.length, q.value.length); } catch (e) { /* ignore */ } }
}
function refreshRows() {
  var tb = $('#t tbody'); if (!tb) return;
  tb.innerHTML = renderListRowsHTML(D.index, D.state, D.stars);
  var c = $('#count'); if (c) c.textContent = filterSortIndex(D.index, D.state, D.stars).length + ' shown';
  var wb = $('#watchbtn'); if (wb) { wb.outerHTML = watchButtonHTML(D.index, D.state, D.stars); }
  $$('#t thead th[data-sort]').forEach(function (th) { th.classList.toggle('sorted', th.dataset.sort === D.state.sort); });
  var so = $('#sort'); if (so && so.value !== D.state.sort) so.value = D.state.sort;
  saveState();
}
function navFor(ticker) {
  var idx = arr(D.index), pos = -1;
  for (var i = 0; i < idx.length; i++) if (String(idx[i].ticker).toUpperCase() === String(ticker).toUpperCase()) { pos = i; break; }
  if (pos < 0) return {};
  return { prev: pos > 0 ? idx[pos - 1].ticker : null, next: pos + 1 < idx.length ? idx[pos + 1].ticker : null, rank: pos + 1 };
}
function findRow(ticker) {
  var t = String(ticker || '').toUpperCase(), idx = arr(D.index);
  for (var i = 0; i < idx.length; i++) if (String(idx[i].ticker).toUpperCase() === t) return idx[i];
  return null;
}
function mountCompany(ticker, tab, record, sub) {
  D.current = { ticker: ticker, tab: tab, sub: sub || 'dcf' };
  document.title = ticker + ' — ' + (record.name || obj(record.score).name || '') + " · Owner's-Earnings DCF";
  mount(renderCompanyHTML(record, tab, navFor(ticker), sub), chartSpecs(record));
  watchHeader();
}
/* The tab bar condenses (ticker · last close · change · expected return) once the header scrolls away. */
function watchHeader() {
  var hero = $('.hero', D.app), bar = $('.tabbar', D.app);
  if (!hero || !bar) return;
  bar.classList.toggle('condensed', hero.getBoundingClientRect().bottom < 0);
}
var scrollTimer = null;
function onScroll() { // one layout read per ~50 ms (a timer, not rAF: rAF pauses in background tabs); condenses the bar once the header is above the viewport
  if (scrollTimer) return;
  scrollTimer = setTimeout(function () { scrollTimer = null; watchHeader(); }, 50);
}
function hashFor(ticker, tab, sub) { return '#' + ticker + (tab === 'overview' ? '' : '.' + tab) + (tab === 'forecast' && sub && sub !== 'dcf' ? '.' + sub : ''); }
function showTab(tab, sub) {
  var page = $('.page', D.app); if (!page || !D.current) return;
  $$('.tab', page).forEach(function (b) { var on = b.dataset.tab === tab; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); });
  $$('.pane', page).forEach(function (p) { p.classList.toggle('on', p.dataset.pane === tab); });
  D.current.tab = tab;
  if (sub) showSub(sub); else { setHash(hashFor(D.current.ticker, tab, D.current.sub)); drawVisible(page); }
}
function showSub(sub) { // the Forecast sub-tab (DCF / Street / Analysts)
  var page = $('.page', D.app); if (!page || !D.current) return;
  sub = SUB_KEYS.indexOf(sub) >= 0 ? sub : 'dcf';
  $$('.subtab', page).forEach(function (b) { var on = b.dataset.sub === sub; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); });
  $$('.subpane', page).forEach(function (p) { p.classList.toggle('on', p.dataset.sub === sub); });
  D.current.sub = sub;
  setHash(hashFor(D.current.ticker, D.current.tab, sub));
  drawVisible(page);
}
function embeddedRecord(ticker) {
  var sd = root.SITE_DATA; if (!sd) return null;
  var recs = sd.records || sd.data || {};
  if (Array.isArray(recs)) { for (var i = 0; i < recs.length; i++) if (recs[i] && String(recs[i].ticker).toUpperCase() === String(ticker).toUpperCase()) return recs[i]; return null; }
  if (recs[ticker]) return recs[ticker];
  var keys = Object.keys(recs);
  for (var j = 0; j < keys.length; j++) if (keys[j].toUpperCase() === String(ticker).toUpperCase()) return recs[keys[j]];
  return null;
}
function fetchJSON(path, cb) {
  if (typeof fetch !== 'function') { cb(new Error('fetch is not available in this browser')); return; }
  fetch(path, { cache: 'no-cache' }).then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + path);
    return r.json();
  }).then(function (data) { cb(null, data); }, function (e) { cb(e || new Error('fetch failed for ' + path)); });
}
function loadRecord(ticker, cb) {
  if (D.records[ticker]) { cb(null, D.records[ticker]); return; }
  if (D.embedded) { var r = embeddedRecord(ticker); if (r) D.records[ticker] = r; cb(r ? null : new Error('not embedded'), r); return; }
  if (D.pending[ticker]) { D.pending[ticker].push(cb); return; }
  D.pending[ticker] = [cb];
  fetchJSON('./data/' + encodeURIComponent(ticker) + '.json', function (err, data) {
    var cbs = D.pending[ticker]; delete D.pending[ticker];
    if (!err && data) D.records[ticker] = data;
    cbs.forEach(function (f) { f(err, data); });
  });
}
/* #T · #T.tab · #T.forecast.<dcf|street|analysts>; splits at the LAST '.' so dotted tickers route (#BRK.B.data). */
function parseHash(h) {
  h = String(h || '').replace(/^#/, '');
  try { h = decodeURIComponent(h); } catch (e) { /* keep raw */ }
  if (!h) return { ticker: null, tab: 'overview', sub: 'dcf' };
  h = h.replace(/\//g, '.'); // legacy v2 form "#T/tab"
  if (!/^[A-Za-z0-9._-]+$/.test(h)) return { ticker: h, tab: 'overview', sub: 'dcf', bad: true };
  var sub = 'dcf', i = h.lastIndexOf('.');
  if (i > 0 && SUB_KEYS.indexOf(h.slice(i + 1).toLowerCase()) >= 0 && /\.forecast$/i.test(h.slice(0, i))) { sub = h.slice(i + 1).toLowerCase(); h = h.slice(0, i); i = h.lastIndexOf('.'); }
  if (i > 0) { var tab = h.slice(i + 1).toLowerCase(); if (TAB_KEYS.indexOf(tab) >= 0) return { ticker: h.slice(0, i), tab: tab, sub: tab === 'forecast' ? sub : 'dcf' }; }
  return { ticker: h, tab: 'overview', sub: 'dcf' };
}
function route() {
  if (!D.index) return;
  var p = parseHash(location.hash);
  if (!p.ticker) { if (D.current || !$('#listView', D.app)) mountList(); return; }
  var row = findRow(p.ticker);
  if (!row || p.bad) {
    D.notice = 'No company "' + p.ticker + '" in this ranking — back to the list.';
    setHash('#'); mountList(); return;
  }
  var ticker = row.ticker;
  if (D.current && D.current.ticker === ticker) { if (D.current.tab !== p.tab) showTab(p.tab, p.tab === 'forecast' ? p.sub : null); else if (p.tab === 'forecast' && D.current.sub !== p.sub) showSub(p.sub); return; }
  var token = (D.routeToken = {});
  var cached = D.records[ticker];
  if (!cached) D.app.innerHTML = '<div class="card loading" role="status">Loading ' + esc(ticker) + '…</div>';
  loadRecord(ticker, function (err, record) {
    if (D.routeToken !== token) return; // a later navigation won
    if (err || !record) {
      if (D.embedded) { D.current = { ticker: ticker, tab: p.tab }; mount(renderMissingHTML(row, D.meta), {}); return; }
      D.current = { ticker: ticker, tab: p.tab };
      mount('<article class="page open"><nav class="dnav"><a class="back" href="#">← Ranking</a></nav>' + renderErrorHTML('The record for ' + ticker + ' could not be loaded.', err && err.message) + '</article>', {});
      return;
    }
    mountCompany(ticker, p.tab, record, p.sub);
  });
}
function wireEvents() {
  document.addEventListener('click', function (e) {
    var tb = e.target.closest ? e.target.closest('.tab') : null;
    if (tb && D.current) { showTab(tb.dataset.tab); return; }
    var stb = e.target.closest ? e.target.closest('.subtab') : null;
    if (stb && D.current) { showSub(stb.dataset.sub); return; }
    var ffb = e.target.closest ? e.target.closest('.ffseg button') : null;
    if (ffb) { var fcard = ffb.closest('.ffcard'); $$('.ffseg button', fcard).forEach(function (x) { var on = x === ffb; x.classList.toggle('on', on); x.setAttribute('aria-pressed', String(on)); }); $$('.ffpane', fcard).forEach(function (pn) { pn.classList.toggle('on', pn.dataset.ff === ffb.dataset.ff); }); return; }
    var wb = e.target.closest ? e.target.closest('#watchbtn') : null;
    if (wb) { D.state.watch = !D.state.watch; refreshRows(); return; }
    var star = e.target.closest ? e.target.closest('button.star[data-star]') : null;
    if (star) { var t = String(star.dataset.star || '').toUpperCase(), k = D.stars.indexOf(t); if (k >= 0) D.stars.splice(k, 1); else D.stars.push(t); saveStars(); refreshRows(); return; }
    var rb = e.target.closest ? e.target.closest('.ranges button') : null;
    if (rb) { var card = rb.closest('.pc'); $$('.ranges button', card).forEach(function (x) { var on = x === rb; x.classList.toggle('on', on); x.setAttribute('aria-pressed', String(on)); }); card.dataset.range = rb.dataset.r; drawPriceCard(card); return; }
    var sb = e.target.closest ? e.target.closest('#tierseg button, #fitseg button') : null;
    if (sb) {
      var segEl = sb.parentNode; $$('button', segEl).forEach(function (x) { var on = x === sb; x.classList.toggle('on', on); x.setAttribute('aria-pressed', String(on)); });
      if (segEl.id === 'tierseg') D.state.tier = sb.dataset.f; else D.state.fit = sb.dataset.fit;
      refreshRows(); return;
    }
    var th = e.target.closest ? e.target.closest('#t thead th[data-sort]') : null;
    if (th) { D.state.sort = th.dataset.sort; refreshRows(); }
  });
  document.addEventListener('change', function (e) {
    if (e.target.matches('.toggles input')) { drawPriceCard(e.target.closest('.pc')); return; }
    if (e.target.id === 'sort') { D.state.sort = e.target.value; refreshRows(); }
  });
  document.addEventListener('input', function (e) { if (e.target.id === 'q') { D.state.q = e.target.value; refreshRows(); } });
  window.addEventListener('hashchange', route);
  var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { drawVisible(D.app); }, 150); });
  window.addEventListener('scroll', onScroll, { passive: true });
}
function boot() {
  D.app = document.getElementById('app'); if (!D.app) return;
  loadState(); wireEvents();
  var sd = root.SITE_DATA;
  if (sd && typeof sd === 'object') {
    D.embedded = true; D.meta = obj(sd.meta); D.index = arr(sd.index);
    route(); return;
  }
  D.app.innerHTML = '<div class="card loading" role="status">Loading the ranking…</div>';
  fetchJSON('./meta.json', function (e1, meta) {
    if (e1) { D.app.innerHTML = renderErrorHTML('meta.json could not be fetched', e1.message); return; }
    fetchJSON('./index.json', function (e2, index) {
      if (e2) { D.app.innerHTML = renderErrorHTML('index.json could not be fetched', e2.message); return; }
      D.meta = obj(meta); D.index = arr(index);
      route();
    });
  });
}

/* ------------------------------------------------------------ 7. exports */
var API = {
  esc: esc, num: num, fmtMoney: fmtMoney, fmtBig: fmtBig, fmtCnt: fmtCnt, fmtPct: fmtPct, fmtPts: fmtPts, fmtX: fmtX, fmtCap: fmtCap, signCls: signCls, safeId: safeId, md: md,
  tierForIrr: tierForIrr, liveView: liveView, hurdlePrices: hurdlePrices, sensitivity: sensitivity, modelFit: modelFit,
  renderListHTML: renderListHTML, renderListRowsHTML: renderListRowsHTML, renderRowHTML: renderRowHTML, renderStaleHTML: renderStaleHTML, filterSortIndex: filterSortIndex, defaultState: defaultState, normState: normState,
  normStars: normStars, isWatched: isWatched, watchCount: watchCount, watchButtonHTML: watchButtonHTML, COLS: COLS,
  floorFlags: floorFlags, oeHistory: oeHistory, oeForecastSeries: oeForecastSeries, renderForecastDCF: renderForecastDCF, renderForecastStreet: renderForecastStreet, renderForecastAnalysts: renderForecastAnalysts, chartSpecsStreet: chartSpecsStreet, drawFan: drawFan, SUBTABS: SUBTABS, SUB_KEYS: SUB_KEYS, hashFor: hashFor,
  renderCompanyHTML: renderCompanyHTML, renderHeader: renderHeader, renderPriceChart: renderPriceChart, renderOverview: renderOverview, renderFinancials: renderFinancials, renderDividends: renderDividends,
  renderSegments: renderSegments, renderForecast: renderForecast, renderAnalysis: renderAnalysis, renderData: renderData, renderMissingHTML: renderMissingHTML, renderErrorHTML: renderErrorHTML,
  renderAbout: renderAbout, renderPerformance: renderPerformance, financialPerformance: financialPerformance, renderStreet: renderStreet, renderFilings: renderFilings, renderTabSummary: renderTabSummary,
  chartSpecs: chartSpecs, chartSpecsFinancials: chartSpecsFinancials, chartSpecsDividends: chartSpecsDividends, chartSpecsSegments: chartSpecsSegments, chartSpecsForecast: chartSpecsForecast, priceSpec: priceSpec,
  parseHash: parseHash, TABS: TABS, TAB_KEYS: TAB_KEYS, SORTS: SORTS, TIER_ACCENT: TIER_ACCENT,
  drawChart: drawChart, drawPrice: drawPrice // DOM-touching only through the element they are handed
};
if (typeof module !== 'undefined' && module.exports) module.exports = API;
else {
  API.route = route; API.state = D;
  root.App = API;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  }
}
})(typeof window !== 'undefined' ? window : this);
