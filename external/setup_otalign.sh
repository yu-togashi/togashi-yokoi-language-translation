#!/usr/bin/env bash
# Clone the official otalign implementation (GPL-3.0) into external/otalign/,
# pin it to a fixed upstream commit, and apply our local fixes.
# external/otalign/ is gitignored; our changes live in external/otalign.patch.
#
# To update the patch after editing external/otalign/:
#   git -C external/otalign diff > external/otalign.patch
set -euo pipefail

cd "$(dirname "$0")"
commit=37e48f82e607cc338c44fb6022ad7566d74d369a  # upstream HEAD, 2020-06-16

if [ ! -d otalign ]; then
  git clone https://github.com/dmelis/otalign.git otalign
fi
git -C otalign checkout -q "$commit"

if [ -s otalign.patch ]; then
  if git -C otalign apply --check ../otalign.patch 2>/dev/null; then
    git -C otalign apply ../otalign.patch
    echo "applied otalign.patch"
  else
    echo "otalign.patch already applied or does not apply cleanly; skipped"
  fi
fi
