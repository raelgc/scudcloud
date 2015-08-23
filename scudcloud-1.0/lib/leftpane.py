from PyQt4 import QtWebKit, QtGui, QtCore
from PyQt4.Qt import QApplication, QKeySequence
from PyQt4.QtCore import QBuffer, QByteArray, QUrl, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings
from resources import Resources

class LeftPane(QWebView):

    def __init__(self, window):
        QWebView.__init__(self)
        self.window = window
        with open(Resources.get_path("leftpane.js"), "r") as f:
            self.js = f.read()
        self.setFixedWidth(0)
        self.setVisible(False)
        # We don't want plugins for this simple pane
        self.settings().setAttribute(QWebSettings.PluginsEnabled, False)
        self.setUrl(QUrl.fromLocalFile(Resources.get_path("leftpane.html")))
        self.page().currentFrame().addToJavaScriptWindowObject("leftPane", self)
        self.page().currentFrame().evaluateJavaScript(self.js)

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
        self.page().currentFrame().evaluateJavaScript("LeftPane.addTeam('"+id+"','"+name+"','"+url+"','"+icon+"',"+checked+");")
        
    def click(self, i):
        self.page().currentFrame().evaluateJavaScript("LeftPane.click("+str(i)+");")

    def alert(self, team):
        if team is not None:
            self.page().currentFrame().evaluateJavaScript("LeftPane.alert('"+team+"');")

    def stopAlert(self, team):
        if team is not None:
            self.page().currentFrame().evaluateJavaScript("LeftPane.stopAlert('"+team+"');")
    
    def clickNext(self, direction):
        self.page().currentFrame().evaluateJavaScript("LeftPane.clickNext("+str(direction)+");")

    @QtCore.pyqtSlot(str) 
    def switchTo(self, url):
        self.window.switchTo(url)

    def contextMenuEvent(self, event):
        pass


