import threading
import mido
import time

# TODO: background check for lp connected....

DEVICE_PORT_NAME = 'Launchpad'


def check_device():
    while 1:
        if DEVICE_PORT_NAME in mido.get_input_names():
            print('DEVICE OK', mido.get_input_names())
        else:
            print('Wait for', DEVICE_PORT_NAME)
        time.sleep(2)


thread = threading.Thread(target=check_device)
thread.daemon = True
thread.start()

with mido.open_output(DEVICE_PORT_NAME, autoreset=True) as output_port:
    with mido.open_input(DEVICE_PORT_NAME, autoreset=True) as input_port:
        for message in input_port:
            print('Received {}'.format(message))
