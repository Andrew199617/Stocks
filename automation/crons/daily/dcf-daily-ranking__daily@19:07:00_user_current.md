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
1. Run `python3 ~/workspace/stocks/_system/build_daily_html.py` — it aggregates every ~/workspace/stocks/<TICKER>/score.json (plus fundamentals.json / prices.json where present) into ~/workspace/stocks/_daily/ranking-<today>.html (the self-contained ranking with every company page embedded: price-vs-value chart, Overview / Financials / Forecast / Analysis / Data tabs) and one standalone page per company under _daily/companies/, and reports sweep progress (done of 2,617).
2. Deliver the dated ranking file as an attachment in this chat (not latest.html), with a short message: sweep progress (X analyzed of 2,617, plus pilot exceptions), the top 10 by weighted IRR as a compact list (ticker, tier, bear→bull band, weighted IRR, price, IV@15%, upside), and call out any NEW Tier S or A names whose score.json has alert_eligible: true since yesterday's ranking (compare the previous dated file / score.json analysis_dates). Name sector misfits as such — their tiers are soft.
3. If zero companies have been analyzed so far, still send the file with one line saying the sweep has not completed its first company yet. Keep the message short and blunt; the file is the deliverable. Do not create Feed units.
