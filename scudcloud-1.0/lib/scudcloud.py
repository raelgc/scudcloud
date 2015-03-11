#!/usr/bin/env python3
INSTALL_DIR = "/opt/scudcloud/"
import sys, os
import notify2
from cookiejar import PersistentCookieJar
from leftpane import LeftPane
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
    urgent = False
    messages = 0

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
        self.leftPane = LeftPane(self)
        self.cookiesjar = PersistentCookieJar(self)
        webView = Wrapper(self)
        webView.page().networkAccessManager().setCookieJar(self.cookiesjar)
        self.stackedWidget = QtGui.QStackedWidget()
        self.stackedWidget.addWidget(webView)
        centralWidget = QtGui.QWidget(self)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.leftPane)
        layout.addWidget(self.stackedWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.addMenu()
        self.tray = Systray(self)
        self.systray()
        self.installEventFilter(self)
        if self.identifier is None:
            webView.load(QtCore.QUrl(self.SIGNIN_URL))
        else:
            webView.load(QtCore.QUrl(self.domain()))
        webView.show()

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
                "preferences": self.createAction("Preferences", self.current().preferences),
                "systray":     self.createAction("Close to Tray", self.systray, None, True),
                "addTeam":     self.createAction("Sign in to Another Team", self.current().addTeam),
                "signout":     self.createAction("Signout", self.current().logout),
                "exit":        self.createAction("Quit", self.exit, QKeySequence.Close)
            },
            "edit": {
                "undo":        self.current().pageAction(QtWebKit.QWebPage.Undo),
                "redo":        self.current().pageAction(QtWebKit.QWebPage.Redo),
                "cut":         self.current().pageAction(QtWebKit.QWebPage.Cut),
                "copy":        self.current().pageAction(QtWebKit.QWebPage.Copy),
                "paste":       self.current().pageAction(QtWebKit.QWebPage.Paste),
                "reload":      self.current().pageAction(QtWebKit.QWebPage.Reload)
            },
            "help": {
                "help":       self.createAction("Help and Feedback", self.current().help, QKeySequence.HelpContents),
                "center":     self.createAction("Slack Help Center", self.current().helpCenter),
                "about":      self.createAction("About", self.current().about)
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

    def current(self):
        return self.stackedWidget.currentWidget()

    def teams(self, teams):
        if teams is not None and len(teams) > 1:
            self.leftPane.show()
            for t in teams:
                self.leftPane.addTeam(t['id'], t['team_name'], t['team_url'], t == teams[0])

    def switchTo(self, url):
        index = -1
        for i in range(0, self.stackedWidget.count()):
            if self.stackedWidget.widget(i).url().toString().startswith(url):
                index = i
                break
        if index != -1:
            self.stackedWidget.setCurrentIndex(index)
        else:
            webView = Wrapper(self)
            webView.page().networkAccessManager().setCookieJar(self.cookiesjar)
            webView.load(QtCore.QUrl(url))
            webView.show()
            self.stackedWidget.addWidget(webView)
            self.stackedWidget.setCurrentWidget(webView)
        self.quicklist(self.current().listChannels())

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.focusInEvent(event)
        return True

    def focusInEvent(self, event):
        print("Focus in!")
        self.launcher.set_property("urgent", False)
        self.tray.stopAlert()
        self.urgent = False

    def titleChanged(self):
        self.setWindowTitle(self.current().title())

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
                        item.connect(Dbusmenu.MENUITEM_SIGNAL_ITEM_ACTIVATED, self.current().openChannel)
                        ql.child_append(item)
                self.launcher.set_property("quicklist", ql)

    def notify(self, title, message):
        notice = notify2.Notification(title, message, INSTALL_DIR+"resources/scudcloud.png")
        notice.show()
        self.alert()

    def alert(self):
        print("Trying to alert...")
        if not self.isActiveWindow() and not self.urgent:
            print("Alerting!")
            self.launcher.set_property("urgent", True)
            self.tray.alert()
            self.urgent = True

    def count(self):
        total = 0
        for i in range(0, self.stackedWidget.count()):
            total+=self.stackedWidget.widget(i).messages
        if total > self.messages:
            self.alert()
        elif 0 == total:
            self.launcher.set_property("count_visible", False)
        else:
            self.launcher.set_property("count", total)
            self.launcher.set_property("count_visible", True)
        self.messages = total
