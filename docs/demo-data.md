# Production planner demo data

The `m3-production-planner-demo-cleanup` skill prepares an Infor M3 tenant for a production planner demo and resets it afterwards. It creates the customer order a demo starts from. Afterwards it deletes the orders, proposals and temporary shift patterns the demo left behind, so the same demo can run again.

It is a setup tool for the people who prepare and run demos. It is not part of the Infor Industry AI plugin and is installed separately, from [`demo/m3-production-planner-demo-cleanup`](../demo/m3-production-planner-demo-cleanup).

> [!WARNING]
> The cleanup deletes customer orders, manufacturing orders (MOs), MO proposals and shift pattern adjustments, and a delete can't be undone. Use the skill only on a demo or test tenant, and install it only for the people who run demos.

## Commands

| Say | What happens |
|---|---|
| `Set up demo data for swap material for item <item> and customer <customer>` | Creates one customer order of 10 of the item, requested for delivery 7 working days from today |
| `Set up demo data for double shift for item <item> and customer <customer>` ("extra shift" works too) | Creates one customer order of 10 of the item, requested for delivery on the Wednesday of next week, or of the week after when today is Thursday to Sunday |
| `Clean production demo data for item <item>` | The full reset: deletes the item's customer orders, its MOs and MO proposals and those of its lower levels, and the temporary shift patterns on the work centers they use, then re-creates those work centers' capacity |
| `Delete all COs for item <item>` | Deletes the item's customer orders, or only the item's lines when an order also has other items |
| `Delete all MOs for item <item>` | Deletes the MOs and MO proposals of the item and of its lower levels |
| `Delete shift pattern for <work center>` | Deletes the work center's temporary shift pattern adjustments and re-creates its capacity |

"Remove", "clear", "reset" and "clean up" work as well as "clean" and "delete". The item, customer or work center has to be typed in the command. Claude never takes it from earlier in the conversation, and asks once if it's missing.

Every command runs the same way. Claude reads what exists and shows one card that lists exactly what it will create or delete and what it will leave. It acts only after a yes to that card. It reads each record again just before changing it, and reads back afterwards to report what M3 now shows.

## Setting up demo data

Both scenarios create one customer order with one line:

- **Facility and warehouse:** the signed-in user's, from their M3 user settings.
- **Quantity:** 10, in the item's basic unit of measure.
- **Order type:** the customer's default customer order type (CRS610). If the customer has none, Claude asks which one to use.
- **Responsible:** the signed-in user.
- **Price:** from M3. If the item has no price, M3 refuses the order and Claude says so.

The requested delivery date is counted from the M3 system date:

- **Swap material:** 7 working days after today, counting Monday to Friday. Public holidays aren't skipped.
- **Double shift:** the Wednesday of next week when today is Monday, Tuesday or Wednesday, otherwise the Wednesday of the week after.

Nothing else is created: no MOs, proposals, purchase orders or shift patterns. M3's own planning may add supply for the order afterwards. In the double shift scenario, the planner adds the temporary shift pattern during the demo itself.

If the item already has an open customer order in the user's facility (a line below status 66), the setup creates nothing and asks you to clean the item's demo data first.

## Cleaning up

The full reset reads everything before it shows its card, because a deleted MO can no longer be read for the work centers it used. One card and one yes cover the whole reset. After the yes, it works in this order:

1. **Customer orders for the item.** An order whose lines are all for the item is deleted (status 90). An order that also has other items keeps them, and only the item's lines are deleted.
2. **MOs and MO proposals** of the item and of its semi-finished items, up to 6 levels down the product structure, top level first.
3. **Temporary shift pattern adjustments** on the work centers those MOs and proposals used.
4. **Capacity** of those work centers, re-created for the dates the orders and adjustments covered.

The reset never changes:

- Purchase orders.
- The normal shift pattern of a work center. Only temporary adjustments on top of it are deleted.
- Customer order lines that are delivered or invoiced (status 66 or higher), or that are in another facility.
- Orders and work centers that aren't on the card. Other MOs on the same work centers aren't rescheduled, and they lose any extra capacity the reset deletes.

