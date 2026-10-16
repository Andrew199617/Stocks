#!/usr/bin/env python3
"""prices.py intraday tests (2026-10-15; review round the same day). Run:
python3 _system/tests/test_prices.py (or python3 -m pytest _system/tests).
No network, no writes inside the repo: the pure functions in prices.py plus
a throwaway temp dir used as STOCKS_BASE for the file-level (run_one) cases,
with the two fetchers and the clock (now_et) monkeypatched.

1. ms_to_et: a true ms epoch → (ET date, minutes) across both DST boundaries
   of 2026 (spring forward 03-08, fall back 11-01), including a UTC-vs-ET
   date change; ms_as_wallclock reads Nasdaq's x (ET wall-clock encoded as
   UTC) and decode_point picks whichever reading agrees with the label.
2. downsample: right-closed 5-minute buckets keyed by their END minute, last
   price in each bucket wins, time order, no empty buckets; the 959 / 960 /
   961 boundary puts the 16:00 closing print in bar 960 and the first
   after-hours print in 965; 9:30 → 570; 19:59 → 1200.
3. merge_sessions: same-day entry replaced (never duplicated), capped at 5,
   oldest first, malformed entries dropped; a stored entry that reaches a
   later minute (or the same minute with more bars) is KEPT over a shorter
   new capture; legacy entries get `complete` derived from their bars.
3b. merge_sessions orders captures by the RAW last print (entry last_minute)
   before the 5-minute bucket: a stale 08:41 capture arriving after a stored
   08:44 one (both in the 08:45 bar, same bar count) no longer replaces it;
   the same last print falls to complete, then the later captured_at, so a
   late partial capture cannot take back completion; legacy entries without
   last_minute fall back to bucket / bar count; run_one end to end.
4. parse_chart on an inline sample of the real APP payload shape, including
   captured_at / complete / close / bar_key.
5. session_complete: by last print (>= 19:55) or by capture time (>= 20:00 ET
   of the session date, or a later date).
6. reconcile_with_daily: a PRE-MARKET payload (session_date = the day after
   daily[-1]) gets prev_close = daily[-1]'s close with a warning naming
   Nasdaq's stale previousClose; an in-session payload whose daily series
   already has the session row gets prev_close = the row before and close =
   that row; no daily row before the session → Nasdaq's value, with a warning.
7. run_one with fakes: a re-run on the same day leaves one entry per day;
   a chart failure keeps the daily series, writes intraday null, a warning
   and the previous sessions_5d; --no-intraday carries both blocks over;
   the pre-existing keys are unchanged in meaning; the pre-market case end
   to end (APP 2026-10-15 08:40 ET as the reviewers captured it).
"""
import os, sys, json, tempfile, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
sys.path.insert(0, SYS)
import prices as P  # noqa: E402

# Real points from the APP payload of 2026-10-14 (x = ET wall-clock as UTC)
SAMPLE = {"data": {"symbol": "APP", "timeAsOf": "Oct 14, 2026", "lastSalePrice": "$262.19",
                   "previousClose": "$272.28", "volume": "4,348,338",
                   "chart": [
                       {"z": {"dateTime": "4:00 AM ET", "value": "271.8767"}, "x": 1791950400000, "y": 271.8767},
                       {"z": {"dateTime": "4:01 AM ET", "value": "272.90"}, "x": 1791950460000, "y": 272.9},
                       {"z": {"dateTime": "4:02 AM ET", "value": "272.06"}, "x": 1791950520000, "y": 272.06},
                       {"z": {"dateTime": "4:14 AM ET", "value": "272.56"}, "x": 1791951240000, "y": 272.56},
                       {"z": {"dateTime": "9:30 AM ET", "value": "270.10"}, "x": 1791984600000, "y": 270.10},
                       {"z": {"dateTime": "9:34 AM ET", "value": "269.55"}, "x": 1791984840000, "y": 269.55},
                       {"z": {"dateTime": "3:59 PM ET", "value": "262.19"}, "x": 1792007940000 - 4 * 3600000, "y": 262.19},
                       {"z": {"dateTime": "7:59 PM ET", "value": "257.14"}, "x": 1792007940000, "y": 257.14},
                       {"z": {"dateTime": "bogus", "value": "0"}, "x": "nope", "y": None},
                   ]}}
SAMPLE_BARS = [[240, 271.8767], [245, 272.06], [255, 272.56], [570, 270.10], [575, 269.55], [960, 262.19], [1200, 257.14]]

