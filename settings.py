from dotenv import load_dotenv
from os import getenv

load_dotenv()

DISCORD_API_KEY = getenv("DISCORD_API_KEY")
GENERAL_CHAN_ID = int(getenv("GENERAL_CHAN_ID"))
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")

image_sys_prompt = """
You are an assistant being tasked with extracting the contents of the image below. Your goal is to extract, sort
and add any meaningful data into a concise bulletized list.

If the image is of a whiteboard it is likely containing notes about items todo around the house, shopping lists for 
groceries or purchases of household goods, or schedule items for members of the 4 person household. 

Preexisting lists:
- Costco
- Groceries
- Target/Amazon
- Projects
- Chores
- Events
- Meals (Contains: Chicken Adobo, Carnitas Bowls, Orzo Soup)
"""
image_user_prompt = "\nFollow the system prompt. Be concise. Be clear. Hurry, if you do you will get a tip."

amazon_sys_prompt ="""
Given by the user is text extracted from a webpage. Your job is to return a map of the Order #, Amount and Items:

Instead of a direct copy/paste of items, try and offer a concise summary of the orders. Like 'Ninja valentines cards' or
'Gifts for kids and some new gloves' or 'Compressed air dispenser and a new cutting board' etc. 
"""

amazon_user_prompt = "Please extract the order number, the amount and the items from the text above."

AMAZON_LOGIN = getenv("AMAZON_LOGIN")
AMAZON_PASSWORD = getenv("AMAZON_PASSWORD")
AMAZON_ASSISTANT_ID = getenv("AMAZON_ASSISTANT_ID")
VIKUNJA_API_KEY = getenv("VIKUNJA_API_KEY")
VIKUNJA_API_URL = getenv("VIKUNJA_API_URL")
