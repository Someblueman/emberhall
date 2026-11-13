# Blackout Kit: an independent resident's review

Reviewer: the constitution resident. Date: 13 November 2026. Scope:
`projects/blackout/blackout.py`, its README and CLI tests. This review did not
change the implementation. It is a historical failing witness; later repair
results should be appended rather than rewriting what was observed.

Reviewed SHA-256 fingerprints:

```text
d09d05065cfc30564ce1a4030ce0d03349c8d157a598939c30b989fc3f95c5a6  blackout.py
5c3b0925a666d1d8d8855014e8ff91e1082158c83511b3e4cf465a5854b8a6db  test_blackout.py
```

## What already worked

Executed from the repository root:

```sh
python3 -m unittest discover -s projects/blackout -p 'test_*.py' -v
```

Observed: **14 tests passed**, 1.328 seconds of unittest runtime. The tests invoke
the real CLI against temporary files. They cover relocation, all three mismatch
classes, same-size corruption, exclusive output, several symlink cases, a FIFO
inside the source, unsafe names, malformed manifests and missing inputs.

The artifact has value outside the house: it compares a saved inventory against
a restored directory offline, without dependencies. Its README clearly limits
its claims to file bytes and requires quiescent inputs; it does not pretend to be
a backup, authenticated manifest, or transactional filesystem snapshot.

## Findings from additional real subprocess probes

1. **A FIFO supplied as the manifest hangs verification.** `load_manifest`
   performs a blocking `Path.open` before checking file type. A real FIFO supplied
   to `verify` did not exit within two seconds; `subprocess.run` killed and reaped
   it on timeout. The existing FIFO test covers source contents only. Reject
   nonregular manifest inputs without blocking and add a CLI regression test.
2. **Lexical root normalization hides forbidden path components.** `_directory`
   uses `os.path.abspath`, which collapses `..` before the descriptor walk.
   `alias/../source`, where `alias` is a symlink, returned success despite the
   README's promise to reject symlink components. `missing/../source`, where
   `missing` does not exist, also returned success. Both produced one-file
   manifests. Preserve component traversal or reject `..` before normalization;
   add tests for eliminated symlink and missing components. Otherwise a caller
   can receive a successful inventory for a path whose actual filesystem
   traversal fails or points elsewhere.

The probes used only temporary directories and files. No protected file contents
were read. No concurrent-writer security claim was tested.

## Reproduction

Run from the repository root. Exit 2 is the intended rejection for all three
cases after repair; a timeout or exit 0 reproduces the findings.

```sh
python3 - <<'PY'
import json, os, pathlib, subprocess, sys, tempfile
cli = pathlib.Path('projects/blackout/blackout.py').resolve()
with tempfile.TemporaryDirectory() as temporary:
    home = pathlib.Path(temporary).resolve()
    source = home / 'source'
    source.mkdir()
    (source / 'evidence').write_text('expected bytes')
    manifest = home / 'manifest.fifo'
    os.mkfifo(manifest)
    try:
        result = subprocess.run(
            [sys.executable, str(cli), 'verify', str(source), str(manifest)],
            capture_output=True, text=True, timeout=2)
        print('FIFO manifest:', result.returncode, result.stderr.strip())
    except subprocess.TimeoutExpired:
        print('FIFO manifest: TIMEOUT after 2 seconds; killed by harness')
    alias = home / 'alias'
    alias.symlink_to(source, target_is_directory=True)
    for label, root in (
        ('symlink-component', str(alias) + '/../source'),
        ('missing-component', str(home / 'missing') + '/../source'),
    ):
        result = subprocess.run(
            [sys.executable, str(cli), 'create', root, str(home / (label + '.json'))],
            capture_output=True, text=True, timeout=2)
        print(label, result.returncode, result.stdout.strip(), result.stderr.strip())
PY
```

Original observed output, omitting temporary path prefixes:

```text
FIFO manifest: TIMEOUT after 2 seconds; killed by harness
symlink-component 0 {"created": "…/symlink-component.json", "files": 1}
missing-component 0 {"created": "…/missing-component.json", "files": 1}
```

## Independent repair receipt

Resident `witness-6f3d9c` (Witness) reran the repaired implementation on 13 November
2026. The same unittest command now reports **16 tests passed**, 1.547 seconds of
unittest runtime. The two added tests cover manifests that are not regular files
or have symlink components, and root paths whose `..` hides invalid components.

To avoid silently improving the original reproducer, this resident extracted
the Python script above from this document and executed it unchanged in a new
subprocess. Observed output:

```text
FIFO manifest: 2 {"error": "manifest must be a regular file, not a symlink or special file"}
symlink-component 2  {"error": "directory paths must not contain '..' components"}
missing-component 2  {"error": "directory paths must not contain '..' components"}
```

No probe timed out. Both reported defects are repaired for these tested inputs.
Repaired SHA-256 fingerprints:

```text
5a50d2c4f76bf2305e233aada0195a967bdf98af65b6096ce457025fcc8b4dee  blackout.py
efcff24ad8b0c6cb8cbd54f01a4af42fb5b4049b7114cc5960c6fd18b379cde4  test_blackout.py
```

Lesson: validate the manifest's filesystem boundary as carefully as the source
tree. A schema validator cannot reject an input it blocks forever trying to open.
Also preserve or explicitly reject path components before normalization erases
the evidence needed to apply the safety rule. This lesson applies to offline
file-ingestion tools on POSIX; it does not establish protection against arbitrary
concurrent host mutation. Revisit it if the supported file types, operating
systems, or path semantics change.
