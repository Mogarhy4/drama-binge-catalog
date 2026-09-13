# Add your Telegram numeric user ID here
ADMIN_IDS = [932575497]

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
                "name": "Hero Husband's Apocalypse Harem",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BAACAgQAAxkBAAMiaqXIO0oDWKj3xS1ZofseV37F25UAAkgeAAJx7ihRE4jy3T8Z6909BA"},
                    {"name": "Episode 2", "file_id": "BAACAgQAAxkBAAMsaqXKNAr6csp1C43OI64fy30NP5gAAkoeAAJx7ihREz6FBDXCYaU9BA"},
                    {"name": "Episode 3", "file_id": "BAACAgQAAxkBAAMuaqXKWexL7VveH-4zzLgy5KiGmtUAAkseAAJx7ihRefpl2CgvkUQ9BA"},
                    {"name": "Episode 4", "file_id": "BAACAgQAAxkBAAMwaqXKkHcOBZNGcKpi2B67jdWaj6wAAkweAAJx7ihR_NGjoBi0g0Y9BA"},
                    {"name": "Episode 5", "file_id": "BAACAgQAAxkBAAMyaqXKuRqCy1OzF-DIpUfMLCSOlDoAAvUgAAJx7jBRNl0xpSX8XLQ9BA"},
                    {"name": "Episode 6", "file_id": "BAACAgQAAxkBAAM0aqXK3L0jdGngklPnpaIq-IerCUwAAvYgAAJx7jBRYQHen2xEnQs9BA"},
                    {"name": "Episode 7", "file_id": "BAACAgQAAxkBAAM2aqXLCtYRNZ5hKu5oBmqV-7vPWxcAAvcgAAJx7jBR5t580ZWkbXM9BA"},
                    {"name": "Episode 8", "file_id": "BAACAgQAAxkBAAM4aqXLKufSQNg8wbFmw_LVQ1MpFj8AAvggAAJx7jBRQdT--Oayq-M9BA"},
                    {"name": "Episode 9", "file_id": "BAACAgQAAxkBAAM6aqXLSETumJjVn4INiTOVZLKWBR8AAvkgAAJx7jBRZ1qxRCKbOu89BA"}
                ]
            }
        ]
    },

    "flash_marriage": {
        "title": "⚡ Flash Marriage",
        "series": [
            {
                "name": "Top Gear Guy Finds His Mr's Right",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BAACAgQAAxkBAANNaqbxn4cH_2EckwABc2yeGBv-nXKGAAJ9IwACfzE5UWYPInSD9_tfPQQ"},
                    {"name": "Episode 2", "file_id": "BAACAgQAAxkBAANPaqbxuUi7dg0g3zbUKrJS7YgYfCoAAn4jAAJ_MTlRPUw0R1YCoyU9BA"},
                    {"name": "Episode 3", "file_id": "BAACAgQAAxkBAANRaqbx0u1RbFVEUjDgePY0Ad95IZYAAn8jAAJ_MTlRJyZ8suJwrLQ9BA"},
                    {"name": "Episode 4", "file_id": "BAACAgQAAxkBAANTaqbx8Pgk9XT7C5wCNToZG81supgAAoAjAAJ_MTlRXFFtfEo99qE9BA"},
                    {"name": "Episode 5", "file_id": "BAACAgQAAxkBAANVaqbyCO0hHuAtt1GNozsIn8aZirQAAoEjAAJ_MTlRuENBLA5zPB89BA"},
                    {"name": "Episode 6", "file_id": "BAACAgQAAxkBAANXaqbyJlz5LERs2iHrvkcgAAFJ0t9MAAKCIwACfzE5UWShY-MNSTeZPQQ"},
                    {"name": "Episode 7", "file_id": "BAACAgQAAxkBAANZaqbyOt8uzayBT-7NqxGxely94swAAoMjAAJ_MTlRiYkm6vD2HwQ9BA"},
                    {"name": "Episode 8", "file_id": "BAACAgQAAxkBAANbaqbyV9rVHQhvH7o90k4tOLhTligAAoQjAAJ_MTlRebThkfH0W9c9BA"},
                    {"name": "Episode 9", "file_id": "BAACAgQAAxkBAANdaqbycETKUizPsigp1QqygDhbbvgAAoUjAAJ_MTlRfrt4bA1SZ5c9BA"},
                    {"name": "Episode 10", "file_id": "BAACAgQAAxkBAANfaqbykLC5tMKgmmo4GtQznMNYc9cAAoYjAAJ_MTlRzc216qqRO8Q9BA"}
                ]
            },
            {
                "name": "The Substitute Brid For The First Vampire",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BAACAgQAAxkBAAN1aqb4grTBsMswbWGdLiEsKYy8kr0AAqwjAAJ_MTlR7FDVDcMaIB49BA"},
                    {"name": "Episode 2", "file_id": "BAACAgQAAxkBAAN2aqb4gpofp3wChBruRJ_gmvLUSikAAq0jAAJ_MTlRM17o3JN9NOA9BA"},
                    {"name": "Episode 3", "file_id": "BAACAgQAAxkBAAN3aqb4giM4UPGLBCCF7M7j_uBkJiYAAq4jAAJ_MTlRIYB9FadFD0o9BA"},
                    {"name": "Episode 4", "file_id": "BAACAgQAAxkBAAN4aqb4gny8QxrYIYzbleHMFQaK0DYAAq8jAAJ_MTlRgBjDAfK2ER49BA"},
                    {"name": "Episode 5", "file_id": "BAACAgQAAxkBAAN5aqb4guOaf1bpvC0HId0nXipIoewAArAjAAJ_MTlRhUlf1SzSvo49BA"},
                    {"name": "Episode 6", "file_id": "BAACAgQAAxkBAAN6aqb4goErsNQjkamJDIH4_HYHv4kAArEjAAJ_MTlRFqJGHJZSgEQ9BA"},
                    {"name": "Episode 7", "file_id": "BAACAgQAAxkBAAN7aqb4gqKQctesKPiY1dWllthVXegAArIjAAJ_MTlRR5dd-9Dim8I9BA"},
                    {"name": "Episode 8", "file_id": "BAACAgQAAxkBAAN8aqb4gvkY-hFDMoPmfjekdSNTy_EAArMjAAJ_MTlRRXqSctmgaxE9BA"},
                    {"name": "Episode 9", "file_id": "BAACAgQAAxkBAAN9aqb4gknuUO82FOk4ctaGE7fHZh8AArQjAAJ_MTlR4HsBnAmIrNA9BA"},
                    {"name": "Episode 10", "file_id": "BAACAgQAAxkBAAN-aqb4gizEgnLwC3kyIYbME3v4lbwAArUjAAJ_MTlRSbojaqzWYX49BA"}
                ]
            }
        ]
    },

    "campus_cinderella": {
        "title": "🏛️ Campus",
        "series": [
            {
                "name": "My Finace's Brother Owns Me Every Night",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BAACAgQAAxkBAANhaqb3efrL7tY5NfwC8SxTKAIVL1UAAqAjAAJ_MTlRt9WoOZbCteM9BA"},
                    {"name": "Episode 2", "file_id": "BAACAgQAAxkBAANiaqb3ef_lYT7JahE06to0w8CXhs8AAqEjAAJ_MTlRdj2KkHqxic89BA"},
                    {"name": "Episode 3", "file_id": "BAACAgQAAxkBAANlaqb3vNs4AjFwRrs_uYbYWG_Lk9sAAqIjAAJ_MTlRotaM9-OrPrs9BA"},
                    {"name": "Episode 4", "file_id": "BAACAgQAAxkBAANmaqb3vMd3Xvoj3bc0oQABnyCE9tuZAAKjIwACfzE5UWqoyihuYHT3PQQ"},
                    {"name": "Episode 5", "file_id": "BAACAgQAAxkBAANnaqb3vMKO0oBT-DpuG8_d_nwtQ3cAAqQjAAJ_MTlRh77C4JKCBek9BA"},
                    {"name": "Episode 6", "file_id": "BAACAgQAAxkBAANoaqb3vNaWlNbV2NwEJu1OLsIg_IQAAqUjAAJ_MTlRrRye3AMxluQ9BA"},
                    {"name": "Episode 7", "file_id": "BAACAgQAAxkBAANpaqb3vAAB0YzhIt23-lkn4jT0f3nlAAKmIwACfzE5UdkEa-OLo7_XPQQ"},
                    {"name": "Episode 8", "file_id": "BAACAgQAAxkBAANqaqb3vHMgP6WFOUC3x32WZTWZYf0AAqcjAAJ_MTlReIy4y0etlsU9BA"},
                    {"name": "Episode 9", "file_id": "BAACAgQAAxkBAANraqb3vDLV7cqBmZYp2_IzW3Cf27MAAqgjAAJ_MTlRahMBsogvwt89BA"},
                    {"name": "Episode 10", "file_id": "BAACAgQAAxkBAANsaqb3vMxeo-l64oRWpab6dwSPODkAAqkjAAJ_MTlRmSJLMSGXgmg9BA"}
                ]
            }
        ]
    },
}

