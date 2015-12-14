import sys, os, time
from cookiejar import PersistentCookieJar
from leftpane import LeftPane
from notifier import Notifier
from resources import Resources
from speller import Speller
from systray import Systray
from wrapper import Wrapper
from threading import Thread
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.Qt import QApplication, QKeySequence, QTimer
from PyQt4.QtCore import QUrl, QSettings
from PyQt4.QtWebKit import QWebSettings, QWebPage
from PyQt4.QtNetwork import QNetworkDiskCache

# Auto-detection of Unity and Dbusmenu in gi repository
try:
    from gi.repository import Unity, Dbusmenu
except ImportError:
    Unity = None
    Dbusmenu = None
    from launcher import DummyLauncher 

class ScudCloud(QtGui.QMainWindow):

    plugins = True
    debug = False
    forceClose = False
    messages = 0
    speller = Speller()

    def __init__(self, parent = None, settings_path = ""):
        super(ScudCloud, self).__init__(parent)
        self.setWindowTitle('ScudCloud')
        self.settings_path = settings_path
        self.notifier = Notifier(Resources.APP_NAME, Resources.get_path('scudcloud.png'))
        self.settings = QSettings(self.settings_path + '/scudcloud.cfg', QSettings.IniFormat)
        self.identifier = self.settings.value("Domain")
        if Unity is not None:
            self.launcher = Unity.LauncherEntry.get_for_desktop_id("scudcloud.desktop")
        else:
            self.launcher = DummyLauncher(self)
        self.webSettings()
        self.leftPane = LeftPane(self)
        self.stackedWidget = QtGui.QStackedWidget()
        centralWidget = QtGui.QWidget(self)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.leftPane)
        layout.addWidget(self.stackedWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.startURL = Resources.SIGNIN_URL
        if self.identifier is not None:
            self.startURL = self.domain()
        self.addWrapper(self.startURL)
        self.addMenu()
        self.tray = Systray(self)
        self.systray(ScudCloud.minimized)
        self.installEventFilter(self)
        self.statusBar().showMessage('Loading Slack...')

    def addWrapper(self, url):
        webView = Wrapper(self)
        webView.page().networkAccessManager().setCookieJar(self.cookiesjar)
        webView.page().networkAccessManager().setCache(self.diskCache)
        webView.load(QtCore.QUrl(url))
        webView.show()
        self.stackedWidget.addWidget(webView)
        self.stackedWidget.setCurrentWidget(webView)

    def webSettings(self):
        self.cookiesjar = PersistentCookieJar(self)
        self.zoom = self.readZoom()
        # Required by Youtube videos (HTML5 video support only on Qt5)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, self.plugins)
        # We don't want Java
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavaEnabled, False)
        # Enabling Local Storage (now required by Slack)
        QWebSettings.globalSettings().setAttribute(QWebSettings.LocalStorageEnabled, True)
        # We need browsing history (required to not limit LocalStorage)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PrivateBrowsingEnabled, False)
        # Enabling Cache
        self.diskCache = QNetworkDiskCache(self)
        self.diskCache.setCacheDirectory(self.settings_path)
        # Required for copy and paste clipboard integration
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        # Enabling Inspeclet only when --debug=True (requires more CPU usage)
        QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, self.debug)

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def toggleMenuBar(self):
        menu = self.menuBar()
        state = menu.isHidden()
        menu.setVisible(state)
        if state:
            self.settings.setValue("Menu", "False")
        else:
            self.settings.setValue("Menu", "True")

    def restore(self):
        geometry = self.settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        windowState = self.settings.value("windowState")
        if windowState is not None:
            self.restoreState(windowState)
        else:
            self.setWindowState(QtCore.Qt.WindowMaximized)

    def systray(self, show=None):
        if show is None:
            show = self.settings.value("Systray") == "True"
        if show:
            self.tray.show()
            self.menus["file"]["close"].setEnabled(True)
            self.settings.setValue("Systray", "True")
        else:
            self.tray.setVisible(False)
            self.menus["file"]["close"].setEnabled(False)
            self.settings.setValue("Systray", "False")

    def readZoom(self):
        default = 1
        if self.settings.value("Zoom") is not None:
            default = float(self.settings.value("Zoom"))
        return default

    def setZoom(self, factor=1):
        if factor > 0:
            for i in range(0, self.stackedWidget.count()):
                widget = self.stackedWidget.widget(i)
                widget.setZoomFactor(factor)
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
                "preferences": self.createAction("Preferences", lambda : self.current().preferences()),
                "systray":     self.createAction("Close to Tray", self.systray, None, True),
                "addTeam":     self.createAction("Sign in to Another Team", lambda : self.switchTo(Resources.SIGNIN_URL)),
                "signout":     self.createAction("Signout", lambda : self.current().logout()),
                "close":       self.createAction("Close", self.close, QKeySequence.Close),
                "exit":        self.createAction("Quit", self.exit, QKeySequence.Quit)
            },
            "edit": {
            },
            "view": {
                "zoomin":      self.createAction("Zoom In", self.zoomIn, QKeySequence.ZoomIn),
                "zoomout":     self.createAction("Zoom Out", self.zoomOut, QKeySequence.ZoomOut),
                "reset":       self.createAction("Reset", self.zoomReset, QtCore.Qt.CTRL + QtCore.Qt.Key_0),
                "fullscreen":  self.createAction("Toggle Full Screen", self.toggleFullScreen, QtCore.Qt.Key_F11),
                "hidemenu":    self.createAction("Toggle Menubar", self.toggleMenuBar, QtCore.Qt.Key_F12)
            },
            "help": {
                "help":       self.createAction("Help and Feedback", lambda : self.current().help(), QKeySequence.HelpContents),
                "center":     self.createAction("Slack Help Center", lambda : self.current().helpCenter()),
                "about":      self.createAction("About", lambda : self.current().about())
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
        fileMenu.addAction(self.menus["file"]["close"])
        fileMenu.addAction(self.menus["file"]["exit"])
        self.editMenu = menu.addMenu("&Edit")
        self.updateEditMenu()
        viewMenu = menu.addMenu("&View")
        viewMenu.addAction(self.menus["view"]["zoomin"])
        viewMenu.addAction(self.menus["view"]["zoomout"])
        viewMenu.addAction(self.menus["view"]["reset"])
        viewMenu.addSeparator()
        viewMenu.addAction(self.menus["view"]["fullscreen"])
        if Unity is None:
            viewMenu.addAction(self.menus["view"]["hidemenu"])
        helpMenu = menu.addMenu("&Help")
        helpMenu.addAction(self.menus["help"]["help"])
        helpMenu.addAction(self.menus["help"]["center"])
        helpMenu.addSeparator()
        helpMenu.addAction(self.menus["help"]["about"])
        self.enableMenus(False)
        showSystray = self.settings.value("Systray") == "True"
        self.menus["file"]["systray"].setChecked(showSystray)
        self.menus["file"]["close"].setEnabled(showSystray)
        # Restore menu visibility
        visible = self.settings.value("Menu")
        if visible is not None and visible == "False":
            menu.setVisible(False)

    def enableMenus(self, enabled):
        self.menus["file"]["preferences"].setEnabled(enabled == True)
        self.menus["file"]["addTeam"].setEnabled(enabled == True)
        self.menus["file"]["signout"].setEnabled(enabled == True)
        self.menus["help"]["help"].setEnabled(enabled == True)

    def updateEditMenu(self):
        self.editMenu.clear()
        self.menus["edit"] = {
            "undo":        self.current().pageAction(QtWebKit.QWebPage.Undo),
            "redo":        self.current().pageAction(QtWebKit.QWebPage.Redo),
            "cut":         self.current().pageAction(QtWebKit.QWebPage.Cut),
            "copy":        self.current().pageAction(QtWebKit.QWebPage.Copy),
            "paste":       self.current().pageAction(QtWebKit.QWebPage.Paste),
            "back":        self.current().pageAction(QtWebKit.QWebPage.Back),
            "forward":     self.current().pageAction(QtWebKit.QWebPage.Forward),
            "reload":      self.current().pageAction(QtWebKit.QWebPage.Reload)
        }
        self.editMenu.addAction(self.menus["edit"]["undo"])
        self.editMenu.addAction(self.menus["edit"]["redo"])
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.menus["edit"]["cut"])
        self.editMenu.addAction(self.menus["edit"]["copy"])
        self.editMenu.addAction(self.menus["edit"]["paste"])
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.menus["edit"]["back"])
        self.editMenu.addAction(self.menus["edit"]["forward"])
        self.editMenu.addAction(self.menus["edit"]["reload"])

    def createAction(self, text, slot, shortcut=None, checkable=False):
        action = QtGui.QAction(text, self)
        action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
            self.addAction(action)
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
        for t in teams:
            # If team_icon is not present, it's because team is already connected
            if 'team_icon' in t:
                self.leftPane.addTeam(t['id'], t['team_name'], t['team_url'], t['team_icon']['image_44'], t == teams[0])
        if len(teams) > 1:
            self.leftPane.show()

    def switchTo(self, url):
        exists = False
        for i in range(0, self.stackedWidget.count()):
            if self.stackedWidget.widget(i).url().toString().startswith(url):
                self.stackedWidget.setCurrentIndex(i)
                self.quicklist(self.current().listChannels())
                self.current().setFocus()
                self.leftPane.click(i)
                exists = True
                break
        if not exists:
            self.addWrapper(url)
        self.updateEditMenu()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.focusInEvent(event)
        if event.type() == QtCore.QEvent.KeyPress:
            # Ctrl + <n>
            modifiers = QtGui.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ControlModifier:
                if event.key() == QtCore.Qt.Key_1:   self.leftPane.click(0)
                elif event.key() == QtCore.Qt.Key_2: self.leftPane.click(1)
                elif event.key() == QtCore.Qt.Key_3: self.leftPane.click(2)
                elif event.key() == QtCore.Qt.Key_4: self.leftPane.click(3)
                elif event.key() == QtCore.Qt.Key_5: self.leftPane.click(4)
                elif event.key() == QtCore.Qt.Key_6: self.leftPane.click(5)
                elif event.key() == QtCore.Qt.Key_7: self.leftPane.click(6)
                elif event.key() == QtCore.Qt.Key_8: self.leftPane.click(7)
                elif event.key() == QtCore.Qt.Key_9: self.leftPane.click(8)
                # Ctrl + Tab
                elif event.key() == QtCore.Qt.Key_Tab: self.leftPane.clickNext(1)
            # Ctrl + BackTab
            if (modifiers & QtCore.Qt.ControlModifier) and (modifiers & QtCore.Qt.ShiftModifier):
                if event.key() == QtCore.Qt.Key_Backtab: self.leftPane.clickNext(-1)
            # Ctrl + Shift + <key>
            if (modifiers & QtCore.Qt.ShiftModifier) and (modifiers & QtCore.Qt.ShiftModifier):
                if event.key() == QtCore.Qt.Key_V: self.current().createSnippet()
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
            # Let's save the first team registered as default
            qUrl = self.stackedWidget.widget(0).url()
            if self.identifier is None and Resources.MESSAGES_URL_RE.match(qUrl.toString()):
                self.settings.setValue("Domain", 'https://'+qUrl.host())

    def show(self):
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.setVisible(True)

    def exit(self):
        self.forceClose = True
        self.close()

    def quicklist(self, channels):
        if Dbusmenu is not None:
            if channels is not None:
                ql = Dbusmenu.Menuitem.new()
                self.launcher.set_property("quicklist", ql)
                for c in channels:
                    if c['is_member']:
                        item = Dbusmenu.Menuitem.new ()
                        item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "#"+c['name'])
                        item.property_set ("id", c['name'])
                        item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
                        item.connect(Dbusmenu.MENUITEM_SIGNAL_ITEM_ACTIVATED, self.current().openChannel)
                        ql.child_append(item)
                self.launcher.set_property("quicklist", ql)

    def notify(self, title, message, icon=None):
        self.notifier.notify(title, message, icon)
        self.alert()

    def alert(self):
        if not self.isActiveWindow():
            self.launcher.set_property("urgent", True)
            self.tray.alert()

    def count(self):
        total = 0
        for i in range(0, self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            messages = widget.highlights
            if messages == 0:
                self.leftPane.stopAlert(widget.team())
            else:
                self.leftPane.alert(widget.team())
            if messages is not None:
                total+=messages
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
