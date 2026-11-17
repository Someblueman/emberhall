/* DOM adapter. Every derived time and import/edit boundary comes from model.js. */
(function () {
  'use strict';
  const model = globalThis.CueRehearsal;
  const $ = id => document.getElementById(id);
  const SVG_NS = 'http://www.w3.org/2000/svg';
  let project = model.initial();
  const history = [];
  function pushUndo() {
    history.push(project);
    if (history.length > 30) history.shift();
  }
  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  }
  function svgNode(tag, attrs, className) {
    const element = document.createElementNS(SVG_NS, tag);
    if (className) element.setAttribute('class', className);
    for (const [k, v] of Object.entries(attrs || {})) element.setAttribute(k, String(v));
    return element;
  }
  function message(id, text, error = false) {
    $(id).textContent = text; $(id).classList.toggle('error', error);
  }
  function syncTimelineSelection() {
    const selected = $('step').value;
    for (const btn of $('timeline').querySelectorAll('.tl-cue-btn')) {
      const active = btn.dataset.stepId === selected;
      btn.classList.toggle('is-selected', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    }
  }
  function selectStep() {
    const step = project.scenario.steps.find(s => s.id === $('step').value);
    if (!step) return;
    $('duration').value = step.duration;
    $('release').value = step.release;
    $('prerequisites').value = step.prerequisites.join(', ');
    $('resource').value = step.resource;
    syncTimelineSelection();
  }
  function renderTimeline() {
    const tl = model.timelineData(project);
    const bFin = tl.baselineFinish === null ? 'blocked' : `${tl.baselineFinish} min`;
    const sFin = tl.scenarioFinish === null ? 'blocked' : `${tl.scenarioFinish} min`;
    const delta = tl.deltaFinish === null ? 'unfinished'
      : (tl.deltaFinish === 0 ? 'no finish change' : `${tl.deltaFinish > 0 ? '+' : ''}${tl.deltaFinish} min finish`);
    $('timeline-summary').textContent = `Original ${bFin} · Rehearsal ${sFin} (${delta}). Click any cue to edit it.`;
    const container = $('timeline');
    container.replaceChildren();
    const span = tl.maxTime - tl.minTime;
    const xAt = t => ((t - tl.minTime) / span) * 1000;
    const scaleRow = node('div', undefined, 'tl-scale-row');
    scaleRow.append(node('span', 'Cue & track', 'tl-scale-label'));
    const scaleAxis = node('div', undefined, 'tl-scale-axis');
    const midTime = Math.round((tl.minTime + tl.maxTime) / 2);
    scaleAxis.append(
      node('span', `${tl.minTime}m`),
      node('span', `${midTime}m`),
      node('span', `${tl.maxTime}m`)
    );
    scaleRow.append(scaleAxis, node('span', 'Rehearsal', 'tl-scale-time'));
    container.append(scaleRow);
    const selected = $('step').value;
    for (const row of tl.rows) {
      const rowEl = node('div', undefined, 'tl-row');
      const btn = node('button', undefined, 'tl-cue-btn');
      btn.type = 'button';
      btn.dataset.stepId = row.id;
      const isSelected = row.id === selected;
      btn.classList.toggle('is-selected', isSelected);
      btn.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
      btn.append(node('span', row.label, 'tl-cue-label'), node('span', `${row.track} · ${row.resource}`, 'tl-cue-meta'));
      btn.addEventListener('click', () => {
        $('step').value = row.id;
        selectStep();
        $('duration').focus();
      });
      const svg = svgNode('svg', { viewBox: '0 0 1000 28', preserveAspectRatio: 'none', 'aria-hidden': 'true' }, 'tl-bar-svg');
      for (const conflict of tl.scenarioConflicts) {
        const cx = xAt(conflict.start), cw = Math.max(8, xAt(conflict.end) - cx);
        svg.append(svgNode('rect', { x: cx.toFixed(1), y: 0, width: cw.toFixed(1), height: 28 }, 'tl-conflict-band'));
      }
      if (row.baseline && !row.baseline.blocked) {
        const bx = xAt(row.baseline.start), bw = Math.max(8, xAt(row.baseline.end) - bx);
        svg.append(svgNode('rect', { x: bx.toFixed(1), y: 3, width: bw.toFixed(1), height: 8, rx: 2 }, 'tl-bar-base'));
      }
      let timeText = 'absent', timeWarn = false;
      if (row.scenario) {
        if (row.scenario.blocked) {
          svg.append(svgNode('rect', { x: 0, y: 14, width: 120, height: 11, rx: 2 }, 'tl-bar-blocked'));
          timeText = 'BLOCKED';
          timeWarn = true;
        } else {
          const sx = xAt(row.scenario.start), sw = Math.max(8, xAt(row.scenario.end) - sx);
          const shifted = (row.scenario.deltaStart !== null && row.scenario.deltaStart !== 0) ||
            (row.scenario.deltaEnd !== null && row.scenario.deltaEnd !== 0);
          const barClass = (shifted || row.scenario.conflicting) ? 'tl-bar-changed' : 'tl-bar-ok';
          svg.append(svgNode('rect', { x: sx.toFixed(1), y: 14, width: sw.toFixed(1), height: 11, rx: 2 }, barClass));
          const dEnd = row.scenario.deltaEnd;
          const note = row.scenario.conflicting ? ' overlap'
            : (dEnd !== null && dEnd !== 0 ? ` (${dEnd > 0 ? '+' : ''}${dEnd}m)` : '');
          timeText = `${row.scenario.start} → ${row.scenario.end}${note}`;
          timeWarn = Boolean(row.scenario.conflicting || (dEnd !== null && dEnd > 0));
        }
      }
      const timeEl = node('span', timeText, timeWarn ? 'tl-time is-alert' : 'tl-time');
      rowEl.append(btn, svg, timeEl);
      container.append(rowEl);
    }
  }
  function renderPlan(kind, plan, result) {
    $(`${kind}-name`).textContent = plan.name;
    const blocked = result.entries.filter(e => e.start === null).length;
    $(`${kind}-summary`).textContent = `${blocked ? `${blocked} blocked · finish unresolved` : `Earliest finish: ${result.finish} min`} · ${result.conflicts.length} resource overlap(s)`;
    const target = $(`${kind}-result`); target.replaceChildren();
    const steps = new Map(plan.steps.map(s => [s.id, s]));
    for (const group of result.cycles) target.append(node('p', `Cycle: ${group.join(' ↔ ')}`, 'issue'));
    for (const conflict of result.conflicts) target.append(node('p',
      `Resource overlap: ${conflict.resource} · ${conflict.steps.join(' & ')} · [${conflict.start}, ${conflict.end}). Times stay unchanged.`, 'issue'));
    const entries = [...result.entries].sort((a, b) => {
      const sa = steps.get(a.id), sb = steps.get(b.id);
      return sa.track.localeCompare(sb.track, 'en') || (a.start ?? Infinity) - (b.start ?? Infinity) || a.id.localeCompare(b.id, 'en');
    });
    let track;
    for (const entry of entries) {
      const step = steps.get(entry.id);
      if (track !== step.track) { track = step.track; target.append(node('h4', track, 'track')); }
      const cue = node('div', undefined, 'cue');
      const top = node('div', undefined, 'cue-top');
      top.append(node('strong', step.label), node('span', entry.start === null ? 'BLOCKED' : `${entry.start} → ${entry.end}`, 'time'));
      cue.append(top, node('p', `${step.id} · ${step.duration} min · ${step.resource}`, 'cue-meta'), node('p', entry.explanation, 'explanation'));
      target.append(cue);
    }
  }
  function render() {
    const selected = $('step').value, focused = document.activeElement.id;
    const focusedStep = document.activeElement.dataset ? document.activeElement.dataset.stepId : null;
    $('project-title').textContent = project.title; $('origin').textContent = project.origin;
    $('step').replaceChildren();
    for (const step of project.scenario.steps) {
      const option = node('option', `${step.label} (${step.id})`); option.value = step.id;
      $('step').append(option);
    }
    if (project.scenario.steps.some(s => s.id === selected)) $('step').value = selected;
    $('resource-controls').replaceChildren(); $('resource-ids').replaceChildren();
    for (const resource of project.scenario.resources) {
      const label = node('label', undefined, 'resource-toggle');
      const input = node('input'); input.type = 'checkbox'; input.id = `available-${resource.id}`; input.checked = resource.available;
      label.htmlFor = input.id;
      input.addEventListener('change', () => {
        pushUndo();
        project = model.setResource(project, resource.id, input.checked); render();
        message('edit-message', `${resource.name} is ${input.checked ? 'available' : 'unavailable'} in the scenario.`);
      });
      label.append(input, node('span', `${resource.name} (${resource.id})`));
      $('resource-controls').append(label);
      const option = node('option'); option.value = resource.id; $('resource-ids').append(option);
    }
    renderTimeline();
    selectStep();
    $('undo').disabled = history.length === 0;
    const result = model.compare(project);
    renderPlan('baseline', project.baseline, result.baseline);
    renderPlan('scenario', project.scenario, result.scenario);
    $('changes').replaceChildren(...result.changes.map(change => node('li', `${change.id}: ${change.message}`)));
    if (focused && $(focused)) $(focused).focus();
    else if (focusedStep) {
      const btn = $('timeline').querySelector(`.tl-cue-btn[data-step-id="${focusedStep}"]`);
      if (btn) btn.focus();
    }
  }
  $('step').addEventListener('change', selectStep);
  $('step-form').addEventListener('submit', event => {
    event.preventDefault();
    try {
      const raw = $('prerequisites').value.trim();
      const next = model.editStep(project, $('step').value, {
        duration: Number($('duration').value), release: Number($('release').value),
        prerequisites: raw ? raw.split(',').map(s => s.trim()) : [], resource: $('resource').value.trim()
      });
      pushUndo();
      project = next; render(); message('edit-message', 'Scenario updated. See the timeline, cue explanations and change from baseline below.');
    } catch (error) { message('edit-message', `Change rejected: ${error.message}. Current project preserved.`, true); }
  });
  $('reset').addEventListener('click', () => {
    pushUndo();
    project = model.resetScenario(project); render(); message('edit-message', 'Scenario replaced with a fresh clone of the baseline.');
  });
  $('undo').addEventListener('click', () => {
    if (!history.length) return;
    project = history.pop(); render(); message('edit-message', 'Restored the previous scenario.');
  });
  $('export').addEventListener('click', () => {
    $('json').value = model.toJSON(project); message('io-message', 'Exported the current baseline and scenario to the text box. Copy it or download a file to keep it.');
  });
  $('download').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([model.toJSON(project)], { type: 'application/json' }));
    const link = node('a'); link.href = url; link.download = 'cue-rehearsal.json';
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    message('io-message', 'Requested a JSON file download of both current plans.');
  });
  $('import').addEventListener('click', () => {
    try {
      const next = model.parseJSON($('json').value);
      pushUndo();
      project = next; render(); message('io-message', 'Imported baseline and scenario. Both are shown above.');
      message('edit-message', 'The imported scenario is ready to edit.');
    } catch (error) { message('io-message', `Import rejected: ${error.message}. Current project preserved.`, true); }
  });
  render();
}());
