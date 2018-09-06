#!/usr/bin/envpython
# Chroot Environment setup
import os
import subprocess
import sys


DEPOT_TOOLS = "depot_tools"
CHROOT = "chroot"
Current_Path = os.getcwd()
Tool_Path = Current_Path + "/" + DEPOT_TOOLS
Chroot_Path = Current_Path + "/" + CHROOT
ENV_PATH = os.environ["PATH"] + ':' + Tool_Path
os.environ["PATH"] = ENV_PATH


def setup_depot_tool():
    if not os.path.isdir(Tool_Path):
        ans = raw_input("depot_tool is not exsit, press 'y' for download depot tool\n")
        if ans == 'y':
            print 'Download now .....
            subprocess.call(["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])
        else:
            return -1


def help_menu():
    print 'Usage: chromenv [repo command=n] [code source=n]'
    print 'Commands:'
    print '-b : repo init [firmware branch]'
    print '-s : repo sync'
    print '-c : cros_sdk'
    print '-d : cros_sdk --delete'
    print '-r : cros_sdk --replace'
    print '-h : help'


def cmd_menu(argv):

    for cmd in argv:
        if cmd == '-b':
            if len(argv) > 2 and argv[2] != "":
                branch_name = str(argv[2])
                subprocess.call(["repo", "init", "-u", "https://chromium.googlesource.com/chromiumos/manifest.git"])
                subprocess.call(["repo", "init", "-b", "firmware-buddy-6301.202.B"])
                subprocess.call(["repo", "sync"])
                break
            else:
                ans = raw_input("the branch name is empty, press 'y' to use tot or 'n' to exit\n")
                if ans == 'y':
                    subprocess.call(["repo", "init", "-u", "https://chromium.googlesource.com/chromiumos/manifest.git"])
                    subprocess.call(["repo", "sync"])
                else:
                    break

        elif cmd == '-s':
            subprocess.call(["repo", "sync"])
            break
        elif cmd == '-c':
            subprocess.call(["cros_sdk", "--no-ns-pid"])
            break
        elif cmd == '-d':
            subprocess.call(["cros_sdk", "--delete"])
            break
        elif cmd == '-r':
            subprocess.call(["cros_sdk", "--replace"])
            break
        elif cmd == '-n':
            subprocess.call(["cros_sdk", "--nouse-image"])
            break
        elif cmd == '-h':
            help_menu()
            break
    else:
        print "Usage: chromenv [repo command=n] [code source=n] \n"
        print "Use 'chromenv -h' to print a list of commands"


def main(argv):
    setup_depot_tool()
    cmd_menu(argv)


if __name__ == '__main__':
    main(sys.argv)
