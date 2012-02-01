#!/bin/bash

if [ -z "$1" ]; then

  echo "Please provide FCGI command to run: start, stop, restart, status"
  exit 1

fi

if [ -z "$2" ]; then
  echo "Please provide instance name: link5"
  exit 1
fi


if [[ "$2" == "link5" || "$2" == "ALL" ]] ; then
  ./fcgi_start_link5_instance.sh $1 "link5" 9080
fi

