import sqlite3
import json
import sqlite3
import os 

progPath = os.path.dirname(os.path.abspath(__file__))

def getChannelList() -> dict:
    with open('../channelList.json', 'r') as jsonRaw:
        return json.load(jsonRaw)

if __name__ == "__main__":
    global dataBase, curr
    dataBase = sqlite3.connect('../db - Copy.s3db')
    curr = dataBase.cursor()
    lbryData = getChannelList()

    for wallet in lbryData:
        for channel in lbryData[wallet]:
            curr.execute(f"""INSERT INTO channels(
                channel_name, channel_id, wallet_name, account_id, upload_fee)
                VALUES('{channel}', 
                        '{lbryData[wallet][channel]["channel_id"]}',
                        '{wallet}',
                        '{lbryData[wallet][channel]["account_id"]}',
                        '{lbryData[wallet][channel]["upload_fee"]}')""")
            
            for folder in lbryData[wallet][channel]["content_folder"]:
                curr.execute(f"""INSERT INTO content_folder(
                    channel_name, folder)
                    VALUES('{channel}', '{folder}')""")
            
            for tag in lbryData[wallet][channel]["content_tags"]:
                curr.execute(f"""INSERT INTO content_tag(
                    channel_name, tag)
                    VALUES('{channel}', '{tag}')""")

            for account in lbryData[wallet][channel]["funding_account_ids"]:
                curr.execute(f"""INSERT INTO funding_account(
                    channel_name, account_id)
                    VALUES('{channel}', '{account}')""")
    dataBase.commit()

    dataBase.close()