#!/usr/bin/env python3
"""Check this repository against the Claude plugin directory's automated rules.

`claude plugin validate` checks the manifests and the skills' front matter. This
script checks the rest of the pre-submission checklist
(https://claude.com/docs/plugins/pre-submission-checklist): the repository's
layout, size and file names; the plugin folder's README, license, file types
and file sizes; that every host the plugin names is described in its README;
that no ION API credentials are committed; and, with --base, that the plugin's
version was raised when anything in the plugin folder changed.

Errors are rules that would block the submission, stop validation, or hold the
plugin for a reviewer. Warnings are things a reviewer may still ask about.

Usage:
    python3 scripts/ci/check-plugin.py [--base <commit>]

Run it from anywhere in the repository. Python 3.9 or later, nothing to install.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path, PurePosixPath

KIB = 1024
MIB = 1024 * KIB

MAX_REPO_ARCHIVE = 50 * MIB
MAX_REPO_UNPACKED = 256 * MIB
MAX_REPO_ENTRIES = 10_000
MAX_FILE = 5 * MIB
MAX_INSPECTED_FILE = 256 * KIB
NEAR_INSPECTED_LIMIT = 230 * KIB
MAX_PLUGIN_FILES = 512
MIN_README_WORDS = 40

IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
FONTS = {".woff", ".woff2", ".ttf", ".otf"}
SYSTEM_FILES = {".ds_store", "thumbs.db", "desktop.ini", "__macosx"}
WINDOWS_DEVICES = re.compile(r"^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?$", re.IGNORECASE)
WINDOWS_INVALID = re.compile(r'[<>:"|?*\\\x00-\x1f]')
SAFE_FOLDER = re.compile(r"^[A-Za-z0-9._-]+$")
PLUGIN_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
RESERVED_NAMES = {"claude", "anthropic", "official", "plugin", "mcp", "test"}
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
URL_FIELDS = ("homepage", "repository", "documentationUrl", "supportUrl", "privacyPolicyUrl")
REWRITING_ATTRIBUTES = re.compile(r"(?<![\w-])(export-ignore|export-subst|filter|ident|working-tree-encoding)\b")
PACKAGE_CONFIGS = {".npmrc", ".yarnrc", ".yarnrc.yml", "bunfig.toml", "uv.toml", "pip.conf", ".pypirc"}
LOCKFILES = {"package-lock.json", "npm-shrinkwrap.json", "bun.lock", "bun.lockb"}
BUNDLES = {".mcpb", ".dxt"}
LAUNCHER = re.compile(r"\b(npx|bunx|uvx|pnpm\s+dlx|yarn\s+dlx|pipx\s+run)\s+(?:-\S+\s+)*([^\s\"']+)")
PINNED = re.compile(r"(@\d+\.\d+\.\d+[^\s\"']*|==\d+\.\d+\.\d+\S*)$")
URL_HOST = re.compile(r"\bhttps?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
# Hosts that appear only as XML namespaces and are never fetched.
NAMESPACE_HOSTS = {"www.w3.org"}
IONAPI_KEYS = re.compile(r'"(saak|sask)"\s*:\s*"[^"]+"')

ON_CI = os.environ.get("GITHUB_ACTIONS") == "true"


class Report:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def _emit(self, level, path, message):
        if ON_CI:
            location = f" file={path}" if path else ""
            print(f"::{level}{location}::{message}")
        else:
            where = f"{path}: " if path else ""
            print(f"{level.upper()}: {where}{message}")

    def error(self, path, message):
        self.errors += 1
        self._emit("error", path, message)

    def warning(self, path, message):
        self.warnings += 1
        self._emit("warning", path, message)


def git(*args, check=True):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def repo_files():
    """Files that are or would be committed: tracked plus untracked, not ignored."""
    listed = git("ls-files", "-z", "--cached", "--others", "--exclude-standard").stdout.split("\0")
    return sorted({p for p in listed if p and os.path.lexists(p)})


def words_outside_code(markdown):
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", " ", markdown, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    return len(re.findall(r"[A-Za-z0-9][\w'’-]*", text))


def is_text(data):
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def is_complete_image(ext, data):
    if ext == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n") and data[-12:-8] == b"\x00\x00\x00\x00" and data[-8:-4] == b"IEND"
    if ext in (".jpg", ".jpeg"):
        return data.startswith(b"\xff\xd8") and data.rstrip(b"\x00").endswith(b"\xff\xd9")
    if ext == ".gif":
        return data[:6] in (b"GIF87a", b"GIF89a") and data.endswith(b"\x3b")
    if ext == ".webp":
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP" and int.from_bytes(data[4:8], "little") + 8 == len(data)
    return False


def semver_key(version):
    match = SEMVER.match(version or "")
    return tuple(int(part) for part in match.groups()) if match else None


def check_repository(report, files):
    modes = {}
    for line in git("ls-files", "-s", "-z").stdout.split("\0"):
        if line:
            meta, path = line.split("\t", 1)
            modes[path] = meta.split()[0]

    entries = set()
    folded = {}
    total = 0
    for path in files:
        parts = PurePosixPath(path).parts
        for i in range(1, len(parts) + 1):
            entries.add("/".join(parts[:i]))
        for part in parts:
            if WINDOWS_INVALID.search(part) or part.endswith((".", " ")) or WINDOWS_DEVICES.match(part):
                report.error(path, f'"{part}" is not a valid file name on Windows, so the directory cannot validate the repository.')
                break
        if os.path.islink(path) or modes.get(path) == "120000":
            report.error(path, "Symbolic link. Commit the file itself.")
            continue
        if modes.get(path) == "160000":
            report.error(path, "Git submodule. Commit the files themselves.")
            continue
        size = os.path.getsize(path)
        total += size
        with open(path, "rb") as handle:
            head = handle.read(200)
        if head.startswith(b"version https://git-lfs.github.com/spec/"):
            report.error(path, "Git LFS pointer file. Commit the file itself.")
        if path.endswith(".ionapi"):
            report.error(path, "ION API credentials file. Remove it from the repository and delete the authorized application in ION API.")
        if PurePosixPath(path).name == ".gitattributes":
            with open(path, encoding="utf-8", errors="replace") as handle:
                for number, line in enumerate(handle, 1):
                    found = REWRITING_ATTRIBUTES.search(line.split("#", 1)[0])
                    if found:
                        report.error(path, f"Line {number} sets {found.group(1)}, which stops the directory from validating the repository.")

    for entry in entries:
        folded.setdefault(entry.lower(), []).append(entry)
    for names in folded.values():
        if len(names) > 1:
            report.error(names[0], f"Names differ only by capitalization: {', '.join(sorted(names))}.")

    if len(entries) >= MAX_REPO_ENTRIES:
        report.error(None, f"The repository has {len(entries)} files and folders; the directory validates fewer than {MAX_REPO_ENTRIES}.")
    if total >= MAX_REPO_UNPACKED:
        report.error(None, f"The repository is {total / MIB:.1f} MiB unpacked; the limit is {MAX_REPO_UNPACKED // MIB} MiB.")
    archive = subprocess.run(["git", "archive", "--format=tar.gz", "HEAD"], capture_output=True)
    if archive.returncode == 0 and len(archive.stdout) >= MAX_REPO_ARCHIVE:
        report.error(None, f"The repository archive is {len(archive.stdout) / MIB:.1f} MiB; the limit is {MAX_REPO_ARCHIVE // MIB} MiB.")

    for path in files:
        if path.lower().endswith(tuple(IMAGES | FONTS)) or os.path.islink(path):
            continue
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except (UnicodeDecodeError, OSError):
            continue
        if IONAPI_KEYS.search(text):
            report.error(path, "Contains ION API service account keys (saak or sask). Remove them and rotate the credentials.")


def plugin_folders(report):
    marketplace = Path(".claude-plugin/marketplace.json")
    if not marketplace.is_file():
        report.error(str(marketplace), "Missing.")
        return []
    try:
        data = json.loads(marketplace.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.error(str(marketplace), f"Not valid JSON: {exc}.")
        return []
    folders = []
    for entry in data.get("plugins", []):
        source = entry.get("source")
        if isinstance(source, str):
            folders.append(PurePosixPath(os.path.normpath(source)).as_posix())
    return folders


def inside(folder, target):
    folder = os.path.realpath(folder)
    return os.path.commonpath([folder, os.path.realpath(target)]) == folder


def check_manifest(report, folder):
    path = f"{folder}/.claude-plugin/plugin.json"
    if not os.path.isfile(path):
        report.error(path, "Missing. The plugin folder must contain .claude-plugin/plugin.json.")
        return None
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.error(path, f"Not valid JSON: {exc}.")
        return None

    name = manifest.get("name", "")
    if not PLUGIN_NAME.match(name):
        report.error(path, f'name "{name}" must be lowercase letters, digits and hyphens, up to 64 characters, starting and ending with a letter or digit.')
    if name in RESERVED_NAMES:
        report.error(path, f'name "{name}" is a reserved word.')
    for field in ("description", "author", "version"):
        if not manifest.get(field):
            report.error(path, f"Set {field}.")
    if manifest.get("version") and not semver_key(manifest["version"]):
        report.error(path, f'version "{manifest["version"]}" is not a semantic version such as 1.2.3.')

    author = manifest.get("author") if isinstance(manifest.get("author"), dict) else {}
    for label, value in (("displayName", manifest.get("displayName")), ("author.name", author.get("name"))):
        if value and any(unicodedata.category(ch) == "Cf" or ord(ch) > 0x24F for ch in value):
            report.error(path, f"{label} has invisible characters or letters outside the Latin script.")

    urls = [(field, manifest.get(field)) for field in URL_FIELDS] + [("author.url", author.get("url"))]
    for field, value in urls:
        if isinstance(value, str) and value and not value.startswith("https://"):
            report.error(path, f"{field} must be an https:// URL.")

    def walk(value, key):
        if isinstance(value, dict):
            for k, v in value.items():
                yield from walk(v, k)
        elif isinstance(value, list):
            for v in value:
                yield from walk(v, key)
        elif isinstance(value, str) and (value.startswith(("./", "../")) or "/../" in value):
            yield key, value

    for key, value in walk(manifest, None):
        target = os.path.join(folder, value)
        if not inside(folder, target):
            report.error(path, f'{key} "{value}" points outside the plugin folder.')
        elif not os.path.exists(target):
            report.error(path, f'{key} "{value}" does not exist.')

    if manifest.get("icon") is None:
        report.warning(path, "No icon. The directory listing shows the icon from plugin.json.")
    return manifest


def check_plugin(report, folder, all_files):
    for part in PurePosixPath(folder).parts:
        if not SAFE_FOLDER.match(part):
            report.error(folder, f'Folder "{part}" on the plugin path may only use letters, digits, dots, hyphens and underscores.')

    manifest = check_manifest(report, folder)
    prefix = folder.rstrip("/") + "/"
    files = [p for p in all_files if p.startswith(prefix)]

    readme = Path(folder, "README.md")
    readme_text = ""
    if not readme.is_file():
        report.error(str(readme), "Missing. The directory shows the README as the listing's description.")
    else:
        readme_text = readme.read_text(encoding="utf-8")
        count = words_outside_code(readme_text)
        if count < MIN_README_WORDS:
            report.error(str(readme), f"{count} words outside code blocks; the directory needs at least {MIN_README_WORDS}.")

    if not Path(folder, "LICENSE").is_file() and not (manifest or {}).get("license"):
        report.error(folder, "Add a LICENSE file or set license in plugin.json.")

    if len(files) > MAX_PLUGIN_FILES:
        report.error(folder, f"{len(files)} files; a plugin with more than {MAX_PLUGIN_FILES} is held for a reviewer.")

    icon = os.path.normpath(os.path.join(folder, (manifest or {}).get("icon") or "")) if (manifest or {}).get("icon") else None
    shown = {os.path.normpath(os.path.join(folder, m)) for m in re.findall(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)", readme_text)}
    shown |= {os.path.normpath(os.path.join(folder, m)) for m in re.findall(r"<img[^>]+src=[\"']([^\"']+)", readme_text)}
    hosts = {}
    package_json = Path(folder, "package.json").is_file()

    for path in files:
        rel = path[len(prefix):]
        name = PurePosixPath(path).name
        ext = PurePosixPath(path).suffix.lower()
        if any(part.lower() in SYSTEM_FILES for part in PurePosixPath(rel).parts):
            report.error(path, "macOS or Windows system file. Remove it and add it to .gitignore.")
            continue
        if os.path.islink(path):
            continue
        size = os.path.getsize(path)
        if size >= MAX_FILE:
            report.error(path, f"{size / MIB:.1f} MiB; every file in the plugin must be under {MAX_FILE // MIB} MiB.")
        if ext in BUNDLES:
            report.error(path, "MCP server bundle. Declare the server with command and args, or with url.")
        if name in PACKAGE_CONFIGS:
            report.error(path, "Package manager configuration that can set a registry or package source.")
        if name in LOCKFILES and package_json and "/" not in rel:
            report.warning(path, "Dependencies install from a lockfile, which a reviewer always checks.")

        data = Path(path).read_bytes()
        if ext in IMAGES:
            if not is_complete_image(ext, data):
                report.error(path, f"Not a complete {ext[1:].upper()} image.")
            if os.path.normpath(path) not in shown:
                what = "the icon" if os.path.normpath(path) == icon else "a bundled image"
                report.warning(path, f"This is {what}, and README.md doesn't show it with Markdown image syntax, so a reviewer may hold it.")
            continue
        if ext in FONTS:
            continue
        if not is_text(data):
            report.error(path, "Binary file. A plugin may hold text files, PNG, JPEG, GIF and WebP images and fonts; anything else is held for a reviewer.")
            continue
        if size >= MAX_INSPECTED_FILE:
            report.error(path, f"{size / KIB:.0f} KiB; files other than images and fonts must be under {MAX_INSPECTED_FILE // KIB} KiB or the plugin is held for a reviewer.")
        elif size >= NEAR_INSPECTED_LIMIT:
            report.warning(path, f"{size / KIB:.0f} KiB, close to the {MAX_INSPECTED_FILE // KIB} KiB limit for files other than images and fonts.")

        text = data.decode("utf-8")
        if rel != ".claude-plugin/plugin.json":  # its URLs are listing links, not destinations
            for host in URL_HOST.findall(text):
                hosts.setdefault(host.lower(), path)
        if re.search(r"`[^`\n]*\.(png|jpe?g|gif|webp|woff2?|ttf|otf)`", text, re.IGNORECASE):
            report.warning(path, "Names an image or font path in backticks. Show bundled images in README.md with Markdown image syntax instead.")
        if rel == ".mcp.json" or rel.startswith("hooks/"):
            if ext == ".json":
                try:
                    json.loads(text)
                except json.JSONDecodeError as exc:
                    report.error(path, f"Not valid JSON: {exc}.")
            for launcher, package in LAUNCHER.findall(text):
                if not PINNED.search(package) or package.endswith("@latest"):
                    report.error(path, f'{launcher} runs "{package}" without an exact version, for example {package}@1.2.3.')

    readme_lower = readme_text.lower()
    for host, path in sorted(hosts.items()):
        if host not in NAMESPACE_HOSTS and host not in readme_lower:
            report.error(path, f"Names {host}, which README.md doesn't mention. Describe in README.md everything the plugin sends to or fetches from it.")


def check_version(report, folder, base):
    if git("cat-file", "-e", f"{base}^{{commit}}", check=False).returncode != 0:
        report.warning(None, f"Base commit {base} isn't in this clone, so the version raise wasn't checked.")
        return
    changed = [p for p in git("diff", "--name-only", base, "--", folder).stdout.splitlines() if p]
    changed += [p for p in git("ls-files", "--others", "--exclude-standard", "--", folder).stdout.splitlines() if p]
    if not changed:
        return
    path = f"{folder}/.claude-plugin/plugin.json"
    before = git("show", f"{base}:{path}", check=False)
    if before.returncode != 0:
        return
    try:
        old = json.loads(before.stdout).get("version")
        new = json.loads(Path(path).read_text(encoding="utf-8")).get("version")
    except (json.JSONDecodeError, OSError):
        return
    old_key, new_key = semver_key(old), semver_key(new)
    if old_key and new_key and new_key <= old_key:
        report.error(path, f"{len(changed)} file(s) in {folder} changed since {base[:12]}, but version is still {new} (was {old}). Raise it so installed copies update.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--base", help="commit to compare with for the version raise")
    args = parser.parse_args()

    root = git("rev-parse", "--show-toplevel").stdout.strip()
    os.chdir(root)

    report = Report()
    files = repo_files()
    check_repository(report, files)
    folders = plugin_folders(report)
    for folder in folders:
        check_plugin(report, folder, files)
        if args.base:
            check_version(report, folder, args.base)

    checked = ", ".join(folders) or "no plugin"
    print(f"Checked {len(files)} files and {checked}: {report.errors} error(s), {report.warnings} warning(s).")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
