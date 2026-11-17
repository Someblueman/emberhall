/* Original second-shot drawings: Sorrel, actual wake dc2782e12aaf495ebda8922a4dd2d9ef, 17 Nov 2026. */
(function (root) {
  'use strict';
  // A cut closer to the same sill. The waiting moth keeps Hawthorn's cut pose.
  // The keeper's curled wing, bowed head and two hands shelter the lamp first;
  // its hands open toward the visitor before either moth moves closer.
  const folded = [-7,-28,-19,-58,-25,-41,-29,-7,-17,24,-8,22];
  const poses = [
    { time:3, x:600, y:333, tilt:-18, reach:.1, feeler:-18, offer:0,
      lanternX:734, lanternY:300, lanternTilt:-4, shutter:.62, shelter:1,
      wing:folded, keeper:{x:758,y:333,tilt:-19,reach:.85,feeler:-8,
        wing:[-12,-36,-66,-80,-74,-46,-65,-5,-29,24,-8,22]},
      caption:'Closer to the sill: behind a cracked shutter, another moth bends around a small lantern.' },
    { time:3.48, x:600, y:333, tilt:-18, reach:.1, feeler:-14, offer:0,
      lanternX:734, lanternY:300, lanternTilt:0, shutter:0, shelter:1,
      wing:folded, keeper:{x:758,y:333,tilt:-19,reach:.85,feeler:-5,
        wing:[-13,-35,-66,-81,-73,-45,-62,-3,-28,26,-8,22]},
      caption:'The shutter opens. The nicked-wing moth cups the lantern in both hands, a wing curved over it.' },
    { time:4.03, x:600, y:333, tilt:-8, reach:.15, feeler:3, offer:.12,
      lanternX:726, lanternY:299, lanternTilt:-4, shutter:0, shelter:.82,
      wing:[-9,-30,-25,-64,-33,-43,-35,-4,-20,27,-8,22],
      keeper:{x:754,y:333,tilt:-29,reach:.8,feeler:8,
        wing:[-12,-33,-58,-73,-64,-37,-55,4,-29,28,-9,22]},
      caption:'The keeper looks toward the waiting moth. Its antennae lift; one hand opens beside the light.' },
    { time:4.67, x:609, y:333, tilt:10, reach:.65, feeler:12, offer:.78,
      lanternX:698, lanternY:301, lanternTilt:-10, shutter:0, shelter:.25,
      wing:[-13,-34,-54,-78,-64,-39,-60,5,-35,31,-9,22],
      keeper:{x:749,y:333,tilt:-27,reach:1,feeler:10,
        wing:[-12,-33,-47,-70,-55,-35,-49,4,-27,28,-9,22]},
      caption:'The keeper brings the lantern out over the sill and offers an empty hand. The waiting moth reaches back.' },
    { time:5.25, x:632, y:333, tilt:13, reach:.95, feeler:9, offer:1,
      lanternX:691, lanternY:304, lanternTilt:2, shutter:0, shelter:0,
      wing:[-12,-31,-42,-68,-50,-34,-47,4,-28,28,-8,22],
      keeper:{x:746,y:333,tilt:-13,reach:.95,feeler:7,wing:folded},
      caption:'The first moth steps closer. Both pairs of hands meet beneath the warm lantern.' },
    { time:6, x:638, y:333, tilt:8, reach:.8, feeler:4, offer:1,
      lanternX:692, lanternY:308, lanternTilt:0, shutter:0, shelter:0,
      wing:folded, keeper:{x:747,y:333,tilt:-8,reach:.8,feeler:4,wing:folded},
      caption:'Two moths rest together on the sill, sharing the light between their hands.' }
  ].map(p => ({...p, scene:2}));
  const shot = {duration:6, author:'Sorrel', poses};
  if (typeof module !== 'undefined' && module.exports) module.exports = shot;
  else root.LanternShotTwo = shot;
}(typeof window === 'undefined' ? globalThis : window));
