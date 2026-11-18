"""A real PTY host for a terminal compiled to Brainfuck from Python.

Only the tape program interprets shell output. This host relays keyboard bytes,
validates complete frames, and paints their literal cells in the outer terminal.
Requires a POSIX host, Python 3.10+, and Node; no installed Python packages.
"""
from __future__ import annotations

import argparse
import errno
import fcntl
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import struct
import subprocess
import sys
import termios
import time
import tty

HERE = Path(__file__).resolve().parent
FRAME_SIZE = 1924
ROWS, COLS = 24, 40
PALETTES = (
    ("111820", "cf5966", "62bb87", "d2b75b", "668bd7", "bb76cc", "54bac7", "dce4ed"),
    ("738090", "ff8991", "99efb0", "ffe18a", "9ebdff", "e7a6f5", "8ceaf3", "ffffff"),
)


def decode_frame(data: bytes) -> tuple[bytes, bytes, int, int]:
    if (len(data) != FRAME_SIZE or data[0] != 255 or data[-1] != 254
            or any(c < 32 or c > 126 for c in data[1:961])
            or any(c > 127 for c in data[961:1921])
            or data[1921] >= ROWS or data[1922] >= COLS):
        raise ValueError("Malformed frame from the tape machine")
    return data[1:961], data[961:1921], data[1921], data[1922]


def paint_frame(data: bytes) -> bytes:
    cells, attributes, row, col = decode_frame(data)
    out = bytearray(b"\x1b[?25l")
    last = None
    for r in range(ROWS):
        out.extend(f"\x1b[{r + 1};1H".encode())
        for i in range(r * COLS, (r + 1) * COLS):
            attribute = attributes[i]
            if attribute != last:
                fg = PALETTES[attribute >> 6][attribute & 7]
                bg = PALETTES[0][(attribute >> 3) & 7]
                out.extend(f"\x1b[38;2;{rgb(fg)};48;2;{rgb(bg)}m".encode())
                last = attribute
            out.append(cells[i])
    out.extend(f"\x1b[{row + 1};{col + 1}H\x1b[?25h".encode())
    return bytes(out)


def rgb(colour: str) -> str:
    return ";".join(str(int(colour[n:n + 2], 16)) for n in (0, 2, 4))


def session_processes(session: int) -> list[int]:
    """Find live members across job-control groups, without reading commands."""
    try:
        listing = subprocess.run(["ps", "-axo", "pid=,stat="], capture_output=True,
                                 text=True, check=True, timeout=2)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError("Cannot inspect processes for terminal cleanup") from error
    members = []
    for line in listing.stdout.splitlines():
        pid_text, state = line.split()
        if state.startswith("Z"):
            continue  # Only the process's parent can reap a zombie.
        pid = int(pid_text)
        try:
            if os.getsid(pid) == session:
                members.append(pid)
        except ProcessLookupError:
            pass  # Exited between the snapshot and the session check.
    return members


def stop_session(session: int) -> None:
    """Stop the PTY session while its leader PID is still reserved by waitid."""
    deadline = time.monotonic() + 3
    while members := session_processes(session):
        # Freeze before killing so ordinary children cannot keep forking while
        # we drain the session. Recheck membership before every signal.
        for sig in (signal.SIGSTOP, signal.SIGKILL):
            for pid in members:
                try:
                    if os.getsid(pid) == session:
                        os.kill(pid, sig)
                except ProcessLookupError:
                    pass
        if time.monotonic() >= deadline:
            raise RuntimeError("Terminal session processes did not stop")
        time.sleep(0.01)


