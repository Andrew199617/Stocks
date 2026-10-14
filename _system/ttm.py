#!/usr/bin/env python3
"""TTM owner's-earnings calculator (v5, 2026-10-13 — agents never hand-compute TTM again).

Usage: python3 ttm.py <TICKER> [--cik N]

Computes trailing-twelve-month OCF, capex, SBC and diluted shares from EDGAR
companyfacts 10-Q YTD facts: TTM = FY - prior-year YTD + current YTD, with the
YTD periods matched by fiscal-year start. Prints JSON with every input value
(FY, prior YTD, current YTD, tag used) so the arithmetic is auditable.

Capex policy (round-2, 2026-10-14): if a filer has NO capex facts in
companyfacts at all (any candidate tag, any period), that is a data gap —
exit 3 — UNLESS a judgment capex_override fills it. The old zero-fill-with-
warning path is gone: ttm.py holds the same standard as the engine's
DATA_GAP gate. If capex facts exist but any of the three TTM inputs is
missing (e.g. APP FY25), that is likewise a data gap: exit 3. Missing
OCF/SBC/shares facts also exit 3. Exit 2 = no CIK found.

On success the full output is also written to <TICKER>/ttm.json — the
machine-readable provenance for the engine's --ttm base pin (make_score.py
refuses a pinned base that differs from ttm.json). Day counts are
INCLUSIVE (end - start + 1) so a filled annual leg is exactly the override
value, matching the engine's annual fill. Leg matching tolerates a filed
fact whose start date is within a few days of the expected period start
(match on end date + nearest start): a real filed fact is never replaced
by an override fill. DCF_TTM_NO_WRITE=1 suppresses the ttm.json write
(make_score.py's measurement runs must not clobber the worker's file).

Overrides (v5.1, 2026-10-13): judgment.json may carry capex_override /
sbc_override / shares_override ({value, source, reason, kind}). For a field
with an override, the TTM legs are assembled on the OCF anchor timeline: a
leg uses the filer's own fact when one exists for the anchor period,
otherwise it is filled with the override value prorated by days in the leg
period (value x days/365) — so a fully untagged year nets to exactly the
override value in the TTM. Filled legs are listed in overrides_used, and an
override-filled capex leg raises no CAPEX_NOT_FILED warning. Share counts
are averages, not flows: a shares override is used unprorated as the TTM
denominator. DCF_NO_OVERRIDES=1 disables override loading.
"""
import json, sys, os, csv, time, urllib.request, urllib.error, datetime

UA = {"User-Agent": "Muse research andrewmauro199612@gmail.com"}
BASE = "/home/hatch/workspace/stocks"
SYS = f"{BASE}/_system"

OCF_TAGS = ["NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]
CAPEX_TAGS = ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsForConstructionInProcess",
              "PaymentsToAcquireOtherPropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
              "PaymentsToAcquireOtherProductiveAssets"]
SBC_TAGS = ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"]
SHARE_TAGS = ["WeightedAverageNumberOfDilutedSharesOutstanding",
              "WeightedAverageNumberOfSharesOutstandingDiluted",
              "WeightedAverageNumberOfSharesOutstandingBasic"]
FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A")


def get_json(url, headers=UA, timeout=90):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:  # retry with backoff on any transient fetch failure
            last = e
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last


def resolve_cik(ticker):
    if "--cik" in sys.argv:
        return int(sys.argv[sys.argv.index("--cik") + 1])
    sec = json.load(open(f"{SYS}/sec_tickers_exchange.json"))
    cik_by_ticker = {}
    for rec in sec["data"]:
        cik_by_ticker.setdefault(rec[2].upper(), rec[0])
    for cand in (ticker, ticker.replace("/", "-"), ticker.replace("/", ".")):
        if cand in cik_by_ticker:
            return cik_by_ticker[cand]
    with open(f"{SYS}/universe.csv") as f:
        for row in csv.DictReader(f):
            if row["ticker"] == ticker and row.get("cik"):
                return int(row["cik"])
    return None


def merged_facts(facts, tags, unit):
    """{(start, end): (value, tag)} across candidate tags — per exact period the
    highest-priority tag that reports it wins; latest filing wins within a tag."""
    us = facts.get("facts", {}).get("us-gaap", {})
    merged = {}
    for tag in tags:
        if tag not in us:
            continue
        best = {}
        for e in us[tag].get("units", {}).get(unit, []):
            if e.get("form", "") not in FORMS or not e.get("start") or not e.get("end"):
                continue
            key = (e["start"], e["end"])
            prev = best.get(key)
            if prev is None or e.get("filed", "") > prev[0]:
                best[key] = (e.get("filed", ""), e["val"])
        for k, (_, v) in best.items():
            if k not in merged:
                merged[k] = (v, tag)
    return merged


