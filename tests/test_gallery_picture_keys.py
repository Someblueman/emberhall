"""Keyboard browsing in the shipped dialog; native scrolling needs a browser."""
import unittest
from tests import test_gallery_picture as picture


@unittest.skipUnless(picture.shutil.which('node'), 'Node executes the renderer')
class GalleryPictureKeyTests(unittest.TestCase):
    run_renderer = picture.GalleryPictureTests.run_renderer

    def test_arrow_and_endpoint_navigation_keep_focus_and_reset_changed_picture(self):
        self.run_renderer(r'''
show();const opener=openPicture(),dialog=get('gallery-picture');
assert.equal(dialog.attrs['aria-describedby'],'gallery-picture-help');
assert.match(text(dialog),/Left and Right.*Home and End/);
const scroll=get('gallery-picture-scroll');scroll.contains=node=>all(scroll).includes(node);
const pictures=completedCatalog().filter(e=>creationPreview(e)),count=pictures.length;
const position=(index)=>`Picture ${index} of ${count} · ${pictures[index-1].title}`;
const key=(key,extra={})=>{const e={key,target:document.activeElement,
 prevented:false,preventDefault(){this.prevented=true;},...extra};
 dialog.listeners.keydown(e);return e.prevented;};
get('gallery-picture-next').focus();
assert(key('ArrowRight'));assert.equal(get('gallery-picture-title').textContent,'Lantern Loop');
assert.equal(document.activeElement,get('gallery-picture-next'));
get('gallery-picture-size').listeners.click();scroll.scrollLeft=200;
assert(key('End'));assert.equal(get('gallery-picture-position').textContent,position(count));
assert.equal(get('gallery-picture-size').attrs['aria-pressed'],'false');
assert.equal(scroll.scrollLeft,0);
get('gallery-picture-size').listeners.click();scroll.scrollTop=75;
assert(key('End'));assert.equal(get('gallery-picture-size').attrs['aria-pressed'],'true');
assert.equal(scroll.scrollTop,75,'Staying on the same picture preserves its zoom and scroll');
assert(key('Home'));assert.equal(get('gallery-picture-position').textContent,position(1));
assert(key('ArrowLeft'));assert.equal(get('gallery-picture-position').textContent,position(count));
assert(key('ArrowRight'));assert.equal(get('gallery-picture-position').textContent,position(1));
show();get('gallery-picture').close();assert.equal(document.activeElement,get(opener.id));
''')

    def test_scrolling_modified_and_handled_keys_stay_with_the_browser(self):
        self.run_renderer(r'''
show();openPicture();const dialog=get('gallery-picture'),scroll=get('gallery-picture-scroll');
scroll.contains=node=>all(scroll).includes(node);
const key=(key,target,extra={})=>{const e={key,target,prevented:false,
 preventDefault(){this.prevented=true;},...extra};dialog.listeners.keydown(e);return e.prevented;};
const image=all(scroll).find(n=>n.tag==='img'),close=get('gallery-picture-close');
const before=get('gallery-picture-position').textContent;
for(const target of [scroll,image])for(const k of ['ArrowLeft','ArrowRight','Home','End'])
 assert.equal(key(k,target),false,'The picture region keeps its own scrolling keys');
for(const flag of ['altKey','ctrlKey','metaKey','shiftKey','isComposing','defaultPrevented'])
 assert.equal(key('ArrowRight',close,{[flag]:true}),false);
for(const k of ['Tab','Escape','ArrowUp','ArrowDown','Enter',' '])assert.equal(key(k,close),false);
assert.equal(get('gallery-picture-position').textContent,before);
catalog=catalog.filter(p=>p.id==='tessera-loom');renderCollection();
assert.equal(key('ArrowRight',close),false,'A single picture has nowhere to browse');
assert.match(get('gallery-picture-position').textContent,/Picture 1 of 1/);
''')