# The pre-market capture the reviewers made: 2026-10-15 08:40 ET, session 10-15, previousClose still the 10-13 close.
X_1015_0400 = 1791950400000 + 24 * 3600000
PREMARKET = {"data": {"symbol": "APP", "timeAsOf": "Oct 15, 2026 8:40 AM ET", "lastSalePrice": "$258.80",
                      "previousClose": "$272.28",
                      "chart": [
                          {"z": {"dateTime": "4:00 AM ET", "value": "260.00"}, "x": X_1015_0400, "y": 260.0},
                          {"z": {"dateTime": "7:12 AM ET", "value": "259.10"}, "x": X_1015_0400 + 192 * 60000, "y": 259.1},
                          {"z": {"dateTime": "8:40 AM ET", "value": "258.80"}, "x": X_1015_0400 + 280 * 60000, "y": 258.8},
                      ]}}


def et(s):
    return datetime.datetime.fromisoformat(s).replace(tzinfo=P.ET)


def test_ms_to_et_across_dst():
    # 2026-03-07 14:30 UTC = 09:30 EST (UTC-5)
    assert P.ms_to_et(1772893800000) == ("2026-03-07", 570), P.ms_to_et(1772893800000)
    # 2026-03-09 13:30 UTC = 09:30 EDT (UTC-4): one hour less offset after spring forward
    assert P.ms_to_et(1773063000000) == ("2026-03-09", 570), P.ms_to_et(1773063000000)
    # 2026-03-08 03:30 UTC = 2026-03-07 22:30 EST: the ET date is the day before
    assert P.ms_to_et(1772940600000) == ("2026-03-07", 1350)
    # fall back 2026-11-01: 2026-10-30 20:00 UTC = 16:00 EDT; 2026-11-02 21:00 UTC = 16:00 EST
    assert P.ms_to_et(1793390400000) == ("2026-10-30", 960)
    assert P.ms_to_et(1793653200000) == ("2026-11-02", 960)
    # Nasdaq's convention: x = ET wall-clock encoded as UTC
    assert P.ms_as_wallclock(1791950400000) == ("2026-10-14", 240)
    assert P.ms_to_et(1791950400000) == ("2026-10-14", 0)  # a true-epoch reading would be 4 h early
    # decode_point: the label decides which reading wins
    assert P.decode_point(SAMPLE["data"]["chart"][0]) == ("2026-10-14", 240, 271.8767)
    true_epoch = {"z": {"dateTime": "9:30 AM ET"}, "x": 1773063000000, "y": 10.0}  # 2026-03-09 13:30 UTC
    assert P.decode_point(true_epoch) == ("2026-03-09", 570, 10.0)
    no_label = {"x": 1791950400000, "y": 1.5}
    assert P.decode_point(no_label) == ("2026-10-14", 240, 1.5)
    assert P.decode_point({"z": {"dateTime": "bogus"}, "x": "nope", "y": None}) is None
    assert P.decode_point({"x": 1791950400000, "y": 0}) is None
    assert P.label_minutes("7:59 PM ET") == 1199 and P.label_minutes("16:00") == 960 and P.label_minutes(None) is None
    assert P.minutes_hhmm(240) == "04:00" and P.minutes_hhmm(1199) == "19:59"


def test_downsample_right_closed_buckets():
    pts = [(240, 1.0), (241, 2.0), (244, 3.0), (245, 4.0), (249, 5.0), (570, 6.0), (574, 7.0), (1199, 8.0)]
    bars = P.downsample(pts)
    assert bars == [[240, 1.0], [245, 4.0], [250, 5.0], [570, 6.0], [575, 7.0], [1200, 8.0]], bars
    keys = [b[0] for b in bars]
    assert keys == sorted(keys) and all(k % 5 == 0 for k in keys)
    assert P.downsample([]) == []
    # the regular close: 15:59 and the 16:00 closing print share bar 960 and the close wins;
    # 16:01-16:04 are the first after-hours bar (965), never overwriting the close
    assert P.downsample([(959, 10.0), (960, 10.5), (961, 9.0), (964, 9.1), (965, 9.2)]) == [[960, 10.5], [965, 9.2]]
    # the open: 9:26-9:29 (pre-market) and the 9:30 opening print share bar 570 and the open wins
    assert P.downsample([(566, 1.0), (569, 1.1), (570, 1.2), (571, 1.3)]) == [[570, 1.2], [575, 1.3]]
    assert P.downsample([(959, 262.19)]) == [[960, 262.19]]
    assert P.downsample([(0, 1.23456)]) == [[0, 1.2346]]  # 4 dp
    assert P.downsample([(236, 1.0)]) == [[240, 1.0]] and P.downsample([(1196, 1.0)]) == [[1200, 1.0]]


