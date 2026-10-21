#!/usr/bin/env node
'use strict';
/* Pre-render the chat attachment's static layer (2026-10-16).
 *
 * The v6 app renders in the browser, and the iOS chat attachment viewer never
 * runs its script — the file sat on "Loading the ranking…". This script runs
 * the app's OWN renderers once in Node and build_site.py inlines the finished
 * HTML into the attachment's #app, under a tiny cleanup script that removes
 * the layer the moment JavaScript executes: one renderer, no drift, the
 * interactive app untouched where JS runs, full content where it does not.
 *
 * app.js is loaded through its module.exports Node API (the same path its
 * own test suite, _daily/site/tests/app.test.js, uses): every renderer is a
 * pure string function, and the chart draws take a stub element
 * ({clientWidth, clientHeight, innerHTML} — the tests' fakeEl) and write the
 * finished SVG string into it. No DOM, no jsdom, no npm dependency.
 *
 * Input: the exact payload build_site.py embeds as window.SITE_DATA
 * ({meta, index, records, embedded_top, embedded}). Output: one HTML fragment
 *   <style>…static rules…</style><div id="static">…list + one section per
 *   index row…</div>
 * Full pages for embedded records; the app's own "not embedded" page for the
 * rest, so every ranking row's link lands somewhere. Navigation is plain
 * HTML with NO fragment anchors: a radio group (name="conav") sits at the
 * top of #static — one co-list input (checked by default) plus one
 * co-<TICKER> input per company — the row / details / prev-next links are
 * <label for="co-<TICKER>"> elements, the back control is a label for
 * co-list, each section shows via a generated sibling rule
 * (#co-<T>:checked ~ .page#c-<T>) and the list hides while any company
 * radio is checked. (Fragment navigation was dropped 2026-10-20: the iOS
 * chat viewer ignores it, so tapping a company did nothing.) The tier
 * filter is CSS radios + :has over the rows' data-tier, and every tab
 * pane is stacked visible (the app's tab strips are hidden — inert
 * buttons would be dead taps).
 *
 * Usage: node prerender.js --payload P.json --app APPJS --out FRAGMENT.html
 * Exit 0 on success (warnings on stderr); non-zero on any hard failure —
 * build_site.py then refuses to replace the previous attachment.
 */
const fs = require('fs');
const path = require('path');

function arg(name) {
  const i = process.argv.indexOf('--' + name);
  return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : null;
}

const CHART_W = 828;   // .page max-width (860) minus card chrome: the widest the app ever draws at
const PRICE_H = 280;   // app.css .pchart height (desktop)
const FAN_H = 260;     // app.css .fanchart height

const STATIC_CSS = [
  '#static .controls{display:none}',                       // the app's seg buttons / sort / search are JS-only; the radio filter below replaces the tier one
  '#static .page{display:none}',                           // company sections wait for their nav radio (per-company rules are generated in main; id specificity overrides .page.open)
  '#static input[name="conav"]{position:absolute;opacity:0;width:1px;height:1px}',   // the nav radios themselves are invisible; their labels are the tap targets
  '#static .coradio:checked ~ #listView{display:none}',    // any company radio checked (co-list lacks .coradio) hides the list — one page at a time
  '#static label[for^="co-"]{cursor:pointer}',
  '#static #t td.co label{color:var(--txt);text-decoration:none;display:flex;flex-direction:column;gap:2px;min-width:0}',   // mirror of app.css #t td.co a for the row label
  '#static #t td.co label b{font-size:15px}',
  '#static .pane{display:block}',                          // every tab's panel, stacked — present as plain HTML, no tab tap needed
  '#static .subpane{display:block}',
  '#static .tabbar .tabs{display:none}',                   // inert tab buttons would be dead taps; the panes below them are all visible
  '#static .subtabs{display:none}',
  '#static .pcbar{display:none}',                          // price range buttons / overlay toggles are JS-only; the default range is rendered
  '#static .prtiers{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0;align-items:center}',
  '#static .prtiers .prlab{font-size:13px;color:var(--mut)}',
  '#static .prtiers input{position:absolute;opacity:0;width:1px;height:1px}',
  '#static .prtiers label{background:var(--card2);border:1px solid var(--line2);color:var(--txt2);padding:8px 12px;border-radius:10px;font-size:13.5px;cursor:pointer;min-height:38px;display:inline-flex;align-items:center}',
  '#static .prtiers input:checked+label{background:#2C3648;color:#fff}',
  '#static .prtiers input:focus-visible+label{outline:2px solid var(--acc);outline-offset:2px}',
  '#static:has(#prtf-S:checked) #t tbody tr:not([data-tier="S"]){display:none}',
  '#static:has(#prtf-A:checked) #t tbody tr:not([data-tier="A"]){display:none}',
  '#static:has(#prtf-B:checked) #t tbody tr:not([data-tier="B"]){display:none}',
  '#static:has(#prtf-C:checked) #t tbody tr:not([data-tier="C"]){display:none}',
  '#static:has(#prtf-D:checked) #t tbody tr:not([data-tier="D"]){display:none}',
  '#static:has(#prtf-F:checked) #t tbody tr:not([data-tier="F"]){display:none}'
].join('\n');

