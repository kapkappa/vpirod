#!/usr/bin/env python3

import os, sys
import pika

rank = sys.argv[1]

number_of_reducers = sys.argv[2]

receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()

receive_queue_name = "mapper_to_shuffler"+rank
receive_channel.queue_declare(queue=receive_queue_name)

send_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
send_channel = send_connection.channel()

alphabet = {l: (i % int(number_of_reducers)) for i, l in enumerate("abcdefghijklmnopqrstuvwxyz")} # d = {'а': 0, ... }
dict = {}


def to_reduce():
    for key in dict.keys():
        message = key
        if (message[0] not in alphabet.keys()):
            continue

        for i in dict[key]:
            message = message + " " + i

        destination = str(alphabet[message[0]])
        send_channel.queue_declare(queue = destination)
        send_channel.basic_publish(exchange='', routing_key=destination, body=message)

    for i in range(int(number_of_reducers)):
        send_channel.queue_declare(queue = str(i))
        send_channel.basic_publish(exchange='', routing_key=str(i), body="__quit__")



def callback(ch, method, properties, body):
    words = body.decode('utf-8').split()
    if (words[0] == "__quit__"):
        to_reduce()
        receive_channel.stop_consuming()
        return

    if (words[0] not in dict.keys()):
        dict[words[0]] = []

    dict[words[0]].append(words[1])


receive_channel.basic_consume(queue=receive_queue_name, on_message_callback=callback, auto_ack=True)
receive_channel.start_consuming()
receive_channel.close()

#print("shuffler: END")
