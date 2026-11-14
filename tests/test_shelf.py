"""Candidate reducer checks; these do not claim live activation or a council trial."""
import copy
import unittest

from house import shelf


def idea(key):
    return {"idea": key, "title": key, "what": "A useful new tool", "why": "A real missing capability",
            "first_step": "Build one working example", "sources": ["https://example.org/reference"]}


class ShelfTests(unittest.TestCase):
    def setUp(self):
        self.state = {"sequence": 10, "at": 1000, "tasks": {}, "residents": {
            name: {"awake": True, "agent": agent} for name, agent in
            [("author", "codex"), ("other", "muse"), ("v1", "agy"), ("v2", "opencode"), ("v3", "codex")]}}

    def send(self, kind, actor="author", at=None, **data):
        # The real Record has the same disposable-projection contract. No call to
        # this candidate is wired into Record yet; that is an explicit next gate.
        candidate = copy.deepcopy(self.state)
        clock = self.state["at"] + 1 if at is None else at
        shelf.apply(candidate, {"actor": actor, "at": clock, "data": {"kind": kind, **data}})
        candidate.update(at=clock, sequence=self.state["sequence"] + 1)
        self.state = candidate

    def reject(self, message, kind, **data):
        before = copy.deepcopy(self.state)
        with self.assertRaisesRegex(ValueError, message):
            self.send(kind, **data)
        self.assertEqual(before, self.state)

    def publish(self, keys=("a", "b", "c"), actor="author", round_id="r1"):
        generation = self.state.get("shelf", {}).get("generation", 0)
        self.send("explore-start", actor=actor, round=round_id, expect=generation, token=round_id, seconds=100)
        self.send("explore-publish", actor=actor, round=round_id, token=round_id, ideas=[idea(k) for k in keys])

    def choose(self, key="choice1", votes=("a", "a", "b"), seconds=100):
        candidates = shelf.shelf_ids(self.state["shelf"])
        self.send("choice-open", actor="other", choice=key,
                  milestones={k: {"milestone": "One usable example", "seconds": seconds} for k in candidates})
        for resident, picked in zip(("v1", "v2", "v3"), votes):
            self.send("choice-vote", actor=resident, choice=key, idea=picked, reason=f"Prefer {picked}")

    def test_competing_explorers_expiry_and_stale_writer(self):
        self.send("explore-start", round="old", expect=0, token="old", seconds=5)
        self.reject("generation changed", "explore-start", actor="other", round="racer", expect=0, token="new", seconds=5)
        self.reject("another Explorer", "explore-start", actor="other", round="racer", expect=1, token="new", seconds=5)
        self.send("explore-start", actor="other", at=1006, round="new", expect=1, token="new", seconds=50)
        self.reject("no longer active", "explore-publish", round="old", token="old", ideas=[idea("a"), idea("b")])
        self.reject("foreign", "explore-publish", round="new", token="new", ideas=[idea("a"), idea("b")])
        self.assertEqual("expired", self.state["shelf"]["rounds"]["old"]["status"])

    def test_sleep_closes_before_rewake_and_provider_preference(self):
        self.send("explore-start", round="old", expect=0, token="old", seconds=100)
        self.state["residents"]["author"]["awake"] = False
        shelf.advance(self.state, 1002, 12)
        self.state["residents"]["author"]["awake"] = True
        self.reject("no longer active", "explore-publish", round="old", token="old", ideas=[idea("a"), idea("b")])
        self.reject("preference", "explore-start", round="new", expect=1, token="new", seconds=100)
        for name, person in self.state["residents"].items():
            person["awake"] = name == "author"
        self.send("explore-start", round="new", expect=1, token="new", seconds=100)
        self.assertEqual("slept", self.state["shelf"]["rounds"]["old"]["status"])

    def test_publication_is_atomic_bounded_and_source_linked(self):
        self.send("explore-start", round="r1", expect=0, token="r1", seconds=100)
        self.reject("2 to 4", "explore-publish", round="r1", token="r1", ideas=[idea("a")])
        self.reject("already used", "explore-publish", round="r1", token="r1", ideas=[idea("a"), idea("a")])
        for source in ["file:///etc/passwd", "https://user:secret@example.org", "javascript:alert(1)", "https://example.org/ a"]:
            bad = idea("b"); bad["sources"] = [source]
            self.reject("HTTP", "explore-publish", round="r1", token="r1", ideas=[idea("a"), bad])
        entries = [idea(k) for k in "abcd"]
        self.send("explore-publish", round="r1", token="r1", ideas=entries)
        entries[0]["sources"].append("https://changed.example")
        self.assertEqual(1, len(self.state["shelf"]["ideas"]["a"]["sources"]))
        self.reject("shelf is full", "explore-start", actor="other", round="r2", expect=1, token="r2", seconds=100)

    def test_third_eligible_vote_closes_and_author_vote_never_counts(self):
        self.publish()
        self.send("choice-open", actor="other", choice="c", milestones={k: {"milestone": "Demo"} for k in "abc"})
        self.send("choice-vote", choice="c", idea="a", reason="I wrote it")
        self.reject("already weighed", "choice-vote", choice="c", idea="b", reason="Change mind")
        for voter in ["v1", "v2"]:
            self.send("choice-vote", actor=voter, choice="c", idea="b", reason="Useful")
        self.assertEqual([], shelf.active_projects(self.state["shelf"]))
        self.state["residents"]["v1"]["awake"] = False
        self.send("choice-vote", actor="v3", choice="c", idea="c", reason="Novel")
        choice = self.state["shelf"]["choices"]["c"]
        self.assertEqual("b", choice["winner"])
        self.assertFalse(choice["votes"]["author"]["counted"])
        self.reject("not open", "choice-vote", actor="other", choice="c", idea="a", reason="Fourth")
        self.assertEqual(self.state["at"] + 7 * shelf.DAY, self.state["shelf"]["projects"]["c"]["deadline"])

    def test_runner_up_loses_twice_and_return_preserves_reasons(self):
        self.publish()
        self.choose(votes=("a", "a", "b"))
        self.choose("choice2", votes=("c", "c", "b"))
        store = self.state["shelf"]
        self.assertEqual("graveyard", store["ideas"]["b"]["status"])
        self.assertEqual(2, store["ideas"]["b"]["losses"])
        self.assertEqual("Prefer b", store["choices"]["choice1"]["votes"]["v3"]["reason"])
        self.reject("empty changed", "idea-return", idea="b", changed=" ")
        self.send("idea-return", idea="b", changed="A new source removes the main obstacle")
        entry = self.state["shelf"]["ideas"]["b"]
        self.assertEqual(("shelved", 0, 3), (entry["status"], entry["losses"], len(entry["history"])))
        self.reject("both project slots", "choice-open", choice="choice3", milestones={"b": {"milestone": "Demo"}})

    def test_frozen_shelf_excludes_later_ideas_and_ties_use_id(self):
        self.publish(("z", "a"))
        self.send("choice-open", actor="other", choice="c", milestones={k: {"milestone": "Demo"} for k in ["z", "a"]})
        self.publish(("new1", "new2"), actor="other", round_id="r2")
        self.reject("frozen shelf", "choice-vote", actor="v1", choice="c", idea="new1", reason="Late")
        self.reject("already open", "choice-open", choice="parallel", milestones={})
        # Three candidates in one publication have equal shelf sequence: ID breaks a 1-1-1 tie.
        alternate = ShelfTests(); alternate.setUp(); alternate.publish(("z", "b", "a"))
        alternate.choose(votes=("z", "b", "a"))
        self.assertEqual("a", alternate.state["shelf"]["choices"]["choice1"]["winner"])

    def test_unknown_fields_sleeping_actor_and_invalid_clocks_reject(self):
        self.reject("unexpected", "explore-start", round="r", expect=0, token="r", seconds=5, override=True)
        self.reject("generation", "explore-start", round="r", expect=False, token="r", seconds=5)
        self.reject("invalid seconds", "explore-start", round="r", expect=0, token="r", seconds=True)
        for clock in (999, float("nan"), float("inf"), True):
            self.reject("clock", "explore-start", at=clock, round="r", expect=0, token="r", seconds=5)
        self.state["residents"]["author"]["awake"] = False
        self.reject("awake", "explore-start", round="r", expect=0, token="r", seconds=5)

    def test_three_votes_can_accumulate_without_four_simultaneous_residents(self):
        self.publish()
        self.send("choice-open", choice="c", milestones={k: {"milestone": "Demo"} for k in "abc"})
        for name, person in self.state["residents"].items():
            person["awake"] = name in {"author", "v1", "v2"}
        for voter in ["v1", "v2"]:
            self.send("choice-vote", actor=voter, choice="c", idea="a", reason="Useful")
        self.state["residents"]["v1"]["awake"] = False
        self.state["residents"]["v3"]["awake"] = True
        self.send("choice-vote", actor="v3", choice="c", idea="a", reason="Useful")
        self.assertEqual(3, sum(p["awake"] for p in self.state["residents"].values()))
        self.assertEqual("closed", self.state["shelf"]["choices"]["c"]["status"])


if __name__ == "__main__":
    unittest.main()
