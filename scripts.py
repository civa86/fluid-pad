import os
from fluid_pad.__main__ import main
from watchgod import run_process


def develop():
  os.environ["LOGLEVEL"] = "DEBUG"
  current_dir = os.path.dirname(os.path.realpath(__file__))
  run_process(os.path.join(current_dir, 'fluid_pad'), main)
