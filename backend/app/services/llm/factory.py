"""LLM Provider 工厂：根据配置返回单例实例。"""
from functools import lru_cache

from app.core.config import settings
from app.services.llm.base import LLMError, LLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_provider import OpenAIProvider


@lru_cache
def get_llm() -> LLMProvider:
    """返回配置指定的 Provider 单例。

    如需接入新模型（如文心一言、ChatGLM 云端），在此新增分支即可。
    """
    provider = settings.llm_provider.lower()
    if provider == "ollama":
        return OllamaProvider()
    if provider in ("openai", "qwen", "deepseek"):
        return OpenAIProvider()
    raise LLMError(f"未知的 LLM_PROVIDER：{settings.llm_provider}")
