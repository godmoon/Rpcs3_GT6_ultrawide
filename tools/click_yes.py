#!/usr/bin/env python3
# 在 Xvfb 里给 Qt 对话框发送 Alt+Y（选中 Yes）
import time, sys
from Xlib import display, X, XK
from Xlib.ext import xtest

disp = display.Display(':99')
time.sleep(float(sys.argv[1]) if len(sys.argv) > 1 else 8)

def key(name, press=True):
    ks = XK.string_to_keysym(name)
    kc = disp.keysym_to_keycode(ks)
    xtest.fake_input(disp, X.KeyPress if press else X.KeyRelease, kc)
    disp.sync()

key('Alt_L', True); time.sleep(0.2)
key('y', True); time.sleep(0.1); key('y', False); time.sleep(0.1)
key('Alt_L', False); time.sleep(0.5)
key('Return', True); time.sleep(0.1); key('Return', False)
disp.sync()
print('sent Alt+Y / Return')
