#!/usr/bin/env python3
"""Same-ladder SIC-group return medians for the moat scorecard's industry_structure pillar — engine 5.7 (Andrew,
2026-10-19, R4 revised M2: "the fourth-best company in a good industry beats the best company in a bad one"; design
03b §3.3 with the main agent's decisions 03c 5 and 13, 2026-10-20). Policy-bearing (its output feeds make_score's
moat evidence). stdlib only, no network.

Usage: python3 _system/industry_returns.py              dry run: prints the groups, n, median, coverage; writes nothing
       python3 _system/industry_returns.py --write      writes _system/industry_returns.json (stable write: only when a
                                                         member's value, SIC, type or ladder changed; `built` is volatile)
       python3 _system/industry_returns.py --json PATH  writes the build to PATH instead (tests)
       python3 _system/industry_returns.py --check      exit 1 when the committed file differs from a fresh build apart
                                                         from `built` (a test and manual tool — preflight never runs it)
Exit 0 / 1 / 2 (usage).

Every folder with score.json (not `_`-prefixed) is a candidate member: its SIC (dcf_numbers.json sector_model.sic,
else dcf_engine.folder_sic: fundamentals.json profile.sic, then profile.json about.sic), its business type (judgment
moat_scorecard.business_type when declared, else moat_scorecard's hint: the SIC lock incl. the SIC-6798 mortgage-REIT
rule, the fee hint, the sector flag), its ladder family (roe / real_assets / default) and its governing 5-FY median
through moat_scorecard.governing_return — the same function make_score scores with. One member per CIK (03c decision
5: FWONA / FWONK, FOX / FOXA — the alphabetically first ticker stays; the other is listed in `excluded`). A folder
with no SIC or an unmeasured governing return is listed in `excluded` with the reason.

Groups are built per (ladder family, SIC level 4 / 3 / 2, code) with >= 2 members, keyed `<ladder>|<level>:<code>`,
so a company's peers are read from its own family's group only (a regulated utility's 5% ROIC and a waste hauler's
18% tangible ROIC are not one distribution). Each group records its members, n (members whose median is not -inf),
n_dropped (03c decision 13 option (b): a -inf median — losses on non-positive capital — is undefined and dropped, thin
and loss-making peers with finite medians stay), the median, the metric mix and a label. make_score computes the
leave-one-out median from the members (moat_scorecard.pillar_industry_structure), never from another ladder's group.

Cadence: the daily-ranking cron writes it after profile.py --all; rebuild_scores.py writes it before rebuilding;
the code PR carries the initial build. make_score only reads it and prints its build date and sha256. A company PR
does not rebuild it, so between two cron runs the committed file is legitimately one or more re-scores behind: the
test suite checks its internal consistency (consistency_problems), never its currency (--check).
"""
import argparse
import collections
import datetime
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import moat_scorecard as M  # noqa: E402
import dcf_engine as E  # noqa: E402
from _stable import write_json_if_changed, same_content  # noqa: E402

BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(HERE)
SCHEMA = 1
VOLATILE = ("built",)
RULE = {"levels": list(M.INDUSTRY_LEVELS), "min_peers": M.INDUSTRY_MIN_PEERS, "self_excluded": True, "same_ladder": True,
        "dedupe": "one member per CIK (the alphabetically first ticker)",
        "drop": "peers whose governing median is -inf (losses on non-positive capital) are dropped and counted",
        "ladders": {"roe": ["financial_balance_sheet"], "real_assets": ["real_assets"], "default": "every other type"},
        "measure": "governing 5-FY median (moat_scorecard.governing_return)"}


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _today():
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo("America/New_York")).date().isoformat()


