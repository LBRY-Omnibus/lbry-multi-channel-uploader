from imgurpython import ImgurClient
import requests
import json
import os
import sqlite3
import time
import hashlib
import gc


progPath = os.path.dirname(os.path.abspath(__file__))

#grabs balance and unlocks supports is balance is insuficient
def checkBal(wallet) -> str:
    print('--waiting to check balance--')
    time.sleep(90)
    wallet = requests.post("http://localhost:5279", json={"method": "wallet_balance", "params": {"wallet_id": wallet}}).json()
    walletBal = float(wallet['result']['available'])
    print(walletBal)

    if(walletBal <= 1):
        print('--unlocking funds--')
        supports = requests.post("http://localhost:5279", json={"method": "support_list", "params": {"wallet_id": wallet, "page_size": 50}}).json()
        print(supports)
        for a in supports["result"]["items"]:
            requests.post("http://localhost:5279", json={"method": "support_abandon", "params": {"claim_id": a['claim_id'], "wallet_id": wallet}}).json()
        #checkBal(wallet)
    else:
        return(walletBal)
    return(walletBal)

#grabs channel list info
def getChannelList() -> dict:
    with open('./channelList.json', 'r') as jsonRaw:
        return json.load(jsonRaw)

#grabs what hasn't been uploaded under a channel from a list of all files
def getNotUploaded(channel, files) -> list:
    curr.execute(f"""CREATE TEMP TABLE a(files TEXT)""")
    for a in files: #hack to insert list that's slow af
        curr.execute(f"""INSERT INTO a(files) VALUES("{a}")""")
    curr.execute(f"""DELETE FROM a WHERE files in (SELECT file FROM uploaded WHERE channel = '{channel}')""")
    unUploaded = curr.execute(f"""SELECT files FROM a""").fetchall()
    unUploaded = list(a[0] for a in unUploaded) #one list
    curr.execute(f"""DROP TABLE a""")
    return(unUploaded)

#add uploaded to db
def insertNewUpload(wallet, channel, file, url) -> None:
    curr.execute(f"""INSERT INTO uploaded(wallet, channel, file, url) VALUES('{wallet}', '{channel}', '{file}', '{url}')""")
    dataBase.commit()
    return()

#uploads thumbnail to imgur
def imgurUploader(image) -> str:
    client_id = '30383064d011baa'
    client_secret = '220dedf34c01f3ce3fd14278819920a3adfec313'
    client = ImgurClient(client_id, client_secret)
    thumbnail = client.upload_from_path(image, config=None, anon=True)
    print(thumbnail['link'])
    return(thumbnail['link'])

#creates animated thumbnail off video
def thumbnailCreator(video) -> str:
     os.system(f"""ffmpeg -i "{video}" -fs 3M -vf "scale=640:-2" -y "{progPath + '/temp/thumbnailTemp.gif'}" """)
     print(progPath + "/temp/thumbnailTemp.gif")
     return(progPath + "/temp/thumbnailTemp.gif")

#uploads video to lbry
def uploadToLBRY(wallet, channels, channel, file, funding_account_ids, account_id) -> str:
    channelInfo = channels[channel]
    thumbnail = imgurUploader(thumbnailCreator(file))
    name = str(hashlib.sha256(os.path.splitext(file)[0].encode('utf-8').strip()).hexdigest())[:5] + str(os.path.splitext(os.path.basename(file))[0])
    nameTable = name.maketrans("", "", " !@#$%^&*()_-+=[]:,<.>/?;:'\|")
    name = name.translate(nameTable)
    upload = requests.post("http://localhost:5279", json={"method": "publish", "params": {
                                "name": name, 
                                "bid": channelInfo['upload_fee'], "file_path": file, "title": os.path.splitext(os.path.basename(file))[0], "tags": channelInfo['content_tags'], 
                                "thumbnail_url": thumbnail, "channel_id": channelInfo['channel_id'], "account_id": account_id, "wallet_id": wallet, 
                                "funding_account_ids": funding_account_ids}}).json()
    print(upload)
    if 'error' in upload.keys():
        checkBal(wallet)
        afterError = uploadToLBRY(channels, channel, file)
        return(afterError)
    else:
        insertNewUpload(wallet, channel, file, (upload["result"]["outputs"][0]["permanent_url"]))
        return(upload['result']['outputs'][0]['permanent_url'])

if __name__ == "__main__":
    global dataBase, curr
    for gayloop in range(0,1): #shit hack for making bad code run once 
        dataBase = sqlite3.connect(progPath + '/db.s3db')
        curr = dataBase.cursor()
        lbryData = getChannelList()
        for wallet in lbryData:
            addWallet = requests.post("http://localhost:5279", json={"method": "wallet_add", "params": {'wallet_id':wallet}}).json()
            for channel in lbryData[wallet]:
                print(channel)
                #allows for content to be spread across different folders
                fileList = []
                for d in (0, len(lbryData[wallet][channel]['content_folder'])-1):
                    for (root,dirs,files) in os.walk(lbryData[wallet][channel]['content_folder'][d], topdown=True, followlinks=True):
                        if "ignore" in lbryData[wallet][channel].keys():
                            dirs[:] = [g for g in dirs if g not in lbryData[wallet][channel]['ignore']]
                        #combines root and name together if name does not have !qB in it and adds to list, otherwise add None (e), then removes every none in list (f) 
                        fileList.extend(f for f in [(root.replace('\\', '/') + '/' + e) if '.!qB' not in e else None for e in files] if f)
                notUploaded = getNotUploaded(channel, fileList)
                print(notUploaded)
                for c in notUploaded[0:1]:
                    url = uploadToLBRY(wallet, lbryData[wallet], channel, c, lbryData[wallet][channel]['funding_account_ids'], lbryData[wallet][channel]['account_id'])
                    print(url)
                print("--Sleeping--")
                time.sleep(30) if not len(notUploaded) == 0 else time.sleep(1)
            if not wallet == "default_wallet":
                removeWallet = requests.post("http://localhost:5279", json={"method": "wallet_remove", "params": {'wallet_id':wallet}}).json()
            gc.collect()
        dataBase.close()
        print("--Finnished Set, Sleeping--")
        time.sleep(30)