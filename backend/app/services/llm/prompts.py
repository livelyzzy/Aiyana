"""Prompt 模板：驱动「智能解析 / 智能核查 / 多维度评价」三大能力。

所有 Prompt 均要求模型输出结构化 JSON，并附带理由（reason），
用于支撑系统「评价结果可解释性」的需求。
"""

SYSTEM_ROLE = (
    "你是大学生软件实训教学成果的评审专家，精通软件开发流程与工程规范。"
    "请严格依据用户提供的材料进行判断，输出格式严格的 JSON，不要输出任何多余文本。"
)

# ---------- 智能内容解析 ----------
PARSE_SYSTEM = SYSTEM_ROLE + (
    "你的任务是从实训成果材料中提取结构化信息。"
    '输出 JSON：{"summary": "...", "key_steps": ["..."], "features": ["..."], '
    '"ui_elements": ["..."], "technologies": ["..."]}'
)

# ---------- 智能核查 ----------
INSPECT_SYSTEM = SYSTEM_ROLE + (
    "你的任务是对比「实训任务要求」与「学生成果内容」，识别问题。"
    '输出 JSON：{"deviations": [{"item": "要求点", "issue": "偏离说明", "severity": "高/中/低"}], '
    '"logic_issues": [{"issue": "...", "reason": "..."}], '
    '"missing_steps": [{"step": "...", "reason": "..."}], "overall": "总体结论"}'
)


def build_parse_messages(content: str) -> list[dict]:
    return [
        {"role": "system", "content": PARSE_SYSTEM},
        {"role": "user", "content": f"请解析以下实训成果材料并提取结构化信息：\n\n{content}"},
    ]


def build_inspect_messages(requirements: str, content: str) -> list[dict]:
    return [
        {"role": "system", "content": INSPECT_SYSTEM},
        {
            "role": "user",
            "content": (
                f"【实训任务要求】\n{requirements}\n\n"
                f"【学生成果内容】\n{content}\n\n"
                "请完成核查并输出 JSON。"
            ),
        },
    ]


def build_evaluate_messages(rubrics: list[dict], content: str) -> list[dict]:
    rubric_text = "\n".join(
        f"- {r['name']}（权重 {r['weight']}）：{r.get('description', '')}" for r in rubrics
    )
    system = SYSTEM_ROLE + (
        "你的任务是按给定评价指标对学生成果进行客观评分（0-100 分）。"
        "对每个指标给出分数和理由。"
        '输出 JSON：{"items": [{"name": "指标名", "score": 0-100, "comment": "评分理由"}]}'
    )
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                f"【评价指标】\n{rubric_text}\n\n【学生成果内容】\n{content}\n\n"
                "请逐项评分并输出 JSON。"
            ),
        },
    ]
