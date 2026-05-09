import telebot
import requests
import re
import datetime
import os
import threading
import time
from flask import Flask

# ===================== ТАНЗИМОТ =====================
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "8710051156:AAGsowg5DhvLjI7xyrgWoD0O74cCEGrTeik")
FF_API_URL  = "https://info-ob49.onrender.com/api/account/"
BAN_API_URL = "https://bancheck-xprince.onrender.com/checkban"
FF_REGIONS  = ["IND","BD","SG","ID","VN","TH","ME","TW","BR","RU","PK","CIS","US"]
PORT        = int(os.environ.get("PORT", 8080))
# =====================================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ─── FLASK ───────────────────────────────────────────
@app.route('/')
def index(): return "✅ zadxpro running!", 200

@app.route('/health')
def health(): return "OK", 200

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

# ─── HELPERS ─────────────────────────────────────────
def fmt_date(ts):
    try: return datetime.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
    except: return "—"

RANK_MAP = {
    301:"Бронза I",  302:"Бронза II",  303:"Бронза III",
    304:"Нуқра I",   305:"Нуқра II",   306:"Нуқра III",
    307:"Тилло I",   308:"Тилло II",   309:"Тилло III",
    310:"Платина",   311:"Алмос",      312:"Устод",
    313:"Гроссмайстер", 314:"Чэллэнҷер"
}
def rank(r): return RANK_MAP.get(r, "#" + str(r) if r else "—")

GENDER = {"Gender_MALE":"👨 Мард", "Gender_FEMALE":"👩 Зан"}
MODE   = {"ModePrefer_BR":"Battle Royale", "ModePrefer_CS":"Clash Squad"}
TACT   = {"TimeActive_NIGHT":"🌙 Шаб", "TimeActive_DAY":"☀️ Рӯз", "TimeActive_EVENING":"🌆 Бегох"}

def get_ff(uid):
    for region in FF_REGIONS:
        try:
            url = FF_API_URL + "?uid=" + uid + "&region=" + region
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get("basicInfo", {}).get("nickname"):
                    return d
        except:
            continue
    return None

def get_ban(uid):
    try:
        r = requests.get(BAN_API_URL + "?uid=" + uid, timeout=8)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# ─── /start ──────────────────────────────────────────
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    text = (
        "🎮 <b>Free Fire Info Bot</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 Командаҳо:\n\n"
        "🔍 /check <code>UID</code> — маълумоти бозингар\n"
        "🚫 /ban <code>UID</code> — санҷидани бан\n\n"
        "Мисол: /check 8898233939\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>🤖 zadxpro bot</i>"
    )
    bot.send_message(msg.chat.id, text, parse_mode="HTML")

# ─── /check UID ──────────────────────────────────────
@bot.message_handler(commands=['check'])
def cmd_check(msg):
    args = msg.text.strip().split()
    if len(args) < 2 or not args[1].isdigit():
        bot.reply_to(msg, "❗ Истифода: /check UID\nМисол: /check 8898233939")
        return

    uid  = args[1]
    wait = bot.reply_to(msg, "🔍 Дар ҷустуҷӯ...")
    data = get_ff(uid)
    ban  = get_ban(uid)

    try: bot.delete_message(msg.chat.id, wait.message_id)
    except: pass

    if not data:
        bot.reply_to(msg, "❌ UID " + uid + " ёфт нашуд!")
        return

    b    = data.get("basicInfo", {})
    c    = data.get("clanBasicInfo", {})
    s    = data.get("socialInfo", {})
    cr   = data.get("creditScoreInfo", {})
    diam = data.get("diamondCostRes", {})
    pet  = data.get("petInfo", {})

    sig = re.sub(r'\[.*?\]', '', s.get("signature", "")).strip() or "—"

    # Бан статус
    if ban:
        is_banned = (
            ban.get("is_banned") or
            ban.get("banned") or
            ban.get("status") == "banned" or
            str(ban.get("ban_status", "")).lower() in ["banned", "true", "1"]
        )
        ban_status = "🚫 БАН ШУДААСТ" if is_banned else "✅ Бан нест"
    else:
        ban_status = "❓ Санҷида нашуд"

    clan_name = c.get("clanName", "—") if c else "—"
    clan_mem  = (str(c.get("memberNum", "—")) + "/" + str(c.get("capacity", "—"))) if c else "—"

    text = (
        "🎮 <b>Free Fire Info</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>Ник:</b>         " + str(b.get("nickname", "—")) + "\n"
        "🆔 <b>UID:</b>         <code>" + str(b.get("accountId", uid)) + "</code>\n"
        "🌍 <b>Регион:</b>      " + str(b.get("region", "—")) + "\n"
        "⭐ <b>Сатх:</b>        " + str(b.get("level", "—")) + "\n"
        "📊 <b>Тачриба:</b>     " + str(b.get("exp", "—")) + "\n"
        "🏅 <b>Ранг BR:</b>     " + rank(b.get("rank")) + "\n"
        "🏆 <b>Ранг CS:</b>     " + rank(b.get("csRank")) + "\n"
        "🔝 <b>Макс ранг:</b>   " + rank(b.get("maxRank")) + "\n"
        "❤️ <b>Лайк:</b>        " + str(b.get("liked", "—")) + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏰 <b>Клан:</b>        " + clan_name + "\n"
        "👥 <b>Аъзои клан:</b>  " + clan_mem + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚧  <b>Ҷинс:</b>       " + GENDER.get(s.get("gender", ""), "—") + "\n"
        "🎯 <b>Реҷа:</b>        " + MODE.get(s.get("modePrefer", ""), "—") + "\n"
        "⏰ <b>Фаъолият:</b>    " + TACT.get(s.get("timeActive", ""), "—") + "\n"
        "💬 <b>Биография:</b>   " + sig + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 <b>Алмос:</b>       " + str(diam.get("diamondCost", "—")) + "\n"
        "🌟 <b>Кредит:</b>      " + str(cr.get("creditScore", "—")) + "/100\n"
        "🐾 <b>Pet сатх:</b>    " + str(pet.get("level", "—")) + "\n"
        "📅 <b>Рӯзи сохт:</b>  " + fmt_date(b.get("createAt", 0)) + "\n"
        "🕐 <b>Охирин вход:</b> " + fmt_date(b.get("lastLoginAt", 0)) + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚫 <b>Бан:</b>         " + ban_status + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>🤖 zadxpro bot</i>"
    )
    bot.reply_to(msg, text, parse_mode="HTML")

# ─── /ban UID ────────────────────────────────────────
@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    args = msg.text.strip().split()
    if len(args) < 2 or not args[1].isdigit():
        bot.reply_to(msg, "❗ Истифода: /ban UID\nМисол: /ban 8898233939")
        return

    uid  = args[1]
    wait = bot.reply_to(msg, "🔍 Бан санҷида дорем...")
    ban  = get_ban(uid)

    try: bot.delete_message(msg.chat.id, wait.message_id)
    except: pass

    if not ban:
        bot.reply_to(msg, "❌ Маълумот гирифта нашуд!")
        return

    is_banned = (
        ban.get("is_banned") or
        ban.get("banned") or
        ban.get("status") == "banned" or
        str(ban.get("ban_status", "")).lower() in ["banned", "true", "1"]
    )

    if is_banned:
        text = "🚫 <b>UID " + uid + " БАН ШУДААСТ!</b>"
    else:
        text = "✅ <b>UID " + uid + " бан нашудааст!</b>"

    bot.reply_to(msg, text, parse_mode="HTML")

# ─── MAIN ────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 zadxpro bot starting on Railway...")
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Polling started!")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
