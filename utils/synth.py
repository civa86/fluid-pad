import sys
from mingus.midi import fluidsynth
from mingus.containers import Note

SYNTH_CHANNEL = 1


def load_sf2(SF2):
    if not fluidsynth.init(SF2):
        print("Couldn't load soundfont", SF2)
        sys.exit(1)


def set_instrument(bank, instrument):
    fluidsynth.set_instrument(SYNTH_CHANNEL, instrument, bank)


def play(note, octave):
    fluidsynth.play_Note(Note(note, octave), SYNTH_CHANNEL, 100)


def stop(note, octave):
    fluidsynth.stop_Note(Note(note, octave), SYNTH_CHANNEL)
