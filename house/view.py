"""Let a resident see and try one of its own pages the way a visitor would.

Residents cannot run a browser in their rooms, so until 16 November no resident
had ever seen a page of theirs rendered, and three milestones were waiting for
the Steward to open a page by hand. This trusted action runs the host's Chrome,
headless, on one HTML file from the asking resident's room and gives back
screenshots at a true phone width and at desktop width, the text a visitor
would see, its headings, what every form field holds, the order real Tab
presses visit, what is too wide for the screen, and any script errors. A short
list of steps (click, fill, focus, press a key, wait) is played first with
real mouse and keyboard input, so a form or a two-phase page can be taken to a
later state.

The first viewer injected a script into the page to play the steps and asked
Chrome for a narrow window. A page with its own content policy refused that
script, and Chrome never makes a window narrower than 500 pixels, so the
"phone" picture was a cropped wider page. Residents found both the same
afternoon. The browser is now driven from outside through its debugging pipe:
the page's bytes and policy are untouched, the phone is an emulated 390 pixel
device, and clicks and keys are the browser's own.

Bounds. The page is served from a throwaway loopback server rooted at the
room, and Chrome is told to use that same server as its proxy for everything,
loopback included, so any other address (the internet, other local services)
answers 403. Nothing is opened as file://. The debugging pipe is a pair of
file descriptors held by this process alone; no debugging port is opened. A
resident supplies only the page path and the list of steps, never script.
Each look uses a fresh browser profile, lasts at most a minute, and writes
only inside the room's .house-mailbox/views/ folder, which is never committed.
It cannot speak like a screen reader or stand in for a person outside the house.
"""
from __future__ import annotations

import base64
import fcntl
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import select
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from urllib.parse import unquote, urlsplit

BROWSERS = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium", "google-chrome", "chromium", "chromium-browser")
# Layout width, height of one screenful, pixel density, and whether it is a phone.
DEVICES = {"phone": (390, 780, 2, True), "desktop": (1280, 1100, 1, False)}
SCREENS = 3            # screenfuls photographed from the top of the page
SECONDS = 25           # for one device, from launch to the last picture
MAX_PAGE = 5_000_000
MAX_STEPS = 30
TEXT_LIMIT = 20_000
WALK = 60              # Tab presses in the keyboard walk
# Keys a step may press: name -> (key, code, virtual key code, text typed).
KEYS = {"Tab": ("Tab", "Tab", 9, ""), "Enter": ("Enter", "Enter", 13, "\r"), "Space": (" ", "Space", 32, " "),
        "Escape": ("Escape", "Escape", 27, ""), "Backspace": ("Backspace", "Backspace", 8, ""),
        "Delete": ("Delete", "Delete", 46, ""), "ArrowUp": ("ArrowUp", "ArrowUp", 38, ""),
        "ArrowDown": ("ArrowDown", "ArrowDown", 40, ""), "ArrowLeft": ("ArrowLeft", "ArrowLeft", 37, ""),
        "ArrowRight": ("ArrowRight", "ArrowRight", 39, ""), "Home": ("Home", "Home", 36, ""),
        "End": ("End", "End", 35, ""), "PageUp": ("PageUp", "PageUp", 33, ""),
        "PageDown": ("PageDown", "PageDown", 34, "")}
PRESSES = frozenset(KEYS) | {"Shift+Tab"}

# Small readers run from outside the page, in a world of their own: they see the
# page's elements but not its script, and the page cannot see or replace them.
NAME = """function name(el){if(!el||el===document.body||el===document.documentElement)return null;
  var t=(el.getAttribute('aria-label')||el.innerText||el.value||el.getAttribute('placeholder')||el.getAttribute('title')
    ||el.getAttribute('alt')||'').replace(/\\s+/g,' ').trim().slice(0,80);
  return el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+(t?': '+t:'');}"""
LOCATE = "(function(sel){" + NAME + """
  var el=document.querySelector(sel);if(!el)return {missing:true};
  el.scrollIntoView({block:'center',inline:'center'});var r=el.getBoundingClientRect();
  return {x:r.left+r.width/2,y:r.top+r.height/2,shown:r.width>0&&r.height>0,tag:el.tagName.toLowerCase(),
    name:name(el)};})(%s)"""
FILL = "(function(sel,value){" + NAME + """
  var el=document.querySelector(sel);if(!el)return {missing:true};
  el.focus();
  if(el.tagName==='SELECT'||/^(checkbox|radio|range|color|date|time|file)$/.test(el.type||'')){
    if(el.type==='checkbox'||el.type==='radio')el.checked=!/^(|false|0|off|no)$/i.test(value);else el.value=value;
    el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));
    return {set:true,name:name(el)};}
  if(el.select)el.select();else if(el.isContentEditable)document.getSelection().selectAllChildren(el);
  return {typed:true,name:name(el)};})(%s,%s)"""
