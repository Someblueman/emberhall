"""Let a resident see one of its own pages the way a visitor would.

Residents cannot run a browser in their rooms, so until 16 November no resident
had ever seen a page of theirs rendered, and three milestones were waiting for
the Steward to open a page by hand. This trusted action runs the host's Chrome,
headless, on one HTML file from the asking resident's room and gives back
screenshots at phone and desktop width, the page's text after its scripts have
run, its headings, its keyboard tab order, a few plain accessibility facts and
any script errors. A short list of steps (click, fill, focus, wait) can be
played first, so a form or a two-phase page can be taken to a later state.

Bounds. The page is served from a throwaway loopback server rooted at the
room, and Chrome is told to use that same server as its proxy for everything,
loopback included, so any other address (the internet, other local services)
answers 403. Nothing is opened as file://. Each look uses a fresh browser
profile, lasts at most a minute, and writes only inside the room's
.house-mailbox/views/ folder, which is never committed. It cannot press real
keys, speak like a screen reader, or stand in for a person outside the house.
"""
from __future__ import annotations

from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
from urllib.parse import unquote, urlsplit

BROWSERS = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium", "google-chrome", "chromium", "chromium-browser")
WIDTHS = {"phone": (390, 1800), "desktop": (1280, 1800)}
SECONDS = 20
MAX_PAGE = 5_000_000
MAX_STEPS = 30
TEXT_LIMIT = 20_000
REPORT = "house-view-report"

# Played inside the page before it is looked at. Synthetic events only.
DRIVER = """
<script>(function(){
  var steps=%s, errors=[], notes=[];
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||'error').slice(0,300));});
  window.addEventListener('unhandledrejection',function(e){errors.push(('Unhandled rejection: '+String(e.reason)).slice(0,300));});
  var say=console.error;console.error=function(){errors.push(Array.prototype.join.call(arguments,' ').slice(0,300));return say.apply(console,arguments);};
  function find(sel){var el=document.querySelector(sel);if(!el)notes.push('nothing matches '+sel);return el;}
  function play(i){
    if(i>=steps.length)return done();
    var s=steps[i],el;
    try{
      if(s.click){el=find(s.click);if(el){el.focus&&el.focus();el.click();}}
      else if(s.fill){el=find(s.fill[0]);if(el){el.focus&&el.focus();el.value=s.fill[1];
        el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}}
      else if(s.focus){el=find(s.focus);if(el)el.focus();}
    }catch(e){notes.push('step '+(i+1)+' failed: '+String(e).slice(0,200));}
    setTimeout(function(){play(i+1);},s.wait||150);
  }
  function done(){
    var a=document.activeElement,box=document.createElement('script');
    box.type='application/json';box.id='%s';
    box.textContent=JSON.stringify({errors:errors.slice(0,30),notes:notes.slice(0,30),steps:steps.length,
      focused:a&&a!==document.body?(a.tagName.toLowerCase()+(a.id?'#'+a.id:'')):null,
      secure:window.isSecureContext,width:window.innerWidth,
      overflow:document.documentElement.scrollWidth>window.innerWidth+1});
    document.documentElement.appendChild(box);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(function(){play(0);},100);});
  else setTimeout(function(){play(0);},100);
})();</script>
"""


def browser() -> str:
    for candidate in BROWSERS:
        found = candidate if os.path.isabs(candidate) and os.access(candidate, os.X_OK) else shutil.which(candidate)
        if found:
            return found
    raise ValueError("no Chrome or Chromium is installed on the host; ask the Steward (need-raise, kind hardware)")


def page_path(workspace: Path, name: str) -> Path:
    """One committed-or-working HTML file inside the room; never a hidden path or a link out of it."""
    parts = Path(name).parts
    if (not name or Path(name).is_absolute() or any(part in {"..", "."} or part.startswith(".") for part in parts)
            or not name.endswith((".html", ".htm"))):
        raise ValueError("view takes one .html file by its path inside your room")
    target = workspace.joinpath(*parts)
    if target.is_symlink() or not target.is_file() or workspace.resolve() not in target.resolve().parents:
        raise ValueError("that page is not a regular file inside your room")
    if target.stat().st_size > MAX_PAGE:
        raise ValueError("that page is larger than the viewer accepts")
    return target


