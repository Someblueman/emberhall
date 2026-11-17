'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const PROJECT_DIR = path.resolve(__dirname, '..');
const PLAYER_DIR = __dirname;

const realTruth = JSON.parse(
  fs.readFileSync(path.join(PROJECT_DIR, 'case/truth-sheet.json'), 'utf8')
);
const realLanding = JSON.parse(
  fs.readFileSync(path.join(PROJECT_DIR, 'case/landing-clerk.json'), 'utf8')
);
const realEngine = JSON.parse(
  fs.readFileSync(path.join(PROJECT_DIR, 'case/engine-room.json'), 'utf8')
);
const realScenesMap = new Map([
  ['landing-clerk', realLanding],
  ['engine-room', realEngine],
]);

function makeMockDom(htmlSource) {
  class FakeElement {
    constructor(tagName) {
      this.tagName = tagName.toUpperCase();
      this.children = [];
      this.parentNode = null;
      this.attributes = {};
      this.dataset = {};
      this.listeners = {};
      this._id = '';
      this._className = '';
      this._textContent = '';
      this._innerHTML = '';
      this.hidden = false;
      this.disabled = false;
      this.checked = false;
      this.value = '';
      this.type = '';
      this.name = '';
      this.htmlFor = '';
      this.scrollTop = 0;
      this.scrollHeight = 0;
      this.classList = {
        _set: new Set(),
        toggle: (cls, force) => {
          if (force === undefined) {
            if (this.classList._set.has(cls)) this.classList._set.delete(cls);
            else this.classList._set.add(cls);
          } else if (force) {
            this.classList._set.add(cls);
          } else {
            this.classList._set.delete(cls);
          }
          this._className = [...this.classList._set].join(' ');
        },
        contains: (cls) => this.classList._set.has(cls),
      };
    }
    get id() { return this._id; }
    set id(v) { this._id = String(v); this.attributes.id = this._id; }
    get className() { return this._className; }
    set className(v) {
      this._className = String(v);
      this.classList._set = new Set(this._className.split(/\s+/).filter(Boolean));
    }
    get textContent() {
      if (this.children.length === 0) return this._textContent;
      return this._textContent + this.children.map((c) => c.textContent).join(' ');
    }
    set textContent(v) {
      this._textContent = String(v);
      this._innerHTML = '';
      this.children = [];
    }
    get innerHTML() { return this._innerHTML; }
    set innerHTML(v) {
      this._innerHTML = String(v);
      this.children = [];
      this._textContent = '';
    }
    appendChild(child) {
      child.parentNode = this;
      this.children.push(child);
      return child;
    }
    remove() {
      if (this.parentNode) {
        this.parentNode.children = this.parentNode.children.filter((c) => c !== this);
        this.parentNode = null;
      }
    }
    setAttribute(k, v) {
      this.attributes[k] = String(v);
      if (k === 'id') this._id = String(v);
      if (k === 'for') this.htmlFor = String(v);
    }
    getAttribute(k) { return this.attributes[k] ?? null; }
    addEventListener(type, fn) {
      if (!this.listeners[type]) this.listeners[type] = [];
      this.listeners[type].push(fn);
    }
    dispatchEvent(type) {
      for (const fn of this.listeners[type] || []) fn({ target: this });
    }
    click() { this.dispatchEvent('click'); }
    focus() { documentState.activeElement = this; }
    select() {}
    querySelectorAll(selector) {
      const results = [];
      const walk = (node) => {
        for (const child of node.children) {
          if (matchesSelector(child, selector)) results.push(child);
          walk(child);
        }
      };
      walk(documentState.body);
      return results;
    }
  }

  function matchesSelector(node, selector) {
    if (selector === '#tabs button.tab') {
      const parent = node.parentNode;
      return parent && parent.id === 'tabs' && node.tagName === 'BUTTON' && node.classList.contains('tab');
    }
    if (selector === 'input[type="checkbox"][data-key]') {
      return node.tagName === 'INPUT' && node.type === 'checkbox' && typeof node.dataset.key === 'string';
    }
    if (selector === 'input[name="selfcheck"]') {
      return node.tagName === 'INPUT' && node.type === 'radio' && node.name === 'selfcheck';
    }
    return false;
  }

  const documentState = {
    activeElement: null,
    readyState: 'complete',
    body: new FakeElement('body'),
  };
  const byId = new Map();
  const register = (id, tag) => {
    const el = new FakeElement(tag);
    el.id = id;
    byId.set(id, el);
    documentState.body.appendChild(el);
    return el;
  };

  for (const [id, tag] of [
    ['case-title', 'h1'],
    ['case-question', 'p'],
    ['case-kicker', 'p'],
    ['case-sub', 'p'],
    ['source-note', 'p'],
    ['mode-badge', 'span'],
    ['load-files', 'input'],
    ['load-fixture', 'button'],
    ['load-status', 'p'],
    ['reach-stage', 'section'],
    ['tabs', 'nav'],
    ['scene-panel', 'article'],
    ['notebook', 'div'],
    ['route', 'ol'],
    ['explanation', 'textarea'],
    ['submit', 'button'],
    ['submit-hint', 'span'],
    ['answer-panel', 'section'],
    ['answer-question', 'p'],
    ['answer-text', 'p'],
    ['answer-note', 'p'],
    ['cited-summary', 'p'],
    ['export', 'button'],
    ['show-record', 'button'],
    ['copy-record', 'button'],
    ['record-text', 'textarea'],
    ['export-status', 'p'],
  ]) {
    register(id, tag);
  }
  byId.get('answer-panel').hidden = true;
  byId.get('case-question').hidden = true;
  byId.get('record-text').hidden = true;

  for (const val of ['supported', 'ambiguous', 'trivial']) {
    const radio = new FakeElement('input');
    radio.type = 'radio';
    radio.name = 'selfcheck';
    radio.value = val;
    radio.id = 'selfcheck-' + val;
    documentState.body.appendChild(radio);
  }

  // Check static HTML for radio labels as well
  const document = {
    readyState: 'complete',
    body: documentState.body,
    getElementById: (id) => byId.get(id) || null,
    createElement: (tag) => new FakeElement(tag),
    createTextNode: (text) => ({ tagName: '#text', textContent: String(text), children: [] }),
    querySelectorAll: (sel) => documentState.body.querySelectorAll(sel),
    addEventListener: () => {},
  };

  return { document, byId, htmlSource };
}

