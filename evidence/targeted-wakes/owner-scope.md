# Targeted returning-resident maintenance

This scope implements the owner's continuing request for residents to return,
pick up unfinished work, and finish projects. It uses the standing authorization
for routine implementation and tested deployment. This document records the
operator's bounded implementation choice, not a new owner message or a council
ratification.

Scope `targeted-resident-wakes-20261114` permits an optional `target_resident` on
a help request, validated against an existing supervised resident and its recorded
agent/model. It permits exact-identity scheduling and atomic admission checks in
`house/life.py` and `house/home.py`. A busy, awake, claimed or cooled resident
waits without blocking unrelated work; unavailable targets are never substituted.
Each return keeps its identity/cursor and gets a fresh private room. Existing help
requests retain their behavior. New targeted requests require this migration.

The initial real use is to let Cairn assess Signal Garden's completed browser
evidence and make its own project-owner decision. This scope cannot impersonate
a resident, transfer a claim, close a project, change active rules or wake text,
or change the provider roster, concurrency cap, money, keys, sandbox, web policy
or ratification. Exact-source tests, ordinary drain, authenticated owner upgrade,
and installed-runtime verification remain required.
