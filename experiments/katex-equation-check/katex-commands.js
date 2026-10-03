// List every control sequence KaTeX supports, for the converter's math
// normalisation (scripts/katex-commands.txt). A name counts as supported when
// KaTeX renders it, or fails with any error other than "undefined", in one of
// a few calling shapes.
//
//   node katex-commands.js <out.txt>
//
// Run on 30 Sep 2026 as an inline `node -e` snippet that wrote straight to the
// library's scripts/katex-commands.txt; only the output path became an argument.
const fs=require("fs"), katex=require("katex");
const src=fs.readFileSync(require.resolve("katex/dist/katex.js"),"utf8");
const names=new Set([...src.matchAll(/"\\\\([a-zA-Z]+)"/g)].map(m=>m[1]));
const ok=[];
for (const n of names) {
  let good=false;
  for (const t of ["\\"+n, "\\"+n+"{x}", "\\"+n+"{x}{y}", "\\"+n+"{x}{y}{z}", "\\begin{"+n+"}x\\end{"+n+"}", "\\left.\\"+n+"\\right."]) {
    try { katex.renderToString(t,{throwOnError:true,strict:false}); good=true; break; }
    catch(e){ if(!/Undefined control sequence|No such environment/.test(e.message)) { good=true; break; } }
  }
  if (good) ok.push(n);
}
ok.sort();
fs.writeFileSync(process.argv[2], "# Control sequences KaTeX supports (generated from KaTeX "+katex.version+"; see arxiv-html.lua).\n"+ok.join("\n")+"\n");
console.log(names.size, "candidates,", ok.length, "supported");
for (const t of ["rank","textsc","mbox","mathbbm","frac","operatorname","text","color","tag","displaystyle","limits","bigl","boxed","mathcal","lx"]) console.log(t, ok.includes(t));
