from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.database import recent_history, stats
from utils.files import human_size
router=Router()

@router.message(Command("history"))
@router.message(F.text=="🕘 History")
async def history(m: Message):
    rows=await recent_history(m.from_user.id)
    if not rows: return await m.answer("History is empty.")
    await m.answer("🕘 Recent conversions\n\n"+"\n".join(f"{r['original_format'].upper()} → {r['output_format'].upper()} • {r['status']}" for r in rows))

@router.message(Command("stats"))
async def stat(m: Message):
    s=await stats(m.from_user.id)
    await m.answer(f"📊 Your stats\nConversions: {s['total']}\nSuccessful: {s['ok'] or 0}\nProcessed: {human_size(s['bytes'] or 0)}")
