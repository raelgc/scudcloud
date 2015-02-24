INSTALL_DIR = "/opt/scudcloud/"
import sys, subprocess
from PyQt4 import QtWebKit, QtCore
from PyQt4.Qt import QApplication, QKeySequence
from PyQt4.QtCore import QBuffer, QByteArray, QUrl, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebSettings

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
        copyAction = self.pageAction(QtWebKit.QWebPage.Paste)
        copyAction.setShortcuts(QKeySequence.Paste)

    def call(self, function, arg=None):
        if isinstance(arg, str):
            arg = "'"+arg+"'"
        if arg is None:
            arg = ""
        self.page().currentFrame().evaluateJavaScript("ScudCloud."+function+"("+arg+");")

    def urlChanged(self, qUrl):
        self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(INSTALL_DIR+"/resources/login.css"))
        self.page().currentFrame().addToJavaScriptWindowObject("desktop", self)
        self.window.quicklist(self.page().currentFrame().evaluateJavaScript(self.js))
        url = qUrl.toString()
        if self.window.SIGNIN_URL != url:
            self.window.settings.setValue("Domain", 'https://'+qUrl.host())
    
    def linkClicked(self, qUrl):
        url = qUrl.toString()
        if self.window.SIGNIN_URL == url or url.endswith(".slack.com/messages?") or url.endswith(".slack.com/"):
            self.load(qUrl)
        else:
            subprocess.call(('xdg-open', url))

    def openChannel(self, menuitem, timestamp):
        self.call("join", menuitem.property_get("id"))
        self.window.setWindowState(self.window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.window.activateWindow()

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
        self.window.count(value)

