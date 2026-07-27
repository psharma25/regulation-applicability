import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";

const fail = message => {
  console.error(`Validation failed: ${message}`);
  process.exitCode = 1;
};
const text = path => readFileSync(path, "utf8");
const hash = path => createHash("sha256").update(readFileSync(path)).digest("hex");

const html = text("index.html");
if (!html.toLowerCase().includes("<!doctype html>")) fail("index.html has no HTML doctype");
if (!html.includes("<title>ThreatForge")) fail("index.html has an unexpected title");
if (!html.includes("localStorage")) fail("browser persistence code is missing");
if (hash("index.html") !== hash("extension/media/index.html")) {
  fail("extension/media/index.html is stale; run npm run sync:extension");
}

for (const path of ["package.json", "extension/package.json"]) {
  try { JSON.parse(text(path)); } catch (error) { fail(`${path} is invalid JSON: ${error.message}`); }
}
try { execFileSync(process.execPath, ["--check", "extension/extension.js"], { stdio: "pipe" }); }
catch (error) { fail(`extension/extension.js has invalid JavaScript: ${error.stderr?.toString() || error.message}`); }

const walk = dir => readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
  const path = `${dir}/${entry.name}`;
  return entry.isDirectory() ? walk(path) : [path];
});
const nestedArchives = walk(".").filter(path => path.endsWith(".zip"));
if (nestedArchives.length) fail(`release source contains nested ZIP files: ${nestedArchives.join(", ")}`);

if (!process.exitCode) console.log("ThreatForge web app and VS Code extension validated.");
