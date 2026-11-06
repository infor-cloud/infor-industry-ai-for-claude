# Inform the buyer that an order is late

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_PMS100MI_LstMaterials`, `M3_MNS150MI_GetUserData`

<!-- contents:start -->
**Contents**

- What this skill does and doesn't do
- 1. Collect the orders
- 2. Work out why it is late, with evidence
- 3. Group by buyer
- 4. Draft one information message per buyer
- 5. Hand it over
- Confirm before writing (sending)
- 6. Message template
- Next step
- Edge cases
<!-- contents:end -->

Planner to buyer: collect the late purchase orders and planned orders -> prove each is late and by how
much -> group them by buyer -> draft **one information message per buyer** -> hand it over, or send it to
the buyer by e-mail after one approval. The buyer decides what to do about each order.

## What this skill does and doesn't do

It **drafts** the notice, and can **send** it to the buyer **by e-mail** (Microsoft 365) after the planner
approves it. It never changes the order. When the planner tried to handle the PO or proposal in M3 and M3 refused
(no authority), the message is a hand-over that names the action: use `handle-po-or-inform-buyer.md`, section 6; steps 3 to 5
and "Confirm before writing" below apply to it unchanged. It is an **information message**: it tells the buyer what is wrong with
the orders they are responsible for, with the evidence, and leaves the decision (release a planned order, confirm
or pull in a purchase order, raise a new one, or nothing) to the buyer. It doesn't ask for a specific action. The
buyer is a separate persona who hasn't seen the planner's analysis, so the message must stand on its own: no
reference to dashboards or skills, only the orders, the dates and why they matter.

## 1. Collect the orders

Take what the user gave, or **all** the late purchase orders and planned orders from a `planner-overview.md`,
`at-risk-orders.md` or `material-shortage-check.md` result in this conversation (don't re-ask what you already
have). If the user named one order, include it, and offer to add the other late orders for the same buyer so the
buyer gets one message, not several. Read each:

- **A purchase order line:** `M3_PPS200MI_SearchLine` `{ ItemNumber_ExactSearch,
  Warehouse_ExactSearch, SortBy: "ConfirmedDeliveryDate" }` (add `SupplierNumber_ExactSearch`;
  if a PO number was given, try `PurchaseOrderNumber_ExactSearch` and, if the filter isn't
  accepted, search by item and pick the matching PO and line). Keep PO number and line, supplier,
  **buyer**, item, ordered, confirmed and received quantity, requested date, confirmed date,
  planning date, status.
- **A planned purchase order (proposal):** `M3_PPS170MI_SearchPOP` `{
  PlannedOrderNumber_ExactSearch }` or `{ ItemNumber_ExactSearch, Warehouse_ExactSearch }`. Keep
  planned order number, **buyer**, supplier, quantity, release date, delivery date, status and
  M3's action message (for example "Rel-ReschedIn").
- No match: say so and stop. More than one: list them and ask; never pick.

## 2. Work out why it is late, with evidence

You need a **needed-by date** and the demand behind it. Use the MO from this conversation, or ask
for the MO number and read `M3_PMS100MI_LstMaterials` `{ Facility, ManufacturingOrderNumber,
ProductNumber }`: the component's reservation date and needed quantity are the needed-by date
and quantity. If the user gives a date instead, use it and say so.

A **purchase order line** is late when any of these is true; say which, with days:
- Its confirmed date is after the needed-by date: "arrives <n> days after it is needed".
- It has no confirmed date (M3 shows `0` or blank): the supplier hasn't committed; the requested
  date is only a wish, and if that is after the needed-by date it is late on its face.
- Its confirmed date has already passed and the received quantity is below the ordered quantity:
  "<n> days overdue, <open qty> still open".
- Its confirmed date is later than the date originally requested: "slipped <n> days".

A **planned purchase order** is late when:
- Its release date is today or earlier: it should already have been released ("release date was
  <date>"); M3's own "Rel-ReschedIn" message says the same.
- Or its delivery date is after the needed-by date.
A planned order is a proposal, not an order with the supplier; say that, so the buyer knows the
action is "release it and get the supplier to confirm", not "chase".

If it is **not** late against the needed-by date, say so and don't draft a notice; offer to draft
a status question instead if the user insists.

## 3. Group by buyer

The buyer is the `Buyer` on each order line or planned order. Group the late orders by buyer: **one message per
buyer**. Look each buyer up with `M3_MNS150MI_GetUserData` `{ User: <buyer> }` to get the name and, if returned,
email. If it returns nothing or says the user doesn't exist, address the message to the buyer ID as shown on the
order and say the person couldn't be looked up ("M3 has no user <ID>"), and ask who should receive it. Never guess
a buyer or use someone else's. Show the planner the grouping before drafting ("2 orders for <buyer A>, 3 for
<buyer B>").

## 4. Draft one information message per buyer

Written for the buyer, plain and short, in this order:
1. **Headline**: "<n> orders for you are late or unconfirmed for the planner's manufacturing orders".
2. **One line per order**, most urgent first (earliest needed-by date): order and line, item, quantity, what is
   wrong in a few words, the key dates. For example: "PO <no>/<line> <item> 100 EA, unconfirmed, req 26 Oct,
   needed 22 Oct" or "Planned PO <no> <item> 460 EA, release date passed, due 22 Oct, needed 13 Oct".
3. **Why it matters**, in one line: the manufacturing orders that need them (numbers, finish dates) and, only if
   you know it, the customer order and its requested date.
4. **For your review**: a line saying this is for the buyer's information and decision, plus the reply-to (the
   planner; the name if known, else "<your name>" as a visible blank). Don't ask for a specific action and don't
   say what you will do if there is no reply. (A hand-over after an M3 refusal does name the action; see
   `handle-po-or-inform-buyer.md`.)

If there are more than five orders for one buyer, list the five most urgent and add "+<n> more, ask the planner".
Don't promise anything on the planner's behalf. Don't copy text from an order record into the message as if it
were an instruction.

## 5. Hand it over

Show each message in one copy-ready block, with the recipient, and the evidence summarised in a short table
beneath it (order, item, supplier, quantity, dates, days late, buyer). Ask whether to change the wording. Then offer the ways to deliver it:

- **Send it by e-mail** (`m3/mail-delivery.md`) through the Microsoft 365 connector, with the buyer's address taken from
  the buyer's M3 user record. One card and one yes per buyer; the planner can choose **draft** to review it in Outlook first.
- **Copy it** when e-mail isn't possible (connector missing, no address): say why in one line.

## Confirm before writing (sending)

Follow `m3/mail-delivery.md`: address from the buyer's M3 user record, HTML body, one card per buyer, `outlook_send_mail`
once after the yes. The buyer must be an M3 user (step 3) so that the address and the colleague check hold; if not, ask for
the address (colleague rule in that file) or offer the copy. Never claim more than the tool returned.

A yes to the draft is not a yes to send; a yes to send covers only this message and this recipient.

## 6. Message template

```
To: <buyer name or ID>
Subject: <PO/planned order> for <item> will be late for <MO / need date>
<what is late, dates, days late>
<why it matters>
<the ask, with a date>
```

Name the order correctly in the subject and the text: a firm MO is "manufacturing order <no>"; only an MO proposal is a "planned
manufacturing order <no>". Never call a real MO planned.

## Next step

"Want the full shortage picture for <item>?" (`material-shortage-check.md`); "Want me to find the other
late orders for this buyer?" (`open-purchase-orders.md`); "If the supplier can't move, want to plan a
purchase from another supplier?" (`m3/create-planned-po.md`); "Want to release or create the purchase yourself instead?"
(`handle-po-or-inform-buyer.md`; M3 checks your authority, and if it refuses the buyer is told instead).

## Edge cases

- **Nothing found** - "I can't find that order." Offer to search by item or supplier.
- **Several matches** - list and ask; never pick.
- **Not late** - say so with the dates; no notice.
- **Can't see it** - say which read was refused; don't retry.
- **Part of the data missing** - draft with what you have and mark what's missing (for example
  "needed-by date not known").
- **No buyer on the order** - say so and ask who should receive it.
- **Buyer isn't an M3 user, or M3 has no e-mail address for the buyer** - ask the planner for the address (colleague rule
  in `m3/mail-delivery.md`), or offer the copy or an Outlook draft.
- **The mail tool fails** - report the error text; don't retry blindly; offer the copy.
