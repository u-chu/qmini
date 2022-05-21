#!/usr/bin/python
# -*- coding: utf-8 -*-
# python2.7
#------------------------------------------------
import sys
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication
 
class MainWindow(QMainWindow):
   def __init__(self):
      QMainWindow.__init__(self)
      uic.loadUi('plist.ui', self)
      #self.pushButton1.clicked.connect(self.pushButton1_Click) # Обработка нажатия на кнопку pushButton1
   #def pushButton1_Click (self):
    #  print ("PUSH")
 
app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())