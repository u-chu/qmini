#!/usr/bin/env python3
#-*- coding: UTF-8 -*-

# from genericpath import isdir
import sys, os
try:
    # import PySide3
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QApplication,  QVBoxLayout, QLabel, QMainWindow, \
        QToolBar, QAction,  QStyle, QSlider, QToolButton, QMenu, QStatusBar, QStyleFactory, \
        QListWidget, QCheckBox, QWidget, QMessageBox, QWidget, QListWidgetItem, \
        QAbstractItemView, QHBoxLayout
    from PySide2.QtCore import QStringListModel, QObject, SIGNAL, QPoint, QSettings, QEvent
except:
    # import PyQt5
    print('pyqt')
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication,  QVBoxLayout, QLabel, QMainWindow, \
        QToolBar, QAction,  QStyle, QSlider, QToolButton, QMenu, QStatusBar, QStyleFactory, \
        QListWidget, QCheckBox, QWidget, QMessageBox, QWidget, QListWidgetItem, \
        QAbstractItemView, QHBoxLayout
    from PyQt5.QtCore import QStringListModel, QObject, QPoint, QSettings, QEvent
    # , SIGNAL
from modpybass import pybass
import glob
import time
# import configparser
#from PyQt5.QtWidgets import 
#import Notify

import mutagen
from modpybass.pybass import *

if sys.platform.startswith('win'):
  try:
   from PySide2.QtWinExtras import QWinTaskbarProgress, \
		  QWinTaskbarButton, QWinThumbnailToolBar, QWinThumbnailToolButton
  except:
   from PyQt5.QtWinExtras import QWinTaskbarProgress, \
		  QWinTaskbarButton, QWinThumbnailToolBar, QWinThumbnailToolButton



# configdir = os.path.expanduser('~/')
# configname=os.path.join(configdir, 'qmini.ini')
# print (configname)
# config = configparser.ConfigParser()

formats=[]
names=[]

plugins=[]
"""Notify.init('qmbp')
noti=Notify.Notification()"""

class ListViewW(QMainWindow):
  def __init__(self, parent, x=50, y=200, w=500, h=400):
    super(ListViewW, self).__init__(parent)
    self.parent=parent

    hbox=QVBoxLayout()
    vbox=QHBoxLayout()
    self.pListModel=QStringListModel([])
    # self.pList.setModel(self.pListModel)
    wdg = QWidget()
    self.pList=QListWidget(wdg)
    self.pList.setSelectionMode( QAbstractItemView.ExtendedSelection)
    self.pList.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
    hbox.addWidget(self.pList)

    wdg.setLayout(hbox);
    self.setCentralWidget(wdg)
    self.setGeometry(x, y, w, h)
    self.cbCloseOnDblClick=QCheckBox("Close on take song from playlist", self)
    self.cbCloseOnDblClick.setCheckState(QtCore.Qt.Checked)
    hbox.addWidget(self.cbCloseOnDblClick)
    hbox.addLayout(vbox)
    cbConsume=QCheckBox("Consume", wdg)
    cbRandom=QCheckBox("Random", wdg)
    cbRepeat=QCheckBox("Repeat", wdg)
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
    self.sb=QStatusBar(self)
    self.setStatusBar(self.sb)
    # kb_del=QShortcut(self.pList )
    # kb_del.setKey(QtGui.QKeySequence("Del"))
      # QtCore.Qt.Key_Delete)
    # kb_del.activated.connect(self.delete_pos)
    qs=QSettings('qmini.ini', 'lv')
    self.restoreGeometry(qs.value("geometry"))

  def keyPressEvent(self, e):
    # print(e)
    key = e.key()
    if key==QtCore.Qt.Key_Delete:
      self.delete_pos()
    super(ListViewW, self).keyPressEvent(e)

  def cb_changed(self, state):
    print(state)

  def closeEvent(self, event):
    qs=QSettings('qmini.ini', 'lv')
    qs.setValue("geometry", self.saveGeometry())
    qs.sync()
  
  def delete_pos(self, e=0):
   for i in self.pList.selectedItems():
     a=i.data(QtCore.Qt.UserRole)
     self.parent.songs[a]=''
    # print()
  #  print(self, e)
   self.parent.read_song_list()
