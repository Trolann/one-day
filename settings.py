from dotenv import load_dotenv
from os import getenv

load_dotenv()

DISCORD_API_KEY = getenv("DISCORD_API_KEY")
GENERAL_CHAN_ID = int(getenv("GENERAL_CHAN_ID"))
OPENAI_API_KEY = getenv("OPENAI_API_KEY")

image_sys_prompt = """
You are an assistant being tasked with extracting the contents of the image below. Your goal is to extract, sort
and add any meaningful data into a concise bulletized list.

If the image is of a whiteboard it is likely containing notes about items todo around the house, shopping lists for 
groceries or purchases of household goods, or schedule items for members of the 4 person household. If an item is 
crossed out, indicate it using markdown ~~crossed out~~. 

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