import sys
import os
import importlib.util
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependency(package):
    try:
        spec = importlib.util.find_spec(package)
        if spec is None:
            return False
        module = importlib.import_module(package)
        logger.info(f"✓ {package} {getattr(module, '__version__', 'unknown version')}")
        return True
    except Exception as e:
        logger.error(f"✗ {package}: {str(e)}")
        return False

def main():
    logger.info("Checking Python environment...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "aiohttp",
        "pydantic",
        "python-dotenv",
        "pandas",
        "plotly",
        "numpy",
        "requests",
        "gtts",
        "groq",
        "cachetools",
        "faiss-cpu",
        "sentence_transformers",
        "whisper",
        "langchain",
        "langchain_community",
        "langchain_huggingface",
        "langgraph",
        "psutil"
    ]
    
    missing_packages = []
    for package in required_packages:
        if not check_dependency(package):
            missing_packages.append(package)
    
    if missing_packages:
        logger.error("\nMissing packages:")
        for package in missing_packages:
            logger.error(f"- {package}")
        logger.error("\nPlease install missing packages using:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        return False
    
    # Check if we can import our own modules
    try:
        from agents import api_agent, analysis_agent
        logger.info("✓ Local modules can be imported")
    except ImportError as e:
        logger.error(f"✗ Cannot import local modules: {e}")
        logger.error("Make sure you're in the correct directory and PYTHONPATH is set correctly")
        return False
    
    logger.info("\nEnvironment check completed successfully!")
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 