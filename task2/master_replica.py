#!/usr/bin/env python3

import sys, time, pika

print("master replica")

dict = {'x' : "", 'y' : "", 'z' : ""}
times = {'x' : 0, 'y' : 0, 'z' : 0}
print("data: {}".format(dict))

id = 0
number_of_replicas = int(sys.argv[1])

confirmations = 0

#sending connection
send_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
send_channel = send_connection.channel()


#get info from client
client_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
client_channel = client_connection.channel()
client_channel.queue_declare(queue='client-master')


#receive connection
receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()
receive_channel.queue_declare(queue = '0')


def callback_replicas(ch, method, properties, body):
    #confirmation from replica
    print("receive info from replica")

    global confirmations
    confirmations += 1

    if confirmations == number_of_replicas:
        confirmations = 0
        print("all replicas updated!")
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

    #send info to replicas
    print("send message to {} replica".format(1))
    destination = 1
    send_channel.queue_declare(queue = str(destination))
    send_channel.basic_publish(exchange='', routing_key=str(destination), body= key + " " + value + " " + str(times[key]))

    #get confirmations
    print("waiting for responses")

    receive_channel.basic_consume(queue='0', on_message_callback=callback_replicas, auto_ack=True)
    receive_channel.start_consuming()



client_channel.basic_consume(queue='client-master', on_message_callback=callback_client, auto_ack=True)
client_channel.start_consuming()

print("END")
time.sleep(10)
