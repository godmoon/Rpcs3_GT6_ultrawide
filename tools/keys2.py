#!/usr/bin/env python3
# 向 :99 上的游戏窗口发送按键，按键间隔可调：keys2.py 0.8 x Down Return
import sys, time
from Xlib import display, X, XK
from Xlib.ext import xtest

gap = float(sys.argv[1])
d = display.Display(':99')
xtest.fake_input(d, X.MotionNotify, x=640, y=360)
d.sync()
time.sleep(0.2)
for name in sys.argv[2:]:
    kc = d.keysym_to_keycode(XK.string_to_keysym(name))
    xtest.fake_input(d, X.KeyPress, kc)
    d.sync()
    time.sleep(0.10)
    xtest.fake_input(d, X.KeyRelease, kc)
    d.sync()
    print('key', name)
    time.sleep(gap)
