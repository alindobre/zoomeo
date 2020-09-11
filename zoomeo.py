#!/usr/bin/python3
# pull images from zoom cloud recordings

import json
import requests
import urllib.request
import vimeo
import datetime
import sys
import time

# initially, we just use hardcoded stuff
with open('config.json') as f:
    config = json.load(f)

headers = {
    'Authorization': 'bearer ' + config['zoom']['jwt']['access_token']
}

import http.client
#http.client.HTTPConnection.debuglevel = 1
import pprint

r = requests.get('https://api.zoom.us/v2/users/me/recordings?from=2020-01-01', headers=headers)
recordings_json = json.loads(r.content.decode('utf-8', 'ignore'))

v = None

for meeting in recordings_json['meetings']:
    for recording in meeting['recording_files']:
        del_url = f"https://api.zoom.us/v2/meetings/{recording['meeting_id']}/recordings/{recording['id']}?action=trash"
        if recording['file_size'] == 0:
            print(f"IGNORE-SIZE-0: {del_url}")
            continue
        if recording['file_size'] < 1024*1000*10: # 10MB
            print(f"DELETE-SIZE: {del_url} size={recording['file_size']}")
            requests.delete(del_url, headers=headers)
            continue
        try:
            dt = datetime.datetime.strptime(recording['recording_start'], "%Y-%m-%dT%H:%M:%SZ")
            dt = dt + datetime.timedelta(hours=1)
            title = f"{dt.strftime('%A')} {dt.day} {dt.strftime('%b')}, {dt.strftime('%H_%M_%S_BST')}"
        except:
            title = recording['recording_start']
        print(f"DOWNLOAD:  {recording['recording_start']} {recording['download_url']}")
        urllib.request.urlretrieve(f"{recording['download_url']}?access_token={config['zoom']['jwt']['access_token']}", filename='/tmp/zoomeo')
        if not v:
            v = vimeo.VimeoClient(
                token=config['vimeo']['oauth']['token'],
                key=config['vimeo']['oauth']['key'],
                secret=config['vimeo']['oauth']['secret']
            )
        print(f"UPLOAD:    {recording['recording_start']} > {title}")
        video_uri = v.upload('/tmp/zoomeo', data={
          'name': title,
          'privacy': { 'view': 'unlisted' },
        })

        print(f"PASSWORD:  {recording['recording_start']} > {title}")
        v.patch(video_uri, data={
          'privacy': {
              'view': 'password',
              'download': 'false'
          },
          'password': config['vimeo']['videos_password']
        })

        print(f"TRANSCODE: {recording['recording_start']} > {title}")
        rep = 0
        tries = 0
        while rep < 1800:
            try:
                response = v.get(video_uri + '?fields=transcode.status').json()
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                tries += 1
                if tries < 5:
                    continue
                raise
            if response['transcode']['status'] == 'complete':
                print(f"\nDELETE: {del_url}")
                requests.delete(del_url, headers=headers)
                break
            elif response['transcode']['status'] == 'in_progress':
                if not rep % 60:
                    if rep > 0:
                        sys.stdout.write("\n")
                    sys.stdout.write(f"    {rep:8} ")
                sys.stdout.write('.')
                sys.stdout.flush()
            else:
                print(rep, 'Video encountered an error during transcoding.')
                break
            rep += 1
            time.sleep(1)
