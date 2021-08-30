from discord.ext import commands
from discord.utils import get
from discord import Intents
from discord import File
from discord import Embed
from discord import Game
from discord import errors
from subprocess import Popen
import asyncio, yaml
from config import *
from tools import *


intents = Intents.default()
intents.members = True # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix='/', help_command=None, intents=intents)
#client = discord.Client(intents=intents)


# Extended MSA Bot Commands
@bot.command()
async def cmds(ctx): # Help command
    with open("cmds.md") as f:
        cmds = f.read()
    await ctx.send("__**NJIT MSA Bot Commands:**__```CSS\n" + cmds + "```")

# Manage Bot Server
@bot.command()
async def botserver(ctx, *args): # (WARNING: Do NOT edit this bot command function unless you know what you're doing)
    if len(args) == 0 or int(ctx.author.id) not in DEVS:
        return -1
    cmd = args[0].lower()
    if cmd == "stop":
        await ctx.send(f"```{MSA} MSA Bot stopped!```"); await asyncio.sleep(1)
        os.popen("sudo systemctl stop botd"); exit()
    elif cmd == "restart":
        await ctx.send(f"```{MSA} MSA Bot restarted!```"); await asyncio.sleep(1)
        os.popen("sudo systemctl restart botd")
    elif cmd == "status":
        with open("bot_stats.yaml") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            await ctx.send(f"```yaml\n{data}```")
    elif cmd == "update":
        if "db" in args:
            p = Popen("./update_db.sh"); await asyncio.sleep(1)
            await ctx.send(f"```{MSA} MSA Bot database update system triggered! (~ 30 minute runtime)```")
            while p.poll() is None:
                time.sleep(60)
            await ctx.send(f"```{MSA} MSA Bot database update complete!```")
            return 0
        await ctx.send(f"```{MSA} MSA Bot CI/CD system triggered!```"); await asyncio.sleep(1)
        out = os.popen("sudo ./update_bot.sh"); print("CLI OUTPUT:", out.read())
    else:
        await ctx.send(f"```Error: Command does not exist!```")

@bot.command()
async def herotime(ctx, *args): # It's Ben 10!
    choice = ''
    if len(args) > 0:
        choice = " ".join(args)
    alien_form = ben_10(choice)
    await ctx.send(ctx.author.mention + f" has transformed into **{alien_form}**!")

@bot.command()
async def showroles(ctx, *args): # Show role-selection roles
    is_admin = check_admin(ctx)
    if not is_admin:
        return -1
    with open("role_selection.txt", 'r', encoding="utf-8") as f:
        text = f.read()
        if text == '':
            await ctx.send("`Role selections empty`")
        else:
            await ctx.send(text)

@bot.command()
async def addrole(ctx, *args): # Add role-selection role
    is_admin = check_admin(ctx)
    if not is_admin:
        return -1
    if len(args) == 0:
        await ctx.send(f"`/addrole <emoji> <@Role>`\n"
                       "`/addrole <emoji> <@Bro-Role> <@Sis-Role>`")
        return 0
    emoji = args[0]; role = args[1].replace("<@&", '').strip('>')
    if len(args) == 3:
        extra = args[2].replace("<@&", '').strip('>')
    else:
        extra = 0
    with open("role_selection.txt", 'r+', encoding="utf-8") as f:
        lines = f.readlines()
        entry = f"{extra} {emoji} {role}\n"
        if entry not in lines:
            f.write(entry)
        else:
            await ctx.send(f"`Role Reaction already exists!`", delete_after=25)
            return -1
    update_role_select()
    await ctx.send(f"`Role Reaction Added!`", delete_after=25)

@bot.command()
async def deleterole(ctx, *args): # Remove role-selection role
    is_admin = check_admin(ctx)
    if not is_admin:
        return -1
    if len(args) != 1:
        await ctx.send(f"`/deleterole <emoji>`\n")
        return 0
    emoji = args[0]
    if edit_file("role_selection.txt", emoji, exact=False):
        await ctx.send(f"`Role Reaction Removed!`", delete_after=25)
    else:
        await ctx.send(f"`Role Reaction does not exist!`", delete_after=25)

# Add user to server officially
@bot.command()
async def add(ctx, *args):
   is_admin = check_admin(ctx, add_on="Representative")
   if not is_admin:
      return -1
   if len(args) <= 1: # If user already has full name
      user_id = re.search(r"\d{5,}", args[0])
      if user_id:
         guild = bot.get_guild(SERVER_ID)
         member = guild.get_member(int(user_id.group()))
         sibling, rm_role = get_sibling_role(member)
         if '@' in member.nick:
            await ctx.send("**Please don't leave the user's nickname as email!**", delete_after=25)
            return -1
         role = get(
         bot.get_guild(SERVER_ID).roles, name=f"{sibling}")
         await member.add_roles(role)
         await member.remove_roles(rm_role)
         siblinghood = get_sibling(sibling)
         channel = bot.get_channel(siblinghood.general)
         await channel.send("<@!" + user_id.group() + f"> *has* ***officially*** *joined the {MSA} MSA Discord! Welcome your " + sibling + "!*")
      else:
         await ctx.send("**Invalid command! Please make sure you're @ing the user.**", delete_after=25)
         await ctx.delete(delay=300)
   else: # If you want to manually nickname user
      user_id = re.search(r"\d{5,}", args[0])
      if user_id:
         guild = bot.get_guild(SERVER_ID)
         member = guild.get_member(int(user_id.group()))
         sibling, rm_role = get_sibling_role(member)
         role = get(bot.get_guild(SERVER_ID).roles, name=f"{sibling}")
         nName = get_name(member.nick) # get member.name if nick is None
         try:
            if nName != None:
               await member.edit(nick=str(nName))
            else:
               new_name = args[1:]; nName = ''
               for name in new_name:
                    nName += name.capitalize() + ' '
               await member.edit(nick=str(nName).strip(' '))
         except errors.Forbidden:
            print("Success!\n", nName)
         await member.add_roles(role)
         await member.remove_roles(rm_role)
         siblinghood = get_sibling(sibling)
         channel = bot.get_channel(siblinghood.general)
         await channel.send("<@!" + user_id.group() + f"> *has* ***officially*** *joined the {MSA} MSA Discord! Welcome your fellow " + sibling + "!*")
      else:
         await ctx.send("**Invalid command! Please make sure you're @ing the user.**", delete_after=25)
         await ctx.message.delete(delay=300)

# Set timer command
@bot.command()
async def timer(ctx, *args):
   is_not_a_num = re.search(r"^(\d{2,4})$", ''.join(args))
   if is_not_a_num or len(args) != 2: # Make sure 2 arguments were passed
      await ctx.send("***Invalid Command! Must include hours followed by minutes!***\n (ex: `/timer 0 30`)")
   else:
      eta = ((int(args[0]) * 60) * 60) + (int(args[1]) * 60)
      await ctx.send(f"You will be notified in **" + args[0] + "** hour(s) & **" + args[1] + "** minute(s)!")
      await asyncio.sleep(eta)
      await ctx.send(ctx.author.mention + " **ALERT! YOUR TIMER HAS RUN OUT! DO WHAT YOU MUST!**")


# Sisters Exclusive Commands
##async def SIS_EXAMPLE_CMD(ctx):
##    if check_gender(ctx.author) == "Sister":
##        print("Sisters command executed!")


# Brothers Exclusive Commands
##async def BRO_EXAMPLE_CMD(ctx):
##    if check_gender(ctx.author) == "Brother":
##        print("Brothers command executed!")



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error
