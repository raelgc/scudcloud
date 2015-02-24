#!/usr/bin/env python3
INSTALL_DIR = "/opt/scudcloud/"
import sys, os
sys.path.append(INSTALL_DIR+'lib')
import notify2
from cookiejar import PersistentCookieJar
from wrapper import Wrapper
from gi.repository import Unity, GObject, Dbusmenu
from os.path import expanduser
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.Qt import QApplication
from PyQt4.QtCore import QUrl, QSettings

class ScudCloud(QtGui.QMainWindow):

    APP_NAME = "ScudCloud Client"
    SIGNIN_URL = "https://slack.com/signin"
    debug = False

    def __init__(self, parent=None):
        super(ScudCloud, self).__init__(parent)
        self.setWindowTitle('ScudCloud')
        notify2.init(self.APP_NAME)
        self.settings = QSettings(expanduser("~")+"/.scudcloud", QSettings.IniFormat)
        self.identifier = self.settings.value("Domain")
        self.launcher = Unity.LauncherEntry.get_for_desktop_id("scudcloud.desktop")
        self.webView = Wrapper(self)
        self.cookiesjar = PersistentCookieJar(self)
        self.webView.page().networkAccessManager().setCookieJar(self.cookiesjar)
        self.ui()
        self.webView.load(QtCore.QUrl(self.domain()))
        self.webView.show()

    def ui(self):
        self.resize(800, 600)
        self.centralwidget = QtGui.QWidget(self)
        self.mainLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(0)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.gridLayout = QtGui.QVBoxLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.addWidget(self.webView)
        self.mainLayout.addWidget(self.frame)
        self.setCentralWidget(self.centralwidget)

    def domain(self):
        if self.identifier is None:
            return self.SIGNIN_URL
        else:
            if self.identifier.endswith(".slack.com"):
                return self.identifier
            else:
                return "https://"+self.identifier+".slack.com"

    def focusInEvent(self, event):
        self.launcher.set_property("urgent", False)

    def titleChanged(self):
        self.setWindowTitle(self.webView.title())

    def closeEvent(self, event):
        self.cookiesjar.save()

    def quicklist(self, channels):
        ql = Dbusmenu.Menuitem.new()
        self.launcher.set_property("quicklist", ql)
        if channels is not None:
            for c in channels:
                if c['is_member']:
                    item = Dbusmenu.Menuitem.new ()
                    item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "#"+c['name'])
                    item.property_set ("id", c['name'])
                    item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
                    item.connect(Dbusmenu.MENUITEM_SIGNAL_ITEM_ACTIVATED, self.webView.openChannel)
                    ql.child_append(item)
            self.launcher.set_property("quicklist", ql)

    def notify(self, title, message):
        notice = notify2.Notification(title, message, INSTALL_DIR+"resources/scudcloud.png")
        notice.show()

    def count(self, value):
        if value > self.webView.messages:
            if not self.isActiveWindow():
                self.launcher.set_property("urgent", True)
        elif 0 == value:
            self.launcher.set_property("urgent", False)
            self.launcher.set_property("count_visible", False)
        else:
            self.launcher.set_property("count", value)
            self.launcher.set_property("count_visible", True)
        self.webView.messages = value
