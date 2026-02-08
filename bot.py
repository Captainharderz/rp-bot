import discord
from discord.ext import commands
import os
import json
import random

# =======================
# CONFIGURATION DES INTENTS
# =======================
intents = discord.Intents.default()
intents.message_content = True  # pour lire les messages
intents.members = True          # pour gérer les membres

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
# PERMIS RP
# =======================

# ADMIN → créer un permis
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

# TOUS → voir son permis
@bot.command()
async def monpermis(ctx):
    data = load_json(PERMIS_FILE)
    user_id = str(ctx.author.id)

    if user_id not in data:
        await ctx.send("❌ Tu n'as pas de permis RP.")
        return

    permis = data[user_id]
    await ctx.send(
        f"🪪 **PERMIS RP**\n"
        f"👤 Joueur : {ctx.author.name}\n"
        f"⭐ Points : **{permis['points']}/12**"
    )

# ADMIN → ajouter des points
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

# ADMIN → retirer des points
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
# CARTE GRISE RP
# =======================

# ADMIN → ajouter un véhicule
@bot.command()
@commands.has_permissions(administrator=True)
async def addvehicule(ctx, member: discord.Member, marque: str, modele: str, plaque: str):
    data = load_json(VEHICULE_FILE)
    user_id = str(member.id)

    if user_id not in data:
        data[user_id] = []

    # Vérifier si la plaque existe déjà
    for v in data[user_id]:
        if v["plaque"].lower() == plaque.lower():
            await ctx.send("❌ Cette plaque existe déjà pour ce joueur.")
            return

    data[user_id].append({"marque": marque, "modele": modele, "plaque": plaque})
    save_json(VEHICULE_FILE, data)
    await ctx.send(f"🚗 Carte grise créée pour {member.mention} : {marque} {modele} — `{plaque}`")

# TOUS → voir ses véhicules
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

# ADMIN → supprimer un véhicule
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
# LIVRAISONS RP
# =======================

points_A = [
    "https://imgur.com/a/OCBYB3f",
    "https://imgur.com/a/HlY9e8J",
    "https://imgur.com/a/Iq6pVIt"
]

points_B = [
    "https://imgur.com/a/WC97b1F",
    "https://imgur.com/a/cIfDccB",
    "https://imgur.com/a/Rm1IuPp"
]

marchandises_legales = [
    "Livraison colis 3000$",
    "Jantes 5000$",
    "Matériel électronique 1500$"
]

marchandises_illegales = [
    "Cocaïne 10000$",
    "Cannabis 5000$",
    "Armes 30000$"
]

@bot.command()
async def pointa(ctx):
    lieu = random.choice(points_A)
    await ctx.send(f"📍 **POINT A — CHARGEMENT**\n\n{lieu}\nRends-toi sur ce point pour récupérer la marchandise 🚚")

@bot.command()
async def marchandise(ctx, type_marchandise: str):
    type_marchandise = type_marchandise.lower()
    if type_marchandise not in ["legal", "illegal"]:
        await ctx.send("❌ Utilisation : `!rp_marchandise legal` ou `!rp_marchandise illegal`")
        return
    if type_marchandise == "legal":
        march = random.choice(marchandises_legales)
        emoji = "📦"
    else:
        march = random.choice(marchandises_illegales)
        emoji = "🚨"
    await ctx.send(f"{emoji} **MARCHANDISE {type_marchandise.upper()}**\n\n📦 {march}")

@bot.command()
async def pointb(ctx):
    lieu = random.choice(points_B)
    await ctx.send(f"📍 **POINT B — DÉCHARGEMENT**\n\n{lieu}\nDépose la marchandise ici 📦")

# =======================
# LANCER LE BOT
# =======================
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
