// What carrel's fallback (page-links.js) would link in answers, without a browser: each answer's
// markdown, its code and its pdf.invalid links taken out, goes through the same matcher.
// The library gives the papers' titles, for the names of other papers that keep a citation plain.
//   node fallback.mjs <carrel> <library> runs <runs dir> [--list]  coverage per run, as count.py
//                                              counts it; --list prints every link it adds
//   node fallback.mjs <carrel> <library> chats <transcripts dir> [since]  every link it adds
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';

const [carrel, library, mode, dir, since = '2026-10-26'] = process.argv.slice(2);
const { findCitations, answerFile, shortName, namesAnother, namesPattern } = await import(join(carrel, 'src/carrel/static/page-links.js'));
const { parsePaperLink } = await import(join(carrel, 'src/carrel/static/links.js'));

// Each paper's PDF (relative to pdf_root, which mirrors the library folder) and title.
const PAPERS = readdirSync(join(library, 'library'), { recursive: true })
  .filter((f) => /\.(txt|md)$/.test(f) && !f.endsWith('README.md'))
  .map((f) => ({
    pdf: f.replace(/\.(txt|md)$/, '.pdf'),
    title: /^title:\s*["']?(.+?)["']?\s*$/m.exec(readFileSync(join(library, 'library', f), 'utf8').slice(0, 2000))?.[1],
  }));

const LINK = /\[((?:[^\[\]\n]|\[[^\]\n]*\])*)\]\((http:\/\/pdf\.invalid[^)\s]*)\)/g;
const CITE = /\b(?:pp?\.|pages?)\s?\d+(?:\s?[–-]\s?\d+)?/gi;
const CODE = /```[\s\S]*?```|`[^`\n]*`/g;
const ASKED = /^\[Reading (?:library\/)?(.+?)\.(?:txt|md)(?:, page \d+)?\]/m;

// The paper each of run.sh's questions names in its context line (kv names none).
const LME = 'llm/memory/benchmarks/LongMemEval. Benchmarking Chat Assistants on Long-Term Interactive Memory';
const ASKED_IN = Object.fromEntries(
  Object.entries({
    'lme-parts': LME,
    'lme-sizes': LME,
    'lme-con': LME,
    completep: "deep-learning/optimizers-and-schedules/Don't be lazy. CompleteP enables compute-efficient deep transformers",
    topics: 'nlp/topic-models/A Survey on Neural Topic Models. Methods, Applications, and Challenges',
    judgebench: 'llm/evaluation/methods/JudgeBench. A Benchmark for Evaluating LLM-based Judges',
  }).map(([id, path]) => [id, `[Reading library/${path}.txt]`]),
);

/** Plain citations in an answer, and how many of them the fallback links, with what it adds. */
function fallback(text, question) {
  const linked = [...text.matchAll(LINK)].map((m) => parsePaperLink(m[2])?.file).filter(Boolean);
  const asked = ASKED.exec(question ?? '')?.[1];
  const file = answerFile(asked ? `${asked}.pdf` : undefined, linked);
  const rest = text.replace(CODE, (m) => ' '.repeat(m.length)).replace(LINK, (m) => '\u0000'.repeat(m.length));
  const plain = [...rest.matchAll(CITE)];
  const own = shortName(PAPERS.find((p) => p.pdf === file)?.title);
  const names = namesPattern([...new Set(PAPERS.filter((p) => p.pdf !== file).map((p) => shortName(p.title)).filter((n) => n && n !== own))]);
  const lineStart = (i) => rest.lastIndexOf('\n', i) + 1;
  const found = file ? findCitations(rest) : [];
  const added = found.filter((c) => !namesAnother(rest.slice(lineStart(c.start), c.start), names));
  const covered = plain.filter((m) => added.some((c) => c.start <= m.index && m.index < c.end)).length;
  const kept = found.filter((c) => !added.includes(c)).map((c) => rest.slice(Math.max(0, c.start - 60), c.end).replace(/\u0000+/g, '[L]').replace(/\s+/g, ' '));
  return { file, kept, plain: plain.length, covered, added: added.map((c) => ({ ...c, context: rest.slice(Math.max(0, c.start - 90), c.end + 10).replace(/\u0000+/g, '[L]').replace(/\s+/g, ' ') })) };
}

function* events(path) {
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    try { yield JSON.parse(line); } catch { /* not JSON */ }
  }
}

if (mode === 'runs') {
  const totals = {};
  for (const run of readdirSync(dir).filter((d) => statSync(join(dir, d)).isDirectory()).sort()) {
    for (const f of readdirSync(join(dir, run)).filter((f) => f.endsWith('.jsonl'))) {
      const texts = [];
      for (const e of events(join(dir, run, f))) {
        if (e.type === 'assistant') for (const b of e.message.content ?? []) if (b.type === 'text') texts.push(b.text);
      }
      const r = fallback(texts.join('\n\n'), ASKED_IN[f.replace('.jsonl', '')]);
      const t = (totals[run] ??= { plain: 0, covered: 0, added: 0, answers: 0 });
      if (process.argv.includes('--list')) for (const k of r.kept) console.log(`${run}\t${f.replace('.jsonl', '')}\tKEPT PLAIN\t${k}`);
      if (process.argv.includes('--list')) for (const c of r.added) console.log(`${run}\t${f.replace('.jsonl', '')}\tp.${c.page}${c.dest ? ' ' + c.dest : ''}\t${c.context}`);
      t.plain += r.plain; t.covered += r.covered; t.added += r.added.length; t.answers += 1;
    }
  }
  console.log('run\tplain\tlinked by the fallback\tlinks added');
  for (const [run, t] of Object.entries(totals)) console.log(`${run}\t${t.plain}\t${t.covered}\t${t.added}`);
} else {
  for (const f of readdirSync(dir).filter((f) => f.endsWith('.jsonl'))) {
    let question = '';
    let texts = [];
    const flush = (ts) => {
      if (!texts.length) return;
      const r = fallback(texts.join('\n\n'), question);
      for (const k of r.kept) console.log(`${ts.slice(0, 10)}\t${f.slice(0, 6)}\tKEPT PLAIN\t${k}`);
      for (const c of r.added) console.log(`${ts.slice(0, 10)}\t${f.slice(0, 6)}\t${basename(r.file).slice(0, 28)}\tp.${c.page}${c.dest ? ' ' + c.dest : ''}\t${c.context}`);
      texts = [];
    };
    let ts = '';
    for (const e of events(join(dir, f))) {
      if (e.timestamp && e.timestamp < since) continue;
      if (e.type === 'user' && typeof e.message?.content === 'string') {
        flush(ts); question = e.message.content; ts = e.timestamp ?? '';
      } else if (e.type === 'assistant') {
        for (const b of e.message.content ?? []) if (b.type === 'text') texts.push(b.text);
      }
    }
    flush(ts);
  }
}
