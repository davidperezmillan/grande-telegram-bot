# Grande Bot - Simple Telegram Bot

A simple Telegram bot that starts and runs using Telethon.

## Features

- Starts a Telegram bot
- Runs until disconnected

## Project Structure

```
grande_bot/
├── main.py                     # Main bot file
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables example
├── data/                      # Data directory
├── logs/                      # Logs directory
└── downloads/                 # Downloads directory
```

## Installation and Setup

### 1. Clone and configure

```bash
cd grande_bot
cp .env.example .env
```

### 2. Configure environment variables

Edit `.env`:

```env
# Telegram API credentials (from https://my.telegram.org)
API_ID=your_api_id
API_HASH=your_api_hash

# Bot token (from @BotFather)
BOT_TOKEN=your_bot_token
```

### 3. Build and run

```bash
docker-compose up -d
```

### 4. View logs

```bash
docker-compose logs -f grande-bot
```