"""Exercise the complete latest frame and the publication transfer budget."""
import copy
import gzip
import json
import random
from unittest.mock import patch
import unittest

from house import publish as publisher
from house.body import projection
from house.home_work import git
from house.public_history import Encoder, decode, encode
from tests.support import HouseCase


def current_json(snapshot):
    return publisher.current_snapshot_files(snapshot)["current.json"]


def fixture(frames, scars=None):
    encoder = Encoder(chunked=True)
    refs = [encoder.value(frame) for frame in frames]
    return dict(final={'name':'Test house','house_id':'test-id','private':'never public'},
                frames=refs,nodes=encoder.nodes,scars=scars or {},head='journal',
                source_head='source',observed_at=123.,commits=[])


def frame(seq, **extra):
    return dict(seq=seq,at=100.+seq,event={'op':'say','actor':'a','title':'Hello'},
                rooms=[{'id':'door','name':'Door'}],residents=[],tasks=[],scars=[],**extra)


class CurrentSnapshotUnitTests(unittest.TestCase):
    def test_exact_current_frame_and_only_selected_scar_catalog(self):
        frames = [frame(1),frame(2)]
        frames[1]['scars'] = [{'id':'kept','mended':True,'reviews':2}]
        scars = {'kept':{'id':'kept','title':'repair','mended':True,'reviews':2},
                 'unused':{'id':'unused','title':'unused'}}
        source = fixture(frames,scars)
        before = copy.deepcopy(source)
        out = json.loads(current_json(source))
        self.assertEqual(out['frames'],frames[-1:])
        self.assertEqual(out['history'],dict(current_only=True,total_frames=2,last_sequence=2))
        self.assertEqual(out['scars'],{'kept':{'id':'kept','title':'repair'}})
        self.assertNotIn('private',json.dumps(out))
        self.assertEqual(source,before)

    def test_unrelated_historical_nodes_are_not_decoded(self):
        source = fixture([frame(1),frame(2)])
        # Append a deliberately invalid unreachable node: a whole-table decoder
        # would visit it. The selected-frame reader must never touch it.
        source['nodes'].append({'unused':{'ref':10**9}})
        self.assertEqual(json.loads(current_json(source))['frames'],[frame(2)])

    def test_seeded_chunked_dag_matches_full_decoder(self):
        rng = random.Random(20261126)
        frames = [frame(n,samples=[{'x':rng.randrange(8),'values':list(range(70))} for _ in range(40)])
                  for n in range(1,101)]
        source = fixture(frames)
        out = json.loads(current_json(source))
        full = projection(source['final'],'journal','source',123.,[],frames,{})
        decoded = decode(encode(full,chunked=True))
        self.assertEqual(out['frames'],decoded['frames'][-1:])
        for key in ('version','name','house_id','journal_head','source_head','observed_at','timezone','commits','limits'):
            self.assertEqual(out[key],decoded[key])

    def test_size_is_independent_of_historical_frame_count(self):
        first = fixture([frame(1)])
        many = fixture([frame(1)]*10000)
        a,b = current_json(first),current_json(many)
        self.assertLessEqual(len(b)-len(a),4)  # only the total count grows
        self.assertLess(len(b),1500)
        self.assertEqual(json.loads(b)['history']['total_frames'],10000)

    def test_whole_current_frame_is_retained_without_summary_truncation(self):
        f = frame(1,shelf={'projects':[{'id':str(n),'detail':'x'*50} for n in range(100)]})
        f['tasks']=[{'id':str(n),'description':'y'*30} for n in range(500)]
        out=json.loads(current_json(fixture([f])))
        self.assertEqual(out['frames'][0],f)

    def test_gzip_companion_preserves_the_frame_and_fits_the_combined_budget(self):
        latest = frame(2, description="words " * 1000)
        source = fixture([frame(1), latest])
        with patch.object(publisher, 'CURRENT_SNAPSHOT_MAX_BYTES', 1000):
            files = publisher.current_snapshot_files(source)
        current = json.loads(files['current.json'])
        self.assertEqual(set(files), {'current.json', current['gzip']})
        decoded = json.loads(gzip.decompress(files[current['gzip']]))
        self.assertEqual(decoded['frames'], [latest])
        self.assertEqual(decoded['history'], current['history'])
        self.assertEqual(decoded['journal_head'], current['journal_head'])
        self.assertLessEqual(sum(map(len, files.values())), 1000)

    def test_empty_missing_corrupt_and_oversize_fail_explicitly(self):
        for source in ({},fixture([])):
            with self.assertRaises(ValueError):current_json(source)
        missing=fixture([frame(1)]);missing['frames'][0]={'ref':10**9}
        with self.assertRaises(ValueError):current_json(missing)
        scars=fixture([frame(1)]);scars['nodes'][scars['frames'][0]['ref']]['scars']={'ref':10**9}
        with self.assertRaises(ValueError):current_json(scars)
        with patch.object(publisher,'CURRENT_SNAPSHOT_MAX_BYTES',100):
            with self.assertRaisesRegex(ValueError,'size budget'):
                current_json(fixture([frame(1)]))


class CurrentSnapshotPublicationTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo/'site').mkdir()
        for name in ('index.html','house.css','house.js'):
            (self.repo/'site'/name).write_text('fixture '+name)
        git(self.repo,'add','site')
        git(self.repo,'-c','commit.gpgsign=false','-c','user.name=Test','-c','user.email=test@local',
            'commit','-m','Disposable publication fixture')

    def test_real_publisher_pairs_current_and_history_heads_and_frames(self):
        for n in range(25):
            self.record.append('say','alice',{'text':f'Seeded event {n}'})
        result=publisher.publish(self.record)
        ref='refs/heads/'+publisher.BRANCH
        out=json.loads(self.record.git('show',ref+':current.json'))
        wire=json.loads(self.record.git('show',ref+':history.json'))
        full=decode(wire,lambda path:self.record.git('show',ref+':'+path))
        head=json.loads(self.record.git('show',ref+':head.json'))
        self.assertEqual(out['frames'],full['frames'][-1:])
        self.assertEqual(out['history']['total_frames'],len(full['frames']))
        self.assertEqual(out['history']['last_sequence'],head['seq'])
        self.assertEqual(out['journal_head'],head['journal_head'])
        self.assertEqual(out['source_head'],head['source_head'])
        self.assertLess(len(json.dumps(out)),publisher.CURRENT_SNAPSHOT_MAX_BYTES)
        self.assertFalse(publisher.publish(self.record)['changed'])
        self.record.append('say','bob',{'text':'One newer event'})
        publisher.publish(self.record)
        newer=json.loads(self.record.git('show',ref+':current.json'))
        self.assertEqual(newer['history']['total_frames'],out['history']['total_frames']+1)
        self.assertNotEqual(newer['journal_head'],out['journal_head'])

    def test_size_failure_does_not_change_publication_or_source_refs(self):
        publisher.publish(self.record)
        ref='refs/heads/'+publisher.BRANCH
        before=self.record.git('rev-parse',ref)
        source=self.record.git('rev-parse','HEAD')
        journal=self.record.read()[2]
        self.record.append('say','alice',{'text':'Fresh event'})
        with patch.object(publisher,'CURRENT_SNAPSHOT_MAX_BYTES',10):
            with self.assertRaisesRegex(ValueError,'size budget'):publisher.publish(self.record)
        self.assertEqual(self.record.git('rev-parse',ref),before)
        self.assertEqual(self.record.git('rev-parse','HEAD'),source)
        self.assertNotEqual(self.record.read()[2],journal)  # only our explicit append changed it

    def test_existing_version_four_publication_gets_current_without_a_head_change(self):
        commit = publisher.publish(self.record)['commit']
        root = self.record.git('ls-tree', commit)
        without_current = b'\n'.join(line for line in root.splitlines()
                                     if not line.endswith(b'\tcurrent.json')) + b'\n'
        tree = self.record.git('mktree', data=without_current).decode().strip()
        old = self.record.git('commit-tree', tree, '-p', commit, data=b'Old format\n').decode().strip()
        ref = 'refs/heads/' + publisher.BRANCH
        self.record.git('update-ref', ref, old, commit)
        self.assertTrue(publisher.publish(self.record)['changed'])
        self.assertEqual(self.record.git('show', ref + ':head.json'),
                         self.record.git('show', commit + ':head.json'))
        current = json.loads(self.record.git('show', ref + ':current.json'))
        self.assertEqual(current['journal_head'], self.record.read()[2])
        self.assertFalse(publisher.publish(self.record)['changed'])
