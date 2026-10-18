import asyncio, shutil, os
from pathlib import Path
from config import config

def find_libreoffice():
    exe=shutil.which("libreoffice") or shutil.which("soffice")
    if exe: return exe
    if os.name=="nt":
        for base in (os.environ.get("PROGRAMFILES"),os.environ.get("PROGRAMFILES(X86)")):
            if base:
                p=Path(base)/"LibreOffice/program/soffice.exe"
                if p.exists(): return str(p)
    return None

async def convert(src: Path, outdir: Path, fmt: str) -> Path:
    exe=find_libreoffice()
    if not exe: raise RuntimeError("LibreOffice is not installed.")
    profile=(outdir/"lo_profile").resolve()
    args=[exe,f"-env:UserInstallation={profile.as_uri()}","--headless","--convert-to",fmt,"--outdir",str(outdir),str(src)]
    p=await asyncio.create_subprocess_exec(*args,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    try: out,err=await asyncio.wait_for(p.communicate(),config.conversion_timeout)
    except asyncio.TimeoutError:
        p.kill(); await p.wait(); raise RuntimeError("LibreOffice timeout")
    if p.returncode: raise RuntimeError(err.decode(errors="replace")[-1200:])
    found=[p for p in outdir.iterdir() if p.is_file() and p.suffix.lower()==f".{fmt.lower()}"]
    if not found: raise RuntimeError("LibreOffice did not produce output")
    return max(found,key=lambda p:p.stat().st_mtime)
