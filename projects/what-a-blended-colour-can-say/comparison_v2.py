"""Second prospective instrument; the first experiment remains frozen and inconclusive."""
from __future__ import annotations

import argparse
from dataclasses import replace
from fractions import Fraction as F
import hashlib
from html import escape
import json
from pathlib import Path
import re

import blended_colour as bc
import comparison as first
import display_colour as dc
import render_legend as rl
from verify_atlas import verify_atlas

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'comparison_v2'
ORDER = 'dist_a_then_atlas_b'


def palettes() -> dict[str, bc.Palette]:
    result = {}
    for name, corners, relation in (
        ('fern_violet_v2', ((1, 2, 12), (3, 13, 5), (14, 4, 2), (11, 1, 9)),
         (F(1, 5), F(3, 10), F(1, 10), F(2, 5))),
        ('copper_ice_v2', ((2, 3, 13), (4, 14, 3), (13, 5, 1), (10, 2, 11)),
         (F(1, 8), F(3, 8), F(1, 4), F(1, 4))),
    ):
        c0, c1, c3, c4 = (tuple(F(c, 16) for c in row) for row in corners)
        c2 = tuple(sum(w*c for w, c in zip(relation, axis)) for axis in zip(c0, c1, c3, c4))
        result[name] = bc.Palette(name, ('L1', 'L2', 'L3', 'L4', 'L5'),
                                  tuple(F(i) for i in range(1, 6)), (c0, c1, c2, c3, c4))
    ends = ((F(1, 16), F(5, 16), F(13, 16)), (F(13, 16), F(9, 16), F(1, 16)))
    colours = tuple(tuple((1-F(i, 4))*a + F(i, 4)*b for a, b in zip(*ends)) for i in range(5))
    result['plum_lime_ramp_v2'] = bc.Palette('plum_lime_ramp_v2', ('R1','R2','R3','R4','R5'),
                                           tuple(F(i) for i in range(1, 6)), colours)
    return result


def specs() -> tuple[first.ComparisonCase, ...]:
    rows = (
        ('A', 'fern_violet_v2', (
            ((F(1,5), F(7,20), F(0), F(9,20), F(0)), (3,4), 'exact', 'gt', F(1,2)),
            ((F(1,8), F(1,8), F(1,2), F(1,8), F(1,8)), (3,4), 'exact', 'lt', F(1,5)),
            ((F(0), F(0), F(1), F(0), F(0)), (2,), 'exact', 'gt', F(9,10)),
            ((F(1,3), F(1,6), F(0), F(0), F(1,2)), (3,4), 'srgb8', 'lt', F(12,25)),
            ((F(1,5), F(1,5), F(1,5), F(1,10), F(3,10)), (3,4), 'linear8', 'gt', F(3,5)))),
        ('B', 'copper_ice_v2', (
            ((F(1,8), F(1,4), F(0), F(5,8), F(0)), (3,4), 'exact', 'lt', F(3,5)),
            ((F(1,10), F(1,5), F(2,5), F(1,10), F(1,5)), (3,4), 'exact', 'gt', F(1,2)),
            ((F(0), F(1,4), F(1,2), F(1,4), F(0)), (1,3), 'exact', 'lt', F(1,10)),
            ((F(1,6), F(1,3), F(0), F(0), F(1,2)), (3,4), 'srgb8', 'gt', F(13,25)),
            ((F(1,8), F(1,4), F(1,8), F(1,4), F(1,4)), (3,4), 'linear8', 'lt', F(1,3)))),
    )
    result = []
    for group, palette, cases in rows:
        for i, (weights, event, mode, op, threshold) in enumerate(cases, 1):
            actual_palette = 'plum_lime_ramp_v2' if group == 'B' and i == 3 else palette
            label = 'P(' + ', '.join(palettes()[actual_palette].labels[j] for j in event) + ')'
            case = rl.Case(f'V2-{i}{group}', f'Observation {i}{group}', actual_palette, weights, event, label, True)
            result.append(first.ComparisonCase(case, group, ('EXACT','BOUNDED','UNIDENTIFIABLE','ROUNDED_SRGB8','ROUNDED_LINEAR8')[i-1], mode, op, threshold,
                                               ('min','max') if i % 2 else ('max','min')))
    return tuple(result)


