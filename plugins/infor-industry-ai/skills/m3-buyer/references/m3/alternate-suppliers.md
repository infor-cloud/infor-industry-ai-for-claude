# Alternate suppliers for an item

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS115MI_LstAltSupplier`, `M3_PPS100MI_GetAgrLine`, `M3_PPS200MI_GetHead`, `M3_PPS100MI_LstAgrHeadBySup`, `M3_PPS100MI_LstAgrLine`, `M3_CRS620MI_SearchSupplier`, `M3_MMS200MI_LstItmWhsByItm`

Shared procedure (from the buyer's delayed-PO option D). **Use it only for the item on the purchase order being analysed**, never for a substitute or any other item found along the way.

Call `M3_PPS115MI_LstAltSupplier` with `ItemNumber` (add `RequiredQuantity` and `RequiredUnitOfMeasure` with the open
quantity when you want price evaluation for that quantity). It returns one record per supplier agreement:
`AlternateSupplierNumber`, `AgreementNumber`, `AgreementStatus`, `ItemSupplierStatus`, `SupplyLeadTime`,
`ValidFromDate`/`ValidToDate`, `Currency`, `NetPriceLocalCurrency` with `LocalCurrency`.

- **Fallback while the tool is unavailable:** `M3_MMS200MI_LstItmWhsByItm` shows the default supplier and lead time per
  warehouse (a different supplier in another warehouse is a lead). Present it as an indication that `LstAltSupplier` or
  the agreement lines must confirm.
- **Exclude the supplier of the delayed PO.** If that is the only record, the item is **single-source**: say so, and an
  alternative supplier does not apply. If the call fails, the item is "unknown", never "single-source".
- **Only use agreements with a valid status** (for example "Valid (40)") whose validity period covers the date the order
  would be placed.
- **Always check the lead time of the warehouse on the order line.** Read `LeadTime` and `SupplyLeadTime` of the item in
  the warehouse of the PO line (or demand line) with `M3_MMS200MI_LstItmWhsByItm` (`CompanyNumber`, `ItemNumber`,
  `Warehouse`), every time, whatever the agreement says. Reuse the result if the item's warehouses were already read in this conversation. Arrival from the alternate supplier = today + that
  warehouse `LeadTime`. Show the lead time, the warehouse and where it came from. If the agreement's `SupplyLeadTime` is
  above 0 and differs, show both and use the longer one. `SupplyLeadTime` = 0 on the agreement is **not maintained**,
  not "immediate": it never gives an arrival date by itself. Only if the warehouse `LeadTime` is also 0 or missing,
  ask the user for the supplier's real lead time and treat arrival as unknown. Then compare: is the arrival before
  the need date?
- **Currency is given here**, so show it: price in `NetPriceLocalCurrency` is in `LocalCurrency`; the agreement currency is
  `Currency`. Do not convert. Before using a price in cost arithmetic, confirm the price quantity (per unit or per 100,
  say) with `M3_PPS100MI_GetAgrLine` (agreement, supplier, valid-from date), and compare like with like against the
  current PO price. The PO price is in the PO currency: read it from the PO header (`M3_PPS200MI_GetHead`, `Currency`), or,
  if the header can't be read, from the agreement with the PO's supplier (`Currency` in the list above; `m3-concepts.md`,
  "Currency"). Never write that
  the PO has no currency. Cost difference = (new price − current price) × quantity plus any known expedite or transport charge.
  Show the arithmetic.
- **If the tool returns a metadata error** (`PurchasedQuantity` as `***`), do not retry. Tell the user in one line that
  alternative suppliers could not be read for this item, and fall back to `M3_PPS100MI_LstAgrHeadBySup` /
  `M3_PPS100MI_LstAgrLine` and `M3_CRS620MI_SearchSupplier`.
- **Suppliers not found are not proof there is none**: an item can be bought from a supplier with no agreement. Say "no
  alternative on record in M3", not "no alternative exists".
- **Do not mention supplier screening, sanctions lists, approval or qualification** for an alternate supplier, and do not
  list any such condition. A supplier with a valid agreement is fine to buy from: the buyer can create the PO without any
  further question about the supplier.

A new purchase from the chosen supplier is a **PO created directly** (batch entry), not a planned PO (proposal): `create-new-po.md`, section "From an alternate supplier". The same file covers confirming the new PO at once (D1) and what happens to the original, delayed line (D2).
