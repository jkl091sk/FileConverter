import json
from pathlib import Path
from database.database import get_settings
_cache={}
def _load(lang):
    if lang not in _cache:
        p=Path(__file__).parent.parent/"locales"/f"{lang}.json"
        _cache[lang]=json.loads(p.read_text(encoding="utf-8"))
    return _cache[lang]
async def t(user_id,key):
    lang=(await get_settings(user_id)).language
    return _load(lang).get(key,_load("en").get(key,key))
