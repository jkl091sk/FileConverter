from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main import main_menu
from services.i18n import t
router=Router()

@router.message(Command("start"))
async def start(m: Message):
    await m.answer(await t(m.from_user.id,"welcome"), reply_markup=main_menu())

@router.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer("Send a file, choose an available action, and wait for the result.\nUse /cancel to cancel the current operation.")

@router.message(Command("formats"))
@router.message(F.text=="📋 Formats")
async def formats(m: Message):
    await m.answer("Images: PNG JPG WEBP BMP TIFF GIF\nAudio: MP3 WAV OGG FLAC AAC M4A\nVideo: MP4 WEBM MOV MKV AVI GIF + MP3/WAV extraction\nDocuments: DOCX PDF TXT ODT RTF HTML\nPDF: TXT, images, compress, split, selected pages\nArchives: ZIP 7Z TAR TAR.GZ")

@router.message(Command("about"))
@router.message(F.text=="ℹ️ About")
async def about(m: Message):
    await m.answer("FileConverter converts files directly in Telegram. Uploaded files are processed temporarily and are not permanently stored.")

@router.message(F.text=="📤 Convert File")
async def prompt(m: Message):
    await m.answer("Send me a file as a document, photo, audio, video, or animation.")
