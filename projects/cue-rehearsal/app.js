/* DOM adapter. Every derived time and import/edit boundary comes from model.js. */
(function () {
  'use strict';
  const model = globalThis.CueRehearsal;
  const $ = id => document.getElementById(id);
  let project = model.initial();
  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  }
  function message(id, text, error = false) {
    $(id).textContent = text; $(id).classList.toggle('error', error);
  }
  function selectStep() {
    const step = project.scenario.steps.find(s => s.id === $('step').value);
    $('duration').value = step.duration;
    $('release').value = step.release;
    $('prerequisites').value = step.prerequisites.join(', ');
    $('resource').value = step.resource;
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
    $('project-title').textContent = project.title; $('origin').textContent = project.origin;
    $('step').replaceChildren();
    for (const step of project.scenario.steps) {
      const option = node('option', `${step.label} (${step.id})`); option.value = step.id;
      $('step').append(option);
    }
    if (project.scenario.steps.some(s => s.id === selected)) $('step').value = selected;
    selectStep();
    $('resource-controls').replaceChildren(); $('resource-ids').replaceChildren();
    for (const resource of project.scenario.resources) {
      const label = node('label', undefined, 'resource-toggle');
      const input = node('input'); input.type = 'checkbox'; input.id = `available-${resource.id}`; input.checked = resource.available;
      input.addEventListener('change', () => {
        project = model.setResource(project, resource.id, input.checked); render();
        message('edit-message', `${resource.name} is ${input.checked ? 'available' : 'unavailable'} in the scenario.`);
      });
      label.append(input, node('span', `${resource.name} (${resource.id})`));
      $('resource-controls').append(label);
      const option = node('option'); option.value = resource.id; $('resource-ids').append(option);
    }
    const result = model.compare(project);
    renderPlan('baseline', project.baseline, result.baseline);
    renderPlan('scenario', project.scenario, result.scenario);
    $('changes').replaceChildren(...result.changes.map(change => node('li', `${change.id}: ${change.message}`)));
    if (focused && $(focused)) $(focused).focus();
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
      project = next; render(); message('edit-message', 'Scenario updated. See each cue’s explanation and the change from baseline below.');
    } catch (error) { message('edit-message', `Change rejected: ${error.message}. Current project preserved.`, true); }
  });
  $('reset').addEventListener('click', () => {
    project = model.resetScenario(project); render(); message('edit-message', 'Scenario replaced with a fresh clone of the baseline.');
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
      project = next; render(); message('io-message', 'Imported baseline and scenario. Both are shown above.');
      message('edit-message', 'The imported scenario is ready to edit.');
    } catch (error) { message('io-message', `Import rejected: ${error.message}. Current project preserved.`, true); }
  });
  render();
}());
