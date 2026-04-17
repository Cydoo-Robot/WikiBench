# Clone atomicmemory/llm-wiki-compiler under .wikibench-sandboxes/ and npm install + build.
# Requires: git, Node.js 18+ with npm on PATH. API keys are NOT stored here — set
# ANTHROPIC_API_KEY (or see upstream README) in your environment before wikibench run/verify.

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Sandbox = Join-Path $RepoRoot ".wikibench-sandboxes" "llm-wiki-compiler"

New-Item -ItemType Directory -Force -Path (Split-Path $Sandbox) | Out-Null

if (-not (Test-Path (Join-Path $Sandbox ".git"))) {
    git clone --depth 1 https://github.com/atomicmemory/llm-wiki-compiler.git $Sandbox
}

Push-Location $Sandbox
try {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Error "npm not found. Install Node.js 18+ from https://nodejs.org/ and re-open the terminal."
    }
    npm install
    npm run build
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Sandbox ready: $Sandbox"
Write-Host "Set environment (PowerShell):"
Write-Host ('  $env:WIKIBENCH_LLM_WIKI_ROOT="' + $Sandbox + '"')
Write-Host "And provider keys, e.g.:"
Write-Host '  $env:ANTHROPIC_API_KEY="..."'
Write-Host "Then: uv run pytest tests/adapter_contract/test_community_llmwiki.py -v --no-cov"
Write-Host "  (with WIKIBENCH_RUN_LLMWIKI_INTEGRATION=1 and WIKIBENCH_LLM_MOCK unset)"
