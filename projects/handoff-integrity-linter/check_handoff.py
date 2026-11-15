#!/usr/bin/env python3
"""Check explicit draft artifact claims against a workspace, without writing it."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any


class ClaimError(ValueError):
    """Invalid claim input or unsafe filesystem entry."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ClaimError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_path(value: Any) -> str:
    if (not isinstance(value, str) or not value
            or any(part in ('', '.', '..') for part in value.split('/'))
            or '\\' in value or ':' in value
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ClaimError(f"invalid repo-relative path: {value!r}")
    value.encode('utf-8', errors='strict')
    if any(part.casefold() == '.git' for part in value.split('/')):
        raise ClaimError("Git metadata is not an artifact")
    return value


def validate_claims(value: Any) -> list[dict[str, Any]]:
    if (not isinstance(value, dict) or set(value) != {'version', 'artifacts'}
            or type(value['version']) is not int or value['version'] != 1
            or not isinstance(value['artifacts'], list) or not value['artifacts']):
        raise ClaimError('expected version 1 and a nonempty artifacts list')
    seen: set[str] = set()
    for entry in value['artifacts']:
        if (not isinstance(entry, dict) or 'path' not in entry
                or set(entry) - {'path', 'sha256', 'bytes', 'git'}):
            raise ClaimError('artifact requires path; allowed fields: path, sha256, bytes, git')
        path = validate_path(entry['path'])
        if path in seen:
            raise ClaimError(f'duplicate artifact path: {path}')
        seen.add(path)
        if 'bytes' in entry and (type(entry['bytes']) is not int or entry['bytes'] < 0):
            raise ClaimError(f'invalid byte count: {path}')
        if 'sha256' in entry and (not isinstance(entry['sha256'], str)
                or re.fullmatch('[0-9a-f]{64}', entry['sha256']) is None):
            raise ClaimError(f'invalid SHA-256: {path}')
        if 'git' in entry and entry['git'] not in ('clean', 'dirty'):
            raise ClaimError(f'invalid Git state: {path}')
    return value['artifacts']


def identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def open_directory(path: Path) -> int:
    if os.name != 'posix' or not hasattr(os, 'O_NOFOLLOW'):
        raise ClaimError('safe filesystem checks require POSIX with O_NOFOLLOW')
    # Resolve caller-supplied root aliases (e.g. macOS /tmp); artifact components
    # are opened separately and never resolved through symlinks.
    return os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)


def read_regular(root_fd: int, path: str) -> tuple[str, int]:
    parent = os.dup(root_fd)
    try:
        parts = path.split('/')
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=parent)
            os.close(parent)
            parent = child
        before = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode):
            raise ClaimError('symlink or nonregular file is forbidden')
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=parent)
        try:
            if identity(before) != identity(os.fstat(fd)):
                raise ClaimError('file changed before reading')
            digest = hashlib.sha256()
            size = 0
            while chunk := os.read(fd, 1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
            if (identity(before) != identity(os.fstat(fd))
                    or identity(before) != identity(os.stat(
                        parts[-1], dir_fd=parent, follow_symlinks=False))):
                raise ClaimError('file changed during reading')
            return digest.hexdigest(), size
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def git_command(workspace: Path, *args: str) -> bytes:
    # Ignore inherited repository/index overrides, disable optional index writes
    # and filesystem-monitor helpers. These commands never invoke hooks or diff.
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_NO_LAZY_FETCH'] = '1'
    result = subprocess.run(
        ['git', '--no-optional-locks', '--literal-pathspecs', '-c', 'core.fsmonitor=false',
         '-c', 'core.untrackedCache=false', '-C', str(workspace), *args],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15,
        check=False)
    if result.returncode:
        raise ClaimError('Git discovery/status failed: ' + result.stderr.decode(
            'utf-8', errors='replace').strip())
    return result.stdout


def check(workspace: Path, claims: list[dict[str, Any]]) -> dict[str, Any]:
    workspace = workspace.resolve(strict=True)
    root_fd = open_directory(workspace)
    try:
        git_error = None
        try:
            root = git_command(workspace, 'rev-parse', '--show-toplevel').rstrip(b'\n')
            if Path(os.fsdecode(root)).resolve() != workspace:
                raise ClaimError('workspace must be the Git top-level for repo-relative Git claims')
        except (OSError, ClaimError, subprocess.TimeoutExpired) as exc:
            git_error = str(exc)
        results = []
        for entry in claims:
            path = entry['path']
            row: dict[str, Any] = {'path': path, 'ok': False, 'errors': []}
            try:
                digest, size = read_regular(root_fd, path)
                row.update(sha256=digest, bytes=size)
            except (OSError, ClaimError) as exc:
                row['errors'].append(f'file unavailable or unsafe: {exc}')
            if 'sha256' in row:
                for field in ('sha256', 'bytes'):
                    if field in entry and entry[field] != row[field]:
                        row['errors'].append(f'{field} mismatch (expected {entry[field]})')
            state = 'unavailable'
            reason = git_error
            # Unsafe/missing artifacts must never be handed to Git through an
            # unverified symlink. Their filesystem failure already fails the row.
            if reason is None and 'sha256' in row:
                try:
                    tracked = git_command(workspace, 'ls-files', '--cached', '-z', '--', path)
                    changes = git_command(workspace, 'status', '--porcelain=v1', '-z',
                                          '--untracked-files=all', '--ignored=matching', '--', path)
                    state = 'dirty' if not tracked or changes else 'clean'
                except (OSError, ClaimError, subprocess.TimeoutExpired) as exc:
                    reason = str(exc)
            row['git'] = state
            if reason:
                row['git_reason'] = reason
            if 'git' in entry and entry['git'] != state:
                row['errors'].append(f'git mismatch (expected {entry["git"]}, observed {state})')
            row['ok'] = not row['errors']
            results.append(row)
        return {'ok': all(row['ok'] for row in results), 'git_available': git_error is None,
                'artifacts': results}
    finally:
        os.close(root_fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path, help='workspace root (Git top-level for Git checks)')
    parser.add_argument('claims', type=Path, help='UTF-8 JSON claim file')
    args = parser.parse_args(argv)
    try:
        claim_path = args.claims.absolute()
        parent = open_directory(claim_path.parent.resolve(strict=True))
        try:
            # Apply the same no-follow/regular-file rule to the claim input.
            digest, size = read_regular(parent, claim_path.name)
            fd = os.open(claim_path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=parent)
            with os.fdopen(fd, 'rb') as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ClaimError('claims must be a regular file')
                raw = stream.read()
            if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
                raise ClaimError('claim file changed during reading')
        finally:
            os.close(parent)
        claims = validate_claims(json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object))
        result = check(args.workspace, claims)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0 if result['ok'] else 1
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}), file=sys.stderr, flush=True)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    sys.exit(main())
