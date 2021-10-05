import asyncio, aiohttp
import re, os, time, smtplib, hashlib, urllib.request
import sqlite3 as sql
from random import randint
from email.message import EmailMessage
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from config import *
# (Note: All variables not declared probably came from config.py)


#If email treated as spam:
 #https://support.google.com/mail/contact/bulk_send_new?rd=1


DB_CONN = sql.connect(DB_PATH)
KEY = RSA.import_key(DB_SECRET.encode("ascii"), SP) # Just you try and get it :D
BEN_10 = ["Heatblast", "Wildmutt", "Diamondhead", "XLR8", "Grey Matter",
          "Four Arms", "Stinkfly", "Ripjaws", "Upgrade", "Ghostfreak",
          "Cannonbolt", "Ditto", "Way Big", "Upchuck",
          "Wildvine", "Alien X", "Echo Echo", "Brainstorm", "Swampfire",
          "Humongousaur", "Jetray", "Big Chill", "Chromastone", "Goop",
          "Spidermonkey", "Rath", "Nanomech"]
SIKE = {'@':'a', '!': 'i', '1': 'i', '5': 's',
        '3': 'e', '0': 'o', 'l': 'i'}
CURSES = ["retard", "fuck", "shit", "ass",
          "pussy", "fucker", "dick", "nigger",
          "bitch", "nigg", "damn", "prick",
          "nigga", "hoe", "siut", "whore",
          "cunt", "dickhead", "isis", "taliban",
          "extremist", "terrorist"]

# Remove a line from a file based on value
def edit_file(file, value, exact=True):
    with open(file, 'r+', encoding="utf-8") as f:
        lines = f.readlines()
        f.seek(0); found = False
        if exact == True:
            for line in lines:
                line = line.strip('\n')
                if str(line).lower() != str(value).lower():
                    f.write(line + '\n')
                else:
                    found = True
        else:
            for line in lines:
                line = line.strip('\n')
                if str(value).lower() not in str(line).lower() :
                    f.write(line + '\n')
                else:
                    found = True
        f.truncate()
        return found

# Return 4-digit verification code string after sending email
def send_email(addr: str, gender='', test=False) -> str:
    sCode = f"{randint(0,9)}{randint(0,9)}{randint(0,9)}{randint(0,9)}"
    verify_link = f"{VERIFY_SITE}/verified/{sCode}/{gender}"
    verify_btn = f'<a class="button" type="button" href="{verify_link}" target="_blank">VERIFY!</a>'
    style_btn = """<head><style>
                    .button {
                        font-size: 14px;
                        text-decoration: none;
                        background-color:#FF0000;
                        color: #FFFFFF;
                        border-radius: 2px;
                        border: 1px solid #000000;
                        font-family: Helvetica, Arial, sans-serif;
                        font-weight: bold;
                        padding: 8px 12px;
                    }
                    .button:hover {
                        background-color:#FF4500
                    }
                  </style></head>"""
    html = f"""<html>{style_btn}<body>
            <b>Your verification link to join the chat is below:<b><br><br>
            <a class="button" type="button" href="{verify_link}" target="_blank">VERIFY!</a><br>
            <h4>{verify_link}</h4><br>
            Please click this link to join the {MSA} Discord. This link will expire in 15 minutes.
            </body></html>"""
    if not test:
        msg = EmailMessage()
        msg.set_content(html, subtype="html")
        msg["Subject"] = f"Verification Code for {MSA} MSA Discord"
        msg["From"] = EMAIL
        msg["To"] = addr
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(EMAIL,
                    APP_PASS)
            s.send_message(msg)
    else:
        print(sCode)
    return sCode

# SQL Query Function
def sqlite_query(query, args=(), one=False):
   cur = DB_CONN.cursor()
   cur = DB_CONN.execute(query, args); DB_CONN.commit()
   rv = [dict((cur.description[idx][0], value)
              for idx, value in enumerate(row)) for row in cur.fetchall()]
   return (rv[0] if rv else None) if one else rv

# Print SQL sample of records & return total records
def get_total_records() -> int:
   records = 0
   for row in sqlite_query(f"SELECT * FROM Links"):
      records += 1
   return records

# Encrypt msg string
def encrypt(msg):
    cipher = PKCS1_OAEP.new(KEY.publickey())
    cipher_text = cipher.encrypt(msg.encode())
    return cipher_text

# Decrypt cipher text
def decrypt(cipher_text):
    cipher = PKCS1_OAEP.new(KEY)
    decrypted_text = cipher.decrypt(cipher_text)
    return decrypted_text.decode()

# Return full name string based on email
def get_name(addr: str) -> str:
    sid = re.sub(r"@.+\.", '', str(addr))
    sid = sid.replace("edu", '')
    hashed_sid = hashlib.sha1(sid.encode()).hexdigest()
    query = f"SELECT full_name FROM Links WHERE sid=?"
    result = sqlite_query(query, (hashed_sid,), one=True)
    if result != None:
        full_name = result["full_name"]
        return decrypt(full_name)

