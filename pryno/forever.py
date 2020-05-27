from pryno.util import tools
from subprocess import Popen
import datetime as dt
import time
import sys
import os

def continuous_deployment():
    tools.kill_cd()
    os.popen("git pull")
    os.popen("chmod +x forever.py")
    time.sleep(5)
    os.popen("python3 forever.py main.py")


if __name__ == "__main__":
    filename = sys.argv[1]
    pid = os.getpid()
    with open('pids/forever.pid', 'w') as w:
        w.write(str(pid))
    while True:
    
        print("")
        print("-\*---------------|It's Fovereeeever|---------------*/-")
        print("-\*                        .                        */-")
        print("-\*                        .                        */-")
        print("\n"+ str(dt.datetime.now()))
        print("\nStarting " + filename + "\n")
        print("-\*                        .                        */-")
        print("-\*                        .                        */-")
        print("-\|This time I know and there's no doubt in my mind|*/-")
        print("")
        p = Popen("python3 " + filename, shell=True)
        p.wait()