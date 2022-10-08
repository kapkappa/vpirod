#!/usr/bin/env python3

import pika, sys

#STEP 0: get number of processes from starter script

number_of_processes = int(sys.argv[1])
dict = {l: (i % number_of_processes) for i, l in enumerate("abcdefghijklmnopqrstuvwxyz")} # d = {'а': 0, ... }



#STEP 1: receive message from client

client_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
client_channel = client_connection.channel()
client_channel.queue_declare(queue='client-manager')

def callback_client(ch, method, properties, _body):
    print("MANAGER: message {} received from CLIENT".format(_body.decode("utf-8")))
    letter = _body.decode("utf-8")
    step2(letter)


#STEP 2: send message to selected process

def step2(letter):
    exchange_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    exchange_channel = exchange_connection.channel()
    exchange_channel.exchange_declare(exchange='processes', exchange_type='direct')

    proc_number = dict[letter]
    print("MANAGER: sending message to {} PROCESS".format(proc_number))
    exchange_channel.basic_publish(exchange='processes', routing_key=str(proc_number), body=letter)



#STEP 3: receive message from selected process
    process_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    process_channel = process_connection.channel()
    process_channel.queue_declare(queue='processes-manager')

    def callback_process(ch, method, properties, __body):
#        print("MANAGER: message {} received from any process".format(__body.decode("utf-8")))
        step3(__body.decode("utf-8"))


#STEP 4: send message back to client
    def step3(street):
#        print("MANAGER: message {} sent to CLIENT".format(street))
        client_channel.basic_publish(exchange='', routing_key='manager-client', body=street)
        if (street == "__quit__"):
            process_channel.stop_consuming()


    process_channel.basic_consume(queue='processes-manager', on_message_callback=callback_process, auto_ack=True)
    process_channel.start_consuming()



client_channel.basic_consume(queue='client-manager', on_message_callback=callback_client, auto_ack=True)
client_channel.start_consuming()

print("MANAGER: stopped consuming")
client_connection.close()
print("MANAGER: connection closed")
