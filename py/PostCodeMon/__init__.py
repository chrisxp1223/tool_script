"""
PostCodeMon - A modern Python wrapper for Windows CLI tools.

This package provides a comprehensive framework for wrapping legacy Windows
executables with modern Python interfaces, enhanced error handling, logging,
and automation capabilities.
"""

__version__ = "0.1.0"
__author__ = "ChromeOS Hardware Team"
__email__ = "chromeos-hardware@example.com"

from .core.wrapper import ToolWrapper
from .core.config import ConfigManager
from .core.logger import LogManager

__all__ = ["ToolWrapper", "ConfigManager", "LogManager"]