#    print(len(self.parent.songs))


class QMini(QMainWindow):
 def __init__(self, *args, **kwargs):
  super(QMini, self).__init__(*args, **kwargs)
  self.songs=[]
  # print(len(self.songs))
  self.song_ptr=0
  self.cur_handle=None
  self.timer=QtCore.QTimer()
  self.timer.timeout.connect(self.timer_func)
  self.setWindowTitle('QMini')
  self.repeat=False
  self.random=False
  self.consume=False
  # self.destroyed.connect(self.on_destroy)
  if sys.platform.startswith('win'):
    self.wtb=QWinTaskbarButton(self)
    self.tTB=QWinThumbnailToolBar(self)
    self.initWinUI()
  self.initUI()

  # a_help=QShortcut(QtGui.QKeySequence("F1"), self)
  # a_help.activated.connect(self.show_help)
  # a_help1=QShortcut(QtGui.QKeySequence("h"), self)
  # a_help1.activated.connect(self.show_help)

  self.LV=self.LV=ListViewW(self)
  

  
    
#  @staticmethod   
 """def show_help(self=0, e=0):
  QMessageBox(QMessageBox.Information, "Help", "F1, h - help\ns - save playlist with rewrite content\na-add to saved playlist\nl - load playlist\ne - enqueue saved playlist to current\np - show current playlist\n\n", QMessageBox.Ok).exec()"""

 def showEvent(self, a0: QtGui.QShowEvent):
  super(QMini, self).showEvent(a0)
  print (self.sender())
  # if not self.wtb:
  if platform.system().lower() == 'windows':
    if not self.wtb.window(): self.wtb.setWindow(self.windowHandle())
    if not self.tTB.window(): self.tTB.setWindow(self.windowHandle())

 def save_playlist(self, b):
  if(len(self.songs)<=0):
    QMessageBox.information(self, "Info", "Playlist is empty", QMessageBox.Ok).exec()
  # print('save_playlist')
  with open ('playlist.m3u', b) as m3u:
    if(b=='w'):
      m3u.write('#EXTM3U\n')
    for i in self.songs:
      h=BASS_StreamCreateFile(False, i, 0,0,BASS_MUSIC_PRESCAN|BASS_UNICODE)
      l=BASS_ChannelGetLength(h, BASS_POS_BYTE)
      l=int(BASS_ChannelBytes2Seconds(h, l))
      BASS_StreamFree(h)
      r=self.get_tags(i)
      # st = "{0} :: {1} ({2}) :: {3} [{4}]".format(b[2], b[1], b[3], b[0], l)
      m3u.write('#{0}, {1} - {2}\n'.format(l, r[2], r[0]))
      m3u.write(i+'\n')
    m3u.close()
  QMessageBox.information(self, "Info", "Playlist saved", QMessageBox.Ok)

 def load_playlist(self, a):
  print('load playlist')
  if a==0:
    self.clear_playlist()
  self.add_from_m3u('playlist.m3u')
  # elif a==1:
    # self.add_from_m3u('playlist.m3u')
  
 def keyPressEvent(self, e):
  # print(e)
  key = e.key()
  if (key==QtCore.Qt.Key_H or key==QtCore.Qt.Key_F1):
    # print (key)
    QMessageBox.information(self, "Help", "F1, h - help\ns - save playlist with rewrite content\na-add to saved playlist\nl - load playlist\ne - enqueue saved playlist to current\np - show current playlist\n\n", QMessageBox.Ok).exec()
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
  else:
    super(QMini, self).keyPressEvent(e)
  # print(key, int(QtCore.Qt.Key_H))
  # if e.type==QEvent.keyPress:

