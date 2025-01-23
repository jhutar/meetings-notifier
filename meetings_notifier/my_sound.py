#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging

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
import wave
import pasimple

from . import helpers


config = {
    "sound_alerts": [
        {
            "sink": "nonexixtent_sink",
            "modify": True,
            "volume": 0.3,
        },
        {
            "sink": "alsa_output.pci-0000_00_1f.3-platform-skl_hda_dsp_generic.HiFi__Speaker__sink",
            "modify": True,
            "volume": 0.3,
        },
    ],
    "sound_file": "/usr/share/sounds/alsa/Front_Center.wav",
}

class MySound:
    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.pulse = pulsectl.Pulse(helpers.APP_NAME)

        # Read a .wav file with its attributes
        with wave.open(self.config["sound_file"], "rb") as wave_file:
            self._format = pasimple.width2format(wave_file.getsampwidth())
            self._channels = wave_file.getnchannels()
            self._sample_rate = wave_file.getframerate()
            self._audio_data = wave_file.readframes(wave_file.getnframes())
            self.logger.info(f"Loaded file {self.config['sound_file']}: format: {self._format}, channels: {self._channels}, sample rate: {self._sample_rate}, data size: {len(self._audio_data)}")

    def play(self):
        """Play the file via PulseAudio once in all configured and available sinks, play it once"""
        for sink_setup in self.config["sound_alerts"]:
            try:
                sink = self.pulse.get_sink_by_name(sink_setup["sink"])
            except pulsectl.pulsectl.PulseIndexError:
                self.logger.warning(f"Can not find sink {sink_setup['sink']}, check your config. Skipping it.")
                continue

            self.logger.debug(f"Playing alert sound on sink {sink.name}")

            if sink_setup["modify"]:
                sink_mute_old = sink.mute
                sink_volume_old = self.pulse.volume_get_all_chans(sink)
                self.pulse.mute(sink, mute=False)
                self.pulse.volume_set_all_chans(sink, sink_setup["volume"])

            with pasimple.PaSimple(
                pasimple.PA_STREAM_PLAYBACK,
                self._format,
                self._channels,
                self._sample_rate,
                app_name=helpers.APP_NAME,
                device_name=sink.name
            ) as pa:
                pa.write(self._audio_data)
                pa.drain()

            if sink_setup["modify"]:
                self.pulse.volume_set_all_chans(sink, sink_volume_old)
                self.pulse.mute(sink, mute=sink_mute_old)


if __name__ == "__main__":
    mysound = MySound(config)
    mysound.play()
