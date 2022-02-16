import sqlite3
import os

progPath = os.path.dirname(os.path.abspath(__file__))
dataBase = sqlite3.connect('../src/data/database/db - Copy.s3db')
curr = dataBase.cursor()

for a in list(b[0] for b in curr.execute(f"""SELECT file FROM uploaded""").fetchall()):
    curr.execute(f"""UPDATE uploaded SET file_path = '{os.path.split(a)[0]}', file_name = '{os.path.split(a)[1]}' WHERE file = '{a}' """)

dataBase.commit()
dataBase.close()