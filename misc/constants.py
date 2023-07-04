from pathlib import Path
from tempfile import gettempdir


temp_dir = Path(gettempdir(), "kruase")
if not temp_dir.exists():
    temp_dir.mkdir()
