#!/usr/bin/env python3

import pika, sys

#STEP 0: get number of processes from starter script

number_of_processes = sys.argv[1]

#STEP 1: receive message from client

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='client-manager', durable=True)

def callback_client(ch, method, properties, body):
    letter = body
    step2(letter.lower())

channel.basic_consume(queue='client-manager', on_message_callback=callback_client, auto_ack=True)
channel.start_consuming()

#STEP 2: send message to selected process

def step2(letter):

    dict = {l: (i % number_of_processes) for i, l in enumerate("abcdefghijklmnopqrstuvwxyz")} # d = {'а': 0, ... }

    def get_number(letter):
        if (letter.isalpha() == false):
            return -1

        return dict[letter]


    channel.exchange_declare(exchange='processes', exchange_type='direct')

    proc_number = get_number(letter)
    print("MANAGER: sending message to {} process!".format(proc_number))

    channel.basic_publish(exchange='processes', routing_key=proc_number), body=letter)

#STEP 4: receive message from selected process

    




#fourth step: send message back to client


