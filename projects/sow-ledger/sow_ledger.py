#!/usr/bin/env python3
"""Turn a small Markdown seed ledger into deterministic, dated JSON (stdlib only)."""
from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import unicodedata


COLUMNS = ('variety', 'harvest_year', 'quantity', 'germination',
           'sow_by', 'shelf_life_years')
MAX_INPUT_BYTES = 1_000_000


def integer(value: str, field: str) -> int:
    if not re.fullmatch(r'[0-9]{1,10}', value):
        raise ValueError(f'{field} must be an integer from 0 to 9999999999')
    return int(value)


def iso_date(value: str) -> date:
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
        raise ValueError('dates must use YYYY-MM-DD')
    return date.fromisoformat(value)


def cells(line: str) -> list[str]:
    line = line.strip()
    if not (line.startswith('|') and line.endswith('|')):
        raise ValueError('table rows must start and end with |')
    values = [cell.strip() for cell in line[1:-1].split('|')]
    if len(values) != len(COLUMNS):
        raise ValueError('each table row must have exactly six cells')
    return values


def report(text: str, as_of: date) -> dict:
    """Validate the entire ledger before producing any output."""
    if any(ord(char) < 32 and char not in '\r\n' for char in text):
        raise ValueError('control characters are not supported')
    if '\x7f' in text:
        raise ValueError('control characters are not supported')
    lines = [(number, line.strip()) for number, line in enumerate(text.splitlines(), 1)
             if line.strip()]
    while lines and lines[0][1].startswith('# '):
        lines.pop(0)
    if len(lines) < 3 or cells(lines[0][1]) != list(COLUMNS):
        raise ValueError('expected the documented header and at least one seed row')
    if not all(re.fullmatch(r':?-{3,}:?', cell) for cell in cells(lines[1][1])):
        raise ValueError('expected a Markdown table separator')
    entries = []
    seen = set()
    for number, line in lines[2:]:
        try:
            row = dict(zip(COLUMNS, cells(line)))
            variety = unicodedata.normalize('NFC', row['variety'])
            if not variety or variety == '-':
                raise ValueError('variety must be nonempty')
            identity = variety.casefold()
            if identity in seen:
                raise ValueError(f'duplicate variety: {variety}')
            seen.add(identity)
            # Empty cells and a single dash always mean unknown/unspecified.
            row = {key: value if value not in ('', '-') else None
                   for key, value in row.items()}
            year = None
            if row['harvest_year'] is not None:
                raw_year = row['harvest_year']
                if not re.fullmatch(r'[0-9]{4}', raw_year):
                    raise ValueError('harvest_year must have four digits')
                year = int(raw_year)
                if not 1 <= year <= as_of.year:
                    raise ValueError('harvest_year must be between 0001 and the as-of year')
            quantity = (integer(row['quantity'], 'quantity')
                        if row['quantity'] is not None else None)
            germination = None
            if row['germination'] is not None:
                ratio = row['germination'].split('/')
                if len(ratio) != 2:
                    raise ValueError('germination must be n/m')
                n, m = (integer(value, 'germination count') for value in ratio)
                if m == 0 or n > m:
                    raise ValueError('germination requires 0 <= n <= m and m > 0')
                percentage = (Decimal(n) * 100 / Decimal(m)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
                germination = {'germinated': n, 'tested': m,
                               'percent': str(percentage)}
            sow_by = None
            source = None
            shelf_life = None
            if row['sow_by'] is not None and row['shelf_life_years'] is not None:
                raise ValueError('choose sow_by or shelf_life_years, not both')
            if row['sow_by'] is not None:
                sow_by = iso_date(row['sow_by'])
                source = 'explicit_date'
            elif row['shelf_life_years'] is not None:
                shelf_life = integer(row['shelf_life_years'], 'shelf_life_years')
                if year is None or year + shelf_life > 9999:
                    raise ValueError('shelf-life assumption needs a known harvest year and end year <= 9999')
                sow_by = date(year + shelf_life, 12, 31)
                source = 'user_shelf_life_assumption'
            entries.append({
                'variety': variety, 'harvest_year': year,
                'age_calendar_years': as_of.year - year if year is not None else None,
                'quantity': quantity, 'germination': germination,
                'sow_by': sow_by.isoformat() if sow_by is not None else None,
                'sow_by_source': source, 'shelf_life_years': shelf_life,
            })
        except ValueError as exc:
            raise ValueError(f'line {number}: {exc}') from exc
    entries.sort(key=lambda entry: (entry['sow_by'] is None, entry['sow_by'] or '',
                                    entry['variety'].casefold(), entry['variety']))
    return {'version': 1, 'as_of': as_of.isoformat(), 'entries': entries}


def read_ledger(path: Path) -> str:
    """Reject special inputs instead of blocking on a FIFO."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('input must be a regular file, not a symlink or special file')
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError('input changed while opening')
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError('input exceeds 1000000 bytes')
    return raw.decode('utf-8')


def write_report(output: Path, payload: bytes) -> None:
    """Stage beside the destination, then publish with one atomic replace."""
    temporary = None
    try:
        descriptor, name = tempfile.mkstemp(prefix='.sow-ledger-', dir=output.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path, help='UTF-8 Markdown seed ledger')
    parser.add_argument('--as-of', required=True, help='injected date: YYYY-MM-DD')
    parser.add_argument('--output', required=True, type=Path, help='atomic JSON output file')
    args = parser.parse_args(argv)
    try:
        as_of = iso_date(args.as_of)
        text = read_ledger(args.ledger)
        result = report(text, as_of)
        try:
            destination = args.output.lstat()
        except FileNotFoundError:
            destination = None
        if destination is not None:
            if not stat.S_ISREG(destination.st_mode):
                raise ValueError('output must be a regular file, not a symlink or special file')
            if args.ledger.samefile(args.output):
                raise ValueError('output must not replace the input ledger')
        payload = (json.dumps(result, ensure_ascii=False, sort_keys=True,
                              indent=2, allow_nan=False) + '\n').encode('utf-8')
        write_report(args.output, payload)
    except (ValueError, OSError) as exc:
        print(f'sow-ledger: {exc}', file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
