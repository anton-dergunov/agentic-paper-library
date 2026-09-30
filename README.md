# papers

My research-paper library: markdown copies of papers, organised by topic, for reading and
discussing papers with a coding agent. The PDFs live outside the repository, in
`~/Yandex.Disk.localized/Papers/`, at the same topic paths.

- [library/](library/README.md): the papers, by topic
- [catalog/](catalog/): the topic tree, and the papers deliberately not added
- [docs/](docs/): how this setup was chosen, open tasks, experiments
- [AGENTS.md](AGENTS.md): how an agent works here

Add a paper:

```bash
./scripts/add-arxiv-paper.sh 2501.13956 llm/memory/agent
./scripts/add-pdf-paper.sh ~/Downloads/paper.pdf llm/evaluation/methods --title "..."
./scripts/add-web-article.py https://distill.pub/2017/momentum/ deep-learning/optimizers-and-schedules
./scripts/build-index.py && ./scripts/check-library.py
```

Or ask Claude Code to add it (`/add-paper`), which also picks the topic and writes the summary.
