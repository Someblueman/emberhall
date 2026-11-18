#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const rig = require('./stage-rig.js');

function markCoord(index) {
  const row = Math.floor(index / 4);
  const col = index % 4;
  const y = 165 + row * 22;
  const halfSpan = 96 + row * 12;
  const x = 180 + ((col - 1.5) / 1.5) * halfSpan;
  return { x, y };
}

function buildState() {
  const state = rig.createShowState({ leadRig: 'rook', initialCast: {} });
  rig.placePuppet(state, 'A', 0);
  rig.placePuppet(state, 'B', 1);
  rig.placePuppet(state, 'C', 2);
  rig.placePuppet(state, 'D', 3);
  rig.startHatPlay(state, 'A');
  for (const target of ['B', 'C', 'A', 'D', 'B', 'C', 'D']) {
    rig.throwHat(state, target);
  }
  return rig.stepTake(state, state.beats.length - 1);
}

function puppetSvg(id, x, y, isHolding) {
  const meta = rig.PUPPET_META[id];
  const arm = isHolding
    ? '<path d="M-7 -22 L-13 -32 M7 -22 L14 -33" stroke="#f5dfc0" stroke-width="2.2" stroke-linecap="round"/>'
    : '<path d="M-7 -22 L-11 -14 M7 -22 L11 -14" stroke="#f5dfc0" stroke-width="2.1" stroke-linecap="round"/>';
  let body = '';
  if (id === 'A') body = `<path d="M-8 -4 L-6 -26 L6 -26 L8 -4 L4 -4 L3 -13 L-3 -13 L-4 -4 Z" fill="${meta.color}" stroke="#f7efd9" stroke-width="1"/>`;
  else if (id === 'B') body = `<path d="M-10 -6 L-4 -25 L4 -25 L10 -6 Z" fill="${meta.color}" stroke="#f7efd9" stroke-width="1"/>`;
  else if (id === 'C') body = `<path d="M-7 -4 L-7 -25 L7 -25 L7 -4 L2 -4 L0 -12 L-2 -4 Z" fill="${meta.color}" stroke="#f7efd9" stroke-width="1"/>`;
  else body = `<path d="M-6 -4 L-8 -23 L8 -23 L6 -4 Z" fill="${meta.color}" stroke="#f7efd9" stroke-width="1"/>`;
  const ring = isHolding ? '<circle cx="0" cy="-31" r="9.5" fill="none" stroke="#f4c867" stroke-width="1.6"/>' : '';
  return `<g transform="translate(${x.toFixed(1)}, ${y.toFixed(1)})">
    <ellipse cx="0" cy="1" rx="11" ry="3.5" fill="rgba(34,25,20,0.25)"/>
    ${arm}${body}
    <circle cx="0" cy="-31" r="5.8" fill="#f5dfc0" stroke="#221914" stroke-width="1.1"/>
    <circle cx="-2" cy="-31.5" r="0.9" fill="#221914"/><circle cx="2" cy="-31.5" r="0.9" fill="#221914"/>
    <rect x="-7" y="-12" width="14" height="10" rx="2" fill="#221914" stroke="#f4ebd7" stroke-width="0.8"/>
    <text x="0" y="-4.5" text-anchor="middle" fill="#fff6e5" font-size="7.5" font-weight="700" font-family="Helvetica Neue, Arial, sans-serif">${id}</text>
    ${ring}
  </g>`;
}

function bowlerSvg(x, y, scale, tilt) {
  return `<g transform="translate(${x.toFixed(1)}, ${y.toFixed(1)}) rotate(${tilt}) scale(${scale})">
    <path d="M-12 2 Q0 5 12 2 L13 4 Q0 8 -13 4 Z" fill="#1b1614" stroke="#f4ebd7" stroke-width="0.9"/>
    <path d="M-8 2 C-8 -9 8 -9 8 2 Z" fill="#231d1a" stroke="#f4ebd7" stroke-width="0.8"/>
    <path d="M-7.8 0.2 H7.8" stroke="#b7832e" stroke-width="1.6"/>
  </g>`;
}

