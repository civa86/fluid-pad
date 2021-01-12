import mido


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

    def __init__(self, port):
        self.port = port

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
        # TODO: set mode to XY to be sure is not in drum mode....

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

    def is_note_keys(self, x, y):
        return x < self.notes_keys_col and (y % 2 != 0 or not x in self.semi_notes_void_col)

    # TODO: refactor arguments...
    def init_layout(self, current_mode, octave):
        self.reset_layout()
        self.send_lp_cc(self.mode_keys[current_mode], self.colors["AMBER"])

        if current_mode == 0:
            self.setup_octaves(octave)
            for x in self.song_keys:
                self.send_lp_note(x, self.colors["GREEN_LOW"])
            for x in range(0, self.notes_keys_col):
                for y in range(0, 8):
                    if self.is_note_keys(x, y):
                        n = y * 16 + x
                        col = self.colors["AMBER"] if y % 2 == 0 else self.colors["YELLOW"]
                        self.send_lp_note(n, col)
        elif current_mode == 2:
            print('init_layout for mode 2...')
