"""LLM Provider 抽象层。"""
from app.services.llm.base import LLMProvider
from app.services.llm.factory import get_llm

__all__ = ["LLMProvider", "get_llm"]
