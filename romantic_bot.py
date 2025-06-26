# romantic_bot_v3.py
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

API_TOKEN = "7711930364:AAEoVeW_M5JhhHCOx_234MU1zO4kgDMltSs"
OWNER_ID = 547994168  # Замени на свой Telegram ID (узнать через @userinfobot)

# Меню (можно дополнить блюдами)
menu = [
    {
        "name": "🍝 Спагетти с любовью",
        "kisses": 5,
        "image": "https://example.com/spaghetti.jpg"
    },
    {
        "name": "🥗 Салат «Сердечко»",
        "kisses": 3,
        "image": "https://example.com/salad.jpg"
    },
    {
        "name": "🍰 Тирамису обожания",
        "kisses": 4,
        "image": "https://example.com/tiramisu.jpg"
    },
]

# Хранилище корзин
user_carts = {}

# Команда /start
async def start_cmd(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_carts[user_id] = []

    await message.answer("Привет, моя любимая! 🍓\nДобро пожаловать в Домашний Ресторан. Выбирай, что хочешь 😘")

    # Отправляем меню
    for idx, item in enumerate(menu):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Добавить за {item['kisses']} 😘", callback_data=f"add_{idx}")]
        ])
        await bot.send_photo(
            chat_id=user_id,
            photo=item["image"],
            caption=item["name"],
            reply_markup=kb
        )

# Обработка нажатий "Добавить"
async def add_item(call: CallbackQuery):
    idx = int(call.data.split("_")[1])
    user_id = call.from_user.id
    item = menu[idx]

    user_carts.setdefault(user_id, []).append(item)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить заказ", callback_data="checkout")]
    ])

    await call.message.answer(f"Добавлено в корзину: {item['name']}", reply_markup=kb)
    await call.answer()

# Оформление заказа
async def checkout(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await call.answer("Корзина пуста 😢")
        return

    # Составим заказ
    summary = "\n".join([f"— {item['name']} ({item['kisses']} 😘)" for item in cart])
    total = sum(item['kisses'] for item in cart)

    text = f"🍽️ Твой заказ:\n{summary}\n\nИтого: {total} поцелуйчиков 😘"

    await call.message.answer(text)
    await call.answer("Заказ оформлен 💌")

    # Отправка владельцу
    await bot.send_message(
        OWNER_ID,
        f"📥 Новый заказ от {call.from_user.full_name} (@{call.from_user.username}):\n{text}",
        parse_mode=ParseMode.HTML
    )

    user_carts[user_id] = []  # Очищаем корзину

# Основной запуск
async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_cmd, Command("start"))
    dp.callback_query.register(add_item, F.data.startswith("add_"))
    dp.callback_query.register(checkout, F.data == "checkout")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
