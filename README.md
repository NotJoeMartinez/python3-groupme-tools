# Python3 Groupme-Tools

Tools to fetch the complete history of a GroupMe group chat and analyze it.

## Example Usage

**Downloads a json file with full transcript of group** 

```bash
python groupme-fetch.py [Group ID] [Your Access Token]
```

**Downloads images and makes html page of transcript** 
You will need groupme-fetch.py to make a json file before doing this 

```bash
python html-transcript.py [filename.json] [html-output-directory]
```

## `groupme-fetch.py` 
Allows you to grab the entire transcript for one of your groups and save it as JSON for backup and analysis. It is documented; run it with `--help` for help. It also allows you to fetch recent updates in the group to keep your JSON file up to date.

## `simple-transcript.py` 
Processes a JSON file into a human-readable text transcript.

## `stat/*`
The files in the `stat` folder allow for learning interesting things about the transcript's content and the group's history.

## Finding your access token

**nb. there are better ways to do this now; see [GroupMe API docs](https://dev.groupme.com/docs/v3).**

Log into [GroupMe's web interface](https://web.groupme.com/groups) and use Chrome or Safari's inspector to monitor the network requests when you load one of your groups.

You'll notice a GET request to an endpoint `https://v2.groupme.com/groups/GROUP_ID/messages`.

One of the headers sent with that request, `X-Access-Token`, is your access token.

## Finding your group ID

**nb. there are better ways to do this now; see [GroupMe API docs](https://dev.groupme.com/docs/v3).**

Again, in GroupMe's web interface, the group ID is the numeric ID included in the group's URL (`https://web.groupme.com/groups/GROUP_ID`).

## Requirements/Dependencies/Python
- Wget
- Requests
`pip install -r requirments.txt`

## Keep your transcript up to date
After your initial fetch with `groupme-fetch.py`, optionally using the `oldest` option to fetch older history. You should have a complete transcript up to the last time you fetched. Then...
Note the `oldest` or `newest` parameters are message IDs from your transcript JSON file.
`python groupme-fetch.py GROUPID ACCESSTOKEN newest $(python newest-id.py transcript-GROUPID.json)`
