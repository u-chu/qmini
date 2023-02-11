#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os
import platform
# from genericpath import isdir
import sys
# from pprint import pprint

try:
    from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia
except:
    print('pyqt')
    from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets

import time

import mutagen
from pprint import pprint

# import configparser
#from PyQt5.QtWidgets import 
#import Notify

# from modpybass.pybass import *
# import pytags

# sys.setdefaultencoding('utf-8')

if sys.platform.lower().startswith('win'):
  try:
   from PySide2 import QtWinExtras
  #  import (QWinTaskbarButton, QWinTaskbarProgress,                            QWinThumbnailToolBar,                                    QWinThumbnailToolButton)
  except:
   from PyQt5 import QtWinExtras 
  #  import (QWinTaskbarButton, QWinTaskbarProgress,                                  QWinThumbnailToolBar,                                  QWinThumbnailToolButton)



# configdir = os.path.expanduser('~/')
# configname=os.path.join(configdir, 'qmini.ini')
# print (configname)
# config = configparser.ConfigParser()

# formats=[]
# names=[]

# plugins=[]
"""Notify.init('qmbp')
noti=Notify.Notification()"""

# qm=""
# qs=''
pls=os.path.expanduser('~/qmini.m3u')
sTitle='.: QMini :.' 

class ItemDelegate(QtWidgets.QStyledItemDelegate):
 def setIndex(self, i):
  self.index=i
  
 def paint(self, painter, option, index):
#   print(index.row(), self.index)
  if index.row()==self.index:
   option.font.setWeight(QtGui.QFont.Bold)
   option.font.setStyle(QtGui.QFont.StyleNormal)
  else:
   option.font.setWeight(QtGui.QFont.Normal)
   option.font.setStyle(QtGui.QFont.StyleNormal)
  QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

# class QElidedLabel(QtWidgets.QLabel):
#  def paintEvent(self, event):
#   painter = QtGui.QPainter(self)
#   textDoc = QtGui.QTextDocument()
#   metrics = QtGui.QFontMetrics(self.font())
#   elided = metrics.elidedText(self.text(), QtCore.Qt.ElideRight, self.width() - 10)
#   textDoc.setPlainText(elided)
#   textDoc.drawContents(painter)
#   return super(QElidedLabel, self).paintEvent(event)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
  def __init__(self, parent):
    super(SystemTrayIcon, self).__init__(parent)
    self.parent=parent
  def event(self, evt):
    """
    +    if (e->type() == QEvent::Wheel) {
+        QWheelEvent * w = (QWheelEvent *)e;
+
+        if (w->orientation() == Qt::Vertical) {
+            wheel_delta += w->delta();
+
+            if (abs( wheel_delta ) >= 120) {
+                emit wheel( wheel_delta > 0 ? MyTrayIcon::WheelUp : MyTrayIcon::WheelDown );
+                wheel_delta = 0;
+            }
+        }
    """
    if evt.type() == QtCore.QEvent.Wheel:
      w = QtGui.QWheelEvent()
      print(w.delta())
    print(12)
    return super(SystemTrayIcon, self).event(evt)
  def wheelEvent(self, evt):
    print(11)
    return super(SystemTrayIcon, self).wheelEvent(evt)

