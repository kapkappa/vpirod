#!/usr/bin/env python3

import os, sys, re
import pika

rank = sys.argv[1]

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

queue_name = "splitter_to_mapper"+rank
channel.queue_declare(queue=queue_name)

for root, dirs, files in os.walk("M"+rank):
    for file in files:
        if ("txt" in file):
            print(file)
            with open("M"+rank+"/"+file, "r") as f:
                for line in f:
                    line = re.sub(r'[^\w\s]','', line)
                    channel.basic_publish(exchange='', routing_key=queue_name, body=line.lower())
            f.close()

print("splitter: END")
channel.basic_publish(exchange='', routing_key=queue_name, body="__quit__")

