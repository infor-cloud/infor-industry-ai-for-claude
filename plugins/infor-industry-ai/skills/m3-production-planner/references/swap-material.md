# Swap a material line on an MO for an alternative item

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_UpdMatLine`, `M3_PMS100MI_Reschedule`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`, `M3_PMS100MI_SearchMaterial`, `M3_MMS020MI_LstItemRelation`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_PMS100MI_SearchMO`, `M3_PMS170MI_SearchMOP`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PMS170MI_DelPlannedMO`, `M3_PMS100MI_GetMatLine`

<!-- contents:start -->
**Contents**

- What this does and doesn't do
- 1. When to offer a swap (all four must hold)
- 2. Find the alternative items
- 3. Where the alternative comes from, and is it quicker
- 4. Offer it (advice only)
- Confirm before writing
- 5. Read back and report: Result line
- Next step
- Edge cases
<!-- contents:end -->

Guided write, two calls on one card: identify the MO line -> confirm it is short and that nothing else fixes it -> find
alternative items -> check where each one's supply comes from and whether it is quicker -> recommend -> one card ->
change the material line -> read it back -> reschedule the MO on its **current start date** (no date change) -> read
back and report. **One yes covers both calls. Do not mention the reschedule to the planner (not in the card, the report or the next step): it is part of the swap. Say something only if it fails (step 4).**

## What this does and doesn't do

- **Does:** replaces the component on **one material line of one MO** with an **alternative item** M3 holds as a
  related item with **replacement type 3, 4 or 5** (`M3_PMS100MI_UpdMatLine`), then **reschedules that MO on its current start date, so
  no date changes**, so that M3 recalculates it with the new component (`M3_PMS100MI_Reschedule`).
- **Only an alternative item.** The alternative must be an item related to the original with replacement type 3
  (interchangeable), type 4 (full interchangeability) or type 5 (product alternative material), and with a record in the line's warehouse. All three types are
  treated the same here. Never swap to an item the planner names that has no such relation: say so, and point to
  engineering or the item master. (`m3/known-inconsistencies.md` K1, K19: the buyer reads a wider set of types.)
- **Only when the swap is the fix.** It is offered when the original cannot be had in time and rescheduling doesn't
  help (step 1). When a reschedule or a pulled-in PO closes the gap, recommend those first and offer the swap only if
  the planner asks for it.
- **Report only what the swap affected.** The confirmation and the read-back cover the MO that was swapped, its material
  line and, only when the swap moved them, the lower-level orders it touched. Never mention MOs, POs or other orders that
  the swap did not change, not even as a warning or a side observation. Unaffected orders come up only if the planner
  asks.
