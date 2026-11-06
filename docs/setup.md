# Infor Industry AI Connector for M3 – Setup and Reference

## Overview

The Infor Industry AI connector lets Claude look up and act on Infor M3 data, such as customer orders, purchase orders, manufacturing orders, items, stock and customers, through M3 Business Engine (BE) APIs.

M3 GenAI Gateway exposes M3 MI transactions as Model Context Protocol (MCP) tools, and Claude reaches it through Infor ION API Gateway. Each tool wraps one M3 MI transaction, for example CRS610MI GetBasicData. Field names are rewritten from four-character M3 codes to readable names, and status codes can be presented as named values.

This page is for the people who set the connector up and for users who connect Claude to M3. Setting it up involves three roles: a user with the IFS role `M3GENAI-BE-Administrator`, who reviews the tools; a user with the `IONAPI-Administrator` role, who registers Claude in ION API; and a Claude Owner or Primary Owner, who adds the connector to Claude.

The role-based skills for buyers, production planners and customer service reps are a separate install: the Infor Industry AI plugin in this repository. The plugin uses this connector.

### How it works

```mermaid
flowchart LR
    user([M3 user]) --> claude[Claude]
    claude -- "MCP tool call<br/>with the user's token" --> ionapi[Infor ION API Gateway]
    ionapi --> gateway[M3 GenAI Gateway]
    gateway -- "MI transaction<br/>as the signed-in user" --> m3[(M3 Business Engine)]
    claude -. "OAuth sign-in" .-> sso[Infor OS sign-in]
    admin(["M3GENAI-BE-Administrator"]) -- "GenAI Gateway<br/>admin tool" --> tools[("Standard and<br/>customized tools")]
    tools --- gateway
```

1. Each user connects Claude to M3 once, by signing in with their Infor OS account.
2. When Claude needs M3 data, it calls a tool. The call goes to ION API Gateway with the user's access token.
3. M3 GenAI Gateway runs the MI transaction in M3 as that user, so M3 security applies as it does in M3 itself.
4. The result comes back with readable field names, and with only the fields enabled in GenAI Gateway.

## Prerequisites

Before connecting Claude, make sure the following are in place.

