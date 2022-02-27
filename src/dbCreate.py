import os 
from main import db as dbManager

progPath = os.path.dirname(os.path.abspath(__file__))

def __main():
    global dataBase, curr
    with dbManager('default') as con:
        with con as curr:
            curr.execute(f"""CREATE TABLE IF NOT EXISTS uploaded (wallet TEXT, channel_name TEXT, file_path TEXT, file_name TEXT, url TEXT) """)
            curr.execute(f"""CREATE TABLE IF NOT EXISTS ignore (channel_name TEXT, ignore_location TEXT, ignore TEXT, ignore_type TEXT) """)
            con.commit()

if __name__ == '__main__':
    __main()