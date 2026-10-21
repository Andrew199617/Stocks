'use strict';
/* Assembles a minimal data/<TICKER>.json record per _system/SITE_CONTRACT.md straight from a
   company folder (score.json, dcf_numbers.json, fundamentals.json, prices.json, live.json,
   segments.json, ttm.json, judgment.json, profile.json, street.json, financials_history.csv,
   analysis.md). Used by the tests only when the data layer has not written
   _daily/site/data/<TICKER>.json yet — a fresh clone, where prices.json / live.json / street.json
   (gitignored Nasdaq caches) are absent too and come through as null. No valuation is computed
   here: forecast.paths / hurdle_prices / sensitivity are taken from the engine's stored values
   when present and left empty otherwise, exactly as the app must cope. Two build_site rules are
   mirrored because they change what the page shows: a live.json older than the scored analysis is
   withheld (liveShown → record.live null, record.live_withheld, row.live_withheld), and a split since
   scoring restates the run's per-share figures and share counts (liveSplit / restateSplit →
   record.split_restated, row.split_restated). */
const fs = require('node:fs');
const path = require('node:path');

function jload(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { return null; } }
function tread(p) { try { return fs.readFileSync(p, 'utf8'); } catch (e) { return null; } }
function coerce(v) {
  if (v === undefined || v === null || v === '') return null;
  if (v === 'True') return true; if (v === 'False') return false;
  const f = Number(v); return isFinite(f) && /^-?\d/.test(v) ? f : v;
}
function parseCsv(text) {
  if (!text) return [];
  const lines = text.split(/\r?\n/).filter((l) => l.length);
  if (!lines.length) return [];
  const head = lines[0].split(',');
  return lines.slice(1).map((l) => { const cells = l.split(','); const r = {}; head.forEach((h, i) => { r[h] = coerce(cells[i]); }); return r; });
}
function n(v) { const f = Number(v); return v === null || v === undefined || v === '' || !isFinite(f) ? null : f; }
function isObj(v) { return !!v && typeof v === 'object' && !Array.isArray(v); }
/* record.profile as build_site.py serves it: profile.json (SEC: about, filings) with street.json's Nasdaq street / market
   blocks on it and street.json's fetched_at as street_fetched_at; a legacy profile.json that still carries street / market
   keeps them when there is no street.json; null when neither file exists. */
function profileOf(dir) {
  const profile = jload(path.join(dir, 'profile.json')), street = jload(path.join(dir, 'street.json'));
  if (!isObj(profile) && !isObj(street)) return null;
  const out = Object.assign({}, isObj(profile) ? profile : {});
  if (isObj(street)) { out.street = isObj(street.street) ? street.street : null; out.market = isObj(street.market) ? street.market : null; out.street_fetched_at = street.fetched_at || null; }
  else { out.street = isObj(out.street) ? out.street : null; out.market = isObj(out.market) ? out.market : null; out.street_fetched_at = null; }
  return out;
}

/* build_site.live_shown: the live.json the page shows as current, and why one was withheld. A live.json without a price or
   a weighted IRR is not shown (live_ok); one whose close (price_date) is older than the later of score.json analysis_date
   and live.scored_date is withheld, and so is one left from an earlier run (live.scored_date before score.analysis_date) — record.live null, record.live_withheld says why, the scored figures are the latest available. */
function date10(v) { return typeof v === 'string' && v.length >= 10 ? v.slice(0, 10) : null; }
/* [Codex review r2 of PR #47] a numbers.iprd_adjustment treatment not_applied_share_count_unverified is never repriced:
   any live.json is withheld, and the record says so without one (reason iprd_share_count_unverified). */
const IPRD_WITHHELD_NOTE = 'The acquired-IPR&D charge was not deducted by the engine (share count unverified): the published tier '
  + "is the main agent's tier_override with a hand deduction that reprice.py cannot replay, so the scored "
  + 'figures are the current ones and no live repricing is shown.';
/* [Codex review r6 of PR #47] build_site.iprd_unresolved: a run make_score refused for an unresolved acquired-IPR&D charge
   (a period awaiting its cash-flow check, or excluded non_usd_no_rate with a positive native expense or cash outflow) —
   withheld the same way, reason iprd_unresolved. */
const IPRD_UNRESOLVED_NOTE = "The latest engine run left an acquired-IPR&D charge unresolved (awaiting the worker's cash-flow check, "
  + 'or in a currency the engine cannot convert), so make_score refused it: the score on file is an earlier '
  + "run's, a live repricing of the new run would carry unadjusted figures, and none is shown until the "
  + 'folder is scored again.';