function fakeEl(w, h) { return { clientWidth: w, clientHeight: h || 0, innerHTML: '' }; }

function main() {
  const payloadPath = arg('payload'), appPath = arg('app'), outPath = arg('out');
  if (!payloadPath || !appPath || !outPath) {
    console.error('prerender: usage: node prerender.js --payload P.json --app APPJS --out FRAGMENT.html');
    return 2;
  }
  const App = require(path.resolve(appPath));
  const payload = JSON.parse(fs.readFileSync(payloadPath, 'utf8'));
  const meta = payload.meta && typeof payload.meta === 'object' ? payload.meta : {};
  const index = Array.isArray(payload.index) ? payload.index : [];
  const records = payload.records && typeof payload.records === 'object' ? payload.records : {};
  const warnings = [];
  const repo = App.repoList(meta, index);
  // exactly the stm object mountCompany hands renderCompanyHTML in the attachment (stmState with D.embedded)
  const stm = { status: 'embedded', data: null, error: null, line: null, statement: 'income', period: 'annual', growth: false, site: meta.site_url || '' };

  const byUpper = {};
  index.forEach((r) => { if (r && r.ticker) byUpper[String(r.ticker).toUpperCase()] = r.ticker; });
  function navFor(ticker) {
    let pos = -1;
    for (let i = 0; i < index.length; i++) if (String(index[i].ticker).toUpperCase() === String(ticker).toUpperCase()) { pos = i; break; }
    if (pos < 0) return {};
    return { prev: pos > 0 ? index[pos - 1].ticker : null, next: pos + 1 < index.length ? index[pos + 1].ticker : null, rank: pos + 1 };
  }

  /* Run the app's own draw functions on stub elements and splice the SVG they
     produce into the chart placeholders of one rendered page. */
  function injectCharts(html, specs, ticker) {
    html = html.replace(/<div class="chart[^"]*" data-cid="([^"]+)"><\/div>/g, (m, cid) => {
      const el = fakeEl(CHART_W, 0);
      try { App.drawChart(el, specs[cid]); } catch (e) { warnings.push(ticker + ' chart ' + cid + ': ' + (e && e.message)); return m; }
      return m.slice(0, -6) + el.innerHTML + '</div>';
    });
    html = html.replace(/<div class="fanchart[^"]*" data-cid="([^"]+)"><\/div>/g, (m, cid) => {
      const el = fakeEl(CHART_W, FAN_H);
      try { App.drawFan(el, specs[cid]); } catch (e) { warnings.push(ticker + ' fan ' + cid + ': ' + (e && e.message)); return m; }
      return m.slice(0, -6) + (el.innerHTML || '') + '</div>';
    });
    const pm = /<div class="pchart" data-cid="price"[^>]*><\/div>/.exec(html);
    if (pm && specs.price) {
      const el = fakeEl(CHART_W, PRICE_H);
      let res = null;
      try { res = App.drawPrice(el, specs.price, { range: App.defaultRange(specs.price) }); } catch (e) { warnings.push(ticker + ' price chart: ' + (e && e.message)); }
      if (el.innerHTML) {
        html = html.replace(pm[0], pm[0].slice(0, -6) + el.innerHTML + '</div>');
        if (res && res.text) { // the readout line drawPriceCard fills in the browser
          const txt = String(res.text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
          html = html.replace('<span class="pcret"></span>', '<span class="pcret ' + (res.cls || '') + '">' + txt + '</span>');
        }
      }
    }
    return html;
  }

  /* ---- the ranking, with every row present (fit: all) for the CSS tier filter */
  const state = { tier: 'all', fit: 'all', sort: 'irr_live', q: '', watch: false };
  let list = App.renderListHTML(meta, index, state, []);
  const radios = '<div class="prtiers" role="group" aria-label="Filter by tier"><span class="prlab">Tier</span>'
    + [['all', 'All'], ['S', 'S'], ['A', 'A'], ['B', 'B'], ['C', 'C'], ['D', 'D'], ['F', 'F']]
      .map((x) => '<input type="radio" name="prtf" id="prtf-' + x[0] + '"' + (x[0] === 'all' ? ' checked' : '') + '><label for="prtf-' + x[0] + '">' + x[1] + '</label>').join('')
    + '</div>';
  const twrap = '<div class="twrap"><table id="t">';
  if (list.indexOf(twrap) < 0) { console.error('prerender: ranking table anchor not found in renderListHTML output — app markup changed'); return 1; }
  list = list.replace(twrap, radios + twrap);

  /* ---- one section per index row */
  const anchors = {};   // canonical ticker -> fragment anchor id
  const sections = [];
  let full = 0, missing = 0;
  for (const row of index) {
    const t = row.ticker;
    const rec = records[t];
    let html;
    if (rec) {
      try {
        html = App.renderCompanyHTML(rec, 'overview', navFor(t), 'dcf', { stm: stm, stars: [], repo: repo });
        html = injectCharts(html, App.companyCharts(rec, stm), t);
      } catch (e) {
        warnings.push(t + ': page render failed (' + (e && e.message) + ') — not-embedded page used');
        html = null;
      }
      if (html) {
        const m = /id="d-([^"]+)"/.exec(html);
        if (!m) { console.error('prerender: no article id in the rendered page for ' + t); return 1; }
        anchors[t] = 'c-' + m[1];
        html = html.replace('id="d-' + m[1] + '"', 'id="' + anchors[t] + '"');
        full++;
      }
    }
    if (!html) {
      html = App.renderMissingHTML(row, meta);
      anchors[t] = 'c-' + App.safeId(t);
      html = html.replace('<article class="page open">', '<article class="page open" id="' + anchors[t] + '">');
      missing++;
    }
    sections.push(html);
  }

  /* ---- hash links (#T, #T.tab, #T.forecast.sub) -> in-file section anchors.
     Intermediate step only: navLabels below turns every section anchor into
     a radio label, so no fragment link survives into the fragment. */
  function anchorFor(token) {
    const up = token.toUpperCase();
    if (byUpper[up]) return anchors[byUpper[up]];
    let best = null;
    Object.keys(byUpper).forEach((k) => { if (up.indexOf(k + '.') === 0 && (!best || k.length > best.length)) best = k; });
    return best ? anchors[byUpper[best]] : null;
  }
  function rewriteLinks(html) {
    return html.replace(/href="#([A-Za-z0-9._-]+)"/g, (m, token) => {
      const a = anchorFor(token);
      return a ? 'href="#' + a + '"' : m;
    });
  }

  /* ---- no-JS navigation (2026-10-20): anchors -> labels for the conav
     radios. The viewer's fragment navigation is inert, but a <label> tap
     checks its radio in any HTML renderer, and the sibling rules in the
     generated CSS do the rest. The back anchor (href="#") becomes the
     co-list label; every #c-<T> anchor keeps its classes and content. */
  function navLabels(html) {
    html = html.replace(/<a class="back" href="#">← Ranking<\/a>/g,
      '<label class="back" for="co-list">← Ranking</label>');
    return html.replace(/<a\b([^>]*?)href="#c-([A-Za-z0-9_.-]+)"([^>]*)>([\s\S]*?)<\/a>/g,
      (m, pre, suf, post, inner) => {
        const attrs = (pre + post).trim().replace(/\s+/g, ' ');
        return '<label' + (attrs ? ' ' + attrs : '') + ' for="co-' + suf + '">' + inner + '</label>';
      });
  }
  // safeId's only selector-special character is the dot (kept for tickers like BF.B)
  function cssId(s) { return s.replace(/\./g, '\\.'); }
  const suffixes = index.map((row) => anchors[row.ticker].slice(2));   // anchors[t] is 'c-<suffix>'
  const navRadios = '<input type="radio" name="conav" id="co-list" checked>'
    + suffixes.map((s) => '<input type="radio" name="conav" class="coradio" id="co-' + s + '">').join('');
  const navCss = suffixes.map((s) => '#static #co-' + cssId(s) + ':checked ~ .page#c-' + cssId(s) + '{display:block}').join('\n');

  const fragment = '<style>\n' + STATIC_CSS + '\n' + navCss + '\n</style>\n<div id="static">\n'
    + navRadios + '\n' + navLabels(rewriteLinks(list)) + '\n' + sections.map((h) => navLabels(rewriteLinks(h))).join('\n') + '\n</div>\n';
  fs.writeFileSync(outPath, fragment);
  warnings.forEach((w) => console.error('prerender: warning: ' + w));
  console.log('prerender: ' + index.length + ' sections (' + full + ' full, ' + missing + ' not-embedded), fragment '
    + Buffer.byteLength(fragment).toLocaleString('en-US') + ' B' + (warnings.length ? ', ' + warnings.length + ' warning(s)' : ''));
  return 0;
}

process.exit(main());
