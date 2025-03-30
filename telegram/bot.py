from telebot.async_telebot import AsyncTeleBot
from core.config import settings
import logging

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('bot.log'),
#         logging.StreamHandler()
#     ]
# )

logger = logging.getLogger(__name__)

bot = AsyncTeleBot(settings.BOT_TOKEN)

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    user_id = message.from_user.id
    await bot.reply_to(message, f"Your Telegram ID is: {user_id}")