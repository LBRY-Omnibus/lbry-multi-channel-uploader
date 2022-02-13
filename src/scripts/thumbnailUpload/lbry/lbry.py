import os
import requests
import json
import time

def main(image) -> str:
    upload = requests.post("http://localhost:5279", json={"method": "publish", "params": {
                            "name": str(time.time()), "bid": "0.01", "file_path": image}}).json()
    print("https://lbry.tv/$/download/" + upload["result"]["outputs"][0]["name"] + "/" + upload["result"]["outputs"][0]["claim_id"])
    return("https://lbry.tv/$/download/" + upload["result"]["outputs"][0]["name"] + "/" + upload["result"]["outputs"][0]["claim_id"])
