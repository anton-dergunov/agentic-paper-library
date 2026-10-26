// A web article's page, as headless Chrome rendered it, to markdown:
//
//     node to-markdown.mjs <page.html> <url>     (markdown on stdout)
//
// Defuddle extracts the article and writes it as markdown, with maths as TeX and footnotes
// as footnotes (experiments/web-articles). Before it runs, pictures, canvases, inline SVG
// plots and interactive figures are removed (the agent's copy keeps no images; an SVG
// inside a MathJax container is maths and stays), and the Distill template's empty
// <d-cite key="a,b"> citations get their keys written into the text. Links inside headings
// become their text: Defuddle drops a heading's links as permalinks, and transformer-circuits
// puts the section's title in one ("§ 2 [Building …](#building)" came out as "§ 2").
// Defuddle is developed against jsdom 24; on later versions its selectors fail.
//
// A warning goes to stderr when the markdown has fewer than three quarters of the words in
// the article's prose (its paragraphs, list items, headings and captions): Defuddle stopped
// at an attribution-graph widget of transformer-circuits.pub (`.cg-div`, now removed) and
// silently kept half of them. A whole article's markdown has more words than its prose
// (maths, footnote links): 1.6–1.9 times on transformer-circuits.pub.
import { readFileSync } from "node:fs";
import { JSDOM, VirtualConsole } from "jsdom";
import { Defuddle } from "defuddle/node";

const [, , page, url] = process.argv;
const dom = new JSDOM(readFileSync(page, "utf8"), { url, virtualConsole: new VirtualConsole() });
const doc = dom.window.document;
// .cg-div: transformer-circuits.pub's interactive attribution graphs.
doc.querySelectorAll("img, picture, canvas, video, svg:not(mjx-container svg), .cg-div").forEach((e) => e.remove());
doc.querySelectorAll("h1 a, h2 a, h3 a, h4 a, h5 a, h6 a").forEach((a) => a.replaceWith(...a.childNodes));
doc.querySelectorAll("d-cite[key], dt-cite[key]").forEach((e) =>
  e.replaceWith(doc.createTextNode(` [${e.getAttribute("key").split(",").map((k) => k.trim()).join(", ")}]`)));
const words = (text) => (text.match(/[\p{L}\p{N}]+/gu) || []).length;
const article = doc.querySelector("d-article, dt-article, article, main") || doc.body;
const prose = [...article.querySelectorAll("p, h1, h2, h3, h4, h5, h6, li, blockquote, figcaption, pre")]
  .filter((e) => !e.parentElement.closest("p, li, blockquote, figcaption, pre, script, style, noscript"));
const expected = prose.reduce((n, e) => n + words(e.textContent), 0);
const result = await Defuddle(doc, url, { markdown: true, removeImages: true, useAsync: false });
const got = words(result.content);
if (got < expected * 0.75) {
  process.stderr.write(`warning: the markdown has ${got} words, the article's prose ${expected}: some of it may be missing; compare it with ${url}\n`);
}
process.stdout.write(result.content);