def member_for(base, t):
    """(member record, None) or (None, why excluded) for folder t."""
    folder = os.path.join(base, t)
    n = _read(os.path.join(folder, "dcf_numbers.json")) or {}
    j = _read(os.path.join(folder, "judgment.json")) or {}
    sm = n.get("sector_model") if isinstance(n.get("sector_model"), dict) else {}
    sic, desc, _ = E.folder_sic(base, t)
    sic = str(sm.get("sic")).strip() if sm.get("sic") else sic
    fund = _read(os.path.join(folder, "fundamentals.json")) or {}
    cik = fund.get("cik") or n.get("cik")
    if not sic or not str(sic).isdigit():
        return None, "no SIC"
    sc = j.get("moat_scorecard") if isinstance(j.get("moat_scorecard"), dict) else None
    if sc and sc.get("business_type") in M.BUSINESS_TYPES:
        btype, basis = sc["business_type"], "declared"
    else:
        raw = M.raw_rows(folder)[1]
        allowed, _, cls = M.type_lock(sic, raw[-1] if raw else None)
        btype, _ = M.sic_hint(sic, n.get("fragility_flags"), allowed, cls)
        basis = "hint"
    g = M.governing_return(folder, btype, n)
    if g["value"] is None:
        return None, "governing return unmeasured"
    return {"sic": str(sic), "sic_description": desc, "cik": int(cik) if str(cik or "").isdigit() else (cik or None),
            "business_type": btype, "type_basis": basis, "ladder": M.ladder_family(btype), "measure": g["measure"],
            "median": g["median"], "median_note": g["median_note"]}, None


def _value(m):
    return M._peer_value(m)


def _label(level, code, descs):
    if level == 4:
        c = collections.Counter(d for d in descs if d)
        return (sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0] if c else f"SIC {code}")
    if level == 3:
        return f"SIC {code}x · {M.MAJOR_GROUPS.get(code[:2], 'major group ' + code[:2])}"
    return f"SIC {code} · {M.MAJOR_GROUPS.get(code, 'major group ' + code)}"


def build(base=BASE, built=None):
    """The industry_returns.json document for every scored folder under base (deterministic: members sorted by ticker,
    groups by key)."""
    members, excluded, by_cik = {}, {}, {}
    folders = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(base, "*", "score.json")))
    for t in folders:
        if t.startswith(("_", ".")):
            continue
        m, why = member_for(base, t)
        if m is None:
            excluded[t] = why
            continue
        key = str(m.get("cik")) if m.get("cik") not in (None, "") else None
        if key and key in by_cik:
            excluded[t] = f"same CIK as {by_cik[key]} (one member per CIK)"
            continue
        if key:
            by_cik[key] = t
        members[t] = m
    return {"schema": SCHEMA, "built": built or _today(), "builder": "industry_returns.py", "rule": RULE,
            "members": {t: members[t] for t in sorted(members)}, "groups": groups_from(members),
            "excluded": {t: excluded[t] for t in sorted(excluded)}}


def groups_from(members):
    """The groups document built from the member records alone: per (ladder family, SIC level, code) with >= 2
    members, keyed `<ladder>|<level>:<code>`, sorted by key (build() and consistency_problems() share it)."""
    groups = {}
    acc = collections.defaultdict(list)
    for t, m in members.items():
        for lvl in M.INDUSTRY_LEVELS:
            acc[(m["ladder"], lvl, m["sic"][:lvl])].append(t)
    for (lad, lvl, code), ts in sorted(acc.items()):
        if len(ts) < 2:
            continue
        ts = sorted(ts)
        vals = [_value(members[t]) for t in ts]
        kept = [v for v in vals if v is not None and v != -math.inf]
        med = M._median(kept) if kept else None
        mix = collections.Counter(members[t]["measure"] for t in ts)
        groups[f"{lad}|{lvl}:{code}"] = {
            "ladder": lad, "level": lvl, "code": code,
            "label": _label(lvl, code, [members[t].get("sic_description") for t in ts]),
            "members": ts, "n": len(kept), "n_dropped": len(vals) - len(kept),
            "median": (M._r(med) if med is not None and math.isfinite(med) else None),
            "median_note": (M.NOTE_INF if med == math.inf else None),
            "metric_mix": {k: mix[k] for k in sorted(mix)}}
    return groups


