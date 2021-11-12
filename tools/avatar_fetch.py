import json
import os
import requests # to get image from the web
import shutil # to save it locally


# Iterating through the json list


def save_avatars(avatar_dir,json_file):
    os.mkdir(avatar_dir)

    file_object = open(json_file)
    data = json.load(file_object)
    avatar_urls = []
    for i in data:
        if i['avatar_url'] not in avatar_urls:
            if i['avatar_url'] is not None:
                avatar_urls.append(i['avatar_url'])

    for url in avatar_urls: 
        ## Set up the image URL and filename
        filename = avatar_dir + url.split("/")[-1] + ".jpeg"

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(url, stream = True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
            
            # Open a local file with wb ( write binary ) permission.
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                
            print('Image sucessfully Downloaded: ',filename)
        else:
            print('Image Couldn\'t be retreived')

