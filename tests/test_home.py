"""Real inert processes exercise supervision; these are not live model wakes."""
import json
import os
import unittest
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import zipfile

from house import home
from house.home_work import git
from house.life import CONTROLLER
from tests.support import HouseCase, SOURCE


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host process-recovery fixture requires macOS setuid ps")
class HomeTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "source.txt").write_text("base\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "Initial source")
        self.record.append("arrive", CONTROLLER, {"name": "Watch keeper"})
        self.runtime = self.root / "runtime.pyz"
        with zipfile.ZipFile(self.runtime, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                archive.write(file, "house/" + file.name)
            archive.writestr("__main__.py", "import sys\nfrom house.home import main\nraise SystemExit(main(sys.argv[2:]))\n")
        self.native = self.root / "native.py"
        self.native.write_text("import json,sys,time\nfrom pathlib import Path\n"
            "Path('source.txt').write_text('resident contribution\\n')\n"
            "Path(sys.argv[1]).write_text('native launched')\n"
            "time.sleep(float(sys.argv[2]))\n"
            "print(json.dumps({'type':'turn.completed','usage':{'input_tokens':3,'output_tokens':2}}),flush=True)\n")
        self.delay = 0.1
        for target, value in (("active_policy", lambda _: {"revision": "synthetic-fixture-policy"}),
                              ("active_prompt", lambda _: "Inert test fixture; no model call."),
                              ("providers.command", self.command)):
            helper = patch("house.home." + target, value)
            helper.start(); self.addCleanup(helper.stop)
        self.coordinator = home.Coordinator(self.record, self.runtime)
        self.addCleanup(self.coordinator.close)

    def command(self, kind, model, workspace, private, client, **kwargs):
        return [sys.executable, str(self.native), str(private / "native-started"), str(self.delay)], dict(os.environ)

    def drain(self, coordinator=None):
        coordinator = coordinator or self.coordinator
        deadline = time.monotonic() + 15
        while coordinator.running and time.monotonic() < deadline:
            coordinator.tick(start=False, poll=False)
            time.sleep(0.03)
        self.assertFalse(coordinator.running, "fixture process failed to finish")

    def test_three_real_rooms_preserve_work_and_fourth_waits(self):
        self.delay = 1
        for number in range(4):
            self.record.append("life", "alice", {"kind": "help", "request": f"help-{number}",
                                                "reason": "Independent fixture work"})
        result = self.coordinator.tick(poll=False)
        self.assertEqual(len(result["started"]), 3)
        self.assertEqual(self.coordinator.tick(poll=False)["started"], [])
        state = self.record.read()[0]
        self.assertEqual({run["agent"] for run in state["life"]["runs"].values()},
                         {"codex", "opencode", "muse"})
        self.drain()
        state = self.record.read()[0]
        self.assertEqual((self.repo / "source.txt").read_text(), "base\n")
        for run in result["started"]:
            item = state["life"]["runs"][run]
            self.assertEqual(item["outcome"], "success")
            self.assertEqual(item["usage"], {"input_tokens": 3, "output_tokens": 2})
            path = self.coordinator.private / run
            candidate = json.loads((path / "contribution.json").read_text())
            self.assertEqual(candidate["paths"], ["source.txt"])
            self.assertEqual(candidate["status"], "pending-review")
            self.assertNotIn("env", json.loads((path / "launch.json").read_text()))
            self.assertTrue((path / "preservation.json").exists())
        self.assertEqual(len(home.pending_contributions(self.coordinator.private)), 3)
        self.assertEqual(state["life"]["requests"]["help-3"]["status"], "pending")
        self.assertEqual(state["life"]["requests"]["help-0"]["status"], "pending")

    def test_native_cannot_start_before_accepted_launch_receipt(self):
        original = self.coordinator.life
        def refuse(kind, run, **data):
            if kind == "run-launched":
                raise ValueError("injected launch rejection")
            return original(kind, run, **data)
        with patch.object(self.coordinator, "life", refuse):
            run = self.coordinator.start("codex")
        self.assertFalse((self.coordinator.private / run / "native-started").exists())
        state = self.record.read()[0]
        self.assertEqual(state["life"]["runs"][run]["outcome"], "failed")
        self.assertGreater(state["life"]["budgets"]["codex"]["until"], time.time())
        self.assertEqual(home.choose_provider(state, time.time()), "opencode")

    def test_observed_outcome_survives_cleanup_retry(self):
        run = self.coordinator.start("codex")
        self.coordinator.running[run].process.wait(timeout=10)
        with patch("house.home.group_stopped", return_value=False):
            with self.assertRaisesRegex(ValueError, "observed result retained"):
                self.coordinator.reap()
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["status"], "active")
        self.coordinator.reap()
        state, events, _ = self.record.read()
        observations = [e for e in events if e["id"] == f"home-{run}-observed"]
        self.assertEqual(len(observations), 1)
        self.assertEqual(state["life"]["runs"][run]["outcome"], "success")

    def test_new_coordinator_recovers_observed_result_and_immediately_hands_off(self):
        run = self.coordinator.start("codex")
        self.coordinator.running[run].process.wait(timeout=10)
        with patch("house.home.group_stopped", return_value=False):
            with self.assertRaisesRegex(ValueError, "observed result retained"):
                self.coordinator.reap()
        self.coordinator.running.clear()  # The first coordinator lost its in-memory state.
        replacement = home.Coordinator(self.record, self.runtime)
        self.addCleanup(replacement.close)
        self.assertEqual(replacement.recover(), [run])
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["outcome"], "success")
        following = replacement.tick(poll=False)["started"]
        self.assertEqual(len(following), 1)
        self.assertEqual(self.record.read()[0]["life"]["runs"][following[0]]["agent"], "opencode")
        self.drain(replacement)

    def test_quota_rotates_and_requeues_assigned_help(self):
        self.native.write_text("import json,sys\nprint(json.dumps({'type':'error',"
                               "'message':'usage limit reached'}),flush=True)\nsys.exit(1)\n")
        self.record.append("life", "alice", {"kind": "help", "request": "quota-help", "reason": "Work"})
        run = self.coordinator.start("codex", "quota-help")
        self.drain()
        state = self.record.read()[0]
        self.assertEqual(state["life"]["runs"][run]["outcome"], "quota")
        self.assertEqual(state["life"]["requests"]["quota-help"]["status"], "pending")
        self.assertGreater(state["life"]["budgets"]["codex"]["until"], time.time() + 850)
        self.assertEqual(home.choose_provider(state, time.time(), "codex"), "opencode")

    def test_idle_watchdog_stops_real_process_and_preserves_room(self):
        self.delay = 30
        self.coordinator.inactivity_seconds = 0.5
        run = self.coordinator.start("codex")
        self.drain()
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["outcome"], "interrupted")
        self.assertTrue((self.coordinator.private / "residents" / run / "source.txt").exists())

    def test_crashed_coordinator_recovers_real_orphan_as_interrupted(self):
        script = self.root / "crash.py"
        script.write_text(f"import sys,os\nsys.path.insert(0,{str(SOURCE)!r})\n"
            "from pathlib import Path\nfrom house import home\nfrom house.record import Record\n"
            "home.active_policy=lambda _: {'revision':'synthetic-fixture-policy'}\n"
            "home.active_prompt=lambda _: 'Inert crash fixture'\n"
            f"home.providers.command=lambda k,m,w,p,c,**kwargs: ([sys.executable,{str(self.native)!r},str(p/'native-started'),'30'],dict(os.environ))\n"
            f"c=home.Coordinator(Record({str(self.repo)!r}),Path({str(self.runtime)!r}))\n"
            "run=c.start('codex')\nprint(run,flush=True)\nos._exit(17)\n")
        process = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, 17, process.stderr)
        run = process.stdout.strip()
        item = self.record.read()[0]["life"]["runs"][run]
        self.addCleanup(home.kill_group, item["pgid"])
        self.assertTrue(home.group_members(item["pgid"]))
        self.assertEqual(self.coordinator.recover(), [run])
        self.assertTrue(home.group_stopped(item["pgid"]))
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["outcome"], "interrupted")

    def test_unidentified_process_group_is_never_signalled(self):
        self.delay = 30
        run = self.coordinator.start("codex")
        with patch("house.home.group_members", return_value=["unrelated service"]), \
                patch("house.home.kill_group") as kill:
            with self.assertRaisesRegex(ValueError, "unidentified"):
                self.coordinator.recover()
            kill.assert_not_called()
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["status"], "active")

    def test_singleton_and_provider_fairness(self):
        with home.single_coordinator(self.coordinator.private):
            code = (f"from pathlib import Path;from house.home import single_coordinator;"
                    f"c=single_coordinator(Path({str(self.coordinator.private)!r}));c.__enter__()")
            child = subprocess.run([sys.executable, "-c", code], cwd=SOURCE, capture_output=True, text=True)
            self.assertNotEqual(child.returncode, 0)
            self.assertIn("already running", child.stderr)
        state = {"life": {"runs": {str(n): {"agent": kind, "status": "completed", "started_sequence": n+1}
                                      for n, kind in enumerate(home.KINDS)}, "budgets": {}}}
        self.assertEqual(home.choose_provider(state, 100), "codex")
        state["life"]["budgets"] = {kind: {"until": 101} for kind in home.KINDS}
        self.assertIsNone(home.choose_provider(state, 100))
        self.assertEqual(home.choose_provider(state, 101), "codex")

    def test_pointer_is_selected_only_for_new_launch(self):
        replacement = self.root / "new-runtime.pyz"
        replacement.write_bytes(self.runtime.read_bytes())
        run = self.coordinator.start("codex")
        running = self.coordinator.running[run]
        (self.coordinator.private / "active-runtime.json").write_text("{}")
        with patch("house.runtime.selected", return_value={"entry": str(replacement)}):
            self.coordinator.refresh_runtime()
        self.assertEqual(self.coordinator.runtime, replacement)
        self.assertIs(self.coordinator.running[run], running)
        self.drain()

    def test_native_final_sleep_is_delivered_before_reap(self):
        self.native.write_text("import json,subprocess,sys\nfrom pathlib import Path\n"
            "client=str(Path.cwd()/'.house-client')\nactor=sys.argv[3]\n"
            "def call(*args):\n return json.loads(subprocess.check_output([client,*args],text=True))\n"
            "call('arrive','--as',actor,'--name','Fixture')\n"
            "call('say','--as',actor,'A real local mailbox client reached the journal')\n"
            "seen=call('read','--as',actor,'--limit','200')\n"
            "call('sleep','--as',actor,'--through',str(seen['through']),'--note','Finished through mailbox')\n"
            "print(json.dumps({'type':'turn.completed','usage':{}}),flush=True)\n")
        def command(kind, model, workspace, private, client, **kwargs):
            actor = self.record.read()[0]["life"]["runs"][private.name]["resident"]
            return [sys.executable, str(self.native), str(private / "native-started"), "0", actor], dict(os.environ)
        self.record.append("life", "alice", {"kind": "help", "request": "sleep-help", "reason": "Complete a handoff"})
        with patch("house.home.providers.command", command):
            run = self.coordinator.start("codex", "sleep-help")
        self.drain()
        state, events, _ = self.record.read()
        item = state["life"]["runs"][run]
        self.assertEqual(item["outcome"], "success")
        self.assertFalse(state["residents"][item["resident"]]["awake"])
        self.assertTrue(any(e["op"] == "sleep" and e["actor"] == item["resident"] for e in events))
        self.assertEqual(state["life"]["requests"]["sleep-help"]["status"], "resolved")
        self.assertEqual(json.loads((self.coordinator.private / run / "contribution.json").read_text())["paths"], [])

    def test_old_sleep_or_unfinished_claim_does_not_resolve_help(self):
        for reason in ("woken", "unfinished"):
            self.record.append("life", "alice", {"kind": "help", "request": reason, "reason": "Still needs work"})
            run = self.coordinator.start("codex", reason)
            actor = self.record.read()[0]["life"]["runs"][run]["resident"]
            self.record.append("arrive", actor, {"name": "Fixture"})
            if reason == "unfinished":
                self.record.append("task", actor, {"task": reason, "title": "Unfinished", "description": "Fixture"})
                self.record.append("claim", actor, {"task": reason, "token": "claim-token", "expect": 0, "seconds": 60})
            self.record.append("sleep", actor, {"through": self.record.read()[0]["sequence"], "note": "Earlier handoff"})
            if reason == "woken":
                self.record.append("wake", actor, {})
            self.drain()
            self.assertEqual(self.record.read()[0]["life"]["requests"][reason]["status"], "pending")
