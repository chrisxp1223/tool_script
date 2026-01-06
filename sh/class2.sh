#!/bin/bash

USER_NAME=$(id -un)

echo "your user name is ${USER_NAME}"

if [ "${UID}" -eq 0 ]
then 
        echo "You are root."
else
       echo "You are  not root" 
fi
