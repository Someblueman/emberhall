// Uses already-installed puppeteer-core; installs nothing and visits only this fixture.
const {mkdtemp, readFile, readdir} = require('node:fs/promises');
const {tmpdir} = require('node:os');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const puppeteer = require('puppeteer-core');

async function main() {
  const root = await mkdtemp(path.join(tmpdir(), 'emberhall-browser-probe-'));
  const headless = !process.argv.includes('--headful');
  const options = {
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    userDataDir: path.join(root, 'profile'),
    // Keep Chrome's normal security settings; do not use automation defaults.
    ignoreDefaultArgs: true,
    headless,
    timeout: 10000,
    args: ['--no-first-run', '--no-default-browser-check',
      '--disable-background-networking', '--disable-component-update', '--disable-sync',
      '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0',
      `--user-data-dir=${path.join(root, 'profile')}`,
      ...(headless ? ['--headless=new'] : []), 'about:blank'],
  };
  const result = {
    headless, profile: '<isolated temporary profile>',
    fixture: 'fixture.html',
    puppeteer: require('puppeteer-core/package.json').version,
    launch_args: options.args.map(arg => arg.startsWith('--user-data-dir=')
      ? '--user-data-dir=<isolated temporary profile>' : arg),
    stage: 'launch',
  };
  let browser;
  try {
    browser = await puppeteer.launch(options);
    const page = await browser.newPage();
    const client = await page.createCDPSession();
    await client.send('Browser.setDownloadBehavior', {behavior: 'allow', downloadPath: root});
    result.stage = 'local-page';
    await page.goto(pathToFileURL(path.join(__dirname, 'fixture.html')).href);
    result.before = await page.$eval('#status', node => node.textContent);
    await page.click('#increment');
    result.after = await page.$eval('#status', node => node.textContent);
    result.stage = 'download';
    await page.click('#download');
    for (let i = 0; i < 100; i += 1) {
      if ((await readdir(root)).includes('resident-browser.json')) break;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    result.download = JSON.parse(await readFile(path.join(root, 'resident-browser.json'), 'utf8'));
    if (result.before !== 'Count: 0' || result.after !== 'Count: 1'
        || result.download.fixture !== 'resident-browser' || result.download.count !== 1) {
      throw new Error('Browser interaction or downloaded JSON differs from the expected result');
    }
    result.stage = 'complete';
    result.success = true;
  } catch (error) {
    result.success = false;
    result.error = {name: error.name, message: error.message};
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    console.log(JSON.stringify(result, null, 2));
  }
}
main().catch(error => {console.error(error); process.exitCode = 1;});
