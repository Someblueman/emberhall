"""The page viewer: a resident sees one page of their own room, and nothing leaves the Mac."""
import json
import os
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import ProxyHandler, build_opener
from urllib.error import HTTPError

from house import mailbox, mailbox_jobs, resident_actions, view
from tests.test_mailbox import MailboxCase

PAGE = """<!doctype html><html lang="en"><head><title>Try me</title>
<style>.wide{width:900px}</style></head><body>
<h1>A small page</h1><p id="out">before</p>
<label for="name">Name</label><input id="name"><input id="bare">
<button id="go" onclick="document.getElementById('out').textContent='pressed ' + document.getElementById('name').value">Go</button>
<img src="missing.png"><div class="wide">wide</div>
<script>
fetch('OUTSIDE').then(r => r.text()).then(t => document.body.dataset.outside = 'reached', () => document.body.dataset.outside = 'refused');
</script></body></html>"""


# The installer runs candidate tests where no socket may be opened; these run on the host (house.testrun).
SOCKETS = unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                          "host-only: the candidate sandbox allows no sockets")


def chrome_installed():
    try:
        return bool(view.browser())
    except ValueError:
        return False


class PathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.room = Path(self.tmp.name) / "room"
        (self.room / "pages" / ".hidden").mkdir(parents=True)
        (self.room / "pages/ok.html").write_text(PAGE)
        (self.room / "pages/.hidden/x.html").write_text(PAGE)
        (self.room / "notes.md").write_text("no")
        outside = Path(self.tmp.name) / "outside.html"
        outside.write_text(PAGE)
        os.symlink(outside, self.room / "link.html")

    def test_only_a_plain_html_file_inside_the_room_is_viewed(self):
        self.assertEqual(self.room / "pages/ok.html", view.page_path(self.room, "pages/ok.html"))
        for name in ("", "/etc/hosts.html", "../outside.html", "pages/../../outside.html", "pages/.hidden/x.html",
                     ".house-mailbox/x.html", "notes.md", "link.html", "pages/none.html"):
            with self.assertRaises(ValueError, msg=name):
                view.page_path(self.room, name)

    def test_steps_are_a_short_list_of_known_verbs(self):
        def steps(value):
            (self.room / "steps.json").write_text(json.dumps(value))
            return view.steps_from(self.room, "steps.json")
        self.assertEqual([], view.steps_from(self.room, None))
        good = [{"fill": ["#name", "Ada"]}, {"click": "#go", "wait": 50}, {"focus": "#go"}, {"wait": 10}]
        self.assertEqual(good, steps(good))
        for bad in ({"click": "#go"}, [{"click": "#a"}] * 31, [{"eval": "alert(1)"}], [{"click": 5}],
                    [{"click": "#a", "focus": "#b"}], [{"fill": "#name"}], [{"wait": 60000}]):
            with self.assertRaises(ValueError, msg=bad):
                steps(bad)
        for name in ("../steps.json", "/tmp/steps.json", ".secret.json", "missing.json"):
            with self.assertRaises(ValueError, msg=name):
                view.steps_from(self.room, name)

    def test_the_viewer_is_a_read_only_resident_action(self):
        self.assertIn("view", resident_actions.ACTIONS)
        from house import renovation
        self.assertIn("house/view.py", renovation.STEWARD_ONLY, "residents cannot widen the viewer by renovation")
        args = resident_actions.parse(["view", "pages/ok.html", "--as", "me", "--request", "look-1",
                                       "--steps", "steps.json"], "me")
        self.assertEqual(("pages/ok.html", "steps.json"), (args.path, args.steps))
        with self.assertRaises(ValueError):
            resident_actions.parse(["view", "pages/ok.html", "--as", "someone-else", "--request", "r"], "me")

    @SOCKETS
    def test_the_proxy_serves_the_room_and_refuses_every_other_address(self):
        httpd = view.server(self.room, self.room / "pages/ok.html", [])
        self.addCleanup(httpd.server_close)
        self.addCleanup(httpd.shutdown)
        port = httpd.server_address[1]
        through = build_opener(ProxyHandler({"http": f"http://127.0.0.1:{port}"}))

        def status(url):
            try:
                return through.open(url, timeout=5).status
            except HTTPError as error:
                return error.code
        self.assertEqual(200, status(f"http://127.0.0.1:{port}/pages/ok.html"))
        body = through.open(f"http://127.0.0.1:{port}/pages/ok.html", timeout=5).read().decode()
        self.assertIn(view.REPORT, body, "the looked-at page carries the viewer's own report script")
        # Asked the way a browser asks its proxy. (urllib would skip the proxy for some hosts by itself.)
        import http.client
        for url in ("http://example.org/", f"http://127.0.0.1:{port + 1}/", f"http://localhost:{port}/pages/ok.html",
                    "http://169.254.169.254/latest/meta-data", "https://example.org/"):
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("GET", url)
            self.assertEqual(403, connection.getresponse().status, url)
            connection.close()
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request("CONNECT", "example.org:443")
        self.assertEqual(403, connection.getresponse().status)
        connection.close()
        for url in (f"http://127.0.0.1:{port}/link.html", f"http://127.0.0.1:{port}/pages/.hidden/x.html",
                    f"http://127.0.0.1:{port}/pages/%2e%2e/%2e%2e/outside.html"):
            self.assertIn(status(url), {403, 404}, url)


