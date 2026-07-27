import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";

const root = process.cwd();
const port = Number(process.env.PORT || 8080);
const types = {
  ".html": "text/html; charset=utf-8",
  ".svg": "image/svg+xml",
  ".json": "application/json; charset=utf-8"
};

createServer((req, res) => {
  const pathname = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
  const relative = pathname === "/" ? "index.html" : normalize(pathname).replace(/^(\.\.[/\\])+/, "");
  const file = join(root, relative);
  if (!file.startsWith(root) || !existsSync(file) || !statSync(file).isFile()) {
    res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    res.end("Not found");
    return;
  }
  res.writeHead(200, {
    "content-type": types[extname(file)] || "application/octet-stream",
    "cache-control": extname(file) === ".html" ? "no-cache" : "public, max-age=3600",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer"
  });
  createReadStream(file).pipe(res);
}).listen(port, "127.0.0.1", () => {
  console.log(`ThreatForge running at http://127.0.0.1:${port}`);
});
