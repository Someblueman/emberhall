"""A fixed no-shell journal tool for the installed OpenCode V2 plugin registry."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys


def validate_workspace(workspace: Path) -> None:
    """V2 tool containment is lexical: never admit a room containing links.

    The allowed native tools can write regular files, not create links. Rooms
    have one assigned writer; a hostile same-user shell remains outside this
    cooperative boundary. Recheck after the process gate, before account import.
    """
    if not workspace.is_absolute() or not workspace.is_dir() or workspace.resolve(strict=True) != workspace:
        raise ValueError("OpenCode room must have a canonical path without links")
    def unreadable(error):
        raise ValueError("OpenCode room cannot be fully inspected") from error
    for parent, directories, files in os.walk(workspace, followlinks=False, onerror=unreadable):
        for name in directories + files:
            info = (Path(parent) / name).lstat()
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise ValueError("OpenCode room cannot contain links or special files")
            if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
                raise ValueError("OpenCode room cannot contain hard-linked files")


def configure(private: Path, workspace: Path, runtime: Path, resident: str, env: dict, *,
              web: bool = False) -> dict:
    config = private / 'opencode-config'
    tool = config / 'plugins' / 'house_journal.js'
    tool.parent.mkdir(parents=True, exist_ok=True)
    # Never execute the workspace's client or import workspace Python. These
    # literal inputs are selected by the coordinator before the model starts.
    python = ('import sys;sys.path.insert(0,' + repr(str(runtime)) + ');'
              'from pathlib import Path;from house.mailbox import client_main;'
              'raise SystemExit(client_main(Path(' + repr(str(workspace)) + '),'
              + repr(resident) + ',sys.argv[1:]))')
    source = '''import {execFile} from "node:child_process";
export default {id: "emberhall.journal", async setup(ctx) {
  await ctx.tool.transform(editor => {
  // Permission classes are shared: worktree_remove also uses "edit". Keep
  // exactly the reviewed file tools, then install the fixed journal tool.
  const allowed = new Set(["read", "glob", "grep", "edit", "write", "patch"]);
  for (const tool of editor.list()) if (!allowed.has(tool.name)) editor.remove(tool.id);
  editor.add({
  name: "house_journal",
  options: {permission: "house_journal", codemode: false},
  description: "Emberhall journal. Pass normal house command arguments as an array. No shell syntax. Identity and source room are fixed by the coordinator. Use [\\"--help\\"] for commands.",
  input: {type: "object", properties: {argv: {type: "array", minItems: 1, maxItems: 128,
    items: {type: "string", maxLength: 100000}}}, required: ["argv"], additionalProperties: false},
  async execute(args, context) {
    if (!args || !Array.isArray(args.argv) || args.argv.length < 1 || args.argv.length > 128 ||
        args.argv.some(x => typeof x !== "string" || x.length > 100000))
      throw new Error("Expected a bounded command argument array");
    await ctx.permission.assert({sessionID: context.sessionID, agent: context.agent,
      source: {type: "tool", messageID: context.messageID, id: context.id},
      action: "house_journal", resources: ["*"], save: ["*"]});
    const content = await new Promise((resolve, reject) => {
      execFile(PYTHON, ["-I", "-c", CODE, ...args.argv],
        {shell: false, cwd: ROOM, signal: context.signal, timeout: 3720000, maxBuffer: 12000000},
        (error, stdout, stderr) => {
          if (error) reject(new Error((stderr || error.message).slice(0, 2000)));
          else resolve(stdout);
        });
    });
    return {content};
  }
  });
  });
}};
'''
    source = source.replace('PYTHON', json.dumps(str(Path(sys.executable).resolve())))
    source = source.replace('CODE', json.dumps(python)).replace('ROOM', json.dumps(str(workspace)))
    if web:
        source = source.replace('"write", "patch"', '"write", "patch", "websearch", "webfetch"')
    tool.write_text(source)
    tool.chmod(0o600)
    # Empty private data prevents V2 from importing the stale legacy auth.json.
    # The gated process imports just the current, owner-authorized Go login.
    isolated = private / 'opencode-settings'
    isolated.mkdir(exist_ok=True)
    # Clear inherited overrides, including obsolete V1 flags and simulation/server
    # switches. The model never shares the global session database.
    for name in list(env):
        if name.startswith('OPENCODE_') or name == 'EXA_API_KEY':
            env.pop(name)
    env.update(OPENCODE_CONFIG_DIR=str(config), XDG_CONFIG_HOME=str(isolated),
               OPENCODE_TEST_HOME=str(isolated), OPENCODE_CONFIG_PROJECT_DISABLE='1',
               OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1')
    for key in ('XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME'):
        location = private / key.lower()
        location.mkdir(mode=0o700, exist_ok=True)
        env[key] = str(location)
    rules = [{"action": "*", "resource": "*", "effect": "deny"}]
    for action in ('read', 'glob', 'grep', 'edit', 'house_journal'):
        rules.append({"action": action, "resource": "*", "effect": "allow"})
    if web:
        rules.extend({"action": action, "resource": "*", "effect": "allow"}
                     for action in ("websearch", "webfetch"))
    for action in ('shell', 'subagent', 'external_directory', 'execute'):
        rules.append({"action": action, "resource": "*", "effect": "deny"})
    for action, resource in [('read', '*.env*'), ('edit', '.house-client'),
                             ('edit', '*/.house-client')]:
        rules.append({"action": action, "resource": resource, "effect": "deny"})
    # Native edits have no legitimate Git metadata use. Include case variants:
    # macOS can resolve .GIT to .git while permission globs are case-sensitive.
    for directory in ('.git', '.giT', '.gIt', '.gIT', '.Git', '.GiT', '.GIt', '.GIT'):
        for resource in (directory, directory + '/*', '*/' + directory, '*/' + directory + '/*'):
            rules.append({"action": "edit", "resource": resource, "effect": "deny"})
    # Policies are evaluated before plugin import and again at permission checks.
    # The same deny envelope applies globally and to the selected primary agent.
    policies = [{"action": "provider.use", "resource": "*", "effect": "deny"},
                {"action": "provider.use", "resource": "opencode-go", "effect": "allow"},
                {"action": "plugin.use", "resource": "*", "effect": "deny"},
                {"action": "plugin.use", "resource": str(tool), "effect": "allow"},
                {"action": "mcp.use", "resource": "*", "effect": "deny"},
                {"action": "skill.use", "resource": "*", "effect": "deny"},
                {"action": "websearch.use", "resource": "*", "effect": "allow" if web else "deny"}]
    policies.extend({"action": "tool.use", "resource": rule["action"] + ':' + rule["resource"],
                     "effect": rule["effect"]} for rule in rules)
    # Each private run starts without a persisted selection. Otherwise the first
    # search opens an interactive provider form which headless run cancels.
    # Native Exa supports its public endpoint without a key; never inherit a
    # separately billed Exa credential or rotate to another provider.
    return {"permissions": rules, "policies": policies,
            "websearch": {"provider": "exa"} if web else False,
            "agents": {"emberhall": {"mode": "primary", "permissions": rules}}}
