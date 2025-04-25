import random
import string
import math
import sys

# Custom mutator parameters. Tweak these for your use case.

MAXIMUM_LENGTH = 100_000 # Absolute maximum length of the generated data.
NEW_DATA_CHANCE = 0.01 # Possibility of creating an entirely new string
MAX_REPEAT_COUNT = 100_00 # Maximum amount of repetitions
MAX_REPEAT_LENGTH = 10000 # Maximum length of the repeating stuff
MAX_REPEAT_COUNT_LINEAR = 10000
MIN_REPEAT_COUNT_LINEAR = 200
MAX_REPEAT_TOKEN_LENGTH = 5 # Maximum length of the string which to repeat.
MAX_REPEAT_STRING_COUNT = 10 # Maximum amount of repeating substrings
MAX_SUBSTRING_LENGTH = 10

def f(x: float) -> float: # Function (this is assumed to be growing in the period 0 <= x <= 1)
    return (x + 0.6) ** 3 + max(MIN_REPEAT_COUNT_LINEAR, round(MAX_REPEAT_COUNT_LINEAR * x))

PRECALC = f(1.0) # Precalculated value for faster execution

def dist_function(x: float) -> float: # Distribution. x is assumed to be between 0 <= x <= 1
    assert 0 <= x <= 1
    return f(x) / PRECALC # Random value divided by maximum value. (Maximum is assumed to be at x = 1)

def distribution(val: int) -> int: # Returns a random number (max is c and minimum is zero). This function is biased against small numbers (the probability of generating a relatively small number is high, whileas the probability of generating a comparatively large number is small.)
    return round(val * dist_function(chance()))

def custom_mutator(data, max_size, seed, native_mutator):
    # Just call mutate and see what happens...
    if isinstance(data, bytearray):
        convert = True
        data = bytes(data)
    new_data = mutate(data)
    if convert:
        new_data = bytearray(new_data)
    if len(new_data) >= max_size:
        return new_data[:max_size] # Just add a cutoff
    return new_data

def chance() -> float: # Shorthand
    return random.random()

def c(const: float) -> bool: # Rolls a dice and returns true with a probability of "const"
    return chance() <= const

def rnum(n: int) -> int: # Shorthand
    if n in (0, -1):
        return 0
    return random.randrange(0, n)

def stringmult(string_bytes: bytes, val: int) -> bytes: # Multiplies string by val times.
    if len(string_bytes) == 0: # Avoid division by zero
        return string_bytes
    count = min(math.floor(MAX_REPEAT_LENGTH/len(string_bytes)), val)
    assert isinstance(count, int)
    out = string_bytes * count
    assert len(out) <= MAX_REPEAT_LENGTH
    return out

def rand_ascii_string(n: int) -> bytes: # Generates n random ascii bytes (taken from string.printable)
    return bytes([ord(random.choice(string.printable)) for _ in range(n)]) # Create array of allowed bytes and convert to bytes

def generate_repeating(n: int) -> bytes: # Generate a random repeating string and repeat it n times
    #return stringmult(rand_ascii_string(rnum(MAX_REPEAT_TOKEN_LENGTH)), n)
    return stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), n)

def generate_new() -> bytes: # Generate a new ascii string.
    repeat_count = rnum(MAX_REPEAT_STRING_COUNT)
    out = b"" # Final generated string
    for _ in range(repeat_count): # Generate "repeat_count" repeating strings.
        out += generate_repeating(rnum(MAX_REPEAT_COUNT))
    return out

def get_substr(data: bytes) -> bytes:
    rand_ind = min(rnum(len(data)), MAX_SUBSTRING_LENGTH)
    length = rnum(len(data[rand_ind:])-1)
    result = data[rand_ind:rand_ind+length]
    return result, rand_ind # Return the substring

def mutate_existing(data: bytes) -> bytes:
    substr, rand_ind = get_substr(data)
    if substr:
        # Just cut out the original string and then add the multiplied substring in there.
        rep_count = distribution(MAX_REPEAT_COUNT)
        multiplication = stringmult(substr, rep_count)
        data = data[:rand_ind] + multiplication + data[rand_ind+len(substr):]
        return data
    # Place somewhere else.
    place_index = rnum(len(data)-1)
    rep_count = distribution(MAX_REPEAT_COUNT)
    multiplication = stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), rep_count)
    data = data[place_index:] + multiplication + data[place_index:]
    return data

def mutate(data: bytes): # Main mutator entry point. Returns a mutated version of the data.
    if c(NEW_DATA_CHANCE): # Create new string.
        return generate_new()
    # Mutate existing.
    return mutate_existing(data)

def fuzz(buf, add_buf, max_size): # For AFL and AFL++
    data = buf
    data = bytes(data) # Convert bytearray to bytes.
    data = mutate(data)
    if len(data) >= max_size:
        print("Truncating returned fuzz data...\n")
        print("Orig len is " + str(len(data)) + " . New len is " + str(max_size))
        data = data[:max_size] # Truncate
    data = bytearray(data) # Convert bytes back to bytearray.
    return data

def deinit(): # AFL and AFL++ complain if we do not have this for some reason...
    pass

if __name__=="__main__": # For testing only. This just checks that the mutator doesn't crash
    MAX_MUT_COUNT = 2000
    TEST_COUNT = 100000
    BRACE_COUNT = 100
    while True:
        MUT_COUNT = rnum(MAX_MUT_COUNT)
        RESULT = b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        for _ in range(MUT_COUNT):
            RESULT = mutate_existing(RESULT)
            if len(RESULT) > MAXIMUM_LENGTH: # Bounds check
                RESULT = RESULT[:MAXIMUM_LENGTH]
    sys.exit(0) # exit succesfully
