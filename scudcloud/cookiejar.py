#!/usr/bin/env python3
from PyQt5 import QtCore, QtNetwork

class PersistentCookieJar(QtNetwork.QNetworkCookieJar):

    def __init__(self, parent):
        super(PersistentCookieJar, self).__init__(parent)
        self.mainWindow = parent
        self.load()
        self.save()

    def save(self):
        listCookies = self.allCookies()
        data = QtCore.QByteArray()
        for cookie in  listCookies:
            if not cookie.isSessionCookie():
                data.append(cookie.toRawForm()+ "\n")
        self.mainWindow.settings.setValue("Cookies",data)

    def load(self):
        data = self.mainWindow.settings.value("Cookies")
        if data is not None:
            self.setAllCookies(QtNetwork.QNetworkCookie.parseCookies(data))
