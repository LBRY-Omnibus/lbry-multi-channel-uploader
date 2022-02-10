from imgurpython import ImgurClient
import os
def main(image) -> str:
    client_id = '30383064d011baa'
    client_secret = '220dedf34c01f3ce3fd14278819920a3adfec313'
    client = ImgurClient(client_id, client_secret)
    thumbnail = client.upload_from_path(image, config=None, anon=True)
    os.remove(image)
    return(thumbnail['link'])