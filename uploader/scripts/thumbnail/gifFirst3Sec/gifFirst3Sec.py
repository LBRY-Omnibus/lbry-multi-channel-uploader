def main(video) -> str:
    import os
    progPath = os.path.dirname(os.path.abspath(__file__))
    os.system(f"""ffmpeg -i "{video}" -fs 3M -vf "scale=640:-2" -y "{progPath + '/temp/thumbnailTemp.gif'}" """)
    print(progPath + "/temp/thumbnailTemp.gif")
    return(progPath + "/temp/thumbnailTemp.gif")