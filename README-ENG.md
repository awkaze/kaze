# Kaze - Multifunctional Discord Bot

*version 3.2.1*

Kaze is a Discord Bot created for the 1rst year of computer science students from the IUT of Lannion's server, in order to offer funny and useful commands for the members.
The bot was developped in a way that makes it working only on this specific server, but you can use it anywhere else if you want to.

## Table of Contents

- [Setup](#setup)
- [Features](#features)
- [Data](#data)
- [Contact](#contact)

## Setup

You can clone the project with the `git clone https://github.com/awkaze/kaze` command. Everything is Open source.

You can also dowload the compressed folder which contains the program and execute it.

You will only have to create a `.env` file in the folder and add your own values for every field (`TOKEN`, `MDP_BDD`, `HOST`, `UTILISATEUR`, `BDD`, `OWNER`, `SERVEUR`), after downloading [Python 3.9](https://www.python.org/downloads/release/python-3917/) (or subsequent) and the following libraries :

- [dotenv](https://pypi.org/project/python-dotenv/)
- [discord.py](https://pypi.org/project/discord.py/)
- [mysql](https://pypi.org/project/mysql/)

## Features

Kaze offer the possibility to send messages at random intervals (betwenn 1 hour and 3 hour after the last obtained point) in an activity channel choosed with the `salon` command, a message that gives one point to the first person who reacts, automatically. Be sure to enable the feature by using the `activite` command before going any further. <br> Those points can be found in the leaderboard using the `classement` command.<br> There is also an economy system, used in this feature and also in future mini games that will be implemented soon. Money can be consulted with the `riches` command, that displays richest server members' leaderboard.

![Exemple de message d'activité](https://cdn.discordapp.com/attachments/1217160501390479423/1217160516414472262/image.png?ex=66030410&is=65f08f10&hm=f614518984b4a5bdeec6d6a1c1aba5a8955ef20434767fab9fc64b64b9d02ffe&)
*Be the first to click on the reaction below to score 1 point. Thanks for your activity !*<br>
*@Maël / Parzival won the point !*

You can also make (fake) money easily by using the `actif` command, which allows you to get 200₭ instantly, every 24 hours.
![Exemple de la commande actif](https://cdn.discordapp.com/attachments/1217160501390479423/1217163226039451879/image.png?ex=66030696&is=65f09196&hm=14679831591f3de5c4122e49c379d1bb7423d965ae84d8c7c11ad96c16bc5964&)
*Congrats, you won your daily 200₭. Come back in 24 hours to get 200 more !*<br>
*Sorry, but you can only claim 200₭ per day. Come back in 23 hours and 59 minutes.*

There are also other commands such as `say`, `ping` or `uptime`.
You will find them all using the `help` command !

## Data
All the data are stored in an external **MySQL** database, managed with a [phpMyAdmin](https://www.phpmyadmin.net) control panel.


## Contact
The project : https://github.com/awkaze/kaze

You can add me on Discord : [awkaze_](discordapp.com/users/713900037796659211)

<img src="https://cdn.discordapp.com/attachments/1217160501390479423/1217173449814839446/image.png?ex=6603101c&is=65f09b1c&hm=a3833ee15013dbaa1f26d6e845709583964e9211418fd7e4ab10fdc763a3cd95&" width="500" height="300">
