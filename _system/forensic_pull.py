#!/usr/bin/env python3
"""Second-pass forensic battery + filing-freshness check (added 2026-10-13).

Usage: python3 forensic_pull.py <TICKER> [--cik N]

Pulls filing-direct EDGAR facts for the tags pass 1's engine does not use and
prints a markdown battery for the second-pass worker's second_pass.md:
- margin structure per FY: gross margin, COGS % rev, SG&A % rev, combined
  (COGS+SG&A) % rev (the IBM split-migration test), NI vs operating income gap,
  discontinued-ops and nonoperating income lines.
- prepaid battery: prepaid balances (quarterly, latest 8), % of assets,
  prepaids/SG&A, YoY / QoQ jumps.
- filing freshness: EDGAR submissions after pass 1's analysis date, flagging
  newer 10-K/10-Q periods than pass 1 used and material 8-Ks.
Missing tags print as n/a — never crash, never invent.
"""
import json, os, sys, urllib.request, datetime, time

UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # v5.4: runs anywhere
# v5.4 (audit round-1 battery bugs): items 2.02 (results) and 7.01 (Reg FD)
# are routine and no longer count as material; STALE_PASS1 is now computed
# BEFORE the flag list prints; candidate tags merge per period (pick() took
# the first tag with any data — the truncation bug v4 fixed in the engine).
MATERIAL_8K_ITEMS = ("1.01", "1.02", "1.03", "2.01", "2.03", "2.04", "2.05", "2.06", "4.01", "4.02", "5.02", "8.01")

def get_json(url, timeout=90):
    last = None
    for attempt in range(3):  # retry with backoff
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            last = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last

def pick(facts, tags):
    us = facts.get("facts", {}).get("us-gaap", {})
    for t in tags:
        if t in us:
            units = us[t].get("units", {})
            for u in ("USD", "USD/shares"):
                if u in units and units[u]:
                    return t, units[u]
    return None, []

def _rows_for(facts, tag):
    us = facts.get("facts", {}).get("us-gaap", {})
    units = (us.get(tag) or {}).get("units", {})
    for u in ("USD", "USD/shares"):
        if u in units and units[u]:
            return units[u]
    return []

def annual_series(facts, tags):
    """{end_date: value} from ~annual-duration facts, MERGED across the
    candidate tags per period (priority order), latest filing wins per tag."""
    out, used = {}, []
    for tag in tags:
        rows = _rows_for(facts, tag)
        if not rows:
            continue
        best = {}
        for r in rows:
            if r.get("form") not in ("10-K", "10-K/A", "20-F", "40-F"):
                continue
            s, e = r.get("start"), r.get("end")
            if not s or not e:
                continue
            days = (datetime.date.fromisoformat(e) - datetime.date.fromisoformat(s)).days
            if not (300 <= days <= 400):
                continue
            prev = best.get(e)
            if prev is None or r.get("filed", "") > prev[1]:
                best[e] = (r["val"], r.get("filed", ""))
        for e, (v, _) in best.items():
            if e not in out:
                out[e] = v
                if tag not in used: used.append(tag)
    return ("+".join(used) if used else None), out

def instant_series(facts, tags, limit=8):
    """Latest balance per period end (any form), merged across tags, most recent `limit` ends."""
    out, used = {}, []
    for tag in tags:
        rows = _rows_for(facts, tag)
        if not rows:
            continue
        best = {}
        for r in rows:
            e = r.get("end")
            if not e or "val" not in r:
                continue
            prev = best.get(e)
            if prev is None or r.get("filed", "") > prev[1]:
                best[e] = (r["val"], r.get("filed", ""))
        for e, (v, _) in best.items():
            if e not in out:
                out[e] = v
                if tag not in used: used.append(tag)
    ends = sorted(out)[-limit:]
    return ("+".join(used) if used else None), {k: out[k] for k in ends}

def fmt(v):
    if v is None:
        return "n/a"
    if abs(v) >= 1e9:
        return f"${v/1e9:,.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:,.0f}M"
    return f"${v:,.0f}"

