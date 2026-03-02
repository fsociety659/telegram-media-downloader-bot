import asyncio
import logging
import os
import yt_dlp
import functools
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile

TOKEN = "TOKEN"
SAVE_PATH = os.path.expanduser('~/video_yotube')

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🎬 Видео", callback_data="mp4"),
        types.InlineKeyboardButton(text="🎵 Аудио", callback_data="mp3")
    )
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Кидай ссылку, я скачаю видео")

@dp.message(lambda message: "http" in message.text)
async def handle_link(message: types.Message):
    await message.reply(
        "Сыллку сохранил! 🎯 Выбирай формат:", reply_markup=get_kb(),
        )

@dp.callback_query(F.data.in_(["mp4", "mp3"]))
async def download_logic(callback: types.CallbackQuery):
    if callback.message.reply_to_message:
        url = callback.message.reply_to_message.text
    else:
        await callback.message.edit_text("Ошибка: Ссылка потеряна!")
        return

    await callback.message.edit_text(f"Начинаю скачивание {callback.data}... ⏳")

    unique_id = f"file_{callback.from_user.id}_{int(asyncio.get_event_loop().time())}"
    
    ydl_opts = {
        'outtmpl': f"{SAVE_PATH}/{unique_id}.%(ext)s",
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if callback.data == 'mp4' else 'bestaudio/best',

        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    if callback.data == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(
                None, 
                functools.partial(ydl.extract_info, url, download=True)
            )
            real_file_path = ydl.prepare_filename(info)
            
            if callback.data == 'mp3' and not real_file_path.endswith('.mp3'):
                real_file_path = os.path.splitext(real_file_path)[0] + '.mp3'

        await callback.message.edit_text("Загрузка в Telegram.... 🚀")
        
        if not os.path.exists(real_file_path):
             await callback.message.edit_text(f"Ошибка: файл не найден ❌")
             return

        to_send = FSInputFile(real_file_path)
        if callback.data == 'mp4':
            await callback.message.answer_video(to_send, caption="Твой видос готов!")
        else:
            await callback.message.answer_audio(to_send, caption="Твой звук готов!")
        
        if os.path.exists(real_file_path):
            os.remove(real_file_path)
        await callback.message.delete()
    
    except Exception as e:
        await callback.message.edit_text(f"Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


