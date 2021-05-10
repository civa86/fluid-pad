import sys
import os
import signal
import time
import threading

import mido

from utils.log import set_log_level, debug
import utils.synth as synth
from utils.midi import MidiController

SF2 = "resources/sf2/VintageDreamsWaves-v2.sf2"

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
set_log_level(LOGLEVEL)

synth.load_sf2(SF2)
synth.set_instrument(128, 5)
synth.volume()

notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

for x in range(10):
    for n in notes:
        print('play', n, 'in octave', x)
        synth.play(n, x)
        time.sleep(0.2)
        synth.stop_all()
        input("Press Enter to continue...")
