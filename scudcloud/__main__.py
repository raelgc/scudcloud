#!/usr/bin/env python3

import os, sys

# Flexible install dir (we assume that 'resources' is package_data)
#INSTALL_DIR = os.path.dirname(os.path.realpath(__file__))

# Ensure the workind directory containing this file is on the python
# path.  Using the loader causes Python to not add this file to the
# path.  :(
#print("Sys.path is \"%s\"" % str(':'.join(sys.path)))
#print("Appending path: \"%s\"" % INSTALL_DIR)
#sys.path.append(INSTALL_DIR)

from scudcloud.resources import Resources
import scudcloud.scudcloud as sca
from scudcloud.version import __version__

import fcntl, platform, signal, tempfile
from sip import SIP_VERSION_STR
from shutil import copyfile
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

# The ScudCloud QMainWindow
win = None

def main():
    global win
    signal.signal(signal.SIGINT, exit)
    args = parse_arguments()
    appKey = "scudcloud.pid"
    socket = QLocalSocket()
    socket.connectToServer(appKey)
    if socket.isOpen():
        socket.close()
        socket.deleteLater()
        return 0
    socket.deleteLater()
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(Resources.APP_NAME+' Slack')
    app.setWindowIcon(QtGui.QIcon(Resources.get_path('scudcloud.png')))
    try:
        settings_path, cache_path = load_settings(args.confdir, args.cachedir)
    except:
        print("Data directories "+args.confdir+" and "+args.cachedir+" could not be created! Exiting...")
        raise SystemExit()
    minimized = True if args.minimized is True else None
    urgent_hint = True if args.urgent_hint is True else None

    # Let's move the CSS to cachedir to enable additional actions
    copyfile(Resources.get_path('resources.css'), os.path.join(cache_path, 'resources.css'))

    # If there is an qt4 config and not a qt5, let's copy the old one
    qt4_config = os.path.join(settings_path, 'scudcloud.cfg')
    qt5_config = os.path.join(settings_path, 'scudcloud_qt5.cfg')
    if os.path.exists(qt4_config) and not os.path.exists(qt5_config):
        copyfile(qt4_config, qt5_config)

    win = sca.ScudCloud(
        debug=args.debug,
        minimized=minimized,
        urgent_hint=urgent_hint,
        settings_path=settings_path,
        cache_path=cache_path
    )
    app.commitDataRequest.connect(win.setForceClose, type=QtCore.Qt.DirectConnection)

    server = QLocalServer()
    server.newConnection.connect(restore)
    server.listen(appKey)
    win.restore()
    if win.minimized is None:
        win.show()
    sys.exit(app.exec_())

def restore():
    global win
    win.setWindowFlags(win.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    win.showNormal()
    win.setWindowFlags(win.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
    win.showNormal()
    win.activateWindow()

def load_settings(*dirs):
    for d in dirs:
        if not os.path.isdir(d):
            os.makedirs(d)
    if dirs[0] not in sys.path:
        sys.path[0:0] = [dirs[0]]
    return dirs

def parse_arguments():
    from argparse import ArgumentParser
    from os.path import expanduser
    if 'XDG_CONFIG_HOME' in os.environ and os.environ['XDG_CONFIG_HOME']:
        default_confdir = os.path.join(os.environ['XDG_CONFIG_HOME'], 'scudcloud')
    else:
        default_confdir = Resources.DEFAULT_CONFDIR
    if 'XDG_CACHE_HOME' in os.environ and os.environ['XDG_CACHE_HOME']:
        default_cachedir = os.path.join(os.environ['XDG_CACHE_HOME'], 'scudcloud')
    else:
        default_cachedir = Resources.DEFAULT_CACHEDIR
    parser = ArgumentParser()
    parser.add_argument('--confdir',    dest='confdir',      metavar='dir', default=default_confdir,  help="change the configuration directory")
    parser.add_argument('--cachedir',   dest='cachedir',     metavar='dir', default=default_cachedir, help="change the default cache directory")
    parser.add_argument('--debug',      dest='debug',        type=bool,     default=False,            help="enable webkit debug console (default: False)")
    parser.add_argument('--minimized',  dest='minimized',    type=bool,     default=False,            help="start minimized to tray (default: False)")
    parser.add_argument('--urgent-hint',dest='urgent_hint',  type=bool,     default=False,            help="set window manager URGENT hint( default: False)")
    parser.add_argument('--version',    action="store_true",                                          help="print version and exit")
    args = parser.parse_args()
    if args.version:
        versions()
        sys.exit()
    args.confdir = expanduser(args.confdir)
    args.cachedir = expanduser(args.cachedir)
    return args

def versions():
    print("ScudCloud", __version__)
    print("Python", platform.python_version())
    print("Qt", QT_VERSION_STR)
    print("PyQt", PYQT_VERSION_STR)
    print("SIP", SIP_VERSION_STR)

def exit(*args):
    if win is not None:
        win.exit()
    else:
        QtGui.QApplication.quit()

if __name__ == '__main__':
    main()
