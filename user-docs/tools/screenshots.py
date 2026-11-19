#!/usr/bin/env python3
"""Generate the user-docs screenshots from tools/screens/*.yml.

Run against a local Parcella instance with the built-in sample data and
every module switched on (see tools/dev_server.sh):

    python user-docs/tools/screenshots.py                  # everything
    python user-docs/tools/screenshots.py --only 'members/*'
    python user-docs/tools/screenshots.py --lang de        # German UI -> members/detail.de.png

English screenshots are the default (members/detail.png). With --lang
other than en, each shot is saved with that language as a suffix next to
the English one (issue #365); the German docs then show detail.de.png
and fall back to detail.png where no German shot exists. The --lang
switch changes the club's UI language on the instance and leaves it
there, so switch it back (or run --lang en last) before English shots.

Manifest entries (see STYLE.md):

    - name: members/detail       # -> docs/assets/screenshots/members/detail.png
      url: /members/             # either url ...
      from: /members/            # ... or from + follow: open `from`, take the
      follow: '^/members/[0-9a-f-]{36}$'  # first <a> whose href path (or path?query) matches (re.search)
      # `follow` may also be a LIST of regexes for multi-hop navigation:
      # each one is applied on the page the previous hop landed on, e.g.
      #   from: /parcels/
      #   follow: ['^/parcels/[0-9a-f-]{36}$', '^/parcels/[0-9a-f-]{36}/edit$']
      # (list -> detail -> edit form). A plain string is a single hop.
      full_page: false           # optional
      logout: false              # optional: shoot without being logged in
      wait_for: '#some-element'  # optional CSS selector to wait for
      click: '[data-bs-target="#modal"]'   # optional: click before the shot

Needs: pip install playwright pyyaml; playwright install chromium
(or a system Chrome/Chromium, auto-detected or given via --browser-path).
"""
from __future__ import annotations

import argparse
import fnmatch
import io
import mimetypes
import os
import tarfile
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

TOOLS_DIR = Path(__file__).resolve().parent
MANIFEST_DIR = TOOLS_DIR / "screens"
OUT_DIR = TOOLS_DIR.parent / "docs" / "assets" / "screenshots"

VIEWPORT = {"width": 1440, "height": 900}
TIMEOUT_MS = 15_000
DEFAULT_LANG = "en"  # the docs' default language: its screenshots carry no suffix
SYSTEM_BROWSERS = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]

# No animations/blinking caret, so shots are reproducible (and Bootstrap
# modals open instantly after a `click`).
STABILIZE_CSS = """
*, *::before, *::after {
  transition: none !important; animation: none !important; caret-color: transparent !important;
}
"""
STABILIZE_JS = (
    "document.addEventListener('DOMContentLoaded', () => {"
    " const s = document.createElement('style'); s.textContent = %r;"
    " document.head.appendChild(s); });" % STABILIZE_CSS
)


class ShotError(Exception):
    pass


# ---------------------------------------------------------------------------
# CDN fallback: the app loads Bootstrap, icons, Chart.js etc. from
# cdn.jsdelivr.net. Where that host is unreachable (offline, strict proxy)
# the pages would be photographed unstyled -- so on a failed CDN request
# the same file is served from the package's npm registry tarball, cached
# under ~/.cache/parcella-docs-cdn/. Off with --no-cdn-fallback.
# ---------------------------------------------------------------------------

CDN_CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "parcella-docs-cdn"
NPM_REGISTRY = "https://registry.npmjs.org"
JSDELIVR_RX = re.compile(r"^https://cdn\.jsdelivr\.net/npm/((?:@[^/]+/)?[^/@]+)@([^/]+)/(.+)$")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")


