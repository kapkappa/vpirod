#!/usr/bin/env python3

import pika, sys

proc_number = sys.argv[1]

#STEP 0: receive data from ETL process

streets = ['a', 'aa', 'aaa']

#step 1: receive message

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='processes', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

#severities = sys.argv[1:]
#if not severities:
#    sys.stderr.write("Usage: %s [info] [warning] [error]\n" % sys.argv[0])
#    sys.exit(1)

#for severity in severities:
#    channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=severity)

channel.queue_bind(exchange='processes', queue=queue_name, routing_key=proc_number)

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))

    channel.queue_declare(queue='processes-manager', durable=True)
    channel.basic_publish(exchange='', routing_key='processes-manager', body=body)



channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

#STEP 2: send message back to the manager


