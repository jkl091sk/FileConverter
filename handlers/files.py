import logging, uuid
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from utils.files import safe_filename, human_size
from services.file_detector import detect, outputs
from services.cleanup import remove_tree
from keyboards.conversion import conversion_keyboard
from services.i18n import t

router=Router()
class Flow(StatesGroup):
    awaiting_choice=State()
    awaiting_pages=State()

def attachment(m: Message):
    for obj in (m.document,m.video,m.audio,m.animation,m.photo[-1] if m.photo else None):
        if obj: return obj
    return None

@router.message(Command("cancel"))
async def cancel(m: Message,state:FSMContext):
    d=await state.get_data()
    if d.get("workdir"): await remove_tree(Path(d["workdir"]))
    await state.clear(); await m.answer("Cancelled.")

@router.message(F.document | F.video | F.audio | F.animation | F.photo)
async def receive(m: Message, bot: Bot, state: FSMContext):
    old=await state.get_data()
    if old.get("workdir"): await remove_tree(Path(old["workdir"]))
    await state.clear()
    obj=attachment(m); size=getattr(obj,"file_size",0) or 0
    if size>config.max_file_size: return await m.answer(await t(m.from_user.id,"too_large"))
    token=uuid.uuid4().hex[:10]; work=config.temp_directory/f"{m.from_user.id}_{token}"; work.mkdir(parents=True,exist_ok=False)
    try:
        rawname=getattr(obj,"file_name",None) or (f"photo_{obj.file_unique_id}.jpg" if m.photo else f"file_{obj.file_unique_id}")
        name=safe_filename(rawname); src=work/name
        await bot.download(obj,destination=src)
        d=detect(src,name); fmts=outputs(d)
        if d.kind=="video" and size>config.max_video_size: fmts=[]
        if not fmts:
            await remove_tree(work); return await m.answer(await t(m.from_user.id,"unsupported"))
        await state.set_state(Flow.awaiting_choice)
        await state.update_data(token=token,workdir=str(work),src=str(src),kind=d.kind,ext=d.ext,name=name,size=size)
        await m.answer(f"📄 <b>File received</b>\n\nName: {name}\nFormat: {d.ext.upper()}\nSize: {human_size(size)}\n\n<b>Convert to:</b>",
                       parse_mode="HTML",reply_markup=conversion_keyboard(token,fmts))
    except Exception:
        logging.exception("Receive failed"); await remove_tree(work); await state.clear(); await m.answer(await t(m.from_user.id,"failed"))
