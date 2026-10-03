# Configuration

A library is a folder with `paper-library.yaml` at its root. `paperlib` finds it from the working directory, searching that folder and its parents, or from `$PAPER_LIBRARY`. `paperlib init` writes the file with comments; every key is optional.

| Key | Default | What it sets |
|---|---|---|
| `reader` | your user name | Who reads the library. The skills address notes and questions to them, and the guide names them. |
| `pdf_root` | `pdfs` | Where the original PDFs go, mirroring `library/`. Keep it out of git: a synced folder (Dropbox, Yandex Disk, iCloud) makes the PDFs readable on a tablet. |
| `pdf_link` | none (`init` writes `pdf`) | A symlink in the library to `pdf_root`, made by `paperlib init` and ignored by git. An editor opened on the library then shows both trees, and the indexes link each paper's PDF through it. |
| `overview_dir` | none | A folder for your own note per paper, which the `overview` skill writes, e.g. a folder in an Obsidian vault. Without it, the skill asks where notes should go. |
| `library`, `catalog`, `notes`, `reviews`, `inbox` | `library`, `catalog`, `notes`, `reviews`, `INBOX.txt` | The library's own folders and files, if you want other names. |
| `cache` | `~/.cache/papers` | arXiv downloads (HTML, figures, LaTeX sources) and marker's environment, shared by every library. |
| `chrome` | found on PATH, then the macOS app | Headless Chrome, for web articles. |

Relative paths are taken from the library root, and `~` is expanded. The environment variables `LIBRARY_DIR`, `PDF_ROOT` and `PAPERS_CACHE` override the config, for example on a machine where the PDFs are mounted somewhere else. `PAPERS_MARKER_PYTHON` points at another marker environment.

## What else lives in a library

| File | Who writes it |
|---|---|
| `AGENTS.md` | You: who reads this library, their focus, how they like papers explained, other places on the machine the agent may use. It ends with `@.claude/library-guide.md`. |
| `CLAUDE.md` | `@AGENTS.md`, so that Claude Code reads it. |
| `.claude/library-guide.md` | `paperlib build-index`, from the engine's [guide](../guide/library-guide.md) with your paths filled in. Commit it, so an agent without the engine still knows the conventions. |
| `.claude/skills/` | `paperlib init`: symlinks to the engine's skills, ignored by git. |
| `.vscode/settings.json` | `paperlib init`, once: the PDF viewer's root and search excludes. |

Run `paperlib init` again after updating the engine, or on a new machine. It only adds what is missing.
