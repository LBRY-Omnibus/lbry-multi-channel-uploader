import json 
import os
import sqlite3

progPath = os.path.dirname(os.path.abspath(__file__))

global dataBase, curr
dataBase = sqlite3.connect(progPath + '/data/database/db.s3db')
curr = dataBase.cursor()

with open('./script.json', 'r') as jsonRaw:
    jsonDat =  json.load(jsonRaw)

channelName = 'vidya'
channelDat = curr.execute(f"""SELECT * FROM channels WHERE channel_name = '{channelName}' """).fetchall()
contentTags = curr.execute(f"""SELECT tag FROM content_tag WHERE channel_name = '{channelName}' """).fetchall()
contentTags = [a[0] for a in contentTags]
fundingAccounts = curr.execute(f"""SELECT account_id FROM funding_account WHERE channel_name = '{channelName}' """).fetchall()
fundingAccounts = [a[0] for a in fundingAccounts]
contentFolders = curr.execute(f"""SELECT folder FROM content_folder WHERE channel_name = '{channelName}' """).fetchall()
contentFolders = [a[0] for a in contentFolders]

for a in jsonDat:
    if a == 'upload':
        if 'in' in list(jsonDat[a][1])[0]:
            query = "SELECT * FROM channels WHERE"
            for b in jsonDat[a][1]['in']:
                if type(b) == dict and (dictHeader := list(b)[0]) in ['channel_name', 'channel_id', 'wallet_name', 'acount_id', 'upload_fee']:
                    query += f" {dictHeader} = '{b[dictHeader]}'"
                elif type(b) == str and b in ['OR', 'AND', 'OR NOT', 'AND NOT']:
                    query += f" {b}"
        else:
            query = "SELECT * FROM channels"

        channelDat = curr.execute(query).fetchall()

        #contentTags = curr.execute(f"""SELECT tag FROM content_tag WHERE channel_name = '{channelName}' """).fetchall()
        #contentTags = [a[0] for a in contentTags]
        #fundingAccounts = curr.execute(f"""SELECT account_id FROM funding_account WHERE channel_name = '{channelName}' """).fetchall()
        #fundingAccounts = [a[0] for a in fundingAccounts]
        #contentFolders = curr.execute(f"""SELECT folder FROM content_folder WHERE channel_name = '{channelName}' """).fetchall()
        #contentFolders = [a[0] for a in contentFolders]

        if 'where' in list(jsonDat[a][1])[0]:
            for b in jsonDat[a][1]['where']:
                pass
            withResult = curr.execute(query).fetchall()
            print(withResult)