// Exercise the script from the shipped page with real WebCrypto. This models
// form controls, not layout, trusted clicks, clipboard access or a browser.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { webcrypto } = require('node:crypto');
const vm = require('node:vm');

const html = readFileSync(join(__dirname, 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function page(digest = webcrypto.subtle.digest.bind(webcrypto.subtle)) {
  const elements = {};
  for (const match of html.matchAll(/<([a-z]+)\b([^>]*\bid="([^"]+)"[^>]*)>([^<]*)/g)) {
    const [, tag, attrs, id, text] = match;
    const handlers = {};
    elements[id] = {
      value: '', textContent: text, disabled: /\bdisabled\b/.test(attrs),
      hidden: /\bhidden\b/.test(attrs), readOnly: /\breadonly\b/.test(attrs),
      content: tag === 'template' ? { textContent: text } : undefined,
      addEventListener: (event, fn) => { handlers[event] = fn; },
      // Call the handler even if disabled to test its guard independently.
      click: () => handlers.click(), input: () => handlers.input?.(), focus() {}, select() {},
    };
  }
  const downloads = [];
  let downloadBlob;
  const document = {
    getElementById: id => elements[id], execCommand: () => false,
    body: { appendChild() {} },
    createElement: () => ({ click() { downloads.push({ name: this.download, blob: downloadBlob }); }, remove() {} }),
  };
  const clipboard = { writeText: () => Promise.reject(Error('clipboard denied')) };
  vm.runInNewContext(script, {
    document, navigator: { clipboard },
    crypto: { getRandomValues: array => webcrypto.getRandomValues(array), subtle: { digest } },
    TextEncoder, Uint8Array, Blob,
    URL: { createObjectURL: blob => { downloadBlob = blob; return 'blob:test'; }, revokeObjectURL() {} },
    setTimeout: fn => fn(),
  });
  const fill = () => {
    elements.exposure.value = 'Synthetic code test; prompt source already read.';
    elements.prediction.value = 'A café bead 🟢\nNo physical draw.';
    elements.reasoning.value = 'Testing a receipt, not making a blinded prediction.';
  };
  return { elements, fill, document, clipboard, downloads, issue: () => elements['issue-receipt'].click() };
}

async function main() {
  const first = page();
  const e = first.elements;
  assert.equal(e.phase2.disabled, true);
  assert.equal(e['task-choice'].disabled, false);
  assert.ok(e['run-example'], 'the supplied software example must be runnable');
  assert.equal(e['run-example'].disabled, true);
  e['run-example'].click();
  assert.equal(e['example-result'].textContent, 'Not run yet.');
  assert.equal(e['supplied-prompt'].hidden, true);
  assert.equal(e['supplied-prompt'].textContent.trim(), '');
  await first.issue();
  assert.equal(e.phase2.disabled, true);
  assert.equal(e.receipt.value, '');
  assert.match(e['phase1-status'].textContent, /required/);

  first.fill();
  const original = { exposure: e.exposure.value, prediction: e.prediction.value, reasoning: e.reasoning.value };
  await first.issue();
  const receipt = JSON.parse(e.receipt.value);
  assert.equal(e.phase2.disabled, false);
  assert.equal(e['task-choice'].disabled, true);
  assert.equal(e['supplied-prompt'].hidden, false);
  assert.match(e['supplied-prompt'].textContent, /Synthetic prompt S-03/);
  assert.match(e['supplied-prompt'].textContent, /\[12,3,8,3,-2,0\]/);
  assert.equal(e['example-runner'].hidden, false);
  assert.equal(e['run-example'].disabled, false);
  e.observation.value = 'Existing manual observation';
  e['run-example'].click();
  e['run-example'].click();
  assert.equal(e['example-result'].textContent, 'Sorted: [-2,0,3,3,8,12]. 4th smallest: 3.');
  assert.equal(e.observation.value, 'Existing manual observation');
  e.observation.value = '';

  // S-04 choice selects the frequency task with its own input.
  const second = page();
  second.fill();
  second.elements['task-s04'].checked = true;
  await second.issue();
  const secondElements = second.elements;
  assert.equal(secondElements['task-choice'].disabled, true);
  assert.match(secondElements['supplied-prompt'].textContent, /Synthetic prompt S-04/);
  assert.match(secondElements['supplied-prompt'].textContent, /\[4,9,4,6,1,4\]/);
  assert.equal(secondElements['run-example'].disabled, false);
  secondElements['run-example'].click();
  assert.equal(secondElements['example-result'].textContent, 'Sorted: [1,4,4,4,6,9]. Most frequent: 4.');

  for (const name of ['exposure', 'prediction', 'reasoning']) assert.equal(e[name].readOnly, true);
  assert.equal(e['issue-receipt'].disabled, true);
  await e['copy-receipt'].click();
  assert.match(e['phase1-status'].textContent, /copy.*manually/i);
  first.document.execCommand = () => true;
  await e['copy-receipt'].click();
  assert.equal(e['phase1-status'].textContent, 'Receipt copied.');
  first.document.execCommand = () => false;
  first.clipboard.writeText = async text => { assert.equal(text, e.receipt.value); };
  await e['copy-receipt'].click();
  assert.equal(e['phase1-status'].textContent, 'Receipt copied.');
  first.clipboard.writeText = undefined;
  await e['copy-receipt'].click();
  assert.match(e['phase1-status'].textContent, /copy.*manually/i);

  e['export-report'].click();
  assert.equal(e['export-output'].textContent, '');
  assert.equal(e['download-report'].disabled, true);
  assert.match(e['phase2-status'].textContent, /non-empty/);
  e.observation.value = 'Synthetic observation: the receipt revealed the supplied text; no bead was drawn.';
  e['edit-field'].value = 'No revision of the locked prediction.';
  e['export-report'].click();
  const report = JSON.parse(e['export-output'].textContent);
  assert.deepEqual(report.phase1, original);
  assert.equal(report.receipt.hash, receipt.hash);
  assert.equal(e['download-report'].disabled, false);

  // An already-revealed receipt cannot be silently replaced. Export uses its
  // immutable snapshot, even if a script changes a read-only control's value.
  e.prediction.value = 'A hindsight replacement';
  await first.issue();
  assert.equal(e.receipt.value, JSON.stringify(receipt, null, 2));
  assert.equal(e.observation.value, report.phase2.observation);
  e['export-report'].click();
  assert.deepEqual(JSON.parse(e['export-output'].textContent), report);

  // Editing the observation or its revision invalidates the old downloadable
  // report until the trialist explicitly exports their current text again.
  for (const name of ['observation', 'edit-field']) {
    e[name].value += ' Updated after export.';
    e[name].input();
    assert.equal(e['export-output'].textContent, '');
    assert.equal(e['download-report'].disabled, true);
    e['export-report'].click();
    const updated = JSON.parse(e['export-output'].textContent);
    assert.equal(updated.phase2[name === 'edit-field' ? 'edit' : name], e[name].value);
    assert.equal(updated.receipt.hash, receipt.hash);
    assert.equal(e['download-report'].disabled, false);
  }
  assert.equal(e['export-output'].hidden, false);
  e['download-report'].click();
  assert.equal(first.downloads[0].name, 'trial-report.json');
  assert.equal(await first.downloads[0].blob.text(), e['export-output'].textContent);

  let resolveHash;
  let calls = 0;
  const delayed = page((...args) => {
    calls++;
    return new Promise(resolve => { resolveHash = () => resolve(webcrypto.subtle.digest(...args)); });
  });
  delayed.fill();
  const pending = delayed.issue();
  assert.equal(delayed.elements.phase2.disabled, true);
  assert.equal(delayed.elements['supplied-prompt'].hidden, true);
  assert.equal(delayed.elements.exposure.readOnly, true);
  assert.equal(delayed.elements['task-choice'].disabled, true);
  // Even a script changing a disabled radio during hashing must not change the
  // task captured when the prediction was locked.
  delayed.elements['task-s04'].checked = true;
  await delayed.issue();
  assert.equal(calls, 1, 'a second click must not start a competing hash');
  resolveHash();
  await pending;
  assert.equal(delayed.elements.phase2.disabled, false);
  assert.match(delayed.elements['supplied-prompt'].textContent, /Synthetic prompt S-03/);
  assert.equal(delayed.elements['task-choice'].disabled, true);

  for (const failure of [() => Promise.reject(Error('digest failed')), () => { throw Error('no WebCrypto'); }]) {
    let fail = true;
    const retry = page((...args) => fail ? failure() : webcrypto.subtle.digest(...args));
    retry.fill();
    retry.elements['task-s04'].checked = true;
    await retry.issue();
    assert.equal(retry.elements.phase2.disabled, true);
    assert.equal(retry.elements['supplied-prompt'].hidden, true);
    assert.equal(retry.elements.receipt.value, '');
    assert.equal(retry.elements.exposure.readOnly, false);
    assert.equal(retry.elements['issue-receipt'].disabled, false);
    assert.equal(retry.elements['task-choice'].disabled, false);
    assert.match(retry.elements['phase1-status'].textContent, /Could not compute/);
    fail = false;
    retry.elements['task-s04'].checked = false;
    await retry.issue();
    assert.equal(retry.elements.phase2.disabled, false);
    assert.match(retry.elements['supplied-prompt'].textContent, /Synthetic prompt S-03/);
    assert.equal(retry.elements['task-choice'].disabled, true);
  }

  process.stdout.write(JSON.stringify(report));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
