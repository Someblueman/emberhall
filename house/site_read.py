"""Let a resident read the house's own published site, and nothing else on the internet.

Residents have no network of their own. They asked to check that visitors receive
the version the house tested. The Steward agreed, limited to the house's own
public site: one plain HTTP GET of one page or asset under PREFIX, returning facts
about what was served (status, size, SHA-256, and the text of text files). This is
not general web access, and this module is Steward-only so that residents cannot
widen it.

Bounds. The resident gives a path relative to PREFIX, never a URL. The path is
checked strictly before any network use, and the final URL is built here and
checked again. Redirects are not followed: a 3xx comes back as its status and
Location, as data. No cookies, no credentials, no proxy from the environment, and
no header but a generic User-Agent (and the Host and identity Accept-Encoding that
http.client adds itself). The read lasts at most TIMEOUT seconds and stops at
MAX_BODY bytes. A run may read the site RUN_LIMIT times, one at a time. What comes
back is data only: nothing fetched is written to the room, run or rendered.
"""
import codecs
import fcntl
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import time
from pathlib import Path
from urllib.parse import unquote_to_bytes, urlsplit

PREFIX = "https://someblueman.github.io/emberhall/"
HOST = "someblueman.github.io"
USER_AGENT = "emberhall-site-read"
TIMEOUT = 15            # seconds, connection to last byte
MAX_BODY = 5 * 1024 * 1024
TEXT_LIMIT = 200_000    # characters of decoded text returned
MAX_PATH = 200
RUN_LIMIT = 60          # reads of the site per resident run
MIN_GAP = 1.0           # seconds between two reads by one run
HEADER_LIMIT = 500

SAFE = re.compile(r"[A-Za-z0-9/._~%-]*")
ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")
TEXT_TYPES = frozenset({"text/html", "text/css", "text/plain", "text/javascript", "text/xml",
                        "application/javascript", "application/x-javascript", "application/json",
                        "application/xml", "image/svg+xml"})


def check_path(path) -> str:
    """Return the path if it can only name a published file under PREFIX; otherwise refuse before any network use."""
    if not isinstance(path, str):
        raise ValueError("read-site takes a path inside the house's public site")
    if len(path) > MAX_PATH:
        raise ValueError(f"that path is longer than {MAX_PATH} characters")
    if not SAFE.fullmatch(path):
        raise ValueError("read-site takes only letters, digits and / . _ - ~ % in a path: no scheme, query, "
                         "fragment, space, backslash or @")
    if ESCAPE.search(path):
        raise ValueError("a % in the path must be followed by two hex digits")
    if path.startswith("/") or "//" in path:
        raise ValueError("give the path relative to the site front page, with no leading / and no //")
    # What a server would see after decoding each segment must still be a plain file name.
    for part in path.split("/"):
        try:
            name = unquote_to_bytes(part).decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("a percent escape in the path is not valid UTF-8") from None
        if name in {".", ".."} or part in {".", ".."}:
            raise ValueError("a path may not contain a . or .. segment")
        if any(not (char.isalnum() or char in "._~-") for char in name):
            raise ValueError("a percent escape in the path decodes to something a file name cannot hold")
    return path


def build_url(path) -> str:
    """The one URL to ask for, checked against the fixed prefix, host and scheme."""
    url = PREFIX + check_path(path)
    parts = urlsplit(url)
    if (not url.startswith(PREFIX) or parts.scheme != "https" or parts.hostname != HOST or parts.port is not None
            or parts.username is not None or parts.password is not None or parts.query or parts.fragment
            or not parts.path.startswith("/emberhall/")):
        raise ValueError("that is not a page of the house's public site")
    return url


def claim(state: Path, run: str) -> None:
    """Count one read for this run, or refuse. Waits out the short gap between reads rather than refusing it."""
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    name = hashlib.sha256(run.encode()).hexdigest()
    with (state / (name + ".lock")).open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        file = state / (name + ".json")
        try:
            seen = json.loads(file.read_text())
            count, last = int(seen["count"]), float(seen["last"])
        except (OSError, ValueError, KeyError, TypeError):
            count, last = 0, 0.0
        if count >= RUN_LIMIT:
            raise ValueError(f"read-site is limited to {RUN_LIMIT} reads of the public site per run and this run has "
                             "used them; keep what you learned in your notes and read again in a later run")
        wait = last + MIN_GAP - time.time()
        if 0 < wait <= MIN_GAP:
            time.sleep(wait)
        temporary = file.with_suffix(".tmp")
        temporary.write_text(json.dumps({"count": count + 1, "last": time.time()}))
        os.replace(temporary, file)


