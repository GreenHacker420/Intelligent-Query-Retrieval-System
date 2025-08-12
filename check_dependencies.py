"""Check if all required dependencies are available."""

import sys
import importlib

def check_dependency(module_name, package_name=None):
    """Check if a dependency is available."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name} - Not installed")
        return False

def main():
    """Check all dependencies."""
    print("🔍 Checking Dependencies...\n")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        ("google.genai", "Google GenAI"),
        ("pinecone", "Pinecone"),
        ("fitz", "PyMuPDF"),
        ("docx", "python-docx"),
        ("aiohttp", "aiohttp"),
        ("loguru", "Loguru"),
        ("dotenv", "python-dotenv"),
    ]
    
    results = []
    for module, name in dependencies:
        result = check_dependency(module, name)
        results.append(result)
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} dependencies available")
    
    if all(results):
        print("🎉 All dependencies are installed!")
        return 0
    else:
        print("\n💡 To install missing dependencies:")
        print("pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
