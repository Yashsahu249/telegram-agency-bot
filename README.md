# The Agency Telegram Bot 🤖

A Telegram bot powered by [The Agency](https://github.com/msitarzewski/agency-agents) AI agents using OpenRouter API.

## Setup

1. **Activate virtual environment:**
   ```bash
   cd telegram-agency-bot
   source venv/bin/activate
   ```

2. **Configure environment:**
   Edit `.env` file with your tokens:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   OPENROUTER_API_KEY=your_openrouter_key
   ```

3. **Sync agents from The Agency:**
   ```bash
   python sync_agents.py
   ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## Commands

- `/start` - Welcome message
- `/help` - Help information
- `/agents` - List available agents
- `/models` - List available AI models
- `/setmodel <model>` - Set preferred model

## Structure

```
telegram-agency-bot/
├── bot.py           # Main bot code
├── sync_agents.py   # Sync agents from agency-agents repo
├── agents/          # Agent index (183 agents)
├── .env             # API tokens
└── requirements.txt # Dependencies
```

## Bot Features

- 🤖 183 specialized AI agents from The Agency
- 💬 Conversational interface
- 📚 Agent selection and specialization
- ⚡ Powered by OpenRouter API
