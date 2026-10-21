#!/usr/bin/env python3
"""Queue manager for the DCF sweep (v5, 2026-10-13 — replaces hand-edited queue.json).

Usage:
  python3 queue.py [--file PATH] claim          -> print the claimed ticker
  python3 queue.py [--file PATH] done <TICKER>   (refuses, exit 1, an engine 5.7 run whose analysis.md fails
                                                   check_quotes.py — R3, 2026-10-19)
  python3 queue.py [--file PATH] block <TICKER> [reason...]
  python3 queue.py [--file PATH] block <TICKER> --stdin   (reason read from stdin)
  python3 queue.py [--file PATH] reap            -> print reaped tickers
  python3 queue.py [--file PATH] requeue <TICKER>   (blocked/expired -> pending)
  python3 queue.py [--file PATH] migrate-data-gap   (one-off status migration)
  python3 queue.py refresh <TICKER> --stdin         (done -> pending: a newer filing exists; v5.4)
  python3 queue.py pass2-claim                      -> print the second-pass ticker (v5.4)
  python3 queue.py pass2-check <TICKER>             (exit 1 when the name was refreshed or re-scored after the
                                                     claim; records nothing — run before writing anything for the review)
  python3 queue.py pass2-done <TICKER> <done_no_change|done_changed>
                                                    (refuses, exit 1, when the name was re-scored after the claim,
                                                     or when an engine 5.7 run's analysis.md fails check_quotes.py)
  python3 queue.py pass2-reset <TICKER>             (-> pending)
With --file, the second-pass queue is the second_pass_queue.json beside PATH.

All read-modify-write cycles run under an fcntl lock on <queue>.lock and are
saved atomically (tmp file + rename), so parallel workers can never claim the
same ticker or clobber each other's updates. claim stamps claimed_at (ET) and
runs the reaper first, under the same lock (round-2 audit: no job ever called
reap, so a crashed claim stayed in progress forever). block auto-selects the
status: a reason starting with "DATA_GAP" lands in blocked_data_gap (the list
awaiting override decisions), anything else in blocked_no_data. Reasons should
arrive via --stdin: a quoted shell argument mangles dollar amounts and quotes
(TKO's note lost the digits after each "$").
The queue.json schema is unchanged: {built, cutoff_market_cap_b, universe_size,
queue: [{ticker, queue_pos, status, ...}]}.

Scoring generations (Codex review of PR #2): pass 2 reviews one pass-1
scoring run, not a ticker forever. A generation is identified by the
claimed_at stamp a DONE queue entry keeps from the pass-1 claim that produced
its score (done keeps it; refresh, requeue and the reaper drop it, so every
re-score carries a new one); a done entry without claimed_at falls back to
its completed date, and APP (outside the queue) has a single generation (a
re-score made by hand, outside claim/done, is not a new generation: run
pass2-reset for it). Only a claim stamp proves a scoring run: a done entry
that lost its stamp (build_universe.py rebuilt queue.json keeping only
ticker, queue_pos and status until 2026-10-16; it now keeps every surviving
entry verbatim) neither reopens a done review nor refuses a claim, so a
universe rebuild does not re-review every name; the next re-score stamps
the entry again. The generation is deliberately not derived from
score.json or dcf_numbers.json: pass 2's own make_score.py / engine rerun
rewrites both, which would make every pass-2 worker look obsolete at its
own pass2-done.
pass2-claim records the generation on the entry; a done entry recorded
against an older generation is eligible again; refresh puts a done
second-pass entry back to pending; and pass2-done refuses when the score
was refreshed or re-scored after the claim. pass2-check runs the same test
without recording anything; the worker runs it before it writes anything
for the review (second_pass.md, the analysis.md addendum, judgment.json,
ttm.json, the engine), so an obsolete review stops before it writes. Both
refusals name their case and what is true in it: (a) the name is pending,
being re-scored or blocked, so the re-score it awaits rewrites
judgment.json, dcf_numbers.json and score.json; (b) a newer generation is
already scored, so nothing will rewrite what an obsolete worker wrote. After
a pass2-check refusal the worker has written nothing and writes nothing;
after a pass2-done refusal it deletes the second_pass.md it wrote in this
run and leaves the rest (SECOND_PASS.md step 7). A live in-progress claim
is never re-issued early, even for a newer generation (it is reclaimable
once its 90-minute lease expires; the cron timeout is 60 minutes), so an
obsolete worker can never finish a newer generation's claim. Entries written before generations existed: a done one
counts for the current generation unless the score was completed on the
review date or later (a date cannot order a review and a re-score on the
same day, so that case gets one more review); an in-progress one is refused
at pass2-done when the score's generation stamp is later than its
claimed_at.

Locks and Windows (2026-10-16, so Andrew can run the tools from a PC). Two
locks: <queue>.lock serialises every queue.json read-modify-write (claim,
done, block, requeue, refresh, reap, migrate-data-gap, and
build_universe.py's rebuild); second_pass_queue.json.lock serialises the
second-pass commands. No code path holds both, so they cannot deadlock:
refresh releases the queue lock before it takes the second-pass lock, and
pass2-claim / pass2-check / pass2-done read queue.json without its lock (a
snapshot: a refresh that lands after it is caught by refresh's own reset or
by the next pass2-check / pass2-done). A future path that needs both takes
the queue lock first, then the second-pass lock, never the reverse. Every
save is a temp file + os.replace, retried on PermissionError (Windows
refuses to replace a file another process holds open: build_site.py,
filing_watch.py, an editor, a virus scanner); every load is retried on
PermissionError and on a parse failure (on Windows a read that lands while
another process replaces the file fails to open). A second-pass queue that
still cannot be read stops the command instead of being treated as empty,
which would save over every recorded review.
"""
import json, os, sys, time, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lock import locked  # v5.4: cross-platform exclusive file lock (fcntl / msvcrt)
from _stable import _replace  # os.replace, retried on a Windows PermissionError
import check_quotes as _quotes  # v5.7 (R3, Andrew 2026-10-19): the quote gate on done / pass2-done

