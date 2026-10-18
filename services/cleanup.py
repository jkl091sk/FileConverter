import asyncio, shutil, time
from pathlib import Path
from config import config

async def remove_tree(path: Path):
    await asyncio.to_thread(shutil.rmtree, path, True)

async def cleanup_stale_temp(max_age_hours=12):
    config.temp_directory.mkdir(parents=True, exist_ok=True)
    cutoff=time.time()-max_age_hours*3600
    for p in config.temp_directory.iterdir():
        try:
            if p.is_dir() and p.stat().st_mtime < cutoff:
                await remove_tree(p)
        except OSError:
            pass
