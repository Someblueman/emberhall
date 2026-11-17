'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const model = require('./rain_model.js');
const appSource = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');

function runApp(savedJson = null) {
  const storage = new Map();
  if (savedJson !== null) {
    storage.set('rain-ledger-v1-state', savedJson);
  }
  const elements = new Map();
  const makeEl = (tag = 'div') => {
    const el = {
      tagName: tag.toUpperCase(),
      children: [],
      listeners: {},
      value: '',
      textContent: '',
      _innerHTML: '',
      className: '',
      hidden: false,
      classList: { add() {}, remove() {}, toggle() {} },
      appendChild(child) { this.children.push(child); return child; },
      addEventListener(type, fn) { this.listeners[type] = fn; },
      setAttribute() {},
    };
    Object.defineProperty(el, 'innerHTML', {
      get() { return this._innerHTML; },
      set(val) { this._innerHTML = String(val); if (val === '') this.children = []; },
    });
    return el;
  };
  const get = id => {
    if (!elements.has(id)) elements.set(id, makeEl());
    return elements.get(id);
  };
  const document = {
    getElementById: get,
    createElement: makeEl,
    querySelectorAll: () => [],
    body: makeEl('body'),
  };
  const windowObj = { RainLedgerModel: model, print() {} };
  const localStorage = {
    getItem: key => (storage.has(key) ? storage.get(key) : null),
    setItem: (key, val) => storage.set(key, String(val)),
  };
  vm.runInNewContext(appSource, { window: windowObj, document, localStorage, Blob, URL });
  return { elements, storage, get };
}

test('opens with the 2-month sample ledger when localStorage has no saved state', () => {
  const { get } = runApp(null);
  const summaryText = get('summary-grid').children
    .map(box => box.children.map(c => c.textContent).join(': '))
    .join(' | ');
  assert.match(summaryText, /YTD Total: 88\.8 mm/);
  assert.match(summaryText, /Recorded Days: 10 \/ 365/);
  assert.equal(get('log-tbody').children.length, 10);
  assert.match(get('status-banner').textContent, /Sample 2-month ledger loaded/);
  assert.equal(get('status-banner').hidden, false);
});

test('preserves saved localStorage ledger and Clear Year still resets to 0 readings', () => {
  const custom = model.upsertReading(model.createLedger(2025), { date: '2025-01-05', amount: 3.5, unit: 'mm' });
  const { get } = runApp(model.exportJson(custom));
  assert.equal(get('log-tbody').children.length, 1);
  get('clear-btn').listeners.click();
  assert.equal(get('log-tbody').children.length, 1);
  assert.match(get('log-tbody').children[0].children[0].textContent, /No readings recorded yet/);
  assert.match(get('status-banner').textContent, /Cleared all readings/);
});

test('every form field is explicitly named by its visible label', () => {
  const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
  const labelled = [...html.matchAll(/<label[^>]*\bfor="([^"]+)"/g)].map(m => m[1]);
  const fields = [...html.matchAll(/<(?:input|select|textarea)[^>]*\bid="([^"]+)"/g)].map(m => m[1]);
  assert.ok(fields.length > 0, 'index.html should contain labelled fields');
  assert.deepEqual([...labelled].sort(), [...fields].sort());
});
