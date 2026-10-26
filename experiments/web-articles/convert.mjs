// The JavaScript candidates on one rendered page:
//
//     node convert.mjs <page.html> <url> <out-dir>
//
// writes <out-dir>/defuddle.md, readability.md, and article.txt (the text of the
// article element as the browser rendered it, the reference for coverage).
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { JSDOM, VirtualConsole } from "jsdom";
import { Defuddle } from "defuddle/node";
import { Readability } from "@mozilla/readability";
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";

const [, , page, url, out] = process.argv;
const html = readFileSync(page, "utf8");
const quiet = new VirtualConsole();  // the page's CSS and scripts are not run; their errors are noise
// The same DOM for every form. No form keeps images: pictures, canvases and inline SVG plots
// go (an SVG inside a MathJax container is maths, and stays). The Distill template's
// citations are empty <d-cite key="a,b"> elements: their keys are written into the text.
const dom = () => {
  const made = new JSDOM(html, { url, virtualConsole: quiet });
  const doc = made.window.document;
  doc.querySelectorAll("img, picture, canvas, video, svg:not(mjx-container svg)").forEach((e) => e.remove());
  doc.querySelectorAll("d-cite[key], dt-cite[key]").forEach((e) =>
    e.replaceWith(doc.createTextNode(` [${e.getAttribute("key").split(",").map((k) => k.trim()).join(", ")}]`)));
  return made;
};

// Defuddle as documented for Node: markdown out, images removed, no fetch fallback.
const defuddled = await Defuddle(dom().window.document, url, { markdown: true, removeImages: true, useAsync: false });
writeFileSync(join(out, "defuddle.md"), defuddled.content);

// Readability + Turndown with GFM tables, as their READMEs set them up; images dropped.
const article = new Readability(dom().window.document).parse();
const turndown = new TurndownService({ headingStyle: "atx", codeBlockStyle: "fenced" });
turndown.use(gfm);
turndown.remove(["script", "style"]);
writeFileSync(join(out, "readability.md"), article ? turndown.turndown(article.content) : "");

// The article as rendered: the element the old converter also started from.
const doc = dom().window.document;
doc.querySelectorAll("script, style, noscript, nav, header, footer").forEach((e) => e.remove());
const body = doc.querySelector("d-article, dt-article, article, main") || doc.body;
writeFileSync(join(out, "article.txt"), body.textContent);
