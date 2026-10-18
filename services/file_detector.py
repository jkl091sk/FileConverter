from dataclasses import dataclass
from pathlib import Path
import filetype

EXT_KIND = {
"png":"image","jpg":"image","jpeg":"image","webp":"image","bmp":"image","tif":"image","tiff":"image","gif":"image",
"mp3":"audio","wav":"audio","ogg":"audio","flac":"audio","aac":"audio","m4a":"audio",
"mp4":"video","webm":"video","mov":"video","mkv":"video","avi":"video",
"docx":"document","odt":"document","rtf":"document","txt":"document","html":"document","htm":"document",
"pdf":"pdf","zip":"archive","7z":"archive","tar":"archive","gz":"archive","tar.gz":"archive"
}
@dataclass
class Detected:
    ext: str
    mime: str
    kind: str

def detect(path: Path, original_name: str) -> Detected:
    low=original_name.lower()
    ext="tar.gz" if low.endswith(".tar.gz") else Path(original_name).suffix.lower().lstrip(".")
    head=path.read_bytes()[:8192]
    guess=filetype.guess(str(path))
    mime=guess.mime if guess else "application/octet-stream"
    expected=EXT_KIND.get(ext,"unknown")

    if ext=="pdf": return Detected(ext,"application/pdf","pdf" if head.startswith(b"%PDF-") else "unknown")
    if ext=="docx": return Detected(ext,mime,"document" if head.startswith(b"PK") else "unknown")
    if ext=="odt": return Detected(ext,mime,"document" if head.startswith(b"PK") else "unknown")
    if ext=="rtf": return Detected(ext,mime,"document" if head.lstrip().startswith(b"{\\rtf") else "unknown")
    if ext in {"txt","html","htm"}:
        try: head.decode("utf-8")
        except UnicodeDecodeError:
            try: head.decode("cp1252")
            except UnicodeDecodeError: return Detected(ext,mime,"unknown")
        return Detected(ext,mime,"document")
    if ext=="zip": return Detected(ext,mime,"archive" if head.startswith(b"PK") else "unknown")
    if ext=="7z": return Detected(ext,mime,"archive" if head.startswith(b"7z\xbc\xaf\x27\x1c") else "unknown")
    if ext in {"tar","tar.gz","gz"}: return Detected(ext,mime,"archive")

    if expected in {"image","audio","video"}:
        if not guess: return Detected(ext,mime,"unknown")
        family=guess.mime.split("/",1)[0]
        valid=(expected=="image" and family=="image") or (expected=="audio" and family in {"audio","video"}) or (expected=="video" and family=="video")
        return Detected(ext,mime,expected if valid else "unknown")
    return Detected(ext,mime,"unknown")

def outputs(d: Detected):
    e=d.ext
    if d.kind=="image": return [x for x in ["png","jpg","webp","bmp","tiff","gif","pdf"] if x!=e]
    if d.kind=="audio": return [x for x in ["mp3","wav","ogg","flac","aac","m4a"] if x!=e]
    if d.kind=="video": return [x for x in ["mp4","webm","mov","mkv","avi","gif","mp3","wav"] if x!=e]
    if d.kind=="document":
        matrix={"docx":["pdf","txt","odt","rtf","html"],"odt":["pdf","docx","txt","rtf","html"],
        "rtf":["pdf","docx","odt","txt","html"],"txt":["pdf","docx","odt","rtf","html"],
        "html":["pdf","docx","odt","rtf","txt"],"htm":["pdf","docx","odt","rtf","txt"]}
        return matrix.get(e,[])
    if d.kind=="pdf": return ["txt","images","compress","split","extract"]
    if d.kind=="archive": return ["list","extract"]
    return []
