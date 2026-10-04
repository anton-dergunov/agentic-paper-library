// Render every $...$ / $$...$$ in the library with KaTeX (what VS Code's
// preview uses) and summarise the errors.
//
//   node check.js <folder of paper markdown>
//   LIST=1 ...   also one "FAILFILE <count> <path>" line per failing paper
//   ALL=1 ...    also one "FAIL <path> <kind> <TeX>" line per failure
const fs = require("fs");
const path = require("path");
const katex = require("katex");

const root = process.argv[2];
const macros = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], "utf8")) : {};
const files = [];
(function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p);
    else if (e.name.endsWith(".md") && e.name !== "README.md") files.push(p);
  }
})(root);

let total = 0, failed = 0;
const byKind = {}, examples = {}, perFile = {}, all = [];
for (const f of files) {
  let text = fs.readFileSync(f, "utf8").replace(/```[\s\S]*?```/g, "");
  const items = [];
  text = text.replace(/(?<!\\)\$\$([\s\S]+?)\$\$/g, (_, t) => { items.push([t, true]); return " "; });
  for (const line of text.split("\n")) {
    const re = /(?<![\\$])\$(?!\$)((?:\\.|[^$\\])+?)\$(?!\$)/g;
    let m;
    while ((m = re.exec(line))) items.push([m[1], false]);
  }
  for (let [tex, display] of items) {
    total++;
    // Inside an HTML table pandoc writes "<" and ">" as entities, which the browser decodes.
    tex = tex.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
    try {
      katex.renderToString(tex, { throwOnError: true, displayMode: display, strict: false, macros: { ...macros } });
    } catch (e) {
      failed++;
      let kind = e.message.replace(/^KaTeX parse error: /, "").replace(/ at position \d+:[\s\S]*/, "");
      kind = kind.replace(/Expected 'EOF', got '(.)'.*/, "Expected EOF, got '$1'");
      byKind[kind] = (byKind[kind] || 0) + 1;
      if (!examples[kind]) examples[kind] = [path.basename(f), tex.slice(0, 160)];
      perFile[f] = (perFile[f] || 0) + 1;
      all.push([f, kind, tex]);
    }
  }
}
if (process.env.LIST) { for (const [f, n] of Object.entries(perFile)) console.log("FAILFILE\t" + n + "\t" + f); }
if (process.env.ALL) {
  // Every failure: file, error kind, the TeX.
  for (const [f, kind, tex] of all) console.log("FAIL\t" + f + "\t" + kind + "\t" + JSON.stringify(tex.slice(0, 400)));
}
console.log(`files ${files.length}, math spans ${total}, failed ${failed}`);
for (const [k, n] of Object.entries(byKind).sort((a, b) => b[1] - a[1]).slice(0, 40)) {
  console.log(String(n).padStart(6), k, "  e.g.", JSON.stringify(examples[k]));
}
