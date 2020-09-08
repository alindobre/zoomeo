#!/usr/bin/python3
# pull images from zoom cloud recordings

import json

# initially, we just use hardcoded stuff
with open('config.json') as f:
    config = json.load(f)
