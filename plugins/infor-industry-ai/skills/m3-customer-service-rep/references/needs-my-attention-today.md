# Customer service rep: what needs my attention today (text view, also called the morning view)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_OIS100MI_SearchHead_LimitedOutput`, `M3_OIS120MI_GetCOStopInfo`, `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get`, `M3_MMS200MI_GetItmWhsBal_Subname`

<!-- contents:start -->
**Contents**

- Two ways to see the same work: What the rep wants
- 1. What to collect
- 2. Ranking
- 3. Suggested action per group
- 4. Show it
<!-- contents:end -->

## Two ways to see the same work

The rep can ask for the day in two forms. They are separate: asking for one never produces the other.

| The rep asks | Form | What you do |
|---|---|---|
| "What needs my attention today", "my morning view", "what is at risk", "which of my orders need me" | **Text view** (this file) | Read from M3 and answer in chat. Build nothing. |
| "Show my dashboard", "open my dashboard", "show me my escalated customer orders in a dashboard" | **Dashboard view** | Open the rep's existing dashboard (`SKILL.md`, "Showing the dashboard"). Run no M3 calls for it. |

- **Text view:** do not open, offer or mention the dashboard on your own. When the rep asks for the text view and also wants the
  dashboard, do the text view and then open the dashboard as a second step.
- **Dashboard view:** do not run the text view first. The dashboard reads M3 itself.
- If the rep says "show my orders" or "list my orders", that is a plain chat table, not the morning view.

### What the rep wants

"Which of my customer orders need a decision today?" A short, ranked list: what is stopped for credit, late, due soon and not
picked, at risk, or backordered; which focus orders are in flight; which customers are owed an update; and which one matters
most. Run the searches below, then merge them into one ranked list. **Read only: the morning view never writes to M3.**

## 1. What to collect

"Mine" is the rep's open customer orders, as defined in `m3/settings.md` (responsible user = the signed-in user; if nothing
comes back, ask which user or customers to cover). Today is the M3 date.

**Which orders: follow `m3/order-set.md`.** It is the one rule shared with the dashboard, so both show the same orders: the rep's open orders, a look-back of 90 days by default ("Days back"), the dates compared by you after you have read the orders, and the look-back line in the answer, in its **Chat** wording. The rep may change the look-back for this answer ("look back 180 days", "only the last 30 days"); the dashboard's own setting is separate. Count the open orders left out, so the answer can say how many.

| # | Group | Tool | How |
|---|---|---|---|
| a | Credit-stopped | `M3_OIS100MI_SearchHead_LimitedOutput`, `M3_OIS120MI_GetCOStopInfo` | Stop code 1 to 8 are credit stops; 0 is no stop and 9 is released by hand. **The stop-code range filter can be ignored by the tool**: search for "not equal to 0" with a date window, then drop 0 and 9 yourself. Read the stop info for the top orders only, to say which limit stopped it. |
| b | Past due | `M3_OIS100MI_SearchLine_LimitedOutput` | Open lines (below delivered) with a confirmed date before today. Date filters can return nothing even when lines exist (`m3/tool-conventions.md`): if so, search on the rep and status and compare the dates yourself. |
| c | Due within 2 days, not picked | `M3_OIS100MI_SearchLine_LimitedOutput` | Allocated lines with a picking-list quantity of 0 and a requested or confirmed date within 2 days. A credit-stopped one is obvious; the others get "remind the warehouse". |
| d | At risk | `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get` | Open lines whose supply date in the material plan, a purchase order or a manufacturing order is later than the requested date. Only for the top lines (see limits). |
| e | Backordered | `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_MMS200MI_GetItmWhsBal_Subname` | Past-due quantity with nothing allocated, valued at the line price times the quantity. Group by item. |
| f | Focus orders in flight | `M3_OIS100MI_SearchLine_LimitedOutput` | The rep's lines on the focus order type (`m3/settings.md`, "Focus order type"; ask if unknown, and leave the group out if the rep has none): the step each one is on (make, buy, transfer, credit). |
| g | Customer updates owed | `M3_OIS100MI_SearchLine_LimitedOutput` | Lines where the confirmed date differs from the requested date. M3 holds no record of what the customer was told: say "update may be owed", never "not sent". |

