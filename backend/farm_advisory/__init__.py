"""
SmartAgri Farm Advisory Module
==============================
Unified backend integration for voice recognition, AI advisory, and multilingual support.

Exports:
- router: FastAPI router for voice endpoints
- Voice processing functions from index.py
"""

# FastAPI router for voice endpoints
from .router import router

__all__ = [
    "router",
]