class ListViewW(QtWidgets.QMainWindow):
  def __init__(self, parent, x=50, y=200, w=500, h=400):
    super(ListViewW, self).__init__(parent)
    self.parent=parent

    hbox=QtWidgets.QVBoxLayout()
    vbox=QtWidgets.QHBoxLayout()
    # self.model=QStringListModel([])
    self.model=QtGui.QStandardItemModel(1,4)

    wdg = QtWidgets.QWidget()
    # self.pList=QListWidget(wdg)
    # self.plist=QTableView(wdg)
    self.plist=QtWidgets.QTreeView(wdg)

    self.model.setHeaderData(0, QtCore.Qt.Horizontal, "")
    self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Title")
    self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Album")
    self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Artist")
    self.plist.setModel(self.model)

    self.plist.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection)
    self.plist.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
    self.plist.setWordWrap(True)
    hbox.addWidget(self.plist)
    self.plist.header().setDefaultSectionSize(200)
    # self.plist.header().resizeSection(1, 250)
    self.plist.header().setStretchLastSection(True)
    self.plist.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    self.plist.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.plist.setFrameShape(QtWidgets.QFrame.NoFrame)
    self.plist.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    
    """ui->playlistView->verticalHeader()->setVisible(false);                  
    ui->playlistView->setSelectionBehavior(QAbstractItemView::SelectRows);  
    ui->playlistView->setSelectionMode(QAbstractItemView::SingleSelection); 
    ui->playlistView->setEditTriggers(QAbstractItemView::NoEditTriggers);  """

    wdg.setLayout(hbox);
    self.setCentralWidget(wdg)
    self.setGeometry(x, y, w, h)
    self.cbCloseOnDblClick=QtWidgets.QCheckBox("Close on take song from playlist", self)
    self.cbCloseOnDblClick.setCheckState(QtCore.Qt.Checked)
    hbox.addWidget(self.cbCloseOnDblClick)
    hbox.addLayout(vbox)
    cbConsume=QtWidgets.QCheckBox("Consume", wdg)
    cbRandom=QtWidgets.QCheckBox("Random", wdg)
    cbRepeat=QtWidgets.QCheckBox("Repeat", wdg)
    cbConsume.setChecked(self.parent.consume)
    cbRandom.setChecked(self.parent.random)
    cbRepeat.setChecked(self.parent.repeat)
    # f=lambda x: (self.parent.consume = not self.parent.consume)
    # QObject.connect(cbConsume, SIGNAL('triggered(bool)'), f, True)
    # QObject.connect(cbConsume, SIGNAL('stateChamged(int)'), self.cb_changed)
    cbConsume.stateChanged.connect(self.cb_changed)
    # cbConsume.toggled.connect(lambda x: not x, self.parent.consume)
    # cbConsume.toggled.connect(lambda x: not x, self.parent.consume)
    # cbRandom.stateChanged.connect(lambda x: not x, self.parent.random)
    # cbRepeat.stateChanged.connect(lambda x: not x, self.parent.repeat)
    vbox.addWidget(cbConsume)
    vbox.addWidget(cbRandom)
    vbox.addWidget(cbRepeat)
    self.setWindowFlags(QtCore.Qt.Tool)
    
    self.destroyed.connect(self.close)
    self.sb=QtWidgets.QStatusBar(self)
    self.setStatusBar(self.sb)
    # kb_del=QShortcut(self.plist )
    # kb_del.setKey(QtGui.QKeySequence("Del"))
      # QtCore.Qt.Key_Delete)
    # kb_del.activated.connect(self.delete_pos)
    qset=QtCore.QSettings('qmini')
    qset.beginGroup('lv')
    self.restoreGeometry(qset.value("geometry"))
    qset.endGroup()

  def keyPressEvent(self, e):
    # print(e)
    key = e.key()
    if key==QtCore.Qt.Key_Delete:
      self.delete_pos()
    super(ListViewW, self).keyPressEvent(e)

  def cb_changed(self, state):
    print('state=', state)

  def closeEvent(self, event):
    # qs=QSettings('qmini.ini', 'lv')
    qset=QtCore.QSettings('qmini')
    qset.beginGroup('lv')
    qset.setValue("geometry", self.saveGeometry())
    qset.endGroup()
    qset.sync()
  
  def delete_pos(self, e=0):
   for i in self.plist.selectedItems():
     a=i.data(QtCore.Qt.UserRole)
     self.parent.songs[a]=''
    # print()
  #  print(self, e)
   self.parent.read_song_list()
#    print(len(self.parent.songs))


class QMini(QtWidgets.QMainWindow):
 def __init__(self, *args, **kwargs):
  super(QMini, self).__init__(*args, **kwargs)
  self._player = QtMultimedia.QMediaPlayer()
  #~ print(self._player.playlist())
  if sys.platform.startswith('win'):
    self.wtb=QtWinExtras.QWinTaskbarButton(self)
    self.tTB=QtWinExtras.QWinThumbnailToolBar(self)
    self.initWinUI()
  self.initUI()
  pl=QtMultimedia.QMediaPlaylist()
  #~ pl.currentMediaChanged.connect(self.onCurrentMediaChanged)
  # print(pl)
  self._player.setPlaylist(pl)
  self._player.playlist().currentMediaChanged.connect(self.onCurrentMediaChanged)
  print(self._player.playlist())
  
  self.setWindowTitle(sTitle)
  self.repeat=False
  self.random=False
  self.consume=False
  # self.destroyed.connect(self.on_destroy)
  
  self._player.stateChanged.connect(self.onStateChanged)

  self.LV=ListViewW(self)
  self.bd=ItemDelegate(self)
  self.LV.plist.setItemDelegate(self.bd)
  self.LV.plist.doubleClicked.connect(self.onDblClick)

 def onStateChanged(self, state):
  # print(state)
  # self.qs.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
  if state==QtMultimedia.QMediaPlayer.PlayingState:
   self.a_pause.triggered.connect(self._player.pause) 
   self.a_pause.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
  elif state== QtMultimedia.QMediaPlayer.PausedState:
   self.a_pause.triggered.connect(self._player.play) 
   self.a_pause.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
  elif state==QtMultimedia.QMediaPlayer.StoppedState:
   self.a_pause.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
   self.titl_label.setText('')
   self.aLabel.setText('/00:00')
   self.cLabel.setText('<b>00:00</b>')
   self.hscale.setValue(0)
   self.qs.setToolTip(sTitle)
   self.setWindowTitle(sTitle)
   if platform.system().lower() == 'windows':
    self.wtbprogress.setValue(0)
  else:
   pass
  if self.LV.isVisible():
    self.read_song_list()
  # self.qs.hide()  
  self.qs.setIcon(self.a_pause.icon())
  self.qs.show()
  # self.qs.show()
  # print(self.a_pause.icon(), self.qs.icon())

 def onDurationChanged(self, duration):
  self.hscale.setMaximum(duration)
  self.hscale.sliderReleased.connect(self.onSliderReleased)
  d=duration/1000.0
  if d>=3600:
    self.aLabel.setText( "%s"%time.strftime("/%H:%M:%S", time.gmtime(d)))
  else:
    self.aLabel.setText( "%s"%time.strftime("/%M:%S", time.gmtime(d)))
  if platform.system().lower()=='windows':
    self.wtbprogress.setMaximum(duration)

 def onPositionChanged(self, pos):
  self.hscale.setValue(pos)
  p=pos/1000.0
  if p>=3600:    
    self.cLabel.setText("%s"%time.strftime("<b>%H:%M:%S</b>", time.gmtime(p)))
  else:
    self.cLabel.setText("%s"%time.strftime("<b>%M:%S</b>", time.gmtime(p)))
  if platform.system().lower()=='windows':
    self.wtbprogress.setValue(pos)
  
