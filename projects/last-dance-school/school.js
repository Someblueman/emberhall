/* Original articulated paper puppets; all movement comes from dance.js memories. */
(function () {
  'use strict';
  const D = window.Dance;
  const $ = id => document.getElementById(id);
  const names = {moth: 'Moth', ada: 'Ada', pip: 'Pip', rue: 'Rue'};
  const words = {bow: 'crooked bow', wave: 'sleeve-wave', stamp: 'brave stamp', turn: 'sideways turn'};
  const cast = {
    moth: {x: 285, y: 409, size: 1.08, coat: '#bfa673', trim: '#706653', skin: '#e3d4b4'},
    ada: {x: 475, y: 435, size: .86, coat: '#759da5', trim: '#384f65', skin: '#e9d9bc'},
    pip: {x: 675, y: 425, size: .94, coat: '#bb7866', trim: '#6c4650', skin: '#d5bd9c'},
    rue: {x: 490, y: 451, size: .65, coat: '#b1af7c', trim: '#65735b', skin: '#e8d5aa'}
  };
  for (const [id, c] of Object.entries(cast)) {
    const hair = id === 'moth' ? '<path d="M-22-137q-9-10-8-21l37-2 10-18 9 18 5 13-57 2" fill="#69705d"/><path d="M-16-111q8 12 15 0 8 13 17-1" fill="#ded9c5"/>'
      : id === 'ada' ? '<path d="M-26-132l8-33 16 22 22-11 9 29-19-9-7 10-12-13z" fill="#493e40"/>'
      : id === 'pip' ? '<path d="M-28-131q0-33 25-26 25-9 29 22l-54 8" fill="#c6a07c"/><path d="M-14-94l35 2 17 36-22-4-11-29" fill="#e5c581"/>'
      : '<path d="M-25-133q20-31 48 3l-25-5-2 13-9-12-12 9" fill="#6e6352"/>';
    const sleeves = id === 'rue' ? 31 : 22;
    $(id).innerHTML = `
      <ellipse data-part="shadow" cx="0" cy="6" rx="38" ry="9" fill="#202f36" opacity=".35"/>
      <g data-part="left-leg" transform="translate(-14 -43)"><path d="M0 0l-5 40" stroke="${c.trim}" stroke-width="14" stroke-linecap="round"/><path d="M-10 35l-12 9 27 1-1-10" fill="#333a43"/></g>
      <g data-part="right-leg" transform="translate(15 -43)"><path d="M0 0l6 40" stroke="${c.trim}" stroke-width="14" stroke-linecap="round"/><path d="M0 35l0 10 28-1-13-10" fill="#333a43"/></g>
      <g data-part="body">
      <path d="M-22-100l-14 61q35 15 71-1l-15-61z" fill="${c.coat}" stroke="${c.trim}" stroke-width="2"/>
      <path d="M0-98l-3 61M-25-53l15 3" stroke="${c.trim}" fill="none" stroke-width="2"/>
      <circle cx="6" cy="-79" r="2" fill="${c.trim}"/><circle cx="4" cy="-61" r="2" fill="${c.trim}"/>
      <g data-part="left-arm" transform="translate(-22 -94)"><path d="M0 0l-12 ${sleeves} 4 22" fill="none" stroke="${c.coat}" stroke-width="15" stroke-linecap="round"/><ellipse cx="-8" cy="${sleeves + 24}" rx="6" ry="8" fill="${c.skin}"/></g>
      <g data-part="right-arm" transform="translate(22 -94)"><path d="M0 0l13 ${sleeves} -4 22" fill="none" stroke="${c.coat}" stroke-width="15" stroke-linecap="round"/><ellipse cx="9" cy="${sleeves + 24}" rx="6" ry="8" fill="${c.skin}"/></g>
      <g data-part="head"><path d="M-7-105v12h15v-12" fill="${c.skin}"/><path d="M-25-137q21-20 49 1l-3 27-19 10-23-10z" fill="${c.skin}" stroke="${c.trim}" stroke-width="1.5"/>
      <circle cx="-10" cy="-123" r="2" fill="#333a43"/><circle cx="11" cy="-122" r="2" fill="#333a43"/><path d="M-3-114l7 1" stroke="#725b50" stroke-width="2"/>
      ${hair}</g></g>`;
  }
  const parts = Object.fromEntries(Object.keys(cast).map(id => [id,
    Object.fromEntries([...$(id).querySelectorAll('[data-part]')].map(el => [el.dataset.part, el]))]));
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let state = null, running = false, elapsed = 0, previous = null, rehearsalTime = 0;
  let rehearsalSlot = 0;
  function phrase() {
    return ['first', 'second', 'third'].map(id => D.gesture($(id).value, $('big').checked));
  }
  function options() {
    return {ada: $('watch-ada').checked, pip: $('watch-pip').checked,
      teacher: document.querySelector('input[name="teacher"]:checked').value, late: $('late').checked};
  }
  function memoryList() {
    $('handoffs').replaceChildren();
    if (!state || !state.handoffs.length) {
      const li = document.createElement('li'); li.textContent = 'No lesson has passed yet.'; $('handoffs').append(li); return;
    }
    for (const h of state.handoffs) {
      const li = document.createElement('li');
      li.textContent = `${names[h.from]} → ${names[h.to]}: ${h.count ? state.memories[h.to].map(g => words[g.kind]).join(', ') : 'no movements reached this pupil'}.`;
      $('handoffs').append(li);
    }
  }
  function refresh() {
    $('beat-title').textContent = state ? D.beats[state.beat].title : 'Before the last class';
    $('line').textContent = state ? D.caption(state) : `Moth offers a ${words[phrase()[rehearsalSlot].kind]}. Ada gives it a little more care.`;
    const ended = state && state.beat === D.beats.length - 1;
    $('play').textContent = !state ? 'Begin the last class' : ended ? 'The class is over' : running ? 'Pause the dance' : 'Let it move';
    $('play').disabled = !!ended;
    $('step').disabled = !!ended;
    $('again').hidden = !state;
    $('change-dance').hidden = !!state;
    $('time').textContent = state ? `${state.beat + 1} of ${D.beats.length} moments · ${running ? 'The dance is moving' : 'Still — take your time'}` : 'About three minutes. Or take it one still at a time.';
    for (const id of ['phrase', 'witnesses', 'teachers']) $(id).disabled = !!state;
    $('locked').hidden = !state;
    memoryList();
    const act = state && D.performance(state);
    const movement = act && state.memories[act.who][act.slot];
    $('stage-description').textContent = state ? `${D.beats[state.beat].title}. ${D.caption(state)}${act ? ` ${names[act.who]} ${movement ? `performs a ${words[movement.kind]}` : 'holds still with no learned movement'}.` : ''}` : `Moth and Ada rehearse a ${words[phrase()[rehearsalSlot].kind]} while Pip waits. An empty chair stands beside the path.`;
  }
  function pose(id, g, phase, x, disposition = 'standing') {
    const c = cast[id], p = parts[id], pulse = Math.sin(Math.PI * phase);
    let tilt = 0, left = 5, right = -4, lift = 0, hop = 0, head = 0;
    if (g) {
      if (g.kind === 'bow') { tilt = g.tilt * 1.8 * pulse; left = -22 * pulse; right = 18 * pulse; head = 8 * pulse; }
      if (g.kind === 'wave') { right = -145 * g.reach * pulse; left = -20 * pulse; tilt = -g.tilt * .35 * pulse; }
      if (g.kind === 'stamp') { lift = -g.foot * pulse; hop = -4 * Math.sin(phase * Math.PI * 2); left = 40 * pulse; right = -35 * pulse; tilt = g.tilt * .3 * pulse; }
      if (g.kind === 'turn') { tilt = -g.tilt * pulse; right = -58 * g.reach * pulse; left = -45 * g.reach * pulse; head = -12 * pulse; }
    }
    const walking = disposition === 'walking' ? Math.sin(phase * Math.PI * 4) : 0;
    const seated = disposition === 'seated';
    if (walking) { hop -= Math.abs(walking) * 4; left += walking * 16; right -= walking * 16; }
    if (seated) { tilt = 8; head = 4; }
    if (disposition === 'looking') head = -18;
    $(id).setAttribute('transform', `translate(${x} ${c.y + hop + (seated ? 47 : 0)}) scale(${c.size})`);
    p.body.setAttribute('transform', `rotate(${tilt} 0 -42)`);
    p.head.setAttribute('transform', `rotate(${head} 0 -104)`);
    p['left-arm'].setAttribute('transform', `translate(-22 -94) rotate(${left})`);
    p['right-arm'].setAttribute('transform', `translate(22 -94) rotate(${right})`);
    p['left-leg'].setAttribute('transform', `translate(-14 -43) rotate(${seated ? -75 : -lift * .7 + walking * 22})`);
    p['right-leg'].setAttribute('transform', `translate(15 ${-43 + lift}) rotate(${seated ? -70 : lift * .6 - walking * 22})`);
  }
  function draw(still = false) {
    const b = state ? state.beat : -1;
    const phase = still || reduced ? .5 : (state ? elapsed % 4 : rehearsalTime % 3) / (state ? 4 : 3);
    const act = state ? D.performance(state) : {who: 'moth', slot: rehearsalSlot};
    const source = state ? state.memories : {moth: phrase(), ada: D.learn(phrase(), 'ada', [0, 1, 2]), pip: [], rue: []};
    for (const [id, c] of Object.entries(cast)) {
      let x = c.x, visible = id === 'rue' ? b >= 13 : id === 'moth' ? b < 12 : true;
      let g = act && act.who === id ? source[id][act.slot] : null;
      if (!state && id === 'ada') g = source.ada[rehearsalSlot];
      if (b >= 22 && id !== 'moth' && source[id].length) g = source[id][b === 23 ? source[id].length - 1 : 0];
      if (b === 11 && id === 'moth') x -= (still ? .65 : elapsed / 8) * 380;
      if (state && b >= 13) {
        if (id === 'ada' || id === 'pip') x = id === state.teacher ? 335 : 700;
        if (id === 'rue') x = 520;
      }
      if (id === 'rue' && b === 13) x += (still ? .25 : 1 - elapsed / 8) * 400;
      if (id === 'rue' && state && state.late && b === 14) visible = false;
      // A pupil who missed the first class stays on the path, not pretending to learn.
      if (state && b <= 4 && id !== 'moth' && id !== 'rue' && !state.watching[id]) x += 125;
      $(id).setAttribute('display', visible ? 'inline' : 'none');
      let disposition = 'standing';
      if (id === 'moth' && b === 10) disposition = 'seated';
      else if ((id === 'moth' && b === 11) || (id === 'rue' && b === 13)) disposition = 'walking';
      else if (id === 'rue' && b === 21) disposition = 'looking';
      if (disposition === 'seated') x = 263;
      pose(id, g, phase, x, disposition);
    }
  }
  function begin(moving) {
    state = D.start(phrase(), options()); elapsed = 0; running = moving && !reduced; refresh(); draw(true);
  }
  $('play').addEventListener('click', () => {
    if (!state) begin(true);
    else { running = !running; refresh(); }
  });
  $('step').addEventListener('click', () => {
    if (!state) begin(false);
    else { D.next(state); elapsed = 0; running = false; refresh(); draw(true); }
  });
  $('again').addEventListener('click', () => {
    state = null; elapsed = 0; rehearsalTime = 0; running = false; refresh(); draw(true); $('first').focus();
  });
  for (const [slot, id] of ['first', 'second', 'third'].entries()) $(id).addEventListener('click', () => {
    const button = $(id);
    button.value = D.kinds[(D.kinds.indexOf(button.value) + 1) % D.kinds.length];
    button.textContent = `${['First', 'Then', 'Last'][slot]}: A ${words[button.value]}`;
    rehearsalSlot = slot; rehearsalTime = 0; refresh(); draw(true);
  });
  $('big').addEventListener('change', () => {
    rehearsalTime = 0; refresh(); draw(true);
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && running) { running = false; refresh(); }
    previous = null;
  });
  function frame(now) {
    const delta = previous === null ? 0 : Math.min(.1, (now - previous) / 1000); previous = now;
    if (!state && !reduced) { rehearsalTime += delta; draw(); }
    if (state && running) {
      elapsed += delta;
      if (elapsed >= D.beats[state.beat].seconds) {
        elapsed = 0; D.next(state);
        if (state.beat === D.beats.length - 1) running = false;
        refresh();
      }
      draw();
    }
    requestAnimationFrame(frame);
  }
  refresh(); draw(true); requestAnimationFrame(frame);
})();
