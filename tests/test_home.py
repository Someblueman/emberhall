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
                if file.name != "opencode_auth.py":
                    archive.write(file, "house/" + file.name)
            # Inert native fixtures must never inspect the actual account. The
            # installed importer boundary has separate synthetic-credential tests.
            archive.writestr("house/opencode_auth.py", "def bootstrap(executable, source, private, env):\n"
                " (private / 'auth-prepared').write_text('synthetic account fixture')\n")
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
        env = dict(os.environ, EMBERHALL_OPENCODE_SOURCE_DB=str(private / "synthetic-auth.db"))
        return [sys.executable, str(self.native), str(private / "native-started"), str(self.delay)], env

    def drain(self, coordinator=None):
        coordinator = coordinator or self.coordinator
        deadline = time.monotonic() + 15
        while coordinator.running and time.monotonic() < deadline:
            coordinator.tick(start=False, poll=False)
            time.sleep(0.03)
        self.assertFalse(coordinator.running, "fixture process failed to finish")

    def test_completed_process_is_success_when_supervisor_is_stopping(self):
        run = self.coordinator.start("codex")
        process = self.coordinator.running[run].process
        self.assertEqual(0, process.wait(timeout=15))
        self.coordinator.stopping = True
        self.coordinator.tick(poll=False)
        result = self.record.read()[0]["life"]["runs"][run]
        self.assertEqual("success", result["outcome"])
        self.assertEqual({"input_tokens": 3, "output_tokens": 2}, result["usage"])

    def test_completed_process_is_not_interrupted_by_late_inactivity_check(self):
        run = self.coordinator.start("codex")
        running = self.coordinator.running[run]
        self.assertEqual(0, running.process.wait(timeout=15))
        path = self.coordinator.private / run
        running.sizes = tuple((path / name).stat().st_size for name in ("stdout.jsonl", "stderr.log"))
        running.last_activity = time.monotonic() - self.coordinator.inactivity_seconds - 1
        self.coordinator.tick(start=False, poll=False)
        self.assertEqual("success", self.record.read()[0]["life"]["runs"][run]["outcome"])

    def test_muse_continuation_transcript_finishes_without_false_provider_hold(self):
        transcript = (SOURCE / "evidence/keep-moving-runtime/muse-sequential-turns.jsonl").read_text()
        self.native.write_text("import sys\nsys.stdout.write(" + repr(transcript) + ")\n")
        run = self.coordinator.start("muse")
        self.drain()
        state = self.record.read()[0]
        self.assertEqual("success", state["life"]["runs"][run]["outcome"])
        self.assertEqual(14055014, state["life"]["runs"][run]["usage"]["input_tokens"])
        self.assertNotIn("muse", state["life"]["budgets"])

    def test_assignment_names_the_actual_provider_transport(self):
        for kind in ("opencode", "codex"):
            run = self.coordinator.start(kind)
            prompt = (self.coordinator.private / run / "prompt.txt").read_text()
            if kind == "opencode":
                self.assertIn("Use the house_journal tool with an argv array", prompt)
                self.assertIn('house_journal argv ["wait", "--as",', prompt)
                self.assertNotIn(".house-client for every canonical", prompt)
            else:
                self.assertIn(".house-client for every canonical", prompt)
                self.assertNotIn("Use the house_journal", prompt)
            self.drain()
            if kind == "opencode":
                self.assertTrue((self.coordinator.private / run / "auth-prepared").exists())

    def test_due_checkpoint_names_fixed_channel_and_metadata_only_finish(self):
        evidence = self.repo / "evidence"
        evidence.mkdir()
        (evidence / "checkpoint.json").write_text(json.dumps({"last_event_utc": "2000-01-01T00:00:00+00:00"}))
        git(self.repo, "add", "evidence/checkpoint.json")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "Old fixture checkpoint")
        run = self.coordinator.start("codex")
        resident = self.record.read()[0]["life"]["runs"][run]["resident"]
        prompt = (self.coordinator.private / run / "prompt.txt").read_text()
        self.assertIn(f"checkpoint --as {resident} --task TASK --token TOKEN --request {run}-checkpoint", prompt)
        self.assertIn("Finish with the metadata only", prompt)
        self.assertIn("independent source review", prompt)
        self.drain()

    def test_ready_backlog_fills_only_uncovered_capacity_without_help(self):
        self.delay = 30
        self.coordinator.start("codex")
        for name in ("one", "two", "three"):
            self.record.append("task", "alice", {"task": name, "title": name,
                "description": "Independent fixture work", "ready": True})
        result = self.coordinator.tick(poll=False)
        self.assertEqual(len(result["started"]), 2)
        self.assertEqual(len(result["active"]), 3)
        self.assertEqual(self.coordinator.tick(poll=False)["started"], [])
        state = self.record.read()[0]
        self.assertEqual(state["life"]["requests"], {})
        self.assertTrue(all(state["life"]["runs"][run]["backlog"] for run in result["started"]))
        self.assertIn("task with --ready", (self.coordinator.private / result["started"][0] / "prompt.txt").read_text())
        for item in self.coordinator.running.values():
            item.process.terminate()
        self.drain()

    def test_backlog_claim_during_provider_choice_does_not_launch_stale_work(self):
        self.delay = 30
        self.coordinator.start("codex")
        for name in ("one", "two"):
            self.record.append("task", "alice", {"task": name, "title": name,
                "description": "Independent fixture work", "ready": True})
        old_choose = home.choose_provider
        def choose(state, at, preferred=None, **kwargs):
            self.record.append("claim", "alice", {"task": "two", "expect": 0,
                "token": "won-before-admission", "seconds": 60})
            return old_choose(state, at, preferred, **kwargs)
        with patch("house.home.choose_provider", side_effect=choose):
            result = self.coordinator.tick(poll=False)
        self.assertEqual(result["started"], [])
        self.assertEqual(len(self.record.read()[0]["life"]["runs"]), 1)
        self.assertEqual(len(list(self.coordinator.private.glob("*/prompt.txt"))), 1)
        for item in self.coordinator.running.values():
            item.process.terminate()
        self.drain()

    def test_ready_work_respects_cooldowns_and_failed_start_does_not_spin(self):
        self.record.append("task", "alice", {"task": "one", "title": "One", "ready": True,
                                             "description": "Independent fixture work"})
        with patch("house.home.providers.command", side_effect=ValueError("inert startup failure")):
            result = self.coordinator.tick(poll=False)
        self.assertEqual(len(result["started"]), 1)
        self.assertEqual(result["active"], [])
        for kind in home.KINDS:
            self.record.append("life", CONTROLLER, {"kind": "budget", "agent": kind,
                "until": time.time() + 3600, "reason": "Synthetic unavailable allowance"})
        before = self.record.read()
        self.assertEqual(self.coordinator.tick(poll=False)["started"], [])
        self.assertEqual(self.record.read(), before)

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

    def test_requested_model_is_used_only_for_its_kind_and_recorded_in_prompt(self):
        self.record.append("life", "alice", {"kind": "help", "request": "deep-review",
            "reason": "A difficult review", "agent": "codex", "model": "gpt-6-astra"})
        with patch("house.home.providers.command", wraps=self.command) as native:
            first = self.coordinator.start("codex", "deep-review")
            self.assertEqual(native.call_args.args[1], "gpt-6-astra")
        self.assertIn("codex / gpt-6-astra", (self.coordinator.private / first / "prompt.txt").read_text())
        self.drain()
        with patch("house.home.providers.command", wraps=self.command) as native:
            second = self.coordinator.start("muse", "deep-review")
            self.assertEqual(native.call_args.args[1], "muse-ember-1.0")
        self.drain()
        self.assertEqual(self.record.read()[0]["life"]["runs"][second]["model"], "muse-ember-1.0")
        events = self.record.read()[1]
        receipt = next(e for e in events if e["id"] == f"home-{second}-assignment")
        observation = json.loads(receipt["data"]["text"][len(home.work_metrics.ASSIGNMENT_PREFIX):])
        self.assertEqual(observation["reason"], "direct")
        self.assertEqual(observation["requested_agent"], "codex")

    def test_expired_native_credential_keeps_long_backoff_after_failed_finish(self):
        self.native.write_text("import json\nprint(json.dumps({'type':'error','error':"
            "{'data':{'statusCode':401,'message':'This API key has expired.'}}}))\n")
        run = self.coordinator.start("opencode")
        self.drain()
        state = self.record.read()[0]
        self.assertEqual(state["life"]["runs"][run]["outcome"], "failed")
        budget = state["life"]["budgets"]["opencode"]
        self.assertGreater(budget["until"], time.time() + 23 * 3600)
        self.assertIn("credentials", budget["reason"])

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

    def test_scheduled_start_records_reason_and_waiting_without_changing_outcome(self):
        result = self.coordinator.tick(poll=False)
        run = result["started"][0]
        self.drain()
        state, events, _ = self.record.read()
        observations = [e["data"]["text"] for e in events if e["op"] == "say" and e["actor"] == CONTROLLER]
        assignment = next(json.loads(text[len(home.work_metrics.ASSIGNMENT_PREFIX):])
                          for text in observations if text.startswith(home.work_metrics.ASSIGNMENT_PREFIX))
        self.assertEqual(assignment["run"], run)
        self.assertEqual(assignment["reason"], "balanced")
        self.assertEqual(assignment["lane"], "work")
        self.assertEqual(assignment["prior_starts"], dict.fromkeys(home.KINDS, 0))
        self.assertTrue(any(text.startswith(home.work_metrics.WAIT_PREFIX) for text in observations))
        self.assertEqual(state["life"]["runs"][run]["outcome"], "success")

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

    def test_finished_task_survives_actual_late_native_error(self):
        from house.files import artifact, workspace_path
        self.native.write_text("import json,sys,time\nfrom pathlib import Path\n"
            "while not Path('proof.txt').exists(): time.sleep(0.01)\n"
            "print(json.dumps({'type':'error','message':'malformed terminal response'}),flush=True)\n"
            "sys.exit(1)\n")
        self.task()
        self.record.append("life", "alice", {"kind": "help", "request": "build",
            "task": "work", "reason": "Build a deliverable"})
        run = self.coordinator.start("codex", "build")
        actor = self.record.read()[0]["life"]["runs"][run]["resident"]
        self.record.append("arrive", actor, {"name": "Builder"})
        self.record.append("claim", actor, {"task": "work", "expect": 0, "token": "build", "seconds": 60})
        proof = self.root / "proof.txt"; proof.write_text("Durable deliverable\n")
        self.record.append("finish", actor, {"task": "work", "token": "build", "result": "Built",
            "artifacts": {"proof.txt": artifact(self.root, "proof.txt")}})
        (workspace_path(self.record, run) / "proof.txt").write_bytes(proof.read_bytes())
        self.drain()
        state = self.record.read()[0]
        self.assertEqual(state["life"]["runs"][run]["outcome"], "failed")
        self.assertEqual(state["life"]["requests"]["build"]["status"], "resolved")
        self.assertTrue((self.coordinator.private / run / "preservation.json").exists())


