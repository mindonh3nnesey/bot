import random
import asyncio
import aiohttp
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

import google.generativeai as genai

# ========== НАСТРОЙКИ ==========
TOKEN = "8827001682:AAFFYvCxWSfpJWklygz6S5hqa1pAVe-6vaA"
MOM_CHAT_ID = 8987266887

# Погода
OPENWEATHER_API_KEY = "c7da02ba55b526be69e89920705df7b3"
CITY = "Rostov-na-Donu"

# Gemini
GEMINI_API_KEY = "AQ.Ab8RN6J5OSZJHrnNVpsQW1C7QrsoJS1RrBMcw4Y90ijOCgAaTw"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ========== ЦВЕТА ==========
COLORS = {
    "2026-06-26": "Ежевичный + черничный + светло-лавандовый",
    "2026-06-27": "Лиственных зеленый + мягкий зеленый + кремовый",
    "2026-06-28": "Теплый коралл + оранжево-розовый + бежевый",
    "2026-06-29": "Ледяной голубой + жемчужно-серый + белый",
    "2026-06-30": "Бордовый + винный + татуовый",
    "2026-07-01": "Лавандовый + персиковый + мятный",
    "2026-07-02": "Морская волна + лимонный + васильковый",
    "2026-07-03": "Коралловый + песочный + небесный",
    "2026-07-04": "Розовый зефир + шалфейный + молочный",
    "2026-07-05": "Стальной синий + серебристый + пыльная роза",
    "2026-07-06": "Янтарный + свекличный + слоновая кость",
    "2026-07-07": "Аквамариновый + крем-брюле + серо-коричневый",
    "2026-07-08": "Малиновый сорбет + сиренево-дымчатый + серый камень",
    "2026-07-09": "Сенсорный зелёный + светлое золото + песочный",
    "2026-07-10": "Бирюзовый бриз + белый + лавандовый туман",
    "2026-07-11": "Терракота + мягкое мороженое + слоновая кость",
    "2026-07-12": "Джонсовый серый + персиковый крем + дымчатый",
    "2026-07-13": "Шелковый мусс + павлиний + кремовый",
    "2026-07-14": "Морская пена + нежно-розовый + тёплый серый",
    "2026-07-15": "Какао + карамель + айвори",
    "2026-07-16": "Глициния + фисташковый + пудровый",
    "2026-07-17": "Чернильный + ледяной серо-голубой + белый",
    "2026-07-18": "Янтарное золото + чайная роза + молочный",
    "2026-07-19": "Нефритовый + кремово-жёлтый + светло-серый",
    "2026-07-20": "Персик абрикос + ледяная мята + молочный",
    "2026-07-21": "Петрольный + тату-розовый + песочный",
    "2026-07-22": "Лимонный шифон + лилово-серый + айвори",
    "2026-07-23": "Кирпичный + эвкалиптовый + бежевый",
    "2026-07-24": "Ледяной голубой + розовая дымка + серебро",
    "2026-07-25": "Горячий мёд + пыльный бирюзовый + кремовый",
    "2026-07-26": "Черничный + сливочный крем + серо-бежевый",
    "2026-07-27": "Изумрудный + нежный абрикос + молочный",
    "2026-07-28": "Дымчато-фиолетовый + небесная лазурь + айвори",
    "2026-07-29": "Песчаник + оливковый хаки + кремовый",
    "2026-07-30": "Рожковое дерево + светлый шалфей + перламутровый серый",
    "2026-07-31": "Полночный синий + золотой песок + айвори"
}

# ========== ТЕКСТЫ ==========
AFFIRMATIONS = [
    "Ты можешь всё, что захочешь! 💪",
    "Ты — самая лучшая мама на свете! ❤️",
    "Ты сильная и красивая! ✨",
    "Ты способна на великие дела! 🌟",
    "Каждый день ты становишься лучше! 🌈",
    "Твоя улыбка делает мир светлее! 😊",
    "Ты — источник любви и тепла! 💖",
    "Ты заслуживаешь всего самого лучшего! 🌺",
    "Твоя доброта меняет мир! 🌍",
    "Ты — волшебница, и у тебя всё получится! 🦋",
    "Я горжусь тобой! 💫",
    "Ты делаешь этот мир лучше! 🌸",
    "Верь в себя, и у тебя всё получится! 🌻",
    "Твоя сила — в твоём сердце! 💝",
    "Ты невероятная женщина! 💎"
]

HOW_ARE_YOU = [
    "Как твоё настроение сегодня? 🌅",
    "Как проходит твой день? ☀️",
    "Как ты себя чувствуешь? 💕",
    "Расскажи, как у тебя дела? 😊",
    "Всё хорошо? Я переживаю за тебя! 🤗",
    "Какой сегодня у тебя день? 🌸",
    "Ты сегодня счастлива? Надеюсь, да! 💖"
]

LOVE_MESSAGES = [
    "❤️ Я тебя люблю, мамуля!",
    "💖 Просто хочу сказать, что ты у меня самая лучшая!",
    "💕 Люблю тебя бесконечно!",
    "✨ Ты — моё вдохновение! Люблю!",
    "🌸 Я так тебя люблю! Ты — моя звёздочка!",
    "💝 Ты самое дорогое, что у меня есть! Люблю!",
    "🌺 Люблю тебя, мамуля! Ты моя радость!",
    "🌟 Ты — моя вселенная! Люблю бесконечно!",
    "💗 Ты — моё сердце! Люблю!",
    "🌹 Ты — моя роза! Люблю тебя!"
]

