(function (root) {
  'use strict';
  const shot = typeof module !== 'undefined' && module.exports ? require('./shot-one.js') : root.LanternShotOne;
  const clampTime = time => Number.isFinite(time) ? Math.max(0, Math.min(shot.duration, time)) : 0;
  function poseAt(time) {
    const t = clampTime(time);
    const index = Math.max(0, shot.poses.findIndex(p => p.time >= t));
    if (index === 0) return { ...shot.poses[0], time:t, wing:[...shot.poses[0].wing] };
    const a = shot.poses[index - 1], b = shot.poses[index];
    let u = (t - a.time) / (b.time - a.time);
    // A soft ease settles each drawn gesture; the final quarter-second holds.
    if (index === 5) u = Math.min(1, u * 1.5);
    u = u * u * (3 - 2 * u);
    const result = { time:t, caption:u < .5 ? a.caption : b.caption };
    for (const key of ['x','y','tilt','reach','feeler','lanternX','lanternY','lanternTilt','shutter']) result[key] = a[key] + (b[key] - a[key]) * u;
    result.wing = a.wing.map((n,i) => n + (b.wing[i] - n) * u);
    return result;
  }
  const number = n => Number(n.toFixed(3));
  function wingPath(w) {
    const p = w.map(number);
    return `M -5 -20 C ${p[0]} ${p[1]} ${p[2]} ${p[3]} ${p[4]} ${p[5]} C ${p[6]} ${p[7]} ${p[8]} ${p[9]} ${p[10]} ${p[11]} Q -9 7 -5 -20 Z`;
  }
  function frameSVG(p, id, decorative = false) {
    const n = number, glow = 1 - p.shutter * .86;
    const role = decorative ? 'aria-hidden="true"' : `role="img" aria-labelledby="${id}-title ${id}-desc"`;
    const feathers = Array.from({length:9}, (_,i) => `<path d="M ${-6-i*.5} ${-10+i*4} l -7 4 M ${6+i*.5} ${-10+i*4} l 7 4"/>`).join('');
    const veins = `<path d="M -8 -15 Q -36 -34 -67 -45 M -9 -4 Q -33 -6 -60 6 M -12 10 Q -30 13 -41 23" fill="none" stroke="#bc8d67" stroke-width="1.5" opacity=".6"/>`;
    const wing = `<path d="${wingPath(p.wing)}" fill="url(#${id}-wing)" stroke="#ead9ad" stroke-width="1.5"/><g clip-path="url(#${id}-leftwing)">${veins}<circle cx="-42" cy="-23" r="10" fill="#86695d"/><circle cx="-42" cy="-23" r="6" fill="#e5c59b"/><circle cx="-42" cy="-23" r="3" fill="#3d4c4a"/></g>`;
    const dust = [[58,102],[151,61],[205,141],[310,90],[387,47],[438,312],[94,351],[292,319],[583,70]].map(([x,y],i) => `<circle cx="${x}" cy="${y}" r="${i%3===0?1.6:.8}" fill="#c9d4bd" opacity=".35"/>`).join('');
    const boards = Array.from({length:6}, (_,i) => `<path d="M ${658+i*27} 72 v 297"/><path d="M ${669+i*27} ${100+i*31} q -6 54 0 93" opacity=".5"/>`).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 440" ${role}>
      <title id="${id}-title">Lantern Loop, first shot at ${p.time.toFixed(2)} seconds</title><desc id="${id}-desc">${p.caption}</desc>
      <defs>
        <linearGradient id="${id}-wall" x2="1" y2="1"><stop stop-color="#21494e"/><stop offset="1" stop-color="#0d292f"/></linearGradient>
        <linearGradient id="${id}-wing" x2=".6" y2="1"><stop stop-color="#f5e7be"/><stop offset=".55" stop-color="#d6bd94"/><stop offset="1" stop-color="#9c7e69"/></linearGradient>
        <radialGradient id="${id}-glow"><stop stop-color="#ffd282" stop-opacity=".4"/><stop offset="1" stop-color="#f1aa53" stop-opacity="0"/></radialGradient>
        <linearGradient id="${id}-wood"><stop stop-color="#315357"/><stop offset="1" stop-color="#244349"/></linearGradient>
        <clipPath id="${id}-window"><rect x="650" y="72" width="160" height="297" rx="70"/></clipPath>
        <clipPath id="${id}-leftwing"><path d="${wingPath(p.wing)}"/></clipPath>
      </defs>
      <rect width="900" height="440" fill="url(#${id}-wall)"/>
      <path d="M 0 398 Q 440 385 900 403 L 900 440 H 0 Z" fill="#0d2228"/>
      <path d="M 0 410 Q 470 397 900 416 M 0 427 Q 470 414 900 433" stroke="#47605c" fill="none" opacity=".45"/>
      <path d="M 41 0 v 391 M 47 0 v 391 M 867 0 v 397" stroke="#5a7770" opacity=".25"/>
      <path d="M 0 27 H 900" stroke="#081c23" stroke-width="16"/>
      <path d="M 0 20 H 900" stroke="#5d7970" opacity=".5"/>
      ${dust}
      <rect x="638" y="60" width="184" height="321" rx="82" fill="#081b22" stroke="#658078" stroke-width="3"/>
      <rect x="650" y="72" width="160" height="297" rx="70" fill="#0a151e"/>
      <ellipse cx="${n(p.lanternX)}" cy="${n(p.lanternY)}" rx="178" ry="172" fill="url(#${id}-glow)" opacity="${n(glow)}"/>
      <g transform="translate(${n(p.lanternX)} ${n(p.lanternY)}) rotate(${n(p.lanternTilt)})">
        <path d="M 0 -190 V -48" stroke="#8b9b7d" stroke-width="2"/>
        <path d="M -12 -29 Q -16 -50 0 -50 Q 16 -50 12 -29" fill="none" stroke="#d9c191" stroke-width="3"/>
        <path d="M -24 -28 Q 0 -38 24 -28 L 28 23 Q 0 35 -28 23 Z" fill="#ecad55" stroke="#f6d58c" stroke-width="2"/>
        <path d="M -17 -22 Q 0 -30 17 -22 L 20 20 Q 0 28 -20 20 Z" fill="#ffe6a5"/>
        <path d="M 0 -28 V 28 M -26 -19 H 26 M -28 17 H 28" stroke="#b67c45" stroke-width="3"/>
        <path d="M -30 -30 Q 0 -48 30 -30 L 23 -23 H -23 Z M -29 26 Q 0 42 29 26" fill="#a97949" stroke="#edc880" stroke-width="2"/>
      </g>
      <g clip-path="url(#${id}-window)"><g transform="translate(${n(160*(1-p.shutter))} 0)">
        <rect x="650" y="72" width="160" height="297" fill="url(#${id}-wood)" stroke="#81958a" stroke-width="2"/>
        <g stroke="#102e35" fill="none">${boards}</g>
        <path d="M 651 141 H 810 M 651 309 H 810" stroke="#19383e" stroke-width="12"/>
        <path d="M 651 137 H 810 M 651 305 H 810" stroke="#6c8275" stroke-width="2"/>
        <circle cx="673" cy="251" r="5" fill="#c3a970"/><path d="M 673 254 q -9 17 0 20 q 9 -3 0 -20" fill="none" stroke="#c3a970" stroke-width="3"/>
      </g></g>
      <path d="M 615 377 H 845 l 8 12 H 607 Z" fill="#44635e" stroke="#809085" stroke-width="1.5"/>
      <path d="M 611 391 H 850" stroke="#091f26" stroke-width="7"/>
      <ellipse cx="${n(p.x)}" cy="380" rx="${n(15+(p.y-190)*.16)}" ry="4" fill="#06191d" opacity=".4"/>
      <g transform="translate(${n(p.x)} ${n(p.y)}) rotate(${n(p.tilt)})">
        <g>${wing}</g><g transform="scale(-1 1)">${wing}</g>
        <path d="M -5 7 Q -12 30 0 47 Q 12 30 5 7" fill="#bdac88" stroke="#eddfb8" stroke-width="2"/>
        <path d="M -7 26 H 7 M -6 34 H 6" stroke="#786c59" fill="none"/>
        <g fill="none" stroke="#eddfb8" stroke-width="2" stroke-linecap="round">${feathers}
          <path d="M -8 11 Q -22 29 -12 39 M 8 11 Q 22 29 12 39 M -7 -8 Q ${n(-21-12*p.reach)} ${n(-8-30*p.reach)} ${n(-20-14*p.reach)} ${n(4-45*p.reach)} M 7 -8 Q ${n(21+12*p.reach)} ${n(-8-30*p.reach)} ${n(20+14*p.reach)} ${n(4-45*p.reach)}"/>
        </g>
        <ellipse cy="-7" rx="13" ry="20" fill="#e8d8ad"/>
        <path d="M -11 -16 l -7 1 7 5 M 11 -16 l 7 1 -7 5" fill="#f6e7c1"/>
        <path d="M -7 -25 Q ${n(-20-p.feeler)} ${n(-63-Math.min(0,p.feeler)*1.6)} ${n(-31-p.feeler)} ${n(-57-Math.min(0,p.feeler)*2)} M 7 -25 Q ${n(20+p.feeler)} ${n(-63-Math.min(0,p.feeler)*1.6)} ${n(31+p.feeler)} ${n(-57-Math.min(0,p.feeler)*2)}" fill="none" stroke="#e8d8ad" stroke-width="2.5" stroke-linecap="round"/>
        <ellipse cy="-28" rx="14" ry="12" fill="#ecdfb9"/>
        <ellipse cx="-7" cy="-30" rx="4" ry="5" fill="#20383b"/><ellipse cx="7" cy="-30" rx="4" ry="5" fill="#20383b"/>
        <circle cx="-5.8" cy="-31.5" r="1.2" fill="#fff0be"/><circle cx="8.2" cy="-31.5" r="1.2" fill="#fff0be"/>
      </g>
      <path d="M 18 46 H 34 M 18 46 V 62 M 882 422 H 866 M 882 422 V 406" fill="none" stroke="#9cb0a1" opacity=".45"/>
    </svg>`;
  }
  function mount() {
    const stage = document.getElementById('stage'), seek = document.getElementById('seek');
    const play = document.getElementById('play'), pause = document.getElementById('pause');
    const status = document.getElementById('status'), clock = document.getElementById('clock');
    let time = 0, playing = false, started = 0, frame = null;
    const stills = shot.poses.map((p,i) => {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'still';
      button.setAttribute('aria-label',`Seek to drawing ${i+1}, ${p.time.toFixed(2)} seconds`);
      button.innerHTML = frameSVG(p, `still-${i}`, true) + `<span><b>0${i+1}</b>${p.time.toFixed(2)} s</span>`;
      button.addEventListener('click', () => { stop(); time = p.time; render(); status.textContent = `Paused on drawing ${i+1}.`; });
      document.getElementById('contact-sheet').append(button);
      return button;
    });
    function render() {
      stage.innerHTML = frameSVG(poseAt(time), 'film');
      seek.value = time.toFixed(2); seek.setAttribute('aria-valuetext',`${time.toFixed(2)} seconds of 3`);
      clock.textContent = `${time.toFixed(2)} / 3.00 s`;
      stills.forEach((b,i) => b.setAttribute('aria-current',Math.abs(time-shot.poses[i].time)<.006 ? 'true' : 'false'));
    }
    function stop() {
      playing = false; if (frame !== null) cancelAnimationFrame(frame); frame = null;
      // Both controls remain usable: disabling a focused Pause loses focus.
    }
    function tick(now) {
      if (!playing) return;
      time = clampTime((now-started)/1000); render();
      if (time >= shot.duration) { stop(); status.textContent = 'End of the first shot. The second shot is still to come.'; }
      else frame = requestAnimationFrame(tick);
    }
    function start(restart) {
      stop(); if (restart || time >= shot.duration) time = 0;
      playing = true; started = performance.now()-time*1000;
      // Play remains focusable; activating it again simply continues playback.
      status.textContent = 'Playing the first shot.';
      render(); frame = requestAnimationFrame(tick);
    }
    play.addEventListener('click',() => start(false));
    pause.addEventListener('click',() => { stop(); render(); status.textContent = `Paused at ${time.toFixed(2)} seconds.`; });
    document.getElementById('replay').addEventListener('click',() => start(true));
    seek.addEventListener('input',() => { stop(); time = clampTime(Number(seek.value)); render(); status.textContent = 'Paused. Use the arrow keys to choose a moment.'; });
    document.addEventListener('visibilitychange',() => {
      if (document.hidden && playing) { stop(); status.textContent = 'Paused while the page is hidden.'; }
    });
    render();
  }
  const api = { clampTime, poseAt, frameSVG };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else { root.LanternFilm = api; mount(); }
}(typeof window === 'undefined' ? globalThis : window));
