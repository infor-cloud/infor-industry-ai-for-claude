# Which orders: one order set for every view

<!-- layout: reference -->

Shared reference. The dashboard, the text view in chat and a scheduled run must show the same orders. This is the one rule they all follow.
The only setting is **Days back**, the user's own choice: it is not a customer value, and it starts at 90.

## The rule

1. **Whose.** Open customer orders where the responsible user is the signed-in user, or the user the rep picked.
2. **Open.** The order is not Delivered, Invoiced or Deleted (the lowest line status is below Delivered).
3. **How far back.** Compare the **requested delivery date on the order header** with today (the M3 date). The order is in the order set when
   that date is **on or after** today minus **Days back**. An order due today or later is never left out. An order with no requested date is in the set.
4. **Compare the dates yourself.** Read the rep's open orders first, then apply step 3. Do not rely on a date filter in the search: it can
   silently return nothing (`m3/tool-conventions.md`).
5. **Count what was left out** (N), so the answer can say how many.
6. **Cut-off.** Search tools stop at about 30 rows, oldest order number first. A round number of rows (30, 40, ...) means the list may be
   incomplete: say so, and do not call the counts complete.
7. **Say the rule.** Every list or answer carries the look-back line below.

## Days back

Default **90**, a whole number from **1** to **999** (three characters). The cutoff date is today minus Days back, in calendar days, and the
cutoff day itself is included. The dashboard remembers the number per person in its Settings box; in chat the rep can change it for one
answer ("look back 180 days"). Both start at 90.

## The look-back line

- **Dashboard:** `Looking back {D} days: open orders due since {cutoff} and later are shown; {N} older open orders left out. Change this in Settings.`
- **Chat:** `Looking back {D} days: open orders due since {cutoff} and later are shown; {N} older open orders left out. Say "look back 180 days" to change it.`
- Leave out `; {N} older open orders left out` when N is 0. Write "1 older open order" for 1 and "2 older open orders" for 2 or more.

## Worked cases

The dashboard is tested against these rows (a test reads this table). "today -90" means a requested date 90 days before today.

| Case | Requested date | Days back | In the order set |
|---|---|---|---|
| A | today | 90 | yes |
| B | today -30 | 90 | yes |
| C | today -89 | 90 | yes |
| D | today -90 | 90 | yes |
| E | today -91 | 90 | no |
| F | today -200 | 90 | no |
| G | today +40 | 90 | yes |
| H | none | 90 | yes |
| I | today -30 | 30 | yes |
| J | today -31 | 30 | no |
| K | today -999 | 999 | yes |
| L | today -1000 | 999 | no |

Orders that are not open are never in the set, whatever their date:

| Status | In the order set |
|---|---|
| status Allocated | yes |
| status Delivered | no |
| status Invoiced | no |
| status Deleted | no |
