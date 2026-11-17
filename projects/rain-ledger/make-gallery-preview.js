/*
 * Deterministic Gallery preview for Rain Ledger.
 *
 * Loads example_two_month.json through rain_model.js and draws the actual
 * summarizeLedger() figures: YTD total, rainy/zero/gap distinction, April and
 * May totals against normals, and sample log lines.
 * Run `node make-gallery-preview.js` to print the SVG; tests check byte parity.
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const M = require("./rain_model.js");

const W = 1200;
const H = 620;

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function fmt(num, unit) {
  return num.toFixed(unit === "in" ? 2 : 1);
}

function svg() {
  const raw = fs.readFileSync(path.join(__dirname, "example_two_month.json"), "utf8");
  const ledger = M.importJson(raw);
  const summary = M.summarizeLedger(ledger);
  const unit = summary.displayUnit;
  const april = summary.months[3];
  const may = summary.months[4];
  const wettest = summary.wettestDay;

  const parts = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img">`);
  parts.push(`<title>Rain Ledger 2025 summary: ${fmt(summary.ytdTotal, unit)} ${unit} across ${summary.recordedDays} recorded days (${summary.rainyDays} rainy, ${summary.zeroDays} zeroes, ${summary.gapDays} gaps) with April and May totals compared against normals.</title>`);
  parts.push(`<rect width="${W}" height="${H}" fill="#f6f7f9"/>`);
  parts.push(`<rect x="20" y="20" width="${W - 40}" height="${H - 40}" rx="16" fill="#ffffff" stroke="#d8dee6" stroke-width="2"/>`);

  // Header
  parts.push(`<text x="52" y="64" font-family="system-ui, sans-serif" font-size="14" font-weight="700" letter-spacing="1.6" fill="#1d5b79">RAIN LEDGER · ${summary.year} SINGLE-GAUGE YEAR LOG</text>`);
  parts.push(`<text x="52" y="102" font-family="system-ui, sans-serif" font-size="30" font-weight="700" fill="#1b2430">April–May sample ledger (${fmt(summary.ytdTotal, unit)} ${unit})</text>`);
  parts.push(`<text x="1148" y="64" text-anchor="end" font-family="system-ui, sans-serif" font-size="16" font-weight="600" fill="#5a6573">${summary.recordedDays} / ${summary.daysInYear} days recorded</text>`);

  // Four stat cards
  const stats = [
    ["YTD TOTAL", `${fmt(summary.ytdTotal, unit)} ${unit}`, `${summary.rainyDays} rainy · ${summary.zeroDays} dry zeroes`],
    ["MISSED-DAY GAPS", `${summary.gapDays}`, "Unrecorded days stay distinct from 0"],
    ["WETTEST DAY", `${fmt(wettest.displayAmount, unit)} ${unit}`, `${wettest.date} (mixed mm &amp; in)`],
    ["APRIL &amp; MAY NORMALS", `${fmt(april.total + may.total, unit)} / ${fmt(april.normal + may.normal, unit)} ${unit}`, "Below normal in both months"],
  ];
  stats.forEach(([label, val, sub], i) => {
    const sx = 52 + i * 278;
    parts.push(`<rect x="${sx}" y="128" width="262" height="106" rx="10" fill="#f6f7f9" stroke="#d8dee6" stroke-width="1.5"/>`);
    parts.push(`<text x="${sx + 18}" y="156" font-family="system-ui, sans-serif" font-size="12" font-weight="700" letter-spacing="1" fill="#5a6573">${label}</text>`);
    parts.push(`<text x="${sx + 18}" y="192" font-family="system-ui, sans-serif" font-size="26" font-weight="700" fill="#1b2430">${val}</text>`);
    parts.push(`<text x="${sx + 18}" y="218" font-family="system-ui, sans-serif" font-size="12.5" fill="#5a6573">${sub}</text>`);
  });

  // Left: Monthly comparison bars (April & May vs Normal)
  parts.push(`<rect x="52" y="256" width="530" height="312" rx="12" fill="#f6f7f9" stroke="#d8dee6" stroke-width="1.5"/>`);
  parts.push(`<text x="76" y="290" font-family="system-ui, sans-serif" font-size="15" font-weight="700" fill="#1b2430">Monthly Totals vs Owner Normals (${unit})</text>`);
  const maxVal = Math.max(april.normal, may.normal, april.total, may.total, 1);
  [april, may].forEach((m, idx) => {
    const y0 = 322 + idx * 116;
    const normW = (m.normal / maxVal) * 440;
    const totW = (m.total / maxVal) * 440;
    const sign = m.deltaFromNormal >= 0 ? "+" : "";
    parts.push(`<text x="76" y="${y0}" font-family="system-ui, sans-serif" font-size="16" font-weight="700" fill="#1b2430">${esc(m.name)} (${m.recordedDays}/${m.daysInMonth} days · ${m.zeroDays} zero · ${m.gapDays} gaps)</text>`);
    parts.push(`<text x="76" y="${y0 + 22}" font-family="system-ui, sans-serif" font-size="13.5" fill="#5a6573">Recorded ${fmt(m.total, unit)} ${unit} vs normal ${fmt(m.normal, unit)} ${unit} (${sign}${fmt(m.deltaFromNormal, unit)} ${unit})</text>`);
    parts.push(`<rect x="76" y="${y0 + 34}" width="${normW.toFixed(1)}" height="28" rx="6" fill="#dce5ed" stroke="#9fb3c4" stroke-width="1.2"/>`);
    parts.push(`<rect x="76" y="${y0 + 34}" width="${totW.toFixed(1)}" height="28" rx="6" fill="#1d5b79"/>`);
  });
  parts.push(`<rect x="76" y="542" width="16" height="12" rx="3" fill="#1d5b79"/><text x="98" y="553" font-family="system-ui, sans-serif" font-size="12.5" fill="#5a6573">Recorded total</text>`);
  parts.push(`<rect x="210" y="542" width="16" height="12" rx="3" fill="#dce5ed" stroke="#9fb3c4"/><text x="232" y="553" font-family="system-ui, sans-serif" font-size="12.5" fill="#5a6573">Owner normal</text>`);

  // Right: Sample daily log rows (showing mm, in, and recorded zero)
  parts.push(`<rect x="606" y="256" width="542" height="312" rx="12" fill="#f6f7f9" stroke="#d8dee6" stroke-width="1.5"/>`);
  parts.push(`<text x="630" y="290" font-family="system-ui, sans-serif" font-size="15" font-weight="700" fill="#1b2430">Sample Daily Readings (mixed units &amp; dry zeroes)</text>`);
  const sampleDates = ["2025-04-01", "2025-04-02", "2025-04-03", "2025-05-05", "2025-05-10"];
  sampleDates.forEach((date, i) => {
    const entry = ledger.entries[date];
    const ry = 310 + i * 48;
    const isZero = entry.mm === 0;
    parts.push(`<rect x="628" y="${ry}" width="498" height="38" rx="7" fill="#ffffff" stroke="#d8dee6" stroke-width="1"/>`);
    parts.push(`<text x="644" y="${ry + 24}" font-family="ui-monospace, Menlo, monospace" font-size="13.5" fill="#1b2430">${esc(entry.date)}</text>`);
    parts.push(`<text x="766" y="${ry + 24}" font-family="system-ui, sans-serif" font-size="13.5" font-weight="600" fill="#1d5b79">${esc(entry.amount)} ${esc(entry.unit)} (${fmt(M.fromMm(entry.mm, unit), unit)} ${unit})</text>`);
    parts.push(`<rect x="974" y="${ry + 8}" width="136" height="22" rx="11" fill="${isZero ? "#eef2f6" : "#e6f4ea"}"/>`);
    parts.push(`<text x="1042" y="${ry + 23}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="${isZero ? "#5a6573" : "#1e6b34"}">${isZero ? "Recorded zero" : "Rainy day"}</text>`);
  });

  parts.push(`</svg>`);
  return parts.join("\n") + "\n";
}

if (typeof module !== "undefined" && module.exports) module.exports = { svg };
if (typeof require !== "undefined" && require.main === module) {
  if (process.argv.includes("--write")) {
    fs.writeFileSync(path.join(__dirname, "gallery-preview.svg"), svg());
  } else {
    process.stdout.write(svg());
  }
}
