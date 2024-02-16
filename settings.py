from dotenv import load_dotenv
from os import getenv

load_dotenv()

DISCORD_API_KEY = getenv("DISCORD_API_KEY")
GENERAL_CHAN_ID = int(getenv("GENERAL_CHAN_ID"))