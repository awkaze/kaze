# Kaze - Bot Discord Multifonction

(You're currently reading the french version of our README. Select README-ENG for the english version !)

*version 3.2.1*

Kaze est un Bot Discord créé pour le serveur Discord des 1ères années du BUT Informatique de l'IUT de Lannion, dans le but de proposer des commandes amusantes et utiles pour ses membres.
Le bot est codé de sorte à ce qu'il ne fonctionne que sur ce serveur, mais les techniques utilisées peuvent être réutilisées autre part.

## Table des Matières

- [Installation](#installation)
- [Fonctionnalités](#fonctionnalités)
- [Données](#données)
- [Contact](#contact)

## Installation

Vous pouvez cloner le projet à l'aide de la commande `git clone https://github.com/awkaze/kaze`. Tout est Open source.

Vous pouvez aussi télécharger le dossier compressé contenant le programme et l'éxécuter.

Vous aurez seulement à créer un fichier `.env` dans le dossier et à y ajouter vos propres valeurs en face de chaque identifiant (`TOKEN`, `MDP_BDD`, `HOST`, `UTILISATEUR`, `BDD`, `OWNER`, `SERVEUR`), après avoir installé [Python 3.9](https://www.python.org/downloads/release/python-3917/) (ou ultérieur) et les bibliothèques  suivantes :

- [dotenv](https://pypi.org/project/python-dotenv/)
- [discord.py](https://pypi.org/project/discord.py/)
- [mysql](https://pypi.org/project/mysql/)

## Fonctionnalités

Kaze présente la possibilité d'envoyer des messages à intervalles aléatoires (entre 1h et 3h après le dernier point obtenu) dans un salon d'activité défini grâce à la commande `salon`, message qui rapporte un point à la première personne qui y réagit, tout cela automatiquement. Attention à bien avoir activé la fonctionnalité à l'aide de la commande `activite`.<br> Ces points peuvent être consultés grâce à la commande `classement`.<br> Il y a également un système d'économie obtenable grâce à ce même message et des futurs mini-jeux qui seront implémentés. L'argent peut être consulté avec la commande `riches` qui affiche le classement des membres les plus riches du serveur.

![Exemple de message d'activité](https://cdn.discordapp.com/attachments/1217160501390479423/1217160516414472262/image.png?ex=66030410&is=65f08f10&hm=f614518984b4a5bdeec6d6a1c1aba5a8955ef20434767fab9fc64b64b9d02ffe&)

Une autre possibilité de se faire de l'argent fictif facilement reste la commande `actif`, qui permet de recevoir 200₭ directement, toutes les 24h.
![Exemple de la commande actif](https://cdn.discordapp.com/attachments/1217160501390479423/1217163226039451879/image.png?ex=66030696&is=65f09196&hm=14679831591f3de5c4122e49c379d1bb7423d965ae84d8c7c11ad96c16bc5964&)

Il existe d'autres commandes telles que `say`, `ping` ou `uptime`.
Elles sont toutes consultables avec la commande `help` !

## Données
Toutes les données sont stockées dans une base de données **MySQL** hébergée sur un serveur externe, gérées à l'aide de [phpMyAdmin](https://www.phpmyadmin.net).

## Contact
Lien du projet : https://github.com/awkaze/kaze

Vous pouvez me contacter via Discord : [awkaze_](discordapp.com/users/713900037796659211)

<img src="https://cdn.discordapp.com/attachments/1217160501390479423/1217173449814839446/image.png?ex=6603101c&is=65f09b1c&hm=a3833ee15013dbaa1f26d6e845709583964e9211418fd7e4ab10fdc763a3cd95&" width="500" height="300">

