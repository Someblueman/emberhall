"""Real SSH signatures with disposable keys and authority roots."""
import copy
import subprocess

from house.governance import ballot
from house.record import Record
from tests.support import HouseCase


class GovernanceTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.key = self.root / "disposable-owner"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(self.key)],
                       check=True, capture_output=True)
        self.public = self.key.with_suffix(".pub").read_text()
        self.signed = self.authorized_house("signed")

    def authorized_house(self, name):
        record = Record(self.new_repo(name))
        record.found(name, "Initial rules", self.public)
        record.append("arrive", "alice", {"name": "Alice"})
        self.propose(record)
        return record

    def propose(self, record, proposal="amend", text="Replacement rules"):
        record.append("propose", "alice", {"proposal": proposal, "text": text,
                      "reason": "A precise change", "base": record.read()[0]["rule_revision"]})

    def sign(self, message):
        result = subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(self.key),
                                 "-n", "longhouse-rules-v1"],
                                input=message, capture_output=True, check=True)
        return result.stdout.decode()

    def reject_ratification(self, record, signature, proposal="amend", reason="signature"):
        before = record.read()
        with self.assertRaisesRegex(ValueError, reason):
            record.append("ratify", "alice", {"proposal": proposal, "signature": signature})
        after = record.read()
        self.assertEqual(after[2], before[2])
        self.assertEqual(after[0]["rules"], before[0]["rules"])

    def test_sealed_house_refuses_even_real_signature(self):
        self.propose(self.record)
        signature = self.sign(ballot(self.record.read()[0], "amend"))
        self.reject_ratification(self.record, signature, reason="sealed")

    def test_unsigned_and_foreign_key_fail_but_exact_authority_succeeds(self):
        self.reject_ratification(self.signed, "This is not a signature")
        another = self.root / "wrong-owner"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(another)],
                       check=True, capture_output=True)
        message = ballot(self.signed.read()[0], "amend")
        result = subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(another),
                                 "-n", "longhouse-rules-v1"], input=message,
                                capture_output=True, check=True)
        self.reject_ratification(self.signed, result.stdout.decode())
        self.signed.append("ratify", "alice", {
            "proposal": "amend", "signature": self.sign(message)})
        self.assertEqual(self.signed.read()[0]["rules"], "Replacement rules")

    def test_signature_binds_text_proposal_house_and_base(self):
        state = self.signed.read()[0]
        for field in ("text", "base", "house", "proposal"):
            with self.subTest(field=field):
                altered = copy.deepcopy(state)
                proposal = "amend"
                if field == "house":
                    altered["house_id"] = "another-house"
                elif field == "proposal":
                    altered["proposals"]["other"] = altered["proposals"].pop("amend")
                    proposal = "other"
                else:
                    altered["proposals"][proposal][field] = "tampered value"
                self.reject_ratification(self.signed, self.sign(ballot(altered, proposal)))
        second = self.authorized_house("second")
        self.reject_ratification(second, self.sign(ballot(state, "amend")))

    def test_signed_stale_proposal_cannot_replace_new_rules(self):
        signature = self.sign(ballot(self.signed.read()[0], "amend"))
        self.propose(self.signed, "newer", "Newer rules")
        self.signed.append("ratify", "alice", {"proposal": "newer", "signature":
                           self.sign(ballot(self.signed.read()[0], "newer"))})
        self.reject_ratification(self.signed, signature, reason="no longer current")

    def test_returning_to_old_rule_text_does_not_revive_old_approval(self):
        original = self.signed.read()[0]
        old_signature = self.sign(ballot(original, "amend"))
        self.propose(self.signed, "away", "Different rules")
        self.signed.append("ratify", "alice", {"proposal": "away", "signature":
                           self.sign(ballot(self.signed.read()[0], "away"))})
        self.propose(self.signed, "back", original["rules"])
        self.signed.append("ratify", "alice", {"proposal": "back", "signature":
                           self.sign(ballot(self.signed.read()[0], "back"))})
        self.assertEqual(self.signed.read()[0]["rules"], original["rules"])
        self.reject_ratification(self.signed, old_signature, reason="no longer current")
