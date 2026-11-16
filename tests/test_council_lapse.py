"""An enactment closes only pending proposals about the same thing (owner upgrade of 16 November)."""
import unittest
from unittest.mock import patch

from house import body, council
from tests import test_council

DAY = 86400


def house():
    """The council fixture as a helper object; its own tests are not collected from this module."""
    return type("House", (test_council.CouncilTests,), {"runTest": lambda self: None})()


class ScopedLapseTests(unittest.TestCase):
    def setUp(self):
        self.h = house(); self.h.setUp()
        self.h.authorize()
        self.h.state["wake_policy"] = {}

    def __getattr__(self, name):
        # Fixture verbs (trial, endorse, notice, sync, enact, reject, event) and its clock and state.
        if name in {"trial", "endorse", "notice", "sync", "enact", "reject", "event", "state"}:
            return getattr(self.h, name)
        raise AttributeError(name)

    @property
    def now(self):
        return self.h.now

    @now.setter
    def now(self, value):
        self.h.now = value

    def install(self):
        self.state.setdefault("maintenance", {}).setdefault("migrations", {})[council.SCOPED_LAPSE] = {
            "at": self.now, "sequence": self.state["sequence"]}

    def propose(self, name="rule-one", mode="rule"):
        self.event("council-propose", {"proposal": name, "mode": mode, "title": name,
                   "text": "Text of " + name, "reason": "A witnessed improvement",
                   "base": self.state["rule_revision"]})

    def ready(self, name="rule-one", mode="rule"):
        self.propose(name, mode)
        self.trial(name)
        self.endorse(name, "bob")
        self.endorse(name, "carol")
        self.notice(name)

    def later(self, seconds=DAY):
        self.now += seconds
        self.sync()

    def view(self):
        people = {name: {} for name in self.state["residents"]}
        return {item["id"]: item for item in body.voting_view(self.state, people, {})["proposals"]}

    def test_before_the_upgrade_any_enactment_closes_every_other_proposal(self):
        self.ready("rule-one")
        self.ready("wake-one", "wake-prompt")
        self.later()
        self.enact("rule-one")
        self.reject("council-enact", {"proposal": "wake-one"}, "stale rule revision")
        self.assertEqual("", council.lapsed(self.state, "wake-one", self.state["proposals"]["wake-one"]))
        self.assertTrue(self.view()["wake-one"]["stale"])

    def test_an_enactment_closes_only_proposals_of_its_own_kind(self):
        self.install()
        self.now += 1
        self.ready("rule-one")
        self.ready("rule-two")
        self.ready("wake-one", "wake-prompt")
        self.propose("wake-two", "wake-prompt")
        self.later()
        self.enact("rule-one")
        self.reject("council-enact", {"proposal": "rule-two"}, "proposal lapsed: rule-one changed the same thing")
        self.assertIsNone(council.lapsed(self.state, "wake-one", self.state["proposals"]["wake-one"]))
        # A proposal that survived keeps collecting what it needs, then is enacted on its old base.
        self.trial("wake-two")
        self.endorse("wake-two", "bob")
        self.enact("wake-one")
        self.assertEqual("wake-prompt", self.state["council"]["rules"]["wake-one"]["mode"])
        self.reject("council-endorse", {"proposal": "wake-two", "evidence": "Checked again"},
                    "proposal lapsed: wake-one changed the same thing", actor="carol")
        view = self.view()
        self.assertEqual({"how": "overtaken", "by": "rule-one"}, view["rule-two"]["closure"])
        self.assertEqual({"how": "overtaken", "by": "wake-one"}, view["wake-two"]["closure"])
        self.assertNotIn("closure", view["wake-one"])
        self.assertFalse(view["wake-one"]["stale"])
        # New proposals are still made against the current revision.
        self.reject("council-propose", {"proposal": "rule-three", "mode": "rule", "title": "t", "text": "x",
                                        "reason": "r", "base": "0" * 64}, "stale rule revision")

    def test_proposals_already_lapsed_stay_closed_unless_the_steward_restored_them(self):
        self.ready("rule-one")
        self.ready("wake-one", "wake-prompt")
        self.ready("wake-brief-001", "wake-prompt")
        self.ready("wake-brief-002", "wake-prompt")
        self.later()
        self.enact("rule-one")
        self.now += 60
        self.install()
        with patch.object(council, "RESTORED", frozenset({"wake-brief-002"})):
            self.reject("council-enact", {"proposal": "wake-one"}, "stale rule revision")
            view = self.view()
            self.assertEqual({"how": "lapsed", "by": None}, view["wake-one"]["closure"])
            self.assertEqual({"how": "replaced", "by": "wake-brief-002"}, view["wake-brief-001"]["closure"])
            self.assertFalse(view["wake-brief-002"]["stale"])
            self.later(60)
            self.enact("wake-brief-002")
        self.assertEqual("active", self.state["council"]["rules"]["wake-brief-002"]["status"])
        self.assertEqual(frozenset({"wake-brief-build-004"}), council.RESTORED)

    def test_a_renovation_closes_only_renovations_of_the_same_files(self):
        def renovation(*files):
            return {"mode": "renovation", "status": "pending", "base": "old", "proposed_at": 100,
                    "renovation": {"files": {name: "0" * 64 for name in files}}}
        state = {"rule_revision": "new", "maintenance": {"migrations": {council.SCOPED_LAPSE: {"at": 50}}},
                 "proposals": {}, "council": {"decisions": {}, "rules": {"done": {
                     "mode": "renovation", "status": "installed", "enacted_at": 200,
                     "renovation": {"files": {"house/publish.py": "1" * 64, "house/checkpoint.py": "1" * 64}}}}}}
        self.assertEqual("done", council.lapsed(state, "same", renovation("house/publish.py", "house/body.py")))
        self.assertIsNone(council.lapsed(state, "other", renovation("house/body.py")))
        self.assertIsNone(council.lapsed(state, "rule", {"mode": "rule", "base": "old", "proposed_at": 100}))
        self.assertEqual({"how": "delivered", "by": "done"},
                         body._closure(state, "same", renovation("house/publish.py"), "done"))
        earlier = renovation("house/publish.py") | {"proposed_at": 300}
        self.assertIsNone(council.lapsed(state, "after", earlier), "only later changes close a proposal")
        state["council"]["decisions"]["1"] = {"target": "founding-charter", "outcome": "repealed", "recorded_at": 400}
        self.assertEqual("founding-charter",
                         council.lapsed(state, "rule", {"mode": "rule", "base": "old", "proposed_at": 100}))
        self.assertIsNone(council.lapsed(state, "other", renovation("house/body.py")))


if __name__ == "__main__":
    unittest.main()