- **Nothing but the component changes.** The line keeps its quantity, and the reschedule sends the MO's **current
  ordered quantity** and its **current start date** (M3 refuses a reschedule without a date: "Start or finish date must be
  entered"): the quantity and the dates stay as they are, in this flow. M3 itself may recalculate the times and the finish.
- **One MO and one line at a time.** The same shortage on several MOs is offered one after another, each with its own
  check and card: the first swap uses up the alternative's stock, so the next check starts again from the balance.
- **Purchase orders and planned POs are never changed here.** If the alternative's supply is a PO or a proposal, the
  buyer owns it (`inform-buyer-of-late-order.md`).
- **From a dashboard.** A Confirm click on a board may run this, as in chat: the board shows the same card, re-reads the MO and the component first, makes the same two calls in the same order and, when the card names it, the MO proposal delete of step 4b (the one delete a board may run, as a step of this flow and never on its own), and reads the result back. A board never runs it without that Confirm click.

## 1. When to offer a swap (all four must hold)

Read the MO and its component line (`M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`), then the original component the way
`material-shortage-check.md` does (balance, open PO lines, planned POs, competing MOs). Keep the **line's sequence
number** (the material line number): `M3_PMS100MI_UpdMatLine` needs it. If `LstMaterials` doesn't return it, try
`M3_PMS100MI_SearchMaterial` on the MO; if neither gives it, say so and don't offer the swap.

| # | Condition | How it is judged |
|---|---|---|
| A | **Not enough of the original in stock** | The original's running balance goes below zero on or before the line's reservation date (the date it is needed): stock plus supply, minus the MO's own need and competing demand. Name the quantity short. |
| B | **Existing supply of the original comes too late** | Every open PO line and planned PO for the original arrives after the need date, or is unconfirmed or only proposed, or there is none. Unconfirmed and planned supply never counts as safe (planner rule 2). For a made component, the supply is the open MO or MO proposal that makes it: it counts as late when it finishes after the need date, is preliminary or held, is only a proposal, or is blocked. |
| C | **Rescheduling the MO does not help** | Use the logic of `reschedule-mo.md` step 3. It does **not** help when (i) no confirmed supply covers the shortfall, so there is no date to move to; or (ii) moving the start to the day after the last confirmed supply makes the MO finish after its due date or after the requested date of a customer order it covers; or (iii) the lower-level order that supplies the component is itself late or blocked. If a reschedule would meet every date, this is not a swap case: recommend the reschedule. |
| D | **An alternative item exists** | At least one related item with replacement type 3, 4 or 5 that has supply either in stock or on a PO, planned PO, MO or MO proposal, quicker than the original (steps 2 and 3). |

Also don't offer it, and say why in one line, when: the MO is completed; the line shows material already issued or
reported (M3 would refuse); the MO's status is not one where a material line can change (M3 validates this strictly:
let it decide, and report its error plainly).

## 2. Find the alternative items

`M3_MMS020MI_LstItemRelation` `{ ItemNumber: <the original component>, ReplacementType: "ConditionalInterchangeability
(3)" }` and, in parallel, the same call with `ReplacementType: "FullInterchangeability (4)"` and with `ReplacementType: "ProductAlternativeMaterial (5)"`. Rows can come back as a
name, a name with the code in brackets, or a number: read the code, and keep only **types 3, 4 and 5**; if a filter was
ignored and other types come back, drop them yourself (accessories and cross-sell items
are never alternatives). Keep only relations whose start date is today or earlier. (The tool's filter label for type 3 reads
"ConditionalInterchangeability"; in this setup type 3 is used as **fully interchangeable**, so the label is just the filter
value to send. Type 4 is "FullInterchangeability" and type 5 is "ProductAlternativeMaterial".)

**Each of the three calls may answer "Record does not exist"** when the item has no relations of that type (type 5 often
has none). That is an empty list for that type (`m3/tool-conventions.md`): use the rows of the other calls, and say "no
alternative items are set up" only when all three come back empty.

For each one keep: the item, its **replacement type (3, 4 or 5)**, its **start date** and whether it is the **preferred** item.
Types 3, 4 and 5 all mean **fully interchangeable** here: no conditions, no conversion, same quantity.

