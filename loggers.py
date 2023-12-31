import logging

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.basicConfig(
            level=logging.INFO,
            datefmt="[%d/%m/%Y %H:%M:%S]",
            format="%(asctime)s - [MASSACCOUNTCREATOR] >> %(levelname)s << %(message)s",
            handlers=[logging.FileHandler("mac.log"), logging.StreamHandler()],
    )