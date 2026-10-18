import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext
from handlers.files import Flow
from services.conversion_manager import convert
from services.cleanup import remove_tree
from database.database import add_history
from services.i18n import t
router=Router()

@router.callback_query(F.data.startswith("cv:"))
async def convert_cb(c: CallbackQuery,state:FSMContext):
    _,token,target=c.data.split(":",2); d=await state.get_data()
    if d.get("token")!=token: return await c.answer("This conversion has expired.",show_alert=True)
    if target=="extract" and d.get("kind")=="pdf":
        await state.set_state(Flow.awaiting_pages); await state.update_data(target=target)
        await c.message.answer("Send page numbers, e.g. 1,3,5-8"); return await c.answer()
    await c.answer(); await _run(c.message,c.from_user.id,state,target)

@router.message(Flow.awaiting_pages)
async def pages(m:Message,state:FSMContext):
    try:
        pages=parse_pages(m.text or "")
        if not pages or len(pages)>100: raise ValueError
    except ValueError:
        return await m.answer("Invalid pages. Example: 1,3,5-8 (max 100 pages).")
    await _run(m,m.from_user.id,state,"extract",pages)

def parse_pages(s):
    out=set()
    for part in s.replace(" ","").split(","):
        if not part: continue
        if "-" in part:
            a,b=map(int,part.split("-",1))
            if b<a or b-a>99: raise ValueError
            out.update(range(a,b+1))
        else: out.add(int(part))
    if any(x<1 for x in out): raise ValueError
    return sorted(out)

async def _run(msg,user_id,state,target,pages=None):
    d=await state.get_data(); work=Path(d["workdir"]); src=Path(d["src"]); out=work/"out"; out.mkdir(exist_ok=True)
    status=await msg.answer("⏳ Converting…")
    try:
        results=await convert(d["kind"],src,out,target,user_id,pages)
        for p in results:
            await msg.answer_document(FSInputFile(p),caption="✅ Conversion complete")
        await add_history(user_id,d["ext"],target,d["name"],results[0].name,d["size"],"success")
        await status.edit_text("✅ Done.")
    except Exception:
        logging.exception("Conversion failed")
        await add_history(user_id,d["ext"],target,d["name"],"",d["size"],"failed")
        await status.edit_text(await t(user_id,"failed"))
    finally:
        await remove_tree(work); await state.clear()
