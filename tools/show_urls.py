import re

def show_urls(transcript):
    for elem in transcript:

        text = elem["text"]
        aurl = elem["avatar_url"]
        purl = elem["picture_url"]

        if  aurl != None:
            print(aurl)

        if purl != None:
            print(purl)

        if text != None:
            match = re.findall(
                r'(http|https)(:\/\/[\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', 
                    text)
            if len(match) > 0:
                for i in match:
                    url = ''.join(i)
                    print(url)