#!/usr/bin/env python
import os
import subprocess
import sys
ROOT = "/mnt/host/source/Project/"
pty_config_file = "./pty_number"

project_list = [
				"nautilus",
				"coral",
				"poppy",
				"setzer",
				"robo",
				"nahser"];

def help_menu():
	print "Usage: [target] [board name] "

def call_minicom(pty, location):

	cmd = "minicom -D" + pty
	os.chdir(location)
	os.getcwd()
	print "minicom -D " + pty
	os.system(cmd)

def get_support_list(argv):

	not_supported = True

	for index in project_list:
		if index == argv:
			not_supported = False
			break

	if (not_supported):
		board = None
		print "not supported board"

	return not_supported

def get_uart_type(argv):

	if argv == "ec":
		not_connection  = os.system("dut-control ec_uart_pty > pty_number")
		if not_connection:
			print "connection fail"
			return None

		fd = open("pty_number","r")
		fd.read(len("ec_uart_pty:"))
		target = fd.readline()
		os.remove("./pty_number")
		return target

	if argv == "cpu":
		not_connection = os.system("dut-control cpu_uart_pty > pty_number")
		if not_connection:
			print "connection fail"
			return None

		fd = open(pty_config_file, "r")
		fd.read(len("cpu_uart_pty:"))
		target = fd.readline()
		os.remove(pty_config_file)
		return target

	print "unkonw targe given "

def get_board_location(board):

	location = ROOT + str(board)

	if (not os.path.isdir(location)):
		create = raw_input("Project folder doesn't exiset, do you want to create it ? press y to create.. ")
		if str(create) == 'y' or str(create) == 'Y':
			os.makedirs(location)
		else:
			print "exit"
			return

	return location

def main(argv):

	if len(argv) <= 2:
		help_menu()
		return

	target = argv[1]
	board = argv[2]

	pty = get_uart_type(target)

	if pty == None:
		return

	if (get_support_list(board)):
		return

	location = get_board_location(board)
	call_minicom(pty,location)

	print "end.."
	return

if __name__ == '__main__':
    main(sys.argv)


