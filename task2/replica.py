#!/usr/bin/env python3

import sys, pika, time
import random

id = sys.argv[1]
number_of_replicas = int(sys.argv[2])
print("replica {}".format(id))

dict = {'x' : "", 'y' : "", 'z' : ""}
times = {'x' : 0, 'y' : 0, 'z' : 0}
print("Data: {}\nTimestamps: {}".format(dict, times))

k = 0
if number_of_replicas > 1:
    k = 2
if number_of_replicas > 3:
    k = 3

#receive from any replica
receive_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
receive_channel = receive_connection.channel()
receive_channel.queue_declare(queue = id)


#connection for sending to replicas
send_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
send_channel = send_connection.channel()


def receive_callback(ch, method, properties, body):
#    print("message received")

    list = body.decode('utf-8').split()
    key = list[0]
    value = list[1]
    time_stamp = int(list[2])

    if times[key] < time_stamp:
        print("new value {}: {}, {}".format(key, value, time_stamp))

        dict[key] = value
        times[key] = time_stamp

        #send new info
        for i in range(k):
            print(i)
            destination = int(id)
            while (destination == int(id)):
                destination = random.randint(1, number_of_replicas)
                print(destination)

            print("destination: {}".format(destination))

            send_channel.queue_declare(queue = str(destination))
            send_channel.basic_publish(exchange='', routing_key=str(destination), body=key + " " + value + " " + str(time_stamp))


        send_channel.queue_declare(queue = '0')
        send_channel.basic_publish(exchange='', routing_key='0', body="confirm")


receive_channel.basic_consume(queue=id, on_message_callback=receive_callback, auto_ack=True)
receive_channel.start_consuming()

print("END")
time.sleep(10)
