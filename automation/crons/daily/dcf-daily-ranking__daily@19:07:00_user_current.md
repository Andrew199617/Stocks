---
id: dcf-daily-ranking
title: Daily DCF ranking HTML
enabled: true
owner: goal:russell-3000-owner-s-earnings-dcf-sweep
mode: task
schedule:
  kind: daily
  timezone: '@user.current'
  time: 19:07:00
timeout_secs: 1800
delivery:
  - chat_id: be9b1806-e747-4d34-97fc-f5080aadead5
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"be9b1806-e747-4d34-97fc-f5080aadead5","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"70fbb853-a274-4b72-9764-c40089a5f6af"}'
  presentation_locale: en-US
---
Send Andrew today's owner's-earnings DCF ranking.

Steps:
1. Run `python3 ~/workspace/stocks/_system/build_daily_html.py` — it aggregates every ~/workspace/stocks/<TICKER>/score.json into ~/workspace/stocks/_daily/ranking-<today>.html and reports sweep progress (done of 2,617).
2. Deliver that HTML file as an attachment in this chat (the dated ranking file, not latest.html), with a short message: sweep progress (X analyzed of 2,617, plus pilot exceptions), the top 10 by implied IRR as a compact list (ticker, tier, implied IRR, price, IV@15%, upside@15%), and call out any NEW Tier S or A names (≥20% implied IRR) that appeared since yesterday's ranking — compare against the previous dated ranking file / score.json analysis_dates if available.
3. If zero companies have been analyzed so far, still send the file with one line saying the sweep has not completed its first company yet. Keep the message short and blunt; the file is the deliverable. Do not create Feed units.
