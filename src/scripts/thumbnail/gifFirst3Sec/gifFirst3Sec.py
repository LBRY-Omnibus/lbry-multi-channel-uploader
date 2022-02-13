
def main(video) -> str:
    import os
    progPath = os.path.dirname(os.path.abspath(os.path.join(__file__,"../../..")))
    os.system(f"""ffmpeg -i "{video}" -fs 3M -vf "scale=640:-2" -y "{progPath + '/data/thumbnailTemp.gif'}" """)
    print(progPath + "/data/thumbnailTemp.gif")
    return(progPath + '/data/thumbnailTemp.gif')