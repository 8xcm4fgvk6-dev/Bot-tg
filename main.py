from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

TOKEN = "BOT_TOKENNI_BU_YERGA_QOY"
ADMIN_ID = 123456789
CHANNEL_ID = "@kanalingiz"

bot = Bot(TOKEN)
dp = Dispatcher(bot)

# SQLite bazaga ulanish
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎬 Kino ro‘yxati", callback_data="list"))
    kb.add(InlineKeyboardButton("ℹ️ Admin", callback_data="admin"))
    return kb

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    member = await bot.get_chat_member(CHANNEL_ID, msg.from_user.id)
    if member.status in ["left", "kicked"]:
        await msg.answer(f"⚠️ Avval kanalga obuna bo‘ling: {CHANNEL_ID}")
        return
    await msg.answer("🎬 Kino botga xush kelibsiz!\nKino kodini yuboring yoki menyudan tanlang", reply_markup=main_menu())

@dp.callback_query_handler()
async def callbacks(call: types.CallbackQuery):
    if call.data == "list":
        cursor.execute("SELECT code FROM movies")
        codes = cursor.fetchall()
        movie_list = "\n".join([c[0] for c in codes]) or "❌ Kino yo‘q"
        await call.message.answer(f"🎬 Kino kodlari:\n{movie_list}")
    elif call.data == "admin":
        if call.from_user.id != ADMIN_ID:
            await call.message.answer("❌ Siz admin emassiz")
            return
        await call.message.answer("📥 Kino qo‘shish uchun video yuboring va reply qilib `/save KOD` deb yozing", parse_mode="Markdown")

@dp.message_handler(commands=['save'])
async def save_movie(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    if not msg.reply_to_message or not msg.reply_to_message.video:
        await msg.answer("❌ Videoga reply qilib yuboring")
        return
    try:
        code = msg.text.split()[1]
    except IndexError:
        await msg.answer("❌ Kodni yozing, masalan: /save A13")
        return
    file_id = msg.reply_to_message.video.file_id
    cursor.execute("INSERT OR REPLACE INTO movies (code, file_id) VALUES (?, ?)", (code, file_id))
    conn.commit()
    await msg.answer(f"✅ Kino saqlandi! Kod: {code}")

@dp.message_handler()
async def send_movie(msg: types.Message):
    code = msg.text.strip()
    cursor.execute("SELECT file_id, views FROM movies WHERE code=?", (code,))
    result = cursor.fetchone()
    if result:
        file_id, views = result
        await msg.answer_video(file_id)
        cursor.execute("UPDATE movies SET views = views + 1 WHERE code=?", (code,))
        conn.commit()
    else:
        await msg.answer("❌ Bunday kod topilmadi")

if __name__ == "__main__":
    executor.start_polling(dp)
