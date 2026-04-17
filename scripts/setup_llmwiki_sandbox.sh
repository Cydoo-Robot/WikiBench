#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SANDBOX="${REPO_ROOT}/.wikibench-sandboxes/llm-wiki-compiler"
mkdir -p "$(dirname "$SANDBOX")"
if [[ ! -d "${SANDBOX}/.git" ]]; then
  git clone --depth 1 https://github.com/atomicmemory/llm-wiki-compiler.git "${SANDBOX}"
fi
cd "${SANDBOX}"
command -v npm >/dev/null || { echo "npm not found; install Node.js 18+"; exit 1; }
npm install
npm run build
echo ""
echo "Sandbox ready: ${SANDBOX}"
echo "export WIKIBENCH_LLM_WIKI_ROOT=${SANDBOX}"
echo "export ANTHROPIC_API_KEY=..." # see upstream README
