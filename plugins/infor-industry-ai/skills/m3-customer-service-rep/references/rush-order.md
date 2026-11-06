# Customer service rep: rush order (UC2)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_CRS610MI_SearchCustomer`, `M3_CRS610MI_GetBasicData`, `M3_CRS610MI_LstAddresses`, `M3_MMS200MI_SearchItem`, `M3_OIS100MI_AddBatchHead`, `M3_OIS100MI_SndBatchLine`, `M3_OIS100MI_Confirm`, `M3_OIS100MI_LstErrMsgOrder`, `M3_OIS100MI_SearchHead_LimitedOutput`, `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_OIS120MI_GetCOStopInfo`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS120MI_AllocateOrdLine`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get`, `M3_CRS420MI_Add`, `M3_CRS420MI_AddFreeText`

## What this does

A customer calls and needs an order, often several lines, by a requested date. The rep types the call into the chat. You do the checking and the
legwork; the rep approves anything that creates, moves or costs something. The aim is to meet the requested date by any honest means. If that is
impossible, say so plainly and give the best alternatives. If there is a better way to reach the same goal than the one described here, take it
and explain why.

Show your work at each step.

## Checklist

Work through these in order and confirm each one before you answer. Track them yourself; don't show the checklist in the reply.

- [ ] 0. Who and what: user, company, division, facility and warehouse; the customer (one match, or ask which); the ship-to
- [ ] 1. Order captured and read back, a yes before anything is created; created with the recipe and read back from M3
- [ ] 2. Credit read; a stopped order is not released, and the rep knows which limit stopped it
- [ ] 3. Stock checked per line, here and in the other warehouses; part stock: asked before splitting
- [ ] 4. Supply read: material plan, open purchase and manufacturing orders
- [ ] 5. Buyer alerted where a purchase is needed; nothing bought by the rep
- [ ] 6. If the date can't be met: said in one sentence, with the real alternatives and their dates
- [ ] 7. One summary per line (path, what was done, the date M3 supports and which kind it is, what is open); customer update offered

## 0. Who and what

The current user, company, division, facility and warehouse. The customer by search (one result: use it; several: stop and
ask which). The ship-to address list.

**Tools:** `M3_MNS150MI_GetUserData_CurrentUser`, `M3_CRS610MI_SearchCustomer`, `M3_CRS610MI_GetBasicData`, `M3_CRS610MI_LstAddresses`.

## 1. Capture and create

Collect customer, ship-to, each item and quantity, the requested date and the order type. Read the summary back and get
a yes before creating anything. Use the creation recipe in "Creating the order" below.

**Tools:** `M3_MMS200MI_SearchItem`.

### Creating the order

**Validate (read only):** the customer (basic data), the item in the warehouse, the order type defaults, the stock. The item's basic unit of measure is not
in the item/warehouse record: ask the user.

**Create (writes), the recipe that works:**
1. Create a batch order header (customer, order type, facility, warehouse, requested date, responsible user; an order date and requested date in the past
   backdate the order). It returns a temporary batch number.
2. Add one batch line per line: item, the temporary number, quantity, **the unit of measure** (without it M3 refuses the line), requested date, warehouse.
   The call gives no error even if the line is wrong: M3 validates at confirm. A confirmed delivery date on the line is kept as sent.
3. **Confirm** the temporary number. It returns the firm order number and a status. If it fails, read the batch order's error log. Do not use the lock
   release for this.
4. Read back the lines and the header.

M3 decides the price from the item file or price lists; a price sent on the line is ignored. If the item has no price, M3 refuses the order ("Sales price must
be entered"): say so; do not invent a price. Whether an order is delivered, allocated or left open after creation depends on the order type settings.

**Safety.** Show the full order and get a yes before creating. If a step fails after the header exists, stop and report; delete nothing without a new yes.
After creation, report what M3 shows, not what was sent.

**Tools:** `M3_OIS100MI_AddBatchHead`, `M3_OIS100MI_SndBatchLine`, `M3_OIS100MI_Confirm`, `M3_OIS100MI_LstErrMsgOrder`, `M3_OIS100MI_SearchHead_LimitedOutput`, `M3_OIS100MI_SearchLine_LimitedOutput`.

## 2. Credit

Read the stop code and the credit room. If the order is stopped, **do not release it**. Tell the rep which limit stopped it and that
the promise depends on the credit controller; offer to draft the request. Carry on with stock and supply so the answer is ready when it is released.

**Tools:** `M3_OIS120MI_GetCOStopInfo`.

## 3. Stock, per line

Free stock here covers the line: allocate it (own yes), then remind the warehouse to pick: a rep does not release for picking. Free stock is in another warehouse: a distribution order from that warehouse (`fix-a-line.md`).
Only part is free: say how much and ask whether to split the line; never split on your own. Nothing free: step 4.

**Tools:** `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS120MI_AllocateOrdLine`.

## 4. Supply

Read the material plan for coming supply and the projected balance; read the open purchase and manufacturing orders. If the plan comes
back empty for an item that clearly has supply, say that the call answered nothing; do not conclude there is none.
For a manufactured item look at the bill of materials, raw material, capacity and labor if the tools exist; otherwise draft a request to the planner
with item, quantity and date.

**Tools:** `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get`.

## 5. Buy

The rep does not create planned POs. Alert the buyer (`fix-a-line.md`, "Alert the buyer or planner"). Say "requested from the supplier" until the supplier confirms.

**Tools:** `M3_CRS420MI_Add`, `M3_CRS420MI_AddFreeText`.

## 6. No way to meet the date

Say so in one sentence, then the best real alternatives, each with its date and source: ship what is free now and the
rest later; the full quantity on the earliest supported date; from another warehouse (a distribution order); an alternative item; stock taken from another order (a decision for the
rep). Lead times come from M3, not from memory.

## 7. Close

One summary per line: path, what was done, the date M3 supports and which kind of date it is, what is still open. Offer the customer update.
