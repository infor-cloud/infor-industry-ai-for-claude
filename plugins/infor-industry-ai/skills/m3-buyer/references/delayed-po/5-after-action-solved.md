<!-- Part of references/delayed-po.md (UC3). Read only after a mitigation write was accepted. -->

## 5. After the action: show the impact is solved

Run this after **every** mitigation action the buyer confirmed and M3 accepted: a swap, a distribution order proposal, a new PO to an alternate supplier, a confirmed line with a new date, a reschedule, an allocation, a delete or finish mark of the original line. Never after a failed write, and never before the read-back of the write itself. It answers one question: **are the orders from step 2 now covered?**

1. **Re-read the plan.** `M3_MMS080MI_LstMtPlByItmWhs` for the PO line's item and warehouse. Add what the action touched: for a swap, the MO's material lines (`M3_PMS100MI_LstMaterials`) and the substitute's plan; for a distribution order, the receiving warehouse's plan and the sending warehouse's stock and plan; for a planned PO or a new date, the item's plan. Planning data lags (about a minute): if the plan does not show the change yet, read again up to three times. If it still does not, say "M3 has not updated the plan yet (read at <time>)" and do not claim the impact is solved, except after a new PO to an alternate supplier or a swap that reads back: those count as solved without the plan (point 2).
   **M3's action messages are not evidence after a mitigation.** The delayed PO line still carries its old date in M3 until the buyer adjusts it (the delay was given in days, or as a date that is not recorded yet), so the plan keeps counting that supply on the old date. It can then show the new supply (for example the new PO to an alternate supplier) with the action message DeleteOrder, meaning M3 sees it as surplus, and the MO with RescheduleOut. Those messages are not valid in this situation: do not read them as "the new order is not needed", do not lower the verdict because of them, and never show an order as ⚠️ only because of them. Say in one line that M3's messages will clear once the original line is adjusted (point 6), and tell the buyer not to delete the new supply.
2. **Show the same orders as in step 2, same three sections (MO, CO, DO), before and now.** One table per section, columns: Order (a customer order with its customer name) · Need date · Before (slack in days) · Now (slack in days) · Status. Before is the figure you showed in step 2; do not recalculate it. Status, always an icon followed by a word:
   - ✅ **Solved**: covered by stock, or by supply that is firm and arrives on or before the need date (a distribution order proposal at status Released (60) is firm; one at firm status 20 is not). **Two mitigations count as solved as soon as they are done and read back, without waiting for the plan:** a new PO to an alternate supplier that exists and arrives on or before the need date (confirmed or not: an unconfirmed one gets one line "supplier confirmation still open" and the verdict stays solved), and a material swap whose read-back shows the substitute on the MO line. Say which supply and its date. Slack now = need date minus the new supply's date (for a swap: available now).
   - ⚠️ **Covered, not firm**: depends on a planned PO or a distribution order proposal that is not at status Released (60). A real PO to an alternate supplier is not a planned PO: it is ✅ Solved above. Say what must happen and who does it (for example the planner releases the firm proposal in M3).
   - ❌ **Still affected**: short by a quantity, or late by <n> days.
   - ℹ️ **Not checked**: say why.
3. **Customer orders found through an MO** ("possible", step 2): when the MO row is ✅ Solved, the MO keeps its planned finish date, so these customer orders make their need dates: show them ✅ "solved through MO <no>", with their customer name. Do not estimate a new finish date for the MO, and do not re-read the finished product's plan to second-guess it (its action messages, such as RescheduleOut, are not valid here, see point 1). When the MO is not solved, say these orders stay at risk.
4. **Check the action did not create a new problem**, in one line: the substitute's free quantity left after the swap, the sending warehouse still above its safety stock and still covering its own orders, the alternate supplier's order larger than the need. If it did, show it as ⚠️.
5. **The verdict, in one line:** "Impact solved: all <n> orders covered" only when every row is ✅. A new PO to an alternate supplier that exists, or a swap that reads back, gives "Impact solved" (see ✅ Solved above). Otherwise "<n> of <m> orders solved, <k> still affected" or "covered, but not firm", and name the open points. State plainly whether the delayed PO line was changed: if it was not reconfirmed, deleted or finish marked, it is still delayed in M3 and its arrival is now only the fallback; M3's action messages stay until it is adjusted.
6. **What next: adjust the original order, straight away.** All rows ✅: do not offer other mitigation options (`m3/action-buttons.md`, "One chosen action, one card"). Go ahead with the delayed PO line in the same reply, without waiting for the buyer to ask: after a new PO to an alternate supplier that is step D2 (`create-new-po.md`, section 6); after a swap it is the delayed line, which is now surplus for the MO (`swap-material.md`, "Next step"). Name the line, give the options, and recommend reconfirming it with the supplier's real date and quantity, because adjusting the original is what clears M3's action messages. Ask for the date and quantity if the buyer has not given them. The write still needs the buyer's yes on its own card. Also offer the drafted message to the MO responsible or the planner. Any row ⚠️ or ❌: say which orders remain, and then, and only then, offer the next mitigation option that would close them. Work that option out again from the plan and stock you just read (step 3 for that option): the options table from before the action is void, so never reuse its arrival dates, free quantities or cost differences.

Layout:

```
**Impact after <action in words>** (read <time>)

**Manufacturing orders (MO)**
| Order | Need | Before | Now | Status |
...
**Customer orders (CO)**
| Order · customer | Need | Before | Now | Status |
...
**Distribution orders (DO)**
| ... |   (or "No distribution orders affected")

<Verdict, one line>
Open: <what is not firm or still short, who acts>
```
