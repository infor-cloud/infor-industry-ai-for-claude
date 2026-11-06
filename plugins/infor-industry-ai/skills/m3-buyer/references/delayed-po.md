# Buyer: delayed PO resolution (UC3)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_ARS200MI_ServerTimeZone`, `M3_PPS200MI_SearchLine`, `M3_PPS200MI_LstLineTrans`, `M3_PPS200MI_GetHead`, `M3_PPS115MI_LstAltSupplier`, `M3_PMS100MI_Get`, `M3_OIS100MI_GetLine`, `M3_OIS100MI_GetOrderHead`, `M3_CRS610MI_GetBasicData_CustomerName`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS020MI_LstItemRelation`, `M3_PDS013MI_LstAltMat`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_DPS001MI_LstRelation`, `M3_MMS200MI_GetItmWhsBasic`

<!-- layout: reference -->

This file is the index. It holds the rules, the checklist and step 0 (tools and batches). Read it first, then read only the step file you need, when you reach that step. Do not read all of them up front.

## Which file to read, and when

| Step | File | Read it when |
|---|---|---|
| 1. Confirm the delay | `delayed-po/1-confirm-delay.md` | After batch 1 has returned the PO line and header |
| 2. Overall impact | `delayed-po/2-overall-impact.md` (and `impact-check.md`) | After batch 2 has returned the plan |
| 3. Mitigation options: overview and the table of A to E | `delayed-po/3-mitigation-options.md` | Always, before judging the options |
| 3. Option B, substitutes | `delayed-po/3b-substitutes.md` | When the item has related items or alternate material |
| 3. Option C, distribution order | `delayed-po/3c-distribution-order.md` | When another warehouse shows stock |
| 3. Option D, alternate supplier, and stale lines | `delayed-po/3d-alternate-supplier.md` | Always (option D is always checked) |
| 4. Recommendations with actions | `delayed-po/4-recommendations.md` | Before writing the answer |
| Show it, next step | `delayed-po/6-show-it-and-next-step.md` | Before writing the answer |
| 5. After the action: impact solved | `delayed-po/5-after-action-solved.md` | Only after the buyer confirmed a mitigation write and M3 accepted it |

Other files that name sections of the former single file now mean: "Distribution order from another warehouse (option C)" = `delayed-po/3c-distribution-order.md`; "Alternative suppliers (option D)" and "D2" = `delayed-po/3d-alternate-supplier.md`; "Substitutes (option B)" = `delayed-po/3b-substitutes.md`.

## Parallel calls are a rule, not a tip

Each batch in step 0 is **one turn that contains every call of that batch**. Never send the calls of a batch one at a time, and never wait for the result of one call before sending another call of the same batch. A call waits only for a result it needs as an input. The same holds for the per-order reads inside a batch: all customer order headers, all MO reads and all customer name reads of the batch go out together. A run that sends more than about six turns of reads is doing it wrong.

## What this does (use case UC3)

This skill is for supplier delays: lines at status 20 to 49. If the PO line is below 20 or stopped, the
supplier has not been told about the order: say so and ask the buyer to release and send it or fix the
date first, instead of running the mitigation options. If the line is at 50 to 70, it is not a supplier delay (goods
received, waiting for put-away or inspection): name who acts, instead of running the mitigation options.

Input: a PO and line, or an item. If the buyer gives only a supplier or item, list the matching
late lines (`morning-view.md`, search a) and let them pick.

Work through the steps in order. Skip a step only if it clearly does not apply, and say so.

**Check every mitigation option, every time.** Mitigation options A to E (step 3) are all tried with their tools on every run, also when an earlier one already closes the gap and also when the answer looks obvious. Never leave one as "not checked" and never skip one because another is better: the buyer chooses between working options, so the buyer needs to see them all. An option that cannot work still gets its row, with the reason M3 gave (no stock, no relation, no agreement, arrives after the need date).

**An options table is only valid for the state it was read in.** After any write that changes the line, the supply or the dates (a confirmation, a distribution order proposal, a new PO, a swap, a finish mark or a delete), whether it was made in this chat or in the dashboard, the earlier mitigation options table and its recommendations are void. Read the PO line and the plan again (batches 1 to 3; planning data lags about a minute, so read again up to three times until the plan differs from the one before the write) and work out options A to E again before recommending anything. When the buyer says something was done in the dashboard, or the line no longer looks as it did, do the same. Never reuse an arrival date, free quantity or cost difference from before the write.

Dates: lateness uses the confirmed date (or the requested date if none); slack and arrival use the planned date. See "The three dates" in `m3/m3-concepts.md`.

**The supplier's date is the arrival date.** When the buyer gives a date from the supplier (by phone, message or confirmation), always treat it as the date the goods are in our warehouse, whatever the delivery terms. Use it as the arrival date for slack and for every option. Never ask whether it is a ship date or an arrival date, and never offer to draft a message to the supplier to ask that.

**A delay given in days.** When the buyer says the PO "will be delayed by n days" and gives no date, the new arrival date is the confirmed date plus n days (the requested date plus n days if there is no confirmed date), and the planned (projected) date moves by the same n days. Say so in the Basis line ("new arrival = confirmed date + n days"). Nothing is written to M3 for this: it is a what-if until the supplier gives a date.

## Checklist

Work through these in order and confirm each one before you answer. Track them yourself; don't show the checklist in the reply.

