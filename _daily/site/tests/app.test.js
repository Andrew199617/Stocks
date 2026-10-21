'use strict';
/* Tests for _daily/site/app.js. Run: node _daily/site/tests/app.test.js (zero dependencies).
   Loads app.js via require (the module.exports branch), the real data/<T>.json records for
   APP, KR and AEE when the data layer has written them (else a fixture assembled from the
   company folders), and the synthetic fixture that carries dividends, segments and live.
   build_site.py's output (data/, index.json, meta.json) is a gitignored cache that a fresh clone
   does not have: every check that reads it falls back to the committed company files or skips
   with a printed note, and the fixtures always run. To run the suite as a fresh clone would,
   without touching the real cache: APP_TEST_BUILT=<an empty dir> node _daily/site/tests/app.test.js
   (APP_TEST_BASE=<dir> also moves the company folders, e.g. a copy holding only committed files). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SITE = path.resolve(__dirname, '..');
const BASE = process.env.APP_TEST_BASE ? path.resolve(process.env.APP_TEST_BASE) : path.resolve(SITE, '..', '..');
const BUILT = process.env.APP_TEST_BUILT ? path.resolve(process.env.APP_TEST_BUILT) : SITE; // where data/, index.json, meta.json are read
const HAVE_BUILT = fs.existsSync(path.join(BUILT, 'data')) && fs.existsSync(path.join(BUILT, 'index.json')) && fs.existsSync(path.join(BUILT, 'meta.json'));
const App = require(path.join(SITE, 'app.js'));
const { assemble } = require('./fixtures/assemble.js');

const results = [], pending = [], skipped = [];
function test(name, fn) { // fn may return a promise (the router tests wait on deferred fetches); the summary waits for every one
  try {
    const r = fn();
    if (r && typeof r.then === 'function') { pending.push(Promise.resolve(r).then(() => { results.push([name, null]); }, (e) => { results.push([name, e]); })); return; }
    results.push([name, null]);
  } catch (e) { results.push([name, e]); }
}
function skip(what) { if (skipped.indexOf(what) < 0) { skipped.push(what); console.log('  (skipped: ' + what + ')'); } } // a real-data check with nothing to read
/* A company's statements file: the served copy when the data layer wrote it, else the committed <T>/statements.json it is copied from. */
function statementsPath(t) {
  const served = path.join(BUILT, 'data', t + '.statements.json');
  if (fs.existsSync(served)) return served;
  const own = path.join(BASE, t, 'statements.json');
  return fs.existsSync(own) ? own : null;
}
function loadRecord(t) {
  const p = path.join(BUILT, 'data', t + '.json');
  if (fs.existsSync(p)) return { record: JSON.parse(fs.readFileSync(p, 'utf8')), source: 'data/' + t + '.json' };
  const r = assemble(BASE, t);
  return r ? { record: r, source: 'assembled from ' + t + '/' } : null;
}
function inject(v) { // append a raw-HTML marker to every string in a record
  if (typeof v === 'string') return v + '<x-inj>';
  if (Array.isArray(v)) return v.map(inject);
  if (v && typeof v === 'object') { const o = {}; Object.keys(v).forEach((k) => { o[k] = inject(v[k]); }); return o; }
  return v;
}
function fakeEl(w, h) { return { clientWidth: w || 600, clientHeight: h || 260, innerHTML: '' }; }
function tabOrder(html) { const re = /data-pane="([a-z]+)"/g, out = []; let m; while ((m = re.exec(html))) out.push(m[1]); return out; }
const synthetic = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'synthetic.json'), 'utf8'));
const metaPath = path.join(BUILT, 'meta.json'), indexPath = path.join(BUILT, 'index.json');
const meta = fs.existsSync(metaPath) ? JSON.parse(fs.readFileSync(metaPath, 'utf8')) : { date: '2026-10-14', sweep: { done: 3, total: 2617 }, counts: { tiers: { S: 0, A: 0, B: 1, C: 1, D: 0, F: 1 }, misfits: 1, with_live: 2 }, hurdles: { S: 0.25, A: 0.2, B: 0.15, C: 0.1 }, notes: [], stale: [] };
const loaded = {};
['APP', 'KR', 'AEE', 'HBAN', 'ZS', 'EXPE'].forEach((t) => { const r = loadRecord(t); if (r) loaded[t] = r; });
/* The records build_site.py wrote (data/<T>.json). A check that pins what the build adds to a real record — the engine's
   replayed paths, live floor flags, profile.street — reads only these; an assembled stand-in skips it with a note. */
const built = {}; Object.keys(loaded).forEach((t) => { if (loaded[t].source.startsWith('data/')) built[t] = loaded[t].record; });
function builtOr(t, what) { if (built[t]) return built[t]; skip(what + ' — needs the built data/' + t + '.json'); return null; }
const index = fs.existsSync(indexPath) ? JSON.parse(fs.readFileSync(indexPath, 'utf8')) : Object.keys(loaded).map((t) => loaded[t].record.row);

/* ---- helpers */
test('fmt helpers: null / negative / 1e12 edge cases', () => {
  assert.equal(App.fmtMoney(null), '—'); assert.equal(App.fmtMoney(undefined), '—'); assert.equal(App.fmtMoney('abc'), '—');
  assert.equal(App.fmtMoney(1234.5), '$1,234.50'); assert.equal(App.fmtMoney(-1234.5), '-$1,234.50'); assert.equal(App.fmtMoney(0.0375, 4), '$0.0375');
  assert.equal(App.fmtBig(null), '—'); assert.equal(App.fmtBig(1e12), '$1.00T'); assert.equal(App.fmtBig(3.2e12), '$3.20T'); assert.equal(App.fmtBig(-2.5e9), '-$2.50B');
  assert.equal(App.fmtBig(19000000), '$19M'); assert.equal(App.fmtBig(4776000), '$5M'); assert.equal(App.fmtBig(1500), '$2K'); assert.equal(App.fmtBig(12.345), '$12.35'); assert.equal(App.fmtBig(0), '$0.00');
  assert.equal(App.fmtCnt(null), '—'); assert.equal(App.fmtCnt(1.5e9), '1.50B'); assert.equal(App.fmtCnt(337875000), '337.9M'); assert.equal(App.fmtCnt(999), '999'); assert.equal(App.fmtCnt(-2e6), '-2.0M');
  assert.equal(App.fmtPct(null), '—'); assert.equal(App.fmtPct(0.1843), '18.4%'); assert.equal(App.fmtPct(-0.123), '-12.3%'); assert.equal(App.fmtPct(0.1843, 1, true), '+18.4%'); assert.equal(App.fmtPct(0, 1, true), '+0.0%'); assert.equal(App.fmtPct(12.3456, 0), '1,235%');
  assert.equal(App.fmtPts(null), '—'); assert.equal(App.fmtPts(38.1), '+38%'); assert.equal(App.fmtPts(-55.6, 1), '-55.6%');
  assert.equal(App.fmtX(null), '—'); assert.equal(App.fmtX(5.2), '5.2×'); assert.equal(App.fmtX(1.1, 2), '1.10×'); assert.equal(App.fmtX(-0.5), '-0.5×');
  assert.equal(App.fmtCap(null), '—'); assert.equal(App.fmtCap(93.11), '$93.11B'); assert.equal(App.fmtCap(1234.5), '$1,234.50B');
  assert.equal(App.num(''), null); assert.equal(App.num(true), null); assert.equal(App.num('1e3'), 1000); assert.equal(App.num(NaN), null); assert.equal(App.num('272.28'), 272.28);
  assert.equal(App.signCls(null), ''); assert.equal(App.signCls(-1), 'neg'); assert.equal(App.signCls(2), 'pos'); assert.equal(App.signCls(0), '');
  assert.equal(App.esc('<a href="x">&\'</a>'), '&lt;a href=&quot;x&quot;&gt;&amp;&#39;&lt;/a&gt;'); assert.equal(App.esc(null), ''); assert.equal(App.esc(0), '0');
  assert.equal(App.safeId('BRK.B'), 'BRK.B'); assert.equal(App.safeId('A B/C'), 'A-B-C');
  assert.equal(App.tierForIrr(0.26), 'S'); assert.equal(App.tierForIrr(0.2), 'A'); assert.equal(App.tierForIrr(0.15), 'B'); assert.equal(App.tierForIrr(0.1), 'C'); assert.equal(App.tierForIrr(0.05), 'D'); assert.equal(App.tierForIrr(null), null);
  assert.equal(App.tierForIrr(0.12, { B: 0.11 }), 'B');
});

test('md(): headings, lists, tables, bold, code, links, hr, fences, escaping', () => {
  const html = App.md(synthetic.analysis_md);
  assert.ok(html.includes('<h2>Synthetic Payer Corp</h2>'), 'h1 maps to h2');
  assert.ok(html.includes('<h3>What it is</h3>'), 'h2 maps to h3');
  assert.ok(html.includes('<b>fixture</b>') && html.includes('<code>code</code>'));
  assert.ok(html.includes('<a href="https://example.com/?a=1&amp;b=2" target="_blank" rel="noopener">link</a>'), 'link with escaped href');
  assert.ok(html.includes('<ul><li>first point continued line</li><li>second point</li></ul>'), 'ul with continuation line');
  assert.ok(html.includes('<ol><li>ordered one</li><li>ordered two</li></ol>'), 'ordered list');
  assert.ok(html.includes('<table class="mdt"><thead><tr><th>Scenario</th><th>IRR</th></tr></thead><tbody><tr><td>Bear</td><td>8%</td></tr><tr><td>Bull</td><td>21%</td></tr></tbody></table>'), 'table');
  assert.ok(html.includes('<hr>'));
  assert.ok(html.includes('<pre class="json">raw &lt;block&gt;</pre>'), 'fenced code escaped');
  assert.ok(html.includes('&lt;angle&gt; brackets'), 'raw angle brackets escaped');
  assert.ok(!/<angle>/.test(html));
  assert.equal(App.md(''), ''); assert.equal(App.md(null), '');
  assert.equal(App.md('###### deep'), '<h4>deep</h4>');
  assert.equal(App.md('[x](javascript:alert(1))'), '<p>[x](javascript:alert(1))</p>', 'non-http links are not linked');
  assert.equal(App.md('a\nb\n\nc'), '<p>a b</p><p>c</p>');
  assert.equal(App.md('| a | b |\n|---|---|\n| 1 | 2 |'), '<div class="twrap"><table class="mdt"><thead><tr><th>a</th><th>b</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table></div>');
});

test('parseHash: #, #T, #T.tab, dotted tickers, legacy #T/tab, bad tokens, forecast sub-tabs', () => {
  assert.deepEqual(App.parseHash('#'), { ticker: null, tab: 'overview', sub: 'dcf' });
  assert.deepEqual(App.parseHash(''), { ticker: null, tab: 'overview', sub: 'dcf' });
  assert.deepEqual(App.parseHash('#APP'), { ticker: 'APP', tab: 'overview', sub: 'dcf' });
  assert.deepEqual(App.parseHash('#APP.financials'), { ticker: 'APP', tab: 'financials', sub: 'dcf' });
  assert.deepEqual(App.parseHash('#BRK.B'), { ticker: 'BRK.B', tab: 'overview', sub: 'dcf' });
  assert.deepEqual(App.parseHash('#BRK.B.data'), { ticker: 'BRK.B', tab: 'data', sub: 'dcf' });
  assert.deepEqual(App.parseHash('#APP/forecast'), { ticker: 'APP', tab: 'forecast', sub: 'dcf' });
  assert.equal(App.parseHash('#<script>').bad, true);
  assert.equal(App.parseHash('#APP.Financials').tab, 'financials');
  assert.deepEqual(App.parseHash('#APP.forecast.street'), { ticker: 'APP', tab: 'forecast', sub: 'street' });
  assert.deepEqual(App.parseHash('#BRK.B.forecast.analysts'), { ticker: 'BRK.B', tab: 'forecast', sub: 'analysts' });
  assert.deepEqual(App.parseHash('#APP.forecast.dcf'), { ticker: 'APP', tab: 'forecast', sub: 'dcf' });
  assert.deepEqual(App.parseHash('#APP.overview.street'), { ticker: 'APP.overview.street', tab: 'overview', sub: 'dcf' }, 'a sub-tab suffix only counts after .forecast');
  assert.deepEqual(App.parseHash('#APP/forecast/street'), { ticker: 'APP', tab: 'forecast', sub: 'street' }, 'legacy slashes');
  assert.equal(App.hashFor('APP', 'overview', 'dcf'), '#APP'); assert.equal(App.hashFor('APP', 'forecast', 'dcf'), '#APP.forecast'); assert.equal(App.hashFor('APP', 'forecast', 'street'), '#APP.forecast.street'); assert.equal(App.hashFor('APP', 'data', 'street'), '#APP.data');
});

test('liveView: live figures when live.json exists, scored otherwise', () => {
  const v = App.liveView(synthetic);
  assert.equal(v.is_live, true); assert.equal(v.irr, 0.161); assert.equal(v.tier, 'B'); assert.equal(v.scored_tier, 'C'); assert.equal(v.scored_irr, 0.142); assert.equal(v.price, 45); assert.equal(v.scored_price, 50);
  assert.ok(Math.abs(v.upside - 33.333) < 0.01, 'upside from live iv15 / price'); assert.equal(v.cap_b, 4.5); assert.equal(v.tier_changed, true);
  const noLive = Object.assign({}, synthetic, { live: null });
  const w = App.liveView(noLive);
  assert.equal(w.is_live, false); assert.equal(w.irr, 0.142); assert.equal(w.tier, 'C'); assert.equal(w.price, 50); assert.equal(w.upside, 20);
  const hp = App.hurdlePrices(synthetic); assert.equal(hp[15], 60); assert.equal(hp[20], 45.5); assert.equal(hp[25], 36);
  const hp2 = App.hurdlePrices({ score: { iv_at_15: 10 }, row: { iv20: 8, iv25: 6 } }); assert.deepEqual(hp2, { 15: 10, 20: 8, 25: 6 });
  const sens = App.sensitivity(synthetic); assert.equal(sens.weighted[15], 60); assert.equal(sens.bear.irr_live, 0.09);
  const sens2 = App.sensitivity({ numbers: { scenarios: { bear: { iv_at_15: 42, irr: 0.08 } }, weighted: { iv_at_15: 60, irr: 0.14 } } });
  assert.equal(sens2.bear[15], 42); assert.equal(sens2.weighted.irr, 0.14); assert.equal(sens2.bull[15], null);
});

/* ---- real records */
Object.keys(loaded).forEach((t) => {
  const record = loaded[t].record;
  test(t + ': every tab renders without throwing (' + loaded[t].source + ')', () => {
    App.TAB_KEYS.forEach((tab) => {
      const html = App.renderCompanyHTML(record, tab);
      assert.ok(typeof html === 'string' && html.length > 1000, tab + ' renders');
      assert.ok(!html.includes('could not be rendered'), tab + ' has no renderer error: ' + (html.match(/could not be rendered: [^<]*/) || [''])[0]);
      assert.ok(html.includes('class="tab on" data-tab="' + tab + '"'), tab + ' tab is selected');
      assert.ok(html.includes('class="pane on" data-pane="' + tab + '"'), tab + ' pane is on');
    });
    ['renderHeader', 'renderPriceChart', 'renderOverview', 'renderFinancials', 'renderDividends', 'renderSegments', 'renderForecast', 'renderAnalysis', 'renderData'].forEach((fn) => { assert.ok(App[fn](record).length > 0, fn); });
    const specs = App.chartSpecs(record); assert.ok(specs.price, 'price spec');
    Object.keys(specs).forEach((k) => { if (k !== 'price') { const el = fakeEl(); App.drawChart(el, specs[k]); assert.ok(el.innerHTML.includes('<svg') || el.innerHTML.includes('No data'), k + ' draws'); } });
    if (record.prices && record.prices.weekly && record.prices.weekly.length) { const el = fakeEl(); const r = App.drawPrice(el, specs.price, { range: '5Y' }); assert.ok(el.innerHTML.includes('<svg') && r && /\d%/.test(r.text), 'price chart draws'); }
  });
  test(t + ': tab order and header figures', () => {
    const html = App.renderCompanyHTML(record, 'overview');
    assert.deepEqual(tabOrder(html), ['overview', 'financials', 'dividends', 'segments', 'forecast', 'analysis', 'data']);
    const head = App.renderHeader(record), s = record.score || {}, lv = record.live;
    if (lv && typeof lv.irr_weighted === 'number') {
      assert.ok(head.includes('Expected return / yr · live'), 'live label');
      assert.ok(head.includes('>' + App.fmtPct(lv.irr_weighted) + '</span>'), 'big number is the live IRR ' + App.fmtPct(lv.irr_weighted));
      assert.ok(head.includes('Scored <b>' + App.fmtPct(s.implied_irr) + '</b>'), 'scored figure beside the live one');
      assert.ok(head.includes('lvchip'), 'tier chip (live vs scored)');
      assert.ok(head.includes('>Last close</span>') && head.includes('scored ' + App.fmtMoney(lv.scored_price !== undefined ? lv.scored_price : s.price)), 'last close tile with the scored price');
    } else {
      assert.ok(!head.includes('· live'), 'no live label');
      assert.ok(head.includes(App.fmtPct(s.implied_irr)), 'big number is the scored IRR');
      assert.ok(head.includes('Probability-weighted IRR at'));
    }
  });
});

test('AEE (Tier F, no scenarios): forecast empty state, header without a return', () => {
  if (!loaded.AEE) { console.log('  (AEE record not available — skipped)'); return; }
  const r = loaded.AEE.record, fc = App.renderForecast(r), head = App.renderHeader(r);
  assert.ok(fc.includes('No projection'), 'forecast empty state');
  assert.ok(head.includes('>—</span>') || head.includes('F ·'), 'F header');
  assert.ok(App.renderOverview(r).includes('No positive owner'), 'gauge label for F');
});
test('KR (52/53-week FY): quarterly labels and annual FYs render from fundamentals', () => {
  if (!loaded.KR) { console.log('  (KR record not available — skipped)'); return; }
  const fin = App.renderFinancials(loaded.KR.record);
  assert.ok(fin.includes('Q2 FY2027') || fin.includes('FY2026'), 'labels present');
  assert.ok(fin.includes('<table class="fin">'), 'statement tables');
  const specs = App.chartSpecsFinancials(loaded.KR.record); assert.ok(specs['fin-ann'] && specs['fin-q'], 'annual + quarterly specs');
});
test('empty states: dividends and segments when the blocks are absent', () => {
  const noExtras = Object.assign({}, synthetic, { segments: null, fundamentals: Object.assign({}, synthetic.fundamentals, { dividends: undefined }) });
  assert.ok(App.renderDividends(noExtras).includes('Dividend enrichment has not run'), 'dividends empty state');
  assert.ok(App.renderSegments(noExtras).includes('No segment tables'), 'segments empty state');
  assert.deepEqual(App.chartSpecsSegments(noExtras), {}); assert.deepEqual(App.chartSpecsDividends(noExtras), {});
  const noDiv = Object.assign({}, synthetic, { fundamentals: Object.assign({}, synthetic.fundamentals, { dividends: { dps_ttm: null, frequency: 'none', buybacks_ttm: 60000000, buyback_yield: 0.013, price: 45, price_date: '2026-10-14', annual_dps: [], history: [], notes: [] } }) });
  const nd = App.renderDividends(noDiv); assert.ok(nd.includes('No dividend') && nd.includes('Buyback yield'), 'no-dividend state keeps the buyback tiles');
  assert.ok(App.renderFinancials({ fundamentals: null, history: [] }).includes('No financial history'));
  assert.ok(App.renderFinancials({ fundamentals: null, history: synthetic.history }).includes('Financial history (engine)'), 'history CSV fallback');
  assert.ok(App.renderAnalysis({}).includes('No analysis.md'));
  assert.ok(App.renderPriceChart({ score: synthetic.score, numbers: synthetic.numbers, live: synthetic.live, prices: null }).includes('pvplot'), 'number line without prices');
  assert.ok(App.renderCompanyHTML({}, 'overview').includes('<article'), 'empty record still renders');
});

