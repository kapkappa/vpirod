#!/usr/bin/env python3

import pika, sys

#first step: receive message from client

dict = {l: i for i, l in enumerate("abcdefghijklmnopqrstuvwxyz")} # d = {'а': 0, ... }

def get_number(letter):
    if (letter.isalpha() == false):
        return -1

    return dict[letter.lower()]


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='client-manager', durable=True)

def callback_client(ch, method, properties, body):
    letter = body
    number_of_proc = get_number(letter)
    //TODO

channel.basic_consume(queue='client-manager', on_message_callback=callback_client, auto_ack=True)
channel.start_consuming()


#second step: send message to selected process

channel.exchange_declare(exchange='processes', exchange_type='direct')

channel.basic_publish(exchange='processes', routing_key=number_of_proc, body=letter.lower())


#third step: receive message from selected process





#fourth step: send message back to client


