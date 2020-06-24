# -*- coding: utf-8 -*-

# - Configure module -
# * Quan.digital *

import os
import shutil
import json


def create_settings(
        base_path='./settings_base.py',
        config_path='config.json',
        out_path='../util/settings.py'):
    '''Creates settings.py in the correct directory given config.json.'''
    print('Generating settings.py...')
    # Copy base to correct file
    shutil.copy2(base_path, out_path)

    # Load new configs
    with open(config_path, 'r') as r:
        configs = json.load(r)

    # Write new configs
    with open(out_path, 'a') as w:
        for key, value in configs.items():
            w.write(key)
            w.write(' = ')
            # If number is either int or float, write it plainly
            try:
                floatest = float(value)
                w.write(str(value))
            # Otherwise, sandwich with quotation marks so they end up as
            # strings
            except BaseException:
                w.write('"')
                w.write(value)
                w.write('"')
            w.write('\n\n')
    print('settings.py successfully created!')


def setup_instance():
    '''Configure modules for deployment.'''
    os.popen('sudo -s')
    os.popen('sudo apt upgrade')
    os.popen('sudo apt install python3-pip')
    os.popen('pip3 install -e .')
    print('Instance setup completed.')


def process_runner():
    '''Creates screen and runs shell script indefinitely.'''
    os.popen('screen -S pryno')
    os.popen('chmod +x forever.py')
    os.popen('python3 forever.py main.py')


if __name__ == '__main__':
    # setup_instance()
    # create_settings()
    process_runner()
