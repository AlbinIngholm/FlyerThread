import aiohttp
import discord
from discord.ext import commands, tasks
from scraper import get_flyer_images
from config import (
    DISCORD_TOKEN, CHANNEL_ID, TIMEZONE, POSTING_DAY, POSTING_HOUR,
    POSTING_MINUTE, STORES, MESSAGES, LANGUAGE, EXCLUDED_FLYER_PAGES
)
import asyncio
from datetime import datetime
import zoneinfo
import io
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Validate DISCORD_TOKEN
if not DISCORD_TOKEN or not isinstance(DISCORD_TOKEN, str) or len(DISCORD_TOKEN) < 50:
    logger.error("DISCORD_TOKEN is missing or invalid in .env file")
    exit(1)
logger.info(f"Loaded DISCORD_TOKEN: {DISCORD_TOKEN[:10]}...")

# Validate CHANNEL_ID
if not isinstance(CHANNEL_ID, int) or CHANNEL_ID <= 0:
    logger.error("CHANNEL_ID must be a valid integer in .env file")
    exit(1)
logger.info(f"Loaded CHANNEL_ID: {CHANNEL_ID}")

# Validate TIMEZONE
try:
    tz = zoneinfo.ZoneInfo(TIMEZONE)
except zoneinfo.ZoneInfoNotFoundError:
    logger.error(f"Invalid TIMEZONE: {TIMEZONE}. Using 'UTC' as fallback.")
    tz = zoneinfo.ZoneInfo("UTC")

# Validate LANGUAGE
if LANGUAGE not in MESSAGES:
    logger.warning(f"Language '{LANGUAGE}' not supported. Using 'en' as fallback.")
    LANGUAGE = "en"

# Validate POSTING_DAY
if not (0 <= POSTING_DAY <= 6):
    logger.error(f"POSTING_DAY must be between 0 and 6. Using 0 (Monday) as fallback.")
    POSTING_DAY = 0

# Validate POSTING_HOUR and POSTING_MINUTE
if not (0 <= POSTING_HOUR <= 23):
    logger.error(f"POSTING_HOUR must be between 0 and 23. Using 8 as fallback.")
    POSTING_HOUR = 8
if not (0 <= POSTING_MINUTE <= 59):
    logger.error(f"POSTING_MINUTE must be between 0 and 59. Using 15 as fallback.")
    POSTING_MINUTE = 15

# Validate EXCLUDED_FLYER_PAGES
if not (0 <= EXCLUDED_FLYER_PAGES):
    logger.error(f"EXCLUDED_FLYER_PAGES must be a non-negative integer. Using 0 as fallback.")
    EXCLUDED_FLYER_PAGES = 0

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for member list visibility and thread management

# Initialize bot
bot = commands.Bot(command_prefix="$", intents=intents)

last_run_date = None

@bot.event
async def on_ready():
    """Log when the bot is ready and connected to Discord."""
    logger.info(f"✅ FlyerThread is online as {bot.user}! Intents: {bot.intents}")
    logger.info(f"Connected to guilds: {[guild.name for guild in bot.guilds]}")
    weekly_flyer_task.start()

@tasks.loop(minutes=15)
async def weekly_flyer_task():
    """Check every 15 minutes to post flyers on the configured day and time."""
    global last_run_date
    now = datetime.now(tz)

    # Check if it's the configured day and time (within a 15-minute window)
    if (now.weekday() == POSTING_DAY and now.time().hour == POSTING_HOUR and
            POSTING_MINUTE <= now.time().minute < POSTING_MINUTE + 15):
        if last_run_date != now.date():
            logger.info(f"Starting flyer posting job at {POSTING_HOUR:02d}:{POSTING_MINUTE:02d} {TIMEZONE}")
            await post_flyers()
            last_run_date = now.date()
    elif last_run_date is not None and now.date() > last_run_date:
        last_run_date = None  # Reset if it's a new day

@weekly_flyer_task.before_loop
async def before_weekly_flyer_task():
    """Ensure the bot is ready before starting the task loop."""
    await bot.wait_until_ready()

@bot.command()
async def postnow(ctx):
    """Manually trigger flyer posting with the $postnow command."""
    if ctx.channel.id != CHANNEL_ID:
        logger.warning(f"$postnow command used in incorrect channel: {ctx.channel.id}")
        await ctx.send("This command can only be used in the configured channel.")
        return
    await ctx.send("Manually starting flyer posting...")
    await post_flyers()

