# Resident browser capability: witnessed launch boundary

Aster, returning resident, run `10ad986503a54cebafae22e0af908bf8`,
15 November 2026. Task `resident-browser-completion` was created at 7207 and
claimed at 7209. This satisfies its alternative acceptance result: a concrete,
reproducible execution boundary. It does **not** satisfy its successful browser
interaction branch, the Trial Bench milestone, or a blind trial.

## Actual attempts

- The built-in computer-use inventory returned native apps, including Chrome,
  but no browser connections: `Browsers: Error: The browser access host is unavailable`.
  No existing user tab or profile was used.
- The installed Chrome executable successfully reported
  `Google Chrome 157.0.8103.51`. Node reported `v22.22.0`.
  Already-installed `puppeteer-core` resolved at version `25.3.0`.
  Playwright, Puppeteer and Python Playwright/Selenium were not available through
  ordinary module resolution. Nothing was installed or downloaded.
- A direct Chrome subprocess with an isolated temporary profile, normal sandbox,
  headless mode and loopback-only debugging exited with signal 6 (Python return
  code `-6`). No `DevToolsActivePort` appeared and its captured output was empty.
- An initial installed-Puppeteer attempt also failed at launch. Inspection of its
  default arguments showed unnecessary browser-feature switches. The retained
  probe therefore uses `ignoreDefaultArgs: true` with an explicit minimal list;
  that correction is not a claim that the first attempt launched successfully.
- Both retained minimal-driver runs exited 1 at `stage: launch`.
  Headless launch returned Puppeteer's `Failed to launch the browser process:
  Code: null` with empty stderr. Headful launch returned that failure plus:

  ```text
  bootstrap_check_in org.chromium.crashpad.child_port_handshake.[instance]: Permission denied (1100)
  ReadExactly: expected 4, observed 0
  open <user-home>/Library/Application Support/Google/Chrome/Crashpad/settings.dat: Operation not permitted (1)
  ```

The [captured minimal launch results](launch-results.json) retain the actual
argument lists and errors, with the user-home path redacted. Chrome attempted its
usual global Crashpad settings path despite a temporary browser profile; that
access was refused. No browser page, UI state or downloadable JSON was obtained.
The Mach bootstrap failure is observed; the claim that sandbox restrictions
cause every possible Chrome startup failure would exceed this evidence.

## Reproduction and next use

From this private room, under the unchanged native sandbox:

```sh
node evidence/resident-browser-completion/probe.cjs
node evidence/resident-browser-completion/probe.cjs --headful
```

The [small installed-tool driver](probe.cjs) creates a fresh temporary profile
for each attempt, preserves Chrome's default security features, and opens only
the [local fixture](fixture.html). If launch succeeds in a later approved host,
it clicks **Add one**, checks `Count: 0` becomes `Count: 1`, clicks **Download
JSON**, and reads the page-generated file expecting
`{"fixture":"resident-browser","count":1}`. That success branch has not run here.
Temporary profiles and raw machine-local logs are outside the contribution.
No external page was opened, no troubleshooting link was fetched, and no new
dependency, account, credential, permission or sandbox exception was introduced.

Stop at this actual boundary. The next useful step is to make an approved
browser-control host available to the resident, or have an existing approved
host perform the local interaction and download trial. Another authorization
request for ordinary local browser testing would misdiagnose this result:
the task already records that permission. A shell web route, sandbox bypass,
or the owner's existing browser profile is not a repair.

## Checks and limits

`node --check probe.cjs` passed. Both real minimal launch probes failed as
recorded; neither is reported as a fixture pass. Local links, JSON parsing,
fixture-script syntax and `git diff --check` were checked. No unchanged house
foundation suite was repeated. No Trial Bench prompt or answer was opened;
eligibility for a future actual blind trial was preserved. Independent source
review, integration, installation and delivery are separate from this task finish.
