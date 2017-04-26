from scudcloud.browser import Browser
from scudcloud.downloader import Downloader
from scudcloud.resources import Resources

import sys, subprocess, os, json
from urllib.parse import parse_qs, urlparse, urlsplit

from PyQt5 import QtWebKit, QtGui, QtCore, QtWidgets
from PyQt5.Qt import QApplication, QKeySequence, QTimer
from PyQt5.QtCore import QBuffer, QByteArray, QUrl
from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtNetwork import QNetworkProxy

class Wrapper(QWebView):

    highlights = 0
    unreads = 0
    id = 0
    icon = None
    name = ''

    def __init__(self, window):
        self.configure_proxy()
        QWebView.__init__(self)
        self.window = window
        with open(Resources.get_path('scudcloud.js'), 'r') as f:
            self.default_js = f.read()
        if self.window.disable_snippets:
            with open(Resources.get_path('disable_snippets.js'), 'r') as f:
                self.disable_snippets_js = f.read()
        self.setPage(Browser())
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.urlChanged.connect(self._urlChanged)
        self.loadStarted.connect(self._loadStarted)
        self.loadFinished.connect(self._loadFinished)
        self.linkClicked.connect(self._linkClicked)
        self.page().featurePermissionRequested.connect(self.permissionRequested)
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
        self.pageAction(QWebPage.Undo).setShortcuts(QKeySequence.Undo)
        self.pageAction(QWebPage.Redo).setShortcuts(QKeySequence.Redo)
        self.pageAction(QWebPage.Cut).setShortcuts(QKeySequence.Cut)
        self.pageAction(QWebPage.Copy).setShortcuts(QKeySequence.Copy)
        self.pageAction(QWebPage.Paste).setShortcuts(QKeySequence.Paste)
        self.pageAction(QWebPage.Back).setShortcuts(QKeySequence.Back)
        self.pageAction(QWebPage.Forward).setShortcuts(QKeySequence.Forward)
        self.pageAction(QWebPage.Reload).setShortcuts(QKeySequence.Refresh)

    def contextMenuEvent(self, event):
        entriesToHide = ['Direction', 'Open in New Window', 'Save Link...']
        menu = QtWidgets.QMenu(self)
        hit = self.page().currentFrame().hitTestContent(event.pos())
        if self.window.speller.initialized:
            element = hit.element()
            if hit.isContentEditable() and not hit.isContentSelected() and element.attribute("type") != "password":
                self.window.speller.populateContextMenu(menu, element)
        pageMenu = self.page().createStandardContextMenu()
        url = hit.linkUrl()
        if pageMenu is not None:
            for a in pageMenu.actions():
                if 'Copy' == a.text():
                    menu.addAction(a)
                    # Adding Copy Quoted
                    action = QtWidgets.QAction('Copy Quoted', self)
                    action.triggered.connect(lambda: self.copyQuoted(str(self.selectedText())))
                    menu.addAction(action)
                elif 'Open Link' == a.text() and not url.isEmpty():
                    action = QtWidgets.QAction('Open Link', self)
                    action.triggered.connect(lambda: self.systemOpen(
                        self._urlToString(url)))
                    menu.addAction(action)
                elif a.text() in entriesToHide:
                    continue
                # Let's skip Slack redirect engine only when copying the link (Fixes #42)
                elif 'Copy Link' == a.text() and not url.isEmpty():
                    action = QtWidgets.QAction('Copy Link', self)
                    action.triggered.connect(lambda: self.decodeAndCopy(
                        self._urlToString(url)))
                    menu.addAction(action)
                elif a.isSeparator():
                    menu.addSeparator()
                elif a.isVisible():
                    menu.addAction(a)
        del pageMenu
        menu.exec_(event.globalPos())

    def copyQuoted(self, str):
        mark = '> '
        quote = mark + str.replace('\n', '\n' + mark)
        QApplication.clipboard().setText(quote)

    def decodeAndCopy(self, url):
        if url.startswith("https://slack-redir.net/link?url="):
            url_param = parse_qs(urlsplit(url).query).get('url')
            decodedURL = url_param[0] if url_param else url
        else:
            decodedURL = url
        QApplication.clipboard().setText(decodedURL)

    def call(self, function, arg=None):
        if isinstance(arg, str):
            arg = "'"+arg+"'"
        if arg is None:
            arg = ""
        return self.page().currentFrame().evaluateJavaScript("ScudCloud."+function+"("+arg+");")

    def _loadStarted(self):
        # Some custom CSS to clean/fix UX
        resources = os.path.join(self.window.cache_path, 'resources.css')
        self.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(resources))
        # Fixing lack of MutationObserver in Qt 5.2.1 (#551)
        self.page().currentFrame().evaluateJavaScript("var MutationObserver = MutationObserver || WebKitMutationObserver;null")

    def mousePressEvent(self, event):
        if self.window.debug: print("Mouse Button {}".format(event.button()))
        if 8 == event.button():
            self.back()
        elif 16 == event.button():
            self.forward()
        super(Wrapper, self).mousePressEvent(event)

    def _urlChanged(self, qUrl):
        url = self._urlToString(qUrl)
        if self.window.debug: print("URL Changed: {}".format(url))
        # Some integrations/auth will get back to /services with no way to get back to chat
        if Resources.SERVICES_URL_RE.match(url):
            self.systemOpen(url)
            self.load(QUrl("https://"+qUrl.host()+"/messages/general"))

    @staticmethod
    def _urlToString(url):
        """Convert QUrl to str preserving encoding of special characters."""
        return bytes(url.toEncoded()).decode('latin1')

    def _loadFinished(self, ok=True):
        # Starting the webkit-JS bridge
        self.page().currentFrame().addToJavaScriptWindowObject("desktop", self)
        # Loading ScudCloud JS client
        self.page().currentFrame().evaluateJavaScript(self.default_js+";null")
        if self.window.disable_snippets:
            self.page().currentFrame().evaluateJavaScript(self.disable_snippets_js+";null")
        self.window.statusBar().hide()

    def systemOpen(self, url):
        subprocess.call(('xdg-open', url))

    def _linkClicked(self, qUrl):
        url = self._urlToString(qUrl)
        if self.window.debug: print("Link Clicked: {}".format(url))
        if Resources.SIGNIN_URL == url or Resources.MAINPAGE_URL_RE.match(url):
            self.window.switchTo(url)
        elif Resources.MESSAGES_URL_RE.match(url) or Resources.SSO_URL_RE.match(url) or Resources.GOOGLE_OAUTH2_URL_RE.match(url):
            self.load(qUrl)
        else:
            self.systemOpen(url)

    def sendTickle(self):
        self.call("sendTickle")

    def preferences(self):
        self.window.show()
        self.call("preferences")

    def createSnippet(self):
        self.call("createSnippet")

    def team(self):
        return self.call("getCurrentTeam")

    def logout(self):
        self.call("logout")

    def help(self):
        self.call("help")

    def helpCenter(self):
        self.systemOpen("https://slack.zendesk.com/hc/en-us")

    def about(self):
        self.systemOpen("https://github.com/raelgc/scudcloud")

    def listChannels(self):
        return self.call("listChannels")

    def openChannel(self, menuitem, timestamp):
        self.call("join", menuitem.property_get("id"))
        self.window.show()

    @QtCore.pyqtSlot()
    def addTeam(self):
        self.window.addTeam()

    @QtCore.pyqtSlot(int, int)
    def count(self, highlight, unread):
        self.highlights = highlight
        self.unreads = unread
        team = self.team()
        if highlight == 0:
            self.window.leftPane.stopAlert(team)
        else:
            self.window.leftPane.alert(team, highlight)
        if unread == 0:
            self.window.leftPane.stopUnread(self.id)
        else:
            self.window.leftPane.unread(self.id)
        self.window.count()

    @QtCore.pyqtSlot(str)
    def populate(self, serialized):
        data = json.loads(serialized)
        self.window.teams(data['teams'])
        if self.window.current() == self:
            self.window.quicklist(data['channels'])
        self.id = data['teams'][0]['id']
        self.name = data['teams'][0]['team_name']
        # Using team id to avoid invalid icon paths (Fixes #315)
        icon_name = 'scudcloud_' + data['teams'][0]['id'] + '.jpg'
        icon_path = os.path.join(self.window.cache_path, icon_name)
        # Download the file to use in notifications
        self.downloader = Downloader(self, data['icon'], icon_path)
        self.downloader.start()

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

    @QtCore.pyqtSlot(str)
    def createPost(self, teamUrl):
        self.systemOpen("{}files/create/space".format(teamUrl))

    @QtCore.pyqtSlot(str)
    def open(self, url):
        self.systemOpen(url)

    @QtCore.pyqtSlot(str, str)
    def sendMessage(self, title, message):
        erase = ['['+self.name.lower()+'] in ', '['+self.name.lower()+'] from ']
        for s in erase:
            title = str(title).replace(s, '', 1)
        self.window.notify(title, str(message), self.icon)
