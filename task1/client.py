#!/usr/bin/env python3

import pika, sys

#STEP 1: send a message to the manager

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='client-manager', durable=True)

message = ' '.join(sys.argv[1:])

channel.basic_publish(exchange='', routing_key='client-manager', body=message, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))

print("CLIENT: message sent")

#STEP 2: receive a message from the manager

channel.queue_declare(queue='manager-client', durable=True)

def callback(ch, method, properties, body):
    print("CLIENT: message recieved")
    print(body)

channel.basic_consume(queue='manager-client', on_message_callback=callback)
channel.start_consuming()

connection.close()
