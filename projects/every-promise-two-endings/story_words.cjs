// Count distinct reachable prose paragraphs once, including authored alternatives.
// Exclude headings, choices, UI and the earlier italic chapter-navigation notices.
function countStory({fresh, view, step}) {
  const queue = [fresh()], seen = new Set(), paragraphs = new Set();
  while (queue.length) {
    const state = queue.pop();
    const key = JSON.stringify({...state, heard: [...state.heard].sort()});
    if (seen.has(key)) continue;
    seen.add(key);
    const page = view(state);
    for (const block of page.prose) {
      if (block.startsWith('<em>')) continue;
      // Separate quoted promise paragraphs before deduplication too.
      for (const paragraph of block.split(/<\/?p>/)) {
        const prose = paragraph.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
        if (prose) paragraphs.add(prose);
      }
    }
    for (const action of page.choices) queue.push(step(state, action.id));
  }
  const words = [...paragraphs].reduce((n, p) =>
    n + (p.match(/[\p{L}\p{N}]+(?:['’\-][\p{L}\p{N}]+)*/gu) || []).length, 0);
  return {words, paragraphs: paragraphs.size, states: seen.size};
}
module.exports = countStory;
if (require.main === module) {
  const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
  const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
  const sandbox = {module: {exports: {}}};
  vm.runInNewContext(html.match(/<script id="chapter">([\s\S]*?)<\/script>/)[1], sandbox);
  console.log(JSON.stringify(countStory(sandbox.module.exports)));
}
