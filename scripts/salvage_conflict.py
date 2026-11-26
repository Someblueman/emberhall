#!/usr/bin/env python3
"""Reassemble verified inspection bundle pages as a patch; never apply it."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import tempfile


def salvage(pages, destination):
    """Validate contiguous exact-identity pages before exclusive output creation."""
    identity = None
    cursor = 0
    complete = False
    digest = hashlib.sha256()
    with tempfile.TemporaryFile() as patch:
        for filename in pages:
            if complete:
                raise ValueError('page after completed bundle')
            page = json.loads(Path(filename).read_text())
            keys = ('run', 'base', 'contribution', 'selected_paths', 'patch_bytes', 'patch_sha256')
            current = {key: page[key] for key in keys}
            if identity is None:
                identity = current
            if current != identity or page.get('bundle') is not True or page['offset'] != cursor:
                raise ValueError('bundle identity or continuation mismatch')
            chunk = base64.b64decode(page['patch_base64'], validate=True)
            cursor += len(chunk)
            if page['through'] != cursor or cursor > page['patch_bytes']:
                raise ValueError('bundle byte count mismatch')
            complete = page['has_more'] is False
            if complete != (cursor == page['patch_bytes']) or (not chunk and not complete):
                raise ValueError('invalid bundle completion')
            digest.update(chunk); patch.write(chunk)
        if not complete or digest.hexdigest() != identity['patch_sha256']:
            raise ValueError('incomplete bundle or SHA-256 mismatch')
        patch.seek(0)
        # Existing files are never overwritten. No git command is run here.
        with Path(destination).open('xb') as output:
            while chunk := patch.read(64_000):
                output.write(chunk)
    return {**identity, 'sha256': digest.hexdigest(), 'bytes': cursor}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pages', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(salvage(args.pages, args.output), sort_keys=True))


if __name__ == '__main__':
    main()
