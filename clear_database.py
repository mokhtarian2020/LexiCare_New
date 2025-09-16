#!/usr/bin/env python3
"""
Script to clear all existing data from the LexiCare database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.session import SessionLocal
from backend.db.models import Report
from sqlalchemy import text

def clear_database():
    """Clear all existing data from the database"""
    
    print("🗑️ LexiCare Database Cleanup")
    print("=" * 40)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # First, show current data count
        current_reports = db.query(Report).all()
        print(f"📊 Current reports in database: {len(current_reports)}")
        
        if len(current_reports) == 0:
            print("✅ Database is already empty!")
            return
        
        # Show some examples of what will be deleted
        print(f"\n📋 Sample reports to be deleted:")
        for i, report in enumerate(current_reports[:5]):
            print(f"  {i+1}. CF: {report.patient_cf}, Type: {report.report_type}, Date: {report.report_date}")
        
        if len(current_reports) > 5:
            print(f"  ... and {len(current_reports) - 5} more reports")
        
        # Confirm deletion
        print(f"\n⚠️ WARNING: This will DELETE ALL {len(current_reports)} reports!")
        print("This action cannot be undone.")
        
        # For script automation, we'll proceed directly
        # In production, you might want user confirmation
        
        print(f"\n🗑️ Deleting all reports...")
        
        # Delete all reports
        deleted_count = db.query(Report).delete()
        db.commit()
        
        print(f"✅ Successfully deleted {deleted_count} reports!")
        
        # Verify deletion
        remaining_reports = db.query(Report).count()
        print(f"📊 Reports remaining: {remaining_reports}")
        
        if remaining_reports == 0:
            print("🎉 Database is now clean and ready for new data!")
        else:
            print(f"⚠️ Warning: {remaining_reports} reports still remain")
            
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clear_database_with_confirmation():
    """Clear database with user confirmation"""
    
    print("🗑️ LexiCare Database Cleanup")
    print("=" * 40)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Show current data count
        current_reports = db.query(Report).all()
        print(f"📊 Current reports in database: {len(current_reports)}")
        
        if len(current_reports) == 0:
            print("✅ Database is already empty!")
            return
        
        # Show what will be deleted
        print(f"\n📋 Reports to be deleted:")
        for i, report in enumerate(current_reports[:10]):
            print(f"  {i+1}. CF: {report.patient_cf}, Type: {report.report_type[:50]}..., Date: {report.report_date}")
        
        if len(current_reports) > 10:
            print(f"  ... and {len(current_reports) - 10} more reports")
        
        # Ask for confirmation
        print(f"\n⚠️ WARNING: This will DELETE ALL {len(current_reports)} reports!")
        print("This action cannot be undone.")
        
        response = input("Are you sure you want to delete all data? (yes/no): ").lower().strip()
        
        if response in ['yes', 'y']:
            print(f"\n🗑️ Deleting all reports...")
            
            # Delete all reports
            deleted_count = db.query(Report).delete()
            db.commit()
            
            print(f"✅ Successfully deleted {deleted_count} reports!")
            print("🎉 Database is now clean and ready for new data!")
            
        else:
            print("❌ Operation cancelled. No data was deleted.")
            
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # For direct execution, clear without confirmation
    clear_database()
    
    print(f"\n💡 To run with confirmation prompt, use:")
    print(f"   python -c \"from clear_database import clear_database_with_confirmation; clear_database_with_confirmation()\"")
