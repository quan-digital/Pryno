import subprocess
import sys

# Checks for settings.py and creates it accordingly
try:
    from pryno.util import settings
except:
    print('No settings.py found!')
    from pryno.config import configure
    configure.create_settings(base_path='config/settings_base.py', config_path='config/config.json' , out_path = 'util/settings.py')
    from pryno.util import settings

from subprocess import Popen
import datetime as dt
import time
import sys
import os
from pryno.dashboard import app
from pryno.util import tools

# Call this function to leave the bot proccess running without stopping passing as argument main.py
#
if __name__ == "__main__":
    tools.create_dirs()
    filename = sys.argv[1]

    # if sys.argv[2] is None:
    #     reinstall = False
    # else:
    #     reinstall = True
    # if reinstall:
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
