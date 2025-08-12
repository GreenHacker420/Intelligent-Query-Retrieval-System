"""Simple environment check without external dependencies."""

import os

def load_env_file():
    """Load environment variables from .env file."""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
        return env_vars
    except FileNotFoundError:
        print("❌ .env file not found")
        return {}

def check_environment():
    """Check environment configuration."""
    print("🔧 Checking Environment Configuration...\n")
    
    # Load .env file
    env_vars = load_env_file()
    
    if not env_vars:
        print("❌ No environment variables loaded")
        return False
    
    print(f"📁 Loaded {len(env_vars)} variables from .env file\n")
    
    # Check required variables
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API Key',
        'PINECONE_API_KEY': 'Pinecone API Key', 
        'PINECONE_ENVIRONMENT': 'Pinecone Environment',
        'PINECONE_INDEX_NAME': 'Pinecone Index Name'
    }
    
    all_good = True
    
    for var, description in required_vars.items():
        value = env_vars.get(var, '')
        
        if not value:
            print(f"❌ {var} ({description}): Not set")
            all_good = False
        elif var == 'PINECONE_ENVIRONMENT' and value == 'your_pinecone_environment':
            print(f"⚠️  {var} ({description}): Needs to be updated from placeholder")
            print(f"   Current: {value}")
            print(f"   💡 Common values: us-east-1-aws, us-west-2-aws, eu-west-1-aws")
            all_good = False
        elif var in ['GEMINI_API_KEY', 'PINECONE_API_KEY']:
            print(f"✅ {var} ({description}): {value[:20]}...{value[-10:]}")
        else:
            print(f"✅ {var} ({description}): {value}")
    
    print()
    
    # Check optional but useful variables
    optional_vars = {
        'APP_NAME': 'Application Name',
        'DEBUG': 'Debug Mode',
        'MAX_CHUNK_SIZE': 'Maximum Chunk Size',
        'MAX_RETRIEVAL_RESULTS': 'Maximum Retrieval Results'
    }
    
    print("📋 Optional Configuration:")
    for var, description in optional_vars.items():
        value = env_vars.get(var, 'Not set')
        print(f"   {var}: {value}")
    
    print()
    
    # Validate API key formats
    print("🔍 API Key Validation:")
    
    gemini_key = env_vars.get('GEMINI_API_KEY', '')
    if gemini_key:
        if gemini_key.startswith('AIza') and len(gemini_key) > 30:
            print("✅ Gemini API key format looks correct")
        else:
            print("⚠️  Gemini API key format may be incorrect")
            print("   Expected format: AIzaSy... (39 characters)")
    
    pinecone_key = env_vars.get('PINECONE_API_KEY', '')
    if pinecone_key:
        if pinecone_key.startswith('pcsk_') and len(pinecone_key) > 40:
            print("✅ Pinecone API key format looks correct")
        else:
            print("⚠️  Pinecone API key format may be incorrect")
            print("   Expected format: pcsk_... (longer than 40 characters)")
    
    print()
    
    return all_good

def main():
    """Main function."""
    print("🚀 Simple Environment Configuration Check\n")
    
    config_ok = check_environment()
    
    print("=" * 50)
    print("📊 CONFIGURATION STATUS")
    print("=" * 50)
    
    if config_ok:
        print("🎉 Environment configuration looks good!")
        print("\n✅ Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test API connectivity: python test_env_config.py")
        print("3. Run the application: python main.py")
    else:
        print("⚠️  Configuration issues found!")
        print("\n🔧 Required Actions:")
        print("1. Update PINECONE_ENVIRONMENT in .env file")
        print("   - Check your Pinecone dashboard for the correct environment")
        print("   - Common values: us-east-1-aws, us-west-2-aws, eu-west-1-aws")
        print("2. Verify your API keys are correct")
        print("3. Re-run this check: python check_env_simple.py")
    
    print("\n📋 Current .env file status:")
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("❌ .env file missing - copy from .env.template")
    
    return 0 if config_ok else 1

if __name__ == "__main__":
    exit(main())
