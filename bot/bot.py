from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import uuid

from db import init_db, save_user_token, get_user_token

TOKEN = "ТОКЕН_ТЕЛЕГРАМ_БОТА"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

init_db()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id

    # Создаём токен
    token = str(uuid.uuid4())
    save_user_token(user_id, token)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Мой профиль"))

    await message.answer("Добро пожаловать!", reply_markup=keyboard)


@dp.message_handler(lambda m: m.text == "Мой профиль")
async def profile(message: types.Message):
    user_id = message.from_user.id
    token = get_user_token(user_id)

    link = f"https://{YOUR_DOMAIN}/profile?token={token}"

    await message.answer(f"Ваш профиль:\n{link}")


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)
