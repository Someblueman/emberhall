'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const M = require('./rain_model.js');

function withReading(amount = 10, unit = 'mm') {
  return M.upsertReading(M.createLedger(2025), { date: '2025-04-01', amount, unit });
}

test('noncanonical dates cannot create a second reading for the same day', () => {
  const ledger = withReading();
  const before = M.exportJson(ledger);
  const alias = { date: ' 2025-04-01 ', amount: 20, unit: 'mm' };
  for (const date of [alias.date, '2025-04-01\n', '\t2025-04-01']) {
    assert.throws(() => M.upsertReading(ledger, { ...alias, date }), /Invalid date format/);
  }
  assert.throws(() => M.removeReading(ledger, alias.date), /Invalid date format/);
  const imported = JSON.parse(before);
  imported.entries.push(alias);
  assert.throws(() => M.importJson(JSON.stringify(imported)), /Invalid date format/);
  assert.equal(M.exportJson(ledger), before);
  const updated = M.upsertReading(ledger, { ...alias, date: '2025-04-01' });
  assert.equal(M.summarizeLedger(updated).recordedDays, 1);
  assert.equal(M.summarizeLedger(updated).ytdTotal, 20);
});

test('non-numeric types and blank amounts are refused without replacing work', () => {
  const ledger = withReading();
  const before = M.exportJson(ledger);
  for (const amount of [[], [3], {}, true, false, null, '', ' ', '\t\n']) {
    const imported = JSON.parse(before);
    imported.entries[0].amount = amount;
    assert.throws(() => M.importJson(JSON.stringify(imported)), /valid number/);
    if (amount !== null && amount !== '') {
      assert.throws(() => M.setMonthlyNormal(ledger, 4, amount), /valid number/);
    }
    assert.equal(M.exportJson(ledger), before);
  }
  for (const amount of [0, '0', ' 0.5 ', '1e2']) {
    assert.equal(M.validateAmount(amount), Number(amount));
  }
  assert.equal(M.setMonthlyNormal(ledger, 4, '').normalsMm[4], null);
  assert.equal(M.setMonthlyNormal(ledger, 4, null).normalsMm[4], null);
});

test('conversion and accumulated-total overflow fail before accepting a ledger', () => {
  const ledger = withReading();
  const before = M.exportJson(ledger);
  assert.throws(() => M.toMm(1e308, 'in'), /finite/);
  assert.throws(() => M.setMonthlyNormal(ledger, 4, 1e308, 'in'), /finite/);
  const imported = JSON.parse(before);
  imported.entries[0] = { date: '2025-04-01', amount: 1e308, unit: 'in' };
  assert.throws(() => M.importJson(JSON.stringify(imported)), /finite/);
  const large = withReading(1e308);
  assert.throws(() => M.upsertReading(large, { date: '2025-05-01', amount: 1e308, unit: 'mm' }), /finite/);
  const csv = 'date,amount,unit\n2025-04-01,1e308,mm\n2025-05-01,1e308,mm\n';
  assert.throws(() => M.importCsv(csv, 2025), /finite/);
  assert.equal(M.exportJson(ledger), before);
  assert.equal(M.summarizeLedger(large).ytdTotal, 1e308);
});

test('valid example and mixed-unit updates retain totals through both exports', () => {
  const fs = require('node:fs');
  const example = M.importJson(fs.readFileSync(`${__dirname}/example_two_month.json`, 'utf8'));
  const summary = M.summarizeLedger(example);
  assert.equal(summary.recordedDays, 10);
  assert.ok(Math.abs(summary.ytdTotal - 88.75) < 1e-9);
  assert.equal(summary.zeroDays, 3);
  const json = M.exportJson(example);
  assert.equal(M.exportJson(M.importJson(json)), json);
  const csv = M.exportCsv(example);
  assert.equal(M.exportCsv(M.importCsv(csv, 2025)), csv);
  const changed = M.upsertReading(example, { date: '2025-04-01', amount: '1', unit: 'in' });
  assert.equal(M.summarizeLedger(changed).recordedDays, 10);
  assert.ok(Math.abs(M.summarizeLedger(changed).ytdTotal - 102.15) < 1e-9);
});
