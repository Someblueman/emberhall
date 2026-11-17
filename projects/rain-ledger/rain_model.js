(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.RainLedgerModel = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const MM_PER_INCH = 25.4;
  const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];

  function isLeapYear(year) {
    if (!Number.isInteger(year) || year < 1) {
      throw new Error(`Invalid year: ${year}`);
    }
    return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
  }

  function daysInMonth(year, month) {
    if (!Number.isInteger(month) || month < 1 || month > 12) {
      throw new Error(`Invalid month: ${month}`);
    }
    const lengths = [31, isLeapYear(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    return lengths[month - 1];
  }

  function daysInYear(year) {
    return isLeapYear(year) ? 366 : 365;
  }

  function parseIsoDate(dateStr) {
    if (typeof dateStr !== 'string') {
      throw new Error('Invalid date format: expected YYYY-MM-DD string');
    }
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateStr);
    if (!match || dateStr.length !== 10) {
      throw new Error(`Invalid date format "${dateStr}": expected YYYY-MM-DD`);
    }
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    if (month < 1 || month > 12) {
      throw new Error(`Invalid calendar date "${dateStr}": month out of range`);
    }
    const maxDay = daysInMonth(year, month);
    if (day < 1 || day > maxDay) {
      throw new Error(`Invalid calendar date "${dateStr}": day out of range`);
    }
    return { year, month, day };
  }

  function validateUnit(unit) {
    if (unit !== 'mm' && unit !== 'in') {
      throw new Error(`Unsupported unit "${unit}": expected "mm" or "in"`);
    }
    return unit;
  }

  function validateAmount(amount) {
    if ((typeof amount !== 'number' && typeof amount !== 'string') ||
        (typeof amount === 'string' && amount.trim() === '')) {
      throw new Error('Amount must be a valid number');
    }
    const num = typeof amount === 'number' ? amount : Number(amount.trim());
    if (!Number.isFinite(num)) {
      throw new Error('Amount must be a valid number');
    }
    if (num < 0) {
      throw new Error('Amount must be non-negative');
    }
    return num;
  }

  function toMm(amount, unit) {
    const validAmount = validateAmount(amount);
    const validUnit = validateUnit(unit);
    const mm = validUnit === 'in' ? validAmount * MM_PER_INCH : validAmount;
    if (!Number.isFinite(mm)) {
      throw new Error('Converted amount must be finite');
    }
    return mm;
  }

  function fromMm(mm, unit) {
    const validMm = validateAmount(mm);
    const validUnit = validateUnit(unit);
    return validUnit === 'in' ? validMm / MM_PER_INCH : validMm;
  }

  function createLedger(year, options = {}) {
    if (!Number.isInteger(year) || year < 1900 || year > 2100) {
      throw new Error(`Invalid ledger year: ${year}`);
    }
    const displayUnit = validateUnit(options.displayUnit || 'mm');
    const normalsMm = {};
    for (let m = 1; m <= 12; m += 1) {
      normalsMm[m] = null;
    }
    return {
      year,
      displayUnit,
      normalsMm,
      entries: {},
    };
  }

  function upsertReading(ledger, reading) {
    if (!reading || typeof reading !== 'object') {
      throw new Error('Reading must be an object');
    }
    const { year } = parseIsoDate(reading.date);
    if (year !== ledger.year) {
      throw new Error(`Date "${reading.date}" does not match ledger year ${ledger.year}`);
    }
    const amount = validateAmount(reading.amount);
    const unit = validateUnit(reading.unit);
    const mm = toMm(amount, unit);
    const note = reading.note === undefined || reading.note === null ? '' : String(reading.note);

    const nextLedger = {
      ...ledger,
      entries: {
        ...ledger.entries,
        [reading.date]: {
          date: reading.date,
          amount,
          unit,
          mm,
          note,
        },
      },
    };
    // At most one year's readings: validate derived totals before a caller can
    // replace or persist its current ledger with this candidate.
    summarizeLedger(nextLedger);
    return nextLedger;
  }

  function removeReading(ledger, date) {
    parseIsoDate(date);
    if (!Object.prototype.hasOwnProperty.call(ledger.entries, date)) {
      return ledger;
    }
    const nextEntries = { ...ledger.entries };
    delete nextEntries[date];
    return {
      ...ledger,
      entries: nextEntries,
    };
  }

  function setDisplayUnit(ledger, unit) {
    return {
      ...ledger,
      displayUnit: validateUnit(unit),
    };
  }

  function setMonthlyNormal(ledger, month, amount, unit = ledger.displayUnit) {
    if (!Number.isInteger(month) || month < 1 || month > 12) {
      throw new Error(`Invalid month: ${month}`);
    }
    let nextMm = null;
    if (amount !== null && amount !== undefined && amount !== '') {
      nextMm = toMm(amount, unit);
    }
    return {
      ...ledger,
      normalsMm: {
        ...ledger.normalsMm,
        [month]: nextMm,
      },
    };
  }

  function summarizeLedger(ledger, overrideUnit) {
    const displayUnit = validateUnit(overrideUnit || ledger.displayUnit);
    const totalDays = daysInYear(ledger.year);
    const sortedDates = Object.keys(ledger.entries).sort();

    const months = [];
    for (let m = 1; m <= 12; m += 1) {
      const mDays = daysInMonth(ledger.year, m);
      months.push({
        month: m,
        name: MONTH_NAMES[m - 1],
        daysInMonth: mDays,
        recordedDays: 0,
        gapDays: mDays,
        zeroDays: 0,
        rainyDays: 0,
        totalMm: 0,
        total: 0,
        normal: ledger.normalsMm[m] === null ? null : fromMm(ledger.normalsMm[m], displayUnit),
        deltaFromNormal: null,
        wettestDay: null,
      });
    }

    let recordedDays = 0;
    let zeroDays = 0;
    let rainyDays = 0;
    let ytdTotalMm = 0;
    let ytdWettest = null;

    for (const date of sortedDates) {
      const entry = ledger.entries[date];
      const { month } = parseIsoDate(date);
      const mSummary = months[month - 1];

      recordedDays += 1;
      mSummary.recordedDays += 1;
      mSummary.gapDays = mSummary.daysInMonth - mSummary.recordedDays;

      if (entry.mm === 0) {
        zeroDays += 1;
        mSummary.zeroDays += 1;
      } else {
        rainyDays += 1;
        mSummary.rainyDays += 1;
      }

      ytdTotalMm += entry.mm;
      mSummary.totalMm += entry.mm;
      if (!Number.isFinite(ytdTotalMm)) {
        throw new Error('Rainfall total must be finite');
      }

      if (entry.mm > 0) {
        if (!ytdWettest || entry.mm > ytdWettest.mm) {
          ytdWettest = entry;
        }
        if (!mSummary.wettestDay || entry.mm > mSummary.wettestDay.mm) {
          mSummary.wettestDay = entry;
        }
      }
    }

    for (const mSummary of months) {
      mSummary.total = fromMm(mSummary.totalMm, displayUnit);
      if (mSummary.normal !== null) {
        mSummary.deltaFromNormal = mSummary.total - mSummary.normal;
      }
      if (mSummary.wettestDay) {
        mSummary.wettestDay = {
          date: mSummary.wettestDay.date,
          amount: mSummary.wettestDay.amount,
          unit: mSummary.wettestDay.unit,
          displayAmount: fromMm(mSummary.wettestDay.mm, displayUnit),
        };
      }
      delete mSummary.totalMm;
    }

    return {
      year: ledger.year,
      displayUnit,
      daysInYear: totalDays,
      recordedDays,
      gapDays: totalDays - recordedDays,
      zeroDays,
      rainyDays,
      ytdTotal: fromMm(ytdTotalMm, displayUnit),
      wettestDay: ytdWettest
        ? {
            date: ytdWettest.date,
            amount: ytdWettest.amount,
            unit: ytdWettest.unit,
            displayAmount: fromMm(ytdWettest.mm, displayUnit),
          }
        : null,
      months,
    };
  }

  function exportJson(ledger) {
    const sortedDates = Object.keys(ledger.entries).sort();
    const entries = sortedDates.map((date) => {
      const e = ledger.entries[date];
      return {
        date: e.date,
        amount: e.amount,
        unit: e.unit,
        note: e.note || '',
      };
    });
    const normalsMm = {};
    for (let m = 1; m <= 12; m += 1) {
      normalsMm[m] = ledger.normalsMm[m] === undefined ? null : ledger.normalsMm[m];
    }
    return JSON.stringify(
      {
        schema: 'rain-ledger/v1',
        year: ledger.year,
        displayUnit: ledger.displayUnit,
        normalsMm,
        entries,
      },
      null,
      2
    );
  }

  function importJson(jsonText) {
    let parsed;
    try {
      parsed = JSON.parse(jsonText);
    } catch (err) {
      throw new Error(`Invalid JSON: ${err.message}`);
    }
    if (!parsed || typeof parsed !== 'object') {
      throw new Error('Invalid JSON: expected an object');
    }
    let ledger = createLedger(parsed.year, { displayUnit: parsed.displayUnit || 'mm' });
    if (parsed.normalsMm && typeof parsed.normalsMm === 'object') {
      for (let m = 1; m <= 12; m += 1) {
        const val = parsed.normalsMm[m];
        if (val !== null && val !== undefined) {
          ledger = setMonthlyNormal(ledger, m, val, 'mm');
        }
      }
    }
    if (Array.isArray(parsed.entries)) {
      for (const item of parsed.entries) {
        ledger = upsertReading(ledger, item);
      }
    } else if (parsed.entries && typeof parsed.entries === 'object') {
      for (const date of Object.keys(parsed.entries).sort()) {
        ledger = upsertReading(ledger, parsed.entries[date]);
      }
    } else {
      throw new Error('Invalid JSON: entries must be an array or object');
    }
    return ledger;
  }

  function csvEscape(value) {
    const str = String(value === undefined || value === null ? '' : value);
    if (/[",\n\r]/.test(str)) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  }

  function parseCsvRow(line) {
    const fields = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i += 1) {
      const ch = line[i];
      if (inQuotes) {
        if (ch === '"') {
          if (line[i + 1] === '"') {
            current += '"';
            i += 1;
          } else {
            inQuotes = false;
          }
        } else {
          current += ch;
        }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        fields.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
    if (inQuotes) {
      throw new Error('Malformed CSV: unclosed quote');
    }
    fields.push(current);
    return fields;
  }

  function exportCsv(ledger) {
    const sortedDates = Object.keys(ledger.entries).sort();
    const lines = ['date,amount,unit,mm,note'];
    for (const date of sortedDates) {
      const e = ledger.entries[date];
      const mmRounded = Number(e.mm.toFixed(6));
      lines.push(
        [
          csvEscape(e.date),
          csvEscape(e.amount),
          csvEscape(e.unit),
          csvEscape(mmRounded),
          csvEscape(e.note || ''),
        ].join(',')
      );
    }
    return lines.join('\n') + '\n';
  }

  function importCsv(csvText, year, displayUnit = 'mm') {
    if (typeof csvText !== 'string') {
      throw new Error('CSV input must be a string');
    }
    const lines = csvText
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .split('\n')
      .filter((line) => line.trim() !== '');

    if (lines.length === 0) {
      throw new Error('CSV input is empty');
    }

    const header = parseCsvRow(lines[0]).map((h) => h.trim().toLowerCase());
    const dateIdx = header.indexOf('date');
    const amountIdx = header.indexOf('amount');
    const unitIdx = header.indexOf('unit');
    const noteIdx = header.indexOf('note');

    if (dateIdx === -1 || amountIdx === -1 || unitIdx === -1) {
      throw new Error('CSV header must include date, amount, and unit columns');
    }

    let ledger = createLedger(year, { displayUnit });
    for (let i = 1; i < lines.length; i += 1) {
      const row = parseCsvRow(lines[i]);
      ledger = upsertReading(ledger, {
        date: (row[dateIdx] || '').trim(),
        amount: (row[amountIdx] || '').trim(),
        unit: (row[unitIdx] || '').trim(),
        note: noteIdx !== -1 ? row[noteIdx] || '' : '',
      });
    }
    return ledger;
  }

  return {
    MM_PER_INCH,
    MONTH_NAMES,
    isLeapYear,
    daysInMonth,
    daysInYear,
    parseIsoDate,
    validateUnit,
    validateAmount,
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
  };
});