- [ ] 0. Read tools loaded in one call, reads sent in the batches of step 0, none held back for an unrelated result
- [ ] Status checked first: 20 to 49 is a supplier delay; below 20, stopped, or 50 to 70 is not (say who acts instead)
- [ ] 1. Delay confirmed: what the PO says, what the supplier says (taken as the arrival date, no question about ship or arrival), the new gap in days
- [ ] 2. Overall impact found with `impact-check.md` and shown in three sections (MO, CO, DO): coverage, orders already past, value and priority, the customer name of every late customer order, and the customer orders possibly affected through each affected MO (`impact-check.md` 6d), every item shown as number and name (the names the plan does not carry are read in batch 3)
- [ ] 3. All five mitigation options A to E tried with their tools (none left as "not checked", none skipped because another one works), each with arrival against need date, cost difference, orders still affected, risk and actions
- [ ] 4. Recommendations with actions: one recommendation and one fallback, each with its actions in a table labelled with the option letter (C, or C1, C2 for its steps), no numeric options, no action panel; actions that would change M3 listed separately
- [ ] Show it: in the chat shape; actions offered, nothing changed without a yes
- [ ] 5. After any confirmed mitigation action that M3 accepted: show before and now for every affected order (MO, CO, DO). A new PO to an alternate supplier that exists, or a material swap that reads back, counts as solved: M3's action messages on the supply are not evidence. Then go straight to adjusting the original PO line (`delayed-po/5-after-action-solved.md`, point 6)

## 0. Load the tools once, then read in batches

Do this first. The reads in steps 1 to 3 wait on each other in only a few places, so they go out as five parallel batches, not as one call after another. Before the first read, load the read tools of this flow with **one** tool search (`select:` and the exact names): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_ARS200MI_ServerTimeZone`, `M3_PPS200MI_SearchLine`, `M3_PPS200MI_LstLineTrans`, `M3_PPS200MI_GetHead`, `M3_PPS115MI_LstAltSupplier`, `M3_PMS100MI_Get`, `M3_OIS100MI_GetLine`, `M3_OIS100MI_GetOrderHead`, `M3_CRS610MI_GetBasicData_CustomerName`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS020MI_LstItemRelation`, `M3_PDS013MI_LstAltMat`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_DPS001MI_LstRelation`, `M3_MMS200MI_GetItmWhsBasic`. These are read tools only, and this overrides the load-by-step line above for this file. Write tools stay unloaded until the buyer picks an action: load them then, for the write card. Load nothing twice.

| Batch | Read together | Needs from before |
|---|---|---|
| 1 | `M3_MNS150MI_GetUserData_CurrentUser`, `M3_ARS200MI_ServerTimeZone`, `M3_PPS200MI_SearchLine` (the PO and line), `M3_PPS200MI_GetHead` (currency, facility) | The PO number from the buyer; with only an item or a supplier, list the late lines first (see "What this does") |
| 2 | `M3_MMS080MI_LstMtPlByItmWhs` (item and warehouse of the line), `M3_MMS200MI_LstItmWhsByItm` (company, item, no warehouse), `M3_PPS115MI_LstAltSupplier` (item and open quantity), `M3_MMS020MI_LstItemRelation` (item) | Item, warehouse and open quantity from batch 1; company from the user |
| 3 | For each affected MO: `M3_PMS100MI_Get` and `M3_PDS013MI_LstAltMat`. For each customer order in the plan: `M3_OIS100MI_GetOrderHead` and `M3_OIS100MI_GetLine`. `M3_DPS001MI_LstRelation` for each other warehouse with free stock. `M3_MMS200MI_LstItmWhsByItm` with `Warehouse` for each substitute. `M3_MMS200MI_GetItmWhsBasic` (item and the warehouse of the PO line) for each item in the plan whose name no result has yet, above all the finished product of each MO (the `ReferenceText` of its plan record) | The plan, the stock and the item relations from batch 2 |
| 4 | `M3_CRS610MI_GetBasicData_CustomerName` for each customer. `M3_MMS080MI_LstMtPlByItmWhs` for each MO's finished product (`impact-check.md`, 6d), and for another warehouse or a substitute only when its stock record shows demand | The order headers and MOs from batch 3 |
| 5 | The order header, line and customer name for each customer order found in batch 4 | The plan of the finished product from batch 4 |

- **Send every call of a batch in the same turn.** A call waits only for a result it needs, never for an unrelated one.
- **The status check can end the flow early.** If batch 1 shows the line below 20, stopped, or at 50 to 70, answer with who acts (see "What this does") and read nothing more.
- **Facility** for `M3_PMS100MI_Get` and `M3_PDS013MI_LstAltMat`: the `Facility` on the item/warehouse record of the MO's warehouse (batch 2), else on the PO header (batch 1).
- **A failed call is reported and the rest of its batch carries on**; only the calls that needed it wait.
- **Skip only what a rule says to skip** (a plan is read only when the stock record shows demand). All five mitigation options are still checked.
- **Don't read again what a batch returned** (shared rule "Read and load once").
- **Item names.** Every item in the answer is shown as `<item number> · <item name>` (`SKILL.md`, "Answer layout"). Some results already carry the name and need no call: `SearchLine` (`PurchaseOrderItemName`), `LstItmWhsByItm` (`ItemName`), `LstAltMat` (`ItemName`). The material plan and the MO and customer order tools return only the number, so batch 3 reads the missing names. Write "name not available" only when that read returned no name, never because it was not made.
