#!/bin/python3
"""Loads everything onto the ESP32"""

import argparse
import os
import time
import functools
import logging

from ampy import pyboard

logging.basicConfig(level=logging.INFO)

PORT = "/dev/ttyUSB0"
BAUD = 115200

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'onboard')
EXCLUDES = ['.pyc', '.txt', '.gitignore', '__pycache__']
IGNORED_FILES = [f.strip() for f in open('onboard/file_blacklist').readlines()]

files = []
for base_path, subdirs, subfiles in os.walk(BASE_PATH):
    for filename in subfiles:
        full_path = os.path.join(base_path, filename)
        to_path = os.path.relpath(full_path, BASE_PATH)

        found = False
        for exclude in EXCLUDES:
            if exclude in to_path:
                found = True
        if found:
            continue

        if to_path in IGNORED_FILES:
            continue
        files.append(full_path)


print(files)

def run_text(text):
    pyb = pyboard.Pyboard(PORT, BAUD, 'micro', 'python')
    pyb.enter_raw_repl()
    logging.debug("Running: {}".format(repr(text)))
    output = pyb.exec_(text)
    logging.debug("Got: {}".format(repr(output)))
    #pyboard.stdout_write_bytes(output)
    pyb.exit_raw_repl()
    pyb.close()

    return output

def load_file(input_file, onboard_path):
    ensure_dir(os.path.dirname(onboard_path))
    logging.info("Loading file {} to {}".format(input_file, onboard_path))

    file_contents = open(input_file, 'rb').read()
    file_name = os.path.basename(onboard_path)
    file_str = '''f = open("{}", "wb");
f.write({});
f.close()'''.format(onboard_path, repr(file_contents))

    run_text(file_str)


@functools.lru_cache()
def ensure_dir(directory):
    if not directory:
        return

    parent_dirs = directory.split('/')[:-1]
    for par_dir in parent_dirs:
        ensure_dir(par_dir)

    cmd = "import os; print('{}' in os.listdir('{}'))".format(os.path.basename(directory), os.path.dirname(directory))
    res = run_text(cmd)
    if b'False' in res:
        logging.info("Making Directory {}".format(directory))
        cmd = "import os; os.mkdir('{}')".format(directory)
        res = run_text(cmd)
    elif b'True' in res:
        return False
    else:
        print("ENSURE_DIR FAILED")
    print(res)


for file_id, file_name in enumerate(files):
    print("{:.0f}%".format(file_id/len(files) * 100))
    to_path = os.path.relpath(file_name, BASE_PATH)
    load_file(file_name, to_path)
