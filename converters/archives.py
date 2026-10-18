import asyncio, tarfile, zipfile
from pathlib import Path
import py7zr
from utils.security import safe_join

MAX_FILES=1000
MAX_EXTRACTED=500*1024*1024

def _validate(names_sizes, outdir):
    total=0
    for name,size in names_sizes:
        safe_join(outdir,name)
        total += max(0,size or 0)
        if total>MAX_EXTRACTED: raise ValueError("Archive expands beyond safety limit")

async def list_contents(src: Path):
    def work():
        n=src.name.lower()
        if n.endswith(".zip"):
            with zipfile.ZipFile(src) as z:return [(i.filename,i.file_size) for i in z.infolist()[:MAX_FILES]]
        if n.endswith(".7z"):
            with py7zr.SevenZipFile(src) as z:return [(x.filename,getattr(x,"uncompressed",0) or 0) for x in z.list()[:MAX_FILES]]
        with tarfile.open(src) as t:return [(m.name,m.size) for m in t.getmembers()[:MAX_FILES]]
    return await asyncio.to_thread(work)

async def extract(src: Path, outdir: Path):
    def work():
        items=asyncio.run(list_contents(src)) if False else None
        n=src.name.lower()
        if n.endswith(".zip"):
            with zipfile.ZipFile(src) as z:
                infos=z.infolist()
                if len(infos)>MAX_FILES: raise ValueError("Too many files")
                _validate([(i.filename,i.file_size) for i in infos],outdir)
                for i in infos:
                    target=safe_join(outdir,i.filename)
                    if i.is_dir(): target.mkdir(parents=True,exist_ok=True); continue
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(i) as a, target.open("wb") as b:
                        b.write(a.read(MAX_EXTRACTED+1))
        elif n.endswith(".7z"):
            with py7zr.SevenZipFile(src) as z:
                infos=z.list()
                if len(infos)>MAX_FILES: raise ValueError("Too many files")
                _validate([(x.filename,getattr(x,"uncompressed",0) or 0) for x in infos],outdir)
                z.extractall(outdir)
        else:
            with tarfile.open(src) as t:
                ms=t.getmembers()
                if len(ms)>MAX_FILES: raise ValueError("Too many files")
                _validate([(m.name,m.size) for m in ms],outdir)
                for m in ms:
                    target=safe_join(outdir,m.name)
                    if m.isdir(): target.mkdir(parents=True,exist_ok=True)
                    elif m.isfile():
                        target.parent.mkdir(parents=True,exist_ok=True)
                        f=t.extractfile(m)
                        if f:
                            data=f.read(MAX_EXTRACTED+1)
                            if len(data)>MAX_EXTRACTED: raise ValueError("File too large")
                            target.write_bytes(data)
    await asyncio.to_thread(work)
