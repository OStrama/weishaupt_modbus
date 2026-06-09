"""Pytest configuration file."""

from pathlib import Path
import sys

# Add the project root to the Python path so tests can import custom_components
sys.path.insert(0, str(Path(__file__).parent))
