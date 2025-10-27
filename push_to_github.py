#!/usr/bin/env python3
"""
Script to push LexiCare project to GitHub
"""
import subprocess
import os

def run_command(command, description):
    """Run a shell command and print the result"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='/home/amir/Documents/amir/LexiCare_new')
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Push the complete LexiCare project to GitHub"""
    
    print("🚀 LEXICARE PROJECT - GITHUB PUSH")
    print("=" * 50)
    
    # Check current status
    run_command("git status", "Checking current Git status")
    
    # Add all files
    if run_command("git add .", "Adding all files to Git"):
        print("✅ All files added successfully")
    
    # Check what will be committed
    run_command("git status", "Checking files to be committed")
    
    # Commit changes
    commit_message = "Complete LexiCare system with all enhancements: duplicate detection, chronological comparison, medical accuracy fixes, EHR integration, and organized file structure"
    
    if run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("✅ Changes committed successfully")
    
    # Push to GitHub
    if run_command("git push origin main", "Pushing to GitHub repository"):
        print("✅ Successfully pushed to GitHub!")
        print("\n🎉 COMPLETE SUCCESS!")
        print("📋 Your LexiCare project is now fully backed up on GitHub")
        print("🔗 Repository: https://github.com/mokhtarian2020/LexiCare_New")
    else:
        print("❌ Push failed. Checking remote configuration...")
        run_command("git remote -v", "Checking remote repositories")

if __name__ == "__main__":
    main()