function iprdUnresolved(blk) {
  const pos = (v) => n(v) !== null && n(v) > 0;
  for (const p of Array.isArray(blk.periods) ? blk.periods : []) {
    if (!isObj(p)) continue;
    if (p.excluded === 'awaiting_cash_flow_check') return true;
    if (p.excluded === 'non_usd_no_rate' && (pos(p.expense_native) || pos(p.cash_native))) return true;
  }
  return blk.treatment === 'awaiting_cash_flow_check' || blk.treatment === 'non_usd_no_rate';
}
function liveShown(score, lv, numbers) {
  const blk = isObj(numbers) && isObj(numbers.iprd_adjustment) ? numbers.iprd_adjustment : {};
  const unresolved = iprdUnresolved(blk);
  if (unresolved || blk.treatment === 'not_applied_share_count_unverified') {
    const ok = isObj(lv) && n(lv.price) !== null && n(lv.irr_weighted) !== null;
    return { live: null, withheld: { reason: unresolved ? 'iprd_unresolved' : 'iprd_share_count_unverified', price: ok ? n(lv.price) : null, price_date: ok ? date10(lv.price_date) : null,
      scored_date: date10((score || {}).analysis_date) || date10((numbers || {}).as_of), method: null, note: unresolved ? IPRD_UNRESOLVED_NOTE : IPRD_WITHHELD_NOTE } };
  }
  if (!isObj(lv) || n(lv.price) === null || n(lv.irr_weighted) === null) return { live: null, withheld: null };
  const sa = date10((score || {}).analysis_date), ls = date10(lv.scored_date), pd = date10(lv.price_date);
  if (sa && ls && ls < sa) return { live: null, withheld: { reason: 'live_from_earlier_run', price: n(lv.price), price_date: pd, scored_date: sa, method: null,
    note: 'The live repricing on file is from the ' + ls + ' run, before the current score (' + sa + '); the scored figures are the latest available.' } };
  const scored = [sa, ls].filter(Boolean);
  const sd = scored.length ? scored.sort()[scored.length - 1] : null;
  if (pd === null || sd === null || pd >= sd) return { live: lv, withheld: null };
  const method = isObj(lv.basis_check) && typeof lv.basis_check.method === 'string' ? lv.basis_check.method : null;
  return { live: null, withheld: { reason: 'live_older_than_score', price: n(lv.price), price_date: pd, scored_date: sd, method,
    note: 'The last close on file (' + pd + ') predates the scored analysis (' + sd + ') — no close after the analysis is on file, '
      + 'so the scored figures are the latest available, as of the ' + pd + ' close.' } };
}
/* build_site.live_split / restate_split: a split since the scored run (live.split_factor, else basis_check.factor) restates
   every per-share run figure (SPLIT_DIVIDE ÷ factor) and the run's share counts (SPLIT_MULTIPLY × factor) in today's share
   units, and records record.split_restated / row.split_restated. `*` = every key of an object / item of a list. */
const RATES = [10, 12, 15, 20, 25], IVK = RATES.map((r) => 'iv_at_' + r);
const SPLIT_DIVIDE = [].concat(
  ['price', 'base_oe_per_share'].concat(IVK).map((k) => 'score.' + k), IVK.map((k) => 'score.scenarios.*.' + k),
  ['score.override_impact.base_oe_without_override', 'score.override_impact.base_oe_with_override', 'score.second_pass.prior_iv_at_15'],
  ['price', 'base_oe_per_share', 'base_oe_latest_per_share', 'base_oe_normalized_per_share'].concat(IVK).map((k) => 'numbers.' + k),
  IVK.map((k) => 'numbers.scenarios.*.' + k), IVK.map((k) => 'numbers.weighted.' + k),
  ['numbers.hurdle_prices.*', 'numbers.inputs.base_oe_ps_arg', 'numbers.override_impact.base_oe_per_share_zero_fill', 'numbers.override_impact.base_oe_per_share_final'],
  ['forecast.paths.*.*', 'forecast.hurdle_prices.*', 'forecast.inputs.base_oe_ps_arg'], RATES.map((r) => 'forecast.sensitivity.*.' + r),
  ['price', 'iv15', 'iv12', 'iv20', 'iv25'].map((k) => 'row.' + k), ['ttm.ttm_oe_per_share']);
