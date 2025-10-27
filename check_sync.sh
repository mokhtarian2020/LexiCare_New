#!/bin/bash

echo "🔍 CHECKING LEXICARE GITHUB SYNC STATUS"
echo "========================================"

cd /home/amir/Documents/amir/LexiCare_new

echo ""
echo "📁 Current directory: $(pwd)"
echo "🌐 Remote repository:"
git remote -v

echo ""
echo "🔄 Current Git status:"
git status

echo ""
echo "📊 File count summary:"
echo "  • Total files in project: $(find . -type f ! -path './.git/*' | wc -l)"
echo "  • Files tracked by Git: $(git ls-files | wc -l)"
echo "  • Backend files: $(find backend -type f 2>/dev/null | wc -l)"
echo "  • Frontend files: $(find frontend -type f 2>/dev/null | wc -l)"
echo "  • Test files: $(find tests -type f 2>/dev/null | wc -l)"
echo "  • Archive files: $(find tests_archive -type f 2>/dev/null | wc -l)"

echo ""
echo "🔍 Checking sync with GitHub:"
git fetch origin main 2>/dev/null
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null)
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null)

if [ "$AHEAD" -gt 0 ]; then
    echo "⚠️  Local repository is $AHEAD commits AHEAD of GitHub"
    echo "📤 You need to PUSH to GitHub: git push origin main"
elif [ "$BEHIND" -gt 0 ]; then
    echo "⚠️  Local repository is $BEHIND commits BEHIND GitHub"
    echo "📥 You need to PULL from GitHub: git pull origin main"
else
    echo "✅ Local repository is IN SYNC with GitHub!"
fi

echo ""
echo "📋 Last commit:"
git log -1 --oneline

echo ""
echo "🎯 SYNC CHECK COMPLETE"