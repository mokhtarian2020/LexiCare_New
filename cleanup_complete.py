#!/usr/bin/env python3
"""
Script to clean up both database and storage files
"""

import sys
import os
import glob
from pathlib import Path

# Change to backend directory for imports to work
script_dir = Path(__file__).parent
backend_dir = script_dir / "backend"
original_cwd = os.getcwd()

# Temporarily change to backend directory
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

try:
    from db.session import SessionLocal
    from db.models import Report
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def clean_storage_files():
    """Clean up orphaned PDF files in storage"""
    
    print("🗂️ Cleaning Storage Files")
    print("=" * 30)
    
    storage_path = "backend/storage"
    
    if not os.path.exists(storage_path):
        print("📁 Storage directory doesn't exist")
        return
    
    # Get all PDF files in storage (excluding .gitkeep)
    pdf_files = glob.glob(os.path.join(storage_path, "*.pdf"))
    
    print(f"📊 Found {len(pdf_files)} PDF files in storage")
    
    if len(pdf_files) == 0:
        print("✅ Storage is already clean!")
        return
    
    # Show some examples
    print(f"\n📋 Files to be deleted:")
    for i, file_path in enumerate(pdf_files[:5]):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        print(f"  {i+1}. {filename} ({file_size:,} bytes)")
    
    if len(pdf_files) > 5:
        print(f"  ... and {len(pdf_files) - 5} more files")
    
    # Calculate total size
    total_size = sum(os.path.getsize(f) for f in pdf_files)
    print(f"\n💾 Total storage to be freed: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # Delete files
    print(f"\n🗑️ Deleting {len(pdf_files)} files...")
    
    deleted_count = 0
    for file_path in pdf_files:
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")
    
    print(f"✅ Successfully deleted {deleted_count} files!")
    
    # Verify cleanup
    remaining_files = glob.glob(os.path.join(storage_path, "*.pdf"))
    print(f"📊 Files remaining: {len(remaining_files)}")
    
    if len(remaining_files) == 0:
        print("🎉 Storage is now clean!")

def full_cleanup():
    """Perform complete cleanup of database and storage"""
    
    print("🧹 LexiCare Complete Database & Storage Cleanup")
    print("=" * 55)
    
    # Clean database
    db = SessionLocal()
    try:
        current_reports = db.query(Report).count()
        print(f"📊 Current reports in database: {current_reports}")
        
        if current_reports > 0:
            print(f"🗑️ Deleting {current_reports} database records...")
            deleted_count = db.query(Report).delete()
            db.commit()
            print(f"✅ Deleted {deleted_count} database records")
        else:
            print("✅ Database is already empty")
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        db.rollback()
    finally:
        db.close()
    
    print()
    
    # Clean storage
    clean_storage_files()
    
    print(f"\n🎉 Complete cleanup finished!")
    print("💡 The system is now ready for fresh data.")
    print("📄 You can now upload your medical reports for testing.")

if __name__ == "__main__":
    full_cleanup()
