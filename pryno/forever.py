from pryno.util import tools, settings
from subprocess import Popen
import datetime as dt
import time
import sys
import os
import pryno.telegram_bot.quan_bot as telegram_bot


def continuous_deployment():
    telegram_bot.send_group_message(msg="🆕 Bot for {0} is being updated\
         currently on version {1}".format(settings.CLIENT_NAME, settings.BOT_VERSION))
    time.sleep(4)
    tools.kill_pids()
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
        try:
            p = Popen("python3 " + filename, shell=True)
            p.wait()
        except (KeyboardInterrupt, SystemExit):
            time.sleep(4)
            tools.kill_pids()
            sys.exit()
