"""
    The MIT License

    Copyright 2011 Thomas Dall'Agnese <thomas.dallagnese@gmail.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

"""
__author__ = "Thomas Dall'Agnese"
__email__ = "thomas.dallagnese@gmail.com"
__version__ = "1.0"
__URL__ = "http://www.dallagnese.fr"

from PyQt4.QtGui import QMessageBox, QApplication
from PyQt4.QtCore import QIODevice, QTimer, QCoreApplication
from PyQt4.QtNetwork import QLocalServer, QLocalSocket
import sys

class QSingleApplication(QApplication):
    def singleStart(self, mainWindow, pid):
        self.mainWindow = mainWindow
        self.pid = pid
        # Socket
        self.m_socket = QLocalSocket()
        self.m_socket.connected.connect(self.connectToExistingApp)
        self.m_socket.error.connect(self.startApplication)
        self.m_socket.connectToServer(pid, QIODevice.WriteOnly)
    def connectToExistingApp(self):
        if len(sys.argv)>1 and sys.argv[1] is not None:
            self.m_socket.write(sys.argv[1])
            self.m_socket.bytesWritten.connect(self.quit)
        else:
            QMessageBox.warning(None, self.applicationName(), self.tr("The program is already running."))
            # Quit application in 250 ms
            QTimer.singleShot(250, self.quit)
    def show(self):
        self.m_server.newConnection.connect(self.getNewConnection)
        self.mainWindow.show()
    def startApplication(self):
        self.m_server = QLocalServer()
        if self.m_server.listen(self.pid):
            self.show()
        else:
            # Try one more time, now deleting the pid
            QLocalServer.removeServer(self.pid)
            if self.m_server.listen(self.pid):
                self.show()
            else:
                QMessageBox.critical(None, self.tr("Error"), self.tr("Error listening the socket."))
    def getNewConnection(self):
        self.new_socket = self.m_server.nextPendingConnection()
        self.new_socket.readyRead.connect(self.readSocket)
    def readSocket(self):
        f = self.new_socket.readLine()
        self.mainWindow.getArgsFromOtherInstance(str(f))
        self.mainWindow.activateWindow()
        self.mainWindow.show()

