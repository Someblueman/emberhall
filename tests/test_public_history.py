"""Public transport preserves every projected value across Python and browser JS."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from house import public_history
from house.public_history import CHUNK, Encoder, decode, encode

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

    def chunked(self, projection):
        encoder = Encoder(chunked=True)
        root = encoder.value(projection)
        return {'version': 4, 'parts': [], 'root': root, 'nodes': encoder.nodes}

    def concats(self, wire):
        return [node for node in wire['nodes'] if isinstance(node, list) and node and isinstance(node[0], list)]

    def test_long_lists_roundtrip_as_chunks_and_small_ones_are_unchanged(self):
        with patch.object(public_history, 'CHUNK', 4):
            for length in (0, 1, 3, 4, 5, 8, 9, 17, 16 * 4 + 1, 4 ** 3 * 4 + 3):
                for make in (lambda n: n, lambda n: str(n), lambda n: {'n': n % 3}, lambda n: [n % 2, [n % 3]]):
                    projection = {'version': 1, 'frames': [], 'items': [make(n) for n in range(length)]}
                    wire = self.chunked(projection)
                    with self.subTest(length=length):
                        self.assertEqual(decode(wire), projection)
                        self.assertIsInstance(decode(wire)['items'], list)
                        self.assertEqual(bool(self.concats(wire)), length > 4)
                        for concat in self.concats(wire):
                            self.assertTrue(1 < len(concat[0]) <= 4)
            # More than CHUNK ** 2 items need a concat of concats.
            wire = self.chunked({'version': 1, 'items': list(range(4 ** 2 * 3 + 2))})
            is_concat = lambda ref: wire['nodes'][ref] in self.concats(wire)
            self.assertTrue(any(is_concat(ref) for concat in self.concats(wire) for ref in concat[0]))
            self.assertEqual(decode(wire)['items'], list(range(4 ** 2 * 3 + 2)))
            nested = {'version': 1, 'frames': [{'seq': n, 'runs': [{'id': m} for m in range(n + 5)]} for n in range(9)],
                      'matrix': [[m for m in range(n + 1)] for n in range(9)]}
            self.assertEqual(decode(self.chunked(nested)), nested)
        flat = {'version': 1, 'items': list(range(CHUNK))}
        self.assertEqual(self.chunked(flat)['nodes'], encode(flat)['nodes'])
        self.assertEqual(encode(flat)['version'], 2)
        self.assertEqual(self.concats(encode({'version': 1, 'items': list(range(CHUNK * 3))})), [])
        long = {'version': 1, 'items': list(range(CHUNK * 3 + 1))}
        self.assertEqual(decode(self.chunked(long)), long)
        self.assertEqual(decode(encode(long, chunked=True)), long)
        self.assertEqual(self.chunked(long), encode(long, chunked=True))

    def test_an_appended_list_reuses_every_full_chunk_and_group(self):
        with patch.object(public_history, 'CHUNK', 4):
            encoder = Encoder(chunked=True)
            runs = [{'id': n} for n in range(70)]
            encoder.value({'runs': runs})
            before = len(encoder.nodes)
            encoder.value({'runs': runs + [{'id': 70}]})
            # One new run, the changed last chunk, and the concats above it; no chunk is written twice.
            self.assertEqual(len(encoder.nodes) - before, 1 + 1 + 1 + 1 + 1)
            more = len(encoder.nodes)
            encoder.value({'runs': runs + [{'id': 70}, {'id': 71}]})
            self.assertEqual(len(encoder.nodes) - more, 1 + 1 + 1 + 1 + 1)
        encoder = Encoder(chunked=True)
        runs = [{'id': n} for n in range(1100)]
        encoder.value(runs)
        before = len(encoder.nodes)
        encoder.value(runs + [{'id': 1100}])
        self.assertLessEqual(len(encoder.nodes) - before, 6)
        sizes = [len(json.dumps(node)) for node in encoder.nodes[before:]]
        self.assertLess(sum(sizes), 600)

    def test_lists_of_lists_cannot_be_confused_with_concat_nodes(self):
        for chunk in (3, CHUNK):
            with patch.object(public_history, 'CHUNK', chunk):
                for items in ([[]], [[[]]], [[1]], [[], []], [[1, 2, 3]], [[[1, 2, 3]]], [[0]], [[0, 1], [2]],
                              [[n] for n in range(chunk * 2 + 1)], [[[n]] for n in range(chunk * 2 + 1)],
                              [list(range(chunk + 1))], [[list(range(chunk + 1))]]):
                    projection = {'version': 1, 'items': items, 'wrapped': {'items': [items]}}
                    wire = self.chunked(projection)
                    with self.subTest(items=items):
                        self.assertEqual(decode(wire), projection)
                        self.assertEqual(decode(encode(projection)), projection)
                        for node in wire['nodes']:
                            if isinstance(node, list) and len(node) == 1 and isinstance(node[0], list):
                                self.assertTrue(all(type(ref) is int for ref in node[0]))
        # A real [[]] is [{"ref": n}] on the wire, never an inline array.
        wire = encode({'version': 1, 'items': [[]]})
        self.assertIn([{'ref': 0}], wire['nodes'])
        self.assertEqual(wire['nodes'][0], [])

    def test_malformed_concat_nodes_are_rejected(self):
        def wire(*concat, version=4):
            nodes = [[1, 2], [3], {'k': 1}, list(concat), {'version': 1, 'items': {'ref': 3}}]
            made = {'version': version, 'root': {'ref': 4}, 'nodes': nodes}
            return made | {'parts': []} if version in (3, 4) else made
        self.assertEqual(decode(wire([0, 1]))['items'], [1, 2, 3])
        invalid = {
            'out of range': wire([0, 9]), 'negative': wire([-1, 0]), 'forward': wire([0, 4]),
            'itself': wire([0, 3]), 'member not a list': wire([0, 2]), 'empty': wire([]),
            'boolean': wire([True, 0]), 'fractional': wire([0.5]), 'string': wire(['0']),
            'ref object': wire([{'ref': 0}]), 'nested inline': wire([[0]]),
            'version 2': wire([0, 1], version=2), 'version 3': wire([0, 1], version=3),
        }
        for name, bad in invalid.items():
            with self.subTest(name), self.assertRaises(ValueError):
                decode(bad)
        # A concat of a concat is legal.
        nested = {'version': 4, 'parts': [], 'root': {'ref': 4}, 'nodes': [
            [1, 2], [3], [[0, 1]], [[2, 1]], {'version': 1, 'items': {'ref': 3}}]}
        self.assertEqual(decode(nested)['items'], [1, 2, 3, 3])
        with self.assertRaises(ValueError):
            decode({'version': 5, 'parts': [], 'root': {'ref': 0}, 'nodes': [{'version': 1}]})

    @unittest.skipUnless(shutil.which('node'), 'Node executes the real browser decoder')
    def test_browser_decoder_matches_python_and_retains_version_one(self):
        projection = json.loads((ROOT / 'site/history.json').read_text())
        projection['literal'] = {'ref': 4, '__proto__': {'polluted': True}}
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('site/house.js','utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
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
