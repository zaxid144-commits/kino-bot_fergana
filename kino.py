import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# ----------------------------------------------------
# НАСТРОЙКИ БОТА И АДМИНИСТРАТОРА
# ----------------------------------------------------
BOT_TOKEN = "8995206672:AAFKlE6d86dZ1BaiZv1T4qJpbGoMXs9JTBE"
ADMIN_PHONE = "+998 99 272 29 10"
ADMIN_CHAT_ID = 123456789  # Укажите ваш ID в Telegram для получения уведомлений о брони

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище языков пользователей: {user_id: "ru" | "uz"}
user_languages = {}

# ----------------------------------------------------
# ОГРОМНАЯ МНОГОЯЗЫЧНАЯ АФИША (20 ФИЛЬМОВ)
# ----------------------------------------------------
MOVIES = {
    "movie_ted": {
        "title": {"ru": "🧸 Третий лишний (Ted)", "uz": "🧸 Uchinchi ortiqcha (Ted)"},
        "description": {
            "ru": "История о взрослом парне Джоне и его плюшевом говорящем медведе Теде.",
            "uz": "Jon va uning sho'x gapiradigan Ted ayig'i haqidagi mashhur komediya."
        },
        "price_min": 10000, "price_max": 40000,
        "image": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=9fbo_pQvU7M"
    },
    "movie_hangover": {
        "title": {"ru": "🍸 Мальчишник в Вегасе", "uz": "🍸 Vegasdagi ziyofat"},
        "description": {
            "ru": "Друзья просыпаются после безумной вечеринки и пытаются найти пропавшего жениха.",
            "uz": "Do'stlar Las-Vegasdagi shiddatli kechadan so'ng yo'qolgan kuyovni qidirishadi."
        },
        "price_min": 15000, "price_max": 45000,
        "image": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=tcdUhdOlz9M"
    },
    "movie_intouchables": {
        "title": {"ru": "♿️ 1+1 (Неприкасаемые)", "uz": "♿️ 1+1 (Daxlsizlar)"},
        "description": {
            "ru": "Богатый аристократ в инвалидном кресле нанимает в сиделки бывшего заключенного.",
            "uz": "Nogiron aristokrat va uning quvnoq yordamchisi Driss haqidagi samimiy film."
        },
        "price_min": 10000, "price_max": 40000,
        "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=0RqDiYnFxTk"
    },
    "movie_fast5": {
        "title": {"ru": "🚗 Форсаж 5", "uz": "🚗 Forsaj 5"},
        "description": {
            "ru": "Доминик Торетто и его команда собираются в Рио-де-Жанейро для грандиозного ограбления.",
            "uz": "Dominik Toretto va uning jamoasi Rio-de-Janeyroda buyuk o'g'rilikni amalga oshirishadi."
        },
        "price_min": 15000, "price_max": 45000,
        "image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=f23M2L33R3M"
    },
    "movie_dark_knight": {
        "title": {"ru": "🦇 Темный рыцарь", "uz": "🦇 Qora ritsar"},
        "description": {
            "ru": "Бэтмен поднимает ставки в войне с криминалом, противостоя Джокеру.",
            "uz": "Betmen Gotam shahrida Djo'ker bilan to'qnash keladi."
        },
        "price_min": 15000, "price_max": 50000,
        "image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=EXeTwQWrcwY"
    },
    "movie_pirates": {
        "title": {"ru": "🏴‍☠️ Пираты Карибского моря", "uz": "🏴‍☠️ Karib dengizi qaroqchilari"},
        "description": {
            "ru": "Приключения эксцентричного капитана Джека Воробья на морях и океанах.",
            "uz": "Kapitan Djek Chittakning «Qora marvarid» kemasini qaytarish yolidagi sarguzashtlari."
        },
        "price_min": 10000, "price_max": 45000,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=naQr0utrFYU"
    },
    "movie_home_alone": {
        "title": {"ru": "🏠 Один дома", "uz": "🏠 Uyda yolg'iz"},
        "description": {
            "ru": "Кевин случайно остается один дома на Рождество и защищает свой дом от грабителей.",
            "uz": "8 yoshli Kevin tasodifan uyda yolg'iz qolib, uyini ikki o'g'ridan himoya qiladi."
        },
        "price_min": 5000, "price_max": 35000,
        "image": "https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=jEDaVHmw7rI"
    },
    "movie_interstellar": {
        "title": {"ru": "🚀 Интерстеллар", "uz": "🚀 Interstellar"},
        "description": {
            "ru": "Команда исследователей отправляется в космос в поиске нового дома для человечества.",
            "uz": "Tadqiqotchilar jamoasi insoniyat uchun yangi sayyora topish maqsadida koinotga yo'l oladi."
        },
        "price_min": 20000, "price_max": 50000,
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=zSWdZVtXT7E"
    },
    "movie_gladiator": {
        "title": {"ru": "⚔️ Гладиатор", "uz": "⚔️ Gladiator"},
        "description": {
            "ru": "История генерала Максимуса, который вынужден сражаться на арене Колизея.",
            "uz": "Rim generali Maksimusning Kolizey arenasida jang qilishga majbur bo'lganligi haqida."
        },
        "price_min": 10000, "price_max": 40000,
        "image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=owK1qxDselE"
    },
    "movie_matrix": {
        "title": {"ru": "🕶 Матрица", "uz": "🕶 Matritsa"},
        "description": {
            "ru": "Хакер Нео узнает правду об иллюзорности своего мира и вступает в войну с машинами.",
            "uz": "Xaker Neo o'z dunyosining xayoliy ekanligini bilib oladi va urushga kirishadi."
        },
        "price_min": 10000, "price_max": 45000,
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=vKQi3bBA1y8"
    },
    "movie_shrek": {
        "title": {"ru": "🟢 Шрек 2", "uz": "🟢 Shrek 2"},
        "description": {
            "ru": "Шрек и Фиона отправляются в Тридевятое королевство знакомиться с родителями.",
            "uz": "Shrek va Fiona malakaning ota-onasi bilan tanishish uchun yo'l olishadi."
        },
        "price_min": 5000, "price_max": 35000,
        "image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=xBgSfhp5Fxo"
    },
    "movie_harry_potter": {
        "title": {"ru": "⚡️ Гарри Поттер и Философский камень", "uz": "⚡️ Garri Potter va Falsafa toshi"},
        "description": {
            "ru": "Мальчик-сирота узнает, что он волшебник, и отправляется учиться в Хогвартс.",
            "uz": "11 yoshli yetim bola o'zining sehrgar ekanligini bilib, Xogvartsga boradi."
        },
        "price_min": 10000, "price_max": 40000,
        "image": "https://images.unsplash.com/photo-1514539079130-25950c84af65?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=VyHV0BRmydw"
    },
    "movie_spiderman": {
        "title": {"ru": "🕷 Человек-паук: Новый день", "uz": "🕷 O'rmonchi odam: Yangi kun"},
        "description": {
            "ru": "Питер Паркер сталкивается с новыми угрозами на улицах Нью-Йорка.",
            "uz": "Piter Parker Nyu-York ko'chalarida yangi tahdidlarga duch keladi."
        },
        "price_min": 20000, "price_max": 55000,
        "image": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=JfVOs4VSpmA"
    },
    "movie_dune": {
        "title": {"ru": "🎬 Дюна: Часть вторая", "uz": "🎬 Dyuna: Ikkinchi qism"},
        "description": {
            "ru": "Продолжение эпической фантастической саги о Поле Атрейдесе на Арракисе.",
            "uz": "Arrakis sayyorasidagi Pol Atreydes haqidagi epik fantastik saganing davomi."
        },
        "price_min": 25000, "price_max": 55000,
        "image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=Way9Dexny3w"
    },
    "movie_panda": {
        "title": {"ru": "🐼 Кунг-фу Панда 4", "uz": "🐼 Kung-fu Panda 4"},
        "description": {
            "ru": "По отправляется в новое приключение, чтобы стать духовным лидером.",
            "uz": "Po Tinchlik vodiysining ruhiy yetakchisiga aylanish uchun yo'lga tushadi."
        },
        "price_min": 15000, "price_max": 45000,
        "image": "https://images.unsplash.com/photo-1564349683136-77e08dba1ef9?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=_inKs4eeHiI"
    },
    "movie_avatar": {
        "title": {"ru": "🌊 Аватар: Путь воды", "uz": "🌊 Avatar: Suv yo'li"},
        "description": {
            "ru": "Джейк Салли и Нейтири защищают свою семью и океаны Пандоры от новых угроз.",
            "uz": "Djeyk Salli va Neytiri oilasini va Pandora okeanlarini yangi xavflardan himoya qiladi."
        },
        "price_min": 25000, "price_max": 55000,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=d9MyW72ELq0"
    },
    "movie_pulp_fiction": {
        "title": {"ru": "🕶 Криминальное чтиво", "uz": "🕶 Jinoiy qissa"},
        "description": {
            "ru": "Философские разговоры двух бандитов, боксерский поединок и спасение жены босса.",
            "uz": "Ikki jinoiy sherikning falsafiy suhbatlari va xavfli sarguzashtlari."
        },
        "price_min": 10000, "price_max": 40000,
        "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=s7EdQ4FqbhY"
    },
    "movie_avengers": {
        "title": {"ru": "🛡 Мстители: Финал", "uz": "🛡 Qasoskorlar: Intihosi"},
        "description": {
            "ru": "Оставшиеся в живых члены команды Мстителей пытаются исправить последствия щелчка Таноса.",
            "uz": "Qasoskorlar jamoasi Tanosning harakatlari oqibatlarini tuzatishga harakat qilishadi."
        },
        "price_min": 20000, "price_max": 55000,
        "image": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=TcMBFSGVi1c"
    },
    "movie_conjuring": {
        "title": {"ru": "👻 Заклятие", "uz": "👻 La'nat"},
        "description": {
            "ru": "Детективы-паранормалы Эд и Лоррейн Уоррен помогают семье, столкнувшейся с темными силами.",
            "uz": "Ed va Lorreyn Uorren sirli va qo'rqinchli hodisalarga duch kelgan oilaga yordam berishadi."
        },
        "price_min": 10000, "price_max": 45000,
        "image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=k10ETZ41q5o"
    },
    "movie_lion_king": {
        "title": {"ru": "🦁 Король Лев", "uz": "🦁 Qirol Sher"},
        "description": {
            "ru": "История львенка Симбы, проходящего трудный путь от изгнанника до законного короля саванны.",
            "uz": "Kichik Simba sherining qirollik taxtiga bo'lgan mashaqqatli yo'li."
        },
        "price_min": 5000, "price_max": 35000,
        "image": "https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=600&auto=format&fit=crop&q=80",
        "trailer": "https://www.youtube.com/watch?v=4CbLXeG1008"
    }
}

