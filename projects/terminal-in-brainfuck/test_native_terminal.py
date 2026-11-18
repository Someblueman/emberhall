"""Real POSIX PTYs, the committed tape, and the actual Node worker."""
import fcntl
import hashlib
import os
from pathlib import Path
import pty
import select
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time
import unittest

import model
from run_terminal import HERE, decode_frame, paint_frame, run_session


class NativeTerminalTests(unittest.TestCase):
    def test_recorded_shell_command_replays_on_the_current_tape(self):
        record = (HERE / "recordings/native-shell.txt").read_text()
        command = record.split("Command passed to /bin/sh -c:\n", 1)[1].split("\n\n", 1)[0]
        fields = dict(line.split(": ", 1) for line in record.splitlines() if ": " in line)
        frames = []
        self.assertEqual(run_session(["/bin/sh", "-c", command], frames.append, timeout=10),
                         int(fields["Exit status"]))
        self.assertEqual(len(frames), int(fields["Complete frames"]))
        self.assertEqual(hashlib.sha256(frames[-1]).hexdigest(), fields["Final frame SHA256"])
        cells, attributes, row, col = decode_frame(frames[-1])
        self.assertEqual((row, col), (4, 0))
        self.assertEqual([cells[i:i + 40].rstrip() for i in range(0, 160, 40)],
                         [b"REAL SHELL", b"size: 24 40", b"RED", b"xyCDE"])
        self.assertEqual(attributes[80:83], bytes([1, 1, 1]))
        current_hash = hashlib.sha256((HERE / "terminal.bf").read_bytes()).hexdigest()
        self.assertIn(f"Recovery tape SHA256: {current_hash}", record)

    def test_real_pty_frames_match_independent_model(self):
        payload = b"\x1b[31mRED\x1b[0m\n" + b"line\n" * 26 + b"ABC\r\x1b[2CY"
        command = "printf '" + "".join(f"\\{byte:03o}" for byte in payload) + "'"
        actual = []
        self.assertEqual(run_session(["/bin/sh", "-c", command], actual.append, timeout=10), 0)
        ref = model.RefTerminal()
        expected = [ref.frame()]
        # POSIX output processing on the real PTY inserts CR before LF.
        for byte in payload.replace(b"\n", b"\r\n"):
            ref.feed(byte)
            expected.append(ref.frame())
        self.assertEqual(len(actual), len(expected))
        for frame, want in zip(actual, expected):
            cells, attrs, row, col = decode_frame(frame)
            self.assertEqual((cells.decode(), row, col, list(attrs)), want)

    def test_keyboard_reaches_program_on_controlling_pty(self):
        reader, writer = os.pipe()
        sent = False
        frames = []
        def see(frame):
            nonlocal sent
            frames.append(frame)
            if not sent and frame[1:6] == b"READY":
                os.write(writer, b"pond\n")
                sent = True
        try:
            code = 'stty -echo; printf READY; read word; printf "\\nGOT:%s\\n" "$word"; exit 7'
            self.assertEqual(run_session(["/bin/sh", "-c", code], see, input_fd=reader, timeout=10), 7)
            self.assertTrue(sent)
            self.assertIn(b"GOT:pond", frames[-1][1:961])
        finally:
            os.close(reader)
            os.close(writer)

    def test_backpressure_drains_every_frame(self):
        frames = []
        code = 'i=0; while [ "$i" -lt 1200 ]; do printf x; i=$((i+1)); done'
        self.assertEqual(run_session(["/bin/sh", "-c", code], frames.append, timeout=15), 0)
        self.assertEqual(len(frames), 1201)
        cells, _, row, col = decode_frame(frames[-1])
        self.assertEqual((row, col), (23, 0))
        self.assertEqual(cells[:920], b"x" * 920)
        self.assertEqual(cells[920:], b" " * 40)

    def test_keyboard_interrupt_and_eof_reach_the_pty(self):
        cases = [
            (b"\x03", "trap 'printf INT; exit 0' INT; printf WAIT; while :; do sleep 1; done", b"INT"),
            (b"\x04", "printf WAIT; read word || printf EOF", b"EOF"),
        ]
        for key, code, expected in cases:
            reader, writer = os.pipe()
            frames = []
            sent = False
            def see(frame):
                nonlocal sent
                frames.append(frame)
                if not sent and b"WAIT" in frame[1:961]:
                    os.write(writer, key)
                    sent = True
            try:
                self.assertEqual(run_session(["/bin/sh", "-c", code], see, input_fd=reader, timeout=5), 0)
                self.assertIn(expected, frames[-1][1:961])
            finally:
                os.close(reader)
                os.close(writer)

    def test_nul_is_explicit_failure(self):
        with self.assertRaises(RuntimeError):
            run_session(["/bin/sh", "-c", "printf '\\000'; sleep 5"], lambda _: None, timeout=10)

    def test_timeout_reaps_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pid"
            with self.assertRaises(TimeoutError):
                run_session(["/bin/sh", "-c", f'echo $$ > "{path}"; sleep 100'], lambda _: None, timeout=0.5)
            with self.assertRaises(ProcessLookupError):
                os.kill(int(path.read_text()), 0)

    def test_missing_process_inspection_refuses_to_start_a_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "node").symlink_to(shutil.which("node"))
            marker = root / "started"
            result = subprocess.run(
                [sys.executable, str(HERE / "run_terminal.py"), "--snapshot", "--", "/bin/sh",
                 "-c", f"echo started > {shlex.quote(str(marker))}"],
                env=dict(os.environ, PATH=directory), input=b"", capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"Cannot inspect processes for terminal cleanup", result.stderr)
            self.assertFalse(marker.exists())

    def test_live_exit_and_signal_restore_outer_terminal(self):
        for terminate in (False, True):
            with self.subTest(terminate=terminate):
                master, slave = pty.openpty()
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
                before = termios.tcgetattr(slave)
                proc = subprocess.Popen(
                    [sys.executable, str(HERE / "run_terminal.py"), "--", "/bin/sh", "-c", "sleep 100"],
                    stdin=slave, stdout=slave, stderr=subprocess.PIPE)
                try:
                    output = b""
                    deadline = time.monotonic() + 10
                    while b"\x1b[?25h" not in output and time.monotonic() < deadline:
                        if select.select([master], [], [], 0.1)[0]:
                            output += os.read(master, 65536)
                    self.assertIn(b"\x1b[?1049h", output)
                    self.assertIn(b"\x1b[?25h", output)
                    if terminate:
                        proc.send_signal(signal.SIGTERM)
                    else:
                        os.write(master, b"\x1d")
                    _, errors = proc.communicate(timeout=10)
                    self.assertEqual(proc.returncode, 130, errors)
                    after = termios.tcgetattr(slave)
                    # macOS marks queued input for reprocessing on return to
                    # canonical mode. PENDIN is kernel state, not a mode we set.
                    after[3] &= ~getattr(termios, "PENDIN", 0)
                    before[3] &= ~getattr(termios, "PENDIN", 0)
                    self.assertEqual(after, before)
                finally:
                    if proc.poll() is None:
                        proc.kill()
                    proc.communicate()
                    os.close(master)
                    os.close(slave)

    def test_interactive_job_groups_stop_when_the_host_leaves(self):
        # Job control creates another process group in the shell's session.
        # Ignore HUP and close the job's PTY descriptors: hanging up the PTY
        # or killing just the shell group cannot satisfy this regression.
        for ending in ("exit", "escape", "signal", "timeout", "exit-open", "stopped", "foreground"):
            with self.subTest(ending=ending), tempfile.TemporaryDirectory() as directory:
                shell_path = Path(directory) / "shell"
                job_path = Path(directory) / "job"
                code = ("import os,signal,time; from pathlib import Path; "
                        "signal.signal(signal.SIGHUP, signal.SIG_IGN); "
                        f"Path({str(job_path)!r}).write_text(str(os.getpid())); ")
                if ending == "stopped":
                    code += "os.kill(os.getpid(), signal.SIGSTOP); "
                code += "time.sleep(60)"
                script = Path(directory) / "job.py"
                script.write_text(code)
                redirects = "" if ending == "exit-open" else "</dev/null >/dev/null 2>&1 "
                background = "" if ending == "foreground" else "&"
                command = (f"echo $$ > {shlex.quote(str(shell_path))}; "
                           f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} "
                           f"{redirects}{background}\n")
                master, slave = pty.openpty()
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
                before = termios.tcgetattr(slave)
                args = [sys.executable, str(HERE / "run_terminal.py")]
                if ending == "timeout":
                    args += ["--timeout", "3"]
                proc = subprocess.Popen(args, stdin=slave, stdout=slave, stderr=subprocess.PIPE)
                job_pid = None
                try:
                    output = bytearray()
                    deadline = time.monotonic() + 8
                    while b"\x1b[?25h" not in output and time.monotonic() < deadline:
                        if select.select([master], [], [], 0.05)[0]:
                            output.extend(os.read(master, 65536))
                    self.assertIn(b"\x1b[?25h", output)
                    os.write(master, command.encode())
                    while (not job_path.exists() or not job_path.read_text()) and time.monotonic() < deadline:
                        if select.select([master], [], [], 0.05)[0]:
                            output.extend(os.read(master, 65536))
                    self.assertTrue(job_path.exists(), f"interactive shell did not start its job; "
                                    f"host status: {proc.poll()}")
                    job_pid = int(job_path.read_text())
                    shell_pid = int(shell_path.read_text())
                    self.assertEqual(os.getsid(job_pid), shell_pid)
                    self.assertNotEqual(os.getpgid(job_pid), os.getpgid(shell_pid))
                    if ending in ("exit", "exit-open"):
                        os.write(master, b"exit\n")
                    elif ending in ("escape", "stopped", "foreground"):
                        os.write(master, b"\x1d")
                    elif ending == "signal":
                        proc.send_signal(signal.SIGTERM)
                    # Drain live painting while waiting, rather than filling
                    # the outer PTY and mistaking blocked rendering for cleanup.
                    while proc.poll() is None and time.monotonic() < deadline:
                        if select.select([master], [], [], 0.05)[0]:
                            output.extend(os.read(master, 65536))
                    _, errors = proc.communicate(timeout=2)
                    self.assertEqual(proc.returncode,
                                     {"exit": 0, "exit-open": 0, "timeout": 1}.get(ending, 130), errors)
                    for _ in range(100):
                        state = subprocess.run(["ps", "-p", str(job_pid), "-o", "stat="],
                                               capture_output=True, text=True, timeout=2)
                        if not state.stdout.strip() or state.stdout.lstrip().startswith("Z"):
                            break
                        time.sleep(0.01)
                    else:
                        self.fail(f"{ending}: interactive background job {job_pid} survived")
                    after = termios.tcgetattr(slave)
                    after[3] &= ~getattr(termios, "PENDIN", 0)
                    before[3] &= ~getattr(termios, "PENDIN", 0)
                    self.assertEqual(after, before)
                finally:
                    if proc.poll() is None:
                        proc.kill()
                    proc.communicate()
                    if job_pid is not None:
                        try:
                            os.kill(job_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    os.close(master)
                    os.close(slave)

    def test_detached_session_is_outside_cleanup_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "detached"
            script = Path(directory) / "detach.py"
            script.write_text(
                "import os,signal,time; from pathlib import Path; os.setsid(); "
                "signal.signal(signal.SIGHUP, signal.SIG_IGN); "
                f"Path({str(path)!r}).write_text(str(os.getpid())); time.sleep(60)")
            # Wait for detachment before the original shell exits. No race
            # with the host's permitted session cleanup is intended here.
            command = (f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} "
                       f"</dev/null >/dev/null 2>&1 & while [ ! -s {shlex.quote(str(path))} ]; "
                       "do sleep 0.01; done")
            detached = None
            try:
                self.assertEqual(run_session(["/bin/sh", "-c", command], lambda _: None,
                                             timeout=5), 0)
                detached = int(path.read_text())
                self.assertEqual(os.getsid(detached), detached)
                os.kill(detached, 0)
            finally:
                if detached is None and path.exists():
                    detached = int(path.read_text())
                if detached is not None:
                    try:
                        os.kill(detached, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_renderer_refuses_untrusted_control_bytes(self):
        frame = bytes([255]) + b" " * 960 + bytes([7]) * 960 + bytes([0, 0, 254])
        self.assertIn(b"\x1b[1;1H", paint_frame(frame))
        with self.assertRaises(ValueError):
            paint_frame(frame[:1] + b"\x1b" + frame[2:])
        with self.assertRaises(ValueError):
            decode_frame(frame[:-1])


if __name__ == "__main__":
    unittest.main()
