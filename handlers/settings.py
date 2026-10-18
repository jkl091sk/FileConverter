from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import get_settings, update_setting
router=Router()

def kb():
    return InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="🇬🇧 English",callback_data="set:language:en"),InlineKeyboardButton(text="🇺🇦 Українська",callback_data="set:language:uk"),InlineKeyboardButton(text="🇷🇺 Русский",callback_data="set:language:ru")],
      [InlineKeyboardButton(text="Image 75",callback_data="set:image_quality:75"),InlineKeyboardButton(text="Image 90",callback_data="set:image_quality:90"),InlineKeyboardButton(text="Image 95",callback_data="set:image_quality:95")],
      [InlineKeyboardButton(text="Audio Low",callback_data="set:audio_quality:low"),InlineKeyboardButton(text="Medium",callback_data="set:audio_quality:medium"),InlineKeyboardButton(text="High",callback_data="set:audio_quality:high")],
      [InlineKeyboardButton(text="Toggle filenames",callback_data="toggle:preserve_filenames"),InlineKeyboardButton(text="Toggle metadata",callback_data="toggle:preserve_metadata")]
    ])

async def text(uid):
    s=await get_settings(uid)
    return f"⚙️ Settings\nLanguage: {s.language}\nImage quality: {s.image_quality}\nAudio quality: {s.audio_quality}\nPreserve filenames: {s.preserve_filenames}\nPreserve metadata: {s.preserve_metadata}"

@router.message(Command("settings"))
@router.message(F.text=="⚙️ Settings")
async def settings(m: Message): await m.answer(await text(m.from_user.id),reply_markup=kb())

@router.callback_query(F.data.startswith("set:"))
async def set_cb(c: CallbackQuery):
    _,field,value=c.data.split(":",2)
    if field=="image_quality": value=int(value)
    await update_setting(c.from_user.id,field,value); await c.message.edit_text(await text(c.from_user.id),reply_markup=kb()); await c.answer("Saved")

@router.callback_query(F.data.startswith("toggle:"))
async def toggle_cb(c: CallbackQuery):
    field=c.data.split(":",1)[1]; s=await get_settings(c.from_user.id)
    value=not getattr(s,field); await update_setting(c.from_user.id,field,int(value))
    await c.message.edit_text(await text(c.from_user.id),reply_markup=kb()); await c.answer("Saved")