def test_session_complete():
    assert P.session_complete(1195, et("2026-10-14T19:56:00"), "2026-10-14")
    assert P.session_complete(1199, None, "2026-10-14")
    assert not P.session_complete(1194, et("2026-10-14T19:55:00"), "2026-10-14")
    assert P.session_complete(1000, et("2026-10-14T20:00:00"), "2026-10-14")      # capture after 20:00 ET
    assert P.session_complete(1000, "2026-10-15T02:07:00-04:00", "2026-10-14")   # next-day capture (ISO string)
    assert P.session_complete(1000, et("2026-10-18T12:00:00"), "2026-10-16")     # weekend capture of Friday
    assert not P.session_complete(1000, et("2026-10-14T19:59:00"), "2026-10-14")
    assert not P.session_complete(520, et("2026-10-15T08:41:00"), "2026-10-15")  # the reviewers' pre-market capture
    assert not P.session_complete(None, "garbage", "2026-10-14") and not P.session_complete(500, None, None)
    # a UTC-stamped capture is converted to ET before the 20:00 test (00:30 UTC = 20:30 EDT)
    assert P.session_complete(1000, datetime.datetime(2026, 10, 15, 0, 30, tzinfo=datetime.timezone.utc), "2026-10-14")


def test_merge_sessions_rolling_and_guard():
    def e(d, n=1, last=240, nbars=1, complete=False, cap="2026-10-15T08:00:00-04:00"):
        bars = [[last - 5 * (nbars - 1 - i), n] for i in range(nbars)]
        return {"session_date": d, "prev_close": n, "close": None, "captured_at": cap, "complete": complete,
                "bar_key": "end", "bars": bars}
    buf = []
    for d in ("2026-10-07", "2026-10-08", "2026-10-09", "2026-10-10", "2026-10-13"):
        buf = P.merge_sessions(buf, e(d))
    assert [s["session_date"] for s in buf] == ["2026-10-07", "2026-10-08", "2026-10-09", "2026-10-10", "2026-10-13"]
    # same day again, further into the session: replaced, not duplicated, newer bars win
    buf2 = P.merge_sessions(buf, e("2026-10-13", 99, last=600))
    assert len(buf2) == 5 and buf2[-1]["prev_close"] == 99 and [s["session_date"] for s in buf2] == [s["session_date"] for s in buf]
    # same day again but SHORTER (an out-of-order / late partial run): the stored entry is kept
    buf2b = P.merge_sessions(buf2, e("2026-10-13", 7, last=520))
    assert buf2b[-1]["prev_close"] == 99 and buf2b[-1]["bars"][-1][0] == 600
    # same last minute, fewer bars: kept; same last minute, same or more bars: replaced (a later capture is a superset)
    full = e("2026-10-13", 5, last=600, nbars=3)
    assert P.merge_sessions(buf2b, full)[-1]["prev_close"] == 5
    assert P.merge_sessions([full], e("2026-10-13", 6, last=600, nbars=2))[-1]["prev_close"] == 5
    assert P.merge_sessions([full], e("2026-10-13", 6, last=600, nbars=3))[-1]["prev_close"] == 6
    # a complete entry is never shortened by a partial one, a longer capture still replaces it
    done = e("2026-10-13", 1, last=1200, nbars=4, complete=True)
    assert P.merge_sessions([done], e("2026-10-13", 2, last=900))[-1] is done
    # a sixth day drops the oldest
    buf3 = P.merge_sessions(buf2, e("2026-10-14"))
    assert [s["session_date"] for s in buf3] == ["2026-10-08", "2026-10-09", "2026-10-10", "2026-10-13", "2026-10-14"]
    # unsorted + malformed input is cleaned and ordered
    messy = [e("2026-10-14"), "junk", {"session_date": None, "bars": []}, {"session_date": "2026-10-09"}, e("2026-10-10")]
    assert [s["session_date"] for s in P.merge_sessions(messy, e("2026-10-13"))] == ["2026-10-10", "2026-10-13", "2026-10-14"]
    assert P.clean_sessions(messy) == [e("2026-10-10"), e("2026-10-14")]
    assert P.merge_sessions(None, e("2026-10-14")) == [e("2026-10-14")]
    # legacy entries (written before `complete` existed) get the flag from their own bars, bars untouched
    legacy = [{"session_date": "2026-10-14", "prev_close": 15.24, "bars": [[240, 15.2], [1195, 15.11]]},
              {"session_date": "2026-10-13", "prev_close": 15.0, "bars": [[240, 15.2], [955, 15.09]]}]
    cl = P.clean_sessions(legacy)
    assert [s["session_date"] for s in cl] == ["2026-10-13", "2026-10-14"]
    assert cl[1]["complete"] is True and cl[0]["complete"] is False and cl[1]["bars"] == [[240, 15.2], [1195, 15.11]]
    assert "bar_key" not in cl[0]  # no retro-labelling: the app treats both keyings as x = key


