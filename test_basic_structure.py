"""Basic structure test without requiring external dependencies."""

import sys
import os
import importlib.util

def test_file_structure():
    """Test that all required files exist."""
    print("🔍 Testing File Structure...\n")
    
    required_files = [
        "requirements.txt",
        ".env.template",
        "main.py",
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/config.py",
        "src/core/gemini_client.py",
        "src/services/__init__.py",
        "src/services/document_processor.py",
        "src/services/vector_store.py",
        "src/services/retrieval_engine.py",
        "src/api/__init__.py",
        "src/api/main.py",
        "src/api/models/__init__.py",
        "src/api/models/request.py",
        "src/api/models/response.py",
        "src/api/routes/__init__.py",
        "src/api/routes/hackrx.py",
        "prd/idea.md",
        "prd/ques.md",
        "prd/plan.md",
        "README.md",
        "IMPLEMENTATION_CHECKLIST.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    print(f"\n📊 File Structure: {len(required_files) - len(missing_files)}/{len(required_files)} files present")
    return len(missing_files) == 0


def test_python_syntax():
    """Test that all Python files have valid syntax."""
    print("\n🐍 Testing Python Syntax...\n")
    
    python_files = [
        "main.py",
        "src/core/config.py",
        "src/core/gemini_client.py",
        "src/services/document_processor.py",
        "src/services/vector_store.py",
        "src/services/retrieval_engine.py",
        "src/api/main.py",
        "src/api/models/request.py",
        "src/api/models/response.py",
        "src/api/routes/hackrx.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            # Try to compile the source
            compile(source, file_path, 'exec')
            print(f"✅ {file_path}")
            
        except SyntaxError as e:
            print(f"❌ {file_path} - Syntax Error: {e}")
            syntax_errors.append(file_path)
        except FileNotFoundError:
            print(f"❌ {file_path} - File not found")
            syntax_errors.append(file_path)
        except Exception as e:
            print(f"⚠️  {file_path} - Other error: {e}")
    
    print(f"\n📊 Python Syntax: {len(python_files) - len(syntax_errors)}/{len(python_files)} files valid")
    return len(syntax_errors) == 0


def test_import_structure():
    """Test that imports are structured correctly (without actually importing)."""
    print("\n📦 Testing Import Structure...\n")
    
    import_tests = [
        ("src/core/config.py", ["pydantic_settings", "pydantic"]),
        ("src/core/gemini_client.py", ["google.genai", "loguru"]),
        ("src/services/document_processor.py", ["aiohttp", "fitz", "docx"]),
        ("src/services/vector_store.py", ["pinecone"]),
        ("src/api/main.py", ["fastapi", "uvicorn"]),
        ("src/api/models/request.py", ["pydantic"]),
        ("src/api/models/response.py", ["pydantic"])
    ]
    
    import_issues = []
    for file_path, expected_imports in import_tests:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            missing_imports = []
            for imp in expected_imports:
                if f"import {imp}" not in content and f"from {imp}" not in content:
                    missing_imports.append(imp)
            
            if missing_imports:
                print(f"⚠️  {file_path} - Missing imports: {missing_imports}")
                import_issues.append(file_path)
            else:
                print(f"✅ {file_path}")
                
        except FileNotFoundError:
            print(f"❌ {file_path} - File not found")
            import_issues.append(file_path)
    
    print(f"\n📊 Import Structure: {len(import_tests) - len(import_issues)}/{len(import_tests)} files correct")
    return len(import_issues) == 0


def test_configuration_structure():
    """Test configuration file structure."""
    print("\n⚙️ Testing Configuration Structure...\n")
    
    try:
        with open('.env.template', 'r') as f:
            env_content = f.read()
        
        required_vars = [
            "GEMINI_API_KEY",
            "PINECONE_API_KEY",
            "PINECONE_ENVIRONMENT",
            "PINECONE_INDEX_NAME",
            "APP_NAME",
            "DEBUG",
            "MAX_CHUNK_SIZE",
            "MAX_RETRIEVAL_RESULTS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✅ All required environment variables present")
            return True
            
    except FileNotFoundError:
        print("❌ .env.template file not found")
        return False


def test_api_structure():
    """Test API structure and endpoints."""
    print("\n🌐 Testing API Structure...\n")
    
    try:
        with open('src/api/routes/hackrx.py', 'r') as f:
            api_content = f.read()
        
        required_elements = [
            "@router.post",
            "/hackrx/run",
            "QueryRequest",
            "QueryResponse",
            "process_queries"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in api_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing API elements: {missing_elements}")
            return False
        else:
            print("✅ API structure complete")
            return True
            
    except FileNotFoundError:
        print("❌ API route file not found")
        return False


def main():
    """Run all basic structure tests."""
    print("🚀 Starting Basic Structure Tests...\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Import Structure", test_import_structure),
        ("Configuration", test_configuration_structure),
        ("API Structure", test_api_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append(False)
    
    print(f"\n📊 Overall Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All basic structure tests passed!")
        print("\n✅ System Structure Status:")
        print("- All required files are present")
        print("- Python syntax is valid")
        print("- Import structure is correct")
        print("- Configuration is complete")
        print("- API structure is ready")
        print("\n🔧 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure environment: cp .env.template .env")
        print("3. Add API keys to .env file")
        print("4. Test with: python main.py")
    else:
        print("⚠️  Some structure tests failed. Please review the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
