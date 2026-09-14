import os
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

# Configuration
ADMIN_IDS = [932575497]
CHANNEL_USERNAME = "@DramaClipsBingeShorts"
BOT_USERNAME = "DramaBingeCatalog_bot"

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 1. Lightweight health check server for Render & UptimeRobot
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, format, *args):
        pass  # Keeps logs clean

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# 2. Start the health-check server in the background thread
threading.Thread(target=run_health_server, daemon=True).start()

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

    "toxic_love": {
        "title": "⚠️ Toxic Love",
        "series": [
            {
                "name": "My Finace Cheated, So I chose His Billionaire Dad",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBBGqnsIP3JYiWVKP9edi1BjtRGblrAAJAHwACfzFBUXOLv5z45H6LPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBBWqnsINURsBM6B0wtN1zJgTCSY5QAAJBHwACfzFBUe8c9n-oTsQGPQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBBmqnsIM5xhJV8LGkZQq2nEoeE2jAAAJCHwACfzFBURrAlv9oCUXwPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBB2qnsIP9iILJqw6j6xbDfWGMavADAAJDHwACfzFBUQ7vNfBbyODJPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBCGqnsIPmQ3JkM1UUAb54UxStHHNRAAJEHwACfzFBUUzG8ml3QdUBPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBCWqnsINDSYy_t4oBalnlMt4ejCgXAAJFHwACfzFBUbmPVSl2wTj-PQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBCmqnsINlCEIBkZzLEIwYIo3HkTOuAAJGHwACfzFBUUApMOWF2w83PQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAIBC2qnsINQh-QW70W72A8QS2Uf2hZpAAJHHwACfzFBUaG8JRv0RoCvPQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAIBDGqnsIOYSmGPW7PZTWd4kvpkVIw8AAJIHwACfzFBUQnNhW4pg-6OPQQ"}
                ]
            }
        ]
    },

    "secret_identity": {
        "title": "🎭 Secret Identity",
        "series": [
            {
                "name": "The Hidden Dragon Rider Returns For Justice",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBFmqnsrqxwoOQXgbL1raamRfOryelAAJKHwACfzFBUW5zVXeytoAkPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBF2qnsroFAAEfdGauZ8RW7ApfOkBgeQACSx8AAn8xQVEXTYe6qlntUz0E"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBGGqnsrqLcy8MhYLTwYU3JjsETFjbAAJMHwACfzFBURfE319nSZP2PQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBGWqnsroUQLPMo0mrw-hltasNinFpAAJNHwACfzFBURX2xcpUR9GtPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBGmqnsrr1KLrl0pGod_sqy00PvCP8AAJOHwACfzFBUXIZ7Kv5av-MPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBG2qnsrqYm0i4behf_m-Jeb5yek7oAAJPHwACfzFBURiGzuK0KrNyPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBHGqnsroxTXyEgd1rwXsMjJnDdgdyAAJQHwACfzFBUcQ1iH19VURjPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAIBHWqnsrraNcy0lh1y_odeubXYBC0TAAJRHwACfzFBURqgAAGlctsFiT0E"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAIBHmqnsrrK0PVXTvcBa56xB99YLfXBAAJSHwACfzFBUX8RdiM--3igPQQ"},
                    {"name": "Episode 10", "file_id": "BQACAgQAAxkBAAIBH2qnsrpFvpZtdmbqVIxX4MtCAtwVAAJTHwACfzFBUfm0myto23HVPQQ"}
                ]
            }
        ]
    },

    "strong_female": {
        "title": "⚡ Strong Female",
        "series": [
            {
                "name": "Wait, You Called The Lady Boss A Side Piece?",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBKmqntOOROuPBbpPmq6QJNpcwitD9AAJaHwACfzFBUZVqU98mHAbrPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBK2qntOONlLJGZYMX3XZf9gn_E_oNAAJbHwACfzFBUU2DAAGlir0O7D0E"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBLGqntOPlLZXItssNvwMkAfRk6tlXAAJcHwACfzFBUV2e0WjncbElPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBLWqntONY0OInUTzC0kVUWGKOsQ2HAAJdHwACfzFBUefV8v0RP4gpPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBLmqntON8MIUKl6QzSpFdm8ytQ6NTAAJeHwACfzFBUX4MEaGAYm3VPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBL2qntOOp0CKH4FJTQ0ioUJEiY8PhAAJfHwACfzFBUXKtoMlEQ62LPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBMGqntOO99wZlZrWFn4frQ3fptaXiAAJgHwACfzFBUWVD0vwHFVFHPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAIBMWqntOOQssugy1kdYg_Sc9I_VPWhAAJhHwACfzFBUWKEFfNi54u-PQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAIBMmqntOM93a3EtmVJ19Dh1C63CTahAAJiHwACfzFBUW9NzHWntiXqPQQ"},
                    {"name": "Episode 10", "file_id": "BQACAgQAAxkBAAIBM2qntON8Q4nUevJDCzkAAbo8t7nefgACYx8AAn8xQVFGOzZiEw_XfT0E"}
                ]
            },
            {
                "name": "Owned By My Husband's Sister",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBqGqn1AWkzZ3eGcCQs-mwCtUUmzaZAALJHwACfzFBUSDTTOmgL75mPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBqWqn1AX71Q0XSZDm79qlS1lC-CIAA8ofAAJ_MUFRjcxTwrTM-TM9BA"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBqmqn1AXGCT79rIG4dqBqOs5RUk9_AALLHwACfzFBUd9kJVa9u5snPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBq2qn1AXmFkIalBH_JvgbMHmjxqMxAALMHwACfzFBUYLGRjLw6984PQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBsGqn1Gk1qMYEnvP1AAENlw7nRYzWVwACzR8AAn8xQVFAJTb7l9Hikz0E"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBsWqn1GnkuVuZ1ncAAah4ezRXgehh2gACzh8AAn8xQVHWbsQ3tCDgFD0E"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBsmqn1Gk4oi0Jx1FUOr2cGoW67oE0AALPHwACfzFBUT254xrPaeu8PQQ"}
                ]
            }
        ]
    },

    "vampire": {
        "title": "🧛 Vampire",
        "series": [
            {
                "name": "Too Late To Love His Substitute Slave",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBcmqn0GwBlkQEYxXRYbvGwVZNcCW2AAKgHwACfzFBUeWK3G0ILicZPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBc2qn0GydCF3fiPO3xQqmXCGvXnAUAAKhHwACfzFBUW7jvB73e9CyPQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBdGqn0Gx0hkA3Xdc6ki77WQfO-IUSAAKiHwACfzFBUeoeAAEStDVOqD0E"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBdWqn0GxoBMhqZjfib5EI1SEm5fnkAAKjHwACfzFBUZTUtbf_5hOcPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBdmqn0GwDlcIXKNkgSWZIgvpgB4tLAAKkHwACfzFBUbPeCvLWaM2CPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBd2qn0GzRCHIbues9O-Rv9ZWRvmUPAAKlHwACfzFBUQx7GXbAWYrrPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBeGqn0Gy5Ag-B0ME9Q4YcqQ-dnXsvAAKmHwACfzFBUWP5YGR9mD6kPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAIBeWqn0GzmiQdLMY-rWjayLEj5-N1FAAKnHwACfzFBUb7IBpIXCqv-PQQ"}
                ]
            },
            {
                "name": "The Mermaid Queen Rises From Betrayal",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BAACAgQAAxkBAAIBhGqn0ZsyNPJryCMCwAnZkA06LSvPAAKyHwACfzFBUbp2V6bJ4MV7PQQ"},
                    {"name": "Episode 2", "file_id": "BAACAgQAAxkBAAIBhmqn0alTdIK9pFfd46dkwHnXliFaAAKzHwACfzFBUVdmaza5Wg2ePQQ"},
                    {"name": "Episode 3", "file_id": "BAACAgQAAxkBAAIBhmqn0alTdIK9pFfd46dkwHnXliFaAAKzHwACfzFBUVdmaza5Wg2ePQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBimqn0b1t6PdfjVmXjusmd0CECpq5AAK2HwACfzFBUe1J02P5rcxrPQQ"},
                    {"name": "Episode 5", "file_id": "BAACAgQAAxkBAAIBjGqn0cg4hYEhUbcF8cVOF9eUEeCeAAK3HwACfzFBUbdGt4idyrRUPQQ"},
                    {"name": "Episode 6", "file_id": "BAACAgQAAxkBAAIBjmqn0dCMIiRY-HTQgQ6SuiWo2PNOAAK5HwACfzFBUWwOuYAhWH4dPQQ"}
                ]
            }
        ]
    },

    "cheating": {
        "title": "💔 Cheating",
        "series": [
            {
                "name": "The Captian Secret Wife Was The Real Ace",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBkGqn0tl_bAF3ry6bhyIWoVV5Cq4UAAK8HwACfzFBUYC6bAABVP4ecD0E"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBkWqn0tnPPXfXTKK9Vn33NPc0eg6oAAK9HwACfzFBUf43JNXgIzABPQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBkmqn0tkh-U7_bnK9A2o_J08GRNCKAAK-HwACfzFBUT2ZJYMQA8VUPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBk2qn0tlCpDATX3f-eDsAAWvhEmbzCQACvx8AAn8xQVH5--PGP5Wi5z0E"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBlGqn0tmzlPHnbu6xy6poO25-7bvTAALAHwACfzFBUeYWd_S_9HEwPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBlWqn0tk0P-RlysRYSb8aRtB7QUK9AALBHwACfzFBUT2IUWOZ_QkRPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBlmqn0tkUx7522iAj_PJiEW7lzewCAALCHwACfzFBUQjrJLMMkFlCPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAIBl2qn0tk2iUPZDEQ8gyVTdpPrEDP6AALDHwACfzFBUY33fx8vhrN6PQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAIBomqn01EeiEvurgP-jO3aK4AsTT4NAALFHwACfzFBUaXCzNIF-2AbPQQ"},
                    {"name": "Episode 10", "file_id": "BQACAgQAAxkBAAIBo2qn01Gw4WwtvEwnjXN6A4jL2696AALGHwACfzFBUVCJ-rp-H9m6PQQ"},
                    {"name": "Episode 11", "file_id": "BQACAgQAAxkBAAIBpGqn01HMsxct3WkJI7lx0Zc9GAQ_AALHHwACfzFBUZNd4bWNSHr7PQQ"}
                ]
            }
        ]
    },

    "werewolf": {
        "title": "🐺 Werewolf",
        "series": [
            {
                "name": "The Hidden Dragon Rider Returns For Justice",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIByGqn1WHU9532EAGmzrYOGXCkR77VAALaHwACfzFBUdLx72_w5kXFPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBtmqn1QQB58lDIY6xqd7zrbu_4X7MAALRHwACfzFBUUnh6ZZG1srAPQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBt2qn1QSRvU5cOb-RglLVcODPlLKhAALSHwACfzFBUeb1NnP2PvThPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBuGqn1QStCvr9eJrBu2jNn5C_WNdAAALTHwACfzFBUZXyN-zX_AfOPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIBuWqn1QSKeAvWRIN7zOcYiG_GM9wrAALUHwACfzFBUeOw5S2QjOMnPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAIBumqn1QR9XwABuE5AP9Gc9j9OdcSN4wAC1R8AAn8xQVG8z3w-GM_XJT0E"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAIBu2qn1QSVQo9NXavQYdoFeBIqXZ5JAALWHwACfzFBUTUKrlMKByJqPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAIBvGqn1QTZHBi6MkR0rqQ5mkCS7LlyAALXHwACfzFBUTZfzARGZL4yPQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAIBvWqn1QQzBVCT--NmxKW_ZAXU-5Q4AALYHwACfzFBUXB4RLRulh8zPQQ"},
                    {"name": "Episode 10", "file_id": "BQACAgQAAxkBAAIBvmqn1QQKp43IkhnX9Fzzr7lU_UY4AALZHwACfzFBUXcg3Rn2Erp8PQQ"}
                ]
            },
            {
                "name": "Fall In Love With Claws And Fangs",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAIBymqn1jPHIQ5ZM-scdD8X3uYvcGc0AALbHwACfzFBUXxOaQg1Kva9PQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAIBy2qn1jMgF6v2e_G_08v56zYmVL3PAALcHwACfzFBUSDw6pfyBkD_PQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAIBzGqn1jNjeRxPHfdxHwfjSB1YqZw_AALdHwACfzFBUbkHQRx63bS1PQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAIBzWqn1jPxHl-wLBfNFnsl2LX7fFBBAALeHwACfzFBUajdq2G3F1TDPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAIB0mqn1msMIBLEzeJv_eYQ8giE_pmOAALfHwACfzFBUfAPUOnXjXujPQQ"}
                ]
            }
        ]
    },

    "regret": {
        "title": "🥀 Regret",
        "series": [
            {
                "name": "I Walked Away You Wasted Away",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAICSWqoG4ThJsRrF_4zj-uYnV2-Wyg6AAKKIAACfzFBUXekrGfYzySCPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAICSmqoG4TLkykipcCiLoMJeVgAAXmFRgACiyAAAn8xQVGjxFgej-m8Wj0E"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAICS2qoG4QJ1sTv5IuN0p9zNnY6r4oOAAKMIAACfzFBUScf0AezDJt4PQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAICTGqoG4QinJrX91_Ae0JKzNofOGxzAAKNIAACfzFBUfecCq1zhWE4PQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAICTWqoG4TcSXNyPDLhMamazQhLHn8gAAKOIAACfzFBUQx9cUY7-1iZPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAICTmqoG4SCXC2pcnyzKSVEcX7u1uhlAAKPIAACfzFBUZX8GHrsbQkuPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAICT2qoG4TrZO9TfqZboHcUwPUN6BUYAAKQIAACfzFBUWWD4DwQJB_kPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAICUGqoG4TAkLxwkSIvW1Iv8Qnxd128AAKRIAACfzFBUXNfwRwXszcIPQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAIBomqn01EeiEvurgP-jO3aK4AsTT4NAALFHwACfzFBUaXCzNIF-2AbPQQ"},
                    {"name": "Episode 10", "file_id": "BQACAgQAAxkBAAICUmqoG4SWtYhLCEmw_2oCHjptno40AAKUIAACfzFBUVwKN9dgyshQPQQ"},
                    {"name": "Episode 11", "file_id": "BQACAgQAAxkBAAICXWqoG4b6hvPgSwhrv9me27ISHwABugAClSAAAn8xQVGtFYZqXYy6Lj0E"}
                ]
            }
        ]
    },

    "princess": {
        "title": "👑 Princess",
        "series": [
            {
                "name": "I Dumped Zeus:Th God King",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAICX2qoHQ2EvTzN1ailR21mdwMWSwauAAKYIAACfzFBUYtsvWBvpY41PQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAICX2qoHQ2EvTzN1ailR21mdwMWSwauAAKYIAACfzFBUYtsvWBvpY41PQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAICYWqoHQ3CZKyxgbeZ-i1tbIzfvaX4AAKaIAACfzFBUaoTzQQSi2aSPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAICYmqoHQ0JUwvYjpu2nsQvprT00D1WAAKbIAACfzFBUXT8ZPyi0WqbPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAICZ2qoHaPcC6E7BzJfhJ-wjem1VjdxAAKdIAACfzFBUX3UGZ_GgLXuPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAICZ2qoHaPcC6E7BzJfhJ-wjem1VjdxAAKdIAACfzFBUX3UGZ_GgLXuPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAICaWqoHaPV13iHGuOKCSbz2t-_wuq8AAKgIAACfzFBUSgaMV9h5rq6PQQ"}
                ]
            }
        ]
    },

    "family_kids": {
        "title": "👨‍👩‍👧 Family & Kids",
        "series": [
            {
                "name": "His Baby Girl Is A MAgical Beasts, Whisperer",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAICbWqoHpg8tnBpECY9wf-7DcpLPZOKAAKkIAACfzFBUdSxqwvGtrCiPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAICbmqoHphAoD_MbuHMKA6-dkG4w9_qAAKlIAACfzFBUY2Jg--Qp7wGPQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAICb2qoHpgEu7gJJm0GsgUgFuTRGFacAAKmIAACfzFBUUJLbx5lsIDYPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAICcGqoHpjTAwI-aAH9Nk-Fyw9ptwnuAAKnIAACfzFBUfNzIIszNgX3PQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAICcWqoHphDWt19yRo5fMyer2YAARKJ1QACqCAAAn8xQVHCPEohihRWVD0E"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAICcmqoHpgDRBZri0z8Vys6N-Cfl4k4AAKpIAACfzFBURAlIGRQraxpPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAICc2qoHpg7HA9V-AIY1gbHW_bHk96yAAKqIAACfzFBUXKeD9MqcmWlPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAICdGqoHpgohdz3-TvbAlx6MBJpw53LAAKrIAACfzFBUZcbz7b7L9yVPQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAICdWqoHphb2w5HzoCX7-8LClQPdE0pAAKtIAACfzFBUcVNO9uxyjKBPQQ"},
                    {"name": "Episode 10", "file_id": "BQACAgQAAxkBAAICdmqoHpiZtZ2nspp0ZFn_RAVrTXGiAAKuIAACfzFBUZ0eUPwB7HXBPQQ"},
                    {"name": "Episode 11", "file_id": "BQACAgQAAxkBAAICgWqoHp-z7VuuFsM1039HqZVcehMPAAKvIAACfzFBUXccHoU1hGOUPQQ"},
                    {"name": "Episode 12", "file_id": "BQACAgQAAxkBAAICgmqoHp_hMGl0CS5MrIRZIDR-MOEEAAKwIAACfzFBUXXiJPJRYyN9PQQ"},
                    {"name": "Episode 13", "file_id": "BQACAgQAAxkBAAICg2qoHp_j_mCiGNHWWr-J9qkR2MSnAAKxIAACfzFBUYKTEczLzggVPQQ"}
                ]
            }
        ]
    },

    "heir": {
        "title": "💎 Heir",
        "series": [
            {
                "name": "From Ragas To The Hidden Heirs Bride",
                "episodes": [
                    {"name": "Episode 1", "file_id": "BQACAgQAAxkBAAICh2qoKHm1Nukz1ymQlzx5R8gyt_oUAALAIAACfzFBUTdQD7MrHaTfPQQ"},
                    {"name": "Episode 2", "file_id": "BQACAgQAAxkBAAICiGqoKHmKnDqAkrqxBrQoFSyWEXJBAALBIAACfzFBUTAfPiP_4nc1PQQ"},
                    {"name": "Episode 3", "file_id": "BQACAgQAAxkBAAICiWqoKHmOJ-IcdplL7vGeSivjvvdJAALCIAACfzFBUUb5-BT_JDqjPQQ"},
                    {"name": "Episode 4", "file_id": "BQACAgQAAxkBAAICimqoKHldtOO97blZgt69MIdJdYztAALDIAACfzFBUdu-zvsx0_OGPQQ"},
                    {"name": "Episode 5", "file_id": "BQACAgQAAxkBAAICi2qoKHm_ifPjGVF4YyiyjS6r_LifAALFIAACfzFBUamC-8-_p4rZPQQ"},
                    {"name": "Episode 6", "file_id": "BQACAgQAAxkBAAICjGqoKHkYlji77SQhWC3CFyrpScv2AALGIAACfzFBUbqKvL2cQ8AUPQQ"},
                    {"name": "Episode 7", "file_id": "BQACAgQAAxkBAAICjWqoKHl_U99inkhCeHHbPcCvWfmBAALHIAACfzFBUV5kcIXk0u6EPQQ"},
                    {"name": "Episode 8", "file_id": "BQACAgQAAxkBAAICjmqoKHki76bUmit0m2Ag-xwvYT8XAALIIAACfzFBUbiGe5rpEY5JPQQ"},
                    {"name": "Episode 9", "file_id": "BQACAgQAAxkBAAICl2qoKQ_rjJh-k9JiKaOCn1_ZeGL9AALKIAACfzFBUcomgHHqTMDSPQQ"}
                ]
            }
        ]
    },

}