def baseline(items: list[dict], palette_map: dict[str, bc.Palette], title: str) -> str:
    """All three scopes have the same endpoint information as the atlas.

    Reuse the frozen distribution formatter; do not add bounds or classifications.
    """
    blocks = []
    template = None
    for mode in ('exact', *dc.MODES):
        current = [first._evaluate_spec(replace(item['spec'], query_mode=mode), palette_map) for item in items]
        page = first.build_distribution_html(current, palette_map, title)
        template = page
        for i, match in enumerate(re.finditer(r'<article data-case="\d+">.*?</article>', page, re.S)):
            spec = items[i]['spec']
            block = match.group().replace(f'data-case="{i}"', f'data-case="{i}" data-mode="{mode}" data-query="{spec.query_mode}"' + ('' if mode == spec.query_mode else ' hidden'), 1)
            blocks.append(block)
    assert template is not None
    template = re.sub(r'<div id="card-view">.*?</div>\n<footer>', '<div id="card-view">'+''.join(blocks)+'</div>\n<footer>', template, flags=re.S)
    control = '<label for="mode-choice">Observation model</label><select id="mode-choice"><option value="query">Case question</option><option>exact</option><option>srgb8</option><option>linear8</option></select>'
    template = template.replace('<label for="case-choice">', control+'<label for="case-choice">')
    template = template.replace("card.hidden = index !== 'all' && card.dataset.case !== index;", "const selected = document.getElementById('mode-choice').value; const wanted = selected === 'query' ? card.dataset.query : selected; card.hidden = card.dataset.mode !== wanted || (index !== 'all' && card.dataset.case !== index);")
    template = template.replace("choice.addEventListener('change', showCase);", "choice.addEventListener('change', showCase); document.getElementById('mode-choice').addEventListener('change', showCase);")
    template = template.replace('</script>', rl.SELECT_KEYS + '</script>')
    return template.replace('</main>', '<p>EXACT means one probability; BOUNDED means a restricted interval; UNIDENTIFIABLE means [0, 1]. All distributions use the selected scope. Rounded observations use conservative closed boxes. Percentages approximate exact rational weights. linear8 bytes are data, not displayed light.</p></main>')


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def source_hashes() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
            ('comparison_v2.py', 'render_legend.py', 'COMPARISON_V2.md', 'comparison.py',
             'blended_colour.py', 'display_colour.py', 'quantized_bounds.py', 'verify_atlas.py')}


def generate(out: Path = OUT) -> None:
    palette_map, cases = palettes(), specs()
    evaluated = [first._evaluate_spec(spec, palette_map) for spec in cases]
    keys, prompts = {}, []
    for item in evaluated:
        spec = item['spec']
        keys[spec.case.id] = dict(set=spec.set_name, query_mode=spec.query_mode,
            p_min=str(item['queried_p_min']), p_max=str(item['queried_p_max']),
            status=item['queried_status'], q4_answer=item['q4_answer'])
        prompts.append(dict(id=spec.case.id, set=spec.set_name, query_mode=spec.query_mode,
                            event=spec.case.event_label, q4=spec.probe_question()))
    write_json(out/'prompts.json', dict(schema='blended-comparison-v2', order=ORDER, cases=prompts))
    write_json(out/'keys/answers.json', dict(schema='blended-comparison-v2-keys', cases=keys))
    write_json(out/'inputs/cases.json', [dict(id=s.case.id, palette=s.case.palette,
               weights=list(map(str,s.case.weights)), event_indices=s.case.event_indices,
               mode=s.query_mode, probe_op=s.probe_op, threshold=str(s.probe_threshold)) for s in cases])
    for group in ('A', 'B'):
        items = [i for i in evaluated if i['spec'].set_name == group]
        selected = [i['spec'] for i in items]
        rendered = rl.render_atlas(palette_map, [s.case for s in selected], mode_led=True,
                                  query_modes={s.case.id:s.query_mode for s in selected},
                                  title=f'Second comparison {group}: probability atlas')
        atlas_dir = out/f'atlas_{group.lower()}'
        atlas_dir.mkdir(parents=True, exist_ok=True)
        for name, kind in (('first_legend.html','html'), ('first_legend.svg','svg'), ('witnesses.json','witnesses')):
            (atlas_dir/name).write_text(rendered[kind], encoding='utf-8')
        dist_dir = out/f'dist_{group.lower()}'
        dist_dir.mkdir(parents=True, exist_ok=True)
        (dist_dir/'index.html').write_text(baseline(items, palette_map, f'Second comparison {group}: explicit distributions'), encoding='utf-8')
    write_json(out/'keyboard-cards.json', [
        {'focus':'#case-choice'}, {'press':'Home'}, *({'press':'ArrowDown'} for _ in range(4)), {'press':'Enter'},
        {'press':'Tab'}, {'press':'Shift+Tab'},
        {'focus':'#mode-choice'}, {'press':'Home'}, {'press':'ArrowDown'},
        {'press':'ArrowDown'}, {'press':'ArrowDown'}, {'press':'Enter'}])
    write_json(out/'keyboard-vector.json', [
        {'focus':'#case-choice'}, {'press':'Home'}, *({'press':'ArrowDown'} for _ in range(4)), {'press':'Enter'},
        {'focus':'#mode-choice'}, {'press':'Home'}, {'press':'ArrowDown'}, {'press':'ArrowDown'}, {'press':'Enter'},
        {'focus':'#vector-toggle'}, {'press':'Space'}, {'focus':'#vector-window'},
        {'press':'ArrowRight'}, {'press':'ArrowRight'}, {'press':'ArrowRight'},
        {'focus':'#vector-right'}, {'press':'Enter'}])
    files = {str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'freeze.json'}
    write_json(out/'freeze.json', dict(schema='blended-comparison-v2-freeze', files=files, sources=source_hashes()))


