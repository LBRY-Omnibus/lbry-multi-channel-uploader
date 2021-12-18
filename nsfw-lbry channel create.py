import requests

channelName = input('name of channel:')
bid = input('bid amount:')
channelTitle = input('channel title:')
channelDisc = input('channel discription:')
tags = input('channel tags (seperated by ,):').split(',')
thumbnail = input('channel thumbnail:')

response = requests.post("http://localhost:5279", json={"method": "channel_create", "params": 
        {"name": channelName, "bid": bid, "title": channelTitle, "description": channelDisc, "tags": tags, 
        "thumbnail_url": thumbnail, "account_id": "bQnAHW3yQAMKrzMUrzevb6zPFDtHABhmXr", "wallet_id": "nsfw",
        "funding_account_ids": ["bQnAHW3yQAMKrzMUrzevb6zPFDtHABhmXr"], "preview": False, "blocking": False}}).json()
print(response)
input()