def _premarket_payload(last_label, last_minute, last_price):
    """PREMARKET with its final point moved to `last_minute` (same date, 3 points)."""
    pts = PREMARKET["data"]["chart"][:2] + [{"z": {"dateTime": last_label, "value": str(last_price)},
                                             "x": X_1015_0400 + (last_minute - 240) * 60000, "y": last_price}]
    return {"data": {**PREMARKET["data"], "chart": pts, "lastSalePrice": f"${last_price}"}}


def test_merge_sessions_raw_last_print_beats_bucket():
    # Finding 4289642911: two captures of 10-15 inside the SAME 5-minute bucket (08:41 and 08:44 both end in bar 525)
    a = P.parse_chart(_premarket_payload("8:41 AM ET", 521, 258.10), captured_at=et("2026-10-15T08:41:20"))
    b = P.parse_chart(_premarket_payload("8:44 AM ET", 524, 258.95), captured_at=et("2026-10-15T08:44:30"))
    ea, eb = P.session_entry(a), P.session_entry(b)
    assert ea["last_minute"] == 521 and eb["last_minute"] == 524
    assert P._last_bar_minute(ea) == P._last_bar_minute(eb) == 525 and len(ea["bars"]) == len(eb["bars"]) == 3  # the old guard tied
    assert ea["bars"][-1] == [525, 258.1] and eb["bars"][-1] == [525, 258.95]
    # out of order: the 08:44 capture is stored, the older 08:41 result arrives late -> stored kept (old code replaced it)
    kept = P.merge_sessions([eb], ea)
    assert len(kept) == 1 and kept[0] is eb and kept[0]["bars"][-1] == [525, 258.95], kept
    # a stale response stamped LATER (a cached copy fetched at 08:46) still loses: the raw print decides before captured_at
    stale = dict(ea, captured_at="2026-10-15T08:46:00-04:00")
    assert P.merge_sessions([eb], stale)[0] is eb
    # in order: the 08:41 capture is stored, the 08:44 one replaces it
    assert P.merge_sessions([ea], eb)[0] is eb
    # a later raw print in a later bucket with FEWER bars still wins (raw minute first)
    c = dict(eb, last_minute=531, bars=[[240, 260.0], [535, 259.0]])
    assert P.merge_sessions([eb], c)[0] is c and P.merge_sessions([c], eb)[0] is c
    # same raw print: the later captured_at wins either way round; a full tie goes to the new entry (a re-run replaces)
    eb2 = dict(eb, captured_at="2026-10-15T08:44:55-04:00", bars=[[240, 260.0], [435, 259.1], [525, 259.0]])
    assert P.merge_sessions([eb2], eb)[0] is eb2 and P.merge_sessions([eb], eb2)[0] is eb2
    twin = dict(eb)
    assert P.merge_sessions([eb], twin)[0] is twin
    # completion is never taken back: last print 19:50 (bar 1190) captured 20:01 is complete by capture time;
    # a 19:58 capture of the same last print arriving late is partial and is not stored over it
    done = dict(eb, last_minute=1190, bars=[[240, 1.0], [1190, 2.0]], captured_at="2026-10-15T20:01:00-04:00", complete=True)
    late = dict(done, captured_at="2026-10-15T19:58:00-04:00", complete=False)
    assert P.merge_sessions([done], late)[0] is done and P.merge_sessions([late], done)[0] is done
    # malformed raw fields are ignored (bucket fallback) instead of crashing or winning
    for junk in (None, "08:44", True, -1, 1440):
        j = dict(eb, last_minute=junk)
        assert P._raw_last_minute(j) is None
        # bucket 525 = 525, bars 3 = 3, both partial -> captured_at decides: j 08:44:30 > ea 08:41:20
        assert P.merge_sessions([j], ea)[0] is j and P.merge_sessions([ea], j)[0] is j


