# Buyer: create a new PO (batch entry)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS200MI_AddLine`, `M3_PPS370MI_StartEntry`, `M3_PPS370MI_AddHead`, `M3_PPS370MI_AddLine`, `M3_PPS370MI_FinishEntry`, `M3_PPS115MI_LstAltSupplier`, `M3_PPS200MI_SearchLine`, `M3_PPS001MI_ConfirmLine`, `M3_PPS001MI_FinishMark`, `M3_PPS200MI_DltLine`, `M3_PPS200MI_LstLine2`, `M3_PPS200MI_UpdLine`

<!-- contents:start -->
**Contents**

- What this does
- 1. Read first, ask for what is missing
- 2. Create the batch
- 3. Finish and find the PO
- 4. Read back
- 5. Confirm the new PO (alternate supplier)
- 6. The original line (step D2)
- Show it: Price check
<!-- contents:end -->

## What this does

Use when the buyer wants to buy something that has **no PO and no planned PO yet** ("create a PO to <supplier> for
<item>", "new PO with these two lines"). If a planned PO already exists for it, release it with `planned-pos.md`. If the PO
already exists, add a line with `po-actions.md` ("Add a line to an existing PO"). `M3_PPS200MI_AddLine` is never used to
create a PO. Buying from an alternate supplier for a shortage (option D of `delayed-po.md`) also goes through this file:
see "From an alternate supplier" below. A planned PO (`m3/create-planned-po.md`) is made only when the buyer asks for a proposal.

New POs are created through **purchase order batch entry (PPS370MI)**. The records are collected under one **message
number** (one PO per message number) and become a real PO only when the batch is finished:

| Step | Call | What it does |
|---|---|---|
| 1. Start | `M3_PPS370MI_StartEntry` (`BatchOrigin` = `AUTO`, always) | Returns a **message number**. Creates no PO. |
| 2. Header | `M3_PPS370MI_AddHead` (`MessageNumber`, `SupplierNumber`, `Facility`, `Warehouse`, `RequestedDeliveryDate`) | All five are required. **Returns the PO number** (`PurchaseOrderNumber`). Keep it. |
| 3. Lines | `M3_PPS370MI_AddLine` (`MessageNumber`, `ItemNumber`, `OrderedQuantityAltUom`, **`PurchaseOrderNumber` = the number from `AddHead`**), one call per line | **The PO number from `AddHead` must be passed on every line**, or M3 answers "The purchase order number or header reference must be entered". Returns `PurchaseOrderNumber` and `PurchaseOrderLineNumber`. Do not pass a line number yourself. |
| 4. Finish | `M3_PPS370MI_FinishEntry` (`MessageNumber`) | Starts the processing of the batch into a purchase order. Returns `{}`. The PO appears later. |

**From an alternate supplier (option D of the delayed-PO answer).** Option D has two steps: **D1** creates the new PO
(and offers to confirm it at once), **D2** decides what happens to the original, delayed line (section 6). When the buyer
chooses option D, **create the PO directly**: do not create a planned PO and do not offer to release one. The
answer to "what do I buy from whom" is already in the impact analysis, so fill the plan from it and let the buyer correct it:

- **Supplier:** the alternate supplier the buyer chose, from `m3/alternate-suppliers.md` (a valid agreement). Ask nothing
  about the supplier, and do not mention screening, approval or qualification: with a valid agreement the buyer can create the PO.
- **Item and quantity:** the item of the delayed PO line, and the quantity the buyer chooses: the short quantity that the
  delayed PO would have covered, or less. Show both numbers and ask which; never fill it in alone.
- **Facility and warehouse:** those of the delayed PO line.
- **Requested delivery date:** the arrival date used in option D (today + the warehouse lead time), unless the buyer gives
  another one. Say where it came from. If the arrival is after the need date, say how many days late.
- **Offer to confirm the new PO right away (D1).** In the same message as the quantity question, ask: *"Has the supplier
  already confirmed the date and quantity? If so, tell me the confirmed date (the requested date <date> if they agreed to
  it) and the quantity, and I will confirm the new PO line as soon as the PO exists."* Never fill in the confirmed date or
  quantity, and never assume the supplier has confirmed. If the buyer says no or not yet, the line stays unconfirmed and the
  confirm is offered again when the supplier answers (`po-actions.md`, "Confirm a PO line").
- **The original line is not part of this card.** What happens to the delayed line of the original supplier is step D2
  (section 6), decided after the new PO exists and is read back.

Then follow sections 1 to 4 below (one card, one yes for the batch), section 5 if the buyer asked for the confirm, and
section 6 (D2). After the PO exists, and again after each later write, run "After the action" in `delayed-po.md`.

## 1. Read first, ask for what is missing

Never fill in a value.

1. **Supplier** (number and name), **facility**, **warehouse**, **requested delivery date**, and for each line the **item**
   (number and name) and **quantity**. If the buyer has a PO in the same facility and warehouse for the supplier, offer those
   values, but still ask.
2. **Batch origin:** always `AUTO`. Do not ask the buyer and do not use another value.
3. **Is the supplier valid for the item?** `M3_PPS115MI_LstAltSupplier`: a record with this supplier and `AgreementStatus`
   Valid. If none (the tool may answer "Record does not exist"), say the price has no agreement behind it; the buyer decides.
4. **Does a PO or planned PO already exist** for the same item and supplier (`SearchLine`, `SearchPOP`)? If so, say so and
   ask whether to add to it (existing PO: `po-actions.md`; planned PO: `planned-pos.md`) instead of creating a new one.

**Show the whole plan once and get one yes for the batch:** *"Create a new PO to <supplier name> (<no>), facility <fac>,
warehouse <wh>, requested <date>: line 1 <item no> · <item name> <qty>; line 2 ... Shall I do it?"* A message from the
buyer that names supplier, item, quantity and date and asks you to create it is that confirmation. Run the calls in order.

**Alternate supplier only: add the confirm offer to the card** (see "From an alternate supplier" above): ask for the
supplier's confirmed date and quantity, or "not yet". Do not ask about the original line here: it is step D2 (section 6).
**Before `FinishEntry`, ask again only if** something changed from the plan or a step returned something unexpected.

After a failed step, **stop**: do not start a second batch to "try again" (that could create a second PO). A batch that
stopped half way stays open in M3 with a header and no lines: tell the buyer the message number and that it has to be
cleared in PPS370.

## 2. Create the batch

**Confirm before writing:** the one yes from step 1 covers the batch. Run the calls in order.

1. `StartEntry` with `BatchOrigin` = `AUTO`: keep the message number. If it fails, report the error as it is and stop.
2. `AddHead`: keep the **PO number** it returns. Report any error and stop.
3. `AddLine` for each line, with that PO number. Check that every line returns the **same PO number**; if not, stop before
   `FinishEntry` and tell the buyer. Lines are numbered by M3 (1, 2, ...).

## 3. Finish and find the PO

`FinishEntry`, once. **Then find the PO:** `GetHead` for the PO number from step 2, then `SearchHead`
(`SupplierNumber_ExactSearch`, `Buyer_ExactSearch`) as a second check. The PO is created by a background job: wait about
30 seconds between checks and check **up to 4 times (about 2 minutes)**. As soon as it exists, go to step 4.
**If the PO is still not found, tell the buyer exactly:** *"Something went wrong, please check the Purchase order batch
order entry in M3."* Add the message number and the PO number the batch used, so they can find it. Do not run
`FinishEntry` again, do not start a new batch, and do not guess the reason: there is no tool that reads the batch, its
status or its error messages.

## 4. Read back

**Read back the header:** `GetHead`: supplier, buyer (does it match the signed-in user?), facility, warehouse, currency,
requested date. **Read back each line** with `LstLine2` and `SearchLine` (it lags a little): item, quantity, **price and
line amount in the PO currency**, dates, status. Compare with what was entered and mark differences ⚠️.

## 5. Confirm the new PO (alternate supplier)

Runs only when the buyer gave the supplier's confirmed date and quantity in answer to the offer in "From an alternate
supplier", and only after step 4 shows the PO and its line. Never confirm a line the buyer did not ask to confirm.

1. **Re-read the new line** with `M3_PPS200MI_SearchLine` (`PurchaseOrderNumber_ExactSearch`,
   `PurchaseOrderLineNumber_ExactSearch`): status 15 or 20, nothing received, quantity as on the card. If anything differs,
   stop and ask again.
2. **Confirm it** as in `po-actions.md`, "Confirm a PO line": `M3_PPS001MI_ConfirmLine` with the new PO number, the line
   number returned in step 2, `PurchaseOrderLineSuffix` 0, `ConfirmedDeliveryDate` and `ConfirmedQuantity` exactly as the
   buyer gave them, and `ConfirmedPurchasePrice` only if the supplier gave a price. The buyer's reply names the line (the
   new PO), the date and the quantity, so it is the yes for this write (`m3/write-protocol.md`, step 2). Say before writing
   that the planned date moves with the confirmed date, with the old and the expected new planned date.