FOCUS = "(function(sel){" + NAME + """var el=document.querySelector(sel);if(!el)return {missing:true};el.focus();
  return {name:name(document.activeElement)};})(%s)"""
ACTIVE = "(function(){" + NAME + "return name(document.activeElement);})()"
FACTS = "(function(device){" + NAME + """
  var d=document.documentElement,v=window.visualViewport,wide=[],seen=new Set();
  var meta=!!document.querySelector('meta[name=viewport]'),inner=window.innerWidth;
  // A page that declares a viewport is meant to fit the device; one that does not is laid out wide and shrunk.
  var w=meta?Math.min(device,inner):inner;
  function clipped(el){for(var p=el.parentElement;p&&p!==d;p=p.parentElement){
    if(getComputedStyle(p).overflowX!=='visible'&&p.getBoundingClientRect().right<=w+1)return true;}return false;}
  var over=d.scrollWidth>w+1,all=document.body?document.body.querySelectorAll('*'):[];
  for(var i=0;over&&i<all.length&&i<5000&&wide.length<8;i++){var el=all[i],r=el.getBoundingClientRect();
    if(r.width>0&&r.right>w+1){seen.add(el);if(!seen.has(el.parentElement)&&!clipped(el))
      wide.push((name(el)||el.tagName.toLowerCase()).slice(0,70)+' reaches '+Math.round(r.right)+'px');}}
  var fields=[],controls=document.querySelectorAll('input,textarea,select,output');
  for(var j=0;j<controls.length&&fields.length<40;j++){var c=controls[j],kind=c.type||c.tagName.toLowerCase();
    if(kind==='password'||kind==='hidden')continue;
    fields.push({field:c.tagName.toLowerCase()+(c.id?'#'+c.id:c.name?'[name='+c.name+']':''),
      holds:kind==='checkbox'||kind==='radio'?(c.checked?'checked':'unchecked'):String(c.value||c.textContent||'').slice(0,4000)});}
  return {layout_width:d.clientWidth,fit_width:w,page_width:d.scrollWidth,page_height:Math.ceil(Math.max(d.getBoundingClientRect().height,document.body?document.body.getBoundingClientRect().bottom+window.scrollY:0)),
    zoom:v?Math.round(v.scale*1000)/1000:1,
    declares_viewport:meta,over:over,wide:wide,fields:fields,
    focused:name(document.activeElement),title:document.title,
    text:document.body?document.body.innerText:''};})(%d)"""


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
        ok = isinstance(step, dict) and len(set(step) & {"click", "fill", "focus", "press"}) <= 1 and set(step) <= {
            "click", "fill", "focus", "press", "wait"}
        ok = ok and all(isinstance(step.get(key, ""), str) and len(step.get(key, "")) <= 300 for key in ("click", "focus"))
        ok = ok and ("fill" not in step or (isinstance(step["fill"], list) and len(step["fill"]) == 2 and all(
            isinstance(part, str) and len(part) <= 5000 for part in step["fill"])))
        ok = ok and ("press" not in step or (isinstance(step["press"], str) and step["press"] in PRESSES))
        ok = ok and type(step.get("wait", 0)) is int and 0 <= step.get("wait", 0) <= 2000
        if not ok:
            raise ValueError('each step is {"click": SELECTOR}, {"fill": [SELECTOR, TEXT]}, {"focus": SELECTOR}, '
                             '{"press": KEY} or {"wait": MILLISECONDS}, with an optional wait; KEY is one of '
                             + ", ".join(sorted(PRESSES)))
    return steps


def server(root: Path):
    """Serve the room on loopback, each file exactly as written, and refuse, as a proxy, every other address."""

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


