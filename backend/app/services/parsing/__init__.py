"""文件解析服务：docx / pdf / 图片 OCR -> 纯文本。"""
from app.services.parsing.dispatcher import extract_text

__all__ = ["extract_text"]