M3 doesn't delete an MO that has started or has reported output or stock movements. Claude lists such MOs with M3's message, and they have to be closed or reversed in M3.

## A demo, start to finish

1. Set up the data, for example with `Set up demo data for double shift for item <item> and customer <customer>`. Check the card and reply yes.
2. Run the demo with the production planner skill, for example: "Give me all production orders at risk and recommendations to mitigate the risks."
3. Reset afterwards with `Clean production demo data for item <item>`. Check the card and reply yes.
4. Set up again before the next demo.

Use an item and a customer that your demo tenant has set up for the scenario.

## Before you start

- **A demo or test M3 tenant** with the M3 connector set up, as the [setup guide](setup.md) describes.
- **The tools the skill uses.** All 28 are in the Infor Industry AI tool set. A user with the IFS role `M3GENAI-BE-Administrator` can check that they are in place, from the repository root (the [GenAI Gateway tool scripts](../scripts/genai-gateway/README.md) describe the `.ionapi` file the script needs):

  ```bash
  python3 scripts/genai-gateway/gg.py check --skills demo
  ```

  Nine of the tools change data, and five of those delete: `M3_OIS100MI_DelHead`, `M3_OIS100MI_DelLine`, `M3_PMS100MI_DltMO`, `M3_PMS170MI_DelPlannedMO` and `M3_PDS010MI_DelShiftPatAdj`. The others are `M3_OIS100MI_AddBatchHead`, `M3_OIS100MI_SndBatchLine`, `M3_OIS100MI_Confirm` and `M3_PDS010MI_CrtCapacity`. `M3_PMS100MI_DltMO` is used only by this skill, not by the plugin. If a tool is missing or disabled, Claude says which one and stops before the step that needs it.
- **M3 authority.** Tool calls run as the signed-in user, who needs authority for the M3 programs behind the tools (see [M3 roles and permissions](setup.md#m3-roles-and-permissions)).
- **Skills turned on in Claude.** Skills need code execution. On Team and Enterprise plans, a Claude Owner or Primary Owner checks that **Cloud code execution and file creation** and **Skills** are on in **Organization settings** > **Plugins & skills**, on the **Policy** tab. On other plans, each user turns on code execution in **Settings** > **Capabilities**.
- **The demo data it was built for.** The skill expects the normal shift pattern of a work center to start at 07:00 (shift 001, 07:00 to 11:00). It finds temporary adjustments by reading each work center's capacity at 07:00, so on a tenant with other shift times it may not find them.

## Install

Install the skill only for the people who run demos.

**Claude apps**

1. Zip the folder, with the folder itself at the root of the zip:

   ```bash
   cd demo && zip -r m3-production-planner-demo-cleanup.zip m3-production-planner-demo-cleanup
   ```

2. In Claude, go to **Customize** > **Skills**, click **+**, then **+ Create skill**, and select **Upload a skill**.
3. Choose the zip file.

The skill appears in your skills list, where you can turn it off between demos. Don't add it in **Organization settings** > **Plugins & skills**, because a skill added there goes to every user in the organization.

**Claude Code**

```bash
cp -R demo/m3-production-planner-demo-cleanup ~/.claude/skills/
```

Start a new conversation after installing.

## Troubleshooting

| What you see | What to do |
|---|---|
| "There are already customer orders for ..." when you set up | Clean the item's demo data first, then set up again. |
| M3 refuses the new order with "Sales price must be entered" | Give the item a price in M3, or use another item. |
| An MO is left after the cleanup, with M3's message | It has started or has reported output. Close or reverse it in M3. |
| Claude says a tool is missing | The `M3GENAI-BE-Administrator` enables the tool in GenAI Gateway, or sets up the missing tools with the [GenAI Gateway tool scripts](../scripts/genai-gateway/README.md). |
| M3 refuses a call with a security or authority message | Connect the user to an M3 role that gives access to the program (MNS410). |
| M3 still shows the old shift after a shift pattern delete | M3 can take a moment to update the capacity. Read it again later. |

## Support

For help, contact Infor Support through [Infor Concierge](https://concierge.infor.com).