function collectAll(node) {
  const out = [];
  if (!node || !Array.isArray(node.children)) return out;
  for (const child of node.children) {
    out.push(child);
    out.push(...collectAll(child));
  }
  return out;
}

test('reach-model builds spoiler-free view model, live SVG, and gallery preview SVG', () => {
  const reach = require('./reach-model.js');
  const vmState = reach.buildReachViewModel(
    realTruth,
    realScenesMap,
    'landing-clerk',
    new Set(['landing-clerk#1', 'engine-room#1'])
  );

  assert.equal(vmState.isMothCase, true);
  assert.equal(vmState.accounts.length, 2);
  assert.equal(vmState.accounts[0].active, true);
  assert.equal(vmState.accounts[0].citedCount, 1);
  assert.equal(vmState.accounts[1].citedCount, 1);
  assert.equal(vmState.citedFactsCount, 2);

  const f2 = vmState.facts.find((f) => f.id === 'F2');
  const f5 = vmState.facts.find((f) => f.id === 'F5');
  assert.equal(f2.shoreCited, true);
  assert.equal(f2.engineCited, false);
  assert.equal(f5.shoreCited, false);
  assert.equal(f5.engineCited, true);

  const liveSvg = reach.liveReachSvg(vmState);
  assert.match(liveSvg, /^<svg\b/);
  assert.match(liveSvg, /North Landing/);
  assert.match(liveSvg, /South Pier/);
  assert.match(liveSvg, /Orchard Float/);
  assert.doesNotMatch(liveSvg, /passenger left at Orchard Float/i);
  assert.doesNotMatch(liveSvg, /north-landing clerk watched/i);

  const previewSvg = reach.galleryPreviewSvg(realTruth, realScenesMap);
  assert.match(previewSvg, /^<svg\b/);
  assert.match(previewSvg, /The North Desk/);
  assert.match(previewSvg, /Below the Waterline/);
  assert.doesNotMatch(previewSvg, /passenger left at Orchard Float/i);
  assert.equal(
    fs.readFileSync(path.join(PROJECT_DIR, 'gallery-preview.svg'), 'utf8'),
    previewSvg,
    'gallery-preview.svg must match reach-model galleryPreviewSvg output'
  );
});

test('index.html wires reach-model.js, #reach-stage, and explicit for-labels on selfcheck radios', () => {
  const html = fs.readFileSync(path.join(PLAYER_DIR, 'index.html'), 'utf8');
  assert.match(html, /<script\s+src="reach-model\.js"\s+defer><\/script>/);
  assert.match(html, /id="reach-stage"/);
  assert.match(html, /<input[^>]+id="selfcheck-supported"[^>]+name="selfcheck"/);
  assert.match(html, /<label\s+for="selfcheck-supported">/);
  assert.match(html, /<label\s+for="selfcheck-ambiguous">/);
  assert.match(html, /<label\s+for="selfcheck-trivial">/);
});

