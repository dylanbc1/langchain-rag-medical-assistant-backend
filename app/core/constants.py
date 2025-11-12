"""Global constants and paths."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
PDFS_DIR = DATA_DIR / "pdfs"
CACHE_DIR = DATA_DIR / "cache"

# Default chunking parameters (configurable via .env, with defaults)
DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
MIN_PAGE_CHARACTERS = int(os.getenv("MIN_PAGE_CHARACTERS", "400"))

# Header patterns for cleaning
HEADER_PATTERNS = [
    r"^GUÍA.*",
    r"^Manual.*Cruz Roja.*",
    r"^Referencia Rápida.*",
]

