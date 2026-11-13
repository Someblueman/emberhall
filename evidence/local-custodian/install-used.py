"""Prepare a same-account, loopback-only macOS custodian; enroll transport keys.

This is local operator administration, not part of the resident wire protocol.
It does not change journal authority, copy the journal, or load a launch agent.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import pwd
import re
import shlex
import subprocess
import sys
import tempfile

LABEL = "local.emberhall.custodian"
DEFAULT_ROOT = Path.home() / ".local/state/emberhall-custodian"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()


def write(path: Path, text: str, mode: int = 0o600) -> None:
    with path.open("x") as stream:
        stream.write(text)
    path.chmod(mode)


def replace(path: Path, text: str) -> None:
    fd, name = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def safe_path(path: Path) -> Path:
    path = path.expanduser().resolve()
    # OpenSSH's config/authorized_keys syntax is not a shell argument vector.
    if not re.fullmatch(r"/[A-Za-z0-9_./-]+", str(path)):
        raise ValueError("installation and repository paths must use ASCII letters, digits, /._-")
    return path


def prepare(source: Path, root: Path, port: int) -> dict:
    if sys.platform != "darwin":
        raise ValueError("this launch-agent recipe requires macOS")
    source, root = safe_path(source), safe_path(root)
    if not 1024 <= port <= 65535:
        raise ValueError("port must be 1024..65535")
    account = pwd.getpwuid(os.getuid()).pw_name
    if not re.fullmatch(r"[A-Za-z0-9_-]+", account):
        raise ValueError("unsupported account name")
    python = safe_path(Path(sys.executable))
    commit = run("git", "-C", str(source), "rev-parse", "HEAD")
    paths = ["custodian_entry.py", *sorted(str(p.relative_to(source))
             for p in (source / "house").glob("*.py"))]
    contents = {}
    for name in paths:
        path = source / name
        content = path.read_bytes()
        committed = subprocess.check_output(["git", "-C", str(source), "show", f"{commit}:{name}"])
        if path.is_symlink() or content != committed:
            raise ValueError(f"runtime must match the source commit: {name}")
        contents[name] = content
    verify = json.loads(subprocess.check_output(
        [str(python), "-m", "house", "--repo", str(source), "verify"], cwd=source, text=True))
    anchor = run("git", "-C", str(source), "rev-parse", "refs/house/foundation")
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    release = root / "release"
    release.mkdir(mode=0o700)
    (release / "house").mkdir(mode=0o700)
    for name, content in contents.items():
        target = release / name
        target.write_bytes(content)
        target.chmod(0o400)
    for name in ("residents", "empty", "logs"):
        (root / name).mkdir(mode=0o700)
    run("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(root / "host_key"))
    write(root / "authorized_keys", "")
    write(root / "known_hosts", f"[127.0.0.1]:{port} " + (root / "host_key.pub").read_text())
    config = f"""Port {port}
ListenAddress 127.0.0.1
HostKey {root}/host_key
PidFile {root}/sshd.pid
AuthorizedKeysFile {root}/authorized_keys
AllowUsers {account}
AuthenticationMethods publickey
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM no
PermitEmptyPasswords no
HostbasedAuthentication no
PermitRootLogin no
PermitUserEnvironment no
PermitUserRC no
StrictModes yes
DisableForwarding yes
PermitTTY no
PermitTunnel no
X11Forwarding no
MaxSessions 1
MaxStartups 4:50:8
LoginGraceTime 20
ClientAliveInterval 15
ClientAliveCountMax 2
PrintMotd no
PrintLastLog no
LogLevel ERROR
"""
    write(root / "sshd_config", config)
    plist = {"Label": LABEL, "ProgramArguments": ["/usr/bin/env", "-i",
             "PATH=/usr/bin:/bin:/usr/sbin:/sbin", "LC_ALL=C", "/usr/sbin/sshd",
             "-D", "-e", "-f", str(root / "sshd_config")],
             "RunAtLoad": True, "KeepAlive": True, "ThrottleInterval": 10,
             "WorkingDirectory": str(root / "empty"), "Umask": 0o077,
             "StandardOutPath": str(root / "logs/stdout.log"),
             "StandardErrorPath": str(root / "logs/stderr.log")}
    with (root / f"{LABEL}.plist").open("xb") as stream:
        plistlib.dump(plist, stream)
    (root / f"{LABEL}.plist").chmod(0o600)
    manifest = {"label": LABEL, "root": str(root), "source": str(source),
                "source_commit": commit, "python": str(python), "account": account,
                "uid": os.getuid(), "port": port, "house": verify["house"], "anchor": anchor,
                "head_at_prepare": verify["head"], "events_at_prepare": verify["events"],
                "runtime_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in contents.items()},
                "host_fingerprint": run("ssh-keygen", "-lf", str(root / "host_key.pub")),
                "boundary": "same account; restricted loopback transport, not hostile same-user isolation"}
    write(root / "installation.json", json.dumps(manifest, indent=2) + "\n")
    run("/usr/sbin/sshd", "-t", "-f", str(root / "sshd_config"))
    return manifest


def enroll(root: Path, resident: str) -> dict:
    root = safe_path(root)
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", resident):
        raise ValueError("invalid resident ID")
    manifest = json.loads((root / "installation.json").read_text())
    with (root / "enrollment.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        target = root / "residents" / resident
        target.mkdir(mode=0o700, exist_ok=False)
        run("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(target / "key"))
        command = [manifest["python"], "-I", str(root / "release/custodian_entry.py"),
                   "--repo", manifest["source"], "--expect-anchor", manifest["anchor"],
                   "--resident", resident, "--timeout", "30"]
        launcher = "\n".join(["#!/bin/sh", "set -eu", 'if [ -n "${SSH_ORIGINAL_COMMAND:-}" ]; then',
                             "    printf '%s\\n' 'remote commands are not accepted' >&2",
                             "    exit 2", "fi", "umask 077", f"cd {shlex.quote(str(root / 'empty'))}",
                             "exec /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C " + shlex.join(command), ""])
        write(target / "launch", launcher, 0o700)
        run("/bin/sh", "-n", str(target / "launch"))
        write(target / "client", f"""Host emberhall-{resident}
    HostName 127.0.0.1
    Port {manifest['port']}
    User {manifest['account']}
    IdentityFile {target}/key
    IdentitiesOnly yes
    IdentityAgent none
    BatchMode yes
    StrictHostKeyChecking yes
    UserKnownHostsFile {root}/known_hosts
    GlobalKnownHostsFile /dev/null
    UpdateHostKeys no
    RequestTTY no
    ForwardAgent no
    ClearAllForwardings yes
    ControlMaster no
    ControlPath none
""")
        # Atomic replacement under the enrollment lock prevents lost key bindings.
        line = f'restrict,command="{target}/launch" ' + (target / "key.pub").read_text()
        replace(root / "authorized_keys", (root / "authorized_keys").read_text() + line)
        return {"resident": resident, "alias": f"emberhall-{resident}",
                "client_config": str(target / "client"), "house": manifest["house"],
                "fingerprint": run("ssh-keygen", "-lf", str(target / "key.pub"))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser("prepare")
    install.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    install.add_argument("--port", type=int, default=22222)
    add = commands.add_parser("enroll")
    add.add_argument("resident")
    args = parser.parse_args()
    os.umask(0o077)
    try:
        result = (prepare(args.source, args.root, args.port) if args.command == "prepare"
                  else enroll(args.root, args.resident))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({"error": str(error),
                          "recovery": "Inspect existing files before retry; no partial installation is erased."}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
