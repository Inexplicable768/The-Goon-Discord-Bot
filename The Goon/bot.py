import asyncio
import io
import json
import os
import random
import html
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from datetime import datetime

import spotipy as sp

### A DISCORD BOT MADE BY INEXPLICABLE768 ###
### ENJOY THE MESSY CODE ###

# setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)
client = discord.Client(intents=intents)
DATA_FOLDER = "./data"
PASSCODE = "goon6767%"

user_agent = {
    "User-Agent": "https://replit.com/@mathematicaency/TheGoon#main.py, v1.0)"
}
custom_emojis = [
    "<:ocelot:1394152101864669235>", "<:lazermax:1394151691749949632>",
    "<:orangeman:1394151590553980998>", "<a:fdiscordmods:1394151257375113458>",
    "<:killme:1394151095122792448>", "<:missing:1394150968706469938>",
    "<:vincentvangofyourself:1394150760027127900>",
    "<:cornluke:1394150657577189479>", "<:max:1394150597514498128>",
    "<:letmegoon:1394150527528337419>", "<:garlicquentin:1394150107145965729>",
    "<:andrewvodka:1394150028163027076>", "<:thatspea:1394149976439001200>",
    "<:meltingdrew:1394149942301294765>",
    "<:idontmindthesmell:1394149520710832218>",
    "<:hammers:1394149453107040338>", "<:getajob:1394022666314322012>",
    "<:diddytesla:1394022591177429012>", "<:thegoon:1394022544218001459>"
]

soundboard_sounds = {
    "airhorn": "sounds/airhorn.mp3",
    "bruh": "sounds/bruh.mp3",
    "sad trombone": "sounds/sad_trombone.mp3",
    "fart": "sounds/fart.mp3",
    "rimshot": "sounds/rimshot.mp3"
}
# === points system ===

from typing import Dict
DATA_DIR = "server_data"  

def read_points(server_id: str) -> Dict[str, int]:
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = os.path.join(DATA_DIR, f"{server_id}_points.json")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else {}
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"[{server_id}] Points file missing or corrupted. Creating a new one.")
        return {}


def write_points(server_id: str, points: Dict[str, int]) -> bool:
    if not isinstance(points, dict):
        raise TypeError("points must be a dictionary")

    os.makedirs(DATA_DIR, exist_ok=True)
    filename = os.path.join(DATA_DIR, f"{server_id}_points.json")
    temp_filename = filename + ".tmp"

    try:
        # Write to temp file first (prevents corruption)
        with open(temp_filename, "w", encoding="utf-8") as f:
            json.dump(points, f, indent=2)

        os.replace(temp_filename, filename)
        return True

    except Exception as e:
        print(f"Error writing {filename}: {e}")
        return False
    

def add_points(server_id: str, user_id: str, amount: int) -> int:
    points = read_points(server_id)

    # Ensure user exists
    points[user_id] = points.get(user_id, 0) + amount

    write_points(server_id, points)
    return points[user_id]

def set_points(server_id: str, user_id: str, amount: int) -> int:
    points = read_points(server_id)

    # Set user points
    points[user_id] = amount

    write_points(server_id, points)
    return points[user_id]


async def sync_points_for_guild(guild: discord.Guild, default_points: int = 1000):
    points = read_points(str(guild.id))
    updated = False

    for member in guild.members:
        if member.bot:
            continue

        user_id = str(member.id)

        if user_id not in points:
            points[user_id] = default_points
            updated = True

    if updated:
        write_points(str(guild.id), points)
        print(f"[{guild.name}] Points synced.")


# auxiliary function to play a sound in a voice channel
async def play_sound(bot: discord.Client,channel: discord.VoiceChannel,file_path: str,volume: float = 1.0,disconnect_after: bool = True):
    voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
    if voice_client is None:
        voice_client = await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)
    audio_source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(file_path),
        volume=volume
    )
    voice_client.play(audio_source)
    while voice_client.is_playing():
        await asyncio.sleep(0.5)
    if disconnect_after:
        await voice_client.disconnect()




# this should help the bot stay in the call maybe?
class Silence(discord.PCMVolumeTransformer):

    def __init__(self):
        super().__init__(
            discord.FFmpegPCMAudio(
                "pipe:0",
                pipe=True,
                stderr=None,
                before_options="-f lavfi -i anullsrc=r=48000:cl=stereo"))

    def read(self):
        return b'\x00' * 3840  # 20ms of stereo silence at 48kHz (2 channels * 2 bytes * 960 samples)


# CONSTANTS AND DATA SECTION

permissions_integer = 586005375540800
version = "v1.4.0"

# path to anime trivia questions data file
ANIME_TRIVIA_FILE = "data/anime_trivia.txt"
# hangman words. some are normal some are not
WORDS = [
    "apple", "banana", "orange", "grape", "peach", "mango", "cherry", "lemon", "lime", "melon",
    "kiwi", "papaya", "apricot", "avocado", "coconut", "fig", "guava", "nectarine", "pear", "plum",
    "raisin", "strawberry", "blueberry", "raspberry", "blackberry", "pineapple", "pomegranate",
    "watermelon", "cantaloupe", "honeydew", "computer", "keyboard", "monitor", "mouse", "laptop",
    "printer", "router", "server", "browser", "software", "hardware", "network", "database",
    "algorithm", "function", "variable", "integer", "boolean", "string", "package", "module",
    "library", "framework", "sandbox", "virtual", "container", "compile", "execute", "debug",
    "iterate", "bicycle", "airplane", "helicopter", "submarine", "scooter", "skateboard", "train",
    "trolley", "highway", "bridge", "tunnel", "airport", "station", "harbor", "island", "desert",
    "forest", "jungle", "mountain", "valley", "river", "ocean", "glacier", "volcano",
    "earthquake", "hurricane", "tornado", "rainbow", "thunder", "lightning", "shadow", "mirror",
    "window", "doorway", "hallway", "ceiling", "carpet", "pillow", "blanket", "mattress",
    "wardrobe", "dresser", "bookshelf", "cabinet", "countertop", "sink", "faucet", "toilet", "shower",
    "diddy", "skibidi", "gyatt", "lock in twin", "the goon", "boner", "clanker", "jazz", "anime",
    "goku", "naruto", "sasuke", "vegeta", "luffy", "zoro", "saitama", "todoroki", "eren", "mikasa","attack on titan",
    "death note", "fullmetal alchemist", "one piece", "my hero academia", "dragon ball", "bleach", "fairy tail", "demon slayer", "jujutsu kaisen",
    "hunter x hunter", "neon genesis evangelion", "cowboy bebop", "samurai champloo", "steins gate", "code geass", 
    "tokyo ghoul", "black clover", "mob psycho 100", "the promised neverland", "dragon quest", "fire emblem", "final fantasy", "the legend of zelda", "pokemon", "metroid", "halo", "call of duty",
    "fortnite", "minecraft", "roblox", "among us", "apex legends", "overwatch", "league of legends", "dota 2", "valorant",
    "counter strike", "world of warcraft", "the witcher", "cyberpunk", "red dead redemption", "grand theft auto",
    "shinji", "asuka", "rei", "kaiji", "l", "light yagami", "ryuk", "itachi", "kakashi", "shikamaru", "hinata",
    "sakura", "deku", "bakugo", "all might", "shoto", "eren yeager", "levi ackerman", "mikasa ackerman"
]

