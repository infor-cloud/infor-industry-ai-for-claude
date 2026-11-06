<!-- Part of references/delayed-po.md (UC3), step 3, option C. -->

### Distribution order from another warehouse (option C)

All movement of goods between our own warehouses is a **distribution order**: always use that term, never "transfer". When another
warehouse has free stock of the item, **propose a distribution order proposal** to the buyer without waiting to be asked, and list it
in the mitigation options table and among the actions that would change M3.

1. **Free quantity.** In the other warehouse: `AvailableInventory` after its own demand (`ReservedQuantity` and `ReservedPlannedOrderQuantity` on its stock record; read its material plan only when one of them is not 0), minus `SafetyStock`
   (`m3/stock-across-warehouses.md`). The `SupplyingWarehouse` setting does not block a distribution order: when the
   relation in step 2 exists, offer it, and do not warn that M3 may refuse the direction.
   Read the other warehouse's own demand from its stock record too (`ReservedQuantity`, `AllocatableNet`): an empty material plan is not an answer about demand (`m3/known-inconsistencies.md`, K3). When the plan is empty, go by the stock record and say so in one line.
2. **Relation.** `M3_DPS001MI_LstRelation` with `RelationType` "Distr-TwoWhs (1)", `FromWarehouse` and `ToWarehouse`. An empty answer means
   no relation: do not offer it, and say an administrator must add one. A hit gives the transport days; expected arrival = planning date + transport days.
3. **Quantity.** The quantity the affected orders need before the delayed PO arrives, up to the free quantity. Say how much of the short
   quantity it covers and which orders stay affected.
4. **Offer it as a write card** (`m3/write-protocol.md`): `M3_DPS170MI_CrtPlannedDO` with `FromWarehouse`, `Warehouse` (the receiving one), `ItemNumber`,
   `PlannedQuantity`, `PlanningDate` (default today; tell the buyer it can change) and `PlannedOrderStatus`: `Pur/planMan` (status 20, firm) by default,
   or `Released` (status 60) when the buyer asks to release it (item 5). The card names the status in words and with its number.
   After the yes: re-read the free stock in the sending warehouse, write in one call, then read the receiving warehouse's plan
   (`M3_MMS080MI_LstMtPlByItmWhs`) and the sending warehouse's plan, and report the category and status M3 shows for the proposal (20 or 60, as on the card).
   If M3 shows another status, say so with ⚠️ and do not call the proposal released. Then run step 5 (`delayed-po/5-after-action-solved.md`) to show whether the impact is solved.
5. **Firm or released.** The status is a value the buyer decides, like the date and the quantity: the card starts at firm (20) and says it can change.
   - **Firm (status 20):** the proposal is not released, and the planner releases it. List that as a plain-text step with the planner as "who".
   - **Released (status 60):** the buyer releases it in the same write. They ask for it in the reply that starts the step ("C1 release", "create and release it")
     or in answer to the card ("release"). Never choose it for the buyer. A request to release changes a value on the card, so show the card again with
     status Released (60) and wait for the yes. A message that names the whole action and its values (item, quantity, from and to warehouse, planning date,
     released) is itself the yes (`m3/write-protocol.md`, step 2). The card for this variant also says: which warehouse ships and how much of its free quantity
     the proposal uses (and what is left above its safety stock), that the planner has nothing left to release, and that it cannot be undone from here.
   - **An existing proposal cannot be released from here.** `M3_DPS170MI_CrtPlannedDO` sets a status only when it creates the proposal; this skill has no call that
     changes the status of a proposal that already exists (one created earlier in the conversation at status 20, or one made by M3's planning). When the buyer asks
     to release one, say so in one sentence, name the proposal by item, quantity, warehouses and planning date, and tell them to release it in M3 or ask the planner.
     Never delete a proposal and create it again at status 60 to get around this.
   - Either way it is a **proposal**, not a distribution order: do not say that stock has moved, or that a distribution order exists, until M3 shows it.
     Do not use the inbox steps or the calls that add a distribution order head and line.
6. **Once the buyer has chosen the distribution order, the card and the reply say nothing about swapping** or any other mitigation option. The same holds the other way round for the swap (`swap-material.md`). Close the card with "If you want something else, say so."
