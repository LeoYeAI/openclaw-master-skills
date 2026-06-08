#!/usr/bin/env python3
import json
import os
import platform

system = platform.system().lower()
session = None
if system == 'linux':
    if os.environ.get('WAYLAND_DISPLAY'):
        session = 'wayland'
    elif os.environ.get('DISPLAY'):
        session = 'x11'
print(json.dumps({'ok': True, 'platform': system, 'linux_session': session}, ensure_ascii=False))
