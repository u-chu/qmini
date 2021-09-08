#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from genericpath import isdir
import sys, os
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication,  QHBoxLayout, QLabel, QMainWindow, QProgressBar,\
    QToolBar, QAction,  QStyle, QSlider, QWidget, QToolButton, QMenu, QStatusBar, QStyleFactory, \
    QPushButton, QFileDialog
from PyQt5.QtGui import QIcon
import pybass
import glob
import time
import configparser
#import Notify

import mutagen
from pybass import *

configdir = os.path.expanduser('~/')
configname=os.path.join(configdir, 'qmbp.ini')
config = configparser.ConfigParser()

formats=[]
names=[]

plugins=[]
"""Notify.init('qmbp')
noti=Notify.Notification()"""


class QMini(QMainWindow):

 def __init__(self):
  super().__init__()
  self.songs=[]
  self.song_ptr=0
  self.cur_handle=None
  self.timer=QtCore.QTimer()
  self.timer.timeout.connect(self.timer_func)
  self.initUI()

 def dragEnterEvent(self, e):
  print (e.mimeData().urls(), '\n')
  if e.mimeData().hasUrls():
   e.accept()
  else:
   e.ignore()

 def add_file_to_list(self, fname):
  buf = BASS_StreamCreateFile(False, fname, 0,0,BASS_MUSIC_PRESCAN|BASS_SAMPLE_FLOAT|BASS_UNICODE)
  if buf!=0:
   BASS_StreamFree(buf)
   self.songs.append(fname)
  else:
   print("BASS_ErrorGetCode= ", BASS_ErrorGetCode(), '; file name= ', fname )


 def add_from_dir(self, i):
  for r, d, f in os.walk(i):
   for fn in f:
    if '.' in fn:
     fname=os.path.join(r, fn)
     if(os.path.isdir(fname)):
      self.add_from_dir(fname)
     else:
      self.add_file_to_list(fname)
     """buf = BASS_StreamCreateFile(False, fname, 0,0,BASS_MUSIC_PRESCAN|BASS_SAMPLE_FLOAT|BASS_UNICODE)
     print (buf)
     if buf!=0:
      BASS_StreamFree(buf)
      self.songs.append(fname)
     else:
       print(BASS_ErrorGetCode())"""

 def dropEvent(self, e):
   #~ uri=[]
   for i in e.mimeData().urls():
     #print(i.path()[1::])
     i=i.path()[1::]
     if (os.path.isdir(i)):
      self.add_from_dir(i)
     else:
      self.add_file_to_list(i)
      """buf = BASS_StreamCreateFile(False, i, 0,0,BASS_MUSIC_PRESCAN|BASS_SAMPLE_FLOAT|BASS_UNICODE)
      print(buf)
      if buf!=0:
       BASS_StreamFree(buf)
       self.songs.append(i)
      else:
       print(BASS_ErrorGetCode())"""
   print (self.songs)
   if(self.song_ptr<=0):
    self.song_ptr=0
   if self.cur_handle==None:
    self.playfile(self.song_ptr)


 def initUI(self):
  #~ self.statusBar().showMessage('Ready')
  self.setGeometry(300, 300, 500, 30)
  self.setWindowTitle('qmbp')
  self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))))
  self.setAcceptDrops(True)
  # Using a title
  a_rev = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaSeekBackward'))), 'Rewind', self)
  a_forw = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaSeekForward'))), 'Forward', self)
  a_stop = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaStop'))), 'Stop', self)
  """
  'SP_MediaPause',
  'SP_MediaPlay',
  """
  self.a_pause = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))), 'Play/Pause', self)
  a_back = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaSkipBackward'))), 'Back', self)
  a_next = QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaSkipForward'))), 'Next', self)

  a_stop.triggered.connect(self.pstop)
  self.a_pause.triggered.connect(self.ppause)
  a_rev.triggered.connect(self.skip_back)
  a_forw.triggered.connect(self.skip_fwd)
  a_back.triggered.connect(self.prev_song)
  a_next.triggered.connect(self.next_song)

  a_shuffle=QAction('Shuffle', self)
  a_repeat=QAction('Repeat', self)
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
  menuToolButton=QToolButton()
  #QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DockWidgetCloseButton'))),
                               #'Options', self)
  menuToolButton.setPopupMode(QToolButton.InstantPopup)
  #menuToolButton.setArrowType(QtCore.Qt.DownArrow)
  ptToolbar.addWidget(menuToolButton)
  """a_openfile=QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton'))), 'Add file(s)', self)
  a_openfile.triggered.connect(self.add_files)
  a_openfolder=QAction(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirOpenIcon'))), 'Add folder(s)', self)
  a_openfolder.triggered.connect(self.add_folders)"""
  oMenu=QMenu('Options')
  #oMenu.addAction(a_openfile)

  #oMenu.addAction(a_openfolder)
  #oMenu.addSeparator()
  oMenu.addAction(a_shuffle)
  oMenu.addAction(a_repeat)


  """sMenu=oMenu.addMenu('Styles')
  sPlastic= QAction('Plastic', self)
  sMac=QAction('Mac', self)
  sWindows=QAction('Windows', self)
  sWindowsXP=QAction('Windows XP', self)
  sWindowsVista=QAction('Windows Vista', self)
  sCleanlooks=QAction('Cleanlooks', self)
  sMotif=QAction('Motif', self)
  sCustom=QAction('Cutsom style', self)
  sMenu.addAction(sPlastic)
  sMenu.addAction(sMac)
  sMenu.addAction(sWindows)
  sMenu.addAction(sWindowsXP)
  sMenu.addAction(sWindowsVista)
  sMenu.addAction(sCleanlooks)
  sMenu.addAction(sMotif)
  sMenu.addSeparator()
  sMenu.addAction(sCustom)"""
  menuToolButton.setMenu(oMenu)
  #sWindows.triggered.connect(self.set_style, 'Fusion')
  #sWindows.triggered.connect(lambda x:QApplication.setStyle(x), 'Fusion')
  self.repeat=False
  a_repeat.triggered.connect(lambda x: not x, self.repeat)
  self.random=False
  a_shuffle.triggered.connect(lambda x: not x, self.random)

  #pShuffle=QCheckBox("Shuffle")
  #pRandom=QCheckBox("Random")
  #ptToolbar.addWidget(pShuffle)
  #ptToolbar.addWidget(pRandom)
  hbox=QHBoxLayout()
  #
  #a_openfile = QPushButton("Open file")
  #a_openfile.setIcon(QIcon())
  #a_openfile.resize(QtCore.QSize(16, 16))
  self.titl_label=QLabel('')
  self.titl_label.setTextFormat(QtCore.Qt.RichText)
  #hbox.addWidget(a_openfile)
  hbox.addWidget(self.titl_label)
  wdg = QWidget()
  wdg.setLayout(hbox);
  self.setCentralWidget(wdg)
  #sb=QStatusBar()
  #sb.setSizeGripEnabled(False)
  #self.setStatusBar(sb)
  self.show()
  self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
  self.destroyed.connect(self.on_destroy)
  #QApplication.setStyle('Macintosh')

 """def add_folders(self):
  folders=QFileDialog.getExistingDirectory(self, "Add folder(s)", "", QFileDialog.ShowDirsOnly)
  print(folders)"""

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


 @staticmethod
 def on_destroy(self):
  print(self.parent())
  if not BASS_PluginFree(0):
   print ("plugins free error: ", BASS_ErrorGetCode())
  BASS_PluginFree(0)
  BASS_Free()

  p= QtCore.QPoint()
  self.mapToGlobal(p)
  if not os.path.exists(configdir):
   os.makedirs(configdir)
  if not config.has_section("main"):
   config.add_section("main")
  config.set('main', 'y', str(p.y()))
  config.set('main', 'x', str(p.x()))
  #config.set('main', 'randon', str(self.random))
  #config.set('main', 'repeat', str(self.repeat))
  with open(configname, 'w') as configfile:
   config.write(configfile)
  """if self.cur_handle != None:
   bcia= BASS_ChannelIsActive(s.cur_handle)
   config.set('main', 'status', str(bcia))
   config.set('main', 'song', str(s.song_ptr))
   if bcia==BASS_ACTIVE_PLAYING or bcia==BASS_ACTIVE_PAUSED:
    curpl=os.path.join(configdir, 'current.m3u')
    fp = open(curpl, "w")
    newlist = self.songs[:]
    newlist.sort(reverse=False)
    for song in newlist:
     fp.write(song + '\n')
    fp.close()
  else:
   config.set('main', 'status', str(BASS_ACTIVE_STOPPED))"""
  with open(configname, 'w') as configfile:
   config.write(configfile)


 def timer_func(self):
  #print ('timer_func')
  if self.song_ptr<0 or self.cur_handle==None:
   return True
  bcia= BASS_ChannelIsActive(self.cur_handle)
  pos=BASS_ChannelGetPosition(self.cur_handle, pybass.BASS_POS_BYTE)
  secs=BASS_ChannelBytes2Seconds(self.cur_handle, pos)
  self.hscale.setValue(pos)
  #print(self.hscale.getTickPosition())
  ct1=time.strftime("<b>%M:%S</b>", time.gmtime(secs))
  #print(ct1, pos)
  self.cLabel.setText(ct1)
  if bcia==BASS_ACTIVE_STOPPED or pos >= self.wlen:
   self.next_song()
  return True

 def prev_song(self, w=None):
  if self.song_ptr>0:
   self.song_ptr-=1
   if self.cur_handle!= None:
    BASS_ChannelStop(self.cur_handle)
    BASS_StreamFree(self.cur_handle)
    self.cur_handle=None
   #self.stop()
   self.playfile(self.song_ptr)
  else:
   self.song_ptr=-1
   self.pstop()

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

 def ppause(s,  e):
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
   s.a_pause.setIcon(QIcon(s.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))))
  elif bcia == BASS_ACTIVE_PAUSED or bcia == BASS_ACTIVE_STALLED:
   BASS_ChannelPlay(s.cur_handle, False)
   s.a_pause.setIcon(QIcon(s.style().standardIcon(getattr(QStyle, 'SP_MediaPause'))))


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
   s.a_pause.setIcon(QIcon(s.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))))
   #~ s.abox.set_text("/00:00")
   #~ s.cbox.set_markup("<b>00:00</b>")
   #~ s.hscale.set_value(0)
   #~ s.lb.set_value(0)
   # ~ s.lb.set_fraction(0)
   #~ s.toolbar.get_nth_item(4).set_stock_id(gtk.STOCK_MEDIA_PLAY)
   #~ s.set_scale_slider(0)
   s.titl_label.setText('')
   s.aLabel.setText('')
   s.cLabel.setText('')
   s.timer.stop()
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
  if f> len(s.songs):
   s.song_ptr=0
   f=0
  fname = s.songs[f]
  print (fname)
  s.cur_handle=BASS_StreamCreateFile(False, fname, 0,0,BASS_MUSIC_PRESCAN|BASS_STREAM_AUTOFREE|BASS_SAMPLE_FLOAT|BASS_UNICODE)
  #print ('s.cur_handle=', s.cur_handle)

  if s.cur_handle==None:
   ec=BASS_ErrorGetCode()
   print (get_error_description(ec), ec)
  a=s.get_tags(fname)

  s.titl_label.setText("<b>%s</b> - <i>%s</i> - %s (%s)"%(a[0], a[2], a[1], a[3]))
  BASS_ChannelPlay(s.cur_handle, False)
  s.timer.start()

  s.wlen=BASS_ChannelGetLength(s.cur_handle, BASS_POS_BYTE)
  secs=BASS_ChannelBytes2Seconds(s.cur_handle, s.wlen)
  ct1=time.strftime("/<b>%M:%S</b>", time.gmtime(secs))
  s.aLabel.setText(ct1)
  s.hscale.setMaximum(int(s.wlen))

  a=time.gmtime(secs)
  s.a_pause.setIcon(QIcon(s.style().standardIcon(getattr(QStyle, 'SP_MediaPause'))))


 def get_tag(self, f, t1):
  res=''
  try:
   res=f[t1]
  except:
   res=''
  return res

 def get_tags(self, fname):
  f=mutagen.File(fname)
  l=None
  if fname.endswith(('.MP3','.mp3')):
   l= self.get_tags_mp3(f)
  else:
   l= self.get_tags(f)
  return l

 def get_tags_common(self, f):
  alb=self.get_tag(f,  'album')
  art=self.get_tag(f, 'artist')
  tit=self.get_tag(f, 'title')
  yea=self.get_tag(f, 'year')
  if yea=='':
   yea=self.get_tag(f, 'date')
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
 r, d = os.path.split(os.path.abspath(os.path.expanduser(sys.argv[0])))
 #print(r, d)

 for f in glob.glob(r+'/bass*.dll'):
   #print (f)
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
  BASS_Init(-1, 44100,0, 0,0)
  # ~ print BASS_PluginLoad("libtags.so", 0)
  LoadPlugins()
  #print (plugins)
  #print (BASS_GetVersion())

  app = QApplication(sys.argv)
  ex = QMini()
  #w = QWidget()
  #w.resize(250, 150)
  #w.move(300, 300)
  #w.setWindowTitle('Simple')
  #w.show()

  sys.exit(app.exec())