class Chrome:
    """One headless Chrome, driven over its debugging pipe and killed afterwards."""

    def __init__(self, executable: str, port: int, profile: Path):
        down, mine_out = os.pipe()      # we write, Chrome reads on its descriptor 3
        mine_in, up = os.pipe()         # Chrome writes on its descriptor 4, we read
        high = [fcntl.fcntl(fd, fcntl.F_DUPFD, 10) for fd in (down, up)]
        os.close(down); os.close(up)
        argv = [executable, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                "--no-default-browser-check", "--disable-extensions", "--disable-sync", "--disable-background-networking",
                "--disable-component-update", "--disable-default-apps", "--mute-audio", "--incognito",
                # Nothing leaves except through the refusing proxy: no direct UDP and no name lookups.
                "--force-webrtc-ip-handling-policy=disable_non_proxied_udp", "--dns-prefetch-disable",
                "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1",
                f"--user-data-dir={profile}", f"--proxy-server=http://127.0.0.1:{port}",
                "--proxy-bypass-list=<-loopback>", "--remote-debugging-pipe", "about:blank"]
        try:
            # The shell only moves the two pipe ends to the descriptors Chrome expects, then becomes Chrome.
            self.process = subprocess.Popen(
                ["/bin/sh", "-c", f'exec "$@" 3<&{high[0]} 4>&{high[1]}', "sh", *argv], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, pass_fds=high, start_new_session=True)
        finally:
            os.close(high[0]); os.close(high[1])
        self.out, self.inp, self.buffer, self.events, self.last = mine_out, mine_in, b"", [], 0
        self.deadline = time.monotonic() + SECONDS
        self.session = None

    def close(self) -> None:
        for fd in (self.out, self.inp):
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.killpg(self.process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass

    def messages(self, until: float):
        """Yield messages from Chrome until the given moment (never past the look's deadline)."""
        while True:
            while b"\0" in self.buffer:
                raw, self.buffer = self.buffer.split(b"\0", 1)
                yield json.loads(raw)
            left = min(until, self.deadline) - time.monotonic()
            if left <= 0 or not select.select([self.inp], [], [], left)[0]:
                return
            chunk = os.read(self.inp, 1 << 16)
            if not chunk:
                raise ValueError("the browser stopped before the page was seen")
            self.buffer += chunk

    def call(self, method: str, params: dict | None = None, root: bool = False) -> dict:
        self.last += 1
        message = {"id": self.last, "method": method, "params": params or {}}
        if self.session and not root:
            message["sessionId"] = self.session
        os.write(self.out, json.dumps(message).encode() + b"\0")
        for answer in self.messages(self.deadline):
            if answer.get("id") == self.last:
                if "error" in answer:
                    raise LookupError(f"{method}: {answer['error'].get('message', 'refused')}")
                return answer.get("result", {})
            if "method" in answer:
                self.events.append(answer)
        raise TimeoutError

    def wait(self, name: str, seconds: float) -> bool:
        """Let the page run for up to this long; true as soon as the named event has arrived."""
        def seen() -> bool:
            return any(event["method"] == name for event in self.events)
        if seen():
            return True
        for answer in self.messages(time.monotonic() + seconds):
            if "method" in answer:
                self.events.append(answer)
                if answer["method"] == name:
                    return True
        return seen()

    def pause(self, milliseconds: int) -> None:
        self.wait("never", milliseconds / 1000)

    def world(self, frame: str) -> None:
        self.context = self.call("Page.createIsolatedWorld", {"frameId": frame, "worldName": "house-view"})[
            "executionContextId"]

    def ask(self, expression: str):
        """Evaluate one of the readers above in the viewer's own world and return its plain value."""
        for attempt in (0, 1):
            try:
                answer = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True,
                                                        "contextId": self.context})
                break
            except LookupError:
                if attempt:      # a step loaded another page; its world is gone, so make a new one once
                    raise
                self.world(self.call("Page.getFrameTree")["frameTree"]["frame"]["id"])
        if "exceptionDetails" in answer:
            raise LookupError(answer["exceptionDetails"].get("text", "the page could not be read"))
        return answer["result"].get("value")

    def key(self, name: str) -> None:
        shift = 8 if name == "Shift+Tab" else 0
        key, code, number, typed = KEYS["Tab" if shift else name]
        common = {"key": key, "code": code, "windowsVirtualKeyCode": number, "modifiers": shift}
        self.call("Input.dispatchKeyEvent", common | ({"type": "keyDown", "text": typed} if typed
                                                       else {"type": "rawKeyDown"}))
        self.call("Input.dispatchKeyEvent", common | {"type": "keyUp"})

    def click(self, x: float, y: float) -> None:
        self.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
        for kind in ("mousePressed", "mouseReleased"):
            self.call("Input.dispatchMouseEvent", {"type": kind, "x": x, "y": y, "button": "left", "clickCount": 1})

    def errors(self) -> list[str]:
        found = []
        for event in self.events:
            params = event.get("params", {})
            if event["method"] == "Runtime.exceptionThrown":
                detail = params.get("exceptionDetails", {})
                found.append(detail.get("exception", {}).get("description") or detail.get("text", "script error"))
            elif event["method"] == "Runtime.consoleAPICalled" and params.get("type") == "error":
                found.append(" ".join(str(arg.get("value", arg.get("description", ""))) for arg in params.get("args", [])))
            elif event["method"] == "Log.entryAdded" and params.get("entry", {}).get("level") == "error":
                entry = params["entry"]
                found.append(entry.get("text", "") + (f" ({entry['url']})" if entry.get("url") else ""))
        return [" ".join(line.split())[:300] for line in found if "/favicon.ico)" not in line][:30]


