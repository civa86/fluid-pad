import mido
from fluid_pad.const import DRUMS_DATA


class MidiController:
  colors = {
      "GREEN": 60,
      "GREEN_LOW": 28,
      "YELLOW": 62,
      "AMBER": 63,
      "RED": 15,
      "RED_LOW": 13,
      "GREEN_FLASH": 56
  }
  note_min = 112
  note_max = 118

  next_instrument_key = 107
  next_10_instruments_key = 105
  prev_instrument_key = 106
  prev_10_instruments_key = 104

  notes_keys_col = 7
  semi_notes_void_col = [0, 3]
  octave_keys = [7, 23, 39, 55, 71, 87, 103, 119]
  mode_keys = [109, 110, 111]
  song_keys = [8, 24, 40, 56, 72, 88, 104, 120]

  drum_keys = None
  drum_keys_col = 8

  def __init__(self, port):
    self.port = port
    self.drum_keys = range(0, len(DRUMS_DATA['KITS']))

  def set_port(self, port):
    self.port = port

  def send_lp_note(self, note, velocity):
    if self.port:
      self.port.send(mido.Message('note_on', note=note, velocity=velocity))

  def send_lp_cc(self, control, value):
    if self.port:
      self.port.send(mido.Message('control_change', control=control, value=value))

  def reset_layout(self):
    self.send_lp_cc(0, 0)

  def setup_octaves(self, octave):
    for x in self.octave_keys:
      self.send_lp_note(x, self.colors["RED_LOW"])
    if len(self.octave_keys) > octave:
      self.send_lp_note(self.octave_keys[octave], self.colors["RED"])

  def setup_instrument_navigator(self, current, min, max):
    if current > min:
      self.send_lp_cc(self.prev_instrument_key, self.colors["GREEN"])
      self.send_lp_cc(self.prev_10_instruments_key, self.colors["GREEN"])
    else:
      self.send_lp_cc(self.prev_instrument_key, self.colors["GREEN_LOW"])
      self.send_lp_cc(self.prev_10_instruments_key, self.colors["GREEN_LOW"])

    if current < max:
      self.send_lp_cc(self.next_instrument_key, self.colors["GREEN"])
      self.send_lp_cc(self.next_10_instruments_key, self.colors["GREEN"])
    else:
      self.send_lp_cc(self.next_instrument_key, self.colors["GREEN_LOW"])
      self.send_lp_cc(self.next_10_instruments_key, self.colors["GREEN_LOW"])

  def setup_drum_navigator(self, current):
    for x in self.drum_keys:
      current_color = self.colors["RED"] if x == current else self.colors["RED_LOW"]
      self.send_lp_note(x, current_color)

  def is_note_keys(self, x, y):
    return x < self.notes_keys_col and (y % 2 != 0 or x not in self.semi_notes_void_col)

  def get_button_coordinates(self, midi_note):
    btn_col = midi_note % 16
    btn_row = int(midi_note / 16)
    return btn_col, btn_row

  def init_instrument_layout(self, octave):
    self.reset_layout()
    self.send_lp_cc(self.mode_keys[0], self.colors["AMBER"])
    self.setup_octaves(octave)
    for x in range(0, self.notes_keys_col):
      for y in range(0, 8):
        if self.is_note_keys(x, y):
          n = y * 16 + x
          col = self.colors["AMBER"] if y % 2 == 0 else self.colors["YELLOW"]
          self.send_lp_note(n, col)

  def init_drums_layout(self, kit):
    self.reset_layout()
    self.send_lp_cc(self.mode_keys[1], self.colors["AMBER"])
    for x in range(1, self.drum_keys_col):
      for y in range(1, 8):
        n = y * 16 + x
        if DRUMS_DATA['MAPPING'][kit][y][x] != 0:
          self.send_lp_note(n, self.colors["AMBER"])
