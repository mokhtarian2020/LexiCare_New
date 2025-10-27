#!/usr/bin/env python3
"""
Script to test and add doctor feedback to reports
"""
import sys
import os
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from db.session import SessionLocal, get_db
    from db.models import Report
    from db.crud import get_report, update_report_feedback
    
    def test_feedback_api():
        """Test the feedback API functionality"""
        print("🧪 Testing Doctor Feedback Functionality")
        print("=" * 60)
        
        db = SessionLocal()
        try:
            # Get all reports
            reports = db.query(Report).all()
            print(f"📊 Found {len(reports)} reports in database")
            
            if not reports:
                print("❌ No reports found to test feedback on")
                return
                
            # Test adding feedback to the first report
            test_report = reports[0]
            print(f"\n🧪 Testing feedback on report: {test_report.filename}")
            print(f"   Patient: {test_report.codice_fiscale}")
            print(f"   Current AI Diagnosis: {test_report.diagnosis}")
            print(f"   Current AI Classification: {test_report.classification}")
            
            # Check current feedback
            current_doctor_diagnosis = getattr(test_report, 'doctor_diagnosis', None)
            current_doctor_classification = getattr(test_report, 'doctor_classification', None)
            current_doctor_comment = getattr(test_report, 'doctor_comment', None)
            
            print(f"   Current Doctor Diagnosis: {current_doctor_diagnosis}")
            print(f"   Current Doctor Classification: {current_doctor_classification}")
            print(f"   Current Doctor Comment: {current_doctor_comment}")
            
            # Add or update feedback
            new_feedback = {
                'doctor_diagnosis': 'Proteinuria confermata dal medico - richiede monitoraggio',
                'doctor_classification': 'severo',
                'doctor_comment': 'Il paziente dovrebbe seguire una dieta a basso contenuto proteico e ripetere l\'esame tra 2 settimane. Considerare ulteriori test renali.'
            }
            
            print(f"\n✏️ Adding new feedback...")
            print(f"   New Doctor Diagnosis: {new_feedback['doctor_diagnosis']}")
            print(f"   New Doctor Classification: {new_feedback['doctor_classification']}")
            print(f"   New Doctor Comment: {new_feedback['doctor_comment']}")
            
            # Update the report
            success = update_report_feedback(
                db=db,
                report_id=test_report.id,
                doctor_diagnosis=new_feedback['doctor_diagnosis'],
                doctor_classification=new_feedback['doctor_classification'],
                doctor_comment=new_feedback['doctor_comment']
            )
            
            if success:
                print("✅ Feedback added successfully!")
                
                # Verify the update
                updated_report = get_report(db, test_report.id)
                if updated_report:
                    print(f"\n🔍 Verification - Updated report:")
                    print(f"   Doctor Diagnosis: {updated_report.doctor_diagnosis}")
                    print(f"   Doctor Classification: {updated_report.doctor_classification}")
                    print(f"   Doctor Comment: {updated_report.doctor_comment}")
                else:
                    print("❌ Could not retrieve updated report")
            else:
                print("❌ Failed to add feedback")
                
            # Test adding feedback to second report if it exists
            if len(reports) > 1:
                test_report2 = reports[1]
                print(f"\n🧪 Testing feedback on second report: {test_report2.filename}")
                
                feedback2 = {
                    'doctor_diagnosis': 'Valori nella norma secondo revisione medica',
                    'doctor_classification': 'normale',
                    'doctor_comment': 'I risultati sono accettabili. Continuare con controlli di routine ogni 6 mesi.'
                }
                
                success2 = update_report_feedback(
                    db=db,
                    report_id=test_report2.id,
                    doctor_diagnosis=feedback2['doctor_diagnosis'],
                    doctor_classification=feedback2['doctor_classification'],
                    doctor_comment=feedback2['doctor_comment']
                )
                
                if success2:
                    print("✅ Second feedback added successfully!")
                else:
                    print("❌ Failed to add second feedback")
                    
        except Exception as e:
            print(f"❌ Error testing feedback: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
            
    def display_all_feedback():
        """Display all reports with their feedback"""
        print("\n📋 All Reports with Feedback Status")
        print("=" * 80)
        
        db = SessionLocal()
        try:
            reports = db.query(Report).order_by(Report.upload_date.desc()).all()
            
            if not reports:
                print("❌ No reports found")
                return
                
            for i, report in enumerate(reports, 1):
                print(f"\n📄 Report #{i}: {report.filename}")
                print(f"   👤 Patient: {report.codice_fiscale}")
                print(f"   📅 Report Date: {report.report_date}")
                print(f"   📋 Type: {getattr(report, 'report_category', 'N/A')}")
                print(f"   🤖 AI Diagnosis: {report.diagnosis}")
                print(f"   🤖 AI Classification: {report.classification}")
                
                # Doctor feedback
                doctor_diagnosis = getattr(report, 'doctor_diagnosis', None)
                doctor_classification = getattr(report, 'doctor_classification', None) 
                doctor_comment = getattr(report, 'doctor_comment', None)
                
                has_feedback = any([doctor_diagnosis, doctor_classification, doctor_comment])
                
                if has_feedback:
                    print(f"   ✅ HAS DOCTOR FEEDBACK:")
                    print(f"      👨‍⚕️ Diagnosis: {doctor_diagnosis or 'N/A'}")
                    print(f"      👨‍⚕️ Classification: {doctor_classification or 'N/A'}")
                    print(f"      👨‍⚕️ Comment: {doctor_comment or 'N/A'}")
                else:
                    print(f"   ❌ NO DOCTOR FEEDBACK")
                    
        except Exception as e:
            print(f"❌ Error displaying feedback: {e}")
        finally:
            db.close()
            
    def test_feedback_api_endpoint():
        """Test the API endpoint for feedback"""
        print("\n🌐 Testing Feedback API Endpoint")
        print("=" * 50)
        
        import requests
        
        # Get a report ID to test with
        db = SessionLocal()
        try:
            reports = db.query(Report).all()
            if not reports:
                print("❌ No reports found for API testing")
                return
                
            test_report = reports[0]
            report_id = str(test_report.id)
            
            print(f"🧪 Testing API with report ID: {report_id}")
            
            # Test data
            api_feedback = {
                "doctor_diagnosis": "API Test: Conferma diagnosi con raccomandazioni aggiuntive",
                "doctor_classification": "severo", 
                "doctor_comment": "API Test: Inviato tramite endpoint API - funziona correttamente!"
            }
            
            # Make API call
            try:
                response = requests.post(
                    f"http://localhost:8008/api/feedback/{report_id}",
                    json=api_feedback,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("✅ API call successful!")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"❌ API call failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ Could not connect to API - make sure backend is running on port 8008")
            except Exception as e:
                print(f"❌ API call error: {e}")
                
        finally:
            db.close()

    if __name__ == "__main__":
        print("🩺 LexiCare Doctor Feedback Tester")
        print("=" * 60)
        
        # Test feedback functionality
        test_feedback_api()
        
        # Display all feedback
        display_all_feedback()
        
        # Test API endpoint
        test_feedback_api_endpoint()
        
        print("\n✅ Feedback testing complete!")
        
except ImportError as e:
    print(f"❌ Could not import required modules: {e}")
    print("Make sure you're in the LexiCare directory and the backend is properly set up.")
