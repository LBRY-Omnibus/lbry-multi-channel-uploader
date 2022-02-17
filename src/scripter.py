import json 
import os
import sqlite3
import main

progPath = os.path.dirname(os.path.abspath(__file__))

global dataBase, curr
dataBase = sqlite3.connect(progPath + '/data/database/db.s3db')
curr = dataBase.cursor()

with open('./script.json', 'r') as jsonRaw:
    jsonDat =  json.load(jsonRaw)
for a in jsonDat:
    if a == 'upload':
        # -----------------------------------------------------------------------------------------------
        # 'in' grabs channels if they have the given data,
        # the channels returned are used later for 'where' and uploading when they are eventually looped over
        # if in is not suplied in the script then it defaults to all channels
        # -----------------------------------------------------------------------------------------------
        if 'in' in list(jsonDat[a][1])[0]:
            query = "SELECT * FROM channels WHERE"
            arguments = jsonDat[a][1]['in']
            for c,b in enumerate(arguments):
                #if the datatype is a dict then treat it as a argument and interprit 
                if type(b) == dict:
                    dictHeader = list(b)[0]
                    if dictHeader in ['channel_name', 'channel_id', 'wallet_name', 'acount_id', 'upload_fee']:
                        query += f" {dictHeader} = '{b[dictHeader]}'"
                    dictDataField = {'content_folder':'folder', 'content_tag': 'channel_name', 'funding_account':'channel_name'}
                    if dictHeader in list(dictDataField):
                        query += f" channel_name IN (SELECT channel_name FROM {dictHeader} WHERE {dictDataField[dictHeader]} = '{b[dictHeader]}')"
                    # if a modfifier (AND, OR, etc) is not given next and not at the end add AND
                    if c+1 <= len(arguments)-1:
                        if not type(arguments[c+1]) == str:
                            query += " AND"
                # if the datatype is string and in the list of operators then add the string as and operator
                elif type(b) == str and b in ['OR', 'AND', 'OR NOT', 'AND NOT']:
                    query += f" {b}"
        else:
            query = "SELECT * FROM channels"
        print(query)
        channelDat = curr.execute(query).fetchall()
        # -----------------------------------------------------------------------------------------------
        # while 'in' grabs channels if they have the given data,
        # 'where' uses the data for each channel if the conditions say so
        # -----------------------------------------------------------------------------------------------
        if 'where' in list(jsonDat[a][1])[0]:
            pass
            #make soemtime soon please an thank future me

    for channel in channelDat:
        uploadAmmount = 1
        contentTags = curr.execute(f"""SELECT tag FROM content_tag WHERE channel_name = '{channel[0]}' """).fetchall()
        contentTags = [a[0] for a in contentTags]
        fundingAccounts = curr.execute(f"""SELECT account_id FROM funding_account WHERE channel_name = '{channel[0]}' """).fetchall()
        fundingAccounts = [a[0] for a in fundingAccounts]
        contentFolders = curr.execute(f"""SELECT folder FROM content_folder WHERE channel_name = '{channel[0]}' """).fetchall()
        contentFolders = [a[0] for a in contentFolders]
        main.main(channel, contentTags, fundingAccounts, contentFolders, uploadAmmount = uploadAmmount)
        