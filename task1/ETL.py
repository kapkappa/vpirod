#!/usr/bin/env python3

import subprocess

#subprocess.run("/home/gravitage/prog/github/vpirod/task1/osm_handler.sh")
message = subprocess.run("/home/gravitage/prog/github/vpirod/task1/osm_handler.sh", capture_output=True, text=True)

print(message)