**Limits.**
- Search tools cut off silently (about 30 rows on some tools). A list that ends on a round number may be incomplete: say so and
  narrow the dates.
- Check supply (group d) for at most the 10 highest-ranked lines. The rest are marked "supply not checked".
- If more than 30 orders come back, rank by the rules below and work with the top 30, and say so.
- Reuse a stock or material-plan result when several lines share the same item and warehouse.
- If the material plan comes back empty for an item that clearly has supply, say the call answered nothing; do not conclude
  there is none.

## 2. Ranking

Rank by what costs the most if nothing is done today:

1. **Lines that miss the requested date within 2 days, the earliest first.** Rank by the dates, not by the order type: the
   order types differ in every M3 set-up.
2. **Credit stops that block a line due within 2 days.** These go to the credit controller.
3. Customer value and order priority, when known.
4. Days late.
5. Backorder value, grouped by item, last: one alert to the buyer covers many orders.

A stale late line that no customer is chasing ranks **below** a line that is only a day late and due to ship now. Say that in the answer.

## 3. Suggested action per group

Use only the actions the skill already has, and only offer one when `fix-a-line.md` says M3 will accept it.

| Group | Suggested action |
|---|---|
| Credit-stopped | Draft the request to the credit controller (`m3/personas-and-handoffs.md`). **Never release it.** |
| Due in 2 days, not picked | Remind the warehouse by e-mail draft (`m3/mail-delivery.md`). A line that is not allocated yet: **Allocate** is a proposal with its own yes (`fix-a-line.md`). A rep never releases a delivery for picking: the warehouse does. |
| Past due / at risk | The ways to fix the line, in order (`fix-a-line.md`): allocate, transfer, alternative item, take stock from another order, alert the buyer or planner, new date. |
| Backordered | Alert the buyer for the item. |
| Update owed | Draft the customer update (`customer-updates.md`). Never state a date M3 has not confirmed. |

Every action is a proposal. Nothing changes in M3 until the rep says yes (`m3/write-protocol.md`).

## 4. Show it

The text view looks like the dashboard's **Needs Action** list, so the rep sees the same thing in chat and on the page: the same
columns in the same order, the same words, the same date icons and the same sort order. Follow "Answer layout" in `SKILL.md`, and
the layout below.

**The answer, in this order**
1. **One line:** the number of escalations and the three counts the dashboard's chips show: need your action, credit hand-overs
   (🔒), no fix available (❌). Add the M3 date and time.
2. **Start with:** the one to three orders that cost the most if nothing is done today, by the ranking in section 2, one short
   sentence each (customer, why, how late). This is where the ranking shows; the table below is sorted like the dashboard.
3. **The table "Needs Action"**, one table, columns as below, sorted by the **earliest confirmed delivery date** first
   (the requested date when nothing is confirmed), then by order number. At most 10 rows; say how many more there are.
   Directly under the table title, **one line with the look-back**, in the **Chat** wording of `m3/order-set.md`. Leave out the part about older open orders when N is 0.
4. **The date legend** directly under the table.
5. **Suggested next step** for the top three orders, one line each, from section 3.
6. **Basis** (how the counts were derived, what was not checked) and **Next:**.

**Columns, exactly as in the dashboard:** Order no · Customer · Item no · Qty · Requested · Confirmed · Order type · Status · Issue.
- **Customer** is the name, never only the number. **Item no** is the first item, then `+N` for the other lines (`ITEM-5 +1`).
  **Qty** is the total over the lines.
- **Requested** and **Confirmed** are dates with an icon in front, by the same rule as the dashboard: ❌ the date is before today
  (already late, or the promise has passed) · ⏰ the date is today · ⚠️ the confirmed date is later than the requested date.
  No icon for any other date. "Not set" when there is no date. Keep the three kinds of date apart (`SKILL.md`, rule 3).
