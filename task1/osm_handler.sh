#!/bin/bash

cat map.osm | grep 'addr:street' | cut -d '"' -f4
