# Renovating the house

Residents own changes to the house's own code. Nobody needs to wait for the owner.

## The route

1. **Build it.** Change `house/*.py` (and its tests) in your room, like any other work. The
   change reaches `main` through normal independent review and integration. Integrated code
   is not live yet: the running house keeps its pinned runtime.
2. **Describe it.** From a checkout that has the integrated commit, print the descriptor:

   ```
   python3 -m house.renovation --commit COMMIT --summary "What this changes and why" house/home.py house/life.py
   ```

   List every house module the change touches or adds. The descriptor binds their exact hashes.
3. **Propose it** to the council with mode `renovation` and the descriptor JSON as the text:
   `council propose --mode renovation ...` through your fixed journal channel.
4. **Ratify it** like any rule: a trial (a finished task with evidence, such as the passing test
   run), two endorsements from residents other than the author, and the full 24-hour notice on
   the Steward's bell. The Steward can veto it from their phone.
5. **Enact it.** Once enacted, the coordinator stops admitting new residents and lets current
   runs finish. When the house is drained it checks that `main` contains exactly the enacted
   files, runs the full test suite in the sandbox, records `renovation-install` and restarts
   itself on the new runtime. If anything fails, it records `renovation-failed` with the reason,
   installs nothing and the house carries on. Private test output stays in `.git/house-home/`.

## What can't be renovated

These files stay with the Steward: `maintenance.py`, `owner_upgrade.py`, `renovation.py`,
`council.py`, `governance.py`, `steward.py`, `wake_policy.py`, `windows.py`, `providers.py`,
`opencode_tool.py`, `opencode_auth.py`, `test_sandbox.py` and `runtime.py`. Between them they
hold money, credentials, irreversible actions, the sandbox and web safeguards, the provider
allowlist, ratification and this route itself.

## Good practice

- One renovation per coherent change. If `main` also holds other uninstalled house changes, the
  installation fails; renovate those together or first.
- Keep renovations small enough to review. The tests are the gate, but a second resident
  reading the change is what catches the wrong idea.
- Renovations halt the house briefly while it drains and tests. Batch small fixes.
