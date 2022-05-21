#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from pybass import *

BASS_Init(-1, 44100,0, 0,0)
h=HPLUGIN(0)
p=ctypes.c_char_p("C:\\_work\\python\\qmini\\bass_ape.dll".encode('utf-8', 'errors=ignore'))
d=ctypes.c_ulong(0)
#h=BASS_PluginLoad(h, "")
BASS_PluginLoad(p, h)
print('h=', h)
#bpi = BASS_PLUGININFO()
bpi = BASS_PluginGetInfo(h)
v=ctypes.c_ulong()
#v=bpi._fields_['version']
print(bpi*formats)
BASS_PluginFree(0)
BASS_Free()
