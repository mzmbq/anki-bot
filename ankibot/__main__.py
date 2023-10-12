# pylint: disable=missing-function-docstring
# pylint: disable=fixme

import logging
import os
import tomllib

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import (Application, CommandHandler, ContextTypes, MessageHandler,
    filters, PicklePersistence, CallbackQueryHandler)

from ankibot.dictionary.cambridge import CambridgeDictionary, Dictionary


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )


logger = logging.getLogger(__name__)

def parse_config():
    with open("config.toml", "rb") as f:
        return tomllib.load(f)

config = parse_config()
settings = config["settings"]


async def start_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    assert isinstance(update.effective_user, User)
    start_text = f"Hello, {update.effective_user.mention_html()}!\nUse /help command"
    await update.message.reply_html(start_text)


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    help_msg = "Commands:\n" \
        "/help - ...\n" \
        "/login - to connect to your ankiweb account\n"

    await update.message.reply_text(help_msg)


# async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     pass


# async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     pass


async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print all the words the user saved so far"""
    # TODO: generate a deck file?

    assert isinstance(context.user_data, dict)
    deck = context.user_data.get("deck", [])

    if len(deck) == 0:
        await update.message.reply_text("You have to add some words to your deck first")
        return

    msg = "\n------\n".join([str(i) for i in deck])
    await update.message.reply_text(msg)


# TODO: Implement
def validate_word(_word: str) -> bool:
    return True


async def lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dictionary = context.bot_data["cambridge_dict"]
    word = update.message.text

    if not validate_word(word):
        await update.message.reply_text("Incorrect input")
        return

    if word not in dictionary:
        await update.message.reply_text(f"{word} not found.")
        return

    assert isinstance(update.effective_user, User)
    await show5(update.effective_user, dictionary, word, 0)


async def button_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert isinstance(update.effective_user, User)
    assert isinstance(context.user_data, dict)

    dictionary = context.bot_data["cambridge_dict"]
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    data = query.data
    if data.startswith("more"):
        _, word, page = data.split("$")
        await show5(update.effective_user, dictionary, word, int(page)+1)
    else:
        word, idx = data.split("$")
        def_model = dictionary.get_definitions(word)[int(idx)]

        if "deck" not in context.user_data:
            context.user_data["deck"] = []
        deck = context.user_data["deck"]

        if word in deck:
            # TODO: implement comparison method for WordDefinition?
            await update.message.reply_text("Your deck already contains this word")
            return

        deck.append(def_model)
        await query.message.reply_text(f"Adding definition *{def_model.definition}* to your deck")


async def show5(user: User, dictionary: Dictionary, word: str, page: int) -> None:
    words_per_page = settings["words_per_page"]

    begin = words_per_page * page
    definitions = dictionary[word][begin:begin + words_per_page]

    if len(definitions) == 0:
        await user.send_message("No more definitions found")
        return

    end = begin + len(definitions)

    # create definitions list
    definitions_msg = "\n***\n".join([f"{begin + i + 1}. {d}" for i,
                                     d in enumerate(definitions)])

    # create buttons
    keyboard_numbers = [InlineKeyboardButton(
        str(i+1), callback_data=f"{word}${i}") for i in range(begin, end)]
    keyboard = [keyboard_numbers, [InlineKeyboardButton(
        "Show more", callback_data=f"more${word}${page}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await user.send_message(definitions_msg, reply_markup=reply_markup)


async def post_init(app: Application):
    """Initialize the bot data"""

    bot_data = app.bot_data

    if "cambridge_dict" not in bot_data:
        bot_data["cambridge_dict"] = CambridgeDictionary()


def main() -> None:
    setup_logging()

    logger.info("Starting the ankibot...")

    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    if token is None:
        logger.fatal("Could not find bot token")
        return

    filepath = "persistent_data"
    persistence = PicklePersistence(filepath=filepath)

    application = Application.builder()\
        .token(token)\
        .persistence(persistence)\
        .post_init(post_init)\
        .build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("all", all_command))
    # application.add_handler(CommandHandler("login", login_command))
    # application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, lookup_command))

    application.add_handler(CallbackQueryHandler(button_command))

    application.run_polling()


if __name__ == "__main__":
    main()
