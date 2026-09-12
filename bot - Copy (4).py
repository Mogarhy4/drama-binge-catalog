import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

CHANNEL_USERNAME = "@DramaClipsBingeShorts"
BOT_USERNAME = "DramaBingeCatalog_bot"

# 3-Tier Database: Category -> Series (with multiple episodes)
DATABASE = {
    "forbidden_love": {
        "title": "🔥 Forbidden Love",
        "series": [
            {
                "name": "Secret Affair",
                "episodes": [
                    {"name": "Episode 1", "file_id": "PASTE_YOUR_FILE_ID_FOR_EP_1"},
                    {"name": "Episode 2", "file_id": "PASTE_YOUR_FILE_ID_FOR_EP_2"},
                ]
            },
            {
                "name": "Hidden Hearts",
                "episodes": [
                    {"name": "Episode 1", "file_id": "PASTE_YOUR_FILE_ID_FOR_HIDDEN_HEARTS_EP1"},
                ]
            }
        ]
    },
    "strong_female_lead": {
        "title": "⚡ Strong Female Lead",
        "series": [
            {
                "name": "Queen's Revenge",
                "episodes": [
                    {"name": "Episode 1", "file_id": "PASTE_YOUR_FILE_ID_HERE"},
                ]
            }
        ]
    }
}

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
    for title, cat_key in CATEGORIES:
        url = f"https://t.me/{BOT_USERNAME}?start={cat_key}"
        row.append(InlineKeyboardButton(title, url=url))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        cat_key = context.args[0]
        category_data = DATABASE.get(cat_key)
        
        if not category_data or not category_data["series"]:
            await update.message.reply_text("🎬 Series for this category are coming soon! Stay tuned.")
            return

        # Level 1 -> Show Series list with episode counts
        keyboard = []
        for s_idx, show in enumerate(category_data["series"]):
            ep_count = len(show["episodes"])
            btn_text = f"📺 {show['name']} ({ep_count} Episodes)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"series_{cat_key}_{s_idx}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"📂 *{category_data['title']} Catalog*\n\nSelect a series below to view available episodes:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    reply_markup = build_catalog_keyboard()
    await update.message.reply_text(
        "🎬 *Welcome to Drama Clips & Binge Shorts*\n\nChoose a category below to explore episodes:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_video_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if video:
        file_id = video.file_id
        await update.message.reply_text(
            f"✅ *Video Received & Registered!*\n\n"
            f"Here is your permanent `file_id`:\n`{file_id}`\n\n"
            f"Copy this string and paste it into your `DATABASE` episode list.",
            parse_mode="Markdown"
        )
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Level 2 -> User clicked a Series, show its Episodes
    if data.startswith("series_"):
        # Safely split from the right to handle category names with underscores
        remaining, s_idx_str = data.rsplit("_", 1)
        _, cat_key = remaining.split("_", 1)
        s_idx = int(s_idx_str)
        
        show_info = DATABASE[cat_key]["series"][s_idx]
        
        keyboard = []
        for e_idx, ep in enumerate(show_info["episodes"]):
            keyboard.append([InlineKeyboardButton(f"▶️ {ep['name']}", callback_data=f"ep_{cat_key}_{s_idx}_{e_idx}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"📺 *{show_info['name']}*\n\nChoose an episode to watch:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # Level 3 -> User clicked an Episode, send the video file
    if data.startswith("ep_"):
        remaining, e_idx_str = data.rsplit("_", 1)
        remaining2, s_idx_str = remaining.rsplit("_", 1)
        _, cat_key = remaining2.split("_", 1)
        
        s_idx = int(s_idx_str)
        e_idx = int(e_idx_str)
        
        ep_info = DATABASE[cat_key]["series"][s_idx]["episodes"][e_idx]
        file_id = ep_info["file_id"]
        
        try:
            await context.bot.send_video(
                chat_id=query.from_user.id,
                video=file_id,
                caption=f"▶️ Now Playing: *{ep_info['name']}*\nEnjoy your show!",
                parse_mode="Markdown"
            )
        except Exception as e:
            await query.message.reply_text(f"Error loading video. Make sure you replaced the placeholder with a valid file_id.\nDetails: {e}")

    # Level 2 -> User clicked a Series, show its Episodes
    if data.startswith("series_"):
        _, cat_key, s_idx_str = data.split("_")
        s_idx = int(s_idx_str)
        
        show_info = DATABASE[cat_key]["series"][s_idx]
        
        keyboard = []
        for e_idx, ep in enumerate(show_info["episodes"]):
            keyboard.append([InlineKeyboardButton(f"▶️ {ep['name']}", callback_data=f"ep_{cat_key}_{s_idx}_{e_idx}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"📺 *{show_info['name']}*\n\nChoose an episode to watch:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # Level 3 -> User clicked an Episode, send the video file
    if data.startswith("ep_"):
        _, cat_key, s_idx_str, e_idx_str = data.split("_")
        s_idx = int(s_idx_str)
        e_idx = int(e_idx_str)
        
        ep_info = DATABASE[cat_key]["series"][s_idx]["episodes"][e_idx]
        file_id = ep_info["file_id"]
        
        try:
            await context.bot.send_video(
                chat_id=query.from_user.id,
                video=file_id,
                caption=f"▶️ Now Playing: *{ep_info['name']}*\nEnjoy your show!",
                parse_mode="Markdown"
            )
        except Exception as e:
            await query.message.reply_text(f"Error loading video. Make sure you replaced the placeholder with a valid file_id.\nDetails: {e}")

async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = build_catalog_keyboard()
    channel_text = (
        "🎬 *Drama Catalog Master Menu*\n\n"
        "Tap any category below to instantly open our bot and browse series privately:"
    )
    try:
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=channel_text, reply_markup=reply_markup, parse_mode="Markdown")
        await update.message.reply_text(f"Successfully published the catalog to {CHANNEL_USERNAME}!")
    except Exception as e:
        await update.message.reply_text(f"Failed to post. Error: {e}")

def main():
    token = "8974449532:AAGs7pmg_MdT__U9Tlz_-QceT5OGHt6Mm_4"
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("postchannel", post_to_channel))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video_upload))
    
    print("Bot is up and listening...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()