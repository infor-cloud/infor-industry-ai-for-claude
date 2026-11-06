<!-- Part of references/delayed-po.md (UC3), step 3, option B. -->

### Substitutes (option B)

1. `M3_MMS020MI_LstItemRelation` with `ItemNumber`. Only these `ReplacementType` values are substitutes:
   CompleteReplacement (1), ReplacementAfterBalanceDepletion (2), ConditionalInterchangeability (3),
   FullInterchangeability (4), ProductAlternativeMaterial (5), SuccessorReplacement (8). AccessoryItem (7) and
   CrossSellItem (9) are **not** substitutes: leave them out. Note `StartDate` (the relation must have
   started) and `PreferredItem`. A related item that is also alternate material in the bill of material (step 4) is the strongest candidate: say so.
2. **Type 3 (conditional) means the substitute only fits under conditions** that M3 does not return: say
   "engineering or quality must approve" and do not call it a drop-in. The tool does not return a
   quantity factor: if the item names or sizes differ (for example 1800X800 against 2400X1200), say that the
   quantity needed in the substitute is unknown until engineering gives the factor. Never convert yourself.
3. **Stock:** `M3_MMS200MI_LstItmWhsByItm` with `CompanyNumber`, `ItemNumber` **and `Warehouse`**. Without the
   warehouse filter it returns every warehouse (very long). Use `ApprovedOnHandBalance`, `AllocatableNet`,
   `AvailableInventory` and `SafetyStock` (stock above safety stock is what can be used without breaking
   the buffer). Stock on hand means the substitute is available now: compare with the need dates.
   **Free quantity** = the substitute's projected balance after its own planned demand (planned demand = `ReservedPlannedOrderQuantity` on the stock record; read `M3_MMS080MI_LstMtPlByItmWhs` for the substitute and warehouse only when it is not 0, to get the dates; an empty plan is no plan data, so then go by the stock record) minus `SafetyStock`. Example: 200 on hand, 75 planned out, safety stock 100 = 25 free (the 125 left after the planned demand is not free: 100 of it is the buffer). Show this arithmetic, and never call the balance after other demand "free" before the safety stock is taken off.
4. **Bill of material:** `M3_PDS013MI_LstAltMat` (`Facility`, `ProductNumber` of the manufacturing order's
   product). An empty list means the BOM has no alternate material, so each MO needs its component changed
   by hand: say so, and that the buyer can change the MO's component themselves or contact the planner.
5. **Cost:** `LstItemRelation` returns no price. **Do not call `M3_PPS115MI_LstAltSupplier` for the substitute.** That tool is used only for the item on the purchase order (option D and the currency fallback), never for a substitute or any other item found in the analysis. The substitute's cost change is "price not available" in the table, and the buyer or engineering supplies the price. Do not put prices in messages to order or manufacturing owners.
6. For each substitute capture: its number and name (`ItemName` on the stock record), stock in the warehouse, that stock minus safety stock, which orders it
   could serve (earliest need dates first), what must be approved, and what cannot be judged from M3 (size
   and quantity factor, price, customer acceptance).
7. **Doing the swap: the Swap action.** When the substitute is a related item of type 3 or 5 with a record in the MO's warehouse and enough free quantity (step 3 above), the recommendation lists a **Swap** action for each affected MO. Its card is the swap card of `swap-material.md` (one card, one yes, two writes: `M3_PMS100MI_UpdMatLine`, then `M3_PMS100MI_Reschedule` on the MO's current start date with no date change; read back after each). A substitute that fails one of these conditions gets no Swap action: say why in one line, and that engineering or the planner must change the line. Add the MO responsible (`m3/m3-concepts.md`, "Who is responsible for what") to its card and, when the swap is done, offer a drafted message to them (`messages.md`): the buyer does not change another person's MO without telling them. Engineering or quality approval is not in M3: the card asks for it, and the swap starts only on a reply that says it is approved.
