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
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(Resources.APP_NAME+' Slack_SSB')
    app.setWindowIcon(QtGui.QIcon(Resources.get_path('scudcloud.png')))
    try:
        settings_path = load_settings(args.confdir)
    except:
        print("Configuration directory " + args.confdir +\
              " could not be created! Exiting...")
        raise SystemExit()
    minimized = True if args.minimized is True else None

    win = sca.ScudCloud(debug=args.debug, minimized=minimized, settings_path=settings_path)
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

def load_settings(confdir):
    if not os.path.isdir(confdir):
        os.makedirs(confdir)
    if confdir not in sys.path:
        sys.path[0:0] = [confdir]
    return confdir

def parse_arguments():
    from argparse import ArgumentParser
    from os.path import expanduser
    if 'XDG_CONFIG_HOME' in os.environ and os.environ['XDG_CONFIG_HOME']:
        default_confdir = os.environ['XDG_CONFIG_HOME'] + '/scudcloud'
    else:
        default_confdir = '~/.config/scudcloud'
    parser = ArgumentParser()
    parser.add_argument('--confdir',    dest='confdir',      metavar='dir', default=default_confdir, help="change the configuration directory")
    parser.add_argument('--debug',      dest='debug',        type=bool,     default=False,           help="enable webkit debug console (default: False)")
    parser.add_argument('--minimized',  dest='minimized',    type=bool,     default=False,           help="start minimized to tray (default: False)")
    parser.add_argument('--version',    action="store_true",                                         help="print version and exit")
    args = parser.parse_args()
    if args.version:
        versions()
        sys.exit()
    args.confdir = expanduser(args.confdir)
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
