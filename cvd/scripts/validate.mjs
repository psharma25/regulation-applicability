import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(new URL("../index.html", import.meta.url), "utf8");
const failures = [];
const requireText = (value, label) => {
  if (!html.includes(value)) failures.push(`Missing ${label}`);
};

requireText("<!DOCTYPE html>", "HTML5 doctype");
requireText('name="viewport"', "responsive viewport");
requireText("Content-Security-Policy", "Content Security Policy");
requireText('name="referrer"', "referrer policy");
requireText('aria-label="Main views"', "main-navigation label");
requireText("cvd.console.v3", "current storage schema");

const inlineScripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map((match) => match[1])
  .filter((source) => source.trim());
for (const [index, source] of inlineScripts.entries()) {
  try {
    new vm.Script(source, { filename: `index.html:inline-script-${index}` });
  } catch (error) {
    failures.push(`JavaScript parse failure: ${error.message}`);
  }
}

const staticIds = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
const duplicateIds = [...new Set(staticIds.filter((id, index) => staticIds.indexOf(id) !== index))];
if (duplicateIds.length) failures.push(`Duplicate static IDs: ${duplicateIds.join(", ")}`);

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log(`Validated index.html: ${inlineScripts.length} inline script block(s), ${staticIds.length} static IDs.`);