const SPLIT_MULTIPLY = ['numbers.shares_diluted_latest', 'history.*.shares_diluted', 'ttm.ttm_shares_diluted'];
function fmtG(f) { return String(Number(Number(f).toPrecision(6))); } // Python's {:g} for a split factor
function liveSplit(lv) {
  if (!isObj(lv)) return { factor: null, label: null };
  const bc = isObj(lv.basis_check) ? lv.basis_check : {};
  let f = n(lv.split_factor); if (f === null) f = n(bc.factor);
  if (f === null || f <= 0 || Math.abs(f - 1) < 1e-9) return { factor: null, label: null };
  return { factor: f, label: typeof bc.split === 'string' && bc.split ? bc.split : fmtG(f) + 'x' };
}
function scalePath(o, parts, factor) { // build_site._scale_path: scale every number at the dotted path in place; how many were scaled
  if (!parts.length) return 0;
  const key = parts[0], rest = parts.slice(1); let cnt = 0;
  if (isObj(o)) {
    (key === '*' ? Object.keys(o) : (key in o ? [key] : [])).forEach((k) => {
      if (rest.length) cnt += scalePath(o[k], rest, factor);
      else if (n(o[k]) !== null) { o[k] = n(o[k]) * factor; cnt++; }
    });
  } else if (Array.isArray(o) && key === '*') {
    o.forEach((v, i) => { if (rest.length) cnt += scalePath(v, rest, factor); else if (n(v) !== null) { o[i] = n(v) * factor; cnt++; } });
  }
  return cnt;
}
function restateSplit(rec, factor, label, lv) { // in place on the record's own deep copy, like build_site.restate_split
  const s = rec.score || {}, fields = [];
  const asScored = { price: n(s.price), iv_at_15: n(s.iv_at_15), base_oe_per_share: n(s.base_oe_per_share) };
  SPLIT_DIVIDE.forEach((p) => { if (scalePath(rec, p.split('.'), 1 / factor)) fields.push(p); });
  SPLIT_MULTIPLY.forEach((p) => { if (scalePath(rec, p.split('.'), factor)) fields.push(p); });
  const scoredDate = typeof lv.scored_date === 'string' ? lv.scored_date : s.analysis_date;
  rec.split_restated = { factor, split: label, scored_date: scoredDate, price_date: typeof lv.price_date === 'string' ? lv.price_date : null, fields, as_scored: asScored,
    note: 'A ' + label + ' split since the scored run (' + scoredDate + '): every per-share figure of the run (prices, intrinsic values, hurdle prices, owner\'s earnings per share, '
      + 'the forecast paths) is divided by ' + fmtG(factor) + ' and its share counts multiplied by ' + fmtG(factor) + ', so they read in today\'s share units next to the last close. '
      + 'IRRs, tiers, upside and market cap do not change.' };
  if (isObj(rec.row)) rec.row.split_restated = { factor, split: label };
  return rec;
}

