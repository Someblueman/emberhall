'use strict';
const fs = require('node:fs');
const path = require('node:path');
const dir = __dirname;
function build() {
  let html = fs.readFileSync(path.join(dir,'page.html'),'utf8');
  for (const name of ['expression','story','audit','ui']) {
    const source = fs.readFileSync(path.join(dir,name + '.js'),'utf8').replace(/<\/script/gi,'<\\/script');
    html = html.replace('/*__' + name.toUpperCase() + '__*/',() => source);
  }
  const examples = Object.fromEntries(['case','branch','clean','unsupported'].map(name => [name,fs.readFileSync(path.join(dir,'fixtures',name + '.html'),'utf8')]));
  const encoded = JSON.stringify(examples).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
  return html.replace('/*__EXAMPLES__*/',() => 'const TWINE_EXAMPLES = ' + encoded + ';');
}
if (require.main === module) fs.writeFileSync(path.join(dir,'index.html'),build());
module.exports = {build};
