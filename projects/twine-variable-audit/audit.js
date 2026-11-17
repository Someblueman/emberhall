/* Bounded concrete route exploration: no guessed branch can become a witness. */
(function (root) {
  'use strict';
  const S = typeof module !== 'undefined' ? require('./story.js') : root.TwineStory;
  const E = typeof module !== 'undefined' ? require('./expression.js') : root.TwineExpression;
  const DEFAULTS = {states:2000, depth:48, steps:100000, findings:500};
  function audit(html, limits = DEFAULTS) {
    limits = {...DEFAULTS,...limits};
    const story = S.extract(html), compiled = new Map();
    const unchecked = [...story.unchecked], findings = [], findingKeys = new Set(), noteKeys = new Set();
    const names = new Map(), occurrences = new Map(); let steps = 0, stopped = false;
    function note(passage,line,reason) {
      const key = JSON.stringify([passage,line,reason]);
      if (!noteKeys.has(key)) { noteKeys.add(key); unchecked.push({passage,line,reason}); }
    }
    for (const p of story.passages.values()) {
      let code;
      try { code = S.compile(p); }
      catch (error) { code = {...p,nodes:[{type:'blocked',line:1,value:error.message}],notes:[{passage:p.name,line:1,reason:error.message}],names:[]}; }
      compiled.set(p.name,code);
      for (const n of code.notes) note(n.passage,n.line,n.reason);
      for (const n of code.names) {
        const key = n.name.toLowerCase();
        if (!names.has(key)) names.set(key,new Map());
        const group = names.get(key);
        if (!group.has(n.name)) group.set(n.name,n);
      }
      for (const token of flatten(code.nodes)) {
        if (token.type === 'link' && !compiled.has(token.value) && !story.passages.has(token.value)) note(p.name,token.line,'Missing link target: ' + token.value);
      }
    }
    for (const group of names.values()) {
      if (group.size < 2) continue;
      if (findings.length >= limits.findings) { note('Story',1,'Finding limit reached; remaining analysis is unchecked.'); stopped = true; break; }
      findings.push({kind:'case', names:[...group.keys()], locations:[...group.values()], passage:[...group.values()][0].passage,line:[...group.values()][0].line});
    }
    function execute(passage,env,path,prior = []) {
      function observe(name,line) {
        const key = JSON.stringify([name,passage.name,line]);
        if (!occurrences.has(key)) occurrences.set(key,[...path]);
      }
      const links = [], decisions = [];
      function read(name,line) {
        observe(name,line);
        if (env[name] !== undefined) return;
        const key = JSON.stringify([passage.name,line,name]);
        if (findingKeys.has(key)) return;
        if (findings.length >= limits.findings) { note(passage.name,line,'Finding limit reached; remaining analysis is unchecked.'); stopped = true; return; }
        findingKeys.add(key);
        findings.push({kind:'unset',name,passage:passage.name,line,path:[...path],decisions:[...prior,...decisions]});
      }
      function value(ast,line) { return E.evaluate(ast,env,name => read(name,line)); }
      function run(nodes) {
        for (const node of nodes) {
          if (stopped) return false;
          if (++steps > limits.steps) { note(passage.name,node.line,'Execution step limit reached; remaining routes are unchecked.'); stopped = true; return false; }
          if (node.type === 'blocked') return false;
          if (node.type === 'set') {
            const v = value(node.value.value,node.line);
            if (typeof v === 'number' && !Number.isFinite(v)) { note(passage.name,node.line,'Non-finite arithmetic result is unchecked.'); return false; }
            if (typeof v === 'string' && v.length > 10000) { note(passage.name,node.line,'Computed string length limit reached.'); return false; }
            observe(node.value.name,node.line);
            env[node.value.name] = v;
          } else if (node.type === 'read') {
            const output = value(node.value,node.line);
            if (typeof output === 'string' && /[<\[$_?{]|@@|(?:https?|ftp|mailto):/.test(output)) {
              note(passage.name,node.line,'Printed string may expand more story markup; the remaining route is unchecked.');
              return false;
            }
          }
          else if (node.type === 'link') links.push({target:node.value,line:node.line});
          else if (node.type === 'if') {
            for (const branch of node.branches) {
              const matches = branch.condition === null || Boolean(value(branch.condition,branch.line));
              decisions.push({passage:passage.name,line:branch.line,taken:matches});
              if (matches) { if (!run(branch.nodes)) return false; break; }
            }
          }
        }
        return true;
      }
      return run(passage.nodes) ? {links,env,decisions} : null;
    }
    let initial = Object.create(null), initialOK = !story.globalBarrier, initialDecisions = [];
    if (initialOK && compiled.has('StoryInit')) {
      const init = execute(compiled.get('StoryInit'),initial,['StoryInit']);
      initialOK = Boolean(init);
      initialDecisions = init?.decisions || [];
      if (init?.links.length) { note('StoryInit',1,'Links in StoryInit are unsupported; routes were not analysed.'); initialOK = false; }
    }
    const queue = initialOK ? [{passage:story.start,env:initial,path:[story.start],decisions:initialDecisions}] : [];
    const seen = new Set(), visited = new Set(), scheduled = new Set(); let index = 0;
    function stateKey(item) {
      return JSON.stringify([item.passage,Object.keys(item.env).filter(k => k.startsWith('$')).sort().map(k => [k,typeof item.env[k],Object.is(item.env[k],-0) ? '-0' : String(item.env[k])])]);
    }
    if (queue.length) scheduled.add(stateKey(queue[0]));
    while (index < queue.length && !stopped) {
      const item = queue[index++];
      for (const key of Object.keys(item.env)) if (key.startsWith('_')) delete item.env[key];
      const key = stateKey(item);
      if (seen.has(key)) continue;
      if (seen.size >= limits.states) { note(item.passage,1,'State limit reached; remaining routes are unchecked.'); break; }
      seen.add(key); visited.add(item.passage);
      const p = compiled.get(item.passage);
      const result = execute(p,item.env,item.path,item.decisions);
      if (!result) continue;
      for (const link of result.links) {
        if (!compiled.has(link.target)) continue;
        if (link.target === 'StoryInit') { note(p.name,link.line,'A link into the StoryInit code passage is unchecked.'); continue; }
        const nextKey = stateKey({passage:link.target,env:result.env});
        if (scheduled.has(nextKey)) continue;
        if (item.path.length >= limits.depth) { note(p.name,link.line,'Route depth limit reached; later visits are unchecked.'); continue; }
        if (queue.length >= limits.states) { note(p.name,link.line,'State limit reached; remaining choices are unchecked.'); continue; }
        scheduled.add(nextKey);
        queue.push({passage:link.target,env:Object.assign(Object.create(null),result.env),path:[...item.path,link.target],decisions:[...item.decisions,...result.decisions]});
      }
    }
    for (const p of story.passages.values()) {
      if (p.name !== 'StoryInit' && !visited.has(p.name)) note(p.name,1,'Passage was not reached by a supported route.');
    }
    for (const f of findings) {
      if (f.kind === 'case') for (const location of f.locations) location.path = occurrences.get(JSON.stringify([location.name,location.passage,location.line])) || null;
    }
    return {name:story.name,start:story.start,findings,unchecked,passages:[...story.passages.values()],states:seen.size,steps,limits,complete:unchecked.length === 0};
  }
  function flatten(nodes) {
    return nodes.flatMap(n => n.type === 'if' ? [n,...n.branches.flatMap(b => flatten(b.nodes))] : [n]);
  }
  const api = {audit,DEFAULTS};
  if (typeof module !== 'undefined') module.exports = api;
  root.TwineAudit = api;
})(globalThis);
