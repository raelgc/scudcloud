from PyQt4.Qt import QApplication

class Launcher:
    def __init__(self, parent):
        self.parent = parent
    def set_property(self, name, value):
        if "urgent" == name and True == value:
            QApplication.alert(self.parent)