async def post_flyers():
    """Fetch and post flyer images to Discord threads."""
    logger.info("Starting flyer posting")
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        logger.error(f"Channel with ID {CHANNEL_ID} not found")
        return

    # Fetch active and archived threads
    try:
        active_threads = channel.threads
        archived_threads = [thread async for thread in channel.archived_threads(limit=None)]
        all_threads = active_threads + archived_threads
    except discord.errors.Forbidden:
        logger.error(f"Bot lacks permission to access threads in channel {CHANNEL_ID}")
        return
    except Exception as e:
        logger.error(f"Error fetching threads: {e}")
        return

    # Get current week number
    now = datetime.now(tz)
    week_number = now.isocalendar().week

    # Archive old store threads that don't match the current week
    for thread in all_threads:
        for store_name in STORES:
            expected_thread_name = f"{store_name} - Week {week_number}"
            if thread.name.startswith(store_name) and thread.name != expected_thread_name:
                try:
                    await thread.edit(archived=True)
                    logger.info(f"Archived thread: {thread.name}")
                except discord.errors.Forbidden:
                    logger.error(f"Bot lacks permission to archive thread {thread.name}")
                except Exception as e:
                    logger.error(f"Failed to archive thread {thread.name}: {e}")

    thread_mentions = []
    async with aiohttp.ClientSession() as session:
        for store_name, store_url in STORES.items():
            logger.info(f"Processing store: {store_name}")
            # Check for existing thread
            thread = None
            expected_thread_name = f"{store_name} - Week {week_number}"
            for existing_thread in active_threads:
                if existing_thread.name == expected_thread_name and not existing_thread.archived:
                    thread = existing_thread
                    logger.info(f"Reusing existing thread: {expected_thread_name}")
                    break

            # Create a new thread if none exists
            if thread is None:
                try:
                    thread = await channel.create_thread(
                        name=expected_thread_name,
                        type=discord.ChannelType.public_thread,
                        auto_archive_duration=10080  # 7 days
                    )
                    logger.info(f"Created new public thread: {expected_thread_name}")
                except discord.errors.Forbidden:
                    logger.error(f"Bot lacks permission to create thread for {expected_thread_name}")
                    continue
                except Exception as e:
                    logger.error(f"Could not create thread for {expected_thread_name}: {e}")
                    continue

            thread_mentions.append(f"<#{thread.id}>")
            try:
                flyers = await get_flyer_images(store_url)
                logger.info(f"Found {len(flyers)} flyers for {store_name}")
            except Exception as e:
                logger.error(f"Error scraping flyers for {store_name}: {e}")
                continue

            # Exclude a configurable number of pages if EXCLUDED_FLYER_PAGES is greater than 0
            if EXCLUDED_FLYER_PAGES > 0:
                original_count = len(flyers)
                flyers = flyers[:-EXCLUDED_FLYER_PAGES]
                logger.info(f"Excluded the last {EXCLUDED_FLYER_PAGES} flyers, keeping {len(flyers)} (originally {original_count}) for {store_name}")

            if not flyers:
                try:
                    await thread.send(MESSAGES[LANGUAGE]["no_flyers"])
                except discord.errors.Forbidden:
                    logger.error(f"Bot lacks permission to send messages in thread {expected_thread_name}")
                except Exception as e:
                    logger.error(f"Error sending no-flyers message to {expected_thread_name}: {e}")
                continue

            # Process images for the store
            files = []
            for flyer_url in flyers:
                try:
                    async with session.get(flyer_url) as resp:
                        if resp.status != 200:
                            logger.error(f"Failed to download {flyer_url} with status {resp.status}")
                            continue
                        image_data = await resp.read()

                    # Convert image to appropriate format
                    image = Image.open(io.BytesIO(image_data)).convert("RGBA")
                    buffer = io.BytesIO()
                    if flyer_url.lower().endswith(('.jpg', '.jpeg')):
                        image.save(buffer, format="JPEG", quality=95)
                        filename = flyer_url.split("/")[-1].rsplit(".", 1)[0] + ".jpg"
                    else:
                        image.save(buffer, format="PNG")
                        filename = flyer_url.split("/")[-1].rsplit(".", 1)[0] + ".png"
                    buffer.seek(0)
                    files.append(discord.File(fp=buffer, filename=filename))

                except Exception as e:
                    logger.error(f"Error processing image {flyer_url}: {e}")

            # Send up to 10 files at once to respect Discord's limit
            for i in range(0, len(files), 10):
                try:
                    await thread.send(files=files[i:i+10])
                    logger.info(f"Sent {len(files[i:i+10])} flyer images in thread {expected_thread_name}")
                except discord.errors.Forbidden:
                    logger.error(f"Bot lacks permission to send images in thread {expected_thread_name}")
                except Exception as e:
                    logger.error(f"Error sending images to {expected_thread_name}: {e}")

    # Send summary message with week number
    if thread_mentions:
        summary_message = MESSAGES[LANGUAGE]["summary"].format(
            week_number=week_number,
            threads="\n".join(thread_mentions)
        )
        try:
            await channel.send(summary_message)
            logger.info("Finished posting flyers and sent summary message")
        except discord.errors.Forbidden:
            logger.error("Bot lacks permission to send messages in channel")
        except Exception as e:
            logger.error(f"Error sending summary message: {e}")

try:
    bot.run(DISCORD_TOKEN)
except discord.errors.LoginFailure as e:
    logger.error(f"Failed to login: {e}. Check DISCORD_TOKEN and intents in Discord Developer Portal")
    exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    exit(1)