def load_overrides(ticker):
    """Structured judgment overrides from {ticker}/judgment.json — same
    validation as dcf_engine.py: a malformed override is ignored here and
    refused by make_score.py."""
    if os.environ.get("DCF_NO_OVERRIDES"):
        return {}
    try:
        j = json.load(open(f"{BASE}/{ticker}/judgment.json"))
    except Exception:
        return {}
    out = {}
    for field, key in (("capex", "capex_override"), ("sbc", "sbc_override"), ("shares", "shares_override")):
        o = j.get(key) if isinstance(j, dict) else None
        if (isinstance(o, dict) and isinstance(o.get("value"), (int, float))
                and not isinstance(o.get("value"), bool)
                and o.get("kind") in ("filing", "estimate")
                and str(o.get("source") or "").strip() and str(o.get("reason") or "").strip()):
            out[field] = {"value": float(o["value"]), "kind": o["kind"],
                          "source": o["source"], "reason": o["reason"]}
    return out


def days(a, b):
    """INCLUSIVE day count of the period a..b (end - start + 1) — a calendar
    fiscal year is 365 days, so an override-filled annual leg comes to exactly
    the override value, matching the engine's annual fill (round-2: the old
    exclusive count made APP's FY leg $18.95M against the engine's $19.00M)."""
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1


