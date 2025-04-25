import sys

import atheris
import mutator # Custom mutator


with atheris.instrument_imports():
    import fuzzers
    from django.core.exceptions import SuspiciousOperation


def TestOneInput(data):
    if len(data) == 0: # We use the first byte to choose the test, so therefore just do this.
        return
    #assert len(fuzzers.tests) <= 256 # must fit in a byte....
    choice = int(data[0])
    choice = choice % len(fuzzers.tests_str)
    data = data[1:] # Do the thing...
    #choice = 17
    func, data_type = fuzzers.tests_str[choice]
    #print("We chose this function: "+str(func))
    # This loop here causes fuzzing redundancy. Maybe remove this?
    assert data_type == str # Should be string...

    #print("We chose this function: "+str(func))

    # Here in the original version we used the fuzz data provider to generate inputs, however in this fork we just use only the functions which take strings.

    '''
    if data_type == str:
        data = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)
    elif data_type == bytes:
        data = fdp.ConsumeBytes(sys.maxsize)
    elif data_type == int:
        data = fdp.ConsumeInt(sys.maxsize)
    '''



    try:
        data = data.decode("utf-8")
        func(data)
    except (UnicodeDecodeError, SuspiciousOperation):
        # Just ignore decode errors
        return
    except Exception:
        print(func, data_type, repr(data))
        raise
    return

def CustomMutator(data, max_size, seed):
    try:
        res = mutator.mutate(data) # Call custom mutator.
    except:
        res = atheris.Mutate(data, len(data))
    else:
        res = atheris.Mutate(res, len(res))
    if len(res) >= max_size: # Truncate inputs which are too long...
        return res[:max_size]
    return res

atheris.Setup(sys.argv, TestOneInput, custom_mutator=CustomMutator, internal_libfuzzer=True)
atheris.Fuzz()

