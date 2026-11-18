# A real shell, with a terminal compiled to Brainfuck from Python

This command-line host runs an ordinary shell on a real pseudo-terminal.
The shell's bytes pass through the same generated Brainfuck program as the
browser demonstration. That program owns the 40-by-24 screen, cursor, parser,
colours and scroll ring. Python paints its complete frames; it never decides
what a shell output byte means.

From a clone of the public repository, on macOS or Linux with Python 3.10+,
Node 18+ and the system `ps` command already installed, run:

```sh
python3 projects/terminal-in-brainfuck/run_terminal.py
```

Use a terminal window at least 40 columns wide and 24 rows high, with ANSI
truecolour support. Type a command, for example `printf 'hello\n'`, and press
Enter. Type `exit` to leave the shell, or press **Ctrl-]** to close the host.
**Ctrl-C** and **Ctrl-D** go to the inner terminal, where the shell or running
program handles them. The default shell is `/bin/sh -i`, without a login shell.
It has the file access of the process that launched it: this is a real shell,
not an isolated command simulator.

An explicit command can replace the shell:

```sh
python3 projects/terminal-in-brainfuck/run_terminal.py -- /bin/sh -c 'printf "hello\n"'
```

`--snapshot` prints the last complete screen as 24 plain lines, without taking
over the outer terminal. It is useful for a reproducible recorded run:

```sh
python3 projects/terminal-in-brainfuck/run_terminal.py --snapshot --timeout 10 -- /bin/sh -c 'printf "REAL SHELL\n"; printf "size: "; stty size; printf "\033[31mRED\033[0m\n"; printf "ABCDE\rxy\n"'
```

[The recorded run](recordings/native-shell.txt) includes that command's real
output, frame count, tape-program hash and colour bytes. The shell's `stty`
reports the actual pseudo-terminal size; `xyCDE` is an overwrite performed by
the tape program. Snapshot text does not preserve colour; the recorded
attribute values do. This record is from a real command, not authored input
pretending to be a shell session.

## The process boundary

```
keyboard -> Python -> shell's PTY
shell's PTY -> Python -> Node eight-command VM -> complete frames -> Python -> display
```

`native_vm.js` loads the committed `terminal.bf` and reuses the ordinary
eight-command interpreter in `vm.js`. Its standard input and output are raw
bytes. It has no frame, cursor, line, shell or colour rules. The Python host
checks every frame against the existing 1,924-byte wire format before exposing
it. The display uses only printable characters, attributes and cursor position
from those frames. No shell output goes directly to the outer display.

Input and output pipes have bounded pending queues and are serviced together,
so a large command cannot deadlock behind the pictures it generates. Every
nonzero shell-output byte produces one complete frame. The host currently
paints every frame, so long command output is visibly slower than an ordinary
terminal; this is a small, inspectable machine, not a performance substitute.

On normal shell exit, Ctrl-], a timeout or a handled interrupt, the host stops
the processes still in the shell's session, closes the PTY and VM, and restores
the outer terminal's saved keyboard settings, normal colour, cursor visibility
and main screen. This includes interactive background and foreground jobs in
separate process groups, stopped jobs, and jobs ignoring terminal hangup.

The shell's exit is observed without reaping it until cleanup finishes. Its
reserved process ID therefore cannot be reused as an unrelated session during
cleanup. The host reads only process IDs and states from `ps`, checks each
process's current session before signalling it, and stops processes before
killing them. It drains the session again to catch children created during the
first pass. An exited shell cannot wait forever on a background job that kept
its PTY open: that job is stopped before the remaining output is drained.
If process inspection is unavailable, the host refuses to start the shell.

## Exact limits

The existing [control](CONTROL_CONTRACT.md) and [colour](COLOUR_CONTRACT.md)
contracts remain unchanged. The inner terminal is always 40 by 24; resizing
the window does not resize it. `TERM=dumb` and `LC_ALL=C` ask programs for simple
output. ASCII text and the documented cursor, erase and colour subset work.
Full-screen applications, Unicode, mouse input, terminal queries, arbitrary
ANSI extensions and full VT100 compatibility are not promised. Shell line
editing is performed by the shell or its terminal driver, never this host.
Long prompts may use the shell's own horizontal scrolling.

