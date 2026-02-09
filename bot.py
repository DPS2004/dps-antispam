import os
import io
import datetime
import asyncio

import configparser

import discord
from discord.ext import commands
from discord import app_commands

from PIL import Image
import imagehash

configExample = configparser.ConfigParser()

configExample['DISCORD'] = {
    'token' : 'abcdefghijklmnopqrstuvwxyz0123456789',
    'logChannel' : '1234567890',
    'trustedRole' : 'trusted',
    'untrustedRole' : 'untrusted',
    'guild' : '1234567890'
}
configExample['SETTINGS'] = {
    'distance': '1000'
}

with open('example.ini', 'w') as configfile:
    configExample.write(configfile)

if not os.path.isfile('config.ini'):
    raise FileNotFoundError("config.ini not found, create it from example.ini")

config = configparser.ConfigParser()
config.read(['example.ini','config.ini'])

###image matching###
hashes = []
imageList = os.scandir("spamImages")
for image in imageList:
    h = imagehash.phash(Image.open(image.path),hash_size=64)
    #print(image.path, h)
    hashes.append({"h": h,"path": image.path})
    #print(hashes[len(hashes)-1])

def getClosest(targetHash):
    closestDistance = 99999
    closestFilename = ""
    for i in hashes:
        distance = abs(i['h']-targetHash)
        if(distance < closestDistance):
            closestDistance = distance
            closestFilename = i['path']
    return closestDistance, closestFilename
    

###discord###
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)
#client = commands.Bot(command_prefix='$', intents=intents)
tree = app_commands.CommandTree(client)

botGuild = None
if 'guild' in config['DISCORD']:
    botGuild=discord.Object(id=config['DISCORD']['guild'])
    print('using guild')
else:
    print("no guild specified")
    
    
async def trust(message):
    await message.author.add_roles(message.guild.get_role(int(config['DISCORD']['trustedRole'])))

async def purgeChannel(message,channel,time):
    #print("started channel " + channel.name)
    async for m in channel.history(limit=20):
        if m.author == message.author:
            await m.delete()
            print("deleted message in " + channel.name)
    #print("ok done with " + channel.name)
    
async def purge(message):
    time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    for channel in message.guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.permissions_for(message.guild.me).view_channel:
            asyncio.create_task(purgeChannel(message,channel,time))
            #print(channel.name)
            #await purgeChannel(message,channel,time);

async def untrust(message, attachment, closestDistance, closestFilename):
    await message.author.add_roles(message.guild.get_role(int(config['DISCORD']['untrustedRole'])))
    referenceImage = discord.File(closestFilename)
    matchImage = await attachment.to_file()
    logChannel = message.guild.get_channel(int(config['DISCORD']['logChannel']))
    await logChannel.send("hey bozos i found a spammer probably?\n<@"+str(message.author.id)+">\ndistance: " + str(closestDistance) + " (threshold is " + config['SETTINGS']['distance'] + ")\nmatched filename: " + closestFilename + "\nchannel: " + message.channel.name,files = [matchImage,referenceImage])
    await purge(message)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(await tree.sync(guild=botGuild))
    print("synced commands")


@client.event
async def on_message(message):
    if (not message.guild) or message.author == client.user:
        return
    if message.author.get_role(int(config['DISCORD']['trustedRole'])):
        return
    if message.author.get_role(int(config['DISCORD']['untrustedRole'])):
        print('untrusted user sent a message??? something is wrong.')
        #return
    print("checking out new user's message.")
    
    
    if not message.attachments:
        print("no attachments, probably a ok!")
        await trust(message)
    print("message has attachments")
    for attachment in message.attachments:
        # Save the attachment to a local file
        file = io.BytesIO()
        await attachment.save(file)
        image = Image.open(file)
        ##image.show()
        targetHash = imagehash.phash(image,hash_size=64)
        closestDistance, closestFilename = getClosest(targetHash)
        print(closestDistance, closestFilename)
        image.close()
        file.close()
        if closestDistance < int(config['SETTINGS']['distance']):
            print("found a match!!!")
            await untrust(message,attachment,closestDistance, closestFilename)
            return
    
    if not message.author.get_role(int(config['DISCORD']['untrustedRole'])):
        print("checked attachments, no match found")
        await trust(message)


"""
@tree.command(name="ping", description="test command",guild = botGuild)
async def _ping(interaction) -> None:
    await interaction.response.send_message("awerwaerawreegeuirgheiurg!")
"""

client.run(config['DISCORD']['token'])