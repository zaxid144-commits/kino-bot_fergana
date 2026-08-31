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
# 0. ВЕБ-СЕРВЕР ДЛЯ ПРОХОЖДЕНИЯ ПОРТА НА RENDER
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live and running!")


def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()


threading.Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# 1. НАСТРОЙКИ И ИНИЦИАЛИЗАЦИЯ
# ==========================================
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8995206672:AAFKlE6d86dZ1BaiZv1T4qJpbGoMXs9JTBE")
ADMIN_PHONE = "+998 99 272 29 10"  # Номер для бронирования

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище выбора языка пользователей
user_data = {}

# ==========================================
# 2. РАСШИРЕННЫЙ КАТАЛОГ ФИЛЬМОВ
# ==========================================
MOVIES = [
    {
        "id": 1,
        "title_ru": "Дюна: Часть вторая (2024)",
        "title_uz": "Duna: Ikkinchi qism (2024)",
        "price": 45000,
        "time": "15:00, 18:30, 21:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmMjA2MTIyONAtYTIzOC00YzI4LWIxNDYtMWJmY2I3LWM2YThlXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 2,
        "title_ru": "Кунг-фу Панда 4 (2024)",
        "title_uz": "Kung Fu Panda 4 (2024)",
        "price": 35000,
        "time": "12:00, 14:00, 16:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmYTA3N2IxOTMtYThhOC00Y2E4LWIxNjItZTU3NDI2NDI4OTk3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 3,
        "title_ru": "Годзилла и Конг: Новая империя (2024)",
        "title_uz": "Godzilla va Kong: Yangi imperiya (2024)",
        "price": 40000,
        "time": "17:00, 20:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmNzI2OTM2M2UtYWFiOC00NWZhLTg3MDAtMDU0YmIxOGU3OTNmXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 4,
        "title_ru": "Стражи Галактики. Часть 3 (2023)",
        "title_uz": "Galaktika qo'riqchilari 3 (2023)",
        "price": 40000,
        "time": "16:30, 19:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmMjM2ZTBjNjItYjA0OC00ZWEzLThmMDUtYzg3NWNmNWY0M2E3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 5,
        "title_ru": "Оппенгеймер (2023)",
        "title_uz": "Oppenxaymer (2023)",
        "price": 45000,
        "time": "18:00, 21:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmN2I0NjAxZGYtMGMyOC00YzkwLWI4OWItNmU2M2RhOTlkOThkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 6,
        "title_ru": "Аватар: Путь воды (2022)",
        "title_uz": "Avatar: Suv yo'li (2022)",
        "price": 45000,
        "time": "14:30, 18:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmYjA0YzA0YWUtZDkzOS00MWEzLWIxYjYtYmI3YWU3OGI3NzhkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 7,
        "title_ru": "Человек-паук: Нет пути домой (2021)",
        "title_uz": "O'rgimchak-odam: Uyga yo'l yo'q (2021)",
        "price": 35000,
        "time": "13:00, 17:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmM2MyOGI4YjktYjNhZC00NDA4LWI3ZmMtNWYwYWY1OWRkYmUyXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 8,
        "title_ru": "Бэтмен (2022)",
        "title_uz": "Betmen (2022)",
        "price": 40000,
        "time": "19:00, 22:00",
        "poster": "https://m.media-amazon.com/images/M/MVBmM2JkOTlhNDktYjE3YS00NzA3LWIzM2EtN2Y4YmJkNmRjNWRkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 9,
        "title_ru": "Кот в сапогах 2: Последнее желание (2022)",
        "title_uz": "Etik kiygan mushuk 2 (2022)",
        "price": 35000,
        "time": "11:00, 13:30, 15:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmNmI3N2VjN2UtN2U3ZS00Y2UzLTkyNmEtYWRiYjgzYzg4MTlhXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    {
        "id": 10,
        "title_ru": "Интерстеллар (Классика)",
        "title_uz": "Interstellar (Klassika)",
        "price": 40000,
        "time": "20:30",
        "poster": "https://m.media-amazon.com/images/M/MVBmNzA3OWI2ODktZmE2YS00MDk0LWI4ZjItYzA1YjhkYzhkMDY4XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    }
]

TEXTS = {
    "ru": {
        "welcome": "👋 **Добро пожаловать в кинотеатр «Фестиваль»!**\n\nПожалуйста, выберите язык обслуживания:",
        "main_menu": "🎬 **Главное меню**\nВыберите нужный раздел:",
        "btn_catalog": "🍿 Афиша фильмов",
        "btn_contact": "📞 Контакты и адрес",
        "btn_lang": "🌐 Сменить язык",
        "contacts": f"📍 **Кинотеатр «Фестиваль»**\n📞 Бронирование и справки: {ADMIN_PHONE}\n🏢 Адрес: ТЦ «Фестиваль»\n💵 Оплата принимается **только наличными** в кассе кинотеатра.",
        "select_movie": "🎟 **Выберите фильм из афиши:**",
        "movie_info": "🎬 **{title}**\n\n⏰ Сеансы: {time}\n💰 Цена билета: {price} сум\n💵 Оплата: Наличными в кассе",
        "btn_reserve": "📞 Забронировать место",
        "btn_back": "⬅️ Назад к афише",
        "reserve_info": f"📞 **Бронирование билетов**\n\nДля бронирования мест на фильм **«{{title}}»** позвоните по номеру:\n👉 `{ADMIN_PHONE}`\n\n*(Назовите кассиру фильм, время сеанса и количество мест)*"
    },
    "uz": {
        "welcome": "👋 **«Festival» kinoteatriga xush kelibsiz!**\n\nIltimos, xizmat ko'rsatish tilini tanlang:",
        "main_menu": "🎬 **Asosiy menyu**\nKerakli bo'limni tanlang:",
        "btn_catalog": "🍿 Filmlar afishasi",
        "btn_contact": "📞 Kontaktlar va manzil",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "contacts": f"📍 **«Festival» kinoteatri**\n📞 Bron qilish va ma'lumot: {ADMIN_PHONE}\n🏢 Manzil: «Festival» KSM\n💵 To'lov **faqat naqd pulda** kassa orqali amalga oshiriladi.",
        "select_movie": "🎟 **Afishadan filmni tanlang:**",
        "movie_info": "🎬 **{title}**\n\n⏰ Seanslar: {time}\n💰 Chipta narxi: {price} so'm\n💵 To'lov: Kassada naqd pulda",
        "btn_reserve": "📞 Joyni bron qilish",
        "btn_back": "⬅️ Afishaga orqaga",
        "reserve_info": f"📞 **Chiptalarni bron qilish**\n\n**«{{title}}»** filmiga joylarni bron qilish uchun ushbu raqamga qo'ng'iroq qiling:\n👉 `{ADMIN_PHONE}`\n\n*(Kassirga film nomi, seans va joylar sonini ayting)*"
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
    buttons = []
    for m in MOVIES:
        title = m["title_ru"] if lang == "ru" else m["title_uz"]
        buttons.append([InlineKeyboardButton(text=title, callback_data=f"movie_{m['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_detail_keyboard(lang, movie_id):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_reserve"], callback_data=f"reserve_{movie_id}")],
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


@dp.callback_query(F.data.startswith("reserve_"))
async def reserve_ticket(call: types.CallbackQuery):
    lang = user_data.get(call.from_user.id, {}).get("lang", "ru")
    movie_id = int(call.data.split("_")[1])
    movie = next((m for m in MOVIES if m["id"] == movie_id), None)

    if movie:
        title = movie["title_ru"] if lang == "ru" else movie["title_uz"]
        msg_text = TEXTS[lang]["reserve_info"].format(title=title)

        back_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["btn_back"], callback_data="back_catalog")]
        ])

        try:
            await call.message.delete()
        except Exception:
            pass

        await call.message.answer(msg_text, reply_markup=back_kb, parse_mode="Markdown")


# ==========================================
# 5. ОСНОВНОЙ ЗАПУСК
# ==========================================
async def main():
    print(f"Бот ТЦ «Фестиваль» успешно запущен. Телефон бронирования: {ADMIN_PHONE}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