3. **Read back** with `SearchLine`: status 35, confirmed date, quantity and price, and the planning date. Compare with what
   the buyer gave and mark differences ⚠️. If M3 sent the PO on creation (status 20), say so; do not offer to print it.
4. Run "After the action" in `delayed-po.md`. The new PO solves the impact as soon as it exists and is read back (section 4), confirmed or not: a confirmed one (status 35) says so, an unconfirmed one gets the line "supplier confirmation still open". M3's action message on the new line (for example DeleteOrder) is not valid while the original line is unadjusted: do not delete the new PO because of it, and do not show the orders as "covered, not firm".

## 6. The original line (step D2)

Runs only after the new PO exists and is read back (step 4), and after the confirm if the buyer asked for it (step 5).
The original line is the delayed line of the original supplier: it keeps supplying the item, on its old date, until the
buyer decides what to do with it. Nothing here is decided for the buyer.

**Offer it straight away, without waiting to be asked**, in the same reply as the impact after the new PO (and its confirm). The new PO takes care of the orders, so adjusting the original line is the next step, and it is what clears M3's action messages: the plan still counts the delayed line on its old date until it is adjusted. Recommend option 1 (reconfirm with the supplier's real date and quantity), and ask for them if the buyer has not given them. Say what option 2 would do: a delete removes the original supply, so compare the warehouse's balance after it with the item's safety stock and say if it falls below. The write itself still needs the buyer's yes on its own card.

