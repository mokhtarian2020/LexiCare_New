#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from unittest.mock import AsyncMock
from backend.api.analyze import analyze_documents
from backend.db.session import get_db

async def simulate_upload_workflow():
    """Simulate uploading both PDFs sequentially to test comparison"""
    
    print("🧪 Testing Complete Upload & Comparison Workflow")
    print("=" * 55)
    
    # Get database connection
    db = next(get_db())
    
    try:
        # Step 1: Upload first PDF (Feb 2024)
        print("📄 Step 1: Uploading first PDF (Feb 2024, Proteine: 15)...")
        
        with open('report_2024_02_01.pdf', 'rb') as f:
            content1 = f.read()
        
        # Create mock file object
        mock_file1 = AsyncMock()
        mock_file1.filename = "report_2024_02_01.pdf"
        mock_file1.read = AsyncMock(return_value=content1)
        
        # Mock request object
        mock_request = AsyncMock()
        
        # Upload first file
        result1 = await analyze_documents(mock_request, [mock_file1], db)
        
        print(f"Result 1 - Saved: {result1['risultati'][0].get('salvato', False)}")
        if result1['risultati'][0].get('salvato'):
            print(f"  Patient: {result1['risultati'][0].get('nome_paziente')}")
            print(f"  CF: {result1['risultati'][0].get('codice_fiscale')}")
            print(f"  Report Type: {result1['risultati'][0].get('tipo_referto')}")
            print(f"  Comparison Status: {result1['risultati'][0].get('situazione', 'N/A')}")
            print(f"  Explanation: {result1['risultati'][0].get('spiegazione', 'N/A')}")
        print()
        
        # Step 2: Upload second PDF (May 2024)
        print("📄 Step 2: Uploading second PDF (May 2024, Proteine: 45)...")
        
        with open('report_2024_05_01.pdf', 'rb') as f:
            content2 = f.read()
        
        # Create mock file object
        mock_file2 = AsyncMock()
        mock_file2.filename = "report_2024_05_01.pdf"
        mock_file2.read = AsyncMock(return_value=content2)
        
        # Upload second file
        result2 = await analyze_documents(mock_request, [mock_file2], db)
        
        print(f"Result 2 - Saved: {result2['risultati'][0].get('salvato', False)}")
        if result2['risultati'][0].get('salvato'):
            print(f"  Patient: {result2['risultati'][0].get('nome_paziente')}")
            print(f"  CF: {result2['risultati'][0].get('codice_fiscale')}")
            print(f"  Report Type: {result2['risultati'][0].get('tipo_referto')}")
            print(f"  Comparison Status: {result2['risultati'][0].get('situazione', 'N/A')}")
            print(f"  Explanation: {result2['risultati'][0].get('spiegazione', 'N/A')}")
        
        print()
        print("🎯 Test Summary:")
        print(f"  First upload should have no comparison (first report)")
        print(f"  Second upload should show 'peggiorata' (15 → 45 mg/dl)")
        
        # Validate expected results
        if result1['risultati'][0].get('situazione') == 'nessun confronto disponibile':
            print("  ✅ First upload: Correctly shows no comparison available")
        else:
            print(f"  ❌ First upload: Expected 'nessun confronto disponibile', got '{result1['risultati'][0].get('situazione')}'")
            
        if result2['risultati'][0].get('situazione') == 'peggiorata':
            print("  ✅ Second upload: Correctly detected worsening condition")
        else:
            print(f"  ❌ Second upload: Expected 'peggiorata', got '{result2['risultati'][0].get('situazione')}'")
            
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(simulate_upload_workflow())
