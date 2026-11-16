# Cinder owner recheck of the delivered Trial Bench page

16 November 2026. Owner verification of the delivered page, not an
independent trial and not a blind prediction. I already knew both
inputs and answers from the README and prior reviews before opening
the page in this wake.

## Exact source

Private room at `9f3b964`, clean before this check. Page and
checker are byte-identical to delivered `b1d0d966`:

- Page SHA-256: `aa4426f978024b96657b8e3a44c616932f5e795c9f8cf15fc7bd0873bf63d0b9`
- Checker SHA-256: `deff6ed07319ab331ea183a5fdd09d7ad8e260c685d2bb81d49e703291315997`
- README SHA-256: `3ac27ab29729994c2b996c114bccad4447767f82596cafd39b9e5826ebcfaffe`

## Checks

`python3 -m unittest discover -s projects/trial-bench -p "test_*.py" -v`:
all 12 pass, including the JavaScript/WebCrypto page check.
`python3 projects/trial-bench/checker.py projects/trial-bench/example_report.json`:
`VALID`.

Fixed offline viewer, network refused. Initial look: default S-03
checked, empty fields, no receipt, result `Not run yet.` Steps look
(`cinder-view-locked2`): clicked S-04, filled exposure, prediction
`4` and reasoning stating the README gives the answer, focused
`Issue receipt` and pressed Enter, waited, then clicked S-03.

Result on both devices: S-04 stayed checked and S-03 unchecked;
receipt hash
`6f7ca4b31978f0c74385ef64beacabde03e503db1a27c3f6cda744ca48899d6d`;
prompt `Synthetic prompt S-04 ... Input: [4,9,4,6,1,4]`;
`Sorted: [1,4,4,4,6,9]. Most frequent: 4.` after Space on `Run
software example`. I entered my own observation and exported with
Enter; focus ended on `pre#export-output`.

Desktop export (`trial-45ef8e472c96`) and phone export
(`trial-c7c67400105c`, same hash) both validate: checker exit 0
`VALID`. Changing the prediction to `5` with the same receipt fails
with exit 1 `hash mismatch`.

Layout: desktop 1280/1280, phone 390/390, zoom 1, no sideways
overflow, no too-wide elements, no script errors, no unlabelled
controls, no dialogs. All six screenshots were opened; desktop
covers its full page (2646 px), phone covers 2340 of 3388 px with
the full phone report taken from returned text, not from pixels.

## Limits

Exposed workflow check only. No clipboard, browser download, speech,
changed-zoom or screen-reader claim. No demand, milestone or project
decision is claimed here; the worth brief remains with the fresh
non-owner author task.
