import mido


class MidiController:
    colors = {
        "GREEN": 60,
        "GREEN_LOW": 28,
        "YELLOW": 62,
        "AMBER": 63,
        "RED": 15,
        "RED_LOW": 13,
    }
    note_min = 112
    note_max = 118

    next_instrument_key = 107
    next_10_instruments_key = 105
    prev_instrument_key = 106
    prev_10_instruments_key = 104

    note_keys = [80, 81, 82, 83, 84, 85, 86, 112, 113, 114, 115, 116, 117, 118]
    semi_note_keys = [65, 66, 68, 69, 70, 97, 98, 100, 102, 102]
    octave_keys = [48, 49, 50, 51, 52, 53, 54]

    modes = [109, 110]

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

    # TODO: refactor arguments...
    def init_layout(self, current_mode, octave):
        self.reset_layout()
        self.send_lp_cc(self.modes[current_mode], self.colors["AMBER"])
        # LEDs for mode 0
        if current_mode == 0:
            self.send_lp_cc(self.modes[current_mode], self.colors["AMBER"])
            self.setup_octaves(octave)
            for x in self.note_keys:
                self.send_lp_note(x, self.colors["YELLOW"])
            for x in self.semi_note_keys:
                self.send_lp_note(x, self.colors["AMBER"])