def consistency_problems(doc):
    """[] when an industry_returns.json document is internally consistent, else one line per problem: the schema,
    builder and rule this code writes; members sorted, each on a known measure and ladder, its median or its
    median_note (never both, never neither), its SIC digits; one member per CIK; no member also excluded; the groups
    exactly what groups_from(members) builds (keys, members, n, n_dropped, median, metric mix, labels).
    [L3 review R2, 2026-10-21] It says nothing about whether the members' values are CURRENT: a company PR does not
    rebuild the file, so between two daily-cron runs it is legitimately one or more re-scores behind (03b §3.3.2 /
    §3.3.3) — --check is the currency tool, and the suite tests consistency only."""
    if not isinstance(doc, dict):
        return ["not a JSON object"]
    probs = []
    for k, want in (("schema", SCHEMA), ("builder", "industry_returns.py"), ("rule", RULE)):
        if doc.get(k) != want:
            probs.append(f"{k} is {doc.get(k)!r}, this code writes {want!r}")
    mem, exc = doc.get("members"), doc.get("excluded")
    if not isinstance(mem, dict) or not isinstance(exc, dict) or not isinstance(doc.get("groups"), dict):
        return probs + ["members, groups and excluded must be objects"]
    if list(mem) != sorted(mem):
        probs.append("members are not sorted by ticker")
    ciks = {}
    for t, m in mem.items():
        if not isinstance(m, dict):
            probs.append(f"member {t} is not an object")
            continue
        if m.get("measure") not in ("roic", "roic_tangible", "roe") or m.get("ladder") not in ("default", "real_assets", "roe"):
            probs.append(f"member {t}: measure {m.get('measure')!r} / ladder {m.get('ladder')!r}")
        if m.get("ladder") != M.ladder_family(m.get("business_type")):
            probs.append(f"member {t}: ladder {m.get('ladder')!r} is not business type {m.get('business_type')!r}'s")
        if (m.get("median") is None) == (m.get("median_note") is None):
            probs.append(f"member {t}: exactly one of median / median_note must be set")
        if not str(m.get("sic") or "").isdigit():
            probs.append(f"member {t}: SIC {m.get('sic')!r}")
        if t in exc:
            probs.append(f"member {t} is also listed in excluded")
        c = m.get("cik")
        if c not in (None, ""):
            if str(c) in ciks:
                probs.append(f"members {ciks[str(c)]} and {t} share CIK {c} (one member per CIK)")
            ciks.setdefault(str(c), t)
    if probs:
        return probs
    try:
        want = groups_from(mem)
    except (KeyError, TypeError, ValueError) as e:
        return [f"groups cannot be rebuilt from the members: {e!r}"]
    got = doc["groups"]
    for k in sorted(set(want) | set(got)):
        if want.get(k) != got.get(k):
            probs.append(f"group {k}: {'missing' if k not in got else 'not built from its members' if k in want else 'not a group of these members'}")
    return probs


def write(path, out):
    """Stable write (only when something besides `built` changed); True when written."""
    return write_json_if_changed(path, out, volatile=VOLATILE, indent=1, ensure_ascii=False, allow_nan=False)


def summary(out):
    meas = len(out["members"])
    lines = [f"industry_returns: {meas} members, {len(out['excluded'])} excluded, {len(out['groups'])} groups (>= 2 members)"]
    for k, g in out["groups"].items():
        if g["n"] >= M.INDUSTRY_MIN_PEERS:
            med = "unbounded" if g["median_note"] == M.NOTE_INF else (f"{g['median'] * 100:.1f}%" if g["median"] is not None else "n/m")
            lines.append(f"  {k}: {g['label']} n {g['n']} (dropped {g['n_dropped']}) median {med}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Same-ladder SIC-group governing-return medians -> _system/industry_returns.json")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--check", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    if sum(bool(x) for x in (a.write, a.json, a.check)) > 1:
        print("industry_returns.py: use one of --write, --json PATH, --check", file=sys.stderr)
        return 2
    path = os.path.join(BASE, "_system", M.INDUSTRY_FILE)
    out = build(BASE)
    if a.check:
        if os.path.exists(path) and same_content(path, out, VOLATILE):
            print(f"industry_returns.py --check: {path} is current")
            return 0
        print(f"industry_returns.py --check: {path} differs from a fresh build (apart from `built`) — run --write")
        return 1
    if a.write or a.json:
        target = a.json or path
        w = write(target, out)
        print(f"industry_returns.py: {target} {'written' if w else 'unchanged'}")
        print(summary(out))
        return 0
    print(summary(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
