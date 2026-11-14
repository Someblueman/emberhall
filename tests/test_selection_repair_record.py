"""Competing real CLI rejection votes preserve one durable outcome and lost receipts."""
import base64
import json
import time
import uuid
from unittest.mock import patch

from house import council, shelf_gate
from house.governance import digest
from house.record import Record
from tests.support import HouseCase
from tests.test_council import approval
from tests.test_shelf import idea


class SelectionRepairRecordTests(HouseCase):
    def test_competing_final_rejections_and_next_explorer(self):
        self.repo=self.new_repo('selection-repair');self.record=Record(self.repo)
        with patch('house.record.uuid.uuid4',side_effect=[uuid.uuid4(),uuid.UUID(council.APPROVED_HOUSE)]):
            self.record.found('Disposable fixture','Fixture charter')
        def write(op,data,actor='alice',request=None):return self.record.append(op,actor,data,request)
        for actor in ('alice','bob','carol','dana','erin'):write('arrive',{'name':actor},actor)
        for actor,agent,model in [('alice','codex','gpt-6.1-sol'),('bob','muse','muse-ember-1.0')]:
            write('life',{'kind':'identity','agent':agent,'model':model},actor)
        write('council-authorize',approval())
        write('council-propose',{'proposal':'new-policy','mode':'rule','title':'Fixture',
            'text':shelf_gate.REVISED_POLICY_TEXT,'reason':'Synthetic policy exercise',
            'base':self.record.read()[0]['rule_revision']})
        write('task',{'task':'trial','title':'Fixture','description':'Synthetic boundary test'})
        write('claim',{'task':'trial','expect':0,'token':'t','seconds':60})
        write('finish',{'task':'trial','token':'t','result':'Fixture','artifacts':{'x.txt':
            {'sha256':digest('fixture'),'base64':base64.b64encode(b'fixture').decode()}}})
        write('council-trial',{'proposal':'new-policy','task':'trial','evidence':'Synthetic'})
        for actor in ('bob','carol'):write('council-endorse',{'proposal':'new-policy','evidence':'Synthetic'},actor)
        write('council-notice',{'proposal':'new-policy','repository':council.REPOSITORY,
            'issue':council.ISSUE,'comment_id':123,'text_sha256':shelf_gate.REVISED_POLICY_SHA256})
        future=time.time()+council.WAIT_SECONDS+1
        with patch('house.record.time.time',return_value=future):
            write('council-sync',{'repository':council.REPOSITORY,'issue':council.ISSUE,
                'owner_id':council.OWNER_ID,'checked_at':future,'comments':[]})
            write('council-enact',{'proposal':'new-policy'})
        write('shelf',{'kind':'explore-start','round':'first','expect':0,'token':'first','seconds':60})
        write('shelf',{'kind':'explore-publish','round':'first','token':'first','ideas':[idea('a'),idea('b')]})
        write('shelf',{'kind':'choice-open','choice':'reject','milestones':{k:{'milestone':'Useful demo'} for k in ('a','b')}})
        vote={'kind':'choice-vote','choice':'reject','idea':None,'reason':'Insufficient value'}
        for actor in ('alice','bob'):write('shelf',vote,actor)
        children=[(actor,self.process('shelf','--as',actor,'--request',actor+'-vote','--data',json.dumps(vote))) for actor in ('carol','dana')]
        for _,child in children:child.communicate(timeout=20)
        self.assertEqual([0,2],sorted(child.returncode for _,child in children))
        winner=next(actor for actor,child in children if child.returncode==0)
        state,events,head=self.record.read()
        self.assertEqual(state['shelf']['projects'],{})
        self.assertEqual(state['shelf']['choices']['reject']['status'],'rejected')
        self.assertEqual(len(state['shelf']['choices']['reject']['votes']),3)
        retry=self.cli('shelf','--as',winner,'--request',winner+'-vote','--data',json.dumps(vote))
        self.assertTrue(retry['replayed']);self.assertEqual(head,self.record.read()[2])
        write('shelf',{'kind':'explore-start','round':'better','expect':1,'token':'better','seconds':60},'bob')
        self.assertEqual(self.record.read()[0],Record(self.repo).read()[0])
        self.assertEqual(self.record.read()[0]['shelf']['explorer'],'better')
