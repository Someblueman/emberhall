// A still from the shipped film, not a separately drawn advertisement.
'use strict';
const film = require('./film.js');

function svg() {
  const still = film.frameSVG(film.poseAt(film.duration), 'gallery-film', true)
    .replace('<svg ', '<svg x="40" y="104" width="1120" height="548" ');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700" role="img" aria-labelledby="gallery-title gallery-desc">
  <title id="gallery-title">Lantern Loop — one small light</title>
  <desc id="gallery-desc">A still from the final drawing: two moths rest on a window sill with their hands beneath one warm lantern.</desc>
  <rect width="1200" height="700" fill="#0d2228"/>
  <text x="40" y="62" fill="#ecdfb9" font-family="Georgia,serif" font-size="40">Lantern Loop</text>
  <text x="1160" y="60" text-anchor="end" fill="#b9c9bd" font-family="system-ui,sans-serif" font-size="22">A six-second silent miniature</text>
  ${still}
  <rect x="40" y="104" width="1120" height="548" fill="none" stroke="#658078" stroke-width="2"/>
  <text x="40" y="683" fill="#b9c9bd" font-family="Georgia,serif" font-size="21">One small light. A film made across separate wakes.</text>
</svg>\n`;
}

module.exports = {svg};
if (require.main === module) process.stdout.write(svg());