#  def templateText(self, text):
#   metric=QtGui.QFontMetrics(self.titl_label.font())
#   w=self.titl_label.width()-3
#   res=metric.elidedText(text, QtCore.Qt.ElideRight, self.titl_label.width())
#   return text


#  def onCurrentIndexChanged(self, index):
#   if self.consume:
#     self._player.playlist().removeMedia(index-1)

 def onCurrentMediaChanged(self, m):
  #~ print(m.canonicalUrl().toLocalFile())
  fn=m.canonicalUrl().toLocalFile()
  if fn==None or len(fn)==0:
    self.setWindowTitle(sTitle)
    return
  self.hscale.setValue(0)
  if os.path.isfile(fn):
   tags=self.get_tags(fn)
  else:
   tags=['','','','']
  # if tags != None:
  s="<b>%s</b> - %s - <i>%s</i> (%s) "%(tags[0], tags[2], tags[1], tags[3])
  self.titl_label.setText(s)
  s1=".: QMini :: %s :: %s :."%(tags[2], tags[0])
  # 
  self.setWindowTitle(s1)
  self.qs.showMessage(sTitle, "%s\n%s (%s)\n%s"%(tags[0],tags[1], tags[3], tags[2]))
  self.qs.setToolTip(s1)
  if self.LV.isVisible():
    self.read_song_list()

 #~ def showEvent(self, a0: QtGui.QShowEvent):
 def showEvent(self, a0):
  super(QMini, self).showEvent(a0)
  # print (self.sender())
  # if not self.wtb:
  if sys.platform.lower() == 'windows':
    if not self.wtb.window(): self.wtb.setWindow(self.windowHandle())
    if not self.tTB.window(): self.tTB.setWindow(self.windowHandle())

 def save_playlist(self, b):
  if(self._player.playlist().mediaCount()<=0):
    QtWidgets.QMessageBox.information(self, "Info", "Playlist is empty", QtWidgets.QMessageBox.Ok)
    return
  # self.deleteAbsent()
  with open (pls, b) as m3u:
    if(b=='w'):
      m3u.write('#EXTM3U\n')
     
    for i in range(self._player.playlist().mediaCount()):
      f= self._player.playlist().media(i).canonicalUrl().toLocalFile()
      l=0 
      if not os.path.isfile(f):
        continue
      try:
        a=mutagen.File(f)
        l=int(a.info.length)
        r=self.get_tags(a)
      except:
        r=['','','','']
      # if r!= None:  
      s="#EXTINF:%i, %s - %s\n%s\n"%(l, r[2], r[0], f)
      #~ print(sys.version, sys.version_info, platform.python_version()['major'])
      if(sys.version_info>=(3,0,0)):
       m3u.write(s)
      else:
       m3u.write(s.encode('utf-8', 'errors=ignore'))
    m3u.close()
  QtWidgets.QMessageBox.information(self, "Info", "Playlist saved", QtWidgets.QMessageBox.Ok)
  

 def load_playlist(self, a):
  # print('load playlist')
  if a==0:
    self.clear_playlist()
  self.add_from_m3u(pls)

  
 def keyPressEvent(self, e):
  # print(e)
  key = e.key()
  if (key==QtCore.Qt.Key_H or key==QtCore.Qt.Key_F1):
    # print (key)
    QtWidgets.QMessageBox.information(self, "Help", "F1, h - help\ns - save playlist with rewrite content\na - add to saved playlist\nl - load playlist\nL - load playlist and start playing\ne - enqueue saved playlist to current\no - open file(s) or folders\np - show current playlist\n\n", QtWidgets.QMessageBox.Ok)
    # self.show_help()
  elif key==QtCore.Qt.Key_P:
    self.show_playlist()
  elif key==QtCore.Qt.Key_S:
    self.save_playlist('w')
  elif key==QtCore.Qt.Key_A:
    self.save_playlist('a')
  elif key==QtCore.Qt.Key_L:
    self.load_playlist(0)
  elif key==QtCore.Qt.Key_E:
    self.load_playlist(1)
  elif key==(QtCore.Qt.Key_Control and QtCore.Qt.Key_C):
    self.clear_playlist()
  elif key==QtCore.Qt.Key_O:
    self.open_files()
  elif key==QtCore.Qt.Key_F5:
    if self._player.state()== QtMultimedia.QMediaPlayer.StoppedState or self._player.state()==QtMultimedia.QMediaPlayer.PausedState:
      self._player.play()
    else:
      self._player.pause()
  else:
    super(QMini, self).keyPressEvent(e)
  # print(key, int(QtCore.Qt.Key_H))
  # if e.type==QEvent.keyPress:

