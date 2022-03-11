import os, sys, re, json
from datetime import datetime
import importlib
from pathlib import Path

from tools import avatar_fetch as af

importlib.reload(sys)
import requests



def onRequestError(request):
    print(request.status_code)
    print(request.headers)
    print(request.text)
    sys.exit(2)


def main(parser, args):

    if len(sys.argv) < 2:
        parser.print_help()
        exit(0)

    group = args.group
    accessToken = args.access_token
    output_dir = args.output_dir
    beforeId = args.oldest
    stopId = args.newest
    pages = args.pages

    transcriptFileName = 'transcript-{0}.json'.format(group)
    output_dict = make_output_dir(output_dir,transcriptFileName)

    transcript = loadTranscript(transcriptFileName)
    if args.resumePrevious or args.resumeNext:
        tempFileName = getTempFileName(output_dict, group)
        tempTranscript = loadTempTranscript(tempFileName)
        transcript = sorted(reconcileTranscripts(transcript, tempTranscript),
                            key=lambda k: k['created_at'])
        if transcript:
            if args.resumePrevious:
                beforeId = transcript[0]['id']
            else:
                stopId = transcript[-1]['id']

    transcript = populateTranscript(output_dict, group, accessToken, transcript, beforeId, stopId, pages)

    # sort transcript in chronological order
    transcript = sorted(transcript, key=lambda k: k[u'created_at'])
    print('Transcript contains {0} messages from {1} to {2}'.format(
        len(transcript),
        datetime.fromtimestamp(transcript[0]['created_at']),
        datetime.fromtimestamp(transcript[-1]['created_at']),
    ))

    transcriptFile = open(f"{output_dict['parent_dir']}{transcriptFileName}", 'w+')

    json.dump(transcript, transcriptFile, ensure_ascii=False)
    transcriptFile.close()
    # output_dict = af.save_avatars()


def make_output_dir(output_dir, transcript_fname):

    if output_dir[-1] == "/":
        output_dir = output_dir[:-1]

    transcript_fname = transcript_fname.replace(".json", "")

    parent_dir = f"{output_dir}/{transcript_fname}/"
    media_dir = f"{parent_dir}/media/"
    chat_imgs = f"{media_dir}/chat_imgs/"
    chat_vids = f"{media_dir}/chat_vids/"
    user_avatars = f"{media_dir}/user_avatars/"

    Path(media_dir).mkdir(parents=True, exist_ok=True)
    Path(chat_imgs).mkdir(parents=True, exist_ok=True)
    Path(chat_vids).mkdir(parents=True, exist_ok=True)
    Path(user_avatars).mkdir(parents=True, exist_ok=True)
    return {
        "parent_dir": parent_dir,
        "meida_dir": media_dir,
        "chat_imgs": chat_imgs,
        "chat_vids": chat_vids,
        "user_avatars": user_avatars 
    }

def reconcileTranscripts(*transcripts):
    """
    Given multiple transcripts, returns a generate that includes any message exactly once
    removing duplicates across transcripts
    """
    seenIds = set()
    for transcript in transcripts:
        for message in transcript:
            if message['id'] not in seenIds:
                seenIds.add(message['id'])
                yield message


def loadTranscript(transcriptFileName):
    """
    Load a transcript file by name
    """
    if os.path.exists(transcriptFileName):
        with open(transcriptFileName, 'rb') as transcriptFile:
            try:
                return json.loads(transcriptFile.read())
            except ValueError:
                print('transcript file had bad json! ignoring')
                return []
    return []


def loadTempTranscript(tempFileName):
    """
    Load a temp transcript file by name
    """
    # todo lot of copy/paste from above
    if os.path.exists(tempFileName):
        with open(tempFileName, 'rb') as tempFile:
            try:
                return [m for line in tempFile.readlines() for m in json.loads(line)]
            except ValueError:
                print('temp file had bad json! ignoring')
                return []
    return []


def populateTranscript(output_dict, group, accessToken, transcript, beforeId, stopId, pageLimit=None):
    complete = False
    pageCount = 0
    endpoint = 'https://v2.groupme.com/groups/' + group + '/messages'
    headers = {
        'Accept': 'application/json, text/javascript',
        'Accept-Charset': 'ISO-8859-1,utf-8',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/json',
        'Origin': 'https://web.groupme.com',
        'Referer': 'https://web.groupme.com/groups/' + group,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
        'X-Access-Token': accessToken
    }

    tempFileName = getTempFileName(output_dict, group)
    with open(tempFileName, 'w') as tempFile:
        while not complete:
            pageCount = pageCount + 1
            if pageLimit and pageCount > pageLimit:
                break

            print('starting on page ' + str(pageCount))

            if beforeId is not None:
                params = {'before_id': beforeId}
            else:
                params = {}
            r = requests.get(endpoint, params=params, headers=headers)

            if r.status_code != 200:
                onRequestError(r)

            response = r.json()
            messages = response[u'response'][u'messages']

            if stopId is not None:
                messages = sorted(messages, key=lambda k: k[u'created_at'], reverse=True)
                for message in messages:
                    if message[u'id'] == stopId:
                        complete = True
                        print('Reached ID ' + stopId + "; stopping!")
                        break
                    else:
                        transcript.append(message)
            else:
                transcript.extend(messages)

            tempFile.write(json.dumps(messages))
            tempFile.write('\n')
            if len(messages) != 20:
                complete = True
                print('Reached the end/beginning!')

            # keep working back in time
            beforeId = messages[-1][u'id']

    return transcript


def getTempFileName(output_dict, group):
    return f"{output_dict['parent_dir']}temp-transcript-{0}.json".format(group)

# def fix_json(trans_file):
#     # Read in the file
#     tf = str(trans_file)
#     with open(tf, 'r') as file:
#         filedata = file.read()
#     # Replace the target string
#     # filedata = filedata.replace(pattern, ',')
#     fixed_json = re.sub('\]\n.', '\n,\n', filedata, flags=re.MULTILINE)

#     # Write the file out again
#     with open(tf, 'w') as file:
#         file.write(fixed_json)
#     pass

if __name__ == '__main__':
    """
    Writes out "transcript-groupId.json" with the history of the group
    in chronological order.

    If a file by that name is found, we'll go ahead and update that
    scrape depending on the options you provide. It is assumed that the
    file is in the correct format *and its messages are in chronological
    order*.

    The easiest way to continue a scrape is to pass --resumePrevious or --resumeNext
    which will continue with the scrape moving backwards/forwards.

    For more fine grained control you can provide --oldest or --newest flags with
    specific message IDs
    """

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--group', action="store",help="The Group ID")
    parser.add_argument('-t', '--access-token', action="store", help="Your acess tokenstore")
    parser.add_argument('-o', '--output-dir', action="store", required=True, help="Output Directory")
    parser.add_argument("--resumePrevious", action='store_true', default=False, help="Resume based on the last found files and get previous messages.")
    parser.add_argument("--resumeNext", action='store_true', default=False, help="Resume based on the last found files and get next messages.")
    parser.add_argument("--oldest", help="The ID of the oldest (topmost) message in the existing transcript file")
    parser.add_argument("--newest", help="The ID of the newest (bottom-most) message in the existing transcript file")
    parser.add_argument("--pages", type=int,
                        help="The number of pages to pull down (defaults to as many as the conversation has")

    args = parser.parse_args()
    main(parser,args)
    sys.exit(0)
