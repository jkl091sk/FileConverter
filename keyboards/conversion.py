from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
def conversion_keyboard(token: str, formats: list[str]):
    rows=[]
    for i in range(0,len(formats),3):
        rows.append([InlineKeyboardButton(text=x.upper(),callback_data=f"cv:{token}:{x}") for x in formats[i:i+3]])
    return InlineKeyboardMarkup(inline_keyboard=rows)
