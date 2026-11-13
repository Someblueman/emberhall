# Blackout Kit

An offline inventory for the day you need to know whether your backup still has
the bytes you saved. Python 3.10+ and a POSIX system (macOS or Linux); no packages,
network, account, or house runtime required.

```sh
python3 projects/blackout/blackout.py create /path/to/source /path/to/source.manifest.json
python3 projects/blackout/blackout.py verify /path/to/backup /path/to/source.manifest.json
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

An output I/O failure also returns **2**, including a closed stdout or stderr
pipe. `create` may already have saved a complete manifest before its success
message is lost. Inspect that manifest and use `verify`; do not assume the file
was rolled back or delete it to retry. A repeated `create` still refuses to
overwrite it. Output failures during `verify` do not alter the backup.

Both operations reject symlinks (including directory components of the root),
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
