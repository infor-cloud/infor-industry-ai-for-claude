# GenAI Gateway tool scripts

`gg.py` lists, checks and sets up the M3 GenAI Gateway tools that the Infor Industry AI skills use. It calls the GenAI Gateway administration API, the same API behind the GenAI Gateway administration tool in Infor Portal.

The skills use standard tools and tools outside the standard set. [`tools/`](tools/) holds a definition for each tool they need beyond the standard set, and for each standard tool they need with other settings, for example with more output fields enabled or status values shown by name. A tenant needs these customized tools before the skills can run their flows.

## What you need

- Python 3.9 or later. Nothing else to install.
- A Backend Service `.ionapi` file whose service account belongs to an Infor OS user with the IFS role `M3GENAI-BE-Administrator`. The script works as that user. An `IONAPI-Administrator` creates the file:
  1. In Infor OS Portal, open **API Gateway** and go to **Authorized Applications**.
  2. Add a new non-Infor authorized application with **Type** **Backend Service**, for example named `GenAI Gateway setup`, and save it.
  3. Click **Download Credentials**, turn on **Create Service Account**, enter the user name of the user with `M3GENAI-BE-Administrator`, and click **Download**.

Keep the `.ionapi` file private, because anyone with it can sign in as that user. When the setup is done, delete the authorized application in ION API.

Tell the script where the file is, once per terminal session:

```bash
export GG_IONAPI=~/Downloads/<file>.ionapi
```

Or pass `--ionapi <file>` with each command. The tenant and the gateway address come from the file.

## List the tools in a tenant

```bash
python3 gg.py list
```

```bash
python3 gg.py list --format csv --out tools.csv
```

Each tool is listed with its type, which version is in effect (`standard`, `customized`, or `none` for a customized tool that is turned off and has no standard version) and its origin. Use `--source standard` or `--source custom` to list one set, and `--format json` for JSON.

## Check a tenant

```bash
python3 gg.py check
```

`check` only reads. It takes the tools each skill uses from the tools line in each skill's `SKILL.md` under [`plugins/infor-industry-ai/skills`](../../plugins/infor-industry-ai/skills), and compares the tenant with them and with `tools/`:

| Result | What to do |
|---|---|
| In place | Nothing |
| Missing | Run `apply` |
| Missing, and `tools/` has no definition for them | Report it to Infor Support |
| Customized but turned off | Enable the tool in GenAI Gateway, or run `apply --enable` |
| Customized differently from `tools/` | Run `apply` to update the tool, after checking the differences |
| Standard tool in effect where `tools/` has a customized version | Run `apply` |
| Standard tool customized in this tenant with fields the skills may not expect | Review the tool in GenAI Gateway. A renamed or disabled field can break a skill. |

Differences show as `current -> expected`. `check` also reports tool names and field long names that Claude doesn't accept: a long name must be 1 to 64 letters, digits, `_`, `.` or `-`, with no spaces. Add `--all` to check the names of every tool in effect, not only the tools the skills use, and `--verbose` to see every difference.

`check` exits with 0 when everything is in place, 1 when changes are needed and 2 on an error, so you can run it from a pipeline.

## Set up the tools

```bash
python3 gg.py apply
```

Without `--apply`, `apply` is a dry run: it lists each tool it would create or update, with the differences, and changes nothing. Review the list, then make the changes:

```bash
python3 gg.py apply --apply
```

- `apply` creates each tool in `tools/` that the tenant doesn't have and updates each one that differs. It never deletes a tool.
- New tools start disabled, as they do when you copy or create a tool in GenAI Gateway. Review them there and enable them, or add `--enable` to enable every tool `apply` writes.
- An update keeps a tool enabled or disabled as it was, unless you add `--enable`.
- An update replaces the tenant's version of the tool, including changes your `M3GENAI-BE-Administrator` users made. Use `--only <tool> ...` to apply some tools and leave the rest.
- A customized tool replaces the standard tool of the same name, so Infor's later changes to that standard tool don't reach the tenant. Run `check` after each M3 GenAI Gateway update.

Set up and test a non-production tenant first. Then run `check` there, try the skills, and repeat on production.

## Update the definitions

To refresh `tools/` from a tenant where the tools are set up and tested:

```bash
python3 gg.py export --needed
```

`export` writes the customized version of each tool the skills use to `tools/`, one JSON file per tool, named after the tool, without the enabled flag. Before you commit, review the changes and make sure that no sensitive field, such as a password or PIN code, is enabled. `export <tool> ...` exports the named tools only, and `--out <folder>` writes somewhere else.

The files use the tool definition format of the GenAI Gateway administration API: the tool's program, transaction, type and description, and its input and output fields with long names, descriptions, types, enum values and whether each field is enabled.