ET = ZoneInfo("America/New_York")
BASE = os.environ.get("STOCKS_BASE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # v5.4
DEFAULT_FILE = f"{BASE}/_system/queue.json"
PASS2_FILE = f"{BASE}/_system/second_pass_queue.json"  # = _pass2_path(DEFAULT_FILE)
LEASE_MINUTES = 90
READ_ATTEMPTS, REPLACE_ATTEMPTS, RETRY_PAUSE = 20, 50, 0.1  # ~2 s / ~5 s (see "Locks and Windows")


def now_et():
    return datetime.datetime.now(ET)


def load(path, attempts=READ_ATTEMPTS, pause=RETRY_PAUSE):
    """json.load, retried on PermissionError and on a parse failure (a read
    that lands mid-replace on Windows); FileNotFoundError is raised at once."""
    for i in range(attempts):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (PermissionError, ValueError):
            if i == attempts - 1:
                raise
            time.sleep(pause)


def save(path, data):
    """Atomic write: temp file + os.replace, the replace retried while another
    process holds the file open (Windows). The temp file never outlives a failure."""
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        _replace(tmp, path, attempts=REPLACE_ATTEMPTS, pause=RETRY_PAUSE)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def with_lock(path, fn):
    with locked(f"{path}.lock"):
        data = load(path)
        result = fn(data)
        save(path, data)
        return result


# ---- v5.4: the second-pass queue goes through the same lock (the pass-2
# spec had workers hand-rewriting second_pass_queue.json as their "lock").
def _pass2_load(path):
    """The second-pass queue; empty only when the file does not exist yet.
    Any other failure (after load's retries) stops the command: an empty
    fallback would be saved over every recorded review."""
    try:
        return load(path)
    except FileNotFoundError:
        return {"entries": {}}
    except (OSError, ValueError) as e:
        print(f"queue.py: cannot read {path} ({type(e).__name__}: {e}); nothing was changed — "
              "restore the file (git) and run the command again", file=sys.stderr)
        sys.exit(1)


def _pass2_path(queue_path):
    """The second-pass queue beside the primary one (by default
    <base>/_system/second_pass_queue.json), so --file moves both together."""
    return os.path.join(os.path.dirname(os.path.abspath(queue_path)), "second_pass_queue.json")


def _load_queue(path):
    """queue.json for the pass-2 commands: a plain exit 1 when it is missing."""
    try:
        return load(path)
    except FileNotFoundError:
        print(f"queue.py: no queue file at {path} (build_universe.py builds it)", file=sys.stderr)
        sys.exit(1)


def _queue_entry(q, ticker):
    for e in (q or {}).get("queue") or []:
        if e.get("ticker") == ticker:
            return e
    return None


def score_generation(q, ticker):
    """The scoring generation pass 2 reviews (see the module docstring): the
    done entry's claimed_at, else "completed <date>"; "unqueued" for a name
    outside the queue (APP); None while the name is not done (refreshed and
    awaiting its re-score, being re-scored, or blocked) — nothing to review."""
    e = _queue_entry(q, ticker)
    if e is None:
        return "unqueued"
    if e.get("status") != "done":
        return None
    if e.get("claimed_at"):
        return e["claimed_at"]
    return f"completed {e['completed']}" if e.get("completed") else "done"


def _stamped(gen):
    """Whether gen is a pass-1 claim stamp (an ISO timestamp), the only
    generation that proves a scoring run; "completed <date>", "done" and
    "unqueued" carry no such evidence."""
    try:
        datetime.datetime.fromisoformat(gen)
        return True
    except (TypeError, ValueError):
        return False


def _later(a, b):
    """a > b for two ISO timestamps; False when either is missing or unparseable."""
    try:
        return datetime.datetime.fromisoformat(a) > datetime.datetime.fromisoformat(b)
    except (TypeError, ValueError):  # missing, a "completed <date>" token, or naive vs aware
        return False


def _lease_live(ent):
    claimed = ent.get("claimed_at")
    if not claimed:
        return False  # pre-lease entries carry no claimed_at: always stale
    try:
        return datetime.datetime.fromisoformat(claimed) >= now_et() - datetime.timedelta(minutes=LEASE_MINUTES)
    except (TypeError, ValueError):
        return False


def _pass2_eligible(ent, gen, qe):
    """Whether a second-pass entry is claimable for the current generation gen."""
    if gen is None:
        return False
    st = ent.get("status")
    if st == "in_progress":
        # Codex review of PR #2: a worker that died after claiming left
        # the ticker in_progress forever — the primary queue's lease
        # reaper never ran here. An expired lease (or a pre-lease entry
        # with no claimed_at) is reclaimable, same 90-minute rule. A live
        # lease is never re-issued early, even for a newer generation: the
        # holder's pass2-done is refused instead.
        return not _lease_live(ent)
    if st in (None, "pending"):
        return True
    if "generation" in ent:
        # Reviewed an older scoring run. Only a claim stamp proves a new one:
        # an entry that lost its stamp in a universe rebuild is not a re-score.
        return _stamped(gen) and ent["generation"] != gen
    # Done before generations were recorded: it counts for the current
    # generation unless the score was completed on the review date or later
    # (a date cannot order a review and a re-score on the same day).
    done_on = (qe or {}).get("completed")
    return bool(done_on and ent.get("date") and done_on >= ent["date"])


PENDING, RESCORED = "pending", "rescored"  # the two refusal cases, (a) and (b) in the module docstring
_NOT_DONE = {"pending": "refreshed for a newer filing; its re-score has not started",
             "in_progress": "being re-scored"}


def _pass2_superseded(ticker, ent, gen, qe):
    """(case, why) when pass2-check / pass2-done must refuse this claim, else
    None. PENDING: the name is not done in queue.json, so the re-score it
    awaits (or is getting) rewrites judgment.json, dcf_numbers.json and
    score.json. RESCORED: a newer generation is already scored."""
    if gen is None:
        st = (qe or {}).get("status", "absent")
        detail = _NOT_DONE.get(st, "its re-score is blocked until it is requeued")
        return PENDING, (f"{ticker} is {st} in queue.json ({detail}), so the score this review "
                         "read is superseded")
    if "generation" in ent:
        if _stamped(gen) and ent["generation"] != gen:
            return RESCORED, (f"{ticker} was re-scored after this claim (claimed generation "
                              f"{ent['generation']}, current {gen}), so this review is of a superseded score")
        return None
    if ent.get("status") == "in_progress" and _later(gen, ent.get("claimed_at")):
        return RESCORED, (f"{ticker} was re-scored after this claim (score generation {gen} is later "
                          f"than the claim at {ent.get('claimed_at')}), so this review is of a superseded score")
    return None


# What is true after each refusal and what the worker does (SECOND_PASS.md steps 5 and 7).
_WRITE_NOTHING = ("Write nothing for this review (no second_pass.md, analysis.md addendum, judgment.json "
                  "or ttm.json; no engine, make_score.py or reprice.py run), report nothing and finish: ")
_CHECK_REFUSED = {
    PENDING: _WRITE_NOTHING + ("the re-score this name awaits rewrites judgment.json, dcf_numbers.json "
                               "and score.json, and the new score gets its own second pass."),
    RESCORED: _WRITE_NOTHING + ("judgment.json, dcf_numbers.json and score.json are the newer "
                                "generation's, and it gets its own second pass once this claim's lease expires."),
}
_DONE_REFUSED = {
    PENDING: ("Nothing was recorded in the second-pass queue. Delete the second_pass.md and any analysis.md "
              "'## Second pass' addendum you wrote in this run and leave the rest: the re-score this name awaits rewrites judgment.json, "
              "dcf_numbers.json and score.json, and your second_pass object goes with them. Report nothing; "
              "the claim is re-issued against the new score once the re-score is done and this claim's "
              "lease expires."),
    RESCORED: ("Nothing was recorded in the second-pass queue. The newer generation is already scored, so "
               "nothing will rewrite what this run wrote: delete the second_pass.md and any analysis.md "
               "'## Second pass' addendum you wrote in this run, and leave judgment.json and score.json as the newer generation left them. Report nothing; "
               "the claim is re-issued against the new score once this claim's lease expires."),
}


def cmd_pass2_claim(path, queue_path):
    """First candidate in queue order whose folder has a score.json and whose
    second-pass entry is absent, pending, recorded against an older scoring
    generation, or an expired claim; marks it in_progress under the lock and
    records the generation it is reviewing."""
    with locked(f"{path}.lock"):
        data = _pass2_load(path)
        entries = data.setdefault("entries", {})
        q = _load_queue(queue_path)
        cands = [e["ticker"] for e in q["queue"] if e.get("status") == "done"]
        if "APP" not in cands:
            cands.append("APP")  # the pilot sits outside the queue
        for t in cands:
            if not os.path.exists(f"{BASE}/{t}/score.json"):
                continue
            gen = score_generation(q, t)
            if _pass2_eligible(entries.get(t) or {}, gen, _queue_entry(q, t)):
                entries[t] = {"status": "in_progress", "date": now_et().date().isoformat(),
                              "claimed_at": now_et().isoformat(timespec="seconds"),
                              "generation": gen}
                save(path, data)
                print(t)
                return
    print("queue.py: no pending second-pass candidates", file=sys.stderr)
    sys.exit(1)


def cmd_pass2_done(path, ticker, status, queue_path=None):
    if status not in ("done_no_change", "done_changed", "pending"):
        print("queue.py: pass2-done status must be done_no_change | done_changed | pending", file=sys.stderr)
        sys.exit(2)
    if status != "pending":
        # v5.7 (R3; 07 §1.17): pass 2 appends to analysis.md, so the same quote gate, before the lock
        why = _quote_gate(ticker)
        if why:
            print(f"queue.py: pass2-done REFUSED — {ticker}: {why}", file=sys.stderr)
            sys.exit(1)
    with locked(f"{path}.lock"):
        data = _pass2_load(path)
        entries = data.setdefault("entries", {})
        if status == "pending":  # pass2-reset: the manual escape hatch, unchecked
            entries[ticker] = {"status": status, "date": now_et().date().isoformat()}
        else:
            q = _load_queue(queue_path or DEFAULT_FILE)
            gen = score_generation(q, ticker)
            ent = entries.get(ticker) or {}
            refused = _pass2_superseded(ticker, ent, gen, _queue_entry(q, ticker))
            if refused:
                case, why = refused
                print(f"queue.py: pass2-done REFUSED — {why}. {_DONE_REFUSED[case]}", file=sys.stderr)
                sys.exit(1)
            # A stamp lost in a universe rebuild keeps the generation the claim recorded.
            rec = gen if _stamped(gen) else ent.get("generation", gen)
            entries[ticker] = {"status": status, "date": now_et().date().isoformat(), "generation": rec}
        save(path, data)
    print(f"{ticker} {status}")


def cmd_pass2_check(path, ticker, queue_path):
    """pass2-done's supersession test with nothing recorded: the worker runs
    it before it writes anything for the review (SECOND_PASS.md step 5)."""
    with locked(f"{path}.lock"):
        ent = (_pass2_load(path).get("entries") or {}).get(ticker) or {}
        q = _load_queue(queue_path)
        gen = score_generation(q, ticker)
        refused = _pass2_superseded(ticker, ent, gen, _queue_entry(q, ticker))
    if refused:
        case, why = refused
        print(f"queue.py: pass2-check REFUSED — {why}. {_CHECK_REFUSED[case]}", file=sys.stderr)
        sys.exit(1)
    print(f"{ticker} claim current (generation {gen})")


def _pass2_reset_for_refresh(path, ticker, reason):
    """refresh: a done second-pass entry goes back to pending — the re-score
    it is about to get is a new generation. In-progress and pending entries
    are left alone (pass2-done refuses a superseded claim). Returns the prior
    status when it reset one, else None."""
    with locked(f"{path}.lock"):
        data = _pass2_load(path)
        entries = data.setdefault("entries", {})
        ent = entries.get(ticker) or {}
        if ent.get("status") not in ("done_no_change", "done_changed"):
            return None
        entries[ticker] = {"status": "pending", "date": now_et().date().isoformat(),
                           "reset_by": "refresh", "refresh_reason": reason,
                           "last_status": ent.get("status"), "last_date": ent.get("date")}
        save(path, data)
        return ent.get("status")


def find(data, ticker):
    for e in data["queue"]:
        if e["ticker"] == ticker:
            return e
    return None


def _reap_locked(data):
    """Expired leases -> pending. Caller holds the lock. Returns reaped tickers."""
    cutoff = now_et() - datetime.timedelta(minutes=LEASE_MINUTES)
    reaped = []
    for e in data["queue"]:
        if e["status"] != "in_progress":
            continue
        claimed = e.get("claimed_at")
        stale = True  # pre-lease entries carry no claimed_at: always stale
        if claimed:
            try:
                stale = datetime.datetime.fromisoformat(claimed) < cutoff
            except ValueError:
                stale = True
        if stale:
            e["status"] = "pending"
            e.pop("claimed_at", None)
            reaped.append(e["ticker"])
    return reaped


def cmd_claim(path):
    def fn(data):
        _reap_locked(data)  # a crashed claim must not hold its ticker forever
        for e in data["queue"]:
            if e["status"] == "pending":
                e["status"] = "in_progress"
                e["claimed_at"] = now_et().isoformat(timespec="seconds")
                return e["ticker"]
        return None
    ticker = with_lock(path, fn)
    if ticker is None:
        print("queue.py: no pending entries", file=sys.stderr)
        sys.exit(1)
    print(ticker)


def _quote_gate(ticker):
    """None when done / pass2-done may proceed, else the refusal text. Engine 5.7 (R3, Andrew 2026-10-19; design 02
    §9, 07 §1.17): a run whose analysis.md quotes a number no generated file holds, or whose key_numbers.md /
    facts.json / saved runs changed after make_score, is not done (check_quotes.py's report). Folders without engine
    output (blocked names, test fixtures) and runs from an engine release before 5.7 pass — they predate the rule."""
    folder = f"{BASE}/{ticker}"
    try:
        with open(f"{folder}/dcf_numbers.json", encoding="utf-8") as f:
            n = json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        return f"dcf_numbers.json unreadable ({e})"
    if not _quotes.gated(n):
        return None
    rep = _quotes.check_folder(folder)
    return None if rep["status"] == "pass" else _quotes.refusal_text(rep)


def cmd_done(path, ticker):
    # v5.7 (R3): the quote gate first, before the queue lock — a refusal records nothing and never holds the lock
    why = _quote_gate(ticker)
    if why:
        print(f"queue.py: done REFUSED — {ticker}: {why}", file=sys.stderr)
        sys.exit(1)

    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        e["status"] = "done"
        e["completed"] = now_et().date().isoformat()
        # claimed_at stays: it identifies this scoring generation for pass 2.
        return ticker
    with_lock(path, fn)
    print(f"{ticker} done")


def cmd_block(path, ticker, reason):
    # DATA_GAP blocks await a judgment decision (an override or a system fix);
    # NO_DATA blocks await filings that do not exist yet. Two lists, two statuses.
    status = "blocked_data_gap" if (reason or "").lstrip().upper().startswith("DATA_GAP") else "blocked_no_data"

    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        e["status"] = status
        e["blocked_date"] = now_et().date().isoformat()
        if reason:
            e["note"] = f"{e['note']} | {reason}" if e.get("note") else reason
        return ticker
    with_lock(path, fn)
    print(f"{ticker} blocked ({status})")


def cmd_requeue(path, ticker):
    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        if e["status"] not in ("blocked_no_data", "blocked_data_gap", "in_progress"):
            print(f"queue.py: {ticker} is {e['status']} — only blocked or in-progress entries requeue", file=sys.stderr)
            sys.exit(1)
        e["status"] = "pending"
        e.pop("claimed_at", None)
        return ticker
    with_lock(path, fn)
    print(f"{ticker} requeued (pending)")


def cmd_refresh(path, ticker, reason):
    """v5.4: a DONE name goes back to pending because a newer filing exists
    (the filing watcher's job — audit round-1 P1 "freshness moves out of pass
    2"). The reason is kept on the entry so the worker sees why it is scoring
    the name again; the previous completion date is preserved as last_done."""
    def fn(data):
        e = find(data, ticker)
        if e is None:
            print(f"queue.py: {ticker} not in queue", file=sys.stderr)
            sys.exit(1)
        if e["status"] != "done":
            print(f"queue.py: {ticker} is {e['status']} — only done entries refresh (use requeue for blocked ones)", file=sys.stderr)
            sys.exit(1)
        e["status"] = "pending"
        e["last_done"] = e.get("completed")
        e["refresh_reason"] = reason or "newer filing"
        e["refresh_date"] = now_et().date().isoformat()
        e.pop("claimed_at", None)
        return ticker
    with_lock(path, fn)
    print(f"{ticker} refreshed (pending): {reason}")
    # Codex review of PR #2: the re-score is a new generation — reopen pass 2.
    prior = _pass2_reset_for_refresh(_pass2_path(path), ticker, reason or "newer filing")
    if prior:
        print(f"{ticker} second pass: {prior} -> pending")


def cmd_migrate_data_gap(path):
    """One-off (round-2): entries blocked before the blocked_data_gap status
    existed, whose note carries a DATA_GAP reason, move to the new status."""
    def fn(data):
        moved = []
        for e in data["queue"]:
            if e["status"] == "blocked_no_data" and (e.get("note") or "").lstrip().upper().startswith("DATA_GAP"):
                e["status"] = "blocked_data_gap"
                moved.append(e["ticker"])
        return moved
    for t in with_lock(path, fn):
        print(t)


def cmd_reap(path):
    for t in with_lock(path, _reap_locked):
        print(t)


def main():
    args = sys.argv[1:]
    path = DEFAULT_FILE
    if "--file" in args:
        i = args.index("--file")
        path = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        sys.exit(2)
    cmd, rest = args[0], args[1:]
    if cmd == "claim":
        cmd_claim(path)
    elif cmd == "done" and len(rest) == 1:
        cmd_done(path, rest[0].upper())
    elif cmd == "block" and len(rest) >= 1:
        if rest[1:] == ["--stdin"]:
            cmd_block(path, rest[0].upper(), sys.stdin.read().strip())
        else:
            cmd_block(path, rest[0].upper(), " ".join(rest[1:]))
    elif cmd == "requeue" and len(rest) == 1:
        cmd_requeue(path, rest[0].upper())
    elif cmd == "migrate-data-gap":
        cmd_migrate_data_gap(path)
    elif cmd == "reap":
        cmd_reap(path)
    elif cmd == "refresh" and len(rest) >= 1:
        if rest[1:] == ["--stdin"]:
            cmd_refresh(path, rest[0].upper(), sys.stdin.read().strip())
        else:
            cmd_refresh(path, rest[0].upper(), " ".join(rest[1:]))
    elif cmd == "pass2-claim":
        cmd_pass2_claim(_pass2_path(path), path)
    elif cmd == "pass2-done" and len(rest) == 2:
        cmd_pass2_done(_pass2_path(path), rest[0].upper(), rest[1], path)
    elif cmd == "pass2-check" and len(rest) == 1:
        cmd_pass2_check(_pass2_path(path), rest[0].upper(), path)
    elif cmd == "pass2-reset" and len(rest) == 1:
        cmd_pass2_done(_pass2_path(path), rest[0].upper(), "pending")
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