games = {}
numbers = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
about_i = [
    "I am the goon *belches loudly*",
    "I have no idea why I exist why are you asking me nerd",
    "Tell me about you first", "We can be bees!", "Gaze upon my massive belly",
    "https://tenor.com/view/it's-been-awhile-its-been-a-while-omni-man-omni-man-meme-invincible-gif-17023911097105463424"
]

bird_images = [
    "https://plus.unsplash.com/premium_photo-1661962626711-8121c34826c2?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8ZnVubnklMjBiaXJkfGVufDB8fDB8fHww",
    "https://images.unsplash.com/photo-1680749512096-9bd509915e53?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZnVubnklMjBiaXJkfGVufDB8fDB8fHww",
    "https://images.unsplash.com/photo-1581362662614-dd27d9eb9291?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8ZnVubnklMjBiaXJkfGVufDB8fDB8fHww",
    "https://plus.unsplash.com/premium_photo-1669810168690-dfc19be1e765?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8ZnVubnklMjBiaXJkfGVufDB8fDB8fHww",
    "https://images.unsplash.com/photo-1620093339029-ad07db9d6d35?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTh8fGZ1bm55JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D",
    "https://images.unsplash.com/photo-1592620478369-e0e0d12e9564?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjJ8fGZ1bm55JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D",
    "https://images.unsplash.com/photo-1659884535789-539040dbbfeb?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mjl8fGZ1bm55JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D",
    "https://images.unsplash.com/photo-1699735129464-4aad9f54fa7b?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDN8fGZ1bm55JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D",
    "https://images.unsplash.com/photo-1705351978886-3b7d1e211753?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDV8fGZ1bm55JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D",
    "https://plus.unsplash.com/premium_photo-1694621017917-bd784f857235?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NTl8fGZ1bm55JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D",
    "https://images.unsplash.com/photo-1694316286534-3304eb00c455?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTA5fHxmdW5ueSUyMGJpcmR8ZW58MHx8MHx8fDA%3D",
    "https://plus.unsplash.com/premium_photo-1674381523736-e6fdc5c1e708?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTExfHxmdW5ueSUyMGJpcmR8ZW58MHx8MHx8fDA%3D",
    "https://images.unsplash.com/photo-1699735129478-f89275a3e601?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTIxfHxmdW5ueSUyMGJpcmR8ZW58MHx8MHx8fDA%3D",
    "https://vistapointe.net/images/vladimir-putin-4.jpg"
]

verses = [
    "John 3:16", "Genesis 1:1", "Psalm 23:1", "Romans 8:28",
    "Philippians 4:13", "Proverbs 3:5", "Isaiah 41:10", "Matthew 6:33",
    "Jeremiah 29:11", "1 Corinthians 13:4", "Romans 12:2", "Joshua 1:9",
    "Hebrews 11:1", "1 John 4:8", "Psalm 46:10", "2 Timothy 1:7", "James 1:5",
    "Matthew 11:28", "Ephesians 2:8", "Galatians 5:22", "Isaiah 40:31",
    "Matthew 5:16", "Colossians 3:23", "Psalm 119:105", "1 Thessalonians 5:16",
    "Romans 5:8", "John 14:6", "Proverbs 18:10", "Romans 10:9", "1 Peter 5:7",
    "2 Chronicles 7:14", "Psalm 37:4", "John 8:12", "Romans 6:23", "Luke 6:31",
    "Philippians 4:6", "Proverbs 16:3", "Matthew 28:19", "1 Corinthians 10:13",
    "Psalm 34:18", "Isaiah 26:3", "Galatians 2:20", "1 John 1:9",
    "Exodus 14:14", "Psalm 121:1", "2 Corinthians 5:17", "Hebrews 13:5",
    "Acts 1:8", "Ephesians 6:11", "James 1:2", "Micah 6:8", "Matthew 22:37",
    "Lamentations 3:22", "Romans 15:13", "Isaiah 43:2", "1 Corinthians 15:58",
    "Philippians 2:3", "Ephesians 4:29", "Psalm 19:14", "Deuteronomy 31:6",
    "Colossians 3:2", "2 Corinthians 12:9", "Hebrews 4:12", "Matthew 7:7",
    "Romans 8:38", "Psalm 91:1", "Ecclesiastes 3:1", "1 Corinthians 6:19",
    "Proverbs 4:23", "Galatians 6:9", "Titus 2:11", "Nahum 1:7",
    "Zephaniah 3:17", "Mark 12:30", "Psalm 139:14", "Luke 1:37",
    "Matthew 5:14", "1 John 5:14", "James 4:7", "Proverbs 27:17", "Psalm 27:1",
    "Isaiah 53:5", "Ephesians 3:20", "Hebrews 10:24", "Colossians 2:6",
    "2 Peter 3:9", "1 Timothy 6:12", "Job 19:25", "Psalm 30:5", "Luke 11:9",
    "Romans 3:23", "John 10:10", "Isaiah 55:8", "Matthew 18:20",
    "Revelation 21:4", "Acts 2:38", "John 15:5", "Psalm 90:12",
    "Ephesians 5:2", "1 John 2:17", "2 Timothy 3:16", "Psalm 100:4",
    "Matthew 6:9", "Hebrews 12:1", "Jeremiah 17:7"
]

iris_songs = [
    "https://www.youtube.com/watch?v=nVSa9OJboIM",
    "https://www.youtube.com/watch?v=3HR52f-T7s8",
    "https://www.youtube.com/watch?v=U4ZspzDkm4Q",
    "https://www.youtube.com/watch?v=5y8AT2h04Q4",
    "https://www.youtube.com/watch?v=lj565P1LjaM",
    "https://www.youtube.com/watch?v=5y8AT2h04Q4",
    "https://www.youtube.com/watch?v=o8hmMQYcL2M",
    "https://www.youtube.com/watch?v=ih_ITHGM_Uo",
    "https://www.youtube.com/watch?v=L7yjXlmDZ_A",
    "https://www.youtube.com/watch?v=8AdYz4Y0pUs",
    "https://www.youtube.com/watch?v=drNBS0jjgh8",
    "https://www.youtube.com/watch?v=j4Eoy-8fejM",
    "https://www.youtube.com/watch?v=CwrsUzyqflU",
    "https://www.youtube.com/watch?v=c9cvcQGXMdw",
]
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'quiet': True,
    'extract_flat': False
}
FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


# === utilities ===
def get_coordinates_from_zip(zip_code: int, country="US"):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "postalcode": zip_code,
        "country": country,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "weather-info-goon"}
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    if results:
        lat = float(results[0]['lat'])
        lon = float(results[0]['lon'])
        return lat, lon
    return None, None


def far(celcius: float):
    return celcius * 1.8 + 32

def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02}:{minute:02}"

def clear_slop():
    pass

async def list_members(guild: discord.Guild):
    return [member async for member in guild.fetch_members(limit=50)]

# math utilities for the calculator command

# === events ===


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if "fuck" in message.content:
        await message.channel.send("Oopsie poopsie you said a no no word.")
    if "nigger" in message.content:
        await message.channel.send(f" @{message.author.display_name} RACIST!!!")
   


# loading event code
@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f"Connected to guild: {guild.name} (ID: {guild.id})")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands globally")

        for guild in bot.guilds:
            guild_obj = discord.Object(id=guild.id)
            synced_guild = await bot.tree.sync(guild=guild_obj)
            print(f"Synced {len(synced)} commands to {guild.name}")
            await sync_points_for_guild(guild)

    except Exception as e:
        print(f"Failed to sync commands: {e}")

    print(f"Bot is online as {bot.user}")


