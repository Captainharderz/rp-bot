import discord
from discord.ext import commands
import os
import json
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import datetime

# =======================
# CONFIGURATION DES INTENTS
# =======================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# =======================
# CRÉATION DU BOT
# =======================
bot = commands.Bot(command_prefix="!rp_", intents=intents)

# =======================
# FICHIERS JSON
# =======================
folder = os.path.dirname(os.path.abspath(__file__))
fichiers = ["permis.json", "vehicules.json"]

for f in fichiers:
    chemin = os.path.join(folder, f)
    if not os.path.exists(chemin):
        with open(chemin, "w") as file:
            json.dump({}, file, indent=4)
        print(f"✅ {f} créé automatiquement !")

PERMIS_FILE = os.path.join(folder, "permis.json")
VEHICULE_FILE = os.path.join(folder, "vehicules.json")

# =======================
# FONCTIONS UTILES
# =======================
def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# =======================
# BOT READY
# =======================
@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")

# =======================
# COMMANDES TEST
# =======================
@bot.command()
async def ping(ctx):
    await ctx.send("Pong ! Le bot fonctionne !")

# =======================
# PERMIS RP (JSON + IMAGE)
# =======================

# ADMIN → créer un permis (avec points)
@bot.command()
@commands.has_permissions(administrator=True)
async def createpermis(ctx, member: discord.Member):
    data = load_json(PERMIS_FILE)
    user_id = str(member.id)

    if user_id in data:
        await ctx.send(f"❌ {member.mention} a déjà un permis RP.")
        return

    data[user_id] = {"nom": member.name, "points": 12}
    save_json(PERMIS_FILE, data)
    await ctx.send(f"🎉 Permis RP créé pour {member.mention} avec **12 points**.")

# TOUS → voir son permis RP en image
@bot.command()
async def monpermis(ctx):
    user_id = str(ctx.author.id)
    data = load_json(PERMIS_FILE)

    if user_id not in data:
        await ctx.send("❌ Tu n'as pas de permis RP.")
        return

    # Génération du permis en image
    try:
        background = Image.open("fond_permis.png").convert("RGBA")
    except:
        await ctx.send("❌ Fond du permis introuvable !")
        return

    # Avatar Discord
    response = requests.get(ctx.author.avatar.url)
    avatar = Image.open(BytesIO(response.content)).resize((250, 250))
    background.paste(avatar, (60, 120))

    draw = ImageDraw.Draw(background)

    # Numéro RP unique
    numero = "RP-" + str(random.randint(100000, 999999))
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    font_path = "arial.ttf"
    font = ImageFont.truetype(font_path, 40)

    # Texte sur le permis
    draw.text((350, 150), f"Nom RP : {ctx.author.display_name}", fill="black", font=font)
    draw.text((350, 220), f"Numéro : {numero}", fill="black", font=font)
    draw.text((350, 290), f"Date : {date}", fill="black", font=font)
    draw.text((350, 360), f"Catégorie : S1", fill="black", font=font)
    draw.text((350, 430), f"Points : {data[user_id]['points']}/12", fill="black", font=font)

    temp_path = f"permis_{user_id}.png"
    background.save(temp_path)
    await ctx.send(file=discord.File(temp_path))

# ADMIN → générer le permis RP pour un autre membre
@bot.command()
@commands.has_permissions(administrator=True)
async def rp_permis(ctx, member: discord.Member = None):
    """Génère le permis RP japonais pour un membre spécifique"""
    if member is None:
        await ctx.send("❌ Veuillez mentionner un membre : `!rp_permis @Membre`")
        return

    user_id = str(member.id)
    data = load_json(PERMIS_FILE)

    # Si le membre n'a pas encore de permis, on le crée automatiquement avec 12 points
    if user_id not in data:
        data[user_id] = {"nom": member.name, "points": 12}
        save_json(PERMIS_FILE, data)

    # Charger le fond du permis
    try:
        background = Image.open("fond_permis.png").convert("RGBA")
    except:
        await ctx.send("❌ Fond du permis introuvable ! Met 'fond_permis.png' dans le dossier du bot.")
        return

    # Récupérer l'avatar Discord
    response = requests.get(member.avatar.url)
    avatar = Image.open(BytesIO(response.content)).resize((250, 250))
    background.paste(avatar, (60, 120))

    draw = ImageDraw.Draw(background)

    # Numéro RP unique
    numero = "RP-" + str(random.randint(100000, 999999))
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    font_path = "arial.ttf"
    font = ImageFont.truetype(font_path, 40)

    # Écriture des informations
    draw.text((350, 150), f"Nom RP : {member.display_name}", fill="black", font=font)
    draw.text((350, 220), f"Numéro : {numero}", fill="black", font=font)
    draw.text((350, 290), f"Date : {date}", fill="black", font=font)
    draw.text((350, 360), f"Catégorie : S1", fill="black", font=font)
    draw.text((350, 430), f"Points : {data[user_id]['points']}/12", fill="black", font=font)

    temp_path = f"permis_{user_id}.png"
    background.save(temp_path)

    await ctx.send(file=discord.File(temp_path))
    await ctx.send(f"🎉 Permis RP généré pour {member.mention} !")

