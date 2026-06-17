"""Read plain text out of a .docx (or .txt) resume without external dependencies.

A .docx is just a zip with word/document.xml inside. We strip the XML tags and
turn paragraph breaks into newlines. This re-runs on every scan, so updating the
resume file is enough — no re-import step needed.
"""
import html
import os
import re
import zipfile


def read_resume_text(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext in (".docx", ".docm"):
        return _read_docx(path)
    # Unknown format: best-effort plain read
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def _read_docx(path: str) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    except Exception:
        return ""
    # paragraph and line breaks -> newlines so words don't run together
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    return html.unescape(text)
