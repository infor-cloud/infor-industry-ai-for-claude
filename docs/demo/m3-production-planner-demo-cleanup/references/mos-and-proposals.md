# Delete the MOs and MO proposals for an item, with their lower levels

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PMS100MI_SearchMO`, `M3_PMS170MI_SearchMOP`, `M3_PMS100MI_LstMaterials`, `M3_PMS170MI_LstMaterials`, `M3_PMS100MI_DltMO`, `M3_PMS170MI_DelPlannedMO`

Command: "Delete all MOs for item <item>". The rules in `SKILL.md` apply (typed item, one card, one yes, re-read before
writing, facility, refusals, read back). Purchase orders are never part of this. `production-demo-reset.md` reuses steps 1, 2 and 4 of this file as part of the full reset (it reads the operation lines before anything is deleted).

## Steps

1. **The item's own orders (level 0).** `M3_PMS100MI_SearchMO { Facility_ExactSearch, ProductNumber_ExactSearch: <item> }`
   and `M3_PMS170MI_SearchMOP { Facility_ExactSearch, ProductNumber_ExactSearch: <item> }`. ("Record does not exist"
   means none.) An MO that is completed or beyond can't be deleted: list it as left alone.
2. **Lower levels.** For every MO read its materials (`M3_PMS100MI_LstMaterials { Facility, ManufacturingOrderNumber,
   ProductNumber }`) and for every proposal its materials (`M3_PMS170MI_LstMaterials { OrderNumber: <proposal number> }`).
   Each component with `AcquisitionCode` Manufacturing is a semi-finished item: read its open MOs and proposals the same
   way (they become the next level). Repeat for each new order or proposal, up to **6 levels**, with a list of numbers
   already seen so nothing is read twice. The lower levels are found by product structure and include **all** open MOs
   and proposals of those semi-finished items, so the card lists them by level.
3. **Card:**

   > **Delete MOs and MO proposals for <item name> (<item>)**
   > Level 0, <item name> (<item>): MOs <numbers>; proposals <numbers>.
   > Level 1, <semi-finished name> (<item>): MOs <numbers>; proposals <numbers>.
   > <one line per further level>
   > Total: <n> MOs and <m> proposals. Left alone: <numbers and why>.
   > This can't be undone. Reply **yes** to delete.

4. **Delete from the top down**, level by level (the top level first, so that M3's protection of proposals tied to a
   higher level can't block a lower one): `M3_PMS100MI_DltMO { ManufacturingOrderNumber }` for an MO,
   `M3_PMS170MI_DelPlannedMO { PlannedOrderNumber: <number> }` for a proposal. M3 only deletes an MO that has not been
   started and has no reported output or stock movement: when M3 refuses one, list it with M3's message (it has to be
   closed or reversed in M3). A proposal M3 refuses because of higher-level demand is tried once more at the end, after
   everything else is deleted; then it is listed.
5. **Read back.** `M3_PMS100MI_SearchMO` and `M3_PMS170MI_SearchMOP` again for the item and for each semi-finished item
   on the card: only the refused ones should be left. Report: deleted, refused (with M3's message), left.
