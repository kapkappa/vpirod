#!/usr/bin/env python3

import os, sys
import pika

rank = sys.argv[1]

receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()
receive_channel.exchange_declare(exchange='reducers', exchange_type='direct')
result = receive_channel.queue_declare(queue='', exclusive=False)
queue_name = result.method.queue
receive_channel.queue_bind(exchange='reducers', queue=queue_name, routing_key=rank)

sending_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
sending_channel = sending_connection.channel()
sending_channel.queue_declare(queue='reducers_to_master')


dict = {}

def to_master():
    for key in dict.keys():
        message = key + " " + str(dict[key])
        sending_channel.basic_publish(exchange='', routing_key='reducers_to_master', body=message)
    sending_channel.basic_publish(exchange='', routing_key='reducers_to_master', body="__quit__")



def callback(ch, method, properties, body):
    message = body.decode('utf-8').split()
    key = message[0]
    if (key == "__quit__"):
        to_master()
        receive_channel.stop_consuming()
        return

    value = 0
    for i in range(1, len(message)):
        value += int(message[i])
    dict[key] = value



receive_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
receive_channel.start_consuming()
receive_channel.close()

print("reducer: END")