**Read the line first** with `M3_PPS200MI_SearchLine` (`PurchaseOrderNumber_ExactSearch`,
`PurchaseOrderLineNumber_ExactSearch`): status, ordered, confirmed and received quantity, confirmed date. If it is not the
line the buyer named, stop and ask.

**Offer two options in one message.** Name the line exactly (<item no> · <item name>, <qty>, <original supplier>) and wait
for the choice. The buyer may also keep the line as it is: then nothing is written and no supplier message is offered.

**Option 1: reconfirm the line with the new date and quantity.** Ask for the new arrival date and the quantity; never fill
them in. Follow `po-actions.md`, "Confirm a PO line" (at status 31 to 35 it is a re-confirmation: show the existing and the
new values side by side) with `M3_PPS001MI_ConfirmLine`. **If the new quantity is less than the original ordered quantity,
ask in the same message whether the rest is still expected:** *"Do you still expect the remaining <rest> pcs on line <n> of
PO <no> from <supplier>?"* In this flow the need is covered elsewhere, so the usual answer is no: send `FinishMark` = 1 in
the same `ConfirmLine` call (`po-actions.md`, section 1, point 3), so the line is not split and the rest is no longer
expected. It is one call and one read back. Without `FinishMark`, M3 splits the line: the rest stays open as a subline
(suffix 1) on the old status and date, and keeps counting as supply in the plan. Do not call `M3_PPS001MI_FinishMark` for
this. A yes to that question names the line, the quantity and the action, and is the yes for the whole confirm; a "yes, I
still expect it" leaves `FinishMark` out and the rest open on suffix 1.