def steps_from(workspace: Path, name: str | None) -> list[dict]:
    if name is None:
        return []
    parts = Path(name).parts
    if Path(name).is_absolute() or any(part in {"..", "."} or part.startswith(".") for part in parts):
        raise ValueError("steps is a JSON file by its path inside your room")
    source = workspace.joinpath(*parts)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 100_000:
        raise ValueError("steps is a small regular JSON file inside your room")
    steps = json.loads(source.read_text())
    if not isinstance(steps, list) or len(steps) > MAX_STEPS:
        raise ValueError(f"steps is a list of at most {MAX_STEPS} steps")
    for step in steps:
        ok = isinstance(step, dict) and len(set(step) & {"click", "fill", "focus"}) <= 1 and set(step) <= {
            "click", "fill", "focus", "wait"}
        ok = ok and all(isinstance(step.get(key, ""), str) and len(step.get(key, "")) <= 300 for key in ("click", "focus"))
        ok = ok and ("fill" not in step or (isinstance(step["fill"], list) and len(step["fill"]) == 2 and all(
            isinstance(part, str) and len(part) <= 5000 for part in step["fill"])))
        ok = ok and type(step.get("wait", 0)) is int and 0 <= step.get("wait", 0) <= 2000
        if not ok:
            raise ValueError('each step is {"click": SELECTOR}, {"fill": [SELECTOR, TEXT]}, {"focus": SELECTOR} '
                             'or {"wait": MILLISECONDS}, with an optional wait')
    return steps


def server(root: Path, page: Path, steps: list[dict]):
    """Serve the room on loopback and refuse, as a proxy, every other address."""
    driver = (DRIVER % (json.dumps(steps).replace("</", "<\\/"), REPORT)).encode()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def refuse(self):
            self.send_response(403); self.send_header("Content-Length", "0"); self.end_headers()

        do_CONNECT = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = refuse

        def do_GET(self):
            target = urlsplit(self.path)
            mine = f"127.0.0.1:{self.server.server_address[1]}"
            if target.netloc not in {"", mine} or target.scheme not in {"", "http"}:
                return self.refuse()
            parts = [part for part in unquote(target.path).split("/") if part]
            if any(part in {"..", "."} or part.startswith(".") for part in parts):
                return self.refuse()
            file = root.joinpath(*parts)
            try:
                if file.is_symlink() or not file.is_file() or root.resolve() not in file.resolve().parents:
                    raise OSError
                body = file.read_bytes() if file.stat().st_size <= 30_000_000 else b""
            except OSError:
                self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers()
                return
            if file == page:
                body += driver
            kind = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        do_HEAD = do_GET

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def chrome(executable: str, port: int, profile: Path, size: tuple[int, int], url: str, *extra: str) -> str:
    argv = [executable, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", "--disable-extensions", "--disable-sync", "--disable-background-networking",
            "--disable-component-update", "--disable-default-apps", "--mute-audio", "--incognito",
            # Nothing leaves except through the refusing proxy: no direct UDP and no name lookups.
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp", "--dns-prefetch-disable",
            "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1",
            f"--user-data-dir={profile}", f"--proxy-server=http://127.0.0.1:{port}", "--proxy-bypass-list=<-loopback>",
            f"--window-size={size[0]},{size[1]}", "--virtual-time-budget=8000", "--run-all-compositor-stages-before-draw",
            *extra, url]
    done = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=SECONDS, start_new_session=True)
    return done.stdout.decode("utf-8", errors="replace")


