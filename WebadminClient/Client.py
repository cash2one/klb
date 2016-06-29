# -*- coding:utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import PyQt4.QtNetwork
import sys
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

App,ClientUI=None,None
class ClientMain(QWebView):
    def __init__(self,parent=None):
        QWebView.__init__(self,parent)
        self.resize(350, 270)
        self.KLB = KalaibaoJS()
        self.show()
        desktop =QApplication.desktop()
        width = desktop.width()
        height = desktop.height()
        self.move((width - self.width())/2, (height - self.height())/2)
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)
        self.load(QUrl(_fromUtf8('http://127.0.0.1:8000/webadmin/Login/')))
        self.page().mainFrame().addToJavaScriptWindowObject("python" , self.KLB)

        self.settings().setAttribute(QWebSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        self.settings().setAttribute(QWebSettings.LocalStorageEnabled, True)


class KalaibaoJS(QObject):

    __pyqtSignals__ = ("contentChanged(const QString &)")

    #关闭程序
    @pyqtSignature("")
    def close(self):
        sys.exit()

    #测试
    @pyqtSignature("")
    def TestLoadURL(self):
        ClientUI.load(QUrl('https://www.baidu.com/'))

    @pyqtSignature("")
    def ChangWindowSize(self):
        ClientUI.load(QUrl(_fromUtf8('http://127.0.0.1:8000/webadmin/Index/')))
        ClientUI.resize(1200, 800)
        desktop =QApplication.desktop()
        width = desktop.width()
        height = desktop.height()
        ClientUI.move((width - ClientUI.width())/2, (height - ClientUI.height())/2)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    ClientUI = ClientMain()
    sys.exit(App.exec_())



