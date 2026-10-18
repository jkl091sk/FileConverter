from pathlib import Path
def safe_join(base: Path, member: str) -> Path:
    base = base.resolve()
    target = (base / member).resolve()
    if target != base and base not in target.parents:
        raise ValueError("Unsafe archive path")
    return target
