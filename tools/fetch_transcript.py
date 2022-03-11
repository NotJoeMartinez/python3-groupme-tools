import json, os, re, requests, sys 

from pathlib import Path




def load_transcript(transcript_fname):
    """
    Load a transcript file by name
    """
    if os.path.exists(transcript_fname):
        with open(transcript_fname, 'rb') as transcriptFile:
            try:
                return json.loads(transcriptFile.read())
            except ValueError:
                print('transcript file had bad json! ignoring')
                return []
    return []



def populate_transcript(output_dir, group, accessToken, transcript, beforeId, stopId, pageLimit=None):
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



    tempFileName = f"{output_dir}/temp-transcript-{0}.json".format(group)

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



def onRequestError(request):
    print(request.status_code)
    print(request.headers)
    print(request.text)
    sys.exit(2)
