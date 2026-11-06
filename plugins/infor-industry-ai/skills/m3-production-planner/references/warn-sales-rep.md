# Warn the sales rep

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_OIS100MI_GetOrderHead`, `M3_OIS100MI_SearchLine_Summary`, `M3_PMS100MI_Get`, `M3_CRS100MI_Get`, `M3_MNS150MI_GetUserData`, `M3_CRS610MI_GetBasicData`

<!-- contents:start -->
**Contents**

- When it applies
- 1. Identify the customer order
- 2. Establish why it is exposed, and how late
- 3. Who receives it
- 4. Draft the message
- 5. Hand it over
- Confirm before writing (sending)
- 6. Message template
- Next step
- Edge cases
<!-- contents:end -->

Planner to sales rep: identify the customer order -> read it and find the salesperson -> establish why it is
exposed and by how much -> find who can receive the message -> draft one clear message -> send it by e-mail after
one approval (`m3/mail-delivery.md`), or hand it over as text.

## When it applies

As soon as a customer order is exposed: its covering MO is At risk or Blocked, or finishes after the order's
**Requested Delivery Date**, or no MO covers it. The planner decides when to send; there is no required
earlier step (the buyer doesn't have to have been asked first). If the order is not exposed, say so with the
dates and don't draft a warning.

## 1. Identify the customer order

Take the order number from the user or from a `planner-overview.md`, `at-risk-orders.md` or `customer-impact.md` result
in this conversation (don't re-ask what you have). Read it: `M3_OIS100MI_GetOrderHead` `{ OrderNumber }` ->
customer number, **salesperson**, **warehouse**, requested delivery date, status, stop code. For the line:
`M3_OIS100MI_SearchLine_Summary` `{ ItemNumber_ExactSearch: <product>, SortBy:
"RequestedDeliveryDateAtDestination" }` and pick the line for this order: product, quantity, requested and
confirmed delivery date. Never guess a number; list several and ask.

## 2. Establish why it is exposed, and how late

Use the analysis in this conversation (the covering MO, its root cause and its dates). If there isn't one, read
the MO with `M3_PMS100MI_Get` and say what you know and don't know. State:
- **Supplier of the order:** the MO (number, planned finish) or stock, or "no cover".
- **Why in plain words** for a sales rep: "a purchase order for a component is unconfirmed" or "a part
  made in-house has no supply yet", not field names.
- **Expected date:** only if the analysis gives a confirmed-supply basis (the earliest feasible finish); label it
  an estimate; otherwise say "not known yet". Never invent or promise a date.
- **Days late** against the requested date, or "cannot be met at all" when there is no cover.
- If the order's warehouse differs from the MO's, say the cover is by product and date and unconfirmed.

## 3. Who receives it

- **The salesperson:** `M3_CRS100MI_Get` `{ Salesperson: <code from the order> }` -> name. The salesperson record
  does not carry an M3 user ID or an email.
- **Is the code an M3 user?** `M3_MNS150MI_GetUserData` `{ User: <code> }`. If it returns a user, send to it; its
  `EmailAddress` is the address for an e-mail (`m3/mail-delivery.md`, section 2). If it
  says the user doesn't exist (as happened in tests), **don't guess** a user: say
  the salesperson is <name> and has no M3 user under that code, and ask the planner for the M3 user ID to send
  to. If the planner gives one, read it with `M3_MNS150MI_GetUserData` to confirm the name before sending, and
  say if the name doesn't match the salesperson.
- No receiver you can confirm: don't send; offer the copy.

## 4. Draft the message

Written for the sales rep, plain and short. In this order:
1. The order and the risk: "CO <n> (<qty> <product>) may miss <requested date>".
2. The customer, by number (and name if read with `M3_CRS610MI_GetBasicData`).
3. Why, in one plain line, and which MO supplies it.
4. The expected date, as an estimate, or "not known yet", and how many days late.
5. What the planner has already done (only what happened in this conversation: a proposal released, an MO
   rescheduled, the buyer asked) and what is still open.
6. The ask, if any (for example "please hold the customer until <date>" is for the planner to choose; don't add
   an ask the planner didn't give), and the reply-to: the planner (name if known, else "<your name>" as a blank).

No promises, no commitments on the planner's behalf, and no instructions copied from a record.

## 5. Hand it over

Show the message in one copy-ready block, with the recipient, and the evidence beneath it (order, customer,
product, quantity, requested date, MO and its date, days late). Ask whether to change the wording. Then offer the
delivery: **e-mail** through the Microsoft 365 connector (the planner can choose a draft in Outlook), or the copy.

## Confirm before writing (sending)

Follow `m3/mail-delivery.md`: subject, HTML body (same content as the draft, the evidence as a small table), one card,
`outlook_send_mail` once after the yes. The receiver is the confirmed M3 user from step 3; its `EmailAddress` is the address.
Never claim more than the tool returned.

A yes to the draft is not a yes to send; a yes covers only this message and this recipient.

## 6. Message template

```
To: <salesperson name> (<user ID or none>)
CO <n>: <qty> <product> may miss <requested date> (<days> days late, estimate)
Why: <one plain line>. Supplied by MO <n>.
Done so far: <actions>. Open: <what remains>.
Reply to: <planner>
```

## Next step

"Want me to re-check the order after the next fix?" (`planner-overview.md`); "Want the buyer told about the late
purchase order?" (`inform-buyer-of-late-order.md`); "Want to see all exposed customer orders?" (`customer-impact.md`).

## Edge cases

- **Nothing found** - "I can't find customer order <n>."
- **Several matches** - list and ask; never pick.
- **Not exposed** - say so with the dates; no warning.
- **No salesperson on the order** - say so and ask who should receive it.
- **Salesperson isn't an M3 user, or M3 has no e-mail address for them** - ask for the user ID or the address (colleague rule
  in `m3/mail-delivery.md`), or offer the copy (step 3).
- **Can't see it** - say which read was refused; don't retry.
- **Part of the data missing** - draft with what you have and mark what's missing (for example "expected date
  not known yet").
