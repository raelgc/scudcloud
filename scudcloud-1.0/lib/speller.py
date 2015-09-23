import os
from PyQt4 import QtGui
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QLocale, QFile, QTextBoundaryFinder

# Checking if python-hunspell is present
try:
     import hunspell
except ImportError:
     class hunspell:
         HunSpell = None

# Simplified version of QupZilla Speller (https://github.com/QupZilla/qupzilla/blob/v1.8/src/lib/plugins/qtwebkit/spellcheck/speller.cpp)
class Speller(QObject):

    hunspell = None
    initialized = False
    element = None
    startPos = 0
    endPos = 0

    def __init__(self):
        super(Speller, self).__init__()
        if self.initialized or hunspell.HunSpell is None:
            return
        dictionaryPath = self.getDictionaryPath()
        language = self.parseLanguage(dictionaryPath)
        if dictionaryPath is None or language is None:
            return
        self.hunspell = hunspell.HunSpell(dictionaryPath + ".dic", dictionaryPath + ".aff")
        self.initialized = True

    def isMisspelled(self, s):
        return not self.hunspell.spell(s)

    def suggest(self, s):
        return self.hunspell.suggest(s)

    def parseLanguage(self, path):
        if '/' in path:
            pos = path.rfind('/')
            return path[-int(pos + 1):]
        return path

    def dictionaryExists(self, path):
        return QFile(path + ".dic").exists() and QFile(path + ".aff").exists();

    def getDictionaryPath(self):
        dicPath = "/usr/share/hunspell/"
        locale = QLocale.system().name()
        if self.dictionaryExists(dicPath + locale):
            return dicPath + locale
        return ''

    def replaceWord(self, word):
        if self.element is None:
            return;
        action = self.sender()
        new = action.data()
        text = str(self.element.evaluateJavaScript("this.value"))
        cursorPos = int(self.element.evaluateJavaScript("this.selectionStart"))
        text = text[:self.startPos] + new + text[self.startPos+len(word):]
        text = text.replace('\\', "\\\\")
        text = text.replace('\n', "\\n")
        text = text.replace('\'', "\\'")
        self.element.evaluateJavaScript("this.value='{}'".format(text))
        self.element.evaluateJavaScript("this.selectionStart=this.selectionEnd={}".format(cursorPos))

    def populateContextMenu(self, menu, hitTest):
        self.element = hitTest.element()
        if self.element is None or self.element.attribute("type") == "password":
            return;
        text = str(self.element.evaluateJavaScript("this.value"))
        pos = int(int(self.element.evaluateJavaScript("this.selectionStart")) + int(1))
        finder =  QTextBoundaryFinder(QTextBoundaryFinder.Word, text)
        finder.setPosition(pos)
        self.startPos = finder.toPreviousBoundary()
        self.endPos = finder.toNextBoundary()
        word = text[self.startPos:self.endPos].strip()
        if not self.isMisspelled(word):
            return
        limit = 6;
        suggests = self.suggest(word)
        count = 0
        if len(suggests) > limit:
            count = limit
        else:
            count = len(suggests)
        boldFont = menu.font()
        boldFont.setBold(True)
        for i in range(0, count):
            action = QtGui.QAction(suggests[i], self)
            action.triggered.connect(lambda:self.replaceWord(word))
            action.setData(suggests[i])
            action.setFont(boldFont)
            menu.addAction(action)
        if count == 0:
            menu.addAction(menu.tr("No suggestions")).setEnabled(False)
        menu.addSeparator();
