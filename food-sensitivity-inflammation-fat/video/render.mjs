// 用法：node render.mjs                 渲染完整 MP4（约 5760 帧，4 个页面并行）
//       node render.mjs --keyframes DIR 每个 beat 截一张中段关键帧（PNG）用于检查
//       node render.mjs --shot 12.5 out.png  截取某一时刻
import { createRequire } from 'module';
import { fileURLToPath, pathToFileURL } from 'url';
import path from 'path';
import fs from 'fs';
import { spawnSync } from 'child_process';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SCRATCH = '/tmp/claude-0/-home-user-woork/ca66b357-1bde-5f1c-9a77-413b3c10556a/scratchpad';
const FRAMES = path.join(SCRATCH, 'frames');
const OUT = path.join(SCRATCH, 'GE-发炎机制-团队版.mp4');
const FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
const FPS = 24, WORKERS = 4;
const url = pathToFileURL(path.join(HERE, 'index.html')).href + '?render=1';
const args = process.argv.slice(2);

async function openPage(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(url);
  await page.waitForFunction('window.__ready===true', null, { timeout: 30000 });
  return page;
}

const browser = await chromium.launch();
try {
  if (args[0] === '--keyframes') {
    const dir = args[1]; fs.mkdirSync(dir, { recursive: true });
    const page = await openPage(browser);
    const beats = await page.evaluate('window.__BEATS');
    for (const b of beats) {
      const t = b.start + (b.end - b.start) * (args[2] ? parseFloat(args[2]) : 0.72);
      await page.evaluate(t => window.__seek(t), t);
      await page.screenshot({ path: path.join(dir, `s${b.scene}b${String(b.beat).padStart(2, '0')}.png`) });
    }
    console.log('keyframes:', beats.length);
  } else if (args[0] === '--shot') {
    const page = await openPage(browser);
    await page.evaluate(t => window.__seek(t), parseFloat(args[1]));
    await page.screenshot({ path: args[2] });
  } else {
    fs.rmSync(FRAMES, { recursive: true, force: true }); fs.mkdirSync(FRAMES, { recursive: true });
    const probe = await openPage(browser);
    const dur = await probe.evaluate('window.__DURATION');
    await probe.close();
    const total = Math.round(dur * FPS);
    let next = 0, done = 0;
    const t0 = Date.now();
    const worker = async () => {
      const page = await openPage(browser);
      for (;;) {
        const i = next++; if (i >= total) break;
        await page.evaluate(t => window.__seek(t), i / FPS);
        const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
        fs.writeFileSync(path.join(FRAMES, `f${String(i).padStart(5, '0')}.jpg`), buf);
        if (++done % 240 === 0) console.log(`${done}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    };
    await Promise.all(Array.from({ length: WORKERS }, worker));
    const r = spawnSync(FFMPEG, ['-y', '-framerate', String(FPS), '-i', path.join(FRAMES, 'f%05d.jpg'),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium', '-movflags', '+faststart', OUT], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error('ffmpeg failed');
    fs.rmSync(FRAMES, { recursive: true, force: true });
    console.log('done ->', OUT);
  }
} finally { await browser.close(); }
