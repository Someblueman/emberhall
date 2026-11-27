"""Check projected name centres and separation between sleeping residents names."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


def overlap(a, b):
    # Separating-axis theorem for convex SVG bed faces and text rectangles.
    for poly in (a, b):
        for p, q in zip(poly, poly[1:] + poly[:1]):
            axis = (q[1] - p[1], p[0] - q[0])
            aa = [x * axis[0] + y * axis[1] for x, y in a]
            bb = [x * axis[0] + y * axis[1] for x, y in b]
            if max(aa) <= min(bb) or max(bb) <= min(aa):
                return False
    return True


@unittest.skipUnless(shutil.which('node'), 'Node executes the shipped renderer')
class QuietLoftBunkLabelTests(unittest.TestCase):
    def test_names_do_not_cross_other_beds_or_labels(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.textContent='';}
 appendChild(n){this.children.push(n);} setAttribute(k,v){this.attrs[k]=String(v);}
}
const document={createElementNS:(_,tag)=>new Element(tag)};
const context=vm.createContext({document});
const source=fs.readFileSync(process.argv[1],'utf8');
// Strip the exact current entrypoint. A changed startup must be audited, not hidden.
const tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail),'Audit changed page startup before loading this fixture');
vm.runInContext(source.slice(0,-tail.length),context);
const render=vm.runInContext('(resident,x,y)=>{const g=document.createElementNS("","g");figure(g,resident,x,y);return g.children[0];}',context);
const names=['Mica','Hawthorn','Keeper','Foxglove','Kittiwake','Tansyfern'];
console.log(JSON.stringify(names.map((name,n)=>render({id:name,name,agent:'codex',presence:'asleep',pose:'sleeping'},32+n%3*55,54+Math.floor(n/3)*62))));
'''
        result = subprocess.run(['node', '-e', script, str(ROOT / 'site/house.js')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        groups = json.loads(result.stdout)
        beds, labels = [], []
        for group in groups:
            faces, texts = [], []
            for node in group['children']:
                attrs = node['attrs']
                if node['tag'] == 'polygon':
                    faces.append([tuple(map(float, pt.split(',')))
                                  for pt in attrs['points'].split()])
                if node['tag'] == 'text':
                    x, y = float(attrs['x']), float(attrs['y'])
                    # 13px system font plus the shipped 3px outline; generous width.
                    half = len(node['textContent']) * 4 + 1.5
                    texts.append((node['textContent'], [(x-half,y-12), (x+half,y-12),
                                                       (x+half,y+4), (x-half,y+4)]))
            beds.append(faces)
            labels.append(texts)
        for i, texts in enumerate(labels):
            name, rect = texts[1]
            for j, faces in enumerate(beds):
                if i != j:
                    cx = (rect[0][0] + rect[1][0]) / 2
                    cy = (rect[0][1] + rect[2][1]) / 2
                    center = [(cx-.5,cy-.5),(cx+.5,cy-.5),(cx+.5,cy+.5),(cx-.5,cy+.5)]
                    self.assertFalse(any(overlap(center, face) for face in faces),
                                     f'{name} crosses bunk {j}')
            for j, other in enumerate(labels):
                for k, (text, box) in enumerate(other):
                    if k == 1 and i != j:
                        self.assertFalse(overlap(rect, box), f'{name} in bunk {i} crosses {text} in bunk {j}')
