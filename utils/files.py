import re
from pathlib import Path
def safe_filename(name: str) -> str:
    name = Path(name or "file").name.replace("\x00", "")
    name = re.sub(r"[\r\n\t/\\]+", "_", name).strip(" .")
    return name[:180] or "file"
def human_size(n: int) -> str:
    x=float(n)
    for u in ("B","KB","MB","GB"):
        if x < 1024 or u=="GB": return f"{x:.1f} {u}"
        x/=1024
