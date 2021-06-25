import sys
import logging
from mingus.midi import fluidsynth
from mingus.containers import Note

logger = logging.getLogger(__name__)


class SynthService:
  channel = 1

  def load_sf2(self, sound_font_path):
    if not fluidsynth.init(sound_font_path):
      logger.debug(f'Could not load soundfont: {sound_font_path}')
      sys.exit(1)

  def set_instrument(self, bank, instrument):
    fluidsynth.set_instrument(self.channel, instrument, bank)

  def play(self, note, octave):
    fluidsynth.play_Note(Note(note, octave), self.channel, 127)

  def play_midi(self, midi_note, velocity):
    if velocity == 0:
      fluidsynth.stop_Note(midi_note, self.channel)
    else:
      fluidsynth.play_Note(midi_note, self.channel, velocity)

  def stop(self, note, octave):
    fluidsynth.stop_Note(Note(note, octave), self.channel)

  def stop_all(self):
    fluidsynth.stop_everything()

  def note_from_int(self, value):
    c = Note()
    c.from_int(value)
    return c

  def volume(self):
    logger.debug('settings....')
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.gain", 0.8)

    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.chorus.level", 1)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.chorus.speed", 2)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.chorus.depth", 40)

    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.reverb.level", 1)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.reverb.room-size", 0.1)
    # fluidsynth.fs.fluid_settings_setnum(fluidsynth.midi.fs.settings, b"synth.reverb.width", 5)

    # logger.debug(dir(fluidsynth.fs))
