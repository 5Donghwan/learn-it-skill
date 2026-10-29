#!/usr/bin/env node
// Check an HTML explainer page the way a reader meets it: headless Chrome over the DevTools protocol.
//
//   node page_check.mjs index.html [--out check]
//
// - Renders at desktop width (1280) and true phone width (390, mobile emulation), light and dark.
// - Saves full-page screenshots in slices: <out>/desktop-light-01.png, <out>/phone-light-01.png, ...
//   (dark theme: the top slice only; theme bugs show there).
// - Reports console messages, uncaught exceptions, failed loads, and sideways scroll.
// - Smoke-tests interaction: moves every slider, number input, and select through its range,
//   clicks every button, opens every <details>, and reports the problems this causes.
// - Writes the visible text to <out>/page-text.txt (for ste_check.py).
// A file without <!doctype> is treated as artifact content and rendered inside the artifact skeleton.
// Needs Node 22+ (built-in WebSocket) and Google Chrome or Chromium. Uses a throwaway Chrome profile.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const argv = process.argv.slice(2);
if (!argv.length) {
  console.error("usage: node page_check.mjs index.html [--out check]");
  process.exit(2);
}
const page = resolve(argv[0]);
const outAt = argv.indexOf("--out");
const out = resolve(outAt >= 0 ? argv[outAt + 1] : join(dirname(page), "check"));
mkdirSync(out, { recursive: true });

const chrome = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].find(existsSync);
if (!chrome) { console.error("no Chrome or Chromium found"); process.exit(1); }
if (typeof WebSocket === "undefined") { console.error("needs Node 22+ (built-in WebSocket)"); process.exit(1); }

// Artifact content has no doctype: wrap it in the same skeleton the artifact viewer adds.
let target = page;
const source = readFileSync(page, "utf8");
if (!/^\s*<!doctype/i.test(source)) {
  target = join(out, "_wrapped.html");
  writeFileSync(target, `<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<base href="${pathToFileURL(dirname(page)).href}/">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
${source}
</body></html>`);
}
const url = pathToFileURL(target).href;

