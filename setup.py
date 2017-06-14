#!/usr/bin/env python3

from setuptools import setup
from setuptools.command.build_py import build_py
from distutils import log
from scudcloud.version import __version__
import glob
import os

class MinifyJsBuildCommand(build_py):
    """
    Processes JavaScript files with jsmin to yield minified versions.
    """
    description = 'Minify JavaScript sources'
    jsdir = os.path.join('scudcloud', 'resources')
    resdir = os.path.join('scudcloud', 'resources')

    def minify(self, source, target):
        import jsmin
        js = jsmin.jsmin(open(source).read())
        with open(target, 'w') as f:
            f.write(js)
        log.info('minified js written to %s' % target)

    def run(self):
        # run this first - creates the target dirs
        build_py.run(self)

        log.info('minifying js under %s' % self.jsdir)
        jsfiles = glob.glob(os.path.join(self.jsdir, '*.js'))
        for jsfile in jsfiles:
            target = os.path.join(self.build_lib, self.resdir, os.path.basename(jsfile))
            self.minify(jsfile, target)

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
      description='ScudCloud is a non official desktop client for Slack',
      entry_points = {
          'gui_scripts': ['scudcloud = scudcloud.__main__:main'],
      },
      keywords = "slack chat im instant_message",
      license = "MIT",
      maintainer='Andrew Stiegmann',
      maintainer_email='andrew.stiegmann@gmail.com',
      package_data = {
          # *.js will be processed separately
          'scudcloud': ['resources/*.css', 'resources/*.html', 'resources/*.png',]
      },
      packages=['scudcloud',],
      requires=['dbus', 'PyQt5',],
      url='https://github.com/raelgc/scudcloud',
      version = __version__,
      setup_requires=['jsmin',],
      cmdclass = {
          'build_py': MinifyJsBuildCommand,
      },
)
