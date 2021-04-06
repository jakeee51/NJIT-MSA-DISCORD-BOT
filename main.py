# -*- coding: utf-8 -*-
'''
بسم الله
Author: David J. Morfe
Application Name: MSA-Bot
Functionality Purpose: An agile Discord Bot to fit any MSA's needs
'''
RELEASE = "v0.0.1 - 4/3/21"


import re, os, sys, time, json, datetime
from cmds import *
from config import *
from tools import *


RUN_TIME = datetime.datetime.now()
LAST_MODIFIED = RUN_TIME.strftime("%m/%d/%Y %I:%M %p")
RELEASE += f" ({ENV})"

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

@bot.event
async def on_member_join(member):
    #await bot.edit_message(message_var, "This is the edit to replace the message.")
    channel = bot.get_channel(VERIFY_ID)
    await asyncio.sleep(86400)
    if len(member.roles) == 1:
        await channel.send(member.mention + " ***Hello again!***\n\n**Please verify to join the chat!**", delete_after=60)

# Listen to added reactions in specified channels
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id != SISTERS.role_select and \
       payload.channel_id != BROTHERS.role_select and \
       payload.channel_id != PROS.role_select:
        return -1
    role_id = listen_role_reaction(payload.emoji, payload.channel_id)
    if role_id:
        role = get(
            bot.get_guild(SERVER_ID).roles, id=role_id)
        del(role_id)
        await payload.member.add_roles(role)

# Listen to removed reactions in specified channels
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id != SISTERS.role_select and \
       payload.channel_id != BROTHERS.role_select and \
       payload.channel_id != PROS.role_select:
        return -1
    role_id = listen_role_reaction(payload.emoji, payload.channel_id)
    if role_id:
        guild = bot.get_guild(SERVER_ID)
        member = guild.get_member(payload.user_id)
        role = get(guild.roles, id=role_id)
        del(role_id); del(guild)
        try:
            await member.remove_roles(role)
        except AttributeError:
            return -1

# Standard MSA Bot Commands
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return -1;
    if message.content.lower().startswith('/version'):
        if message.author.id in DEVS:
            await message.channel.send(f"`{RELEASE} | {LAST_MODIFIED}`")

    # Shared Announcment System
    if listen_announce(message): # Send to alternate announcement channel
        announce_channel = listen_announce(message)
        channel = bot.get_channel(announce_channel)
        try:
          ext = re.search(r".(png|jpg|jpeg|mp4)$", message.attachments[0].url)
        except IndexError:
          ext = None
        if len(message.attachments) == 1 and ext:
            file_name = "imgs/reattach" + str(ext.group())
            with open(file_name, "wb") as f:
                await message.attachments[0].save(f)
            img = File(file_name)
            await channel.send(message.content, file=img)
            os.remove(file_name)
        else:
            await channel.send(message.content)

    # Verification System
    if listen_verify(message): # Verify command
        sid, gender = listen_verify(message)
        if not re.search(r"^[a-zA-Z]{2,4}\d{0,4}$", sid) or \
           not re.search(r"^/verify ", str(message.content)) or \
           sid == '':
            await message.channel.send("**Invalid command! Please make sure you're typing everything correctly.**", delete_after=25)
            await message.delete(delay=300)
        elif not re.search(r"(Brother|Sister)", gender):
            await message.channel.send("**Invalid command! Are you a brother, sister or workforce?**", delete_after=25)
            await message.delete(delay=300)
        elif re.search(r"\d{8}", message.content):
            await message.channel.send("**Invalid command! NOT your student ID, use your UCID!**", delete_after=25)
            await message.delete(delay=300)
        else:
            sid_email = sid.lower() + "@" + MSA.lower() + ".edu"
            vCode = send_email(sid_email, test=TEST_MODE); ID = message.author.id
            with open("verify.txt", 'a') as f:
                f.write(f"{vCode} {sid} {ID} {gender}\n")
            temp = await message.channel.send(f"**We've sent a verification code to your sid at** ___{sid}___**, please copy & paste it below.**", delete_after=300)
            await message.delete(delay=300)
            try: # Purge messages when record is removed from 'verify.txt' otherwise purge in 15 minutes
                await asyncio.wait_for(check_verify(f"{vCode} {sid}", message, temp), timeout=900)
            except asyncio.TimeoutError:
                try:
                    await message.delete(); await temp.delete()
                except errors.NotFound:
                    pass
                edit_file("verify.txt", f"{vCode} {sid} {ID} {gender}")
    elif listen_code(message): # Listen for 4-digit code on the NJIT MSA #verify
        eCode = listen_code(message)
        if eCode:
            with open("verify.txt") as f:
                lines = f.readlines(); flag = True
                if len(lines) != 0:
                    for line in lines:
                        lst = line.strip('\n').split(' ')
                        if lst[0] == eCode.group() and lst[2] == str(message.author.id): # Verify code
                            edit_file("verify.txt", line.strip('\n'))
                            role = get(bot.get_guild(SERVER_ID).roles,
                                                     name=f"{lst[3]}s Waiting Room")
                            await message.author.add_roles(role); flag = False
                            nName = get_name(lst[1])
                            sibling = get_sibling(lst[3])
                            await message.delete()
                            try:
                                if nName != None:
                                    await message.author.edit(nick=f"{nName}")
                                else:
                                    await message.author.edit(nick=f"{lst[1]}")
                            except errors.Forbidden:
                                print("Success!\n", nName)
                            channel = bot.get_channel(sibling.wait) # NJIT MSA #general
                            await channel.send(f"@here ***" + message.author.mention + "***" + f" *has joined the {MSA} MSA Discord!*")
                        else:
                            await message.delete(delay=60)
                    if flag:
                        temp = await message.channel.send("**Invalid code! Who a u?!**")
                        await temp.delete(delay=60)
    else: # Delete every other message in #verify in 5 min.
        if message.channel.id == VERIFY_ID:
            if re.search(r"^[a-zA-Z]{2,4}\d{0,4}$", message.content):
                await message.channel.send("**Invalid command! Read instructions above and use /verify please!**", delete_after=25)
            await message.delete(delay=300)
    await bot.process_commands(message)


# Bot Starting Point
if __name__ == "__main__":
    token = BOT
    bot.run(token)
##bot.logout()
##bot.close()
##print("We have logged out of bot")
