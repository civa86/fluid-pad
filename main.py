import sys
import os
import signal
import time
import threading

import mido

from utils.log import set_log_level, debug
import utils.synth as synth
from utils.midi import MidiController

from drums import DRUM_MAP_KEYS

# ----------------------------------------------------------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------------------------------------------------------
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
    "KIT": 0
}
# ----------------------------------------------------------------------------------------------------------------------
# APPLICATION STATE
# ----------------------------------------------------------------------------------------------------------------------
mode = 0
octave = 2
ctrl = None
# ----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------


def device_listener():
    device_initialized = False
    while 1:
        if DEVICE_PORT_NAME in mido.get_input_names():
            if device_initialized == False and not ctrl is None:
                init()
                device_initialized = True
        else:
            device_initialized = False
        time.sleep(1)


def end_process_handler(signal, frame):
    if ctrl is not None:
        ctrl.reset_layout()
    debug('gracefully exiting')
    sys.exit(0)


def send_note_coords(message, x, y):
    n = NOTES_MATRIX[y % 2][x]
    o = int(message.note / 32) + octave
    if message.velocity == 127:
        debug('Play Note', n + '-' + str(o))
        ctrl.send_lp_note(message.note, ctrl.colors["GREEN"])
        synth.play(n, o)
    else:
        ctrl.send_lp_note(message.note, ctrl.colors["YELLOW"] if btn_row % 2 != 0 else ctrl.colors["AMBER"])
        synth.stop(n, o)


def send_note_str(message, note_str):
    note_info = note_str.split('-')
    if message.velocity == 127:
        debug('Play Note', note_str)
        ctrl.send_lp_note(message.note, ctrl.colors["GREEN"])
        synth.play(note_info[0], int(note_info[1]))
    else:
        debug('Stop Note', note_str)
        ctrl.send_lp_note(message.note, ctrl.colors["AMBER"])
        synth.stop(note_info[0], int(note_info[1]))


def init():
    debug('init mode', mode)
    if mode == 0:
        ctrl.init_instrument_layout(octave)
        update_instrument()
    elif mode == 1:
        ctrl.init_drums_layout(get_drum_current_kit())
        update_drums(DRUMS_DATA['KIT'])


def get_drum_keys():
    return range(0, len(DRUMS_DATA['KITS']))


def get_drum_current_kit():
    return DRUMS_DATA["KITS"][DRUMS_DATA["KIT"]]


def update_drums(kit):
    if kit != DRUMS_DATA['KIT']:
        DRUMS_DATA['KIT'] = kit
        ctrl.init_drums_layout(get_drum_current_kit())

    drum_current_kit = get_drum_current_kit()
    debug("set drum", 'bank', DRUMS_DATA["BANK"], 'kit', drum_current_kit)
    synth.set_instrument(DRUMS_DATA["BANK"], drum_current_kit)
    ctrl.setup_drum_navigator(DRUMS_DATA["KIT"], get_drum_keys())


def update_instrument(increment=0):
    new_instrument = INSTRUMENT_DATA["INSTRUMENT"] + increment
    if new_instrument < INSTRUMENT_DATA["INSTRUMENT_MIN"]:
        new_instrument = INSTRUMENT_DATA["INSTRUMENT_MIN"]
    if new_instrument > INSTRUMENT_DATA["INSTRUMENT_MAX"]:
        new_instrument = INSTRUMENT_DATA["INSTRUMENT_MAX"]

    INSTRUMENT_DATA["INSTRUMENT"] = new_instrument
    debug("set instrument", 'bank', INSTRUMENT_DATA["BANK"], 'instrument', INSTRUMENT_DATA["INSTRUMENT"])
    synth.set_instrument(INSTRUMENT_DATA["BANK"], INSTRUMENT_DATA["INSTRUMENT"])
    ctrl.setup_instrument_navigator(INSTRUMENT_DATA["INSTRUMENT"], INSTRUMENT_DATA["INSTRUMENT_MIN"], INSTRUMENT_DATA["INSTRUMENT_MAX"])


# ----------------------------------------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------------------------------------
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
set_log_level(LOGLEVEL)

device_listener_thread = threading.Thread(target=device_listener)
device_listener_thread.daemon = True
device_listener_thread.start()

signal.signal(signal.SIGINT, end_process_handler)
signal.signal(signal.SIGTERM, end_process_handler)

while not DEVICE_PORT_NAME in mido.get_input_names():
    debug('Wait for', DEVICE_PORT_NAME)
    time.sleep(2)

with mido.open_output(DEVICE_PORT_NAME, autoreset=True) as output_port:
    with mido.open_input(DEVICE_PORT_NAME, autoreset=True) as input_port:
        debug('OUTPUT PORT: {}'.format(output_port))
        debug('INPUT PORT: {}'.format(input_port))

        synth.load_sf2(SF2)
        ctrl = MidiController(output_port)
        synth.volume()

        debug('Waiting for midi messages..')

        for message in input_port:
            debug('Received {}'.format(message))
            # SWITCH MODES
            if message.type == 'control_change' and message.value == 127 and message.control in ctrl.mode_keys:
                new_mode = ctrl.mode_keys.index(message.control)
                if new_mode != mode:
                    mode = new_mode
                    init()

            # INSTRUMENT MODE
            if mode == 0:
                if message.type == 'control_change' and message.value == 127:
                    # INSTRUMENT NAVIGATOR
                    if message.control == ctrl.next_instrument_key:
                        update_instrument(1)
                    if message.control == ctrl.next_10_instruments_key:
                        update_instrument(10)
                    if message.control == ctrl.prev_instrument_key:
                        update_instrument(-1)
                    if message.control == ctrl.prev_10_instruments_key:
                        update_instrument(-10)

                if message.type == 'note_on':
                    btn_col, btn_row = ctrl.get_button_coordinates(message.note)
                    # OCTAVE
                    if message.note in ctrl.octave_keys:
                        octave = btn_row
                        ctrl.setup_octaves(octave)
                    # NOTES
                    if ctrl.is_note_keys(btn_col, btn_row):
                        send_note_coords(message, btn_col, btn_row)
            # DRUMS MODE
            elif mode == 1:
                if message.type == 'note_on':
                    btn_col, btn_row = ctrl.get_button_coordinates(message.note)
                    current_drum_kit = get_drum_current_kit()
                    # KITS
                    if message.note in get_drum_keys():  # TODO: move to ctrl??
                        update_drums(message.note)
                    # NOTES
                    if DRUM_MAP_KEYS[current_drum_kit][btn_row][btn_col] != 0:
                        send_note_str(message, DRUM_MAP_KEYS[current_drum_kit][btn_row][btn_col])
