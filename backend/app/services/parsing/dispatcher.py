"""解析调度器：按扩展名分发到对应解析器。"""
import os

from app.services.parsing.docx_parser import parse_docx
from app.services.parsing.image_parser import parse_image
from app.services.parsing.pdf_parser import parse_pdf

TEXT_EXTENSIONS = {".txt", ".md", ".log", ".py", ".java", ".c", ".cpp", ".js", ".ts", ".html", ".css", ".json"}

PARSERS = {
    ".docx": parse_docx,
    ".pdf": parse_pdf,
    ".png": parse_image,
    ".jpg": parse_image,
    ".jpeg": parse_image,
    ".bmp": parse_image,
}

SUPPORTED_EXTENSIONS = set(PARSERS) | TEXT_EXTENSIONS


def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTENSIONS:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    parser = PARSERS.get(ext)
    if parser is None:
        raise ValueError(f"不支持的文件类型：{ext}")
    return parser(path)
