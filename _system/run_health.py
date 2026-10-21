#!/usr/bin/env python3
"""Job health: page Andrew after 2 consecutive failed runs of a job (engine 5.7, Andrew's ruling R5 of 2026-10-19).

The miss it stops: a cron job failed five runs in a row before anyone noticed. Every cron body opens a run with
`start` and closes it with `record`; the line this script prints is the only health message, and it goes to chat.

Usage:
  python3 _system/run_health.py start <job>
  python3 _system/run_health.py record <job> ok|fail [--reason TEXT | --stdin] [--threshold 2] [--remind-hours 24]
  python3 _system/run_health.py status [<job>] [--json]
  python3 _system/run_health.py check [--crons DIR]

start, record and check print AT MOST ONE LINE to stdout, and that line is for chat (nothing printed = nothing to
post); status is the human query (one summary line per job, then the job's history when one is named).
  record ok    the failure count resets; after an alert it prints, once,
               "RECOVERED <job>: ok again at <time> after <n> failed runs (since <time>)."
  record fail  the count goes up; at exactly the threshold (2) it prints
               "ALERT <job>: 2 failed runs in a row (first <time>, latest <time>). Last reason: <reason> History: ...";
               while the job keeps failing it prints "STILL FAILING <job>: …" once every --remind-hours (24) after
               the alert or the last reminder, and nothing otherwise.
  start        a previous run that started and never recorded (a timeout, a crash, a kill) counts as a failed run
               first ("did not finish (started <ts>, no record — timeout or crash)"), which may print the ALERT.
  check        reads every cron file's front matter (automation/crons/*/*.md: id, enabled, schedule.kind / every;
               daily = 1440 minutes): an enabled job that has recorded at least once, and is not market-hours only
               (dcf-live-refresh), is overdue when now − its last start > max(3 × interval, interval + 60 min); one
               "ALERT …: no run started since …" line names every overdue job, at most once per 24 h per job.
Reasons are one line (newlines become " / "), at most 300 characters.

State: $RUN_HEALTH_FILE or <STOCKS_BASE>/_system/run_health.json — per machine, gitignored; every write runs under
<state>.lock and is saved atomically (temp file + os.replace, retried on Windows). Time: $STOCKS_NOW (tests).
Exit 0; 2 usage; 1 when the state file cannot be read or written (message on stderr — the cron body then reports
"run_health failed: …").
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ops  # noqa: E402
from _lock import locked  # noqa: E402

VERSION = 1
HISTORY_KEEP = 50
REASON_MAX = 300
NO_OVERDUE = frozenset({"dcf-live-refresh"})   # market hours only: no run outside them is not a failure
OVERDUE_REPEAT_HOURS = 24


class StateError(Exception):
    pass


def state_path():
    return os.environ.get("RUN_HEALTH_FILE") or os.path.join(_ops.base_dir(), "_system", "run_health.json")


def _load(path):
    if not os.path.exists(path):
        return {"version": VERSION, "jobs": {}}
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        raise StateError(f"run_health: cannot read {path} ({type(e).__name__}: {e}) — fix or delete it "
                         "(it is per-machine state, never committed)")
    if not (isinstance(d, dict) and isinstance(d.get("jobs"), dict)):
        raise StateError(f"run_health: {path} is not a run_health state file (no 'jobs' object) — fix or delete it")
    return d


def _save(path, d):
    try:
        _ops.write_json_atomic(path, d)
    except OSError as e:
        raise StateError(f"run_health: cannot write {path} ({type(e).__name__}: {e})")


def _job(d, name):
    return d["jobs"].setdefault(name, {"open_start": None, "last_start": None, "last_end": None, "last_result": None,
                                       "last_reason": None, "consecutive_failures": 0, "first_failure_at": None,
                                       "last_ok_at": None, "alerted_at": None, "reminded_at": None,
                                       "overdue_alerted_at": None, "history": []})


def one_line(text):
    s = re.sub(r"\s*[\r\n]+\s*", " / ", str(text or "").strip())
    return s if len(s) <= REASON_MAX else s[:REASON_MAX - 1] + "…"


def _t(s):
    return _ops.parse_ts(s)


def _fail(job, name, reason, now, threshold, remind_hours):
    """Apply one failed run; returns the chat line or None."""
    started = job.get("open_start")
    job["consecutive_failures"] = int(job.get("consecutive_failures") or 0) + 1
    when = started or _ops.iso(now)
    if job["consecutive_failures"] == 1:
        job["first_failure_at"] = when
    job.update(last_end=_ops.iso(now), last_result="fail", last_reason=reason, open_start=None)
    job["history"] = (job.get("history") or []) + [{"start": started, "end": _ops.iso(now), "result": "fail",
                                                     "reason": reason}]
    job["history"] = job["history"][-HISTORY_KEEP:]
    n = job["consecutive_failures"]
    first = _t(job.get("first_failure_at"))
    if n == threshold:
        job["alerted_at"] = _ops.iso(now)
        job["reminded_at"] = None
        return (f"ALERT {name}: {n} failed runs in a row (first {_ops.et_hm(first)}, latest "
                f"{_ops.et_hm(_t(when), ref=first)}). Last reason: {reason} History: python3 _system/run_health.py "
                f"status {name}")
    if n > threshold and job.get("alerted_at"):
        last = _t(job.get("reminded_at")) or _t(job.get("alerted_at"))
        if last is None or now - last >= datetime.timedelta(hours=remind_hours):
            job["reminded_at"] = _ops.iso(now)
            return (f"STILL FAILING {name}: {n} failed runs in a row since {_ops.et_hm(first)}. "
                    f"Last reason: {reason}")
    return None


def cmd_start(name, now):
    path = state_path()
    with locked(f"{path}.lock"):
        d = _load(path)
        job = _job(d, name)
        line = None
        if job.get("open_start"):
            line = _fail(job, name, f"did not finish (started {job['open_start']}, no record — timeout or crash)",
                         now, threshold=2, remind_hours=24)
        job["open_start"] = _ops.iso(now)
        job["last_start"] = _ops.iso(now)
        _save(path, d)
    return line


def cmd_record(name, result, reason, now, threshold, remind_hours):
    path = state_path()
    with locked(f"{path}.lock"):
        d = _load(path)
        job = _job(d, name)
        if result == "fail":
            line = _fail(job, name, one_line(reason) or "no reason given", now, threshold, remind_hours)
        else:
            line = None
            n = int(job.get("consecutive_failures") or 0)
            if job.get("alerted_at"):
                since = _t(job.get("first_failure_at"))
                line = (f"RECOVERED {name}: ok again at {_ops.et_hm(now)} after {n} failed run{'s' if n != 1 else ''} "
                        f"(since {_ops.et_hm(since, ref=now)}).")
            started = job.get("open_start")
            job.update(consecutive_failures=0, first_failure_at=None, alerted_at=None, reminded_at=None,
                       last_end=_ops.iso(now), last_result="ok", last_reason=one_line(reason) or None,
                       last_ok_at=_ops.iso(now), open_start=None)
            job["history"] = ((job.get("history") or []) + [{"start": started, "end": _ops.iso(now), "result": "ok",
                                                              "reason": one_line(reason) or None}])[-HISTORY_KEEP:]
        _save(path, d)
    return line


# --------------------------------------------------------------------------------------------- check
def parse_front_matter(text):
    """The cron file's front matter as a flat dict: top-level keys, and 'schedule.<key>' for the schedule block."""
    lines = (text or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out, block = {}, None
    for raw in lines[1:]:
        if raw.strip() == "---":
            break
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not m:
            continue
        indent, key, val = len(m.group(1)), m.group(2), m.group(3).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        if indent == 0:
            block = key if val == "" else None
            if val != "":
                out[key] = val
        elif block:
            out[f"{block}.{key}"] = val
    return out


def interval_minutes(fm):
    kind = fm.get("schedule.kind")
    if kind == "daily":
        return 1440
    if kind == "interval":
        m = re.fullmatch(r"(\d+)\s*([mhd])", fm.get("schedule.every", "").strip())
        if m:
            return int(m.group(1)) * {"m": 1, "h": 60, "d": 1440}[m.group(2)]
    return None


def default_crons():
    return os.path.join(_ops.base_dir(), "automation", "crons")


def cmd_check(crons, now):
    import glob
    jobs = []
    for f in sorted(glob.glob(os.path.join(crons, "*", "*.md"))):
        try:
            with open(f, encoding="utf-8") as fh:
                fm = parse_front_matter(fh.read())
        except OSError:
            continue
        mins = interval_minutes(fm)
        if fm.get("id") and str(fm.get("enabled", "")).lower() == "true" and mins and fm["id"] not in NO_OVERDUE:
            jobs.append((fm["id"], mins))
    path = state_path()
    with locked(f"{path}.lock"):
        d = _load(path)
        overdue = []
        for name, mins in jobs:
            job = d["jobs"].get(name)
            if not job or not job.get("last_start"):
                continue   # never recorded on this machine: nothing to compare
            last = _t(job["last_start"])
            limit = datetime.timedelta(minutes=max(3 * mins, mins + 60))
            if last is None or now - last <= limit:
                continue
            seen = _t(job.get("overdue_alerted_at"))
            if seen is not None and now - seen < datetime.timedelta(hours=OVERDUE_REPEAT_HOURS):
                continue
            job["overdue_alerted_at"] = _ops.iso(now)
            every = f"{mins // 1440}d" if mins % 1440 == 0 else f"{mins // 60}h" if mins % 60 == 0 else f"{mins}m"
            overdue.append(f"{name}: no run started since {_ops.et_hm(last)} (expected every "
                           f"{'day' if mins == 1440 else every})")
        if overdue:
            _save(path, d)
    if not overdue:
        return None
    return "ALERT " + "; ".join(overdue) + " — check the scheduler."


def cmd_status(name, as_json):
    d = _load(state_path())
    jobs = {name: d["jobs"].get(name)} if name else d["jobs"]
    if as_json:
        return json.dumps(jobs if name is None else jobs.get(name), indent=1)
    lines = []
    for jn, job in sorted(jobs.items()):
        if not job:
            lines.append(f"{jn}: no runs recorded")
            continue
        n = job.get("consecutive_failures") or 0
        lines.append(f"{jn}: last {job.get('last_result') or '-'} at {job.get('last_end') or '-'}"
                     + (f"; {n} failed in a row since {job.get('first_failure_at')}" if n else "")
                     + (f"; alerted {job.get('alerted_at')}" if job.get("alerted_at") else "")
                     + (f"; running since {job.get('open_start')}" if job.get("open_start") else "")
                     + (f"; last reason: {job.get('last_reason')}" if job.get("last_reason") else ""))
        if name:
            for h in reversed(job.get("history") or []):
                lines.append(f"  {h.get('start') or '-'} -> {h.get('end') or '-'}  {h.get('result')}"
                             + (f"  {h.get('reason')}" if h.get("reason") else ""))
    return "\n".join(lines) if lines else "no jobs recorded"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="run_health.py", description="Job health (R5).")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("start")
    s.add_argument("job")
    r = sub.add_parser("record")
    r.add_argument("job")
    r.add_argument("result", choices=("ok", "fail"))
    g = r.add_mutually_exclusive_group()
    g.add_argument("--reason")
    g.add_argument("--stdin", action="store_true")
    r.add_argument("--threshold", type=int, default=2)
    r.add_argument("--remind-hours", type=float, default=24)
    st = sub.add_parser("status")
    st.add_argument("job", nargs="?")
    st.add_argument("--json", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("--crons")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if not a.cmd:
        print(__doc__, file=sys.stderr)
        return 2
    if a.cmd == "record" and a.threshold < 1:
        print("run_health: --threshold must be >= 1", file=sys.stderr)
        return 2
    now = _ops.now_et()
    try:
        if a.cmd == "start":
            line = cmd_start(a.job, now)
        elif a.cmd == "record":
            reason = sys.stdin.read() if a.stdin else a.reason
            line = cmd_record(a.job, a.result, reason, now, a.threshold, a.remind_hours)
        elif a.cmd == "check":
            line = cmd_check(a.crons or default_crons(), now)
        else:
            print(cmd_status(a.job, a.json))
            return 0
    except StateError as e:
        print(str(e), file=sys.stderr)
        return 1
    if line:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
