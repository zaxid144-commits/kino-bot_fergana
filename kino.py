import asyncio
import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


# ==========================================
# 0. ВЕБ-СЕРВЕР ДЛЯ ПРОХОЖДЕНИЯ ПОРТА НА RENDER
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live and running!")


def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()


threading.Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# 1. НАСТРОЙКИ И ИНИЦИАЛИЗАЦИЯ
# ==========================================
logging.basicConfig(level=logging.INFO)

# Укажите ваш токен и ID администратора
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8995206672:AAFKlE6d86dZ1BaiZv1T4qJpbGoMXs9JTBE")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", 6698944628))  # Укажите ваш Telegram ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище выбора пользователей
user_data = {}


class BookingState(StatesGroup):
    waiting_for_receipt = State()


# ==========================================
# 2. ДАННЫЕ О ФИЛЬМАХ И ЯЗЫКАХ
# ==========================================
MOVIES = [
    {"id": 1, "title_ru": "Дюна: Часть вторая", "title_uz": "Duna: Ikkinchi qism", "price": 40000,
     "time": "15:00, 18:30", "poster": "https://picsum.photos/400/600?random=1"},
    {"id": 2, "title_ru": "Кунг-фу Панда 4", "title_uz": "Kung Fu Panda 4", "price": 35000,
     "time": "12:00, 14:00, 16:00", "poster": "https://picsum.photos/400/600?random=2"},
    {"id": 3, "title_ru": "Годзилла и Конг: Новая империя", "title_uz": "Godzilla va Kong: Yangi imperiya",
     "price": 45000, "time": "17:00, 20:00", "poster": "https://picsum.photos/400/600?random=3"},
    {"id": 4, "title_ru": "Мастер и Маргарита", "title_uz": "Usta va Margarita", "price": 40000, "time": "19:00, 21:30",
     "poster": "https://picsum.photos/400/600?random=4"},
    {"id": 5, "title_ru": "Оппенгеймер", "title_uz": "Oppenxaymer", "price": 45000, "time": "21:00",
     "poster": "https://picsum.photos/400/600?random=5"},
]

TEXTS = {
    "ru": {
        "welcome": "👋 **Добро пожаловать в кинотеатр «Фестиваль»!**\n\nПожалуйста, выберите язык обслуживания:",
        "main_menu": "🎬 **Главное меню**\nВыберите нужный раздел:",
        "btn_catalog": "🍿 Афиша фильмов",
        "btn_contact": "📞 Контакты и адрес",
        "btn_lang": "🌐 Сменить язык",
        "contacts": "📍 **Кинотеатр «Фестиваль»**\n📞 Телефон: +998 99 272 29 10\n🏢 Адрес: ТЦ «Фестиваль»",
        "select_movie": "🎟 **Выберите фильм из списка:**",
        "movie_info": "🎬 **{title}**\n\n⏰ Сеансы: {time}\n💰 Цена: {price} сум",
        "btn_buy": "🎟 Купить билет",
        "btn_back": "⬅️ Назад",
        "send_receipt": "💳 **Оплата билета**\n\nПереведите **{price} сум** на карту:\n`8600 0000 0000 0000` (Кинотеатр)\n\nПосле оплаты отправьте сюда **чек / скриншот**.",
        "receipt_received": "✅ **Ваш чек принят!**\nАдминистратор проверит оплату и свяжется с вами.",
        "admin_notify": "📥 **Новая заявка на бронирование!**\n\n👤 Пользователь: @{username} (ID: {user_id})\n🎬 Фильм: {title}\n💰 Сумма: {price} сум"
    },
    "uz": {
        "welcome": "👋 **«Festival» kinoteatriga xush kelibsiz!**\n\nIltimos, xizmat ko'rsatish tilini tanlang:",
        "main_menu": "🎬 **Asosiy menyu**\nKerakli bo'limni tanlang:",
        "btn_catalog": "🍿 Filmlar afishasi",
        "btn_contact": "📞 Kontaktlar va manzil",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "contacts": "📍 **«Festival» kinoteatri**\n📞 Telefon: +998 99 272 29 10\n🏢 Manzil: «Festival» KSM",
        "select_movie": "🎟 **Ro'yxatdan filmni tanlang:**",
        "movie_info": "🎬 **{title}**\n\n⏰ Seanslar: {time}\n💰 Narxi: {price} so'm",
        "btn_buy": "🎟 Chipta sotib olish",
        "btn_back": "⬅️ Orqaga",
        "send_receipt": "💳 **Chipta to'lovi**\n\n**{price} so'm** summani kartaga o'tkazing:\n`8600 0000 0000 0000` (Kinoteatr)\n\nTo'lovdan so'ng **cheksiz / skrinshotni** shu yerga yuboring.",
        "receipt_received": "✅ **Chekingiz qabul qilindi!**\nAdministrator to'lovni tekshiradi va siz bilan bog'lanadi.",
        "admin_notify": "📥 **Yangi bron so'rovi!**\n\n👤 Foydalanuvchi: @{username} (ID: {user_id})\n🎬 Film: {title}\n💰 Summa: {price} so'm"
    }
}


