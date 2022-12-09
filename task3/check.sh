#!/bin/bash

sudo rabbitmqctl list_bindings                 #Lists all bindings on a vhost
sudo rabbitmqctl list_channels                 #Lists all channels in the node
sudo rabbitmqctl list_ciphers                  #Lists cipher suites supported by encoding commands
sudo rabbitmqctl list_connections              #Lists AmqctlP 0.9.1 connections for the node
sudo rabbitmqctl list_consumers                #Lists all consumers for a vhost
sudo rabbitmqctl list_exchanges                #Lists exchanges
sudo rabbitmqctl list_hashes                   #Lists hash functions supported by encoding commands
sudo rabbitmqctl list_node_auth_attempt_stats  #Lists authentication attempts on the target node
sudo rabbitmqctl list_queues                   #Lists queues and their properties
sudo rabbitmqctl list_unresponsive_queues      #Tests queues to respond within timeout. Lists those which did not respond
sudo rabbitmqctl ping                          #Checks that the node OS process is up, registered with EPMD and CLI tools can authenticate with it
#sudo rabbitmqctl report                        #Generate a server status report containing a concatenation of all server status information for support purposes
#sudo rabbitmqctl schema_info                   #Lists schema database tables and their properties
sudo rabbitmqctl status                        #Displays status of a node

