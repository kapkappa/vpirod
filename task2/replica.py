#!/usr/bin/env python3

import sys, pika, time

dict = {'x' : "", 'y' : "", 'z' : ""}
times = {'x' : 0, 'y' : 0, 'z' : 0}

id = sys.argv[1]
number_of_replicas = int(sys.argv[2])

print("replica {}".format(id))


#receive from any replica
receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()


#send to concrete replicas
exchange_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
exchange_channel = exchange_connection.channel()
exchange_channel.exchange_declare(exchange=id, exchange_type='direct')



def receive_callback(ch, method, properties, body):
    print("message received")
    time.sleep(10)

    list = body.decode('utf-8').split()
    key = list[0]
    value = list[1]
    time = int(list[2])

    if times[key] < time:
        dict[key] = value
        times[key] = time

        #send new info
        destination = (int(id) + 1) % number_of_replicas
        if (destination > 0):
            exchange_channel.basic_publish(exchange=id, routing_key=str((int(id)+1) % number_of_replicas), body=key + " " + value + " " + time)
        #send confirmation to master replica
        exchange_channel.basic_publish(exchange=id, routing_key=0, body="comfirm")


for i in range(number_of_replicas):
    if (i != int(id)):
        receive_channel.exchange_declare(exchange=str(i), exchange_type='direct')
        result = receive_channel.queue_declare(queue='', exclusive=False)
        queue_name = result.method.queue
        receive_channel.queue_bind(exchange=str(i), queue=queue_name, routing_key=str(i))
        receive_channel.basic_consume(queue=queue_name, on_message_callback=receive_callback, auto_ack=True)


receive_channel.start_consuming()