# ==========================================
# 3. ВСПОМОГАТЕЛЬНЫЕ КЛАВИАТУРЫ
# ==========================================
def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ])


def get_main_keyboard(lang):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_catalog"])],
            [KeyboardButton(text=t["btn_contact"]), KeyboardButton(text=t["btn_lang"])]
        ],
        resize_keyboard=True
    )


def get_catalog_keyboard(lang):
    t = TEXTS[lang]
    buttons = []
    for m in MOVIES:
        title = m["title_ru"] if lang == "ru" else m["title_uz"]
        buttons.append([InlineKeyboardButton(text=title, callback_data=f"movie_{m['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_detail_keyboard(lang, movie_id):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_buy"], callback_data=f"buy_{movie_id}")],
        [InlineKeyboardButton(text=t["btn_back"], callback_data="back_catalog")]
    ])


# ==========================================
# 4. ОБРАБОТЧИКИ КОМАНД И НАЖАТИЙ
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(TEXTS["ru"]["welcome"], reply_markup=get_lang_keyboard(), parse_mode="Markdown")


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    user_data[call.from_user.id] = {"lang": lang}
    await call.message.delete()
    await call.message.answer(TEXTS[lang]["main_menu"], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")


@dp.message(F.text.in_([TEXTS["ru"]["btn_lang"], TEXTS["uz"]["btn_lang"]]))
async def change_lang(message: types.Message):
    await message.answer(TEXTS["ru"]["welcome"], reply_markup=get_lang_keyboard(), parse_mode="Markdown")


@dp.message(F.text.in_([TEXTS["ru"]["btn_contact"], TEXTS["uz"]["btn_contact"]]))
async def show_contacts(message: types.Message):
    lang = user_data.get(message.from_user.id, {}).get("lang", "ru")
    await message.answer(TEXTS[lang]["contacts"], parse_mode="Markdown")


@dp.message(F.text.in_([TEXTS["ru"]["btn_catalog"], TEXTS["uz"]["btn_catalog"]]))
async def show_catalog_msg(message: types.Message):
    lang = user_data.get(message.from_user.id, {}).get("lang", "ru")
    await message.answer(TEXTS[lang]["select_movie"], reply_markup=get_catalog_keyboard(lang), parse_mode="Markdown")


@dp.callback_query(F.data == "back_catalog")
async def back_to_catalog(call: types.CallbackQuery):
    lang = user_data.get(call.from_user.id, {}).get("lang", "ru")
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(TEXTS[lang]["select_movie"], reply_markup=get_catalog_keyboard(lang),
                              parse_mode="Markdown")


@dp.callback_query(F.data.startswith("movie_"))
async def show_movie_details(call: types.CallbackQuery):
    lang = user_data.get(call.from_user.id, {}).get("lang", "ru")
    movie_id = int(call.data.split("_")[1])
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)

    if movie:
        title = movie["title_ru"] if lang == "ru" else movie["title_uz"]
        caption = TEXTS[lang]["movie_info"].format(title=title, time=movie["time"], price=movie["price"])

        try:
            await call.message.delete()
        except Exception:
            pass

        await call.message.answer_photo(
            photo=movie["poster"],
            caption=caption,
            reply_markup=get_movie_detail_keyboard(lang, movie_id),
            parse_mode="Markdown"
        )


@dp.callback_query(F.data.startswith("buy_"))
async def buy_ticket(call: types.CallbackQuery, state: FSMContext):
    lang = user_data.get(call.from_user.id, {}).get("lang", "ru")
    movie_id = int(call.data.split("_")[1])
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)

    if movie:
        await state.update_data(movie_id=movie_id)
        await state.set_state(BookingState.waiting_for_receipt)

        msg_text = TEXTS[lang]["send_receipt"].format(price=movie["price"])
        try:
            await call.message.delete()
        except Exception:
            pass

        await call.message.answer(msg_text, parse_mode="Markdown")


@dp.message(BookingState.waiting_for_receipt, F.photo | F.document)
async def process_receipt(message: types.Message, state: FSMContext):
    lang = user_data.get(message.from_user.id, {}).get("lang", "ru")
    data = await state.get_data()
    movie_id = data.get("movie_id")
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)
    title = movie["title_ru"] if movie else "Кино"
    price = movie["price"] if movie else 0

    # Ответ пользователю
    await message.answer(TEXTS[lang]["receipt_received"], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

    # Уведомление администратору
    admin_msg = TEXTS["ru"]["admin_notify"].format(
        username=message.from_user.username or "без_юзернейма",
        user_id=message.from_user.id,
        title=title,
        price=price
    )

    try:
        if message.photo:
            await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=message.photo[-1].file_id, caption=admin_msg,
                                 parse_mode="Markdown")
        elif message.document:
            await bot.send_document(chat_id=ADMIN_CHAT_ID, document=message.document.file_id, caption=admin_msg,
                                    parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Не удалось отправить чек администратору: {e}")

    await state.clear()


# ==========================================
# 5. ЗАПУСК БОТА
# ==========================================
async def main():
    print(f"Бот ТЦ «Фестиваль» успешно запущен. ID админа: {ADMIN_CHAT_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
