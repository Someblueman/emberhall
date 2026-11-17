/* Original drawings and staging: Hawthorn, actual wake 123eaae9, 17 Nov 2026. */
(function (root) {
  'use strict';
  // Wing contours share cubic control points so the six drawings can inbetween.
  // Each is a hand-authored pose, in local moth coordinates, not a physics model.
  const poses = [
    { time: 0, x: 122, y: 259, tilt: -18, reach: 0, feeler: -3,
      lanternX: 440, lanternY: 205, lanternTilt: -6, shutter: 0,
      wing: [-11,-30,-78,-89,-88,-45,-96,-3,-53,30,-12,19],
      caption: 'A small moth, wings spread, turns toward a hanging light.' },
    { time: .48, x: 228, y: 225, tilt: 10, reach: .45, feeler: 2,
      lanternX: 503, lanternY: 178, lanternTilt: 8, shutter: 0,
      wing: [-8,-24,-36,-78,-44,-55,-53,-18,-25,25,-9,17],
      caption: 'The moth lifts, its front legs reaching toward the light.' },
    { time: 1.05, x: 359, y: 194, tilt: 19, reach: 1, feeler: 7,
      lanternX: 594, lanternY: 160, lanternTilt: -9, shutter: 0,
      wing: [-13,-34,-80,-92,-93,-40,-92,3,-55,39,-12,19],
      caption: 'Wide wings carry the moth upward; its hands almost cup the glow.' },
    { time: 1.62, x: 490, y: 212, tilt: 26, reach: 1, feeler: 12,
      lanternX: 712, lanternY: 196, lanternTilt: 6, shutter: .12,
      wing: [-7,-31,-18,-78,-25,-54,-32,-17,-19,23,-8,18],
      caption: 'The lantern passes into a window. The moth stretches after it.' },
    { time: 2.24, x: 568, y: 265, tilt: -5, reach: .7, feeler: 1,
      lanternX: 734, lanternY: 231, lanternTilt: -2, shutter: .81,
      wing: [-10,-26,-62,-63,-72,-25,-69,12,-41,35,-11,20],
      caption: 'A shutter closes across the light; the moth brakes above the sill.' },
    { time: 3, x: 600, y: 333, tilt: -18, reach: .1, feeler: -18,
      lanternX: 734, lanternY: 231, lanternTilt: 0, shutter: 1,
      wing: [-7,-28,-19,-58,-25,-41,-29,-7,-17,24,-8,22],
      caption: 'The moth rests on the sill, its wings folded and antennae lowered.' }
  ];
  const shot = { duration: 3, author: 'Hawthorn', poses };
  if (typeof module !== 'undefined' && module.exports) module.exports = shot;
  else root.LanternShotOne = shot;
}(typeof window === 'undefined' ? globalThis : window));
