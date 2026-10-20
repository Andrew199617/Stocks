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
var C_REV = '#7AA2FF', C_NI = '#5BD69C', C_OE = '#C9D4FF', C_OCF = '#7484A0', C_CAPEX = '#F2B84B', C_INTANG = '#C99A3C', C_SBC = '#F08A4B', C_CASH = '#7AA2FF', C_DEBT = '#F08A4B', C_FCF = '#9AD6B4';
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
/* The minus sign is decided on the ROUNDED text: a value that rounds to zero (-4,000 in millions, -0.04%) prints without
   one, never "-0.00" / "-0.0%". */
function minus(v, txt) { return v < 0 && /[1-9]/.test(txt) ? '-' : ''; }
function fmtMoney(v, d) {
  v = num(v); if (v === null) return '—';
  var s = fixed(v, d === undefined ? 2 : d);
  return minus(v, s) + '$' + s;
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
/* A formatted '$' amount restated in `cur`: the ISO code replaces the '$' (a non-USD block's filed legs and DPS); null —
   a block that does not record its unit (divCurrency) — prints the bare number; undefined / 'USD' keep the '$'. */
function curText(t, cur) { return cur === null ? String(t).replace('$', '') : (!cur || cur === 'USD' ? t : String(t).replace('$', cur + '\u00a0')); }
function fmtBigCur(v, cur) { return curText(fmtBig(v), cur ? esc(cur) : cur); }
function fmtDpsCur(v, cur) { return curText(fmtDps(v), cur ? esc(cur) : cur); }
/* The unit of fundamentals.json's dividends amounts (legs, DPS) — ruling-sheet Q8 bug 3, verifier round 2. Under the
   one-currency rule a non-USD block records it (`dividends.currency`); a USD file's block has no key and is USD. A non-USD
   file whose block has no key was written before 2026-10-19: its readers took a USD fact first (TLK's dividends paid is the
   filed USD 1,099,000,000, CX's $90M), so the file's `currency` is NOT the legs' unit — cur null, unrecorded. */
function divCurrency(fund) {
  fund = obj(fund); var d = obj(fund.dividends);
  if (typeof d.currency === 'string' && d.currency) return { cur: d.currency, recorded: true, file: d.currency };
  if (typeof fund.currency === 'string' && fund.currency && fund.currency !== 'USD') return { cur: null, recorded: false, file: fund.currency };
  return { cur: 'USD', recorded: true, file: 'USD' };
}
/* The intangible purchases fundamentals.json's fcf deducts on top of the PP&E capex row (engine 5.5 capex): ocf − capex − fcf
   of the same row, null without all three or when it is zero (the row then deducts PP&E alone). */
function intangCapex(r) {
  r = obj(r); var o = num(r.ocf), c = num(r.capex), f = num(r.fcf);
  if (o === null || c === null || f === null) return null;
  var x = o - c - f; return Math.abs(x) < 0.5 ? null : x;
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
  var p = x * 100, s = fixed(p, d), neg = minus(p, s);
  return (neg || (signed ? '+' : '')) + s + '%';
}
function fmtPts(p, d) { // a value already in percent units, signed: "+38%"
  p = num(p); if (p === null) return '—';
  d = d === undefined ? 0 : d;
  var s = fixed(p, d);
  return (minus(p, s) || '+') + s + '%';
}
function fmtX(v, d) {
  v = num(v); if (v === null) return '—';
  var s = fixed(v, d === undefined ? 1 : d);
  return minus(v, s) + s + '×';
}
function fmtCap(v) { v = num(v); return v === null ? '—' : (v < 0 ? '-' : '') + '$' + fixed(v, 2) + 'B'; }
/* A filed per-share dividend keeps its filed precision: $0.155 stays $0.155 (never rounded to two decimals);
   at least two decimals, at most four, float noise (1.4400000000000002) trimmed. */
function dpsDecimals(v) { var s = Math.abs(v).toFixed(6).replace(/0+$/, ''), i = s.indexOf('.'); return i < 0 ? 2 : Math.min(4, Math.max(2, s.length - i - 1)); }
function fmtDps(v) { v = num(v); return v === null ? '—' : fmtMoney(v, dpsDecimals(v)); }
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
function isoDay(x) { return typeof x === 'string' && /^\d{4}-\d{2}-\d{2}/.test(x) ? x.slice(0, 10) : null; }
function fmtFactor(f) { return String(Number(Number(f).toPrecision(6))); } // a split factor as Python's {:g}: 2 → "2", 1.5 → "1.5", 0.1 → "0.1"
/* record.live_withheld (build_site live_shown): a live.json whose close is older than the scored analysis (Nasdaq had not
   posted the scored session yet), or one left from an earlier run of a re-scored name, is not shown as current — record.live is null, the scored figures are the current ones
   and this says why; [Codex review r2 of PR #47] so is every live repricing of a record whose acquired-IPR&D charge was
   deducted by hand (reason iprd_share_count_unverified: reprice.py never reprices it, live.json or not); [Codex review r6]
   and of a record whose latest engine run make_score refused for an unresolved acquired-IPR&D charge (reason iprd_unresolved);
   [Codex review r11] and any live.json beside a score.json not built from the latest engine run (reason score_not_from_this_run).
   {reason, price, price_date, scored_date, method, note}, or null when nothing was withheld. */
function liveWithheld(record) {
  var w = obj(obj(record).live_withheld);
  if (!Object.keys(w).length) return null;
  return { reason: typeof w.reason === 'string' ? w.reason : null, price: num(w.price), price_date: isoDay(w.price_date), scored_date: isoDay(w.scored_date), method: typeof w.method === 'string' ? w.method : null, note: typeof w.note === 'string' ? w.note : '' };
}
function pendingText(w) { // plain text; escaped where it is printed
  w = obj(w);
  // [Codex review r2 of PR #47] reprice.py never reprices a record whose acquired-IPR&D charge was deducted by hand
  if (w.reason === 'iprd_share_count_unverified') return 'Live figures withheld — the acquired-IPR&D charge was deducted by hand (share count unverified), so the scored figures stand';
  // [Codex review r6 of PR #47] nor one whose latest run make_score refused for an unresolved acquired-IPR&D charge
  if (w.reason === 'iprd_unresolved') return 'Live figures withheld — the latest run left an acquired-IPR&D charge unresolved, so the scored figures stand';
  // [Codex review r11 of PR #47] nor any live repricing beside a score.json from another engine run
  if (w.reason === 'score_not_from_this_run') return 'Live figures withheld — the latest engine run is not scored yet (make_score refused it or has not run on it), so the scored figures stand';
  if (w.price_date && w.scored_date && w.price_date >= w.scored_date) return 'Live figures pending — the live repricing on file predates the ' + w.scored_date + ' score';
  return 'Live figures pending — ' + (w.price_date && w.scored_date ? 'the ' + w.price_date + ' close predates the ' + w.scored_date + ' analysis' : 'the last close on file predates the analysis');
}
/* The close a page that is not live shows as the current price (header, condensed bar): prices.stats.last with its date and
   1-day change — but never a close older than the scored analysis on a record whose live.json was withheld for exactly that
   (the scored price is the current one there). Null when there is no such close. */
function currentClose(record) {
  var st = obj(obj(obj(record).prices).stats), last = num(st.last), date = typeof st.last_date === 'string' && st.last_date ? st.last_date : null;
  if (last === null || !date) return null;
  var w = liveWithheld(record);
  if (w && w.scored_date && date.slice(0, 10) < w.scored_date) return null;
  return { last: last, date: date, chg: num(st.change_1d_pct) };
}
/* record.split_restated (build_site restate_split): a split since the scored run. Every per-share figure of the run in the
   record is already divided by `factor` (today's share units, next to the last close) and its share counts multiplied by
   it; IRRs, tiers, upside and market caps do not change. {factor, split ('2:1'), scored_date, price_date, as_scored (the run
   figures as scored), note}, or null without a split. */
function splitInfo(record) {
  var sp = obj(obj(record).split_restated), f = num(sp.factor);
  if (f === null || !(f > 0) || Math.abs(f - 1) < 1e-9) return null;
  return { factor: f, split: typeof sp.split === 'string' && sp.split ? sp.split : fmtFactor(f) + 'x', scored_date: isoDay(sp.scored_date), price_date: isoDay(sp.price_date),
    as_scored: obj(sp.as_scored), note: typeof sp.note === 'string' ? sp.note : '' };
}
/* What a filed per-share figure (fundamentals.json, as filed) is divided by to read in today's share units after a split
   since scoring: the factor when its row is still on the pre-split basis, else 1. Pre-split = the period ends on or before
   the scored date and the row's filed diluted count sits nearer (log scale) the restated run count ÷ factor than the
   restated count itself. The reference is the run's own count for that fiscal year (record.history, which build_site
   multiplied by the factor), else numbers.shares_diluted_latest (restated). A row whose comparatives a post-split filing
   restated reads ~1× and is left alone; a row without a share count, or a record without a reference, is left as filed. */
function splitRefs(record) {
  var byEnd = {}, byFy = {};
  arr(obj(record).history).forEach(function (r) {
    r = obj(r); var sh = num(r.shares_diluted), e = isoDay(r.period_end);
    if (sh === null || !(sh > 0)) return;
    if (e) byEnd[e] = sh;
    if (r.fy_label !== null && r.fy_label !== undefined && r.fy_label !== '') byFy[String(r.fy_label)] = sh;
  });
  var latest = num(obj(obj(record).numbers).shares_diluted_latest);
  return { byEnd: byEnd, byFy: byFy, latest: latest !== null && latest > 0 ? latest : null };
}
function splitDivisor(sp, refs, sh, end, fy) {
  sh = num(sh); refs = obj(refs);
  if (!sp || sh === null || !(sh > 0)) return 1;
  var e = isoDay(end);
  if (e && sp.scored_date && e > sp.scored_date) return 1;
  var ref = (e && obj(refs.byEnd)[e]) || (fy !== null && fy !== undefined && obj(refs.byFy)[String(fy)]) || refs.latest;
  if (!ref) return 1;
  return Math.abs(Math.log(sh * sp.factor / ref)) < Math.abs(Math.log(sh / ref)) ? sp.factor : 1;
}
/* The split notes the tabs print (HTML). splitChip: the header chip; splitBrief: the short line by the verdict; splitNoteHTML:
   build_site's own note plus a tab-specific sentence. '' without a split. */
function splitChip(sp) { return sp ? '<span class="chip lvchip splitchip" title="' + esc(sp.note) + '">Restated for a ' + esc(sp.split) + ' split since scoring</span>' : ''; }
function splitBrief(sp) {
  if (!sp) return '';
  return '<p class="note splitnote"><b>Restated for a ' + esc(sp.split) + ' split since scoring</b>' + (sp.scored_date ? ' (scored ' + esc(sp.scored_date) + ')' : '') + ': every per-share figure of the run on this page is in today\'s share units (÷ ' + esc(fmtFactor(sp.factor))
    + ') next to the last close; IRRs, tiers and upside are unchanged. The one-liner and the write-up quote the run as scored.</p>';
}
function splitNoteHTML(sp, extra) { return sp ? '<p class="note splitnote"><b>Restated for a ' + esc(sp.split) + ' split since scoring.</b> ' + esc(sp.note) + (extra ? ' ' + extra : '') + '</p>' : ''; }
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
function tile(k, v, cls, sub, title) { // title: plain text shown as the tooltip (a ⓘ cue marks the tile)
  return '<div class="tile"' + (title ? ' title="' + esc(title) + '"' : '') + '><span class="k">' + k + '</span><span class="v ' + (cls || '') + '">' + v + '</span>' + (sub ? '<span class="tsub">' + sub + '</span>' : '') + '</div>';
}
/* A yield as fundamentals.py marks it: dividends.yields_display[key] = {value, bound: exact|lower|upper|indeterminate|null,
   label ("≥ 0.49%", "≤ 2.78%", "≈ 3.53% (incomplete)", "—"), note}. The label is printed, never the bare number, and the note
   goes in the tooltip; an older block without yields_display falls back to the plain figure. */
var BOUND_WORDS = { lower: 'lower bound', upper: 'upper bound', indeterminate: 'incomplete' };
function yieldShown(d, key) {
  d = obj(d); var yd = obj(obj(d.yields_display)[key]);
  if (typeof yd.label === 'string' && yd.label) {
    var b = typeof yd.bound === 'string' ? yd.bound : null;
    return { text: esc(yd.label), note: yd.note ? String(yd.note) : '', bound: b, partial: !!b && b !== 'exact', word: BOUND_WORDS[b] || '' };
  }
  return { text: fmtPct(d[key]), note: '', bound: null, partial: false, word: '' };
}
function yieldTile(d, key, name, cls, sub, more) { // more: an extra tooltip sentence after the yield's own note
  var y = yieldShown(d, key), m = /^(.*?)\s*(\([^)]*\))$/.exec(y.text); // "≈ 3.53% (incomplete)": the parenthetical on its own small line, not wrapped mid-word in the 20px figure
  var v = m ? m[1] + ' <span class="vsfx">' + m[2] + '</span>' : y.text;
  return tile(name, v, y.partial ? (cls ? cls + ' ' : '') + 'bounded' : cls, joinNonEmpty([sub, y.partial && !m ? '<b class="bword">' + y.word + '</b>' : ''], ' · '), joinNonEmpty([y.note, more || ''], ' — '));
}
function section(title, body, note, cls) { // no title → no <h2> at all (an empty heading is noise in the accessibility tree)
  return '<section class="sec ' + (cls || '') + '">' + (title ? '<h2>' + title + '</h2>' : '') + (note ? '<p class="note">' + note + '</p>' : '') + body + '</section>';
}
function chartDiv(id, cls) { return '<div class="chart ' + (cls || '') + '" data-cid="' + esc(id) + '"></div>'; }
function gaugeScale(irr) {
  var scale = 30;
  if (irr !== null && irr * 100 > 30) scale = Math.floor(irr * 100 / 10 + 1) * 10;
  return scale;
}

function renderHeader(record, stars, repo) {
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
    fsub = { sbc_exceeds_cash: 'F · SBC exceeds cash generation', no_cash_generation: 'F · no cash generation', payable_earnings_nonpositive: 'F · payable earnings non-positive' }[fs] || "F · no positive owner's earnings";
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
    // a live.json withheld for predating the analysis (record.live_withheld): its close is not the current price either —
    // the scored price is, with the reason beside it (the note in the tooltip); a close that IS current still shows
    var cc = currentClose(record), wh = liveWithheld(record);
    var pend = wh ? '<span class="lvpend"' + (wh.note ? ' title="' + esc(wh.note) + '"' : '') + '>' + esc(pendingText(wh)) + '</span>' : '';
    sub = 'Probability-weighted IRR at ' + fmtMoney(price);
    priceTile = '<div class="hstat"><span class="k">' + (cc ? 'Last close' : wh ? 'Scored price' : 'Price used') + '</span><span class="v mono">' + fmtMoney(cc ? cc.last : price) + (cc ? chgS : '') + '</span><span class="tsub">'
      + joinNonEmpty([cc ? esc(cc.date) + ' · scored at ' + fmtMoney(price) + ' (' + esc(s.analysis_date || '') + ')' : (wh ? '' : esc(n.price_source || '') + ' · ' + esc(s.analysis_date || '')), pend, rangeSub], ' · ') + '</span></div>';
    ttile = '<span class="ttile" style="background:' + acc + '">' + esc(tier) + '</span>';
  }
  var chip = tierShiftChip(v), schip = splitChip(splitInfo(record));
  var scoredChip = v.is_live ? '<span class="chip lvchip muted" title="Scored on ' + esc(v.scored_date) + '">Scored ' + esc(v.scored_tier) + ' · live ' + esc(tier) + '</span>' : '';
  // watchlist: a repo name carries the fixed repo star chip; any other name gets the per-device star button (local, not synced)
  // the index row is authoritative for the repo flag (a skipped record's embedded row.watchlist can lag — SITE_CONTRACT
  // "Watchlist is in the data"): with a repo list in hand the flag comes from it alone; record.row only without one
  var hticker = String(s.ticker || record.ticker || row.ticker || ''), hrow = Array.isArray(repo) ? { ticker: hticker || row.ticker } : (Object.keys(row).length ? row : { ticker: hticker });
  var wchip = isRepo(hrow, repo) ? '<span class="chip lvchip wchip" title="On the repo watchlist (_system/watchlist.json)">★ Watchlist <span class="sub">repo</span></span>'
    : (hticker ? starButtonHTML(hticker, isStarred(hrow, stars), 'hstar') : '');
  return '<header class="hero" style="--acc:' + acc + '"><div class="hrow">' + ttile
    + '<div class="hname"><div class="hline"><span class="htick">' + esc(s.ticker || record.ticker) + '</span><span class="hco">' + esc(s.name || record.name) + '</span>' + (chip || scoredChip) + schip + wchip + '</div><span class="note">' + meta + '</span></div></div>'
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
  var cc = currentClose(record), hasLast = !!cc, chg = num(st.change_1d_pct); // a close older than a withheld live.json's analysis is not current (currentClose)
  var price = v.is_live ? v.price : (hasLast ? cc.last : v.price), showChg = chg !== null && (v.is_live || hasLast);
  return '<div class="tabsum" aria-hidden="true"><span class="ttile sm" style="background:' + acc + '">' + esc(v.tier) + '</span><b class="mono">' + esc(s.ticker || record.ticker || row.ticker) + '</b>'
    + '<span class="mono" title="' + (v.is_live || hasLast ? 'Last close' : liveWithheld(record) ? 'Scored price — live figures pending' : 'Scored price') + '">' + fmtMoney(price) + '</span>' + (showChg ? '<span class="mono ' + ((chg || 0) >= 0 ? 'pos' : 'neg') + '">' + fmtPts(chg, 2) + '</span>' : '')
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
/* The price card: a 1D · 5D · 1M · YTD · 3M · 6M · 1Y · 5Y · Max range row (a range without data is disabled,
   "not captured yet"; the active one carries the period-return badge), the chart (crosshair on hover / drag,
   arrow keys when focused), the legend and the sources note. drawPriceCard() redraws it; the default range is
   1Y when the record has daily closes, else 5Y. */
function renderPriceChart(record) {
  var pr = obj(record.prices), spec = priceSpec(record), avail = priceRanges(spec), def = defaultRange(spec), body;
  if (def) {
    var ranges = PRICE_RANGES.map(function (r) {
      var ok = avail[r], on = r === def;
      return '<button type="button" data-r="' + r + '" class="' + (on ? 'on' : '') + '" aria-pressed="' + on + '"' + (ok ? '' : ' disabled title="not captured yet"') + '>' + (r === 'MAX' ? 'Max' : r) + '<span class="rb"></span></button>';
    }).join('');
    var toggles = '<label><input type="checkbox" class="tg-iv" checked> Weighted value</label><label><input type="checkbox" class="tg-band" checked> Bear–bull range</label><label><input type="checkbox" class="tg-h"> 20% / 25% hurdle prices</label>';
    var iday = spec.intraday, intraDef = def === '1D' || def === '5D';
    var srcNote = 'Prices: ' + esc(pr.source || '') + ', through ' + esc(pr.as_of || '') + '.'
      + (iday ? ' Intraday: ' + esc(iday.source || 'api.nasdaq.com chart') + ' for ' + esc(iday.session_date || '') + (iday.complete === false && capturedTo(iday) ? ', captured to ' + esc(capturedTo(iday)) + ' (partial — the next prices.py run after 8 PM ET completes it)' : '') + ' (5-minute bars, pre-market and after-hours included' + (arr(pr.sessions_5d).length ? ', ' + arr(pr.sessions_5d).length + ' session' + (arr(pr.sessions_5d).length === 1 ? '' : 's') + ' kept for 5D' : '') + ').' : ' Intraday (1D · 5D) not captured yet for this name.')
      + " The valuation lines are the engine's values at a 15% discount rate — the price at which the expected return equals the hurdle. Where the price sits against them is the whole screen.";
    body = '<div class="pcbar"><div class="ranges" role="group" aria-label="Price range">' + ranges + '</div><div class="toggles">' + toggles + '</div></div>'
      + '<div class="pchart" data-cid="price" tabindex="0" aria-label="Price chart — hover, drag or use the arrow keys to read a point"></div>'
      + '<p class="note pcnote"' + (intraDef ? '' : ' hidden') + '>Value lines hidden on intraday ranges — the axis is tight to the session.</p>'
      + '<div class="pcfoot"><span class="legend"><i style="background:' + C_PRICE + '"></i>Price</span><span class="legend"><i class="dash" style="border-color:' + C_IV + '"></i>Weighted IV @15%</span><span class="legend"><i style="background:' + C_BAND + ';border:1px solid rgba(122,162,255,.6)"></i>Scenario range (super bear → super bull)</span><span class="pcret"></span></div>'
      + '<p class="note">' + srcNote + '</p>';
  } else {
    body = priceVsValueLine(record) + "<p class=\"note\">No price history pulled for this name yet (prices.py) — the number line shows today's price against every scenario's value.</p>";
  }
  return '<section class="sec pcsec"><div class="card pc" data-range="' + esc(def || '') + '">' + body + '</div></section>';
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
  var sp = splitInfo(record), spH = sp ? '<p class="note">Override values are as entered for the scored run, before the ' + esc(sp.split) + ' split since scoring (not restated)'
    + (impH ? '; the base OE/share figures above are restated to today\'s share units' : '') + '.</p>' : '';
  return '<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Field</th><th class="num">Value</th><th>Kind</th><th>Source</th><th>Years filled</th></tr></thead><tbody>' + rows + '</tbody></table></div>' + impH + reasons + spH + '</div>';
}

/* ---- profile cards (record.profile from profile.py; every card renders gracefully without it) */
/* record.profile joins two files: profile.json (SEC: about, filings — committed) and street.json (Nasdaq: street, market,
   its fetched_at as street_fetched_at — a gitignored cache), so either can exist without the other. profilePulled: the
   SEC part is there (any key beyond the street ones). streetPulled: the Nasdaq pull ran — street.json's fetched_at, or a
   record that carries street_fetched_at: null (built without street.json: a fresh clone before its first refresh) says
   not yet; a record built before the split (no street_fetched_at key) counts any profile, as before. */
