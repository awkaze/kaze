# Bot Discord pour le serveur Discord des 1ère année de BUT Info de l'IUT de Lannion
# Version 2.1
# Retrouvez moi sur Discord : awkaze_

# =============IMPORTS=============
import discord, datetime, time, asyncio, os, mysql.connector
from discord.ext import commands
from discord import app_commands
from random import randint, choice
from dotenv import load_dotenv

load_dotenv() # chargement des variables d'environnement (ici, le token du bot)

# ============= CLASSE BOT =============
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        intents.bans = True
        intents.messages = True
        intents.reactions = True
        intents.message_content = True
        super().__init__(command_prefix = "!", intents = intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync(guild = discord.Object(id = 1136325238225895444))
        print(f" Commandes slash de {self.user} activées.")

bot = Bot() # création d'une instance de la classe Bot


# ============= CONNEXION BDD =============

# les variables d'environnement sont stockées dans un fichier .env pour des raisons de sécurité

mydb = mysql.connector.connect(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("MDP_BDD"),
    database=os.getenv("BDD")
)

cursor = mydb.cursor(dictionary=True) # récupération des résultats sous forme de dictionnaire

"""
Schema de la base de données :

kactif : id, kdate 
kbanque : banque_id, montant, bclassement 
kactivite : id, pts, aclassement, treact
kinfos : salon, activite

"""


# ============= FONCTIONS =============

async def ping_db(cursor):
    """
    Envoie de ping à la base de données pour éviter les déconnexions car l'hebergeur que j'utilise (Hostinger) 
    coupe la connexion au bout de 30 secondes d'inactivité, et parfois même moins.

    On prend donc pas de risque et on envoie un ping toutes les 1 secondes.
    Ca ne risque pas de surchager la base de données car c'est une opération très rapide.
    """

    while True:
        cursor.execute("SELECT * FROM kinfos")
        donnees = cursor.fetchall()
        await asyncio.sleep(1) # on attend 1 seconde avant de renvoyer un ping
    

async def verification_conditions(cursor):
    """
    Fonction qui récupère les paramètres actuels d'activité de la base de données.
    Retourne un tuple (jeu, salon) où `jeu` est un booléen qui indique si on peut lancer le jeu d'activité
    et `salon` est l'ID du salon si il a été choisi, sinon None.
    """
    cursor.execute("SELECT * FROM kinfos")
    donnees = cursor.fetchall()
    for row in donnees:
        if str(row['activite']) == "1" and row['salon'] is not None:
            return True, int(row['salon'])
    return False, None

async def recompense_activite():
    """
    Fonction pour envoyer un message aléatoire dans le salon d'activité du serveur toutes les 1 à 3 heures (aléatoire), 
    avec une réaction à cliquer pour gagner 1 point d'activité.
    Le but est de récompenser les membres les plus actifs, et de créer une compétition entre eux.
  
    On commence par récupérer les informations de la table kinfos pour savoir si les messages d'activité sont activés et si un salon a été choisi.
    Si c'est le cas, on lance le jeu d'activité comme décrit ci-dessus.
    Sinon, on attend 1 minute avant de vérifier à nouveau si ces conditions sont remplies.
    L'attente est nécessaire pour éviter de surcharger le bot et le serveur, sinon il est impossible d'effectuer d'autres actions
    comme répondre à des commandes ou envoyer des messages.
    """
    while True:
        jeu, salon_id = await verification_conditions(cursor)
        if not jeu:
            await asyncio.sleep(60) # on attend 1 minute avant de vérifier à nouveau
        if jeu:
            channel = bot.get_channel(salon_id)
            await asyncio.sleep(randint(3600, 10800)) # 1 à 3 heures

            message = await channel.send("Clique sur la réaction ci-dessous en premier pour marquer 1 point. Merci pour ton activité !")
            await message.add_reaction(choice(["🔥", "🌟", "🎉", "🎈", "🎁", "🎊", "🍾", "🎇", "🎆", "🌠", "🌅", "🌄", "🌃", "🌉", "🌁"]))
            messagetime = datetime.datetime.now() # récupérer le moment où la réaction apparait

            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user != bot.user and reaction.message.id == message.id)
            reactiontime = datetime.datetime.now() # récupérer le moment où l'utilisateur appuie sur la réaction
            await channel.send(f"<@{user.id}> a gagné le point !")

            cursor.execute(f"SELECT a.id, a.pts, a.aclassement, a.treact, bq.montant, bq.bclassement FROM kactivite AS a LEFT JOIN kbanque AS bq ON a.id = bq.banque_id WHERE a.id = {user.id}")
            donnees = cursor.fetchall()

            utilisateur_trouve = False 
            temps_reaction = (reactiontime - messagetime).total_seconds()


            async def give_money(howmuch, mydb, cursor, user):
                """
                Fonction pour donner de l'argent à un utilisateur lorsqu'il réagit à un message d'activité et gagne un point.
                """
                
                cursor.execute(f"SELECT a.id, a.pts, a.aclassement, a.treact, bq.montant, bq.bclassement, act.kdate FROM kactivite AS a LEFT JOIN kbanque AS bq ON a.id = bq.banque_id LEFT JOIN kactif AS act ON a.id = act.id WHERE a.id = {user.id}")
                donnees = cursor.fetchall()

                inbanque = False
                for row in donnees:
                    if row['montant'] is not None:
                        actuel = int(row['montant'])
                        nouveau = actuel + howmuch

                        # Update 
                        sql = "UPDATE kbanque SET montant = %s"
                        val = (str(nouveau),) # on met une virgule pour que le tuple soit bien reconnu par la méthode execute()
                        cursor.execute(sql, val)
                        inbanque = True
                if not inbanque:
                    # si on ne trouve pas l'utilisateur 
                    sql = "INSERT INTO kbanque (banque_id, montant, bclassement) VALUES (%s, %s, %s)"
                    val = (user.id, f"{howmuch}", "1")
                    cursor.execute(sql, val)

            async def search_money(mydb, cursor, user):
                cursor.execute(f"SELECT a.id, a.pts, a.aclassement, a.treact, bq.montant, bq.bclassement FROM kactivite AS a LEFT JOIN kbanque AS bq ON a.id = bq.banque_id WHERE a.id = {user.id}")
                donnees = cursor.fetchall()

                chan = await user.create_dm()
                
                # Créer un dictionnaire pour associer chaque valeur à la somme correspondante
                rewards = {
                    "5": "50",
                    "10": "100",
                    "20": "500",
                    "30": "750",
                    "40": "1500",
                    "50": "5000",
                    "75": "10000",
                    "100": "25000"
                }

                # Vérifier si la valeur existe dans le dictionnaire rewards
                for row in donnees:
                    if str(row['pts']) in rewards:
                        # Utiliser la somme associée à la valeur de ['pts']
                        await give_money(int(rewards[str(row['pts'])]), mydb, cursor, user)
                        await chan.send(f"Bravo, tu viens d'obtenir {rewards[str(row['pts'])]}₭ pour avoir atteint {row['pts']} points d'activité. Continue comme ça !")
                    else:
                        await give_money(10, mydb, cursor, user)


            for row in donnees:
                if row['pts'] is not None:
                
                    treact = float(row['treact'])
                    nouveau = int(row['pts']) + 1
                    moyreact = (treact+float(temps_reaction))/2

                    sql = "UPDATE kactivite SET pts = %s, aclassement = %s, treact = %s WHERE id = %s"
                    val = (str(nouveau), "1", str(moyreact), f"{user.id}")
                    cursor.execute(sql, val)
                    utilisateur_trouve = True

            if not utilisateur_trouve:
                # si on ne trouve pas l'utilisateur 
                sql = "INSERT INTO kactivite (id, pts, aclassement, treact) VALUES (%s, %s, %s, %s)"
                val = (user.id, "1", "1", f"{temps_reaction}")
                cursor.execute(sql, val)
            
            await search_money(mydb, cursor, user)

            mydb.commit()