# when a member joins
@bot.event
async def on_member_join(member):
    if member.bot:
        return

    points = read_points(str(member.guild.id))
    user_id = str(member.id)

    if user_id not in points:
        points[user_id] = 0
        write_points(str(member.guild.id), points)
    channels = ['main', 'general', 'welcome', 'home', 'hello']
    for n in channels:
        channel = discord.utils.get(member.guild.text_channels, name=n)
        if channel:
            await channel.send(f"Hello, {member.mention} welcome.")
            await channel.send(
                "https://tenor.com/view/it's-been-awhile-its-been-a-while-omni-man-omni-man-meme-invincible-gif-17023911097105463424"
            )
            break
        else:
            print("Channel not found :(")


# === commands ===


@bot.tree.command(
    name="gpurge",
    description=
    "remove the last n messages in the channel. Admin use only. Can take max 1000"
)
@app_commands.checks.has_permissions(administrator=True)
async def gpurge(interaction: discord.Interaction, amount: int):
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "This command can only be used in a text channel.")
        return
    if amount > 1000:
        await interaction.response.send_message(
            "You can only delete up to 1000 messages at a time.")
        return
    await interaction.response.defer()
    deleted = await interaction.channel.purge(limit=amount)


@bot.tree.command(name="about", description="A totally normal about message")
async def about(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(about_i))

@bot.tree.command(name="soundboard", description="play a sound from the goon's soundboard")
async def soundboard(interaction: discord.Interaction, sound: str): # attach a file
    await interaction.response.send_message("Soundboard command")
    # Implement soundboard functionality here

@bot.tree.command(name="play_mp3", description="Play an attached mp3 file in a vc")
async def playmp3(interaction: discord.Interaction, attac: discord.Attachment): # attach a file
    await interaction.response.send_message("Soundboard command")

# IMPLEMENT HERE: PLAY SPOTIFY SONG


@bot.tree.command(
    name="debug",
    description=
    "Intended for admins. A way to see if the bot is working and see info about the server"
)
async def debug(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Bot User Id {bot.user} \n Connected to guild: {interaction.guild.name}\n (ID: {interaction.guild.id}) \nBot version: {version} \nBot latency: {round(bot.latency * 1000)} ms \n Bot permissions: {permissions_integer}"
    )


