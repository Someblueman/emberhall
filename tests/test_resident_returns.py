"""Synthetic return histories and real inert processes; no live model claims."""
import copy
import json
import os
import sys
import unittest
import uuid
from unittest.mock import patch

from house import council, mailbox, mailbox_jobs, maintenance, resident_actions
from house.integrate import integrate
from house.record import Record
from tests import test_home as home_fixture, test_owner_maintenance as owner_fixture
from tests import test_council, test_wake_policy


class ReturnProjectionTests(unittest.TestCase):
    def setUp(self):
        fixture = owner_fixture.OwnerMaintenanceTests(); fixture.setUp()
        self.h = fixture.h
        migration = fixture.migration() | {"scope": maintenance.CONTINUITY_SCOPE,
            "approval_sha256": maintenance.GROWTH_SHA256}
        migration["protected_files"]["house/model.py"] = maintenance.protected_manifest(self.h.state)["house/model.py"]
        self.h.event("owner-migrate", migration)
        self.start("old")
        self.h.event("arrive", {"name": "Returning Fern"}, "fern")
        self.h.event("life", {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"}, "fern")
        self.h.event("sleep", {"through": self.h.state["sequence"], "note": "Continue the useful thread"}, "fern")
        self.h.event("life", {"kind": "run-finish", "run": "old", "outcome": "success",
            "exit_code": 0, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")

    def payload(self, run):
        return {"kind": "run-start", "run": run, "resident": "fern", "agent": "codex",
            "model": "gpt-6.1-sol", "source_head": "a" * 40, "workspace": "residents/" + run,
            "policy_revision": "fixture", "mode": "work"}

    def start(self, run):
        self.h.event("life", self.payload(run), "watch-keeper")

    def test_return_keeps_memory_and_excludes_simultaneous_reuse(self):
        self.h.event("learn", {"lesson": "kept", "key": "continuity", "claim": "Remember the thread",
                              "evidence": "Synthetic previous-run lesson"}, "fern")
        lessons = copy.deepcopy(self.h.state["lessons"])
        memory = copy.deepcopy(self.h.state["residents"]["fern"])
        self.start("new")
        self.assertEqual(self.h.state["residents"]["fern"], memory)
        self.h.reject("life", self.payload("racing"), "not eligible", "watch-keeper")
        self.h.event("wake", {}, "fern")
        self.assertEqual(self.h.state["residents"]["fern"], memory | {"awake": True})
        self.assertEqual(self.h.state["lessons"], lessons)

    def test_flag_route_awake_and_claim_fences(self):
        before = copy.deepcopy(self.h.state)
        changes = [lambda s: s["maintenance"].update(resident_returns=False),
                   lambda s: s["residents"]["fern"].update(awake=True),
                   lambda s: s["residents"]["fern"].update(model="gpt-6-astra"),
                   lambda s: s["life"]["runs"]["old"].update(model="gpt-6-astra")]
        for change in changes:
            self.h.state = copy.deepcopy(before); change(self.h.state)
            self.h.reject("life", self.payload("wrong"), "not eligible", "watch-keeper")
        self.h.state = copy.deepcopy(before)
        self.h.event("task", {"task": "held", "title": "Held", "description": "Manual claim"})
        self.h.event("claim", {"task": "held", "token": "held-token", "expect": 0, "seconds": 60}, "fern")
        self.h.reject("life", self.payload("live-claim"), "not eligible", "watch-keeper")
        self.h.now += 61
        self.start("expired-claim")
        self.h.reject("renew", {"task": "held", "token": "held-token", "seconds": 60}, "stale", "fern")

    def test_legacy_new_resident_history_remains_valid(self):
        self.h.state["maintenance"]["resident_returns"] = False
        self.h.event("life", self.payload("legacy") | {"resident": "new-person"}, "watch-keeper")
        self.h.event("arrive", {"name": "Legacy new resident"}, "new-person")
        self.assertIn("fern", self.h.state["residents"])


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                 "inert host coordinator uses process-group recovery")
class ReturnProcessTests(unittest.TestCase):
    def setUp(self):
        self.f = home_fixture.HomeTests()
        original_found = Record.found
        def approved_found(record, *args, **kwargs):
            with patch("house.record.uuid.uuid4", side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
                return original_found(record, *args, **kwargs)
        with patch.object(Record, "found", approved_found):
            self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.record, self.coordinator = self.f.record, self.f.coordinator
        self.record.append("council-authorize", "alice", test_council.approval())
        self.record.append("council-wake-authorize", "alice", test_wake_policy.approval())
        state = self.record.read()[0]; old = maintenance.protected_manifest(state)
        self.record.append("owner-migrate", "alice", {"scope": maintenance.CONTINUITY_SCOPE,
            "approval_sha256": maintenance.GROWTH_SHA256, "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64,
            "protected_files": old | {name: "c" * 64 for name in maintenance.OWNER_MODULES},
            "previous_manifest_sha256": maintenance.fingerprint(old), "previous_runtime_sha256": "d" * 64,
            "runtime_sha256": "e" * 64, "test_output_sha256": "f" * 64, "test_count": 1})
        self.f.native.write_text('''import json,subprocess,sys
from pathlib import Path
client,resident,returning,run=sys.argv[1:]
def call(*args):
 p=subprocess.run([client,*args],capture_output=True,text=True,timeout=10)
 if p.returncode: raise RuntimeError(p.stderr)
 return json.loads(p.stdout)
if returning=='yes': call('wake','--as',resident,'--request',run+'-wake')
else: call('arrive','--as',resident,'--name','Fern','--request',run+'-arrive')
page=call('read','--as',resident)
while page['has_more']: page=call('read','--as',resident,'--after',str(page['through']))
call('sleep','--as',resident,'--through',str(page['through']),'--note','Keep the thread','--request',run+'-sleep')
Path('source.txt').write_text('Synthetic preserved contribution')
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':3,'output_tokens':2}}),flush=True)
''')
        def command(kind, model, workspace, private, client, **kwargs):
            resident = kwargs["resident"]
            returning = resident in self.record.read()[0]["residents"]
            return [sys.executable, str(self.f.native), str(client), resident,
                    "yes" if returning else "no", private.name], dict(os.environ)
        mocked = patch("house.home.providers.command", command); mocked.start(); self.addCleanup(mocked.stop)

    def stretch(self):
        run = self.coordinator.start("codex"); self.f.drain()
        state = self.record.read()[0]
        self.assertEqual(state["life"]["runs"][run]["outcome"], "success")
        return run, state["life"]["runs"][run]["resident"]

    def test_two_real_stretches_return_one_identity_with_new_room_and_cursor(self):
        first, resident = self.stretch()
        memory = self.record.read()[0]["residents"][resident]
        second, returned = self.stretch()
        self.assertEqual(returned, resident); self.assertNotEqual(first, second)
        state, events, _ = self.record.read()
        self.assertEqual(state["residents"][resident]["name"], memory["name"])
        self.assertGreater(state["residents"][resident]["cursor"], memory["cursor"])
        self.assertEqual(sum(e["op"] == "arrive" and e["actor"] == resident for e in events), 1)
        prompt = (self.coordinator.private / second / "prompt.txt").read_text()
        self.assertIn("returning as the same resident", prompt)
        self.assertIn('"handoff": "Keep the thread"', prompt)
        self.assertIn("Old room-local request aliases do not transfer", prompt)
        self.assertIn("You cannot independently review your own work", prompt)
        for run in (first, second):
            self.assertTrue((self.coordinator.private / "residents" / run / ".house-client").is_file())

    def test_stale_mailbox_job_and_token_cannot_use_returned_identity(self):
        first, resident = self.stretch()
        self.record.append("task", resident, {"task": "interrupted", "title": "Task", "description": "Preserve"})
        # Confirmed stop on an interrupted later run fences its token.
        start = copy.deepcopy(self.record.read()[0]["life"]["runs"][first])
        payload = {key: start[key] for key in ("kind", "resident", "agent", "model", "source_head", "policy_revision", "mode")}
        self.record.append("life", "watch-keeper", payload | {"run": "crash", "workspace": "residents/crash"})
        self.record.append("wake", resident, {})
        self.record.append("claim", resident, {"task": "interrupted", "expect": 0, "token": "old-token", "seconds": 60})
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": "crash", "outcome": "interrupted",
            "exit_code": None, "usage": {}, "elapsed_seconds": 1})
        second, returned = self.stretch(); self.assertEqual(returned, resident)
        self.assertIn('"outcome": "interrupted"', (self.coordinator.private / second / "prompt.txt").read_text())
        self.assertIn('"released_tasks": ["interrupted"]', (self.coordinator.private / second / "prompt.txt").read_text())
        self.record.append("life", "watch-keeper", payload | {"run": "current", "workspace": "residents/current"})
        self.record.append("wake", resident, {})
        self.record.append("claim", resident, {"task": "interrupted", "expect": 1, "token": "new-token", "seconds": 60})
        with self.assertRaisesRegex(ValueError, "stale"):
            self.record.append("finish", resident, {"task": "interrupted", "token": "old-token", "result": "stale", "artifacts": {}})
        old_room = self.coordinator.private / "residents" / first
        (old_room / ".house-mailbox/requests" / ("a" * 64 + ".json")).write_text(json.dumps(
            {"version": 1, "id": "a" * 64, "argv": ["wake", "--as", resident]}))
        head = self.record.read()[2]
        self.assertEqual(mailbox.service(self.record, self.coordinator.private, first), 0)
        with self.assertRaisesRegex(ValueError, "assigned active"):
            resident_actions.execute(self.record, old_room, resident, first,
                                     ["council", "--as", resident, "status"], "old-job")
        self.assertEqual(self.record.read()[2], head)
        # A delayed queued job is also tied to the old run, not just the person.
        job = mailbox_jobs.enqueue(self.record, first, ["council", "--as", resident, "status"], "old-queued-job")
        mailbox_jobs.tick(self.record)
        self.assertFalse(mailbox_jobs.result(self.record, job)["ok"])
        self.assertEqual(self.record.read()[2], head)
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, first, resident)

    def test_atomic_competing_returns_admit_one(self):
        first, resident = self.stretch()
        old = self.record.read()[0]["life"]["runs"][first]
        payload = {key: old[key] for key in ("kind", "resident", "agent", "model", "source_head", "policy_revision", "mode")}
        children = [self.f.process("life", "--as", "watch-keeper", "--data", json.dumps(
            payload | {"run": run, "workspace": "residents/" + run})) for run in ("race-one", "race-two")]
        codes = []
        for child in children:
            child.communicate(timeout=15); codes.append(child.returncode)
        self.assertEqual(sorted(codes), [0, 2])

    def test_oldest_eligible_sleeper_returns_before_new_identity(self):
        first, older = self.stretch()
        self.record.append("wake", older, {})
        second, newer = self.stretch()
        self.assertNotEqual(older, newer)
        self.record.append("sleep", older, {"through": self.record.read()[0]["sequence"], "note": "Return later"})
        third, chosen = self.stretch()
        self.assertEqual(chosen, older)
        fourth, chosen = self.stretch()
        self.assertEqual(chosen, newer)
        self.assertEqual(len({self.record.read()[0]["life"]["runs"][run]["resident"]
                              for run in (first, second, third, fourth)}), 2)

    def test_prior_sleep_does_not_resolve_later_success_without_new_handoff(self):
        first, resident = self.stretch()
        self.record.append("life", "alice", {"kind": "help", "request": "still-needed",
            "agent": "codex", "reason": "Require a real new handoff"})
        self.f.native.write_text("import json\nprint(json.dumps({'type':'turn.completed','usage':{}}),flush=True)\n")
        second = self.coordinator.start("codex", "still-needed"); self.f.drain()
        state, events, _ = self.record.read()
        run = state["life"]["runs"][second]
        self.assertEqual(run["resident"], resident)
        self.assertEqual(run["outcome"], "success")
        self.assertFalse(any(event["actor"] == resident and event["op"] in {"wake", "sleep"}
                             for event in events[run["started_sequence"]:]))
        self.assertEqual(state["life"]["requests"]["still-needed"]["status"], "pending")
        self.assertNotIn("resolved_at", state["life"]["requests"]["still-needed"])
