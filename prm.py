#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, ctypes, glob
from pybass import *

BASS_Init(-1, 44100,0, 0,0)

exts=b""

#l=[(, '|APE|','*.ape')]
"""l=[b'bass_ape.dll']
#p=ctypes.c_char_p(b"C:\\_work\\python\\qmini\\bass_ape.dll")
for a in l:
    a=os.path.abspath(a)
    print (a)
    p=ctypes.c_char_p(a)
    print (p)"""
	
#for i in l:
#h=HPLUGIN(0)
#a=os.path.abspath(i[0]).encode('utf-8', 'errors=ignore')
#print(p)
    
r, d = os.path.split(os.path.abspath(os.path.expanduser(sys.argv[0])))
for f in glob.glob(r+'/bass*.dll'):
    print(f)
    p=ctypes.c_char_p(f.encode('utf-8', 'errors=ignore'))
    h=BASS_PluginLoad(p, 0)
    print (h, BASS_ErrorGetCode())
    if h>0:
        bpi = BASS_PluginGetInfo(h)
        for i in range(0,bpi.contents.formatc):
            exts+=bpi.contents.formats[i].exts+b";"
            print (str(bpi.contents.formats[i].name), str(bpi.contents.formats[i].exts))
print(exts)        
BASS_PluginFree(0)
BASS_Free()
#v2=ctypes.cast(bpi.contents.formatc, ctypes.c_ulong)
		# ~ bpiv1=ctypes.cast(v1, ctypes.py_object).value
		# ~ print v1, v1._fields_
		# ~ bpiv1=ctypes.cast(v1.formats, ctypes.py_object).value
		# ~ print bpiv1
		# ~ print v1.formats.contents
		# ~ print dir(v1)
		# ~ v2=v1.formatc
		# ~ print v2, dir(v2)
		# ~ print ctypes.cast(v2, ctypes.py_object).value
		# ~ print v3
		# ~ bci=bpi.contents
		# ~ print bci
		# ~ v2=ctypes.cast(bci, ctypes.py_object).value
		# ~ print bpi.formatc, v2
		#~ v4=ctypes.cast(bpi.formatc, ctypes.py_object).value
		#~ print (ctypes.c_wchar_p)(bpi.formats[0].name)
		#~ for a in bpi:
			#~ print a
		#~ print dir(bpi)