TEXTS = {
    "welcome": {
        "ru": "🍿 **Добро пожаловать в кинотеатр ТЦ «Фестиваль» (г. Фергана)!**\n\nВыберите действие ниже:",
        "uz": "🍿 **«Festival» KSM kinoteatriga xush kelibsiz (Farg'ona sh.)!**\n\nQuyidagi harakatni tanlang:"
    },
    "main_menu": {
        "ru": "🍿 Главное меню кинотеатра ТЦ «Фестиваль»:",
        "uz": "🍿 «Festival» KSM kinoteatri asosiy menyusi:"
    },
    "info": {
        "ru": (
            "📍 **Адрес:** г. Фергана, ТЦ «Фестиваль», 3-й этаж.\n"
            "🎟 **Оплата билетов:** Наличными прямо на кассе перед сеансом.\n"
            f"📞 **Контакты и бронь по телефону:** {ADMIN_PHONE}\n\n"
            "Приятного просмотра!"
        ),
        "uz": (
            "📍 **Manzil:** Farg'ona sh., «Festival» KSM, 3-qavat.\n"
            "🎟 **To'lov:** Seansdan oldin kassada naqd pulda.\n"
            f"📞 **Kontakt va telefon orqali bron:** {ADMIN_PHONE}\n\n"
            "Yoqimli tomosha tilaymiz!"
        )
    },
    "catalog_title": {
        "ru": "🍿 **Афиша фильмов в ТЦ «Фестиваль»:**",
        "uz": "🍿 **«Festival» KSMdagi filmlar afishasi:**"
    },
    "ticket_price": {
        "ru": "💰 **Цена билета:** от {price_min:,} до {price_max:,} сум",
        "uz": "💰 **Chipta narxi:** {price_min:,} so'mdan {price_max:,} so'mgacha"
    },
    "choose_count": {
        "ru": "👥 **На сколько человек забронировать билеты?**\n\n🎬 Фильм: {title}",
        "uz": "👥 **Necha kishi uchun chipta bron qilasiz?**\n\n🎬 Film: {title}"
    },
    "booking_success": {
        "ru": (
            "📌 **БРОНИРОВАНИЕ УСПЕШНО ОФОРМЛЕНО!**\n"
            "------------------------------------\n"
            "🎬 **Фильм:** {title}\n"
            "👥 **Количество человек:** {count} чел.\n"
            "🏬 **Кинотеатр:** ТЦ «Фестиваль» (г. Фергана)\n"
            "🎫 **Код брони:** `{booking_code}`\n"
            "💵 **Итого к оплате на кассе:** ~{total_price:,} сум (зависит от места)\n"
            "------------------------------------\n"
            "📩 Уведомление о вашей брони отправлено администратору.\n\n"
            "⚠️ **ВАЖНО:** Назовите кассиру **код брони** и оплатите билет за 15 минут до начала сеанса!"
        ),
        "uz": (
            "📌 **BRON QILISH MUVAFFAQIYATLI BAJARILDI!**\n"
            "------------------------------------\n"
            "🎬 **Film:** {title}\n"
            "👥 **Odamlar soni:** {count} kishi\n"
            "🏬 **Kinoteatr:** «Festival» KSM (Farg'ona sh.)\n"
            "🎫 **Bron kodi:** `{booking_code}`\n"
            "💵 **Kassada jami to'lov:** ~{total_price:,} so'm (joyga bog'liq)\n"
            "------------------------------------\n"
            "📩 Bron haqidagi xabar administratorga yuborildi.\n\n"
            "⚠️ **MUHIM:** Kassirga **bron kodini** ayting va seansdan 15 daqiqa oldin to'lov qiling!"
        )
    }
}


