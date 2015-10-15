from PyQt4 import QtCore, QtGui
from resources import Resources
import scudcloud 

class Systray(QtGui.QSystemTrayIcon):

    urgent = False

    def __init__(self, window):
        super(Systray, self).__init__(QtGui.QIcon.fromTheme("scudcloud"), window)
        self.connect(self, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.activatedEvent)
        self.window = window
        self.setToolTip('ScudCloud')
        self.menu = QtGui.QMenu(self.window)
        self.menu.addAction('Show', self.restore)
        if scudcloud.Unity is None:
            self.menu.addAction('Toggle Menubar', self.toggleMenuBar)
        self.menu.addSeparator()
        self.menu.addAction(self.window.menus["file"]["preferences"])
        self.menu.addAction(self.window.menus["help"]["about"])
        self.menu.addSeparator()
        self.menu.addAction(self.window.menus["file"]["exit"])
        self.setContextMenu(self.menu)

    def alert(self):
        if not self.urgent:
            self.urgent = True
            self.setIcon(QtGui.QIcon.fromTheme("scudcloud-attention"))

    def stopAlert(self):
        self.urgent = False
        self.setIcon(QtGui.QIcon.fromTheme("scudcloud"))

    def setCounter(self, i):
        if 0 == i:
            if True == self.urgent:
                self.setIcon(QtGui.QIcon.fromTheme("scudcloud-attention"))
            else:
                self.setIcon(QtGui.QIcon.fromTheme("scudcloud"))
        elif i > 0 and i < 10:
            self.setIcon(QtGui.QIcon.fromTheme("scudcloud-attention-"+str(int(i))))
        elif i > 9:
            self.setIcon(QtGui.QIcon.fromTheme("scudcloud-attention-9-plus"))

    def restore(self):
        self.window.show()
        self.stopAlert()

    def toggleMenuBar(self):
        self.window.toggleMenuBar()

    def activatedEvent(self, reason):
        if reason in [QtGui.QSystemTrayIcon.MiddleClick, QtGui.QSystemTrayIcon.Trigger]:
            if self.window.isHidden() or self.window.isMinimized() or not self.window.isActiveWindow():
                self.restore()
            else:
                self.window.hide()
