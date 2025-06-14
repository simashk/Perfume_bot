
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import requests
from bs4 import BeautifulSoup

# مراحل گفتگو
STYLE, TONE, SITUATION, GENDER = range(4)

# ذخیره داده کاربران
user_data = {}

# شروع گفتگو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌸 گلی", callback_data='گلی')],
        [InlineKeyboardButton("🌳 چوبی", callback_data='چوبی')],
        [InlineKeyboardButton("🍋 مرکباتی", callback_data='مرکباتی')],
        [InlineKeyboardButton("🔥 شرقی", callback_data='شرقی')],
    ]
    await update.message.reply_text("👃 سبک رایحه مورد علاقه‌ات چیه؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return STYLE

# انتخاب سبک
async def select_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id] = {'style': query.data}
    keyboard = [
        [InlineKeyboardButton("😋 شیرین", callback_data='شیرین')],
        [InlineKeyboardButton("😎 تلخ", callback_data='تلخ')],
        [InlineKeyboardButton("❄️ خنک", callback_data='خنک')],
        [InlineKeyboardButton("🔥 گرم", callback_data='گرم')],
    ]
    await query.edit_message_text("✨ حس کلی عطرت چی باشه؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return TONE

# انتخاب حس
async def select_tone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id]['tone'] = query.data
    keyboard = [
        [InlineKeyboardButton("🏢 رسمی", callback_data='رسمی')],
        [InlineKeyboardButton("❤️ قرار عاشقانه", callback_data='عاشقانه')],
        [InlineKeyboardButton("🎉 مهمونی", callback_data='مهمونی')],
        [InlineKeyboardButton("🧘 روزمره", callback_data='روزمره')],
    ]
    await query.edit_message_text("📍 عطر رو بیشتر کجا استفاده می‌کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return SITUATION

# انتخاب موقعیت
async def select_situation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id]['situation'] = query.data
    keyboard = [
        [InlineKeyboardButton("👩 زنانه", callback_data='زنانه')],
        [InlineKeyboardButton("👨 مردانه", callback_data='مردانه')],
        [InlineKeyboardButton("⚧ یونی‌سکس", callback_data='یونی‌سکس')],
    ]
    await query.edit_message_text("🚻 ترجیح جنسیتی عطرت چیه؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return GENDER

# انتخاب جنسیت و نمایش نتیجه
async def select_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id]['gender'] = query.data

    profile = user_data[query.from_user.id]
    perfumes = get_perfumes(profile)

    if perfumes:
        response = f"🎯 رایحه پیشنهادی: {profile['style']} + {profile['tone']} + {profile['gender']}

"
        for i, p in enumerate(perfumes, 1):
            response += f"{i}. [{p['title']}]({p['link']})
💰 {p['price']}

"
    else:
        response = "متأسفم! عطری مطابق سلیقه‌ات پیدا نکردم."

    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مکالمه لغو شد.")
    return ConversationHandler.END

# وب‌اسکرپینگ از pmlm.ir
def get_perfumes(profile):
    try:
        url = "https://pmlm.ir/product-category/ادوپرفیوم/"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".product-small")

        perfumes = []
        for item in items:
            title = item.select_one(".woocommerce-loop-product__title")
            price = item.select_one(".price")
            link_tag = item.select_one("a.woocommerce-LoopProduct-link")

            if title and price and link_tag:
                title_text = title.text.strip()
                price_text = price.text.strip()
                link = link_tag['href']

                # فیلتر ساده با توجه به سلیقه
                if (profile['style'] in title_text or profile['tone'] in title_text):
                    perfumes.append({
                        'title': title_text,
                        'price': price_text,
                        'link': link,
                    })
        return perfumes[:5]
    except Exception as e:
        print("خطا در اسکرپینگ:", e)
        return []

# راه‌اندازی
def main():
    import asyncio
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STYLE: [CallbackQueryHandler(select_style)],
            TONE: [CallbackQueryHandler(select_tone)],
            SITUATION: [CallbackQueryHandler(select_situation)],
            GENDER: [CallbackQueryHandler(select_gender)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    asyncio.run(app.run_polling())

if __name__ == "__main__":
    main()
