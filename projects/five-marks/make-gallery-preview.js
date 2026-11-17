/*
 * Deterministic Gallery preview for Five Marks on a Line.
 *
 * Draws only what the shipped exhibit model returns: the five-mark shape
 * for b = 5 from exhibit.js `shape`, and the winning starts from its
 * `lower` construction, after checking with its `collision` that no two
 * drawn copies share a mark, including the first copy of the next period.
 * Run `node make-gallery-preview.js` in this directory to regenerate
 * gallery-preview.svg; the committed SVG must match this output byte for
 * byte (tests/test_creations_gallery.py checks).
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const model = require("./exhibit.js");

const W = 1200;
const H = 620;
const B = 5;
const INK = "#202d37";
const PAPER = "#f5f1e7";
const TEAL = "#116c67";
const RUST = "#a33c30";
const GOLD = "#e1ad3c";
const FAINT = "#c8c9bd";

function checkedPacking() {
  const s = model.shape(B);
  const starts = model.lower(B);
  const n = 5 * B + 4;
  const drawn = [...starts, starts[0] + n];
  for (const x of drawn) {
    for (const y of drawn) {
      if (x < y && model.collision(B, x, y)) {
        throw new Error(`starts ${x} and ${y} share a mark`);
      }
    }
  }
  return { s, starts, n };
}

function svg() {
  const { s, starts, n } = checkedPacking();
  const parts = [];
  const text = (x, y, value, fill, size, anchor = "middle", extra = "") =>
    parts.push(`<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="Georgia, serif" font-size="${size}" fill="${fill}"${extra}>${value}</text>`);

  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img">`);
  parts.push(`<title>Five gold marks at ${s.join(", ")} with gaps ${B + 2}, ${B + 2}, ${B}, ${B}, then five teal copies placed at starts ${starts.join(", ")} with no shared mark, repeating every ${n} integers.</title>`);
  parts.push(`<rect width="${W}" height="${H}" fill="${PAPER}"/>`);

  // The shape itself, on the exhibit's dark shape card.
  parts.push(`<rect x="40" y="36" width="1120" height="196" rx="4" fill="${INK}"/>`);
  text(600, 84, "THE FIVE MARKS", "#d7d8cc", 21, "middle", ` letter-spacing="3"`);
  const shapeScale = 1000 / s[4];
  const shapeX = v => 100 + v * shapeScale;
  parts.push(`<line x1="100" y1="140" x2="1100" y2="140" stroke="${FAINT}" stroke-width="2"/>`);
  s.forEach((v, i) => {
    parts.push(`<circle cx="${shapeX(v).toFixed(1)}" cy="140" r="13" fill="${i ? GOLD : PAPER}"/>`);
    text(shapeX(v).toFixed(1), 196, v, PAPER, 24);
    if (i < 4) {
      const mid = shapeX(v) + (s[i + 1] - v) * shapeScale / 2;
      text(mid.toFixed(1), 120, `gap ${i < 2 ? B + 2 : B}`, "#d7d8cc", 19, "middle", ` font-style="italic"`);
    }
  });

  // The winning packing: one row per start, marks joined on a faint line.
  text(600, 292, "THE WINNING PATTERN", INK, 21, "middle", ` letter-spacing="3"`);
  const end = starts[starts.length - 1] + s[4] + 2;
  const scale = 980 / end;
  const px = v => 150 + v * scale;
  starts.forEach((start, row) => {
    const y = 340 + row * 44;
    text(132, y + 6, `start ${start}`, INK, 19, "end");
    parts.push(`<line x1="${px(start).toFixed(1)}" y1="${y}" x2="${px(start + s[4]).toFixed(1)}" y2="${y}" stroke="${FAINT}" stroke-width="2"/>`);
    s.forEach(v => {
      parts.push(`<circle cx="${px(start + v).toFixed(1)}" cy="${y}" r="7" fill="${TEAL}"/>`);
    });
  });
  const seamY2 = 340 + (starts.length - 1) * 44;
  parts.push(`<line x1="${px(n).toFixed(1)}" y1="318" x2="${px(n).toFixed(1)}" y2="${seamY2 + 18}" stroke="${RUST}" stroke-width="2" stroke-dasharray="6 5"/>`);
  text(px(n).toFixed(1), seamY2 + 48, `repeats every ${n}`, RUST, 19, "middle", ` font-style="italic"`);

  text(600, 596, `${starts.length} starts in every ${n} integers · no two copies share a mark`, INK, 22);
  parts.push(`</svg>`);
  return parts.join("\n") + "\n";
}

if (typeof module !== "undefined" && module.exports) module.exports = { svg };
if (typeof require !== "undefined" && require.main === module) {
  fs.writeFileSync(path.join(__dirname, "gallery-preview.svg"), svg());
}
