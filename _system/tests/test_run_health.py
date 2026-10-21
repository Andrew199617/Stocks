#!/usr/bin/env python3
"""run_health.py — page Andrew after 2 consecutive failed runs of a job (engine 5.7, Andrew's ruling R5 of
2026-10-19; design 05 §5, §9). Run: python _system/tests/test_run_health.py.

The miss it stops: a job failed five runs in a row before anyone noticed. Covered: the first failure is silent and
the second prints one ALERT line, once; STILL FAILING once per --remind-hours window; RECOVERED once after an alert
and silence otherwise; a start whose earlier run never recorded counts as a failure once that run is older than the
job's timeout_secs (cron front matter, 3600 s by default), and overlapping runs inside it are not failures (review
2026-10-21); a crash that started before a later ok is history, not part of the failure run; check reads the cadence from
the cron front matter (disabled jobs and dcf-live-refresh skipped, a 15-minute job idle 80 minutes alerts — over
max(3 x 15, 15 + 60) — and 70 does not, once per 24 h); concurrent records lose nothing; reasons are one line, truncated; the state file is gitignored.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ops_harness as H  # noqa: E402


class State:
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="run_health_")
        self.path = os.path.join(self.dir, "run_health.json")

    def run(self, *args, now="2026-10-19T14:15:00", stdin=None):
        r = H.run("run_health.py", *args, base=self.dir, stdin=stdin,
                  env={"RUN_HEALTH_FILE": self.path, "STOCKS_NOW": now})
        assert r.returncode == 0, f"run_health {args} exited {r.returncode}: {r.stderr}"
        lines = [x for x in r.stdout.splitlines() if x.strip()]
        assert len(lines) <= 1, f"more than one line printed: {r.stdout!r}"
        return lines[0] if lines else ""

    def job(self, name):
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)["jobs"][name]

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


J = "dcf-hourly-sweep"


def test_first_failure_silent_second_alerts_once():
    s = State()
    try:
        assert s.run("start", J, now="2026-10-19T14:15:00") == ""
        assert s.run("record", J, "fail", "--reason", "preflight: ENGINE DRIFT — x", now="2026-10-19T14:20:00") == ""
        s.run("start", J, now="2026-10-19T14:30:00")
        line = s.run("record", J, "fail", "--reason", "preflight: ENGINE DRIFT — y", now="2026-10-19T14:35:00")
        assert line.startswith(f"ALERT {J}: 2 failed runs in a row (first 2026-10-19 14:15 ET, latest 14:30 ET). "
                               "Last reason: preflight: ENGINE DRIFT — y History: python3 _system/run_health.py "
                               f"status {J}"), line
        s.run("start", J, now="2026-10-19T14:45:00")
        assert s.run("record", J, "fail", "--reason", "z", now="2026-10-19T14:50:00") == "", "the ALERT prints once"
        j = s.job(J)
        assert j["consecutive_failures"] == 3 and j["alerted_at"] and len(j["history"]) == 3
    finally:
        s.close()


def test_still_failing_once_per_remind_window():
    s = State()
    try:
        s.run("record", J, "fail", "--reason", "a", now="2026-10-19T10:00:00")
        assert s.run("record", J, "fail", "--reason", "b", now="2026-10-19T10:15:00").startswith("ALERT ")
        assert s.run("record", J, "fail", "--reason", "c", now="2026-10-20T09:00:00") == "", "inside 24 h: silent"
        line = s.run("record", J, "fail", "--reason", "d", now="2026-10-20T10:20:00")
        assert line == f"STILL FAILING {J}: 4 failed runs in a row since 2026-10-19 10:00 ET. Last reason: d", line
        assert s.run("record", J, "fail", "--reason", "e", now="2026-10-20T11:00:00") == ""
        assert s.run("record", J, "fail", "--reason", "f", now="2026-10-21T10:30:00").startswith("STILL FAILING ")
    finally:
        s.close()


def test_recovered_once_after_an_alert_and_silent_otherwise():
    s = State()
    try:
        s.run("record", J, "fail", "--reason", "a", now="2026-10-19T14:15:00")
        assert s.run("record", J, "ok", now="2026-10-19T14:30:00") == "", "a recovery without an alert is silent"
        s.run("record", J, "fail", "--reason", "a", now="2026-10-19T14:45:00")
        s.run("record", J, "fail", "--reason", "b", now="2026-10-19T15:00:00")
        s.run("record", J, "fail", "--reason", "c", now="2026-10-19T15:15:00")
        line = s.run("record", J, "ok", now="2026-10-19T16:00:00")
        assert line == f"RECOVERED {J}: ok again at 2026-10-19 16:00 ET after 3 failed runs (since 14:45 ET).", line
        assert s.run("record", J, "ok", now="2026-10-19T16:15:00") == ""
        j = s.job(J)
        assert j["consecutive_failures"] == 0 and j["alerted_at"] is None and j["last_ok_at"]
    finally:
        s.close()


def test_start_without_record_counts_as_failure():
    """A run that never recorded is failed once it is older than the job's timeout (3600 s here: no cron file names
    the job), at the next start."""
    s = State()
    try:
        s.run("start", J, now="2026-10-19T14:15:00")
        assert s.run("start", J, now="2026-10-19T15:20:00") == ""   # the 14:15 run is past its timeout: failure 1
        line = s.run("start", J, now="2026-10-19T16:25:00")          # the 15:20 run too: failure 2
        assert line.startswith(f"ALERT {J}: 2 failed runs in a row (first 2026-10-19 14:15 ET, latest 15:20 ET)"), line
        assert ("did not finish (started 2026-10-19T15:20:00-04:00, no record within its 3600 s timeout — timeout or "
                "crash)") in line, line
        assert s.job(J)["open_starts"] == ["2026-10-19T16:25:00-04:00"]
    finally:
        s.close()


def test_overlapping_runs_inside_the_timeout_are_not_failures():
    """Review 2026-10-21 (P2): a 15-minute job with a 60-minute timeout overlaps its next firing; one open start per
    job read each overlap as a crash and printed an ALERT, then a RECOVERED, for runs that all succeeded."""
    s = State()
    try:
        for t in ("10:00", "10:15", "10:30"):
            assert s.run("start", J, now=f"2026-10-21T{t}:00") == "", t
        for t in ("10:40", "10:50", "11:05"):
            assert s.run("record", J, "ok", now=f"2026-10-21T{t}:00") == "", t
        j = s.job(J)
        assert j["consecutive_failures"] == 0 and j["open_starts"] == [] and j["alerted_at"] is None, j
        assert [h["result"] for h in j["history"]] == ["ok", "ok", "ok"], j["history"]
    finally:
        s.close()


def test_a_crash_before_a_later_ok_is_not_in_the_failure_run():
    """A run that never recorded but started before an ok that came later is history, not part of the current run
    of consecutive failures (no ALERT for two failures with an ok between them)."""
    s = State()
    try:
        s.run("start", J, now="2026-10-21T10:00:00")              # hangs and is killed
        s.run("start", J, now="2026-10-21T10:15:00")
        s.run("record", J, "ok", now="2026-10-21T10:25:00")       # closes the newest run (10:15)
        assert s.run("start", J, now="2026-10-21T11:05:00") == ""  # 10:00 expires: history only
        j = s.job(J)
        assert j["consecutive_failures"] == 0 and [h["result"] for h in j["history"]] == ["ok", "fail"], j
        assert s.run("record", J, "fail", "--reason", "x", now="2026-10-21T11:10:00") == "", "one failure: silent"
        assert s.job(J)["consecutive_failures"] == 1
    finally:
        s.close()


def test_the_timeout_comes_from_the_cron_front_matter():
    s = State()
    crons = os.path.join(s.dir, "crons")
    try:
        _cron(crons, "minutely", "c.md", "id: dcf-live-refresh\nenabled: true\nschedule:\n  kind: interval\n"
                                         "  every: 30m\ntimeout_secs: 1500\n")
        import run_health
        assert run_health.job_timeout("dcf-live-refresh", crons) == 1500
        assert run_health.job_timeout("no-such-job", crons) == run_health.DEFAULT_TIMEOUT_SECS == 3600
        L = "dcf-live-refresh"
        assert s.run("start", L, "--crons", crons, now="2026-10-21T10:00:00") == ""
        assert s.run("start", L, "--crons", crons, now="2026-10-21T10:20:00") == "", "inside 1500 s: still running"
        line = s.run("start", L, "--crons", crons, now="2026-10-21T10:50:00")   # both are past 1500 s
        assert line.startswith(f"ALERT {L}: 2 failed runs in a row (first 2026-10-21 10:00 ET, latest 10:20 ET)"), line
        assert "no record within its 1500 s timeout" in line, line
    finally:
        s.close()


def test_a_state_file_from_before_the_review_is_read():
    s = State()
    try:
        with open(s.path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "jobs": {J: {"open_start": "2026-10-21T08:00:00-04:00", "consecutive_failures": 0,
                                                  "history": []}}}, f)
        assert s.run("start", J, now="2026-10-21T09:30:00") == ""   # the 08:00 run is past 3600 s: failure 1
        j = s.job(J)
        assert "open_start" not in j and j["open_starts"] == ["2026-10-21T09:30:00-04:00"], j
        assert j["consecutive_failures"] == 1 and j["first_failure_at"] == "2026-10-21T08:00:00-04:00", j
    finally:
        s.close()


def _cron(folder, sub, name, front):
    p = os.path.join(folder, sub, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write("---\n" + front + "---\nBody.\n")


def test_check_reads_cadence_from_cron_front_matter():
    s = State()
    crons = os.path.join(s.dir, "crons")
    try:
        _cron(crons, "minutely", "a.md", "id: dcf-hourly-sweep\nenabled: true\nschedule:\n  kind: interval\n"
                                         "  timezone: America/New_York\n  every: 15m\n")
        _cron(crons, "minutely", "b.md", "id: dcf-sweep-parallel\nenabled: false\nschedule:\n  kind: interval\n"
                                         "  every: 15m\n")
        _cron(crons, "minutely", "c.md", "id: dcf-live-refresh\nenabled: true\nschedule:\n  kind: interval\n"
                                         "  every: 30m\n")
        _cron(crons, "daily", "d.md", "id: dcf-daily-ranking\nenabled: true\nschedule:\n  kind: daily\n"
                                      "  timezone: '@user.current'\n  time: 19:07:00\n")
        for job in ("dcf-hourly-sweep", "dcf-sweep-parallel", "dcf-live-refresh", "dcf-daily-ranking"):
            s.run("start", job, now="2026-10-19T09:00:00")
            s.run("record", job, "ok", now="2026-10-19T09:05:00")
        # overdue = idle longer than max(3 x interval, interval + 60 min): 75 min for a 15-minute job (a run may take
        # the cron's 60-minute timeout before the next one starts)
        assert s.run("check", "--crons", crons, now="2026-10-19T10:10:00") == "", "70 min idle: under 15 + 60"
        line = s.run("check", "--crons", crons, now="2026-10-19T10:20:00")
        assert line == ("ALERT dcf-hourly-sweep: no run started since 2026-10-19 09:00 ET (expected every 15m) — "
                        "check the scheduler."), line
        assert s.run("check", "--crons", crons, now="2026-10-19T12:00:00") == "", "once per 24 h"
        line = s.run("check", "--crons", crons, now="2026-10-22T10:00:00")   # daily: over 3 days
        assert line.startswith("ALERT ") and line.endswith(" — check the scheduler.") and line.count("ALERT") == 1, line
        assert "dcf-hourly-sweep: no run started since 2026-10-19 09:00 ET (expected every 15m)" in line, line
        assert "dcf-daily-ranking: no run started since 2026-10-19 09:00 ET (expected every day)" in line, line
        assert "dcf-sweep-parallel" not in line and "dcf-live-refresh" not in line, line
        s.run("start", "dcf-hourly-sweep", now="2026-10-22T10:05:00")
        assert "dcf-hourly-sweep" not in s.run("check", "--crons", crons, now="2026-10-22T10:10:00")
        # the real cron files parse (every enabled job has an id and a cadence)
        import run_health
        real = os.path.join(H.ROOT, "automation", "crons")
        import glob
        ids = []
        for f in glob.glob(os.path.join(real, "*", "*.md")):
            fm = run_health.parse_front_matter(open(f, encoding="utf-8").read())
            assert fm.get("id") and run_health.interval_minutes(fm), (f, fm)
            ids.append(fm["id"])
        assert "dcf-hourly-sweep" in ids and "dcf-daily-ranking" in ids, ids
    finally:
        s.close()


def test_concurrent_records_lose_nothing():
    s = State()
    try:
        env = dict(os.environ, RUN_HEALTH_FILE=s.path, STOCKS_NOW="2026-10-19T14:15:00", PYTHONIOENCODING="utf-8")

        def rec(i):
            subprocess.run([sys.executable, os.path.join(H.SYS, "run_health.py"), "record", f"job-{i % 4}", "fail",
                            "--reason", f"r{i}"], env=env, capture_output=True, timeout=120)
        ts = [threading.Thread(target=rec, args=(i,)) for i in range(12)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        with open(s.path, encoding="utf-8") as f:
            jobs = json.load(f)["jobs"]
        assert sorted(jobs) == [f"job-{k}" for k in range(4)], jobs.keys()
        assert sum(j["consecutive_failures"] for j in jobs.values()) == 12, {k: v["consecutive_failures"] for k, v in jobs.items()}
        assert sum(len(j["history"]) for j in jobs.values()) == 12
    finally:
        s.close()


def test_reason_is_one_line_and_truncated():
    s = State()
    try:
        s.run("record", J, "fail", "--stdin", stdin="line one\nline two\r\n  line three\n")
        assert s.job(J)["last_reason"] == "line one / line two / line three", s.job(J)["last_reason"]
        s.run("record", J, "fail", "--reason", "x" * 500)
        r = s.job(J)["last_reason"]
        assert len(r) == 300 and r.endswith("…"), len(r)
    finally:
        s.close()


def test_state_file_is_gitignored():
    o = H.make_origin({".gitignore": open(os.path.join(H.ROOT, ".gitignore"), encoding="utf-8").read()})
    try:
        c = H.clone(o)
        r = subprocess.run(["git", "-C", c, "check-ignore", "-q", "_system/run_health.json"])
        assert r.returncode == 0, "_system/run_health.json is not gitignored"
        r = subprocess.run(["git", "-C", c, "check-ignore", "-q", "_system/run_health.json.lock"])
        assert r.returncode == 0
    finally:
        o.close()


def test_unreadable_state_exits_1():
    s = State()
    try:
        with open(s.path, "w", encoding="utf-8") as f:
            f.write("{not json")
        r = H.run("run_health.py", "record", J, "ok", base=s.dir, env={"RUN_HEALTH_FILE": s.path})
        assert r.returncode == 1 and "cannot read" in r.stderr and r.stdout == "", (r.returncode, r.stderr)
        assert H.run("run_health.py", "record", J, "maybe", base=s.dir, env={"RUN_HEALTH_FILE": s.path}).returncode == 2
    finally:
        s.close()


if __name__ == "__main__":
    sys.exit(H.run_tests(globals()))