def test_merge_sessions_legacy_entry_without_raw_print():
    # An entry written before last_minute existed (bars + captured_at only, or bars only) is compared by bucket / bar count
    new = P.session_entry(P.parse_chart(_premarket_payload("8:41 AM ET", 521, 258.10), captured_at=et("2026-10-15T08:41:20")))
    assert new["last_minute"] == 521 and P._last_bar_minute(new) == 525 and len(new["bars"]) == 3
    bars3 = [[240, 260.0], [435, 259.1], [525, 258.9]]
    later_bucket = {"session_date": "2026-10-15", "prev_close": 262.19, "bars": bars3[:2] + [[530, 258.7]]}
    assert P.merge_sessions([later_bucket], new)[0] is later_bucket        # 530 > 525: stored kept
    earlier_bucket = {"session_date": "2026-10-15", "prev_close": 262.19, "bars": bars3[:2] + [[520, 258.8]]}
    assert P.merge_sessions([earlier_bucket], new)[0] is new               # 520 < 525: replaced
    more_bars = {"session_date": "2026-10-15", "prev_close": 262.19, "bars": [[240, 260.0], [300, 259.5]] + bars3[1:]}
    assert P.merge_sessions([more_bars], new)[0] is more_bars              # same bucket, 4 bars > 3: stored kept
    # same bucket, same bars, no captured_at on the legacy side: a tie, the new capture replaces it (pre-fix behaviour)
    bare = {"session_date": "2026-10-15", "prev_close": 262.19, "bars": bars3}
    out = P.merge_sessions([bare], new)
    assert out[0] is new and out[0]["last_minute"] == 521
    # same bucket, same bars, legacy captured_at later than the new one: stored kept; earlier: replaced
    stamped = dict(bare, captured_at="2026-10-15T08:44:30-04:00")
    assert P.merge_sessions([stamped], new)[0] is stamped
    assert P.merge_sessions([dict(bare, captured_at="2026-10-15T08:40:00-04:00")], new)[0] is new
    # a legacy complete entry (last bar 1195) is never replaced by a partial capture of the same date
    legacy_done = {"session_date": "2026-10-15", "prev_close": 262.19, "bars": [[240, 260.0], [1195, 258.0]]}
    assert P.merge_sessions([legacy_done], new)[0]["bars"][-1] == [1195, 258.0]
    assert P.merge_sessions([legacy_done], new)[0]["complete"] is True and "last_minute" not in legacy_done


def test_run_one_out_of_order_same_bucket():
    tmp = tempfile.mkdtemp(prefix="prices_test_")
    old_base, old_daily, old_get, old_pause, old_now = P.BASE, P.fetch_daily, P.get_json, P.INTRADAY_PAUSE_S, P.now_et
    try:
        P.BASE, P.INTRADAY_PAUSE_S = tmp, 0
        P.fetch_daily = lambda t, y: [("2026-10-13", 272.28, 1.0), ("2026-10-14", 262.19, 1.0)]
        state = {}
        P.get_json = lambda url, timeout=40: state["payload"]
        P.now_et = lambda: state["now"]
        # 08:44 capture lands first
        state["payload"], state["now"] = _premarket_payload("8:44 AM ET", 524, 258.95), et("2026-10-15T08:44:30")
        first = P.run_one("T", 10, True, True)
        assert first["warnings"][-1].startswith("prev_close:") and first["sessions_5d"][-1]["last_minute"] == 524
        # then a stale 08:41 result (same 08:45 bucket, same 3 bars) is written by a later run
        state["payload"], state["now"] = _premarket_payload("8:41 AM ET", 521, 258.10), et("2026-10-15T08:46:00")
        second = P.run_one("T", 10, True, True)
        s = second["sessions_5d"][-1]
        assert s["last_minute"] == 524 and s["bars"][-1] == [525, 258.95] and s["captured_at"] == "2026-10-15T08:44:30-04:00"
        w = [x for x in second["warnings"] if x.startswith("sessions_5d:")]
        assert w == ["sessions_5d: the stored 2026-10-15 entry (captured 2026-10-15T08:44:30-04:00, last print 08:44) is newer than "
                     "this capture (captured 2026-10-15T08:46:00-04:00, last print 08:41); stored entry kept"], w
        assert json.load(open(f"{tmp}/T/prices.json", encoding="utf-8"))["sessions_5d"][-1]["bars"][-1] == [525, 258.95]
        # a legacy stored entry (no last_minute) in a later bucket: the warning names its last bar
        on_disk = json.load(open(f"{tmp}/T/prices.json", encoding="utf-8"))
        legacy = {k: v for k, v in on_disk["sessions_5d"][-1].items() if k != "last_minute"}
        legacy["bars"] = legacy["bars"][:2] + [[530, 258.7]]
        on_disk["sessions_5d"][-1] = legacy
        with open(f"{tmp}/T/prices.json", "w", encoding="utf-8") as f:
            json.dump(on_disk, f)
        third = P.run_one("T", 10, True, True)
        assert third["sessions_5d"][-1]["bars"][-1] == [530, 258.7] and "last_minute" not in third["sessions_5d"][-1]
        assert any("(captured 2026-10-15T08:44:30-04:00, last bar 08:50) is newer" in x for x in third["warnings"]), third["warnings"]
        # in order: a genuinely later print (08:52) replaces it and no sessions_5d warning is raised
        state["payload"], state["now"] = _premarket_payload("8:52 AM ET", 532, 258.5), et("2026-10-15T08:52:10")
        fourth = P.run_one("T", 10, True, True)
        assert fourth["sessions_5d"][-1]["last_minute"] == 532 and not any(x.startswith("sessions_5d:") for x in fourth["warnings"])
    finally:
        P.BASE, P.fetch_daily, P.get_json, P.INTRADAY_PAUSE_S, P.now_et = old_base, old_daily, old_get, old_pause, old_now
        shutil.rmtree(tmp, ignore_errors=True)


