import sys, importlib, json, datetime
from importlib import reload

reload(sys)



def write_simple_transcript(messages, outputFilename):
    """Prints a readable "transcript" from the given list of messages.

    Assumes the input list is sorted."""
    with open(outputFilename, 'w') as outFile:
        for message in messages:
            name = message[u'name']
            time = datetime.datetime.fromtimestamp(message[u'created_at']).strftime('%Y-%m-%d %H:%M')

            # text is None for a photo message
            if message[u'text'] != None:
                text = message[u'text']
            else:
                text = "(no text)"

            if message[u'system'] is True:
                system_padded = '(SYS) '
            else:
                system_padded = ''

            if len(message[u'favorited_by']) != 0:
                favorites_padded = ' (' + str(len(message[u'favorited_by'])) + 'x <3)'
            else:
                favorites_padded = ''

            if message[u'picture_url'] != None:
                pic = ' ; photo URL ' + message[u'picture_url']
            else:
                pic = ''

            line = u'{0}{1}({2}){3}: {4}{5}\n'.format(
                system_padded, name, time, favorites_padded, text, pic
            )
            outFile.write(line)
    print(f"Transcript saved to {outputFilename}")