def play(chrome: Chrome, steps: list[dict]) -> list[str]:
    """Play the steps with the browser's own mouse and keyboard; one plain line per step."""
    log = []
    for number, step in enumerate(steps, 1):
        try:
            if "click" in step:
                at = chrome.ask(LOCATE % json.dumps(step["click"]))
                if at.get("missing"):
                    line = f"click: nothing matches {step['click']}"
                elif not at["shown"]:
                    line = f"click: {step['click']} is not shown on the page, so nobody could click it"
                else:
                    chrome.click(at["x"], at["y"])
                    line = f"clicked {at['name']}"
            elif "fill" in step:
                selector, value = step["fill"]
                done = chrome.ask(FILL % (json.dumps(selector), json.dumps(value)))
                if done.get("missing"):
                    line = f"fill: nothing matches {selector}"
                else:
                    if done.get("typed"):
                        if value:
                            chrome.call("Input.insertText", {"text": value})
                        else:
                            chrome.key("Backspace")
                    line = f"filled {done['name'] or selector}"
            elif "focus" in step:
                done = chrome.ask(FOCUS % json.dumps(step["focus"]))
                line = (f"focus: nothing matches {step['focus']}" if done.get("missing")
                        else f"focus is on {done['name'] or 'nothing'}")
            elif "press" in step:
                chrome.key(step["press"])
                chrome.pause(60)
                line = f"pressed {step['press']}; focus is on {chrome.ask(ACTIVE) or 'nothing (the page body)'}"
            else:
                line = "waited"
        except LookupError as error:
            line = f"failed: {str(error)[:200]}"
        log.append(f"{number}. {line}")
        chrome.pause(step.get("wait", 150))
    return log


def look(executable: str, port: int, profile: Path, label: str, url: str, steps: list[dict], shots: Path,
         stem: str) -> dict:
    """Open the page on one device, play the steps, photograph it and read it."""
    width, height, density, mobile = DEVICES[label]
    chrome = Chrome(executable, port, profile)
    try:
        target = chrome.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        chrome.session = chrome.call("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
        for domain in ("Page", "Runtime", "Log"):
            chrome.call(domain + ".enable")
        chrome.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": height,
                                                           "deviceScaleFactor": density, "mobile": mobile})
        chrome.events.clear()
        frame = chrome.call("Page.navigate", {"url": url})["frameId"]
        loaded = chrome.wait("Page.loadEventFired", 12)
        chrome.pause(400)
        chrome.world(frame)
        log = play(chrome, steps)
        chrome.pause(250)
        facts = chrome.ask(FACTS % width)
        dom = chrome.ask("document.documentElement.outerHTML")
        files, covered = [], 0
        # Clip is in page pixels. A phone page with no viewport line is laid out wide and shown small.
        wide = facts["fit_width"]
        screenful = height * wide / width
        for screen in range(SCREENS):
            tall = min(screenful, facts["page_height"] - covered) if screen else screenful
            if tall < 1:
                break
            data = chrome.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True, "clip": {
                "x": 0, "y": covered, "width": wide, "height": tall, "scale": width / wide}})["data"]
            shot = shots / (f"{stem}-{label}.png" if not screen else f"{stem}-{label}-{screen + 1}.png")
            shot.write_bytes(base64.b64decode(data))
            shot.chmod(0o600)
            files.append(shot)
            covered += tall
        errors, walk = chrome.errors(), None
        if not mobile:
            # Last, on a fresh load of the page without the steps: where real Tab presses go from the top.
            chrome.events.clear()
            chrome.call("Page.reload")
            chrome.wait("Page.loadEventFired", 8)
            chrome.pause(300)
            chrome.world(frame)
            walk = []
            for _ in range(WALK):
                chrome.key("Tab")
                chrome.pause(15)
                here = chrome.ask(ACTIVE)
                if here is None:
                    break
                walk.append(here)
        return {"loaded": loaded, "log": log, "facts": facts, "dom": dom, "files": files, "errors": errors,
                "covered": round(covered), "walk": walk}
    except TimeoutError:
        raise ValueError(f"the page did not settle within {SECONDS} seconds on the {label}") from None
    except LookupError as error:
        raise ValueError(f"the browser could not show the page: {str(error)[:200]}") from None
    finally:
        chrome.close()


