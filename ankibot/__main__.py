import logging
import os
import tomllib

from dotenv import load_dotenv

from ankibot.bot import AnkiBot


def main() -> None:
    """The main function of the ankibot."""

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    AnkiBot(token=token, config=config)


if __name__ == "__main__":
    main()