class Reader(HTMLParser):
    """Text, headings, tab order and a few accessibility facts from the rendered DOM."""
    FOCUS = {"a", "button", "input", "select", "textarea", "summary"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.headings, self.stops, self.facts = [], [], [], {"images_without_alt": 0, "unlabelled_controls": 0}
        self.skip, self.heading, self.stop, self.labels, self.lang, self.title, self.in_title = 0, None, None, set(), None, "", False
        self.report, self.in_report, self.controls = "", False, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("id") == REPORT:
            self.in_report = True
        if tag in {"script", "style", "template", "noscript"}:
            self.skip += 1
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.in_title = True
        if tag == "meta" and (attrs.get("http-equiv") or "").lower() == "content-security-policy":
            self.facts["own_policy"] = (attrs.get("content") or "")[:300]
        if re.fullmatch(r"h[1-6]", tag):
            self.heading = [tag, ""]
        if tag == "img" and "alt" not in attrs:
            self.facts["images_without_alt"] += 1
        if tag == "label" and attrs.get("for"):
            self.labels.add(attrs["for"])
        hidden = "hidden" in attrs or attrs.get("aria-hidden") == "true" or attrs.get("type") == "hidden"
        index = attrs.get("tabindex")
        focusable = (tag in self.FOCUS and (tag != "a" or "href" in attrs) and "disabled" not in attrs) or index is not None
        if focusable and not hidden and index != "-1":
            order = int(index) if index and index.lstrip("-").isdigit() else 0
            self.stop = {"tag": tag, "name": attrs.get("aria-label") or attrs.get("title") or attrs.get("placeholder") or
                         attrs.get("value") or "", "order": order, "id": attrs.get("id")}
            self.stops.append(self.stop)
            if tag in {"input", "select", "textarea"}:
                self.controls.append((attrs.get("id"), bool(attrs.get("aria-label") or attrs.get("aria-labelledby")
                                                           or attrs.get("title"))))
            if tag in {"input", "img"}:
                self.stop = None

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template", "noscript"}:
            self.skip = max(0, self.skip - 1)
            self.in_report = False
        if tag == "title":
            self.in_title = False
        if self.heading and tag == self.heading[0]:
            self.headings.append(f"{tag}: {' '.join(self.heading[1].split())[:120]}")
            self.heading = None
        if self.stop and tag == self.stop["tag"]:
            self.stop = None
        if tag in {"p", "div", "li", "tr", "section", "article", "br", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.text.append("\n")

    def handle_data(self, data):
        if self.in_report:
            self.report += data
        if self.in_title:
            self.title += data
        if self.skip:
            return
        self.text.append(data)
        if self.heading:
            self.heading[1] += data
        if self.stop is not None and not self.stop["name"]:
            self.stop["name"] = " ".join(data.split())[:80]


def read(dom: str) -> dict:
    reader = Reader()
    reader.feed(dom)
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(reader.text))
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    ordered = sorted((stop for stop in reader.stops if stop["order"] > 0), key=lambda stop: stop["order"]) + [
        stop for stop in reader.stops if stop["order"] == 0]
    reader.facts["unlabelled_controls"] = sum(1 for ident, named in reader.controls
                                              if not named and (ident is None or ident not in reader.labels))
    try:
        report = json.loads(reader.report) if reader.report else None
    except ValueError:
        report = None
    return {"title": " ".join(reader.title.split())[:200], "language": reader.lang,
            "text": text[:TEXT_LIMIT], "text_truncated": len(text) > TEXT_LIMIT, "headings": reader.headings[:80],
            "tab_order": [f"{n}. {stop['tag']}{'#' + stop['id'] if stop['id'] else ''}: {stop['name'] or '(no name)'}"
                          for n, stop in enumerate(ordered[:80], 1)],
            "tab_stops": len(ordered), **reader.facts, "page_report": report}


def render(workspace: Path, name: str, steps_name: str | None = None) -> dict:
    page = page_path(workspace, name)
    steps = steps_from(workspace, steps_name)
    executable = browser()
    out = workspace / ".house-mailbox" / "views"
    out.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", name[:-len(Path(name).suffix)]).strip("-")[-60:] or "page"
    httpd = server(workspace, page, steps)
    port = httpd.server_address[1]
    url = f"http://127.0.0.1:{port}/" + "/".join(Path(name).parts)
    result = {"page": name, "steps_played": len(steps), "screenshots": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="house-view-") as scratch:
            for label, size in WIDTHS.items():
                shot = out / f"{stem}-{label}.png"
                shot.unlink(missing_ok=True)
                chrome(executable, port, Path(scratch) / label, size, url, f"--screenshot={shot}")
                if shot.is_file():
                    shot.chmod(0o600)
                    result["screenshots"][label] = {"file": str(shot.relative_to(workspace)), "width": size[0],
                                                    "height": size[1]}
                result[label] = read(chrome(executable, port, Path(scratch) / (label + "-dom"), size, url, "--dump-dom"))
    except subprocess.TimeoutExpired:
        raise ValueError(f"the page did not settle within {SECONDS} seconds") from None
    finally:
        httpd.shutdown(); httpd.server_close()
    phone, desktop = result.pop("phone"), result.pop("desktop")
    for label, view in (("phone", phone), ("desktop", desktop)):
        report = view.pop("page_report") or {}
        silent = ("the page's own content policy forbids scripts, so steps and script errors are not observed"
                  if "own_policy" in view else "the page did not finish loading within the viewer's time")
        result.setdefault("script_errors", {})[label] = report.get("errors", [silent])
        result.setdefault("step_notes", {})[label] = report.get("notes", [])
        result.setdefault("wider_than_screen", {})[label] = report.get("overflow")
        result.setdefault("focused_after_steps", {})[label] = report.get("focused")
    result.update(desktop)
    result["phone_text_differs"] = phone["text"] != desktop["text"]
    result["note"] = ("Open the screenshot files to look at the page. This is the house's own Chrome with the network "
                      "refused; it presses no real keys and speaks nothing, so claim only what is shown here.")
    return result
