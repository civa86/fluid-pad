import sys

from mingus.midi import fluidsynth
from mingus.containers import Note

from utils.log import debug

SYNTH_CHANNEL = 1


def load_sf2(SF2):
    if not fluidsynth.init(SF2):
        debug("Couldn't load soundfont", SF2)
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


def volume():
    debug('settings....')
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.gain", 0.8)

    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.chorus.level", 1)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.chorus.speed", 2)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.chorus.depth", 40)

    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.reverb.level", 1)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.reverb.room-size", 0.1)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.reverb.width", 5)

    # debug(dir(fluidsynth.fs))