#  def eventFilter(self, e):
  # pass

 def open_files(self):
  path=''
  d=QtWidgets.QFileDialog(self)
  d.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
  if d.exec_():
    path = d.selectedFiles()
    for i in path:
      self.add_file_to_list(i)
      if(self.song_ptr<=0):
        self.song_ptr=0
      if self._player.state()== QtMultimedia.QMediaPlayer.StoppedState:
        self.playfile(self.song_ptr)
    # print(i)
  # path = .getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
  # print (path)


 #~ def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
 def closeEvent(self, a0):
  # qs=QSettings('qmini.ini', 'main')
  qset=QtCore.QSettings('qmini')
  qset.beginGroup('main')
  qset.setValue("geometry", self.saveGeometry())
  qset.setValue("vol", self._player.volume())
  qset.endGroup()
  qset.sync()
  self._player.stop()
  if self.LV:
    self.LV.close()
  return super(QMini, self).closeEvent(a0)

 
 def initWinUI(self):
  self.wtbprogress = self.wtb.progress()
  self.wtbprogress.setRange(0, 0)
  self.wtbprogress.setValue(0)
  self.wtbprogress.show()
  # self.toolBtnControl=QWinThumbnailToolButton(self.tTB)
  #self.tTB.show()
  self.pTB1=QtWinExtras.QWinThumbnailToolButton(self.tTB)
  # self.toolBtnControl.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
  self.pTB1.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))
  
  #~ self.pTB1.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
  
  self.pTB1.clicked.connect(self.prev_song)
  self.pTB2=QtWinExtras.QWinThumbnailToolButton(self.tTB)
  self.pTB2.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
  self.pTB2.clicked.connect(self.ppause)
  self.pTB3=QtWinExtras.QWinThumbnailToolButton(self.tTB)
  self.pTB3.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
  self.pTB3.clicked.connect(self.next_song)

  self.tTB.addButton(self.pTB1)
  self.tTB.addButton(self.pTB2)
  self.tTB.addButton(self.pTB3)
  #~ self.tTB.addButton(self.pTB4)
  #~ self.tTB.addButton(self.pTB5)

 def dragEnterEvent(self, e):
  # print (e.mimeData().urls(), '\n')
  if e.mimeData().hasUrls():
   e.accept()
  else:
   e.ignore()

 def read_song_list(self):
  # k=0
  all=0
  for i in range(self.LV.model.rowCount(), -1, -1):
        self.LV.model.removeRow(i)
