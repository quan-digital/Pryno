import subprocess
import sys

# Checks for settings.py and creates it accordingly
try:
    from pryno.util import settings
except:
    print('No settings.py found!')
    from pryno.config import configure
    configure.create_settings(base_path='pryno/config/settings_base.py', config_path='pryno/config/config.json' , out_path = 'pryno/util/settings.py')
    from pryno.util import settings

from subprocess import Popen
import datetime as dt
import time
import sys
import os
import pryno.telegram_bot.quan_bot as telegram_bot
from pryno.dashboard import app
from pryno.util import tools

def continuous_deployment():
    telegram_bot.send_group_message(msg="🆕 Bot for {0} is updating from version {1}".format(settings.CLIENT_NAME, settings.BOT_VERSION))
    time.sleep(1)
    time.sleep(1)
    subprocess.call(["pip3", "install", "-e", "../."])
    time.sleep(7)
    tools.kill_pids()
    # app.shutdown_server()
    os.popen("git pull https://kauecano:Glubglub69@github.com/canokaue/Pryno")
    time.sleep(4)
    os.popen("chmod +x forever.py")
    os.popen("python3 forever.py main.py True")


if __name__ == "__main__":
    tools.create_dirs()
    filename = sys.argv[1]

    # if sys.argv[2] is None:
    #     reinstall = False
    # else:
    #     reinstall = True
    # if reinstall:
    pid = os.getpid()
    with open('pryno/pids/forever.pid', 'w') as w:
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
