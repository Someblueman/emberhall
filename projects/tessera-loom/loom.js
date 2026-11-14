/* Original Tessera Loom geometry and interface. No dependencies or network. */
(function () {
  'use strict';

  const PALETTES = Object.freeze({
    tidal: Object.freeze({ ink: '#285a61', paper: '#f5ecdb' }),
    ochre: Object.freeze({ ink: '#a54e32', paper: '#f9e8ce' }),
    fern: Object.freeze({ ink: '#355c42', paper: '#e9eddb' }),
  });
  // Both orientations touch all four midpoints, perpendicular to the edge.
  const ARCS = Object.freeze([
    Object.freeze(['M0 50 A50 50 0 0 0 50 0', 'M50 100 A50 50 0 0 1 100 50']),
    Object.freeze(['M50 0 A50 50 0 0 0 100 50', 'M0 50 A50 50 0 0 1 50 100']),
  ]);

  function validate(value) {
    const fail = (message) => { throw new Error(message); };
    if (!value || typeof value !== 'object' || Array.isArray(value)) fail('Expected a motif object.');
    if (Object.keys(value).sort().join(',') !== 'palette,size,tiles,version') fail('Use only version, size, tiles and palette.');
    if (value.version !== 1) fail('This studio reads motif version 1.');
    if (!Number.isInteger(value.size) || value.size < 2 || value.size > 8) fail('Size must be an integer from 2 to 8.');
    if (typeof value.palette !== 'string' || !Object.hasOwn(PALETTES, value.palette)) fail('Palette must be tidal, ochre or fern.');
    if (!Array.isArray(value.tiles) || value.tiles.length !== value.size ** 2 ||
        Array.from(value.tiles).some((tile) => tile !== 0 && tile !== 1)) fail('Tiles must contain exactly size × size zeroes or ones.');
    return { version: 1, size: value.size, tiles: [...value.tiles], palette: value.palette };
  }

  function parseJSON(text) {
    if (typeof text !== 'string' || text.length > 32768) throw new Error('Use a JSON motif of at most 32,768 characters.');
    let value;
    try { value = JSON.parse(text); } catch (_) { throw new Error('That is not valid JSON.'); }
    return validate(value);
  }

  function toJSON(motif) { return JSON.stringify(validate(motif), null, 2) + '\n'; }

  function initial() {
    return { version: 1, size: 4, tiles: [0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0], palette: 'tidal' };
  }

  function turn(motif, index) {
    const next = validate(motif);
    if (!Number.isInteger(index) || index < 0 || index >= next.tiles.length) throw new Error('Tile index is outside the motif.');
    next.tiles[index] = 1 - next.tiles[index];
    return next;
  }

  function resize(motif, size) {
    const old = validate(motif);
    const next = validate({ version: 1, size, palette: old.palette, tiles: Array.from({ length: 64 }, () => 0).slice(0, size ** 2) });
    for (let row = 0; row < Math.min(size, old.size); row++) {
      for (let col = 0; col < Math.min(size, old.size); col++) next.tiles[row * size + col] = old.tiles[row * old.size + col];
    }
    return next;
  }

  function paths(tile) {
    return ARCS[tile].map((d) => `<path d="${d}"/>`).join('');
  }

  function svg(motif, repeats) {
    const m = validate(motif);
    if (repeats !== 4 && repeats !== 8) throw new Error('Repeat count must be 4 or 8.');
    const side = m.size * repeats;
    const { ink, paper } = PALETTES[m.palette];
    let drawing = '';
    for (let row = 0; row < side; row++) {
      for (let col = 0; col < side; col++) {
        drawing += `<g transform="translate(${col * 100} ${row * 100})">${paths(m.tiles[(row % m.size) * m.size + col % m.size])}</g>`;
      }
    }
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${side * 100} ${side * 100}" width="${side * 100}" height="${side * 100}" role="img" aria-labelledby="tessera-title"><title id="tessera-title">Tessera Loom: ${m.size} by ${m.size} motif, repeated ${repeats} by ${repeats}</title><rect width="100%" height="100%" fill="${paper}"/><g fill="none" stroke="${ink}" stroke-width="14" stroke-linecap="butt">${drawing}</g></svg>\n`;
  }

  function mount() {
    const get = (id) => document.getElementById(id);
    const editor = get('editor');
    let motif = initial();
    let selected = 0;
    let shownExport = null;

    function message(text, error = false) {
      get('message').textContent = text;
      get('message').classList.toggle('error', error);
    }

    function invalidateExport() {
      shownExport = null;
      get('download').disabled = true;
      get('transfer').value = '';
    }

    function render(focusTile = false) {
      const { ink, paper } = PALETTES[motif.palette];
      editor.style.gridTemplateColumns = `repeat(${motif.size}, 1fr)`;
      editor.replaceChildren();
      motif.tiles.forEach((tile, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'tile' + (index === selected ? ' selected' : '');
        button.dataset.index = String(index);
        button.tabIndex = index === selected ? 0 : -1;
        button.setAttribute('aria-label', `Row ${Math.floor(index / motif.size) + 1}, column ${index % motif.size + 1}: ${tile ? 'top to right' : 'top to left'} arcs. Turn tile.`);
        button.innerHTML = `<svg viewBox="0 0 100 100" aria-hidden="true"><rect width="100" height="100" fill="${paper}"/><g fill="none" stroke="${ink}" stroke-width="14">${paths(tile)}</g></svg>`;
        editor.append(button);
      });
      get('size').value = String(motif.size);
      get('size-output').value = String(motif.size);
      get('size-label').textContent = `${motif.size} × ${motif.size}`;
      get('palette').value = motif.palette;
      const repeats = Number(get('repeats').value);
      get('preview').innerHTML = svg(motif, repeats);
      get('summary').textContent = `${motif.size} × ${motif.size} motif · ${repeats} × ${repeats} repeats · ${motif.size * repeats} × ${motif.size * repeats} tiles`;
      if (focusTile) editor.children[selected].focus();
    }

    function edit(next, focusTile = false) {
      motif = validate(next);
      selected = Math.min(selected, motif.tiles.length - 1);
      invalidateExport();
      render(focusTile);
      message('Motif changed. Show a fresh export when you are ready to save.');
    }

    editor.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-index]');
      if (!button) return;
      selected = Number(button.dataset.index);
      edit(turn(motif, selected), true);
    });
    editor.addEventListener('focusin', (event) => {
      const button = event.target.closest('button[data-index]');
      if (!button) return;
      selected = Number(button.dataset.index);
      Array.from(editor.children).forEach((tile, i) => {
        tile.tabIndex = i === selected ? 0 : -1;
        tile.classList.toggle('selected', i === selected);
      });
    });
    editor.addEventListener('keydown', (event) => {
      const col = selected % motif.size;
      const row = Math.floor(selected / motif.size);
      let next;
      if (event.key === 'ArrowRight') next = row * motif.size + (col + 1) % motif.size;
      else if (event.key === 'ArrowLeft') next = row * motif.size + (col + motif.size - 1) % motif.size;
      else if (event.key === 'ArrowDown') next = (selected + motif.size) % motif.tiles.length;
      else if (event.key === 'ArrowUp') next = (selected + motif.tiles.length - motif.size) % motif.tiles.length;
      else if (event.key === 'Home') next = event.ctrlKey ? 0 : row * motif.size;
      else if (event.key === 'End') next = event.ctrlKey ? motif.tiles.length - 1 : (row + 1) * motif.size - 1;
      else return;
      event.preventDefault();
      editor.children[next].focus();
    });
    get('size').addEventListener('input', () => edit(resize(motif, Number(get('size').value))));
    get('palette').addEventListener('change', () => edit({ ...motif, palette: get('palette').value }));
    get('invert').addEventListener('click', () => edit({ ...motif, tiles: motif.tiles.map((tile) => 1 - tile) }));
    get('clear').addEventListener('click', () => edit({ ...motif, tiles: motif.tiles.map(() => 0) }));
    get('repeats').addEventListener('change', () => { invalidateExport(); render(); message('Repeat size changed. Show a fresh export to save it.'); });
    get('transfer').addEventListener('input', () => { shownExport = null; get('download').disabled = true; });
    get('load').addEventListener('click', () => {
      try {
        const next = parseJSON(get('transfer').value);
        edit(next);
        message('Loaded JSON motif. Preview updated; show JSON or SVG to save.');
      } catch (error) { message(`${error.message} Your motif has not changed.`, true); }
    });
    function show(format) {
      const content = format === 'json' ? toJSON(motif) : svg(motif, Number(get('repeats').value));
      shownExport = { content, format };
      get('transfer').value = content;
      get('download').disabled = false;
      message(`${format.toUpperCase()} is shown below. Save it, or select and copy the text.`);
    }
    get('show-json').addEventListener('click', () => show('json'));
    get('show-svg').addEventListener('click', () => show('svg'));
    get('download').addEventListener('click', () => {
      if (!shownExport) return;
      const { content, format } = shownExport;
      const url = URL.createObjectURL(new Blob([content], { type: format === 'json' ? 'application/json' : 'image/svg+xml' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `tessera-motif.${format}`;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      message('Save requested. If the browser blocks downloads, select and copy the shown export.');
    });
    render();
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { validate, parseJSON, toJSON, initial, turn, resize, svg, ARCS };
  if (typeof document !== 'undefined') mount();
}());
