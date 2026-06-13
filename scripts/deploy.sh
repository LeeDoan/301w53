#!/bin/zsh

# exit on error
set -e

SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Starting Dashboard Deployment to GitHub ==="

# 1. Run Python data build
echo "Running update_dashboard.py to compile index.html..."
python3 "$SCRIPT_DIR/update_dashboard.py"

# 2. Check if repo exists on GitHub, if not create it
echo "Checking if repository 301w53 exists on GitHub..."
if ! env -u GITHUB_TOKEN gh repo view LDOAN6_ford/301w53 &>/dev/null; then
    echo "Creating public repository LDOAN6_ford/301w53 on GitHub..."
    env -u GITHUB_TOKEN gh repo create 301w53 --public --confirm
else
    echo "Repository LDOAN6_ford/301w53 already exists on GitHub."
fi

# 3. Configure local git remotes
if ! git remote | grep -q "^origin$"; then
    echo "Adding git remote origin..."
    git remote add origin https://github.com/LDOAN6_ford/301w53.git
else
    echo "Remote origin already configured."
    # Ensure correct remote URL
    git remote set-url origin https://github.com/LDOAN6_ford/301w53.git
fi

# 4. Commit and Push
echo "Committing files..."
git add .gitignore index.html README.md scripts/
git commit -m "Build: Consolidated condo board strategy dashboard prototype" || echo "No changes to commit"

git branch -M main

echo "Pushing main branch to GitHub..."
env -u GITHUB_TOKEN git push -u origin main --force

# 5. Enable GitHub Pages if not already enabled
echo "Enabling GitHub Pages on main branch..."
# We wrap this in || true because if Pages is already enabled, it might return a 409 Conflict.
env -u GITHUB_TOKEN gh api repos/LDOAN6_ford/301w53/pages \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -f "source[branch]=main" \
  -f "source[path]=/" || echo "GitHub Pages setup returned status code (likely already enabled)."

echo "=== Deployment Successfully Completed ==="
echo "Live URL: https://ldoan6-ford.github.io/301w53/"