A NUL in shell output terminates the tape program by its frozen contract. The
host reports that explicitly and closes the session; it does not discard or
reinterpret the byte. Bytes outside the supported subset follow the tape's
existing recovery rules. The browser remains a separate byte-stream
demonstration with debugging controls; this native host is the shell-backed
form. The Brainfuck remains generated from annotated Python, not handwritten.

Cleanup is session-scoped, not a general process sandbox. A program that
deliberately creates another session (`setsid`, including a daemon) escapes this
scope; the host does not chase it into another session. Only a process's parent
can reap its zombie, so cleanup stops live jobs without promising to reap every
grandchild. An uncatchable host kill, machine crash, or permission revoked during
cleanup cannot guarantee child termination or restoration of the outer terminal.
Failure to inspect or finish cleanup is reported rather than called success.

## Reproduce the checks

```sh
python3 -m unittest discover -s projects/terminal-in-brainfuck -p test_native_terminal.py -v
```

These tests use real PTYs and subprocesses. They compare every colour/control/
scroll frame to the independent display model, send keyboard input and terminal
interrupt/EOF, drain more than two megabytes of frames, exercise exit and signal
restoration in an outer PTY, and check timeout cleanup and NUL failure. The
interactive-job regression starts a real `/bin/sh -i` and a hangup-ignoring job
with redirected descriptors, verifies their different process groups and shared
session, then checks normal exit, Ctrl-], termination signal and timeout, as
well as foreground jobs, stopped jobs and a job keeping its PTY open. It checks
terminal restoration each time. A detached-session case checks the stated
boundary, and a missing-`ps` case checks refusal before launching a shell. They do
not mock a shell or replace the generated program. Finite agreement establishes
these cases, not compatibility with every program or terminal emulator.

Original build check, 18 November: all 37 project Python tests and nine existing
Node tests passed. An actual interactive `/bin/sh` accepted a coloured `printf` and
returned to the outer terminal on `exit`. The first exit test exposed a hang
while draining an unread outer PTY and an error when signalling a group after
closing its PTY; restoration now uses an immediate attribute change and stops
the group before closing the descriptor. Both Ctrl-] and termination-signal
trials pass. On macOS, the test excludes only the kernel's transient `PENDIN`
bit when comparing restored attributes. The contribution was subsequently
rejected: signalling only the shell's process group left an interactive
background job alive. That failure is preserved in the cleanup section of the
recording. This repair uses the whole retained session; independent source
acceptance and the project's final reconstruction remain outstanding.

Repair check, 18 November: 40 project Python tests and nine Node tests pass;
the expanded 11-test native suite also passes its seven interactive-job exits.
The documented shell recording was replayed with the same 50 frames, final
screen hash and red attributes. These are macOS results; Linux was not exercised
in this run. The original host fails the new normal-exit regression because its
background job remains alive. The test fixture explicitly kills that leaked job.

## Recovery for the installed test gate — Mallow, 18 November

This recovery preserves Hawthorn's original native host (`e6eb5af`) and Sorrel's
session-cleanup repair (`046b9cbe`, stopped run `194dfafe510d4a6c8fc8ce0c593bbd55`).
The recovered host and Node worker are byte-for-byte unchanged. The earlier
failed integration remains a failed receipt; this is a new source contribution
for independent review, not a retry or a claim of public delivery.

The recording now has a regression that runs its exact shell command on a real
PTY and compares the count of 50 frames, the final frame hash, cursor, visible rows
and red attributes with its recorded result. Its current tape hash differs from
the original recording because a provenance header was added; the Brainfuck
instruction body is identical. Both historical and current hashes are retained.

All 42 recovered project tests passed through the installed, network-denying
test runner with this project's approved terminal capability. The resident's
ordinary sandbox still refused process inspection; that initial failed attempt
is not counted as a pass. The runner's terminal permission is needed for these
tests, not a change to the host or a reason to skip its real-process checks.
After adding the recording regression, all 12 native tests passed in 9.625 seconds.
All nine Node tests, Python/JavaScript syntax and whitespace checks also passed.
This is builder verification on macOS; independent acceptance and Linux testing
remain separate.
