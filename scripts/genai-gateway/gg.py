#!/usr/bin/env python3
"""List, check and set up M3 GenAI Gateway tools for the Infor Industry AI skills.

  gg.py list     the tools in a tenant: standard, customized and which one is in effect
  gg.py check    whether a tenant has the customized tools in tools/ and the tools the skills use
  gg.py apply    create or update the customized tools in tools/ (dry run unless --apply)
  gg.py export   save customized tool definitions from a tenant as JSON files

Signs in with a Backend Service .ionapi file from ION API. Python 3.9 or later, standard library only.
See README.md in this folder.
"""

import argparse
import concurrent.futures
import csv
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DEFAULT_TOOLS = HERE / "tools"
DEFAULT_EXCLUDE = HERE / "exclude.txt"
DEFAULT_SKILLS = REPO / "plugins" / "infor-industry-ai" / "skills"

# Claude accepts a tool only when its name and every property name match these.
TOOL_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
PROPERTY_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
TOOLS_LINE = re.compile(r"<!--\s*tools:\s*(.*?)\s*-->", re.S)

TOP_FIELDS = ("program", "transaction", "type", "description")
INPUT_FIELDS = ("longName", "description", "type", "required", "enabled", "enumConstants", "enumValues", "showValues")
OUTPUT_FIELDS = ("longName", "description", "type", "enabled", "enumConstants", "enumValues", "showValues", "filter")
WORKERS = 6
RETRIES = 3
RETRY_STATUS = {429, 502, 503, 504}


class GatewayError(Exception):
    pass


# --- ION API and the gateway ------------------------------------------------------------------------------------


