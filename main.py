# -*- coding: utf-8 -*-
'''
بسم الله
Author: David J. Morfe
Application Name: MSA-Bot
Functionality Purpose: An agile Discord Bot to fit any MSA's needs
'''
RELEASE = "v0.2.0 - 9/14/21"


import re, os, sys, time, json, datetime, yaml
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
       payload.channel_id != BROTHERS.role_select:
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
       payload.channel_id != BROTHERS.role_select:
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
    if message.content == 'nu u':
        if "Cali#6919" == str(message.author):
            await message.channel.send("nu u!")
    if message.content.lower().startswith('/version'):
        if message.author.id in DEVS:
            await message.channel.send(f"`{RELEASE} | {LAST_MODIFIED}`")
    if re.search("(nu nu|Nunu|nunu)", message.content): # Taha
        if message.author.id == 496079190475538461:
            await message.channel.send("nu nu?")
    if "/taha" in message.content.lower(): # Taha
        if message.author.id == 496079190475538461:
            await message.channel.send("Yes we can")
    if "/anas" in message.content.lower(): # Anas
        if message.author.id == 406821958563528737:
            await message.channel.send("knowimsayin dawg", delete_after=10)
    if "Solo Leveling" in message.content:          
        if message.author.id == 185842527520292874: # Omar E.
            await message.channel.send("Yo that junk is fire :fire:", delete_after=10)
    if "ws" == message.content:
        await message.channel.send("Walaikumu Salam")
    if "iA" == message.content:
        await message.channel.send("Insha'Allah")
    if "texas" in str(message.content).lower(): # Siraj
        if message.author.id == 416430987241586698:
            await message.channel.send("https://media.tenor.co/videos/c8bad30e8d9834c6543b7575c3d7bd89/mp4")
    if "cap" in str(message.content).lower(): # Usmaan
        if message.author.id == 397082457179947029:
            await message.channel.send("yo that's cap'n cap'n")
    if re.search(r"\b(retard|fuck|shit|ass|pussy?|fucker|dick|nigger|bitch|nigg|damn|prick|nigga)(s|ed|er|ing|ting)?\b", str(message.content).lower()): # No Bad Language/Cussing
        await message.channel.send("https://gyazo.com/45ad780b2d98f884f00273e3dc0db6cc", delete_after=20)
        await message.delete(delay=1)
    elif curse_check(str(message.content).lower()): # No Bad Language/Cussing
        await message.channel.send("https://gyazo.com/45ad780b2d98f884f00273e3dc0db6cc", delete_after=20)
        await message.delete(delay=1)


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
        ucid, gender = listen_verify(message)
        if not re.search(r"^[a-zA-Z]{2,4}\d{0,4}$", ucid) or \
           not re.search(r"^/verify ", str(message.content)) or \
           ucid == '':
            await message.channel.send("**Invalid command! Please make sure you're typing everything correctly.**", delete_after=25)
            await message.delete(delay=300)
        elif not re.search(r"(Brother|Sister)", gender):
            await message.channel.send("**Invalid command! Are you a brother, sister or workforce?**", delete_after=25)
            await message.delete(delay=300)
        elif re.search(r"\d{8}", message.content):
            await message.channel.send("**Invalid command! NOT your student ID, use your UCID!**", delete_after=25)
            await message.delete(delay=300)
        else:
            email_addr = ucid.lower() + f"@{MSA}.edu".lower(); ID = message.author.id
            temp = await message.channel.send(f"**We've sent a verification link to your email at** ___{email_addr}___**, please check your email.**",
                                              delete_after=300)
            await message.delete(delay=300)
            vCode = send_email(email_addr, gender, test=TEST_MODE)
            result = await send_verify_post({"code": str(vCode)}, test=TEST_MODE)

            if result == '0':
                vCode = send_email(email_addr, gender, test=TEST_MODE)
                result = await send_verify_post(*args)

            if result == '0':
                await message.delete(); temp.delete()
            elif result == '-1':
                await message.delete(); temp.delete()
            elif result == vCode:
                await message.delete(); await temp.delete()
                # {vCode} {email_addr} {ID} {gender}
                guild = bot.get_guild(SERVER_ID)
                role = get(guild.roles, name=f"{gender}s Waiting Room")
                await message.author.add_roles(role) # Add Waiting Room role to user
                nName = get_name(email_addr) # New Nick Name
                try:
                    if nName != None: # Re-name user
                        await message.author.edit(nick=str(nName))
                    else:
                        nName = email_addr
                        await message.author.edit(nick=str(nName))
                except errors.Forbidden:
                    print("Success!\n", nName)
                sibling = get_sibling(gender) # Get brother/sister object
                channel = bot.get_channel(sibling.wait) # NJIT MSA #general
                await channel.send(f"@here ***" + message.author.mention + "***" + f" *has joined the {MSA} MSA Discord!*")
            else:
                print("Invalid post request!")
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
