<!-- Part of references/delayed-po.md (UC3). Read the index first. -->

## 4. Recommendations with actions

Choose one best mitigation option and one fallback, and present them as **Recommendations with actions**. Use this order of judgement:

1. Does it protect the order with the earliest need date and highest priority or value?
2. Does it arrive before the need date? (If not, it is not a solution; call it mitigation.)
3. Cost difference compared with value protected.
4. Risk and number of steps.
5. Does it hurt other orders? State who and by how much.

Write the answer in this shape:

- **The overall impact in two sentences**, including coverage ("this line covers 10 of 725 pcs").
- **A table of the mitigation options**: status (✅ possible · ❌ not possible · ⚠️ needs approval, as in `6-show-it-and-next-step.md`) and
  arrival against the need dates. The table always has all five rows, A to E: an option that cannot work gets its row with the reason (no stock, no relation, no agreement, too late), never "not checked". When two options arrive in time, say which one needs no approval.
- **Recommendations with actions:** recommendation 1 is the best mitigation option, recommendation 2 the fallback.
  Under each one, list its **actions in order**, each with who does it. An action this skill can carry out or draft
  (confirm the line, a distribution order proposal, a new PO to an alternate supplier, a material swap, a message draft, a reschedule) is a
  row in the actions table that starts with its verb and carries its option letter (`m3/action-buttons.md`); a call to the supplier or an approval is a plain-text step. The
  verbs are **Create** (a distribution order proposal, a new PO to an alternate supplier; for the new PO, D1 also offers to **Confirm** it at once; the original line gets its own step D2 with **Confirm line** (reconfirm with the new date and quantity; with `FinishMark` = 1 when a smaller quantity drops the rest), **Delete** (status 15 to 20 only) or **Finish mark** (the full line, status 35 or above), see `3d-alternate-supplier.md`), **Swap** (the material on an MO: one action per
  affected MO, `3b-substitutes.md` step 7) and **Draft** (a message); never "Prepare". No action panel. A recommendation built on a
  substitute always lists its Swap action when the conditions in `swap-material.md` hold, next to the plain-text action
  "get engineering or quality approval", also when it is the fallback.
  A stopped PO (status 12): the buyer removes the stop himself in M3 (no tool for it, and no separate approver is assumed), so do not ask for authorization. Re-read the line with `SearchLine`: if it is no longer stopped (for example 15 ReadyForPrintout), the next step is to print and send it to the supplier, and the supplier message goes with it.
- **Option C actions.** The **Create** row for a distribution order proposal names the status: firm (status 20) by default, and tells the buyer that "C1 release" creates it already released (status 60), see `3c-distribution-order.md`. Offer the release variant in every option C recommendation, as the fallback too, and never present it as the default. The planner's release is the next row, a plain-text step marked "not needed after C1 release".
- **If the best mitigation option is not approved**, say which orders will be late and by how many days, and who
  should be warned (customer orders first).
- **Limits that matter:** only a limit that changes the recommendation (for example a free quantity that rests on the stock balance only)
  goes in one line in the main answer or in "Next:". Do not add a "What M3 cannot tell us" section. Do not write that the PO has no currency: read it from the PO header or the agreement (step 1,
  "Currency"). Leave the cost difference out only when neither gives a currency.
- **Actions that would change M3**, listed separately, each with the exact change. Nothing is done until the
  buyer confirms that exact action. Never delete, except as described in "Replace the item on a PO line" (`po-actions.md`) and, in step D2 after a new PO to an alternate supplier exists, the original line at status 15 to 20 (`create-new-po.md`, "The original line").
- **When the buyer has given the supplier's date, offer to confirm the line in M3 with it** (`po-actions.md`,
  "Confirm a PO line"): the date as the arrival date, the quantity, the price if given, and what the confirmation does
  to the planned date and the orders. Do not offer a message to the supplier to check the date.
- **For a line without a confirmation and without a supplier date, offer both ways:** (a) draft a message to the
  supplier asking for the confirmation (not sent), or (b) the buyer calls the supplier and then tells you the answer,
  and you **confirm the line in M3 in the chat** (`po-actions.md`, "Confirm a PO line").
- **Offer to draft the internal messages** (`messages.md`; in chat, not sent), and a supplier message only when there is no supplier date yet, the buyer wants earlier delivery, or step D2 has just been performed (then ask "Shall I draft a message to the original supplier?" every time): one per recipient, each
  with the PO, item, quantity, dates, what is asked and by when.
