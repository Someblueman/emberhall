/* Generate projects/night-ferry/gallery-preview.svg deterministically from case JSON.
 * Regenerate from the repository root with:
 *   node projects/night-ferry/make-gallery-preview.js > projects/night-ferry/gallery-preview.svg
 */
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const reach = require('./player/reach-model.js');

const caseDir = path.join(__dirname, 'case');
const truth = JSON.parse(fs.readFileSync(path.join(caseDir, 'truth-sheet.json'), 'utf8'));
const landing = JSON.parse(fs.readFileSync(path.join(caseDir, 'landing-clerk.json'), 'utf8'));
const engine = JSON.parse(fs.readFileSync(path.join(caseDir, 'engine-room.json'), 'utf8'));
const scenes = new Map([
  [landing.id, landing],
  [engine.id, engine],
]);

process.stdout.write(reach.galleryPreviewSvg(truth, scenes));
