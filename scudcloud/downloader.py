from urllib import request

from PyQt5.QtCore import QThread

class Downloader(QThread):

    def __init__(self, wrapper, icon, path):
        QThread.__init__(self)
        self.wrapper = wrapper
        self.icon = icon
        self.path = path

    def run(self):
        try:
            file_name, headers = request.urlretrieve(self.icon, self.path)
            self.wrapper.icon = file_name
        except:
            pass