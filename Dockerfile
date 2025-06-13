# Use official Python 3.11 as the base image
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip fonts-liberation libnss3 libatk-bridge2.0-0 libxss1 libasound2 libgtk-3-0 libxshmfence1 libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to cache dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and download browsers
RUN pip install --no-cache-dir playwright \
    && playwright install --with-deps

# Copy the rest of the project
COPY . .

# Start the bot
CMD ["python", "bot.py"]