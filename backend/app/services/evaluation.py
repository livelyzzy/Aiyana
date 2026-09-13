"""多维度评价服务：基于指标调用 LLM 客观评分，并支持教师主观调整。"""
from app.services.llm import get_llm
from app.services.llm.prompts import build_evaluate_messages
from app.services.structuring import load_content_text


async def run_ai_evaluation(rubrics: list[dict], parsed_content: str | None) -> list[dict]:
    """对给定指标逐项 AI 评分，返回 [{name, score, comment}, ...]。"""
    content = load_content_text(parsed_content)
    if not rubrics:
        return []
    if not content.strip():
        return [{"name": r["name"], "score": 0, "comment": "无成果内容可评估"} for r in rubrics]

    llm = get_llm()
    result = await llm.chat_json(build_evaluate_messages(rubrics, content))
    items = result.get("items", [])
    if not isinstance(items, list):
        return []
    return items


def compute_total(scores: list[dict], rubrics: list[dict]) -> float:
    """按权重汇总总分（教师分优先于 AI 分）。"""
    weight_map = {r["id"]: r.get("weight", 1.0) for r in rubrics}
    total_weight = 0.0
    weighted_sum = 0.0
    for s in scores:
        w = float(weight_map.get(s.get("rubric_id"), 1.0) or 1.0)
        score = s.get("teacher_score") if s.get("teacher_score") is not None else s.get("ai_score")
        if score is None:
            continue
        total_weight += w
        weighted_sum += float(score) * w
    return round(weighted_sum / total_weight, 2) if total_weight else 0.0
