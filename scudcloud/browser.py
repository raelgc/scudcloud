from scudcloud.resources import Resources

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

class Browser(QWebEnginePage):
    def __init__(self):
        super(QWebEnginePage, self).__init__()

    def userAgentForUrl(self, url):
        return Resources.USER_AGENT
