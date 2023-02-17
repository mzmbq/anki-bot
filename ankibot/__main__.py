import logging
import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, PicklePersistence, CallbackQueryHandler

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

    context.user_data["word"] = word
    context.user_data["page"] = 0
    
    await show5(update, context)
    
    
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    dictionary = context.bot_data["cambridge_dict"]

    data = query.data
    if data == "more":
        context.user_data["page"] += 1
        await show5(update, context)
    else:
        await query.message.reply_text(f"Adding definition {dictionary.get_definitions(context.user_data['word'])[int(data)].definition} to your deck")

    
    
async def show5(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    word = context.user_data["word"]
    page = context.user_data["page"]
    dictionary = context.bot_data["cambridge_dict"]
    
    start = page * 5
    end = page * 5 + 5
    
    definitions = dictionary.get_definitions(word)[start:end]
    if len(definitions) == 0:
        # TODO: finish
        return
    definitions_msg = "\n***\n".join([f"{start + i}. {d}" for i,
                                     d in enumerate(definitions)])
    
    keyboard_numbers = [InlineKeyboardButton(i, callback_data=str(i)) for i in range(start, end)]
    keyboard = [keyboard_numbers, [InlineKeyboardButton("Show more", callback_data="more")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # TODO: refactor
    if update.message:
        await update.message.reply_text(definitions_msg, reply_markup=reply_markup)
    else:        
        await update.callback_query.from_user.send_message(definitions_msg, reply_markup=reply_markup)


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

    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == "__main__":
    main()
