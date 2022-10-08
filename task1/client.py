#!/usr/bin/env python3

import pika, sys

#STEP 1: send a message to the manager

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='client-manager')

letter = input()

channel.basic_publish(exchange='', routing_key='client-manager', body=letter)
print("CLIENT: message {} sent to MANAGER".format(letter))



#STEP 2: receive a message from the manager

def callback(ch, method, properties, _body):
    print("CLIENT: message {} recieved from MANAGER".format(_body.decode("utf-8")))


channel.queue_declare(queue='manager-client')
channel.basic_consume(queue='manager-client', on_message_callback=callback, auto_ack=True)
channel.start_consuming()

print("CLIENT: consuming stopped")
connection.close()
print("CLIENT: connection closed")
