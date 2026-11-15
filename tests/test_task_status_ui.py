"""Exercise task expiry, owner unknowns and safe text in the actual renderer."""
import shutil
import unittest

from tests.test_workshop_ui import RendererMixin


@unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
class TaskStatusUITests(RendererMixin, unittest.TestCase):
    def test_expiry_boundary_historical_and_current(self):
        self.run_renderer(r'''
current=false;
draw([
 {id:'open',title:'Open work',status:'open',until:0,generation:0},
 {id:'watch',title:'Watch',status:'claimed',owner:'mallow',until:1500,generation:1},
 {id:'stale',title:'Stale',status:'claimed',owner:'mallow',until:500,generation:1}
]);
frame.residents=[{id:'mallow',name:'Mallow',room:'hearth',pose:'standing'}];roomPanel();
// Historical frame at 1000: until 1500 not yet expired, until 500 expired.
assert.match(text(panel()),/3 unfinished · 0 finished/);
assert.equal(cards().length,3);
const cardByTitle=t=>cards().find(c=>text(c).includes(t));
assert.match(text(cardByTitle('Watch')),/Recorded claim · Mallow/);
assert.doesNotMatch(text(cardByTitle('Watch')),/Lease expired/);
assert.match(text(cardByTitle('Stale')),/Lease expired · fate unconfirmed/);
assert.doesNotMatch(text(cardByTitle('Stale')),/Mallow/);
assert.match(text(cardByTitle('Open work')),/Unassigned/);
// Boundary is inclusive: at exactly 1500 the 1500 lease is expired.
frame.at=1500;roomPanel();
assert.match(text(cardByTitle('Watch')),/Lease expired · fate unconfirmed/);
frame.at=1499;roomPanel();
assert.match(text(cardByTitle('Watch')),/Recorded claim · Mallow/);
assert.doesNotMatch(text(cardByTitle('Watch')),/Lease expired/);
// Current view uses the wall clock, not frame.at.
const now=Date.now()/1000;
frame.tasks=[
 {id:'old',title:'Old',status:'claimed',owner:'mallow',until:now-1000,generation:1},
 {id:'fresh',title:'Fresh',status:'claimed',owner:'mallow',until:now+100000,generation:1}
];
frame.residents=[{id:'mallow',name:'Mallow',room:'hearth',pose:'standing'}];
current=true;roomPanel();
assert.match(text(cardByTitle('Old')),/Lease expired · fate unconfirmed/);
assert.match(text(cardByTitle('Fresh')),/Recorded claim · Mallow/);
assert.doesNotMatch(text(cardByTitle('Fresh')),/Lease expired/);
''')

    def test_missing_resident_and_empty_snapshot(self):
        self.run_renderer(r'''
current=false;
draw([
 {id:'orphan',title:'Orphan work',status:'claimed',owner:'ghost',until:3000,generation:1}
]);
frame.residents=[];
roomPanel();
assert.match(text(panel()),/1 unfinished · 0 finished/);
assert.match(text(cards()[0]),/Recorded claim · ghost/);
assert.doesNotMatch(text(panel()),/available/);
draw([]);
assert.match(text(panel()),/No tasks are exposed/);
assert.equal(cards().length,0);
assert.doesNotMatch(text(panel()),/Orphan work/);
''')

    def test_hostile_title_is_safe_text(self):
        self.run_renderer(r'''
current=false;
draw([
 {id:'xss',title:'<img src=x onerror=alert(1)>',status:'open',until:0,generation:0}
]);
roomPanel();
assert.equal(cards().length,1);
assert.match(text(cards()[0]),/Unassigned/);
assert.equal(all(panel()).filter(n=>n.tag==='img').length,0);
// Selecting the card shows the title as text, never as markup.
cards()[0].click();
assert.equal(all(panel()).filter(n=>n.tag==='img').length,0);
assert.match(text($('workshop-detail')),/Unassigned/);
''')
