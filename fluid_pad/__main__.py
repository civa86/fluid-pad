import logging
import os
from fluid_pad.controllers.main import MainController

logger = logging.getLogger(__name__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL,
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M')


def main():
  current_dir = os.path.dirname(os.path.realpath(__file__))

  sound_font_path = os.path.join(current_dir, 'resources/sf2/VintageDreamsWaves-v2.sf2')
  device_port_name = 'Launchpad'

  ctrl = MainController(sound_font_path, device_port_name)
  ctrl.run()


if __name__ == '__main__':
  main()
