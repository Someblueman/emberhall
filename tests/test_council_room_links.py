"""Follow Council room decisions through the shipped renderer."""
import shutil
import unittest

from tests import test_council_room_and_filters as council


SETUP = r"""
const person={name:'Mallow',agent:'codex',id:'mallow'};
const proposal=(id,title)=>({id,title,author:person,mode:'rule',status:'pending',
 stale:false,reason:'A reason to read',text:'The proposed words',endorsements:[],notice:null});
const choice={id:'choice-one',status:'open',owner:person,opened_sequence:1,
 selection_version:2,candidates:[{id:'idea',title:'A bright idea',author:person,milestone:'Try it'}],votes:[]};
frame={seq:2,at:1000,rooms:[{id:'council',name:'The Council',status:'open'}],
 residents:[],tasks:[],scars:[],runs:[],voting:{choices:[choice],proposals:[proposal('one','First proposal')]}};
data={timezone:'UTC',frames:[frame,{...frame,seq:3,voting:{choices:[],proposals:[proposal('future','Future secret')]}}]};
index=0;current=false;selected='council';
const window={location:{hash:'#room/council'},history:{pushState(a,b,hash){window.location.hash=hash;}}};
let shown=null;showViewForHash=hash=>{shown=hash;};
const draw=()=>{nodes['room-content'].replaceChildren();renderCouncilRoom(nodes['room-content']);};
const link=id=>byId(nodes['room-content'],id);
draw();
"""


@unittest.skipUnless(shutil.which('node'), 'Node executes the page renderer')
class CouncilRoomLinksTests(unittest.TestCase):
    run_renderer = council.CouncilRoomAndFiltersTests.run_renderer

    def test_exact_proposal_opens_despite_filters_without_advancing_history(self):
        self.run_renderer(SETUP + r"""
votingState={query:'cannot match',status:'enacted',kind:'choices'};voting();
const before=JSON.stringify(data);
const target=link('council-proposal-one');assert(target);assert.equal(target.href,'#council-view');
let prevented=false;target.listeners.click[0]({preventDefault(){prevented=true;}});
assert(prevented);assert.equal(shown,'#council-view');assert.equal(window.location.hash,'#council-view');
assert.equal(votingState.query,'');assert.equal(votingState.status,'all');assert.equal(votingState.kind,'all');
const record=byId(nodes.voting,'vote-rule-one');assert(record.open);
assert.equal(document.activeElement,record);assert.equal(record.attrs.tabindex,'-1');
assert.equal(index,0);assert.equal(frame.seq,2);assert.equal(current,false);
assert.equal(JSON.stringify(data),before);assert.doesNotMatch(text(nodes.voting),/Future secret/);
// Normal refresh retains the opened record and its keyboard focus.
render=()=>{draw();voting();};refreshView(true);
assert(byId(nodes.voting,'vote-rule-one').open);
assert.equal(document.activeElement,byId(nodes.voting,'vote-rule-one'));
""")

    def test_choice_and_unusual_proposal_ids_are_literal_and_keep_other_disclosures(self):
        self.run_renderer(SETUP + r"""
const odd='x\"/<> ?';frame.voting.proposals.push(proposal(odd,'<img src=x> literal'));
voting();byId(nodes.voting,'vote-rule-one').open=true;draw();
assert(link('council-proposal-'+odd));assert(!all(nodes['room-content']).some(n=>n.tag==='img'));
link('council-choice-choice-one').listeners.click[0]({preventDefault(){}});
assert.equal(document.activeElement,byId(nodes.voting,'vote-choice-choice-one'));
assert(byId(nodes.voting,'vote-choice-choice-one').open);assert(byId(nodes.voting,'vote-rule-one').open);
link('council-proposal-'+odd).listeners.click[0]({preventDefault(){}});
assert.equal(document.activeElement,byId(nodes.voting,'vote-rule-'+odd));
assert(byId(nodes.voting,'vote-choice-choice-one').open);
assert.match(text(nodes.voting),/<img src=x> literal/);assert(!all(nodes.voting).some(n=>n.tag==='img'));
""")

    def test_stale_click_does_not_borrow_a_future_or_missing_record(self):
        self.run_renderer(SETUP + r"""
const old=link('council-proposal-one');frame={...frame,seq:1,voting:{choices:[],proposals:[]}};
votingState={query:'kept',status:'historical',kind:'rule'};
old.listeners.click[0]({preventDefault(){}});
assert.equal(shown,null);assert.equal(window.location.hash,'#room/council');
assert.equal(votingState.query,'kept');assert.equal(frame.seq,1);
assert.equal(openCouncilRecord('proposal','future'),false);
assert.equal(openCouncilRecord('other','one'),false);
frame.voting=null;assert.equal(openCouncilRecord('proposal','one'),false);
""")


if __name__ == '__main__':
    unittest.main()
