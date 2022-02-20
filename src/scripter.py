import json 
import os
import sqlite3
import main
import math

progPath = os.path.dirname(os.path.abspath(__file__))

dataBase = sqlite3.connect(progPath + '/data/database/db.s3db')
curr = dataBase.cursor()

with open('./script.json', 'r') as jsonRaw:
    jsonDat =  json.load(jsonRaw)
for a in jsonDat:
    if a == 'upload':
        uploadAmmount = 'all'
        inQuery = "SELECT * FROM channels"
        contentTagQueryApendix = ""
        fundingAccountQueryApendix = ""
        contentFoldersQueryApendix = ""
        for uploadCommandNum in range(0, len(jsonDat[a]), 1):
            uploadCommand = list(jsonDat[a][uploadCommandNum])[0]
            print(uploadCommand)
            # -----------------------------------------------------------------------------------------------
            # grabs the max upoload ammount if supplied, 
            # otherwise it defaults to 'all'
            # -----------------------------------------------------------------------------------------------
            if 'upload_ammount' == uploadCommand:
                uploadAmmount = jsonDat[a][uploadCommandNum]['upload_ammount']
            # -----------------------------------------------------------------------------------------------
            # 'in' grabs channels if they have the given data,
            # the channels returned are used later for 'where' and uploading when they are eventually looped over
            # if in is not suplied in the script then it defaults to all channels
            # -----------------------------------------------------------------------------------------------
            if 'in' == uploadCommand:
                inQuery += ' WHERE'
                arguments = jsonDat[a][uploadCommandNum]['in']
                for c,b in enumerate(arguments):
                    #if the datatype is a dict then treat it as a argument and interprit 
                    if type(b) == dict:
                        dictHeader = list(b)[0]
                        if dictHeader in ['channel_name', 'channel_id', 'wallet_name', 'acount_id', 'upload_fee']:
                            inQuery += f" {dictHeader} = '{b[dictHeader]}'"
                        dictDataField = {'content_folder':'folder', 'content_tag': 'channel_name', 'funding_account':'channel_name'}
                        if dictHeader in list(dictDataField):
                            inQuery += f" channel_name IN (SELECT channel_name FROM {dictHeader} WHERE {dictDataField[dictHeader]} = '{b[dictHeader]}')"
                        # if a modfifier (AND, OR, etc) is not given next and not at the end add AND
                        if c+1 <= len(arguments)-1:
                            if not type(arguments[c+1]) == str:
                                inQuery += " AND"
                    # if the datatype is string and in the list of operators then add the string as and operator
                    elif type(b) == str and b in ['OR', 'AND', 'OR NOT', 'AND NOT']:
                        inQuery += f" {b}"
            print(inQuery)
            # -----------------------------------------------------------------------------------------------
            # 'remove' removes any values from the queries (exclude given data)
            # -----------------------------------------------------------------------------------------------
            if 'remove' == uploadCommand:
                arguments = jsonDat[a][uploadCommandNum]['remove']
                for c,b in enumerate(arguments):
                    if type(b) == dict:
                        dictHeader = list(b)[0]
                        print(c)
                        #add modifiers to queries
                        if dictHeader == 'content_tags':
                            contentTagQueryApendix += f" AND tag <> '{b[dictHeader]}'"
                        elif dictHeader == 'funding_account':
                            fundingAccountQueryApendix += f" AND account_id <> '{b[dictHeader]}'"
                        elif dictHeader == 'content_folder':
                            contentTagQueryApendix += f" AND folder <> '{b[dictHeader]}'"
    #run querys
    channelDat = curr.execute(inQuery).fetchall()
    if type(uploadAmmount) == str:
        channelUploadAmmount = uploadAmmount
    elif type(uploadAmmount) == int:
        channelUploadAmmount = math.ceil(uploadAmmount/len(channelDat)) if uploadAmmount < len(channelDat) else math.floor(uploadAmmount/len(channelDat))
        # make channelUploadAmount accurate later
    print(channelUploadAmmount)
    returnedUploadAmmount = 0
    for channel in channelDat:
        contentTags = curr.execute(f"""SELECT tag FROM content_tag WHERE channel_name = '{channel[0]}'{contentTagQueryApendix} """).fetchall()
        contentTags = [a[0] for a in contentTags]
        fundingAccounts = curr.execute(f"""SELECT account_id FROM funding_account WHERE channel_name = '{channel[0]}'{fundingAccountQueryApendix} """).fetchall()
        fundingAccounts = [a[0] for a in fundingAccounts]
        contentFolders = curr.execute(f"""SELECT folder FROM content_folder WHERE channel_name = '{channel[0]}'{contentFoldersQueryApendix} """).fetchall()
        contentFolders = [a[0] for a in contentFolders]
        returnedUploadAmmount = main.main(channel, contentTags, fundingAccounts, contentFolders, channelUploadAmmount+returnedUploadAmmount)