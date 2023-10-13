# pylint: disable=missing-function-docstring
# pylint: disable=fixme

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import (Application, CommandHandler, ContextTypes, MessageHandler,
    filters, PicklePersistence, CallbackQueryHandler)

from ankibot.dictionary.cambridge import CambridgeDictionary, Dictionary
from ankibot.errors import AnkiBotError
from ankibot.language_utils import init_nltk


logger = logging.getLogger(__name__)

class AnkiBot():
    """AnkiBot is the main class of the ankibot."""

    def __init__(
        self,
        *,
        token: str | None,
        is_persistent: bool = False,
        persistence_path: str = "",
        words_per_page: int = 10,

        **_kwargs
    ):
        self.token = token
        self.is_persistent = is_persistent
        self.persistence_path = persistence_path
        self.words_per_page = words_per_page

        init_nltk()

        self.app = self._build_app()
        self._register_handlers()

        self.app.run_polling()


    def _build_app(self) -> Application:
        self.builder = Application.builder()

        if self.is_persistent:
            persistence = PicklePersistence(filepath=self.persistence_path)
            self.builder.persistence(persistence)

        if not self.token:
            raise AnkiBotError("No token provided")

        self.builder.token(self.token)\
            .post_init(self._post_init)

        return self.builder.build()

    async def _post_init(self, app: Application):
        """Initialize the bot data"""

        bot_data = app.bot_data

        if "cambridge_dict" not in bot_data:
            bot_data["cambridge_dict"] = CambridgeDictionary()


    def _register_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("all", self.all_command))
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.lookup_command))

        self.app.add_handler(CallbackQueryHandler(self.button_command))


    async def start_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        assert isinstance(update.effective_user, User)
        start_text = f"Hello, {update.effective_user.mention_html()}!\nUse /help command"
        await update.message.reply_html(start_text)


    async def help_command(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""

        help_msg = "Commands:\n" \
            "/help - ...\n" \
            "/login - to connect to your ankiweb account\n"

        await update.message.reply_text(help_msg)


    async def all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    def validate_word(self, _word: str) -> bool:
        return True


    async def lookup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        dictionary = context.bot_data["cambridge_dict"]
        word = update.message.text

        if not self.validate_word(word):
            await update.message.reply_text("Incorrect input")
            return

        if word not in dictionary:
            await update.message.reply_text(f"{word} not found.")
            return

        assert isinstance(update.effective_user, User)
        await self.show5(update.effective_user, dictionary, word, 0)


    async def button_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            await self.show5(update.effective_user, dictionary, word, int(page)+1)
        else:
            word, idx = data.split("$")
            def_model = dictionary[word][int(idx)]

            if "deck" not in context.user_data:
                context.user_data["deck"] = []
            deck = context.user_data["deck"]

            if word in deck:
                # TODO: implement comparison method for WordDefinition?
                await update.message.reply_text("Your deck already contains this word")
                return

            deck.append(def_model)
            await query.message.reply_text(f"Adding definition *{def_model.definition}* to your deck")


    async def show5(self, user: User, dictionary: Dictionary, word: str, page: int) -> None:
        words_per_page = self.words_per_page

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
