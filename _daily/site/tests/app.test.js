'use strict';
/* Tests for _daily/site/app.js. Run: node _daily/site/tests/app.test.js (zero dependencies).
   Loads app.js via require (the module.exports branch), the real data/<T>.json records for
   APP, KR and AEE when the data layer has written them (else a fixture assembled from the
   company folders), and the synthetic fixture that carries dividends, segments and live. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const SITE = path.resolve(__dirname, '..');
const BASE = path.resolve(SITE, '..', '..');
const App = require(path.join(SITE, 'app.js'));
const { assemble } = require('./fixtures/assemble.js');

const results = [];
function test(name, fn) {
  try { fn(); results.push([name, null]); }
  catch (e) { results.push([name, e]); }
}
function loadRecord(t) {
  const p = path.join(SITE, 'data', t + '.json');
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
const metaPath = path.join(SITE, 'meta.json'), indexPath = path.join(SITE, 'index.json');
const meta = fs.existsSync(metaPath) ? JSON.parse(fs.readFileSync(metaPath, 'utf8')) : { date: '2026-10-14', sweep: { done: 3, total: 2617 }, counts: { tiers: { S: 0, A: 0, B: 1, C: 1, D: 0, F: 1 }, misfits: 1, with_live: 2 }, hurdles: { S: 0.25, A: 0.2, B: 0.15, C: 0.1 }, notes: [], stale: [] };
const loaded = {};
['APP', 'KR', 'AEE', 'HBAN', 'ZS', 'EXPE'].forEach((t) => { const r = loadRecord(t); if (r) loaded[t] = r; });
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
  assert.ok(el.innerHTML.includes('Scenario range at 15%'), 'band tooltip'); assert.ok(/^5Y: [+-]\d+% \(\d{4}-\d{2}-\d{2} → \d{4}-\d{2}-\d{2}\)$/.test(r.text), r.text);
  el = fakeEl(800, 280); r = App.drawPrice(el, spec, { range: '1Y', showIv: false, showBand: false, showH: false });
  assert.ok(!el.innerHTML.includes('>IV</text>') && !el.innerHTML.includes('Scenario range'), 'overlays off'); assert.ok(r.text.startsWith('1Y:'));
  assert.ok(/<text [^>]*>\d{2}-\d{2}<\/text>/.test(el.innerHTML), '1Y uses month labels');
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
  ['Street summary', '16 analysts cover SYN', '<b>Buy</b>', '$58.00', '+29%</b> vs the last close $45.00', '$44.00 – $72.00', 'Our hurdle prices: $60.00 for 15% (Tier B), $45.50 for 20%', 'Buy 12', 'Hold 4', 'Sell 0', 'href="#SYN.forecast.street">See forecast', "The Street's view, not ours."].forEach((k) => assert.ok(street.includes(k), k));
  assert.ok(!street.includes('Consensus EPS') && !street.includes('<table'), 'the Overview card is the compact summary — no EPS or history tables');
  assert.ok(street.includes('class="bhs"') && street.includes('width:75.0%'), 'buy / hold / sell bar');
  const filings = App.renderFilings(synthetic);
  assert.ok(filings.includes('8-K') && filings.includes('2.02, 9.01') && filings.includes('Results of operations') && filings.includes('href="https://www.sec.gov/Archives/edgar/data/1234567/syn-8k-20261002.htm"'));
  assert.ok(!filings.includes('javascript:'), 'non-http filing URL is not linked');
  const bare = Object.assign({}, synthetic, { profile: undefined });
  const a2 = App.renderAbout(bare); assert.ok(a2.includes('Profile enrichment has not run') && a2.includes('Retail-Grocery Stores') && a2.includes('NYSE'), 'About falls back to fundamentals.profile');
  assert.ok(App.renderStreet(bare).includes('Street consensus appears once profile.py'), 'Street empty state');
  assert.ok(App.renderForecastStreet(bare).includes('Street consensus appears once profile.py') && App.renderForecastAnalysts(bare).includes('Analyst coverage appears once profile.py'), 'sub-tab empty states');
  const f2 = App.renderFilings(bare); assert.ok(f2.includes('10-K') && f2.includes('latest 10-K') && f2.includes('2026-02-20'), 'Filings fall back to fundamentals latest_filings');
  assert.ok(App.renderAbout({}).includes('No profile facts') || App.renderAbout({}).includes('Profile enrichment'), 'About with nothing at all');
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
  if (loaded.AEE) {
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
  if (canon.length) { const c = App.renderRowHTML(canon[0]); assert.ok(c.includes('class="star fixed"') && !c.includes('data-star='), 'canonical watchlist row: fixed star, no toggle'); }
  assert.ok(App.renderListRowsHTML(rows, { fit: 'all', watch: true, q: 'zzzz' }).includes('Nothing on the watchlist'));
  if (loaded.APP && loaded.APP.record.row.watchlist) assert.ok(App.renderHeader(loaded.APP.record).includes('★ Watchlist'), 'company hero shows the watchlist chip');
  assert.ok(!App.renderHeader(synthetic).includes('★ Watchlist'));
});
test('floor-clamped IRRs are marked (ZS: live super-bear / bear at the floor), header band too', () => {
  const rec = loaded.ZS ? loaded.ZS.record : null;
  if (rec) {
    const sens = App.sensitivity(rec);
    assert.equal(sens.super_bear.irr_live_at_floor, true); assert.equal(sens.bear.irr_live_at_floor, true); assert.equal(sens.base.irr_live_at_floor, false);
    const ff = App.floorFlags(rec, true); assert.ok(ff.bear && ff.super_bear && ff.any && !ff.weighted);
    const fc = App.renderForecastDCF(rec);
    const sb = fc.slice(fc.indexOf('<th>Super bear'), fc.indexOf('<th>Bear'));
    assert.ok(sb.includes('class="num mono atfloor"') && sb.includes('>at floor</sup>'), 'super-bear live IRR cell marked');
    const base = fc.slice(fc.indexOf('<th>Base'), fc.indexOf('<th>Bull'));
    assert.ok(!base.includes('at floor'), 'base cell unmarked');
    assert.ok(fc.includes('<b>At floor</b> marks an IRR the solver clamped'), 'explanation under the table');
    assert.ok(/bear case <b>[A-F]<\/b> \([-\d.]+%, <sup class="floor"/.test(fc), 'hurdle band note marks the bear end');
    assert.ok(App.renderHeader(rec).includes('<sup class="floor"'), 'header band marks the bear end');
  } else console.log('  (ZS record not available — skipped)');
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
  if (loaded.APP) { const a = App.oeForecastSeries(loaded.APP.record); assert.ok(a.H >= 6 && a.histVals[a.baseIndex] !== null, 'APP FY2025 null oe_per_share filled from OE ÷ shares'); assert.equal(a.labels[a.baseIndex + 1], '2026'); }
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
  ['Stock price forecast', '16 analysts cover SYN', 'class="sgauge"', 'Needle at (buy + ½ hold)', 'no strong-buy / strong-sell split', 'data-cid="street-fan"',
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
/* ---- report */
const failed = results.filter((r) => r[1]);
results.forEach((r) => console.log((r[1] ? 'FAIL ' : 'ok   ') + r[0]));
failed.forEach((r) => { console.error('\n--- ' + r[0] + '\n' + (r[1].stack || r[1])); });
console.log('\n' + (results.length - failed.length) + ' passed, ' + failed.length + ' failed' + (Object.keys(loaded).length ? ' · records: ' + Object.keys(loaded).map((t) => t + ' (' + loaded[t].source + ')').join(', ') : ''));
process.exit(failed.length ? 1 : 0);