/* ---- synthetic: dividends, segments, live */
test('synthetic: dividend tiles, DPS chart, history and notes', () => {
  const html = App.renderDividends(synthetic);
  ['Dividend yield', 'Annual dividend', 'Payout frequency', 'Payout ratio (vs EPS)', "Payout vs owner's earnings", 'Dividend growth (YoY)', 'Growth years', 'Buyback yield', 'Net buyback yield', 'Shareholder yield'].forEach((k) => assert.ok(html.includes(k), k));
  assert.ok(html.includes('2.8%') && html.includes('$1.26') && html.includes('Quarterly') && html.includes('5-yr CAGR +8.8%') && html.includes('no cut in the filed history'));
  assert.ok(html.includes('data-cid="div-dps"') && html.includes('Dividend history') && html.includes('2025-12-31'));
  const spec = App.chartSpecsDividends(synthetic)['div-dps'];
  assert.equal(spec.labels.length, 5); assert.equal(spec.series[0].tips[1], 'YoY +11.1%'); assert.equal(spec.series[0].tips[0], '');
  const el = fakeEl(); App.drawChart(el, spec); assert.ok(el.innerHTML.includes('YoY +11.1%'), 'tip in tooltip');
});
test('synthetic: segment tables with eliminations last, totals, stacked chart specs', () => {
  const html = App.renderSegments(synthetic);
  assert.ok(html.includes('Grocery') && html.includes('Pharmacy'));
  assert.ok(html.indexOf('Pharmacy') < html.indexOf('Corporate &amp;amp; eliminations'), 'eliminations row sorted last');
  assert.ok(html.includes('Total <span class="sub">(Revenues (consolidated))</span>'), 'total row');
  assert.ok(html.includes('Share of total') && html.includes('YoY growth') && html.includes('†'));
  assert.ok(html.indexOf('· annual ·') < html.indexOf('· quarterly ·'), 'annual table first');
  const specs = App.chartSpecsSegments(synthetic);
  assert.ok(specs['seg-0'].stacked === true && specs['seg-0'].totals.length === 3 && specs['seg-0'].series.length === 3);
  assert.equal(specs['seg-0'].series[2].name, 'Corporate &amp; eliminations');
  assert.equal(specs['seg-0'].series[0].tips[0], '67% of total');
});
test('drawChart: stacked bars stack positives up and negatives down with a total outline', () => {
  const spec = { labels: ['A', 'B'], yfmt: 'big', height: 200, stacked: true, totals: [150, 80], totalName: 'Tot<al>',
    series: [{ name: 'S1', color: '#111', kind: 'bar', values: [100, 50] }, { name: 'S2', color: '#222', kind: 'bar', values: [60, -20] }, { name: 'Line', color: '#333', kind: 'line', values: [120, 70] }] };
  const el = fakeEl(600); App.drawChart(el, spec);
  const rects = el.innerHTML.match(/<rect [^>]*>/g);
  assert.equal(rects.length, 6, '4 segment rects + 2 total outlines');
  const ys = rects.map((r) => ({ y: parseFloat(/ y="([\d.]+)"/.exec(r)[1]), h: parseFloat(/ height="([\d.]+)"/.exec(r)[1]), fill: /fill="([^"]+)"/.exec(r)[1] }));
  const zero = (function () { const m = /class="zero"[^>]*y1="([\d.]+)"/.exec(el.innerHTML); return parseFloat(m[1]); })();
  assert.ok(ys[0].y + ys[0].h <= zero + 0.2 && ys[2].y + ys[2].h <= ys[0].y + 0.2, 'A: S2 stacked on top of S1 above the zero line');
  assert.ok(ys[3].y >= zero - 0.2, 'B: negative S2 hangs below the zero line');
  assert.ok(ys[4].fill === 'none' && ys[5].fill === 'none', 'total outlines are unfilled');
  assert.ok(el.innerHTML.includes('<title>A · S1: $100.00</title>') && el.innerHTML.includes('Tot&lt;al&gt;: $150.00'), 'tooltips via <title>, escaped');
  assert.ok(el.innerHTML.includes('class="leg"') && el.innerHTML.includes('Tot&lt;al&gt;'), 'legend');
  const grouped = fakeEl(); App.drawChart(grouped, { labels: ['x'], series: [{ name: 'n', color: '#000', kind: 'bar', values: [1] }, { name: 'a', color: '#000', kind: 'area', values: [2] }] });
  assert.ok(grouped.innerHTML.includes('<rect') && grouped.innerHTML.includes('opacity=".15"'), 'grouped bar + area');
  const empty = fakeEl(); App.drawChart(empty, { labels: ['x'], series: [{ name: 'n', kind: 'bar', values: [null] }] }); assert.ok(empty.innerHTML.includes('No data'));
  App.drawChart(empty, null); assert.ok(empty.innerHTML.includes('No data'));
});
test('drawPrice: ranges, overlays, right-edge tags', () => {
  const w = []; for (let i = 0; i < 520; i++) { const d = new Date(Date.UTC(2016, 9, 14) + i * 7 * 864e5); w.push([d.toISOString().slice(0, 10), 100 + Math.sin(i / 20) * 30 + i / 10]); }
  const d = []; for (let i = 0; i < 250; i++) { const dt = new Date(Date.UTC(2025, 9, 14) + i * 864e5); d.push([dt.toISOString().slice(0, 10), 140 + Math.cos(i / 15) * 10]); }
  const spec = { iv15: 160, iv12: 200, lo: 90, hi: 240, h20: 120, h25: 95, price: 150, pdate: '2026-10-14', w: w, d: d, src: 'test', asof: '2026-10-14' };
  let el = fakeEl(800, 280), r = App.drawPrice(el, spec, { range: '5Y', showIv: true, showBand: true, showH: true });
  assert.ok(el.innerHTML.includes('>IV</text>') && el.innerHTML.includes('>20%</text>') && el.innerHTML.includes('>25%</text>'), 'IV and hurdle tags');
  assert.ok(el.innerHTML.includes('Scenario range at 15%'), 'band tooltip'); assert.ok(/^5Y: [+-][\d.]+% \(\d{4}-\d{2}-\d{2} → \d{4}-\d{2}-\d{2}\)$/.test(r.text), r.text); // fmtRange prints one decimal under 100% (price-chart owner)
  el = fakeEl(800, 280); r = App.drawPrice(el, spec, { range: '1Y', showIv: false, showBand: false, showH: false });
  assert.ok(!el.innerHTML.includes('>IV</text>') && !el.innerHTML.includes('Scenario range'), 'overlays off'); assert.ok(r.text.startsWith('1Y:'));
  assert.ok(/<text [^>]*>\d{2}-\d{2}<\/text>/.test(el.innerHTML) || /<text class="xt"[^>]*>[A-Z][a-z]{2}( &#39;\d{2})?<\/text>/.test(el.innerHTML), '1Y uses month labels'); // "Nov" / "Jan '26" since the price-chart rework
  el = fakeEl(); assert.equal(App.drawPrice(el, { w: [] }, {}), null); assert.ok(el.innerHTML.includes('No price history'));
});

/* ---- owner layout decision: header → sticky tab bar → tab content; profile cards; performance prose */
test('company page order: header, tab bar with summary, panes; price chart inside Overview', () => {
  const html = App.renderCompanyHTML(synthetic, 'overview');
  const iHero = html.indexOf('<header class="hero"'), iBar = html.indexOf('<div class="tabbar">'), iSum = html.indexOf('class="tabsum"'), iTabs = html.indexOf('<div class="tabs"'), iPane = html.indexOf('data-pane="overview"'), iPc = html.indexOf('class="card pc"');
  assert.ok(iHero > 0 && iHero < iBar && iBar < iSum && iSum < iTabs && iTabs < iPane && iPane < iPc, 'header → tabbar(summary, tabs) → overview pane → price chart card');
  const ov = html.slice(iPane, html.indexOf('data-pane="financials"'));
  const order = ['class="card pc"', 'class="card verdict"', '<p class="take">', '<h2>About</h2>', '<h2>Financial performance</h2>', '<h2>Street summary</h2>', '<h2>Filings</h2>', '<h2>Key numbers</h2>', '<h2>Scenarios</h2>', '<h2>Moat</h2>', 'Fragility flags'];
  let last = -1; order.forEach((k) => { const i = ov.indexOf(k); assert.ok(i > last, k + ' in order (' + i + ' after ' + last + ')'); last = i; });
  assert.ok(!App.renderHeader(synthetic).includes('class="take"'), 'one-liner lives in the verdict card, header stays compact');
  const sum = App.renderTabSummary(synthetic); assert.ok(sum.includes('SYN') && sum.includes('$45.00') && sum.includes('16.1% live'), 'condensed summary: ticker · last close · expected return');
  const head = App.renderHeader(synthetic); assert.ok(head.includes('Scored <b>14.2%</b>') && head.includes('Last close') && head.includes('$45.00') && head.includes('Value @15%'), 'compact header keeps scored beside live');
  assert.ok(App.renderCompanyHTML(loaded.APP ? loaded.APP.record : synthetic, 'financials').indexOf('class="card pc"') > 0, 'price chart still rendered (inside overview) when another tab is selected');
});
test('About / Street / Filings cards from record.profile, with graceful fallbacks', () => {
  const about = App.renderAbout(synthetic);
  ['1,200 grocery and pharmacy stores', 'Food Chains', 'SIC 5411', 'Cincinnati, OH', '42,000', 'As of December 31, 2025', '1998-03-12', 'synthetic-payer.example', 'href="https://www.sec.gov/Archives/edgar/data/1234567/syn-20251231.htm"'].forEach((k) => assert.ok(about.includes(k), k));
  const street = App.renderStreet(synthetic);
  ['Street summary', 'consensus for SYN is based on 16 analysts', '<b>Buy</b>', '$58.00', '$44.00 – $72.00', 'Our hurdle prices: $60.00 for 15% (Tier B), $45.50 for 20% (Tier A), $36.00 for 25% (Tier S).', 'Buy 12', 'Hold 4', 'Sell 0', 'href="#SYN.forecast.street">See the full forecast', "The Street's view, not ours.", 'Street view — Nasdaq analyst data, not used by the valuation'].forEach((k) => assert.ok(street.includes(k), k));
  assert.ok(!street.includes('Consensus EPS') && !street.includes('<table'), 'the Overview card is the compact summary — no EPS or history tables');
  assert.ok(street.includes('class="bhs"') && street.includes('width:75.0%'), 'buy / hold / sell bar');
  const filings = App.renderFilings(synthetic);
  assert.ok(filings.includes('8-K') && filings.includes('2.02, 9.01') && filings.includes('Results of operations') && filings.includes('href="https://www.sec.gov/Archives/edgar/data/1234567/syn-8k-20261002.htm"'));
  assert.ok(!filings.includes('javascript:'), 'non-http filing URL is not linked');
  const bare = Object.assign({}, synthetic, { profile: undefined });
  const a2 = App.renderAbout(bare); assert.ok(a2.includes('Profile not pulled yet') && a2.includes('Retail-Grocery Stores') && a2.includes('NYSE'), 'About falls back to fundamentals.profile');
  assert.ok(App.renderStreet(bare).includes('Street consensus appears once profile.py'), 'Street empty state');
  assert.ok(App.renderForecastStreet(bare).includes('Street consensus appears once profile.py') && App.renderForecastAnalysts(bare).includes('Analyst coverage appears once profile.py'), 'sub-tab empty states');
  const f2 = App.renderFilings(bare); assert.ok(f2.includes('10-K') && f2.includes('latest 10-K') && f2.includes('2026-02-20'), 'Filings fall back to fundamentals latest_filings');
  assert.ok(App.renderAbout({}).includes('No profile facts') || App.renderAbout({}).includes('Profile not pulled yet'), 'About with nothing at all');
  assert.ok(App.renderFilings({}).includes('filing feed appears once') && App.renderStreet({ profile: { about: {} } }).includes('No analyst data'));
});
test('financialPerformance(): numbers-only prose with the fiscal year named; empty without annual rows', () => {
  const t = App.financialPerformance(synthetic);
  assert.ok(t.startsWith('In fiscal 2024 (ended 2024-12-31) revenue was $2.00B, +11.1% on fiscal 2023.'), t.slice(0, 120));
  ['Gross margin 34.0%', 'operating income $230M (11.5% margin)', 'net income $150M (7.5% margin), +15.4% year over year', 'Operating cash flow $400M (+11.1%)', 'capex $60M', 'stock-based compensation $20M',
   "Owner's earnings (operating cash flow − capex − stock-based compensation) were $320M, a 16.0% margin, $3.20 per diluted share (+15.9% on fiscal 2023)",
   'Over the twelve months to 2025-12-31: revenue $2.15B (+7.5% year over year)', "owner's earnings $343M (16.0% margin), $3.48 per share",
   'Diluted shares were 100.0M, -3.8% on fiscal 2023 and -3.8% over 1 years (fiscal 2023 → 2024)', 'At fiscal year end: cash $180M, total debt $580M, net debt $400M', 'Cash returned or deployed in fiscal 2024: dividends $100M, buybacks $60M, acquisitions $10M.'].forEach((k) => assert.ok(t.includes(k), k));
  assert.ok(!/\b(strong|weak|impressive|healthy|solid|robust)\b/i.test(t), 'no adjectives');
  assert.equal(App.financialPerformance({}), ''); assert.equal(App.financialPerformance({ fundamentals: { annual: [] } }), '');
  assert.ok(App.financialPerformance({ fundamentals: { annual: [{ fy: '2025', period_end: '2025-12-31' }] } }).startsWith('In fiscal 2025 no revenue figure was filed.'));
  if (loaded.KR) { const k = App.financialPerformance(loaded.KR.record); assert.ok(/^In fiscal \d{4} \(ended \d{4}-\d{2}-\d{2}\) revenue was \$[\d.]+B/.test(k), k.slice(0, 80)); assert.ok(App.renderPerformance(loaded.KR.record).includes('Financial performance')); }
  if (loaded.HBAN) assert.ok(App.financialPerformance(loaded.HBAN.record).length > 100, 'bank prose (no cogs) still renders');
});

/* ---- escaping */
test('no raw "<" from data strings survives in any rendered HTML', () => {
  const sources = [synthetic].concat(Object.keys(loaded).map((t) => loaded[t].record));
  sources.forEach((src) => {
    const rec = inject(src);
    const pages = App.TAB_KEYS.map((tab) => App.renderCompanyHTML(rec, tab, { prev: 'P<x-inj>', next: 'N<x-inj>', rank: 3 })).join('');
    const list = App.renderListHTML(inject(meta), [inject(src.row)], { tier: 'all', fit: 'all', sort: 'irr_live', q: '' });
    const missing = App.renderMissingHTML(inject(src.row), inject(meta)) + App.renderErrorHTML('e<x-inj>', 'd<x-inj>');
    [pages, list, missing].forEach((html) => {
      assert.ok(!html.includes('<x-inj>'), 'raw marker leaked for ' + (src.ticker || '?'));
      assert.ok(html.includes('&lt;x-inj&gt;'), 'escaped marker present');
    });
    const specs = App.chartSpecs(rec);
    Object.keys(specs).forEach((k) => { if (k === 'price') return; const el = fakeEl(); App.drawChart(el, specs[k]); assert.ok(!el.innerHTML.includes('<x-inj>'), 'chart ' + k + ' escapes labels and names'); });
  });
});

/* ---- list */
test('renderListHTML: columns, default live sort, filters, search, remembered state shape, stale box', () => {
  const rows = index.concat([synthetic.row]);
  const html = App.renderListHTML(meta, rows, App.defaultState());
  assert.ok(html.includes('<th class="num sortable sorted" data-sort="irr_live"'), 'Live IRR sorted by default');
  ['Company', 'Tier', 'Band', 'Live IRR', 'Scored IRR', 'Price', 'IV @15%', 'Upside', 'Moat', 'Conf.', 'Mkt cap', '1y price', 'Take'].forEach((c) => assert.ok(html.includes('>' + c + '</th>'), c));
  const sorted = App.filterSortIndex(rows, App.defaultState());
  for (let i = 1; i < sorted.length; i++) {
    const a = sorted[i - 1], b = sorted[i], ka = a.irr_live != null ? a.irr_live : a.irr, kb = b.irr_live != null ? b.irr_live : b.irr;
    assert.ok(ka === null || kb === null || ka >= kb, 'descending by live IRR (fallback scored)');
  }
  const tierB = App.filterSortIndex(rows, { tier: 'B', fit: 'all' }); assert.ok(tierB.length >= 1 && tierB.every((r) => (r.tier_live || r.tier) === 'B'), 'tier filter uses the live tier');
  assert.deepEqual(App.filterSortIndex(rows, { fit: 'all', q: 'synthetic payer' }).map((r) => r.ticker), ['SYN'], 'search by name');
  assert.deepEqual(App.filterSortIndex(rows, { fit: 'all', q: 'syn' }).map((r) => r.ticker), ['SYN']);
  assert.equal(App.filterSortIndex(rows, { fit: 'misfit' }).every((r) => r.fit === 'misfit'), true);
  const byCap = App.filterSortIndex(rows, { fit: 'all', sort: 'cap' }); assert.ok(byCap.length === rows.length);
  assert.deepEqual(App.normState({ tier: 'Z', fit: 'nope', sort: 'bogus', q: 5 }), App.defaultState(), 'bad stored state falls back');
  assert.deepEqual(App.normState({ tier: 'C', fit: 'all', sort: 'moat', q: 'kr' }), { tier: 'C', fit: 'all', sort: 'moat', q: 'kr', watch: false });
  assert.equal(App.normState({ watch: true }).watch, true); assert.equal(App.normState({ watch: 'yes' }).watch, false, 'watch must be a real boolean');
  const row = App.renderRowHTML(synthetic.row);
  assert.ok(row.includes('>B</span><span class="was">was C</span>'), 'live tier with "was X"');
  assert.ok(row.includes('16.1%') && row.includes('14.2%') && row.includes('$45.00') && row.includes('+33%') && row.includes('✓ pass 2'), 'live IRR, scored IRR, live price, live upside, pass-2 badge');
  assert.ok(row.includes('href="#SYN"'), 'row links to #TICKER');
  assert.ok(App.renderListRowsHTML([], {}).includes('No companies analyzed yet'));
  assert.ok(App.renderListRowsHTML(rows, { fit: 'all', q: 'zzzzzz' }).includes('Nothing matches'));
  const stale = App.renderListHTML(Object.assign({}, meta, { stale: [{ ticker: 'OLD', name: 'Old Co', tier: 'B', irr: 0.17, analysis_date: '2026-10-12' }] }), rows, {});
  assert.ok(stale.includes('Pre-v5 results — re-run pending (1)') && stale.includes('OLD'), 'stale box');
  assert.ok(!App.renderListHTML(meta, rows, {}).includes('stalebox') || (meta.stale || []).length, 'no stale box without stale rows');
  assert.ok(App.renderMissingHTML(synthetic.row, meta).includes('not embedded in this file'), 'attachment missing-record notice');
  assert.ok(html.includes('id="notice"') && html.includes('role="progressbar"'));
});


/* ---- review round (2026-10-15): condensed bar price rule, column geometry, watchlist, floor markers, Forecast sub-tabs */
test('renderTabSummary pairs the 1-day change with the close it was measured on', () => {
  if (!loaded.AEE || !loaded.AEE.record.prices) skip('AEE tab summary close — needs AEE/prices.json (a gitignored cache)');
  else {
    const r = loaded.AEE.record, st = r.prices.stats, sum = App.renderTabSummary(r);
    assert.ok(!r.live, 'AEE has no live.json');
    assert.ok(sum.includes(App.fmtMoney(st.last)) && sum.includes(App.fmtPts(st.change_1d_pct, 2)), 'last close + its change: ' + sum);
    assert.ok(!sum.includes(App.fmtMoney(r.score.price)) || st.last === r.score.price, 'not the scored price');
    assert.ok(App.renderHeader(r).includes(App.fmtMoney(st.last)), 'header shows the same close');
  }
  const noPx = Object.assign({}, synthetic, { live: null, prices: null });
  const s2 = App.renderTabSummary(noPx);
  assert.ok(s2.includes('$50.00') && !/[+-]\d+\.\d+%<\/span>/.test(s2.replace(/14\.2%/, '')), 'scored price without a change figure: ' + s2);
  const scoredOnlyWithPrices = Object.assign({}, synthetic, { live: null, prices: { stats: { last: 47.5, last_date: '2026-10-14', change_1d_pct: -1.2 }, weekly: [] } });
  const s3 = App.renderTabSummary(scoredOnlyWithPrices);
  assert.ok(s3.includes('$47.50') && s3.includes('-1.20%') && !s3.includes('$50.00'), 'last close with its change, scored price not shown: ' + s3);
  const live = App.renderTabSummary(synthetic); assert.ok(live.includes('$45.00') && live.includes('16.1% live'), 'live page: live price');
});
test('ranking table carries a <colgroup> with explicit widths summing to 100%', () => {
  const html = App.renderListHTML(meta, index, App.defaultState());
  const cg = /<colgroup>([\s\S]*?)<\/colgroup>/.exec(html); assert.ok(cg, 'colgroup present');
  const cols = cg[1].match(/<col /g); assert.equal(cols.length, 13, 'one col per column');
  assert.equal(App.COLS.length, 13);
  const sum = App.COLS.reduce((a, c) => a + c[3], 0); assert.ok(Math.abs(sum - 100) < 0.01, 'widths sum to 100, got ' + sum);
  assert.ok(App.COLS[0][3] >= 12 && App.COLS[12][3] >= 20, 'Company and Take get the room');
  assert.ok(html.indexOf('<colgroup>') < html.indexOf('<thead>'), 'colgroup before thead');
});
test('watchlist: state, filter, toggle button, canonical star vs per-device star extras', () => {
  const rows = index.concat([synthetic.row]);
  const w = App.filterSortIndex(rows, { fit: 'all', watch: true });
  const canon = rows.filter((r) => r.watchlist === true);
  assert.equal(w.length, canon.length, 'watch filter = canonical rows'); assert.ok(w.every((r) => r.watchlist === true));
  assert.equal(App.filterSortIndex(rows, { fit: 'all', watch: false }).length, rows.length, 'off = everything');
  const w2 = App.filterSortIndex(rows, { fit: 'all', watch: true }, ['syn']);
  assert.equal(w2.length, canon.length + 1, 'a starred ticker (case-insensitive) joins the watchlist view'); assert.ok(w2.some((r) => r.ticker === 'SYN'));
  assert.deepEqual(App.normStars(['syn', 'SYN', 7, 'bad ticker!', { x: 1 }]), ['SYN']); assert.deepEqual(App.normStars({ app: true, kr: false }), ['APP']); assert.deepEqual(App.normStars(null), []);
  assert.equal(App.watchCount(rows, ['SYN']), canon.length + 1);
  const html = App.renderListHTML(meta, rows, Object.assign(App.defaultState(), { watch: true }), ['SYN']);
  assert.ok(html.includes('id="watchbtn" class="wbtn on" aria-pressed="true"') && html.includes('★ Watchlist <span class="mono">' + (canon.length + 1) + '</span>'), 'toggle button with the count, pressed');
  assert.ok(html.indexOf('id="tierseg"') < html.indexOf('id="watchbtn"') && html.indexOf('id="watchbtn"') < html.indexOf('id="fitseg"'), 'button sits next to the tier filters');
  const off = App.renderListHTML(meta, rows, App.defaultState()); assert.ok(off.includes('class="wbtn" aria-pressed="false"'));
  const synRow = App.renderRowHTML(synthetic.row, ['SYN']); assert.ok(synRow.includes('class="star on" data-star="SYN" aria-pressed="true"') && synRow.includes('data-watch="1"') && synRow.includes('★'), 'starred row');
  const plain = App.renderRowHTML(synthetic.row); assert.ok(plain.includes('class="star" data-star="SYN" aria-pressed="false"') && plain.includes('☆') && !plain.includes('data-watch'), 'unstarred row has the toggle');
  if (canon.length) { const c = App.renderRowHTML(canon[0]); assert.ok(c.includes('class="star fixed repo"') && !c.includes('data-star='), 'canonical watchlist row: fixed repo star, no toggle'); }
  assert.ok(App.renderListRowsHTML(rows, { fit: 'all', watch: true, q: 'zzzz' }).includes('Nothing on the watchlist'));
  if (loaded.APP && loaded.APP.record.row.watchlist) assert.ok(App.renderHeader(loaded.APP.record).includes('★ Watchlist'), 'company hero shows the watchlist chip');
  assert.ok(!App.renderHeader(synthetic).includes('★ Watchlist'));
});
test('floor-clamped IRRs are marked (ZS: live super-bear / bear at the floor), header band too', () => {
  const rec = builtOr('ZS', 'ZS live floor flags in the Forecast table and header');
  if (rec) {
    const sens = App.sensitivity(rec);
    // the scored flags are the run's own (ZS: super bear and bear at the floor); the live ones follow the last close
    assert.equal(sens.super_bear.irr_at_floor, true); assert.equal(sens.bear.irr_at_floor, true); assert.equal(sens.base.irr_at_floor, false);
    const ff = App.floorFlags(rec, true), SC = ['super_bear', 'bear', 'base', 'bull', 'super_bull'];
    SC.forEach((k) => assert.equal(!!ff[k], sens[k].irr_live_at_floor === true, 'live floor flag ' + k));
    assert.ok(!ff.weighted && !!ff.any === SC.some((k) => !!ff[k]));
    const fc = App.renderForecastDCF(rec);
    const sb = fc.slice(fc.indexOf('<th>Super bear'), fc.indexOf('<th>Bear'));
    assert.ok(sb.includes('class="num mono atfloor"') && sb.includes('>at floor</sup>'), 'super-bear IRR cell marked');
    const base = fc.slice(fc.indexOf('<th>Base'), fc.indexOf('<th>Bull'));
    assert.ok(!base.includes('at floor'), 'base cell unmarked');
    assert.ok(fc.includes('<b>At floor</b> marks an IRR the solver clamped'), 'explanation under the table');
    if (ff.bear) {
      assert.ok(/bear case <b>[A-F]<\/b> \([-\d.]+%, <sup class="floor"/.test(fc), 'hurdle band note marks the bear end');
      assert.ok(App.renderHeader(rec).includes('<sup class="floor"'), 'header band marks the bear end');
    }
  }
  const clean = App.renderForecastDCF(synthetic); assert.ok(!clean.includes('at floor'), 'no marker without flags');
  const flagged = JSON.parse(JSON.stringify(synthetic)); flagged.forecast.sensitivity.bear.irr_at_floor = true; flagged.live = null;
  assert.ok(App.renderForecastDCF(flagged).includes('>at floor</sup>') && App.renderHeader(flagged).includes('<sup class="floor"'), 'scored floor flag marks the scored view');
  const rowFloor = Object.assign({}, synthetic, { row: Object.assign({}, synthetic.row, { irr_at_floor_live: true }) });
  assert.ok(App.liveView(rowFloor).irr_at_floor === true && App.renderHeader(rowFloor).includes('at the model floor'), 'row.irr_at_floor_live counts like live.irr_at_floor');
});
test('Forecast tab: DCF / Street / Analysts sub-tabs, hash-driven, DCF default; every existing section stays', () => {
  const html = App.renderCompanyHTML(synthetic, 'forecast');
  const pane = html.slice(html.indexOf('data-pane="forecast"'), html.indexOf('data-pane="analysis"'));
  assert.ok(pane.includes('class="subtabs"') && pane.includes('class="subtab on" data-sub="dcf"') && pane.includes('data-sub="street"') && pane.includes('data-sub="analysts"'), 'sub-tab strip, DCF on');
  assert.ok(pane.includes('class="subpane on" data-sub="dcf"') && pane.includes('class="subpane" data-sub="street"') && pane.includes('class="subpane" data-sub="analysts"'), 'three panes, DCF visible');
  assert.ok(pane.indexOf('data-sub="dcf"') < pane.indexOf('data-sub="street"') && pane.indexOf('class="subpane" data-sub="street"') < pane.indexOf('class="subpane" data-sub="analysts"'), 'order DCF → Street → Analysts');
  const st = App.renderCompanyHTML(synthetic, 'forecast', null, 'street');
  assert.ok(st.includes('class="subtab on" data-sub="street"') && st.includes('class="subpane on" data-sub="street"') && st.includes('class="subpane" data-sub="dcf"'), 'street sub-tab selected from the hash');
  ["Owner's earnings per share — history and forecast", "Owner's earnings growth", "Owner's earnings per share — the five paths", 'Growth fade', 'Value at every discount rate', 'Hurdle prices', 'How growth was set'].forEach((k) => assert.ok(pane.includes(k), k));
  assert.ok(pane.indexOf('history and forecast') < pane.indexOf("Owner's earnings growth") && pane.indexOf("Owner's earnings growth") < pane.indexOf('the five paths'), 'new sections first');
  Object.keys(loaded).forEach((t) => { const f = App.renderForecast(loaded[t].record, 'analysts'); assert.ok(f.includes('class="subpane on" data-sub="analysts"') && !f.includes('could not be rendered'), t + ' analysts sub-tab'); });
});
test('OE/share history + forecast: series join at the base year, High/Avg/Low tables, growth error bars', () => {
  const J = App.oeForecastSeries(synthetic);
  assert.equal(J.H, 2, 'two filed years'); assert.equal(J.N, 15); assert.equal(J.labels.length, 17);
  assert.deepEqual(J.labels.slice(0, 3), ['2023', '2024', '2025'], 'forecast years continue the fiscal-year labels');
  assert.equal(J.baseIndex, 1); assert.equal(J.weighted[1], synthetic.score.base_oe_per_share, 'weighted path starts from the engine base at the last history position');
  assert.equal(J.weighted[2], synthetic.forecast.paths.weighted[0]); assert.equal(J.super_bull[16], synthetic.forecast.paths.super_bull[14]);
  assert.equal(J.histVals[0], 2.76); assert.equal(J.histVals[1], 3.2); assert.equal(J.histVals[2], null);
  assert.ok(Math.abs(J.histGrowth[1] - (3.2 / 2.76 - 1)) < 1e-12 && J.histGrowth[0] === null, 'filed YoY');
  assert.ok(Math.abs(J.wGrowth[0] - (synthetic.forecast.paths.weighted[0] / synthetic.score.base_oe_per_share - 1)) < 1e-12, 'year-1 weighted growth measured from the base');
  assert.equal(J.bearGrowth[0], synthetic.forecast.growth_paths.bear[0]);
  const specs = App.chartSpecsForecast(synthetic), oe = specs['fc-oe'], g = specs['fc-oegrowth'];
  assert.ok(oe && oe.series[0].kind === 'band' && oe.series[0].lows.length === 17 && oe.series[1].name === 'Filed OE / share' && !oe.series[1].dash && oe.series[4].dash && oe.series[4].width === 3, 'band + solid history + dashed weighted');
  assert.equal(oe.dividerAt, 1);
  assert.ok(g && g.series[0].errors[2] && g.series[0].errors[2].length === 2 && g.series[0].errors[1] === null && g.series[0].colors[2] !== g.series[0].colors[1], 'error bars on forecast bars only, distinct colour');
  let el = fakeEl(800); App.drawChart(el, oe);
  assert.ok(el.innerHTML.includes('opacity=".16"') && el.innerHTML.includes('stroke-dasharray="5 4"') && el.innerHTML.includes('forecast →') && el.innerHTML.includes('class="ldash"'), 'band polygon, dashed forecast, divider, dashed legend swatch');
  el = fakeEl(800); App.drawChart(el, g);
  assert.ok(el.innerHTML.includes('<g class="err"') && el.innerHTML.includes('range:') && el.innerHTML.includes('class="lerr"'), 'error bars drawn with tooltips and a legend entry');
  const dcf = App.renderForecastDCF(synthetic);
  const t1 = dcf.slice(dcf.indexOf('<table class="fin hal">'), dcf.indexOf('</table>', dcf.indexOf('<table class="fin hal">')));
  ['Year 1', 'Year 2', 'Year 3', 'Year 5', 'Year 10', 'Year 15', 'FY2025', 'FY2039', 'High <span class="sub">super bull</span>', 'Avg <span class="sub">probability-weighted</span>', 'Low <span class="sub">super bear</span>'].forEach((k) => assert.ok(t1.includes(k), k));
  assert.ok(t1.includes(App.fmtMoney(synthetic.forecast.paths.weighted[0])) && t1.includes(App.fmtMoney(synthetic.forecast.paths.super_bear[14])) && t1.includes(App.fmtMoney(synthetic.forecast.paths.super_bull[9])), 'table cells come from the stored paths');
  assert.ok(dcf.includes('bull growth path') && dcf.includes('weighted path, YoY') && dcf.includes('bear growth path'), 'growth table rows');
  if (builtOr('APP', 'APP FY2025 OE/share gap against the engine paths')) { // FY2025: capex not tagged, the engine CSV's OE uses the capex estimate override → not a filed value, so no point
    const a = App.oeForecastSeries(built.APP); assert.ok(a.H >= 6 && a.histVals[a.baseIndex] === null && a.hist[a.baseIndex].fy === '2025', 'APP FY2025 OE/share left blank (no filed OE)'); assert.equal(a.labels[a.baseIndex + 1], '2026');
    assert.ok(/FY2025: capex not filed \(the engine run fills capex with an estimate/.test(a.hist[a.baseIndex].why), a.hist[a.baseIndex].why);
    assert.equal(a.weighted[a.baseIndex], built.APP.score.base_oe_per_share, 'the dashed paths still start from the engine base at FY2025');
    assert.ok(App.renderForecastDCF(built.APP).includes('<b>Not shown:</b> FY2025: capex not filed'), 'the note says which year is blank and why');
  }
  if (loaded.AEE) assert.equal(App.oeForecastSeries(loaded.AEE.record), null, 'Tier F: no series');
  const noHist = Object.assign({}, synthetic, { fundamentals: null, history: [] }); const nh = App.oeForecastSeries(noHist); assert.deepEqual(nh.labels.slice(0, 2), ['Base', '+1']); assert.equal(nh.histVals[0], synthetic.score.base_oe_per_share);
  assert.ok(App.renderForecastDCF(noHist).includes('history and forecast'), 'still renders without history');
});
const streetFull = (() => { const r = JSON.parse(JSON.stringify(synthetic)); Object.assign(r.profile.street, {
  history: r.profile.street.history.map((h, i) => Object.assign({}, h, { consensus: i ? 'Buy' : 'Strong Buy' })),
  brokers: ['Alpha Securities', { name: 'Beta Capital' }, ''],
  upgrades_downgrades: [{ date: '2026-09-15', firm: 'Alpha Securities', action: 'upgrade', from: 'Hold', to: 'Buy', target: 61 }, 'Beta Capital initiates at Buy'],
  eps_forecast: { quarterly: [{ period: 'Q1 2026', consensus: 0.41, low: 0.38, high: 0.45, estimates: 9 }, { period: 'Q2 2026', consensus: 0.44, low: 0.4, high: 0.5, estimates: 8 }], annual: [{ period: 'FY2026', consensus: 1.7, low: 1.55, high: 1.9, estimates: 12, revisions_up: 3, revisions_down: 0 }, { period: 'FY2027', consensus: 1.95, low: 1.8, high: 2.2, estimates: 10 }] },
  eps_history: [{ period: 'Q1 2025', consensus: 0.36, actual: 0.38, surprise_pct: 5.6 }, { period: 'Q2 2025', consensus: 0.41, actual: 0.4 }, { period: 'Q3 2025', consensus: 0.4, actual: 0.39, surprise_pct: -2.5 }, { period: 'Q4 2025', consensus: 0.42, actual: 0.43, surprise_pct: 2.4 }],
  eps_upcoming: [{ period: 'Q1 2026', consensus: 0.41 }],
  momentum: { quarter: { period: 'Q1 2026', current: 0.41, week_ago: 0.4, month_ago: 0.39 }, year: { period: 'FY2026', current: 1.7, week_ago: 1.7, month_ago: 1.65 } },
  next_earnings: { date: '2026-10-28', text: 'after market close (estimated)' }, peg_forward: 1.42 }); r.prices = { source: 'test', as_of: '2026-10-14', stats: { last: 45, last_date: '2026-10-14', change_1d_pct: 0.5 }, weekly: [], daily_1y: [] };
  for (let i = 0; i < 260; i++) { const dt = new Date(Date.UTC(2025, 9, 14) + i * 864e5); r.prices.daily_1y.push([dt.toISOString().slice(0, 10), 40 + Math.sin(i / 30) * 5]); } return r; })();
test('Street sub-tab: paragraph, gauge, fan, price-target table, trends, financial forecast toggle, EPS forecast/growth, track record, sources', () => {
  const s = App.renderForecastStreet(streetFull);
  ['Stock price forecast', 'consensus for SYN is based on 16 analysts', '+28.9%</b> vs the last close $45.00', 'class="sgauge"', 'Needle at (buy + ½ hold)', 'no strong-buy / strong-sell split', 'data-cid="street-fan"',
   '<h2>Price target</h2>', '<th>Low</th>', '<th>Average</th>', '<th>High</th>', '$44.00', '$58.00', '$72.00', '-2.2%', '+28.9%', '+60.0%', 'Nasdaq publishes no median target',
   '<h2>Analyst ratings</h2>', 'Of the 16 ratings', 'Recommendation trends', 'data-cid="street-trend"', '2026-10-01', '2026-07-01', '$55.00',
   '<h2>Financial forecast</h2>', 'class="seg ffseg"', 'data-ff="annual" class="on"', 'class="ffpane on" data-ff="annual"', 'class="ffpane" data-ff="quarterly"', 'EPS this year', 'EPS next year', 'from $1.50 (FY2024 filed)', '+13.3%', 'from $1.70 (FY2026 consensus)', '+14.7%', 'EPS this quarter', 'EPS next quarter', 'from $0.38 (Q1 FY2025 filed)', 'from $0.40 (Q2 FY2025 filed)', 'FY2023 <span class="sub">filed</span>', 'FY2026 <span class="sub">consensus</span>', 'Nasdaq publishes EPS consensus only',
   '<h2>EPS forecast</h2>', 'data-cid="street-eps"', '<h2>EPS growth</h2>', 'data-cid="street-epsg"',
   '<h2>Earnings track record</h2>', 'data-cid="street-track"', 'Q4 2025', '+2.4%', '-2.4%', 'Next report: <b>2026-10-28</b>', 'after market close', 'upcoming consensus Q1 2026 $0.41',
   'class="srcbox"', 'Zacks consensus', 'pulled 2026-10-14', 'not GAAP', 'not an input to the DCF', "The Street's view, not ours."].forEach((k) => assert.ok(s.includes(k), k));
  const specs = App.chartSpecsStreet(streetFull);
  assert.ok(specs['street-trend'].stacked && specs['street-trend'].series.length === 3 && specs['street-trend'].labels[0] === '2026-07', 'trend chart oldest first');
  assert.ok(specs['street-eps'].series[0].kind === 'band' && specs['street-eps'].labels.join() === 'FY2023,FY2024,FY2026,FY2027' && specs['street-eps'].series[2].values[1] === 1.5 && specs['street-eps'].series[2].values[2] === 1.7, 'EPS consensus joins at the last filed FY');
  assert.ok(specs['street-epsg'].series[0].errors[2] && Math.abs(specs['street-epsg'].series[0].values[2] - (1.7 / 1.5 - 1)) < 1e-4, 'EPS growth vs last filed FY with low–high error bar');
  assert.ok(specs['street-track'].series[1].tips[1] === 'surprise -2.4%' && specs['street-track'].series[1].tips[0] === 'surprise +5.6%', 'surprise computed when missing, stored when given');
  assert.ok(specs['street-fan'] && specs['street-fan'].pts.length > 200 && specs['street-fan'].mean === 58 && specs['street-fan'].from === 45);
  Object.keys(specs).forEach((k) => { if (k === 'street-fan') return; const el = fakeEl(); App.drawChart(el, specs[k]); assert.ok(el.innerHTML.includes('<svg'), k + ' draws'); });
  const el = fakeEl(800, 260), r = App.drawFan(el, specs['street-fan']);
  assert.ok(el.innerHTML.includes('<svg') && el.innerHTML.includes('>$58.0</text>') && el.innerHTML.includes('>$44.0</text>') && el.innerHTML.includes('>$72.0</text>') && el.innerHTML.includes('Street target range'), 'fan tags and band');
  assert.equal(r.targets, 3); assert.ok(App.drawFan(fakeEl(), null) === null);
  const bare = App.renderForecastStreet(synthetic); assert.ok(bare.includes('fan chart appears once') && bare.includes('No actual-vs-consensus history'), 'graceful without prices / eps_history');
  const noEps = JSON.parse(JSON.stringify(synthetic)); noEps.profile.street.eps_forecast = null; assert.ok(App.renderForecastStreet(noEps).includes('No annual EPS consensus') && !App.chartSpecsStreet(noEps)['street-eps']);
  assert.ok(!App.renderForecastStreet(Object.assign({}, synthetic, { profile: { about: {} } })).includes('<table'), 'no street block → empty card only');
});
test('Analysts sub-tab: brokers, ratings history, momentum, PEG, upgrades / downgrades, honest note', () => {
  const a = App.renderForecastAnalysts(streetFull);
  ['Covering brokers', 'Alpha Securities', 'Beta Capital', '16 analysts in the consensus', 'Ratings history', 'Strong Buy', '<td class="num mono">16</td>', 'Estimate momentum', 'Current quarter', 'Q1 2026', '$0.41', '$0.39', '+5.1%', 'Current year', '+3.0%', 'Forward PEG', '1.42×', 'Upgrades / downgrades', '2026-09-15', 'Alpha Securities · upgrade · Hold → Buy · target $61.00', 'Beta Capital initiates at Buy', 'paid (TipRanks) data'].forEach((k) => assert.ok(a.includes(k), k));
  assert.ok(a.indexOf('2026-10-01') < a.indexOf('2026-07-01'), 'ratings history newest first');
  const bare = App.renderForecastAnalysts(synthetic);
  assert.ok(bare.includes('no broker list') && bare.includes('No estimate-revision momentum') && bare.includes('no upgrades or downgrades') && bare.includes('paid (TipRanks) data'), 'graceful without the extended keys');
  assert.ok(!bare.includes('<x-inj>'));
  const inj = App.renderForecastAnalysts(inject(streetFull)) + App.renderForecastStreet(inject(streetFull)) + App.renderStreet(inject(streetFull));
  assert.ok(!inj.includes('<x-inj>') && inj.includes('&lt;x-inj&gt;'), 'street renderers escape every string');
  const specs = App.chartSpecsStreet(inject(streetFull)); Object.keys(specs).forEach((k) => { if (k === 'street-fan') return; const el = fakeEl(); App.drawChart(el, specs[k]); assert.ok(!el.innerHTML.includes('<x-inj>'), k); });
});
/* ---- 2026-10-15: statements viewer (pure table model + renderer), watchlist merge, dividends review findings, CSS containment */
const stmFx = { ticker: 'FX', cik: 1, as_of: '2026-10-15', currency: 'USD', fiscal_year_end_mmdd: '0131', source: 'SEC EDGAR companyfacts (filing-direct)',
  latest_filed: { form: '10-Q', filed: '2026-09-18', period: '2026-08-15' },
  periods: { annual: [{ end: '2024-02-03', label: 'FY2024', filed: '2024-04-02' }, { end: '2025-02-01', label: 'FY2025', filed: '2025-04-01' }, { end: '2026-01-31', label: 'FY2026', filed: '2026-04-01' }],
    quarterly: [{ end: '2025-05-24', label: 'Q1 FY2026', fy_start: '2025-02-02', filed: '2025-06-20' }, { end: '2025-08-16', label: 'Q2 FY2026', fy_start: '2025-02-02', filed: '2025-09-19' }, { end: '2025-11-08', label: 'Q3 FY2026', fy_start: '2025-02-02', filed: '2025-12-05' }, { end: '2026-01-31', label: 'Q4 FY2026', fy_start: '2025-02-02', filed: '2026-04-01' }, { end: '2026-05-23', label: 'Q1 FY2027', fy_start: '2026-02-01', filed: '2026-06-19' }, { end: '2026-08-15', label: 'Q2 FY2027', fy_start: '2026-02-01', filed: '2026-09-18' }],
    ttm: { end: '2026-08-15', quarters: ['2025-11-08', '2026-01-31', '2026-05-23', '2026-08-15'] }, current: { end: '2026-08-15' } },
  statements: {
    income: [
      { key: 'revenue', label: 'Revenue', level: 0, total: true, unit: 'money', annual: [1.5e11, 1.47e11, 1.5e11], quarterly: [4.5e10, 3.4e10, 3.35e10, 3.75e10, 4.6e10, 3.5e10], ttm: 1.52e11, growth_annual: [null, -0.02, 0.0204], growth_quarterly: [null, null, null, null, 0.0222, 0.0294], derived_quarterly: [false, false, false, true, false, false], tags: ['Revenues'] },
      { key: 'cost_of_revenue', label: 'Cost of revenue', level: 1, total: false, unit: 'money', annual: [1.15e11, 1.13e11, 1.16e11], quarterly: [3.5e10, 2.6e10, 2.6e10, 2.9e10, 3.55e10, 2.7e10], ttm: 1.175e11, growth_annual: [null, -0.0174, 0.0265], growth_quarterly: [null, null, null, null, 0.0143, 0.0385], derived_quarterly: [false, false, false, true, false, false], tags: [] },
      { key: 'eps_diluted', label: 'EPS (diluted)', level: 0, total: true, unit: 'per_share', annual: [2.96, 3.67, 4.1], quarterly: [1.29, 0.84, 0.98, 0.99, 1.41, -0.1], ttm: 3.28, growth_annual: [null, 0.2399, 0.1172], growth_quarterly: [null, null, null, null, 0.093, null], derived_quarterly: [false, false, false, false, false, false], tags: [] },
      { key: 'shares_diluted', label: 'Shares outstanding (diluted, weighted)', level: 0, total: true, unit: 'shares', annual: [7.26e8, 7.3e8, 6.6e8], quarterly: [7.3e8, 7.3e8, 6.6e8, 6.5e8, 6.3e8, 6.08e8], ttm: 6.37e8, growth_annual: [null, 0.0055, -0.0959], growth_quarterly: [null, null, null, null, -0.137, -0.167], derived_quarterly: [false, false, false, true, false, false], tags: [] },
      { key: 'dps', label: 'Dividends per share', level: 0, total: false, unit: 'per_share', annual: [1.16, 1.26, 1.4], quarterly: [null, null, null, null, null, null], ttm: null, growth_annual: [null, 0.0862, 0.1111], growth_quarterly: [null, null, null, null, null, null], derived_quarterly: [false, false, false, false, false, false], tags: [] }],
    balance: [
      { key: 'cash', label: 'Cash & equivalents', level: 1, total: false, unit: 'money', annual: [1.9e9, 1.4e9, 4.6e9], quarterly: [5.1e9, 4.3e9, 4.4e9, 4.6e9, 2.1e9, 3.2e9], ttm: 3.2e9, growth_annual: [null, -0.263, 2.2857], growth_quarterly: [null, null, null, null, -0.588, -0.256], derived_quarterly: [false, false, false, false, false, false], tags: [] },
      { key: 'total_assets', label: 'Total assets', level: 0, total: true, unit: 'money', annual: [5.0e10, 5.3e10, 5.6e10], quarterly: [5.4e10, 5.3e10, 5.6e10, 5.6e10, 5.4e10, 5.5e10], ttm: 5.5e10, growth_annual: [null, 0.06, 0.0566], growth_quarterly: [null, null, null, null, 0, 0.0377], derived_quarterly: [false, false, false, false, false, false], tags: [] }],
    cashflow: [
      { key: 'ocf', label: 'Operating cash flow', level: 0, total: true, unit: 'money', cf_sign: 1, annual: [6.8e9, 5.8e9, 6.4e9], quarterly: [2.2e9, 1.3e9, 1.6e9, 1.3e9, 2.4e9, 1.4e9], ttm: 6.7e9, growth_annual: [null, -0.147, 0.1034], growth_quarterly: [null, null, null, null, 0.0909, 0.0769], derived_quarterly: [false, true, true, true, false, true], tags: [] },
      { key: 'capex', label: 'Capital expenditures', level: 1, total: false, unit: 'money', cf_sign: -1, annual: [3.9e9, 3.9e9, 4.0e9], quarterly: [1.2e9, 0.9e9, 1.0e9, 0.9e9, 1.1e9, 0.95e9], ttm: 3.95e9, growth_annual: [null, 0, 0.0256], growth_quarterly: [null, null, null, null, -0.0833, 0.0556], derived_quarterly: [false, true, true, true, false, true], tags: [] },
      { key: 'fcf', label: 'Free cash flow', level: 0, total: true, unit: 'money', cf_sign: 1, annual: [2.9e9, 1.9e9, 2.4e9], quarterly: [1.0e9, 0.4e9, 0.6e9, 0.4e9, 1.3e9, 0.45e9], ttm: 2.75e9, growth_annual: [null, -0.345, 0.263], growth_quarterly: [null, null, null, null, 0.3, 0.125], derived_quarterly: [false, true, true, true, false, true], tags: [] }],
    metrics: [
      { key: 'gross_margin', label: 'Gross margin', level: 0, total: false, unit: 'pct', annual: [0.2333, 0.2313, 0.2267], quarterly: [0.2222, 0.2353, 0.2239, 0.2267, 0.2283, 0.2286], ttm: 0.227, growth_annual: [null, null, null], growth_quarterly: [null, null, null, null, null, null], derived_quarterly: [false, false, false, false, false, false], tags: [] },
      { key: 'current_ratio', label: 'Current ratio', level: 0, total: false, unit: 'ratio', annual: [0.85, 0.9, 1.1], quarterly: [1.0, 0.95, 0.97, 1.1, 0.88, 0.92], ttm: 0.92, growth_annual: [null, null, null], growth_quarterly: [null, null, null, null, null, null], derived_quarterly: [false, false, false, false, false, false], tags: [] },
      { key: 'book_value_per_share', label: 'Book value per share', level: 0, total: false, unit: 'per_share', annual: [15.5, 16.2, 17.8], quarterly: [16.4, 16.8, 17.1, 17.8, 18.0, 18.4], ttm: 18.4, growth_annual: [null, 0.0452, 0.0988], growth_quarterly: [null, null, null, null, 0.0976, 0.0952], derived_quarterly: [false, false, false, false, false, false], tags: [] }] },
  warnings: ['debt_repaid: 1 derived quarter(s) (2011-01-29) came out negative — not shown'] };
test('statements model: columns newest first, TTM / Current placement, labels with period ends', () => {
  const a = App.stmColumns(stmFx, 'income', 'annual'); assert.deepEqual(a.map((c) => c.label), ['FY2026', 'FY2025', 'FY2024']); assert.deepEqual(a.map((c) => c.sub), ["Jan '26", "Feb '25", "Feb '24"]); assert.deepEqual(a.map((c) => c.i), [2, 1, 0]);
  const q = App.stmColumns(stmFx, 'income', 'quarterly'); assert.equal(q.length, 6); assert.equal(q[0].label, 'Q2 FY2027'); assert.equal(q[0].sub, "Aug '26"); assert.equal(q[5].label, 'Q1 FY2026');
  const t = App.stmColumns(stmFx, 'income', 'ttm'); assert.deepEqual(t.map((c) => c.label), ['TTM', 'FY2026', 'FY2025', 'FY2024']); assert.equal(t[0].sub, "to Aug '26"); assert.equal(t[0].src, 'ttm');
  const b = App.stmColumns(stmFx, 'balance', 'ttm'); assert.deepEqual(b.map((c) => c.label), ['Current', 'FY2026', 'FY2025', 'FY2024']); assert.equal(b[0].sub, "Aug '26");
  const noTtm = JSON.parse(JSON.stringify(stmFx)); noTtm.periods.ttm = null;
  assert.deepEqual(App.stmColumns(noTtm, 'cashflow', 'ttm').map((c) => c.label), ['FY2026', 'FY2025', 'FY2024'], 'no TTM column without four consecutive quarters');
  assert.equal(App.stmTable(noTtm, 'cashflow', 'ttm').ttmMissing, true);
  assert.deepEqual(App.stmColumns(noTtm, 'balance', 'ttm').map((c) => c.label), ['Current', 'FY2026', 'FY2025', 'FY2024'], 'balance keeps Current from periods.current');
  assert.deepEqual(App.stmColumns({}, 'income', 'annual'), []); assert.deepEqual(App.stmTable(null, 'income', 'annual').rows, []);
  assert.equal(App.monthYear('2025-12-31'), "Dec '25"); assert.equal(App.monthYear('bad'), 'bad');
});
test('statements model: money / shares / per-share / ratio / pct formats, indent + total flags, cash-flow sign, growth rows, derived daggers, empty rows dropped', () => {
  assert.equal(App.stmFmt('money', 5480717000), '5,481'); assert.equal(App.stmFmt('money', 4776000), '4.78'); assert.equal(App.stmFmt('money', -1026000000), '-1,026'); assert.equal(App.stmFmt('money', 99999999), '100', 'the 100 M switch is decided on the rounded value'); assert.equal(App.stmFmt('money', 99994999), '99.99'); assert.equal(App.stmFmt('money', 0), '0.00'); assert.equal(App.stmFmt('money', null), '–');
  assert.equal(App.stmFmt('shares', 337031000), '337'); assert.equal(App.stmFmt('shares', 75870706), '75.87'); assert.equal(App.stmFmt('per_share', 9.75), '9.75'); assert.equal(App.stmFmt('per_share', -0.58), '-0.58'); assert.equal(App.stmFmt('per_share', 3.456), '3.46');
  assert.equal(App.stmFmt('pct', 0.2333), '23.3%'); assert.equal(App.stmFmt('pct', -0.05), '-5.0%'); assert.equal(App.stmFmt('ratio', 0.9), '0.90'); assert.equal(App.stmFmt('ratio', 1.2345), '1.23');
  const M = App.stmTable(stmFx, 'income', 'annual', true);
  assert.deepEqual(M.rows.map((r) => r.key), ['revenue', 'cost_of_revenue', 'eps_diluted', 'shares_diluted', 'dps']);
  const rev = M.rows[0]; assert.equal(rev.level, 0); assert.equal(rev.total, true); assert.deepEqual(rev.cells.map((c) => c.text), ['150,000', '147,000', '150,000']); assert.deepEqual(rev.cells.map((c) => c.growthText), ['+2.0%', '-2.0%', '–']); assert.equal(rev.cells[0].growthCls, 'pos'); assert.equal(rev.hasGrowth, true);
  assert.equal(M.rows[1].level, 1); assert.equal(M.rows[1].total, false);
  assert.deepEqual(M.rows[2].cells.map((c) => c.text), ['4.10', '3.67', '2.96']); assert.deepEqual(M.rows[3].cells.map((c) => c.text), ['660', '730', '726']);
  const Q = App.stmTable(stmFx, 'income', 'quarterly', false);
  assert.deepEqual(Q.rows.map((r) => r.key), ['revenue', 'cost_of_revenue', 'eps_diluted', 'shares_diluted'], 'dps has no quarterly values → dropped from that view');
  assert.equal(Q.rows[0].cells[2].derived, true, 'Q4 FY2026 derived'); assert.equal(Q.rows[0].cells[0].derived, false); assert.equal(Q.anyDerived, true); assert.equal(Q.growth, false);
  assert.equal(Q.rows[2].cells[0].text, '-0.10', 'negative EPS with a leading minus'); assert.equal(Q.rows[2].cells[0].growthText, '–');
  const C = App.stmTable(stmFx, 'cashflow', 'ttm', true);
  assert.deepEqual(C.rows.map((r) => r.key), ['ocf', 'capex', 'fcf']);
  assert.deepEqual(C.rows[1].cells.map((c) => c.text), ['-3,950', '-4,000', '-3,900', '-3,900'], 'capex (cf_sign −1) shown as an outflow'); assert.equal(C.rows[1].sign, -1); assert.equal(C.rows[1].cells[0].raw, 3.95e9);
  assert.deepEqual(C.rows[0].cells.map((c) => c.text), ['6,700', '6,400', '5,800', '6,800']); assert.equal(C.rows[0].cells[0].growth, null, 'no growth on the TTM column'); assert.equal(C.rows[0].cells[1].growthText, '+10.3%');
  const B = App.stmTable(stmFx, 'balance', 'ttm'); assert.equal(B.rows[0].cells[0].text, '3,200', 'Current = latest quarter-end instant'); assert.equal(B.rows[0].cells[1].text, '4,600');
  const Mt = App.stmTable(stmFx, 'metrics', 'annual', true); assert.deepEqual(Mt.rows[0].cells.map((c) => c.text), ['22.7%', '23.1%', '23.3%']); assert.equal(Mt.rows[0].hasGrowth, false); assert.deepEqual(Mt.rows[1].cells.map((c) => c.text), ['1.10', '0.90', '0.85']); assert.equal(Mt.rows[2].cells[0].text, '17.80');
});
test('statements renderer: controls, sticky-first-column table, label buttons with aria-expanded, growth rows, dagger legend, units note, sparkline card, states', () => {
  const rec = { ticker: 'FX', score: { ticker: 'FX' } };
  const html = App.renderStatements(rec, { status: 'ready', data: stmFx, statement: 'income', period: 'quarterly', growth: true, line: 'revenue' });
  ['id="stmsec"', '<h2>Financial statements</h2>', 'class="seg stmseg"', 'data-stm="income" class="on"', 'data-stm="balance"', 'data-stm="cashflow"', 'data-stm="metrics"', 'class="seg stpseg"', 'data-stp="quarterly" class="on"', 'data-stp="ttm"', 'class="stm-growth" checked',
    'Millions USD. Fiscal year ends 01/31.', 'shares in millions; newest period first', '<table class="fin stm">', '<th class="stl0">Income statement</th>', '<span class="pl">Q2 FY2027</span><span class="sub">Aug &#39;26</span>',
    '<button type="button" class="stl" data-line="revenue" aria-expanded="true"', '<button type="button" class="stl" data-line="cost_of_revenue" aria-expanded="false"', 'class="l0 strong open" data-line="revenue"', 'class="l1" data-line="cost_of_revenue"',
    '<tr class="sub growth"><th>YoY growth</th>', '<td class="pos">+2.9%</td>', '†</sup>', '† derived quarter: year-to-date minus the prior year-to-date', 'id="stmspark"', '<b>Revenue</b>', 'by fiscal quarter · millions USD', 'class="stm-close"', 'data-cid="stm-spark"',
    'latest filing 10-Q filed 2026-09-18', 'class="stmwarn"', '1 build note'].forEach((k) => assert.ok(html.includes(k), k));
  assert.ok(html.indexOf('<span class="pl">Q2 FY2027</span>') < html.indexOf('<span class="pl">Q1 FY2026</span>'), 'newest first');
  assert.ok(html.indexOf('<table class="fin stm">') < html.indexOf('id="stmspark"'), 'sparkline card directly below the table');
  const cf = App.renderStatements(rec, { status: 'ready', data: stmFx, statement: 'cashflow', period: 'annual' });
  assert.ok(cf.includes('Cash outflows (capex, buybacks, dividends') && cf.includes('>-4,000</td>') && !cf.includes('class="sub growth"') && !cf.includes('id="stmspark"'), 'cash-flow note, outflow negatives, growth rows off, no chart without a line');
  const bal = App.renderStatements(rec, { status: 'ready', data: stmFx, statement: 'balance', period: 'ttm' }); assert.ok(bal.includes('<span class="pl">Current</span>') && bal.includes('"Current" is the latest quarter end'));
  assert.ok(App.renderStatements(rec, {}).includes('<tr class="loading"><th>Loading the full statements…</th>') && App.renderStatements(rec, { status: 'loading' }).includes('Loading the full statements'), 'idle / loading row');
  const emb = App.renderStatements(rec, { status: 'embedded', site: 'https://example.github.io/stocks/' }); assert.ok(emb.includes('The full statements are on the site') && emb.includes('href="https://example.github.io/stocks/#FX.financials"'), 'attachment: link to the site');
  const embNo = App.renderStatements(rec, { status: 'embedded' }); assert.ok(!/href=/.test(embNo.slice(embNo.indexOf('stmbody'))) && embNo.includes("open FX's Financials tab on the site"), 'attachment without meta.site_url: the sentence carries no (dead) relative link');
  assert.ok(html.includes('data-line="revenue" aria-expanded="true" aria-controls="stmspark"') && !html.includes('data-line="cost_of_revenue" aria-expanded="false" aria-controls'), 'the open line\'s button names the chart region it controls; closed lines do not point at a missing id');
  assert.ok(App.renderStatements(rec, { status: 'missing' }).includes('Full statements have not been built for FX yet') && App.renderStatements(rec, { status: 'error', error: 'HTTP 500' }).includes('could not be loaded (HTTP 500)'));
  const spec = App.stmSparkSpec(stmFx, 'cashflow', 'quarterly', 'capex');
  assert.deepEqual(spec.labels, ['Q1 FY2026', 'Q2 FY2026', 'Q3 FY2026', 'Q4 FY2026', 'Q1 FY2027', 'Q2 FY2027'], 'oldest first for the chart'); assert.deepEqual(spec.series[0].values, [-1.2e9, -0.9e9, -1.0e9, -0.9e9, -1.1e9, -0.95e9]); assert.equal(spec.series[0].kind, 'bar'); assert.equal(spec.yfmt, 'big');
  const sp2 = App.stmSparkSpec(stmFx, 'metrics', 'ttm', 'gross_margin'); assert.equal(sp2.labels.length, 3); assert.equal(sp2.series[0].kind, 'line'); assert.equal(sp2.yfmt, 'pct');
  const sh = App.stmSparkSpec(stmFx, 'income', 'annual', 'shares_diluted'); assert.equal(sh.yfmt, 'cnt'); const el = fakeEl(); App.drawChart(el, sh); assert.ok(el.innerHTML.includes('<svg') && el.innerHTML.includes('660.0M') && !el.innerHTML.includes('$660'), 'share counts drawn without a $');
  assert.equal(App.stmSparkSpec(stmFx, 'income', 'quarterly', 'dps'), null, 'no chart for a line without values in that periodicity'); assert.equal(App.stmSparkSpec(stmFx, 'income', 'annual', 'nope'), null);
  const fin = App.renderFinancials(synthetic, { status: 'ready', data: stmFx }); assert.ok(fin.indexOf('id="stmsec"') >= 0 && fin.indexOf('id="stmsec"') < fin.indexOf('<h2>Quarterly</h2>'), 'statements card above the existing quarterly / annual cards');
  assert.ok(App.renderCompanyHTML(synthetic, 'financials', null, null, { stm: { status: 'ready', data: stmFx } }).includes('id="stmsec"'));
  assert.ok(App.renderFinancials({ fundamentals: null, history: [] }, { status: 'missing' }).includes('id="stmsec"'), 'viewer card even without fundamentals');
  const inj = App.renderStatements(rec, { status: 'ready', data: inject(stmFx), statement: 'income', period: 'annual', growth: true, line: 'revenue<x-inj>' });
  assert.ok(!inj.includes('<x-inj>') && inj.includes('&lt;x-inj&gt;'), 'every statements string is escaped');
});
test('negative zero never prints: sign from the rounded text in stmFmt / fmtPct / fmtPts / fmtX / fmtMoney, over the fixture and every served statements file', () => {
  assert.equal(App.stmFmt('money', -4000), '0.00'); assert.equal(App.stmFmt('money', -1106), '0.00'); assert.equal(App.stmFmt('shares', -4999), '0.00'); assert.equal(App.stmFmt('pct', -0.0004), '0.0%'); assert.equal(App.stmFmt('ratio', -0.004), '0.00'); assert.equal(App.stmFmt('per_share', -0.004), '0.00');
  assert.equal(App.stmFmt('money', -5000), '-0.01', 'a value that rounds away from zero keeps its sign'); assert.equal(App.stmFmt('pct', -0.0005), '-0.1%'); assert.equal(App.stmFmt('money', -1026000000), '-1,026');
  assert.equal(App.fmtPct(-0.0004, 1, true), '+0.0%'); assert.equal(App.fmtPct(-0.0004), '0.0%'); assert.equal(App.fmtPct(-0.0006, 1, true), '-0.1%'); assert.equal(App.fmtPts(-0.04), '+0%'); assert.equal(App.fmtX(-0.04), '0.0×'); assert.equal(App.fmtMoney(-0.004), '$0.00'); assert.equal(App.fmtMoney(-0.006), '-$0.01');
  assert.equal(App.minus(-1, '0.00'), ''); assert.equal(App.minus(-1, '0.01'), '-'); assert.equal(App.minus(1, '0.01'), '');
  const negZero = /^-0(\.0+)?%?$/, bad = [];
  const scan = (data, name) => { App.STM_TABS.forEach(([st]) => App.STM_PERIODS.forEach(([pd]) => { App.stmTable(data, st, pd, true).rows.forEach((r) => r.cells.forEach((c) => { if (negZero.test(c.text)) bad.push(name + ' ' + st + ' ' + pd + ' ' + r.key + ' ' + c.text); if (negZero.test(c.growthText)) bad.push(name + ' ' + st + ' ' + pd + ' ' + r.key + ' growth ' + c.growthText); })); })); };
  const neg = JSON.parse(JSON.stringify(stmFx)); neg.statements.income[0].annual[0] = -1106; neg.statements.income[0].growth_annual[1] = -0.0004; neg.statements.metrics[0].annual[1] = -0.0005; neg.statements.cashflow[1].annual[2] = 3000;
  scan(neg, 'fixture'); assert.equal(App.stmTable(neg, 'income', 'annual', true).rows[0].cells[2].text, '0.00'); assert.equal(App.stmTable(neg, 'cashflow', 'annual').rows[1].cells[0].text, '0.00', 'a tiny outflow (cf_sign −1) is not "-0.00"');
  // every served data/<T>.statements.json; on a fresh clone (no data/), the committed <T>/statements.json they are copied from
  const dataDir = path.join(BUILT, 'data'); let files = 0;
  const served = fs.existsSync(dataDir) ? fs.readdirSync(dataDir).filter((f) => /\.statements\.json$/.test(f)).map((f) => path.join(dataDir, f)) : [];
  const own = served.length ? [] : fs.readdirSync(BASE).filter((d) => /^[A-Z][A-Z0-9.-]*$/.test(d)).map((d) => path.join(BASE, d, 'statements.json')).filter((p) => fs.existsSync(p));
  served.concat(own).forEach((p) => { files++; scan(JSON.parse(fs.readFileSync(p, 'utf8')), path.relative(BASE, p)); });
  if (!files) skip('negative-zero sweep over real statements files — none served or committed under ' + BASE);
  assert.deepEqual(bad, [], 'negative-zero cells in ' + files + (served.length ? ' served' : ' committed') + ' statements files');
});
test('company page re-mount keeps an open sparkline: companyCharts() carries the stm-spark spec; focusKey() names redrawn controls', () => {
  const rec = { ticker: 'FX', score: { ticker: 'FX' } };
  const withLine = App.companyCharts(rec, { status: 'ready', data: stmFx, statement: 'income', period: 'annual', line: 'revenue' });
  assert.ok('stm-spark' in withLine && withLine['stm-spark'].series[0].name === 'Revenue' && 'price' in withLine, 'the mounted chart map carries the open line');
  assert.ok(!('stm-spark' in App.companyCharts(rec, { status: 'ready', data: stmFx, line: null })) && !('stm-spark' in App.companyCharts(rec, { status: 'loading', line: 'revenue' })) && !('stm-spark' in App.chartSpecs(rec)), 'no spec without an open line / ready data');
  assert.ok(!('stm-spark' in App.companyCharts(rec, { status: 'ready', data: stmFx, statement: 'income', period: 'quarterly', line: 'dps' })), 'a line with no values in that periodicity has no spec (the card says so)');
  const page = App.renderCompanyHTML(synthetic, 'financials', null, null, { stm: { status: 'ready', data: stmFx, statement: 'income', period: 'annual', line: 'revenue' } });
  assert.ok(page.includes('data-cid="stm-spark"') && page.includes('class="l0 strong open" data-line="revenue"'), 'the page renders the open line, so the spec must be in the map');
  const el = (ds, cls, id) => ({ dataset: ds || {}, classList: { contains: (c) => (cls || []).indexOf(c) >= 0 }, id: id || '' });
  assert.equal(App.focusKey(el({ line: 'revenue' }, ['stl'])), 'button.stl[data-line="revenue"]'); assert.equal(App.focusKey(el({ stm: 'balance' })), '.stmseg button[data-stm="balance"]'); assert.equal(App.focusKey(el({ stp: 'ttm' })), '.stpseg button[data-stp="ttm"]');
  assert.equal(App.focusKey(el({}, ['stm-growth'])), '.stm-growth'); assert.equal(App.focusKey(el({}, ['stm-close'])), '.stm-close'); assert.equal(App.focusKey(el({ star: 'app' }, ['star'])), 'button.star[data-star="app"]'); assert.equal(App.focusKey(el({}, [], 'watchbtn')), '#watchbtn');
  assert.equal(App.focusKey(el({ sort: 'irr' })), null); assert.equal(App.focusKey(null), null); assert.equal(App.cssq('a"b\\c'), 'a\\"b\\\\c');
});
test('watchlist merge: repo (meta.watchlist ∪ row flags) + local stars, dedupe, order; repo star vs local star; header star; copy action', () => {
  const rows = [{ ticker: 'AAA', watchlist: true, irr: 0.2 }, { ticker: 'BBB', irr: 0.15 }, { ticker: 'CCC', irr: 0.1 }, { ticker: 'DDD', irr: 0.05 }];
  const metaW = { watchlist: ['ccc', 'ZZZ'] }, repo = App.repoList(metaW, rows);
  assert.deepEqual(repo, ['CCC', 'ZZZ', 'AAA'], 'meta.watchlist (normalised) then flagged rows');
  assert.equal(App.isRepo(rows[0], repo), true); assert.equal(App.isRepo(rows[2], repo), true); assert.equal(App.isRepo(rows[1], repo), false); assert.equal(App.isRepo(rows[1]), false);
  assert.deepEqual(App.watchTickers(rows, repo, ['ddd', 'DDD', 'bbb', 'QQQ', 'aaa']), ['AAA', 'BBB', 'CCC', 'DDD'], 'the ranked watched names in index order, deduped, upper-cased — exactly the count (QQQ / ZZZ have no row)');
  assert.deepEqual(App.watchTickers(rows, [], []), ['AAA'], 'a row flag alone marks the repo list'); assert.deepEqual(App.watchTickers(rows.slice(1), [], []), []); assert.deepEqual(App.watchTickers([], ['b', 'a'], ['a', 'c']), [], 'nothing ranked, nothing copied');
  assert.equal(App.watchTickers(rows, repo, ['bbb']).length, App.watchCount(rows, ['bbb'], repo), 'copy list length = the button count');
  assert.deepEqual(App.filterSortIndex(rows, { fit: 'all', watch: true }, [], repo).map((r) => r.ticker), ['AAA', 'CCC'], 'meta.watchlist marks rows even without the row flag');
  assert.deepEqual(App.filterSortIndex(rows, { fit: 'all', watch: true }, ['bbb'], repo).map((r) => r.ticker), ['AAA', 'BBB', 'CCC']);
  assert.equal(App.watchCount(rows, ['BBB'], repo), 3);
  assert.ok(App.starHTML(rows[2], [], repo).includes('class="star fixed repo"') && !App.starHTML(rows[2], [], repo).includes('<button'), 'repo star: fixed, drawn as repo, not a toggle');
  assert.ok(App.starHTML(rows[1], ['BBB']).includes('class="star on" data-star="BBB" aria-pressed="true"') && App.starHTML(rows[1], []).includes('aria-pressed="false"') && App.starHTML(rows[1], []).includes('☆'), 'local star toggle');
  const list = App.renderListHTML(metaW, rows, App.defaultState(), ['BBB']);
  assert.ok(list.includes('★ Watchlist <span class="mono">3</span>') && list.includes('id="copywl"') && list.includes('id="copyout"'), 'count includes meta.watchlist names and stars; copy action next to the toggle');
  assert.ok(list.indexOf('id="watchbtn"') < list.indexOf('id="copywl"') && list.indexOf('id="copywl"') < list.indexOf('id="fitseg"'));
  assert.ok(list.includes('class="star fixed repo"') && list.includes('class="star on" data-star="BBB"') && list.includes('class="star" data-star="DDD"'), 'rows: repo star, local star, plain toggle');
  const hero = App.renderHeader({ score: { ticker: 'BBB', name: 'B' }, row: rows[1] }, ['BBB'], repo); assert.ok(hero.includes('class="star on hstar" data-star="BBB" aria-pressed="true"'), 'company header star (local)');
  assert.ok(App.renderHeader({ score: { ticker: 'BBB', name: 'B' }, row: rows[1] }, [], repo).includes('class="star hstar" data-star="BBB" aria-pressed="false"'));
  const heroRepo = App.renderHeader({ score: { ticker: 'CCC', name: 'C' }, row: rows[2] }, [], repo); assert.ok(heroRepo.includes('★ Watchlist <span class="sub">repo</span>') && !heroRepo.includes('data-star='), 'repo name: chip, no toggle');
  assert.ok(App.renderHeader({ score: { ticker: 'CCC', name: 'C' } }, [], repo).includes('★ Watchlist'), 'repo chip from meta.watchlist alone (no row)');
  assert.ok(App.renderCompanyHTML(synthetic, 'overview', null, null, { stars: ['SYN'] }).includes('class="star on hstar" data-star="SYN"'));
});
test('dividends: payer decided from frequency + paid / DPS history (CCL, TKO shapes), filed DPS precision, share-basis meta line', () => {
  const base = Object.assign({}, synthetic.fundamentals.dividends);
  const mk = (over) => Object.assign({}, synthetic, { fundamentals: Object.assign({}, synthetic.fundamentals, { dividends: Object.assign({}, base, over) }) });
  const ccl = App.renderDividends(mk({ dps_ttm: null, dividend_yield: null, frequency: 'quarterly', dividends_paid_ttm: null, dps_basis: 'declared', history: [{ period_end: '2026-08-31', dps: 0.15, kind: 'declared' }, { period_end: '2026-05-31', dps: 0.15, kind: 'declared' }], annual_dps: [{ fy: '2020', period_end: '2020-11-30', dps: 0.5 }], notes: ['dps_ttm: the latest four quarterly DPS facts are not consecutive quarters'] }));
  assert.ok(!ccl.includes('>No dividend<') && ccl.includes('Pays a dividend — no trailing-twelve-month per-share figure') && ccl.includes('2 per-share facts filed, latest $0.15 (2026-08-31)') && ccl.includes('Quarterly') && ccl.includes('no TTM DPS — see notes'), 'CCL: quarterly payer with dps_ttm null is NOT "No dividend"');
  const tko = App.renderDividends(mk({ dps_ttm: null, dividend_yield: null, frequency: null, frequency_basis: null, dividends_paid_ttm: 240359000, dps_basis: 'paid', history: [], annual_dps: [{ fy: '2023', period_end: '2023-12-31', dps: 3.86 }], notes: ['frequency: payment frequency not inferable'] }));
  assert.ok(!tko.includes('>No dividend<') && tko.includes('Cash dividends paid TTM $240M') && tko.includes('latest full-year DPS $3.86 (FY2023)') && tko.includes('Not inferable') && tko.includes('per-share rate not tagged') && tko.includes('payment frequency not inferable'), 'TKO: frequency null + dividends paid renders as a payer with the note');
  const none = App.renderDividends(mk({ dps_ttm: null, dividend_yield: null, frequency: 'none', dividends_paid_ttm: null, history: [], annual_dps: [], notes: [] }));
  assert.ok(none.includes('>No dividend<') && none.includes('Buyback yield'), 'frequency none + nothing paid + no history = No dividend');
  const lapsed = App.renderDividends(mk({ dps_ttm: null, dividend_yield: null, frequency: 'none', dividends_paid_ttm: 0, history: [], annual_dps: [{ fy: '2015', period_end: '2015-12-31', dps: 1 }], notes: [] }));
  assert.ok(lapsed.includes('>No dividend<') && lapsed.includes('data-cid="div-dps"'), 'frequency none with an old history: no current dividend, history chart kept');
  assert.equal(App.fmtDps(0.155), '$0.155'); assert.equal(App.fmtDps(0.15), '$0.15'); assert.equal(App.fmtDps(1.375), '$1.375'); assert.equal(App.fmtDps(0.0375), '$0.0375'); assert.equal(App.fmtDps(1.4400000000000002), '$1.44'); assert.equal(App.fmtDps(3), '$3.00'); assert.equal(App.fmtDps(0.12345), '$0.1235'); assert.equal(App.fmtDps(null), '—'); assert.equal(App.fmtDps(-0.155), '-$0.155');
  const prec = App.renderDividends(mk({ history: [{ period_end: '2026-06-30', dps: 0.155, kind: 'declared' }, { period_end: '2026-03-31', dps: 0.1525, kind: 'declared' }] }));
  assert.ok(prec.includes('>$0.155</td>') && prec.includes('>$0.1525</td>') && !prec.includes('>$0.16</td>'), 'history keeps the filed precision');
  const metaLine = App.renderDividends(mk({ shares_source: 'dei:EntityCommonStockSharesOutstanding (10-Q filed 2026-09-18)', shares_outstanding: 590588700, shares_as_of: '2026-09-15', shares_diluted: 608000000, market_cap: 37260241083, market_cap_basis: '63.09 × 590,588,700 shares' }));
  assert.ok(metaLine.includes('Share basis: dei:EntityCommonStockSharesOutstanding (10-Q filed 2026-09-18) — 590.6M shares as of 2026-09-15 · market cap on that basis $37.26B (63.09 × 590,588,700 shares)') && metaLine.includes("the header's market cap uses the engine's diluted count"), 'meta line names the share basis and the market-cap basis');
  assert.equal(App.chartSpecsDividends(synthetic)['div-dps'].yfmt, 'dps');
  const qfin = App.renderFinancials(Object.assign({}, synthetic, { fundamentals: Object.assign({}, synthetic.fundamentals, { quarterly: synthetic.fundamentals.quarterly.map((q, i) => Object.assign({}, q, { dps_declared: i ? 0.155 : 0.1525 })) }) }));
  assert.ok(qfin.includes('>$0.155</td>') && qfin.includes('>$0.1525</td>'), 'quarterly DPS row keeps the filed precision');
  const still = App.renderDividends(synthetic); ['Dividend yield', 'Annual dividend', '$1.26', 'Payout frequency', 'Quarterly', 'Growth years', 'Buyback yield', 'Shareholder yield', 'Share basis:'].forEach((k) => assert.ok(still.includes(k), k));
});
test('ruling-sheet Q8: Financials labels the PP&E capex row and the FCF / OE that also deduct intangible purchases; prose and chart add up (GMED)', () => {
  // fundamentals.json fcf = OCF − PP&E capex − the engine's intangible leg; capex stays the PP&E leg (GMED FY2025)
  const gm = { fy: '2025', period_end: '2025-12-31', revenue: 2.9e9, ocf: 753447000, capex: 164679000, capex_intangibles: 9746000, sbc: 49779000, fcf: 579022000, oe_conservative: 529243000 };
  const rec = Object.assign({}, synthetic, { fundamentals: Object.assign({}, synthetic.fundamentals, { annual: [gm] }) });
  const fin = App.renderFinancials(rec);
  assert.ok(fin.includes('<th>Capex (PP&amp;E)</th>') && !fin.includes('<th>Capex</th>'), 'the capex rows are labelled PP&E (annual and quarterly)');
  assert.ok(fin.includes('<th>Free cash flow (OCF − PP&amp;E and intangible capex)</th>') && fin.includes("<th>Owner's earnings (FCF − SBC)</th>") && !fin.includes('Free cash flow (OCF − capex)'), 'FCF / OE labels name the intangible leg');
  assert.ok(fin.includes('Free cash flow = operating cash flow − PP&amp;E capex (the row above) − purchases of intangibles') && !fin.includes("Capex is the engine's"), 'the section note does not call the PP&E row the engine capex');
  const t = App.financialPerformance(rec);
  assert.ok(t.includes('PP&amp;E capex $165M') && t.includes('purchases of intangibles $10M') && t.includes("Owner's earnings (operating cash flow − PP&amp;E and intangible capex − stock-based compensation) were $529M"), t);
  const noInt = App.financialPerformance(synthetic); assert.ok(noInt.includes("Owner's earnings (operating cash flow − capex − stock-based compensation)") && !noInt.includes('purchases of intangibles'), 'no intangible leg: the plain wording');
  const cf = App.chartSpecsFinancials(rec)['fin-cf'], names = cf.series.map((x) => x.name);
  assert.deepEqual(names, ['Operating CF', 'Capex (PP&E)', 'Intangible capex', 'SBC', "Owner's earnings"]);
  const bars = cf.series.filter((x) => x.kind === 'bar').reduce((acc, x) => acc + x.values[0], 0);
  assert.equal(bars, gm.oe_conservative, 'the bars add up to the OE line');
  assert.deepEqual(App.chartSpecsFinancials(synthetic)['fin-cf'].series.map((x) => x.name), ['Operating CF', 'Capex (PP&E)', 'SBC', "Owner's earnings"], 'no intangible bar without the leg');
});
test('ruling-sheet Q8 bug 3: a non-USD dividends block prints no cross-currency share of the market cap and no $ on local-currency legs (TLK, RDY)', () => {
  // TLK (branch build): IDR legs, the USD market cap, every yield null — the caption had read "$17.68T (161,834.98%)"
  const base = Object.assign({}, synthetic.fundamentals.dividends);
  const tlk = Object.assign({}, base, { currency: 'IDR', dps_ttm: 312.5, dividend_yield: null, buyback_yield: null, net_buyback_yield: null, shareholder_yield: null,
    market_cap: 10926562490.98, dividends_paid_ttm: null, buybacks_ttm: null, issuance_ttm: null,
    legs: { dividends_paid: { value: 17683000000000 }, buybacks: { value: 0 }, share_issuance: { value: null } } });
  const rec = Object.assign({}, synthetic, { fundamentals: Object.assign({}, synthetic.fundamentals, { currency: 'IDR', dividends: tlk }) });
  const html = App.renderDividends(rec);
  assert.ok(!html.includes('161,834.98%') && !html.includes('$17.68T'), 'no cross-currency ratio, no $ on the IDR leg');
  assert.ok(html.includes('dividends paid IDR 17.68T + net buyback, ÷ market cap $10.93B (USD; the legs are in IDR, so no yield is computed)'), html.slice(html.indexOf('dividends paid'), html.indexOf('dividends paid') + 160));
  assert.ok(html.includes('IDR 312.50') && !html.includes('>$312.50<'), 'the IDR DPS carries its currency');
  // a USD block keeps its share of the market cap (HBAN's "3.04% paid" caption)
  const usd = App.renderDividends(synthetic); assert.ok(/dividends paid \$[\d.]+[MBK] \([\d.]+%\)/.test(usd), 'USD: the share of the cap is shown');
});
test('Q8 round 2: only a block\'s own currency key names the dividend amounts\' unit; a pre-rule non-USD block prints them bare (TLK, CX)', () => {
  // TLK / CX committed (pre-rule): file currency IDR / MXN, no dividends.currency — the legs are the filed USD facts
  const base = Object.assign({}, synthetic.fundamentals.dividends);
  const pre = Object.assign({}, base, { dps_ttm: null, dividend_yield: null, buyback_yield: null, net_buyback_yield: null, shareholder_yield: null,
    market_cap: 10926562490.98, legs: { dividends_paid: { value: 1099000000 }, buybacks: { value: 44000000 }, share_issuance: { value: null } } });
  delete pre.currency;
  const rec = Object.assign({}, synthetic, { fundamentals: Object.assign({}, synthetic.fundamentals, { currency: 'IDR', dividends: pre }) });
  const html = App.renderDividends(rec);
  assert.ok(!html.includes('IDR 1.10B') && !html.includes('the legs are in IDR') && !html.includes('IDR 44'), 'the file currency is not printed as the legs\' unit');
  assert.ok(html.includes('dividends paid 1.10B + net buyback') && html.includes('the legs\' currency is not recorded in this block'), html.slice(html.indexOf('dividends paid'), html.indexOf('dividends paid') + 200));
  assert.ok(html.includes('this block was written before 2026-10-19') && html.includes('may be USD or IDR'), 'the notes say the unit is unrecorded');
  assert.deepEqual(App.divCurrency(rec.fundamentals), { cur: null, recorded: false, file: 'IDR' });
  // a block that records its unit keeps the code; a USD file keeps the $
  assert.deepEqual(App.divCurrency({ currency: 'INR', dividends: { currency: 'INR' } }), { cur: 'INR', recorded: true, file: 'INR' });
  assert.equal(App.divCurrency(synthetic.fundamentals).cur, 'USD');
});
test('Q8 round 2: the dividend-per-share chart prints the block\'s currency, not $ (RDY INR 40.00)', () => {
  const mk = (fund) => { const el = { clientWidth: 600, innerHTML: '' }; App.drawChart(el, App.chartSpecsDividends({ fundamentals: fund })['div-dps']); return el.innerHTML; };
  const inr = mk({ currency: 'INR', dividends: { currency: 'INR', annual_dps: [{ fy: '2023', dps: 30 }, { fy: '2024', dps: 40 }] } });
  assert.ok(!inr.includes('$'), 'no $ in the ticks or tooltips of an INR chart');
  assert.ok(inr.includes('INR\u00a040.00') && inr.includes('FY2024 · Dividend per share: INR\u00a040.00'), inr.slice(0, 400));
  const pre = mk({ currency: 'INR', dividends: { annual_dps: [{ fy: '2024', dps: 40 }] } });
  assert.ok(!pre.includes('$') && !pre.includes('INR') && pre.includes('Dividend per share: 40.00'), 'a pre-rule block: bare amounts');
  const usd = mk({ currency: 'USD', dividends: { annual_dps: [{ fy: '2024', dps: 1.26 }] } });
  assert.ok(usd.includes('Dividend per share: $1.26'), 'USD unchanged');
});
test('Q8 round 2: the Forecast tab OE-history note names the intangible leg when a plotted year deducts one (BBIO)', () => {
  const bb = { fy: '2025', period_end: '2025-12-31', ocf: -445910000, capex: 1097000, sbc: 133024000, fcf: -455502000, oe_conservative: -588526000, shares_diluted: 190000000, oe_per_share: -3.0975 };
  const rec = { fundamentals: { currency: 'USD', annual: [bb] }, numbers: {}, score: {} };
  const html = App.renderForecastDCF(rec);
  assert.ok(html.includes('operating cash flow − PP&amp;E and intangible capex − stock-based compensation') && !html.includes('operating cash flow − capex −'), html.slice(0, 400));
  const plain = App.renderForecastDCF({ fundamentals: { currency: 'USD', annual: [Object.assign({}, bb, { fcf: -447007000, oe_conservative: -580031000, oe_per_share: -3.0528 })] }, numbers: {}, score: {} });
  assert.ok(plain.includes('operating cash flow − capex − stock-based compensation'), 'no intangible leg: the plain wording');
});
test('app.css: every wide element is contained — no horizontal page scroll at phone width (Segments table included)', () => {
  const css = fs.readFileSync(path.join(SITE, 'app.css'), 'utf8');
  assert.ok(/\.twrap\{[^}]*overflow-x:auto/.test(css), '.twrap scrolls horizontally');
  assert.ok(/\.pane\{[^}]*min-width:0[^}]*overflow-x:clip/.test(css), 'tab panes clip horizontal overflow (nothing inside a pane can widen the page)');
  assert.ok(/\.card\{[^}]*min-width:0;max-width:100%/.test(css), 'cards never exceed their container');
  const wide = []; const re = /([^{}]+)\{[^}]*?min-width:(\d+)px[^}]*\}/g; let m; while ((m = re.exec(css))) { if (+m[2] > 320) wide.push(m[1].trim().split(/\s*\n\s*|\*\/\s*/).pop().trim()); }
  assert.ok(wide.length >= 2, 'the ranking and statement tables keep their minimum widths: ' + wide.join(' | '));
  wide.forEach((sel) => assert.ok(/^(table\.fin|#t)$/.test(sel), 'a min-width above 320px only on a table that lives inside .twrap: ' + sel));
  assert.ok(!/table\.fin th\{[^}]*position:sticky/.test(css) && /table\.fin tbody th,table\.fin thead th:first-child\{[^}]*position:sticky/.test(css), 'sticky only on the row-label column, not on every header cell');
  assert.ok(/\.chart svg,\.pchart svg,\.fanchart svg\{max-width:100%\}/.test(css), 'svg never wider than its box');
  assert.ok(/table\.stm th:first-child,table\.stm tbody th\{[^}]*white-space:normal/.test(css), 'statement labels wrap instead of widening the sticky column');
  assert.ok(/\.star\.repo\{[^}]*color:#7AA2FF/.test(css) && /\.star\.on\{color:var\(--warn\)\}/.test(css), 'repo star and local star are drawn differently');
  // the sticky label cell of a total row is opaque: no rule on a "tr.strong th" sets a translucent (rgba) background
  assert.ok(/--cardstrong:#[0-9A-Fa-f]{6}/.test(css) && /table\.fin tr\.strong th\{[^}]*background:var\(--cardstrong\)/.test(css), 'total-row label cells get the opaque blended card colour');
  const rules = /([^{}]+)\{([^}]*)\}/g; let r; while ((r = rules.exec(css))) { const sels = r[1].split(',').map((x) => x.trim()); if (sels.some((x) => /tr\.strong th/.test(x))) assert.ok(!/background:rgba\(/.test(r[2]), 'translucent background on a sticky total label: ' + r[1].trim()); }
  // controls wider than a phone wrap instead of being clipped by the pane: the price-range strip and the statement segment
  assert.ok(/\.ranges\{[^}]*display:flex;flex-wrap:wrap/.test(css) && /\.pcbar>\*\{min-width:0;max-width:100%\}/.test(css), 'the 1D … Max strip wraps (5Y / Max stay tappable at 375px)');
  assert.ok(/\.stmbar \.seg\{flex-wrap:wrap;max-width:100%;min-width:0\}/.test(css) && /\.stmbar \.seg button\{flex:1 1 auto\}/.test(css), 'Income · Balance sheet · Cash flow · Metrics wraps inside a phone-width card');
});

/* ---- 2026-10-15: price chart — stockanalysis-style ranges, intraday 1D / 5D, crosshair geometry, period return */
const pxFx = (() => { // a record-shaped price spec: 288 weekly closes, 255 daily closes ending 2026-10-14, one complete session + today's partial one
  const w = [], d = [];
  for (let i = 0; i < 288; i++) { const dt = new Date(Date.UTC(2021, 3, 9) + i * 7 * 864e5); w.push([dt.toISOString().slice(0, 10), 60 + Math.sin(i / 20) * 20 + i / 8]); }
  for (let i = 0; d.length < 255; i++) { const dt = new Date(Date.UTC(2026, 9, 14) - i * 864e5); if (dt.getUTCDay() === 0 || dt.getUTCDay() === 6) continue; d.unshift([dt.toISOString().slice(0, 10), 250 + Math.cos(i / 15) * 20 - i / 20]); } // 255 trading days back (to mid-October 2025)
  const bars = (from, to, step, p0) => { const o = []; for (let m = from; m <= to; m += step) o.push([m, Math.round((p0 + Math.sin(m / 37) * 3) * 100) / 100]); return o; };
  const full = { session_date: '2026-10-14', prev_close: 272.28, close: 262.19, complete: true, bars: bars(240, 1195, 5, 265) };          // legacy start-keyed day: 955 = 15:55–15:59, 960 = 16:00–16:04
  const today = { session_date: '2026-10-15', prev_close: 262.19, close: null, complete: false, bar_key: 'end', bars: bars(240, 540, 5, 258) }; // pre-market capture at 08:56
  const intraday = Object.assign({ tz: 'America/New_York', regular_open: '09:30', regular_close: '16:00', prev_close_source: 'daily close 2026-10-14', last: 257.67, last_time: '08:56', source: 'api.nasdaq.com chart (no dates)' }, today);
  return { spec: { iv15: 376.12, iv12: 535.47, lo: 134, hi: 640, bear: 183, bull: 420, h20: 290.1, h25: 230.4, price: 262.19, pdate: '2026-10-14', w: w, d: d, src: 'test', asof: '2026-10-14', intraday: intraday, sessions: [full, today] }, w, d, full, today, intraday };
})();
test('price ranges: every range selects the right series and x unit; missing intraday disables 1D / 5D; default 1Y → 5Y → first available', () => {
  const S = pxFx.spec, sel = (r) => App.selectRange(S, r);
  assert.deepEqual(App.PRICE_RANGES, ['1D', '5D', '1M', 'YTD', '3M', '6M', '1Y', '5Y', 'MAX']);
  const one = sel('1D'); assert.equal(one.kind, 'intraday'); assert.equal(one.pts.length, pxFx.today.bars.length); assert.equal(one.pts[0].t, 240); assert.equal(one.pts[one.pts.length - 1].t, 540, 'x = minutes since midnight ET');
  assert.equal(one.prevClose, 262.19); assert.equal(one.base, 262.19); assert.equal(one.baseLabel, 'prev close'); assert.deepEqual(one.domain, [240, 1200], 'the full 4:00 AM – 8:00 PM session window even for a pre-market capture');
  assert.deepEqual(one.shade, [[240, 570], [960, 1200]], 'pre-market = before 09:30, after-hours = after 16:00 (end-keyed rule)');
  assert.ok(one.ticks.some((t) => t[1] === '10 am') && one.ticks.some((t) => t[1] === '12 pm') && one.ticks.some((t) => t[1] === '2 pm') && one.ticks.some((t) => t[1] === '4 pm'), 'x labels as times');
  assert.equal(one.pts[0].label, '4:00 AM ET · Thu Oct 15, 2026'); assert.equal(one.from, '4:00 AM ET'); assert.equal(one.to, '8:56 AM ET', 'a live session ends at its last print (intraday.last_time), not the last bucket end'); assert.equal(one.complete, false); assert.equal(one.partial, 1);
  const five = sel('5D'); assert.equal(five.kind, 'sessions'); assert.equal(five.sessions.length, 2); assert.equal(five.pts.length, pxFx.full.bars.length + pxFx.today.bars.length);
  assert.equal(five.sessions[0].x0, 0); assert.equal(five.sessions[1].x0, 960 + 90, 'sessions laid out end to end with a 90-minute visual gap'); assert.deepEqual(five.seps, [960 + 45]); assert.equal(five.domain[1], 2 * 960 + 90);
  assert.ok(five.pts.some((p) => p.brk), 'the second session starts a new line segment'); assert.equal(five.pts.filter((p) => p.brk).length, 1);
  assert.deepEqual(five.ticks.map((t) => t[1]), ['Wed Oct 14', 'Thu Oct 15'], 'a weekday-date label per session'); assert.deepEqual(five.ticks.map((t) => t[3]), ['Wed 14', 'Thu 15'], 'short labels for narrow charts');
  assert.equal(five.base, 272.28, 'return base = the close before the oldest session'); assert.equal(five.baseLabel, 'close before 2026-10-14'); assert.equal(five.partial, 1); assert.equal(five.complete, false); assert.equal(five.sessions[0].complete, true);
  assert.equal(five.shade.length, 4, 'two shaded regions per session'); assert.deepEqual(five.shade[2], [1050, 1050 + 330]);
  const closeAt = five.pts.filter((p) => p.t === 960 - 240 && !p.brk); assert.equal(closeAt.length, 1); assert.equal(closeAt[0].v, 262.19, 'the complete session ends its regular segment at the filed close');
  assert.ok(five.pts[five.pts.length - 1].label.includes('(partial capture)'), 'partial session points say so in the crosshair label');
  ['1M', '3M', '6M', 'YTD', '1Y'].forEach((r) => { const s = sel(r); assert.equal(s.kind, 'daily', r); assert.equal(s.pts[s.pts.length - 1].iso, '2026-10-14'); assert.equal(s.base, s.pts[0].v); assert.ok(s.pts.every((p, i) => !i || p.t > s.pts[i - 1].t), 'ascending'); });
  assert.ok(sel('1M').pts.length >= 20 && sel('1M').pts.length <= 24, '1M ≈ 22 trading days: ' + sel('1M').pts.length);
  assert.ok(sel('3M').pts.length > sel('1M').pts.length && sel('6M').pts.length > sel('3M').pts.length && sel('1Y').pts.length > sel('6M').pts.length);
  assert.equal(sel('1Y').pts.length, pxFx.d.length, '1Y = the whole daily series when no close sits at or before the 365-day reference date (the fixture starts after it)'); assert.equal(sel('1Y').priorBase, false);
  assert.equal(sel('1M').priorBase, true); assert.equal(sel('1M').baseDate, '2026-09-14', '1M opens at the close at or before 30 days back (prices.py\'s ret_1m_pct reference)'); assert.equal(sel('3M').baseDate, '2026-07-15'); assert.equal(sel('6M').baseDate, '2026-04-15');
  assert.ok(sel('1M').ticks.every((t) => t[0] >= sel('1M').pts[0].t), 'ticks only inside the window');
  assert.ok(sel('1M').ticks.every((t) => /^[A-Z][a-z]{2} \d{1,2}$/.test(t[1])), '1M ticks are "Oct 6"-style dates'); assert.ok(sel('1Y').ticks.some((t) => t[1] === "Jan '26") && sel('1Y').ticks.some((t) => t[1] === 'Nov'), '1Y ticks are months, January carries the year');
  ['5Y', 'MAX'].forEach((r) => { const s = sel(r); assert.equal(s.kind, 'weekly', r); assert.ok(s.ticks.every((t) => /^\d{4}$/.test(t[1])), 'year ticks'); });
  assert.equal(sel('MAX').pts.length, pxFx.w.length); assert.equal(sel('MAX').priorBase, false);
  const fiveY = sel('5Y'); assert.ok(fiveY.pts.length < pxFx.w.length && fiveY.priorBase && fiveY.pts[0].iso <= '2021-10-14' && fiveY.pts[1].iso > '2021-10-14', '5Y opens at the weekly close at or before 1,826 days back: ' + fiveY.pts[0].iso);
  assert.ok(fiveY.ticks.every((t) => t[1] !== '2021' || t[0] >= Date.UTC(2021, 9, 14)), 'no tick on the base row before the window');
  assert.equal(sel('3Y'), null, 'unknown range → null'); assert.equal(sel(''), null); assert.equal(App.selectRange(null, '1Y'), null);
  const avail = App.priceRanges(S); assert.ok(App.PRICE_RANGES.every((r) => avail[r] === true), 'every range available on the full fixture'); assert.equal(App.defaultRange(S), '1Y');
  const noIntra = Object.assign({}, S, { intraday: null, sessions: [] }); assert.equal(App.selectRange(noIntra, '1D'), null); assert.equal(App.selectRange(noIntra, '5D'), null);
  const a2 = App.priceRanges(noIntra); assert.equal(a2['1D'], false); assert.equal(a2['5D'], false); assert.equal(a2['1Y'], true); assert.equal(App.defaultRange(noIntra), '1Y');
  assert.equal(App.selectRange(Object.assign({}, S, { intraday: { bars: [[240, 1]] } }), '1D'), null, 'one bar is not a chart');
  assert.equal(App.selectRange(Object.assign({}, S, { sessions: [{ session_date: '2026-10-15', bars: 'nope' }, null, 7] }), '5D'), null, 'malformed sessions → not captured');
  const weeklyOnly = Object.assign({}, S, { d: [], intraday: null, sessions: [] }); assert.equal(App.defaultRange(weeklyOnly), '5Y', 'the attachment (no daily series) opens on 5Y');
  assert.equal(App.selectRange(weeklyOnly, '1Y').kind, 'weekly', '1Y falls back to weekly closes without a daily series'); assert.equal(App.selectRange(weeklyOnly, '1M').kind, 'weekly');
  assert.equal(App.defaultRange({ w: [], d: [] }), null); assert.equal(App.defaultRange({}), null);
  assert.equal(App.defaultRange({ intraday: pxFx.intraday }), '1D', 'intraday alone: the first range that has data');
  assert.deepEqual(App.cleanBars([[240, '1.5'], ['x', 1], [250], null, [260, 2]]), [[240, 1.5], [260, 2]]);
});
test('YTD opens at the last close of the prior year (the base, as prices.py\'s ret_ytd_pct) and runs through the year', () => {
  const ytd = App.selectRange(pxFx.spec, 'YTD');
  assert.equal(ytd.kind, 'daily'); assert.equal(ytd.pts[0].iso, '2025-12-31', 'the base row opens the window: ' + ytd.pts[0].iso); assert.equal(ytd.priorBase, true); assert.equal(ytd.baseDate, '2025-12-31');
  assert.ok(ytd.pts[1].iso >= '2026-01-01' && ytd.pts[1].iso <= '2026-01-03', 'then the first row of the year (the fixture has no holiday calendar): ' + ytd.pts[1].iso);
  assert.ok(ytd.pts.slice(1).every((p) => p.iso.slice(0, 4) === '2026')); assert.equal(ytd.pts[ytd.pts.length - 1].iso, '2026-10-14');
  assert.ok(ytd.pts.length < App.selectRange(pxFx.spec, '1Y').pts.length && ytd.pts.length > App.selectRange(pxFx.spec, '6M').pts.length, 'YTD (9.5 months) sits between 6M and 1Y');
  const dec = pxFx.d.filter((r) => r[0] >= '2025-12-01' && r[0] < '2026-01-01'); assert.ok(dec.length > 15 && ytd.pts.filter((p) => p.iso.slice(0, 7) === '2025-12').length === 1, 'of the December closes only the base (Dec 31) is drawn');
  assert.ok(!ytd.ticks.some((t) => t[1] === 'Dec') && ytd.ticks[0][1] === "Jan '26", 'no December tick on the base row: ' + ytd.ticks.map((t) => t[1]).join(','));
  const jan2 = { w: [], d: [['2025-12-30', 10], ['2025-12-31', 11], ['2026-01-02', 12], ['2026-01-05', 13]] };
  const y2 = App.selectRange(jan2, 'YTD'); assert.deepEqual(y2.pts.map((p) => p.iso), ['2025-12-31', '2026-01-02', '2026-01-05']); assert.equal(y2.base, 11, 'return base = the Dec 31 close, so Jan 2\'s move counts');
  assert.ok(Math.abs(App.periodReturn(y2.base, y2.last) - (13 / 11 - 1) * 100) < 1e-12);
  const one = App.selectRange({ w: [], d: [['2025-12-31', 11], ['2026-01-02', 12]] }, 'YTD'); assert.ok(one && one.pts.length === 2 && one.base === 11, 'the base plus one January close is already a chart');
  const dec31 = App.selectRange({ w: [], d: [['2025-12-30', 10], ['2025-12-31', 11]] }, 'YTD'); assert.ok(dec31 && dec31.priorBase === false && dec31.base === 10, 'a series ending Dec 31: nothing at or before the prior Dec 31 → first-close fallback (prices.py emits no ret_ytd_pct either)');
  const noPrior = App.selectRange({ w: [], d: [['2026-01-02', 12], ['2026-01-05', 13], ['2026-01-06', 14]] }, 'YTD'); assert.equal(noPrior.pts.length, 3); assert.equal(noPrior.priorBase, false); assert.equal(noPrior.base, 12, 'no close before the window → the first close is the base');
  assert.deepEqual(App.RANGE_DAYS, { '1M': 30, '3M': 91, '6M': 182, '1Y': 365, '5Y': 1826 }, 'prices.py stats() reference distances');
  Object.keys(loaded).forEach((t) => { // the pill must equal prices.stats.ret_*_pct wherever the served daily series reaches the reference close
    const spec = App.priceSpec(loaded[t].record), st = (loaded[t].record.prices || {}).stats || {}; if (App.selectRange(spec, '1M') === null || App.selectRange(spec, '1M').kind !== 'daily') return;
    [['1M', 'ret_1m_pct'], ['3M', 'ret_3m_pct'], ['6M', 'ret_6m_pct'], ['YTD', 'ret_ytd_pct'], ['1Y', 'ret_1y_pct']].forEach(([rg, k]) => {
      const sel = App.selectRange(spec, rg); if (!sel || !sel.priorBase || typeof st[k] !== 'number') return;
      const r = App.drawPrice(fakeEl(800, 280), spec, { range: rg }); assert.ok(Math.abs(Math.round(r.pct * 100) / 100 - st[k]) < 0.011, t + ' ' + rg + ' pill ' + r.pct.toFixed(2) + ' vs stats ' + st[k]);
    });
  });
});
test('nearest-point snapping, period-return math, the 1D minute-to-x mapping, range formatting', () => {
  const xs = [10, 20, 30, 45, 100];
  assert.equal(App.nearestIndex(xs, -5), 0); assert.equal(App.nearestIndex(xs, 10), 0); assert.equal(App.nearestIndex(xs, 14), 0); assert.equal(App.nearestIndex(xs, 15), 0, 'a tie snaps to the earlier point'); assert.equal(App.nearestIndex(xs, 16), 1);
  assert.equal(App.nearestIndex(xs, 37), 2); assert.equal(App.nearestIndex(xs, 38), 3); assert.equal(App.nearestIndex(xs, 99), 4); assert.equal(App.nearestIndex(xs, 1e9), 4); assert.equal(App.nearestIndex([], 5), -1); assert.equal(App.nearestIndex([7], 0), 0); assert.equal(App.nearestIndex(null, 1), -1);
  const big = []; for (let i = 0; i < 2000; i++) big.push(i * 3); for (let k = 0; k < 2000; k += 97) assert.equal(App.nearestIndex(big, k * 3 + 1), k, 'binary search over 2000 points');
  assert.ok(Math.abs(App.periodReturn(100, 110) - 10) < 1e-12); assert.ok(Math.abs(App.periodReturn(272.28, 257.67) - (257.67 / 272.28 - 1) * 100) < 1e-12); assert.equal(App.periodReturn(50, 50), 0); assert.equal(App.periodReturn(0, 5), null, 'no ratio on a zero base'); assert.equal(App.periodReturn(-1, 5), null); assert.equal(App.periodReturn(null, 5), null); assert.equal(App.periodReturn('100', '125'), 25);
  assert.equal(App.fmtRange(12.345), '+12.3%'); assert.equal(App.fmtRange(-0.456), '-0.46%'); assert.equal(App.fmtRange(234.5), '+235%'); assert.equal(App.fmtRange(0), '+0.00%'); assert.equal(App.fmtRange(null), ''); assert.equal(App.fmtRange(-9.99), '-9.99%'); assert.equal(App.fmtRange(-10), '-10.0%');
  const L = 56, PW = 600, dom = [240, 1200];
  assert.equal(App.minuteToX(240, dom, L, PW), L, '4:00 AM at the left edge'); assert.equal(App.minuteToX(1200, dom, L, PW), L + PW, '8:00 PM at the right edge'); assert.ok(Math.abs(App.minuteToX(720, dom, L, PW) - (L + PW / 2)) < 1e-9, 'noon in the middle');
  assert.ok(Math.abs(App.minuteToX(570, dom, L, PW) - (L + PW * 330 / 960)) < 1e-9, '9:30 open'); assert.ok(Math.abs(App.minuteToX(960, dom, L, PW) - (L + PW * 720 / 960)) < 1e-9, '4:00 close');
  assert.equal(App.xScale(5, 5, 5, L, PW), L, 'a degenerate domain does not divide by zero');
  assert.equal(App.timeLabel(570), '9:30 AM'); assert.equal(App.timeLabel(720), '12:00 PM'); assert.equal(App.timeLabel(960), '4:00 PM'); assert.equal(App.timeLabel(1195), '7:55 PM'); assert.equal(App.timeLabel(0), '12:00 AM'); assert.equal(App.timeLabel(600, true), '10 am'); assert.equal(App.timeLabel(720, true), '12 pm');
  assert.equal(App.dayLabel(App.isoParts('2026-10-14'), 'long'), 'Wed Oct 14, 2026'); assert.equal(App.dayLabel(App.isoParts('2026-10-14'), 'dow'), 'Wed Oct 14'); assert.equal(App.dayLabel(App.isoParts('2026-10-14'), 'short'), 'Wed 14'); assert.equal(App.dayLabel(App.isoParts('2026-10-14'), 'md'), 'Oct 14'); assert.equal(App.dayLabel(null), ''); assert.equal(App.isoParts('14/10/2026'), null);
  assert.equal(App.priceTag(1234.56), '1235'); assert.equal(App.priceTag(262.19), '262.2'); assert.equal(App.priceTag(15.104), '15.10');
});
test('session bars: end-keyed and legacy start-keyed days drawn as-is, the filed close placed at 16:00 only when the capture reached it, completeness derived for legacy entries', () => {
  assert.deepEqual(App.sessionBars([[250, 2], [240, 1], [250, 3], [1195, 9]], null), [[240, 1], [250, 3], [1195, 9]], 'sorted, the later duplicate of a key wins');
  assert.deepEqual(App.sessionBars([[955, 10], [960, 10.3], [965, 10.5]], 10.1), [[955, 10], [960, 10.1], [965, 10.5]], 'the official close replaces the 16:00 bucket');
  assert.deepEqual(App.sessionBars([[955, 10], [965, 10.5]], 10.1), [[955, 10], [960, 10.1], [965, 10.5]], 'inserted in order when no bar is keyed 960');
  assert.deepEqual(App.sessionBars([[540, 10], [545, 10.2]], 10.1), [[540, 10], [545, 10.2]], 'a session that stopped before 16:00 gets no close point (nothing captured between)');
  assert.deepEqual(App.sessionBars([[955, 10], [960, 10.3]], 'n/a'), [[955, 10], [960, 10.3]], 'a non-numeric close changes nothing'); assert.deepEqual(App.sessionBars(null, 5), []);
  assert.equal(App.sessionComplete({ complete: true }, [[240, 1]]), true); assert.equal(App.sessionComplete({ complete: false }, [[1195, 1]]), false, 'the block\'s own flag wins');
  assert.equal(App.sessionComplete({}, [[240, 1], [1195, 2]]), true, 'legacy entry: derived from the last bar ≥ 19:55'); assert.equal(App.sessionComplete({}, [[240, 1], [1190, 2]]), false); assert.equal(App.sessionComplete({}, []), false);
});
test('drawPrice 1D / 5D: tight axis, extended-hours shading, the previous-close dashed line, no valuation overlays, crosshair group + geometry; daily ranges keep the overlays', () => {
  const S = pxFx.spec; let el = fakeEl(900, 280), r = App.drawPrice(el, S, { range: '1D', showIv: true, showBand: true, showH: true });
  const h = el.innerHTML;
  assert.equal(r.kind, 'intraday'); assert.equal(r.range, '1D'); assert.equal(r.partial, 1); assert.ok(Math.abs(r.pct - (pxFx.today.bars[pxFx.today.bars.length - 1][1] / 262.19 - 1) * 100) < 1e-9, 'period return vs the previous close');
  assert.ok(/^1D: [+-][\d.]+% \(4:00 AM ET → 8:56 AM ET\) · vs prev close \$262\.19 · partial session \(captured to 8:56 AM ET\)$/.test(r.text), r.text);
  assert.ok(h.includes('class="pcl"') && h.includes('stroke-dasharray="4 4"') && h.includes('Prev close $262.19'), 'previous-close dashed line with its value');
  assert.equal((h.match(/<rect class="ext"/g) || []).length, 2, 'pre-market and after-hours shading'); assert.ok(h.includes('<title>Extended hours</title>'));
  assert.ok(!h.includes('>IV</text>') && !h.includes('>20%</text>') && !h.includes('Scenario range'), 'valuation overlays hidden on an intraday range even when toggled on');
  assert.ok(h.includes('class="xt"') && h.includes('>10 am</text>') && h.includes('>4 pm</text>') && h.includes('>12 pm</text>'), 'time x-labels');
  assert.ok(h.includes('<g class="xh" style="display:none"') && h.includes('class="xv"') && h.includes('class="xhl"') && h.includes('class="xd"') && h.includes('class="xtr"') && h.includes('class="xlr"'), 'hidden crosshair parts: vertical + horizontal guides, dot, right-edge tag, floating label');
  const g = el._pcGeom; assert.ok(g && g.xs.length === pxFx.today.bars.length && g.xs.every((x, i) => !i || x > g.xs[i - 1]), 'geometry left on the element for the crosshair, ascending x');
  assert.ok(Math.abs(g.xs[0] - g.L) < 1e-6 && g.xs[g.xs.length - 1] < g.W - g.R, '4:00 AM at the left edge, 9:00 AM well inside the session window');
  assert.equal(g.pts[3].label, '4:15 AM ET · Thu Oct 15, 2026'); assert.equal(el._pcIdx, -1);
  const ys = h.match(/<text x="\d+" y="[\d.]+" text-anchor="end">\$([\d.,]+)<\/text>/g).map((t) => parseFloat(/\$([\d.,]+)/.exec(t)[1].replace(/,/g, '')));
  assert.ok(Math.min.apply(null, ys) > 200 && Math.max.apply(null, ys) < 300, 'y-axis tight to the session (not stretched to the $640 scenario band): ' + ys.join(','));
  const col = r.cls === 'neg' ? '#FF8A8A' : '#5BD69C'; assert.ok(h.includes('stroke="' + col + '"') && h.includes('fill="' + col + '" opacity=".12"'), 'line and area follow the sign of the return');
  el = fakeEl(900, 280); r = App.drawPrice(el, S, { range: '5D' });
  assert.equal(r.kind, 'sessions'); assert.ok(/^5D: [+-][\d.]+% \(Wed Oct 14 4:00 AM → Thu Oct 15 9:00 AM ET\) · vs close before 2026-10-14 \$272\.28 · 1 of 2 sessions partial$/.test(r.text), r.text);
  assert.equal(r.after, null, 'a live last session: the return ends on its last print, no after-hours clause'); assert.ok(Math.abs(r.pct - (pxFx.today.bars[pxFx.today.bars.length - 1][1] / 272.28 - 1) * 100) < 1e-9);
  assert.equal((el.innerHTML.match(/<line class="sep"/g) || []).length, 1, 'one separator between the two sessions'); assert.equal((el.innerHTML.match(/<rect class="ext"/g) || []).length, 4);
  assert.equal((el.innerHTML.match(/stroke-width="1.8"/g) || []).length, 2, 'one line path per session'); assert.ok(el.innerHTML.includes('>Wed Oct 14</text>') && el.innerHTML.includes('>Thu Oct 15</text>'), 'weekday-date labels'); assert.ok(!el.innerHTML.includes('class="pcl"'), 'no prev-close line on 5D');
  el = fakeEl(900, 280); r = App.drawPrice(el, S, { range: 'YTD', showIv: true, showBand: true, showH: true });
  assert.equal(r.kind, 'daily'); assert.ok(r.text.startsWith('YTD: ') && r.partial === 0 && !r.text.includes('partial')); assert.ok(el.innerHTML.includes('>IV</text>') && el.innerHTML.includes('>20%</text>') && el.innerHTML.includes('Scenario range at 15%'), 'overlays back on a daily range');
  assert.equal(el._pcGeom.pts[0].label, 'Wed Dec 31, 2025', 'the YTD base row is drawn first'); assert.ok(/^[A-Z][a-z]{2} Jan \d{1,2}, 2026$/.test(el._pcGeom.pts[1].label), 'daily crosshair labels carry the full date: ' + el._pcGeom.pts[1].label);
  assert.ok(el.innerHTML.includes('class="xh"') && el._pcGeom.pts.every((p) => Array.isArray(p.sl) && p.sl.length === 1 && p.sl[0] === p.label), 'daily points carry one short token (the date)');
  el = fakeEl(360, 240); r = App.drawPrice(el, S, { range: '1D' }); assert.ok(r && el._pcGeom.L === 44 && el.innerHTML.includes('<svg'), 'phone width draws with the narrow margin');
  el = fakeEl(); r = App.drawPrice(el, S, { range: 'nope' }); assert.equal(r.range, '1Y', 'an unknown range falls back to the default'); el = fakeEl(); r = App.drawPrice(el, S, { range: '3Y' }); assert.equal(r.range, '5Y', 'v6.0 range names map');
  el = fakeEl(); r = App.drawPrice(el, Object.assign({}, S, { intraday: null, sessions: [] }), { range: '1D' }); assert.equal(r.range, '1Y', 'a disabled range falls back to the default');
});
test('a finished session\'s period return ends on the official close (= prices.stats.change_1d_pct); the after-hours print is reported separately; the line colour follows the same figure', () => {
  const S = pxFx.spec, done = Object.assign({}, pxFx.intraday, pxFx.full); // the complete 10-14 session as the 1D block (prev 272.28 → close 262.19, after-hours to 19:55)
  let el = fakeEl(900, 280), r = App.drawPrice(el, Object.assign({}, S, { intraday: done }), { range: '1D' });
  const lastBar = pxFx.full.bars[pxFx.full.bars.length - 1];
  assert.ok(Math.abs(r.pct - (262.19 / 272.28 - 1) * 100) < 1e-9, '1D = close ÷ prev close − 1, not the 19:55 print: ' + r.pct); assert.equal(Math.round(r.pct * 100) / 100, -3.71); assert.equal(r.last, 262.19);
  assert.equal(r.text, '1D: -3.71% (4:00 AM ET → 4:00 PM ET close) · vs prev close $272.28 · after-hours ' + App.fmtMoney(lastBar[1]) + ' at 7:55 PM ET (' + App.fmtRange((lastBar[1] / 262.19 - 1) * 100) + ' vs close)');
  assert.deepEqual(r.after, { t: 1195, v: lastBar[1], label: '7:55 PM ET', pct: (lastBar[1] / 262.19 - 1) * 100 });
  assert.equal(r.cls, 'neg'); assert.ok(el.innerHTML.includes('stroke="#FF8A8A"') && !el.innerHTML.includes('stroke="#5BD69C"'), 'coloured by the regular-session return');
  const up = Object.assign({}, done, { prev_close: 250, close: 262.19 }); r = App.drawPrice(fakeEl(900, 280), Object.assign({}, S, { intraday: up }), { range: '1D' }); assert.equal(r.cls, 'pos'); assert.ok(Math.abs(r.pct - (262.19 / 250 - 1) * 100) < 1e-9);
  const noClose = Object.assign({}, done, { close: null }); r = App.drawPrice(fakeEl(900, 280), Object.assign({}, S, { intraday: noClose }), { range: '1D' });
  assert.ok(Math.abs(r.pct - (lastBar[1] / 272.28 - 1) * 100) < 1e-9, 'without an official close the last print ends the return'); assert.equal(r.after, null); assert.ok(r.text.includes('(4:00 AM ET → 7:55 PM ET)'));
  const toClose = Object.assign({}, done, { bars: pxFx.full.bars.filter((b) => b[0] <= 960), complete: false }); r = App.drawPrice(fakeEl(900, 280), Object.assign({}, S, { intraday: toClose }), { range: '1D' });
  assert.equal(Math.round(r.pct * 100) / 100, -3.71); assert.equal(r.after, null, 'bars that stop at the close: no after-hours clause'); assert.ok(r.text.includes('(4:00 AM ET → 4:00 PM ET close) · vs prev close $272.28 · partial session'));
  el = fakeEl(900, 280); r = App.drawPrice(el, Object.assign({}, S, { sessions: [pxFx.full] }), { range: '5D' });
  assert.equal(Math.round(r.pct * 100) / 100, -3.71, '5D with one finished session = that day\'s close vs the close before it'); assert.ok(r.text.startsWith('5D: -3.71% (Wed Oct 14 4:00 AM → Wed Oct 14 4:00 PM ET close) · vs close before 2026-10-14 $272.28 · after-hours '), r.text);
  r = App.drawPrice(fakeEl(900, 280), S, { range: '5D' }); assert.equal(r.after, null, 'the live 10-15 session ends 5D on its last print');
  assert.deepEqual(App.sessionEnd([[240, 1], [960, 2], [965, 3]], 2), { last: 2, lastAt: '4:00 PM ET close', after: { t: 965, v: 3, label: '4:05 PM ET', pct: 50 } });
  assert.deepEqual(App.sessionEnd([[240, 1], [960, 2]], 2), { last: 2, lastAt: '4:00 PM ET close', after: null }); assert.deepEqual(App.sessionEnd([[240, 1], [955, 2]], 2), { last: 2, lastAt: null, after: null }, 'bars short of 16:00: last print');
  assert.deepEqual(App.sessionEnd([[240, 1], [960, 2], [965, 3]], null), { last: 3, lastAt: null, after: null }, 'no close: last print'); assert.deepEqual(App.sessionEnd([], 2), { last: null, lastAt: null, after: null });
  Object.keys(loaded).forEach((t) => { // every served finished session: the chart's 1D figure equals the hero's daily change
    const rec = loaded[t].record, pr = rec.prices || {}, st = pr.stats || {}, full = (pr.sessions_5d || []).find((x) => x && x.complete === true && typeof x.close === 'number' && x.session_date === st.last_date);
    if (!full) return;
    const spec = App.priceSpec(rec), rr = App.drawPrice(fakeEl(800, 280), Object.assign({}, spec, { intraday: Object.assign({ regular_open: '09:30', regular_close: '16:00' }, full) }), { range: '1D' });
    assert.equal(Math.round(rr.pct * 100) / 100, st.change_1d_pct, t + ' 1D pill vs stats.change_1d_pct'); assert.ok(rr.after === null || rr.after.t > 960, t + ' after-hours only past the close');
  });
});
test('crosshair label fits the plot: full text when it fits, else short tokens packed into lines (phone width 313 px, plot 211 px)', () => {
  const S = pxFx.spec, W = 313, L = 44, R = 58, PW = W - L - R, wide = 900 - 56 - 58;
  const est = (l) => App.estWidth(l) + App.XL_PAD_X;
  ['1D', '5D', 'YTD', '1M', '5Y'].forEach((rg) => {
    const el = fakeEl(W, 240), r = App.drawPrice(el, S, { range: rg }); assert.ok(r && el._pcGeom.L === L && el._pcGeom.W === W, rg);
    el._pcGeom.pts.forEach((p) => {
      const lines = App.crosshairLines(p, PW); assert.ok(lines.length >= 1 && lines.length <= 3, rg + ' lines ' + lines.length);
      lines.forEach((l) => assert.ok(est(l) <= PW, rg + ': "' + l + '" estimated ' + est(l) + ' px > plot ' + PW));
      assert.ok(App.labelWidth(lines) <= PW, 'box fits the plot'); assert.ok(lines[lines.length - 1].endsWith(App.fmtMoney(p.v)), 'the price ends the last line: ' + lines.join(' / '));
      const wideLines = App.crosshairLines(p, wide); assert.deepEqual(wideLines, [p.label + ' · ' + App.fmtMoney(p.v)], 'the full label on a wide plot');
    });
  });
  const five = App.selectRange(S, '5D'), partial = five.pts[five.pts.length - 1], firstDay = five.pts[0];
  assert.deepEqual(partial.sl, ['Thu 15', '9:00 AM (partial)']); assert.deepEqual(firstDay.sl, ['Wed 14', '4:00 AM']);
  assert.deepEqual(App.crosshairLines(partial, PW), ['Thu 15 · 9:00 AM (partial)', App.fmtMoney(partial.v)], 'a partial point keeps its marker on a phone, two lines');
  assert.deepEqual(App.crosshairLines(firstDay, PW), ['Wed 14 · 4:00 AM · ' + App.fmtMoney(firstDay.v)]);
  const one = App.selectRange(S, '1D'); assert.deepEqual(one.pts[0].sl, ['4:00 AM', 'Thu 15']); assert.deepEqual(App.crosshairLines(one.pts[0], PW), ['4:00 AM · Thu 15 · ' + App.fmtMoney(one.pts[0].v)]);
  assert.deepEqual(App.crosshairLines({ label: 'Wed Oct 14, 2026', sl: ['Wed Oct 14, 2026'], v: 1234.5 }, 150), ['Wed Oct 14, 2026', '$1,234.50'], 'date and price split when the plot is very narrow');
  assert.deepEqual(App.crosshairLines({ label: 'x', sl: ['x'], v: 1 }, 10), ['x', '$1.00'], 'a token wider than the plot stays whole (clamped, never dropped)');
  assert.deepEqual(App.crosshairLines({ label: 'a', sl: [], v: 2 }, 1000), ['a · $2.00']); assert.deepEqual(App.crosshairLines({ label: 'a', sl: [], v: 2 }, 10), ['a', '$2.00'], 'no short tokens → the label then the price');
  assert.deepEqual(App.crosshairLines(one.pts[0], PW, 2), ['4:00 AM', 'Thu 15', App.fmtMoney(one.pts[0].v)], 'a measured font twice as wide re-packs onto more lines');
  assert.equal(App.XL_PAD_Y + App.XL_LINE * 2, 32, 'two-line box height');
  Object.keys(loaded).forEach((t) => { // every served record at phone width: no crosshair line wider than the plot
    const spec = App.priceSpec(loaded[t].record), avail = App.priceRanges(spec);
    App.PRICE_RANGES.forEach((rg) => { if (!avail[rg]) return; const el = fakeEl(W, 240); App.drawPrice(el, spec, { range: rg }); el._pcGeom.pts.forEach((p) => App.crosshairLines(p, PW).forEach((l) => assert.ok(est(l) <= PW, t + ' ' + rg + ' "' + l + '"'))); });
  });
});
test('price card markup: nine range buttons with the period-return slot, disabled "not captured yet", default range, intraday note, source note with the partial capture', () => {
  const rec = { score: synthetic.score, numbers: synthetic.numbers, live: synthetic.live, prices: { source: 'stooq', as_of: '2026-10-14', weekly: pxFx.w, daily_1y: pxFx.d, intraday: pxFx.intraday, sessions_5d: [pxFx.full, pxFx.today] } };
  const html = App.renderPriceChart(rec);
  assert.ok(html.includes('class="card pc" data-range="1Y"'), 'default 1Y with a daily series');
  App.PRICE_RANGES.forEach((r) => assert.ok(html.includes('data-r="' + r + '"'), r)); assert.equal((html.match(/<button type="button" data-r="/g) || []).length, 9); assert.ok(html.includes('>Max<span class="rb"></span>'), 'MAX labelled Max; every button carries the badge slot');
  assert.ok(html.includes('data-r="1Y" class="on" aria-pressed="true"') && !html.includes('disabled'), 'nothing disabled on the full record');
  assert.ok(html.includes('class="pchart" data-cid="price" tabindex="0"'), 'the chart is focusable (arrow keys move the crosshair)');
  assert.ok(html.includes('<p class="note pcnote" hidden>Value lines hidden on intraday ranges'), 'intraday note present but hidden on a daily default');
  assert.ok(html.includes('Intraday: api.nasdaq.com chart (no dates) for 2026-10-15, captured to 8:56 AM ET (partial') && html.includes('2 sessions kept for 5D'), 'source note names the partial capture and the session count');
  const noIntra = App.renderPriceChart(Object.assign({}, rec, { prices: { source: 'stooq', as_of: '2026-10-14', weekly: pxFx.w, daily_1y: pxFx.d } }));
  assert.ok(noIntra.includes('data-r="1D" class="" aria-pressed="false" disabled title="not captured yet"') && noIntra.includes('data-r="5D" class="" aria-pressed="false" disabled title="not captured yet"'), '1D / 5D disabled with the title');
  assert.ok(noIntra.includes('Intraday (1D · 5D) not captured yet for this name.'));
  const weeklyOnly = App.renderPriceChart(Object.assign({}, rec, { prices: { source: 'stooq', as_of: '2026-10-14', weekly: pxFx.w } }));
  assert.ok(weeklyOnly.includes('class="card pc" data-range="5Y"') && weeklyOnly.includes('data-r="5Y" class="on"'), 'attachment (weekly only) defaults to 5Y');
  const intraOnly = App.renderPriceChart(Object.assign({}, rec, { prices: { source: 'nasdaq', as_of: '2026-10-15', intraday: pxFx.intraday } }));
  assert.ok(intraOnly.includes('data-range="1D"') && intraOnly.includes('<p class="note pcnote">Value lines hidden'), 'intraday-only record opens on 1D with the note visible');
  Object.keys(loaded).forEach((t) => { // served records: whatever prices.py captured must be drawable, and 1D must be available once intraday exists
    const spec = App.priceSpec(loaded[t].record), avail = App.priceRanges(spec);
    if (spec.intraday && (spec.intraday.bars || []).length >= 2) { assert.equal(avail['1D'], true, t + ' 1D'); const el = fakeEl(800, 280), r = App.drawPrice(el, spec, { range: '1D' }); assert.ok(r && r.kind === 'intraday' && el.innerHTML.includes('class="pcl"'), t + ' 1D draws with its previous close'); assert.equal(r.pct === null, false, t + ' 1D period return'); }
    if (spec.sessions.length) { const el = fakeEl(800, 280), r = App.drawPrice(el, spec, { range: '5D' }); assert.ok(r && r.kind === 'sessions' && r.n >= 2, t + ' 5D draws ' + (r && r.n) + ' points'); }
    App.PRICE_RANGES.forEach((rg) => { if (!avail[rg]) return; const el = fakeEl(800, 280), r = App.drawPrice(el, spec, { range: rg }); assert.ok(r && r.range === rg && el.innerHTML.includes('class="xh"'), t + ' ' + rg); });
  });
  if (loaded.APP) { const i = (loaded.APP.record.prices || {}).intraday; if (i) { const s = App.selectRange(App.priceSpec(loaded.APP.record), '1D'); assert.equal(s.prevClose, i.prev_close, 'APP 1D prev close is the reconciled daily close (not Nasdaq\'s stale previousClose)'); } }
});
test('app.css: the chart scrubs on a horizontal drag but a vertical flick still scrolls (touch-action: pan-y); the return badge is a coloured pill', () => {
  const css = fs.readFileSync(path.join(SITE, 'app.css'), 'utf8');
  assert.ok(/\.pchart\{[^}]*touch-action:pan-y/.test(css), 'touch-action:pan-y on .pchart — never none (a 240 px full-width scroll trap on phones)'); assert.ok(!/touch-action:none/.test(css)); assert.ok(/\.pchart\{[^}]*cursor:crosshair/.test(css));
  assert.ok(/\.ranges \.rb:not\(:empty\)\.pos\{[^}]*color:var\(--pos\)/.test(css) && /\.ranges \.rb:not\(:empty\)\.neg\{[^}]*color:var\(--neg\)/.test(css) && /\.ranges \.rb:not\(:empty\)\{[^}]*border-radius:999px/.test(css), 'green / red pill');
  assert.ok(/\[tabindex\]:focus-visible\{outline:2px solid/.test(css), 'focus-visible on the focusable chart and buttons'); assert.ok(/prefers-reduced-motion:reduce/.test(css));
});

/* ---- 2026-10-15 audit round: About grid + Read more, Street card model, Filings filter, canonical hash, floor markers
   in the Scenarios card and the ranking row, statements basis breaks + period span, summary tables drop empty lines */
test('About: fact grid builder (order, Ticker, employees evidence in the title, first-filing form), Read more clamp, "Profile not pulled yet"', () => {
  const facts = App.aboutFacts(synthetic), keys = facts.map((f) => f.k);
  ['Industry', 'Sector', 'Headquarters', 'Employees', 'Exchange', 'Ticker', 'Fiscal year end', 'Filer category', 'First EDGAR record', 'Website'].forEach((k) => assert.ok(keys.includes(k), k));
  assert.ok(keys.indexOf('Industry') < keys.indexOf('Sector') && keys.indexOf('Sector') < keys.indexOf('Headquarters') && keys.indexOf('Headquarters') < keys.indexOf('Employees') && keys.indexOf('Employees') < keys.indexOf('Exchange') && keys.indexOf('Exchange') < keys.indexOf('Ticker') && keys.indexOf('Ticker') < keys.indexOf('Fiscal year end') && keys.indexOf('Fiscal year end') < keys.indexOf('Filer category') && keys.indexOf('Filer category') < keys.indexOf('First EDGAR record') && keys.indexOf('First EDGAR record') < keys.indexOf('Website'), 'stockanalysis order: ' + keys.join(' > '));
  const emp = facts.find((f) => f.k === 'Employees'); assert.ok(emp.v.includes('42,000') && emp.title.length > 20 && emp.title.includes('42,000') && !emp.v.includes(emp.title), 'count inline, the 10-K sentence only in the title: ' + emp.title);
  assert.ok(facts.find((f) => f.k === 'Ticker').v.includes('SYN'));
  const ff = facts.find((f) => f.k === 'First EDGAR record'); assert.ok(ff.v.includes('1998-03-12') && /not an IPO date/.test(ff.title), 'no registration form recorded: labelled as the start of the EDGAR record, never as the IPO date');
  const withForm = JSON.parse(JSON.stringify(synthetic)); withForm.profile.about.first_sec_filing_form = 'S-1';
  const ff2 = App.aboutFacts(withForm).find((f) => f.k === 'First SEC filing'); assert.ok(ff2.v.includes('<span class="sub">S-1</span>') && !ff2.v.includes('IPO-date proxy') && ff2.title.includes('(S-1)'), 'the form labels the line when profile.py recorded it');
  const bare = App.aboutFacts({ fundamentals: { profile: { sic: '5411', sic_description: 'Retail-Grocery Stores', exchanges: ['NYSE'], filer_category: 'Large accelerated filer', fiscal_year_end_mmdd: '0131' } }, score: { ticker: 'KR', sector: 'Consumer Staples' } });
  assert.deepEqual(bare.map((f) => f.k), ['Industry', 'Sector', 'Exchange', 'Ticker', 'Fiscal year end', 'Filer category'], 'fallbacks from fundamentals.profile, no empty facts');
  assert.deepEqual(App.aboutFacts({}), []);
  const html = App.renderAbout(synthetic);
  assert.ok(html.includes('<div class="fact" title="') && html.includes('<span class="k">Ticker</span>'), 'facts carry the title attribute');
  // Read more: a short description has no button; a long one is cut at a sentence end past half the window, the rest hidden
  const short = App.clampText('One sentence. Two sentences.'); assert.equal(short.more, ''); assert.equal(short.short, 'One sentence. Two sentences.');
  const sentence = 'Alpha beta gamma delta epsilon zeta eta theta iota kappa. '; let long = ''; while (long.length < 1400) long += sentence;
  const c = App.clampText(long); assert.ok(c.short.length <= App.ABOUT_CLAMP && c.short.length > App.ABOUT_CLAMP / 2 && c.short.endsWith('.') && c.more.startsWith('Alpha') && (c.short + ' ' + c.more).trim() === long.trim(), 'cut at a sentence end; nothing lost: ' + c.short.length);
  const noDots = App.clampText(long.replace(/\. /g, ' ')); assert.ok(noDots.short.length <= App.ABOUT_CLAMP && noDots.more.length > 0 && !noDots.short.endsWith(' '), 'no sentence end → cut at a word');
  assert.equal(App.clampText('x'.repeat(App.ABOUT_CLAMP + 80)).more, '', 'a tail shorter than a line is not worth a button'); assert.equal(App.clampText(null).short, '');
  const longRec = JSON.parse(JSON.stringify(synthetic)); longRec.profile.about.description = { text: long, source: '10-K Item 1 Business', form: '10-K', filed: '2026-02-20', accession: '0001234567-26-000012', url: 'https://www.sec.gov/Archives/edgar/data/1234567/syn-20251231.htm' };
  const lh = App.renderAbout(longRec);
  assert.ok(lh.includes('<button type="button" class="readmore" aria-expanded="false">Read more</button>') && lh.includes('<span class="more" hidden>') && lh.includes('<span class="ell">…</span>'), 'expander markup');
  assert.ok(lh.includes('10-K Item 1 Business · filed 2026-02-20 · <a href="https://www.sec.gov/Archives/edgar/data/1234567/syn-20251231.htm"') && lh.includes('0001234567-26-000012</a>'), 'the filing the prose came from is linked');
  assert.ok(!App.renderAbout(synthetic).includes('readmore') || (typeof synthetic.profile.about.description === 'object' ? synthetic.profile.about.description.text : synthetic.profile.about.description).length > App.ABOUT_CLAMP + 80, 'no button on a short description');
  const none = App.renderAbout(Object.assign({}, synthetic, { profile: undefined })); assert.ok(none.includes('<b>Profile not pulled yet</b>') && none.includes('Retail-Grocery Stores'), 'absent profile: the wording plus the fundamentals facts');
  assert.ok(!App.renderAbout(inject(longRec)).includes('<x-inj>'), 'escaped');
});
test('Street card model: counts, mean target and its % vs the last close, range, history oldest first; the compact card and its small chart', () => {
  const M = App.streetCardModel(synthetic);
  assert.equal(M.ticker, 'SYN'); assert.equal(M.analysts, 16); assert.equal(M.consensus, 'Buy'); assert.equal(M.price, 45); assert.equal(M.price_word, 'last close');
  assert.equal(M.target_mean, 58); assert.ok(Math.abs(M.pct_mean - (58 / 45 - 1) * 100) < 1e-9, 'mean target vs the last close'); assert.ok(Math.abs(M.pct_low - (44 / 45 - 1) * 100) < 1e-9 && Math.abs(M.pct_high - (72 / 45 - 1) * 100) < 1e-9);
  assert.deepEqual(M.counts, { buy: 12, hold: 4, sell: 0, total: 16, analysts: 16 }); assert.deepEqual(M.hurdles, { 15: 60, 20: 45.5, 25: 36 });
  assert.ok(M.history.length >= 2 && M.history.every((h, i) => !i || h.date >= M.history[i - 1].date) && M.history[0].date === '2026-07-01' && typeof M.history[0].mean_target === 'number', 'history oldest first with the mean target: ' + M.history.map((h) => h.date).join(','));
  const scored = App.streetCardModel(Object.assign({}, synthetic, { live: null })); assert.equal(scored.price, 50); assert.equal(scored.price_word, 'price used'); assert.ok(Math.abs(scored.pct_mean - 16) < 1e-9, 'vs the scored price without live.json');
  assert.equal(App.streetCardModel({ profile: { about: {} } }), null); assert.equal(App.streetCardModel({}), null);
  const noPx = App.streetCardModel(Object.assign({}, synthetic, { live: null, score: Object.assign({}, synthetic.score, { price: null }) })); assert.equal(noPx.pct_mean, null, 'no ratio without a price');
  const html = App.renderStreet(synthetic);
  assert.ok(html.includes('<span class="k">Mean 12-month target</span><span class="v mono">$58.00 <small class="badge pos">+28.9% vs last close $45.00</small></span>'), 'the mean target large with the % badge');
  assert.ok(html.includes('Range $44.00 – $72.00 (-2% to +60%)') && html.includes('data-cid="street-sum"') && html.includes('Ratings by month') && html.includes('class="bhs"'), 'range line, small chart, buy / hold / sell bar');
  assert.ok(html.indexOf('streetlbl') < html.indexOf('<p class="dimp">') && html.indexOf('Our hurdle prices') < html.indexOf('See the full forecast'), 'label first, our hurdle prices before the link');
  const spec = App.chartSpecsStreet(synthetic)['street-sum']; assert.ok(spec && spec.stacked && spec.height === 120 && spec.series.length === 3 && spec.labels.length === M.history.length && /^[A-Z][a-z]{2} '\d{2}$/.test(spec.labels[0]), 'small stacked chart, month labels: ' + spec.labels.join(','));
  const el = fakeEl(400); App.drawChart(el, spec); assert.ok(el.innerHTML.includes('<svg') && el.innerHTML.includes('Buy'));
  const oneMonth = JSON.parse(JSON.stringify(synthetic)); oneMonth.profile.street.history = oneMonth.profile.street.history.slice(-1);
  assert.ok(!App.chartSpecsStreet(oneMonth)['street-sum'] && !App.renderStreet(oneMonth).includes('street-sum') && App.renderStreet(oneMonth).includes('class="bhs"'), 'one month: no chart, the bar stays');
  const noTarget = JSON.parse(JSON.stringify(synthetic)); noTarget.profile.street.target_mean = null; noTarget.profile.street.target_low = null; noTarget.profile.street.target_high = null;
  assert.ok(!App.renderStreet(noTarget).includes('class="stgt"') && App.renderStreet(noTarget).includes('consensus for SYN is based on 16 analysts'), 'no target → no tile, the paragraph stays');
});
test('Filings filter: kinds, counts, chips and data-kind rows', () => {
  assert.equal(App.filingKind('10-K'), 'periodic'); assert.equal(App.filingKind('10-K/A'), 'periodic'); assert.equal(App.filingKind('10-Q'), 'periodic'); assert.equal(App.filingKind('20-F'), 'periodic'); assert.equal(App.filingKind('40-F'), 'periodic'); assert.equal(App.filingKind('10-KT'), 'periodic');
  assert.equal(App.filingKind('8-K'), '8k'); assert.equal(App.filingKind('8-K/A'), '8k'); assert.equal(App.filingKind('6-K'), '8k'); assert.equal(App.filingKind(' 8-k '), '8k');
  assert.equal(App.filingKind('DEF 14A'), 'other'); assert.equal(App.filingKind('S-8'), 'other'); assert.equal(App.filingKind('SC 13G'), 'other'); assert.equal(App.filingKind(''), 'other'); assert.equal(App.filingKind(null), 'other');
  const list = [{ form: '10-Q', filed: '2026-08-05' }, { form: '8-K', filed: '2026-08-05' }, { form: '8-K/A', filed: '2026-07-01' }, { form: 'DEF 14A', filed: '2026-04-20' }, { form: '10-K', filed: '2026-02-20' }, null, 'junk'];
  assert.equal(App.filterFilings(list, 'all').length, 5); assert.deepEqual(App.filterFilings(list, 'periodic').map((f) => f.form), ['10-Q', '10-K']); assert.deepEqual(App.filterFilings(list, '8k').map((f) => f.form), ['8-K', '8-K/A']); assert.deepEqual(App.filterFilings(list, 'other').map((f) => f.form), ['DEF 14A']);
  assert.equal(App.filterFilings(list).length, 5); assert.deepEqual(App.filterFilings(null, '8k'), []); assert.deepEqual(App.FILING_KINDS.map((k) => k[0]), ['all', 'periodic', '8k', 'other']);
  const html = App.renderFilings({ profile: { filings: list, as_of: '2026-10-15' } });
  assert.ok(html.includes('<div class="card fcard" data-fk="all">') && html.includes('class="fchips" role="group"'), 'card + chips row');
  assert.ok(html.includes('data-fk="all" class="on" aria-pressed="true">All <span class="mono">5</span>') && html.includes('data-fk="periodic" class="" aria-pressed="false" title="Annual and quarterly reports, amendments included">10-K / 10-Q <span class="mono">2</span>') && html.includes('>8-K <span class="mono">2</span>') && html.includes('>Other <span class="mono">1</span>'), 'chip counts');
  assert.equal((html.match(/<tr data-kind="periodic">/g) || []).length, 2); assert.equal((html.match(/<tr data-kind="8k">/g) || []).length, 2); assert.equal((html.match(/<tr data-kind="other">/g) || []).length, 1);
  const only8k = App.renderFilings({ profile: { filings: list.filter((f) => f && f.form === '8-K') } }); assert.ok(only8k.includes('data-fk="periodic" class="" aria-pressed="false" disabled') && only8k.includes('data-fk="other" class="" aria-pressed="false" disabled'), 'a chip with nothing behind it is disabled');
  const syn = App.renderFilings(synthetic), total = App.filterFilings(synthetic.profile.filings, 'all').length;
  assert.ok(syn.includes('All <span class="mono">' + total + '</span>') && ['periodic', '8k', 'other'].reduce((a, k) => a + App.filterFilings(synthetic.profile.filings, k).length, 0) === total, 'the three kinds partition the list');
  const fb = App.renderFilings(Object.assign({}, synthetic, { profile: undefined })); assert.ok(fb.includes('data-kind="periodic"') && fb.includes('latest 10-K'), 'the fundamentals fallback rows carry a kind too');
  assert.ok(!App.renderFilings(inject({ profile: { filings: list } })).includes('<x-inj>'));
});
test('canonicalHash: legacy #T/tab and non-canonical casing normalise to #T.tab with the index casing; bad or unknown → null', () => {
  const find = (t) => ['APP', 'BRK.B', 'KR'].find((x) => x.toLowerCase() === String(t).toLowerCase()) || null;
  assert.equal(App.canonicalHash('#app/Financials', find), '#APP.financials'); assert.equal(App.canonicalHash('#APP/forecast/street', find), '#APP.forecast.street'); assert.equal(App.canonicalHash('#App.Forecast.STREET', find), '#APP.forecast.street');
  assert.equal(App.canonicalHash('#APP', find), '#APP'); assert.equal(App.canonicalHash('#APP.overview', find), '#APP', 'overview is the bare ticker'); assert.equal(App.canonicalHash('#APP.forecast.dcf', find), '#APP.forecast'); assert.equal(App.canonicalHash('#APP.data.street', find), null, 'a sub-tab suffix off the forecast tab is an unknown ticker');
  assert.equal(App.canonicalHash('#brk.b/data', find), '#BRK.B.data'); assert.equal(App.canonicalHash('#BRK.B.forecast.analysts', find), '#BRK.B.forecast.analysts');
  assert.equal(App.canonicalHash('#', find), null); assert.equal(App.canonicalHash('', find), null); assert.equal(App.canonicalHash('#<script>', find), null); assert.equal(App.canonicalHash('#NOPE.financials', find), null, 'unknown ticker');
  assert.equal(App.canonicalHash('#kr.dividends'), '#kr.dividends', 'without a finder the token is kept as typed (the tab still lower-cased)'); assert.equal(App.canonicalHash('#KR/Dividends'), '#KR.dividends');
  assert.equal(App.canonicalHash('#APP.financials', find), '#APP.financials', 'a canonical hash is unchanged');
});
test('floor-clamped scenario IRRs are marked in the Overview Scenarios card and badged in the ranking row (live and scored separately)', () => {
  const rec = builtOr('ZS', 'ZS live floor flags in the Overview Scenarios card');
  if (rec) {
    const ov = App.renderOverview(rec), sc = ov.slice(ov.indexOf('<h2>Scenarios</h2>'), ov.indexOf('<h2>Moat</h2>'));
    const sb = sc.slice(sc.indexOf('Super bear'), sc.indexOf('>Bear<')); assert.ok(sb.includes('class="mono scni atfloor"') && sb.includes('>at floor</sup>'), 'ZS live super-bear IRR is marked');
    const base = sc.slice(sc.indexOf('>Base<'), sc.indexOf('>Bull<')); assert.ok(!base.includes('at floor'), 'base unmarked');
    assert.ok(sc.includes('<b>At floor</b> marks an IRR the solver clamped'), 'explanation in the section note');
  }
  assert.ok(!App.renderOverview(synthetic).includes('at floor'), 'no marker without flags');
  const flagged = JSON.parse(JSON.stringify(synthetic)); flagged.forecast.sensitivity.bear.irr_at_floor = true; flagged.live = null;
  const fo = App.renderOverview(flagged), fb = fo.slice(fo.indexOf('>Bear<'), fo.indexOf('>Base<')); assert.ok(fb.includes('class="mono scni atfloor"') && fb.includes('the scored IRR solver stopped at its floor'), 'scored floor flag marks the scored view');
  const liveFlag = JSON.parse(JSON.stringify(synthetic)); liveFlag.forecast.sensitivity.bear.irr_at_floor = true; // scored at floor, live not: the live figure is shown bare, the scored sub-figure marked
  const lo = App.renderOverview(liveFlag), lb = lo.slice(lo.indexOf('>Bear<'), lo.indexOf('>Base<')); assert.ok(!lb.includes('class="mono scni atfloor"') && lb.includes('Scored IRR <b>') && lb.includes('>at floor</sup>'), 'live view: the scored sub-figure carries its own marker');
  const wFloor = Object.assign({}, synthetic, { row: Object.assign({}, synthetic.row, { irr_at_floor_live: true }) }); const wf = App.renderOverview(wFloor); assert.ok(wf.slice(wf.indexOf('scnfoot')).includes('>at floor</sup>'), 'the weighted foot marks the floored headline');
  // ranking row badges and cells
  const rowL = App.renderRowHTML({ ticker: 'X', name: 'X', tier: 'D', tier_live: 'D', irr: 0.03, irr_live: 0.031, irr_at_floor: true, irr_at_floor_live: true, price: 10, price_live: 9 });
  assert.ok(rowL.includes('>live IRR at floor</span>') && rowL.includes('>scored IRR at floor</span>'), 'both badges on a live row with both flags'); assert.equal((rowL.match(/class="num mono[^"]*atfloor"/g) || []).length, 2, 'both IRR cells marked'); assert.equal((rowL.match(/>at floor<\/sup>/g) || []).length, 2);
  const rowS = App.renderRowHTML({ ticker: 'X', name: 'X', tier: 'D', irr: 0.03, irr_at_floor: true, price: 10 });
  assert.ok(rowS.includes('>IRR at floor</span>') && !rowS.includes('live IRR at floor') && !rowS.includes('scored IRR at floor'), 'scored-only row keeps the plain badge'); assert.equal((rowS.match(/atfloor/g) || []).length, 1);
  const rowLiveOnly = App.renderRowHTML({ ticker: 'X', name: 'X', tier: 'D', tier_live: 'D', irr: 0.08, irr_live: 0.031, irr_at_floor: false, irr_at_floor_live: true, price: 10, price_live: 9 });
  assert.ok(rowLiveOnly.includes('>live IRR at floor</span>') && !rowLiveOnly.includes('scored IRR at floor') && /class="num mono strong atfloor">3\.1%/.test(rowLiveOnly) && !/muted atfloor/.test(rowLiveOnly), 'live flag alone marks only the live cell');
  assert.ok(!App.renderRowHTML(synthetic.row).includes('at floor'));
});
test('statements viewer: basis-break quarters are greyed with a title and a legend line; the units note says how far the table reaches', () => {
  const bb = JSON.parse(JSON.stringify(stmFx)); bb.statements.income[0].basis_break_quarterly = [true, true, true, true, false, false];
  const Q = App.stmTable(bb, 'income', 'quarterly', true); assert.equal(Q.anyBasisBreak, true); assert.equal(Q.rows[0].anyBasisBreak, true); assert.equal(Q.rows[1].anyBasisBreak, false);
  assert.deepEqual(Q.rows[0].cells.map((c) => c.basisBreak), [false, false, true, true, true, true], 'newest first: the FY2026 quarters are flagged');
  assert.equal(App.stmTable(bb, 'income', 'annual', true).anyBasisBreak, false, 'annual columns are never flagged'); assert.equal(App.stmTable(stmFx, 'income', 'quarterly').anyBasisBreak, false);
  const html = App.renderStatements({ ticker: 'FX' }, { status: 'ready', data: bb, statement: 'income', period: 'quarterly' });
  assert.equal((html.match(/<td class="bbrk" title="basis break:/g) || []).length, 4, 'four greyed cells with the title'); assert.ok(html.includes('Greyed quarters: that fiscal year'), 'legend');
  assert.ok(!App.renderStatements({ ticker: 'FX' }, { status: 'ready', data: stmFx, statement: 'income', period: 'quarterly' }).includes('Greyed quarters'), 'no legend without a flag');
  const neg = JSON.parse(JSON.stringify(bb)); neg.statements.income[0].quarterly[2] = -5e9; const nh = App.renderStatements({ ticker: 'FX' }, { status: 'ready', data: neg, statement: 'income', period: 'quarterly' }); assert.ok(nh.includes('<td class="negv bbrk" title='), 'both classes when negative and flagged');
  assert.equal(App.stmSpan(App.stmTable(stmFx, 'income', 'annual')), '3 fiscal years, FY2024 → FY2026'); assert.equal(App.stmSpan(App.stmTable(stmFx, 'income', 'quarterly')), '6 quarters, Q1 FY2026 → Q2 FY2027'); assert.equal(App.stmSpan(App.stmTable(stmFx, 'cashflow', 'ttm')), '3 fiscal years, FY2024 → FY2026', 'the TTM column is not counted');
  assert.equal(App.stmSpan({ cols: [{ src: 'annual', label: 'FY2026' }] }), ''); assert.equal(App.stmSpan(null), '');
  assert.ok(html.includes('<b>6 quarters, Q1 FY2026 → Q2 FY2027</b> — scroll the table sideways for the older periods.'), 'units note carries the span');
  if (!statementsPath('APP')) skip('APP statements basis-break check — no APP statements file');
  else { // APP's FY2023 / FY2024 quarters (the apps divestiture) are the real case
    const d = JSON.parse(fs.readFileSync(statementsPath('APP'), 'utf8')), M = App.stmTable(d, 'income', 'quarterly');
    if (M.anyBasisBreak) { const rev = M.rows.find((r) => r.key === 'revenue'); assert.ok(rev.cells.filter((c) => c.basisBreak).length >= 4 && rev.cells.filter((c) => c.basisBreak).every((c) => c.growth === null), 'APP: flagged quarters carry no growth'); }
  }
});
test('summary tables drop a line with no value in any shown period; performance prose with negative growth', () => {
  const rec = JSON.parse(JSON.stringify(synthetic)); rec.fundamentals.quarterly.forEach((q) => { q.capex = null; q.gross_margin = null; }); rec.fundamentals.annual.forEach((a) => { a.rnd = null; a.prepaids_pct_assets = null; });
  const fin = App.renderFinancials(rec), qslice = fin.slice(fin.indexOf('<h2>Quarterly</h2>'), fin.indexOf('<h2>Revenue'));
  assert.ok(qslice.length > 500 && !qslice.includes('<th>Capex (PP&amp;E)</th>') && !qslice.includes('<th>Gross margin</th>') && qslice.includes('<th>Revenue</th>'), 'all-empty quarterly lines dropped (' + qslice.length + ')');
  assert.ok(!fin.includes('<th>R&amp;D</th>') && !fin.includes('<th>Prepaids % assets</th>') && fin.includes('<th>Revenue</th>') && fin.includes('<th>Operating cash flow</th>'), 'all-empty annual lines dropped, the rest kept');
  const full = App.renderFinancials(synthetic); assert.ok(full.includes('<th>Capex (PP&amp;E)</th>') && full.includes('<th>Stock-based compensation</th>') && full.includes('<th>Operating cash flow</th>'), 'lines with values stay');
  const annKeys = Object.keys(synthetic.fundamentals.annual[0]); assert.ok(!annKeys.includes('rnd') ? !full.includes('<th>R&amp;D</th>') : full.includes('<th>R&amp;D</th>'), 'a line the fixture never filed is absent; one it filed is present');
  const neg = { fundamentals: { currency: 'USD', annual: [{ fy: '2024', period_end: '2024-12-31', revenue: 2.1e9, net_income: 2e8 }, { fy: '2025', period_end: '2025-12-31', revenue: 1.99e9, revenue_growth: -0.0524, net_income: 1.5e8, net_margin: 0.0754, net_income_growth: -0.25, shares_diluted: 1.02e8, shares_diluted_growth: 0.02 }] } };
  const t = App.financialPerformance(neg);
  assert.ok(t.startsWith('In fiscal 2025 (ended 2025-12-31) revenue was $1.99B, -5.2% on fiscal 2024.'), t.slice(0, 90)); assert.ok(t.includes('Net income $150M (7.5% margin), -25.0% year over year.') && t.includes('Diluted shares were 102.0M, +2.0% on fiscal 2024'), t);
  assert.ok(!t.includes('Operating cash flow') && !t.includes("Owner's earnings") && !t.includes('At fiscal year end'), 'sentences with no figure are dropped');
});
test('app.css: sticky bars respect the notch inset; the ranking filter row sticks on desktop; the new About / Street / Filings / statements rules exist', () => {
  const css = fs.readFileSync(path.join(SITE, 'app.css'), 'utf8');
  assert.ok(/\.tabbar\{position:sticky;top:env\(safe-area-inset-top,0px\)/.test(css), 'company tab bar: top = env(safe-area-inset-top, 0px)');
  assert.ok(/@media \(min-width:761px\)\{\.controls\{position:sticky;top:env\(safe-area-inset-top,0px\)/.test(css), 'ranking controls sticky at desktop widths only');
  assert.ok(/\.readmore\{/.test(css) && /\.about \.more\[hidden\],\.about \.ell\[hidden\]\{display:none\}/.test(css), 'Read more');
  assert.ok(/\.stgt \.v\{font-size:30px/.test(css) && /\.stgt \.badge\.pos\{color:var\(--pos\)/.test(css) && /\.streetlbl\{/.test(css), 'Street target tile');
  assert.ok(/\.fchips button\.on\{/.test(css) && /table\.filings tr\[hidden\]\{display:none\}/.test(css), 'filing chips');
  assert.ok(/table\.stm td\.bbrk\{color:var\(--mut\)/.test(css), 'basis-break cells greyed');
});

test('tab strip: a deep link or hashchange to a tab past the strip\'s edge scrolls the strip so the active tab is visible (tabScrollLeft, revealTab on mount and showTab)', () => {
  const PAD = App.TAB_PAD; assert.equal(PAD, 16);
  // the reviewer's geometry: phone 375 px, strip 343 px wide (16 px gutters), Forecast at 382.6…465.8 px of the viewport with the strip at 16 px
  const strip = { scrollLeft: 0, clientWidth: 343, scrollWidth: 596 }, forecast = { left: 382.6 - 16, width: 83.2 };
  const next = App.tabScrollLeft(strip, forecast);
  assert.equal(next, Math.round(366.6 + 83.2 + PAD - 343), 'scrolls just far enough to show the tab plus 16 px of its neighbour');
  assert.ok(forecast.left + forecast.width <= next + strip.clientWidth && forecast.left >= next, 'the tab is fully inside the window after the scroll');
  assert.equal(App.tabScrollLeft({ scrollLeft: next, clientWidth: 343, scrollWidth: 596 }, forecast), null, 'a second pass is a no-op (already visible)');
  assert.equal(App.tabScrollLeft({ scrollLeft: 0, clientWidth: 343, scrollWidth: 596 }, { left: 0, width: 90 }), null, 'Overview at scrollLeft 0 needs nothing');
  assert.equal(App.tabScrollLeft({ scrollLeft: 0, clientWidth: 343 }, { left: 100, width: 90 }), null, 'a tab inside the window (with its padding) needs nothing');
  assert.equal(App.tabScrollLeft({ scrollLeft: 200, clientWidth: 343, scrollWidth: 596 }, { left: 20, width: 90 }), 4, 'a tab left of the window scrolls back to it (minus the padding)');
  assert.equal(App.tabScrollLeft({ scrollLeft: 200, clientWidth: 343, scrollWidth: 596 }, { left: 5, width: 90 }), 0, 'never below 0');
  assert.equal(App.tabScrollLeft({ scrollLeft: 0, clientWidth: 343, scrollWidth: 596 }, { left: 540, width: 56 }), 596 - 343, 'the last tab clamps to the strip\'s maximum scroll');
  assert.equal(App.tabScrollLeft({ scrollLeft: 253, clientWidth: 343, scrollWidth: 596 }, { left: 540, width: 56 }), null, 'at the maximum already: no-op');
  assert.equal(App.tabScrollLeft({ scrollLeft: 0, clientWidth: 900, scrollWidth: 596 }, forecast), null, 'desktop: the strip is wider than its tabs, nothing to do');
  assert.equal(App.tabScrollLeft({ scrollLeft: 0, clientWidth: 0 }, forecast), null, 'a hidden strip (clientWidth 0) is left alone');
  assert.equal(App.tabScrollLeft(null, forecast), null); assert.equal(App.tabScrollLeft(strip, null), null); assert.equal(App.tabScrollLeft(strip, { left: 'x', width: 10 }), null);
  // the DOM wrapper is wired into both entry points: the first mount of a company page and every tab switch
  const src = fs.readFileSync(path.join(SITE, 'app.js'), 'utf8');
  const fnBody = (name) => { const i = src.indexOf('function ' + name + '('); assert.ok(i >= 0, name + ' exists'); return src.slice(i, src.indexOf('\nfunction ', i + 1)); };
  assert.ok(/revealTab\(/.test(fnBody('mountCompany')), 'mountCompany reveals the active tab after mount');
  const st = fnBody('showTab'); assert.ok(/revealTab\(page\)/.test(st) && st.indexOf('revealTab(page)') > st.indexOf("classList.toggle('on', on)"), 'showTab reveals the active tab after toggling .on');
  assert.ok(/strip\.scrollLeft = next/.test(fnBody('revealTab')) && !/scrollIntoView/.test(fnBody('revealTab')), 'revealTab sets the strip\'s scrollLeft directly (never scrollIntoView, which can also move the page)');
  const css = fs.readFileSync(path.join(SITE, 'app.css'), 'utf8');
  assert.ok(/\.tabs\{[^}]*overflow-x:auto/.test(css), 'the strip is the horizontal scroll container the helper targets');
});

/* ---- report */
/* ---- review round 4 (2026-10-15): Forecast audit, watchlist view, partial yields, sticky bar, chart / statements minors */
test('OE/share history: a year counts only when BOTH owner\'s earnings and diluted shares are filed; the engine CSV never fills an override year (ZS, APP, AEE)', () => {
  const zs = builtOr('ZS', 'ZS OE/share history against the engine paths');
  if (zs) {
    const H = App.oeHistory(zs), ann = zs.fundamentals.annual;
    assert.ok(H.every((h) => h.v === null || Math.abs(h.v) < 5), 'no -61 / share from the engine CSV\'s mangled FY2018 share count: ' + H.map((h) => h.fy + ':' + h.v).join(' '));
    H.filter((h) => h.v !== null).forEach((h) => { const a = ann.find((r) => String(r.fy) === h.fy); assert.ok(a && a.oe_conservative !== null && a.shares_diluted, 'FY' + h.fy + ' has both filed'); assert.ok(Math.abs(h.v - a.oe_conservative / a.shares_diluted) < 1e-9, 'FY' + h.fy + ' = OE ÷ diluted shares'); });
    assert.ok(H[0].fy === '2017' && H[0].v === null && H[1].v === null && H[2].fy === '2019' && H[2].v !== null, 'FY2017 / FY2018 (no diluted share count in fundamentals) keep their labels but are not drawn');
    assert.ok(App.renderForecastDCF(zs).includes('<b>Not shown:</b> FY2017–FY2018: diluted share count not filed'), 'the leading blank years are named in the note (no silent trim)');
    const sp = App.chartSpecsForecast(zs)['fc-oe'], el = fakeEl(700); App.drawChart(el, sp);
    const ys = [...el.innerHTML.matchAll(/text-anchor="end">([^<]+)</g)].map((m) => Number(m[1].replace(/[$,]/g, '')));
    const histMin = Math.min(...H.filter((h) => h.v !== null).map((h) => h.v)), top = Math.max(...sp.series[0].values.filter((v) => v !== null));
    assert.ok(Math.min(...ys) <= histMin && Math.max(...ys) >= top, 'the y-axis covers the negative history and the super-bull path together: ' + ys.join(' '));
    assert.ok(Math.min(...ys) >= -5, 'and its floor is near the filed losses, not at -61');
    assert.equal(sp.yFloor, null, 'ZS needs no floor once the series is right');
  }
  if (loaded.AEE) {
    const aee = loaded.AEE.record, sp = App.chartSpecsForecast(aee)['fc-oe'], dcf = App.renderForecastDCF(aee);
    assert.ok(sp && sp.series.length === 1 && sp.series[0].name === 'Filed OE / share' && !sp.dividerAt && sp.labels.length === App.oeHistory(aee).length, 'Tier F: the history line alone, no forecast series');
    assert.ok(dcf.includes("<h2>Owner's earnings per share — history</h2>") && dcf.includes('data-cid="fc-oe"') && dcf.includes('No projection') && dcf.includes('the axis covers every one'), 'Tier F DCF sub-tab: history chart + the no-projection note');
    const el = fakeEl(700); App.drawChart(el, sp); assert.ok(el.innerHTML.includes('-$8') && !el.innerHTML.includes('offscale'), 'every negative AEE year is on the scale (no floor on history alone)');
  }
  // engine CSV alone (no fundamentals): a row an override filled is not a filed value
  const csvOnly = { score: { base_oe_per_share: 2 }, numbers: {}, forecast: {}, fundamentals: null, history: [
    { fy_label: 2023, oe_conservative: 100, shares_diluted: 50 }, { fy_label: 2024, oe_conservative: 120, shares_diluted: 50, capex_tag: 'OVERRIDE' }, { fy_label: 2025, oe_conservative: 130, shares_diluted: null }] };
  const C = App.oeHistory(csvOnly);
  assert.deepEqual(C.map((h) => h.v), [2, null, null]); assert.ok(/FY2024: capex filled by an override/.test(C[1].why) && /FY2025: diluted share count not filed/.test(C[2].why), C.map((h) => h.why).join(' | '));
  // fundamentals: oe_per_share present but shares missing → null; OE null → the missing legs are named
  const fx = { numbers: { overrides_applied: [{ field: 'capex', kind: 'estimate', periods_filled: ['2025-12-31'] }] }, fundamentals: { annual: [
    { fy: '2023', period_end: '2023-12-31', oe_per_share: 1.5, oe_conservative: 150, shares_diluted: 100 }, { fy: '2024', period_end: '2024-12-31', oe_per_share: 9, oe_conservative: 200, shares_diluted: null },
    { fy: '2025', period_end: '2025-12-31', oe_per_share: null, oe_conservative: null, ocf: 500, capex: null, sbc: 20, shares_diluted: 100 }] }, history: [{ fy_label: 2025, oe_conservative: 470, shares_diluted: 100 }] };
  const F = App.oeHistory(fx);
  assert.deepEqual(F.map((h) => h.v), [1.5, null, null], 'the engine CSV does not fill a year fundamentals leaves blank');
  assert.ok(/FY2024: diluted share count not filed/.test(F[1].why) && /FY2025: capex not filed \(the engine run fills capex with an estimate/.test(F[2].why), F.map((h) => h.why).join(' | '));
  assert.ok(App.oeGapNote(F).includes('<b>Not shown:</b> FY2024') && App.oeGapNote([{ v: 1 }]) === '');
});
test('OE/share history (engine 5.5): a \'+\'-joined capex_tag is an override year when OVERRIDE is one of its tags; summed component tags are filed values', () => {
  assert.equal(App.isOverrideTag('OVERRIDE'), true);
  assert.equal(App.isOverrideTag('OVERRIDE+PaymentsToAcquireIntangibleAssets'), true);
  assert.equal(App.isOverrideTag('PaymentsToAcquireIntangibleAssets+override'), true, 'case-insensitive, any position');
  assert.equal(App.isOverrideTag('PaymentsToExploreAndDevelopOilAndGasProperties+PaymentsToAcquireOilAndGasProperty'), false);
  assert.equal(App.isOverrideTag('OVERRIDES_NOTED'), false, 'a whole tag, not a substring');
  assert.equal(App.isOverrideTag(null), false); assert.equal(App.isOverrideTag(undefined), false); assert.equal(App.isOverrideTag(''), false);
  const rec = { score: { base_oe_per_share: 2 }, numbers: { overrides_applied: [{ field: 'capex', kind: 'filing', value: 5e6, source: 'Form 20-F for the fiscal year ended December 31, 2024', periods_filled: ['2024-12-31'] }] }, forecast: {}, fundamentals: null, history: [
    { fy_label: 2023, period_end: '2023-12-31', oe_conservative: 100, shares_diluted: 50, capex_tag: 'PaymentsToExploreAndDevelopOilAndGasProperties+PaymentsToAcquireOilAndGasProperty' },
    { fy_label: 2024, period_end: '2024-12-31', oe_conservative: 120, shares_diluted: 50, capex_tag: 'OVERRIDE+PaymentsToAcquireIntangibleAssets' },
    { fy_label: 2025, period_end: '2025-12-31', oe_conservative: 130, shares_diluted: 50, capex_tag: 'PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities+PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities' }] };
  const H = App.oeHistory(rec);
  assert.deepEqual(H.map((h) => h.v), [2, null, 2.6], 'the OVERRIDE+… year is not plotted; the summed-tag years are');
  assert.ok(/FY2024: capex not tagged in companyfacts \(the engine run uses \$5M read from the Form 20-F for the fiscal year ended December 31, 2024/.test(H[1].why), H.map((h) => h.why).join(' | '));
  assert.equal(H[0].why || '', ''); assert.equal(H[2].why || '', '');
});
test('Data tab market cap (engine 5.5): a make_score ADS-corrected cap replaces the pre-5.5 engine figure; a 5.5 run names a non-default share basis', () => {
  const corrected = App.runCapText({ market_cap_basis: 'ads_corrected_by_make_score', market_cap_b: 39.61 }, { market_cap_est: 79216000000 });
  assert.equal(corrected, '$39.61B (ADS-corrected by make_score: price × shares ÷ ratio; the pre-5.5 engine printed $79.22B)');
  assert.equal(App.runCapText({ market_cap_b: 18.54, market_cap_basis: 'diluted_latest_split_adjusted' }, { market_cap_est: 18540000000, market_cap_basis: { shares_source: 'diluted_latest_split_adjusted' } }), '$18.54B (diluted_latest_split_adjusted)');
  assert.equal(App.runCapText({}, { market_cap_est: 35456212000, market_cap_basis: { shares_source: 'diluted_latest' } }), '$35.46B', 'the plain basis adds nothing');
  assert.equal(App.runCapText({}, { market_cap_est: 5e9 }), '$5.00B', 'a pre-5.5 non-ADS run is unchanged');
  assert.equal(App.runCapText({ market_cap_basis: 'ads_corrected_by_make_score', market_cap_b: null }, { market_cap_est: 5e9 }), '$5.00B', 'no corrected figure: the engine figure stands');
  const rec = { score: { market_cap_basis: 'ads_corrected_by_make_score', market_cap_b: 10.93 }, numbers: { market_cap_est: 1092660000000, price: 18.1, price_source: 'nasdaq' } };
  assert.ok(App.renderData(rec).includes('market cap est. $10.93B (ADS-corrected by make_score'), 'the Provenance row prints the corrected cap');
});
test('OE/share chart y-axis: history and forecast share one axis; a floor only when a loss reaches deeper than the chart reaches up, pinned with a ▼ and its real value', () => {
  assert.equal(App.oeAxisFloor([-1.1, 0.9], [0.7, 6.25]), null, 'ZS shape: no floor');
  assert.equal(App.oeAxisFloor([-61, -1, 0.9], [0.7, 6.25]), -6.25, 'a loss below minus the positive extent → floor at minus that extent');
  assert.equal(App.oeAxisFloor([-7, -4, 0.1], []), null, 'history alone (Tier F): never floored');
  assert.equal(App.oeAxisFloor([1, 2], [3]), null); assert.equal(App.oeAxisFloor([], [3]), null);
  const spec = { labels: ['2022', '2023', '2024', '2025'], yfmt: 'money', zero: true, yFloor: -6.25, series: [{ name: 'Filed', color: '#fff', kind: 'line', values: [-61, -1, 0.9, null] }, { name: 'Path', color: '#aaa', kind: 'line', values: [null, null, 0.9, 6.25] }] };
  const el = fakeEl(700); App.drawChart(el, spec);
  const ys = [...el.innerHTML.matchAll(/text-anchor="end">([^<]+)</g)].map((m) => Number(m[1].replace(/[$,]/g, '')));
  assert.ok(Math.min(...ys) >= -10 && Math.max(...ys) >= 6.25, 'axis stops near the floor: ' + ys.join(' '));
  assert.ok(el.innerHTML.includes('class="offscale"') && el.innerHTML.includes('Filed: -$61') && el.innerHTML.includes('below the axis floor'), 'the pinned point keeps its real value in the tooltip and the legend explains the ▼');
  const plain = fakeEl(700); App.drawChart(plain, Object.assign({}, spec, { yFloor: null })); assert.ok(!plain.innerHTML.includes('offscale') && plain.innerHTML.includes('-$80'), 'without a floor the axis runs to the loss');
});
test('Street: quarterly "from" = the filed quarter a year earlier matched on the consensus quarter\'s end month (Nasdaq "Sep 2026"), 52/53-week quarters included', () => {
  const qs = [{ label: 'Q3 FY2025', period_end: '2025-09-30', eps_diluted: 2.45 }, { label: 'Q4 FY2025', period_end: '2025-12-31', eps_diluted: null }, { label: 'Q3 FY2026', period_end: '2025-11-08', eps_diluted: -2.02 }];
  assert.deepEqual(App.yearAgoQuarter({ period: 'Sep 2026', fiscal_end: '2026-09' }, qs), { v: 2.45, label: 'Q3 FY2025 filed', end: '2025-09-30' });
  assert.equal(App.yearAgoQuarter({ period: 'Sep 2026' }, qs).v, 2.45, 'the period text alone is enough');
  assert.equal(App.yearAgoQuarter({ period: 'Dec 2026', fiscal_end: '2026-12' }, qs), null, 'the year-ago quarter has no filed EPS → no "from"');
  assert.equal(App.yearAgoQuarter({ period: 'Oct 2026', fiscal_end: '2026-10' }, qs.slice(2)).v, -2.02, 'Kroger: a quarter ending 2025-11-08 is the year-ago "Oct" quarter (8 days off the month end)');
  assert.equal(App.yearAgoQuarter({ period: 'Mar 2027', fiscal_end: '2027-03' }, qs), null, 'nothing within 45 days');
  assert.equal(App.yearAgoQuarter({ period: 'Q1 2026' }, [{ label: 'Q1 FY2025', period_end: '2025-03-31', eps_diluted: 0.38 }]).v, 0.38, 'Q-form periods still match by quarter number');
  if (builtOr('APP', 'APP Street quarterly "from" (profile.street)')) { const s = App.renderForecastStreet(built.APP); assert.ok(s.includes('from $2.45 (Q3 FY2025 filed)'), 'APP: Sep 2026 consensus vs the filed Sep 2025 quarter'); }
});
test('Watchlist toggle: every watched name whatever the Modeled / misfit filter, the tier filter still applies, the count = rows shown with tier All, Copy = the count with the no-page names in a note', () => {
  const rows = [{ ticker: 'AAA', watchlist: true, fit: 'modeled', tier: 'B', irr: 0.2 }, { ticker: 'MIS', fit: 'misfit', tier: 'C', irr: 0.12 }, { ticker: 'CCC', fit: 'modeled', tier: 'D', irr: 0.05 }, { ticker: 'DDD', fit: 'modeled', tier: 'D', irr: 0.04 }];
  const metaW = { watchlist: ['AAA', 'CCC', 'OUT1', 'PEND'], watchlist_outside: ['OUT1', 'AAA'] }, repo = App.repoList(metaW, rows), stars = ['mis'];
  const on = App.filterSortIndex(rows, { watch: true, fit: 'modeled', tier: 'all' }, stars, repo).map((r) => r.ticker);
  assert.deepEqual(on, ['AAA', 'MIS', 'CCC'], 'the starred misfit shows under the Modeled default');
  assert.equal(on.length, App.watchCount(rows, stars, repo), 'button count = rows shown with the tier filter on All');
  assert.deepEqual(App.filterSortIndex(rows, { watch: true, fit: 'misfit', tier: 'D' }, stars, repo).map((r) => r.ticker), ['CCC'], 'the tier filter still applies');
  assert.deepEqual(App.filterSortIndex(rows, { watch: false, fit: 'modeled' }, stars, repo).map((r) => r.ticker), ['AAA', 'CCC', 'DDD'], 'off: the fit filter is back');
  assert.equal(App.countText(rows, { watch: true, tier: 'D' }, stars, repo), '1 shown · 2 more watched outside the Tier D filter'); assert.equal(App.countText(rows, { watch: true }, stars, repo), '3 shown'); assert.equal(App.countText(rows, { watch: false, fit: 'all' }, stars, repo), '4 shown');
  const c = App.watchCopy(metaW, rows, repo, stars.concat(['zzz']));
  assert.deepEqual(c.tickers, ['AAA', 'MIS', 'CCC']); assert.equal(c.text, 'AAA, MIS, CCC'); assert.equal(c.tickers.length, App.watchCount(rows, stars.concat(['zzz']), repo), 'Copy copies exactly what the count describes');
  assert.deepEqual(c.outside, ['OUT1'], 'a ticker with a row (AAA) is copied even when the data layer lists it as outside'); assert.deepEqual(c.unranked, ['PEND']); assert.deepEqual(c.starsOff, ['ZZZ']);
  const note = App.copyNoteHTML(c); assert.ok(note.includes('Not copied') && note.includes('outside the screened universe (no page): OUT1') && note.includes('not ranked yet: PEND') && note.includes('not in this ranking: ZZZ'), note);
  assert.equal(App.copyNoteHTML({ tickers: ['A'], outside: [], unranked: [], starsOff: [] }), '');
  const list = App.renderListHTML(metaW, rows, { watch: true, fit: 'modeled' }, stars);
  assert.ok(list.includes('★ Watchlist <span class="mono">3</span>') && (list.match(/data-watch="1"/g) || []).length === 3 && list.includes('id="count">3 shown<'), 'button 3 = 3 rows = "3 shown"');
  assert.ok(/class="seg dim" id="fitseg" role="group" title="Ignored while the Watchlist is on"/.test(list) && !App.renderListHTML(metaW, rows, { watch: false }, stars).includes('seg dim'), 'the fit segment is dimmed (and says why) while the watchlist is on');
  assert.ok(list.includes('_system/watchlist.json') && !list.includes('universe.csv'), 'titles name the real source of the repo list');
  if (meta.watchlist_outside) { const repoR = App.repoList(meta, index), cr = App.watchCopy(meta, index, repoR, []); assert.equal(cr.tickers.length, App.watchCount(index, [], repoR)); assert.ok(cr.outside.every((t) => !index.some((r) => r.ticker === t)), 'served data: outside names have no row'); }
  const css = fs.readFileSync(path.join(SITE, 'app.css'), 'utf8'); assert.ok(/\.seg\.dim\{opacity:\.5\}/.test(css) && /\.copynote\{/.test(css));
});
test('Partial yields: the Dividends tiles and the ranking print yields_display labels (≥ / ≤ / ≈) with the note in a tooltip — never the bare number', () => {
  if (loaded.HBAN) {
    const d = loaded.HBAN.record.fundamentals.dividends, html = App.renderDividends(loaded.HBAN.record);
    ['buyback_yield', 'net_buyback_yield', 'shareholder_yield'].forEach((k) => { const yd = d.yields_display[k], txt = html.replace(/<[^>]+>/g, ''); assert.ok(txt.includes(yd.label), k + ' label ' + yd.label); assert.ok(html.includes('title="' + App.esc(yd.note) + '"'), k + ' note in the tooltip'); });
    const bl = d.yields_display.buyback_yield.label; assert.ok(/^≥ /.test(bl) && html.includes('>' + bl + '</span>') && !html.includes('>' + bl.slice(2) + '</span>'), 'HBAN buyback yield: the lower bound is marked');
    assert.ok(html.includes('$150M TTM') && !html.includes('no buyback filed'), 'the partial leg\'s filed sum is shown (legs.buybacks.value), not "no buyback filed"');
    const sl = d.yields_display.shareholder_yield.label; assert.ok(/^≈ [\d.]+% \(incomplete\)$/.test(sl), 'HBAN shareholder yield label ' + sl); assert.ok(html.includes('<b class="bword">lower bound</b>') && html.includes(sl.replace(' (incomplete)', ' <span class="vsfx">(incomplete)</span>')), 'the bound is named on the tile (phones have no hover): under the figure, or the label\'s own "(incomplete)" on its own line');
  }
  if (loaded.ZS) { const z = App.renderDividends(loaded.ZS.record), zd = loaded.ZS.record.fundamentals.dividends.yields_display || {}; const lower = Object.keys(zd).filter((k) => zd[k].bound === 'lower'); assert.ok(lower.length && lower.every((k) => /^≥ /.test(zd[k].label) && z.includes('>' + zd[k].label + '</span>')) && z.includes('no buyback filed'), 'ZS: lower bounds marked'); }
  if (loaded.KR) { const k = App.renderDividends(loaded.KR.record), kd = loaded.KR.record.fundamentals.dividends.yields_display || {}; const exact = Object.keys(kd).filter((x) => !kd[x].bound || kd[x].bound === 'exact'); assert.ok(exact.length === Object.keys(kd).length && exact.every((x) => /^-?[\d.]+%$/.test(kd[x].label) && k.includes('>' + kd[x].label + '</span>')) && !k.includes('class="bword"'), 'exact yields carry no bound marker'); }
  const y = App.yieldShown({ shareholder_yield: 0.0123 }, 'shareholder_yield'); assert.equal(y.text, '1.2%', 'an older block without yields_display falls back to the figure'); assert.equal(y.partial, false);
  assert.deepEqual(App.yieldShown({ yields_display: { buyback_yield: { label: '≤ 2.78%', bound: 'upper', note: 'n' } } }, 'buyback_yield'), { text: '≤ 2.78%', note: 'n', bound: 'upper', partial: true, word: 'upper bound' });
  const r = App.rowYieldHTML({ shareholder_yield: 0.0353, shareholder_yield_label: '≈ 3.53% (incomplete)', shareholder_yield_bound: 'indeterminate' });
  assert.ok(r.includes('Shareholder yield <b class="mono">≈ 3.53% (incomplete)</b>') && r.includes('class="syld bounded"') && r.includes('incomplete: a cash-flow leg is partial'), r);
  assert.equal(App.rowYieldHTML({ shareholder_yield: 0.0353 }), '', 'no label → nothing (never the bare figure)'); assert.equal(App.rowYieldHTML({ shareholder_yield_label: '—' }), '');
  assert.ok(App.rowYieldHTML({ shareholder_yield_label: '12.36%', shareholder_yield_bound: 'exact' }).includes('class="syld"'));
  index.filter((row) => row.shareholder_yield_label).forEach((row) => { const h = App.renderRowHTML(row); assert.ok(h.includes(App.esc(row.shareholder_yield_label)), row.ticker + ' row prints its label'); });
});
test('Overview polish: no empty <h2>; the Street mean-target move once at one precision; the analyst count and the rating split labelled', () => {
  assert.equal(App.renderOverview(synthetic).indexOf('<h2></h2>'), -1); Object.keys(loaded).forEach((t) => assert.equal(App.renderCompanyHTML(loaded[t].record, 'overview').indexOf('<h2></h2>'), -1, t));
  assert.ok(App.renderOverview(synthetic).includes('<h2>Moat</h2>'), 'the Moat card keeps its own heading');
  const card = App.renderStreet(synthetic).replace(/<[^>]+>/g, '');
  assert.equal((card.match(/\+28\.9%/g) || []).length, 1, 'the mean move is printed once (the badge)'); assert.ok(!/\+29%/.test(card), 'not again at 0 dp');
  const sub = App.renderForecastStreet(synthetic).replace(/<[^>]+>/g, ''); assert.ok(sub.includes('+28.9% vs the last close $45.00'), 'the Street sub-tab paragraph uses one decimal, like its price-target table');
  const split = JSON.parse(JSON.stringify(synthetic)); Object.assign(split.profile.street, { analysts: 16, buy: 16, hold: 4, sell: 0 });
  const p = App.streetParagraph(split, split.profile.street);
  assert.ok(p.includes('based on 16 analysts') && p.includes('rating breakdown lists 20 ratings (16 buy · 4 hold · 0 sell)') && p.includes('the two counts differ'), p);
  assert.ok(!App.streetParagraph(synthetic, synthetic.profile.street).includes('rating breakdown lists'), 'no explanation when the counts agree');
  assert.ok(App.renderStreet(split).includes('Rating breakdown · 20 ratings'), 'the bar is labelled with its own total');
});
test('Sticky bar: the condensed line overlays the space above the tabs, so the bar never changes height; condenseNow switches where stuck and natural positions meet', () => {
  const css = fs.readFileSync(path.join(SITE, 'app.css'), 'utf8');
  assert.ok(/\.tabsum\{[^}]*position:absolute[^}]*bottom:100%[^}]*height:var\(--tabsum-h\)/.test(css), 'the summary is out of flow, above the bar');
  assert.ok(/\.tabsum\{[^}]*visibility:hidden/.test(css) && /\.tabbar\.condensed \.tabsum\{visibility:visible\}/.test(css) && !/\.tabbar\.condensed \.tabsum\{display:flex\}/.test(css), 'shown with visibility, never a display switch');
  assert.ok(/\.tabbar\.condensed\{top:calc\(env\(safe-area-inset-top,0px\) \+ var\(--tabsum-h\)\)/.test(css) && /--tabsum-h:36px/.test(css), 'the condensed bar sticks the summary\'s height lower');
  assert.equal(App.TABSUM_H, 36);
  assert.equal(App.condenseNow(100, 18, 36), false); assert.equal(App.condenseNow(18, 18, 36), false, 'natural top 36 = the stuck top: not yet'); assert.equal(App.condenseNow(17, 18, 36), true); assert.equal(App.condenseNow(-400, 18), true); assert.equal(App.condenseNow(null, 18, 36), false);
  const src = fs.readFileSync(path.join(SITE, 'app.js'), 'utf8'); assert.ok(/bar\.classList\.toggle\('condensed', condenseNow\(/.test(src), 'watchHeader uses condenseNow');
});
test('Price chart minors: 5D lays sessions out by session_date whatever the file order; a live 1D card prints one "captured to" time (the last print)', () => {
  const S = pxFx.spec, rev = Object.assign({}, S, { sessions: [pxFx.today, pxFx.full] });
  const a = App.selectRange(S, '5D'), b = App.selectRange(rev, '5D');
  assert.deepEqual(b.sessions.map((s) => s.date), ['2026-10-14', '2026-10-15'], 'oldest first'); assert.equal(b.base, 272.28, 'base = the close before the OLDEST session'); assert.deepEqual(b.pts.map((p) => p.t), a.pts.map((p) => p.t));
  assert.equal(App.capturedTo(pxFx.intraday), '8:56 AM ET'); assert.equal(App.capturedTo({ bars: [[240, 1], [615, 2]] }), '10:15 AM ET', 'no last_time → the last bar'); assert.equal(App.capturedTo({}), '');
  const one = App.selectRange(S, '1D'); assert.equal(one.to, '8:56 AM ET');
  const rec = { score: { ticker: 'PX' }, prices: { source: 's', as_of: '2026-10-14', weekly: pxFx.w, daily_1y: pxFx.d, intraday: pxFx.intraday, sessions_5d: [pxFx.full, pxFx.today] } };
  const card = App.renderPriceChart(rec), el = fakeEl(900, 280), r = App.drawPrice(el, S, { range: '1D' });
  assert.ok(card.includes('captured to 8:56 AM ET (partial') && r.text.includes('captured to 8:56 AM ET') && !r.text.includes('9:00 AM'), 'the source note and the footer print the same time: ' + r.text);
  const done = App.selectRange(Object.assign({}, S, { intraday: Object.assign({}, pxFx.full, { last_time: '19:59' }) }), '1D'); assert.equal(done.to, '7:55 PM ET', 'a finished session keeps its last bar');
});
test('Statements minors: the chart card closes with its line on a period switch; annual-only filers say so; a failed load can be retried; duplicate quarter labels carry their end month', () => {
  const rec = { ticker: 'FX', score: { ticker: 'FX' } };
  const q = App.renderStatements(rec, { status: 'ready', data: stmFx, statement: 'income', period: 'quarterly', line: 'dps' });
  assert.ok(!q.includes('id="stmspark"') && !q.includes('data-line="dps"'), 'dps has no quarterly values: no row, no stale "No data." card');
  assert.ok(App.renderStatements(rec, { status: 'ready', data: stmFx, statement: 'income', period: 'annual', line: 'dps' }).includes('id="stmspark"'), 'annual: the card is there');
  const src = fs.readFileSync(path.join(SITE, 'app.js'), 'utf8');
  assert.ok(/D\.stmView\.period = ss\.dataset\.stp; if \(sraw\.line && !stmSparkSpec\(/.test(src), 'a period switch clears a line that has no values there');
  assert.ok(/restoreFocus\('\.stpseg button\.on', sec3\)/.test(src), 'closing a chart whose line is gone keeps focus in the card (the active period button)');
  const ann = JSON.parse(JSON.stringify(stmFx)); ann.periods.quarterly = []; ann.periods.ttm = null; ann.periods.current = null;
  ['income', 'balance'].forEach((st) => { const h = App.renderStatements(rec, { status: 'ready', data: ann, statement: st, period: 'ttm' }); assert.ok(h.includes('this filer reports annual periods only (no quarterly filings in companyfacts)') && !h.includes('not four consecutive') && !h.includes('"Current" is the latest quarter end'), st); });
  const gap = JSON.parse(JSON.stringify(stmFx)); gap.periods.ttm = null; assert.ok(App.renderStatements(rec, { status: 'ready', data: gap, statement: 'income', period: 'ttm' }).includes('not four consecutive fiscal quarters'), 'quarters exist, TTM null: the consecutive-quarters wording stays');
  const err = App.renderStatements(rec, { status: 'error', error: 'HTTP 500' }); assert.ok(err.includes('class="wbtn sm stm-retry">Retry</button>') && err.includes('reopening the tab retries'));
  assert.ok(/if \(st\.status === 'error'\) \{ st\.status = 'idle';/.test(src) && /closest\('\.stm-retry'\)/.test(src), 'ensureStatements retries an error; the Retry button resets it');
  assert.deepEqual(App.sparkLabels([{ label: 'Q1 FY2012', end: '2011-09-30' }, { label: 'Q1 FY2012', end: '2012-03-31' }]), ["Q1 FY2012 · Sep '11", "Q1 FY2012 · Mar '12"]); assert.deepEqual(App.sparkLabels([{ label: 'FY2024', end: '2024-12-31' }]), ['FY2024'], 'unique labels unchanged');
  const dupF = statementsPath('ADM');
  if (!dupF) skip('ADM duplicate quarter labels — no ADM statements file');
  else { const sp = App.stmSparkSpec(JSON.parse(fs.readFileSync(dupF, 'utf8')), 'income', 'quarterly', 'revenue'); assert.equal(new Set(sp.labels).size, sp.labels.length, 'ADM: every sparkline label distinct'); const el = fakeEl(360); App.drawChart(el, sp); const drawn = (el.innerHTML.match(/<text x="[\d.]+" y="\d+" text-anchor="middle">/g) || []).length; assert.ok(drawn >= 2 && drawn <= Math.floor((360 - 46 - 12) / (sp.labels[0].length * 6.8 + 10)) + 1, 'long labels are thinned to fit: ' + drawn); }
});
test('Hero watchlist chip reads the index (authoritative) when a repo list is given; record.row only without one', () => {
  const lag = { score: { ticker: 'KR', name: 'Kroger' }, row: { ticker: 'KR', watchlist: true } };
  assert.ok(!App.renderHeader(lag, [], []).includes('★ Watchlist <span class="sub">repo</span>') && App.renderHeader(lag, [], []).includes('data-star="KR"'), 'a stale record.row.watchlist does not win over the index-derived repo list');
  assert.ok(App.renderHeader(lag, [], ['KR']).includes('★ Watchlist <span class="sub">repo</span>'));
  assert.ok(App.renderHeader(lag).includes('★ Watchlist <span class="sub">repo</span>'), 'no repo list (a lone record) → record.row is all there is');
  const src = fs.readFileSync(path.join(SITE, 'app.js'), 'utf8'); assert.ok(/renderCompanyHTML\(record, tab, navFor\(ticker\), sub, \{ stm: stm, stars: D\.stars, repo: repoNow\(\) \}\)/.test(src), 'mountCompany passes the meta ∪ index repo list');
});

/* ---- review round 5 (2026-10-15): OE/share history — override kinds, share basis, fiscal-year gaps, all-blank histories; shareholder-yield caption */
/* A built record by ticker (data/<T>.json); on a fresh clone null, and the real-record check that wanted it skips with a
   note — these checks pin the engine's override notes and history placeholders as the build serves them. */
const SITE_DATA = (t) => { const p = path.join(BUILT, 'data', t + '.json'); if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, 'utf8')); skip(t + ' real-record check — needs the built data/' + t + '.json'); return null; };
test('OE/share history: a "filing" override is described as a value read from the filing, never "an filing — not a filed value" (CFG / CMPS / MTB shape)', () => {
  const cfgShape = { numbers: { overrides_applied: [{ field: 'capex', kind: 'filing', value: 174e6, source: 'Form 10-K for fiscal year ended December 31, 2025 (filed 2026-02-12), Consolidated Statements of Cash Flows …', periods_filled: ['2024-12-31', '2025-12-31'] }] },
    fundamentals: { annual: [{ fy: '2023', period_end: '2023-12-31', oe_conservative: 150, shares_diluted: 100, oe_per_share: 1.5 },
      { fy: '2024', period_end: '2024-12-31', oe_conservative: null, ocf: 500, capex: null, sbc: 20, shares_diluted: 100 }, { fy: '2025', period_end: '2025-12-31', oe_conservative: null, ocf: 520, capex: null, sbc: 21, shares_diluted: 100 }] } };
  const H = App.oeHistory(cfgShape), note = App.oeGapNote(H);
  assert.deepEqual(H.map((h) => h.v), [1.5, null, null]);
  assert.ok(!/an filing|with an filing/.test(note) && !/not a filed value/.test(note), note);
  assert.ok(note.includes('<b>Not shown:</b> FY2024–FY2025: capex not tagged in companyfacts (the engine run uses $174M read from the Form 10-K for fiscal year ended December 31, 2025 for both untagged years — a filing value, but not in fundamentals.json, so not plotted)'), note);
  assert.ok(/capex not filed \(the engine run fills capex with an estimate — not a filed value\)/.test(App.overrideWhy({ field: 'capex', kind: 'estimate' }, false)), 'an estimate still says so');
  assert.ok(/capex filled by an estimate in the engine run/.test(App.overrideWhy({ field: 'capex', kind: 'estimate' }, true)) && /\$0 read from the filing/.test(App.overrideWhy({ field: 'capex', kind: 'filing', value: 0, source: 'no form here' }, true)), 'CSV path and an unparseable source');
  ['CFG', 'CMPS', 'MTB'].forEach((t) => { const r = SITE_DATA(t); if (!r) return; const dcf = App.renderForecastDCF(r).replace(/<[^>]+>/g, ''); assert.ok(!/with an filing/.test(dcf) && /capex not tagged in companyfacts \(the engine run uses \$[\d.,]+[MK]? read from the Form 10-K/.test(dcf), t + ': ' + (dcf.match(/Not shown:[^.]*\./) || [''])[0]); });
  const cfg = SITE_DATA('CFG'); if (cfg) assert.ok(App.renderForecastDCF(cfg).includes('FY2020–FY2025: capex not tagged'), 'CFG: one grouped entry for its six years, not six copies');
});
test('OE/share history: a diluted share count off the recent basis by more than 5× is not plotted (WRB counts in thousands, CMG pre-split) and a >3× jump gets no YoY bar (DXCM 4:1)', () => {
  const wrb = SITE_DATA('WRB');
  if (wrb) {
    const H = App.oeHistory(wrb), sp = App.chartSpecsForecast(wrb), oe = sp['fc-oe'], g = sp['fc-oegrowth'];
    ['2017', '2018', '2019'].forEach((fy) => { const h = H.find((x) => x.fy === fy); assert.ok(h && h.v === null && /more than 5× away from the recent filed basis/.test(h.why), fy + ' ' + (h && h.why)); });
    const hv = oe.series[1].values.filter((v) => v !== null); assert.ok(hv.length && Math.max(...hv.map(Math.abs)) < 50, 'no $2,774–$5,343 per-share points: ' + hv.join(','));
    assert.ok(g.series[0].values.slice(0, g.dividerAt + 1).every((v) => v === null || Math.abs(v) < 5), 'no +48,356% "filed, year over year" bar');
    const el = fakeEl(700); App.drawChart(el, oe); const ys = [...el.innerHTML.matchAll(/text-anchor="end">([^<]+)</g)].map((m) => Number(m[1].replace(/[$,]/g, ''))); assert.ok(Math.max(...ys) < 200, 'y-axis on the per-share scale: ' + ys.join(' '));
    assert.ok(App.renderForecastDCF(wrb).includes('FY2017–FY2019: diluted share count more than 5× away'), 'the note names the years and why');
  }
  const cmg = SITE_DATA('CMG');
  if (cmg) { const H = App.oeHistory(cmg); assert.ok(H.filter((h) => Number(h.fy) <= 2021).every((h) => h.v === null) && H.find((h) => h.fy === '2022').v !== null, 'CMG: pre-split years blank, post-split plotted'); const g = App.oeForecastSeries(cmg).histGrowth; assert.ok(g.every((v) => v === null || v > -0.9), 'no -97.7% split "YoY"'); }
  const jump = { fundamentals: { annual: [{ fy: '2019', period_end: '2019-12-31', oe_conservative: 100, shares_diluted: 100 }, { fy: '2020', period_end: '2020-12-31', oe_conservative: 110, shares_diluted: 400 }, { fy: '2021', period_end: '2021-12-31', oe_conservative: 130, shares_diluted: 410 }, { fy: '2022', period_end: '2022-12-31', oe_conservative: 140, shares_diluted: 415 }] } };
  const Hj = App.oeHistory(jump), y = App.histYoy(Hj);
  assert.ok(Hj.every((h) => h.v !== null), '4× is under the basis rule: every year plotted');
  assert.equal(y.g[1], null); assert.ok(/FY2020: diluted shares moved 4\.0× from FY2019/.test(y.why[1]), y.why[1]); assert.ok(Math.abs(y.g[2] - ((130 / 410) / (110 / 400) - 1)) < 1e-12 && y.why[2] === '');
  assert.ok(App.oeYoyNote(y.why).includes('<b>No year-over-year bar:</b> FY2020') && App.oeYoyNote(['', '']) === '');
  // the median of the last three filed counts is the basis, so one slipped latest year does not blank everything before it
  const slip = { fundamentals: { annual: [2021, 2022, 2023, 2024].map((y2, i) => ({ fy: String(y2), period_end: y2 + '-12-31', oe_conservative: 100, shares_diluted: i === 3 ? 100 : 100000 })) } };
  assert.deepEqual(App.oeHistory(slip).map((h) => h.v === null), [false, false, false, true]);
});
test('OE/share history: fiscal years missing from fundamentals.annual get a blank placeholder, so YoY never spans a gap (MTD FY2013 → FY2017, HIG FY2015 → FY2017)', () => {
  const gap = { fundamentals: { annual: [{ fy: '2013', period_end: '2013-12-31', oe_conservative: 80, shares_diluted: 10 }, { fy: '2017', period_end: '2017-12-31', oe_conservative: 140, shares_diluted: 10 }, { fy: '2018', period_end: '2018-12-31', oe_conservative: 150, shares_diluted: 10 }] } };
  const H = App.oeHistory(gap);
  assert.deepEqual(H.map((h) => h.fy), ['2013', '2014', '2015', '2016', '2017', '2018']);
  assert.deepEqual(H.map((h) => h.v), [8, null, null, null, 14, 15]);
  assert.ok(App.oeGapNote(H).includes('FY2014–FY2016: not in fundamentals.annual'), App.oeGapNote(H));
  const y = App.histYoy(H); assert.equal(y.g[4], null, 'no 4-year change labelled YoY'); assert.ok(Math.abs(y.g[5] - (15 / 14 - 1)) < 1e-12);
  // 52/53-week years: period ends 364 / 371 days apart are adjacent even when the fy labels repeat or skip (TDY)
  const wk = { fundamentals: { annual: [{ fy: '2017', period_end: '2017-01-01', oe_conservative: 10, shares_diluted: 10 }, { fy: '2017', period_end: '2017-12-31', oe_conservative: 11, shares_diluted: 10 }, { fy: '2019', period_end: '2019-12-29', oe_conservative: 12, shares_diluted: 10 }, { fy: '2021', period_end: '2021-01-03', oe_conservative: 13, shares_diluted: 10 }] } };
  const W = App.oeHistory(wk); assert.equal(W.length, 5, 'one placeholder (2018-12-30 missing), none between 2019-12-29 and 2021-01-03'); assert.ok(App.histYoy(W).g[4] !== null && App.histYoy(W).g[1] !== null);
  ['MTD', 'HIG'].forEach((t) => { const r = SITE_DATA(t); if (!r) return; const J = App.oeForecastSeries(r); const i17 = J.hist.findIndex((h) => h.fy === '2017'); assert.ok(i17 > 0 && J.hist[i17 - 1].fy === '2016' && J.hist[i17 - 1].v === null && J.histGrowth[i17] === null, t + ': FY2016 placeholder, no FY2017 "YoY"'); });
});
test('OE/share history: when no year has both figures filed the chart keeps fiscal-year labels and the note says why (TDY / HSY / TKO shape)', () => {
  const allNull = Object.assign(JSON.parse(JSON.stringify(synthetic)), { numbers: { overrides_applied: [{ field: 'sbc', kind: 'filing', value: 39.6e6, source: 'Form 10-K for fiscal year ended December 28, 2025 (filed 2026-02-20)', periods_filled: ['2023-12-31', '2024-12-29', '2025-12-28'] }] },
    fundamentals: { annual: [{ fy: '2023', period_end: '2023-12-31', oe_conservative: null, ocf: 900, capex: 100, sbc: null, shares_diluted: 47 }, { fy: '2024', period_end: '2024-12-29', oe_conservative: null, ocf: 950, capex: 90, sbc: null, shares_diluted: 47 }, { fy: '2025', period_end: '2025-12-28', oe_conservative: null, ocf: 990, capex: 110, sbc: null, shares_diluted: 47 }] } });
  const H = App.oeHistory(allNull); assert.equal(H.length, 3, 'nothing trimmed'); assert.ok(H.every((h) => h.v === null));
  const J = App.oeForecastSeries(allNull); assert.deepEqual(J.labels.slice(0, 4), ['2023', '2024', '2025', '2026'], 'fiscal-year labels, not Base / +1'); assert.equal(J.filedCount, 0);
  const sp = App.chartSpecsForecast(allNull)['fc-oe']; assert.ok(/no year has both figures filed/.test(sp.series[1].name) && sp.dividerAt === 2);
  const dcf = App.renderForecastDCF(allNull).replace(/<[^>]+>/g, '');
  assert.ok(!dcf.includes('Solid line: filed owner') && dcf.includes('No solid line: no fiscal year in fundamentals.json has both owner\'s earnings and the diluted share count filed.'), 'no "Solid line" sentence when nothing is drawn');
  assert.ok(dcf.includes('Not shown: FY2023–FY2025: stock-based compensation not tagged in companyfacts (the engine run uses $40M read from the Form 10-K for fiscal year ended December 28, 2025 for all 3 untagged years'), dcf.match(/Not shown:[^.]*\./));
  const tierF = Object.assign({}, allNull, { score: {}, forecast: {}, numbers: Object.assign({}, allNull.numbers, { scenarios: {} }) });
  const hs = App.oeHistorySection(tierF); assert.ok(hs.includes('No fiscal year (fundamentals.json) has both') && hs.includes('Not shown:') && !hs.includes('data-cid="fc-oe"'), 'Tier F: the section explains instead of vanishing');
  ['ARES', 'EME', 'HAL', 'HSY', 'STZ', 'TDY', 'TKO'].forEach((t) => { const r = SITE_DATA(t); if (!r) return; const Jt = App.oeForecastSeries(r); const txt = App.renderForecastDCF(r).replace(/<[^>]+>/g, '');
    assert.ok(!Jt || /^\d{4}$/.test(Jt.labels[0]), t + ' labels ' + (Jt && Jt.labels.slice(0, 3))); assert.ok(txt.includes('No solid line') && txt.includes('Not shown: FY'), t + ': the note explains the empty history'); });
});
test('Shareholder yield tile: the caption names its own dividend leg (cash paid ÷ market cap), so it adds up with net buyback even when it differs from the DPS-based Dividend yield (HBAN, KR)', () => {
  const chk = (t, paidTxt, capTxt) => { const r = loaded[t] ? loaded[t].record : SITE_DATA(t); if (!r) return; const d = r.fundamentals.dividends, html = App.renderDividends(r);
    const i = html.indexOf('<span class="k">Shareholder yield</span>'), tileStart = html.lastIndexOf('<div class="tile"', i), tileHtml = html.slice(tileStart, html.indexOf('</div>', i) + 6);
    assert.ok(tileHtml.includes('dividends paid ' + paidTxt + ' + net buyback, ÷ market cap ' + capTxt), t + ': ' + tileHtml);
    assert.ok(!tileHtml.includes('>dividend + net buyback<'), 'old caption gone');
    assert.ok(tileHtml.includes('not TTM DPS × shares, so it need not equal the Dividend yield tile') && tileHtml.includes(App.esc(d.yields_display ? d.yields_display.shareholder_yield.note || '' : '')), 'tooltip: the yield\'s own note, then the dividend-leg sentence');
    const paidPct = d.legs.dividends_paid.value / d.market_cap, net = d.net_buyback_yield; if (net !== null && net !== undefined) assert.ok(Math.abs(paidPct + net - d.shareholder_yield) < 1e-9, t + ': paid + net buyback = shareholder yield');
  };
  const own = (t) => { const r = loaded[t] ? loaded[t].record : SITE_DATA(t); if (!r) return; const d = r.fundamentals.dividends, paid = d.legs.dividends_paid.value; chk(t, App.fmtBig(paid) + ' (' + App.fmtPct(paid / d.market_cap, 2) + ')', App.fmtBig(d.market_cap)); };
  own('HBAN'); own('KR');   // the figures move with the close the block is priced at; the caption's shape does not
  const app = loaded.APP ? App.renderDividends(loaded.APP.record) : ''; if (app) assert.ok(app.includes('no dividends paid + net buyback'), 'a non-payer says so');
});

/* ---- review round 6 (2026-10-16): the router never mounts a stale company; SEC dates read "updated"; a fresh clone runs the suite */
/* app.js's own route() in a browser-shaped vm sandbox (the module.exports branch has no router). #app is an innerHTML string,
   history.replaceState writes location.hash, and fetch is deferred: each request waits until the test settles it, so a record
   can arrive after the viewer has navigated elsewhere — the review's reproduction (finding 4289642900). */
function routerSandbox(rows) {
  const fetches = [], location = { hash: '' };
  const node = (html) => ({ innerHTML: html || '', textContent: '', style: {}, dataset: {}, classList: { toggle() {}, contains() { return false; } }, focus() {}, setSelectionRange() {},
    querySelector(sel) { return /^#[\w-]+$/.test(sel) && this.innerHTML.includes('id="' + sel.slice(1) + '"') ? node() : null; }, querySelectorAll() { return []; } });
  const app = node();
  const document = { readyState: 'loading', title: '', activeElement: null, addEventListener() {}, getElementById: (id) => (id === 'app' ? app : null), querySelector: (sel) => app.querySelector(sel), querySelectorAll: () => [] };
  const sb = { document, location, console, setTimeout, clearTimeout, scrollTo() {}, addEventListener() {}, getComputedStyle: () => null,
    history: { replaceState(_s, _t, url) { location.hash = url; } },
    localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    fetch: (url) => new Promise((resolve) => { fetches.push({ url, resolve }); }) };
  sb.window = sb; vm.createContext(sb);
  vm.runInContext(fs.readFileSync(path.join(SITE, 'app.js'), 'utf8'), sb, { filename: 'app.js' }); // readyState 'loading': boot() waits for a DOMContentLoaded that never comes
  const D = sb.App.state; D.app = app; D.index = rows; D.meta = meta;
  return { D, app, location, document, fetches,
    go(h) { location.hash = h; sb.App.route(); },
    urls() { return fetches.map((f) => f.url); },
    isList() { return app.innerHTML.includes('id="listView"'); },
    shows() { return D.current ? D.current.ticker + (app.innerHTML.startsWith('<div class="card loading"') ? ' (loading card)' : '') : (this.isList() ? 'ranking' : app.innerHTML.slice(0, 60)); },
    settle(url, record) { const i = fetches.findIndex((f) => f.url === url); assert.ok(i >= 0, 'a fetch pending for ' + url + ' (pending: ' + this.urls().join(', ') + ')'); fetches.splice(i, 1)[0].resolve({ ok: true, status: 200, json: () => record }); return new Promise((r) => setImmediate(r)); } };
}
function recFor(t) { const r = JSON.parse(JSON.stringify(synthetic)); r.ticker = r.folder = r.score.ticker = r.row.ticker = t; r.name = r.score.name = r.row.name = t + ' Corp'; return r; }
const routeRows = ['APP', 'KR', 'EXPE'].map((t) => recFor(t).row);
test('router: #APP → # while APP loads, then APP arrives — the ranking stays (review 4289642900); an unknown name the same', async () => {
  const R = routerSandbox(routeRows);
  R.go('#'); assert.ok(R.isList(), 'ranking mounted');
  R.go('#APP'); assert.ok(R.app.innerHTML.includes('Loading APP'), 'loading card'); assert.deepEqual(R.urls(), ['./data/APP.json']);
  R.go('#'); assert.ok(R.isList(), 'back on the ranking before APP arrives');
  await R.settle('./data/APP.json', recFor('APP'));
  assert.equal(R.shows(), 'ranking', 'APP arriving late does not replace the ranking'); assert.equal(R.D.current, null); assert.equal(App.parseHash(R.location.hash).ticker, null, 'the address still names the ranking');
  assert.equal(R.document.title, "Owner's-Earnings DCF Ranking");
  R.go('#APP'); assert.equal(R.shows(), 'APP', 'the late record was cached: #APP now mounts at once'); assert.equal(R.fetches.length, 0, 'no second request');
  const U = routerSandbox(routeRows); // an unknown name while a company loads: the notice + the ranking, and the late record stays out
  U.go('#KR'); U.go('#NOPE'); assert.ok(U.isList() && App.parseHash(U.location.hash).ticker === null, 'unknown name → the ranking');
  await U.settle('./data/KR.json', recFor('KR')); assert.equal(U.shows(), 'ranking', 'KR arriving after #NOPE does not mount');
});
test('router: back to the company already open while another loads (#KR → #APP → #KR) re-mounts KR, and the late APP record is dropped', async () => {
  const R = routerSandbox(routeRows);
  R.go('#KR'); await R.settle('./data/KR.json', recFor('KR')); assert.equal(R.shows(), 'KR');
  R.go('#APP'); assert.ok(R.app.innerHTML.includes('Loading APP') && R.D.current === null, 'the loading card replaced the KR page, so KR is no longer the open company');
  R.go('#KR'); assert.equal(R.shows(), 'KR', 'KR is back at once from the cache — not left on "Loading APP…"'); assert.ok(R.document.title.startsWith('KR — '));
  await R.settle('./data/APP.json', recFor('APP'));
  assert.equal(R.shows(), 'KR', 'APP arriving late does not replace KR'); assert.equal(R.location.hash, '#KR'); assert.ok(R.document.title.startsWith('KR — '), R.document.title);
  R.go('#EXPE'); R.go('#KR.data'); assert.equal(R.shows(), 'KR'); assert.equal(R.D.current.tab, 'data', 'a tab of the open company while another loads');
  await R.settle('./data/EXPE.json', recFor('EXPE')); assert.equal(R.shows(), 'KR'); assert.equal(R.D.current.tab, 'data');
});
test('router: the latest company navigation wins whichever record arrives first', async () => {
  const R = routerSandbox(routeRows);
  R.go('#APP'); R.go('#KR'); assert.ok(R.app.innerHTML.includes('Loading KR'));
  await R.settle('./data/APP.json', recFor('APP')); assert.ok(R.app.innerHTML.includes('Loading KR') && R.D.current === null, 'the earlier APP record arriving first is dropped');
  await R.settle('./data/KR.json', recFor('KR')); assert.equal(R.shows(), 'KR');
  const Q = routerSandbox(routeRows);
  Q.go('#APP'); Q.go('#KR'); await Q.settle('./data/KR.json', recFor('KR')); await Q.settle('./data/APP.json', recFor('APP'));
  assert.equal(Q.shows(), 'KR', 'KR first, APP late: KR stays');
  const src = fs.readFileSync(path.join(SITE, 'app.js'), 'utf8'), body = src.slice(src.indexOf('function route() {'), src.indexOf('function wireEvents()'));
  assert.ok(body.indexOf('D.routeToken = {}') > 0 && body.indexOf('D.routeToken = {}') < body.indexOf('parseHash(location.hash)'), 'route() takes its token before it reads the hash, so before every early return that follows');
});
test('SEC files are rewritten only when their content changes, so their dates read "updated <date>"; the Street keeps "pulled", prices "through"', () => {
  const about = App.renderAbout(synthetic), filings = App.renderFilings(synthetic), segs = App.renderSegments(synthetic);
  assert.ok(about.includes('<p class="note">Profile updated 2026-10-14.</p>') && !about.includes('Profile as of'), 'About');
  assert.ok(filings.includes('From EDGAR submissions, updated 2026-10-14') && !filings.includes('submissions, as of'), 'Filings');
  assert.ok(segs.includes('. Updated 2026-10-14.</p>') && !/As of /.test(segs), 'Segments');
  const noDate = App.renderSegments(Object.assign({}, synthetic, { segments: Object.assign({}, synthetic.segments, { as_of: null }) }));
  assert.ok(!/Updated|As of/.test(noDate) && noDate.includes('<p class="note">Source: SEC EDGAR XBRL segment axis'), 'no date: no dangling "As of ."');
  const stm = App.renderStatements({ ticker: 'FX' }, { status: 'ready', data: stmFx, statement: 'income', period: 'annual' });
  assert.ok(stm.includes('Source: SEC EDGAR companyfacts (filing-direct), updated 2026-10-15') && !stm.includes('companyfacts (filing-direct), as of'), 'Statements');
  assert.ok(App.renderStreet(synthetic).includes(', pulled 2026-10-14.') && App.renderForecastStreet(synthetic).includes(' — pulled 2026-10-14;'), 'the Street block keeps "pulled" (Nasdaq, re-fetched every run)');
  const priced = Object.assign({}, synthetic, { prices: { source: 'nasdaq historical', as_of: '2026-10-14', weekly: [['2026-10-02', 44], ['2026-10-09', 45]], daily_1y: [['2026-10-13', 44.5], ['2026-10-14', 45]], stats: {} } });
  assert.ok(App.renderPriceChart(priced).includes('Prices: nasdaq historical, through 2026-10-14.'), 'prices keep "through"');
  const all = App.TAB_KEYS.map((t) => App.renderCompanyHTML(synthetic, t)).join('');
  assert.ok(!/Profile as of|EDGAR submissions, as of|companyfacts[^<]*, as of|>Source:[^<]*\. As of/.test(all), 'no SEC file date is labelled "as of" on any tab');
});
test('fresh clone: the test record assembler serves street.json on record.profile as build_site does; the suite never needs the built caches', () => {
  const os = require('node:os'), dir = fs.mkdtempSync(path.join(os.tmpdir(), 'app-test-street-'));
  try {
    const { profileOf } = require('./fixtures/assemble.js');
    assert.equal(profileOf(dir), null, 'neither file: null');
    fs.writeFileSync(path.join(dir, 'profile.json'), JSON.stringify({ ticker: 'T', as_of: '2026-09-01', about: synthetic.profile.about, filings: [] }));
    assert.deepEqual(profileOf(dir), { ticker: 'T', as_of: '2026-09-01', about: synthetic.profile.about, filings: [], street: null, market: null, street_fetched_at: null }, 'profile.json alone: no Street yet');
    fs.writeFileSync(path.join(dir, 'street.json'), JSON.stringify({ ticker: 'T', as_of: '2026-10-16', fetched_at: '2026-10-16T07:01:02-04:00', street: { as_of: '2026-10-16', analysts: 3 }, market: { exchange: 'NYSE' } }));
    const p = profileOf(dir); assert.equal(p.as_of, '2026-09-01', 'profile.json keeps its own (content-change) date'); assert.deepEqual(p.street, { as_of: '2026-10-16', analysts: 3 }); assert.deepEqual(p.market, { exchange: 'NYSE' }); assert.equal(p.street_fetched_at, '2026-10-16T07:01:02-04:00');
    assert.ok(App.renderStreet({ score: { ticker: 'T' }, profile: p }).includes('based on 3 analysts') && App.renderAbout({ profile: p }).includes('Profile updated 2026-09-01'), 'the app reads the merged record');
    fs.unlinkSync(path.join(dir, 'street.json')); fs.writeFileSync(path.join(dir, 'profile.json'), JSON.stringify({ ticker: 'T', as_of: '2026-09-01', street: { analysts: 5 }, market: { exchange: 'NYSE' } }));
    assert.deepEqual(profileOf(dir).street, { analysts: 5 }, 'a legacy profile.json with street / market still serves them');
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
  // the empty states tell "not pulled yet" from "pulled, nothing there" per file: profile.json (SEC) and street.json (Nasdaq) arrive separately
  const secOnly = { score: { ticker: 'T' }, profile: { ticker: 'T', as_of: '2026-09-01', about: synthetic.profile.about, filings: [], street: null, market: null, street_fetched_at: null } };
  assert.ok(App.renderStreet(secOnly).includes('Street consensus appears once profile.py has pulled') && App.renderForecastStreet(secOnly).includes('Street consensus appears once profile.py has pulled') && App.renderForecastAnalysts(secOnly).includes('Analyst coverage appears once profile.py has pulled'), 'profile.json without street.json (a fresh clone): the Street is not pulled yet — not "no analyst data"');
  assert.ok(!App.renderAbout(secOnly).includes('Profile not pulled yet') && App.renderFilings(secOnly).includes('No filings on record.'), 'the SEC part is there');
  const pulledEmpty = { score: { ticker: 'T' }, profile: Object.assign({}, secOnly.profile, { street_fetched_at: '2026-10-16T07:01:02-04:00' }) };
  assert.ok(App.renderStreet(pulledEmpty).includes('No analyst data on record for this name.') && App.renderForecastAnalysts(pulledEmpty).includes('No analyst coverage data on record'), 'street.json pulled, Nasdaq had nothing');
  const nasdaqOnly = { score: { ticker: 'T' }, profile: { street: { analysts: 2 }, market: { exchange: 'NYSE' }, street_fetched_at: '2026-10-16T07:01:02-04:00' } };
  assert.ok(App.renderAbout(Object.assign({}, nasdaqOnly, { fundamentals: synthetic.fundamentals })).includes('Profile not pulled yet') && App.renderFilings(nasdaqOnly).includes('The EDGAR filing feed appears once profile.py has run'), 'street.json without profile.json: the SEC part is not pulled yet');
  assert.ok(App.renderStreet({ profile: { about: {} } }).includes('No analyst data') && App.renderStreet({ profile: { as_of: '2026-10-14', street: null } }).includes('No analyst data'), 'a record built before the split (no street_fetched_at key) reads as before');
  if (!HAVE_BUILT) console.log('  (no built data/, index.json, meta.json under ' + BUILT + ': real-record checks use assembled records or skip, as on a fresh clone)');
});

/* ---- PR #2 follow-ups (2026-10-16): restricted cash in the statements viewer, the dividends price note, a live.json older
   than the score, a split since scoring */
const clone = (o) => JSON.parse(JSON.stringify(o));
const rcFx = (() => { // stmFx with statements.py's restricted-cash marks: a combined cash + restricted total in FY2025 / FY2026 and the last two quarters
  const fx = clone(stmFx);
  const cash = fx.statements.balance[0];
  cash.label = 'Cash & equivalents (some periods incl. restricted cash)';
  cash.incl_restricted_annual = [false, true, true]; cash.incl_restricted_quarterly = [false, false, false, false, true, true]; cash.incl_restricted_ttm = true;
  fx.statements.balance.splice(1, 0, { key: 'restricted_cash', label: 'Restricted cash (included in cash above)', level: 2, total: false, unit: 'money', annual: [null, 2.0e8, null], quarterly: [null, null, null, null, null, null], ttm: null,
    growth_annual: [null, null, null], growth_quarterly: [null, null, null, null, null, null], derived_quarterly: [false, false, false, false, false, false], tags: [] });
  fx.statements.metrics.push({ key: 'net_cash', label: 'Net cash (debt) (some periods incl. restricted cash)', level: 0, total: false, unit: 'money', annual: [-1.0e9, 1.2e9, 3.0e9], quarterly: [1.0e9, 0.9e9, 1.1e9, 3.0e9, 0.4e9, null], ttm: 1.5e9,
    growth_annual: [null, null, 1.5], growth_quarterly: [null, null, null, null, null, null], derived_quarterly: [false, false, false, false, false, false],
    incl_restricted_annual: [false, false, true], incl_restricted_quarterly: [false, false, false, false, true, true], incl_restricted_ttm: false, tags: [] });
  return fx;
})();
test('statements viewer: restricted cash — ‡ (with its title) on exactly the cells statements.py flags incl_restricted_*, a legend line only when a cell is marked', () => {
  const ir = (M, key) => M.rows.find((r) => r.key === key).cells.map((c) => c.inclRestricted);
  const A = App.stmTable(rcFx, 'balance', 'annual'); // columns newest first: FY2026 (i 2), FY2025 (i 1), FY2024 (i 0)
  assert.deepEqual(ir(A, 'cash'), [true, true, false]); assert.deepEqual(ir(A, 'restricted_cash'), [false, false, false], 'the Restricted cash line itself is never marked');
  assert.equal(A.anyInclRestricted, true); assert.equal(A.rows.find((r) => r.key === 'cash').anyInclRestricted, true);
  assert.deepEqual(ir(App.stmTable(rcFx, 'balance', 'ttm'), 'cash'), [true, true, true, false], 'the Current column reads incl_restricted_ttm');
  assert.deepEqual(ir(App.stmTable(rcFx, 'balance', 'quarterly'), 'cash'), [true, true, false, false, false, false], 'quarterly: per column, newest first');
  assert.deepEqual(ir(App.stmTable(rcFx, 'metrics', 'quarterly'), 'net_cash'), [false, true, false, false, false, false], 'a flag on an empty cell (Q2 FY2027 net cash) marks nothing');
  assert.deepEqual(ir(App.stmTable(rcFx, 'metrics', 'ttm'), 'net_cash'), [false, true, false, false], 'net cash: TTM false, FY2026 unsplit');
  assert.equal(App.stmTable(rcFx, 'income', 'annual').anyInclRestricted, false); assert.equal(App.stmTable(stmFx, 'balance', 'annual').anyInclRestricted, false, 'no flags → nothing marked');
  const rec = { ticker: 'FX', score: { ticker: 'FX' } };
  const bal = App.renderStatements(rec, { status: 'ready', data: rcFx, statement: 'balance', period: 'annual' });
  const marks = bal.match(/<sup class="rcash" title="[^"]*">‡<\/sup>/g) || [];
  assert.equal(marks.length, 2, 'one ‡ per marked cell'); assert.ok(marks[0].includes('title="' + App.esc(App.RESTRICTED_TITLE) + '"'));
  assert.equal(App.RESTRICTED_TITLE, 'includes restricted cash: the filed cash + restricted cash total; net cash deducts the restricted part where the Restricted cash line shows it, otherwise still counts it');
  assert.ok(bal.includes('>4,600<sup class="rcash"') && bal.includes('>1,400<sup class="rcash"') && bal.includes('>1,900</td>'), 'FY2026 and FY2025 marked, FY2024 not');
  assert.ok(bal.includes('‡ includes restricted cash; growth is blank where one period deducts it and the other does not.'), 'legend line');
  assert.ok(bal.includes('Restricted cash (included in cash above)') && bal.includes('Cash &amp; equivalents (some periods incl. restricted cash)'), 'the lines statements.py labels');
  const both = App.renderStatements(rec, { status: 'ready', data: rcFx, statement: 'metrics', period: 'quarterly' });
  assert.equal((both.match(/‡<\/sup>/g) || []).length, 1); assert.ok(both.includes('‡ includes restricted cash'));
  const der = App.renderStatements(rec, { status: 'ready', data: rcFx, statement: 'cashflow', period: 'quarterly' });
  assert.ok(der.includes('†</sup>') && !der.includes('‡') && !der.includes('includes restricted cash'), 'no mark, no legend where nothing is flagged (the † legend unaffected)');
  assert.ok(!App.renderStatements(rec, { status: 'ready', data: stmFx, statement: 'balance', period: 'annual' }).includes('‡'));
  // the committed NTRS file (FY2025 5,873.1M includes 531.2M restricted): every flagged valued cell carries one ‡. The committed
  // file first — a served copy built before the restricted-cash split carries no flags
  const own = path.join(BASE, 'NTRS', 'statements.json'), p = fs.existsSync(own) ? own : statementsPath('NTRS');
  if (!p || !fs.readFileSync(p, 'utf8').includes('incl_restricted_')) skip('NTRS restricted-cash marks — needs an NTRS statements.json built with the restricted-cash split');
  else {
    const d = JSON.parse(fs.readFileSync(p, 'utf8'));
    ['balance', 'metrics'].forEach((st) => ['annual', 'quarterly', 'ttm'].forEach((pd) => {
      const M = App.stmTable(d, st, pd), html = App.renderStatements({ ticker: 'NTRS' }, { status: 'ready', data: d, statement: st, period: pd });
      const want = M.rows.reduce((s, r) => s + r.cells.filter((c) => c.inclRestricted).length, 0);
      const flagged = arr2(d.statements[st]).reduce((s, L) => s + M.cols.filter((c) => { const v = c.src === 'ttm' ? L.ttm : (L[c.src] || [])[c.i]; return v !== null && v !== undefined && (c.src === 'ttm' ? L.incl_restricted_ttm === true : (L['incl_restricted_' + c.src] || [])[c.i] === true); }).length, 0);
      assert.equal(want, flagged, 'NTRS ' + st + ' ' + pd + ': the model marks every flagged valued cell');
      assert.equal((html.match(/‡<\/sup>/g) || []).length, want, 'NTRS ' + st + ' ' + pd + ': one ‡ per marked cell');
      assert.equal(html.includes('‡ includes restricted cash'), want > 0, 'NTRS ' + st + ' ' + pd + ': legend iff marked');
    }));
    assert.ok(App.stmTable(d, 'balance', 'annual').anyInclRestricted, 'NTRS balance has marked cells');
  }
});
function arr2(x) { return Array.isArray(x) ? x.filter((l) => l && typeof l === 'object') : []; }

test('Dividends: the yields name the price they stand on from price_source (last close · scored price, no prices.json yet · none); price_note leads the notes, once', () => {
  const withDiv = (over) => { const r = clone(synthetic); Object.assign(r.fundamentals.dividends, over); return r; };
  const closeRec = withDiv({ price: 45, price_date: '2026-10-14', price_source: 'prices.json stats.last', price_note: null });
  const h1 = App.renderDividends(closeRec);
  assert.ok(h1.includes('Yields use the last close $45.00 (2026-10-14).') && h1.includes('TTM DPS ÷ $45.00'), 'prices.json close');
  assert.ok(!/<li>price: /.test(h1), 'no price note without one');
  const pn = 'price: 50.0 from score.json (2026-10-14); prices.json absent';
  const scored = withDiv({ price: 50, price_date: '2026-10-14', price_source: 'score.json price', price_note: pn, notes: synthetic.fundamentals.dividends.notes.concat([pn]) });
  const h2 = App.renderDividends(scored);
  assert.ok(h2.includes('Yields use the scored price $50.00 (2026-10-14), no prices.json yet.'), 'score.json price');
  assert.ok(h2.includes('<ul class="warnlist"><li>' + App.esc(pn) + '</li><li>annual_dps:'), 'price_note is the first item');
  assert.equal(h2.split(App.esc(pn)).length - 1, 1, 'printed once even when an older block also carries it in notes');
  const noPx = withDiv({ price: null, price_date: null, price_source: null, market_cap: null, dividend_yield: null, price_note: 'price: neither prices.json nor score.json carries a price — yields null' });
  const h3 = App.renderDividends(noPx);
  assert.ok(h3.includes('No price is on file, so the yields are blank.') && h3.includes('no price on file') && h3.includes('<li>price: neither prices.json nor score.json carries a price — yields null</li>') && !h3.includes('Yields use'), 'no price');
  const nonPayer = withDiv({ frequency: 'none', dps_ttm: null, dividends_paid_ttm: 0, history: [], annual_dps: [], price: null, price_source: null });
  assert.ok(App.renderDividends(nonPayer).includes('no price is on file, so the yields below are blank.'), 'non-payer without a price');
  assert.ok(App.renderDividends(withDiv({ frequency: 'none', dps_ttm: null, dividends_paid_ttm: 0, history: [], annual_dps: [] })).includes('the yields below use the last close $45.00 (2026-10-14).'), 'non-payer with a close');
  assert.ok(App.renderDividends(synthetic).includes('Yields use the last close $45.00 (2026-10-14).'), 'an older block (price_source "prices.json", no price_note) reads as before');
  // a split since scoring: build_site shows the block as written (never repriced across the split)
  const sp = { factor: 2, split: '2:1', scored_date: '2026-10-14', price_date: '2026-10-20', as_scored: {}, note: 'n' };
  const split = Object.assign(withDiv({ price: 45, price_date: '2026-10-14', price_source: 'prices.json stats.last' }), { split_restated: sp });
  const h4 = App.renderDividends(split);
  assert.ok(h4.includes('Yields use $45.00 on 2026-10-14, before the 2:1 split.') && h4.includes('a split the filings do not report yet is not reflected'), 'block at its own pre-split price');
  assert.equal(App.divPriceWords({ price: 45, price_date: '2026-10-16', price_source: 'prices.json stats.last' }, App.splitInfo(split)), '$45.00 on 2026-10-16 — not repriced across the 2:1 split since scoring', 'a block priced after the scored date: no "before" claim');
  assert.equal(App.divPriceWords({ price: null }, null), null); assert.equal(App.divPriceWords({ price: 3.5 }, null), 'the last close $3.50', 'no date: no empty parentheses');
  assert.ok(!App.renderDividends(inject(scored)).includes('<x-inj>'), 'price_note escaped');
});

/* A record as build_site writes it when live.json's close predates the scored analysis (live_shown). */
const withheldNote = 'The last close on file (2026-10-13) predates the scored analysis (2026-10-14) — no close after the analysis is on file, so the scored figures are the latest available, as of the 2026-10-13 close.';
const withheldRec = (() => {
  const r = clone(synthetic);
  r.live = null;
  r.live_withheld = { reason: 'live_older_than_score', price: 44, price_date: '2026-10-13', scored_date: '2026-10-14', method: 'no_close_since_scoring', note: withheldNote };
  Object.assign(r.row, { tier_live: null, irr_live: null, price_live: null, price_date: null, upside15_live: null, market_cap_b_live: null, live_withheld: true });
  Object.keys(r.forecast.sensitivity).forEach((k) => { r.forecast.sensitivity[k].irr_live = null; });
  r.prices = { source: 'nasdaq historical', as_of: '2026-10-13', stats: { last: 44, last_date: '2026-10-13', change_1d_pct: -1.5, low_52w: 38.4, high_52w: 55.2, ret_1y_pct: 12.5 }, weekly: [['2026-10-02', 45], ['2026-10-09', 44.5]], daily_1y: [] };
  return r;
})();
test('Live older than the score: the header and the condensed bar show the scored price with the reason, never the older close; Overview / Forecast tiles present the scored figures as the latest available', () => {
  const v = App.liveView(withheldRec); assert.equal(v.is_live, false); assert.equal(v.price, 50); assert.equal(v.irr, 0.142);
  const w = App.liveWithheld(withheldRec); assert.deepEqual(w, { reason: 'live_older_than_score', price: 44, price_date: '2026-10-13', scored_date: '2026-10-14', method: 'no_close_since_scoring', note: withheldNote });
  assert.equal(App.latestText(w), 'Scored figures are the latest — the 2026-10-13 close on file predates the 2026-10-14 analysis');
  assert.equal(App.latestText({ reason: 'live_from_earlier_run', price_date: '2026-10-13', scored_date: '2026-10-16' }), 'Scored figures are the latest — the live repricing on file predates the 2026-10-16 score', 'the reason decides, not the dates: an earlier run\'s close predates the new score too');
  assert.equal(App.latestText({ price_date: '2026-10-17', scored_date: '2026-10-16' }), 'Scored figures are the latest — the live repricing on file predates the 2026-10-16 score', 'no reason recorded: the date inference still applies');
  assert.equal(App.liveWithheld(synthetic), null); assert.equal(App.liveWithheld({ live_withheld: null }), null); assert.equal(App.latestText({}), 'Scored figures are the latest — the last close on file predates the analysis');
  assert.equal(App.currentClose(withheldRec), null, 'the 2026-10-13 close predates the 2026-10-14 analysis');
  const head = App.renderHeader(withheldRec);
  assert.ok(head.includes('<span class="k">Scored price</span><span class="v mono">$50.00</span>'), 'scored price as the current price: ' + head);
  assert.ok(head.includes('title="' + App.esc(withheldNote) + '">Scored figures are the latest — the 2026-10-13 close on file predates the 2026-10-14 analysis</span>'), 'the reason beside it, the note in the tooltip');
  assert.ok(!head.includes('$44.00') && !head.includes('-1.50%') && head.includes('52-wk $38.40–$55.20'), 'not the older close nor its 1-day change; the 52-week range stays');
  assert.ok(head.includes('Probability-weighted IRR at $50.00') && !head.includes('· live'), 'the scored IRR');
  const sum = App.renderTabSummary(withheldRec);
  assert.ok(sum.includes('title="Scored price — the latest available">$50.00') && !sum.includes('$44.00') && !sum.includes('-1.50%'), 'condensed bar: ' + sum);
  // a close not older than the analysis is current again (prices.py ran after the scored session; reprice has not yet)
  const fresh = clone(withheldRec); fresh.prices.stats.last_date = '2026-10-14';
  assert.deepEqual(App.currentClose(fresh), { last: 44, date: '2026-10-14', chg: -1.5 });
  const fh = App.renderHeader(fresh); assert.ok(fh.includes('<span class="k">Last close</span>') && fh.includes('$44.00') && fh.includes('Scored figures are the latest'), 'current close, the scored figures still badged as the latest');
  // nothing withheld: unchanged — the last close shows whatever its date (AEE-style record without live.json)
  const plain = clone(withheldRec); delete plain.live_withheld; plain.row.live_withheld = false;
  assert.equal(App.currentClose(plain).last, 44); assert.ok(App.renderHeader(plain).includes('<span class="k">Last close</span>') && !App.renderHeader(plain).includes('pending'));
  assert.ok(App.renderTabSummary(plain).includes('$44.00') && App.renderTabSummary(plain).includes('-1.50%'));
  const ov = App.renderOverview(withheldRec); assert.ok(ov.includes('scored 2026-10-14 · latest available') && ov.includes('title="Scored figures are the latest'), 'Overview price tile');
  const fc = App.renderForecastDCF(withheldRec);
  assert.ok(fc.includes('<span class="k">Scored price</span><span class="v ">$50.00</span><span class="tsub">Scored figures are the latest — the 2026-10-13 close on file predates the 2026-10-14 analysis') && fc.includes('Green = at or above the scored price') && !fc.includes("Today's price"), 'Forecast hurdle tiles');
  // Andrew's ruling (2026-10-20): in this state the scored figures ARE the latest available — no surface calls them pending
  [head, sum, fh, ov, fc].forEach((h) => assert.ok(!/pending/i.test(h), 'no "pending" wording for the latest-available state'));
  App.TAB_KEYS.forEach((t) => { const h = App.renderCompanyHTML(withheldRec, t); assert.ok(!h.includes('could not be rendered'), t); });
  assert.ok(!App.TAB_KEYS.map((t) => App.renderCompanyHTML(inject(withheldRec), t)).join('').includes('<x-inj>'), 'escaped');
});
test('Live older than the score: the ranking marks the row "scored · latest" and ranks it on its scored IRR; the header counts the latest-available rows', () => {
  const row = withheldRec.row, html = App.renderRowHTML(row);
  assert.ok(/<td class="num mono strong"><span class="sub lvpend" title="The scored figures are the latest available: [^"]*">scored · latest<\/span><\/td>/.test(html), 'Live IRR cell: ' + html);
  assert.ok(html.includes('title="scored price — the latest available">$50.00</td>') && html.includes('>14.2%</td>'), 'scored price and IRR');
  assert.ok(!/pending/i.test(html), 'no "pending" wording in the row');
  assert.ok(!App.renderRowHTML(Object.assign({}, row, { live_withheld: false })).includes('scored · latest'), 'no marker otherwise');
  assert.ok(!App.renderRowHTML(synthetic.row).includes('scored · latest'), 'a live row never');
  const rows = [Object.assign({}, row, { ticker: 'W' }), Object.assign({}, synthetic.row, { ticker: 'L1', irr_live: 0.15, irr: 0.1 }), Object.assign({}, synthetic.row, { ticker: 'L2', irr_live: 0.13, irr: 0.2 })];
  assert.deepEqual(App.filterSortIndex(rows, { sort: 'irr_live', fit: 'all' }).map((r) => r.ticker), ['L1', 'W', 'L2'], 'ranked on the scored IRR (14.2%) between 15% and 13% live');
  const m = Object.assign({}, meta, { counts: Object.assign({}, meta.counts, { with_live: 2, live_withheld: 1 }) });
  assert.ok(App.renderListHTML(m, rows).includes('(2 of 3 repriced live, 1 at their scored figures (the latest available); the rest at their scored price)'));
  const noCount = Object.assign({}, m, { counts: { tiers: {} } });
  assert.ok(App.renderListHTML(noCount, rows).includes('1 at their scored figures (the latest available)'), 'counted from the rows without meta.counts.live_withheld');
  assert.ok(!App.renderListHTML(noCount, rows.slice(1)).includes('at their scored figures'), 'none withheld: no clause');
});
test('fixtures/assemble.js mirrors build_site: a live.json older than the later of analysis_date / live.scored_date is withheld; a split since scoring restates the run once', () => {
  const os = require('node:os'), dir = fs.mkdtempSync(path.join(os.tmpdir(), 'app-test-live-'));
  const { assemble: asm, liveShown, liveSplit, SPLIT_DIVIDE, SPLIT_MULTIPLY } = require('./fixtures/assemble.js');
  const put = (f, o) => fs.writeFileSync(path.join(dir, 'T', f), typeof o === 'string' ? o : JSON.stringify(o));
  try {
    fs.mkdirSync(path.join(dir, 'T'));
    const score = Object.assign(clone(synthetic.score), { ticker: 'T' }), numbers = Object.assign(clone(synthetic.numbers), { inputs: Object.assign(clone(synthetic.numbers.inputs), { base_oe_ps_arg: 3.2 }), hurdle_prices: { 15: 60, 20: 45.5, 25: 36 } });
    delete score.iv_at_20; // the row's iv20 then falls back to live.json's
    put('score.json', score); put('dcf_numbers.json', numbers);
    put('financials_history.csv', 'period_end,fy_label,revenue,oe_conservative,shares_diluted\n2024-12-31,2024,2000000000,320000000,100000000\n');
    put('ttm.json', { ttm_oe_total: 343000000, ttm_shares_diluted: 98500000, ttm_oe_per_share: 3.4822 });
    const live = Object.assign(clone(synthetic.live), { ticker: 'T', price_date: '2026-10-13', scored_date: '2026-10-14', basis_check: { method: 'no_close_since_scoring' } });
    put('live.json', live);
    let r = asm(dir, 'T');
    assert.equal(r.live, null); assert.equal(r.row.live_withheld, true); assert.equal(r.row.irr_live, null); assert.equal(r.row.price_live, null); assert.equal(r.forecast.sensitivity.weighted.irr_live, null);
    assert.deepEqual(r.live_withheld, { reason: 'live_older_than_score', price: 45, price_date: '2026-10-13', scored_date: '2026-10-14', method: 'no_close_since_scoring', note: withheldNote });
    assert.equal(r.split_restated, null);
    put('live.json', Object.assign({}, live, { price_date: '2026-10-14' })); r = asm(dir, 'T');
    assert.ok(r.live && r.live_withheld === null && r.row.live_withheld === false && r.row.irr_live === 0.161, 'a same-day close is shown');
    put('live.json', Object.assign({}, live, { price_date: '2026-10-14', scored_date: '2026-10-15' })); r = asm(dir, 'T');
    assert.equal(r.live, null, 'the later of analysis_date and live.scored_date counts'); assert.equal(r.live_withheld.scored_date, '2026-10-15');
    put('live.json', Object.assign({}, live, { price: null })); r = asm(dir, 'T');
    assert.ok(r.live === null && r.live_withheld === null && r.row.live_withheld === false, 'a live.json without a price is not shown and not "withheld"');
    assert.deepEqual(liveShown(score, null), { live: null, withheld: null });
    // a split since scoring: live.json in today's units (÷ 2) with split_factor 2
    const half = (o) => Object.assign({}, o, { price: o.price / 2, scored_price: o.scored_price / 2, iv_at_15: o.iv_at_15 / 2, iv_at_12: o.iv_at_12 / 2, iv_at_20: o.iv_at_20 / 2, iv_at_25: o.iv_at_25 / 2 });
    const splitLive = Object.assign(half(live), { price_date: '2026-10-20', split_factor: 2, basis_check: { status: 'split_adjusted', factor: 2, split: '2:1', method: 'ratio' } });
    put('live.json', Object.assign({}, live, { price_date: '2026-10-20' })); const base = asm(dir, 'T');
    put('live.json', splitLive); r = asm(dir, 'T');
    assert.deepEqual(r.row.split_restated, { factor: 2, split: '2:1' }); assert.equal(r.split_restated.factor, 2); assert.equal(r.split_restated.scored_date, '2026-10-14'); assert.equal(r.split_restated.price_date, '2026-10-20');
    assert.deepEqual(r.split_restated.as_scored, { price: 50, iv_at_15: 60, base_oe_per_share: 3.2 });
    assert.ok(r.split_restated.note.startsWith('A 2:1 split since the scored run (2026-10-14): every per-share figure of the run') && r.split_restated.note.includes('divided by 2 and its share counts multiplied by 2'));
    [['score.price', 25], ['score.iv_at_15', 30], ['numbers.price', 25], ['numbers.weighted.iv_at_15', 30], ['row.price', 25], ['row.iv15', 30], ['numbers.inputs.base_oe_ps_arg', 1.6], ['forecast.inputs.base_oe_ps_arg', 1.6],
      ['numbers.hurdle_prices.20', 22.75], ['forecast.hurdle_prices.20', 22.75], ['forecast.sensitivity.weighted.15', 30], ['ttm.ttm_oe_per_share', 1.7411],
      ['numbers.shares_diluted_latest', 2e8], ['ttm.ttm_shares_diluted', 1.97e8], ['row.irr', 0.142], ['row.irr_live', 0.161], ['score.implied_irr', 0.142]].forEach(([p, want]) => {
      const got = p.split('.').reduce((o, k) => (o == null ? o : o[k]), r); assert.ok(Math.abs(got - want) < 1e-9, p + ' = ' + got + ', want ' + want + ' (divided once)');
    });
    assert.equal(r.history[0].shares_diluted, 2e8, 'engine history shares × 2');
    assert.ok(Math.abs(r.row.iv20 - splitLive.iv_at_20) < 1e-9 && Math.abs(r.row.iv20 - base.row.iv20 / 2) < 1e-9, 'the live.json iv20 fallback (today\'s units) is restated exactly once');
    assert.ok(r.split_restated.fields.includes('score.price') && r.split_restated.fields.includes('history.*.shares_diluted') && r.split_restated.fields.every((f) => SPLIT_DIVIDE.includes(f) || SPLIT_MULTIPLY.includes(f)));
    assert.deepEqual(liveSplit({ split_factor: 1 }), { factor: null, label: null }); assert.deepEqual(liveSplit({ basis_check: { factor: 3 } }), { factor: 3, label: '3x' });
    put('live.json', Object.assign({}, splitLive, { split_factor: 1, basis_check: {} })); assert.equal(asm(dir, 'T').split_restated, null, 'factor 1: nothing restated');
    put('live.json', Object.assign({}, splitLive, { price_date: '2026-10-13' })); r = asm(dir, 'T');
    assert.ok(r.live === null && r.split_restated === null && r.score.price === 50, 'a withheld live.json\'s split factor is not applied');
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

/* A record as build_site writes it after a 2:1 split since scoring: fixtures/assemble.js's restateSplit on the synthetic record
   (the mirror of build_site.restate_split), with live.json in today's units as reprice.py writes it. */
const splitLiveFx = Object.assign(clone(synthetic.live), { price: 22.5, scored_price: 25, iv_at_15: 30, iv_at_12: 40, iv_at_20: 22.75, iv_at_25: 18, price_date: '2026-10-20', split_factor: 2, basis_check: { status: 'split_adjusted', factor: 2, split: '2:1' } });
const splitRec = (() => { // the row's live fields come from live.json (today's units), like build_site's index_row
  const r = require('./fixtures/assemble.js').restateSplit(clone(synthetic), 2, '2:1', splitLiveFx); r.live = clone(splitLiveFx); r.row.price_live = splitLiveFx.price; r.row.price_date = splitLiveFx.price_date; return r;
})();
test('Split since scoring: the run reads in today\'s units (restated fields), a header chip, a short note by the verdict, notes on Forecast / Data / Analysis / Financials, a ranking badge', () => {
  const sp = App.splitInfo(splitRec);
  assert.deepEqual([sp.factor, sp.split, sp.scored_date, sp.price_date], [2, '2:1', '2026-10-14', '2026-10-20']); assert.deepEqual(sp.as_scored, { price: 50, iv_at_15: 60, base_oe_per_share: 3.2 });
  [null, {}, { factor: 1 }, { factor: 0 }, { factor: 'x' }].forEach((x) => assert.equal(App.splitInfo({ split_restated: x }), null, JSON.stringify(x)));
  assert.equal(App.splitInfo({ split_restated: { factor: 0.1 } }).split, '0.1x'); assert.equal(App.fmtFactor(2.0), '2'); assert.equal(App.fmtFactor(1.5), '1.5');
  const v = App.liveView(splitRec); assert.equal(v.price, 22.5); assert.equal(v.scored_price, 25); assert.ok(Math.abs(v.upside - 33.333) < 0.01, 'upside unchanged');
  const head = App.renderHeader(splitRec);
  assert.ok(head.includes('<span class="chip lvchip splitchip" title="' + App.esc(splitRec.split_restated.note) + '">Restated for a 2:1 split since scoring</span>'), 'header chip');
  assert.ok(head.includes('$30.00') && head.includes('Scored <b>14.2%</b> at $25.00') && head.includes('$22.50'), 'Value @15%, scored price and last close in today\'s units');
  const page = App.renderCompanyHTML(splitRec, 'overview');
  const brief = page.indexOf('<p class="note splitnote"><b>Restated for a 2:1 split since scoring</b> (scored 2026-10-14): every per-share figure of the run on this page is in today\'s share units (÷ 2)');
  assert.ok(brief > page.indexOf('class="sec pcsec"') && brief < page.indexOf('class="card verdict"'), 'the short note sits between the price chart and the verdict');
  const ov = App.renderOverview(splitRec); assert.ok(ov.includes('IV @15% <b>$40.00</b>') && ov.includes('$1.60<span class="bu"> / share</span>') && ov.includes('>$22.75<'), 'scenario IV, base OE and hurdle tiles restated');
  const fc = App.renderForecastDCF(splitRec);
  assert.ok(fc.startsWith('<p class="note splitnote"><b>Restated for a 2:1 split since scoring.</b> ' + App.esc(splitRec.split_restated.note) + ' Scored at $50.00 with IV @15% $60.00 before the split.</p>'), 'Forecast note: ' + fc.slice(0, 300));
  assert.ok(fc.includes('<td class="num mono pos">$30.00</td>') && fc.includes('Price for 25% (Tier S)</span><span class="v neg">$18.00'), 'sensitivity and hurdle prices restated');
  const data = App.renderData(splitRec);
  assert.ok(data.startsWith('<p class="note splitnote"><b>Restated for a 2:1 split since scoring.</b>') && data.includes('judgment.json below is the run\'s input as entered, before the split.'), 'Data note');
  assert.ok(data.includes('$25.00 (nasdaq_quote_api) · scored at $50.00 before the 2:1 split') && data.includes('diluted shares 200.0M (restated × 2)') && data.includes('$1.60/share (scored $3.20 before the 2:1 split)') && data.includes('<th>Split since scoring</th><td>2:1 (factor 2) · scored 2026-10-14 · restated against the 2026-10-20 close · IV @15% as scored $60.00</td>'), 'Data provenance rows');
  const an = App.renderAnalysis(splitRec); assert.ok(an.startsWith('<p class="note splitnote"><b>2:1 split since scoring.</b> The write-up quotes the run as scored (2026-10-14), before the split: divide its per-share dollar figures') && an.includes('by 2 to compare'), 'Analysis note');
  const fin = App.renderFinancials(splitRec, { status: 'missing' }); assert.ok(fin.startsWith('<p class="note splitnote"><b>2:1 split since scoring.</b> Per-share figures in the filed statements on this tab'), 'Financials note');
  assert.ok(App.renderFinancials(Object.assign({}, splitRec, { fundamentals: null })).includes('engine history\'s share counts are restated to today\'s share units (× 2)'));
  assert.ok(App.renderPerformance(splitRec).includes('filings before the 2:1 split since scoring are on the pre-split basis'));
  const row = App.renderRowHTML(splitRec.row);
  assert.ok(/<span class="bdg sp" title="A 2:1 split since scoring: [^"]*">2:1 split since scoring<\/span>/.test(row) && row.includes('>$30.00</td>') && row.includes('>$22.50</td>'), 'ranking badge, restated IV and live price');
  const ovr = clone(splitRec); ovr.numbers.overrides_applied = [{ field: 'shares', value: 98500000, kind: 'filing', source: 'Form 10-K', reason: '', periods_filled: ['2024-12-31'] }];
  assert.ok(App.renderOverrides(ovr).includes('Override values are as entered for the scored run, before the 2:1 split since scoring'), 'overrides as entered');
  // no split: none of it
  const none = App.TAB_KEYS.map((t) => App.renderCompanyHTML(synthetic, t)).join('') + App.renderRowHTML(synthetic.row);
  assert.ok(!none.includes('splitnote') && !none.includes('split since scoring') && !none.includes('split-adjusted') && !none.includes('splitchip'), 'nothing without split_restated');
  App.TAB_KEYS.forEach((t) => { const h = App.renderCompanyHTML(splitRec, t); assert.ok(!h.includes('could not be rendered'), t); });
  assert.ok(!App.TAB_KEYS.map((t) => App.renderCompanyHTML(inject(splitRec), t)).join('').includes('<x-inj>') && !App.renderRowHTML(inject(splitRec).row).includes('<x-inj>'), 'escaped');
});
test('Split since scoring: filed OE/share years still on the pre-split basis are ÷ factor next to the restated forecast (a post-split refiling is left alone); Street EPS "from" figures too', () => {
  const H = App.oeHistory(splitRec);
  assert.deepEqual(H.map((h) => [h.fy, Math.round(h.v * 1e4) / 1e4, h.split || 0]), [['2023', 1.38, 2], ['2024', 1.6, 2]], 'FY2023 (no run row: vs the restated latest count) and FY2024 (vs the run\'s own FY2024 count) ÷ 2');
  assert.deepEqual(H.map((h) => h.sh), [2.08e8, 2e8], 'their counts × 2, so the basis rule compares like with like');
  const J = App.oeForecastSeries(splitRec); assert.equal(J.base, 1.6); assert.equal(J.raw.weighted[0], 1.7, 'forecast restated by build_site'); assert.ok(Math.abs(J.histGrowth[1] - (1.6 / 1.38 - 1)) < 1e-9, 'YoY on the adjusted pair');
  const fc = App.renderForecastDCF(splitRec);
  assert.equal((fc.match(/Filed years on the pre-split basis \(FY2023–FY2024\) are divided by 2 for the 2:1 split since scoring/g) || []).length, 2, 'under the OE/share chart and the growth chart');
  // FY2024 refiled after the split (its comparatives restated): ~1× the run's restated count → as filed; FY2023 still pre-split
  const refiled = clone(splitRec); Object.assign(refiled.fundamentals.annual[1], { shares_diluted: 2e8, oe_per_share: 1.6 });
  assert.deepEqual(App.oeHistory(refiled).map((h) => [h.fy, Math.round(h.v * 1e4) / 1e4, h.split || 0]), [['2023', 1.38, 2], ['2024', 1.6, 0]]);
  assert.ok(App.renderForecastDCF(refiled).includes('Filed years on the pre-split basis (FY2023) are divided by 2'));
  const allPost = clone(refiled); Object.assign(allPost.fundamentals.annual[0], { shares_diluted: 2.08e8, oe_per_share: 1.38 });
  assert.ok(App.oeHistory(allPost).every((h) => !h.split) && App.renderForecastDCF(allPost).includes('The filed years shown are already on the post-split basis of the 2:1 split since scoring'));
  // a fiscal year ending after the scored date is never divided
  const later = clone(splitRec); later.fundamentals.annual.push(Object.assign(clone(later.fundamentals.annual[1]), { fy: '2026', period_end: '2026-12-31' }));
  assert.equal(App.oeHistory(later).slice(-1)[0].split, undefined);
  const sp = App.splitInfo(splitRec), refs = App.splitRefs(splitRec);
  assert.deepEqual(refs, { byEnd: { '2024-12-31': 2e8 }, byFy: { 2024: 2e8 }, latest: 2e8 });
  assert.equal(App.splitDivisor(sp, refs, 1e8, '2024-12-31', '2024'), 2); assert.equal(App.splitDivisor(sp, refs, 1.9e8, '2024-12-31', '2024'), 1); assert.equal(App.splitDivisor(sp, refs, null, '2024-12-31'), 1); assert.equal(App.splitDivisor(null, refs, 1e8), 1);
  assert.equal(App.splitDivisor(sp, { byEnd: {}, byFy: {}, latest: null }, 1e8, '2020-12-31'), 1, 'no reference: left as filed');
  const rev = { factor: 0.1, split: '1:10', scored_date: '2026-10-14' }; assert.equal(App.splitDivisor(rev, { byEnd: {}, byFy: {}, latest: 1e7 }, 1e8, '2025-12-31'), 0.1, 'a 1:10 reverse split: the pre-split count is 10× today\'s');
  assert.equal(App.oeSplitNote(H, null), ''); assert.equal(App.oeSplitNote([], sp), '');
  assert.ok(App.oeHistory(synthetic).every((h) => !h.split), 'no split: untouched');
  assert.deepEqual(App.oeHistory(synthetic).map((h) => h.v), [2.76, 3.2]);
  // Street: Nasdaq's consensus is in today's units — the filed EPS it is measured from is split-adjusted where pre-split
  const eps = App.epsAnnualHist(splitRec); assert.deepEqual(eps.map((h) => [h.fy, h.v, h.split]), [['2023', 0.625, 2], ['2024', 0.75, 2]]); assert.equal(eps[1].g, 0.2, 'same basis both years: the filed growth stands');
  refiled.fundamentals.annual[1].eps_diluted = 0.8; const mixed = App.epsAnnualHist(refiled); assert.ok(Math.abs(mixed[1].g - (0.8 / 0.625 - 1)) < 1e-9 && mixed[1].split === 0, 'the growth across the two bases is recomputed on the adjusted values (not the filed 20%)');
  const st = App.renderForecastStreet(splitRec);
  assert.ok(st.includes('from $0.75 (FY2024 filed, split-adjusted)'), 'annual from');
  assert.ok(st.includes('from $0.19 (Q1 FY2025 filed, split-adjusted)'), 'quarterly from (vs the restated latest count)');
  assert.ok(st.includes('After the 2:1 split since scoring the filed columns stay as filed') && st.includes('Solid line: filed diluted EPS by fiscal year (years on the pre-split basis ÷ 2 for the 2:1 split since scoring).'), 'Street notes');
  assert.ok(st.includes('<td>$1.50</td>'), 'the filed column itself stays as filed');
  assert.equal(App.chartSpecsStreet(splitRec)['street-eps'].series[1].name, 'Filed diluted EPS (split-adjusted)');
  assert.deepEqual(App.chartSpecsStreet(splitRec)['street-eps'].series[1].values.slice(0, 2), [0.625, 0.75]);
  const plainSt = App.renderForecastStreet(synthetic); assert.ok(plainSt.includes('from $1.50 (FY2024 filed)') && !plainSt.includes('split-adjusted') && !plainSt.includes('split since scoring'), 'no split: as before');
  assert.deepEqual(App.yearAgoQuarterAdj(synthetic, { period: 'Q1 2026' }, synthetic.fundamentals.quarterly), App.yearAgoQuarter({ period: 'Q1 2026' }, synthetic.fundamentals.quarterly));
});

Promise.all(pending).then(() => {
  const failed = results.filter((r) => r[1]);
  results.forEach((r) => console.log((r[1] ? 'FAIL ' : 'ok   ') + r[0]));
  failed.forEach((r) => { console.error('\n--- ' + r[0] + '\n' + (r[1].stack || r[1])); });
  console.log('\n' + (results.length - failed.length) + ' passed, ' + failed.length + ' failed' + (Object.keys(loaded).length ? ' · records: ' + Object.keys(loaded).map((t) => t + ' (' + loaded[t].source + ')').join(', ') : '')
    + (skipped.length ? ' · ' + skipped.length + ' real-data check' + (skipped.length === 1 ? '' : 's') + ' skipped (' + (HAVE_BUILT ? 'files absent' : 'no built data/: a fresh clone') + ')' : ''));
  process.exit(failed.length ? 1 : 0);
});
