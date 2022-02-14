import json 
import os
import sqlite3

progPath = os.path.dirname(os.path.abspath(__file__))

global dataBase, curr
dataBase = sqlite3.connect(progPath + '/data/db.s3db')
curr = dataBase.cursor()

with open('./script.json', 'r') as jsonRaw:
    jsonDat =  json.load(jsonRaw)

for a in jsonDat:
    if 'in' in jsonDat[a][1].keys():
        query = "SELECT * FROM channels WHERE"
        for b in jsonDat[a][1]['in']:
            print(jsonDat[a][1]['in'])
            if type(b) == dict:
                if 'channel' in b.keys():
                    query += f" channel_name = '{b['channel']}'"
                elif 'wallet' in b.keys():
                    query += f" wallet_name = '{b['wallet']}'"
                elif 'account' in b.keys():
                    query += f" account_id = '{b['account']}'"
            elif type(b) == str:
                query += f" {b} "
        print(query)
        withResult = curr.execute(query).fetchall()
        print(withResult)  
            