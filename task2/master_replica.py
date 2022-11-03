#!/usr/bin/env python3

import sys, time, pika

print("master replica")

dict = {'x' : "", 'y' : "", 'z' : ""}
times = {'x' : 0, 'y' : 0, 'z' : 0}
print(dict)

id = 0
number_of_replicas = int(sys.argv[1])


#send to concrete replicas
exchange_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
exchange_channel = exchange_connection.channel()
exchange_channel.exchange_declare(exchange='0', exchange_type='direct')


#get info from client
client_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
client_channel = client_connection.channel()
client_channel.queue_declare(queue='client-master')


#receive from any replica
receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()


confirmations = 0

def callback_replicas(ch, method, properties, body):
    #confirmation from replica
    print("receive info")
    confirmations += 1
    if confirmations == number_of_replicas:
        confirmations = 0
        print("all replicas updated")
        receive_channel.stop_consuming()



def callback_client(ch, method, properties, body):
    #TODO: checks
    print(body)
    list = body.decode('utf-8').split()
    print(list)

    key = list[0]
    value = list[1]

    time.sleep(2)

    if key not in dict:
        print("Wrong key")
        return

    print("debug")
    time.sleep(2)

    dict[key] = value

    print("debug2")
    time.sleep(2)

    times[key] += 1

    print("debug3")
    print(dict)
    time.sleep(2)
    #send info
    exchange_channel.basic_publish(exchange='0', routing_key='1', body= key + " " + value + " " + str(times[key]))

    print("debug4")
    time.sleep(2)

    #get confirmations
    receive_channel.start_consuming()



for i in range(number_of_replicas):
    print(i)
    if (i != id):
        receive_channel.exchange_declare(exchange=str(i), exchange_type='direct')
        result = receive_channel.queue_declare(queue='', exclusive=False)
        queue_name = result.method.queue
        receive_channel.queue_bind(exchange=str(i), queue=queue_name, routing_key=str(i))
        receive_channel.basic_consume(queue=queue_name, on_message_callback=callback_replicas, auto_ack=True)



client_channel.basic_consume(queue='client-master', on_message_callback=callback_client, auto_ack=True)
client_channel.start_consuming()

print("END")
time.sleep(10)