def _npm_package_dir(pkg: str, version: str) -> Path:
    target = CDN_CACHE / f"{pkg.replace('/', '__')}@{version}"
    if (target / "package").is_dir():
        return target
    import httpx  # FastAPI's test/runtime dep, already in the app's requirements

    tarball = f"{NPM_REGISTRY}/{pkg}/-/{pkg.split('/')[-1]}-{version}.tgz"
    data = httpx.get(tarball, follow_redirects=True, timeout=60).raise_for_status().content
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        tf.extractall(target, filter="data")
    # most tarballs use "package/", a few use the package name
    if not (target / "package").is_dir():
        dirs = [d for d in target.iterdir() if d.is_dir()]
        if len(dirs) == 1:
            dirs[0].rename(target / "package")
    return target


def _cdn_route(route) -> None:
    url = route.request.url
    try:
        resp = route.fetch(timeout=10_000)
        if resp.status < 400:
            route.fulfill(response=resp)
            return
    except PlaywrightError:
        pass
    m = JSDELIVR_RX.match(url.split("?")[0])
    if not m:
        route.abort()
        return
    pkg, version, rel = m.groups()
    try:
        root = (_npm_package_dir(pkg, version) / "package").resolve()
        file = (root / rel).resolve()
        if not file.is_file() and ".min." in rel:  # jsdelivr minifies on the fly
            file = (root / rel.replace(".min.", ".")).resolve()
        if root not in file.parents or not file.is_file():
            raise FileNotFoundError(rel)
    except Exception as e:
        print(f"WARN  CDN fallback failed for {url}: {e}")
        route.abort()
        return
    ctype = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
    route.fulfill(status=200, body=file.read_bytes(), headers={
        "content-type": ctype, "access-control-allow-origin": "*"})


def load_entries(only: list[str], files: list[Path]) -> list[dict]:
    entries, seen = [], {}
    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        except yaml.YAMLError as e:
            print(f"WARN  {path.name}: invalid YAML, skipped ({e})")
            continue
        if not isinstance(data, list):
            print(f"WARN  {path.name}: expected a list of entries, skipped")
            continue
        for i, entry in enumerate(data):
            if not isinstance(entry, dict) or not entry.get("name"):
                print(f"WARN  {path.name}[{i}]: entry without a name, skipped")
                continue
            entry = dict(entry, _file=path.name)
            name = entry["name"]
            if name in seen:
                print(f"WARN  {name}: defined in {seen[name]} and {path.name}; the later one wins")
            seen[name] = path.name
            if only and not any(fnmatch.fnmatch(name, pat) for pat in only):
                continue
            entries.append(entry)
    return entries


def check_entry(entry: dict) -> None:
    name = entry["name"]
    if name.startswith("/") or ".." in Path(name).parts or not re.fullmatch(r"[\w./-]+", name):
        raise ShotError(f"invalid name {name!r}")
    has_url, has_from = "url" in entry, "from" in entry or "follow" in entry
    if has_url == has_from:
        raise ShotError("needs either `url` or `from` + `follow`")
    if has_from and not (entry.get("from") and entry.get("follow")):
        raise ShotError("`from` and `follow` must both be set")
    if has_from:
        for pat in follow_patterns(entry):
            try:
                re.compile(pat)
            except re.error as e:
                raise ShotError(f"bad `follow` regex {pat!r}: {e}")


def follow_patterns(entry: dict) -> list[str]:
    f = entry["follow"]
    if isinstance(f, str):
        return [f]
    if isinstance(f, list) and f and all(isinstance(p, str) for p in f):
        return f
    raise ShotError("`follow` must be a regex string or a non-empty list of them")


def goto(page, base_url: str, url: str, logged_in: bool):
    target = urljoin(base_url + "/", url.lstrip("/")) if not url.startswith("http") else url
    try:
        resp = page.goto(target, wait_until="load", timeout=TIMEOUT_MS)
    except PlaywrightError as e:
        raise ShotError(f"could not load {url}: {e.message.splitlines()[0]}")
    if resp is None:
        raise ShotError(f"no response for {url}")
    if resp.status >= 400:
        raise ShotError(f"HTTP {resp.status} on {url}")
    final_path = urlparse(page.url).path
    if logged_in and final_path.startswith("/auth/login") and not url.startswith("/auth/login"):
        raise ShotError(f"{url} redirected to the login page (session lost or no permission?)")
    if final_path.startswith("/auth/change-password") and not url.startswith("/auth/change-password"):
        raise ShotError(f"{url} redirected to the forced password change")
    try:
        page.wait_for_load_state("networkidle", timeout=5_000)
    except PlaywrightError:
        pass  # long-polling pages etc. -- 'load' is good enough
    return resp


