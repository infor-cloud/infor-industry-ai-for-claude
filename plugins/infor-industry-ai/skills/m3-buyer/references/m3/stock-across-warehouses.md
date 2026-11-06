# Stock across warehouses

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS200MI_GetItmWhsBal`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_MMS080MI_LstMtPlByItmWhs`

Shared procedure.

1. **Start with `M3_MMS200MI_LstItmWhsByItm` (company and item), once per item in the conversation.** It returns every warehouse that carries the item with
   `ApprovedOnHandBalance`, `ReservedQuantity`, `AllocatableNet`, `AvailableInventory`, `ProjectedOnHandEndOfLeadTime`,
   `LeadTime`, `SupplyLeadTime`, `SafetyStock`, `ReservedPlannedOrderQuantity`, `SupplyingWarehouse` and the default supplier. The numbers come back as strings: convert them. Reuse this one result for the PO line's warehouse and every other warehouse: don't call `GetItmWhsBal` for a warehouse it already returned. If every
   warehouse shows 0 on hand, re-allocation and a distribution order are dead: say so and stop.
2. Check the line's (or the order's) own warehouse first, then the other warehouses.
3. Only when you need more detail for one warehouse, call `M3_MMS200MI_GetItmWhsBal` or
   `M3_MMS200MI_GetItmWhsBal_Subname` (one item, one warehouse). Which warehouses to look at: the order's own warehouse,
   the user's default warehouse, every warehouse on the open customer order lines involved, and any others from
   `LstItmWhsByItm`.
4. Read `ApprovedOnHandBalance`, `ReservedQuantity`, `AllocatableNet`, `AvailableInventory` and
   `ProjectedOnHandEndOfLeadTime`. **Free to allocate here** = `AllocatableNet`; **free for a distribution order from another warehouse** =
   `AvailableInventory` in that warehouse. For another warehouse, read its material plan too
   (`M3_MMS080MI_LstMtPlByItmWhs`) only when its stock record shows demand (`ReservedQuantity` or `ReservedPlannedOrderQuantity` not 0): the stock is only free after its own demand.
5. `M3_MMS200MI_LstSumWhsBal` needs an alias number, so it does not fit this check.

**The late PO may still count as supply.** Compare `ProjectedOnHandEndOfLeadTime` with `AvailableInventory` for the
PO's warehouse. If the projection is far higher and the gap is about the open PO quantity, planning is probably counting
the late PO and will not create new replenishment. Point this out as an inference. The fix is to re-date the line to a
realistic date or close it; both are writes and need the user's confirmation.