# ----------------------------------------------------
# КЛАВИАТУРЫ
# ----------------------------------------------------
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ])


def main_keyboard(lang):
    catalog_btn = "🎟 Посмотреть афишу" if lang == "ru" else "🎟 Filmlar afishasi"
    info_btn = "📍 Локация и контакты" if lang == "ru" else "📍 Manzil va kontaktlar"
    change_lang_btn = "🌐 Сменить язык / Tilni o'zgartirish"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=catalog_btn, callback_data="catalog")],
        [InlineKeyboardButton(text=info_btn, callback_data="info")],
        [InlineKeyboardButton(text=change_lang_btn, callback_data="change_lang")]
    ])


def movies_keyboard(lang):
    buttons = []
    for movie_id, data in MOVIES.items():
        title = data["title"][lang]
        buttons.append([InlineKeyboardButton(text=title, callback_data=f"select_{movie_id}")])

    back_btn = "⬅️ Главное меню" if lang == "ru" else "⬅️ Asosiy menyu"
    buttons.append([InlineKeyboardButton(text=back_btn, callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def movie_details_keyboard(movie_id, trailer_url, lang):
    reserve_btn = "🎟 Забронировать (Наличными)" if lang == "ru" else "🎟 Bron qilish (Naqd pul)"
    trailer_btn = "🎬 Смотреть трейлер" if lang == "ru" else "🎬 Treylerni tomosha qilish"
    back_btn = "⬅️ К списку фильмов" if lang == "ru" else "⬅️ Filmlar ro'yxatiga"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=reserve_btn, callback_data=f"startreserve_{movie_id}")],
        [InlineKeyboardButton(text=trailer_btn, url=trailer_url)],
        [InlineKeyboardButton(text=back_btn, callback_data="catalog")]
    ])


