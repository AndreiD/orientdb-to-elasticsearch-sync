# -*- coding: utf-8 -*-
import logging
import logging.handlers

import requests
import os
import sys
import colorstreamhandler
from math import log

LOG_FILENAME = '../errors_log.out'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000, backupCount=0)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter("%(asctime)s ### %(message)s", "%Y-%m-%d %H:%M:%S"))
my_logger.addHandler(file_handler)

stderr_log_handler = colorstreamhandler.ColorStreamHandler()
stderr_log_handler.setLevel(logging.NOTSET)
stderr_log_handler.setFormatter(logging.Formatter("%(message)s", "%Y-%m-%d %H:%M:%S"))
my_logger.addHandler(stderr_log_handler)


def cool_log(message, category="debug"):
    if category == "debug":
        my_logger.debug(message)
    if category == "info":
        my_logger.info(message)
    if category == "warning":
        my_logger.warning(message)
    if category == "error":
        my_logger.error(message)


unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'



def delete_in_es(url):
    try:
        m_req = requests.delete(url, timeout=5)
        if m_req.status_code == 200:
            return True
        else:
            cool_log("got different than 200 return code on deletion > "+str(m_req.status_code),category="error")
            return False
    except requests.exceptions.RequestException as e:
        cool_log(e, category="error")
        return False


def post_to_es(url, data):
    try:
        m_req = requests.post(url, data=data, timeout=5)
        if m_req.status_code == 201 or m_req.status_code == 200:
            return True
        else:
            cool_log("got different than 200,201 return code on insertion > "+str(m_req.status_code),category="error")
            return False
    except requests.exceptions.RequestException as e:
        cool_log(e, category="error")
        return False

def get_web_content(url):
    try:
        output = requests.get(url, timeout=5).content
        return output
    except requests.exceptions.RequestException as e:
        cool_log(e, category="error")


def get_web_content_auth(url, user, password):
    try:
        output = requests.get(url, auth=(user, password), timeout=5).content
        return output
    except requests.exceptions.RequestException as e:
        cool_log(e, category="error")


def clear_screen():
    if sys.platform == 'amiga':
        print '\f',
    if sys.platform == 'win32':
        print os.system("CLS"), chr(13), " ", chr(13),
    if sys.platform == 'linux2':
        print os.system("clear"), chr(13), " ", chr(13),

