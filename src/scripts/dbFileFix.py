#sqlite shit itself so I had to use this to reset the filename off of the lbry title
import sqlite3
import requests
import os 

progPath = os.path.dirname(os.path.abspath(__file__))
dataBase = sqlite3.connect(progPath + '/db - Copy.s3db')
curr = dataBase.cursor()

for a in list(b[0] for b in curr.execute(f"""SELECT url FROM uploaded""").fetchall()):
    info = requests.post("http://localhost:5279", json={"method": "resolve", "params": {"urls": a}}).json()
    print(info['result'][a]['value']['title'])
    curr.execute(f"""UPDATE uploaded SET file = "{info['result'][a]['value']['title']}" WHERE url = "{a}" """)

dataBase.commit()
dataBase.close()