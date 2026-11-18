"""Reading the house's own public site: one GET, one fixed origin, data back, and no real network in these tests."""
import hashlib
import http.client
import os
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from house import mailbox, mailbox_jobs, renovation, resident_actions, site_read
from tests.test_mailbox import MailboxCase

SOCKETS = unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                          "host-only: the candidate sandbox allows no sockets")


def no_network(timeout):
    raise AssertionError("the network was used")


class ConstantTests(unittest.TestCase):
    def test_the_production_prefix_is_exactly_the_houses_public_site(self):
        self.assertEqual("https://someblueman.github.io/emberhall/", site_read.PREFIX)
        self.assertEqual("someblueman.github.io", site_read.HOST)
        self.assertEqual("https://someblueman.github.io/emberhall/", site_read.build_url(""))
        self.assertEqual("https://someblueman.github.io/emberhall/head.json", site_read.build_url("head.json"))
        self.assertEqual("https://someblueman.github.io/emberhall/history/part-1.json",
                         site_read.build_url("history/part-1.json"))

    def test_only_the_steward_can_change_it(self):
        self.assertIn("house/site_read.py", renovation.STEWARD_ONLY)
        self.assertIn("read-site", resident_actions.ACTIONS)
        self.assertIn("read-site", mailbox.ALLOWED)

    def test_the_command_takes_a_path_or_nothing(self):
        args = resident_actions.parse(["read-site", "head.json", "--as", "me", "--request", "r"], "me")
        self.assertEqual("head.json", args.path)
        self.assertEqual("", resident_actions.parse(["read-site", "--as", "me", "--request", "r"], "me").path)
        with self.assertRaises(ValueError):
            resident_actions.parse(["read-site", "--as", "someone-else", "--request", "r"], "me")


class PathTests(unittest.TestCase):
    def test_plain_paths_are_accepted(self):
        for path in ("", "head.json", "a/b/c.html", "history/part-001.json", "a_b~c-d.css", "dir/", "caf%C3%A9.html",
                     "x%2Dy.html", "..hidden", "a..b", ".well-known/x"):
            self.assertEqual(path, site_read.check_path(path), path)

    def test_every_forbidden_form_is_refused_before_any_network_call(self):
        bad = ["https://example.org/", "http://someblueman.github.io/emberhall/", "//example.org/x", "/x", "a//b",
               "..", "../x", "a/../b", "a/..", ".", "a/./b", "a\\b", "..\\x", "user@host", "a@b", "x?y=1", "x#frag",
               "x y", "x\ty", "x\nfoo", "x\r\n", "x\x00", "x\x7f", " ", "head.json ", "a:b", "javascript:alert(1)",
               "%2e%2e/x", "a/%2e%2e/b", "%2E%2E", "%2e", "a/%2e/b", "a%2fb", "%2f", "%2F%2e%2e", "a%5Cb", "%5c",
               "a%40b", "a%3Fb", "a%23b", "a%20b", "a%09b", "a%0ab", "a%00b", "a%7Fb", "a%25b", "%25", "%", "%4",
               "%zz", "a%2", "%ff", "%c3", "a%3Ab", "café.html", "x" * (site_read.MAX_PATH + 1), "a;b", "a=b",
               "a&b", "a+b", "a,b", "a*b", "a'b", "a\"b", "a<b", "a|b", "a{b}", "a[b]"]
        for path in bad:
            with self.assertRaises(ValueError, msg=repr(path)):
                site_read.check_path(path)
            with self.assertRaises(ValueError, msg=repr(path)):
                site_read.fetch(path, connection=no_network)
        for path in (None, 5, b"x", ["a"]):
            with self.assertRaises(ValueError):
                site_read.fetch(path, connection=no_network)

    def test_a_refused_path_is_not_counted_against_the_run(self):
        with tempfile.TemporaryDirectory() as state:
            with self.assertRaises(ValueError):
                site_read.read_site(Path(state), "run-1", "../x", connection=no_network)
            self.assertEqual([], list(Path(state).iterdir()))

    def test_the_final_url_is_checked_against_the_fixed_prefix(self):
        with patch.object(site_read, "PREFIX", "https://someblueman.github.io.evil.example/emberhall/"):
            with self.assertRaises(ValueError):
                site_read.build_url("x")
        with patch.object(site_read, "PREFIX", "http://someblueman.github.io/emberhall/"):
            with self.assertRaises(ValueError):
                site_read.build_url("x")


