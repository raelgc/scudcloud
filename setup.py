#!/usr/bin/env python3

from distutils.core import setup
import glob
import os

def get_icon_data_file_tuple(theme):
    directory = '/usr/share/icons/%s/scalable/apps' % theme
    files = glob.glob(os.path.join('share', 'icons', theme, '*.svg'))
    return (directory, files)

def _data_files():
    yield 'share/applications', ['scudcloud.desktop']
    yield 'share/doc/scudcloud', ['LICENSE', 'README.md']
    for theme in ['hicolor', 'mono-dark', 'mono-light']:
        yield get_icon_data_file_tuple(theme)

# TODO: Get version information from git.
def get_version():
    with open('scudcloud/VERSION', 'r') as vfile:
        return vfile.read()

setup(name='scudcloud',
      author='Rael Gugelmin Cunha',
      author_email='rael.gc@gmail.com',
      data_files=list(_data_files()),
      description='Unofficial Slack Client',
      keywords = "slack chat im instant_message",
      license = "MIT",
      maintainer='Andrew Stiegmann',
      maintainer_email='andrew.stiegmann <AT> gmail.com',
      package_data={'scudcloud': ['VERSION', 'resources/*',]},
      packages=['scudcloud',],
      requires=['dbus', 'PyQt4',],
      url='https://github.com/raelgc/scudcloud',
      version=get_version(),
)
