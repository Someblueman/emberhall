"""Fixed local mailbox client; native sandboxes never write canonical Git."""
from pathlib import Path
import sys

from .mailbox import directory
from .record import Record


def client(record: Record, workspace: Path, resident: str, runtime: Path) -> Path:
    """Create only the resident's local endpoint, bound to its pinned interpreter."""
    path = workspace / ".house-client"
    source = f'''#!{sys.executable} -I
import sys
from pathlib import Path
sys.path.insert(0, {str(runtime)!r})
from house.mailbox import client_main
raise SystemExit(client_main(Path({str(workspace)!r}), {resident!r}, sys.argv[1:]))
'''
    path.write_text(source)
    path.chmod(0o700)
    for kind in ("requests", "responses"):
        with directory(workspace, ".house-mailbox", kind, create=True):
            pass
    with (workspace / ".git/info/exclude").open("a") as exclude:
        exclude.write("\n.house-client\n.house-mailbox/\n")
    return path
