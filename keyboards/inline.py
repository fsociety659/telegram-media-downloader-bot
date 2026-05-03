from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎬 Видео", callback_data="mp4"),
        InlineKeyboardButton(text="🎵 Аудио", callback_data="mp3")
    )
    return builder.as_markup()