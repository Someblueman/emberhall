'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const {
  MM_PER_INCH,
  isLeapYear,
  daysInMonth,
  daysInYear,
  parseIsoDate,
  toMm,
  fromMm,
  createLedger,
  upsertReading,
  removeReading,
  setDisplayUnit,
  setMonthlyNormal,
  summarizeLedger,
  exportJson,
  importJson,
  exportCsv,
  importCsv,
} = require('./rain_model.js');

test('leap-year calendar handling', () => {
  assert.equal(isLeapYear(2024), true);
  assert.equal(isLeapYear(2025), false);
  assert.equal(isLeapYear(2000), true);
  assert.equal(isLeapYear(1900), false);

  assert.equal(daysInMonth(2024, 2), 29);
  assert.equal(daysInMonth(2025, 2), 28);
  assert.equal(daysInYear(2024), 366);
  assert.equal(daysInYear(2025), 365);

  assert.deepEqual(parseIsoDate('2024-02-29'), { year: 2024, month: 2, day: 29 });
  assert.throws(() => parseIsoDate('2025-02-29'), /Invalid calendar date/);
});

test('unit conversion between mm and inches', () => {
  assert.equal(MM_PER_INCH, 25.4);
  assert.ok(Math.abs(toMm(1, 'in') - 25.4) < 1e-9);
  assert.ok(Math.abs(fromMm(25.4, 'in') - 1) < 1e-9);
  assert.equal(toMm(12.5, 'mm'), 12.5);
  assert.equal(fromMm(12.5, 'mm'), 12.5);
});

test('malformed date and amount refusal', () => {
  const ledger = createLedger(2025, { displayUnit: 'mm' });

  assert.throws(() => upsertReading(ledger, { date: '2025-02-29', amount: 5, unit: 'mm' }), /Invalid calendar date/);
  assert.throws(() => upsertReading(ledger, { date: '2025-13-01', amount: 5, unit: 'mm' }), /Invalid calendar date/);
  assert.throws(() => upsertReading(ledger, { date: 'not-a-date', amount: 5, unit: 'mm' }), /Invalid date format/);
  assert.throws(() => upsertReading(ledger, { date: '2024-06-01', amount: 5, unit: 'mm' }), /does not match ledger year/);

  assert.throws(() => upsertReading(ledger, { date: '2025-06-01', amount: -1, unit: 'mm' }), /non-negative/);
  assert.throws(() => upsertReading(ledger, { date: '2025-06-01', amount: 'abc', unit: 'mm' }), /valid number/);
  assert.throws(() => upsertReading(ledger, { date: '2025-06-01', amount: '', unit: 'mm' }), /valid number/);
  assert.throws(() => upsertReading(ledger, { date: '2025-06-01', amount: 5, unit: 'cm' }), /Unsupported unit/);
});

test('duplicate-date update replaces previous reading rather than adding', () => {
  let ledger = createLedger(2025, { displayUnit: 'mm' });
  ledger = upsertReading(ledger, { date: '2025-04-10', amount: 10, unit: 'mm', note: 'morning' });
  ledger = upsertReading(ledger, { date: '2025-04-10', amount: 1.5, unit: 'in', note: 'corrected' });

  const summary = summarizeLedger(ledger);
  assert.equal(summary.recordedDays, 1);
  assert.equal(summary.rainyDays, 1);
  assert.ok(Math.abs(summary.ytdTotal - 38.1) < 1e-9);
  assert.equal(ledger.entries['2025-04-10'].note, 'corrected');
});

