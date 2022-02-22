import json 
import os
import sqlite3
import main
import math
import requests

progPath = os.path.dirname(os.path.abspath(__file__))

dataBase = sqlite3.connect(progPath + '/data/database/db.s3db')
curr = dataBase.cursor()

with open('./script.json', 'r') as jsonRaw:
    jsonDat =  json.load(jsonRaw)
for a in jsonDat:
    if a == 'upload':
        uploadAmmount = 'all'
        channelDat = []
        channelBid = 0
        contentFolders = []
        contentTags = []
        channelUploadAmmount = 0
        channelDatValues = {'wallet_id':[], 'channel_name':[], 'channel_id':[], "page_size":50, "resolve":False, "no_totals":True}
        for uploadCommand in jsonDat[a]:
            uploadCommandDat = jsonDat[a][uploadCommand]
            # -----------------------------------------------------------------------------------------------
            # grabs the max upoload ammount if supplied, 
            # otherwise it defaults to 'all'
            # -----------------------------------------------------------------------------------------------
            if 'upload_ammount' == uploadCommand:
                uploadAmmount = jsonDat[a][uploadCommand]
            # -----------------------------------------------------------------------------------------------
            # add stuff for grabing channels
            # -----------------------------------------------------------------------------------------------
            if uploadCommand == 'wallet_id':
                channelDatValues['wallet_id'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['wallet_id'].append(uploadCommandDat)
            if uploadCommand == 'channel_name':
                channelDatValues['channel_name'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['channel_name'].append(uploadCommandDat)
            if uploadCommand == 'channel_id':
                channelDatValues['channel_id'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['channel_id'].append(uploadCommandDat)

    channelDat = requests.post("http://localhost:5279", json={"method": "channel_list", "params": channelDatValues}).json()
    '''
    if type(uploadAmmount) == str:
        channelUploadAmmount = uploadAmmount
    elif type(uploadAmmount) == int:
        channelUploadAmmount = math.ceil(uploadAmmount/len(channelDat)) if uploadAmmount < len(channelDat) else math.floor(uploadAmmount/len(channelDat))
        # make channelUploadAmount accurate later
    print(channelUploadAmmount)
    returnedUploadAmmount = 0
    '''
    returnedUploadAmmount = main.main(channel, wallet, contentTags, fundingAccounts, contentFolders, channelUploadAmmount)
