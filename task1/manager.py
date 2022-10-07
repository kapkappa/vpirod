#!/usr/bin/env python3

import pika, sys

#STEP 0: get number of processes from starter script

number_of_processes = int(sys.argv[1])
dict = {l: (i % number_of_processes) for i, l in enumerate("abcdefghijklmnopqrstuvwxyz")} # d = {'а': 0, ... }



#STEP 1: receive message from client

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='client-manager', durable=True)

def callback_client(ch, method, properties, body):
    print("MANAGER: message received from CLIENT")
    print(body.decode("utf-8"))
    letter = body.decode("utf-8")
    step2(letter.lower())


#STEP 2: send message to selected process

def step2(letter):
    def get_number(letter):
        if (letter.isalpha() == False):
            return -1
        return dict[letter]

    channel.exchange_declare(exchange='processes', exchange_type='direct')

    proc_number = get_number(letter)
    print("MANAGER: sending message to {} process!".format(proc_number))

    channel.basic_publish(exchange='processes', routing_key=str(proc_number), body=letter)



#STEP 3: receive message from selected process
    channel.queue_declare(queue='processes-manager', durable=True)

    def callback_process(ch, method, properties, body):
        print("MANAGER: message received from {} process".format(proc_number))
        step3(body.decode("utf-8"))


#STEP 4: send message back to client

    def step3(streets):
        print("MANAGER: message sent to CLIENT")
        channel.basic_publish(exchange='', routing_key='client-manager', body=streets)

    channel.basic_consume(queue='processes-manager', on_message_callback=callback_client, auto_ack=True)
    channel.start_consuming()



channel.basic_consume(queue='client-manager', on_message_callback=callback_client, auto_ack=True)
channel.start_consuming()
