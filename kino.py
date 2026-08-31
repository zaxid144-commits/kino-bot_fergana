import asyncio
import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


# ==========================================
# 0. ВЕБ-СЕРВЕР ДЛЯ СТАБИЛЬНОЙ РАБОТЫ НА RENDER
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Kino Bot is running perfectly!")


def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()


threading.Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# 1. НАСТРОЙКИ И ПЕРЕМЕННЫЕ
# ==========================================
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8995206672:AAFKlE6d86dZ1BaiZv1T4qJpbGoMXs9JTBE")

# Номера телефонов (укажи нужные)
PHONE_BOOKING = "+998 93 484 51 41"  # Номер для бронирования
PHONE_SUPPORT = "+998 99 272 29 10"  # Номер техподдержки

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище выбранного языка пользователей
user_data = {}

# ==========================================
# 2. КАТАЛОГ ФИЛЬМОВ И АФИША (ЦЕНЫ 5 000 - 50 000 СУМ)
# ==========================================
MOVIES = [
    {
        "id": 1,
        "title_ru": "Человек-паук: Новый день",
        "title_uz": "O'rgimchak-odam: Yangi kun",
        "price": 50000,
        "time": "15:00, 18:00, 21:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmM2MyOGI4YjktYjNhZC00NDA4LWI3ZmMtNWYwYWY1OWRkYmUyXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 2,
        "title_ru": "Веном: Последний танец (2024)",
        "title_uz": "Venom: Oxirgi raqs (2024)",
        "price": 45000,
        "time": "16:30, 19:30, 22:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmM2E5ZmYyMzItPCI0ZS00OGMwLTg4MTctN2E3OTM0ZDA3ZTZhXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 3,
        "title_ru": "Человек-паук: Нет пути домой (2021)",
        "title_uz": "O'rgimchak-odam: Uyga yo'l yo'q (2021)",
        "price": 35000,
        "time": "14:00, 17:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmM2MyOGI4YjktYjNhZC00NDA4LWI3ZmMtNWYwYWY1OWRkYmUyXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 4,
        "title_ru": "Бэтмен (2022)",
        "title_uz": "Betmen (2022)",
        "price": 30000,
        "time": "18:00, 21:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmM2JkOTlhNDktYjE3YS00NzA3LWIzM2EtN2Y4YmJkNmRjNWRkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 5,
        "title_ru": "Джентльмены (2020)",
        "title_uz": "Jentlmenlar (2020)",
        "price": 25000,
        "time": "19:00, 21:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmNzE5OTE5NmUtMTM3MS00MDlhLWE4NDctYTY1MzE1ZmJhZTBmXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 6,
        "title_ru": "Довод (2020)",
        "title_uz": "Tenet (2020)",
        "price": 20000,
        "time": "20:00",
        "poster": "https://m.media-amazon.com/images/M/MVBYzVkMTNhYjEtNmI3NC00YTI0LWI4NzYtMjA1YmJlZWJmNWZhXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 7,
        "title_ru": "Мстители: Финал (2019)",
        "title_uz": "Qasoskorlar: Final (2019)",
        "price": 15000,
        "time": "16:00, 19:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmMTZiNmMxMmEtYWQ3ZC00MWVlLTg5ODAtOTNmZTBjNzA0N2M1XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 8,
        "title_ru": "Интерстеллар (Классика)",
        "title_uz": "Interstellar (Klassika)",
        "price": 10000,
        "time": "21:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmNzA3OWI2ODktZmE2YS00MDk0LWI4ZjItYzA1YjhkYzhkMDY4XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 9,
        "title_ru": "Ретро Утро: Мультфильмы",
        "title_uz": "Retro Multfilmlar",
        "price": 5000,
        "time": "11:00, 13:00",
        "poster": "https://picsum.photos/400/600?random=9"
    }
]

