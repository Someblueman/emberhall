"""Compare the selected moment's ideas using the real Study renderer."""
import shutil
import unittest
from tests import test_study_room


@unittest.skipUnless(shutil.which("node"), "Node is required for the renderer")
class StudyComparisonTests(unittest.TestCase):
    run_js = test_study_room.StudyRoomTests.run_js
    def test_pair_limit_remove_clear_and_focus(self):
        self.run_js(r'''
renderStudyDesk(root,shelfData);
assert.match(text(find('study-comparison')),/0 of 2 chosen/);
find('study-compare-add-checked').listeners.click();
assert.match(text(find('study-comparison')),/1 of 2 chosen/);
assert.equal(document.activeElement,find('study-compare-add-checked'));
assert.equal(find('study-compare-add-checked')['aria-pressed'],'true');
find('study-compare-add-second').listeners.click();
assert.match(text(find('study-comparison')),/2 of 2 chosen/);
assert.equal(document.activeElement,find('study-comparison'));
assert(find('study-compare-add-research').disabled);
assert(!find('study-compare-add-second').disabled);
assert.equal(all(find('study-comparison')).filter(n=>n.scope==='col').length,2);
assert.equal(all(find('study-comparison')).filter(n=>n.scope==='row').length,8);
find('study-compare-remove-checked').listeners.click();
assert.match(text(find('study-comparison')),/1 of 2 chosen/);
assert.equal(document.activeElement,find('study-comparison'));
assert(!find('study-compare-add-research').disabled);
find('study-compare-clear').listeners.click();
assert.match(text(find('study-comparison')),/0 of 2 chosen/);
assert.equal(document.activeElement,find('study-search'));
assert(!find('study-compare-clear'));
''')

    def test_comparison_survives_search_pages_and_refresh(self):
        self.run_js(r'''
renderStudyDesk(root,shelfData);
find('study-compare-add-checked').listeners.click();
find('study-next').listeners.click();
find('study-compare-add-renew').listeners.click();
assert.match(text(find('study-comparison')),/Checked idea.*Renew idea/);
change('study-search','nothing like this','input');
assert.match(text(find('study-comparison')),/2 of 2 chosen/);
assert.match(text(root),/No ideas match/);
change('study-filter','checked','change');
root.replaceChildren();renderStudyDesk(root,shelfData);
assert.match(text(find('study-comparison')),/2 of 2 chosen/);
assert.equal(find('study-search').value,'nothing like this');
assert.equal(find('study-filter').value,'checked');
find('study-compare-remove-renew').listeners.click();
assert.match(text(find('study-comparison')),/1 of 2 chosen/);
''')

    def test_only_selected_moment_fields_and_shelved_choices_survive(self):
        self.run_js(r'''
ideas[0].brief={...brief,reach:'Future reach',risks:'Future risk'};
renderStudyDesk(root,shelfData);
find('study-compare-add-checked').listeners.click();
find('study-compare-add-second').listeners.click();
root.replaceChildren();renderStudyDesk(root,{...shelfData,ideas:[
 {...ideas[0],brief:{audience:'Earlier audience'},sources:[]},
 {...ideas[1],status:'project'},ideas[4]]});
assert.match(text(find('study-comparison')),/1 of 2 chosen/);
assert.doesNotMatch(text(find('study-comparison')),/Future reach|Future risk|Second reader idea|Outside reader/);
find('study-compare-add-empty').listeners.click();
assert.match(text(find('study-comparison')),/Earlier audience/);
assert.doesNotMatch(text(find('study-comparison')),/Future reach|Future risk|Second reader idea|Outside reader/);
assert.match(text(find('study-comparison')),/Not recorded in this snapshot/);
assert.match(text(find('study-comparison')),/No evidence recorded/);
root.replaceChildren();renderStudyDesk(root,shelfData);
assert.match(text(find('study-comparison')),/2 of 2 chosen/);
root.replaceChildren();renderStudyDesk(root,{...shelfData,ideas:[]});
assert.equal(studyState.compare.length,0);
root.replaceChildren();renderStudyDesk(root,shelfData);
assert.match(text(find('study-comparison')),/0 of 2 chosen/);
''')

    def test_text_safety_evidence_links_and_unknown_assessment(self):
        self.run_js(r'''
Object.assign(ideas[0],{id:'a / ☃',title:'<img src=x onerror=alert(1)>',plain:'Literal <script> text',
 sources:['https://example.org/read','https://example.org/read','javascript:alert(1)','https://user:secret@example.org/'],
 brief:{for:'house',asked:[{who:'House record',said:'Keep the original failure',where:'event 10'}]}});
renderStudyDesk(root,shelfData);
find('study-compare-add-'+encodeURIComponent(ideas[0].id)).listeners.click();
find('study-compare-add-second').listeners.click();
const panel=find('study-comparison');
assert.equal(all(panel).filter(n=>n.tag==='img'||n.tag==='script').length,0);
assert.match(text(panel),/Literal <script> text/);
assert.match(text(panel),/House record.*event 10/);
const links=all(panel).filter(n=>n.tag==='a');
assert.equal(links.length,2);assert.equal(links[0].href,'https://example.org/read');
assert.equal(links[0].rel,'noopener noreferrer');assert.equal(links[0].target,'_blank');
assert.match(text(root),/Evidence checked/);
assert.doesNotMatch(text(root),/Checked means another resident|Checked by another resident/);
change('study-filter','unknown','change');
assert.match(text(find('study-ideas')||root),/Earlier idea/);
''')

    def test_comparison_header_shows_scale_field_and_keeps(self):
        self.run_js(r'''
ideas[0].scale='great';
ideas[0].brief={...brief,field:'mathematics'};
ideas[0].keeps=[{author:'r1',kind:'codex',finding:'Checked'},{author:'r2',kind:'muse',finding:'Checked'}];
ideas[1].scale='small';
ideas[1].brief={...brief,field:'art'};
renderStudyDesk(root,shelfData);
find('study-compare-add-checked').listeners.click();
find('study-compare-add-second').listeners.click();
const panel=find('study-comparison');
assert.equal(all(panel).filter(n=>n.scope==='row').length,8);
const cols=all(panel).filter(n=>n.scope==='col');
assert.match(text(cols[0]),/Great work.*mathematics.*kept by 2/);
assert.match(text(cols[1]),/Small project.*art/);
''')
