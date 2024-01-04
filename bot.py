# DISCORD
import discord
from discord import app_commands

# ML MODELS
from models.correctional import correctional_predicts
from models.sentimental import sentimentally_negative_predicts

# ETC
from collections import defaultdict
from dotenv import load_dotenv
import os

# BOT SETTINGS
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

nerding_list = defaultdict(lambda: set())

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} activated!')

# add_nerd
# Adds a user to be nerded in future messages
@tree.command(
    name="add_nerd",
    description="Adds this user to be nerded in future messages"
)
async def add_nerd(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} has been added to the nerding list in {interaction.guild.name}", ephemeral=True)
    nerding_list[interaction.guild.id].add(interaction.user.id)

# remove_nerd
# Removes a user from being nerded
@tree.command(
    name="remove_nerd",
    description="Removes this user from being nerded"
)
async def remove_nerd(interaction):
    await interaction.response.send_message(f"{interaction.user.mention} has been removed from my nerding list in {interaction.guild.name}!", ephemeral=True)
    if interaction.user.id in nerding_list[interaction.guild.id]:
        nerding_list[interaction.guild.id].remove(interaction.user.id)

# get_invite_link
# Sends the invite link of this bot
@tree.command(
    name="get_invite_link",
    description="Sends the invite link of this bot"
)
async def get_invite_link(interaction):
    await interaction.response.send_message(f"https://discord.com/api/oauth2/authorize?client_id=1191957746795425823&permissions=8&scope=bot+applications.commands", ephemeral=True)

# Reading messages
@client.event
async def on_message(message: discord.Message):
    nerd_authorized = message.guild.id in nerding_list and message.author.id in nerding_list[message.guild.id]
    correctional_and_negative = correctional_predicts(message.content) and sentimentally_negative_predicts(message.content)
    if nerd_authorized and correctional_and_negative:
        await message.add_reaction("🤓")

load_dotenv()

client.run(os.getenv("DISCORD_BOT_TOKEN"))