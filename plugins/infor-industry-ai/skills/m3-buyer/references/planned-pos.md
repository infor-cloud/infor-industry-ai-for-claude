# Buyer: planned POs (proposals)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS170MI_SearchPOP`, `M3_PPS170MI_RelPOP`, `M3_PPS170MI_UpdPlannedPO`, `M3_PPS200MI_SearchHead`, `M3_PPS200MI_GetHead`

<!-- contents:start -->
**Contents**

- 1. Review the planned POs: Planned PO codes
- 2. Releasing a planned PO (write)
- Show it
<!-- contents:end -->

## 1. Review the planned POs

Reviews the buyer's planned purchase orders (proposals) from `M3_PPS170MI_SearchPOP`:
`Buyer_ExactSearch` = `User`, no warehouse filter. The search returns supplier, item, quantity,
`ReleaseDate`, `DeliveryDate`, `ActionMessage`, `PlannedOrderStatus` (a name), `Currency`,
warehouse and facility. `SearchPOP` returns the currency, so show it for planned POs.

- **Overdue** = `ReleaseDate` before today. **Due soon** = today up to and including 5 days ahead.
  Show both groups, overdue first; leave later ones out and count them in one line.
- Group by supplier and item, with the number of planned POs and the total quantity per group, and the
  warehouse on each.
- **Can be released** = no warning, or a numeric warning. **Must be changed first** = a letter or
  letter+number code (a stop). Separate the two.
- Translate status, action message and warning code with the tables below. Never show a name or code
  alone.
- For **overdue** planned POs run `impact-check.md` (find the planned PO's own record by its planned
  order number, category planned purchase order) to see which orders depend on it. Release first the
  ones that affect orders with the earliest need date.
- **Releasing** is a write: `M3_PPS170MI_RelPOP`, only after the buyer confirms that exact planned PO
  (see "Writes" in `SKILL.md`).

### Planned PO codes

Translate status, action message and warning code with `m3/status-codes.md` ("Planned purchase orders"). Numeric
warning codes can be released; letter codes are stops that must be changed first. C1 and C2 mean a released order is or
will be delayed: if one appears, offer `delayed-po.md` for that order.

## 2. Releasing a planned PO (write)

Releasing is **two steps** (tested):

1. **Set each planned PO to status 60 (Released)** with `M3_PPS170MI_UpdPlannedPO`: `PlannedOrderNumber`,
   `PlannedOrderSubnumber` = 0, `PlannedOrderSubnumber2` = 0, `PlannedOrderStatus` = `Released`.
2. **Run `M3_PPS170MI_RelPOP`** with buyer, supplier and facility (`FromBuyer`/`ToBuyer`, `FromSupplierNumber`/
   `ToSupplierNumber`, `FromFacility`/`ToFacility`). **Do not use the number range**: its "purchase order number" is
   a number assigned to a planned PO, not the planned order number, and the planned order number released nothing.

**There is no step that assigns a PO number.** M3 gives the new PO its number when `RelPOP` creates it: read it from the
new PO afterwards. A planned PO made with `m3/create-planned-po.md` is released the same way.

`RelPOP` releases **every planned PO at status Released that matches the selection**, and only those. That is why the
selection is safe only when you control which planned POs are at status 60:

- **Never call `RelPOP` without buyer, supplier and facility**, and never "release all". For a request like "release
  everything overdue", list the planned POs by number (item, quantity, supplier, release date, what depends on it) and
  get the buyer's confirmation of that list.
- **Several planned POs:** set all of them to status 60 first, then run `RelPOP` once per supplier (and facility).
  M3 creates the orders at the same time, and **planned POs for the same supplier are grouped into the same PO**. Say so.
  If the buyer wants separate POs for the same supplier, do step 1 and 2 for one planned PO at a time.
- **`PlannedOrderStatus_ExactSearch` is ignored by `SearchPOP`** (tested: it returned every planned PO), so check the status
  in the rows yourself.