#   self.LV.model.clear()
  # self.deleteAbsent()
  # l=[]
  # for i in range(self._player.playlist().mediaCount(), -1, -1):
  #   f= self._player.playlist().media(i).canonicalUrl().toLocalFile()
  #   if not os.path.isfile(f):
  #     self._player.playlist().removeMedia(i)
  
  for i in range(self._player.playlist().mediaCount()):
    f= self._player.playlist().media(i).canonicalUrl().toLocalFile()
    if os.path.isfile(f):
     # self._player.playlist().removeMedia()
      
     b=self.get_tags(f)
     # if b!= None:
     a=str(i+1)
     # self._player.playlist().media(i)
     # print(self._player.playlist().currentIndex())
     self.bd.setIndex(int(self._player.playlist().currentIndex()))
     if i==int(self._player.playlist().currentIndex()):
      a=">"
    
    #  a1=QtGui.QStandardItem(a)
     
     a3=QtGui.QStandardItem("%s (%s)"%(b[1], b[3]))
     a4=QtGui.QStandardItem("%s"%b[2])    
     a5=0
     try:
      f=mutagen.File(f)
      a5=int(f.info.length)
     except:
      pass

     all+=a5
    #  a51=QtGui.QStandardItem("%s"%time.strftime("%M:%S", time.gmtime(a5))) 
     a1=QtGui.QStandardItem("%s"%a)
     a2=QtGui.QStandardItem("%s (%s)"%(b[0], time.strftime("%M:%S", time.gmtime(a5))))

    else:
      a1=QtGui.QStandardItem('File is absent')
      a2=QtGui.QStandardItem('')
      a3=QtGui.QStandardItem('')
      a4=QtGui.QStandardItem('')
      # a51=QtGui.QStandardItem('Unknown')
    # self.LV.plist.model().appendRow([a1, a2,a3,a4, a51])
    self.LV.plist.model().appendRow([a1, a2,a3,a4])
  self.LV.plist.setColumnWidth(0,30)
  self.LV.model.setHeaderData(0, QtCore.Qt.Horizontal, "")
  self.LV.model.setHeaderData(1, QtCore.Qt.Horizontal, "Title")
  self.LV.model.setHeaderData(2, QtCore.Qt.Horizontal, "Album")
  self.LV.model.setHeaderData(3, QtCore.Qt.Horizontal, "Artist")  
  self.LV.model.setHeaderData(4, QtCore.Qt.Horizontal, "Duration")
  # print('self.LV.plist.columnWidth(0)=', self.LV.plist.columnWidth(0))
  
  self.LV.sb.showMessage(time.strftime("total running time: %H:%M:%S", time.gmtime(all)))

 def show_playlist(self, e=0):
  #if self.LV==None:
   #self.LV=ListViewW(self)
  self.LV.setWindowTitle('Playlist')
  self.read_song_list()
  self.LV.show()

 def onDblClick(self, index):
  print(index.row())
  self._player.stop()
  # print(index)
  self._player.playlist().setCurrentIndex(index.row())
  # self.songs.setCurrentIndex(index.row())
  self._player.play()
  if self.LV.cbCloseOnDblClick.checkState() == QtCore.Qt.Checked:
   self.LV.hide()
 
 def add_file_to_list(self, fname):
  if os.path.isfile(fname):
   f=os.path.realpath(fname)
   f=mutagen.File(f)
   if f==None:
    return
   self._player.playlist().addMedia(QtCore.QUrl.fromLocalFile(fname))
  if self.LV.isVisible():
    self.read_song_list()

  
 def add_from_m3u(self, fn):
  a=os.path.split(fn)[0]
  # print(a, fn)
  with open(fn) as m3ufile:
   for line in m3ufile:
    line = line.strip()
    linepath = os.path.join(a, line)
    # print(linepath)
    if os.path.isdir(line):
    #  QMessageBox(QMessageBox.Information, "Help", line, QMessageBox.Ok).exec() 
    #  print(line) 
    #  print(line)
     self.add_from_dir(line)
    elif os.path.isdir(linepath):      
     self.add_from_dir(linepath)
    elif os.path.exists(linepath):
     self.add_file_to_list(linepath) 
    #  self.songs.append(linepath) 
    elif os.path.exists(a):
     self.add_file_to_list(a) 
    #  self.songs.append(a)
    

 def add_from_dir(self, i):
  l=[]
  for r, d, f in os.walk(i):
   for fn in f:
    if '.' in fn:
     fname=os.path.join(r, fn)
     if(os.path.isdir(fname)):
      self.add_from_dir(fname)
     else:
      l.append(os.path.realpath(fname))
  l.sort()
  for i in l:
    self.add_file_to_list(i)

 def dragEnterEvent(self, e):
  # print(e.mimeData())
  if e.mimeData().hasFormat('text/uri-list'):
    e.accept()
  else:
    e.ignore()

 def parseCommandString(self, argv):
  for i in argv:
    self.parseFile(i)
  if self._player.State()==QtMultimedia.QMediaPlayer.StoppedState:
    self._player.play()

 def parseFile(self, i):
  # print("i=", i)
  if (os.path.isdir(i)):
   self.add_from_dir(i)
  else:
   e=i[-4:].lower()
  #  print (e)
   if e=='.m3u':
    self.add_from_m3u(i)
   else:
    self.add_file_to_list(i)
  # print(self._player.State()) 
 
 def dropEvent(self, e):
  print(e.mimeData())
  for r in e.mimeData().urls():
   i=r.path(QtCore.QUrl.FullyDecoded)
   self.parseFile(i)
  if self._player.state()==QtMultimedia.QMediaPlayer.StoppedState:
    self._player.play()
  #  self.playfile(self._player.playlist().currentIndex())


 def initUI(self):
  # qs=QSettings('qmini.ini', 'main')
  
  self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
  self.setAcceptDrops(True)
  # Using a title
  a_rev = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward), 'Rewind', self)
  a_forw = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward), 'Forward', self)
  a_stop = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop), 'Stop', self)
  self.a_pause =QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay), 'Play/Pause', self)
  # a_play=QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay), 'Play', self)
  a_back = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward), 'Back', self)
  a_next = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward), 'Next', self)

  # a_stop.triggered.connect(self.pstop)
  a_stop.triggered.connect(self.onStop)
  # self.a_pause.triggered.connect(self.ppause)
  # a_play.triggered.connect(self._player.play)
  self.a_pause.triggered.connect(self._player.play)
  a_rev.triggered.connect(self.skip_back)
  # a_rev.triggered.connect(self._player.rew
  a_forw.triggered.connect(self.skip_fwd)
  # a_back.triggered.connect(self._player.pre)
  a_back.triggered.connect(self.prev_song)
  # a_back.triggered.connect(self._player.previous)
  a_next.triggered.connect(self.next_song)
  # a_next.triggered.connect(self._player.nex

  a_shuffle=QtWidgets.QAction('Shuffle', self)  
  a_repeat=QtWidgets.QAction('Repeat', self)
  a_consume=QtWidgets.QAction('Consume', self)
  a_clear_playlist=QtWidgets.QAction('Clear playlist', self)
  #exitAction.setShortcut('Ctrl+Q')
  #exitAction.triggered.connect(qApp.quit)

  #~ ptToolbar = self.addToolBar("play")
  ptToolbar=QtWidgets.QToolBar("play")
  #ptToolbar.setIconSize(QtCore.QSize(16, 16))
  
  ptToolbar.addAction(a_rev)
  ptToolbar.addAction(a_forw)
  ptToolbar.addSeparator()
  ptToolbar.addAction(a_stop)
  ptToolbar.addAction(self.a_pause)
  # ptToolbar.addAction(a_play)
  ptToolbar.addSeparator()
  ptToolbar.addAction(a_back)
  ptToolbar.addAction(a_next)

  self.hscale=QtWidgets.QSlider(QtCore.Qt.Horizontal)
  self.hscale.setTickInterval(10);
  self.hscale.setSingleStep(1);
  # self.hscale.sliderMoved.connect(self.onSliderMoved)
  # self.hscale.sliderPressed.connect(self.onSliderPressed)
  self.hscale.sliderReleased.connect(self.onSliderReleased)
  self._player.positionChanged.connect(self.onPositionChanged)
  self._player.durationChanged.connect(self.onDurationChanged)
  # self._player.currentIndexChanged.connect(self.onCurrentIndexChanged)

  self.cLabel=QtWidgets.QLabel('<b>00:00</b>')
  self.cLabel.setTextFormat(QtCore.Qt.RichText)
  self.aLabel=QtWidgets.QLabel('/00:00')
  self.aLabel.setTextFormat(QtCore.Qt.RichText)
  ptToolbar.addSeparator()
  ptToolbar.addWidget(self.hscale)
  ptToolbar.addSeparator()
  ptToolbar.addWidget(self.cLabel)
  ptToolbar.addWidget(self.aLabel)
  #ptToolbar.addAction(a_shuffle)
  #ptToolbar.addAction(a_repeat)
  
  """a_openfile=QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton'))), 'Add file(s)', self)
  a_openfile.triggered.connect(self.add_files)
  a_openfolder=QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirOpenIcon'))), 'Add folder(s)', self)
  a_openfolder.triggered.connect(self.add_folders)"""

  a_show_playlist=QtWidgets.QAction('Show playlist', self)
  # a_show_playlist.setShortcut(QtGui.QKeySequence("p"))
    # QtCore.Qt.Key_P);
  a_show_playlist.triggered.connect(self.show_playlist)
  a_clear_playlist.triggered.connect(self.clear_playlist)
  