def https_connection(timeout: float):
    return http.client.HTTPSConnection(HOST, timeout=timeout)


def clean(value, limit=HEADER_LIMIT):
    return None if value is None else "".join(ch for ch in value if ch.isprintable())[:limit]


def is_text(content_type: str | None) -> bool:
    kind = (content_type or "").split(";")[0].strip().lower()
    return kind in TEXT_TYPES or kind.endswith(("+json", "+xml"))


def charset(content_type: str | None) -> str:
    found = re.search(r"charset=([A-Za-z0-9_.:-]+)", content_type or "", re.IGNORECASE)
    try:
        return codecs.lookup(found.group(1)).name if found else "utf-8"
    except LookupError:
        return "utf-8"


def fetch(path, connection=https_connection) -> dict:
    """One GET of one file under PREFIX. `connection` only chooses where the bytes travel, so tests can use a
    local server; the URL, path and checks are always the production ones and residents cannot pass it."""
    url = build_url(path)
    target = "/" + url.split("/", 3)[3]
    deadline = time.monotonic() + TIMEOUT
    conn = None
    try:
        conn = connection(TIMEOUT)
        conn.request("GET", target, headers={"User-Agent": USER_AGENT})
        response = conn.getresponse()
        status = response.status
        content_type = clean(response.getheader("Content-Type"))
        if 300 <= status < 400:
            return {"url": url, "status": status, "location": clean(response.getheader("Location"), 2000),
                    "redirect_followed": False,
                    "note": "The house site answered with a redirect. It was not followed. Ask for the "
                            "Location path yourself if you want it."}
        body, truncated = bytearray(), False
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            if conn.sock is not None:
                conn.sock.settimeout(remaining)
            chunk = response.read(min(65536, MAX_BODY + 1 - len(body)))
            if not chunk:
                break
            body += chunk
            if len(body) > MAX_BODY:
                del body[MAX_BODY:]
                truncated = True
                break
        encoding = (response.getheader("Content-Encoding") or "identity").strip().lower()
        result = {"url": url, "status": status, "content_type": content_type,
                  "content_length_header": clean(response.getheader("Content-Length")),
                  "bytes_read": len(body), "sha256": hashlib.sha256(body).hexdigest(), "truncated": truncated}
        if is_text(content_type) and encoding == "identity":
            text = bytes(body).decode(charset(content_type), errors="replace")
            result.update(text=text[:TEXT_LIMIT], text_truncated=len(text) > TEXT_LIMIT)
        else:
            result["text"] = None
            result["note"] = ("Not shown as text: " + ("the server sent it compressed." if encoding != "identity"
                              else "it is not a text type. Its size and sha256 are above."))
        if truncated:
            result["note"] = (result.get("note", "") + f" Reading stopped at {MAX_BODY} bytes, so bytes_read and "
                              "sha256 cover only that much.").strip()
        return result
    except (TimeoutError, OSError, http.client.HTTPException) as error:
        # Say what kind of failure it was. Never a stack trace or anything about this machine.
        if isinstance(error, TimeoutError):
            why = f"the read took longer than {TIMEOUT} seconds and was stopped"
        elif isinstance(error, ConnectionRefusedError):
            why = "the connection was refused"
        elif isinstance(error, socket.gaierror):
            why = "the site's name could not be looked up"
        elif isinstance(error, ssl.SSLError):
            why = "the secure connection could not be made"
        else:
            why = "the site could not be read"
        return {"url": url, "status": None, "error": why}
    finally:
        if conn is not None:
            conn.close()


def read_site(state: Path, run: str, path, connection=https_connection) -> dict:
    """The resident action: check the path, count the read against the run, then fetch."""
    build_url(path)
    claim(state, run)
    return fetch(path, connection)
