# Buyer: messages

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PPS200MI_GetHead`, `M3_OIS100MI_GetLine`, `M3_OIS100MI_GetOrderHead`, `M3_CRS610MI_GetBasicData_CustomerName`, `M3_MMS200MI_GetItmWhsBasic`, `M3_PPS001MI_FinishMark`, `M3_MNS150MI_GetUserData`

<!-- contents:start -->
**Contents**

- What this does
- Rules for every message
- Offer the message in Outlook
<!-- contents:end -->

<!-- layout: reference -->

## What this does

Writes one message per recipient, from the facts the buyer already has in this conversation (read from M3 in this run).
Recipients and wording follow below. The decision about what to ask for comes from `delayed-po.md`; recording a
confirmation in M3 is in `po-actions.md`. After a drafted message, the buyer is offered to have it put in Outlook as a draft (last section).

## Rules for every message

Write **one message per recipient**, never one combined message.
Use the buyer's name from `M3_MNS150MI_GetUserData_CurrentUser` (`UserName`) as sender. Use the facts read from M3 in
this run, give every amount with its currency (PO currency from `M3_PPS200MI_GetHead`, customer order currency from
`M3_OIS100MI_GetLine`), write dates as YYYY-MM-DD and ask for a reply **by a date** (default: two days ahead; tell the
buyer it can be changed). Say plainly what is not known; never state a conclusion M3 does not support (for example
"the quantity will differ": say "may differ"). Keep each message under about 15 lines. Do not put prices in messages
to order or manufacturing owners. If the recipient's name is not in M3, write "Hi," and tell the buyer the name or
e-mail is missing. Name the responsible user id you found.

Before drafting, read the order headers (`M3_OIS100MI_GetOrderHead`) and, for a customer order, the customer name
(`M3_CRS610MI_GetBasicData_CustomerName`, with the customer number from the header). If a header is Deleted or closed, or the material
plan no longer lists the order, **re-run the impact check** and use the current orders. Orders change between sessions.

**1. To the customer order responsible** (`ResponsibleUser` from `M3_OIS100MI_GetOrderHead`), for a substitute:

> Subject: Customer order <order>: can the customer accept a different <product> instead of <item>?
> Customer order <order> line <line> (customer <no>, <customer name>, <contact>) has <qty> pcs of <item>, <name>, requested for
> <date>. We cannot deliver it: there is no stock of <item> in any warehouse, and the next supply is planned for
> <date> at the earliest. We have a similar <product> in stock in warehouse <wh>: <substitute 1, name>; <substitute 2,
> name>. **Please note that the sizes differ: <new size> against <old size>.** Could you check with the customer
> whether one of these is acceptable instead of <item>, and let me know? If it is, please change the order line. If
> not, the customer will need a new date, which would be <date> at the earliest.

**2. To the manufacturing order responsible** (the responsible of the item/warehouse of the MO's product: `M3_MMS200MI_GetItmWhsBasic` with `ItemNumber` = the MO product and `Warehouse` = the MO warehouse, field `ResponsibleUser`),
for a substitute:

> Subject: MO <no> / <no>: change material from <item> to a <product> in stock?
> Manufacturing orders <list> (product <product>, <qty> pcs each) each need <qty> pcs of <item>, <name>. There is no
> stock of <item> in any warehouse, and the next supply is planned for <date> at the earliest. MO <no> should have
> started on <date>, and MO <no> is due on <date>. I suggest changing the material on both orders to a similar
> <product> that is in stock in warehouse <wh>: <substitute 1>; <substitute 2>. **Please note that the sizes differ:
> <new> against <old>, so the quantity needed per product may differ too.** Could you choose which one fits and the
> quantity per unit, change the material on the MOs, and let me know? If the material cannot be changed, please tell
> me, and the orders will wait until <date>.

**Who is "the customer order responsible"?** `ResponsibleUser` from `M3_OIS100MI_GetOrderHead`. **If that is the buyer himself**
(this happened in tests), write to the **salesperson** on the order (`Salesperson`) instead, who deals
with the customer, and say which field you used. If the person is not an active M3 user (M3 rejected one salesperson code as a user in
tests), say so and ask the buyer who covers that customer.

**2b. To the salesperson / customer order responsible about a late order** (the supply is confirmed, but after the need date):

> Subject: Customer order <order>: <item> arrives <date>, please inform <customer name>
> Customer order <order> line <line> (customer <no>, <customer name>) has <qty> pcs of <item>, <name>. The requested delivery date was <date> and
> the order is worth <value> <currency>. We have no stock of <item>, and the supplier has now confirmed delivery to our warehouse
> <wh> on <date>, full quantity (PO <no>). We cannot ship before the goods are received, so the order will be late. Could you tell
> the customer, and let me know by <date> which delivery date you agree with them? Once you have, the date on the order line can
> be updated to match.

Use the order value only if it was read; if a value is for the whole order and not the line, say "order value".

**3. To the supplier, asking for a confirmation** (sent line without confirmation, date passed):

> Subject: PO <no> line <line>, <item>, <qty> pcs: please confirm date
> Purchase order <no>, line <line>: item <item>, <name>, <qty> pcs at <price> <currency> per piece (<amount>
> <currency>), delivery warehouse <wh>, terms <terms>. The requested date was <date> and we have not received a
> confirmation. Could you please confirm by <date>: 1. That the order is received and accepted at <qty> pcs and
> <price> <currency> per piece. 2. Your confirmed delivery date to our warehouse. If you cannot deliver, please tell us so that we can
> plan around it.

**4. To the supplier, asking for earlier delivery** (the order that covers the shortage). Send it only after the PO has
been sent to the supplier (a stopped PO first has its stop removed by the buyer, then is printed and sent):

> Subject: PO <no> line <line>, <item>, <qty> pcs: earliest delivery date please
> Purchase order <no>, line <line>: item <item>, <name>, <qty> pcs at <price> <currency> per piece, delivery warehouse
> <wh>, terms <terms> (agreement <no>). Our requested date is <date> and our system plans the goods in on <date>. We
> have production and customer orders waiting for this item since <first need date>, so we ask for the earliest
> delivery you can offer, even in part. Could you please confirm by <date>: 1. That the order is received and
> accepted at <qty> pcs and <price> <currency> per piece. 2. Your confirmed delivery date. 3. The earliest date for a
> first partial delivery, and the quantity.

Do not add lines about collection or transport unless the PO terms say so (EXW means we collect, FOB does not mean
the same): leave transport out unless the buyer asks.

**5. To the original supplier after option D2** (a new PO went to an alternate supplier, and the original line was then
reconfirmed, deleted or finish marked). Ask the buyer first: *"Shall I draft a message to <supplier> about this?"*, and
draft only on a yes. Use the variant that matches what was done:

> Subject: PO <no> line <line>, <item>: <new date and quantity noted | line cancelled | remaining quantity cancelled>
> **Reconfirmed:** Purchase order <no>, line <line>: item <item>, <name>. We note your new delivery date <date> to our
> warehouse <wh> for <new qty> pcs, and we have confirmed the line on that date and quantity. <If finish marked: We will
> not expect the remaining <rest> pcs on this line, so please do not deliver them.> Please confirm by <date> that this is
> correct.
>
> **Deleted, or finish marked in full:** Purchase order <no>, line <line>: item <item>, <name>, <qty> pcs. Because of the
> delay we have covered this need elsewhere and no longer need this line. Please treat the line as cancelled and do not
> deliver it. Please confirm by <date> that you have noted this.

Say plainly to the buyer if the order had already been sent (status 20 or higher): the delete or the finish mark in M3 does
not tell the supplier, so this message is how they find out. Nothing is sent.

**6. To the supplier about cancelled lines** (after any `M3_PPS001MI_FinishMark`, whether or not option D2 was involved;
`po-actions.md`, section 5). The skill **suggests this e-mail itself** right after the read-back: *"Shall I draft an e-mail to
<supplier> about the cancelled line(s)?"* Draft only on a yes. One message per supplier, listing **every line finish marked in
this conversation** for that supplier (a table when there is more than one line). Take the supplier name from the PO header
(`M3_PPS200MI_GetHead` or `SearchHead`); the open quantity is ordered minus received, as read back; the confirmed date is the one
on the line before the finish mark. Use only values read from M3; write "not available" for what M3 did not return.

> Subject: PO <no>: cancelled line(s) <line list>, please do not deliver
> Hello <supplier contact or "team">,
> We are cancelling the open quantity on the following line(s) of purchase order <no>. Please do not deliver them.
>
> | Line | Item | Cancelled quantity | Previously confirmed date |
> |---|---|---|---|
> | <line> | <item> · <name> | <open qty> <uom> | <date or "none"> |
>
> <If part of the line was already received:> The <received qty> pcs already delivered stand and will be invoiced as normal.
> <If other lines on the PO stay open:> The other lines on this order are not affected.
> Please confirm by <date> that you have noted the cancellation and that nothing is in transit. If goods have already been
> shipped, please tell us the quantity and shipping date so that we can agree what to do.

Do not give a reason unless the buyer supplies one, and do not mention prices, penalties or claims. Tell the buyer when the
PO is at status 20 or higher that this e-mail is the only way the supplier finds out. Nothing is sent: the buyer reviews it
and sends it from Outlook.

## Offer the message in Outlook

After you show a drafted message (any of the variants above), offer to put it in the buyer's Outlook drafts. The offer is the question in the "Next:" line. This only creates a draft; the buyer reads, edits and sends it from Outlook.

- **Only when Microsoft 365 mail is connected.** Before the first offer in a conversation, load `outlook_create_draft` with one tool search by exact name (the connector prefix differs per install). If the tool is not there, or the user is not signed in to Microsoft 365, make no offer and say nothing about it (shared rule: other connectors are optional). Don't search again in the same conversation.
- **The offer is one line:** "Shall I put this in your Outlook drafts?" Add the recipient when it is known ("to <name>, <address>"), or "no recipient set, you add it in Outlook" when it is not. When several messages were drafted, name them all in the one offer.
- **A yes creates the draft:** `outlook_create_draft`, once per message, with:
  - `subject`: the subject line of the draft, without the word "Subject:", at most 255 characters.
  - `body` and `bodyType` = `html`: the message as it was shown in chat, with only `<p>`, `<br>`, `<b>`, `<ol>` or `<ul>` with `<li>`, and a small `<table>` if the message has one. The tool rejects anything else (images, styles, spans, scripts). Start with the greeting, put the numbered questions in a list, and end with "Best regards," and the buyer's name (`UserName`). No icons, no signature block (Outlook adds none to a draft; add one only if the buyer gives it), and no mention of this chat or of the skill.
  - `to`: only an address M3 gave. For a colleague (the customer order responsible, the salesperson, the MO responsible) read `M3_MNS150MI_GetUserData` with `User` = that user id and take `EmailAddress`. For a supplier or a customer this skill reads no address: leave `to` out and say so, unless the buyer types one in the chat. If M3 returns no address for a colleague, leave `to` out and say so. **Never guess an address** from a name, a pattern or an earlier mail.
  - No `cc` or `bcc` unless the buyer asks.
- **Draft only. This skill never sends e-mail.** Never call `outlook_send_mail` or `outlook_send_draft`. A message to a supplier or a customer leaves only when the buyer sends it from Outlook.
- **A yes covers the messages named in the offer.** If the buyer changes the wording, show the changed message again and offer again: the earlier yes does not carry over.
- **Report only what the tool returned:** the draft is in the Drafts folder of the Outlook account that is signed in, with the link the tool gives (`webLink`), who it is addressed to (or that no recipient is set), and that nothing has been sent. Do not say the recipient got or read anything.
- **On an error** (not signed in, rate limit, HTML rejected): say it plainly with the error text and keep the message in chat. If the tool rejects the HTML, remove what it names and try once more. For any other error do not retry blindly: a draft may have been created, so ask the buyer to check the Drafts folder first.
- It changes nothing in M3, so the orders and POs stand as the earlier read-back showed.