#   pOpt=ptToolbar.addAction(" ")
  pOpt=QtWidgets.QToolButton(ptToolbar)
  pOpt.setText('Menu')
  ptToolbar.addWidget(pOpt)
#   print (pOpt)
  self.oMenu=QtWidgets.QMenu(self)
  pOpt.setMenu(self.oMenu)
  
  pOpt.setPopupMode(QtWidgets.QToolButton.InstantPopup)


  #oMenu.addAction(a_openfolder)
  #oMenu.addSeparator()
  self.oMenu.addAction(a_consume)
  self.oMenu.addAction(a_shuffle)
  self.oMenu.addAction(a_repeat)
  self.oMenu.addSeparator()
  self.oMenu.addAction(a_show_playlist)
  self.oMenu.addAction(a_clear_playlist)
  self.oMenu.addSeparator()
  # am=oMenu.addMenu('Styles')
  # for s in QtWidgets.QStyleFactory.keys():
    # a=am.addAction(s)
    # a.triggered.connect(self.set_style(s))

  hbox=QtWidgets.QVBoxLayout()
  hbox2=QtWidgets.QHBoxLayout()
  hbox2.addLayout(hbox)
  qd=QtWidgets.QSlider()
  # qd=QtWidgets.QDial()
  qd.setMinimum(0)
  qd.setMaximum(100)
  qset=QtCore.QSettings('qmini')
  # print('qs.fileName=', qs.fileName())
  qset.beginGroup('main')
  self.restoreGeometry(qset.value("geometry"))
  self.setMaximumWidth(600)
  self.setMaximumHeight(50)
  # self.setFixedWidth(self.getWidth())
  self._player.setVolume(int(qset.value('vol', 100)))
  qset.endGroup()
  qd.setValue(self._player.volume())
  
  try:
    qd.setNotchesVisible(True)
  except:
    pass
  try:
    qd.setTickPosition(QtWidgets.QSlider.TicksRight)
  except:
    pass
  
  # qd.resize(4, 4)
  qd.valueChanged.connect(self.onValueChanged)
  # hbox2=QtWidgets.QHBoxLayout()
  # hbox.addChildLayout(hbox2)

  self.titl_label=QtWidgets.QLabel('Drop files here, or press l for load saved playlist')
  self.titl_label.setTextFormat(QtCore.Qt.RichText)
  self.titl_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
  self.titl_label.setAlignment(QtCore.Qt.AlignLeft)
  self.titl_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
  self.titl_label.customContextMenuRequested.connect(self.onContextMenu)
  #hbox.addWidget(a_openfile)
  hbox.addWidget(self.titl_label)
  wdg = QtWidgets.QWidget()
  wdg.setLayout(hbox2);
  self.setCentralWidget(wdg)
  hbox2.addWidget(qd, QtCore.Qt.AlignRight)
  hbox.addWidget(ptToolbar, QtCore.Qt.AlignBottom)
  # self.sb1=QtWidgets.QStatusBar(wdg)
  # hbox.addWidget(self.sb1)
  # self.addToolBar(QtCore.Qt.BottomToolBarArea, ptToolbar)

  self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
  # self.qm1=QtGui.QIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
  # self.qm2=QtGui.QIcon(self.style().standardIcon(QStyle.SP_MediaPause))
  # print(self.qm)
  self.setWindowTitle(sTitle)
  self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
  # self.qs=QtWidgets.QSystemTrayIcon()
  self.qs=SystemTrayIcon(self)
  # self.qs.inputEvent.connect(self.onWheelEvent)
  self.qs.setIcon(self.a_pause.icon())
  self.qs.setToolTip(sTitle)
  self.qs.activated.connect(self.onActivated)
  # self.qs.triggered.connect(self.show)
  menu = QtWidgets.QMenu('tray')
  # print('menu=', menu)
  # Add a Quit option to the menu.
  # QAction()
  
  menu.addAction(a_back)
  menu.addAction(a_next)
  menu.addSeparator()
  menu.addAction(a_stop)
  menu.addAction(self.a_pause)
  menu.addSeparator()
  quit = menu.addAction( "Quit")
  quit.triggered.connect(app.quit)
  # Add the menu to the tray
  self.qs.setContextMenu(menu)
  self.qs.setVisible(True)
  # self.setWindowFlags(self.windowFlags() |QtCore.Qt.Tool| QtCore.Qt.WindowSystemMenuHint |QtCore.Qt.WindowMinMaxButtonsHint)
  # self.destroyed.connect(self.on_destroy)
  self.show()
 

  """
      def onSystemTrayIconClicked(self, reason):
        if reason == QSystemTrayIcon.Unknown:
            past
        elif reason == QSystemTrayIcon.Context:
            menuWorker.systemTrayMenuShowed.emit()
        elif reason == QSystemTrayIcon.DoubleClick:
            past
        elif reason == QSystemTrayIcon.Trigger:
            self.setVisible(not self.isVisible())
        elif reason == QSystemTrayIcon.MiddleClick:
            past
        else:
            past
  """

