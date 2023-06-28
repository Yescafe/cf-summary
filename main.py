import discord
import os
import dotenv
from binder import make_binder

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, proxy="http://127.0.0.1:7890")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    binder = make_binder()
    ret = binder.compile(message.content)
    if not ret is None:
        await message.channel.send(ret.strip())

client.run(os.getenv('TOKEN'))
