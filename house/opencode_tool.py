"""A fixed no-shell journal tool for the installed OpenCode V1 tool registry."""
from __future__ import annotations

import json
from pathlib import Path
import sys


def configure(private: Path, workspace: Path, runtime: Path, resident: str, env: dict) -> None:
    config = private / 'opencode-config'
    tool = config / 'tools' / 'house_journal.js'
    tool.parent.mkdir(parents=True, exist_ok=True)
    # Never execute the workspace's client or import workspace Python. These
    # literal inputs are selected by the coordinator before the model starts.
    python = ('import sys;sys.path.insert(0,' + repr(str(runtime)) + ');'
              'from pathlib import Path;from house.mailbox import client_main;'
              'raise SystemExit(client_main(Path(' + repr(str(workspace)) + '),'
              + repr(resident) + ',sys.argv[1:]))')
    source = '''import {execFile} from "node:child_process";
export default {
  description: "Emberhall journal. Pass normal house command arguments as an array. No shell syntax. Identity and source room are fixed by the coordinator. Use [\\"--help\\"] for commands.",
  args: {argv: {type: "array", items: {type: "string"}}},
  async execute(args) {
    if (!args || !Array.isArray(args.argv) || args.argv.length < 1 || args.argv.length > 128 ||
        args.argv.some(x => typeof x !== "string" || x.length > 100000))
      throw new Error("Expected a bounded command argument array");
    return await new Promise((resolve, reject) => {
      execFile(PYTHON, ["-I", "-c", CODE, ...args.argv],
        {shell: false, cwd: ROOM, timeout: 3720000, maxBuffer: 12000000},
        (error, stdout, stderr) => {
          if (error) reject(new Error((stderr || error.message).slice(0, 2000)));
          else resolve(stdout);
        });
    });
  }
};
'''
    source = source.replace('PYTHON', json.dumps(str(Path(sys.executable).resolve())))
    source = source.replace('CODE', json.dumps(python)).replace('ROOM', json.dumps(str(workspace)))
    tool.write_text(source)
    tool.chmod(0o600)
    # Keep subscription authentication in its existing data location. Only
    # configuration/custom-tool/skill discovery is isolated from user/project code.
    isolated = private / 'opencode-settings'
    isolated.mkdir(exist_ok=True)
    for name in ('OPENCODE_CONFIG', 'OPENCODE_TUI_CONFIG', 'OPENCODE_CONFIG_DIR'):
        env.pop(name, None)
    env.update(OPENCODE_CONFIG_DIR=str(config), XDG_CONFIG_HOME=str(isolated),
               OPENCODE_TEST_HOME=str(isolated), OPENCODE_DISABLE_PROJECT_CONFIG='1',
               OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_DEFAULT_PLUGINS='1',
               OPENCODE_PURE='1')