CATEGORIES = [
    ("🔥 Forbidden Love", "forbidden_love"),
    ("⚡ Flash Marriage", "flash_marriage"),
    ("🏛️ Campus", "campus"),
    ("⚡ Strong Female", "strong_female"),
    ("💍 Contr. Marriage", "contract_marriage"),
    ("❤️ After Marriage", "love_after_marriage"),
    ("🏃‍♂️ Chasing Love", "chasing_love"),
    ("⚠️ Toxic Love", "toxic_love"),
    ("💔 Getting Back 💔", "getting_back_💔"),
    ("🏡 House Wives", "house_wives"),
    ("💼 Female CEO", "female_ceo"),
    ("🎬 Action & Thriller", "action_thriller"),
    ("❤️ Romance", "romance"),
    ("😂 Comedy & Sitcom", "comedy_sitcom"),
    ("🌌 Sci-Fi & Fantasy", "sci_fi_fantasy"),
    ("🕵️ Crime & Mystery", "crime_mystery"),
    ("😱 Horror", "horror"),
    ("🏛️ Historical Epic", "historical_epic"),
    ("🎨 Anime", "anime"),
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
        # Dynamically calculate series count from DATABASE to display on the button
        cat_data = DATABASE.get(cat_key)
        series_count = len(cat_data["series"]) if cat_data and "series" in cat_data else 0
        
        # Append count tag to button title (e.g., "[2 Series]")
        display_title = f"{title} [{series_count}]"
        
        url = f"https://t.me/{BOT_USERNAME}?start={cat_key}"
        row.append(InlineKeyboardButton(display_title, url=url))
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

        keyboard = []
        for s_idx, show in enumerate(category_data["series"]):
            ep_count = len(show["episodes"])
            btn_text = f"📺 {show['name']} ({ep_count} Episodes)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"series_{cat_key}_{s_idx}")])
        
        keyboard.append([InlineKeyboardButton("🏠 Main Categories", callback_data="main_menu")])
        
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
    # Check if the user sending the video is an admin
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🎬 Welcome! Use our channel links to browse and watch series.")
        return

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

    if data == "main_menu":
        reply_markup = build_catalog_keyboard()
        await query.message.edit_text(
            "🎬 *Welcome to Drama Clips & Binge Shorts*\n\nChoose a category below to explore episodes:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    if data.startswith("series_"):
        remaining, s_idx_str = data.rsplit("_", 1)
        _, cat_key = remaining.split("_", 1)
        s_idx = int(s_idx_str)
        
        show_info = DATABASE[cat_key]["series"][s_idx]
        
        keyboard = []
        for e_idx, ep in enumerate(show_info["episodes"]):
            keyboard.append([InlineKeyboardButton(f"▶️ {ep['name']}", callback_data=f"ep_{cat_key}_{s_idx}_{e_idx}")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back to Series", callback_data=f"backcat_{cat_key}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"📺 *{show_info['name']}*\n\nChoose an episode to watch:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    if data.startswith("backcat_"):
        _, cat_key = data.split("_", 1)
        category_data = DATABASE.get(cat_key)
        
        keyboard = []
        for s_idx, show in enumerate(category_data["series"]):
            ep_count = len(show["episodes"])
            btn_text = f"📺 {show['name']} ({ep_count} Episodes)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"series_{cat_key}_{s_idx}")])
        
        keyboard.append([InlineKeyboardButton("🏠 Main Categories", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"📂 *{category_data['title']} Catalog*\n\nSelect a series below to view available episodes:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

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

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Dummy web server to satisfy Render's Web Service port requirement
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# Start the web server in a background thread
threading.Thread(target=run_health_server, daemon=True).start()

if __name__ == "__main__":
    main()