#!/usr/bin/env bash
# Build paper/main.pdf from paper/main.tex + paper/references.bib.
# Trash-aware: temporary LaTeX artifacts are MOVED into .trash/latex-build/
# instead of being deleted. This keeps the lab safety rule (no rm) intact.

set -euo pipefail

cd "$(dirname "$0")/paper"

TEX=main
AUX_EXTS="aux log bbl blg out toc fdb_latexmk fls synctex.gz"

echo "==> pdflatex pass 1"
pdflatex -interaction=nonstopmode "$TEX.tex" >/dev/null || {
  echo "pdflatex pass 1 failed — showing main.log"
  tail -60 "$TEX.log"
  exit 1
}

echo "==> bibtex"
if [ -f "$TEX.aux" ]; then
  bibtex "$TEX" || echo "bibtex warnings (continuing)"
fi

echo "==> pdflatex pass 2"
pdflatex -interaction=nonstopmode "$TEX.tex" >/dev/null || true

echo "==> pdflatex pass 3"
pdflatex -interaction=nonstopmode "$TEX.tex" >/dev/null || {
  echo "pdflatex pass 3 failed — showing main.log"
  tail -60 "$TEX.log"
  exit 1
}

# Check for undefined references
if grep -q "Warning: There were undefined references" "$TEX.log" 2>/dev/null; then
  echo "WARN: undefined references in $TEX.log"
fi

if [ -f "$TEX.pdf" ]; then
  size=$(ls -lh "$TEX.pdf" | awk '{print $5}')
  echo "==> Built paper/$TEX.pdf ($size)"
else
  echo "ERROR: paper/$TEX.pdf was not produced"
  exit 1
fi

# Trash-aware cleanup: MOVE artifacts instead of deleting
stamp="$(date +%F)"
trash_dir="../.trash/latex-build/$stamp"
mkdir -p "$trash_dir"
for ext in $AUX_EXTS; do
  if [ -f "$TEX.$ext" ]; then
    mv "$TEX.$ext" "$trash_dir/$TEX.$ext.$(date +%H%M%S)"
  fi
done

# Log the cleanup
if [ -f ../logs/trash.md ]; then
  echo "$(date +"%Y-%m-%d %H:%M")  paper/*.{$(echo $AUX_EXTS | tr ' ' ',')}  →  $trash_dir   reason: LaTeX build artifacts" \
    >> ../logs/trash.md
fi
