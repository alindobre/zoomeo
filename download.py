#!/usr/bin/python3
# pull images from zoom cloud recordings

import json
import requests

# initially, we just use hardcoded stuff
with open('config.json') as f:
    config = json.load(f)

headers = {
    'Authorization': 'bearer ' + config['access_token']
}

#import http.client
#http.client.HTTPConnection.debuglevel = 1


r = requests.get('https://api.zoom.us/v2/users/me/recordings?from=2020-01-01', headers=headers)
recordings_json = json.loads(r.content.decode('utf-8', 'ignore'))

for meeting in recordings_json['meetings']:
    for recording in meeting['recording_files']:
        if recording['file_size'] < 1024000:
            print(recording['download_url'], recording['recording_start'])