var STREET_KEYS = ['street', 'market', 'street_fetched_at'];
function profilePulled(p) { return Object.keys(obj(p)).some(function (k) { return STREET_KEYS.indexOf(k) < 0; }); }
function streetPulled(p) {
  p = obj(p);
  if (p.street_fetched_at) return true;
  return Object.prototype.hasOwnProperty.call(p, 'street_fetched_at') ? false : Object.keys(p).length > 0;
}
function safeUrl(u) { u = String(u || ''); return /^https?:\/\//i.test(u) ? u : ''; }
function extLink(url, text) { var u = safeUrl(url); return u ? '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + text + '</a>' : text; }
/* "Read more": a description past ~600 characters is cut at a sentence end inside the second half of the window
   (else at a word), the remainder hidden until the button is tapped. {short, more} — more is '' when nothing is hidden. */
var ABOUT_CLAMP = 600;
function clampText(text, limit) {
  text = String(text === null || text === undefined ? '' : text); limit = limit || ABOUT_CLAMP;
  if (text.length <= limit + 80) return { short: text, more: '' }; // a tail shorter than a line is not worth a button
  var half = Math.floor(limit / 2), i = text.slice(half, limit).lastIndexOf('. '), cut = i >= 0 ? half + i + 1 : -1;
  if (cut < 0) { var sp = text.lastIndexOf(' ', limit); cut = sp > half ? sp : limit; }
  return { short: text.slice(0, cut).replace(/\s+$/, ''), more: text.slice(cut).replace(/^\s+/, '') };
}
/* The About fact grid (pure): [{k, v (HTML), title}] in the stockanalysis order — Industry, Sector, Headquarters,
   Employees (the 10-K sentence in the title), Exchange, Ticker, Fiscal year end, Filer category, Incorporated,
   First SEC filing (its form when profile.py recorded one), Website, EDGAR. profile.about first, fundamentals.profile
   and the engine run as fallbacks; a fact without a value is left out. */
function aboutFacts(record) {
  var p = obj(record.profile), about = obj(p.about), fp = obj(obj(record.fundamentals).profile), n = obj(record.numbers), s = obj(record.score), row = obj(record.row);
  var facts = [], push = function (k, v, title) { if (v !== null && v !== undefined && v !== '') facts.push({ k: k, v: v, title: title || '' }); };
  var industry = about.industry || fp.sic_description, sector = about.sector || s.sector || record.sector || row.sector, sic = about.sic || fp.sic;
  push('Industry', industry ? esc(industry) + (sic ? ' <span class="sub">SIC ' + esc(sic) + '</span>' : '') : null);
  push('Sector', sector ? esc(sector) : null);
  var addr = obj(about.address), hq = about.headquarters || joinNonEmpty([addr.city, addr.state], ', ');
  push('Headquarters', hq ? esc(hq) : null, joinNonEmpty([addr.street, addr.city, addr.state, addr.zip, addr.country], ', '));
  var emp = about.employees && typeof about.employees === 'object' ? obj(about.employees) : (num(about.employees) !== null ? { count: about.employees } : null);
  if (emp && (num(emp.count) !== null || emp.count)) push('Employees', (num(emp.count) !== null ? fmtCnt(emp.count) : esc(emp.count)) + (emp.as_of ? ' <span class="sub">as of ' + esc(emp.as_of) + '</span>' : '') + (emp.form || emp.url ? ' <span class="sub">' + (safeUrl(emp.url) ? extLink(emp.url, esc(emp.form || 'filing')) : esc(emp.form || '')) + '</span>' : ''),
    emp.evidence ? String(emp.evidence) + (emp.basis ? ' (' + emp.basis + ')' : '') : '');
  push('Exchange', about.exchange || first(about.exchanges) || first(fp.exchanges) ? esc(about.exchange || first(about.exchanges) || first(fp.exchanges)) : null);
  var ticker = s.ticker || record.ticker || row.ticker;
  push('Ticker', ticker ? '<span class="mono">' + esc(ticker) + '</span>' : null);
  var fye = String(about.fiscal_year_end_mmdd || fp.fiscal_year_end_mmdd || '');
  push('Fiscal year end', fye.length === 4 ? esc(fye.slice(0, 2)) + '/' + esc(fye.slice(2)) : null);
  push('Filer category', about.filer_category || fp.filer_category ? esc(about.filer_category || fp.filer_category) : null);
  push('Incorporated', about.state_of_incorporation || fp.state_of_incorporation ? esc(about.state_of_incorporation || fp.state_of_incorporation) : null);
  // Only a registration or listing form dates the IPO; anything else (a 13G, a
  // Form 4) is just where EDGAR's record starts for a company public before 1996.
  // EDGAR filing became mandatory for all registrants by May 1996, so a first
  // record before 1997 is where the archive starts, not a listing (Kroger's is a
  // 1994 debt prospectus); after that, only a registration form dates the IPO.
  var regForm = /^(S-1|S-1\/A|F-1|F-1\/A|S-11|10-12B|10-12G|8-A12B|8-A12G|424B4|20-F|40-F)$/i.test(String(about.first_sec_filing_form || ''))
    && String(about.first_sec_filing || '') >= '1997-01-01';
  push(regForm ? 'First SEC filing' : 'First EDGAR record', about.first_sec_filing ? esc(about.first_sec_filing) + ' <span class="sub">' + esc(about.first_sec_filing_form || 'filing') + '</span>' : null,
    regForm ? 'Earliest registration, listing or periodic form on EDGAR (' + String(about.first_sec_filing_form) + ') — the IPO-date proxy'
            : 'Earliest filing on EDGAR; the company was public before EDGAR\'s records start (1993–96), so this is not an IPO date');
  push('Website', safeUrl(about.website) ? extLink(about.website, esc(String(about.website).replace(/^https?:\/\//i, '').replace(/\/$/, ''))) : null);
  var cik = about.cik || n.cik;
  push('EDGAR', safeUrl(about.edgar_url || fp.edgar_url) ? extLink(about.edgar_url || fp.edgar_url, 'company filings') + (cik ? ' <span class="sub">CIK ' + esc(cik) + '</span>' : '') : null);
  return facts;
}
function renderAbout(record) {
  var p = obj(record.profile), about = obj(p.about), facts = aboutFacts(record);
  var factsH = facts.map(function (f) { return '<div class="fact"' + (f.title ? ' title="' + esc(f.title) + '"' : '') + '><span class="k">' + f.k + '</span><span>' + f.v + '</span></div>'; }).join('');
  var desc = '';
  if (about.description) {
    var d = typeof about.description === 'object' ? obj(about.description) : { text: about.description }, c = clampText(d.text);
    var srcLabel = d.source ? esc(d.source) : 'From the ' + esc(d.form || '10-K') + ', Item 1 Business';
    var src = '<span class="sub">' + srcLabel + (d.filed ? ' · filed ' + esc(d.filed) : '') + (d.url || d.accession ? ' · ' + (safeUrl(d.url) ? extLink(d.url, esc(d.accession || 'open the filing')) : esc(d.accession || '')) : '') + '</span>';
    desc = '<p class="dimp">' + esc(c.short) + (c.more ? '<span class="ell">…</span><span class="more" hidden> ' + esc(c.more) + '</span> <button type="button" class="readmore" aria-expanded="false">Read more</button>' : '') + '</p>' + src;
  } else if (about.description_short) desc = '<p class="dimp">' + esc(about.description_short) + '</p><span class="sub">Nasdaq company profile</span>';
  // The 10-K description is authoritative; Nasdaq's short profile is shown only
  // when there is no 10-K text (review finding: for some names it describes a
  // different entity — Estée Lauder's is its charitable foundation).
  var missing = profilePulled(p) ? '' : '<p class="note"><b>Profile not pulled yet</b> — profile.py has not run for this name; the facts shown come from fundamentals.json and the engine run.</p>';
  if (!facts.length && !desc) return section('About', '<div class="card empty">' + (missing || '<p class="note">No profile facts on record.</p>') + '</div>');
  return section('About', '<div class="card about">' + desc + (facts.length ? '<div class="facts">' + factsH + '</div>' : '') + missing + (p.as_of ? '<p class="note">Profile updated ' + esc(p.as_of) + '.</p>' : '') + '</div>');
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
  if (num(a.capex) !== null) c.push('PP&amp;E capex ' + fmtBig(a.capex) + (num(a.capex_pct_rev) !== null ? ' (' + fmtPct(a.capex_pct_rev) + ' of revenue)' : ''));
  var aInt = intangCapex(a);
  if (aInt !== null) c.push('purchases of intangibles ' + fmtBig(aInt));
  if (num(a.sbc) !== null) c.push('stock-based compensation ' + fmtBig(a.sbc) + (num(a.sbc_pct_ocf) !== null ? ' (' + fmtPct(a.sbc_pct_ocf) + ' of operating cash flow)' : ''));
  if (c.length) out.push(c.join('; ').replace(/^./, function (x) { return x.toUpperCase(); }) + '.');
  if (num(a.oe_conservative) !== null) out.push("Owner's earnings (operating cash flow − " + (aInt !== null ? 'PP&amp;E and intangible capex' : 'capex') + " − stock-based compensation) were " + fmtBig(a.oe_conservative) + (num(a.oe_margin) !== null ? ', a ' + fmtPct(a.oe_margin) + ' margin' : '') + (num(a.oe_per_share) !== null ? ', ' + fmtMoney(a.oe_per_share) + ' per diluted share' : '') + (num(a.oe_per_share_growth) !== null && prev ? ' (' + fmtPct(a.oe_per_share_growth, 1, true) + ' on fiscal ' + esc(prev.fy) + ')' : '') + '.');
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
  var sp = splitInfo(record);
  return section('Financial performance', '<div class="card"><p class="dimp">' + text + '</p><p class="note">Generated from the filed figures in fundamentals.json (EDGAR companyfacts) — see the Financials tab for the statements.'
    + (sp ? ' Per-share figures are as filed: filings before the ' + esc(sp.split) + ' split since scoring are on the pre-split basis.' : '') + '</p></div>');
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
  return section(title || 'Street summary', '<div class="card empty"><p class="note">' + (streetPulled(p) ? 'No analyst data on record for this name.' : 'Street consensus appears once profile.py has pulled the Nasdaq analyst data for this name.') + ' The Street\'s targets are shown only beside our hurdle prices and never enter the valuation.</p></div>');
}
/* The one paragraph both the summary card and the Street sub-tab open with. */
/* opts.noTargetPct: the summary card prints the mean target's move in its own badge, so the paragraph leaves it out (the
   same figure is never shown twice at two precisions); elsewhere the move is printed once, one decimal. Nasdaq's analyst
   count (the consensus summary) and its buy / hold / sell split (the ratings table) come from two different tables and
   need not agree (APP: 16 analysts, 20 ratings) — the paragraph names both when they differ. */
function streetParagraph(record, st, opts) {
  opts = obj(opts);
  var v = liveView(record), c = streetCounts(st), px = v.price, tm = num(st.target_mean), lo = num(st.target_low), hi = num(st.target_high), t = esc(obj(record.score).ticker || record.ticker || obj(record.row).ticker);
  var parts = [], split = c.total && c.analysts !== null && c.analysts !== c.total;
  parts.push((c.analysts !== null ? 'Nasdaq\'s consensus for ' + t + ' is based on ' + c.analysts + ' analyst' + (c.analysts === 1 ? '' : 's') : 'Nasdaq lists analyst coverage for ' + t) + (st.consensus ? '; the consensus rating is <b>' + esc(st.consensus) + '</b>' : '') + '.'
    + (split ? ' Its rating breakdown lists ' + c.total + ' rating' + (c.total === 1 ? '' : 's') + ' (' + (c.buy || 0) + ' buy · ' + (c.hold || 0) + ' hold · ' + (c.sell || 0) + ' sell) — a separate Nasdaq table, so the two counts differ.' : ''));
  if (tm !== null) parts.push('The mean 12-month price target is <b class="mono">' + fmtMoney(tm) + '</b>' + (px && !opts.noTargetPct ? ', <b class="' + signCls(tm - px) + '">' + fmtPts((tm / px - 1) * 100, 1) + '</b> vs ' + (v.is_live ? 'the last close ' : 'the price used ') + fmtMoney(px) : '') + (lo !== null || hi !== null ? ' (range ' + fmtMoney(lo) + ' – ' + fmtMoney(hi) + ')' : '') + '.');
  return parts.join(' ');
}
function bhsBar(c) {
  if (!c.total) return '';
  var w = function (x) { return ((x || 0) / c.total * 100).toFixed(1) + '%'; };
  return '<div class="bhs" role="img" aria-label="' + esc('Rating breakdown: ' + (c.buy || 0) + ' buy, ' + (c.hold || 0) + ' hold, ' + (c.sell || 0) + ' sell') + '"><i class="buy" style="width:' + w(c.buy) + '"></i><i class="hold" style="width:' + w(c.hold) + '"></i><i class="sell" style="width:' + w(c.sell) + '"></i></div>'
    + '<div class="bhsl"><span class="bhst">Rating breakdown · ' + c.total + ' rating' + (c.total === 1 ? '' : 's') + '</span><span><i class="buy"></i>Buy ' + esc(c.buy !== null ? c.buy : '—') + '</span><span><i class="hold"></i>Hold ' + esc(c.hold !== null ? c.hold : '—') + '</span><span><i class="sell"></i>Sell ' + esc(c.sell !== null ? c.sell : '—') + '</span></div>';
}
function streetSourceNote(st) {
  return '<b>The Street\'s view, not ours.</b> Source: ' + esc(st.source || 'Nasdaq analyst endpoints') + (st.as_of ? ', pulled ' + esc(st.as_of) : '') + '. Third-party data shown for context beside our hurdle prices; nothing here enters the owner\'s-earnings valuation.';
}
/* The compact Street card's model (pure): the counts, the mean / low / high targets with their % vs the price the page
   uses (the last close on a live page), the monthly rating history oldest first (for the small chart), our hurdle
   prices beside them. Null without profile.street. */
function streetCardModel(record) {
  var st = streetOf(record); if (!st) return null;
  var v = liveView(record), c = streetCounts(st), px = num(v.price), tm = num(st.target_mean), lo = num(st.target_low), hi = num(st.target_high);
  var pct = function (x) { return x !== null && px !== null && px > 0 ? (x / px - 1) * 100 : null; };
  var hist = arr(st.history).filter(function (r) { return r && typeof r === 'object'; }).map(function (r) { var cc = streetCounts(r); return { date: String(r.date || ''), buy: cc.buy, hold: cc.hold, sell: cc.sell, total: cc.total, mean_target: num(r.mean_target) }; })
    .filter(function (r) { return r.total > 0 || r.mean_target !== null; }).sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
  return { ticker: String(obj(record.score).ticker || record.ticker || obj(record.row).ticker || ''), analysts: c.analysts, consensus: st.consensus || null, counts: c,
    price: px, price_word: v.is_live ? 'last close' : 'price used', price_date: v.price_date || null,
    target_mean: tm, target_low: lo, target_high: hi, pct_mean: pct(tm), pct_low: pct(lo), pct_high: pct(hi),
    history: hist, hurdles: hurdlePrices(record), as_of: st.as_of || null, source: st.source || null };
}
function renderStreet(record) {
  var st = streetOf(record), M = streetCardModel(record);
  if (!st || !M) return streetEmpty(record, 'Street summary');
  var hp = M.hurdles, c = M.counts;
  var ours = hp[15] !== null || hp[20] !== null || hp[25] !== null ? ' Our hurdle prices: ' + fmtMoney(hp[15]) + ' for 15% (Tier B), ' + fmtMoney(hp[20]) + ' for 20% (Tier A), ' + fmtMoney(hp[25]) + ' for 25% (Tier S).' : '';
  var target = M.target_mean !== null ? '<div class="stgt"><span class="k">Mean 12-month target</span><span class="v mono">' + fmtMoney(M.target_mean) + (M.pct_mean !== null ? ' <small class="badge ' + signCls(M.pct_mean) + '">' + fmtPts(M.pct_mean, 1) + ' vs ' + M.price_word + ' ' + fmtMoney(M.price) + '</small>' : '') + '</span>'
    + (M.target_low !== null || M.target_high !== null ? '<span class="tsub">Range ' + fmtMoney(M.target_low) + ' – ' + fmtMoney(M.target_high) + (M.pct_low !== null && M.pct_high !== null ? ' (' + fmtPts(M.pct_low, Math.abs(M.pct_low) < 1 ? 1 : 0) + ' to ' + fmtPts(M.pct_high, Math.abs(M.pct_high) < 1 ? 1 : 0) + ')' : '') + '</span>' : '') + '</div>' : '';
  var chart = M.history.length >= 2 ? '<h3 class="sub3">Ratings by month</h3>' + chartDiv('street-sum', 'small') : '';
  return section('Street summary', '<div class="card street"><span class="k streetlbl">Street view — Nasdaq analyst data, not used by the valuation</span><p class="dimp">' + streetParagraph(record, st, { noTargetPct: M.target_mean !== null && M.pct_mean !== null }) + '</p>' + target + bhsBar(c) + chart
    + '<p class="note">' + ours.replace(/^ /, '') + '</p><p class="note"><a class="seefc" href="#' + esc(M.ticker) + '.forecast.street">See the full forecast →</a> · ' + streetSourceNote(st) + '</p></div>');
}
/* Filings card filter: All · 10-K / 10-Q (periodic reports, amendments included) · 8-K (current reports; 6-K for a
   foreign filer) · Other (proxy, registration, …). filingKind(form) names a filing's chip; filterFilings keeps the rows
   for one chip ('all' keeps every row). Pure, node-tested; the chips toggle rows in the DOM without a re-render. */
var FILING_KINDS = [['all', 'All'], ['periodic', '10-K / 10-Q'], ['8k', '8-K'], ['other', 'Other']];
function filingKind(form) {
  var f = String(form || '').toUpperCase().trim().replace(/\/A$/, '');
  if (/^(10-K|10-Q|10-KT|10-QT|20-F|40-F|10-K405|10-KSB|10-QSB)$/.test(f)) return 'periodic';
  if (f === '8-K' || f === '6-K') return '8k';
  return 'other';
}
function filterFilings(filings, kind) {
  var list = arr(filings).filter(function (f) { return f && typeof f === 'object'; });
  return kind && kind !== 'all' ? list.filter(function (f) { return filingKind(f.form) === kind; }) : list;
}
function renderFilings(record) {
  var p = obj(record.profile), fp = obj(obj(record.fundamentals).profile);
  var filings = arr(p.filings).filter(function (f) { return f && typeof f === 'object'; });
  if (!filings.length) {
    var lf = obj(fp.latest_filings), keys = Object.keys(lf);
    if (!keys.length) return section('Filings', '<div class="card empty"><p class="note">' + (profilePulled(p) ? 'No filings on record.' : 'The EDGAR filing feed appears once profile.py has run for this name.') + '</p></div>');
    filings = keys.map(function (form) { var d = obj(lf[form]); return { form: form, filed: d.filed, period: d.period, url: d.url, description: 'latest ' + form }; });
  }
  filings = filings.slice(0, 20);
  var rows = filings.map(function (f) {
    var items = arr(f.items).map(function (x) { return esc(x); }).join(', ');
    return '<tr data-kind="' + filingKind(f.form) + '"><td class="mono">' + esc(f.filed) + '</td><td><b>' + esc(f.form) + '</b>' + (items ? ' <span class="sub">' + items + '</span>' : '') + '</td><td>' + esc(f.description || '') + (f.period ? ' <span class="sub">period ' + esc(f.period) + '</span>' : '') + '</td><td>' + (safeUrl(f.url) ? extLink(f.url, 'open') : '') + '</td></tr>';
  }).join('');
  var chips = FILING_KINDS.map(function (k) { var n = filterFilings(filings, k[0]).length; return '<button type="button" data-fk="' + k[0] + '" class="' + (k[0] === 'all' ? 'on' : '') + '" aria-pressed="' + (k[0] === 'all') + '"' + (n ? '' : ' disabled') + (k[0] === '8k' ? ' title="Current reports (6-K for a foreign filer)"' : k[0] === 'periodic' ? ' title="Annual and quarterly reports, amendments included"' : '') + '>' + k[1] + ' <span class="mono">' + n + '</span></button>'; }).join('');
  return section('Filings', '<div class="card fcard" data-fk="all"><div class="fchips" role="group" aria-label="Filter by form">' + chips + '</div><div class="twrap"><table class="mini filings"><thead><tr><th>Filed</th><th>Form</th><th>What</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div><p class="note">From EDGAR submissions' + (p.as_of ? ', updated ' + esc(p.as_of) : '') + (fp.eight_k_count_12m !== undefined && fp.eight_k_count_12m !== null ? ' · ' + esc(fp.eight_k_count_12m) + ' 8-Ks in the last 12 months' : '') + '.</p></div>');
}

/* Engine 5.6 (acquired IPR&D, Andrew 2026-10-19): one disclosure line under the base OE card when the scored run
   deducted a one-time acquired-IPR&D charge per share from every intrinsic value and added it to the price each
   IRR is solved at (Codex review r3 of PR #47: added, not deducted — a higher price, a lower IRR). The IVs, IRRs and
   hurdle prices on the page are already the adjusted ones; the line says where the gap to the paths comes from.
   [Codex review r16 of PR #47] Only the adjustment of the run the displayed score came from is described as applied:
   score.json's own block, and never when the score on file is an earlier run's (live_withheld reason
   score_not_from_this_run or iprd_unresolved). The engine record's block alone (the score carries none — make_score
   copies it whenever the run has one, so that score is another run's) or beside a foreign score is named as the
   latest run's adjustment pending its score, never as already in the figures. The charge is per traded unit: per ADS
   when the run's applied ads_ratio (numbers.iprd_adjustment.ads_ratio, else numbers.ads_ratio) is not 1, as
   key_numbers.md prints it. '' for every other record. */
function iprdUnit(record) {
  var nb = obj(obj(record.numbers).iprd_adjustment), r = num(nb.ads_ratio);
  if (r === null) { var a = obj(record.numbers).ads_ratio; r = num(a && typeof a === 'object' ? a.ratio : a); }
  return r !== null && r > 0 && Math.abs(r - 1) >= 1e-12 ? '/ADS' : '/sh';
}
function iprdWhere(b) {
  return arr(b.periods).filter(function (p) { return p && num(p.deducted) > 0; }).map(function (p) {
    return (p.window === 'fy' ? 'FY' + esc(String(p.period).slice(0, 4)) : 'YTD ' + esc(p.period)) + ', ' + (p.amount_basis === 'cash_outflow' ? 'cash' : 'expense') + ' basis';
  }).join('; ');
}
function iprdNote(record) {
  var w = liveWithheld(record), foreign = !!w && (w.reason === 'score_not_from_this_run' || w.reason === 'iprd_unresolved');
  var b = obj(obj(record.score).iprd_adjustment), c, where;
  if (!foreign && Object.keys(b).length) {
    if (b.treatment === 'amortized_in_base') return 'Acquired IPR&amp;D: amortized in the base OE (iprd_amortized base override) — no one-time deduction.';
    c = num(b.charge_per_share);
    if (b.treatment !== 'one_time_value_deduction' || c === null || c <= 0) return '';
    where = iprdWhere(b);
    return 'Acquired IPR&amp;D: −' + fmtMoney(c) + iprdUnit(record) + ' one-time' + (where ? ' (' + where + ')' : '') + ' — deducted from every intrinsic value and added to the price each IRR is solved at; the base OE is unchanged.';
  }
  b = obj(obj(record.numbers).iprd_adjustment); c = num(b.charge_per_share);
  if (b.treatment !== 'one_time_value_deduction' || c === null || c <= 0) return '';
  where = iprdWhere(b);
  return 'Acquired IPR&amp;D: the latest engine run deducts −' + fmtMoney(c) + iprdUnit(record) + ' one-time' + (where ? ' (' + where + ')' : '') + ', pending its score — the scored figures shown do not include it.';
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
  var up = v.upside, hp = hurdlePrices(record), px = v.price, iv15 = num(s.iv_at_15 !== undefined ? s.iv_at_15 : row.iv15), wh = liveWithheld(record);
  var tiles = [
    tile(v.is_live ? 'Last close' : 'Price', fmtMoney(px), '', v.is_live ? esc(v.price_date) + ' · scored at ' + fmtMoney(v.scored_price) : (wh ? 'scored ' + esc(v.price_date) + ' · live pending' : ''), wh && !v.is_live ? pendingText(wh) : ''),
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
    + '<p class="note">Basis: ' + baseSrc + '. Latest FY ' + fmtMoney(n.base_oe_latest_per_share) + '/sh · 3-yr median ' + fmtMoney(n.base_oe_normalized_per_share) + '/sh · growth blend ' + fmtPct(n.g_blend) + ' → start ' + fmtPct(n.g_base) + ' · terminal ' + fmtPct(n.g_terminal) + '.</p>'
    + (iprdNote(record) ? '<p class="note">' + iprdNote(record) + '</p>' : '') + '</div>';
  // scenarios
  // a scenario IRR the solver clamped at its floor (irr_at_floor / irr_live_at_floor) is a bound, not a solved return:
  // it is marked like the Forecast tab's sensitivity table, never presented as a bare figure
  var scn = Object.keys(obj(n.scenarios)).length ? obj(n.scenarios) : obj(s.scenarios), rows = '', sens = sensitivity(record), anyFloor = false;
  var liveFloorTitle = 'the live IRR solver stopped at its floor — the last close did not improve this case; the figure is a bound (at most about the terminal growth rate), not a solved return';
  var scoredFloorTitle = 'the scored IRR solver stopped at its floor: this figure is a bound (at most about the terminal growth rate), not a solved return';
  LABELS.forEach(function (l) {
    var k = l[0], r = obj(scn[k]), scoredIrr = num(r.irr), fr = obj(sens[k]);
    var rIrr = v.is_live ? obj(v.scenarios[k]).irr : scoredIrr;
    if (rIrr === null || rIrr === undefined) rIrr = scoredIrr;
    var shownFloor = v.is_live ? !!fr.irr_live_at_floor : !!fr.irr_at_floor, scoredFloor = !!fr.irr_at_floor;
    if (shownFloor || (v.is_live && scoredFloor)) anyFloor = true;
    var w = rIrr !== null ? Math.max(0, Math.min(100, rIrr * 100 / scale * 100)) : 0;
    var prob = num(r.prob) !== null ? Math.round(num(r.prob) * 100) + '%' : '—';
    var scoredH = v.is_live && scoredIrr !== null ? '<span>Scored IRR <b>' + fmtPct(scoredIrr) + '</b>' + (scoredFloor ? ' ' + floorSup(scoredFloorTitle) : '') + '</span>' : '';
    rows += '<div class="scn"><div class="scnh"><span class="scnn"><i style="background:' + SCN_COLORS[k] + '"></i>' + l[1] + '<span class="prob">' + prob + '</span></span><span class="mono scni' + (shownFloor ? ' atfloor' : '') + '">' + fmtPct(rIrr) + (shownFloor ? ' ' + floorSup(v.is_live ? liveFloorTitle : scoredFloorTitle) : '') + '</span></div>'
      + '<div class="scnbar"><div class="scnfill" style="width:' + w.toFixed(1) + '%;background:' + acc + '"></div><div class="scntick" style="left:' + hurdleLeft.toFixed(1) + '%"></div></div>'
      + '<div class="scnsub"><span>Growth start <b>' + fmtPct(r.g_start) + '</b></span><span>OE multiple <b>' + fmtX(r.oe_mult, 2) + '</b></span><span>IV @15% <b>' + fmtMoney(r.iv_at_15) + '</b></span>' + scoredH + '</div></div>';
  });
  if (v.irr_at_floor) anyFloor = true;
  var sc = '<div class="card scncard">' + rows + '<div class="scnfoot"><span>Probability-weighted' + (v.is_live ? ' · at last close' : '') + '</span><span class="mono' + (v.irr_at_floor ? ' atfloor' : '') + '">IV ' + fmtMoney(iv15) + ' · IRR ' + fmtPct(irr) + (v.irr_at_floor ? ' ' + floorSup(v.is_live ? liveFloorTitle : scoredFloorTitle) : '') + (v.is_live ? ' <span class="scored">scored ' + fmtPct(v.scored_irr) + '</span>' : '') + '</span></div></div>';
  var floorNote = anyFloor ? ' <b>At floor</b> marks an IRR the solver clamped at its floor: a bound (read it as "at most about the terminal growth rate"), not a solved return — a floored live figure above the scored one is not an improvement at the last close.' : '';
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
  return splitBrief(splitInfo(record)) + gauge + p2 + renderAbout(record) + renderPerformance(record) + renderStreet(record) + renderFilings(record)
    + section('Key numbers', kn) + (ov ? section('Overrides', ov, 'Filing gaps filled by a judgment override — an override never replaces a filed value.') : '')
    + section('Scenarios', sc, 'IRR ' + atPx + ' for each case, against the 15% hurdle.' + (v.is_live ? " Live figures reprice the scored cash-flow paths at the last close; the scored IRR is the agent's verdict-date figure." : '') + floorNote)
    + section('', moatH) + (flags.length ? section('Fragility flags <span class="fcount mono">' + flags.length + '</span>', fl) : '');
}

/* ---- Financials */
function derivedSup() { return '<sup title="derived: year-to-date minus prior year-to-date">†</sup>'; }
/* stm = the statements-viewer state (see renderStatements); the viewer card sits above the summary cards. */
function renderFinancials(record, stm) {
  var fund = record.fundamentals && typeof record.fundamentals === 'object' ? record.fundamentals : null, hist = arr(record.history), parts = [];
  var stmH = renderStatements(record, stm);
  if (fund) {
    var ann = arr(fund.annual), q = arr(fund.quarterly), ttm = obj(fund.ttm), cur = fund.currency || 'USD';
    var unitNote = 'Figures as filed with the SEC, in ' + esc(cur) + '.' + (cur !== 'USD' ? ' <b>Not USD</b> — the engine converts for the valuation; this tab shows the filings as filed.' : '');
    var warn = arr(fund.warnings).map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('');
    if (warn) unitNote += '<ul class="warnlist">' + warn + '</ul>';
    if (q.length) {
      var qlabels = q.map(function (r) { return r.label || r.period_end; });
      var qhead = qlabels.map(function (l) { return '<th class="num">' + esc(l) + '</th>'; }).join('');
      // a line with no value in any shown period is dropped (the full statements viewer's rule) — a row of dashes says nothing
      var blank = function (rows, key) { return rows.every(function (r) { return r[key] === null || r[key] === undefined; }); };
      var qrow = function (name, key, f) {
        f = f || fmtBig;
        if (blank(q, key)) return '';
        return '<tr><th>' + name + '</th>' + q.map(function (r) { return '<td>' + f(r[key]) + (r[key + '_derived'] ? derivedSup() : '') + '</td>'; }).join('') + '</tr>';
      };
      var qpct = function (name, key) { if (blank(q, key)) return ''; return '<tr class="sub"><th>' + name + '</th>' + q.map(function (r) { var c = signCls(r[key]); return '<td' + (c ? ' class="' + c + '"' : '') + '>' + fmtPct(r[key], 1, true) + '</td>'; }).join('') + '</tr>'; };
      var qt = '<div class="twrap"><table class="fin"><thead><tr><th>Quarter</th>' + qhead + '</tr><tr class="sub"><th>Period end</th>' + q.map(function (r) { return '<td>' + esc(r.period_end) + '</td>'; }).join('') + '</tr></thead><tbody>'
        + qrow('Revenue', 'revenue') + qpct('Revenue growth (YoY)', 'revenue_yoy') + qrow('Gross margin', 'gross_margin', fmtPct) + qrow('Operating income', 'operating_income') + qrow('Net income', 'net_income') + qpct('Net income growth (YoY)', 'net_income_yoy') + qrow('EPS (diluted)', 'eps_diluted', fmtMoney)
        + qrow('Operating cash flow', 'ocf') + qrow('Capex (PP&amp;E)', 'capex') + qrow('Stock-based comp', 'sbc') + qrow("Owner's earnings (cons.)", 'oe_conservative') + qpct("Owner's earnings growth (YoY)", 'oe_conservative_yoy') + qrow('Diluted shares', 'shares_diluted', fmtCnt)
        + qrow('Dividends paid', 'dividends_paid', fmtBig, true) + qrow('Buybacks', 'buybacks', fmtBig, true) + qrow('DPS declared', 'dps_declared', fmtDps, true) + qrow('DPS paid', 'dps_paid', fmtDps, true) + '</tbody></table></div>';
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
      var ablank = function (key) { return ann.every(function (r) { return r[key] === null || r[key] === undefined; }); }; // same rule as the quarterly table: an all-empty line is dropped
      var arow = function (name, key, f, cls) { f = f || fmtBig; if (ablank(key)) return ''; return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th>' + name + '</th>' + ann.map(function (r) { return '<td>' + f(r[key]) + '</td>'; }).join('') + '</tr>'; };
      var apct = function (name, key) { if (ablank(key)) return ''; return '<tr class="sub"><th>' + name + '</th>' + ann.map(function (r) { var c = signCls(r[key]); return '<td' + (c ? ' class="' + c + '"' : '') + '>' + fmtPct(r[key], 1, true) + '</td>'; }).join('') + '</tr>'; };
      var pend = '<tr class="sub"><th>Period end</th>' + ann.map(function (r) { return '<td>' + esc(r.period_end) + '</td>'; }).join('') + '</tr>';
      var inc = '<div class="twrap"><table class="fin"><thead><tr><th>Income statement</th>' + head + '</tr>' + pend + '</thead><tbody>'
        + arow('Revenue', 'revenue', null, 'strong') + apct('Revenue growth', 'revenue_growth') + arow('Cost of revenue', 'cogs') + arow('Gross profit', 'gross_profit') + apct('Gross margin', 'gross_margin') + arow('R&amp;D', 'rnd') + arow('SG&amp;A', 'sga') + arow('Operating income', 'operating_income', null, 'strong') + apct('Operating margin', 'operating_margin') + arow('Interest expense', 'interest_expense') + arow('Pretax income', 'pretax_income') + arow('Income tax', 'tax') + arow('Net income', 'net_income', null, 'strong') + apct('Net margin', 'net_margin') + apct('Net income growth', 'net_income_growth') + arow('EPS (diluted)', 'eps_diluted', fmtMoney) + apct('EPS growth', 'eps_diluted_growth') + arow('Diluted shares', 'shares_diluted', fmtCnt) + apct('Share count change', 'shares_diluted_growth') + '</tbody></table></div>';
      var cf = '<div class="twrap"><table class="fin"><thead><tr><th>Cash flow</th>' + head + '</tr></thead><tbody>'
        + arow('Operating cash flow', 'ocf', null, 'strong') + apct('OCF growth', 'ocf_growth') + arow('Capex (PP&amp;E)', 'capex') + apct('Capex % revenue', 'capex_pct_rev') + arow('Depreciation &amp; amortization', 'da') + arow('Stock-based compensation', 'sbc') + apct('SBC % revenue', 'sbc_pct_rev') + apct('SBC % OCF', 'sbc_pct_ocf') + arow('Free cash flow (OCF − PP&amp;E and intangible capex)', 'fcf') + arow("Owner's earnings (FCF − SBC)", 'oe_conservative', null, 'strong') + apct("Owner's earnings margin", 'oe_margin') + apct("Owner's earnings growth", 'oe_conservative_growth') + arow('OE per share', 'oe_per_share', fmtMoney) + apct('OE/share growth', 'oe_per_share_growth') + arow('Dividends paid', 'dividends_paid') + arow('Buybacks', 'buybacks') + arow('Acquisitions', 'acquisitions') + arow('Investing cash flow', 'icf') + arow('Financing cash flow', 'fincf') + '</tbody></table></div>';
      var bs = '<div class="twrap"><table class="fin"><thead><tr><th>Balance sheet</th>' + head + '</tr></thead><tbody>'
        + arow('Cash &amp; equivalents', 'cash') + arow('Short-term investments', 'short_term_investments') + arow('Receivables', 'receivables') + arow('Inventory', 'inventory') + arow('Prepaids', 'prepaids') + apct('Prepaids % assets', 'prepaids_pct_assets') + arow('Current assets', 'assets_current') + arow('PP&amp;E (net)', 'ppe_net') + arow('Goodwill', 'goodwill') + apct('Goodwill % assets', 'goodwill_pct_assets') + arow('Intangibles', 'intangibles') + arow('Total assets', 'assets', null, 'strong') + arow('Current liabilities', 'liab_current') + arow('Deferred revenue', 'deferred_revenue') + arow('Total debt', 'total_debt', null, 'strong') + arow('Net debt (debt − cash)', 'net_debt') + arow('Operating lease liabilities', 'lease_liabilities') + arow('Total liabilities', 'liabilities') + arow("Shareholders' equity", 'equity', null, 'strong') + arow('Book value / share', 'book_value_per_share', fmtMoney) + arow('Current ratio', 'current_ratio', fmtX) + apct('Return on equity', 'roe') + apct('ROIC (proxy)', 'roic_proxy') + arow("Net debt / owner's earnings", 'net_debt_to_oe', fmtX) + '</tbody></table></div>';
      parts.push(section('Revenue &amp; profits', '<div class="card">' + chartDiv('fin-ann') + inc + '</div>', unitNote));
      parts.push(section("Cash flow &amp; owner's earnings", '<div class="card">' + chartDiv('fin-cf') + cf + '</div>', "Owner's earnings = free cash flow − stock-based compensation (SBC always treated as a real cost). Free cash flow = operating cash flow − PP&amp;E capex (the row above) − purchases of intangibles, the engine's capex definition — so it can be below OCF minus the PP&amp;E row."));
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
  // a split since scoring: this tab is the filings as filed — only the run's figures elsewhere are restated
  var sp = splitInfo(record), spH = !sp ? '' : '<p class="note splitnote"><b>' + esc(sp.split) + ' split since scoring.</b> '
    + (fund ? 'Per-share figures in the filed statements on this tab (EPS, owner\'s earnings and book value per share, share counts) are as filed: periods filed before the split are on the pre-split basis. The engine run\'s figures on the other tabs are restated to today\'s share units.</p>'
            : 'The engine history\'s share counts are restated to today\'s share units (× ' + esc(fmtFactor(sp.factor)) + ').</p>');
  return spH + stmH + parts.join('');
}

/* ---- Statements viewer (Financials tab): <T>/statements.json served as ./data/<T>.statements.json, loaded on demand
   when the Financials tab opens (never embedded in the attachment). Pure model + renderer; the DOM part (fetch, state,
   events) is in section 6. Columns are newest first; the TTM view puts one TTM column (flows) or a "Current" column
   (balance-sheet instants, the latest quarter end) first, then the fiscal years, like stockanalysis. */
var STM_TABS = [['income', 'Income'], ['balance', 'Balance sheet'], ['cashflow', 'Cash flow'], ['metrics', 'Metrics']];
var STM_PERIODS = [['annual', 'Annual'], ['quarterly', 'Quarterly'], ['ttm', 'TTM']];
var STM_KEYS = STM_TABS.map(function (t) { return t[0]; }), STM_PKEYS = STM_PERIODS.map(function (t) { return t[0]; });
var STM_NAMES = { income: 'income statement', balance: 'balance sheet', cashflow: 'cash-flow statement', metrics: 'metrics' };
function stmNorm(stm) {
  var s = obj(stm);
  return { status: s.status || 'idle', data: s.data && typeof s.data === 'object' && !Array.isArray(s.data) ? s.data : null, error: s.error || null,
    statement: STM_KEYS.indexOf(s.statement) >= 0 ? s.statement : 'income', period: STM_PKEYS.indexOf(s.period) >= 0 ? s.period : 'annual',
    growth: s.growth === true, line: typeof s.line === 'string' && s.line ? s.line : null, site: typeof s.site === 'string' ? s.site : '' };
}
function monthYear(end) { var p = isoParts(end); return p ? MON[p.m] + " '" + String(p.y).slice(2) : String(end || ''); } // "2025-12-31" → "Dec '25"
/* Money and shares in millions: no decimals from 100 M up, two below; per-share two decimals; ratios two; percentages one.
   Negatives carry a leading minus; an empty cell is "–". */
function stmFmt(unit, v) {
  v = num(v); if (v === null) return '–';
  var a = Math.abs(v), t;
  if (unit === 'money' || unit === 'shares') { var m = a / 1e6; t = Math.round(m * 100) / 100 >= 100 ? fixed(m, 0) : fixed(m, 2); } // the 100 M switch is decided on the rounded value (99.995 M → "100", not "100.00")
  else if (unit === 'pct') t = fixed(a * 100, 1) + '%';
  else t = fixed(a, 2); // per_share, ratio
  return minus(v, t) + t; // sign from the rounded text: -4,000 in millions is "0.00", not "-0.00"
}
/* The column list for a statement × period, newest first: [{src: 'annual'|'quarterly'|'ttm', i, label, sub, end, filed}]. */
function stmColumns(data, statement, period) {
  var P = obj(obj(data).periods), ann = arr(P.annual).filter(function (p) { return p && typeof p === 'object'; }), q = arr(P.quarterly).filter(function (p) { return p && typeof p === 'object'; });
  var ttm = P.ttm && typeof P.ttm === 'object' && !Array.isArray(P.ttm) ? P.ttm : null, cur = obj(P.current), isBal = statement === 'balance', cols = [];
  if (period === 'quarterly') {
    q.forEach(function (p, i) { cols.push({ src: 'quarterly', i: i, label: String(p.label || p.end || ''), sub: monthYear(p.end), end: p.end || null, filed: p.filed || null }); });
    return cols.reverse();
  }
  if (period === 'ttm') {
    var curEnd = cur.end || (q.length ? q[q.length - 1].end : null) || (ttm ? ttm.end : null);
    if (isBal && curEnd) cols.push({ src: 'ttm', i: -1, label: 'Current', sub: monthYear(curEnd), end: curEnd, filed: null });
    else if (!isBal && ttm && ttm.end) cols.push({ src: 'ttm', i: -1, label: 'TTM', sub: 'to ' + monthYear(ttm.end), end: ttm.end, filed: null, quarters: arr(ttm.quarters) });
  }
  ann.forEach(function (p, i) { cols.push({ src: 'annual', i: i, label: String(p.label || p.end || ''), sub: monthYear(p.end), end: p.end || null, filed: p.filed || null }); });
  var first = cols.length && cols[0].src === 'ttm' ? [cols.shift()] : [];
  return first.concat(cols.reverse());
}
/* The table model: rows (lines with at least one value in the chosen period) × columns, each cell formatted, with the YoY
   growth, the derived-quarter flag and the cash-flow sign applied (outflow lines, cf_sign −1, are shown as negatives).
   inclRestricted (statements.py restricted_cash_split): the cell counts restricted cash — on the cash line, a cell filed only
   as the combined cash + restricted cash total; on net cash, net cash per share and the ROIC proxy, a period where no figure
   separates the restricted part (incl_restricted_annual / _quarterly per column, incl_restricted_ttm for the TTM / Current
   column). */
function stmTable(data, statement, period, growth) {
  statement = STM_KEYS.indexOf(statement) >= 0 ? statement : 'income'; period = STM_PKEYS.indexOf(period) >= 0 ? period : 'annual';
  var lines = arr(obj(obj(data).statements)[statement]).filter(function (l) { return l && typeof l === 'object'; }), cols = stmColumns(data, statement, period);
  var rows = lines.map(function (L) {
    var sign = statement === 'cashflow' && num(L.cf_sign) === -1 ? -1 : 1, unit = L.unit || 'money', lvl = Math.max(0, Math.min(2, num(L.level) || 0));
    var cells = cols.map(function (c) {
      var v = num(c.src === 'ttm' ? L.ttm : get(L[c.src], c.i)), shown = v === null ? null : (v === 0 ? 0 : v * sign);
      var g = c.src === 'ttm' ? null : num(get(L['growth_' + c.src], c.i)), der = c.src === 'quarterly' && get(L.derived_quarterly, c.i) === true;
      var bb = c.src === 'quarterly' && get(L.basis_break_quarterly, c.i) === true; // statements.py: the fiscal year's four quarters do not sum to its restated FY figure
      var ir = v !== null && (c.src === 'ttm' ? L.incl_restricted_ttm === true : get(L['incl_restricted_' + c.src], c.i) === true); // a mark on an empty cell would mark nothing
      return { raw: v, value: shown, text: stmFmt(unit, shown), derived: der, basisBreak: bb, inclRestricted: ir, growth: g, growthText: g === null ? '–' : fmtPct(g, 1, true), growthCls: signCls(g) };
    });
    return { key: String(L.key || ''), label: String(L.label || L.key || ''), level: lvl, total: L.total === true, unit: unit, sign: sign, cells: cells,
      hasGrowth: cells.some(function (c) { return c.growth !== null; }), anyDerived: cells.some(function (c) { return c.derived; }), anyBasisBreak: cells.some(function (c) { return c.basisBreak; }),
      anyInclRestricted: cells.some(function (c) { return c.inclRestricted; }), empty: cells.every(function (c) { return c.raw === null; }) };
  }).filter(function (r) { return !r.empty; });
  return { statement: statement, period: period, growth: growth === true, cols: cols, rows: rows, lines: lines.length,
    anyDerived: rows.some(function (r) { return r.anyDerived; }), anyBasisBreak: rows.some(function (r) { return r.anyBasisBreak; }), anyInclRestricted: rows.some(function (r) { return r.anyInclRestricted; }),
    ttmMissing: period === 'ttm' && !cols.some(function (c) { return c.src === 'ttm'; }) };
}
/* "7 fiscal years, FY2019 → FY2025" / "26 quarters, Q1 FY2020 → Q2 FY2026": how far the table reaches (a phone shows two
   or three columns of it). The TTM / Current column is not counted. */
function stmSpan(M) {
  var cols = arr(obj(M).cols).filter(function (c) { return c.src !== 'ttm'; }), n = cols.length;
  if (n < 2) return '';
  return n + (cols[0].src === 'quarterly' ? ' quarters' : ' fiscal years') + ', ' + String(cols[n - 1].label) + ' → ' + String(cols[0].label);
}
var BASIS_BREAK_TITLE = 'basis break: this fiscal year\'s four quarters do not add up to its restated fiscal-year figure (the quarters were filed on the earlier basis — a divestiture or restatement); the growth cells on it are blank. See the build notes.';
var RESTRICTED_TITLE = 'includes restricted cash: the filed cash + restricted cash total; net cash deducts the restricted part where the Restricted cash line shows it, otherwise still counts it';
var RESTRICTED_LEGEND = '‡ includes restricted cash; growth is blank where one period deducts it and the other does not. ';
function renderStatementsTable(M, openLine) {
  var head = '<tr><th class="stl0">' + esc(STM_NAMES[M.statement] || M.statement).replace(/^./, function (c) { return c.toUpperCase(); }) + '</th>'
    + M.cols.map(function (c) { return '<th class="num"><span class="pl">' + esc(c.label) + '</span><span class="sub">' + esc(c.sub) + '</span></th>'; }).join('') + '</tr>';
  var body = M.rows.map(function (r) {
    var open = openLine && r.key === openLine;
    var tr = '<tr class="l' + r.level + (r.total ? ' strong' : '') + (open ? ' open' : '') + '" data-line="' + esc(r.key) + '"><th><button type="button" class="stl" data-line="' + esc(r.key) + '" aria-expanded="' + (open ? 'true' : 'false') + '"' + (open ? ' aria-controls="stmspark"' : '') + ' title="Chart this line">' + esc(r.label) + '</button></th>'
      + r.cells.map(function (c) { var cls = joinNonEmpty([c.value !== null && c.value < 0 ? 'negv' : '', c.basisBreak ? 'bbrk' : ''], ' '); return '<td' + (cls ? ' class="' + cls + '"' : '') + (c.basisBreak ? ' title="' + esc(BASIS_BREAK_TITLE) + '"' : '') + '>' + esc(c.text) + (c.derived ? '<sup title="derived quarter: year-to-date minus the prior year-to-date; Q4 = fiscal year minus nine months">†</sup>' : '')
        + (c.inclRestricted ? '<sup class="rcash" title="' + esc(RESTRICTED_TITLE) + '">‡</sup>' : '') + '</td>'; }).join('') + '</tr>';
    if (M.growth && r.hasGrowth) tr += '<tr class="sub growth"><th>YoY growth</th>' + r.cells.map(function (c) { return '<td' + (c.growthCls ? ' class="' + c.growthCls + '"' : '') + '>' + esc(c.growthText) + '</td>'; }).join('') + '</tr>';
    return tr;
  }).join('');
  return '<div class="twrap stmwrap"><table class="fin stm"><thead>' + head + '</thead><tbody>' + body + '</tbody></table></div>';
}
/* The chart spec for one line over the selected periodicity (oldest first; the TTM view charts the fiscal years). */
function stmSparkSpec(data, statement, period, key) {
  var lines = arr(obj(obj(data).statements)[statement]).filter(function (l) { return l && typeof l === 'object'; }), L = null;
  lines.forEach(function (l) { if (!L && String(l.key) === String(key)) L = l; });
  if (!L) return null;
  var cols = stmColumns(data, statement, period === 'ttm' ? 'annual' : period).slice().reverse(), sign = statement === 'cashflow' && num(L.cf_sign) === -1 ? -1 : 1, unit = L.unit || 'money';
  var vals = cols.map(function (c) { var v = num(get(L[c.src], c.i)); return v === null ? null : (v === 0 ? 0 : v * sign); });
  if (!vals.some(function (v) { return v !== null; })) return null;
  var yfmt = { money: 'big', shares: 'cnt', per_share: 'money', pct: 'pct', ratio: 'num' }[unit] || 'big', kind = unit === 'money' || unit === 'shares' ? 'bar' : 'line';
  return { labels: sparkLabels(cols), yfmt: yfmt, height: 200, zero: true, series: [{ name: String(L.label || key), color: unit === 'pct' || unit === 'ratio' ? C_NI : C_REV, kind: kind, values: vals }],
    xlabel: period === 'quarterly' ? 'Fiscal quarter' : 'Fiscal year' };
}
/* The sparkline's x labels: the period labels, or — when any label repeats (a fiscal-year-end change makes statements.py
   label two different quarters "Q1 FY2012": ADM 2011-09-30 and 2012-03-31) — every label with its end month. */
function sparkLabels(cols) {
  var labs = arr(cols).map(function (c) { return String(c.label); }), dup = labs.some(function (l, i) { return labs.indexOf(l) !== i; });
  return dup ? arr(cols).map(function (c) { return String(c.label) + (c.end ? ' · ' + monthYear(c.end) : ''); }) : labs;
}
function renderSparkCard(data, stm) {
  var lines = arr(obj(obj(data).statements)[stm.statement]).filter(function (l) { return l && typeof l === 'object'; }), L = null;
  lines.forEach(function (l) { if (!L && String(l.key) === stm.line) L = l; });
  if (!L) return '';
  var unitWord = { money: 'millions ' + esc(obj(data).currency || 'USD'), shares: 'shares', per_share: 'per share', pct: 'percent', ratio: 'ratio' }[L.unit] || '';
  return '<div class="card spark" id="stmspark" role="region" aria-label="' + esc(L.label) + ' chart"><div class="sparkh"><span><b>' + esc(L.label) + '</b> <span class="note">' + esc(stm.period === 'quarterly' ? 'by fiscal quarter' : 'by fiscal year') + (unitWord ? ' · ' + unitWord : '') + '</span></span><button type="button" class="stm-close" aria-label="Close chart" title="Close">×</button></div>' + chartDiv('stm-spark') + '</div>';
}
function renderStatementsBody(stm, ticker) {
  var d = stm.data, M = stmTable(d, stm.statement, stm.period, stm.growth), cur = d.currency || 'USD', fye = String(d.fiscal_year_end_mmdd || ''), lf = obj(d.latest_filed);
  var isBal = stm.statement === 'balance', ttm = obj(obj(d.periods).ttm), annualOnly = !arr(obj(d.periods).quarterly).length;
  var units = 'Millions ' + esc(cur) + '.' + (fye.length === 4 ? ' Fiscal year ends ' + esc(fye.slice(0, 2)) + '/' + esc(fye.slice(2)) + '.' : '') + ' Per-share figures in ' + esc(cur) + '; shares in millions; newest period first.'
    + (stm.statement === 'cashflow' ? ' Cash outflows (capex, buybacks, dividends, repayments, acquisitions, investment purchases) are shown as negatives.' : '')
    + (stm.statement === 'metrics' && stm.period === 'ttm' ? ' Flow-based metrics are trailing twelve months; balance-based ones (book value, net cash, ratios on balances) are at the latest quarter end.' : '')
    + (stm.period === 'ttm' && !M.ttmMissing ? (isBal ? ' "Current" is the latest quarter end.' : (ttm.end ? ' TTM = the four consecutive quarters to ' + esc(ttm.end) + '.' : '')) : '')
    + (M.ttmMissing ? (annualOnly ? ' No ' + (isBal ? 'Current' : 'TTM') + ' column: this filer reports annual periods only (no quarterly filings in companyfacts).' : (isBal ? ' No Current column: no quarter-end balance sheet is filed after the last fiscal year.' : ' No TTM column: the last four quarters are not four consecutive fiscal quarters (see the build notes).')) : '')
    + (cur !== 'USD' ? ' <b>Not USD</b> — shown as filed, no conversion.' : '');
  var span = stmSpan(M); if (span) units += ' <b>' + esc(span) + '</b> — scroll the table sideways for the older periods.';
  var table = M.rows.length ? renderStatementsTable(M, stm.line) : '<p class="note">No ' + esc(STM_NAMES[stm.statement] || stm.statement) + ' lines carry a value for this period.</p>';
  var legend = '<p class="note">' + (M.anyDerived ? '† derived quarter: year-to-date minus the prior year-to-date in the same fiscal year; Q4 = fiscal year minus nine months. ' : '')
    + (M.anyBasisBreak ? 'Greyed quarters: that fiscal year\'s four quarters do not add up to its restated fiscal-year figure (filed on the earlier basis — a divestiture or restatement), so their growth cells are blank. ' : '')
    + (M.anyInclRestricted ? RESTRICTED_LEGEND : '')
    + 'Tap a line\'s name to chart it. Source: ' + esc(d.source || 'SEC EDGAR companyfacts') + (d.as_of ? ', updated ' + esc(d.as_of) : '') + (lf.form ? '; latest filing ' + esc(lf.form) + (lf.filed ? ' filed ' + esc(lf.filed) : '') + (lf.period ? ' for the period ending ' + esc(lf.period) : '') : '') + '.</p>';
  var warn = arr(d.warnings).map(function (w) { return '<li>' + esc(w) + '</li>'; });
  // the chart card only while the open line has values in this periodicity (a period switch can drop the row — the card goes too)
  return '<p class="note units">' + units + '</p>' + table + legend + (stm.line && stmSparkSpec(d, stm.statement, stm.period, stm.line) ? renderSparkCard(d, stm) : '')
    + (warn.length ? '<details class="stmwarn"><summary>' + warn.length + ' build note' + (warn.length === 1 ? '' : 's') + ' from statements.py</summary><ul class="warnlist">' + warn.join('') + '</ul></details>' : '');
}
/* stm = {status: idle|loading|ready|missing|error|embedded, data, error, statement, period, growth, line, site}. */
function renderStatements(record, stm) {
  stm = stmNorm(stm);
  var s = obj(record.score), t = String(s.ticker || record.ticker || obj(record.row).ticker || '');
  var seg = function (cls, attr, items, cur, label) { return '<div class="seg ' + cls + '" role="group" aria-label="' + label + '">' + items.map(function (it) { return '<button type="button" data-' + attr + '="' + it[0] + '" class="' + (it[0] === cur ? 'on' : '') + '" aria-pressed="' + (it[0] === cur) + '">' + it[1] + '</button>'; }).join('') + '</div>'; };
  var bar = '<div class="stmbar">' + seg('stmseg', 'stm', STM_TABS, stm.statement, 'Statement') + seg('stpseg', 'stp', STM_PERIODS, stm.period, 'Period') + '<label class="tgl"><input type="checkbox" class="stm-growth"' + (stm.growth ? ' checked' : '') + '> Growth rows</label></div>';
  var body;
  if (stm.status === 'embedded') body = '<p class="note">The full statements are on the site — ' + (stm.site ? '<a class="seefc" href="' + esc(stm.site + '#' + t + '.financials') + '">open ' + esc(t) + '\'s Financials tab there ›</a>' : 'open ' + esc(t) + '\'s Financials tab on the site (this file carries no link to it: the data layer did not record the site URL)') + '. This attachment carries the summary tables below only.</p>';
  else if (stm.status === 'missing') body = '<p class="note">Full statements have not been built for ' + esc(t) + ' yet: <code>statements.py</code> writes <code>' + esc(t) + '/statements.json</code> and <code>build_site.py</code> serves it as <code>data/' + esc(t) + '.statements.json</code>. The summary tables below come from fundamentals.json.</p>';
  else if (stm.status === 'error') body = '<p class="note">The statements file could not be loaded' + (stm.error ? ' (' + esc(stm.error) + ')' : '') + '. <button type="button" class="wbtn sm stm-retry">Retry</button> The summary tables below come from fundamentals.json; reopening the tab retries too.</p>';
  else if (stm.status === 'ready' && stm.data) body = renderStatementsBody(stm, t);
  else body = '<div class="twrap"><table class="fin stm"><tbody><tr class="loading"><th>Loading the full statements…</th><td class="note">./data/' + esc(t) + '.statements.json</td></tr></tbody></table></div>';
  return '<section class="sec stmsec" id="stmsec"><h2>Financial statements</h2><p class="note">Income statement, balance sheet, cash-flow statement and derived metrics over the whole EDGAR filing history — every fiscal year, every derivable quarter and the trailing twelve months. Filed values and plain arithmetic on them; nothing estimated.</p>'
    + '<div class="card stmcard">' + bar + '<div class="stmbody">' + body + '</div></div></section>';
}

/* ---- Dividends (fundamentals.json "dividends" block) */
/* The price the block's yields stand on, worded from its own price_source (HTML; null without a price): build_site reprices
   the block at prices.json's last close ('prices.json stats.last'); fundamentals.py falls back to score.json's analysis price
   when there is no prices.json yet. Across a split since scoring the block is shown as written (never repriced: its filed
   DPS and share count would meet a post-split close) — the wording says so. */
function divPriceWords(d, sp) {
  d = obj(d); var p = num(d.price), date = isoDay(d.price_date);
  if (p === null) return null;
  if (sp) {
    var before = date && (!sp.scored_date || date <= sp.scored_date);
    return fmtMoney(p) + (date ? ' on ' + esc(date) : '') + (before ? ', before the ' + esc(sp.split) + ' split' : ' — not repriced across the ' + esc(sp.split) + ' split since scoring');
  }
  var at = fmtMoney(p) + (date ? ' (' + esc(date) + ')' : '');
  return String(d.price_source || '').indexOf('score.json') >= 0 ? 'the scored price ' + at + ', no prices.json yet' : 'the last close ' + at;
}
function renderDividends(record) {
  var fund = obj(record.fundamentals), d = fund.dividends;
  if (!d || typeof d !== 'object' || Array.isArray(d)) return '<div class="card empty"><p class="note">Dividend enrichment has not run for this name yet — fundamentals.py adds a <code>dividends</code> block (declared / paid per-share facts, dividends paid, buybacks, issuance) once it is re-run.</p></div>';
  var price = num(d.price), dps = num(d.dps_ttm), basis = d.dps_basis, sp = splitInfo(record);
  // "No dividend" is decided from the block's frequency ('none' = no per-share fact AND nothing paid) and the absence of
  // dividends paid / DPS history — never from dps_ttm being null (CCL pays quarterly with dps_ttm null after the staleness
  // rule; TKO, a 20-F-style payer, has frequency null with a note). Those render as payers with the note.
  var freq = d.frequency === undefined ? null : d.frequency, hasPaid = num(d.dividends_paid_ttm) !== null && num(d.dividends_paid_ttm) > 0;
  var dpsFacts = arr(d.history).filter(function (r) { return r && typeof r === 'object' && num(r.dps) !== null && num(r.dps) > 0; });
  var annFacts = arr(d.annual_dps).filter(function (r) { return r && typeof r === 'object' && num(r.dps) !== null && num(r.dps) > 0; });
  var hasDps = dpsFacts.length > 0 || annFacts.length > 0;
  var payer = freq === 'none' ? hasPaid : (hasDps || hasPaid);
  var priceNote = divPriceWords(d, sp); // null without a price: the sentences below say the yields are blank
  // buyback / net buyback / shareholder yield print yields_display's label (≥ / ≤ / ≈ when a leg is partial) with the note in
  // the tooltip; the leg amounts come from dividends.legs (a partial leg still carries its filed sum — HBAN's Q1-only $150M)
  var legs = obj(d.legs), legV = function (k, alt) { var v = num(obj(legs[k]).value); return v !== null ? v : num(alt); };
  // Q8 bug 3: a non-USD block's DPS and flow legs are filed in its own currency and the price / market cap are USD — the
  // amounts carry the currency code and no leg ÷ market cap share is printed (the yields themselves are null). A block
  // that does not record its unit (written before 2026-10-19 in a non-USD file — divCurrency) prints the bare amounts.
  var DC = divCurrency(fund), cur = DC.cur, cross = cur !== 'USD';
  var unrecNote = DC.recorded ? '' : 'The currency of the dividend amounts on this tab is not recorded: this block was written before 2026-10-19, when the readers took a filed USD fact first, so they may be USD or ' + esc(DC.file) + ' (the currency fundamentals.json reports in). They print without a currency and no yield is computed until the file\'s next refresh records it.';
  var amt = function (v) { return fmtBigCur(v, cur); }, dpsF = function (v) { return fmtDpsCur(v, cur); };
  var bbV = legV('buybacks', d.buybacks_ttm), issV = legV('share_issuance', d.issuance_ttm);
  // the shareholder-yield caption names its own dividend leg (cash paid ÷ market cap), which differs from the DPS-based
  // Dividend yield tile when the share count moved (HBAN: 3.04% paid vs a 4.11% DPS yield)
  var divPaidV = legV('dividends_paid', d.dividends_paid_ttm), mcap = num(d.market_cap);
  var shyCaption = (divPaidV === null ? 'dividends paid (none filed)' : divPaidV === 0 ? 'no dividends paid' : 'dividends paid ' + amt(divPaidV) + (mcap && mcap > 0 && !cross ? ' (' + fmtPct(divPaidV / mcap, 2) + ')' : '')) + ' + net buyback, ÷ market cap' + (mcap && mcap > 0 ? ' ' + fmtBig(mcap) : '') + (cross ? (DC.recorded ? ' (USD; the legs are in ' + esc(cur) + ', so no yield is computed)' : ' (USD; the legs\' currency is not recorded in this block, so no yield is computed)') : '');
  var cashTiles = [
    yieldTile(d, 'buyback_yield', 'Buyback yield', '', bbV !== null ? amt(bbV) + ' TTM' : 'no buyback filed'),
    yieldTile(d, 'net_buyback_yield', 'Net buyback yield', signCls(d.net_buyback_yield), issV !== null ? 'buybacks − issuance ' + amt(issV) : 'buybacks − issuance'),
    yieldTile(d, 'shareholder_yield', 'Shareholder yield', signCls(d.shareholder_yield), shyCaption, 'The dividend leg is cash dividends paid over the trailing twelve months (cash-flow statement), not TTM DPS × shares, so it need not equal the Dividend yield tile (TTM DPS ÷ price).')
  ];
  var parts = [];
  if (!payer) {
    var paid = num(d.dividends_paid_ttm);
    var why = (paid === null || paid === 0) ? 'no dividend per-share fact or dividend payment in the filings' : 'no per-share dividend fact filed; cash dividends paid TTM ' + amt(paid);
    parts.push('<div class="card nodiv"><span class="k">Dividend</span><span class="bv">No dividend</span><p class="note">' + why + '. Capital returned to shareholders comes through buybacks, if any — ' + (priceNote ? 'the yields below use ' + priceNote : 'no price is on file, so the yields below are blank') + '.</p></div>');
    parts.push('<div class="tiles">' + cashTiles.join('') + '</div>');
  } else {
    var g5 = num(d.dps_cagr_5y), g3 = num(d.dps_cagr_3y);
    var gsub = joinNonEmpty([g5 !== null ? '5-yr CAGR ' + fmtPct(g5, 1, true) : '', g3 !== null ? '3-yr CAGR ' + fmtPct(g3, 1, true) : ''], ' · ');
    var gy = num(d.growth_years), cut = d.last_cut_fy;
    if (dps === null) parts.push('<div class="card nodiv"><span class="k">Dividend</span><span class="bv">Pays a dividend — no trailing-twelve-month per-share figure</span><p class="note">'
      + joinNonEmpty([hasPaid ? 'Cash dividends paid TTM ' + amt(d.dividends_paid_ttm) : '', dpsFacts.length ? dpsFacts.length + ' per-share fact' + (dpsFacts.length === 1 ? '' : 's') + ' filed, latest ' + dpsF(dpsFacts[0].dps) + ' (' + esc(dpsFacts[0].period_end) + ')' : (annFacts.length ? 'latest full-year DPS ' + dpsF(annFacts[annFacts.length - 1].dps) + ' (FY' + esc(annFacts[annFacts.length - 1].fy) + ')' : '')], ' · ')
      + '. A TTM DPS and yield need four consecutive quarterly per-share facts (or a current full-year fact) — the notes below say what is missing.</p></div>');
    var tiles = [
      yieldTile(d, 'dividend_yield', 'Dividend yield', '', dps === null ? 'no TTM DPS — see notes' : (price !== null ? 'TTM DPS ÷ ' + fmtMoney(price) : 'no price on file')),
      tile('Annual dividend', dpsF(dps), '', dps === null ? (annFacts.length ? 'last full year FY' + esc(annFacts[annFacts.length - 1].fy) + ': ' + dpsF(annFacts[annFacts.length - 1].dps) : 'no TTM DPS') : (basis ? 'TTM DPS · ' + esc(basis) : 'TTM DPS')),
      tile('Payout frequency', freq ? (DIV_FREQ[freq] || esc(freq)) : 'Not inferable', '', freq ? '' : 'per-share rate not tagged in the filings'),
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
    var rows = hist.map(function (r) { return '<tr><td class="mono">' + esc(r.period_end) + '</td><td class="num mono">' + dpsF(r.dps) + '</td><td>' + esc(r.kind) + '</td></tr>'; }).join('');
    parts.push(section('Dividend history', '<div class="card"><div class="twrap"><table class="mini"><thead><tr><th>Period end</th><th class="num">DPS</th><th>Basis</th></tr></thead><tbody>' + rows + '</tbody></table></div><p class="note">The last ' + hist.length + ' per-share facts, newest first, at their filed precision.</p></div>'));
  }
  // price_note (fundamentals.py: "price: … from score.json …" / "… carries a price — yields null") leads the list; it is never
  // in `notes` any more (build_site drops it from older blocks), and an equal entry is skipped so it cannot print twice
  var pn = typeof d.price_note === 'string' && d.price_note ? d.price_note : null;
  var notes = (pn ? '<li>' + esc(pn) + '</li>' : '') + (unrecNote ? '<li>' + unrecNote + '</li>' : '') + arr(d.notes).filter(function (x) { return x !== pn; }).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
  // the share basis the block used and the market cap on that basis — it can differ from the header's live market cap (a different share count)
  var so = num(d.shares_outstanding), sd = num(d.shares_diluted), cap = num(d.market_cap);
  var meta = 'Share basis: ' + (d.shares_source ? esc(d.shares_source) : (sd !== null ? 'latest diluted weighted-average count' : '—')) + (so !== null ? ' — ' + fmtCnt(so) + ' shares' + (d.shares_as_of ? ' as of ' + esc(d.shares_as_of) : '') : (sd !== null ? ' — ' + fmtCnt(sd) + ' diluted shares' : ''))
    + (cap !== null ? ' · market cap on that basis ' + fmtBig(cap) + (d.market_cap_basis ? ' (' + esc(d.market_cap_basis) + ')' : '') : '') + " — the header's market cap uses the engine's diluted count at the last close, so the two can differ.";
  parts.push("<p class=\"note\">Filing-direct EDGAR figures: per-share dividend facts (declared or paid, as filed) and the cash-flow statement's dividends paid, buybacks and issuance; TTM is the last four filed quarters. " + (priceNote ? 'Yields use ' + priceNote + '.' : 'No price is on file, so the yields are blank.')
    + (sp ? ' Per-share dividends are as filed: a split the filings do not report yet is not reflected, so the block keeps its own price and date.' : '') + '</p><p class="note">' + meta + '</p>' + (notes ? '<ul class="warnlist">' + notes + '</ul>' : ''));
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
  parts.push('<p class="note">Source: ' + esc(sg.source || '') + (fl ? ' — ' + fl : '') + '.' + (sg.as_of ? ' Updated ' + esc(sg.as_of) + '.' : '') + '</p>' + (warn ? '<ul class="warnlist">' + warn + '</ul>' : ''));
  return parts.join('');
}

/* ---- Forecast: three sub-tabs (owner decision, 2026-10-14 night) — DCF (ours), Street (Nasdaq analyst data,
   third-party, never an input), Analysts (coverage and rating history). Hash form: #T.forecast (DCF),
   #T.forecast.street, #T.forecast.analysts. */
var SUBTABS = [['dcf', 'DCF'], ['street', 'Street'], ['analysts', 'Analysts']];
var SUB_KEYS = SUBTABS.map(function (t) { return t[0]; });
var FC_YEARS = [1, 2, 3, 5, 10, 15];

/* Filed OE/share history, oldest first, last 10 fiscal years: a fiscal year gets a value only when BOTH its owner's
   earnings and its diluted share count are filed — fundamentals.annual.oe_per_share, or OE ÷ diluted shares (display
   arithmetic on the two filed values) when that cell is empty; every other year is null with the reason in `why`
   ("FY2025: capex not filed (…)") and `reason` (the same text without the year, so oeGapNote can group a run of years).
   The engine CSV is used only for a record without fundamentals.annual, and never for a row an override filled.
   - An override is described by its kind: 'estimate' is not a filed value; 'filing' IS a filed value, read from the
     filing text (CFG's capex, TDY's SBC) — but it is not in fundamentals.json and the engine applies the one figure to
     every untagged year, so the year stays blank and the note says exactly that.
   - A fiscal year missing from fundamentals.annual (MTD FY2014–16) gets a null placeholder, found from the period ends,
     so two years apart never sit next to each other as if adjacent.
   - Share basis: a year whose filed diluted count is more than SHARE_BASIS_X× away from the recent basis (median of the
     last three filed counts) is not plotted — WRB's FY2017–22 counts are in thousands (193,527), CMG's FY2016–21 are
     pre-50:1-split. Per-share figures on two bases are not comparable, and the app never restates them — with one
     exception: a split since scoring (record.split_restated). build_site restated the run (the forecast, the base) to
     today's share units, so a filed year still on the pre-split basis (splitDivisor) is divided by the factor — its count
     multiplied — before the basis rule runs, and `split` names the factor (oeSplitNote prints it under the charts).
   - Leading empty years are kept (labels and reasons), so a name with no plottable year still gets fiscal-year labels
     and a note that says why (TDY: SBC not tagged in any year). */
var OE_LEGS = { ocf: 'operating cash flow', capex: 'capex', sbc: 'stock-based compensation', shares: 'diluted share count' };
var SHARE_BASIS_X = 5, SHARE_JUMP_X = 3;
function filingCite(src) {
  var m = /^Form\s+[\w\-\/]+\s+for\s+(?:the\s+)?(?:fiscal\s+)?(?:year|period)\s+ended\s+[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}/.exec(String(src || ''));
  return m ? 'the ' + m[0] : 'the filing';
}
function overrideWhy(o, csv) { // one missing leg the engine run filled, worded by the override's kind
  var f = OE_LEGS[o.field] || String(o.field || 'a figure'), n = arr(o.periods_filled).length, v = num(o.value);
  var amt = v === null ? 'a figure' : (o.field === 'shares' ? fmtCnt(v) + ' shares' : v === 0 ? '$0' : fmtBig(v));
  if (o.kind === 'filing') return f + ' not tagged in companyfacts (the engine run uses ' + amt + ' read from ' + filingCite(o.source) + (n === 2 ? ' for both untagged years' : n > 2 ? ' for all ' + n + ' untagged years' : '')
    + ' — a filing value, but not in fundamentals.json, so not plotted)';
  var what = o.kind === 'estimate' ? 'an estimate' : 'an override' + (o.kind ? ' (' + String(o.kind) + ')' : '');
  return csv ? f + ' filled by ' + what + ' in the engine run (not a filed value)' : f + ' not filed (the engine run fills ' + f + ' with ' + what + ' — not a filed value)';
}
/* An engine CSV *_tag cell names the filed tag(s) a figure came from; since engine 5.5 a capex cell can be a '+'-joined list
   of the summed component tags ("PaymentsToExploreAndDevelopOilAndGasProperties+PaymentsToAcquireOilAndGasProperty"). The
   year is an override year when OVERRIDE is any one of them. */
function isOverrideTag(v) { return v !== null && v !== undefined && String(v).toUpperCase().split('+').map(function (t) { return t.trim(); }).indexOf('OVERRIDE') >= 0; }
function fyGapYears(a, b) { // whole fiscal years missing between two consecutive annual rows (0 when adjacent / unknown)
  var p = isoParts(a.end), q = isoParts(b.end);
  if (p && q) { var d = (q.ms - p.ms) / 864e5; return d > 400 ? Math.round(d / 365.25) - 1 : 0; }
  var x = Number(a.fy), y = Number(b.fy); return isFinite(x) && isFinite(y) && y - x > 1 ? y - x - 1 : 0;
}
function fyAdjacent(a, b) { // one fiscal year apart (period ends 330–400 days apart; fiscal-year labels when an end is missing)
  var p = isoParts(a.end), q = isoParts(b.end);
  if (p && q) { var d = (q.ms - p.ms) / 864e5; return d >= 330 && d <= 400; }
  var x = Number(a.fy), y = Number(b.fy); return isFinite(x) && isFinite(y) && y - x === 1;
}
function oeHistory(record) {
  var fund = obj(record.fundamentals), ann = arr(fund.annual).filter(function (r) { return r && typeof r === 'object'; }), rows = [];
  var n = obj(record.numbers), ovr = arr(n.overrides_applied).filter(function (o) { return o && typeof o === 'object'; });
  var overrideFor = function (field, end) { var hit = null; ovr.forEach(function (o) { if (!hit && o.field === field && (end === null || arr(o.periods_filled).some(function (p) { return String(p).slice(0, 10) === String(end || '').slice(0, 10); }))) hit = o; }); return hit; };
  var legWhy = function (field, end) { var o = overrideFor(field, end || ''); return o ? overrideWhy(o, false) : OE_LEGS[field] + ' not filed'; };
  var cell = function (r, fy, csv) {
    var oe = num(r.oe_conservative), sh = num(r.shares_diluted), end = r.period_end || null, base = { fy: fy, end: end, sh: sh !== null && sh > 0 ? sh : null };
    var over = !csv ? null : Object.keys(r).filter(function (k) { return /_tag$/.test(k) && isOverrideTag(r[k]); }).map(function (k) { return k.replace(/_tag$/, ''); });
    if (over && over.length) return Object.assign(base, { v: null, reason: over.map(function (f) { var key = f === 'shares_diluted' ? 'shares' : f, o = overrideFor(key, end || '') || overrideFor(key, null); return o ? overrideWhy(o, true) : f + ' filled by an override in the engine run (not a filed value)'; }).join(' and ') });
    if (oe !== null && sh !== null && sh > 0) { var ps = num(r.oe_per_share); return Object.assign(base, { v: !csv && ps !== null ? ps : oe / sh, reason: '' }); }
    var miss = [];
    if (oe === null) { var legs = ['ocf', 'capex', 'sbc'].filter(function (l) { return num(r[l]) === null; }); if (!legs.length) miss.push("owner's earnings not filed"); legs.forEach(function (l) { miss.push(legWhy(l, end)); }); }
    if (sh === null || !(sh > 0)) miss.push(legWhy('shares', end));
    return Object.assign(base, { v: null, reason: miss.join(' and ') });
  };
  if (ann.length) ann.forEach(function (r) { rows.push(cell(r, String(r.fy || r.period_end || ''), false)); });
  else arr(record.history).filter(function (r) { return r && typeof r === 'object'; }).forEach(function (r) { rows.push(cell(r, String(r.fy_label || r.period_end || ''), true)); });
  // a split since scoring: the filed years still on the pre-split basis into today's share units, like the restated forecast
  // (the engine CSV branch needs nothing — build_site already multiplied its share counts)
  var sp = splitInfo(record);
  if (sp && ann.length) {
    var refs = splitRefs(record);
    rows.forEach(function (h) { var f = splitDivisor(sp, refs, h.sh, h.end, h.fy); if (f === 1) return; h.sh = h.sh * f; if (h.v !== null) h.v = h.v / f; h.split = f; });
  }
  // share basis: the median of the last three filed diluted counts (one slipped latest year cannot move it)
  var shs = rows.filter(function (h) { return h.sh !== null; }).slice(-3).map(function (h) { return h.sh; }).sort(function (a, b) { return a - b; });
  var ref = shs.length ? shs[Math.floor((shs.length - 1) / 2)] : null;
  if (ref) rows.forEach(function (h) {
    if (h.v === null || h.sh === null || Math.max(h.sh / ref, ref / h.sh) <= SHARE_BASIS_X) return;
    h.v = null; h.basis = true;
    h.reason = 'diluted share count more than ' + SHARE_BASIS_X + '× away from the recent filed basis (' + fmtCnt(ref) + ', the median of the last three filed years) — a split, a unit slip or a pre-IPO share class in the filed data, so OE/share is not comparable';
  });
  var out = [];
  rows.forEach(function (h, i) {
    var gap = i ? fyGapYears(rows[i - 1], h) : 0, f0 = i ? Number(rows[i - 1].fy) : NaN;
    for (var k = 1; k <= gap; k++) out.push({ fy: isFinite(f0) ? String(f0 + k) : '?', end: null, sh: null, v: null, gap: true, reason: 'not in fundamentals.annual (fundamentals.py emitted no row for this fiscal year)' });
    out.push(h);
  });
  out.forEach(function (h) { h.why = h.v === null && h.reason ? 'FY' + h.fy + ': ' + h.reason : ''; });
  return out.slice(-10);
}
/* The OE/share chart's y-axis floor. The axis always covers history AND forecast together (drawChart takes every series);
   a floor is set only when a negative filed year reaches further below zero than the whole chart reaches above it (a
   loss-making past next to a positive forecast), at minus that positive extent: the year is pinned to the floor with a ▼
   marker and its real value in the tooltip, so one deep loss cannot flatten fifteen projection years into a line. History
   alone (Tier F) is never floored — every filed year is on the scale. Null when no floor is needed. */
function oeAxisFloor(histVals, fcVals) {
  var h = arr(histVals).filter(isNum), f = arr(fcVals).filter(isNum);
  if (!h.length || !f.length) return null;
  var hMin = Math.min.apply(null, h), P = Math.max.apply(null, h.concat(f).concat([0]));
  return hMin < 0 && P > 0 && hMin < -P ? -P : null;
}
function yoy(vals) { // growth when the prior value is positive; null otherwise (a ratio on a negative base has no sign)
  return vals.map(function (v, i) { var p = i ? vals[i - 1] : null; return v !== null && p !== null && p > 0 ? v / p - 1 : null; });
}
/* Year-over-year OE/share growth on oeHistory's rows: only between two plotted years ONE fiscal year apart whose diluted
   counts moved less than SHARE_JUMP_X× (a 4:1 split such as DXCM's sits under the basis rule but over this one). `why`
   names the bars left blank for a gap or a share-basis jump; a prior year that is not positive needs no note. */
function histYoy(hist) {
  var H = arr(hist), g = [], why = [];
  H.forEach(function (h, i) {
    var p = i ? H[i - 1] : null, w = '';
    var ok = p && h.v !== null && p.v !== null && p.v > 0;
    if (ok && !fyAdjacent(p, h)) { ok = false; w = 'FY' + h.fy + ': FY' + p.fy + ' is not the prior fiscal year'; }
    if (ok && p.sh && h.sh && Math.max(h.sh / p.sh, p.sh / h.sh) > SHARE_JUMP_X) { ok = false; w = 'FY' + h.fy + ': diluted shares moved ' + (Math.max(h.sh / p.sh, p.sh / h.sh)).toFixed(1) + '× from FY' + p.fy + ' (' + fmtCnt(p.sh) + ' → ' + fmtCnt(h.sh) + ' — a split, a merger or a unit change), so the per-share change is not comparable'; }
    g.push(ok ? h.v / p.v - 1 : null); why.push(w);
  });
  return { g: g, why: why };
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
  var hy = histYoy(hist);
  return { labels: labels.concat(fcLabels), fcLabels: fcLabels, hist: hist, histVals: histVals, base: base, baseIndex: H - 1, H: H, N: N,
    weighted: pad(w, true), bear: pad(paths.bear, true), bull: pad(paths.bull, true), super_bear: pad(paths.super_bear, true), super_bull: pad(paths.super_bull, true),
    raw: { weighted: w, bear: arr(paths.bear).map(num), bull: arr(paths.bull).map(num), super_bear: arr(paths.super_bear).map(num), super_bull: arr(paths.super_bull).map(num) },
    histGrowth: hy.g, histGrowthWhy: hy.why, filedCount: hist.filter(function (h) { return h.v !== null; }).length, wGrowth: wg, bearGrowth: g('bear'), bullGrowth: g('bull') };
}
function hal(title, cols, rows, note) { // High / Avg / Low table
  var head = cols.map(function (c) { return '<th class="num">' + c + '</th>'; }).join('');
  var body = rows.map(function (r) { return '<tr' + (r.strong ? ' class="strong"' : '') + '><th>' + r.name + '</th>' + r.cells.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('');
  return '<div class="twrap"><table class="fin hal"><thead><tr><th>' + title + '</th>' + head + '</tr></thead><tbody>' + body + '</tbody></table></div>' + (note ? '<p class="note">' + note + '</p>' : '');
}
/* The years the OE/share chart leaves blank, and why. A run of consecutive years with the same reason is one entry
   (" Not shown: FY2020–FY2025: capex not tagged in companyfacts (…)."); rows without `reason` print their `why` as is. */
function oeGapNote(hist) {
  var gaps = [], out = [], cur = null; // a plotted year (or a different reason) ends a run
  arr(hist).forEach(function (h) {
    if (!h) return;
    if (h.v !== null || !(h.why || h.reason)) { cur = null; return; }
    if (h.reason && cur && cur.reason === h.reason) { cur.to = h.fy; return; }
    cur = { reason: h.reason || null, from: h.fy, to: null, why: h.why }; gaps.push(cur);
  });
  gaps.forEach(function (g) { out.push(esc(g.reason ? 'FY' + g.from + (g.to && g.to !== g.from ? '–FY' + g.to : '') + ': ' + g.reason : g.why)); });
  return out.length ? ' <b>Not shown:</b> ' + out.join('; ') + '.' : '';
}
/* The plotted years oeHistory divided for a split since scoring (h.split), as one sentence; when none needed it (filed after
   the split) the sentence says the filed years are already on today's basis. '' without a split or without a plotted year. */
function oeSplitNote(hist, sp) {
  if (!sp) return '';
  var H = arr(hist).filter(function (h) { return h && !h.gap && h.v !== null && h.v !== undefined; }), adj = H.filter(function (h) { return h.split; }); // plotted years only
  if (!adj.length) return H.length ? ' The filed years shown are already on the post-split basis of the ' + esc(sp.split) + ' split since scoring, like the restated forecast.' : '';
  var fys = adj.map(function (h) { return String(h.fy); }), a = Number(fys[0]), b = Number(fys[fys.length - 1]);
  var span = fys.length > 1 && isFinite(a) && isFinite(b) && b - a + 1 === fys.length ? 'FY' + fys[0] + '–FY' + fys[fys.length - 1] : fys.map(function (f) { return 'FY' + f; }).join(', ');
  return ' Filed years on the pre-split basis (' + esc(span) + ') are divided by ' + esc(fmtFactor(sp.factor)) + ' for the ' + esc(sp.split) + ' split since scoring, so the filed line reads in today\'s share units next to the restated forecast.';
}
/* The growth chart's blank historical bars that need a reason (not one fiscal year apart, or a share-basis jump). */
function oeYoyNote(whys) {
  var w = arr(whys).filter(Boolean).map(esc);
  return w.length ? ' <b>No year-over-year bar:</b> ' + w.join('; ') + '.' : '';
}
/* History only (Tier F, or a run without stored paths): the filed OE/share line, no forecast. Without any plottable
   year the section still says which years were looked at and why none is drawn; '' only without any annual row. */
function oeHistorySection(record) {
  var H = oeHistory(record), filed = H.filter(function (h) { return h.v !== null; });
  if (!H.length) return '';
  var src = arr(obj(record.fundamentals).annual).length ? ' (fundamentals.json)' : ' (engine history CSV)';
  if (!filed.length) return section("Owner's earnings per share — history", '<div class="card empty"><p class="note">No fiscal year' + src + ' has both owner\'s earnings and the diluted share count filed, so no OE/share history is drawn.' + oeGapNote(H) + ' No forecast is drawn: this run has no projection path.</p></div>');
  var neg = filed.filter(function (h) { return h.v < 0; }).length;
  // fundamentals.json's oe_conservative also deducts the engine's intangible leg (Q8 / engine 5.5 capex) — the formula names it
  // whenever a plotted year has one (BBIO FY2025: −445.9M − 1.1M − 133.0M = −580.0M, plotted −588.5M with $8.5M of intangibles)
  var annRows = arr(obj(record.fundamentals).annual), withInt = filed.some(function (h) { return annRows.some(function (r) { return r && h.end && r.period_end === h.end && intangCapex(r) !== null; }); });
  return section("Owner's earnings per share — history", '<div class="card">' + chartDiv('fc-oe') + '<p class="note">Filed owner\'s earnings (operating cash flow − ' + (withInt ? 'PP&amp;E and intangible capex' : 'capex') + ' − stock-based compensation) per diluted share by fiscal year'
    + src + ' — only years with both figures filed, on one share basis.' + (neg ? ' ' + neg + ' of the ' + filed.length + ' years are negative; the axis covers every one.' : '') + oeGapNote(H) + oeSplitNote(H, splitInfo(record))
    + ' No forecast is drawn: this run has no projection path.</p></div>', 'What was filed — there is no positive base for the engine to grow.');
}
function renderForecastDCF(record) {
  var s = obj(record.score), n = obj(record.numbers), fc = obj(record.forecast), row = obj(record.row);
  var hasScn = Object.keys(obj(n.scenarios)).length || Object.keys(obj(s.scenarios)).length || Object.keys(obj(fc.sensitivity)).length;
  var noProj = "<div class=\"card empty\"><p class=\"note\">No projection: the engine found no positive normalized owner's earnings (Tier F), so there is no cash-flow path to discount.</p></div>";
  var sp = splitInfo(record), spTop = splitNoteHTML(sp, sp && sp.as_scored && num(sp.as_scored.price) !== null ? 'Scored at ' + fmtMoney(sp.as_scored.price) + (num(sp.as_scored.iv_at_15) !== null ? ' with IV @15% ' + fmtMoney(sp.as_scored.iv_at_15) : '') + ' before the split.' : '');
  if (!hasScn) return spTop + oeHistorySection(record) + noProj;
  var parts = spTop ? [spTop] : [], inp = Object.keys(obj(fc.inputs)).length ? obj(fc.inputs) : obj(n.inputs);
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
      + '<p class="note">' + (J.filedCount ? 'Solid line: filed owner\'s earnings per diluted share by fiscal year' + (arr(obj(record.fundamentals).annual).length ? ' (fundamentals.json)' : ' (engine history CSV)') + ' — only years with both owner\'s earnings and the diluted share count filed, on one share basis.' : (J.hist.length && J.hist[0].fy !== 'Base' ? 'No solid line: no fiscal year' + (arr(obj(record.fundamentals).annual).length ? ' in fundamentals.json' : ' in the engine history CSV') + ' has both owner\'s earnings and the diluted share count filed.' : 'No solid line: this record has no filed annual history.')) + oeGapNote(J.hist) + oeSplitNote(J.hist, sp) + ' Dashed lines from the base year: the engine\'s projection — base ' + fmtMoney(base) + '/share (' + esc({ ttm_json: 'TTM', agent_supplied_ttm_override: 'TTM pin', median_of_last_3_fy_oe_per_share: '3-year median' }[s.base_source] || s.base_source || 'engine base') + ') grown along each scenario\'s path; the bold dashed line is the probability-weighted path whose IRR is the headline, the shaded band runs from super bear to super bull. Year-15 flow carries a Gordon terminal value at ' + fmtPct(gterm) + ' growth.' + (fc.replayed ? ' Paths replayed from the recorded run inputs through the engine (pre-5.4 run).' : '') + '</p></div>', 'What the DCF actually discounts, against what was filed.'));
    var gy = [1, 2, 3], gcell = function (vals, y) { var v = get(vals, y - 1); return '<span class="mono ' + signCls(v) + '">' + fmtPct(v, 1, true) + '</span>'; };
    var hasG = J.bearGrowth.length && J.bullGrowth.length;
    var t2 = hal('OE / share growth', gy.map(yl), [
      { name: 'High <span class="sub">bull growth path</span>', cells: gy.map(function (y) { return hasG ? gcell(J.bullGrowth, y) : '—'; }) },
      { name: 'Avg <span class="sub">weighted path, YoY</span>', strong: true, cells: gy.map(function (y) { return gcell(J.wGrowth, y); }) },
      { name: 'Low <span class="sub">bear growth path</span>', cells: gy.map(function (y) { return hasG ? gcell(J.bearGrowth, y) : '—'; }) }]);
    parts.push(section("Owner's earnings growth", '<div class="card">' + chartDiv('fc-oegrowth') + t2
      + '<p class="note">Historical bars: year-over-year change in the filed OE/share between consecutive fiscal years (blank where either year is not plotted or the prior year was not positive).' + oeYoyNote(J.histGrowthWhy) + oeSplitNote(J.hist, sp) + ' Forecast bars: the year-over-year change of the probability-weighted path (year 1 is measured from the base, so it also carries the scenarios\' OE level multiples); the error bar runs from the bear to the bull growth path for the same year' + (hasG ? '' : ' (no growth paths stored for this run)') + '.</p></div>'));
  }
  else parts.push(oeHistorySection(record));
  if (arr(paths.weighted).length) {
    parts.push(section("Owner's earnings per share — the five paths", '<div class="card">' + chartDiv('fc-paths') + '<p class="note">Base ' + fmtMoney(base) + "/share × each scenario's OE multiple, grown along its growth path. The weighted line is the probability-weighted path whose IRR is the headline. Year-15 flow carries a Gordon terminal value at " + fmtPct(gterm) + ' growth.' + (fc.replayed ? ' Paths replayed from the recorded run inputs through the engine (pre-5.4 run).' : '') + '</p></div>'));
    if (arr(gpaths.base).length) parts.push(section('Growth fade', '<div class="card">' + chartDiv('fc-growth') + '<p class="note">Growth holds for 2 years, then converges linearly to the ' + fmtPct(gterm) + ' terminal rate over the competitive advantage period of ' + esc(capYears) + ' years (moat ' + esc(moat) + '/10 → CAP = 2 + 1.3 × moat).</p></div>'));
  } else parts.push('<div class="card"><p class="note">No stored projection paths for this run — the 15-year paths appear after the next engine run (5.4+) or when the data layer replays them.</p></div>');
  var sens = sensitivity(record), lv = liveView(record), price = lv.price, wh = lv.is_live ? null : liveWithheld(record);
  var pxWord = lv.is_live ? 'the last close' : wh ? 'the scored price' : "today's price"; // withheld: the scored price is the current one, not "today's"
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
    + tile(lv.is_live ? 'Last close' : wh ? 'Scored price' : "Today's price", fmtMoney(price), '', lv.is_live ? esc(lv.price_date) + ' · scored at ' + fmtMoney(lv.scored_price) : (wh ? esc(pendingText(wh)) : ''), wh ? wh.note : '');
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
/* The filed quarter a year before a consensus quarter (the "from" on a quarterly EPS tile). Nasdaq names its quarters by
   the fiscal quarter's end month ("Sep 2026", fiscal_end "2026-09"): the match is the fundamentals.quarterly row whose
   period_end lies within 45 days of that month's last day one year earlier (Kroger's 52/53-week quarters end a week off
   the month). A "Q3 2026" / "Q3 FY2026" style period falls back to quarter number + year − 1 on the row labels. Null when
   no filed quarter matches or its diluted EPS is not filed. */
function yearAgoQuarter(f, quarters) {
  f = obj(f); var rows = arr(quarters).filter(function (r) { return r && typeof r === 'object'; }), hit = null;
  var m = /^(\d{4})-(\d{2})/.exec(String(f.fiscal_end || '')), mm = null;
  if (!m) { var mp = /^([A-Za-z]{3})[a-z]*\.?\s+(\d{4})$/.exec(String(f.period || '').trim()), mi = mp ? MON.indexOf(mp[1].charAt(0).toUpperCase() + mp[1].slice(1, 3).toLowerCase()) : -1; if (mi >= 0) mm = { y: +mp[2], m: mi }; }
  else mm = { y: +m[1], m: +m[2] - 1 };
  if (mm) {
    var target = Date.UTC(mm.y - 1, mm.m + 1, 0), best = 46 * 864e5;
    rows.forEach(function (r) { var p = isoParts(r.period_end); if (p && Math.abs(p.ms - target) < best) { best = Math.abs(p.ms - target); hit = r; } });
  } else {
    var q = qParse(f.period);
    if (q) rows.forEach(function (r) { var h = qParse(r.label || r.period_end); if (!hit && h && h.q === q.q && h.y === q.y - 1) hit = r; });
  }
  if (!hit || num(hit.eps_diluted) === null) return null;
  return { v: num(hit.eps_diluted), label: esc(hit.label || hit.period_end) + ' filed', end: hit.period_end || null };
}
function fyParse(period) { var m = /(\d{4})/.exec(String(period || '')); return m ? Number(m[1]) : null; }
/* Filed diluted EPS by fiscal year, oldest first, for the comparisons with Nasdaq's consensus (in today's share units). After
   a split since scoring a year still on the pre-split basis is divided by the factor (splitDivisor; `split` names it) and
   its growth is recomputed where the basis changes between two years; otherwise the filed values as they are. */
function epsAnnualHist(record) {
  var sp = splitInfo(record), refs = sp ? splitRefs(record) : null, prev = null;
  return arr(obj(record.fundamentals).annual).filter(function (r) { return r && typeof r === 'object' && num(r.eps_diluted) !== null; }).map(function (r) {
    var f = sp ? splitDivisor(sp, refs, r.shares_diluted, r.period_end, r.fy) : 1, v = num(r.eps_diluted) / f, g = num(r.eps_diluted_growth);
    if (prev && prev.f !== f) g = prev.v > 0 ? v / prev.v - 1 : null; // the filed growth spans the two bases
    prev = { f: f, v: v };
    return { fy: String(r.fy || ''), v: v, g: g, r: r, split: f !== 1 ? f : 0 };
  });
}
/* The year-ago filed quarter for a consensus quarter (yearAgoQuarter), split-adjusted like epsAnnualHist. */
function yearAgoQuarterAdj(record, f, quarters) {
  var q = yearAgoQuarter(f, quarters), sp = splitInfo(record);
  if (!q || !sp) return q;
  var row = obj(arr(quarters).filter(function (r) { return r && typeof r === 'object' && (r.period_end || null) === q.end; })[0]);
  var k = splitDivisor(sp, splitRefs(record), row.shares_diluted, q.end, null);
  return k === 1 ? q : Object.assign({}, q, { v: q.v / k, label: q.label + ', split-adjusted', split: k });
}
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
  var aTiles = '<div class="tiles">' + epsTile('EPS this year', fa[0] || null, lastFy ? lastFy.v : null, lastFy ? 'FY' + esc(lastFy.fy) + ' filed' + (lastFy.split ? ', split-adjusted' : '') : '') + epsTile('EPS next year', fa[1] || null, fa[0] ? num(fa[0].consensus) : null, fa[0] ? esc(fa[0].period) + ' consensus' : '') + '</div>';
  // the consensus is in today's share units: after a split since scoring a filed "from" still on the pre-split basis is ÷ factor
  var spS = splitInfo(record), refsS = spS ? splitRefs(record) : null;
  var qFrom = function (f) { return yearAgoQuarterAdj(record, f, qH); };
  var q0 = qFrom(fq[0]), q1 = qFrom(fq[1]);
  var qTiles = '<div class="tiles">' + epsTile('EPS this quarter', fq[0] || null, q0 ? q0.v : null, q0 ? q0.label : '') + epsTile('EPS next quarter', fq[1] || null, q1 ? q1.v : null, q1 ? q1.label : '') + '</div>';
  var ffTable = function (histRows, histLabel, fcRows, isQ) {
    var cols = histRows.map(function (r) { return '<th class="num">' + histLabel(r) + ' <span class="sub">filed</span></th>'; }).join('') + fcRows.map(function (f) { return '<th class="num">' + esc(f.period) + ' <span class="sub">consensus</span></th>'; }).join('');
    var line = function (name, hf, ff, cls) { return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th>' + name + '</th>' + histRows.map(function (r) { return '<td>' + hf(r) + '</td>'; }).join('') + fcRows.map(function (f, i) { return '<td>' + ff(f, i) + '</td>'; }).join('') + '</tr>'; };
    var dash = function () { return '—'; };
    var prevEps = function (i) { if (i > 0) return num(fcRows[i - 1].consensus); var h = histRows.length ? histRows[histRows.length - 1] : null; if (!h) return null; if (isQ) { var qf = qFrom(fcRows[0]); return qf ? qf.v : null; } var e = num(h.eps_diluted); return e === null ? null : e / (spS ? splitDivisor(spS, refsS, h.shares_diluted, h.period_end, h.fy) : 1); };
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
    + '<p class="note">Revenue, profit and margin rows show "—" in the consensus columns because Nasdaq publishes EPS consensus only. EPS growth in a consensus column is measured against the prior filed figure (or the prior consensus); the "from" figure on a quarterly tile is the same quarter a year earlier as filed.'
    + (spS && (annH.some(function (h) { return h.split; }) || (q0 && q0.split) || (q1 && q1.split) || annRows.some(function (r) { return splitDivisor(spS, refsS, r.shares_diluted, r.period_end, r.fy) !== 1; }))
      ? ' After the ' + esc(spS.split) + ' split since scoring the filed columns stay as filed; a "from" figure and the EPS growth into a consensus column divide a filed EPS still on the pre-split basis by ' + esc(fmtFactor(spS.factor)) + ' (split-adjusted), because the consensus is in today\'s share units.' : '')
    + '</p></div>'));
  // (5) EPS forecast chart + table
  var epsHal = function (rows, labelOf) { return hal('EPS', rows.map(function (f) { return esc(labelOf(f)); }), [
    { name: 'High', cells: rows.map(function (f) { return '<span class="mono">' + fmtMoney(f.high) + '</span>'; }) },
    { name: 'Avg <span class="sub">consensus</span>', strong: true, cells: rows.map(function (f) { return '<span class="mono">' + fmtMoney(f.consensus) + '</span>'; }) },
    { name: 'Low', cells: rows.map(function (f) { return '<span class="mono">' + fmtMoney(f.low) + '</span>'; }) }]); };
  if (fa.length || annH.length) parts.push(section('EPS forecast', '<div class="card">' + (fa.length ? chartDiv('street-eps') : '') + (fa.length ? epsHal(fa, function (f) { return f.period; }) : '<p class="note">No annual EPS consensus on record.</p>') + '<p class="note">Solid line: filed diluted EPS by fiscal year' + (annH.some(function (h) { return h.split; }) ? ' (years on the pre-split basis ÷ ' + esc(fmtFactor(spS.factor)) + ' for the ' + esc(spS.split) + ' split since scoring)' : '') + '. Dashed: the Nasdaq consensus, with the low–high range of estimates shaded. Consensus EPS is on the analysts\' adjusted basis, not GAAP, so the two lines are not strictly comparable.</p></div>'));
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
  if (!st) return '<div class="card empty"><p class="note">' + (streetPulled(p) ? 'No analyst coverage data on record for this name.' : 'Analyst coverage appears once profile.py has pulled the Nasdaq analyst data for this name.') + '</p>' + honest + '</div>';
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
  var out = [], sp = splitInfo(record);
  // the write-up, the pass-2 note and the judgment quote the run's dollar figures as scored (not restated)
  if (sp) out.push('<p class="note splitnote"><b>' + esc(sp.split) + ' split since scoring.</b> The write-up quotes the run as scored' + (sp.scored_date ? ' (' + esc(sp.scored_date) + ')' : '') + ', before the split: divide its per-share dollar figures (prices, intrinsic values, owner\'s earnings per share) by '
    + esc(fmtFactor(sp.factor)) + ' to compare them with today\'s price. IRRs, tiers and percentages are unchanged.</p>');
  if (record.analysis_md) out.push('<div class="card md">' + md(record.analysis_md) + '</div>');
  else out.push('<div class="card empty"><p class="note">No analysis.md in this folder.</p></div>');
  if (record.second_pass_md) out.push(section('Second pass', '<div class="card md">' + md(record.second_pass_md) + '</div>'));
  return out.join('');
}

/* The Data tab's run market cap (engine 5.5). A pre-5.5 ADS run printed market_cap_est = the per-ADS price × the
   ORDINARY share count; make_score corrects it in score.json (market_cap_basis "ads_corrected_by_make_score",
   market_cap_b = price × shares ÷ ads_ratio), so that figure is shown and the engine's own is named as superseded.
   A 5.5 run's cap is shown with its share basis when that is not the plain latest diluted count. */
function runCapText(s, n) {
  s = obj(s); n = obj(n);
  if (s.market_cap_basis === 'ads_corrected_by_make_score' && num(s.market_cap_b) !== null)
    return fmtCap(s.market_cap_b) + ' (ADS-corrected by make_score: price × shares ÷ ratio; the pre-5.5 engine printed ' + fmtBig(n.market_cap_est) + ')';
  var src = obj(n.market_cap_basis).shares_source;
  return fmtBig(n.market_cap_est) + (src && src !== 'diluted_latest' ? ' (' + esc(src) + ')' : '');
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
  // after a split since scoring the run's per-share figures and share count here are restated (record.split_restated);
  // as_scored keeps the price, IV and base as the run had them
  var sp = splitInfo(record), asc = sp ? sp.as_scored : {}, before = sp ? ' before the ' + esc(sp.split) + ' split' : '';
  kv('Price', fmtMoney(n.price) + ' (' + esc(n.price_source) + ')' + (sp && num(asc.price) !== null ? ' · scored at ' + fmtMoney(asc.price) + before : '') + ' · market cap est. ' + runCapText(s, n) + ' · diluted shares ' + fmtCnt(n.shares_diluted_latest) + (sp ? ' (restated × ' + esc(fmtFactor(sp.factor)) + ')' : ''));
  var inp = obj(n.inputs);
  kv('Base', fmtMoney(n.base_oe_per_share) + '/share' + (sp && num(asc.base_oe_per_share) !== null ? ' (scored ' + fmtMoney(asc.base_oe_per_share) + before + ')' : '') + ' · ' + esc(n.base_source) + ' · pin source ' + esc(inp.base_pin_source));
  if (sp) kv('Split since scoring', esc(sp.split) + ' (factor ' + esc(fmtFactor(sp.factor)) + ')' + (sp.scored_date ? ' · scored ' + esc(sp.scored_date) : '') + (sp.price_date ? ' · restated against the ' + esc(sp.price_date) + ' close' : '') + (num(asc.iv_at_15) !== null ? ' · IV @15% as scored ' + fmtMoney(asc.iv_at_15) : ''));
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
  var parts = [splitNoteHTML(sp, j && typeof j === 'object' ? 'judgment.json below is the run\'s input as entered, before the split.' : '') + section('Provenance', '<div class="card"><div class="twrap"><table class="kv"><tbody>' + rows.join('') + '</tbody></table></div></div>')];
  if (Object.keys(obj(ttm.inputs)).length) {
    var ti = obj(ttm.inputs), trs = '';
    [['ocf', 'Operating cash flow'], ['capex', 'Capex'], ['sbc', 'Stock-based comp'], ['shares_diluted', 'Diluted shares']].forEach(function (c) {
      var k = c[0], d = obj(ti[k]), f = k === 'shares_diluted' ? fmtCnt : fmtBig;
      trs += '<tr><th>' + c[1] + '</th><td class="num mono">' + f(d.fy) + '</td><td class="num mono">' + f(d.ytd_prior) + '</td><td class="num mono">' + f(d.ytd_current) + '</td><td class="num mono strong">' + (k !== 'shares_diluted' ? f(d.ttm) : f(d.ytd_current)) + '</td><td class="small">' + esc(d.fy_tag) + '</td></tr>';
    });
    var fyEnd = get(obj(ti.ocf).fy_period, 1) || '';
    var ovUsed = arr(ttm.overrides_used).map(function (o) { return obj(o).field; }).filter(Boolean);
    parts.push(section('TTM construction', '<div class="card"><div class="twrap"><table class="fin"><thead><tr><th>TTM leg</th><th class="num">FY ' + esc(fyEnd) + '</th><th class="num">− prior YTD</th><th class="num">+ current YTD</th><th class="num">= TTM</th><th>Tag</th></tr></thead><tbody>' + trs + '</tbody></table></div>'
      + "<p class=\"note\">TTM owner's earnings " + fmtBig(ttm.ttm_oe_total) + ' ÷ ' + fmtCnt(ttm.ttm_shares_diluted) + ' shares = <b class="mono">' + fmtMoney(ttm.ttm_oe_per_share) + '</b> / share, computed by ttm.py from EDGAR 10-Q year-to-date facts (FY − prior YTD + current YTD). ' + (ovUsed.length ? 'Overrides used: ' + esc(ovUsed.join(', ')) + '. ' : '')
      + (sp ? 'The legs above are as filed, before the ' + esc(sp.split) + ' split; the share count and the per-share figure in this sentence are restated to today\'s share units.' : '') + '</p></div>'));
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

/* The company page. nav = {prev, next, rank} (tickers by rank) is optional; sub is the Forecast sub-tab;
   opts = {stm (statements-viewer state), stars (per-device watchlist), repo (repo watchlist tickers)}, all optional. */
function renderCompanyHTML(record, tab, nav, sub, opts) {
  record = obj(record); nav = obj(nav); opts = obj(opts);
  tab = TAB_KEYS.indexOf(tab) >= 0 ? tab : 'overview';
  sub = SUB_KEYS.indexOf(sub) >= 0 ? sub : 'dcf';
  var s = obj(record.score), row = obj(record.row), ticker = s.ticker || record.ticker || row.ticker || '';
  var navRight = 'Pass 1 · ' + esc(s.analysis_date || row.analysis_date);
  if (obj(s.second_pass).verdict === 'changed') navRight = 'Pass 2 revised · ' + esc(s.second_pass.date);
  var tabBtns = TABS.map(function (t) { return '<button type="button" role="tab" class="tab' + (t[0] === tab ? ' on' : '') + '" data-tab="' + t[0] + '" aria-selected="' + (t[0] === tab) + '">' + t[1] + '</button>'; }).join('');
  // header → sticky tab bar → tab content; the price-vs-value chart is the Overview tab's first card (owner decision, 2026-10-14)
  var panes = TABS.map(function (t) {
    var body;
    try { body = (t[0] === 'overview' ? renderPriceChart(record) : '') + (t[0] === 'forecast' ? renderForecast(record, sub) : t[0] === 'financials' ? renderFinancials(record, opts.stm) : TAB_RENDERERS[t[0]](record)); }
    catch (e) { body = '<div class="card err">This tab could not be rendered: ' + esc(e && e.message) + '</div>'; }
    return '<div class="pane' + (t[0] === tab ? ' on' : '') + '" data-pane="' + t[0] + '" role="tabpanel">' + body + '</div>';
  }).join('');
  var pn = '<div class="pnav">' + (nav.prev ? '<a href="#' + esc(nav.prev) + '" class="pn">← ' + esc(nav.prev) + '</a>' : '<span></span>')
    + '<span class="note">' + (nav.rank ? 'rank ' + esc(nav.rank) : '') + '</span>' + (nav.next ? '<a href="#' + esc(nav.next) + '" class="pn">' + esc(nav.next) + ' →</a>' : '<span></span>') + '</div>';
  return '<article class="page open" id="d-' + esc(safeId(ticker)) + '" data-ticker="' + esc(ticker) + '">'
    + '<nav class="dnav"><a class="back" href="#">← Ranking</a><span class="navr mono">' + navRight + '</span></nav>'
    + renderHeader(record, opts.stars, opts.repo)
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
/* The repo watchlist = meta.watchlist (every ticker in _system/watchlist.json) ∪ index rows flagged watchlist: true; the
   viewer's stars are the per-device extras (localStorage "stocks.watchlist"). */
function repoList(meta, index) {
  var out = normStars(obj(meta).watchlist);
  arr(index).forEach(function (r) { r = obj(r); if (r.watchlist === true) { var t = String(r.ticker || '').toUpperCase(); if (t && out.indexOf(t) < 0) out.push(t); } });
  return out;
}
function isRepo(row, repo) { row = obj(row); return row.watchlist === true || (Array.isArray(repo) && repo.indexOf(String(row.ticker || '').toUpperCase()) >= 0); }
function isWatched(row, stars, repo) { return isRepo(row, repo) || isStarred(row, stars); }
/* The watched names that have a page in this ranking (repo + local stars), deduped, in index (rank) order — exactly the
   rows the "★ Watchlist N" toggle shows with the tier filter on All, and exactly what "Copy tickers" copies. */
function watchTickers(index, repo, stars) {
  var seen = {}, out = [];
  arr(index).forEach(function (r) { r = obj(r); var t = String(r.ticker || '').toUpperCase(); if (t && !seen[t] && isWatched(r, stars, repo)) { seen[t] = 1; out.push(t); } });
  return out;
}
/* What "Copy tickers" copies and what it leaves out, named: {tickers (= the count), outside (repo names outside the
   screened universe — meta.watchlist_outside — with no page), unranked (repo names in the universe, not ranked yet),
   starsOff (device stars with no row in this ranking)}. A ticker with an index row is always in `tickers`, even when the
   data layer also lists it in watchlist_outside (APP, the pilot). */
function watchCopy(meta, index, repo, stars) {
  var inIdx = {}; arr(index).forEach(function (r) { var t = String(obj(r).ticker || '').toUpperCase(); if (t) inIdx[t] = 1; });
  var tickers = watchTickers(index, repo, stars), outsideAll = normStars(obj(meta).watchlist_outside), rp = normStars(repo);
  var outside = outsideAll.filter(function (t) { return !inIdx[t]; }).sort();
  var unranked = rp.filter(function (t) { return !inIdx[t] && outsideAll.indexOf(t) < 0; }).sort();
  var starsOff = normStars(stars).filter(function (t) { return !inIdx[t] && rp.indexOf(t) < 0 && outsideAll.indexOf(t) < 0; }).sort();
  return { tickers: tickers, text: tickers.join(', '), outside: outside, unranked: unranked, starsOff: starsOff };
}
function copyNoteHTML(c) {
  c = obj(c); var parts = [];
  if (arr(c.outside).length) parts.push('outside the screened universe (no page): ' + esc(arr(c.outside).join(', ')));
  if (arr(c.unranked).length) parts.push('in the universe, not ranked yet: ' + esc(arr(c.unranked).join(', ')));
  if (arr(c.starsOff).length) parts.push('starred on this device, not in this ranking: ' + esc(arr(c.starsOff).join(', ')));
  return parts.length ? '<span class="note copynote">Not copied — on the watchlist but ' + parts.join('; ') + '.</span>' : '';
}
/* "#count": rows shown; with the watchlist on and a tier filter set, how many watched names that filter hides. */
function countText(index, state, stars, repo) {
  state = normState(state);
  var shown = filterSortIndex(index, state, stars, repo).length;
  if (!state.watch || state.tier === 'all') return shown + ' shown';
  var all = filterSortIndex(index, Object.assign({}, state, { tier: 'all' }), stars, repo).length;
  return shown + ' shown' + (all > shown ? ' · ' + (all - shown) + ' more watched outside the Tier ' + state.tier + ' filter' : '');
}
function starButtonHTML(t, on, cls) {
  return '<button type="button" class="star' + (on ? ' on' : '') + (cls ? ' ' + cls : '') + '" data-star="' + esc(t) + '" aria-pressed="' + (on ? 'true' : 'false') + '" title="' + (on ? 'Remove the star (this device only)' : 'Star on this device (local, not synced)') + '" aria-label="' + (on ? 'Unstar ' : 'Star ') + esc(t) + '">' + (on ? '★' : '☆') + '</button>';
}
function copyButtonHTML() {
  return '<button type="button" id="copywl" class="wbtn sm" title="Copy the tickers the Watchlist count describes (repo + starred names ranked here) as a comma-separated list; watchlist names with no page are listed separately">Copy tickers</button><span id="copyout" class="copyout" role="status" aria-live="polite"></span>';
}
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
function filterSortIndex(index, state, stars, repo) {
  state = normState(state); stars = normStars(stars); repo = normStars(repo);
  var q = state.q.trim().toLowerCase();
  var rows = arr(index).map(function (r, i) { return { r: obj(r), i: i }; }).filter(function (x) {
    // the Watchlist toggle is a view, not another AND-filter: on, it shows every watched name whatever the Modeled / misfit
    // filter says (a starred misfit must appear); the tier filter and the search still apply
    var r = x.r, okT = state.tier === 'all' || rowTier(r) === state.tier, okF = state.watch || state.fit === 'all' || (r.fit || 'modeled') === state.fit;
    var okW = !state.watch || isWatched(r, stars, repo);
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
function starHTML(row, stars, repo) { // repo rows get the fixed repo star (drawn differently - the file is the source of truth); every other row a per-device toggle
  var t = String(obj(row).ticker || '');
  if (isRepo(row, repo)) return '<span class="star fixed repo" role="img" aria-label="On the repo watchlist" title="On the repo watchlist (_system/watchlist.json)">★</span>';
  return starButtonHTML(t, isStarred(row, stars));
}
/* The ranking row's shareholder yield: index.json's shareholder_yield_label (≥ / ≤ / ≈ when a cash-flow leg is partial),
   never the bare shareholder_yield — a row without the label (an older index) shows nothing rather than an unmarked bound. */
function rowYieldHTML(row) {
  row = obj(row); var lab = typeof row.shareholder_yield_label === 'string' ? row.shareholder_yield_label : '';
  if (!lab || lab === '—') return '';
  var b = row.shareholder_yield_bound, partial = typeof b === 'string' && b !== 'exact';
  var title = 'Shareholder yield (dividends + buybacks − share issuance, TTM, ÷ market cap)' + (partial ? ' — ' + (BOUND_WORDS[b] || b) + ': a cash-flow leg is partial; the Dividends tab names it' : '');
  return '<span class="syld' + (partial ? ' bounded' : '') + '" title="' + esc(title) + '">Shareholder yield <b class="mono">' + esc(lab) + '</b></span> · ';
}
function renderRowHTML(row, stars, repo) {
  row = obj(row);
  var t = row.ticker || '', tier = rowTier(row), scoredTier = row.tier || '?', sp = obj(row.second_pass), badges = [];
  if (sp.verdict === 'changed') badges.push('<span class="bdg p2">↺ pass 2: ' + esc(sp.prior_tier) + ' → ' + esc(scoredTier) + '</span>');
  else if (Object.keys(sp).length) badges.push('<span class="bdg p2">✓ pass 2</span>');
  arr(row.overrides).forEach(function (o) { if (o && typeof o === 'object' && o.field) badges.push('<span class="bdg ov">' + esc(o.field) + ': ' + (o.kind === 'estimate' ? 'AI estimate' : 'filing override') + '</span>'); });
  if (row.tier_override || (row.tier_by_numbers && row.tier && row.tier !== row.tier_by_numbers)) badges.push('<span class="bdg to">tier ' + esc(row.tier_by_numbers) + '→' + esc(row.tier) + ' by judgment</span>');
  if (row.fit === 'misfit') badges.push('<span class="bdg mf">sector misfit</span>');
  var fl = arr(row.flags), live = num(row.irr_live) !== null, liveFloor = live && row.irr_at_floor_live === true, scoredFloor = row.irr_at_floor === true;
  var liveFloorT = 'The live IRR solver stopped at its floor: the figure is a bound (at most about the terminal growth rate), not a solved return', scoredFloorT = 'The scored IRR solver stopped at its floor: the figure is a bound (at most about the terminal growth rate), not a solved return';
  if (liveFloor) badges.push('<span class="bdg mf" title="' + liveFloorT + '">live IRR at floor</span>');
  if (scoredFloor) badges.push('<span class="bdg mf" title="' + scoredFloorT + '">' + (live ? 'scored IRR at floor' : 'IRR at floor') + '</span>');
  if (row.irr_capped) badges.push('<span class="bdg mf">IRR capped</span>');
  // row.split_restated (build_site): the run's price / IV columns are restated for a split since scoring
  var srs = obj(row.split_restated), srf = num(srs.factor);
  if (srf !== null && srf > 0 && Math.abs(srf - 1) > 1e-9) badges.push('<span class="bdg sp" title="' + esc('A ' + (srs.split || fmtFactor(srf) + 'x') + ' split since scoring: the price and IV columns are the run restated to today\'s share units (÷ ' + fmtFactor(srf) + '); IRR, tier and upside are unchanged') + '">' + esc(srs.split || fmtFactor(srf) + 'x') + ' split since scoring</span>');
  // row.live_withheld: live.json predates the scored analysis, or the record is never repriced (an acquired-IPR&D charge
  // deducted by hand, or left unresolved by the latest run, or a latest run not scored yet — the record's live_withheld.reason says which), so the row is ranked on its scored IRR (the live fields are null)
  var pending = !live && row.live_withheld === true, pendingT = 'Live figures pending: the live repricing on file predates the scored analysis, or the record is not repriced (an acquired-IPR&D charge deducted by hand or left unresolved, or a latest engine run not scored yet; its page says which), so this row is ranked on its scored IRR';
  var tb = (live && row.tier_bear_live) || row.tier_bear, tu = (live && row.tier_bull_live) || row.tier_bull;
  var band = tb && tu ? '<span class="band" title="' + (live ? 'bear → bull tier at the last close' : 'bear → bull tier as scored') + '"><i style="background:' + (TIER_ACCENT[tb] || '#333') + '">' + esc(tb) + '</i>→<i style="background:' + (TIER_ACCENT[tu] || '#333') + '">' + esc(tu) + '</i></span>' : '—';
  var up = live ? num(row.upside15_live) : num(row.upside15), price = live && num(row.price_live) !== null ? row.price_live : row.price;
  var cap = live && num(row.market_cap_b_live) !== null ? row.market_cap_b_live : row.market_cap_b, r1 = num(row.ret_1y_pct), moat = num(row.moat);
  var tierCell = '<span class="tbadge" style="background:' + (TIER_ACCENT[tier] || '#333') + '" title="' + (live ? 'Live tier at the last close' : 'Scored tier') + '">' + esc(tier) + '</span>' + (live && tier !== scoredTier ? '<span class="was">was ' + esc(scoredTier) + '</span>' : '');
  return '<tr data-ticker="' + esc(t) + '" data-tier="' + esc(tier) + '" data-fit="' + esc(row.fit || 'modeled') + '"' + (isWatched(row, stars, repo) ? ' data-watch="1"' : '') + '>'
    + '<td class="co"><div class="corow">' + starHTML(row, stars, repo) + '<a href="#' + esc(t) + '"><b class="mono">' + esc(t) + '</b><span class="nm">' + esc(row.name) + '</span></a></div><span class="sub">' + esc(row.sector) + '</span></td>'
    + '<td>' + tierCell + '</td><td class="num">' + band + '</td>'
    + '<td class="num mono strong' + (liveFloor ? ' atfloor' : '') + '">' + (live ? fmtPct(row.irr_live) + (liveFloor ? ' ' + floorSup(liveFloorT) : '') : pending ? '<span class="sub lvpend" title="' + esc(pendingT) + '">live pending</span>' : '<span class="sub">—</span>') + '</td>'
    + '<td class="num mono' + (live ? ' muted' : ' strong') + (scoredFloor ? ' atfloor' : '') + '">' + fmtPct(row.irr) + (scoredFloor ? ' ' + floorSup(scoredFloorT) : '') + '</td>'
    + '<td class="num mono"' + (row.price_date ? ' title="' + esc(row.price_date) + '"' : pending ? ' title="scored price — live figures pending"' : '') + '>' + fmtMoney(price) + '</td>'
    + '<td class="num mono">' + fmtMoney(row.iv15) + '</td>'
    + '<td class="num mono ' + signCls(up) + '">' + (up !== null ? fmtPts(up, 0) : '—') + '</td>'
    + '<td class="num mono">' + (moat !== null ? moat.toFixed(0) + '/10' : '—') + '</td>'
    + '<td>' + esc(row.confidence) + (row.confidence_capped ? '<span class="sub"> capped</span>' : '') + '</td>'
    + '<td class="num mono">' + fmtCap(cap) + '</td>'
    + '<td class="num mono ' + signCls(r1) + '">' + (r1 !== null ? fmtPts(r1, 0) : '—') + '</td>'
    + '<td class="take">' + badges.join('') + '<span>' + esc(row.one_liner) + '</span><span class="sub">' + rowYieldHTML(row) + (fl.length ? '⚠ ' + fl.length + ' flags · ' : '') + esc(row.analysis_date) + ' · <a href="#' + esc(t) + '" class="more">details ›</a></span></td></tr>';
}
function renderListRowsHTML(index, state, stars, repo) {
  var rows = filterSortIndex(index, state, stars, repo);
  if (!arr(index).length) return '<tr><td colspan="13">No companies analyzed yet.</td></tr>';
  if (!rows.length) return '<tr><td colspan="13" class="note">' + (normState(state).watch ? 'Nothing on the watchlist matches these filters.' : 'Nothing matches these filters.') + '</td></tr>';
  return rows.map(function (r) { return renderRowHTML(r, stars, repo); }).join('');
}
function fitDim(state) { return normState(state).watch ? ' dim' : ''; } // the Modeled / misfit segment is ignored while the Watchlist is on
function watchCount(index, stars, repo) { return arr(index).filter(function (r) { return isWatched(r, stars, repo); }).length; }
function watchButtonHTML(index, state, stars, repo) {
  var n = watchCount(index, stars, repo), on = normState(state).watch;
  return '<button type="button" id="watchbtn" class="wbtn' + (on ? ' on' : '') + '" aria-pressed="' + on + '" title="Show every name on the repo watchlist (_system/watchlist.json) that is ranked here, plus the names starred on this device — whatever the Modeled / Sector misfits filter says; the tier filter and the search still apply. The count is the rows shown with the tier filter on All.">★ Watchlist <span class="mono">' + n + '</span></button>';
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
  var repo = repoList(meta, index);
  var sweep = obj(meta.sweep), counts = obj(meta.counts), tiers = obj(counts.tiers);
  var done = num(sweep.done) || 0, total = num(sweep.total) || 0, pct = total ? done / total * 100 : 0;
  var misfits = num(counts.misfits) !== null ? num(counts.misfits) : index.filter(function (r) { return obj(r).fit === 'misfit'; }).length;
  var withLive = num(counts.with_live) !== null ? num(counts.with_live) : index.filter(function (r) { return num(obj(r).irr_live) !== null; }).length;
  var pendingN = num(counts.live_withheld) !== null ? num(counts.live_withheld) : index.filter(function (r) { return obj(r).live_withheld === true; }).length;
  var tierChips = 'SABCDF'.split('').map(function (t) { return '<span class="tchip" style="--c:' + TIER_ACCENT[t] + '"><i>' + t + '</i>' + (num(tiers[t]) !== null ? num(tiers[t]) : index.filter(function (r) { return obj(r).tier === t; }).length) + '</span>'; }).join('');
  var notes = arr(meta.notes).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
  var seg = function (id, items, cur, attr, extra, title) { return '<div class="seg' + (extra || '') + '" id="' + id + '" role="group"' + (title ? ' title="' + esc(title) + '"' : '') + '>' + items.map(function (it) { return '<button type="button" data-' + attr + '="' + esc(it[0]) + '" class="' + (it[0] === cur ? 'on' : '') + '" aria-pressed="' + (it[0] === cur) + '">' + it[1] + '</button>'; }).join('') + '</div>'; };
  var sortSel = '<select id="sort" aria-label="Sort">' + SORTS.map(function (s) { return '<option value="' + s[0] + '"' + (s[0] === state.sort ? ' selected' : '') + '>Sort: ' + s[1] + '</option>'; }).join('') + '</select>';
  var ths = COLS.map(function (c) { var sortable = SORTS.some(function (s) { return s[0] === c[2]; }); return '<th class="' + c[1] + (sortable ? ' sortable' : '') + (sortable && state.sort === c[2] ? ' sorted' : '') + '"' + (sortable ? ' data-sort="' + c[2] + '" title="Sort by ' + esc(c[0]) + '"' : (c[2] ? ' title="' + esc(c[2]) + '"' : '')) + '>' + c[0] + '</th>'; }).join('');
  var colgroup = '<colgroup>' + COLS.map(function (c, i) { return '<col class="c' + (i + 1) + '" style="width:' + c[3] + '%">'; }).join('') + '</colgroup>';
  return '<div id="listView">'
    + '<header class="lhead"><div><h1>Owner\'s-Earnings DCF Ranking</h1><div class="note">' + esc(meta.date) + ' · ' + commas(done) + ' of ' + commas(total) + ' companies under $40B analyzed (' + pct.toFixed(1) + '%) · ranked by probability-weighted expected return at the last close (' + withLive + ' of ' + index.length + ' repriced live' + (pendingN ? ', ' + pendingN + ' pending a close after scoring' : '') + '; the rest at their scored price) · tap a company for its page</div>'
    + '<div class="prog" role="progressbar" aria-valuenow="' + pct.toFixed(1) + '" aria-valuemin="0" aria-valuemax="100"><div style="width:' + pct.toFixed(2) + '%"></div></div></div>'
    + '<div class="tchips">' + tierChips + '<span class="tchip"><i style="background:#3A4252">MF</i>' + misfits + ' sector misfits</span></div></header>'
    + '<div id="notice" class="notice" role="status" aria-live="polite"></div>'
    + '<details class="howto"><summary>How to read this</summary><p>Each company gets a five-scenario owner\'s-earnings DCF (super bear / bear / base / bull / super bull, each with an assigned likelihood); growth fades over a moat-driven competitive advantage period. <b>Live IRR</b> is the probability-weighted expected annual return with the scored cash-flow paths repriced at the last close; <b>Scored IRR</b> is the agent\'s verdict-date figure at the price it used. The <b>band</b> is the bear-case → bull-case tier. <b>IV</b> is the probability-weighted intrinsic value per share at a 15% discount rate; <b>Upside</b> is IV vs price. Tiers: S ≥25% · A 20–25% · B 15–20% (clears the 15% hurdle) · C 10–15% · D &lt;10% · F no positive owner\'s earnings. Banks, insurers, REITs and utilities fit the owner\'s-earnings model poorly and are marked <b>sector misfit</b> — their tiers are soft. Screening-grade standardized DCF — read the Analysis tab before acting.</p>' + (notes ? '<ul class="warnlist">' + notes + '</ul>' : '') + '</details>'
    + '<div class="controls">' + seg('tierseg', [['all', 'All'], ['S', 'S'], ['A', 'A'], ['B', 'B'], ['C', 'C'], ['D', 'D'], ['F', 'F']], state.tier, 'f') + watchButtonHTML(index, state, stars, repo) + copyButtonHTML() + seg('fitseg', [['modeled', 'Modeled'], ['misfit', 'Sector misfits'], ['all', 'All']], state.fit, 'fit', fitDim(state), state.watch ? 'Ignored while the Watchlist is on' : '') + sortSel
    + '<input id="q" type="search" placeholder="Search ticker / name / sector…" aria-label="Search" value="' + esc(state.q) + '"><span class="note" id="count">' + esc(countText(index, state, stars, repo)) + '</span></div>'
    + '<div class="twrap"><table id="t">' + colgroup + '<thead><tr>' + ths + '</tr></thead><tbody>' + renderListRowsHTML(index, state, stars, repo) + '</tbody></table></div>'
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
    w: arr(pr.weekly), d: arr(pr.daily_1y), src: pr.source || null, asof: pr.as_of || null,
    intraday: pr.intraday && typeof pr.intraday === 'object' && !Array.isArray(pr.intraday) ? pr.intraday : null, sessions: arr(pr.sessions_5d) };
}

/* ---- price chart ranges (pure). 1D = prices.intraday.bars (x = minutes since midnight ET, 4:00 AM – 8:00 PM window),
   5D = prices.sessions_5d laid out session by session with a visual gap, 1M · YTD · 3M · 6M · 1Y = daily closes
   (weekly when the record carries no daily series — the attachment trims daily_1y), 5Y · MAX = weekly closes.
   Daily / weekly windows use prices.py's own reference dates (30 · 91 · 182 · 365 · 1826 days back, YTD = Dec 31) and
   start at the close AT OR BEFORE that date — the period return's base — so the pill agrees with prices.stats.ret_*_pct;
   only when nothing precedes the window (MAX, a trimmed series) is the first close the base.
   selectRange() returns {kind, pts: [{t, v, label, sl}], domain, ticks, shade, seps, base, last, after, ...} with t in the
   range's own x unit (minutes, virtual minutes, or ms epoch), `sl` the point's short crosshair tokens, `last` the value the
   period return ends on (the regular-session close on a finished 1D / 5D session, else the last print) and `after` the
   after-hours print measured against that close, or null when that range's data is missing ("not captured yet"). */
var PRICE_RANGES = ['1D', '5D', '1M', 'YTD', '3M', '6M', '1Y', '5Y', 'MAX'];
var SESS_START = 240, SESS_END = 1200, SESS_GAP = 90, REG_OPEN = 570, REG_CLOSE = 960, SESS_LAST_BAR = 1195; // minutes since midnight ET
var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
function isoParts(s) {
  var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(s || '')); if (!m) return null;
  var ms = Date.UTC(+m[1], +m[2] - 1, +m[3]);
  return { y: +m[1], m: +m[2] - 1, d: +m[3], ms: ms, dow: new Date(ms).getUTCDay(), iso: m[0] };
}
/* The one "captured to" time a live 1D card prints (the footer and the source note): the session's last print
   (intraday.last_time, "10:11") when prices.py recorded it, else the last bar's key. The bars are end-keyed 5-minute
   buckets, so the last bar's key (10:15) can run up to four minutes past the last print. */
function capturedTo(iday, bars) {
  var t = hhmm(obj(iday).last_time, null);
  if (t === null) { var b = arr(bars).length ? bars : cleanBars(obj(iday).bars); t = b.length ? b[b.length - 1][0] : null; }
  return t === null ? '' : timeLabel(t) + ' ET';
}
function hhmm(s, dflt) { var m = /^(\d{1,2}):(\d{2})/.exec(String(s || '')); return m ? +m[1] * 60 + +m[2] : dflt; }
function timeLabel(min, short) { // 570 → "9:30 AM"; short → "10 am", "12 pm"
  min = Math.round(min); var h = Math.floor(min / 60) % 24, mm = min % 60, ap = h >= 12 ? 'PM' : 'AM', h12 = h % 12 || 12;
  return short ? h12 + ' ' + ap.toLowerCase() : h12 + ':' + (mm < 10 ? '0' : '') + mm + ' ' + ap;
}
function dayLabel(p, style) { // p from isoParts: long "Tue Oct 14, 2026" · dow "Tue Oct 14" · short "Tue 14" · md "Oct 14"
  if (!p) return '';
  if (style === 'short') return DOW[p.dow] + ' ' + p.d;
  if (style === 'md') return MON[p.m] + ' ' + p.d;
  return DOW[p.dow] + ' ' + MON[p.m] + ' ' + p.d + (style === 'long' ? ', ' + p.y : '');
}
function cleanBars(x) { return arr(x).filter(function (b) { return Array.isArray(b) && num(b[0]) !== null && num(b[1]) !== null; }).map(function (b) { return [num(b[0]), num(b[1])]; }); }
/* A session's bars in time order, one per minute key, with the OFFICIAL regular-session close (prices.py `close`, the
   filed daily close) placed at the 16:00 key when the capture reached the close — a bar keyed 960 is the 15:56–16:00
   bucket (end-keyed) or the 16:00–16:04 bucket (legacy start-keyed, after-hours prints included), so the filed close
   replaces it; a session whose bars stop before 16:00 is left alone (a point at 16:00 would draw a line across hours
   that were not captured). Both bar keyings are drawn as-is (x = key). */
function sessionBars(bars, close, regClose) {
  var b = cleanBars(bars).sort(function (p, q) { return p[0] - q[0]; }), out = [];
  b.forEach(function (x) { if (out.length && out[out.length - 1][0] === x[0]) out[out.length - 1] = x; else out.push(x); });
  close = num(close); regClose = regClose === undefined ? REG_CLOSE : regClose;
  if (close !== null && out.length && out[out.length - 1][0] >= regClose) {
    var at = -1; for (var i = 0; i < out.length; i++) { if (out[i][0] === regClose) at = i; if (out[i][0] >= regClose) break; }
    if (at >= 0) out[at] = [regClose, close];
    else { var k = 0; while (k < out.length && out[k][0] < regClose) k++; out.splice(k, 0, [regClose, close]); }
  }
  return out;
}
/* complete: the block's own boolean when it carries one, else derived from the last bar (≥ 19:55 ET) like prices.py does. */
function sessionComplete(block, bars) { var c = obj(block).complete; if (typeof c === 'boolean') return c; return bars.length ? bars[bars.length - 1][0] >= SESS_LAST_BAR : false; }
function closeSeries(x) { // [[iso, close]] → [{iso, ms, v, p}] sorted ascending, bad rows dropped
  return arr(x).map(function (r) { var p = Array.isArray(r) ? isoParts(r[0]) : null, v = Array.isArray(r) ? num(r[1]) : null; return p && v !== null ? { iso: p.iso, ms: p.ms, v: v, p: p } : null; })
    .filter(Boolean).sort(function (a, b) { return a.ms - b.ms; });
}
function periodReturn(base, last) { base = num(base); last = num(last); return base !== null && last !== null && base > 0 ? (last / base - 1) * 100 : null; }
function fmtRange(pct) { pct = num(pct); return pct === null ? '' : fmtPts(pct, Math.abs(pct) >= 100 ? 0 : Math.abs(pct) >= 10 ? 1 : 2); }
function xScale(t, t0, t1, L, plotW) { return L + plotW * ((t - t0) / Math.max(1, t1 - t0)); }
function minuteToX(min, domain, L, plotW) { return xScale(min, domain[0], domain[1], L, plotW); } // the 1D mapping
function nearestIndex(xs, x) { // index of the closest value in an ascending array (binary search); -1 when empty
  var n = arr(xs).length; if (!n) return -1;
  if (x <= xs[0]) return 0; if (x >= xs[n - 1]) return n - 1;
  var lo = 0, hi = n - 1;
  while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (xs[mid] <= x) lo = mid; else hi = mid; }
  return x - xs[lo] <= xs[hi] - x ? lo : hi;
}
var RANGE_DAYS = { '1M': 30, '3M': 91, '6M': 182, '1Y': 365, '5Y': 1826 }; // prices.py stats(): the same reference dates, so the pill and stats.ret_*_pct agree
function selectRange(spec, range) {
  spec = obj(spec); range = String(range || '').toUpperCase();
  if (PRICE_RANGES.indexOf(range) < 0) return null;
  var iday = spec.intraday && typeof spec.intraday === 'object' && !Array.isArray(spec.intraday) ? spec.intraday : null;
  var open = hhmm(iday && iday.regular_open, REG_OPEN), close = hhmm(iday && iday.regular_close, REG_CLOSE), SPAN = SESS_END - SESS_START;
  if (range === '1D') {
    if (!iday) return null;
    var b = sessionBars(iday.bars, iday.close, close); if (b.length < 2) return null;
    var p1 = isoParts(iday.session_date), dl = p1 ? dayLabel(p1, 'long') : String(iday.session_date || ''), pc = num(iday.prev_close), done = sessionComplete(iday, b);
    var dom = [Math.min(SESS_START, b[0][0]), Math.max(SESS_END, b[b.length - 1][0])];
    var dS = p1 ? dayLabel(p1, 'short') : '';
    var pts1 = b.map(function (x) { return { t: x[0], v: x[1], label: timeLabel(x[0]) + ' ET' + (dl ? ' · ' + dl : ''), sl: dS ? [timeLabel(x[0]), dS] : [timeLabel(x[0]) + ' ET'] }; });
    var ticks1 = [[360, '6 am', 1], [480, '8 am', 1], [600, '10 am', 0], [720, '12 pm', 0], [840, '2 pm', 0], [960, '4 pm', 0], [1080, '6 pm', 1]].filter(function (t) { return t[0] >= dom[0] && t[0] <= dom[1]; });
    var end1 = sessionEnd(b, num(iday.close), close);
    return { range: '1D', kind: 'intraday', pts: pts1, domain: dom, ticks: ticks1, shade: [[dom[0], open], [close, dom[1]]], seps: [], prevClose: pc,
      base: pc !== null ? pc : pts1[0].v, baseLabel: pc !== null ? 'prev close' : null, from: timeLabel(b[0][0]) + ' ET', to: done ? timeLabel(b[b.length - 1][0]) + ' ET' : capturedTo(iday, b), date: p1 ? p1.iso : (iday.session_date || null), sessions: [],
      complete: done, partial: done ? 0 : 1, close: num(iday.close), last: end1.last, lastAt: end1.lastAt, after: end1.after };
  }
  if (range === '5D') {
    var ss = arr(spec.sessions).filter(function (x) { return x && typeof x === 'object' && !Array.isArray(x); })
      .map(function (x) { var bb = sessionBars(x.bars, x.close, close); return { date: x.session_date || null, p: isoParts(x.session_date), pc: num(x.prev_close), bars: bb, complete: sessionComplete(x, bb), close: num(x.close) }; })
      .filter(function (x) { return x.bars.length; })
      .sort(function (a, b) { var da = String(a.date || ''), db = String(b.date || ''); return da < db ? -1 : da > db ? 1 : 0; }) // oldest first whatever order the file carries (the base is the oldest session's prev close)
      .slice(-5);
    var pts5 = [], ticks5 = [], shade5 = [], seps5 = [], sessions = [], partial = 0;
    ss.forEach(function (sx, i) {
      var x0 = i * (SPAN + SESS_GAP), lab = sx.p ? dayLabel(sx.p, 'dow') : String(sx.date || ''), labS = sx.p ? dayLabel(sx.p, 'short') : lab, dlab = sx.p ? dayLabel(sx.p, 'long') : String(sx.date || '');
      sx.bars.forEach(function (bar, j) { var m = Math.max(SESS_START, Math.min(SESS_END, bar[0])); pts5.push({ t: x0 + m - SESS_START, v: bar[1], label: timeLabel(bar[0]) + ' ET' + (dlab ? ' · ' + dlab : '') + (sx.complete ? '' : ' (partial capture)'), sl: [labS, timeLabel(bar[0]) + (sx.complete ? '' : ' (partial)')], brk: j === 0 && i > 0 }); });
      ticks5.push([x0 + SPAN / 2, lab, 0, labS]);
      shade5.push([x0, x0 + open - SESS_START], [x0 + close - SESS_START, x0 + SPAN]);
      if (i) seps5.push(x0 - SESS_GAP / 2);
      if (!sx.complete) partial++;
      sessions.push({ date: sx.date, x0: x0, x1: x0 + SPAN, prevClose: sx.pc, n: sx.bars.length, complete: sx.complete, close: sx.close });
    });
    if (!ss.length || pts5.length < 2) return null;
    var pc0 = ss[0].pc, sl5 = ss[ss.length - 1], end5 = sessionEnd(sl5.bars, sl5.close, close), dow5 = sl5.p ? dayLabel(sl5.p, 'dow') : String(sl5.date || '');
    return { range: '5D', kind: 'sessions', pts: pts5, domain: [0, ss.length * SPAN + (ss.length - 1) * SESS_GAP], ticks: ticks5, shade: shade5, seps: seps5, prevClose: null,
      base: pc0 !== null ? pc0 : pts5[0].v, baseLabel: pc0 !== null ? 'close before ' + (ss[0].p ? ss[0].p.iso : ss[0].date) : null, from: (ss[0].p ? dayLabel(ss[0].p, 'dow') : String(ss[0].date || '')) + ' ' + timeLabel(ss[0].bars[0][0]),
      to: dow5 + ' ' + timeLabel(sl5.bars[sl5.bars.length - 1][0]) + ' ET', sessions: sessions,
      complete: partial === 0, partial: partial, close: null, last: end5.last, lastAt: end5.lastAt ? dow5 + ' ' + end5.lastAt : null, after: end5.after };
  }
  var dly = closeSeries(spec.d), wk = closeSeries(spec.w), longR = range === '5Y' || range === 'MAX';
  var pool = longR ? (wk.length >= 2 ? wk : dly) : (dly.length >= 2 ? dly : wk);
  if (pool.length < 2) return null;
  var last = pool[pool.length - 1], cut;
  if (range === 'MAX') cut = -Infinity;
  else if (range === 'YTD') cut = Date.UTC(last.p.y - 1, 11, 31); // prices.py: the close at or before Dec 31 of the prior year
  else cut = last.ms - RANGE_DAYS[range] * 864e5;
  // the base row = the close at or before the cut (prices.py's _close_at_or_before rule); it opens the window so the
  // line starts where the return is measured from. Nothing at or before the cut → the first close is the base.
  var bi = -1; for (var ri = 0; ri < pool.length; ri++) { if (pool[ri].ms <= cut) bi = ri; else break; }
  var rows = pool.slice(Math.max(bi, 0));
  if (rows.length < 2) return null;
  var pts = rows.map(function (r) { return { t: r.ms, v: r.v, label: dayLabel(r.p, 'long'), sl: [dayLabel(r.p, 'long')], iso: r.iso }; }), ticks = [], seen = {};
  var tr = bi >= 0 ? rows.slice(1) : rows; // the base row never carries a tick (no "Dec" on YTD)
  if (range === '1M') {
    tr.forEach(function (r) { if (r.p.dow === 1) ticks.push([r.ms, dayLabel(r.p, 'md'), 0]); });
    if (ticks.length < 2) { ticks = []; tr.forEach(function (r) { ticks.push([r.ms, dayLabel(r.p, 'md'), 0]); }); }
  } else if (!longR) tr.forEach(function (r) { var k = r.p.y + '-' + r.p.m; if (seen[k]) return; seen[k] = 1; ticks.push([r.ms, MON[r.p.m] + (r.p.m === 0 ? " '" + String(r.p.y).slice(2) : ''), 0]); });
  else tr.forEach(function (r) { if (seen[r.p.y]) return; seen[r.p.y] = 1; ticks.push([r.ms, String(r.p.y), 0]); });
  return { range: range, kind: pool === dly ? 'daily' : 'weekly', pts: pts, domain: [pts[0].t, pts[pts.length - 1].t], ticks: ticks, shade: [], seps: [], prevClose: null,
    base: pts[0].v, baseLabel: null, baseDate: pts[0].iso, priorBase: bi >= 0, from: pts[0].iso, to: pts[pts.length - 1].iso, sessions: [], complete: true, partial: 0, close: null,
    last: pts[pts.length - 1].v, lastAt: null, after: null };
}
/* Where a session's period return ends: the official close (the point sessionBars placed at the regular-close key) when
   the session carries one and its bars reach that key — then the after-hours print, if any, is reported separately
   against that close; otherwise (live session, no close yet) the last print. */
function sessionEnd(bars, close, regClose) {
  var n = bars.length, lastBar = n ? bars[n - 1] : null;
  if (!n) return { last: null, lastAt: null, after: null };
  close = num(close); regClose = regClose === undefined ? REG_CLOSE : regClose;
  var at = -1; for (var i = 0; i < n; i++) if (bars[i][0] === regClose) { at = i; break; }
  if (close === null || at < 0) return { last: lastBar[1], lastAt: null, after: null };
  var after = lastBar[0] > regClose ? { t: lastBar[0], v: lastBar[1], label: timeLabel(lastBar[0]) + ' ET', pct: periodReturn(bars[at][1], lastBar[1]) } : null;
  return { last: bars[at][1], lastAt: timeLabel(regClose) + ' ET close', after: after };
}
function priceRanges(spec) { var o = {}; PRICE_RANGES.forEach(function (r) { o[r] = selectRange(spec, r) !== null; }); return o; }
/* 1Y when a daily series exists, else 5Y, else the first range that has data; null without any. */
function defaultRange(spec) {
  var a = priceRanges(spec);
  if (a['1Y'] && closeSeries(obj(spec).d).length >= 2) return '1Y';
  if (a['5Y']) return '5Y';
  for (var i = 0; i < PRICE_RANGES.length; i++) if (a[PRICE_RANGES[i]]) return PRICE_RANGES[i];
  return null;
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
    out['fin-cf'] = { labels: labels, yfmt: 'big', height: 220, series: [{ name: 'Operating CF', color: C_OCF, kind: 'bar', values: col(ann, 'ocf') }, { name: 'Capex (PP&E)', color: C_CAPEX, kind: 'bar', values: col(ann, 'capex', neg) }].concat(ann.some(function (r) { return intangCapex(r) !== null; }) ? [{ name: 'Intangible capex', color: C_INTANG, kind: 'bar', values: ann.map(function (r) { var x = intangCapex(r); return x === null ? null : -x; }) }] : []).concat([{ name: 'SBC', color: C_SBC, kind: 'bar', values: col(ann, 'sbc', neg) }, { name: "Owner's earnings", color: C_OE, kind: 'line', values: col(ann, 'oe_conservative') }]) };
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
  // the bars and ticks print the block's DPS unit (divCurrency: INR 40.00, not $40.00 — verifier round 2)
  out['div-dps'] = { labels: ann.map(function (r) { return 'FY' + r.fy; }), yfmt: 'dps', cur: divCurrency(record.fundamentals).cur, height: 220, series: [{ name: 'Dividend per share', color: C_FCF, kind: 'bar', values: ann.map(function (r) { return num(r.dps); }), tips: tips }] };
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
  if (!arr(paths.weighted).length) { // Tier F / no stored paths: the filed history alone, no forecast
    var H0 = oeHistory(record);
    if (H0.some(function (h) { return h.v !== null; })) out['fc-oe'] = { labels: H0.map(function (h) { return h.fy; }), yfmt: 'money', height: 240, zero: true, xlabel: 'Fiscal year',
      series: [{ name: 'Filed OE / share', color: C_OE, kind: 'line', width: 2.5, values: H0.map(function (h) { return h.v === null ? null : Math.round(h.v * 1e4) / 1e4; }) }] };
    return out;
  }
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
    out['fc-oe'] = { labels: J.labels, yfmt: 'money', height: 280, zero: true, xlabel: 'Fiscal year → projection', dividerAt: J.baseIndex,
      yFloor: oeAxisFloor(J.histVals, [].concat(J.weighted, J.bear, J.bull, J.super_bear, J.super_bull)), series: [
      { name: 'Super bear → super bull', color: '#7AA2FF', kind: 'band', values: J.super_bull.map(r4), lows: J.super_bear.map(r4) },
      { name: J.filedCount ? 'Filed OE / share' : 'Filed OE / share (no year has both figures filed)', color: C_OE, kind: 'line', width: 2.5, values: J.histVals.map(r4) },
      { name: 'Bear', color: SCN_COLORS.bear, kind: 'line', dash: true, width: 1.5, nodots: true, values: J.bear.map(r4) },
      { name: 'Bull', color: SCN_COLORS.bull, kind: 'line', dash: true, width: 1.5, nodots: true, values: J.bull.map(r4) },
      { name: 'Probability-weighted', color: SCN_COLORS.weighted, kind: 'line', dash: true, width: 3, values: J.weighted.map(r4), tips: tipsW }] };
    var gVals = [], gErr = [], gCol = [], gTips = [];
    for (var m = 0; m < J.labels.length; m++) {
      if (m <= J.baseIndex) { gVals.push(r5(J.histGrowth[m])); gErr.push(null); gCol.push(C_OE); gTips.push(J.histGrowthWhy[m] || 'filed, year over year'); }
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
  // the Overview's compact Street card: the last six months of buy / hold / sell counts as a small stacked chart
  var hs = hist.slice(-6).filter(function (r) { return streetCounts(r).total > 0; });
  if (hs.length >= 2) out['street-sum'] = { labels: hs.map(function (r) { return monthYear(String(r.date || '')); }), yfmt: 'num', height: 120, stacked: true, series: [
    { name: 'Buy', color: '#5BD69C', kind: 'bar', values: hs.map(function (r) { return num(r.buy); }) }, { name: 'Hold', color: '#fbbf24', kind: 'bar', values: hs.map(function (r) { return num(r.hold); }) }, { name: 'Sell', color: '#FF8A8A', kind: 'bar', values: hs.map(function (r) { return num(r.sell); }) }] };
  var annH = epsAnnualHist(record).slice(-10), fa = arr(obj(st.eps_forecast).annual).filter(function (r) { return r && typeof r === 'object'; }).slice(0, 4);
  if (fa.length) {
    var H = annH.length, labels = annH.map(function (h) { return 'FY' + h.fy; }).concat(fa.map(function (f) { return String(f.period); }));
    var joinAt = H ? annH[H - 1].v : null;
    var pad = function (f) { var o = []; for (var i = 0; i < H - 1; i++) o.push(null); if (H) o.push(joinAt); fa.forEach(function (x) { o.push(r4(f(x))); }); return o; };
    var filed = annH.map(function (h) { return r4(h.v); }); while (filed.length < labels.length) filed.push(null);
    out['street-eps'] = { labels: labels, yfmt: 'money', height: 240, zero: true, dividerAt: H - 1, series: [
      { name: 'Low → high estimate', color: '#7AA2FF', kind: 'band', values: pad(function (x) { return x.high; }), lows: pad(function (x) { return x.low; }) },
      { name: 'Filed diluted EPS' + (annH.some(function (h) { return h.split; }) ? ' (split-adjusted)' : ''), color: C_OE, kind: 'line', width: 2.5, values: filed },
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
/* Every chart the company page mounts: the record's specs plus the statements sparkline when the cached statements state
   is ready with a line open — so a re-mount (back to the ranking and return, Overview → Financials later in the session)
   draws the open line's chart instead of "No data." */
function companyCharts(record, stm) {
  var out = chartSpecs(record); stm = stmNorm(stm);
  var sp = stm.status === 'ready' && stm.line ? stmSparkSpec(stm.data, stm.statement, stm.period, stm.line) : null;
  if (sp) out['stm-spark'] = sp;
  return out;
}
/* Focus restoration: the statements viewer and the star buttons redraw their markup, which drops keyboard focus to <body>.
   focusKey(el) names the control (a selector) so it can be re-found and focused after the redraw; pure, node-tested. */
function cssq(s) { return String(s === null || s === undefined ? '' : s).replace(/["\\]/g, '\\$&'); }
function focusKey(el) {
  if (!el) return null;
  var ds = el.dataset || {}, cl = el.classList, has = function (c) { return !!(cl && cl.contains && cl.contains(c)); };
  if (ds.line !== undefined && has('stl')) return 'button.stl[data-line="' + cssq(ds.line) + '"]';
  if (ds.stm !== undefined) return '.stmseg button[data-stm="' + cssq(ds.stm) + '"]';
  if (ds.stp !== undefined) return '.stpseg button[data-stp="' + cssq(ds.stp) + '"]';
  if (has('stm-growth')) return '.stm-growth';
  if (has('stm-close')) return '.stm-close';
  if (ds.star !== undefined && has('star')) return 'button.star[data-star="' + cssq(ds.star) + '"]';
  if (el.id === 'watchbtn') return '#watchbtn';
  return null;
}

/* ------------------------------------------------------------ 6. DOM: charts, mount, route, data */
function fmtBigJs(v) { var a = Math.abs(v), s = v < 0 ? '-' : ''; if (a >= 1e12) return s + '$' + (a / 1e12).toFixed(2) + 'T'; if (a >= 1e9) return s + '$' + (a / 1e9).toFixed(a >= 1e10 ? 0 : 1) + 'B'; if (a >= 1e6) return s + '$' + (a / 1e6).toFixed(0) + 'M'; if (a >= 1e3) return s + '$' + (a / 1e3).toFixed(0) + 'K'; return s + '$' + a.toFixed(2); }
var FMT = { big: fmtBigJs, pct: function (v) { return (v * 100).toFixed(Math.abs(v) >= 0.995 ? 0 : 1) + '%'; }, money: function (v) { return (v < 0 ? '-' : '') + '$' + (Math.abs(v) >= 100 ? Math.abs(v).toFixed(0) : Math.abs(v) >= 10 ? Math.abs(v).toFixed(1) : Math.abs(v).toFixed(2)); }, num: function (v) { return v.toLocaleString(); },
  dps: fmtDps, cnt: function (v) { return fmtCnt(v); } }; // dps: filed precision (dividend chart); cnt: share counts (statement sparklines)
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
  if ('cur' in spec && spec.cur !== 'USD' && (fmt === FMT.dps || fmt === FMT.big)) { var fmt0 = fmt; fmt = function (v) { return curText(fmt0(v), spec.cur); }; } // spec.cur: the amounts' currency (null: unrecorded)
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
  // spec.yFloor: the axis stops there (rounded down to a grid step); a value below it is drawn at the floor with a ▼ marker
  var floored = isNum(spec.yFloor) && lo < spec.yFloor && spec.yFloor < hi;
  var ax = nice(floored ? spec.yFloor : lo, hi, 4), clip = floored ? ax.lo : null, offScale = false;
  var Yraw = function (v) { return T + (H - T - B) * (1 - (v - ax.lo) / (ax.hi - ax.lo)); }, Y = function (v) { return Yraw(clip !== null && v < clip ? clip : v); };
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
    pts.forEach(function (p) {
      if (clip !== null && p[2] < clip) { offScale = true; s += '<path class="offscale" d="M' + (p[0] - 5).toFixed(1) + ',' + (p[1] - 7).toFixed(1) + ' L' + (p[0] + 5).toFixed(1) + ',' + (p[1] - 7).toFixed(1) + ' L' + p[0].toFixed(1) + ',' + (p[1] + 1).toFixed(1) + 'Z" fill="' + sr.color + '"><title>' + tip(sr, p[3], p[2]) + ' (below the axis floor)</title></path>'; return; }
      if (!sr.nodots) s += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="' + (n > 20 ? 2 : 3) + '" fill="' + sr.color + '"><title>' + tip(sr, p[3], p[2]) + '</title></circle>';
    });
  });
  var maxLab = Math.max.apply(null, [0].concat(labels.map(function (lb) { return String(lb).length; }))), every = Math.ceil(n / Math.max(2, Math.floor((W - L - R) / Math.max(58, maxLab * 6.8 + 10)))); // long labels ("Q1 FY2012 · Sep '11") get more room
  labels.forEach(function (lb, i) { if (i % every !== 0 && i !== n - 1) return; s += '<text x="' + X(i).toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(lb) + '</text>'; });
  s += '</svg>';
  var legItem = function (x) { return '<span>' + (x.kind === 'err' ? '<i class="lerr" style="border-color:' + x.color + '"></i>' : x.kind === 'band' ? '<i style="background:' + x.color + ';opacity:.35"></i>' : x.dash ? '<i class="ldash" style="border-color:' + x.color + '"></i>' : '<i style="background:' + x.color + '"></i>') + esc(x.name) + '</span>'; };
  var leg = series.map(legItem).concat(arr(spec.legendExtra).map(legItem)).join('') + (offScale ? '<span class="offleg">▼ below the axis floor — hover for the value</span>' : '');
  if (spec.stacked && arr(spec.totals).length) leg += '<span><i style="background:transparent;border:1px solid #ECEEF2"></i>' + esc(spec.totalName || 'Total') + '</span>';
  el.innerHTML = s + '<div class="leg">' + leg + (spec.xlabel ? '<span style="margin-left:auto">' + esc(spec.xlabel) + '</span>' : '') + '</div>';
}

/* Price chart. opts = {range, showIv, showBand, showH}. 1D / 5D: the axis is tight to the session(s), pre-market
   and after-hours are shaded, 1D draws the previous close as a dashed line, the valuation overlays are hidden.
   Every other range: closes with the weighted IV@15 line, the scenario band and the hurdle prices. The line and
   area colour follow the sign of the period return (last ÷ base − 1; base = the previous close on 1D, the close
   before the oldest session on 5D, else the close at or before the window's reference date (the first drawn point);
   last = the regular-session close on a finished 1D / 5D session — the after-hours print is reported separately —
   else the last print). Writes the drawn geometry to el._pcGeom for the crosshair (crosshairShow) and returns
   {text, cls, pct, range, kind, from, to, n, geom, after, last}; null without data. */
function priceTag(v) { return v >= 1000 ? v.toFixed(0) : v.toFixed(v >= 100 ? 1 : 2); }
function drawPrice(el, d, opts) {
  opts = obj(opts); d = d && typeof d === 'object' ? d : null;
  var showIv = opts.showIv !== false, showBand = opts.showBand !== false, showH = !!opts.showH;
  var fail = function () { el.innerHTML = '<p class="note">No price history.</p>'; el._pcGeom = null; return null; };
  if (!d) return fail();
  var range = String(opts.range || '').toUpperCase(); range = { '3Y': '5Y', '10Y': 'MAX' }[range] || range; // v6.0 range names
  var sel = selectRange(d, range);
  if (!sel) { range = defaultRange(d); sel = range ? selectRange(d, range) : null; }
  if (!sel) return fail();
  var intra = sel.kind === 'intraday' || sel.kind === 'sessions', pts = sel.pts, n = pts.length;
  var W = Math.max(el.clientWidth || 600, 280), H = el.clientHeight || 260, L = W < 480 ? 44 : 56, R = 58, T = 14, B = 26, PW = W - L - R;
  var vals = pts.map(function (p) { return p.v; }), lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
  if (intra) { if (sel.prevClose !== null) { lo = Math.min(lo, sel.prevClose); hi = Math.max(hi, sel.prevClose); } }
  else {
    var over = []; if (showIv && d.iv15) over.push(d.iv15); if (showBand && d.lo && d.hi) over.push(d.lo, d.hi); if (showH) { if (d.h20) over.push(d.h20); if (d.h25) over.push(d.h25); }
    var cap = hi * 3; over.forEach(function (v) { if (v <= cap) { lo = Math.min(lo, v); hi = Math.max(hi, v); } });
  }
  var padV = (hi - lo) * 0.06 || Math.abs(hi) * 0.005 || 1; lo = Math.max(0, lo - padV); hi = hi + padV;
  var ax = nice(lo, hi, 4), Y = function (v) { return T + (H - T - B) * (1 - (v - ax.lo) / (ax.hi - ax.lo)); };
  var X = function (t) { return xScale(t, sel.domain[0], sel.domain[1], L, PW); };
  var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + (intra ? 'Intraday price' : 'Price history against the engine\'s values') + '">', afmt = axisFmt(FMT.money, ax.step);
  arr(sel.shade).forEach(function (sh) { // extended hours, behind everything
    var x0 = X(Math.max(sh[0], sel.domain[0])), x1 = X(Math.min(sh[1], sel.domain[1])); if (x1 - x0 < 0.5) return;
    s += '<rect class="ext" x="' + x0.toFixed(1) + '" y="' + T + '" width="' + (x1 - x0).toFixed(1) + '" height="' + (H - T - B) + '" fill="rgba(255,255,255,.045)"><title>Extended hours</title></rect>';
  });
  for (var v = ax.lo; v <= ax.hi + ax.step / 1e6; v += ax.step) { var y = Y(v); if (y < T - 1 || y > H - B + 1) continue; s += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '"/><text x="' + (L - 6) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + esc(afmt(v)) + '</text>'; }
  if (!intra && showBand && d.lo && d.hi) { var y1 = Y(Math.min(d.hi, ax.hi)), y2 = Y(Math.max(d.lo, ax.lo)); s += '<rect x="' + L + '" y="' + Math.min(y1, y2).toFixed(1) + '" width="' + (W - L - R) + '" height="' + Math.abs(y2 - y1).toFixed(1) + '" fill="rgba(122,162,255,.14)" stroke="rgba(122,162,255,.45)"><title>Scenario range at 15%: ' + esc(FMT.money(d.lo)) + ' – ' + esc(FMT.money(d.hi)) + '</title></rect>'; }
  var endV = sel.last !== null && sel.last !== undefined ? sel.last : vals[n - 1];
  var ret = periodReturn(sel.base, endV), up = ret !== null ? ret >= 0 : endV >= vals[0], col = up ? '#5BD69C' : '#FF8A8A';
  var xs = [], ys = [], segs = [], seg = null;
  pts.forEach(function (p) { var x = X(p.t), yv = Y(p.v); xs.push(x); ys.push(yv); if (!seg || p.brk) { seg = []; segs.push(seg); } seg.push([x, yv]); });
  var floorY = Y(ax.lo).toFixed(1);
  segs.forEach(function (sg) { // one path per session so 5D breaks across the gaps
    var path = ''; sg.forEach(function (q, i) { path += (i ? ' L' : 'M') + q[0].toFixed(1) + ',' + q[1].toFixed(1); });
    if (sg.length > 1) s += '<path d="' + path + ' L' + sg[sg.length - 1][0].toFixed(1) + ',' + floorY + ' L' + sg[0][0].toFixed(1) + ',' + floorY + 'Z" fill="' + col + '" opacity=".12"/>';
    s += '<path d="' + path + '" fill="none" stroke="' + col + '" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>';
  });
  arr(sel.seps).forEach(function (sx) { var x = X(sx).toFixed(1); s += '<line class="sep" x1="' + x + '" x2="' + x + '" y1="' + T + '" y2="' + (H - B) + '" stroke="#3A4252" stroke-dasharray="3 3"/>'; });
  var tag = function (yy, label, color) { return '<rect x="' + (W - R + 3) + '" y="' + (yy - 9).toFixed(1) + '" width="' + (R - 5) + '" height="18" rx="4" fill="' + color + '"/><text x="' + (W - R + (R - 5) / 2 + 3) + '" y="' + (yy + 4).toFixed(1) + '" text-anchor="middle" style="fill:#0C0E12;font-weight:600">' + esc(label) + '</text>'; };
  var line = function (vv, label, color, dash, title) { if (!vv || vv > ax.hi || vv < ax.lo) return; var yy = Y(vv); s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + yy.toFixed(1) + '" y2="' + yy.toFixed(1) + '" stroke="' + color + '" stroke-width="1.5" stroke-dasharray="' + dash + '"><title>' + esc(title) + ': ' + esc(FMT.money(vv)) + '</title></line>' + tag(yy, label, color); };
  if (intra) {
    if (sel.prevClose !== null) { var yp = Y(sel.prevClose); if (yp >= T && yp <= H - B) s += '<line class="pcl" x1="' + L + '" x2="' + (W - R) + '" y1="' + yp.toFixed(1) + '" y2="' + yp.toFixed(1) + '" stroke="#A0A8B6" stroke-width="1" stroke-dasharray="4 4"><title>Previous close: ' + esc(FMT.money(sel.prevClose)) + '</title></line><text class="pct" x="' + (L + 6) + '" y="' + (yp - 4).toFixed(1) + '" text-anchor="start">Prev close ' + esc(fmtMoney(sel.prevClose)) + '</text>'; }
  } else {
    if (showH) { line(d.h20, '20%', '#B79CFF', '2 3', 'Price for a 20% return (Tier A)'); line(d.h25, '25%', '#B79CFF', '2 3', 'Price for a 25% return (Tier S)'); }
    if (showIv && d.iv15) line(d.iv15, 'IV', '#C9D4FF', '6 4', 'Weighted IV @15%');
  }
  var lastC = vals[n - 1], yl = ys[n - 1];
  s += '<circle cx="' + xs[n - 1].toFixed(1) + '" cy="' + yl.toFixed(1) + '" r="4" fill="' + col + '"><title>' + esc(pts[n - 1].label) + ': ' + esc(FMT.money(lastC)) + '</title></circle>' + tag(yl, priceTag(lastC), col);
  if (!intra && d.iv15 && d.iv15 > ax.hi) s += '<text x="' + (L + 6) + '" y="' + (T + 12) + '" style="fill:#C9D4FF">▲ IV@15% ' + esc(FMT.money(d.iv15)) + ' above chart</text>';
  var wide = PW >= 520, lastX = -1e9; // x labels: minor ticks only when wide, never closer than 48px, short session labels when narrow
  arr(sel.ticks).forEach(function (t) { if (t[2] && !wide) return; var x = X(t[0]); if (x < L + 6 || x > W - R - 6 || x - lastX < 48) return; lastX = x; s += '<text class="xt" x="' + x.toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(!wide && t[3] ? t[3] : t[1]) + '</text>'; });
  // crosshair, hidden until a pointer or the arrow keys move it (crosshairShow positions the parts)
  s += '<g class="xh" style="display:none" aria-hidden="true"><line class="xv" x1="0" x2="0" y1="' + T + '" y2="' + (H - B) + '" stroke="#A0A8B6" stroke-dasharray="3 3"/><line class="xhl" x1="' + L + '" x2="' + (W - R) + '" y1="0" y2="0" stroke="#A0A8B6" stroke-dasharray="3 3"/>'
    + '<circle class="xd" r="4.5" fill="' + col + '" stroke="#0C0E12" stroke-width="1.5"/><rect class="xtr" x="' + (W - R + 3) + '" width="' + (R - 5) + '" height="18" rx="4" fill="#ECEEF2"/><text class="xtt" x="' + (W - R + (R - 5) / 2 + 3) + '" text-anchor="middle" style="fill:#0C0E12;font-weight:600"></text>'
    + '<rect class="xlr" y="' + (T - 12) + '" height="18" rx="4" fill="#1B1F27" stroke="#2C323D"/><text class="xlt" y="' + (T + 1) + '" text-anchor="middle" style="fill:#ECEEF2"></text></g>';
  s += '</svg>'; el.innerHTML = s;
  var geom = { W: W, H: H, L: L, R: R, T: T, B: B, xs: xs, ys: ys, pts: pts, col: col, range: range, kind: sel.kind, domain: sel.domain };
  el._pcGeom = geom; el._pcIdx = -1;
  var partial = sel.partial ? (sel.kind === 'intraday' ? ' · partial session (captured to ' + sel.to + ')' : ' · ' + sel.partial + ' of ' + sel.sessions.length + ' sessions partial') : '';
  var after = sel.after ? ' · after-hours ' + fmtMoney(sel.after.v) + ' at ' + sel.after.label + (sel.after.pct !== null ? ' (' + fmtRange(sel.after.pct) + ' vs close)' : '') : '';
  var text = range + ': ' + (ret !== null ? fmtRange(ret) : '—') + ' (' + sel.from + ' → ' + (sel.lastAt || sel.to) + ')' + (sel.baseLabel ? ' · vs ' + sel.baseLabel + ' ' + fmtMoney(sel.base) : '') + after + partial;
  return { text: text, cls: ret === null ? '' : (ret >= 0 ? 'pos' : 'neg'), pct: ret, range: range, kind: sel.kind, from: sel.from, to: sel.to, n: n, geom: geom, partial: sel.partial || 0, after: sel.after || null, last: endV };
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
var D = { app: null, meta: null, index: null, records: {}, pending: {}, charts: {}, state: defaultState(), stars: [], current: null, notice: '', embedded: false,
  statements: {}, stmView: { statement: 'income', period: 'annual', growth: false } };
var STARS_KEY = 'stocks.watchlist', STARS_KEY_OLD = 'oe-dcf.stars.v1'; // JSON array of tickers; the old key is read once and migrated
function $(sel, r) { return (r || document).querySelector(sel); }
function $$(sel, r) { return Array.prototype.slice.call((r || document).querySelectorAll(sel)); }
function setHash(h) { try { if (history.replaceState) history.replaceState(null, '', h); else location.hash = h; } catch (e) { /* sandboxed / file: */ } }
function loadState() {
  try { var raw = localStorage.getItem(STORAGE_KEY); if (raw) D.state = normState(JSON.parse(raw)); } catch (e) { D.state = defaultState(); }
  try { var st = localStorage.getItem(STARS_KEY); D.stars = st ? normStars(JSON.parse(st)) : []; } catch (e2) { D.stars = []; }
  try { var old = localStorage.getItem(STARS_KEY_OLD); if (old) { normStars(JSON.parse(old)).forEach(function (t) { if (D.stars.indexOf(t) < 0) D.stars.push(t); }); localStorage.removeItem(STARS_KEY_OLD); saveStars(); } } catch (e3) { /* no storage */ }
}
function repoNow() { return repoList(D.meta, D.index); }
function saveState() { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(D.state)); } catch (e) { /* private mode */ } }
function saveStars() { try { localStorage.setItem(STARS_KEY, JSON.stringify(D.stars)); } catch (e) { /* private mode */ } }

function drawPriceCard(card) {
  var el = $('.pchart', card); if (!el) return;
  var spec = D.charts.price, cb = function (sel) { var c = $(sel, card); return c ? c.checked : undefined; };
  var res = drawPrice(el, spec, { range: card.dataset.range || defaultRange(spec), showIv: cb('.tg-iv') !== false, showBand: cb('.tg-band') !== false, showH: cb('.tg-h') === true });
  var range = res ? res.range : (card.dataset.range || ''), intra = !!res && (res.kind === 'intraday' || res.kind === 'sessions');
  card.dataset.range = range;
  $$('.ranges button', card).forEach(function (b) { // active state + the period-return badge under the active range
    var on = b.dataset.r === range; b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
    var rb = $('.rb', b); if (rb) { rb.textContent = on && res && res.pct !== null ? fmtRange(res.pct) : ''; rb.className = 'rb' + (on && res && res.cls ? ' ' + res.cls : ''); }
  });
  var ret = $('.pcret', card); if (ret) { ret.textContent = res ? res.text : ''; ret.className = 'pcret ' + (res ? res.cls : ''); }
  var note = $('.pcnote', card); if (note) note.hidden = !intra;
  var tg = $('.toggles', card); if (tg) tg.classList.toggle('dim', intra);
}
/* ---- crosshair (DOM only): the chart's geometry is left on the element by drawPrice; the parts of the hidden
   <g class="xh"> are moved to the nearest point. Listeners are delegated from document (wireEvents), never attached
   per chart, so re-renders leak nothing. */
function crosshairHide(el) { var grp = el && $('.xh', el); if (grp) grp.style.display = 'none'; if (el) el._pcIdx = -1; }
function crosshairShow(el, i) {
  var g = el._pcGeom; if (!g || !g.xs.length) return;
  i = Math.max(0, Math.min(g.xs.length - 1, i));
  var grp = $('.xh', el); if (!grp) return;
  var px = g.xs[i], py = g.ys[i], p = g.pts[i], PW = g.W - g.L - g.R;
  var setA = function (sel, attrs) { var nd = $(sel, grp); if (nd) Object.keys(attrs).forEach(function (k) { nd.setAttribute(k, attrs[k]); }); return nd; };
  setA('.xv', { x1: px.toFixed(1), x2: px.toFixed(1) }); setA('.xhl', { y1: py.toFixed(1), y2: py.toFixed(1) }); setA('.xd', { cx: px.toFixed(1), cy: py.toFixed(1) });
  setA('.xtr', { y: (py - 9).toFixed(1) }); var tt = setA('.xtt', { y: (py + 4).toFixed(1) }); if (tt) tt.textContent = priceTag(p.v);
  // the floating label: the full text when it fits the plot, else the point's short tokens packed into as many lines as the
  // plot width needs (estimated per character, then measured in the browser and re-packed once when the font runs wider)
  var lt = $('.xlt', grp), lr = $('.xlr', grp), lines = crosshairLines(p, PW), lw = labelWidth(lines);
  var place = function () {
    var lx = Math.max(g.L + lw / 2, Math.min(g.W - g.R - lw / 2, px));
    if (lr) { lr.setAttribute('x', (lx - lw / 2).toFixed(1)); lr.setAttribute('width', lw.toFixed(1)); lr.setAttribute('height', String(XL_PAD_Y + XL_LINE * lines.length)); }
    if (lt) { lt.setAttribute('x', lx.toFixed(1)); setLines(lt, lines, lx); }
  };
  place();
  if (lt && typeof lt.getComputedTextLength === 'function') { // real text width: widen the box to it, or re-pack when it overflows the plot
    var measured = 0; try { measured = lt.getComputedTextLength ? measureLines(lt) : 0; } catch (e) { measured = 0; }
    if (measured > 0) {
      var est = Math.max.apply(null, lines.map(function (l) { return l.length; })) * XL_CH, k = measured / Math.max(1, est);
      if (measured + XL_PAD_X > PW && k > 1) { lines = crosshairLines(p, PW, k); lw = Math.min(PW, labelWidth(lines, k)); place(); }
      else { lw = Math.min(PW, measured + XL_PAD_X); place(); }
    }
  }
  grp.style.display = ''; el._pcIdx = i;
}
/* Floating-label text fitting (pure). A point carries its full `label` and short tokens `sl`; the price is the last token.
   crosshairLines(point, plotWidth, scale) → the lines to draw: [full label] when it fits, else the tokens packed greedily
   (' · ' between tokens on a line) so no line exceeds the plot width; a lone token wider than the plot stays whole (clamped).
   Widths are estimated at XL_CH px per character (IBM Plex Mono 11.5 px ≈ 7.0) times `scale`, plus the box padding. */
var XL_CH = 7.1, XL_PAD_X = 14, XL_PAD_Y = 6, XL_LINE = 13;
function estWidth(str, scale) { return String(str).length * XL_CH * (scale || 1); }
function labelWidth(lines, scale) { return Math.max.apply(null, lines.map(function (l) { return estWidth(l, scale); })) + XL_PAD_X; }
function crosshairLines(p, plotW, scale) {
  p = obj(p); var price = fmtMoney(p.v), full = (p.label || '') + ' · ' + price, fits = function (str) { return estWidth(str, scale) + XL_PAD_X <= plotW; };
  if (fits(full)) return [full];
  var sl = arr(p.sl).filter(Boolean).map(String), tokens = (sl.length ? sl : [String(p.label || '')]).filter(Boolean).concat([price]), lines = [], cur = '';
  tokens.forEach(function (tok) { var cand = cur ? cur + ' · ' + tok : tok; if (cur && !fits(cand)) { lines.push(cur); cur = tok; } else cur = cand; });
  if (cur) lines.push(cur);
  return lines.length ? lines : [full];
}
function setLines(textEl, lines, x) { // one <tspan> per line (the first on the text's own baseline, the rest XL_LINE below)
  while (textEl.firstChild) textEl.removeChild(textEl.firstChild);
  if (lines.length === 1 || !textEl.ownerDocument || !textEl.ownerDocument.createElementNS) { textEl.textContent = lines.join(' · '); return; }
  lines.forEach(function (l, i) { var ts = textEl.ownerDocument.createElementNS('http://www.w3.org/2000/svg', 'tspan'); ts.setAttribute('x', x.toFixed(1)); if (i) ts.setAttribute('dy', String(XL_LINE)); ts.textContent = l; textEl.appendChild(ts); });
}
function measureLines(textEl) { // the widest line's rendered width
  var ts = textEl.getElementsByTagName ? textEl.getElementsByTagName('tspan') : [], w = 0;
  if (ts.length) { for (var i = 0; i < ts.length; i++) w = Math.max(w, ts[i].getComputedTextLength()); return w; }
  return textEl.getComputedTextLength();
}
function crosshairAt(el, clientX) { // client x → SVG x → nearest drawn point
  var g = el._pcGeom, svg = $('svg', el); if (!g || !svg || !svg.getBoundingClientRect) return;
  var r = svg.getBoundingClientRect(); if (!r.width) return;
  crosshairShow(el, nearestIndex(g.xs, (clientX - r.left) * g.W / r.width));
}
function chartOf(t) { return t && t.closest ? t.closest('.pchart') : null; }
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
function activeKey(scope) { var ae = document.activeElement; return ae && (!scope || scope.contains(ae)) ? focusKey(ae) : null; }
function restoreFocus(sel, scope) {
  var el = sel ? $(sel, scope || D.app) : null;
  if (el) { try { el.focus({ preventScroll: true }); } catch (e) { try { el.focus(); } catch (e2) { /* ignore */ } } }
  return el;
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
  var repo = repoNow(), keep = activeKey(); // a star or the watch toggle keeps keyboard focus across the redraw
  tb.innerHTML = renderListRowsHTML(D.index, D.state, D.stars, repo);
  var c = $('#count'); if (c) c.textContent = countText(D.index, D.state, D.stars, repo);
  var fs = $('#fitseg'); if (fs) { fs.className = 'seg' + fitDim(D.state); if (D.state.watch) fs.title = 'Ignored while the Watchlist is on'; else fs.removeAttribute('title'); }
  var wb = $('#watchbtn'); if (wb) { wb.outerHTML = watchButtonHTML(D.index, D.state, D.stars, repo); }
  if (keep) restoreFocus(keep);
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
  if (tab === 'financials') ensureStatements(ticker, true); // marks the state loading before the first render; the fetch callback redraws the card
  var stm = stmState(ticker);
  mount(renderCompanyHTML(record, tab, navFor(ticker), sub, { stm: stm, stars: D.stars, repo: repoNow() }), companyCharts(record, stm));
  revealTab($('.page', D.app)); // a deep link to a tab past the strip's edge (#T.analysis on a phone) must show its highlighted button
  watchHeader();
}
/* The tab strip scrolls sideways on a phone (.tabs{overflow-x:auto}); the active tab must be inside the visible part or the
   viewer cannot tell which pane is open. tabScrollLeft (pure) → the scrollLeft that brings the tab into view with TAB_PAD px
   of its neighbour showing, or null when it is already fully visible. strip = {scrollLeft, clientWidth[, scrollWidth]},
   tab = {left, width} in the strip's CONTENT coordinates (0 = the strip's first pixel, scroll included). */
var TAB_PAD = 16;
function tabScrollLeft(strip, tab) {
  strip = obj(strip); tab = obj(tab);
  var sl = num(strip.scrollLeft) || 0, cw = num(strip.clientWidth), sw = num(strip.scrollWidth), l = num(tab.left), w = num(tab.width);
  if (cw === null || cw <= 0 || l === null || w === null) return null;
  var lo = l - TAB_PAD, hi = l + w + TAB_PAD, next = null;
  if (lo < sl) next = lo; else if (hi > sl + cw) next = hi - cw;
  if (next === null) return null;
  if (sw !== null && sw > cw) next = Math.min(next, sw - cw);
  next = Math.max(0, Math.round(next));
  return next === sl ? null : next;
}
function revealTab(page) {
  var strip = $('.tabs', page || D.app), on = strip && $('.tab.on', strip);
  if (!strip || !on || !strip.getBoundingClientRect || !on.getBoundingClientRect) return null;
  var sr = strip.getBoundingClientRect(), tr = on.getBoundingClientRect();
  var next = tabScrollLeft({ scrollLeft: strip.scrollLeft, clientWidth: strip.clientWidth, scrollWidth: strip.scrollWidth }, { left: tr.left - sr.left + strip.scrollLeft, width: tr.width });
  if (next !== null) strip.scrollLeft = next; // a direct assignment: instant (reduced motion needs no opt-out) and it never scrolls the page itself
  return next;
}
/* ---- statements viewer state (DOM): one cache entry per ticker, the view (statement · period · growth) shared across pages */
function stmRaw(ticker) {
  var st = D.statements[ticker];
  if (!st) st = D.statements[ticker] = { ticker: ticker, status: D.embedded ? 'embedded' : 'idle', data: null, error: null, line: null };
  return st;
}
function stmState(ticker) {
  var st = stmRaw(ticker);
  return { status: st.status, data: st.data, error: st.error, line: st.line, statement: D.stmView.statement, period: D.stmView.period, growth: D.stmView.growth, site: obj(D.meta).site_url || '' };
}
function ensureStatements(ticker, quiet) {
  var st = stmRaw(ticker);
  if (st.status === 'error') { st.status = 'idle'; st.error = null; } // a failed fetch (network blip, HTTP 500) is retried when the tab opens again
  if (st.status !== 'idle') return;
  var has = obj(obj(findRow(ticker)).has);
  if (has.statements === false) { st.status = 'missing'; if (!quiet) redrawStatements(); return; } // the index says the builder found no statements.json — no 404 round-trip
  st.status = 'loading'; if (!quiet) redrawStatements();
  fetchJSON('./data/' + encodeURIComponent(ticker) + '.statements.json', function (err, data) {
    if (err || !data || typeof data !== 'object' || Array.isArray(data)) { st.status = err && /HTTP 404/.test(String(err.message)) ? 'missing' : 'error'; st.error = err ? err.message : 'not an object'; }
    else { st.status = 'ready'; st.data = data; }
    if (D.current && D.current.ticker === ticker) redrawStatements();
  });
}
function redrawStatements(focusSel) { // focusSel: the control to focus after the redraw (default: the one that had focus inside the card)
  var sec = $('#stmsec', D.app); if (!sec || !D.current) return;
  var t = D.current.ticker, st = stmState(t), keep = focusSel || activeKey(sec);
  sec.outerHTML = renderStatements(D.records[t] || { ticker: t }, st);
  var spec = st.status === 'ready' && st.line ? stmSparkSpec(st.data, st.statement, st.period, st.line) : null;
  if (spec) D.charts['stm-spark'] = spec; else delete D.charts['stm-spark'];
  var sec2 = $('#stmsec', D.app); if (sec2) { drawVisible(sec2); if (keep) restoreFocus(keep, sec2); }
  return sec2;
}
/* The tab bar condenses (ticker · last close · change · expected return) once the header scrolls away. The condensed line
   overlays the --tabsum-h px above the tabs and the condensed bar sticks that much lower (app.css), so the bar's height never
   changes; condenseNow (pure) switches when the bar's natural top — the hero's bottom plus the bar's top margin — comes
   within that height of the viewport top, where the stuck and the natural positions coincide (no jump either way). */
var TABSUM_H = 36;
function condenseNow(heroBottom, marginTop, sumH) {
  heroBottom = num(heroBottom); if (heroBottom === null) return false;
  return heroBottom + (num(marginTop) || 0) < (num(sumH) !== null ? num(sumH) : TABSUM_H);
}
function watchHeader() {
  var hero = $('.hero', D.app), bar = $('.tabbar', D.app);
  if (!hero || !bar) return;
  var mt = 0, sh = TABSUM_H;
  try { var cs = root.getComputedStyle ? root.getComputedStyle(bar) : null; if (cs) { mt = parseFloat(cs.marginTop) || 0; sh = parseFloat(cs.getPropertyValue('--tabsum-h')) || TABSUM_H; } } catch (e) { /* defaults */ }
  bar.classList.toggle('condensed', condenseNow(hero.getBoundingClientRect().bottom, mt, sh));
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
  revealTab(page); // hashchange to #T.data while on #T, or a tap on a half-visible tab: the strip scrolls so the highlighted tab is in view
  if (sub) showSub(sub); else { setHash(hashFor(D.current.ticker, tab, D.current.sub)); drawVisible(page); }
  if (tab === 'financials') ensureStatements(D.current.ticker); // loads ./data/<T>.statements.json the first time the tab opens
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
/* The canonical form of a company hash — '#T', '#T.tab', '#T.forecast.sub' with the index's ticker casing — for any
   accepted spelling (legacy '#T/tab', odd casing); findTicker(name) returns the index's ticker or null. Null when the
   hash names no company, a bad token or an unknown name. route() rewrites the address bar to it on load. */
function canonicalHash(h, findTicker) {
  var p = parseHash(h);
  if (!p.ticker || p.bad) return null;
  var t = typeof findTicker === 'function' ? findTicker(p.ticker) : p.ticker;
  return t ? hashFor(String(t), p.tab, p.sub) : null;
}
/* Every navigation takes a fresh token FIRST, so a company record still in flight from an earlier hash can never mount
   over what this one shows: back to the ranking (#APP → # while APP loads), an unknown name, or a return to the company
   already open (#KR → #APP → #KR while APP loads). The loading card replaces the open company's page, so D.current is
   cleared with it — a return to that company re-mounts it from the cache instead of leaving "Loading …" on screen. */
function route() {
  if (!D.index) return;
  var token = (D.routeToken = {});
  var p = parseHash(location.hash);
  if (!p.ticker) { if (D.current || !$('#listView', D.app)) mountList(); return; }
  var row = findRow(p.ticker);
  if (!row || p.bad) {
    D.notice = 'No company "' + p.ticker + '" in this ranking — back to the list.';
    setHash('#'); mountList(); return;
  }
  var ticker = row.ticker, canon = hashFor(ticker, p.tab, p.sub);
  if (String(location.hash || '') !== canon) setHash(canon); // legacy '#T/tab' and non-canonical casing → '#T.tab' on load (replaceState: no hashchange, no history entry)
  if (D.current && D.current.ticker === ticker) { if (D.current.tab !== p.tab) showTab(p.tab, p.tab === 'forecast' ? p.sub : null); else if (p.tab === 'forecast' && D.current.sub !== p.sub) showSub(p.sub); return; }
  var cached = D.records[ticker];
  if (!cached) { D.current = null; D.app.innerHTML = '<div class="card loading" role="status">Loading ' + esc(ticker) + '…</div>'; }
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
    var cp = e.target.closest ? e.target.closest('#copywl') : null;
    if (cp) { copyWatchlist(); return; }
    var star = e.target.closest ? e.target.closest('button.star[data-star]') : null;
    if (star) {
      var t = String(star.dataset.star || '').toUpperCase(), k = D.stars.indexOf(t), keep = focusKey(star); if (k >= 0) D.stars.splice(k, 1); else D.stars.push(t); saveStars();
      if ($('#t tbody')) refreshRows();
      else { $$('button.star[data-star]', D.app).forEach(function (b) { if (String(b.dataset.star || '').toUpperCase() === t) b.outerHTML = starButtonHTML(t, D.stars.indexOf(t) >= 0, b.classList.contains('hstar') ? 'hstar' : ''); }); restoreFocus(keep); }
      return;
    }
    // About: "Read more" reveals the rest of the description in place (the text is already in the markup)
    var rm = e.target.closest ? e.target.closest('.readmore') : null;
    if (rm) {
      var para = rm.closest('.dimp'), wasOpen = rm.getAttribute('aria-expanded') === 'true';
      if (para) { $$('.more', para).forEach(function (x) { x.hidden = wasOpen; }); $$('.ell', para).forEach(function (x) { x.hidden = !wasOpen; }); }
      rm.setAttribute('aria-expanded', String(!wasOpen)); rm.textContent = wasOpen ? 'Read more' : 'Show less';
      return;
    }
    // Filings: the form chips hide the rows of the other kinds (no re-render; the rows carry data-kind)
    var fk = e.target.closest ? e.target.closest('.fchips button[data-fk]') : null;
    if (fk && !fk.disabled) {
      var fcd = fk.closest('.fcard'), kind = fk.dataset.fk;
      if (fcd) { fcd.dataset.fk = kind; $$('.fchips button', fcd).forEach(function (b) { var on = b === fk; b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on)); }); $$('tr[data-kind]', fcd).forEach(function (tr) { tr.hidden = kind !== 'all' && tr.dataset.kind !== kind; }); }
      return;
    }
    // statements viewer controls
    var ss = e.target.closest ? e.target.closest('.stmseg button, .stpseg button') : null;
    if (ss && D.current) {
      var sraw = stmRaw(D.current.ticker);
      if (ss.dataset.stm) { D.stmView.statement = ss.dataset.stm; sraw.line = null; }
      else { D.stmView.period = ss.dataset.stp; if (sraw.line && !stmSparkSpec(sraw.data, D.stmView.statement, D.stmView.period, sraw.line)) sraw.line = null; } // the open line has no values in the new periodicity: its row is dropped, so the chart closes with it
      redrawStatements(); return;
    }
    var rt = e.target.closest ? e.target.closest('.stm-retry') : null;
    if (rt && D.current) { var rr = stmRaw(D.current.ticker); rr.status = 'idle'; rr.error = null; ensureStatements(D.current.ticker); restoreFocus('.stmseg button.on'); return; }
    var sl = e.target.closest ? e.target.closest('button.stl[data-line]') : null;
    if (sl && D.current) {
      var raw = stmRaw(D.current.ticker), key = String(sl.dataset.line || ''); raw.line = raw.line === key ? null : key;
      var sec = redrawStatements(), sp = sec && $('#stmspark', sec);
      if (sp && sp.scrollIntoView && root.innerWidth < 760) { try { sp.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e4) { sp.scrollIntoView(); } }
      return;
    }
    var sc = e.target.closest ? e.target.closest('.stm-close') : null;
    if (sc && D.current) { // focus returns to the line whose chart was closed — or, when that row is gone, to the active period button
      var rw = stmRaw(D.current.ticker), closed = rw.line; rw.line = null;
      var sec3 = redrawStatements(closed ? 'button.stl[data-line="' + cssq(closed) + '"]' : null);
      if (sec3 && (!document.activeElement || !sec3.contains(document.activeElement))) restoreFocus('.stpseg button.on', sec3);
      return;
    }
    var rb = e.target.closest ? e.target.closest('.ranges button') : null;
    if (rb) { var card = rb.closest('.pc'); if (card && !rb.disabled && rb.dataset.r) { card.dataset.range = rb.dataset.r; drawPriceCard(card); } return; }
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
    if (e.target.matches('.stm-growth')) { D.stmView.growth = !!e.target.checked; redrawStatements(); return; }
    if (e.target.id === 'sort') { D.state.sort = e.target.value; refreshRows(); }
  });
  document.addEventListener('input', function (e) { if (e.target.id === 'q') { D.state.q = e.target.value; refreshRows(); } });
  // price-chart crosshair: pointer events (.pchart{touch-action:pan-y}: a horizontal drag scrubs, a vertical flick
  // still scrolls the page — the browser then fires pointercancel, which hides the crosshair); a touch crosshair
  // stays after the finger lifts and clears on the next tap elsewhere. Touch/mouse fallbacks only for browsers
  // without PointerEvent.
  var onPoint = function (e) { var el = chartOf(e.target); if (el) { crosshairAt(el, e.clientX); return; } if (e.type === 'pointerdown' || e.type === 'mousedown') $$('.pchart', D.app).forEach(crosshairHide); };
  var onOut = function (e) { var el = chartOf(e.target); if (el && e.pointerType !== 'touch' && !(e.relatedTarget && el.contains(e.relatedTarget))) crosshairHide(el); };
  if (root.PointerEvent) {
    document.addEventListener('pointermove', onPoint); document.addEventListener('pointerdown', onPoint);
    document.addEventListener('pointerout', onOut); document.addEventListener('pointercancel', function (e) { crosshairHide(chartOf(e.target)); });
  } else {
    var onTouch = function (e) { var t = e.touches && e.touches[0], el = t && chartOf(t.target); if (el) crosshairAt(el, t.clientX); };
    document.addEventListener('touchstart', onTouch, { passive: true }); document.addEventListener('touchmove', onTouch, { passive: true });
    document.addEventListener('mousemove', onPoint); document.addEventListener('mousedown', onPoint); document.addEventListener('mouseout', onOut);
  }
  document.addEventListener('keydown', function (e) { // the chart is focusable: ← → Home End move the crosshair, Esc hides it
    var el = e.target && e.target.classList && e.target.classList.contains('pchart') ? e.target : null; if (!el || !el._pcGeom) return;
    var n = el._pcGeom.xs.length, i = typeof el._pcIdx === 'number' && el._pcIdx >= 0 ? el._pcIdx : n - 1, k = e.key;
    if (k === 'ArrowLeft') i -= 1; else if (k === 'ArrowRight') i += 1; else if (k === 'Home') i = 0; else if (k === 'End') i = n - 1; else if (k === 'Escape') { crosshairHide(el); return; } else return;
    e.preventDefault(); crosshairShow(el, i);
  });
  window.addEventListener('hashchange', route);
  var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { drawVisible(D.app); }, 150); });
  window.addEventListener('scroll', onScroll, { passive: true });
}
/* "Copy tickers": exactly the names the "★ Watchlist N" count describes (watchCopy), via navigator.clipboard; the repo names
   with no page here are named in a note beside it, not copied. When the clipboard API is unavailable or refused, a read-only
   field with the text selected so it can be copied by hand. */
function copyWatchlist() {
  var out = $('#copyout'); if (!out) return;
  var c = watchCopy(D.meta, D.index, repoNow(), D.stars), text = c.text, note = copyNoteHTML(c);
  var fallback = function () {
    out.innerHTML = '<input type="text" readonly aria-label="Watchlist tickers" value="' + esc(text) + '"><span class="note">select &amp; copy (' + c.tickers.length + ')</span>' + note;
    var inp = $('input', out); if (inp) { try { inp.focus(); inp.select(); } catch (e) { /* ignore */ } }
  };
  if (!c.tickers.length) { out.innerHTML = '<span>No watched name is ranked here</span>' + note; return; }
  var clip = typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function' ? navigator.clipboard : null;
  if (!clip) { fallback(); return; }
  try { clip.writeText(text).then(function () { out.innerHTML = '<span>Copied ' + c.tickers.length + ' ticker' + (c.tickers.length === 1 ? '' : 's') + '</span>' + note; }, fallback); }
  catch (e) { fallback(); }
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
  repoList: repoList, isRepo: isRepo, isStarred: isStarred, watchTickers: watchTickers, watchCopy: watchCopy, copyNoteHTML: copyNoteHTML, countText: countText, rowYieldHTML: rowYieldHTML, yieldShown: yieldShown, streetParagraph: streetParagraph, starHTML: starHTML, starButtonHTML: starButtonHTML, copyButtonHTML: copyButtonHTML,
  fmtDps: fmtDps, dpsDecimals: dpsDecimals,
  STM_TABS: STM_TABS, STM_PERIODS: STM_PERIODS, stmNorm: stmNorm, stmFmt: stmFmt, companyCharts: companyCharts, focusKey: focusKey, cssq: cssq, minus: minus, stmColumns: stmColumns, stmTable: stmTable, stmSparkSpec: stmSparkSpec, renderStatements: renderStatements, renderStatementsTable: renderStatementsTable, monthYear: monthYear,
  floorFlags: floorFlags, oeHistory: oeHistory, oeForecastSeries: oeForecastSeries, renderForecastDCF: renderForecastDCF, renderForecastStreet: renderForecastStreet, renderForecastAnalysts: renderForecastAnalysts, chartSpecsStreet: chartSpecsStreet, drawFan: drawFan, SUBTABS: SUBTABS, SUB_KEYS: SUB_KEYS, hashFor: hashFor,
  renderCompanyHTML: renderCompanyHTML, renderHeader: renderHeader, renderPriceChart: renderPriceChart, renderOverview: renderOverview, renderFinancials: renderFinancials, renderDividends: renderDividends,
  renderSegments: renderSegments, renderForecast: renderForecast, renderAnalysis: renderAnalysis, renderData: renderData, renderMissingHTML: renderMissingHTML, renderErrorHTML: renderErrorHTML,
  renderAbout: renderAbout, renderPerformance: renderPerformance, financialPerformance: financialPerformance, renderStreet: renderStreet, renderFilings: renderFilings, renderTabSummary: renderTabSummary,
  aboutFacts: aboutFacts, clampText: clampText, ABOUT_CLAMP: ABOUT_CLAMP, streetCardModel: streetCardModel, filingKind: filingKind, filterFilings: filterFilings, FILING_KINDS: FILING_KINDS, canonicalHash: canonicalHash, stmSpan: stmSpan,
  divCurrency: divCurrency,
  chartSpecs: chartSpecs, chartSpecsFinancials: chartSpecsFinancials, chartSpecsDividends: chartSpecsDividends, chartSpecsSegments: chartSpecsSegments, chartSpecsForecast: chartSpecsForecast, priceSpec: priceSpec,
  PRICE_RANGES: PRICE_RANGES, selectRange: selectRange, priceRanges: priceRanges, defaultRange: defaultRange, periodReturn: periodReturn, fmtRange: fmtRange, nearestIndex: nearestIndex, minuteToX: minuteToX, xScale: xScale, timeLabel: timeLabel, dayLabel: dayLabel, isoParts: isoParts, priceTag: priceTag,
  sessionBars: sessionBars, capturedTo: capturedTo, yearAgoQuarter: yearAgoQuarter, oeAxisFloor: oeAxisFloor, oeHistorySection: oeHistorySection, sessionComplete: sessionComplete, cleanBars: cleanBars, sessionEnd: sessionEnd, RANGE_DAYS: RANGE_DAYS,
  crosshairLines: crosshairLines, labelWidth: labelWidth, estWidth: estWidth, XL_CH: XL_CH, XL_PAD_X: XL_PAD_X, XL_PAD_Y: XL_PAD_Y, XL_LINE: XL_LINE,
  condenseNow: condenseNow, TABSUM_H: TABSUM_H, sparkLabels: sparkLabels, oeGapNote: oeGapNote, oeYoyNote: oeYoyNote, histYoy: histYoy, overrideWhy: overrideWhy, isOverrideTag: isOverrideTag, runCapText: runCapText, SHARE_BASIS_X: SHARE_BASIS_X, SHARE_JUMP_X: SHARE_JUMP_X, renderStatementsBody: renderStatementsBody,
  parseHash: parseHash, TABS: TABS, TAB_KEYS: TAB_KEYS, SORTS: SORTS, TIER_ACCENT: TIER_ACCENT, tabScrollLeft: tabScrollLeft, TAB_PAD: TAB_PAD,
  liveWithheld: liveWithheld, pendingText: pendingText, currentClose: currentClose, splitInfo: splitInfo, splitRefs: splitRefs, splitDivisor: splitDivisor, fmtFactor: fmtFactor, splitBrief: splitBrief,
  renderOverrides: renderOverrides, iprdNote: iprdNote, divPriceWords: divPriceWords, oeSplitNote: oeSplitNote, epsAnnualHist: epsAnnualHist, yearAgoQuarterAdj: yearAgoQuarterAdj, RESTRICTED_TITLE: RESTRICTED_TITLE, RESTRICTED_LEGEND: RESTRICTED_LEGEND,
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
