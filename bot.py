# DISCORD
import discord
from discord import app_commands
from discord import Interaction

# ML MODELS
from models.correctional import correctional_predicts
from models.sentimental import sentimentally_negative_predicts

# FIREBASE
import firebase_admin
from firebase_admin import db

# ETC
from collections import defaultdict
from dotenv import load_dotenv
import os

# LOAD ENV
load_dotenv()

# BOT SETTINGS
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# FIREBASE SETUP
cred = firebase_admin.credentials.Certificate(os.getenv("PATH_TO_FIREBASE_SECRET"))
rd = firebase_admin.initialize_app(cred, {
	"databaseURL": "https://nerd-bot-840c1-default-rtdb.firebaseio.com/"
})
nerding_list = db.reference("/nerding_list")

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
    try:
        nerding_list.child(f"{str(interaction.guild.id)}/{str(interaction.user.id)}").update({
            "nerd": True
        })
        embed = discord.Embed(title="Success", description=f"{interaction.user.mention} has been added to the nerding list in {interaction.guild.name}", color=0x00ff00)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"Try again or submit a ticket (to @soondae for now).\nError: {str(e)}", color=0xff0000)
    finally:
        await interaction.response.send_message(embed=embed, ephemeral=True)
# remove_nerd
# Removes a user from being nerded
@tree.command(
    name="remove_nerd",
    description="Removes this user from being nerded"
)
async def remove_nerd(interaction):
    try:
        nerding_list.child(f"{str(interaction.guild.id)}/{str(interaction.user.id)}").update({
            "nerd": False
        })
        embed = discord.Embed(title="Success", description=f"{interaction.user.mention} has been removed from the nerding list in {interaction.guild.name}", color=0x00ff00)
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"Try again or submit a ticket (to @soondae for now).\nError: {str(e)}", color=0xff0000)
    finally:
        await interaction.response.send_message(embed=embed, ephemeral=True)

# get_invite_link
# Sends the invite link of this bot
@tree.command(
    name="get_invite_link",
    description="Sends the invite link of this bot"
)
async def get_invite_link(interaction: Interaction):
    await interaction.response.send_message(f"https://discord.com/api/oauth2/authorize?client_id=1191957746795425823&permissions=8&scope=bot+applications.commands", ephemeral=True)

# Reading messages
@client.event
async def on_message(message: discord.Message):
    if not message.guild:
        return
    snapshot = nerding_list.child(f"{str(message.guild.id)}/{str(message.author.id)}/nerd").get()
    nerd_authorized = snapshot if snapshot is not None else False
    correctional_and_negative = correctional_predicts(message.content) and sentimentally_negative_predicts(message.content)
    if nerd_authorized and correctional_and_negative:
        await message.add_reaction("🤓")

client.run(os.getenv("DISCORD_BOT_TOKEN"))