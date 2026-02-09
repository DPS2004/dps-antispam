import configparser
import os
import discord

configExample = configparser.ConfigParser()

configExample['DISCORD'] = {
    'token' : 'abcdefghijklmnopqrstuvwxyz0123456789',
    'logChannel' : '1234567890',
    'trustedRole' : 'trusted',
    'untrustedRole' : 'untrusted',
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


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(config['DISCORD']['token'])