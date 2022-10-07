#!/usr/bin/env python3

import pika, sys

proc_number = sys.argv[1]

#STEP 0: receive data from ETL process

streets = ['xxxxxx', 'yyyyyy', 'zzzzzzzzz']

#step 1: receive message

receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()
receive_channel.exchange_declare(exchange='processes', exchange_type='direct')
result = receive_channel.queue_declare(queue='', exclusive=False)
queue_name = result.method.queue
receive_channel.queue_bind(exchange='processes', queue=queue_name, routing_key=proc_number)


def callback(ch, method, properties, _body):
    print("PROCESS {}: message received from MANAGER".format(proc_number))

    sending_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    sending_channel = sending_connection.channel()
    sending_channel.queue_declare(queue='processes-manager')
    sending_channel.basic_publish(exchange='', routing_key='processes-manager', body=streets[0])

    print("PROCESS {}: message sent to MANAGER".format(proc_number))



receive_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
receive_channel.start_consuming()


print("PROCESS {}: consuming stopped".format(proc_number))
connection.close()
print("PROCESS {}: connection closed".format(proc_number))
