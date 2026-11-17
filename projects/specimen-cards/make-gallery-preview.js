/*
 * Deterministic Gallery preview for Specimen Cards.
 *
 * Extracts the shipped SpecimenCards model from index.html, builds the
 * opening sampleDeck() and due queue, and renders the first paired card
 * alongside the 4-card botanical queue.
 * Run `node make-gallery-preview.js` to print the SVG; tests check byte parity.
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const W = 1200;
const H = 620;

function loadModel() {
  const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!match) throw new Error("Specimen Cards inline script not found");
  const context = { module: { exports: {} } };
  vm.runInNewContext(match[1], context, { filename: "specimen-cards-inline.js" });
  return context.module.exports;
}

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function wrapLines(text, maxChars) {
  const words = String(text).split(/\s+/);
  const lines = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  return lines;
}

function svg() {
  const Cards = loadModel();
  const deck = Cards.sampleDeck();
  const due = Cards.queue(deck, 0);
  const active = due[0];
  if (!active) throw new Error("Sample deck has no due card");

  const parts = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img">`);
  parts.push(`<title>Specimen Cards studio: botanical sample deck with ${due.length} cards due now, paired front and back faces, and spaced-repetition grade buttons.</title>`);
  parts.push(`<rect width="${W}" height="${H}" fill="#edf2e8"/>`);
  parts.push(`<rect x="20" y="20" width="${W - 40}" height="${H - 40}" rx="18" fill="#fffdf6" stroke="#b9c8b8" stroke-width="2"/>`);

  // Header
  parts.push(`<text x="52" y="64" font-family="system-ui, sans-serif" font-size="14" font-weight="700" letter-spacing="1.6" fill="#386b52">SPECIMEN CARDS · OFFLINE CARD STUDIO</text>`);
  parts.push(`<text x="52" y="102" font-family="Georgia, serif" font-size="30" fill="#20352e">Botanical sample deck ready to review</text>`);
  parts.push(`<text x="1148" y="64" text-anchor="end" font-family="system-ui, sans-serif" font-size="16" font-weight="600" fill="#386b52">${due.length} due now · ${deck.cards.length} cards total</text>`);

  // Left paired 5 x 3.5 style card
  parts.push(`<rect x="52" y="130" width="676" height="360" rx="14" fill="#ffffff" stroke="#b9c8b8" stroke-width="2"/>`);
  parts.push(`<line x1="390" y1="146" x2="390" y2="474" stroke="#b9c8b8" stroke-width="2" stroke-dasharray="6,6"/>`);
  parts.push(`<text x="80" y="168" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="1.4" fill="#386b52">FRONT · ${esc(active.id.toUpperCase())}</text>`);
  parts.push(`<text x="418" y="168" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="1.4" fill="#386b52">BACK · REVEALED</text>`);

  wrapLines(active.front, 24).forEach((line, idx) => {
    parts.push(`<text x="80" y="${224 + idx * 34}" font-family="Georgia, serif" font-size="23" fill="#20352e">${esc(line)}</text>`);
  });
  wrapLines(active.back, 25).forEach((line, idx) => {
    parts.push(`<text x="418" y="${224 + idx * 34}" font-family="Georgia, serif" font-size="22" fill="#20352e">${esc(line)}</text>`);
  });

  // Grade buttons matching model intervals
  const grades = [
    ["Again · 5m", "#fffdf6", "#386b52", "#386b52"],
    ["Hard · 10m", "#fffdf6", "#386b52", "#386b52"],
    ["Good · 1d", "#386b52", "#386b52", "#ffffff"],
    ["Easy · 4d", "#fffdf6", "#386b52", "#386b52"],
  ];
  grades.forEach(([label, fill, stroke, ink], i) => {
    const gx = 80 + i * 156;
    parts.push(`<rect x="${gx}" y="422" width="142" height="44" rx="8" fill="${fill}" stroke="${stroke}" stroke-width="1.8"/>`);
    parts.push(`<text x="${gx + 71}" y="449" text-anchor="middle" font-family="system-ui, sans-serif" font-size="15" font-weight="600" fill="${ink}">${esc(label)}</text>`);
  });

  // Right queue list from sampleDeck()
  parts.push(`<rect x="752" y="130" width="396" height="426" rx="14" fill="#f7faf4" stroke="#b9c8b8" stroke-width="1.5"/>`);
  parts.push(`<text x="776" y="166" font-family="system-ui, sans-serif" font-size="14" font-weight="700" letter-spacing="1.2" fill="#386b52">DUE QUEUE (BOX 0)</text>`);
  due.forEach((card, i) => {
    const ry = 188 + i * 86;
    const isFirst = i === 0;
    parts.push(`<rect x="774" y="${ry}" width="352" height="74" rx="9" fill="${isFirst ? "#ffffff" : "#edf2e8"}" stroke="${isFirst ? "#386b52" : "#b9c8b8"}" stroke-width="${isFirst ? 2 : 1.2}"/>`);
    parts.push(`<text x="790" y="${ry + 26}" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#386b52">${esc(card.id)} · box ${card.state.box}</text>`);
    const snippet = card.front.length > 38 ? `${card.front.slice(0, 37)}…` : card.front;
    parts.push(`<text x="790" y="${ry + 52}" font-family="Georgia, serif" font-size="16" fill="#20352e">${esc(snippet)}</text>`);
  });

  // Footer note
  parts.push(`<text x="52" y="542" font-family="system-ui, sans-serif" font-size="15" fill="#405b4d">Offline JSON export/import · 5 × 3.5 inch paired print layout · plain text only</text>`);
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
