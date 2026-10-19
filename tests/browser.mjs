// Prueba real de interfaz con Chrome/Edge y Node >= 22.12, sin dependencias adicionales.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdtemp, readFile, writeFile, mkdir, rm } from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const executable = process.env.BROWSER_PATH || [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"
].find(existsSync);
assert.ok(executable, "Instala Chrome/Edge o define BROWSER_PATH con la ruta al ejecutable.");

async function freePort() {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function until(check, description) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try { if (await check()) return; } catch { /* Esperar al servidor o al render. */ }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Tiempo agotado: ${description}`);
}

const profile = await mkdtemp(path.join(tmpdir(), "cyk-browser-"));
const port = await freePort();
const debugPort = await freePort();
const base = process.env.BASE_URL || `http://127.0.0.1:${port}`;
let server, browser, socket;
let logs = "";
try {
  if (!process.env.BASE_URL) {
    server = spawn(process.env.PYTHON || "python", ["-u", "app.py"], {
      cwd: root, windowsHide: true, env: { ...process.env, PORT: String(port) }
    });
    server.stdout.on("data", (data) => { logs += data; });
    server.stderr.on("data", (data) => { logs += data; });
  }
  await until(async () => (await fetch(base)).ok, "inicio del servidor web");
  browser = spawn(executable, ["--headless=new", `--user-data-dir=${profile}`,
    `--remote-debugging-port=${debugPort}`, "--no-first-run", "--no-default-browser-check",
    "--window-size=1440,1100", "about:blank"], { windowsHide: true, stdio: "ignore" });
  await until(async () => (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).ok,
    "inicio del navegador");
  const targets = await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json();
  const target = targets.find((entry) => entry.type === "page");
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  let id = 0;
  const pending = new Map();
  const errors = [];
  socket.addEventListener("message", ({ data }) => {
    const message = JSON.parse(data);
    if (message.method === "Runtime.exceptionThrown") errors.push(message.params);
    if (pending.has(message.id)) {
      const { resolve, reject, timer } = pending.get(message.id);
      clearTimeout(timer);
      pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    }
  });
  function cdp(method, params = {}) {
    return new Promise((resolve, reject) => {
      const current = ++id;
      const timer = setTimeout(() => { pending.delete(current); reject(new Error(method)); }, 15000);
      pending.set(current, { resolve, reject, timer });
      socket.send(JSON.stringify({ id: current, method, params }));
    });
  }
  async function evaluate(expression) {
    const response = await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
    return response.result.value;
  }
  await cdp("Runtime.enable");
  await cdp("Page.enable");
  await cdp("Emulation.setDeviceMetricsOverride", {
    width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false
  });
  await cdp("Page.navigate", { url: base });
  const ready = () => until(() => evaluate(
    'Boolean(document.querySelector(".boton-principal") && !document.querySelector(".boton-principal").disabled)'
  ), "respuesta y render de React");
  await ready();

  const text = () => evaluate('document.querySelector(".resultados")?.innerText || ""');
  const consoleText = () => evaluate('document.querySelector(".consola-wrapper pre")?.textContent || ""');
  async function click(label) {
    const clicked = await evaluate(`(() => {
      const button = Array.from(document.querySelectorAll("button")).find(b => b.textContent.trim() === ${JSON.stringify(label)});
      if (!button || button.disabled) return false;
      button.click(); return true;
    })()`);
    assert.ok(clicked, `Botón disponible: ${label}`);
  }
  async function fill(selector, value) {
    await evaluate(`(() => {
      const input = document.querySelector(${JSON.stringify(selector)});
      const prototype = input.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(prototype, "value").set.call(input, ${JSON.stringify(value)});
      input.dispatchEvent(new Event("input", { bubbles: true }));
    })()`);
  }
  async function screenshot(name) {
    if (!process.argv.includes("--capturas")) return;
    const metrics = await cdp("Page.getLayoutMetrics");
    const image = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true,
      clip: { x: 0, y: 0, width: 1440, height: Math.ceil(metrics.cssContentSize.height), scale: 1 } });
    const directory = path.join(root, "docs", "screenshots");
    await mkdir(directory, { recursive: true });
    await writeFile(path.join(directory, name), Buffer.from(image.data, "base64"));
  }

  assert.match(await consoleText(), /Pertenece al lenguaje\?: SÍ/);
  assert.match(await text(), /se utiliza sin convertir/);
  assert.ok(await evaluate('document.querySelector(".resultados svg circle") !== null'));
  await screenshot("01_arbol_sintactico_aceptada.png");
  await click("Tabla Dinámica CYK (T[i][j])");
  assert.ok(await evaluate('document.querySelector(".tabla-matriz") !== null'));
  await screenshot("02_tabla_dinamica_cyk.png");
  await click("The cat drinks beer");
  await ready();
  assert.match(await consoleText(), /Pertenece al lenguaje\?: NO/);
  await screenshot("03_frase_rechazada.png");
  await click("Árbol Sintáctico (Parse Tree)");
  await click("The cat drinks the beer");
  await ready();
  assert.match(await consoleText(), /Pertenece al lenguaje\?: SÍ/);
  await screenshot("04_segunda_frase_aceptada.png");
  await click("He cuts meat with a knife");
  await ready();
  assert.match(await consoleText(), /Pertenece al lenguaje\?: NO/);
  await click("He cuts the meat with a knife");
  await ready();
  assert.match(await consoleText(), /Pertenece al lenguaje\?: SÍ/);

  for (const [file, action] of [["1.txt", "se convirtió a CNF"], ["1-cnf.txt", "se utiliza sin convertir"]]) {
    await fill("textarea", await readFile(path.join(root, "ejemplos", file), "utf8"));
    await fill('input[type="text"]', "");
    await click("Solo analizar gramática");
    await ready();
    assert.ok((await text()).includes(action));
    assert.doesNotMatch(await consoleText(), /Resultado CYK/);
    assert.equal(await evaluate('document.querySelector(".resultados svg")'), null);
  }
  await fill("textarea", "sin flecha");
  await click("Solo analizar gramática");
  await ready();
  assert.ok(await evaluate('document.querySelector("[role=alert]") !== null'));
  assert.equal(await evaluate('document.querySelector(".resultados")'), null);
  await fill("textarea", "S -> e");
  await fill('input[type="text"]', "");
  await click("Validar con CYK");
  await ready();
  assert.match(await consoleText(), /Pertenece al lenguaje\?: SÍ/);
  assert.match(await consoleText(), /ε/);
  assert.equal(errors.length, 0, JSON.stringify(errors));
  console.log("OK: frases aceptadas/rechazadas, árbol, tabla, dos modos CNF, errores y cadena vacía.");
} catch (error) {
  console.error(logs);
  throw error;
} finally {
  socket?.close();
  for (const process of [browser, server]) {
    if (process && process.exitCode === null) {
      const exited = new Promise(resolve => process.once("exit", resolve));
      process.kill();
      await exited;
    }
  }
  // Solo se elimina el perfil temporal creado por esta ejecución, fuera del proyecto.
  if (path.dirname(path.resolve(profile)) === path.resolve(tmpdir()) && path.basename(profile).startsWith("cyk-browser-")) {
    await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  }
}
