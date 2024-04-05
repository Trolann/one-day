import discord
from time import time, sleep
from discord.ext import commands, tasks
from settings import DISCORD_API_KEY
from multiprocessing import Pipe
from inputs.new_image import is_image
import asyncio

# Set up intents to listen for user messages and member join events
intents = discord.Intents.all()
intents.messages = True
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix='$', intents=intents)

systems_pipe: Pipe = None
raw_message_pipe: Pipe = None
image_pipe: Pipe = None
audio_pipe: Pipe = None

@bot.event
async def on_ready():
    systems_pipe.send((0, "Bot is ready"))
    send_raw_message.start()
    print(f'{bot.user} has connected to Discord!')
    print(f'Connected to the following guilds:')
    for guild in bot.guilds:
        print(f'{guild.name}(id: {guild.id})')


@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    if message.content.lower().startswith('!amazon'):
        print(f"Received amazon command from {message.author}")
        raw_message_pipe.send((message.id, message.content))
        return



    # A simple ping pong to see if the bot is responding at all, before any other branches
    if message.content.lower().startswith('ping?'):
        print(f"Received ping from {message.author}")
        await message.reply('pong!')
        return


    if message.attachments:
        images = []
        files = []
        for attachment in message.attachments:
            if is_image(attachment.url):
                images.append(attachment.url)
            else:
                files.append(attachment.url)

        request_dict = {
            'message_id': message.id,
            'prompt': message.content
        }
        if images:
            request_dict['images'] = images
            image_pipe.send(request_dict)
        if '.ogg' in files[0]:
            request_dict['audio'] = files
            audio_pipe.send(request_dict)
        return
    if message.content:
        raw_message_pipe.send((message.id, message.content))

@bot.command()
async def ping(ctx):
    await ctx.send('pong!')

# Bot loop to receive messages from parent process and send them to Discord
@tasks.loop(seconds=0.1)
async def send_raw_message():
    if raw_message_pipe:
        while raw_message_pipe.poll():
            print("Received message from raw_message_pipe pipe")
            channel_id, message = raw_message_pipe.recv()
            channel = bot.get_channel(channel_id)

            if channel:
                if type(message) is list:
                    send_strs = await trim_messages(message)
                else:
                    send_strs = [message]
                for send_str in send_strs:
                    try:
                        await channel.send(send_str)
                    except Exception as e:
                        print(f"Error: {e}")
                        await channel.send(f'Error: {e}')
                        print(f"Message: {send_str}")
                print('Sent message')
            else:
                print(f"Channel with id {channel_id} not found")


async def trim_messages(message):
    print(f"Message is a list of length {len(message)}")
    send_strs = []
    send_str = ""
    for item in message:
        item_str = f"{item}\n"  # Convert dictionary to string and add newline
        if len(send_str + item_str) <= 2000:
            send_str += item_str
        else:
            send_strs.append(f"```python\n{send_str}\n```")  # Append the current string to send_strs
            send_str = item_str  # Start a new send_str with the current item
    # Make sure to add the last send_str if it's not empty
    if send_str:
        send_strs.append(f"```python\n{send_str}\n```")
    return send_strs


def run_bot(systems_pipe_to_parent: Pipe, raw_message_pipe_to_parent: Pipe, image_pipe_to_parent: Pipe, audio_pipe_to_parent: Pipe):
    print("Starting bot")
    global raw_message_pipe
    global systems_pipe
    global image_pipe
    global audio_pipe
    systems_pipe = systems_pipe_to_parent
    raw_message_pipe = raw_message_pipe_to_parent
    image_pipe = image_pipe_to_parent
    audio_pipe = audio_pipe_to_parent
    asyncio.run(bot.start(DISCORD_API_KEY))

if __name__ == '__main__':
    print('Starting the asyncio loop')
    asyncio.run(run_bot())