- **Status** is an icon and the dashboard's own word: ⚠️ Shortfall · ⏳ Not picked yet · 🔒 Credit stop (or "Credit stop, manual") ·
  ❌ Shortfall, no path / No lines / Lines not readable. Orders that are on track are not in this table.
- **Issue** is the dashboard's short text, with a small icon for the kind of problem: 🛒 Purchase order late · 🏭 Planned
  manufacturing order late, Manufacturing order late · 🚚 Transfer late · 📦 Was due <date>: not picked, Due today: not picked ·
  🔒 Manual hold: no auto release · ❌ No supply covers the shortfall, Order has no lines. Say it in the dashboard's words; do not
  reword it.

**Legend**, always under the table: `Dates: ❌ already late · ⏰ due today · ⚠️ promised after the requested date.`

An example, with demo values (the values are not settings):

```
Good morning. **6 escalations** need you: ⚠️ 6 need your action · 🔒 0 credit hand-overs · ❌ 0 no fix available. As of 2026-10-28 08:30.

**Start with:** 1000001 Customer A (due 2026-10-22, not picked) and 1000002 Customer B (due 2026-10-27, not picked).

**Needs Action** (earliest confirmed delivery date first)
*Looking back 90 days: open orders due since 2026-07-30 and later are shown; 3 older open orders left out. Say "look back 180 days" to change it.*
| Order no | Customer | Item no | Qty | Requested | Confirmed | Order type | Status | Issue |
|---|---|---|---|---|---|---|---|---|
| 1000001 | Customer A | ITEM-1 | 50 | ❌ 2026-10-22 | ❌ 2026-10-22 | Type A | ⏳ Not picked yet | 📦 Was due 2026-10-22: not picked |
| 1000002 | Customer B | ITEM-2 | 100 | ❌ 2026-10-27 | ❌ 2026-10-27 | Type A | ⏳ Not picked yet | 📦 Was due 2026-10-27: not picked |
| 1000003 | Customer C | ITEM-3 | 60 | ⏰ 2026-10-28 | ⏰ 2026-10-28 | Type A | ⚠️ Shortfall | 🛒 Purchase order late |
| 1000004 | Customer D | ITEM-4 | 15 | ⏰ 2026-10-28 | ⏰ 2026-10-28 | Type A | ⚠️ Shortfall | 🚚 Transfer late |
| 1000005 | Customer C | ITEM-3 +2 | 120 | 2026-10-29 | 2026-10-29 | Type B | ⚠️ Shortfall | 🏭 Planned manufacturing order late |
| 1000006 | Customer E | ITEM-5 +1 | 44 | ⏰ 2026-10-28 | ⚠️ 2026-10-30 | Type A | ⚠️ Shortfall | 🏭 Planned manufacturing order late |
Dates: ❌ already late · ⏰ due today · ⚠️ promised after the requested date.

**Suggested next step**
| Order no | Suggested next step |
|---|---|
| 1000001 | Remind the warehouse to pick and pack, or allocate, then release if stock is free (two confirmations). |
| 1000003 | Alert the buyer: the purchase order is late. Or swap to an alternative item. |
| 1000004 | Create a distribution order proposal from the warehouse that has stock. |

Basis: orders where you are the responsible user, read from M3 on 2026-10-28 08:30, looking back 90 days. Supply checked for the top 10 lines.
Next: which order do you want to work on?
```

Rules for the answer:
- Dates are YYYY-MM-DD. Keep requested, projected and confirmed apart; label each ("projected", never "promised").
- Order values come from the order's own currency. Never mix or convert; write "currency not available" if it cannot be read.
- Say for each item whether anything is short: "covered by stock, no impact" is useful and ranks the line lower.
- Leave out a table that has 0 rows and say "0 <group>" in one line.
- Show at most 10 orders in the table; summarise the rest in one line ("+ N more, the earliest confirmed date is <date>").
- End by asking which order to work on, or go straight to `fix-a-line.md` if the rep names one.
