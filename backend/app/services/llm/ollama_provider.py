"""Ollama 本地 Provider。"""
import httpx

from app.core.config import settings
from app.services.llm.base import LLMError, LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        payload: dict = {"model": self.model, "messages": messages, "stream": False}
        if json_mode:
            payload["format"] = "json"

        url = f"{self.base_url}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise LLMError(
                f"本地模型调用失败（请确认 Ollama 已启动且已拉取模型 {self.model}）：{exc}"
            ) from exc

        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise LLMError(f"本地模型响应格式异常：{data}") from exc
