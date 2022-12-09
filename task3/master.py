#!/usr/bin/env python3

import pika
import os, shutil
import subprocess, sys
import shlex
import time

path = sys.argv[1]
mapping_nodes = sys.argv[2]
convolution_nodes = sys.argv[3]

for i in range(int(mapping_nodes)):
    os.mkdir("M"+str(i))
    shutil.copy("splitter.py", "M"+str(i))
    shutil.copy("mapper.py", "M"+str(i))
    shutil.copy("shuffle.py", "M"+str(i))

for i in range(int(convolution_nodes)):
    os.mkdir("R"+str(i))
    shutil.copy("reducer.py", "R"+str(i))

#let suppose directories are already exist
c = 0
for root, dirs, files in os.walk(path):
    for f in files:
        shutil.copy(path+"/"+f, "M"+str(c))
        c = (c + 1) % int(mapping_nodes)

for i in range(int(mapping_nodes)):
    print("starting splitter №{}".format(i))
    subprocess.Popen(["python3", "M"+str(i)+"/splitter.py", str(i)], stdin=None, stdout=None, stderr=None, close_fds=True)

for i in range(int(mapping_nodes)):
    print("starting mapper №{}".format(i))
    subprocess.Popen(["python3", "M"+str(i)+"/mapper.py", str(i)], stdin=None, stdout=None, stderr=None, close_fds=True)

for i in range(int(mapping_nodes)):
    print("starting shuffler №{}".format(i))
    subprocess.Popen(["python3", "M"+str(i)+"/shuffle.py", str(i), convolution_nodes], stdin=None, stdout=None, stderr=None, close_fds=True)

for i in range(int(convolution_nodes)):
    print("starting reducer №{}".format(i))
    subprocess.Popen(["python3", "R"+str(i)+"/reducer.py", str(i)], stdin=None, stdout=None, stderr=None, close_fds=True)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='reducers_to_master')

def callback(ch, method, properties, body):
    message = body.decode('utf-8')
    if (message == "__quit__"):
        channel.stop_consuming()
        return

    print(message)


channel.basic_consume(queue='reducers_to_master', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
channel.close()
print("END")

for i in range(int(mapping_nodes)):
    shutil.rmtree("M"+str(i))

for i in range(int(convolution_nodes)):
    shutil.rmtree("R"+str(i))
