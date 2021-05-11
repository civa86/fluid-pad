import sys
import os
import signal
import time
import threading

import mido

from utils.log import set_log_level, debug
import utils.synth as synth
from utils.midi import MidiController

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
    "KITS": [2, 4, 5],
    "KIT": 0
}
# SONGS = [
#     {
#         8: "resources/midi/sw.mid",
#         24: "resources/midi/stangata.mid",
#         40: "resources/midi/jammin.mid",
#         56: "resources/midi/simpson.mid",
#         72: "resources/midi/rollem.mid",
#     },
#     {
#         8: "resources/midi/loop1.mid",
#         24: "resources/midi/loop2.mid",
#         40: "resources/midi/loop3.mid"
#     }
# ]
# ----------------------------------------------------------------------------------------------------------------------
# APPLICATION STATE
# ----------------------------------------------------------------------------------------------------------------------
mode = 1
octave = 2
ctrl = None
song_playing = None
# ----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------


def device_listener():
    global song_playing
    device_initialized = False
    while 1:
        if DEVICE_PORT_NAME in mido.get_input_names():
            if device_initialized == False and not ctrl is None:
                init()
                device_initialized = True
        else:
            song_playing = None
            device_initialized = False
        time.sleep(1)


def end_process_handler(signal, frame):
    if ctrl is not None:
        ctrl.reset_layout()
    debug('gracefully exiting')
    sys.exit(0)


def send_note(message, x, y):
    n = NOTES_MATRIX[y % 2][x]
    o = int(message.note / 32) + octave
    if message.velocity == 127:
        debug('Play Note', n + '-' + str(o))
        ctrl.send_lp_note(message.note, ctrl.colors["GREEN"])
        synth.play(n, o)
    else:
        ctrl.send_lp_note(message.note, ctrl.colors["YELLOW"] if btn_row % 2 != 0 else ctrl.colors["AMBER"])
        synth.stop(n, o)


def init():
    debug('init mode', mode)
    ctrl.init_layout(mode, octave)
    if mode == 0:
        update_instrument()
    elif mode == 1:
        update_drums(DRUMS_DATA['KIT'])


def get_drum_keys():
    return range(0, len(DRUMS_DATA['KITS']))


def update_drums(kit):
    if kit != DRUMS_DATA['KIT']:
        DRUMS_DATA['KIT'] = kit
    debug("set drum", 'bank', DRUMS_DATA["BANK"], 'kit', DRUMS_DATA["KITS"][DRUMS_DATA["KIT"]])
    synth.set_instrument(DRUMS_DATA["BANK"], DRUMS_DATA["KITS"][DRUMS_DATA["KIT"]])
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


def play_midi_song(song):
    global song_playing
    last_note = None
    if song_playing is None:
        song_playing = song
        for msg in mido.MidiFile(song).play():
            if song_playing is not None:
                if msg.type == 'note_on':
                    synth.play_midi(msg.note, msg.velocity)
            else:
                synth.stop_all()
                break
        song_playing = None


def playing_key(key):
    global song_playing
    col = 0
    while 1:
        if song_playing is not None:
            if col == 0:
                ctrl.send_lp_note(key, ctrl.colors["GREEN"])
                col = 1
            else:
                ctrl.send_lp_note(key, ctrl.colors["GREEN_LOW"])
                col = 0
            time.sleep(0.5)
        else:
            ctrl.send_lp_note(key, ctrl.colors["GREEN_LOW"])
            break


def start_playing_song(song, message):
    play_midi_song_thread = threading.Thread(target=play_midi_song, args=[song])
    play_midi_song_thread.start()
    playing_key_thread = threading.Thread(target=playing_key, args=[message.note])
    playing_key_thread.start()


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
                    # TODO: manage instrument....

            if mode == 0:
                if message.type == 'control_change' and message.value == 127:
                    if song_playing is not None:
                        song_playing = None

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
                    if song_playing is None:
                        btn_col = message.note % 16
                        btn_row = int(message.note / 16)
                        # OCTAVE
                        if message.note in ctrl.octave_keys:
                            octave = btn_row
                            ctrl.setup_octaves(octave)
                        # NOTES
                        if ctrl.is_note_keys(btn_col, btn_row):
                            send_note(message, btn_col, btn_row)
                    # SONGS
                    # if message.note in ctrl.song_keys and message.velocity == 127:
                    #     song = SONGS[mode].get(message.note, None)
                    #     if song and song_playing is None:
                    #         start_playing_song(song, message)
                    #     else:
                    #         if song != song_playing:
                    #             song_playing = None
                    #             time.sleep(0.5)
                    #             start_playing_song(song, message)
                    #         else:
                    #             song_playing = None
            elif mode == 1:
                # DRUMS NAVIGATOR
                if message.type == 'note_on':
                    if song_playing is None:
                        if message.note in get_drum_keys():
                            update_drums(message.note)