@bot.tree.command(name="ping_me", description="Ping the bot to see latency")
async def ping_me(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Ping Latency: {latency} ms")


@bot.tree.command(name="roll_die", description="Roll an n sided die")
async def roll_die(interaction: discord.Interaction, sides: int):
    choice = random.randint(1, sides)
    await interaction.response.send_message(
        f":game_die: You rolled a: {choice}")


@bot.tree.command(name="flip_coin",
                  description="Flip a coin, what else do you want...")
async def flip_coin(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Coin Flip: {random.choice(['Heads', 'Tails'])}")


@bot.tree.command(
    name="random_user",
    description=
    "Picks a random user from the server. Do what you want with this info, im not your mom"
)
async def random_user(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server.")
        return
    members = await list_members(interaction.guild)
    selected = random.choice(members)
    await interaction.response.send_message(
        f"Selected: {selected.display_name}")


@bot.tree.command(
    name="marry_kiss_kill",
    description=
    "A totally family friendly game. Choose 1 to marry, 1 to kiss, 1 to kill. YOU HAVE TO."
)
async def marry_boff_kill(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server.")
        return
    members = await list_members(interaction.guild)
    selected = random.sample(members, 3)
    await interaction.response.send_message(
        f"MBK: {', '.join(m.display_name for m in selected)}")


@bot.tree.command(
    name="drinking_game",
    description="Take a drink every time what the goon says happens")
async def drinking_game(interaction: discord.Interaction):
    await interaction.response.send_message("DONT DRINK KIDS")



@bot.tree.command(
    name="phasmo_item",
    description="Helpful for phasmophobia tarot card roulette or other uses")
async def phasmo_item(interaction: discord.Interaction):
    items = [
        "Video Camera", "Photo Camera", "Tripod", "D.O.T.S", "UV Light",
        "Salt", "Sanity Pills", "Smudge & Matches", "Sound Recorder",
        "Sound Sensor", "Crucifix", "Para-mic", "EMF Reader", "Thermometer",
        "Candle", "Notepad", "Spirit Box", "Motion Sensor", "Headgear",
        "Flashlight", "Sound Recorder"
    ]
    await interaction.response.send_message(
        f"Item Selected: {random.choice(items)}")


@bot.tree.command(name="phasmo_ghosts", description="Bet on a random ghost")
async def phasmo_ghosts(interaction: discord.Interaction):
    ghosts = [
        "Spirit", "Wraith", "Phantom", "Poltergeist", "Banshee", "Jinn",
        "Mare", "Revenant", "Shade", "Demon", "Yurei", "Oni", "Yokai", "Hantu",
        "Goryo", "Myling", "Onryo", "The Twins", "Raiju", "Obake", "The Mimic",
        "Moroi", "Deogen", "Thaye"
    ]
    await interaction.response.send_message(
        f"Ghost Selected: {random.choice(ghosts)}")


@bot.tree.command(name="phasmo_challenge",description="Get a random challenge for phasmophobia")
async def phasmo_challenge(interaction: discord.Interaction):
    challenges = [
      "No Flashlights", "No Sprinting", "One Hand Only", "No Sanity",
      "Talk With Tongue Out", "Smudges Only", "Asylum Nightmare","Cursed Posseession Roulette","Tarot Roulette",
      "Power Outage", "Ouija Board Roulette", "Alone With The Ghost", "One in One Out", "Hide and Seek", "Drink If You Die",
      "No Pills", "Locked Doors", "No Lights IRL", "Amish Mode", "Burglery", "No Hiding Places", "German Mode", "Japanese Mode", "Italian Mode",
      "Lighter Only", "Fast Ghost", "Jesus Freak", "Live and Learn", "Spirit Box Roulette", "Drew Soundboard", "Conseula Andrew", "Flirt With The Ghost", 
      "Smokers Lung", "Thunderstorm", "Fox News Version", "One Word","Inumaki Mode", "Crippled Mode", "Must Talk During Hunts", "Couples Mode", "Singing During Hunts", 
      "Lethal Company Mode", "Ching Chong Mode", 
    ]
    challenge_desc = [
        "You cannot bring or use flashlights during the game", "You cannot sprint during the game","Play Using 1 Hand!", "Start at 0 sanity and cannot use pills",
        "You must talk with your tongue out the entire game", "You can only use smudges and no other items","Play on asylum on nightmare difficulty", "Pass around a cursed possession item to a new person every minute",
        "Follow the rules listed in #phasmo", "No Lights can be turned on.", "Ask the ouija board a question every minute", "You cannot leave the ghost room once found",
        "Only one person can enter the building at a time", "Play hide and seek with eachother and try not to die", "Take a shot every time you die for the next 3 games",
        "You cannot use sanity pills", "Once you enter the house you cannot leave", "Shut off all lights in your room while playing", "Party like its 1699. No technology allowed",
        "Steal as many items you can from the ghosts house. If anyone dies you all lose", "Disable Hiding Spots","Change the langauge to german","Change the language to japanese","Change the language to italian",
        "You can only use a lighter as a light source","Fast boi ghost", "Act like luke gregory (jesus freak) every time a ghost event or hunt happens. You can only use crucifixs and smudges", 
        "Play the song by crush40 live and learn when someone dies", "Pass around the spirit box. You can only ask funny or stupid questions. Take a drink if the ghost answers", 
        "Drew can only use soundboard sounds to communicate during hunts","Andrew must talk as consula during hunts", "Flirt with the ghost every chance you get",
        "Talk like youve been smoking for 90 years every time a ghost event happens", "Make the weather thunderstorm in game settings", "Say the oppisite of whats true for evidence gathered",
        "You have to say one word through the radio until someone else responds","Salmon. Benito Flakes. Kelp", "Crouch the whole game", "Try to have a normal conversation while a ghost tries to kill you", 
        "Split into pairs and you have to walk inside eachother", "Sing very loudly during a hunt", "3 people are the company and 1 person is forced to go in",
        "Talk in broken english or a chinese accent", 
    ]
    challenge = random.choice(challenges)

    await interaction.response.send_message(
        f"Challenge Selected: {challenge} description: {challenge_desc[challenges.index(challenge)]}"
    )
    

@bot.tree.command(name="trump", description="Can you tell which ones he said and which he didnt? HINT: its all")
async def trump(interaction: discord.Interaction):
    trump_quotes = [
        "The Biden administration spent $8 million making mice transgender",
        "I have the best words, I have the best, but there is no better word than 'stupid'",
        "Our country is being run by maniacs, and I don't mean me",
        "we must build a wall, and Mexico is going to pay for it",
        "I will be the greatest jobs president that God ever created",
        "Nobody knows more about trade than me. Nobody.",
        "I have a very big abrain",
        "My uncle was a great professor at MIT for many years… so I understand nuclear."
        "Despite the constant negative press covfefe",
        "I think I am actually humble. I think I’m much more humble than you would understand",
        "Windmills cause cancer.",
        "I could stand in the middle of Fifth Avenue and shoot somebody, and I wouldn’t lose any voters.",
        "I’m, like, a really smart person",
        "It's freezing and snowing in New York – we need global warming!",
        "Sorry losers and haters, but my I.Q. is one of the highest -and you all know it!",
        "Our Army manned the air, it rammed the ramparts, it took over the airports. It did everything it had to do (refering to 1776)",
        "If Ivanka weren’t my daughter, perhaps I’d be dating her", 
        "The kidney has a very special place in the heart.", 
        "And then I see the disinfectant, where it knocks it out in a minute… is there a way we can do something like that, by injection inside?” (2020, COVID briefing)",
        "https://www.youtube.com/watch?v=UNqiIglMVBo",
        "We are a nation that just recently heard that saudia arabia and russia will reepodee uhhhh",
        "Obamna",
        "About 40% of fresh vegables at about 40%", 
        "We will reduce drug prices by 1200. 1300. 1500 16 17 even 2000 percent",
        "people don’t really know if Denmark has any legal rights to [Greenland]",
        "They are dangerous,” Trump said on the matter. “You see what’s happening up in the Massachusetts area with the whales … The windmills are driving the whales crazy, obviously",
        "Let’s put her with a rifle standing there with nine barrels shooting at her, let’s see how she feels about it. You know, when the guns are trained on her face",
        "Everything is perfect. Her undergarments, sometimes referred to as panties, are folded perfectly, wrapped. They're, like, so perfect. I think that she steams them",
        "I love the poorly educated", 
        "This is a guy that was all man. This man was strong and tough, and I refused to say it, but he took showers with the other pros, they came out of there, they said, ‘oh my God, that’s unbelievable’. I had to say it.",
        "I am the father of IVF",
        "Around the globe everyone is talking about artificial intelligence. I find that too artificial, I can’t stand it. I don’t even like the name",
        "It’s okay to call my daughter a ‘piece of ass’ ",
        "They call me the president of Europe. Which is an honor.",
        "They call him Darth Vader, I call him a fine man",
        "The late great hannibal lecter. Was a great man. He would often have a friend for dinner",
        "She gets over that big barbell and she gets it up and she... ohh uhh phhh",
        "Theyre eating the cats, theyre eating the dogs",
        "I've known Jeff [epstien]for 15 years. Terrific guy. He's a lot of fun to be with. It is even said that he likes beautiful women as much as I do, and many of them are on the younger side",
        "We have concepts of a plan"
        


    ]
    await interaction.response.send_message(random.choice(trump_quotes))

@bot.tree.command(name="day", description="What day")
async def day(interaction: discord.Interaction):
    day_gifs = [ # evangelion day of the week gifs
        ["https://tenor.com/view/misato-katsuragi-evangelion-monday-gif-17874469027297406149", "https://tenor.com/view/evangelion-eva-neon-genesis-monday-gif-22825465",
         "https://tenor.com/view/misato-katsuragi-misato-monday-misato-noodles-misato-ramen-monday-gif-17259092371060544500", "https://tenor.com/view/neon-genesis-evangelion-evangelion-misato-monday-misato-monday-gif-24456753",
         "https://tenor.com/view/today-is-monday-gif-15908032799820029633", "https://tenor.com/view/misato-misato-monday-evangelion-gif-8952534871494026624", 
         "https://tenor.com/view/asuka-evangelion-eva-monday-asuka-monday-gif-21221631", "https://tenor.com/view/evangelion-evangelion-monday-toji-toji-suzuhara-kerokitty-gif-25294559",
         "https://tenor.com/view/penpen-penpenmonday-codex-cozy-evangelion-gif-24946363"],
        ["https://tenor.com/view/misato-tuesday-martes-evangelion-gif-25307441", "https://tenor.com/view/evangelion-eva-tuesday-neon-genesis-gif-22825472"],
        []
    ]
    day = datetime.datetime.now().strftime("%A")
    await interaction.response.send_message("Day of the week")


@bot.tree.command(name="birthday", description="Set a reminder for your birthday so the goon can announce it")
async def bday(interaction: discord.Interaction, day: str):
    with open("birthdays.txt", "a") as f:
        f.write(f"{interaction.user.id},{interaction.user.display_name},{day}\n")
    await interaction.response.send_message(f"Birthday set for {day}")


@bot.tree.command(name="bird_picture",
                  description="Why youd need this im not sure but here it is")
async def bird_picture(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(bird_images))


def check_weather_alerts(zip):
    lat, lon = get_coordinates_from_zip(zip)
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    headers = {
        "User-Agent": "my-weather-app/1.0 (your_email@example.com)"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    if not data["features"]:
        return False # no weather alerts
  
    return data


@bot.tree.command(name="weather", description="wanna touch grass today")
async def weather(interaction: discord.Interaction, zipcode: int):
    lat, lon = get_coordinates_from_zip(zipcode)
    if lat is None:
        await interaction.response.send_message(
            "Could not find location for that ZIP code.")
        return

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "precipitation"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "current_weather" not in data:
            raise KeyError("Missing 'current_weather'")

        # check for weather alerts

        alert = check_weather_alerts(zipcode) # returns true if there is an alert

        weather = data["current_weather"]
        await interaction.response.send_message(
            f"Weather at {zipcode} \nTemperature: {weather['temperature']}°C / {far(float(weather['temperature'])):.1f}°F\n" +
            f"Wind Speed: {weather['windspeed']} km/h\nWind Direction: {weather['winddirection']}° \n" +
            f"Precipitation (next 3 hours): {data['hourly']['precipitation'][0]} mm , {data['hourly']['precipitation'][1]} mm, {data['hourly']['precipitation'][2]} mm\n"
            )
        if alert != False:
            event_name = alert["features"][0]["properties"]["event"]
            severity = alert["features"][0]["properties"]["severity"]
            area = alert["features"][0]["properties"]["areaDesc"]
            headline = alert["features"][0]["properties"]["headline"]
            instruct = alert["features"][0]["properties"]["instruction"]

            await interaction.followup.send("⚠️ SEVERE WEATHER ALERT ⚠️  \n" +
               f"{event_name}\n" +
               f"{severity}  \n"+
               f"{area}\n" +
               f"{headline}\n" +
               f"{instruct}"
            )
                                            
                                
       
       
       

    except Exception as e:
        print("Weather error:", e)
        await interaction.response.send_message("Failed to fetch weather data."
                                                )


@bot.tree.command(name="random_list", description="pick from a list of things")
async def random_list(interaction: discord.Interaction, args: str):
    """Choose a random item from a user-given list"""
    if not args:
        await interaction.response.send_message(
            "Please give me a list to pick from.")
        return
    await interaction.response.send_message(f"Selected: {random.choice(args)}")


@bot.tree.command(name="iris",
                  description="play a PEAK song from IRIS offical")
async def iris(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(iris_songs))


@bot.tree.command(name="did_you_pray_today", description="Did you pray today?")
async def did_you_pray_today(interaction: discord.Interaction):
    await interaction.response.send_message("Did you pray today?")
    await interaction.followup.send(
        "https://www.youtube.com/watch?v=cMsoDefWep8")


asmr_videos = [
    "https://www.youtube.com/watch?v=rvoLyfQSN1w",
    "https://www.youtube.com/watch?v=AUs0WWQR96A"
]
@bot.tree.command(name="asmr",
                  description="sends a relaxing asmr video... yes")
async def asmr(interaction: discord.Interaction):
    await interaction.response.send_message("Sleep Bronana Peel")
    await interaction.followup.send(
        random.choice(asmr_videos)
    )
@bot.tree.command(name="hawk_tuah",
                  description="sleep")    
async def hawk_tuah(interaction: discord.Interaction):    
    await interaction.response.send_message("Sleep Fam")
    await interaction.followup.send("https://www.youtube.com/watch?v=rvoLyfQSN1w")

@bot.tree.command(name="dragonforce", description="epic")
async def dragonforce(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://www.youtube.com/watch?v=cqH1kMG5P0Q")

# GAMES 

@bot.tree.command(name="roulette", description="Test your luck at roulette")
async def roulette(interaction: discord.Interaction,
                   color: str,
                   num: str,
                   money: int = 100) -> None:
    """Play Roulette. Bet on a number or color. enter NONE for number to bet on color only"""
    color = color.strip().lower()
    number = random.randint(0, 36)
    if number == 0:
        winning_color = 'green'
    elif number % 2 == 0:
        winning_color = 'black'
    else:
        winning_color = 'red'

    await interaction.response.send_message("The ball landed on {} {}".format(
        winning_color, number))

    # Check for wins
    if color == winning_color and num == 'NONE' and winning_color != 'green':
        money *= 2
        await interaction.followup.send(
            "You won with a payout of 2:1. Your money is now {}".format(money))
    elif color == 'NONE' and num == str(
            number) or winning_color == color and winning_color == 'green':
        money *= 36
        await interaction.followup.send(
            "You won with a payout of 35:1. Your money is now {}".format(money)
        )
    else:
        await interaction.followup.send(
            "You lost! Your money is now {}".format(money))

    await interaction.followup.send(
        "Thanks for playing! Use the command again to play another round.")
    
# note: add goon points system later
@bot.tree.command(name="slot_machine", description="More gambling oh boy")
async def slot_machine(interaction: discord.Interaction):
    money = read_points(str(interaction.guild.id))
    user_id = str(interaction.user.id)
    money = money.get(user_id, 0)
    if money < 100:
        await interaction.response.send_message(
            "You need at least 100 points to play the slot machine.")
        return
    money -= 100  # cost to play
    """Play a simple slot machine game"""
    symbols = ['🍒', '🍋', '🍊', '🍉', '⭐', '🔔', '7️⃣']
    reel1 = random.choice(symbols)
    reel2 = random.choice(symbols)
    reel3 = random.choice(symbols)

    await interaction.response.send_message(
        "Spinning... {} | {} | {}".format(reel1, reel2, reel3))

    if reel1 + reel2 + reel3 == "7️⃣7️⃣7️⃣":
        money *= 25
        await interaction.followup.send(
            "🎉GOONPOT!!!🎉 - You won with a payout of 25:1. Your money is now {}".format(
                money)
        )
    elif (reel1 + reel2 + reel3).count('7️⃣') == 2:
        money *= 10
        await interaction.followup.send(
            "🎉BIG WIN!🎉 - You won with a payout of 10:1. Your money is now {}".format(
                money))
    elif reel1 == reel2 == reel3:
        money *= 5
        await interaction.followup.send(
            "MODERATE WIN! - You won with a payout of 5:1. Your money is now {}".format(
                money))
    elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
        await interaction.followup.send(
            "SO CLOSE GOONER. You lost! Your money is now {}".format(money))
    else:
        await interaction.followup.send(
            "YOU LOST! and this clanka won! Your money is now {}".format(money))

    await interaction.followup.send(
        "Thanks for playing! Use the command again to play another round.")
    set_points(str(interaction.guild.id), user_id, money)




@bot.tree.command(name='blackjack', description="Play blackjack")
async def blackjack(interaction: discord.Interaction, money: int = 100):
    """Play Blackjack"""
    deck = [n + ' of ' + s for n in numbers for s in suits]
    random.shuffle(deck)
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    await interaction.response.send_message("Card: {}".format(player_hand[0]))
    await interaction.followup.send("hit or stand?")
    while True:
        response = await bot.wait_for(
            'message',
            check=lambda message: message.author == interaction.user)
        if response.content.lower() == 'hit':
            player_hand.append(deck.pop())
            await interaction.followup.send("Card: {}".format(player_hand[-1]))
            if sum([int(card.split()[0]) for card in player_hand]) > 21:
                await interaction.followup.send("Bust! You lose.")
                break
        elif response.content.lower() == 'stand':
            while sum([int(card.split()[0]) for card in dealer_hand]) < 17:
                dealer_hand.append(deck.pop())
            await interaction.followup.send(
                "Dealer's hand: {}".format(dealer_hand))
            if sum([int(card.split()[0]) for card in dealer_hand]) > 21:
                await interaction.followup.send("Dealer busts! You win.")
                money *= 2
                await interaction.followup.send(
                    "Your money is now {}".format(money))
            elif sum([int(card.split()[0]) for card in player_hand
                      ]) > sum([int(card.split()[0]) for card in dealer_hand]):
                await interaction.followup.send("You win!")
                money *= 2
                await interaction.followup.send(
                    "Your money is now {}".format(money))
            else:
                await interaction.followup.send("You lose.")
            break
        else:
            await interaction.followup.send(
                "Please enter 'hit' or 'stand' or 'quit'.")


@bot.tree.command(name="steam_top_sales",
                  description="Check out the top games on sale on steam")
async def get_top_sales(interaction: discord.Interaction, limit: int = 5):
    """Get the top games on sale from Steam. Shows 5 by default"""
    url = "https://store.steampowered.com/search/?specials=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.select(".search_result_row")
    print(f"Top {limit} games on sale:\n")
    game_list = ""
    await interaction.response.send_message(f"Top {limit} games on sale:")

    for result in results[:limit]:
        if result.select_one(".title") is None:
            print("Skipping invalid result")
            continue
        title = result.select_one(".title").text.strip()
        discount = result.select_one(".search_discount span")
        price = result.select_one(".search_price_discount_combined")
        link = str(result["href"])

        price_text = price.text.strip().replace("\n", " ") if price else "N/A"

        game_list += f"{title}  Price: {price_text}\n  Link: {'<' + link + '>'}\n"
    await interaction.followup.send(game_list)

@bot.tree.command(name="anime_music", description="sends a PEAK song")
async def anime_music(interaction: discord.Interaction):
    anime_songs = [
        ""
    ]
    await interaction.response.send_message(random.choice(anime_songs))



@bot.tree.command(name="anime_trivia", description="Get a random anime trivia question!")
async def anime_trivia(interaction: discord.Interaction):
    url = "https://opentdb.com/api.php?amount=10&category=31"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json() # api returns a json object

    if data["response_code"] != 0 or not data["results"]:
        return await interaction.response.send_message(
            "ERROR: Couldn't fetch trivia question. Please try again later.",
            ephemeral=True
        )

    question_data = random.choice(data["results"])

    question = html.unescape(question_data["question"])
    correct = html.unescape(question_data["correct_answer"])
    incorrect = [html.unescape(a) for a in question_data["incorrect_answers"]]

    answers = incorrect + [correct]
    random.shuffle(answers)

    embed = discord.Embed(
        title="Anime Trivia",
        description=question,
        color=discord.Color.blurple()
    )

    for i, answer in enumerate(answers, start=1):
        embed.add_field(name=f"{chr(64+i)}", value=answer, inline=False)

    embed.set_footer(text="Answer will be revealed in 30 seconds. Enter the option number in chat.")


    await interaction.response.send_message(embed=embed)
    # wait for 30 seconds before revealing the answer


@bot.tree.command(name="news", description="Get the latest news headlines from a reliable source")
async def news(interaction: discord.Interaction):
    await interaction.response.send_message("Here are the latest news headlines: ")


@bot.tree.command(name="truth_or_dare",
                  description="I tried to keep it family friendly i promise")
async def truth_or_dare(interaction: discord.Interaction):
    truths = [
        "What's the weirdest thing you've ever eaten?",
        "What's your least favorite anime",
        "What's your favorite song?",
        "Have you ever lied to get out of trouble?",
        "What's something you've never told anyone?"
        "What's the most embarrassing thing that has happened to you?",
        "If you were stranded on an island whats the first thing you'd do?",
        "What is the bordest you've ever been?",
        "What is your opinion on the current president?",
        "What is the dumbest / most cringy thing you've ever said?",
        "If you could only eat one food for the rest of your life what would it be?",
        "Do you prefer hot or cold showers?",
        "What is the worst movie you have ever seen?",
    ]
    dares = [
        "Tell a joke. NOW!",
        "Sing the intro to through the fire and flames",
        "Lick peanut butter off your elbow",
        "DM a random person and talk in brainrot",
        "Play clone hero at 200% speed blindfolded",
        "Play minecraft with your feet for 10 minutes",
        "take a drink every time carney jared says something crazy on his latest stream",
        "Do pushups and say david every time you do one",
        "take a shot of a carbonated drink. All of it god dammit",
        "sing the national anthem",
        "sing the alphabet backwards",
        "do your best miku impression"
        "pick a random person and say their name in a french accent",
    ]
    await interaction.response.send_message("Truth or Dare?")
    response = await bot.wait_for(
        'message', check=lambda message: message.author == interaction.user)
    if response.content.lower() == 'truth':
        await interaction.followup.send(random.choice(truths))
        return
    elif response.content.lower() == 'dare':
        await interaction.followup.send(random.choice(dares))
        return


@bot.tree.command(name="tic_tac_toe_h",
                  description="Play tic tac toe with a friend")
async def tic_tac_toe_h(interaction: discord.Interaction,
                        player2: discord.Member):
    turn = 0
    board = [
        ":white_large_square:", ":white_large_square:", ":white_large_square:",
        ":white_large_square:", ":white_large_square:", ":white_large_square:",
        ":white_large_square:", ":white_large_square:", ":white_large_square:"
    ]
    await interaction.response.send_message(
        f"{player2} Do you accept to play tic tac toe? Y/N")
    response = await bot.wait_for(
        'message', check=lambda message: message.author == player2)
    if response.content.lower() == 'y':
        await interaction.followup.send("Player 1 is X and Player 2 is O")
        await interaction.followup.send(f"Player {turn+1}'s turn")
        await interaction.followup.send(board[0] + board[1] + board[2] + "\n" +
                                        board[3] + board[4] + board[5] + "\n" +
                                        board[6] + board[7] + board[8])
        while turn != 2:
            response = await bot.wait_for(
                'message',
                check=lambda message: message.author == interaction.user or
                message.author == player2)
            if type(int(response.content)) is int:
                board[int(response.content)] = ":x:" if turn == 0 else ":o:"
                turn = 1 if turn == 0 else 0
                await interaction.followup.send(f"Player {turn+1}'s turn")
                await interaction.followup.send(board[0] + board[1] +
                                                board[2] + "\n" + board[3] +
                                                board[4] + board[5] + "\n" +
                                                board[6] + board[7] + board[8])
            elif response.content.lower() == 'quit':
                await interaction.followup.send("Game ended")
                turn = 2
                break
            else:
                await interaction.followup.send(
                    "Please enter a number between 0 and 8")
                continue

    else:
        return
    return


@bot.tree.command(name="hangman",
                  description="Play hangman with questionable words")
async def hangman(interaction: discord.Interaction):
    if not interaction.channel:
        return
    if interaction.channel.id in games:
        await interaction.followup.send(
            "A game is already running in this channel moron.")
        return
    await interaction.response.send_message(
        "Starting hangman. Use /guess <letter> to guess a letter.")
    word = random.choice(WORDS)
    display = ["_"] * len(word)
    guesses = []
    attempts = 6

    games[interaction.channel.id] = {
        "word": word,
        "display": display,
        "guesses": guesses,
        "attempts": attempts
    }

    await interaction.followup.send(
        f"Hangman started. Word: `{' '.join(display)}`\n"
        f"Guess a letter using `!guess <letter>`")


@bot.tree.command(name="guess", description="Guess a letter in the hangman game")
async def guess(interaction: discord.Interaction, letter: str):
    game = games.get(interaction.channel.id)
    if not game:
        await interaction.response.send_message(
            "No hangman game is running. Start one with `/hangman`.",
            ephemeral=True)
        return
    letter = letter.lower()
    if letter in game["guesses"]:
        await interaction.followup.send(f"You already guessed `{letter}`!")
        return
    game["guesses"].append(letter)
    if letter in game["word"]:
        for i, l in enumerate(game["word"]):
            if l == letter:
                game["display"][i] = letter
        await interaction.followup.send(f"✅ Correct. `{' '.join(game['display'])}`")
    else:
        game["attempts"] -= 1
        await interaction.followup.send(
            f"❌  `{letter}` isn't in the word. Attempts left: {game['attempts']}"
        )
    if "_" not in game["display"]:
        await interaction.followup.send(f":check: Correct. The word was `{game['word']}`.")
        del games[interaction.channel.id]
    elif game["attempts"] <= 0:
        await interaction.followup.send(f" Game over. The word was `{game['word']}`.")
        del games[interaction.channel.id]

@bot.tree.command(name="joke", description="Get a shitty deplorable joke")
async def dad_joke(interaction: discord.Interaction):
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    joke = response.json()["joke"]
    await interaction.response.send_message(joke)


@bot.tree.command(
    name="elon_musk_twitter",
    description=
    "See the crazy ravings of elon musk. I'm not responsible for your sanity")
async def elon_musk_twitter(interaction: discord.Interaction):
    await interaction.response.send_message("https://twitter.com/elonmusk")


@bot.tree.command(name="goon", description="don't enter this command. PLEASE")
async def goon(interaction: discord.Interaction):
    await interaction.response.send_message(
        "FREAK AHH WHY WOULD YOU ENTER THIS COMMAND")
    await interaction.followup.send(
        "https://tenor.com/view/benjammins-gooner-goon-what-a-gooner-simp-gif-6065693207482219935"
    )


# === GeoGuess ===
# rarley do i comment code but this is hard to read
def get_random_coordinate():
    lat = round(random.uniform(-60, 85), 6)
    lon = round(random.uniform(-180, 180), 6)
    return lat, lon

def get_osm_map_url(lat, lon, zoom=15, size="800x600"):
    return f"https://staticmap.openstreetmap.de/staticmap.php?center={lat},{lon}&zoom={zoom}&size={size}"



@bot.tree.command(
    name="meme",
    description=
    "Get a random meme from reddit, May or may not be cringe or nsfw")
async def meme(interaction: discord.Interaction):
    url = "https://meme-api.com/gimme"
    response = requests.get(url)
    data = response.json()
    await interaction.response.send_message(data["url"])
    await interaction.followup.send(data["title"] + "" + (data["author"]))


@bot.tree.command(
    name="bible",
    description="Let the goon preach to you. Get a random Bible verse.")
async def bible(interaction: discord.Interaction):
    chance = random.randint(1, 100)
    if chance % 99 == 0:
        await interaction.response.send_message(
            "And den a jesussss tiurned de watah into MOONSHINNEEEE")
        return
    chance2 = random.randint(1, 200)
    if chance2 == 1:
        await interaction.response.send_message(
            "Goon 10:23 ling gan guli guli ling wa")
    verse = random.choice(verses)
    url = f"https://bible-api.com/{verse.replace(' ', '%20')}"

    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                message = f"**{data['reference']}**\n{data['text']}"
                await interaction.followup.send(
                    message.replace("Yahweh", "God"))
            else:
                await interaction.followup.send(
                    "Failed to fetch the verse. Try again later.")


@bot.tree.command(name="flag", description="Get a random flag from the world")
async def flag(interaction: discord.Interaction):
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,flags"
    response = requests.get(url)
    data = response.json()
    country = random.choice(data)
    try:
        await interaction.response.send_message(country["flags"]["png"])
        await interaction.followup.send(country["name"]["common"])
        await interaction.followup.send(country["capital"][0])
    except Exception as e:
        print(e)


@bot.tree.command(name="vc_join", description="Bot joins your vc")
async def join(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.followup.send( "This command can only be used in a server.")
        return
    if not interaction.user.voice:
        await interaction.followup.send("You must be in a voice channel!" )
        return
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if vc:
        await interaction.followup.send( "I'm already connected to a voice channel.")
        return
    vc = await channel.connect()  # STORE IT 
    await interaction.followup.send(f"Joined {channel.name}")



@bot.tree.command(name="vc_leave", description="Bot leaves your vc")
async def leave(interaction:discord.Interaction):
    return

@bot.tree.command(
    name="degoon",
    description="deletes the last n messages in the channel sent by the goon")
async def degoon(interaction: discord.Interaction, amount: int):
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "This command can only be used in a text channel.")
        return

    await interaction.response.defer()
    deleted = await interaction.channel.purge(
        limit=amount+1, check=lambda m: m.author == bot.user)
    await interaction.followup.send(f"Deleted {len(deleted)} messages.")


@bot.tree.command(name="trivia", description="Get a random trivia question!")
async def trivia(interaction: discord.Interaction):
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url).json()

    if response["response_code"] != 0:
        await interaction.response.send_message("ERROR: Failed to fetch a trivia question.", ephemeral=True)
        return

    data = response["results"][0]

    question = html.unescape(data["question"])
    correct = html.unescape(data["correct_answer"])
    incorrect = [html.unescape(ans) for ans in data["incorrect_answers"]]

    choices = incorrect + [correct]
    random.shuffle(choices)

    choice_text = "\n".join(f"{chr(65+i)}. {choice}" for i, choice in enumerate(choices))

    embed = discord.Embed(
        title="QUIZZYPOO TIME!",
        description=f"**{question}**\n\n{choice_text}",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Answer will be revealed in 30 seconds. Enter the letter of your choice in chat.")

    await interaction.response.send_message(embed=embed)

# make matching game here

@bot.tree.command(name="shrimp", description="Is that shit real man")
async def shrimp(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://img.ifunny.co/images/9c52b138d1ebf767b59aba505dd66e1d0790a5146b306e63ca4e0a5b5f85cb84_1.jpg"
    )


# MONEY COMMANDS

@bot.tree.command(name="wallet",
                  description="See how many goon points you have")
async def wallet(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server.")
        return

    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    points = read_points(server_id)

    # If user not in points, initialize them
    if user_id not in points:
        points[user_id] = 0
        write_points(server_id, points)
    user_points = points[user_id]
    await interaction.response.send_message(
        f"🪙You have {user_points} goon points. These will replace the dollar trust me")

@bot.tree.command(name="beat",description="Beat someone up and take their goon points. Or get arrested.")
async def beat(interaction: discord.Interaction):
    person = random_user() # random person
    result = random.randint(1, 10)
    if result == 5:
        money = random.randint(100, 200)
        await interaction.response.send_message(f"You beat up {person} and got {money} goon points. The goon approves 👍")
    else:
        await interaction.response.send_message("lol why would you beat someone up for goon points")
    
@bot.tree.command(name="fight", description="See if you can battle against ME THE GOON")
async def fight(interaction: discord.Interaction):
    pass

@bot.tree.command(name="give",
                  description="Give goon points to someone. Admins only")
@app_commands.checks.has_permissions(administrator=True)
async def give(interaction: discord.Interaction, user: discord.Member,
               amount: int):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server.")
        return
    write_points(str(interaction.guild.id), {str(user.id), amount})
    await interaction.response.send_message("Gave goon points to user")

@bot.tree.command(name="store", description="View the goon point store where u can buy totally non scam items and maybe some cool stuff")
async def store(interaction: discord.Interaction):
    store_items = {
        "1. Poo Stick": 400,
        "2. Bronze Halbred": 700,
        "3. Berserk Longsword": 1200,
        "4. Daggers of Thors": 2800,
        "5. Murasama Katana": 5000,
        "6. Golden Turd": 10000,
        "7. Zangetsu: ":15000,
        "8. Spear of Longinus": 20000,
        "9. Positron Rifle": 30000,
        "A. Goon Membership": 10000,
        "B. Supreme Gooner Role": 50000,
        "C. Ultimate Freak Role": 200000,
        "D. Luffy's Straw Hat": 67676767,
        "E. The One Piece": 9999999999,
    }
    store_message = "🪙 **Goon Point Store** 🪙\n Here you can buy RPG weapons and items that will get you pulled aside by TSA\n\n"
    for item, price in store_items.items():
        store_message += f"{item}: {price} goon points\n"
    await interaction.response.send_message(store_message)

# random stuff

@bot.tree.command(name="suprise", description="Ba da ba ba ba david")
async def suprise(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://www.youtube.com/watch?v=Y5OXryKC1SA")


@bot.tree.command(name="omni", description="We can be bees!")
async def omni(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://tenor.com/view/omni-gyatt-gif-17689339150837030890")
    
    
@bot.tree.command(name="gif", description="completley random gif from tenor")
async def gif(interaction: discord.Interaction):
    pass
    

@bot.tree.command(name="cat", description="random cat gif from tenor")
async def cat(interaction: discord.Interaction):
    cats = [
        "https://tenor.com/view/cat-gif-16258174987336597266",
        "https://tenor.com/view/cat-cat-with-tongue-cat-smiling-gif-11949735780193730026",
        "https://tenor.com/view/silly-reaction-meme-stan-twitter-funny-stressed-gif-7713976294327515532"
    ]
    await interaction.response.send_message(random.choice(cats))


@bot.tree.command(name="info", description="Actual info trust me bro")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"=== THE GOON ===\n\n a discord bot made by Inexplicable768 (alex). \n version: {version}\nI didnt know i had to put that there"
    )

@bot.tree.command(name="calculator", description="Evaluate an expression")
async def calculator(interaction: discord.Interaction, expression: str):
    if len(str(expression)) > 50: # very basic way of making sure harmful code isnt executed. 
                                  # Im not really worried about vulnerabilities given this is only used by friends that dont know much about code
        return
    answer = eval(expression)
    await interaction.response.send_message(answer)

# IMAGE GENERATION COMMANDS - The user supplies an image over discord and the bot returns a modified image

async def return_image(interaction: discord.Interaction, image: Image.Image):
    with io.BytesIO() as image_binary:
        image.save(image_binary, format="PNG")
        image_binary.seek(0)

        # If you've already responded, use followup
        if interaction.response.is_done():
            await interaction.followup.send(
                file=discord.File(fp=image_binary, filename="image.png")
            )
        else:
            await interaction.response.send_message(
                file=discord.File(fp=image_binary, filename="image.png")
            )


@bot.tree.command(name="img_invert", description="Inverts the colors of an image")
async def invert_image(interaction: discord.Interaction, image: discord.Attachment):
    await interaction.response.defer()
    image_bytes = await image.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inverted_image = ImageOps.invert(image_pil)
    await return_image(interaction, inverted_image)


@bot.tree.command(name="img_greyscale", description="Grayscales an image")
async def greyscale_image(interaction: discord.Interaction, image: discord.Attachment):
    await interaction.response.defer()
    image_bytes = await image.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    greyscaled = ImageOps.grayscale(image_pil)
    await return_image(interaction, greyscaled)


@bot.tree.command(name="img_contrast", description="Change the contrast of an image")
async def img_contrast(
    interaction: discord.Interaction,
    image: discord.Attachment,
    contrast_lvl: float = 2.0
):
    await interaction.response.defer()
    image_bytes = await image.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    contrast = ImageEnhance.Contrast(image_pil).enhance(contrast_lvl)
    await return_image(interaction, contrast)

@bot.tree.command(name="img_sharpen", description="Sharpens an image")
async def img_sharpen(
    interaction: discord.Interaction,
    image: discord.Attachment,
    sharplvl: int
):
    await interaction.response.defer()
    image_bytes = await image.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    sharp = ImageEnhance.Contrast(image_pil).enhance(sharplvl)
    await return_image(interaction, sharp)


@bot.tree.command(name="img_deepfry", description="Deepfries an image")
async def fry_image(
    interaction: discord.Interaction,
    image: discord.Attachment,
    fry_level: int = 3
):
    await interaction.response.defer()
    fry_level = max(1, min(fry_level, 10))  # clamp fry level

    image_bytes = await image.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Over-enhance image
    img = ImageEnhance.Color(img).enhance(2.5 + fry_level)
    img = ImageEnhance.Contrast(img).enhance(2.0 + fry_level * 0.5)
    img = ImageEnhance.Sharpness(img).enhance(3.0 + fry_level)

    # Add random noise (safe divisor)

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    # Heavy JPEG compression
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=5, subsampling=2)
    buffer.seek(0)

    img = Image.open(buffer).convert("RGB")
    img.load()

    await return_image(interaction, img)


@bot.tree.command(name="img_blur", description="blurs an image")
async def img_blur(interaction: discord.Interaction, image: discord.Attachment, blur_level: int):
    await interaction.response.defer()
    image_bytes = await image.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_level))
    await return_image(interaction, img)


@bot.tree.command(name="img_caption", description="Adds a caption as a top banner on an image")
async def img_caption(
    interaction: discord.Interaction,
    image: discord.Attachment,
    caption: str
):
    await interaction.response.defer()

    # Read image bytes and open with PIL
    image_bytes = await image.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    draw = ImageDraw.Draw(img)
    font_size = max(20, img.width // 15)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Measure text size
    text_bbox = draw.textbbox((0, 0), caption, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    padding = 10
    banner_height = text_height + padding * 2

    # Draw white banner rectangle at the top
    draw.rectangle([(0, 0), (img.width, banner_height)], fill="white")

    # Center text horizontally, vertically in the banner
    x = (img.width - text_width) / 2
    y = padding

    # Draw black text
    draw.text((x, y), caption, font=font, fill="black")

    # Save image to bytes
    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        await interaction.followup.send(file=discord.File(fp=image_binary, filename="captioned.png"))


## END IMAGE GENERATION
            
@bot.tree.command(name="therapy", description="Feeling down? Let the bot counsel you")
async def therapy(
    interaction: discord.Interaction   
):
    await interaction.response.send_message("Its ok brotato. You're in the arms of the goon")

@bot.tree.command(name="music", description="Get a random song from my playlist of bangers")
async def music(
    interaction: discord.Interaction
):
    playlist_id = "spotify:playlist:YOUR_PLAYLIST_ID"  # replace with your playlist URI

    # Get all tracks in the playlist
    results = sp.playlist_items(playlist_id)
    tracks = results['items']

    # If the playlist is large, fetch next pages
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    # Extract track names
    track_names = [track['track']['name'] for track in tracks]

# DND dice simulation commands 
@bot.tree.command(name="d4", description="Rolls a d4")
async def d4(
    interaction: discord.Interaction
):
    result = random.randint(1, 4)
    await interaction.response.send_message(f"d4 rolls: {result}")

@bot.tree.command(name="d6", description="Rolls a d6")
async def d6(interaction: discord.Interaction):
    result = random.randint(1, 6)
    await interaction.response.send_message(f"d6 rolls: {result}")

@bot.tree.command(name="d8", description="Rolls a d8")
async def d8(interaction: discord.Interaction):
    result = random.randint(1, 8)
    await interaction.response.send_message(f"d8 rolls: {result}")

@bot.tree.command(name="d10", description="Rolls a d10")
async def d10(interaction: discord.Interaction):
    result = random.randint(1, 10)
    await interaction.response.send_message(f"d10 rolls: {result}")

@bot.tree.command(name="d20", description="Rolls a d20")
async def d20(interaction: discord.Interaction):
    result = random.randint(1, 20)
    await interaction.response.send_message(f"d20 rolls: {result}")

@bot.tree.command(name="help", description="List all commands")
async def help_command(interaction: discord.Interaction):
    command_list = ""
    for command in await bot.tree.fetch_commands(): 
        command_list += f"/{command.name}: {command.description}\n"
    if not command_list:
        command_list = "No commands found!"
    await interaction.response.send_message(f"**Available Commands:**\n{command_list}\n")


# === Errors ===


@give.error
async def give_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You must be an administrator to use this command.",
            ephemeral=True)


@gpurge.error
async def give_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You must be an administrator to use this command.",
            ephemeral=True)


# === Start Bot ===
if __name__ == "__main__":
    try:
        token = os.getenv("TOKEN") or ""
        if not token:
            raise ValueError("Missing TOKEN environment variable.")
        bot.run(token)
    except Exception as e:
        print("Bot failed to start:", e)
