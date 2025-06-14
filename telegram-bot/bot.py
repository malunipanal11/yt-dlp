import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# yt-dlp download function
async def download_audio(url: str, output_path: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return filename
    except Exception as e:
        logger.error(f"Error downloading: {e}")
        return None

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube URL, and I'll download the audio as MP3!")

# Message handler for URLs
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Processing your URL...")

    # Download the audio
    output_path = "downloads"
    os.makedirs(output_path, exist_ok=True)
    filename = await download_audio(url, output_path)

    if filename and os.path.exists(filename):
        # Send the file to the user
        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio)
        # Clean up
        os.remove(filename)
        await update.message.reply_text("Audio sent! Send another URL or use /start.")
    else:
        await update.message.reply_text("Failed to download the audio. Please check the URL and try again.")

def main():
    # Initialize the bot with your token
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    # Start the bot with polling
    application.run_polling()

if __name__ == '__main__':
    main()
