"""
Configuration module for the housing finance advisor application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

# Application Configuration
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
POLICY_DATA_DIR = DATA_DIR / "policies"
VECTOR_DB_PATH = DATA_DIR / "vector_db"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, POLICY_DATA_DIR, VECTOR_DB_PATH, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Agent Configuration
AGENT_CONFIG = {
    "max_iterations": 10,
    "verbose": True,
    "return_intermediate_steps": True,
}

# Tool Configuration
TOOL_CONFIG = {
    "policy_lookup": {
        "use_rag": True,
        "top_k": 5,
    },
    "cost_calculator": {
        "enable_validation": True,
    },
    "report_generator": {
        "template_dir": PROJECT_ROOT / "templates",
        "output_format": "markdown",  # Options: markdown, pdf, html
    },
}
