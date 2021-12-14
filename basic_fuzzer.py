import sys

import atheris

with atheris.instrument_imports():
    import fuzzers


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    choice = fdp.ConsumeIntInRange(0, len(fuzzers.tests) - 1)
    func, data_type = fuzzers.tests[choice]

    if data_type == str:
        data = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)
    elif data_type == bytes:
        data = fdp.ConsumeBytes(sys.maxsize)
    elif data_type == int:
        data = fdp.ConsumeInt(sys.maxsize)

    try:
        func(data)
    except Exception:
        print(func, data_type, repr(data))
        raise


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
