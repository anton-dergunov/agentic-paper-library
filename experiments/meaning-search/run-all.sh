#!/usr/bin/env bash
# Embed the library with every candidate, one after another (embed.py's usage has the details).
set -euo pipefail
cd "$(dirname "$0")"
for encoder in "${@:-minilm bge-small bge-base e5-small specter qwen3}"; do
  for name in $encoder; do
    uv run --quiet --project ../.. --with sentence-transformers \
      python embed.py "$name" tsa ts ta --cpu-sample 100 2>&1 | grep -v -e Redirects -e "Loading weights"
  done
done