function assemble(base, ticker) {
  const dir = path.join(base, ticker);
  const score = jload(path.join(dir, 'score.json'));
  const numbers = jload(path.join(dir, 'dcf_numbers.json'));
  if (!score || !numbers) return null;
  const shown = liveShown(score, jload(path.join(dir, 'live.json')), numbers), live = shown.live, split = liveSplit(live), sf = split.factor || 1;
  const fundamentals = jload(path.join(dir, 'fundamentals.json'));
  const prices = jload(path.join(dir, 'prices.json'));
  const segments = jload(path.join(dir, 'segments.json'));
  const ttm = jload(path.join(dir, 'ttm.json'));
  const judgment = jload(path.join(dir, 'judgment.json'));
  const history = parseCsv(tread(path.join(dir, 'financials_history.csv')));
  const scn = numbers.scenarios || {};
  const sens = {};
  Object.keys(scn).forEach((k) => { const r = scn[k] || {}; sens[k] = { 10: n(r.iv_at_10), 12: n(r.iv_at_12), 15: n(r.iv_at_15), 20: n(r.iv_at_20), 25: n(r.iv_at_25), irr: n(r.irr), irr_live: live && live.scenarios && live.scenarios[k] ? n(live.scenarios[k].irr) : null }; });
  if (numbers.weighted) sens.weighted = { 10: n(numbers.weighted.iv_at_10), 12: n(numbers.weighted.iv_at_12), 15: n(numbers.weighted.iv_at_15), 20: n(numbers.weighted.iv_at_20), 25: n(numbers.weighted.iv_at_25), irr: n(numbers.weighted.irr), irr_live: live ? n(live.irr_weighted) : null };
  const numbersOut = Object.assign({}, numbers); delete numbersOut.paths; delete numbersOut.growth_paths;
  const fit = score.model_fit || ((score.fragility_flags || []).some((f) => String(f).startsWith('SECTOR_MODEL_MISMATCH')) ? 'misfit' : 'modeled');
  const liveIrr = live ? n(live.irr_weighted) : null;
  const liveUp = live && n(live.iv_at_15) !== null && n(live.price) ? (n(live.iv_at_15) / n(live.price) - 1) * 100 : null;
  const st = (prices && prices.stats) || {};
  const row = {
    ticker: score.ticker, name: score.name, sector: score.sector, fit,
    tier: score.tier_final || score.tier_by_numbers, tier_by_numbers: score.tier_by_numbers, tier_override: !!(score.tier_by_numbers && score.tier_final && score.tier_final !== score.tier_by_numbers),
    tier_live: live ? live.tier || null : null, tier_bear: score.tier_bear || (live && live.tier_bear) || null, tier_bull: score.tier_bull || (live && live.tier_bull) || null,
    irr: n(score.implied_irr), irr_live: liveIrr, irr_bear: n(score.irr_bear !== undefined ? score.irr_bear : (live && live.irr_bear)), irr_bull: n(score.irr_bull !== undefined ? score.irr_bull : (live && live.irr_bull)),
    irr_at_floor: !!score.irr_at_floor, irr_capped: !!score.irr_capped, f_subtype: score.f_subtype || null,
    price: n(score.price), price_live: live ? n(live.price) : null, price_date: live ? live.price_date || null : null, ret_1y_pct: n(st.ret_1y_pct),
    // live.json's IVs are in today's share units: a fallback goes back to run units (× the split factor) before restateSplit
    iv15: n(score.iv_at_15), iv12: n(score.iv_at_12),
    iv20: n(score.iv_at_20) !== null ? n(score.iv_at_20) : (live && n(live.iv_at_20) !== null ? n(live.iv_at_20) * sf : null),
    iv25: n(score.iv_at_25) !== null ? n(score.iv_at_25) : (live && n(live.iv_at_25) !== null ? n(live.iv_at_25) * sf : null),
    live_withheld: !!shown.withheld, split_restated: null,
    upside15: n(score.upside_at_15_pct), upside15_live: liveUp, market_cap_b: n(score.market_cap_b), market_cap_b_live: live && n(live.market_cap_est) !== null ? n(live.market_cap_est) / 1e9 : null,
    moat: n(score.moat_score), cap_years: n(score.cap_years), confidence: score.confidence, confidence_capped: !!score.confidence_capped,
    one_liner: score.one_liner, analysis_date: score.analysis_date, engine_release: score.engine_release || null,
    flags: score.fragility_flags || [], overrides: (score.overrides || []).map((o) => ({ field: o.field, kind: o.kind })), override_unblocks_tier: !!((score.override_impact || {}).unblocks_tier),
    second_pass: score.second_pass || null, alert_eligible: !!score.alert_eligible, dividend_yield: null, shareholder_yield: null,
    has: { prices: !!prices, fundamentals: !!fundamentals, dividends: !!(fundamentals && fundamentals.dividends), segments: !!segments, live: !!live, analysis: fs.existsSync(path.join(dir, 'analysis.md')), second_pass: fs.existsSync(path.join(dir, 'second_pass.md')) }
  };
  const rec = {
    ticker: score.ticker, name: score.name, sector: score.sector, folder: ticker, built_at: new Date().toISOString(), built_from_mtime: 0,
    row, score, numbers: numbersOut,
    forecast: {
      paths: numbers.paths || {}, growth_paths: numbers.growth_paths || {}, sensitivity: sens,
      hurdle_prices: numbers.hurdle_prices || null, inputs: numbers.inputs || {}, g_base: numbers.g_base, g_blend: numbers.g_blend, g_terminal: numbers.g_terminal, cap_years: numbers.cap_years,
      growth_components: numbers.growth_components || {}, growth_components_adjusted: numbers.growth_components_adjusted || null, share_cagr: numbers.share_cagr, share_count_adj: numbers.share_count_adj, share_adj_basis: numbers.share_adj_basis || null,
      replayed: false
    },
    live, live_withheld: shown.withheld, split_restated: null,
    history, fundamentals, prices: prices ? { source: prices.source, as_of: prices.as_of, stats: prices.stats, weekly: prices.weekly || [], daily_1y: prices.daily_1y || [] } : null,
    segments, ttm, judgment, profile: profileOf(dir), registry: [],
    analysis_md: tread(path.join(dir, 'analysis.md')), second_pass_md: tread(path.join(dir, 'second_pass.md')),
    files: fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => !f.startsWith('.')).sort() : []
  };
  // a deep copy first (build_site's finite() copy): forecast.inputs / hurdle_prices share objects with numbers here, and a
  // restatement must divide each path once
  const out = JSON.parse(JSON.stringify(rec));
  return split.factor ? restateSplit(out, split.factor, split.label, live) : out;
}

module.exports = { assemble, parseCsv, profileOf, liveShown, liveSplit, restateSplit, SPLIT_DIVIDE, SPLIT_MULTIPLY };
