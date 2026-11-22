"""Picture-view behavior in the actual Gallery renderer; native keys need a browser."""
from pathlib import Path
import shutil
import subprocess
import unittest

from tests.test_gallery_room import HARNESS

ROOT = Path(__file__).resolve().parents[1]
PICTURE_DOM = r'''
vm.runInContext(`
const append=Element.prototype.appendChild;
Element.prototype.appendChild=function(node){node.parentNode=this;return append.call(this,node);};
Element.prototype.getAttribute=function(key){return this.attrs[key]??null;};
Element.prototype.remove=function(){this.parentNode.children=this.parentNode.children.filter(node=>node!==this);};
Element.prototype.showModal=function(){this.open=true;all(this).find(node=>node.autofocus)?.focus();};
Element.prototype.close=function(){if(!this.open)return;this.open=false;this.listeners.close?.();};
Object.defineProperty(Element.prototype,'classList',{get(){return {toggle:(name,on)=>{
 this.className=(this.className||'').split(' ').filter(value=>value&&value!==name).concat(on?[name]:[]).join(' ');
}};}});
document.body=new Element('body');
const previousGet=document.getElementById;
document.getElementById=id=>previousGet(id)||all(document.body).find(node=>node.id===id)||null;
const pictureButton=()=>all(root).find(node=>node.className==='creation-picture-open');
const openPicture=()=>{const button=pictureButton();button.focus();button.listeners.click();return button;};
`,ctx);
'''


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class GalleryPictureTests(unittest.TestCase):
    def run_renderer(self, checks):
        result = subprocess.run(
            ['node', '-e', HARNESS + PICTURE_DOM + '\nvm.runInContext(' + repr(checks) + ',ctx);',
             str(ROOT / 'site/house.js'), str(ROOT / 'site/projects.json')],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_picture_credit_size_controls_and_return_after_redraw(self):
        self.run_renderer(r'''
show();const originalButton=openPicture(),dialog=get('gallery-picture');
assert(dialog.open);assert.equal(dialog.attrs['aria-labelledby'],'gallery-picture-title');
assert.equal(document.activeElement,get('gallery-picture-close'));
assert.match(originalButton.attrs['aria-label'],/Look closely at Tessera Loom/);
assert.equal(originalButton.attrs['aria-haspopup'],'dialog');
const large=all(dialog).find(node=>node.tag==='img'),small=images()[0];
assert.equal(large.src,small.src);assert.equal(large.alt,small.alt);
assert.equal(large.width,1600);assert.match(text(dialog),/Made in Tessera Loom/);
assert.equal(all(dialog).find(node=>node.tag==='a').href,'projects/tessera-loom/index.html');
const size=get('gallery-picture-size'),scroll=get('gallery-picture-scroll');
size.listeners.click();assert.equal(size.attrs['aria-pressed'],'true');
assert.match(scroll.className,/original-size/);assert.match(size.textContent,/Fit picture/);
size.listeners.click();assert.equal(size.attrs['aria-pressed'],'false');
assert.doesNotMatch(scroll.className,/original-size/);
show();assert.notEqual(pictureButton(),originalButton);
get('gallery-picture-close').listeners.click();
assert.equal(creationPicture,null);assert.equal(get('gallery-picture'),null);
assert.equal(document.activeElement,pictureButton());
openPicture();get('gallery-picture').close();assert.equal(document.activeElement,pictureButton());
''')

    def test_history_and_removed_publication_clear_open_picture(self):
        self.run_renderer(r'''
show();openPicture();current=false;show();
assert.equal(creationPicture,null);assert.equal(all(document.body).filter(n=>n.tag==='img').length,0);
assert.equal(pictureButton(),undefined);assert.equal(images().length,0);
current=true;show();openPicture();catalog=[];renderCollection();
assert.equal(creationPicture,null);assert.equal(get('gallery-picture'),null);
catalog=manifest.projects;show();openPicture();
catalog=catalog.map(entry=>({...entry,files:[]}));renderCollection();
assert.equal(creationPicture,null);
for(const files of [{},'projects/tessera-loom/gallery-preview.svg',null]){
 catalog=manifest.projects;show();openPicture();
 catalog=catalog.map(entry=>({...entry,files}));renderCollection();assert.equal(creationPicture,null);
}
''')

    def test_unlisted_and_unsafe_previews_have_no_picture_button(self):
        self.run_renderer(r'''
const first=manifest.projects[0];
for(const overrides of [{files:[]},{files:['https://evil.test/gallery-preview.svg']},{href:'javascript:evil()'}]){
 catalog=[{...first,...overrides}];show();
 assert.equal(pictureButton(),undefined);assert.equal(images().length,0);
}
catalog=[{...first,title:'<img src=x onerror=evil()>'}];show();openPicture();
assert.equal(get('gallery-picture-title').textContent,'<img src=x onerror=evil()>');
assert.equal(all(document.body).filter(n=>n.tag==='img').length,1);
''')

    def test_dance_picture_waits_for_completion_and_listed_asset(self):
        self.run_renderer(r'''
const dance={id:'last-dance-school',title:'The Last Dance School',category:'creation',action:'Play',
 summary:'Teach a dance and watch it travel.',href:'projects/last-dance-school/index.html',
 files:['projects/last-dance-school/index.html','projects/last-dance-school/gallery-preview.svg']};
catalog=[dance];frame.shelf.projects=[{idea:dance.id,status:'active'}];show();
assert.equal(pictureButton(),undefined);assert.equal(images().length,0);
frame.shelf.projects[0].status='done';show();
assert.equal(images().length,1);assert.equal(images()[0].src,dance.files[1]);
assert.match(images()[0].alt,/Lio.*Bea/);
const opener=openPicture(),dialog=get('gallery-picture');
assert.equal(all(dialog).find(n=>n.tag==='img').src,dance.files[1]);
assert.equal(all(dialog).find(n=>n.tag==='a').href,dance.href);
assert.match(text(dialog),/Play The Last Dance School/);
dialog.close();assert.equal(document.activeElement,opener);
current=false;show();assert.equal(pictureButton(),undefined);assert.equal(images().length,0);
current=true;catalog=[{...dance,files:[dance.href]}];show();
assert.equal(pictureButton(),undefined);assert.equal(images().length,0);
''')

    def test_browse_pictures_updates_credit_link_and_resets_zoom(self):
        self.run_renderer(r'''
show();const opener=openPicture(),dialog=get('gallery-picture');
const position=get('gallery-picture-position'),next=get('gallery-picture-next');
assert.equal(position.attrs.role,'status');assert.match(position.textContent,/Picture 1 of 16/);
get('gallery-picture-size').listeners.click();
const scroll=get('gallery-picture-scroll');scroll.scrollLeft=500;scroll.scrollTop=200;
next.focus();next.listeners.click();
assert.equal(document.activeElement,next);assert.equal(get('gallery-picture'),dialog);
assert.equal(get('gallery-picture-title').textContent,'Lantern Loop');
assert.match(position.textContent,/Picture 2 of 16 · Lantern Loop/);
assert.match(text(dialog),/From Lantern Loop’s own final drawing/);
assert.equal(all(dialog).find(n=>n.tag==='a').href,'projects/lantern-loop/index.html');
assert.match(all(dialog).find(n=>n.tag==='a').textContent,/Play Lantern Loop/);
assert.match(all(dialog).find(n=>n.tag==='img').src,/lantern-loop/);
assert.equal(get('gallery-picture-size').attrs['aria-pressed'],'false');
assert.doesNotMatch(scroll.className,/original-size/);
assert.equal(scroll.scrollLeft,0);assert.equal(scroll.scrollTop,0);
assert.match(scroll.attrs['aria-label'],/Lantern Loop picture/);
get('gallery-picture-previous').listeners.click();
assert.equal(get('gallery-picture-title').textContent,'Tessera Loom');
get('gallery-picture-previous').listeners.click();
assert.match(position.textContent,/Picture 16 of 16 · You Were Supposed to Drop It/);
next.listeners.click();assert.match(position.textContent,/Picture 1 of 16/);
show();get('gallery-picture').close();assert.equal(document.activeElement,get(opener.id));
''')

    def test_browsing_rechecks_completed_manifest_and_closes_revoked_picture(self):
        self.run_renderer(r'''
show();openPicture();
frame.shelf.projects.find(p=>p.idea==='lantern-loop').status='active';
catalog=catalog.map(p=>p.id==='night-ferry'?{...p,files:[]}:p);
catalog=catalog.map(p=>p.id==='signal-garden'?{...p,href:'javascript:evil()'}:p);
renderCollection();assert.match(get('gallery-picture-position').textContent,/1 of 13/);
get('gallery-picture-next').listeners.click();
assert.equal(get('gallery-picture-title').textContent,'Specimen Cards');
catalog=catalog.filter(p=>p.id==='specimen-cards');renderCollection();
assert.match(get('gallery-picture-position').textContent,/Picture 1 of 1/);
assert(get('gallery-picture-next').disabled);assert(get('gallery-picture-previous').disabled);
catalog[0].files=[];renderCollection();assert.equal(creationPicture,null);
assert.equal(get('gallery-picture'),null);
''')

    def test_room_and_full_gallery_buttons_have_distinct_focus_targets(self):
        self.run_renderer(r'''
show();assert.match(pictureButton().id,/room-tessera-loom$/);
const full=new Element('div');full.id='creations';nodes.creations=full;document.body.appendChild(full);
galleryState.query='Tessera';renderCollection();
const fullButton=all(full).find(n=>n.className==='creation-picture-open');
assert.match(fullButton.id,/card-tessera-loom$/);
assert.notEqual(fullButton.id,pictureButton().id);
fullButton.listeners.click();renderCollection();get('gallery-picture').close();
assert.equal(galleryState.query,'Tessera');assert.equal(get('gallery-search').value,'Tessera');
assert.equal(document.activeElement,get(fullButton.id));assert.notEqual(document.activeElement,fullButton);
''')
