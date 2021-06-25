import logging
import os
from fluid_pad.controller import Controller

logger = logging.getLogger(__name__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL,
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M')


def main():
  ctrl = Controller()
  ctrl.run()


if __name__ == '__main__':
  main()