def persons_count_keyboard(movie_id, lang):
    buttons = [
        [
            InlineKeyboardButton(text="1 чел", callback_data=f"reserve_{movie_id}_1"),
            InlineKeyboardButton(text="2 чел", callback_data=f"reserve_{movie_id}_2"),
            InlineKeyboardButton(text="3 чел", callback_data=f"reserve_{movie_id}_3")
        ],
        [
            InlineKeyboardButton(text="4 чел", callback_data=f"reserve_{movie_id}_4"),
            InlineKeyboardButton(text="5 чел", callback_data=f"reserve_{movie_id}_5")
        ]
    ]
    back_btn = "⬅️ Назад" if lang == "ru" else "⬅️ Orqaga"
    buttons.append([InlineKeyboardButton(text=back_btn, callback_data=f"select_{movie_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ----------------------------------------------------
# ХЕНДЛЕРЫ
# ----------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = "Пожалуйста, выберите язык / Iltimos, tilni tanlang:"
    await message.answer(welcome_text, reply_markup=lang_keyboard())


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.split("_")[1]
    user_languages[call.from_user.id] = lang

    await call.message.edit_text(
        TEXTS["welcome"][lang],
        reply_markup=main_keyboard(lang),
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data == "change_lang")
async def change_language(call: CallbackQuery):
    await call.message.edit_text(
        "Пожалуйста, выберите язык / Iltimos, tilni tanlang:",
        reply_markup=lang_keyboard()
    )
    await call.answer()


@dp.callback_query(F.data == "main_menu")
async def back_to_main(call: CallbackQuery):
    lang = user_languages.get(call.from_user.id, "ru")
    await call.message.edit_text(TEXTS["main_menu"][lang], reply_markup=main_keyboard(lang))
    await call.answer()


@dp.callback_query(F.data == "info")
async def show_info(call: CallbackQuery):
    lang = user_languages.get(call.from_user.id, "ru")
    back_btn = "⬅️ Назад" if lang == "ru" else "⬅️ Orqaga"

    await call.message.edit_text(
        TEXTS["info"][lang],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=back_btn, callback_data="main_menu")]
        ]),
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    lang = user_languages.get(call.from_user.id, "ru")
    await call.message.edit_text(
        TEXTS["catalog_title"][lang],
        reply_markup=movies_keyboard(lang),
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data.startswith("select_"))
async def select_movie(call: CallbackQuery):
    lang = user_languages.get(call.from_user.id, "ru")
    movie_id = call.data.replace("select_", "")
    movie = MOVIES.get(movie_id)

    if movie:
        title = movie["title"][lang]
        description = movie["description"][lang]
        price_str = TEXTS["ticket_price"][lang].format(
            price_min=movie["price_min"],
            price_max=movie["price_max"]
        )

        caption = (
            f"🎬 **{title}**\n\n"
            f"📝 {description}\n\n"
            f"{price_str}"
        )
        await call.message.answer_photo(
            photo=movie["image"],
            caption=caption,
            reply_markup=movie_details_keyboard(movie_id, movie["trailer"], lang),
            parse_mode="Markdown"
        )
        await call.message.delete()
    await call.answer()


