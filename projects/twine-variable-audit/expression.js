/* A deliberately small TwineScript interpreter. Story text is never JavaScript. */
(function (root) {
  'use strict';
  const aliases = {is:'===', isnot:'!==', eq:'==', neq:'!=', gt:'>', gte:'>=', lt:'<', lte:'<=', and:'&&', or:'||', not:'!'};
  const precedence = {'||':1, '&&':2, '===':3, '!==':3, '==':3, '!=':3, '>':4, '<':4, '>=':4, '<=':4, '+':5, '-':5, '*':6, '/':6, '%':6};
  function parse(source) {
    const tokens = []; let i = 0;
    while (i < source.length) {
      if (/\s/.test(source[i])) { i++; continue; }
      const rest = source.slice(i); let m;
      if ((m = /^(?:\$|_)[A-Za-z_$][A-Za-z0-9_$]*/.exec(rest))) tokens.push({type:'var', value:m[0]});
      else if ((m = /^(?:\d+(?:\.\d*)?|\.\d+)/.exec(rest))) tokens.push({type:'literal', value:Number(m[0])});
      else if (rest[0] === '"' || rest[0] === "'") {
        const quote = source[i++]; let value = '', closed = false;
        while (i < source.length) {
          let c = source[i++];
          if (c === quote) { closed = true; break; }
          if (c === '\n' || c === '\r') throw Error('Unescaped newline in string');
          if (c === '\\') {
            c = source[i++];
            const escapes = {n:'\n', r:'\r', t:'\t', '\\':'\\', '"':'"', "'":"'"};
            if (!Object.hasOwn(escapes, c)) throw Error('Unsupported string escape');
            c = escapes[c];
          }
          value += c;
        }
        if (!closed) throw Error('Unclosed string');
        tokens.push({type:'literal', value}); continue;
      } else if (rest.startsWith('++') || rest.startsWith('--')) {
        throw Error('Variable increment/decrement is unchecked');
      } else if ((m = /^(===|!==|==|!=|>=|<=|&&|\|\||[()+*/%!<>-])/.exec(rest))) tokens.push({type:'op', value:m[0]});
      else if ((m = /^[A-Za-z]+/.exec(rest))) {
        const word = m[0];
        if (Object.hasOwn(aliases, word)) tokens.push({type:'op', value:aliases[word], raw:word});
        else if (word === 'def' || word === 'ndef') {
          // SugarCube 2.37.3 substitutes these tokens without parentheses. Keeping
          // the comparison here lets the normal precedence parser group it;
          // treating def as one unary atom changes mixed conditions' meaning.
          tokens.push({type:'literal', value:'undefined'}, {type:'op', value:word === 'def' ? '!==' : '==='}, {type:'guard', value:'typeof'});
        } else if (word === 'typeof') tokens.push({type:'guard', value:word});
        else if (['true','false','null','undefined'].includes(word)) tokens.push({type:'literal', value:({true:true,false:false,null:null,undefined:undefined})[word]});
        else throw Error('Unsupported expression word: ' + word);
      } else throw Error('Unsupported expression near ' + rest.slice(0, 30));
      i += m[0].length;
      if (tokens.length > 256) throw Error('Expression is too long');
    }
    if (tokens.some((t,i) => t.raw === 'is' && tokens[i+1]?.raw === 'not')) throw Error('The ambiguous legacy is not operator is unchecked');
    let pos = 0;
    function atom() {
      const t = tokens[pos++]; if (!t) throw Error('Missing expression');
      if (t.type === 'literal' || t.type === 'var') return t;
      if (t.type === 'guard') {
        const v = tokens[pos++];
        if (!v || v.type !== 'var') throw Error(t.value + ' requires a simple variable');
        return {type:'guard', value:t.value, variable:v.value};
      }
      if (['!','-','+'].includes(t.value)) return {type:'unary', op:t.value, arg:atom()};
      if (t.value === '(') {
        const value = expr(1);
        if (tokens[pos++]?.value !== ')') throw Error('Missing closing parenthesis');
        return value;
      }
      throw Error('Unexpected operator');
    }
    function expr(min) {
      let left = atom();
      while ((precedence[tokens[pos]?.value] || 0) >= min) {
        const op = tokens[pos++].value;
        left = {type:'binary', op, left, right:expr(precedence[op] + 1)};
      }
      return left;
    }
    const ast = expr(1);
    if (pos !== tokens.length) throw Error('Unsupported expression suffix');
    return ast;
  }
  function evaluate(ast, env, read) {
    if (ast.type === 'literal') return ast.value;
    if (ast.type === 'var') { read(ast.value); return env[ast.value]; }
    if (ast.type === 'guard') return typeof env[ast.variable];
    if (ast.type === 'unary') {
      const x = evaluate(ast.arg, env, read);
      return ast.op === '!' ? !x : ast.op === '-' ? -x : +x;
    }
    // Equality with undefined (and loose equality with null) is a deliberate guard.
    const guard = ['===','!==','==','!='].includes(ast.op) && [ast.left,ast.right].some(n => n.type === 'literal' && (n.value === undefined || (n.value === null && ['==','!='].includes(ast.op))));
    const operand = n => guard && n.type === 'var' ? env[n.value] : evaluate(n, env, read);
    const a = operand(ast.left);
    if (ast.op === '&&') return a && evaluate(ast.right, env, read);
    if (ast.op === '||') return a || evaluate(ast.right, env, read);
    const b = operand(ast.right);
    switch (ast.op) {
      case '===': return a === b;
      case '!==': return a !== b;
      case '==': return a == b; // SugarCube eq is the JavaScript loose-equality operator.
      case '!=': return a != b;
      case '>': return a > b;
      case '<': return a < b;
      case '>=': return a >= b;
      case '<=': return a <= b;
      case '+': return a + b;
      case '-': return a - b;
      case '*': return a * b;
      case '/': return a / b;
      case '%': return a % b;
      default: throw Error('Unsupported operator');
    }
  }
  function variables(ast) {
    if (ast.type === 'var') return [ast.value];
    if (ast.type === 'guard') return [ast.variable];
    return ['arg','left','right'].flatMap(k => ast[k] ? variables(ast[k]) : []);
  }
  const api = {parse, evaluate, variables};
  if (typeof module !== 'undefined') module.exports = api;
  root.TwineExpression = api;
})(globalThis);
