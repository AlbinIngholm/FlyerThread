# config.py
# Configuration file for bot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord bot token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Discord channel ID where the bot will post
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) if os.getenv("CHANNEL_ID") else None

# Timezone for scheduling (e.g., "Europe/Oslo", "America/New_York")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Oslo")

# Posting schedule: day (0=Monday, 6=Sunday), hour (0-23), minute (0-59)
POSTING_DAY = int(os.getenv("POSTING_DAY", 0))
POSTING_HOUR = int(os.getenv("POSTING_HOUR", 8))
POSTING_MINUTE = int(os.getenv("POSTING_MINUTE", 15))

# Language for messages (e.g., "en" for English, "no" for Norwegian)
LANGUAGE = os.getenv("LANGUAGE", "en")

# Number of flyer pages to exclude from the end of the list (e.g., 0 for none, 4 to exclude the last 4). To reduce ads at the end
EXCLUDED_FLYER_PAGES = int(os.getenv("EXCLUDED_FLYER_PAGES", 0))

# Store URLs for scraping flyers (customize for your region)
STORES = {
    "StoreName": "https://url.com/flyer"
}

# Message translations
MESSAGES = {
    "en": {
        "summary": "This week (week {week_number}), check out the latest flyers:\n\n{threads}",
        "no_flyers": "No flyer images found."
    },
    "no": {
        "summary": "Denne uken (uke {week_number}) er det massive mengder nam nam. Sjekk tilbudsavisene:\n\n{threads}",
        "no_flyers": "Ingen tilbudsaviser funnet."
    }
}
