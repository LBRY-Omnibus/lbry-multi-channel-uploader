from imgurpython import ImgurClient
import requests
import json
import os
import sqlite3
import time
import hashlib
import gc
import dbCreate

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
    curr.execute(f"""DELETE FROM a WHERE files in (SELECT file FROM uploaded WHERE channel_name = '{channel}')""")
    unUploaded = curr.execute(f"""SELECT files FROM a""").fetchall()
    unUploaded = list(a[0] for a in unUploaded) #one list
    curr.execute(f"""DROP TABLE a""")
    return(unUploaded)

#add uploaded to db
def insertNewUpload(wallet, channel, file, url) -> None:
    curr.execute(f"""INSERT INTO uploaded(wallet, channel_name, file, url) VALUES('{wallet}', '{channel}', '{file}', '{url}')""")
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
def uploadToLBRY(channelName, channelId, walletName, acountId, uploadFee, contentTags, fundingAccounts, file) -> str:
    thumbnail = imgurUploader(thumbnailCreator(file))
    name = str(hashlib.sha256(os.path.splitext(file)[0].encode('utf-8').strip()).hexdigest())[:5] + str(os.path.splitext(os.path.basename(file))[0])
    nameTable = name.maketrans("", "", " !@#$%^&*()_-+=[]:,<.>/?;:'\|")
    name = name.translate(nameTable)
    upload = requests.post("http://localhost:5279", json={"method": "publish", "params": {
                            "name": name, "bid": uploadFee, "file_path": file, "title": os.path.splitext(os.path.basename(file))[0], 
                            "tags": contentTags, "thumbnail_url": thumbnail, "channel_id": channelId, "account_id": acountId, "wallet_id": walletName, 
                            "funding_account_ids": fundingAccounts}}).json()
    print(upload)
    if 'error' in upload.keys():
        checkBal(walletName)
        afterError = uploadToLBRY(channelName, channelId, walletName, acountId, uploadFee, contentTags, fundingAccounts, file)
        return(afterError)
    else:
        insertNewUpload(walletName, channelName, file, (upload["result"]["outputs"][0]["permanent_url"]))
        return(upload['result']['outputs'][0]['permanent_url'])

if __name__ == "__main__":
    global dataBase, curr
    dbCreate.__main()
    dataBase = sqlite3.connect(progPath + '/db.s3db')
    curr = dataBase.cursor()
    channelName = 'vidya'

    channelDat = curr.execute(f"""SELECT * FROM channels WHERE channel_name = '{channelName}' """).fetchall()
    contentTags = curr.execute(f"""SELECT tag FROM content_tag WHERE channel_name = '{channelName}' """).fetchall()
    contentTags = [a[0] for a in contentTags]
    fundingAccounts = curr.execute(f"""SELECT account_id FROM funding_account WHERE channel_name = '{channelName}' """).fetchall()
    fundingAccounts = [a[0] for a in fundingAccounts]
    contentFolders = curr.execute(f"""SELECT folder FROM content_folder WHERE channel_name = '{channelName}' """).fetchall()
    contentFolders = [a[0] for a in contentFolders]

    addWallet = requests.post("http://localhost:5279", json={"method": "wallet_add", "params": {'wallet_id':channelDat[0][2]}}).json()

    fileList = []
    for d in (0, len(contentFolders)-1):
        for (root,dirs,files) in os.walk(contentFolders[d], topdown=True, followlinks=True):
            ignoreDirs = curr.execute(f"""SELECT ignore_location, ignore, ignore_type FROM ignore WHERE channel_name = '{channelName}' """).fetchall()
            for e in ignoreDirs:
                if e[0] == root:
                    if e[2] == 'dir':
                        dirs[:] = [g for g in dirs if g not in e[0]]
                    if e[2] == 'file':
                        files[:] = [f for f in files if not (e[1] == f and e[2] == 'file')]
            #combines root and name together if name does not have !qB in it and adds to list, otherwise add None (e), then removes every none in list (f) 
            fileList.extend(f for f in [(root.replace('\\', '/') + '/' + e) if '.!qB' not in e else None for e in files] if f)
    notUploaded = getNotUploaded(channelName, fileList)

    url = uploadToLBRY(channelName = channelDat[0][0], channelId = channelDat[0][1], walletName = channelDat[0][2], acountId = channelDat[0][3], uploadFee = channelDat[0][4],
                        contentTags = contentTags, fundingAccounts = fundingAccounts, file = notUploaded[0])

    gc.collect()
    dataBase.close()