# 📥 YouTube Downloader Bot (Aiogram 3)

A powerful and stable Telegram bot for downloading video and audio from YouTube. Now featuring asynchronous processing and anti-blocking measures.

## ✨ Features
- 🎬 **Video Download**: High-quality MP4 format.
- 🎵 **Audio Extraction**: Convert video to MP3 (192 kbps).
- ⚡ **Asynchronous Engine**: The bot never freezes, handling multiple downloads simultaneously.
- 🛡️ **Stable Connection**: Built-in SSL fix and User-Agent spoofing to prevent YouTube blocks.
- 🗑 **Auto-Cleanup**: Files are deleted from the server immediately after sending.
- ⌨️ **Modern UI**: Clean interface using Inline Keyboards.

## 🚀 Installation & Setup

### 1. System Requirements
- **Python 3.10+**
- **FFmpeg**: Required for media processing and merging tracks.
  - **Arch Linux**: `sudo pacman -S ffmpeg`
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org), extract, and add the `bin` folder to your System PATH.

### 2. Install Dependencies
```bash
pip install -r requirements.txt