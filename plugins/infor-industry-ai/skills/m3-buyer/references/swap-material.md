# Buyer: swap a material line on an MO for a substitute

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_UpdMatLine`, `M3_PMS100MI_Reschedule`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`, `M3_PMS100MI_SearchMaterial`, `M3_MMS200MI_GetItmBasic`, `M3_MMS020MI_LstItemRelation`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PMS100MI_GetMatLine`

Guided write behind the **Swap** action, two calls on one card: find the MO line -> check the substitute -> one card that asks for the approval -> change the material line -> read it back -> reschedule the MO on its **current start date** (no date change) -> read back and report. **One yes covers both calls; the reschedule needs no separate approval.** The buyer reaches it from a substitute in `delayed-po.md` (mitigation option B). It is the same flow as the production planner's swap (`m3-production-planner`), started from the buyer's answer.

## What this does and doesn't do

- **Does:** replaces the component on **one material line of one MO** with a substitute (`M3_PMS100MI_UpdMatLine`), then reschedules that MO on its current start date, so no date changes, and M3 recalculates it with the new component (`M3_PMS100MI_Reschedule`).
- **Only a related item of replacement type 3 or 5**, with a record in the line's warehouse (step 2). A substitute of any other type, or one that is only alternate material in the bill of material, gets no Swap action: say that engineering or the planner must change the line. Never swap to an item the buyer names that has no such relation.
- **Only with enough free quantity** of the substitute in the line's warehouse, after its own planned demand and above its safety stock (step 2). Otherwise no Swap action, with the reason.
- **Only with approval, and the approval is easy to give.** Engineering or quality approval is not in M3, so the card always reminds the buyer that the swap needs it. The easy option: one short reply that says the approval is in place, such as **approved**, **approved, swap**, **yes, approved** or **ok, it's approved**, confirms the approval and starts the swap in the same step. The buyer never has to type or paste the Confirm line, field values or anything else from the card: the card already holds them. A reply with no approval in it (a bare **yes**, **swap**, **do the swap**) is not approval: ask once, in one short line, whether the approval is in place, and do nothing else until the answer.
- **Nothing but the component changes.** The line keeps its quantity and warehouse. The reschedule sends the MO's current ordered quantity and current start date (M3 refuses a reschedule without a date: "Start or finish date must be entered"). M3 itself may recalculate the times and the finish, and raises the order's priority to high.
- **Only the swap is reported.** Say nothing about lower-level orders, semi-finished components, other material lines of the MO or other MOs, before the swap or after it: not as a note, a warning or an offer to check them. The card and the report cover the swap and its direct result only.
- **One MO and one line at a time.** The same shortage on several MOs gets one Swap action per MO, each with its own card: the first swap uses up the substitute's free quantity, so the next one is checked again from what is left.
- **Purchase orders and planned POs are never changed here.** The delayed PO stays as it is; the buyer decides about it afterwards.
- **From the dashboard.** The dashboard's Swap button opens a confirmation dialog with the same values as the card (`workspace.md`). A bare Confirm is not approval: the dialog has a required Approval field that the buyer has to choose, saying that engineering or quality has approved the substitute and that the quantity is right. Nothing is written without it, and the dialog never fills it in.

## 1. Find the MO line

For each MO the delay affects (`impact-check.md`): `M3_PMS100MI_Get` (facility, MO number, product) for the status, ordered quantity, start date and warehouse, then `M3_PMS100MI_LstMaterials` for the line that holds the original component. Keep the line's **sequence number** (`M3_PMS100MI_UpdMatLine` needs it) and its remaining quantity. If `LstMaterials` doesn't return the sequence number, try `M3_PMS100MI_SearchMaterial` on the MO; if neither does, say so and show no Swap button for that MO.

**Names come from the item master, never "name not available".** The card shows the name of the product (the finished item of the MO), of the original component and of the substitute. Reuse a name already read in this conversation; otherwise read it with `M3_MMS200MI_GetItmBasic` (item number only; the name is the same in every warehouse). Never write "name not available" on this card.

Show no Swap button, and say why in one line, when the MO is completed, the line shows material already issued or reported (M3 would refuse), or the MO's status doesn't let a material line change (M3 validates this strictly: let it decide, and report its error plainly).

## 2. Check the substitute

- **Relation.** `M3_MMS020MI_LstItemRelation` for the original component: the substitute must come back with replacement type 3 or 5 and a start date of today or earlier. Types 3 and 5 are both treated as interchangeable here, as in the production planner's swap; the buyer's approval covers the conditions M3 doesn't return. (`m3/known-inconsistencies.md` says where the buyer and the planner read relation types differently.)
- **Record in the warehouse.** `M3_MMS200MI_LstItmWhsByItm` with the item **and the line's warehouse**. No record: not usable on this line.
- **Free quantity.** As in `delayed-po.md` ("Substitutes", step 3): stock on hand, minus its own planned demand from `M3_MMS080MI_LstMtPlByItmWhs` (an empty plan is no plan data: go by the stock record), minus safety stock. It must cover the line's remaining quantity. Show the arithmetic.
- **Quantity factor.** The swap keeps the line's quantity. If the item names or sizes differ, the quantity the substitute needs is unknown until engineering gives the factor (`delayed-po.md`, "Substitutes", step 2): say so in the card and ask the buyer to confirm the quantity is right before the card. Never convert yourself.

## Confirm before writing

One card for the two calls, shown in chat when the buyer replies with the option letter of the Swap (B, or B2 for the swap step) (`m3/action-buttons.md`). Re-read first (`m3/write-protocol.md`, step 3): the MO is open and unchanged, the line still holds the original, and the substitute's free quantity still covers it. If anything differs, don't show the card: say what changed.

> **Swap material on MO <number>**
> <product number, product name from the item master> - facility <f> - line <seq>
> Component <original, name> -> <substitute, name> (related item, replacement type <3 or 5>). Quantity on the line <q> <unit> (unchanged). Warehouse <wh> (unchanged).
> Why: <the delayed PO and the shortage, one line>. Free quantity of <substitute>: <n> (<on hand> on hand - <planned demand> planned out - <safety stock> safety stock).
> If you reply approved I will do these things in order:
> 1. Change the material line: `M3_PMS100MI_UpdMatLine`, component only.
> 2. Only if M3 shows the change, reschedule the MO with **no date change**: `M3_PMS100MI_Reschedule` on the current start date <date>, quantity <q> as it is now, infinite capacity planning. M3 recalculates the order, may change the times and the finish, and raises the priority to high.
> Approval needed: engineering or quality must approve <substitute> for <product>. M3 does not hold this approval.
> Easy option: reply **approved** if the approval is in place. That one short reply confirms the approval and does the swap. If it is not approved yet, say so and I will hold the swap.
> MO responsible: <name, from the item/warehouse record>. You get a drafted message for them after the swap.
> Not changed: purchase orders and planned POs (including the delayed one), other MOs. I can't undo this from here: going back means another swap or a change in M3.
> If you want something else, say so.

**The card ends there.** Once the buyer has chosen the swap, say nothing about the other mitigation options, in particular not about a distribution order, before or after the card. The same holds the other way round: once the buyer has chosen a distribution order (`delayed-po.md`, option C), the card says nothing about swapping.

Every value on the card is read-only and comes from M3. The buyer replies with a short approval such as **approved** (see "Only with approval" above). Treat that reply as the yes for this card, once, with the values on the card. Never ask the buyer to type or paste field values.

Only after that yes:

1. **Call `M3_PMS100MI_UpdMatLine` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber, SequenceNumber, ComponentNumber: <substitute> }`. Send nothing else (no `ComponentQuantity`): every other field of the line stays as it is. On an error, report it plainly and stop: no reschedule, no retry (M3 validates against the order status, reservations, allocations and the item's warehouse record, and may refuse). Read the line first to see whether it saved.
2. **Read the line back** with `M3_PMS100MI_GetMatLine` `{ Facility, ManufacturingOrderNumber, ProductNumber, SequenceNumber }`. If it still shows the original, wait a moment and read again (up to four reads). **Only when it shows the substitute and the expected quantity**, go on. If it doesn't, say so and stop without the reschedule.
3. **Re-read the MO** (`M3_PMS100MI_Get`) for its current quantity and start date, then **call `M3_PMS100MI_Reschedule` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber, OrderedQuantityAltUom: <the MO's current ordered quantity>, FiniteCapacityPlanning: false, StartDate: <the MO's current start date> }` and **no `PlannedFinishDate`**. The yes on the card covers this call, because the card named it: don't ask again. Never send any date other than the current start date. If M3 refuses it anyway, report M3's message: **the swap still stands**, the MO is not recalculated, and the planner can reschedule in M3 on a date the planner chooses. Don't retry, and don't pick a date.

## 3. Read back and report

1. **The line:** a small table (field, before, now): component, quantity, warehouse. ✅ for what changed as the card said, ⚠️ for anything unexpected.
2. **The MO:** `M3_PMS100MI_Get`: wait while the status reads "...-ChangeInProgress" (up to four reads), then show before and now for start and finish date and time, quantity, priority and status. The dates should be unchanged: if M3 moved either, say so prominently with both values. The times may change and the priority becomes high: report both. The change in the background took about a minute in testing.
3. **The line and the impact:** the read-back above (step 2 of this section) already shows the substitute on the line. A swap that reads back counts as solved (`delayed-po.md`, step 5, "Solved"): the MO is ✅ covered by the substitute and the customer orders behind it are ✅ solved through the MO. Do not use the plan's action messages (RescheduleOut on the MO, DeleteOrder or RescheduleIn on supply) to judge it: they are not valid until the delayed PO is adjusted. If the read-back does not show the substitute, the line is not covered: say so (❌). Then show the impact for every affected order, before and now, as `delayed-po.md` step 5 describes (the same MO, CO and DO tables, with the verdict "Impact solved"). Include the substitute's free quantity left after the swap.
4. **Nothing about lower levels.** Do not mention lower-level orders, semi-finished components or other material lines of the MO, not even as a note or an offer to check them. Don't list orders the swap did not touch.
5. **Customer orders:** covered by the impact tables of step 3 (customer name, before and now). Do not repeat them in a separate list.

### Result line

```
MO <n>, line <seq>: <original> -> <substitute>; qty <q> <unit> (unchanged)
Rescheduled with no date change: start <d> (<unchanged | old -> new>); finish <d> (<unchanged | old -> new>); priority <old> -> high
Material now: <✅ covered by <substitute> (swap done) | ❌ the line does not show the substitute>
```

## Next step

- **Draft a message to the MO responsible** (`messages.md`): the buyer does not change another person's MO without telling them. In chat, not sent.
- **The delayed PO line** is still open and is now surplus for this MO. Offer to adjust it straight away, without waiting to be asked, as its own card (never part of the swap card): name the line, offer to reconfirm it with the supplier's real date and quantity, or to reduce it or finish mark it (`po-actions.md`), and recommend the reconfirm when the supplier has given a date, because adjusting the original is what clears M3's action messages (the plan still counts it on its old date). The buyer decides; ask for the date and quantity if they are not given.
- **More MOs with the same shortage:** the next Swap action, checked again from the substitute's remaining free quantity.

## Edge cases

- **No related item of type 3 or 5** - "No substitute (replacement type 3 or 5) is set up for <original>." Show the other mitigation options; never suggest an item from outside the relations.
- **A relation that hasn't started yet** - list it as "starts <date>"; no button.
- **The substitute has no record in the line's warehouse** - not usable here; say so.
- **M3 refuses the line change** - report its message; nothing was changed; don't try another route or another tool.
- **The line changed but the reschedule failed or was refused** - report both results separately; the swap stands.
- **MO or line changed since the answer was shown** - don't write; re-read and show the answer again.
- **Several lines on one MO short** - one line at a time, each with its own card; the reschedule runs after each swap.
- **Several matches** (MO, line, relation) - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry.
- **A tool is missing** - say which (`M3_PMS100MI_UpdMatLine`, `M3_PMS100MI_Reschedule` or `M3_MMS020MI_LstItemRelation`) and that the swap isn't offered; don't use another write tool.