#  def eventFilter(self, e):
  # pass

 def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
  qs=QSettings('qmini.ini', 'main')
  qs.setValue("geometry", self.saveGeometry())
  qs.sync()
  if self.LV:
    self.LV.close()
  if not BASS_PluginFree(0):
   print ("plugins free error: ", BASS_ErrorGetCode())
  BASS_PluginFree(0)
  BASS_Free()
  return super(QMini, self).closeEvent(a0)

 
 def initWinUI(self):
  self.wtbprogress = self.wtb.progress()
  self.wtbprogress.setRange(0, 0)
  self.wtbprogress.setValue(0)
  self.wtbprogress.show()
  # self.toolBtnControl=QWinThumbnailToolButton(self.tTB)
  #self.tTB.show()
  self.pTB1=QWinThumbnailToolButton(self.tTB)
  # self.toolBtnControl.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
  self.pTB1.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
  
  #~ self.pTB1.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
  
  self.pTB1.clicked.connect(self.prev_song)
  self.pTB2=QWinThumbnailToolButton(self.tTB)
  self.pTB2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
  self.pTB2.clicked.connect(self.ppause)
  self.pTB3=QWinThumbnailToolButton(self.tTB)
  self.pTB3.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
  self.pTB3.clicked.connect(self.next_song)

  self.tTB.addButton(self.pTB1)
  self.tTB.addButton(self.pTB2)
  self.tTB.addButton(self.pTB3)
  #~ self.tTB.addButton(self.pTB4)
  #~ self.tTB.addButton(self.pTB5)

 def dragEnterEvent(self, e):
  print (e.mimeData().urls(), '\n')
  if e.mimeData().hasUrls():
   e.accept()
  else:
   e.ignore()

 def read_song_list(self):
  k=0
  all=0
  self.LV.pList.clear()
  for i in self.songs:   
   if not os.path.isfile(i):
     k+=1
     continue
   b=self.get_tags(i)
   a= QListWidgetItem()
   h=BASS_StreamCreateFile(False, i, 0,0,BASS_MUSIC_PRESCAN|BASS_UNICODE)
   l=BASS_ChannelGetLength(h, BASS_POS_BYTE)
   l=BASS_ChannelBytes2Seconds(h, l)
   BASS_StreamFree(h)
   all+=l
   l=time.strftime("%M:%S", time.gmtime(l))
   st = "{0} :: {1} ({2}) :: {3} [{4}]".format(b[2], b[1], b[3], b[0], l)
  #  print(k, self.song_ptr)
   if k==self.song_ptr:
    st='>'+st
   else:
     st=" "+st
   a.setData(QtCore.Qt.DisplayRole, st)
   a.setData(QtCore.Qt.UserRole, k)
   self.LV.pList.addItem(a)
   self.LV.pList.itemDoubleClicked.connect(self.lv1dblClick)
   k+=1
  all="Total: %s"%time.strftime("%H:%M:%S", time.gmtime(all))
  self.LV.sb.showMessage(all)
  # return all

 def show_playlist(self, e=0):
  #if self.LV==None:
   #self.LV=ListViewW(self)
  self.LV.setWindowTitle('Playlist')
  self.read_song_list()
  self.LV.show()

 def lv1dblClick(self, item=0):
   if self.cur_handle!= None:
    BASS_ChannelStop(self.cur_handle)
    BASS_StreamFree(self.cur_handle)
    self.cur_handle=None
   self.song_ptr =  item.data(QtCore.Qt.UserRole)
   self.playfile(self.song_ptr)
   if self.LV.cbCloseOnDblClick.checkState() == QtCore.Qt.Checked:
    self.LV.hide()
   
 def add_file_to_list(self, fname):
  # buf=0
  # print(u'%s'%fname)
  # if platform.system().lower()=='windows':
  # fname=bytes(fname.encode('utf-8', 'ignore')).decode('utf-8', 'ignore')
  buf = BASS_StreamCreateFile(False, fname, 0,0, BASS_UNICODE)
  # print(buf)
  # BASS_MUSIC_PRESCAN|BASS_SAMPLE_FLOAT|BASS_UNICODE
  # buf=1
  # else:
    # buf = BASS_StreamCreateFile(False, fname.encode('utf-8', 'ignore'), 0,0,BASS_MUSIC_PRESCAN|BASS_SAMPLE_FLOAT)
  if buf!=0:
   BASS_StreamFree(buf)
   self.songs.append(fname)
  #  print(len(self.songs))
   if self.LV.isVisible():
    self.read_song_list()
   #~ self.pListModel.setStringList(self.songs)
  else:
   print("BASS_ErrorGetCode= ", BASS_ErrorGetCode(), '; file name= ', fname )
  
 def add_from_m3u(self, fn):
  a=os.path.split(fn)[0]
  with open(fn) as m3ufile:
   for line in m3ufile:
    line = line.strip()
    linepath = os.path.join(a, line)
    # print(linepath)
    if os.path.isdir(line):
    #  QMessageBox(QMessageBox.Information, "Help", line, QMessageBox.Ok).exec() 
    #  print(line) 
     self.add_songs_from_dir(line)
    elif os.path.isdir(linepath):      
     self.add_songs_from_dir(linepath)
    elif os.path.exists(linepath):
     self.songs.append(linepath) 
    elif os.path.exists(a):
     self.songs.append(a)
    

 def add_from_dir(self, i):
  for r, d, f in os.walk(i):
   for fn in f:
    if '.' in fn:
     fname=os.path.join(r, fn)
     if(os.path.isdir(fname)):
      self.add_from_dir(fname)
     else:
      self.add_file_to_list(os.path.realpath(fname))
     """buf = BASS_StreamCreateFile(False, fname, 0,0,BASS_MUSIC_PRESCAN|BASS_SAMPLE_FLOAT|BASS_UNICODE)
     print (buf)
     if buf!=0:
      BASS_StreamFree(buf)
      self.songs.append(fname)
     else:
       print(BASS_ErrorGetCode())"""

 def dragEnterEvent(self, e):
  if e.mimeData().hasFormat('text/uri-list'):
    e.accept()
  else:
    e.ignore()
 
 def dropEvent(self, e):
   #~ uri=[]
  # e.setDropAction(QtCore.Qt.MoveAction)
  # e.accept()
  for i in e.mimeData().urls():
    i=u''+i.path()[1::]
    # print(i)
    if (os.path.isdir(i)):
     self.add_from_dir(i)
    else:
     e=i[-4:].lower()
     if e=='.m3u':
      self.add_from_m3u(i)
     else:
      self.add_file_to_list(i)
  if(self.song_ptr<=0):
   self.song_ptr=0
  if self.cur_handle==None:
   self.playfile(self.song_ptr)


 def initUI(self):
  qs=QSettings('qmini.ini', 'main')
  self.restoreGeometry(qs.value("geometry"))
  self.setWindowIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
  self.setAcceptDrops(True)
  # Using a title
  a_rev = QAction(self.style().standardIcon(QStyle.SP_MediaSeekBackward), 'Rewind', self)
  a_forw = QAction(self.style().standardIcon(QStyle.SP_MediaSeekForward), 'Forward', self)
  a_stop = QAction(self.style().standardIcon(QStyle.SP_MediaStop), 'Stop', self)
  self.a_pause = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), 'Play/Pause', self)
  a_back = QAction(self.style().standardIcon(QStyle.SP_MediaSkipBackward), 'Back', self)
  a_next = QAction(self.style().standardIcon(QStyle.SP_MediaSkipForward), 'Next', self)

  a_stop.triggered.connect(self.pstop)
  self.a_pause.triggered.connect(self.ppause)
  a_rev.triggered.connect(self.skip_back)
  a_forw.triggered.connect(self.skip_fwd)
  a_back.triggered.connect(self.prev_song)
  a_next.triggered.connect(self.next_song)

  a_shuffle=QAction('Shuffle', self)  
  a_repeat=QAction('Repeat', self)
  a_consume=QAction('Consume', self)
  a_clear_playlist=QAction('Clear playlist', self)
  #exitAction.setShortcut('Ctrl+Q')
  #exitAction.triggered.connect(qApp.quit)

  #~ ptToolbar = self.addToolBar("play")
  ptToolbar=QToolBar("play")
  #ptToolbar.setIconSize(QtCore.QSize(16, 16))
  self.addToolBar(QtCore.Qt.BottomToolBarArea, ptToolbar)
  ptToolbar.addAction(a_rev)
  ptToolbar.addAction(a_forw)
  ptToolbar.addSeparator()
  ptToolbar.addAction(a_stop)
  ptToolbar.addAction(self.a_pause)
  ptToolbar.addSeparator()
  ptToolbar.addAction(a_back)
  ptToolbar.addAction(a_next)

  self.hscale=QSlider(QtCore.Qt.Horizontal)
  self.hscale.setTickInterval(10);
  self.hscale.setSingleStep(1);

  self.cLabel=QLabel('<b>00:00</b>')
  self.cLabel.setTextFormat(QtCore.Qt.RichText)
  self.aLabel=QLabel('/00:00')
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

  a_show_playlist=QAction('Show playlist', self)
  # a_show_playlist.setShortcut(QtGui.QKeySequence("p"))
    # QtCore.Qt.Key_P);
  a_show_playlist.triggered.connect(self.show_playlist)
  a_clear_playlist.triggered.connect(self.clear_playlist)
  
  pOpt=ptToolbar.addAction(" ")
