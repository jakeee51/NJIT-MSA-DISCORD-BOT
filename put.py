import re, time, hashlib, yaml
from config import DB_SECRET
from tools import encrypt, get_total_records
import sqlite3 as sql


# Populate database.db with new data from a data text file
def populate_links(conn, data_file):
   cur = conn.cursor()
   to_db = []
   with open(data_file) as f:
      line = f.readline(); c = 0; thous = '0'
      while line.strip('\n') != '':
         try:
            line = f.readline(); line = line.strip('\n')
         except UnicodeDecodeError:
            with open("bad.txt", 'a') as w:
               w.write(line + '\n')
            continue
         if line == '':
            break
         lst = line.split('\t')
         try:
            sid = re.sub(r"@.+\.edu", '', lst[1])
            email = lst[1]
            names = lst[0].split(',')
         except IndexError: # Ignore non-person records
            print("False record dodged!", lst)
            continue

         if len(names) == 2:
            name = names[-1] + ' ' + names[0]
         elif len(names) == 3:
            if len(names[2]) != 1:
               name = names[-1] + ' ' + names[1] + ' ' + names[0]
            else:
               name = name[1] + ' ' + name[-1] + ' ' + names[0]
         else:
            name = names[0]
         name = re.sub(r"  ", ' ', name).strip(' ')

         if len(sid) > 20 or len(name) > 55 or len(email) > 20: # Ignore professor records
            continue
         # Encryption here
         sid = hashlib.sha1(sid.encode()).hexdigest()
         name = encrypt(name); email = encrypt(email)
         val = (sid, name, email)
         to_db.append(val); c += 1
         if str(c)[0] != thous:
            thous = str(c)[0]
            print("Number of appended records:", c)

   query = "INSERT OR IGNORE INTO Links VALUES(?,?,?)"
   cur.executemany(query, to_db)
   conn.commit()
   print("\nDone!\n", c, "records created!")
   print("Database updated!")
   with open("bot_stats.yaml") as f:
      data = yaml.load(f, Loader=yaml.FullLoader)
   with open("bot_stats.yaml", 'w') as f:
      data["Database Status"] = f":green_circle: (Updated as of {time.ctime()})"
      data["Total Records"] = get_total_records()
      yaml.dump(data, f)

if __name__ == "__main__":
   db_path = "database/database.db"
   conn = sql.connect(db_path)
   populate_links(conn, "loot.txt")
   conn.close()
