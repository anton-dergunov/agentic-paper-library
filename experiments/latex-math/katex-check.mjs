// Renders every $…$ and $$…$$ in the given files (markdown, or a claude -p JSON reply) with carrel's KaTeX, strict, and reports failures.
//   CARREL=<carrel checkout> node katex-check.mjs <file>…
import fs from 'node:fs';
const katex = (await import(`${process.env.CARREL}/src/carrel/static/vendor/katex/katex.mjs`)).default;
let ok = 0, bad = 0;
for (const f of process.argv.slice(2)) {
  let t = fs.readFileSync(f, 'utf8');
  if (f.endsWith('.json')) t = JSON.parse(t).result;
  t = t.replace(/```[\s\S]*?```/g, '');
  const forms = [];
  t = t.replace(/\$\$([\s\S]+?)\$\$/g, (_, x) => { forms.push([x, true]); return ''; });
  for (const m of t.matchAll(/\$(?![\s$])((?:\\.|[^\\$])+?)(?<![\s\\])\$(?!\d)/g)) forms.push([m[1], false]);
  for (const [tex, display] of forms) {
    try { katex.renderToString(tex, { displayMode: display, throwOnError: true }); ok++; }
    catch (e) { bad++; console.log(`${f.split('/').pop()}: ${e.message.slice(0, 120)}`); }
  }
}
console.log(`${ok} formulas render, ${bad} fail`);
