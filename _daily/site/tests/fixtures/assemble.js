'use strict';
/* Assembles a minimal data/<TICKER>.json record per _system/SITE_CONTRACT.md straight from a
   company folder (score.json, dcf_numbers.json, fundamentals.json, prices.json, live.json,
   segments.json, ttm.json, judgment.json, financials_history.csv, analysis.md). Used by the
   tests only when the data layer has not written _daily/site/data/<TICKER>.json yet. No
   valuation is computed here: forecast.paths / hurdle_prices / sensitivity are taken from the
   engine's stored values when present and left empty otherwise, exactly as the app must cope. */
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

function assemble(base, ticker) {
  const dir = path.join(base, ticker);
  const score = jload(path.join(dir, 'score.json'));
  const numbers = jload(path.join(dir, 'dcf_numbers.json'));
  if (!score || !numbers) return null;
  const live = jload(path.join(dir, 'live.json'));
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
    iv15: n(score.iv_at_15), iv12: n(score.iv_at_12), iv20: n(score.iv_at_20 !== undefined ? score.iv_at_20 : (live && live.iv_at_20)), iv25: n(score.iv_at_25 !== undefined ? score.iv_at_25 : (live && live.iv_at_25)),
    upside15: n(score.upside_at_15_pct), upside15_live: liveUp, market_cap_b: n(score.market_cap_b), market_cap_b_live: live && n(live.market_cap_est) !== null ? n(live.market_cap_est) / 1e9 : null,
    moat: n(score.moat_score), cap_years: n(score.cap_years), confidence: score.confidence, confidence_capped: !!score.confidence_capped,
    one_liner: score.one_liner, analysis_date: score.analysis_date, engine_release: score.engine_release || null,
    flags: score.fragility_flags || [], overrides: (score.overrides || []).map((o) => ({ field: o.field, kind: o.kind })), override_unblocks_tier: !!((score.override_impact || {}).unblocks_tier),
    second_pass: score.second_pass || null, alert_eligible: !!score.alert_eligible, dividend_yield: null, shareholder_yield: null,
    has: { prices: !!prices, fundamentals: !!fundamentals, dividends: !!(fundamentals && fundamentals.dividends), segments: !!segments, live: !!live, analysis: fs.existsSync(path.join(dir, 'analysis.md')), second_pass: fs.existsSync(path.join(dir, 'second_pass.md')) }
  };
  return {
    ticker: score.ticker, name: score.name, sector: score.sector, folder: ticker, built_at: new Date().toISOString(), built_from_mtime: 0,
    row, score, numbers: numbersOut,
    forecast: {
      paths: numbers.paths || {}, growth_paths: numbers.growth_paths || {}, sensitivity: sens,
      hurdle_prices: numbers.hurdle_prices || null, inputs: numbers.inputs || {}, g_base: numbers.g_base, g_blend: numbers.g_blend, g_terminal: numbers.g_terminal, cap_years: numbers.cap_years,
      growth_components: numbers.growth_components || {}, growth_components_adjusted: numbers.growth_components_adjusted || null, share_cagr: numbers.share_cagr, share_count_adj: numbers.share_count_adj, share_adj_basis: numbers.share_adj_basis || null,
      replayed: false
    },
    live, history, fundamentals, prices: prices ? { source: prices.source, as_of: prices.as_of, stats: prices.stats, weekly: prices.weekly || [], daily_1y: prices.daily_1y || [] } : null,
    segments, ttm, judgment, registry: [],
    analysis_md: tread(path.join(dir, 'analysis.md')), second_pass_md: tread(path.join(dir, 'second_pass.md')),
    files: fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => !f.startsWith('.')).sort() : []
  };
}

module.exports = { assemble, parseCsv };
