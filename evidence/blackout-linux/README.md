# Filename boundaries witnessed on Linux

The gap left by the returning Muse reports is closed for **Linux tmpfs**.
Actual `create`, `verify` and `plan` subprocesses reject a real invalid-UTF-8
filename without partial stdout or a new manifest. Two distinct NFC/NFD names
coexist, retain their original spellings and contents, and match separately.
Removing only the synthetic NFD member makes only that exact name missing and
unrecoverable. Input bytes, size, mode and mtime, plus the original manifest
bytes, remain unchanged by the CLI calls.

The complete product suite passed39 tests with zero skips under Python3.13.18
on Linux7.0.12/aarch64. On this macOS host,37 executed tests pass and the two
filesystem-capability probes explicitly skip. Those skips are not Linux evidence.
`test_filenames.py` detects the actual filesystem capability rather than assuming
that an operating-system label determines filename behavior.

`image.json` pins the downloaded official Python image digest. `run.json` retains
the exact create command, resource limits, non-root UID1000, disabled networking,
read-only source/root filesystem, dropped capabilities, no-new-privileges and
tmpfs mount. `linux-tests.txt` records the actual interpreter/kernel/mount and all
39 results. The source hashes were compared before and after execution.

The owned container was removed. Docker was initially stopped; the operator
started it for this bounded check and restored its stopped state afterward.
The downloaded image remains cached. No resident received Docker access or any
permission change. This is not an ext4, all-filesystems, malicious-writer or
personal-backup recovery claim. Production Blackout code needed no repair.
