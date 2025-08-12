"""Test environment configuration and API connectivity."""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_api():
    """Test Gemini API connectivity."""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...")
        
        # Try to import and test Gemini
        try:
            from google import genai
            
            client = genai.Client(api_key=api_key)
            print("✅ Gemini client created successfully")
            
            # Test a simple generation
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Say 'Hello from Gemini!' if you can read this."
            )
            
            print(f"✅ Gemini API test successful: {response.text[:50]}...")
            return True
            
        except ImportError:
            print("⚠️  google-genai package not installed, but API key is configured")
            return True
        except Exception as e:
            print(f"❌ Gemini API test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini test error: {e}")
        return False

def test_pinecone_config():
    """Test Pinecone configuration."""
    try:
        api_key = os.getenv('PINECONE_API_KEY')
        environment = os.getenv('PINECONE_ENVIRONMENT')
        index_name = os.getenv('PINECONE_INDEX_NAME')
        
        if not api_key:
            print("❌ PINECONE_API_KEY not found")
            return False
        
        print(f"✅ PINECONE_API_KEY found: {api_key[:20]}...")
        print(f"📍 PINECONE_ENVIRONMENT: {environment}")
        print(f"📋 PINECONE_INDEX_NAME: {index_name}")
        
        if environment == "your_pinecone_environment":
            print("⚠️  PINECONE_ENVIRONMENT needs to be updated!")
            print("💡 Common Pinecone environments:")
            print("   - us-east-1-aws")
            print("   - us-west-2-aws") 
            print("   - eu-west-1-aws")
            print("   - asia-southeast-1-aws")
            print("   Check your Pinecone dashboard for the correct environment")
            return False
        
        # Try to test Pinecone connection
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=api_key)
            indexes = pc.list_indexes()
            print(f"✅ Pinecone connection successful")
            print(f"📊 Available indexes: {[idx.name for idx in indexes.indexes]}")
            
            if index_name not in [idx.name for idx in indexes.indexes]:
                print(f"⚠️  Index '{index_name}' doesn't exist yet (will be created automatically)")
            else:
                print(f"✅ Index '{index_name}' already exists")
            
            return True
            
        except ImportError:
            print("⚠️  pinecone package not installed, but API key is configured")
            return True
        except Exception as e:
            print(f"❌ Pinecone connection failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Pinecone test error: {e}")
        return False

def test_all_env_vars():
    """Test all environment variables."""
    print("🔧 Testing Environment Configuration...\n")
    
    required_vars = [
        'GEMINI_API_KEY',
        'PINECONE_API_KEY', 
        'PINECONE_ENVIRONMENT',
        'PINECONE_INDEX_NAME',
        'APP_NAME',
        'MAX_CHUNK_SIZE',
        'MAX_RETRIEVAL_RESULTS'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print(f"\n📊 Environment Status: {len(required_vars) - len(missing_vars)}/{len(required_vars)} variables set")
    
    return len(missing_vars) == 0

async def main():
    """Run all environment tests."""
    print("🚀 Environment Configuration Test\n")
    
    # Test basic environment variables
    env_ok = test_all_env_vars()
    print()
    
    # Test API connections
    print("🌐 Testing API Connectivity...\n")
    
    gemini_ok = await test_gemini_api()
    print()
    
    pinecone_ok = test_pinecone_config()
    print()
    
    # Summary
    print("=" * 50)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 50)
    
    if env_ok and gemini_ok and pinecone_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your environment is fully configured")
        print("🚀 Ready to run: python main.py")
    else:
        print("⚠️  Configuration Issues Found:")
        if not env_ok:
            print("   - Missing environment variables")
        if not gemini_ok:
            print("   - Gemini API issues")
        if not pinecone_ok:
            print("   - Pinecone configuration issues")
        
        print("\n🔧 Next Steps:")
        if not pinecone_ok:
            print("1. Update PINECONE_ENVIRONMENT in .env file")
            print("2. Check your Pinecone dashboard for the correct environment")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Re-run this test: python test_env_config.py")

if __name__ == "__main__":
    asyncio.run(main())
