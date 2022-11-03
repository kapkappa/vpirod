#!/usr/bin/env python3

import sys, time, pika

print("master replica")

dict = {'x' : "", 'y' : "", 'z' : ""}
times = {'x' : 0, 'y' : 0, 'z' : 0}
print(dict)

id = 0
number_of_replicas = int(sys.argv[1])


#exchange point  for sending
exchange_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
exchange_channel = exchange_connection.channel()
exchange_channel.exchange_declare(exchange='0', exchange_type='direct')


#get info from client
client_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
client_channel = client_connection.channel()
client_channel.queue_declare(queue='client-master')


#receive connection
receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()


confirmations = 0

def callback_replicas(ch, method, properties, body):
    #confirmation from replica
    print("receive info from replica")
    confirmations += 1
    if confirmations == number_of_replicas:
        confirmations = 0
        print("all replicas updated")
        receive_channel.stop_consuming()



def callback_client(ch, method, properties, body):
    print("get message from client")
    list = body.decode('utf-8').split()
    print(list)

    key = list[0]
    value = list[1]

    if key not in dict:
        print("Wrong key")
        return

    dict[key] = value
    times[key] += 1

    print(dict)
    print(times)

    #send info
    print("send message to {} replica".format(1))
    exchange_channel.basic_publish(exchange='0', routing_key='1', body= key + " " + value + " " + str(times[key]))

    #get confirmations
    print("waiting for responses")
    receive_channel.start_consuming()



for i in range(number_of_replicas):
    print("connecting with replica {}".format(i+1))
    receive_channel.exchange_declare(exchange=str(i+1), exchange_type='direct')
    result = receive_channel.queue_declare(queue='', exclusive=False)
    queue_name = result.method.queue
    receive_channel.queue_bind(exchange=str(i+1), queue=queue_name, routing_key=str(i+1))
    receive_channel.basic_consume(queue=queue_name, on_message_callback=callback_replicas, auto_ack=True)



client_channel.basic_consume(queue='client-master', on_message_callback=callback_client, auto_ack=True)
client_channel.start_consuming()

print("END")
time.sleep(10)
