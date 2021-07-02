from fluid_pad.utils.singleton import Singleton

# DRUM_NOTES = [
#
#     {
#         inst: 4,
#         name: 'Analog',
#         notes: {
#             'kicks': ['F1', 'G1', 'G#1', 'B1', 'C2', 'A#3', 'G#4'],
#             'Snares': ['E1', 'F#1', 'A1', 'A#1', 'D2', 'D#2', 'E2', 'F3', 'G#3', 'B3', 'D4', 'D#4', 'E4', 'A#4', 'B4', 'C5'],
#             'HHs': ['F#2', 'G#2', 'A#2', 'C#3', 'D#3', 'E3', 'F#3', 'A3', 'C4', 'C#4', 'F4', 'F#4', 'A4'],
#             'Toms': ['C1', 'C#1', 'D1', 'D#1', 'C#2', 'F2', 'G2', 'A2', 'B2', 'C3', 'D3', 'G#3', 'G4']
#         }
#     }
# ]


class DrumsService(metaclass=Singleton):
  mapping = {
      2: [
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 'C-1', 'C#-1', 'D-1', 'E-1', 'F-1', 'F#-1', 0],
          [0, 'D#-1', 'B-1', 'C-2', 'D#-2', 'D-2', 'E-2', 0],
          [0, 'C#-2', 'F#-2', 'A#-2', 'F-2', 'G-2', 'A-2', 'B-2', ],
          ['C#-3', 'G#-3', 'B-4', 'D#-5', 'C-3', 'D-3', 'D-4', 'D#-4'],
          [0, 0, 0, 0, 'E-4', 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0]
      ],
      5: [
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 'G-1', 'A-1', 'G#-1', 'D-2', 0, 0],
          [0, 'A#-1', 'B-1', 'C-2', 'D#-2', 'F-2', 'B-2', 0],
          [0, 0, 'C#-2', 'F#-2', 'E-2', 'G-2', 0, 0],
          [0, 0, 'A#-2', 'C#-3', 'A-2', 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0]
      ]
  }
  bank = 128
  kits = [2, 5]
  selected_kit_index = 0

  def get_number_of_kits(self):
    return len(self.kits)

  def get_bank(self):
    return self.bank

  def set_initial_kit(self):
    self.selected_kit_index = 0

  def get_current_kit(self):
    return self.kits[self.selected_kit_index]

  def get_current_kit_index(self):
    return self.selected_kit_index

  def set_current_kit_index(self, index):
    self.selected_kit_index = index

  def get_kit_mapping(self, kit):
    return self.mapping[kit]

  def get_current_mapping(self):
    current_drum_kit = self.get_current_kit()
    return self.get_kit_mapping(current_drum_kit)
