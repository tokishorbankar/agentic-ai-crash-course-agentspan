from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# Constants for package and workspace roots
PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parent
WORKSPACE_ROOT: Final[Path] = PACKAGE_ROOT.parent.parent


# Load environment variables from .env file if it exists
@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    tavily_api_key: str
    calculator_mcp_url: str
    mcp_server_script: Path
    project_root: Path
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8000


# Utility functions to load environment variables and configuration
def _load_dotenv() -> None:
    dotenv_path = WORKSPACE_ROOT / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    else:
        load_dotenv(override=False)


# Function to ensure required environment variables are set
def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is missing. "
            "Set it in your environment or in a .env file."
        )
    return value


# Function to load the application configuration from environment variables
def load_config() -> AppConfig:
    _load_dotenv()

    return AppConfig(
        openai_api_key=_required_env("OPENAI_API_KEY"),
        tavily_api_key=_required_env("TAVILY_API_KEY"),
        calculator_mcp_url=os.getenv("CALCULATOR_MCP_URL", "http://localhost:8000/mcp"),
        mcp_server_script=PACKAGE_ROOT / "mcp" / "mcp-server.py",
        project_root=WORKSPACE_ROOT,
    )
