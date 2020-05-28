#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import join, dirname

here = dirname(__file__)

setup(name='pryno',
      version='0.1.5',
      description='BitMEX autonomous trading using Keep Alive HTTP + Plot.ly Dash + Telegram API.',
      long_description=open(join(here, 'README.md')).read(),
      author='canokaue & claudiovb',
      author_email='kaue.cano@quan.digital',
      url='quan.digital',
      install_requires=[
        'requests==2.23.0',
        'websocket-client==0.57.0',
        'requests==2.23.0',
        'schedule==0.6.0',
        'dash==1.11.0',
        'flask-login==0.5.0',
        'dash-auth==1.3.2',
        'dash-core-components==1.9.1',
        'python-telegram-bot==12.7'
      ],
      packages=find_packages(),
      )