- An Infor M3 tenant with Business Engine MI transactions available through the M3 API Gateway (`/m3api-rest/v2`).
- Velocity Suite for that tenant. It includes M3 GenAI Gateway, which provides the MCP endpoints through Infor ION API Gateway.
- A user with the IFS role `M3GENAI-BE-Administrator`, to review and customize tools in the GenAI Gateway admin UI.
- A user with the `IONAPI-Administrator` role, to register Claude as an authorized application in ION API.
- For each person who will use the connector, an M3 user account with authority for the M3 programs whose tools they will call (see [M3 roles and permissions](#m3-roles-and-permissions)).
- On Claude Team and Enterprise plans, a Claude Owner or Primary Owner to add the connector for the organization. On Enterprise, a custom role with **Manage access to Libraries** can also add it. On Free, Pro and Max plans, each user adds it.

No network allow-listing is needed. Claude reaches the tenant through ION API Gateway over the public internet.

## Setup

| Part | Who | Where |
|---|---|---|
| [Part 1: Review the tools](#part-1-review-the-tools-m3genai-be-administrator) | IFS role `M3GENAI-BE-Administrator` | Infor Portal > M3 > **Administration Tools** > **GenAI Gateway** |
| [Part 2: Register Claude in ION API](#part-2-register-claude-in-ion-api-ionapi-administrator) | `IONAPI-Administrator` | Infor OS Portal > **API Gateway** > **Authorized Applications** |
| [Part 3: Add the connector in Claude](#part-3-add-the-connector-in-claude-claude-owner-or-primary-owner) | Claude Owner or Primary Owner | Claude > **Organization settings** > **Connectors** |
| [Part 4: Connect Claude](#part-4-connect-claude-each-user) | Each user | Claude > **Customize** > **Connectors** |
| [Check that it works](#check-that-it-works) | Each user | A Claude conversation |

### Part 1: Review the tools (`M3GENAI-BE-Administrator`)

1. Sign in to Infor Portal with an account that has the IFS role `M3GENAI-BE-Administrator`, and open M3.
2. Under **Administration Tools**, click **GenAI Gateway**.
3. On the **Standard** tab, review the tools that are available. Open a tool to see all of its input and output fields. Agents can use only the fields that are enabled.
4. To change a tool, click **Copy** in the **Details** form. The customized version replaces the standard tool. If you give it a sub-name, it appears as a separate tool.
5. Edit the tool description, enable or disable fields, and change field long names, descriptions, types or enum values as needed. Update any instructions that refer to a renamed field.
6. To turn a customized tool off, disable it. Disabling a customized tool that has no sub-name returns to the standard tool. Standard tools can't be turned off for a tenant.

> [!IMPORTANT]
> A copied or new tool starts disabled. Users don't see it, and the standard tool stays in use, until you enable it.

Customized tools are listed on the **Customized** tab. To create a tool that has no standard version, click **+** in the **Tools** list and enter the **Program**, **Transaction** and optional **Sub-name**, for example `CRS610MI` and `GetBasicData`.

This guide describes the Infor Industry AI tool set: the standard tools and the customized tools in this repository, including those the Infor Industry AI skills use (see [Tools](#tools)). To create the customized tools in a tenant, or to check a tenant against the tool set, see [GenAI Gateway tool scripts](../scripts/genai-gateway/README.md).

### Part 2: Register Claude in ION API (`IONAPI-Administrator`)

1. In Infor OS Portal, open **API Gateway** and go to **Authorized Applications**.
2. Add a new non-Infor authorized application and fill in the form:

   | Field | Value |
   |---|---|
   | **Name** | A name for the application, for example `Claude` |
   | **Type** | **MCP Client** |
   | **Description** | For example `Claude connector for Infor M3` |
   | **Redirect URL** | `https://claude.ai/api/mcp/auth_callback` |
   | **OAuth 2.1 Access Token** | Keep the default, **2 Hours** |
   | **Issue Refresh Tokens** | On. Without refresh tokens, users must sign in again each time the access token expires. |

3. Under **MCP Server Access**, select **Infor M3** (endpoint `M3/service/genai-gateway/mcp/be/`). This allows the application to access the M3 MCP server only.
4. Save the application. ION API generates the **Client ID**.
5. Under **MCP Client Configuration**, the `mcp.json` snippet shows the connector URL (`url`) and the client ID (`clientId`) for your tenant. Click **Copy**, and pass both values to the person who adds the connector in Claude.

The snippet has this form, with your tenant's values:

```json
{
  "mcpServers": {
    "m3-emscmcp": {
      "type": "http",
      "url": "https://mingle-ionapi.inforcloudsuite.com/<tenant>/M3/service/genai-gateway/mcp/be/",
      "oauth": {
        "clientId": "<client ID>"
      }
    }
  }
}
```

### Part 3: Add the connector in Claude (Claude Owner or Primary Owner)

On Claude Team and Enterprise plans, a Claude Owner or Primary Owner adds the connector once for the organization. On Enterprise, a custom role with **Manage access to Libraries** can also add it.

1. In Claude, go to **Organization settings** > **Connectors**.
2. Click **Add**, point to **Custom** and select **Web**.
3. Enter the name **Infor Industry AI**.
4. Enter the `url` value from the snippet as the MCP server URL.
5. Choose **Use your own OAuth client** and enter the `clientId` value from the snippet. Leave the client secret empty.
6. Click **Add**.

> [!NOTE]
> Infor OS signs Claude in with the client ID from Part 2. The other OAuth options in the dialog, **Use Claude's published identity** and **Register automatically**, don't work with Infor OS.

On Free, Pro and Max plans, each user adds the connector: go to **Customize** > **Connectors**, click **+**, choose **Add custom connector** and enter the same name, URL and client ID.

### Part 4: Connect Claude (each user)

1. In Claude, go to **Customize** > **Connectors**.
2. Find **Infor Industry AI** and click **Connect**.
3. Sign in with your Infor OS credentials for the tenant.

The connector works in Claude on the web, Claude Desktop and the Claude mobile apps.

### Check that it works

Ask Claude "Which M3 user am I signed in as?" It should answer by calling a read-only user lookup tool (MNS150MI GetUserData for the current user, `M3_MNS150MI_GetUserData_CurrentUser`) and return your M3 user ID. If it does not, check your sign-in and your M3 authority.

Claude first asks to use the tool. Allow it. The answer includes your M3 user ID and name, and your default company, division, facility and warehouse.

### Optional: use the same tools in Infor GenAI Factory

The same M3 tools can be added to agents in GenAI Factory by selecting the M3 BE MCP server and clicking **Add** on each tool. The tool definition is copied into the agent. If a tool changes later, remove it from the agent and add it again.

## Tools

Each tool is one M3 MI transaction, named `M3_<Program>_<Transaction>`, for example `M3_CRS610MI_GetBasicData`. Tools use readable field names and these types: string, integer, number, date, time, boolean and enum. An enum shows a field such as status as named values instead of codes.

| Type | What Claude sends and receives |
|---|---|
| `string` | Text, for example a customer number |
| `integer` | A whole number |
| `number` | A number that can have decimals, for example a quantity or price |
| `date` | A date as `YYYY-MM-DD`, for example `2026-11-05` |
| `time` | A time as `HH:mm`, for example `14:30` |
| `boolean` | `true` or `false` |
| `enum` | One of the field's named values, for example a status name instead of its code |

Most M3 API transactions listed in the API Gateway can be enabled as tools, and a subset is on by default as standard tools. The set grows with each release.

This guide describes the Infor Industry AI tool set, 264 tools at the time of writing:

- 86 standard tools, as Infor delivers them.
- 178 customized tools, defined in [`scripts/genai-gateway/tools`](../scripts/genai-gateway/tools/). 145 have no standard version, and 33 replace a standard tool with other settings, for example with more output fields enabled or status values shown by name.

The table summarizes the tool set by area, and the [appendix](#appendix-tools) lists each tool. The tool list in GenAI Gateway is the complete reference for a tenant.

| Area | M3 programs | Changes data |
|---|---|---|
| Customer orders | OIS100MI customer orders, order lines, batch orders, texts and quotations, OIS010MI and OIS014MI order types, OIS120MI order stops, OIS275MI batch order lines, OIS320MI prices, OIS340MI supply alternatives, OIS350MI invoices per order, OIS390MI customer returns, OIS060MI and OIS111MI blanket agreements, QPS115MI quotations, MWS150MI supply chain | Yes: OIS010MI, OIS100MI, OIS120MI |
| Customers and suppliers | CRS610MI customers, CRS618MI and CMS055MI contacts, CRS620MI suppliers | Yes: CRS610MI |
| Purchase orders | PPS200MI purchase orders and lines, PPS001MI confirmations, PPS170MI planned purchase orders, PPS370MI batch entry, PPS600MI printing, PPS100MI agreements, PPS115MI alternate suppliers, PPS205MI purchase monitoring, PPS330MI order history, PPS360MI delivery notes, PPS390MI claims | Yes: PPS001MI, PPS170MI, PPS200MI, PPS370MI, PPS600MI |
| Manufacturing orders | PMS100MI manufacturing orders, materials and operations, PMS170MI planned manufacturing orders, PDS010MI work centers, PDS016MI daily capacity, PDS030MI shift patterns, CPS100MI capacity load, PDS013MI alternate materials, QMS300MI and PMS130MI quality inspection | Yes: PDS010MI, PMS100MI, PMS170MI |
| Items and inventory | MMS200MI items and balances, MMS060MI balance identities, MMS080MI material plans, MMS120MI allocations, MMS310MI inventory updates, MWS121MI preallocations, MMS037MI planning policies, MMS025MI aliases, MMS020MI item relations | Yes: MMS120MI, MMS200MI, MMS310MI |
| Warehouse and shipping | MWS410MI deliveries, MWS411MI delivery lines, MWS420MI picking lists, MWS423MI packing, DRS100MI shipments, MMS100MI distribution orders, DPS170MI distribution order proposals, DPS001MI distribution relations | Yes: DPS001MI, DPS170MI, MMS100MI, MWS410MI, MWS420MI, MWS423MI |
| Finance | ARS200MI and ARS251MI accounts receivable, APS370MI goods received not invoiced, APS450MI invoice matching, GLS200MI general ledger, FAS001MI, FAS002MI, FAS003MI, FAS004MI and FAS010MI fixed assets, RMS440MI credit tickler notes | No |
| Users, roles and messages | MNS150MI users, MNS405MI and MNS410MI roles, MNS320MI batch jobs, CRS420MI application messages | Yes: CRS420MI |
| Configuration and reference data | CMS975MI features, CODEXPMI configuration items, CMS004MI, CMS005MI, CMS006MI, CMS007MI and CMS009MI printer files, ARS200MI system date and time, CRS025MI item groups, CRS100MI salespeople, CRS111MI e-mail addresses, CRS200MI requisition order types | Yes: CRS025MI |

### Tools that change data

No standard tool changes data. In the tool set, 78 customized tools create, change, release or delete M3 records, and 11 of them delete. The [appendix](#appendix-tools) marks each one. Examples are `M3_OIS100MI_AddOrderHead`, `M3_PPS170MI_RelPOP`, `M3_PPS200MI_ApprovePO`, `M3_PMS100MI_CrtMO`, `M3_MMS200MI_UpdItmPrice`, `M3_MWS420MI_Confirm` and `M3_CRS610MI_ChgBasicData`. The Infor Industry AI skills use 42 of them.

A user with the `M3GENAI-BE-Administrator` role can disable any of them in GenAI Gateway, or leave them out when setting up the tools (see [Data safeguards](#data-safeguards)).

> [!WARNING]
> A tool that changes data does so as the signed-in user, within that user's M3 authority. Users should review each request before allowing it in Claude, and should not choose **Always allow** for these tools.

## M3 roles and permissions

| Who | Role or authority | What it allows |
|---|---|---|
| GenAI Gateway administrator | IFS role `M3GENAI-BE-Administrator` | Opens GenAI Gateway in Infor Portal to view, customize, enable and disable tools |
| ION API administrator | `IONAPI-Administrator` | Registers Claude as an MCP Client authorized application in API Gateway and gives it access to the Infor M3 MCP server |
| End user | M3 user account with authority for the M3 programs behind the tools | Runs the tools, within the user's M3 authority |

Tool calls run as the signed-in user, not as a shared service account, and M3 security applies. A user can see or change only what M3 already lets them see or change.

To check which M3 roles a user has, use the tool `M3_MNS410MI_LstRolesByUser`.

## Data safeguards

Users with the `M3GENAI-BE-Administrator` role control what Claude can see and do through GenAI Gateway, and each user controls which tools Claude may call.

- **Field filtering.** Only enabled fields are available to Claude. GenAI Gateway requests only the enabled output fields from M3, so a disabled field never leaves M3. Disable any input or output field that should not be exposed.
- **Read-only deployments.** Standard tools only read data. To limit Claude to lookups, leave out the tools that change data when you set up the tools, or disable them in GenAI Gateway. The [appendix](#appendix-tools) marks each one.
- **Controlled changes.** A customized tool replaces the standard one, so changes are made in one place and apply to every user of the tenant.
- **Approvals in Claude.** Claude asks before it calls a tool, unless the user has chosen **Always allow** for that tool. Users can block tools they don't need: in **Customize** > **Connectors**, select the connector and set the tool's permission to **Blocked**.

## Troubleshooting

| What you see | Cause | What to do |
|---|---|---|
| Sign-in fails, or Claude can't connect after sign-in | The redirect URL, the client ID or the MCP server access doesn't match | The `IONAPI-Administrator` checks that the authorized application has the redirect URL `https://claude.ai/api/mcp/auth_callback` and **Infor M3** selected under **MCP Server Access**. If the client ID in Claude is wrong, the Claude Owner or Primary Owner removes the connector and adds it again with the right one. |
| Users have to sign in again every 2 hours | **Issue Refresh Tokens** is off | The `IONAPI-Administrator` turns on **Issue Refresh Tokens** for the authorized application. |
| Claude connects but finds no M3 tools | The tenant doesn't have Velocity Suite, so M3 GenAI Gateway isn't active | Contact Infor Support. |
| "The signed-in Infor user is not set up as a user in M3 for this tenant" | The Infor OS account has no M3 user | Set the person up as a user in M3 (MNS150). |
| M3 refuses a call with a security or authority message | The user lacks M3 authority for that program | Connect the user to an M3 role that gives access to the program (MNS410). |
| A tool is missing in Claude, or a change doesn't show | The tool is disabled, a field long name breaks the naming rule, or the conversation started before the change | The `M3GENAI-BE-Administrator` enables the tool and checks its long names (see [Edit input or output fields](#edit-input-or-output-fields)). The user starts a new conversation. |

## Support

For help with setup or tool behavior, contact Infor Support through [Infor Concierge](https://concierge.infor.com).

## Using the M3 GenAI Gateway administration tool

### Launch the M3 BE MCP tool admin UI

1. Sign in to Portal with an account that has the IFS role `M3GENAI-BE-Administrator`. Navigate to M3.
2. In **Administration Tools**, click **GenAI Gateway** to start the admin UI.

### Standard tools

The MCP tools that are available to use immediately are a subset of all Business Engine APIs. The number of tools will increase with new releases.

You can view a standard tool. The input and output fields show all the available fields in the API. Agents can use enabled fields. Standard tools can't be edited or turned off for a tenant.

To make a customized version of a standard tool, click **Copy** in the **Details** form. A customized version of a tool replaces the standard tool. If you specify a sub-name, the new tool is displayed as a separate tool. The copy starts disabled, so enable it when you have finished editing.

### Customized tools

On the **Customized** tab, all customized tools are shown.

To replace a standard tool or create a new variant of a standard tool, create the tool on the **Standard** tab.

To create a new tool that does not exist as a standard tool, click **+** in the **Tools** list. Specify values in the **Program** field, **Transaction** field, and the optional **Sub-name** field. For example, `CRS610MI` and `GetBasicData`.

### Edit tool details

You can change the description of a tool and enable or disable a tool. When you disable a customized tool for a standard tool without a sub-name, the standard tool is used.

### Edit input or output fields

All input fields are listed, but only the enabled fields can be used.

You can change this information:

- Long name
- Description
- Type
- Enum keys or values

Enum keys or values are used if the type is an enum. Both values are a comma-separated list, and the number of values must match.

Follow these rules when you edit fields:

- **Long names** may contain only letters, digits, underscores (`_`), periods (`.`) and hyphens (`-`), up to 64 characters, with no spaces. Claude ignores the whole tool if one of its long names breaks this rule.
- **Types** must match the M3 field. A field that holds decimals must be `number`, not `integer`. Otherwise the call fails when M3 returns a decimal value.
- **Enum keys and values** pair up in order. For example, keys `Preliminary,Active` and values `10,20` map `Preliminary` to `10` and `Active` to `20`.

## Appendix: tools

The Infor Industry AI tool set at the time of writing, by area. **Source** shows where each tool comes from:

- **Standard**: Infor's standard tool, as delivered.
- **Customized**: a customized tool from [`scripts/genai-gateway/tools`](../scripts/genai-gateway/tools/) that has no standard version.
- **Standard, customized**: a customized tool from the same folder that replaces the standard tool of the same name.

<details>
<summary><strong>Customer orders</strong> (45 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_MWS150MI_SelSupplyChain` | Every order connected to an order's supply chain, across levels | No | Standard, customized |
| `M3_OIS010MI_Cpy` | Creates a customer order type by copying one | Yes | Customized |
| `M3_OIS010MI_Get` | Settings of one customer order type | No | Customized |
| `M3_OIS010MI_LstOrderTypes` | Customer order types and their main settings | No | Customized |
| `M3_OIS010MI_Upd` | Changes a customer order type | Yes | Customized |
| `M3_OIS014MI_Get` | Field selection and defaults of one customer order type | No | Customized |
| `M3_OIS060MI_GetCustBlkAgr` | One customer blanket agreement header | No | Standard |
| `M3_OIS060MI_LstCustBlkAgr` | Customer blanket agreement headers for one or more customers | No | Standard |
| `M3_OIS100MI_AddBatchHead` | Creates a batch customer order header | Yes | Customized |
| `M3_OIS100MI_AddOrderHead` | Creates a customer order header | Yes | Customized |
| `M3_OIS100MI_AddOrderLine` | Adds a line to a customer order | Yes | Customized |
| `M3_OIS100MI_AddText` | Adds a text note to a customer order | Yes | Customized |
| `M3_OIS100MI_Confirm` | Confirms a batch customer order and creates the customer order | Yes | Customized |
| `M3_OIS100MI_CreditCheck` | Runs a credit check on a customer order and updates its credit stop | Yes | Customized |
| `M3_OIS100MI_DelHead` | Deletes a customer order (status 90) | Yes | Customized |
| `M3_OIS100MI_DelLine` | Deletes a customer order line | Yes | Customized |
| `M3_OIS100MI_DltLineCharge` | Deletes the charges on a customer order line | Yes | Customized |
| `M3_OIS100MI_DltLnInfo` | Deletes the additional information on a customer order line | Yes | Customized |
| `M3_OIS100MI_GetLine` | One customer order line | No | Customized |
| `M3_OIS100MI_GetOrderHead` | Header of one customer order | No | Customized |
| `M3_OIS100MI_GetOrderHead_RequestedFields` | Header of one customer order, without recalculating order totals | No | Standard |
| `M3_OIS100MI_GetUpdateSts` | Status of a background update of customer orders | No | Customized |
| `M3_OIS100MI_LstErrMsgOrder` | Error messages for a batch customer order | No | Standard |
| `M3_OIS100MI_ReleaseOrder` | Releases a customer order locked with LockOrder in Sales Desk | Yes | Customized |
| `M3_OIS100MI_SearchHead_LimitedOutput` | Customer order headers that match search criteria | No | Standard, customized |
| `M3_OIS100MI_SearchLine_LimitedOutput` | Customer order lines that match search criteria | No | Standard |
| `M3_OIS100MI_SearchLine_Summary` | Customer order lines that match search criteria, with a short set of fields | No | Standard |
| `M3_OIS100MI_SearchQuotation` | Quotations that match search criteria | No | Standard |
| `M3_OIS100MI_SndBatchLine` | Adds a line to a batch customer order | Yes | Customized |
| `M3_OIS100MI_UpdCOPlanDates` | Changes the planning, requested, departure and confirmed dates on customer orders, as a background update | Yes | Customized |
| `M3_OIS111MI_LstAgrHead_ValidAgreements` | Active blanket agreements for a customer | No | Standard |
| `M3_OIS120MI_GetCOStopInfo` | Stop and credit information for one customer order | No | Standard, customized |
| `M3_OIS120MI_LstCOStopByCUOR` | Order stop information by the customer's own order number | No | Standard, customized |
| `M3_OIS120MI_LstCOStopByPYNO` | Order stop information for all orders of a payer | No | Standard, customized |
| `M3_OIS120MI_UpdCOStop` | Changes the stop code on a customer order header | Yes | Customized |
| `M3_OIS275MI_SearchBatchLine` | Batch customer order lines that match search criteria | No | Standard |
| `M3_OIS320MI_GetPriceLine` | Sales price and discounts for one customer and item | No | Customized |
| `M3_OIS340MI_LstSupplSummary` | Supply alternatives from a supply model simulation for a customer, item or order | No | Standard, customized |
| `M3_OIS350MI_LstAllInvByCO` | Invoices for one customer order | No | Standard |
| `M3_OIS390MI_GetHead` | Header of one customer return | No | Standard |
| `M3_OIS390MI_GetHeadPickUp` | Pick-up details of one customer return | No | Standard |
| `M3_OIS390MI_GetLine` | One customer return line | No | Standard |
| `M3_OIS390MI_LstLine` | Lines of one customer return | No | Standard |
| `M3_OIS390MI_LstOpenLine` | Open customer return lines | No | Standard |
| `M3_QPS115MI_GetQuoteInfo` | Header of one sales quotation | No | Standard |

</details>

<details>
<summary><strong>Customers and suppliers</strong> (13 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_CMS055MI_LstByCustomer` | Contact people connected to a customer | No | Standard |
| `M3_CRS610MI_Add` | Creates a customer from a template customer | Yes | Customized |
| `M3_CRS610MI_ChgBasicData` | Changes a customer's basic data | Yes | Customized |
| `M3_CRS610MI_ChgFinancial` | Changes a customer's financial settings, such as credit limit, currency and tax | Yes | Customized |
| `M3_CRS610MI_ChgOrderInfo` | Changes a customer's order defaults and controls | Yes | Customized |
| `M3_CRS610MI_GetBasicData` | Basic data for one customer: name, address, contacts and classification | No | Standard |
| `M3_CRS610MI_GetBasicData_CustomerName` | Name of one customer | No | Standard |
| `M3_CRS610MI_GetFinancial` | Financial, credit control and invoicing settings for one customer | No | Standard |
| `M3_CRS610MI_GetOrderInfo` | Order defaults and controls for one customer | No | Standard |
| `M3_CRS610MI_LstAddresses` | Addresses of one customer | No | Standard |
| `M3_CRS610MI_SearchCustomer` | Customers that match search criteria | No | Standard |
| `M3_CRS618MI_Get` | One contact person | No | Standard |
| `M3_CRS620MI_SearchSupplier` | Suppliers that match search criteria | No | Standard |

</details>

<details>
<summary><strong>Purchase orders</strong> (48 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_PPS001MI_ConfirmLine` | Confirms a purchase order line with the supplier's date, quantity and price | Yes | Customized |
| `M3_PPS001MI_FinishMark` | Marks purchase orders or lines as finished | Yes | Customized |
| `M3_PPS100MI_GetAgrLine` | One purchase agreement line | No | Customized |
| `M3_PPS100MI_LstAgrHead` | Purchase agreement headers for a company | No | Customized |
| `M3_PPS100MI_LstAgrHeadBySup` | Purchase agreement headers for a supplier | No | Standard, customized |
| `M3_PPS100MI_LstAgrLine` | Lines of one purchase agreement | No | Standard, customized |
| `M3_PPS100MI_LstStgPrice` | Staggered prices on a purchase agreement line | No | Standard, customized |
| `M3_PPS115MI_LstAltSupplier` | Supplier and alternate supplier agreements for an item | No | Standard, customized |
| `M3_PPS170MI_CrtPOP` | Creates planned purchase orders | Yes | Customized |
| `M3_PPS170MI_DelPlannedPO` | Deletes a planned purchase order | Yes | Customized |
| `M3_PPS170MI_GeneratePONbr` | Assigns a purchase order number to a planned purchase order | Yes | Customized |
| `M3_PPS170MI_GetPlannedPO` | One planned purchase order | No | Customized |
| `M3_PPS170MI_RelPOP` | Releases planned purchase orders as purchase orders | Yes | Customized |
| `M3_PPS170MI_SearchPOP` | Planned purchase orders that match search criteria | No | Customized |
| `M3_PPS170MI_SelErrPOP` | Planned purchase orders with errors after a batch update | No | Customized |
| `M3_PPS170MI_Select` | Planned purchase orders for a warehouse or warehouse group, in a status range | No | Customized |
| `M3_PPS170MI_UpdPlannedPO` | Changes planned purchase orders | Yes | Customized |
| `M3_PPS200MI_AddLine` | Adds a line to a purchase order | Yes | Customized |
| `M3_PPS200MI_ApprovePO` | Approves purchase orders that wait for authorization | Yes | Customized |
| `M3_PPS200MI_DltLine` | Deletes a purchase order line | Yes | Customized |
| `M3_PPS200MI_GetAddresses` | Header addresses of one purchase order | No | Standard |
| `M3_PPS200MI_GetHead` | Header of one purchase order | No | Customized |
| `M3_PPS200MI_GetLine` | One purchase order line | No | Customized |
| `M3_PPS200MI_LstDupOrders` | Duplicate purchase order lines | No | Customized |
| `M3_PPS200MI_LstLine` | Lines of one purchase order | No | Customized |
| `M3_PPS200MI_LstLine2` | Lines of one purchase order, with full-length item and text fields | No | Customized |
| `M3_PPS200MI_LstLineTrans` | Goods receipts for one purchase order line | No | Customized |
| `M3_PPS200MI_LstReceiptsByPO` | Goods receipts for one purchase order | No | Customized |
| `M3_PPS200MI_SearchHead` | Purchase order headers that match search criteria | No | Customized |
| `M3_PPS200MI_SearchLine` | Purchase order lines that match search criteria | No | Standard, customized |
| `M3_PPS200MI_UpdLine` | Changes purchase order lines | Yes | Customized |
| `M3_PPS205MI_LstMonitors` | Purchase monitoring records for purchase orders | No | Customized |
| `M3_PPS330MI_ListPOTrans` | History of a purchase order or line | No | Customized |
| `M3_PPS360MI_GetHead` | One supplier delivery note header | No | Standard |
| `M3_PPS360MI_LstDetail` | Package details of one supplier delivery note | No | Standard |
| `M3_PPS360MI_LstHeadByPack` | Delivery note headers for a package number | No | Standard |
| `M3_PPS360MI_SearchHead` | Supplier delivery note headers that match search criteria | No | Standard |
| `M3_PPS370MI_AddHead` | Adds a purchase order header to a batch entry | Yes | Customized |
| `M3_PPS370MI_AddLine` | Adds purchase order lines to a batch entry | Yes | Customized |
| `M3_PPS370MI_FinishEntry` | Processes a purchase order batch entry | Yes | Customized |
| `M3_PPS370MI_StartEntry` | Starts a purchase order batch entry | Yes | Customized |
| `M3_PPS390MI_GetClaimHead` | Header of one purchase or return-to-supplier claim | No | Standard |
| `M3_PPS390MI_GetClaimLine` | One claim line | No | Standard |
| `M3_PPS390MI_LstClaimByPuno` | Claims for a purchase order | No | Standard |
| `M3_PPS390MI_LstClaimBySuno` | Claims for a supplier | No | Standard |
| `M3_PPS390MI_LstClaimHead` | Claim headers | No | Standard |
| `M3_PPS390MI_LstClaimLine` | Lines of one claim | No | Standard |
| `M3_PPS600MI_PrintPO` | Prints a purchase order | Yes | Customized |

</details>

<details>
<summary><strong>Manufacturing orders</strong> (43 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_CPS100MI_SelTotalLoad` | Total pegged load for one work center over a period | No | Customized |
| `M3_PDS010MI_AddShiftPatAdj` | Sets which shift pattern a work center uses for a date range | Yes | Customized |
| `M3_PDS010MI_CrtCapacity` | Re-creates work center capacity for a date range | Yes | Customized |
| `M3_PDS010MI_DelShiftPatAdj` | Deletes a work center's shift pattern adjustment | Yes | Customized |
| `M3_PDS010MI_Get` | One work center | No | Customized |
| `M3_PDS010MI_LstRelPerWC` | Resource relations for the work centers in a facility | No | Customized |
| `M3_PDS013MI_GetAltMat` | Alternate material for one product structure line | No | Customized |
| `M3_PDS013MI_LstAltMat` | Alternate materials for a product | No | Customized |
| `M3_PDS016MI_GetDailyCap` | Daily capacity of a work center for one date and time interval | No | Customized |
| `M3_PDS016MI_LstDailyCap` | Daily capacity of a work center | No | Customized |
| `M3_PDS030MI_SelPatternLines` | Shift pattern lines for a range of facilities | No | Customized |
| `M3_PMS100MI_CrtMO` | Creates a manufacturing order | Yes | Customized |
| `M3_PMS100MI_DltMO` | Deletes preliminary manufacturing orders | Yes | Customized |
| `M3_PMS100MI_Get` | Header of one manufacturing order | No | Standard, customized |
| `M3_PMS100MI_GetMatLine` | One material line on a manufacturing order | No | Standard, customized |
| `M3_PMS100MI_GetOperation` | One operation on a manufacturing order | No | Standard, customized |
| `M3_PMS100MI_HoldMO` | Puts manufacturing orders on hold | Yes | Customized |
| `M3_PMS100MI_LstByRORN` | Manufacturing orders linked to a reference order | No | Customized |
| `M3_PMS100MI_LstMaterials` | Material lines of a released manufacturing order | No | Standard, customized |
| `M3_PMS100MI_LstOperations` | Operations of a released manufacturing order | No | Standard, customized |
| `M3_PMS100MI_RelHeldMO` | Releases a held manufacturing order | Yes | Customized |
| `M3_PMS100MI_ReschedOper` | Reschedules operations on a manufacturing order | Yes | Customized |
| `M3_PMS100MI_Reschedule` | Reschedules a manufacturing order: dates, times, quantity and priority | Yes | Customized |
| `M3_PMS100MI_SearchMO` | Manufacturing orders that match search criteria | No | Standard, customized |
| `M3_PMS100MI_SearchMaterial` | Manufacturing order material lines that match search criteria | No | Standard |
| `M3_PMS100MI_SearchOperation` | Manufacturing order operations that match search criteria | No | Standard |
| `M3_PMS100MI_SelMatByHead` | Material lines of released manufacturing orders, selected by header criteria | No | Customized |
| `M3_PMS100MI_SelOrderHead` | Released manufacturing order headers, selected by flexible criteria | No | Customized |
| `M3_PMS100MI_SplitMO` | Splits a manufacturing order in two at an operation | Yes | Customized |
| `M3_PMS100MI_TriggerJob` | Starts a background job by transaction name and job number | Yes | Customized |
| `M3_PMS100MI_UpdMatLine` | Changes material lines on a manufacturing order | Yes | Customized |
| `M3_PMS100MI_UpdOperation` | Changes an operation on a manufacturing order | Yes | Customized |
| `M3_PMS130MI_LstOpenQI` | Balance identities still under quality inspection, for an item and lot | No | Customized |
| `M3_PMS170MI_CrtPlannedMO` | Creates planned manufacturing orders, simulated or real | Yes | Customized |
| `M3_PMS170MI_DelPlannedMO` | Deletes a planned manufacturing order | Yes | Customized |
| `M3_PMS170MI_Get` | Header of one planned manufacturing order | No | Standard |
| `M3_PMS170MI_LstMaterials` | Material lines of one planned manufacturing order | No | Standard |
| `M3_PMS170MI_LstOperations` | Operations of one planned manufacturing order | No | Standard |
| `M3_PMS170MI_SearchMOP` | Planned manufacturing orders that match search criteria | No | Standard |
| `M3_PMS170MI_SetStatus` | Changes the status of a planned manufacturing order | Yes | Customized |
| `M3_QMS300MI_GetQIRqByRefOrd` | Quality inspection request for a reference order | No | Customized |
| `M3_QMS300MI_LstQIReqByOrCat` | Quality inspection requests for an item and facility, by order category | No | Customized |
| `M3_QMS300MI_LstQIReqByStat` | Quality inspection requests for an item and facility, by status | No | Customized |

</details>

<details>
<summary><strong>Items and inventory</strong> (31 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_MMS020MI_LstItemRelation` | Relations between an item and other items | No | Standard |
| `M3_MMS025MI_GetAlias` | One alias for an item, such as an EAN code | No | Standard |
| `M3_MMS025MI_LstAlias` | Aliases of one item | No | Standard |
| `M3_MMS025MI_LstItem` | Items that use an alias number | No | Standard |
| `M3_MMS037MI_LstPlanPolicy` | Planning policies and their parameters | No | Customized |
| `M3_MMS060MI_Get` | Balance identities for one item in a warehouse | No | Customized |
| `M3_MMS060MI_List` | Balance identities in one warehouse, by item, location, status and lot | No | Customized |
| `M3_MMS080MI_LstMtPlByItmWhs` | Material plan for one item in a warehouse | No | Customized |
| `M3_MMS080MI_LstPOHBalance` | Projected on-hand balance per item and warehouse on a planning date | No | Customized |
| `M3_MMS120MI_AllocateOrdLine` | Allocates stock to an order line | Yes | Customized |
| `M3_MMS120MI_DeAllocateOrLne` | Removes the stock allocated to an order line | Yes | Customized |
| `M3_MMS120MI_UpdDetAlloc` | Changes the detailed allocation quantities on an order line | Yes | Customized |
| `M3_MMS200MI_CpyItmBasic` | Creates an item by copying an existing item | Yes | Customized |
| `M3_MMS200MI_CpyItmFac` | Connects an item to a facility by copying an existing connection | Yes | Customized |
| `M3_MMS200MI_CpyItmWhs` | Connects an item to a warehouse by copying an existing connection | Yes | Customized |
| `M3_MMS200MI_GetItmBasic` | Basic data for one item | No | Standard |
| `M3_MMS200MI_GetItmPrice` | Price data for one item | No | Customized |
| `M3_MMS200MI_GetItmWhsBal` | On-hand balance for one item in a warehouse, by stock status | No | Customized |
| `M3_MMS200MI_GetItmWhsBal_Subname` | On-hand balance for one item in a warehouse, with more fields, such as allocatable, consignment and planning quantities | No | Customized |
| `M3_MMS200MI_GetItmWhsBasic` | Settings for one item in one warehouse | No | Standard |
| `M3_MMS200MI_GetSumWhsBal` | Summarized balance and planning data for one item in a warehouse | No | Customized |
| `M3_MMS200MI_LstItmWhsByItm` | Item-warehouse settings for one item or all items | No | Customized |
| `M3_MMS200MI_LstSumWhsBal` | Summarized balances for the items in a warehouse | No | Customized |
| `M3_MMS200MI_SearchItem` | Items that match search criteria | No | Standard |
| `M3_MMS200MI_UpdItmBasic` | Changes an item's basic data | Yes | Customized |
| `M3_MMS200MI_UpdItmPrice` | Changes an item's price data | Yes | Customized |
| `M3_MMS200MI_UpdItmWhs` | Changes an item's warehouse settings | Yes | Customized |
| `M3_MMS310MI_Update` | Updates the on-hand balance at a location, as a quick physical inventory | Yes | Customized |
| `M3_MWS121MI_LstAcqByCUOR` | Supply orders preallocated to the lines of a customer's order number | No | Customized |
| `M3_MWS121MI_LstAcqByDmdOrd` | Supply orders preallocated to one demand order line | No | Customized |
| `M3_MWS121MI_LstDmdByAcqOrd` | Demand order lines preallocated from one supply order | No | Customized |

</details>

<details>
<summary><strong>Warehouse and shipping</strong> (28 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_DPS001MI_AddRelDistrWhs` | Creates a distribution relation between two warehouses | Yes | Customized |
| `M3_DPS001MI_LstRelation` | Warehouse distribution relations of one relation type | No | Customized |
| `M3_DPS170MI_CrtPlannedDO` | Creates planned distribution orders | Yes | Customized |
| `M3_DPS170MI_DelPlannedDO` | Deletes planned distribution orders | Yes | Customized |
| `M3_DPS170MI_GetJobNumber` | A new batch job number for updating distribution order proposals | No | Customized |
| `M3_DPS170MI_GetUserJobSts` | Batch update status of a user's distribution order inbox | No | Customized |
| `M3_DPS170MI_SelErrDOP` | Distribution order proposals that a batch update did not update | No | Customized |
| `M3_DPS170MI_SndInboxDOP` | Sends distribution order proposals to a user's inbox for batch update | Yes | Customized |
| `M3_DPS170MI_TriggerUpdJob` | Starts the batch update of the planned distribution orders in the user's inbox | Yes | Customized |
| `M3_DRS100MI_GetShipment` | Header of one outbound shipment | No | Standard |
| `M3_DRS100MI_LstByDelivery` | Deliveries connected to a shipment | No | Standard |
| `M3_DRS100MI_LstByPlace` | Deliveries of a shipment, by destination | No | Standard |
| `M3_DRS100MI_LstShipPickDet` | Picking lines of a shipment | No | Standard |
| `M3_DRS100MI_LstShipPicklist` | Picking lists of a shipment, with their status | No | Standard |
| `M3_DRS100MI_LstShipment` | Shipments that match selection criteria | No | Standard |
| `M3_MMS100MI_AddDOHead` | Creates a requisition, replenishment or distribution order header | Yes | Customized |
| `M3_MMS100MI_AddDOLine` | Adds a line to a distribution order | Yes | Customized |
| `M3_MMS100MI_LstLines` | Lines of a requisition or distribution order | No | Customized |
| `M3_MWS410MI_GetAdr_ADRT` | Address of one delivery, by address type | No | Standard |
| `M3_MWS410MI_GetHead` | Header of one delivery | No | Standard, customized |
| `M3_MWS410MI_LstPackages_PASO` | Packages of a delivery at one packaging level | No | Standard |
| `M3_MWS410MI_RelForPick` | Releases a delivery for picking | Yes | Customized |
| `M3_MWS411MI_LstDelLnByOrd` | Delivery lines for one order or order line | No | Customized |
| `M3_MWS411MI_LstDeliveryLine` | Lines of one delivery | No | Standard, customized |
| `M3_MWS420MI_Confirm` | Confirms all issues on a picking list | Yes | Customized |
| `M3_MWS420MI_LstPickList` | Picking lists that match selection criteria | No | Standard, customized |
| `M3_MWS423MI_PackPicklist` | Reports a whole picking list as packed | Yes | Customized |
| `M3_MWS423MI_UnpackPicklist` | Unpacks a whole picking list | Yes | Customized |

</details>

<details>
<summary><strong>Finance</strong> (16 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_APS370MI_LstRecByPO` | Goods received not invoiced, for a purchase order | No | Standard, customized |
| `M3_APS370MI_Search` | Goods received not invoiced transactions that match search criteria | No | Standard, customized |
| `M3_APS450MI_CheckLineTol` | Quantity and price variances between a supplier invoice line and its goods receipt | No | Customized |
| `M3_ARS200MI_SearchInvoices` | Accounts receivable transactions that match search criteria | No | Standard, customized |
| `M3_ARS251MI_LstExtraInfo` | Additional information on a customer invoice transaction | No | Standard |
| `M3_FAS001MI_GetAsset` | Net book value of one fixed asset | No | Standard |
| `M3_FAS001MI_SearchAssets` | Fixed assets that match search criteria | No | Standard |
| `M3_FAS002MI_Lst` | Depreciation types | No | Standard |
| `M3_FAS003MI_Lst` | Cost and accounted values of fixed assets | No | Standard |
| `M3_FAS004MI_Lst` | Fixed asset insurance | No | Standard |
| `M3_FAS010MI_LstDepPlan` | Depreciation plans | No | Standard |
| `M3_GLS200MI_GetVoucherHead2_VoucherHead` | Header of one voucher | No | Standard |
| `M3_GLS200MI_SearchGenLedger` | General ledger voucher lines that match search criteria | No | Standard |
| `M3_RMS440MI_GetTickleNote` | One credit tickler note for a payer | No | Standard |
| `M3_RMS440MI_LstTicklNoteInv` | Invoices linked to tickler notes | No | Standard |
| `M3_RMS440MI_LstTickleNote` | Credit tickler notes for payers in a division | No | Standard |

</details>

<details>
<summary><strong>Users, roles and messages</strong> (17 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_CRS420MI_Add` | Creates an application message that notifies a user | Yes | Customized |
| `M3_CRS420MI_AddFreeText` | Adds free text to an application message | Yes | Customized |
| `M3_CRS420MI_Complete` | Sets an application message to Completed (status 50) | Yes | Customized |
| `M3_CRS420MI_Delete` | Deletes an application message | Yes | Customized |
| `M3_CRS420MI_Get` | One application message | No | Customized |
| `M3_CRS420MI_LstByActDate` | Application messages in action date order | No | Customized |
| `M3_CRS420MI_LstFreeText` | Free-text lines of one application message | No | Customized |
| `M3_MNS150MI_GetUserData` | Settings of one M3 user | No | Standard, customized |
| `M3_MNS150MI_GetUserData_CurrentUser` | The signed-in user's M3 settings, such as company, division, facility and warehouse | No | Standard |
| `M3_MNS150MI_LstCmpDivi_ListCmpDiviForUser` | Companies and divisions of a user | No | Standard |
| `M3_MNS150MI_LstUserData_ListUserData` | M3 users | No | Standard |
| `M3_MNS150MI_Search` | M3 users that match search criteria | No | Standard |
| `M3_MNS150MI_SelUsers_ListSelectedUsers` | Users in a range of users or divisions | No | Standard |
| `M3_MNS320MI_Search` | Submitted batch jobs that match search criteria | No | Standard |
| `M3_MNS405MI_Lst` | Role definitions | No | Standard |
| `M3_MNS410MI_Lst` | Roles assigned to users, with validity dates | No | Standard |
| `M3_MNS410MI_LstRolesByUser` | Roles of one user | No | Standard |

</details>

<details>
<summary><strong>Configuration and reference data</strong> (23 tools)</summary>

| Tool | Summary | Changes data | Source |
|---|---|---|---|
| `M3_ARS200MI_ServerTimeZone` | Current system date and time | No | Standard, customized |
| `M3_CMS004MI_LstPrtfVariants` | Variants of a printer file | No | Standard, customized |
| `M3_CMS005MI_SearchPrtf` | Printer files that match search criteria. Printer files define M3 output documents. | No | Standard, customized |
| `M3_CMS006MI_LstPrtfStructs` | XML structures of printer files | No | Standard, customized |
| `M3_CMS007MI_LstPrtfSections` | XML sections of printer files | No | Standard, customized |
| `M3_CMS009MI_LstElemBySect` | XML elements in a printer file section | No | Standard, customized |
| `M3_CMS009MI_LstElemByStruct` | XML elements in a printer file structure | No | Standard, customized |
| `M3_CMS975MI_Get` | One feature, and whether it is active in the tenant | No | Standard, customized |
| `M3_CMS975MI_GetKBURL` | Knowledge base link for a feature | No | Standard |
| `M3_CMS975MI_Lst` | Features, and whether each is active | No | Standard, customized |
| `M3_CMS975MI_LstToggles` | Features of a product, such as M3 Business Engine | No | Standard |
| `M3_CMS975MI_Search` | Features that match search criteria | No | Standard |
| `M3_CODEXPMI_LstConfigItems_GetKeyFieldNames` | Key field names of a configuration item type | No | Standard |
| `M3_CODEXPMI_LstConfigItems_GetMenu` | Menu of a configuration item type | No | Standard |
| `M3_CODEXPMI_LstConfigItems_GetRecords` | Records of a configuration item type | No | Standard |
| `M3_CODEXPMI_LstConfigItmTyp` | Configuration item types available for export | No | Standard |
| `M3_CODEXPMI_LstConfigItmTyp_GetConfigItemFromMenu` | Configuration item types under one menu | No | Standard |
| `M3_CRS025MI_AddItemGroup` | Creates an item group | Yes | Customized |
| `M3_CRS025MI_GetItemGroup` | One item group | No | Customized |
| `M3_CRS025MI_LstItemGroup` | Item groups with their descriptions, demand patterns and catch weight tolerances | No | Customized |
| `M3_CRS100MI_Get` | One salesperson, with sales department, business area, shop and Sales Hub settings | No | Customized |
| `M3_CRS111MI_Get` | One e-mail address from the central e-mail address register | No | Customized |
| `M3_CRS200MI_LstOrderType` | Requisition and distribution order types and their main settings | No | Customized |

</details>

---

Copyright © 2026 Infor. All rights reserved. See [LICENSE](../LICENSE).
