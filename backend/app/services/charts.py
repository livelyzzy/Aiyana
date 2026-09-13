"""报表图表生成（matplotlib -> PNG 字节）。"""
from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# 中文字体：优先 Windows 常用字体，跨平台回退
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


def radar_chart(labels: list[str], values: list[float], title: str) -> bytes:
    """雷达图，展示多维度得分。"""
    import numpy as np

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    values = values + values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw={"polar": True})
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_title(title, pad=20)
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def bar_chart(labels: list[str], values: list[float], title: str) -> bytes:
    """柱状图，展示班级/课程维度分布。"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, values, color="#4C78A8")
    ax.set_title(title)
    ax.set_ylabel("分数")
    ax.set_ylim(0, 100)
    for i, v in enumerate(values):
        ax.text(i, v + 1, str(v), ha="center", fontsize=9)
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
