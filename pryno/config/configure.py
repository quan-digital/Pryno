# -*- coding: utf-8 -*-

# - Configure -
# * Quan.digital *

# Creates settings.py in the correct directory given config.json

import shutil
import json

if __name__ == '__main__':

    # Copy base to correct file
    shutil.copy2('./settings_base.py', '../util/settings.py')

    # Load new configs
    with open('config.json', 'r') as r:
        configs = json.load(r)

    # Write new configs
    with open('../util/settings.py', 'a') as w:
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