**Option 2: delete the line, or finish mark it.** Which one is possible depends on the status you just read:

- **Status 15 to 20** (ready for printout, printed): the line can be deleted with `M3_PPS200MI_DltLine`.
- **Status 35 or above** (confirmed, on the way, received): the line cannot be deleted. Offer the finish mark instead, and
  say that this is why. It closes the full line, not just a rest (`po-actions.md`, section 5).
- **Other statuses** (below 15, or 21 to 34): this rule does not cover them. Say so, show the line, and let the buyer choose
  delete or finish mark; M3 decides, and its error is reported as it is.
- **Anything received:** never delete. A finish mark closes what remains.

**For a delete**, in this order:

1. **Say who has the order.** At status 20 the original supplier already has the order and the delete does not tell them.
   Below 20 nothing has reached the supplier.
2. **Delete:** `M3_PPS200MI_DltLine` (`PurchaseOrderNumber`, `PurchaseOrderLineNumber` of the original line), once, after the
   buyer's yes on a card that names the PO, the line and the delete. If M3 refuses (the status does not allow it), show the
   error as it is and stop: do not retry, and offer the finish mark.
3. **Read back** with `M3_PPS200MI_LstLine2`: the original line is gone. If it was the only line, say that the original PO
   is now empty and ask whether the buyer wants to do anything with it. Never delete a header.

**For a finish mark**, follow `po-actions.md`, "Finish mark a PO line".

**After you have performed the action** (reconfirm, delete or finish mark), ask: *"Shall I draft a message to <original
supplier> about this?"* Ask it every time, after the action and not before, as one question. On a yes, draft it from
`messages.md` ("To the original supplier after option D2"); it is never sent. Then run "After the action" in
`delayed-po.md`: the original supply has changed and the new PO supplies the orders.

## Show it

- Whether the PO is **not yet sent** (status 15 ReadyForPrintout, or 12 stopped if the order type needs approval or the
  value is below the minimum) or already Printed (20). **Status 20 means the supplier has the order.** Do not say it is sent
  unless the status is 20. Whether M3 sends it on creation is a setting on the order type; if it is already 20, do not
  offer to print it unless the buyer asks for a copy.
- Offer the next steps: print it (`po-actions.md`, "Print a PO"), confirm the lines when the supplier answers, re-run
  `impact-check.md` for the items.
- **The original line (alternate supplier only):** step D2, section 6. Never before the new PO exists and its header and
  lines are read back (step 4).
- Lines added later to the same PO use `M3_PPS200MI_AddLine` with the PO number; the supplier has not seen them if the PO
  was already printed.

### Price check

Tested: the line carried `OurReferenceType` AgreementNo and an agreement number, `PurchasePrice` in the PO currency and
`PurchasePriceLocalCurrency` in the local currency, which matched the agreement price from `LstAltSupplier` (a
local-currency price). So batch entry does use the valid agreement; the two numbers are the same price in two currencies.

**Rule:** compare prices **only in the same currency**. `NetPriceLocalCurrency` from `LstAltSupplier` is in the **local
currency** (`LocalCurrency`), not the PO currency. Read the line with `LstLine2` and check
`OurReferenceType`/`OurReferenceNumber` (the agreement) and `PurchasePriceLocalCurrency`. Show both values with their
currency labels. If the currencies cannot be matched, say that the price cannot be compared and ask the buyer to check it in
M3; never write that a price is wrong, never assume a currency. Offer `M3_PPS200MI_UpdLine` for a price only if the buyer
decides it must change (a second write, confirmed).

Not yet tested: a PO with two lines.
