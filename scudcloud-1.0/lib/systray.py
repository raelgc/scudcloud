from PyQt4 import QtCore, QtGui

class Systray(QtGui.QSystemTrayIcon):
    def __init__(self, window):
        super(Systray, self).__init__(QtGui.QIcon.fromTheme("scudcloud"), window)
        self.window = window
        self.setToolTip(self.window.APP_NAME)
        self.menu = QtGui.QMenu(self.window)
        self.menu.addAction('Show', self.restore)
        self.menu.addSeparator()
        self.menu.addAction(self.window.menus["file"]["preferences"])
        self.menu.addAction(self.window.menus["help"]["about"])
        self.menu.addSeparator()
        self.menu.addAction(self.window.menus["file"]["exit"])
        self.setContextMenu(self.menu)

    def alert(self):
        self.setIcon(QtGui.QIcon.fromTheme("scudcloud-attention"))

    def stopAlert(self):
        self.setIcon(QtGui.QIcon.fromTheme("scudcloud"))

    def restore(self):
        self.window.show()
        self.stopAlert()

    def activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.restore()
