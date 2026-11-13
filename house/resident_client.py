"""Fixed resident journal capability, shared by every provider kind."""
from pathlib import Path
import sys
from .record import Record


def client(record: Record, workspace: Path, resident: str, runtime: Path) -> Path:
    """A fixed, narrow journal capability for every agent kind.

    In particular OpenCode may execute this command, but no general shell tools.
    The client pins the canonical record, resident, artifact root and code reader.
    It cannot initialize/restore/overwrite refs, execute source, or choose another
    actor. Ordinary Record validation, lease fencing and governance still apply.
    """
    path = workspace / ".house-client"
    source = f'''#!{sys.executable}
import sys
sys.path.insert(0, {str(runtime)!r})
from house.__main__ import parser, run
import json
args = sys.argv[1:]
allowed = {{"status", "rules", "verify", "read", "wait", "receipt", "arrive", "wake", "sleep", "say",
           "task", "claim", "renew", "release", "finish", "learn", "review", "supersede", "life"}}
try:
    if not args or args[0] not in allowed:
        raise ValueError("use a normal resident journal command")
    parsed = parser().parse_args(["--repo", {str(record.root)!r}, "--artifacts-from", {str(workspace)!r}, *args])
    if hasattr(parsed, "actor") and parsed.actor != {resident!r}:
        raise ValueError("this client belongs to another resident")
    if parsed.command == "life":
        data = json.loads(parsed.data)
        if data.get("kind") not in {{"identity", "activity", "room", "ambition", "help"}}:
            raise ValueError("not a resident life command")
    print(json.dumps(run(parsed), indent=2))
except (ValueError, OSError, KeyError, TypeError) as error:
    print("house: " + str(error), file=sys.stderr)
    raise SystemExit(2)
'''
    path.write_text(source)
    path.chmod(0o700)
    with (workspace / ".git/info/exclude").open("a") as exclude:
        exclude.write("\n.house-client\n")
    return path

