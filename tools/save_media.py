import requests, shutil, os, re
from pathlib import Path

def downloader(url, path, ext):

    filename = url.replace("https://i.groupme.com", "")
    filename = filename.replace("https://v.groupme.com", "")
    filename = filename.replace("/", "")

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



def save_videos(transcript, media_dir):
    for elem in transcript:
        text = elem["text"]
        if text != None:
            match = re.findall(
                r'(http|https)(:\/\/[\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', 
                    text)
            if len(match) > 0:
                for i in match:
                    url = ''.join(i)
                    if url.endswith(".mp4"):
                        downloader(url, f"{media_dir}/vids", "mp4")


def save_documents():
    pass




def make_output_dir(media_dir):

    if media_dir[-1] == "/":
        output_dir = media_dir[:-1]

    chat_imgs = f"{media_dir}/imgs/"
    chat_vids = f"{media_dir}/vids/"
    user_avatars = f"{media_dir}/avatars/"

    Path(media_dir).mkdir(parents=True, exist_ok=True)
    Path(chat_imgs).mkdir(parents=True, exist_ok=True)
    Path(chat_vids).mkdir(parents=True, exist_ok=True)
    Path(user_avatars).mkdir(parents=True, exist_ok=True)