class CompletedHelpTests(HouseCase):
    """Real journal/recovery boundaries without host ps or model execution."""

    def setUp(self):
        super().setUp()
        self.record.append("arrive", CONTROLLER, {"name": "Clock"})
        self.runtime = self.root / "inert-runtime.pyz"
        self.runtime.touch()  # These tests never execute a runtime or native route.
        self.coordinator = home.Coordinator(self.record, self.runtime)

    def offer(self, key="build", **binding):
        self.record.append("life", "alice", {"kind": "help", "request": key,
            "reason": "Build work", **binding})

    def start_record(self, run="worker", key="build"):
        data = {"kind": "run-start", "run": run, "resident": "resident-" + run,
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
            "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "work"}
        if key:
            data["help_request"] = key
        self.record.append("life", CONTROLLER, data)
        self.record.append("arrive", data["resident"], {"name": run})
        return data["resident"]

    def complete(self, task="work", actor="alice"):
        from house.files import artifact
        self.record.append("claim", actor, {"task": task, "expect": 0, "token": task, "seconds": 60})
        (self.repo / "proof.txt").write_text("Durable deliverable\n")
        self.record.append("finish", actor, {"task": task, "token": task, "result": "Built",
            "artifacts": {"proof.txt": artifact(self.repo, "proof.txt")}})

    def result(self, outcome):
        return {"outcome": outcome, "exit_code": 0 if outcome == "success" else 1,
            "usage": {}, "elapsed_seconds": 1}

    def late_error(self, outcome):
        self.task(); self.offer(task="work"); actor = self.start_record()
        self.complete(actor=actor)
        self.record.append("task", actor, {"task": "left", "title": "Unfinished",
            "description": "Release on observed stop"})
        self.record.append("claim", actor, {"task": "left", "expect": 0,
            "token": "old", "seconds": 60})
        self.coordinator.finish("worker", self.result(outcome))
        state = self.record.read()[0]
        self.assertEqual(state["life"]["requests"]["build"]["status"], "resolved")
        self.assertEqual(state["life"]["runs"]["worker"]["outcome"], outcome)
        self.assertEqual(state["life"]["runs"]["worker"]["exit_code"], 1)
        self.assertGreater(state["life"]["budgets"]["codex"]["until"], time.time())
        self.assertEqual(state["tasks"]["left"]["status"], "open")
        self.assertIn("proof.txt", state["tasks"]["work"]["artifacts"])

    def test_done_task_survives_late_failure_with_other_claim_release(self):
        self.late_error("failed")

    def test_done_task_survives_quota_with_other_claim_release(self):
        self.late_error("quota")

    def test_crash_after_task_finish_resolves_once_across_recovery(self):
        self.task(); self.offer(task="work"); self.start_record(); self.complete()
        self.assertEqual(self.coordinator.recover(), ["worker"])
        state, events, _ = self.record.read()
        self.assertEqual(state["life"]["requests"]["build"]["status"], "resolved")
        self.assertEqual(state["life"]["runs"]["worker"]["outcome"], "interrupted")
        head = self.record.read()[2]
        self.assertEqual(home.Coordinator(self.record, self.runtime).recover(), [])
        self.assertEqual(self.record.read()[2], head)
        self.assertEqual(sum(e["data"].get("kind") == "help-resolved" for e in events), 1)

    def test_recovery_retry_after_resolution_before_terminal_run_does_not_duplicate(self):
        self.task(); self.offer(task="work"); self.start_record(); self.complete()
        append = self.record.append
        def interrupted(op, actor, data, request=None):
            if data.get("kind") == "run-finish":
                raise OSError("Crash before terminal receipt")
            return append(op, actor, data, request)
        with patch.object(self.record, "append", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "Crash before terminal"):
                self.coordinator.recover()
        replacement = home.Coordinator(self.record, self.runtime)
        self.assertEqual(replacement.recover(), ["worker"])
        self.assertEqual(replacement.recover(), [])
        events = self.record.read()[1]
        self.assertEqual(sum(e["data"].get("kind") == "help-resolved" for e in events), 1)

    def test_previously_requeued_done_task_is_resolved_before_another_launch(self):
        self.task(); self.offer(task="work"); self.start_record(); self.complete()
        self.record.append("life", CONTROLLER, {"kind": "run-finish", "run": "worker",
            **self.result("interrupted")})  # The older coordinator requeued it.
        with patch("house.home.providers.command", side_effect=AssertionError("must not launch")):
            self.assertIsNone(self.coordinator.start("codex", "build"))
        self.assertEqual(self.record.read()[0]["life"]["requests"]["build"]["status"], "resolved")
        self.assertEqual(len(self.record.read()[0]["life"]["runs"]), 1)

    def test_tick_removes_completed_pending_demand_before_admission(self):
        self.task(); self.offer(task="work"); self.complete()
        self.start_record(key=None)  # Minimum-one presence is already covered.
        with patch("house.home.providers.command", side_effect=AssertionError("must not launch")):
            self.assertEqual(self.coordinator.tick(poll=False)["started"], [])
        self.assertEqual(self.record.read()[0]["life"]["requests"]["build"]["status"], "resolved")

    def test_task_finished_during_runtime_refresh_is_resolved_before_admission(self):
        self.task(); self.offer(task="work")
        with patch.object(self.coordinator, "refresh_runtime", side_effect=self.complete), \
                patch("house.home.active_policy", side_effect=AssertionError(
                    "completed help reached admission policy")):
            self.assertIsNone(self.coordinator.start("codex", "build"))
        state = self.record.read()[0]
        self.assertEqual(state["life"]["requests"]["build"]["status"], "resolved")
        self.assertEqual(state["life"]["runs"], {})

    def test_successful_sleep_cannot_complete_unfinished_bound_task(self):
        self.task(); self.offer(task="work"); actor = self.start_record()
        self.record.append("sleep", actor, {"through": 0, "note": "No deliverable yet"})
        self.coordinator.finish("worker", self.result("success"))
        self.assertEqual(self.record.read()[0]["life"]["requests"]["build"]["status"], "pending")

    def test_unbound_matching_task_name_and_reason_do_not_imply_completion(self):
        self.task(); self.complete(); self.offer("work")
        self.start_record(key="work")
        self.coordinator.finish("worker", self.result("interrupted"))
        self.assertEqual(self.record.read()[0]["life"]["requests"]["work"]["status"], "pending")
        for run, sleep in (("awake", False), ("handoff", True)):
            actor = self.start_record(run, key="work")
            if sleep:
                self.record.append("sleep", actor, {"through": 0, "note": "Current handoff"})
            self.coordinator.finish(run, self.result("success"))
            expected = "resolved" if sleep else "pending"
            self.assertEqual(self.record.read()[0]["life"]["requests"]["work"]["status"], expected)

    def test_done_task_does_not_replace_source_review_receipt(self):
        from tests.test_explorer_dispatch_home import configure
        from tests.test_source_review import SourceReviewTests
        configure(self, SourceReviewTests)
        self.coordinator = home.Coordinator(self.record, self.runtime)
        self.start_record("source", key=None)
        self.record.append("life", CONTROLLER, {"kind": "run-finish", "run": "source",
            **self.result("success")})
        self.task(); self.complete(); self.offer(task="work", review_run="source")
        actor = self.start_record()
        self.record.append("sleep", actor, {"through": 0, "note": "Review still unavailable"})
        self.coordinator.finish("worker", self.result("success"))
        self.assertEqual(self.record.read()[0]["life"]["requests"]["build"]["status"], "pending")
        saved = self.coordinator.private / "source"; saved.mkdir()
        (saved / "contribution.json").write_text(json.dumps({"commit": "b" * 40}))
        (saved / "integration.json").write_text(json.dumps({"run": "source",
            "contribution": "b" * 40, "status": "rejected"}))
        self.start_record("reviewer")
        self.coordinator.finish("reviewer", self.result("failed"))
        self.assertEqual(self.record.read()[0]["life"]["requests"]["build"]["status"], "resolved")