def follow_link(page, base_url: str, pattern: str) -> str:
    base = urlparse(base_url)
    rx = re.compile(pattern)
    hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    for href in hrefs:
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        u = urlparse(urljoin(page.url, href))
        if u.netloc and u.netloc != base.netloc:
            continue
        full = u.path + (f"?{u.query}" if u.query else "")
        # the path alone first; path + query too, for patterns like '\?year=\d+$'
        if rx.search(u.path) or (u.query and rx.search(full)):
            return full
    raise ShotError(f"no link on {urlparse(page.url).path} matches {pattern!r}")


def shot_path(name: str, lang: str) -> Path:
    """English is the default image (members/detail.png); any other
    language gets a suffix (members/detail.de.png), which the docs'
    i18n plugin (suffix structure) picks for that language's pages."""
    suffix = "" if lang == DEFAULT_LANG else f".{lang}"
    return OUT_DIR / f"{name}{suffix}.png"


def shoot(page, base_url: str, entry: dict, logged_in: bool, optimize: bool, lang: str = "en") -> Path:
    if "url" in entry:
        goto(page, base_url, str(entry["url"]), logged_in)
    else:
        goto(page, base_url, str(entry["from"]), logged_in)
        for pat in follow_patterns(entry):
            goto(page, base_url, follow_link(page, base_url, pat), logged_in)

    if entry.get("wait_for"):
        try:
            page.wait_for_selector(entry["wait_for"], state="visible", timeout=TIMEOUT_MS)
        except PlaywrightError:
            raise ShotError(f"wait_for {entry['wait_for']!r} never became visible")
    if entry.get("click"):
        try:
            page.click(entry["click"], timeout=TIMEOUT_MS)
        except PlaywrightError as e:
            raise ShotError(f"click {entry['click']!r} failed: {e.message.splitlines()[0]}")
        try:
            page.wait_for_load_state("networkidle", timeout=5_000)
        except PlaywrightError:
            pass
        page.wait_for_timeout(300)  # let modals/dropdowns settle

    page.evaluate("document.fonts && document.fonts.ready")
    out = shot_path(entry["name"], lang)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out), full_page=bool(entry.get("full_page", False)))
    if optimize:
        optimize_png(out)
    return out


def optimize_png(path: Path) -> None:
    if shutil.which("oxipng"):
        subprocess.run(["oxipng", "-q", "-o", "3", "--strip", "safe", str(path)], check=False)
    elif shutil.which("optipng"):
        subprocess.run(["optipng", "-quiet", "-o2", str(path)], check=False)


def login(page, base_url: str, user: str, password: str) -> None:
    goto(page, base_url, "/auth/login", logged_in=False)
    page.fill("input[name=email]", user)
    page.fill("input[name=password]", password)
    with page.expect_navigation(timeout=TIMEOUT_MS):
        page.click("form[action='/auth/login'] button[type=submit]")
    if urlparse(page.url).path.startswith("/auth/login"):
        raise ShotError(f"login as {user} failed")
    if urlparse(page.url).path.startswith("/auth/change-password"):
        raise ShotError(f"{user} must change the password first (log in once by hand, or run "
                        "`tools/dev_server.sh seed` on a throwaway dev instance)")


