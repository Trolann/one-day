import discord
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
        if files:
            request_dict['files'] = files
        image_pipe.send(request_dict)
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
            channel_id, message = raw_message_pipe.recv()
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(message)
            else:
                print(f"Channel with id {channel_id} not found")

def run_bot(systems_pipe_to_parent: Pipe, raw_message_pipe_to_parent: Pipe, image_pipe_to_parent: Pipe):
    print("Starting bot")
    global raw_message_pipe
    global systems_pipe
    global image_pipe
    systems_pipe = systems_pipe_to_parent
    raw_message_pipe = raw_message_pipe_to_parent
    image_pipe = image_pipe_to_parent
    asyncio.run(bot.start(DISCORD_API_KEY))

if __name__ == '__main__':
    asyncio.run(run_bot())
