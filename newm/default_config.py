from __future__ import annotations
from typing import Callable, Any

import os
import pwd
import time
import subprocess
import logging

from newm.layout import Layout

from pywm import (
    PYWM_MOD_LOGO,
    # PYWM_MOD_ALT
)

logger = logging.getLogger(__name__)

def execute(command: str) -> str:
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return proc.stdout.read().decode() if proc.stdout is not None else ""


mod = PYWM_MOD_LOGO
background = {
    'path': os.path.dirname(os.path.realpath(__file__)) + '/resources/wallpaper.jpg',
    'anim': True
}

outputs = [
    { 'name': 'eDP-1' },
    { 'name': 'virt-1', 'pos_x': -1280, 'pos_y': 0, 'width': 1280, 'height': 720 }
]

class BacklightManager:
    def __init__(self) -> None:
        self._current = 0
        self._max = 1
        self._enabled = True
        try:
            self._current = int(execute("brightnessctl g"))
            self._max = int(execute("brightnessctl m"))
        except Exception:
            logger.exception("Disabling BacklightManager")
            self._enabled = False

        self._predim = self._current

    def callback(self, code: str) -> None:
        if code in ["lock", "idle-lock"]:
            self._current = int(self._predim / 2)
            execute("brightnessctl s %d" % self._current)
        elif code == "idle":
            self._current = int(self._predim / 1.5)
            execute("brightnessctl s %d" % self._current)
        elif code == "active":
            self._current = self._predim
            execute("brightnessctl s %d" % self._current)

    def adjust(self, factor: float) -> None:
        if self._predim < .3*self._max and factor > 1.:
            self._predim += int(.1*self._max)
        else:
            self._predim = max(0, min(self._max, int(self._predim * factor)))
        self._current = self._predim
        execute("brightnessctl s %d" % self._current)

backlight_manager = BacklightManager()

def key_bindings(layout: Layout) -> list[tuple[str, Callable[[], Any]]]:
    return [
        ("M-h", lambda: layout.move(-1, 0)),
        ("M-j", lambda: layout.move(0, 1)),
        ("M-k", lambda: layout.move(0, -1)),
        ("M-l", lambda: layout.move(1, 0)),
        ("M-u", lambda: layout.basic_scale(1)),
        ("M-n", lambda: layout.basic_scale(-1)),
        ("M-t", lambda: layout.move_in_stack(1)),

        ("M-H", lambda: layout.move_focused_view(-1, 0)),
        ("M-J", lambda: layout.move_focused_view(0, 1)),
        ("M-K", lambda: layout.move_focused_view(0, -1)),
        ("M-L", lambda: layout.move_focused_view(1, 0)),

        ("M-C-h", lambda: layout.resize_focused_view(-1, 0)),
        ("M-C-j", lambda: layout.resize_focused_view(0, 1)),
        ("M-C-k", lambda: layout.resize_focused_view(0, -1)),
        ("M-C-l", lambda: layout.resize_focused_view(1, 0)),

        ("M-Return", lambda: os.system("alacritty &")),
        ("M-q", lambda: layout.close_focused_view()),

        ("M-p", lambda: layout.ensure_locked(dim=True)),
        ("M-P", lambda: layout.terminate()),
        ("M-C", lambda: layout.update_config()),

        ("M-f", lambda: layout.toggle_fullscreen()),

        ("ModPress", lambda: layout.toggle_overview()),

        ("XF86MonBrightnessUp", lambda: backlight_manager.adjust(1.1)),
        ("XF86MonBrightnessDown", lambda: backlight_manager.adjust(0.9)),
    ]

panels = {
    'lock': {
        'cmd': 'alacritty -e newm-panel-basic lock',
    },
    'launcher': {
        'cmd': 'alacritty -e newm-panel-basic launcher'
    },
}

bar = {
    'top_texts': lambda: [
        pwd.getpwuid(os.getuid())[0],
        time.strftime("%c"),
    ],
    'bottom_texts': lambda: [
        "newm",
        "powered by pywm"
    ]
}

energy = {
    'idle_callback': backlight_manager.callback
}
