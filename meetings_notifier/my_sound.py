#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###import warnings
###
###warnings.filterwarnings(
###    "ignore",
###    category=RuntimeWarning,
###    message="Your system is avx2 capable but pygame was not built with support for it.",
###)
###import pygame
###
###
###pygame.mixer.init()
###
###def play(sound="/usr/share/sounds/alsa/Front_Center.wav"):
###    pygame.mixer.music.load(sound)
###    pygame.mixer.music.play()


import pulsectl

pulse = pulsectl.Pulse('my-client-name')
for i in pulse.sink_list():
    print("Sink:", i)


import wave
import pasimple

# Read a .wav file with its attributes
with wave.open('/usr/share/sounds/alsa/Front_Center.wav', 'rb') as wave_file:
    format = pasimple.width2format(wave_file.getsampwidth())
    channels = wave_file.getnchannels()
    sample_rate = wave_file.getframerate()
    audio_data = wave_file.readframes(wave_file.getnframes())

print("format", format)
print("channels", channels)
print("sample_rate", sample_rate)
###print("audio_data", audio_data)

# Play the file via PulseAudio
with pasimple.PaSimple(pasimple.PA_STREAM_PLAYBACK, format, channels, sample_rate) as pa:
    pa.write(audio_data)
    pa.drain()
