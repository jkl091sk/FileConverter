from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
      [KeyboardButton(text="📤 Convert File"),KeyboardButton(text="📋 Formats")],
      [KeyboardButton(text="🕘 History"),KeyboardButton(text="⚙️ Settings")],
      [KeyboardButton(text="ℹ️ About")]
    ],resize_keyboard=True)
