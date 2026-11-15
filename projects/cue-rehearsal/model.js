/* Shared by the offline page and Node tests. No DOM, clock or I/O. */
(function (root) {
  'use strict';
  const MAX_TEXT = 200000;
  const fail = (message) => { throw new Error(message); };
  function record(value, keys, path) {
    if (!value || typeof value !== 'object' || Array.isArray(value) ||
        Object.getPrototypeOf(value) !== Object.prototype) fail(`${path}: expected an object`);
    const actual = Object.keys(value);
    if (actual.length !== keys.length || actual.some(k => !keys.includes(k)))
      fail(`${path}: expected exactly ${keys.join(', ')}`);
  }
  function text(value, path, max = 120) {
    if (typeof value !== 'string' || !value.trim() || value.length > max || /[\u0000-\u001f\u007f]/.test(value))
      fail(`${path}: expected 1–${max} visible characters`);
  }
  function id(value, path) {
    if (typeof value !== 'string' || !/^[a-z][a-z0-9-]{0,39}$/.test(value))
      fail(`${path}: use a letter followed by lowercase letters, digits or hyphens (max 40)`);
  }
  function integer(value, path, min, max) {
    if (!Number.isSafeInteger(value) || value < min || value > max)
      fail(`${path}: expected an integer from ${min} to ${max}`);
  }
  function list(value, path, min, max) {
    if (!Array.isArray(value) || value.length < min || value.length > max ||
        Object.keys(value).length !== value.length) fail(`${path}: expected ${min}–${max} entries`);
  }
  function validatePlan(plan, path) {
    record(plan, ['name', 'resources', 'steps'], path);
    text(plan.name, `${path}.name`);
    list(plan.resources, `${path}.resources`, 1, 30);
    const resources = new Set();
    for (const r of plan.resources) {
      record(r, ['id', 'name', 'available'], `${path}.resource`);
      id(r.id, 'resource.id'); text(r.name, 'resource.name');
      if (resources.has(r.id)) fail(`${path}: duplicate resource ID ${r.id}`);
      resources.add(r.id);
      if (typeof r.available !== 'boolean') fail('resource.available: expected boolean');
    }
    list(plan.steps, `${path}.steps`, 1, 80);
    const ids = new Set();
    for (const step of plan.steps) {
      record(step, ['id', 'label', 'track', 'release', 'duration', 'prerequisites', 'resource'], `${path}.step`);
      id(step.id, 'step.id'); text(step.label, 'step.label'); text(step.track, 'step.track', 40);
      if (ids.has(step.id)) fail(`${path}: duplicate step ID ${step.id}`);
      ids.add(step.id);
      integer(step.release, 'step.release', -1000000, 1000000);
      integer(step.duration, 'step.duration', 1, 1000000);
      list(step.prerequisites, 'step.prerequisites', 0, 80);
      for (const p of step.prerequisites) id(p, 'prerequisite');
      if (new Set(step.prerequisites).size !== step.prerequisites.length) fail('duplicate prerequisite');
      id(step.resource, 'step.resource');
    }
    return plan;
  }
  function validate(project) {
    record(project, ['version', 'title', 'origin', 'baseline', 'scenario'], 'project');
    if (project.version !== 1) fail('version: expected 1');
    text(project.title, 'title'); text(project.origin, 'origin');
    validatePlan(project.baseline, 'baseline'); validatePlan(project.scenario, 'scenario');
    if (JSON.stringify(project, null, 2).length + 1 > MAX_TEXT) fail('Formatted JSON exceeds 200000 characters');
    return project;
  }
  const clone = value => JSON.parse(JSON.stringify(value));
  function parseJSON(source) {
    if (typeof source !== 'string' || source.length > MAX_TEXT) fail('JSON exceeds 200000 characters');
    return validate(JSON.parse(source));
  }
  function toJSON(project) {
    validate(project);
    const result = JSON.stringify(project, null, 2) + '\n';
    if (result.length > MAX_TEXT) fail('JSON exceeds 200000 characters');
    return result;
  }
  // Tarjan components isolate cycles from steps merely downstream of a cycle.
  function cycleGroups(steps) {
    const byId = new Map(steps.map(s => [s.id, s]));
    const indexes = new Map(), low = new Map(), active = new Set(), stack = [], groups = [];
    let next = 0;
    function visit(key) {
      indexes.set(key, next); low.set(key, next++); stack.push(key); active.add(key);
      for (const p of [...byId.get(key).prerequisites].sort()) {
        if (!byId.has(p)) continue;
        if (!indexes.has(p)) { visit(p); low.set(key, Math.min(low.get(key), low.get(p))); }
        else if (active.has(p)) low.set(key, Math.min(low.get(key), indexes.get(p)));
      }
      if (low.get(key) === indexes.get(key)) {
        const group = []; let p;
        do { p = stack.pop(); active.delete(p); group.push(p); } while (p !== key);
        group.sort();
        if (group.length > 1 || byId.get(key).prerequisites.includes(key)) groups.push(group);
      }
    }
    for (const key of [...byId.keys()].sort()) if (!indexes.has(key)) visit(key);
    return groups.sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0);
  }
  function calculate(plan) {
    validatePlan(plan, 'plan');
    const steps = new Map(plan.steps.map(s => [s.id, s]));
    const resources = new Map(plan.resources.map(r => [r.id, r]));
    const cycles = cycleGroups(plan.steps), cyclic = new Set(cycles.flat());
    const results = new Map();
    function derive(key) {
      if (results.has(key)) return results.get(key);
      const step = steps.get(key), blockers = [];
      if (cyclic.has(key)) blockers.push(`Cycle includes ${key}`);
      for (const p of [...step.prerequisites].sort()) if (!steps.has(p)) blockers.push(`Missing prerequisite: ${p}`);
      if (!resources.has(step.resource)) blockers.push(`Unknown resource: ${step.resource}`);
      else if (!resources.get(step.resource).available) blockers.push(`Unavailable resource: ${step.resource}`);
      // Cyclic members are already blocked: never recurse back into the component.
      const predecessors = cyclic.has(key) ? [] : [...step.prerequisites].sort()
        .filter(p => steps.has(p)).map(derive);
      for (const p of predecessors) if (p.start === null) blockers.push(`Blocked prerequisite: ${p.id}`);
      let start = null, end = null, explanation;
      if (blockers.length) explanation = blockers.join('; ') + '. No interval assigned.';
      else {
        start = Math.max(step.release, ...predecessors.map(p => p.end)); end = start + step.duration;
        const terms = [`release ${step.release}`, ...predecessors.map(p => `${p.id} ends ${p.end}`)];
        explanation = `Start ${start} = max(${terms.join(', ')}); finish ${end} = ${start} + ${step.duration}.`;
      }
      const result = { id: key, start, end, blockers, explanation };
      results.set(key, result); return result;
    }
    const entries = [...steps.keys()].sort().map(derive);
    const conflicts = [];
    for (let i = 0; i < entries.length; i++) for (let j = i + 1; j < entries.length; j++) {
      const a = entries[i], b = entries[j], resource = steps.get(a.id).resource;
      if (a.start !== null && b.start !== null && resource === steps.get(b.id).resource &&
          a.start < b.end && b.start < a.end)
        conflicts.push({ resource, steps: [a.id, b.id], start: Math.max(a.start, b.start), end: Math.min(a.end, b.end) });
    }
    return { entries, cycles, conflicts, finish: entries.some(e => e.start === null) ? null : Math.max(...entries.map(e => e.end)) };
  }
  function compare(project) {
    validate(project);
    const baseline = calculate(project.baseline), scenario = calculate(project.scenario);
    const before = new Map(baseline.entries.map(e => [e.id, e]));
    const after = new Map(scenario.entries.map(e => [e.id, e]));
    const changes = [...new Set([...before.keys(), ...after.keys()])].sort().map(key => {
      const a = before.get(key), b = after.get(key);
      if (!a) return { id: key, message: 'Added in scenario.' };
      if (!b) return { id: key, message: 'Absent from scenario.' };
      if (a.start === null || b.start === null) return { id: key, message:
        `Baseline ${a.start === null ? 'blocked' : a.start + '–' + a.end}; scenario ${b.start === null ? 'blocked' : b.start + '–' + b.end}.` };
      return { id: key, message: `Start ${b.start - a.start >= 0 ? '+' : ''}${b.start - a.start} min; finish ${b.end - a.end >= 0 ? '+' : ''}${b.end - a.end} min.` };
    });
    return { baseline, scenario, changes };
  }
  function editStep(project, key, patch) {
    validate(project);
    const copy = clone(project), step = copy.scenario.steps.find(s => s.id === key);
    if (!step) fail(`Unknown step: ${key}`);
    for (const k of Object.keys(patch)) {
      if (!['duration', 'release', 'prerequisites', 'resource'].includes(k)) fail(`Cannot edit ${k}`);
      step[k] = clone(patch[k]);
    }
    return validate(copy);
  }
  function setResource(project, key, available) {
    validate(project);
    const copy = clone(project), resource = copy.scenario.resources.find(r => r.id === key);
    if (!resource) fail(`Unknown resource: ${key}`);
    resource.available = available;
    return validate(copy);
  }
  function resetScenario(project) {
    validate(project);
    const copy = clone(project); copy.scenario = clone(copy.baseline); copy.scenario.name = 'Rehearsal';
    return copy;
  }
  function initial() {
    const resources = [['crew', 'Room crew'], ['projector', 'Projector'], ['printer', 'Printer'],
      ['paper-team', 'Paper team'], ['host', 'Workshop host']].map(([id, name]) => ({ id, name, available: true }));
    const step = (id, label, track, duration, prerequisites, resource) =>
      ({ id, label, track, release: 0, duration, prerequisites, resource });
    const baseline = { name: 'Original plan', resources, steps: [
      step('unlock', 'Unlock the room', 'Room', 5, [], 'crew'),
      step('tables', 'Arrange tables', 'Room', 10, ['unlock'], 'crew'),
      step('projector', 'Check projector', 'Room', 8, ['unlock'], 'projector'),
      step('room-ready', 'Walk through the room', 'Room', 4, ['tables', 'projector'], 'crew'),
      step('print', 'Print workshop cards', 'Paper', 6, [], 'printer'),
      step('pack', 'Pack the card sets', 'Paper', 7, ['print'], 'paper-team'),
      step('welcome', 'Welcome the group', 'Together', 3, ['room-ready', 'pack'], 'host')
    ] };
    return resetScenario({ version: 1, title: 'The print-and-make workshop', origin: 'Minute 0 · preparation begins', baseline, scenario: clone(baseline) });
  }
  const api = { validate, calculate, compare, parseJSON, toJSON, editStep, setResource, resetScenario, initial };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.CueRehearsal = api;
}(typeof globalThis !== 'undefined' ? globalThis : this));
