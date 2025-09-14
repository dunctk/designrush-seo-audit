#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/publish_to_github.sh [repo-name]
# Requires: GitHub CLI (gh) authenticated, git installed.

NAME="${1:-designrush-seo-audit}"
DESC="Agency Directory SEO audit and strategy (Polars + uv)"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' not found. Install: https://cli.github.com/" >&2
  exit 1
fi

# Initialize or normalize to 'main'
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  :
else
  git init -b main
fi

if git rev-parse --verify main >/dev/null 2>&1; then
  git checkout main >/dev/null 2>&1 || true
else
  git checkout -b main >/dev/null 2>&1 || true
fi

git add -A
git commit -m "chore: initial push" || true

# Create private repo and push
gh repo create "$NAME" \
  --private \
  --source . \
  --remote origin \
  --description "$DESC" \
  --disable-wiki

git push -u origin main
echo "Pushed to GitHub: https://github.com/$(gh api user -q .login)/$NAME"