test('player auto-opens first account, keeps answer gated, labels all checkboxes, and updates live reach', async () => {
  const html = fs.readFileSync(path.join(PLAYER_DIR, 'index.html'), 'utf8');
  const reachSource = fs.readFileSync(path.join(PLAYER_DIR, 'reach-model.js'), 'utf8');
  const playerSource = fs.readFileSync(path.join(PLAYER_DIR, 'player.js'), 'utf8');
  const fixtureSource = fs.readFileSync(path.join(PLAYER_DIR, 'fixture/fixture.js'), 'utf8');

  const { document, byId } = makeMockDom(html);
  const windowObj = {
    location: { protocol: 'http:', search: '', href: 'http://127.0.0.1:8080/player/index.html' },
    addEventListener: () => {},
    NIGHT_FERRY_FIXTURE: null,
  };

  const fetchMock = async (url) => {
    const href = String(url);
    if (href.endsWith('truth-sheet.json')) return { ok: true, json: async () => realTruth };
    if (href.endsWith('landing-clerk.json')) return { ok: true, json: async () => realLanding };
    if (href.endsWith('engine-room.json')) return { ok: true, json: async () => realEngine };
    return { ok: false, status: 404 };
  };

  const context = vm.createContext({
    window: windowObj,
    document,
    URL,
    URLSearchParams,
    fetch: fetchMock,
    Blob: class {},
    FileReader: class {},
    navigator: {},
    setTimeout,
    console,
  });
  windowObj.window = windowObj;

  vm.runInContext(fixtureSource, context);
  vm.runInContext(reachSource, context);
  vm.runInContext(playerSource, context);

  // Allow promise chain in boot() to resolve
  await new Promise((r) => setTimeout(r, 20));

  // 1. First account opens immediately on load (no blank placeholder)
  const scenePanel = byId.get('scene-panel');
  assert.match(scenePanel.textContent, /The North Desk/);
  assert.doesNotMatch(scenePanel.textContent, /Choose an account above to read it/);

  // 2. Live reach stage is rendered immediately
  const reachStage = byId.get('reach-stage');
  assert.match(reachStage.innerHTML, /<svg\b/);
  assert.match(reachStage.innerHTML, /North Landing/);
  assert.match(reachStage.innerHTML, /0 \/ 6 facts cited/);

  // 3. Answer and canonical truth statements remain strictly out of DOM before submit
  const answerPanel = byId.get('answer-panel');
  assert.equal(answerPanel.hidden, true);
  assert.equal(byId.get('answer-text').textContent, '');
  const preSubmitDump =
    scenePanel.textContent + byId.get('notebook').textContent + reachStage.innerHTML;
  assert.doesNotMatch(preSubmitDump, /The passenger left at Orchard Float/);
  assert.doesNotMatch(preSubmitDump, /north-landing clerk watched/);

  // 4. Every checkbox in scene-panel and notebook has an explicit id matched by label.htmlFor
  const allBoxes = [
    ...collectAll(scenePanel).filter((n) => n.tagName === 'INPUT' && n.type === 'checkbox'),
    ...collectAll(byId.get('notebook')).filter((n) => n.tagName === 'INPUT' && n.type === 'checkbox'),
  ];
  assert.equal(allBoxes.length, 9);
  for (const box of allBoxes) {
    assert.ok(box.id && box.id.length > 0, 'checkbox must have id');
    assert.equal(box.parentNode.tagName, 'LABEL');
    assert.equal(box.parentNode.htmlFor, box.id, 'label must bind htmlFor to checkbox id');
  }

  // 5. Switching to Below the Waterline and citing a statement updates reachStage
  const tabs = collectAll(byId.get('tabs')).filter((n) => n.tagName === 'BUTTON');
  assert.equal(tabs.length, 2);
  assert.equal(tabs[0].getAttribute('aria-pressed'), 'true');
  tabs[1].click();
  assert.match(scenePanel.textContent, /Below the Waterline/);
  assert.equal(tabs[1].getAttribute('aria-pressed'), 'true');

  const engineBoxes = collectAll(scenePanel).filter(
    (n) => n.tagName === 'INPUT' && n.type === 'checkbox'
  );
  engineBoxes[1].checked = true;
  engineBoxes[1].dispatchEvent('change');
  assert.match(reachStage.innerHTML, /1 \/ 6 facts cited/);

  // 6. Submitting empty text keeps answer hidden; non-empty reveals it
  byId.get('submit').click();
  assert.equal(answerPanel.hidden, true);
  byId.get('explanation').value = 'Moth stopped once at Orchard Float because F5 matches F2.';
  byId.get('submit').click();
  assert.equal(answerPanel.hidden, false);
  assert.match(byId.get('answer-text').textContent, /Orchard Float/);
  assert.equal(byId.get('submit').disabled, true);
});