def pct(x):
    return f"{x*100:+.1f}%" if x is not None else "n/a"

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ticker = args[0].upper()
    cik = None
    if "--cik" in sys.argv:
        cik = int(sys.argv[sys.argv.index("--cik") + 1])
    folder = f"{BASE}/{ticker}"
    nums, score = {}, {}
    try:
        nums = json.load(open(f"{folder}/dcf_numbers.json", encoding="utf-8"))
    except Exception:
        pass
    try:
        score = json.load(open(f"{folder}/score.json", encoding="utf-8"))
    except Exception:
        pass
    if cik is None:
        cik = nums.get("cik")
    if not cik:
        # fall back to EDGAR ticker map
        m = get_json("https://www.sec.gov/files/company_tickers.json")
        for v in m.values():
            if v["ticker"] == ticker:
                cik = v["cik_str"]
                break
    if not cik:
        print(f"# Forensic battery — {ticker}\n\nBLOCKED: no CIK found.")
        return
    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json")

    rev_t, rev = annual_series(facts, ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"])
    gp_t, gp = annual_series(facts, ["GrossProfit"])
    cogs_t, cogs = annual_series(facts, ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"])
    sga_t, sga = annual_series(facts, ["SellingGeneralAndAdministrativeExpense"])
    if not sga:
        sm_t, sm = annual_series(facts, ["SellingAndMarketingExpense", "SalesAndMarketingExpense"])
        ga_t, ga = annual_series(facts, ["GeneralAndAdministrativeExpense"])
        merged = {y: sm[y] + ga[y] for y in sm if y in ga}
        if merged:
            sga_t, sga = f"{sm_t}+{ga_t}", merged
    ni_t, ni = annual_series(facts, ["NetIncomeLoss"])
    oi_t, oi = annual_series(facts, ["OperatingIncomeLoss"])
    disc_t, disc = annual_series(facts, ["IncomeLossFromDiscontinuedOperationsNetOfTax", "DiscontinuedOperationsIncomeLossNetOfTax"])
    nonop_t, nonop = annual_series(facts, ["NonoperatingIncomeExpense", "OtherNonoperatingIncomeExpense"])
    pp_t, pp = instant_series(facts, ["PrepaidExpenseAndOtherAssetsCurrent", "PrepaidExpenseCurrent"])
    ast_t, ast = instant_series(facts, ["Assets"])

    print(f"# Forensic battery — {ticker} (CIK {cik})")
    print(f"Tags used: revenue={rev_t}, gross_profit={gp_t}, cogs={cogs_t}, sga={sga_t}, ni={ni_t}, oi={oi_t}, disc_ops={disc_t}, nonop={nonop_t}, prepaids={pp_t}, assets={ast_t}\n")
    years = sorted(set(rev) | set(gp) | set(ni))[-6:]
    print("| FY end | Revenue | Gross margin | COGS %rev | SG&A %rev | (COGS+SG&A) %rev | NI vs OI gap | Disc ops | Nonop inc |")
    print("|---|---|---|---|---|---|---|---|---|")
    flags = []
    prev = {}
    for y in years:
        r = rev.get(y)
        gm = (gp[y] / r) if y in gp and r else None
        cp = (cogs[y] / r) if y in cogs and r else None
        sp = (sga[y] / r) if y in sga and r else None
        comb = (cp + sp) if (cp is not None and sp is not None) else None
        gap = None
        if y in ni and y in oi and oi[y]:
            gap = (ni[y] - oi[y]) / abs(oi[y])
        print(f"| {y} | {fmt(r)} | {pct(gm) if gm is not None else 'n/a'} | {pct(cp) if cp is not None else 'n/a'} | {pct(sp) if sp is not None else 'n/a'} | {pct(comb) if comb is not None else 'n/a'} | {pct(gap) if gap is not None else 'n/a'} | {fmt(disc.get(y))} | {fmt(nonop.get(y))} |")
        if prev:
            if cp is not None and prev.get("cp") is not None and abs(cp - prev["cp"]) > 0.03:
                flags.append(f"COGS_SWING {y}: COGS % of revenue moved {pct(cp - prev['cp'])} YoY — weak cost control / moat evidence.")
            if comb is not None and prev.get("comb") is not None and abs(comb - prev["comb"]) < 0.01:
                moved = [k for k in ("cp", "sp") if prev.get(k) is not None and (cp if k == 'cp' else sp) is not None and abs((cp if k == 'cp' else sp) - prev[k]) > 0.02]
                if moved:
                    flags.append(f"SPLIT_MIGRATION {y}: combined (COGS+SG&A)/rev flat but components moved >2pp — cost optics (IBM pattern); trust the combined series.")
            if gap is not None and abs(gap) > 0.15:
                flags.append(f"NI_OI_GAP {y}: net income differs from operating income by {pct(gap)} — noncore items are material to earnings quality.")
        if y in disc and disc[y]:
            flags.append(f"DISC_OPS {y}: discontinued operations {fmt(disc[y])} on the books — divestiture optics check required.")
        prev = {"cp": cp, "sp": sp, "comb": comb}
    print("\n## Prepaid battery")
    if pp:
        ends = sorted(pp)
        for e in ends:
            share = (pp[e] / ast[e]) if e in ast and ast[e] else None
            print(f"- {e}: prepaids {fmt(pp[e])}" + (f" = {share*100:.1f}% of assets" if share is not None else ""))
        last = ends[-1]
        if len(ends) >= 2 and pp[ends[-2]]:
            q = pp[last] / pp[ends[-2]] - 1
            if abs(q) > 0.20:
                flags.append(f"PREPAID_QOQ {last}: prepaids moved {pct(q)} QoQ — check for expense deferral.")
        yoy_ends = [e for e in ends if e[:4] == str(int(last[:4]) - 1) and e[5:] == last[5:]]
        if yoy_ends and pp[yoy_ends[-1]]:
            yy = pp[last] / pp[yoy_ends[-1]] - 1
            print(f"- YoY change at {last}: {pct(yy)}")
            if yy > 0.30:
                flags.append(f"PREPAID_YOY {last}: prepaids up {pct(yy)} YoY — verify against OCF trend (earnings up + OCF down + prepaids up = deferral pattern).")
        sga_latest = sga[max(sga)] if sga else None
        if sga_latest:
            print(f"- Prepaids / latest FY SG&A: {pp[last]/sga_latest*100:.0f}%")
    else:
        print("- No prepaid tag found (n/a).")
    # v5.4: freshness is computed BEFORE the flag list prints so STALE_PASS1
    # actually appears in it (audit round-1: it was appended after printing).
    fresh_lines = []
    try:
        subs = get_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        rec = subs["filings"]["recent"]
        pass1_date = score.get("analysis_date", "0000-00-00")
        pass1_period = nums.get("latest_period_end", "")
        n = len(rec["filingDate"])
        newer_periodic, material_8k = [], []
        for i in range(n):
            fd, form = rec["filingDate"][i], rec["form"][i]
            if fd <= pass1_date:
                continue
            period = rec["reportDate"][i] if i < len(rec["reportDate"]) else ""
            if form in ("10-K", "10-K/A", "10-Q", "10-Q/A") and period > pass1_period:
                newer_periodic.append(f"{form} filed {fd}, period {period}")
            if form == "8-K":
                items = rec["items"][i] if i < len(rec["items"]) else ""
                if any(k in items for k in MATERIAL_8K_ITEMS):
                    material_8k.append(f"8-K filed {fd}, items {items}")
        fresh_lines.append(f"- Pass 1 analysis date: {pass1_date}; latest period pass 1 used: {pass1_period or 'n/a'}")
        fresh_lines.append(f"- Newer periodic filing since pass 1: {'; '.join(newer_periodic) if newer_periodic else 'NONE — pass 1 data is filing-current.'}")
        fresh_lines.append(f"- Material 8-Ks since pass 1 (items 2.02 / 7.01 excluded as routine): {'; '.join(material_8k[:5]) if material_8k else 'none'}")
        if newer_periodic:
            flags.append("STALE_PASS1: a newer periodic filing exists — recompute the TTM base filing-direct (ttm.py) before concluding.")
    except Exception as e:
        fresh_lines.append(f"- Submissions check failed: {e}")

    print("\n## Battery flags")
    print("\n".join(f"- {f}" for f in flags) if flags else "- None tripped.")
    print("\n## Filing freshness")
    print("\n".join(fresh_lines))
    print("\n(Worker: paste this battery into second_pass.md and resolve every tripped flag in writing.)")

if __name__ == "__main__":
    main()
