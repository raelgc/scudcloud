from PyQt4 import QtCore, QtGui

class Systray(QtGui.QSystemTrayIcon):
    def __init__(self, window):
        super(Systray, self).__init__(QtGui.QIcon.fromTheme("scudcloud"), window)
        QtCore.QObject.connect(self, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.activatedEvent)
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

    def activatedEvent(self, reason):
        if reason in [QtGui.QSystemTrayIcon.MiddleClick, QtGui.QSystemTrayIcon.Trigger]:
            if self.window.isHidden():
                self.restore()
            else:
                if self.window.isMinimized():
                    self.restore()
                else:
                    self.window.hide()

