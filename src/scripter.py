import json 
import os
import main as lbryMain
import math
import requests
import dbCreate

progPath = os.path.dirname(os.path.abspath(__file__))

#for the upload command
def upload(a):
    def upload_ammount() -> None:
        nonlocal uploadAmmount
        uploadAmmount = uploadCommandDat
        return

    def wallet_id() -> None:
        nonlocal channelDatValues
        channelDatValues['wallet_id'] = uploadCommandDat
        return

    def channel_name() -> None:
        nonlocal channelDatValues
        channelDatValues['name'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['name'].append(uploadCommandDat)
        return

    def channel_id() -> None:
        nonlocal channelDatValues
        channelDatValues['claim_id'].extend(uploadCommandDat) if type(uploadCommandDat) == list else channelDatValues['claim_id'].append(uploadCommandDat)
        return

    def funding_accounts() -> None:
        nonlocal fundingAccounts
        fundingAccounts.extend(uploadCommandDat) if type(uploadCommandDat) == list else fundingAccounts.append(uploadCommandDat)
        return

    def folders() -> None:
        nonlocal contentFolders
        contentFolders.extend(uploadCommandDat) if type(uploadCommandDat) == list else contentFolders.append(uploadCommandDat)
        return

    def tags() -> None:
        nonlocal contentTags
        contentTags.extend(uploadCommandDat) if type(uploadCommandDat) == list else contentTags.append(uploadCommandDat)
        return

    def account_id() -> None:
        nonlocal accountId
        accountId = uploadCommandDat
        return

    def bid() -> None:
        nonlocal channelBid
        channelBid += uploadCommandDat
        return

    uploadAmmount = 1
    channelDat = []
    channelBid = 0
    contentFolders = []
    contentTags = []
    channelUploadAmmount = 0
    fundingAccounts = []
    accountId = ''
    channelDatValues = {'wallet_id':'default_wallet', 'name':[], 'claim_id':[], "page_size":50, "resolve":False, "no_totals":True}
    for uploadCommand in a['upload']:
        uploadCommandDat = a['upload'][uploadCommand]
        #find better way to implement this other then eval
        try:
            eval(f"""{uploadCommand}()""")
        except NameError:
            print('command attribute does not exist')
        requests.post("http://localhost:5279", json={"method": "wallet_add", "params": {'wallet_id':channelDatValues['wallet_id']}}).json()
        channelDat = requests.post("http://localhost:5279", json={"method": "channel_list", "params": channelDatValues}).json()['result']['items']
        if type(uploadAmmount) == str:
            channelUploadAmmount = uploadAmmount
        elif type(uploadAmmount) == int:
            channelUploadAmmount = math.ceil(uploadAmmount/len(channelDat)) if uploadAmmount < len(channelDat) else math.floor(uploadAmmount/len(channelDat))
            # make channelUploadAmount accurate later
        returnedUploadAmmount = 0
        for channel in channelDat:
            returnedUploadAmmount = lbryMain.main(channel, channelDatValues['wallet_id'], accountId, contentTags, fundingAccounts, contentFolders, channelBid, channelUploadAmmount+returnedUploadAmmount)


def main(script):
    dbCreate.__main()
    with lbryMain.db('default') as con:
        with con as curr:
            with open(script, 'r') as jsonRaw:
                jsonDat =  json.load(jsonRaw)
            if 'command' in [jsonDat]:
                for a in jsonDat['commands']:
                    # find alt. to eval that doesn't rape speed
                    try:
                        eval(f"""{list(a)[0]}({a})""")
                    except NameError:
                        #should run some more error handling stuff later
                        print("Command does not exist")

if __name__ == '__main__':
    main('./script.json')