import os
from fluid_pad.__main__ import main


if __name__ == '__main__':
  os.environ["LOGLEVEL"] = "DEBUG"
  main()
