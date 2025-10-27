#!/usr/bin/env python3
"""
Script to check if all LexiCare files are pushed to GitHub
"""
import subprocess
import os
from pathlib import Path

def run_git_command(command, description):
    """Run a git command and return the result"""
    print(f"\n🔍 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd='/home/amir/Documents/amir/LexiCare_new'
        )
        
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(f"Warning: {result.stderr.strip()}")
            
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, ""

def count_local_files():
    """Count all files in the local repository"""
    project_path = Path('/home/amir/Documents/amir/LexiCare_new')
    
    # Count all files (excluding .git directory)
    all_files = []
    for file_path in project_path.rglob('*'):
        if file_path.is_file() and '.git' not in str(file_path):
            relative_path = file_path.relative_to(project_path)
            all_files.append(str(relative_path))
    
    return all_files

def main():
    """Check GitHub sync status"""
    
    print("🔍 LEXICARE GITHUB SYNC CHECK")
    print("=" * 50)
    
    # Check if we're in a git repository
    success, _ = run_git_command("git status", "Checking Git repository status")
    if not success:
        print("❌ Not a git repository or git command failed")
        return
    
    # Check remote repository
    success, remotes = run_git_command("git remote -v", "Checking remote repositories")
    if not success or not remotes:
        print("❌ No remote repository configured")
        return
    
    # Check current branch
    success, branch = run_git_command("git branch --show-current", "Current branch")
    print(f"Current branch: {branch}")
    
    # Check for uncommitted changes
    success, status = run_git_command("git status --porcelain", "Checking for uncommitted changes")
    if status:
        print("⚠️  UNCOMMITTED CHANGES FOUND:")
        print(status)
    else:
        print("✅ No uncommitted changes - all files are staged/committed")
    
    # Check if local branch is ahead/behind remote
    success, ahead_behind = run_git_command("git rev-list --left-right --count origin/main...HEAD", "Checking sync with remote")
    if success and ahead_behind:
        behind, ahead = ahead_behind.split('\t')
        if int(ahead) > 0:
            print(f"⚠️  Local repository is {ahead} commits ahead of remote")
            print("📤 Need to push to sync with GitHub")
        elif int(behind) > 0:
            print(f"⚠️  Local repository is {behind} commits behind remote")
            print("📥 Need to pull from GitHub")
        else:
            print("✅ Local repository is in sync with GitHub")
    
    # Get last commit info
    success, last_commit = run_git_command("git log -1 --oneline", "Last commit")
    if success:
        print(f"Last commit: {last_commit}")
    
    # Count local files
    print(f"\n📁 LOCAL FILE INVENTORY")
    print("-" * 30)
    local_files = count_local_files()
    
    # Categorize files
    categories = {
        'Backend': [],
        'Frontend': [],
        'Tests': [],
        'Documentation': [],
        'Configuration': [],
        'Archive': [],
        'Other': []
    }
    
    for file_path in local_files:
        if file_path.startswith('backend/'):
            categories['Backend'].append(file_path)
        elif file_path.startswith('frontend/'):
            categories['Frontend'].append(file_path)
        elif file_path.startswith('tests/') or file_path.startswith('tests_archive/'):
            categories['Tests'].append(file_path)
        elif file_path.endswith('.md') or file_path.endswith('.txt'):
            categories['Documentation'].append(file_path)
        elif file_path in ['docker-compose.yml', '.env', '.env.example', 'requirements.txt', '.gitignore']:
            categories['Configuration'].append(file_path)
        elif file_path.startswith('tests_archive/'):
            categories['Archive'].append(file_path)
        else:
            categories['Other'].append(file_path)
    
    total_files = len(local_files)
    print(f"📊 Total files in project: {total_files}")
    
    for category, files in categories.items():
        if files:
            print(f"  • {category}: {len(files)} files")
    
    # Check what files are tracked by git
    success, tracked_files = run_git_command("git ls-files", "Checking Git-tracked files")
    if success:
        tracked_count = len(tracked_files.split('\n')) if tracked_files else 0
        print(f"\n📋 Git tracking: {tracked_count} files")
        
        if tracked_count < total_files:
            untracked_count = total_files - tracked_count
            print(f"⚠️  {untracked_count} files may not be tracked by Git")
        else:
            print("✅ All files appear to be tracked by Git")
    
    # Final summary
    print(f"\n🎯 SYNC STATUS SUMMARY")
    print("=" * 30)
    
    if not status and ahead_behind and ahead_behind == "0\t0":
        print("✅ ALL FILES SUCCESSFULLY SYNCED WITH GITHUB!")
        print("🎉 Your complete LexiCare project is backed up")
        print("🔗 Repository: https://github.com/mokhtarian2020/LexiCare_New")
    elif status:
        print("⚠️  SYNC INCOMPLETE - Uncommitted changes found")
        print("💡 Run: git add . && git commit -m 'Update' && git push")
    elif ahead_behind and int(ahead_behind.split('\t')[1]) > 0:
        print("⚠️  SYNC INCOMPLETE - Local changes not pushed")
        print("💡 Run: git push origin main")
    else:
        print("❓ Unable to determine sync status")
        print("💡 Check your internet connection and GitHub repository")

if __name__ == "__main__":
    main()