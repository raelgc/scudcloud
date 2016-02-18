from scudcloud.resources import Resources

import os
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QLocale, QFile, QTextBoundaryFinder

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
    startPos = 0

    def __init__(self):
        super(Speller, self).__init__()
        if self.initialized or hunspell.HunSpell is None:
            return
        dictionaryPath = self.getDictionaryPath()
        language = self.parseLanguage(dictionaryPath)
        if not dictionaryPath or language is None:
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
        dicPath = Resources.SPELL_DICT_PATH + QLocale.system().name()
        if self.dictionaryExists(dicPath):
            return dicPath
        return ''

    def replaceWord(self, element, word):
        action = self.sender()
        new = action.data()
        if isinstance(new, bytes):
            new = new.decode('utf8')
        text = str(element.evaluateJavaScript("this.value"))
        cursorPos = int(element.evaluateJavaScript("this.selectionStart"))
        text = text[:self.startPos] + new + text[self.startPos+len(word):]
        text = text.replace('\\', "\\\\")
        text = text.replace('\n', "\\n")
        text = text.replace('\'', "\\'")
        element.evaluateJavaScript("this.value='{}'".format(text))
        element.evaluateJavaScript("this.selectionStart=this.selectionEnd={}".format(cursorPos))

    def getWord(self, element):
        text = str(element.evaluateJavaScript("this.value"))
        pos = int(int(element.evaluateJavaScript("this.selectionStart")) + int(1))
        finder =  QTextBoundaryFinder(QTextBoundaryFinder.Word, text)
        finder.setPosition(pos)
        self.startPos = finder.toPreviousBoundary()
        return text[self.startPos:finder.toNextBoundary()].strip()

    def populateContextMenu(self, menu, element):
        word = self.getWord(element)
        if self.isMisspelled(word):
            suggests = self.suggest(word)
            count = Resources.SPELL_LIMIT
            if len(suggests) < count:
                count = len(suggests)
            boldFont = menu.font()
            boldFont.setBold(True)
            for i in range(0, count):
                if isinstance(suggests[i], bytes):
                    suggests[i] = suggests[i].decode('utf8')
                action = QtGui.QAction(str(suggests[i]), self)
                action.triggered.connect(lambda:self.replaceWord(element, word))
                action.setData(suggests[i])
                action.setFont(boldFont)
                menu.addAction(action)
            if count == 0:
                menu.addAction(menu.tr("No suggestions")).setEnabled(False)
            menu.addSeparator();
