#changes the location of a folder across the whole program
import sqlite3
import requests
import os 
import json

progPath = os.path.dirname(os.path.abspath(__file__))

oldFolder = 'D:/'
newFolder = 'E:/'

#changes in db
dataBase = sqlite3.connect(progPath + '/db.s3db')
curr = dataBase.cursor()
allFiles = list(b[0] for b in curr.execute(f""" SELECT file FROM uploaded """).fetchall())
for a in range(0, len(allFiles)):
    allFiles[a] = [os.path.dirname(allFiles[a]), os.path.basename(allFiles[a])]
for b in range(0, len(allFiles)):
    if allFiles[b][0] == oldFolder:
        curr.execute(f""" UPDATE uploaded SET file = "{newFolder + '/' + allFiles[b][1]}" WHERE file = "{allFiles[b][0] + '/' + allFiles[b][1]}" """)
        allFiles[b][0] == newFolder
dataBase.commit()
dataBase.close()

#changes in json
with open('./channelList.json', 'r') as jsonRaw:
    jsonDat = json.load(jsonRaw)
for a in jsonDat:
    for b in range(0, len(jsonDat[a]['content_folder'])):
        if jsonDat[a]['content_folder'][b] == oldFolder:
            jsonDat[a]['content_folder'][b] = newFolder
with open('./channelList.json', 'w') as jsonRaw:
    json.dump(jsonDat, jsonRaw, indent=4)