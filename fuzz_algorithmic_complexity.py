import sys
import mutator # Custom mutator
import time # For measuring execution time...

TIMEOUT_MS = 100 # Milliseconds to report a potential DOS issue...
# TIMEOUT_MS = TIMEOUT_MS / 1000 # To seconds...

if "--nofuzz" not in sys.argv:
    import atheris
    with atheris.instrument_imports():
        import fuzzers
        from django.core.exceptions import SuspiciousOperation
else: # Standalone import...
    import fuzzers
    from django.core.exceptions import SuspiciousOperation

def TestOneInput(data):
    if len(data) == 0: # We use the first byte to choose the test, so therefore we can not process empty inputs.
        return
    #assert len(fuzzers.tests) <= 256 # must fit in a byte....
    choice = int(data[0])
    choice = choice % len(fuzzers.tests_str)
    data = data[1:] # Do the thing...
    func, data_type = fuzzers.tests_str[choice]
    # assert data_type == str # Should be string...
    # Here in the original version we used the fuzz data provider to generate inputs, however in this fork we just use only the functions which take strings.
    start = time.time()
    try:
        data = data.decode("utf-8") # Try to decode as hex. All the functions should only take string input, therefore 
        func(data)
    except (UnicodeDecodeError, SuspiciousOperation, AssertionError): # AssertionError is for the html parser errors...
        # Just ignore decode errors
        end = time.time()
        if end - start >= TIMEOUT_MS:
            raise TimeoutError
        return
    except Exception:
        print(func, data_type, repr(data))
        raise
    end = time.time()
    print(end - start)
    if end - start >= TIMEOUT_MS:
        raise TimeoutError
    return

if "--nofuzz" not in sys.argv:

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

    atheris.Setup(sys.argv, TestOneInput, custom_mutator=CustomMutator, internal_libfuzzer=True) # Use the custom mutator
    atheris.Fuzz()
else:
    # Just run the thing with the sys stdin input...
    TestOneInput(bytes(sys.stdin.read(), encoding="ascii"))