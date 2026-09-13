"""智能内容解析：用 LLM 将原始文本抽取为结构化数据。"""
import json

from app.services.llm import get_llm
from app.services.llm.prompts import build_parse_messages

RAW_TEXT_LIMIT = 8000  # 截断超长文本，控制 token 开销


def _truncate(text: str, limit: int = RAW_TEXT_LIMIT) -> str:
    return text if len(text) <= limit else text[:limit] + "\n...(已截断)"


async def structure_content(raw_text: str) -> dict:
    """对原始文本做结构化抽取，返回 dict（summary/key_steps/features/ui_elements/technologies）。"""
    if not raw_text.strip():
        return {
            "summary": "",
            "key_steps": [],
            "features": [],
            "ui_elements": [],
            "technologies": [],
        }
    llm = get_llm()
    result = await llm.chat_json(build_parse_messages(_truncate(raw_text)))
    # 归一化字段
    for key in ("key_steps", "features", "ui_elements", "technologies"):
        if key not in result:
            result[key] = []
        if not isinstance(result[key], list):
            result[key] = [str(result[key])]
    result["raw_text"] = _truncate(raw_text)
    return result


def load_content_text(parsed_content: str | None) -> str:
    """从 parsed_content（结构化 JSON 或纯文本）中取出供 LLM 使用的文本。"""
    if not parsed_content:
        return ""
    try:
        data = json.loads(parsed_content)
        if isinstance(data, dict):
            return data.get("raw_text") or json.dumps(data, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        pass
    return parsed_content
