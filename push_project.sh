#!/bin/bash

echo "🚀 LEXICARE PROJECT - GITHUB PUSH"
echo "=================================================="

cd /home/amir/Documents/amir/LexiCare_new

echo ""
echo "🔍 Checking current Git status..."
git status

echo ""
echo "📁 Adding all files to Git..."
git add .

echo ""
echo "📋 Files to be committed:"
git status

echo ""
echo "💾 Committing changes..."
git commit -m "Complete LexiCare system with all enhancements: duplicate detection, chronological comparison, medical accuracy fixes, EHR integration, and organized file structure"

echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Push completed!"
echo "🔗 Repository: https://github.com/mokhtarian2020/LexiCare_New"