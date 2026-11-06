import { constants } from "node:fs";
import { access, copyFile, mkdir, mkdtemp, readFile, rmdir, unlink, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { performance } from "node:perf_hooks";
import { chromium } from "playwright";

const viewport = { width: 1280, height: 720 };

async function requireUnused(path) {
  try {
    await access(path);
  } catch (error) {
    if (error.code === "ENOENT") return;
    throw error;
  }
  throw new Error(`Dosya zaten var: ${path}`);
}

async function capture(directory) {
  const output = resolve(directory);
  await mkdir(output, { recursive: true });
  const videoPath = join(output, "demo.webm");
  const markerPath = join(output, "markers.json");
  await requireUnused(videoPath);
  await requireUnused(markerPath);

  const html = await readFile(new URL("./demo.html", import.meta.url), "utf8");
  const browser = await chromium.launch();
  const markers = [];
  try {
    const staging = await mkdtemp(join(output, ".recording-"));
    const context = await browser.newContext({ viewport, recordVideo: { dir: staging, size: viewport } });
    await context.route(/^https?:\/\//, (route) => route.abort());
    const page = await context.newPage();
    const video = page.video();
    const start = performance.now();

    await page.setContent(html);
    await page.waitForTimeout(900);
    for (const [button, result] of [
      ["Önizlemeyi hazırla", "Önizleme hazır"],
      ["Önizlemeyi onayla", "Kurgu onaylandı"],
    ]) {
      const locator = page.getByRole("button", { name: button, exact: true });
      const box = await locator.boundingBox();
      if (!box) throw new Error(`Düğme görünmüyor: ${button}`);
      const time = performance.now() - start;
      await locator.click();
      await page.getByRole("status").getByText(result, { exact: true }).waitFor();
      markers.push({
        time_seconds: Math.round(time) / 1000,
        label: button,
        target: { x: Math.round(box.x + box.width / 2), y: Math.round(box.y + box.height / 2) },
      });
      await page.waitForTimeout(1250);
    }

    await context.close();
    const stagedVideo = await video.path();
    await copyFile(stagedVideo, videoPath, constants.COPYFILE_EXCL);
    await unlink(stagedVideo);
    await rmdir(staging);
    await writeFile(markerPath, JSON.stringify({ video: "demo.webm", viewport, approximate: true, markers }, null, 2) + "\n", { flag: "wx" });
  } finally {
    await browser.close();
  }
  console.log(videoPath);
  console.log(markerPath);
}

if (process.argv.length !== 3) {
  console.error("Kullanım: node demo-browser/capture.mjs ÇIKTI_KLASÖRÜ");
  process.exitCode = 2;
} else {
  try {
    await capture(process.argv[2]);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