#   print (pOpt)
  oMenu=QMenu('Options')
  pOpt.setMenu(oMenu)
#   pOpt.setPopupMode(QToolbutton.InstantPopup)
#   pOpt.setArrowType(QtCore.Qt.DownArrow)
  #oMenu.addAction(a_openfile)

  #oMenu.addAction(a_openfolder)
  #oMenu.addSeparator()
  oMenu.addAction(a_consume)
  oMenu.addAction(a_shuffle)
  oMenu.addAction(a_repeat)
  oMenu.addSeparator()
  oMenu.addAction(a_show_playlist)
  oMenu.addAction(a_clear_playlist)
  oMenu.addSeparator()
  am=oMenu.addMenu('Styles')
  for s in QtWidgets.QStyleFactory.keys():
    a=am.addAction(s)

  hbox=QVBoxLayout()

  self.titl_label=QLabel('Drop files here, or press l for load saved playlist')
  self.titl_label.setTextFormat(QtCore.Qt.RichText)
  self.titl_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
  self.titl_label.setAlignment(QtCore.Qt.AlignLeft)
  #hbox.addWidget(a_openfile)
  hbox.addWidget(self.titl_label)

  wdg = QWidget()
  wdg.setLayout(hbox);
  self.setCentralWidget(wdg)

  self.show()
  self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
  # self.setWindowFlags(self.windowFlags() |QtCore.Qt.Tool| QtCore.Qt.WindowSystemMenuHint |QtCore.Qt.WindowMinMaxButtonsHint)
  # self.destroyed.connect(self.on_destroy)


 def toggle_check_menu_item(self, a, x):
  a = not a
  x.setCheckable(a)

 def clear_playlist(self, w=0):
  self.pstop()
  self.songs*=0
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

 def set_style(self, style):
  QApplication.setStyle(QStyleFactory.create(style))

 def timer_func(self):
  #print ('timer_func')
  if self.song_ptr<0 or self.cur_handle==None:
   return True
  bcia= BASS_ChannelIsActive(self.cur_handle)
  pos=BASS_ChannelGetPosition(self.cur_handle, pybass.BASS_POS_BYTE)
  secs=BASS_ChannelBytes2Seconds(self.cur_handle, pos)
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
  return True

 def prev_song(self, w=None):
  if self.song_ptr>0:
   self.song_ptr-=1   
  else:
   self.song_ptr=0
  if self.cur_handle!= None:
    BASS_ChannelStop(self.cur_handle)
    BASS_StreamFree(self.cur_handle)
    self.cur_handle=None
   #self.stop()
  self.playfile(self.song_ptr)
  #  self.pstop()
  if self.LV.isVisible():
    self.read_song_list()

 def next_song(self, w=None):
  if self.song_ptr< len(self.songs)-1:
   self.song_ptr+=1
   #self.stop()
   if self.cur_handle!= None:
    BASS_ChannelStop(self.cur_handle)
    BASS_StreamFree(self.cur_handle)
    self.cur_handle=None
   self.playfile(self.song_ptr)
  elif self.song_ptr< len(self.songs)-1 and self.repeat:
   self.song_ptr=0
   #self.stop()
   if self.cur_handle!= None:
    BASS_ChannelStop(self.cur_handle)
    BASS_StreamFree(self.cur_handle)
    self.cur_handle=None
   self.playfile(self.song_ptr)
  else:
   self.song_ptr=-1
   self.pstop()
  if self.LV.isVisible():
    self.read_song_list()

 def ppause(s,  e=0):
  if len(s.songs)<=0:
   return
  if s.cur_handle==None:
   if s.song_ptr<0:
    s.song_ptr=0
   s.playfile(s.song_ptr)
   return
  bcia= BASS_ChannelIsActive(s.cur_handle)
  if bcia==BASS_ACTIVE_PLAYING:
   BASS_ChannelPause(s.cur_handle)
   s.a_pause.setIcon(s.style().standardIcon(QStyle.SP_MediaPlay))
   if platform.system().lower() == 'windows':
     s.wtbprogress.setPaused(True)
     s.pTB2.setIcon(s.style().standardIcon(QStyle.SP_MediaPlay))
  elif bcia == BASS_ACTIVE_PAUSED or bcia == BASS_ACTIVE_STALLED:
   BASS_ChannelPlay(s.cur_handle, False)   
   s.a_pause.setIcon(s.style().standardIcon(QStyle.SP_MediaPause))
   if platform.system().lower() == 'windows':
     s.wtbprogress.setPaused(False)
     s.pTB2.setIcon(s.style().standardIcon(QStyle.SP_MediaPause))


 def pstop(s,  e=0):
  if s.cur_handle!=None:
   #~ if s.song_ptr >=0: #and self.cur_id>=0:
   bcia= BASS_ChannelIsActive(s.cur_handle)
   print (bcia)
   if bcia==BASS_ACTIVE_PLAYING or bcia==BASS_ACTIVE_PAUSED or bcia==BASS_ACTIVE_STALLED:
    BASS_ChannelStop(s.cur_handle)
    BASS_StreamFree(s.cur_handle)
   s.song_ptr=-1
   s.cur_handle=None
   s.a_pause.setIcon(s.style().standardIcon(QStyle.SP_MediaPlay))
   #~ s.abox.set_text("/00:00")
   #~ s.cbox.set_markup("<b>00:00</b>")
   #~ s.hscale.set_value(0)
   #~ s.lb.set_value(0)
   # ~ s.lb.set_fraction(0)
   #~ s.toolbar.get_nth_item(4).set_stock_id(gtk.STOCK_MEDIA_PLAY)
   #~ s.set_scale_slider(0)
   s.titl_label.setText('')
   s.aLabel.setText('/00:00')
   s.cLabel.setText('<b>00:00</b>')
   s.setWindowTitle('QMini')
   s.timer.stop()
   if platform.system().lower() == 'windows':
     s.wtbprogress.setValue(0)
     s.pTB2.setIcon(s.style().standardIcon(QStyle.SP_MediaPlay))
  if s.LV.isVisible():
    s.read_song_list()
   # ~ s.titl_label.set_tooltip_markup("")

 def skip_fwd(self, w=None):
  self.skip(20)
  pass
 def skip_back(self, w=None):
  self.skip(-20)
  pass

 def skip(self, sec):
  if self.cur_handle == None:
   return
  pos=BASS_ChannelGetPosition(self.cur_handle, pybass.BASS_POS_BYTE)
  secs=BASS_ChannelBytes2Seconds(self.cur_handle, pos)
  secs += sec
  if pos < 0: pos = 0.
  pos=BASS_ChannelSeconds2Bytes(self.cur_handle, secs)
  BASS_ChannelSetPosition(self.cur_handle, int(pos), pybass.BASS_POS_BYTE)




 def playfile(s, f):
  if len(s.songs)<=0:
    print('no files in playlist')
    return
  if f> len(s.songs):
   s.song_ptr=0
   f=0
  fname = s.songs[f]
  print (fname)
  s.cur_handle=BASS_StreamCreateFile(False, fname, 0,0,BASS_MUSIC_PRESCAN|BASS_UNICODE)
  #print ('s.cur_handle=', s.cur_handle)

  if s.cur_handle==None:
   ec=BASS_ErrorGetCode()
   print (get_error_description(ec), ec)
  a=s.get_tags(fname)

  s.titl_label.setText("<b>%s</b> - <i>%s</i> - %s (%s)"%(a[0], a[2], a[1], a[3]))
  s.setWindowTitle("QMini - %s :: %s :: %s (%s)"%(a[0], a[2], a[1], a[3]))
  BASS_ChannelPlay(s.cur_handle, False)
  s.timer.start()

  s.wlen=BASS_ChannelGetLength(s.cur_handle, BASS_POS_BYTE)
  secs=BASS_ChannelBytes2Seconds(s.cur_handle, s.wlen)
  ct1=time.strftime("/<b>%M:%S</b>", time.gmtime(secs))
  s.aLabel.setText(ct1)
  s.hscale.setMaximum(int(s.wlen))
  s.wtbprogress.setMaximum(s.wlen)

  a=time.gmtime(secs)
  s.a_pause.setIcon(s.style().standardIcon(QStyle.SP_MediaPause))
  if platform.system().lower()=='windows':
    s.pTB2.setIcon(s.style().standardIcon(QStyle.SP_MediaPause))


 def get_tag(self, f, t1):
  res=''
  try:
   res=f[t1]
  except:
   res=''
  if isinstance(res, list):
    res=res[0]
  return res

 def get_tags(self, fname):
  f=mutagen.File(fname)
  l=None
  if fname.endswith(('.MP3','.mp3')):
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
  yea=self.get_tag(f, 'TDRC')
  if yea=='':
   yea=self.get_tag(f, 'TYER')
  #~ print get_tag(f, 'TLEN'), get_tag(f, 'TDEN')
  return (tit, alb, art, yea)

