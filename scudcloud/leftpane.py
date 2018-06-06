from scudcloud.resources import Resources

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWebEngineWidgets import QWebEngineView

class LeftPane(QWebEngineView):

    def __init__(self, window):
        QWebEngineView.__init__(self)
        self.window = window
        with open(Resources.get_path("leftpane.js"), "r") as f:
            self.js = f.read()
        # We don't want plugins for this simple pane
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)
        self.reset()

    def reset(self):
        self.setFixedWidth(0)
        self.setVisible(False)
        self.setUrl(QUrl.fromLocalFile(Resources.get_path("leftpane.html")))
        self.page().addToJavaScriptWindowObject("leftPane", self)
        self.page().evaluateJavaScript(self.js)

    def show(self):
        self.setFixedWidth(65)
        self.setVisible(True)

    def hide(self):
        self.setFixedWidth(0)
        self.setVisible(False)

    def addTeam(self, id, name, url, icon, active=False):
        if active is True:
            checked = "true"
        else:
            checked = "false"
        self.page().evaluateJavaScript('LeftPane.addTeam("{}","{}","{}","{}","{}");'.format(id, name, url, icon, checked))

    def click(self, i):
        self.page().evaluateJavaScript('LeftPane.click({});'.format(i))

    def alert(self, teamId, messages):
        if teamId is not None:
            self.page().evaluateJavaScript('LeftPane.alert("{}","{}");'.format(teamId, messages))

    def unread(self, teamId):
        self.page().evaluateJavaScript('LeftPane.unread("{}");'.format(teamId))

    def stopAlert(self, team):
        if team is not None:
            self.page().evaluateJavaScript('LeftPane.stopAlert("{}");'.format(team))

    def stopUnread(self, teamId):
        self.page().evaluateJavaScript('LeftPane.stopUnread("{}");'.format(teamId))

    def clickNext(self, direction):
        self.page().evaluateJavaScript('LeftPane.clickNext("{}");'.format(direction))

    @QtCore.pyqtSlot(str)
    def switchTo(self, url):
        self.window.switchTo(url)

    def contextMenuEvent(self, event):
        if self.window.debug:
            menu = self.page().createStandardContextMenu()
            menu.exec_(event.globalPos())