async def the_activity():
    """
    Fonction qui modifie le statut du bot sur Discord.
    """
    global start_time # on récupère la variable start_time déclarée dans la fonction on_ready()
    start_time = time.time()
    await bot.change_presence(activity=discord. Activity(type=discord.ActivityType.watching, name="bientôt..."))

async def guess_nb(channel, message):
    """
    Fonction pour lancer le jeu où il faut deviner un nombre entre 1 et 100.
    L'avantage c'est que la fonction est asynchrone, ce qui permet de continuer à utiliser le bot normalement pendant que le jeu tourne.
    """
    number = str(randint(1,100))
    while True:
        def check(m):
            return m.content == number and m.channel == channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=120.0)
            await channel.send(f'{msg.author.mention} a gagné ! Le nombre à deviner était {number}.')
            
        except asyncio.TimeoutError:
            await message.reply(f"Temps écoulé ! Le nombre à deviner était {number}.")
            break  
   
# ======== EVENEMENTS ========
@bot.event
async def on_ready():
    """
    Fonction qui s'exécute lorsque le bot se connecte à Discord.
    """
    print(f'{bot.user.name} est connecté !')
    bot.loop.create_task(the_activity())
    bot.loop.create_task(recompense_activite())
    bot.loop.create_task(ping_db(cursor))
    # bot.loop.create_task() permet de continuer à utiliser le bot normalement pendant que ces fonctions tournent en arrière-plan