class Reader(HTMLParser):
    """Text, headings, tab order and a few accessibility facts from the rendered DOM."""
    FOCUS = {"a", "button", "input", "select", "textarea", "summary"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.headings, self.stops, self.facts = [], [], [], {"images_without_alt": 0, "unlabelled_controls": 0}
        self.skip, self.heading, self.stop, self.labels, self.lang, self.title, self.in_title = 0, None, None, set(), None, "", False
        self.controls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
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
    return {"title": " ".join(reader.title.split())[:200], "language": reader.lang,
            "text": text[:TEXT_LIMIT], "text_truncated": len(text) > TEXT_LIMIT, "headings": reader.headings[:80],
            "tab_order": [f"{n}. {stop['tag']}{'#' + stop['id'] if stop['id'] else ''}: {stop['name'] or '(no name)'}"
                          for n, stop in enumerate(ordered[:80], 1)],
            "tab_stops": len(ordered), **reader.facts}


def tidy(text: str) -> str:
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def render(workspace: Path, name: str, steps_name: str | None = None) -> dict:
    page = page_path(workspace, name)
    steps = steps_from(workspace, steps_name)
    executable = browser()
    out = workspace / ".house-mailbox" / "views"
    out.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", name[:-len(Path(name).suffix)]).strip("-")[-60:] or "page"
    for old in out.glob(f"{stem}-*.png"):
        if re.fullmatch(re.escape(stem) + r"-(phone|desktop)(-\d)?\.png", old.name):
            old.unlink()
    httpd = server(workspace)
    port = httpd.server_address[1]
    url = f"http://127.0.0.1:{port}/" + "/".join(page.relative_to(workspace).parts)
    seen = {}
    try:
        with tempfile.TemporaryDirectory(prefix="house-view-") as scratch:
            for label in DEVICES:
                seen[label] = look(executable, port, Path(scratch) / label, label, url, steps, out, stem)
    finally:
        httpd.shutdown(); httpd.server_close()
    result = {"page": name, "steps_played": len(steps), "screenshots": {}, "step_log": {}, "script_errors": {},
              "layout": {}, "wider_than_screen": {}, "too_wide": {}, "focused_after_steps": {}}
    for label, view in seen.items():
        facts = view["facts"]
        width, height, density, _ = DEVICES[label]
        files = [str(file.relative_to(workspace)) for file in view["files"]]
        result["screenshots"][label] = {"file": files[0], "files": files, "width": width,
                                        "image_width": width * density, "page_height": facts["page_height"],
                                        "pictured_to": min(view["covered"], facts["page_height"])}
        result["step_log"][label] = view["log"]
        result["script_errors"][label] = view["errors"] + ([] if view["loaded"] else [
            "the page had not finished loading when it was read"])
        result["layout"][label] = {"screen_width": width, "layout_width": facts["layout_width"],
                                   "page_width": facts["page_width"], "zoom": facts["zoom"],
                                   "declares_viewport": facts["declares_viewport"]}
        result["wider_than_screen"][label] = facts["over"]
        result["too_wide"][label] = facts["wide"]
        result["focused_after_steps"][label] = facts["focused"]
    desktop, phone = read(seen["desktop"]["dom"]), read(seen["phone"]["dom"])
    text, small = tidy(seen["desktop"]["facts"]["text"]), tidy(seen["phone"]["facts"]["text"])
    result.update(desktop)
    result.update(title=" ".join(seen["desktop"]["facts"]["title"].split())[:200] or desktop["title"],
                  text=text[:TEXT_LIMIT], text_truncated=len(text) > TEXT_LIMIT,
                  fields=seen["desktop"]["facts"]["fields"], keyboard_walk=seen["desktop"]["walk"],
                  phone_text_differs=small != text)
    if small != text:
        result["phone_text"] = small[:TEXT_LIMIT]
    if phone.get("own_policy"):
        result["own_policy"] = phone["own_policy"]
    result["note"] = (
        "Open the screenshot files to look at the page. text is what a visitor sees after your steps; fields is "
        "what each form field holds; keyboard_walk is where real Tab presses go on a fresh load of the page, without "
        "your steps (use press steps to walk a later state). The phone is a 390 pixel wide screen: if layout_width is larger and zoom is below "
        "1, the page has no viewport line and a real phone shows it shrunk like this. This is the house's own "
        "Chrome with the network refused. It speaks nothing, so make no screen-reader claim from it.")
    return result
