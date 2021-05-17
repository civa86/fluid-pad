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
DEVICE_PORT_NAME = "Launchpad"

SF2 = "resources/sf2/VintageDreamsWaves-v2.sf2"

NOTES_MATRIX = [
    [None, 'C#', 'D#', None, 'F#', 'G#', 'A#'],
    ['C', 'D', 'E', 'F', 'G', 'A', 'B']
]

INSTRUMENT_DATA = {
    "BANK": 0,
    "INSTRUMENT_MIN": 0,
    "INSTRUMENT_MAX": 127,
    "INSTRUMENT": 0
}

DRUMS_DATA = {
    "BANK": 128,
    "KITS": [2, 5],
    "KIT": 0,
    "MAPPING": {
        2: [
            [0,      0,       0,       0,       0,      0,      0,       0],
            [0,      0,       0,       0,       0,      0,      0,       0],
            [0,      'C-1',   'C#-1',  'D-1',   'E-1',  'F-1',  'F#-1',    0],
            [0,      'D#-1',  'B-1',   'C-2',   'D#-2', 'D-2',  'E-2',     0],
            [0,      'C#-2',  'F#-2',  'A#-2',  'F-2',  'G-2',  'A-2',  'B-2', ],
            ['C#-3', 'G#-3',  'B-4',   'D#-5',  'C-3',  'D-3',  'D-4',  'D#-4'],
            [0,      0,       0,       0,       'E-4',   0,     0,           0],
            [0,      0,       0,       0,       0,       0,     0,       0]
        ],
        5: [
            [0,     0,       0,       0,       0,       0,       0,       0],
            [0,     0,       0,       0,       0,       0,       0,       0],
            [0,     0,       'G-1',   'A-1',   'G#-1',  'D-2',   0,       0],
            [0,     'A#-1',  'B-1',   'C-2',   'D#-2',  'F-2',   'B-2',   0],
            [0,     0,       'C#-2',  'F#-2',  'E-2',   'G-2',   0,       0],
            [0,     0,       'A#-2',  'C#-3',  'A-2',   0,       0,       0],
            [0,     0,       0,       0,       0,       0,       0,       0],
            [0,     0,       0,       0,       0,       0,       0,       0]
        ]
    }
}
