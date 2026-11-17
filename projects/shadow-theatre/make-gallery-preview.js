/*
 * Deterministic Gallery preview for Shadow Theatre.
 *
 * Renders the shipped "Clipped Horizon" challenge exactly as the exhibit's
 * own model computes it: scene-core.js supplies the props, the projected
 * rays and the merged shadow intervals, and this file only draws them.
 * Run `node make-gallery-preview.js` in this directory to regenerate
 * gallery-preview.svg; the committed SVG must match this output byte for
 * byte (tests/test_creations_gallery.py checks).
 */
"use strict";

const ShadowCore = require("./scene-core.js");

const W = 1200;
const H = 760;
// Scene space: x from -6 to 114, y from -8 to 108 (y grows upward).
const X = x => (70 + ((x + 6) / 120) * 1060).toFixed(1);
const Y = y => (712 - ((y + 8) / 116) * 664).toFixed(1);

function svg() {
  const scene = ShadowCore.CHALLENGES.find(c => c.id === "clipped-horizon");
  if (!scene) throw new Error("clipped-horizon challenge missing");
  const { light, screen, props, target } = scene;
  const result = ShadowCore.computeShadows(light, props, screen);
  if (!ShadowCore.matchesTarget(result.intervals, target, scene.tolerance)) {
    throw new Error("preview scene no longer meets its target");
  }

  const clampY = y => Math.max(screen.yMin, Math.min(screen.yMax, y));
  // End a drawn ray where it first reaches the screen line or leaves the plot.
  function rayEnd(throughX, throughY) {
    const dx = throughX - light.x;
    const dy = throughY - light.y;
    let t = (screen.x - light.x) / dx;
    if (dy > 0) t = Math.min(t, (106 - light.y) / dy);
    if (dy < 0) t = Math.min(t, (-6 - light.y) / dy);
    return [light.x + t * dx, light.y + t * dy];
  }

  const parts = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img">`);
  parts.push(`<title>Shadow Theatre stage: a point light casts two dark shadow bands from three props onto a pale screen, matching the amber target brackets.</title>`);
  parts.push(`<rect width="${W}" height="${H}" fill="#1d1a26"/>`);
  // Whole light cone reaching the screen.
  parts.push(`<polygon points="${X(light.x)},${Y(light.y)} ${X(screen.x)},${Y(screen.yMax)} ${X(screen.x)},${Y(screen.yMin)}" fill="#f2c14e" opacity="0.10"/>`);
  // Blocked cones behind each prop, drawn over the lit cone.
  for (const ray of result.rays) {
    parts.push(`<polygon points="${X(light.x)},${Y(light.y)} ${X(screen.x)},${Y(clampY(ray.ya))} ${X(screen.x)},${Y(clampY(ray.yb))}" fill="#12101a" opacity="0.72"/>`);
  }
  // Ray edges through prop endpoints.
  for (const ray of result.rays) {
    for (const endY of [ray.p.yLow, ray.p.yHigh]) {
      const [ex, ey] = rayEnd(ray.p.x, endY);
      parts.push(`<line x1="${X(light.x)}" y1="${Y(light.y)}" x2="${X(ex)}" y2="${Y(ey)}" stroke="#e8b64c" stroke-width="1.6" opacity="0.55"/>`);
    }
  }
  // Screen, then the model's merged shadow intervals as dark bands on it.
  parts.push(`<rect x="${X(screen.x)}" y="${Y(screen.yMax)}" width="16" height="${(Y(screen.yMin) - Y(screen.yMax)).toFixed(1)}" fill="#e8dfc8"/>`);
  for (const [a, b] of result.intervals) {
    parts.push(`<rect x="${X(screen.x)}" y="${Y(b)}" width="16" height="${(Y(a) - Y(b)).toFixed(1)}" fill="#17131f"/>`);
  }
  // Target brackets just right of the screen.
  for (const [a, b] of target) {
    parts.push(`<rect x="${(Number(X(screen.x)) + 26).toFixed(1)}" y="${Y(b)}" width="10" height="${(Y(a) - Y(b)).toFixed(1)}" fill="none" stroke="#e8b64c" stroke-width="3"/>`);
  }
  // Props as silhouettes on stands above the floor line.
  parts.push(`<line x1="${X(-4)}" y1="${Y(-4)}" x2="${X(112)}" y2="${Y(-4)}" stroke="#4a4258" stroke-width="2"/>`);
  for (const p of props) {
    parts.push(`<line x1="${X(p.x)}" y1="${Y(-4)}" x2="${X(p.x)}" y2="${Y(p.yLow)}" stroke="#4a4258" stroke-width="3"/>`);
    parts.push(`<rect x="${(Number(X(p.x)) - 6).toFixed(1)}" y="${Y(p.yHigh)}" width="12" height="${(Y(p.yLow) - Y(p.yHigh)).toFixed(1)}" fill="#050409"/>`);
  }
  // The point light.
  parts.push(`<circle cx="${X(light.x)}" cy="${Y(light.y)}" r="26" fill="#f2c14e" opacity="0.18"/>`);
  parts.push(`<circle cx="${X(light.x)}" cy="${Y(light.y)}" r="11" fill="#ffd97a"/>`);
  // Labels.
  parts.push(`<text x="${X(light.x)}" y="${(Number(Y(light.y)) + 52).toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="21" letter-spacing="3" fill="#cfc4a5">LIGHT</text>`);
  parts.push(`<text x="${(Number(X(screen.x)) + 8).toFixed(1)}" y="${(Number(Y(screen.yMax)) - 16).toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="21" letter-spacing="3" fill="#cfc4a5">SCREEN</text>`);
  parts.push(`<text x="${(Number(X(props[0].x))).toFixed(1)}" y="${(Number(Y(-4)) + 34).toFixed(1)}" text-anchor="middle" font-family="Georgia, serif" font-size="21" letter-spacing="3" fill="#cfc4a5">PROPS</text>`);
  parts.push(`</svg>`);
  return parts.join("\n") + "\n";
}

if (typeof module !== "undefined" && module.exports) module.exports = { svg };
if (typeof require !== "undefined" && require.main === module) {
  require("node:fs").writeFileSync(require("node:path").join(__dirname, "gallery-preview.svg"), svg());
}
