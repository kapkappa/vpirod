#!/usr/bin/env python3

import sys, time, pika, random

print("master replica")

dict = {'x' : "", 'y' : "", 'z' : ""}
times = {'x' : 0, 'y' : 0, 'z' : 0}
print("Data: {}\nTimestamps: {}".format(dict, times))

id = 0
number_of_replicas = int(sys.argv[1])

confirmations = 0

seq = list(range(1, number_of_replicas+1))

k = number_of_replicas / 3
if k < 3:
    k = number_of_replicas

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


#random_seq = random.sample(seq, k)

def callback_replicas(ch, method, properties, body):
    #confirmation from replica
#    print("receive info from replica")

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
    value = ""
    for i in range(1, len(list)):
        value += list[i]
        value += " "
    value = value[:-1]

    if key not in dict:
        print("Wrong key")
        return

    dict[key] = value
    times[key] += 1

    print("Data: {},\nTimestamps: {}".format(dict, times))

    #send info to replicas
#    print("send message to {} replica".format(1))
#    destination = 1

#    time.sleep(5)

    random_seq = random.sample(seq, k)

#    print("random")
#    time.sleep(5)

    for destination in random_seq:
        send_channel.queue_declare(queue = str(destination))
        send_channel.basic_publish(exchange='', routing_key=str(destination), body= key + " " + value + " " + str(times[key]))



    #get confirmations
#    print("waiting for responses")
#    time.sleep(5)

    if (number_of_replicas > 0):
        receive_channel.basic_consume(queue='0', on_message_callback=callback_replicas, auto_ack=True)
        receive_channel.start_consuming()



client_channel.basic_consume(queue='client-master', on_message_callback=callback_client, auto_ack=True)
try:
    client_channel.start_consuming()
except KeyboardInterrupt:
    print("Receive keyboard interruption!")

send_connection.close()
receive_connection.close()
client_connection.close()

print("Bye!")
time.sleep(5)
