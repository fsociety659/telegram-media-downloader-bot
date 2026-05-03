import asyncio
import os
import yt_dlp
import functools
import time

from aiogram import Router, types, F
from aiogram.types import FSInputFile
from keyboards.inline import get_kb

router = Router()

SAVE_PATH = os.path.expanduser('~/video_yotube')
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def get_progress_bar(percent):
    length = 10
    filled_length = int(length * percent // 100)
    bar = '🟩' * filled_length + '⬜' * (length - filled_length)
    return bar

def progress_hook(d, message, loop):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%').replace('%', '')
        try:
            percent = float(p)
        except Exception:
            percent = 0

        last_update = getattr(progress_hook, "last_update", 0)
        if time.time() - last_update < 2:
            return

        progress_hook.last_update = time.time()
        bar = get_progress_bar(percent)
        text = f"Скачивание: {percent:.1f}%\n{bar}"

        asyncio.run_coroutine_threadsafe(message.edit_text(text), loop)

@router.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    await message.reply("Ссылку сохранил! 🎯 Выбирай формат:", reply_markup=get_kb())

@router.callback_query(F.data.in_(["mp4", "mp3"]))
async def download_logic(callback: types.CallbackQuery):
    if callback.message.reply_to_message:
        url = callback.message.reply_to_message.text
    else:
        await callback.message.edit_text("Ошибка: Ссылка потеряна!")
        return

    await callback.message.edit_text("Проверяю файл... ⏳")
    loop = asyncio.get_running_loop()

    unique_id = f"file_{callback.from_user.id}_{int(time.time())}"

    ydl_opts = {
        'outtmpl': f"{SAVE_PATH}/{unique_id}.%(ext)s",
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if callback.data == 'mp4' else 'bestaudio/best',
        'referer': 'https://google.com',
        'geo_bypass': True,
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'progress_hooks': [lambda d: progress_hook(d, callback.message, loop)],
    }

    if callback.data == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = await loop.run_in_executor(None, functools.partial(ydl.extract_info, url, download=False))
            filesize = info.get('filesize') or info.get('filesize_approx')
            if filesize and filesize > 50 * 1024 * 1024:
                await callback.message.edit_text("❌ Файл слишком большой (> 50MB)")
                return

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, functools.partial(ydl.extract_info, url, download=True))
            real_file_path = ydl.prepare_filename(info)
            if callback.data == 'mp3' and not real_file_path.endswith('.mp3'):
                real_file_path = os.path.splitext(real_file_path)[0] + '.mp3'

        await callback.message.edit_text("Загрузка в Telegram.... 🚀")
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
        if 'real_file_path' in locals() and os.path.exists(real_file_path):
            os.remove(real_file_path)
