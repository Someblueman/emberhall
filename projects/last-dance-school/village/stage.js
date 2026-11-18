/* A paper village made for this fable. No remote art or borrowed sprites. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  $('village-scenery').innerHTML = `
    <defs><linearGradient id="river-light" x2="0" y2="1"><stop stop-color="#8bafb2"/><stop offset="1" stop-color="#2d626e"/></linearGradient></defs>
    <path fill="#283e52" d="M0 0h900v570H0z"/>
    <g id="village-stars" fill="#d9d3b2"><circle cx="78" cy="78" r="2"/><circle cx="690" cy="58" r="2"/><circle cx="825" cy="144" r="2"/><circle cx="517" cy="42" r="2"/></g>
    <circle cx="724" cy="103" r="41" fill="#e1d4a8"/>
    <path fill="#6a8176" d="M0 270Q130 183 290 285T600 267T900 229V570H0z"/>
    <path fill="#3d625c" d="M0 383Q180 299 387 373L440 570H0zM506 370Q672 288 900 346V570H467z"/>
    <path id="river" fill="url(#river-light)" d="M443 282Q377 347 446 397T439 570H532Q555 489 495 421T492 282z"/>
    <g id="river-ripples" fill="none" stroke="#bdcec1" stroke-width="3" opacity=".6"><path d="M431 332h38m-16 43h35m-3 69h26m-48 45h36m-17 48h29"/></g>
    <g id="north-house"><path d="M65 254l112-67 117 73-9 145-211 3z" fill="#8caaa5" stroke="#385361" stroke-width="4"/><path d="M46 263l126-92 143 87-23 15-119-66-105 74z" fill="#495467"/><path d="M151 312l58-3v99h-62z" fill="#354854"/><path d="M94 286h34v45H94zM233 288h34v40h-34z" fill="#f0c77e"/><path d="M80 409h205" stroke="#d2c5a0" stroke-width="8"/></g>
    <g id="south-house"><path d="M605 254l118-63 106 75-12 133-203 7z" fill="#ba8c75" stroke="#694c53" stroke-width="4"/><path d="M580 262l143-91 131 99-25 14-109-73-124 69z" fill="#6f4d59"/><path d="M691 311h55l8 91h-62z" fill="#5c4652"/><path d="M633 284h33v45h-33zM770 290h30v39h-30z" fill="#f0c77e"/></g>
    <g id="whole-bridge" stroke="#b9a27a" fill="none"><path d="M337 410l224-8" stroke-width="17"/><path d="M341 365l213-6M344 350v61m205-62v61" stroke-width="5"/><path d="M366 366v40m31-41v40m31-42v40m31-42v40m31-42v40m31-42v40" stroke-width="3"/></g>
    <path id="loose-plank" d="M420 410h72v13h-72z" fill="#c7b18a"/>
    <g id="broken-bridge" fill="#c4ae88"><path d="M335 401l61-4-3 17-59 4zM511 402l50-7 3 18-49 7z"/><path d="M386 414l31 45-8 4-35-47z"/></g>
    <g id="stepping-stones" fill="#a5aaa0" stroke="#5b7471" stroke-width="2"><ellipse cx="432" cy="457" rx="15" ry="7"/><ellipse cx="468" cy="438" rx="13" ry="6"/><ellipse cx="495" cy="462" rx="14" ry="7"/></g>
    <g id="new-plank"><path d="M330 439l320-5 2 17-320 5z" fill="#cbb189" stroke="#8d795f" stroke-width="2"/><path d="M350 444l280-4" stroke="#8d795f" stroke-width="2"/></g>
    <g id="south-bench" stroke="#aa8b6e" stroke-width="6"><path d="M680 427h100M695 428l-4 37m76-38 7 36"/></g>
    <g id="village-chair" transform="translate(105 431) scale(.85)"><use href="#chair-shape"/></g>
    <g id="little-tree" transform="translate(324 351)"><path d="M0 65L-4-16m-1 41L-30-3m27 23L25-8" stroke="#7b775d" stroke-width="7" fill="none"/><path d="M-45-10q-12-34 22-33 22-39 39-4 43-11 39 29-12 36-51 25-39 16-49-17" fill="#acb17a"/></g>
    <g id="rain" stroke="#b1c9cd" opacity=".65" stroke-width="2"><path d="M110 95l-25 48m105-27-25 48m105-75-25 48m105-10-25 48m105-81-25 48m105-12-25 48m105-67-25 48m105-7-25 48m105-81-25 48m-650 46-25 48m105-27-25 48m105-75-25 48m105-10-25 48m105-81-25 48m105-12-25 48m105-67-25 48"/></g>
    <path id="pip-scarf" d="M755 414l-10 27 33 16-7 21-38-23 10-42z" fill="#e9c77d"/>
    <path id="chair-thread" d="M165 370q-19-17-21-1 1 13 22 1 24-18 28-2-2 13-28 2m0 0 10 42" fill="none" stroke="#9ccbd6" stroke-width="3"/>
    <path fill="url(#paper)" d="M0 0h900v570H0z" pointer-events="none"/>`;
  const ending = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  ending.id = 'returning-clearing';
  for (const [original, id, transform] of [
    ['little-tree','ending-tree','translate(728 360) scale(1.2)'],
    ['chair-thread','ending-thread','translate(97 44)'],
    ['new-plank','ending-plank','translate(-40 47)']
  ]) {
    const item = $(original).cloneNode(true); item.id = id; item.setAttribute('transform', transform); ending.append(item);
  }
  $('village-scenery').after(ending);
  function show(id, yes) { $(id).style.display = yes ? '' : 'none'; }
  function scenery(state, fraction) {
    const b = state ? state.beat : -1;
    show('clearing', b < 24 || b >= 80); show('village-scenery', b >= 24 && b < 80);
    show('returning-clearing', b >= 80); show('ending-thread', b >= 86);
    if (b < 24) { $('stage').setAttribute('viewBox', '0 0 900 570'); return; }
    show('loose-plank', b === 32 || b === 33);
    $('loose-plank').setAttribute('transform', b === 32 ? `translate(${fraction * 22} ${fraction * 80}) rotate(${fraction * 65} 450 410)` : 'translate(65 -13) rotate(-14 450 410)');
    show('whole-bridge', b < 32); show('broken-bridge', b >= 32 && b < 68);
    show('stepping-stones', b >= 64); show('new-plank', b >= 67);
    $('new-plank').setAttribute('transform', b === 67 ? `translate(0 ${-61 * (1 - fraction)})` : '');
    $('ending-plank').setAttribute('transform', `translate(-40 ${b === 80 ? -61 + fraction * 108 : 47})`);
    show('rain', b >= 32 && b < 39); show('pip-scarf', b >= 58);
    show('chair-thread', b >= 86); show('village-chair', b >= 39);
    const treeSize = b < 32 ? .38 : b < 56 ? .65 : 1;
    $('little-tree').setAttribute('transform', `translate(315 376) scale(${treeSize})`);
    $('river-ripples').setAttribute('transform', `translate(0 ${Math.sin(fraction * Math.PI * 2) * 4})`);
    $('rain').setAttribute('transform', `translate(${-fraction * 18} ${fraction * 25})`);
    $('village-chair').setAttribute('transform', `translate(${b === 39 ? 310 - fraction * 205 : 105} 431) scale(.85)`);
    $('ending-thread').setAttribute('transform', `translate(97 44) rotate(${Math.sin(fraction * Math.PI * 2) * 6} 166 370)`);
    $('chair-thread').setAttribute('transform', `rotate(${Math.sin(fraction * Math.PI * 2) * 5} 166 370)`);
    const view = b >= 80 ? '100 130 700 450' : b >= 40 && b <= 47 ? '40 180 540 360'
      : b >= 48 && b <= 55 ? '370 180 530 360'
      : b >= 72 ? '140 140 630 420' : '0 0 900 570';
    $('stage').setAttribute('viewBox', view);
  }
  function placement(state, id, fraction) {
    const b = state.beat;
    let visible = false, x = 450, y = 442, size = 1, disposition = 'standing';
    if (b < 32) {
      visible = ['ada', 'pip', 'rue'].includes(id);
      x = {ada: 240, pip: 676, rue: 385}[id]; size = id === 'rue' ? .85 : 1;
    } else if (b < 40) {
      visible = ['ada', 'pip', 'rue'].includes(id);
      x = {ada: 185, pip: 735, rue: 310}[id]; size = id === 'rue' ? .92 : 1;
      disposition = 'looking';
      if (b === 33 && id === 'pip') { x = 488; disposition = 'balancing'; }
      if (b === 33 && id === 'ada') { x = 370; disposition = 'reaching'; }
      if (b === 39 && id === 'rue') { x = 355 - fraction * 144; disposition = 'carrying'; }
    } else if (b < 48) {
      visible = id === 'rue' || (id === 'lio' && (b > 42 || state.audience.lio) && !(b === 40 && state.audience.lioLate));
      x = id === 'rue' ? 190 : 350; size = id === 'lio' ? .78 : 1;
      if (id === 'lio' && !state.audience.lio) x = 75;
      else if (id === 'lio' && b === 40) { x -= (1 - fraction) * 180; disposition = 'walking'; }
    } else if (b < 56) {
      visible = id === 'pip' || (id === 'bea' && (b > 50 || state.audience.bea));
      x = id === 'pip' ? 526 : 753; size = id === 'bea' ? .82 : 1;
      if (id === 'bea' && !state.audience.bea) x = 870;
      else if (id === 'bea' && b === 48) { x += (1 - fraction) * 110; disposition = 'carrying'; }
    } else if (b < 64) {
      visible = ['rue', 'lio', 'bea'].includes(id);
      x = {rue: 105, lio: 335, bea: 700}[id]; size = id === 'rue' ? 1 : 1.08;
      if (id === 'rue') { disposition = 'seated'; y = 426; }
    } else if (b < 72) {
      visible = id === 'lio' || id === 'bea';
      const progress = b < 68 ? (b - 64 + fraction) / 4 : 1;
      x = id === 'lio' ? 290 + progress * 100 : 740 - progress * 150;
      size = 1.08; if (b < 68) disposition = b === 67 ? 'carrying' : 'walking';
    } else {
      visible = id === 'lio' || id === 'bea' || (id === 'rue' && b >= 80 && b < 86);
      x = id === 'lio' ? 354 : id === 'bea' ? 607 : 166; size = id === 'rue' ? 1 : 1.08;
      if (id === 'rue') disposition = 'seated';
      if (b === 75 && id !== 'rue') disposition = 'laughing';
      if (b === 80 && id !== 'rue') disposition = 'carrying';
      if (b >= 80 && id === 'rue') { x = 263; y = 411; }
      if (b === 76 && id === 'lio' && !state.audience.exchange) disposition = 'looking';
    }
    return {visible, x: x || 450, y, size, disposition};
  }
  window.VillageStage = {scenery, placement};
})();
