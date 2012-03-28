#!/bin/bash

if [ -z "$1" ]; then

  echo "Please provide FCGI command to run: start, stop, restart"
  exit 1

fi

if [ -z "$2" ]; then

  echo "Please provide instance name, e.g.: bout-de-papier"
  exit 1

fi

if [ -z "$3" ]; then

  echo "Please provide initial port, e.g. 8800"
  exit 1

fi



APP_DIR="/home/link5.me/link5"
WORKERS=2           # this affects reliability - one or two workers may die
MIN_CHILDREN=4      # this affects how server would react on unexpected load
MAX_CHILDREN=4      # this affects how much memory server would consume + server performance
MAX_REQUESTS=500    # this affects memory leaks protection
ENV="$2"
PORT="$3"

function start(){
    echo "Starting Link5: ${ENV} FCGI instances...";
    cd "${APP_DIR}"

    for (( I=${PORT}; I < ${PORT}+${WORKERS}; I++)); do
        echo "Port ${I}..."
        ./manage.py runfcgi port=${I} outlog="${APP_DIR}/../${ENV}-output-${I}.log" errlog="${APP_DIR}/../${ENV}-error-${I}.log" pidfile="${APP_DIR}/../${ENV}-${I}.pid" host=127.0.0.1 method=threaded minspare="${MIN_CHILDREN}" maxchildren="${MAX_CHILDREN}" maxrequests="${MAX_REQUESTS}" daemonize=true

        if [ "$?" -ne "0" ]; then
            rm -f "${APP_DIR}/../${ENV}-${I}.pid"   # erase invalid PID
            exit 1                                  # exit on exception
        fi
    done
    echo "Done."
}

function stop(){
    echo "Stopping link5: ${ENV} FCGI instances...";
    for x in `ls ${APP_DIR}/../${ENV}-*.pid`; do
        p=`cat "${x}"`
        echo "PID ${p}..."
        kill "$p"
        rm -f "${x}"
    done
    echo "Done."
}

function restart(){
    echo "Restarting link5: ${ENV} FCGI instances...";
    for (( I=${PORT}; I < ${PORT}+${WORKERS}; I++)); do
        echo "Port ${I}..."
        if [ -f "${APP_DIR}/../${ENV}-${I}.pid" ] ; then    # PID file exists
            kill `cat "${APP_DIR}/../${ENV}-${I}.pid"`
            rm "${APP_DIR}/../${ENV}-${I}.pid"
        else
            echo "PID file is not found!"
        fi
        sleep 1
        ./manage.py runfcgi  port=${I} outlog="${APP_DIR}/../${ENV}-output-${I}.log" errlog="${APP_DIR}/../${ENV}-error-${I}.log" pidfile="${APP_DIR}/../${ENV}-${I}.pid" host=127.0.0.1 method=threaded minspare="${MIN_CHILDREN}" maxchildren="${MAX_CHILDREN}" maxrequests="${MAX_REQUESTS}" daemonize=true
        if [ "$?" -ne "0" ]; then
            rm -f "${APP_DIR}/../${ENV}-${I}.pid"   # erase invalid PID
            exit 1                                  # exit on exception
        fi
    done
    echo "Done."
}

function status(){
    echo "Gathering Link5: ${ENV} FCGI instances status..."
    for (( I=${PORT}; I < ${PORT}+${WORKERS}; I++)); do

        if [ -f "${APP_DIR}/../${ENV}-${I}.pid" ]; then
            pid=`cat "${APP_DIR}/../${ENV}-${I}.pid"`
            processes=`ps --no-headers --pid $pid`
            if [ "$?" -ne "0" ]; then
                echo "Port ${I}: process is not found, possible crash"
            else
                echo "Port ${I}: running: PID $pid"
                #echo "$processes"
                #tail "${APP_DIR}/../${ENV}-output-${I}.log"
            fi
        else
            echo "Port ${I}: not started"
        fi

    done
    echo "Done."
}

$1
