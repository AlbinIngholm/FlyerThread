from playwright.async_api import async_playwright
import logging
from config import STORES

logger = logging.getLogger(__name__)

async def get_flyer_images(store_url):
    """Scrape flyer images from the given store URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(store_url, timeout=60000) # Added timeout
        except Exception as e:
            logger.error(f"Failed to navigate to {store_url}: {e}")
            await browser.close()
            return []

        try:
            await page.wait_for_selector("img[src*='.webp']", timeout=15000) # Increased timeout slightly
        except Exception:
            logger.warning(f"No .webp images found on {store_url} after waiting.") # Changed print to logger.warning
            await browser.close()
            return []

        images = await page.eval_on_selector_all(
            "img[src*='.webp']", "elements => elements.map(e => e.src)"
        )

        await browser.close()
        logger.info(f"Successfully scraped {len(images)} images from {store_url}") # Added info log
        return images