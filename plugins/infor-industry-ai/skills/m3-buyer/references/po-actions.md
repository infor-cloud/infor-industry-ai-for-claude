# Buyer: actions on PO lines

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS001MI_ConfirmLine`, `M3_PPS200MI_AddLine`, `M3_PPS600MI_PrintPO`, `M3_PPS001MI_FinishMark`, `M3_PPS200MI_DltLine`, `M3_PPS200MI_GetHead`, `M3_PPS200MI_UpdLine`, `M3_PPS115MI_LstAltSupplier`, `M3_PPS200MI_SearchHead`

<!-- contents:start -->
**Contents**

- What this does
- 1. Confirm a PO line (the buyer calls the supplier, or the supplier answers a message)
- 2. Replace the item on a PO line (option B, buyer does it himself)
- 3. Add a line to an existing PO
- 4. Print a PO
- 5. Finish mark a PO line
- 6. Delete a PO line
- Show it
<!-- contents:end -->

## What this does

Writes on existing purchase order lines, always in the same pattern: **read the line, check the conditions, show the
exact action in plain words, write only when the buyer confirms, read back, then say what it changes for the orders.**
Each action below follows that pattern. Planning and decisions (which option, which date) are in `delayed-po.md`;
message drafts are in `messages.md`; releasing planned POs is in `planned-pos.md`.

| Action | Tools | State |
|---|---|---|
| Confirm or re-confirm a PO line (with `FinishMark` = 1 to drop the unconfirmed rest instead of splitting the line) | `M3_PPS001MI_ConfirmLine` | Confirm tested; the `FinishMark` field not tested yet |
| Replace the item on a PO line | `M3_PPS200MI_AddLine`, `DltLine` | Tested |
| Create a new PO (batch entry) | `M3_PPS370MI_*`, see `create-new-po.md` | Tested |
| Add a line to an existing PO | `M3_PPS200MI_AddLine` | Tested |
| Print a PO (sends it to the supplier) | `M3_PPS600MI_PrintPO` | Added, not tested |
| Finish mark a PO line (close a full line or order that is no longer wanted; never for a shortfall) | `M3_PPS001MI_FinishMark` | Added, not tested |
| Delete a PO line the buyer no longer wants (status 15 to 29; send PO number and line number) | `M3_PPS200MI_DltLine` | Used in the replace flow (tested); on its own not tested |
| Advise a shipment | not decided | Not built |
| Receive goods | not decided | Not built |

## 1. Confirm a PO line (the buyer calls the supplier, or the supplier answers a message)

Use when the supplier has agreed a delivery date for a line (by phone, or by reply to a message). The buyer
tells you the result in the chat and you record it in M3 with `M3_PPS001MI_ConfirmLine`.

**Read first** with `SearchLine` (`PurchaseOrderNumber_ExactSearch`, `PurchaseOrderLineNumber_ExactSearch`):
status, ordered quantity, price, requested and planning date, `ReceivedQuantity`, terms. Then check:

1. **Which statuses can be confirmed:** 15 ReadyForPrintout, 20 Printed, 31 DeliveryDateConfirmed, 32
   PurchasePriceConfirmed, 33 PriceAndDeliveryConfirmedNotApproved and 35 PriceAndDeliveryConfirmedApproved. At 31 to
   35 this is a **re-confirmation** (for example the confirmed date changes): show the existing confirmed date,
   quantity and price next to the new ones, and what changes. Other statuses (stopped 11 to 14, 40 and above) are
   not covered by the buyer's rule: do not refuse in advance, but say so, show the line, and let M3 answer;
   report the error as it is and stop. A line at 15 can be confirmed before it is sent; say that the order has
   still not been sent to the supplier.
2. **Prefill from the PO line, ask only for what is not on it:** the confirmed **delivery date** (default: the line's confirmed date if set, otherwise its requested date), the confirmed
   **quantity** (default: the line's confirmed quantity if set, otherwise the ordered quantity), and the confirmed
   **price** only if the supplier gave one. The supplier's date is always the arrival date (the date the goods are in our
   warehouse), whatever the delivery terms: do not ask whether it is a ship, pickup or arrival date. Do not record who the buyer talked to: M3 has no field
   for it; put it in the chat summary. Show the defaults on the card and say where each came from ("requested date on the line"). A date or quantity the buyer gives always replaces the default.
3. **Quantity above the ordered quantity:** M3 accepts it (tested: 310 confirmed against 300 ordered, no
   error, and the line amount stayed on the ordered quantity). Say so, and ask the buyer whether the order quantity should
   change too.
   **Quantity below the ordered quantity: M3 splits the line unless `FinishMark` is sent.** Without it, the confirmed
   quantity stays on the line (its ordered quantity is cut to the confirmed quantity, status 35, the confirmed date, and the
   planning date moves with it) and the rest becomes a new subline (suffix 1) that keeps the old status and the old date and
   still counts as supply in the plan. Before writing, always ask: *"Do you still expect the remaining <rest> pcs from
   <supplier>?"* Always ask it when the original line of an alternate-supplier purchase is reconfirmed with a smaller
   quantity (`create-new-po.md`, section 6).
   - **No, drop them:** send `FinishMark` = 1 in the same `ConfirmLine` call. The line is not split and nothing is left
     open on it. Do not use `M3_PPS001MI_FinishMark` for this (section 5).
   - **Yes, they come later:** leave `FinishMark` out. The line is split on purpose: the confirmed part is on suffix 0 and
     the rest on suffix 1, which is confirmed later with its own `ConfirmLine` call (`PurchaseOrderLineSuffix` = 1) when the
     supplier gives its date (not tested yet). This is how a first partial delivery and a later rest are recorded.
   Say on the card which of the two happens, and what is left open on the line.
4. **Planned date moves with the confirmed date.** M3 recalculates the planning date from the confirmed date plus
   the lead time (tested: the requested date had given a planned date 7 days later, and the confirmed
   date then gave a planned date 7 days after it too). So a confirmed date **later** than the requested date
   makes the supply arrive later in the plan. Say this before writing and show the old and the expected new
   planned date (confirmed date + the same gap as today's planned date minus requested date).
5. **Price:** if the confirmed price differs from the PO price, show the difference per piece and for the line, in
   the PO header currency (`M3_PPS200MI_GetHead`), before writing.

**Write:** if the buyer's own message already names the line, the date, the quantity and (if used) the price and
asks you to confirm it in M3, that is the confirmation of the exact action. Otherwise show the call in plain
words and wait: *"Confirm PO <no> line <line>: delivery date <date>, quantity <qty>, price <price> <currency> (M3
then uses the confirmed values in planning). Shall I do it?"*

`M3_PPS001MI_ConfirmLine` with `PurchaseOrderNumber`, `PurchaseOrderLineNumber`, `PurchaseOrderLineSuffix` (0),
`ConfirmedDeliveryDate`, `ConfirmedQuantity`, only if given `ConfirmedPurchasePrice`, and `FinishMark` = 1 only when the
confirmed quantity is below the ordered quantity and the buyer does not expect the rest (point 3). One call: never confirm
first and finish mark afterwards.

**Read back** with `SearchLine` (wait a moment if it still shows the old values): status
(tested: date, quantity and price together took a Printed line to 35 directly), `ConfirmedDeliveryDate` (the field
only appears once it is set), quantity, price and the new `PlanningDate`. Then re-read the material plan for the
item to see the effect. Report any error from M3 as it is and stop.

**Read the whole PO, not one line number, when the quantity was below the ordered quantity** (`SearchLine` with
`PurchaseOrderNumber_ExactSearch` only): after a split, a read with the line number can show only suffix 0 for a while,
while the plan already lists both. Check that the quantities add up. With `FinishMark` = 1 expect no suffix 1 and an ordered
quantity equal to the confirmed one. Without it expect a suffix 1 with the rest, at its old status and date. If a suffix 1
shows although the buyer said to drop the rest, say so (⚠️) and do not call the rest dropped.

**Then say what it does to the orders:** compare the confirmed date with the need dates already read for this line
(re-run `impact-check.md` if the data is more than a few hours old) and list which orders are still late, by how
many days, and which are now covered. Offer the next step (substitute, messages to the order owners from `messages.md`, earlier delivery
request). Never promise that the supplier will keep the date.

**When the line is the original, delayed line of a mitigation that is already done** (a new PO to an alternate supplier or a material swap, `delayed-po.md` step 5; `create-new-po.md`, section 6): the orders are already solved, so do not list them as late because this line arrives later. Say instead that the plan now counts this line on its real date, re-read the plan once and report which action messages M3 still shows (the DeleteOrder on the new supply and the RescheduleOut on the MO should be gone; if one is still there, say so, and that the plan can lag about a minute).

## 2. Replace the item on a PO line (option B, buyer does it himself)

`M3_PPS200MI_UpdLine` cannot change the item (no item field). The way to swap an item on a PO is to **add a
new line with the substitute and delete the old line**. Apart from deleting the original line after a new PO to an alternate
supplier (`create-new-po.md`), this is the only case where this skill deletes anything. Offer it only when the buyer wants the substitute **bought on this PO**, not when the substitute is
already in stock and only the orders need changing.

**Preconditions (read, then state the result of each; stop if one fails):**

1. **Read the old line** with `SearchLine` (`PurchaseOrderNumber_ExactSearch`,
   `PurchaseOrderLineNumber_ExactSearch`): item, quantity, price, dates, status. Whether it can be deleted is
   decided by M3: `DltLine` returns an error if the status does not allow it. Show that error and stop; do
   not guess in advance.
2. **Status:** best at 20 or below (not confirmed). If the PO has been **sent** (status 20 Printed), the
   supplier already has the old line: the buyer must also tell the supplier. Draft that message. At status
   below 20 or stopped (12) nothing has reached the supplier.
3. **Same supplier:** the PO header has one supplier. Call `M3_PPS115MI_LstAltSupplier` for the substitute and
   look for a record with that supplier and `AgreementStatus` Valid. If there is none, stop and say so: the
   price on the new line would have no agreement behind it. (In a test the first check showed no record for the PO's
   supplier; a check after the add showed a valid agreement. We do not know what changed in between, so always check
   before adding, and check again after.)
4. **Same quantity:** the new line gets the old line's `OrderedQuantityAltUom`. If the sizes differ, say so and
   ask the buyer to confirm the quantity before going on.
5. **The demand side is handled:** orders and MOs still ask for the old item. If their owners have not
   agreed to the substitute (see `messages.md`), warn that the new supply will not serve them.

**Show the buyer the plan in plain words and as calls, then wait for confirmation of each write:**

| Step | Call | After it |
|---|---|---|
| 1. Add the new line | `M3_PPS200MI_AddLine` (`PurchaseOrderNumber`, `ItemNumber` = substitute, `OrderedQuantityAltUom` = old quantity) | The tool returns an empty result even on success. `SearchLine` is updated with a slight delay, so list the lines first: `M3_PPS200MI_LstLine` is the right tool but currently fails with a metadata error (`ConfirmedPurchasePriceLocalCurrency`), so use `LstLine2` (the new line gets the number after the highest, for example 21). Then read it with `SearchLine` using `PurchaseOrderLineNumber_ExactSearch`, and wait a moment and try once more if it is not there yet. Show: line number, item, quantity, **price and line amount against the old line**, dates, status. |
| 2. Delete the old line | `M3_PPS200MI_DltLine` (`PurchaseOrderNumber`, `PurchaseOrderLineNumber` of the old line) | Returns an empty result on success. Read back with `LstLine2`: the old line is gone and the new one remains. Report any error and stop. |
| 3. Optional: copy the old dates to the new line | `M3_PPS200MI_UpdLine` (`RequestedDeliveryDate`, `PlanningDate`) | Read back. Only if the defaults differ from the old line. |

**Always compare the new line's price with the old line's before step 2** and say so when it differs
(tested: 100.00 against 40.00, so the line amount went from 4,000.00 to 10,000.00). The currency of a PO is on
the PO header and is the same on all its lines: read it with `M3_PPS200MI_GetHead` (`PurchaseOrderNumber`, field `Currency`).
If the tool returns a metadata error, take the currency from the agreement with the PO's supplier (`M3_PPS115MI_LstAltSupplier`,
`Currency`; `m3/m3-concepts.md`, "Currency") and say it comes from the agreement; write "currency not available" only if neither gives one. The buyer confirms step 2 with that in front of them.

Do step 1 before step 2 so that nothing is lost if adding fails. Never delete before the new line is
confirmed to exist. After step 2 re-run `impact-check.md` for both items: the old item loses this supply and
the substitute gains it. Report the effect on the orders.

## 3. Add a line to an existing PO

`M3_PPS200MI_AddLine` is only for a PO that already exists; a new PO is created with `create-new-po.md`.

Use when the buyer wants to buy more of an item on a PO that already exists (for example a substitute on the same PO and date as the
original item). The buyer names the item and quantity; **ask which PO if it is not clear**, because the PO's supplier decides the price.

**Read first:** the PO's lines (`SearchLine`), the PO header currency (`M3_PPS200MI_GetHead`), and the supplier agreements for the item
(`M3_PPS115MI_LstAltSupplier`): is there a valid agreement with **this PO's supplier**? If not, say so before writing and show the price
M3 will probably use (an existing line of the same item on that PO shows it). The buyer confirms with that in front of them.

**Write:** `M3_PPS200MI_AddLine` with `PurchaseOrderNumber`, `ItemNumber`, `OrderedQuantityAltUom`.

**Read back** (`LstLine2` for the line number, then `SearchLine` with the line number or the whole PO; it lags a little): line number,
item, quantity, **price and line amount in the PO currency**, requested date, planning date and status. Compare the dates with the line
the new one should match: the new line took the PO's dates (tested: the same requested and planning dates as the
existing line). If a date must differ, `M3_PPS200MI_UpdLine` sets it (a second write, confirm it).

**Say:** a line added to a PO that is already printed shows status 20 at once, but the supplier received the PO **before** this line
existed: the buyer must tell the supplier about the new line (offer a message from `messages.md`), and the line still needs a
confirmation. Never claim the supplier has seen it.

## 4. Print a PO

Use when the buyer wants a purchase order printed and sent to the supplier ("print PO x", "send the unsent lines"). Printing is what
moves a PO from ReadyForPrintout (15) to Printed (20), and **status 20 means the supplier has the order** (whether M3 delivers it by
e-mail, EDI or paper is set on the order type). So printing is an action with an outside effect: treat it like sending a message.

**Read first:** the PO header and lines (`M3_PPS200MI_SearchHead`, `SearchLine`, or `LstLine2`), the currency and total (`M3_PPS200MI_GetHead`).
Then check:

1. **Which PO and which status.** A PO whose lines are at 15 can be printed. Lines that are stopped (11 to 14) cannot: say what must be
   cleared first (remove the stop, complete the account string) and stop. If the lines are already at 20 or higher the PO has been
   printed and the supplier already has it: **do not print it again unless the buyer asks for a copy**. A reprint is a **copy**: it is
   done with `PrintCopies` = 1 (see Write below).
2. **A PO that got new lines after it was printed** (for example a line added after printing): the new line shows status 20 at once,
   but the supplier has not seen it. Say so. Printing again would produce a copy or revision: ask the buyer how they send revisions.
3. **What the supplier will receive:** supplier, lines (item, quantity, price, requested date), total in the PO currency.

**Ask:** "Print PO <no> to <supplier> (<n> lines, <total> <currency>)? It will go to the supplier." A message from the buyer that names the
PO and asks you to print it is the confirmation.

**Write:** `M3_PPS600MI_PrintPO` with `PurchaseOrderNumber`.
- **First print** (lines at 15): `PurchaseOrderNumber` only.
- **Orders at status 20 or higher: always set `PrintCopies` = 1.** The value 1 means a copy of the already printed order is printed; without
  it M3 will not print an order that has been printed. Say that it is a copy.
- `PrintPackingInstruction` and `PrintPreview` are not understood well enough yet: **do not set them** unless the buyer asks, and say what
  you set. Several POs: print them one at a time, each confirmed (a list confirmed by number is enough for the confirmation).

**`PrintPO` returns a `JobNumber`** (tested: a copy with `PrintCopies` = 1 returned a job number): the print runs as a job. **Do not show the job number to the buyer**: it means nothing to them. Say "the print request was accepted". The job queue cannot be read (`M3_MNS320MI_Search` fails), so you cannot confirm that the document was produced or delivered: say so
and never claim the supplier received it. A copy does not change the PO status.

**Read back** with `SearchHead` (the header's lowest and highest line status) and `SearchLine` or `LstLine2`; they lag a little, so wait and try
again. Expect Printed (20). Report the status, and that the supplier has the order if the status is 20. If the status did not change, say so and
do not retry in a loop.

**Then offer** the next step: a message to the supplier with `messages.md` if something needs asking, and the confirm flow (above) when the
supplier answers.

**Not tested yet:** the first print (a PO at status 15). Test it only on a PO the buyer names and confirms, and check the
status after the call, whether `PrintPreview` is needed, and that a copy with `PrintCopies` = 1 works on a PO that is
already printed.

## 5. Finish mark a PO line

Use `M3_PPS001MI_FinishMark` only to **close a full PO line or a full order** that is not wanted any more and can no longer
be deleted (status 35 or above): for example the original line of an alternate-supplier purchase when the buyer drops all of
it (step D2 of option D, `create-new-po.md`, section 6). It sets the completion flag, so M3 treats the line as fully delivered.

**Not for a shortfall.** Do not use it to drop the unconfirmed rest of a line that is reconfirmed with a smaller quantity:
that is `FinishMark` = 1 on the `ConfirmLine` call itself (section 1, point 3). A separate `M3_PPS001MI_FinishMark` call
after a smaller confirmation comes too late (M3 has already split the line), and it closes the whole order, including the
confirmed part.

**Read first** with `SearchLine` (`PurchaseOrderNumber_ExactSearch`, `PurchaseOrderLineNumber_ExactSearch`): status, ordered,
confirmed and received quantity. Then check:

1. **Which line.** The buyer names the PO and line, or it is the original line of step D2. Never finish mark a line the buyer
   did not name.
2. **One line only.** Always send the PO number **and** the line number (`PurchaseOrderNumber`, `PurchaseOrderLineNumber`) with the
   suffix (`PurchaseOrderLineSuffix`, 0 unless the buyer names a subline). With both, M3 finish marks only that line, also when the PO has
   other open lines. Never send the PO number alone: the tool would then close the whole PO. Read back that only this line is finished.
3. **What it means for planning.** The line's (or the order's) whole open quantity is no longer expected. Say how many pcs
   that is, and which orders depended on it (`impact-check.md`).
4. **Who has the order.** At status 20 or higher the supplier has the order and a finish mark does not tell them. M3 sends
   nothing, so after the write you always suggest an e-mail to the supplier about the cancelled line (see "Suggest the
   e-mail to the supplier" below). Say this on the card too: "The supplier is not told by this; I will suggest an e-mail to
   <supplier> afterwards."

**Ask first, and do not write until it is answered Yes:** "Have you confirmed with the supplier that you can close this order?"
This question comes before the confirmation below, on every finish mark, also when the buyer's own message names the PO and
the line. Only an explicit Yes lets you go on. On No, or no answer, write nothing: say the supplier should agree first, offer
to draft a message asking them (`messages.md`), and stop. The answer is not stored in M3: do not claim it is.

**Then ask:** "Finish mark PO <no> line <line> (<item no> · <item name>, <qty> ordered, <qty> confirmed or received)? M3 then
expects nothing more on this line." A yes to that question, or a message from the buyer that names the PO, the line and
the action, is the confirmation.

**Write:** `M3_PPS001MI_FinishMark` with `PurchaseOrderNumber` and `PurchaseOrderLineNumber` (and the suffix). One call.

**Read back** with `SearchLine` and the PO's lines (`LstLine2`): report what M3 shows (status and quantities). The finish flag
may not be visible in these tools: if it is not, say so, and never claim more than M3 shows.

**Then say what it does to the orders** (as at the end of section 1).

**Suggest the e-mail to the supplier (always, right after the read-back).** A finish mark cancels the open quantity in M3 only;
the supplier still believes the line is coming. Once the read-back is shown, end the answer with the suggestion as the
"Next:" line, for example: *"The supplier is not told by a finish mark. Shall I draft an e-mail to <supplier> about the
cancelled line(s) on PO <no>?"* Do not skip it because the line looks small, and do not wait for the buyer to ask. On a yes,
draft message 6 in `messages.md` ("To the supplier about cancelled lines"), one message per supplier, listing every line
finish marked in this conversation for that supplier, then offer it in Outlook as a draft (`messages.md`, "Offer the
message in Outlook"). On a no, drop it and do not ask again for the same line. This skill never sends the e-mail.

**Not tested yet.** Test it only on a PO line the buyer names and confirms: check that a line number is accepted, that only
that line is finished, and what the read-back shows.

## 6. Delete a PO line

Use `M3_PPS200MI_DltLine` when the buyer names a line they no longer want and it is at **status 15 to 29** (ReadyForPrintout up to
before the supplier has confirmed it). From status 31 the line is finish marked instead (section 5).

**Read first** with `SearchLine` (`PurchaseOrderNumber_ExactSearch`, `PurchaseOrderLineNumber_ExactSearch`): status, item, ordered quantity,
suffix. Then check:

1. **Which line.** The buyer names the PO and the line. Never delete a line the buyer did not name.
2. **Status 15 to 29, suffix 0.** Outside that range say so and stop (at 31 or above: finish mark; stopped 11 to 14: clear the stop or ask
   in M3). A subline (suffix above 0) is not deleted from here: the tool cannot name a suffix.
3. **What it means for planning.** The line's quantity is no longer expected. Say how many pcs and which orders depended on it (`impact-check.md`).
4. **Who has the order.** At status 20 the supplier already has the order and a delete does not tell them: offer a drafted message (`messages.md`).
   At 15 the supplier has not received it.

**Ask:** "Delete PO <no> line <line> (<item no> · <item name>, <qty> ordered, status <status>)? It cannot be undone from here." A yes to that
question, or a message from the buyer that names the PO, the line and the action, is the confirmation.

**Write:** `M3_PPS200MI_DltLine` with `PurchaseOrderNumber` **and** `PurchaseOrderLineNumber`. Always send both. One call.

**Read back** with `LstLine2` (or `SearchLine`; it lags a little, so wait and try once more): the line is gone and the other lines remain. If the
line is still listed, say so (⚠️) and do not call it deleted. Then say what it does to the orders (as at the end of section 1).

## Show it

After a write, show the read-back as a small table (field, before, now) with ✅ for what changed as intended and ⚠️ for anything unexpected (for example the planned date moving later). Follow "Answer layout" in `SKILL.md`.