def verify(out: Path = OUT) -> tuple[int, int]:
    freeze = json.loads((out/'freeze.json').read_text())
    actual = {str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in out.rglob('*') if p.is_file() and p.name != 'freeze.json'}
    if actual != freeze['files'] or source_hashes() != freeze['sources']:
        raise ValueError('Frozen instrument differs: do not assess or update its seal silently')
    counts = [0, 0]
    keys = json.loads((out/'keys/answers.json').read_text())['cases']
    if set(keys) != {s.case.id for s in specs()}:
        raise ValueError('Wrong second-instrument keys')
    for group in ('a','b'):
        bundle = json.loads((out/f'atlas_{group}/witnesses.json').read_text())
        n, m = verify_atlas(bundle); counts[0] += n; counts[1] += m
        for swatch in bundle['swatches']:
            key = keys[swatch['id']]
            cert, _, status = rl._mode_result(swatch, key['query_mode'])
            if (key['p_min'],key['p_max'],key['status']) != (cert['p_min'],cert['p_max'],status):
                raise ValueError('Key disagrees with certified scope')
        html = (out/f'dist_{group}/index.html').read_text()
        if any(word in html for word in ('class="result"', 'answer_keys', 'witnesses.json')):
            raise ValueError('Baseline leaked an answer summary')
    return tuple(counts)


def score(responses: dict, out: Path = OUT) -> dict:
    verify(out)
    if responses.get('order') != ORDER or type(responses.get('phone_desktop_ok')) is not bool:
        raise ValueError('Use the fixed order and a boolean browser result')
    for view in ('dist_view','atlas_view'):
        for row in responses[view].values():
            if type(row.get('q5_clarity')) is not int or not 1 <= row['q5_clarity'] <= 5:
                raise ValueError('Clarity must be an integer from 1 to 5')
    keys = json.loads((out/'keys/answers.json').read_text())
    return first.score_responses(responses, keys)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    gen = sub.add_parser('generate'); gen.add_argument('--out', type=Path, required=True)
    check = sub.add_parser('verify'); check.add_argument('--dir', type=Path, default=OUT)
    scoring = sub.add_parser('score'); scoring.add_argument('responses', type=Path)
    args = parser.parse_args()
    if args.command == 'generate':
        if args.out.resolve() == OUT.resolve() and (OUT/'freeze.json').exists():
            parser.error('Frozen pack already exists: regenerate into a separate directory')
        generate(args.out); print('Generated second instrument:', verify(args.out))
    elif args.command == 'verify':
        print('Verified second instrument:', verify(args.dir))
    else:
        print(json.dumps(score(json.loads(args.responses.read_text())), indent=2))


if __name__ == '__main__':
    main()
