"""Newest finished work leads the real Gallery without losing a reader's place."""
import unittest
from tests import test_gallery_picture as picture


@unittest.skipUnless(picture.shutil.which('node'), 'Node executes the renderer')
class GalleryCompletionOrderTests(unittest.TestCase):
    run_renderer = picture.GalleryPictureTests.run_renderer

    def test_recorded_completion_orders_cards_room_and_pictures(self):
        self.run_renderer(r'''
const project=(id,idea,status,completed)=>({id,idea,status,...(completed?{completed}: {})});
const old=project('tiles','tessera-loom','done');
const film=project('film','lantern-loop','done');
const poem=project('poem','bench-for-two','done');
data={frames:[
 {seq:1,shelf:{projects:[project('tiles','tessera-loom','active')]}},
 {seq:2,shelf:{projects:[old]}},
 {seq:3,shelf:{projects:[old,project('film','lantern-loop','active')]}},
 {seq:4,shelf:{projects:[old,film]}},
 {seq:5,shelf:{projects:[old,film,project('poem','bench-for-two','active')]}},
 {seq:6,shelf:{projects:[old,film,poem]}}
]};
frame={...frame,seq:6,shelf:{projects:[old,film,poem]}};
const before=JSON.stringify(data);
assert.deepEqual(Array.from(completedCatalog(),p=>p.id),['bench-for-two','lantern-loop','tessera-loom']);
show();assert.match(images()[0].src,/bench-for-two/);
nodes.creations=root;renderCollection();
assert.equal(all(root).filter(n=>n.tag==='article')[0].children[0].textContent,'The Bench Was for Two');
openPicture();get('gallery-picture-next').listeners.click();
assert.equal(get('gallery-picture-title').textContent,'Lantern Loop');
get('gallery-picture').close();
current=false;frame=data.frames[3];galleryRoomChoice=null;show();
assert.equal(galleryRoomChoice,'lantern-loop');assert.equal(images().length,0);
assert(!completedCatalog().some(p=>p.id==='bench-for-two'));
assert.equal(JSON.stringify(data),before,'Sorting must not rewrite published history');
''')

    def test_missing_gapped_and_tied_records_keep_stable_catalog_order(self):
        self.run_renderer(r'''
data={frames:[
 {seq:10,shelf:{projects:[{id:'tiles',idea:'tessera-loom',status:'done'}]}},
 {seq:20,shelf:{projects:[{id:'tiles',idea:'tessera-loom',status:'done'},
  {id:'film',idea:'lantern-loop',status:'done'}]}}
]};
frame={...frame,seq:90,shelf:{projects:[
 {id:'tiles',idea:'tessera-loom',status:'done'},
 {id:'film',idea:'lantern-loop',status:'done'},
 {id:'poem',idea:'bench-for-two',status:'active'},
 {id:'packing',idea:'five-mark-packing',status:'done',completed:[{sequence:70},{sequence:80}]},
 {id:'garden',idea:'signal-garden',status:'done',completed:[{sequence:80}]},
 {id:'future',idea:'night-ferry',status:'done',completed:[{sequence:100}]},
 {id:'bad',idea:'cue-rehearsal',status:'done',completed:[{sequence:'89'},{sequence:-1}]}
]}};
assert.deepEqual(Array.from(completedCatalog(),p=>p.id),[
 'signal-garden','five-mark-packing','tessera-loom','lantern-loop','night-ferry','cue-rehearsal']);
// A later duplicate record cannot erase the valid completion receipt.
frame.shelf.projects.push({id:'older',idea:'five-mark-packing',status:'done',completed:[{sequence:30}]});
assert.equal(completedCatalog()[1].id,'five-mark-packing');
data=undefined;
assert.equal(completedCatalog()[0].id,'signal-garden');
frame.shelf.projects=frame.shelf.projects.map(p=>({...p,completed:undefined}));
assert.equal(completedCatalog()[0].id,'tessera-loom');
''')

    def test_refresh_keeps_selected_work_and_open_picture(self):
        self.run_renderer(r'''
data={frames:[]};show();get('gallery-room-next').listeners.click();
assert.equal(galleryRoomChoice,'lantern-loop');
const opener=openPicture(),dialog=get('gallery-picture');
get('gallery-picture-next').focus();
frame.shelf.projects=frame.shelf.projects.map(p=>({...p,
 completed:[{sequence:p.idea==='bench-for-two'?89:p.idea==='lantern-loop'?88:1}]}));
show();assert.equal(galleryRoomChoice,'lantern-loop');
assert.equal(get('gallery-picture'),dialog);
assert.equal(get('gallery-picture-title').textContent,'Lantern Loop');
assert.match(get('gallery-picture-position').textContent,/Picture 2 of/);
assert.equal(document.activeElement,get('gallery-picture-next'));
get('gallery-picture').close();
assert.equal(document.activeElement,get(opener.id));
get('gallery-room-previous').listeners.click();assert.equal(galleryRoomChoice,'bench-for-two');
''')
