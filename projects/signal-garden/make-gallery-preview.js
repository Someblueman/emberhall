/*
 * Deterministic Gallery preview for Signal Garden.
 *
 * Runs the lesson's own model.js on the opening tile from garden.js under
 * one four-bit burst, and draws what the model returns: the original tile,
 * the consecutive layout's damaged recovery, and the interleaved layout's
 * whole recovery. Run `node make-gallery-preview.js` in this directory to
 * regenerate gallery-preview.svg; the committed SVG must match this output
 * byte for byte (tests/test_creations_gallery.py checks).
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const SignalGarden = require("./model.js");

const W = 1200;
const H = 560;

function openingTile() {
  const source = fs.readFileSync(path.join(__dirname, "garden.js"), "utf8");
  const match = source.match(/const seed = \[([0-9,\s]+)\]/);
  if (!match) throw new Error("garden.js seed tile not found");
  return match[1].split(",").map(s => Number(s.trim()));
}

// First four-bit burst where interleaving recovers the tile whole while the
// consecutive layout loses at least two pixels. Deterministic for a given
// tile and model; throws if the model's guarantee ever changes.
function tellingBurst(picture) {
  for (let start = 0; start + 4 <= 28; start += 1) {
    const consecutive = SignalGarden.run(picture, start, 4, "consecutive");
    const interleaved = SignalGarden.run(picture, start, 4, "interleaved");
    if (interleaved.matches && consecutive.changed >= 2) {
      return { start, consecutive, interleaved };
    }
  }
  throw new Error("no telling burst found");
}

function tile(parts, x0, bits, original) {
  const cell = 64;
  const gap = 8;
  bits.forEach((bit, i) => {
    const x = x0 + (i % 4) * (cell + gap);
    const y = 90 + Math.floor(i / 4) * (cell + gap);
    parts.push(`<rect x="${x}" y="${y}" width="${cell}" height="${cell}" rx="6" fill="${bit ? "#22301f" : "#fffdf4"}" stroke="#cbbf9d" stroke-width="2"/>`);
    if (original && bit !== original[i]) {
      parts.push(`<rect x="${x + 4}" y="${y + 4}" width="${cell - 8}" height="${cell - 8}" rx="4" fill="none" stroke="#c0392b" stroke-width="5"/>`);
    }
  });
}

function svg() {
  const picture = openingTile();
  const { start, consecutive, interleaved } = tellingBurst(picture);
  const parts = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img">`);
  parts.push(`<title>Signal Garden triptych: the opening 4 by 4 tile, the same tile after a four-bit burst sent in a row with ${consecutive.changed} pixels wrong ringed in red, and the tile recovered whole when the bits are woven.</title>`);
  parts.push(`<rect width="${W}" height="${H}" fill="#f7f1df"/>`);

  const panels = [
    { x: 80, bits: picture, original: null, title: "ORIGINAL", note: "the opening tile" },
    { x: 460, bits: consecutive.recovered, original: picture, title: "SENT IN A ROW", note: `${consecutive.changed} pixels wrong` },
    { x: 840, bits: interleaved.recovered, original: null, title: "WOVEN BETWEEN ROWS", note: "recovered whole" },
  ];
  for (const panel of panels) {
    tile(parts, panel.x, panel.bits, panel.original);
    parts.push(`<text x="${panel.x + 140}" y="424" text-anchor="middle" font-family="Georgia, serif" font-size="24" letter-spacing="2" fill="#22301f">${panel.title}</text>`);
    parts.push(`<text x="${panel.x + 140}" y="456" text-anchor="middle" font-family="Georgia, serif" font-size="20" font-style="italic" fill="#6b6242">${panel.note}</text>`);
  }

  // The shared burst along the 28 channel positions.
  parts.push(`<text x="80" y="500" font-family="Georgia, serif" font-size="19" font-style="italic" fill="#6b6242">the same four flipped bits in both sendings (positions ${start + 1} to ${start + 4} of 28)</text>`);
  const step = 1040 / 28;
  for (let i = 0; i < 28; i += 1) {
    const flipped = i >= start && i < start + 4;
    parts.push(`<rect x="${(80 + i * step).toFixed(1)}" y="514" width="${(step - 8).toFixed(1)}" height="22" rx="4" fill="${flipped ? "#c0392b" : "#d8cfb4"}"/>`);
  }
  parts.push(`</svg>`);
  return parts.join("\n") + "\n";
}

if (typeof module !== "undefined" && module.exports) module.exports = { svg };
if (typeof require !== "undefined" && require.main === module) {
  fs.writeFileSync(path.join(__dirname, "gallery-preview.svg"), svg());
}
