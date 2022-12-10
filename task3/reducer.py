#!/usr/bin/env python3

import os, sys
import pika

rank = sys.argv[1]

number_of_shufflers = int(sys.argv[2])

receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()
receive_channel.queue_declare(queue=rank, exclusive=False)

sending_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
sending_channel = sending_connection.channel()
sending_channel.queue_declare(queue='reducers_to_master')


dict = {}

count = 0

def to_master():
    for key in dict.keys():
        message = key + " " + str(dict[key])
        sending_channel.basic_publish(exchange='', routing_key='reducers_to_master', body=message)
    sending_channel.basic_publish(exchange='', routing_key='reducers_to_master', body="__quit__")



def callback(ch, method, properties, body):
    global count
    message = body.decode('utf-8').split()
    key = message[0]
    if (key == "__quit__"):
        count += 1
        if (count == number_of_shufflers):
            to_master()
            receive_channel.stop_consuming()
            return

        return

    value = 0
    for i in range(1, len(message)):
        value += int(message[i])

    if (key not in dict.keys()):
        dict[key] = 0

    dict[key] += value



receive_channel.basic_consume(queue=rank, on_message_callback=callback, auto_ack=True)
receive_channel.start_consuming()
receive_channel.close()

#print("reducer: END")
