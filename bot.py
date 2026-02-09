import configparser
import os
import discord
from discord.ext import commands
from discord import app_commands

configExample = configparser.ConfigParser()

configExample['DISCORD'] = {
    'token' : 'abcdefghijklmnopqrstuvwxyz0123456789',
    'logChannel' : '1234567890',
    'trustedRole' : 'trusted',
    'untrustedRole' : 'untrusted',
    'guild' : '1234567890'
}

with open('example.ini', 'w') as configfile:
    configExample.write(configfile)

if not os.path.isfile('config.ini'):
    raise FileNotFoundError("config.ini not found, create it from example.ini")

config = configparser.ConfigParser()
config.read(['example.ini','config.ini'])


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

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(await tree.sync(guild=botGuild))
    print("synced commands")


@client.event
async def on_message(message):
    
    if message.author == client.user:
        return
    if message.author.get_role(int(config['DISCORD']['trustedRole'])):
        return
    if message.author.get_role(int(config['DISCORD']['untrustedRole'])):
        print('untrusted user sent a message??? something is wrong.')
        return
    print("checking out new user's message.")




@tree.command(name="ping", description="test command",guild = botGuild)
async def _ping(interaction) -> None:
    await interaction.response.send_message("awerwaerawreegeuirgheiurg!")


client.run(config['DISCORD']['token'])