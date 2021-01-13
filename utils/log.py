import logging


def set_log_level(log_level):
    logging.basicConfig(level=log_level,
                        format='[%(asctime)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M')


def buid_string(arguments):
    log_str = ""
    for x in arguments:
        log_str += "{} ".format(x)
    return log_str


def debug(*args):
    log_str = buid_string(locals()['args'])
    logging.debug(log_str)
