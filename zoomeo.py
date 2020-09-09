#!/usr/bin/python3
# pull images from zoom cloud recordings

import json
import requests
import urllib.request

# initially, we just use hardcoded stuff
with open('config.json') as f:
    config = json.load(f)

headers = {
    'Authorization': 'bearer ' + config['access_token']
}

import http.client
#http.client.HTTPConnection.debuglevel = 1
import pprint

r = requests.get('https://api.zoom.us/v2/users/me/recordings?from=2020-01-01', headers=headers)
recordings_json = json.loads(r.content.decode('utf-8', 'ignore'))

for meeting in recordings_json['meetings']:
    for recording in meeting['recording_files']:
        if recording['file_size'] < 1024000:
            del_uri = f"https://api.zoom.us/v2/meetings/{recording['meeting_id']}/recordings/{recording['id']}?action=trash"
            print(f'DELETE {del_url}')
            requests.delete(del_uri, headers=headers)
            continue
            try:
                dt = datetime.datetime.strptime(recording['recording_start'], "%Y-%m-%dT%H:%M:%SZ")
                title = f"{dt.strftime('%A')} {dt.day} {dt.strftime('%b')}, {dt.strftime('%X')}"
            except:
                title = recording['recording_start']
            print("DOWNLOAD: {title} {recording['download_url']}")
            local_filename, headers = urllib.request.urlretrieve(f"{recording['download_url']}?access_token=${config['access_token']}", filename='/tmp/zoomeo')
