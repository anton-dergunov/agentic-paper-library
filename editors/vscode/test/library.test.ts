import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, realpathSync, symlinkSync, writeFileSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import * as path from 'node:path';
import { test } from 'node:test';
import { loadConfig, loadLibrary } from '../src/library';

// `npm test` runs in editors/vscode.
const EXAMPLE = path.resolve('../../examples/library');

test('the example library: config and papers', async () => {
  const config = loadConfig(EXAMPLE, {});
  assert.equal(config.libraryDir, path.join(EXAMPLE, 'library'));
  assert.equal(config.pdfRoot, path.join(EXAMPLE, 'pdfs'));
  assert.equal(config.pdfLink, path.join(EXAMPLE, 'pdfs'));
  assert.equal(config.notesDir, path.join(EXAMPLE, 'notes'));

  const library = await loadLibrary(config);
  assert.deepEqual(
    library.papers.map((p) => p.title),
    [
      'Direct Preference Optimization: Your Language Model is Secretly a Reward Model',
      'Larimar: Large Language Models with Episodic Memory Control',
      'Why Momentum Really Works',
    ],
  );
  const larimar = library.papers[1];
  assert.equal(larimar.topic, 'llm/memory/parametric');
  assert.equal(larimar.stem, 'Larimar. Large Language Models with Episodic Memory Control');
  assert.equal(larimar.year, '2024');
  assert.match(larimar.summary, /episodic memory/);
  assert.equal(larimar.pdfPath, path.join(EXAMPLE, 'pdfs', larimar.topic, `${larimar.stem}.pdf`));
  assert.equal(library.topicIndex(larimar), path.join(EXAMPLE, 'library', larimar.topic, 'README.md'));
});

test('environment variables override the config, ~ is expanded', () => {
  const root = mkdtempSync(path.join(tmpdir(), 'paper-library-'));
  writeFileSync(path.join(root, 'paper-library.yaml'), 'pdf_root: ~/Papers\nnotes: memory\n');
  const config = loadConfig(root, { LIBRARY_DIR: '/elsewhere/library' });
  assert.equal(config.libraryDir, '/elsewhere/library');
  assert.equal(config.pdfRoot, path.join(homedir(), 'Papers'));
  assert.equal(config.pdfLink, undefined);
  assert.equal(config.notesDir, path.join(root, 'memory'));
  assert.equal(loadConfig(root, { PDF_ROOT: '/mnt/pdfs' }).pdfRoot, '/mnt/pdfs');
});

/** A library whose PDF root lives outside it, linked in as pdf/, the way `paperlib init` sets it up. */
async function linkedLibrary() {
  const base = realpathSync(mkdtempSync(path.join(tmpdir(), 'paper-library-')));
  const root = path.join(base, 'papers');
  const pdfRoot = path.join(base, 'Synced', 'Papers');
  const topic = path.join(root, 'library', 'llm', 'memory');
  mkdirSync(path.join(topic, 'images', 'A-MEM. Agentic Memory'), { recursive: true });
  mkdirSync(path.join(pdfRoot, 'llm', 'memory'), { recursive: true });
  mkdirSync(path.join(root, 'notes'));
  symlinkSync(pdfRoot, path.join(root, 'pdf'));
  writeFileSync(
    path.join(root, 'paper-library.yaml'),
    `reader: the reader\npdf_root: ${pdfRoot}\npdf_link: pdf\n`,
  );
  writeFileSync(
    path.join(topic, 'A-MEM. Agentic Memory.md'),
    `---\ntitle: 'A-MEM: Agentic Memory'\nauthors: [${'Some Author, '.repeat(2000)}Last Author]\n` +
      `published: 2025-02-17\nsummary: Zettelkasten-style memory for agents.\n---\n\n# A-MEM\n`,
  );
  writeFileSync(path.join(topic, 'No Frontmatter.md'), '# Just a body\n');
  writeFileSync(path.join(topic, 'README.md'), '# llm/memory\n');
  writeFileSync(path.join(topic, 'images', 'A-MEM. Agentic Memory', 'x.md'), 'not a paper\n');
  writeFileSync(path.join(pdfRoot, 'llm', 'memory', 'A-MEM. Agentic Memory.pdf'), '%PDF-1.7\n');
  writeFileSync(path.join(root, 'notes', 'A-MEM. Agentic Memory.md'), '# A-MEM\n');
  return { root, pdfRoot, library: await loadLibrary(loadConfig(root, {})) };
}

test('papers: long frontmatter, no frontmatter, indexes and figures skipped, notes found', async () => {
  const { root, library } = await linkedLibrary();
  assert.deepEqual(
    library.papers.map((p) => p.title),
    ['A-MEM: Agentic Memory', 'No Frontmatter'],
  );
  const [amem, bare] = library.papers;
  assert.equal(amem.summary, 'Zettelkasten-style memory for agents.');
  assert.equal(amem.year, '2025');
  assert.equal(amem.pdfPath, path.join(root, 'pdf', 'llm', 'memory', 'A-MEM. Agentic Memory.pdf'));
  assert.equal(amem.notesPath, path.join(root, 'notes', 'A-MEM. Agentic Memory.md'));
  assert.equal(bare.summary, '');
  assert.equal(bare.notesPath, undefined);
});

test('paperForFile: markdown, PDF through the link or the real root, notes', async () => {
  const { root, pdfRoot, library } = await linkedLibrary();
  const stem = 'A-MEM. Agentic Memory';
  const at = (file: string) => {
    const found = library.paperForFile(file);
    return found && [found.paper.stem, found.kind];
  };
  assert.deepEqual(at(path.join(root, 'library', 'llm', 'memory', `${stem}.md`)), [stem, 'markdown']);
  assert.deepEqual(at(path.join(root, 'pdf', 'llm', 'memory', `${stem}.pdf`)), [stem, 'pdf']);
  assert.deepEqual(at(path.join(pdfRoot, 'llm', 'memory', `${stem}.pdf`)), [stem, 'pdf']);
  assert.deepEqual(at(path.join(root, 'notes', `${stem}.md`)), [stem, 'notes']);
  assert.equal(at(path.join(root, 'library', 'llm', 'memory', 'README.md')), undefined);
  assert.equal(at(path.join(root, 'library', 'llm', `${stem}.md`)), undefined);
  assert.equal(at(path.join(root, 'AGENTS.md')), undefined);
});
