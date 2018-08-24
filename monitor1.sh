#!/bin/bash

# Use this with nohup to keep t1_manager always running in case it crashes
# sudo chmod 777 monitor1.sh
# nohup ./monitor1.sh

until python2.7 t1_manager.py; do
    echo "'t1_manager.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done