@bot.event
async def on_message(message): 
    """
    Fonction qui s'exécute à chaque fois qu'un message est envoyé sur le serveur.
    """
    await bot.process_commands(message) 


@bot.event
async def on_member_join(member):
    """
    Fonction qui s'exécute lorsque qu'un membre rejoint le serveur.
    """
    await member.send("Bienvenue sur le serveur Discord des 1ère année de BUT Info de l'IUT de Lannion ! Tu n'as plus qu'à envoyer ton nom et prénom dans le salon verification pour avoir accès à l'ensemble du serveur. :slight_smile:")
    channel = bot.get_channel(1136341234189869227)
    guild = bot.get_guild(1136325238225895444)
    await channel.send(f"Bienvenue à {member.mention} qui vient de débarquer sur le serv ! On est {str(guild.member_count)}.")

@bot.event
async def on_member_remove(member):
    """
    Fonction qui s'exécute lorsque qu'un membre quitte le serveur.
    """
    channel = bot.get_channel(1136341234189869227)
    guild = bot.get_guild(1136325238225895444)
    await channel.send(f"{member.name} s'est cassé du serv.. On est plus que {str(guild.member_count)}.")

@bot.event
async def on_command_error(ctx, error):
    """
    Fonction qui s'exécute lorsqu'une erreur survient lors de l'exécution d'une commande.
    """
    if isinstance(error, commands.CommandOnCooldown): # si l'erreur est une commande en cooldown
        cooldown = error.retry_after # on récupère le temps restant avant de pouvoir réutiliser la commande
        await ctx.reply(f"Doucement, tu ne peux utiliser cette commande qu'une fois par minute. Réessaye dans `{str(cooldown)[:str(cooldown).find('.')]}` secondes.")

# =================== COMMMANDES=====================
        
# ===== CHOIX SALON =====