def start_diff(a, b):
    return abs((datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days)


def shift_year(dstr, delta):
    d = datetime.date.fromisoformat(dstr)
    try:
        return d.replace(year=d.year + delta).isoformat()
    except ValueError:  # Feb 29
        return d.replace(year=d.year + delta, day=28).isoformat()


def extract_ttm(series, label, problems):
    """series: {(start,end): (val, tag)}. Returns dict of inputs or None."""
    annual = [(s, e, v, t) for (s, e), (v, t) in series.items() if 330 <= days(s, e) <= 380]
    if not annual:
        problems.append(f"{label}: no annual (FY) fact")
        return None
    fy_start, fy_end, fy_val, fy_tag = max(annual, key=lambda x: x[1])
    # current-year YTD: periods starting at the fiscal-year start that follows fy_end
    starts_after = sorted({s for (s, e) in series if s > fy_start and 0 <= days(fy_end, s) <= 10})
    cur = None
    for st in starts_after:
        cands = [(e, v, t) for (s, e), (v, t) in series.items() if s == st and days(s, e) <= 300]
        if cands:
            e, v, t = max(cands, key=lambda x: x[0])
            cur = (st, e, v, t)
            break
    if cur is None:
        problems.append(f"{label}: no post-FY YTD fact (no 10-Q since the {fy_end} fiscal year end)")
        return None
    cur_start, cur_end, cur_val, cur_tag = cur
    # prior-year YTD: same fiscal start as the FY (within a few days — filers
    # occasionally shift a period start), ending ~1 year before cur_end
    target_end = shift_year(cur_end, -1)
    prior, prior_key = None, None
    for (s, e), (v, t) in series.items():
        if start_diff(s, fy_start) <= 5 and abs((datetime.date.fromisoformat(e) - datetime.date.fromisoformat(target_end)).days) <= 6:
            key = (start_diff(s, fy_start), -datetime.date.fromisoformat(e).toordinal())
            if prior is None or key < prior_key:
                prior, prior_key = (s, e, v, t), key
    if prior is None:
        problems.append(f"{label}: no prior-year YTD fact matching {target_end} (FY start {fy_start})")
        return None
    return {"fy": fy_val, "fy_period": [fy_start, fy_end], "fy_tag": fy_tag,
            "ytd_prior": prior[2], "ytd_prior_period": [prior[0], prior[1]], "ytd_prior_tag": prior[3],
            "ytd_current": cur_val, "ytd_current_period": [cur_start, cur_end], "ytd_current_tag": cur_tag,
            "ttm": fy_val - prior[2] + cur_val}


def main():
    ticker = sys.argv[1].upper()
    cik = resolve_cik(ticker)
    if cik is None:
        print(f"ttm.py: NO_CIK for {ticker}", file=sys.stderr)
        sys.exit(2)
    facts = get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")

    problems, warnings = [], []
    overrides = load_overrides(ticker)
    overrides_used = []
    ocf = extract_ttm(merged_facts(facts, OCF_TAGS, "USD"), "ocf", problems)
    anchor = None
    if ocf:
        anchor = {"fy": tuple(ocf["fy_period"]), "ytd_prior": tuple(ocf["ytd_prior_period"]),
                  "ytd_current": tuple(ocf["ytd_current_period"])}

    def assemble(series, field):
        """TTM legs on the OCF anchor timeline for an override-backed field:
        the filer's own fact wins when one exists for the anchor period —
        including a fact whose start is shifted a few days (matched on end
        date + nearest start), so a real filed fact is never replaced by an
        override fill; a truly missing leg is filled with the override
        prorated by inclusive days (x days/365)."""
        ov = overrides[field]
        legs, filled_legs = {}, {}
        for leg in ("fy", "ytd_prior", "ytd_current"):
            per = anchor[leg]
            hit = series.get(per)
            if not hit:
                cands = [(start_diff(s, per[0]), (s, e), v) for (s, e), v in series.items()
                         if e == per[1] and start_diff(s, per[0]) <= 5]
                if cands:
                    cands.sort(key=lambda x: x[0])
                    _, k, v = cands[0]
                    hit = (v, series[k][1])
                    per = k
            if hit:
                legs[leg] = (per, hit[0], hit[1])
            else:
                d = days(per[0], per[1])
                amt = ov["value"] * d / 365.0
                legs[leg] = (per, amt, "OVERRIDE")
                filled_legs[leg] = {"period": list(per), "amount": amt, "days": d, "prorated": True}
        if filled_legs:
            overrides_used.append({"field": field, "value": ov["value"], "kind": ov["kind"],
                                   "source": ov["source"], "legs_filled": filled_legs})
        fy, pr, cu = legs["fy"], legs["ytd_prior"], legs["ytd_current"]
        return {"fy": fy[1], "fy_period": list(fy[0]), "fy_tag": fy[2],
                "ytd_prior": pr[1], "ytd_prior_period": list(pr[0]), "ytd_prior_tag": pr[2],
                "ytd_current": cu[1], "ytd_current_period": list(cu[0]), "ytd_current_tag": cu[2],
                "ttm": fy[1] - pr[1] + cu[1]}

    sbc_series = merged_facts(facts, SBC_TAGS, "USD")
    if "sbc" in overrides and anchor:
        sbc = assemble(sbc_series, "sbc")
    else:
        sbc = extract_ttm(sbc_series, "sbc", problems)

    _plen = len(problems)
    shares = extract_ttm(merged_facts(facts, SHARE_TAGS, "shares"), "shares_diluted", problems)
    if shares is None and "shares" in overrides:
        del problems[_plen:]  # the override rescues the missing share count
        ov = overrides["shares"]
        shares = {"fy": None, "fy_period": None, "fy_tag": None,
                  "ytd_prior": None, "ytd_prior_period": None, "ytd_prior_tag": None,
                  "ytd_current": ov["value"],
                  "ytd_current_period": list(anchor["ytd_current"]) if anchor else None,
                  "ytd_current_tag": "OVERRIDE", "ttm": None}
        overrides_used.append({"field": "shares", "value": ov["value"], "kind": ov["kind"],
                               "source": ov["source"],
                               "legs_filled": {"ytd_current": {"amount": ov["value"], "prorated": False,
                                               "note": "share counts are weighted averages, not flows — used unprorated as the TTM denominator"}}})

    capex_series = merged_facts(facts, CAPEX_TAGS, "USD")
    if "capex" in overrides and anchor:
        capex = assemble(capex_series, "capex")
    elif not capex_series:
        # Round-2: no more zero-fill-with-warning. A never-filed capex is a
        # data gap here exactly as in the engine (DATA_GAP:capex); only a
        # judgment override (the branch above) may fill it.
        problems.append("capex: no capex facts in companyfacts under any candidate tag and no "
                        "capex_override in judgment.json — refusing to zero-fill (same DATA_GAP standard as the engine)")
        capex = {"fy": 0, "ytd_prior": 0, "ytd_current": 0, "ttm": 0,
                 "fy_period": None, "ytd_prior_period": None, "ytd_current_period": None,
                 "fy_tag": None, "ytd_prior_tag": None, "ytd_current_tag": None}
    else:
        capex = extract_ttm(capex_series, "capex", problems)

    if problems:
        print(f"ttm.py: cannot compute TTM for {ticker} (CIK {cik}): " + "; ".join(problems), file=sys.stderr)
        sys.exit(3)

    oe_total = ocf["ttm"] - capex["ttm"] - sbc["ttm"]
    shares_in = dict(shares)
    shares_in.pop("ttm", None)  # share counts are weighted averages, not flows — a "TTM sum" is meaningless; the TTM denominator is the current-YTD average
    shares_in["basis"] = "ttm_shares_diluted = ytd_current (weighted average diluted shares for the current YTD period)"
    out = {"ticker": ticker, "cik": cik, "entity": facts.get("entityName"),
           "fy_end": ocf["fy_period"][1], "ytd_end": ocf["ytd_current_period"][1],
           "inputs": {"ocf": ocf, "capex": capex, "sbc": sbc, "shares_diluted": shares_in},
           "ttm_ocf": ocf["ttm"], "ttm_capex": capex["ttm"], "ttm_sbc": sbc["ttm"],
           "ttm_shares_diluted": shares["ytd_current"],
           "ttm_oe_total": oe_total,
           "ttm_oe_per_share": oe_total / shares["ytd_current"] if shares["ytd_current"] else None,
           "warnings": warnings, "overrides_used": overrides_used}
    if not os.environ.get("DCF_TTM_NO_WRITE"):
        # Machine-readable provenance for the base pin: the engine's --ttm
        # reads this file, and make_score.py refuses a pinned base that
        # differs from it by >0.1%.
        with open(f"{BASE}/{ticker}/ttm.json", "w") as f:
            json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
