"""Run-history paging through the shipped Beds renderer."""
import shutil
import unittest

from tests import test_beds_directory as directory


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class BedsRunTests(unittest.TestCase):
    run_renderer = directory.BedsDirectoryTests.run_renderer

    def test_pages_reach_every_run_once_and_keep_residents_independent(self):
        self.run_renderer(r'''
const records=Array.from({length:14},(_,i)=>({...runs[0],id:'stay'+i,
 sequence:30+i,last_sequence:50+i,start:3000+i,end:4000+i}));
frame={...frame,seq:100,runs:[...records,...records.map(r=>({...r,id:'other-'+r.id,resident:'r1'}))]};
const before=JSON.stringify(frame);show();
const visible=id=>all(get('beds-runs-'+id)).filter(n=>n.tag==='code').map(n=>n.textContent);
assert.equal(visible('r0').join(','),'stay13,stay12,stay11,stay10,stay9,stay8');
assert.match(text(get('beds-runs-status-r0')),/14 recorded runs.*1–6 shown.*latest start first/);
assert(get('beds-runs-newer-r0').disabled);assert(!get('beds-runs-older-r0').disabled);
let seen=[...visible('r0')];get('beds-runs-older-r0').listeners.click();
assert.equal(document.activeElement,get('beds-runs-r0'));
assert.match(text(get('beds-runs-status-r0')),/7–12 shown/);seen.push(...visible('r0'));
assert.equal(visible('r1').join(','),'other-stay13,other-stay12,other-stay11,other-stay10,other-stay9,other-stay8');
get('beds-runs-older-r0').listeners.click();seen.push(...visible('r0'));
assert(get('beds-runs-older-r0').disabled);assert.match(text(get('beds-runs-status-r0')),/13–14 shown/);
assert.equal(seen.length,14);assert.equal(new Set(seen).size,14);
get('beds-runs-newer-r0').listeners.click();assert.match(text(get('beds-runs-status-r0')),/7–12 shown/);
assert.equal(JSON.stringify(frame),before);
''')

    def test_refresh_history_bounds_and_receipt_visits(self):
        self.run_renderer(r'''
const records=Array.from({length:13},(_,i)=>({...runs[0],id:'stay'+i,
 sequence:30+i,last_sequence:50+i,start:3000+i,end:4000+i}));
data.frames=[{...frame,seq:50,runs:records.slice(0,1)},
 {...frame,seq:62,runs:records}];index=1;frame=data.frames[1];show();search('fern');
const card=get('beds-person-r0');card.open=true;card.listeners.toggle();
get('beds-runs-older-r0').listeners.click();
for(const changed of [false,true]) {
 get('beds-runs-older-r0').focus();refreshView(changed);
 assert.equal(document.activeElement,get('beds-runs-older-r0'));
 assert(get('beds-person-r0').open);assert.match(text(get('beds-runs-status-r0')),/7–12 shown/);
}
get('beds-runs-older-r0').listeners.click();
assert(get('beds-event-end-stay0'));get('beds-event-end-stay0').listeners.click();
assert.equal(frame.seq,50);assert.equal(current,false);
assert.equal(document.activeElement,get('beds-name-r0'));
assert.match(text(get('beds-runs-status-r0')),/1 recorded run.*1–1 shown/);
assert.equal(all(root).filter(n=>n.className==='beds-run').length,1);
assert(!get('beds-event-end-stay12'));
assert(!get('beds-runs-older-r0'),'One page needs no paging controls');
// Even an over-complete input frame may not leak future-started runs.
frame={...frame,runs:[...records,{...records[0],id:'future',sequence:100}]};show();
assert(!text(root).includes('future'));assert.match(text(get('beds-runs-status-r0')),/13 recorded runs/);
''')

    def test_empty_history_and_literal_resident_names(self):
        self.run_renderer(r'''
frame={...frame,residents:[{...people[0],name:'<img src=x>'}],runs:[]};show();
assert.match(text(root),/No supervised run receipts/);assert(!get('beds-runs-older-r0'));
assert(!all(root).some(n=>n.tag==='img'));
assert.equal(get('beds-runs-r0').attrs['aria-label'],'Run history for <img src=x>');
''')


if __name__ == '__main__':
    unittest.main()
