import requests, shutil, os
from pathlib import Path

def downloader(url, path, ext):

    filename = url.replace("https://i.groupme.com/", "")

    res = requests.get(url, stream = True)

    if res.status_code == 200:
        res.raw.decode_content = True

        with open(f"{path}/{filename}.{ext}", 'wb') as f:
            shutil.copyfileobj(res.raw, f)
            print(f"saved: {path}/{filename}.{ext}")


def save_imgs(transcript, media_dir):

    for pic in transcript:
        if pic["picture_url"] != None:
            img_url = pic["picture_url"]
            downloader(img_url, f"{media_dir}/imgs", "jpeg")


def save_avatars(transcript, media_dir):

    for elem in transcript:
        avatar_url = elem["avatar_url"]
        if avatar_url != None:
            downloader(avatar_url, f"{media_dir}/avatars", "jpeg")




def save_videos():
    pass

def save_documents():
    pass




def make_output_dir(output_dir):

    if output_dir[-1] == "/":
        output_dir = output_dir[:-1]

    media_dir = f"{output_dir}/media/"
    chat_imgs = f"{media_dir}/imgs/"
    chat_vids = f"{media_dir}/vids/"
    user_avatars = f"{media_dir}/avatars/"

    Path(media_dir).mkdir(parents=True, exist_ok=True)
    Path(chat_imgs).mkdir(parents=True, exist_ok=True)
    Path(chat_vids).mkdir(parents=True, exist_ok=True)
    Path(user_avatars).mkdir(parents=True, exist_ok=True)
