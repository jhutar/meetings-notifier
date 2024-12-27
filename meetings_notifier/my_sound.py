#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import warnings

warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="Your system is avx2 capable but pygame was not built with support for it.",
)
import pygame


pygame.mixer.init()

def play(sound="/usr/share/sounds/alsa/Front_Center.wav"):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()
