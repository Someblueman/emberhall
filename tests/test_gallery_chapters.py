"""Completed chapters use recorded stage evidence without completing their work."""
import unittest
from tests import test_gallery_picture as picture


@unittest.skipUnless(picture.shutil.which('node'), 'Node executes the renderer')
class GalleryChapterTests(unittest.TestCase):
    run_renderer = picture.GalleryPictureTests.run_renderer

    def test_completed_opening_appears_in_collection_and_room(self):
        self.run_renderer(r'''
const chapter=manifest.projects.find(p=>p.id==='every-promise-two-endings')||
 {id:'every-promise-two-endings',title:'Every Promise Has Two Endings — Opening chapter',
 summary:'The weight of morning. A complete opening chapter; the remaining acts are unwritten.',
 category:'creation',action:'Play',href:'projects/every-promise-two-endings/index.html',
 files:['projects/every-promise-two-endings/index.html']};
catalog=[...catalog.filter(p=>p.id!==chapter.id),chapter];
const receipt={stage:0,sequence:80,evidence:'reviewed-opening',milestone:'The bridge and its next morning.'};
const project={id:'long-story',idea:chapter.id,status:'active',stage:1,completed:[receipt]};
frame.shelf.projects.push(project);
const before=JSON.stringify({frame,catalog});
assert.equal(completedCatalog()[0].id,chapter.id);
nodes.creations=root;renderCollection();
const card=all(root).find(n=>n.tag==='article'&&text(n).includes(chapter.title));
assert(card);assert.match(text(card),/Completed opening chapter · Longer work continues/);
assert.match(text(card),/Recorded at event 80 · Evidence: reviewed-opening/);
assert.match(text(card),/The bridge and its next morning/);
assert.equal(all(card).find(n=>n.tag==='a').href,chapter.href);
assert.equal(project.status,'active');
show();assert.equal(galleryRoomChoice,chapter.id);
assert.match(text(root),/Completed opening chapter · Longer work continues/);
assert.equal(all(root).find(n=>n.className==='creation-action').href,chapter.href);
assert.equal(JSON.stringify({frame,catalog}),before,'Rendering preserves records and catalog');
// Finishing later stages must neither redate nor expand this opening entry.
project.status='done';project.completed.push({...receipt,stage:2,sequence:89});
frame.shelf.projects.push({id:'new-poem',idea:'bench-for-two',status:'done',completed:[{sequence:85}]});
assert.deepEqual(Array.from(completedCatalog().slice(0,2),e=>e.id),['bench-for-two',chapter.id]);
renderCollection();
assert.match(text(root),/Completed opening chapter/);
assert.doesNotMatch(text(root),/Longer work continues/);
''')

    def test_unfinished_unregistered_and_invalid_stage_evidence_stay_out(self):
        self.run_renderer(r'''
const entry={id:'every-promise-two-endings',title:'Opening chapter',summary:'The remaining acts are unwritten.',
 category:'creation',action:'Play',href:'projects/every-promise-two-endings/index.html',files:[]};
catalog=[entry];
const receipt={stage:0,sequence:80,evidence:'reviewed-opening',milestone:'Completed opening'};
const project={id:'story',idea:entry.id,status:'active',completed:[receipt]};
frame.shelf.projects=[project];
for(const completed of [[],[{...receipt,stage:1}],[{...receipt,sequence:91}],
 [{...receipt,sequence:'80'}],[{...receipt,sequence:0}],[{...receipt,evidence:' '}],
 [{...receipt,milestone:''}]]) {
 project.completed=completed;assert.equal(completedCatalog().length,0);
}
project.completed=[receipt];project.status='dropped';assert.equal(completedCatalog().length,0);
project.status='done';project.completed=[];assert.equal(completedCatalog().length,0);
project.status='active';project.completed=[receipt];
frame.seq=undefined;assert.equal(completedCatalog().length,0);frame.seq=90;
assert.equal(completedCatalog().length,1);
catalog=[{...entry,id:'unfinished-sample'}];project.idea='unfinished-sample';
assert.equal(completedCatalog().length,0,'A receipt alone does not register a chapter');
catalog=[];assert.equal(completedCatalog().length,0);
''')

    def test_historical_boundary_and_completion_order(self):
        self.run_renderer(r'''
const entry={id:'every-promise-two-endings',title:'Opening chapter',summary:'A chapter of a longer story.',
 category:'creation',action:'Play',href:'projects/every-promise-two-endings/index.html',files:[]};
catalog=[...catalog.filter(p=>p.id!==entry.id),entry];
const receipt={stage:0,sequence:80,evidence:'reviewed-opening',milestone:'The complete opening'};
const story={id:'story',idea:entry.id,status:'active',completed:[receipt]};
const poem={id:'poem',idea:'bench-for-two',status:'done',completed:[{sequence:70}]};
data={frames:[{seq:79,shelf:{projects:[{...story,completed:[]},poem]}},
 {seq:80,shelf:{projects:[story,poem]}},
 {seq:81,shelf:{projects:[{...story,status:'done'},poem]}}]};
current=false;frame={...frame,seq:79,shelf:{projects:[story,poem]}};
assert(!completedCatalog().some(e=>e.id===entry.id),'Even a future receipt cannot leak backward');
frame=data.frames[1];
assert.deepEqual(Array.from(completedCatalog(),e=>e.id),[entry.id,'bench-for-two']);
nodes.creations=root;renderCollection();
assert.match(text(root),/current published versions/);
assert.match(text(root),/Completed opening chapter · Longer work continues/);
frame=data.frames[2];
assert.equal(completedCatalog()[0].completedChapter.sequence,80,'Whole-work closure cannot date a chapter');
''')

    def test_first_colour_legend_requires_its_own_completed_stage(self):
        self.run_renderer(r'''
const legend=manifest.projects.find(p=>p.id==='what-a-blended-colour-can-say');
assert(legend,'The first legend must be published in the manifest');
catalog=[legend];
const receipt={stage:0,sequence:80,evidence:'blended-colour-m1-verify',milestone:'Checked model and first vector legend'};
const project={id:'great-rook-20261121',idea:legend.id,status:'active',stage:1,completed:[]};
frame.shelf.projects=[project];
assert.equal(completedCatalog().length,0,'An active project alone is not a completed legend');
for(const invalid of [{...receipt,stage:1},{...receipt,sequence:91},{...receipt,evidence:''}]) {
 project.completed=[invalid];assert.equal(completedCatalog().length,0);
}
project.completed=[receipt];
assert.equal(completedCatalog()[0].id,legend.id);
nodes.creations=root;renderCollection();
assert.match(text(root),/Completed first legend · Longer work continues/);
assert.match(text(root),/Milestone completion record/);
assert.doesNotMatch(text(root),/Completed opening chapter/);
assert.equal(all(root).find(n=>n.className==='creation-action').href,legend.href);
const preview=all(root).find(n=>n.tag==='img');
assert(preview,'The first colour legend should display its verified example SVG');
assert.equal(preview.src,'projects/what-a-blended-colour-can-say/legends/example.svg');
frame.seq=79;assert.equal(completedCatalog().length,0,'No receipt appears before it happened');
''')
