#!/usr/bin/env python3
INSTALL_DIR = "/opt/scudcloud/"
import sys, os
import notify2
from cookiejar import PersistentCookieJar
from systray import Systray
from wrapper import Wrapper
if "ubuntu"==os.environ.get('DESKTOP_SESSION'):
    from gi.repository import Unity, GObject, Dbusmenu
else:
    from launcher import Launcher
from os.path import expanduser
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.Qt import QApplication, QKeySequence
from PyQt4.QtCore import QUrl, QSettings

class ScudCloud(QtGui.QMainWindow):

    APP_NAME = "ScudCloud Client"
    SIGNIN_URL = "https://slack.com/signin"
    debug = False
    forceClose = False

    def __init__(self, parent=None):
        super(ScudCloud, self).__init__(parent)
        self.setWindowTitle('ScudCloud')
        notify2.init(self.APP_NAME)
        self.settings = QSettings(expanduser("~")+"/.scudcloud", QSettings.IniFormat)
        self.identifier = self.settings.value("Domain")
        if "ubuntu"==os.environ.get('DESKTOP_SESSION'):
            self.launcher = Unity.LauncherEntry.get_for_desktop_id("scudcloud.desktop")
        else:
            self.launcher = Launcher(self)
        self.webView = Wrapper(self)
        self.cookiesjar = PersistentCookieJar(self)
        self.webView.page().networkAccessManager().setCookieJar(self.cookiesjar)
        self.setCentralWidget(self.webView)
        self.addMenu()
        self.tray = Systray(self)
        self.systray()
        if self.identifier is None:
            self.webView.load(QtCore.QUrl(self.SIGNIN_URL))
        else:
            self.webView.load(QtCore.QUrl(self.domain()))
        self.webView.show()

    def systray(self, show=None):
        if show is None: 
            show = self.settings.value("Systray") == "True"
        if show:
            self.tray.show()
            self.settings.setValue("Systray", "True")
        else:
            self.tray.setVisible(False)
            self.settings.setValue("Systray", "False")

    def addMenu(self):
        self.menus = {
            "file": {
                "preferences": self.createAction("Preferences", self.webView.preferences),
                "systray":     self.createAction("Close to Tray", self.systray, None, True),
                "addTeam":     self.createAction("Sign in to Another Team", self.webView.addTeam),
                "signout":     self.createAction("Signout", self.webView.logout),
                "exit":        self.createAction("Quit", self.exit, QKeySequence.Close)
            },
            "edit": {
                "undo":        self.webView.pageAction(QtWebKit.QWebPage.Undo),
                "redo":        self.webView.pageAction(QtWebKit.QWebPage.Redo),
                "cut":         self.webView.pageAction(QtWebKit.QWebPage.Cut),
                "copy":        self.webView.pageAction(QtWebKit.QWebPage.Copy),
                "paste":       self.webView.pageAction(QtWebKit.QWebPage.Paste),
                "reload":      self.webView.pageAction(QtWebKit.QWebPage.Reload)
            },
            "help": {
                "help":       self.createAction("Help and Feedback", self.webView.help, QKeySequence.HelpContents),
                "center":     self.createAction("Slack Help Center", self.webView.helpCenter),
                "about":      self.createAction("About", self.webView.about)
             }
        }
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        fileMenu.addAction(self.menus["file"]["preferences"])
        fileMenu.addAction(self.menus["file"]["systray"])
        fileMenu.addSeparator()
        fileMenu.addAction(self.menus["file"]["addTeam"])
        fileMenu.addAction(self.menus["file"]["signout"])
        fileMenu.addSeparator()
        fileMenu.addAction(self.menus["file"]["exit"])
        editMenu = menu.addMenu("&Edit")
        editMenu.addAction(self.menus["edit"]["undo"])
        editMenu.addAction(self.menus["edit"]["redo"])
        editMenu.addSeparator()
        editMenu.addAction(self.menus["edit"]["cut"])
        editMenu.addAction(self.menus["edit"]["copy"])
        editMenu.addAction(self.menus["edit"]["paste"])
        editMenu.addSeparator()
        editMenu.addAction(self.menus["edit"]["reload"])
        helpMenu = menu.addMenu("&Help")
        helpMenu.addAction(self.menus["help"]["help"])
        helpMenu.addAction(self.menus["help"]["center"])
        helpMenu.addSeparator()
        helpMenu.addAction(self.menus["help"]["about"])
        self.enableMenus(False)
        self.menus["file"]["systray"].setChecked(self.settings.value("Systray") == "True")

    def enableMenus(self, enabled):
        self.menus["file"]["preferences"].setEnabled(enabled)
        self.menus["file"]["addTeam"].setEnabled(enabled)
        self.menus["file"]["signout"].setEnabled(enabled)
        self.menus["help"]["help"].setEnabled(enabled)

    def createAction(self, text, slot, shortcut=None, checkable=False):
        action = QtGui.QAction(text, self)        
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def domain(self):
        if self.identifier.endswith(".slack.com"):
            return self.identifier
        else:
            return "https://"+self.identifier+".slack.com"

    def focusInEvent(self, event):
        self.launcher.set_property("urgent", False)
        self.tray.stopAlert()

    def titleChanged(self):
        self.setWindowTitle(self.webView.title())

    def closeEvent(self, event):
        if not self.forceClose and self.settings.value("Systray") == "True":
            self.hide()
            event.ignore()
        else:
            self.cookiesjar.save()

    def show(self):
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.setVisible(True)

    def exit(self):
        self.forceClose = True
        self.close()

    def quicklist(self, channels):
        if "ubuntu"==os.environ.get('DESKTOP_SESSION'):
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
                self.tray.alert()
        elif 0 == value:
            self.launcher.set_property("urgent", False)
            self.launcher.set_property("count_visible", False)
            self.tray.stopAlert()
        else:
            self.launcher.set_property("count", value)
            self.launcher.set_property("count_visible", True)
        self.webView.messages = value