#  def onSliderMoved(self, pos):
#   self._player.setPosition(pos)

 def onValueChanged(self, value):
  self._player.setVolume(value)

 def wheelEvent(self, event):
  return super(QMini, self).wheelEvent(event)
  # pass

 def onStop(self):
  self.hscale.sliderReleased.disconnect()
  self._player.stop()
  # (self.onSliderReleased)

 def onSliderReleased(self):
  self._player.setPosition(self.hscale.sliderPosition())
  # self.hscale.sliderMoved.connect(self.onSliderMoved)

#  def onSliderPressed(self):
#   self.hscale.sliderMoved.disconnect()
  # (self.onSliderMoved)

 def onActivated(self, reason):
  if reason==QtWidgets.QSystemTrayIcon.MiddleClick:
    s=self._player.state()
    if s==QtMultimedia.QMediaPlayer.StoppedState or s==QtMultimedia.QMediaPlayer.PausedState:
      self._player.play()
    else:
      self._player.pause()
  elif reason==QtWidgets.QSystemTrayIcon.Trigger:
    self.show()
    self.activateWindow()
    # self.raise()
    # self.seta
  elif reason==QtWidgets.QSystemTrayIcon.Unknown:
    print (10)
    pass
  elif reason == QtWidgets.QSystemTrayIcon.DoubleClick:
    pass
  elif reason ==QtWidgets.QSystemTrayIcon.Context:
    self.qs.contextMenu().emit()

 def onContextMenu(self, p):
  self.oMenu.exec_(self.titl_label.mapToGlobal(p))

 def clear_playlist(self, w=0):
  self._player.stop()
  self._player.playlist().clear()
  if self.LV.isVisible():
    self.read_song_list()



 """def add_files(self):
  #maskname=
  mask=""
  for n in formats:
   mask+=str(n)+";"
  mask+=";"
  for n in formats:
   mask+=str(n)+";;"
  files= QFileDialog.getOpenFileNames(self, "Add file(s)", "", mask)
  print(files)
  for i in files:
   if (os.path.isdir(i)):
    self.add_from_dir(i)
   else:
    self.add_file_to_list(i)"""

