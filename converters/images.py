import asyncio
from pathlib import Path
from PIL import Image, ImageSequence, ImageFile
Image.MAX_IMAGE_PIXELS = 80_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False

async def convert(src: Path, dst: Path, fmt: str, quality=90, preserve_metadata=True):
    def work():
        with Image.open(src) as im:
            im.verify()
        with Image.open(src) as im:
            savefmt={"jpg":"JPEG","tiff":"TIFF"}.get(fmt,fmt.upper())
            if fmt=="jpg" and im.mode not in ("RGB","L"): im=im.convert("RGB")
            kwargs={}
            if fmt in ("jpg","webp"): kwargs["quality"]=quality
            if preserve_metadata and "exif" in im.info: kwargs["exif"]=im.info["exif"]
            im.save(dst, savefmt, **kwargs)
    await asyncio.to_thread(work)

async def to_pdf(src: Path, dst: Path):
    def work():
        with Image.open(src) as im:
            if im.mode!="RGB": im=im.convert("RGB")
            im.save(dst, "PDF", resolution=100)
    await asyncio.to_thread(work)
