#!/bin/bash


# Use this with nohup to keep t2_manager always running in case it crashes
# sudo chmod 777 monitor2.sh
# nohup ./monitor2.sh

until python2.7 t2_manager.py; do
    echo "'t2_manager.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done
