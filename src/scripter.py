import json 
import os
import sqlite3
import main
import math
import requests
import dbCreate

progPath = os.path.dirname(os.path.abspath(__file__))
dbCreate.__main()

dataBase = sqlite3.connect(progPath + '/data/database/db.s3db')
curr = dataBase.cursor()

with open('./script.json', 'r') as jsonRaw:
    jsonDat =  json.load(jsonRaw)
for a in range(0, len(jsonDat['commands']), 1):
    if list(jsonDat['commands'][a])[0] == 'upload':
        uploadAmmount = 1
        channelDat = []
        channelBid = 0
        contentFolders = []
        contentTags = []
        channelUploadAmmount = 0
        fundingAccounts = []
        accountId = ''
        channelDatValues = {'wallet_id':'default_wallet', 'name':[], 'claim_id':[], "page_size":50, "resolve":False, "no_totals":True}
        #This whole section needs to be cleaned up and made better in general
        for uploadCommand in jsonDat['commands'][a]['upload']:
            uploadCommandDat = jsonDat['commands'][a]['upload'][uploadCommand]
            # -----------------------------------------------------------------------------------------------
            # grabs the max upoload ammount if supplied, 
            # otherwise it defaults to 1
            # -----------------------------------------------------------------------------------------------
            if 'upload_ammount' == uploadCommand:
                uploadAmmount = uploadCommandDat
            # -----------------------------------------------------------------------------------------------
            # add stuff for grabing channels
            # -----------------------------------------------------------------------------------------------
            if uploadCommand == 'wallet_id':
                channelDatValues['wallet_id'] = uploadCommandDat
            if uploadCommand == 'channel_name':
                channelDatValues['name'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['name'].append(uploadCommandDat)
            if uploadCommand == 'channel_id':
                channelDatValues['claim_id'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['claim_id'].append(uploadCommandDat)
            if uploadCommand == 'funding_accounts':
                fundingAccounts.extend(uploadCommandDat) if type(uploadCommandDat) == list else fundingAccounts.append(uploadCommandDat)
            if uploadCommand == 'folders':
                contentFolders.extend(uploadCommandDat) if type(uploadCommandDat) == list else contentFolders.append(uploadCommandDat)
            if uploadCommand == 'account_id':
                accountId = uploadCommandDat
            if uploadCommand == 'bid':
                channelBid += uploadCommandDat

        requests.post("http://localhost:5279", json={"method": "wallet_add", "params": {'wallet_id':channelDatValues['wallet_id']}}).json()
        channelDat = requests.post("http://localhost:5279", json={"method": "channel_list", "params": channelDatValues}).json()['result']['items']
        
        if type(uploadAmmount) == str:
            channelUploadAmmount = uploadAmmount
        elif type(uploadAmmount) == int:
            channelUploadAmmount = math.ceil(uploadAmmount/len(channelDat)) if uploadAmmount < len(channelDat) else math.floor(uploadAmmount/len(channelDat))
            # make channelUploadAmount accurate later
        returnedUploadAmmount = 0
        for channel in channelDat:
            returnedUploadAmmount = main.main(channel, channelDatValues['wallet_id'], accountId, contentTags, fundingAccounts, contentFolders, channelBid, channelUploadAmmount+returnedUploadAmmount)
