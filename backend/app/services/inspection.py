"""智能核查服务：对比任务要求与成果内容，识别偏离项、逻辑漏洞与缺失步骤。"""
from app.services.llm import get_llm
from app.services.llm.prompts import build_inspect_messages
from app.services.structuring import load_content_text


async def run_inspection(requirements: str, parsed_content: str | None) -> dict:
    """执行核查，返回结构化发现（deviations/logic_issues/missing_steps/overall）。"""
    content = load_content_text(parsed_content)
    if not content.strip():
        return {
            "deviations": [],
            "logic_issues": [],
            "missing_steps": [],
            "overall": "未解析到成果内容，无法核查。",
        }
    llm = get_llm()
    result = await llm.chat_json(build_inspect_messages(requirements, content))
    for key in ("deviations", "logic_issues", "missing_steps"):
        result.setdefault(key, [])
    result.setdefault("overall", "")
    return result
