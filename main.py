import os
import re
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== ТРАНСКРИПЦИЯ ==================
TRANS = {
    "ا": "a", "ب": "b", "ت": "t", "ث": "th", "ج": "j",
    "ح": "ḥ", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r",
    "ز": "z", "س": "s", "ش": "sh", "ص": "ṣ", "ض": "ḍ",
    "ط": "ṭ", "ظ": "ẓ", "ع": "ʿ", "غ": "gh", "ف": "f",
    "ق": "q", "ك": "k", "ل": "l", "م": "m", "ن": "n",
    "ه": "h", "و": "w", "ي": "y", "ء": "ʼ",
    "ى": "ā", "ة": "h"
}

def transliterate(text: str) -> str:
    return "".join(TRANS.get(ch, ch) for ch in text)

# ================== ТАДЖВИД ==================
def tajweed_rules(text: str) -> str:
    rules = []

    izhar = "ءهعحغخ"
    idgham_ghunna = "ينمو"
    idgham_no_ghunna = "لر"
    ikhfa = "تثجدذزسشصضطظفقك"

    for i in range(len(text) - 1):
        ch, nxt = text[i], text[i + 1]

        # Нун сакина / танвин
        if ch == "ن" or ch in "ًٌٍ":
            if nxt in izhar:
                rules.append(f"Изхар: ن/танвин + {nxt}")
            elif nxt in idgham_ghunna:
                rules.append(f"Идгам с гунной: ن/танвин + {nxt}")
            elif nxt in idgham_no_ghunna:
                rules.append(f"Идгам без гунны: ن/танвин + {nxt}")
            elif nxt == "ب":
                rules.append("Икляб: ن/танвин + ب")
            elif nxt in ikhfa:
                rules.append(f"Ихфа: ن/танвин + {nxt}")

        # Мим сакина
        if ch == "م":
            if nxt == "م":
                rules.append("Идгам шафауи: م + م")
            elif nxt == "ب":
                rules.append("Ихфа шафауи: م + ب")
            else:
                rules.append(f"Изхар шафауи: م + {nxt}")

    return "\n".join(dict.fromkeys(rules)) or "Явных правил таджвида не найдено"

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕌 Отправь арабский текст — я выдам:\n"
        "• транскрипцию\n"
        "• правила таджвида"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    response = (
        f"📖 Текст:\n{text}\n\n"
        f"🔤 Транскрипция:\n{transliterate(text)}\n\n"
        f"📘 Таджвид:\n{tajweed_rules(text)}"
    )

    await update.message.reply_text(response)

# ================== ЗАПУСК ==================
def main():
    if not TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не задан")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Bot started")
    app.run_polling()

if _name_ == "_main_":
    main()
