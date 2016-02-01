#!/usr/bin/env python3

from setuptools import setup
from scudcloud.version import __version__
import glob
import os

def _data_files():
    for theme in ['hicolor', 'ubuntu-mono-dark', 'ubuntu-mono-light', 'elementary']:
        directory = os.path.join('share', 'icons', theme, 'scalable', 'apps')
        files = glob.glob(os.path.join('share', 'icons', theme, '*.svg'))
        yield directory, files

    yield os.path.join('share', 'doc', 'scudcloud'), \
        ['LICENSE', 'README']
    yield os.path.join('share', 'applications'), \
        glob.glob(os.path.join('share', '*.desktop'))
    yield os.path.join('share', 'pixmaps'), \
        glob.glob(os.path.join('scudcloud', 'resources', 'scudcloud.png'))


setup(name='scudcloud',
      author='Rael Gugelmin Cunha',
      author_email='rael.gc@gmail.com',
      data_files=list(_data_files()),
      description='Unofficial Slack Client',
      entry_points = {
          'gui_scripts': ['scudcloud = scudcloud.__main__:main'],
      },
      keywords = "slack chat im instant_message",
      license = "MIT",
      maintainer='Andrew Stiegmann',
      maintainer_email='andrew.stiegmann AT gmail.com',
      package_data={'scudcloud': ['resources/*',]},
      packages=['scudcloud',],
      requires=['dbus', 'PyQt4',],
      url='https://github.com/raelgc/scudcloud',
      version = __version__,
)
