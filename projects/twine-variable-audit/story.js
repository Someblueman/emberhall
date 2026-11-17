/* Parse the serialized story as a small data language, without a DOM or runtime. */
(function (root) {
  'use strict';
  const E = typeof module !== 'undefined' ? require('./expression.js') : root.TwineExpression;
  const LIMITS = {input:2000000, passages:500, passage:60000, tokens:1500, nesting:32};
  function decode(text) {
    return text.replace(/&([^;\s&]+);/g, (whole, entity) => {
      const named = {amp:'&', lt:'<', gt:'>', quot:'"', apos:"'", '#39':"'", nbsp:'\u00a0'};
      if (Object.hasOwn(named, entity)) return named[entity];
      if (/^#(?:[0-9]+|x[0-9a-f]+)$/i.test(entity)) {
        const n = entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2),16) : Number(entity.slice(1));
        if (n > 0 && n <= 0x10ffff && !(n >= 0xd800 && n <= 0xdfff)) return String.fromCodePoint(n);
      }
      throw Error('Unsupported or invalid HTML entity: ' + whole);
    });
  }
  function attributes(source) {
    const attrs = Object.create(null);
    // Published Twine uses quoted attributes. Reject ambiguous hand-written HTML.
    const re = /\s+([a-z][a-z0-9-]*)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'))?/ig;
    let m, end = 0;
    while ((m = re.exec(source))) {
      if (source.slice(end,m.index).trim()) throw Error('Malformed attributes');
      const key = m[1].toLowerCase();
      if (Object.hasOwn(attrs,key)) throw Error('Duplicate attribute: ' + key);
      attrs[key] = decode(m[2] ?? m[3] ?? ''); end = re.lastIndex;
    }
    if (source.slice(end).trim()) throw Error('Malformed attributes');
    return attrs;
  }
  function extract(html) {
    if (typeof html !== 'string' || html.length > LIMITS.input) throw Error('Story exceeds the two-million-character input limit');
    const containers = [...html.matchAll(/<tw-storydata\b([^>]*)>([\s\S]*?)<\/tw-storydata\s*>/gi)];
    if (containers.length !== 1 || (html.match(/<tw-storydata\b/gi) || []).length !== 1) throw Error('Expected exactly one complete tw-storydata element');
    const attrs = attributes(containers[0][1]);
    if (attrs.format !== 'SugarCube' || !/^2\.37(?:\.\d+)?$/.test(attrs['format-version'] || '')) throw Error('This first version checks published Twine 2 SugarCube 2.37.x stories only');
    const body = containers[0][2], passages = new Map(), ids = new Map(), unchecked = [];
    const re = /<tw-passagedata\b([^>]*)>([\s\S]*?)<\/tw-passagedata\s*>/gi;
    let m, remainder = body;
    while ((m = re.exec(body))) {
      if (passages.size >= LIMITS.passages) throw Error('More than 500 passages');
      const a = attributes(m[1]);
      if (!a.name || !a.pid || passages.has(a.name) || ids.has(a.pid)) throw Error('Passage names and identifiers must be present and unique');
      if (m[2].includes('<')) throw Error('Passage text must be HTML-escaped in the published file');
      const text = decode(m[2]).replace(/\r\n?/g,'\n');
      if (text.length > LIMITS.passage) throw Error('Passage exceeds 60,000 characters: ' + a.name);
      const p = {name:a.name, pid:a.pid, tags:(a.tags || '').split(/\s+/).filter(Boolean), text};
      passages.set(p.name,p); ids.set(p.pid,p.name);
      remainder = remainder.replace(m[0], '');
    }
    // Story JavaScript and init/widget hooks can affect every reachable passage.
    let globalBarrier = false;
    remainder = remainder.replace(/<(script|style)\b([^>]*)>([\s\S]*?)<\/\1\s*>/gi, (all,tag,a,content) => {
      if (content.trim()) {
        const script = tag.toLowerCase() === 'script';
        unchecked.push({passage:script ? 'Story JavaScript' : 'Story stylesheet', line:1, reason:script ? 'Story JavaScript may change variables or navigation; routes were not analysed.' : 'Story styling may hide passage links; routes were not analysed.'});
        globalBarrier = true;
      }
      return '';
    }).replace(/<tw-tag\b[^>]*>\s*<\/tw-tag\s*>/gi,'');
    if (remainder.trim()) throw Error('Unrecognised or malformed story-data elements');
    const start = ids.get(attrs.startnode);
    if (!start) throw Error('The story needs an explicit startnode matching a passage identifier');
    const special = /^(?:Passage(?:Header|Footer|Ready|Done)|Story(?:Interface|Caption|Menu|Banner|Subtitle|Author|DisplayTitle|Share|Settings|Stylesheet|JavaScript)|Widget)$/;
    for (const p of passages.values()) {
      if (p.tags.some(t => ['init','widget','script'].includes(t)) || special.test(p.name)) {
        unchecked.push({passage:p.name,line:1,reason:'Special passage or init/widget/script hook is unsupported; routes were not analysed.'});
        globalBarrier = true;
      }
    }
    if (start === 'StoryInit') throw Error('StoryInit cannot also be the start passage');
    return {name:attrs.name || 'Untitled story', start, passages, unchecked, globalBarrier};
  }
  function compile(passage) {
    const text = passage.text, tokens = [], notes = [], names = [];
    let i = 0;
    const lineAt = offset => text.slice(0,offset).split('\n').length;
    function add(type, value, at = i) {
      tokens.push({type,value,line:lineAt(at)});
      if (tokens.length > LIMITS.tokens) throw Error('Passage token limit exceeded');
    }
    function unsupported(reason, at = i) {
      notes.push({passage:passage.name,line:lineAt(at),reason}); add('blocked',reason,at);
    }
    function ast(source, line) {
      const value = E.parse(source);
      names.push(...E.variables(value).map(name => ({name,passage:passage.name,line})));
      return value;
    }
    while (i < text.length) {
      const rest = text.slice(i); let m;
      const masks = [['"""','"""'],['{{{','}}}'],['<nowiki>','</nowiki>'],['/%','%/'],['/*','*/'],['<!--','-->']];
      const mask = masks.find(([open]) => rest.startsWith(open));
      if (mask) {
        const end = text.indexOf(mask[1],i + mask[0].length);
        if (end < 0) { unsupported('Unclosed literal or comment'); break; }
        i = end + mask[1].length; continue;
      }
      if (rest.startsWith('$$')) { i += 2; continue; }
      if (rest.startsWith('<<')) {
        // Find >> outside quoted strings (e.g. <<set $message to ">>">>).
        let j = i + 2, quote = null;
        for (; j < text.length; j++) {
          const c = text[j];
          if (quote) { if (c === '\\') j++; else if (c === quote) quote = null; }
          else if (c === '"' || c === "'") quote = c;
          else if (text.startsWith('>>',j)) break;
        }
        if (j === text.length) { unsupported('Unclosed macro'); break; }
        const raw = text.slice(i+2,j), body = raw.trim(), at = i, line = lineAt(i);
        if (/^\s/.test(raw)) { unsupported('Whitespace before the macro name is unchecked',at); i = j + 2; continue; }
        // Match macro names separately; punctuation print forms have no word boundary.
        const head = /^(\/if|[A-Za-z]+|[=-])(?=\s|$)/.exec(body);
        const kind = head?.[1], arg = head ? body.slice(head[0].length).trim() : '';
        try {
          if (kind === 'set') {
            const assignment = /^((?:\$|_)[A-Za-z_$][A-Za-z0-9_$]*)\s*(?:=(?!=)|\bto\b)\s*([\s\S]+)$/.exec(arg);
            if (!assignment) throw Error('Only one simple-variable assignment per set macro is supported');
            const name = assignment[1], value = ast(assignment[2],line);
            names.push({name,passage:passage.name,line}); add('set',{name,value},at);
          } else if (kind === 'if' || kind === 'elseif') add(kind,ast(arg,line),at);
          else if (['else','endif','/if'].includes(kind) && !arg) add(kind === '/if' ? 'endif' : kind,null,at);
          else if (['print','=','-'].includes(kind)) add('read',ast(arg,line),at);
          else unsupported('Unsupported macro: <<' + body.slice(0,70) + '>>',at);
        } catch (error) { unsupported(error.message,at); }
        i = j + 2; continue;
      }
      if (text[i] === '|' && (i === 0 || text[i-1] === '\n')) { unsupported('Table markup and its styling are unchecked'); break; }
      if (/^\?[A-Za-z_$]/.test(rest)) { unsupported('Template expansion is unchecked'); break; }
      if (/^(?:https?|ftp|mailto):/i.test(rest)) { unsupported('Automatic external link markup is unchecked'); break; }
      if (rest.startsWith('[[')) {
        const end = text.indexOf(']]',i+2);
        if (end < 0) { unsupported('Unclosed passage link'); break; }
        const body = text.slice(i+2,end), parts = body.split(/\||->|<-/);
        let target = parts.length === 1 ? parts[0] : body.includes('<-') ? parts[0] : parts[1];
        if (parts.length > 2 || /[\[\]$<>"'`]|(?:^|\W)_[A-Za-z]/.test(parts.join('')) || /^[a-z][a-z0-9+.-]*:/i.test(target)) {
          unsupported('Dynamic, setter, external or expression link is unchecked');
        } else add('link',target.trim());
        i = end+2; continue;
      }
      if (text[i] === '<' || text[i] === '\\' || rest.startsWith('@@') || rest.startsWith('[img[')) {
        unsupported('HTML, escape, image or custom markup is unchecked'); break;
      }
      if ((m = /^(?:\$|_)[A-Za-z_$][A-Za-z0-9_$]*/.exec(rest))) {
        if (/^(?:\.[A-Za-z_$]|\[|\()/.test(text.slice(i+m[0].length))) unsupported('Property, index or method access is unchecked');
        else { const line = lineAt(i); names.push({name:m[0],passage:passage.name,line}); add('read',{type:'var',value:m[0]}); }
        i += m[0].length; continue;
      }
      i++;
    }
    let pos = 0;
    function block(depth) {
      if (depth > LIMITS.nesting) throw Error('Conditional nesting limit exceeded');
      const nodes = [];
      while (pos < tokens.length && !['elseif','else','endif'].includes(tokens[pos].type)) {
        const t = tokens[pos++];
        if (t.type !== 'if') { nodes.push(t); continue; }
        const branches = [{condition:t.value,line:t.line,nodes:block(depth+1)}];
        while (tokens[pos]?.type === 'elseif') {
          const b = tokens[pos++]; branches.push({condition:b.value,line:b.line,nodes:block(depth+1)});
        }
        if (tokens[pos]?.type === 'else') {
          const b = tokens[pos++]; branches.push({condition:null,line:b.line,nodes:block(depth+1)});
        }
        if (tokens[pos++]?.type !== 'endif') throw Error('Missing or misplaced closing if');
        nodes.push({type:'if',branches,line:t.line});
      }
      return nodes;
    }
    try {
      const nodes = block(0);
      if (pos !== tokens.length) throw Error('Unexpected else, elseif or endif');
      return {...passage,nodes,notes,names};
    } catch (error) {
      return {...passage,nodes:[{type:'blocked',value:error.message,line:1}],notes:[...notes,{passage:passage.name,line:1,reason:error.message}],names};
    }
  }
  const api = {extract,compile,LIMITS};
  if (typeof module !== 'undefined') module.exports = api;
  root.TwineStory = api;
})(globalThis);