def test_parse_chart_sample():
    intra =P.parse_chart(SAMPLE, captured_at=et("2026-10-15T02:07:00"))
    assert intra["session_date"] == "2026-10-14" and intra["tz"] == "America/New_York"
    assert intra["regular_open"] == "09:30" and intra["regular_close"] == "16:00"
    assert intra["prev_close"] == 272.28 and intra["prev_close_nasdaq"] == 272.28 and intra["prev_close_source"] == "nasdaq"
    assert intra["last_sale"] == 262.19 and intra["close"] == 262.19 and intra["close_source"] == "nasdaq lastSalePrice"
    assert intra["last"] == 257.14 and intra["last_time"] == "19:59" and intra["last_minute"] == 1199
    assert intra["points"] == 8 and intra["source"] == P.INTRADAY_SOURCE and intra["bar_key"] == "end"
    assert intra["captured_at"] == "2026-10-15T02:07:00-04:00" and intra["complete"] is True
    assert intra["bars"] == SAMPLE_BARS, intra["bars"]
    # the pre-market capture: not complete, no close yet (lastSalePrice is the live pre-market print)
    pre = P.parse_chart(PREMARKET, captured_at=et("2026-10-15T08:40:00"))
    assert pre["session_date"] == "2026-10-15" and pre["complete"] is False and pre["close"] is None and pre["close_source"] is None
    assert pre["last"] == 258.8 and pre["last_time"] == "08:40" and pre["last_sale"] == 258.8 and pre["prev_close"] == 272.28
    assert pre["bars"] == [[240, 260.0], [435, 259.1], [520, 258.8]]
    # an in-session capture after 16:00 carries the close from lastSalePrice
    mid = dict(SAMPLE["data"]); mid = {"data": {**mid, "chart": SAMPLE["data"]["chart"][:7]}}  # last point 15:59
    assert P.parse_chart(mid, captured_at=et("2026-10-14T15:59:30"))["close"] is None
    mid["data"]["chart"] = mid["data"]["chart"] + [{"z": {"dateTime": "4:00 PM ET"}, "x": 1791950400000 + 720 * 60000, "y": 262.19}]
    assert P.parse_chart(mid, captured_at=et("2026-10-14T16:00:30"))["close"] == 262.19
    # the clock default: captured_at comes from now_et()
    old = P.now_et
    try:
        P.now_et = lambda: et("2026-10-14T21:00:00")
        auto = P.parse_chart(mid)
        assert auto["captured_at"] == "2026-10-14T21:00:00-04:00" and auto["complete"] is True
    finally:
        P.now_et = old
    for bad in (None, {}, {"data": {"chart": []}}, {"data": {"chart": [{"x": "a"}]}}):
        try:
            P.parse_chart(bad); assert False, "expected ValueError"
        except ValueError:
            pass


