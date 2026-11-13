import unittest

from house.council import OWNER_ID
from house.inbox import requests


class InboxTests(unittest.TestCase):
    def item(self, body, owner=OWNER_ID):
        return {"id": 10, "user": {"id": owner}, "body": body,
                "html_url": "https://github.com/Someblueman/longhouse/issues/2#issuecomment-10"}

    def test_only_authenticated_owner_and_no_generated_notice_feedback(self):
        comments = [self.item("wake for useful work"), self.item("wake", 99),
                    self.item("<!-- emberhall-notice something -->\nWAKE"), self.item("VETO rule-1")]
        found = requests([], comments)
        self.assertEqual(len(found), 1)
        self.assertIn("wake for useful work", found[0]["reason"])

    def test_edits_wake_again_but_repeated_poll_is_same_request(self):
        original = requests([], [self.item("First request")])[0]
        self.assertEqual(original, requests([], [self.item("First request")])[0])
        self.assertNotEqual(original["request"], requests([], [self.item("Revised request")])[0]["request"])

    def test_new_owner_issues_work_but_pull_requests_and_control_body_are_excluded(self):
        issue = self.item("Please continue") | {"number": 2, "title": "Wake the house"}
        self.assertEqual(len(requests([issue], [])), 1)
        self.assertEqual(requests([issue | {"pull_request": {"url": "pr"}}], []), [])
        self.assertEqual(requests([issue | {"number": 1}], []), [])

    def test_wren_empty_issue_body_does_not_poison_other_wake_requests(self):
        empty = self.item(None) | {"number": 2, "title": "Wake, please"}
        found = requests([empty], [self.item("Actual work") | {"id": 11}])
        self.assertEqual(len(found), 2)
        self.assertIn("Wake, please", found[0]["reason"])
