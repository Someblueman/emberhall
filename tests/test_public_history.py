"""Public transport preserves every projected value across Python and browser JS."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from house.public_history import decode, encode

ROOT = Path(__file__).resolve().parent.parent


class PublicHistoryTests(unittest.TestCase):
    def test_real_history_roundtrip_reuses_containers_and_is_deterministic(self):
        projection = json.loads((ROOT / 'site/history.json').read_text())
        wire = encode(projection)
        self.assertEqual(decode(wire), projection)
        self.assertEqual(wire, encode(projection))
        self.assertLess(len(json.dumps(wire)), len(json.dumps(projection)) // 2)
        decoded = decode(encode({'version': 1, 'frames': [
            {'seq': 1, 'rooms': [{'id': 'door'}]},
            {'seq': 2, 'rooms': [{'id': 'door'}]}]}))
        self.assertIs(decoded['frames'][0]['rooms'], decoded['frames'][1]['rooms'])
        self.assertIsNot(decoded['frames'][0], decoded['frames'][1])

    def test_values_resembling_refs_and_malformed_transport(self):
        projection = {'version': 1, 'frames': [], 'literal': {'ref': 3},
                      'types': [False, 0, None, '', [], {}, 1.5, '<script>'],
                      '__proto__': {'polluted': True}}
        self.assertEqual(decode(encode(projection)), projection)
        self.assertIs(decode(projection), projection)
        invalid = [
            {'version': 3}, {'version': 2, 'nodes': {}, 'root': {'ref': 0}},
            {'version': 2, 'nodes': [None], 'root': {'ref': 0}},
            {'version': 2, 'nodes': [{'version': 1}], 'root': {'ref': True}},
            {'version': 2, 'nodes': [{'cycle': {'ref': 0}}], 'root': {'ref': 0}},
            {'version': 2, 'nodes': [{'forward': {'ref': 1}}, {}], 'root': {'ref': 1}},
            {'version': 2, 'nodes': [{'inline': []}], 'root': {'ref': 0}},
            {'version': 2, 'nodes': [{'version': 1}], 'root': {'ref': -1}},
            {'version': 2, 'nodes': [{'version': 1}], 'root': {'ref': 0, 'extra': 1}},
            {'version': 2, 'nodes': [[]], 'root': {'ref': 0}},
        ]
        for wire in invalid:
            with self.subTest(wire=wire), self.assertRaises(ValueError):
                decode(wire)

    @unittest.skipUnless(shutil.which('node'), 'Node executes the real browser decoder')
    def test_browser_decoder_matches_python_and_retains_version_one(self):
        projection = json.loads((ROOT / 'site/history.json').read_text())
        projection['literal'] = {'ref': 4, '__proto__': {'polluted': True}}
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('site/house.js','utf8'),tail='refresh();\nsetInterval(refresh,60000);\n';
assert(source.endsWith(tail));const ctx=vm.createContext({});vm.runInContext(source.slice(0,-tail.length),ctx);
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const decoded=ctx.decodePublicHistory(input.wire);
assert.equal(JSON.stringify(decoded),JSON.stringify(input.projection));
assert.equal(ctx.decodePublicHistory(input.projection),input.projection);
assert.equal({}.polluted,undefined);
for(const ref of [-1, true, 0.5, 1])assert.throws(()=>ctx.decodePublicHistory({version:2,nodes:[{version:1}],root:{ref}}));
assert.throws(()=>ctx.decodePublicHistory({version:2,nodes:[{cycle:{ref:0}}],root:{ref:0}}));
assert.throws(()=>ctx.decodePublicHistory({version:2,nodes:[{inline:[]}],root:{ref:0}}));
assert.throws(()=>ctx.decodePublicHistory({version:2,nodes:[],root:null}));
assert.equal(ctx.buildCatchupDigest(decoded.frames,13,1).tasks[0].seq,14);
console.log('ok');
'''
        result = subprocess.run(['node', '-e', script], cwd=ROOT,
                                input=json.dumps({'projection': projection, 'wire': encode(projection)}),
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
