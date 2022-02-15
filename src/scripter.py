import json 
import os
import sqlite3

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
            for b in jsonDat[a][1]['in']:
                if type(b) == dict:
                    dictHeader = list(b)[0]
                    #includes channel with given name, id, wallet name, account id, or fee
                    if dictHeader in ['channel_name', 'channel_id', 'wallet_name', 'acount_id', 'upload_fee']:
                        query += f" {dictHeader} = '{b[dictHeader]}'"
                    #includes channel with given folder, tag, ot funding account
                    dictDataField = {'content_folder':'folder', 'content_tag': 'channel_name', 'funding_account':'channel_name'}
                    if dictHeader in list(dictDataField):
                        query += f" channel_name IN (SELECT channel_name FROM {dictHeader} WHERE {dictDataField[dictHeader]} = '{b[dictHeader]}')"
                
                elif type(b) == str and b in ['OR', 'AND', 'OR NOT', 'AND NOT']:
                    query += f" {b}"
        else:
            query = "SELECT * FROM channels"
        channelDat = curr.execute(query).fetchall()
        # -----------------------------------------------------------------------------------------------
        # while 'in' grabs channels if they have the given data,
        # 'where' uses the data for each channel if the conditions say so
        # -----------------------------------------------------------------------------------------------
        if 'in' in list(jsonDat[a][1])[0]:
            pass
            #make soemtime soon please an thank future me