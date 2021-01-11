import sys
import signal
import time
import mido
import threading

import utils.synth as synth
from utils.midi import MidiController

# FUNCTIONS


def check_device():
    while 1:
        if DEVICE_PORT_NAME in mido.get_input_names():
            print('DEVICE OK', mido.get_input_names())
        else:
            print('Wait for', DEVICE_PORT_NAME)
        time.sleep(2)


def check_launchpad():
    print('run check')
    # TODO: check for unplug / replug....
    check = True
    while check == True:
        if DEVICE_PORT_NAME in mido.get_input_names():
            check = False
        else:
            print('Wait for', DEVICE_PORT_NAME)
            time.sleep(2)


def end_process_handler(signal, frame):
    ctrl.reset_layout()
    sys.exit(0)


def send_note(message, note, octave, press_color, release_color):
    if message.velocity == 127:
        ctrl.send_lp_note(message.note, press_color)
        synth.play(note, octave)
    else:
        ctrl.send_lp_note(message.note, release_color)
        synth.stop(note, octave)


def update_instrument(value):
    new_instrument = SYNTH_DATA[mode]["INSTRUMENT"] + value
    if new_instrument < SYNTH_DATA[mode]["INSTRUMENT_MIN"]:
        new_instrument = SYNTH_DATA[mode]["INSTRUMENT_MIN"]
    if new_instrument > SYNTH_DATA[mode]["INSTRUMENT_MAX"]:
        new_instrument = SYNTH_DATA[mode]["INSTRUMENT_MAX"]

    SYNTH_DATA[mode]["INSTRUMENT"] = new_instrument
    print("SET INSTRUMENT:", 'bank', SYNTH_DATA[mode]["BANK"], 'instrument', SYNTH_DATA[mode]["INSTRUMENT"])
    synth.set_instrument(SYNTH_DATA[mode]["BANK"], SYNTH_DATA[mode]["INSTRUMENT"])
    ctrl.setup_instrument_navigator(SYNTH_DATA[mode]["INSTRUMENT"], SYNTH_DATA[mode]["INSTRUMENT_MIN"], SYNTH_DATA[mode]["INSTRUMENT_MAX"])


# CONSTANTS
DEVICE_PORT_NAME = "Launchpad"
SF2 = "sf2/VintageDreamsWaves-v2.sf2"
NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
SEMI_NOTES = [None, 'C#', 'D#', None, 'F#', 'G#', 'A#']
SYNTH_DATA = [
    {
        "BANK": 0,
        "INSTRUMENT_MIN": 0,
        "INSTRUMENT_MAX": 127,
        "INSTRUMENT": 0
    },
    {
        "BANK": 128,
        "INSTRUMENT_MIN": 2,
        "INSTRUMENT_MAX": 2,
        "INSTRUMENT": 2
    }
]

# APPLICATION STATE
mode = 0
octave = 3
ctrl = None

# MAIN
thread = threading.Thread(target=check_device)
thread.daemon = True
thread.start()

signal.signal(signal.SIGINT, end_process_handler)
signal.signal(signal.SIGTERM, end_process_handler)

with mido.open_output(DEVICE_PORT_NAME, autoreset=True) as output_port:
    with mido.open_input(DEVICE_PORT_NAME, autoreset=True) as input_port:
        print('OUTPUT PORT: {}'.format(output_port))
        print('INPUT PORT: {}'.format(input_port))

        ctrl = MidiController(output_port)
        ctrl.init_layout(mode, octave)

        synth.load_sf2(SF2)
        update_instrument(0)

        print('Waiting for input..')

        for message in input_port:
            print('Received {}'.format(message))
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
                    # OCTAVE
                    if message.note in ctrl.octave_keys:
                        octave = message.note % 16
                        ctrl.setup_octaves(octave)
                    # NOTES
                    if message.note in ctrl.note_keys:
                        n = NOTES[message.note % 16]
                        o = int(message.note / 32) - 2 + octave
                        print('NOTE', str(n) + '-' + str(o))
                        send_note(message, n, o, ctrl.colors["GREEN"], ctrl.colors["YELLOW"])
                    # SEMI_NOTES
                    if message.note in ctrl.semi_note_keys:
                        n = SEMI_NOTES[message.note % 16]
                        o = int(message.note / 32) - 2 + octave
                        print('SEMI_NOTE', str(n) + '-' + str(o))
                        send_note(message, n, o, ctrl.colors["GREEN"], ctrl.colors["AMBER"])
