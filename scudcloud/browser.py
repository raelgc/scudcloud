from scudcloud.resources import Resources

from PyQt5.QtWebKitWidgets import QWebView, QWebPage

class Browser(QWebPage):
    def __init__(self):
        super(QWebPage, self).__init__()

    def userAgentForUrl(self, url):
        return Resources.USER_AGENT
