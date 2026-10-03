import { existsSync } from 'node:fs';
import * as path from 'node:path';
import * as vscode from 'vscode';
import { CONFIG_NAME, Library, LibraryConfig, Paper, loadConfig, loadLibrary } from './library';

const RECENT_KEY = 'paperLibrary.recent';
const RECENT_MAX = 20;

export function activate(context: vscode.ExtensionContext) {
  const folder = vscode.workspace.workspaceFolders?.find((f) => existsSync(path.join(f.uri.fsPath, CONFIG_NAME)));
  if (!folder) return;
  let config: LibraryConfig;
  try {
    config = loadConfig(folder.uri.fsPath);
  } catch (error) {
    vscode.window.showErrorMessage(`Paper Library: cannot read ${CONFIG_NAME}: ${error}`);
    return;
  }
  void vscode.commands.executeCommand('setContext', 'paperLibrary.active', true);

  // Loaded on first use; any change to a paper file drops it, and the next command reads it again.
  let library: Promise<Library> | undefined;
  const getLibrary = () => {
    library ??= loadLibrary(config).catch((error) => {
      library = undefined;
      throw error;
    });
    return library;
  };
  const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(config.libraryDir, '**/*.md'));
  const drop = () => (library = undefined);
  watcher.onDidCreate(drop);
  watcher.onDidDelete(drop);
  watcher.onDidChange(drop);
  const notesWatcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(config.notesDir, '*.md'));
  notesWatcher.onDidCreate(drop);
  notesWatcher.onDidDelete(drop);

  const recent = {
    get: () => context.workspaceState.get<string[]>(RECENT_KEY, []),
    add: (paper: Paper) => {
      const key = `${paper.topic}/${paper.stem}`;
      const keys = [key, ...recent.get().filter((k) => k !== key)].slice(0, RECENT_MAX);
      return context.workspaceState.update(RECENT_KEY, keys);
    },
  };

  context.subscriptions.push(
    watcher,
    notesWatcher,
    vscode.commands.registerCommand('paperLibrary.openPaper', () => openPaper(getLibrary(), recent)),
    vscode.commands.registerCommand('paperLibrary.searchText', () => searchText(config, folder)),
    vscode.commands.registerCommand('paperLibrary.revealInLibrary', (uri?: vscode.Uri) =>
      revealInLibrary(getLibrary(), recent, uri),
    ),
  );
}

export function deactivate() {}

interface Recent {
  get(): string[];
  add(paper: Paper): Thenable<void>;
}

const buttons = {
  markdown: { iconPath: new vscode.ThemeIcon('markdown'), tooltip: 'Open the markdown' },
  notes: { iconPath: new vscode.ThemeIcon('note'), tooltip: 'Open the notes' },
  reveal: { iconPath: new vscode.ThemeIcon('list-tree'), tooltip: 'Reveal in Explorer' },
};

interface PaperItem extends vscode.QuickPickItem {
  paper: Paper;
}

/** A quick pick over every paper by title. Enter opens the PDF; the item buttons open the other files. */
async function openPaper(libraryPromise: Promise<Library>, recent: Recent) {
  const pick = vscode.window.createQuickPick<PaperItem | vscode.QuickPickItem>();
  pick.placeholder = 'Open a paper by title or topic (Enter opens the PDF)';
  pick.matchOnDescription = true;
  pick.busy = true;
  pick.show();

  let library: Library;
  try {
    library = await libraryPromise;
  } catch (error) {
    pick.hide();
    vscode.window.showErrorMessage(`Paper Library: cannot read the papers: ${error}`);
    return;
  }
  const item = (paper: Paper): PaperItem => ({
    label: paper.title,
    description: [paper.topic, paper.year].filter(Boolean).join(' · '),
    detail: paper.summary || undefined,
    buttons: paper.notesPath ? [buttons.markdown, buttons.notes, buttons.reveal] : [buttons.markdown, buttons.reveal],
    paper,
  });
  const byKey = new Map(library.papers.map((p) => [`${p.topic}/${p.stem}`, p]));
  const recentPapers = recent.get().flatMap((key) => byKey.get(key) ?? []);
  const recentSet = new Set(recentPapers);
  const rest = library.papers.filter((p) => !recentSet.has(p));
  pick.items = recentPapers.length
    ? [
        { label: 'recently opened', kind: vscode.QuickPickItemKind.Separator },
        ...recentPapers.map(item),
        { label: `all papers (${library.papers.length})`, kind: vscode.QuickPickItemKind.Separator },
        ...rest.map(item),
      ]
    : rest.map(item);
  pick.busy = false;

  pick.onDidAccept(() => {
    const selected = pick.selectedItems[0];
    if (!selected || !('paper' in selected)) return;
    pick.hide();
    void openPdf(selected.paper, recent);
  });
  pick.onDidTriggerItemButton(({ item: selected, button }) => {
    if (!('paper' in selected)) return;
    pick.hide();
    const { paper } = selected;
    void recent.add(paper);
    if (button === buttons.markdown) void open(paper.mdPath);
    else if (button === buttons.notes && paper.notesPath) void open(paper.notesPath);
    else if (button === buttons.reveal) void reveal(paper.mdPath);
  });
  pick.onDidHide(() => pick.dispose());
}