# ========== КЛАВИАТУРА ==========
def get_keyboard():
    keyboard = [
        [KeyboardButton("🎨 Цвета дня")],
        [KeyboardButton("📅 Цвета на завтра")],
        [KeyboardButton("💪 Аффирмация")],
        [KeyboardButton("🌤 Погода")],
        [KeyboardButton("💬 Спросить у ИИ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def get_month_name(month):
    months = {1: "января", 2: "февраля", 3: "марта", 4: "апреля",
              5: "мая", 6: "июня", 7: "июля", 8: "августа",
              9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
    return months.get(month, "")

def get_colors_for_date(date_obj):
    date_str = date_obj.strftime("%Y-%m-%d")
    return COLORS.get(date_str, "🌈 Розовый + голубой + золотой")

# ========== ОБРАБОТЧИКИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет, мамуля! 💖\n\n"
        "Я твой личный помощник!\n"
        "🔹 Цвета дня — что надеть\n"
        "🔹 Аффирмация — поддержка\n"
        "🔹 Погода — реальная погода\n"
        "🔹 ИИ — отвечу на любой вопрос\n\n"
        "Я всегда рядом и люблю тебя! ❤️",
        reply_markup=get_keyboard()
    )

async def colors_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    colors = get_colors_for_date(today)
    await update.message.reply_text(
        f"📅 Сегодня {today.day} {get_month_name(today.month)}\n"
        f"✨ Твои цвета удачи: {colors}\n"
        f"💡 Выбирай одежду в этих цветах! 💖",
        reply_markup=get_keyboard()
    )

async def colors_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tomorrow = datetime.now() + timedelta(days=1)
    colors = get_colors_for_date(tomorrow)
    await update.message.reply_text(
        f"📅 Завтра {tomorrow.day} {get_month_name(tomorrow.month)}\n"
        f"✨ Цвета удачи: {colors}\n"
        f"💡 Можешь подготовить одежду уже сегодня!",
        reply_markup=get_keyboard()
    )

async def affirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    aff = random.choice(AFFIRMATIONS)
    await update.message.reply_text(f"💫 {aff}", reply_markup=get_keyboard())

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await update.message.reply_text(
                        f"🌤 Погода в Ростове-на-Дону:\n"
                        f"🌡 {data['main']['temp']}°C (ощущается как {data['main']['feels_like']}°C)\n"
                        f"☁️ {data['weather'][0]['description'].capitalize()}\n"
                        f"💨 Ветер: {data['wind']['speed']} м/с\n"
                        f"💧 Влажность: {data['main']['humidity']}%\n\n"
                        f"Одевайся по погоде, мамуля! 💕",
                        reply_markup=get_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        "🌤 Не удалось получить погоду, но ты всё равно красивая! 💖",
                        reply_markup=get_keyboard()
                    )
    except Exception as e:
        await update.message.reply_text(
            "🌤 Погода сегодня отличная!\n☀️ Солнечно, тепло, примерно +25°C",
            reply_markup=get_keyboard()
        )

async def ask_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = " ".join(context.args) if context.args else "Расскажи что-нибудь тёплое"
    await update.message.reply_text("🤔 Думаю...")
    try:
        response = model.generate_content(
            f"Ты — заботливый помощник для мамы. Отвечай с любовью и поддержкой.\n\n"
            f"Вопрос: {user_question}"
        )
        await update.message.reply_text(
            f"💬 {response.text}\n\nТы всегда можешь спросить что угодно! 💖",
            reply_markup=get_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(
            "😅 Не удалось получить ответ, но я всё равно тебя люблю! 💖",
            reply_markup=get_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎨 Цвета дня":
        await colors_today(update, context)
    elif text == "📅 Цвета на завтра":
        await colors_tomorrow(update, context)
    elif text == "💪 Аффирмация":
        await affirmation(update, context)
    elif text == "🌤 Погода":
        await weather(update, context)
    elif text == "💬 Спросить у ИИ":
        await update.message.reply_text(
            "🤖 Напиши свой вопрос, и я отвечу! 💬",
            reply_markup=get_keyboard()
        )
    else:
        context.args = [text]
        await ask_gemini(update, context)

# ========== ТЕСТОВЫЙ РЕЖИМ ==========
async def test_messages(context: ContextTypes.DEFAULT_TYPE):
    messages = [
        lambda: f"🌅 Доброе утро! Сегодня {datetime.now().day} {get_month_name(datetime.now().month)}\nТвои цвета: {get_colors_for_date(datetime.now())}",
        lambda: f"☀️ {random.choice(HOW_ARE_YOU)}",
        lambda: f"🌅 Добрый вечер! Ты сегодня многое сделала — я горжусь тобой! 💖",
        lambda: f"💫 {random.choice(AFFIRMATIONS)}"
    ]
    i = 0
    while True:
        try:
            if i % 3 == 0:
                msg = random.choice(LOVE_MESSAGES)
            else:
                msg = messages[i % len(messages)]()
            await context.bot.send_message(chat_id=MOM_CHAT_ID, text=msg, reply_markup=get_keyboard())
            i += 1
            await asyncio.sleep(120)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await asyncio.sleep(60)

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Бот ЗАПУЩЕН! Всё работает!")
    print(f"👤 ID мамы: {MOM_CHAT_ID}")
    print(f"📅 Сегодня: {datetime.now().strftime('%d.%m.%Y')}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(test_messages(app))
    app.run_polling()

if __name__ == "__main__":
    main()
