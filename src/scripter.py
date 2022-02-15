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
    if a == 'upload':
        if 'in' in list(jsonDat[a][1])[0]:
            query = "SELECT * FROM channels WHERE"
            for b in jsonDat[a][1]['in']:
                if type(b) == dict and (dictHeader := list(b)[0]) in ['channel_name', 'channel_id', 'wallet_name', 'acount_id', 'upload_fee']:
                    query += f" {dictHeader} = '{b[dictHeader]}'"
                elif type(b) == str and b in ['OR', 'AND', 'OR NOT', 'AND NOT']:
                    query += f" {b}"
            withResult = curr.execute(query).fetchall()
            print(withResult)