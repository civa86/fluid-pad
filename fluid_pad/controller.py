
import logging
import sys
import os
import signal
import time
import threading
import mido
import fluid_pad.synth as synth
from fluid_pad.midi import MidiController
from fluid_pad.const import DEVICE_PORT_NAME, SF2, NOTES_MATRIX, INSTRUMENT_DATA, DRUMS_DATA

logger = logging.getLogger(__name__)


class Controller:
  mode = 0
  octave = 2
  midi_controller = None
  sound_font_path = None

  def __init__(self):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    self.sound_font_path = os.path.join(current_dir, SF2)

  def device_listener(self):
    device_initialized = False
    while True:
      if DEVICE_PORT_NAME in mido.get_input_names():
        if device_initialized == False and self.midi_controller is not None:
          self.init_mode()
          device_initialized = True
      else:
        device_initialized = False
        logger.debug(f'Wait for {DEVICE_PORT_NAME}')
      time.sleep(1)

  def end_process_handler(self, signal, frame):
    if self.midi_controller is not None:
      self.midi_controller.reset_layout()
    logger.debug('gracefully exiting')
    sys.exit(0)

  def send_note_coords(self, message, x, y):
    n = NOTES_MATRIX[y % 2][x]
    o = int(message.note / 32) + self.octave
    if message.velocity == 127:
      logger.debug(f'Play Note {n}-{str(o)}')
      self.midi_controller.send_lp_note(message.note, self.midi_controller.colors["GREEN"])
      synth.play(n, o)
    else:
      self.midi_controller.send_lp_note(
          message.note, self.midi_controller.colors["YELLOW"] if y % 2 != 0 else self.midi_controller.colors["AMBER"])
      synth.stop(n, o)

  def send_note_str(self, message, note_str):
    note_info = note_str.split('-')
    if message.velocity == 127:
      logger.debug(f'Play Note {note_str}')
      self.midi_controller.send_lp_note(message.note, self.midi_controller.colors["GREEN"])
      synth.play(note_info[0], int(note_info[1]))
    else:
      logger.debug(f'Stop Note {note_str}')
      self.midi_controller.send_lp_note(message.note, self.midi_controller.colors["AMBER"])
      synth.stop(note_info[0], int(note_info[1]))

  def init_mode(self):
    logger.debug(f'init mode {self.mode}')
    if self.mode == 0:
      self.midi_controller.init_instrument_layout(self.octave)
      self.update_instrument()
    elif self.mode == 1:
      self.midi_controller.init_drums_layout(self.get_drum_current_kit())
      self.update_drums(DRUMS_DATA['KIT'])

  def get_drum_current_kit(self):
    return DRUMS_DATA["KITS"][DRUMS_DATA["KIT"]]

  def update_drums(self, kit):
    if kit != DRUMS_DATA['KIT']:
      DRUMS_DATA['KIT'] = kit
      self.midi_controller.init_drums_layout(self.get_drum_current_kit())

    drum_current_kit = self.get_drum_current_kit()
    logger.debug(
        f'Set drum: bank {DRUMS_DATA["BANK"]}, kit {drum_current_kit}')
    synth.set_instrument(DRUMS_DATA["BANK"], drum_current_kit)
    self.midi_controller.setup_drum_navigator(DRUMS_DATA["KIT"])

  def update_instrument(self, increment=0):
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
    self.midi_controller.setup_instrument_navigator(
        INSTRUMENT_DATA["INSTRUMENT"], INSTRUMENT_DATA["INSTRUMENT_MIN"], INSTRUMENT_DATA["INSTRUMENT_MAX"])

  def run(self):
    device_listener_thread = threading.Thread(target=self.device_listener)
    device_listener_thread.daemon = True
    device_listener_thread.start()

    signal.signal(signal.SIGINT, self.end_process_handler)
    signal.signal(signal.SIGTERM, self.end_process_handler)

    while DEVICE_PORT_NAME not in mido.get_input_names():
      time.sleep(2)

    with mido.open_output(DEVICE_PORT_NAME, autoreset=True) as output_port:
      with mido.open_input(DEVICE_PORT_NAME, autoreset=True) as input_port:
        logger.debug(f'OUTPUT PORT: {output_port}')
        logger.debug(f'INPUT PORT: {input_port}')

        synth.load_sf2(self.sound_font_path)
        self.midi_controller = MidiController(output_port)
        synth.volume()

        logger.debug('Waiting for midi messages..')

        for message in input_port:
          logger.debug(f'Received {message}')
          # SWITCH MODES
          if message.type == 'control_change' and message.value == 127 and message.control in self.midi_controller.mode_keys:
            new_mode = self.midi_controller.mode_keys.index(message.control)
            if new_mode != self.mode:
              self.mode = new_mode
              self.init_mode()

          # INSTRUMENT MODE
          if self.mode == 0:
            if message.type == 'control_change' and message.value == 127:
              # INSTRUMENT NAVIGATOR
              if message.control == self.midi_controller.next_instrument_key:
                self.update_instrument(1)
              if message.control == self.midi_controller.next_10_instruments_key:
                self.update_instrument(10)
              if message.control == self.midi_controller.prev_instrument_key:
                self.update_instrument(-1)
              if message.control == self.midi_controller.prev_10_instruments_key:
                self.update_instrument(-10)

            if message.type == 'note_on':
              btn_col, btn_row = self.midi_controller.get_button_coordinates(
                  message.note)
              # OCTAVE
              if message.note in self.midi_controller.octave_keys:
                self.octave = btn_row
                self.midi_controller.setup_octaves(self.octave)
              # NOTES
              if self.midi_controller.is_note_keys(btn_col, btn_row):
                self.send_note_coords(message, btn_col, btn_row)
          # DRUMS MODE
          elif self.mode == 1:
            if message.type == 'note_on':
              btn_col, btn_row = self.midi_controller.get_button_coordinates(
                  message.note)
              current_drum_kit = self.get_drum_current_kit()
              # KITS
              if message.note in self.midi_controller.drum_keys:
                self.update_drums(message.note)
              # NOTES
              if DRUMS_DATA["MAPPING"][current_drum_kit][btn_row][btn_col] != 0:
                self.send_note_str(
                    message, DRUMS_DATA["MAPPING"][current_drum_kit][btn_row][btn_col])
