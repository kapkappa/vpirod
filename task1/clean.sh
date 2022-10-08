#!/bin/bash

list=`sudo rabbitmqctl list_queues | cut -f1`

for queue in $list; do
    sudo rabbitmqctl delete_queue $queue
done

sudo rabbitmqctl close_all_connections
