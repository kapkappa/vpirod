#!/usr/bin/env python3

import subprocess

#STEP 1: get data from osm-file

message = subprocess.run('./osm_handler.sh', capture_output=True, text=True)

streets = message.stdout
streets = streets.split('\n')

streets=list(set(streets))
print(streets)

#STEP 2: send data to processes
...

