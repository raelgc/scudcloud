#!/usr/bin/env python3
import sys, os
from cookiejar import PersistentCookieJar
from leftpane import LeftPane
from notifier import Notifier
from systray import Systray
from wrapper import Wrapper
from os.path import expanduser
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.Qt import QApplication, QKeySequence
from PyQt4.QtCore import QUrl, QSettings

# Auto-detection of Unity and Dbusmenu in gi repository
try:
    from gi.repository import Unity, Dbusmenu
except ImportError:
    Unity = None
    Dbusmenu = None
    from launcher import DummyLauncher

from resources import get_resource_path

class ScudCloud(QtGui.QMainWindow):

    APP_NAME = "ScudCloud Client"
    SIGNIN_URL = "https://slack.com/signin"
    debug = False
    forceClose = False
    messages = 0

    def __init__(self, parent=None, settings_path=None):
        super(ScudCloud, self).__init__(parent)
        self.setWindowTitle('ScudCloud')
        self.notifier = Notifier(self.APP_NAME, get_resource_path('scudcloud.png'))

        if settings_path is None:
            print("ERROR: Settings path not set!")
            raise SystemExit()
        else:
            self.settings = QSettings(settings_path, QSettings.IniFormat)

        self.identifier = self.settings.value("Domain")
        if Unity is not None:
            self.launcher = Unity.LauncherEntry.get_for_desktop_id("scudcloud.desktop")
        else:
            self.launcher = DummyLauncher(self)
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
        self.zoom()
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

    def zoom(self):
        default = 1
        if self.settings.value("Zoom") is not None:
            default = float(self.settings.value("Zoom"))
        self.current().setZoomFactor(default)

    def setZoom(self, factor=1):
        if factor > 0:
            self.current().setZoomFactor(factor)
            self.settings.setValue("Zoom", factor)

    def zoomIn(self):
        self.setZoom(self.current().zoomFactor() + 0.1)

    def zoomOut(self):
        self.setZoom(self.current().zoomFactor() - 0.1)

    def zoomReset(self):
        self.setZoom()

    def addMenu(self):
        self.menus = {
            "file": {
                "preferences": self.createAction("Preferences", self.current().preferences),
                "systray":     self.createAction("Close to Tray", self.systray, None, True),
                "addTeam":     self.createAction("Sign in to Another Team", self.current().addTeam),
                "signout":     self.createAction("Signout", self.current().logout),
                "exit":        self.createAction("Quit", self.exit, QKeySequence.Quit)
            },
            "edit": {
                "undo":        self.current().pageAction(QtWebKit.QWebPage.Undo),
                "redo":        self.current().pageAction(QtWebKit.QWebPage.Redo),
                "cut":         self.current().pageAction(QtWebKit.QWebPage.Cut),
                "copy":        self.current().pageAction(QtWebKit.QWebPage.Copy),
                "paste":       self.current().pageAction(QtWebKit.QWebPage.Paste),
                "reload":      self.current().pageAction(QtWebKit.QWebPage.Reload)
            },
            "view": {
                "zoomin":      self.createAction("Zoom In", self.zoomIn, QKeySequence.ZoomIn),
                "zoomout":     self.createAction("Zoom Out", self.zoomOut, QKeySequence.ZoomOut),
                "reset":       self.createAction("Reset", self.zoomReset, QtCore.Qt.CTRL + QtCore.Qt.Key_0)
            },
            "help": {
                "help":       self.createAction("Help and Feedback", self.current().help, QKeySequence.HelpContents),
                "center":     self.createAction("Slack Help Center", self.current().helpCenter),
                "about":      self.createAction("About", self.current().about)
             }
        }
        self.createAction("Hide", self.close, QKeySequence.Close)
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
        viewMenu = menu.addMenu("&View")
        viewMenu.addAction(self.menus["view"]["zoomin"])
        viewMenu.addAction(self.menus["view"]["zoomout"])
        viewMenu.addAction(self.menus["view"]["reset"])
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
                try:
                    self.leftPane.addTeam(t['id'], t['team_name'], t['team_url'], t['team_icon']['image_88'], t == teams[0])
                except:
                    self.leftPane.addTeam(t['id'], t['team_name'], t['team_url'], '', t == teams[0])



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
        if event.type() == QtCore.QEvent.KeyPress and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if event.key() == QtCore.Qt.Key_1:   self.leftPane.click(0)
            elif event.key() == QtCore.Qt.Key_2: self.leftPane.click(1)
            elif event.key() == QtCore.Qt.Key_3: self.leftPane.click(2)
            elif event.key() == QtCore.Qt.Key_4: self.leftPane.click(3)
            elif event.key() == QtCore.Qt.Key_5: self.leftPane.click(4)
            elif event.key() == QtCore.Qt.Key_6: self.leftPane.click(5)
            elif event.key() == QtCore.Qt.Key_7: self.leftPane.click(6)
            elif event.key() == QtCore.Qt.Key_8: self.leftPane.click(7)
            elif event.key() == QtCore.Qt.Key_9: self.leftPane.click(8)
        return QtGui.QMainWindow.eventFilter(self, obj, event);

    def focusInEvent(self, event):
        self.launcher.set_property("urgent", False)
        self.tray.stopAlert()

    def titleChanged(self):
        self.setWindowTitle(self.current().title())

    def closeEvent(self, event):
        if not self.forceClose and self.settings.value("Systray") == "True":
            self.hide()
            event.ignore()
        else:
            self.cookiesjar.save()
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())

    def show(self):
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.setVisible(True)

    def exit(self):
        self.forceClose = True
        self.close()

    def quicklist(self, channels):
        if Dbusmenu is not None:
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
        self.notifier.notify(title, message)
        self.alert()

    def alert(self):
        if not self.isActiveWindow():
            self.launcher.set_property("urgent", True)
            self.tray.alert()

    def count(self):
        total = 0
        for i in range(0, self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            if widget.messages == 0:
                self.leftPane.stopAlert(widget.team())
            else:
                self.leftPane.alert(widget.team())
            total+=widget.messages
        if total > self.messages:
            self.alert()
        if 0 == total:
            self.launcher.set_property("count_visible", False)
            self.tray.setCounter(0)
        else:
            self.tray.setCounter(total)
            self.launcher.set_property("count", total)
            self.launcher.set_property("count_visible", True)
        self.messages = total
