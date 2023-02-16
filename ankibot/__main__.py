import logging
import os
from dotenv import load_dotenv

from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, PicklePersistence

from ankibot.dictionary.cambridge import CambridgeDictionary
from ankibot.dictionary.word_definition import WordDefinition


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_text = f"Hello, {update.effective_user.mention_html()}!\nUse /help command"
    await update.message.reply_html(start_text)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = "Commands:\n" \
        "/help - ...\n" \
        "/login - to connect to your ankiweb account\n"

    await update.message.reply_text(help_text)


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_data = context.bot_data
    word = update.message.text

    if "cambridge_dict" not in bot_data:
        bot_data["cambridge_dict"] = CambridgeDictionary()
    dictionary = bot_data["cambridge_dict"]

    if not dictionary.contains(word):
        await update.message.reply_text(f"{word} not found.")
        return

    definitions = dictionary.get_definitions(word)
    definitions_msg = "\n***\n".join([f"{i}. {d}" for i,
                                     d in enumerate(definitions)])

    await update.message.reply_text(definitions_msg)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    filepath = "persistent_data"
    persistence = PicklePersistence(filepath=filepath)

    application = Application.builder().token(
        token).persistence(persistence).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, lookup))

    application.run_polling()


if __name__ == "__main__":
    main()