# ==========================================
# 3. ТЕКСТЫ НА 2 ЯЗЫКАХ
# ==========================================
TEXTS = {
    "ru": {
        "welcome": "👋 **Добро пожаловать в кинотеатр «Фестиваль»!**\n\nПожалуйста, выберите язык:",
        "main_menu": "🎬 **Главное меню**\nВыберите нужный раздел ниже:",
        "btn_catalog": "🍿 Афиша и выбор сеансов",
        "btn_contact": "📍 Контакты и адрес",
        "btn_lang": "🌐 Сменить язык",
        "contacts": (
            f"📍 **Кинотеатр «Фестиваль»**\n"
            f"🏢 **Адрес:** г. Фергана, Центр, ТЦ «Фестиваль»\n\n"
            f"📞 **Бронирование билетов:** `{PHONE_BOOKING}`\n"
            f"🛠 **Техподдержка:** `{PHONE_SUPPORT}`\n\n"
            f"💵 *Оплата производится наличными в кассе.*"
        ),
        "select_movie": "🎟 **Выберите фильм из афиши:**",
        "movie_info": (
            "🎬 **Фильм:** {title}\n\n"
            "⏰ **Доступные сеансы:** {time}\n"
            "💰 **Цена билета:** {price:,} сум\n"
            "💵 **Оплата:** Наличными в кассе"
        ),
        "btn_reserve": "📞 Забронировать место",
        "btn_back": "⬅️ Назад к афише",
        "reserve_info": (
            "📞 **БРОНИРОВАНИЕ МЕСТ**\n\n"
            "🎬 **Выбранный фильм:** {title}\n"
            "💰 **Цена билета:** {price:,} сум\n\n"
            "Для бронирования мест звоните главному менеджеру кинотеатра:\n"
            "👉 **`{phone}`**\n\n"
            "*(Позвоните по номеру выше, назовите фильм и забронируйте нужное количество мест!)*"
        )
    },
    "uz": {
        "welcome": "👋 **«Festival» kinoteatriga xush kelibsiz!**\n\nIltimos, tilni tanlang:",
        "main_menu": "🎬 **Asosiy menyu**\nKerakli bo'limni tanlang:",
        "btn_catalog": "🍿 Afisha va seanslar",
        "btn_contact": "📍 Kontaktlar va manzil",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "contacts": (
            f"📍 **«Festival» kinoteatri**\n"
            f"🏢 **Manzil:** Farg'ona sh., Markaz, «Festival» KSM\n\n"
            f"📞 **Chipta bron qilish:** `{PHONE_BOOKING}`\n"
            f"🛠 **Texnik qo'llab-quvvatlash:** `{PHONE_SUPPORT}`\n\n"
            f"💵 *To'lov kassada naqd pulda amalga oshiriladi.*"
        ),
        "select_movie": "🎟 **Afishadan filmni tanlang:**",
        "movie_info": (
            "🎬 **Film:** {title}\n\n"
            "⏰ **Mavjud seanslar:** {time}\n"
            "💰 **Chipta narxi:** {price:,} so'm\n"
            "💵 **To'lov:** Kassada naqd pulda"
        ),
        "btn_reserve": "📞 Joyni bron qilish",
        "btn_back": "⬅️ Afishaga orqaga",
        "reserve_info": (
            "📞 **JOYLARNI BRON QILISH**\n\n"
            "🎬 **Tanlangan film:** {title}\n"
            "💰 **Chipta narxi:** {price:,} so'm\n\n"
            "Joyni bron qilish uchun kinoteatr bosh menejeriga qo'ng'iroq qiling:\n"
            "👉 **`{phone}`**\n\n"
            "*(Yuqoridagi raqamga qo'ng'iroq qiling, film nomini ayting va joylarni bron qiling!)*"
        )
    }
}


# ==========================================
# 4. КЛАВИАТУРЫ
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
    buttons = []
    for m in MOVIES:
        title = m["title_ru"] if lang == "ru" else m["title_uz"]
        buttons.append(
            [InlineKeyboardButton(text=f"{title} ({m['price']:,} сум/so'm)", callback_data=f"movie_{m['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_detail_keyboard(lang, movie_id):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_reserve"], callback_data=f"reserve_{movie_id}")],
        [InlineKeyboardButton(text=t["btn_back"], callback_data="back_catalog")]
    ])


# ==========================================
# 5. ОБРАБОТЧИКИ СОБЫТИЙ
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(TEXTS["ru"]["welcome"], reply_markup=get_lang_keyboard(), parse_mode="Markdown")


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    user_data[call.from_user.id] = {"lang": lang}
    try:
        await call.message.delete()
    except Exception:
        pass
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
        caption = TEXTS[lang]["movie_info"].format(
            title=title,
            time=movie["time"],
            price=movie["price"]
        )

        try:
            await call.message.delete()
        except Exception:
            pass

        # Безопасный вызов: если фото не сгрузится с интернета, выведет просто текст
        try:
            await call.message.answer_photo(
                photo=movie["poster"],
                caption=caption,
                reply_markup=get_movie_detail_keyboard(lang, movie_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Ошибка фото: {e}")
            await call.message.answer(
                text=caption,
                reply_markup=get_movie_detail_keyboard(lang, movie_id),
                parse_mode="Markdown"
            )


@dp.callback_query(F.data.startswith("reserve_"))
async def reserve_ticket(call: types.CallbackQuery):
    lang = user_data.get(call.from_user.id, {}).get("lang", "ru")
    movie_id = int(call.data.split("_")[1])
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)

    if movie:
        title = movie["title_ru"] if lang == "ru" else movie["title_uz"]
        msg_text = TEXTS[lang]["reserve_info"].format(
            title=title,
            price=movie["price"],
            phone=PHONE_BOOKING
        )

        back_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_catalog")]
        ])

        try:
            await call.message.delete()
        except Exception:
            pass

        await call.message.answer(msg_text, reply_markup=back_kb, parse_mode="Markdown")


# ==========================================
# 6. ЗАПУСК
# ==========================================
async def main():
    print("Бот ТЦ «Фестиваль» успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