class Gateway:
    """The GenAI Gateway tool administration API for one tenant."""

    def __init__(self, ionapi_path, base_url=None, timeout=60):
        try:
            cfg = json.loads(Path(ionapi_path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise GatewayError(f"cannot read {ionapi_path}: {e}")
        missing = [k for k in ("ti", "ci", "cs", "iu", "pu", "ot", "saak", "sask") if not cfg.get(k)]
        if missing:
            raise GatewayError(f"{ionapi_path} is not a Backend Service .ionapi file with a service account "
                               f"(missing {', '.join(missing)})")
        self.tenant = cfg["ti"]
        self.timeout = timeout
        self.base = (base_url or f"{cfg['iu'].rstrip('/')}/{cfg['ti']}/M3/service/genai-gateway/v1").rstrip("/")
        self.base += "/metadata/tools/be"
        self._token = self._sign_in(cfg)

    def _sign_in(self, cfg):
        body = urllib.parse.urlencode({
            "grant_type": "password",
            "username": cfg["saak"], "password": cfg["sask"],
            "client_id": cfg["ci"], "client_secret": cfg["cs"],
        }).encode()
        req = urllib.request.Request(cfg["pu"] + cfg["ot"], data=body, method="POST",
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.load(r)["access_token"]
        except urllib.error.HTTPError as e:
            raise GatewayError(f"sign-in to Infor OS failed (HTTP {e.code}). Check that the .ionapi file is current "
                               "and its service account is active.")
        except (urllib.error.URLError, KeyError, ValueError) as e:
            raise GatewayError(f"sign-in to Infor OS failed: {e}")

    def _call(self, method, path="", query=None, body=None):
        url = self.base + path + ("?" + urllib.parse.urlencode(query) if query else "")
        headers = {"Authorization": "Bearer " + self._token, "Accept": "application/json"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        # GET reads and PUT replaces a whole definition, so a retry after a dropped connection is safe.
        for attempt in range(RETRIES + 1):
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    return r.status, (json.loads(raw) if raw.strip() else None)
            except urllib.error.HTTPError as e:
                if e.code in RETRY_STATUS and attempt < RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                raw = e.read()
                try:
                    errors = [x.get("desc") for x in json.loads(raw).get("errors", [])]
                except (ValueError, AttributeError):
                    errors = []
                return e.code, {"errors": errors}
            except (urllib.error.URLError, ConnectionError, TimeoutError, http.client.HTTPException) as e:
                if attempt < RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                raise GatewayError(f"{method} {url}: {getattr(e, 'reason', e)}")

    @staticmethod
    def _data(status, payload, what):
        if status == 401:
            raise GatewayError(f"{what}: the gateway rejected the token (HTTP 401)")
        if status == 403:
            raise GatewayError(f"{what}: access denied (HTTP 403). The service account's user needs the IFS role "
                               "M3GENAI-BE-Administrator.")
        if status >= 400:
            detail = "; ".join(e for e in (payload or {}).get("errors", []) if e) or "no details"
            raise GatewayError(f"{what}: HTTP {status}: {detail}")
        return payload.get("data", payload) if isinstance(payload, dict) else payload

    def list(self, source):
        status, payload = self._call("GET", query={"metadata-source": source})
        return self._data(status, payload, f"list {source} tools")

    def get(self, name, source):
        """The full definition, or None when the tenant has no such tool."""
        status, payload = self._call("GET", "/" + urllib.parse.quote(name), {"metadata-source": source})
        if status == 404:
            return None
        return self._data(status, payload, f"get {source} {name}")

    def get_many(self, names, source):
        with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
            return dict(zip(names, pool.map(lambda n: self.get(n, source), names)))

    def put(self, definition):
        name = definition["name"]
        status, payload = self._call("PUT", "/" + urllib.parse.quote(name), body=definition)
        self._data(status, payload, f"put {name}")


# --- definitions ------------------------------------------------------------------------------------------------


def load_definitions(tools_dir, only=None):
    tools_dir = Path(tools_dir)
    if not tools_dir.is_dir():
        raise GatewayError(f"{tools_dir}: folder not found")
    defs = {}
    for path in sorted(tools_dir.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("name") != path.stem:
            raise GatewayError(f"{path}: name {d.get('name')!r} differs from the file name")
        defs[d["name"]] = d
    if only:
        unknown = sorted(set(only) - set(defs))
        if unknown:
            raise GatewayError(f"no definition in {tools_dir} for {', '.join(unknown)}")
        defs = {n: defs[n] for n in only}
    return defs


def load_excluded(path):
    """Tool names in exclude.txt, without the comments."""
    path = Path(path)
    if not path.is_file():
        return set()
    names = (line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return {n for n in names if n}


def needed_tools(skills_dir):
    """Every tool named on a skill's tools line, by tool name, with the skills that use it."""
    skills_dir = Path(skills_dir)
    files = sorted(skills_dir.glob("*/SKILL.md"))
    if not files:
        raise GatewayError(f"{skills_dir}: no skills found (pass --skills with the plugin's skills folder)")
    needed = {}
    for f in files:
        m = TOOLS_LINE.search(f.read_text(encoding="utf-8"))
        for t in (x.strip() for x in (m.group(1).split(",") if m else [])):
            if t and t != "none":
                needed.setdefault(t, []).append(f.parent.name)
    return needed


def lint(definition):
    """Problems that make Claude reject the tool, or make fields collide or misread."""
    problems = []
    if not TOOL_NAME.match(definition.get("name", "")):
        problems.append("tool name is not 1-64 letters, digits, _ or -")
    for kind, params in (("input", definition.get("inputParameters") or []),
                         ("output", definition.get("outputParameters") or [])):
        seen = {}
        for p in params:
            if not p.get("enabled"):
                continue
            ln = p.get("longName") or ""
            if not PROPERTY_NAME.match(ln):
                problems.append(f"{kind} {p.get('name')}: long name {ln!r} is not 1-64 letters, digits, _ . or -")
            if ln in seen:
                problems.append(f"{kind} {p.get('name')}: long name {ln!r} is also used by {seen[ln]}")
            seen.setdefault(ln, p.get("name"))
            if p.get("type") == "enum":
                # An empty key is allowed: it names M3's blank value, for example ",Complete" with " ,10".
                keys = (p.get("enumConstants") or "").split(",")
                values = (p.get("enumValues") or "").split(",")
                if not any(k.strip() for k in keys) or len(keys) != len(values):
                    problems.append(f"{kind} {p.get('name')}: enum has {len(keys)} keys and {len(values)} values")
    if not (definition.get("description") or "").strip():
        problems.append("description is empty")
    return problems


def _norm(value):
    # A missing key, None, "" and false all mean "not set" in a definition.
    return "" if value is None or value is False else value


# Field changes that can break a skill: it relies on the long names, types and enabled fields it was written for.
BREAKING = {"longName", "type", "enabled", "required", "enumConstants", "added", "removed"}


def diff(want, have):
    """Differences from have to want as (where, field, old, new), ignoring tool-level enabled and version."""
    out = []
    for f in TOP_FIELDS:
        if _norm(want.get(f)) != _norm(have.get(f)):
            out.append(("tool", f, have.get(f), want.get(f)))
    for kind, key, fields in (("input", "inputParameters", INPUT_FIELDS), ("output", "outputParameters", OUTPUT_FIELDS)):
        w = {p["name"]: p for p in want.get(key) or []}
        h = {p["name"]: p for p in have.get(key) or []}
        for name in sorted(set(w) | set(h)):
            if name not in h:
                out.append((f"{kind} {name}", "added", None, None))
            elif name not in w:
                out.append((f"{kind} {name}", "removed", None, None))
            else:
                for f in fields:
                    if _norm(w[name].get(f)) != _norm(h[name].get(f)):
                        out.append((f"{kind} {name}", f, h[name].get(f), w[name].get(f)))
    return out


def render(change):
    where, field, old, new = change
    if field in ("added", "removed"):
        return f"{where}: {field}"
    start = 0
    if isinstance(old, str) and isinstance(new, str):
        # Long texts often differ in the middle: start both a little before the first difference.
        start = next((i for i, (a, b) in enumerate(zip(old, new)) if a != b), min(len(old), len(new)))
        start = max(0, start - 20)
    label = field if where == "tool" else f"{where} {field}"
    return f"{label}: {_short(old, start)} -> {_short(new, start)}"


def _short(value, start=0, width=60):
    if not isinstance(value, str):
        return json.dumps(value)
    text = ("..." if start else "") + value[start:]
    text = text if len(text) <= width else text[: width - 3] + "..."
    return repr(text)


def _print_changes(changes, verbose, indent, limit):
    for c in changes[: None if verbose else limit]:
        print(" " * indent + render(c))
    if not verbose and len(changes) > limit:
        print(" " * indent + f"... {len(changes) - limit} more (use --verbose)")


# --- commands ---------------------------------------------------------------------------------------------------


def tool_rows(gw):
    standard = {t["name"]: t for t in gw.list("standard")}
    custom = {t["name"]: t for t in gw.list("custom")}
    rows = []
    for name in sorted(set(standard) | set(custom)):
        s, c = standard.get(name), custom.get(name)
        if c and c.get("enabled"):
            in_effect, shown = "customized", c
        elif s:
            in_effect, shown = "standard", s
        else:
            in_effect, shown = "none", c
        origin = "standard, customized" if s and c else "standard" if s else "customized only"
        rows.append({"name": name, "program": shown["program"], "transaction": shown["transaction"],
                     "type": shown["type"], "origin": origin, "in_effect": in_effect,
                     "description": shown.get("description", "")})
    return rows


def cmd_list(gw, args):
    rows = tool_rows(gw)
    if args.source == "standard":
        rows = [r for r in rows if r["origin"] != "customized only"]
    elif args.source == "custom":
        rows = [r for r in rows if r["origin"] != "standard"]
    out = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    try:
        if args.format == "json":
            json.dump(rows, out, indent=1, ensure_ascii=False)
            out.write("\n")
        elif args.format == "csv":
            w = csv.DictWriter(out, fieldnames=list(rows[0]) if rows else ["name"])
            w.writeheader()
            w.writerows(rows)
        else:
            width = max([len(r["name"]) for r in rows] + [4])
            out.write(f"{'Tool':<{width}}  {'Type':<6}  {'In effect':<10}  Origin\n")
            for r in rows:
                out.write(f"{r['name']:<{width}}  {r['type']:<6}  {r['in_effect']:<10}  {r['origin']}\n")
            counts = {k: sum(r["in_effect"] == k for r in rows) for k in ("standard", "customized", "none")}
            out.write(f"\n{len(rows)} tools in {gw.tenant}: {counts['standard']} standard and "
                      f"{counts['customized']} customized in effect, {counts['none']} turned off\n")
    finally:
        if args.out:
            out.close()
    if args.out:
        print(f"Wrote {len(rows)} tools to {args.out}")
    return 0


def cmd_check(gw, args):
    skills_note = None
    if Path(args.skills).exists() or args.skills != str(DEFAULT_SKILLS):
        needed = needed_tools(args.skills)
    else:
        needed = {}
        skills_note = f"No skills in {args.skills}, so only tools/ was checked. Pass --skills to check the skills too."
    defs = load_definitions(args.tools)
    standard = {t["name"] for t in gw.list("standard")}
    custom = {t["name"]: t for t in gw.list("custom")}
    on = {n for n, t in custom.items() if t.get("enabled")}

    names = set(needed) | set(defs) | ((standard | set(custom)) if args.all else set())
    print(f"Reading {len(names)} tools in {gw.tenant} ...", file=sys.stderr)
    full_custom = gw.get_many(sorted(n for n in names if n in on or (n in needed and n in custom)), "custom")
    full_standard = gw.get_many(sorted(n for n in names if n in standard and (n in needed or n not in on)), "standard")

    buckets = {k: [] for k in ("ok", "missing", "nodef", "off", "differs", "local", "uncustomized")}
    naming = {}
    for n in sorted(names):
        active = full_custom.get(n) if n in on else full_standard.get(n)
        if active:
            problems = lint(active)
            if problems:
                naming[n] = problems
        if n not in needed and n not in defs:
            continue
        if n in custom and n not in on and (n in defs or active is None):
            buckets["off"].append((n, []))
        elif active is None:
            buckets["missing" if n in defs else "nodef"].append((n, []))
        elif n not in on:
            buckets["uncustomized" if n in defs else "ok"].append((n, []))
        elif n in defs:
            changes = diff(defs[n], active)
            buckets["differs" if changes else "ok"].append((n, changes))
        elif n in standard:
            changes = [c for c in diff(full_standard[n], active) if c[1] in BREAKING]
            buckets["local" if changes else "ok"].append((n, changes))
        else:
            buckets["ok"].append((n, []))

    skills = sorted({s for v in needed.values() for s in v})
    checked = len(set(needed) | set(defs))
    print(f"\n{gw.tenant}: {checked} tools checked: the {len(defs)} customized tools in tools/"
          + (f" and the {len(needed)} tools the skills use ({', '.join(skills)})" if needed else ""))
    if skills_note:
        print(f"  {skills_note}")
    labels = (
        ("ok", "In place"),
        ("missing", "Missing. apply creates them"),
        ("nodef", "Missing, and tools/ has no definition for them"),
        ("off", "Customized but turned off. Enable them in GenAI Gateway, or run apply --enable"),
        ("differs", "Customized differently from tools/. apply updates them"),
        ("uncustomized", "Standard tool in effect where tools/ has a customized version. apply creates it"),
        ("local", "Standard tool customized in this tenant with fields the skills may not expect. "
                  "Review them in GenAI Gateway"),
    )
    for key, label in labels:
        items = buckets[key]
        if key != "ok" and not items:
            continue
        print(f"  {len(items):>3}  {label}")
        if key == "ok":
            continue
        for n, changes in items:
            print(f"         {n}" + (f"  (used by {', '.join(needed[n])})" if n in needed else ""))
            _print_changes(changes, args.verbose, 13, 5)
    extra = sorted(set(custom) - set(defs))
    if extra:
        excluded = load_excluded(args.exclude)
        print(f"\n  Customized in {gw.tenant} but not in tools/ (not counted as a problem):")
        for n in extra:
            print(f"         {n}" + ("  (left out on purpose, see exclude.txt)" if n in excluded else ""))
    if naming:
        print(f"\nNaming problems in {'the tools in effect' if args.all else 'the tools checked'}. "
              "Claude does not accept a tool with these. Fix them in GenAI Gateway:")
        for n, problems in sorted(naming.items()):
            print(f"  {n}")
            for problem in problems:
                print(f"      {problem}")
    bad = any(buckets[k] for k in buckets if k != "ok") or bool(naming)
    print("\nResult: " + ("changes needed" if bad else "everything checked is in place"))
    return 1 if bad else 0


def cmd_apply(gw, args):
    defs = load_definitions(args.tools, args.only)
    invalid = {n: lint(d) for n, d in defs.items() if lint(d)}
    if invalid:
        for n, problems in invalid.items():
            print(f"{n}: " + "; ".join(problems), file=sys.stderr)
        raise GatewayError("fix the definitions above before applying")
    print(f"Reading {len(defs)} customized tools in {gw.tenant} ...", file=sys.stderr)
    current = gw.get_many(list(defs), "custom")

    plan = []
    for n, d in defs.items():
        have = current.get(n)
        if have is None:
            plan.append(("create", n, dict(d, enabled=args.enable), []))
            continue
        enabled = True if args.enable else bool(have.get("enabled"))
        changes = diff(d, have)
        if args.enable and not have.get("enabled"):
            changes = [("tool", "enabled", False, True)] + changes
        plan.append(("update" if changes else "unchanged", n, dict(d, enabled=enabled), changes))

    for action, n, d, changes in plan:
        if action == "unchanged":
            continue
        state = "enabled" if d["enabled"] else "turned off"
        print(f"{action:<7} {n}  ({state})")
        _print_changes(changes, args.verbose, 12, 8)
    counts = {a: sum(p[0] == a for p in plan) for a in ("create", "update", "unchanged")}
    print(f"\n{gw.tenant}: {counts['create']} to create, {counts['update']} to update, {counts['unchanged']} unchanged")

    todo = [p for p in plan if p[0] != "unchanged"]
    if not todo:
        return 0
    if not args.apply:
        print("Dry run. Nothing was changed. Run again with --apply to make these changes.")
        return 0
    failed = 0
    for action, n, d, _ in todo:
        try:
            gw.put(d)
            print(f"  done    {n}")
        except GatewayError as e:
            failed += 1
            print(f"  failed  {n}: {e}", file=sys.stderr)
    print(f"\n{len(todo) - failed} of {len(todo)} changes made in {gw.tenant}.")
    if not args.enable and counts["create"]:
        print("New tools are turned off. Review them in GenAI Gateway, then enable them there or run apply --enable.")
    return 1 if failed else 0


def cmd_export(gw, args):
    custom = {t["name"] for t in gw.list("custom")}
    excluded = load_excluded(args.exclude)
    if args.all:
        names = sorted(custom - excluded)
    else:
        names = sorted(args.names)
    if not names:
        raise GatewayError("name the tools to export, or pass --all")
    skipped = [n for n in names if n not in custom]
    names = [n for n in names if n in custom]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    written = 0
    for n, d in gw.get_many(names, "custom").items():
        if d is None:
            skipped.append(n)
            continue
        d.pop("enabled", None)
        (out / f"{n}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
    print(f"Wrote {written} definition{'' if written == 1 else 's'} from {gw.tenant} to {out}")
    if args.all:
        stale = sorted(p for p in out.glob("*.json") if p.stem not in names)
        for p in stale:
            p.unlink()
        if stale:
            print(f"Removed {len(stale)} no longer customized in {gw.tenant} or now excluded: "
                  + ", ".join(p.stem for p in stale))
        if excluded & custom:
            print(f"Left out, as listed in {args.exclude}: {', '.join(sorted(excluded & custom))}")
    if skipped:
        print(f"Not customized in {gw.tenant}, not exported: {', '.join(sorted(skipped))}")
    return 0


# --- command line -----------------------------------------------------------------------------------------------


def main(argv=None):
    p = argparse.ArgumentParser(prog="gg.py", description=__doc__.split("\n\n")[0])
    p.add_argument("--ionapi", default=os.environ.get("GG_IONAPI"),
                   help="Backend Service .ionapi file (or set GG_IONAPI)")
    p.add_argument("--base-url", help="gateway URL ending in /genai-gateway/v1, if not derived from the .ionapi file")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("list", help="list the tools in the tenant")
    s.add_argument("--source", choices=("all", "standard", "custom"), default="all")
    s.add_argument("--format", choices=("table", "csv", "json"), default="table")
    s.add_argument("--out", help="write to this file instead of the screen")
    s.set_defaults(run=cmd_list)

    s = sub.add_parser("check", help="check the tenant against tools/ and the skills (read only)")
    s.add_argument("--skills", default=str(DEFAULT_SKILLS), help="the plugin's skills folder")
    s.add_argument("--tools", default=str(DEFAULT_TOOLS), help="folder of tool definitions")
    s.add_argument("--exclude", default=str(DEFAULT_EXCLUDE), help="file of tools left out on purpose")
    s.add_argument("--all", action="store_true", help="also check naming on every tool in effect")
    s.add_argument("--verbose", action="store_true", help="show every difference")
    s.set_defaults(run=cmd_check)

    s = sub.add_parser("apply", help="create or update the customized tools in tools/ (dry run unless --apply)")
    s.add_argument("--tools", default=str(DEFAULT_TOOLS), help="folder of tool definitions")
    s.add_argument("--only", nargs="+", metavar="TOOL", help="only these tools")
    s.add_argument("--apply", action="store_true", help="make the changes")
    s.add_argument("--enable", action="store_true", help="turn the tools on (new tools are turned off otherwise)")
    s.add_argument("--verbose", action="store_true", help="show every difference")
    s.set_defaults(run=cmd_apply)

    s = sub.add_parser("export", help="save customized tool definitions as JSON files")
    s.add_argument("names", nargs="*", metavar="TOOL")
    s.add_argument("--all", action="store_true",
                   help="every customized tool except those in exclude.txt, and remove files for the rest")
    s.add_argument("--exclude", default=str(DEFAULT_EXCLUDE), help="file of tools to leave out")
    s.add_argument("--out", default=str(DEFAULT_TOOLS), help="folder to write to")
    s.set_defaults(run=cmd_export)

    args = p.parse_args(argv)
    if not args.ionapi:
        p.error("pass --ionapi FILE or set GG_IONAPI")
    try:
        gw = Gateway(args.ionapi, args.base_url)
        return args.run(gw, args)
    except GatewayError as e:
        print(f"gg.py: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
