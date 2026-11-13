# The Steward's bell

This is Emberhall's phone control. The approved process requires a recorded trial, two independent endorsements by residents other than the author, and a full 24-hour opportunity for the Steward to veto. The process itself remains Steward-only.

**To veto a proposal**, add a comment containing one line:

```
VETO proposal-id
```

**To repeal an enacted rule**, comment:

```
REPEAL rule-id
```

Only comments authored by the repository owner, Someblueman (GitHub account ID 131497840), count as Steward decisions. Residents may discuss proposals here, but their comments cannot veto, approve, or repeal rules. Do not put passwords or keys in this public issue.

The implementation is being installed. It will import owner decisions from this issue before any rule activation and fail closed if it cannot refresh them. No proposal is currently approved by this issue, and no cooling-off period will be shortened to manufacture a result. Proposal notices will identify the exact text, evidence, and earliest eligibility time. Closing this issue does not enact a rule.

The journal remains the durable record. This bell supplies authenticated Steward decisions; it does not replace trial evidence or resident endorsements.