- **Check between the steps:** read `M3_PPS170MI_SearchPOP` (buyer) and confirm that exactly the intended planned POs have
  `PlannedOrderStatus` = `Released` and that no other planned PO of that buyer, supplier and facility does. If another
  one is at Released, stop: `RelPOP` would release it too.

**Before asking for confirmation, check and show:**

1. The planned PO can be released: no letter-code warning (stop) and not already Released (60). If it is a stop,
   say what must change first (see the warning table) and do not release.
2. Facts: planned order number, item, quantity, supplier, warehouse, release date, delivery date, price and
   currency (`SearchPOP` gives `Currency`). **If the action message is `DeleteOrder`, M3 suggests deleting the
   planned PO** (the need has gone): say so, give the amount that would be ordered, and ask the buyer whether to
   release it anyway. Never release a `DeleteOrder` planned PO without that explicit answer.
   Only the buyer's own planned POs (`Buyer` = the user) are in scope: planned POs of other buyers for the same supplier
   are listed but never released.
3. What depends on it (from `impact-check.md`) and how late the orders already are.

**Ask:** "Release planned PO <no> (<item>, <qty> from <supplier>) now? M3 will create a purchase order from it."
A message from the buyer that already names the planned PO number and asks for the release is the confirmation.

**M3 validates the planned PO when it is updated.** If `UpdPlannedPO` fails, report the message as it is. Tested:
"Responsible <user> does not exist" and then "Requisition by <user> does not exist": the planned PO carried a user
that no longer exists. Setting `ResponsibleUser` and `Requisitioner` to the buyer fixes it, but it changes who
owns the planned PO: **ask the buyer, naming each field, before changing it**, and do it only in the same update.
Never retry with other changes without asking.

**After the call** (`UpdPlannedPO` and `RelPOP` return no data; `RelPOP` runs as a batch job):

1. Wait a moment. Right after `RelPOP`, `SearchPOP` can still show the planned PO as Released and no PO exists yet.
   The job queue cannot be read (`M3_MNS320MI_Search` fails: "table CJBCTL is not indexed"), so look for the result
   instead: `M3_PPS200MI_SearchHead` (buyer, `OrderDate_ExactSearch` today) for the new PO, then `SearchLine` for its
   lines. If nothing has appeared after a few tries, say so and ask the buyer to check the job in M3.
2. Report the new PO number, line, item, quantity, price and amount (currency from `M3_PPS200MI_GetHead`), requested and
   planning date and **status**. In the test the new PO was already **Printed (20)**, not ReadyForPrintout: say
   that **status 20 means the supplier has the order**: whether M3 sends it automatically when it is released is a setting on the
   order type. A new PO at 15 would still have to be printed and sent.
3. Confirm with `SearchPOP` that the planned PO is gone.
   **A PO made from an overdue planned PO keeps the old requested date** (tested: an overdue planned PO became a PO whose requested and
   planning dates were both already past). Say so, and say that a real
   delivery date has to come from the supplier: offer the message or the call and confirm flow.
4. Offer the next step: a message to the supplier, or the call and confirm flow (`po-actions.md`, "Confirm a
   PO line") for the new line. For an order that is late, ask for the earliest delivery date.
5. If M3 returns an error, report it as it is and stop. Do not retry with a wider selection.

**Several planned POs for one supplier** (tested): set to Released one by one, checked, then released with one `RelPOP` for
buyer, supplier and facility, they became **one PO with all the lines**. The planned POs were gone from `SearchPOP` at once,
the PO was not yet visible in `SearchHead` for a moment, and `SearchLine` first showed only some of the lines (`LstLine2`
showed all).

## Show it

Present planned POs as a table with a status icon (❌ overdue, ⚠️ due soon or warning, ✅ releasable, ❌ stop code) and the action in the last column. Follow "Answer layout" in `SKILL.md`.
