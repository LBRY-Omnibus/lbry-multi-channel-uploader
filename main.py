from imgurpython import ImgurClient
from requests.api import request
import requests
import json
import os
import sqlite3
import time
import hashlib
import random


progPath = os.path.dirname(os.path.abspath(__file__))

#grabs balance and unlocks supports is balance is insuficient
def checkBal() -> str:
    print('--waiting to check balance--')
    time.sleep(90)
    wallet = requests.post("http://localhost:5279", json={"method": "wallet_balance", "params": {"wallet_id": "nsfw"}}).json()
    walletBal = float(wallet['result']['available'])

    if(walletBal <= 1):
        print('--unlocking funds--')
        supports = requests.post("http://localhost:5279", json={"method": "support_list", "params": {"wallet_id": "nsfw", "page_size": 50}}).json()
        print(supports)
        for a in supports["result"]["items"]:
            requests.post("http://localhost:5279", json={"method": "support_abandon", "params": {"claim_id": a['claim_id'], "wallet_id": "nsfw"}}).json()
        checkBal()
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
def insertNewUpload(channel, file, url) -> None:
    curr.execute(f"""INSERT INTO uploaded(channel, file, url) VALUES('{channel}', '{file}', '{url}')""")
    dataBase.commit()
    return()

#uploads thumbnail to imgur
def imgurUploader(image) -> str:
    client_id = '30383064d011baa'
    client_secret = '7d80b6d588a7e1b1b7b4f1ced3b83b13b6e51034'
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
def uploadToLBRY(channels, channel, file) -> str:
    channelInfo = channels[channel]
    thumbnail = imgurUploader(thumbnailCreator(file))
    name = str(hashlib.sha256(os.path.splitext(file)[0].encode('utf-8').strip()).hexdigest())[:5] + str(os.path.splitext(os.path.basename(file))[0])
    nameTable = name.maketrans("", "", " !@#$%^&*()_-+=[]:,<.>/?;:'\|")
    name = name.translate(nameTable)
    upload = requests.post("http://localhost:5279", json={"method": "publish", "params": {
                                "name": name, 
                                "bid": channelInfo['upload_fee'], "file_path": file, "title": os.path.splitext(os.path.basename(file))[0], "tags": channelInfo['content_tags'], 
                                "thumbnail_url": thumbnail, "channel_id": channelInfo['channel_id'], "account_id": "bQnAHW3yQAMKrzMUrzevb6zPFDtHABhmXr", "wallet_id": "nsfw", 
                                "funding_account_ids": ["bQnAHW3yQAMKrzMUrzevb6zPFDtHABhmXr", "bPqPneKocvBHye5aRGZE1E2qjKExjKKtYX"]}}).json()
    #print(upload)
    print(upload)
    if 'error' in upload.keys():
        checkBal()
        afterError = uploadToLBRY(channels, channel, file)
        return(afterError)
    else:
        insertNewUpload(channel, file, (upload["result"]["outputs"][0]["permanent_url"]))
        return(upload['result']['outputs'][0]['permanent_url'])

if __name__ == "__main__":
    global dataBase, curr
    for gayloop in range(0,1):
        dataBase = sqlite3.connect(progPath + '/db.s3db')
        curr = dataBase.cursor()
        channels = getChannelList()
        for a in channels:
            print(a)
            #allows for content to be spread across different folders
            fileList = []
            for d in (0, len(channels[a]['content_folder'])-1):
                for (root,dirs,files) in os.walk(channels[a]['content_folder'][d], topdown=True, followlinks=True):
                    #combines root and name together if name does not have !qB in it and adds to list, otherwise add None (e), then removes every none in list (f) 
                    fileList.extend(f for f in [(root.replace('\\', '/') + '/' + e) if '.!qB' not in e else None for e in files] if f)
            notUploaded = getNotUploaded(a, fileList)
            print(notUploaded)
            for c in notUploaded[0:1]:
                url = uploadToLBRY(channels, a, c)
                print(url)
            print("--Sleeping--")
            time.sleep(30) if not len(notUploaded) == 0 else time.sleep(1)
        dataBase.close()
        print("--Finnished Set, Sleeping--")
        time.sleep(30)