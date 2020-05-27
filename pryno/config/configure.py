# -*- coding: utf-8 -*-

# - Configure -
# * Quan.digital *

import shutil
import json

def run(base_path = './settings_base.py', config_path = 'config.json' , out_path = '../util/settings.py'):
    '''Creates settings.py in the correct directory given config.json.'''
    print('No settings.py file found, generating...')
    # Copy base to correct file
    shutil.copy2(base_path , out_path)

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
            # Otherwise, sandwich with quotation marks so they end up as strings
            except:
                w.write('"')
                w.write(value)
                w.write('"')
            w.write('\n\n')
    print('settings.py successfully created!')

if __name__ == '__main__':
    run()
