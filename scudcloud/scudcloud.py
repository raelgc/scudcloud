from scudcloud.cookiejar import PersistentCookieJar
from scudcloud.leftpane import LeftPane
from scudcloud.notifier import Notifier
from scudcloud.resources import Resources
from scudcloud.systray import Systray
from scudcloud.wrapper import Wrapper
from scudcloud.speller import Speller

import sys, os, time

from threading import Thread
from PyQt5 import QtCore, QtGui, QtWebKit, QtWidgets, QtWebKitWidgets
from PyQt5.Qt import QApplication, QKeySequence, QTimer
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebPage
from PyQt5.QtNetwork import QNetworkDiskCache

# Auto-detection of dbus and dbus.mainloop.qt
try:
    import dbus
    from dbus.mainloop.pyqt5 import DBusQtMainLoop
except ImportError:
    DBusQtMainLoop = None

# Auto-detection of Unity and Dbusmenu in gi repository
try:
    import gi
    gi.require_version('Unity', '7.0')
    from gi.repository import Unity, Dbusmenu
except (ImportError, ValueError):
    Unity = None
    Dbusmenu = None
    from scudcloud.launcher import DummyLauncher

class ScudCloud(QtWidgets.QMainWindow):

    forceClose = False
    messages = 0
    speller = Speller()
    title = 'ScudCloud'

    def __init__(self, debug = False, minimized = None, urgent_hint = None, settings_path = '', cache_path = ''):
        super(ScudCloud, self).__init__(None)
        self.debug = debug
        self.minimized = minimized
        self.urgent_hint = urgent_hint
        self.setWindowTitle(self.title)
        self.settings_path = settings_path
        self.cache_path = cache_path
        self.notifier = Notifier(Resources.APP_NAME, Resources.get_path('scudcloud.png'))
        self.settings = QSettings(self.settings_path + '/scudcloud_qt5.cfg', QSettings.IniFormat)
        self.notifier.enabled = self.settings.value('Notifications', defaultValue=True, type=bool)
        self.identifier = self.settings.value("Domain")
        if Unity is not None:
            self.launcher = Unity.LauncherEntry.get_for_desktop_id("scudcloud.desktop")
        else:
            self.launcher = DummyLauncher(self)
        self.webSettings()
        self.snippetsSettings()
        self.leftPane = LeftPane(self)
        self.stackedWidget = QtWidgets.QStackedWidget()
        centralWidget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.leftPane)
        layout.addWidget(self.stackedWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.startURL = Resources.SIGNIN_URL
        if self.identifier is not None:
            if isinstance(self.identifier, str):
                self.domains = self.identifier.split(",")
            else:
                self.domains = self.identifier
            self.startURL = self.normalize(self.domains[0])
        else:
            self.domains = []
        self.addWrapper(self.startURL)
        self.addMenu()
        self.tray = Systray(self)
        self.systray(self.minimized)
        self.installEventFilter(self)
        self.statusBar().showMessage('Loading Slack...')
        self.tickler = QTimer(self)
        self.tickler.setInterval(1800000)
        # Watch for ScreenLock events
        if DBusQtMainLoop is not None:
            DBusQtMainLoop(set_as_default=True)
            sessionBus = dbus.SessionBus()
            # Ubuntu 12.04 and other distros
            sessionBus.add_match_string("type='signal',interface='org.gnome.ScreenSaver'")
            # Ubuntu 14.04 and above
            sessionBus.add_match_string("type='signal',interface='com.ubuntu.Upstart0_6'")
            sessionBus.add_message_filter(self.screenListener)
            self.tickler.timeout.connect(self.sendTickle)
        # If dbus is not present, tickler timer will act like a blocker to not send tickle too often
        else:
            self.tickler.setSingleShot(True)
        self.tickler.start()

    def screenListener(self, bus, message):
        event = message.get_member()
        # "ActiveChanged" for Ubuntu 12.04 and other distros. "EventEmitted" for Ubuntu 14.04 and above
        if event == "ActiveChanged" or event == "EventEmitted":
            arg = message.get_args_list()[0]
            # True for Ubuntu 12.04 and other distros. "desktop-lock" for Ubuntu 14.04 and above
            if (arg == True or arg == "desktop-lock") and self.tickler.isActive():
                self.tickler.stop()
            elif (arg == False or arg == "desktop-unlock") and not self.tickler.isActive():
                self.sendTickle()
                self.tickler.start()

    def sendTickle(self):
        for i in range(0, self.stackedWidget.count()):
            self.stackedWidget.widget(i).sendTickle()

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
        # We don't want Flash (it causes a lot of trouble in some distros)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, False)
        # We don't need Java
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavaEnabled, False)
        # Enabling Local Storage (now required by Slack)
        QWebSettings.globalSettings().setAttribute(QWebSettings.LocalStorageEnabled, True)
        # We need browsing history (required to not limit LocalStorage)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PrivateBrowsingEnabled, False)
        # Enabling Cache
        self.diskCache = QNetworkDiskCache(self)
        self.diskCache.setCacheDirectory(self.cache_path)
        # Required for copy and paste clipboard integration
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        # Enabling Inspeclet only when --debug=True (requires more CPU usage)
        QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, self.debug)

    def snippetsSettings(self):
        self.disable_snippets = self.settings.value("Snippets")
        if self.disable_snippets is not None:
            self.disable_snippets = self.disable_snippets == "False"
        else:
            self.disable_snippets = False
        if self.disable_snippets:
            disable_snippets_css = ''
            with open(Resources.get_path('disable_snippets.css'), 'r') as f:
                disable_snippets_css = f.read()
            with open(os.path.join(self.cache_path, 'resources.css'), 'a') as f:
                f.write(disable_snippets_css)

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

    def addTeam(self):
        self.switchTo(Resources.SIGNIN_URL)

    def addMenu(self):
        # We'll register the webpage shorcuts with the window too (Fixes #338)
        undo = self.current().pageAction(QWebPage.Undo)
        redo = self.current().pageAction(QWebPage.Redo)
        cut = self.current().pageAction(QWebPage.Cut)
        copy = self.current().pageAction(QWebPage.Copy)
        paste = self.current().pageAction(QWebPage.Paste)
        back = self.current().pageAction(QWebPage.Back)
        forward = self.current().pageAction(QWebPage.Forward)
        reload = self.current().pageAction(QWebPage.Reload)
        self.menus = {
            "file": {
                "preferences": self.createAction("Preferences", lambda : self.current().preferences()),
                "systray":     self.createAction("Close to Tray", self.systray, None, True),
                "addTeam":     self.createAction("Sign in to Another Team", lambda : self.addTeam()),
                "signout":     self.createAction("Signout", lambda : self.current().logout()),
                "close":       self.createAction("Close", self.close, QKeySequence.Close),
                "exit":        self.createAction("Quit", self.exit, QKeySequence.Quit)
            },
            "edit": {
                "undo":        self.createAction(undo.text(), lambda : self.current().page().triggerAction(QWebPage.Undo), undo.shortcut()),
                "redo":        self.createAction(redo.text(), lambda : self.current().page().triggerAction(QWebPage.Redo), redo.shortcut()),
                "cut":         self.createAction(cut.text(), lambda : self.current().page().triggerAction(QWebPage.Cut), cut.shortcut()),
                "copy":        self.createAction(copy.text(), lambda : self.current().page().triggerAction(QWebPage.Copy), copy.shortcut()),
                "paste":       self.createAction(paste.text(), lambda : self.current().page().triggerAction(QWebPage.Paste), paste.shortcut()),
                "back":        self.createAction(back.text(), lambda : self.current().page().triggerAction(QWebPage.Back), back.shortcut()),
                "forward":     self.createAction(forward.text(), lambda : self.current().page().triggerAction(QWebPage.Forward), forward.shortcut()),
                "reload":      self.createAction(reload.text(), lambda : self.current().page().triggerAction(QWebPage.Reload), reload.shortcut()),
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
        editMenu = menu.addMenu("&Edit")
        editMenu.addAction(self.menus["edit"]["undo"])
        editMenu.addAction(self.menus["edit"]["redo"])
        editMenu.addSeparator()
        editMenu.addAction(self.menus["edit"]["cut"])
        editMenu.addAction(self.menus["edit"]["copy"])
        editMenu.addAction(self.menus["edit"]["paste"])
        editMenu.addSeparator()
        editMenu.addAction(self.menus["edit"]["back"])
        editMenu.addAction(self.menus["edit"]["forward"])
        editMenu.addAction(self.menus["edit"]["reload"])
        viewMenu = menu.addMenu("&View")
        viewMenu.addAction(self.menus["view"]["zoomin"])
        viewMenu.addAction(self.menus["view"]["zoomout"])
        viewMenu.addAction(self.menus["view"]["reset"])
        viewMenu.addSeparator()
        viewMenu.addAction(self.menus["view"]["fullscreen"])
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

    def createAction(self, text, slot, shortcut=None, checkable=False):
        action = QtWidgets.QAction(text, self)
        action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
            self.addAction(action)
        if checkable:
            action.setCheckable(True)
        return action

    def normalize(self, url):
        if url.endswith(".slack.com"):
            url+= "/"
        elif not url.endswith(".slack.com/"):
            url = "https://"+url+".slack.com/"
        return url

    def current(self):
        return self.stackedWidget.currentWidget()

    def teams(self, teams):
        if len(self.domains) == 0:
            self.domains.append(teams[0]['team_url'])
        team_list = [t['team_url'] for t in teams]
        for t in teams:
            for i in range(0, len(self.domains)):
                self.domains[i] = self.normalize(self.domains[i])
                # When team_icon is missing, the team already exists (Fixes #381, #391)
                if 'team_icon' in t:
                    if self.domains[i] in team_list:
                        add = next(item for item in teams if item['team_url'] == self.domains[i])
                        if 'team_icon' in add:
                            self.leftPane.addTeam(add['id'], add['team_name'], add['team_url'], add['team_icon']['image_44'], add == teams[0])
                            # Adding new teams and saving loading positions
                            if t['team_url'] not in self.domains:
                                self.leftPane.addTeam(t['id'], t['team_name'], t['team_url'], t['team_icon']['image_44'], t == teams[0])
                                self.domains.append(t['team_url'])
                                self.settings.setValue("Domain", self.domains)
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

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.focusInEvent(event)
        if event.type() == QtCore.QEvent.KeyPress:
            # Ctrl + <n>
            modifiers = QtWidgets.QApplication.keyboardModifiers()
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
        return QtWidgets.QMainWindow.eventFilter(self, obj, event);

    def focusInEvent(self, event):
        self.launcher.set_property("urgent", False)
        self.tray.stopAlert()
        # Let's tickle all teams on window focus, but only if tickle was not fired in last 30 minutes
        if DBusQtMainLoop is None and not self.tickler.isActive():
            self.sendTickle()
            self.tickler.start()

    def titleChanged(self):
        self.setWindowTitle(self.current().title())

    def setForceClose(self):
        self.forceClose = True

    def closeEvent(self, event):
        if not self.forceClose and self.settings.value("Systray") == "True":
            self.hide()
            event.ignore()
        else:
            self.cookiesjar.save()
            self.settings.setValue("Domain", self.domains)
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("Domain", self.domains)
        self.forceClose = False

    def show(self):
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.setVisible(True)

    def exit(self):
        # Make sure tray is not visible (Fixes #513)
        self.tray.setVisible(False)
        self.setForceClose()
        self.close()

    def quicklist(self, channels):
        if Dbusmenu is not None:
            if channels is not None:
                ql = Dbusmenu.Menuitem.new()
                self.launcher.set_property("quicklist", ql)
                for c in channels:
                    if hasattr(c, '__getitem__') and c['is_member']:
                        item = Dbusmenu.Menuitem.new ()
                        item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "#"+c['name'])
                        item.property_set ("id", c['name'])
                        item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
                        item.connect(Dbusmenu.MENUITEM_SIGNAL_ITEM_ACTIVATED, self.current().openChannel)
                        ql.child_append(item)
                self.launcher.set_property("quicklist", ql)

    def notify(self, title, message, icon):
        if self.debug: print("Notification: title [{}] message [{}] icon [{}]".format(title, message, icon))
        self.notifier.notify(title, message, icon)
        self.alert()

    def alert(self):
        if not self.isActiveWindow():
            self.launcher.set_property("urgent", True)
            self.tray.alert()
        if self.urgent_hint is True:
            QApplication.alert(self)

    def count(self):
        total = 0
        unreads = 0
        for i in range(0, self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            highlights = widget.highlights
            unreads+= widget.unreads
            total+=highlights
        if total > self.messages:
            self.alert()
        if 0 == total:
            self.launcher.set_property("count_visible", False)
            self.tray.setCounter(0)
            if unreads > 0:
                self.setWindowTitle("*{}".format(self.title))
            else:
                self.setWindowTitle(self.title)
        else:
            self.tray.setCounter(total)
            self.launcher.set_property("count", total)
            self.launcher.set_property("count_visible", True)
            self.setWindowTitle("[{}]{}".format(str(total), self.title))
        self.messages = total
