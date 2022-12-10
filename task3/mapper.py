#!/usr/bin/env python3

import os, sys
import pika

rank = sys.argv[1]

receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()

receive_queue_name = "splitter_to_mapper"+rank
receive_channel.queue_declare(queue=receive_queue_name)

send_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
send_channel = send_connection.channel()

send_queue_name = "mapper_to_shuffler"+rank
send_channel.queue_declare(queue=send_queue_name)

def callback(ch, method, properties, body):
    words = body.decode('utf-8').split()
    if (len(words) == 0): return
    if (words[0] == "__quit__"):
        receive_channel.stop_consuming()
        send_channel.basic_publish(exchange='', routing_key=send_queue_name, body="__quit__")
        return

    for w in words:
        send_channel.basic_publish(exchange='', routing_key=send_queue_name, body=w+" 1")


receive_channel.basic_consume(queue=receive_queue_name, on_message_callback=callback, auto_ack=True)
receive_channel.start_consuming()
receive_channel.close()

#print("mapper: END")
