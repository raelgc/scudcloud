INSTALL_DIR = "/opt/scudcloud/"
from PyQt4 import QtWebKit, QtGui, QtCore
from PyQt4.Qt import QApplication, QKeySequence
from PyQt4.QtCore import QBuffer, QByteArray, QUrl, SIGNAL
from PyQt4.QtWebKit import QWebView, QWebPage, QWebSettings

class LeftPane(QWebView):

    def __init__(self, window):
        QWebView.__init__(self)
        self.window = window
        with open (INSTALL_DIR+"resources/leftpane.js", "r") as f:
             self.js=f.read()
        self.setFixedWidth(0)
        self.setVisible(False)
        self.setUrl(QUrl.fromLocalFile(INSTALL_DIR+"resources/leftpane.html"))
        self.page().currentFrame().addToJavaScriptWindowObject("leftPane", self)
        self.page().currentFrame().evaluateJavaScript(self.js)

    def show(self):
        self.setFixedWidth(65)
        self.setVisible(True)

    def hide(self):
        self.setFixedWidth(0)
        self.setVisible(False)

    def addTeam(self, id, name, url):
        self.page().currentFrame().evaluateJavaScript("LeftPane.addTeam('"+id+"','"+name+"','"+url+"');")
        
    @QtCore.pyqtSlot(str) 
    def switchTo(self, url):
        self.window.switchTo(url)

    #def contextMenuEvent(self, event):
    #    pass

