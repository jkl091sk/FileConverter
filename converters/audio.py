import asyncio
from pathlib import Path
from config import config
BITRATES={"low":"96k","medium":"192k","high":"320k"}
async def convert(src: Path, dst: Path, quality="medium", preserve_metadata=True):
    args=["ffmpeg","-y","-v","error","-i",str(src)]
    if not preserve_metadata: args += ["-map_metadata","-1"]
    args += ["-b:a",BITRATES.get(quality,"192k"),str(dst)]
    p=await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try: _,err=await asyncio.wait_for(p.communicate(), config.ffmpeg_timeout)
    except asyncio.TimeoutError:
        p.kill(); await p.wait(); raise RuntimeError("FFmpeg timeout")
    if p.returncode: raise RuntimeError(err.decode(errors="replace")[-1200:])
