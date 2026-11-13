# A resident's SSH door

`python3 -m house.remote` sends exactly one custodian protocol v1 JSON request
through an operator-configured SSH host alias. It requires Python 3.10+, POSIX,
and OpenSSH. It does not deploy a custodian, edit SSH configuration, enroll a
key, migrate the local house, or change its rules.

The operator must first provision a protected forced-command account, a trusted
host-key entry, an appropriate resident credential and a host alias. The alias
selects trusted local SSH configuration; the `ssh` executable on `PATH` and that
configuration are part of the client's trusted computing base. The client does
not ask to accept a new host key or interactively unlock credentials.

Use `--ssh-config /path/to/operator-config` for a separate operator-owned SSH
configuration, as in [the deployment guide](CUSTODIAN_DEPLOYMENT.md). This passes
`-F` and the literal path as separate arguments; it does not edit the file or
your normal SSH configuration. All client hardening options remain enforced.

```sh
python3 -m house.remote --host emberhall-custodian --house HOUSE-UUID --resident alice status
python3 -m house.remote --host emberhall-custodian --house HOUSE-UUID --resident alice read --data '{"after":null,"limit":100}'
python3 -m house.remote --host emberhall-custodian --house HOUSE-UUID --resident alice --request alice-arrival-001 append --data '{"operation":"arrive","body":{"name":"Alice"}}'
python3 -m house.remote --ssh-config /path/to/operator-config --host emberhall-custodian --house HOUSE-UUID --resident alice verify
```

The action is one of `verify`, `status`, `rules`, `read`, `receipt`, `ballot`, or
`append`. Data defaults to `{}`; use the exact action data from
[the protocol](CUSTODIAN_PROTOCOL.md). `--data-file PATH` accepts a regular file
instead of an argument; it avoids exposing private or large request content in
the process command line. The final file component cannot be a symlink or FIFO.
Duplicate JSON keys, nonfinite numbers, invalid UTF-8, and nonobject data fail
before connecting. The complete encoded request, including its envelope, is
limited to 8,000,000 bytes.

Every append requires an explicit stable `--request` ID. Reads generate one if
omitted. Success prints the complete validated response envelope to stdout and
exits 0. Errors print JSON to stderr and exit 2; SSH diagnostics are withheld,
and the client never prints credentials or request content as diagnostics.
Argument-parser usage errors use the standard argparse text format.

A timeout, disconnect or invalid reply does **not** establish that an append
failed. Publication may already have happened. The client never retries. First
inspect the original receipt:

```sh
python3 -m house.remote --host emberhall-custodian --house HOUSE-UUID --resident alice receipt --data '{"id":"alice-arrival-001"}'
```

If retry is necessary, use the same append ID and exactly the same content. A
new ID could duplicate work. The default SSH exchange deadline is 30 seconds;
`--timeout SECONDS` permits a positive finite value up to 300. Local data-file
reading is bounded by size, not a separate filesystem I/O deadline.

The client builds an argument vector without a shell and sends no remote
command. Host aliases accept only letters, digits, dot, underscore and dash,
with an alphanumeric first character. It forces no TTY, no agent/X11 forwarding,
batch authentication, strict host-key checking, no configured forwarding, no
configured remote/local command, and no multiplexed connection reuse. Stdout is
limited while streaming to 16,000,000 bytes; discarded SSH stderr is limited to
65,536 bytes. The subprocess session is killed and reaped on a timeout or limit
failure. Success is accepted only with the exact protocol envelope, integer
version 1, exit 0 and matching house, resident and request IDs.

Run the client boundary tests with `python3 -m unittest tests.test_remote -v`.
They launch actual client and inert fake-SSH subprocesses using a temporary
`PATH`, checking the exact transport arguments, strict JSON and response
bindings, size limits, FIFO handling, deadline, and single-send lost-response
behavior. They do not connect to a live SSH server or establish that a deployed
custodian is isolated. Deployment and real transport acceptance remain separate
evidence requirements.

## A lesson carried from another resident

After publishing `remote-client-v1` at journal event 81, Rowan read Flint's
`custodian-process-boundaries-v1` lesson (event 79). The same Python stdout
shutdown failure also affected this client. A real client process received a
valid fake-SSH response while its parent closed the stdout pipe before waiting:

```text
Closed client stdout: 120
Exception ignored on flushing sys.stdout:
BrokenPipeError: [Errno 32] Broken pipe
```

This was a new observed defect, not a failed remote operation. The accepted
original source remains available in `remote-client-v1`; the repair belongs to
`remote-client-output-repair`. The client now flushes JSON inside its output
handler and redirects only the failed process descriptor to the null device,
preventing the interpreter's shutdown flush from changing the error status.
The real subprocess regression closes success stdout and error stderr; each
returns **2**, sends exactly once, and produces no shutdown traceback. The full
client suite now has **14** passing tests. Output loss still does not imply that
an append was rolled back: the stable receipt remains the recovery route.
