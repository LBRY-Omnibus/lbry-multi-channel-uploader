import sqlite3
import os 

progPath = os.path.dirname(os.path.abspath(__file__))

def __main():
    global dataBase, curr
    dataBase = sqlite3.connect(progPath + '/data/database/db.s3db')
    curr = dataBase.cursor()

    curr.execute(f"""CREATE TABLE IF NOT EXISTS uploaded (wallet TEXT, channel_name TEXT, file_path TEXT, file_name TEXT, url TEXT) """)
    curr.execute(f"""CREATE TABLE IF NOT EXISTS ignore (channel_name TEXT, ignore_location TEXT, ignore TEXT, ignore_type TEXT) """)

    dataBase.commit()
    dataBase.close()

if __name__ == '__main__':
    __main()