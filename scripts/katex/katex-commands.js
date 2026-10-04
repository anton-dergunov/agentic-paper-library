// List every control sequence KaTeX supports, for the converter's math
// normalisation (scripts/katex-commands.txt, read by arxiv-html.lua). A name
// counts as supported when KaTeX renders it, or fails with any error other
// than "undefined", in one of a few calling shapes. A name that passes in
// math but not inside \text{...} is marked "math": \times, \pm and \mathbin
// are undefined or refused in a text argument.
//
//   node katex-commands.js <out.txt>
const fs = require("fs"), katex = require("katex");
const src = fs.readFileSync(require.resolve("katex/dist/katex.js"), "utf8");
const names = new Set([...src.matchAll(/"\\\\([a-zA-Z]+)"/g)].map(m => m[1]));

// A macro (\\ne, \\operatorname) fails in text on what it expands to, so any
// "undefined" or "in text mode" error counts, whatever name it reports.
const REFUSED = /Undefined control sequence|No such environment|Can't use function '[^']*' in text mode/;

function supported(shapes) {
  for (const t of shapes) {
    try { katex.renderToString(t, { throwOnError: true, strict: false }); return true; }
    catch (e) { if (!REFUSED.test(e.message)) return true; }
  }
  return false;
}

const lines = [];
let mathOnly = 0;
for (const n of [...names].sort()) {
  const c = "\\" + n;
  const math = [c, c + "{x}", c + "{x}{y}", c + "{x}{y}{z}", "\\begin{" + n + "}x\\end{" + n + "}", "\\left." + c + "\\right."];
  if (!supported(math)) continue;
  const text = [c, c + "{x}", c + "{x}{y}", c + "{x}{y}{z}"].map(t => "\\text{" + t + "}");
  const inText = supported(text);
  mathOnly += !inText;
  lines.push(inText ? n : n + "\tmath");
}
fs.writeFileSync(process.argv[2], "# Control sequences KaTeX supports; \"math\" marks those it refuses in a text argument\n# (generated from KaTeX " + katex.version + " by scripts/katex/katex-commands.js; see arxiv-html.lua).\n" + lines.join("\n") + "\n");
console.log(names.size, "candidates,", lines.length, "supported,", mathOnly, "math only");