CATEGORIES = [
    ("🔥 Forbidden Love", "forbidden_love"),
    ("⚡ Flash Marriage", "flash_marriage"),
    ("🏛️ Campus", "campus_cinderella"),
    ("⚡ Strong Female", "strong_female"),
    ("🐺 Werewolf", "werewolf"),
    ("🧛 Vampire", "vampire"),
    ("💔 Cheating", "cheating"),
    ("👑 Princess", "princess"),
    ("👨‍👩‍👧 Family & Kids", "family_kids"),
    ("⚠️ Toxic Love", "toxic_love"),
    ("🥀 Regret", "regret"),
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
    ("🎭 Secret Identity", "secret_identity"),
    ("💎 Heir", "heir"),
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
    total_series = sum(len(cat_data.get("series", [])) for cat_data in DATABASE.values())
    
    keyboard = [
        [InlineKeyboardButton(f"🔥 Total Available Series: {total_series}", callback_data="total_counter")]
    ]
    
    row = []
    for title, cat_key in CATEGORIES:
        cat_data = DATABASE.get(cat_key)
        series_count = len(cat_data["series"]) if cat_data and "series" in cat_data else 0
        
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
            raw_name = show['name']
            short_name = raw_name if len(raw_name) <= 28 else raw_name[:25] + "..."
            btn_text = f"📺 {short_name} ({ep_count} Eps)"
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

    if data == "total_counter":
        await query.answer("🔥 This shows the total active series in our database!", show_alert=False)
        return

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
        raw_name = show_info['name']
        short_name = raw_name if len(raw_name) <= 35 else raw_name[:32] + "..."
        ep_count = len(show_info["episodes"])
        
        await query.message.edit_text(
            f"📺 *{short_name}* \n({ep_count} Episodes available)\n\nChoose an episode to watch:",
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
            raw_name = show['name']
            short_name = raw_name if len(raw_name) <= 28 else raw_name[:25] + "..."
            btn_text = f"📺 {short_name} ({ep_count} Eps)"
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
        
        show_info = DATABASE[cat_key]["series"][s_idx]
        ep_info = show_info["episodes"][e_idx]
        file_id = ep_info["file_id"]
        
        app_link = "https://bit.ly/4xlLGEC"
        
        caption_text = (
            f"🎬 *{show_info['name']}* - *{ep_info['name']}*\n\n"
            f"▶️ Now Playing! Enjoy your show.\n\n"
            f"⏳ *Come back later for more episodes and daily updates!*\n\n"
            f"📱 Watch more original short dramas & full episodes on our app:\n"
            f"🔗 {app_link}"
        )
        
        try:
            await context.bot.send_video(
                chat_id=query.from_user.id,
                video=file_id,
                caption=caption_text,
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

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
        
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def main():
    token = "8974449532:AAFCZcCzAoVbegRGZdOF_zk1nu6baUnko_M"
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("postchannel", post_to_channel))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video_upload))
    
    print("Bot is up and listening...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    main()