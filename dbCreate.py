import sqlite3
import os 

progPath = os.path.dirname(os.path.abspath(__file__))

def __main():
    global dataBase, curr
    dataBase = sqlite3.connect(progPath + '/db.s3db')
    curr = dataBase.cursor()

    curr.execute(f"""CREATE TABLE IF NOT EXISTS uploaded (wallet TEXT, channel_name TEXT, file TEXT, url TEXT) """)
    curr.execute(f"""CREATE TABLE IF NOT EXISTS ignore (channel_name TEXT, ignore_location TEXT, ignore TEXT, ignore_type TEXT) """)
    curr.execute(f"""CREATE TABLE IF NOT EXISTS funding_accoutnt (channel_name TEXT, account_id TEXT)""")
    curr.execute(f"""CREATE TABLE IF NOT EXISTS content_tag (channel_name TEXT, tag TEXT)""")
    curr.execute(f"""CREATE TABLE IF NOT EXISTS content_folder (channel_name TEXT, folder TEXT)""")
    curr.execute(f"""CREATE TABLE IF NOT EXISTS channels (channel_name TEXT, channel_id TEXT, wallet_name TEXT, account_id TEXT, upload_fee TEXT,
                    PRIMARY KEY (channel_name, channel_id))""")

    dataBase.commit()
    dataBase.close()