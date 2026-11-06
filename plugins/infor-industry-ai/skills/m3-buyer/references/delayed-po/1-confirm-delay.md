<!-- Part of references/delayed-po.md (UC3). Read the index first. -->

## 1. Confirm the delay

`M3_PPS200MI_SearchLine` with `PurchaseOrderNumber_ExactSearch` and `PurchaseOrderLineNumber_ExactSearch`
(`GetLine` takes no line number, do not use it): status, ordered, confirmed and received quantity,
requested and planning date, delivery method and terms. `SearchLine` returns `ConfirmedDeliveryDate`
only once it is set: if the status is 31 or higher and the field is missing, ask the buyer for it. Report the status as
name and code. If the buyer reacts to a supplier message (updated confirmation, ASN or transport
notice), compare it with `M3_PPS200MI_LstLineTrans` (ShipmentAdvice, TrnsptNotific). Report: what the PO says, what the supplier says, and the new gap in days.
The supplier's date is the arrival date (see "Dates" above): the gap is that date minus the PO's confirmed date, or its
requested date if none is confirmed.

**Currency.** `SearchLine` returns no currency, so read it when an amount or a cost difference is needed: first on the PO
header (`M3_PPS200MI_GetHead`, `PurchaseOrderNumber`, field `Currency`; the same on every line of the PO), second, if the
header can't be read, on the agreement for the PO's supplier and item (`m3/m3-concepts.md`, "Currency";
`M3_PPS115MI_LstAltSupplier` gives the agreement's `Currency`). Never write that the PO has no currency or that the currency
is missing. Only when neither source gives one, write "currency not available" and leave the cost arithmetic out.
