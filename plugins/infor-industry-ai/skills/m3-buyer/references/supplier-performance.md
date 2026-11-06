# Buyer: supplier performance (scorecard)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS200MI_SearchLine`, `M3_PPS200MI_LstReceiptsByPO`

## What this does

Calculates, per supplier, how reliably goods arrive, from lines that have been received. It is history: current late and
unconfirmed lines are in `morning-view.md`. Say which supplier(s) and which period.

**Which suppliers:** the supplier(s) the buyer names; otherwise the suppliers on the buyer's open PO lines (the morning view
list), at most 5. **Which period:** lines whose promised date was in the last 12 months (default, tell the buyer it can
change; M3 test data is old, so say plainly if there are no lines in the period and offer a longer one).
**Whose orders:** all buyers' lines for that supplier, because it is the supplier's performance; say so.

## 1. Collect

1. Lines: `M3_PPS200MI_SearchLine` with `SupplierNumber_ExactSearch` and `ReceivedQuantity_LargerThan` 0. Fields used:
   `PurchaseOrderNumber`, `PurchaseOrderLineNumber`, `PurchaseOrderLineSuffix`, `OrderedQuantityAltUom`, `ReceivedQuantity`,
   `RequestedDeliveryDate`, `ConfirmedDeliveryDate` (only present when set), `RejectedQuantity`. Date filters can return nothing
   (see `m3/tool-conventions.md`): filter on supplier and received quantity only and select the period yourself.
2. Receipts: `M3_PPS200MI_LstReceiptsByPO` (one call per PO, `PurchaseOrderNumber`). Each record has `PurchaseOrderLineNumber`,
   `PurchaseOrderLineSuffix`, `TransactionDate`, `ReportedQuantity`. **Read at most 20 POs per supplier**, the most recent
   first, and say how many POs were left out.
3. A line is evaluated at the level of PO + line + suffix (a line can be split into sublines with their own receipts).

## 2. Definitions (state them in the answer)

- **Promised date** = `ConfirmedDeliveryDate`, or `RequestedDeliveryDate` if there is no confirmation.
- **Receipt date** = the `TransactionDate` of the last receipt on the line (time ignored).
- **Received quantity** = sum of `ReportedQuantity` on the line and suffix. If it differs from `SearchLine` `ReceivedQuantity`,
  use `SearchLine` and say they differ.
- **On time** = receipt date on or before the promised date. **Early deliveries count as on time**; show the average and the
  number of early lines separately.
- **In full** = received quantity at least the ordered quantity. Tolerances are not read, so a line short by even one piece is
  not in full: say so.
- **OTIF** = on time and in full. **OTIF %** = OTIF lines / evaluated lines.
- **Days vs promise** = receipt date minus promised date (negative = early). Show the average and the median.
- **Date drift** = confirmed date minus requested date, for lines that have both (does the supplier move our dates?).

## Show it

For each supplier: lines evaluated, OTIF %, on time %, in full %, average days vs promise, early lines, date drift, and the
POs read (of how many). **With fewer than 5 lines, show the counts but no percentage** and say the sample is too small.
Add a basis line: period, how lines and receipts were read, the definitions above.

Say what is **not included**: delivery note and shipment dates (the delivery note search is broken), quality (use
`RejectedQuantity` only as a note), cost of delays, and the reason for a late delivery. Do not judge whose fault a late
delivery was.

Show the scorecard as a table per supplier with ✅ / ⚠️ / ❌ next to OTIF (your own thresholds are not set: say that the icon only marks 90% or more ✅, 70 to 89% ⚠️, below 70% ❌ as a default the buyer can change, and show no icon with fewer than 5 lines). Follow "Answer layout" in `SKILL.md`.

## Next step
Then offer the practical next step: for a supplier with low OTIF and open lines, go to `morning-view.md` for what is open
now, or draft a message with `messages.md`.

## Edge cases
If the buyer has no received lines yet, a scorecard for the buyer's own orders is empty: say so and use the supplier's
lines from all buyers.
