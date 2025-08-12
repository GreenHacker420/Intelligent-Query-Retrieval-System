#!/usr/bin/env python3
"""Test the optimization improvements."""

import asyncio
import json
import aiohttp
import time

async def test_optimized_system():
    """Test the optimized document processing system."""
    
    # Create a test document with sample content
    test_content = """
    INSURANCE POLICY DOCUMENT
    
    SECTION 1: COVERAGE DETAILS
    This policy provides comprehensive health insurance coverage for the policyholder and eligible dependents.
    
    SECTION 2: SURGICAL PROCEDURES
    Coverage for surgical procedures includes:
    - Knee surgery: Covered after 24-month waiting period
    - Heart surgery: Covered immediately for emergency cases
    - Cosmetic surgery: Not covered unless medically necessary
    
    SECTION 3: MATERNITY BENEFITS
    Maternity benefits are available after 12 months of continuous coverage.
    Benefits include:
    - Prenatal care
    - Delivery expenses
    - Postnatal care for 6 weeks
    
    SECTION 4: EXCLUSIONS
    The following are not covered:
    - Pre-existing conditions for first 48 months
    - Experimental treatments
    - Self-inflicted injuries
    
    SECTION 5: CLAIM PROCEDURES
    To file a claim:
    1. Contact customer service within 30 days
    2. Submit required documentation
    3. Wait for claim processing (5-10 business days)
    """
    
    # Save test document
    with open('test_policy.txt', 'w') as f:
        f.write(test_content)
    
    print("🧪 Testing Optimized Document Processing System")
    print("=" * 50)
    
    # Test file upload
    print("📁 Step 1: Testing file upload...")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Upload file
        with open('test_policy.txt', 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='test_policy.txt', content_type='text/plain')
            
            async with session.post('http://localhost:8000/api/v1/hackrx/upload', data=data) as response:
                if response.status == 200:
                    upload_result = await response.json()
                    file_url = upload_result['file_url']
                    print(f"✅ File uploaded successfully: {upload_result['filename']}")
                    print(f"   Size: {upload_result['size']} bytes")
                else:
                    print(f"❌ Upload failed: {response.status}")
                    return
        
        upload_time = time.time() - start_time
        print(f"⏱️  Upload time: {upload_time:.2f}s")
        
        # Test document analysis
        print("\n🧠 Step 2: Testing document analysis...")
        analysis_start = time.time()
        
        test_questions = [
            "Does this policy cover knee surgery?",
            "What is the waiting period for maternity benefits?"
        ]
        
        analysis_payload = {
            "documents": file_url,
            "questions": test_questions
        }
        
        async with session.post(
            'http://localhost:8000/api/v1/hackrx/run',
            json=analysis_payload,
            headers={'Content-Type': 'application/json'}
        ) as response:
            if response.status == 200:
                result = await response.json()
                analysis_time = time.time() - analysis_start
                
                print(f"✅ Analysis completed successfully!")
                print(f"⏱️  Analysis time: {analysis_time:.2f}s")
                print(f"📊 Processing summary:")
                print(f"   - Questions processed: {result['processing_summary']['total_questions']}")
                print(f"   - Successful responses: {result['processing_summary']['successful_responses']}")
                print(f"   - Total processing time: {result['processing_summary']['total_processing_time']}")
                
                print(f"\n📋 Sample Results:")
                for i, answer in enumerate(result['answers'][:2]):  # Show first 2 answers
                    print(f"\n   Question {i+1}: {answer['question']}")
                    print(f"   Coverage: {'✅ Covered' if answer['isCovered'] else '❌ Not Covered'}")
                    print(f"   Confidence: {answer['confidence_score']:.1%}")
                    print(f"   Rationale: {answer['rationale'][:100]}...")
                
                total_time = time.time() - start_time
                print(f"\n🎯 Total Test Time: {total_time:.2f}s")
                
                if total_time < 30:  # Should be much faster now
                    print("🎉 OPTIMIZATION SUCCESS: System is now fast and efficient!")
                else:
                    print("⚠️  Still slow - may need further optimization")
                
            else:
                error_text = await response.text()
                print(f"❌ Analysis failed: {response.status}")
                print(f"   Error: {error_text}")
    
    # Cleanup
    import os
    try:
        os.remove('test_policy.txt')
        print("\n🧹 Cleaned up test files")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(test_optimized_system())