@SOCKETS
@unittest.skipUnless(chrome_installed(), "needs Chrome or Chromium on the host")
class RenderTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.arrive()
        self.hits = []
        test = self

        class Outside(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                test.hits.append(self.path)
                self.send_response(200); self.send_header("Content-Length", "2")
                self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b"ok")
        self.outside = ThreadingHTTPServer(("127.0.0.1", 0), Outside)
        threading.Thread(target=self.outside.serve_forever, daemon=True).start()
        self.addCleanup(self.outside.server_close)
        self.addCleanup(self.outside.shutdown)
        (self.workspace / "pages").mkdir()
        (self.workspace / "pages/try.html").write_text(
            PAGE.replace("OUTSIDE", f"http://127.0.0.1:{self.outside.server_address[1]}/secret"))
        (self.workspace / "steps.json").write_text(json.dumps([{"fill": ["#name", "Ada"]}, {"click": "#go"}]))

    def test_a_resident_sees_their_page_through_the_mailbox_and_nothing_leaves(self):
        argv = ["view", "pages/try.html", "--as", self.resident, "--request", "look-1", "--steps", "steps.json"]
        self.assertEqual("inspection", mailbox_jobs.lane(self.record, {
            "argv": argv, "run": self.run, "resident": self.resident}))
        self.record._mailbox_runtime = self.runtime
        self.addCleanup(lambda: mailbox_jobs.stop(self.record, self.run))
        before = self.record.read()[0]["sequence"]
        process = self.start(*argv)
        deadline = time.monotonic() + 150
        while process.poll() is None and time.monotonic() < deadline:
            mailbox.service(self.record, self.private, self.run)
            mailbox_jobs.tick(self.record)
            time.sleep(0.05)
        output, errors = process.communicate(timeout=5)
        self.assertEqual(0, process.returncode, (output, errors))
        result = json.loads(output)
        result = result.get("result", result)
        self.assertEqual(("Try me", "en", 2), (result["title"], result["language"], result["steps_played"]))
        self.assertIn("A small page", result["text"])
        self.assertIn("pressed Ada", result["text"], "the steps were played before the page was read")
        self.assertEqual(1, result["images_without_alt"])
        self.assertEqual(1, result["unlabelled_controls"])
        self.assertTrue(result["wider_than_screen"]["phone"])
        self.assertFalse(result["wider_than_screen"]["desktop"])
        for label in ("phone", "desktop"):
            shot = self.workspace / result["screenshots"][label]["file"]
            self.assertTrue(shot.is_file() and shot.read_bytes().startswith(b"\x89PNG"), label)
            self.assertIn(".house-mailbox/views/", result["screenshots"][label]["file"])
        self.assertEqual([], self.hits, "the page asked for another address on this Mac and must not reach it")
        self.assertEqual(before, self.record.read()[0]["sequence"], "looking at a page records nothing")


if __name__ == "__main__":
    unittest.main()
