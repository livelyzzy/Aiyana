"""PDF 文本抽取（基于 PyMuPDF）。"""
import fitz  # PyMuPDF


def parse_pdf(path: str) -> str:
    parts: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            text = page.get_text()
            if text.strip():
                parts.append(text.strip())
    return "\n".join(parts)
