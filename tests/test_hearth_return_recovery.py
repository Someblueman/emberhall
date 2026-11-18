"""Recover a new conversation trip after its published starting moment vanishes."""
import shutil
import unittest

from tests import test_hearth_conversation as conversation


@unittest.skipUnless(shutil.which("node"), "Node executes the Hearth renderer")
class HearthReturnRecoveryTests(unittest.TestCase):
    run_renderer = conversation.HearthConversationTests.run_renderer

    def test_missing_origin_allows_fresh_trip_and_exact_return(self):
        self.run_renderer(r'''
render=()=>{frame=data.frames[index];show();};choose=()=>{};
show();get('hearth-visit-12').listeners.click();
data.frames=data.frames.filter(f=>f.seq!==13);show();
assert.equal(get('hearth-return'),null);assert.match(text(root),/original moment is absent/);
search('Message');get('hearth-older').listeners.click();
const saved=JSON.stringify(hearthState),before=JSON.stringify(data);
get('hearth-visit-8').listeners.click();
assert.equal(hearthTrail.sequence,12);assert.equal(frame.seq,8);
assert.equal(hearthState.page,0);assert.doesNotMatch(text(root),/Message 9|Message 13/);
assert(get('hearth-return'));get('hearth-return').listeners.click();
assert.equal(frame.seq,12);assert.equal(current,false);
assert.equal(JSON.stringify(hearthState),saved);
assert.equal(document.activeElement,get('hearth-visit-8'));assert(get('hearth-visit-8').scrolled);
assert.equal(hearthTrail,null);assert.equal(JSON.stringify(data),before);
''')

    def test_origin_disappears_between_draw_and_click(self):
        self.run_renderer(r'''
render=()=>{frame=data.frames[index];show();};choose=()=>{};
show();get('hearth-visit-12').listeners.click();
const visit=get('hearth-visit-10');
data.frames=data.frames.filter(f=>f.seq!==13);
visit.listeners.click();assert.equal(hearthTrail.sequence,12);
get('hearth-return').listeners.click();assert.equal(frame.seq,12);
assert.equal(document.activeElement,get('hearth-visit-10'));
''')

    def test_same_moment_does_not_invent_a_recoverable_trip(self):
        self.run_renderer(r'''
render=()=>{frame=data.frames[index];show();};choose=()=>{};
show();get('hearth-visit-12').listeners.click();
data.frames=data.frames.filter(f=>f.seq!==13);show();
get('hearth-visit-12').listeners.click();
assert.equal(hearthTrail.sequence,13);assert.equal(get('hearth-return'),null);
assert.match(text(root),/original moment is absent/);
get('hearth-visit-11').listeners.click();assert.equal(hearthTrail.sequence,12);
get('hearth-visit-10').listeners.click();assert.equal(hearthTrail.sequence,12);
get('hearth-return').listeners.click();assert.equal(frame.seq,12);
assert.equal(document.activeElement,get('hearth-visit-11'));
''')
