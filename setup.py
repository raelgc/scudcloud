#!/usr/bin/env python3

from setuptools import setup
from scudcloud.version import __version__
import glob
import os

def _data_files():
    yield 'share/applications', ['share/scudcloud.desktop']
    yield 'share/doc/scudcloud', ['LICENSE', 'README']
    for theme in ['hicolor', 'mono-dark', 'mono-light']:
        directory = 'share/icons/%s/scalable/apps' % theme
        files = glob.glob(os.path.join('share', 'icons', theme, '*.svg'))
        yield directory, files

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
      maintainer_email='andrew.stiegmann <AT> gmail.com',
      package_data={'scudcloud': ['resources/*',]},
      packages=['scudcloud',],
      requires=['dbus', 'PyQt4',],
      url='https://github.com/raelgc/scudcloud',
      version = __version__,
)