def test_reconcile_with_daily():
    daily = [("2026-10-10", 100.0, 1.0), ("2026-10-13", 272.28, 1.0), ("2026-10-14", 262.19, 1.0)]
    # pre-market 10-15: Nasdaq still says the 10-13 close; the file's own 10-14 close is used and the disagreement recorded
    pre = P.parse_chart(PREMARKET, captured_at=et("2026-10-15T08:40:00"))
    w = P.reconcile_with_daily(pre, daily)
    assert pre["prev_close"] == 262.19 and pre["prev_close_source"] == "daily close 2026-10-14" and pre["prev_close_nasdaq"] == 272.28
    assert len(w) == 1 and "272.28" in w[0] and "262.19" in w[0] and "daily used" in w[0], w
    assert pre["close"] is None
    # the 10-14 session with the daily series already carrying 10-14: prev = the 10-13 row, close = the 10-14 row, no warning
    full = P.parse_chart(SAMPLE, captured_at=et("2026-10-15T02:07:00"))
    assert P.reconcile_with_daily(full, daily) == []
    assert full["prev_close"] == 272.28 and full["prev_close_source"] == "daily close 2026-10-13"
    assert full["close"] == 262.19 and full["close_source"] == "daily close"
    # the same session when lastSalePrice and the daily row disagree beyond rounding: daily wins, warning
    full2 = P.parse_chart(SAMPLE, captured_at=et("2026-10-15T02:07:00"))
    w2 = P.reconcile_with_daily(full2, [("2026-10-13", 272.28, 1.0), ("2026-10-14", 262.30, 1.0)])
    assert full2["close"] == 262.3 and len(w2) == 1 and w2[0].startswith("close:")
    # rounding-level differences are silent
    full3 = P.parse_chart(SAMPLE, captured_at=et("2026-10-15T02:07:00"))
    assert P.reconcile_with_daily(full3, [("2026-10-13", 272.284, 1.0), ("2026-10-14", 262.186, 1.0)]) == []
    # no daily row before the session (a name listed today): Nasdaq's value stays, with a warning
    fresh = P.parse_chart(PREMARKET, captured_at=et("2026-10-15T08:40:00"))
    w3 = P.reconcile_with_daily(fresh, [("2026-10-15", 258.0, 1.0)])
    assert fresh["prev_close"] == 272.28 and fresh["prev_close_source"] == "nasdaq" and len(w3) == 1 and "no daily close before" in w3[0]
    assert fresh["close"] == 258.0 and fresh["close_source"] == "daily close"
    # no daily rows at all and no previousClose: prev_close stays None, nothing to warn about
    none_ = P.parse_chart({"data": {"chart": PREMARKET["data"]["chart"]}}, captured_at=et("2026-10-15T08:40:00"))
    assert P.reconcile_with_daily(none_, []) == [] and none_["prev_close"] is None and none_["prev_close_source"] is None
    # the session entry carries what the 5D chart needs
    ent = P.session_entry(full)
    assert ent == {"session_date": "2026-10-14", "prev_close": 272.28, "close": 262.19, "captured_at": "2026-10-15T02:07:00-04:00",
                   "complete": True, "last_minute": 1199, "bar_key": "end", "bars": SAMPLE_BARS}


