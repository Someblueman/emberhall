"""Exercise presence and mind filters through the shipped resident directory."""
import shutil
import unittest

from tests import test_beds_directory as directory


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class BedsFilterTests(unittest.TestCase):
    run_renderer = directory.BedsDirectoryTests.run_renderer

    def test_combined_filters_alias_paging_and_reset(self):
        self.run_renderer(r'''
people[1].agent='muse';people[1].presence='recorded awake';people[1].pose='standing';
people[2].agent='opencode';people[3].agent='agy';
const before=JSON.stringify(frame),bunks=JSON.stringify(dormView(frame,1));show();
const change=(id,value)=>{get(id).value=value;get(id).listeners.change();};
change('beds-presence','awake');assert.match(text(get('beds-results')),/1 of 14/);
assert(get('beds-person-r1'));assert(!get('beds-person-r0'));
change('beds-agent','muse');assert(get('beds-person-r1'));
search('fern');assert.match(text(get('beds-results')),/0 of 14/);
assert.match(text(root),/No residents match/);
change('beds-presence','stopped');change('beds-agent','codex');search('Willow');
assert.match(text(get('beds-results')),/1 of 14/);assert(get('beds-person-r0'));
assert.match(text(root),/stopped without sleep/);
get('beds-reset').listeners.click();assert.equal(get('beds-agent').value,'all');
assert.equal(get('beds-presence').value,'all');assert.equal(get('beds-search').value,'');
assert.equal(document.activeElement,get('beds-search'));
change('beds-presence','asleep');assert.match(text(get('beds-results')),/12 of 14/);
get('beds-next').listeners.click();assert.equal(bedsState.page,1);
assert.equal(document.activeElement,get('beds-list'));assert(get('beds-next').disabled);
change('beds-agent','opencode');assert.equal(bedsState.page,0);assert(get('beds-person-r2'));
assert.equal(JSON.stringify(frame),before);assert.equal(JSON.stringify(dormView(frame,1)),bunks);
''')

    def test_unknown_fields_are_not_treated_as_awake_and_names_stay_literal(self):
        self.run_renderer(r'''
frame.residents=[{id:'odd',name:'<script>literal</script>',agent:'future-kind',presence:'something new'},
 {id:'missing',name:'No badge'},{id:'stopped',name:'Interrupted',pose:'unconfirmed',presence:'recorded awake'}];
show();const change=(id,value)=>{get(id).value=value;get(id).listeners.change();};
change('beds-agent','unrecorded');assert.match(text(get('beds-results')),/3 of 3/);
change('beds-presence','unknown');assert.match(text(get('beds-results')),/2 of 3/);
assert.match(text(root),/presence unrecorded/);assert.match(text(root),/<script>literal/);
assert(!all(root).some(n=>n.tag==='script'));
change('beds-presence','awake');assert.match(text(get('beds-results')),/0 of 3/);
change('beds-presence','stopped');assert(get('beds-person-stopped'));
''')

    def test_history_refresh_and_absent_matches_preserve_filters(self):
        self.run_renderer(r'''
people[0].agent='muse';show();
const change=(id,value)=>{get(id).value=value;get(id).listeners.change();};
change('beds-agent','muse');change('beds-presence','stopped');search('Willow');
const card=get('beds-person-r0');card.open=true;card.listeners.toggle();
for(const changed of [false,true]) {
 get('beds-agent').focus();refreshView(changed);
 assert.equal(document.activeElement,get('beds-agent'));assert.equal(get('beds-agent').value,'muse');
 assert.equal(get('beds-presence').value,'stopped');assert(get('beds-person-r0').open);
 get('beds-presence').focus();refreshView(changed);
 assert.equal(document.activeElement,get('beds-presence'));
}
// Later identity information must not be borrowed when going back in time.
data.frames[0]={...data.frames[0],residents:[{id:'r0',name:'Willow',agent:'codex',presence:'recorded awake'}]};
get('beds-event-end-run0').listeners.click();assert.equal(frame.seq,20);
assert.equal(get('beds-agent').value,'muse');assert.equal(get('beds-presence').value,'stopped');
assert.equal(get('beds-search').value,'Willow');assert.match(text(get('beds-results')),/0 of 1/);
get('beds-reset').listeners.click();assert(get('beds-person-r0'));assert.doesNotMatch(text(root),/Fern/);
index=2;current=true;render();assert.match(text(get('beds-results')),/14 of 14/);
''')


if __name__ == '__main__':
    unittest.main()