@bot.hybrid_command(name = "salon", with_app_command = True, description = "Choisis le salon dans lequel tu veux que j'envoie les messages de récompense d'activité.")
@app_commands.guilds(discord.Object(id = 1136325238225895444))
async def salon(ctx: commands.Context, salon=None):
    """
    Fonction pour choisir le salon dans lequel les messages d'activité seront envoyés.
    """

    # on verifie que l'utilisateur est bien un admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.reply("Tu dois être administrateur pour utiliser cette commande.")
        return
    else:
        cursor.execute(f"SELECT * FROM kinfos")
        donnees = cursor.fetchall()

        try:
            for row in donnees:
                if row['salon'] is not None: # si un salon a déjà été choisi
                    if salon is None: # si l'utilisateur n'a pas précisé de salon à l'appel de la commande
                        if row['salon'] == ctx.channel.id: 
                            await ctx.reply("Ce salon est déjà défini comme salon d'activité.")
                        else: 
                            sql = "UPDATE kinfos SET salon = %s"
                            val = (ctx.channel.id,) # on met une virgule pour que le tuple soit bien reconnu par la méthode execute()
                            cursor.execute(sql, val)
                            await ctx.reply(f"Nouveau salon d'activité : <#{ctx.channel.id}>.")
                    else:
                        salon = bot.get_channel(int(salon[2:-1])) # on enlève les 2 premiers caractères et le dernier pour ne garder que l'id car le format est <#id>
                        if row['salon'] == salon.id: 
                            await ctx.reply(f"Le salon <#{salon.id}> est déjà défini comme salon d'activité.")
                        else:
                            sql = "UPDATE kinfos SET salon = %s"
                            val = (str(salon.id),) # on met une virgule pour que le tuple soit bien reconnu par la méthode execute()
                            cursor.execute(sql, val)
                            await ctx.reply(f"Nouveau salon d'activité : <#{salon.id}>.")
                else: 
                    if salon is None:
                        sql = "INSERT INTO kinfos (salon) VALUES (%s)"
                        val = (str(ctx.channel.id))
                        cursor.execute(sql, val)
                        await ctx.reply(f"Salon d'activité défini sur <#{salon.id}>.")
                    else: 
                        sql = "INSERT INTO kinfos (salon) VALUES (%s)"
                        val = (str(salon.id))
                        cursor.execute(sql, val)
                        await ctx.reply(f"Salon d'activité défini sur <#{salon.id}>.")
            mydb.commit()
        except:
            await ctx.reply("Mauvaise syntaxe. Consulte l'aide (`/help`) pour plus d'informations. ")


# ===== ACTIVITE =====

@bot.hybrid_command(name = "activite", with_app_command = True, description = "Choisir d'activer ou de désactiver les messages d'activité.")
@app_commands.guilds(discord.Object(id = 1136325238225895444))
async def activite(ctx: commands.Context):
    """
    Fonction pour activer ou désactiver les messages d'activité.
    """
    # on verifie que l'utilisateur est bien un admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.reply("Tu dois être administrateur pour utiliser cette commande.")
        return
    else:
        cursor.execute(f"SELECT * FROM kinfos")
        donnees = cursor.fetchall()

        for row in donnees:
            if str(row['activite']) == "1":
                sql = "UPDATE kinfos SET activite = %s"
                val = ("0",)
                cursor.execute(sql, val)
                await ctx.reply("Les messages d'activité sont désormais désactivés.")
            else:
                if row['salon'] is None:
                    await ctx.reply("Tu dois d'abord choisir un salon dans lequel les messages d'activité seront envoyés avec la commande `/salon` avant de pouvoir les activer !")
                else:
                    sql = "UPDATE kinfos SET activite = %s"
                    val = ("1",)
                    cursor.execute(sql, val)
                    await ctx.reply("Les messages d'activité sont désormais activés.")
        
        mydb.commit()

# ===== PING =====

@bot.hybrid_command(name = "ping", with_app_command = True, description = "afficher le temps de réaction du bot.")
@app_commands.guilds(discord.Object(id = 1136325238225895444))
async def ping(ctx: commands.Context):
    """
    Fonction pour afficher le temps de réaction du bot.
    """
    latency = bot.latency * 1000  # on convertit la latence renvoyée par la méthode en millisecondes
    await ctx.reply(f'Pong! Je réponds avec une latence de : {latency:.2f} ms')


# ===== SAY =====

@bot.command()
async def say(ctx, *, message=None):
    """
    Fonction pour répéter un message.
    """
    if ctx.author.id == 713900037796659211:
        if message != None:
            await ctx.message.delete()
            await ctx.send(message)
        else:
            await ctx.reply("Qu'est-ce que tu veux que je dise ?")

# ===== UPTIME =====
        
@bot.hybrid_command(name = "uptime", with_app_command = True, description = "Affiche le temps écoulé depuis le lancement du bot")
@app_commands.guilds(discord.Object(id = 1136325238225895444))
async def uptime(ctx: commands.Context):
    """
    Fonction pour afficher le temps écoulé depuis le lancement du bot.
    """
    current_time = time.time()
    difference = int(round(current_time - start_time)) # on récupère le temps écoulé depuis le lancement du bot (qu'on a initialisé dans la fonction on_ready() )
    await ctx.reply("Temps depuis lancement : "+str(datetime.timedelta(seconds=difference))) 

# ===== ACTIF =====
    
