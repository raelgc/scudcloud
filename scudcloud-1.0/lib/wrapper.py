INSTALL_DIR = "/opt/scudcloud/"
import sys, subprocess
from PyQt4 import QtWebKit, QtGui, QtCore
from PyQt4.Qt import QApplication, QKeySequence
from PyQt4.QtCore import QBuffer, QByteArray, QUrl, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings

class Wrapper(QWebView):

    messages = 0

    def __init__(self, window):
        QWebView.__init__(self)
        self.window = window
        with open (INSTALL_DIR+"resources/scudcloud.js", "r") as f:
             self.js=f.read()
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, self.window.debug)
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.connect(self, SIGNAL("urlChanged(const QUrl&)"), self.urlChanged)
        self.connect(self, SIGNAL("linkClicked(const QUrl&)"), self.linkClicked)
        self.addActions()

    def addActions(self):
        self.pageAction(QtWebKit.QWebPage.Undo).setShortcuts(QKeySequence.Undo)
        self.pageAction(QtWebKit.QWebPage.Redo).setShortcuts(QKeySequence.Redo)
        self.pageAction(QtWebKit.QWebPage.Cut).setShortcuts(QKeySequence.Cut)
        self.pageAction(QtWebKit.QWebPage.Copy).setShortcuts(QKeySequence.Copy)
        self.pageAction(QtWebKit.QWebPage.Paste).setShortcuts(QKeySequence.Paste)
        self.pageAction(QtWebKit.QWebPage.Reload).setShortcuts(QKeySequence.Refresh)

    def call(self, function, arg=None):
        if isinstance(arg, str):
            arg = "'"+arg+"'"
        if arg is None:
            arg = ""
        return self.page().currentFrame().evaluateJavaScript("ScudCloud."+function+"("+arg+");")

    def urlChanged(self, qUrl):
        self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(INSTALL_DIR+"/resources/login.css"))
        self.page().currentFrame().addToJavaScriptWindowObject("desktop", self)
        boot_data = self.page().currentFrame().evaluateJavaScript(self.js)
        self.window.quicklist(boot_data['channels'])
        self.window.teams(boot_data['teams'])
        self.window.enableMenus(self.isConnected())
        url = qUrl.toString()
        if self.window.SIGNIN_URL != url and url.endswith(".slack.com/"):
            self.window.settings.setValue("Domain", 'https://'+qUrl.host())

    def linkClicked(self, qUrl):
        url = qUrl.toString()
        if self.window.SIGNIN_URL == url or url.endswith(".slack.com/messages?") or url.endswith(".slack.com/"):
            self.load(qUrl)
        elif url.startswith("https://accounts.google.com/o/oauth"):
            self.load(qUrl)
        else:
            subprocess.call(('xdg-open', url))

    def preferences(self):
        self.window.show()
        self.call("preferences")

    def addTeam(self):
        self.call("addTeam")

    def logout(self):
        self.call("logout")

    def help(self):
        self.call("help")

    def helpCenter(self):
        subprocess.call(('xdg-open', "https://slack.zendesk.com/hc/en-us"))

    def about(self):
        subprocess.call(('xdg-open', "https://github.com/raelgc/scudcloud"))

    def isConnected(self):
        return self.call("isConnected")

    def listChannels(self):
        return self.call("listChannels")

    def openChannel(self, menuitem, timestamp):
        self.call("join", menuitem.property_get("id"))
        self.window.show()

    @QtCore.pyqtSlot(bool) 
    def enableMenus(self, enabled):
        self.window.enableMenus(enabled)

    @QtCore.pyqtSlot(bool) 
    def pasted(self, checked):
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasImage():
            pixmap = clipboard.pixmap()
            byteArray = QByteArray()
            buffer = QBuffer(byteArray)
            pixmap.save(buffer, "PNG")
            self.call("setClipboard", str(byteArray.toBase64(), sys.stdout.encoding))

    @QtCore.pyqtSlot(str, str) 
    def sendMessage(self, title, message):
        self.window.notify(str(title).replace("New message from ", "").replace("New message in ", ""), str(message))

    @QtCore.pyqtSlot(int) 
    def count(self, value):
        self.messages = value;
        self.window.count()

