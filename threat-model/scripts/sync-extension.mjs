import { copyFileSync } from "node:fs";

copyFileSync("index.html", "extension/media/index.html");
console.log("Synchronized index.html to extension/media/index.html");
