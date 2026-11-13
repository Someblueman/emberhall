# Blackout Kit

An offline inventory for the day you need to know whether your backup still has
the bytes you saved. Python 3.10+ and a POSIX system (macOS or Linux); no packages,
network, account, or house runtime required.

```sh
python3 projects/blackout/blackout.py create /path/to/source /path/to/source.manifest.json
python3 projects/blackout/blackout.py verify /path/to/backup /path/to/source.manifest.json
python3 projects/blackout/blackout.py plan /path/to/surviving-archive /path/to/source.manifest.json
```

`create` records each regular file's relative path, byte length, and SHA-256. It
stores a complete manifest atomically, refuses to overwrite an existing one,
and requires the manifest to be outside the source directory. Keep this manifest
on another device along with your backup. Protect its authenticity separately:
checksums detect corruption, but a person who can replace the manifest can also
replace the expected checksums.

`verify` reads every regular file in the backup and prints JSON with `missing`,
`changed`, `extra`, and `matched`. Exit status **0** means all recorded bytes match
and there are no extra files; **1** means a mismatch; **2** means an unsafe source,
malformed manifest, or I/O error prevented verification. A failure never repairs,
deletes, or alters your files.

`plan` reads a surviving archive and the same trusted manifest, then prints a
read-only recovery plan: the same `missing`, `changed`, `extra`, and `matched`
classifications as `verify`, plus `restores`, `ambiguous`, and `unrecoverable`.
Each `restores` entry has `target`, `status` (`missing` or `changed`),
`candidates`, `recoverable`, and `ambiguous`. A candidate is any surviving
regular file whose size and SHA-256 are byte-identical to the expected entry
for that target, including an `extra` file that looks like a rename and a
`matched` file whose bytes are duplicated elsewhere. Exit status follows
`verify`: **0** when nothing is missing, changed, or extra; **1** when the
plan describes a mismatch; **2** when unsafe input, a malformed manifest, or
an I/O error prevented planning. `plan` never copies, renames, overwrites, or
deletes, and it never chooses for you: when more than one surviving file
matches a target, `ambiguous` is true and `candidates` lists every match
sorted by path, so you must make that one-byte-identical choice explicitly.
When no surviving file matches, the target appears in `unrecoverable`.
Candidates are sorted, JSON keys are sorted, and no timestamps or random
values are included, so the same manifest and archive produce byte-identical
`plan` output. If output fails (for example a closed stdout), `plan` exits
**2** and the scanned archive is unchanged; inspect the archive and re-run
`plan` rather than assuming a restore happened.

An output I/O failure also returns **2**, including a closed stdout or stderr
pipe. `create` may already have saved a complete manifest before its success
message is lost. Inspect that manifest and use `verify`; do not assume the file
was rolled back or delete it to retry. A repeated `create` still refuses to
overwrite it. Output failures during `verify` do not alter the backup.

Ctrl-C during scanning, planning or saving returns **130** with
`{"error": "interrupted"}` on stderr when that stream is available. Treat any
stdout from a cancelled operation as incomplete. Scans do not alter their inputs
or publish a partial manifest. `create` may already have published
a complete manifest before cancellation; inspect it and use `verify`. Do not
delete it just to retry: another `create` still refuses to overwrite it.
This covers a handled interrupt, not a forced kill or power-loss durability.

All three operations reject symlinks (including directory components of the root),
devices, sockets, FIFOs, and nonportable names containing colons, backslashes,
control characters, or invalid UTF-8. Manifests reject absolute paths, traversal,
duplicate paths and JSON keys, inconsistent file/directory paths, unknown fields,
unsupported versions, and invalid lengths or digests. Descriptor-relative opens
with `O_NOFOLLOW` keep a raced symlink from redirecting the scanner. Changes
observed while reading a file or enumerating a directory fail closed.
The input manifest must also be a regular file with no symlink components;
opening a FIFO cannot block verification. Root and input-manifest directory paths
must omit `..` components, so normalization cannot conceal a symlink or missing
directory. Use an absolute path or a relative path descending from your current
directory.

Paths match exactly, including letter case and Unicode normalization form. A
restore that changes `Report.txt` to `report.txt`, or changes a name from NFC to
NFD, reports the original as `missing` and the new spelling as `extra`, even if
the filesystem treats both spellings as the same name. Preserve names when
copying between filesystems; distinct source names may collide on the destination.
Investigate these differences against the trusted source before renaming files.
Keep the original manifest: creating a new one from the restore would replace
the baseline you are checking.

Use a **quiescent directory or filesystem snapshot**. This is not a transactional
snapshot of a live filesystem, and it does not guarantee detection of a malicious
concurrent writer. This format preserves file contents only: empty directories,
ownership, permissions, timestamps, extended attributes, and hard-link identity
are outside its scope. It does not copy or restore backups. A successful check
proves a point-in-time byte comparison, not future recoverability.

Run the real CLI tests from the repository root:

```sh
python3 -m unittest discover -s projects/blackout -p 'test_*.py' -v
```
