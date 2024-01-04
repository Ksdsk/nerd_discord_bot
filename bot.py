import discord
import os
from random import uniform
from discord import app_commands
from dotenv import load_dotenv
from collections import defaultdict
from transformers import pipeline
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import re
import nltk.corpus
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.tree import DecisionTreeClassifier

messages = pd.read_csv('data/correctional.csv')

vectorizer = TfidfVectorizer(
    lowercase = False,
    analyzer = "word"
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

nerding_list = defaultdict(lambda: set())
sentimental_classifier = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
    return_all_scores=True
)

nltk.download('stopwords')
nltk.download('wordnet')

stop = stopwords.words('english')
lemmatizer = WordNetLemmatizer()
vectorizer = TfidfVectorizer(
    lowercase = False,
    analyzer = "word"
)

data = []
for message in messages["text_snippet"].tolist():
    temp = message.lower()
    temp = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", temp)
    temp = " ".join([lemmatizer.lemmatize(word) for word in temp.split()])
    data.append(temp)
    
data_labels = messages["correctional"].tolist()
features = vectorizer.fit_transform(data)
features_nd = features.toarray()

X_train, X_test, y_train, y_test = train_test_split(
    features_nd,
    data_labels,
    train_size = 0.8
)

rf_model = DecisionTreeClassifier()
rf_model.fit(X=X_train, y=y_train)
y_pred = rf_model.predict(X=X_test)

def prepare_text(original: str):
    text = original.lower()
    text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
    text = " ".join([lemmatizer.lemmatize(word) for word in text.split()])
    return text

def correctional(text: str) -> bool:
    vectorized_text = vectorizer.transform([prepare_text(text)])
    if int(rf_model.predict(vectorized_text)[0]) == 0:
        return False
    else:
        return True

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
    if message.guild.id in nerding_list and message.author.id in nerding_list[message.guild.id]:
        if (correctional(message.content)):
            print(f"{message.author.id} said something correctional")
            if (sentimental_classifier(message.content)[0][2]['score'] >= 0.3):
                print(f"{message.author.id} said something negative")
                await message.add_reaction("🤓")
        else:
            print(f"{message.author.id} said {message.content}")
load_dotenv()

client.run(os.getenv("DISCORD_BOT_TOKEN"))
