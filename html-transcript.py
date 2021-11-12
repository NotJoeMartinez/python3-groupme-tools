"""
Module to translate JSON transcript into a pretty HTML output.

This module actually should create a folder that contains an index.html as well
as all the necessary images for the transcript to be rendered in browser
completely offline.
"""

# from UserDict import UserDict
from collections import UserDict 
from inspect import cleandoc
import datetime as dt
import json
import requests
import datetime
import os.path
import sys
import shutil
import re
import fileinput

_HTML_HEADER = """<!doctype html>\n'
<html>\n<head>
<meta charset="UTF-8">
<title>GroupMe Transcript</title>
<link rel="stylesheet" type="text/css" href="groupme.css">
<script src="http://cdn.jsdelivr.net/emojione/1.5.0/lib/js/emojione.min.js"></script>
<link rel="stylesheet" href="http://cdn.jsdelivr.net/emojione/1.5.0/assets/css/emojione.min.css"/>
<script src="groupme.js"></script>
</head>\n<body>
<div class="container">
<h1>GroupMe Transcript</h1>
<div class="chat">
"""

_HTML_FOOTER = """</div>
</div>
</body>
</html>
"""


class ImageCache(UserDict):
    """Maps image URLs to local filenames."""

    def __init__(self, folder, initialdata={}):
        UserDict.__init__(self, initialdata)
        self._folder = folder

    def _save_image(self, url):
        # Full disclosure, largely adapted from this SO answer:
        # http://stackoverflow.com/a/16696317
        local_file = url.split('/')[-1] + ".jpeg"
        local = os.path.join(self._folder, local_file)
        if os.path.exists(local):
            return local_file
        print('Downloading image.')
        resp = requests.get(url, stream=True)
        with open(local, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return local_file

    def __getitem__(self, key):
        try:
            return UserDict.__getitem__(self, key)
        except KeyError:
            local = self._save_image(key)
            self[key] = local
            return local


def write_html_transcript(messages, outfile, imgcache):

    for i, message in enumerate(messages):
        # Get variables
        name = message[u'name']
        time_obj = datetime.datetime.fromtimestamp(message[u'created_at'])
        time_str = time_obj.strftime('%Y-%m-%d %H:%M')
        text = message[u'text']
        if text is None:
            text = u''
        system = message[u'system']
        faves = message[u'favorited_by']
        nlikes = faves if faves == 0 else len(faves)
        pic = message[u'picture_url']


        # Open div
        outfile.write('<div class="message-container')
        if system:
            outfile.write(' system')
        outfile.write('">')

        # Author
        outfile.write('<div class="author">')
        outfile.write(name)
        outfile.write('</div>')

        # time stamp
        outfile.write("<div class='timestamp'> {}</div> <br>".format(time_str) )
        # Message span
        outfile.write('<div class="message"><span class="message-span" title="{}">'.format(time_str) )
        outfile.write(text)
        outfile.write('</span></div>')

        # Likes
        if nlikes > 0:
            outfile.write('<div class="likes">')
            outfile.write("<img class='emojione' src='http://cdn.jsdelivr.net/emojione/assets/png/2764.png'>x</img>")
            outfile.write('<span class="likes-count">%d</span>' % nlikes)
            outfile.write('</div>')

        # Image
        if pic:
            local = imgcache[pic]
            outfile.write('<img src="' + local + '" class="picture-message" width="500" height="600" >')

        # Close div
        outfile.write('</div>\n')

        # print('%04d/%04d messages processed' % (i, len(messages)))


def write_html(folder, messages, emoji=True):
    imgcache = ImageCache(folder)
    index_fn = os.path.join(folder, 'index.html')
    shutil.copyfile('assets/groupme.css', os.path.join(folder, 'groupme.css'))
    shutil.copyfile('assets/groupme.js', os.path.join(folder, 'groupme.js'))
    with open(index_fn, 'w') as f:
        f.write(_HTML_HEADER)
        write_html_transcript(messages, f, imgcache)
        f.write(_HTML_FOOTER)



def main(args):

    json_file = args.jsonfile
    output_dir = args.outputdir

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


    # calls fix_json
    trans_file = open(json_file)

    transcript = json.load(trans_file)
    trans_file.close()

    write_html(output_dir, transcript)


if __name__ == '__main__':
    help_str= """
    Usage: html-transcript.py [filename.json] [html-output-folder]

    Takes a JSON GroupMe transcript and writes a mostly offline HTML version of
    your transcript. 
    """

    import argparse
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument("-jf","--jsonfile", action="store", help="json file produced from groupme-fetch.py", required=True)
    parser.add_argument("-od","--outputdir",action="store", help="folder to output html files to", required=True)
    args = parser.parse_args()

    main(args)
