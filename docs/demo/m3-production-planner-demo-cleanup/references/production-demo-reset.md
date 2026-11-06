# Clean production demo data for an item (the full reset)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`,
plus the tools named in `customer-orders.md`, `mos-and-proposals.md` and `shift-pattern.md`, and
`M3_PMS100MI_LstOperations`, `M3_PMS170MI_LstOperations`.

Command: "Clean production demo data for item <item>". The rules in `SKILL.md` apply (typed item, **one card and one yes
for the whole command**, re-read before writing, facility, refusals, read back). Five parts, always in this order:

1. COs of the item. 2. MOs and MO proposals of the item and all its lower levels. 3. Work centers used by those MOs and
proposals. 4. Temporary shift patterns on those work centers. 5. Capacity of those work centers.

**The order matters.** Everything is **read first** (the work centers in particular: an MO that is deleted can no longer be
read, so its operation lines have to be read before part 2 is deleted). Then one card, one yes, then deleting in the order
below.

## Read (nothing is changed yet)

1. **Facility** from `M3_MNS150MI_GetUserData_CurrentUser`. If the item doesn't exist or nothing is found anywhere, say so
   in one line and stop.
2. **COs.** Steps 1 and 2 of `customer-orders.md` (read the lines, sort into whole orders / only the lines for the item /
   left alone).
3. **MOs and proposals.** Steps 1 and 2 of `mos-and-proposals.md` (level 0, then the lower levels through the product
   structure, up to 6 levels, all open MOs and proposals of the semi-finished items).
4. **Work centers.** For **every MO and every proposal on the list** (all levels) read its operation lines:
   `M3_PMS100MI_LstOperations { Facility, ManufacturingOrderNumber, ProductNumber }` for an MO and
   `M3_PMS170MI_LstOperations { OrderNumber: <proposal number> }` for a proposal. Collect the distinct work centers
   (use the field names M3 returns) and, per work center, the earliest and latest operation date. Orders that will not be
   deleted (left alone) don't count. Confirm each work center and read its description with `M3_PDS010MI_Get { Facility,
   WorkCenter }`. Operations without a work center are skipped. If M3 returns no operation lines at all, there are no work
   centers: parts 4 and 5 are left out of the card and you say so on it.
5. **Temporary shift patterns.** For each work center, use steps 2 and 3 of `shift-pattern.md`, with the search window
   widened to cover its operations: from the earlier of (Monday two weeks ago, the Monday of its earliest operation date)
   to the later of (today + 14 weeks, its latest operation date). Result per work center: no adjustment, or one or more
   adjustments with from date, to date and the shift read on those days.
   **Only a shift pattern that differs from the work center's normal one is an adjustment.** The normal shift pattern
   (normally 001) is never touched, and a work center with no deviating week has nothing to delete.

## Card

> **Clean production demo data for <item name> (<item>)**
> **Customer orders:** whole orders (<n>): <numbers>. Only the lines for this item (<n>): <order/line>; the other lines stay. Left alone (<n>): <order/line> (delivered or invoiced).
> **MOs and MO proposals:** Level 0, <item name> (<item>): MOs <numbers>; proposals <numbers>. Level 1, <semi-finished name> (<item>): MOs <numbers>; proposals <numbers>. <one line per further level>. Total: <n> MOs and <m> proposals. Left alone: <numbers and why>.
> **Work centers used:** <name> (<code>), <name> (<code>), ...
> **Temporary shift patterns to delete:** <work center name (code)>: <from date> to <to date>, shift <shift>, <h> h a week instead of <normal> h. (<work center name (code)>: none.) The normal shift <normal> stays.
> **Capacity to re-create:** <work center name (code)>: <from date> to <to date>, ...
> Other MOs that use these work centers are not rescheduled, and they lose any extra capacity that is deleted here.
> This can't be undone. Reply **yes** to run all of it.

Leave a part off the card if it is empty (for example no COs), and say "none" for it in one short line instead. The
"Capacity to re-create" span per work center runs from its earliest to its latest date among its operations on the card
and its deleted adjustments.

## After the yes

Re-read each record just before its write (SKILL.md rule 3). Then, **in this order**:

1. **COs.** Step 4 of `customer-orders.md`. COs first, so that no customer order demand is left behind to block or recreate
   supply.
2. **MOs and proposals, top down**, level by level. Step 4 of `mos-and-proposals.md` (including the second try for a
   proposal M3 refused because of higher-level demand).
3. **Shift patterns.** `M3_PDS010MI_DelShiftPatAdj { Facility, WorkCenter, FromDate }` per adjustment (step 5 of
   `shift-pattern.md`, delete only). If M3 answers "does not exist" because the adjustment started on a weekend, try the
   Sunday and then the Saturday before it.
4. **Capacity.** `M3_PDS010MI_CrtCapacity { Facility, WorkCenter, FromDate, ToDate }` for **every** work center on the
   card, with the span from the card (also for a work center that had no adjustment, as requested), and always after its
   own shift pattern delete. If a delete was refused, still re-create the capacity for that work center only if nothing
   else changed there; otherwise leave it and say why.

A refusal or an error follows SKILL.md rules 9 to 11: the run goes on with the next record when M3 simply refuses a
record, and stops when a call fails with a server error or an authority refusal (say what was and wasn't done, including
which of the five parts were not reached).

## Read back and report

Use the read-back of each part: `M3_OIS100MI_GetOrderHead` and the item's lines (COs), `M3_PMS100MI_SearchMO` and
`M3_PMS170MI_SearchMOP` for the item and each semi-finished item (MOs and proposals), `M3_PDS016MI_GetDailyCap` at 07:00
for the from and to dates of each deleted adjustment (normal shift back; if it still shows the old one, read again every
20 seconds, up to 4 times). Report in a few lines, per part: deleted, refused (with M3's message), left, and per work
center "back to the normal shift <normal> from <from> to <to>" and "capacity re-created". Say nothing about the capacity
calls unless one failed. Purchase orders are never touched; if open purchase orders exist for the item or its components,
that is not mentioned unless the user asks.
