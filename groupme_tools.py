import sys, json, importlib, argparse
from datetime import datetime
from pathlib import Path

from tools import *

importlib.reload(sys)


def main(parser, args):
    if len(sys.argv) < 2:
        parser.print_help()
        exit(0)

    if args.command=="fetch":

        group_id = args.group_id
        access_token = args.access_token
        beforeId = args.oldest
        stopId = args.newest
        pages = args.pages

        output_dir = f"{args.output_dir}/{group_id}"
        transcript_fname = f'{output_dir}/transcript-{group_id}.json'

        # Makes directorys for output
        make_output_dir(output_dir)

        transcript = load_transcript(transcript_fname)

        # Adjust stop ids if resume previous was called
        if args.resumePrevious or args.resumeNext:
            tempFileName = f"{output_dir}/temp-transcript-{0}.json".format(group_id)
            tempTranscript = loadTempTranscript(tempFileName)

            transcript = sorted(reconcileTranscripts(transcript, tempTranscript),
                            key=lambda k: k['created_at'])
        if transcript:
            if args.resumePrevious:
                beforeId = transcript[0]['id']
            else:
                stopId = transcript[-1]['id']


        populate_transcript(output_dir,group_id,access_token,transcript, beforeId, stopId)

        # sort transcript in chronological order
        transcript = sorted(transcript, key=lambda k: k[u'created_at'])

        print(f"Transcript contains {len(transcript)} messages") 
     


        # Writes new json file
        transcriptFile = open(transcript_fname, 'w+')
        json.dump(transcript, transcriptFile, ensure_ascii=False)
        transcriptFile.close()

    if args.command=="simple":

        json_file = args.json_file
        output_file = args.output_file

        with open(json_file) as transcriptFile:
            transcript = json.load(transcriptFile)

        write_simple_transcript(transcript, output_file)

    if args.command=="html":
        json_file = args.json_file
        output_dir = f"{args.output_dir}/html"

        
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)


        # calls fix_json
        trans_file = open(json_file)

        transcript = json.load(trans_file)
        trans_file.close()

        write_html(output_dir, transcript)

        print(f"HTML file made in {output_dir}/index.html")





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Archive groupme transcripts")

    subparsers = parser.add_subparsers(dest='command')

    ## Fetch
    fetch = subparsers.add_parser('fetch', help="Fetches json transcript see fetch --help")
    fetch.add_argument('-g','--group-id', action="store", required=True, help="Group id of transcript you want to fetch")
    fetch.add_argument('-t', '--access-token', action="store", required=True, help="Your acess tokenstore")
    fetch.add_argument('-o', '--output-dir', action="store", required=True, help="Output Directory")

    fetch.add_argument("--resumePrevious", action='store_true', default=False, help="Resume based on the last found files and get previous messages")
    fetch.add_argument("--resumeNext", action='store_true', default=False, help="Resume based on the last found files and get next messages.")
    fetch.add_argument("--oldest", help="The ID of the oldest (topmost) message in the existing transcript file")
    fetch.add_argument("--newest", help="The ID of the newest (bottom-most) message in the existing transcript file")
    fetch.add_argument("--pages", type=int,
                        help="The number of pages to pull down (defaults to as many as the conversation has")

    # Simple Transcript
    simple = subparsers.add_parser('simple', help="Writes text file see simple --help")
    simple.add_argument("-jf", "--json-file", required=True, help="Input json filename (should not be temp file)")
    simple.add_argument("-o", "--output-file", required=True, help="output json filename Ex: [output.json]")
    

    # Html Transcript
    html = subparsers.add_parser('html', help="writes html file")
    html.add_argument("-jf","--json-file", action="store", help="Json file made from fetch")
    html.add_argument("-od","--output-dir", action="store", help="Directory to store the html file")


    args = parser.parse_args()
    main(parser, args)
    