# =======================
# COMMANDES POINTS ADMIN
# =======================
@bot.command()
@commands.has_permissions(administrator=True)
async def addpoints(ctx, member: discord.Member, points: int):
    data = load_json(PERMIS_FILE)
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("❌ Ce joueur n'a pas de permis RP.")
        return
    data[user_id]["points"] += points
    if data[user_id]["points"] > 12:
        data[user_id]["points"] = 12
    save_json(PERMIS_FILE, data)
    await ctx.send(f"➕ {points} points ajoutés à {member.mention} (**{data[user_id]['points']}/12**)")

@bot.command()
@commands.has_permissions(administrator=True)
async def removepoints(ctx, member: discord.Member, points: int):
    data = load_json(PERMIS_FILE)
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("❌ Ce joueur n'a pas de permis RP.")
        return
    data[user_id]["points"] -= points
    if data[user_id]["points"] < 0:
        data[user_id]["points"] = 0
    save_json(PERMIS_FILE, data)
    await ctx.send(f"➖ {points} points retirés à {member.mention} (**{data[user_id]['points']}/12**)")
    if data[user_id]["points"] == 0:
        await ctx.send(f"🚨 {member.mention} n'a plus de points → **PERMIS SUSPENDU RP**")

# ADMIN → supprimer un permis
@bot.command()
@commands.has_permissions(administrator=True)
async def removepermis(ctx, member: discord.Member):
    data = load_json(PERMIS_FILE)
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("❌ Ce joueur n'a pas de permis RP.")
        return
    del data[user_id]
    save_json(PERMIS_FILE, data)
    await ctx.send(f"🗑️ Permis RP supprimé pour {member.mention}")

# =======================
# CARTE GRISE RP (inchangée)
# =======================
@bot.command()
@commands.has_permissions(administrator=True)
async def addvehicule(ctx, member: discord.Member, marque: str, modele: str, plaque: str):
    data = load_json(VEHICULE_FILE)
    user_id = str(member.id)
    if user_id not in data:
        data[user_id] = []
    for v in data[user_id]:
        if v["plaque"].lower() == plaque.lower():
            await ctx.send("❌ Cette plaque existe déjà pour ce joueur.")
            return
    data[user_id].append({"marque": marque, "modele": modele, "plaque": plaque})
    save_json(VEHICULE_FILE, data)
    await ctx.send(f"🚗 Carte grise créée pour {member.mention} : {marque} {modele} — `{plaque}`")

@bot.command()
async def mesvehicules(ctx):
    data = load_json(VEHICULE_FILE)
    user_id = str(ctx.author.id)
    if user_id not in data or len(data[user_id]) == 0:
        await ctx.send("❌ Tu ne possèdes aucun véhicule RP.")
        return
    message = f"🚗 **Véhicules RP de {ctx.author.name} :**\n\n"
    for v in data[user_id]:
        message += f"• {v['marque']} {v['modele']} — `{v['plaque']}`\n"
    await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def removevehicule(ctx, member: discord.Member, plaque: str):
    data = load_json(VEHICULE_FILE)
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("❌ Ce joueur n'a aucun véhicule.")
        return
    new_list = [v for v in data[user_id] if v["plaque"].lower() != plaque.lower()]
    if len(new_list) == len(data[user_id]):
        await ctx.send("❌ Aucune voiture trouvée avec cette plaque.")
        return
    data[user_id] = new_list
    save_json(VEHICULE_FILE, data)
    await ctx.send(f"🗑️ Véhicule `{plaque}` supprimé pour {member.mention}")

# =======================
# LANCER LE BOT
# =======================
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
