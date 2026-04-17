import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
COMPLETIONS_API_KEY = os.getenv("COMPLETIONS_API_KEY")
COMPLETIONS_BASE_URL = os.getenv(
    "COMPLETIONS_BASE_URL", "https://completions.me/api/v1"
)
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-sonnet-4.5")

AGENTS_DIR = Path(__file__).parent / "agents"

SYSTEM_PROMPT = """You are an AI assistant from "The Agency" - a collection of specialized AI agents.
Available agents include: Frontend Developer, Backend Architect, AI Engineer, DevOps Automator,
Marketing Content Creator, Sales Outreach Specialist, SEO Specialist, Product Manager, and many more.

When asked to act as a specific agent, adopt their persona and expertise. Provide specialized,
professional responses based on the agent's specialty area.

Always be helpful, knowledgeable, and action-oriented in your responses. Use Markdown formatting
where appropriate for code blocks, headers, lists, etc."""


def get_available_models():
    return [
        "claude-opus-4.6",
        "claude-sonnet-4.6",
        "claude-sonnet-4.5",
        "claude-haiku-4.5",
        "gpt-5.2",
        "gpt-4.1",
        "gemini-3.1-pro-preview",
        "gemini-2.5-pro",
    ]


def call_ai(prompt, model=None):
    url = f"{COMPLETIONS_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {COMPLETIONS_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4096,
        "temperature": 0.7,
    }

    logger.info(f"Calling AI with model: {model or DEFAULT_MODEL}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        logger.info(f"API Response Status: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"API Error: {response.text}")
            return f"API Error ({response.status_code}): {response.text[:200]}"

        data = response.json()
        logger.info(f"API Response received, processing...")

        choices = data.get("choices", [])
        if choices and len(choices) > 0:
            content = choices[0].get("message", {}).get("content", "")
            if content:
                logger.info(f"Response length: {len(content)} chars")
                return content

        return "I received your message but couldn't generate a response. Please try again."

    except requests.exceptions.Timeout:
        logger.error("API Timeout error")
        return "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Unexpected error: {str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🎭 *Welcome to The Agency Bot!*

I provide access to specialized AI agents for various tasks:

*Engineering:* Frontend, Backend, Mobile, AI/ML, DevOps
*Marketing:* Content, SEO, Social Media, Growth Hacking
*Sales:* Outreach, Discovery, Proposals, Pipeline
*Product:* Sprint Planning, Research, Feedback Analysis
*Design:* UI/UX, Branding, Visual Storytelling
*Support:* Customer Service, Analytics, Infrastructure

*Commands:*
/start - Show this welcome message
/agents - List all available agents
/help - Show help information
/setmodel - Set AI model (e.g., /setmodel claude-sonnet-4.5)
/models - List available models

*Powered by completions.me (Unlimited Free AI)*
"""
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 *How to use The Agency Bot:*

1. *Direct Questions:* Ask me anything and I'll provide a specialized response.

2. *Agent Selection:* Use /agents to see all available specialists.

3. *Custom Model:* Set your preferred AI model with /setmodel.

*Examples:*
- "Help me build a React component"
- "Create a marketing strategy for my SaaS"
- "Review my sales email"
- "Plan a sprint for my team"
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agents_list = """
🎭 *Available Agency Agents:*

*💻 Engineering:*
• Frontend Developer - React/Vue/Angular
• Backend Architect - API/DB/Scalability
• AI Engineer - ML/AI Integration
• DevOps Automator - CI/CD/Cloud

*📢 Marketing:*
• Content Creator - Copy/Strategy
• Growth Hacker - User Acquisition
• SEO Specialist - Search Optimization
• Social Media Strategist - Cross-platform

*💼 Sales:*
• Outbound Strategist - Prospecting
• Discovery Coach - Qualifying
• Proposal Strategist - RFPs

*🎯 Product:*
• Sprint Prioritizer - Agile Planning
• Trend Researcher - Market Intel

*🎨 Design:*
• UI Designer - Visual Design
• UX Researcher - User Testing

*💬 Support:*
• Support Responder - Customer Service
• Analytics Reporter - KPIs/Dashboards

*Just describe what you need and I'll match you with the right specialist!*
"""
    await update.message.reply_text(agents_list, parse_mode="Markdown")


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    models = get_available_models()
    models_text = "*Available Free Models:*\n\n"
    models_text += "\n".join([f"• `{m}`" for m in models])
    models_text += "\n\n*Default: claude-sonnet-4.5*"
    await update.message.reply_text(models_text, parse_mode="Markdown")


async def setmodel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        model = context.args[0]
        context.user_data["model"] = model
        await update.message.reply_text(
            f"✅ Model set to: `{model}`", parse_mode="Markdown"
        )
    else:
        current = context.user_data.get("model", DEFAULT_MODEL)
        await update.message.reply_text(
            f"Current model: `{current}`\n\nUsage: /setmodel <model_id>\n\nUse /models to see available options.",
            parse_mode="Markdown",
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📷 *Images not supported yet*\n\n"
        "Please send your questions as text messages. "
        "I can help with code, marketing, sales, and more!",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        chat_id = update.message.chat_id

        logger.info(f"Message from {chat_id}: {user_message[:100]}")

        await update.message.reply_text("🎭 Consulting with the Agency specialists...")

        model = context.user_data.get("model", DEFAULT_MODEL)
        logger.info(f"Using model: {model}")

        response = call_ai(user_message, model=model)

        logger.info(f"Response received, sending to user...")

        max_length = 4096
        if len(response) > max_length:
            chunks = [
                response[i : i + max_length]
                for i in range(0, len(response), max_length)
            ]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await update.message.reply_text(chunk, parse_mode="Markdown")
                else:
                    await update.message.reply_text(
                        f"_...continued ({i + 1}/{len(chunks)})_"
                    )
                    await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred. Please try again.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again or use /help for assistance."
        )


def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    if not COMPLETIONS_API_KEY or COMPLETIONS_API_KEY == "YOUR_COMPLETIONS_KEY":
        logger.error("COMPLETIONS_API_KEY not set!")
        print("❌ ERROR: COMPLETIONS_API_KEY not set!")
        print("📝 Please:")
        print("   1. Go to https://completions.me")
        print("   2. Sign up (free, no credit card)")
        print("   3. Get your API key")
        print("   4. Add it to the .env file as COMPLETIONS_API_KEY=your_key")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("agents", agents_command))
    app.add_handler(CommandHandler("models", models_command))
    app.add_handler(CommandHandler("setmodel", setmodel_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("🤖 Agency Bot starting...")
    print("=" * 50)
    print("🎭 THE AGENCY TELEGRAM BOT")
    print("=" * 50)
    print("Powered by completions.me (Unlimited Free AI)")
    print("Bot is running! Press Ctrl+C to stop.")
    print("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