@bot.hybrid_command(name = "actif", with_app_command = True, description = "Recois de l'argent tous les jours avec cette commande !")
@app_commands.guilds(discord.Object(id = 1136325238225895444))
async def actif(ctx: commands.Context):
    """
    Fonction pour recevoir 200₭ tous les jours.

    On vérifie si la date de la dernière récompense reçue par l'utilisateur est supérieure à 24h.
    Si c'est le cas, on lui donne 200₭ et on met à jour la date de la dernière récompense.
    Sinon, on lui dit de revenir dans 24h.
    """

    cursor.execute(f"SELECT * FROM kactif LEFT JOIN kbanque ON kactif.id = kbanque.banque_id WHERE kactif.id = {ctx.author.id}")
    donnees = cursor.fetchall()

    # on vérifie si l'utilisateur est dans la table kactif
    if donnees != []:
        """"""
        for row in donnees:
            last_reward_time = row['kdate']
            last_reward_time = datetime.datetime.strptime(last_reward_time, "%Y-%m-%d %H:%M:%S.%f") # on convertit la date en objet datetime pour pouvoir la manipuler
            time_since_last_reward = datetime.datetime.now() - last_reward_time

            # on vérifie si la date de la dernière récompense est supérieure à 24h
            if time_since_last_reward >= datetime.timedelta(hours=24):

                # on vérifie si l'utilisateur est dans la table kbanque
                if row['montant'] is not None:

                    # on lui donne 200₭ 
                    actuel = int(row['montant']) 
                    nouveau = actuel + 200

                    sql = "UPDATE kbanque SET montant = %s, bclassement = %s WHERE banque_id = %s"
                    val = (str(nouveau), "1", f"{ctx.author.id}")
                    cursor.execute(sql, val)
                
                # sinon, on crée une nouvelle ligne pour lui
                else: # si on ne trouve pas l'utilisateur
                    sql = "INSERT INTO kbanque (id, montant, bclassement) VALUES (%s, %s, %s)"  
                    val = (ctx.author.id, f"200", "1")
                    cursor.execute(sql, val)
                
                sql = "UPDATE kactif SET kdate = %s WHERE id = %s"
                val = (str(datetime.datetime.now()), f"{ctx.author.id}")
                cursor.execute(sql, val)

                await ctx.reply("Bravo, tu as gagné tes 200₭ journaliers. Reviens dans 24h pour en avoir 200 de plus !")
            else:
                # on lui dit de revenir dans 24h
                time_until_next_reward = last_reward_time + datetime.timedelta(hours=24) - datetime.datetime.now()
                hours, remainder = divmod(time_until_next_reward.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await ctx.reply(f"Désolé, mais tu ne peux récupérer 200₭ qu'1 fois par jour ! Reviens dans **{hours} heures et {minutes} minutes**.")
    else:
        # on crée une nouvelle ligne pour lui
        sql = "INSERT INTO kactif (id, kdate) VALUES (%s, %s)"
        val = (f"{ctx.author.id}", str(datetime.datetime.now()))
        cursor.execute(sql, val)
        mydb.commit()

        cursor.execute(f"SELECT * FROM kactif LEFT JOIN kbanque ON kactif.id = kbanque.banque_id WHERE kactif.id = {ctx.author.id}")
        donnees = cursor.fetchall()

        # on vérifie si l'utilisateur est dans la table kbanque
        for row in donnees:
            if row['montant'] is not None: 

                # on lui donne 200₭
                actuel = int(row['montant'])
                nouveau = actuel + 200

                sql = "UPDATE kbanque SET montant = %s, bclassement = %s WHERE banque_id = %s"
                val = (str(nouveau), "1", f"{ctx.author.id}")
                cursor.execute(sql, val)
            else:
                # sinon, on crée une nouvelle ligne pour lui
                sql = "INSERT INTO kbanque (banque_id, montant, bclassement) VALUES (%s, %s, %s)"  
                val = (ctx.author.id, f"200", "1")
                cursor.execute(sql, val)
        await ctx.reply("Bravo, tu as gagné tes 200₭ journaliers. Reviens dans 24h pour en avoir 200 de plus !")

    mydb.commit()

bot.run(os.getenv("TOKEN"))