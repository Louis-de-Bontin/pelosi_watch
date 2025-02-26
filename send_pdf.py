from decouple import Config, RepositoryEnv
import os
from telegram import Bot
from datetime import datetime


env = Config(RepositoryEnv(os.path.join(os.getcwd(), '.env')))

telegram_bot = Bot(token=env.get('TELEGRAM_BOT_TOKEN'))


async def send_pdf_to_telegram(file_path, pdf_filename):
    try:
        with open(file_path, 'rb') as pdf:
            await telegram_bot.send_document(
                chat_id=env.get('TELEGRAM_CHANNEL_ID'),
                document=pdf,
                caption=f"New Pelosi Filing: {pdf_filename} (Date: {datetime.now().strftime('%Y-%m-%d')})"
            )
        print(f"PDF sent to Telegram channel: {pdf_filename}")
    except Exception as e:
        print(f"Error sending PDF to Telegram: {e}")