- **Price and cost** aren't returned by this tool; don't compare them.
- **A record in the line's warehouse.** `M3_MMS200MI_LstItmWhsByItm` `{ ItemNumber, Warehouse: <the line's warehouse> }`
  (always pass the warehouse). No record there: the alternative can't be used on this line; list it as not usable.

## 3. Where the alternative comes from, and is it quicker

The quantity to cover is the line's **remaining quantity** (the same quantity as the original). Only the **line's own warehouse** counts; stock elsewhere is information (`m3/stock-across-warehouses.md`),
not a swap.

For each usable alternative, in parallel: `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`
`{ ItemNumber_ExactSearch, Warehouse_ExactSearch, SortBy: "ConfirmedDeliveryDate" }`, `M3_PPS170MI_SearchPOP`
`{ ItemNumber_ExactSearch, Warehouse_ExactSearch }`, for a made alternative also `M3_PMS100MI_SearchMO` and `M3_PMS170MI_SearchMOP`
`{ Facility_ExactSearch, ProductNumber_ExactSearch, SortBy: "StartDate" }` (skip MOs that are completed or have nothing left to make; a proposal in another warehouse does not count), and, to see competing demand, `M3_MMS080MI_LstMtPlByItmWhs`
(an empty plan is "no plan data", never "enough"; `m3/material-plan.md`).

Work out **Available from**: the first date the alternative covers the whole remaining quantity, after other demand:

| Source | Available from | Label |
|---|---|---|
| Free stock now (`AllocatableNet`) covers it | today | ✅ In stock |
| Free stock plus open PO lines with a **confirmed** date cover it | the date the quantity is complete | ⚠️ Confirmed PO <no> (not yet received) |
| Needs a PO line with no confirmed date | its requested date | ⚠️ Unconfirmed PO <no> (not safe) |
| Needs a planned PO (proposal) | its delivery date | ⚠️ Proposed, not released (not safe) |
| Free stock plus open **MOs** (firm) cover it | the finish date of the MO that completes the quantity | ⚠️ MO <no> (not yet finished) |
| Needs a **preliminary or held MO** | its planned finish date | ⚠️ Preliminary or held MO <no> (not safe) |
| Needs an **MO proposal** | its planned finish date | ⚠️ Proposed MO <no>, not released (not safe) |
| Doesn't cover it even with everything above | none | ❌ Not enough (covers <q> of <r>): not offered as a swap |

Rules:
- **Quicker than the original.** Compare with the date the **original** is covered, taking the earliest of its PO lines
  and planned POs even if unconfirmed (it has no date at all when it has no supply). For a made original it is the
  earliest finish of its open MOs and MO proposals, even if not firm. Offer an alternative only when its
  Available from date is **earlier** than the original's; show the days gained ("5 days sooner", or "the original has no
  supply"). Equal or later: not offered.
- **Does it meet the need?** Say whether Available from is on or before the line's need date (✅ In time) or after it
  (⚠️ Still <n> days after the need date: quicker, but not in time). A quicker alternative that is still late is
  offered with the warning and a lower confidence; the MO keeps its start date, so say that it would
  still wait for it.
- **Not safe supply** (unconfirmed PO, planned PO, MO proposal, preliminary or held MO) is shown with its label and never counted as ✅. If the swap rests
  on one of these, say who can make it firm: the buyer for POs and planned POs (`inform-buyer-of-late-order.md`), the planner (release or firm the order) for MOs and MO proposals.
- **An alternative with no stock, no PO, no planned PO, no MO and no MO proposal** is not offered. You may add its supply lead time
  (`SupplyLeadTime` from the item/warehouse record) as information only.
- **Competing demand on the alternative** (other MOs and orders): from the plan or the balance. If it can't be read,
  say "competing demand on <item> not checked" and lower the confidence.

## 4. Offer it (advice only)

Show up to three alternatives, best first: in stock before on order; then the earliest Available from; then confirmed
before unconfirmed; then the preferred item. Nothing is applied by showing the options.

> **Option: swap <original> for <alternative> on MO <n>** (line <seq>, operation <op>)
> Why: <original> is short <qty> on <need date>; its supply is <PO no. arriving <date>, <n> days too late | none>;
> a reschedule doesn't help because <reason from condition C>.
> <Alternative>: <qty> in stock | <label> from <date>, <n> days sooner; <✅ In time | ⚠️ still <n> days after the need date>.
> Write the quantity in stock when there is any. When the alternative is already in stock, write no date and no days
> sooner, only the quantity. Write a date only for supply that is not in stock yet (a partly stocked alternative: the
> quantity in stock, then the rest with its date).
> <When the original is a made item with a related MO proposal: "MO proposal <no> for <original> (<qty> <unit>, finish <date>) is deleted too.">
> Confidence: <High when in stock or on a confirmed PO and competing demand was read; Medium when supply is on an
> unconfirmed PO or only proposed; Low when competing demand on the alternative was not read>.
> What would change it: <the PO or proposal that isn't firm, demand not checked>.

Several alternatives: a small table (alternative, qty in stock, label and available from only when not in stock yet, days sooner, in time?, preferred) and one
recommendation.

## Confirm before writing

One card for the two calls. Re-read first (write protocol step 3): the MO is open and unchanged, the line still holds the
original, the original is still short, and the alternative's balance still covers it. If anything differs, don't show the
card: say what changed.

> **Swap material on MO <number>**
> <product number, product name from the item master> - facility <f> - line <seq>, operation <op>
> Component <original, name> -> <alternative, name> (related item, replacement type <3, 4 or 5>). Quantity on the line <q> <unit>
> (unchanged). Warehouse <wh> (unchanged).
> Why: <the shortage and why nothing else closes it, one line>. Supply of <alternative>: <label, date>.
> If you reply yes I will change the material line: `M3_PMS100MI_UpdMatLine`, component only.
> <When the original is a made item and an MO proposal for it ties to this need: "I will also delete MO proposal <no> for <original, name> (<qty> <unit>, finish <date>): `M3_PMS170MI_DelPlannedMO`.">
> <When the supply is not in stock: "<Alternative> is not in stock yet; the line will wait for <PO or proposal>, which is
> <not firm>.">
> Not changed: purchase orders and planned POs (including the original's), other MOs. I can't undo this from here: going back means another swap or a change in M3.
> Reply **yes** to swap.

Only after an explicit yes to this card:

1. **Snapshot the lower levels** as `reschedule-mo.md` step 2 does (the MOs that make semi-finished components, with
   their dates), before the first call. The snapshot is for your own comparison afterwards: do not show it or mention
   any of its orders unless step 5 finds one affected.
2. **Call `M3_PMS100MI_UpdMatLine` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber, SequenceNumber,
   ComponentNumber: <alternative> }`. Send nothing
   else (no `ComponentQuantity`): every other field of the line stays as it is. On an error, report it plainly and stop: no reschedule, no retry
   (M3 validates against the order status, reservations, allocations and the item's warehouse record, and may refuse).
   Read the line first to see whether it saved.
3. **Read the line back** with `M3_PMS100MI_GetMatLine` `{ Facility, ManufacturingOrderNumber, ProductNumber,
   SequenceNumber }`. If it still shows the original, wait a moment and read again (up to four reads). **Only when it
   shows the alternative and the expected quantity**, go on. If it doesn't, say so and stop without the reschedule.
4. **Re-read the MO** (`M3_PMS100MI_Get`) for its current quantity, then **call `M3_PMS100MI_Reschedule` once** with `{
   Facility, ManufacturingOrderNumber, ProductNumber, OrderedQuantityAltUom: <the MO's current ordered quantity, the same as on the MO>,
   FiniteCapacityPlanning: false, StartDate: <the MO's current start date, as just read> }` and **no `PlannedFinishDate`**.
   (M3 refuses a call with no date: "Start or finish date must be entered". Tested.) The yes on the card covers this call:
   don't ask again and don't mention it. Never send any date other than the current start date.
   If M3 refuses it anyway, report M3's message: **the swap still stands**, the MO is not recalculated, and the planner
   can reschedule in M3 or with `reschedule-mo.md` on a date the planner chooses. Don't retry, and don't pick a date.
4b. **Delete the MO proposal(s) the card named** (only when the original is a made, semi-finished item). Find them before
   the card: `M3_PMS170MI_SearchMOP { Facility_ExactSearch, ProductNumber_ExactSearch: <original> }`; take the proposals in the
   same warehouse that finish by the need date plus 7 days (from today when the need date has passed), earliest first, as long
   as together they do not exceed the quantity this MO needs of the original. M3 shows no link between the MO and its proposal
   here, so item, quantity and date decide, and the card names each one. After the swap (and the reschedule, or when that was
   refused), read the list again and delete only a proposal that is still there with the same number, quantity and finish
   date: `M3_PMS170MI_DelPlannedMO { PlannedOrderNumber }`, one call each, then read the list a last time. Never delete one the
   card did not name. If M3 refuses one, report its message and go on with the next; don't retry. The yes on the card covers
   these calls.

## 5. Read back and report

1. **The line:** a small table (field, before, now): component, quantity per unit, warehouse, operation, reservation date.
   ✅ for what changed as the card said, ⚠️ for anything unexpected.
2. **The MO:** `M3_PMS100MI_Get`: wait while the status reads "...-ChangeInProgress" (up to four reads; it took about a
   minute in the test), then give the start and finish date. Don't mention the reschedule, the times or the priority. If M3
   moved the start date, say so with both values.
3. **The lower levels** against the snapshot, **only when the swap affected one**: a lower-level order
   whose dates, quantity or status changed, or that now conflicts with the MO's need date. Then report that order in the block
   `reschedule-mo.md` step 4 describes (affected, conflict). Don't change any of them. **When none was affected, say
   nothing about the lower levels**: no MO numbers, dates, quantities or status, no "unchanged" and no "none found". An MO
   that the swap did not touch is not part of the report, even when it looks late or at risk: if it matters for another
   reason, the planner asks for it (`at-risk-orders.md`).
4. **The shortage again:** re-read the MO's material lines (`M3_PMS100MI_LstMaterials`) and the alternative's balance and
   say whether the line is now covered: ✅ covered by stock, ⚠️ waiting for <PO or proposal> on <date>, ❌ still short <qty>.
   Give the MO's new verdict in one line. Planning data changes when M3's planning runs: say the read time.

### Result line

```
MO <n>, line <seq>: <original> -> <alternative>; qty <q> <unit> (unchanged)
MO dates: start <d>, finish <d>[; start moved from <old> - only when M3 moved it]
[MO proposal <no> for <original>: deleted | not deleted (<M3 message>) - only when the card named one]
Material now: <✅ in stock | ⚠️ waits for <PO/proposal> on <date> | ❌ short <qty>>.[ Lower levels: <order, what moved> - only when one was affected; otherwise leave this out]
```

## Next step

- The alternative's supply is a planned PO or unconfirmed PO: "Want me to tell the buyer to release or confirm
  <PO or planned order> for <alternative>?" (`inform-buyer-of-late-order.md`).
- The original's open POs and planned POs may no longer be needed: say so in one line; the buyer decides (offer a drafted message).
- More MOs short on the same original: "MO <m> has the same shortage; want to check it for a swap?" (one at a time).
- "Want the full check on the new line?" (`material-shortage-check.md`); "Which customers does this affect?" (`customer-impact.md`).

## Edge cases

- **No related items of type 3, 4 or 5** - "No alternative items (replacement type 3, 4 or 5) are set up for <original>." Offer the other
  options (`material-shortage-check.md` step 4). Never suggest an item from outside the relations.
- **Alternatives exist but none is quicker, or none has enough** - show them with the reason (✅/❌ labels) and don't offer a swap.
- **A relation that hasn't started yet** - list it as "starts <date>"; not offered.
- **Alternative has no record in the line's warehouse** - not usable here; say so.
- **M3 refuses the line change** - report its message; nothing was changed; don't try another route or another tool.
- **The line changed but the reschedule failed or was refused** - report both results separately; the swap stands.
- **MO or line changed since the options were shown** - don't write; re-read and re-offer.
- **Several lines on one MO short** - one line at a time, each with its own card; the reschedule runs after each swap.
- **Several matches** (MO, line, relation) - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry.
- **A tool is missing** - say which (`M3_PMS100MI_UpdMatLine`, `M3_PMS100MI_Reschedule` or `M3_MMS020MI_LstItemRelation`) and that the swap isn't offered; don't use another write tool.
