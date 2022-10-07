#!/usr/bin/env python3

import pika, sys

#STEP 1: send a message to the manager

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='client-manager', durable=True)

letter = input()

channel.basic_publish(exchange='', routing_key='client-manager', body=letter)

print("CLIENT: message sent to MANAGER")



#STEP 2: receive a message from the manager

#channel.queue_declare(queue='manager-client', durable=True)

def callback(ch, method, properties, body):
    print("CLIENT: message recieved from MANAGER")
    print(body.decode("utf-8"))

channel.basic_consume(queue='client-manager', on_message_callback=callback)
channel.start_consuming()

connection.close()
