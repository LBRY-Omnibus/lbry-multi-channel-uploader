from imgurpython import ImgurClient
from requests.api import request
import requests
import json
import os
import sqlite3
import time

progPath = os.path.dirname(os.path.abspath(__file__))
dataBase = sqlite3.connect(progPath + '/db.s3db')
curr = dataBase.cursor()

progPath = os.path.dirname(os.path.abspath(__file__))

#grabsbalance and unlocks supports is balance is insuficient
def checkBal() -> str:
    wallet = requests.post("http://localhost:5279", json={"method": "wallet_balance", "params": {"wallet_id": "nsfw"}}).json()
    walletBal = float(wallet['result']['available'])

    if(walletBal >= 1):
        supports = requests.post("http://localhost:5279", json={"method": "support_list", "params": {"wallet_id": "nsfw", "page_size": 50}}).json()
        print(supports)
        for a in supports["result"]["items"]:
            request.post("http://localhost:5279", json={"method": "support_abandon", "params": {"wallet_id": "nsfw", "txid": a['txid']}}).json()
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
        curr.execute(f"""INSERT INTO a(files) VALUES('{a}')""")
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
     os.system(f"""ffmpeg -i "{video}" -fs 3M -vf "scale=640:-2" -y {progPath + "/temp/thumbnailTemp.gif"}""")
     print(progPath + "/temp/thumbnailTemp.gif")
     return(progPath + "/temp/thumbnailTemp.gif")

#uploads video to lbry
def uploadToLBRY(channels, channel, file) -> str:
    channelInfo = channels[channel]
    filePath = channelInfo['content_folder'] + '/' + file
    thumbnail = imgurUploader(thumbnailCreator(filePath))
    upload = requests.post("http://localhost:5279", json={"method": "publish", "params": {"name": os.path.splitext(os.path.basename(file))[0].replace(' ', ''), 
                                "bid": channelInfo['upload_fee'], "file_path": filePath, "title": file, "tags": channelInfo['content_tags'], 
                                "thumbnail_url": thumbnail, "channel_id": channelInfo['channel_id'],
                                "account_id": "bQnAHW3yQAMKrzMUrzevb6zPFDtHABhmXr", "wallet_id": "nsfw", "funding_account_ids": ["bQnAHW3yQAMKrzMUrzevb6zPFDtHABhmXr"]}}).json()
    print(upload)
    insertNewUpload(channel, file, (upload["result"]["outputs"][0]["permanent_url"]))
    return(upload['result']['outputs'][0]['permanent_url'])

if __name__ == "__main__":
    channels = getChannelList()
    for a in channels:
        print(a)
        fileList = (os.listdir(channels[a]['content_folder']))
        notUploaded = getNotUploaded(a, fileList)
        print(notUploaded)
        for c in notUploaded[0:1]:
            url = uploadToLBRY(channels, a, c)
            print(url)
    dataBase.close()