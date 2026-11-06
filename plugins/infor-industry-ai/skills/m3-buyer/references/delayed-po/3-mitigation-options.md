<!-- Part of references/delayed-po.md (UC3). Step 3 overview: read this first, then only the option files you need. -->

## 3. Look at the mitigation options

For each mitigation option, gather facts, then judge. Every option is tried on every run ("Check every mitigation option, every time" in the index): one that cannot work is shown as not possible, with the reason, never left out. In the answer, always call
them "mitigation options", never just "options".

**Changing the delivery method is not a mitigation option in this skill.** M3 has no way to do it through the
tools we use (no method list, lead time or cost), so never suggest it as a fix. If the buyer raises it,
say it must be arranged with the supplier or carrier outside M3, and that a faster carrier only helps once
the supplier has confirmed a date.

| Mitigation option | Tools | Check |
|---|---|---|
| **A. Check if stock balance can be re-allocated** | stock from the `M3_MMS200MI_LstItmWhsByItm` call (read only) | Is there stock on hand in the warehouse of the PO line? Show on hand, reserved and free quantity. No stock on hand answers it: show "no stock in the warehouse" as the reason. The re-allocation itself is manual: the buyer does it in M3, so the action is a plain-text step with the buyer as "who", never a write from here. Do not read orders, priorities or who loses. |
| **B. Substitute item** | `M3_MMS020MI_LstItemRelation`, `M3_PDS013MI_LstAltMat`, `M3_MMS200MI_LstItmWhsByItm` (see `3b-substitutes.md`) | Related items and the bill of material's alternate material for each affected MO's product, the substitute's free quantity in the warehouse (after its own planned demand and above safety stock), and whether engineering must approve. |
| **C. Stock in other warehouses (distribution order)** | `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS080MI_LstMtPlByItmWhs` for the other warehouse (only when its stock record shows demand), `M3_DPS001MI_LstRelation` | Free quantity elsewhere, after their own demand and above safety stock, and a distribution relation to the short warehouse. If both hold, **propose a distribution order proposal** (`M3_DPS170MI_CrtPlannedDO`; see `3c-distribution-order.md`). |
| **D. Alternative supplier** | `M3_PPS115MI_LstAltSupplier` (see `3d-alternate-supplier.md`), `M3_PPS100MI_GetAgrLine / LstAgrHeadBySup / LstAgrLine`, `M3_CRS620MI_SearchSupplier`, `M3_MMS200MI_LstItmWhsByItm` | Alternate suppliers with agreement price. **Always read the lead time of the warehouse on the PO line** (its `LeadTime` from the one `LstItmWhsByItm` call, or `LstItmWhsByItm` with `Warehouse` if that call was not made): arrival = today + that `LeadTime`. Is the arrival before the need date? New PO needed: **create the PO directly** (`M3_PPS370MI_*`, see `create-new-po.md`), not a planned PO. |
| **E. Accept and reschedule** | `M3_PMS100MI_Reschedule`, `M3_OIS100MI_UpdCOPlanDates` | What moves if we simply accept the new date? Use when slack covers it or no option is better. |

**Read each fact once.** One `M3_MMS200MI_LstItmWhsByItm` call for the short item (`m3/stock-across-warehouses.md`, step 1) gives stock, reserved quantity, safety stock, planned demand (`ReservedPlannedOrderQuantity`), lead time and supplying warehouse for every warehouse: use it for options A, C and D, and do not repeat it with `GetItmWhsBal`. A substitute needs one call with the line's warehouse. Read a material plan for another warehouse or for a substitute only when its stock record shows demand (`ReservedQuantity` or `ReservedPlannedOrderQuantity` not 0), because then you need the dates; when both are 0 the stock record already answers it, and you say so in one line. Do not read the MO's material lines in the analysis: `swap-material.md` reads them when the buyer chooses the swap.

For each mitigation option capture: **arrival date vs. need date, cost difference, orders still affected,
who is affected, risk, what actions it requires**. Cost difference = (new price − current price) × quantity
plus any known expedite or transport charge. Show the arithmetic, in the currency read as in step 1 ("Currency").

Quality status and engineering approval are **not** in M3 data. If an option depends on them (a substitute item,
option B), list it as a condition the buyer must clear. **This never applies to an alternate supplier (option D):** do
not mention supplier screening, sanctions lists, approval or qualification for it. A supplier with a valid agreement is
fine to buy from, and the buyer can create the PO without any further question about the supplier.

### Can anything arrive in time?

Before the mitigation options, compare the earliest need date with the fastest possible supply: the item/warehouse
lead time of the warehouse on the PO line (`LeadTime` from the one `M3_MMS200MI_LstItmWhsByItm` call, or from a call with `Warehouse`) added to today, and the dates of other open supply
(for example a stopped PO that could be released). If nothing can arrive before the earliest need date,
say so up front: the work is then to minimise the damage (priorities, early warning to customers), not to
find a full fix.

### Stock check across warehouses

Follow `m3/stock-across-warehouses.md`. If every warehouse shows 0 on hand, mitigation options A and C are not possible (no stock in any warehouse): show both rows with that reason and go on with B, D and E.

### Where the details of each option are

- Option B (substitutes): `delayed-po/3b-substitutes.md`
- Option C (distribution order): `delayed-po/3c-distribution-order.md`
- Option D (alternate supplier) and stale lines: `delayed-po/3d-alternate-supplier.md`
- Options A and E need nothing beyond the table above.
