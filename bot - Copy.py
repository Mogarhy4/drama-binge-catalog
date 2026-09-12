import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Hardcoded channel username based on your setup
CHANNEL_USERNAME = "@DramaClipsBingeShorts"

CATEGORIES = [
    ("🔥 Forbidden Love", "forbidden_love"),
    ("⚡ Strong Female Lead", "strong_female_lead"),
    ("💍 Contract Marriage", "contract_marriage"),
    ("❤️ Love After Marriage", "love_after_marriage"),
    ("🏃‍♂️ Chasing Love", "chasing_love"),
    ("⚠️ Toxic Love", "toxic_love"),
    ("💔 Getting Back at Ex", "getting_back_at_ex"),
    ("🏡 House Wives", "house_wives"),
    ("💼 Female CEO", "female_ceo"),
    ("🎬 Action & Thriller", "action_thriller"),
    ("❤️ Romance & Drama", "romance_drama"),
    ("😂 Comedy & Sitcom", "comedy_sitcom"),
    ("🌌 Sci-Fi & Fantasy", "sci_fi_fantasy"),
    ("🕵️ Crime & Mystery", "crime_mystery"),
    ("😱 Horror & Suspense", "horror_suspense"),
    ("🏛️ Historical Epic", "historical_epic"),
    ("🎨 Animation & Anime", "animation_anime"),
    ("📹 Documentary", "documentary"),
    ("👨‍👩‍👧 Family & Kids", "family_kids"),
    ("📺 Reality TV", "reality_tv"),
    ("🗺️ Adventure", "adventure"),
    ("🦸‍♂️ Superhero", "superhero"),
    ("🏥 Medical Drama", "medical_drama"),
    ("⚖️ Legal & Political", "legal_political"),
    ("⚽ Sports", "sports"),
    ("📱 Short Clips", "short_clips"),
    ("⭐ Exclusive Series", "exclusive_series"),
    ("🔥 Trending Now", "trending_now"),
    ("🎲 Random Pick", "random_pick")
]

def build_catalog_keyboard():
    keyboard = []
    row = []
    for title, callback_data in CATEGORIES:
        row.append(InlineKeyboardButton(title, callback_data=callback_data))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = build_catalog_keyboard()
    welcome_text = (
        "🎬 *Welcome to Drama Clips & Binge Shorts*\n\n"
        "Choose a category below to explore episodes:"
    )
    await update.message.reply_text(text=welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = build_catalog_keyboard()
    channel_text = (
        "🎬 *Drama Catalog Master Menu*\n\n"
        "Tap any category below to instantly browse and stream our exclusive series and short clips:"
    )
    
    try:
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=channel_text, reply_markup=reply_markup, parse_mode="Markdown")
        await update.message.reply_text(f"Successfully published the catalog menu directly to {CHANNEL_USERNAME}!")
    except Exception as e:
        await update.message.reply_text(f"Failed to post. Make sure the bot is an admin in {CHANNEL_USERNAME}.\nError: {e}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_category = query.data
    await query.message.reply_text(f"You selected: *{selected_category}*.", parse_mode="Markdown")

def main():
    token = "8974449532:AAGs7pmg_MdT__U9Tlz_-QceT5OGHt6Mm_4"
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("postchannel", post_to_channel))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is up and listening...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()