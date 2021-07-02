from fluid_pad.utils.singleton import Singleton


class InstrumentService(metaclass=Singleton):
  notes_matrix = [
      [None, 'C#', 'D#', None, 'F#', 'G#', 'A#'],
      ['C', 'D', 'E', 'F', 'G', 'A', 'B']
  ]
  bank = 0
  min_val = 0
  max_val = 127
  current = 0

  def get_notes_matrix(self):
    return self.notes_matrix

  def get_bank(self):
    return self.bank

  def get_current(self):
    return self.current

  def get_min_value(self):
    return self.min_val

  def get_max_value(self):
    return self.max_val

  def set_new_instrument(self, increment=0):
    new_instrument = self.current + increment
    if new_instrument < self.min_val:
      new_instrument = self.min_val
    if new_instrument > self.max_val:
      new_instrument = self.max_val
    self.current = new_instrument
