import os
import datetime
import logging
import urllib.parse

from base64 import b64decode
from io import BytesIO
from json import loads as load_json

import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
    
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

description = 'memes'
intents = discord.Intents.default()
env_cmd_prefix = os.getenv('CMD_PREFIX')
prefix = env_cmd_prefix if env_cmd_prefix is not None else '!' 
bot = commands.Bot(command_prefix=prefix, description=description, intents=intents)

@bot.event
async def on_ready():
    logging.info(f'logged in as: {bot.user.name}, id: {bot.user.id}')
    join_url = os.getenv('JOIN_URL')
    join_url = join_url if join_url is not None else "https://developer.discord.com"
    logging.info(f'join the bot to your server using this url: {join_url}')

@bot.command()
async def tiktok(ctx):
    if ctx.channel.name in channel_whitelist:
        try:
            # stripping the '!tiktok' from the message via the ctx prefix (!) and the invoked_with (tiktok)
            user_input = ctx.message.content.replace(f'{ctx.prefix}{ctx.invoked_with}','').strip()
            logging.info(f' CMD: user: {ctx.author.name}, channel: {ctx.channel.name}, command: {ctx.invoked_with}, args: \'{user_input}\'')
            # replacing spaces and special characters with their URL encoded counterparts so the request to the tiktok api doesn't fail
            input_encoded = urllib.parse.quote_plus(user_input)
            # making a request to tiktok with our sanitised text, and saving the response's text (it's a json object that contains the mp3 base 64 encoded)
            response_json = requests.post(f"https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker=en_us_002&req_text={input_encoded}").text
            # parsing out the actual part that's the mp3 b64 string from the json: the .data.v_str object
            b64_mp3 = load_json(s=response_json)['data']['v_str']
            # decoding the base64 string to binary
            binary_mp3 = b64decode(s=b64_mp3, validate=False) 
            # making it palpable for discord by turning it into a python native byte object from a byte-like object(the binary string)
            binary_payload = BytesIO(binary_mp3)
            # building the discord api representation for the file object that we're sending back
            output_file = discord.File(fp=binary_payload, filename=f'tiktok_lady_{datetime.datetime.utcnow().isoformat()}.mp3')
            # yeet
            await ctx.send(file=output_file)
        except Exception as e:
            await ctx.send(content='sorry the tiktok lady is borked right now :(')
            logging.critical(f'something went wrong in the tiktok command. stack trace:\n\n{str(e)}')

@bot.command()
async def source(ctx):
    if ctx.channel.name in channel_whitelist:
        logging.info(f' CMD: user: {ctx.author.name}, channel: {ctx.channel.name}, command: {ctx.invoked_with}')
        await ctx.send(content='https://github.com/robot-o/staboto')

try:
    channel_whitelist = os.environ['CHANNEL_WHITELIST'].split(',')
except:
    logging.critical('failed to get CHANNEL_WHITELIST env variable. are you sure you\'ve set it?')
    exit(1)

bot.run(os.environ['DISCORD_TOKEN'])