test('hand-built two-month synthetic series distinguishes zero from gap', () => {
  // Synthetic series for 2025 (non-leap, 365 days):
  // April (30 days):
  //   2025-04-01: 12.0 mm
  //   2025-04-02: 0 mm (recorded dry day)
  //   2025-04-03: 0.5 in (= 12.7 mm)
  //   (27 missed-day gaps)
  // May (31 days):
  //   2025-05-05: 25.4 mm (= 1.0 in)
  //   2025-05-10: 0.0 in (= 0 mm, recorded dry day)
  //   (29 missed-day gaps)
  let ledger = createLedger(2025, { displayUnit: 'mm' });
  ledger = setMonthlyNormal(ledger, 4, 50, 'mm');
  ledger = upsertReading(ledger, { date: '2025-04-01', amount: 12.0, unit: 'mm' });
  ledger = upsertReading(ledger, { date: '2025-04-02', amount: 0, unit: 'mm' });
  ledger = upsertReading(ledger, { date: '2025-04-03', amount: 0.5, unit: 'in' });
  ledger = upsertReading(ledger, { date: '2025-05-05', amount: 25.4, unit: 'mm' });
  ledger = upsertReading(ledger, { date: '2025-05-10', amount: 0, unit: 'in' });

  const summaryMm = summarizeLedger(ledger, 'mm');
  assert.equal(summaryMm.daysInYear, 365);
  assert.equal(summaryMm.recordedDays, 5);
  assert.equal(summaryMm.gapDays, 360);
  assert.equal(summaryMm.zeroDays, 2);
  assert.equal(summaryMm.rainyDays, 3);
  assert.ok(Math.abs(summaryMm.ytdTotal - 50.1) < 1e-9);
  assert.equal(summaryMm.wettestDay.date, '2025-05-05');
  assert.ok(Math.abs(summaryMm.wettestDay.displayAmount - 25.4) < 1e-9);

  const april = summaryMm.months[3];
  assert.equal(april.month, 4);
  assert.equal(april.recordedDays, 3);
  assert.equal(april.gapDays, 27);
  assert.equal(april.zeroDays, 1);
  assert.equal(april.rainyDays, 2);
  assert.ok(Math.abs(april.total - 24.7) < 1e-9);
  assert.ok(Math.abs(april.normal - 50) < 1e-9);
  assert.ok(Math.abs(april.deltaFromNormal - (-25.3)) < 1e-9);

  // Totals display in inches
  const summaryIn = summarizeLedger(setDisplayUnit(ledger, 'in'));
  assert.equal(summaryIn.displayUnit, 'in');
  assert.ok(Math.abs(summaryIn.ytdTotal - (50.1 / 25.4)) < 1e-9);
  assert.ok(Math.abs(summaryIn.wettestDay.displayAmount - 1.0) < 1e-9);

  // Removing a reading turns it back into a gap
  const afterRemove = removeReading(ledger, '2025-04-02');
  assert.equal(summarizeLedger(afterRemove).recordedDays, 4);
  assert.equal(summarizeLedger(afterRemove).zeroDays, 1);
});

test('deterministic JSON and CSV export/import round-trip and validation', () => {
  let ledger = createLedger(2025, { displayUnit: 'mm' });
  ledger = upsertReading(ledger, { date: '2025-05-05', amount: 1, unit: 'in', note: 'storm, heavy' });
  ledger = upsertReading(ledger, { date: '2025-04-01', amount: 10, unit: 'mm', note: 'light' });

  const json1 = exportJson(ledger);
  const json2 = exportJson(ledger);
  assert.equal(json1, json2);

  const reimportedJson = importJson(json1);
  assert.equal(exportJson(reimportedJson), json1);

  const csv1 = exportCsv(ledger);
  assert.match(csv1, /^date,amount,unit,mm,note\n2025-04-01,10,mm,10,light\n2025-05-05,1,in,25.4,"storm, heavy"/);

  const reimportedCsv = importCsv(csv1, 2025, 'mm');
  assert.equal(summarizeLedger(reimportedCsv).recordedDays, 2);
  assert.ok(Math.abs(summarizeLedger(reimportedCsv).ytdTotal - 35.4) < 1e-9);

  // Malformed imports must throw before replacing anything
  assert.throws(() => importJson('{"year": 2025, "entries": {"2025-02-29": {"date": "2025-02-29", "amount": 1, "unit": "mm"}}}'), /Invalid calendar date/);
  assert.throws(() => importCsv('date,amount,unit,mm,note\n2025-04-01,-5,mm,-5,bad', 2025), /non-negative/);
});
