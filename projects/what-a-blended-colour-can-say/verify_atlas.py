"""Verify a saved atlas's exact and outer-box certificates without optimization."""

import argparse
from fractions import Fraction as F
import json
from pathlib import Path

import blended_colour as bc
import display_colour as dc
import quantized_bounds as qb


def verify_atlas(data: dict) -> tuple[int, int]:
    if (data['schema'], data['model'], data['rounding'], data['observation_claim']) != (
        'blended-colour-atlas-v2', 'rational-linear-light-srgb', 'half-up',
        'closed-rational-outer-box',
    ):
        raise ValueError('Unsupported atlas model or observation claim')
    palettes = {
        name: bc.Palette(name, tuple(p['labels']), tuple(map(F, p['values'])),
                         tuple(tuple(map(F, c)) for c in p['colours']))
        for name, p in data['palettes'].items()
    }
    ids, observations = set(), 0
    if not data['swatches']:
        raise ValueError('Empty atlas')
    for s in data['swatches']:
        if s['id'] in ids:
            raise ValueError('Duplicate case ID')
        ids.add(s['id'])
        palette, event = palettes[s['palette']], s['event_indices']
        if not event or any(type(i) is not int or not 0 <= i < palette.size for i in event):
            raise ValueError('Invalid event')
        rgb = tuple(map(F, s['rgb']))
        if bc.blend_colour(palette, tuple(map(F, s['weights']))) != rgb:
            raise ValueError('Source weights and target colour differ')
        if dc.hex_rgb(dc.encode_rgb(rgb)) != s['hex']:
            raise ValueError('Displayed swatch is not the encoded source colour')
        bc.verify_certificate(palette, rgb, event, bc.certificate_from_dict(s['certificate']))
        modes = set()
        if not s['observations']:
            raise ValueError('Missing observations')
        for obs in s['observations']:
            mode = obs['mode']
            if mode in modes:
                raise ValueError('Duplicate observation mode')
            modes.add(mode)
            if dc.hex_rgb(obs['rgb8']) != obs['hex'] or tuple(obs['rgb8']) != dc.encode_rgb(rgb, mode):
                raise ValueError('Observation bytes do not encode the source colour')
            lower, upper = dc.observation_box(obs['rgb8'], mode)
            if (tuple(map(F, obs['lower'])), tuple(map(F, obs['upper']))) != (lower, upper):
                raise ValueError('Observation box differs from the specified byte enclosure')
            qb.verify_observation(palette, obs['rgb8'], event,
                                  qb.certificate_from_dict(obs['certificate']), mode)
            observations += 1
    return len(ids), observations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('atlas', type=Path)
    args = parser.parse_args()
    try:
        cases, observations = verify_atlas(json.loads(args.atlas.read_text(encoding='utf-8')))
    except (ValueError, KeyError, TypeError, IndexError, OSError, ZeroDivisionError) as exc:
        parser.exit(1, f'INVALID: {exc}\n')
    print(f'VALID: {cases} exact cases; {observations} conservative byte-box certificates; no optimizer called.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
