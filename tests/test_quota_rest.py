"""A model that has hit its quota rests until its provider says it returns; Codex carries its share.

Steward, 16 November: OpenCode's weekly limit and one Antigravity model's limit had run out for six
days. The house rested the whole family for fifteen minutes and then spent a real start finding out
again. Both providers say when the limit returns; these tests use their own words.
"""
import collections
import json
import os
import pathlib
import time
import unittest
from unittest.mock import patch

from house import body, course, home, life, providers
from house.life import CONTROLLER
from tests import test_home

OPENCODE = json.dumps({"type": "error", "timestamp": 1794856345792, "sessionID": "ses_x", "error": {
    "type": "provider.go-limit",
    "message": "OpenCode Go weekly usage limit reached. Switch to a free model, or turn on Extra Usage on the Go "
               "page in OpenCode Console to keep going.",
    "status": 429, "response": {"body": json.dumps({"type": "error", "error": {
        "type": "GoUsageLimitError", "message": "OpenCode Go usage limit reached (weekly, resets in 6d 4h). To keep "
        "going now, turn on Extra Usage or upgrade to Go Plus."}, "metadata": {"limitName": "weekly"}})},
    "retryAfterMs": 535655000}})
AGY_OUT = "\n".join((json.dumps({"event": "init", "conversation_id": "c1"}), json.dumps({"event": "result", "result": {
    "conversation_id": "c1", "status": "ERROR", "response": "",
    "error": "Individual quota reached. Please upgrade your subscription to increase your limits. Resets in 143h1m4s.",
    "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}, "finished_reason": "error"}})))
AGY_ERR = ("error: Individual quota reached. Please upgrade your subscription to increase your limits. "
           "Resets in 143h1m4s.\n")
ARGON, HYDROGEN = "gemini-4-argon-high", "gemini-4-hydrogen-high"


class ReadingTests(unittest.TestCase):
    def test_each_provider_says_when_its_limit_returns(self):
        go = providers.result("opencode", OPENCODE, "", 1)
        self.assertEqual(("quota", 535655.0), (go["outcome"], go["retry_after_seconds"]))
        agy = providers.result("agy", AGY_OUT, AGY_ERR, 3)
        self.assertEqual(("quota", 143 * 3600 + 64.0), (agy["outcome"], agy["retry_after_seconds"]))

    def test_a_limit_that_names_no_time_or_an_absurd_one_is_not_trusted(self):
        self.assertIsNone(providers.reset_after("429 Too many requests"))
        self.assertIsNone(providers.reset_after("quota reached, resets in 400d"))
        self.assertEqual(21600, providers.reset_after("usage limit reached (resets in 6h)"))
        self.assertEqual(60, providers.reset_after("rate limit, resets in 5s"))
        plain = providers.result("codex", json.dumps({"type": "error", "message": "429 Too many requests"}), "", 1)
        self.assertEqual("quota", plain["outcome"])
        self.assertNotIn("retry_after_seconds", plain)
        done = providers.result("codex", json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}), "", 0)
        self.assertEqual({"outcome": "success", "usage": {"input_tokens": 1}}, done)


def house(installed=True):
    return {"sequence": 10, "at": 1000.0, "residents": {}, "tasks": {}, "life": life.empty(),
            "maintenance": {"migrations": {life.QUOTA_REST: {"at": 900.0}} if installed else {}}}


def rest(state, agent, model, until, at=1000.0, **more):
    state["sequence"] += 1
    life.apply(state, {"actor": CONTROLLER, "at": at, "data": {
        "kind": "budget", "agent": agent, "model": model, "until": until, "reason": "quota", **more}})


class RecordTests(unittest.TestCase):
    def test_before_the_decision_a_model_cannot_rest(self):
        state = house(installed=False)
        with self.assertRaisesRegex(ValueError, "not enabled yet"):
            rest(state, "agy", ARGON, 5000)
        self.assertTrue(life.model_available(state, "agy", ARGON, 1000))

    def test_one_capped_model_rests_and_its_family_carries_on(self):
        state = house()
        rest(state, "agy", ARGON, 1000 + life.PROBE_SECONDS, resets_at=1000 + 514864)
        self.assertFalse(life.model_available(state, "agy", ARGON, 2000))
        self.assertTrue(life.model_available(state, "agy", HYDROGEN, 2000))
        self.assertTrue(life.provider_available(state, "agy", 2000), "hydrogen still has room")
        self.assertEqual([HYDROGEN], life.open_models(state, "agy", 2000))
        self.assertEqual({}, state["life"]["budgets"], "the family-wide cooldown is untouched")
        self.assertEqual(1000 + 514864, state["life"]["model_budgets"]["agy"][ARGON]["resets_at"])
        self.assertTrue(life.model_available(state, "agy", ARGON, 1000 + life.PROBE_SECONDS), "then it is tried again")
        with self.assertRaisesRegex(ValueError, "outside the Steward's allowance"):
            rest(state, "agy", "gemini-9", 5000)
        rest(state, "agy", ARGON, 1500)
        self.assertEqual(1000 + life.PROBE_SECONDS, state["life"]["model_budgets"]["agy"][ARGON]["until"],
                         "a later failure cannot shorten the rest")

    def test_a_family_with_every_route_capped_is_unavailable_until_one_returns(self):
        state = house()
        for n, model in enumerate(providers.ROTATION["opencode"]):
            rest(state, "opencode", model, 5000 + n)
        self.assertFalse(life.provider_available(state, "opencode", 4000))
        self.assertTrue(life.provider_available(state, "opencode", 5000), "the first route back reopens the family")
        self.assertTrue(life.provider_available(state, "codex", 4000))

    def test_the_record_refuses_a_start_on_a_resting_model(self):
        state = house()
        state["residents"][CONTROLLER] = {"awake": True, "name": "Watch keeper"}
        rest(state, "agy", ARGON, 5000)
        start = {"kind": "run-start", "run": "a" * 32, "resident": "resident-new", "agent": "agy", "model": ARGON,
                 "source_head": "0" * 40, "workspace": "w", "policy_revision": "p", "mode": "work"}
        with self.assertRaisesRegex(ValueError, "resting until its quota returns"):
            life.apply(state, {"actor": CONTROLLER, "at": 2000.0, "data": start})


class WaitingTests(unittest.TestCase):
    """The night this was installed, a wake aimed at a resident on a resting model sat first in the
    queue. The coordinator chose its family (another route was open), could not start it, and stopped
    looking, every tick: nothing started for ten minutes. Such a wake waits without being offered."""

    def request(self):
        return {"kind": "help", "status": "pending", "agent": "agy", "model": ARGON, "target_resident": "resident-x"}

    def test_a_wake_aimed_at_a_resting_model_waits_and_is_not_offered(self):
        state = house()
        rest(state, "agy", ARGON, 5000)
        with patch("house.life.return_eligible", return_value=True):
            self.assertFalse(life.targeted_pending_eligible(state, self.request(), 2000))
            self.assertTrue(life.targeted_pending_eligible(state, self.request(), 5000), "offered once it returns")
            other = {**self.request(), "model": HYDROGEN}
            self.assertTrue(life.targeted_pending_eligible(state, other, 2000), "its family's open route is unaffected")

    def test_the_queue_does_not_list_it(self):
        state = house()
        state["life"]["requests"]["r1"] = self.request()
        with patch("house.life.return_eligible", return_value=True):
            self.assertEqual(["r1"], life.workload(state, 2000)["pending_help"])
            rest(state, "agy", ARGON, 5000)
            self.assertEqual([], life.workload(state, 2000)["pending_help"])
            self.assertEqual(["r1"], life.workload(state, 5000)["pending_help"])


class SharingTests(unittest.TestCase):
    def capped(self):
        state = house()
        for model in providers.ROTATION["opencode"]:
            rest(state, "opencode", model, 9000)
        rest(state, "agy", ARGON, 9000)
        return state

    def test_routes_pass_over_a_resting_model(self):
        state = self.capped()
        self.assertEqual(HYDROGEN, course.route(state, "agy", at=2000))
        self.assertEqual(HYDROGEN, course.route(state, "agy", strong=True, at=2000), "the stronger route is resting")
        self.assertEqual(ARGON, course.route(state, "agy", strong=True, at=9000))
        self.assertEqual(ARGON, course.route(state, "agy", strong=True), "callers that give no time are unchanged")

    def test_codex_takes_the_share_resting_routes_leave(self):
        state = self.capped()
        self.assertEqual({"codex": 2.5, "opencode": 0.0, "muse": 1.0, "agy": 0.5}, home.provider_shares(state, 2000))
        self.assertEqual({kind: 1.0 for kind in home.KINDS}, home.provider_shares(state, 9000), "limits returned")
        self.assertEqual({kind: 1.0 for kind in home.KINDS}, home.provider_shares(house(installed=False), 2000))
        runs = state["life"]["runs"]
        picked = collections.Counter()
        for n in range(96):
            kind = home.choose_provider(state, 2000)
            picked[kind] += 1
            runs[str(n)] = {"agent": kind, "status": "completed", "started_sequence": n + 1, "model": "m"}
        self.assertEqual(0, picked["opencode"])
        self.assertEqual(96, picked["codex"] + picked["muse"] + picked["agy"])
        self.assertTrue(56 <= picked["codex"] <= 62 and 22 <= picked["muse"] <= 26 and 10 <= picked["agy"] <= 15,
                        f"about five in eight to Codex, a quarter to Muse, an eighth to the half-open family: {picked}")

    def test_codex_may_hold_several_runs_while_it_carries_others(self):
        state = self.capped()
        runs = state["life"]["runs"]
        for n in range(2):
            runs[f"c{n}"] = {"agent": "codex", "status": "active", "started_sequence": n + 1, "model": "m"}
        runs["m"] = {"agent": "muse", "status": "active", "started_sequence": 3, "model": "m"}
        self.assertEqual("agy", home.choose_provider(state, 2000), "an idle family with an open route goes first")
        runs["a"] = {"agent": "agy", "status": "active", "started_sequence": 4, "model": HYDROGEN}
        self.assertEqual("codex", home.choose_provider(state, 2000), "a third Codex run before a second Muse run")
        ordinary = house()
        ordinary["life"]["runs"] = {"c": {"agent": "codex", "status": "active", "started_sequence": 1, "model": "m"}}
        self.assertNotEqual("codex", home.choose_provider(ordinary, 2000), "with no limits reached, one run each")

    def test_if_codex_is_resting_too_nothing_is_moved(self):
        state = self.capped()
        for model in providers.ROTATION["codex"]:   # Codex rests only when every one of its routes does
            rest(state, "codex", model, 9000)
        self.assertEqual({kind: 1.0 for kind in home.KINDS}, home.provider_shares(state, 2000))
        self.assertIn(home.choose_provider(state, 2000), {"muse", "agy"})

    def test_the_public_page_wording_names_the_return_and_who_covers(self):
        source = (pathlib.Path(body.__file__).parents[1] / "site/house.js").read_text()
        self.assertIn("function quotaRestWords(agent,now)", source)
        self.assertIn("its provider says it returns", source)
        self.assertIn("Codex covers its share until then", source)
        self.assertIn('frame["model_rests"]', pathlib.Path(body.__file__).read_text())


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                 "host process-recovery fixture requires macOS setuid ps")
class CoordinatorTests(unittest.TestCase):
    """The real coordinator, with a native that answers as OpenCode Go does at its weekly limit."""

    def setUp(self):
        self.h = test_home.HomeTests("test_completed_process_is_success_when_supervisor_is_stopping")
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.addCleanup(self.h.tearDown)
        self.h.native.write_text(f"import sys\nprint({OPENCODE!r})\nsys.exit(1)\n")

    def enable(self):
        for target in ("house.life.quota_rest", "house.home.quota_rest"):
            helper = patch(target, lambda state: True)
            helper.start(); self.addCleanup(helper.stop)
        helper = patch("house.course.enabled", lambda state: True)
        helper.start(); self.addCleanup(helper.stop)

    def test_before_the_decision_a_quota_is_a_fifteen_minute_family_rest(self):
        run = self.h.coordinator.start("opencode")
        self.h.drain()
        state = self.h.record.read()[0]
        self.assertEqual("quota", state["life"]["runs"][run]["outcome"])
        budget = state["life"]["budgets"]["opencode"]
        self.assertLess(budget["until"], time.time() + 1000)
        self.assertNotIn("model_budgets", state["life"])

    def test_a_weekly_limit_rests_that_model_until_it_returns_and_the_next_start_takes_another(self):
        self.enable()
        run = self.h.coordinator.start("opencode")
        self.h.drain()
        state = self.h.record.read()[0]
        first = state["life"]["runs"][run]
        self.assertEqual("quota", first["outcome"])
        self.assertNotIn("opencode", state["life"]["budgets"], "the family is not benched")
        resting = state["life"]["model_budgets"]["opencode"][first["model"]]
        now = time.time()
        self.assertAlmostEqual(now + life.PROBE_SECONDS, resting["until"], delta=120)
        self.assertAlmostEqual(now + 535655, resting["resets_at"], delta=120)
        self.assertEqual("quota", resting["reason"])
        self.assertTrue(life.provider_available(state, "opencode", now))
        again = self.h.coordinator.start("opencode")
        self.h.drain()
        second = self.h.record.read()[0]["life"]["runs"][again]
        self.assertNotEqual(first["model"], second["model"], "the next start takes a route that is not resting")
        third = self.h.coordinator.start("opencode")
        self.h.drain()
        state = self.h.record.read()[0]
        self.assertEqual(3, len(state["life"]["model_budgets"]["opencode"]))
        self.assertFalse(life.provider_available(state, "opencode", time.time()), "every route is resting now")
        self.assertIsNone(self.h.coordinator.start("opencode"))
        self.assertEqual(2.0, home.provider_shares(state, time.time())["codex"])
        self.assertIsNotNone(third)


if __name__ == "__main__":
    unittest.main()
