from pathlib import Path
from uuid import uuid4

from textract import process

from engine.fb2_processor import process_fb2
from misc.constants import temp_dir


def get_temp_file_path(extension: str = None) -> Path:
    return Path(temp_dir, str(uuid4()) + ("" if extension.startswith(".") else ".") + (extension if extension else ""))


def get_plain_text(path: Path) -> str:
    if path.suffix == ".fb2":
        return process_fb2(path)
    else:
        return process(str(path), output_encoding="utf-8").decode("utf-8").replace(chr(160), " ")