# Шаг 1 бронирования: выбор количества человек
@dp.callback_query(F.data.startswith("startreserve_"))
async def choose_persons(call: CallbackQuery):
    lang = user_languages.get(call.from_user.id, "ru")
    movie_id = call.data.replace("startreserve_", "")
    movie = MOVIES.get(movie_id)

    if movie:
        title = movie["title"][lang]
        msg = TEXTS["choose_count"][lang].format(title=title)
        await call.message.answer(msg, reply_markup=persons_count_keyboard(movie_id, lang), parse_mode="Markdown")
    await call.answer()


# Шаг 2 бронирования: фиксация брони на выбранное число человек
@dp.callback_query(F.data.startswith("reserve_"))
async def process_reservation(call: CallbackQuery):
    lang = user_languages.get(call.from_user.id, "ru")
    parts = call.data.split("_")
    movie_id = f"{parts[1]}_{parts[2]}"
    count = int(parts[3])
    movie = MOVIES.get(movie_id)

    if movie:
        title_ru = movie["title"]["ru"]
        title_user = movie["title"][lang]
        booking_code = f"FEST-{random.randint(10000, 99999)}"
        user = call.from_user
        total_price = movie["price_max"] * count

        # 1. Ответ пользователю
        user_msg = TEXTS["booking_success"][lang].format(
            title=title_user,
            count=count,
            booking_code=booking_code,
            total_price=total_price
        )
        await call.message.answer(user_msg, parse_mode="Markdown")

        # 2. Уведомление администратору в Telegram
        admin_notice = (
            f"🔔 **НОВАЯ БРОНЬ (НА {count} ЧЕЛ.)!**\n"
            f"------------------------------------\n"
            f"🎬 **Фильм:** {title_ru}\n"
            f"👥 **Человек:** {count} чел.\n"
            f"🎫 **Код брони:** `{booking_code}`\n"
            f"💵 **Примерная сумма:** ~{total_price:,} сум\n"
            f"👤 **Клиент:** @{user.username if user.username else 'Без username'} ({user.full_name})\n"
            f"📞 **Телефон админа:** {ADMIN_PHONE}\n"
            f"------------------------------------"
        )
        try:
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notice, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Не удалось отправить уведомление администратору: {e}")

    await call.answer()


# ----------------------------------------------------
# ЗАПУСК БОТА
# ----------------------------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    print(f"Бот ТЦ «Фестиваль» запущен. Номер администратора: {ADMIN_PHONE}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())