def run_session(command: list[str], on_frame, *, input_fd: int | None = None,
                timeout: float | None = None) -> int:
    """Run a controlling PTY and a separate generic VM with bounded queues.

    on_frame gets only validated, complete frames. Ctrl-] on input_fd leaves the
    host; other bytes, including Ctrl-C and Ctrl-D, go unchanged to the PTY.
    """
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node is required; install it before running this host")
    # Refuse to launch if the host cannot inspect its eventual cleanup scope.
    session_processes(os.getsid(0))
    worker = subprocess.Popen([node, str(HERE / "native_vm.js")],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert worker.stdin is not None and worker.stdout is not None
    pid = None
    master = None
    exited = None
    stopped = False
    try:
        pid, master = pty.fork()
        if pid == 0:
            try:
                fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
                os.environ.update(TERM="dumb", LC_ALL="C", COLUMNS=str(COLS), LINES=str(ROWS))
                os.execvp(command[0], command)
            except OSError as error:
                os.write(2, f"Cannot start {command[0]}: {error}\r\n".encode())
                os._exit(127)
        for fd in (master, worker.stdin.fileno(), worker.stdout.fileno()):
            os.set_blocking(fd, False)
        to_vm, to_shell, frames = bytearray(), bytearray(), bytearray()
        master_open = True
        worker_open = True
        started = time.monotonic()
        while worker_open:
            if timeout is not None and time.monotonic() - started > timeout:
                raise TimeoutError("Native terminal session timed out")
            if exited is None:
                exited = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
                if exited is not None:
                    # A background job can hold the PTY open after its shell
                    # exits. Stop it now, then drain already written output.
                    stop_session(pid)
                    stopped = True
            if not master_open and not to_vm and not worker.stdin.closed:
                worker.stdin.close()
            readers = [worker.stdout.fileno()]
            if master_open and len(to_vm) < 65536:
                readers.append(master)
            if input_fd is not None and master_open and len(to_shell) < 65536:
                readers.append(input_fd)
            writers = []
            if to_vm and not worker.stdin.closed:
                writers.append(worker.stdin.fileno())
            if to_shell and master_open:
                writers.append(master)
            readable, writable, _ = select.select(readers, writers, [], 0.05)
            for fd in writable:
                queue = to_shell if fd == master else to_vm
                try:
                    count = os.write(fd, queue[:4096])
                except BlockingIOError:
                    continue
                except OSError as error:
                    if fd == master and error.errno == errno.EIO:
                        master_open = False
                        to_shell.clear()
                        continue
                    raise
                del queue[:count]
            for fd in readable:
                try:
                    data = os.read(fd, 16384 if fd == worker.stdout.fileno() else 4096)
                except BlockingIOError:
                    continue
                except OSError as error:
                    if fd == master and error.errno == errno.EIO:
                        data = b""
                    else:
                        raise
                if fd == worker.stdout.fileno():
                    if not data:
                        worker_open = False
                        continue
                    frames.extend(data)
                    while len(frames) >= FRAME_SIZE:
                        frame = bytes(frames[:FRAME_SIZE])
                        del frames[:FRAME_SIZE]
                        decode_frame(frame)
                        on_frame(frame)
                elif fd == master:
                    if data:
                        to_vm.extend(data)
                    else:
                        master_open = False
                        to_shell.clear()
                elif not data:
                    # Pipe EOF is a keyboard EOF, not EOF on the shell's output.
                    to_shell.extend(b"\x04")
                    input_fd = None
                elif b"\x1d" in data:
                    return 130
                else:
                    to_shell.extend(data)
            if worker.poll() is not None and worker.returncode:
                raise RuntimeError(f"Tape machine exited with status {worker.returncode}")
        if frames:
            raise ValueError("Tape machine ended with a partial frame")
        if worker.wait(timeout=2):
            raise RuntimeError("Tape machine failed")
        if exited is None:
            exited = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOWAIT)
        return exited.si_status if exited.si_code == os.CLD_EXITED else -exited.si_status
    finally:
        try:
            if pid and not stopped:
                stop_session(pid)
        finally:
            if master is not None:
                os.close(master)
            if pid:
                # Also bound failure cleanup if process inspection itself
                # becomes unavailable after launch. Preserve that error.
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                # Cleanup precedes reaping: the session leader PID cannot be
                # reused by an unrelated session during membership checks.
                os.waitpid(pid, 0)
            if worker.poll() is None:
                worker.kill()
            worker.wait()
            worker.stdin.close()
            worker.stdout.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true", help="print final plain screen instead of live painting")
    parser.add_argument("--timeout", type=float, help="stop after this many seconds")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command after -- (default: /bin/sh -i)")
    args = parser.parse_args(argv)
    command = args.command or ["/bin/sh", "-i"]
    if command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command must follow --")
    if args.timeout is not None and args.timeout <= 0:
        parser.error("timeout must be positive")
    if not args.snapshot:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            parser.error("live mode needs a terminal; use --snapshot for a recorded run")
        size = shutil.get_terminal_size()
        if size.columns < COLS or size.lines < ROWS:
            parser.error("live mode needs at least 40 columns and 24 rows")
    latest = None
    def show(frame):
        nonlocal latest
        latest = frame
        if not args.snapshot:
            sys.stdout.buffer.write(paint_frame(frame))
            sys.stdout.buffer.flush()
    saved = None
    previous_term = signal.getsignal(signal.SIGTERM)
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupted)
    try:
        if not args.snapshot:
            print("Terminal compiled to Brainfuck from Python. Ctrl-] exits.", file=sys.stderr)
            saved = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin)
            sys.stdout.buffer.write(b"\x1b[?1049h\x1b[?7l\x1b[2J")
            sys.stdout.buffer.flush()
        result = run_session(command, show, input_fd=sys.stdin.fileno(), timeout=args.timeout)
        if args.snapshot and latest is not None:
            cells, _, _, _ = decode_frame(latest)
            print("\n".join(cells[i:i + COLS].decode("ascii").rstrip() for i in range(0, 960, COLS)))
        return result if result >= 0 else 128 - result
    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
        print(f"Native terminal: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        if saved is not None:
            try:
                sys.stdout.buffer.write(b"\x1b[0m\x1b[?25h\x1b[?7h\x1b[?1049l")
                sys.stdout.buffer.flush()
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSANOW, saved)
        signal.signal(signal.SIGTERM, previous_term)


if __name__ == "__main__":
    raise SystemExit(main())