const profile = mkdtempSync(join(tmpdir(), "page-check-"));
const proc = spawn(chrome, ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`,
  "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
const cleanup = () => { try { proc.kill(); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };

try {
  const wsUrl = await new Promise((res, rej) => {
    let buf = "";
    const timer = setTimeout(() => rej(new Error("Chrome did not start")), 20000);
    proc.stderr.on("data", (d) => {
      buf += d;
      const m = buf.match(/ws:\/\/\S+/);
      if (m) { clearTimeout(timer); res(m[0]); }
    });
  });

  // A minimal DevTools-protocol client.
  const ws = new WebSocket(wsUrl);
  await new Promise((r) => ws.addEventListener("open", r, { once: true }));
  let seq = 0;
  const pending = new Map();
  const listeners = new Set();
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
    } else if (msg.method) {
      for (const fn of listeners) fn(msg);
    }
  });
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
    const id = ++seq;
    pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params, sessionId }));
  });

  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const cdp = (method, params) => send(method, params, sessionId);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const problems = new Map(); // message -> count
  const note = (text) => problems.set(text, (problems.get(text) || 0) + 1);
  listeners.add((m) => {
    if (m.sessionId !== sessionId) return;
    const p = m.params;
    if (m.method === "Runtime.consoleAPICalled") {
      note(`console.${p.type}: ${p.args.map((a) => a.value ?? a.description ?? "").join(" ")}`);
    } else if (m.method === "Runtime.exceptionThrown") {
      const d = p.exceptionDetails;
      note(`uncaught: ${(d.exception?.description ?? d.text).split("\n")[0]}`);
    } else if (m.method === "Log.entryAdded" && p.entry.level !== "verbose") {
      note(`${p.entry.level}: ${p.entry.text}${p.entry.url ? " " + p.entry.url : ""}`);
    } else if (m.method === "Page.javascriptDialogOpening") {
      note(`dialog: ${p.type}("${p.message}") — artifact viewers never show dialogs`);
      cdp("Page.handleJavaScriptDialog", { accept: true }).catch(() => {});
    }
  });
  await cdp("Page.enable");
  await cdp("Runtime.enable");
  await cdp("Log.enable");

  const evaluate = async (expression) =>
    (await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true })).result.value;

  async function load(width, height, mobile, dark) {
    await cdp("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await cdp("Emulation.setTouchEmulationEnabled", { enabled: mobile });
    await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }] });
    const loaded = new Promise((r) => {
      const fn = (m) => { if (m.sessionId === sessionId && m.method === "Page.loadEventFired") { listeners.delete(fn); r(); } };
      listeners.add(fn);
    });
    await cdp("Page.navigate", { url });
    await Promise.race([loaded, sleep(15000)]);
    await sleep(1500); // web fonts, CDN scripts, entry animations
  }

  const lines = [];
  for (const [name, width, height, mobile] of [["desktop", 1280, 800, false], ["phone", 390, 844, true]]) {
    for (const dark of [false, true]) {
      await load(width, height, mobile, dark);
      const m = await evaluate("({sw: document.documentElement.scrollWidth, iw: innerWidth, sh: document.documentElement.scrollHeight})");
      const tag = `${name}-${dark ? "dark" : "light"}`;
      if (m.sw > m.iw + 1) note(`${tag}: the page scrolls sideways (${m.sw}px of content in a ${m.iw}px window)`);
      const slice = height * 2;
      const last = dark ? Math.min(m.sh, slice) : m.sh; // dark: top slice only
      let n = 0;
      for (let y = 0; y < last; y += slice) {
        const { data } = await cdp("Page.captureScreenshot", {
          format: "png", captureBeyondViewport: true,
          clip: { x: 0, y, width, height: Math.min(slice, m.sh - y), scale: 1 },
        });
        writeFileSync(join(out, `${tag}-${String(++n).padStart(2, "0")}.png`), Buffer.from(data, "base64"));
      }
      lines.push(`${tag}: page is ${m.sh}px tall; ${n} slice${n > 1 ? "s" : ""} of ${slice}px`);
      if (name === "desktop" && !dark) writeFileSync(join(out, "page-text.txt"), await evaluate("document.body.innerText"));
    }
  }

  // Interaction smoke test on the desktop light view.
  await load(1280, 800, false, false);
  const before = new Map(problems);
  const done = await evaluate(`(async () => {
    const fire = (el) => { el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true })); };
    const inputs = [...document.querySelectorAll("input[type=range], input[type=number], select")];
    for (const el of inputs) {
      const keep = el.value;
      const values = el.tagName === "SELECT" ? [...el.options].map((o) => o.value) : [el.min || "0", el.max || "100"];
      for (const v of [...values, keep]) { el.value = v; fire(el); await new Promise((r) => setTimeout(r, 30)); }
    }
    const buttons = [...document.querySelectorAll("button, [role=button]")].filter((b) => !b.disabled && b.type !== "submit");
    for (const b of buttons) { b.click(); await new Promise((r) => setTimeout(r, 30)); }
    const details = [...document.querySelectorAll("details")];
    details.forEach((d) => { d.open = true; });
    await new Promise((r) => setTimeout(r, 500));
    return { inputs: inputs.length, buttons: buttons.length, details: details.length };
  })()`);
  const fresh = [...problems.keys()].filter((k) => problems.get(k) !== before.get(k));
  lines.push(`interaction: moved ${done.inputs} inputs, clicked ${done.buttons} buttons, opened ${done.details} <details>; ${fresh.length} new problem(s)`);

  console.log(`checked ${page}`);
  for (const l of lines) console.log("  " + l);
  console.log(problems.size ? "problems:" : "problems: none");
  for (const [text, count] of problems) console.log(`  ${count > 1 ? `(x${count}) ` : ""}${text}`);
  console.log(`screenshots and page-text.txt: ${out}`);
  ws.close();
} finally {
  cleanup();
}
