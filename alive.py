# -*- coding: utf-8 -*-
'''
بسم الله
Author: David J. Morfe
Application Name: MSA-Bot
Functionality Purpose: An agile Discord Bot to fit any MSA's needs
'''


import re, os, sys, time
from cmds import *
from config import *
from tools import *

##MODE = ''; USER = 0

class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self .stream, attr)
sys.stdout = Unbuffered(sys.stdout)

# Executes when bot begins running
@bot.event
async def on_ready():
    await bot.change_presence(activity = Game(name = "/cmds (For all cmds)"))
    print("We have logged in as {0.user} in {1}".format(bot, ENV))
    if MODE == '' or MODE == '0':
        print("DM MODE")
        global USER
        try:
            USER = int(input("Enter User ID: "))
            guild = bot.get_guild(SERVER_ID)
            member = guild.get_member(USER)
        except:
            print("Wrong type!")
        reply = str(input("reply here: "))
        await member.send(reply)
    else:
        print("CHANNEL MODE")
        try:
            chan = int(input("Enter Channel ID: "))
            channel = bot.get_channel(chan)
        except (ValueError,AttributeError):
            print("Wrong type!")
            chan = 631090067963772931
            channel = bot.get_channel(chan)
        while True:
            reply = str(input("reply here: "))
            await channel.send(reply)

# Standard MSA Bot Commands
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return -1;
    if message.author.id == USER:
        print(message.content)
        reply = str(input("reply here: "))
        await message.author.send(reply)
    await bot.process_commands(message)


# Bot Starting Point
if __name__ == "__main__":
    global MODE, USER
    MODE = input("Enter 0 for DM or 1 for CHANNEL: ")
    token = BOT
    bot.run(token)
##bot.logout()
##bot.close()
##print("We have logged out of bot")
##Greetings! This is the MSA (Marriage Student Association) Bot. Please type a sister's name to proceed to ensalvement :D
