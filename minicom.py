#!/usr/bin/env python
import os
import subprocess
import sys

ROOT="~/trunk/Project"
project_list = [
                "nautilus",
                "coral",
                "poppy",
                "setzer",
                "robo",
                "nahser"];

def help_menu():
     print "Usage: [target] [board name] "

def call_minicom(target,board):
    print "minicom -D XXXXX"

def get_support_list(argv):
    
    supported = False
    
    for index in project_list:
        if index == argv:
            supported = True
            break
    if (not supported): 
        print "not supported board"

    return supported

def get_uart_type(argv):
    print "unkonw targe given "

def get_board_location():
    print "location not found"

def main(argv):

    if len(argv) <= 1:
        help_menu()
        return 

    if (not get_support_list(argv[2])):
        return 
    
    target = get_uart_type(argv[1])
    
    board = get_board_location()

            
    call_minicom(target,board)


if __name__ == '__main__':
    main(sys.argv)