def ensure_language(page, base_url: str, lang: str) -> None:
    """The UI language is a club-wide setting (Admin -> Settings), not a
    per-user or cookie one -- switch it there if it differs."""
    try:
        goto(page, base_url, "/admin/settings", logged_in=True)
    except ShotError as e:
        print(f"WARN  can't check the UI language ({e}); screenshots use whatever is set")
        return
    select = page.locator("#settings-form select[name=language]")
    if select.count() == 0:
        print("WARN  no language field on /admin/settings; screenshots use whatever is set")
        return
    current = select.input_value()
    if current == lang:
        return
    try:
        select.select_option(lang)
    except PlaywrightError:
        raise ShotError(f"language {lang!r} isn't offered on /admin/settings")
    with page.expect_navigation(timeout=TIMEOUT_MS):
        page.click("button[type=submit][form=settings-form]")
    print(f"INFO  switched the club's UI language from {current!r} to {lang!r} (Admin -> Settings)")


def launch(pw, browser_path: str | None):
    if browser_path:
        return pw.chromium.launch(executable_path=browser_path)
    try:
        return pw.chromium.launch()
    except PlaywrightError as first:
        for exe in SYSTEM_BROWSERS:
            found = shutil.which(exe)
            if found:
                print(f"INFO  Playwright's Chromium unavailable, using {found}")
                return pw.chromium.launch(executable_path=found)
        raise first


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--user", default="admin@parcella.local")
    ap.add_argument("--password", default="admin1234")
    ap.add_argument("--only", action="append", default=[], metavar="GLOB",
                    help="only entries whose name matches (repeatable), e.g. 'members/*'")
    ap.add_argument("--lang", default="en", help="UI language to set before shooting (default: en)")
    ap.add_argument("--manifest", action="append", default=[], metavar="FILE",
                    help="manifest file(s) to use instead of tools/screens/*.yml")
    ap.add_argument("--browser-path", help="Chrome/Chromium executable instead of Playwright's own")
    ap.add_argument("--no-cdn-fallback", dest="cdn_fallback", action="store_false",
                    help="don't serve cdn.jsdelivr.net assets from npm tarballs when the CDN is unreachable")
    ap.add_argument("--optimize", action="store_true", help="run oxipng/optipng on each PNG if installed")
    args = ap.parse_args()
    base_url = args.base_url.rstrip("/")

    files = [Path(m) for m in args.manifest] or sorted(MANIFEST_DIR.glob("*.yml"))
    entries = load_entries(args.only, files)
    if not entries:
        print(f"No manifest entries found in {MANIFEST_DIR}" + (f" matching {args.only}" if args.only else ""))
        return 1

    ok, failed = [], []
    with sync_playwright() as pw:
        browser = launch(pw, args.browser_path)
        ctx_opts = dict(viewport=VIEWPORT, device_scale_factor=1, locale="de-DE",
                        timezone_id="Europe/Berlin", color_scheme="light")
        def new_context():
            ctx = browser.new_context(**ctx_opts)
            ctx.add_init_script(STABILIZE_JS)
            if args.cdn_fallback:
                ctx.route("https://cdn.jsdelivr.net/**", _cdn_route)
            return ctx

        auth_ctx = new_context()
        page = auth_ctx.new_page()
        try:
            login(page, base_url, args.user, args.password)
            ensure_language(page, base_url, args.lang)
        except ShotError as e:
            print(f"ERROR {e}")
            browser.close()
            return 2

        anon_page = None
        for entry in entries:
            name = entry["name"]
            try:
                check_entry(entry)
                if entry.get("logout"):
                    if anon_page is None:
                        anon_page = new_context().new_page()
                    out = shoot(anon_page, base_url, entry, False, args.optimize, args.lang)
                else:
                    out = shoot(page, base_url, entry, True, args.optimize, args.lang)
                ok.append(name)
                print(f"OK    {name} -> {out.relative_to(TOOLS_DIR.parent)}")
            except ShotError as e:
                failed.append(name)
                print(f"WARN  {name} ({entry['_file']}): {e}")
            except PlaywrightError as e:
                failed.append(name)
                print(f"WARN  {name} ({entry['_file']}): {e.message.splitlines()[0]}")
        browser.close()

    print(f"\n{len(ok)} OK, {len(failed)} failed")
    if failed:
        print("Failed:\n  " + "\n  ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
