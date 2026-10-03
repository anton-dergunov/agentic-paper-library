// A paper library on disk: its config, its papers and the files of each paper.
// No `vscode` import, so that the tests run under plain Node.

import { existsSync, promises as fs, readFileSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import * as path from 'node:path';
import { parse } from 'yaml';

export const CONFIG_NAME = 'paper-library.yaml';

/** Where a library keeps its trees, resolved as the engine's paperlib.py does. */
export interface LibraryConfig {
  root: string;
  libraryDir: string;
  pdfRoot: string;
  /** The symlink to pdfRoot inside the library, when `pdf_link:` names one. */
  pdfLink?: string;
  notesDir: string;
}

export interface Paper {
  title: string;
  /** Folder under the library, e.g. `llm/memory/agent`. */
  topic: string;
  /** Filename without extension, shared by the markdown, the PDF and the notes. */
  stem: string;
  year: string;
  summary: string;
  mdPath: string;
  pdfPath: string;
  notesPath?: string;
}

export type FileKind = 'markdown' | 'pdf' | 'notes';

/** Relative paths are taken from the library root and `~` is expanded; environment variables override. */
export function loadConfig(root: string, env: NodeJS.ProcessEnv = process.env): LibraryConfig {
  const raw = (parse(readFileSync(path.join(root, CONFIG_NAME), 'utf8')) ?? {}) as Record<string, unknown>;
  const resolve = (value: unknown) => {
    const text = String(value);
    const expanded = text === '~' || text.startsWith('~/') ? path.join(homedir(), text.slice(1)) : text;
    return path.resolve(root, expanded);
  };
  return {
    root,
    libraryDir: env.LIBRARY_DIR || resolve(raw.library ?? 'library'),
    pdfRoot: env.PDF_ROOT || resolve(raw.pdf_root ?? 'pdfs'),
    pdfLink: raw.pdf_link ? resolve(raw.pdf_link) : undefined,
    notesDir: resolve(raw.notes ?? 'notes'),
  };
}

export class Library {
  private readonly byKey = new Map<string, Paper>();
  private readonly byStem = new Map<string, Paper>();
  /** Each tree's folder, also under its real path: the PDF viewer may hold a PDF by either. */
  private readonly roots: [FileKind, string][];

  constructor(readonly config: LibraryConfig, readonly papers: Paper[]) {
    for (const paper of papers) {
      this.byKey.set(`${paper.topic}/${paper.stem}`, paper);
      this.byStem.set(paper.stem, paper);
    }
    const pdfFolders = [config.pdfLink, config.pdfRoot].filter((dir): dir is string => !!dir);
    this.roots = [
      ...withRealPaths(config.notesDir).map((dir): [FileKind, string] => ['notes', dir]),
      ...withRealPaths(config.libraryDir).map((dir): [FileKind, string] => ['markdown', dir]),
      ...pdfFolders.flatMap(withRealPaths).map((dir): [FileKind, string] => ['pdf', dir]),
    ];
  }

  /** The paper a markdown copy, PDF or notes file belongs to, and which of the three it is. */
  paperForFile(file: string): { paper: Paper; kind: FileKind } | undefined {
    const ext = path.extname(file).toLowerCase();
    for (const [kind, dir] of this.roots) {
      const rel = path.relative(dir, file);
      if (!rel || rel.startsWith('..') || path.isAbsolute(rel)) continue;
      if (ext !== (kind === 'pdf' ? '.pdf' : '.md')) return undefined;
      const key = rel.slice(0, -ext.length).split(path.sep).join('/');
      const paper = kind === 'notes' ? this.byStem.get(key) : this.byKey.get(key);
      return paper && { paper, kind };
    }
    return undefined;
  }

  /** The generated index of a paper's topic folder. */
  topicIndex(paper: Paper): string {
    return path.join(this.config.libraryDir, paper.topic, 'README.md');
  }
}

/** Reads every paper's frontmatter. About a quarter of a second for 2,000 papers. */
export async function loadLibrary(config: LibraryConfig): Promise<Library> {
  const files = await paperFiles(config.libraryDir);
  const notes = new Set(await fs.readdir(config.notesDir).catch(() => [] as string[]));
  const pdfDir = config.pdfLink ?? config.pdfRoot;
  const papers: Paper[] = [];
  // In batches, to stay well under the open-file limit.
  for (let i = 0; i < files.length; i += 64) {
    const batch = files.slice(i, i + 64);
    const metas = await Promise.all(batch.map(readFrontmatter));
    batch.forEach((file, j) => {
      const meta = metas[j];
      const rel = path.relative(config.libraryDir, file);
      const stem = path.basename(file, '.md');
      const topic = path.dirname(rel).split(path.sep).join('/');
      papers.push({
        title: text(meta.title) || stem,
        topic: topic === '.' ? '' : topic,
        stem,
        year: text(meta.published).slice(0, 4),
        summary: text(meta.summary),
        mdPath: file,
        pdfPath: path.join(pdfDir, rel.slice(0, -'.md'.length) + '.pdf'),
        notesPath: notes.has(`${stem}.md`) ? path.join(config.notesDir, `${stem}.md`) : undefined,
      });
    });
  }
  // Titles that open with a quote or with maths sort by their first word.
  const key = (title: string) => title.replace(/^[^\p{L}\p{N}]+/u, '');
  papers.sort((a, b) => key(a.title).localeCompare(key(b.title), 'en', { sensitivity: 'base' }));
  return new Library(config, papers);
}

/** Every paper's markdown file: not the indexes, nor anything in figure folders or hidden ones. */
async function paperFiles(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const full = path.join(dir, entry.name);
      if (entry.name.startsWith('.')) return [];
      if (entry.isDirectory()) return entry.name === 'images' ? [] : paperFiles(full);
      return entry.name.endsWith('.md') && entry.name !== 'README.md' ? [full] : [];
    }),
  );
  return nested.flat();
}

const FRONTMATTER = /^---\n([\s\S]*?)\n---\n/;

/** The YAML between the leading `---` lines, reading only the start of the file when that suffices. */
export async function readFrontmatter(file: string): Promise<Record<string, unknown>> {
  const handle = await fs.open(file, 'r');
  let head: string;
  try {
    const buffer = Buffer.alloc(16384);
    const { bytesRead } = await handle.read(buffer, 0, buffer.length, 0);
    head = buffer.toString('utf8', 0, bytesRead);
    if (bytesRead === buffer.length && head.startsWith('---\n') && !FRONTMATTER.test(head)) {
      head = await fs.readFile(file, 'utf8');
    }
  } finally {
    await handle.close();
  }
  const match = FRONTMATTER.exec(head);
  if (!match) return {};
  try {
    return (parse(match[1]) ?? {}) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function text(value: unknown): string {
  return value === undefined || value === null ? '' : String(value).trim();
}

function withRealPaths(dir: string): string[] {
  if (!existsSync(dir)) return [dir];
  const real = realpathSync(dir);
  return real === dir ? [dir] : [dir, real];
}
