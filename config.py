import re
from key import *

class ServerPartition(object):
   #__slots__ = ("name", "wait", "general", "announce")
   def __init__(self, name, wait, general, announce, **kwargs):
      self.__dict__.update(kwargs)
      self.name = name
      self.wait = wait
      self.general = general
      self.announce = announce

class StaticMsg(object):
   __slots__ = ("channel", "message", "reaction")
   def __init__(self, channel, message, reaction):
      self.channel = channel
      self.message = message
      self.reaction = reaction

__bro_options = {"role_select": 756318101880176752}
__sis_options = {"role_select": 750886997874311179}

# Update the role-selection listener
def update_role_select():
   with open("role_selection.txt", encoding="utf-8") as f:
      lines = f.readlines()
      for line in lines:
         extra, emote, role = line.split(' ')
         if extra == '0' and emote not in ROLE_EMOJIS:
            ROLE_EMOJIS[emote] = int(role)
         elif extra != 0 and \
              emote not in SPLIT_ROLES_EMOJIS[BROTHERS.role_select] or \
              emote not in SPLIT_ROLES_EMOJIS[SISTERS.role_select]:
            SPLIT_ROLES_EMOJIS[BROTHERS.role_select][emote[0]] = int(role)
            SPLIT_ROLES_EMOJIS[SISTERS.role_select][emote[0]] = int(extra)


# Set all global variables
BROTHERS = ServerPartition("Brother", 748745649746477086,
                  631090067963772931, 687402472586870849,
                  **__bro_options)
SISTERS = ServerPartition("Sister", 748761869480624158,
                 748762901531066458, 748764105686384650,
                 **__sis_options)
TEST_MODE = False; ENV = ENV; MSA = "NJIT"
EMAIL = "noreply.njitmsa@gmail.com"
VERIFY_SITE = "https://VerificationSystem.njitmsa.repl.co"
BOT = os.getenv("BOT_SECRET", bot_pass())
APP_PASS = os.getenv("EMAIL_SECRET", email_pass())
SP = os.getenv("SECRET_PASS", secret_pass())
DB_SECRET = re.sub(r"\\n", '\n', os.getenv("DB_SECRET", db_pass()))
ENCRYPT_KEY = re.sub(r"\\n", '\n', os.getenv("PUBLIC_KEY", pub_pass()))
DB_PATH = "database/database.db"
VERIFY_ID = 688625250832744449
SERVER_ID = 630888887375364126
ROLE_EMOJIS = {"\U0001f9d5": 750931950964965506,
               "\N{BABY}": 750922989972750337,
               "\N{GIRL}": 750923173956026438,
               "\N{WOMAN}": 750923497101983795,
               "\N{OLDER WOMAN}": 750923619634249740,
               "\N{OPEN BOOK}": 762052942302937111,
               "\U0001f4af": 778401907713638460}
SPLIT_ROLES_EMOJIS = {BROTHERS.role_select: {},
                      SISTERS.role_select: {}}
DEVS = [233691753922691072, 423584353055146004, 351438119926628354,
        496079190475538461, 397082457179947029, 761123575021174784,
        326389855712051201]
os.chdir(CWD) # Return to original directory
update_role_select() # Update the role-selection listener upon startup

'''
Notes:
- Create Brother/Sister roles role
- Create #verify chat
- Enable Developer Mode
  Copy ID's:
  - Right click on Server Name
  - Right click on #verify chat
  - Right click on #general chat
- Make @everyone role only able to talk in #verify chat
'''