class Site:
    """A local stand-in for the house's site. It answers on loopback; the code under test still believes the URL."""

    def __init__(self, test):
        self.seen = []
        outer = self
        self.routes = {}
        self.delay = 0

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def do_GET(self):
                outer.seen.append((self.path, dict(self.headers)))
                if outer.delay:
                    time.sleep(outer.delay)
                status, headers, body = outer.routes.get(self.path, (404, {}, b"missing"))
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                if "Content-Length" not in headers:
                    self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except OSError:
                    pass

        class Quiet(ThreadingHTTPServer):
            def handle_error(self, request, client_address):
                pass  # a reader that stops early at the cap resets the connection; that is expected

        self.httpd = Quiet(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        test.addCleanup(self.httpd.server_close)
        test.addCleanup(self.httpd.shutdown)

    def connection(self, timeout):
        return http.client.HTTPConnection("127.0.0.1", self.httpd.server_address[1], timeout=timeout)


@SOCKETS
class FetchTests(unittest.TestCase):
    def setUp(self):
        self.site = Site(self)

    def get(self, path):
        return site_read.fetch(path, connection=self.site.connection)

    def test_a_text_page_comes_back_as_facts_and_text(self):
        body = "<!doctype html><title>Emberhall</title><p>café</p>".encode()
        self.site.routes["/emberhall/"] = (200, {"Content-Type": "text/html; charset=utf-8"}, body)
        result = self.get("")
        self.assertEqual("https://someblueman.github.io/emberhall/", result["url"])
        self.assertEqual(200, result["status"])
        self.assertEqual("text/html; charset=utf-8", result["content_type"])
        self.assertEqual(str(len(body)), result["content_length_header"])
        self.assertEqual(len(body), result["bytes_read"])
        self.assertEqual(hashlib.sha256(body).hexdigest(), result["sha256"])
        self.assertIs(False, result["truncated"])
        self.assertEqual(body.decode(), result["text"])
        self.assertIs(False, result["text_truncated"])

    def test_json_css_js_svg_xml_and_plain_are_text_and_other_types_are_not(self):
        for kind in ("application/json", "text/css", "text/javascript", "application/javascript", "image/svg+xml",
                     "application/xml", "text/plain; charset=utf-8", "application/ld+json"):
            self.site.routes["/emberhall/x"] = (200, {"Content-Type": kind}, b"hello")
            self.assertEqual("hello", self.get("x")["text"], kind)
        for kind in ("image/png", "application/octet-stream", "application/pdf", "font/woff2"):
            body = b"\x89PNG\r\n\x1a\n\x00\xff"
            self.site.routes["/emberhall/x"] = (200, {"Content-Type": kind}, body)
            result = self.get("x")
            self.assertIsNone(result["text"], kind)
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (result["bytes_read"], result["sha256"]))
            self.assertIn("note", result)

    def test_a_compressed_answer_is_not_decoded_as_text(self):
        self.site.routes["/emberhall/x"] = (200, {"Content-Type": "text/html", "Content-Encoding": "gzip"}, b"\x1f\x8b")
        self.assertIsNone(self.get("x")["text"])

    def test_a_missing_page_is_just_a_status(self):
        result = self.get("nope.html")
        self.assertEqual((404, b"missing".__len__()), (result["status"], result["bytes_read"]))

    def test_a_redirect_is_returned_as_data_and_never_followed(self):
        self.site.routes["/emberhall/old"] = (301, {"Location": "https://example.org/elsewhere"}, b"moved")
        self.site.routes["/elsewhere"] = (200, {}, b"must not be asked for")
        result = self.get("old")
        self.assertEqual(301, result["status"])
        self.assertEqual("https://example.org/elsewhere", result["location"])
        self.assertIs(False, result["redirect_followed"])
        self.assertNotIn("sha256", result)
        self.assertNotIn("text", result)
        self.site.routes["/emberhall/rel"] = (302, {"Location": "/emberhall/head.json"}, b"")
        self.assertEqual("/emberhall/head.json", self.get("rel")["location"])
        self.assertEqual(["/emberhall/old", "/emberhall/rel"], [path for path, _ in self.site.seen],
                         "no second request was made")

    def test_the_request_is_one_plain_get_with_only_a_generic_user_agent(self):
        self.get("head.json")
        (path, headers), = self.site.seen
        self.assertEqual("/emberhall/head.json", path)
        self.assertEqual({"user-agent", "host", "accept-encoding"}, {key.lower() for key in headers})
        self.assertEqual("emberhall-site-read", headers["User-Agent"])
        self.assertEqual("identity", headers["Accept-Encoding"])

    def test_a_big_body_stops_at_the_cap_and_says_so(self):
        body = bytes(range(256)) * 20
        self.site.routes["/emberhall/big.bin"] = (200, {"Content-Type": "application/octet-stream"}, body)
        with patch.object(site_read, "MAX_BODY", 1000):
            result = self.get("big.bin")
        self.assertIs(True, result["truncated"])
        self.assertEqual(1000, result["bytes_read"])
        self.assertEqual(hashlib.sha256(body[:1000]).hexdigest(), result["sha256"])
        self.assertEqual(str(len(body)), result["content_length_header"])
        exact = bytes(1000)
        self.site.routes["/emberhall/exact"] = (200, {"Content-Type": "application/octet-stream"}, exact)
        with patch.object(site_read, "MAX_BODY", 1000):
            self.assertIs(False, self.get("exact")["truncated"], "a body exactly at the cap is whole")

    def test_the_production_limits_are_the_ones_asked_for(self):
        self.assertEqual(5 * 1024 * 1024, site_read.MAX_BODY)
        self.assertEqual(15, site_read.TIMEOUT)
        self.assertEqual(200_000, site_read.TEXT_LIMIT)
        self.assertEqual(60, site_read.RUN_LIMIT)

    def test_long_text_is_cut_and_flagged(self):
        self.site.routes["/emberhall/long.txt"] = (200, {"Content-Type": "text/plain"}, b"abcdefghij" * 5)
        with patch.object(site_read, "TEXT_LIMIT", 12):
            result = self.get("long.txt")
        self.assertEqual(("abcdefghijab", True, 50), (result["text"], result["text_truncated"], result["bytes_read"]))

    def test_a_slow_answer_ends_in_a_plain_error(self):
        self.site.routes["/emberhall/slow"] = (200, {"Content-Type": "text/plain"}, b"late")
        self.site.delay = 1.5
        started = time.monotonic()
        with patch.object(site_read, "TIMEOUT", 0.5):
            result = self.get("slow")
        self.assertLess(time.monotonic() - started, 1.2)
        self.assertEqual({"url", "status", "error"}, set(result))
        self.assertIsNone(result["status"])
        self.assertIn("longer than", result["error"])

    def test_a_refused_connection_is_a_plain_error_without_host_details(self):
        probe = Site(self)
        port = probe.httpd.server_address[1]
        probe.httpd.shutdown()
        probe.httpd.server_close()
        result = site_read.fetch("head.json", connection=lambda timeout: http.client.HTTPConnection(
            "127.0.0.1", port, timeout=timeout))
        self.assertEqual({"url": "https://someblueman.github.io/emberhall/head.json", "status": None,
                          "error": "the connection was refused"}, result)
        self.assertNotIn("127.0.0.1", repr(result))

    def test_other_failures_are_plain_too(self):
        import socket
        import ssl
        for error, words in ((socket.gaierror(8, "nodename nor servname provided"), "looked up"),
                             (ssl.SSLError(1, "CERTIFICATE_VERIFY_FAILED"), "secure connection"),
                             (http.client.RemoteDisconnected("gone"), "could not be read")):
            def broken(timeout, error=error):
                raise error
            result = site_read.fetch("", connection=broken)
            self.assertIn(words, result["error"])
            self.assertEqual({"url", "status", "error"}, set(result))


class RateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.state = Path(tmp.name) / "site-read"
        self.calls = []
        sleep = patch("house.site_read.time.sleep", side_effect=self.calls.append)
        sleep.start()
        self.addCleanup(sleep.stop)
        fetch = patch.object(site_read, "fetch", side_effect=lambda path, connection=None: {"path": path})
        fetch.start()
        self.addCleanup(fetch.stop)

    def test_a_run_may_read_the_limit_and_is_then_refused_clearly(self):
        with patch.object(site_read, "RUN_LIMIT", 3), patch.object(site_read, "MIN_GAP", 0):
            for number in range(3):
                self.assertEqual({"path": "p"}, site_read.read_site(self.state, "run-a", "p"))
            with self.assertRaises(ValueError) as refused:
                site_read.read_site(self.state, "run-a", "p")
            self.assertIn("limited to 3 reads", str(refused.exception))
            self.assertEqual({"path": "p"}, site_read.read_site(self.state, "run-b", "p"), "the limit is per run")
            with self.assertRaises(ValueError):
                site_read.read_site(self.state, "run-a", "p")

    def test_reads_are_spaced_by_the_gap(self):
        site_read.read_site(self.state, "run-a", "p")
        self.assertEqual([], self.calls)
        site_read.read_site(self.state, "run-a", "p")
        self.assertEqual(1, len(self.calls))
        self.assertTrue(0 < self.calls[0] <= site_read.MIN_GAP)

    def test_the_counter_survives_a_new_process(self):
        with patch.object(site_read, "RUN_LIMIT", 1), patch.object(site_read, "MIN_GAP", 0):
            site_read.read_site(self.state, "run-a", "p")
            # The worker is a fresh process per request, so the count lives on disk, not in memory.
            with self.assertRaises(ValueError):
                site_read.read_site(Path(str(self.state)), "run-a", "q")

    def test_a_damaged_counter_starts_again_rather_than_failing(self):
        site_read.read_site(self.state, "run-a", "p")
        for file in self.state.glob("*.json"):
            file.write_text("not json")
        self.assertEqual({"path": "p"}, site_read.read_site(self.state, "run-a", "p"))


class ChannelTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.arrive()

    def test_it_is_a_read_only_action_in_the_inspection_lane_with_no_journal_event(self):
        argv = ["read-site", "head.json", "--as", self.resident, "--request", "read-1"]
        self.assertEqual("inspection", mailbox_jobs.lane(self.record, {
            "argv": argv, "run": self.run, "resident": self.resident}))
        mailbox.parse(argv, self.record.root, self.workspace, self.resident)
        before = self.record.read()[0]["sequence"]
        with patch("house.site_read.fetch", return_value={"status": 200}) as fetched:
            result = resident_actions.execute(self.record, self.workspace, self.resident, self.run, argv, "read-1")
        self.assertEqual({"status": 200}, result)
        self.assertEqual("head.json", fetched.call_args.args[0])
        self.assertEqual(before, self.record.read()[0]["sequence"], "reading the site records nothing")
        self.assertIsNone(resident_actions.known_result(self.record, self.resident, self.run, argv, "read-1"))
        state = self.record.common / "house-home" / "site-read"
        self.assertEqual(1, len(list(state.glob("*.json"))), "one read was counted against the run")

    def test_a_bad_path_is_refused_through_the_channel_before_any_fetch(self):
        argv = ["read-site", "../x", "--as", self.resident, "--request", "read-2"]
        with patch("house.site_read.fetch") as fetched:
            with self.assertRaises(ValueError):
                resident_actions.execute(self.record, self.workspace, self.resident, self.run, argv, "read-2")
        fetched.assert_not_called()


if __name__ == "__main__":
    unittest.main()