/** The PDF, in whichever editor claims *.pdf (the PDF viewer); the markdown when there is no PDF. */
async function openPdf(paper: Paper, recent: Recent) {
  void recent.add(paper);
  if (existsSync(paper.pdfPath)) {
    await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(paper.pdfPath));
  } else {
    vscode.window.showWarningMessage(`No PDF for "${paper.title}" at ${paper.pdfPath}; opening the markdown.`);
    await open(paper.mdPath);
  }
}

function open(file: string) {
  return vscode.commands.executeCommand('vscode.open', vscode.Uri.file(file));
}

function reveal(file: string) {
  return vscode.commands.executeCommand('revealInExplorer', vscode.Uri.file(file));
}

/** The search view, limited to the papers' markdown, filled with the selection. */
function searchText(config: LibraryConfig, folder: vscode.WorkspaceFolder) {
  const editor = vscode.window.activeTextEditor;
  const selection = editor && !editor.selection.isEmpty ? editor.document.getText(editor.selection) : '';
  const rel = path.relative(folder.uri.fsPath, config.libraryDir);
  const base = rel && !rel.startsWith('..') && !path.isAbsolute(rel) ? `./${rel.split(path.sep).join('/')}` : config.libraryDir;
  return vscode.commands.executeCommand('workbench.action.findInFiles', {
    query: selection.includes('\n') ? '' : selection,
    filesToInclude: `${base}/**/*.md`,
    filesToExclude: '**/README.md',
    triggerSearch: !!selection,
  });
}

/** The active file: a text editor's document, or a custom editor's file (a PDF in the viewer). */
function activeFile(): vscode.Uri | undefined {
  const input = vscode.window.tabGroups.activeTabGroup.activeTab?.input;
  if (input instanceof vscode.TabInputText || input instanceof vscode.TabInputCustom) return input.uri;
  return vscode.window.activeTextEditor?.document.uri;
}

/** From any file of a paper, the paper's other files. The counterpart (PDF ↔ markdown) comes first. */
async function revealInLibrary(libraryPromise: Promise<Library>, recent: Recent, uri?: vscode.Uri) {
  const file = uri ?? activeFile();
  if (!file || file.scheme !== 'file') {
    vscode.window.showInformationMessage('Paper Library: open a paper (its PDF, markdown or notes) first.');
    return;
  }
  const library = await libraryPromise;
  const found = library.paperForFile(file.fsPath);
  if (!found) {
    vscode.window.showInformationMessage(`Paper Library: ${path.basename(file.fsPath)} is not a paper of this library.`);
    return;
  }
  const { paper, kind } = found;
  type Action = vscode.QuickPickItem & { run: () => Thenable<unknown> };
  const pdf: Action = { label: '$(file-pdf) Open the PDF', run: () => openPdf(paper, recent) };
  const markdown: Action = { label: '$(markdown) Open the markdown', run: () => open(paper.mdPath) };
  const actions: Action[] = kind === 'pdf' ? [markdown] : kind === 'markdown' ? [pdf] : [pdf, markdown];
  if (paper.notesPath && kind !== 'notes') {
    actions.push({ label: '$(note) Open the notes', run: () => open(paper.notesPath!) });
  }
  actions.push(
    {
      label: '$(book) Open the topic index',
      description: paper.topic,
      run: () => vscode.commands.executeCommand('markdown.showPreview', vscode.Uri.file(library.topicIndex(paper))),
    },
    { label: '$(list-tree) Reveal in Explorer', run: () => reveal(paper.mdPath) },
  );
  const action = await vscode.window.showQuickPick(actions, { title: paper.title });
  await action?.run();
}