def LoadPlugins():
#  r, d = os.path.split(os.path.abspath(os.path.expanduser(sys.argv[0])))
#  print(r, d)
 d =''
 e=''
 p=''
 if platform.system().lower() == 'windows':
  d=os.path.dirname('bass.dll')
  e='.dll'
  p=''
 else:
  d=os.path.dirname('libbass.so')
  e='.so'
  p='lib'
 d=os.path.realpath(d) 
 n= d+'\\'+p+'bass*'+e
 print(n)
 l=glob.glob(n)
 print('l:', l)
 for f in l:
  print ('f: ', f)
   #try:
  p=ctypes.c_char_p(f.encode('utf-8', 'errors=ignore'))
  h=BASS_PluginLoad(p, 0)
  if h>0:
   #~ print f
   bpi = BASS_PLUGININFO()
   bpi = BASS_PluginGetInfo(h)
   #print(bpi)
   for i in range(0,bpi.contents.formatc):
    #print (str(bpi.contents.formats[i].name), str(bpi.contents.formats[i].exts))
    formats.append(str(bpi.contents.formats[i].exts))
    names.append(str(bpi.contents.formats[i].name))
   plugins.append(h)
 #print(formats, names)
    #except:
    # pass

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = QMini()

  ex.setWindowTitle('QMini')
  print (BASS_Init(-1, 44100,0, ex.winId(),0))
  LoadPlugins()
  # a1=os.path.realpath('bass_tta.dll').encode('utf-8', 'ignore')
  # print(a1)
  # h=BASS_PluginLoad(a1, BASS_UNICODE)
  # print(h)
  # if h>0:
    # plugins.append(h)
  # else:
    # print('BASS_ErrorGetCode=', BASS_ErrorGetCode())
  # BASS_SetConfig(BASS_CONFIG_DEV_BUFFER,250)
  sys.exit(app.exec_())
