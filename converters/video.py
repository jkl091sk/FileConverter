import asyncio
from pathlib import Path
from config import config
async def convert(src: Path, dst: Path, fmt: str, preserve_metadata=True):
    args=["ffmpeg","-y","-v","error","-i",str(src)]
    if not preserve_metadata: args += ["-map_metadata","-1"]
    if fmt=="mp3": args += ["-vn","-codec:a","libmp3lame","-q:a","2"]
    elif fmt=="wav": args += ["-vn","-codec:a","pcm_s16le"]
    elif fmt=="gif": args += ["-vf","fps=12,scale=720:-1:flags=lanczos"]
    elif fmt=="webm": args += ["-c:v","libvpx-vp9","-crf","32","-b:v","0","-c:a","libopus"]
    elif fmt=="mp4": args += ["-c:v","libx264","-preset","medium","-crf","23","-c:a","aac"]
    args += [str(dst)]
    p=await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try: _,err=await asyncio.wait_for(p.communicate(), config.ffmpeg_timeout)
    except asyncio.TimeoutError:
        p.kill(); await p.wait(); raise RuntimeError("FFmpeg timeout")
    if p.returncode: raise RuntimeError(err.decode(errors="replace")[-1200:])
