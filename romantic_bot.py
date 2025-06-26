import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import os

API_TOKEN = os.getenv("API_TOKEN")  # можно подставить токен вручную
OWNER_ID = int(os.getenv("OWNER_ID"))  # или вставить Telegram ID напрямую

menu = [
    {
        "name": "🥗 Салат с креветками",
        "kisses": 3,
        "image": "https://cdn.pixabay.com/photo/2017/03/17/08/13/shrimp-2150880_1280.jpg",
        "desc": "Лёгкий салат с хрустящими листьями салата, томатами черри и обжаренными креветками.\n💋 Стоимость: 3 поцелуйчика"
    },
    {
        "name": "🧀 Брускетты с моцареллой",
        "kisses": 2,
        "image": "https://cdn.pixabay.com/photo/2020/01/22/08/50/tomato-4783712_1280.jpg",
        "desc": "Хрустящий багет с тёплой моцареллой, свежими томатами и базиликом.\n💋 Стоимость: 2 поцелуйчика"
    },
    {
        "name": "🍝 Паста с соусом Альфредо",
        "kisses": 5,
        "image": "https://cdn.pixabay.com/photo/2022/03/18/11/17/spaghetti-7076177_1280.jpg",
        "desc": "Нежная паста в сливочном соусе с пармезаном и курицей.\n💋 Стоимость: 5 поцелуйчиков"
    },
    {
        "name": "🍗 Куриное филе в сливочно-грибном соусе",
        "kisses": 5,
        "image": "https://cdn.pixabay.com/photo/2016/03/05/19/02/abstract-1238657_1280.jpg",
        "desc": "Сочное куриное филе, тушёное в соусе с шампиньонами.\n💋 Стоимость: 5 поцелуйчиков"
    },
    {
        "name": "🍰 Торт «Три шоколада»",
        "kisses": 4,
        "image": "https://cdn.pixabay.com/photo/2014/11/28/08/03/cake-548591_1280.jpg",
        "desc": "Воздушный десерт с тремя слоями: горький, молочный и белый шоколад.\n💋 Стоимость: 4 поцелуйчика"
    },
    {
        "name": "🥤 Клубничный лимонад",
        "kisses": 2,
        "image": "https://cdn.pixabay.com/photo/2016/06/23/18/53/drink-1474444_1280.jpg",
        "desc": "Освежающий напиток из свежей клубники, мяты и лимона.\n💋 Стоимость: 2 поцелуйчика"
    }
]

user_carts = {}

# Старт + меню
async def start_cmd(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_carts[user_id] = []

    await message.answer(
        "🌹 Добро пожаловать в Домашний Ресторан!\n"
        "Сегодня ты — самая желанная гостья ❤️\n\n"
        "Выбирай, что тебе по вкусу, и я с любовью всё приготовлю 😘"
    )

    for idx, item in enumerate(menu):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Добавить за {item['kisses']} 😘", callback_data=f"add_{idx}")]
        ])
        await bot.send_photo(
            chat_id=user_id,
            photo=item["image"],
            caption=f"{item['name']}\n\n{item['desc']}",
            reply_markup=kb
        )

    action_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Завершить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart")]
    ])
    await message.answer("Когда будешь готова — заверши заказ или очисти корзину:", reply_markup=action_kb)

# Добавить блюдо
async def add_item(call: CallbackQuery):
    idx = int(call.data.split("_")[1])
    user_id = call.from_user.id
    item = menu[idx]

    cart = user_carts.setdefault(user_id, [])
    if item in cart:
        await call.answer("Ты уже добавила это блюдо 💕", show_alert=True)
        return

    cart.append(item)
    await call.answer(f"Добавлено: {item['name']}")

# Завершить заказ
async def checkout(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await call.answer("Корзина пуста 😢")
        return

    summary = "\n".join([f"• {item['name']} — {item['kisses']} 😘" for item in cart])
    total = sum(item['kisses'] for item in cart)
    text = f"🧾 Твой заказ:\n\n{summary}\n\nИтого: {total} поцелуйчиков 💋"

    await call.message.answer(text)
    await call.message.answer("Спасибо за заказ, любимая 💖 Всё будет готово с душой и любовью ✨")
    await call.answer("Заказ отправлен 💌")

    await bot.send_message(
        OWNER_ID,
        f"📥 Новый заказ от {call.from_user.full_name} (@{call.from_user.username}):\n\n{text}"
    )

    user_carts[user_id] = []

# Очистить корзину
async def clear_cart(call: CallbackQuery):
    user_id = call.from_user.id
    user_carts[user_id] = []
    await call.answer("Корзина очищена 🧹")
    await call.message.answer("Твоя корзина теперь пуста 🌸")

# Основной запуск
async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_cmd, Command("start"))
    dp.callback_query.register(add_item, F.data.startswith("add_"))
    dp.callback_query.register(checkout, F.data == "checkout")
    dp.callback_query.register(clear_cart, F.data == "clear_cart")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
