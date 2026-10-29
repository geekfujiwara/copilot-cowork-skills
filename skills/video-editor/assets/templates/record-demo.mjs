// Copy into an approved working folder with the accompanying package manifest.
import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { createInterface } from 'node:readline/promises';
import { performance } from 'node:perf_hooks';
import path from 'node:path';

const [url, destination] = process.argv.slice(2);
if (!url || !destination || !['http:', 'https:'].includes(new URL(url).protocol)) {
  throw new Error('Usage: node record-demo.mjs <approved-http-or-https-url> <new-output-folder>');
}
if (!process.stdin.isTTY) {
  throw new Error('Manual recording needs an interactive terminal. For automation, replace the prompt with verified app-specific actions.');
}
const output = path.resolve(destination);
await mkdir(output, { recursive: false });
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
  recordVideo: { dir: path.join(output, 'takes'), size: { width: 1920, height: 1080 } },
});
const actions = [];
const started = performance.now();
await context.exposeBinding('recordDemoClick', (_source, event) => {
  if (actions.length >= 10000) throw new Error('Click log limit exceeded.');
  actions.push({ time: (performance.now() - started) / 1000, x: event.x, y: event.y });
});
await context.addInitScript(() => {
  if (window !== window.top) return;
  document.addEventListener('click', event => {
    void window.recordDemoClick({ x: event.clientX, y: event.clientY });
  });
});
const page = await context.newPage();
const video = page.video();
const terminal = createInterface({ input: process.stdin, output: process.stdout });
try {
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await terminal.question('Record the approved fictional workflow. Press Enter here to finish. ');
} finally {
  terminal.close();
  await writeFile(path.join(output, 'actions.json'), JSON.stringify(actions, null, 2));
  await context.close();
  await video.saveAs(path.join(output, 'raw.webm'));
  await browser.close();
}
