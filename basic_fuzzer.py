import struct
import sys

import atheris

with atheris.instrument_imports():
    import fuzzers

def TestOneInput(data):
    if len(data) < 2:
        choice = 0 # Needed so we produce coverage events for short input
    else:
        choice = struct.unpack('>H', data[:2])[0] % len(fuzzers.tests)
    if choice >= len(fuzzers.tests):
        return

    data = data[2:]
    if fuzzers.tests[choice][1] == str:
        data = data.decode("utf8", "replace")

    fuzzers.tests[choice][0](data)

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()