import sys
import os
import signal
import time
import threading
import mido
import logging
import fluid_pad.synth as synth
from fluid_pad.midi import MidiController
from fluid_pad.const import DEVICE_PORT_NAME, SF2, NOTES_MATRIX, INSTRUMENT_DATA, DRUMS_DATA


mode = 0
octave = 2
ctrl = None

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------


def device_listener():
    device_initialized = False
    while True:
        if DEVICE_PORT_NAME in mido.get_input_names():
            if device_initialized == False and ctrl is not None:
                init()
                device_initialized = True
        else:
            device_initialized = False
            logger.debug(f'Wait for {DEVICE_PORT_NAME}')
        time.sleep(1)


def end_process_handler(signal, frame):
    if ctrl is not None:
        ctrl.reset_layout()
    logger.debug('gracefully exiting')
    sys.exit(0)


def send_note_coords(message, x, y):
    n = NOTES_MATRIX[y % 2][x]
    o = int(message.note / 32) + octave
    if message.velocity == 127:
        logger.debug(f'Play Note {n}-{str(o)}')
        ctrl.send_lp_note(message.note, ctrl.colors["GREEN"])
        synth.play(n, o)
    else:
        ctrl.send_lp_note(
            message.note, ctrl.colors["YELLOW"] if btn_row % 2 != 0 else ctrl.colors["AMBER"])
        synth.stop(n, o)


def send_note_str(message, note_str):
    note_info = note_str.split('-')
    if message.velocity == 127:
        logger.debug(f'Play Note {note_str}')
        ctrl.send_lp_note(message.note, ctrl.colors["GREEN"])
        synth.play(note_info[0], int(note_info[1]))
    else:
        logger.debug(f'Stop Note {note_str}')
        ctrl.send_lp_note(message.note, ctrl.colors["AMBER"])
        synth.stop(note_info[0], int(note_info[1]))


def init():
    logger.debug(f'init mode {mode}')
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
    logger.debug(
        f'Set drum: bank {DRUMS_DATA["BANK"]}, kit {drum_current_kit}')
    synth.set_instrument(DRUMS_DATA["BANK"], drum_current_kit)
    ctrl.setup_drum_navigator(DRUMS_DATA["KIT"], get_drum_keys())


def update_instrument(increment=0):
    new_instrument = INSTRUMENT_DATA["INSTRUMENT"] + increment
    if new_instrument < INSTRUMENT_DATA["INSTRUMENT_MIN"]:
        new_instrument = INSTRUMENT_DATA["INSTRUMENT_MIN"]
    if new_instrument > INSTRUMENT_DATA["INSTRUMENT_MAX"]:
        new_instrument = INSTRUMENT_DATA["INSTRUMENT_MAX"]

    INSTRUMENT_DATA["INSTRUMENT"] = new_instrument
    logger.debug(
        f'Set instrument: bank {INSTRUMENT_DATA["BANK"]}, instrument {INSTRUMENT_DATA["INSTRUMENT"]}')
    synth.set_instrument(
        INSTRUMENT_DATA["BANK"], INSTRUMENT_DATA["INSTRUMENT"])
    ctrl.setup_instrument_navigator(
        INSTRUMENT_DATA["INSTRUMENT"], INSTRUMENT_DATA["INSTRUMENT_MIN"], INSTRUMENT_DATA["INSTRUMENT_MAX"])


# ----------------------------------------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------------------------------------
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL,
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

device_listener_thread = threading.Thread(target=device_listener)
device_listener_thread.daemon = True
device_listener_thread.start()

signal.signal(signal.SIGINT, end_process_handler)
signal.signal(signal.SIGTERM, end_process_handler)

while DEVICE_PORT_NAME not in mido.get_input_names():
    time.sleep(2)

with mido.open_output(DEVICE_PORT_NAME, autoreset=True) as output_port:
    with mido.open_input(DEVICE_PORT_NAME, autoreset=True) as input_port:
        logger.debug(f'OUTPUT PORT: {output_port}')
        logger.debug(f'INPUT PORT: {input_port}')

        synth.load_sf2(SF2)
        ctrl = MidiController(output_port)
        synth.volume()

        logger.debug('Waiting for midi messages..')

        for message in input_port:
            logger.debug(f'Received {message}')
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
                    btn_col, btn_row = ctrl.get_button_coordinates(
                        message.note)
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
                    btn_col, btn_row = ctrl.get_button_coordinates(
                        message.note)
                    current_drum_kit = get_drum_current_kit()
                    # KITS
                    if message.note in get_drum_keys():  # TODO: move to ctrl??
                        update_drums(message.note)
                    # NOTES
                    if DRUMS_DATA["MAPPING"][current_drum_kit][btn_row][btn_col] != 0:
                        send_note_str(
                            message, DRUMS_DATA["MAPPING"][current_drum_kit][btn_row][btn_col])
