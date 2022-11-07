#!/usr/bin/env python3

import pika, sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='client-master')


while(True):
    print("CLIENT: new iteration")

    try:
        string = input()
        list = string.split()
        print(list)
    except EOFError as e:
        break

    channel.basic_publish(exchange='', routing_key='client-master', body=string)
    print("CLIENT: message {} sent to MASTER".format(string))


connection.close()
print("CLIENT: connection with master closed")
