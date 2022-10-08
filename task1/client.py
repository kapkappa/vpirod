#!/usr/bin/env python3

import pika, sys

#STEP 1: send a message to the manager

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='client-manager')
channel.queue_declare(queue='manager-client')


while(True):
    print("CLIENT: new iteration")

    letter = input()

    if (letter.isalpha() == False):
        print("Wrong input: enter a letter")
        continue

    channel.basic_publish(exchange='', routing_key='client-manager', body=letter.lower())
    print("CLIENT: message {} sent to MANAGER".format(letter))

    requested_streets = []

    #STEP 2: receive a message from the manager
    def callback(ch, method, properties, _body):
        if (_body.decode("utf-8") == "__quit__"):
            channel.stop_consuming()
        else:
            requested_streets.append(_body.decode("utf-8"))

#        print("CLIENT: message {} recieved from MANAGER".format(_body.decode("utf-8")))


    channel.basic_consume(queue='manager-client', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

    print(requested_streets)



print("CLIENT: consuming stopped")
connection.close()
print("CLIENT: connection closed")
