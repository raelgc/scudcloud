from PyQt4 import QtCore, QtGui

class Systray(QtGui.QSystemTrayIcon):
    def __init__(self, window):
        super(Systray, self).__init__(QtGui.QIcon.fromTheme("scudcloud"), window)
        self.window = window
        self.setToolTip(self.window.APP_NAME)
        self.menu = QtGui.QMenu(self.window)
        self.menu.addAction('Show', self.activated)
        self.menu.addAction('Exit', self.window.close)
        self.setContextMenu(self.menu)

    def alert(self):
        self.setIcon(QtGui.QIcon.fromTheme("scudcloud-attention"))

    def stopAlert(self):
        self.setIcon(QtGui.QIcon.fromTheme("scudcloud"))

    def activated(self):
        self.window.setWindowState(self.window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.window.activateWindow()
        self.stopAlert()

