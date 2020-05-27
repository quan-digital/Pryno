
import json
from pryno.config import settings_base
with open('config.json', 'r') as r:
    configs = json.load(r)

with open('../util/settings.py', 'w') as w:
    for item in dir(settings_base):
        if not item.startswith('__') and not item.startswith('key') and not item.startswith('pkg_resources'):
            w.write(item)
            w.write(' = ')
            try:
                floattime = float(item)
                w.write(settings_base.__dict__[item])
            except:
                w.write(str(str(settings_base.__dict__[item])))
            w.write('\n\n')
    for key, value in configs.items():
        w.write(key)
        w.write(' = ')
        w.write(value)
        w.write('\n\n')

