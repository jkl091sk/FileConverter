import asyncio, shutil, zipfile
from pathlib import Path
from converters import images,audio,video,documents,pdf,archives
from database.database import get_settings

async def convert(kind, src: Path, outdir: Path, target: str, user_id: int, pages=None):
    s=await get_settings(user_id)
    stem=src.stem
    if kind=="image":
        dst=outdir/f"{stem}.{target}"
        if target=="pdf": await images.to_pdf(src,dst)
        else: await images.convert(src,dst,target,s.image_quality,s.preserve_metadata)
        return [dst]
    if kind=="audio":
        dst=outdir/f"{stem}.{target}"; await audio.convert(src,dst,s.audio_quality,s.preserve_metadata); return [dst]
    if kind=="video":
        dst=outdir/f"{stem}.{target}"; await video.convert(src,dst,target,s.preserve_metadata); return [dst]
    if kind=="document":
        return [await documents.convert(src,outdir,target)]
    if kind=="pdf":
        if target=="txt":
            dst=outdir/f"{stem}.txt"; await pdf.to_text(src,dst); return [dst]
        if target=="compress":
            dst=outdir/f"{stem}_compressed.pdf"; await pdf.compress(src,dst); return [dst]
        if target=="extract":
            dst=outdir/f"{stem}_pages.pdf"; await pdf.extract(src,dst,pages or []); return [dst]
        folder=outdir/target; folder.mkdir()
        result=await (pdf.to_images(src,folder) if target=="images" else pdf.split(src,folder))
        z=outdir/f"{stem}_{target}.zip"
        await asyncio.to_thread(_zip_files,z,result,folder)
        return [z]
    if kind=="archive":
        if target=="list":
            items=await archives.list_contents(src)
            dst=outdir/f"{stem}_contents.txt"
            dst.write_text("\n".join(f"{n} ({size} bytes)" for n,size in items),encoding="utf-8")
            return [dst]
        folder=outdir/"extracted"; folder.mkdir()
        await archives.extract(src,folder)
        z=outdir/f"{stem}_extracted.zip"
        files=[p for p in folder.rglob("*") if p.is_file()]
        await asyncio.to_thread(_zip_files,z,files,folder)
        return [z]
    raise ValueError("Unsupported conversion")

def _zip_files(dst, files, base):
    with zipfile.ZipFile(dst,"w",zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(base))