function renderStagePanel(rigName, offsetX, state, snap) {
  const stageSnap = snap[rigName];
  const slipped = stageSnap.landedOnDrummer;
  const label = rigName === 'rook' ? 'Stage I · Caught by D' : 'Stage II · Bowler on Drummer';
  const marks = [];
  for (let i = 0; i < 16; i += 1) {
    const c = markCoord(i);
    marks.push(`<ellipse cx="${c.x.toFixed(1)}" cy="${c.y.toFixed(1)}" rx="10" ry="4" fill="rgba(255,248,231,0.45)" stroke="#6c4d2d" stroke-width="1"/>`);
  }
  let wire = '';
  if (stageSnap.litWire) {
    const fc = markCoord(state.marks[rigName][stageSnap.litWire.from]);
    const tc = markCoord(state.marks[rigName][stageSnap.litWire.to]);
    const y1 = fc.y - 34;
    const y2 = tc.y - 34;
    const mx = (fc.x + tc.x) / 2;
    const cy = Math.min(y1, y2) - 34;
    const d = `M${fc.x.toFixed(1)} ${y1.toFixed(1)} Q${mx.toFixed(1)} ${cy.toFixed(1)} ${tc.x.toFixed(1)} ${y2.toFixed(1)}`;
    wire = `<path d="${d}" fill="none" stroke="#f4c867" stroke-width="6" opacity="0.4" stroke-linecap="round"/><path d="${d}" fill="none" stroke="#f4c867" stroke-width="2.5" stroke-linecap="round"/>`;
  } else if (slipped && snap.from) {
    const fc = markCoord(state.marks[rigName][snap.from]);
    wire = `<path d="M${fc.x.toFixed(1)} ${(fc.y - 34).toFixed(1)} Q${((fc.x + 180) / 2).toFixed(1)} 165 180 264" fill="none" stroke="#b5372f" stroke-width="2" stroke-dasharray="4 4"/>`;
  }
  const puppets = state.castOrder
    .slice()
    .sort((a, b) => markCoord(state.marks[rigName][a]).y - markCoord(state.marks[rigName][b]).y)
    .map((p) => {
      const c = markCoord(state.marks[rigName][p]);
      return puppetSvg(p, c.x, c.y, stageSnap.holder === p);
    })
    .join('\n');
  const hatOnHolder = stageSnap.holder
    ? (() => {
        const hc = markCoord(state.marks[rigName][stageSnap.holder]);
        return bowlerSvg(hc.x, hc.y - 38, 0.9, -6);
      })()
    : '';
  const drummer = `<g transform="translate(180, 294)">
    <ellipse cx="0" cy="20" rx="34" ry="7" fill="#0e0a08"/>
    <rect x="-22" y="2" width="44" height="18" rx="3" fill="#a63429" stroke="#f4c867" stroke-width="1.5"/>
    <ellipse cx="0" cy="2" rx="22" ry="5" fill="#efe0be" stroke="#4c341a" stroke-width="1.2"/>
    <path d="${slipped ? 'M-16 2 L-13 -14 L13 -14 L16 2 Z' : 'M-15 2 L-11 -18 L11 -18 L15 2 Z'}" fill="#2f3d4c" stroke="#d8c5a3" stroke-width="1"/>
    <circle cx="0" cy="${slipped ? -21 : -24}" r="8.5" fill="#f5dfc0" stroke="#1b1411" stroke-width="1.2"/>
    ${slipped
      ? `<line x1="-12" y1="-8" x2="-25" y2="0" stroke="#d6b681" stroke-width="2"/><line x1="12" y1="-8" x2="26" y2="-2" stroke="#d6b681" stroke-width="2"/>${bowlerSvg(0, -24, 1.12, -4)}`
      : '<circle cx="-3" cy="-25" r="1.3" fill="#1b1411"/><circle cx="3" cy="-25" r="1.3" fill="#1b1411"/><line x1="-11" y1="-10" x2="-20" y2="-35" stroke="#f3d49b" stroke-width="2.2"/><line x1="11" y1="-10" x2="20" y2="-35" stroke="#f3d49b" stroke-width="2.2"/>'
    }
  </g>`;

  return `<g transform="translate(${offsetX}, 24)">
    <rect width="360" height="340" rx="6" fill="#231915"/>
    <rect x="20" y="18" width="320" height="232" fill="#e9dab8"/>
    <path d="M20 144 L76 102 L134 138 L194 92 L266 134 L340 106 L340 250 L20 250 Z" fill="#d8c39b" opacity="0.65"/>
    <polygon points="34,152 326,152 344,244 16,244" fill="#c79e65" stroke="#5b3f24" stroke-width="1.5"/>
    <polygon points="42,157 318,157 332,238 28,238" fill="#d7b37c"/>
    ${marks.join('')}
    ${wire}
    ${puppets}
    <rect x="14" y="242" width="332" height="14" rx="3" fill="#472d1c"/>
    <rect x="20" y="256" width="320" height="72" rx="4" fill="#1b1411"/>
    ${drummer}
    <path d="M0 0 H46 Q34 115 26 244 H0 Z" fill="#7b1e1b"/>
    <path d="M360 0 H314 Q326 115 334 244 H360 Z" fill="#7b1e1b"/>
    <path d="M0 0 H360 V28 Q315 44 270 28 Q225 46 180 28 Q135 46 90 28 Q45 44 0 28 Z" fill="#771c19" stroke="#3c0d0c" stroke-width="1.5"/>
    <path d="M0 28 Q45 44 90 28 Q135 46 180 28 Q225 46 270 28 Q315 44 360 28" fill="none" stroke="#d9a54a" stroke-width="2"/>
    ${hatOnHolder}
    <text x="180" y="356" text-anchor="middle" fill="#221914" font-size="13" font-weight="700" font-family="Georgia, serif">${label}</text>
  </g>`;
}

function generateSvg() {
  const state = rig.createShowState({ leadRig: 'rook', initialCast: {} });
  rig.placePuppet(state, 'A', 0);
  rig.placePuppet(state, 'B', 1);
  rig.placePuppet(state, 'C', 2);
  rig.placePuppet(state, 'D', 3);
  rig.startHatPlay(state, 'A');
  for (const target of ['B', 'C', 'A', 'D', 'B', 'C', 'D']) {
    rig.throwHat(state, target);
  }
  const snap = rig.stepTake(state, state.beats.length - 1);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 390" width="760" height="390">
  <rect width="760" height="390" fill="#efe3ca"/>
  <rect x="6" y="6" width="748" height="378" fill="none" stroke="#221914" stroke-width="2"/>
  ${renderStagePanel('rook', 14, state, snap)}
  ${renderStagePanel('shrikhande', 386, state, snap)}
</svg>
`;
}

if (require.main === module) {
  const outPath = path.join(__dirname, 'gallery-preview.svg');
  fs.writeFileSync(outPath, generateSvg(), 'utf8');
}

module.exports = { generateSvg };
