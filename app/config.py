from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"


CATALOG_PATH = DATA_DIR / "catalog.json"

FAISS_PATH = DATA_DIR / "catalog.faiss"

EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"


# Retrieval configuration
RETRIEVAL_TOP_K = 20  # Raw candidates retrieved (before ranking)
TOP_K = 5              # Final recommendations after ranking

# Logging configuration
LOG_LEVEL = "INFO"

API_TITLE = "Assessment Recommendation API"

API_VERSION = "1.0.0"

API_DESCRIPTION = """
SHL-style assessment recommendation service.

Features:
- Intent detection
- Query parsing
- Semantic retrieval
- Assessment recommendations
"""