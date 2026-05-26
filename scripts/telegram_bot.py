"""Telegram bot for the proposal agent. Run alongside the FastAPI server."""
import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN", "")
API_BASE = "http://localhost:8000"
DEFAULT_DEVELOPER = "artem_koshevoi"

# per-chat state (in-memory, resets on bot restart)
active_threads: dict[int, str] = {}    # chat_id → thread_id
active_developer: dict[int, str] = {}  # chat_id → developer_id

HELP_TEXT = """Send me a job description to generate a proposal.

Commands:
/dev <developer_id> — set developer (default: artem_koshevoi)
/new — clear current proposal, start fresh
/help — show this message

While reviewing a proposal:
  reply with feedback → revise
  reply "approve" → finish"""


def _split(text: str, limit: int = 4000) -> list[str]:
    """Split text into chunks within Telegram's 4096 char limit."""
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        parts.append(text[:limit])
        text = text[limit:]
    return parts


async def _send(update: Update, text: str) -> None:
    for part in _split(text):
        await update.message.reply_text(part)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello! I'm the proposal agent.\n\n{HELP_TEXT}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    active_threads.pop(update.effective_chat.id, None)
    await update.message.reply_text("Ready for a new job. Send the description.")


async def cmd_dev(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if not context.args:
        current = active_developer.get(chat_id, DEFAULT_DEVELOPER)
        await update.message.reply_text(
            f"Current developer: {current}\nUsage: /dev <developer_id>"
        )
        return
    dev_id = context.args[0]
    active_developer[chat_id] = dev_id
    await update.message.reply_text(f"Developer set to: {dev_id}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id in active_threads:
        # revision / approval mode
        await update.message.reply_text("Processing...")
        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(f"{API_BASE}/revise-proposal", json={
                "thread_id": active_threads[chat_id],
                "feedback": text,
            })
            resp.raise_for_status()
            result = resp.json()

        if text.lower() == "approve":
            active_threads.pop(chat_id, None)
            await update.message.reply_text("Approved. Final proposal:")
            await _send(update, result["proposal"])
        else:
            await update.message.reply_text(f"Revised (v{result['revision_count']}):")
            await _send(update, result["proposal"])
            await update.message.reply_text("Reply with feedback or 'approve'.")

    else:
        # new job mode
        developer_id = active_developer.get(chat_id, DEFAULT_DEVELOPER)
        developer_name = developer_id.replace("_", " ").title()
        await update.message.reply_text(f"Generating proposal for {developer_name}...")

        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(f"{API_BASE}/process-job", json={
                "job_text": text,
                "developer_id": developer_id,
            })
            resp.raise_for_status()
            result = resp.json()

        verdict = result["verdict"]

        if verdict == "SKIP":
            await update.message.reply_text(
                f"Skipped: {result['verdict_reason']}\n\nSend a new job description."
            )
            return

        active_threads[chat_id] = result["thread_id"]
        await update.message.reply_text(f"Verdict: {verdict} — {result['verdict_reason']}\n\nProposal:")
        await _send(update, result["proposal"])
        await update.message.reply_text("Reply with feedback or 'approve'.")


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Error: {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(f"Something went wrong: {context.error}")


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN not set in .env")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("dev", cmd_dev))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(handle_error)

    print(f"Bot started. Polling... (API: {API_BASE})")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
