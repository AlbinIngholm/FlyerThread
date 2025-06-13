# FlyerThread Discord Bot

**FlyerThread** is a Discord bot designed to scrape weekly store flyers and post them into dedicated threads in a Discord channel. This helps users easily keep track of the latest deals and promotions from their favorite stores.

---

## Features

- **Automated Scraping**: Scrapes flyer images from configured store URLs.  
- **Scheduled Posting**: Posts flyers automatically on a defined day and time each week.  
- **Dedicated Threads**: Creates or reuses Discord threads for each store to keep flyers organized.  
- **Multi-language Support**: Currently supports English and Norwegian for bot messages.  
- **Manual Trigger**: Allows manual triggering of flyer posting via a Discord command.  
- **Robust Error Handling**: Includes logging and checks for common issues like missing tokens or invalid configurations.  

---

## ⚠️ Important Note about the Scraper

This bot uses a basic web scraper built with [Playwright](https://playwright.dev/). It works best with websites that do not implement aggressive anti-scraping techniques. It has been tested on sites like **mattilbud.no**.

Limitations include:

- Aggressive bot detection  
- Complex CAPTCHAs  
- JavaScript-heavy content loading  
- Strict `robots.txt` rules  

If a store URL doesn't work, it may be due to such protections.

---

## 🔒 Legal and Ethical Considerations

Using this bot responsibly is essential. This tool is intended for **educational and personal use only**.

**Before scraping any website:**

- **Check `robots.txt`**: Respect the site's access rules.  
- **Review Terms of Service**: Some sites prohibit scraping entirely.  
- **Rate Limit Requests**: Avoid overloading servers. This bot posts once weekly by default.  
- **Limit Data Use**: Use scraped content only to display flyers inside Discord.  
- **Contact Site Owners**: For regular or large-scale scraping, consider asking permission.  
- **Understand Fair Use**: Know how copyright and content usage laws apply in your region.  

> **Disclaimer**: The developers of this bot are not liable for misuse or legal issues. Use responsibly and at your own risk.

---

## 🛠️ Setup

### 1. Prerequisites

- Python 3.8+  
- pip  
- Node.js (required for Playwright)  
- Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)

### 2. Installation

```bash
git clone https://github.com/AlbinIngholm/FlyerThread.git
cd FlyerThread
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### 3. Configuration

Create a `.env` file in the project root using `.env.example` as a reference:

```env
DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
CHANNEL_ID="YOUR_DISCORD_CHANNEL_ID_HERE"
TIMEZONE="Europe/Oslo"
POSTING_DAY=0
POSTING_HOUR=8
POSTING_MINUTE=15
LANGUAGE="en"
EXCLUDED_FLYER_PAGES=0
```

**Descriptions:**

- `DISCORD_TOKEN`: Get this from your bot's page in the Developer Portal.  
- `CHANNEL_ID`: Right-click a channel in Discord → Copy ID (enable Developer Mode if needed).  
- `TIMEZONE`: e.g., `Europe/Oslo` or `America/New_York`.  
- `POSTING_DAY`: 0 = Monday, 6 = Sunday.  
- `POSTING_HOUR` / `POSTING_MINUTE`: 24-hour format.  
- `LANGUAGE`: `en` (English) or `no` (Norwegian).  
- `EXCLUDED_FLYER_PAGES`: Useful if flyers end with irrelevant pages.

### 4. Discord Bot Permissions

Make sure the bot has the following permissions:

- Send Messages  
- Create Public Threads  
- Manage Threads  
- Read Message History  

### 5. Running the Bot

```bash
python bot.py
```

---

## ✨ Usage

- The bot posts flyers automatically as scheduled.  
- Manually trigger with:

```
$postnow
```

---

## 📁 Project Structure

```
FlyerThread/
├── bot.py              # Main bot logic and scheduling
├── scraper.py          # Web scraping with Playwright
├── config.py           # Configuration and environment loading
├── .env.example        # Example environment file
├── requirements.txt    # Python dependencies
├── .gitignore          # Git exclusions
└── LICENSE             # MIT License
```

---

## 🤝 Contributing

Open issues or submit PRs for bugs, features, or improvements. Contributions are welcome!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
