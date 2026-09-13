"""LLM 抽象基类：所有 Provider（本地/云端）统一实现该接口。

业务层只依赖 `LLMProvider.chat()`，从而在 Ollama（本地）与 OpenAI 兼容
（云端）之间无缝切换。
"""
import json
import re
from abc import ABC, abstractmethod


class LLMError(RuntimeError):
    """LLM 调用失败。"""


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        """发送多轮消息，返回文本回复。json_mode=True 时要求模型输出 JSON。"""

    async def chat_json(self, messages: list[dict]) -> dict:
        """调用并解析 JSON 回复（自动剥离 ```json 代码块）。"""
        raw = await self.chat(messages, json_mode=True)
        return self._extract_json(raw)

    @staticmethod
    def _extract_json(raw: str) -> dict:
        text = raw.strip()
        # 剥离 markdown 代码围栏
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence:
            text = fence.group(1).strip()
        # 截取首个 JSON 对象
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise LLMError(f"无法从模型输出中解析 JSON：{raw[:200]}")
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:  # noqa: BLE001
            raise LLMError(f"JSON 解析失败：{exc}") from exc
