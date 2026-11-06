<!-- Part of references/delayed-po.md (UC3), step 3, option D and stale lines. -->

### Alternative suppliers (option D)

Follow `m3/alternate-suppliers.md`. When the buyer chooses an alternate supplier, **create the PO directly** with
`create-new-po.md` (section "From an alternate supplier"): one card, one yes, a real PO to the supplier. Do not create a
planned PO (a proposal) and do not offer to release one.
Arrival = today + the lead time of the PO line's warehouse. When that is after the need date, still show the option, with how many days late it arrives and what it costs: it can be the fallback. Agreement prices from `M3_PPS115MI_LstAltSupplier` are in `LocalCurrency`: compare them in that currency and name it.

**Option D has two steps.** **D1** creates the new PO (`create-new-po.md`) and also offers to confirm it at once with the supplier's date and quantity. **D2** is what happens to the original, delayed line, offered as two options once the new PO exists (D1 already solves the impact, see step 5 in `delayed-po/5-after-action-solved.md`; D2 is offered straight after it, because adjusting the original line is what clears M3's action messages): reconfirm it with the new date and quantity (and, when the new quantity is smaller than the ordered one, ask whether the rest is still expected, and send `FinishMark` = 1 on the confirm if it is not), or delete it (possible at status 15 to 20; at status 35 or above the full line is finish marked instead). After the action is performed, ask whether a message to the original supplier should be drafted (`messages.md`).

### Stale lines and planning

- **Far past due.** If the confirmed date is more than 60 days in the past (default, tell the buyer
  it can change) and nothing is received, treat the line as **stale**. Say so, and ask whether the
  supplier will still deliver. Do not build the mitigation options around a date that old.
- **The late PO may still count as supply**: see `m3/stock-across-warehouses.md`.
