import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Подключение к базе данных
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, referred_by INTEGER)")

# Загрузка списка кранов
with open("faucets.json", "r", encoding="utf-8") as f:
    faucets = json.load(f)

# Список крипто-игр
games = [
    {"name": "Rollercoin", "link": "https://rollercoin.com/?r=yourref"},
    {"name": "Coin Hunt World", "link": "https://coinhunt.gsc.im"},
    {"name": "CryptoBlades", "link": "https://app.cryptoblades.io"},
    {"name": "Alien Worlds", "link": "https://play.alienworlds.io"},
    {"name": "Womplay", "link": "https://womplay.io"}
]

# Команда /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    ref = message.text.split()[1] if len(message.text.split()) > 1 else None
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, ref))
        conn.commit()
    welcome_text = (
        "👋 Добро пожаловать в крипто-кран бот!\n\n"
        "Здесь ты найдёшь лучшие сайты и игры для заработка криптовалюты 💸\n\n"
        "📋 Нажми «Краны» — и начни зарабатывать прямо сейчас!\n"
        "🎮 Или выбери «Игры» — и играй, получая крипту!\n"
        "👥 Приглашай друзей и получай бонусы за каждого реферала."
    )
    bot.send_message(user_id, welcome_text)
    show_menu(user_id)

# Меню
def show_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📋 Краны", callback_data="faucets"),
        InlineKeyboardButton("🎮 Игры", callback_data="games")
    )
    markup.add(InlineKeyboardButton("👥 Рефералы", callback_data="ref"))
    bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)

# Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "faucets":
        text = "🧴 <b>Список кранов:</b>\n\n"
        for f in faucets:
            text += f"🔹 <b>{f['name']}</b> — <a href='{f['link']}'>Перейти</a>\n"
        text += "\n👉 Используй наш бот: @Crypt0RainBot"
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", disable_web_page_preview=True)

    elif call.data == "games":
        text = "🎮 <b>Игры с заработком криптовалюты:</b>\n\n"
        for g in games:
            text += f"🕹 <b>{g['name']}</b> — <a href='{g['link']}'>Играть</a>\n"
        text += "\n👉 Используй наш бот: @Crypt0RainBot"
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", disable_web_page_preview=True)

    elif call.data == "ref":
        user_id = call.from_user.id
        cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,))
        count = cursor.fetchone()[0]
        username = bot.get_me().username
        referral_text = (
            f"👥 У вас {count} рефералов\n"
            f"🔗 Ваша ссылка:\n"
            f"https://t.me/{username}?start={user_id}"
        )
        bot.send_message(user_id, referral_text)

# Запуск бота
print("✅ Бот запущен и ждёт команд...")
try:
    bot.infinity_polling()
except Exception as e:
    print("❌ Ошибка при запуске бота:", e)
