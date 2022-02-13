from imgurpython import ImgurClient
import os
def main(image) -> str:
    client_id = '30383064d011baa'
    client_secret = '842dd4c58e3c57356fb62d431857738e5ddc2d5f'
    client = ImgurClient(client_id, client_secret)
    thumbnail = client.upload_from_path(image, config=None, anon=True)
    os.remove(image)
    return(thumbnail['link'])