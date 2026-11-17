/* Original visual companion. No network, storage, dependencies or automatic motion. */
(function () {
  'use strict';
  function shape(b) { return [0, b + 2, 2 * b + 4, 3 * b + 4, 4 * b + 4]; }
  function parameter(value) {
    const b = Number(value);
    if (String(value).trim() === '' || !Number.isInteger(b) || b < 1 || b > 11 || b % 2 !== 1) {
      throw new RangeError('Choose an odd whole number from 1 to 11. The shape has not changed.');
    }
    return b;
  }
  function forbidden(b) {
    const s = shape(b);
    return new Set(s.flatMap((x, i) => s.slice(i + 1).map(y => y - x)));
  }
  function collision(b, x, y) {
    if (x === y) return null;
    const other = new Set(shape(b).map(s => y + s));
    const shared = shape(b).map(s => x + s).find(v => other.has(v));
    return shared === undefined ? null : { x, y, distance: Math.abs(x - y), shared };
  }
  function attempt(b, selected, x) {
    if (!Number.isInteger(x) || x < 0 || x >= 5 * b + 4) throw new RangeError('Start outside the window');
    if (x === 0) return { selected: [...selected], kind: 'anchor' };
    if (selected.includes(x)) return { selected: selected.filter(v => v !== x), kind: 'removed' };
    for (const y of selected) {
      const clash = collision(b, x, y);
      if (clash) return { selected: [...selected], kind: 'clash', clash };
    }
    return { selected: [...selected, x].sort((a, c) => a - c), kind: 'added' };
  }
  function lower(b) { return Array.from({ length: b }, (_, i) => 2 * i); }
  function initialExclusions(b, t) {
    return [0, 3, 4].map(row => ({ row, position: 1 + shape(b)[row], distance: Math.abs(1 + shape(b)[row] - t) }));
  }
  function transitions(b) {
    return [1, 2].flatMap(from => [0, 3, 4].map(to => ({ from, to, distance: Math.abs(2 + shape(b)[to] - shape(b)[from]) })));
  }
  const model = { shape, parameter, forbidden, collision, attempt, lower, initialExclusions, transitions };
  if (typeof module !== 'undefined' && module.exports) { module.exports = model; return; }
  const $ = id => document.getElementById(id);
  const ink = '#202d37', teal = '#116c67', rust = '#a33c30', gold = '#e1ad3c';
  let b = 5, selected = [0], step = 0, high = false, mode = 'packing', cursor = 1;
  const svg = (title, width, height, body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${title}">${body}</svg>`;
  const text = (x, y, value, color = ink, size = 12) => `<text x="${x}" y="${y}" text-anchor="middle" fill="${color}" font-size="${size}">${value}</text>`;
  const line = (x1, y1, x2, y2, color = ink, dash = '') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" ${dash ? 'stroke-dasharray="4 4"' : ''}/>`;
  function renderShape() {
    const s = shape(b), scale = 480 / s[4];
    let body = line(25, 38, 505, 38, '#c8c9bd');
    s.forEach((v, i) => {
      const x = 25 + v * scale;
      body += `<circle cx="${x}" cy="38" r="6" fill="${i ? '#e1ad3c' : '#f5f1e7'}"/>` + text(x, 70, v, '#f5f1e7', 20);
      if (i < 4) body += text(x + (s[i + 1] - v) * scale / 2, 18, i < 2 ? `a = ${b + 2}` : `b = ${b}`, '#d7d8cc', 18);
    });
    $('shape').innerHTML = svg(`Five marks at ${s.join(', ')}, with gaps ${b + 2}, ${b + 2}, ${b}, ${b}`, 530, 82, body);
    $('shape-description').textContent = `b = ${b} · a = b + 2 = ${b + 2} · S = {${s.join(', ')}}`;
  }
  function drawCollision(clash) {
    if (!clash) { $('collision-picture').replaceChildren(); return; }
    const { x, y, shared } = clash, s = shape(b), left = Math.min(x, y), right = Math.max(x, y) + s[4];
    const px = v => 32 + (v - left) * 356 / (right - left);
    let body = '';
    [y, x].forEach((start, i) => {
      const height = 32 + 54 * i;
      body += line(px(start), height, px(start + s[4]), height, '#9ca69f');
      s.forEach(v => { body += `<circle cx="${px(start + v)}" cy="${height}" r="5" fill="${start + v === shared ? rust : teal}"/>`; });
      body += text(210, height + 22, `${i ? 'Tried' : 'Existing'} start ${start}`, ink, 12);
    });
    body += line(px(shared), 18, px(shared), 97, rust, 'dash');
    body += text(210, 135, `Both copies contain ${shared}`, rust, 14);
    $('collision-picture').innerHTML = svg(`Copies at starts ${x} and ${y} share integer ${shared}`, 420, 146, body);
  }
  function renderStarts(focus = null) {
    const n = 5 * b + 4;
    $('window-description').textContent = `This window contains ${n} integers, 0 through ${n - 1}. The proposed bound is ${b} starts. Can you beat it legally?`;
    $('starts').replaceChildren();
    for (let x = 0; x < n; x++) {
      const button = document.createElement('button');
      const chosen = selected.includes(x), clash = !chosen && selected.some(y => collision(b, x, y));
      button.type = 'button'; button.dataset.start = x; button.textContent = x;
      button.className = x === 0 ? 'fixed' : chosen ? 'chosen' : clash ? 'clash' : '';
      button.disabled = x === 0; button.tabIndex = x === cursor ? 0 : -1;
      button.setAttribute('aria-pressed', String(chosen));
      button.setAttribute('aria-label', `Start ${x}${x === 0 ? ', fixed' : chosen ? ', placed; remove' : clash ? ', clashes; show why' : ', available; place'}`);
      $('starts').append(button);
    }
    $('count').textContent = `${selected.length} of ${b} proposed possible starts placed: {${selected.join(', ')}}.`;
    if (focus !== null) $('starts').querySelector(`[data-start="${focus}"]`).focus();
  }
  function place(x) {
    const result = attempt(b, selected, x);
    selected = result.selected; cursor = x || 1;
    const messages = {
      added: `Start ${x} fits. No copy touches another.`, removed: `Removed start ${x}.`, anchor: 'Zero anchors this window and stays fixed.',
      clash: result.clash ? `Start ${x} clashes with start ${result.clash.y}: both copies contain ${result.clash.shared}. The forbidden start distance is ${result.clash.distance}. Nothing was added.` : ''
    };
    $('placement-message').textContent = messages[result.kind];
    drawCollision(result.clash); renderStarts(x || 1);
  }
  function reset() {
    selected = [0]; cursor = 1;
    $('placement-message').textContent = 'Zero is placed. Try a pale number, or inspect a red dashed one to see why it clashes.';
    drawCollision(null); renderStarts();
  }
  function renderColumns() {
    const s = shape(b), t = high ? 2 * b + 3 : b + 1, cell = 44, bandSize = Math.min(b, 6), width = Math.max(288, 68 + cell * bandSize);
    const bands = Math.ceil(b / bandSize), extraTop = bands * 235;
    let body = '';
    for (let c = 0; c < b; c++) {
      const band = Math.floor(c / bandSize) * 235, col = c % bandSize;
      body += text(58 + col * cell, band + 18, `C${c}`, c % 2 ? teal : ink, 12);
      for (let row = 0; row < 5; row++) {
        const x = 38 + col * cell, y = band + 30 + row * 40;
        const odd = c % 2 === 1, active = b > 1 && (step === 2 && c === 1 || step === 3 && odd);
        const candidate = active && [1, 2].includes(row);
        const crossed = c === 0 && row > 0 || active && !candidate || active && step === 3 && c === b - 2;
        const fill = c === 0 && row === 0 ? ink : candidate ? gold : '#fffaf0';
        body += `<rect x="${x}" y="${y}" width="36" height="30" rx="3" fill="${fill}" stroke="${odd ? teal : '#b8bbae'}"/>`;
        body += text(x + 18, y + 20, c + s[row], c === 0 && row === 0 ? '#fff' : ink, 12);
        if (crossed) body += line(x + 3, y + 3, x + 33, y + 27, rust) + line(x + 33, y + 3, x + 3, y + 27, rust);
      }
    }
    for (let band = 0; band < bands; band++) for (let row = 0; row < 5; row++) body += text(15, band * 235 + 50 + row * 40, `r${row}`, ink, 11);
    body += text(width / 2, extraTop + 8, 'Outside the columns', ink, 13);
    [b, b + 1, 2 * b + 2, 2 * b + 3].forEach((v, i) => {
      const x = 28 + i * (width - 56) / 4, y = extraTop + 23;
      const excluded = i === 0 || i === 2 || b === 1;
      body += `<rect x="${x}" y="${y}" width="44" height="32" rx="3" fill="${step >= 2 && v === t && b > 1 ? gold : '#fffaf0'}" stroke="${excluded ? rust : teal}"/>` + text(x + 22, y + 21, v, ink, 13);
      if ((step >= 1 || b === 1) && excluded) body += line(x + 3, y + 3, x + 41, y + 29, rust) + line(x + 41, y + 3, x + 3, y + 29, rust);
    });
    $('column-picture').innerHTML = svg(`Five rows in ${b} columns. Step ${step + 1}. ${step >= 2 && b > 1 ? 'Rows 1 and 2 remain under consideration in highlighted odd columns.' + (step === 3 ? ' Both are excluded at the final column.' : '') : 'Column zero contains the fixed start zero.'} Four extra positions are shown separately.`, width, extraTop + 68, body);
    $('step-number').textContent = `${step + 1} / 4`;
    $('previous').disabled = step === 0; $('next').disabled = step === 3;
    $('extra-controls').hidden = b === 1 || step < 2;
    $('extra-low').setAttribute('aria-pressed', String(!high)); $('extra-high').setAttribute('aria-pressed', String(high));
    const titles = ['Split the window into columns.', 'There are four positions left over.', 'An extra start traps the first odd column.', 'The trap travels, then meets zero.'];
    const texts = [
      'Column C_c is the shape shifted by c, for c = 0,…,b−1. Any two positions in a column differ by a forbidden distance, so it holds at most one start. The five row intervals are disjoint. That accounts for 5b of the 5b+4 positions.',
      'The four extra positions are b, b+1, 2b+2 and 2b+3. Zero forbids b and 2b+2. The other two differ by b+2, so at most one can be used. To reach the bound b, an occupied extra must cost one of the b columns.',
      'Suppose an extra is occupied and every odd column is occupied. In C_1, rows 0, 3 and 4 clash with that extra. Only rows 1 and 2 can remain. This is a restriction on an assumed packing, not a promise that either row is otherwise legal.',
      'From row 1 or 2 in column c, each row 0, 3 or 4 in column c+2 is forbidden. So an unbroken chain of occupied odd columns must stay in rows 1 and 2. At the final odd column c=b−2, those positions are 2b and 3b+2: both clash with zero. Contradiction. Some odd column is empty. Its missing start pays for the extra.'
    ];
    $('step-title').textContent = titles[step]; $('step-text').textContent = texts[step];
    if (b === 1) {
      $('step-title').textContent = 'The one-start bound is immediate.';
      $('step-text').textContent = 'Every positive distance from 1 through 8 is forbidden. With zero fixed, no other start fits in this nine-integer window. So there is at most one start. The odd-column chain is needed only for odd b of at least 3.';
      $('step-number').textContent = 'Direct case'; $('previous').disabled = true; $('next').disabled = true;
    }
    const instances = [
      `Here: ${b} columns × 5 positions = ${5 * b}; ${5 * b + 4} positions in the whole window.`,
      `Here the extras are ${b}, ${b + 1}, ${2 * b + 2}, ${2 * b + 3}. The possible pair differs by ${b + 2}.`,
      `Here t = ${t}; the first odd column has candidate positions ${1 + s[1]} and ${1 + s[2]}.`,
      `Here the odd columns are ${Array.from({ length: (b - 1) / 2 }, (_, i) => 2 * i + 1).join(' → ')}. Their last candidate positions are ${2 * b} and ${3 * b + 2}.`
    ];
    $('step-instance').textContent = b === 1 ? 'Special case b=1: all distances 1 through 8 are forbidden. Zero alone fills the allowed one start in a nine-integer window. There is no odd-column chain; no extra is possible.' : instances[step];
    $('exclusions').replaceChildren();
    if (b === 1 || step < 2) return;
    const heading = document.createElement('p'); heading.textContent = step === 2 ? 'Exact exclusions from the chosen extra:' : 'All forbidden exits from rows 1 and 2:';
    const list = document.createElement('ul');
    const formulas = step === 2 ? (high ? ['2b+2', 'b+2', '2b+2'] : ['b', '2b+4', '3b+4']) : ['b', '2b+4', '3b+4', '2b+2', 'b+2', '2b+2'];
    const entries = step === 2 ? initialExclusions(b, t) : transitions(b);
    entries.forEach((e, i) => {
      const li = document.createElement('li');
      li.textContent = step === 2 ? `Row ${e.row}, position ${e.position}: distance ${formulas[i]} = ${e.distance}.` : `Row ${e.from} → row ${e.to}: distance ${formulas[i]} = ${e.distance}.`;
      list.append(li);
    });
    $('exclusions').append(heading, list);
  }
  function renderPeriod() {
    const n = 5 * b + 4, s = shape(b), next = $('seam').checked, periods = next ? 2 : 1;
    const end = Math.max(n, (periods - 1) * n + 2 * b - 2 + s[4]), scale = 490 / end, px = x => 25 + x * scale;
    let body = line(25, 18, 515, 18, '#a6ada6');
    for (let p = 0; p < periods; p++) {
      for (let i = 0; i < b; i++) {
        const start = p * n + 2 * i, y = 58 + i * 22;
        body += `<path d="M${px(start) - 3},10 l6,0 l-3,6 z" fill="${p ? rust : teal}"/>`;
        body += line(px(start), y, px(start + s[4]), y, '#d0d2c6');
        s.forEach(v => { body += `<circle cx="${px(start + v)}" cy="${y}" r="3" fill="${p ? rust : teal}"/>`; });
      }
    }
    body += line(px(n), 5, px(n), 65 + b * 22, rust, 'dash') + text(px(n), 40, `n=${n}`, rust, 12);
    body += text(45, 40, '0', ink, 12);
    $('period-picture').innerHTML = svg(`${periods} period${periods > 1 ? 's' : ''} of starts spaced by two, with period length ${n}. Copies cross the boundary without sharing a mark.`, 540, 76 + b * 22, body);
    $('period-description').textContent = `${b === 1 ? "Start at 0" : `Start at 0, 2, …, ${2 * b - 2}`}; repeat every ${n} integers. Switch the next period off and on to inspect the seam.`;
    $('density').textContent = `${b} ${b === 1 ? "start" : "starts"} / ${n} integers`;
    $('period-detail').textContent = `Starting density ${b}/${n}. Covered density ${5 * b}/${n}. Each copy has five marks, so these are different quantities. The rule extends in both directions forever; the diagram shows only ${periods} period${periods > 1 ? 's' : ''} of starts.${b > 1 ? ` In the window argument, this construction uses the extra at ${b + 1} and leaves the final odd column C${b - 2} empty.` : ''}`;
  }
  function render() { renderShape(); renderStarts(); renderColumns(); renderPeriod(); }
  $('parameter-form').noValidate = true;
  $('parameter-form').addEventListener('submit', event => {
    event.preventDefault();
    try {
      b = parameter($('parameter').value); step = 0; high = false;
      $('parameter').removeAttribute('aria-invalid'); $('parameter-message').textContent = `Shape changed to b = ${b}. Starts and proof steps reset.`;
      reset(); render();
    } catch (error) {
      $('parameter').setAttribute('aria-invalid', 'true'); $('parameter-message').textContent = error.message;
    }
  });
  for (const name of ['packing', 'proof', 'period']) $('mode-' + name).addEventListener('click', () => {
    mode = name;
    for (const item of ['packing', 'proof', 'period']) {
      $(item).hidden = item !== mode; $('mode-' + item).setAttribute('aria-pressed', String(item === mode));
    }
  });
  $('starts').addEventListener('click', event => {
    const button = event.target.closest('button[data-start]'); if (button) place(Number(button.dataset.start));
  });
  $('starts').addEventListener('keydown', event => {
    const button = event.target.closest('button[data-start]'); if (!button) return;
    const x = Number(button.dataset.start), last = 5 * b + 3;
    const moves = { ArrowLeft: x - 1, ArrowRight: x + 1, ArrowUp: x - 1, ArrowDown: x + 1, Home: 1, End: last };
    if (!(event.key in moves)) return;
    event.preventDefault(); cursor = Math.max(1, Math.min(last, moves[event.key]));
    for (const item of $('starts').children) item.tabIndex = Number(item.dataset.start) === cursor ? 0 : -1;
    $('starts').querySelector(`[data-start="${cursor}"]`).focus();
  });
  $('reset').addEventListener('click', reset);
  $('load-lower').addEventListener('click', () => {
    selected = lower(b); drawCollision(null); renderStarts();
    $('placement-message').textContent = `Loaded {${selected.join(', ')}}: ${b} legal starts.${b > 1 ? ` The extra at ${b + 1} is used, and column C${b - 2} is empty: the construction really pays for its extra.` : ''} The third encounter shows why repeating these also works across the boundary.`;
  });
  $('previous').addEventListener('click', () => { step = Math.max(0, step - 1); renderColumns(); });
  $('next').addEventListener('click', () => { step = Math.min(3, step + 1); renderColumns(); });
  $('extra-low').addEventListener('click', () => { high = false; renderColumns(); });
  $('extra-high').addEventListener('click', () => { high = true; renderColumns(); });
  $('seam').addEventListener('change', renderPeriod);
  reset(); render();
})();
