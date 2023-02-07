import logging
import os
from dotenv import load_dotenv

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ankibot.dictionary.cambridge import CambridgeDictionary
from ankibot.dictionary.word_definition import WordDefinition


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if CambridgeDictionary().contains(update.message.text):
        text = "Found:\n"
        for i, d in enumerate(CambridgeDictionary().get_definitions(update.message.text)):
            text += str(i+1) + ". " + d.definition+ "\n"
            for e in d.examples:
                text += "- " + e + "\n"
            text += "---\n"
    else:
        text = "Not found"
    await update.message.reply_text(text)


def main() -> None:
    """Start the bot."""

    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, lookup))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
