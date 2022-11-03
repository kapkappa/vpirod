#!/usr/bin/env python3

import subprocess, sys
import shlex
import time

number_of_replicas = sys.argv[1]

slaves_command = ["python3", "replica.py"]
master_command = ["python3", "master_replica.py"]
new_window_command = "x-terminal-emulator -e".split()

subprocess.Popen(["x-terminal-emulator", "-e", "python3", "master_replica.py", str(number_of_replicas)], stdin=None, stdout=None, stderr=None, close_fds=True)

for i in range(int(number_of_replicas)):
#    subprocess.check_call(new_window_command + slaves_command + [id] + [number_of_replicas])
    subprocess.Popen(["x-terminal-emulator", "-e", "python3", "replica.py", str(i), str(number_of_replicas)], stdin=None, stdout=None, stderr=None, close_fds=True)
