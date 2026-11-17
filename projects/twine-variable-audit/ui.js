(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  let result = null, fileVersion = 0, lastSourceTrigger = null;
  function el(tag,text,cls) {
    const node = document.createElement(tag); if (text !== undefined) node.textContent = text;
    if (cls) node.className = cls; return node;
  }
  function status(text,partial = false) { $('status').textContent = text; $('status').className = partial ? 'partial' : ''; }
  function clearReport() { result = null; $('report').hidden = true; $('source-panel').hidden = true; }
  function changed() { fileVersion++; clearReport(); status('Story changed. Check it to see a fresh report.'); }
  function showSource(name,line = 1) {
    const p = result?.passages.find(p => p.name === name); if (!p) return;
    $('source-panel').hidden = false; $('source-title').textContent = name;
    $('source-note').textContent = 'Line ' + line + ' in the decoded passage text. Highlighted text is displayed as source, never rendered.';
    const source = $('source'); source.replaceChildren();
    p.text.split('\n').forEach((text,i) => source.append(el(i+1 === line ? 'mark' : 'span',String(i+1).padStart(3,' ') + '  ' + text)));
    $('source-title').focus();
    source.querySelector('mark')?.scrollIntoView({block:'nearest'});
  }
  function sourceButton(name,line,label) {
    const b = el('button',label || name + ' · line ' + line,'secondary');
    b.type = 'button'; b.addEventListener('click',() => { lastSourceTrigger = b; showSource(name,line); }); return b;
  }
  function render() {
    $('report').hidden = false; $('findings').replaceChildren(); $('unchecked').replaceChildren();
    const unset = result.findings.filter(f => f.kind === 'unset').length;
    const cases = result.findings.filter(f => f.kind === 'case').length;
    status((result.complete ? 'Supported routes checked' : 'Partly checked') + ' · ' + unset + ' possible unset read' + (unset === 1 ? '' : 's') + ' · ' + cases + ' name comparison' + (cases === 1 ? '' : 's'),!result.complete);
    $('counts').textContent = result.name + ' · ' + result.states + ' distinct passage states explored. Start: ' + result.start + '. Findings are suggestions to inspect, not automatic fixes.';
    if (!result.findings.length) $('findings').append(el('p',result.complete ? 'No variable findings on the supported routes. This does not check every SugarCube feature.' : 'No variable findings in the part checked. Read the unchecked list before drawing a conclusion.'));
    for (const f of result.findings) {
      const article = el('article',undefined,'finding');
      article.append(el('div',f.kind === 'case' ? 'Possible spelling mismatch' : 'Possible read before a value was set','tag'));
      if (f.kind === 'case') {
        article.append(el('h3',f.names.join(' / ')),el('p','These names differ only in letter case. This compares source spellings, including unvisited branches; it does not say they must be the same variable.'));
        for (const location of f.locations) {
          article.append(sourceButton(location.passage,location.line,location.name + ' in ' + location.passage + ' · line ' + location.line));
          if (location.path) {
            const details = el('details'); details.append(el('summary','A route to ' + location.name + ' here'));
            const route = el('ol',undefined,'route');
            location.path.forEach((name,i) => { const li = el('li'); li.append(sourceButton(name,i === location.path.length-1 ? location.line : 1)); route.append(li); });
            details.append(route); article.append(details);
          } else article.append(el('p','No supported execution of this occurrence was reached; this spelling is compared as source text only.','quiet'));
        }
      } else {
        article.append(el('h3',f.name + ' in ' + f.passage + ' · line ' + f.line),el('p','No defined value was found on this supported route. Check whether that is intentional.'));
        article.append(sourceButton(f.passage,f.line,'Show this line'));
        const list = el('ol',undefined,'route');
        f.path.forEach((name,i) => { const li = el('li'); li.append(sourceButton(name,i === f.path.length-1 ? f.line : 1)); list.append(li); });
        article.append(el('h3','One route to the read'),list);
        if (f.decisions.length) {
          const details = el('details'); details.append(el('summary','Conditions along this route'));
          for (const d of f.decisions) details.append(el('p',d.passage + ' · line ' + d.line + ': ' + (d.taken ? 'branch taken' : 'condition false')));
          article.append(details);
        }
      }
      $('findings').append(article);
    }
    if (!result.unchecked.length) $('unchecked').append(el('p','No skipped syntax or exhausted limits were found within this checker’s documented scope.'));
    if (result.unchecked.length > 200) $('unchecked').append(el('p','Showing the first 200 of ' + result.unchecked.length + ' unchecked items. This story is only partly checked.'));
    for (const item of result.unchecked.slice(0,200)) {
      const p = el('p',item.reason + ' ');
      if (result.passages.some(x => x.name === item.passage)) p.append(sourceButton(item.passage,item.line));
      else p.append(el('strong',item.passage));
      $('unchecked').append(p);
    }
  }
  $('back-report').addEventListener('click',() => { if (lastSourceTrigger?.isConnected) lastSourceTrigger.focus(); else $('report-title').focus(); });
  $('story-input').addEventListener('input',changed);
  $('audit').addEventListener('click',() => {
    clearReport();
    try { result = TwineAudit.audit($('story-input').value); render(); $('editor').open = false; }
    catch (error) { status('Not checked: ' + error.message,true); }
    $('report-title').focus();
  });
  $('clear').addEventListener('click',() => { $('story-input').value = ''; $('story-file').value = ''; changed(); status('Story cleared. Your report will appear here.'); $('editor').open = true; $('story-input').focus(); });
  $('load-example').addEventListener('click',() => { $('story-input').value = TWINE_EXAMPLES[$('example').value]; $('story-file').value = ''; changed(); status('Example loaded. Choose “Check story” to see its report.'); $('editor').open = true; $('story-input').focus(); });
  $('story-file').addEventListener('change',async () => {
    const file = $('story-file').files[0]; if (!file) return;
    changed(); const version = fileVersion;
    $('story-input').value = '';
    if (file.size > 2000000) { status('Not checked: local file exceeds two million bytes.',true); return; }
    try {
      const text = await file.text();
      if (version !== fileVersion) return;
      $('story-input').value = text; status('File loaded as text. Choose “Check story” to see its report.');
    } catch { if (version === fileVersion) status('Could not read the local file. Paste its HTML instead.',true); }
  });
})();
