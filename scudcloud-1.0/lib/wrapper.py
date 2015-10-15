import sys, subprocess, os, json, tempfile
from urllib import request
from urllib.parse import urlparse
from resources import Resources
from PyQt4 import QtWebKit, QtGui, QtCore
from PyQt4.Qt import QApplication, QKeySequence, QTimer
from PyQt4.QtCore import QBuffer, QByteArray, QUrl, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from PyQt4.QtNetwork import QNetworkProxy

class Wrapper(QWebView):

    icon = None

    def __init__(self, window):
        self.configure_proxy()
        QWebView.__init__(self)
        self.window = window
        with open(Resources.get_path("scudcloud.js"), "r") as f:
            self.js = f.read()
        self.setZoomFactor(self.window.zoom)
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.connect(self, SIGNAL("urlChanged(const QUrl&)"), self.urlChanged)
        self.connect(self, SIGNAL("loadStarted()"), self.loadStarted)
        self.connect(self, SIGNAL("loadFinished(bool)"), self.loadFinished)
        self.connect(self, SIGNAL("linkClicked(const QUrl&)"), self.linkClicked)
        #self.page().connect(self.page(), SIGNAL("featurePermissionRequested (QWebFrame*,QWebPage::Feature)"), self.permissionRequested)
        self.addActions()

    def permissionRequested(self, frame, feature):
        self.page().setFeaturePermission(frame, feature, QWebPage.PermissionGrantedByUser)

    def configure_proxy(self):
        proxy = urlparse(os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY'))
        if proxy.hostname is not None and proxy.port is not None:
            q_network_proxy = QNetworkProxy(QNetworkProxy.HttpProxy, proxy.hostname, proxy.port)
            if proxy.username is not None:
                q_network_proxy.setUser(proxy.username)
            if proxy.password is not None:
                q_network_proxy.setPassword(proxy.password)
            QNetworkProxy.setApplicationProxy(q_network_proxy)

    def addActions(self):
        self.pageAction(QWebPage.SetTextDirectionDefault).setVisible(False)
        self.pageAction(QWebPage.SetTextDirectionLeftToRight).setVisible(False)
        self.pageAction(QWebPage.SetTextDirectionRightToLeft).setVisible(False)
        self.pageAction(QWebPage.Undo).setShortcuts(QKeySequence.Undo)
        self.pageAction(QWebPage.Redo).setShortcuts(QKeySequence.Redo)
        self.pageAction(QWebPage.Cut).setShortcuts(QKeySequence.Cut)
        self.pageAction(QWebPage.Copy).setShortcuts(QKeySequence.Copy)
        self.pageAction(QWebPage.Paste).setShortcuts(QKeySequence.Paste)
        self.pageAction(QWebPage.Back).setShortcuts(QKeySequence.Back)
        self.pageAction(QWebPage.Forward).setShortcuts(QKeySequence.Forward)
        self.pageAction(QWebPage.Reload).setShortcuts(QKeySequence.Refresh)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        if self.window.speller.initialized:
            hit = self.page().currentFrame().hitTestContent(event.pos())
            element = hit.element()
            if hit.isContentEditable() and not hit.isContentSelected() and element.attribute("type") != "password":
                self.window.speller.populateContextMenu(menu, element)
        pageMenu = self.page().createStandardContextMenu()
        if pageMenu is not None:
            for a in pageMenu.actions():
                if a.isSeparator():
                    menu.addSeparator()
                elif a.isVisible():
                    menu.addAction(a)
        del pageMenu
        menu.exec_(event.globalPos())

    def call(self, function, arg=None):
        if isinstance(arg, str):
            arg = "'"+arg+"'"
        if arg is None:
            arg = ""
        return self.page().currentFrame().evaluateJavaScript("ScudCloud."+function+"("+arg+");")

    def loadStarted(self):
        # Some custom CSS to clean/fix UX
        self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(Resources.get_path("resources.css")))

    def urlChanged(self, qUrl):
        url = qUrl.toString()
        # Some integrations/auth will get back to /services with no way to get back to chat
        if Resources.SERVICES_URL_RE.match(url):
            self.systemOpen(url)
            self.load(QUrl("https://"+qUrl.host()+"/messages/general"))

    def loadFinished(self, ok=True):
        self.page().currentFrame().addToJavaScriptWindowObject("desktop", self)
        self.page().currentFrame().evaluateJavaScript(self.js)
        self.window.enableMenus(self.isConnected())
        self.window.statusBar().hide()

    def systemOpen(self, url):
        subprocess.call(('xdg-open', url))

    def linkClicked(self, qUrl):
        url = qUrl.toString()
        handle_link = (
            Resources.SIGNIN_URL == url or
            Resources.MAINPAGE_URL_RE.match(url) or
            Resources.MESSAGES_URL_RE.match(url) or
            Resources.SSO_URL_RE.match(url) or
            url.startswith("https://accounts.google.com/o/oauth"))
        if handle_link:
            self.load(qUrl)
        else:
            self.systemOpen(url)

    def preferences(self):
        self.window.show()
        self.call("preferences")

    def isConnected(self):
        return self.call("isConnected")

    def createSnippet(self):
        self.call("createSnippet")

    def team(self):
        return self.call("getCurrentTeam")

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

    def count(self):
        try:
            return self.call("count")
        except:
            return 0

    @QtCore.pyqtSlot(str) 
    def populate(self, serialized):
        data = json.loads(serialized)
        self.window.teams(data['teams'])
        if self.window.current() == self:
            self.window.quicklist(data['channels'])
        iconFile = data['teams'][0]['team_name']+'.png'
        filename, headers = request.urlretrieve(data['icon'], tempfile.gettempdir()+'/'+iconFile)
        self.icon = filename

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
        self.window.notify(str(title).replace("New message from ", "").replace("New message in ", ""), str(message), self.icon)