def test_run_one_rolling_and_failure():
    tmp = tempfile.mkdtemp(prefix="prices_test_")
    old_base, old_daily, old_get, old_pause, old_now = P.BASE, P.fetch_daily, P.get_json, P.INTRADAY_PAUSE_S, P.now_et
    try:
        P.BASE, P.INTRADAY_PAUSE_S = tmp, 0
        daily = [("2026-10-10", 100.0, 1.0), ("2026-10-13", 272.28, 1.0), ("2026-10-14", 262.19, 1.0)]  # the real APP closes
        P.fetch_daily = lambda t, y: list(daily)
        state = {"payload": SAMPLE, "now": et("2026-10-15T02:07:00")}
        P.now_et = lambda: state["now"]

        def fake_get(url, timeout=40):
            assert "chart?assetclass=stocks" in url and "fromdate" not in url, url
            if isinstance(state["payload"], Exception):
                raise state["payload"]
            return state["payload"]
        P.get_json = fake_get
        # seed: four older sessions already on disk (as a previous run would have left them)
        seed = {"ticker": "T", "sessions_5d": [{"session_date": d, "prev_close": 1, "bars": [[240, 1]]}
                                              for d in ("2026-10-07", "2026-10-08", "2026-10-09", "2026-10-13")]}
        os.makedirs(f"{tmp}/T"); json.dump(seed, open(f"{tmp}/T/prices.json", "w"))
        out = P.run_one("T", 10, True, True)
        assert out["intraday"]["session_date"] == "2026-10-14" and out["warnings"] == [], out["warnings"]
        assert out["fetched_at"] == "2026-10-15T02:07:00-04:00" and out["intraday"]["captured_at"] == out["fetched_at"]
        assert [s["session_date"] for s in out["sessions_5d"]] == ["2026-10-07", "2026-10-08", "2026-10-09", "2026-10-13", "2026-10-14"]
        # prev_close / close come from the daily series the file itself carries, not Nasdaq's quote fields
        assert out["intraday"]["prev_close"] == 272.28 and out["intraday"]["prev_close_source"] == "daily close 2026-10-13"
        assert out["intraday"]["close"] == 262.19 and out["intraday"]["close_source"] == "daily close"
        assert out["intraday"]["complete"] is True
        assert out["sessions_5d"][-1] == {"session_date": "2026-10-14", "prev_close": 272.28, "close": 262.19, "captured_at": out["fetched_at"],
                                          "complete": True, "last_minute": 1199, "bar_key": "end", "bars": out["intraday"]["bars"]}
        assert all(s["complete"] is False for s in out["sessions_5d"][:-1])  # legacy seed entries: derived from their bars
        # a stored entry without `close` gets the filed daily close for its date when the series has that row
        by_date = {s["session_date"]: s for s in out["sessions_5d"]}
        assert by_date["2026-10-13"]["close"] == 272.28 and by_date["2026-10-13"]["close_source"] == "daily close"
        assert "close" not in by_date["2026-10-09"]  # no daily row for it: left alone
        # the pre-existing keys are what v5.4 wrote
        assert out["as_of"] == "2026-10-14" and out["rows"] == 3 and out["stats"]["last"] == 262.19 and out["stats"]["prev_close"] == 272.28
        assert out["daily_1y"] == [["2026-10-10", 100.0], ["2026-10-13", 272.28], ["2026-10-14", 262.19]]
        assert set(out) == {"ticker", "source", "currency", "as_of", "fetched_at", "first_date", "rows", "daily_1y",
                            "weekly", "monthly", "stats", "intraday", "sessions_5d", "warnings"}
        # re-run the same day: no duplicate
        state["now"] = et("2026-10-15T02:30:00")
        out2 = P.run_one("T", 10, True, True)
        assert [s["session_date"] for s in out2["sessions_5d"]] == [s["session_date"] for s in out["sessions_5d"]]
        on_disk = json.load(open(f"{tmp}/T/prices.json", encoding="utf-8"))
        assert on_disk["sessions_5d"] == out2["sessions_5d"] and on_disk["intraday"]["bars"] == out2["intraday"]["bars"]
        # the reviewers' pre-market capture, end to end: 10-15 session at 08:40 while the daily series ends at 10-14
        state["payload"], state["now"] = PREMARKET, et("2026-10-15T08:40:00")
        out_pre = P.run_one("T", 10, True, True)
        i = out_pre["intraday"]
        assert i["session_date"] == "2026-10-15" and i["prev_close"] == 262.19 and i["prev_close_nasdaq"] == 272.28  # not the 10-13 close
        assert i["complete"] is False and i["close"] is None and i["last_time"] == "08:40"
        assert len(out_pre["warnings"]) == 1 and out_pre["warnings"][0].startswith("prev_close: Nasdaq previousClose 272.28 differs")
        assert [s["session_date"] for s in out_pre["sessions_5d"]] == ["2026-10-08", "2026-10-09", "2026-10-13", "2026-10-14", "2026-10-15"]
        assert out_pre["sessions_5d"][-1]["prev_close"] == 262.19 and out_pre["sessions_5d"][-1]["complete"] is False
        assert out_pre["sessions_5d"][-2]["complete"] is True and out_pre["sessions_5d"][-2]["close"] == 262.19  # 10-14 untouched
        # an out-of-order shorter capture of the same session never shortens the stored one (warning says so)
        shorter = {"data": {**PREMARKET["data"], "chart": PREMARKET["data"]["chart"][:2]}}
        state["payload"], state["now"] = shorter, et("2026-10-15T08:45:00")
        out_short = P.run_one("T", 10, True, True)
        assert out_short["sessions_5d"][-1]["bars"] == out_pre["sessions_5d"][-1]["bars"]
        assert out_short["sessions_5d"][-1]["captured_at"] == "2026-10-15T08:40:00-04:00"
        assert any(w.startswith("sessions_5d: the stored 2026-10-15 entry") for w in out_short["warnings"]), out_short["warnings"]
        assert out_short["intraday"]["last_time"] == "07:12"  # the intraday block itself is always this capture
        # chart failure: daily kept, intraday null, warning, sessions carried over
        state["payload"] = OSError("boom")
        out3 = P.run_one("T", 10, True, True)
        assert out3["intraday"] is None and out3["stats"]["last"] == 262.19 and out3["daily_1y"] == out["daily_1y"]
        assert len(out3["warnings"]) == 1 and "OSError: boom" in out3["warnings"][0]
        assert out3["sessions_5d"] == out_short["sessions_5d"]
        assert json.load(open(f"{tmp}/T/prices.json", encoding="utf-8"))["intraday"] is None
        # --no-intraday: both blocks carried over from the previous (null-intraday) file, warning says so
        state["payload"] = SAMPLE
        out4 = P.run_one("T", 10, True, True, intraday=False)
        assert out4["intraday"] is None and out4["sessions_5d"] == out3["sessions_5d"] and "--no-intraday" in out4["warnings"][0]
        out5 = P.run_one("T", 10, True, True)             # fetch again, then skip: intraday carried over
        out6 = P.run_one("T", 10, True, True, intraday=False)
        assert out6["intraday"] == out5["intraday"] and out6["sessions_5d"] == out5["sessions_5d"]
        # a fresh folder (no previous file): one session
        out7 = P.run_one("NEW", 10, False, True)
        assert [s["session_date"] for s in out7["sessions_5d"]] == ["2026-10-14"] and not os.path.exists(f"{tmp}/NEW/prices.json")
    finally:
        P.BASE, P.fetch_daily, P.get_json, P.INTRADAY_PAUSE_S, P.now_et = old_base, old_daily, old_get, old_pause, old_now
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                fails += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if fails else 0)
