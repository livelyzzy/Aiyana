"""图片 OCR 解析。

默认使用 PaddleOCR（可选依赖）。未安装时抛出明确错误；
生产环境可替换为云端 OCR（百度/阿里）或大模型多模态识别。
"""


def parse_image(path: str) -> str:
    try:
        from paddleocr import PaddleOCR  # type: ignore
    except ImportError as exc:  # noqa: BLE001
        raise RuntimeError(
            "未安装 PaddleOCR，无法解析图片。请先 `pip install paddleocr paddlepaddle`，"
            "或改用云端 OCR / 多模态大模型。"
        ) from exc

    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    result = ocr.ocr(path, cls=True)

    lines: list[str] = []
    for page in result or []:
        for item in page or []:
            # item = [box, (text, confidence)]
            try:
                lines.append(item[1][0])
            except (IndexError, TypeError):
                continue
    return "\n".join(lines)