# Check if message has curse word
def curse_check(msg: str) -> bool:
    msg = msg.replace('l', 'i')
    wordCheck = ''
    for i in range(len(msg)):
        char = msg[i]
        if char in SIKE:
            char = SIKE[char]
        wordCheck += char
        wordCheck = wordCheck.strip(' ')
        if wordCheck in CURSES:
            try:
                if msg[i+1] != char or msg[i+1] != ' ':
                    wordCheck = ''
                    continue
            except IndexError:
                pass
            return True
    for curse in CURSES:
        if re.search(fr"\b{curse}\b", msg):
            return True
    return False

# Return gender based on user
def check_gender(user):
    roles = user.roles
    for role in roles:
        if role.name == "Brother" or role.name == "Sister":
            return role.name

# Return true if user is admin or another role
def check_admin(msg, add_on=''):
    roles = msg.author.roles
    for role in roles:
        if role.name == "Admin" or "Shura" in role.name:
            return True
        if role.name == add_on:
            return True
    return False

# Return random Ben 10 alien
def ben_10(choice=''):
    choice = choice.strip(' '); alien_form = ''
    if choice == '':
        idx = randint(0,28)
        alien_form = BEN_10[idx]
    else:
        for alien in BEN_10:
            if alien.lower() in choice.lower():
                got = randint(1,3)
                if got == 1:
                    alien_form = alien; break
                else:
                    ignore = BEN_10.index(alien)
                    idx = randint(0,26)
                    temp = BEN_10[:ignore] + BEN_10[ignore+1:]
                    alien_form = temp[idx]; break
        if alien_form == '':
            idx = randint(0,27)
            alien_form = BEN_10[idx]
    return alien_form

# Retrieve role for those in waiting room
def get_sibling_role(member):
    roles = member.roles; ret = None
    for role in roles:
        if role.name == "Brothers Waiting Room":
            ret = ("Brother", role); break
        elif role.name == "Sisters Waiting Room":
            ret = ("Sister", role); break
    return ret

# Return sibling global object based on gender
def get_sibling(sibling):
    if sibling == "Brother":
        return BROTHERS
    else:
        return SISTERS

# Return announcement channel id while listening to announcements/events
def listen_announce(msg):
    if msg.channel.id == BROTHERS.announce:
        if "@everyone" in msg.content:
            return SISTERS.announce
    elif msg.channel.id == SISTERS.announce:
        if "@everyone" in msg.content:
            return BROTHERS.announce
    else:
        False

# Return role id based on emoji
def listen_role_reaction(emoji, channel):
    role_id = 0
    emoji = emoji.name.encode('unicode-escape')
    emote = re.search(r".+?\\", str(emoji).strip("b'\\"))
    if emote and str(emoji).lower().count('u') > 1:
        emoji = ("\\" + emote.group().strip('\\')).encode()
    for role_emoji in ROLE_EMOJIS:
        if "\\U" not in emoji.decode():
            if emoji.decode() in role_emoji:
                return ROLE_EMOJIS[role_emoji]
        if emoji == role_emoji.encode('unicode-escape'):
            return ROLE_EMOJIS[role_emoji]
    if len(emoji) == 11:
        emoji = emoji[1:].decode('unicode-escape')
    else:
        emoji = emoji.decode('unicode-escape')
    for role_select_channel in SPLIT_ROLES_EMOJIS:
        if role_select_channel == channel:
            return SPLIT_ROLES_EMOJIS[channel][emoji]
    return False

# Parse and return email & join type based on /verify request
def listen_verify(msg):
    if msg.channel.id == VERIFY_ID:
        if msg.content.startswith('/verify'):
            request = re.sub(r"/verify ", '', msg.content.lower())
            join_type = re.search(r"(brothers?|sis(tas?|ters?))", request) or ''
            if join_type:
                ucid = re.sub(fr"{join_type.group()}", '', request).strip(' ')
                if join_type.group()[0] == 'b':
                    join_type = "Brother"
                elif join_type.group()[0] == 's':
                    join_type = "Sister"
                else:
                    join_type = ''
                return ucid, join_type
            return (request, '')

# Listen for 4-digit code in #verify
def listen_code(msg):
    if msg.channel.id == VERIFY_ID:
        return re.search(r"^\d\d\d\d$", msg.content)

# Return sibling global object based on general channel_id
def in_general(channel_id):
    if channel_id == BROTHERS.general:
        return BROTHERS
    elif channel_id == SISTERS.general:
        return SISTERS
    else:
        return False

# Send Post Request
async def send_verify_post(data={}, test=False):
    if test:
        return '1'
    url = VERIFY_SITE + '/verify'
    data_encoded = urllib.parse.urlencode(data)
    data_encoded = data_encoded.encode("ascii")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            result = await resp.text()
    return result

# Constantly check for changes in verify.txt
async def check_verify(record, msg, temp):
    while True:
        with open("verify.txt") as f:
            text = f.read()
            if not re.search(fr"{record}", text):
                break
        await asyncio.sleep(0)
    await msg.delete(); await temp.delete()
