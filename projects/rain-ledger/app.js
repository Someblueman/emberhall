(function () {
  'use strict';

  const M = window.RainLedgerModel;
  const STORAGE_KEY = 'rain-ledger-v1-state';

  const EXAMPLE_TWO_MONTH = {
    schema: 'rain-ledger/v1',
    year: 2025,
    displayUnit: 'mm',
    normalsMm: {
      1: null, 2: null, 3: null, 4: 65, 5: 80, 6: null,
      7: null, 8: null, 9: null, 10: null, 11: null, 12: null,
    },
    entries: [
      { date: '2025-04-01', amount: 12.0, unit: 'mm', note: 'Steady morning shower' },
      { date: '2025-04-02', amount: 0, unit: 'mm', note: 'Recorded dry day' },
      { date: '2025-04-03', amount: 0.5, unit: 'in', note: 'Afternoon squall (entered in inches)' },
      { date: '2025-04-08', amount: 4.2, unit: 'mm', note: 'Light drizzle' },
      { date: '2025-04-15', amount: 0, unit: 'mm', note: 'Recorded dry day' },
      { date: '2025-04-21', amount: 18.6, unit: 'mm', note: 'Spring front' },
      { date: '2025-05-02', amount: 0.25, unit: 'in', note: 'Early May rain' },
      { date: '2025-05-05', amount: 25.4, unit: 'mm', note: 'Heavy downpour (1.00 in)' },
      { date: '2025-05-10', amount: 0, unit: 'in', note: 'Recorded dry day' },
      { date: '2025-05-18', amount: 9.5, unit: 'mm', note: 'Evening rain' },
    ],
  };

  let loadedSampleOnStart = false;
  let ledger = loadInitialLedger();

  const yearInput = document.getElementById('year-input');
  const displayUnitSelect = document.getElementById('display-unit-select');
  const printBtn = document.getElementById('print-btn');
  const statusBanner = document.getElementById('status-banner');
  const readingForm = document.getElementById('reading-form');
  const readingDate = document.getElementById('reading-date');
  const readingAmount = document.getElementById('reading-amount');
  const readingUnit = document.getElementById('reading-unit');
  const readingNote = document.getElementById('reading-note');
  const summaryYearLabel = document.getElementById('summary-year-label');
  const summaryGrid = document.getElementById('summary-grid');
  const monthlyTbody = document.getElementById('monthly-tbody');
  const logTbody = document.getElementById('log-tbody');
  const exportJsonBtn = document.getElementById('export-json-btn');
  const exportCsvBtn = document.getElementById('export-csv-btn');
  const importFileInput = document.getElementById('import-file-input');
  const loadExampleBtn = document.getElementById('load-example-btn');
  const clearBtn = document.getElementById('clear-btn');

  function loadInitialLedger() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        return M.importJson(saved);
      }
    } catch (_err) {
      // Ignore corrupt localStorage and start fresh
    }
    loadedSampleOnStart = true;
    return M.importJson(JSON.stringify(EXAMPLE_TWO_MONTH));
  }

  function persistLedger() {
    try {
      localStorage.setItem(STORAGE_KEY, M.exportJson(ledger));
    } catch (_err) {
      // Ignore storage quota errors
    }
  }

  function showStatus(message, isError) {
    statusBanner.textContent = message;
    statusBanner.className = `status-banner no-print ${isError ? 'error' : 'ok'}`;
    statusBanner.hidden = false;
  }

  function fmt(num, unit) {
    const decimals = unit === 'in' ? 2 : 1;
    return num.toFixed(decimals);
  }

  function render() {
    const summary = M.summarizeLedger(ledger);
    const unit = summary.displayUnit;

    yearInput.value = String(ledger.year);
    displayUnitSelect.value = unit;
    summaryYearLabel.textContent = `${ledger.year}${M.isLeapYear(ledger.year) ? ' (leap year, 366 days)' : ' (365 days)'}`;

    document.querySelectorAll('.unit-label').forEach((el) => {
      el.textContent = unit;
    });

    const wettestText = summary.wettestDay
      ? `${fmt(summary.wettestDay.displayAmount, unit)} ${unit} (${summary.wettestDay.date})`
      : 'None';

    const stats = [
      ['YTD Total', `${fmt(summary.ytdTotal, unit)} ${unit}`],
      ['Recorded Days', `${summary.recordedDays} / ${summary.daysInYear}`],
      ['Rainy Days (> 0)', String(summary.rainyDays)],
      ['Recorded Zeroes', String(summary.zeroDays)],
      ['Missed-Day Gaps', String(summary.gapDays)],
      ['Wettest Day', wettestText],
    ];

    summaryGrid.innerHTML = '';
    for (const [label, value] of stats) {
      const box = document.createElement('div');
      box.className = 'stat-box';
      const lbl = document.createElement('div');
      lbl.className = 'stat-label';
      lbl.textContent = label;
      const val = document.createElement('div');
      val.className = 'stat-value';
      val.textContent = value;
      box.appendChild(lbl);
      box.appendChild(val);
      summaryGrid.appendChild(box);
    }

    monthlyTbody.innerHTML = '';
    for (const m of summary.months) {
      const tr = document.createElement('tr');

      const cells = [
        m.name,
        String(m.daysInMonth),
        String(m.recordedDays),
        String(m.gapDays),
        String(m.zeroDays),
        String(m.rainyDays),
        fmt(m.total, unit),
      ];
      for (const text of cells) {
        const td = document.createElement('td');
        td.textContent = text;
        tr.appendChild(td);
      }

      const normalTd = document.createElement('td');
      const normalInput = document.createElement('input');
      normalInput.type = 'number';
      normalInput.min = '0';
      normalInput.step = 'any';
      normalInput.className = 'normal-input';
      normalInput.placeholder = '—';
      normalInput.value = m.normal === null ? '' : fmt(m.normal, unit);
      normalInput.setAttribute('aria-label', `${m.name} normal rainfall in ${unit}`);
      normalInput.addEventListener('change', () => {
        try {
          const raw = normalInput.value.trim();
          ledger = M.setMonthlyNormal(ledger, m.month, raw === '' ? null : raw, unit);
          persistLedger();
          render();
        } catch (err) {
          showStatus(err.message, true);
        }
      });
      normalTd.appendChild(normalInput);
      tr.appendChild(normalTd);

      const deltaTd = document.createElement('td');
      if (m.deltaFromNormal === null) {
        deltaTd.textContent = '—';
      } else {
        const sign = m.deltaFromNormal >= 0 ? '+' : '';
        deltaTd.textContent = `${sign}${fmt(m.deltaFromNormal, unit)}`;
      }
      tr.appendChild(deltaTd);

      monthlyTbody.appendChild(tr);
    }

    const sortedDates = Object.keys(ledger.entries).sort();
    logTbody.innerHTML = '';
    if (sortedDates.length === 0) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 6;
      td.textContent = 'No readings recorded yet. All days are currently missed-day gaps.';
      tr.appendChild(td);
      logTbody.appendChild(tr);
    } else {
      for (const date of sortedDates) {
        const entry = ledger.entries[date];
        const tr = document.createElement('tr');

        const dateTd = document.createElement('td');
        dateTd.textContent = entry.date;
        tr.appendChild(dateTd);

        const enteredTd = document.createElement('td');
        enteredTd.textContent = `${entry.amount} ${entry.unit}`;
        tr.appendChild(enteredTd);

        const convTd = document.createElement('td');
        convTd.textContent = `${fmt(M.fromMm(entry.mm, unit), unit)} ${unit}`;
        tr.appendChild(convTd);

        const statusTd = document.createElement('td');
        statusTd.textContent = entry.mm === 0 ? 'Recorded zero' : 'Rainy';
        tr.appendChild(statusTd);

        const noteTd = document.createElement('td');
        noteTd.textContent = entry.note || '';
        tr.appendChild(noteTd);

        const actionTd = document.createElement('td');
        actionTd.className = 'no-print';
        const delBtn = document.createElement('button');
        delBtn.type = 'button';
        delBtn.className = 'danger-btn small-btn';
        delBtn.textContent = 'Delete';
        delBtn.addEventListener('click', () => {
          ledger = M.removeReading(ledger, entry.date);
          persistLedger();
          render();
          showStatus(`Removed reading for ${entry.date} (now a missed-day gap).`, false);
        });
        actionTd.appendChild(delBtn);
        tr.appendChild(actionTd);

        logTbody.appendChild(tr);
      }
    }
  }

  function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  readingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    try {
      const existed = Boolean(ledger.entries[readingDate.value]);
      ledger = M.upsertReading(ledger, {
        date: readingDate.value,
        amount: readingAmount.value,
        unit: readingUnit.value,
        note: readingNote.value.trim(),
      });
      persistLedger();
      render();
      showStatus(
        existed
          ? `Updated reading for ${readingDate.value}.`
          : `Saved reading for ${readingDate.value}.`,
        false
      );
      readingAmount.value = '';
      readingNote.value = '';
    } catch (err) {
      showStatus(err.message, true);
    }
  });

  yearInput.addEventListener('change', () => {
    const nextYear = Number(yearInput.value);
    if (!Number.isInteger(nextYear) || nextYear < 1900 || nextYear > 2100) {
      showStatus('Year must be an integer between 1900 and 2100.', true);
      yearInput.value = String(ledger.year);
      return;
    }
    if (nextYear !== ledger.year) {
      ledger = M.createLedger(nextYear, { displayUnit: ledger.displayUnit });
      persistLedger();
      render();
      showStatus(`Switched to empty ${nextYear} ledger.`, false);
    }
  });

  displayUnitSelect.addEventListener('change', () => {
    ledger = M.setDisplayUnit(ledger, displayUnitSelect.value);
    persistLedger();
    render();
  });

  printBtn.addEventListener('click', () => {
    window.print();
  });

  exportJsonBtn.addEventListener('click', () => {
    downloadFile(`rain-ledger-${ledger.year}.json`, M.exportJson(ledger), 'application/json');
    showStatus(`Exported rain-ledger-${ledger.year}.json.`, false);
  });

  exportCsvBtn.addEventListener('click', () => {
    downloadFile(`rain-ledger-${ledger.year}.csv`, M.exportCsv(ledger), 'text/csv');
    showStatus(`Exported rain-ledger-${ledger.year}.csv.`, false);
  });

  importFileInput.addEventListener('change', async () => {
    const file = importFileInput.files && importFileInput.files[0];
    if (!file) return;
    try {
      const text = await file.text();
      const nextLedger = file.name.toLowerCase().endsWith('.csv')
        ? M.importCsv(text, ledger.year, ledger.displayUnit)
        : M.importJson(text);
      ledger = nextLedger;
      persistLedger();
      render();
      showStatus(`Imported ${file.name} (${Object.keys(ledger.entries).length} readings).`, false);
    } catch (err) {
      showStatus(`Import rejected (current data preserved): ${err.message}`, true);
    } finally {
      importFileInput.value = '';
    }
  });

  loadExampleBtn.addEventListener('click', () => {
    ledger = M.importJson(JSON.stringify(EXAMPLE_TWO_MONTH));
    persistLedger();
    render();
    showStatus('Loaded 2025 two-month synthetic example (10 readings across April–May).', false);
  });

  clearBtn.addEventListener('click', () => {
    ledger = M.createLedger(ledger.year, { displayUnit: ledger.displayUnit });
    persistLedger();
    render();
    showStatus(`Cleared all readings for ${ledger.year}.`, false);
  });

  render();
  if (loadedSampleOnStart) {
    showStatus('Sample 2-month ledger loaded (10 readings across April–May 2025). Add readings, change year, or Clear Year to start fresh.', false);
  }
})();
