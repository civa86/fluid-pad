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
    fluidsynth.play_Note(Note(note, octave), SYNTH_CHANNEL, 127)


def play_midi(midi_note, velocity):
    if velocity == 0:
        fluidsynth.stop_Note(midi_note, SYNTH_CHANNEL)
    else:
        fluidsynth.play_Note(midi_note, SYNTH_CHANNEL, velocity)


def stop(note, octave):
    fluidsynth.stop_Note(Note(note, octave), SYNTH_CHANNEL)


def stop_all():
    fluidsynth.stop_everything()


def note_from_int(value):
    c = Note()
    c.from_int(value)
    return c
