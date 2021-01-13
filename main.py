import sys
import signal
import time
import mido
import threading

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
MODES_WITH_SOUND = [0, 1]
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
SONGS = {
    8: "resources/midi/sw.mid",
    24: "resources/midi/stangata.mid",
    40: "resources/midi/x_files.mid",
    56: "resources/midi/rollem.mid",
    72: "resources/midi/exodus.mid",
}
# ----------------------------------------------------------------------------------------------------------------------
# APPLICATION STATE
# ----------------------------------------------------------------------------------------------------------------------
mode = 0
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
    ctrl.reset_layout()
    sys.exit(0)


def send_note(message, x, y):
    n = NOTES_MATRIX[y % 2][x]
    o = int(message.note / 32) + octave
    if message.velocity == 127:
        print('Play Note', n + '-' + str(o))
        ctrl.send_lp_note(message.note, ctrl.colors["GREEN"])
        synth.play(n, o)
    else:
        ctrl.send_lp_note(message.note, ctrl.colors["YELLOW"] if btn_row % 2 != 0 else ctrl.colors["AMBER"])
        synth.stop(n, o)


def init():
    print('init mode', mode)
    ctrl.init_layout(mode, octave)
    if mode in MODES_WITH_SOUND:
        update_instrument()


def update_instrument(increment=0):
    new_instrument = SYNTH_DATA[mode]["INSTRUMENT"] + increment
    if new_instrument < SYNTH_DATA[mode]["INSTRUMENT_MIN"]:
        new_instrument = SYNTH_DATA[mode]["INSTRUMENT_MIN"]
    if new_instrument > SYNTH_DATA[mode]["INSTRUMENT_MAX"]:
        new_instrument = SYNTH_DATA[mode]["INSTRUMENT_MAX"]

    SYNTH_DATA[mode]["INSTRUMENT"] = new_instrument
    print("set instrument", 'bank', SYNTH_DATA[mode]["BANK"], 'instrument', SYNTH_DATA[mode]["INSTRUMENT"])
    synth.set_instrument(SYNTH_DATA[mode]["BANK"], SYNTH_DATA[mode]["INSTRUMENT"])
    ctrl.setup_instrument_navigator(SYNTH_DATA[mode]["INSTRUMENT"], SYNTH_DATA[mode]["INSTRUMENT_MIN"], SYNTH_DATA[mode]["INSTRUMENT_MAX"])


def play_midi_song(song):
    global song_playing
    last_note = None
    if song_playing is None:
        song_playing = song
        for msg in mido.MidiFile(song).play():
            if song_playing is not None:
                if msg.type == 'note_on':

                    # if last_note is not None:
                    # ctrl.send_lp_note(last_note, ctrl.colors["YELLOW"])
                    # ctrl.send_lp_note(msg.note, ctrl.colors["GREEN"])
                    # last_note = msg.note

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
    playT = threading.Thread(target=play_midi_song, args=[song])
    playT.start()
    playTKey = threading.Thread(target=playing_key, args=[message.note])
    playTKey.start()


# ----------------------------------------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------------------------------------
thread = threading.Thread(target=device_listener)
thread.daemon = True
thread.start()

while not DEVICE_PORT_NAME in mido.get_input_names():
    print('Wait for', DEVICE_PORT_NAME)
    time.sleep(2)

signal.signal(signal.SIGINT, end_process_handler)
signal.signal(signal.SIGTERM, end_process_handler)

with mido.open_output(DEVICE_PORT_NAME, autoreset=True) as output_port:
    with mido.open_input(DEVICE_PORT_NAME, autoreset=True) as input_port:
        print('OUTPUT PORT: {}'.format(output_port))
        print('INPUT PORT: {}'.format(input_port))

        synth.load_sf2(SF2)
        ctrl = MidiController(output_port)

        print('Waiting for midi messages..')

        for message in input_port:
            print('Received {}'.format(message))
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
                    if message.note in ctrl.song_keys and message.velocity == 127:
                        song = SONGS.get(message.note, None)
                        if song and song_playing is None:
                            start_playing_song(song, message)
                        else:
                            if song != song_playing:
                                song_playing = None
                                time.sleep(0.5)
                                start_playing_song(song, message)
                            else:
                                song_playing = None
