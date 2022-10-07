#!/usr/bin/env python3

import subprocess, sys

import time

number_of_proc = sys.argv[1]

print("ETL process")
subprocess.run(["python3", "ETL.py", number_of_proc])


for i in range(int(number_of_proc)):
    print("{} process".format(i))
    subprocess.Popen(["python3", "process.py", str(i)], stdin=None, stdout=None, stderr=None, close_fds=True)


print("manager process")
subprocess.Popen(["python3", "manager.py", number_of_proc], stdin=None, stdout=None, stderr=None, close_fds=True)

print("client process")
subprocess.run(["python3", "client.py"])

