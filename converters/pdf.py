import asyncio
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import fitz

async def to_text(src: Path, dst: Path):
    def work():
        r=PdfReader(src)
        dst.write_text("\n\n".join((p.extract_text() or "") for p in r.pages), encoding="utf-8")
    await asyncio.to_thread(work)

async def to_images(src: Path, outdir: Path) -> list[Path]:
    def work():
        doc=fitz.open(src); result=[]
        if doc.page_count>100: raise ValueError("PDF has too many pages (max 100)")
        for i,p in enumerate(doc):
            target=outdir/f"page_{i+1:03}.png"
            p.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False).save(target)
            result.append(target)
        doc.close(); return result
    return await asyncio.to_thread(work)

async def compress(src: Path, dst: Path):
    def work():
        doc=fitz.open(src)
        doc.save(dst, garbage=4, deflate=True, clean=True)
        doc.close()
    await asyncio.to_thread(work)

async def split(src: Path, outdir: Path) -> list[Path]:
    def work():
        r=PdfReader(src)
        if len(r.pages)>100: raise ValueError("PDF has too many pages (max 100)")
        res=[]
        for i,page in enumerate(r.pages):
            w=PdfWriter(); w.add_page(page); p=outdir/f"page_{i+1:03}.pdf"
            with p.open("wb") as f:w.write(f)
            res.append(p)
        return res
    return await asyncio.to_thread(work)

async def extract(src: Path, dst: Path, pages: list[int]):
    def work():
        r=PdfReader(src); w=PdfWriter()
        for n in pages:
            if n<1 or n>len(r.pages): raise ValueError("Page outside PDF range")
            w.add_page(r.pages[n-1])
        with dst.open("wb") as f:w.write(f)
    await asyncio.to_thread(work)
