import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import random
import aiohttp
import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=":3", intents=intents, help_command=None)

ffmpeg_path = 'E:\\Users\\atomi\\Downloads\\ffmpeg-master-latest-win64-gpl\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'

# List to track jailed users
jailed_users = []

# Jail command
@bot.command(name="jail", help="Send a user to jail")
async def jail(ctx, user: discord.Member):
    if user.id not in jailed_users:
        jailed_users.append(user.id)
        await ctx.send(f"{user.mention} has been jailed!")
    else:
        await ctx.send(f"{user.mention} is already in jail!")

# Release command to free jailed users
@bot.command(name="release", help="Release a user from jail")
async def release(ctx, user: discord.Member):
    if user.id in jailed_users:
        jailed_users.remove(user.id)
        await ctx.send(f"{user.mention} has been released from jail!")
    else:
        await ctx.send(f"{user.mention} is not in jail.")

# Event listener to reply "jail!" to jailed users
@bot.event
async def on_message(message):
    if message.author.id in jailed_users:
        await message.channel.send("jail!")
    
    await bot.process_commands(message)

# Function to check if the bot is already playing a song
def is_playing(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_playing()

# Command to join a voice channel
@bot.command(name="join", help="Joins a voice channel")
@commands.cooldown(1, 5, commands.BucketType.user)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            await channel.connect()
        else:
            await ctx.send("I'm already here, silly!")
    else:
        await ctx.send("You gotta be in a voice channel for me to join, ya know!")

# Command to leave a voice channel
@bot.command(name="leave", help="Leaves the voice channel")
@commands.cooldown(1, 5, commands.BucketType.user)
async def leave(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Toodles! Bye bye!")
    else:
        await ctx.send("I'm not in a voice channel, silly!")

# Command to play music from YouTube
@bot.command(name="play", help="Plays a YouTube URL or searches for a song")
@commands.cooldown(1, 5, commands.BucketType.user)
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("You gotta be in a voice channel to play music!")
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        await ctx.invoke(join)
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client is None:
            await ctx.send("Couldn't join the voice channel. Boo hoo!")
            return

    if is_playing(ctx):
        await ctx.send("I'm already playing a tune! Use :3stop to stop it.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                video = info['entries'][0]
                url = video['url']
                title = video.get('title', 'Unknown title')
            else:
                url = info['url']
                title = info.get('title', 'Unknown title')

            ffmpeg_options = {
                'options': '-vn',
                'executable': ffmpeg_path
            }
            voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
            await ctx.send(f"Now playing: {title}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Command to stop playing music
@bot.command(name="stop", help="Stops the current song")
@commands.cooldown(1, 5, commands.BucketType.user)
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Music stopped. Silence is golden!")
    else:
        await ctx.send("No music is playing right now, silly!")

# Rock-paper-scissors command with cooldown
@bot.command(name="rps", help="Play rock-paper-scissors with the bot")
@commands.cooldown(1, 5, commands.BucketType.user)
async def rps(ctx, choice: str):
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)

    if choice.lower() not in choices:
        await ctx.send("That's not a valid choice! Pick rock, paper, or scissors.")
        return

    if choice.lower() == bot_choice:
        await ctx.send(f"We both chose {bot_choice}. It's a tie! Woohoo!")
    elif (choice.lower() == 'rock' and bot_choice == 'scissors') or \
         (choice.lower() == 'paper' and bot_choice == 'rock') or \
         (choice.lower() == 'scissors' and bot_choice == 'paper'):
        await ctx.send(f"You chose {choice}. I chose {bot_choice}. You win! Yay!")
    else:
        await ctx.send(f"You chose {choice}. I chose {bot_choice}. I win! Better luck next time!")

# Beatbox command
@bot.command(name="oribeatbox", help="Send random beatbox sounds")
@commands.cooldown(1, 5, commands.BucketType.user)
async def oribeatbox(ctx):
    beatbox_sounds = ["Boom bap", "Pshh pshh", "Chk chk", "Tsss"]
    await ctx.send(random.choice(beatbox_sounds))

# Kiss command with randomized anime gifs
@bot.command(name="kiss", help="Send a kiss gif to a user")
async def kiss(ctx, user: discord.Member):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.giphy.com/v1/gifs/search", params={"api_key": "v68IkrsO991Ol3MhnRTcSOlEEvLpQUDO", "q": "anime kiss", "limit": 50}) as resp:
            data = await resp.json()
            gif_url = random.choice(data["data"])["images"]["original"]["url"]
            await ctx.send(f"{ctx.author.mention} gives {user.mention} a big kiss! {gif_url}")

# Kill command with randomized anime gifs
@bot.command(name="kill", help="Send a kill gif to a user")
async def kill(ctx, user: discord.Member):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.giphy.com/v1/gifs/search", params={"api_key": "v68IkrsO991Ol3MhnRTcSOlEEvLpQUDO", "q": "anime kill", "limit": 50}) as resp:
            data = await resp.json()
            gif_url = random.choice(data["data"])["images"]["original"]["url"]
            await ctx.send(f"{ctx.author.mention} kills {user.mention}! {gif_url}")

# Hug command with randomized anime gifs
@bot.command(name="hug", help="Send a hug gif to a user")
async def hug(ctx, user: discord.Member):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.giphy.com/v1/gifs/search", params={"api_key": "v68IkrsO991Ol3MhnRTcSOlEEvLpQUDO", "q": "anime hug", "limit": 50}) as resp:
            data = await resp.json()
            gif_url = random.choice(data["data"])["images"]["original"]["url"]
            await ctx.send(f"{ctx.author.mention} gives {user.mention} a big hug! {gif_url}")

# Command to search for a username
@bot.command(name="orifind", help="Search for a username on the internet")
@commands.cooldown(1, 60, commands.BucketType.user)
async def orifind(ctx, username: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.social-searcher.com/v2/search?q={username}&network=all&key=847ac83b683091cc3a64c5528752c12e") as resp:
            data = await resp.json()
            if data["posts"]:
                embed = discord.Embed(title=f"Results for {username}", color=discord.Color.blue())
                for post in data["posts"]:
                    embed.add_field(name=post["network"], value=post["url"], inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Couldn't find anything for {username}... They're a sneaky one!")

# Bot shutdown command
@bot.command(name="orishutdown", help="Shut down the bot")
@commands.is_owner()
async def orishutdown(ctx):
    await ctx.send("Goodnight! *shuts down*")
    await bot.close()

# Help command
@bot.command(name="helpme", help="Show help information")
async def helpme(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.green())
    embed.add_field(name=":3jail @user", value="Send a user to jail.", inline=False)
    embed.add_field(name=":3release @user", value="Release a user from jail.", inline=False)
    embed.add_field(name=":3play [song]", value="Play a song or search for one.", inline=False)
    embed.add_field(name=":3stop", value="Stop the current song.", inline=False)
    embed.add_field(name=":3join", value="Join a voice channel.", inline=False)
    embed.add_field(name=":3leave", value="Leave a voice channel.", inline=False)
    embed.add_field(name=":3rps [choice]", value="Play rock-paper-scissors.", inline=False)
    embed.add_field(name=":3oribeatbox", value="Send random beatbox sounds.", inline=False)
    embed.add_field(name=":3kiss @user", value="Send a kiss gif.", inline=False)
    embed.add_field(name=":3kill @user", value="Send a kill gif.", inline=False)
    embed.add_field(name=":3hug @user", value="Send a hug gif.", inline=False)
    embed.add_field(name=":3orifind [username]", value="Search for a username on the internet.", inline=False)
    embed.add_field(name=":3orishutdown", value="Shut down the bot.", inline=False)
    await ctx.send(embed=embed)

bot.run("MTI1OTA4NTk4NjUwNDM4MDQyNg.GguFTa.U42cy0x-MZuJ8t5DKMw6NOli0dZAzSWKRKGGyU")



