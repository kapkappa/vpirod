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
receive_channel.queue_declare(queue = id)


#connection for sending to replicas
send_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
send_channel = send_connection.channel()


def receive_callback(ch, method, properties, body):
    print("message received")

    list = body.decode('utf-8').split()
    print(list)
    key = list[0]
    value = list[1]
    time_stamp = int(list[2])

    if times[key] < time_stamp:
        dict[key] = value
        times[key] = time_stamp

        #send new info
#        destination = random.randint(1, number_of_replicas)
        destination = 2

        if (destination != int(id)):
            send_channel.queue_declare(queue = str(destination))
            send_channel.basic_publish(exchange='', routing_key=str(destination), body=key + " " + value + " " + str(time_stamp))

        send_channel.queue_declare(queue = '0')
        send_channel.basic_publish(exchange='', routing_key='0', body="confirm")

    print("end of processing")


receive_channel.basic_consume(queue=id, on_message_callback=receive_callback, auto_ack=True)
receive_channel.start_consuming()

print("END")
time.sleep(10)