#  def set_style(self, style):
#   QApplication.setStyle(QtWidgets.QStyleFactory.create(style))

 """def timer_func(self):
  #print ('timer_func')
  if self.song_ptr<0 or self.cur_handle==None:
   return True
  # bcia= BASS_ChannelIsActive(self.cur_handle)
  # pos=BASS_ChannelGetPosition(self.cur_handle, BASS_POS_BYTE)
  # secs=BASS_ChannelBytes2Seconds(self.cur_handle, pos)
  self.hscale.setValue(pos)
  if platform.system().lower()=='windows':
    self.wtbprogress.setValue(pos)
  #print(self.hscale.getTickPosition())
  ct1=time.strftime("<b>%M:%S</b>", time.gmtime(secs))
  #print(ct1, pos)
  self.cLabel.setText(ct1)
  if bcia==BASS_ACTIVE_STOPPED or pos >= self.wlen:
   self.next_song()
  #if self.LV.isVisible():
   # self.read_song_list()
  return True"""

 def prev_song(self, w=None):
  self.hscale.sliderReleased.disconnect()
  self._player.stop()
  self._player.playlist().setCurrentIndex(self._player.playlist().currentIndex()-1)
  self._player.play()
  if self.LV.isVisible():
    self.read_song_list()

 def next_song(self, w=None):
  self.hscale.sliderReleased.disconnect()
  self._player.stop()
  self._player.playlist().setCurrentIndex(self._player.playlist().currentIndex()+1)
  self._player.play()
  if self.LV.isVisible():
    self.read_song_list()


 def skip_fwd(self, w=None):
  self.skip(20)
  pass
 def skip_back(self, w=None):
  self.skip(-20)
  pass

 def skip(self, sec):
  secs=self._player.position()
  secs += sec*1000
  self._player.setPosition(secs)
  # if pos < 0: pos = 0.
  # pos=BASS_ChannelSeconds2Bytes(self.cur_handle, secs)
  # BASS_ChannelSetPosition(self.cur_handle, int(pos), BASS_POS_BYTE)




 def get_tag(self, f, t1):
  res=''
  if f != None:
   if t1 in f.keys():
    res=f.get(t1,'')
    #~ pprint(f[t1])
    if f[t1].encoding==0:
     res=res.text[0].encode('latin-1', 'replace').decode('cp1251', 'replace').encode('utf-8', 'replace')
  #~ pprint(res)
  return res
  

 def get_tags(self, fname):
  f=os.path.realpath(fname)
  l=("","","","")
  f=mutagen.File(f)
  if fname.lower().endswith(('.mp3')):
   l= self.get_tags_mp3(f)
  else:
   l= self.get_tags_common(f)
  return l

 def get_tags_common(self, f):
  alb=self.get_tag(f,  'album')
  art=self.get_tag(f, 'artist')
  tit=self.get_tag(f, 'title')
  yea=self.get_tag(f, 'year')
  if yea=='':
   yea=self.get_tag(f, 'date')
  #print(type(alb))
  return (tit, alb, art, yea)

 def get_tags_mp3(self, f):
  alb=self.get_tag(f, 'TALB')
  art=self.get_tag(f, 'TPE1')
  tit=self.get_tag(f, 'TIT2')
  try:
   yea=f['TDRC']
  except:
   try:
    yea=f['TYER']
   except:
    yea=''
  #  yea=self.get_tag(f, 'TYER')
  return (tit, alb, art, yea)

if __name__ == '__main__':
  app = QtWidgets.QApplication(sys.argv)  
  ex = QMini()
  py_qss=os.path.realpath(sys.argv[0]).replace('.py', '.qss')
  with open(py_qss, "r") as h:
    app.setStyleSheet(h.read())
  ex.parseCommandString(sys.argv[1:])  
  sys.exit(app.exec_())
