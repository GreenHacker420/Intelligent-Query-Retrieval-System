#!/usr/bin/env python3
"""Check available Pinecone environments and help configure the correct one."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_pinecone_environments():
    """Check available Pinecone environments."""
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            print("❌ PINECONE_API_KEY not found in environment")
            return
        
        print("🔍 Checking Pinecone environments...")
        print(f"📋 API Key: {api_key[:20]}...")
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        
        # List available indexes to understand the environment
        print("\n📊 Available indexes:")
        try:
            indexes = pc.list_indexes()
            if indexes.indexes:
                for idx in indexes.indexes:
                    print(f"  ✅ Index: {idx.name}")
                    print(f"     Host: {idx.host}")
                    print(f"     Spec: {idx.spec}")
                    print()
            else:
                print("  📝 No indexes found (this is normal for new accounts)")
        except Exception as e:
            print(f"  ❌ Error listing indexes: {e}")
        
        # Try to create a test index to determine available environments
        print("🧪 Testing available environments...")
        
        # Common Pinecone environments to test
        test_environments = [
            "us-east-1-aws",
            "us-west-2-aws", 
            "eu-west-1-aws",
            "asia-southeast-1-aws",
            "us-central1-gcp",
            "europe-west1-gcp",
            "asia-northeast1-gcp"
        ]
        
        working_env = None
        
        for env in test_environments:
            try:
                print(f"  🔍 Testing {env}...")
                
                # Try to create a test index (we'll delete it immediately)
                from pinecone import ServerlessSpec
                
                test_index_name = "test-env-check"
                
                # Try to create index with this environment
                pc.create_index(
                    name=test_index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws" if "aws" in env else "gcp",
                        region=env
                    )
                )
                
                print(f"  ✅ {env} - WORKING!")
                working_env = env
                
                # Clean up test index
                try:
                    pc.delete_index(test_index_name)
                    print(f"  🧹 Cleaned up test index")
                except:
                    pass
                
                break  # Found working environment
                
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "404" in error_msg:
                    print(f"  ❌ {env} - Not available")
                elif "already exists" in error_msg:
                    print(f"  ✅ {env} - Available (test index already exists)")
                    working_env = env
                    break
                elif "quota" in error_msg or "limit" in error_msg:
                    print(f"  ⚠️  {env} - Available but quota exceeded")
                    working_env = env
                    break
                else:
                    print(f"  ❓ {env} - Error: {e}")
        
        if working_env:
            print(f"\n🎉 Found working environment: {working_env}")
            print(f"\n🔧 Update your .env file:")
            print(f"PINECONE_ENVIRONMENT={working_env}")
            
            # Update .env file automatically
            update_env_file(working_env)
            
        else:
            print("\n❌ No working environments found.")
            print("💡 This might be because:")
            print("   - Your Pinecone account is in a different region")
            print("   - You need to check your Pinecone dashboard for available regions")
            print("   - Your API key might not have the right permissions")
            
            print("\n🔗 Please check your Pinecone dashboard at: https://app.pinecone.io/")
            
    except ImportError:
        print("❌ Pinecone package not installed")
        print("💡 Install with: pip install pinecone")
    except Exception as e:
        print(f"❌ Error checking Pinecone: {e}")

def update_env_file(working_env):
    """Update the .env file with the working environment."""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update the PINECONE_ENVIRONMENT line
        updated_lines = []
        env_updated = False
        
        for line in lines:
            if line.startswith('PINECONE_ENVIRONMENT='):
                updated_lines.append(f'PINECONE_ENVIRONMENT={working_env}\n')
                env_updated = True
            else:
                updated_lines.append(line)
        
        # If PINECONE_ENVIRONMENT wasn't found, add it
        if not env_updated:
            updated_lines.append(f'PINECONE_ENVIRONMENT={working_env}\n')
        
        # Write back to .env file
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated .env file with PINECONE_ENVIRONMENT={working_env}")
        
    except Exception as e:
        print(f"⚠️  Could not update .env file automatically: {e}")
        print(f"💡 Please manually update PINECONE_ENVIRONMENT={working_env} in your .env file")

def main():
    """Main function."""
    print("🔧 Pinecone Environment Checker")
    print("=" * 40)
    
    check_pinecone_environments()
    
    print("\n" + "=" * 40)
    print("✅ Environment check complete!")

if __name__ == "__main__":
    main()
